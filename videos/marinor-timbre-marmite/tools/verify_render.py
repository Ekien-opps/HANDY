#!/usr/bin/env python3
"""Numeric QA of a rendered PNG sequence + contact sheet (deterministic).

    python3 tools/verify_render.py [renders/check_png] [--sheet snapshots/contact-sheet.jpg]

Checks (spec section 9 + brief):
  1. 60 frames, RGBA, 1080x1350
  2. alpha == 0 outside the paper silhouette bbox (+8 px) for f0-f35
  3. f28-f59: no flame-coloured pixel inside the pot opening / under the lid
  4. f1-f32: stamp outside the vignette identical to f0 (and the whole stamp outside the moving pot region)
  5. containment: f0-f32 every pixel that differs from f0 lies inside the vignette, and none in the 24 px
     safe band (excluding the static printed flames that are identical anyway)
  6. f0 vs reference-full-render.png, composited over white at the reference scale: mean |dRGB|
  7. motion-blur stack drift: static vignette corners identical to f0 on every frame f0-f32
Writes the contact sheet (10 x 6, all 60 frames over a mid-grey checkerboard, no text).
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "assets", "build")
SRC = os.path.join(ROOT, "assets", "src")

VIG = (136.146, 160.596, 937.686, 1177.866)
SAFE = (160.1, 184.6, 913.7, 1153.9)
PAPER = (74.55, 99.0, 999.3 + 6.156, 1239.6 + 6.156)
OX, OY, SCALE = 74.55, 99.0, 1.8
REF_K = 371.085 / 445.3
REF_AX = 313.03 - 34.22 * REF_K
REF_AY = 44.327 - 34.22 * REF_K


def load(d, i):
    return np.asarray(Image.open(os.path.join(d, f"frame_{i + 1:06d}.png")))


def flame_mask(rgb):
    r, g, b = (rgb[..., k].astype(int) for k in range(3))
    return (r > 200) & (b < 110) & (r - b > 130) & (g > 60)


def checker(w, h, s=24):
    yy, xx = np.mgrid[0:h, 0:w]
    c = ((xx // s + yy // s) % 2).astype(np.float64)
    v = 128 + 20 * (c - 0.5)
    return np.dstack([v, v, v])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", nargs="?", default=os.path.join(ROOT, "renders", "check_png"))
    ap.add_argument("--sheet", default=os.path.join(ROOT, "snapshots", "contact-sheet.jpg"))
    a = ap.parse_args()
    files = sorted(f for f in os.listdir(a.dir) if f.endswith(".png"))
    rep = {"frames": len(files)}
    frames = [load(a.dir, i) for i in range(len(files))]
    rep["shape_ok"] = all(f.shape == (1350, 1080, 4) for f in frames)

    # 2. alpha outside paper bbox
    m = np.ones((1350, 1080), bool)
    x0, y0, x1, y1 = PAPER
    m[int(np.floor(y0 - 8)):int(np.ceil(y1 + 8)), int(np.floor(x0 - 8)):int(np.ceil(x1 + 8))] = False
    rep["alpha_outside_paper_bbox_max_f0_35"] = int(max(f[..., 3][m].max() for f in frames[:36]))
    rep["alpha_outside_paper_bbox_max_f36_59"] = int(max(f[..., 3][m].max() for f in frames[36:]))

    # 3. no fire after f28 in the pot opening / under the lid (rest lid bbox + rim ellipse, generous)
    pot = json.load(open(os.path.join(BUILD, "pot.json")))
    yy, xx = np.mgrid[0:1350, 0:1080]
    rim = pot["rim_ellipse"]
    ell = ((xx + 0.5 - rim["cx"]) / (rim["rx"] + 20)) ** 2 + ((yy + 0.5 - rim["cy"]) / (rim["ry"] + 20)) ** 2 <= 1
    lb = pot["lid_bbox"]
    lidbox = (xx >= lb[0] - 20) & (xx <= lb[2] + 20) & (yy >= lb[1] - 40) & (yy <= lb[3] + 10)
    region = ell | lidbox
    fire_counts = {i: int((flame_mask(frames[i][..., :3]) & region & (frames[i][..., 3] > 0)).sum()) for i in range(28, 60)}
    rep["fire_px_in_pot_f28_59_max"] = max(fire_counts.values())
    rep["fire_px_in_pot_f27"] = int((flame_mask(frames[27][..., :3]) & region).sum())

    # 4. outside the vignette identical to f0 up to f32
    out_v = np.ones((1350, 1080), bool)
    out_v[int(VIG[1]) - 1:int(np.ceil(VIG[3])) + 1, int(VIG[0]) - 1:int(np.ceil(VIG[2])) + 1] = False
    f0 = frames[0].astype(int)
    rep["outside_vignette_maxdiff_f1_32"] = int(max(np.abs(frames[i].astype(int) - f0)[out_v].max() for i in range(1, 33)))

    # 5. containment: changed pixels vs f0 must avoid the safe band
    safe_band = np.zeros((1350, 1080), bool)
    vx0, vy0, vx1, vy1 = (int(np.floor(VIG[0])), int(np.floor(VIG[1])), int(np.ceil(VIG[2])), int(np.ceil(VIG[3])))
    safe_band[vy0:vy1, vx0:vx1] = True
    safe_band[int(np.ceil(SAFE[1])):int(SAFE[3]), int(np.ceil(SAFE[0])):int(SAFE[2])] = False
    band = {}
    for i in range(1, 33):
        d = np.abs(frames[i].astype(int) - f0).max(axis=2) > 2
        band[i] = int((d & safe_band).sum())
    rep["changed_px_in_safe_band_f1_32"] = {k: v for k, v in band.items() if v}
    bb = {}
    for i in range(1, 33):
        d = np.abs(frames[i].astype(int) - f0).max(axis=2) > 2
        if d.any():
            ys, xs = np.nonzero(d)
            bb[i] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    rep["changed_bbox_f1_32_union"] = [min(v[0] for v in bb.values()), min(v[1] for v in bb.values()),
                                       max(v[2] for v in bb.values()), max(v[3] for v in bb.values())]

    # 7. static corners (blur stack drift)
    corners = [(150, 175), (925, 175), (150, 1165), (925, 1165), (200, 300), (850, 300), (160, 700)]
    rep["static_corner_maxdiff_f0_32"] = int(max(np.abs(frames[i][y, x, :3].astype(int) - f0[y, x, :3]).max()
                                                 for i in range(33) for (x, y) in corners))

    # 6. f0 vs reference at the reference scale, over white
    rgba = frames[0].astype(np.float64) / 255
    white = rgba[..., :3] * rgba[..., 3:4] + (1 - rgba[..., 3:4])
    s = REF_K / SCALE
    bx0 = OX - REF_AX / s
    by0 = OY - REF_AY / s
    pad = 700
    big = np.ones((1350 + 2 * pad, 1080 + 2 * pad, 3))
    big[pad:pad + 1350, pad:pad + 1080] = white
    im = Image.fromarray(np.clip(big * 255 + 0.5, 0, 255).astype(np.uint8))
    box = (bx0 + pad, by0 + pad, bx0 + pad + 1000 / s, by0 + pad + 563 / s)
    got = np.asarray(im.resize((1000, 563), Image.LANCZOS, box=box)).astype(np.float64)
    ref = np.asarray(Image.open(os.path.join(SRC, "reference-full-render.png")).convert("RGB")).astype(np.float64)
    d = np.abs(got - ref)
    rep["ref_mean_abs_diff"] = round(float(d.mean()), 3)
    # inside the stamp only (paper bbox at reference scale)
    rx0, ry0 = REF_AX + s * (PAPER[0] - OX), REF_AY + s * (PAPER[1] - OY)
    rx1, ry1 = REF_AX + s * (PAPER[2] - OX), REF_AY + s * (PAPER[3] - OY)
    sub = d[int(ry0):int(ry1), int(rx0):int(rx1)]
    rep["ref_mean_abs_diff_stamp_bbox"] = round(float(sub.mean()), 3)
    rep["ref_p99_stamp_bbox"] = round(float(np.percentile(sub.max(axis=2), 99)), 1)
    Image.fromarray(np.hstack([ref, got, 255 - np.clip(d * 4, 0, 255)]).astype(np.uint8)).save(
        os.path.join(ROOT, "snapshots", "f0_vs_reference.png"))

    # contact sheet
    tw, th = 216, 270
    bg = checker(tw, th, 12)
    sheet = np.zeros((6 * th, 10 * tw, 3))
    for i, f in enumerate(frames[:60]):
        t = np.asarray(Image.fromarray(f).resize((tw, th), Image.LANCZOS)).astype(np.float64) / 255
        comp = t[..., :3] * 255 * t[..., 3:4] + bg * (1 - t[..., 3:4])
        r, c = divmod(i, 10)
        sheet[r * th:(r + 1) * th, c * tw:(c + 1) * tw] = comp
    os.makedirs(os.path.dirname(a.sheet), exist_ok=True)
    Image.fromarray(np.clip(sheet + 0.5, 0, 255).astype(np.uint8)).save(a.sheet, quality=92)
    rep["sheet"] = os.path.relpath(a.sheet, ROOT)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
