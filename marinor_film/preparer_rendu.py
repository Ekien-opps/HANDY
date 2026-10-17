# -*- coding: utf-8 -*-
"""
Prépare marinor_film.blend pour le rendu final (Blender 5.1), en un clic.

Dans Blender, avec marinor_film.blend ouvert : onglet Scripting > Text > Open >
preparer_rendu.py > Run Script. Le compte rendu s'affiche dans la console et dans le
texte Blender « Reglages_Rendu ». Le fichier est enregistré à la fin.

Réglages appliqués :
  - carte graphique : OptiX (NVIDIA RTX), sinon CUDA, sinon processeur ;
  - Cycles, 128 échantillons max, seuil de bruit 0,01, débruitage OpenImageDenoise sur GPU ;
  - Persistent Data (la scène n'est pas rechargée à chaque image) ;
  - flou de mouvement 0,5 (0,25 pendant le travelling sur les étiquettes, réglé par le script de
    mise en scène), AgX, balance des blancs 4000 K ;
  - 1920 x 1080, 24 i/s, images 1 à 2040, caméra CAM_Film_Marinor ;
  - sortie en suite d'images PNG dans rendu/images/ (reprise possible après un arrêt).
"""

import bpy

ECHANTILLONS = 128
SORTIE = "//rendu/images/marinor_"
lignes = []


def p(txt):
    lignes.append(txt)
    print(txt)


def essayer(libelle, action):
    try:
        action()
        p("  ok  " + libelle)
    except Exception as e:
        p("  --  " + libelle + " (non disponible : %s)" % e)


sc = bpy.context.scene
p("=" * 60)
p("RÉGLAGES DU RENDU FINAL")
p("=" * 60)

# 1. Carte graphique
appareil = "processeur (CPU)"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for type_gpu in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
        try:
            prefs.compute_device_type = type_gpu
        except Exception:
            continue
        prefs.get_devices()
        cartes = [d for d in prefs.devices if d.type == type_gpu]
        if cartes:
            for d in prefs.devices:
                d.use = (d.type == type_gpu)
            appareil = "%s : %s" % (type_gpu, ", ".join(d.name for d in cartes))
            break
    bpy.ops.wm.save_userpref()
except Exception as e:
    p("  --  préférences GPU non modifiables : %s" % e)
sc.cycles.device = 'GPU' if not appareil.startswith("processeur") else 'CPU'
p("Carte de rendu : " + appareil)

# 2. Moteur et qualité
sc.render.engine = 'CYCLES'
essayer("échantillons max %d, seuil de bruit 0,01" % ECHANTILLONS,
        lambda: (setattr(sc.cycles, "samples", ECHANTILLONS), setattr(sc.cycles, "use_adaptive_sampling", True),
                 setattr(sc.cycles, "adaptive_threshold", 0.01), setattr(sc.cycles, "adaptive_min_samples", 0),
                 setattr(sc.cycles, "time_limit", 0.0)))
essayer("débruitage OpenImageDenoise (albédo + normales, précis, GPU)",
        lambda: (setattr(sc.cycles, "use_denoising", True), setattr(sc.cycles, "denoiser", 'OPENIMAGEDENOISE'),
                 setattr(sc.cycles, "denoising_input_passes", 'RGB_ALBEDO_NORMAL'),
                 setattr(sc.cycles, "denoising_prefilter", 'ACCURATE')))
essayer("débruitage sur la carte graphique", lambda: setattr(sc.cycles, "denoising_use_gpu", True))
essayer("Persistent Data", lambda: setattr(sc.render, "use_persistent_data", True))

def flou_anime():
    ad = sc.animation_data
    act = ad.action if ad else None
    if act is None:
        return False
    if hasattr(act, "layers") and len(act.layers):
        return any(fc.data_path == "render.motion_blur_shutter" for layer in act.layers
                   for strip in layer.strips for cb in strip.channelbags for fc in cb.fcurves)
    return any(fc.data_path == "render.motion_blur_shutter" for fc in getattr(act, "fcurves", []))


sc.render.use_motion_blur = True
if flou_anime():
    p("  ok  flou de mouvement 0,5 (0,25 pendant le travelling : réglage du script conservé)")
else:
    essayer("flou de mouvement 0,5", lambda: setattr(sc.render, "motion_blur_shutter", 0.5))
essayer("AgX + balance des blancs 4000 K",
        lambda: (setattr(sc.view_settings, "view_transform", 'AgX'),
                 setattr(sc.view_settings, "use_white_balance", True),
                 setattr(sc.view_settings, "white_balance_temperature", 4000.0)))

# 3. Format et images
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.render.fps, sc.render.fps_base = 24, 1.0
sc.frame_start, sc.frame_end, sc.frame_step = 1, 2040, 1
p("  ok  1920 x 1080, 24 i/s, images 1 à 2040")
cam = bpy.data.objects.get("CAM_Film_Marinor")
if cam:
    sc.camera = cam
    p("  ok  caméra active : CAM_Film_Marinor")
else:
    p("  !!  CAM_Film_Marinor introuvable : relancer d'abord marinor_mise_en_scene.py")

# 4. Sortie : suite d'images PNG, reprise possible
sc.render.filepath = SORTIE
essayer("type de sortie : image", lambda: setattr(sc.render.image_settings, "media_type", 'IMAGE'))
img = sc.render.image_settings
img.file_format = 'PNG'
img.color_mode = 'RGB'
img.color_depth = '8'
img.compression = 15
sc.render.use_file_extension = True
sc.render.use_overwrite = False
sc.render.use_placeholder = True
p("  ok  sortie PNG dans %s (Overwrite décoché, Placeholders coché)" % SORTIE)

p("=" * 60)
p("Prêt. Images de contrôle : double-clic sur images_controle.bat (Blender fermé),")
p("ou Render > Render Image sur les images 450, 700 et 1050.")
p("Rendu complet : double-clic sur lancer_rendu.bat (Blender fermé).")
p("=" * 60)
t = bpy.data.texts.get("Reglages_Rendu") or bpy.data.texts.new("Reglages_Rendu")
t.clear()
t.write("\n".join(lignes))
if bpy.data.filepath:
    bpy.ops.wm.save_mainfile()
    p("Fichier enregistré : " + bpy.data.filepath)
