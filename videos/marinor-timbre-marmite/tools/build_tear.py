#!/usr/bin/env python3
"""Tear geometry for the Marin'Or stamp (spec 6.4 / 6.5 / 9 "Déchirure"), canvas px @1x.

Outputs (assets/build/):
  tear.json                 crack polylines, fragments F1/F2/F3, transforms, lips (+ reveal chunks), liseré, stress mark
  tear_preview_lines.png    crack + fragments over the stamp at rest
  tear_preview_final.png    fragments at x1.00 (rest), over a checkerboard
  tear_preview_peak.png     fragments at x1.35 (f38 peak)
  tear_preview_f35.png      reveal check: crack front at f35 (trunk 95 %), nothing moved yet
  previews/*.html           the exact HTML/SVG that Chromium rasterised (reference implementation)

Deterministic: fixed seeds, no wall-clock. Re-run:  (cd PROJECT && python3 tools/build_tear.py)
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
from scipy.ndimage import gaussian_filter1d
from shapely import affinity
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Point, Polygon, box
from shapely.ops import linemerge, polygonize, unary_union
from shapely.validation import make_valid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stamp_geom import (BUILD, CANVAS_H, CANVAS_W, GREY_OFFSET_PX, POT_S, POT_X0, POT_Y0, ROOT,  # noqa: E402
                        SCRATCH, bezier_point, canvas_segments, fmt, load_source, paper_polygon,
                        u2c, vignette_rect_px)
import build_stamp_parts as bsp  # noqa: E402

PREV = os.path.join(BUILD, "previews")
SEED = 20261013

# ----------------------------------------------------------------------------------------------
# Spec 6.4 base geometry (px @1x)
SPEC_S, SPEC_N, SPEC_ER, SPEC_EB = (92.8, 479.2), (635.0, 823.0), (981.0, 783.4), (714.7, 1221.5)
TRUNK_MID = [(207, 552), (233, 537), (345, 637), (372, 623), (491, 733), (519, 720)]
A_MID = [(724, 797), (745, 813), (849, 785), (871, 800)]
B_MID = [(657, 913), (638, 936), (670, 1049), (652, 1077)]
EXT = {"trunk": (60.0, None), "branchA": (1014.0, None), "branchB": (None, 1255.0)}  # spec cut extensions

TRANSFORMS = {  # spec 6.4 table: rot deg (SVG/screen convention, + = clockwise), T px, tilt deg
    "F1": {"pivot": "E_R", "rest": {"rot": 1.1, "tx": -2.4, "ty": -4.8, "tilt": ("rotY", -2.0)},
           "peak": {"rot": 1.5, "tx": -3.2, "ty": -6.5, "tilt": ("rotY", -2.7)}},
    "F2": {"pivot": "E_B", "rest": {"rot": -0.8, "tx": -6.4, "ty": 4.8, "tilt": ("rotX", 1.5)},
           "peak": {"rot": -1.1, "tx": -8.6, "ty": 6.5, "tilt": ("rotX", 2.0)}},
    "F3": {"pivot": "E_B", "rest": {"rot": 0.8, "tx": 6.4, "ty": 4.8, "tilt": ("rotY", 1.5)},
           "peak": {"rot": 1.1, "tx": 8.6, "ty": 6.5, "tilt": ("rotY", 2.0)}},
}
# Luminance from tilt. Convention (After Effects, right-handed: x right, y down, z into screen):
# +rotY brings the right edge toward camera -> the face turns left; +rotX brings the top edge toward camera
# -> the face turns down. Key light upper-left (matches the pot's shading). Facing the light = brighter.
LUM_REST = {"F1": -0.037, "F2": -0.030, "F3": +0.030}   # x1.35 -> -5.0 %, -4.05 %, +4.05 %
SPRING_MULT = {36: 0.60, 37: 1.10, 38: 1.35, 39: 1.23, 40: 1.00, 41: 0.88, 42: 0.92, 43: 1.00,
               44: 1.04, 45: 1.03, 46: 1.00, 47: 1.00}

LIP = {  # lip widths (px) along the crack, inside each fragment
    # fib_len = (min, gamma scale, max) px ; fib_gap = mean spacing px
    "F1": {"mid": 9.5, "amp": 1.5, "fine": 0.55, "fib_len": (0.9, 0.8, 4.6), "fib_gap": 9.0},
    "F2": {"mid": 4.0, "amp": 1.0, "fine": 0.35, "fib_len": (0.5, 0.45, 2.4), "fib_gap": 12.0},
    "F3": {"mid": 4.0, "amp": 1.0, "fine": 0.35, "fib_len": (0.5, 0.45, 2.4), "fib_gap": 12.0},
}
CHUNK = 6.0          # reveal granularity along the crack (px of base arc length)
CHUNK_OVERLAP = 1.0  # overlap between consecutive chunks so opaque chunks never show AA seams
FRONT_START, FRONT_SPEED, BRANCH_END = 33.6, 470.0, 36.0


# ----------------------------------------------------------------------------------------------
def notch_bottoms():
    """Deepest point of every perforation notch of the WHITE paper (canvas px)."""
    segs = canvas_segments(load_source()["white_d"])
    out, pos = [], None
    for s in segs:
        if s[0] in "ML":
            pos = s[1]
            continue
        if s[0] == "C":
            p0, p3 = np.array(pos), np.array(s[3])
            chord = p3 - p0
            n = np.array([-chord[1], chord[0]]) / np.linalg.norm(chord)
            ts = np.linspace(0, 1, 4001)
            pts = np.array([bezier_point(pos, *s[1:], t) for t in ts])
            dep = (pts - p0) @ n
            k = int(np.argmax(np.abs(dep)))
            out.append({"pt": pts[k], "depth": float(abs(dep[k])), "chord": float(np.linalg.norm(chord))})
            pos = s[3]
    return out


def snap(spec_pt, notches):
    best = min(notches, key=lambda n: np.hypot(*(n["pt"] - np.array(spec_pt))))
    return tuple(float(round(v, 3)) for v in best["pt"]), float(np.hypot(*(best["pt"] - np.array(spec_pt)))), best


def value_noise(rng, length, scale):
    """Smooth 1-D value noise in [-1, 1], function of arc length."""
    n = int(length / scale) + 4
    vals = rng.uniform(-1, 1, n)

    def f(s):
        x = np.asarray(s) / scale
        i = np.floor(x).astype(int)
        t = x - i
        t = t * t * t * (t * (t * 6 - 15) + 10)
        i = np.clip(i, 0, n - 2)
        return vals[i] * (1 - t) + vals[i + 1] * t
    return f


def midpoint_displace(p0, p1, s0, s1, rng, cap=1.4, amp=1.2, hurst=0.55, min_len=1.6):
    """Fractal (midpoint displacement) polyline between two fixed vertices. Returns [(x,y,s), ...]."""
    d = np.array(p1, float) - np.array(p0, float)
    L = float(np.linalg.norm(d))
    nrm = np.array([-d[1], d[0]]) / L
    pts = [(np.array(p0, float), s0), (np.array(p1, float), s1)]
    seg = L
    while seg > min_len:
        sigma = min(cap, amp * (seg / 40.0) ** hurst)
        new = [pts[0]]
        for (qa, sa), (qb, sb) in zip(pts[:-1], pts[1:]):
            off = float(np.clip(rng.normal(0, sigma), -2 * sigma, 2 * sigma))
            new.append(((qa + qb) / 2 + nrm * off, (sa + sb) / 2))
            new.append((qb, sb))
        pts = new
        seg /= 2
    return [(float(p[0]), float(p[1]), float(s)) for p, s in pts]


def build_branch(verts, seed):
    rng = np.random.default_rng(seed)
    out, s = [], 0.0
    for a, b in zip(verts[:-1], verts[1:]):
        L = math.dist(a, b)
        seg = midpoint_displace(a, b, s, s + L, rng)
        out.extend(seg if not out else seg[1:])
        s += L
    return out, s


def base_tangent_fn(verts, sigma=4.0):
    """Smoothed unit tangent of the base polyline as a function of base arc length."""
    v = np.array(verts, float)
    seglen = np.linalg.norm(np.diff(v, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seglen)])
    ds = 0.25
    ss = np.arange(0, cum[-1] + ds, ds)
    idx = np.clip(np.searchsorted(cum, ss, side="right") - 1, 0, len(seglen) - 1)
    tan = (v[idx + 1] - v[idx]) / seglen[idx, None]
    tx = gaussian_filter1d(tan[:, 0], sigma / ds, mode="nearest")
    ty = gaussian_filter1d(tan[:, 1], sigma / ds, mode="nearest")
    nn = np.hypot(tx, ty)
    tx, ty = tx / nn, ty / nn

    def f(s):
        return np.stack([np.interp(s, ss, tx), np.interp(s, ss, ty)], axis=-1)
    return f


def poly_d(geom, nd=2):
    """SVG path data of a (Multi)Polygon (even-odd safe: holes are emitted as subpaths)."""
    polys = [geom] if isinstance(geom, Polygon) else [g for g in getattr(geom, "geoms", []) if isinstance(g, Polygon)]
    parts = []
    for p in polys:
        if p.is_empty:
            continue
        for ring in [p.exterior] + list(p.interiors):
            c = np.round(np.array(ring.coords)[:-1], nd)
            parts.append("M" + "L".join(f"{fmt(x)} {fmt(y)}" for x, y in c) + "Z")
    return "".join(parts)


def line_d(geom, nd=2):
    lines = [geom] if isinstance(geom, LineString) else [g for g in getattr(geom, "geoms", []) if isinstance(g, LineString)]
    parts = []
    for ln in lines:
        c = np.round(np.array(ln.coords), nd)
        if len(c) >= 2:
            parts.append("M" + "L".join(f"{fmt(x)} {fmt(y)}" for x, y in c))
    return "".join(parts)


def polys_of(g):
    if g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon) and p.area > 1e-6]


def lines_of(g):
    if g.is_empty:
        return []
    if isinstance(g, LineString):
        return [g]
    out = []
    for p in getattr(g, "geoms", []):
        out.extend(lines_of(p))
    return out


# ----------------------------------------------------------------------------------------------
def main():
    os.makedirs(PREV, exist_ok=True)
    os.makedirs(SCRATCH, exist_ok=True)
    report = {}

    white, _ = paper_polygon("white", step=0.8)
    vx, vy, vw, vh = vignette_rect_px()
    vig = box(vx, vy, vx + vw, vy + vh)
    src = load_source()
    flame_polys = []
    for _, pts in src["polys"]:
        v = [float(t) for t in pts.split()]
        flame_polys.append(Polygon([u2c(v[i], v[i + 1]) for i in range(0, len(v), 2)]))
    picture = unary_union([vig] + flame_polys)   # where lips can be seen (original flames overhang the vignette)

    # 1. endpoints -> true notch bottoms of the white paper
    notches = notch_bottoms()
    S, dS, nS = snap(SPEC_S, notches)
    ER, dER, nER = snap(SPEC_ER, notches)
    EB, dEB, nEB = snap(SPEC_EB, notches)
    N = SPEC_N
    report["endpoints"] = {
        "S": {"spec": SPEC_S, "notchBottom": S, "moved_px": round(dS, 3), "notchDepth_px": round(nS["depth"], 2), "notchChord_px": round(nS["chord"], 2)},
        "E_R": {"spec": SPEC_ER, "notchBottom": ER, "moved_px": round(dER, 3), "notchDepth_px": round(nER["depth"], 2), "notchChord_px": round(nER["chord"], 2)},
        "E_B": {"spec": SPEC_EB, "notchBottom": EB, "moved_px": round(dEB, 3), "notchDepth_px": round(nEB["depth"], 2), "notchChord_px": round(nEB["chord"], 2)},
    }
    for k, p in (("S", S), ("E_R", ER), ("E_B", EB)):
        assert white.exterior.distance(Point(p)) < 0.05, k

    base = {
        "trunk": [S] + TRUNK_MID + [N],
        "branchA": [N] + A_MID + [ER],
        "branchB": [N] + B_MID + [EB],
    }
    seeds = {"trunk": SEED + 1, "branchA": SEED + 2, "branchB": SEED + 3}

    # 2. dense fractal cracks
    dense, length = {}, {}
    for b, verts in base.items():
        pts, L = build_branch(verts, seeds[b])
        dense[b] = pts
        length[b] = L
        bl = LineString(verts)
        dev = max(bl.distance(Point(x, y)) for x, y, _ in pts)
        report.setdefault("noise", {})[b] = {"baseLength_px": round(L, 2), "denseLength_px": round(LineString([(x, y) for x, y, _ in pts]).length, 2),
                                             "maxDeviation_px": round(dev, 2), "vertices": len(pts)}

    # 3. cut lines (crack + spec extension + to the rectangle edge) -> fragments
    ext_trunk = [(-20.0, S[1]), (EXT["trunk"][0], S[1])]
    ext_A = [(EXT["branchA"][0], ER[1]), (CANVAS_W + 20.0, ER[1])]
    ext_B = [(EB[0], EXT["branchB"][1]), (EB[0], CANVAS_H + 20.0)]
    trunk_xy = [(x, y) for x, y, _ in dense["trunk"]]
    A_xy = [(x, y) for x, y, _ in dense["branchA"]]
    B_xy = [(x, y) for x, y, _ in dense["branchB"]]
    cut_lines = [LineString(ext_trunk + trunk_xy), LineString(A_xy + ext_A), LineString(B_xy + ext_B)]
    for ln in cut_lines:
        assert ln.is_simple
    rect = box(0, 0, CANVAS_W, CANVAS_H)
    faces = [f for f in polygonize(unary_union(cut_lines + [rect.exterior])) if f.area > 1 and rect.contains(f.representative_point())]
    assert len(faces) == 3, len(faces)

    def pick(pt):
        return [f for f in faces if f.contains(Point(pt))][0]
    frag = {"F1": pick((535, 300)), "F2": pick((200, 1000)), "F3": pick((900, 1100))}
    assert len({id(v) for v in frag.values()}) == 3
    union_area = unary_union(list(frag.values())).area
    assert abs(union_area - rect.area) < 1e-3 and abs(sum(f.area for f in frag.values()) - rect.area) < 1e-3

    paper_piece, grey_copy, frac = {}, {}, {}
    for k, f in frag.items():
        pc = white.intersection(f)
        assert isinstance(pc, Polygon), f"{k}: paper piece is not a single polygon (bridge/island)"
        paper_piece[k] = pc
        grey_copy[k] = affinity.translate(pc, GREY_OFFSET_PX, GREY_OFFSET_PX)
        frac[k] = pc.area / white.area
    report["areaFractions_whitePaper"] = {k: round(v * 100, 2) for k, v in frac.items()}
    report["areaFractions_spec"] = {"F1": 52.6, "F2": 33.1, "F3": 14.3}

    # which fragments border which branch (and on which side)
    edges = {"F1": ["trunk", "branchA"], "F2": ["trunk", "branchB"], "F3": ["branchA", "branchB"]}

    # 4. lips
    lips_full, lip_chunks, lisere, lisere_chunks = {}, {}, {}, []
    all_chunks = []
    stats_lip = {}
    for fk, branches in edges.items():
        cfg = LIP[fk]
        region_parts, base_parts = [], []
        fchunks = []
        for b in branches:
            pts = np.array(dense[b])
            P, s = pts[:, :2], pts[:, 2]
            tan_f = base_tangent_fn(base[b])
            T = tan_f(s)
            Nrm = np.stack([-T[:, 1], T[:, 0]], axis=1)
            # orient the normal into the fragment (test at the middle of the branch)
            mid = len(P) // 2
            probe = P[mid] + Nrm[mid] * 3
            if not frag[fk].contains(Point(probe)):
                Nrm = -Nrm
            rng = np.random.default_rng(SEED + 100 + 10 * int(fk[1]) + list(base).index(b))
            n35 = value_noise(rng, length[b], 35.0)
            n9 = value_noise(rng, length[b], 9.0)
            n3 = value_noise(rng, length[b], 2.6)
            w = cfg["mid"] + cfg["amp"] * (0.7 * n35(s) + 0.3 * n9(s)) + cfg["fine"] * n3(s)
            w = np.clip(w, cfg["mid"] - cfg["amp"], cfg["mid"] + cfg["amp"])
            Q = P + Nrm * w[:, None]
            # fibres: thin leaning white wisps rooted just inside the inner edge (irregular spacing, heavy-tailed
            # lengths, occasional pairs). They are drawn white over the liseré, like paper fibres over the print.
            spikes = []
            sc = float(rng.gamma(1.5, cfg["fib_gap"] / 1.5)) * 0.6
            while sc < length[b] - 1.5:
                for _rep in range(2 if rng.uniform() < 0.22 else 1):
                    scc = sc + (_rep * float(rng.uniform(1.6, 3.2)))
                    if scc > length[b] - 1.0:
                        break
                    L_sp = float(min(cfg["fib_len"][2], cfg["fib_len"][0] + rng.gamma(2.0, cfg["fib_len"][1])))
                    hw = float(rng.uniform(0.55, 1.15)) * (1.0 if fk == "F1" else 0.8)
                    lean = float(rng.normal(0, 0.45)) * L_sp
                    tf = tan_f(np.array([scc]))[0]
                    nf = np.array([-tf[1], tf[0]])
                    if nf @ Nrm[min(np.searchsorted(s, scc), len(s) - 1)] < 0:
                        nf = -nf
                    root = np.array([np.interp(scc, s, Q[:, 0]), np.interp(scc, s, Q[:, 1])]) - nf * 0.6
                    tip = root + nf * (L_sp + 0.6) + tf * lean
                    spikes.append((scc, Polygon([root - tf * hw, tip, root + tf * hw])))
                sc += float(rng.gamma(1.5, cfg["fib_gap"] / 1.5)) + 1.0
            Pout = P - Nrm * 0.75  # overshoot across the crack, trimmed exactly by the fragment boundary
            sp_s = np.array([t[0] for t in spikes]) if spikes else np.zeros(0)

            def interp_xy(sv, ss, pp):
                return np.array([np.interp(sv, ss, pp[:, 0]), np.interp(sv, ss, pp[:, 1])])

            # chunks along the base arc length (overlapping by CHUNK_OVERLAP)
            nchunks = int(math.ceil(length[b] / CHUNK))
            for ci in range(nchunks):
                s0 = ci * CHUNK
                s1 = min(length[b], (ci + 1) * CHUNK)
                a0, a1 = max(0.0, s0 - CHUNK_OVERLAP * 0.5), min(length[b], s1 + CHUNK_OVERLAP * 0.5)
                ip = (s > a0) & (s < a1)
                outer = [interp_xy(a0, s, Pout)] + list(Pout[ip]) + [interp_xy(a1, s, Pout)]
                inner = [interp_xy(a0, s, Q)] + list(Q[ip]) + [interp_xy(a1, s, Q)]
                pg = make_valid(Polygon(outer + inner[::-1]))
                gbase = unary_union(polys_of(pg)).intersection(frag[fk]).intersection(picture)
                fib = [spikes[j][1] for j in np.nonzero((sp_s >= s0) & (sp_s < s1))[0]]
                gfull = unary_union(polys_of(gbase) + fib).intersection(frag[fk]).intersection(picture) if fib else gbase
                pb, pf = polys_of(gbase), polys_of(gfull)
                if pb:
                    base_parts.append(unary_union(pb))
                if not pf:
                    continue
                g = unary_union(pf)
                region_parts.append(g)
                fchunks.append({"branch": b, "s0": round(s0, 2), "s1": round(s1, 2), "geom": g})
            report.setdefault("fibres", {})[f"{fk}/{b}"] = len(spikes)
            stats_lip[f"{fk}/{b}"] = {"width_min": round(float(w.min()), 2), "width_max": round(float(w.max()), 2)}
        region = unary_union(region_parts)
        region = region.intersection(frag[fk]).intersection(picture)
        region = unary_union([p.buffer(0) for p in polys_of(region)])
        lips_full[fk] = region
        lip_chunks[fk] = fchunks
        all_chunks.extend((fk, c) for c in fchunks)
        # liseré: inner edge of the lip band WITHOUT fibres (not on the crack, not on the picture border)
        bregion = unary_union([p.buffer(0) for p in polys_of(unary_union(base_parts).intersection(frag[fk]).intersection(picture))])
        bd = bregion.boundary
        bd = bd.difference(frag[fk].boundary.buffer(0.08)).difference(picture.boundary.buffer(0.08))
        ls = [ln for ln in lines_of(linemerge(lines_of(bd)) if lines_of(bd) else bd) if ln.length > 0.8]
        lisere[fk] = MultiLineString(ls) if ls else MultiLineString([])
        # liseré reveal pieces: each vertex takes (branch, s) of the nearest crack sample of this fragment
        cand = []
        for b in branches:
            arr = np.array(dense[b])
            cand.append((b, arr))
        for ln in ls:
            c = np.array(ln.coords)
            # densify to <= 1 px
            dense_c = [c[0]]
            for p0, p1 in zip(c[:-1], c[1:]):
                n = max(1, int(math.ceil(np.linalg.norm(p1 - p0) / 1.0)))
                for t in np.linspace(0, 1, n + 1)[1:]:
                    dense_c.append(p0 + (p1 - p0) * t)
            dense_c = np.array(dense_c)
            tags = []
            for p in dense_c:
                best = None
                for b, arr in cand:
                    d2 = (arr[:, 0] - p[0]) ** 2 + (arr[:, 1] - p[1]) ** 2
                    j = int(np.argmin(d2))
                    if best is None or d2[j] < best[0]:
                        best = (d2[j], b, arr[j, 2])
                tags.append((best[1], int(best[2] // CHUNK)))
            start = 0
            for i in range(1, len(dense_c) + 1):
                if i == len(dense_c) or tags[i] != tags[start]:
                    seg = dense_c[max(0, start - 1):i] if start > 0 else dense_c[start:i]
                    if len(seg) >= 2:
                        b, ci = tags[start]
                        lisere_chunks.append({"fragment": fk, "branch": b, "s0": round(ci * CHUNK, 2),
                                              "s1": round(min(length[b], (ci + 1) * CHUNK), 2),
                                              "d": "M" + "L".join(f"{fmt(round(x, 2))} {fmt(round(y, 2))}" for x, y in seg)})
                    start = i
    report["lipWidths"] = stats_lip

    # 5. stress mark at S (f33): a 10 px micro-split along the trunk start + white fibres frayed into the notch
    tp = np.array(dense["trunk"])
    ss = np.array([0.0, 2.5, 5.0, 7.5, 10.0])
    sp = np.stack([np.interp(ss, tp[:, 2], tp[:, 0]), np.interp(ss, tp[:, 2], tp[:, 1])], axis=1)
    tan_f = base_tangent_fn(base["trunk"])
    T0 = tan_f(ss)
    Nn = np.stack([-T0[:, 1], T0[:, 0]], axis=1)
    half = 1.35 * (1 - ss / 10.0)
    # start 1 px outside the paper so the split visibly opens from the notch edge
    root = sp[0] - T0[0] * 1.0
    slit = Polygon([tuple(root + Nn[0] * half[0])] + [tuple(p) for p in (sp + Nn * half[:, None])[1:-1]] + [tuple(sp[-1])]
                   + [tuple(p) for p in (sp - Nn * half[:, None])[1:-1][::-1]] + [tuple(root - Nn[0] * half[0])]).buffer(0)
    slit = slit.intersection(white)
    rng = np.random.default_rng(SEED + 7)
    fibres = []
    for ang, ln, wd in ((-28, 4.2, 0.9), (-6, 5.6, 1.0), (17, 3.6, 0.8), (36, 2.6, 0.7)):
        a = math.radians(180 + ang + rng.uniform(-4, 4))
        dvec = np.array([math.cos(a), math.sin(a)])
        nvec = np.array([-dvec[1], dvec[0]])
        root = np.array(S) + nvec * rng.uniform(-1.2, 1.2) + np.array([0.6, 0])
        tip = root + dvec * ln
        fibres.append(Polygon([root + nvec * wd * 0.5, tip, root - nvec * wd * 0.5]))
    fray = unary_union(fibres).difference(white.buffer(-0.4))
    stress = {
        "frame": 33, "anchor": S, "size_px": 10,
        "slit": {"d": poly_d(slit), "fill": "#4D4D4D", "opacity": 0.75,
                 "note": "micro-split along the first 10 px of the trunk; reads on the white margin"},
        "fibres": {"d": poly_d(fray), "fill": "#FFFFFF", "opacity": 1.0,
                   "note": "white fibres frayed into the notch void; read on dark page backgrounds"},
        "hideAtFrame": 34,
    }

    # 6. transforms + gap widths
    pivots = {"E_R": ER, "E_B": EB}

    def apply_tf(fk, pt, mult=1.0, table="rest"):
        t = TRANSFORMS[fk][table]
        px, py = pivots[TRANSFORMS[fk]["pivot"]]
        th = math.radians(t["rot"] * mult)
        x, y = pt[0] - px, pt[1] - py
        return (x * math.cos(th) - y * math.sin(th) + px + t["tx"] * mult,
                x * math.sin(th) + y * math.cos(th) + py + t["ty"] * mult)

    def gap(fa, fb, pt, table):
        a = apply_tf(fa, pt, 1.0, table)
        b_ = apply_tf(fb, pt, 1.0, table)
        return round(math.dist(a, b_), 1)
    report["openingAtRest_px"] = {"S (F1|F2)": gap("F1", "F2", S, "rest"), "N (F1|F2)": gap("F1", "F2", N, "rest"),
                                  "N (F1|F3)": gap("F1", "F3", N, "rest"), "E_R (F1|F3)": gap("F1", "F3", ER, "rest"),
                                  "N (F2|F3)": gap("F2", "F3", N, "rest"), "E_B (F2|F3)": gap("F2", "F3", EB, "rest")}
    report["openingAtPeak_px"] = {"S (F1|F2)": gap("F1", "F2", S, "peak"), "E_R (F1|F3)": gap("F1", "F3", ER, "peak"),
                                  "E_B (F2|F3)": gap("F2", "F3", EB, "peak")}

    def tf_entry(fk, table):
        t = TRANSFORMS[fk][table]
        px, py = pivots[TRANSFORMS[fk]["pivot"]]
        lum = LUM_REST[fk] * (1.0 if table == "rest" else 1.35)
        return {"rotateDeg": t["rot"], "translatePx": [t["tx"], t["ty"]], t["tilt"][0] + "Deg": t["tilt"][1],
                "luminanceShift": round(lum, 4),
                "svgTransform": f"translate({fmt(t['tx'])} {fmt(t['ty'])}) rotate({fmt(t['rot'])} {fmt(px)} {fmt(py)})",
                "gsap": {"svgOrigin": f"{fmt(px)} {fmt(py)}", "rotation": t["rot"], "x": t["tx"], "y": t["ty"]}}

    # 7. tear.json
    def frag_entry(fk):
        f = frag[fk]
        coords = [[round(x, 3), round(y, 3)] for x, y in np.array(f.exterior.coords)[:-1]]
        return {
            "polygon": coords,
            "d": poly_d(f, 3),
            "paperPieceD": poly_d(paper_piece[fk], 2),
            "greyCopyD": poly_d(grey_copy[fk], 2),
            "areaFractionOfWhitePaper": round(frac[fk], 4),
            "pivotName": TRANSFORMS[fk]["pivot"],
            "pivot": list(pivots[TRANSFORMS[fk]["pivot"]]),
            "rest_x1.00": tf_entry(fk, "rest"),
            "peak_x1.35": tf_entry(fk, "peak"),
            "luminanceSign": "+" if LUM_REST[fk] > 0 else "-",
            "lips": {
                "widthPx": [LIP[fk]["mid"] - LIP[fk]["amp"], LIP[fk]["mid"] + LIP[fk]["amp"]],
                "fill": "#FFFFFF",
                "fullD": poly_d(lips_full[fk], 2),
                "chunks": [{"branch": c["branch"], "s0": c["s0"], "s1": c["s1"], "d": poly_d(c["geom"], 2)} for c in lip_chunks[fk]],
            },
            "lisere": {"stroke": "#4D4D4D", "strokeOpacity": 0.25, "strokeWidth": 1.0, "fullD": line_d(lisere[fk], 2),
                       "chunks": [{k: v for k, v in c.items() if k != "fragment"} for c in lisere_chunks if c["fragment"] == fk]},
        }

    f_N = FRONT_START + length["trunk"] / FRONT_SPEED
    tear = {
        "about": "Marin'Or stamp tear geometry, canvas px @1x (1080x1350, origin top-left). Generated by tools/build_tear.py "
                 f"(seed {SEED}). Spec: SPEC_timbre-marmite.md 6.4/6.5/9.",
        "canvas": {"width": CANVAS_W, "height": CANVAS_H},
        "points": {"S": list(S), "N": list(N), "E_R": list(ER), "E_B": list(EB)},
        "endpointCheck": report["endpoints"],
        "baseVertices": {k: [list(map(float, p)) for p in v] for k, v in base.items()},
        "crack": {b: {"from": "S" if b == "trunk" else "N", "to": {"trunk": "N", "branchA": "E_R", "branchB": "E_B"}[b],
                      "baseLength": round(length[b], 3),
                      "points": [[round(x, 3), round(y, 3)] for x, y, _ in dense[b]],
                      "s": [round(v, 3) for _, _, v in dense[b]],
                      "d": "M" + "L".join(f"{fmt(round(x, 3))} {fmt(round(y, 3))}" for x, y, _ in dense[b])}
                  for b in dense},
        "cutExtensions": {"trunk": [list(S), [EXT["trunk"][0], S[1]], [-20.0, S[1]]],
                          "branchA": [list(ER), [EXT["branchA"][0], ER[1]], [CANVAS_W + 20.0, ER[1]]],
                          "branchB": [list(EB), [EB[0], EXT["branchB"][1]], [EB[0], CANVAS_H + 20.0]]},
        "partitionRect": [0, 0, CANVAS_W, CANVAS_H],
        "paperThicknessOffsetPx": [round(GREY_OFFSET_PX, 3), round(GREY_OFFSET_PX, 3)],
        "stacking": ["F1", "F2", "F3"],
        "fragments": {fk: frag_entry(fk) for fk in ("F1", "F2", "F3")},
        "pictureClip": {"note": "lips/liseré already clipped to vignette rect U printed flame polygons (the original flames overhang the vignette bottom by 7.4 px)",
                        "d": poly_d(picture, 2)},
        "front": {
            "unit": "s = arc length along the BASE (un-noised) polyline of each branch, px; trunk from S, branches from N",
            "trunk": {"startFrame": FRONT_START, "speedPxPerFrame": FRONT_SPEED, "length": round(length["trunk"], 3),
                      "reachesNAtFrame": round(f_N, 4), "formula": "s(f) = clamp(470*(f-33.6), 0, L)"},
            "branchA": {"startFrame": round(f_N, 4), "endFrame": BRANCH_END, "length": round(length["branchA"], 3),
                        "speedPxPerFrame": round(length["branchA"] / (BRANCH_END - f_N), 2),
                        "formula": "s(f) = clamp((f-fN)/(36-fN), 0, 1) * L"},
            "branchB": {"startFrame": round(f_N, 4), "endFrame": BRANCH_END, "length": round(length["branchB"], 3),
                        "speedPxPerFrame": round(length["branchB"] / (BRANCH_END - f_N), 2),
                        "formula": "s(f) = clamp((f-fN)/(36-fN), 0, 1) * L"},
            "frames": {str(f): {"trunk": round(min(length["trunk"], max(0, FRONT_SPEED * (f - FRONT_START))), 2),
                                "branchA": round(min(1, max(0, (f - f_N) / (BRANCH_END - f_N))) * length["branchA"], 2),
                                "branchB": round(min(1, max(0, (f - f_N) / (BRANCH_END - f_N))) * length["branchB"], 2)}
                       for f in (33, 34, 35, 36)},
            "showRule": "show a lip/liseré chunk when front_s[chunk.branch](f) > chunk.s0 (strict) (chunks overlap 1 px: opaque white, no AA seams). "
                        "From f36 on, swap the chunks for fragments.*.lips.fullD / lisere.fullD (single clean paths).",
            "hairline": "optional f34-f35 only (before the fragments move): stroke crack.*.d up to the front, #4D4D4D, 1.2 px, opacity 0.55",
        },
        "spring": {"multipliers": SPRING_MULT, "rule": "rot, translate and tilt/luminance = multiplier x rest values "
                   "(the spec's x1.35 column is the rounded x1.35 of the rest column; use the table values at f38)",
                   "zeta": 0.32, "hz": 10, "stiffness": 3948, "damping": 40.2, "mass": 1},
        "tiltLighting": {"convention": "After Effects right-handed axes (x right, y down, z into screen): +rotY turns the face left, "
                                        "+rotX turns the face down. Key light upper-left (pot shading). Shift = filter brightness(1+L) on the fragment group.",
                         "rest": LUM_REST, "peak": {k: round(v * 1.35, 4) for k, v in LUM_REST.items()}},
        "stressMark": stress,
        "report": report,
    }
    with open(os.path.join(BUILD, "tear.json"), "w") as fjs:
        json.dump(tear, fjs, separators=(",", ":"))

    # 8. previews
    write_previews(tear, frag, lips_full, lisere, base, dense, S, N, ER, EB, notches, white)
    report["chunks"] = {fk: len(lip_chunks[fk]) for fk in lip_chunks}
    report["lisereChunks"] = len(lisere_chunks)
    report["tearJsonBytes"] = os.path.getsize(os.path.join(BUILD, "tear.json"))
    print(json.dumps(report, indent=1, default=float))


# ----------------------------------------------------------------------------------------------
CHECKER = ("background-color:#d6d6d6;background-image:linear-gradient(45deg,#b8b8b8 25%,transparent 25%,transparent 75%,#b8b8b8 75%),"
           "linear-gradient(45deg,#b8b8b8 25%,transparent 25%,transparent 75%,#b8b8b8 75%);background-size:30px 30px;"
           "background-position:0 0,15px 15px;")


def scene_html(body, defs_extra="", bg=CHECKER, w=1080, h=1350, viewbox="0 0 1080 1350"):
    svg = bsp.write_stamp_svg()  # same defs as the shipped file
    defs = bsp.defs_inner(svg).replace("assets/build/glitter.png", "../glitter.png")
    pot = (f'<image id="potOriginal" href="../ref-pot-original-rgba.png" x="{POT_X0:.3f}" y="{POT_Y0:.3f}" '
           f'width="{512 * POT_S:.3f}" height="{512 * POT_S:.3f}" preserveAspectRatio="none"/>')
    picture = ('<g id="pictureFull" style="isolation:isolate"><use href="#vignetteRect"/><use href="#printedFlamesPolys"/>'
               '<use href="#potOriginal"/><use href="#printedGlitter"/></g>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;{bg}}}svg{{display:block}}</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="{viewbox}">
<defs>{defs}{pot}{picture}{defs_extra}</defs>
{body}
</svg></body></html>"""


def fragment_group(fk, fr, transform, lum, lips_d, lisere_d, show_grey=True):
    filt = f' style="filter:brightness({1 + lum:.4f})"' if abs(lum) > 1e-6 else ""
    grey = f'<path d="{fr["greyCopyD"]}" fill="#4D4D4D"/>' if show_grey else ""
    return (f'<g id="frag{fk}" transform="{transform}"{filt}>{grey}'
            f'<g clip-path="url(#clip{fk})"><use href="#paperWhitePath"/><use href="#pictureFull"/></g>'
            f'<path d="{lips_d}" fill="#FFFFFF"/>'
            f'<path d="{lisere_d}" fill="none" stroke="#4D4D4D" stroke-opacity="0.25" stroke-width="1" stroke-linejoin="round" stroke-linecap="round"/>'
            '</g>')


def write_previews(tear, frag, lips_full, lisere, base, dense, S, N, ER, EB, notches, white):
    F = tear["fragments"]
    clips = "".join(f'<clipPath id="clip{k}" clipPathUnits="userSpaceOnUse"><path d="{F[k]["d"]}"/></clipPath>' for k in F)
    jobs = []

    # final (x1.00) and peak (x1.35)
    for name, key in (("final", "rest_x1.00"), ("peak", "peak_x1.35")):
        body = "".join(fragment_group(k, F[k], F[k][key]["svgTransform"], F[k][key]["luminanceShift"],
                                      F[k]["lips"]["fullD"], F[k]["lisere"]["fullD"]) for k in ("F1", "F2", "F3"))
        html = scene_html(body, clips)
        p = os.path.join(PREV, f"tear_preview_{name}.html")
        with open(p, "w") as fh:
            fh.write(html)
        jobs.append({"html": p, "out": os.path.join(BUILD, f"tear_preview_{name}.png"), "width": 1080, "height": 1350, "dpr": 1, "transparent": False})
        # 2x crops for close inspection (scratch only)
        jobs.append({"html": p, "out": os.path.join(SCRATCH, f"tear_{name}_2x.png"), "width": 1080, "height": 1350, "dpr": 2, "transparent": False})

    # f35 reveal check (fragments not moved; stamp master intact underneath; chunks with s0 <= front)
    fr35 = tear["front"]["frames"]["35"]
    chunks = ""
    for k in ("F1", "F2", "F3"):
        ds = [c["d"] for c in F[k]["lips"]["chunks"] if fr35[c["branch"]] > c["s0"]]
        ls = [c["d"] for c in F[k]["lisere"]["chunks"] if fr35[c["branch"]] > c["s0"]]
        chunks += f'<path d="{"".join(ds)}" fill="#FFFFFF"/>'
        chunks += f'<path d="{"".join(ls)}" fill="none" stroke="#4D4D4D" stroke-opacity="0.25" stroke-width="1" stroke-linecap="round"/>'
    tp = np.array(tear["crack"]["trunk"]["points"])
    ts = np.array(tear["crack"]["trunk"]["s"])
    hl = tp[ts <= fr35["trunk"]]
    hair = "M" + "L".join(f"{x:.2f} {y:.2f}" for x, y in hl)
    body = ('<g style="isolation:isolate"><use href="#paperGreyPath"/><use href="#paperWhitePath"/><use href="#pictureFull"/></g>'
            + chunks + f'<path d="{hair}" fill="none" stroke="#4D4D4D" stroke-opacity="0.55" stroke-width="1.2" stroke-linejoin="round"/>')
    p = os.path.join(PREV, "tear_preview_f35.html")
    with open(p, "w") as fh:
        fh.write(scene_html(body))
    jobs.append({"html": p, "out": os.path.join(BUILD, "tear_preview_f35.png"), "width": 1080, "height": 1350, "dpr": 1, "transparent": False})

    # f33 stress mark close-up (scratch, 4x) on white page and on dark page
    sm = tear["stressMark"]
    body = ('<g style="isolation:isolate"><use href="#paperGreyPath"/><use href="#paperWhitePath"/><use href="#pictureFull"/></g>'
            f'<path d="{sm["slit"]["d"]}" fill="#4D4D4D" fill-opacity="{sm["slit"]["opacity"]}"/><path d="{sm["fibres"]["d"]}" fill="#FFFFFF"/>')
    for bgname, bg in (("white", "background:#ffffff;"), ("dark", "background:#1d1d1f;")):
        p = os.path.join(PREV, f"stress_mark_{bgname}.html")
        with open(p, "w") as fh:
            fh.write(scene_html(body, bg=bg, w=200, h=160, viewbox=f"{S[0] - 45:.2f} {S[1] - 40:.2f} 100 80"))
        jobs.append({"html": p, "out": os.path.join(SCRATCH, f"stress_mark_{bgname}.png"), "width": 200, "height": 160, "dpr": 2, "transparent": False})

    # lines preview
    cols = {"F1": "#2F6BFF", "F2": "#18B26B", "F3": "#E0338A"}
    overlay = "".join(f'<path d="{F[k]["d"]}" fill="{cols[k]}" fill-opacity="0.22" stroke="{cols[k]}" stroke-width="1.5"/>' for k in F)
    lips_ov = "".join(f'<path d="{F[k]["lips"]["fullD"]}" fill="#FFFFFF" fill-opacity="0.9"/>' for k in F)
    cracks = "".join(f'<path d="{tear["crack"][b]["d"]}" fill="none" stroke="#111" stroke-width="2.2" stroke-linejoin="round"/>' for b in tear["crack"])
    basel = "".join('<polyline points="' + " ".join(f"{x},{y}" for x, y in base[b]) + '" fill="none" stroke="#FFD400" stroke-width="1" stroke-dasharray="4 3"/>' for b in base)
    exts = "".join('<polyline points="' + " ".join(f"{x},{y}" for x, y in tear["cutExtensions"][b][:2]) + '" fill="none" stroke="#FF3B30" stroke-width="2"/>' for b in tear["cutExtensions"])
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="#FF3B30" stroke-width="2"/>' for x, y in (S, ER, EB))
    dots += f'<circle cx="{N[0]}" cy="{N[1]}" r="5" fill="#111"/>'
    dots += "".join(f'<circle cx="{n["pt"][0]:.2f}" cy="{n["pt"][1]:.2f}" r="1.6" fill="#FF3B30"/>' for n in notches)
    body = ('<g style="isolation:isolate"><use href="#paperGreyPath"/><use href="#paperWhitePath"/><use href="#pictureFull"/></g>'
            + overlay + lips_ov + basel + cracks + exts + dots)
    p = os.path.join(PREV, "tear_preview_lines.html")
    with open(p, "w") as fh:
        fh.write(scene_html(body, bg="background:#ffffff;"))
    jobs.append({"html": p, "out": os.path.join(BUILD, "tear_preview_lines.png"), "width": 1080, "height": 1350, "dpr": 1, "transparent": False})

    jp = os.path.join(SCRATCH, "render_jobs_tear.json")
    with open(jp, "w") as fh:
        json.dump(jobs, fh)
    subprocess.run(["node", os.path.join(ROOT, "tools", "render_html.mjs"), "--batch", jp], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
