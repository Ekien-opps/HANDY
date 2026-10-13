#!/usr/bin/env python3
"""Compact extract of assets/build/tear.json for the composition (deterministic, re-runnable).

Usage:  python3 tools/inline_tear.py            -> writes assets/build/tear_inline.json (for inspection)
        from inline_tear import tear_payload  -> (svg_defs: str, data: dict) used by tools/build_index.py

What is kept (everything else in tear.json stays out of index.html):
  - fragment polygons F1/F2/F3 (clip paths, shared crack vertices preserved: same numbers, same rounding)
  - lips fullD + liseré fullD per fragment (single clean paths)
  - crack polylines (noised points + base arc length s) for the front-reveal mask and the hairline
  - stress mark (f33) paths, pivots, rest/peak transforms, spring multipliers, luminance shifts, front params
The grey paper-thickness copies are NOT inlined: they are rebuilt live as paperGreyPath clipped by the
fragment polygon shifted by the paper offset (+6.156, +6.156), which is the same set.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "assets", "build")
NUM = re.compile(r"-?\d+\.\d+|-?\d+")


def rnd(v, nd=2):
    s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def round_path(d, nd=2):
    d = NUM.sub(lambda m: rnd(float(m.group(0)), nd), d)
    return re.sub(r"\s+", " ", d).strip()


def tear_payload():
    t = json.load(open(os.path.join(BUILD, "tear.json")))
    F = t["fragments"]
    defs = []
    for k in ("F1", "F2", "F3"):
        fr = F[k]
        defs.append(f'<path id="tp{k}" d="{round_path(fr["d"], 2)}"/>')
    # clip paths: fragment polygon, and the same polygon shifted by the paper thickness (grey copy)
    off = t["paperThicknessOffsetPx"]
    for k in ("F1", "F2", "F3"):
        defs.append(f'<clipPath id="tc{k}" clipPathUnits="userSpaceOnUse"><use href="#tp{k}"/></clipPath>')
        defs.append(f'<clipPath id="tg{k}" clipPathUnits="userSpaceOnUse"><use href="#tp{k}" '
                    f'transform="translate({rnd(off[0], 3)} {rnd(off[1], 3)})"/></clipPath>')
    for k in ("F1", "F2", "F3"):
        lips = F[k]["lips"]
        lis = F[k]["lisere"]
        defs.append(f'<path id="tl{k}" fill="{lips["fill"]}" d="{round_path(lips["fullD"], 2)}"/>')
        defs.append(f'<path id="ts{k}" fill="none" stroke="{lis["stroke"]}" stroke-opacity="{lis["strokeOpacity"]}" '
                    f'stroke-width="{lis["strokeWidth"]}" stroke-linejoin="round" stroke-linecap="round" '
                    f'd="{round_path(lis["fullD"], 2)}"/>')
    sm = t["stressMark"]
    stress = (f'<path fill="{sm["slit"]["fill"]}" fill-opacity="{sm["slit"]["opacity"]}" d="{round_path(sm["slit"]["d"], 2)}"/>'
              f'<path fill="{sm["fibres"]["fill"]}" fill-opacity="{sm["fibres"]["opacity"]}" d="{round_path(sm["fibres"]["d"], 2)}"/>')

    crack = {}
    for b in ("trunk", "branchA", "branchB"):
        c = t["crack"][b]
        pts = []
        for (x, y) in c["points"]:
            pts += [round(x, 2), round(y, 2)]
        crack[b] = {"p": pts, "s": [round(v, 2) for v in c["s"]], "L": round(t["front"][b]["length"], 3)}

    frag = {}
    for k in ("F1", "F2", "F3"):
        fr = F[k]
        r, p = fr["rest_x1.00"], fr["peak_x1.35"]
        frag[k] = {
            "pivot": fr["pivot"],
            "rest": [r["rotateDeg"], r["translatePx"][0], r["translatePx"][1], r["luminanceShift"]],
            "peak": [p["rotateDeg"], p["translatePx"][0], p["translatePx"][1], p["luminanceShift"]],
        }
    data = {
        "crack": crack,
        "front": {"start": t["front"]["trunk"]["startFrame"], "speed": t["front"]["trunk"]["speedPxPerFrame"],
                  "end": 36.0},
        "frag": frag,
        "mult": {int(k): v for k, v in t["spring"]["multipliers"].items()},
        "stressFrame": sm["frame"],
        "hair": {"stroke": "#4D4D4D", "width": 1.2, "opacity": 0.55},
    }
    return "\n".join(defs), stress, data


if __name__ == "__main__":
    defs, stress, data = tear_payload()
    out = os.path.join(BUILD, "tear_inline.json")
    json.dump({"defs_bytes": len(defs), "stress_bytes": len(stress), "data": data}, open(out, "w"), separators=(",", ":"))
    print("defs", len(defs), "bytes; stress", len(stress), "; data", len(json.dumps(data, separators=(",", ":"))), "bytes ->", out)
