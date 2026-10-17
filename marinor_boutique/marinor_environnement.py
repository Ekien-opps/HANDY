# -*- coding: utf-8 -*-
"""
Marin'Or Ivoire : environnement urbain de Cocody Riviera, Abidjan (Blender 5.1)
==============================================================================

Une avenue résidentielle de Cocody Riviera à l'heure dorée, autour du magasin :
avenue bitumée bordée de flamboyants, manguiers, fromagers et palmiers, villas
contemporaines derrière de hauts murs blancs et des portails en fer forgé
noir, jardins débordants (hibiscus, bougainvilliers, bananiers), voitures,
agent de sécurité devant un portail, soleil bas et ciel bleu à nuages doux.

Le magasin n'est pas modifié : il est posé sur sa parcelle, au niveau du
trottoir, avec un parvis pavé en pente douce, un parking devant la façade et
une allée de service vers la porte de livraison.

Utilisation
-----------
1. Ce script est dans `marinor_boutique/`, à côté de `marinor_batiment.py`,
   `elements.csv` et du dossier `textures/` (avec `textures/env/`).
2. Dans Blender 5.1 : Scripting > Ouvrir > ce fichier > Exécuter (Alt+P).
   - Si le magasin n'est pas dans la scène, le script lance d'abord
     `marinor_batiment.py` pour le construire.
   - Il construit ensuite le décor, règle le ciel, le soleil, les caméras et le
     rendu, puis enregistre `marinor_cocody.blend` dans ce même dossier.
3. Rapport dans la console et dans le texte Blender `Rapport_Cocody`.

Relançable : tout ce que ce script crée porte la marque TAG_ENV et est
supprimé au début. Aucune dépendance externe (bpy, mathutils, bibliothèque
standard). Le décor est reproductible : même GRAINE = même rue.

Repères (ceux du magasin) : unité le mètre, origine au coin extérieur avant
gauche du magasin, X le long de l'avenue, Y vers le fond du magasin (la rue
est du côté des y négatifs), Z vers le haut, sol fini du magasin à z = 0.
"""

import math
import os
import random
import traceback

import bpy
from mathutils import Matrix, Vector


# =============================================================================
# CONSTANTES
# =============================================================================

TAG_ENV = "marinor_env"
TEXTURES_ENV_DIR = "//textures/env/"
BLEND_SORTIE = "marinor_cocody.blend"
SCRIPT_MAGASIN = "marinor_batiment.py"
OBJET_TEMOIN_MAGASIN = "Sol_Vente"          # présent si le magasin est construit
GRAINE = 2026

# Soleil de fin d'après-midi : bas, à l'ouest-sud-ouest de l'avenue.
SOLEIL_ELEVATION_DEG = 17.0
SOLEIL_AZIMUT_DEG = 216.0           # angle depuis +X (0 = +X, 90 = +Y, 180 = -X) : sud-ouest
SOLEIL_PUISSANCE = 8.0              # W/m²
SOLEIL_TEMPERATURE_K = 3600.0
SOLEIL_ANGLE_DEG = 0.9              # douceur des ombres
CIEL_PUISSANCE = 0.15
CIEL_NUAGES = 0.55                  # 0 = ciel pur, 1 = très nuageux
LUMINOSITE_NUAGES = 8.0
BRUME_DISTANCE_M = 1100.0           # distance à laquelle la brume atteint 63 %
BRUME_COULEUR = "#e8c79a"
BRUME_FORCE = 0.45                  # luminosité de la brume (à accorder au ciel)

# Vitrines du magasin : le matériau d'origine (alpha 0,35) paraît laiteux en
# plein jour. True = verre clair (reflets selon l'angle, intérieur bien visible),
# appliqué au matériau MAT_Verre_Clair de ce fichier uniquement : la géométrie du
# magasin et son script ne changent pas.
VITRAGE_REALISTE_MAGASIN = True

MOTEUR = "CYCLES"                   # "CYCLES" (photoréaliste) ou "BLENDER_EEVEE"
RESOLUTION = (1920, 1080)
EXPOSITION = 0.6                    # réglage d'exposition de la vue (en IL)
ECHANTILLONS_CYCLES = 256
CAMERA_ACTIVE = "CAM_Avenue_Cocody"

# Profil en travers de l'avenue (y), côté magasin (nord) puis côté opposé (sud).
Y_LIMITE_N = -7.0                   # limite des parcelles côté magasin
Y_PLANTATION_N = (-7.8, -7.0)       # bande plantée au pied des murs
Y_TROTTOIR_N = (-9.6, -7.8)         # trottoir pavé
Y_ACCOTEMENT_N = (-11.2, -9.6)      # accotement engazonné, arbres d'alignement
Y_BORDURE_N = (-11.35, -11.2)
Y_ROUTE = (-19.35, -11.35)          # chaussée de 8 m, deux voies
Y_BORDURE_S = (-19.5, -19.35)
Y_ACCOTEMENT_S = (-21.1, -19.5)
Y_TROTTOIR_S = (-22.9, -21.1)
Y_PLANTATION_S = (-23.7, -22.9)
Y_LIMITE_S = -23.7

Z_ROUTE = -0.30                     # dessus de la chaussée
Z_TROTTOIR = -0.15                  # dessus des trottoirs et bordures
Z_ACCOTEMENT = -0.16
Z_PLANTATION = -0.18
Z_SOL = -0.36                       # terrain naturel (sous la chaussée) et pied des murs
Z_JARDIN = -0.12                    # pelouses des villas
Z_PARVIS_FACADE = -0.025            # parvis du magasin au pied de la façade

X_AVENUE = (-1600.0, 1600.0)        # longueur de la chaussée
X_VILLAS = (-520.0, 520.0)          # villas de part et d'autre
X_ARBRES = (-700.0, 700.0)          # arbres d'alignement

# Accotement d'en face laissé sans arbre : vue dégagée sur la façade du magasin.
# Les arbres à l'ouest (côté soleil) sont écartés pour que la façade reste au soleil.
VUE_DEGAGEE_FACADE = (-30.0, 40.0)
VUE_DEGAGEE_NORD = (-22.0, 39.0)
X_PORTAIL_GARDIEN = 8.0             # l'agent de sécurité garde le portail le plus proche

# Parcelle du magasin (24 x 16 m) : allée de service à gauche, cour à l'arrière,
# jardin à droite derrière une grande jardinière basse (le magasin reste visible
# depuis l'avenue).
PARCELLE_MAGASIN = (-4.0, 38.0, Y_LIMITE_N, 20.0)

COLLECTIONS_ENV = [
    "ENV_Voirie", "ENV_Parcelle_magasin", "ENV_Villas", "ENV_Portails", "ENV_Vegetation",
    "ENV_Mobilier_urbain", "ENV_Vehicules", "ENV_Personnages", "ENV_Lointain",
    "ENV_Lumieres", "ENV_Cameras",
]


# =============================================================================
# RAPPORT
# =============================================================================

RAPPORT = {"objets": 0, "instances": 0, "faces": 0, "textures": [], "manquantes": [],
           "avertissements": [], "erreurs": []}


def log(msg):
    print("[Cocody] " + msg)


def avertir(msg):
    RAPPORT["avertissements"].append(msg)
    log("AVERTISSEMENT : " + msg)


def erreur(msg):
    RAPPORT["erreurs"].append(msg)
    log("ERREUR : " + msg)


def marquer(id_data):
    id_data[TAG_ENV] = True
    return id_data


def hex_lin(h, a=1.0):
    h = h.lstrip("#")
    s = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s) + (a,)


# =============================================================================
# DOSSIER, NETTOYAGE, MAGASIN
# =============================================================================

def dossier_projet():
    candidats = []
    if bpy.data.filepath:
        candidats.append(os.path.dirname(bpy.data.filepath))
    f = globals().get("__file__")
    if f:
        candidats.append(os.path.dirname(bpy.path.abspath(f)))
    try:
        esp = bpy.context.space_data
        if esp and esp.type == 'TEXT_EDITOR' and esp.text and esp.text.filepath:
            candidats.append(os.path.dirname(bpy.path.abspath(esp.text.filepath)))
    except Exception:
        pass
    for t in bpy.data.texts:
        if t.filepath:
            candidats.append(os.path.dirname(bpy.path.abspath(t.filepath)))
    candidats.append(os.getcwd())
    for d in candidats:
        if d and os.path.isfile(os.path.join(d, SCRIPT_MAGASIN)):
            return os.path.normpath(d)
    return None


def nettoyer():
    scene_coll = bpy.context.scene.collection
    for ob in list(bpy.data.objects):
        if ob.get(TAG_ENV):
            bpy.data.objects.remove(ob, do_unlink=True)
    for coll in list(bpy.data.collections):
        if coll.get(TAG_ENV) or coll.name in COLLECTIONS_ENV:
            for ob in list(coll.objects):
                if len(ob.users_collection) == 1:
                    scene_coll.objects.link(ob)
            bpy.data.collections.remove(coll)
    blocs = (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras,
             bpy.data.images, bpy.data.node_groups, bpy.data.worlds, bpy.data.curves, bpy.data.texts)
    for bloc in blocs:
        for id_data in list(bloc):
            if id_data.get(TAG_ENV):
                bloc.remove(id_data)


def assurer_magasin(dossier):
    if bpy.data.objects.get(OBJET_TEMOIN_MAGASIN) is not None:
        log("magasin présent dans la scène")
        return True
    chemin = os.path.join(dossier, SCRIPT_MAGASIN)
    log("magasin absent : exécution de " + chemin)
    try:
        code = compile(open(chemin, encoding="utf-8").read(), chemin, "exec")
        exec(code, {"__name__": "__main__", "__file__": chemin})
    except Exception:
        erreur("construction du magasin impossible :\n" + traceback.format_exc())
        return False
    return bpy.data.objects.get(OBJET_TEMOIN_MAGASIN) is not None


# =============================================================================
# MATÉRIAUX (procéduraux, sauf les cartes de feuillage)
# =============================================================================

MATS = {}
GROUPE_BRUME = None


def arbre_noeuds(mat):
    if mat.node_tree is None:
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    return nt


def entree(noeud, nom, valeur):
    s = noeud.inputs.get(nom)
    if s is None:
        avertir("entrée '%s' absente (%s)" % (nom, noeud.bl_idname))
        return
    s.default_value = valeur


def creer_groupe_brume():
    """Shader -> mélange vers une émission couleur de brume selon la distance à la
    caméra (rayons caméra seulement : reflets et éclairage non affectés)."""
    ng = marquer(bpy.data.node_groups.new("ENV_Brume", "ShaderNodeTree"))
    ng.interface.new_socket("Shader", in_out='INPUT', socket_type='NodeSocketShader')
    ng.interface.new_socket("Shader", in_out='OUTPUT', socket_type='NodeSocketShader')
    n, l = ng.nodes, ng.links
    gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    lp = n.new("ShaderNodeLightPath")
    div = n.new("ShaderNodeMath"); div.operation = 'DIVIDE'
    div.inputs[1].default_value = -BRUME_DISTANCE_M
    ex = n.new("ShaderNodeMath"); ex.operation = 'EXPONENT'
    inv = n.new("ShaderNodeMath"); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
    mul = n.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'
    em = n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = hex_lin(BRUME_COULEUR)
    em.inputs["Strength"].default_value = BRUME_FORCE
    em.name = em.label = "Couleur brume"
    mix = n.new("ShaderNodeMixShader")
    l.new(lp.outputs["Ray Length"], div.inputs[0])
    l.new(div.outputs[0], ex.inputs[0])
    l.new(ex.outputs[0], inv.inputs[1])
    l.new(inv.outputs[0], mul.inputs[0])
    l.new(lp.outputs["Is Camera Ray"], mul.inputs[1])
    l.new(mul.outputs[0], mix.inputs[0])
    l.new(gi.outputs[0], mix.inputs[1])
    l.new(em.outputs[0], mix.inputs[2])
    l.new(mix.outputs[0], go.inputs[0])
    return ng


def sortie_avec_brume(nt, shader_socket):
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    if GROUPE_BRUME is not None:
        g = nt.nodes.new("ShaderNodeGroup")
        g.node_tree = GROUPE_BRUME
        g.location = (700, 0)
        nt.links.new(shader_socket, g.inputs[0])
        nt.links.new(g.outputs[0], out.inputs["Surface"])
    else:
        nt.links.new(shader_socket, out.inputs["Surface"])
    return out


def coord_uv(nt, echelle=1.0):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if echelle == 1.0:
        return tc.outputs["UV"]
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (echelle, echelle, echelle)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def rampe(nt, fac_socket, couleurs):
    """ColorRamp : couleurs = [(position, hex), ...]."""
    cr = nt.nodes.new("ShaderNodeValToRGB")
    el = cr.color_ramp.elements
    while len(el) > 1:
        el.remove(el[-1])
    el[0].position, el[0].color = couleurs[0][0], hex_lin(couleurs[0][1])
    for pos, h in couleurs[1:]:
        e = el.new(pos)
        e.color = hex_lin(h)
    nt.links.new(fac_socket, cr.inputs["Fac"])
    return cr.outputs["Color"]


def melange_rgb(nt, a, b, facteur=1.0, mode='MIX'):
    """Nœud Mix en couleur (sockets par identifiant : plusieurs portent le même nom)."""
    mx = nt.nodes.new("ShaderNodeMix")
    mx.data_type = 'RGBA'
    mx.blend_type = mode
    sock = {s.identifier: s for s in mx.inputs}
    for cle, val in (("Factor_Float", facteur), ("A_Color", a), ("B_Color", b)):
        if isinstance(val, (int, float)):
            sock[cle].default_value = val
        elif isinstance(val, tuple):
            sock[cle].default_value = val
        else:
            nt.links.new(val, sock[cle])
    return [o for o in mx.outputs if o.identifier == "Result_Color"][0]


def bruit(nt, vecteur, echelle, detail=4.0, rugosite=0.5, etirement=None):
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = echelle
    nz.inputs["Detail"].default_value = detail
    nz.inputs["Roughness"].default_value = rugosite
    if etirement is not None:
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = etirement
        nt.links.new(vecteur, mp.inputs["Vector"])
        vecteur = mp.outputs["Vector"]
    nt.links.new(vecteur, nz.inputs["Vector"])
    return nz.outputs["Fac"]


def relief(nt, bsdf, hauteur_socket, force, distance=0.02):
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = force
    b.inputs["Distance"].default_value = distance
    nt.links.new(hauteur_socket, b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])


def principled(nt, couleur=None, rugosite=0.5, metal=0.0, vernis=0.0, emission=None, force_em=0.0):
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    if isinstance(couleur, str):
        p.inputs["Base Color"].default_value = hex_lin(couleur)
    elif couleur is not None:
        nt.links.new(couleur, p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = rugosite
    p.inputs["Metallic"].default_value = metal
    if vernis:
        entree(p, "Coat Weight", vernis)
        entree(p, "Coat Roughness", 0.04)
    if emission:
        entree(p, "Emission Color", hex_lin(emission))
        entree(p, "Emission Strength", force_em)
    return p


def nouveau_mat(nom, couleur_vue="#808080"):
    mat = marquer(bpy.data.materials.new(nom))
    mat.diffuse_color = hex_lin(couleur_vue)
    MATS[nom] = mat
    return mat, arbre_noeuds(mat)


def mat_uni(nom, couleur, rugosite=0.5, metal=0.0, vernis=0.0, emission=None, force_em=0.0,
            grain=0.0, echelle_grain=8.0):
    """Matériau uni, avec un léger grain de couleur optionnel."""
    mat, nt = nouveau_mat(nom, couleur)
    coul = couleur
    if grain:
        f = bruit(nt, coord_uv(nt), echelle_grain, 6.0, 0.6)
        c = hex_lin(couleur)
        sombre = "#%02x%02x%02x" % tuple(int(255 * max(0.0, (v ** (1 / 2.2)) * (1 - grain))) for v in c[:3])
        clair = "#%02x%02x%02x" % tuple(int(255 * min(1.0, (v ** (1 / 2.2)) * (1 + grain * 0.5))) for v in c[:3])
        coul = rampe(nt, f, [(0.3, sombre), (0.7, clair)])
    p = principled(nt, coul, rugosite, metal, vernis, emission, force_em)
    sortie_avec_brume(nt, p.outputs["BSDF"])
    mat.roughness = rugosite
    return mat


def mat_asphalte():
    mat, nt = nouveau_mat("ENV_Asphalte", "#353537")
    uv = coord_uv(nt)
    fin = bruit(nt, uv, 60.0, 8.0, 0.7)
    large = bruit(nt, uv, 0.06, 3.0, 0.5)
    c_fin = rampe(nt, fin, [(0.35, "#2a2a2c"), (0.65, "#454547")])
    c_large = rampe(nt, large, [(0.35, "#58585a"), (0.65, "#3b3b3e")])
    res = melange_rgb(nt, c_fin, c_large, 0.9, 'MULTIPLY')
    # le mélange multiplie : on remonte la luminosité
    br = nt.nodes.new("ShaderNodeBrightContrast"); br.inputs["Bright"].default_value = 0.06
    nt.links.new(res, br.inputs["Color"])
    rug = nt.nodes.new("ShaderNodeMapRange")
    rug.inputs["To Min"].default_value = 0.62; rug.inputs["To Max"].default_value = 0.9
    nt.links.new(large, rug.inputs["Value"])
    p = principled(nt, br.outputs["Color"])
    nt.links.new(rug.outputs["Result"], p.inputs["Roughness"])
    relief(nt, p, fin, 0.25, 0.01)
    sortie_avec_brume(nt, p.outputs["BSDF"])


def mat_pave(nom, couleur_a, couleur_b, joint, l_brique, h_brique, decalage=0.5, rugosite=0.8):
    mat, nt = nouveau_mat(nom, couleur_a)
    uv = coord_uv(nt)
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.offset = decalage
    br.inputs["Color1"].default_value = hex_lin(couleur_a)
    br.inputs["Color2"].default_value = hex_lin(couleur_b)
    br.inputs["Mortar"].default_value = hex_lin(joint)
    br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.006
    br.inputs["Brick Width"].default_value = l_brique
    br.inputs["Row Height"].default_value = h_brique
    br.inputs["Bias"].default_value = 0.0
    nt.links.new(uv, br.inputs["Vector"])
    sale = bruit(nt, uv, 1.5, 4.0, 0.6)
    tache = rampe(nt, sale, [(0.4, "#c8c2b8"), (0.75, "#ffffff")])
    p = principled(nt, melange_rgb(nt, br.outputs["Color"], tache, 1.0, 'MULTIPLY'), rugosite)
    relief(nt, p, br.outputs["Fac"], 0.6, 0.01)
    sortie_avec_brume(nt, p.outputs["BSDF"])


def mat_gazon(nom="ENV_Gazon", sec=0.25):
    mat, nt = nouveau_mat(nom, "#4a7a28")
    uv = coord_uv(nt)
    fin = bruit(nt, uv, 45.0, 6.0, 0.7)
    moyen = bruit(nt, uv, 2.5, 4.0, 0.6)
    c1 = rampe(nt, fin, [(0.3, "#2f561a"), (0.7, "#5c8d2c")])
    c2 = rampe(nt, moyen, [(0.0, "#ffffff"), (0.55, "#ffffff"), (0.75, "#c9b779" if sec else "#ffffff")])
    p = principled(nt, melange_rgb(nt, c1, c2, min(1.0, sec * 3), 'MULTIPLY'), 0.92)
    entree(p, "Specular IOR Level", 0.3)
    relief(nt, p, fin, 0.5, 0.02)
    sortie_avec_brume(nt, p.outputs["BSDF"])


def mat_enduit(nom, couleur, salissure=0.12):
    """Enduit de façade : grain fin et légères coulures en bas des murs."""
    mat, nt = nouveau_mat(nom, couleur)
    uv = coord_uv(nt)
    grain = bruit(nt, uv, 30.0, 8.0, 0.65)
    taches = bruit(nt, uv, 0.8, 5.0, 0.6, etirement=(1.0, 0.25, 1.0))
    c = rampe(nt, taches, [(0.45, couleur), (0.85, couleur)])
    fr = nt.nodes.new("ShaderNodeMapRange")
    fr.inputs["From Min"].default_value = 0.55; fr.inputs["From Max"].default_value = 0.8
    fr.inputs["To Min"].default_value = 0.0; fr.inputs["To Max"].default_value = salissure * 3
    nt.links.new(taches, fr.inputs["Value"])
    p = principled(nt, melange_rgb(nt, c, (0.82, 0.8, 0.76, 1.0), fr.outputs["Result"], 'MULTIPLY'), 0.88)
    relief(nt, p, grain, 0.18, 0.005)
    sortie_avec_brume(nt, p.outputs["BSDF"])


def mat_ecorce(nom, couleur_a, couleur_b, etirement=(1.0, 6.0, 1.0), anneaux=False):
    mat, nt = nouveau_mat(nom, couleur_a)
    uv = coord_uv(nt)
    f = bruit(nt, uv, 3.0, 8.0, 0.65, etirement=etirement)
    c = rampe(nt, f, [(0.3, couleur_b), (0.7, couleur_a)])
    hauteur = f
    if anneaux:
        w = nt.nodes.new("ShaderNodeTexWave")
        w.wave_type = 'BANDS'
        w.bands_direction = 'Y'
        w.inputs["Scale"].default_value = 3.0
        w.inputs["Distortion"].default_value = 1.5
        nt.links.new(uv, w.inputs["Vector"])
        m = nt.nodes.new("ShaderNodeMath"); m.operation = 'MULTIPLY'
        nt.links.new(w.outputs["Fac"], m.inputs[0]); nt.links.new(f, m.inputs[1])
        hauteur = m.outputs[0]
    p = principled(nt, c, 0.9)
    relief(nt, p, hauteur, 0.8, 0.03)
    sortie_avec_brume(nt, p.outputs["BSDF"])


def mat_feuillage(nom, fichier, dossier_tex, translucidite=0.35, teinte_dos="#9fbf4a", cartes=True):
    """Carte de feuillage : texture à fond transparent, éclairée par transparence."""
    mat, nt = nouveau_mat(nom, "#3f6b25")
    chemin = os.path.join(dossier_tex, fichier)
    img = None
    if os.path.isfile(chemin):
        try:
            img = marquer(bpy.data.images.load(chemin, check_existing=False))
            img.name = fichier
            RAPPORT["textures"].append(fichier)
        except Exception as exc:
            erreur("lecture impossible de %s : %s" % (fichier, exc))
    else:
        RAPPORT["manquantes"].append(fichier)
        avertir("texture absente : %s (couleur unie de secours)" % fichier)
    p = principled(nt, "#3f6b25", 0.55)
    entree(p, "Specular IOR Level", 0.35)
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    tr.inputs["Color"].default_value = hex_lin(teinte_dos)
    mixl = nt.nodes.new("ShaderNodeMixShader")
    mixl.inputs[0].default_value = translucidite
    nt.links.new(p.outputs["BSDF"], mixl.inputs[1])
    nt.links.new(tr.outputs["BSDF"], mixl.inputs[2])
    final = mixl.outputs[0]
    if img is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img
        tex.extension = 'CLIP'
        tex.interpolation = 'Linear'
        nt.links.new(coord_uv(nt), tex.inputs["Vector"])
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
        # teinte de transparence : la couleur de la feuille, éclaircie
        dos = nt.nodes.new("ShaderNodeVectorMath"); dos.operation = 'MULTIPLY'
        dos.inputs[1].default_value = (1.6, 1.6, 1.2)
        nt.links.new(tex.outputs["Color"], dos.inputs[0])
        nt.links.new(dos.outputs["Vector"], tr.inputs["Color"])
        if cartes:
            tp = nt.nodes.new("ShaderNodeBsdfTransparent")
            mixa = nt.nodes.new("ShaderNodeMixShader")
            nt.links.new(tex.outputs["Alpha"], mixa.inputs[0])
            nt.links.new(tp.outputs["BSDF"], mixa.inputs[1])
            nt.links.new(mixl.outputs[0], mixa.inputs[2])
            final = mixa.outputs[0]
    sortie_avec_brume(nt, final)
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = 'DITHERED'
    else:
        mat.blend_method = 'HASHED'
    mat.use_backface_culling = False
    return mat


def mat_vitrage(nom, couleur="#1b252c"):
    mat, nt = nouveau_mat(nom, couleur)
    p = principled(nt, couleur, 0.03, 0.0)
    entree(p, "Specular IOR Level", 0.9)
    entree(p, "IOR", 1.52)
    sortie_avec_brume(nt, p.outputs["BSDF"])
    return mat


def mat_ciel_lointain(nom, couleur):
    """Collines et silhouettes de la ville au loin."""
    return mat_uni(nom, couleur, 0.95, grain=0.15, echelle_grain=0.02)


def creer_materiaux(dossier_tex):
    global GROUPE_BRUME
    MATS.clear()
    GROUPE_BRUME = creer_groupe_brume()
    mat_asphalte()
    mat_uni("ENV_Marquage", "#e6e3da", 0.55, grain=0.35, echelle_grain=4.0)
    mat_uni("ENV_Beton", "#b9b4aa", 0.85, grain=0.25, echelle_grain=6.0)
    mat_uni("ENV_Caniveau", "#8f8a80", 0.9, grain=0.3, echelle_grain=5.0)
    mat_pave("ENV_Pave_Trottoir", "#a9a092", "#958b7e", "#6e675f", 0.20, 0.10)
    mat_pave("ENV_Pave_Parvis", "#d6c8ae", "#cbbb9f", "#9a8f7e", 0.60, 0.40, decalage=0.0, rugosite=0.6)
    mat_pave("ENV_Pave_Allee", "#9c8f80", "#8a7d70", "#5e564e", 0.22, 0.11, decalage=0.5)
    mat_gazon()
    mat_gazon("ENV_Gazon_Jardin", sec=0.08)
    mat_uni("ENV_Terre", "#4b3727", 0.95, grain=0.35, echelle_grain=12.0)
    mat_uni("ENV_Terrain", "#4f6330", 0.95, grain=0.3, echelle_grain=0.08)
    mat_enduit("ENV_Enduit_Blanc", "#f1eee8")
    mat_enduit("ENV_Enduit_Creme", "#ece2cf")
    mat_enduit("ENV_Enduit_Gris", "#d8d6d1")
    mat_uni("ENV_Chaperon", "#dcd7cd", 0.75, grain=0.15)
    mat_uni("ENV_Fer_Forge", "#111111", 0.42, metal=0.65)
    mat_uni("ENV_Menuiserie", "#1d1d1e", 0.38, metal=0.5)
    mat_vitrage("ENV_Vitrage")
    mat_uni("ENV_Bois_Claustra", "#7d5130", 0.55, grain=0.3, echelle_grain=3.0)
    mat_uni("ENV_Pierre", "#6f665c", 0.8, grain=0.45, echelle_grain=2.5)
    mat_uni("ENV_Tuile", "#5b5651", 0.7, grain=0.3, echelle_grain=1.5)
    mat_uni("ENV_Soubassement", "#5f5a54", 0.85, grain=0.2)
    mat_uni("ENV_Applique", "#fff0d6", 0.4, emission="#ffc47a", force_em=18.0)
    mat_uni("ENV_Lampadaire", "#6c7075", 0.4, metal=0.85)
    mat_uni("ENV_Plaque", "#f6f4ef", 0.5)
    mat_uni("ENV_Texte_Noir", "#101010", 0.5)
    # Végétation
    mat_ecorce("ENV_Ecorce", "#5d4b3b", "#3a2e24")
    mat_ecorce("ENV_Ecorce_Fromager", "#8f8d7f", "#6d6b5e", etirement=(1.0, 3.0, 1.0))
    mat_ecorce("ENV_Stipe_Palmier", "#8c806d", "#5f564a", etirement=(4.0, 1.0, 1.0), anneaux=True)
    mat_ecorce("ENV_Stipe_Bananier", "#6f7a3a", "#4d5a28", etirement=(1.0, 4.0, 1.0))
    mat_uni("ENV_Gaine_Palmier", "#5f7f34", 0.6, grain=0.2)
    mat_uni("ENV_Noix_Coco", "#6e7a2c", 0.5, grain=0.3)
    mat_feuillage("ENV_Feuillage_Flamboyant", "ENV_Feuillage_Flamboyant.png", dossier_tex)
    mat_feuillage("ENV_Feuillage_Flamboyant_vert", "ENV_Feuillage_Flamboyant_vert.png", dossier_tex)
    mat_feuillage("ENV_Feuillage_Manguier", "ENV_Feuillage_Manguier.png", dossier_tex, 0.25, "#6f9a35")
    mat_feuillage("ENV_Feuillage_Fromager", "ENV_Feuillage_Fromager.png", dossier_tex)
    mat_feuillage("ENV_Feuillage_Tropical", "ENV_Feuillage_Tropical.png", dossier_tex, 0.3)
    mat_feuillage("ENV_Bougainvillier", "ENV_Bougainvillier.png", dossier_tex, 0.3, "#d05aa0")
    mat_feuillage("ENV_Hibiscus", "ENV_Hibiscus.png", dossier_tex, 0.3)
    mat_feuillage("ENV_Palme", "ENV_Palme.png", dossier_tex, 0.4, "#b5c45a")
    mat_feuillage("ENV_Feuille_Bananier", "ENV_Feuille_Bananier.png", dossier_tex, 0.45, "#b9d35a")
    mat_feuillage("ENV_Touffe_Herbe", "ENV_Touffe_Herbe.png", dossier_tex, 0.3)
    haie = mat_feuillage("ENV_Haie", "ENV_Haie_color.jpg", dossier_tex, 0.15, cartes=False)
    haie.use_backface_culling = True
    # Véhicules
    mat_uni("ENV_Peinture_Noire", "#060708", 0.22, metal=0.35, vernis=1.0)
    mat_uni("ENV_Peinture_Blanche", "#e9e9e6", 0.25, metal=0.1, vernis=1.0)
    mat_uni("ENV_Peinture_Argent", "#8e9398", 0.28, metal=0.85, vernis=1.0)
    mat_uni("ENV_Peinture_Bleu_Nuit", "#101b2c", 0.25, metal=0.5, vernis=1.0)
    mat_uni("ENV_Pneu", "#151515", 0.85)
    mat_uni("ENV_Jante", "#b4b7ba", 0.22, metal=1.0)
    mat_vitrage("ENV_Vitre_Auto", "#0b0e11")
    mat_uni("ENV_Plastique_Auto", "#121212", 0.6)
    mat_uni("ENV_Chrome", "#d8d8d8", 0.08, metal=1.0)
    mat_uni("ENV_Phare", "#eef3f7", 0.05, emission="#fff6e8", force_em=0.4)
    mat_uni("ENV_Feu_Arriere", "#7a0a0a", 0.2, emission="#ff1a10", force_em=0.6)
    # Personnage
    mat_uni("ENV_Uniforme", "#1a2333", 0.75, grain=0.2, echelle_grain=20.0)
    mat_uni("ENV_Peau", "#4a2c20", 0.5)
    mat_uni("ENV_Chaussure", "#0c0c0c", 0.35)
    mat_uni("ENV_Insigne", "#d9a520", 0.35, metal=0.8)
    # Lointain
    mat_ciel_lointain("ENV_Collines", "#56704a")
    mat_ciel_lointain("ENV_Ville_Lointaine", "#c9c2b4")
    mat_uni("ENV_Canopee_Lointaine", "#34521f", 0.9, grain=0.45, echelle_grain=0.6)


# =============================================================================
# GÉOMÉTRIE : accumulateur de faces multi-matériaux
# =============================================================================

class Maille:
    def __init__(self):
        self.v, self.f, self.uv, self.m, self.lisse = [], [], [], [], []
        self.noms_mats = []

    def _im(self, mat):
        if mat not in self.noms_mats:
            self.noms_mats.append(mat)
        return self.noms_mats.index(mat)

    def face(self, pts, uvs, mat, lisse=False):
        base = len(self.v)
        self.v += [tuple(p) for p in pts]
        self.f.append(tuple(range(base, base + len(pts))))
        self.uv.append([tuple(u) for u in uvs])
        self.m.append(self._im(mat))
        self.lisse.append(lisse)

    def faces_indexees(self, sommets, faces, uvs, mat, lisse=False):
        """Faces partageant leurs sommets (surfaces lissées : troncs, carrosseries)."""
        base = len(self.v)
        self.v += [tuple(p) for p in sommets]
        im = self._im(mat)
        for f, u in zip(faces, uvs):
            self.f.append(tuple(base + i for i in f))
            self.uv.append([tuple(x) for x in u])
            self.m.append(im)
            self.lisse.append(lisse)

    def quad(self, a, b, c, d, mat, uv=((0, 0), (1, 0), (1, 1), (0, 1)), lisse=False):
        self.face([a, b, c, d], uv, mat, lisse)

    def boite(self, x0, x1, y0, y1, z0, z1, mat, faces="tout"):
        """Pavé aligné sur les axes. UV en mètres (projection par face)."""
        P = [Vector(p) for p in [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                                 (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]]
        F = {"bas": (0, 3, 2, 1), "haut": (4, 5, 6, 7), "avant": (0, 1, 5, 4), "droite": (1, 2, 6, 5),
             "arriere": (2, 3, 7, 6), "gauche": (3, 0, 4, 7)}
        for nom, idx in F.items():
            if faces != "tout" and nom not in faces:
                continue
            pts = [P[i] for i in idx]
            if nom in ("bas", "haut"):
                uvs = [(p.x, p.y) for p in pts]
            elif nom in ("avant", "arriere"):
                uvs = [(p.x, p.z) for p in pts]
            else:
                uvs = [(p.y, p.z) for p in pts]
            self.face(pts, uvs, mat)

    def boite_m(self, mat_transfo, taille, mat):
        """Pavé centré, de taille (dx, dy, dz), transformé par une matrice 4x4."""
        hx, hy, hz = taille[0] / 2, taille[1] / 2, taille[2] / 2
        loc = [Vector(p) for p in [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
                                   (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]]
        P = [mat_transfo @ p for p in loc]
        for idx, (a, b) in zip([(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)],
                               [(0, 1), (0, 1), (0, 2), (1, 2), (0, 2), (1, 2)]):
            uvs = [(loc[i][a], loc[i][b]) for i in idx]
            self.face([P[i] for i in idx], uvs, mat)

    def tube(self, points, rayons, mat, segments=8, bout=True, base=False, ecrasement=1.0):
        """Tube le long d'une polyligne (repères transportés). UV : u autour, v le long, en m."""
        n = len(points)
        if n < 2:
            return
        pts = [Vector(p) for p in points]
        tang = []
        for i in range(n):
            t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)])
            tang.append(t.normalized() if t.length > 1e-9 else Vector((0, 0, 1)))
        ref = Vector((1, 0, 0)) if abs(tang[0].x) < 0.9 else Vector((0, 1, 0))
        nrm = tang[0].cross(ref).normalized()
        sommets, faces, uvs = [], [], []
        v_long = 0.0
        perim = 2 * math.pi * max(rayons[0], 0.01)
        for i in range(n):
            if i > 0:
                nrm = (nrm - tang[i] * nrm.dot(tang[i]))
                nrm = nrm.normalized() if nrm.length > 1e-9 else tang[i].orthogonal().normalized()
                v_long += (pts[i] - pts[i - 1]).length
            bin_ = tang[i].cross(nrm)
            for k in range(segments):
                a = 2 * math.pi * k / segments
                d = nrm * math.cos(a) * ecrasement + bin_ * math.sin(a)
                sommets.append(pts[i] + d * rayons[i])
        for i in range(n - 1):
            for k in range(segments):
                k2 = (k + 1) % segments
                faces.append((i * segments + k, i * segments + k2, (i + 1) * segments + k2, (i + 1) * segments + k))
                l0 = sum((pts[j + 1] - pts[j]).length for j in range(i))
                l1 = l0 + (pts[i + 1] - pts[i]).length
                uvs.append([(perim * k / segments, l0), (perim * (k + 1) / segments, l0),
                            (perim * (k + 1) / segments, l1), (perim * k / segments, l1)])
        if bout:
            faces.append(tuple((n - 1) * segments + k for k in range(segments)))
            uvs.append([(0, 0)] * segments)
        if base:
            faces.append(tuple(reversed(range(segments))))
            uvs.append([(0, 0)] * segments)
        self.faces_indexees(sommets, faces, uvs, mat, lisse=True)
        if bout or base:
            for j in range(1, 1 + int(bout) + int(base)):
                self.lisse[-j] = False

    def cylindre(self, c, r, h, mat, segments=12, axe=(0, 0, 1)):
        c, ax = Vector(c), Vector(axe).normalized()
        self.tube([c, c + ax * h], [r, r], mat, segments, bout=True, base=True)

    def sphere(self, c, r, mat, seg=10, anneaux=6, echelle=(1, 1, 1)):
        c = Vector(c)
        sx, sy, sz = echelle
        sommets = []
        for j in range(anneaux + 1):
            t = math.pi * j / anneaux
            for i in range(seg):
                p = 2 * math.pi * i / seg
                sommets.append(c + Vector((r * sx * math.sin(t) * math.cos(p), r * sy * math.sin(t) * math.sin(p),
                                           r * sz * math.cos(t))))
        faces, uvs = [], []
        for j in range(anneaux):
            for i in range(seg):
                i2 = (i + 1) % seg
                faces.append((j * seg + i, (j + 1) * seg + i, (j + 1) * seg + i2, j * seg + i2))
                uvs.append([(i / seg, j / anneaux), (i / seg, (j + 1) / anneaux),
                            ((i + 1) / seg, (j + 1) / anneaux), ((i + 1) / seg, j / anneaux)])
        self.faces_indexees(sommets, faces, uvs, mat, lisse=True)

    def carte(self, centre, normale, taille, rotation, mat, rapport=1.0, decal_v=0.0):
        """Carte carrée (ou rectangulaire) à texture transparente."""
        n = Vector(normale).normalized()
        u = n.orthogonal().normalized()
        u = Matrix.Rotation(rotation, 3, n) @ u
        v = n.cross(u)
        hu, hv = taille / 2 * rapport, taille / 2
        c = Vector(centre) + v * decal_v * taille
        self.quad(c - u * hu - v * hv, c + u * hu - v * hv, c + u * hu + v * hv, c - u * hu + v * hv, mat)

    def bande(self, axe_pts, laterals, largeurs, mat, pli=0.0):
        """Bande souple (palme, feuille) : 3 sommets en travers (bord, nervure, bord).
        u = abscisse relative le long, v = 0 (gauche) à 1 (droite)."""
        n = len(axe_pts)
        for i in range(n - 1):
            q = []
            for j in (i, i + 1):
                p, lat, w = Vector(axe_pts[j]), Vector(laterals[j]), largeurs[j]
                bas = Vector((0, 0, -pli * w))
                q.append((p - lat * w / 2 + bas, p, p + lat * w / 2 + bas))
            u0, u1 = i / (n - 1), (i + 1) / (n - 1)
            self.quad(q[0][0], q[1][0], q[1][1], q[0][1], mat, ((u0, 0), (u1, 0), (u1, 0.5), (u0, 0.5)))
            self.quad(q[0][1], q[1][1], q[1][2], q[0][2], mat, ((u0, 0.5), (u1, 0.5), (u1, 1), (u0, 1)))

    def extrusion_profil(self, profils, ys, mat):
        """Loft de profils (x, z) de même nombre de points, placés aux y donnés ;
        couvercles aux deux bouts. Sert aux carrosseries."""
        npts = len(profils[0])
        sommets = []
        for prof, y in zip(profils, ys):
            sommets += [Vector((x, y, z)) for x, z in prof]
        faces, uvs = [], []
        for s in range(len(profils) - 1):
            for i in range(npts):
                i2 = (i + 1) % npts
                a, b = s * npts + i, s * npts + i2
                faces.append((a, b, b + npts, a + npts))
                uvs.append([(sommets[k].x, sommets[k].z) for k in (a, b, b + npts, a + npts)])
        faces.append(tuple(range(npts))[::-1])
        uvs.append([(p[0], p[1]) for p in profils[0]][::-1])
        dern = (len(profils) - 1) * npts
        faces.append(tuple(range(dern, dern + npts)))
        uvs.append([(p[0], p[1]) for p in profils[-1]])
        self.faces_indexees(sommets, faces, uvs, mat, lisse=False)

    def vers_maillage(self, nom):
        me = marquer(bpy.data.meshes.new(nom))
        me.from_pydata(self.v, [], self.f)
        if self.f:
            uv = me.uv_layers.new(name="UVMap")
            plat = [c for face_uv in self.uv for u in face_uv for c in u]
            uv.data.foreach_set("uv", plat)
            me.polygons.foreach_set("material_index", self.m)
            me.polygons.foreach_set("use_smooth", self.lisse)
        for nom_mat in self.noms_mats:
            mat = MATS.get(nom_mat)
            if mat is None:
                erreur("matériau inconnu : " + nom_mat)
                mat = MATS["ENV_Beton"]
            me.materials.append(mat)
        me.validate(clean_customdata=False)
        me.update()
        RAPPORT["faces"] += len(self.f)
        return me


COLLS = {}


def objet(nom, donnees, coll, loc=(0, 0, 0), rot_z=0.0, echelle=1.0, ombre=True):
    if isinstance(donnees, Maille):
        donnees = donnees.vers_maillage(nom)
    ob = marquer(bpy.data.objects.new(nom, donnees))
    COLLS[coll].objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (0.0, 0.0, rot_z)
    if echelle != 1.0:
        ob.scale = (echelle, echelle, echelle)
    if not ombre and hasattr(ob, "visible_shadow"):
        ob.visible_shadow = False
    RAPPORT["objets"] += 1
    return ob


def instance(nom, maillage, coll, loc, rot_z=0.0, echelle=1.0):
    ob = objet(nom, maillage, coll, loc, rot_z, echelle)
    RAPPORT["instances"] += 1
    return ob


# =============================================================================
# VÉGÉTATION
# =============================================================================

def bezier(a, b, c, n):
    a, b, c = Vector(a), Vector(b), Vector(c)
    return [a * (1 - t) ** 2 + b * 2 * t * (1 - t) + c * t * t for t in (i / (n - 1) for i in range(n))]


def direction_aleatoire(rg, biais_haut=0.6):
    v = Vector((rg.gauss(0, 1), rg.gauss(0, 1), rg.gauss(0, 1) + biais_haut))
    return v.normalized() if v.length > 1e-6 else Vector((0, 0, 1))


def regrouper(rg, points, centre, n):
    """Répartit des points en n secteurs autour d'un centre (azimut)."""
    groupes = [[] for _ in range(n)]
    phase = rg.uniform(0, 2 * math.pi)
    for p in points:
        a = math.atan2(p.y - centre.y, p.x - centre.x)
        groupes[int(((a - phase) % (2 * math.pi)) / (2 * math.pi) * n) % n].append(p)
    return [g for g in groupes if g]


def moyenne(pts):
    s = Vector((0, 0, 0))
    for p in pts:
        s += p
    return s / max(len(pts), 1)


def ramure(m, rg, depart, points, n_branches, r_depart, ecorce, n_sous=3, montee=0.25):
    """Charpentières du tronc vers les secteurs du houppier, puis branches vers
    des sous-secteurs. Les extrémités atteignent le feuillage."""
    for g in regrouper(rg, points, depart, n_branches):
        cg = moyenne(g)
        cible = depart.lerp(cg, 0.72)
        ctrl = depart.lerp(cible, 0.5) + Vector((0, 0, (cible - depart).length * montee))
        chemin = bezier(depart, ctrl, cible, 6)
        r0, r1 = r_depart, r_depart * 0.45
        m.tube(chemin, [r0 + (r1 - r0) * i / 5 for i in range(6)], ecorce, 7)
        for sg in regrouper(rg, g, cible, n_sous):
            c2 = cible.lerp(moyenne(sg), 0.85)
            ctrl2 = cible.lerp(c2, 0.5) + Vector((0, 0, (c2 - cible).length * 0.15))
            m.tube(bezier(cible, ctrl2, c2, 4), [r1 * 0.8, r1 * 0.55, r1 * 0.35, r1 * 0.2], ecorce, 5)


def cartes_feuillage(m, rg, points, taille, mat, par_point=1, biais=0.7, dispersion=0.4):
    for p in points:
        for _ in range(par_point):
            c = p + Vector((rg.gauss(0, dispersion), rg.gauss(0, dispersion), rg.gauss(0, dispersion * 0.6)))
            m.carte(c, direction_aleatoire(rg, biais), taille * rg.uniform(0.75, 1.25),
                    rg.uniform(0, 2 * math.pi), mat)


def tronc(m, rg, hauteur, r_base, r_haut, ecorce, inclinaison=0.06, n=8, contreforts=0):
    az = rg.uniform(0, 2 * math.pi)
    dx, dy = math.cos(az) * inclinaison, math.sin(az) * inclinaison
    pts, rs = [], []
    for i in range(n):
        t = i / (n - 1)
        pts.append(Vector((dx * hauteur * t * t + rg.gauss(0, 0.03), dy * hauteur * t * t + rg.gauss(0, 0.03),
                           -0.3 + (hauteur + 0.3) * t)))
        evase = 1.0 + 0.45 * max(0.0, 1 - t * 6)
        rs.append((r_base + (r_haut - r_base) * t) * evase)
    m.tube(pts, rs, ecorce, 10)
    for k in range(contreforts):
        a = az + k * 2 * math.pi / contreforts + rg.uniform(-0.3, 0.3)
        d = Vector((math.cos(a), math.sin(a), 0))
        lat = Vector((-d.y, d.x, 0)) * 0.09
        ext = r_base + rg.uniform(1.6, 2.6)
        hz = rg.uniform(2.2, 3.4)
        b0, b1, b2 = d * r_base * 0.6, d * ext, d * r_base * 0.6 + Vector((0, 0, hz))
        base = Vector((0, 0, -0.25))
        for s in (-1, 1):
            m.face([b0 + base + lat * s, b1 + base + lat * s * 0.3, b2 + lat * s * 0.4], [(0, 0), (1, 0), (0, 1)], ecorce)
        m.quad(b1 + base - lat * 0.3, b1 + base + lat * 0.3, b2 + lat * 0.4, b2 - lat * 0.4, ecorce)
    return pts[-1]


def arbre_flamboyant(graine, fleuri=True):
    """Flamboyant : tronc court, charpentières très ouvertes, houppier en parasol."""
    rg = random.Random(graine)
    m = Maille()
    R = rg.uniform(6.5, 8.0)
    z0 = rg.uniform(7.0, 8.2)
    sommet = tronc(m, rg, rg.uniform(2.6, 3.4), 0.42, 0.3, "ENV_Ecorce", 0.08)
    pts = []
    for _ in range(int(R * R * 9)):
        r = R * math.sqrt(rg.random())
        z = z0 + 1.6 * (1 - (r / R) ** 2) + rg.uniform(-0.7, 0.6) * (0.5 + 0.5 * (1 - r / R))
        a = rg.uniform(0, 2 * math.pi)
        pts.append(Vector((r * math.cos(a) + sommet.x, r * math.sin(a) + sommet.y, z - 0.5 * (r / R) ** 3)))
    ramure(m, rg, sommet, pts, rg.randint(4, 6), 0.27, "ENV_Ecorce", 3, montee=0.05)
    mat = "ENV_Feuillage_Flamboyant" if fleuri else "ENV_Feuillage_Flamboyant_vert"
    cartes_feuillage(m, rg, pts, 1.7, mat, 1, 1.4, 0.35)
    return m


def arbre_manguier(graine):
    """Manguier : dôme dense et sombre."""
    rg = random.Random(graine)
    m = Maille()
    R, Rz = rg.uniform(4.2, 5.4), rg.uniform(3.6, 4.6)
    sommet = tronc(m, rg, rg.uniform(1.8, 2.4), 0.38, 0.3, "ENV_Ecorce", 0.05)
    zc = sommet.z + Rz * 0.95
    pts = []
    for _ in range(int(R * R * 44)):
        d = Vector((rg.gauss(0, 1), rg.gauss(0, 1), rg.gauss(0, 1))).normalized()
        k = 0.6 + 0.4 * rg.random() ** 0.5
        p = Vector((d.x * R * k, d.y * R * k, d.z * Rz * k))
        if p.z < -Rz * 0.55:
            p.z = -Rz * 0.55 + rg.uniform(0, 0.3)
        pts.append(p + Vector((sommet.x, sommet.y, zc)))
    ramure(m, rg, sommet, [p for p in pts if p.z > zc - Rz * 0.2], rg.randint(4, 5), 0.25,
           "ENV_Ecorce", 3, montee=0.35)
    cartes_feuillage(m, rg, pts, 1.0, "ENV_Feuillage_Manguier", 1, 0.5, 0.25)
    return m


def arbre_fromager(graine):
    """Fromager (kapokier) : très haut fût gris à contreforts, branches en étages."""
    rg = random.Random(graine)
    m = Maille()
    H = rg.uniform(19.0, 24.0)
    sommet = tronc(m, rg, H, 0.85, 0.32, "ENV_Ecorce_Fromager", 0.02, n=10, contreforts=5)
    pts_tous = []
    for etage, (fz, lg, nb) in enumerate([(0.62, 7.5, 5), (0.8, 6.5, 4), (1.0, 5.0, 4)]):
        z = H * fz
        for k in range(nb):
            a = rg.uniform(0, 2 * math.pi) if k == 0 else a + 2 * math.pi / nb + rg.uniform(-0.3, 0.3)
            L = lg * rg.uniform(0.8, 1.15)
            d = Vector((math.cos(a), math.sin(a), 0.12))
            dep = Vector((sommet.x * fz, sommet.y * fz, z))
            fin = dep + d * L
            m.tube(bezier(dep, dep + d * L * 0.5 + Vector((0, 0, 0.4)), fin, 5),
                   [0.22 - 0.04 * etage, 0.16, 0.12, 0.09, 0.06], "ENV_Ecorce_Fromager", 6)
            for _ in range(int(L * 26)):
                t = rg.uniform(0.35, 1.05)
                p = dep + d * L * t + Vector((rg.gauss(0, 1.6), rg.gauss(0, 1.6), rg.uniform(0.2, 1.6)))
                pts_tous.append(p)
    cartes_feuillage(m, rg, pts_tous, 1.25, "ENV_Feuillage_Fromager", 1, 1.0, 0.4)
    return m


def palmier(graine, royal=False):
    """Cocotier (stipe incliné, noix) ou palmier royal (stipe droit, gaine verte)."""
    rg = random.Random(graine)
    m = Maille()
    H = rg.uniform(12.0, 16.0) if royal else rg.uniform(9.0, 13.5)
    incl = rg.uniform(0.0, 0.04) if royal else rg.uniform(0.08, 0.2)
    az = rg.uniform(0, 2 * math.pi)
    pts, rs = [], []
    for i in range(12):
        t = i / 11
        courbe = incl * H * (t ** 1.6)
        pts.append(Vector((math.cos(az) * courbe, math.sin(az) * courbe, -0.3 + (H + 0.3) * t)))
        r = (0.26 if royal else 0.2) - (0.05 if royal else 0.06) * t
        if royal:
            r += 0.06 * math.sin(math.pi * min(1.0, t * 1.4))       # renflement du palmier royal
        rs.append(r * (1.25 if i == 0 else 1.0))
    m.tube(pts, rs, "ENV_Stipe_Palmier", 10)
    haut = pts[-1]
    if royal:
        m.tube([haut, haut + Vector((0, 0, 1.8))], [rs[-1] * 1.05, rs[-1] * 0.85], "ENV_Gaine_Palmier", 10)
        haut = haut + Vector((0, 0, 1.8))
    else:
        for k in range(rg.randint(6, 12)):
            a = rg.uniform(0, 2 * math.pi)
            m.sphere(haut + Vector((math.cos(a) * 0.28, math.sin(a) * 0.28, rg.uniform(-0.7, -0.2))),
                     0.14, "ENV_Noix_Coco", 8, 5)
    n = rg.randint(15, 20)
    for k in range(n):
        a = k * 2.39996 + rg.uniform(-0.15, 0.15)
        age = k / n
        tangage = math.radians(55 - 75 * age + rg.uniform(-8, 8))
        L = rg.uniform(4.0, 5.2) * (0.75 if age < 0.15 else 1.0)
        d = Vector((math.cos(a) * math.cos(tangage), math.sin(a) * math.cos(tangage), math.sin(tangage)))
        lat = Vector((-math.sin(a), math.cos(a), 0))
        axe, lats, largs = [], [], []
        p = Vector(haut)
        seg = 9
        for i in range(seg + 1):
            t = i / seg
            axe.append(p.copy())
            torsion = Matrix.Rotation(rg.uniform(-0.05, 0.05) + 0.25 * t * (1 if k % 2 else -1), 3, d)
            lats.append(torsion @ lat)
            largs.append(1.75 * (0.6 + 0.4 * math.sin(math.pi * min(1.0, 0.2 + t))))
            p = p + d * (L / seg)
            d = (d + Vector((0, 0, -0.11 - 0.1 * t))).normalized()
        m.bande(axe, lats, largs, "ENV_Palme", pli=0.12)
    return m


def bananier(graine):
    rg = random.Random(graine)
    m = Maille()
    for s in range(rg.randint(2, 4)):
        base = Vector((rg.uniform(-0.6, 0.6), rg.uniform(-0.6, 0.6), -0.1))
        h = rg.uniform(1.8, 3.4)
        m.tube([base, base + Vector((rg.gauss(0, 0.08), rg.gauss(0, 0.08), h))], [0.13, 0.09],
               "ENV_Stipe_Bananier", 8)
        haut = base + Vector((0, 0, h))
        for k in range(rg.randint(5, 8)):
            a = rg.uniform(0, 2 * math.pi)
            tang = math.radians(rg.uniform(35, 70))
            d = Vector((math.cos(a) * math.cos(tang), math.sin(a) * math.cos(tang), math.sin(tang)))
            lat = Vector((-math.sin(a), math.cos(a), 0))
            axe, lats, largs = [], [], []
            p = haut.copy()
            L = rg.uniform(1.6, 2.4)
            for i in range(7):
                axe.append(p.copy()); lats.append(lat); largs.append(0.62)
                p = p + d * (L / 6)
                d = (d + Vector((0, 0, -0.16))).normalized()
            # la texture est verticale : on échange u et v en construisant la bande à plat
            n = len(axe)
            for i in range(n - 1):
                q = []
                for j in (i, i + 1):
                    w = largs[j] / 2
                    q.append((axe[j] - lats[j] * w + Vector((0, 0, -0.06)), axe[j], axe[j] + lats[j] * w + Vector((0, 0, -0.06))))
                v0, v1 = i / (n - 1), (i + 1) / (n - 1)
                m.quad(q[0][0], q[0][1], q[1][1], q[1][0], "ENV_Feuille_Bananier", ((0, v0), (0.5, v0), (0.5, v1), (0, v1)))
                m.quad(q[0][1], q[0][2], q[1][2], q[1][1], "ENV_Feuille_Bananier", ((0.5, v0), (1, v0), (1, v1), (0.5, v1)))
    return m


def buisson(graine, mat, rayon=0.9, hauteur=1.4, taille_carte=0.75, densite=40):
    rg = random.Random(graine)
    m = Maille()
    pts = []
    for _ in range(int(densite * rayon * rayon * hauteur)):
        d = Vector((rg.gauss(0, 1), rg.gauss(0, 1), rg.gauss(0, 1))).normalized()
        k = rg.random() ** 0.4
        pts.append(Vector((d.x * rayon * k, d.y * rayon * k, hauteur * 0.5 + d.z * hauteur * 0.5 * k)))
    cartes_feuillage(m, rg, pts, taille_carte, mat, 1, 0.4, 0.12)
    return m


def cascade_bougainvillier(graine, longueur=3.0, hauteur_mur=2.6, chute=1.6):
    """Bougainvillier débordant d'un mur : sur le chaperon et en cascade côté rue (y < 0)."""
    rg = random.Random(graine)
    m = Maille()
    pts = []
    for _ in range(int(longueur * 55)):
        x = rg.uniform(0, longueur)
        t = rg.random() ** 1.5
        fin = 0.5 + 0.5 * math.sin(math.pi * x / longueur)
        z = hauteur_mur + 0.5 - t * chute * fin * 1.3
        y = -0.25 - rg.uniform(0, 0.35) * (1 - t * 0.5) if z < hauteur_mur else rg.uniform(-0.4, 1.0)
        pts.append(Vector((x, y, z)))
    for p in pts:
        n = Vector((rg.gauss(0, 0.5), -1.0, rg.gauss(0, 0.5) + (0.8 if p.z > hauteur_mur else 0)))
        m.carte(p, n, rg.uniform(0.55, 0.85), rg.uniform(0, 2 * math.pi), "ENV_Bougainvillier")
    return m


def touffes_herbe(rg, m, x0, x1, y0, y1, z, densite):
    for _ in range(int((x1 - x0) * (y1 - y0) * densite)):
        c = Vector((rg.uniform(x0, x1), rg.uniform(y0, y1), z))
        a = rg.uniform(0, math.pi)
        lg, h = rg.uniform(0.35, 0.6), rg.uniform(0.15, 0.3)
        for da in (0.0, math.pi / 2):
            d = Vector((math.cos(a + da), math.sin(a + da), 0)) * lg / 2
            m.quad(c - d, c + d, c + d + Vector((0, 0, h)), c - d + Vector((0, 0, h)), "ENV_Touffe_Herbe")


# =============================================================================
# VOIRIE ET TROTTOIRS
# =============================================================================

def construire_voirie(rg, coupures_n, coupures_s):
    """coupures : intervalles x des entrées charretières (bordure abaissée, accotement pavé)."""
    xa, xb = X_AVENUE
    m = Maille()
    # chaussée et caniveaux
    m.boite(xa, xb, Y_ROUTE[0], Y_ROUTE[1], Z_ROUTE - 0.2, Z_ROUTE, "ENV_Asphalte", faces=("haut",))
    for y0, y1 in ((Y_ROUTE[0], Y_ROUTE[0] + 0.35), (Y_ROUTE[1] - 0.35, Y_ROUTE[1])):
        m.boite(xa, xb, y0, y1, Z_ROUTE - 0.1, Z_ROUTE + 0.004, "ENV_Caniveau", faces=("haut",))
    objet("ENV_Chaussee", m, "ENV_Voirie")

    # marquage : axe discontinu (3 m / 3 m) et lignes de rive continues
    mk = Maille()
    zc = Z_ROUTE + 0.006
    yc = (Y_ROUTE[0] + Y_ROUTE[1]) / 2
    x = xa
    while x < xb:
        mk.quad((x, yc - 0.06, zc), (x + 3.0, yc - 0.06, zc), (x + 3.0, yc + 0.06, zc), (x, yc + 0.06, zc),
                "ENV_Marquage", ((x, 0), (x + 3, 0), (x + 3, 0.12), (x, 0.12)))
        x += 6.0
    for yr in (Y_ROUTE[0] + 0.55, Y_ROUTE[1] - 0.55):
        mk.quad((xa, yr - 0.06, zc), (xb, yr - 0.06, zc), (xb, yr + 0.06, zc), (xa, yr + 0.06, zc),
                "ENV_Marquage", ((xa, 0), (xb, 0), (xb, 0.12), (xa, 0.12)))
    objet("ENV_Marquage_sol", mk, "ENV_Voirie", ombre=False)

    # trottoirs, bordures, accotements, bandes plantées, des deux côtés
    for cote, coupures in (("N", coupures_n), ("S", coupures_s)):
        Yb = Y_BORDURE_N if cote == "N" else Y_BORDURE_S
        Ya = Y_ACCOTEMENT_N if cote == "N" else Y_ACCOTEMENT_S
        Yt = Y_TROTTOIR_N if cote == "N" else Y_TROTTOIR_S
        Yp = Y_PLANTATION_N if cote == "N" else Y_PLANTATION_S
        mt = Maille()
        mt.boite(xa, xb, Yt[0], Yt[1], Z_SOL - 0.1, Z_TROTTOIR, "ENV_Pave_Trottoir", faces=("haut", "avant", "arriere"))
        mt.boite(xa, xb, Yp[0], Yp[1], Z_SOL - 0.1, Z_PLANTATION, "ENV_Terre", faces=("haut",))
        # bordures et accotements : segments entre les entrées charretières
        bornes = sorted(coupures)
        segments_pleins, x = [], xa
        for c0, c1 in bornes:
            if c0 > x:
                segments_pleins.append((x, c0))
            x = max(x, c1)
        if x < xb:
            segments_pleins.append((x, xb))
        for s0, s1 in segments_pleins:
            mt.boite(s0, s1, Yb[0], Yb[1], Z_ROUTE - 0.1, Z_TROTTOIR, "ENV_Beton", faces=("haut", "avant", "arriere"))
            mt.boite(s0, s1, Ya[0], Ya[1], Z_SOL - 0.1, Z_ACCOTEMENT, "ENV_Gazon")
        for c0, c1 in bornes:
            # bateau : bordure abaissée et accotement pavé, en pente douce
            mt.boite(c0, c1, Yb[0], Yb[1], Z_ROUTE - 0.1, Z_ROUTE + 0.03, "ENV_Beton", faces=("haut", "avant", "arriere"))
            y_route, y_trot = (Ya[0], Ya[1]) if cote == "N" else (Ya[1], Ya[0])
            zr, zt = Z_ROUTE + 0.03, Z_TROTTOIR
            mt.quad((c0, y_route, zr), (c1, y_route, zr), (c1, y_trot, zt), (c0, y_trot, zt), "ENV_Pave_Allee",
                    ((c0, y_route), (c1, y_route), (c1, y_trot), (c0, y_trot)))
            if cote == "S":
                mt.f[-1] = mt.f[-1][::-1]
                mt.uv[-1] = mt.uv[-1][::-1]
            # la bande plantée est aussi pavée devant l'entrée
            mt.boite(c0, c1, Yp[0], Yp[1], Z_SOL - 0.1, Z_TROTTOIR, "ENV_Pave_Allee", faces=("haut",))
        objet("ENV_Trottoir_" + cote, mt, "ENV_Voirie")

    # terrain naturel (sous tout le reste) et collines au loin
    mg = Maille()
    mg.boite(-3000, 3000, -2500, 2500, Z_SOL - 0.3, Z_SOL - 0.005, "ENV_Terrain", faces=("haut",))
    objet("ENV_Terrain", mg, "ENV_Voirie")


def segments_libres(xa, xb, coupures, marge=1.0):
    """Intervalles de [xa, xb] hors des coupures (avec marge)."""
    libres, x = [], xa
    for c0, c1 in sorted(coupures):
        if c0 - marge > x:
            libres.append((x, c0 - marge))
        x = max(x, c1 + marge)
    if x < xb:
        libres.append((x, xb))
    return libres


# =============================================================================
# VILLAS (repère local : rue du côté y < 0, mur de façade sur y = 0..0,20,
# parcelle x = 0..L, y = 0..P)
# =============================================================================

def portail(rg, largeur, hauteur, style):
    """Portail battant à deux vantaux en fer forgé noir (repère local du mur)."""
    m = Maille()
    f = "ENV_Fer_Forge"
    e = 0.06
    for vantail in (0, 1):
        x0 = vantail * largeur / 2 + 0.01
        x1 = x0 + largeur / 2 - 0.02
        y0, y1 = 0.07, 0.13
        m.boite(x0, x1, y0, y1, 0.04, 0.04 + e, f)                        # traverse basse
        m.boite(x0, x1, y0, y1, hauteur - e, hauteur, f)                  # traverse haute
        m.boite(x0, x1, y0, y1, 1.0, 1.0 + e * 0.8, f)                    # traverse intermédiaire
        m.boite(x0, x0 + e, y0, y1, 0.04, hauteur, f)
        m.boite(x1 - e, x1, y0, y1, 0.04, hauteur, f)
        if style == "plein":
            m.boite(x0 + e, x1 - e, 0.09, 0.11, 0.1, 1.0, f)              # soubassement plein
        else:
            nb = int((x1 - x0) / 0.12)
            for k in range(1, nb):
                xx = x0 + k * (x1 - x0) / nb
                m.boite(xx - 0.012, xx + 0.012, 0.088, 0.112, 0.1, 1.0, f)
        nb = int((x1 - x0) / 0.11)
        for k in range(1, nb):
            xx = x0 + k * (x1 - x0) / nb
            m.boite(xx - 0.011, xx + 0.011, 0.089, 0.111, 1.0, hauteur + 0.12, f)
            pointe = Vector((xx, 0.1, hauteur + 0.2))
            m.face([Vector((xx - 0.03, 0.1, hauteur + 0.12)), Vector((xx + 0.03, 0.1, hauteur + 0.12)), pointe],
                   [(0, 0), (1, 0), (0.5, 1)], f)
        # volutes : anneaux le long de la traverse haute
        nv = max(2, int((x1 - x0) / 0.45))
        for k in range(nv):
            cx = x0 + (k + 0.5) * (x1 - x0) / nv
            cz = hauteur - 0.32
            pts = [Vector((cx + 0.15 * math.cos(2 * math.pi * i / 12), 0.1, cz + 0.15 * math.sin(2 * math.pi * i / 12)))
                   for i in range(13)]
            m.tube(pts, [0.012] * 13, f, 4, bout=False)
            m.tube([Vector((cx, 0.1, cz - 0.15)), Vector((cx, 0.1, 1.0))], [0.01, 0.01], f, 4, bout=False)
    # poignée
    m.boite(largeur / 2 - 0.12, largeur / 2 - 0.08, 0.02, 0.07, 1.15, 1.35, "ENV_Chrome")
    return m


def mur_cloture(m, x0, x1, hauteur, ouvertures, rg, mat_mur, grille=False, piliers_tous=3.6):
    """Mur de clôture sur y = 0..0,20, de x0 à x1 (repère local), avec piliers et chaperon.
    Renvoie la liste des piliers (x)."""
    pleins = segments_libres(x0, x1, ouvertures, marge=0.0)
    piliers = []
    for s0, s1 in pleins:
        if s1 - s0 < 0.05:
            continue
        m.boite(s0, s1, 0.0, 0.2, Z_PLANTATION, hauteur, mat_mur)
        m.boite(s0 - 0.03, s1 + 0.03, -0.05, 0.25, hauteur, hauteur + 0.06, "ENV_Chaperon")
        m.boite(s0, s1, -0.01, 0.21, Z_PLANTATION, Z_PLANTATION + 0.25, "ENV_Soubassement",
                faces=("avant", "arriere"))
        n = max(1, int(round((s1 - s0) / piliers_tous)))
        for k in range(n + 1):
            piliers.append(s0 + (s1 - s0) * k / n)
        if grille:
            hg = 0.75
            m.boite(s0, s1, 0.08, 0.12, hauteur + 0.06 + hg - 0.04, hauteur + 0.06 + hg, "ENV_Fer_Forge")
            xx = s0 + 0.06
            while xx < s1 - 0.03:
                m.boite(xx - 0.01, xx + 0.01, 0.09, 0.11, hauteur + 0.06, hauteur + 0.06 + hg + 0.1, "ENV_Fer_Forge")
                xx += 0.13
    for px in piliers:
        m.boite(px - 0.25, px + 0.25, -0.08, 0.28, Z_PLANTATION, hauteur + 0.25, mat_mur)
        m.boite(px - 0.3, px + 0.3, -0.13, 0.33, hauteur + 0.25, hauteur + 0.33, "ENV_Chaperon")
    return piliers


def applique(m, x, y_face, z):
    """Applique murale lumineuse (côté rue, face vers -y)."""
    m.boite(x - 0.07, x + 0.07, y_face - 0.09, y_face, z - 0.13, z + 0.13, "ENV_Menuiserie")
    m.boite(x - 0.05, x + 0.05, y_face - 0.1, y_face - 0.085, z - 0.1, z + 0.08, "ENV_Applique")


def fenetre(m, x0, x1, z0, z1, y_face, cote="avant", claustra=False):
    """Baie vitrée posée sur une façade : vitrage sombre, cadre noir, meneaux.
    cote : 'avant' (face -y), 'gauche' (face -x) ou 'droite' (face +x)."""
    def b(a0, a1, b0, b1, c0, c1, mat):
        if cote == "avant":
            m.boite(a0, a1, y_face - b1, y_face - b0, c0, c1, mat)
        elif cote == "gauche":
            m.boite(y_face - b1, y_face - b0, a0, a1, c0, c1, mat)
        else:
            m.boite(y_face + b0, y_face + b1, a0, a1, c0, c1, mat)
    e = 0.05
    b(x0, x1, 0.0, 0.03, z0, z1, "ENV_Vitrage")
    b(x0 - e, x1 + e, 0.0, 0.06, z0 - e, z0, "ENV_Menuiserie")
    b(x0 - e, x1 + e, 0.0, 0.06, z1, z1 + e, "ENV_Menuiserie")
    b(x0 - e, x0, 0.0, 0.06, z0, z1, "ENV_Menuiserie")
    b(x1, x1 + e, 0.0, 0.06, z0, z1, "ENV_Menuiserie")
    nb = max(1, int(round((x1 - x0) / 1.3)))
    for k in range(1, nb):
        xm = x0 + (x1 - x0) * k / nb
        b(xm - 0.025, xm + 0.025, 0.0, 0.05, z0, z1, "ENV_Menuiserie")
    if claustra:
        xx = x0 + 0.06
        while xx < x1 - 0.03:
            b(xx - 0.025, xx + 0.025, 0.06, 0.16, z0, z1, "ENV_Bois_Claustra")
            xx += 0.14


def maison(m, rg, x0, x1, y0, y1, mat_enduit):
    """Villa contemporaine : rez-de-chaussée, étage décalé, dalles débordantes,
    baies vitrées, claustras bois, bande de pierre. Une sur trois a un toit à 4 pans."""
    z_sol = 0.30
    h1, h2 = 3.3, 3.2
    l, p = x1 - x0, y1 - y0
    m.boite(x0 - 0.3, x1 + 0.3, y0 - 1.2, y1, Z_JARDIN, z_sol, "ENV_Pierre")       # socle + terrasse
    m.boite(x0, x1, y0, y1, z_sol, z_sol + h1, mat_enduit)
    # étage : décalé et en porte-à-faux sur une partie
    dx = rg.choice((-1, 1)) * rg.uniform(0.8, 2.2)
    e0, e1 = x0 + max(0.0, dx) + rg.uniform(0, 1.2), x1 + min(0.0, dx) - rg.uniform(0, 1.2)
    deb = rg.uniform(0.7, 1.2)
    ey0 = max(y0 - rg.uniform(0.6, 1.6), y0 - deb + 0.1)
    z2 = z_sol + h1 + 0.3
    m.boite(e0, e1, ey0, y1 - rg.uniform(0, 2.0), z2, z2 + h2, mat_enduit)
    # dalles débordantes (signature des villas contemporaines)
    m.boite(x0 - deb, x1 + deb, y0 - deb - 0.3, y1 + deb * 0.5, z_sol + h1, z2, mat_enduit)
    toit_4_pans = rg.random() < 0.33
    if toit_4_pans:
        zt = z2 + h2
        c0, c1, d0, d1 = e0 - 0.8, e1 + 0.8, ey0 - 0.8, y1 + 0.4
        m.boite(c0, c1, d0, d1, zt, zt + 0.2, mat_enduit)
        hz = min(c1 - c0, d1 - d0) * 0.22
        mx = ((c0 + c1) / 2, (d0 + d1) / 2)
        faitage = 0.5 * max(0.0, (c1 - c0) - (d1 - d0))
        a = Vector((mx[0] - faitage / 2, mx[1], zt + 0.2 + hz))
        b = Vector((mx[0] + faitage / 2, mx[1], zt + 0.2 + hz))
        z = zt + 0.2
        A, B, C, D = Vector((c0, d0, z)), Vector((c1, d0, z)), Vector((c1, d1, z)), Vector((c0, d1, z))
        m.quad(A, B, b, a, "ENV_Tuile", ((c0, 0), (c1, 0), (b.x, 3), (a.x, 3)))
        m.quad(C, D, a, b, "ENV_Tuile", ((c1, 0), (c0, 0), (a.x, 3), (b.x, 3)))
        m.face([B, C, b], [(0, 0), (3, 0), (1.5, 3)], "ENV_Tuile")
        m.face([D, A, a], [(0, 0), (3, 0), (1.5, 3)], "ENV_Tuile")
    else:
        m.boite(e0 - deb, e1 + deb, ey0 - deb, y1 + deb * 0.4, z2 + h2, z2 + h2 + 0.35, mat_enduit)
        m.boite(e0 + 0.5, e0 + 3.0, y1 - 3.5, y1 - 1.0, z2 + h2 + 0.35, z2 + h2 + 1.6, mat_enduit)  # cage d'escalier
    # baies : rez-de-chaussée (grandes), étage (avec ou sans claustra)
    nb1 = rg.randint(2, 3)
    larg = (l - 1.2) / nb1
    for k in range(nb1):
        a0 = x0 + 0.6 + k * larg + 0.2
        fenetre(m, a0, a0 + larg - 0.4, z_sol + 0.05, z_sol + h1 - 0.35, y0)
    claus = rg.random() < 0.6
    m.boite(e0 + 0.3, e0 + 1.1, ey0 - 0.04, ey0, z2, z2 + h2, "ENV_Pierre")         # bande de pierre
    fenetre(m, e0 + 1.6, e1 - 0.6, z2 + 0.4, z2 + h2 - 0.4, ey0, claustra=claus)
    # garde-corps vitré sur la terrasse avant
    m.boite(x0 + 0.2, x1 - 0.2, y0 - deb - 0.25, y0 - deb - 0.2, z2, z2 + 1.0, "ENV_Vitrage")
    # fenêtres latérales (visibles en enfilade le long de l'avenue)
    for cote, xf in (("gauche", x0), ("droite", x1)):
        for k in range(max(1, int(p / 4.5))):
            b0 = y0 + 1.0 + k * 4.5
            if b0 + 2.0 < y1 - 0.5:
                fenetre(m, b0, b0 + 2.0, z_sol + 0.9, z_sol + h1 - 0.5, xf, cote=cote)
    for cote, xf in (("gauche", e0), ("droite", e1)):
        fenetre(m, ey0 + 1.2, ey0 + 3.2, z2 + 0.8, z2 + h2 - 0.5, xf, cote=cote)
    return z_sol


def villa(rg, nom, L, P, gauche_mur=True, dossier_vegetation=None):
    """Construit une villa (repère local) : renvoie les mailles et la liste des
    plantations (type, x, y, rot, échelle) en repère local."""
    mur, portes, bati = Maille(), Maille(), Maille()
    mat_enduit = rg.choice(["ENV_Enduit_Blanc", "ENV_Enduit_Blanc", "ENV_Enduit_Creme", "ENV_Enduit_Gris"])
    hm = rg.uniform(2.4, 2.9)
    gx = rg.uniform(2.5, max(3.0, L - 9.0))
    gl = rg.choice((4.0, 4.5, 5.0))
    px = gx + gl + 0.5
    ouvertures = [(gx, gx + gl), (px, px + 1.0)]
    piliers = mur_cloture(mur, 0.0, L, hm, ouvertures, rg, "ENV_Enduit_Blanc", grille=rg.random() < 0.35)
    for x in (gx, gx + gl, px, px + 1.0):
        mur.boite(x - 0.25, x + 0.25, -0.08, 0.28, Z_PLANTATION, hm + 0.35, "ENV_Enduit_Blanc")
        mur.boite(x - 0.3, x + 0.3, -0.13, 0.33, hm + 0.35, hm + 0.43, "ENV_Chaperon")
    applique(mur, gx - 0.25, -0.08, hm - 0.35)
    applique(mur, gx + gl + 0.25, -0.08, hm - 0.35)
    applique(mur, px + 1.25, -0.08, hm - 0.35)
    # murs latéraux et de fond
    if gauche_mur:
        mur.boite(0.0, 0.2, 0.2, P, Z_SOL, hm, "ENV_Enduit_Blanc")
        mur.boite(-0.03, 0.23, 0.2, P, hm, hm + 0.06, "ENV_Chaperon")
    mur.boite(0.0, L, P - 0.2, P, Z_SOL, hm, "ENV_Enduit_Blanc", faces=("avant", "haut"))
    # portail et portillon
    style = rg.choice(("ajoure", "plein", "ajoure"))
    g = portail(rg, gl, hm - 0.05, style)
    pt = portail(rg, 1.0, hm - 0.3, style)
    # jardin : pelouse et allée
    hx0, hx1 = rg.uniform(2.0, 4.0), L - rg.uniform(2.0, 4.0)
    hy0 = rg.uniform(6.5, 8.5)
    hy1 = min(P - 4.0, hy0 + rg.uniform(10.0, 14.0))
    bati.boite(0.2, L, 0.2, P - 0.2, Z_SOL, Z_JARDIN, "ENV_Gazon_Jardin", faces=("haut",))
    bati.boite(gx, gx + gl, 0.2, hy0 - 1.2, Z_SOL, Z_JARDIN + 0.01, "ENV_Pave_Allee", faces=("haut",))
    maison(bati, rg, hx0, hx1, hy0, hy1, mat_enduit)
    # plantations du jardin
    plant = []
    for _ in range(rg.randint(1, 3)):
        x = rg.choice((rg.uniform(1.0, max(1.2, gx - 1.0)), rg.uniform(min(L - 1.2, px + 2.0), L - 1.0)))
        plant.append(("palmier_royal" if rg.random() < 0.4 else "cocotier", x, rg.uniform(1.5, 4.5)))
    for _ in range(rg.randint(1, 2)):
        x = rg.uniform(1.0, L - 1.0)
        if not (gx - 1.0 < x < px + 2.0):
            plant.append(("bananier", x, rg.uniform(1.2, 3.0)))
    if rg.random() < 0.45:
        plant.append((rg.choice(("manguier", "flamboyant")), rg.uniform(3.0, L - 3.0), rg.uniform(hy1 + 1.0, P - 2.0)))
    # buissons derrière le mur (dépassent au-dessus)
    xb = 1.0
    while xb < L - 1.0:
        if not (gx - 0.8 < xb < px + 1.8):
            plant.append(("hibiscus_haut", xb, 0.9))
        xb += rg.uniform(1.6, 3.0)
    # bougainvillier en cascade sur un ou deux pans de mur
    for s0, s1 in segments_libres(0.4, L - 0.4, ouvertures, marge=0.6):
        if s1 - s0 > 2.5 and rg.random() < 0.6:
                plant.append(("bougainvillier", rg.uniform(s0, s1 - 2.5), 0.0))
    return mur, portes, bati, g, pt, (gx, gl, px), plant, hm, piliers


# =============================================================================
# VÉHICULES ET PERSONNAGE
# =============================================================================

def profil_voiture(L, H, garde, capot, coffre, suv, retrait=0.0):
    """Profil latéral (x, z) de la caisse basse avec passages de roue. x = 0 au centre,
    avant vers +x. retrait : profil rentré (chanfrein des côtés)."""
    r_roue = (0.40 if suv else 0.33) + 0.05 + retrait
    e_av, e_ar = L / 2 - (0.95 if suv else 0.9), -L / 2 + (1.0 if suv else 0.95)
    zb = garde + retrait
    zc = (0.40 if suv else 0.33)
    belt = H - retrait
    pts = []
    # dessous : de l'arrière vers l'avant
    pts.append((-L / 2 + 0.12 + retrait, zb + 0.08))
    pts.append((e_ar - r_roue - 0.02, zb))
    for i in range(9):
        a = math.pi - math.pi * i / 8
        pts.append((e_ar + r_roue * math.cos(a), zc + r_roue * math.sin(a)))
    pts.append((e_ar + r_roue + 0.02, zb))
    pts.append((e_av - r_roue - 0.02, zb))
    for i in range(9):
        a = math.pi - math.pi * i / 8
        pts.append((e_av + r_roue * math.cos(a), zc + r_roue * math.sin(a)))
    pts.append((e_av + r_roue + 0.02, zb))
    pts.append((L / 2 - 0.1 - retrait, zb + 0.1))
    # face avant, capot, pare-brise (base), ligne de caisse, arrière
    pts.append((L / 2 - retrait, zb + 0.3))
    pts.append((L / 2 - 0.05 - retrait, capot - 0.12 - retrait))
    pts.append((L / 2 - 0.3 - retrait, capot - retrait))
    pts.append((L / 2 - 1.2, capot + 0.04 - retrait))
    pts.append((-L / 2 + 0.25 + retrait, coffre - retrait))
    pts.append((-L / 2 + 0.02 + retrait, coffre - 0.12 - retrait))
    pts.append((-L / 2 + retrait, zb + 0.3))
    return pts[::-1]          # sens trigonométrique vu depuis -y


def voiture(graine, peinture, suv=True):
    rg = random.Random(graine)
    m = Maille()
    L, W = (4.95, 2.0) if suv else (4.85, 1.85)
    garde = 0.42 if suv else 0.32
    capot = 1.08 if suv else 0.86
    coffre = 1.1 if suv else 0.92
    toit = 1.80 if suv else 1.44
    ch = 0.07
    profils = [profil_voiture(L, toit, garde, capot, coffre, suv, ch), profil_voiture(L, toit, garde, capot, coffre, suv),
               profil_voiture(L, toit, garde, capot, coffre, suv), profil_voiture(L, toit, garde, capot, coffre, suv, ch)]
    m.extrusion_profil(profils, [-W / 2, -W / 2 + ch, W / 2 - ch, W / 2], peinture)
    # habitacle vitré (léger rentré) et toit
    xa = L / 2 - 1.2                 # base du pare-brise
    xr = -L / 2 + (0.25 if suv else 0.45)
    zb = capot + 0.02
    pente_av = 0.75 if suv else 0.95
    pente_ar = 0.15 if suv else 0.65
    def vitre(rentre):
        return [(xr + rentre, coffre - 0.02), (xa - rentre * 0.5, zb), (xa - pente_av, toit - 0.06 - rentre * 0.4),
                (xr + pente_ar + rentre * 0.3, toit - 0.06 - rentre * 0.4)]
    wv = W / 2 - 0.1
    m.extrusion_profil([vitre(0.06), vitre(0.0), vitre(0.0), vitre(0.06)], [-wv, -wv + 0.08, wv - 0.08, wv],
                       "ENV_Vitre_Auto")
    m.boite(xr + pente_ar + 0.05, xa - pente_av - 0.02, -wv + 0.06, wv - 0.06, toit - 0.07, toit, peinture)
    # montants (B), rétroviseurs, calandre, feux, plaques, poignées
    xb = (xa - pente_av + xr + pente_ar) / 2 + 0.1
    for s in (-1, 1):
        y = s * (wv + 0.005)
        m.boite(xb - 0.05, xb + 0.05, min(y, y - s * 0.02), max(y, y - s * 0.02), zb, toit - 0.06, "ENV_Plastique_Auto")
        m.boite(xa - 0.1, xa + 0.05, s * (W / 2 + 0.12) - 0.05, s * (W / 2 + 0.12) + 0.05, zb + 0.05, zb + 0.18, peinture)
        for xp in (xb + 0.35, xb - 0.6):
            m.boite(xp - 0.12, xp + 0.12, s * (W / 2 + 0.005) - 0.01, s * (W / 2 + 0.005) + 0.01,
                    capot - 0.12, capot - 0.09, "ENV_Chrome")
    zf = garde + 0.42
    m.boite(L / 2 - 0.02, L / 2 + 0.01, -0.5, 0.5, zf - 0.12, zf + 0.12, "ENV_Plastique_Auto")
    for s in (-1, 1):
        m.boite(L / 2 - 0.06, L / 2 - 0.005, s * 0.78 - 0.17, s * 0.78 + 0.17, zf + 0.1, zf + 0.2, "ENV_Phare")
        m.boite(-L / 2 + 0.005, -L / 2 + 0.06, s * 0.75 - 0.2, s * 0.75 + 0.2, coffre - 0.3, coffre - 0.18, "ENV_Feu_Arriere")
    m.boite(L / 2 - 0.01, L / 2 + 0.015, -0.26, 0.26, garde + 0.12, garde + 0.24, "ENV_Plaque")
    m.boite(-L / 2 - 0.015, -L / 2 + 0.01, -0.26, 0.26, garde + 0.32, garde + 0.44, "ENV_Plaque")
    # roues
    r = 0.40 if suv else 0.33
    for xw in (L / 2 - (0.95 if suv else 0.9), -L / 2 + (1.0 if suv else 0.95)):
        for s in (-1, 1):
            y0 = s * (W / 2 - 0.27)
            m.cylindre((xw, y0, r), r, 0.25, "ENV_Pneu", 20, axe=(0, s, 0))
            m.cylindre((xw, s * (W / 2 - 0.015), r), r * 0.62, 0.012, "ENV_Jante", 16, axe=(0, s, 0))
    return m


def gardien(graine):
    """Agent de sécurité debout (uniforme bleu nuit, casquette), face vers -y."""
    rg = random.Random(graine)
    m = Maille()
    U, P = "ENV_Uniforme", "ENV_Peau"
    for s in (-1, 1):
        x = s * 0.1
        m.boite(x - 0.06, x + 0.06, -0.14, 0.06, 0.0, 0.09, "ENV_Chaussure")              # rangers
        m.tube([(x, -0.02, 0.08), (x, -0.01, 0.5), (x, 0.0, 0.92)], [0.065, 0.07, 0.085], U, 8)
        # bras le long du corps, mains devant
        m.tube([(s * 0.23, 0.0, 1.42), (s * 0.26, -0.02, 1.15), (s * 0.2, -0.1, 0.95)], [0.055, 0.05, 0.045], U, 7)
        m.sphere((s * 0.18, -0.13, 0.92), 0.05, P, 8, 5)
    m.tube([(0, 0.0, 0.9), (0, 0.0, 1.1), (0, 0.0, 1.35), (0, 0.0, 1.47)], [0.17, 0.165, 0.2, 0.17], U, 12,
           ecrasement=0.7)
    m.boite(-0.17, 0.17, -0.13, 0.13, 0.9, 0.95, "ENV_Chaussure")                        # ceinturon
    m.boite(0.08, 0.13, -0.135, -0.12, 1.3, 1.36, "ENV_Insigne")
    m.tube([(0, 0, 1.47), (0, 0, 1.56)], [0.05, 0.05], P, 8)
    m.sphere((0, -0.01, 1.66), 0.105, P, 12, 8, echelle=(0.9, 1.0, 1.15))
    m.tube([(0, 0.0, 1.73), (0, 0.0, 1.8)], [0.11, 0.105], U, 12)                       # casquette
    m.boite(-0.08, 0.08, -0.2, -0.08, 1.735, 1.75, U)                                    # visière
    return m


# =============================================================================
# MOBILIER URBAIN, LOINTAIN
# =============================================================================

def lampadaire():
    m = Maille()
    m.cylindre((0, 0, -0.2), 0.11, 0.7, "ENV_Lampadaire", 10)
    m.tube([(0, 0, -0.2), (0, 0, 7.6), (0, -0.4, 8.2), (0, -1.6, 8.35)], [0.08, 0.06, 0.05, 0.045],
           "ENV_Lampadaire", 8, bout=True)
    m.boite(-0.15, 0.15, -2.2, -1.5, 8.25, 8.4, "ENV_Lampadaire")
    m.boite(-0.12, 0.12, -2.15, -1.55, 8.24, 8.25, "ENV_Chaperon")
    return m


def toit_4_pans(m, c0, c1, d0, d1, z, mat, pente=0.22):
    hz = min(c1 - c0, d1 - d0) * pente
    mx, my = (c0 + c1) / 2, (d0 + d1) / 2
    fa = 0.5 * max(0.0, (c1 - c0) - (d1 - d0))
    a, b = Vector((mx - fa / 2, my, z + hz)), Vector((mx + fa / 2, my, z + hz))
    A, B, C, D = Vector((c0, d0, z)), Vector((c1, d0, z)), Vector((c1, d1, z)), Vector((c0, d1, z))
    m.quad(A, B, b, a, mat, ((c0, 0), (c1, 0), (b.x, 3), (a.x, 3)))
    m.quad(C, D, a, b, mat, ((c1, 0), (c0, 0), (a.x, 3), (b.x, 3)))
    m.face([B, C, b], [(0, 0), (3, 0), (1.5, 3)], mat)
    m.face([D, A, a], [(0, 0), (3, 0), (1.5, 3)], mat)


def arriere_plan(rg, mod):
    """Quartier en arrière des villas de l'avenue : maisons simplifiées et
    jardins arborés, pour la profondeur des vues (Cocody est très vert)."""
    enduits = ["ENV_Enduit_Blanc", "ENV_Enduit_Blanc", "ENV_Enduit_Creme", "ENV_Enduit_Gris"]
    n_arbres = 0
    for cote, (ya, yb) in (("N", (Y_LIMITE_N + 40.0, 175.0)), ("S", (-175.0, Y_LIMITE_S - 40.0))):
        m = Maille()
        y = ya
        while y < yb:
            pas_y = rg.uniform(30.0, 38.0)
            x = -470.0 + rg.uniform(0, 10)
            while x < 470.0:
                pas_x = rg.uniform(24.0, 34.0)
                lx, ly = rg.uniform(10.0, 16.0), rg.uniform(9.0, 13.0)
                cx, cy = x + pas_x / 2 + rg.uniform(-3, 3), y + pas_y / 2 + rg.uniform(-3, 3)
                h = rg.choice((3.6, 7.0, 7.0, 7.4))
                mat = rg.choice(enduits)
                m.boite(cx - lx / 2, cx + lx / 2, cy - ly / 2, cy + ly / 2, Z_SOL, h, mat)
                if rg.random() < 0.45:
                    toit_4_pans(m, cx - lx / 2 - 0.7, cx + lx / 2 + 0.7, cy - ly / 2 - 0.7, cy + ly / 2 + 0.7,
                                h, "ENV_Tuile")
                else:
                    d = rg.uniform(0.6, 1.1)
                    m.boite(cx - lx / 2 - d, cx + lx / 2 + d, cy - ly / 2 - d, cy + ly / 2 + d, h, h + 0.3, mat)
                # mur de clôture côté rue intérieure
                m.boite(x, x + pas_x - 0.5, y, y + 0.2, Z_SOL, 2.5, "ENV_Enduit_Blanc", faces=("avant", "arriere", "haut"))
                for _ in range(rg.randint(1, 3)):
                    for essai in range(6):
                        tx, ty = rg.uniform(x + 2, x + pas_x - 2), rg.uniform(y + 2, y + pas_y - 2)
                        if abs(tx - cx) > lx / 2 + 2.5 or abs(ty - cy) > ly / 2 + 2.5:
                            break
                    esp = rg.choice(("manguier", "manguier", "flamboyant", "flamboyant_vert", "cocotier",
                                     "palmier_royal", "cocotier", "fromager" if rg.random() < 0.15 else "manguier"))
                    n_arbres += 1
                    planter(mod, rg, esp, "ENV_Quartier_%s_%04d" % (cote, n_arbres), (tx, ty, Z_JARDIN))
                x += pas_x
            y += pas_y
        objet("ENV_Quartier_" + cote, m, "ENV_Lointain")
    log("%d arbres dans l'arrière-quartier" % n_arbres)


def lointain(rg):
    """Collines et silhouettes d'immeubles, noyées dans la brume."""
    m = Maille()
    n = 96
    r0, r1 = 1600.0, 2400.0
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        h0 = 35 + 55 * (0.5 + 0.5 * math.sin(a0 * 3 + 1.3)) * (0.6 + 0.4 * math.sin(a0 * 7))
        h1 = 35 + 55 * (0.5 + 0.5 * math.sin(a1 * 3 + 1.3)) * (0.6 + 0.4 * math.sin(a1 * 7))
        A = Vector((r0 * math.cos(a0), r0 * math.sin(a0), Z_SOL - 1))
        B = Vector((r0 * math.cos(a1), r0 * math.sin(a1), Z_SOL - 1))
        C = Vector((r1 * math.cos(a1), r1 * math.sin(a1), h1))
        D = Vector((r1 * math.cos(a0), r1 * math.sin(a0), h0))
        m.quad(A, B, C, D, "ENV_Collines", ((a0 * 300, 0), (a1 * 300, 0), (a1 * 300, 600), (a0 * 300, 600)))
    objet("ENV_Collines", m, "ENV_Lointain", ombre=False)
    # canopée et toits lointains, entre l'arrière-quartier et les collines
    c, t = Maille(), Maille()
    for k in range(5200):
        a = rg.uniform(0, 2 * math.pi)
        r = 180.0 + (1450.0 - 180.0) * rg.random() ** 0.8
        x, y = r * math.cos(a), r * math.sin(a)
        if abs(y) < 180.0 and abs(x) < 480.0:
            continue
        if rg.random() < 0.22:
            w, d, h = rg.uniform(10, 16), rg.uniform(9, 13), rg.choice((3.6, 7.0))
            t.boite(x - w / 2, x + w / 2, y - d / 2, y + d / 2, Z_SOL, h, rg.choice(("ENV_Enduit_Blanc", "ENV_Enduit_Creme")),
                    faces=("haut", "avant", "arriere", "gauche", "droite"))
        else:
            rr = rg.uniform(4.0, 8.0)
            c.sphere((x, y, rr * 0.8), rr, "ENV_Canopee_Lointaine", 7, 4, echelle=(1, 1, rg.uniform(0.7, 1.0)))
    objet("ENV_Canopee_lointaine", c, "ENV_Lointain", ombre=False)
    objet("ENV_Toits_lointains", t, "ENV_Lointain", ombre=False)
    v = Maille()
    for k in range(40):
        a = math.radians(rg.uniform(160, 200))
        r = rg.uniform(1100, 1500)
        cx, cy = r * math.cos(a), r * math.sin(a)
        w, d, h = rg.uniform(15, 35), rg.uniform(15, 35), rg.uniform(20, 95)
        v.boite(cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, Z_SOL, h, "ENV_Ville_Lointaine")
    objet("ENV_Ville_lointaine", v, "ENV_Lointain", ombre=False)


# =============================================================================
# PARCELLE DU MAGASIN
# =============================================================================

def z_parvis(y):
    """Pente douce du parvis : du pied de façade (y = 0) vers le trottoir (y = -7)."""
    t = min(1.0, max(0.0, -y / -Y_LIMITE_N))
    return Z_PARVIS_FACADE + (Z_TROTTOIR - Z_PARVIS_FACADE) * t


def construire_parcelle_magasin(rg, modeles):
    x0, x1, y0, y1 = PARCELLE_MAGASIN
    m = Maille()
    # parvis pavé en pente (façade -> trottoir), cour et allée de service à niveau
    for xa, xb in ((x0, 0.0), (0.0, 24.0), (24.0, x1)):
        A, B = Vector((xa, Y_LIMITE_N, z_parvis(Y_LIMITE_N))), Vector((xb, Y_LIMITE_N, z_parvis(Y_LIMITE_N)))
        C, D = Vector((xb, 0.0, z_parvis(0.0))), Vector((xa, 0.0, z_parvis(0.0)))
        m.quad(A, B, C, D, "ENV_Pave_Parvis", ((xa, A.y), (xb, B.y), (xb, 0), (xa, 0)))
    m.boite(x0, 0.0, 0.0, y1, Z_SOL, Z_PARVIS_FACADE, "ENV_Pave_Allee", faces=("haut",))
    m.boite(24.0, x1, 0.0, y1, Z_SOL, Z_PARVIS_FACADE, "ENV_Gazon_Jardin", faces=("haut",))
    m.boite(0.0, 24.0, 16.0, y1, Z_SOL, Z_PARVIS_FACADE, "ENV_Pave_Allee", faces=("haut",))
    # soubassement du magasin (côtés et arrière, hors porte de livraison)
    zb = Z_PARVIS_FACADE
    m.boite(-0.03, 0.0, 0.0, 16.03, zb, 0.25, "ENV_Soubassement", faces=("gauche",))
    m.boite(24.0, 24.03, 0.0, 16.03, zb, 0.25, "ENV_Soubassement", faces=("droite",))
    for a, b in ((-0.03, 3.0), (4.2, 24.03)):
        m.boite(a, b, 16.0, 16.03, zb, 0.25, "ENV_Soubassement", faces=("arriere",))
    # marquage des places de parking (9 places de 2,50 m)
    for k in range(10):
        x = 0.75 + k * 2.5
        ya, yb = -6.5, -1.9
        za, zb2 = z_parvis(ya) + 0.004, z_parvis(yb) + 0.004
        m.quad((x - 0.05, ya, za), (x + 0.05, ya, za), (x + 0.05, yb, zb2), (x - 0.05, yb, zb2), "ENV_Marquage")
    zl = z_parvis(-1.9) + 0.004
    m.quad((0.7, -1.95, zl), (23.3, -1.95, zl), (23.3, -1.85, zl), (0.7, -1.85, zl), "ENV_Marquage")
    # murs de clôture : côtés (bas devant, hauts derrière), fond, mur à droite de la façade
    hm = 2.6
    for xm in (x0, x1 - 0.2):
        m.boite(xm, xm + 0.2, Y_LIMITE_N, 0.0, Z_TROTTOIR, 0.9, "ENV_Enduit_Blanc")
        m.boite(xm - 0.03, xm + 0.23, Y_LIMITE_N, 0.0, 0.9, 0.96, "ENV_Chaperon")
        m.boite(xm, xm + 0.2, 0.0, y1, Z_SOL, hm, "ENV_Enduit_Blanc")
        m.boite(xm - 0.03, xm + 0.23, 0.0, y1, hm, hm + 0.06, "ENV_Chaperon")
    m.boite(x0, x1, y1 - 0.2, y1, Z_SOL, hm, "ENV_Enduit_Blanc")
    m.boite(x0, x1, y1 - 0.23, y1 + 0.03, hm, hm + 0.06, "ENV_Chaperon")
    m.boite(24.0, x1 - 0.2, -0.2, 0.0, Z_PARVIS_FACADE, hm, "ENV_Enduit_Blanc")
    m.boite(24.0, x1 - 0.2, -0.23, 0.03, hm, hm + 0.06, "ENV_Chaperon")
    # grande jardinière basse avec palmiers devant le mur de droite
    ja, jb, jc, jd = 25.0, x1 - 1.0, -6.4, -0.8
    m.boite(ja, jb, jc, jd, z_parvis(jc), 0.40, "ENV_Enduit_Blanc")
    m.boite(ja + 0.15, jb - 0.15, jc + 0.15, jd - 0.15, 0.40, 0.42, "ENV_Terre", faces=("haut",))
    for a0, a1, b0, b1 in ((ja, jb, jc, jc + 0.15), (ja, jb, jd - 0.15, jd),
                           (ja, ja + 0.15, jc + 0.15, jd - 0.15), (jb - 0.15, jb, jc + 0.15, jd - 0.15)):
        m.boite(a0, a1, b0, b1, 0.40, 0.52, "ENV_Enduit_Blanc")
    objet("ENV_Parcelle_magasin", m, "ENV_Parcelle_magasin")
    # portail de l'allée de service (coulissant, à l'alignement de la façade)
    g = portail(rg, 3.8, 2.4, "plein")
    objet("ENV_Portail_service_magasin", g, "ENV_Portails", loc=(x0 + 0.2, -0.1, Z_PARVIS_FACADE))
    plant = [("palmier_royal", 26.2, -2.4), ("palmier_royal", 31.0, -4.6), ("palmier_royal", 35.6, -2.2),
             ("bananier_bas", 28.4, -1.8), ("tropical", 33.2, -5.3), ("tropical", 26.0, -5.4),
             ("hibiscus", 29.4, -5.0), ("hibiscus", 33.6, -1.6), ("tropical", 36.2, -5.4),
             ("cocotier", 27.0, 3.0), ("bananier", 30.5, 2.6), ("cocotier", 35.5, 4.5),
             ("manguier", 31.0, 10.5), ("bananier", 36.0, 15.0), ("flamboyant", 12.0, 19.0)]
    # bougainvillier en cascade sur le mur du jardin (côté parvis)
    plant.append(("bougainvillier", 27.5, -0.2))
    plant.append(("bougainvillier", 32.0, -0.2))
    return plant


# =============================================================================
# CIEL, SOLEIL, CAMÉRAS, RENDU
# =============================================================================

def vecteur_soleil():
    el, az = math.radians(SOLEIL_ELEVATION_DEG), math.radians(SOLEIL_AZIMUT_DEG)
    return Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))


def construire_ciel():
    scene = bpy.context.scene
    w = marquer(bpy.data.worlds.new("ENV_Ciel_Cocody"))
    scene.world = w
    if w.node_tree is None:
        w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    n, l = nt.nodes, nt.links

    def ciel(disque):
        s = n.new("ShaderNodeTexSky")
        for t in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA"):
            try:
                s.sky_type = t
                break
            except TypeError:
                continue
        s.sun_elevation = math.radians(SOLEIL_ELEVATION_DEG)
        s.sun_rotation = math.radians(90.0 - SOLEIL_AZIMUT_DEG)       # 0 = soleil vers +Y
        s.sun_disc = disque
        s.sun_size = math.radians(0.9)
        s.sun_intensity = 0.35
        s.altitude = 50.0
        try:
            s.air_density = 1.0
            s.aerosol_density = 1.2
        except AttributeError:
            s.dust_density = 1.2
        return s

    ciel_cam, ciel_lum = ciel(True), ciel(False)
    # Nuages : bruit projeté sur un plafond nuageux (direction / z)
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Generated"], sep.inputs[0])
    zc = n.new("ShaderNodeMath"); zc.operation = 'MAXIMUM'; zc.inputs[1].default_value = 0.035
    l.new(sep.outputs["Z"], zc.inputs[0])
    comb = n.new("ShaderNodeCombineXYZ")
    for axe in ("X", "Y"):
        d = n.new("ShaderNodeMath"); d.operation = 'DIVIDE'
        l.new(sep.outputs[axe], d.inputs[0]); l.new(zc.outputs[0], d.inputs[1])
        l.new(d.outputs[0], comb.inputs[axe])
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.8
    nz.inputs["Detail"].default_value = 12.0
    nz.inputs["Roughness"].default_value = 0.58
    nz.inputs["Distortion"].default_value = 0.35
    l.new(comb.outputs[0], nz.inputs["Vector"])
    seuil = 0.62 - 0.14 * CIEL_NUAGES
    masque = n.new("ShaderNodeMapRange")
    masque.inputs["From Min"].default_value = seuil
    masque.inputs["From Max"].default_value = seuil + 0.12
    l.new(nz.outputs["Fac"], masque.inputs["Value"])
    # moins de nuages juste au-dessus de l'horizon (perspective)
    fade = n.new("ShaderNodeMapRange")
    fade.inputs["From Min"].default_value = 0.03
    fade.inputs["From Max"].default_value = 0.2
    l.new(sep.outputs["Z"], fade.inputs["Value"])
    mm = n.new("ShaderNodeMath"); mm.operation = 'MULTIPLY'
    l.new(masque.outputs["Result"], mm.inputs[0]); l.new(fade.outputs["Result"], mm.inputs[1])
    # couleur des nuages : dorée côté soleil, rosée/grise à l'opposé
    s = vecteur_soleil()
    dot = n.new("ShaderNodeVectorMath"); dot.operation = 'DOT_PRODUCT'
    dot.inputs[1].default_value = (s.x, s.y, s.z)
    l.new(tc.outputs["Generated"], dot.inputs[0])
    fr = n.new("ShaderNodeMapRange")
    fr.inputs["From Min"].default_value = -0.4
    fr.inputs["From Max"].default_value = 1.0
    l.new(dot.outputs["Value"], fr.inputs["Value"])
    coul = n.new("ShaderNodeValToRGB")
    el = coul.color_ramp.elements
    el[0].position, el[0].color = 0.0, (0.40, 0.40, 0.44, 1.0)
    el[1].position, el[1].color = 0.75, (0.58, 0.52, 0.44, 1.0)
    e3 = el.new(1.0); e3.color = (1.0, 0.69, 0.38, 1.0)
    l.new(fr.outputs["Result"], coul.inputs["Fac"])
    # densité : dessous plus sombre au cœur des nuages
    coeur = n.new("ShaderNodeMapRange")
    coeur.inputs["From Min"].default_value = seuil + 0.05
    coeur.inputs["From Max"].default_value = seuil + 0.3
    coeur.inputs["To Min"].default_value = 1.0
    coeur.inputs["To Max"].default_value = 0.82
    l.new(nz.outputs["Fac"], coeur.inputs["Value"])
    ombre = n.new("ShaderNodeVectorMath"); ombre.operation = 'SCALE'
    l.new(coul.outputs["Color"], ombre.inputs[0])
    l.new(coeur.outputs["Result"], ombre.inputs["Scale"])
    # luminosité des nuages (à régler avec le ciel)
    lum_ciel = n.new("ShaderNodeVectorMath"); lum_ciel.operation = 'SCALE'
    lum_ciel.name = lum_ciel.label = "Luminosite nuages"
    l.new(ombre.outputs["Vector"], lum_ciel.inputs[0])
    lum_ciel.inputs["Scale"].default_value = LUMINOSITE_NUAGES

    def melange(ciel_noeud):
        return melange_rgb(nt, ciel_noeud.outputs["Color"], lum_ciel.outputs["Vector"], mm.outputs[0], 'MIX')

    bg_cam, bg_lum = n.new("ShaderNodeBackground"), n.new("ShaderNodeBackground")
    l.new(melange(ciel_cam), bg_cam.inputs["Color"])
    l.new(melange(ciel_lum), bg_lum.inputs["Color"])
    for b in (bg_cam, bg_lum):
        b.inputs["Strength"].default_value = CIEL_PUISSANCE
    lp = n.new("ShaderNodeLightPath")
    mix = n.new("ShaderNodeMixShader")
    l.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    l.new(bg_lum.outputs[0], mix.inputs[1])
    l.new(bg_cam.outputs[0], mix.inputs[2])
    out = n.new("ShaderNodeOutputWorld")
    l.new(mix.outputs[0], out.inputs["Surface"])

    # soleil
    sol = marquer(bpy.data.lights.new("ENV_Soleil", 'SUN'))
    sol.energy = SOLEIL_PUISSANCE
    sol.angle = math.radians(SOLEIL_ANGLE_DEG)
    if hasattr(sol, "use_temperature"):
        sol.use_temperature = True
        sol.temperature = SOLEIL_TEMPERATURE_K
    else:
        sol.color = (1.0, 0.78, 0.55)
    ob = objet("ENV_Soleil", sol, "ENV_Lumieres")
    ob.rotation_euler = (-vecteur_soleil()).to_track_quat('-Z', 'Y').to_euler()
    ob.location = (0, 0, 60)


def camera(nom, pos, cible, focale, ouverture=None, distance=None):
    d = marquer(bpy.data.cameras.new(nom))
    d.lens = focale
    d.clip_start = 0.05
    d.clip_end = 5000.0
    d.sensor_width = 36.0
    if ouverture:
        d.dof.use_dof = True
        d.dof.aperture_fstop = ouverture
        d.dof.focus_distance = distance or (Vector(cible) - Vector(pos)).length
    ob = objet(nom, d, "ENV_Cameras")
    ob.location = pos
    ob.rotation_euler = (Vector(cible) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    return ob


def vitrage_realiste():
    """Verre clair : transparent + reflet de Fresnel. La lumière traverse dans les
    deux sens (intérieur éclairé visible, lumière du magasin sur le parvis)."""
    mat = bpy.data.materials.get("MAT_Verre_Clair")
    if mat is None or mat.node_tree is None:
        avertir("MAT_Verre_Clair introuvable : vitrines laissées telles quelles")
        return
    nt = mat.node_tree
    nt.nodes.clear()
    fr = nt.nodes.new("ShaderNodeFresnel"); fr.inputs["IOR"].default_value = 1.52
    tp = nt.nodes.new("ShaderNodeBsdfTransparent")
    tp.inputs["Color"].default_value = (0.93, 0.96, 0.95, 1.0)      # léger vert du verre
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.01
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(fr.outputs["Fac"], mix.inputs[0])
    nt.links.new(tp.outputs["BSDF"], mix.inputs[1])
    nt.links.new(gl.outputs["BSDF"], mix.inputs[2])
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = 'BLENDED'
    mat[TAG_ENV + "_vitrage"] = True
    log("vitrines : verre clair")


def construire_cameras():
    cams = {
        # Vue de référence : depuis la chaussée, le long de l'avenue, magasin à droite.
        "CAM_Avenue_Cocody": ((40.0, -16.6, 1.6), (-35.0, -6.0, 3.5), 24.0, 8.0, 34.0),
        # Façade du magasin, depuis le trottoir d'en face.
        "CAM_Facade_Boutique": ((12.0, -23.6, 1.7), (12.0, 0.0, 2.4), 30.0, None, None),
        # Trois-quarts, depuis la chaussée.
        "CAM_Trois_Quarts": ((-14.0, -17.5, 1.7), (14.0, -1.0, 2.6), 22.0, None, None),
        # Vue aérienne (drone).
        "CAM_Drone": ((-34.0, -52.0, 26.0), (14.0, 4.0, 0.0), 26.0, None, None),
        # Entrée : le parvis et l'intérieur éclairé à travers la porte vitrée.
        "CAM_Parvis_Entree": ((19.6, -6.4, 1.6), (11.5, 1.5, 1.7), 22.0, None, None),
    }
    scene = bpy.context.scene
    for nom, (p, c, f, fst, dist) in cams.items():
        ob = camera(nom, p, c, f, fst, dist)
        if nom == CAMERA_ACTIVE:
            scene.camera = ob


def regler_rendu():
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.resolution_percentage = 100
    try:
        sc.render.engine = MOTEUR
    except TypeError:
        avertir("moteur %s indisponible" % MOTEUR)
    vs = sc.view_settings
    try:
        vs.view_transform = 'AgX'
        for look in ("AgX - Medium High Contrast", "AgX - Base Contrast", "Medium High Contrast"):
            try:
                vs.look = look
                break
            except TypeError:
                continue
    except TypeError:
        pass
    vs.exposure = EXPOSITION
    reglages = [
        ("cycles", dict(samples=ECHANTILLONS_CYCLES, use_denoising=True, max_bounces=8, diffuse_bounces=4,
                        glossy_bounces=4, transmission_bounces=8, transparent_max_bounces=64,
                        use_adaptive_sampling=True, adaptive_threshold=0.02, caustics_reflective=False,
                        caustics_refractive=False, blur_glossy=1.0)),
        ("eevee", dict(use_raytracing=True, use_shadows=True, shadow_ray_count=2, shadow_step_count=8,
                       taa_render_samples=128, use_fast_gi=True)),
    ]
    for attr, valeurs in reglages:
        groupe = getattr(sc, attr, None)
        if groupe is None:
            continue
        for cle, val in valeurs.items():
            try:
                setattr(groupe, cle, val)
            except (AttributeError, TypeError):
                pass


# =============================================================================
# CONSTRUCTION DU DÉCOR
# =============================================================================

def construire_modeles():
    """Modèles de végétation et d'objets répétés (données partagées par les instances)."""
    rg = random.Random(GRAINE)
    mod = {}

    def ajout(cle, maille_fonc, n):
        mod[cle] = [maille_fonc(rg.randint(0, 10 ** 6)).vers_maillage("ENV_Modele_%s_%d" % (cle, i))
                    for i in range(n)]

    ajout("flamboyant", lambda g: arbre_flamboyant(g, True), 3)
    ajout("flamboyant_vert", lambda g: arbre_flamboyant(g, False), 1)
    ajout("manguier", arbre_manguier, 2)
    ajout("fromager", arbre_fromager, 2)
    ajout("cocotier", lambda g: palmier(g, False), 3)
    ajout("palmier_royal", lambda g: palmier(g, True), 2)
    ajout("bananier", bananier, 3)
    ajout("hibiscus", lambda g: buisson(g, "ENV_Hibiscus", 0.9, 1.5), 3)
    ajout("hibiscus_haut", lambda g: buisson(g, "ENV_Hibiscus", 1.0, 3.3, 0.85, 26), 3)
    ajout("tropical", lambda g: buisson(g, "ENV_Feuillage_Tropical", 0.8, 1.1, 0.7), 2)
    ajout("bougainvillier", cascade_bougainvillier, 3)
    mod["bananier_bas"] = mod["bananier"]
    mod["lampadaire"] = [lampadaire().vers_maillage("ENV_Modele_lampadaire")]
    return mod


def planter(mod, rg, espece, nom, loc, rot=None, echelle=None, coll="ENV_Vegetation"):
    variantes = mod.get(espece)
    if not variantes:
        avertir("espèce inconnue : " + espece)
        return None
    me = rg.choice(variantes)
    rot = rg.uniform(0, 2 * math.pi) if rot is None else rot
    ech = rg.uniform(0.85, 1.15) if echelle is None else echelle
    if espece == "bananier_bas":
        ech *= 0.7
    return instance(nom, me, coll, loc, rot, ech)


def construire_decor(dossier):
    rg = random.Random(GRAINE)
    for nom_coll in COLLECTIONS_ENV:
        c = marquer(bpy.data.collections.new(nom_coll))
        bpy.context.scene.collection.children.link(c)
        COLLS[nom_coll] = c
    dossier_tex = os.path.normpath(bpy.path.abspath(TEXTURES_ENV_DIR, start=dossier))
    log("textures du décor : " + dossier_tex)
    creer_materiaux(dossier_tex)
    mod = construire_modeles()

    # ---- parcelles des deux côtés de l'avenue
    lots_n, lots_s = [], []
    x = PARCELLE_MAGASIN[0]
    while x > X_VILLAS[0]:
        L = rg.uniform(22.0, 32.0)
        lots_n.append((x - L, L))
        x -= L
    x = PARCELLE_MAGASIN[1]
    while x < X_VILLAS[1]:
        L = rg.uniform(22.0, 32.0)
        lots_n.append((x, L))
        x += L
    x = X_VILLAS[0]
    while x < X_VILLAS[1]:
        L = rg.uniform(22.0, 32.0)
        lots_s.append((x, L))
        x += L

    coupures_n = [(PARCELLE_MAGASIN[0], 24.0)]
    coupures_s = []
    plantations_monde = []          # (espèce, x, y, rot, échelle, nom)

    # ---- villas
    n_villa = 0
    candidats_gardien = []
    for cote, lots in (("N", lots_n), ("S", lots_s)):
        for (x0, L) in lots:
            n_villa += 1
            P = rg.uniform(30.0, 38.0)
            nom = "ENV_Villa_%s%02d" % (cote, n_villa)
            mur, _, bati, g, pt, (gx, gl, px), plant, hm, piliers = villa(rg, nom, L, P)
            if cote == "N":
                loc, rot = Vector((x0, Y_LIMITE_N, 0.0)), 0.0
                def vers_monde(lx, ly, x0=x0):
                    return Vector((x0 + lx, Y_LIMITE_N + ly, 0.0))
                coupures_n.append((x0 + gx - 0.3, x0 + gx + gl + 0.3))
            else:
                loc, rot = Vector((x0 + L, Y_LIMITE_S, 0.0)), math.pi
                def vers_monde(lx, ly, x0=x0, L=L):
                    return Vector((x0 + L - lx, Y_LIMITE_S - ly, 0.0))
                coupures_s.append((x0 + L - gx - gl - 0.3, x0 + L - gx + 0.3))
            objet(nom + "_cloture", mur, "ENV_Villas", loc, rot)
            objet(nom + "_maison", bati, "ENV_Villas", loc, rot)
            gl_obj = objet(nom + "_portail", g, "ENV_Portails", loc, rot)
            gl_obj.location = vers_monde(gx, 0.0)
            gl_obj.location.z = Z_PLANTATION
            pt_obj = objet(nom + "_portillon", pt, "ENV_Portails", vers_monde(px, 0.0), rot)
            pt_obj.location.z = Z_PLANTATION
            for esp, lx, ly in plant:
                p = vers_monde(lx, ly)
                if (cote == "S" and VUE_DEGAGEE_FACADE[0] - 10 < p.x < VUE_DEGAGEE_FACADE[1] + 10
                        and esp in ("cocotier", "palmier_royal", "manguier", "flamboyant")):
                    continue                    # ombre portée sur la façade du magasin
                if esp == "bougainvillier":
                    # modèle prévu pour un mur de 2,60 m : on le cale sur le chaperon
                    plantations_monde.append((esp, p.x, p.y, rot, 1.0, nom, hm - 2.6))
                else:
                    plantations_monde.append((esp, p.x, p.y, None, None, nom, Z_JARDIN))
            if cote == "S":
                candidats_gardien.append((abs(x0 + L - gx - gl / 2 - X_PORTAIL_GARDIEN), vers_monde, gx, gl, hm, rot))
    log("%d villas" % n_villa)
    # plaque « RIVIERA 3 » et agent de sécurité devant le portail le plus proche de
    # X_PORTAIL_GARDIEN (côté opposé, bien visible depuis l'avenue)
    _, vers_monde, gx, gl, hm, rot = min(candidats_gardien, key=lambda c: c[0])
    plaque(vers_monde(gx - 1.0, -0.005) + Vector((0, 0, hm - 0.9)), rot)
    gob = objet("ENV_Agent_securite", gardien(GRAINE), "ENV_Personnages",
                vers_monde(gx + gl - 0.7, -0.75), rot + math.radians(-25))
    gob.location.z = Z_TROTTOIR

    # ---- voirie
    construire_voirie(rg, coupures_n, coupures_s)
    # ---- parcelle du magasin
    for esp, lx, ly in construire_parcelle_magasin(rg, mod):
        if esp == "bougainvillier":
            plantations_monde.append((esp, lx, ly, 0.0, 1.0, "ENV_Magasin", 0.0))
            continue
        z = 0.42 if ly < 0 else Z_PARVIS_FACADE           # jardinière ou jardin latéral
        plantations_monde.append((esp, lx, ly, None, None, "ENV_Magasin", z))

    # ---- plantations des jardins
    for k, (esp, x, y, rot, ech, origine, z) in enumerate(plantations_monde):
        planter(mod, rg, esp, "ENV_%s_%04d" % (esp.capitalize(), k), (x, y, z), rot, ech)

    # ---- arbres d'alignement sur les accotements
    n_arbre = 0
    for cote, coupures, (ya, yb) in (("N", coupures_n, Y_ACCOTEMENT_N), ("S", coupures_s, Y_ACCOTEMENT_S)):
        yc = (ya + yb) / 2
        reserve = [VUE_DEGAGEE_FACADE] if cote == "S" else [VUE_DEGAGEE_NORD]
        for s0, s1 in segments_libres(X_ARBRES[0], X_ARBRES[1], coupures + reserve, marge=2.5):
            x = s0 + rg.uniform(1.0, 4.0)
            while x < s1:
                r = rg.random()
                if r < 0.5:
                    esp = "flamboyant" if rg.random() < 0.85 else "flamboyant_vert"
                elif r < 0.78:
                    esp = "manguier"
                elif r < 0.9:
                    esp = "palmier_royal"
                else:
                    esp = "fromager"
                n_arbre += 1
                planter(mod, rg, esp, "ENV_Alignement_%s_%04d" % (cote, n_arbre),
                        (x, yc + rg.uniform(-0.25, 0.25), Z_ACCOTEMENT))
                x += rg.uniform(11.0, 17.0) if esp != "palmier_royal" else rg.uniform(7.0, 10.0)
    # Zones dégagées : palmiers royaux seulement (ombre fine, façade au soleil)
    for cote, (z0, z1), (ya, yb) in (("N", VUE_DEGAGEE_NORD, Y_ACCOTEMENT_N), ("S", VUE_DEGAGEE_FACADE, Y_ACCOTEMENT_S)):
        coup = coupures_n if cote == "N" else coupures_s + [(-2.0, 26.0)]   # axe de CAM_Facade_Boutique
        for s0, s1 in segments_libres(z0, z1, coup, marge=1.5):
            x = s0 + 1.0
            while x < s1 - 0.5:
                n_arbre += 1
                planter(mod, rg, "palmier_royal", "ENV_Alignement_%s_%04d" % (cote, n_arbre),
                        (x, (ya + yb) / 2, Z_ACCOTEMENT))
                x += rg.uniform(8.0, 10.0)
    # deux flamboyants pour encadrer le magasin
    planter(mod, rg, "flamboyant", "ENV_Flamboyant_magasin_G", (-25.0, -10.4, Z_ACCOTEMENT), echelle=1.08)
    planter(mod, rg, "flamboyant", "ENV_Flamboyant_magasin_D", (41.5, -10.4, Z_ACCOTEMENT), echelle=1.12)
    log("%d arbres d'alignement" % n_arbre)

    # ---- haies et massifs fleuris au pied des murs (bandes plantées)
    for cote, coupures, (ya, yb) in (("N", coupures_n, Y_PLANTATION_N), ("S", coupures_s, Y_PLANTATION_S)):
        mh = Maille()
        rgh = random.Random(GRAINE + (1 if cote == "N" else 2))
        # côté nord, le mur est en yb ; côté sud, en ya
        h0, h1 = (ya + 0.1, yb - 0.25) if cote == "N" else (ya + 0.25, yb - 0.1)
        for s0, s1 in segments_libres(X_VILLAS[0], X_VILLAS[1], coupures, marge=0.3):
            if s1 - s0 < 0.5:
                continue
            h = rgh.uniform(0.6, 0.9)
            mh.boite(s0, s1, h0, h1, Z_PLANTATION, Z_PLANTATION + h, "ENV_Haie",
                     faces=("haut", "avant", "arriere", "gauche", "droite"))
            # silhouette irrégulière et fleurs
            xx = s0
            while xx < s1:
                mat = "ENV_Hibiscus" if rgh.random() < 0.35 else "ENV_Feuillage_Tropical"
                c = Vector((xx, rgh.uniform(h0, h1), Z_PLANTATION + h + rgh.uniform(-0.15, 0.1)))
                mh.carte(c, direction_aleatoire(rgh, 0.8), rgh.uniform(0.5, 0.8), rgh.uniform(0, 6.3), mat)
                xx += rgh.uniform(0.25, 0.5)
        objet("ENV_Haies_" + cote, mh, "ENV_Vegetation")

    # ---- touffes d'herbe sur les accotements proches des caméras
    mt = Maille()
    rgt = random.Random(GRAINE + 3)
    for (ya, yb) in (Y_ACCOTEMENT_N, Y_ACCOTEMENT_S):
        for s0, s1 in segments_libres(-80.0, 110.0, coupures_n + coupures_s, marge=0.2):
            touffes_herbe(rgt, mt, s0, s1, ya + 0.05, yb - 0.05, Z_ACCOTEMENT, 2.2)
    objet("ENV_Touffes_herbe", mt, "ENV_Vegetation", ombre=False)

    # ---- lampadaires (accotement côté magasin)
    lp = mod["lampadaire"][0]
    k = 0
    for s0, s1 in segments_libres(X_ARBRES[0], X_ARBRES[1], coupures_n + [VUE_DEGAGEE_NORD], marge=1.0):
        x = s0 + 6.0
        while x < s1:
            k += 1
            instance("ENV_Lampadaire_%03d" % k, lp, "ENV_Mobilier_urbain", (x, Y_ACCOTEMENT_N[1] - 0.3, Z_ACCOTEMENT), 0.0)
            x += 34.0

    # ---- véhicules
    suv_noir = voiture(11, "ENV_Peinture_Noire", True).vers_maillage("ENV_Modele_SUV_noir")
    berline_bl = voiture(12, "ENV_Peinture_Blanche", False).vers_maillage("ENV_Modele_Berline_blanche")
    berline_ar = voiture(13, "ENV_Peinture_Argent", False).vers_maillage("ENV_Modele_Berline_argent")
    suv_bleu = voiture(14, "ENV_Peinture_Bleu_Nuit", True).vers_maillage("ENV_Modele_SUV_bleu")
    for nom, me, x, y, rz in [
            ("ENV_Voiture_parking_1", suv_noir, 0.75 + 2.5 * 2 + 1.25, -4.3, math.pi / 2),
            ("ENV_Voiture_parking_2", berline_bl, 0.75 + 2.5 * 0 + 1.25, -4.2, math.pi / 2),
            ("ENV_Voiture_rue_1", suv_bleu, -26.0, Y_ROUTE[1] - 1.25, math.pi),
            ("ENV_Voiture_rue_2", berline_ar, 70.0, Y_ROUTE[0] + 1.25, 0.0),
            ("ENV_Voiture_rue_3", berline_bl, -95.0, Y_ROUTE[0] + 3.0, 0.0),
            ("ENV_Voiture_rue_4", suv_noir, -170.0, Y_ROUTE[1] - 2.9, math.pi)]:
        z = z_parvis(y) if y > Y_LIMITE_N else Z_ROUTE
        instance(nom, me, "ENV_Vehicules", (x, y, z), rz)

    # ---- arrière-quartier (toits et jardins au-delà des villas de l'avenue), lointain
    arriere_plan(rg, mod)
    lointain(rg)
    # variantes de modèles restées sans instance
    for me in list(bpy.data.meshes):
        if me.get(TAG_ENV) and me.users == 0:
            bpy.data.meshes.remove(me)


def plaque(pos, rot=0.0):
    """Plaque « RIVIERA 3 » sur le mur de clôture, face à la rue (repère local -y)."""
    m = Maille()
    m.boite(-0.42, 0.42, -0.02, 0.0, -0.13, 0.13, "ENV_Plaque")
    objet("ENV_Plaque_Riviera3", m, "ENV_Mobilier_urbain", pos, rot)
    cu = marquer(bpy.data.curves.new("ENV_Texte_Riviera3", 'FONT'))
    cu.body = "RIVIERA 3"
    cu.size = 0.16
    cu.extrude = 0.002
    cu.align_x = 'CENTER'
    cu.align_y = 'CENTER'
    cu.materials.append(MATS["ENV_Texte_Noir"])
    ob = objet("ENV_Texte_Riviera3", cu, "ENV_Mobilier_urbain")
    ob.location = pos + Matrix.Rotation(rot, 3, 'Z') @ Vector((0, -0.025, 0))
    ob.rotation_euler = (math.pi / 2, 0.0, rot)


# =============================================================================
# RAPPORT, ENREGISTREMENT, PROGRAMME PRINCIPAL
# =============================================================================

def rapport_texte(chemin):
    r = RAPPORT
    t = ["=" * 64, "RAPPORT Cocody Riviera (environnement du magasin)", "=" * 64,
         "Objets créés : %d (dont %d instances de modèles partagés)" % (r["objets"], r["instances"]),
         "Faces construites : %d" % r["faces"],
         "Textures chargées (%d) : %s" % (len(r["textures"]), ", ".join(r["textures"]) or "aucune"),
         "Textures manquantes (%d) : %s" % (len(r["manquantes"]), ", ".join(r["manquantes"]) or "aucune"),
         "Avertissements (%d)" % len(r["avertissements"])]
    t += ["  - " + a for a in r["avertissements"]]
    t.append("Erreurs (%d)" % len(r["erreurs"]))
    t += ["  - " + e for e in r["erreurs"]]
    t.append("Caméra active : %s" % CAMERA_ACTIVE)
    t.append("Fichier : " + (chemin or "NON ENREGISTRÉ"))
    t.append("=" * 64)
    return "\n".join(t)


def enregistrer(dossier):
    chemin = os.path.join(dossier, BLEND_SORTIE)
    bpy.ops.wm.save_as_mainfile(filepath=chemin)
    for img in bpy.data.images:
        if (img.get(TAG_ENV) or img.get("marinor_genere")) and img.filepath and not img.filepath.startswith("//"):
            try:
                img.filepath = bpy.path.relpath(img.filepath)
            except ValueError:
                pass
    bpy.ops.wm.save_mainfile()
    return chemin


def main():
    for cle in RAPPORT:
        RAPPORT[cle] = 0 if isinstance(RAPPORT[cle], int) else []
    chemin = None
    dossier = dossier_projet()
    if dossier is None:
        erreur("%s introuvable : enregistrez ce script dans le dossier marinor_boutique." % SCRIPT_MAGASIN)
    else:
        try:
            if assurer_magasin(dossier):
                nettoyer()
                construire_decor(dossier)
                construire_ciel()
                if VITRAGE_REALISTE_MAGASIN:
                    vitrage_realiste()
                construire_cameras()
                regler_rendu()
            else:
                erreur("magasin introuvable : décor non construit")
        except Exception:
            erreur("construction interrompue :\n" + traceback.format_exc())
        texte = marquer(bpy.data.texts.new("Rapport_Cocody"))
        texte.write(rapport_texte(os.path.join(dossier, BLEND_SORTIE)))
        try:
            chemin = enregistrer(dossier)
        except Exception:
            erreur("enregistrement impossible :\n" + traceback.format_exc())
    print("\n" + rapport_texte(chemin) + "\n")


main()
