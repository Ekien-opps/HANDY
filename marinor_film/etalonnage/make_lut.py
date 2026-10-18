# Génère Marinor_Ivoire_Look.cube (LUT 3D 33^3, Rec.709 / sRGB affiché -> affiché).
import sys
import numpy as np

CONTRASTE = 0.30        # courbe en S (0 = aucune)
RELEVE = 0.030          # remontée des ombres moyennes
NOIRS = 0.018           # noirs un peu plus denses
OMBRES = np.array([-0.012, 0.002, 0.022])   # ombres légèrement bleutées (profondeur)
LUMIERES = np.array([0.010, 0.004, -0.012])  # hautes lumières légèrement chaudes
VIBRANCE = 0.18         # renforce les couleurs ternes, épargne les couleurs déjà vives
TAILLE = 33


def grade(rgb):
    x = np.clip(rgb, 0.0, 1.0)
    # 1. contraste : courbe en S douce, pivot à mi-gris
    s = x * x * (3.0 - 2.0 * x)
    x = x + CONTRASTE * (s - x)
    # les ombres moyennes ne s'écrasent pas : légère remontée autour de 1/3 (plans sombres lisibles)
    x = x + RELEVE * x * (1.0 - x) ** 2 / 0.148
    # 2. noirs plus denses avec une entrée douce (pas d'écrasement)
    x = x - NOIRS * (1.0 - x) ** 6
    # 3. virage des ombres et des hautes lumières selon la luminance
    L = (x @ np.array([0.2126, 0.7152, 0.0722]))[..., None]
    pied = np.clip(L / 0.08, 0.0, 1.0)                 # le noir pur reste neutre
    x = x + pied * (1.0 - L) ** 2 * OMBRES + L ** 2 * LUMIERES
    # 4. vibrance
    L = (x @ np.array([0.2126, 0.7152, 0.0722]))[..., None]
    sat = x.max(axis=-1, keepdims=True) - x.min(axis=-1, keepdims=True)
    x = L + (x - L) * (1.0 + VIBRANCE * (1.0 - np.clip(sat * 1.6, 0, 1)))
    return np.clip(x, 0.0, 1.0)


def ecrire_cube(chemin):
    g = np.linspace(0.0, 1.0, TAILLE)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")          # rouge varie le plus vite
    rgb = np.stack([r, gg, b], axis=-1).reshape(-1, 3)
    out = grade(rgb)
    with open(chemin, "w", newline="\n") as f:
        f.write('TITLE "Marin\'Or Ivoire - Look film"\n')
        f.write("# Rec.709 / sRGB -> Rec.709 / sRGB. Contraste doux, ombres froides, lumières chaudes, vibrance.\n")
        f.write("LUT_3D_SIZE %d\nDOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n" % TAILLE)
        for v in out:
            f.write("%.6f %.6f %.6f\n" % tuple(v))


if __name__ == "__main__":
    ecrire_cube(sys.argv[1])
