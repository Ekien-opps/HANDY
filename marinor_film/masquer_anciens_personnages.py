# -*- coding: utf-8 -*-
"""
Retire du film les personnages Mixamo importés à la main (Ch12, Ch18, Ch28, Ch41… dans
« Collection »), sans rien supprimer : ils sont déplacés dans une collection
« ANCIENS_personnages_masques » qui est exclue de la scène (ni visibles, ni rendus).

Les 4 personnages du film (collection FILM_Personnages, créés par marinor_mise_en_scene.py)
ne sont pas touchés. Pour annuler : dans l'Outliner, recocher la case de la collection
ANCIENS_personnages_masques.

Dans Blender : onglet Scripting > Text > Open > masquer_anciens_personnages.py > Run Script.
Le compte rendu s'écrit dans la console et dans le texte Blender « Anciens_Personnages ».
"""

import bpy

TAG = "marinor_film"
NOM_COLL = "ANCIENS_personnages_masques"
lignes = []


def p(txt):
    lignes.append(txt)
    print(txt)


def descendants(ob):
    res = []
    for o in bpy.data.objects:
        q = o.parent
        while q is not None:
            if q == ob:
                res.append(o)
                break
            q = q.parent
    return res


sc = bpy.context.scene
coll = bpy.data.collections.get(NOM_COLL)
if coll is None:
    coll = bpy.data.collections.new(NOM_COLL)
    sc.collection.children.link(coll)

# Squelettes Mixamo qui ne viennent pas du script de mise en scène
anciens = [o for o in bpy.data.objects
           if o.type == 'ARMATURE' and not o.get(TAG)
           and any("mixamorig" in b.name.lower() for b in o.data.bones)]
deplaces = []
for arm in anciens:
    groupe = [arm] + descendants(arm)
    # maillages déformés par ce squelette mais rangés à part (pants, hoody… non parentés)
    for o in bpy.data.objects:
        if o.type == 'MESH' and o not in groupe and not o.get(TAG):
            if any(m.type == 'ARMATURE' and m.object == arm for m in o.modifiers):
                groupe.append(o)
    for o in groupe:
        if o.get(TAG):
            continue
        for c in list(o.users_collection):
            if c != coll:
                c.objects.unlink(o)
        if o.name not in coll.objects:
            coll.objects.link(o)
        deplaces.append(o.name)

# Collection exclue de la scène : ni affichée, ni rendue (réversible)
def couche(lc, nom):
    if lc.collection.name == nom:
        return lc
    for enfant in lc.children:
        r = couche(enfant, nom)
        if r:
            return r
    return None

for vl in sc.view_layers:
    lc = couche(vl.layer_collection, NOM_COLL)
    if lc:
        lc.exclude = True
    vl.update()

p("=" * 64)
p("Anciens personnages Mixamo retirés du film : %d squelette(s)" % len(anciens))
for arm in anciens:
    p("  - " + arm.name)
p("Objets déplacés dans %s (exclue de la scène) : %d" % (NOM_COLL, len(deplaces)))
for n in deplaces:
    p("    " + n)
film = [o.name for o in bpy.data.objects if o.type == 'ARMATURE' and o.get(TAG)]
p("Personnages du film conservés : %d %s" % (len(film), film))
p("Pour annuler : recocher la case de la collection %s dans l'Outliner." % NOM_COLL)
p("=" * 64)
t = bpy.data.texts.get("Anciens_Personnages") or bpy.data.texts.new("Anciens_Personnages")
t.clear()
t.write("\n".join(lignes))
