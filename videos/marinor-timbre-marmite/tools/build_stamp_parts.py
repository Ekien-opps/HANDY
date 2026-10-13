#!/usr/bin/env python3
"""Build assets/build/stamp-parts.svg (stamp artwork in canvas px), assets/build/glitter.png,
assets/build/ref-pot-original-rgba.png, and a Chromium check against reference-full-render.png.

Re-runnable and deterministic:  (cd PROJECT && python3 tools/build_stamp_parts.py)
"""
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stamp_geom import (BUILD, OX, OY, ROOT, SCALE, SCRATCH, SRC, POT_S, POT_X0, POT_Y0,  # noqa: E402
                        canvas_segments, fmt, load_source, segments_to_d, u2c)

PREV = os.path.join(BUILD, "previews")


def build_glitter():
    rgb = Image.open(os.path.join(SRC, "glitter-rgb.png")).convert("RGB")
    mask = Image.open(os.path.join(SRC, "glitter-mask.png")).convert("L")
    a = np.array(rgb)
    m = np.array(mask)
    # Outside the mask the RGB was flattened on white; a white pixel in screen mode would paint white,
    # so the mask is required. Keep un-masked pixels black (neutral for screen) to avoid white fringes
    # when Chrome filters the upscaled image.
    a[m == 0] = 0
    rgba = np.dstack([a, m])
    Image.fromarray(rgba, "RGBA").save(os.path.join(BUILD, "glitter.png"), optimize=True)


def build_pot_ref():
    rgb = Image.open(os.path.join(SRC, "pot-rgb-512.png")).convert("RGB")
    mask = Image.open(os.path.join(SRC, "pot-mask-512.png")).convert("L")
    rgba = rgb.copy()
    rgba.putalpha(mask)
    rgba.save(os.path.join(BUILD, "ref-pot-original-rgba.png"), optimize=True)


def grad_xml(gid, coords, stops):
    x1, y1 = u2c(coords[0], coords[1])
    x2, y2 = u2c(coords[2], coords[3])
    s = "".join(f'<stop offset="{float(o):g}" stop-color="{c.upper()}"/>' for o, c in stops)
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{fmt(x1)}" y1="{fmt(y1)}" '
            f'x2="{fmt(x2)}" y2="{fmt(y2)}">{s}</linearGradient>')


def poly_points(pts_str):
    v = [float(t) for t in pts_str.split()]
    pts = [u2c(v[i], v[i + 1]) for i in range(0, len(v), 2)]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in pts)


def stamp_defs(glitter_href="assets/build/glitter.png"):
    src = load_source()
    g = src["grads"]
    gids = list(g.keys())
    vig_id = [k for k in gids if k.endswith("27")][0]
    a_id = [k for k in gids if k.endswith("13")][0]   # class cls-2 -> left polygon
    b_id = [k for k in gids if k.endswith("14")][0]   # class cls-1 -> right polygon
    rx, ry, rw, rh = src["rect"]
    x0, y0 = u2c(rx, ry)
    w, h = rw * SCALE, rh * SCALE
    polys = {cls: pts for cls, pts in src["polys"]}
    gx, gy = u2c(*src["glitter_xy"])
    grey_d = segments_to_d(canvas_segments(src["grey_d"]))
    white_d = segments_to_d(canvas_segments(src["white_d"]))
    rect_attr = f'x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(w)}" height="{fmt(h)}"'
    defs = [
        grad_xml("vignetteGrad", *g[vig_id]),
        grad_xml("pfGradA", *g[a_id]),
        grad_xml("pfGradB", *g[b_id]),
        f'<path id="paperGreyPath" fill="#4D4D4D" d="{grey_d}"/>',
        f'<path id="paperWhitePath" fill="#FFFFFF" d="{white_d}"/>',
        f'<rect id="vignetteRect" {rect_attr} fill="url(#vignetteGrad)"/>',
        f'<clipPath id="vignetteClip" clipPathUnits="userSpaceOnUse"><rect {rect_attr}/></clipPath>',
        '<g id="printedFlamesPolys">'
        f'<polygon fill="url(#pfGradA)" points="{poly_points(polys["cls-2"])}"/>'
        f'<polygon fill="url(#pfGradB)" points="{poly_points(polys["cls-1"])}"/>'
        '</g>',
        '<g id="printedGlitter" style="mix-blend-mode:screen">'
        f'<image href="{glitter_href}" xlink:href="{glitter_href}" x="{fmt(gx)}" y="{fmt(gy)}" '
        f'width="{fmt(352 * SCALE)}" height="{fmt(207 * SCALE)}" preserveAspectRatio="none"/>'
        '</g>',
        # Self-contained picture minus the pot: the glitter screens onto the opaque vignette inside
        # this isolated group. When the pot is layered in, rebuild the same stack with the pot between
        # #printedFlamesPolys and #printedGlitter (as in the original artwork).
        '<g id="printedFlames" style="isolation:isolate">'
        '<use href="#vignetteRect" xlink:href="#vignetteRect"/>'
        '<use href="#printedFlamesPolys" xlink:href="#printedFlamesPolys"/>'
        '<use href="#printedGlitter" xlink:href="#printedGlitter"/>'
        '</g>',
    ]
    return defs


def write_stamp_svg():
    defs = stamp_defs()
    body = (
        '<g id="stampAtRestNoPot" style="isolation:isolate">'
        '<use href="#paperGreyPath" xlink:href="#paperGreyPath"/>'
        '<use href="#paperWhitePath" xlink:href="#paperWhitePath"/>'
        '<use href="#vignetteRect" xlink:href="#vignetteRect"/>'
        '<use href="#printedFlamesPolys" xlink:href="#printedFlamesPolys"/>'
        '<!-- the pot goes here (canvas x 162.444, y 360.45, 737.28 x 737.28) -->'
        '<use href="#printedGlitter" xlink:href="#printedGlitter"/>'
        '</g>'
    )
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!-- Marin\'Or Ivoire stamp parts, canvas px @1x (1080x1350). Generated by tools/build_stamp_parts.py.\n'
        '     Source u -> canvas: x = 74.55 + 1.8*x_u ; y = 99 + 1.8*y_u. Glitter href is relative to the\n'
        '     composition root (index.html); inline these defs into the composition to use them. -->\n'
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 1080 1350" width="1080" height="1350">\n'
        '<defs>\n' + "\n".join(defs) + '\n</defs>\n' + body + '\n</svg>\n'
    )
    with open(os.path.join(BUILD, "stamp-parts.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    return svg


def defs_inner(svg):
    return svg[svg.index("<defs>") + 6: svg.index("</defs>")]


# reference-full-render.png is the 16:9 artboard at 1/1.2 px per u. Vignette edges measured on the
# reference (anti-aliasing coverage): left 313.03, right 684.115, top 44.327 -> k = 371.085/445.3.
REF_K = 371.085 / 445.3
REF_AX = 313.03 - 34.22 * REF_K
REF_AY = 44.327 - 34.22 * REF_K


def check_html(svg, out_html):
    # canvas px -> reference px: ref = A + K*(c - O)/1.8
    k = REF_K / SCALE
    tx = REF_AX - k * OX
    ty = REF_AY - k * OY
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:#fff;width:1000px;height:563px;overflow:hidden}}svg{{display:block}}</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="563" viewBox="0 0 1000 563">
<defs>{defs_inner(svg).replace('assets/build/glitter.png', '../glitter.png')}</defs>
<g transform="matrix({k:.8f} 0 0 {k:.8f} {tx:.5f} {ty:.5f})"><g style="isolation:isolate">
<use href="#paperGreyPath"/><use href="#paperWhitePath"/><use href="#vignetteRect"/><use href="#printedFlamesPolys"/>
<image href="../ref-pot-original-rgba.png" x="{POT_X0:.3f}" y="{POT_Y0:.3f}" width="{512 * POT_S:.3f}" height="{512 * POT_S:.3f}" preserveAspectRatio="none"/>
<use href="#printedGlitter"/>
</g></g></svg></body></html>"""
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)


def canvas_html(svg, out_html, checker=True):
    bg = ("background-color:#d9d9d9;background-image:linear-gradient(45deg,#bfbfbf 25%,transparent 25%,transparent 75%,#bfbfbf 75%),"
          "linear-gradient(45deg,#bfbfbf 25%,transparent 25%,transparent 75%,#bfbfbf 75%);background-size:32px 32px;"
          "background-position:0 0,16px 16px;") if checker else "background:transparent;"
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1080px;height:1350px;overflow:hidden;{bg}}}svg{{display:block}}</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1350" viewBox="0 0 1080 1350">
<defs>{defs_inner(svg).replace('assets/build/glitter.png', '../glitter.png')}</defs>
<g style="isolation:isolate">
<use href="#paperGreyPath"/><use href="#paperWhitePath"/><use href="#vignetteRect"/><use href="#printedFlamesPolys"/>
<image href="../ref-pot-original-rgba.png" x="{POT_X0:.3f}" y="{POT_Y0:.3f}" width="{512 * POT_S:.3f}" height="{512 * POT_S:.3f}" preserveAspectRatio="none"/>
<use href="#printedGlitter"/>
</g></svg></body></html>"""
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)


def render(jobs):
    jp = os.path.join(SCRATCH, "render_jobs_stamp.json")
    with open(jp, "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", os.path.join(ROOT, "tools", "render_html.mjs"), "--batch", jp], check=True, cwd=ROOT)


def compare():
    ref = np.array(Image.open(os.path.join(SRC, "reference-full-render.png")).convert("RGB")).astype(float)
    got = np.array(Image.open(os.path.join(BUILD, "stamp_check_ref-scale.png")).convert("RGB")).astype(float)
    d = np.abs(ref - got)
    dm = d.max(axis=2)
    stats = {
        "mean_abs_diff_0_255": round(float(d.mean()), 3),
        "p99_abs_diff": round(float(np.percentile(dm, 99)), 2),
        "p999_abs_diff": round(float(np.percentile(dm, 99.9)), 2),
        "frac_pixels_diff_gt_16": round(float((dm > 16).mean()), 5),
        "frac_pixels_diff_gt_48": round(float((dm > 48).mean()), 5),
    }
    # side by side + amplified diff for eyeballing
    h, w = ref.shape[:2]
    heat = np.clip(dm * 4, 0, 255).astype(np.uint8)
    canvas = Image.new("RGB", (w * 3, h), (255, 255, 255))
    canvas.paste(Image.fromarray(ref.astype(np.uint8)), (0, 0))
    canvas.paste(Image.fromarray(got.astype(np.uint8)), (w, 0))
    canvas.paste(Image.fromarray(255 - heat).convert("RGB"), (2 * w, 0))
    canvas.save(os.path.join(BUILD, "stamp_check_vs_reference.png"))
    return stats


def main():
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(PREV, exist_ok=True)
    os.makedirs(SCRATCH, exist_ok=True)
    build_glitter()
    build_pot_ref()
    svg = write_stamp_svg()
    check_html(svg, os.path.join(PREV, "stamp_check_ref-scale.html"))
    canvas_html(svg, os.path.join(PREV, "stamp_check_canvas.html"))
    render([
        {"html": os.path.join(PREV, "stamp_check_ref-scale.html"), "out": os.path.join(BUILD, "stamp_check_ref-scale.png"),
         "width": 1000, "height": 563, "dpr": 1, "transparent": False},
        {"html": os.path.join(PREV, "stamp_check_canvas.html"), "out": os.path.join(BUILD, "stamp_check_canvas.png"),
         "width": 1080, "height": 1350, "dpr": 1, "transparent": False},
    ])
    stats = compare()
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
