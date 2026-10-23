"""Affiche American's Gym v3 : même structure que la v2, nouvelle photo
(athlète aux haltères) et nouvelle accroche. Produit l'image finale et un PSD
dont chaque élément est un vrai calque séparé.

Éléments repris de la v2 : cartouche logo, pictos Sport / Santé / Bien-être
(calques détourés par deplacer_pictos.py), bandeau slogan, bandeau contacts.
Textes recomposés en Montserrat (police de l'affiche d'origine).

Usage : python3 affiche_v3.py <affiche_v2> <photo> <dossier_calques_v2> <dossier_sortie>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from psd_tools import PSDImage
from psd_tools.constants import ProtectedFlags
from scipy import ndimage

from deplacer_pictos import ELEMENTS as PICTOS

W, H = 1080, 720
FONTS = Path(__file__).parent / "fonts"
DARK = (9, 14, 19)
WHITE = (249, 252, 254)
RED = (236, 24, 39)

TITLE = "AMERICAN’S GYM"
ACCROCHE = ("Plus fort chaque jour,", "mieux dans votre peau !")

PHOTO_SCALE = 1.6            # 612×408 -> 979×653
PHOTO_LEFT = 186             # genou gauche de l'athlète vers x = 450
TEXT_X = 46
BAND_TOP, RED_BAND_TOP = 607, 664


def font(weight, size):
    return ImageFont.truetype(str(FONTS / f"Montserrat-{weight}.ttf"), size)


def draw_text(text, fnt, color, x, y):
    """Calque RGBA pleine page : texte + ombre portée douce (lisibilité sur la photo)."""
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).text((x + 2, y + 3), text, font=fnt, fill=150)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.putalpha(sh.filter(ImageFilter.GaussianBlur(4)))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(txt).text((x, y), text, font=fnt, fill=color + (255,))
    return Image.alpha_composite(layer, txt)


def logo_panel(v2):
    """Cartouche blanc à coin arrondi + logo, détouré de l'affiche v2."""
    a = np.asarray(v2).astype(np.float64)
    white = a.min(-1) > 232
    lbl, _ = ndimage.label(white)
    panel = lbl == lbl[5, 5]
    panel = ndimage.binary_fill_holes(panel)
    panel[250:] = False
    disk = np.hypot(*np.mgrid[-6:7, -6:7]) <= 6
    panel = ndimage.binary_opening(panel, structure=disk)     # supprime les éclats du fond
    panel = ndimage.binary_fill_holes(panel)
    # contour lissé et anti-crénelé
    soft = ndimage.gaussian_filter(panel.astype(float), 1.2)
    alpha = np.clip((soft - 0.5) * 2.2 + 0.5, 0, 1)
    rgb = a.copy()
    rim = alpha < 1
    rgb[rim] = WHITE                       # pas de liseré de l'ancien fond
    return Image.fromarray(np.dstack([rgb, alpha * 255]).round().astype(np.uint8), "RGBA")


def main(v2_path, photo_path, calques_dir, out_dir):
    out_dir = Path(out_dir)
    v2 = Image.open(v2_path).convert("RGB")
    layers = []                            # (nom, image RGBA pleine page, groupe)

    # 1) fond sombre + photo agrandie
    layers.append(("Fond sombre", Image.new("RGBA", (W, H), DARK + (255,)), "Fond"))
    photo = Image.open(photo_path).convert("RGB")
    pw, ph = round(photo.width * PHOTO_SCALE), round(photo.height * PHOTO_SCALE)
    big = photo.resize((pw, ph), Image.LANCZOS).filter(
        ImageFilter.UnsharpMask(radius=1.4, percent=55, threshold=2))
    ph_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ph_layer.paste(big, (PHOTO_LEFT, 0))
    layers.append(("Photo — athlète aux haltères", ph_layer, "Fond"))

    # 2) dégradé sombre pour la lisibilité (comme sur la v2)
    xx = np.arange(W, dtype=float)
    t = np.clip((xx - 170) / (660 - 170), 0, 1)
    ax = 1 - t * t * (3 - 2 * t)
    yy = np.arange(H, dtype=float)[:, None]
    ay = np.clip((yy - 540) / (BAND_TOP - 540), 0, 1) * 0.55       # assise au-dessus du bandeau
    alpha = np.clip(np.maximum(ax[None, :] * 0.97, ay), 0, 1)
    grad = np.dstack([np.full((H, W, 3), DARK, float), alpha * 255]).round().astype(np.uint8)
    layers.append(("Dégradé sombre (lisibilité)", Image.fromarray(grad, "RGBA"), "Fond"))

    # 3) logo
    layers.append(("Cartouche logo American's Gym", logo_panel(v2), "Logo"))

    # 4) textes
    f_title = font(800, 60)
    while f_title.getlength(TITLE) > 500:
        f_title = f_title.font_variant(size=f_title.size - 1)
    y = 252
    layers.append(("Titre — AMERICAN'S GYM", draw_text(TITLE, f_title, WHITE, TEXT_X, y), "Textes"))
    asc = f_title.getbbox(TITLE)[3]
    f_acc = font(800, f_title.size - 6)
    while max(f_acc.getlength(s) for s in ACCROCHE) > 510:
        f_acc = f_acc.font_variant(size=f_acc.size - 1)
    y += asc + 6
    layers.append((f"Accroche — {ACCROCHE[0]}", draw_text(ACCROCHE[0], f_acc, WHITE, TEXT_X + 2, y), "Textes"))
    y += f_acc.size + 8
    layers.append((f"Accroche — {ACCROCHE[1]}", draw_text(ACCROCHE[1], f_acc, RED, TEXT_X + 2, y), "Textes"))
    text_bottom = y + f_acc.getbbox(ACCROCHE[1])[3]

    # 5) pictos (calques détourés de la v2), centrés sous les textes
    parts = [Image.open(Path(calques_dir) / f"_v2_calque_{i}.png").convert("RGBA") for i in range(len(PICTOS))]
    union = None
    for p in parts:
        bb = p.getchannel("A").getbbox()
        union = bb if union is None else (min(union[0], bb[0]), min(union[1], bb[1]),
                                          max(union[2], bb[2]), max(union[3], bb[3]))
    block_h = union[3] - union[1]
    top = text_bottom + (BAND_TOP - text_bottom - block_h) // 2
    dx, dy = TEXT_X + 4 - union[0], top - union[1]
    for (name, _, _), p in zip(PICTOS, parts):
        moved = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        moved.paste(p, (dx, dy))
        layers.append((name, moved, "Pictos"))

    # 6) bandeaux du bas, identiques à la v2
    for name, y0, y1 in (("Bandeau slogan", BAND_TOP, RED_BAND_TOP), ("Bandeau contacts", RED_BAND_TOP, H)):
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        band.paste(v2.crop((0, y0, W, y1)), (0, y0))
        layers.append((name, band, "Bandeaux"))

    # composition
    final = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    for _, im, _ in layers:
        final = Image.alpha_composite(final, im)
    final = final.convert("RGB")
    stem = "american_gym_v3_athlete"
    final.save(out_dir / f"{stem}.png", optimize=True)
    final.save(out_dir / f"{stem}.jpg", quality=97, subsampling=0)

    # PSD
    psd = PSDImage.new("RGB", (W, H), depth=8)
    groups = {}
    order = ["Fond", "Logo", "Textes", "Pictos", "Bandeaux"]
    names = {"Fond": "01 — Fond (photo + dégradé)", "Logo": "02 — Logo",
             "Textes": "03 — Titre et accroche", "Pictos": "04 — Pictos Sport / Santé / Bien-être",
             "Bandeaux": "05 — Bandeaux slogan et contacts"}
    for g in order:
        groups[g] = psd.create_group(name=names[g])
    for name, im, g in layers:
        bb = im.getchannel("A").getbbox()
        lay = groups[g].create_pixel_layer(im.crop(bb), name=name, top=bb[1], left=bb[0])
        if name == "Fond sombre":
            lay.lock(ProtectedFlags.COMPLETE)
    ref = psd.create_pixel_layer(final, name="Affiche finale aplatie (référence)")
    ref.visible = False
    psd.save(out_dir / f"{stem}.psd")

    chk = PSDImage.open(out_dir / f"{stem}.psd")
    comp = np.asarray(chk.composite(force=True, ignore_preview=True).convert("RGB")).astype(int)
    diff = np.abs(comp - np.asarray(final).astype(int))
    print(f"accroche : {f_acc.size}px, titre : {f_title.size}px, pictos y {top}-{top + block_h}")
    print(f"PSD : écart max avec l'image finale {diff.max()} ({(diff.max(-1) > 1).sum()} px > 1)")


if __name__ == "__main__":
    main(*sys.argv[1:5])
