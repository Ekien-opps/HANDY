#!/usr/bin/env python3
"""Marin'Or Ivoire · 100 g stand-up pouch (doypack) -> Wavefront OBJ + MTL + face textures.

Units: centimetres, Y up, centre of the base at the origin, front face towards +Z.
The pouch outline is measured on the client's front/back mockups (all share one template):
silhouette 1249 px wide at the top = 14 cm.

Geometry
  - front and back film surfaces are height fields over the silhouette: flat top seal with a zip
    ridge, flat side seals, an inflated body whose cross-section goes from a lens (under the zip)
    to an ellipse at the bottom, closed by an oval gusset base;
  - a thin edge strip joins front and back along the outline (film thickness).
Textures: the front / back mockups projected straight on (planar UV), colours pushed past the
outline so no fringe appears at the edges.

Run:  python3 tools/build_pouch.py <produit>     (produits: tools/products.json)
"""
import argparse
import json
import math
import os

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = json.load(open(os.path.join(ROOT, "tools", "products.json")))

# template measurements (px, on the 1380 x 2000 mockups)
IMG_W, IMG_H = 1380, 2000
CX = (67 + 1316) / 2
Y_TOP_PX, Y_BOT_PX = 93, 1923
S = 14.0 / 1249.0  # cm per px
H = (Y_BOT_PX - Y_TOP_PX) * S  # 20.5 cm
SEAL_SIDE = 0.55  # side seal width (cm)
Y_TS = H - (360 - Y_TOP_PX) * S  # bottom of the flat top seal (cm from the base)
Y_ZIP = H - (322 - Y_TOP_PX) * S  # zip ridge centre
T_MAX, EPS = 3.0, 0.012  # half thickness of the body at the base, half film thickness
NU, NV = 120, 220  # grid resolution across / along


def silhouette_halfwidth():
    """Half-width (cm) of the pouch outline as a function of height Y (cm), from the mockup alpha."""
    a = np.asarray(Image.open(os.path.join(ROOT, "src", "akpi", "face-avant.webp")).convert("RGBA"))[..., 3]
    ys, hw = [], []
    for y in range(Y_TOP_PX, Y_BOT_PX - 20):
        xs = np.where(a[y] > 128)[0]
        if len(xs):
            ys.append((Y_BOT_PX - y) * S)
            hw.append(((xs[-1] - xs[0]) / 2) * S)
    ys, hw = np.asarray(ys[::-1]), np.asarray(hw[::-1])
    # smooth (the outline is straight-ish) and extend to Y=0 with the lowest measured value
    hw = ndimage.uniform_filter1d(hw, 41, mode="nearest")
    return lambda Y: np.interp(Y, ys, hw, left=hw[0], right=hw[-1])


def thickness(Y):
    """Half thickness of the inflated body at height Y."""
    Y = np.asarray(Y, float)
    t = T_MAX * np.clip(1 - (Y / Y_TS) ** 2, 0, None) ** 0.85
    return np.where(Y < Y_TS, t, 0.0)


def zip_ridge(Y):
    return 0.10 * np.exp(-((Y - Y_ZIP) / 0.14) ** 2) + 0.05 * np.exp(-((Y - (Y_ZIP - 0.45)) / 0.10) ** 2)


def surface(sign, hw):
    """Vertices (NV+1, NU+1, 3) and UVs of the front (sign=+1) or back (sign=-1) film."""
    V = np.zeros((NV + 1, NU + 1, 3))
    UV = np.zeros((NV + 1, NU + 1, 2))
    for j in range(NV + 1):
        Y = H * j / NV
        w = float(hw(Y))
        # rounded bottom corners of the outline
        corner = 0.9
        if Y < corner:
            w -= corner - math.sqrt(max(corner ** 2 - (corner - Y) ** 2, 0.0))
        xe = max(w - SEAL_SIDE, 0.01)
        t = float(thickness(Y))
        q = 0.5 + 0.5 * min(Y / Y_TS, 1.0)  # ellipse at the base -> lens under the zip
        for i in range(NU + 1):
            s = -1 + 2 * i / NU
            # denser sampling near the seal line: map s through a smooth curve
            X = w * s
            r = abs(X) / xe
            g = (1 - r * r) ** q if r < 1 else 0.0
            z = EPS + t * g + float(zip_ridge(Y))
            V[j, i] = (X, Y, sign * z)
            xi = CX + X / S if sign > 0 else CX - X / S  # back face is seen mirrored
            yi = Y_BOT_PX - Y / S
            UV[j, i] = (xi / IMG_W, 1 - yi / IMG_H)
    return V, UV


def vertex_normals(V, F):
    N = np.zeros_like(V)
    fn = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    for k in range(3):
        np.add.at(N, F[:, k], fn)
    return N / (np.linalg.norm(N, axis=1, keepdims=True) + 1e-12)


def grid_faces(nv, nu, off, flip):
    F = []
    for j in range(nv):
        for i in range(nu):
            a = off + j * (nu + 1) + i
            b, c, d = a + 1, a + nu + 2, a + nu + 1
            F += [(a, b, c), (a, c, d)] if not flip else [(a, c, b), (a, d, c)]
    return F


def prep_texture(src, dst):
    """Make the mockup face opaque and push edge colours past the outline (no fringe at the seams)."""
    im = np.asarray(Image.open(src).convert("RGBA")).astype(np.float32)
    a = im[..., 3] / 255.0
    solid = a > 0.98
    idx = ndimage.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    filled = im[idx[0], idx[1], :3]
    out = filled.copy()
    out[solid] = im[solid, :3]
    Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGB").save(dst, optimize=True)
    # mean colour of the bottom strip (for the gusset base and the edges)
    strip = im[Y_BOT_PX - 60:Y_BOT_PX - 20, 300:1080]
    m = strip[strip[..., 3] > 250][:, :3].mean(0)
    return "#%02X%02X%02X" % tuple(int(v) for v in m)


def hex_lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return " ".join("%.4f" % (x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c)


def build(product):
    P = PRODUCTS[product]
    NAME = P["name"]
    BUILD = os.path.join(ROOT, "build", product)
    os.makedirs(BUILD, exist_ok=True)
    tex_f, tex_b = f"{product}_face-avant.png", f"{product}_face-arriere.png"
    col_f = prep_texture(os.path.join(ROOT, P["front"]), os.path.join(BUILD, tex_f))
    col_b = prep_texture(os.path.join(ROOT, P["back"]), os.path.join(BUILD, tex_b))
    edge_col = P.get("edge", col_f)

    hw = silhouette_halfwidth()
    Vf, UVf = surface(+1, hw)
    Vb, UVb = surface(-1, hw)
    n = (NV + 1) * (NU + 1)
    verts = np.vstack([Vf.reshape(-1, 3), Vb.reshape(-1, 3)])
    uvs = np.vstack([UVf.reshape(-1, 2), UVb.reshape(-1, 2)])
    F_front = np.asarray(grid_faces(NV, NU, 0, flip=False))
    F_back = np.asarray(grid_faces(NV, NU, n, flip=True))

    # outline strip (film edge) + gusset base: extra vertices with their own UVs
    ev, euv, F_edge = [], [], []

    def add(p, uv=(0.5, 0.5)):
        ev.append(p)
        euv.append(uv)
        return len(verts) + len(ev) - 1

    def ring(j_or_i, kind):
        if kind == "row":
            return [j_or_i * (NU + 1) + i for i in range(NU + 1)]
        return [j * (NU + 1) + j_or_i for j in range(NV + 1)]

    # sides (left i=0, right i=NU) and top (j=NV): quads between front and back boundary vertices
    for kind, idxs in (("col", ring(0, "col")), ("col", ring(NU, "col")), ("row", ring(NV, "row"))):
        a = [add(tuple(verts[k])) for k in idxs]
        b = [add(tuple(verts[n + k])) for k in idxs]
        for k in range(len(idxs) - 1):
            F_edge += [(a[k], a[k + 1], b[k + 1]), (a[k], b[k + 1], b[k])]
    # base (j=0): front bottom row to back bottom row, a flat oval
    bot = ring(0, "row")
    a = [add(tuple(verts[k])) for k in bot]
    b = [add(tuple(verts[n + k])) for k in bot]
    for k in range(len(bot) - 1):
        F_edge += [(a[k], a[k + 1], b[k + 1]), (a[k], b[k + 1], b[k])]

    allv = np.vstack([verts, np.asarray(ev)])
    alluv = np.vstack([uvs, np.asarray(euv)])
    F_edge = np.asarray(F_edge)
    # orient every edge/base face outwards (away from the pouch's interior axis)
    c0 = np.array([0, H * 0.45, 0])
    for k, f in enumerate(F_edge):
        p = allv[f]
        fn = np.cross(p[1] - p[0], p[2] - p[0])
        cen = p.mean(0)
        out = cen - c0
        if cen[1] < 1e-6:
            out = np.array([0, -1.0, 0])
        if np.dot(fn, out) < 0:
            F_edge[k] = f[[0, 2, 1]]
    F_all = np.vstack([F_front, F_back, F_edge])
    N = vertex_normals(allv, F_all)
    # edge/base vertices get flat normals of their own faces (they are separate vertices)
    NE = vertex_normals(allv, F_edge)
    N[len(verts):] = NE[len(verts):]

    obj = os.path.join(BUILD, NAME + ".obj")
    with open(obj, "w") as f:
        f.write(f"# Marin'Or Ivoire - {P['title']} - stand-up pouch (doypack)\n")
        f.write("# Units: centimetres. Y up. Base centre at origin. Front face towards +Z.\n")
        f.write(f"mtllib {NAME}.mtl\no Sachet\n")
        for p in allv:
            f.write("v %.5f %.5f %.5f\n" % tuple(p))
        for t in alluv:
            f.write("vt %.6f %.6f\n" % tuple(t))
        for nn in N:
            f.write("vn %.5f %.5f %.5f\n" % tuple(nn))
        for mat, F in (("Sachet_face_avant", F_front), ("Sachet_face_arriere", F_back), ("Sachet_tranche_fond", F_edge)):
            f.write(f"usemtl {mat}\ns 1\n")
            for tri in F:
                a1, b1, c1 = (int(x) + 1 for x in tri)
                f.write(f"f {a1}/{a1}/{a1} {b1}/{b1}/{b1} {c1}/{c1}/{c1}\n")
    with open(os.path.join(BUILD, NAME + ".mtl"), "w") as f:
        f.write(f"# Marin'Or Ivoire - {P['title']}\n# Kd values are LINEAR RGB (sRGB hex in comments)\n")
        for mat, tex in (("Sachet_face_avant", tex_f), ("Sachet_face_arriere", tex_b)):
            f.write(f"\nnewmtl {mat}\nKa 0 0 0\nKd 1 1 1\nKs 0.35 0.35 0.35\nNs 180\nd 1\nillum 2\nmap_Kd {tex}\n")
        f.write(f"\nnewmtl Sachet_tranche_fond\n# {edge_col}\nKa 0 0 0\nKd {hex_lin(edge_col)}\nKs 0.3 0.3 0.3\nNs 150\nd 1\nillum 2\n")
    bbox = allv.min(0), allv.max(0)
    stats = {"product": product, "vertices": int(len(allv)), "triangles": int(len(F_all)),
             "size_cm": {"width": round(float(bbox[1][0] - bbox[0][0]), 2), "height": round(float(bbox[1][1]), 2),
                         "depth": round(float(bbox[1][2] - bbox[0][2]), 2)},
             "edge_colour": edge_col}
    json.dump(stats, open(os.path.join(BUILD, "stats.json"), "w"), indent=1)
    json.dump({"name": NAME, "obj": f"../build/{product}/{NAME}.obj", "front": f"../build/{product}/{tex_f}",
               "back": f"../build/{product}/{tex_b}", "edge": edge_col, "height": H},
              open(os.path.join(BUILD, "preview.json"), "w"), indent=1)
    readme = open(os.path.join(ROOT, "tools", "LISEZ-MOI.template.txt"), encoding="utf-8").read()
    for k, v in {**P, "tex_f": tex_f, "tex_b": tex_b, "w": stats["size_cm"]["width"], "h": stats["size_cm"]["height"],
                 "d": stats["size_cm"]["depth"], "verts": f"{stats['vertices']:,}".replace(",", " "),
                 "tris": f"{stats['triangles']:,}".replace(",", " "), "edge": edge_col}.items():
        readme = readme.replace("{" + k + "}", str(v).replace(".", ",") if k in ("w", "h", "d") else str(v))
    open(os.path.join(BUILD, "LISEZ-MOI.txt"), "w", encoding="utf-8").write(readme)
    print(json.dumps(stats))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("product", choices=sorted(PRODUCTS))
    build(ap.parse_args().product)
