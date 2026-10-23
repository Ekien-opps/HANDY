"""Affiche des tarifs American's Gym — trois retouches :

  1. Titre : « AMERICAN'S GYMS » -> « AMERICAN'S GYM ». Le S est effacé (papier
     froissé reconstitué), « GYM » est recentré entre les deux barres rouges, et
     les barres sont prolongées symétriquement pour garder l'écart d'origine.
  2. Suppression du cercle vert tracé autour de l'haltère levé.
  3. Haltère levé : plateaux élargis pour avoir la même taille apparente que
     ceux de l'haltère tenu en bas (même hauteur, même largeur de disque).

Usage : python3 retouche_tarifs.py <affiche> <dossier_sortie>
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

from retouche_gazon import laplace_fill, masked_blur, quilt

SEED = 5

# --- titre ---
LETTERS_BOX = (668, 74, 836, 132)       # x0, y0, x1, y1 autour de « GYMS »
S_X0 = 794                              # le S commence après cette colonne
BAR_L = (556, 665, 78, 99)              # barre gauche : x0, x1, y0, y1 (avec halo)
BAR_R = (837, 944, 72, 95)              # barre droite
GAP = 9                                 # écart barre / lettre d'origine

# --- haltère levé : disques (x0, x1, y_dessus, y_dessous) ---
PLATES = [dict(box=(84, 114, 129, 190)),    # disque gauche
          dict(box=(134, 168, 133, 195))]   # disque droit
TARGET_PLATE_W = 35       # largeur des disques de l'haltère du bas (32 à 36 px)
HAND_BOX = (102, 146, 140, 200)

# --- cercle vert ---
LOGO_BOX_X = (78, 216)                  # cartouche blanc du logo, en haut à gauche
LOGO_BOX_BOTTOM = 116                   # ligne de son bord inférieur


def title_fix(img, rng):
    h, w, _ = img.shape
    yy, xx = np.mgrid[:h, :w]
    x0, y0, x1, y1 = LETTERS_BOX
    box = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
    lum = img.mean(-1)
    ink = box & (lum < 205)
    lbl, n = ndimage.label(ink)
    sizes = ndimage.sum(ink, lbl, range(1, n + 1))
    ink = np.isin(lbl, 1 + np.nonzero(sizes >= 40)[0])        # pas de poussières isolées
    hole = ndimage.binary_dilation(ink, iterations=2) & box

    # fond papier sous les lettres
    red = (img[..., 0] > 150) & (img[..., 1] < 140) & (img[..., 0] - img[..., 1] > 50)
    paper = (lum > 200) & ~ndimage.binary_dilation(red, iterations=3)
    paper &= (yy >= 14) & (yy <= 132) & (xx >= 546) & (xx <= 949)
    ok = paper & ~ndimage.binary_dilation(hole, iterations=1)
    L = masked_blur(img.astype(np.float32), ok.astype(np.float32), 5.0).astype(np.float64)
    fill = hole | (ndimage.binary_dilation(hole, iterations=4) & ~ok)
    L = laplace_fill(L, fill, ok & ~fill)
    src = ok & ~ndimage.binary_dilation(ink | red, iterations=4) & (yy >= 60)
    tex = img - L + L.mean(axis=(0, 1))          # plis du papier, éclairage moyen
    T_syn = quilt(tex, ~ndimage.binary_dilation(hole, iterations=1), src, hole, rng)
    # le pli garde son contraste, l'éclairage local reste celui reconstitué
    bg = img.copy()
    bg[hole] = np.clip(T_syn - L.mean(axis=(0, 1)) + L, 0, 255)[hole]
    # pas de point sombre parasite dans le papier reconstitué
    med = np.stack([ndimage.median_filter(bg[..., c], size=7) for c in range(3)], -1)
    speck = hole & (bg.mean(-1) < med.mean(-1) - 25)
    speck = ndimage.binary_dilation(speck, iterations=1) & hole
    bg[speck] = med[speck]

    # lettres G, Y, M : alpha (encre noire sur papier)
    alpha = np.clip(1 - img.mean(-1) / np.maximum(bg.mean(-1), 1), 0, 1) * hole
    alpha[xx >= S_X0] = 0
    cols = np.nonzero(alpha.max(0) > 0.5)[0]
    gym_x0, gym_x1 = cols.min(), cols.max() + 1
    bars_center = (BAR_L[0] + BAR_R[1]) / 2
    dx = int(round(bars_center - (gym_x0 + gym_x1) / 2))

    # barres prolongées vers « GYM » (copie de leur partie centrale, embout conservé)
    out = bg.copy()
    new_l_end = gym_x0 + dx - GAP
    new_r_start = gym_x1 + dx + GAP
    out = extend_bar(out, BAR_L, new_l_end - BAR_L[1], side="right")
    out = extend_bar(out, BAR_R, BAR_R[0] - new_r_start, side="left")

    # recomposition de « GYM » décalé
    a = np.zeros_like(alpha)
    a[:, dx:] = alpha[:, :-dx] if dx > 0 else alpha
    out = out * (1 - a[..., None])
    changed = hole | (a > 0)
    for bx0, bx1, by0, by1 in ((BAR_L[1] - 8, new_l_end + 2, BAR_L[2], BAR_L[3]),
                               (new_r_start - 2, BAR_R[0] + 8, BAR_R[2], BAR_R[3])):
        changed[by0:by1, bx0:bx1] = True
    info = dict(dx=dx, gym=(gym_x0 + dx, gym_x1 + dx), bars=(new_l_end, new_r_start))
    return out, changed, info


def extend_bar(img, bar, n, side):
    """Allonge une barre rouge de n px côté 'right' ou 'left'.

    Les colonnes juste avant l'embout (même hauteur, même nuance, même netteté)
    sont dupliquées, puis l'embout d'origine est replacé au bout."""
    if n <= 0:
        return img
    x0, x1, y0, y1 = bar
    rows = slice(y0, y1)
    cap = 8
    out = img.copy()
    if side == "right":
        body = img[rows, x1 - cap - n:x1 - cap].copy()
        end = img[rows, x1 - cap:x1 + 5].copy()
        out[rows, x1 - cap:x1 - cap + n] = body
        out[rows, x1 - cap + n:x1 + 5 + n] = end
    else:
        body = img[rows, x0 + cap:x0 + cap + n].copy()
        end = img[rows, x0 - 5:x0 + cap].copy()
        out[rows, x0 + cap - n:x0 + cap] = body
        out[rows, x0 - 5 - n:x0 + cap - n] = end
    return out


def remove_green_ring(img):
    """Efface le cercle vert. Les structures dessous (mur, bandes noires, bras)
    sont verticales : chaque colonne est reconstituée entre le pixel valide
    au-dessus et celui en dessous. Si les deux diffèrent (bord du cartouche du
    logo au-dessus), la structure du dessous est prolongée vers le haut."""
    g = img[..., 1] - np.maximum(img[..., 0], img[..., 2])
    ring = g > 25
    lbl, n = ndimage.label(ring)
    sizes = ndimage.sum(ring, lbl, range(1, n + 1))
    ring = lbl == (np.argmax(sizes) + 1)
    hole = ndimage.binary_dilation(ring, iterations=3)
    out = img.copy()
    h = img.shape[0]
    for x in np.nonzero(hole.any(0))[0]:
        col = hole[:, x]
        y = 0
        while y < h:
            if not col[y]:
                y += 1
                continue
            ya = y
            while y < h and col[y]:
                y += 1
            yb = y                                   # run = [ya, yb)
            above = img[max(ya - 2, 0):ya, x].mean(0)
            below = img[yb:min(yb + 2, h), x].mean(0)
            t = (np.arange(ya, yb) - ya + 1) / (yb - ya + 1)
            if np.abs(above - below).mean() > 40:
                out[ya:yb, x] = below                # prolonge la structure du dessous
                if LOGO_BOX_X[0] <= x < LOGO_BOX_X[1] and ya <= LOGO_BOX_BOTTOM:
                    out[ya:LOGO_BOX_BOTTOM, x] = above        # le cartouche du logo garde son bord
                    out[LOGO_BOX_BOTTOM, x] = (above + below) / 2
            else:
                out[ya:yb, x] = above * (1 - t)[:, None] + below * t[:, None]
    # léger grain pour ne pas laisser de zone trop lisse
    rng = np.random.default_rng(3)
    noise = ndimage.gaussian_filter(rng.normal(0, 2.0, img.shape[:2]), 0.6)
    out[hole] += noise[hole][:, None]
    return np.clip(out, 0, 255), hole


def plate_mask(img, box):
    """Disque = ce qui diffère du fond (interpolé colonne par colonne), hors peau,
    complété en forme convexe (partie du bord perdue sur la bande noire)."""
    from skimage.morphology import convex_hull_image
    x0, x1, ya, yb = box
    t = ((np.arange(ya, yb) - ya + 1) / (yb - ya + 1))[:, None, None]
    bg = img[ya - 1, x0:x1][None] * (1 - t) + img[yb, x0:x1][None] * t
    crop = img[ya:yb, x0:x1]
    skin = (crop[..., 0] - crop[..., 2]) > 22
    m = (np.abs(crop - bg).mean(-1) > 22) & ~skin
    m = ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=2))
    m = ndimage.binary_opening(m, iterations=1)
    lbl, n = ndimage.label(m)
    m = lbl == (np.argmax(ndimage.sum(m, lbl, range(1, n + 1))) + 1)
    m = convex_hull_image(m) & ~skin
    return m, bg


def enlarge_dumbbell(img):
    """Élargit les deux disques de l'haltère levé jusqu'à la largeur de ceux de
    l'haltère du bas, à hauteur égale. La main reste devant."""
    out = img.copy()
    h, w, _ = img.shape
    layer = np.zeros((h, w, 4))                       # disques élargis, pleine page
    erase = np.zeros((h, w), bool)
    bgfill = np.zeros((h, w, 3))
    for pl in PLATES:
        x0, x1, ya, yb = pl["box"]
        m, bg = plate_mask(img, pl["box"])
        cols = np.nonzero(m.any(0))[0]
        sx = TARGET_PLATE_W / (cols.max() - cols.min() + 1)
        # ancre : centre du disque (le disque s'élargit des deux côtés, la main reste devant)
        inner = x0 + (cols.min() + cols.max() + 1) / 2
        alpha = ndimage.gaussian_filter(m.astype(float), 0.6) * ndimage.binary_dilation(m, iterations=1)
        src = Image.fromarray(np.dstack([img[ya:yb, x0:x1], alpha * 255]).astype(np.uint8), "RGBA").convert("RGBa")
        # étirement horizontal autour du centre : x_nouveau = inner + (x - inner) * sx
        nx0 = int(np.floor(inner + (x0 - inner) * sx))
        nx1 = int(np.ceil(inner + (x1 - inner) * sx))
        c = (inner - x0) + (nx0 - inner) / sx           # source locale de la colonne nx0
        big = src.transform((nx1 - nx0, yb - ya), Image.AFFINE, (1 / sx, 0, c, 0, 1, 0),
                            resample=Image.BICUBIC).convert("RGBA")
        layer[ya:yb, nx0:nx1] = np.asarray(big).astype(np.float64)
        er = np.zeros((h, w), bool)
        er[ya:yb, x0:x1] = ndimage.binary_dilation(m, iterations=1)
        erase |= er
        bgfill[ya:yb, x0:x1][er[ya:yb, x0:x1]] = bg[er[ya:yb, x0:x1]]
    a = layer[..., 3:4] / 255
    # 1) l'ancien disque n'est effacé que là où le nouveau ne le recouvre pas
    hx0, hx1, hy0, hy1 = HAND_BOX
    near_hand = np.zeros((h, w), bool)
    crop = img[hy0:hy1, hx0:hx1]
    near_hand[hy0:hy1, hx0:hx1] = ndimage.binary_dilation((crop[..., 0] - crop[..., 2]) > 22, iterations=3)
    gone = erase & (a[..., 0] < 0.5) & ~near_hand
    out[gone] = bgfill[gone]
    # 2) disques élargis
    out = layer[..., :3] * a + out * (1 - a)
    # 3) la main repasse devant
    skin_a = np.clip(((crop[..., 0] - crop[..., 2]) - 12) / 20, 0, 1)
    skin_a = ndimage.gaussian_filter(skin_a, 0.5)[..., None]
    out[hy0:hy1, hx0:hx1] = crop * skin_a + out[hy0:hy1, hx0:hx1] * (1 - skin_a)
    return np.clip(out, 0, 255)


def main(src, out_dir):
    out_dir = Path(out_dir)
    rng = np.random.default_rng(SEED)
    orig = Image.open(src).convert("RGB")
    img = np.asarray(orig).astype(np.float64)
    stages = [("Titre — AMERICAN'S GYM (S retiré, barres prolongées)", None),
              ("Cercle vert supprimé", None), ("Haltère levé agrandi", None)]
    s1, _, info = title_fix(img, rng)
    s1 = np.round(np.clip(s1, 0, 255))
    s2, _ = remove_green_ring(s1)
    s2 = np.round(s2)
    s3 = np.round(enlarge_dumbbell(s2))
    print("titre :", info)
    final = s3.astype(np.uint8)
    stem = "american_gym_tarifs_retouche"
    Image.fromarray(final).save(out_dir / f"{stem}.png", optimize=True)
    Image.fromarray(final).save(out_dir / f"{stem}.jpg", quality=97, subsampling=0)

    # PSD : original verrouillé + un calque par retouche (pixels modifiés uniquement)
    from psd_tools import PSDImage
    from psd_tools.constants import ProtectedFlags
    psd = PSDImage.new("RGB", orig.size, depth=8)
    psd.create_pixel_layer(orig, name="Affiche originale").lock(ProtectedFlags.COMPLETE)
    prev = img
    for (name, _), cur in zip(stages, (s1, s2, s3)):
        diff = np.abs(cur - prev).max(-1) > 0
        ys, xs = np.nonzero(diff)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        rgba = np.dstack([cur, diff * 255.0])[y0:y1, x0:x1].astype(np.uint8)
        psd.create_pixel_layer(Image.fromarray(rgba, "RGBA"), name=name, top=int(y0), left=int(x0))
        print(f"{name} : {diff.sum()} px (x {x0}-{x1}, y {y0}-{y1})")
        prev = cur
    ref = psd.create_pixel_layer(Image.fromarray(final), name="Affiche retouchée aplatie (référence)")
    ref.visible = False
    psd.save(out_dir / f"{stem}.psd")
    chk = np.asarray(PSDImage.open(out_dir / f"{stem}.psd").composite(force=True, ignore_preview=True).convert("RGB"))
    print("PSD = image finale :", np.abs(chk.astype(int) - final.astype(int)).max() == 0)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
