"""Retouche de l'affiche American's Gym : suppression du bloc vert fluo (#01e406)
et reconstitution du gazon synthétique.

Méthode :
  1. Détection du bloc vert (+ marge anti-crénelage / bavure de compression).
  2. Séparation éclairage / texture : L = éclairage basse fréquence,
     T = I / L = texture (grain, brins, micro-ombres).
  3. L est reconstruit dans le trou par résolution de l'équation de Laplace
     (continuité parfaite du dégradé de lumière et du vignettage).
  4. T est synthétisée par « image quilting » : des patchs de vrai gazon, pris
     sur les mêmes lignes (même échelle de perspective), sont assemblés avec
     coutures à erreur minimale.
  5. Recomposition I = L * T, puis reconstruction du fondu gazon -> bandeau blanc.

Usage : python3 retouche_gazon.py <affiche_source> <dossier_sortie>
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage, sparse
from scipy.sparse.linalg import spsolve

SEED = 7
GRASS_LAST_ROW = 622      # dernière ligne de gazon avant le fondu du bandeau blanc
PATCH, OVERLAP = 22, 8
ROW_TOLERANCE = 18        # écart de ligne max entre patch source et cible (perspective)


def green_block_mask(img):
    r, g, b = (img[..., i] for i in range(3))
    core = (g > 150) & (r < 90) & (b < 90) & (g - np.maximum(r, b) > 110)
    core = ndimage.binary_opening(core, iterations=1)
    lbl, n = ndimage.label(core)
    sizes = ndimage.sum(core, lbl, range(1, n + 1))
    core = lbl == (np.argmax(sizes) + 1)
    core = ndimage.binary_fill_holes(core)
    # marge pour le contour anti-crénelé et la bavure chroma de la compression
    return ndimage.binary_dilation(core, iterations=4)


def masked_blur(img, valid, sigma):
    w = cv2.GaussianBlur(valid.astype(np.float32), (0, 0), sigma)
    out = np.stack([cv2.GaussianBlur(img[..., c] * valid, (0, 0), sigma)
                    for c in range(3)], -1)
    return out / np.maximum(w, 1e-4)[..., None]


def laplace_fill(field, hole, known):
    """Remplit field dans hole (Dirichlet sur known, Neumann ailleurs)."""
    ys, xs = np.nonzero(hole)
    idx = -np.ones(hole.shape, np.int64)
    idx[ys, xs] = np.arange(len(ys))
    n = len(ys)
    rows, cols, vals = [], [], []
    rhs = np.zeros((n, field.shape[2]))
    diag = np.zeros(n)
    h, w = hole.shape
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        ny, nx = ys + dy, xs + dx
        inside = (ny >= 0) & (ny < h) & (nx >= 0) & (nx < w)
        k = np.nonzero(inside)[0]
        nyk, nxk = ny[k], nx[k]
        unk = hole[nyk, nxk]
        kn = known[nyk, nxk] & ~unk
        diag[k[unk | kn]] += 1
        rows += list(k[unk]); cols += list(idx[nyk[unk], nxk[unk]]); vals += [-1.0] * int(unk.sum())
        rhs[k[kn]] += field[nyk[kn], nxk[kn]]
    A = sparse.csr_matrix((vals, (rows, cols)), shape=(n, n)) + sparse.diags(diag)
    out = field.copy()
    for c in range(field.shape[2]):
        out[ys, xs, c] = spsolve(A.tocsc(), rhs[:, c])
    return out


def min_cut_path(err, axis):
    """Chemin de coût minimal (programmation dynamique). axis=0 : vertical."""
    e = err if axis == 0 else err.T
    cost = e.copy()
    for i in range(1, cost.shape[0]):
        prev = cost[i - 1]
        left = np.r_[np.inf, prev[:-1]]
        right = np.r_[prev[1:], np.inf]
        cost[i] += np.minimum(np.minimum(left, prev), right)
    path = np.zeros(cost.shape[0], int)
    path[-1] = int(np.argmin(cost[-1]))
    for i in range(cost.shape[0] - 2, -1, -1):
        j = path[i + 1]
        lo, hi = max(j - 1, 0), min(j + 2, cost.shape[1])
        path[i] = lo + int(np.argmin(cost[i, lo:hi]))
    return path


def quilt(tex, known, source_ok, hole, rng):
    """Synthèse de texture par patchs dans hole, à partir des zones source_ok."""
    canvas = tex.copy()
    filled = known.copy()
    h, w = hole.shape
    ys, xs = np.nonzero(hole)
    y_lo, y_hi, x_lo, x_hi = ys.min(), ys.max(), xs.min(), xs.max()
    step = PATCH - OVERLAP
    # positions source valides : patch entier dans du gazon propre
    src_valid = ndimage.binary_erosion(source_ok, np.ones((PATCH, PATCH)), border_value=0)
    src_valid = np.roll(np.roll(src_valid, -(PATCH // 2), 0), -(PATCH // 2), 1)  # coin haut-gauche
    tex32 = tex.astype(np.float32)
    for y0 in range(max(y_lo - OVERLAP, 0), y_hi + 1, step):
        y0 = min(y0, h - PATCH)
        for x0 in range(max(x_lo - OVERLAP, 0), x_hi + 1, step):
            x0 = min(x0, w - PATCH)
            sl = (slice(y0, y0 + PATCH), slice(x0, x0 + PATCH))
            need = hole[sl] & ~filled[sl]
            if not need.any():
                continue
            m = filled[sl].astype(np.float32)
            # bande de lignes source de même échelle de perspective
            sy0 = max(y0 - ROW_TOLERANCE, 0)
            sy1 = min(y0 + ROW_TOLERANCE + PATCH, h)
            strip = tex32[sy0:sy1]
            if m.sum() > 0:
                ssd = cv2.matchTemplate(strip, canvas[sl].astype(np.float32),
                                        cv2.TM_SQDIFF, mask=np.repeat(m[..., None], 3, 2))
                ssd /= m.sum()
            else:
                ssd = np.zeros((strip.shape[0] - PATCH + 1, strip.shape[1] - PATCH + 1), np.float32)
            valid = src_valid[sy0:sy0 + ssd.shape[0], :ssd.shape[1]]
            ssd = np.where(valid & np.isfinite(ssd), ssd, np.inf)
            best = ssd.min()
            cand = np.argwhere(ssd <= best * 1.15 + 1e-6)
            cy, cx = cand[rng.integers(len(cand))]
            patch = tex[sy0 + cy:sy0 + cy + PATCH, cx:cx + PATCH]
            # couture à erreur minimale sur les recouvrements déjà synthétisés
            take = np.ones((PATCH, PATCH), bool)
            prev = filled[sl] & hole[sl]
            err = ((patch - canvas[sl]) ** 2).sum(-1)
            if prev[:, :OVERLAP].any():
                e = np.where(prev[:, :OVERLAP], err[:, :OVERLAP], 0)
                p = min_cut_path(e, 0)
                for i, j in enumerate(p):
                    take[i, :j] = False
            if prev[:OVERLAP, :].any():
                e = np.where(prev[:OVERLAP, :], err[:OVERLAP, :], 0)
                p = min_cut_path(e, 1)
                for j, i in enumerate(p):
                    take[:i, j] = False
            take &= hole[sl]                 # on ne touche jamais aux pixels d'origine
            take |= need                     # tout pixel manquant doit être rempli
            canvas[sl][take] = patch[take]
            filled[sl] |= take
    return canvas


def main(src, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    img = np.asarray(Image.open(src).convert("RGB")).astype(np.float64)
    h, w, _ = img.shape
    yy, xx = np.mgrid[:h, :w]

    hole = green_block_mask(img)
    grass_rows = yy <= GRASS_LAST_ROW
    hole_grass = hole & grass_rows

    # pixels qui ne sont pas du gazon (textes, icônes, sujet, bandeaux) : exclus des sources
    sm = cv2.GaussianBlur(img.astype(np.float32), (0, 0), 2.0)
    r, g, b = sm[..., 0], sm[..., 1], sm[..., 2]
    grassy = (g > r + 18) & (g > b + 12) & (g < 200) & (np.max(sm, -1) - np.min(sm, -1) < 120)
    grassy = ndimage.binary_opening(grassy, iterations=2)
    not_grass = ndimage.binary_dilation(~grassy, iterations=3)
    base_known = ~ndimage.binary_dilation(hole, iterations=1) & grass_rows

    # 1) éclairage basse fréquence
    lum_valid = base_known & ~ndimage.binary_dilation(
        (np.min(img, -1) > 150) | (img[..., 0] > img[..., 1] + 40), iterations=4)
    L = masked_blur(img.astype(np.float32), lum_valid.astype(np.float32), 9.0).astype(np.float64)
    L = np.maximum(L, 4.0)
    fill_zone = hole_grass | (ndimage.binary_dilation(hole_grass, iterations=2) & ~lum_valid & grass_rows)
    L_filled = laplace_fill(L, fill_zone, lum_valid & ~fill_zone)

    # 2) texture relative (grain) — log pour une meilleure homogénéité
    T = np.log(img + 1.0) - np.log(L_filled + 1.0)

    # 3) synthèse de texture
    source_ok = grassy & ~not_grass & base_known & (yy >= 440) & (yy <= GRASS_LAST_ROW)
    source_ok &= ~ndimage.binary_dilation(hole, iterations=6)
    T_syn = quilt(T, base_known & ~hole_grass, source_ok, hole_grass, rng)

    rec = np.exp(np.log(L_filled + 1.0) + T_syn) - 1.0
    out = img.copy()
    out[hole_grass] = rec[hole_grass]

    # 4) fondu gazon -> bandeau blanc. Les colonnes voisines du bloc portent aussi un
    #    halo sombre de compression (ringing) : la zone réparée est élargie de 50 px.
    ref_cols = (~hole[GRASS_LAST_ROW]) & (xx[0] > 180) & (xx[0] < 460)
    g_ref = img[GRASS_LAST_ROW - 1:GRASS_LAST_ROW + 1, ref_cols].mean(0)
    white_ref = img[629:633, ref_cols].mean(0)
    hole_cols = hole[GRASS_LAST_ROW - 4:GRASS_LAST_ROW + 1].any(0)
    x_end = np.nonzero(hole_cols)[0].max() + 50
    band_w = np.clip((x_end - xx[0]) / 20.0, 0, 1)        # fondu horizontal sur 20 px
    band_w[~(hole_cols | (xx[0] <= x_end))] = 0
    white = img[629:633].mean(0)
    band_alpha = np.zeros((h, w))
    for y in range(GRASS_LAST_ROW + 1, 629):
        a = np.clip(((img[y, ref_cols] - g_ref) / np.maximum(white_ref - g_ref, 1)).mean(), 0, 1)
        if y >= 626:
            a = 1.0
        grass = out[2 * GRASS_LAST_ROW - y + 1]            # ligne miroir : garde le grain
        fixed = a * white + (1 - a) * grass
        out[y] = band_w[:, None] * fixed + (1 - band_w[:, None]) * img[y]
        band_alpha[y] = band_w
    # le gazon d'origine dans le halo de compression est lui aussi remplacé
    for y in range(GRASS_LAST_ROW - 2, GRASS_LAST_ROW + 1):
        halo = band_w * ~hole[y]
        out[y] = halo[:, None] * out[y - 3] + (1 - halo[:, None]) * out[y]
        band_alpha[y] = np.maximum(band_alpha[y], halo)
    hole = hole | (band_alpha > 0)

    out = np.clip(np.rint(out), 0, 255).astype(np.uint8)

    # masque progressif (bord adouci de ~1,5 px) pour le calque de retouche
    alpha = cv2.GaussianBlur(hole.astype(np.float32), (0, 0), 1.0)
    alpha = np.where(ndimage.binary_erosion(hole, iterations=2), 1.0,
                     np.where(hole, np.clip(alpha * 1.6, 0, 1), 0.0))
    alpha = np.round(alpha * 255) / 255             # masque 8 bits, identique au PSD
    final = (out * alpha[..., None] + img * (1 - alpha[..., None]))
    final = np.clip(np.rint(final), 0, 255).astype(np.uint8)

    Image.fromarray(final).save(out_dir / "american_gym_retouche.png", optimize=True)
    Image.fromarray(final).save(out_dir / "american_gym_retouche.jpg", quality=97, subsampling=0)
    # éléments pour le PSD : gazon reconstitué (RVB) + son masque de fusion
    Image.fromarray(out).save(out_dir / "_gazon_rvb.png")
    Image.fromarray((alpha * 255).round().astype(np.uint8)).save(out_dir / "_gazon_masque.png")
    print("pixels remplacés :", int(hole.sum()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
