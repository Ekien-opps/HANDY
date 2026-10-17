# -*- coding: utf-8 -*-
"""
Génère les textures de végétation du décor de Cocody (textures/env/*.png).

Python 3 + Pillow :  python3 generer_textures_env.py
Les PNG produits sont déjà fournis dans textures/env/ ; ce script ne sert qu'à
les refaire ou à les modifier (couleurs, densité). Ce sont des « cartes » à
fond transparent, posées sur des plans dans Blender (feuillages des arbres,
palmes, feuilles de bananier, fleurs). Le RVB des pixels transparents reprend
la couleur moyenne des feuilles, pour éviter les liserés clairs au filtrage.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

DOSSIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textures", "env")
SUR = 2           # suréchantillonnage (anticrénelage)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def varier(c, r, amp=18, lum=0.0):
    """Couleur c (rgb) avec une variation aléatoire et un décalage de luminosité."""
    k = 1.0 + lum
    return tuple(max(0, min(255, int(v * k + r.uniform(-amp, amp)))) for v in c)


def toile(w, h):
    return Image.new("RGBA", (w * SUR, h * SUR), (0, 0, 0, 0))


def finir(img, nom, flou=0.0):
    w, h = img.size[0] // SUR, img.size[1] // SUR
    if flou:
        img = img.filter(ImageFilter.GaussianBlur(flou * SUR))
    img = img.resize((w, h), Image.LANCZOS)
    # Bord sans halo : RVB des pixels transparents = moyenne des pixels opaques.
    px = img.load()
    somme, nb = [0, 0, 0], 0
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            r, g, b, a = px[x, y]
            if a > 200:
                somme[0] += r; somme[1] += g; somme[2] += b; nb += 1
    moy = tuple(s // max(nb, 1) for s in somme)
    fond = Image.new("RGBA", (w, h), moy + (0,))
    fond.alpha_composite(img)
    # alpha d'origine conservé (alpha_composite sur fond transparent le garde)
    fond.putalpha(img.getchannel("A"))
    os.makedirs(DOSSIER, exist_ok=True)
    chemin = os.path.join(DOSSIER, nom)
    fond.save(chemin, optimize=True)
    print("ecrit", chemin, "%dx%d" % (w, h))


def feuille(d, cx, cy, longueur, largeur, angle, couleur, nervure=None, pointe=1.0):
    """Feuille lancéolée (deux arcs), base en (cx, cy), orientée selon angle."""
    pts_g, pts_d = [], []
    n = 10
    ca, sa = math.cos(angle), math.sin(angle)
    for i in range(n + 1):
        t = i / n
        demi = largeur / 2 * math.sin(math.pi * t ** (0.8 * pointe)) * (1 - 0.15 * t)
        ax, ay = t * longueur, demi
        pts_g.append((cx + ax * ca - ay * sa, cy + ax * sa + ay * ca))
        pts_d.append((cx + ax * ca + ay * sa, cy + ax * sa - ay * ca))
    d.polygon(pts_g + pts_d[::-1], fill=couleur + (255,))
    if nervure:
        d.line([(cx, cy), (cx + longueur * 0.95 * ca, cy + longueur * 0.95 * sa)],
               fill=nervure + (255,), width=max(1, int(largeur * 0.08)))


def eclaircir_haut(img, force=0.25):
    """Feuillage plus clair en haut (lumière du ciel), plus sombre en bas."""
    w, h = img.size
    grad = Image.linear_gradient("L").resize((w, h))          # 0 en haut -> 255 en bas
    sombre = img.point(lambda v: int(v * (1 - force)))
    clair = img.point(lambda v: min(255, int(v * (1 + force * 0.6))))
    rgb = Image.composite(sombre.convert("RGB"), clair.convert("RGB"), grad)
    out = rgb.convert("RGBA")
    out.putalpha(img.getchannel("A"))
    return out


# =============================================================================
# FEUILLAGES EN TOUFFES (cartes de houppier)
# =============================================================================

def touffe_feuilles(nom, taille, verts, nb, l_feuille, rapport, fleurs=None, rameaux="#5a4630",
                    graine=1, forme="lanceolee", vieilles=None):
    """Touffe de feuilles disposées autour de rameaux partant du bas-centre."""
    r = random.Random(graine)
    S = taille * SUR
    img = toile(taille, taille)
    d = ImageDraw.Draw(img)
    cx, cy = S / 2, S / 2
    rayon = S * 0.44
    # rameaux
    extremites = []
    for k in range(r.randint(5, 8)):
        a = r.uniform(-math.pi, 0) if r.random() < 0.8 else r.uniform(0, math.pi)
        lng = rayon * r.uniform(0.55, 0.95)
        x1, y1 = cx + lng * math.cos(a), cy + lng * math.sin(a)
        d.line([(cx + r.uniform(-8, 8), cy + S * 0.05), (x1, y1)], fill=hexrgb(rameaux) + (255,),
               width=max(2, int(S * 0.006)))
        extremites.append((x1, y1))
    # feuilles : plus denses au centre, en couronne vers l'extérieur
    for i in range(nb):
        rr = rayon * math.sqrt(r.random()) * 0.92
        a = r.uniform(0, 2 * math.pi)
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        ang = a + r.uniform(-0.7, 0.7)
        lf = l_feuille * S * r.uniform(0.7, 1.15)
        base = hexrgb(r.choice(verts))
        if vieilles and r.random() < vieilles[1]:
            base = hexrgb(r.choice(vieilles[0]))
        lum = -0.25 * (rr / rayon) + r.uniform(-0.1, 0.12)
        c = varier(base, r, 14, lum)
        if forme == "pennee":
            # feuille composée : rachis + petites folioles (flamboyant)
            ca, sa = math.cos(ang), math.sin(ang)
            d.line([(x, y), (x + lf * ca, y + lf * sa)], fill=varier(c, r, 6, -0.2) + (255,), width=max(1, SUR))
            nf = 9
            for j in range(1, nf + 1):
                t = j / (nf + 1)
                px_, py_ = x + lf * t * ca, y + lf * t * sa
                for s in (-1, 1):
                    fa = ang + s * r.uniform(1.0, 1.35)
                    feuille(d, px_, py_, lf * 0.26 * (1 - 0.4 * t), lf * 0.11, fa, varier(c, r, 10))
        else:
            feuille(d, x, y, lf, lf * rapport, ang, c, nervure=varier(c, r, 4, 0.18))
    # fleurs
    if fleurs:
        couleurs, nb_grappes, nb_fleurs, t_fleur = fleurs
        for g in range(nb_grappes):
            rr = rayon * math.sqrt(r.random()) * 0.85
            a = r.uniform(0, 2 * math.pi)
            gx, gy = cx + rr * math.cos(a), cy + rr * math.sin(a) - S * 0.03
            for f in range(nb_fleurs):
                fx = gx + r.gauss(0, S * 0.035)
                fy = gy + r.gauss(0, S * 0.03)
                tf = t_fleur * S * r.uniform(0.7, 1.2)
                c = varier(hexrgb(r.choice(couleurs)), r, 16, r.uniform(-0.15, 0.1))
                rot = r.uniform(0, 2 * math.pi)
                for p in range(5):
                    pa = rot + p * 2 * math.pi / 5
                    feuille(d, fx, fy, tf, tf * 0.8, pa, c, pointe=0.5)
                d.ellipse([fx - tf * 0.18, fy - tf * 0.18, fx + tf * 0.18, fy + tf * 0.18],
                          fill=(250, 214, 90, 255))
    finir(eclaircir_haut(img), nom)


# =============================================================================
# PALME, FEUILLE DE BANANIER, PELOUSE
# =============================================================================

def palme(nom, graine=3):
    """Palme de cocotier vue de dessus : base à gauche, pointe à droite."""
    r = random.Random(graine)
    W, Hh = 1024, 384
    img = toile(W, Hh)
    d = ImageDraw.Draw(img)
    S_w, S_h = W * SUR, Hh * SUR
    cy = S_h / 2
    rachis = []
    for i in range(101):
        t = i / 100
        rachis.append((S_w * (0.02 + 0.96 * t), cy + math.sin(t * 2.2) * S_h * 0.04))
    vert = hexrgb("#4f7a2a")
    for i in range(14, 100, 1):
        t = i / 100
        x0, y0 = rachis[i]
        long_f = S_h * 0.47 * math.sin(math.pi * (0.15 + 0.85 * t)) ** 0.7 * (1.0 - 0.35 * t)
        for s in (-1, 1):
            if r.random() < 0.06:
                continue                          # foliole manquante
            ang = -s * (math.pi / 2 - r.uniform(0.45, 0.7))
            c = varier(vert, r, 16, r.uniform(-0.2, 0.12) + (0.08 if s < 0 else -0.08))
            feuille(d, x0, y0, long_f * r.uniform(0.85, 1.05), S_h * 0.022, ang, c, pointe=1.3)
    d.line(rachis, fill=hexrgb("#9a8f4a") + (255,), width=int(S_h * 0.018))
    finir(img, nom)


def feuille_bananier(nom, graine=5):
    """Feuille de bananier verticale : pétiole en bas, déchirures latérales."""
    r = random.Random(graine)
    W, Hh = 512, 1024
    img = toile(W, Hh)
    d = ImageDraw.Draw(img)
    Sw, Sh = W * SUR, Hh * SUR
    cx = Sw / 2
    vert = hexrgb("#5f8f2c")
    y_bas, y_haut = Sh * 0.97, Sh * 0.03
    pts_g, pts_d = [], []
    for i in range(41):
        t = i / 40
        y = y_bas + (y_haut - y_bas) * t
        demi = Sw * 0.47 * math.sin(math.pi * min(1.0, 0.12 + t * 0.95)) ** 0.6
        pts_g.append((cx - demi, y)); pts_d.append((cx + demi, y))
    d.polygon(pts_g + pts_d[::-1], fill=vert + (255,))
    limbe = img.getchannel("A")
    # nervures latérales (plus claires), limitées au limbe
    nerv = toile(W, Hh)
    dn = ImageDraw.Draw(nerv)
    for k in range(70):
        t = r.uniform(0.05, 0.97)
        y = y_bas + (y_haut - y_bas) * t
        c = varier(vert, r, 10, r.uniform(-0.12, 0.15))
        for s in (-1, 1):
            dn.line([(cx, y), (cx + s * Sw * 0.5, y - Sh * 0.05)], fill=c + (255,), width=SUR * 3)
    vide = Image.new("RGBA", img.size, (0, 0, 0, 0))
    img.alpha_composite(Image.composite(nerv, vide, limbe))
    d = ImageDraw.Draw(img)
    # déchirures (transparentes)
    for k in range(r.randint(6, 10)):
        t = r.uniform(0.15, 0.9)
        y = y_bas + (y_haut - y_bas) * t
        s = r.choice((-1, 1))
        x0 = cx + s * Sw * r.uniform(0.06, 0.2)
        d.line([(x0, y), (cx + s * Sw * 0.52, y - Sh * 0.055)], fill=(0, 0, 0, 0), width=SUR * 2)
    # bord bruni
    contour = pts_g + pts_d[::-1]
    d.line(contour + [contour[0]], fill=hexrgb("#8a7a3a") + (255,), width=SUR * 3)
    d.line([(cx, Sh), (cx, y_haut)], fill=hexrgb("#b9c37a") + (255,), width=SUR * 7)
    finir(eclaircir_haut(img, 0.15), nom)


def herbe(nom, graine=9):
    """Touffe d'herbe / couvre-sol, vue de côté : base en bas."""
    r = random.Random(graine)
    W, Hh = 512, 256
    img = toile(W, Hh)
    d = ImageDraw.Draw(img)
    Sw, Sh = W * SUR, Hh * SUR
    for k in range(260):
        x = r.uniform(Sw * 0.05, Sw * 0.95)
        h = Sh * r.uniform(0.35, 0.95) * (1 - abs(x / Sw - 0.5) * 0.9)
        pench = r.uniform(-0.35, 0.35)
        c = varier(hexrgb(r.choice(["#4f7d27", "#5d8c2e", "#3f6a20", "#6f9a35"])), r, 12, r.uniform(-0.2, 0.15))
        pts = [(x - SUR * 3, Sh), (x + h * pench, Sh - h), (x + SUR * 3, Sh)]
        d.polygon(pts, fill=c + (255,))
    finir(img, nom)


def haie_opaque(nom, graine=11):
    """Texture répétable de haie taillée (feuilles serrées, opaque)."""
    r = random.Random(graine)
    T = 512
    S = T * SUR
    img = Image.new("RGBA", (S, S), hexrgb("#24421a") + (255,))
    d = ImageDraw.Draw(img)
    verts = ["#3c6b24", "#477a2a", "#2f5a1d", "#5a8a32", "#35621f"]
    for i in range(2600):
        x, y = r.uniform(0, S), r.uniform(0, S)
        lf = S * r.uniform(0.03, 0.05)
        ang = r.uniform(0, 2 * math.pi)
        c = varier(hexrgb(r.choice(verts)), r, 12, r.uniform(-0.25, 0.2))
        for ox in (-S, 0, S):
            for oy in (-S, 0, S):
                if -lf < x + ox < S + lf and -lf < y + oy < S + lf:
                    feuille(d, x + ox, y + oy, lf, lf * 0.55, ang, c)
    img = img.resize((T, T), Image.LANCZOS)
    os.makedirs(DOSSIER, exist_ok=True)
    img.convert("RGB").save(os.path.join(DOSSIER, nom), quality=92)
    print("ecrit", nom)


def main():
    random.seed(0)
    touffe_feuilles("ENV_Feuillage_Flamboyant.png", 1024, ["#4c7f25", "#5a8f2c", "#3e6e1f", "#6a9a33"],
                    150, 0.20, 0.3, forme="pennee", graine=21,
                    fleurs=(["#e2361c", "#d1261a", "#f0521e", "#c81f1a"], 15, 24, 0.022))
    touffe_feuilles("ENV_Feuillage_Flamboyant_vert.png", 1024, ["#4c7f25", "#5a8f2c", "#3e6e1f", "#6a9a33"],
                    170, 0.20, 0.3, forme="pennee", graine=22,
                    fleurs=(["#e2361c", "#d1261a", "#f0521e"], 2, 12, 0.022))
    touffe_feuilles("ENV_Feuillage_Manguier.png", 1024, ["#1f4a17", "#2a5a1c", "#173d12", "#35672a"],
                    380, 0.22, 0.24, graine=31, vieilles=(["#7a3a24", "#8f5a2a"], 0.04))
    touffe_feuilles("ENV_Feuillage_Fromager.png", 1024, ["#4d7d2a", "#5b8a33", "#41702a", "#6d9a3c"],
                    260, 0.16, 0.32, graine=41)
    touffe_feuilles("ENV_Feuillage_Tropical.png", 1024, ["#2f6a22", "#3f7d2a", "#286020", "#4a8a30"],
                    300, 0.18, 0.36, graine=51)
    touffe_feuilles("ENV_Bougainvillier.png", 1024, ["#3d6e22", "#4a7d2b"], 140, 0.13, 0.55, graine=61,
                    fleurs=(["#c2187a", "#d61f8c", "#a8126a", "#e13a9d"], 16, 26, 0.022))
    touffe_feuilles("ENV_Hibiscus.png", 1024, ["#2c5e1e", "#376b24", "#24521a"], 240, 0.17, 0.5, graine=71,
                    fleurs=(["#d8141c", "#e52a2a", "#c40f1f"], 10, 3, 0.05))
    palme("ENV_Palme.png")
    feuille_bananier("ENV_Feuille_Bananier.png")
    herbe("ENV_Touffe_Herbe.png")
    haie_opaque("ENV_Haie_color.jpg")


if __name__ == "__main__":
    main()
