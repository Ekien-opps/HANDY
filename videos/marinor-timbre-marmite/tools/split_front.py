#!/usr/bin/env python3
"""Split assets/build/pot_front.png into the front body (wall, base, left handle, front lip) and the right
handle, so the flame can pass IN FRONT of the right handle (the handle is attached at the back-right of the
rim, the flame rises from E in the front-right part of the opening).

    python3 tools/split_front.py   -> assets/build/pot_front_body.png, assets/build/pot_handle_r.png

Deterministic. pot_front_body + pot_handle_r == pot_front exactly (complementary soft masks, straight alpha).
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "assets", "build")


def main():
    pot = json.load(open(os.path.join(BUILD, "pot.json")))
    rim = pot["rim_ellipse"]
    im = np.asarray(Image.open(os.path.join(BUILD, "pot_front.png")).convert("RGBA")).astype(np.float64)
    h, w = im.shape[:2]
    s = 2.0  # 2x density
    yy, xx = np.mgrid[0:h, 0:w]
    x = (xx + 0.5) / s
    y = (yy + 0.5) / s
    # outside the rim's outer ellipse (+1 px), right side, above the wall's upper corner
    e = ((x - rim["cx"]) / (rim["rx"] + 1.0)) ** 2 + ((y - rim["cy"]) / (rim["ry"] + 1.0)) ** 2
    x_right = rim["cx"] + rim["rx"]           # 802.55: the wall's right edge starts here
    upper = (y <= rim["cy"]) & (e > 0.85)   # pot_front holds nothing of the rim above cy except the lug edge
    lower = (y > rim["cy"]) & (x > x_right + 3.0)
    m = (x > 700) & (y < 720) & (upper | lower)
    # keep only the connected component that is the lug (largest blob with alpha)
    a = im[..., 3] > 8
    lab, n = ndi.label(m & a)
    if n > 1:
        sizes = ndi.sum(np.ones_like(lab), lab, index=np.arange(1, n + 1))
        m = lab == (1 + int(np.argmax(sizes)))
    else:
        m = lab == 1
    k = m.astype(np.float64)  # binary split: body + handle recombine exactly

    handle = im.copy()
    handle[..., 3] = im[..., 3] * k
    body = im.copy()
    body[..., 3] = im[..., 3] * (1 - k)
    for arr, name in ((body, "pot_front_body.png"), (handle, "pot_handle_r.png")):
        out = arr.copy()
        out[..., 3] = np.round(out[..., 3])
        out[out[..., 3] == 0, :3] = 0
        Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA").save(os.path.join(BUILD, name), optimize=True)
    ys, xs = np.nonzero(k > 0)
    print("handle px", int(k.sum()), "bbox canvas", xs.min() / s, xs.max() / s, ys.min() / s, ys.max() / s)


if __name__ == "__main__":
    main()
