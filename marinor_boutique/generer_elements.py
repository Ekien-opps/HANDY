# -*- coding: utf-8 -*-
"""
Génère elements.csv : plan du magasin Marin'Or Ivoire (version 3, 24 x 16 m : plan de la version 2, éclairage renforcé).

Python 3 seul, sans Blender :  python3 generer_elements.py
Le plan (cotes, meubles, lampes) se modifie ici, puis on relance ce script
et le script Blender. Le CSV produit reste la référence lue par Blender.

Repères : origine au coin extérieur avant gauche, X = largeur (0 à 24),
Y = profondeur depuis la rue (0 à 16), Z = hauteur. x, y, z = centre de l'objet.
Meubles : dim_x = largeur, dim_y = profondeur, dim_z = hauteur, face avant
vers -Y avant rotation ; rot_z oriente le meuble (90 = face vers +X,
-90 = face vers -X, 180 = face vers +Y).
"""

import csv
import os

# =============================================================================
# COTES GÉNÉRALES
# =============================================================================

W, D = 24.0, 16.0           # emprise extérieure
H = 3.50                    # hauteur sous plafond (murs)
EP = 0.20                   # murs extérieurs
CL = 0.10                   # cloisons
Z_PLAFOND = H - 0.03        # sous-face du plafond (spots)

Y_SEP = 12.05               # cloison vente / locaux du personnel (faces 12,00 et 12,10)
Y_COUL = 13.55              # cloison couloir / pièces (faces 13,50 et 13,60)
X_RES = 9.05                # cloison réserve / couloir et bureau
X_PIECES = [13.05, 14.85, 18.05, 21.85]   # bureau | WC | vestiaire | pause | local technique

H_PORTE = 2.20
VITRINE_BAS, VITRINE_HAUT = 0.40, 3.00
H_PORTE_ENTREE, H_IMPOSTE = 2.40, 3.00

CHAMPS = ["id", "nom", "type", "collection", "x", "y", "z", "dim_x", "dim_y", "dim_z",
          "rot_x_deg", "rot_z_deg", "materiau", "notes"]
LIGNES = []


def n(v):
    s = ("%.4f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def ajouter(nom, typ, coll, x, y, z, dx=0.0, dy=0.0, dz=0.0, rx=0.0, rz=0.0, mat="", notes=""):
    ident = "%03d" % (len(LIGNES) + 1)
    LIGNES.append(dict(id=ident, nom=nom, type=typ, collection=coll,
                       x=n(x), y=n(y), z=n(z), dim_x=n(dx), dim_y=n(dy), dim_z=n(dz),
                       rot_x_deg=n(rx), rot_z_deg=n(rz), materiau=mat, notes=notes))
    return ident


def boite(nom, coll, x0, x1, y0, y1, z0, z1, mat, notes="", typ="box"):
    """Pavé donné par ses bornes."""
    return ajouter(nom, typ, coll, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2,
                   x1 - x0, y1 - y0, z1 - z0, mat=mat, notes=notes)


def mur(nom, coll, axe, c, a, b, ep, mat, ouvertures=(), hauteur=H, notes=""):
    """Mur le long de X (axe 'x', à y = c) ou de Y (axe 'y', à x = c), de a à b.
    ouvertures : (debut, fin, hauteur_porte, nom_court)."""
    pleins, linteaux, cur = [], [], a
    for oa, ob, oh, court in sorted(ouvertures):
        if oa > cur + 1e-6:
            pleins.append((cur, oa))
        linteaux.append((oa, ob, oh, court))
        cur = ob
    if b > cur + 1e-6:
        pleins.append((cur, b))

    def pave(nom_obj, s, e, z0, z1, note):
        if axe == "x":
            boite(nom_obj, coll, s, e, c - ep / 2, c + ep / 2, z0, z1, mat, note)
        else:
            boite(nom_obj, coll, c - ep / 2, c + ep / 2, s, e, z0, z1, mat, note)

    for i, (s, e) in enumerate(pleins, 1):
        pave(nom if len(pleins) == 1 and not linteaux else "%s_%d" % (nom, i), s, e, 0.0, hauteur, notes)
    for oa, ob, oh, court in linteaux:
        pave("%s_linteau_%s" % (nom, court), oa, ob, oh, hauteur, "au-dessus de la porte " + court)


def porte(nom, axe, c, a, b, h, mat, ep_mur=CL, double=False, chambranle=0, typ="door", cadres=False):
    """Porte(s) à pivot dans un mur. Le pivot est au gond (a, ou a et b si double).
    chambranle : -1 / +1 = côté du mur (vers -Y/-X ou +Y/+X), 0 = aucun."""
    largeur = b - a
    vantaux = [(a, a + largeur / 2, "_G"), (a + largeur / 2, b, "_D")] if double else [(a, b, "")]
    for i, (va, vb, suf) in enumerate(vantaux):
        gond = vb if (double and i == 1) else va
        px, py = (gond, c) if axe == "x" else (c, gond)
        id_pivot = ajouter("Pivot_" + nom + suf, "empty", "Ouvertures", px, py, 0.0,
                           notes="pivot " + nom + suf)
        enfant = "enfant de " + id_pivot
        m = (va + vb) / 2
        if axe == "x":
            ajouter(nom + suf, typ, "Ouvertures", m, c, h / 2, vb - va, 0.04, h, mat=mat, notes=enfant)
        else:
            ajouter(nom + suf, typ, "Ouvertures", c, m, h / 2, 0.04, vb - va, h, mat=mat, notes=enfant)
        if cadres:
            # Montants et traverse du vantail vitré : ils pivotent avec lui.
            w = vb - va
            ajouter("Cadre_" + nom + suf + "_montant_1", "box", "Ouvertures", va + 0.025, c, h / 2,
                    0.05, 0.06, h, mat="MAT_Alu_Cadre", notes=enfant)
            ajouter("Cadre_" + nom + suf + "_montant_2", "box", "Ouvertures", vb - 0.025, c, h / 2,
                    0.05, 0.06, h, mat="MAT_Alu_Cadre", notes=enfant)
            ajouter("Cadre_" + nom + suf + "_traverse", "box", "Ouvertures", m, c, h - 0.03,
                    w, 0.06, 0.06, mat="MAT_Alu_Cadre", notes=enfant)
            ajouter("Cadre_" + nom + suf + "_soubassement", "box", "Ouvertures", m, c, 0.06,
                    w, 0.06, 0.12, mat="MAT_Alu_Cadre", notes=enfant)
    if axe == "x":
        boite("Seuil_" + nom, "Ouvertures", a, b, c - ep_mur / 2, c + ep_mur / 2, 0.0, 0.02, "MAT_Alu_Cadre")
    else:
        boite("Seuil_" + nom, "Ouvertures", c - ep_mur / 2, c + ep_mur / 2, a, b, 0.0, 0.02, "MAT_Alu_Cadre")
    if chambranle:
        f = c + chambranle * (ep_mur / 2 + 0.01)
        e = 0.07
        if axe == "x":
            boite("Chambranle_" + nom + "_gauche", "Ouvertures", a - e, a, f - 0.01, f + 0.01, 0, h + e, "MAT_Bois_Clair")
            boite("Chambranle_" + nom + "_droit", "Ouvertures", b, b + e, f - 0.01, f + 0.01, 0, h + e, "MAT_Bois_Clair")
            boite("Chambranle_" + nom + "_haut", "Ouvertures", a - e, b + e, f - 0.01, f + 0.01, h, h + e, "MAT_Bois_Clair")
        else:
            boite("Chambranle_" + nom + "_gauche", "Ouvertures", f - 0.01, f + 0.01, a - e, a, 0, h + e, "MAT_Bois_Clair")
            boite("Chambranle_" + nom + "_droit", "Ouvertures", f - 0.01, f + 0.01, b, b + e, 0, h + e, "MAT_Bois_Clair")
            boite("Chambranle_" + nom + "_haut", "Ouvertures", f - 0.01, f + 0.01, a - e, b + e, h, h + e, "MAT_Bois_Clair")


def cadre_vitrage(nom, x0, x1, z0, z1, y=-0.01):
    """Parcloses aluminium côté rue autour d'un vitrage de façade."""
    boite("Cadre_" + nom + "_gauche", "Ouvertures", x0, x0 + 0.04, y - 0.01, y + 0.01, z0, z1, "MAT_Alu_Cadre")
    boite("Cadre_" + nom + "_droit", "Ouvertures", x1 - 0.04, x1, y - 0.01, y + 0.01, z0, z1, "MAT_Alu_Cadre")
    boite("Cadre_" + nom + "_bas", "Ouvertures", x0, x1, y - 0.01, y + 0.01, z0, z0 + 0.04, "MAT_Alu_Cadre")
    boite("Cadre_" + nom + "_haut", "Ouvertures", x0, x1, y - 0.01, y + 0.01, z1 - 0.04, z1, "MAT_Alu_Cadre")


def spot(nom, x, y):
    ajouter(nom, "spot", "Eclairage", x, y, Z_PLAFOND, 0.10, 0.10, 0.01,
            mat="MAT_Lumiere_Emissive", notes="spot 2700K vers le bas")


def suspension(nom, x, y, z_bas, notes):
    h_abat = 0.25
    ajouter(nom, "suspension", "Eclairage", x, y, z_bas + h_abat / 2, 0.36, 0.36, h_abat,
            mat="MAT_Laiton_Brosse", notes="abat-jour 2700K " + notes)
    l = Z_PLAFOND - (z_bas + h_abat)
    ajouter(nom + "_cable", "cylinder", "Eclairage", x, y, z_bas + h_abat + l / 2, 0.01, 0.01, l,
            mat="MAT_Alu_Cadre", notes="cable jusqu au plafond")


def panneau(nom, x, y, cote=0.60):
    """Dalle LED encastrée au plafond : diffuseur émissif + lampe Area vers le bas."""
    ajouter(nom, "panneau_led", "Eclairage", x, y, Z_PLAFOND - 0.005, cote, cote, 0.01,
            mat="MAT_Panneau_LED", notes="dalle LED %.2f m 3300K vers le bas" % cote)


def ruban(nom, x0, y0, x1, y1, vers):
    """Lécheur de mur : profilé LED au plafond, parallèle au mur, incliné vers les
    étagères. vers = direction du mur : '-x', '+x' ou '+y'."""
    longueur = abs(x1 - x0) + abs(y1 - y0)
    rz = {"+y": 180.0, "+x": 90.0, "-x": -90.0}[vers]     # repère des meubles : avant vers -Y
    ajouter(nom, "ruban_led", "Eclairage", (x0 + x1) / 2, (y0 + y1) / 2, Z_PLAFOND - 0.01,
            longueur, 0.06, 0.02, rx=-35.0, rz=rz, mat="MAT_Panneau_LED",
            notes="lecheur de mur 3300K, incline vers les etageres (%s)" % vers)


def meuble(nom, typ, coll, x, y, dx, dy, dz, mat, rz=0.0, z_bas=0.0, notes=""):
    ajouter(nom, typ, coll, x, y, z_bas + dz / 2, dx, dy, dz, rz=rz, mat=mat, notes=notes)


def zone(nom, x0, x1, y0, y1, notes):
    ajouter(nom, "empty", "Zones", (x0 + x1) / 2, (y0 + y1) / 2, 0.0, x1 - x0, y1 - y0, 0.0, notes=notes)


# =============================================================================
# SOLS
# =============================================================================

boite("Sol_Vente", "Sol", 0, W, 0, Y_SEP, -0.02, 0, "MAT_Sol_Terracotta", "salle de vente")
boite("Sol_Reserve", "Sol", 0, X_RES, Y_SEP, D, -0.02, 0, "MAT_Sol_BetonCire", "reserve")
boite("Sol_Couloir", "Sol", X_RES, W, Y_SEP, Y_COUL, -0.02, 0, "MAT_Sol_BetonCire", "couloir du personnel")
for nom_sol, xa, xb, mat in [("Sol_Bureau", X_RES, X_PIECES[0], "MAT_Bois_Clair"),
                             ("Sol_WC", X_PIECES[0], X_PIECES[1], "MAT_Sol_Carrelage_Blanc"),
                             ("Sol_Vestiaire", X_PIECES[1], X_PIECES[2], "MAT_Sol_Carrelage_Blanc"),
                             ("Sol_Pause", X_PIECES[2], X_PIECES[3], "MAT_Sol_Carrelage_Blanc"),
                             ("Sol_Local_technique", X_PIECES[3], W, "MAT_Sol_BetonCire")]:
    boite(nom_sol, "Sol", xa, xb, Y_COUL, D, -0.02, 0, mat, nom_sol[4:].lower())

# =============================================================================
# FAÇADE (y = 0 à 0,20) : piliers, vitrines, entrée double au centre
# =============================================================================

PIEC = "Murs_exterieurs"
VITRINES_G = [(0.8, 4.0), (4.0, 7.2), (7.2, 10.4)]
VITRINES_D = [(13.6, 16.8), (16.8, 20.0), (20.0, 23.2)]
ENTREE = (11.1, 12.9)

for i, (xa, xb) in enumerate([(0.0, 0.8), (10.4, ENTREE[0]), (ENTREE[1], 13.6), (23.2, W)], 1):
    boite("Mur_facade_pilier_%d" % i, PIEC, xa, xb, 0, EP, 0, H, "MAT_Mur_Bordeaux", "pilier de facade")
for i, (xa, xb) in enumerate(VITRINES_G + VITRINES_D, 1):
    boite("Mur_facade_allege_%d" % i, PIEC, xa, xb, 0, EP, 0, VITRINE_BAS, "MAT_Mur_Bordeaux", "allege vitrine %d" % i)
    boite("Mur_facade_linteau_%d" % i, PIEC, xa, xb, 0, EP, VITRINE_HAUT, H, "MAT_Mur_Bordeaux", "linteau vitrine %d" % i)
    boite("Vitrine_%d" % i, "Ouvertures", xa, xb, 0.08, 0.12, VITRINE_BAS, VITRINE_HAUT, "MAT_Verre_Clair",
          "vitrine %.2f x %.2f" % (xb - xa, VITRINE_HAUT - VITRINE_BAS), typ="glass")
    cadre_vitrage("vitrine_%d" % i, xa, xb, VITRINE_BAS, VITRINE_HAUT)
boite("Mur_facade_linteau_entree", PIEC, ENTREE[0], ENTREE[1], 0, EP, H_IMPOSTE, H, "MAT_Mur_Bordeaux", "linteau entree")
boite("Imposte_vitree_entree", "Ouvertures", ENTREE[0], ENTREE[1], 0.08, 0.12, H_PORTE_ENTREE, H_IMPOSTE,
      "MAT_Verre_Clair", "imposte au-dessus de la porte", typ="glass")
cadre_vitrage("imposte", ENTREE[0], ENTREE[1], H_PORTE_ENTREE, H_IMPOSTE)
porte("Porte_entree", "x", 0.10, ENTREE[0], ENTREE[1], H_PORTE_ENTREE, "MAT_Verre_Clair",
      ep_mur=EP, double=True, typ="glass", cadres=True)

boite("Auvent_dalle", PIEC, 0, W, -1.20, 0, VITRINE_HAUT, VITRINE_HAUT + 0.10, "MAT_Alu_Cadre",
      "auvent en porte-a-faux de 1.20 m")

# Murs latéraux et mur du fond (porte de livraison dans la réserve)
boite("Mur_gauche", PIEC, 0, EP, EP, D - EP, 0, H, "MAT_Mur_Creme", "mur lateral gauche")
boite("Mur_droit", PIEC, W - EP, W, EP, D - EP, 0, H, "MAT_Mur_Creme", "mur lateral droit")
LIVRAISON = (3.0, 4.2)
mur("Mur_arriere", PIEC, "x", D - EP / 2, 0, W, EP, "MAT_Mur_Bordeaux",
    [(LIVRAISON[0], LIVRAISON[1], H_PORTE, "livraison")])
porte("Porte_livraison", "x", D - EP / 2, LIVRAISON[0], LIVRAISON[1], H_PORTE, "MAT_Alu_Cadre", ep_mur=EP)

# =============================================================================
# TOIT, PLAFOND, ENSEIGNE
# =============================================================================

boite("Plafond_interieur", "Toit_plafond", EP, W - EP, EP, D - EP, Z_PLAFOND, H, "MAT_Plafond_Blanc",
      "supprimable avec le toit")
boite("Toit_dalle", "Toit", 0, W, 0, D, H, H + 0.20, "MAT_Toit_Etancheite", "dalle de toit supprimable")
Z_ACRO = (H + 0.20, H + 0.60)
boite("Acrotere_avant", "Toit", 0, W, 0, EP, *Z_ACRO, "MAT_Toit_Etancheite", notes="muret facade")
boite("Acrotere_arriere", "Toit", 0, W, D - EP, D, *Z_ACRO, "MAT_Toit_Etancheite", notes="muret fond")
boite("Acrotere_gauche", "Toit", 0, EP, EP, D - EP, *Z_ACRO, "MAT_Toit_Etancheite", notes="muret gauche")
boite("Acrotere_droit", "Toit", W - EP, W, EP, D - EP, *Z_ACRO, "MAT_Toit_Etancheite", notes="muret droit")

Z_ENS = (3.20, 4.00)
boite("Enseigne_caisson", "Enseigne", W / 2 - 5.0, W / 2 + 5.0, -0.20, 0, *Z_ENS, "MAT_Laiton_Brosse",
      notes="caisson exterieur en saillie, 10 m")
ajouter("Enseigne_logo", "plane", "Enseigne", W / 2, -0.21, sum(Z_ENS) / 2, 1.24, 0.70, 0, rx=90,
        mat="MAT_Logo", notes="logo, hauteur 0.70 m, largeur selon le ratio de l image")
ajouter("Enseigne_lumiere", "area_light", "Enseigne", W / 2, -0.80, sum(Z_ENS) / 2, 9.0, 0.5, 0,
        notes="lumiere d appoint tournee vers l enseigne 2700K")

# =============================================================================
# CLOISONS ET PORTES INTÉRIEURES
# Les sanitaires et le vestiaire ouvrent sur un couloir fermé : aucune de
# leurs portes ne donne sur la salle de vente.
# =============================================================================

PORTE_RESERVE = (7.0, 8.6)        # double, salle de vente -> réserve
PORTE_STAFF = (22.3, 23.2)        # salle de vente -> couloir du personnel
PORTE_RES_COUL = (12.4, 13.3)     # réserve -> couloir (cloison x = 9,05)
PORTES_PIECES = {"Porte_bureau": (9.5, 10.4), "Porte_WC": (13.3, 14.1), "Porte_vestiaire": (15.2, 16.0),
                 "Porte_pause": (18.4, 19.3), "Porte_local_technique": (22.0, 22.8)}

mur("Cloison_vente", "Cloisons", "x", Y_SEP, EP, W - EP, CL, "MAT_Mur_Creme",
    [(PORTE_RESERVE[0], PORTE_RESERVE[1], H_PORTE, "reserve"), (PORTE_STAFF[0], PORTE_STAFF[1], H_PORTE, "staff")],
    notes="separation vente / locaux du personnel")
mur("Cloison_reserve", "Cloisons", "y", X_RES, Y_SEP + CL / 2, D - EP, CL, "MAT_Mur_Creme",
    [(PORTE_RES_COUL[0], PORTE_RES_COUL[1], H_PORTE, "couloir")], notes="reserve / couloir et bureau")
mur("Cloison_couloir", "Cloisons", "x", Y_COUL, X_RES + CL / 2, W - EP, CL, "MAT_Mur_Creme",
    [(a, b, H_PORTE, nom.replace("Porte_", "")) for nom, (a, b) in PORTES_PIECES.items()],
    notes="couloir / pieces du personnel")
for nom_c, x in zip(["Cloison_bureau_WC", "Cloison_WC_vestiaire", "Cloison_vestiaire_pause", "Cloison_pause_local"],
                    X_PIECES):
    boite(nom_c, "Cloisons", x - CL / 2, x + CL / 2, Y_COUL + CL / 2, D - EP, 0, H, "MAT_Mur_Creme")

porte("Porte_reserve", "x", Y_SEP, PORTE_RESERVE[0], PORTE_RESERVE[1], H_PORTE, "MAT_Bois_Clair",
      double=True, chambranle=-1)
porte("Porte_staff", "x", Y_SEP, PORTE_STAFF[0], PORTE_STAFF[1], H_PORTE, "MAT_Bois_Clair", chambranle=-1)
porte("Porte_reserve_couloir", "y", X_RES, PORTE_RES_COUL[0], PORTE_RES_COUL[1], H_PORTE, "MAT_Bois_Clair")
for nom_p, (a, b) in PORTES_PIECES.items():
    porte(nom_p, "x", Y_COUL, a, b, H_PORTE, "MAT_Bois_Clair")

# Lambris (salle de vente) et plinthes (cloison du fond, côté vente)
boite("Lambris_gauche", "Murs_interieurs", EP, EP + 0.02, EP, Y_SEP - CL / 2, 0, 1.20, "MAT_Lambris_Bois")
boite("Lambris_droit", "Murs_interieurs", W - EP - 0.02, W - EP, EP, Y_SEP - CL / 2, 0, 1.20, "MAT_Lambris_Bois")
y_pl = Y_SEP - CL / 2
for i, (xa, xb) in enumerate([(EP + 0.02, PORTE_RESERVE[0] - 0.07), (PORTE_RESERVE[1] + 0.07, PORTE_STAFF[0] - 0.07),
                              (PORTE_STAFF[1] + 0.07, W - EP - 0.02)], 1):
    boite("Plinthe_fond_%d" % i, "Murs_interieurs", xa, xb, y_pl - 0.015, y_pl, 0, 0.08, "MAT_Bois_Clair")

ajouter("Logo_mur_marque", "plane", "Murs_interieurs", EP + 0.005, 2.6, 2.30, 1.59, 0.90, 0, rx=90, rz=90,
        mat="MAT_Logo", notes="logo sur le mur de marque, face vers +X")

# =============================================================================
# MOBILIER DE VENTE
# =============================================================================

MV = "Mobilier_vente"
# Étagères murales : gauche (épices), droite (marinades), fond (essentiels).
for i in range(6):
    meuble("Etagere_gauche_%d" % (i + 1), "etagere_murale", MV, EP + 0.02 + 0.225, 5.2 + 1.2 * i,
           1.2, 0.45, 2.2, "MAT_Bois_Clair", rz=90, notes="etagere murale, face vers la salle")
for i in range(5):
    meuble("Etagere_droite_%d" % (i + 1), "etagere_murale", MV, W - EP - 0.02 - 0.225, 5.8 + 1.2 * i,
           1.2, 0.45, 2.2, "MAT_Bois_Clair", rz=-90, notes="etagere murale marinades")
for i in range(10):
    meuble("Etagere_fond_%d" % (i + 1), "etagere_murale", MV, 10.2 + 1.2 * i, Y_SEP - CL / 2 - 0.225,
           1.2, 0.45, 2.2, "MAT_Bois_Clair", notes="etagere murale du fond")
# Vitrines réfrigérées (marinades fraîches)
for i in range(4):
    meuble("Frigo_%d" % (i + 1), "frigo", MV, 1.625 + 1.25 * i, Y_SEP - CL / 2 - 0.375,
           1.25, 0.75, 2.10, "MAT_Laque_Blanche", notes="vitrine refrigeree portes vitrees")
# Gondoles double face en îlots, dans le sens de la profondeur
for cote, xs in (("G", [3.2, 6.0, 8.8]), ("D", [15.2, 18.0, 20.8])):
    for i, x in enumerate(xs, 1):
        meuble("Gondole_%s_%d" % (cote, i), "gondole", MV, x, 7.4, 3.6, 1.0, 1.6, "MAT_Bois_Clair", rz=90,
               notes="gondole double face 3.60 m")
# Présentoirs à bacs (épices en vrac) sur l'axe central
for i, y in enumerate([6.4, 8.8], 1):
    meuble("Presentoir_vrac_%d" % i, "presentoir_vrac", MV, 12.0, y, 2.0, 1.2, 0.85, "MAT_Bois_Clair",
           notes="presentoir a bacs, epices en vrac")

# =============================================================================
# DÉGUSTATION ET ACCUEIL
# =============================================================================

MD = "Mobilier_degustation"
for t, xt in enumerate([3.0, 6.8], 1):
    meuble("Table_degustation_%d" % t, "table", MD, xt, 2.8, 1.8, 0.7, 1.05, "MAT_Bois_Clair",
           notes="table haute de degustation")
    for k, (ox, oy) in enumerate([(-0.5, -0.6), (0.5, -0.6), (-0.5, 0.6), (0.5, 0.6)], 1):
        meuble("Tabouret_%d_%d" % (t, k), "tabouret", MD, xt + ox, 2.8 + oy, 0.38, 0.38, 0.75, "MAT_Cuir_Bordeaux")
    for k, ox in enumerate([-0.45, 0.45], 1):
        suspension("Suspension_degustation_%d_%d" % (t, k), xt + ox, 2.8, 2.20, "au-dessus de la table")
meuble("Banc_attente", "table", MD, 9.2, 0.75, 1.6, 0.45, 0.45, "MAT_Bois_Clair", notes="banc d attente")

PL = "Plantes"
for i, (x, y) in enumerate([(0.75, 0.75), (W - 0.75, 0.75), (9.15, 11.45), (0.75, 4.2)], 1):
    meuble("Plante_%d" % i, "plante", PL, x, y, 0.6, 0.6, 1.5, "MAT_Pot")

ajouter("Tapis_entree", "plane", "Decor_sol", W / 2, 0.95, 0.005, 2.0, 1.4,
        mat="MAT_Tapis_Fibre", notes="tapis, texture gris raye (teinte modifiable dans le materiau)")
ajouter("Tapis_logo", "plane", "Decor_sol", W / 2, 0.95, 0.008, 1.24, 0.70,
        mat="MAT_Logo", notes="logo au centre du tapis, ratio respecte")

# =============================================================================
# CAISSES : deux comptoirs en L, équipés, et deux bornes libre-service
# Le caissier est côté façade (y < 3,40), le client côté salle (y > 4,10).
# =============================================================================

CC, EQ = "Comptoir_caisse", "Equipement_caisse"
for k, x0 in enumerate([14.4, 18.6], 1):
    s = "_%d" % k
    boite("Comptoir_bar" + s, CC, x0, x0 + 2.6, 3.4, 4.1, 0, 1.0, "MAT_Bois_Clair", "barre du comptoir")
    boite("Comptoir_retour" + s, CC, x0 + 1.9, x0 + 2.6, 2.7, 3.4, 0, 1.0, "MAT_Bois_Clair", "retour du L")
    boite("Comptoir_plan_bar" + s, CC, x0 - 0.02, x0 + 2.62, 3.38, 4.12, 1.0, 1.04, "MAT_Plan_Comptoir")
    boite("Comptoir_plan_retour" + s, CC, x0 + 1.88, x0 + 2.62, 2.68, 3.38, 1.0, 1.04, "MAT_Plan_Comptoir")
    boite("Comptoir_lisere" + s, CC, x0 - 0.02, x0 + 2.62, 4.12, 4.14, 1.0, 1.04, "MAT_Laiton_Brosse",
          "lisere laiton cote client")
    z = 1.04
    meuble("Ecran_caisse" + s, "ecran", EQ, x0 + 0.9, 3.65, 0.45, 0.18, 0.40, "MAT_Plastique_Noir", z_bas=z,
           notes="ecran caissier")
    meuble("Ecran_client" + s, "ecran", EQ, x0 + 0.9, 3.97, 0.30, 0.14, 0.30, "MAT_Plastique_Noir", rz=180,
           z_bas=z, notes="afficheur client")
    meuble("Clavier" + s, "box", EQ, x0 + 0.9, 3.48, 0.44, 0.14, 0.025, "MAT_Plastique_Noir", z_bas=z)
    meuble("Scanner" + s, "scanner", EQ, x0 + 1.6, 3.75, 0.10, 0.12, 0.20, "MAT_Plastique_Noir", z_bas=z,
           notes="scanner code-barres sur socle")
    meuble("TPE" + s, "tpe", EQ, x0 + 2.05, 3.92, 0.09, 0.18, 0.07, "MAT_Plastique_Noir", rz=180, z_bas=z,
           notes="terminal de paiement tourne vers le client")
    meuble("Imprimante_ticket" + s, "box", EQ, x0 + 0.3, 3.6, 0.15, 0.20, 0.14, "MAT_Plastique_Noir", z_bas=z)
    meuble("Caisse_enregistreuse" + s, "box", EQ, x0 + 2.25, 3.03, 0.41, 0.42, 0.11, "MAT_Plastique_Noir",
           z_bas=z, notes="tiroir-caisse")
    meuble("Unite_centrale" + s, "box", EQ, x0 + 0.4, 3.15, 0.20, 0.40, 0.40, "MAT_Plastique_Noir",
           notes="ordinateur de caisse sous le comptoir")
    suspension("Suspension_caisse" + s, x0 + 1.3, 3.75, 2.30, "au-dessus de la caisse")
for k, y in enumerate([2.2, 3.4], 1):
    meuble("Borne_libre_service_%d" % k, "borne", EQ, 22.7, y, 0.6, 0.5, 1.55, "MAT_Laque_Blanche", rz=-90,
           notes="borne d encaissement libre-service")

# =============================================================================
# LOCAUX DU PERSONNEL
# =============================================================================

BO, SA, LT = "Mobilier_back_office", "Sanitaires", "Local_technique"
# Réserve
for i, (x, y, rz, l) in enumerate([(1.3, 15.5, 0, 2.0), (5.65, 15.5, 0, 2.0), (7.85, 15.5, 0, 2.0),
                                   (0.5, 13.4, 90, 2.0), (4.5, 13.6, 0, 2.4)], 1):
    meuble("Rayonnage_reserve_%d" % i, "rayonnage", BO, x, y, l, 0.6, 2.4, "MAT_Metal_Galva", rz=rz)
meuble("Table_reserve", "table", BO, 7.6, 14.2, 1.6, 0.8, 0.9, "MAT_Bois_Clair", notes="table de preparation")
# Bureau
meuble("Bureau_table", "table", BO, 11.4, 15.4, 1.4, 0.7, 0.75, "MAT_Bois_Clair")
meuble("Bureau_chaise", "chaise", BO, 11.4, 14.75, 0.45, 0.45, 0.9, "MAT_Plastique_Noir", rz=180)
meuble("Bureau_ecran", "ecran", BO, 11.4, 15.55, 0.55, 0.18, 0.40, "MAT_Plastique_Noir", z_bas=0.75)
meuble("Bureau_clavier", "box", BO, 11.4, 15.25, 0.44, 0.14, 0.025, "MAT_Plastique_Noir", z_bas=0.75)
meuble("Bureau_unite_centrale", "box", BO, 12.35, 15.45, 0.20, 0.40, 0.40, "MAT_Plastique_Noir")
meuble("Bureau_armoire", "box", BO, 9.4, 15.15, 0.5, 1.1, 2.0, "MAT_Laque_Blanche")
# Vestiaire
meuble("Casiers_vestiaire", "casiers", BO, 16.6, 15.55, 2.4, 0.5, 1.9, "MAT_Mur_Bordeaux", notes="6 colonnes de casiers")
meuble("Banc_vestiaire", "table", BO, 16.9, 14.6, 1.4, 0.4, 0.45, "MAT_Bois_Clair")
boite("Miroir_vestiaire", BO, 17.985, 17.995, 14.05, 14.55, 1.05, 1.95, "MAT_Miroir")
# Salle de pause
meuble("Pause_plan_travail", "box", BO, 20.8, 15.5, 2.0, 0.6, 0.9, "MAT_Bois_Clair", notes="kitchenette")
meuble("Pause_frigo", "box", BO, 19.45, 15.5, 0.6, 0.6, 0.85, "MAT_Laque_Blanche")
meuble("Pause_table", "table", BO, 20.3, 14.4, 1.0, 0.7, 0.75, "MAT_Bois_Clair")
meuble("Pause_chaise_1", "chaise", BO, 19.55, 14.4, 0.45, 0.45, 0.9, "MAT_Bois_Clair", rz=90)
meuble("Pause_chaise_2", "chaise", BO, 21.05, 14.4, 0.45, 0.45, 0.9, "MAT_Bois_Clair", rz=-90)
# WC du personnel
xw = X_PIECES[0] + CL / 2           # face ouest du WC (13,10)
boite("WC_cuvette", SA, 14.15, 14.55, 15.0, 15.68, 0, 0.40, "MAT_Sanitaire_Blanc", "cuvette contre le fond")
boite("WC_reservoir", SA, 14.15, 14.55, 15.68, 15.80, 0.20, 0.95, "MAT_Sanitaire_Blanc", "reservoir")
boite("Lavabo_vasque", SA, xw, xw + 0.40, 14.75, 15.25, 0.775, 0.925, "MAT_Sanitaire_Blanc")
boite("Lavabo_pied", SA, xw + 0.14, xw + 0.26, 14.94, 15.06, 0, 0.775, "MAT_Sanitaire_Blanc")
ajouter("Lavabo_robinet", "cylinder", SA, xw + 0.05, 15.0, 1.0, 0.03, 0.03, 0.15, mat="MAT_Laiton_Brosse")
boite("Miroir_WC", SA, xw, xw + 0.01, 14.78, 15.22, 1.25, 1.85, "MAT_Miroir")
ajouter("Porte_papier_WC", "cylinder", SA, X_PIECES[1] - CL / 2 - 0.06, 15.0, 0.70, 0.11, 0.11, 0.10, rx=90,
        mat="MAT_Sanitaire_Blanc", notes="rouleau horizontal")
boite("Grille_ventilation_WC", LT, 13.875, 14.025, D - EP - 0.01, D - EP, 2.725, 2.875, "MAT_Alu_Cadre")
# Local technique
boite("Tableau_electrique", LT, W - EP - 0.05, W - EP, 14.3, 14.9, 1.0, 1.8, "MAT_Plafond_Blanc")
meuble("Baie_informatique", "box", LT, 22.3, 15.45, 0.6, 0.6, 1.6, "MAT_Plastique_Noir")

# =============================================================================
# ÉCLAIRAGE
# =============================================================================

for r, y in enumerate([1.6, 4.4, 7.4, 10.4], 1):
    for c, x in enumerate([2.0, 5.9, 9.8, 14.2, 18.1, 22.0], 1):
        spot("Spot_vente_R%dC%d" % (r, c), x, y)
for i, (x, y) in enumerate([(2.3, 13.3), (6.6, 13.3), (2.3, 14.9), (6.6, 14.9)], 1):
    spot("Spot_reserve_%d" % i, x, y)
for i, x in enumerate([11.5, 16.5, 21.0], 1):
    spot("Spot_couloir_%d" % i, x, 12.8)
for nom_s, xa, xb in [("Spot_bureau", X_RES, X_PIECES[0]), ("Spot_WC", X_PIECES[0], X_PIECES[1]),
                      ("Spot_vestiaire", X_PIECES[1], X_PIECES[2]), ("Spot_pause", X_PIECES[2], X_PIECES[3]),
                      ("Spot_local_technique", X_PIECES[3], W - EP)]:
    spot(nom_s, (xa + xb) / 2, 14.7)

# =============================================================================
# ZONES (marqueurs vides pour placer les produits)
# =============================================================================

zone("Zone_Accueil", 10.8, 13.2, 0.2, 1.8, "accueil et tapis")
zone("Zone_Degustation", 1.6, 8.2, 1.6, 4.0, "tables hautes de degustation")
zone("Zone_Mur_marque", 0.2, 0.4, 1.8, 3.4, "logo du mur de marque")
zone("Zone_Caisses", 14.4, 21.2, 2.7, 4.1, "deux comptoirs de caisse")
zone("Zone_Bornes", 22.4, 23.0, 1.9, 3.7, "bornes libre-service")
zone("Zone_Epices", 0.2, 9.3, 4.6, 11.8, "etageres gauche et gondoles G")
zone("Zone_Vrac", 11.0, 13.0, 5.8, 9.4, "presentoirs a bacs")
zone("Zone_Essentiels", 14.7, 21.3, 5.6, 9.2, "gondoles D : pate d arachide, huile rouge")
zone("Zone_Marinades", 23.3, 23.8, 5.2, 11.2, "etageres murales droite")
zone("Zone_Produits_frais", 1.0, 6.0, 11.25, 12.0, "vitrines refrigerees")
zone("Zone_Mur_fond", 9.6, 21.6, 11.55, 12.0, "etageres du fond")
zone("Zone_Reserve", EP, X_RES - CL / 2, Y_SEP + CL / 2, D - EP, "reserve")
zone("Zone_Bureau", X_RES + CL / 2, X_PIECES[0] - CL / 2, Y_COUL + CL / 2, D - EP, "bureau")
zone("Zone_WC", X_PIECES[0] + CL / 2, X_PIECES[1] - CL / 2, Y_COUL + CL / 2, D - EP, "toilettes du personnel")
zone("Zone_Vestiaire", X_PIECES[1] + CL / 2, X_PIECES[2] - CL / 2, Y_COUL + CL / 2, D - EP, "vestiaire")
zone("Zone_Pause", X_PIECES[2] + CL / 2, X_PIECES[3] - CL / 2, Y_COUL + CL / 2, D - EP, "salle de pause")
zone("Zone_Local_technique", X_PIECES[3] + CL / 2, W - EP, Y_COUL + CL / 2, D - EP, "local technique")

# =============================================================================
# ÉCLAIRAGE RENFORCÉ (version 3) : aucun coin sombre
# Ajouté en fin de fichier pour garder les numéros des lignes précédentes.
# Dalles LED entre les spots, lécheurs de murs au-dessus des étagères, une
# dalle au moins par pièce du personnel.
# =============================================================================

# Salle de vente : dalles au milieu des mailles de spots, plus une rangée le
# long des vitrines et une le long du fond.
for r, y in enumerate([0.9, 3.0, 5.9, 8.9, 11.3], 1):
    for c, x in enumerate([1.0, 3.95, 7.85, 12.0, 16.15, 20.05, 23.0], 1):
        if c in (1, 7) and y > 4.5:
            continue                    # le long des étagères latérales : lécheurs
        panneau("Dalle_vente_R%dC%d" % (r, c), x, y)
# Lécheurs : étagères gauche, droite, fond, vitrines réfrigérées.
ruban("Lecheur_gauche", 1.25, 4.7, 1.25, 11.6, "-x")
ruban("Lecheur_droite", W - 1.25, 5.3, W - 1.25, 11.1, "+x")
ruban("Lecheur_fond", 9.7, 10.85, 21.5, 10.85, "+y")
ruban("Lecheur_frigos", 1.1, 10.55, 5.9, 10.55, "+y")
# Locaux du personnel
for i, (x, y) in enumerate([(4.45, 13.3), (4.45, 14.9), (1.2, 14.1), (7.9, 14.1)], 1):
    panneau("Dalle_reserve_%d" % i, x, y)
for i, x in enumerate([10.2, 14.0, 19.0, 23.1], 1):
    panneau("Dalle_couloir_%d" % i, x, 12.8)
for nom_d, xa, xb in [("Dalle_bureau", X_RES, X_PIECES[0]), ("Dalle_WC", X_PIECES[0], X_PIECES[1]),
                      ("Dalle_vestiaire", X_PIECES[1], X_PIECES[2]), ("Dalle_pause", X_PIECES[2], X_PIECES[3]),
                      ("Dalle_local_technique", X_PIECES[3], W - EP)]:
    panneau(nom_d, (xa + xb) / 2, 15.3, cote=0.60 if xb - xa > 2.2 else 0.45)


if __name__ == "__main__":
    noms = [l["nom"] for l in LIGNES]
    doublons = {x for x in noms if noms.count(x) > 1}
    if doublons:
        raise SystemExit("noms en double : %s" % sorted(doublons))
    sortie = os.path.join(os.path.dirname(os.path.abspath(__file__)), "elements.csv")
    with open(sortie, "w", newline="", encoding="utf-8") as f:
        ecrivain = csv.DictWriter(f, fieldnames=CHAMPS, lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(LIGNES)
    print("%d lignes ecrites dans %s" % (len(LIGNES), sortie))
