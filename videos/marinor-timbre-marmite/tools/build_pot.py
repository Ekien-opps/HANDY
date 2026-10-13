#!/usr/bin/env python3
"""Marin'Or "timbre marmite" -- option B (2.5D) pot cut + repaint.

Cuts the single 512 px pot raster (assets/src/pot-rgb-512.png + pot-mask-512.png)
into animatable layers and repaints what the closed lid hides, then writes
full-canvas RGBA PNGs at 2x density (2160 x 2700 = the 1080 x 1350 canvas),
a manifest (pot.json), a parity report and review previews.

Deterministic: no randomness, re-runnable.  Never touches assets/src/.

    python3 tools/build_pot.py            # build everything
    python3 tools/build_pot.py --debug    # + geometry overlays in assets/build/debug/

Coordinate systems
  raster   : continuous coords of the 512 px pot image, pixel i covers [i, i+1)
  canvas   : composition px @1x, x = 162.444 + 1.44 * rx ; y = 360.45 + 1.44 * ry
  canvas2x : the PNG pixels, X = 2 * x
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy import optimize

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "src"
OUT = ROOT / "assets" / "build"
DEBUG = "--debug" in sys.argv

# ----------------------------------------------------------------------------
# canvas / mapping
# ----------------------------------------------------------------------------
CANVAS = (1080, 1350)
DEN = 2
CW, CH = CANVAS[0] * DEN, CANVAS[1] * DEN
OX, OY, SC = 74.55 + 1.8 * 48.83, 99.0 + 1.8 * 145.25, 1.8 * 0.8  # raster -> canvas@1x
OX2, OY2, SC2 = OX * DEN, OY * DEN, SC * DEN                   # raster -> canvas@2x

# working window inside the 2x canvas (the pot at rest lives in it)
WX0, WY0, WW, WH = 280, 660, 1580, 1600


def r2c(rx, ry):
    """raster continuous -> canvas @1x"""
    return OX + SC * np.asarray(rx, float), OY + SC * np.asarray(ry, float)


# window pixel centres in raster coords
_jj = np.arange(WW, dtype=np.float64)
_ii = np.arange(WH, dtype=np.float64)
RX = ((WX0 + _jj + 0.5 - OX2) / SC2)[None, :].repeat(WH, 0)
RY = ((WY0 + _ii + 0.5 - OY2) / SC2)[:, None].repeat(WW, 1)

PX = SC2  # output px per raster px


# ----------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------
def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def lerp(a, b, t):
    t = np.asarray(t, float)
    if np.ndim(a) and np.ndim(t):
        t = t[..., None]
    return a + (b - a) * t


def smooth(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def soft_inside(sd, w=1.15):
    """sd: signed distance in raster px (negative inside) -> AA coverage."""
    return np.clip(0.5 - sd * PX / w, 0.0, 1.0)


def ell_rho(cx, cy, a, b, x=None, y=None):
    x = RX if x is None else x
    y = RY if y is None else y
    return np.sqrt(((x - cx) / a) ** 2 + ((y - cy) / b) ** 2)


def ell_sd(cx, cy, a, b, x=None, y=None):
    """First-order signed distance (raster px, <0 inside) to an axis-aligned ellipse."""
    x = RX if x is None else x
    y = RY if y is None else y
    dx, dy = x - cx, y - cy
    rho = np.sqrt((dx / a) ** 2 + (dy / b) ** 2) + 1e-12
    gx, gy = dx / (a * a) / rho, dy / (b * b) / rho
    g = np.sqrt(gx * gx + gy * gy) + 1e-12
    return (rho - 1.0) / g


def ell_y(cx, cy, a, b, x, front=True):
    t = np.clip((np.asarray(x, float) - cx) / a, -1, 1)
    s = np.sqrt(1 - t * t)
    return cy + b * s if front else cy - b * s


def up(arr512, pad=24):
    """LANCZOS-resample a 512 raster field (HxW or HxWxC float) into the window."""
    a = np.asarray(arr512, np.float32)
    padw = ((pad, pad), (pad, pad)) + ((0, 0),) * (a.ndim - 2)
    a = np.pad(a, padw, mode="edge")
    box = ((WX0 - OX2) / SC2 + pad, (WY0 - OY2) / SC2 + pad,
           (WX0 + WW - OX2) / SC2 + pad, (WY0 + WH - OY2) / SC2 + pad)
    chans = a[..., None] if a.ndim == 2 else a
    out = [np.asarray(Image.fromarray(np.ascontiguousarray(chans[..., c]), mode="F")
                      .resize((WW, WH), Image.LANCZOS, box=box), np.float64)
           for c in range(chans.shape[2])]
    return out[0] if a.ndim == 2 else np.stack(out, -1)


def unsharp(img, sigma=1.4, amount=0.45):
    blur = ndi.gaussian_filter(img, (sigma, sigma, 0) if img.ndim == 3 else sigma)
    return img + amount * (img - blur)


def crisp_alpha(a_up, w=1.15, pre_sigma=0.7):
    """Turn a soft upscaled coverage into a crisp ~1 px AA edge (gradient-normalised)."""
    s = ndi.gaussian_filter(a_up, pre_sigma)
    gy, gx = np.gradient(s)
    g = np.hypot(gx, gy)
    d = (s - 0.5) / np.maximum(g, 1e-4)
    out = np.clip(d / w + 0.5, 0, 1)
    flat = g < 0.004
    out[flat] = np.clip(np.round(s[flat]), 0, 1)
    return out


def harmonic_fill(img, known, unknown):
    """Membrane (Laplace) fill of img (HxWxC) on `unknown`, Dirichlet on `known`
    neighbours, natural (Neumann) boundary elsewhere. Exact sparse solve."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
    img = img.copy()
    H, W = unknown.shape
    idx = -np.ones((H, W), int)
    uy, ux = np.nonzero(unknown)
    n = len(uy)
    idx[uy, ux] = np.arange(n)
    rows, cols, vals = [], [], []
    rhs = np.zeros((n, img.shape[2]))
    diag = np.zeros(n)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ny, nx = uy + dy, ux + dx
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        k = np.nonzero(ok)[0]
        nyk, nxk = ny[k], nx[k]
        isu = unknown[nyk, nxk]
        isk = known[nyk, nxk] & ~isu
        diag[k[isu | isk]] += 1
        rows += list(k[isu]); cols += list(idx[nyk[isu], nxk[isu]]); vals += [-1.0] * int(isu.sum())
        rhs[k[isk]] += img[nyk[isk], nxk[isk]]
    diag = np.maximum(diag, 1e-9)
    A = coo_matrix((np.concatenate([diag, vals]),
                    (np.concatenate([np.arange(n), rows]), np.concatenate([np.arange(n), cols]))),
                   shape=(n, n)).tocsr()
    sol = spsolve(A, rhs)
    img[uy, ux] = sol.reshape(n, -1)
    return img


def save_rgba(path, rgb, a):
    """rgb/a are window-sized arrays (rgb 0..255 straight, a 0..1) -> full 2x canvas PNG."""
    full = np.zeros((CH, CW, 4), np.uint8)
    a8 = np.clip(np.round(a * 255), 0, 255).astype(np.uint8)
    rgb8 = np.clip(np.round(rgb), 0, 255).astype(np.uint8)
    rgb8[a8 == 0] = 0
    full[WY0:WY0 + WH, WX0:WX0 + WW, :3] = rgb8
    full[WY0:WY0 + WH, WX0:WX0 + WW, 3] = a8
    Image.fromarray(full, "RGBA").save(path, optimize=True)
    return full


def over(dst_rgb, dst_a, src_rgb, src_a):
    """straight-alpha 'over'"""
    out_a = src_a + dst_a * (1 - src_a)
    pm = src_rgb * src_a[..., None] + dst_rgb * (dst_a * (1 - src_a))[..., None]
    out_rgb = np.where(out_a[..., None] > 1e-6, pm / np.maximum(out_a, 1e-6)[..., None], 0)
    return out_rgb, out_a


# ----------------------------------------------------------------------------
# 1. load + silhouette (no sticker outline) at 512
# ----------------------------------------------------------------------------
def load_sources():
    rgb = np.asarray(Image.open(SRC / "pot-rgb-512.png").convert("RGB"), np.float64)
    mask = np.asarray(Image.open(SRC / "pot-mask-512.png").convert("L"), np.float64) / 255
    return rgb, mask


def silhouette512(rgb):
    """Coloured pot silhouette: everything not connected to the outside through near-white."""
    W = 255.0
    dist = np.sqrt(((W - rgb) ** 2).sum(2))
    nw = dist < 12
    lab, _ = ndi.label(nw)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border))
    fg = ~bg
    pure = ndi.binary_erosion(fg, iterations=2)
    d, (iy, ix) = ndi.distance_transform_edt(~pure, return_indices=True)
    F = rgb[iy, ix]
    num = ((W - rgb) * (W - F)).sum(2)
    den = ((W - F) ** 2).sum(2) + 1e-6
    alpha = np.clip(num / den, 0, 1)
    alpha[pure] = 1
    alpha[d > 4] = 0
    # decontaminated colour field, extended outwards
    col = rgb.copy()
    part = (alpha > 0.5) & (alpha < 0.97)
    col[part] = np.clip((rgb[part] - (1 - alpha[part, None]) * W) / alpha[part, None], 0, 255)
    good = alpha > 0.5
    _, (iy, ix) = ndi.distance_transform_edt(~good, return_indices=True)
    col = col[iy, ix]
    return alpha, col, fg


# ----------------------------------------------------------------------------
# 2. measurements on the raster (continuous coords)
# ----------------------------------------------------------------------------
def measure(rgb, alpha):
    L = rgb @ np.array([0.2126, 0.7152, 0.0722])
    Ls = ndi.gaussian_filter1d(L, 0.7, axis=1)
    # --- joint line (dark line at the skirt bottom), detected column by column
    gcx, ga, gcy, gb = 260, 183, 198, 81
    pts = []
    for x in range(84, 440):
        t = (x - gcx) / ga
        yg = gcy + gb * math.sqrt(max(0.0, 1 - t * t))
        ys = np.arange(int(yg) - 9, int(yg) + 10)
        det = Ls[ys, x] - 0.5 * (Ls[ys - 3, x] + Ls[ys + 3, x])
        i = int(np.argmin(det))
        off = 0.0
        if 0 < i < len(ys) - 1:
            d0, d1, d2 = det[i - 1], det[i], det[i + 1]
            den = d0 - 2 * d1 + d2
            off = 0.5 * (d0 - d2) / den if den != 0 else 0.0
        if det[i] < -8:
            pts.append((x + 0.5, ys[i] + off + 0.5))
    pts = np.array(pts)

    def res(p):
        cx, cy, a, b = p
        return (np.sqrt(((pts[:, 0] - cx) / a) ** 2 + ((pts[:, 1] - cy) / b) ** 2) - 1) * b

    J = optimize.least_squares(res, [260, 190, 187, 90]).x
    j_rms = float(np.sqrt(np.mean(res(J) ** 2)))

    # --- subpixel silhouette edges per row
    def left_edge(y):
        row = alpha[y]
        l = int(np.nonzero(row > 0.5)[0].min())
        return (l + 3) - row[l - 3:l + 3].sum()

    def right_edge(y):
        row = alpha[y]
        r = int(np.nonzero(row > 0.5)[0].max())
        return (r - 2) + row[r - 2:r + 4].sum()

    lid_left = float(np.mean([left_edge(y) for y in range(168, 187)]))
    body_l = float(np.mean([left_edge(y) for y in range(214, 225)]))
    body_r = float(np.mean([right_edge(y) for y in range(214, 225)]))

    # --- lid back silhouette (top ellipse), same centre x as the joint
    top = []
    for x in list(range(84, 199)) + list(range(322, 417)):
        col = alpha[:, x]
        y0 = int(np.nonzero(col > 0.5)[0].min())
        top.append((x + 0.5, (y0 + 3) - col[y0 - 3:y0 + 3].sum()))
    top = np.array(top)
    a_lid = J[0] - lid_left

    def res_t(p):
        cy, b = p
        return (np.sqrt(((top[:, 0] - J[0]) / a_lid) ** 2 + ((top[:, 1] - cy) / b) ** 2) - 1) * b

    T = optimize.least_squares(res_t, [169, 92]).x
    t_rms = float(np.sqrt(np.mean(res_t(T) ** 2)))

    # --- knob (dark cap + stem), filled
    # cap: darker than the lit lid; stem: much darker than the knob's cast shadow on the lid
    rows = np.arange(512)[:, None]
    knob_core = (alpha > 0.5) & (((L < 108) & (rows <= 125)) | ((L < 62) & (rows > 125)))
    lab, _ = ndi.label(knob_core)
    knob_core = lab == lab[100, 258]
    knob_core = ndi.binary_fill_holes(ndi.binary_closing(knob_core, iterations=2))
    # stem centre (rows of the stem) and the lowest point of the knob below it
    cs = []
    for y in range(134, 151):
        xs_ = np.nonzero(knob_core[y])[0]
        cs.append(0.5 * (xs_.min() + xs_.max() + 1))
    base_x = float(np.mean(cs))
    colk = knob_core[:, int(base_x)]
    bottom = int(np.nonzero(colk)[0].max())

    m = dict(
        joint=dict(cx=J[0], cy=J[1], a=J[2], b=J[3], rms=j_rms, n=len(pts)),
        top=dict(cx=J[0], cy=T[0], a=a_lid, b=T[1], rms=t_rms),
        lid_half=a_lid, lid_left=lid_left,
        body_left=body_l, body_right=body_r,
        knob_core=knob_core, knob_base=(base_x, bottom + 1.0),
        joint_pts=pts,
    )
    return m




# ----------------------------------------------------------------------------
# 3. sampling helpers on the 512 grid / window grid
# ----------------------------------------------------------------------------
def sample512(field, rx, ry, order=1):
    """sample a 512 field (HxWxC) at raster continuous coords (pixel centre = i+0.5)"""
    coords = [np.asarray(ry, float) - 0.5, np.asarray(rx, float) - 0.5]
    if field.ndim == 2:
        return ndi.map_coordinates(field, coords, order=order, mode="nearest")
    return np.stack([ndi.map_coordinates(field[..., c], coords, order=order, mode="nearest")
                     for c in range(field.shape[2])], -1)


def samplewin(field, rx, ry, order=1):
    """sample a window field at raster continuous coords"""
    j = np.asarray(rx, float) * SC2 + OX2 - WX0 - 0.5
    i = np.asarray(ry, float) * SC2 + OY2 - WY0 - 0.5
    if field.ndim == 2:
        return ndi.map_coordinates(field, [i, j], order=order, mode="nearest")
    return np.stack([ndi.map_coordinates(field[..., c], [i, j], order=order, mode="nearest")
                     for c in range(field.shape[2])], -1)


def num_normal(sd):
    gy, gx = np.gradient(sd)
    g = np.hypot(gx, gy) + 1e-9
    return gx / g, gy / g


def polygon_sd(poly, x, y):
    """signed distance (raster px, <0 inside) of points to a polygon (shapely)."""
    import shapely
    P = shapely.Polygon(poly)
    pts = shapely.points(np.asarray(x).ravel(), np.asarray(y).ravel())
    d = shapely.distance(P.exterior, pts)
    inside = shapely.contains_xy(P, np.asarray(x).ravel(), np.asarray(y).ravel())
    return np.where(inside, -d, d).reshape(np.shape(x))


# ----------------------------------------------------------------------------
# 4. look development: palette (spec 4.2) and shading functions
# ----------------------------------------------------------------------------
PAL = dict(
    lid="#B1BAC1", lid_rim="#C7CED4", body="#66747D", body_sh="#44525B",
    knob="#57646D", knob_fl="#2F3A3E", handle="#946A48", handle_sh="#643E23",
    floor="#1C2327", wall="#33404A", under_a="#8F99A0", under_b="#6F7A82", joint="#2B363C",
)
P = {k: hexrgb(v) for k, v in PAL.items()}


class Geo:
    pass


def ring_colour(g, x, y):
    """Top of the pot wall (rim lip): rounded inner edge, flat lit top, outer highlight, roll-off."""
    xn = np.clip((x - g.cxr) / g.a_o, -1.2, 1.2)
    rho = ell_rho(g.cxr, g.cyr, g.a_o, g.b_o, x, y)
    u = np.clip((rho - g.s_i) / (1 - g.s_i), 0, 1)
    th = np.arctan2((x - g.cxr) / g.a_o, (y - g.cyr) / g.b_o)  # 0 front, +pi/2 right, pi back
    top_l = np.array([160.0, 170, 177])
    top_r = np.array([117.0, 129, 137])
    base = lerp(top_l, top_r, smooth(-1.05, 1.05, xn))
    # inner roll: dark where it faces away from the key light, lit on the back-right
    lit_in = np.clip(np.cos(th - np.radians(140)), 0, 1) ** 1.5
    inner = base * (0.50 + 0.38 * lit_in)[..., None]
    c = lerp(inner, base, smooth(0.0, 0.36, u))
    # outer edge highlight (front-left catches the key light)
    lit_out = 0.30 + 0.70 * np.clip(np.cos(th - np.radians(-55)), 0, 1)
    bump = smooth(0.52, 0.74, u) * (1 - smooth(0.84, 0.97, u))
    c = c + np.array([30.0, 31, 31]) * (lit_out * bump)[..., None]
    # roll-off towards the outer wall
    c = c * lerp(1.0, 0.80, smooth(0.86, 1.0, u))[..., None]
    return c


def interior_colour(g, x, y):
    """Inside of the pot: back inner wall (#33404A family) + floor (#1C2327), cold state."""
    xi = (x - g.cxr) / g.a_i
    y_back = ell_y(g.cxr, g.cyr, g.a_i, g.b_i, x, front=False)
    y_front = ell_y(g.cxr, g.cyr, g.a_i, g.b_i, x, front=True)
    # floor ellipse (wall/floor junction)
    fcy = g.cyr + g.depth
    rho_f = ell_rho(g.cxr, fcy, g.a_f, g.b_f, x, y)
    y_fback = np.where(np.abs(x - g.cxr) < g.a_f,
                       ell_y(g.cxr, fcy, g.a_f, g.b_f, x, front=False), y_front)
    y_fback = np.minimum(y_fback, y_front)
    v = np.clip((y - y_back) / np.maximum(y_fback - y_back, 1e-3), 0, 1)
    wall_top = np.array([70.0, 84, 95])
    wall_mid = P["wall"]
    wall_low = np.array([33.0, 42, 48])
    wall = np.where((v < 0.35)[..., None],
                    lerp(wall_top, wall_mid, smooth(0, 0.35, v)),
                    lerp(wall_mid, wall_low, smooth(0.35, 1.0, v)))
    # inner right wall faces the key light (top-left): brighter on the right, darker left
    side = 1.0 + 0.20 * np.clip(xi, -1, 1) - 0.06 * np.clip(xi, -1, 1) ** 2
    wall = wall * side[..., None]
    # shadow cast by the front wall (light from the front-left): soft band rising to the right
    y_sh = ell_y(g.cxr + 0.22 * g.a_i, g.cyr - 0.98 * g.b_i, g.a_i, g.b_i, x, front=True)
    inside_sh = np.abs(x - (g.cxr + 0.22 * g.a_i)) < g.a_i
    sh = np.where(inside_sh, smooth(-6.0, 10.0, y - y_sh), 1.0)
    wall = wall * (1 - 0.30 * sh)[..., None]
    # floor
    floor = P["floor"] * (1.0 + 0.10 * np.clip(xi, -1, 1))[..., None]
    floor = floor * (1 - 0.18 * sh)[..., None]
    # AO at the wall/floor junction
    dj = (rho_f - 1) * g.b_f  # ~ distance (vertical units) from the floor rim
    ao = np.exp(-np.abs(dj) / 2.2)
    on_floor = smooth(0.5, -0.5, dj)  # 1 inside floor
    c = lerp(wall, floor, on_floor) * (1 - 0.28 * ao)[..., None]
    # thin cool bounce right under the inner lip at the back (separates lip and wall)
    lip_dist = y - y_back
    c = c * (1 - 0.18 * np.exp(-np.maximum(lip_dist, 0) / 2.0))[..., None]
    return c


# ----------------------------------------------------------------------------
# 5. build
# ----------------------------------------------------------------------------
def build():
    OUT.mkdir(parents=True, exist_ok=True)
    dbg = OUT / "debug"
    if DEBUG:
        dbg.mkdir(exist_ok=True)

    rgb, _mask = load_sources()
    a512, c512, _fg = silhouette512(rgb)
    m = measure(rgb, a512)
    J, T = m["joint"], m["top"]

    g = Geo()
    g.cxj, g.cyj, g.aj, g.bj = J["cx"], J["cy"], J["a"], J["b"]
    g.kr = g.bj / g.aj
    g.a_lid = m["lid_half"]
    g.cyt, g.bt = T["cy"], T["b"]
    g.cut = (g.cxj, g.cyj, g.aj + 0.85, g.bj + 0.85)
    # rim: outer edge = body silhouette at the top, in the plane of the lid/body joint
    g.cxr = 0.5 * (m["body_left"] + m["body_right"])
    g.a_o = 0.5 * (m["body_right"] - m["body_left"])
    g.b_o = g.a_o * g.kr
    g.cyr = g.cyj
    g.wall = 10.0
    g.a_i = g.a_o - g.wall
    g.b_i = g.a_i * g.kr
    g.s_i = g.a_i / g.a_o
    g.a_f, g.b_f = g.a_i * 0.965, g.b_i * 0.965
    g.depth = g.b_i + g.b_f - 0.36 * g.b_i  # projected depth: a modest floor crescent stays visible

    # ---------------- original, upscaled -------------------------------------
    C0 = unsharp(up(c512))
    A0 = crisp_alpha(up(a512))

    # ---------------- analytic masks (window) ---------------------------------
    sd_cutE = ell_sd(*g.cut)
    sd_cut = np.minimum(sd_cutE, RY - g.cyj)              # inside = above the joint cut
    M_cut = soft_inside(sd_cut)
    sd_topE = np.minimum(ell_sd(g.cxj, g.cyt, g.a_lid, g.bt), g.cyt - RY)
    sd_out = np.maximum(np.abs(RX - g.cxj) - g.a_lid, sd_topE)  # analytic lid outline (no bottom)
    M_out = soft_inside(sd_out)
    # where to trust the analytic outline instead of the raster silhouette:
    #   right side (handle behind the lid) and behind the knob (lid back edge hidden)
    w_r = smooth(396, 404, RX)
    w_k = smooth(186, 194, RX) * (1 - smooth(326, 334, RX)) * (1 - smooth(104, 112, RY))
    w_an = np.maximum(w_r, w_k)
    S_lid = A0 * (1 - w_an) + M_out * w_an
    LR = M_cut * M_out                                       # analytic lid region
    # for removing the lid from the body layer: same region grown 1.6 px outwards on its outline
    # (never at the cut) so no sliver of the lid's antialiased silhouette survives in pot_front
    LRg = M_cut * soft_inside(sd_out - 1.6)

    # ---------------- knob ------------------------------------------------------
    core = m["knob_core"]
    sdk512 = np.where(core, -(ndi.distance_transform_edt(core) - 0.5),
                      ndi.distance_transform_edt(~core) - 0.5)
    sdk512 = ndi.gaussian_filter(sdk512, 0.8)
    sdk = up(sdk512)
    KNOB_GROW = 2.2       # include the thin light halo that hugs the knob
    knob_a = soft_inside(sdk - KNOB_GROW) * A0
    knob_rgb = C0.copy()

    # ---------------- lid colour (512 work, then upscale) ----------------------
    lid512 = c512.copy()
    yy, xx = np.mgrid[0:512, 0:512] + 0.5
    # (a) fill under the knob with dome shading (membrane fill from the surrounding lid)
    K_fill = sdk512 < KNOB_GROW + 0.45
    box = np.zeros((512, 512), bool)
    box[38:182, 170:350] = True
    known = box & ~K_fill & (a512 > 0.97)
    unknown = box & ~known
    lid512 = harmonic_fill(lid512, known, unknown)
    # (b) clean colour fringes on the lid's right edge (JPEG chroma vs the handle)
    sd_o512 = np.maximum(np.abs(xx - g.cxj) - g.a_lid,
                         np.minimum(ell_sd(g.cxj, g.cyt, g.a_lid, g.bt, xx, yy), g.cyt - yy))
    nx, ny = num_normal(sd_o512)
    band = (xx > 400) & (yy > 112) & (yy < 212) & (sd_o512 > -4.0) & (sd_o512 < 3.0)
    dep = 4.0
    src_x = xx - nx * (sd_o512 + dep)
    src_y = yy - ny * (sd_o512 + dep)
    fixed = sample512(c512, src_x[band], src_y[band])
    lid512[band] = fixed
    # (c) extend the dark joint line across the cut so the lid's bottom edge is clean
    sd_c512 = np.minimum(ell_sd(*g.cut, xx, yy), yy - g.cyj)
    nx, ny = num_normal(sd_c512)
    band = (sd_c512 > -0.7) & (sd_c512 < 3.0) & (yy > g.cyj)
    src_x = xx - nx * (sd_c512 + 0.7)
    src_y = yy - ny * (sd_c512 + 0.7)
    lid512[band] = sample512(lid512, src_x[band], src_y[band])
    lid_rgb = unsharp(up(lid512))
    lid_a = M_cut * S_lid

    # ---------------- right handle: hidden root (behind the lid) ---------------
    # far arm silhouette continues up-left under the lid and tucks behind the back rim
    hpoly = [(459, 125.6), (447, 121.3), (440, 119.5), (430, 117.7), (421, 116.8), (416.5, 117.4),
             (412.5, 119.6), (409.5, 123.4), (407.4, 128.6), (406.0, 135.0), (404.5, 146), (400, 160),
             (440, 216), (459, 216)]
    bx = (RX > 372) & (RX < 462) & (RY > 108) & (RY < 220)
    sd_h = np.full(RX.shape, 50.0)
    sd_h[bx] = polygon_sd(hpoly, RX[bx], RY[bx])
    sd_ro = ell_sd(g.cxr, g.cyr, g.a_o, g.b_o)              # outer rim, <0 inside
    side_ok = np.maximum(smooth(g.cxr + g.a_o - 0.6, g.cxr + g.a_o + 0.6, RX),
                         1 - smooth(g.cyr - 0.6, g.cyr + 0.6, RY))
    bottom_ok = 1 - smooth(205.8, 207.0, RY)
    H_poly = soft_inside(sd_h)
    H_front = H_poly * soft_inside(-sd_ro) * side_ok * bottom_ok      # visible once the lid lifts
    H_back = H_poly * soft_inside(sd_ro - 2.5) * bottom_ok            # root strip under the back rim
    # colour: sample the clean visible handle (x >= 455) along the top-face direction
    slope = np.full(RX.shape, 0.30)
    sx = 456.5
    sy = RY + slope * (sx - RX)
    hsrc = np.zeros(RX.shape + (3,))
    hsrc[bx] = (samplewin(C0, np.full(int(bx.sum()), sx), sy[bx]) +
                samplewin(C0, np.full(int(bx.sum()), sx + 1.2), sy[bx] + 0.0) +
                samplewin(C0, np.full(int(bx.sum()), sx + 2.4), sy[bx])) / 3.0
    hsrc = ndi.gaussian_filter(hsrc, (2.0, 0.0, 0))
    d_rim = np.maximum(sd_ro, 0)
    shade = (1 - 0.38 * np.exp(-d_rim / 3.0))                       # AO where it tucks behind
    shade *= (1 - 0.30 * np.exp(-np.maximum(RX - (g.cxr + g.a_o), 0) / 2.0) * (RY > g.cyr))
    edge = (1 - 0.42 * np.exp(-np.maximum(-sd_h, 0) / 0.55))       # dark rim like the original
    H_rgb = hsrc * (shade * edge)[..., None]
    # the original handle carries a dark/red seam where the lid edge sat: replace it
    seam = smooth(445.5, 447.0, RX) * (1 - smooth(453.5, 456.0, RX)) * \
        smooth(116.0, 118.5, RY) * (1 - smooth(205.5, 207.5, RY))

    # ---------------- pot_back -------------------------------------------------
    ring = ring_colour(g, RX, RY)
    inner_cov = soft_inside(ell_sd(g.cxr, g.cyr, g.a_i, g.b_i))
    inter = interior_colour(g, RX, RY)
    back_rgb = lerp(ring, inter, inner_cov)
    back_a = soft_inside(sd_ro)
    back_rgb, back_a = over(H_rgb, H_back, back_rgb, back_a)

    # ---------------- pot_front ------------------------------------------------
    # body wall above the cut: extend the wall colour (just below the joint) upwards
    t = np.clip((RX - g.cut[0]) / g.cut[2], -1, 1)
    y_cut = g.cut[1] + g.cut[3] * np.sqrt(1 - t * t)
    wall_ext = samplewin(C0, RX, y_cut + 1.3)
    d_below = np.maximum(sd_ro, 0)                                     # distance outside the rim
    wall_ext = wall_ext * (1 - 0.20 * np.exp(-d_below / 1.6))[..., None]
    ring_front = ring
    rep_rgb = lerp(wall_ext, ring_front, soft_inside(sd_ro))
    body_sides = soft_inside(np.abs(RX - g.cxr) - g.a_o)
    below_mid = smooth(g.cyr - 1.5, g.cyr + 1.5, RY)
    outside_inner = 1 - inner_cov
    rep_a = body_sides * below_mid * outside_inner
    rep_rgb, rep_a = over(rep_rgb, rep_a, H_rgb, H_front)
    # original (visible at rest) outside the lid region, repaint under it
    orig_rgb = lerp(C0, H_rgb, seam * (H_poly > 0.5))
    front_pm = orig_rgb * (A0 * (1 - LRg))[..., None] + rep_rgb * (rep_a * LRg)[..., None]
    front_a = A0 * (1 - LRg) + rep_a * LRg
    front_rgb = front_pm / np.maximum(front_a, 1e-6)[..., None]

    # ---------------- lid underside --------------------------------------------
    ua, ub = 1.02 * g.a_o, 1.02 * g.b_o
    sd_u = ell_sd(g.cxr, g.cyr, ua, ub)
    xn = (RX - g.cxr) / ua
    yn = (RY - g.cyr) / ub
    tt = np.clip(0.5 + 0.38 * xn + 0.42 * yn, 0, 1)
    under = lerp(P["under_a"], P["under_b"], smooth(0, 1, tt))
    rho_u = ell_rho(g.cxr, g.cyr, ua, ub)
    under = under * (1 - 0.16 * np.exp(-((rho_u - 0.91) / 0.035) ** 2))[..., None]  # skirt corner AO
    under = under + 14.0 * smooth(0.955, 0.99, rho_u)[..., None]  # lit skirt edge
    lid_erode = ndi.minimum_filter(lid_a, size=5)
    under_a = soft_inside(sd_u) * lid_erode

    # ---------------- write layers ----------------------------------------------
    layers = {}
    layers["pot_back"] = (back_rgb, back_a)
    layers["pot_front"] = (front_rgb, front_a)
    layers["pot_lid"] = (lid_rgb, lid_a)
    layers["pot_knob"] = (knob_rgb, knob_a)
    layers["pot_lid_under"] = (under, under_a)
    for k, (c, a) in layers.items():
        save_rgba(OUT / f"{k}.png", c, a)
    return g, m, layers, (C0, A0)




# ----------------------------------------------------------------------------
# 6. previews, parity, manifest
# ----------------------------------------------------------------------------
WORK = OUT / "pot_work"


def to_full(rgb, a):
    """window straight (rgb 0..255, a 0..1) -> full canvas float premultiplied RGBA"""
    full = np.zeros((CH, CW, 4))
    full[WY0:WY0 + WH, WX0:WX0 + WW, :3] = rgb * a[..., None]
    full[WY0:WY0 + WH, WX0:WX0 + WW, 3] = a
    return full


def transform_pm(pm, angle_deg, pivot, shift):
    """Rotate a premultiplied full-canvas RGBA by angle (CSS sense: +cw) about pivot then shift.
    pivot/shift in 2x canvas px (continuous)."""
    th = math.radians(angle_deg)
    c, s = math.cos(th), math.sin(th)
    px, py = pivot
    tx, ty = shift
    # output q -> input p = pivot + R^-1 (q - shift - pivot);  R^-1 = rot(-th)
    a, b = c, s
    d, e = -s, c
    cx_ = px - (a * (px + tx) + b * (py + ty))
    cy_ = py - (d * (px + tx) + e * (py + ty))
    out = np.zeros_like(pm)
    for k in range(4):
        im = Image.fromarray(pm[..., k].astype(np.float32), mode="F")
        out[..., k] = np.asarray(im.transform((CW, CH), Image.AFFINE, (a, b, cx_, d, e, cy_),
                                              resample=Image.BICUBIC), np.float64)
    out[..., 3] = np.clip(out[..., 3], 0, 1)
    out[..., :3] = np.clip(out[..., :3], 0, 255 * out[..., 3:4])
    return out


def pm_over(dst, src):
    return src + dst * (1 - src[..., 3:4])


def outline_from(alpha_union, radius):
    """white sticker outline: round dilation of the union alpha (radius in 2x px)."""
    binm = alpha_union >= 0.5
    ys, xs = np.nonzero(binm)
    y0, y1 = max(ys.min() - radius - 4, 0), min(ys.max() + radius + 5, CH)
    x0, x1 = max(xs.min() - radius - 4, 0), min(xs.max() + radius + 5, CW)
    sub = binm[y0:y1, x0:x1]
    d = ndi.distance_transform_edt(~sub)
    # subpixel: shift by the coverage of the nearest inside pixel
    o = np.clip(radius + 0.5 - d, 0, 1)
    o = ndi.gaussian_filter(o, 0.55)
    out = np.zeros_like(alpha_union)
    out[y0:y1, x0:x1] = o
    return np.maximum(out, alpha_union)


def checker(h, w, sq=24):
    yy, xx = np.mgrid[0:h, 0:w]
    m = ((yy // sq + xx // sq) % 2).astype(float)
    c = lerp(np.array([236.0, 236, 236]), np.array([206.0, 206, 206]), m)
    return c


def stamp_background():
    """Paper + vignette of the stamp (no pot, no printed flames), rendered by Chromium @2x."""
    WORK.mkdir(parents=True, exist_ok=True)
    svg = (SRC / "stamp-source.svg").read_text(encoding="utf-8")
    import re
    defs = re.search(r"<linearGradient id=\"D\S*27\".*?</linearGradient>", svg, re.S).group(0)
    paths = re.findall(r"<path class=\"cls-[34]\" d=\"[^\"]+\"/>", svg)
    rect = re.search(r"<rect class=\"cls-7\"[^>]*/>", svg).group(0)
    gid = re.search(r"id=\"(D\S*27)\"", defs).group(1)
    body = "\n".join(paths).replace('class="cls-4"', 'fill="#4d4d4d"').replace('class="cls-3"', 'fill="#ffffff"')
    rect = rect.replace('class="cls-7"', f'fill="url(#{gid})"')
    doc = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CANVAS[0]} {CANVAS[1]}">
<defs>{defs}</defs>
<g transform="translate(74.55 99) scale(1.8)">{body}{rect}</g></svg>"""
    p_svg = WORK / "bg_stamp.svg"
    p_png = WORK / "bg_stamp_2x.png"
    p_svg.write_text(doc, encoding="utf-8")
    subprocess.run(["node", str(ROOT / "tools" / "chrome_shot.cjs"), str(p_svg), str(p_png),
                    str(CW), str(CH)], check=True, timeout=120)
    bg = np.asarray(Image.open(p_png).convert("RGBA"), np.float64)
    return bg


def flatten(pm, bg_rgb):
    return pm[..., :3] + bg_rgb * (1 - pm[..., 3:4])


def down2(img):
    return np.asarray(Image.fromarray(np.clip(np.round(img), 0, 255).astype(np.uint8))
                      .resize((img.shape[1] // 2, img.shape[0] // 2), Image.LANCZOS))


def finish(g, m, layers, ref):
    C0, A0 = ref
    WORK.mkdir(parents=True, exist_ok=True)
    pm = {k: to_full(*v) for k, v in layers.items()}

    # ---------- rest composite + parity ----------
    order = ["pot_back", "pot_front", "pot_lid", "pot_knob"]
    rest = np.zeros((CH, CW, 4))
    for k in order:
        rest = pm_over(rest, pm[k])
    ra = rest[..., 3]
    rrgb = np.where(ra[..., None] > 1e-6, rest[..., :3] / np.maximum(ra, 1e-6)[..., None], 0)
    out = np.zeros((CH, CW, 4), np.uint8)
    out[..., :3] = np.clip(np.round(rrgb), 0, 255)
    out[..., 3] = np.clip(np.round(ra * 255), 0, 255)
    out[out[..., 3] == 0, :3] = 0
    Image.fromarray(out, "RGBA").save(OUT / "pot_rest_composite.png", optimize=True)

    ref_full = to_full(C0, A0)
    wa = ref_full[..., 3]
    inside = wa >= 0.999
    ref_rgb = np.where(wa[..., None] > 1e-6, ref_full[..., :3] / np.maximum(wa, 1e-6)[..., None], 0)
    d_in = np.abs(rrgb - ref_rgb)[inside].mean(1)
    white = np.full(3, 255.0)
    comp_w = flatten(rest, white)
    ref_w = flatten(ref_full, white)
    sil = (wa > 0.004) | (ra > 0.004)
    d_w = np.abs(comp_w - ref_w)[sil].mean(1)
    d_a = np.abs(ra - wa)[sil]
    # with the lid underside in its rest place too (must stay invisible)
    rest_u = np.zeros((CH, CW, 4))
    for k in ["pot_back", "pot_front", "pot_lid_under", "pot_lid", "pot_knob"]:
        rest_u = pm_over(rest_u, pm[k])
    d_u = np.abs(rest_u - rest).max()
    parity = dict(
        reference="original pot raster, sticker outline removed, same 2x upscale (LANCZOS x2.88 + unsharp)",
        mean_abs_rgb_inside=float(d_in.mean()), p99_abs_rgb_inside=float(np.percentile(d_in, 99)),
        max_abs_rgb_inside=float(d_in.max()), pixels_inside=int(inside.sum()),
        pct_inside_over_8=float((d_in > 8).mean() * 100),
        mean_abs_rgb_over_white_silhouette=float(d_w.mean()),
        mean_abs_alpha_silhouette_x255=float(d_a.mean() * 255),
        max_abs_alpha_x255=float(d_a.max() * 255),
        lid_under_at_rest_max_change_x255=float(d_u),
    )
    (OUT / "pot_parity.json").write_text(json.dumps(parity, indent=2))
    if DEBUG:
        heat = np.zeros((CH, CW))
        heat[inside] = d_in
        hv = np.clip(heat * 255 / 24, 0, 255).astype(np.uint8)
        Image.fromarray(hv[WY0:WY0 + WH, WX0:WX0 + WW]).save(WORK / "parity_heat.png")

    # ---------- open pose (spec 5, f12) ----------
    Hx, Hy = r2c(g.cxj - g.aj, g.cyj)
    H2 = (Hx * 2, Hy * 2)
    ang, lift = -36.0, -33.6
    slide = 7.0  # underside slides this many px (local, @1x) under the skirt
    lid_grp = np.zeros((CH, CW, 4))
    under_shifted = np.zeros_like(pm["pot_lid_under"])
    s2 = int(round(slide * 2))
    under_shifted[s2:] = pm["pot_lid_under"][:-s2]
    lid_grp = pm_over(lid_grp, under_shifted)
    lid_grp = pm_over(lid_grp, pm["pot_lid"])
    lid_grp = pm_over(lid_grp, pm["pot_knob"])
    lid_open = transform_pm(lid_grp, ang, H2, (0.0, lift * 2))
    open_pm = np.zeros((CH, CW, 4))
    for k in ["pot_back", "pot_front"]:
        open_pm = pm_over(open_pm, pm[k])
    open_pm = pm_over(open_pm, lid_open)

    bg = stamp_background()
    bg_pm = bg[..., :3] * (bg[..., 3:4] / 255)
    chk = checker(CH, CW)

    def sheet(scene_pm, name):
        ol = outline_from(scene_pm[..., 3], 60)
        ol_pm = np.zeros((CH, CW, 4))
        ol_pm[..., :3] = 255 * ol[..., None]
        ol_pm[..., 3] = ol
        withol = pm_over(ol_pm, scene_pm)
        a = flatten(withol, bg_pm / np.maximum(1, 1))  # bg already premultiplied over black
        # stamp bg has transparent margins: put it over a light neutral first
        base = flatten(np.concatenate([bg_pm, bg[..., 3:4] / 255], -1), np.full(3, 242.0))
        a = flatten(withol, base)
        b = flatten(withol, chk)
        left, right = down2(a), down2(b)
        img = np.concatenate([left, right], 1)
        Image.fromarray(img).save(OUT / name, optimize=True)
        return a, b

    a_closed, _ = sheet(rest, "preview_closed.png")
    a_open, b_open = sheet(open_pm, "preview_open.png")
    if DEBUG:
        for nm, im in (("closed", a_closed), ("open", a_open), ("open_chk", b_open)):
            crop = im[700:2300, 300:1850]
            Image.fromarray(np.clip(np.round(crop), 0, 255).astype(np.uint8)).save(WORK / f"zoom_{nm}.png")

    # ---------- manifest ----------
    def c1(rx, ry):
        x, y = r2c(rx, ry)
        return [round(float(x), 2), round(float(y), 2)]

    def bbox(a, full=False):
        ys, xs = np.nonzero(a > 1 / 255)
        ox, oy = (0, 0) if full else (WX0, WY0)
        return [round((xs.min() + ox) / 2, 1), round((ys.min() + oy) / 2, 1),
                round((xs.max() + 1 + ox) / 2, 1), round((ys.max() + 1 + oy) / 2, 1)]

    lid_a = layers["pot_lid"][1]
    ys, xs = np.nonzero(lid_a > 0.5)
    lc = [round(float((xs.mean() + 0.5 + WX0) / 2), 2), round(float((ys.mean() + 0.5 + WY0) / 2), 2)]
    sil = ra
    ys, xs = np.nonzero(sil > 0.5)
    yb = ys.max()
    bx_ = xs[ys >= yb - 3].mean() - WX0  # (full canvas array, keep the window convention below)
    th = np.linspace(-math.pi / 2, math.pi / 2, 41)
    lip = [c1(g.cxr + g.a_o * math.sin(t), g.cyr + g.b_o * math.cos(t)) for t in th]
    lip_in = [c1(g.cxr + g.a_i * math.sin(t), g.cyr + g.b_i * math.cos(t)) for t in th]
    cut_arc = [c1(g.cut[0] + g.cut[2] * math.sin(t), g.cut[1] + g.cut[3] * math.cos(t)) for t in th]
    rim_c = c1(g.cxr, g.cyr)
    man = dict(
        canvas=[CANVAS[0], CANVAS[1]], density=DEN,
        note="all coordinates canvas @1x px; PNGs are 2160x2700, display at 1080x1350, zero offsets",
        layers=dict(back="pot_back.png", front="pot_front.png", lid="pot_lid.png", knob="pot_knob.png",
                    lid_under="pot_lid_under.png", rest_composite="pot_rest_composite.png"),
        z_order_bottom_to_top=["pot_back", "(flame)", "pot_front", "pot_lid_under", "pot_lid", "pot_knob"],
        rim_ellipse=dict(cx=rim_c[0], cy=rim_c[1], rx=round(g.a_o * SC, 2), ry=round(g.b_o * SC, 2)),
        rim_inner_ellipse=dict(cx=rim_c[0], cy=rim_c[1], rx=round(g.a_i * SC, 2), ry=round(g.b_i * SC, 2)),
        lid_under_ellipse=dict(cx=rim_c[0], cy=rim_c[1], rx=round(1.02 * g.a_o * SC, 2),
                               ry=round(1.02 * g.b_o * SC, 2)),
        lid_cut_ellipse=dict(cx=c1(g.cut[0], g.cut[1])[0], cy=c1(g.cut[0], g.cut[1])[1],
                             rx=round(g.cut[2] * SC, 2), ry=round(g.cut[3] * SC, 2)),
        hinge_H=[round(Hx, 2), round(Hy, 2)],
        lid_center_C=lc,
        knob_base=c1(*m["knob_base"]),
        squash_anchor_B=[round(float((bx_ + 0.5 + WX0) / 2), 2), round(float((yb + 1) / 2), 2)],
        emission_E=[627.0, 647.0],
        pot_bbox_no_outline=bbox(ra, full=True),
        lid_bbox=bbox(lid_a),
        knob_bbox=bbox(layers["pot_knob"][1]),
        front_bbox=bbox(layers["pot_front"][1]),
        back_bbox=bbox(layers["pot_back"][1]),
        front_lip_polyline=lip,
        front_lip_inner_polyline=lip_in,
        lid_bottom_polyline=cut_arc,
        open_preview=dict(lid_rotate_deg=ang, lid_translate_y=lift, lid_under_slide_y_local=slide,
                          outline_px=30),
        fits=dict(joint_ellipse_rms_px512=round(J_rms(m), 3), lid_top_rms_px512=round(m["top"]["rms"], 3)),
        parity=parity,
    )
    (OUT / "pot.json").write_text(json.dumps(man, indent=2))
    return man


def J_rms(m):
    return float(m["joint"]["rms"])


if __name__ == "__main__":
    g, m, layers, ref = build()
    man = finish(g, m, layers, ref)
    print(json.dumps({k: man[k] for k in ("rim_ellipse", "hinge_H", "lid_center_C", "knob_base",
                                          "squash_anchor_B", "pot_bbox_no_outline", "parity")}, indent=1))
