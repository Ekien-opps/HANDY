#!/usr/bin/env python3
"""Marin'Or Ivoire · square clear PET jar (Pâte d'arachide 1 kg) -> Wavefront OBJ + MTL + textures.

Units: centimetres, Y up, centre of the base at the origin, front face towards +Z.
Every dimension is measured on the client's front mockup (src/<produit>/face-avant.webp): the body is
1045 px wide = 12 cm, the silhouette of the shoulder is read row by row from the alpha channel.

Objects (closed shells, smooth normals, UVs)
  Pot_PET        clear PET jar, wall 0.5 mm: rounded-square body (vertical corner radius 1 cm, oval bottom
                 fillet), shoulder rounding into a round neck (profile = mockup silhouette), thread bead,
                 support flange, finish and rolled lip.
  Pate_arachide  peanut paste filling the jar up to the base of the neck (tileable grain texture).
  Couvercle      brown screw cap: 70 vertical knurl ribs, smooth bottom band, rounded top edge, slightly
                 domed top, inside of the cap.
  Etiquette_avant / Etiquette_arriere
                 die-cut labels (straight sides, flat bottom, arched top), 0.12 mm paper on the flat
                 front / back faces (they follow the face where it starts to curve into the shoulder).
                 Printed side = planar projection of the mockup pixels inside the measured outline;
                 back and edges = white paper.

Run:  python3 tools/build_square_jar.py <produit>     (produits: tools/products.json)
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.geometry import LineString, Point, box
from shapely.geometry import Polygon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = json.load(open(os.path.join(ROOT, "tools", "products.json"), encoding="utf-8"))

# --------------------------------------------------------------------------- measured dimensions (cm)
A = 6.0                   # half width of the body (12 cm square), from the mockup
RC = 1.0                  # vertical corner radius: the labels (9.9 cm wide) sit on the flat faces
FB_H, FB_V = 0.65, 0.42   # oval bottom fillet (horizontal / vertical semi-axes), from rows 1003-1038
T_PET = 0.05              # PET wall
GAP_PASTE = 0.012         # paste <-> PET inner wall
SHOULDER_P = 1.0          # corner radius growth along the shoulder (rounded square -> circle at the neck)
# key rows on the front mockup (px)
ROW_SHOULDER = (141, 292)  # silhouette rows of the shoulder (top = neck base, bottom = full body width)
ROW_NECK = (121, 140)      # straight neck
ROW_FLANGE = (108, 118)    # clear support flange (649 px wide)
ROW_PASTE = 150            # top of the paste (dark line just under the neck)
ROW_CAP = (104, 20)        # cap: bottom edge, top of the side
CAP_TOP_DOME = 0.05
N_RIB, RIB_D = 70, 0.05    # 70 ribs (29 px pitch at the centre of a 644 px cap), groove depth
Y_LIP_ABOVE_FLANGE = 0.80  # finish height above the flange (hidden by the cap)
LABEL_T, LABEL_GAP = 0.012, 0.006
TILE = 2.5                 # paste grain texture tile (cm)
PASTE_DOME = 0.03          # slight dome of the paste surface under the neck

# ring sampling of the rounded square: 10 samples per half flat side, 6 per half corner (128 around)
N_FLAT_HALF, N_CORNER_HALF = 10, 6


def hex_lin(h):
    """sRGB hex -> linear RGB (OBJ importers such as Blender's copy Kd straight into linear base colour)."""
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return " ".join("%.4f" % (x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def to_hex(rgb):
    return "#%02X%02X%02X" % tuple(int(round(min(max(v, 0), 255))) for v in rgb)


# --------------------------------------------------------------------------- mockup frame
class Frame:
    """Pixel <-> cm mapping of one mockup (jar centre, scale from the body width, base row)."""

    def __init__(self, path, width_cm):
        im = Image.open(path).convert("RGBA")
        self.rgba = np.asarray(im)
        a = self.rgba[..., 3].astype(float) / 255
        self.alpha = a
        W = a.sum(1)
        self.W = W
        body = W > 0.985 * W.max()
        rows = np.where(body)[0]
        self.Wb = float(np.median(W[rows]))
        xs = np.arange(a.shape[1]) + 0.5
        cx = (a[rows] * xs).sum(1) / a[rows].sum(1)
        self.x0 = float(np.median(cx))
        self.s = width_cm / self.Wb
        half = np.where(W > 0.5 * self.Wb)[0]
        self.yb = float(half.max() + 1)  # bottom edge of the last row wider than half the body

    def world(self, xp, yp, mirror=False):
        x = (np.asarray(xp, float) - self.x0) * self.s
        return (-x if mirror else x), (self.yb - np.asarray(yp, float)) * self.s

    def Y(self, yp):
        return (self.yb - yp) * self.s


# --------------------------------------------------------------------------- rounded-square rings
def ring_phis():
    """Ray angles (x = r sin phi, z = r cos phi) from the arc-length sampling of the body section,
    starting at the back centre (phi = -pi) and increasing (left side, front, right side)."""
    oct_ = []
    lf, lc = A - RC, RC * math.pi / 4
    for i in range(N_FLAT_HALF):
        oct_.append(math.atan2(lf * i / N_FLAT_HALF, A))
    for i in range(N_CORNER_HALF):
        t = (math.pi / 4) * i / N_CORNER_HALF  # angle on the corner arc, 0 at the flat junction
        x, z = (A - RC) + RC * math.sin(t), (A - RC) + RC * math.cos(t)
        oct_.append(math.atan2(x, z))
    oct_ = np.asarray(oct_)  # [0, pi/4)
    q = np.concatenate([oct_, [math.pi / 4], (math.pi / 2 - oct_[1:])[::-1]])  # [0, pi/2)
    full = np.concatenate([q + k * math.pi / 2 for k in range(4)])  # [0, 2pi)
    full = np.sort((full + math.pi) % (2 * math.pi) - math.pi)
    return full


def ray_hit(h, c, phis):
    """Distance from the axis to a rounded square (half width h, corner radius c) along each ray."""
    if h <= 1e-12:
        return np.zeros_like(phis)
    c = min(max(c, 0.0), h)
    dx, dz = np.abs(np.sin(phis)), np.abs(np.cos(phis))
    m = np.maximum(dx, dz)
    t = h / m
    px, pz = t * dx, t * dz
    on_corner = np.minimum(px, pz) > h - c + 1e-12
    cc = h - c
    dc = dx * cc + dz * cc
    disc = np.maximum(dc ** 2 - 2 * cc ** 2 + c ** 2, 0)
    tc = dc + np.sqrt(disc)
    return np.where(on_corner, tc, t)


def loft(profile, phis, rib=None):
    """profile: list of (h, Y, c[, rib_weight]); returns vertices (L, NP, 3)."""
    V = np.zeros((len(profile), len(phis), 3))
    for j, p in enumerate(profile):
        h, Y, c = p[0], p[1], p[2]
        r = ray_hit(h, c, phis)
        if rib is not None and len(p) > 3 and p[3] > 0:
            r = r - p[3] * rib
        V[j, :, 0] = r * np.sin(phis)
        V[j, :, 1] = Y
        V[j, :, 2] = r * np.cos(phis)
    return V


def grid_faces(L, NP):
    j, k = np.meshgrid(np.arange(L - 1), np.arange(NP), indexing="ij")
    a = j * NP + k
    b = j * NP + (k + 1) % NP
    c = (j + 1) * NP + (k + 1) % NP
    d = (j + 1) * NP + k
    return np.concatenate([np.stack([a, b, c], -1).reshape(-1, 3), np.stack([a, c, d], -1).reshape(-1, 3)])


def vertex_normals(V, F):
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    N = np.zeros_like(V)
    for i in range(3):
        np.add.at(N, F[:, i], fn)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


def signed_volume(V, F):
    return float(np.einsum("ij,ij->i", V[F[:, 0]], np.cross(V[F[:, 1]], V[F[:, 2]])).sum() / 6)


def solid(Vg):
    """Closed loft (poles at both ends): outward winding flag + smooth normals (L, NP, 3)."""
    L, NP, _ = Vg.shape
    V = Vg.reshape(-1, 3)
    F = grid_faces(L, NP)
    flip = signed_volume(V, F) < 0
    if flip:
        F = F[:, ::-1]
    N = vertex_normals(V, F).reshape(L, NP, 3)
    # pole rings: one normal for all coincident vertices
    for j in (0, L - 1):
        if np.ptp(Vg[j], axis=0).max() < 1e-9:
            n = N[j].sum(0)
            N[j] = n / np.linalg.norm(n)
    return flip, N, abs(signed_volume(V, F))


# --------------------------------------------------------------------------- mesh container (as tools of marinor-pots)
class Mesh:
    def __init__(self, name):
        self.name = name
        self.v, self.vt, self.vn, self.groups = [], [], [], []

    def add_group(self, mat):
        self.groups.append((mat, []))
        return self.groups[-1][1]

    def addv(self, p, uv, n):
        self.v.append(tuple(float(x) for x in p))
        self.vt.append(tuple(float(x) for x in uv))
        n = np.asarray(n, float)
        self.vn.append(tuple(n / (np.linalg.norm(n) + 1e-12)))
        return len(self.v) - 1


def emit(mesh, mat, Vg, Ng, j0, j1, flip, uv="index", mat_fn=None):
    """Write rows j0..j1 of a loft into mesh. uv: 'index' (u = k/NP, v = row), 'wrap' (arc length in
    TILE units, integer number of tiles around), 'planar' (x, z / TILE, no seam)."""
    faces = mesh.add_group(mat)
    other = {}
    NP = Vg.shape[1]
    rows = range(j0, j1 + 1)
    seam = uv != "planar"
    cols = NP + 1 if seam else NP
    idx = np.zeros((j1 - j0 + 1, cols), int)
    if uv == "wrap":
        vacc = 0.0
        prev = None
    for jj, j in enumerate(rows):
        P = Vg[j]
        if uv == "wrap":
            mid = P.mean(0)
            if prev is not None:
                vacc += float(np.mean(np.linalg.norm(P - prev, axis=1)))
            prev = P
            seg = np.linalg.norm(np.roll(P, -1, 0) - P, axis=1)
            Lr = seg.sum()
            nt = max(1, round(Lr / TILE))
            acc = np.concatenate([[0], np.cumsum(seg)])
            us = acc / max(Lr, 1e-9) * nt
        for k in range(cols):
            kk = k % NP
            if uv == "index":
                t = (k / NP, jj / max(1, j1 - j0))
            elif uv == "wrap":
                t = (us[k], vacc / TILE)
            else:
                t = (P[kk, 0] / TILE, P[kk, 2] / TILE)
            idx[jj, k] = mesh.addv(P[kk], t, Ng[j, kk])
    for jj in range(j1 - j0):
        for k in range(NP):
            k1 = k + 1 if seam else (k + 1) % NP
            a, b, c, d = idx[jj, k], idx[jj, k1], idx[jj + 1, k1], idx[jj + 1, k]
            m2 = mat_fn(j0 + jj, k % NP) if mat_fn else None
            dst = faces if not m2 or m2 == mat else other.setdefault(m2, mesh.add_group(m2))
            for tri in ((a, b, c), (a, c, d)):
                p = [np.asarray(mesh.v[i]) for i in tri]
                if np.linalg.norm(np.cross(p[1] - p[0], p[2] - p[0])) < 1e-12:
                    continue
                dst.append(tri[::-1] if flip else tri)


# --------------------------------------------------------------------------- profiles
def shoulder_curve(fr):
    """(h, Y) of the shoulder, read on the mockup silhouette (row widths of the alpha channel)."""
    y0, y1 = ROW_SHOULDER
    ys = np.arange(y0, y1 + 1)
    W = ndimage.gaussian_filter1d(fr.W.astype(float), 1.0)[ys]
    h = np.minimum(A * W / W[-1], A)
    Y = fr.Y(ys + 0.5)
    pts = np.stack([h, Y], 1)[::-1]  # from the body (bottom) up to the neck
    pts[0] = (A, pts[0, 1])
    ls = LineString(pts).simplify(0.0015, preserve_topology=False)
    return np.asarray(ls.coords)


def c_of(h, rn):
    w = np.clip((A - h) / (A - rn), 0, 1) ** SHOULDER_P
    return RC + (h - RC) * w


def profile_normals(P):
    T = np.zeros_like(P)
    T[1:-1] = P[2:] - P[:-2]
    T[0] = P[1] - P[0]
    T[-1] = P[-1] - P[-2]
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    return np.stack([T[:, 1], -T[:, 0]], 1)


def body_profile(fr):
    """Outer profile from the bottom centre up to the base of the neck: list of (h, Y, c)."""
    sh = shoulder_curve(fr)
    rn = float(sh[-1, 0])
    prof = []
    h0, c0 = A - FB_H, RC - FB_H
    for f in (0.0, 0.2, 0.4, 0.6, 0.8, 0.93):
        prof.append((h0 * f, 0.0, c0 * f))
    for t in np.linspace(0, math.pi / 2, 13):
        h = A - FB_H + FB_H * math.sin(t)
        prof.append((h, FB_V * (1 - math.cos(t)), RC - (A - h)))
    y_s0 = float(sh[0, 1])
    for Y in np.linspace(FB_V, y_s0, 10)[1:-1]:
        prof.append((A, float(Y), RC))
    for h, Y in sh:
        prof.append((float(h), float(Y), float(c_of(h, rn))))
    return prof, rn


def offset_profile(prof, d):
    P = np.asarray([(p[0], p[1]) for p in prof])
    N = profile_normals(P)
    N[0] = (0, -1)  # bottom centre
    out = []
    for (h, Y, c), (nh, ny) in zip(prof, N):
        hh = max(h - d * nh, 0.0)
        out.append((hh if h > 1e-9 else 0.0, Y - d * ny, max(min(c - d * nh, hh), 0.0) if h > 1e-9 else 0.0))
    return out


def pet_profile(fr):
    prof, rn = body_profile(fr)
    y_nb = prof[-1][1]  # base of the neck
    y_f0, y_f1 = fr.Y(ROW_FLANGE[1] + 1), fr.Y(ROW_FLANGE[0])
    r_fl = A * fr.W[ROW_FLANGE[0]:ROW_FLANGE[1] + 1].max() / fr.W[ROW_SHOULDER[1]]
    up = []
    # neck with one thread bead
    yb_ = 0.5 * (y_nb + y_f0)
    for Y in (y_nb + 0.04, yb_ - 0.06, yb_ - 0.03, yb_, yb_ + 0.03, yb_ + 0.06, y_f0 - 0.035):
        up.append((rn + 0.025 * math.exp(-((Y - yb_) / 0.028) ** 2), Y, None))
    # flange (thickness y_f0..y_f1, rounded edge)
    rr = 0.035
    up.append((rn + 0.03, y_f0, None))
    for a in np.linspace(-90, 0, 4):
        up.append((r_fl - rr + rr * math.cos(math.radians(a)), y_f0 + rr + rr * math.sin(math.radians(a)), None))
    for a in np.linspace(0, 90, 4):
        up.append((r_fl - rr + rr * math.cos(math.radians(a)), y_f1 - rr + rr * math.sin(math.radians(a)), None))
    up.append((rn + 0.03, y_f1, None))
    # finish and rolled lip (hidden by the cap)
    y_lip = y_f1 + Y_LIP_ABOVE_FLANGE
    up.append((rn, y_f1 + 0.035, None))
    up.append((rn, y_lip - 0.05, None))
    for a in np.linspace(0, 180, 7)[1:]:
        up.append((rn - 0.05 + 0.05 * math.cos(math.radians(a)), y_lip - 0.05 + 0.05 * math.sin(math.radians(a)), None))
    up.append((rn - 0.10, y_nb + 0.10, None))
    up = [(h, Y, h) for h, Y, _ in up]  # round sections
    inner = offset_profile(prof, T_PET)[::-1]
    full = prof + up + inner
    dims = {"rn": rn, "y_neck": y_nb, "r_flange": r_fl, "y_flange": (y_f0, y_f1), "y_lip": y_lip}
    return full, len(prof), len(prof) + len(up), dims, prof


def paste_profile(fr, prof):
    off = offset_profile(prof, T_PET + GAP_PASTE)
    y_fill = fr.Y(ROW_PASTE)
    out = []
    for i, p in enumerate(off):
        if p[1] < y_fill or i < 6:
            out.append(p)
            continue
        q = off[i - 1]
        t = (y_fill - q[1]) / (p[1] - q[1])
        out.append(tuple(q[k] + t * (p[k] - q[k]) for k in range(3)))
        break
    side_end = len(out) - 1
    h, Y, c = out[-1]
    for f in (0.85, 0.68, 0.5, 0.32, 0.16, 0.0):
        out.append((h * f, y_fill + PASTE_DOME * (1 - f * f), c * f))
    return out, side_end, y_fill



def cap_profile(fr):
    rows = np.arange(ROW_CAP[1] + 6, ROW_CAP[0] - 6)
    R = float(A * np.median(fr.W[rows]) / fr.W[ROW_SHOULDER[1]])
    y0, y_top = fr.Y(ROW_CAP[0]), fr.Y(ROW_CAP[1])
    th = 0.12
    rin = R - th
    y_r0, y_r1 = y0 + 0.19, y_top - 0.13  # ribs end below the rounded top edge (radius 0.08)
    outer = []  # (r, Y, rib weight) from the inner bottom edge round the outside to the top centre
    outer.append((rin, y0, 0))
    outer.append((rin + 0.03, y0, 0))
    for a in np.linspace(-90, 0, 4):
        outer.append((R - 0.03 + 0.03 * math.cos(math.radians(a)), y0 + 0.03 + 0.03 * math.sin(math.radians(a)), 0))
    outer.append((R, y_r0 - 0.06, 0))
    for Y, w in ((y_r0 - 0.03, 0.0), (y_r0, 0.5), (y_r0 + 0.03, 1.0), (0.5 * (y_r0 + y_r1), 1.0),
                 (y_r1 - 0.03, 1.0), (y_r1, 0.5), (y_r1 + 0.02, 0.0)):
        outer.append((R, Y, w))
    rt = 0.08
    for a in np.linspace(0, 90, 7):
        outer.append((R - rt + rt * math.cos(math.radians(a)), y_top - rt + rt * math.sin(math.radians(a)), 0))
    for f in (0.8, 0.6, 0.4, 0.2, 0.0):
        r = (R - rt) * f
        outer.append((r, y_top + CAP_TOP_DOME * (1 - f * f), 0))
    inner = [(rin, y0, 0), (rin, y_top - th - 0.04, 0)]
    for a in np.linspace(0, 90, 4)[1:]:
        inner.append((rin - 0.04 + 0.04 * math.cos(math.radians(a)), y_top - th - 0.04 + 0.04 * math.sin(math.radians(a)), 0))
    for f in (0.7, 0.4, 0.0):
        inner.append(((rin - 0.04) * f, y_top - th, 0))
    full = outer[::-1] + inner[1:]  # top centre -> down the outside -> bottom -> up the inside -> inner centre
    n_out = len(outer)
    return full, n_out, {"R": R, "y0": y0, "y_top": y_top, "ribs": (y_r0, y_r1)}


def cap_phis():
    """Ring samples of the knurled cap: per rib pitch a groove (|f| < 0.13, flat bottom |f| < 0.10) and a land.
    Groove edges are duplicated columns (zero-width quads are dropped) so the walls get crisp normals."""
    F = np.array([0.0, 0.10, 0.10, 0.13, 0.13, 0.5, 0.87, 0.87, 0.90, 0.90])
    G = np.array([1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0])
    pitch = 2 * math.pi / N_RIB
    ph = np.concatenate([-math.pi + pitch * (i + F + 0.5) for i in range(N_RIB)])
    g = np.tile(G, N_RIB)
    fmid = np.tile(np.append((F[:-1] + F[1:]) / 2, 0.95), N_RIB)  # rib fraction at the middle of each column interval
    groove = np.abs(((fmid + 0.5) % 1.0) - 0.5) < 0.13
    return ph, g, groove


# --------------------------------------------------------------------------- labels
def label_outline(L):
    """Measured die-cut outline in mockup pixels: straight sides, flat bottom, arched top."""
    xl, xr, yb = L["xl"], L["xr"], L["yb"]
    cx, cy, R = L["arc"]
    sharp = box(xl, cy - R - 50, xr, yb).intersection(Point(cx, cy).buffer(R, quad_segs=1024))
    top_round = sharp.buffer(-L["r_top"], quad_segs=32).buffer(L["r_top"], quad_segs=32)
    bot_round = box(xl, cy - R - 400, xr, yb).buffer(-L["r_bottom"], quad_segs=32).buffer(L["r_bottom"], quad_segs=32)
    return top_round.intersection(bot_round)


def rasterize(poly, shape, ss=4):
    W, H = shape[1], shape[0]
    img = Image.new("L", (W * ss, H * ss), 0)
    ext = [(x * ss, y * ss) for x, y in np.asarray(poly.exterior.coords)]
    ImageDraw.Draw(img).polygon(ext, fill=255)
    return np.asarray(img.resize((W, H), Image.BOX)).astype(np.float32) / 255


def label_like(rgb):
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return ((B / np.maximum(R, 1) < 0.25) & (R > 205)) | (rgb.min(-1) > 225) | (R > 232)


def label_texture(fr, poly, dst):
    """Crop the label from the mockup; colours pushed past the outline (no fringe), alpha = outline."""
    x0, y0, x1, y1 = poly.bounds
    m = 10
    cx0, cy0 = int(math.floor(x0)) - m, int(math.floor(y0)) - m
    cx1, cy1 = int(math.ceil(x1)) + m, int(math.ceil(y1)) + m
    rgb = fr.rgba[cy0:cy1, cx0:cx1, :3].astype(np.float32)
    shp = rgb.shape[:2]
    sh = lambda p: Polygon(np.asarray(p.exterior.coords) - (cx0, cy0))
    inside = rasterize(sh(poly), shp) > 0.999
    deep = rasterize(sh(poly.buffer(-2.0)), shp) > 0.999
    band = inside & ~(rasterize(sh(poly.buffer(-4.0)), shp) > 0.999)
    good = deep & ~(band & ~label_like(rgb))
    idx = ndimage.distance_transform_edt(~good, return_distances=False, return_indices=True)
    out = rgb[idx[0], idx[1]]
    alpha = rasterize(sh(poly.buffer(1.0)), shp)
    Image.fromarray(np.dstack([out, alpha * 255]).round().clip(0, 255).astype(np.uint8), "RGBA").save(dst, optimize=True)
    stats = {"texture_px": [int(shp[1]), int(shp[0])], "edge_band_px_replaced": int((band & ~label_like(rgb)).sum()),
             "edge_band_px": int(band.sum())}
    return (cx0, cy0, cx1 - cx0, cy1 - cy0), stats


def build_label(name, mat, fr, poly_px, crop, face_z, back):
    """Thin paper label: printed grid (planar UV of the mockup), white back, edge strip."""
    geo = poly_px.buffer(-1.0, quad_segs=32)
    gx0, _, gx1, _ = geo.bounds
    ncol, nrow = 100, 40
    tcol = (1 - np.cos(np.pi * np.linspace(0, 1, ncol + 1))) / 2
    xs = gx0 + 1e-3 + (gx1 - gx0 - 2e-3) * tcol
    u = np.linspace(0, 1, nrow + 1)
    trow = u * (1.4 - 0.4 * u)  # finer rows towards the top (where the face starts to curve)
    P = np.zeros((nrow + 1, ncol + 1, 2))
    for i, x in enumerate(xs):
        seg = geo.intersection(LineString([(x, -1e5), (x, 1e5)]))
        ys = np.asarray(seg.coords)[:, 1] if seg.geom_type == "LineString" else np.concatenate([np.asarray(g.coords)[:, 1] for g in seg.geoms])
        ytop, ybot = ys.min(), ys.max()
        P[:, i, 0] = x
        P[:, i, 1] = ybot + (ytop - ybot) * trow
    cx0, cy0, cw, ch = crop
    X, Y = fr.world(P[..., 0], P[..., 1], mirror=back)
    sgn = -1.0 if back else 1.0
    zf = sgn * (face_z(Y) + LABEL_GAP + LABEL_T)
    zb = sgn * (face_z(Y) + LABEL_GAP)
    dz = (face_z(Y + 1e-3) - face_z(Y - 1e-3)) / 2e-3
    nfront = np.stack([np.zeros_like(Y), -dz, np.full_like(Y, 1.0)], -1) * np.array([1, 1, sgn])
    UV = np.stack([(P[..., 0] - cx0) / cw, 1 - (P[..., 1] - cy0) / ch], -1)
    mesh = Mesh(name)
    fp = mesh.add_group(mat)
    ids_f = np.zeros((nrow + 1, ncol + 1), int)
    ids_b = np.zeros((nrow + 1, ncol + 1), int)
    for j in range(nrow + 1):
        for i in range(ncol + 1):
            ids_f[j, i] = mesh.addv((X[j, i], Y[j, i], zf[j, i]), UV[j, i], nfront[j, i])
    pp = mesh.add_group("Etiquette_papier")
    for j in range(nrow + 1):
        for i in range(ncol + 1):
            ids_b[j, i] = mesh.addv((X[j, i], Y[j, i], zb[j, i]), UV[j, i], -nfront[j, i])
    for j in range(nrow):
        for i in range(ncol):
            a, b, c, d = ids_f[j, i], ids_f[j, i + 1], ids_f[j + 1, i + 1], ids_f[j + 1, i]
            fp += [(a, b, c), (a, c, d)]
            a, b, c, d = ids_b[j, i], ids_b[j, i + 1], ids_b[j + 1, i + 1], ids_b[j + 1, i]
            pp += [(a, c, b), (a, d, c)]
    # edge strip along the boundary loop
    loop = [(0, i) for i in range(ncol + 1)] + [(j, ncol) for j in range(1, nrow + 1)] + \
           [(nrow, i) for i in range(ncol - 1, -1, -1)] + [(j, 0) for j in range(nrow - 1, 0, -1)]
    pts = np.asarray([(X[j, i], Y[j, i]) for j, i in loop])
    n = len(loop)
    ep = mesh.add_group("Etiquette_papier")
    centre = pts.mean(0)
    for q in range(n):
        j0, i0 = loop[q]
        j1, i1 = loop[(q + 1) % n]
        e = pts[(q + 1) % n] - pts[q]
        if np.linalg.norm(e) < 1e-9:
            continue
        nn = np.array([e[1], -e[0], 0.0])
        if np.dot(nn[:2], 0.5 * (pts[q] + pts[(q + 1) % n]) - centre) < 0:
            nn = -nn
        v = [mesh.addv((X[jj, ii], Y[jj, ii], zz[jj, ii]), (0, 0), nn)
             for (jj, ii), zz in (((j0, i0), zb), ((j1, i1), zb), ((j1, i1), zf), ((j0, i0), zf))]
        ep += [(v[0], v[1], v[2]), (v[0], v[2], v[3])]
    # clearance between the paper back and the PET face (piecewise-linear both), per column
    clr = []
    for i in range(ncol + 1):
        fine = np.linspace(Y[0, i], Y[-1, i], 300)
        clr.append(float((np.abs(np.interp(fine, Y[:, i], zb[:, i])) - face_z(fine)).min()))
    w_cm = float(X.max() - X.min())
    h_cm = float(Y.max() - Y.min())
    return mesh, {"width_cm": round(w_cm, 3), "height_cm": round(h_cm, 3),
                  "x_cm": [round(float(X.min()), 3), round(float(X.max()), 3)],
                  "y_cm": [round(float(Y.min()), 3), round(float(Y.max()), 3)], "clearance": min(clr)}


# --------------------------------------------------------------------------- textures and colours
def paste_texture(hexcol, dst, size=512, seed=20261013):
    """Tileable grain of the paste (noise filtered on a periodic grid), mean = the calibrated colour."""
    rng = np.random.default_rng(seed)
    k = np.fft.fftfreq(size)
    K2 = k[:, None] ** 2 + k[None, :] ** 2

    def band(sig):
        n = np.fft.fft2(rng.standard_normal((size, size)))
        f = np.real(np.fft.ifft2(n * np.exp(-2 * (math.pi * sig) ** 2 * K2)))
        return (f - f.mean()) / (f.std() + 1e-12)

    lum = 1 + 0.009 * band(48) + 0.014 * band(7) + 0.03 * band(1.1)
    base = np.array([int(hexcol[i:i + 2], 16) for i in (1, 3, 5)], float)
    img = base[None, None, :] * lum[..., None]
    sp = band(2.2)
    dark = np.clip((sp - 2.3) / 0.8, 0, 1)[..., None]       # sparse roasted specks
    light = np.clip((-sp - 2.5) / 0.8, 0, 1)[..., None]     # a few lighter oily grains
    img = img * (1 - 0.16 * dark * np.array([0.75, 1.0, 1.15])) + light * 0.08 * (255 - img)
    img *= base / img.reshape(-1, 3).mean(0)
    Image.fromarray(img.round().clip(0, 255).astype(np.uint8), "RGB").save(dst, quality=92)


def sample_colours(ff, fb, masks):
    """Median colours on the mockups (paste outside the labels, cap lands) and the labels' white."""
    out = {}
    whites, pastes = [], []
    for fr, mk in zip((ff, fb), masks):
        rgb = fr.rgba[..., :3].astype(float)
        whites.append(rgb[(mk > 0.999) & (rgb.min(-1) > 235)])
        a = fr.alpha > 0.999
        edge = ndimage.distance_transform_edt(a) > 24
        lab = ndimage.binary_dilation(mk > 0.01, iterations=10)
        yy = np.arange(a.shape[0])[:, None] * np.ones((1, a.shape[1]))
        rows = (yy > ROW_SHOULDER[1] + 10) & (yy < fr.yb - 0.6 / fr.s)
        m = a & edge & ~lab & rows & (rgb.max(-1) < 240)
        pastes.append(rgb[m])
    w = np.concatenate(whites).mean(0)
    p = np.median(np.concatenate(pastes), 0)
    rgb = ff.rgba[..., :3].astype(float)
    cap = rgb[ROW_CAP[1] + 12:ROW_CAP[0] - 25, int(ff.x0) - 220:int(ff.x0) + 220].reshape(-1, 3)
    lum = cap.mean(1)
    land = cap[lum > np.percentile(lum, 45)]
    c = np.median(land, 0)
    top = rgb[ROW_CAP[1] - 10:ROW_CAP[1] - 3, int(ff.x0) - 150:int(ff.x0) + 150].reshape(-1, 3)
    out["label_white"] = to_hex(w)
    out["paste_mockup"] = to_hex(p)
    out["cap_mockup"] = to_hex(c)
    out["cap_groove_mockup"] = to_hex(cap[lum < np.percentile(lum, 12)].mean(0))
    out["cap_top_mockup"] = to_hex(np.median(top, 0))
    out["paste_over_white"] = [round(float(x), 3) for x in p / w]
    out["cap_over_white"] = [round(float(x), 3) for x in c / w]
    return out


# --------------------------------------------------------------------------- build
def build(product):
    P = PRODUCTS[product]
    NAME = P["name"]
    BUILD = os.path.join(ROOT, "build", product)
    os.makedirs(BUILD, exist_ok=True)
    ff = Frame(os.path.join(ROOT, P["front"]), P["width_cm"])
    fb = Frame(os.path.join(ROOT, P["back"]), P["width_cm"])
    phis = ring_phis()
    meshes, stats = [], {"product": product, "objects": {}}

    # ---- PET jar
    pet, i_up, i_in, dims, prof = pet_profile(ff)
    Vg = loft(pet, phis)
    flip, Ng, _ = solid(Vg)
    m = Mesh("Pot_PET")
    # neck, flange, finish and lip: thick injection-moulded PET (own material: thicker refraction in PBR)
    emit(m, "PET_transparent", Vg, Ng, 0, len(pet) - 1, flip,
         mat_fn=lambda j, k: "PET_col" if i_up - 1 <= j < i_in else None)
    meshes.append(m)

    # ---- paste
    pp, side_end, y_fill = paste_profile(ff, prof)
    Vp = loft(pp, phis)
    flip_p, Np_, vol = solid(Vp)
    m = Mesh("Pate_arachide")
    emit(m, "Pate_arachide", Vp, Np_, 0, 6, flip_p, uv="planar")
    emit(m, "Pate_arachide", Vp, Np_, 6, side_end, flip_p, uv="wrap")
    emit(m, "Pate_arachide", Vp, Np_, side_end, len(pp) - 1, flip_p, uv="planar")
    meshes.append(m)

    # ---- cap
    cp, n_out, cdims = cap_profile(ff)
    cph, g, groove = cap_phis()
    Vc = loft([(r, Y, r, w) for r, Y, w in cp], cph, rib=RIB_D * g)
    flip_c, Nc, _ = solid(Vc)
    m = Mesh("Couvercle")
    wt = [p[2] for p in cp]
    in_rib = lambda j, k: groove[k] and max(wt[j], wt[j + 1]) > 0
    emit(m, "Couvercle", Vc, Nc, 0, n_out - 1, flip_c, mat_fn=lambda j, k: "Couvercle_stries" if in_rib(j, k) else None)
    emit(m, "Couvercle_interieur", Vc, Nc, n_out - 1, len(cp) - 1, flip_c)
    meshes.append(m)

    # ---- labels
    prof_np = np.asarray([(p[0], p[1]) for p in prof])
    k0 = 6 + 13  # after the bottom disc and fillet: Y increases monotonically
    face_z = lambda Y: np.interp(Y, prof_np[k0:, 1], prof_np[k0:, 0])
    masks, labels = [], {}
    for key, fr, back, mat, nm in (("label_front", ff, False, "Etiquette_avant", "Etiquette_avant"),
                                   ("label_back", fb, True, "Etiquette_arriere", "Etiquette_arriere")):
        poly = label_outline(P[key])
        tex = f"{product}_{'etiquette-arriere' if back else 'etiquette-avant'}.png"
        crop, tstats = label_texture(fr, poly, os.path.join(BUILD, tex))
        masks.append(rasterize(poly, fr.alpha.shape))
        lm, lstats = build_label(nm, mat, fr, poly, crop, face_z, back)
        meshes.append(lm)
        labels[key] = {**lstats, **tstats, "texture": tex}
    stats["label_clearance_cm_min"] = round(min(v.pop("clearance") for v in labels.values()), 5)

    # ---- colours and paste texture
    cols = sample_colours(ff, fb, masks)
    tex_paste = f"{product}_pate-grain.jpg"
    paste_texture(P["paste"], os.path.join(BUILD, tex_paste))

    # ---- write OBJ + MTL
    obj_path = os.path.join(BUILD, NAME + ".obj")
    mtl_name = NAME + ".mtl"
    with open(obj_path, "w") as f:
        f.write(f"# Marin'Or Ivoire - {P['title']} - square clear PET jar, {P['cap_name']} screw cap\n")
        f.write("# Units: centimetres. Y up. Base centre at origin. Front label faces +Z.\n")
        f.write(f"mtllib {mtl_name}\n")
        off = 1
        for mm in meshes:
            f.write(f"o {mm.name}\n")
            for p in mm.v:
                f.write("v %.5f %.5f %.5f\n" % p)
            for t in mm.vt:
                f.write("vt %.6f %.6f\n" % t)
            for n in mm.vn:
                f.write("vn %.5f %.5f %.5f\n" % n)
            V = np.asarray(mm.v)
            VN = np.asarray(mm.vn)
            for mat, fs in mm.groups:
                f.write(f"usemtl {mat}\ns 1\n")
                for tri in fs:
                    i0, i1, i2 = tri
                    gn = np.cross(V[i1] - V[i0], V[i2] - V[i0])
                    if np.dot(gn, VN[i0] + VN[i1] + VN[i2]) < 0:  # make winding agree with the shading normals
                        i1, i2 = i2, i1
                    a, b, c3 = (i + off for i in (i0, i1, i2))
                    f.write(f"f {a}/{a}/{a} {b}/{b}/{b} {c3}/{c3}/{c3}\n")
            off += len(mm.v)
    tex_f, tex_b = labels["label_front"]["texture"], labels["label_back"]["texture"]
    with open(os.path.join(BUILD, mtl_name), "w") as f:
        f.write(f"# Marin'Or Ivoire - {P['title']}\n# Kd values are LINEAR RGB (sRGB hex in comments)\n")
        f.write(f"""
newmtl PET_transparent
Ka 0 0 0
Kd 0.92 0.93 0.93
Ks 0.9 0.9 0.9
Ns 900
Ni 1.57
d 0.15
Tr 0.85
Tf 0.97 0.98 0.98
illum 7

newmtl PET_col
# col, collerette, goulot et lèvre (PET plus épais)
Ka 0 0 0
Kd 0.92 0.93 0.93
Ks 0.9 0.9 0.9
Ns 900
Ni 1.57
d 0.2
Tr 0.8
Tf 0.95 0.96 0.96
illum 7

newmtl Pate_arachide
# {P['paste']} (moyenne de la texture de grain)
Ka 0 0 0
Kd 1 1 1
Ks 0.10 0.10 0.10
Ns 40
d 1
illum 2
map_Kd {tex_paste}

newmtl Couvercle
# {P['cap']}
Ka 0 0 0
Kd {hex_lin(P['cap'])}
Ks 0.30 0.30 0.30
Ns 250
d 1
illum 2

newmtl Couvercle_stries
# {P['cap_groove']} (fond et flancs des stries : ombre des fentes étroites)
Ka 0 0 0
Kd {hex_lin(P['cap_groove'])}
Ks 0.1 0.1 0.1
Ns 60
d 1
illum 2

newmtl Couvercle_interieur
# {P['cap_inner']}
Ka 0 0 0
Kd {hex_lin(P['cap_inner'])}
Ks 0.1 0.1 0.1
Ns 40
d 1
illum 2

newmtl Etiquette_avant
Ka 0 0 0
Kd 1 1 1
Ks 0.25 0.25 0.25
Ns 120
d 1
illum 2
map_Kd {tex_f}

newmtl Etiquette_arriere
Ka 0 0 0
Kd 1 1 1
Ks 0.25 0.25 0.25
Ns 120
d 1
illum 2
map_Kd {tex_b}

newmtl Etiquette_papier
Ka 0 0 0
Kd 0.91 0.91 0.90
Ks 0.05 0.05 0.05
Ns 20
d 1
illum 2
""")
    allv = np.concatenate([np.asarray(mm.v) for mm in meshes])
    bb0, bb1 = allv.min(0), allv.max(0)
    stats["objects"] = {mm.name: {"vertices": len(mm.v), "triangles": sum(len(fs) for _, fs in mm.groups)} for mm in meshes}
    stats["bbox_cm"] = [[round(float(x), 3) for x in bb0], [round(float(x), 3) for x in bb1]]
    stats["jar"] = {"width_cm": 2 * A, "depth_cm": 2 * A, "height_cm": round(float(bb1[1]), 3),
                    "corner_radius_cm": RC, "neck_diameter_cm": round(2 * dims["rn"], 3),
                    "flange_diameter_cm": round(2 * dims["r_flange"], 3),
                    "cap_diameter_cm": round(2 * cdims["R"], 3), "cap_height_cm": round(cdims["y_top"] + CAP_TOP_DOME - cdims["y0"], 3),
                    "cap_bottom_cm": round(cdims["y0"], 3), "shoulder_start_cm": round(prof[k0 + 8][1], 3),
                    "neck_base_cm": round(dims["y_neck"], 3), "paste_fill_cm": round(y_fill, 3),
                    "paste_volume_ml": round(vol, 1)}
    stats["mockup_frames"] = {"front": {"x0": round(ff.x0, 2), "px_per_cm": round(1 / ff.s, 2), "base_row": ff.yb},
                              "back": {"x0": round(fb.x0, 2), "px_per_cm": round(1 / fb.s, 2), "base_row": fb.yb}}
    stats["labels"] = labels
    stats["colours"] = {**cols, "paste_used": P["paste"], "cap_used": P["cap"], "cap_groove_used": P["cap_groove"], "cap_inner_used": P["cap_inner"]}
    with open(os.path.join(BUILD, "stats.json"), "w") as f:
        json.dump(stats, f, indent=1, ensure_ascii=False)
    with open(os.path.join(BUILD, "preview.json"), "w") as f:
        json.dump({"name": NAME, "obj": f"../build/{product}/{NAME}.obj", "front": f"../build/{product}/{tex_f}",
                   "back": f"../build/{product}/{tex_b}", "paste": f"../build/{product}/{tex_paste}",
                   "tile": TILE, "cap": P["cap"], "cap_groove": P["cap_groove"], "cap_inner": P["cap_inner"], "height": round(float(bb1[1]), 3)}, f, indent=1)
    readme = open(os.path.join(ROOT, "tools", "LISEZ-MOI.template.txt"), encoding="utf-8").read()
    fr_ = lambda v, d=1: (f"{v:.{d}f}").replace(".", ",")
    J = stats["jar"]
    subs = {**{k: v for k, v in P.items() if isinstance(v, str)}, "tex_f": tex_f, "tex_b": tex_b, "tex_p": tex_paste,
            "h": fr_(J["height_cm"]), "cap_d": fr_(J["cap_diameter_cm"]), "neck_d": fr_(J["neck_diameter_cm"]),
            "cap_h": fr_(J["cap_height_cm"]),
            "lf_w": fr_(labels["label_front"]["width_cm"]), "lf_h": fr_(labels["label_front"]["height_cm"]),
            "lb_w": fr_(labels["label_back"]["width_cm"]), "lb_h": fr_(labels["label_back"]["height_cm"]),
            "lf_px": "%d × %d" % tuple(labels["label_front"]["texture_px"]),
            "lb_px": "%d × %d" % tuple(labels["label_back"]["texture_px"]),
            "verts": f"{len(allv):,}".replace(",", " "),
            "tris": f"{sum(v['triangles'] for v in stats['objects'].values()):,}".replace(",", " ")}
    for k, v in subs.items():
        readme = readme.replace("{" + k + "}", str(v))
    open(os.path.join(BUILD, "LISEZ-MOI.txt"), "w", encoding="utf-8").write(readme)
    print(json.dumps({k: stats[k] for k in ("objects", "bbox_cm", "jar", "colours")}, ensure_ascii=False))
    print(json.dumps(stats["labels"]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("product", choices=sorted(PRODUCTS), help="product key in tools/products.json")
    build(ap.parse_args().product)
