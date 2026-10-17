# -*- coding: utf-8 -*-
"""
Marin'Or Ivoire : construction du magasin 3D, bâtiment et mobilier (Blender 5.1)
=================================================================================

Utilisation
-----------
1. Placer ce script dans le dossier `marinor_boutique/`, à côté de
   `00_brief.md`, `elements.csv` et du dossier `textures/`.
2. Dans Blender 5.1 : onglet Scripting > Ouvrir > ce fichier > Exécuter (Alt+P).
3. Le script construit le magasin, enregistre `magasin_marinor.blend` dans ce
   même dossier et affiche un rapport dans la console (Fenêtre > Afficher la
   console système sous Windows). Le rapport est aussi copié dans le texte
   Blender `Rapport_Marinor` (éditeur de texte), plus simple à copier.

Le script est relançable : il supprime d'abord tout ce qu'il a créé.
Aucune dépendance externe (uniquement bpy, mathutils et la bibliothèque standard).
"""

import csv
import math
import os
import re
import traceback

import bpy
from mathutils import Euler, Matrix, Vector


# =============================================================================
# CONSTANTES
# =============================================================================

# Dossier des textures. "//" = relatif au .blend. Un chemin absolu marche aussi.
TEXTURES_DIR = "//textures/"

# Dossier du projet (elements.csv). Vide = détection automatique
# (dossier du .blend ouvert, puis dossier de ce script).
BASE_DIR = ""

CSV_NAME = "elements.csv"
BLEND_NAME = "magasin_marinor.blend"

# Marque posée sur tout ce que le script crée (sert au nettoyage au relancement).
TAG = "marinor_genere"

# Éclairage (version 3, renforcé : aucun coin sombre). Les lampes de même
# type partagent leurs données : changer la puissance d'un spot change celle
# de tous les spots. Accents (spots, suspensions, enseigne) en 2700 K ;
# éclairage général (dalles LED, lécheurs de murs) en 3300 K, blanc chaud.
TEMPERATURE_K = 2700.0
TEMPERATURE_GENERALE_K = 3300.0
COULEUR_2700K = "#FFB46B"           # utilisée si la température n'est pas disponible
COULEUR_3000K = "#FFCB98"           # 3300 K
PUISSANCE_SPOT_W = 100.0            # version 2 : 60 W
ANGLE_SPOT_DEG = 100.0              # version 2 : 80°
PUISSANCE_SUSPENSION_W = 60.0       # version 2 : 40 W
PUISSANCE_ENSEIGNE_W = 120.0        # version 2 : 35 W
PUISSANCE_DALLE_W_M2 = 90.0         # dalles LED : puissance par m² (0,60 m -> 32 W)
PUISSANCE_LECHEUR_W_M = 20.0        # lécheurs de murs : puissance par mètre
EMISSION_DALLE = 6.0                # luminosité visible du diffuseur des dalles
DIAMETRE_DISQUE_SPOT = 0.10         # §1 : disque émissif de 0,10 m

# Lampe Area de l'enseigne. Elle est placée devant l'enseigne (y < 0) :
# +90 l'oriente vers +Y, donc vers l'enseigne. -90 l'oriente vers -Y (la rue).
ROT_X_AREA_LIGHT_DEG = 90.0

# Supprime le cube de la scène de démarrage de Blender (il traverse le bâtiment).
SUPPRIMER_CUBE_PAR_DEFAUT = True

COLLECTIONS = [
    "Sol", "Murs_exterieurs", "Murs_interieurs", "Cloisons", "Ouvertures", "Toit",
    "Toit_plafond", "Enseigne", "Eclairage", "Decor_sol", "Mobilier_vente",
    "Mobilier_degustation", "Plantes", "Comptoir_caisse", "Equipement_caisse",
    "Mobilier_back_office", "Sanitaires", "Local_technique", "Zones",
]

# Matériaux (§4). texture : "requise", "optionnelle" ou None (couleur unie).
# tuile : taille en mètres d'une répétition de la texture (réglable ensuite
# dans le nœud Mapping du matériau, sans toucher à la géométrie).
MATERIAUX = {
    "MAT_Sol_Terracotta":      dict(couleur="#c97a52", texture="requise",     tuile=1.0, rugosite=0.70),
    "MAT_Sol_BetonCire":       dict(couleur="#b9aea0", texture="requise",     tuile=2.0, rugosite=0.40),
    "MAT_Sol_Carrelage_Blanc": dict(couleur="#f2efe8", texture="requise",     tuile=1.0, rugosite=0.25),
    "MAT_Mur_Creme":           dict(couleur="#FFECD1", texture="optionnelle", tuile=2.0, rugosite=0.85),
    "MAT_Mur_Bordeaux":        dict(couleur="#7B1421", texture="optionnelle", tuile=2.0, rugosite=0.80),
    "MAT_Lambris_Bois":        dict(couleur="#a0724a", texture="requise",     tuile=1.2, rugosite=0.55),
    "MAT_Bois_Clair":          dict(couleur="#d2b48c", texture="requise",     tuile=1.0, rugosite=0.50),
    "MAT_Plan_Comptoir":       dict(couleur="#e9e3d6", texture=None,          rugosite=0.35),
    "MAT_Laiton_Brosse":       dict(couleur="#F9A825", texture="optionnelle", tuile=0.5, rugosite=0.35, metal=1.0),
    "MAT_Alu_Cadre":           dict(couleur="#2b2b2b", texture=None,          rugosite=0.40, metal=0.8),
    "MAT_Verre_Clair":         dict(couleur="#ffffff", texture=None,          rugosite=0.03, verre=True),
    "MAT_Toit_Etancheite":     dict(couleur="#d9d6cf", texture="optionnelle", tuile=2.0, rugosite=0.90),
    "MAT_Plafond_Blanc":       dict(couleur="#FFFFFF", texture=None,          rugosite=0.90),
    "MAT_Sanitaire_Blanc":     dict(couleur="#FFFFFF", texture=None,          rugosite=0.08, vernis=1.0),
    "MAT_Tapis_Fibre":         dict(couleur="#7B1421", texture="requise",     tuile=0.8, rugosite=0.95, teinte=True),
    "MAT_Logo":                dict(couleur="#FFECD1", texture="requise",     rugosite=0.50, logo=True),
    "MAT_Lumiere_Emissive":    dict(couleur="#fff1d6", texture=None,          rugosite=0.50, emission=8.0),
    "MAT_Panneau_LED":         dict(couleur="#fff4e2", texture=None,          rugosite=0.50,
                                    emission=EMISSION_DALLE, couleur_emission="#ffe3bf"),
    # Mobilier et équipements
    "MAT_Laque_Blanche":       dict(couleur="#f4f1ea", texture=None,          rugosite=0.30),
    "MAT_Metal_Galva":         dict(couleur="#a3a8ad", texture=None,          rugosite=0.35, metal=0.9),
    "MAT_Plastique_Noir":      dict(couleur="#161616", texture=None,          rugosite=0.40),
    "MAT_Ecran":               dict(couleur="#0b1118", texture=None,          rugosite=0.08,
                                    emission=0.6, couleur_emission="#5d8fbf"),
    "MAT_Cuir_Bordeaux":       dict(couleur="#5c1018", texture=None,          rugosite=0.45),
    "MAT_Pot":                 dict(couleur="#b5653d", texture=None,          rugosite=0.80),
    "MAT_Vegetal":             dict(couleur="#2a5519", texture=None,          rugosite=0.60),
    "MAT_Miroir":              dict(couleur="#ffffff", texture=None,          rugosite=0.02, metal=1.0),
}
EXTENSION_TEXTURE = {"MAT_Logo": ".png"}     # les autres : .jpg
OBJETS_LOGO = ("Enseigne_logo", "Tapis_logo", "Logo_mur_marque")


# =============================================================================
# ÉTAT DU RAPPORT
# =============================================================================

RAPPORT = {
    "objets_csv": 0,
    "objets_annexes": 0,
    "textures_chargees": [],
    "textures_manquantes": [],      # (fichier, "requise"/"optionnelle")
    "avertissements": [],
    "erreurs": [],
}


def log(msg):
    print("[Marin'Or] " + msg)


def avertir(msg):
    RAPPORT["avertissements"].append(msg)
    log("AVERTISSEMENT : " + msg)


def erreur(msg):
    RAPPORT["erreurs"].append(msg)
    log("ERREUR : " + msg)


# =============================================================================
# OUTILS
# =============================================================================

def marquer(id_data):
    id_data[TAG] = True
    return id_data


def hex_vers_lineaire(hex_couleur, alpha=1.0):
    h = hex_couleur.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (lin[0], lin[1], lin[2], alpha)


def entree(noeud, nom, valeur):
    """Règle une entrée de nœud si elle existe (noms stables Blender 4.x / 5.x)."""
    socket = noeud.inputs.get(nom)
    if socket is None:
        avertir("entrée '%s' absente du nœud %s" % (nom, noeud.name))
        return
    socket.default_value = valeur


def socket_par_id(sockets, identifiant):
    for s in sockets:
        if s.identifier == identifiant:
            return s
    return None


def trouver_dossier_projet():
    candidats = []
    if BASE_DIR:
        candidats.append(bpy.path.abspath(BASE_DIR))
    if bpy.data.filepath:
        candidats.append(os.path.dirname(bpy.data.filepath))
    fichier_script = globals().get("__file__")
    if fichier_script:
        candidats.append(os.path.dirname(bpy.path.abspath(fichier_script)))
    try:
        espace = bpy.context.space_data
        if espace and espace.type == 'TEXT_EDITOR' and espace.text and espace.text.filepath:
            candidats.append(os.path.dirname(bpy.path.abspath(espace.text.filepath)))
    except Exception:
        pass
    for texte in bpy.data.texts:
        if texte.filepath:
            candidats.append(os.path.dirname(bpy.path.abspath(texte.filepath)))
    candidats.append(os.getcwd())
    for dossier in candidats:
        if dossier and os.path.isfile(os.path.join(dossier, CSV_NAME)):
            return os.path.normpath(dossier)
    return None


def lire_csv(chemin):
    lignes = []
    with open(chemin, newline="", encoding="utf-8-sig") as f:
        for brut in csv.DictReader(f):
            if not (brut.get("nom") or "").strip():
                continue

            def nombre(cle):
                valeur = (brut.get(cle) or "").strip().replace(",", ".")
                return float(valeur) if valeur else 0.0

            lignes.append(dict(
                id=brut["id"].strip(),
                nom=brut["nom"].strip(),
                type=brut["type"].strip().lower(),
                collection=brut["collection"].strip(),
                pos=Vector((nombre("x"), nombre("y"), nombre("z"))),
                dim=Vector((nombre("dim_x"), nombre("dim_y"), nombre("dim_z"))),
                rot_x=nombre("rot_x_deg"),
                rot_z=nombre("rot_z_deg"),
                materiau=(brut.get("materiau") or "").strip(),
                notes=(brut.get("notes") or "").strip(),
            ))
    return lignes


# =============================================================================
# NETTOYAGE (relançable)
# =============================================================================

def nettoyer(lignes):
    noms_objets = {l["nom"] for l in lignes}
    scene_coll = bpy.context.scene.collection

    for ob in list(bpy.data.objects):
        if ob.get(TAG) or ob.name in noms_objets:
            bpy.data.objects.remove(ob, do_unlink=True)

    if SUPPRIMER_CUBE_PAR_DEFAUT:
        cube = bpy.data.objects.get("Cube")
        if (cube and cube.type == 'MESH' and len(cube.data.vertices) == 8
                and cube.location.length < 1e-6):
            bpy.data.objects.remove(cube, do_unlink=True)
            log("cube de la scène par défaut supprimé")

    for coll in list(bpy.data.collections):
        if coll.get(TAG) or coll.name in COLLECTIONS:
            # Ce que l'utilisateur y aurait rangé est remis dans la scène.
            for ob in list(coll.objects):
                if len(ob.users_collection) == 1:
                    scene_coll.objects.link(ob)
            for enfant in list(coll.children):
                if enfant.name not in scene_coll.children:
                    scene_coll.children.link(enfant)
            bpy.data.collections.remove(coll)

    for mat in list(bpy.data.materials):
        if mat.get(TAG) or mat.name in MATERIAUX:
            bpy.data.materials.remove(mat)

    for bloc in (bpy.data.meshes, bpy.data.lights, bpy.data.images, bpy.data.texts):
        for id_data in list(bloc):
            if id_data.get(TAG):
                bloc.remove(id_data)


# =============================================================================
# TEXTURES ET MATÉRIAUX
# =============================================================================

def charger_image(dossier_textures, fichier, non_couleur=False):
    chemin = os.path.join(dossier_textures, fichier)
    if not os.path.isfile(chemin):
        return None
    try:
        img = bpy.data.images.load(chemin, check_existing=False)
    except Exception as exc:
        erreur("lecture impossible de %s : %s" % (fichier, exc))
        return None
    marquer(img)
    img.name = fichier
    if non_couleur:
        try:
            img.colorspace_settings.name = "Non-Color"
        except Exception:
            avertir("espace couleur Non-Color indisponible pour " + fichier)
    if img.size[0] == 0 or img.size[1] == 0:
        erreur("image vide ou illisible : " + fichier)
        return None
    RAPPORT["textures_chargees"].append(fichier)
    return img


def creer_materiau(nom, spec, dossier_textures):
    mat = marquer(bpy.data.materials.new(nom))
    if mat.node_tree is None:
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    sortie = nt.nodes.new("ShaderNodeOutputMaterial")
    sortie.location = (400, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (100, 0)
    nt.links.new(bsdf.outputs["BSDF"], sortie.inputs["Surface"])

    couleur = hex_vers_lineaire(spec["couleur"])
    entree(bsdf, "Base Color", couleur)
    entree(bsdf, "Roughness", spec.get("rugosite", 0.5))
    entree(bsdf, "Metallic", spec.get("metal", 0.0))
    mat.diffuse_color = couleur
    mat.roughness = spec.get("rugosite", 0.5)

    if spec.get("vernis"):
        entree(bsdf, "Coat Weight", spec["vernis"])
        entree(bsdf, "Coat Roughness", 0.03)

    if spec.get("emission"):
        entree(bsdf, "Emission Color", hex_vers_lineaire(spec.get("couleur_emission", spec["couleur"])))
        entree(bsdf, "Emission Strength", spec["emission"])

    if spec.get("verre"):
        entree(bsdf, "Alpha", 0.35)
        entree(bsdf, "IOR", 1.5)
        mat.diffuse_color = (couleur[0], couleur[1], couleur[2], 0.35)
        rendre_transparent(mat, melange=True)

    # Texture couleur : textures/<nom>_color.jpg (ou .png pour le logo).
    img = None
    if spec.get("texture"):
        fichier = nom + "_color" + EXTENSION_TEXTURE.get(nom, ".jpg")
        img = charger_image(dossier_textures, fichier)
        if img is None:
            RAPPORT["textures_manquantes"].append((fichier, spec["texture"]))
            if spec["texture"] == "requise":
                avertir("texture absente : %s -> couleur de secours %s" % (fichier, spec["couleur"]))
            else:
                log("texture optionnelle absente : %s -> couleur %s" % (fichier, spec["couleur"]))

    vecteur = None
    if img is not None and not spec.get("logo"):
        coord = nt.nodes.new("ShaderNodeTexCoord")
        coord.location = (-900, 0)
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.location = (-700, 0)
        echelle = 1.0 / spec.get("tuile", 1.0)
        mapping.inputs["Scale"].default_value = (echelle, echelle, 1.0)
        nt.links.new(coord.outputs["UV"], mapping.inputs["Vector"])
        vecteur = mapping.outputs["Vector"]

    if img is not None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.name = tex.label = "Texture couleur"
        tex.location = (-450, 150)
        tex.image = img
        if vecteur is not None:
            nt.links.new(vecteur, tex.inputs["Vector"])
        else:
            tex.extension = 'CLIP'
        sortie_couleur = tex.outputs["Color"]

        if spec.get("teinte"):
            # Teinte modifiable : couleur B (blanc = texture d'origine).
            mix = nt.nodes.new("ShaderNodeMix")
            mix.name = mix.label = "Teinte"
            mix.location = (-150, 250)
            mix.data_type = 'RGBA'
            mix.blend_type = 'MULTIPLY'
            socket_par_id(mix.inputs, "Factor_Float").default_value = 1.0
            socket_par_id(mix.inputs, "B_Color").default_value = (1.0, 1.0, 1.0, 1.0)
            nt.links.new(sortie_couleur, socket_par_id(mix.inputs, "A_Color"))
            sortie_couleur = socket_par_id(mix.outputs, "Result_Color")

        nt.links.new(sortie_couleur, bsdf.inputs["Base Color"])

        if spec.get("logo"):
            nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
            rendre_transparent(mat, melange=False)

        # Textures optionnelles de rugosité et de relief, même préfixe.
        img_r = charger_image(dossier_textures, nom + "_roughness.jpg", non_couleur=True)
        if img_r is not None:
            tex_r = nt.nodes.new("ShaderNodeTexImage")
            tex_r.location = (-450, -150)
            tex_r.image = img_r
            if vecteur is not None:
                nt.links.new(vecteur, tex_r.inputs["Vector"])
            nt.links.new(tex_r.outputs["Color"], bsdf.inputs["Roughness"])
        img_n = charger_image(dossier_textures, nom + "_normal.jpg", non_couleur=True)
        if img_n is not None:
            tex_n = nt.nodes.new("ShaderNodeTexImage")
            tex_n.location = (-450, -450)
            tex_n.image = img_n
            if vecteur is not None:
                nt.links.new(vecteur, tex_n.inputs["Vector"])
            normal = nt.nodes.new("ShaderNodeNormalMap")
            normal.location = (-150, -450)
            nt.links.new(tex_n.outputs["Color"], normal.inputs["Color"])
            nt.links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])

    return mat, img


def rendre_transparent(mat, melange):
    """melange=True : mode blend (verre). False : découpe alpha (logo)."""
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = 'BLENDED' if melange else 'DITHERED'
    else:
        mat.blend_method = 'BLEND' if melange else 'HASHED'
    if hasattr(mat, "use_transparent_shadow"):
        mat.use_transparent_shadow = True
    mat.use_backface_culling = False


# =============================================================================
# GÉOMÉTRIE (maillages construits directement, sans bpy.ops)
# =============================================================================

def maillage(nom, sommets, faces, uv_fonction, lisse=None, index_mat=None):
    me = marquer(bpy.data.meshes.new(nom))
    me.from_pydata(sommets, [], faces)
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = uv_fonction(co, poly.normal)
    if lisse:
        for poly in me.polygons:
            poly.use_smooth = lisse(poly)
    if index_mat:
        for poly, im in zip(me.polygons, index_mat):
            poly.material_index = im
    me.update()
    me.validate()
    return me


def maillage_box(nom, dim, origine_monde):
    """Pavé centré. UV en mètres, en coordonnées monde : les textures se
    raccordent d'un objet à l'autre (sols, murs)."""
    hx, hy, hz = dim.x / 2, dim.y / 2, dim.z / 2
    s = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
         (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    o = origine_monde

    def uv(co, n):
        w = co + o
        if abs(n.z) > 0.5:
            return (w.x, w.y)
        if abs(n.y) > 0.5:
            return (w.x, w.z)
        return (w.y, w.z)

    return maillage(nom, s, f, uv)


def maillage_plan(nom, largeur, hauteur, uv_01):
    hx, hy = largeur / 2, hauteur / 2
    s = [(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0)]
    if uv_01:
        return maillage(nom, s, [(0, 1, 2, 3)], lambda co, n: (co.x / largeur + 0.5, co.y / hauteur + 0.5))
    return maillage(nom, s, [(0, 1, 2, 3)], lambda co, n: (co.x + hx, co.y + hy))


def maillage_cylindre(nom, diametre, hauteur, segments=32, fond=True, dessus=True):
    r, hz = diametre / 2, hauteur / 2
    s = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        s.append((r * math.cos(a), r * math.sin(a), -hz))
    for i in range(segments):
        a = 2 * math.pi * i / segments
        s.append((r * math.cos(a), r * math.sin(a), hz))
    f = [(i, (i + 1) % segments, segments + (i + 1) % segments, segments + i) for i in range(segments)]
    if fond:
        f.append(tuple(reversed(range(segments))))
    if dessus:
        f.append(tuple(range(segments, 2 * segments)))
    perimetre = 2 * math.pi * r

    def uv(co, n):
        if abs(n.z) > 0.5:
            return (co.x, co.y)
        return ((math.atan2(co.y, co.x) / (2 * math.pi) + 0.5) * perimetre, co.z + hz)

    return maillage(nom, s, f, uv, lisse=lambda p: abs(p.normal.z) < 0.5)


def maillage_disque(nom, diametre, segments=24):
    """Disque horizontal, face vers -Z (vers la salle)."""
    r = diametre / 2
    s = [(r * math.cos(-2 * math.pi * i / segments), r * math.sin(-2 * math.pi * i / segments), 0)
         for i in range(segments)]
    return maillage(nom, s, [tuple(range(segments))], lambda co, n: (co.x / diametre + 0.5, co.y / diametre + 0.5))


# =============================================================================
# MEUBLES COMPOSÉS : un objet par ligne du CSV, fait de plusieurs pièces
# =============================================================================
# Repère local d'une recette : centré en x et y, z = 0 au sol, face avant
# vers -Y. dim = (largeur, profondeur, hauteur). Chaque recette renvoie les
# matériaux supplémentaires (le matériau 0 est celui du CSV) et les pièces.

FACES_BOITE = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def devant(centre, rx, distance):
    """Point situé à `distance` devant (-Y) un centre, pièce inclinée de rx autour de X."""
    return Vector(centre) + Matrix.Rotation(math.radians(rx), 3, 'X') @ Vector((0, -distance, 0))


class Pieces:
    def __init__(self):
        self.sommets, self.faces, self.mats, self.lisses = [], [], [], []

    def _ajout(self, sommets, faces, mat, lisses):
        base = len(self.sommets)
        self.sommets += sommets
        self.faces += [tuple(base + i for i in f) for f in faces]
        self.mats += [mat] * len(faces)
        self.lisses += lisses

    def boite(self, c, t, mat, rx=0.0):
        hx, hy, hz = t[0] / 2, t[1] / 2, t[2] / 2
        rot = Matrix.Rotation(math.radians(rx), 3, 'X')
        coins = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
                 (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
        self._ajout([rot @ Vector(v) + Vector(c) for v in coins], FACES_BOITE, mat, [False] * 6)

    def cylindre(self, c, diametre, hauteur, mat, segments=24, dessus=True):
        r, hz, c = diametre / 2, hauteur / 2, Vector(c)
        anneau = [(r * math.cos(2 * math.pi * i / segments), r * math.sin(2 * math.pi * i / segments))
                  for i in range(segments)]
        sommets = [c + Vector((x, y, -hz)) for x, y in anneau] + [c + Vector((x, y, hz)) for x, y in anneau]
        faces = [(i, (i + 1) % segments, segments + (i + 1) % segments, segments + i) for i in range(segments)]
        faces.append(tuple(reversed(range(segments))))
        if dessus:
            faces.append(tuple(range(segments, 2 * segments)))
        self._ajout(sommets, faces, mat, [True] * segments + [False] * (len(faces) - segments))

    def sphere(self, c, diametre, mat, segments=14, anneaux=8):
        r, c = diametre / 2, Vector(c)
        sommets = [c + Vector((0, 0, r))]
        for k in range(1, anneaux):
            t = math.pi * k / anneaux
            for i in range(segments):
                p = 2 * math.pi * i / segments
                sommets.append(c + Vector((r * math.sin(t) * math.cos(p), r * math.sin(t) * math.sin(p), r * math.cos(t))))
        sommets.append(c + Vector((0, 0, -r)))
        bas = len(sommets) - 1

        def v(k, i):
            return 1 + (k - 1) * segments + i % segments

        faces = [(0, v(1, i), v(1, i + 1)) for i in range(segments)]
        for k in range(1, anneaux - 1):
            faces += [(v(k, i), v(k + 1, i), v(k + 1, i + 1), v(k, i + 1)) for i in range(segments)]
        faces += [(bas, v(anneaux - 1, i + 1), v(anneaux - 1, i)) for i in range(segments)]
        self._ajout(sommets, faces, mat, [True] * len(faces))


def r_gondole(L, P, H):
    p = Pieces()
    p.boite((0, 0, 0.05), (L - 0.06, P, 0.10), 1)                       # socle
    p.boite((0, 0, (0.10 + H) / 2), (L - 0.06, 0.03, H - 0.10), 0)      # panneau central
    for sx in (-1, 1):
        p.boite((sx * (L / 2 - 0.015), 0, H / 2), (0.03, P, H), 2)      # joues d'extrémité
    prof = (P - 0.03) / 2 - 0.01
    z = 0.1125
    while z < H - 0.2:
        for sy in (-1, 1):
            p.boite((0, sy * (0.02 + prof / 2), z), (L - 0.06, prof, 0.025), 0)
            p.boite((0, sy * (0.015 + prof + 0.005), z + 0.005), (L - 0.06, 0.01, 0.035), 1)   # porte-étiquettes
        z += 0.36
    return ["MAT_Alu_Cadre", "MAT_Mur_Bordeaux"], p


def r_etagere_murale(L, P, H):
    p = Pieces()
    prof = P - 0.03
    p.boite((0, P / 2 - 0.015, H / 2), (L, 0.03, H), 0)                 # fond, contre le mur
    for sx in (-1, 1):
        p.boite((sx * (L / 2 - 0.0125), -0.015, H / 2), (0.025, prof, H), 0)
    p.boite((0, -0.015, 0.05), (L - 0.05, prof, 0.10), 1)
    z = 0.1125
    while z < H - 0.3:
        p.boite((0, -0.015, z), (L - 0.05, prof, 0.025), 0)
        p.boite((0, -P / 2 + 0.005, z + 0.005), (L - 0.05, 0.01, 0.035), 1)
        z += 0.38
    p.boite((0, -0.015, H - 0.0125), (L - 0.05, prof, 0.025), 0)
    p.boite((0, -P / 2 + 0.01, H - 0.11), (L - 0.05, 0.02, 0.18), 2)   # fronton
    return ["MAT_Alu_Cadre", "MAT_Mur_Bordeaux"], p


def r_rayonnage(L, P, H):
    p = Pieces()
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.boite((sx * (L / 2 - 0.02), sy * (P / 2 - 0.02), H / 2), (0.04, 0.04, H), 0)
    for k in range(5):
        p.boite((0, 0, 0.15 + k * (H - 0.18) / 4), (L, P, 0.03), 0)
    return [], p


def r_table(L, P, H):
    p = Pieces()
    p.boite((0, 0, H - 0.02), (L, P, 0.04), 0)
    e = min(0.08, P / 4)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.boite((sx * (L / 2 - e), sy * (P / 2 - e), (H - 0.04) / 2), (0.05, 0.05, H - 0.04), 1)
    return ["MAT_Alu_Cadre"], p


def r_tabouret(L, P, H):
    p = Pieces()
    p.cylindre((0, 0, H - 0.03), L, 0.06, 0)
    a = L * 0.3
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.boite((sx * a, sy * a, (H - 0.06) / 2), (0.025, 0.025, H - 0.06), 1)
    for s in (-1, 1):
        p.boite((0, s * a, 0.28), (2 * a, 0.018, 0.018), 1)             # repose-pieds
        p.boite((s * a, 0, 0.28), (0.018, 2 * a, 0.018), 1)
    return ["MAT_Alu_Cadre"], p


def r_chaise(L, P, H):
    p = Pieces()
    p.boite((0, 0, 0.45), (L, P, 0.04), 0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.boite((sx * (L / 2 - 0.03), sy * (P / 2 - 0.03), 0.215), (0.03, 0.03, 0.43), 1)
    p.boite((0, P / 2 - 0.015, (0.47 + H) / 2), (L, 0.03, H - 0.47), 0)   # dossier
    return ["MAT_Alu_Cadre"], p


def r_frigo(L, P, H):
    p = Pieces()
    zb, zh = 0.12, H - 0.13
    p.boite((0, P / 2 - 0.025, H / 2), (L, 0.05, H), 0)
    for sx in (-1, 1):
        p.boite((sx * (L / 2 - 0.025), 0, H / 2), (0.05, P, H), 0)
    p.boite((0, 0, zb / 2), (L, P, zb), 0)
    p.boite((0, 0, (zh + H) / 2), (L, P, H - zh), 0)
    p.boite((0, -P / 2 + 0.04, (zb + zh) / 2), (L - 0.10, 0.02, zh - zb), 1)       # portes vitrées
    p.boite((0, -P / 2 + 0.04, (zb + zh) / 2), (0.03, 0.03, zh - zb), 2)           # montant central
    for sx in (-1, 1):
        p.boite((sx * 0.05, -P / 2 + 0.015, (zb + zh) / 2), (0.02, 0.03, 0.5), 2)  # poignées
    for k in range(1, 5):
        p.boite((0, 0, zb + k * (zh - zb) / 5), (L - 0.10, P - 0.15, 0.015), 2)    # clayettes
    p.boite((0, -P / 2 + 0.08, zh - 0.02), (L - 0.12, 0.03, 0.015), 3)             # éclairage intérieur
    return ["MAT_Verre_Clair", "MAT_Alu_Cadre", "MAT_Lumiere_Emissive"], p


def r_presentoir_vrac(L, P, H):
    p = Pieces()
    h1 = H - 0.44
    p.boite((0, 0, h1 / 2), (L, P, h1), 0)
    p.boite((0, P / 4, h1 + 0.15), (L, P / 2, 0.30), 0)
    cols = max(1, round(L / 0.5))
    cw, cd, hc, e = L / cols - 0.04, P / 2 - 0.06, 0.14, 0.015
    for yc, zb in ((-P / 4, h1), (P / 4, h1 + 0.30)):
        for i in range(cols):
            xc = -L / 2 + (i + 0.5) * L / cols
            p.boite((xc, yc, zb + e / 2), (cw, cd, e), 1)
            for s in (-1, 1):
                p.boite((xc, yc + s * (cd / 2 - e / 2), zb + hc / 2), (cw, e, hc), 1)
                p.boite((xc + s * (cw / 2 - e / 2), yc, zb + hc / 2), (e, cd, hc), 1)
    return ["MAT_Lambris_Bois"], p


def r_plante(L, P, H):
    p = Pieces()
    hp, dp = min(0.45, H * 0.3), L * 0.6
    p.cylindre((0, 0, hp / 2), dp, hp, 0, dessus=False)
    p.cylindre((0, 0, hp - 0.04), dp * 0.95, 0.02, 2)                   # terre
    zt = H * 0.6
    p.cylindre((0, 0, (hp + zt) / 2), 0.04, zt - hp, 2, segments=8)     # tronc
    p.sphere((0, 0, H - L * 0.35), L * 0.7, 1)
    p.sphere((L * 0.12, -L * 0.08, H * 0.62), L * 0.55, 1)
    p.sphere((-L * 0.12, L * 0.1, H * 0.72), L * 0.5, 1)
    return ["MAT_Vegetal", "MAT_Lambris_Bois"], p


def r_ecran(L, P, H):
    p = Pieces()
    hs = H * 0.62
    p.boite((0, 0, 0.0075), (L * 0.45, P, 0.015), 0)                    # pied
    p.boite((0, P * 0.2, 0.015 + H * 0.225), (0.05, 0.03, H * 0.45), 0)
    p.boite((0, 0, H - hs / 2), (L, 0.03, hs), 0)
    p.boite((0, -0.0165, H - hs / 2), (L - 0.02, 0.003, hs - 0.02), 1)  # dalle
    return ["MAT_Ecran"], p


def r_scanner(L, P, H):
    p = Pieces()
    p.boite((0, 0, 0.01), (L, P, 0.02), 0)
    p.boite((0, 0.01, 0.02 + (H - 0.06) / 2), (L * 0.55, P * 0.45, H - 0.06), 0, rx=-12)
    tete = (0, -0.005, H - 0.03)
    p.boite(tete, (L * 0.9, P * 0.8, 0.06), 0, rx=-25)
    p.boite(devant(tete, -25, P * 0.4 + 0.0015), (L * 0.7, 0.003, 0.04), 1, rx=-25)   # fenêtre de lecture
    return ["MAT_Ecran"], p


def r_tpe(L, P, H):
    p = Pieces()
    p.boite((0, 0, (H - 0.003) / 2), (L, P, H - 0.003), 0)
    p.boite((0, -P * 0.15, H - 0.0015), (L * 0.75, P * 0.4, 0.003), 1)
    return ["MAT_Ecran"], p


def r_borne(L, P, H):
    p = Pieces()
    p.boite((0, 0, 0.01), (L * 0.8, P * 0.8, 0.02), 2)
    p.boite((0, 0.05, 0.46), (0.35, 0.30, 0.88), 0)                     # fût
    p.boite((0, 0, 1.0), (L, P, 0.2), 0)                                # tête
    p.boite((0, -0.06, 1.1035), (L * 0.5, P * 0.45, 0.007), 3)          # vitre du scanner
    ecran = (0, P / 2 - 0.1, H - 0.22)
    p.boite(ecran, (L * 0.85, 0.04, 0.42), 2, rx=-15)
    p.boite(devant(ecran, -15, 0.0215), (L * 0.8, 0.003, 0.38), 1, rx=-15)
    return ["MAT_Ecran", "MAT_Plastique_Noir", "MAT_Verre_Clair"], p


def r_casiers(L, P, H):
    p = Pieces()
    p.boite((0, 0.0175, H / 2), (L, P - 0.035, H), 1)
    cols, rangs = max(1, round(L / 0.4)), 2
    dw, dh = L / cols, (H - 0.1) / rangs
    for i in range(cols):
        for j in range(rangs):
            x, z = -L / 2 + dw * (i + 0.5), 0.1 + dh * (j + 0.5)
            p.boite((x, -P / 2 + 0.025, z), (dw - 0.01, 0.02, dh - 0.01), 0)
            p.boite((x + dw / 2 - 0.06, -P / 2 + 0.0075, z), (0.015, 0.015, 0.12), 2)
    return ["MAT_Laque_Blanche", "MAT_Alu_Cadre"], p


RECETTES = {
    "gondole": r_gondole, "etagere_murale": r_etagere_murale, "rayonnage": r_rayonnage,
    "table": r_table, "tabouret": r_tabouret, "chaise": r_chaise, "frigo": r_frigo,
    "presentoir_vrac": r_presentoir_vrac, "plante": r_plante, "ecran": r_ecran,
    "scanner": r_scanner, "tpe": r_tpe, "borne": r_borne, "casiers": r_casiers,
}


def uv_local(co, n):
    if abs(n.z) >= max(abs(n.x), abs(n.y)):
        return (co.x, co.y)
    if abs(n.y) >= abs(n.x):
        return (co.x, co.z)
    return (co.y, co.z)


def maillage_meuble(nom, typ, dim):
    extras, p = RECETTES[typ](dim.x, dim.y, dim.z)
    decal = Vector((0, 0, dim.z / 2))           # origine au centre de l'objet (convention §1)
    sommets = [tuple(v - decal) for v in p.sommets]
    lisses = p.lisses
    me = maillage(nom, sommets, p.faces, uv_local, lisse=lambda poly: lisses[poly.index], index_mat=p.mats)
    return me, extras


# =============================================================================
# LAMPES
# =============================================================================

def couleur_2700k(lum, temperature=TEMPERATURE_K):
    if hasattr(lum, "use_temperature") and hasattr(lum, "temperature"):
        lum.use_temperature = True
        lum.temperature = temperature
        lum.color = (1.0, 1.0, 1.0)
    else:
        secours = COULEUR_2700K if temperature <= TEMPERATURE_K else COULEUR_3000K
        lum.color = hex_vers_lineaire(secours)[:3]


def donnees_lampe(nom, type_lampe, puissance, temperature=TEMPERATURE_K):
    lum = bpy.data.lights.get(nom)
    if lum is not None and lum.get(TAG):
        return lum
    lum = marquer(bpy.data.lights.new(nom, type_lampe))
    lum.energy = puissance
    couleur_2700k(lum, temperature)
    if type_lampe == 'SPOT':
        lum.spot_size = math.radians(ANGLE_SPOT_DEG)
        lum.spot_blend = 0.4
        lum.shadow_soft_size = 0.02
    elif type_lampe == 'POINT':
        lum.shadow_soft_size = 0.03
    return lum


def lampe_invisible_camera(ob):
    """La lampe éclaire et se reflète ; le diffuseur visible est le maillage émissif."""
    if hasattr(ob, "visible_camera"):
        ob.visible_camera = False


# =============================================================================
# CONSTRUCTION
# =============================================================================

def nouvel_objet(nom, data, coll, ligne=None):
    ob = marquer(bpy.data.objects.new(nom, data))
    coll.objects.link(ob)
    if ob.name != nom:
        erreur("nom en conflit : '%s' créé sous le nom '%s'" % (nom, ob.name))
    if ligne is not None:
        ob["marinor_id"] = ligne["id"]
        if ligne["notes"]:
            ob["marinor_notes"] = ligne["notes"]
    return ob


def enfant_annexe(parent, nom, data, coll, decalage):
    """Objet annexe imposé par le type (lampe d'un spot, d'une suspension)."""
    ob = nouvel_objet(nom, data, coll)
    ob.parent = parent
    ob.location = decalage                # local au parent (parent sans rotation)
    RAPPORT["objets_annexes"] += 1
    return ob


def construire_ligne(l, collections, materiaux, logo_img):
    nom, typ, dim, pos = l["nom"], l["type"], l["dim"], l["pos"]
    coll = collections[l["collection"]]
    rot = Euler((math.radians(l["rot_x"]), 0.0, math.radians(l["rot_z"])), 'XYZ')
    mat = materiaux.get(l["materiau"]) if l["materiau"] else None
    if l["materiau"] and mat is None:
        erreur("%s : matériau inconnu '%s'" % (nom, l["materiau"]))

    if typ in ("box", "glass", "door"):
        if typ == "glass" and l["materiau"] != "MAT_Verre_Clair":
            avertir("%s : type glass avec %s" % (nom, l["materiau"]))
        ob = nouvel_objet(nom, maillage_box(nom, dim, pos), coll, l)

    elif typ == "plane":
        largeur, hauteur = dim.x, dim.y
        est_logo = nom in OBJETS_LOGO or l["materiau"] == "MAT_Logo"
        if est_logo:
            mat = materiaux["MAT_Logo"]
            if logo_img is not None:
                # Le ratio du plan suit celui de l'image ; la hauteur du CSV est gardée.
                largeur = hauteur * logo_img.size[0] / logo_img.size[1]
        ob = nouvel_objet(nom, maillage_plan(nom, largeur, hauteur, uv_01=est_logo), coll, l)

    elif typ == "cylinder":
        ob = nouvel_objet(nom, maillage_cylindre(nom, dim.x, dim.z, segments=16 if dim.x < 0.05 else 32), coll, l)

    elif typ == "empty":
        ob = nouvel_objet(nom, None, coll, l)
        if nom.startswith("Pivot_"):
            ob.empty_display_type = 'ARROWS'
            ob.empty_display_size = 0.3
        else:
            ob.empty_display_type = 'PLAIN_AXES'
            ob.empty_display_size = 0.25
            if dim.x or dim.y:
                ob["zone_dim_x"] = dim.x
                ob["zone_dim_y"] = dim.y

    elif typ == "spot":
        # Disque émissif sous le plafond ; la lampe juste dessous.
        ob = nouvel_objet(nom, maillage_disque(nom, DIAMETRE_DISQUE_SPOT), coll, l)
        pos = pos - Vector((0, 0, 0.002))
        ob.visible_shadow = False         # le disque ne bloque pas sa propre lampe
        lum = donnees_lampe("LUM_Spot_2700K", 'SPOT', PUISSANCE_SPOT_W)
        enfant_annexe(ob, nom + "_lampe", lum, coll, (0, 0, -0.02))

    elif typ == "suspension":
        # Abat-jour : cylindre ouvert en bas ; lampe Point au centre, au bas de l'abat-jour.
        ob = nouvel_objet(nom, maillage_cylindre(nom, dim.x, dim.z, fond=False), coll, l)
        lum = donnees_lampe("LUM_Suspension_2700K", 'POINT', PUISSANCE_SUSPENSION_W)
        enfant_annexe(ob, nom + "_lampe", lum, coll, (0, 0, -dim.z / 2 + 0.03))

    elif typ == "panneau_led":
        # Diffuseur émissif carré sous le plafond ; lampe Area juste dessous, vers le bas.
        ob = nouvel_objet(nom, maillage_box(nom, dim, pos), coll, l)
        ob.visible_shadow = False
        cote = round(dim.x, 2)
        lum = donnees_lampe("LUM_Dalle_LED_%d" % round(cote * 100), 'AREA',
                            PUISSANCE_DALLE_W_M2 * dim.x * dim.y, TEMPERATURE_GENERALE_K)
        lum.shape = 'RECTANGLE'
        lum.size, lum.size_y = dim.x * 0.96, dim.y * 0.96
        lampe = enfant_annexe(ob, nom + "_lampe", lum, coll, (0, 0, -dim.z / 2 - 0.002))
        lampe_invisible_camera(lampe)

    elif typ == "ruban_led":
        # Profilé LED : ruban émissif ; lampe Area inclinée par rot_x vers l'avant
        # (-Y local), donc vers le mur après rot_z (repère des meubles).
        ob = nouvel_objet(nom, maillage_box(nom, dim, Vector((0, 0, 0))), coll, l)
        ob.visible_shadow = False
        lum = donnees_lampe("LUM_" + nom, 'AREA', PUISSANCE_LECHEUR_W_M * dim.x, TEMPERATURE_GENERALE_K)
        lum.shape = 'RECTANGLE'
        lum.size, lum.size_y = dim.x, max(dim.y, 0.05)
        lampe = enfant_annexe(ob, nom + "_lampe", lum, coll, (0, 0, -dim.z / 2 - 0.002))
        lampe.rotation_euler = (math.radians(l["rot_x"]), 0.0, 0.0)
        lampe_invisible_camera(lampe)
        rot = Euler((0.0, 0.0, math.radians(l["rot_z"])), 'XYZ')

    elif typ == "area_light":
        lum = donnees_lampe("LUM_" + nom, 'AREA', PUISSANCE_ENSEIGNE_W)
        lum.shape = 'RECTANGLE'
        lum.size = dim.x
        lum.size_y = dim.y
        ob = nouvel_objet(nom, lum, coll, l)
        rot = Euler((math.radians(ROT_X_AREA_LIGHT_DEG + l["rot_x"]), 0.0, math.radians(l["rot_z"])), 'XYZ')

    elif typ in RECETTES:
        me, extras = maillage_meuble(nom, typ, dim)
        ob = nouvel_objet(nom, me, coll, l)
        if mat is not None:
            me.materials.append(mat)
        else:
            me.materials.append(materiaux["MAT_Bois_Clair"])
        for nom_mat in extras:
            me.materials.append(materiaux[nom_mat])
        mat = None

    else:
        erreur("%s : type inconnu '%s'" % (nom, typ))
        return None

    ob.location = pos
    ob.rotation_euler = rot
    if mat is not None and ob.type == 'MESH':
        ob.data.materials.append(mat)
    return ob


def parenter(enfant, parent):
    """Parenté sans déplacer l'enfant dans le monde."""
    enfant.parent = parent
    enfant.matrix_parent_inverse = parent.matrix_basis.inverted()


def construire():
    dossier = trouver_dossier_projet()
    if dossier is None:
        erreur("%s introuvable. Enregistrez ce script (ou le .blend) dans le dossier "
               "marinor_boutique, ou renseignez BASE_DIR en tête de script." % CSV_NAME)
        return None
    dossier_textures = os.path.normpath(bpy.path.abspath(TEXTURES_DIR, start=dossier))
    log("dossier du projet : " + dossier)
    log("dossier des textures : " + dossier_textures)
    if not os.path.isdir(dossier_textures):
        avertir("dossier des textures introuvable : " + dossier_textures)

    lignes = lire_csv(os.path.join(dossier, CSV_NAME))
    log("%d lignes lues dans %s" % (len(lignes), CSV_NAME))

    nettoyer(lignes)

    # Collections : ordre du brief, puis toute valeur supplémentaire du CSV.
    scene = bpy.context.scene
    noms_coll = list(COLLECTIONS)
    for l in lignes:
        if l["collection"] not in noms_coll:
            avertir("collection hors brief : " + l["collection"])
            noms_coll.append(l["collection"])
    collections = {}
    for nom_coll in noms_coll:
        coll = marquer(bpy.data.collections.new(nom_coll))
        scene.collection.children.link(coll)
        collections[nom_coll] = coll

    # Matériaux : une seule fois chacun.
    materiaux, logo_img = {}, None
    for nom_mat, spec in MATERIAUX.items():
        materiaux[nom_mat], img = creer_materiau(nom_mat, spec, dossier_textures)
        if nom_mat == "MAT_Logo":
            logo_img = img
    for l in lignes:
        if l["materiau"] and l["materiau"] not in materiaux:
            avertir("matériau absent du brief, créé en gris : " + l["materiau"])
            materiaux[l["materiau"]], _ = creer_materiau(
                l["materiau"], dict(couleur="#808080", texture="optionnelle", tuile=1.0), dossier_textures)
    if logo_img is None:
        avertir("logo absent : plans du logo en couleur crème, dimensions du CSV")
    else:
        log("logo %d x %d px, ratio %.3f" % (logo_img.size[0], logo_img.size[1],
                                             logo_img.size[0] / logo_img.size[1]))

    # Objets : un par ligne.
    par_id = {}
    for l in lignes:
        try:
            ob = construire_ligne(l, collections, materiaux, logo_img)
        except Exception:
            erreur("ligne %s (%s) :\n%s" % (l["id"], l["nom"], traceback.format_exc()))
            continue
        if ob is not None:
            par_id[l["id"]] = ob
            RAPPORT["objets_csv"] += 1

    # Portes : vantail (et ses cadres) enfant du pivot indiqué dans notes (« enfant de 030 »).
    for l in lignes:
        m = re.search(r"enfant de (\d+)", l["notes"], re.IGNORECASE)
        if not m or l["id"] not in par_id:
            continue
        pivot = par_id.get(m.group(1).zfill(3)) or par_id.get(m.group(1))
        if pivot is None:
            erreur("%s : pivot %s introuvable" % (l["nom"], m.group(1)))
            continue
        parenter(par_id[l["id"]], pivot)

    bpy.context.view_layer.update()
    return dossier


def rapport_texte(chemin_blend):
    r = RAPPORT
    lignes = ["=" * 64, "RAPPORT Marin'Or Ivoire", "=" * 64]
    lignes.append("Objets créés (lignes du CSV) : %d" % r["objets_csv"])
    lignes.append("Objets annexes (lampes des spots, suspensions, dalles et lécheurs) : %d" % r["objets_annexes"])
    lignes.append("Total : %d" % (r["objets_csv"] + r["objets_annexes"]))
    lignes.append("Textures chargées (%d) : %s" % (len(r["textures_chargees"]), ", ".join(r["textures_chargees"]) or "aucune"))
    requises = [f for f, t in r["textures_manquantes"] if t == "requise"]
    optionnelles = [f for f, t in r["textures_manquantes"] if t == "optionnelle"]
    lignes.append("Textures manquantes indispensables (%d) : %s" % (len(requises), ", ".join(requises) or "aucune"))
    lignes.append("Textures optionnelles absentes, couleur de secours (%d) : %s"
                  % (len(optionnelles), ", ".join(optionnelles) or "aucune"))
    lignes.append("Avertissements (%d)" % len(r["avertissements"]))
    lignes += ["  - " + a for a in r["avertissements"]]
    lignes.append("Erreurs (%d)" % len(r["erreurs"]))
    lignes += ["  - " + e for e in r["erreurs"]]
    lignes.append("Fichier : " + (chemin_blend or "NON ENREGISTRÉ"))
    lignes.append("=" * 64)
    return "\n".join(lignes)


def enregistrer(dossier):
    chemin = os.path.join(dossier, BLEND_NAME)
    bpy.ops.wm.save_as_mainfile(filepath=chemin)
    # Le .blend est maintenant dans le dossier : chemins des textures en relatif.
    if TEXTURES_DIR.startswith("//"):
        for img in bpy.data.images:
            if img.get(TAG) and not img.filepath.startswith("//"):
                img.filepath = bpy.path.relpath(img.filepath)
        bpy.ops.wm.save_mainfile()
    return chemin


def main():
    for cle in RAPPORT:
        RAPPORT[cle] = 0 if isinstance(RAPPORT[cle], int) else []
    dossier, chemin_blend = None, None
    try:
        dossier = construire()
    except Exception:
        erreur("construction interrompue :\n" + traceback.format_exc())

    if dossier:
        # Rapport aussi dans un texte Blender, plus simple à copier que la console.
        texte = marquer(bpy.data.texts.new("Rapport_Marinor"))
        texte.write(rapport_texte(os.path.join(dossier, BLEND_NAME)))
        try:
            chemin_blend = enregistrer(dossier)
        except Exception:
            erreur("enregistrement impossible :\n" + traceback.format_exc())

    print("\n" + rapport_texte(chemin_blend) + "\n")


main()
