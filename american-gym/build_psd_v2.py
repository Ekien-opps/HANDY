"""PSD multi-calques de l'affiche v2 (pictos descendus aux chevilles, agrandis).

Structure (du haut vers le bas) :
  Affiche finale aplatie (référence, masquée)
  [03] Pictos Sport / Santé / Bien-être — 5 calques détourés (transparence réelle) :
       ils peuvent être déplacés, redimensionnés ou stylés librement
  [02] Fond reconstitué — gazon / zone sombre à l'ancien emplacement des pictos
  [01] Affiche d'origine (verrouillée)

Usage : python3 build_psd_v2.py <affiche_v2> <dossier_calques> <sortie.psd>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from psd_tools import PSDImage
from psd_tools.constants import ProtectedFlags

from deplacer_pictos import ELEMENTS


def main(src, d, out_psd):
    d = Path(d)
    orig = Image.open(src).convert("RGB")
    fond = Image.open(d / "_v2_fond.png").convert("RGB")
    masque = Image.open(d / "_v2_fond_masque.png").convert("L")
    final = Image.open(d / "american_gym_v2_pictos_chevilles.png").convert("RGB")

    psd = PSDImage.new("RGB", orig.size, depth=8)
    g1 = psd.create_group(name="01 — Affiche d'origine", open_folder=False)
    g1.create_pixel_layer(orig, name="Affiche originale").lock(ProtectedFlags.COMPLETE)

    g2 = psd.create_group(name="02 — Fond reconstitué (ancien emplacement des pictos)")
    box = masque.getbbox()
    lay = g2.create_pixel_layer(fond.crop(box), name="Gazon et zone sombre reconstitués",
                                top=box[1], left=box[0])
    lay.create_mask(masque.crop(box))

    g3 = psd.create_group(name="03 — Pictos Sport / Santé / Bien-être (aux chevilles, agrandis 115 %)")
    for i, (name, _, _) in enumerate(ELEMENTS):
        im = Image.open(d / f"_v2_calque_{i}.png").convert("RGBA")
        bb = im.getchannel("A").getbbox()
        if bb:
            g3.create_pixel_layer(im.crop(bb), name=name, top=bb[1], left=bb[0])

    flat = psd.create_pixel_layer(final, name="Affiche finale aplatie (référence)")
    flat.visible = False
    psd.save(out_psd)

    chk = PSDImage.open(out_psd)
    comp = np.asarray(chk.composite(force=True, ignore_preview=True).convert("RGB")).astype(int)
    diff = np.abs(comp - np.asarray(final).astype(int))
    print(f"PSD écrit : {out_psd} — écart max avec l'image finale : {diff.max()} "
          f"({(diff.max(-1) > 0).sum()} px)")


if __name__ == "__main__":
    main(*sys.argv[1:4])
