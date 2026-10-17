# -*- coding: utf-8 -*-
"""
Diagnostic des personnages (ne modifie rien dans le fichier).

Dans Blender : onglet Scripting > Text > Open > diagnostic_personnages.py > Run Script.
Le résultat s'écrit dans la console (Window > Toggle System Console) et dans le texte
Blender « Diagnostic_Personnages » : le copier en entier (Ctrl+A, Ctrl+C) et l'envoyer.
"""

import bpy

TAG = "marinor_film"
lignes = []


def p(txt=""):
    lignes.append(txt)
    print(txt)


def v3(v):
    return "(%.2f, %.2f, %.2f)" % tuple(v)


def boite_monde(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        oe = o.evaluated_get(dg)
        try:
            me = oe.to_mesh()
        except Exception:
            continue
        M = oe.matrix_world
        pts += [M @ v.co for i, v in enumerate(me.vertices) if i % 5 == 0]
        oe.to_mesh_clear()
    if not pts:
        return None
    mn = [min(q[i] for q in pts) for i in range(3)]
    mx = [max(q[i] for q in pts) for i in range(3)]
    return mn, mx


sc = bpy.context.scene
frame0 = sc.frame_current
p("=" * 70)
p("DIAGNOSTIC PERSONNAGES - fichier : " + bpy.data.filepath)
p("Image courante : %d   Caméra active : %s" % (frame0, sc.camera.name if sc.camera else "aucune"))
p("=" * 70)

armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
p("Squelettes trouvés : %d" % len(armatures))
for arm in armatures:
    cree = bool(arm.get(TAG))
    colls = ", ".join(c.name for c in arm.users_collection) or "aucune"
    enfants = [o for o in bpy.data.objects
               if o.type == 'MESH' and (o.parent == arm or any(m.type == 'ARMATURE' and m.object == arm
                                                               for m in o.modifiers))]
    p("")
    p("--- %s  [%s]" % (arm.name, "créé par le script" if cree else "PAS créé par le script"))
    p("    collection : %s | parent : %s | dans la scène : %s"
      % (colls, arm.parent.name if arm.parent else "aucun", arm.name in sc.objects))
    p("    visible au rendu : %s | échelle locale %s | rotation %s"
      % (not arm.hide_render, v3(arm.scale), v3(arm.rotation_euler)))
    ad = arm.animation_data
    if ad:
        p("    action directe : %s | pistes NLA : %d %s"
          % (ad.action.name if ad.action else "aucune", len(ad.nla_tracks),
             [(t.name, [s.name for s in t.strips]) for t in ad.nla_tracks]))
    else:
        p("    aucune animation")
    p("    maillages liés : %s" % ", ".join("%s%s" % (o.name, "" if not o.hide_render else " (masqué)") for o in enfants))
    for f in (1, 450, 1000):
        sc.frame_set(f)
        hanches = next((b for b in arm.pose.bones if b.name.endswith("Hips")), None)
        h = arm.matrix_world @ hanches.head if hanches else arm.matrix_world.translation
        bb = boite_monde(enfants)
        if bb:
            mn, mx = bb
            p("    image %4d : hanches %s | maillage x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f  (hauteur %.2f m)"
              % (f, v3(h), mn[0], mx[0], mn[1], mx[1], mn[2], mx[2], mx[2] - mn[2]))
        else:
            p("    image %4d : hanches %s | aucun maillage" % (f, v3(h)))

autres = [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(("Ch", "ENV_Agent", "ENV_Perso"))
          and not o.get(TAG)]
p("")
p("Autres maillages ressemblant à des personnages (non créés par le script) : %d" % len(autres))
for o in autres:
    p("    %s | collection %s | position %s | dimensions %s | visible au rendu %s"
      % (o.name, ", ".join(c.name for c in o.users_collection), v3(o.matrix_world.translation),
         v3(o.dimensions), not o.hide_render))
sc.frame_set(frame0)
p("=" * 70)

t = bpy.data.texts.get("Diagnostic_Personnages") or bpy.data.texts.new("Diagnostic_Personnages")
t.clear()
t.write("\n".join(lignes))
