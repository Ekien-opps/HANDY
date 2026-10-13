#!/usr/bin/env python3
"""Generate the HyperFrames composition index.html (deterministic, re-runnable, ~1 s).

    python3 tools/build_index.py [--nmax 16]

Inputs : tools/index.template.html (markup + runtime JS, the file to edit by hand)
         assets/build/stamp-parts.svg (stamp defs), assets/build/flame.json (per-frame flame geometry),
         assets/build/pot.json (rig geometry), tools/inline_tear.py (compact tear data / defs)
Outputs: index.html, assets/build/flame_glitter_tile.png
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inline_tear import tear_payload, rnd  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "assets", "build")
SRC = os.path.join(ROOT, "assets", "src")

OUTLINE_R = 30.3      # px; measured original sticker outline = 30.5 px round offset (union AA adds ~0.2 px)
OUTLINE_N = 36        # offsets on the circle (max radial shortfall r(1-cos(pi/N)) = 0.12 px)


def stamp_defs():
    s = open(os.path.join(BUILD, "stamp-parts.svg"), encoding="utf-8").read()
    inner = s[s.index("<defs>") + 6: s.index("</defs>")]
    # xlink:href duplicates are not needed in HTML5 inline SVG
    import re
    inner = re.sub(r'\s+xlink:href="[^"]*"', "", inner)
    return inner.strip()


def glitter_tile():
    """Largest axis-aligned rectangle of the stamp glitter fully inside its mask (texture is white outside)."""
    rgb = np.asarray(Image.open(os.path.join(SRC, "glitter-rgb.png")).convert("RGB"))
    m = np.asarray(Image.open(os.path.join(SRC, "glitter-mask.png")).convert("L")) >= 250
    best = (0, 0, 0, 0, 0)
    H, W = m.shape
    for y0 in range(H):
        col = np.ones(W, bool)
        for y1 in range(y0, H):
            col &= m[y1]
            if not col.any():
                break
            run = 0
            for x in range(W + 1):
                if x < W and col[x]:
                    run += 1
                else:
                    area = run * (y1 - y0 + 1)
                    if area > best[0] and run >= 24 and (y1 - y0) >= 24:
                        best = (area, x - run, y0, x, y1 + 1)
                    run = 0
    _, x0, y0, x1, y1 = best
    tile = rgb[y0 + 1:y1 - 1, x0 + 1:x1 - 1]
    Image.fromarray(tile).save(os.path.join(BUILD, "flame_glitter_tile.png"))
    return tile.shape[1] * 1.8, tile.shape[0] * 1.8


def outline_filter():
    prims = []
    merge = ['<feMergeNode in="SourceAlpha"/>']
    for i in range(OUTLINE_N):
        a = 2 * math.pi * i / OUTLINE_N
        prims.append(f'<feOffset in="SourceAlpha" dx="{rnd(OUTLINE_R * math.cos(a), 3)}" dy="{rnd(OUTLINE_R * math.sin(a), 3)}" result="o{i}"/>')
        merge.append(f'<feMergeNode in="o{i}"/>')
    return ('<filter id="olF" filterUnits="userSpaceOnUse" x="0" y="0" width="1080" height="1350" '
            'color-interpolation-filters="sRGB">' + "".join(prims) + '<feMerge result="u">' + "".join(merge) +
            '</feMerge><feFlood flood-color="#FFFFFF" result="w"/><feComposite in="w" in2="u" operator="in"/></filter>')


def copy_markup(k):
    """One motion-blur copy of the opaque PICTURE (vignette ... printed glitter)."""
    hide = ' style="isolation:isolate;display:none"' if k else ' style="isolation:isolate"'
    lid_outline = ('<g class="lid"><g class="lus"><use href="#imLidUnder"/></g><use href="#imLid"/>'
                   '<g class="knob"><use href="#imKnob"/></g></g>')
    return (
        f'<g id="pic{k}" class="pic"{hide}>'
        # vignette fill extended 4 px past the clip so every copy is fully opaque inside #vignetteClip
        # (the 1/k stacking is an exact average only for opaque copies; the clip on PICTURE gives the AA edge)
        '<rect x="132.146" y="156.596" width="809.54" height="1025.27" fill="url(#vignetteGrad)"/>'
        '<use href="#printedFlamesPolys"/>'
        f'<g filter="url(#olF)"><g class="sq"><use href="#imBack"/><use href="#imHandleR"/><use href="#imFront"/>{lid_outline}</g></g>'
        '<g class="sq"><use href="#imBack"/>'
        '<use class="heatBack" href="#imBack" filter="url(#heatBackF)" mask="url(#heatMask)" opacity="0"/>'
        '<use class="slitBack" href="#imBack" filter="url(#slitF)" mask="url(#slitMask)" opacity="0"/>'
        '<use href="#imHandleR"/></g>'
        '<use href="#flameG"/>'
        '<g class="sq"><use href="#imFront"/>'
        '<g class="lid"><g class="lus"><use href="#imLidUnder"/>'
        '<use class="heatUnder" href="#imLidUnder" filter="url(#heatUnderF)" opacity="0"/>'
        '<use class="slitUnder" href="#imLidUnder" filter="url(#slitF)" opacity="0"/></g>'
        '<use href="#imLid"/><use class="heatLid" href="#imLid" filter="url(#heatLidF)" mask="url(#lidHeatMask)" opacity="0"/>'
        '<g class="knob"><use href="#imKnob"/></g></g></g>'
        '<use href="#printedGlitter"/>'
        '</g>'
    )


def flame_data():
    fj = json.load(open(os.path.join(BUILD, "flame.json")))
    out = {}
    for f in range(9, 28):
        fr = fj["frames"][str(f)]
        layers = {}
        for name in ("out", "mid", "core"):
            flat = []
            for x, y in fr["layers"][name]:
                flat += [round(x, 2), round(y, 2)]
            layers[name] = flat
        out[f] = {"sx": fr["scaleX"], "sy": fr["scaleY"], **layers}
    g = fj["meta"]["layers"]["out"]["fill"]
    grad = {"x1": g["x1"], "y1": g["y1"], "x2": g["x2"], "y2": g["y2"], "stops": g["stops"]}
    return out, grad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=32, help="max motion-blur sub-frame copies")
    a = ap.parse_args()

    pot = json.load(open(os.path.join(BUILD, "pot.json")))
    tear_defs, stress, tear_data = tear_payload()
    flame, grad = flame_data()
    gw, gh = glitter_tile()

    data = {
        "nmax": a.nmax,
        "H": pot["hinge_H"], "C": pot["lid_center_C"], "KB": pot["knob_base"], "B": pot["squash_anchor_B"],
        "E": pot["emission_E"],
        "lidFree": round(pot["lid_under_ellipse"]["cx"] + pot["lid_under_ellipse"]["rx"], 2),
        "flame": flame,
        "tear": tear_data,
    }
    grad_svg = (f'<linearGradient id="flGrad" gradientUnits="userSpaceOnUse" x1="{grad["x1"]}" y1="{grad["y1"]}" '
                f'x2="{grad["x2"]}" y2="{grad["y2"]}">' +
                "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in grad["stops"]) + "</linearGradient>")
    tpl = open(os.path.join(ROOT, "tools", "index.template.html"), encoding="utf-8").read()
    rep = {
        "<!--@STAMP_DEFS@-->": stamp_defs(),
        "<!--@OUTLINE_FILTER@-->": outline_filter(),
        "<!--@FLAME_GRAD@-->": grad_svg,
        "<!--@GLITTER_PATTERN@-->": (f'<pattern id="glitPat" patternUnits="userSpaceOnUse" width="{rnd(gw, 3)}" height="{rnd(gh, 3)}">'
                                     f'<image href="assets/build/flame_glitter_tile.png" width="{rnd(gw, 3)}" height="{rnd(gh, 3)}" '
                                     f'preserveAspectRatio="none"/></pattern>'),
        "<!--@TEAR_DEFS@-->": tear_defs,
        "<!--@STRESS@-->": stress,
        "<!--@COPIES@-->": "".join(copy_markup(k) for k in range(a.nmax)),
        "/*@DATA@*/null": json.dumps(data, separators=(",", ":")),
    }
    for k, v in rep.items():
        if k not in tpl:
            raise SystemExit(f"placeholder missing in template: {k}")
        tpl = tpl.replace(k, v)
    out = os.path.join(ROOT, "index.html")
    open(out, "w", encoding="utf-8").write(tpl)
    print(f"index.html {len(tpl) / 1024:.1f} KB, nmax {a.nmax}")


if __name__ == "__main__":
    main()
