# -*- coding: utf-8 -*-
"""
Lower thirds Marin'Or Ivoire — style « Clean Edition » (Montserrat, volets obliques en cascade).

Charte : ivoire (bloc titre) + or Marin'Or (ligne d'accent, volet, bandeau du sous-titre),
texte noir Marin'Or. Ces deux teintes cassent le rouge/terracotta du film sans le heurter.

Sortie : ProRes 4444 avec canal alpha (.mov), 1920 x 1080, 24 i/s — calé sur le film.
Usage :  python lower_thirds.py <dossier_sortie> [aperçu_fond.png ...]
"""

import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 24
SS = 2                                   # sur-échantillonnage (bords lisses)

IVOIRE = (255, 246, 232)
OR = (249, 168, 37)
NOIR = (22, 22, 22)

# Mise en page (pixels du film)
X0 = 150                                  # bord gauche du bloc titre
TY = 792                                  # haut du bloc titre
TH = 76                                   # hauteur du bloc titre
SH = 36                                   # hauteur du bandeau sous-titre
PAD_G, PAD_D = 26, 30                     # marges intérieures du titre
SUB_PAD = 16
LIGNE_L = 7                               # épaisseur de la ligne d'accent
LIGNE_X = X0 - 16
INCL = math.tan(math.radians(12))         # inclinaison des volets
TAILLE_TITRE, TAILLE_SOUS = 44, 19
APPROCHE_SOUS = 2.2                       # espacement des lettres du sous-titre

POLICE_TITRE = ImageFont.truetype(os.path.join(ICI, "fonts", "Montserrat-Bold.ttf"), TAILLE_TITRE * SS)
POLICE_SOUS = ImageFont.truetype(os.path.join(ICI, "fonts", "Montserrat-SemiBold.ttf"), TAILLE_SOUS * SS)

# (id, titre, sous-titre, début dans le film en s, durée en s, ensemble)
SERIE = [
    ("01", "Cocody Riviera", "Abidjan · Côte d’Ivoire", 1.0, 4.0, "01_Ouverture"),
    ("02", "Marin’Or Ivoire", "La boutique", 9.0, 4.0, "01_Ouverture"),
    ("03", "Bienvenue", "Entrée", 13.6, 3.0, "02_Accueil"),
    ("04", "Caisses", "Accueil & paiement", 17.6, 3.2, "02_Accueil"),
    ("05", "Nos marinades", "Poulet · Poisson · Mixte", 27.0, 3.6, "03_Boutique"),
    ("06", "Vue d’ensemble", "Épices · Marinades · Vrac", 42.2, 3.4, "03_Boutique"),
    ("07", "Espace personnel", "Accès réservé", 49.0, 3.0, "04_Espace_personnel"),
    ("08", "Salle de pause", "", 55.3, 2.7, "04_Espace_personnel"),
    ("09", "Vestiaire", "", 58.9, 2.7, "04_Espace_personnel"),
    ("10", "Bureau", "", 62.6, 2.7, "04_Espace_personnel"),
    ("11", "Réserve", "Stock", 66.6, 3.0, "04_Espace_personnel"),
    ("12", "Marin’Or Ivoire", "À très bientôt", 80.6, 4.3, "05_Final"),
]
DUREE_FILM = 2040 / FPS


# --- courbes d'animation -------------------------------------------------------------------------
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def prog(t, t0, t1):
    return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)


def ease_out(p):
    return 1 - (1 - p) ** 3


def ease_in_out(p):
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def ease_in(p):
    return p ** 3


# --- dessin ---------------------------------------------------------------------------------------
def largeur_texte(txt, fnt, approche=0.0):
    if not txt:
        return 0
    return fnt.getlength(txt) + approche * SS * (len(txt) - 1)


def texte(d, xy, txt, fnt, fill, approche=0.0):
    x, y = xy
    if approche == 0:
        d.text((x, y), txt, font=fnt, fill=fill)
        return
    for c in txt:
        d.text((x, y), c, font=fnt, fill=fill)
        x += fnt.getlength(c) + approche * SS


def para(x_g, x_d, y_h, y_b):
    """Parallélogramme incliné (bords gauche et droit penchés vers la droite en montant)."""
    if x_d <= x_g:
        return None
    s = (y_b - y_h) * INCL
    return [(x_g + s, y_h), (x_d + s, y_h), (x_d, y_b), (x_g, y_b)]


class LowerThird:
    def __init__(self, titre, sous, duree):
        self.titre, self.sous, self.duree = titre, sous.upper(), duree
        self.lt = (largeur_texte(titre, POLICE_TITRE) / SS) + PAD_G + PAD_D
        self.ls = (largeur_texte(self.sous, POLICE_SOUS, APPROCHE_SOUS) / SS) + 2 * SUB_PAD if sous else 0
        bas = TY + TH + (SH if sous else 0)
        # zone de dessin (avec marge pour l'ombre)
        self.zx0, self.zy0 = LIGNE_X - 40, TY - 40
        self.zx1 = int(X0 + max(self.lt, self.ls) + 80)
        self.zy1 = bas + 50

    # coordonnées zone sur-échantillonnée
    def z(self, x, y):
        return ((x - self.zx0) * SS, (y - self.zy0) * SS)

    def etat(self, t):
        """Avancement de chaque élément (0 = caché, 1 = en place) à l'instant t."""
        D = self.duree
        so = D - 0.78                                    # début de la sortie
        e = {}
        if t < so:
            e["ligne"] = ease_out(prog(t, 0.00, 0.30))
            e["or"] = ease_in_out(prog(t, 0.16, 0.58))
            e["ivoire"] = ease_in_out(prog(t, 0.28, 0.72))
            e["titre"] = ease_out(prog(t, 0.42, 0.88))
            e["bandeau"] = ease_in_out(prog(t, 0.60, 0.95))
            e["sous"] = ease_out(prog(t, 0.72, 1.08))
            e["ligne_haut"] = 1.0
        else:
            u = t - so
            e["sous"] = 1 - ease_in(prog(u, 0.00, 0.26))
            e["bandeau"] = 1 - ease_in_out(prog(u, 0.06, 0.34))
            e["titre"] = 1 - ease_in(prog(u, 0.04, 0.30))
            e["ivoire"] = 1 - ease_in_out(prog(u, 0.10, 0.44))
            e["or"] = 1 - ease_in_out(prog(u, 0.20, 0.54))
            e["ligne"] = 1.0
            e["ligne_haut"] = 1 - ease_in_out(prog(u, 0.46, 0.74))
        return e

    def image(self, t):
        """Image RGBA (taille film) à l'instant t."""
        e = self.etat(t)
        zw, zh = (self.zx1 - self.zx0) * SS, (self.zy1 - self.zy0) * SS
        calque = Image.new("RGBA", (zw, zh), (0, 0, 0, 0))
        forme = Image.new("L", (zw, zh), 0)                 # silhouette pour l'ombre
        d, df = ImageDraw.Draw(calque), ImageDraw.Draw(forme)

        def poly(x_g, x_d, y_h, y_b, couleur):
            p = para(x_g, x_d, y_h, y_b)
            if p:
                pts = [self.z(*q) for q in p]
                d.polygon(pts, fill=couleur)
                df.polygon(pts, fill=255)
            return p

        # ligne d'accent : pousse du bas vers le haut, se retire vers le bas à la sortie
        if e["ligne"] > 0 and e["ligne_haut"] > 0:
            bas = TY + TH
            h = TH * e["ligne"] * e["ligne_haut"]
            poly(LIGNE_X, LIGNE_X + LIGNE_L, bas - h, bas, OR + (255,))

        # volet or puis bloc ivoire (de gauche à droite)
        if e["or"] > 0:
            poly(X0, X0 + self.lt * e["or"], TY, TY + TH, OR + (255,))
        if e["ivoire"] > 0:
            poly(X0, X0 + self.lt * e["ivoire"], TY, TY + TH, IVOIRE + (255,))

        # titre : glisse de la droite, découpé par le bloc ivoire
        if e["titre"] > 0 and e["ivoire"] > 0:
            txt = Image.new("RGBA", (zw, zh), (0, 0, 0, 0))
            dt = ImageDraw.Draw(txt)
            dx = (1 - e["titre"]) * 28
            asc, desc = POLICE_TITRE.getmetrics()
            y = TY + (TH - (asc + desc) / SS) / 2 + 1
            x = X0 + PAD_G + dx + TH * INCL * 0.5
            dt.text(self.z(x, y), self.titre, font=POLICE_TITRE, fill=NOIR + (int(255 * e["titre"]),))
            masque = Image.new("L", (zw, zh), 0)
            p = para(X0, X0 + self.lt * e["ivoire"], TY, TY + TH)
            ImageDraw.Draw(masque).polygon([self.z(*q) for q in p], fill=255)
            txt.putalpha(Image.composite(txt.getchannel("A"), Image.new("L", (zw, zh), 0), masque))
            calque.alpha_composite(txt)

        # bandeau or du sous-titre : sous le bloc, légèrement décalé vers la droite
        if self.sous and e["bandeau"] > 0:
            y0 = TY + TH
            xg = X0 + 12
            poly(xg, xg + self.ls * e["bandeau"], y0, y0 + SH, OR + (255,))
            if e["sous"] > 0:
                txt = Image.new("RGBA", (zw, zh), (0, 0, 0, 0))
                dt = ImageDraw.Draw(txt)
                asc, desc = POLICE_SOUS.getmetrics()
                dy = (1 - e["sous"]) * SH
                y = y0 + (SH - (asc + desc) / SS) / 2 + 1 + dy
                x = xg + SUB_PAD + SH * INCL * 0.5
                texte(dt, self.z(x, y), self.sous, POLICE_SOUS, NOIR + (255,), APPROCHE_SOUS)
                masque = Image.new("L", (zw, zh), 0)
                p = para(xg, xg + self.ls * e["bandeau"], y0, y0 + SH)
                ImageDraw.Draw(masque).polygon([self.z(*q) for q in p], fill=255)
                txt.putalpha(Image.composite(txt.getchannel("A"), Image.new("L", (zw, zh), 0), masque))
                calque.alpha_composite(txt)

        # ombre portée douce (lisibilité sur le décor 3D)
        ombre = forme.filter(ImageFilter.GaussianBlur(14 * SS)).point(lambda v: int(v * 0.30))
        fond = Image.new("RGBA", (zw, zh), (0, 0, 0, 0))
        fond.putalpha(ombre)
        fond = fond.transform((zw, zh), Image.AFFINE, (1, 0, -4 * SS, 0, 1, -6 * SS))
        fond.alpha_composite(calque)

        petit = fond.resize((zw // SS, zh // SS), Image.LANCZOS)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        img.paste(petit, (self.zx0, self.zy0))
        return img


# --- encodage -------------------------------------------------------------------------------------
def encodeur(chemin, n_images):
    return subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (W, H),
         "-r", str(FPS), "-i", "-", "-frames:v", str(n_images), "-c:v", "prores_ks", "-profile:v", "4",
         "-pix_fmt", "yuva444p10le", "-alpha_bits", "16", "-vendor", "apl0", "-qscale:v", "6",
         "-metadata", "title=Marin'Or Ivoire - lower third", chemin],
        stdin=subprocess.PIPE)


def rendre_clip(lt, chemin):
    n = int(round(lt.duree * FPS))
    p = encodeur(chemin, n)
    for i in range(n):
        p.stdin.write(lt.image(i / FPS).tobytes())
    p.stdin.close()
    p.wait()


def rendre_piste(series, chemin):
    """Piste complète de la durée du film : à poser au-dessus du film à 0:00."""
    n = int(round(DUREE_FILM * FPS))
    vide = Image.new("RGBA", (W, H), (0, 0, 0, 0)).tobytes()
    p = encodeur(chemin, n)
    for f in range(n):
        t = f / FPS
        img = None
        for (lt, debut) in series:
            if debut <= t < debut + lt.duree:
                img = lt.image(t - debut)
                break
        p.stdin.write(img.tobytes() if img else vide)
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    sortie = sys.argv[1]
    os.makedirs(sortie, exist_ok=True)
    for (i, titre, sous, debut, duree, groupe) in SERIE:
        nom = "LT%s_%s.mov" % (i, titre.replace("’", "").replace(" ", "_").replace("é", "e").replace("É", "E"))
        dossier = os.path.join(sortie, groupe)
        os.makedirs(dossier, exist_ok=True)
        rendre_clip(LowerThird(titre, sous, duree), os.path.join(dossier, nom))
        print("ok", groupe, nom, flush=True)
