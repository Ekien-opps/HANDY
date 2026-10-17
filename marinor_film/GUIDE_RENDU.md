# Guide pas à pas — du script au film MP4 (Blender 5.1, Windows)

Noms de menus en anglais (interface de Blender en anglais).

## 1. Préparer le dossier

Dans `Dossier de travail\`, après avoir copié le contenu du kit (remplacer les anciens fichiers) :

```
marinor_cocody.blend
marinor_mise_en_scene.py      (version 3)
catalogue_produits.json
elements.csv
generer_signaletique.py
textures\signaletique\        (60 .png)
produits\                     (15 MarinOr_..._OBJ.zip)
personnages\                  (tous les .fbx Mixamo)
```

Supprimer le dossier imbriqué `Dossier de travail\marinor_boutique\` s'il existe.

## 2. Construire la scène

1. Ouvrir **`marinor_cocody.blend`**.
2. **Window > Toggle System Console** (fenêtre noire de suivi, la laisser ouverte).
3. Onglet **Scripting**. Dans l'éditeur de texte : **Text > Open** et choisir `marinor_mise_en_scene.py`
   **sur le disque** (pas une ancienne copie enregistrée dans le .blend, du type `marinor_mise_en_scene.py.001`).
   Si un ancien script est déjà ouvert : **Text > Reload** (Alt+R).
4. **Run Script** (Alt+P). Blender semble figé quelques minutes : c'est normal.
5. Le fichier ouvert devient **`marinor_film.blend`** (barre de titre).

**Contrôles :**

- Texte **`Rapport_Film`** (menu déroulant de l'éditeur de texte) : `Erreurs (0)`, `Personnages (4)`,
  `Produits manquants (0)`, pas de « texture absente ».
- Image **`rendu\controle_etiquettes.png`** : les 15 produits vus depuis l'allée. Chaque étiquette doit
  vous faire face. Produit vu de dos : ajouter `"retourner": true` à sa ligne dans
  `catalogue_produits.json` (Bloc-notes) ; vu de profil : remplacer `null` par `90` ou `-90` dans
  `rot_z_deg`. Puis relancer le script (il peut être relancé dans `marinor_film.blend`).

## 3. Carte graphique (une seule fois)

1. **Edit > Preferences > System > Cycles Render Devices** : **OptiX** (NVIDIA RTX), **CUDA**
   (NVIDIA ancienne) ou **HIP** (AMD). Cocher la carte.
2. **Render Properties** (icône appareil photo) : **Device : GPU Compute**.

## 4. Réglages de rendu

**Render Properties**

| Réglage | Valeur |
|---|---|
| Sampling > Render > Noise Threshold | coché, 0.01 |
| Max Samples | 128 |
| Denoise | coché, OpenImageDenoise, Albedo and Normal, Prefilter Accurate, Use GPU |
| Motion Blur | coché, Shutter 0.5 |
| Performance > Final Render > Persistent Data | coché |
| Color Management | AgX, White Balance 4000 K |

**Output Properties** (icône imprimante)

| Réglage | Valeur |
|---|---|
| Resolution | 1920 × 1080, 100 % |
| Frame Rate | 24 |
| Frame Range | 1 à 2040, Step 1 |
| Chemin de sortie | `//rendu/images/marinor_` |
| Media Type / File Format | Image / PNG, RGB, 8 bits, compression 15 % |
| Overwrite | décoché |
| Placeholders | coché |

Rendre une suite d'images plutôt qu'un MP4 direct : en cas d'arrêt, rien n'est perdu et le rendu
reprend où il s'était arrêté. **Ctrl+S** pour enregistrer.

## 5. Images de contrôle (F12)

Caméra active : **Scene Properties > Camera = `CAM_Film_Marinor`**. Pour chaque image, taper le numéro
dans **Current Frame** (Timeline), puis **F12**, puis **Image > Save As** :

| Image | À vérifier |
|---|---|
| 140 | Survol aérien, boutique visible |
| 316 | Portes automatiques qui s'ouvrent |
| 450 | Caissière assise sur le tabouret, à sa caisse |
| 700 | Gros plan marinades : étiquettes face caméra |
| 1050 | Vue de dessus de toute la boutique |
| 1336 | Salle de pause |
| 1610 | Réserve |
| 1860 | Sortie, agent de sécurité |
| 2040 | Plan final sur la façade |

Noter le temps d'une image (« Time » en haut de la fenêtre) × 2040 = durée totale.

Corrections possibles :

- Caissière trop haute / trop basse : en tête de `marinor_mise_en_scene.py`, `"z_assise": 0.74`
  (baisser à 0.72 pour la descendre), puis refaire l'étape 2.
- Rendu trop lent : Max Samples 64.
- Textures roses : **File > External Data > Find Missing Files** sur `Dossier de travail`.

## 6. Rendu final

- Windows : mise en veille sur **Jamais**, portable sur secteur, autres logiciels fermés.
- **Méthode recommandée** (sans interface, plus rapide), dans `cmd` :

```
cd "C:\Users\DELL\Downloads\Projet Marin'Or\tous les travaux\Animation et Conception 3D\Dossier de travail"
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b marinor_film.blend -a
```

  Ctrl+C pour arrêter ; relancer la même commande pour reprendre.
- Ou dans Blender : **Render > Render Animation** (Ctrl+F12).

Vérifier ensuite `rendu\images\` : 2040 fichiers, aucun de 0 Ko.

## 7. Montage du MP4

1. **File > New > Video Editing**.
2. **Add > Image/Sequence** → `rendu\images\`, **A** (tout), **Add Image Strip**.
3. **Output Properties** : 1920 × 1080, 24 i/s, fin 2040, sortie `//rendu/Marinor_Ivoire_Film.mp4`,
   Media Type **Video**, **FFmpeg Video**, **MPEG-4**, **H.264**, qualité **High** (ou
   Perceptually Lossless), Encoding Speed **Slow**.
4. Facultatif : **Add > Sound** (musique), Audio Codec **AAC** 192 kbps.
5. Enregistrer sous `montage.blend`, puis **Render > Render Animation**.

Résultat : `rendu\Marinor_Ivoire_Film.mp4`, 85 s, Full HD.
