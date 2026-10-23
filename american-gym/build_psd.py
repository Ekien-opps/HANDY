"""Assemble le PSD multi-calques de l'affiche retouchée (Photoshop CC / 2026).

Structure (du haut vers le bas) :
  [03] Éléments graphiques   — copies isolées (logo, titres, pictos, bandeaux...),
                               chacune avec un masque de fusion modifiable
  [02] Retouche gazon        — gazon reconstitué + masque de fusion, repère de zone
  [01] Affiche d'origine     — l'affiche source intacte (verrouillée)

Chaque calque d'élément contient exactement les pixels de l'affiche finale :
le rendu global reste identique à l'image retouchée, quel que soit le masque.

Usage : python3 build_psd.py <affiche_source> <dossier_retouche> <sortie.psd>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from psd_tools import PSDImage
from psd_tools.constants import ProtectedFlags
from scipy import ndimage

# (nom, (x0, y0, x1, y1), type de détourage)
ELEMENTS = [
    ("Logo American's Gym", (36, 14, 266, 218), "zone"),
    ("Titre — AMERICAN'S GYM", (40, 252, 528, 310), "blanc"),
    ("Titre — Votre bien-être", (40, 308, 436, 364), "blanc"),
    ("Titre — notre priorité !", (40, 362, 428, 414), "rouge"),
    ("Pictos Sport / Santé / Bien-être", (66, 410, 386, 492), "blanc+rouge"),
    ("Slogan — Plus qu'une salle, un mode de vie !", (896, 12, 1062, 82), "blanc+rouge"),
    ("Bandeau contacts (téléphones, réseaux, adresse)", (0, 625, 800, 720), "zone"),
    ("Signature rouge — L'excellence du fitness", (750, 588, 1080, 720), "signature"),
]


def matte(rgb, kind):
    a = rgb.astype(np.float64)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if kind == "zone":
        return np.full(r.shape, 255.0)
    m = np.zeros(r.shape)
    if "blanc" in kind:
        m = np.maximum(m, np.clip((a.min(-1) - 120) / (215 - 120), 0, 1))
    if "rouge" in kind:
        red = np.clip(((r - np.maximum(g, b)) - 60) / (140 - 60), 0, 1)
        m = np.maximum(m, red)
    if kind == "signature":
        red = (r - np.maximum(g, b)) > 70
        navy = (a.max(-1) < 70) & (b >= g)
        body = ndimage.binary_closing(red | navy, iterations=3)
        body = ndimage.binary_fill_holes(body)            # texte blanc inclus
        body = ndimage.binary_opening(body, iterations=2)
        lbl, n = ndimage.label(body)
        if n:
            sizes = ndimage.sum(body, lbl, range(1, n + 1))
            body = np.isin(lbl, 1 + np.nonzero(sizes > 2000)[0])
        m = ndimage.gaussian_filter(body.astype(float), 0.7)
    return np.clip(m, 0, 1) * 255


def main(src, retouche_dir, out_psd):
    d = Path(retouche_dir)
    orig = Image.open(src).convert("RGB")
    final = Image.open(d / "american_gym_retouche.png").convert("RGB")
    gazon = Image.open(d / "_gazon_rvb.png").convert("RGB")
    gmask = Image.open(d / "_gazon_masque.png").convert("L")
    final_np = np.asarray(final)

    psd = PSDImage.new("RGB", orig.size, depth=8)

    g1 = psd.create_group(name="01 — Affiche d'origine", open_folder=False)
    base = g1.create_pixel_layer(orig, name="Affiche originale (avec bloc vert)")
    base.lock(ProtectedFlags.COMPLETE)

    g2 = psd.create_group(name="02 — Retouche gazon (bloc vert supprimé)")
    x0, y0, x1, y1 = gmask.getbbox()
    pad = 2
    box = (max(x0 - pad, 0), max(y0 - pad, 0), min(x1 + pad, orig.width), min(y1 + pad, orig.height))
    lay = g2.create_pixel_layer(gazon.crop(box), name="Gazon reconstitué", top=box[1], left=box[0])
    lay.create_mask(gmask.crop(box))
    zone = np.zeros((box[3] - box[1], box[2] - box[0], 4), np.uint8)
    zone[..., 0] = 255
    zone[..., 3] = (np.asarray(gmask.crop(box)) > 127) * 110
    rep = g2.create_pixel_layer(Image.fromarray(zone, "RGBA"),
                                name="Repère — zone retouchée (masqué)", top=box[1], left=box[0])
    rep.visible = False

    g3 = psd.create_group(name="03 — Éléments graphiques (calques isolés)")
    for name, (ex0, ey0, ex1, ey1), kind in ELEMENTS:
        crop = final_np[ey0:ey1, ex0:ex1]
        layer = g3.create_pixel_layer(Image.fromarray(crop), name=name, top=ey0, left=ex0)
        layer.create_mask(Image.fromarray(matte(crop, kind).round().astype(np.uint8)))

    flat = psd.create_pixel_layer(final, name="Affiche finale aplatie (référence)")
    flat.visible = False

    psd.save(out_psd)
    print("PSD écrit :", out_psd)


if __name__ == "__main__":
    main(*sys.argv[1:4])
