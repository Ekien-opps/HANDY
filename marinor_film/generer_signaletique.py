# -*- coding: utf-8 -*-
"""
Génère la signalétique du magasin Marin'Or (textures/signaletique/*.png).

Python 3 + Pillow :  python3 generer_signaletique.py
Lit catalogue_produits.json. Produit :
  - ETQ_<id>.png        étiquettes de rayon (porte-étiquettes des étagères, gondoles, frigos)
  - VRAC_<id>.png       chevalets des bacs de vrac
  - CARTON_<id>.png     impression des cartons de la réserve
  - PANNEAU_<zone>.png  panneaux suspendus des rayons
  - PLAQUE_<piece>.png  plaques de porte des locaux du personnel
Les PNG sont déjà fournis ; ce script ne sert qu'à les refaire ou les modifier.
Aucun prix n'est inscrit : la colonne PRIX ci-dessous est vide par défaut.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "textures", "signaletique")
LOGO = os.path.join(ICI, "textures", "MAT_Logo_color.png")

# Charte (colorimetrie_marque.txt)
BORDEAUX = "#7B1421"
OR = "#F9A825"
CREME = "#FFECD1"
NOIR = "#161616"
BLANC = "#FFFFFF"
VERT = "#2a5519"

# Prix affichés sur les étiquettes, en FCFA (ex. {"paprika": 1500}). Vide : pas de prix.
PRIX = {}

POLICES = ["/usr/share/fonts/opentype/inter/Inter-{}.otf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-{}.ttf",
           "C:/Windows/Fonts/arial{}.ttf"]


def police(taille, graisse="Bold"):
    variantes = {"Bold": ["Bold", "Bold", "bd"], "SemiBold": ["SemiBold", "Bold", "bd"],
                 "Regular": ["Regular", "", ""], "Black": ["Black", "Bold", "bd"]}[graisse]
    for modele, v in zip(POLICES, variantes):
        chemin = modele.format(v).replace("-.ttf", ".ttf")
        if os.path.isfile(chemin):
            return ImageFont.truetype(chemin, taille)
    return ImageFont.load_default()


def texte_centre(d, boite, texte, fnt, couleur):
    x0, y0, x1, y1 = boite
    l, h = d.textbbox((0, 0), texte, font=fnt)[2:]
    d.text((x0 + (x1 - x0 - l) / 2, y0 + (y1 - y0 - h) / 2 - fnt.size * 0.12), texte, font=fnt, fill=couleur)


def ajuster(d, texte, largeur_max, taille, graisse="Bold"):
    while taille > 10:
        fnt = police(taille, graisse)
        if d.textbbox((0, 0), texte, font=fnt)[2] <= largeur_max:
            return fnt
        taille -= 2
    return police(taille, graisse)


def logo(hauteur):
    if not os.path.isfile(LOGO):
        return None
    im = Image.open(LOGO).convert("RGBA")
    return im.resize((max(1, int(im.width * hauteur / im.height)), hauteur), Image.LANCZOS)


def sauver(im, nom):
    os.makedirs(SORTIE, exist_ok=True)
    im.save(os.path.join(SORTIE, nom), optimize=True)
    print("ecrit", nom, "%dx%d" % im.size)


def etiquette(p):
    """Étiquette de rayon 10 x 3 cm (1000 x 300 px)."""
    im = Image.new("RGBA", (1000, 300), BLANC)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 150, 300], fill=BORDEAUX)
    lg = logo(110)
    if lg:
        lg = lg.resize((130, int(lg.height * 130 / lg.width)), Image.LANCZOS)
        im.alpha_composite(lg, (10, (300 - lg.height) // 2))
    d.rectangle([150, 0, 1000, 14], fill=OR)
    fnt = ajuster(d, p["nom"].upper(), 800, 72, "Black")
    d.text((180, 52), p["nom"].upper(), font=fnt, fill=NOIR)
    sous = "Marin'Or Ivoire" + ("  ·  " + p["poids"] if p["poids"] else "")
    d.text((182, 150), sous, font=police(46, "SemiBold"), fill=BORDEAUX)
    prix = PRIX.get(p["id"])
    if prix:
        t = "{:,} FCFA".format(prix).replace(",", " ")
        fnt = police(64, "Black")
        l = d.textbbox((0, 0), t, font=fnt)[2]
        d.text((980 - l, 205), t, font=fnt, fill=NOIR)
    d.rectangle([0, 286, 1000, 300], fill=BORDEAUX)
    sauver(im, "ETQ_%s.png" % p["id"])


def chevalet_vrac(p):
    """Chevalet de bac de vrac 12 x 8 cm (600 x 400 px)."""
    im = Image.new("RGBA", (600, 400), CREME)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 600, 90], fill=BORDEAUX)
    texte_centre(d, (0, 0, 600, 90), "VRAC", police(64, "Black"), OR)
    lignes = p["nom"].split(" ", 1) if len(p["nom"]) > 14 else [p["nom"]]
    y = 130 if len(lignes) > 1 else 170
    for ligne in lignes:
        fnt = ajuster(d, ligne, 540, 70, "Bold")
        texte_centre(d, (0, y, 600, y + 80), ligne, fnt, NOIR)
        y += 85
    texte_centre(d, (0, 320, 600, 390), "au poids  ·  Marin'Or", police(36, "SemiBold"), BORDEAUX)
    sauver(im, "VRAC_%s.png" % p["id"])


def carton(p):
    """Flanc de carton de réserve (1024 x 640 px), kraft imprimé."""
    im = Image.new("RGBA", (1024, 640), "#b98a57")
    d = ImageDraw.Draw(im)
    import random
    r = random.Random(hash(p["id"]) & 0xffff)
    for _ in range(9000):                                     # fibres du kraft
        x, y = r.randrange(1024), r.randrange(640)
        c = r.choice(["#a87b4b", "#c3976a", "#ad8152", "#c9a073"])
        d.line([(x, y), (x + r.randint(2, 9), y + r.randint(-1, 1))], fill=c)
    d.rectangle([0, 300, 1024, 336], fill="#d9b88a")          # ruban adhésif
    lg = logo(190)
    if lg:
        im.alpha_composite(lg, ((1024 - lg.width) // 2, 60))
    fnt = ajuster(d, p["nom"].upper(), 900, 70, "Black")
    texte_centre(d, (0, 380, 1024, 470), p["nom"].upper(), fnt, BORDEAUX)
    texte_centre(d, (0, 480, 1024, 540), (p["poids"] + "  ·  " if p["poids"] else "") + "MARIN'OR IVOIRE",
                 police(40, "Bold"), NOIR)
    d.text((40, 580), "↑ HAUT   ·   FRAGILE   ·   CONSERVER AU SEC", font=police(28, "SemiBold"), fill=NOIR)
    sauver(im, "CARTON_%s.png" % p["id"])


def panneau(nom, titre, sous_titre):
    """Panneau suspendu 1,60 x 0,40 m (1600 x 400 px)."""
    im = Image.new("RGBA", (1600, 400), BORDEAUX)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 1600, 18], fill=OR)
    d.rectangle([0, 382, 1600, 400], fill=OR)
    lg = logo(230)
    if lg:
        im.alpha_composite(lg, (50, (400 - lg.height) // 2))
        x0 = 90 + lg.width
    else:
        x0 = 80
    fnt = ajuster(d, titre, 1520 - x0, 150, "Black")
    d.text((x0 + 30, 70), titre, font=fnt, fill=CREME)
    d.text((x0 + 34, 262), sous_titre, font=police(56, "SemiBold"), fill=OR)
    sauver(im, "PANNEAU_%s.png" % nom)


def plaque(nom, texte):
    """Plaque de porte 30 x 10 cm (900 x 300 px)."""
    im = Image.new("RGBA", (900, 300), CREME)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 900, 300], outline=BORDEAUX, width=16)
    d.rectangle([0, 0, 200, 300], fill=BORDEAUX)
    lg = logo(120)
    if lg:
        lg = lg.resize((170, int(lg.height * 170 / lg.width)), Image.LANCZOS)
        im.alpha_composite(lg, (15, (300 - lg.height) // 2))
    fnt = ajuster(d, texte, 650, 96, "Bold")
    texte_centre(d, (200, 0, 900, 300), texte, fnt, BORDEAUX)
    sauver(im, "PLAQUE_%s.png" % nom)


def main():
    with open(os.path.join(ICI, "catalogue_produits.json"), encoding="utf-8") as f:
        produits = json.load(f)["produits"]
    for p in produits:
        etiquette(p)
        chevalet_vrac(p)
        carton(p)
    panneau("epices", "ÉPICES", "assaisonnements & poudres")
    panneau("marinades", "MARINADES", "prêtes à mariner")
    panneau("essentiels", "ESSENTIELS", "pâte d'arachide & huile rouge")
    panneau("frais", "PRODUITS FRAIS", "marinades fraîches & purées")
    panneau("vrac", "VRAC", "épices au poids")
    panneau("degustation", "DÉGUSTATION", "goûtez avant d'acheter")
    panneau("caisses", "CAISSES", "bienvenue chez Marin'Or")
    panneau("gamme", "TOUTE LA GAMME", "Marin'Or Ivoire")
    plaque("staff", "PERSONNEL")
    plaque("reserve", "RÉSERVE")
    plaque("bureau", "BUREAU")
    plaque("vestiaire", "VESTIAIRE")
    plaque("pause", "SALLE DE PAUSE")
    plaque("wc", "SANITAIRES")
    plaque("local_technique", "LOCAL TECHNIQUE")


if __name__ == "__main__":
    main()
