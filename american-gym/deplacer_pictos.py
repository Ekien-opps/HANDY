"""Affiche American's Gym (v2) : descend les pictos Sport / Santé / Bien-être
(avec leurs textes et les séparateurs rouges) au niveau des chevilles de la
sportive, avec un léger agrandissement, et reconstitue naturellement le fond
(zone sombre + gazon) à leur ancien emplacement. Rien d'autre n'est modifié.

Méthode :
  1. Détourage : alpha des tracés blancs et des séparateurs rouges, estimé par
     rapport au fond reconstitué (contours anti-crénelés conservés).
  2. Fond : éclairage par équation de Laplace + texture par patchs (même
     méthode que retouche_gazon.py) sous les tracés et leur halo de compression.
  3. Agrandissement (bicubique, alpha prémultiplié) et recomposition : le centre
     des cercles est placé à la hauteur des chevilles, l'axe horizontal du bloc
     est conservé.

Usage : python3 deplacer_pictos.py <affiche_v2> <dossier_sortie>
Écrit aussi les calques (fond reconstitué, pictos détourés) pour build_psd_v2.py.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from retouche_gazon import quilt

SCALE = 1.15                         # léger agrandissement
CIRCLE_CY = 441                      # centre des cercles à l'origine (y)
ANKLE_Y = 530                        # hauteur des chevilles (jonction chaussette / basket)
ZONE = (66, 411, 384, 489)           # x0, y0, x1, y1 : pictos + textes + séparateurs
RED_COLS = ((150, 168), (270, 288))  # colonnes des deux séparateurs rouges
SEED = 11
# découpe en calques : (nom, x0, x1) — chaque picto avec son texte, puis les séparateurs
ELEMENTS = [("Picto Sport", 66, 145), ("Séparateur rouge 1", 145, 172),
            ("Picto Santé", 172, 265), ("Séparateur rouge 2", 265, 292),
            ("Picto Bien-être", 292, 390)]


def main(src, out_dir):
    out_dir = Path(out_dir)
    rng = np.random.default_rng(SEED)
    img = np.asarray(Image.open(src).convert("RGB")).astype(np.float64)
    h, w, _ = img.shape
    yy, xx = np.mgrid[:h, :w]
    x0, y0, x1, y1 = ZONE
    zone = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)

    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    in_red = np.zeros((h, w), bool)
    for c0, c1 in RED_COLS:
        in_red |= (xx >= c0) & (xx < c1)
    mn = img.min(-1)
    # tracés blancs : nettement plus clairs que leur voisinage (le gazon clair n'en fait pas partie)
    white = (mn > 55) & ((mn > ndimage.median_filter(mn, size=17) + 30) | (mn > 150))
    red = (r - np.maximum(g, b)) > 35
    strokes = zone & (white | (red & in_red))
    # tracés + contour anti-crénelé + halo de compression
    hole = ndimage.binary_dilation(strokes, iterations=7) & (yy >= y0 - 1) & (yy < y1 + 3) & (xx < x1 + 4)

    # 1) fond reconstitué sous les tracés. Le fond est fait de reflets horizontaux
    #    (sol de la salle, gazon) : l'éclairage est interpolé ligne par ligne.
    known = ~ndimage.binary_dilation(hole, iterations=1)
    ok = known & ~ndimage.binary_dilation(white | ((r - np.maximum(g, b)) > 40), iterations=3)
    okf = ok.astype(np.float32)
    num = ndimage.gaussian_filter(img * okf[..., None], (1.2, 5.0, 0))
    den = ndimage.gaussian_filter(okf, (1.2, 5.0))
    S = num / np.maximum(den, 1e-4)[..., None]
    L = S.copy()
    fill = hole | (ndimage.binary_dilation(hole, iterations=6) & ~ok)
    for y in np.nonzero(fill.any(1))[0]:
        kx = np.nonzero(ok[y] & (den[y] > 0.3) & (xx[y] < 480))[0]
        fx = np.nonzero(fill[y])[0]
        for c in range(3):
            L[y, fx, c] = np.interp(fx, kx, S[y, kx, c])
    L[fill] = ndimage.gaussian_filter(L, (0.8, 0, 0))[fill]
    T = img - S
    region = (xx < 470) & (yy >= 396) & (yy < 540)
    source_ok = ok & region & ~ndimage.binary_dilation(hole, iterations=3)
    T_syn = quilt(T, known, source_ok, hole, rng)
    bg = img.copy()
    bg[hole] = np.clip(L + T_syn, 0, 255)[hole]

    # 2) détourage des pictos (alpha + couleur de premier plan)
    f_white = img[strokes & ~in_red & (img.min(-1) > 200)].mean(0)
    f_red = img[strokes & in_red & red].mean(0) if (strokes & in_red & red).any() else np.array([220., 30, 40])
    f_const = np.where(in_red[..., None] & red[..., None], f_red, f_white)
    alpha = ((img - bg) * (f_const - bg)).sum(-1) / np.maximum(((f_const - bg) ** 2).sum(-1), 1)
    alpha = np.clip(alpha, 0, 1) * (hole & zone & ~(red & ~in_red))   # jamais le titre rouge au-dessus
    alpha[alpha < 0.04] = 0
    a8 = np.round(alpha * 255) / 255
    f_est = bg + (img - bg) / np.maximum(a8, 1e-3)[..., None]
    wgt = np.clip(a8 / 0.35, 0, 1)[..., None]
    fg = np.clip(wgt * f_est + (1 - wgt) * f_const, 0, 255)
    fg = np.round(fg)

    # 3) agrandissement + placement au niveau des chevilles
    ys_, xs_ = np.nonzero(a8 > 0)
    cx = (xs_.min() + xs_.max() + 1) / 2
    ty = ANKLE_Y - CIRCLE_CY * SCALE                 # y_nouveau = ty + SCALE * y_origine
    rgba_src = Image.fromarray(np.dstack([fg, a8 * 255]).round().astype(np.uint8), "RGBA")
    inv = 1 / SCALE                                   # sortie (x, y) -> source
    moved = rgba_src.convert("RGBa").transform(
        (w, h), Image.AFFINE, (inv, 0, cx - cx * inv, 0, inv, -ty * inv),
        resample=Image.BICUBIC).convert("RGBA")
    mv = np.asarray(moved).astype(np.float64)
    a_new = np.round(mv[..., 3]) / 255
    fg_new = mv[..., :3]
    bg8 = np.round(bg)
    final = fg_new * a_new[..., None] + bg8 * (1 - a_new[..., None])
    final = np.clip(np.round(final), 0, 255).astype(np.uint8)

    stem = "american_gym_v2_pictos_chevilles"
    Image.fromarray(final).save(out_dir / f"{stem}.png", optimize=True)
    Image.fromarray(final).save(out_dir / f"{stem}.jpg", quality=97, subsampling=0)
    # calques pour le PSD
    Image.fromarray(bg8.astype(np.uint8)).save(out_dir / "_v2_fond.png")
    # plein (255) sur toute la zone recomposée, bord adouci à l'extérieur (où fond = original)
    soft = ndimage.gaussian_filter(ndimage.binary_dilation(hole, iterations=2).astype(float), 1.0)
    soft = np.where(hole, 1.0, soft) * 255
    Image.fromarray(np.round(soft).astype(np.uint8)).save(out_dir / "_v2_fond_masque.png")
    rgba = np.asarray(moved).copy()
    for i, (name, ex0, ex1) in enumerate(ELEMENTS):
        nx0 = int(np.floor(cx + (ex0 - cx) * SCALE))
        nx1 = int(np.floor(cx + (ex1 - cx) * SCALE))
        part = np.zeros_like(rgba)
        part[:, nx0:nx1] = rgba[:, nx0:nx1]
        Image.fromarray(part, "RGBA").save(out_dir / f"_v2_calque_{i}.png")
    changed = np.abs(final.astype(int) - img.round().astype(int)).max(-1) > 0
    ys, xs = np.nonzero(changed)
    ya, xa = np.nonzero(a_new > 0)
    print(f"pictos : x {xa.min()}-{xa.max()}, y {ya.min()}-{ya.max()} (échelle {SCALE})")
    print(f"pixels modifiés : {changed.sum()} (zone x {xs.min()}-{xs.max()}, y {ys.min()}-{ys.max()})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
