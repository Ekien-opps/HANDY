"""
Panneau publicitaire 3D (monopied) avec l'affiche Marin'Or Ivoire.

Le cadre est dimensionné à partir du ratio réel de l'affiche (2000 x 1181 px),
il n'y a donc ni déformation ni rognage du visuel.

Utilisation :
    blender -b -P build_billboard.py -- [--render]
    # ou, avec le module Python bpy :
    python build_billboard.py [--render]

Produit, dans le dossier de ce script :
    panneau_marinor.blend   scène complète (texture empaquetée dans le .blend)
    panneau_marinor.glb     export glTF (géométrie + affiche)
    renders/*.png           aperçus Cycles (avec --render)
"""

import math
import os
import sys

import bpy  # doit précéder bmesh avec le module bpy autonome
import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
POSTER_PATH = os.path.join(HERE, "textures", "affiche_marinor_ivoire.png")

# --- Dimensions (mètres) -----------------------------------------------------
POSTER_PX = (2000, 1181)                  # taille de l'affiche fournie
POSTER_H = 3.00                           # hauteur visible de l'affiche
POSTER_W = POSTER_H * POSTER_PX[0] / POSTER_PX[1]   # ~5.08 m, même ratio
FRAME_W = 0.13                            # largeur de la moulure du cadre
FRAME_DEPTH = 0.28                        # profondeur du caisson
CLEARANCE = 3.60                          # hauteur sol -> bas du cadre
COLUMN = (0.85, 0.50)                     # section du pied (x, y)
SEAM_GAP = 0.0015                         # joint entre les profilés

OUTER_W = POSTER_W + 2 * FRAME_W
OUTER_H = POSTER_H + 2 * FRAME_W
PANEL_Z = CLEARANCE + OUTER_H / 2          # centre du panneau

# --- Lumière -----------------------------------------------------------------
SUN_ELEV = 52          # degrés au-dessus de l'horizon
SUN_AZIM = 215         # 0 = derrière le panneau (+Y), 180 = côté rue (-Y)
SUN_STRENGTH = 4.0
SKY_STRENGTH = 0.35


def sun_direction():
    """Vecteur unitaire du sol vers le soleil."""
    e, a = math.radians(SUN_ELEV), math.radians(SUN_AZIM)
    return Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e),
                   math.sin(e)))


# --- Utilitaires -------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = "METRIC"
    s.unit_settings.scale_length = 1.0


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def mesh_object(name, bm, col, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    if mat:
        me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = smooth
    return ob


def add_bevel(ob, width=0.006, segments=2):
    m = ob.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(35)
    m.harden_normals = True
    ob.data.polygons.foreach_set("use_smooth", [True] * len(ob.data.polygons))
    if hasattr(ob.data, "use_auto_smooth"):
        ob.data.use_auto_smooth = True
    return m


def box(name, col, size, loc, mat=None, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    ob = mesh_object(name, bm, col, mat)
    if bevel:
        add_bevel(ob, bevel)
    return ob


def cylinder(name, col, p0, p1, radius, mat=None, segments=24):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments,
                          radius1=radius, radius2=radius, depth=d.length)
    ob = mesh_object(name, bm, col, mat, smooth=True)
    ob.location = (p0 + p1) / 2
    ob.rotation_mode = "QUATERNION"
    ob.rotation_quaternion = d.to_track_quat("Z", "Y")
    return ob


# --- Matériaux ---------------------------------------------------------------
def node_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    return m, nt, bsdf


def mat_poster():
    m, nt, bsdf = node_mat("Affiche_MarinOr")
    n, l = nt.nodes, nt.links
    img = bpy.data.images.load(POSTER_PATH)
    img.colorspace_settings.name = "sRGB"
    tex = n.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "EXTEND"
    tex.interpolation = "Cubic"
    tex.location = (-600, 200)
    l.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    # Papier/vinyle d'affichage : satiné, grain très léger
    bsdf.inputs["Roughness"].default_value = 0.42
    bsdf.inputs["Specular IOR Level"].default_value = 0.45
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 900.0
    noise.inputs["Detail"].default_value = 4.0
    noise.location = (-600, -200)
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.04
    bump.inputs["Distance"].default_value = 0.0005
    bump.location = (-300, -200)
    l.new(noise.outputs["Fac"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def mat_painted(name, color, rough=0.35, grime=0.10):
    """Tôle d'aluminium laquée avec légère salissure dans les creux (AO)."""
    m, nt, bsdf = node_mat(name)
    n, l = nt.nodes, nt.links
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Coat Weight"].default_value = 0.15
    ao = n.new("ShaderNodeAmbientOcclusion")
    ao.inputs["Distance"].default_value = 0.25
    ao.location = (-700, 300)
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 6.0
    noise.inputs["Detail"].default_value = 8.0
    noise.location = (-700, 0)
    mix_ao = n.new("ShaderNodeMath")
    mix_ao.operation = "MULTIPLY"
    mix_ao.location = (-450, 150)
    l.new(ao.outputs["AO"], mix_ao.inputs[0])
    l.new(noise.outputs["Fac"], mix_ao.inputs[1])
    ramp = n.new("ShaderNodeValToRGB")
    ramp.location = (-250, 150)
    dirty = [c * 0.78 for c in color[:3]] + [1.0]
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = dirty
    ramp.color_ramp.elements[1].position = 1.0 - grime
    ramp.color_ramp.elements[1].color = color
    # Le facteur va de 0 (creux/sale) à ~0.6 (propre) : on le remappe
    remap = n.new("ShaderNodeMapRange")
    remap.inputs["From Max"].default_value = 0.55
    remap.location = (-450, -50)
    l.new(mix_ao.outputs[0], remap.inputs["Value"])
    l.new(remap.outputs["Result"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def mat_metal(name, color, rough=0.45, metallic=1.0):
    m, nt, bsdf = node_mat(name)
    n, l = nt.nodes, nt.links
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 25.0
    noise.inputs["Detail"].default_value = 10.0
    rng = n.new("ShaderNodeMapRange")
    rng.inputs["To Min"].default_value = rough - 0.12
    rng.inputs["To Max"].default_value = rough + 0.12
    l.new(noise.outputs["Fac"], rng.inputs["Value"])
    l.new(rng.outputs["Result"], bsdf.inputs["Roughness"])
    return m


def mat_simple(name, color, rough=0.5, metallic=0.0, emit=None, transmission=0.0):
    m, nt, bsdf = node_mat(name)
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Transmission Weight"].default_value = transmission
    if emit:
        bsdf.inputs["Emission Color"].default_value = emit[0]
        bsdf.inputs["Emission Strength"].default_value = emit[1]
    return m


def mat_concrete():
    m, nt, bsdf = node_mat("Beton")
    n, l = nt.nodes, nt.links
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 12.0
    noise.inputs["Detail"].default_value = 12.0
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.36, 0.35, 0.33, 1)
    ramp.color_ramp.elements[1].color = (0.58, 0.56, 0.52, 1)
    l.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    l.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.25
    l.new(noise.outputs["Fac"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def mat_pavement():
    """Pavés autobloquants poussiéreux, comme sur la photo de référence."""
    m, nt, bsdf = node_mat("Paves")
    n, l = nt.nodes, nt.links
    coord = n.new("ShaderNodeTexCoord")
    brick = n.new("ShaderNodeTexBrick")
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Brick Width"].default_value = 0.20
    brick.inputs["Row Height"].default_value = 0.10
    brick.inputs["Mortar Size"].default_value = 0.006
    brick.inputs["Mortar Smooth"].default_value = 0.3
    brick.inputs["Color1"].default_value = (0.22, 0.20, 0.18, 1)
    brick.inputs["Color2"].default_value = (0.28, 0.25, 0.22, 1)
    brick.inputs["Mortar"].default_value = (0.14, 0.12, 0.10, 1)
    brick.offset = 0.5
    l.new(coord.outputs["Object"], brick.inputs["Vector"])
    dirt = n.new("ShaderNodeTexNoise")
    dirt.inputs["Scale"].default_value = 0.35
    dirt.inputs["Detail"].default_value = 10.0
    l.new(coord.outputs["Object"], dirt.inputs["Vector"])
    dirt_ramp = n.new("ShaderNodeValToRGB")
    dirt_ramp.color_ramp.elements[0].position = 0.45
    dirt_ramp.color_ramp.elements[1].position = 0.65
    l.new(dirt.outputs["Fac"], dirt_ramp.inputs["Fac"])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["B"].default_value = (0.36, 0.25, 0.16, 1)   # latérite
    l.new(dirt_ramp.outputs["Color"], mix.inputs["Factor"])
    l.new(brick.outputs["Color"], mix.inputs["A"])
    l.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.invert = True
    l.new(brick.outputs["Fac"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


# --- Géométrie ---------------------------------------------------------------
# Profil de la moulure : (retrait u depuis le bord extérieur, profondeur y).
# y < 0 vers l'avant (côté rue). Polygone fermé : face avant plate, chanfrein
# à 45° qui descend jusqu'au plan de l'affiche, puis retour en caisson.
FRAME_PROFILE = [
    (0.000, FRAME_DEPTH),
    (0.000, -0.045),
    (0.060, -0.045),
    (FRAME_W, -0.005),
    (FRAME_W, 0.030),
    (0.035, 0.030),
    (0.035, FRAME_DEPTH),
]


def frame_piece(name, col, mat, side, t0, t1):
    """Profilé à coupe d'onglet. side: 'top'|'bottom'|'left'|'right'.
    t0/t1 : extrémités le long du profilé, en fraction -1..1 ; aux coins
    (|t|==1) la coupe suit la diagonale."""
    A, B = OUTER_W / 2, OUTER_H / 2
    bm = bmesh.new()
    loops = []
    for t in (t0, t1):
        ring = []
        for u, y in FRAME_PROFILE:
            if side in ("top", "bottom"):
                half = A - u
                z = (B - u) * (1 if side == "top" else -1)
                x = half * t if abs(t) == 1 else A * t
                ring.append(bm.verts.new((x, y, PANEL_Z + z)))
            else:
                half = B - u
                x = (A - u) * (1 if side == "right" else -1)
                z = half * t if abs(t) == 1 else B * t
                ring.append(bm.verts.new((x, y, PANEL_Z + z)))
        loops.append(ring)
    k = len(FRAME_PROFILE)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((loops[0][i], loops[0][j], loops[1][j], loops[1][i]))
    bm.faces.new(loops[0])
    bm.faces.new(list(reversed(loops[1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # Joint visible entre les profilés (léger retrait vers le centre du profilé)
    center = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
    axis = Vector((1, 0, 0)) if side in ("top", "bottom") else Vector((0, 0, 1))
    for v in bm.verts:
        s = 1 if (v.co - center).dot(axis) > 0 else -1
        v.co -= axis * s * SEAM_GAP
    ob = mesh_object(name, bm, col, mat)
    add_bevel(ob, 0.004, 2)
    return ob


def build_frame(col, m_frame):
    # Comme sur la photo : traverses haute et basse en deux éléments.
    frame_piece("Cadre_Haut_G", col, m_frame, "top", -1, 0)
    frame_piece("Cadre_Haut_D", col, m_frame, "top", 0, 1)
    frame_piece("Cadre_Bas_G", col, m_frame, "bottom", -1, 0)
    frame_piece("Cadre_Bas_D", col, m_frame, "bottom", 0, 1)
    frame_piece("Cadre_Gauche", col, m_frame, "left", -1, 1)
    frame_piece("Cadre_Droit", col, m_frame, "right", -1, 1)


def build_poster(col, m_poster):
    w, h = POSTER_W / 2, POSTER_H / 2
    # légèrement plus grand que l'ouverture : les bords passent sous la moulure
    m = 0.01
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    vs = [bm.verts.new((x, 0.0, PANEL_Z + z)) for x, z in
          ((-w - m, -h - m), (w + m, -h - m), (w + m, h + m), (-w - m, h + m))]
    f = bm.faces.new(vs)
    # UV calées sur la zone visible : l'affiche entière reste visible
    for loop in f.loops:
        x, z = loop.vert.co.x, loop.vert.co.z - PANEL_Z
        loop[uv].uv = ((x + w) / (2 * w), (z + h) / (2 * h))
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=8, use_grid_fill=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    # face orientée vers -Y (la rue)
    for face in bm.faces:
        if face.normal.y > 0:
            face.normal_flip()
    ob = mesh_object("Affiche", bm, col, m_poster)
    return ob


def build_cabinet(col, m_back, m_steel):
    A, B = OUTER_W / 2 - 0.03, OUTER_H / 2 - 0.03
    # Fond du caisson (derrière l'affiche)
    box("Caisson_Fond", col, (2 * A, 0.02, 2 * B), (0, 0.035, PANEL_Z), m_back)
    # Tôle arrière
    box("Caisson_Dos", col, (2 * A, 0.015, 2 * B),
        (0, FRAME_DEPTH - 0.01, PANEL_Z), m_back)
    # Raidisseurs horizontaux + montants (tubes rectangulaires galvanisés)
    for i, fz in enumerate((-0.33, 0.0, 0.33)):
        box(f"Raidisseur_H{i}", col, (2 * A - 0.1, 0.08, 0.08),
            (0, FRAME_DEPTH + 0.04, PANEL_Z + fz * POSTER_H), m_steel, 0.006)
    for i, fx in enumerate((-0.42, -0.14, 0.14, 0.42)):
        box(f"Montant_V{i}", col, (0.08, 0.06, 2 * B - 0.1),
            (fx * POSTER_W, FRAME_DEPTH + 0.11, PANEL_Z), m_steel, 0.006)
    # Poutre centrale qui reçoit le pied
    box("Poutre_Centrale", col, (0.30, 0.25, OUTER_H * 0.75),
        (0, FRAME_DEPTH + 0.26, CLEARANCE + OUTER_H * 0.375), m_steel, 0.01)


def build_column(col, m_column, m_dark, m_concrete):
    cx, cy = COLUMN
    top = CLEARANCE - 0.12
    y0 = FRAME_DEPTH / 2 + 0.05
    # Fût habillé de lames verticales (comme la photo de référence)
    box("Pied_Fut", col, (cx, cy, top), (0, y0, top / 2), m_column, 0.06)
    for i, fx in enumerate((-0.17, 0.17)):
        for j, side in enumerate((-1, 1)):
            box(f"Pied_Rainure_{i}{j}", col, (0.012, 0.01, top - 0.15),
                (fx * cx, y0 + side * (cy / 2 + 0.001), top / 2), m_dark)
    # Col de liaison sous le panneau
    box("Pied_Col", col, (0.30, 0.25, 0.20), (0, y0, top + 0.10), m_column, 0.02)
    # Platine + massif béton
    box("Pied_Platine", col, (cx + 0.18, cy + 0.18, 0.03),
        (0, y0, 0.135), m_column, 0.005)
    box("Massif_Beton", col, (1.3, 1.1, 0.24), (0, y0, 0.0), m_concrete, 0.03)


def build_lights(col, m_steel, m_lamp, m_glass):
    """Trois projecteurs en pied de panneau, éclairant l'affiche vers le haut."""
    zb = CLEARANCE
    for i, fx in enumerate((-0.33, 0.0, 0.33)):
        x = fx * POSTER_W
        cylinder(f"Projecteur_Bras{i}", col, (x, 0.12, zb + 0.05),
                 (x, -0.95, zb - 0.12), 0.025, m_steel)
        head = box(f"Projecteur_Corps{i}", col, (0.34, 0.09, 0.18),
                   (0, 0, 0), m_lamp, 0.015)
        glass = box(f"Projecteur_Vitre{i}", col, (0.30, 0.01, 0.14),
                    (0, -0.046, 0), m_glass)
        for ob in (head, glass):
            ob.location = (x, -1.02, zb - 0.16)
            ob.rotation_euler = (math.radians(-120), 0, 0)
        # Lumière nocturne (désactivée au rendu de jour)
        ld = bpy.data.lights.new(f"Projecteur_Spot{i}", "SPOT")
        ld.energy = 1200
        ld.spot_size = math.radians(95)
        ld.spot_blend = 0.6
        ld.color = (1.0, 0.95, 0.88)
        lo = bpy.data.objects.new(f"Projecteur_Spot{i}", ld)
        lo.location = (x, -1.10, zb - 0.10)
        lo.rotation_euler = (math.radians(150), 0, 0)
        lo.hide_render = True
        lo.hide_viewport = True
        col.objects.link(lo)


def mat_foliage():
    m, nt, bsdf = node_mat("Feuillage")
    n, l = nt.nodes, nt.links
    noise = n.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0
    noise.inputs["Detail"].default_value = 12.0
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.020, 0.055, 0.015, 1)
    ramp.color_ramp.elements[1].color = (0.10, 0.20, 0.035, 1)
    l.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    # Perspective atmosphérique : le feuillage bleuit avec la distance
    cam = n.new("ShaderNodeCameraData")
    haze = n.new("ShaderNodeMath")
    haze.operation = "MULTIPLY"
    haze.inputs[1].default_value = -1.0 / 700.0
    l.new(cam.outputs["View Distance"], haze.inputs[0])
    expo = n.new("ShaderNodeMath")
    expo.operation = "EXPONENT"
    l.new(haze.outputs[0], expo.inputs[0])
    mix = n.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (0.22, 0.28, 0.34, 1)
    l.new(expo.outputs[0], mix.inputs["Factor"])
    l.new(ramp.outputs["Color"], mix.inputs["B"])
    l.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.75
    bsdf.inputs["Subsurface Weight"].default_value = 0.15
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.9
    leaf = n.new("ShaderNodeTexVoronoi")
    leaf.inputs["Scale"].default_value = 1.6
    l.new(leaf.outputs["Distance"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def build_trees(col):
    """Rideau d'arbres tropicaux en arrière-plan (géométrie procédurale)."""
    from mathutils import noise
    import random
    rnd = random.Random(7)
    m_leaf = mat_foliage()
    m_bark = mat_simple("Ecorce", (0.09, 0.07, 0.05, 1), 0.9)
    i = 0
    for ring_r, count in ((105, 70), (135, 80)):
        bm = bmesh.new()
        for k in range(count):
            a = math.radians(360 * (k + rnd.random() * 0.7) / count)
            r = ring_r + rnd.uniform(-10, 10)
            x, y = r * math.sin(a), r * math.cos(a)
            h = rnd.uniform(9, 18)
            cylinder(f"Arbre_Tronc{i}", col, (x, y, 0), (x, y, h * 0.6),
                     rnd.uniform(0.3, 0.5), m_bark, 8)
            for _ in range(rnd.randint(4, 7)):
                c = Vector((x + rnd.uniform(-4, 4), y + rnd.uniform(-4, 4),
                            h * rnd.uniform(0.6, 1.0)))
                rad = rnd.uniform(3.0, 5.5)
                g = bmesh.ops.create_icosphere(bm, subdivisions=4, radius=rad)
                seed = Vector((rnd.random() * 100, rnd.random() * 100, 0))
                for v in g["verts"]:
                    p = v.co.copy()
                    d = noise.fractal(p * 0.35 + seed, 0.6, 2.0, 5)
                    d += 0.35 * noise.noise(p * 1.4 + seed)
                    v.co = c + p * (1.0 + 0.3 * d) * Vector((1, 1, 0.75))
            i += 1
        mesh_object(f"Lisiere_Arbres_{ring_r}", bm, col, m_leaf, smooth=True)


def build_environment(m_ground):
    col = collection("Environnement")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=400)
    mesh_object("Sol", bm, col, m_ground)
    build_trees(col)

    scene = bpy.context.scene
    world = bpy.data.worlds.new("Ciel_Abidjan")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = "NISHITA"
    sky.sun_disc = False                      # le soleil vient de la lampe
    sky.sun_elevation = math.radians(SUN_ELEV)
    sky.sun_rotation = math.radians(SUN_AZIM)
    sky.altitude = 20
    sky.air_density = 1.0
    sky.dust_density = 0.6
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = SKY_STRENGTH

    # Soleil de fin de matinée, devant-gauche du panneau
    sun = bpy.data.lights.new("Soleil", "SUN")
    sun.energy = SUN_STRENGTH
    sun.angle = math.radians(0.53)
    sun.color = (1.0, 0.96, 0.90)
    so = bpy.data.objects.new("Soleil", sun)
    d = sun_direction()
    so.rotation_mode = "QUATERNION"
    so.rotation_quaternion = (-d).to_track_quat("-Z", "Y")
    col.objects.link(so)
    return col


def build_cameras(target):
    col = collection("Cameras")
    cams = {}
    for name, loc, lens in (
        ("Camera_Face", (-2.2, -13.0, 1.65), 38),
        ("Camera_3-4", (-11.0, -10.5, 2.2), 32),
        ("Camera_Affiche", (0.0, -9.0, PANEL_Z), 50),
        ("Camera_Arriere", (8.5, 11.0, 2.0), 32),
    ):
        cd = bpy.data.cameras.new(name)
        cd.lens = lens
        cd.sensor_width = 36
        ob = bpy.data.objects.new(name, cd)
        ob.location = loc
        con = ob.constraints.new("TRACK_TO")
        con.target = target
        con.track_axis = "TRACK_NEGATIVE_Z"
        con.up_axis = "UP_Y"
        col.objects.link(ob)
        cams[name] = ob
    return cams


def setup_render(scene):
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 96
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1200
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0.0


def build():
    reset_scene()
    scene = bpy.context.scene

    m_poster = mat_poster()
    m_frame = mat_painted("Cadre_Alu_Laque", (0.80, 0.81, 0.82, 1), 0.32)
    m_column = mat_painted("Pied_Laque", (0.78, 0.79, 0.80, 1), 0.38, 0.15)
    m_back = mat_metal("Tole_Galva", (0.62, 0.63, 0.64, 1), 0.5, 0.9)
    m_steel = mat_metal("Acier_Galva", (0.55, 0.56, 0.57, 1), 0.45, 0.9)
    m_dark = mat_simple("Joint_Sombre", (0.05, 0.05, 0.05, 1), 0.7)
    m_lamp = mat_simple("Projecteur_Gris", (0.12, 0.12, 0.13, 1), 0.4, 0.6)
    m_glass = mat_simple("Projecteur_Verre", (0.85, 0.88, 0.9, 1), 0.08,
                         emit=((1.0, 0.95, 0.85, 1), 0.0), transmission=0.0)
    m_concrete = mat_concrete()
    m_ground = mat_pavement()

    panel = collection("Panneau")
    build_poster(panel, m_poster)
    build_frame(panel, m_frame)
    build_cabinet(panel, m_back, m_steel)
    build_column(panel, m_column, m_dark, m_concrete)
    build_lights(panel, m_steel, m_lamp, m_glass)

    build_environment(m_ground)

    target = bpy.data.objects.new("Cible_Camera", None)
    target.location = (0, 0, PANEL_Z - 0.9)
    scene.collection.objects.link(target)
    cams = build_cameras(target)
    cams["Camera_Affiche"].constraints[0].target = None
    cams["Camera_Affiche"].constraints.remove(cams["Camera_Affiche"].constraints[0])
    cams["Camera_Affiche"].rotation_euler = (math.radians(90), 0, 0)
    scene.camera = cams["Camera_Face"]

    setup_render(scene)
    return scene, cams


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    scene, cams = build()

    blend = os.path.join(HERE, "panneau_marinor.blend")
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)
    print("Enregistré :", blend)

    # glTF : uniquement le panneau (le décor procédural ne s'exporte pas)
    for ob in bpy.context.scene.objects:
        ob.select_set(ob.name in bpy.data.collections["Panneau"].all_objects)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(HERE, "panneau_marinor.glb"),
        export_format="GLB", use_selection=True, export_cameras=False,
        export_lights=False, export_apply=True)

    if "--render" in argv:
        out = os.path.join(HERE, "renders")
        os.makedirs(out, exist_ok=True)
        for name in ("Camera_Face", "Camera_3-4", "Camera_Affiche",
                     "Camera_Arriere"):
            scene.camera = cams[name]
            scene.render.filepath = os.path.join(out, name + ".png")
            bpy.ops.render.render(write_still=True)
            print("Rendu :", scene.render.filepath)
        scene.camera = cams["Camera_Face"]
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)

    print(f"Affiche visible : {POSTER_W:.3f} x {POSTER_H:.3f} m "
          f"(ratio {POSTER_W / POSTER_H:.4f}) ; hors-tout cadre : "
          f"{OUTER_W:.3f} x {OUTER_H:.3f} m")


if __name__ == "__main__":
    main()
