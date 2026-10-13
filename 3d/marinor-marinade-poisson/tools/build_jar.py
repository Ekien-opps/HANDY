#!/usr/bin/env python3
"""Marin'Or Ivoire · Marinade Poisson 500 g jar -> Wavefront OBJ + MTL (+ label texture).

Units: centimetres, Y up, jar base centre at the origin, label front facing +Z.
Silhouette measured on src/ref-face-dos.webp (right jar, 804 px = 8.6 cm body diameter).

Objects (each a closed or properly bounded surface, smooth normals, UVs):
  Verre        glass jar: outer wall, rolled lip, inner wall, thick base
  Sauce        cream marinade filling the jar up to the neck, with a meniscus
  Couvercle    green screw cap (outer shell, flared skirt, rolled top edge, underside)
  Etiquette    paper label wrapped on the straight body (front = artwork, back + edges = white paper)
  Pastilles    ring of small embossed glass dots just under the label (as on the reference)

Run:  python3 tools/build_jar.py [--wrap-scale 1.31]
"""
import argparse
import json
import math
import os
import shutil

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
NAME = "MarinOr_Marinade-Poisson_500g"

SEG = 192  # radial segments


# --------------------------------------------------------------------------- profile helpers
def catmull(points, per_seg=8):
    """Centripetal-ish Catmull-Rom through (r, y) points, keeps the end points."""
    P = np.asarray(points, float)
    if len(P) < 3:
        return P
    ext = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        for k in range(per_seg):
            t = k / per_seg
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-1])
    return np.asarray(out)


def arc(cx, cy, rad, a0, a1, n=10):
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([cx + rad * np.cos(a), cy + rad * np.sin(a)], 1)


def dedupe(P, eps=1e-6):
    keep = [P[0]]
    for p in P[1:]:
        if np.hypot(*(p - keep[-1])) > eps:
            keep.append(p)
    return np.asarray(keep)


def profile_normals(P, outward_sign=1.0):
    """2D normals (nr, ny) of a polyline in the (r, y) plane, smooth (averaged tangents)."""
    T = np.zeros_like(P)
    T[1:-1] = P[2:] - P[:-2]
    T[0] = P[1] - P[0]
    T[-1] = P[-1] - P[-2]
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    N = np.stack([T[:, 1], -T[:, 0]], 1) * outward_sign
    return N


# --------------------------------------------------------------------------- mesh container
class Mesh:
    def __init__(self, name):
        self.name = name
        self.v, self.vt, self.vn, self.groups = [], [], [], []  # groups: (material, faces)

    def add_group(self, mat):
        self.groups.append((mat, []))
        return self.groups[-1][1]

    def addv(self, p, uv, n):
        self.v.append(p)
        self.vt.append(uv)
        n = np.asarray(n, float)
        self.vn.append(n / (np.linalg.norm(n) + 1e-12))
        return len(self.v) - 1


def revolve(mesh, mat, P, N, u_range=(0.0, 1.0), v_vals=None, seg=SEG, phi0=-math.pi, phi1=math.pi, flip=False):
    """Revolve profile P (r, y) with 2D normals N around Y. Seam duplicated for clean UVs."""
    faces = mesh.add_group(mat)
    if v_vals is None:
        L = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
        v_vals = L / (L[-1] if L[-1] > 0 else 1)
    idx = np.zeros((seg + 1, len(P)), int)
    for i in range(seg + 1):
        t = i / seg
        phi = phi0 + (phi1 - phi0) * t
        s, c = math.sin(phi), math.cos(phi)
        u = u_range[0] + (u_range[1] - u_range[0]) * t
        for j, ((r, y), (nr, ny)) in enumerate(zip(P, N)):
            idx[i, j] = mesh.addv((r * s, y, r * c), (u, v_vals[j]), (nr * s, ny, nr * c))
    for i in range(seg):
        for j in range(len(P) - 1):
            a, b, c2, d = idx[i, j], idx[i + 1, j], idx[i + 1, j + 1], idx[i, j + 1]
            if P[j][0] < 1e-9 and P[j + 1][0] < 1e-9:
                continue
            tri1, tri2 = (a, d, c2), (a, c2, b)
            if flip:
                tri1, tri2 = tri1[::-1], tri2[::-1]
            # skip degenerate triangles at the axis
            if P[j][0] < 1e-9:
                faces.append(tri1 if not flip else tri1)
            elif P[j + 1][0] < 1e-9:
                faces.append(tri2 if not flip else tri2)
            else:
                faces.append(tri1)
                faces.append(tri2)
    return idx


# --------------------------------------------------------------------------- geometry
def glass_profiles():
    # outer wall, from the base centre outwards then up to the lip (cm)
    base = [(0.0, 0.16), (1.2, 0.12), (2.3, 0.05)]
    foot = arc(2.62, 0.30, 0.30, -90, -20, 6).tolist()  # contact ring with a soft fillet
    heel = catmull([(2.90, 0.20), (3.35, 0.36), (3.80, 0.62), (4.12, 0.98), (4.27, 1.34), (4.30, 1.62)], 8).tolist()
    body = [(4.30, 1.62 + k * (11.20 - 1.62) / 24) for k in range(1, 25)]
    shoulder = catmull([(4.30, 11.20), (4.27, 11.45), (4.20, 11.70), (4.00, 12.12), (3.80, 12.55),
                        (3.59, 12.98), (3.48, 13.24), (3.43, 13.40)], 8).tolist()
    neck = catmull([(3.43, 13.40), (3.50, 13.48), (3.52, 13.58), (3.47, 13.68), (3.36, 13.76)], 6).tolist()
    finish = [(3.34, 13.80 + k * (15.22 - 13.80) / 8) for k in range(1, 9)]
    lip = arc(3.20, 15.22, 0.14, 0, 180, 10).tolist()  # rolled lip, ends at r=3.06
    outer = dedupe(np.asarray(base + foot + heel + body + shoulder + neck + finish + lip))
    # inner wall: from the lip inner edge down to the inner base centre
    inner = [(3.06, 15.22), (3.06, 13.80), (3.08, 13.50), (3.17, 13.25)]
    inner += catmull([(3.17, 13.25), (3.33, 12.92), (3.55, 12.50), (3.76, 12.08), (3.96, 11.66), (4.02, 11.20)], 6).tolist()[1:]
    inner += [(4.02, 11.20 - k * (11.20 - 1.70) / 20) for k in range(1, 21)]
    inner += catmull([(4.02, 1.70), (3.95, 1.25), (3.70, 0.88), (3.25, 0.62), (2.60, 0.50)], 6).tolist()[1:]
    inner += [(1.3, 0.47), (0.0, 0.46)]
    inner = dedupe(np.asarray(inner))
    return outer, inner


def sauce_profile(fill_y=13.52):
    # follows the glass inner wall 0.012 cm inside, up to the fill level, then the meniscus top
    pts = [(0.0, 0.472), (1.3, 0.482), (2.59, 0.512)]
    pts += catmull([(2.59, 0.512), (3.24, 0.632), (3.69, 0.892), (3.94, 1.255), (4.008, 1.70)], 6).tolist()[1:]
    pts += [(4.008, 1.70 + k * (11.20 - 1.70) / 20) for k in range(1, 21)]
    pts += catmull([(4.008, 11.20), (3.948, 11.66), (3.748, 12.08), (3.538, 12.50), (3.318, 12.92), (3.158, 13.25)], 6).tolist()[1:]
    pts += [(3.068, fill_y - 0.03)]
    meniscus = [(3.04, fill_y), (2.9, fill_y - 0.03), (2.4, fill_y - 0.06), (1.2, fill_y - 0.075), (0.0, fill_y - 0.078)]
    return dedupe(np.asarray(pts + meniscus))


def cap_profile():
    # outer shell from the skirt's inner bottom edge, round the flare, up the side, over the rolled top edge to the centre
    P = [(3.44, 13.86)]
    P += arc(3.80, 13.86, 0.08, 180, 270, 4).tolist()  # bottom inner corner -> bottom face
    P += [(3.86, 13.78)]
    P += arc(3.86, 13.86, 0.08, -90, 0, 5).tolist()[1:]  # flare bottom outer corner
    P += [(3.94, 13.98), (3.93, 14.08)]
    P += catmull([(3.93, 14.08), (3.86, 14.16), (3.76, 14.22), (3.73, 14.30)], 4).tolist()[1:]  # step in to the side wall
    P += [(3.72, 14.30 + k * (15.36 - 14.30) / 12) for k in range(1, 13)]
    P += arc(3.38, 15.36, 0.34, 0, 80, 10).tolist()[1:]  # rolled top edge
    P += catmull([(3.44, 15.695), (2.6, 15.80), (1.4, 15.865), (0.0, 15.885)], 8).tolist()[1:]  # gentle dome
    outer = dedupe(np.asarray(P))
    # underside: inner skirt wall then the inside of the top (faces inwards/down)
    inner = dedupe(np.asarray([(3.44, 13.86), (3.42, 14.20), (3.41, 15.30), (3.30, 15.48), (2.0, 15.52), (0.0, 15.53)]))
    return outer, inner


# --------------------------------------------------------------------------- build
def build(wrap_scale):
    os.makedirs(BUILD, exist_ok=True)
    meshes = []

    # ---- glass
    outer, inner = glass_profiles()
    g = Mesh("Verre")
    revolve(g, "Verre", outer, profile_normals(outer, 1.0))
    revolve(g, "Verre", inner, profile_normals(inner, 1.0))  # inner wall: normals point into the cavity
    meshes.append(g)

    # ---- sauce
    sp = sauce_profile()
    s = Mesh("Sauce")
    revolve(s, "Sauce_creme", sp, profile_normals(sp, 1.0))
    meshes.append(s)

    # ---- cap
    co, ci = cap_profile()
    c = Mesh("Couvercle")
    revolve(c, "Couvercle_vert", co, profile_normals(co, 1.0))
    revolve(c, "Couvercle_interieur", ci, profile_normals(ci, -1.0))
    meshes.append(c)

    # ---- label
    lab_src = os.path.join(ROOT, "src", "etiquette-a-plat.webp")
    lab = Image.open(lab_src).convert("RGBA")
    W, H = lab.size
    bg = Image.new("RGBA", lab.size, (255, 255, 255, 255))
    bg.alpha_composite(lab)
    bg.convert("RGB").save(os.path.join(BUILD, "etiquette_marinade-poisson.png"), optimize=True)
    R_LAB, Y0, Y1, TH = 4.312, 1.66, 11.16, 0.012
    h = Y1 - Y0
    arc_len = (W / H) * h * wrap_scale
    ang = arc_len / R_LAB
    if ang > 2 * math.pi:
        raise SystemExit(f"label wraps more than 360 deg ({math.degrees(ang):.1f})")
    lb = Mesh("Etiquette")
    # front (artwork), outward normals
    front = np.asarray([(R_LAB, Y0), (R_LAB, Y1)])
    seg = int(SEG * ang / (2 * math.pi)) + 1
    revolve(lb, "Etiquette_impression", front, np.asarray([(1.0, 0.0), (1.0, 0.0)]), u_range=(0.0, 1.0),
            v_vals=np.asarray([0.0, 1.0]), seg=seg, phi0=-ang / 2, phi1=ang / 2, flip=True)
    # back of the paper (white), facing the glass
    back = np.asarray([(R_LAB - TH, Y0), (R_LAB - TH, Y1)])
    revolve(lb, "Etiquette_papier", back, np.asarray([(-1.0, 0.0), (-1.0, 0.0)]), v_vals=np.asarray([0.0, 1.0]),
            seg=seg, phi0=-ang / 2, phi1=ang / 2)
    # top and bottom paper edges
    top = np.asarray([(R_LAB - TH, Y1), (R_LAB, Y1)])
    revolve(lb, "Etiquette_papier", top, np.asarray([(0.0, 1.0), (0.0, 1.0)]), v_vals=np.asarray([0.0, 1.0]),
            seg=seg, phi0=-ang / 2, phi1=ang / 2, flip=True)
    bot = np.asarray([(R_LAB, Y0), (R_LAB - TH, Y0)])
    revolve(lb, "Etiquette_papier", bot, np.asarray([(0.0, -1.0), (0.0, -1.0)]), v_vals=np.asarray([0.0, 1.0]),
            seg=seg, phi0=-ang / 2, phi1=ang / 2, flip=True)
    # the two vertical end edges
    faces = lb.add_group("Etiquette_papier")
    for phi, sgn in ((-ang / 2, -1.0), (ang / 2, 1.0)):
        sn, cs = math.sin(phi), math.cos(phi)
        n = (sgn * cs, 0.0, -sgn * sn)
        q = [lb.addv((r * sn, y, r * cs), (0, 0), n) for r, y in ((R_LAB - TH, Y0), (R_LAB, Y0), (R_LAB, Y1), (R_LAB - TH, Y1))]
        if sgn > 0:
            faces += [(q[0], q[1], q[2]), (q[0], q[2], q[3])]
        else:
            faces += [(q[0], q[2], q[1]), (q[0], q[3], q[2])]
    meshes.append(lb)

    # ---- embossed dots (ring under the label, on the heel)
    dots = Mesh("Pastilles")
    faces = dots.add_group("Verre")
    n_dots, y_d = 32, 1.36
    # radius of the outer wall at y_d (interpolate on the outer profile)
    o = outer
    k = np.argmin(np.abs(o[:, 1] - y_d) + (o[:, 0] < 4.0) * 10)
    r_d = float(o[k, 0])
    nrm2 = profile_normals(o, 1.0)[k]
    rad = 0.075
    for i in range(n_dots):
        phi = 2 * math.pi * (i + 0.5) / n_dots
        sn, cs = math.sin(phi), math.cos(phi)
        c0 = np.array([r_d * sn, y_d, r_d * cs])
        nz = np.array([nrm2[0] * sn, nrm2[1], nrm2[0] * cs])
        nz /= np.linalg.norm(nz)
        tx = np.array([cs, 0.0, -sn])
        ty = np.cross(nz, tx)
        rows = []
        for a in range(7):  # hemisphere, 7 latitude rows x 12 longitudes
            th = (math.pi / 2) * a / 6
            row = []
            for b in range(12):
                ps = 2 * math.pi * b / 12
                d = math.cos(th) * nz + math.sin(th) * (math.cos(ps) * tx + math.sin(ps) * ty)
                p = c0 + rad * d * np.array([1, 1.25, 1])  # slightly elongated drop
                row.append(dots.addv(tuple(p), (b / 12, a / 6), d))
            rows.append(row)
        for a in range(6):
            for b in range(12):
                a0, a1 = rows[a][b], rows[a][(b + 1) % 12]
                b0, b1 = rows[a + 1][b], rows[a + 1][(b + 1) % 12]
                if a == 0:
                    faces.append((a0, b0, b1))
                else:
                    faces += [(a0, b0, b1), (a0, b1, a1)]
    meshes.append(dots)

    # ---- write OBJ + MTL
    obj_path = os.path.join(BUILD, NAME + ".obj")
    mtl_name = NAME + ".mtl"
    with open(obj_path, "w") as f:
        f.write(f"# Marin'Or Ivoire - Marinade Poisson 500 g - glass jar with green screw cap\n")
        f.write("# Units: centimetres. Y up. Base centre at origin. Label front faces +Z.\n")
        f.write(f"mtllib {mtl_name}\n")
        off = 1
        for m in meshes:
            f.write(f"o {m.name}\n")
            for p in m.v:
                f.write("v %.5f %.5f %.5f\n" % tuple(p))
            for t in m.vt:
                f.write("vt %.6f %.6f\n" % tuple(t))
            for n in m.vn:
                f.write("vn %.5f %.5f %.5f\n" % tuple(n))
            V = np.asarray(m.v); VN = np.asarray(m.vn)
            for mat, fs in m.groups:
                f.write(f"usemtl {mat}\ns 1\n")
                for tri in fs:
                    i0, i1, i2 = tri
                    gn = np.cross(V[i1] - V[i0], V[i2] - V[i0])
                    if np.dot(gn, VN[i0] + VN[i1] + VN[i2]) < 0:  # make winding agree with the shading normals
                        i1, i2 = i2, i1
                    a, b, c3 = (i + off for i in (i0, i1, i2))
                    f.write(f"f {a}/{a}/{a} {b}/{b}/{b} {c3}/{c3}/{c3}\n")
            off += len(m.v)
    with open(os.path.join(BUILD, mtl_name), "w") as f:
        f.write("# Marin'Or Ivoire - Marinade Poisson 500 g\n")
        f.write("""
newmtl Verre
Ka 0 0 0
Kd 0.92 0.95 0.93
Ks 0.9 0.9 0.9
Ns 900
Ni 1.50
d 0.18
Tr 0.82
Tf 0.95 0.98 0.96
illum 7

newmtl Sauce_creme
Ka 0 0 0
Kd 0.906 0.875 0.812
Ks 0.12 0.12 0.12
Ns 60
d 1
illum 2

newmtl Couvercle_vert
Ka 0 0 0
Kd 0.369 0.431 0.141
Ks 0.45 0.45 0.45
Ns 350
d 1
illum 2

newmtl Couvercle_interieur
Ka 0 0 0
Kd 0.30 0.35 0.12
Ks 0.1 0.1 0.1
Ns 40
d 1
illum 2

newmtl Etiquette_impression
Ka 0 0 0
Kd 1 1 1
Ks 0.25 0.25 0.25
Ns 120
d 1
illum 2
map_Kd etiquette_marinade-poisson.png

newmtl Etiquette_papier
Ka 0 0 0
Kd 0.96 0.96 0.95
Ks 0.05 0.05 0.05
Ns 20
d 1
illum 2
""")
    stats = {
        "objects": {m.name: {"vertices": len(m.v), "triangles": sum(len(fs) for _, fs in m.groups)} for m in meshes},
        "label": {"height_cm": round(h, 3), "arc_cm": round(arc_len, 3), "wrap_deg": round(math.degrees(ang), 1),
                  "wrap_scale": wrap_scale, "radius_cm": R_LAB, "texture_px": [W, H]},
        "jar": {"body_diameter_cm": 8.6, "height_cm": 15.885, "cap_diameter_cm": round(2 * 3.94, 2)},
    }
    with open(os.path.join(BUILD, "stats.json"), "w") as f:
        json.dump(stats, f, indent=1)
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--wrap-scale", type=float, default=1.31,
                    help="horizontal scale of the label artwork on the jar (1.0 = true proportions; 1.31 = as in the client's mockups)")
    build(ap.parse_args().wrap_scale)
