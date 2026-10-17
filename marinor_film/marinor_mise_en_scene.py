# -*- coding: utf-8 -*-
"""
Mise en scène finale du magasin Marin'Or Ivoire (Blender 5.1).

À lancer dans Blender 5.1 sur `marinor_cocody.blend` (Scripting > Ouvrir > Exécuter), ou :
    blender marinor_cocody.blend --background --python marinor_mise_en_scene.py
Le script est relançable : tout ce qu'il crée porte la marque `marinor_film` et est
supprimé au lancement suivant. Il enregistre `marinor_film.blend` dans le même dossier.

Étape 1 - Produits : les 15 produits (dossier `produits/`, un zip OBJ par produit, comme
          dans « Les Produits.zip ») sont rangés par catégorie dans les meubles prévus
          (§3 du brief) : épices à gauche, marinades à droite, essentiels au centre droit,
          frais dans les vitrines réfrigérées, toute la gamme au mur du fond, épices en
          vrac dans les présentoirs à bacs. Étiquettes de rayon, panneaux, cartons de
          réserve et plateaux de dégustation en plus.
Étape 2 - Personnages Mixamo (dossier `personnages/`) : caissière assise (micro-
          animations « Sitting Talking »), deux employés qui marchent dans les rayons,
          un agent de sécurité devant l'entrée.
Étape 3 - Caméra : un plan-séquence de 85 s (24 i/s), portes automatiques, plafond
          escamoté pour la vue de dessus, visite des locaux du personnel, sortie.

Les fichiers absents sont signalés dans le rapport (texte Blender `Rapport_Film`),
sans erreur : la scène est construite avec ce qui est disponible.
"""

import bisect
import glob
import json
import math
import os
import random
import traceback
import zipfile

import bpy
import bmesh
from mathutils import Euler, Matrix, Quaternion, Vector

# =============================================================================
# RÉGLAGES
# =============================================================================

TAG = "marinor_film"
BLEND_SORTIE = "marinor_film.blend"
DOSSIER_PRODUITS = "produits"
DOSSIER_PERSONNAGES = "personnages"
CATALOGUE = "catalogue_produits.json"
SIGNALETIQUE = os.path.join("textures", "signaletique")
GRAINE = 7

FPS = 24
FRAME_FIN = 2040                     # 85 s
RESOLUTION = (1920, 1080)
ECHANTILLONS = 128                   # Cycles, avec débruitage
FLOU_CINETIQUE = True
SORTIE_VIDEO = "//rendu/marinor_film_"
BALANCE_BLANCS_K = 4000.0           # balance des blancs de la caméra (étalonnage), 6500 = neutre

# Mise en rayon
ESPACE_PRODUITS = 0.012              # jeu entre deux produits (m)
RANGS_MAX = 3                        # profondeur de rangement (rangs visibles)
ALEA_ROTATION_DEG = 1.2              # micro-désordre naturel
ALEA_POSITION_M = 0.003

# Personnages : préfixe du fichier Mixamo + mot-clé de l'animation
PERSONNAGES = [
    {"nom": "Caissiere", "prefixe": "Ch41", "anim": "Sitting", "mode": "assis",
     "pos": (15.30, 2.86), "rot_z_deg": 180.0, "z_assise": 0.74},
    {"nom": "Employe_Epices", "prefixe": "Ch12", "anim": "Walking", "mode": "marche",
     "trajet": [(4.6, 4.95), (4.6, 10.05), (7.4, 10.05), (7.4, 4.95)], "depart": 0.15},
    {"nom": "Employe_Essentiels", "prefixe": "Ch28", "anim": "Walking", "mode": "marche",
     "trajet": [(19.4, 5.2), (19.4, 10.05), (16.6, 10.05), (16.6, 5.2)], "depart": 0.55},
    {"nom": "Agent_Securite", "prefixe": "Ch18", "anim": "Idle", "mode": "fixe",
     "pos": (10.15, -0.85), "z": -0.025, "rot_z_deg": 18.0},
]

# Portes (pivot, angle d'ouverture en degrés, [(image début ouverture, image début fermeture)])
PORTES = {
    "Pivot_Porte_entree_G": (90.0, [(300, 470), (1796, 1900)]),
    "Pivot_Porte_entree_D": (-90.0, [(300, 470), (1796, 1900)]),
    "Pivot_Porte_staff": (-90.0, [(1172, 1290)]),
    "Pivot_Porte_pause": (90.0, [(1272, 1420)]),
    "Pivot_Porte_vestiaire": (90.0, [(1356, 1500)]),
    "Pivot_Porte_bureau": (90.0, [(1446, 1590)]),
    "Pivot_Porte_reserve_couloir": (90.0, [(1520, 1700)]),
    "Pivot_Porte_reserve_G": (-90.0, [(1640, 1760)]),
    "Pivot_Porte_reserve_D": (90.0, [(1640, 1760)]),
}
DUREE_PORTE = 26                     # images (≈ 1,1 s, portes automatiques)

# Objets escamotés pendant la vue de dessus (plafond, toit, luminaires encastrés)
PREFIXES_PLAFOND = ("Plafond_interieur", "Toit_dalle", "Acrotere_", "Dalle_", "Lecheur_", "Spot_")

# Caméra : (image, position, cible, focale mm). Spline d'Hermite cadencée sur les images.
CAMERA_CLES = [
    (1,    (-46.0, -128.0, 72.0), (18.0, -6.0, 0.0), 22),     # survol aérien
    (96,   (-8.0, -66.0, 30.0),   (13.0, -2.0, 1.5), 24),
    (192,  (12.0, -22.0, 7.0),    (12.0, 0.0, 2.6), 30),      # zoom sur la boutique
    (264,  (12.0, -13.0, 2.4),    (12.0, 0.0, 2.5), 38),
    (316,  (12.0, -6.0, 1.70),    (12.0, 3.0, 1.5), 30),      # les portes s'ouvrent
    (372,  (12.0, -0.6, 1.65),    (12.6, 6.0, 1.40), 24),     # entrée
    (414,  (12.75, 1.85, 1.60),   (15.0, 3.3, 1.20), 24),
    (450,  (13.80, 3.05, 1.45),   (15.3, 3.15, 1.25), 26),    # au ras de la caisse
    (500,  (14.70, 4.60, 1.50),   (18.8, 4.2, 1.25), 26),
    (588,  (21.40, 4.60, 1.60),   (23.4, 7.4, 1.30), 30),
    (636,  (22.72, 5.55, 1.35),   (23.6, 6.15, 1.15), 35),    # travelling latéral
    (720,  (22.72, 8.05, 1.05),   (23.6, 8.65, 0.95), 35),
    (804,  (22.72, 10.60, 1.40),  (23.6, 11.2, 1.35), 35),
    (852,  (21.30, 10.90, 2.20),  (16.0, 8.0, 1.20), 28),     # élévation
    (900,  (17.00, 9.00, 3.20),   (12.5, 6.5, 0.80), 26),
    (960,  (13.60, 7.10, 12.0),   (12.2, 6.1, 0.00), 28),
    (1020, (12.00, 6.10, 24.5),   (12.0, 6.13, 0.0), 32),     # vue de dessus
    (1080, (12.20, 6.10, 25.0),   (12.2, 6.13, 0.0), 32),
    (1140, (20.00, 10.40, 9.0),   (22.75, 12.6, 1.0), 28),    # descente vers le staff
    (1176, (22.75, 10.00, 2.55),  (22.75, 13.0, 1.4), 24),
    (1218, (22.75, 11.30, 1.60),  (22.75, 13.6, 1.5), 22),
    (1250, (22.55, 12.82, 1.60),  (19.5, 12.9, 1.5), 22),     # couloir
    (1300, (19.70, 12.82, 1.60),  (18.85, 15.0, 1.3), 22),
    (1336, (18.85, 13.25, 1.60),  (20.4, 15.2, 1.1), 22),     # salle de pause
    (1386, (16.70, 12.82, 1.60),  (15.6, 15.0, 1.3), 22),
    (1420, (15.60, 13.20, 1.60),  (16.8, 15.3, 1.2), 22),     # vestiaire
    (1478, (10.70, 12.82, 1.60),  (9.95, 15.0, 1.2), 22),
    (1512, (9.95, 13.25, 1.60),   (11.4, 15.3, 1.0), 22),     # bureau
    (1560, (9.70, 12.85, 1.60),   (6.0, 13.4, 1.4), 22),
    (1610, (7.20, 13.15, 1.70),   (2.6, 14.6, 1.3), 22),      # réserve
    (1662, (7.80, 13.00, 1.65),   (7.8, 9.0, 1.3), 22),
    (1704, (7.80, 11.00, 1.65),   (10.2, 5.0, 1.2), 24),      # retour en salle
    (1764, (10.20, 7.60, 1.70),   (12.0, 0.0, 1.4), 24),
    (1830, (11.70, 2.20, 1.70),   (12.0, -5.0, 1.5), 24),     # sortie par les portes
    (1880, (12.00, -2.60, 1.80),  (12.0, -8.0, 1.6), 24),
    (1950, (10.20, -8.00, 2.60),  (12.0, 0.0, 2.4), 26),      # retournement, façade
    (2040, (12.00, -19.00, 4.60), (12.0, 0.0, 2.5), 30),
]

# =============================================================================
# OUTILS
# =============================================================================

RAPPORT = {"produits": [], "instances": 0, "manquants": [], "avertissements": [], "erreurs": [],
           "personnages": [], "objets": 0, "orientations": []}
COLLS = {}
MATS = {}


def log(msg):
    print("[Film] " + msg)


def avertir(msg):
    RAPPORT["avertissements"].append(msg)
    log("AVERTISSEMENT : " + msg)


def erreur(msg):
    RAPPORT["erreurs"].append(msg)
    log("ERREUR : " + msg)


def marquer(idb):
    idb[TAG] = True
    return idb


def dossier_projet():
    candidats = []
    if bpy.data.filepath:
        candidats.append(os.path.dirname(bpy.data.filepath))
    f = globals().get("__file__")
    if f:
        candidats.append(os.path.dirname(bpy.path.abspath(f)))
    for t in bpy.data.texts:
        if t.filepath:
            candidats.append(os.path.dirname(bpy.path.abspath(t.filepath)))
    candidats.append(os.getcwd())
    for d in candidats:
        if d and os.path.isfile(os.path.join(d, CATALOGUE)):
            return os.path.normpath(d)
    return None


def hex_lin(h, a=1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (a,)


def collection(nom, parent=None):
    if nom in COLLS:
        return COLLS[nom]
    c = marquer(bpy.data.collections.new(nom))
    (parent or bpy.context.scene.collection).children.link(c)
    COLLS[nom] = c
    return c


def objet(nom, data, coll, loc=(0, 0, 0), rot=(0, 0, 0)):
    ob = marquer(bpy.data.objects.new(nom, data))
    ob.location = loc
    ob.rotation_euler = rot
    coll.objects.link(ob)
    RAPPORT["objets"] += 1
    return ob


def nettoyer():
    for ob in list(bpy.data.objects):
        if ob.get(TAG):
            bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections):
        if c.get(TAG):
            bpy.data.collections.remove(c)
    for bloc in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.node_groups,
                 bpy.data.actions, bpy.data.armatures, bpy.data.cameras, bpy.data.texts, bpy.data.curves):
        for idb in list(bloc):
            if idb.get(TAG):
                bloc.remove(idb)
    for ob in bpy.data.objects:                      # animations posées sur des objets existants
        if ob.get(TAG + "_anime"):
            ob.animation_data_clear()
            del ob[TAG + "_anime"]
    for ob in bpy.data.objects:                      # modificateurs posés sur des objets existants
        for m in list(ob.modifiers):
            if m.name.startswith("FILM_"):
                ob.modifiers.remove(m)
    for ob in bpy.data.objects:
        if ob.name.startswith(PREFIXES_PLAFOND):
            ob.hide_render = False
            ob.hide_viewport = False


def mat_existant(nom, secours="#808080"):
    m = bpy.data.materials.get(nom)
    if m is None:
        m = mat_uni(nom + "_film", secours)
    return m


def mat_uni(nom, couleur, rugosite=0.5, metal=0.0, emission=0.0):
    if nom in MATS:
        return MATS[nom]
    m = marquer(bpy.data.materials.new(nom))
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = hex_lin(couleur)
    b.inputs["Roughness"].default_value = rugosite
    b.inputs["Metallic"].default_value = metal
    if emission:
        b.inputs["Emission Color"].default_value = hex_lin(couleur)
        b.inputs["Emission Strength"].default_value = emission
    m.diffuse_color = hex_lin(couleur)
    MATS[nom] = m
    return m


def mat_image(nom, chemin, rugosite=0.45, alpha=False, emission=0.0):
    """Matériau imprimé (étiquette, panneau, carton) : image en couleur de base."""
    if nom in MATS:
        return MATS[nom]
    if not os.path.isfile(chemin):
        avertir("texture absente : " + os.path.basename(chemin))
        return mat_uni(nom, "#f4f1ea", rugosite)
    m = marquer(bpy.data.materials.new(nom))
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(chemin, check_existing=True)
    tex.image = img
    nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])
    if alpha:
        nt.links.new(tex.outputs["Alpha"], b.inputs["Alpha"])
    if emission:
        nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emission
    b.inputs["Roughness"].default_value = rugosite
    MATS[nom] = m
    return m


def boite(nom, dims, coll, loc, mats, rot_z=0.0, uv_faces=True):
    """Pavé centré en `loc` (dims x, y, z), UV 0-1 sur chaque face."""
    me = marquer(bpy.data.meshes.new(nom))
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, calc_uvs=uv_faces)
    bmesh.ops.scale(bm, vec=Vector(dims), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    return objet(nom, me, coll, loc, (0, 0, rot_z))


def plan(nom, largeur, hauteur, coll, loc, rot, mat):
    """Plan (XY, normale +Z), UV 0-1 ; rot = (90°, 0, rz) le dresse face vers -Y tourné de rz."""
    me = marquer(bpy.data.meshes.new(nom))
    l, h = largeur / 2, hauteur / 2
    me.from_pydata([(-l, -h, 0), (l, -h, 0), (l, h, 0), (-l, h, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = c
    me.materials.append(mat)
    return objet(nom, me, coll, loc, rot)


def cylindre(nom, diametre, hauteur, coll, loc, mat, segments=24, rot=(0, 0, 0)):
    me = marquer(bpy.data.meshes.new(nom))
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=diametre / 2,
                          radius2=diametre / 2, depth=hauteur)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = len(p.vertices) == 4
    me.materials.append(mat)
    return objet(nom, me, coll, loc, rot)


def dossier_signaletique(dossier):
    """textures/signaletique à côté du script ; sinon le premier dossier « signaletique »
    contenant des ETQ_*.png trouvé dans le dossier du projet (archive décompressée ailleurs)."""
    prefere = os.path.join(dossier, SIGNALETIQUE)
    if glob.glob(os.path.join(prefere, "ETQ_*.png")):
        return prefere
    for racine, sous, fichiers in os.walk(dossier):
        if racine[len(dossier):].count(os.sep) > 5:
            sous[:] = []
            continue
        if os.path.basename(racine).lower() == "signaletique" and any(f.startswith("ETQ_") for f in fichiers):
            log("signalétique trouvée dans " + racine)
            return racine
    avertir("dossier textures/signaletique introuvable : étiquettes et panneaux en couleur unie")
    return prefere


def lire_csv(dossier):
    import csv
    meubles = {}
    with open(os.path.join(dossier, "elements.csv"), encoding="utf-8") as f:
        for l in csv.DictReader(f):
            meubles[l["nom"]] = l
    return meubles


# =============================================================================
# ÉTAPE 1 : PRODUITS
# =============================================================================

MODELES = {}          # id -> objet modèle normalisé (origine au centre du dessous, avant vers -Y)
POINTS = {}           # id -> [(position monde, rot_z)]


def extraire(dossier, archive, cible):
    zp = os.path.join(dossier, DOSSIER_PRODUITS, archive)
    if not os.path.isfile(zp):
        candidats = glob.glob(os.path.join(dossier, DOSSIER_PRODUITS, "**", archive), recursive=True)
        zp = candidats[0] if candidats else None
    if zp and not os.path.isdir(cible):
        with zipfile.ZipFile(zp) as z:
            z.extractall(cible)
    objs = glob.glob(os.path.join(cible, "**", "*.obj"), recursive=True)
    return objs[0] if objs else None


def importer_produit(dossier, p, coll):
    cible = os.path.join(dossier, DOSSIER_PRODUITS, "_extraits", p["id"])
    chemin = extraire(dossier, p["archive"], cible)
    if chemin is None:
        RAPPORT["manquants"].append(p["archive"])
        avertir("produit absent : " + p["archive"])
        return None
    avant = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=chemin)
    nouveaux = [o for o in bpy.data.objects if o not in avant and o.type == 'MESH']
    if not nouveaux:
        avertir("OBJ vide : " + chemin)
        return None
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in nouveaux:
        o.select_set(True)
    bpy.context.view_layer.objects.active = nouveaux[0]
    if len(nouveaux) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    me = ob.data
    pts = [v.co for v in me.vertices]
    mn = Vector((min(v.x for v in pts), min(v.y for v in pts), min(v.z for v in pts)))
    mx = Vector((max(v.x for v in pts), max(v.y for v in pts), max(v.z for v in pts)))
    centre = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    s = p["hauteur_m"] / max(mx.z - mn.z, 1e-6)
    me.transform(Matrix.Scale(s, 4) @ Matrix.Translation(-centre))
    me.update()
    manuel = p.get("rot_z_deg")
    if manuel is None or str(manuel).lower() == "auto":
        angle, motif = orientation_etiquette(me)
        RAPPORT["orientations"].append("%s : %+.0f° (%s)" % (p["id"], math.degrees(angle), motif))
    else:
        angle = math.radians(float(manuel))
        RAPPORT["orientations"].append("%s : %+.0f° (réglage du catalogue)" % (p["id"], float(manuel)))
    me.transform(Matrix.Rotation(angle, 4, 'Z'))
    me.update()
    ob.name = me.name = "PROD_" + p["id"]
    marquer(ob)
    marquer(me)
    for m in me.materials:
        if m:
            marquer(m)
    for c in list(ob.users_collection):
        c.objects.unlink(ob)
    coll.objects.link(ob)
    ob.location = (0, 0, -100)                      # modèle source, hors champ
    ob.hide_render = True
    co = [v.co for v in me.vertices]
    d = Vector((max(v.x for v in co) - min(v.x for v in co), max(v.y for v in co) - min(v.y for v in co),
                max(v.z for v in co) - min(v.z for v in co)))
    p["_dims"] = (d.x, d.y, d.z)
    RAPPORT["produits"].append("%s (%.3f x %.3f x %.3f m)" % (p["id"], d.x, d.y, d.z))
    return ob


def image_base(mat):
    """Image branchée (directement ou non) sur la couleur de base du matériau."""
    if mat is None or not mat.use_nodes:
        return None
    for n in mat.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            pile, vus = [n.inputs["Base Color"]], set()
            while pile:
                sock = pile.pop()
                for l in sock.links:
                    nd = l.from_node
                    if nd.name in vus:
                        continue
                    vus.add(nd.name)
                    if nd.type == 'TEX_IMAGE' and nd.image is not None:
                        return nd.image
                    pile.extend(nd.inputs)
    for n in mat.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image is not None:
            return n.image
    return None


def orientation_etiquette(me):
    """Angle (autour de Z) qui tourne la face la plus « imprimée » du produit vers l'allée (-Y).
    La face avant d'un emballage porte le logo et la photo : elle est la plus colorée.
    On échantillonne la texture sur les faces verticales, par secteur de 45°."""
    import numpy as np
    rg = random.Random(1)
    me.calc_loop_triangles()
    uv = me.uv_layers.active
    pixels = {}
    for i, m in enumerate(me.materials):
        img = image_base(m)
        if img is not None and img.size[0] > 0:
            try:
                arr = np.empty(img.size[0] * img.size[1] * 4, dtype=np.float32)
                img.pixels.foreach_get(arr)
                pixels[i] = (arr.reshape(img.size[1], img.size[0], 4), img.size)
            except Exception:
                pass
    aire_tot = sum(t.area for t in me.loop_triangles if abs(t.normal.z) < 0.6) or 1.0
    faces = []                                                         # (saturation, aire, normale xy)
    for t in me.loop_triangles:
        nrm = t.normal
        if abs(nrm.z) >= 0.6 or t.area <= 0:
            continue
        sat = None
        if t.material_index in pixels and uv is not None:
            img, (w, h) = pixels[t.material_index]
            uvs = [uv.data[l].uv for l in t.loops]
            vals = []
            for _ in range(max(3, min(400, int(3000 * t.area / aire_tot)))):
                a, b = rg.random(), rg.random()
                if a + b > 1:
                    a, b = 1 - a, 1 - b
                u = uvs[0].x + a * (uvs[1].x - uvs[0].x) + b * (uvs[2].x - uvs[0].x)
                v = uvs[0].y + a * (uvs[1].y - uvs[0].y) + b * (uvs[2].y - uvs[0].y)
                px = img[int((v % 1.0) * (h - 1)), int((u % 1.0) * (w - 1))]
                hi, lo = max(px[:3]), min(px[:3])
                vals.append((hi - lo) / hi if hi > 1e-4 else 0.0)
            sat = sum(vals) / len(vals)
        elif t.material_index < len(me.materials) and me.materials[t.material_index] is not None:
            c = me.materials[t.material_index].diffuse_color
            hi, lo = max(c[:3]), min(c[:3])
            sat = (hi - lo) / hi if hi > 1e-4 else 0.0
        if sat is not None:
            faces.append((sat, t.area, Vector((nrm.x, nrm.y)).normalized()))
    if not faces:
        return 0.0, "pas de faces latérales imprimées, inchangé"
    co = [v.co for v in me.vertices]
    dx = max(v.x for v in co) - min(v.x for v in co)
    dy = max(v.y for v in co) - min(v.y for v in co)
    aire = sum(f[1] for f in faces)
    moy = sum(f[0] * f[1] for f in faces) / aire

    def score(direction):
        sel = [(sat, ai) for sat, ai, n in faces if n.dot(direction) > 0.7]
        a = sum(ai for _, ai in sel)
        return (sum(sat * ai for sat, ai in sel) / a, a) if a > 0.05 * aire else (None, 0.0)

    if max(dx, dy) > 1.35 * min(dx, dy):
        # Emballage plat (doypack, sachet, boîte) : l'étiquette est sur une grande face.
        if dy <= dx:
            cands = [(0.0, Vector((0, -1))), (math.pi, Vector((0, 1)))]
        else:
            cands = [(-math.pi / 2, Vector((1, 0))), (math.pi / 2, Vector((-1, 0)))]
        (a_av, d_av), (a_ar, d_ar) = cands
        s_av, s_ar = score(d_av)[0], score(d_ar)[0]
        if s_av is None or s_ar is None or abs(s_av - s_ar) < 0.03:
            return a_av, "recto et verso semblables : vérifier sur la planche de contrôle"
        return (a_av, "face imprimée détectée") if s_av > s_ar else (a_ar, "face imprimée détectée")
    # Bouteille, pot : direction du centre de l'étiquette (excès de couleur pondéré)
    res = Vector((0.0, 0.0))
    total = 0.0
    for sat, ai, n in faces:
        res += n * (sat - moy) * ai
        total += abs(sat - moy) * ai
    if total < 1e-9 or res.length < 0.3 * total:
        return 0.0, "étiquette tout autour ou peu marquée : vérifier sur la planche de contrôle"
    theta = math.atan2(res.y, res.x)
    angle = -math.pi / 2 - theta
    quart = round(angle / (math.pi / 2)) * (math.pi / 2)
    if abs(angle - quart) < math.radians(15):
        angle = quart
    angle = math.atan2(math.sin(angle), math.cos(angle))
    return angle, "étiquette détectée"


def ajouter(pid, pos, rot_z):
    POINTS.setdefault(pid, []).append((Vector(pos), rot_z))


def remplir(rg, pid, produits, M, x0, x1, y_avant, profondeur, z, h_libre, sens=-1.0, rangs=RANGS_MAX):
    """Range un produit sur une tablette, dans le repère local M du meuble.
    x0..x1 : largeur utile ; y_avant : bord avant ; sens = -1 : avant vers -Y local
    (face classique), +1 : avant vers +Y (dos de gondole). z : dessus de la tablette."""
    p = produits.get(pid)
    if p is None or pid not in MODELES:
        return 0
    w, d, h = p["_dims"]
    if h > h_libre + 1e-3:
        avertir("%s trop haut pour la tablette (%.2f > %.2f m)" % (pid, h, h_libre))
        return 0
    n = max(1, int((x1 - x0 + ESPACE_PRODUITS) // (w + ESPACE_PRODUITS)))
    pas = (x1 - x0) / n
    nr = max(1, min(rangs, int(profondeur // (d + ESPACE_PRODUITS))))
    rot_meuble = M.to_euler().z
    rot = rot_meuble + (0.0 if sens < 0 else math.pi)
    for j in range(nr):
        y = y_avant - sens * (d / 2 + 0.008 + j * (d + ESPACE_PRODUITS))
        for i in range(n):
            x = x0 + pas * (i + 0.5)
            loc = M @ Vector((x + rg.uniform(-ALEA_POSITION_M, ALEA_POSITION_M),
                              y + rg.uniform(-ALEA_POSITION_M, ALEA_POSITION_M), z))
            ajouter(pid, loc, rot + math.radians(rg.uniform(-ALEA_ROTATION_DEG, ALEA_ROTATION_DEG)))
    return n * nr


def matrice_meuble(nom, meubles):
    ob = bpy.data.objects.get(nom)
    if ob is None or nom not in meubles:
        avertir("meuble introuvable : " + nom)
        return None, None
    l = meubles[nom]
    dims = Vector((float(l["dim_x"]), float(l["dim_y"]), float(l["dim_z"])))
    # repère local : origine au sol, au centre du meuble
    M = ob.matrix_world @ Matrix.Translation((0, 0, -dims.z / 2))
    return M, dims


def niveaux_etagere(H):
    """(dessus de tablette, hauteur libre) des étagères murales (tablettes tous les 0,38 m)."""
    z, res = 0.1125, []
    while z < H - 0.3:
        res.append(z + 0.0125)
        z += 0.38
    return [(n, 0.355 if i < len(res) - 1 else H - 0.035 - n) for i, n in enumerate(res)]


def niveaux_gondole(H):
    z, res = 0.1125, []
    while z < H - 0.2:
        res.append(z + 0.0125)
        z += 0.36
    return [(n, 0.335 if i < len(res) - 1 else H - n) for i, n in enumerate(res)]


def niveaux_frigo(H):
    zb, zh = 0.12, H - 0.13
    pas = (zh - zb) / 5
    res = [(zb, pas - 0.01)]
    for k in range(1, 5):
        res.append((zb + k * pas + 0.0075, pas - 0.02 if k < 4 else zh - 0.05 - (zb + k * pas)))
    return res


def etiquette(M, x, y, z, pid, coll, sens=-1.0):
    """Étiquette de rayon 10 x 3 cm sur le porte-étiquettes."""
    mat = mat_image("ETQ_" + pid, os.path.join(DOSSIER_SIGN, "ETQ_%s.png" % pid), 0.35)
    rot = M.to_euler().z + (0.0 if sens < 0 else math.pi)
    loc = M @ Vector((x, y, z))
    plan("Etiquette_%s" % pid, 0.10, 0.03, coll, loc, (math.radians(90), 0, rot), mat)


def mise_en_rayon(produits, meubles):
    rg = random.Random(GRAINE)
    coll_e = collection("FILM_Etiquettes", COLLS["FILM"])
    epices = [p["id"] for p in produits.values() if p["categorie"] == "epices"]

    def bloc_etagere(nom, blocs):
        """blocs : [(fraction début, fraction fin, id)] sur la largeur, mêmes produits sur tous les niveaux."""
        M, dims = matrice_meuble(nom, meubles)
        if M is None:
            return
        L, P, H = dims
        xu0, xu1 = -L / 2 + 0.03, L / 2 - 0.03
        for z, hl in niveaux_etagere(H):
            for a, b, pid in blocs:
                x0 = xu0 + (xu1 - xu0) * a + 0.005
                x1 = xu0 + (xu1 - xu0) * b - 0.005
                remplir(rg, pid, produits, M, x0, x1, -P / 2 + 0.03, P - 0.06, z, hl)
                if pid in MODELES:
                    etiquette(M, (x0 + x1) / 2, -P / 2 - 0.0005, z - 0.0075, pid, coll_e)

    def bloc_gondole(nom, blocs_moins, blocs_plus):
        M, dims = matrice_meuble(nom, meubles)
        if M is None:
            return
        L, P, H = dims
        prof = (P - 0.03) / 2 - 0.01
        xu0, xu1 = -(L - 0.06) / 2 + 0.02, (L - 0.06) / 2 - 0.02
        for z, hl in niveaux_gondole(H):
            for sens, blocs in ((-1.0, blocs_moins), (1.0, blocs_plus)):
                for a, b, pid in blocs:
                    x0 = xu0 + (xu1 - xu0) * a + 0.005
                    x1 = xu0 + (xu1 - xu0) * b - 0.005
                    y_av = sens * (0.015 + prof - 0.005)
                    remplir(rg, pid, produits, M, x0, x1, y_av, prof - 0.02, z, hl, sens=sens)
                    if pid in MODELES:
                        etiquette(M, (x0 + x1) / 2, sens * (0.015 + prof + 0.0105), z - 0.0075, pid, coll_e, sens)

    def bloc_frigo(nom, pids):
        M, dims = matrice_meuble(nom, meubles)
        if M is None:
            return
        L, P, H = dims
        xu0, xu1 = -(L - 0.10) / 2 + 0.01, (L - 0.10) / 2 - 0.01
        for k, (z, hl) in enumerate(niveaux_frigo(H)):
            pid = pids[k % len(pids)]
            remplir(rg, pid, produits, M, xu0, xu1, -(P - 0.15) / 2 + 0.01, P - 0.17, z, hl)

    # Épices : 6 étagères murales gauche, 2 produits par étagère (blocs verticaux)
    ordre = epices + ["bouillon_poulet", "piment", "epice_poulet"]
    for i in range(6):
        bloc_etagere("Etagere_gauche_%d" % (i + 1),
                     [(0.0, 0.5, ordre[2 * i]), (0.5, 1.0, ordre[2 * i + 1])])
    # Épices : 3 gondoles G, 3 blocs par face
    for g in range(3):
        moins = [(k / 3, (k + 1) / 3, epices[(g * 3 + k) % 9]) for k in range(3)]
        plus = [(k / 3, (k + 1) / 3, epices[(g * 3 + k + 4) % 9]) for k in range(3)]
        bloc_gondole("Gondole_G_%d" % (g + 1), moins, plus)
    # Marinades : 5 étagères murales droite
    marinades = ["marinade_poulet", "marinade_poisson", "marinade_mixte"]
    for i in range(5):
        if i in (1, 3):
            bloc_etagere("Etagere_droite_%d" % (i + 1), [(k / 3, (k + 1) / 3, marinades[k]) for k in range(3)])
        else:
            bloc_etagere("Etagere_droite_%d" % (i + 1), [(0.0, 1.0, marinades[(i // 2) % 3])])
    # Essentiels : 3 gondoles D, pâte d'arachide et huile rouge
    for g in range(3):
        bloc_gondole("Gondole_D_%d" % (g + 1),
                     [(0.0, 0.5, "pate_arachide"), (0.5, 1.0, "huile_rouge")],
                     [(0.0, 0.5, "huile_rouge"), (0.5, 1.0, "pate_arachide")])
    # Produits frais : 4 vitrines réfrigérées
    bloc_frigo("Frigo_1", ["marinade_poulet"])
    bloc_frigo("Frigo_2", ["marinade_poisson"])
    bloc_frigo("Frigo_3", ["marinade_mixte"])
    bloc_frigo("Frigo_4", ["puree_ail"])
    # Mur du fond : toute la gamme, par catégorie de gauche à droite
    fond = ([(0.0, 0.5, epices[0]), (0.5, 1.0, epices[1])], [(0.0, 0.5, epices[2]), (0.5, 1.0, epices[3])],
            [(0.0, 0.5, epices[4]), (0.5, 1.0, epices[5])], [(0.0, 0.5, epices[6]), (0.5, 1.0, epices[7])],
            [(0.0, 0.5, epices[8]), (0.5, 1.0, "bouillon_poulet")],
            [(0.0, 1.0, "marinade_poulet")], [(0.0, 1.0, "marinade_poisson")], [(0.0, 1.0, "marinade_mixte")],
            [(0.0, 0.5, "pate_arachide"), (0.5, 1.0, "huile_rouge")], [(0.0, 1.0, "puree_ail")])
    for i, blocs in enumerate(fond):
        bloc_etagere("Etagere_fond_%d" % (i + 1), blocs)


def planche_controle(dossier, produits):
    """Image des 15 produits vus de l'allée, avec leur nom : rendu/controle_etiquettes.png.
    Une étiquette qui ne fait pas face se corrige par rot_z_deg dans le catalogue."""
    if not MODELES:
        return
    sc0 = bpy.context.window.scene if bpy.context.window else bpy.context.scene
    sc = bpy.data.scenes.new("FILM_Controle_etiquettes")
    marquer(sc)
    pas = 0.30
    ids = [pid for pid in produits if pid in MODELES]
    cols = 5
    for k, pid in enumerate(ids):
        x, z = (k % cols) * pas, -(k // cols) * 0.45
        inst = bpy.data.objects.new("CTRL_" + pid, MODELES[pid].data)
        sc.collection.objects.link(inst)
        inst.location = (x, 0, z)
        fc = bpy.data.curves.new("CTRL_TXT_" + pid, 'FONT')
        fc.body = "%s\n%s" % (produits[pid]["nom"], pid)
        fc.size = 0.022
        fc.align_x = 'CENTER'
        t = bpy.data.objects.new("CTRL_TXT_" + pid, fc)
        t.location = (x, -0.10, z - 0.05)
        t.rotation_euler = (math.radians(90), 0, 0)
        sc.collection.objects.link(t)
    cam = bpy.data.objects.new("CTRL_CAM", bpy.data.cameras.new("CTRL_CAM"))
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = cols * pas + 0.1
    sc.collection.objects.link(cam)
    lignes = (len(ids) + cols - 1) // cols
    cam.location = ((cols - 1) * pas / 2, -3.0, 0.10 - (lignes - 1) * 0.45 / 2)
    cam.rotation_euler = (math.radians(90), 0, 0)
    sc.camera = cam
    sc.render.engine = 'BLENDER_WORKBENCH'
    sc.display.shading.light = 'STUDIO'
    sc.display.shading.color_type = 'TEXTURE'
    sc.render.resolution_x, sc.render.resolution_y = 1800, int(1800 * (lignes * 0.45 + 0.05) / (cols * pas + 0.1))
    sc.render.image_settings.file_format = 'PNG'
    sortie = os.path.join(dossier, "rendu", "controle_etiquettes.png")
    os.makedirs(os.path.dirname(sortie), exist_ok=True)
    sc.render.filepath = sortie
    try:
        if bpy.context.window:
            bpy.context.window.scene = sc
        bpy.ops.render.render(write_still=True, scene=sc.name)
        log("planche de contrôle des étiquettes : " + sortie)
        RAPPORT["orientations"].append("Planche de contrôle : rendu/controle_etiquettes.png")
    except Exception:
        avertir("planche de contrôle non rendue :\n" + traceback.format_exc())
    finally:
        if bpy.context.window:
            bpy.context.window.scene = sc0
        for o in list(sc.collection.objects):
            data = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if isinstance(data, (bpy.types.Curve, bpy.types.Camera)):
                (bpy.data.curves if isinstance(data, bpy.types.Curve) else bpy.data.cameras).remove(data)
        bpy.data.scenes.remove(sc)


def instancier_produits():
    """Un objet par produit : nuage de points + Geometry Nodes « Instance on Points »."""
    coll = collection("FILM_Produits_en_rayon", COLLS["FILM"])
    for pid, pts in POINTS.items():
        modele = MODELES.get(pid)
        if modele is None or not pts:
            continue
        me = marquer(bpy.data.meshes.new("RAYON_" + pid))
        me.from_pydata([tuple(p) for p, _ in pts], [], [])
        att = me.attributes.new("rot_z", 'FLOAT', 'POINT')
        att.data.foreach_set("value", [r for _, r in pts])
        ob = objet("RAYON_" + pid, me, coll)
        ng = marquer(bpy.data.node_groups.new("GN_Rayon_" + pid, 'GeometryNodeTree'))
        ng.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        ng.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
        n = ng.nodes
        gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
        iop = n.new("GeometryNodeInstanceOnPoints")
        info = n.new("GeometryNodeObjectInfo")
        info.inputs["Object"].default_value = modele
        info.transform_space = 'ORIGINAL'
        att_n = n.new("GeometryNodeInputNamedAttribute")
        att_n.data_type = 'FLOAT'
        att_n.inputs["Name"].default_value = "rot_z"
        comb = n.new("ShaderNodeCombineXYZ")
        ng.links.new(att_n.outputs["Attribute"], comb.inputs["Z"])
        try:
            e2r = n.new("FunctionNodeEulerToRotation")
            ng.links.new(comb.outputs["Vector"], e2r.inputs[0])
            ng.links.new(e2r.outputs[0], iop.inputs["Rotation"])
        except Exception:
            ng.links.new(comb.outputs["Vector"], iop.inputs["Rotation"])
        ng.links.new(gi.outputs[0], iop.inputs["Points"])
        ng.links.new(info.outputs["Geometry"], iop.inputs["Instance"])
        ng.links.new(iop.outputs["Instances"], go.inputs[0])
        mod = ob.modifiers.new("Rayon", 'NODES')
        mod.node_group = ng
        RAPPORT["instances"] += len(pts)


# -----------------------------------------------------------------------------
# Vrac, dégustation, réserve, signalétique, caisse
# -----------------------------------------------------------------------------

def tas_vrac(nom, coll, centre, cw, cd, z0, hauteur, couleur, graines=False):
    """Monticule d'épice dans un bac : grille déformée en dôme, matériau poudre ou graines."""
    me = marquer(bpy.data.meshes.new(nom))
    nx, ny = 18, 20
    verts, faces = [], []
    rg = random.Random(hash(nom) & 0xffff)
    for j in range(ny + 1):
        for i in range(nx + 1):
            u, v = i / nx * 2 - 1, j / ny * 2 - 1
            du, dv = u - 0.12, v + 0.08                       # sommet légèrement décentré
            r = min(1.0, math.sqrt(du * du * 0.9 + dv * dv) / 1.25)
            bord = max(abs(u), abs(v))
            dome = (1 - r * r) ** 1.2                          # tas versé à la pelle
            hz = hauteur * (0.62 + 0.38 * dome) - 0.012 * bord ** 8
            hz += 0.004 * math.sin(7 * u + 3 * v) + rg.uniform(-0.0025, 0.0025)
            verts.append((u * cw / 2, v * cd / 2, hz))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    me.from_pydata(verts, [], faces)
    for p in me.polygons:
        p.use_smooth = True
    m = marquer(bpy.data.materials.new("VRAC_" + nom))
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    b.inputs["Roughness"].default_value = 0.95
    base = hex_lin(couleur)
    # teinte nuancée (grains plus sombres / plus clairs) : la poudre ne doit pas paraître unie
    var = nt.nodes.new("ShaderNodeTexNoise")
    var.inputs["Scale"].default_value = 35.0
    var.inputs["Detail"].default_value = 8.0
    rampe = nt.nodes.new("ShaderNodeValToRGB")
    rampe.color_ramp.elements[0].color = tuple(c * 0.55 for c in base[:3]) + (1.0,)
    rampe.color_ramp.elements[1].color = tuple(min(1.0, c * 1.15) for c in base[:3]) + (1.0,)
    nt.links.new(var.outputs["Fac"], rampe.inputs["Fac"])
    nt.links.new(rampe.outputs["Color"], b.inputs["Base Color"])
    tex = nt.nodes.new("ShaderNodeTexVoronoi" if graines else "ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 260.0 if graines else 140.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.85 if graines else 0.45
    nt.links.new(tex.outputs["Distance"] if graines else tex.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    me.materials.append(m)
    return objet(nom, me, coll, (centre.x, centre.y, z0))


def pelle_doseuse(nom, coll, loc, mat, rot_z):
    """Pelle à épices en inox : godet ouvert (Ø 7 cm) et manche, inclinée et à demi enfoncée."""
    me = marquer(bpy.data.meshes.new(nom))
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=20, radius1=0.032, radius2=0.035, depth=0.065)
    fond = bmesh.ops.create_circle(bm, segments=20, radius=0.032, cap_ends=True)
    bmesh.ops.translate(bm, vec=(0, 0, -0.0325), verts=fond["verts"])
    manche = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.007, radius2=0.007, depth=0.11)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Y'), verts=manche["verts"])
    bmesh.ops.translate(bm, vec=(0.035 + 0.055, 0, 0.01), verts=manche["verts"])
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(mat)
    ob = objet(nom, me, coll, loc, (0, math.radians(-38), rot_z))
    ob.modifiers.new("Epaisseur", 'SOLIDIFY').thickness = 0.0015
    return ob


def vrac(produits, meubles):
    coll = collection("FILM_Vrac", COLLS["FILM"])
    ordres = (["paprika", "piment", "poudre_crevette", "poudre_poisson",
               "epice_poulet", "epice_poisson", "poudre_djoumble", "graines_akpi"],
              ["piment", "paprika", "epice_poisson", "epice_poulet",
               "graines_akpi", "poudre_djoumble", "poudre_poisson", "bouillon_poulet"])
    inox = mat_uni("Inox_pelle", "#cfd2d4", 0.22, metal=1.0)
    for k in range(2):
        nom = "Presentoir_vrac_%d" % (k + 1)
        M, dims = matrice_meuble(nom, meubles)
        if M is None:
            continue
        L, P, H = dims
        h1 = H - 0.44
        cols = max(1, round(L / 0.5))
        cw, cd, e = L / cols - 0.04, P / 2 - 0.06, 0.015
        for r, (yc, zb) in enumerate(((-P / 4, h1), (P / 4, h1 + 0.30))):
            for i in range(cols):
                pid = ordres[k][r * cols + i]
                p = produits[pid]
                xc = -L / 2 + (i + 0.5) * L / cols
                c = M @ Vector((xc, yc, 0))
                tas_vrac("Vrac_%d_%s" % (k + 1, pid), coll, c, cw - 2 * e - 0.004, cd - 2 * e - 0.004,
                         M.translation.z + zb + e, 0.165, p["couleur"], graines=(pid == "graines_akpi"))
                # chevalet incliné sur le bord avant du bac
                carte = mat_image("VRAC_" + pid, os.path.join(DOSSIER_SIGN, "VRAC_%s.png" % pid))
                pos = M @ Vector((xc, yc - cd / 2 - 0.01, zb + 0.14 + 0.045))
                plan("Chevalet_%d_%s" % (k + 1, pid), 0.12, 0.08, coll, pos,
                     (math.radians(70), 0, M.to_euler().z), carte)
                # pelle doseuse plantée dans le tas
                pelle_doseuse("Pelle_%d_%s" % (k + 1, pid), coll,
                              M @ Vector((xc + cw * 0.22, yc + cd * 0.12, zb + e + 0.15)), inox,
                              M.to_euler().z + 0.7)


def degustation(produits, meubles):
    coll = collection("FILM_Degustation", COLLS["FILM"])
    bois = mat_existant("MAT_Bois_Clair", "#d2b48c")
    blanc = mat_existant("MAT_Sanitaire_Blanc", "#ffffff")
    sauces = ["#a4471f", "#c9781f", "#7f8f2a", "#b3261e"]
    for t in (1, 2):
        M, dims = matrice_meuble("Table_degustation_%d" % t, meubles)
        if M is None:
            continue
        H = dims.z
        boite("Plateau_degustation_%d" % t, (0.62, 0.34, 0.02), coll, M @ Vector((0, 0, H + 0.01)), [bois],
              M.to_euler().z)
        for k, c in enumerate(sauces):
            x = -0.22 + k * 0.147
            cylindre("Ramequin_%d_%d" % (t, k), 0.075, 0.035, coll, M @ Vector((x, 0.0, H + 0.0375)), blanc)
            cylindre("Sauce_%d_%d" % (t, k), 0.066, 0.004, coll, M @ Vector((x, 0.0, H + 0.052)),
                     mat_uni("Sauce_%d" % k, c, 0.15))
        for k, pid in enumerate(["marinade_poulet", "huile_rouge", "pate_arachide"]):
            if pid in MODELES:
                ajouter(pid, M @ Vector((-0.55 + k * 0.55, 0.22, H)), M.to_euler().z + math.radians(-8 + 8 * k))


def reserve(produits, meubles):
    coll = collection("FILM_Reserve", COLLS["FILM"])
    rg = random.Random(GRAINE + 3)
    ids = list(produits)
    mats = {pid: mat_image("CARTON_" + pid, os.path.join(DOSSIER_SIGN, "CARTON_%s.png" % pid), 0.85)
            for pid in ids}
    n = 0
    for i in range(1, 6):
        M, dims = matrice_meuble("Rayonnage_reserve_%d" % i, meubles)
        if M is None:
            continue
        L, P, H = dims
        for k in range(5):
            z = 0.15 + k * (H - 0.18) / 4 + 0.015
            x = -L / 2 + 0.05
            while True:
                w, d, h = rg.choice([(0.40, 0.30, 0.25), (0.36, 0.28, 0.30), (0.45, 0.32, 0.22)])
                if x + w > L / 2 - 0.05:
                    break
                for rang in ((0.0,) if P < 0.5 else (-P / 4 + 0.01, P / 4 - 0.01)):
                    pid = rg.choice(ids)
                    hh = h if k < 4 else h
                    nb = 1 if k < 4 else rg.choice((1, 2, 3))
                    for e in range(nb):
                        boite("Carton_%d_%d_%d" % (i, k, n), (w, d, hh), coll,
                              M @ Vector((x + w / 2, rang, z + hh / 2 + e * hh)), [mats[pid]],
                              M.to_euler().z + math.radians(rg.uniform(-2, 2)))
                        n += 1
                x += w + 0.03
    # Palette de livraison près de la porte de livraison
    bois = mat_uni("Bois_palette", "#b08a5c", 0.85)
    boite("Palette_livraison", (1.2, 0.8, 0.144), coll, (1.85, 13.85, 0.072), [bois])
    for a in range(3):
        for b in range(2):
            for c in range(3 - (a == 2)):
                pid = ids[(a * 5 + b * 3 + c) % len(ids)]
                boite("Carton_palette_%d_%d_%d" % (a, b, c), (0.40, 0.38, 0.28), coll,
                      (1.85 - 0.4 + a * 0.4, 13.85 - 0.19 + b * 0.38, 0.144 + 0.14 + c * 0.28), [mats[pid]],
                      math.radians(rg.uniform(-1.5, 1.5)))
    log("%d cartons en réserve" % (n + 17))


def signaletique():
    coll = collection("FILM_Signaletique", COLLS["FILM"])
    alu = mat_existant("MAT_Alu_Cadre", "#2b2b2b")
    dos = mat_existant("MAT_Mur_Bordeaux", "#7B1421")
    zp = 3.47

    def panneau(nom, fichier, x, y, zc, rot_z, suspendu=True, largeur=1.6, hauteur=0.4):
        mat = mat_image("PANNEAU_" + fichier, os.path.join(DOSSIER_SIGN, "PANNEAU_%s.png" % fichier),
                        0.5, emission=0.25)
        R = Matrix.Rotation(rot_z, 4, 'Z')
        boite("Panneau_%s_support" % nom, (largeur + 0.02, 0.018, hauteur + 0.02), coll, (x, y, zc), [dos], rot_z)
        plan("Panneau_%s_face" % nom, largeur, hauteur, coll, Vector((x, y, zc)) + R @ Vector((0, -0.0095, 0)),
             (math.radians(90), 0, rot_z), mat)
        if suspendu:
            plan("Panneau_%s_dos" % nom, largeur, hauteur, coll, Vector((x, y, zc)) + R @ Vector((0, 0.0095, 0)),
                 (math.radians(90), 0, rot_z + math.pi), mat)
            for s in (-1, 1):
                pz = (zc + hauteur / 2 + zp) / 2
                cylindre("Panneau_%s_cable_%d" % (nom, s), 0.004, zp - zc - hauteur / 2, coll,
                         Vector((x, y, pz)) + R @ Vector((s * largeur * 0.4, 0, 0)), alu, 8)

    panneau("Epices", "epices", 6.0, 7.4, 2.78, 0.0)
    panneau("Essentiels", "essentiels", 18.0, 7.4, 2.78, 0.0)
    panneau("Vrac", "vrac", 12.0, 7.6, 2.78, 0.0, largeur=1.2, hauteur=0.3)
    panneau("Caisses", "caisses", 17.8, 3.75, 2.85, 0.0, largeur=1.4, hauteur=0.35)
    panneau("Degustation", "degustation", 4.9, 1.35, 2.85, 0.0, largeur=1.4, hauteur=0.35)
    panneau("Marinades", "marinades", 23.785, 8.2, 2.62, math.radians(-90), suspendu=False, largeur=2.4, hauteur=0.6)
    panneau("Frais", "frais", 3.5, 11.985, 2.62, 0.0, suspendu=False, largeur=2.4, hauteur=0.6)
    panneau("Gamme", "gamme", 15.6, 11.985, 2.62, 0.0, suspendu=False, largeur=2.4, hauteur=0.6)

    def plaque(nom, x, y, z, rot_z, parent=None):
        mat = mat_image("PLAQUE_" + nom, os.path.join(DOSSIER_SIGN, "PLAQUE_%s.png" % nom), 0.4)
        ob = plan("Plaque_" + nom, 0.30, 0.10, coll, (x, y, z), (math.radians(90), 0, rot_z), mat)
        if parent is not None:
            ob.parent = parent
            ob.matrix_parent_inverse = parent.matrix_world.inverted()
        return ob

    vantail = bpy.data.objects.get("Porte_staff")
    plaque("staff", 22.75, 12.05 - 0.03, 1.55, 0.0, bpy.data.objects.get("Pivot_Porte_staff") if vantail else None)
    plaque("reserve", 7.8, 12.0 - 0.006, 2.42, 0.0)
    yc = 13.5 - 0.006
    for nom, x in (("bureau", 10.75), ("wc", 14.4), ("vestiaire", 16.35), ("pause", 19.65),
                   ("local_technique", 21.65)):
        plaque(nom, x, yc, 1.55, 0.0)


def tabouret_caisse(pos):
    """Tabouret haut de caissière (assise 0,74 m, repose-pieds)."""
    coll = collection("FILM_Caisse", COLLS["FILM"])
    cuir = mat_existant("MAT_Cuir_Bordeaux", "#5c1018")
    alu = mat_existant("MAT_Alu_Cadre", "#2b2b2b")
    x, y = pos
    cylindre("Tabouret_caisse_assise", 0.40, 0.06, coll, (x, y, 0.71), cuir, 32)
    cylindre("Tabouret_caisse_pied", 0.05, 0.68, coll, (x, y, 0.34), alu, 16)
    cylindre("Tabouret_caisse_base", 0.46, 0.02, coll, (x, y, 0.01), alu, 32)
    me = marquer(bpy.data.meshes.new("Tabouret_caisse_repose_pieds"))
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, segments=32, radius=0.20)
    bm.to_mesh(me)
    bm.free()
    ob = objet("Tabouret_caisse_repose_pieds", me, coll, (x, y, 0.30))
    sk = ob.modifiers.new("Epaisseur", 'SKIN')
    for v in me.skin_vertices[0].data:
        v.radius = (0.008, 0.008)
    me.materials.append(alu)


# =============================================================================
# ÉTAPE 2 : PERSONNAGES MIXAMO
# =============================================================================

def fichiers_mixamo(dossier, prefixe):
    fs = glob.glob(os.path.join(dossier, DOSSIER_PERSONNAGES, "**", prefixe + "*.fbx"), recursive=True)
    fs += glob.glob(os.path.join(dossier, DOSSIER_PERSONNAGES, "**", prefixe + "*.FBX"), recursive=True)
    return sorted(set(fs))


def a_un_maillage(chemin):
    with open(chemin, "rb") as f:
        return b"Geometry" in f.read()


def importer_fbx(chemin):
    avant = set(bpy.data.objects)
    actions_avant = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=chemin, use_anim=True, automatic_bone_orientation=False)
    objs = [o for o in bpy.data.objects if o not in avant]
    acts = [a for a in bpy.data.actions if a not in actions_avant]
    for idb in objs + acts:
        marquer(idb)
        if hasattr(idb, "data") and idb.data is not None:
            marquer(idb.data)
    return objs, acts


def courbes(action):
    """FCurves d'une action, API à couches (Blender 4.4+) ou ancienne."""
    res = []
    if hasattr(action, "layers") and len(action.layers):
        for layer in action.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    res.extend(cb.fcurves)
    elif hasattr(action, "fcurves"):
        res.extend(action.fcurves)
    return res


def prefixe_os(arm):
    for b in arm.data.bones:
        if b.name.endswith("Hips"):
            return b.name[:-4]
    return ""


def adapter_action(action, prefixe_cible):
    """Renomme les chemins de os (mixamorigN: -> préfixe du squelette cible)."""
    for fc in courbes(action):
        dp = fc.data_path
        if dp.startswith('pose.bones["'):
            nom = dp.split('"')[1]
            court = nom.split(":")[-1]
            fc.data_path = dp.replace('"%s"' % nom, '"%s%s"' % (prefixe_cible, court))


def vitesse_marche(arm, action):
    """Vitesse (m/image) du pied d'appui, mesurée sur le cycle de marche en place."""
    ad = arm.animation_data_create()
    ad.action = action
    sc = bpy.context.scene
    pied = next((p for p in arm.pose.bones if p.name.endswith("LeftToeBase")), None)
    if pied is None:
        return 0.052
    f0, f1 = (int(v) for v in action.frame_range)
    mesures = []
    prec = None
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        p = arm.matrix_world @ pied.head
        if prec is not None and p.z < 0.03 and prec.z < 0.03:
            mesures.append((p - prec).length)
        prec = p
    ad.action = None
    mesures.sort()
    return mesures[len(mesures) // 2] if mesures else 0.052


def poser_nla(arm, action, debut=1, fin=FRAME_FIN, decalage=0):
    ad = arm.animation_data_create()
    ad.action = None
    piste = ad.nla_tracks.new()
    piste.name = "Mixamo"
    f0, f1 = action.frame_range
    longueur = max(1.0, f1 - f0)
    st = piste.strips.new(action.name, int(debut - decalage), action)
    if hasattr(st, "action_slot") and hasattr(action, "slots") and len(action.slots):
        try:
            st.action_slot = action.slots[0]
        except Exception:
            pass
    st.repeat = math.ceil((fin - debut + decalage + 2) / longueur) + 1
    st.extrapolation = 'HOLD'
    st.blend_type = 'REPLACE'


def chemin_boucle(points, rayon=0.7, pas=0.02):
    """Boucle fermée à coins arrondis, échantillonnée tous les `pas` mètres."""
    pts = [Vector((x, y, 0)) for x, y in points]
    n = len(pts)
    poly = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        u, v = (a - b).normalized(), (c - b).normalized()
        r = min(rayon, (a - b).length / 2, (c - b).length / 2)
        p0, p2 = b + u * r, b + v * r
        for k in range(9):
            t = k / 8
            poly.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * b + t * t * p2)
    res = [poly[0]]
    cumul = [0.0]
    for i in range(1, len(poly) + 1):
        q = poly[i % len(poly)]
        seg = (q - res[-1]).length
        if seg >= pas or i == len(poly):
            res.append(q)
            cumul.append(cumul[-1] + seg)
    return res, cumul


def echantillon(res, cumul, s):
    L = cumul[-1]
    s = s % L
    i = max(1, bisect.bisect_left(cumul, s))
    t = (s - cumul[i - 1]) / max(1e-9, cumul[i] - cumul[i - 1])
    return res[i - 1].lerp(res[i], t)


def points_corps(arm, objs):
    """Sommets du personnage (maillage déformé) en coordonnées monde, ou à défaut les os."""
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        if o.type != 'MESH':
            continue
        oe = o.evaluated_get(dg)
        me = oe.to_mesh()
        M = oe.matrix_world
        pts += [M @ v.co for i, v in enumerate(me.vertices) if i % 3 == 0]
        oe.to_mesh_clear()
    if not pts:
        for pb in arm.pose.bones:
            pts += [arm.matrix_world @ pb.head, arm.matrix_world @ pb.tail]
    return pts


NICHE = {"comptoir": "Comptoir_bar_1", "y_fond": 3.85, "z_haut": 0.70, "demi_largeur": 0.50}


def niche_comptoir(x):
    """Dégagement pour les jambes sous le comptoir côté caissière (poste de travail assis) :
    booléen non destructif sur le comptoir, retiré au prochain lancement."""
    cpt = bpy.data.objects.get(NICHE["comptoir"])
    if cpt is None:
        avertir("comptoir %s introuvable : pas de dégagement pour les jambes" % NICHE["comptoir"])
        return False
    coll = collection("FILM_Caisse", COLLS["FILM"])
    l = NICHE["demi_largeur"]
    dec = boite("Niche_caisse_decoupe", (2 * l, NICHE["y_fond"] - 3.30, NICHE["z_haut"] + 0.02), coll,
                (x, (3.30 + NICHE["y_fond"]) / 2, (NICHE["z_haut"] - 0.02) / 2), [])
    dec.display_type = 'WIRE'
    dec.hide_render = True
    m = cpt.modifiers.new("FILM_Niche_caisse", 'BOOLEAN')
    m.operation = 'DIFFERENCE'
    m.object = dec
    try:
        m.solver = 'EXACT'
    except Exception:
        pass
    return True


def asseoir(ctrl, arm, objs, cfg):
    """Pose la caissière sur le tabouret (dessous des fesses = dessus de l'assise), puis la recule
    juste ce qu'il faut : au-dessus de la niche, rien ne doit dépasser la face du comptoir (y 3,40) ;
    dans la niche, les jambes doivent rester avant son fond."""
    sc = bpy.context.scene
    hanches = next((p for p in arm.pose.bones if p.name.endswith("Hips")), None)
    if hanches is None:
        avertir("caissière : os Hips introuvable, hauteur par défaut")
        ctrl.location.z = cfg["z_assise"] - 0.47
        return
    bas, devant = [], []
    for f in (1, 300, 700, 1100):                       # plusieurs instants de l'animation
        sc.frame_set(f)
        h = arm.matrix_world @ hanches.head
        pts = points_corps(arm, objs)
        bassin = [p for p in pts if (p.xy - h.xy).length < 0.16 and p.z < h.z]
        maillage = any(o.type == 'MESH' for o in objs)
        # sans maillage, on ne connaît que l'articulation de la hanche : la peau est ~9 cm dessous
        bas.append(min(p.z for p in bassin) - (0.0 if maillage else 0.09) if bassin else h.z - 0.12)
        devant.append(pts)
    dz = cfg["z_assise"] - min(bas)
    ctrl.location.z += dz
    niche = niche_comptoir(cfg["pos"][0])
    dy = 0.0
    for pts in devant:
        for p in pts:
            z = p.z + dz
            if z >= 1.04:
                continue                                  # au-dessus du plan de travail
            if niche and z < NICHE["z_haut"] - 0.03 and abs(p.x - cfg["pos"][0]) < NICHE["demi_largeur"] - 0.04:
                limite = NICHE["y_fond"] - 0.04
            else:
                limite = 3.40 - 0.03
            dy = max(dy, p.y - limite)
    if dy > 0:
        ctrl.location.y -= dy
        for ob in bpy.data.objects:
            if ob.name.startswith("Tabouret_caisse_"):
                ob.location.y -= dy
    sc.frame_set(1)
    log("caissière : assise à %.3f m (correction %+.3f), recul %.3f m" % (cfg["z_assise"], dz, dy))


def personnages(dossier):
    coll = collection("FILM_Personnages", COLLS["FILM"])
    sc = bpy.context.scene
    for cfg in PERSONNAGES:
        fichiers = fichiers_mixamo(dossier, cfg["prefixe"])
        peau = [f for f in fichiers if a_un_maillage(f)]
        if not peau:
            avertir("personnage %s : aucun FBX Mixamo avec maillage pour %s dans %s/"
                    % (cfg["nom"], cfg["prefixe"], DOSSIER_PERSONNAGES))
            continue
        anim = [f for f in fichiers if cfg["anim"].lower() in os.path.basename(f).lower()]
        objs, acts = importer_fbx(peau[0])
        arm = next((o for o in objs if o.type == 'ARMATURE'), None)
        if arm is None:
            avertir("pas de squelette dans " + peau[0])
            continue
        for o in objs:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            coll.objects.link(o)
        arm.name = "PERSO_" + cfg["nom"]
        action = None
        if cfg["anim"].lower() in os.path.basename(peau[0]).lower() and acts:
            action = acts[0]
        else:
            src = [f for f in anim if f != peau[0]]
            if src:
                objs2, acts2 = importer_fbx(src[0])
                if acts2:
                    action = acts2[0]
                    adapter_action(action, prefixe_os(arm))
                for o in objs2:
                    bpy.data.objects.remove(o, do_unlink=True)
            elif acts:
                action = acts[0]
                avertir("%s : animation « %s » introuvable, animation du fichier utilisée" % (cfg["nom"], cfg["anim"]))
        if action is None:
            avertir("%s : aucune animation" % cfg["nom"])
            continue
        action.name = "ANIM_" + cfg["nom"]
        action.use_fake_user = True
        # Contrôleur de trajectoire
        ctrl = objet("CTRL_" + cfg["nom"], None, coll)
        ctrl.empty_display_type = 'ARROWS'
        ctrl.empty_display_size = 0.4
        arm.parent = ctrl
        arm.matrix_parent_inverse = Matrix.Identity(4)
        arm.location = (0, 0, 0)
        if cfg["mode"] == "marche":
            v = vitesse_marche(arm, action)
            poser_nla(arm, action, decalage=int(cfg.get("depart", 0) * 32))
            res, cumul = chemin_boucle(cfg["trajet"])
            s0 = cfg.get("depart", 0.0) * cumul[-1]
            prec_ang = None
            for f in range(1, FRAME_FIN + 1):
                s = s0 + (f - 1) * v
                p = echantillon(res, cumul, s)
                q = echantillon(res, cumul, s + 0.35)
                ang = math.atan2(q.y - p.y, q.x - p.x) + math.pi / 2
                if prec_ang is not None:                         # continuité de l'angle
                    while ang - prec_ang > math.pi:
                        ang -= 2 * math.pi
                    while ang - prec_ang < -math.pi:
                        ang += 2 * math.pi
                prec_ang = ang
                ctrl.location = (p.x, p.y, 0.0)
                ctrl.rotation_euler = (0, 0, ang)
                ctrl.keyframe_insert("location", frame=f)
                ctrl.keyframe_insert("rotation_euler", frame=f)
            RAPPORT["personnages"].append("%s : marche %.2f m/s sur %.1f m" % (cfg["nom"], v * FPS, cumul[-1]))
        else:
            poser_nla(arm, action)
            x, y = cfg["pos"]
            z = cfg.get("z", cfg.get("z_assise", 0.47) - 0.47)
            ctrl.location = (x, y, z)
            ctrl.rotation_euler = (0, 0, math.radians(cfg.get("rot_z_deg", 0.0)))
            if cfg["mode"] == "assis":
                tabouret_caisse(cfg["pos"])
                asseoir(ctrl, arm, objs, cfg)
            RAPPORT["personnages"].append("%s : %s en (%.2f, %.2f, z %.2f)"
                                          % (cfg["nom"], cfg["mode"], ctrl.location.x, ctrl.location.y,
                                             ctrl.location.z))
        for o in objs:
            if o.type == 'MESH':
                o.visible_shadow = True


# =============================================================================
# ÉTAPE 3 : PORTES, PLAFOND, CAMÉRA
# =============================================================================

def cle_rot(ob, f, angle, interp='BEZIER'):
    ob.rotation_euler.z = angle
    ob.keyframe_insert("rotation_euler", index=2, frame=f)


def animer_portes():
    for nom, (angle, cycles) in PORTES.items():
        piv = bpy.data.objects.get(nom)
        if piv is None:
            avertir("pivot introuvable : " + nom)
            continue
        piv.animation_data_clear()
        piv[TAG + "_anime"] = True
        base = piv.rotation_euler.z
        cle_rot(piv, 1, base)
        for ouvre, ferme in cycles:
            cle_rot(piv, ouvre, base)
            cle_rot(piv, ouvre + DUREE_PORTE, base + math.radians(angle))
            cle_rot(piv, ferme, base + math.radians(angle))
            cle_rot(piv, ferme + DUREE_PORTE + 8, base)
        for fc in courbes(piv.animation_data.action):
            for k in fc.keyframe_points:
                k.interpolation = 'BEZIER'
                k.easing = 'AUTO'
                k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'


def hermite(cles, f):
    """Spline d'Hermite cadencée sur les images (tangentes de Catmull-Rom non uniformes).
    cles : [(image, valeur)], valeur = tuple (vecteur) ou nombre."""
    fs = [c[0] for c in cles]
    scalaire = not isinstance(cles[0][1], tuple)
    def val(k):
        v = cles[k][1]
        return Vector((v, 0, 0)) if scalaire else Vector(v)
    if f <= fs[0] or f >= fs[-1]:
        v = val(0 if f <= fs[0] else len(cles) - 1)
        return v.x if scalaire else v
    i = bisect.bisect_right(fs, f) - 1
    def tangente(k):
        if k == 0:
            return (val(1) - val(0)) / (fs[1] - fs[0])
        if k == len(cles) - 1:
            return (val(k) - val(k - 1)) / (fs[k] - fs[k - 1])
        return 0.5 * ((val(k + 1) - val(k)) / (fs[k + 1] - fs[k]) + (val(k) - val(k - 1)) / (fs[k] - fs[k - 1]))
    h = fs[i + 1] - fs[i]
    t = (f - fs[i]) / h
    h00, h10 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t
    h01, h11 = -2 * t ** 3 + 3 * t ** 2, t ** 3 - t ** 2
    r = h00 * val(i) + h10 * h * tangente(i) + h01 * val(i + 1) + h11 * h * tangente(i + 1)
    return r.x if scalaire else r


def camera():
    coll = collection("FILM_Camera", COLLS["FILM"])
    cam_d = marquer(bpy.data.cameras.new("CAM_Film"))
    cam_d.sensor_width = 36.0
    cam_d.clip_start = 0.05
    cam_d.clip_end = 3000.0
    cam_d.dof.use_dof = True
    cam_d.dof.aperture_fstop = 4.0
    cam = objet("CAM_Film_Marinor", cam_d, coll)
    cam.rotation_mode = 'QUATERNION'
    k_pos = [(c[0], c[1]) for c in CAMERA_CLES]
    k_cib = [(c[0], c[2]) for c in CAMERA_CLES]
    k_len = [(c[0], float(c[3])) for c in CAMERA_CLES]
    prec_q = None
    traj = []
    for f in range(1, FRAME_FIN + 1):
        p = hermite(k_pos, f)
        t = hermite(k_cib, f)
        lens = hermite(k_len, f)
        d = (t - p)
        dn = d.normalized()
        # repère : axe -Z vers la cible ; « haut » = Z monde, sauf en plongée verticale
        haut = Vector((0, 0, 1))
        vertical = abs(dn.z)
        if vertical > 0.97:
            haut = Vector((0, 1, 0)).lerp(Vector((0, 0, 1)), max(0.0, (0.999 - vertical) / 0.029))
        droite = dn.cross(haut).normalized()
        up = droite.cross(dn).normalized()
        R = Matrix((droite, up, -dn)).transposed()
        q = R.to_quaternion()
        if prec_q is not None and prec_q.dot(q) < 0:
            q.negate()
        prec_q = q
        cam.location = p
        cam.rotation_quaternion = q
        cam_d.lens = lens
        cam_d.dof.focus_distance = max(0.3, d.length)
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_quaternion", frame=f)
        cam_d.keyframe_insert("lens", frame=f)
        cam_d.dof.keyframe_insert("focus_distance", frame=f)
        traj.append(p.copy())
    for idb in (cam, cam_d):
        if idb.animation_data and idb.animation_data.action:
            for fc in courbes(idb.animation_data.action):
                for k in fc.keyframe_points:
                    k.interpolation = 'LINEAR'
    bpy.context.scene.camera = cam
    return traj


def escamoter_plafond(traj):
    """Plafond, toit et luminaires encastrés masqués tant que la caméra est au-dessus (vue de dessus)."""
    haut = [i + 1 for i, p in enumerate(traj) if p.z > 3.30 and 8 < p.x < 24.5 and 0 < p.y < 16.5]
    if not haut:
        return
    debut, fin = min(haut), max(haut) + 1
    n = 0
    for ob in bpy.data.objects:
        if not ob.name.startswith(PREFIXES_PLAFOND) or ob.type not in ('MESH',):
            continue
        ob[TAG + "_anime"] = True
        for f, cache in ((1, False), (debut, True), (fin, False)):
            ob.hide_render = cache
            ob.hide_viewport = cache
            ob.keyframe_insert("hide_render", frame=f)
            ob.keyframe_insert("hide_viewport", frame=f)
        n += 1
    log("plafond escamoté (%d objets) des images %d à %d" % (n, debut, fin))


def regler_rendu(dossier):
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, FRAME_FIN
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = ECHANTILLONS
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = RESOLUTION
    sc.render.resolution_percentage = 100
    sc.render.use_motion_blur = FLOU_CINETIQUE
    sc.render.motion_blur_shutter = 0.5
    sc.render.filepath = SORTIE_VIDEO
    try:
        sc.view_settings.use_white_balance = True
        sc.view_settings.white_balance_temperature = BALANCE_BLANCS_K
    except Exception:
        avertir("balance des blancs indisponible")
    try:
        sc.render.image_settings.media_type = 'VIDEO'
    except Exception:
        pass
    try:
        sc.render.image_settings.file_format = 'FFMPEG'
        sc.render.ffmpeg.format = 'MPEG4'
        sc.render.ffmpeg.codec = 'H264'
        sc.render.ffmpeg.constant_rate_factor = 'HIGH'
    except Exception:
        avertir("sortie vidéo FFMPEG indisponible : images PNG")
        sc.render.image_settings.file_format = 'PNG'


# =============================================================================
# PRINCIPAL
# =============================================================================

DOSSIER_ABS = ""
DOSSIER_SIGN = ""


def rapport_texte(chemin):
    r = RAPPORT
    lignes = ["=" * 64, "RAPPORT Film Marin'Or (mise en scène)", "=" * 64,
              "Produits importés (%d) :" % len(r["produits"])] + ["  - " + p for p in r["produits"]] + [
              "Produits en rayon : %d instances" % r["instances"],
              "Produits manquants (%d) : %s" % (len(r["manquants"]), ", ".join(r["manquants"]) or "aucun"),
              "Orientation des étiquettes :"] + ["  - " + o for o in r["orientations"]] + [
              "Personnages (%d) :" % len(r["personnages"])] + ["  - " + p for p in r["personnages"]] + [
              "Objets créés : %d" % r["objets"],
              "Avertissements (%d)" % len(r["avertissements"])] + ["  - " + a for a in r["avertissements"]] + [
              "Erreurs (%d)" % len(r["erreurs"])] + ["  - " + e for e in r["erreurs"]] + [
              "Durée : %d images à %d i/s (%.1f s)" % (FRAME_FIN, FPS, FRAME_FIN / FPS),
              "Fichier : %s" % chemin, "=" * 64]
    return "\n".join(lignes)


def main():
    global DOSSIER_ABS, DOSSIER_SIGN
    for k in RAPPORT:
        RAPPORT[k] = 0 if isinstance(RAPPORT[k], int) else []
    COLLS.clear()
    MATS.clear()
    MODELES.clear()
    POINTS.clear()
    dossier = dossier_projet()
    if dossier is None:
        erreur("%s introuvable : placez ce script dans le dossier marinor_boutique" % CATALOGUE)
        print(rapport_texte(None))
        return
    DOSSIER_ABS = dossier
    DOSSIER_SIGN = dossier_signaletique(dossier)
    chemin = os.path.join(dossier, BLEND_SORTIE)
    try:
        nettoyer()
        COLLS["FILM"] = collection("FILM_Marinor")
        with open(os.path.join(dossier, CATALOGUE), encoding="utf-8") as f:
            produits = {p["id"]: p for p in json.load(f)["produits"]}
        meubles = lire_csv(dossier)
        coll_m = collection("FILM_Modeles_produits", COLLS["FILM"])
        for p in produits.values():
            ob = importer_produit(dossier, p, coll_m)
            if ob is not None:
                MODELES[p["id"]] = ob
        mise_en_rayon(produits, meubles)
        degustation(produits, meubles)
        instancier_produits()
        vrac(produits, meubles)
        reserve(produits, meubles)
        signaletique()
        personnages(dossier)
        animer_portes()
        escamoter_plafond(camera())
        regler_rendu(dossier)
        planche_controle(dossier, produits)
    except Exception:
        erreur("construction interrompue :\n" + traceback.format_exc())
    texte = marquer(bpy.data.texts.new("Rapport_Film"))
    texte.write(rapport_texte(chemin))
    try:
        bpy.ops.wm.save_as_mainfile(filepath=chemin, relative_remap=True)
    except Exception:
        erreur("enregistrement impossible :\n" + traceback.format_exc())
    print("\n" + rapport_texte(chemin) + "\n")


main()
