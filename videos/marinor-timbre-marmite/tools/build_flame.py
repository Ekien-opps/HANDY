#!/usr/bin/env python3
"""
Marin'Or Ivoire - timbre "Marmite chaude" - FLAME geometry (option B, HyperFrames).

Source of truth: SPEC_timbre-marmite.md  §3 (E, axis, sizes), §4.4, §5 (flame column), §6.2, §6.3, §7.

Flat, graphic, faceted flame in the angular language of the two printed flames of the stamp:
straight edges only, sharp tips (26-30 deg), 5 asymmetric tongues leaning outward
(central 1.00 H_fl, flanks 0.70 / 0.62, outer 0.40 / 0.35), base 240 px, H_fl 376 px.

Layers (geometry only; the composition adds FL_GLITTER and FL_GLOW):
  out  : linear gradient #FF6B31 (base) -> #FFA53A (tips), as on the printed flames
  mid  : out inset 18 px (mitre), #F9A825
  core : out inset 37 px (mitre), #FBD021
Inner layers are the exact shapely buffer(-d, mitre) of OUT, re-expressed on the same 15-vertex
template (vanished tongues collapse to zero-area spikes; tongues whose neck < 21.6 px are cut).

Flame-local frame: canvas px at 100 %, origin = base centre, +y down, flame grows towards -y.
Placement: translate(627 647) rotate(14) scale(sx sy)   (SVG transform, applied to the local points).

Outputs (assets/build/):
  flame.json              poses, framePlan f9..f28, baked frames, checks
  flame_poses.png         every pose, every layer, over dark and over #F6E8EA (no text)
  flame_inplace_f12.png   f12 at E (left: real z-order + glow + glitter, right: unoccluded) + guides
  flame_frames_strip.png  f9..f27 in place with the spec lid angles (context preview)
Usage:  python3 tools/build_flame.py [--no-previews]
"""
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from shapely.geometry import Polygon

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "assets" / "build"
TOOLS = ROOT / "tools"
SCRATCH_DEFAULT = Path("/tmp/claude-0/-home-user-HANDY/180e27e0-1c8f-56c9-a284-57d2bdc0b1f3/scratchpad")

# ------------------------------------------------------------------ spec constants
H = 376.0                       # H_fl at 100 %
HALF = 120.0                    # half of the 240 px base
E = np.array([627.0, 647.0])    # emission point
ROT = 14.0                      # axis, degrees clockwise (screen)
INSET = {"mid": 18.0, "core": 37.0}
MIN_BASE = 21.6                 # 12 u
SAFE = dict(x0=160.1, y0=184.6, x1=913.7, y1=1153.9)
GLOW = 24.0
TIP_TARGET_F12 = (732.0, 224.0)
COL = dict(out0="#FF6B31", out1="#FFA53A", mid="#F9A825", core="#FBD021")
# gradient in flame-local px (userSpaceOnUse inside the transformed group): dark at the base,
# light towards the upper right, i.e. along the lean, like the printed flames
GRAD = dict(x1=-70.0, y1=30.0, x2=95.0, y2=-385.0)

# skirt (hidden under pot_front): the outer edges of the outer tongues run on, straight, through the
# base corners down to KNEE_Y (a fan from the pot), then the sides drop vertically to skirtY
KNEE_Y = 90.0
KNEE_MAX_SLANT = 32.0           # deg, cap of the inward slope below the base line
SKIRT_Y = 200.0                 # default skirt bottom (local px, pre-scale)

NAMES = ["skirtBottomL", "skirtKneeL", "baseL", "tipOL", "notch1", "tipFL", "notch2", "tipC",
         "notch3", "tipFR", "notch4", "tipOR", "baseR", "skirtKneeR", "skirtBottomR"]
NV = len(NAMES)
TONGUES = {"OL": (2, 3, 4), "FL": (4, 5, 6), "C": (6, 7, 8), "FR": (8, 9, 10), "OR": (10, 11, 12)}
TIP_IDX = {k: v[1] for k, v in TONGUES.items()}

# ------------------------------------------------------------------ poses (drawn)
# tips: (x, height as fraction of H_fl) for OL, FL, C, FR, OR
# beta: lean of the flank / central tongues = direction (deg) of their axis going DOWN from the tip,
#       measured from +y towards +x (positive = tongue leans left).  Outer tongues: the outer edge
#       runs from the tip to the base corner, the inner edge is at the tip angle.
# ang : tip angles (deg), 26..30
POSES_DEF = {
    # burst (f9, shown squashed 35/60): compact, more erect, flanks and outer tongues still low
    "P1": dict(tips=[(-166, .30), (-106, .62), (2, 1.0), (110, .67), (176, .33)],
               beta=[None, 14, -1, -17, None], ang=[29, 28, 26, 28, 29]),
    # peak shape (f12, 116/95): fully spread; central tip on the axis -> lands on (732;224)
    "P2": dict(tips=[(-208, .35), (-130, .62), (0, 1.0), (148, .70), (220, .40)],
               beta=[None, 25, -4, -31, None], ang=[29, 28, 27, 28, 29]),
    # variation (f13, settling)
    "P3": dict(tips=[(-200, .37), (-124, .65), (-7, 1.0), (140, .68), (212, .38)],
               beta=[None, 22, 0, -28, None], ang=[29, 28, 27, 28, 30]),
    # float flicker, on twos (A is also the base pose of the extinction)
    "A": dict(tips=[(-202, .35), (-126, .63), (-3, 1.0), (142, .70), (214, .40)],
              beta=[None, 23, -2, -29, None], ang=[29, 28, 27, 28, 29]),
    "B": dict(tips=[(-212, .38), (-118, .60), (9, 1.02), (150, .72), (208, .37)],
              beta=[None, 26, -6, -32, None], ang=[30, 28, 27, 27, 29]),
    "C": dict(tips=[(-196, .33), (-134, .66), (-10, .99), (136, .67), (222, .42)],
              beta=[None, 21, 2, -26, None], ang=[28, 29, 27, 28, 30]),
}
SMEAR_STRETCH = 1.30            # central tongue length (from the base line) x 1.30
P0_SCALE = 0.08

# ------------------------------------------------------------------ framePlan (spec §5, §6.3)
LID = {9: (-28.2, -25.9), 10: (-33.7, -31.3), 11: (-35.7, -33.3), 12: (-36.0, -33.6), 13: (-35.0, -33.2),
       14: (-33.0, -32.4), 15: (-31.0, -30.5), 16: (-32.5, -32.5), 17: (-33.0, -33.5), 18: (-31.5, -31.0),
       19: (-32.0, -32.0), 20: (-34.0, -34.4), 21: (-35.0, -35.2), 22: (-34.3, -34.5), 23: (-32.1, -32.3),
       24: (-28.6, -28.7), 25: (-23.6, -23.7), 26: (-17.1, -17.3), 27: (-9.3, -9.3), 28: (0.0, 0.0)}


def extinction_sx(sy):
    k = sy / 100.0
    return round(100.0 * (0.7 + 0.3 * k), 3)


FRAME_PLAN = [
    dict(frame=9, pose="P1", scaleY=35.0, scaleX=60.0, note="birth, 1 frame after the lid pop"),
    dict(frame=10, pose="SMEAR", scaleY=80.0, scaleX=75.0, note="drawn smear: central tongue x1.30 -> ~104 % H_fl, tip y~268"),
    dict(frame=11, blend=dict(a="SMEAR", b="P2", t=0.85), scaleY=108.0, scaleX=88.0, note="smear residue 15 %"),
    dict(frame=12, pose="P2", scaleY=116.0, scaleX=95.0, note="PEAK, tip (732;224)"),
    dict(frame=13, pose="P3", scaleY=108.0, scaleX=102.0, note="stabilisation"),
    dict(frame=14, pose="A", scaleY=100.0, scaleX=100.0),
    dict(frame=15, pose="B", scaleY=103.0, scaleX=99.5, note="float, on twos"),
    dict(frame=16, pose="B", scaleY=103.0, scaleX=99.5),
    dict(frame=17, pose="A", scaleY=97.0, scaleX=101.5),
    dict(frame=18, pose="A", scaleY=97.0, scaleX=101.5),
    dict(frame=19, pose="C", scaleY=101.0, scaleX=100.0),
    dict(frame=20, pose="C", scaleY=104.0, scaleX=100.0, note="armement"),
    dict(frame=21, pose="A", scaleY=100.0, scaleX=100.0, note="base of the extinction expression"),
]
for _f, _p, _sy in ((22, "A", 98.5), (23, "B", 93.7), (24, "B", 86.0), (25, "C", 74.0), (26, "C", 58.5), (27, "A", 37.0)):
    FRAME_PLAN.append(dict(frame=_f, pose=_p, scaleY=_sy, scaleX=extinction_sx(_sy),
                           note="closing: sY slaved to the lid, sX = 0.7+0.3k"))
FRAME_PLAN.append(dict(frame=28, pose=None, scaleY=0.0, scaleX=100.0, visible=False,
                       note="FIRE_OUT = 1: flame 0, not rendered (also f29+)"))


# ------------------------------------------------------------------ geometry helpers
def dvec(beta):
    b = math.radians(beta)
    return np.array([math.sin(b), math.cos(b)])


def beta_of(v):
    return math.degrees(math.atan2(v[0], v[1]))


def isect(p, u, q, v):
    m = np.array([[u[0], -v[0]], [u[1], -v[1]]], float)
    det = m[0, 0] * m[1, 1] - m[0, 1] * m[1, 0]
    if abs(det) < 1e-10:
        return None
    s, _ = np.linalg.solve(m, q - p)
    return p + s * u


def signed_area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def dedupe(P, eps=1e-6):
    out = []
    for p in P:
        if not out or np.hypot(*(p - out[-1])) > eps:
            out.append(p)
    while len(out) > 1 and np.hypot(*(out[0] - out[-1])) <= eps:
        out.pop()
    return np.array(out)


def poly(P):
    D = dedupe(np.asarray(P, float))
    if len(D) < 3:
        return Polygon()
    return Polygon(D)


def skirt_pts(tip_l, tip_r, skirt_y):
    cap = math.tan(math.radians(KNEE_MAX_SLANT))
    sl = min(cap, max(0.0, (-HALF - tip_l[0]) / max(1e-6, -tip_l[1])))
    sr = min(cap, max(0.0, (tip_r[0] - HALF) / max(1e-6, -tip_r[1])))
    kl = np.array([-HALF + sl * KNEE_Y, KNEE_Y])
    kr = np.array([HALF - sr * KNEE_Y, KNEE_Y])
    return np.array([kl[0], skirt_y]), kl, kr, np.array([kr[0], skirt_y])


def build_out(pd, skirt_y=SKIRT_Y):
    tips = [np.array([x, -h * H], float) for x, h in pd["tips"]]
    ang = pd["ang"]
    BL, BR = np.array([-HALF, 0.0]), np.array([HALF, 0.0])
    edges = []
    b = beta_of(BL - tips[0])
    edges.append((b, b + ang[0]))
    for k in (1, 2, 3):
        b = pd["beta"][k]
        edges.append((b - ang[k] / 2.0, b + ang[k] / 2.0))
    b = beta_of(BR - tips[4])
    edges.append((b - ang[4], b))
    notches = []
    for k in range(4):
        n = isect(tips[k], dvec(edges[k][1]), tips[k + 1], dvec(edges[k + 1][0]))
        assert n is not None and n[1] > tips[k][1] and n[1] > tips[k + 1][1] and n[1] < 0, ("notch", k, n)
        notches.append(n)
    sbl, kl, kr, sbr = skirt_pts(tips[0], tips[4], skirt_y)
    pts = [sbl, kl, BL, tips[0], notches[0], tips[1], notches[1], tips[2], notches[2], tips[3],
           notches[3], tips[4], BR, kr, sbr]
    return np.array(pts, float)


def inset_wavefront(P, d, step=0.05, forced=()):
    """Mitre inward offset by wavefront propagation on the edge lines, keeping the template:
    returns (points[n], removed_edge_indices) or (None, all) if the layer vanishes."""
    P = np.asarray(P, float)
    n = len(P)
    U = np.roll(P, -1, axis=0) - P
    L = np.hypot(U[:, 0], U[:, 1])
    if (L < 1e-9).any():
        raise ValueError("zero-length edge in source polygon")
    U = U / L[:, None]
    sgn = 1.0 if signed_area(P) > 0 else -1.0
    N = np.stack([-U[:, 1], U[:, 0]], 1) * sgn
    active = [e for e in range(n) if e not in set(forced)]

    def starts(off, act):
        W = {}
        for j, e in enumerate(act):
            ep = act[j - 1]
            p1, p2 = P[ep] + off * N[ep], P[e] + off * N[e]
            X = isect(p1, U[ep], p2, U[e])
            W[e] = p2 if X is None else X
        return W

    off = 0.0
    while off < d - 1e-12:
        nxt = min(d, off + step)
        W = starts(nxt, active)
        m = len(active)
        lens = {e: float(np.dot(W[active[(j + 1) % m]] - W[e], U[e])) for j, e in enumerate(active)}
        bad = [e for e in active if lens[e] < 0]
        if bad:
            active.remove(min(bad, key=lambda e: lens[e]))
            if len(active) < 3:
                return None, list(range(n))
            continue
        off = nxt
    W = starts(d, active)
    aset = set(active)
    out = np.zeros_like(P)
    for i in range(n):
        j = i
        while j not in aset:
            j = (j + 1) % n
        out[i] = W[j]
    if signed_area(out) * sgn <= 0:
        return None, list(range(n))
    return out, sorted(set(range(n)) - aset)


def tongue_metrics(P, k):
    a, t, b = TONGUES[k]
    A, T, B = P[a], P[t], P[b]
    va, vb = A - T, B - T
    la, lb = np.hypot(*va), np.hypot(*vb)
    if la < 1e-6 or lb < 1e-6:
        return None
    w = va / la + vb / lb
    if np.hypot(*w) < 1e-9:
        return None
    w = w / np.hypot(*w)
    ta = math.acos(max(-1.0, min(1.0, float(np.dot(va, w) / la))))
    tb = math.acos(max(-1.0, min(1.0, float(np.dot(vb, w) / lb))))
    lmin = min(float(np.dot(va, w)), float(np.dot(vb, w)))
    if lmin <= 1e-6:
        return None
    neck = lmin * (math.tan(ta) + math.tan(tb))
    return dict(neck=neck, protrusion=lmin, tip_angle=math.degrees(ta + tb), axis=w)


def collapsed_layer(skirt_y, d):
    """Fully vanished inner layer: zero-area spine on the axis (keeps the skirt-bottom convention)."""
    P = np.zeros((NV, 2))
    P[0] = P[-1] = (0.0, skirt_y - d)
    P[1] = P[-2] = (0.0, KNEE_Y)
    return P


def _distinct(P, i, step):
    j = (i + step) % len(P)
    while np.hypot(*(P[j] - P[i])) < 1e-6 and j != i:
        j = (j + step) % len(P)
    return j


def _param(A, B, X):
    v = B - A
    return float(np.dot(X - A, v) / max(1e-12, np.dot(v, v)))


def spikes(P, max_angle=80.0):
    """Geometric tongue tips of a layer, independent of the template labels: every distinct convex
    vertex sharper than max_angle, with its neck (width at the level of its higher neighbour)."""
    sgn = 1.0 if signed_area(P) > 0 else -1.0
    out = []
    i = 1
    while i <= NV - 2:
        j = i
        while j + 1 <= NV - 2 and np.hypot(*(P[j + 1] - P[i])) < 1e-6:
            j += 1
        ip, jn = _distinct(P, i, -1), _distinct(P, j, +1)
        A, T, B = P[ip], P[i], P[jn]
        va, vb = A - T, B - T
        la, lb = np.hypot(*va), np.hypot(*vb)
        if la > 1e-6 and lb > 1e-6:
            cross = (T - A)[0] * (B - T)[1] - (T - A)[1] * (B - T)[0]
            ang = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(va, vb) / la / lb)))))
            if cross * sgn > 0 and ang < max_angle:
                w = va / la + vb / lb
                w = w / np.hypot(*w)
                ta = math.acos(max(-1.0, min(1.0, float(np.dot(va, w) / la))))
                tb = math.acos(max(-1.0, min(1.0, float(np.dot(vb, w) / lb))))
                lmin = min(float(np.dot(va, w)), float(np.dot(vb, w)))
                out.append(dict(i=i, j=j, angle=ang, neck=lmin * (math.tan(ta) + math.tan(tb))))
        i = j + 1
    return out


def drop_spike(P, sp):
    """Remove a too-thin spike from an inner layer while staying inside it and keeping every edge on
    an existing edge line (no new directions): a contiguous run of vertices around the spike is
    replaced by the intersection of the edge line entering the run and the edge line leaving it
    (the spike merges into a neighbour, or both neighbours meet in a V). The candidate keeping the
    most area without leaving a thin spike wins. Skirt-bottom vertices (0, NV-1) never move."""
    base = poly(P)
    best, best_area = None, -1.0
    for i in range(max(1, sp["i"] - 4), sp["i"] + 1):
        for j in range(sp["j"], min(NV - 2, sp["j"] + 4) + 1):
            ip, jn = _distinct(P, i, -1), _distinct(P, j, +1)
            if np.hypot(*(P[i] - P[ip])) < 1e-6 or np.hypot(*(P[jn] - P[j])) < 1e-6:
                continue
            X = isect(P[ip], P[i] - P[ip], P[j], P[jn] - P[j])
            if X is None or _param(P[ip], P[i], X) <= 0.0 or _param(P[j], P[jn], X) >= 1.0:
                continue
            Q = P.copy()
            Q[i:j + 1] = X
            q = poly(Q)
            if q.is_empty or not q.is_valid or q.difference(base).area > 0.5:
                continue
            if any(s2["neck"] < MIN_BASE and s2["i"] <= j and s2["j"] >= i for s2 in spikes(Q)):
                continue
            if q.area > best_area:
                best, best_area = Q, q.area
    if best is None:
        raise RuntimeError(f"cannot drop spike at vertex {sp['i']}")
    return best


def label_of(sp):
    for k, (a, t, b) in TONGUES.items():
        if sp["i"] <= t <= sp["j"]:
            return k
    return min(TONGUES, key=lambda k: abs(TONGUES[k][1] - sp["i"]))


def inner_layer(out, d, skirt_y):
    """Exact mitre inset (checked against shapely buffer), then spikes whose neck < MIN_BASE are
    dropped with drop_spike (subset, every edge stays parallel to an OUT edge)."""
    res, removed = inset_wavefront(out, d)
    ref = poly(out).buffer(-d, join_style="mitre", mitre_limit=10.0)
    info = dict(removed_edges=removed, cut=[], vanished=[])
    if res is None or ref.is_empty:
        info["vanished"] = list(TONGUES)
        return collapsed_layer(skirt_y, d), info, 0.0
    if ref.geom_type != "Polygon":
        raise RuntimeError(f"inset {d}: buffer split into {ref.geom_type}")
    err = poly(res).symmetric_difference(ref).area
    if err > 2.0:
        raise RuntimeError(f"inset {d}: wavefront vs shapely mismatch {err:.2f} px2")
    for k in TONGUES:
        if tongue_metrics(res, k) is None:
            info["vanished"].append(k)
    for _ in range(8):
        thin = [sp for sp in spikes(res) if sp["neck"] < MIN_BASE]
        if not thin:
            break
        sp = min(thin, key=lambda z: z["neck"])
        res = drop_spike(res, sp)
        info["cut"].append(label_of(sp))
    for k in TONGUES:
        if tongue_metrics(res, k) is None and k not in info["vanished"] and k not in info["cut"]:
            info["cut"].append(k)
    return res, info, err


def make_pose(out, skirt_y=SKIRT_Y):
    layers = {"out": out}
    info = {}
    for name, d in INSET.items():
        P, inf, err = inner_layer(out, d, skirt_y)
        inf["shapely_symdiff_px2"] = round(err, 4)
        layers[name] = P
        info[name] = inf
    return layers, info


def validate_pose(name, layers, strict=True):
    rep = {}
    o = poly(layers["out"])
    assert o.is_valid, (name, "out invalid")
    for ln in ("mid", "core"):
        p = poly(layers[ln])
        if p.is_empty or p.area < 1e-6:
            continue
        assert p.is_valid, (name, ln, "invalid")
    m = poly(layers["mid"])
    c = poly(layers["core"])
    if not m.is_empty:
        assert m.difference(o).area < 0.5, (name, "mid leaks out of out")
    if not c.is_empty:
        assert c.difference(m.buffer(1e-3)).area < 0.5, (name, "core leaks out of mid")
    for k in TONGUES:
        mt = tongue_metrics(layers["out"], k)
        rep[k] = None if mt is None else dict(tip_angle=round(mt["tip_angle"], 2), neck=round(mt["neck"], 1))
        if strict and mt is not None:
            assert mt["neck"] >= MIN_BASE, (name, k, "neck", mt["neck"])
    return rep


def to_canvas(P, sx, sy):
    th = math.radians(ROT)
    c, s = math.cos(th), math.sin(th)
    x, y = P[:, 0] * sx, P[:, 1] * sy
    return np.stack([E[0] + c * x - s * y, E[1] + s * x + c * y], 1)


def set_skirt(layers, skirt_y):
    out = {}
    for ln, P in layers.items():
        Q = P.copy()
        d = 0.0 if ln == "out" else INSET[ln]
        Q[0, 1] = Q[-1, 1] = skirt_y - d
        out[ln] = Q
    return out


# ------------------------------------------------------------------ pot_front occlusion of the skirt
class FrontAlpha:
    def __init__(self):
        a = Image.open(BUILD / "pot_front.png").getchannel("A")
        self.a = np.asarray(a, np.float64) / 255.0
        self.h, self.w = self.a.shape

    def sample(self, XY):
        x = XY[:, 0] * 2.0 - 0.5
        y = XY[:, 1] * 2.0 - 0.5
        x0 = np.clip(np.floor(x).astype(int), 0, self.w - 2)
        y0 = np.clip(np.floor(y).astype(int), 0, self.h - 2)
        fx, fy = np.clip(x - x0, 0, 1), np.clip(y - y0, 0, 1)
        a = self.a
        return (a[y0, x0] * (1 - fx) * (1 - fy) + a[y0, x0 + 1] * fx * (1 - fy)
                + a[y0 + 1, x0] * (1 - fx) * fy + a[y0 + 1, x0 + 1] * fx * fy)


def bottom_hidden(fa, layers, sx, sy):
    worst = 1.0
    for ln, P in layers.items():
        A, B = P[0], P[-1]
        ts = np.linspace(0, 1, 41)[:, None]
        seg = A[None] * (1 - ts) + B[None] * ts
        C = to_canvas(seg, sx, sy)
        for dy in (0.0, -4.0):
            worst = min(worst, float(fa.sample(C + np.array([0.0, dy])).min()))
    return worst


# ------------------------------------------------------------------ build everything
def r2(P):
    return [[round(float(x), 2), round(float(y), 2)] for x, y in P]


def drawn_outs():
    """OUT outlines of every pose (drawn poses + SMEAR + P0)."""
    outs = {k: build_out(v) for k, v in POSES_DEF.items()}
    # SMEAR: P1/P2 in-between, central tongue stretched to 130 % of its length from the base line
    sm = 0.5 * (outs["P1"] + outs["P2"])
    tc = TIP_IDX["C"]
    sm[tc] = np.array([sm[tc][0], SMEAR_STRETCH * sm[tc][1]])
    outs["SMEAR"] = sm
    # P0: germ = P1 at 8 % (sharp tips kept), skirt bottom kept at the common skirtY convention
    p0 = outs["P1"] * P0_SCALE
    p0[0, 1] = p0[-1, 1] = SKIRT_Y
    outs["P0"] = p0
    return outs


def build():
    outs = drawn_outs()
    tc = TIP_IDX["C"]

    order = ["P0", "P1", "SMEAR", "P2", "P3", "A", "B", "C"]
    poses, pinfo, pval = {}, {}, {}
    for k in order:
        layers, info = make_pose(outs[k])
        poses[k] = layers
        pinfo[k] = info
        pval[k] = validate_pose(k, layers, strict=(k != "P0"))

    # ---- frames
    fa = FrontAlpha()
    frames, extremes = {}, {}
    for fp in FRAME_PLAN:
        f = fp["frame"]
        if fp.get("visible", True) is False:
            frames[f] = dict(visible=False)
            continue
        sx, sy = fp["scaleX"] / 100.0, fp["scaleY"] / 100.0
        if "blend" in fp:
            bl = fp["blend"]
            out = (1 - bl["t"]) * outs[bl["a"]] + bl["t"] * outs[bl["b"]]
            layers, _ = make_pose(out)
            validate_pose(f"f{f}", layers)
        else:
            layers = {k: v.copy() for k, v in poses[fp["pose"]].items()}
        validate_pose(f"f{f}", layers)
        # skirt depth: the bottom of every layer must sit under opaque pot_front
        S = SKIRT_Y
        while bottom_hidden(fa, set_skirt(layers, S), sx, sy) < 0.995:
            S += 5.0
            if S > 900:
                raise RuntimeError(f"f{f}: cannot hide the skirt")
        layers = set_skirt(layers, S)
        # recompute inner layers with the final skirt to prove the override rule is exact
        validate_pose(f"f{f}/skirt", layers)
        chk, _ = make_pose(layers["out"], S)
        for ln in ("mid", "core"):
            assert np.abs(chk[ln] - layers[ln]).max() < 0.05 or poly(layers[ln]).area < 1e-6, (f, ln)
        C = to_canvas(layers["out"], sx, sy)
        tip = to_canvas(layers["out"][[tc]], sx, sy)[0]
        top = C[np.argmin(C[:, 1])]
        height_ratio = float(-layers["out"][:, 1].min() * sy / H)
        ex = dict(minX=float(C[:, 0].min()), maxX=float(C[:, 0].max()), minY=float(C[:, 1].min()),
                  maxY=float(C[:, 1].max()), topPoint=[float(top[0]), float(top[1])],
                  centralTip=[float(tip[0]), float(tip[1])], heightRatio=height_ratio)
        ex["ok"] = bool(ex["minY"] - GLOW >= SAFE["y0"] and ex["minX"] - GLOW >= SAFE["x0"]
                        and ex["maxX"] + GLOW <= SAFE["x1"] and ex["maxY"] + GLOW <= SAFE["y1"]
                        and height_ratio <= 1.2 + 1e-9)
        extremes[f] = ex
        frames[f] = dict(visible=True, scaleX=fp["scaleX"], scaleY=fp["scaleY"], skirtY=S, layers=layers,
                         svgTransform=f"translate({E[0]:g} {E[1]:g}) rotate({ROT:g}) scale({sx:g} {sy:g})")
        fp["skirtY"] = S
    return outs, poses, pinfo, pval, frames, extremes


def write_json(poses, pinfo, pval, frames, extremes):
    def layers_json(L):
        return {k: r2(L[k]) for k in ("out", "mid", "core")}

    doc = dict(
        meta=dict(
            what="Marin'Or Ivoire timbre-marmite: faceted flame geometry (spec §3, 4.4, 5, 6.2, 6.3, 7)",
            generator="tools/build_flame.py (deterministic)",
            units="flame-local CSS px at 100 % scale (@1x canvas 1080x1350)",
            local_frame="origin = base centre, +x right, +y DOWN, the flame grows towards -y",
            placement=dict(E=[float(E[0]), float(E[1])], rotationDeg=ROT,
                           svgTransform="translate(627 647) rotate(14) scale(sx sy)  (sx, sy = scaleX/100, scaleY/100)",
                           css="left:0;top:0; transform-origin:0 0; transform: translate(627px,647px) rotate(14deg) scale(sx,sy)"),
            H_fl=H, baseWidth=2 * HALF, insets=INSET, minTongueBase=MIN_BASE,
            vertexOrder=NAMES, vertexCountPerLayer=dict(out=NV, mid=NV, core=NV),
            tongues={k: dict(left=NAMES[a], tip=NAMES[t], right=NAMES[b]) for k, (a, t, b) in TONGUES.items()},
            layers=dict(
                out=dict(fill=dict(type="linearGradient", gradientUnits="userSpaceOnUse (flame-local)",
                                   **GRAD, stops=[[0, COL["out0"]], [1, COL["out1"]]]),
                         note="#FFA53A towards the tips (as on the printed flames), #FF6B31 at the base"),
                mid=dict(fill=COL["mid"], inset=INSET["mid"]),
                core=dict(fill=COL["core"], inset=INSET["core"]),
                glitter="composition: glitter texture, screen 70 %, matte = core",
                glow="composition: OUT blurred 24 px, screen 35 % (safe-zone check uses a 24 px margin)",
                paint_order=["glow?", "out", "mid", "core", "glitter"]),
            skirt=dict(note=("vertices 0/14 (and 1/13) form a hidden skirt below the base line: the inner front lip "
                             "of the pot is ~100 px below E, so a 30 px extension would leave the base edge floating "
                             "in the pot interior. Bottom y of every layer = skirtY - inset (out 0, mid 18, core 37); "
                             "x never changes. framePlan.skirtY gives the depth that keeps all bottoms under "
                             "opaque pot_front for that frame's scale. z-order: pot_back < flame < pot_front."),
                       defaultSkirtY=SKIRT_Y, kneeY=KNEE_Y, kneeMaxSlantDeg=KNEE_MAX_SLANT),
            interpolation=("all poses share the same vertex order and count per layer; collapsed tongues are "
                           "zero-area spikes (tip on the chord between its notches, or all three vertices merged). "
                           "framePlan blends lerp OUT; frames[] holds the exact baked layers to draw."),
            rule_no_text="no text/letters/numbers in any visual output",
        ),
        poses={k: dict(layers=layers_json(poses[k]),
                       innerInfo={ln: dict(vanishedTongues=pinfo[k][ln]["vanished"], cutTongues=pinfo[k][ln]["cut"],
                                           shapelySymDiffPx2=pinfo[k][ln]["shapely_symdiff_px2"])
                                  for ln in ("mid", "core")},
                       outTongues=pval[k])
               for k in poses},
        framePlan=[{k: v for k, v in fp.items()} for fp in FRAME_PLAN],
        frames={str(f): (dict(visible=False) if not fr["visible"] else
                         dict(visible=True, scaleX=fr["scaleX"], scaleY=fr["scaleY"], skirtY=fr["skirtY"],
                              svgTransform=fr["svgTransform"], layers=layers_json(fr["layers"])))
                for f, fr in frames.items()},
        checks=dict(
            safeZone=SAFE, glowMargin=GLOW,
            extremesCanvas={str(f): {k: (round(v, 2) if isinstance(v, float) else
                                         ([round(x, 2) for x in v] if isinstance(v, list) else v))
                                     for k, v in ex.items()} for f, ex in extremes.items()},
            allFramesInsideSafeZoneWithGlow=all(ex["ok"] for ex in extremes.values()),
            f12CentralTip=[round(x, 2) for x in extremes[12]["centralTip"]], f12Target=list(TIP_TARGET_F12),
            f10CentralTipY=round(extremes[10]["centralTip"][1], 2),
        ),
    )
    (BUILD / "flame.json").write_text(json.dumps(doc, indent=1))
    return doc


# ------------------------------------------------------------------ previews (Chromium)
def pts_attr(P):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in dedupe(np.asarray(P, float)))


def grad_def(gid):
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{GRAD["x1"]}" y1="{GRAD["y1"]}" '
            f'x2="{GRAD["x2"]}" y2="{GRAD["y2"]}"><stop offset="0" stop-color="{COL["out0"]}"/>'
            f'<stop offset="1" stop-color="{COL["out1"]}"/></linearGradient>')


def layers_svg(L, gid):
    s = f'<polygon points="{pts_attr(L["out"])}" fill="url(#{gid})"/>'
    for ln in ("mid", "core"):
        if poly(L[ln]).area > 1e-6:
            s += f'<polygon points="{pts_attr(L[ln])}" fill="{COL[ln]}"/>'
    return s


def html_page(w, h, body, bg="transparent"):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;padding:0;'
            f'width:{w}px;height:{h}px;overflow:hidden;background:{bg}}}'
            f'.abs{{position:absolute;left:0;top:0}}</style></head><body>{body}</body></html>')


def poses_sheet(poses, tmp):
    order = ["P0", "P1", "SMEAR", "P2", "P3", "A", "B", "C"]
    sc, cw, ch, pad = 0.74, 330, 470, 20
    W = len(order) * cw + 2 * pad
    Hh = 2 * ch + 3 * pad
    base_y = 395
    defs = grad_def("gs")
    rows = ""
    for r, bg in enumerate(("#161B1E", "#F6E8EA")):
        y0 = pad + r * (ch + pad)
        rows += f'<rect x="{pad}" y="{y0}" width="{len(order) * cw}" height="{ch}" fill="{bg}"/>'
        guide = "#3A4449" if r == 0 else "#D9C3C7"
        for i, k in enumerate(order):
            cx = pad + i * cw + cw / 2
            by = y0 + base_y
            rows += (f'<line x1="{cx - cw / 2 + 14}" y1="{by}" x2="{cx + cw / 2 - 14}" y2="{by}" stroke="{guide}" stroke-width="1"/>'
                     f'<line x1="{cx - cw / 2 + 14}" y1="{by - H * sc:.2f}" x2="{cx + cw / 2 - 14}" y2="{by - H * sc:.2f}" '
                     f'stroke="{guide}" stroke-width="1" stroke-dasharray="3 5"/>')
            clip = f"cl{r}{i}"
            defs += (f'<clipPath id="{clip}"><rect x="{cx - cw / 2}" y="{y0}" width="{cw}" height="{base_y + 46}"/></clipPath>')
            rows += (f'<g clip-path="url(#{clip})"><g transform="translate({cx:.2f} {by:.2f}) scale({sc})">'
                     f'{layers_svg(poses[k], "gs")}</g></g>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{Hh}" viewBox="0 0 {W} {Hh}">'
           f'<defs>{defs}</defs><rect width="{W}" height="{Hh}" fill="#0E1113"/>{rows}</svg>')
    p = tmp / "poses.html"
    p.write_text(html_page(W, Hh, svg))
    return dict(html=str(p), out=str(BUILD / "flame_poses.png"), width=W, height=Hh, dpr=1)


LIP_INNER = None


def lip_clip_poly():
    pot = json.loads((BUILD / "pot.json").read_text())
    lip = pot["front_lip_inner_polyline"]
    pts = [(0, 0), (1080, 0), (1080, lip[-1][1])] + [tuple(p) for p in reversed(lip)] + [(0, lip[0][1])]
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


GLITTER_TILE = {}


def glitter_tile(tmp):
    """Largest axis-aligned rectangle of the stamp glitter that lies fully inside its mask, saved as a
    tile for the preview pattern (the source texture is white outside the mask)."""
    if "uri" in GLITTER_TILE:
        return GLITTER_TILE["uri"], GLITTER_TILE["w"], GLITTER_TILE["h"]
    rgb = np.asarray(Image.open(ROOT / "assets" / "src" / "glitter-rgb.png").convert("RGB"))
    m = np.asarray(Image.open(ROOT / "assets" / "src" / "glitter-mask.png").convert("L")) >= 250
    best = (0, 0, 0, 0, 0)
    for y0 in range(m.shape[0]):
        col = np.ones(m.shape[1], bool)
        for y1 in range(y0, m.shape[0]):
            col &= m[y1]
            if not col.any():
                break
            run, x_start = 0, 0
            for x in range(m.shape[1] + 1):
                if x < m.shape[1] and col[x]:
                    run += 1
                else:
                    area = run * (y1 - y0 + 1)
                    if area > best[0] and run >= 24 and (y1 - y0) >= 24:
                        best = (area, x - run, y0, x, y1 + 1)
                    run = 0
    _, x0, y0, x1, y1 = best
    tile = rgb[y0 + 1:y1 - 1, x0 + 1:x1 - 1]
    path = tmp / "glitter_tile.png"
    Image.fromarray(tile).save(path)
    GLITTER_TILE.update(uri=path.as_uri(), w=tile.shape[1] * 1.8, h=tile.shape[0] * 1.8)
    return GLITTER_TILE["uri"], GLITTER_TILE["w"], GLITTER_TILE["h"]


def flame_canvas_svgs(L, transform, uid, glow=True, glitter=True, only_above_lip=False, ghost_below=False, tmp=None):
    """Returns HTML (several absolutely positioned <svg> so blend modes hit the page backdrop)."""
    glit, gw, gh = glitter_tile(tmp) if glitter else ("", 1, 1)
    clip_lip = (f'<clipPath id="lip{uid}"><polygon points="{lip_clip_poly()}"/></clipPath>' if (only_above_lip or ghost_below) else "")
    cattr = f' clip-path="url(#lip{uid})"' if only_above_lip else ""
    html = ""
    if glow:
        html += (f'<svg class="abs" width="1080" height="1350" style="mix-blend-mode:screen;opacity:.35">'
                 f'<defs>{grad_def("gg" + uid)}<filter id="bl{uid}" x="-30%" y="-30%" width="160%" height="160%">'
                 f'<feGaussianBlur stdDeviation="12"/></filter>{clip_lip}</defs><g{cattr}><g filter="url(#bl{uid})">'
                 f'<g transform="{transform}"><polygon points="{pts_attr(L["out"])}" fill="url(#gg{uid})"/></g></g></g></svg>')
    body = f'<g transform="{transform}">{layers_svg(L, "gf" + uid)}</g>'
    if ghost_below:
        html += (f'<svg class="abs" width="1080" height="1350" style="opacity:.33"><defs>{grad_def("gf" + uid)}</defs>{body}</svg>')
        cattr = f' clip-path="url(#lip{uid})"'
    html += (f'<svg class="abs" width="1080" height="1350"><defs>{grad_def("gf" + uid)}{clip_lip}</defs>'
             f'<g{cattr}>{body}</g></svg>')
    if glitter and poly(L["core"]).area > 1e-6:
        html += (f'<svg class="abs" width="1080" height="1350" style="mix-blend-mode:screen;opacity:.7">'
                 f'<defs><pattern id="gp{uid}" patternUnits="userSpaceOnUse" width="{gw}" height="{gh}">'
                 f'<image href="{glit}" width="{gw}" height="{gh}"/></pattern>'
                 f'<clipPath id="cc{uid}"><polygon transform="{transform}" points="{pts_attr(L["core"])}"/></clipPath>{clip_lip}</defs>'
                 f'<g{cattr}><rect width="1080" height="1350" fill="url(#gp{uid})" clip-path="url(#cc{uid})"/></g></svg>')
    return html


def pot_layers_html(rot, dy, which=("front", "lid")):
    pot = json.loads((BUILD / "pot.json").read_text())
    Hx, Hy = pot["hinge_H"]
    slide = pot["open_preview"]["lid_under_slide_y_local"]
    u = lambda n: (BUILD / n).as_uri()
    s = ""
    if "back" in which:
        s += f'<img class="abs" src="{u("pot_back.png")}" width="1080" height="1350">'
    if "flame" in which:
        s += "{FLAME}"
    if "front" in which:
        s += f'<img class="abs" src="{u("pot_front.png")}" width="1080" height="1350">'
    if "lid" in which:
        s += (f'<div class="abs" style="width:1080px;height:1350px;transform-origin:{Hx}px {Hy}px;'
              f'transform:translate(0px,{dy}px) rotate({rot}deg)">'
              f'<img class="abs" src="{u("pot_lid_under.png")}" width="1080" height="1350" style="top:{slide}px">'
              f'<img class="abs" src="{u("pot_lid.png")}" width="1080" height="1350">'
              f'<img class="abs" src="{u("pot_knob.png")}" width="1080" height="1350"></div>')
    return s


def guides_svg(tip=None):
    g = (f'<svg class="abs" width="1080" height="1350"><rect x="{SAFE["x0"]}" y="{SAFE["y0"]}" '
         f'width="{SAFE["x1"] - SAFE["x0"]:.1f}" height="{SAFE["y1"] - SAFE["y0"]:.1f}" fill="none" stroke="#00B7FF" '
         f'stroke-width="1.2" stroke-dasharray="7 5"/>')
    for (x, y), col in (((E[0], E[1]), "#00B7FF"), (TIP_TARGET_F12, "#FF2BD6")):
        g += (f'<line x1="{x - 9}" y1="{y}" x2="{x + 9}" y2="{y}" stroke="{col}" stroke-width="1.2"/>'
              f'<line x1="{x}" y1="{y - 9}" x2="{x}" y2="{y + 9}" stroke="{col}" stroke-width="1.2"/>')
    if tip is not None:
        g += f'<circle cx="{tip[0]:.2f}" cy="{tip[1]:.2f}" r="4" fill="none" stroke="#FF2BD6" stroke-width="1.2"/>'
    return g + "</svg>"


def inplace_f12(frames, extremes, tmp):
    fr = frames[12]
    L, T = fr["layers"], fr["svgTransform"]
    po = (BUILD / "preview_open.png").as_uri()
    bg = (f'<div class="abs" style="width:1080px;height:1350px;overflow:hidden">'
          f'<img class="abs" src="{po}" width="2160" height="1350"></div>')
    rot, dy = LID[12]
    left = (bg + flame_canvas_svgs(L, T, "a", tmp=tmp) + pot_layers_html(rot, dy) + guides_svg(extremes[12]["centralTip"]))
    right = (bg + flame_canvas_svgs(L, T, "b", glow=False, glitter=False, ghost_below=True)
             + guides_svg(extremes[12]["centralTip"]))
    body = (f'<div class="abs" style="width:1080px;height:1350px;isolation:isolate">{left}</div>'
            f'<div class="abs" style="left:1080px;width:1080px;height:1350px;isolation:isolate">{right}</div>')
    p = tmp / "inplace.html"
    p.write_text(html_page(2160, 1350, body, "#ffffff"))
    return dict(html=str(p), out=str(BUILD / "flame_inplace_f12.png"), width=2160, height=1350, dpr=1)


def frames_strip(frames, tmp):
    bgp = BUILD / "pot_work" / "bg_stamp_2x.png"
    bg = (f'<img class="abs" src="{bgp.as_uri()}" width="1080" height="1350">' if bgp.exists()
          else '<div class="abs" style="width:1080px;height:1350px;background:#F6E8EA"></div>')
    x0, y0, cw, ch, sc = 360, 160, 600, 740, 0.5
    fl = list(range(9, 28))
    cols = 10
    tw, th = int(cw * sc), int(ch * sc)
    W, Hh = cols * tw + (cols + 1) * 6, 2 * th + 18
    body = ""
    for i, f in enumerate(fl):
        fr = frames[f]
        rot, dy = LID[f]
        scene = bg + pot_layers_html(rot, dy, which=("back", "flame", "front", "lid"))
        scene = scene.replace("{FLAME}", flame_canvas_svgs(fr["layers"], fr["svgTransform"], f"s{f}", tmp=tmp))
        cx = 6 + (i % cols) * (tw + 6)
        cy = 6 + (i // cols) * (th + 6)
        body += (f'<div class="abs" style="left:{cx}px;top:{cy}px;width:{tw}px;height:{th}px;overflow:hidden;isolation:isolate">'
                 f'<div class="abs" style="width:1080px;height:1350px;transform-origin:0 0;'
                 f'transform:scale({sc}) translate({-x0}px,{-y0}px)">{scene}</div></div>')
    p = tmp / "strip.html"
    p.write_text(html_page(W, Hh, body, "#202629"))
    return dict(html=str(p), out=str(BUILD / "flame_frames_strip.png"), width=W, height=Hh, dpr=1)


def render(jobs, tmp):
    jf = tmp / "jobs.json"
    jf.write_text(json.dumps(jobs))
    subprocess.run(["node", str(TOOLS / "render_html.mjs"), "--batch", str(jf)], check=True, cwd=str(ROOT))


def notes_table(extremes):
    lines = ["| f | sY/sX | skirtY | minX | maxX | minY (top) | central tip | H ratio | ok (+24 glow) |", "|---|---|---|---|---|---|---|---|---|"]
    for fp in FRAME_PLAN:
        f = fp["frame"]
        if f not in extremes:
            lines.append(f"| {f} | 0 | - | - | - | - | - | 0 | not rendered |")
            continue
        e = extremes[f]
        lines.append(f"| {f} | {fp['scaleY']:g}/{fp['scaleX']:g} | {fp['skirtY']:g} | {e['minX']:.1f} | {e['maxX']:.1f} | "
                     f"{e['minY']:.1f} | ({e['centralTip'][0]:.1f};{e['centralTip'][1]:.1f}) | {e['heightRatio']:.3f} | {e['ok']} |")
    return "\n".join(lines)


def main():
    outs, poses, pinfo, pval, frames, extremes = build()
    doc = write_json(poses, pinfo, pval, frames, extremes)
    print("vertex counts:", {k: {ln: len(v) for ln, v in L.items()} for k, L in poses.items()})
    for k in poses:
        print(k, "mid vanished", pinfo[k]["mid"]["vanished"], "cut", pinfo[k]["mid"]["cut"],
              "| core vanished", pinfo[k]["core"]["vanished"], "cut", pinfo[k]["core"]["cut"],
              "| tips", {t: (v["tip_angle"] if v else None) for t, v in pval[k].items()})
    print(notes_table(extremes))
    print("f12 tip", doc["checks"]["f12CentralTip"], "f10 tip y", doc["checks"]["f10CentralTipY"],
          "all ok", doc["checks"]["allFramesInsideSafeZoneWithGlow"])
    if "--no-previews" in sys.argv:
        return
    base = SCRATCH_DEFAULT if SCRATCH_DEFAULT.exists() else Path(tempfile.gettempdir())
    tmp = Path(tempfile.mkdtemp(prefix="flame_", dir=str(base)))
    jobs = [poses_sheet(poses, tmp), inplace_f12(frames, extremes, tmp), frames_strip(frames, tmp)]
    render(jobs, tmp)
    print("previews:", [j["out"] for j in jobs])


if __name__ == "__main__":
    main()
