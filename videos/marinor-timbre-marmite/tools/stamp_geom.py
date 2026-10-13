"""Shared geometry for the Marin'Or stamp: parse the Illustrator source SVG, convert to canvas px.

Canvas (@1x, 1080 x 1350):   x_px = 74.55 + 1.8 * x_u ;  y_px = 99 + 1.8 * y_u
Pot raster (512 px) -> canvas: x_px = 162.44 + 1.44 * rx ; y_px = 360.45 + 1.44 * ry
"""
import os
import re

import numpy as np
from shapely.geometry import Polygon

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "src")
BUILD = os.path.join(ROOT, "assets", "build")
SCRATCH = "/tmp/claude-0/-home-user-HANDY/180e27e0-1c8f-56c9-a284-57d2bdc0b1f3/scratchpad"

SCALE = 1.8
OX, OY = 74.55, 99.0
CANVAS_W, CANVAS_H = 1080, 1350
GREY_OFFSET_U = 3.42                     # grey paper = white paper translated by (3.42, 3.42) u
GREY_OFFSET_PX = GREY_OFFSET_U * SCALE   # 6.156 px

POT_X0, POT_Y0, POT_S = OX + SCALE * 48.83, OY + SCALE * 145.25, SCALE * 0.8  # 162.444, 360.45, 1.44


def u2c(x, y):
    return OX + SCALE * x, OY + SCALE * y


def fmt(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_TOK = re.compile(r"[MmLlHhVvCcSsQqZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def parse_path(d):
    """Return a list of absolute segments in source units:
    ('M', (x,y)), ('L', (x,y)), ('C', (x1,y1),(x2,y2),(x,y)), ('Z',)."""
    toks = _TOK.findall(d)
    out = []
    i = 0
    cx = cy = 0.0
    sx = sy = 0.0
    cmd = None
    last_c2 = None

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        t = toks[i]
        if re.fullmatch(r"[A-Za-z]", t):
            cmd = t
            i += 1
            if cmd in "Zz":
                out.append(("Z",))
                cx, cy = sx, sy
                last_c2 = None
                continue
        rel = cmd.islower()
        c = cmd.upper()
        if c == "M":
            x, y = num(), num()
            if rel:
                x, y = cx + x, cy + y
            out.append(("M", (x, y)))
            cx, cy = sx, sy = x, y
            cmd = "l" if rel else "L"
            last_c2 = None
        elif c == "L":
            x, y = num(), num()
            if rel:
                x, y = cx + x, cy + y
            out.append(("L", (x, y)))
            cx, cy = x, y
            last_c2 = None
        elif c == "H":
            x = num()
            if rel:
                x = cx + x
            out.append(("L", (x, cy)))
            cx = x
            last_c2 = None
        elif c == "V":
            y = num()
            if rel:
                y = cy + y
            out.append(("L", (cx, y)))
            cy = y
            last_c2 = None
        elif c == "C":
            x1, y1, x2, y2, x, y = (num() for _ in range(6))
            if rel:
                x1, y1, x2, y2, x, y = cx + x1, cy + y1, cx + x2, cy + y2, cx + x, cy + y
            out.append(("C", (x1, y1), (x2, y2), (x, y)))
            last_c2 = (x2, y2)
            cx, cy = x, y
        elif c == "S":
            x2, y2, x, y = (num() for _ in range(4))
            if rel:
                x2, y2, x, y = cx + x2, cy + y2, cx + x, cy + y
            x1, y1 = (2 * cx - last_c2[0], 2 * cy - last_c2[1]) if last_c2 else (cx, cy)
            out.append(("C", (x1, y1), (x2, y2), (x, y)))
            last_c2 = (x2, y2)
            cx, cy = x, y
        else:
            raise ValueError("unsupported path command " + cmd)
    return out


def transform_segments(segs, fx):
    res = []
    for s in segs:
        if s[0] == "Z":
            res.append(s)
        else:
            res.append((s[0],) + tuple(fx(*p) for p in s[1:]))
    return res


def segments_to_d(segs):
    parts = []
    for s in segs:
        if s[0] == "Z":
            parts.append("Z")
        elif s[0] in "ML":
            parts.append(f"{s[0]}{fmt(s[1][0])} {fmt(s[1][1])}")
        else:
            parts.append("C" + " ".join(f"{fmt(p[0])} {fmt(p[1])}" for p in s[1:]))
    return "".join(parts)


def flatten(segs, step=0.35):
    """Polyline approximation (list of rings) of the absolute segments."""
    rings, cur = [], []
    pos = None
    for s in segs:
        if s[0] == "M":
            if len(cur) > 2:
                rings.append(cur)
            cur = [s[1]]
            pos = s[1]
        elif s[0] == "L":
            cur.append(s[1])
            pos = s[1]
        elif s[0] == "C":
            p0 = np.array(pos)
            p1, p2, p3 = (np.array(p) for p in s[1:])
            est = np.linalg.norm(p1 - p0) + np.linalg.norm(p2 - p1) + np.linalg.norm(p3 - p2)
            n = max(4, int(np.ceil(est / step)))
            t = np.linspace(0, 1, n + 1)[1:, None]
            pts = ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3
            cur.extend(map(tuple, pts))
            pos = s[3]
        elif s[0] == "Z":
            pass
    if len(cur) > 2:
        rings.append(cur)
    return rings


def bezier_point(p0, p1, p2, p3, t):
    p0, p1, p2, p3 = (np.array(p, float) for p in (p0, p1, p2, p3))
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


def load_source():
    with open(os.path.join(SRC, "stamp-source.svg"), encoding="utf-8") as f:
        txt = f.read()
    paths = re.findall(r'<path class="(cls-\d)" d="([^"]+)"', txt)
    d = {cls: dd for cls, dd in paths}
    grey_d, white_d = d["cls-4"], d["cls-3"]
    m = re.search(r'<rect class="cls-7" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', txt)
    rect = tuple(float(v) for v in m.groups())
    grads = {}
    for gm in re.finditer(r'<linearGradient id="([^"]+)"[^>]*?x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"[^>]*>(.*?)</linearGradient>', txt, re.S):
        gid = gm.group(1)
        coords = tuple(float(v) for v in gm.groups()[1:5])
        stops = re.findall(r'<stop offset="([\d.]+)" stop-color="(#[0-9a-fA-F]{6})"', gm.group(6))
        grads[gid] = (coords, [(s, c) for s, c in stops])
    polys = re.findall(r'<polygon class="(cls-\d)" points="([^"]+)"', txt)
    glit = re.search(r'<image width="352" height="207" transform="translate\(([\d.]+) ([\d.]+)\)"', txt)
    pot = re.search(r'<image width="512" height="512" transform="translate\(([\d.]+) ([\d.]+)\) scale\(([\d.]+)\)"', txt)
    return {
        "grey_d": grey_d,
        "white_d": white_d,
        "rect": rect,
        "grads": grads,
        "polys": polys,
        "glitter_xy": (float(glit.group(1)), float(glit.group(2))),
        "pot_tf": tuple(float(v) for v in pot.groups()),
    }


def canvas_segments(d):
    return transform_segments(parse_path(d), u2c)


def paper_polygon(which="white", step=0.35):
    src = load_source()
    segs = canvas_segments(src[which + "_d"])
    rings = flatten(segs, step)
    poly = Polygon(rings[0]).buffer(0)
    return poly, segs


def vignette_rect_px():
    x, y, w, h = load_source()["rect"]
    x0, y0 = u2c(x, y)
    return x0, y0, w * SCALE, h * SCALE
