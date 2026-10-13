#!/usr/bin/env python3
"""Marin'Or Ivoire · round PET bottle (red palm oil) -> Wavefront OBJ + MTL + 360° label texture.

Units: centimetres, Y up, base centre at the origin, label front facing +Z.
Everything is measured on the client's two mockups (front / back views of the same bottle render):
  - profile (radius per height) from the alpha silhouette of the front view, scaled so that the
    widest point (bottom of the shoulder) is 6.6 cm;
  - the mockups are perspective views: the label's bottom edge sags more than its top edge. The camera
    (distance, eye height) is solved from those two curves and used both to unwrap the label and to
    render the face / back previews, so that the previews reproduce the mockups;
  - label texture: the two views unwrapped onto the body (column x -> angle, perspective-correct
    asin), each column rectified between the measured top and bottom edges of the label, the two
    halves joined with a short blend at the sides (+/-90 deg), where both views are foreshortened.

Objects
  Bouteille  clear PET shell 0.3 mm: base with push-up, rounded heel, body, long shoulder, neck,
             support ring, finish (hidden under the cap)
  Huile      red palm oil volume up to the neck, with a meniscus
  Bouchon    screw cap: 96 vertical knurls, smooth band, groove of the tamper-evident band,
             rounded top edge; inner faces (Bouchon_interieur)
  Etiquette  printed film 0.12 mm wrapped 360° on the body (texture outside, plain verso inside)

Run:  python3 tools/build_bottle.py <produit>     (produits: tools/products.json)
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = json.load(open(os.path.join(ROOT, "tools", "products.json"), encoding="utf-8"))

SEG = 192                    # radial segments (shell, oil, label, smooth parts of the cap)
KNURLS, KSUB = 96, 8         # cap knurls, segments per knurl (768 around the knurled band)
KDEPTH = 2.6                 # knurl groove depth (px of the mockup)
T_PET, GAP_OIL = 0.03, 0.01  # PET wall, gap between wall and oil (cm)
T_LAB, GAP_LAB = 0.012, 0.004
TEX_W = 3072                 # label texture width (360°)
SEAM_BLEND = 6.0             # degrees of blending on each side of the +/-90° seams
PHI_LIM = 80.0               # beyond this angle a view is too foreshortened: its 80° column is held
INSET = 2.0                  # px kept off the measured label edges when unwrapping (label shortened alike)

# rows / radii measured on the 615 x 1738 mockups (px)
WIN_TOP, WIN_BOT = (850, 898), (1598, 1688)   # search windows: label top / bottom edges
LAB_ROWS = (960, 1590)                       # straight part of the label (centre, radius)
NECK_TOP = 209                               # top of the straight neck (below: support ring)
HEEL_JOIN = 1690                             # lowest silhouette row used (below: base in perspective)
RC_PX = 248.0                                # base contact ring (bottom ellipse of the silhouette)
R_RING, R_FIN = 185.5, 168.6                 # support ring, threaded finish
CAP_BOT, GROOVE, KNURL = 178.0, 133.5, (30.5, 118.5)
SKIRT_IN, UNDER_TOP = 173.0, 22.6


def hex_lin(h):
    """sRGB hex -> linear RGB (OBJ importers such as Blender's copy Kd straight into linear base colour)."""
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return " ".join("%.4f" % (x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


# --------------------------------------------------------------------------- profile helpers (as build_jar.py)
def catmull(points, per_seg=8):
    P = np.asarray(points, float)
    if len(P) < 3:
        return P
    ext = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(per_seg):
            t = k / per_seg
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-1])
    return np.asarray(out)


def arc_px(cx, cy, rad, a0, a1, n):
    """Arc in mockup pixels (y down); angles in degrees, counter-clockwise with Y up."""
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([cx + rad * np.cos(a), cy - rad * np.sin(a)], 1)


def line(p0, p1, step=1.0):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    n = max(int(math.ceil(np.hypot(*(p1 - p0)) / step)), 1)
    return p0 + (p1 - p0) * np.linspace(0, 1, n + 1)[:, None]


def dedupe(P, eps=1e-7):
    keep = [P[0]]
    for p in P[1:]:
        if np.hypot(*(p - keep[-1])) > eps:
            keep.append(p)
    return np.asarray(keep)


def profile_normals(P, outward_sign=1.0):
    T = np.zeros_like(P)
    T[1:-1] = P[2:] - P[:-2]
    T[0] = P[1] - P[0]
    T[-1] = P[-1] - P[-2]
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    return np.stack([T[:, 1], -T[:, 0]], 1) * outward_sign


def simplify_idx(P, eps, max_len):
    """Douglas-Peucker on a dense polyline -> indices kept (segments also split when longer than max_len)."""
    keep, stack = {0, len(P) - 1}, [(0, len(P) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, ab = P[i], P[j] - P[i]
        L = np.hypot(*ab)
        q = P[i + 1:j] - a
        d = np.abs(q[:, 0] * ab[1] - q[:, 1] * ab[0]) / L if L > 1e-12 else np.hypot(q[:, 0], q[:, 1])
        k = int(np.argmax(d))
        if d[k] > eps or L > max_len:
            m = i + 1 + k if d[k] > eps else (i + j) // 2
            keep.add(m)
            stack += [(i, m), (m, j)]
    return np.asarray(sorted(keep))


def smoothstep(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# --------------------------------------------------------------------------- mesh container (as build_jar.py)
class Mesh:
    def __init__(self, name):
        self.name = name
        self.v, self.vt, self.vn, self.groups = [], [], [], []

    def add_group(self, mat):
        self.groups.append((mat, []))
        return self.groups[-1][1]

    def addv(self, p, uv, n):
        self.v.append(tuple(p))
        self.vt.append(tuple(uv))
        n = np.asarray(n, float)
        self.vn.append(n / (np.linalg.norm(n) + 1e-12))
        return len(self.v) - 1


def revolve(mesh, faces, P, N, u_range=(0.0, 1.0), v_vals=None, seg=SEG, phi0=-math.pi, phi1=math.pi):
    """Revolve profile P (r, y) with 2D normals N around Y (seam duplicated for clean UVs)."""
    if v_vals is None:
        L = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
        v_vals = L / (L[-1] if L[-1] > 0 else 1)
    idx = np.zeros((seg + 1, len(P)), int)
    for i in range(seg + 1):
        t = i / seg
        phi = phi0 + (phi1 - phi0) * t
        s, c = math.sin(phi), math.cos(phi)
        u = u_range[0] + (u_range[1] - u_range[0]) * t
        for j, ((r, y), (nr, ny)) in enumerate(zip(P, N)):
            idx[i, j] = mesh.addv((r * s, y, r * c), (u, v_vals[j]), (nr * s, ny, nr * c))
    for i in range(seg):
        for j in range(len(P) - 1):
            a, b, c2, d = idx[i, j], idx[i + 1, j], idx[i + 1, j + 1], idx[i, j + 1]
            if P[j][0] < 1e-9 and P[j + 1][0] < 1e-9:
                continue
            if P[j][0] < 1e-9:
                faces.append((a, d, c2))
            elif P[j + 1][0] < 1e-9:
                faces.append((a, c2, b))
            else:
                faces += [(a, d, c2), (a, c2, b)]
    return idx


def stitch(faces, ring_a, ring_b):
    """Conforming strip between a ring of SEG and a ring of k*SEG vertices (no T-junction)."""
    k = (len(ring_b) - 1) // (len(ring_a) - 1)
    h = k // 2
    for i in range(len(ring_a) - 1):
        a0, a1, b = ring_a[i], ring_a[i + 1], ring_b[k * i:k * i + k + 1]
        for m in range(h):
            faces.append((a0, b[m], b[m + 1]))
        faces.append((a0, b[h], a1))
        for m in range(h, k):
            faces.append((a1, b[m], b[m + 1]))


# --------------------------------------------------------------------------- measurements on the mockups
def load(path):
    return np.asarray(Image.open(os.path.join(ROOT, path)).convert("RGBA")).astype(np.float64)


def silhouette(img):
    """Half-width and centre (px) of every row, from the alpha (sub-pixel)."""
    a = img[..., 3] / 255.0
    w = a.sum(1)
    c = (a * np.arange(a.shape[1])).sum(1) / np.maximum(w, 1e-9)
    return w / 2.0, c


def fill_outside(img):
    """Opaque copy of a mockup, colours pushed past the outline (no fringe at the limbs)."""
    solid = img[..., 3] > 250
    idx = ndimage.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    return img[idx[0], idx[1], :3]


def fit_edge(img, cx, R, win, signed):
    """Label edge row per column (max colour gradient), fitted robustly with y = a + b sin(phi) + c cos(phi)."""
    rgb = img[..., :3]
    xs = np.arange(int(math.ceil(cx - 0.93 * R)), int(cx + 0.93 * R) + 1)
    y0, y1 = win
    col = rgb[y0 - 4:y1 + 4][:, xs]
    c = col[2:-2]
    d = c[4:] - c[:-4]  # centred on rows y0 .. y1-1
    g = d.sum(2) if signed else np.abs(d).sum(2)
    up, dn = col[1:-7], col[7:-1]  # 3 rows above / below each candidate
    bottle = lambda q: (q[..., 0] > 120) & (q[..., 0] > 2.0 * q[..., 1])
    if signed:  # bottom edge: dark label above, bottle red below
        ok = (up[..., 0] < 190) & (up[..., 0] > 1.6 * up[..., 1]) & bottle(dn)
    else:  # top edge: bottle red above, label below
        ok = bottle(up) & (np.abs(dn - up).sum(-1) > 60)
    g = np.where(ok, g, -1e9)
    phi = np.arcsin(np.clip((xs - cx) / R, -1, 1))
    A = np.stack([np.ones_like(phi), np.sin(phi), np.cos(phi)], 1)
    n = np.arange(len(xs))
    keep = np.abs(phi) < math.radians(40)
    for it in range(8):
        gg = g
        if it:  # search close to the current fit
            dist = np.abs(np.arange(y0, y1)[:, None] - (A @ coef)[None, :])
            gg = np.where(dist < 6, g, -1e9)
        k = np.clip(np.argmax(gg, 0), 1, g.shape[0] - 2)
        valid = gg[k, n] > 20
        gm, g0, gp = g[k - 1, n], g[k, n], g[k + 1, n]
        den = gm - 2 * g0 + gp
        sub = np.where((np.abs(den) > 1e-9) & (gm > -1e8) & (gp > -1e8), 0.5 * (gm - gp) / np.where(np.abs(den) > 1e-9, den, 1), 0.0)
        ye = y0 + k + np.clip(sub, -1, 1)
        keep = keep & valid if it == 0 else valid & (np.abs(ye - A @ coef) < max(1.5, 2.5 * res[keep].std()))
        coef = np.linalg.lstsq(A[keep], ye[keep], rcond=None)[0]
        res = ye - A @ coef
    return coef, float(keep.mean()), float(np.abs(res[keep]).max())


def radius_rows(hw, lt):
    """Smoothed profile radius per row; the flare of the printed label's top edge is removed."""
    r = hw.copy()
    i0, i1 = int(lt) - 3, int(lt) + 30
    xs = np.r_[i0 - 30:i0, i1:i1 + 45]
    r[i0:i1] = np.polyval(np.polyfit(xs, r[xs], 3), np.arange(i0, i1))
    out = r.copy()
    out[NECK_TOP - 1:HEEL_JOIN + 8] = ndimage.gaussian_filter1d(r[NECK_TOP - 1:HEEL_JOIN + 8], 3.0, mode="nearest")
    c0, c1 = int(KNURL[0]) - 2, int(CAP_BOT) + 2
    out[c0:c1] = ndimage.gaussian_filter1d(r[c0:c1], 1.5, mode="nearest")
    return out


def measure(P):
    F, B = load(P["front"]), load(P["back"])
    views = {}
    for nm, img in (("front", F), ("back", B)):
        hw, c = silhouette(img)
        cx, R = float(np.median(c[LAB_ROWS[0]:LAB_ROWS[1]])), float(np.median(hw[LAB_ROWS[0]:LAB_ROWS[1]]))
        top = fit_edge(img, cx, R, WIN_TOP, False)
        bot = fit_edge(img, cx, R, WIN_BOT, True)
        views[nm] = dict(img=img, hw=hw, cx=cx, R=R, top=top[0], bot=bot[0], q=(top[1:], bot[1:]))
    at = np.mean([v["top"] for v in views.values()], 0)
    ab = np.mean([v["bot"] for v in views.values()], 0)
    R = np.mean([v["R"] for v in views.values()])
    d = R * (ab[0] - at[0]) / (ab[2] - at[2])  # camera distance (px)
    y_eye = at[0] - at[2] * d / R               # eye height (mockup row)
    hw = views["front"]["hw"]
    rows = np.where(hw > 10)[0]
    # oil level (centre columns), corrected for the view from below
    rgb = F[..., :3]
    cxf = int(round(views["front"]["cx"]))
    lv = []
    for x in range(cxf - 60, cxf + 61):
        col = rgb[225:320, x]
        oil = (col[:, 0] > 150) & (col[:, 0] > 2.5 * col[:, 1])
        lv.append(225 + np.argmax(oil[:-2] & oil[1:-1] & oil[2:]) - 0.5)
    return dict(views=views, lt=float(at[0]), lb=float(ab[0]), d=float(d), y_eye=float(y_eye),
                top_px=float(rows[0]), bottom_px=float(rows[-1] + 0.5), fill_c=float(np.median(lv)))


# --------------------------------------------------------------------------- label texture
def label_texture(M, rr, Ht):
    th = -90.0 + 360.0 * (np.arange(TEX_W) + 0.5) / TEX_W  # texture column -> angle (deg), u=0 at -90°
    v = (np.arange(Ht) + 0.5) / Ht                           # texture row -> 0 (top) .. 1 (bottom)
    Yp = M["lt"] + INSET + v * (M["lb"] - M["lt"] - 2 * INSET)  # physical row of the texture row
    out, wsum = np.zeros((Ht, TEX_W, 3)), np.zeros((1, TEX_W, 1))
    for nm, off in (("front", 0.0), ("back", 180.0)):
        V = M["views"][nm]
        phi = (th - off + 180.0) % 360.0 - 180.0
        w = smoothstep(90.0 + SEAM_BLEND, 90.0 - SEAM_BLEND, np.abs(phi))
        cols = np.where(w > 0)[0]
        R = np.interp(Yp, np.arange(len(rr)), rr) * (V["R"] / M["views"]["front"]["R"])
        lim = np.minimum(np.arcsin((R - 1.6) / R), math.radians(PHI_LIM))
        PH = np.clip(np.radians(phi[cols])[None, :], -lim[:, None], lim[:, None])
        m = M["d"] / (M["d"] - R[:, None] * np.cos(PH))
        X = V["cx"] + R[:, None] * np.sin(PH) * m
        a, b = V["top"], V["bot"]
        yt = a[0] + a[1] * np.sin(PH) + a[2] * np.cos(PH) + INSET
        yb = b[0] + b[1] * np.sin(PH) + b[2] * np.cos(PH) - INSET
        Y = yt + v[:, None] * (yb - yt)
        src = fill_outside(V["img"])
        for ch in range(3):
            out[:, cols, ch] += w[cols][None, :] * ndimage.map_coordinates(src[..., ch], [Y, X], order=3, mode="nearest")
        wsum[0, cols, 0] += w[cols]
    return np.clip(out / wsum, 0, 255).astype(np.uint8)


# --------------------------------------------------------------------------- build
def build(product):
    P = PRODUCTS[product]
    NAME = P["name"]
    BUILD = os.path.join(ROOT, "build", product)
    os.makedirs(BUILD, exist_ok=True)
    M = measure(P)
    hw = M["views"]["front"]["hw"]
    rr = radius_rows(hw, M["lt"])
    rint = lambda y: float(np.interp(y, np.arange(len(rr)), rr))
    r_max = float(rr[600:int(M["lt"]) + 2].max())
    S = P.get("diameter_cm", 6.6) / (2 * r_max)  # cm per px
    d, ye = M["d"], M["y_eye"]
    # base: the bottom of the silhouette is the near side of the contact ring, seen from above
    YB = (M["bottom_px"] + RC_PX * ye / d) / (1 + RC_PX / d)
    # cap top: the top of the silhouette is the near side of the top edge, seen from below
    y_top = (M["top_px"] + 160.0 * ye / d) / (1 + 160.0 / d)
    # oil level: measured at the centre (near side of the surface, seen from below)
    r_in_px = rint(NECK_TOP) - T_PET / S
    y_fill = M["fill_c"] + r_in_px * (ye - M["fill_c"]) / d
    cm = lambda Q: np.c_[np.asarray(Q, float)[:, 0] * S, (YB - np.asarray(Q, float)[:, 1]) * S]

    meshes = []
    # ---------------------------------------------------------------- PET shell
    dome = catmull([(0, YB - 26), (55, YB - 25.2), (110, YB - 21.5), (160, YB - 14.5), (200, YB - 7.5),
                    (226, YB - 2.8), (RC_PX - 7, YB - 0.35), (RC_PX, YB)], 8)
    slope = (rint(HEEL_JOIN - 2) - rint(HEEL_JOIN + 2)) / 4.0
    tu = np.array([slope, -1.0]) / math.hypot(slope, 1.0)
    P0, P3 = np.array([RC_PX, YB]), np.array([rint(HEEL_JOIN), HEEL_JOIN])
    P1, P2 = P0 + np.array([0.6 * (P3[0] - P0[0]), 0.0]), P3 - 0.6 * (P0[1] - P3[1]) * tu
    t = np.linspace(0, 1, 25)[1:, None]
    heel = (1 - t) ** 3 * P0 + 3 * (1 - t) ** 2 * t * P1 + 3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3
    side = np.array([(rr[y], y) for y in range(HEEL_JOIN - 1, NECK_TOP - 1, -1)], float)
    outer_main = cm(dedupe(np.vstack([dome, heel, side])))
    rn = rr[NECK_TOP]
    top = [catmull([(rn, NECK_TOP), (rn + 0.3, 207.4), (rn + 1.8, 205.6), (rn + 4.5, 204.6), (170, 204.15),
                    (R_RING - 2, 204.0)], 6)[1:],
           arc_px(R_RING - 2, 202.0, 2.0, -90, 0, 7)[1:], line((R_RING, 202.0), (R_RING, 184.5))[1:],
           arc_px(R_RING - 2, 184.5, 2.0, 0, 90, 7)[1:], line((R_RING - 2, 182.5), (171.5, 182.5))[1:],
           catmull([(171.5, 182.5), (169.6, 182.1), (168.85, 181.0), (R_FIN, 179.6)], 5)[1:],
           line((R_FIN, 179.6), (R_FIN, 27.0), 2.0)[1:], arc_px(R_FIN - 2.4, 27.0, 2.4, 0, 90, 7)[1:],
           line((R_FIN - 2.4, 24.6), (r_in_px + 2.4, 24.6))[1:], arc_px(r_in_px + 2.4, 27.0, 2.4, 90, 180, 7)[1:],
           line((r_in_px, 27.0), (r_in_px, NECK_TOP), 2.0)[1:]]
    outer_top = cm(np.vstack(top))
    n_out = profile_normals(outer_main, 1.0)
    inner_main = outer_main - T_PET * n_out          # offset into the cavity
    inner_main[0, 0] = 0.0
    shell = dedupe(np.vstack([outer_main, outer_top, inner_main[::-1][1:]]))
    shell_n = profile_normals(shell, 1.0)
    k = simplify_idx(shell, 0.002, 0.5)
    pet = Mesh("Bouteille")
    revolve(pet, pet.add_group("PET"), shell[k], shell_n[k])
    meshes.append(pet)

    # ---------------------------------------------------------------- oil
    n_in = profile_normals(inner_main[::-1], 1.0)[::-1]  # inner wall traversed downwards: normals into the cavity
    wall = inner_main + GAP_OIL * n_in
    wall[0, 0] = 0.0
    Yf = (YB - y_fill) * S
    j = int(np.argmax(wall[:, 1] > Yf))
    rw = float(np.interp(Yf, wall[j - 1:j + 1, 1], wall[j - 1:j + 1, 0]))
    men = [(rw, Yf), (rw - 0.004, Yf - 0.015), (rw - 0.02, Yf - 0.035), (rw - 0.06, Yf - 0.048),
           (rw - 0.15, Yf - 0.053), (rw * 0.55, Yf - 0.055), (0.0, Yf - 0.055)]
    men = np.vstack([np.asarray(men[:1]), catmull(men[1:5], 4), line(men[4], men[6], 0.03)[1:]])
    oil = dedupe(np.vstack([wall[:j], men]))
    oil_n = profile_normals(oil, 1.0)
    k = simplify_idx(oil, 0.002, 0.5)
    hu = Mesh("Huile")
    revolve(hu, hu.add_group("Huile"), oil[k], oil_n[k])
    meshes.append(hu)

    # ---------------------------------------------------------------- cap
    rc = lambda y: rint(y)
    rtb = rc(CAP_BOT - 2)
    A = [(SKIRT_IN, CAP_BOT)] + line((SKIRT_IN, CAP_BOT), (rtb - 1.8, CAP_BOT))[1:].tolist()
    A += arc_px(rtb - 1.8, CAP_BOT - 1.8, 1.8, -90, 0, 6)[1:].tolist()
    A += [(rc(y), y) for y in np.arange(CAP_BOT - 3.0, GROOVE + 1.9, -1.0)]
    g0 = rc(GROOVE)
    A += [(rc(GROOVE + 1.4), GROOVE + 1.4), (g0 - 0.5, GROOVE + 0.9), (g0 - 1.4, GROOVE + 0.3), (g0 - 1.4, GROOVE - 0.3),
          (g0 - 0.5, GROOVE - 0.9), (rc(GROOVE - 1.4), GROOVE - 1.4)]
    A += [(rc(y), y) for y in np.r_[np.arange(GROOVE - 2.5, KNURL[1] + 1.4, -1.0), KNURL[1] + 1.0]]
    A = cm(dedupe(np.asarray(A)))
    An = profile_normals(A, 1.0)
    kA = simplify_idx(A, 0.0012, 0.3)
    er = KNURL[0] - y_top
    C = arc_px(rc(KNURL[0]) - er, KNURL[0], er, 0, 90, 14).tolist()
    C += line((rc(KNURL[0]) - er, y_top), (0.0, y_top + 0.4), 4.0)[1:].tolist()
    C = cm(np.asarray(C))
    Cn = profile_normals(C, 1.0)
    kC = simplify_idx(C, 0.0012, 0.6)
    C, Cn = C[kC], Cn[kC]
    cap = Mesh("Bouchon")
    fc = cap.add_group("Bouchon")
    ia = revolve(cap, fc, A[kA], An[kA])
    # knurled band: grid of 768 x rows, radial grooves, numerical normals
    ky = np.r_[KNURL[1], KNURL[1] - 1, KNURL[1] - 2, KNURL[1] - 3, np.linspace(KNURL[1] - 30, KNURL[0] + 30, 2),
               KNURL[0] + 3, KNURL[0] + 2, KNURL[0] + 1, KNURL[0]]
    nseg = KNURLS * KSUB
    phis = -math.pi + 2 * math.pi * np.arange(nseg + 1) / nseg
    tt = (phis * KNURLS / (2 * math.pi)) % 1.0
    groove = np.where(np.abs(tt - 0.5) < 0.16, np.cos(np.pi * (tt - 0.5) / 0.32) ** 2, 0.0)
    env = smoothstep(KNURL[1], KNURL[1] - 3, ky) * smoothstep(KNURL[0], KNURL[0] + 3, ky)
    rad = (np.array([rc(y) for y in ky])[None, :] - KDEPTH * env[None, :] * groove[:, None]) * S
    Yk = (YB - ky) * S
    G = np.stack([rad * np.sin(phis)[:, None], np.broadcast_to(Yk, rad.shape), rad * np.cos(phis)[:, None]], -1)
    dphi = np.roll(G[:-1], -1, 0) - np.roll(G[:-1], 1, 0)
    dphi = np.concatenate([dphi, dphi[:1]], 0)
    dy = np.gradient(G, axis=1)
    Nk = np.cross(dy, dphi)
    radial = np.stack([np.sin(phis)[:, None] * np.ones_like(rad), np.zeros_like(rad), np.cos(phis)[:, None] * np.ones_like(rad)], -1)
    Nk *= np.sign((Nk * radial).sum(-1, keepdims=True))
    ib = np.zeros((nseg + 1, len(ky)), int)
    for i in range(nseg + 1):
        for jj in range(len(ky)):
            ib[i, jj] = cap.addv(G[i, jj], (i / nseg, jj / (len(ky) - 1)), Nk[i, jj])
    for i in range(nseg):
        for jj in range(len(ky) - 1):
            a, b, c2, d4 = ib[i, jj], ib[i + 1, jj], ib[i + 1, jj + 1], ib[i, jj + 1]
            fc += [(a, d4, c2), (a, c2, b)]
    stitch(fc, ia[:, -1], ib[:, 0])
    icc = revolve(cap, fc, C[1:], Cn[1:])
    stitch(fc, icc[:, 0], ib[:, -1])
    ci = cm(dedupe(np.vstack([line((SKIRT_IN, CAP_BOT), (SKIRT_IN, UNDER_TOP + 1.5), 4.0),
                              arc_px(SKIRT_IN - 1.5, UNDER_TOP + 1.5, 1.5, 0, 90, 6)[1:],
                              line((SKIRT_IN - 1.5, UNDER_TOP), (0.0, UNDER_TOP), 6.0)[1:]])))
    revolve(cap, cap.add_group("Bouchon_interieur"), ci, profile_normals(ci, -1.0))
    meshes.append(cap)

    # ---------------------------------------------------------------- label (360°, seam at -90° = left side)
    lt, lb = M["lt"] + INSET, M["lb"] - INSET
    ys = np.arange(lb, lt - 0.01, -1.0)  # bottom -> top
    base = cm(np.array([(rint(y), y) for y in ys]))
    base = base[simplify_idx(base, 0.001, 1.0)]
    v_vals = (base[:, 1] - base[0, 1]) / (base[-1, 1] - base[0, 1])
    outer = base + np.array([GAP_LAB + T_LAB, 0.0])
    inner = base + np.array([GAP_LAB, 0.0])
    ph = dict(phi0=-math.pi / 2, phi1=1.5 * math.pi)
    lab = Mesh("Etiquette")
    revolve(lab, lab.add_group("Etiquette_impression"), outer, profile_normals(outer, 1.0), v_vals=v_vals, **ph)
    fv = lab.add_group("Etiquette_verso")
    revolve(lab, fv, inner, profile_normals(inner, -1.0), v_vals=v_vals, **ph)
    revolve(lab, fv, np.array([inner[-1], outer[-1]]), np.array([(0.0, 1.0), (0.0, 1.0)]), v_vals=[0.0, 1.0], **ph)
    revolve(lab, fv, np.array([outer[0], inner[0]]), np.array([(0.0, -1.0), (0.0, -1.0)]), v_vals=[0.0, 1.0], **ph)
    meshes.append(lab)
    Ht = int(round(TEX_W * (lb - lt) / (2 * math.pi * rint(0.5 * (lt + lb)))))
    tex = label_texture(M, rr, Ht)
    Image.fromarray(tex, "RGB").save(os.path.join(BUILD, P["texture"]), optimize=True)

    # ---------------------------------------------------------------- write OBJ + MTL
    obj_path = os.path.join(BUILD, NAME + ".obj")
    with open(obj_path, "w") as f:
        f.write(f"# Marin'Or Ivoire - {P['title']} - round clear PET bottle, {P['cap_name']} screw cap\n")
        f.write("# Units: centimetres. Y up. Base centre at origin. Label front faces +Z.\n")
        f.write(f"mtllib {NAME}.mtl\n")
        off = 1
        for m in meshes:
            f.write(f"o {m.name}\n")
            for p in m.v:
                f.write("v %.5f %.5f %.5f\n" % p)
            for tv in m.vt:
                f.write("vt %.6f %.6f\n" % tv)
            for nn in m.vn:
                f.write("vn %.5f %.5f %.5f\n" % tuple(nn))
            V, VN = np.asarray(m.v), np.asarray(m.vn)
            for mat, fs in m.groups:
                f.write(f"usemtl {mat}\ns 1\n")
                for i0, i1, i2 in fs:
                    gn = np.cross(V[i1] - V[i0], V[i2] - V[i0])
                    if np.dot(gn, VN[i0] + VN[i1] + VN[i2]) < 0:  # winding agrees with the shading normals
                        i1, i2 = i2, i1
                    a, b, c3 = (i + off for i in (i0, i1, i2))
                    f.write(f"f {a}/{a}/{a} {b}/{b}/{b} {c3}/{c3}/{c3}\n")
            off += len(m.v)
    with open(os.path.join(BUILD, NAME + ".mtl"), "w") as f:
        f.write(f"# Marin'Or Ivoire - {P['title']}\n# Kd values are LINEAR RGB (sRGB hex in comments)\n")
        f.write(f"""
newmtl PET
Ka 0 0 0
Kd 0.92 0.94 0.94
Ks 0.9 0.9 0.9
Ns 900
Ni 1.57
d 0.15
Tr 0.85
Tf 0.97 0.98 0.98
illum 7

newmtl Huile
# {P['oil']}
Ka 0 0 0
Kd {hex_lin(P['oil'])}
Ks 0.5 0.5 0.5
Ns 400
d 1
illum 2

newmtl Bouchon
# {P['cap']}
Ka 0 0 0
Kd {hex_lin(P['cap'])}
Ks 0.25 0.25 0.25
Ns 120
d 1
illum 2

newmtl Bouchon_interieur
# {P['cap_inner']}
Ka 0 0 0
Kd {hex_lin(P['cap_inner'])}
Ks 0.1 0.1 0.1
Ns 40
d 1
illum 2

newmtl Etiquette_impression
Ka 0 0 0
Kd 1 1 1
Ks 0.35 0.35 0.35
Ns 250
d 1
illum 2
map_Kd {P['texture']}

newmtl Etiquette_verso
Ka 0 0 0
Kd 0.85 0.85 0.84
Ks 0.1 0.1 0.1
Ns 40
d 1
illum 2
""")
    allv = np.vstack([np.asarray(m.v) for m in meshes])
    lo, hi = allv.min(0), allv.max(0)
    H = float(hi[1])
    stats = {
        "objects": {m.name: {"vertices": len(m.v), "triangles": sum(len(fs) for _, fs in m.groups)} for m in meshes},
        "size_cm": {"height": round(H, 3), "max_diameter": round(2 * r_max * S, 3), "label_diameter": round(2 * rint(1200) * S + 2 * (GAP_LAB + T_LAB), 3),
                    "cap_diameter": round(2 * rint(CAP_BOT - 2) * S, 3), "neck_diameter": round(2 * rn * S, 3),
                    "bbox_min": [round(float(x), 4) for x in lo], "bbox_max": [round(float(x), 4) for x in hi]},
        "label": {"bottom_cm": round(float(outer[0, 1]), 3), "top_cm": round(float(outer[-1, 1]), 3),
                  "height_cm": round(float(outer[-1, 1] - outer[0, 1]), 3), "texture_px": [TEX_W, Ht],
                  "edge_fit_quality": {nm: M["views"][nm]["q"] for nm in M["views"]}},
        "oil_level_cm": round(float(Yf - 0.055), 3),
        "mockup_camera": {"px_per_cm": round(1 / S, 3), "distance_cm": round(d * S, 2), "eye_height_cm": round((YB - ye) * S, 3),
                          "base_row_px": round(YB, 1), "cap_top_row_px": round(y_top, 1)},
        "colours": {"cap": P["cap"], "cap_inner": P["cap_inner"], "oil": P["oil"]},
    }
    with open(os.path.join(BUILD, "stats.json"), "w") as f:
        json.dump(stats, f, indent=1)
    with open(os.path.join(BUILD, "preview.json"), "w") as f:
        json.dump({"name": NAME, "obj": f"../build/{product}/{NAME}.obj", "tex": f"../build/{product}/{P['texture']}",
                   "cap": P["cap"], "cap_inner": P["cap_inner"], "oil": P["oil"], "height": round(H, 3),
                   "eye_y": round((YB - ye) * S, 3), "dist": round(d * S, 2), "fov": 16, "exposure": P.get("exposure", 1.0)}, f, indent=1)
    tv = sum(len(m.v) for m in meshes)
    tt_ = sum(sum(len(fs) for _, fs in m.groups) for m in meshes)
    fmt = lambda x, n=1: f"{x:.{n}f}".replace(".", ",")
    readme = open(os.path.join(ROOT, "tools", "LISEZ-MOI.template.txt"), encoding="utf-8").read()
    for key, val in {**P, "verts": f"{tv:,}".replace(",", " "), "tris": f"{tt_:,}".replace(",", " "),
                     "tex_w": TEX_W, "tex_h": Ht, "h": fmt(H), "d": fmt(2 * r_max * S), "d_lab": fmt(stats["size_cm"]["label_diameter"]),
                     "d_cap": fmt(stats["size_cm"]["cap_diameter"]), "d_neck": fmt(stats["size_cm"]["neck_diameter"]),
                     "lab_h": fmt(stats["label"]["height_cm"]), "lab_b": fmt(stats["label"]["bottom_cm"]),
                     "fill": fmt(stats["oil_level_cm"])}.items():
        readme = readme.replace("{" + key + "}", str(val))
    open(os.path.join(BUILD, "LISEZ-MOI.txt"), "w", encoding="utf-8").write(readme)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("product", choices=sorted(PRODUCTS), help="product key in tools/products.json")
    build(ap.parse_args().product)
