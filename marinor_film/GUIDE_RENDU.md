# Guide pas à pas — du script au film MP4 (Blender 5.1, Windows)

Noms de menus en anglais (interface de Blender en anglais).

## 1. Préparer le dossier

Dans `Dossier de travail\`, après avoir copié le contenu du kit (remplacer les anciens fichiers) :

```
marinor_cocody.blend
marinor_film.blend             (votre fichier : il est mis à jour, pas remplacé)
marinor_mise_en_scene.py       (version 3.5 : ligne 43, VERSION = "3.5")
preparer_rendu.py
images_controle.bat
lancer_rendu.bat
catalogue_produits.json
elements.csv
generer_signaletique.py
textures\signaletique\         (60 .png)
produits\                      (15 MarinOr_..._OBJ.zip)
personnages\                   (tous les .fbx Mixamo)
```

## 2. Mettre à jour la scène

1. Ouvrir **`marinor_film.blend`** (ou `marinor_cocody.blend` pour une toute première fois).
2. **Window > Toggle System Console** (fenêtre noire de suivi, la laisser ouverte).
3. Onglet **Scripting**. Dans l'éditeur de texte : **Text > Open** et choisir `marinor_mise_en_scene.py`
   **sur le disque**. Si l'ancien script est déjà ouvert dans l'éditeur : **Text > Reload** (Alt+R).
   Vérifier la ligne 43 : `VERSION = "3.5"`.
4. **Run Script** (Alt+P). Blender semble figé quelques minutes : c'est normal. Le script remplace ce
   qu'il avait créé (produits, personnages, caméra...) et ne touche pas au reste de la boutique.
5. La barre de titre indique **`marinor_film.blend`** : le fichier est enregistré.

**Contrôles** dans le texte **`Rapport_Film`** (menu déroulant de l'éditeur de texte) :

- `script version 3.5`, `Erreurs (0)`, `Personnages (4)`, `Produits manquants (0)` ;
- chaque personnage : « matières mates » ;
- « Vue de dessus » : les objets escamotés avec le plafond (arbre au-dessus de la boutique) et ce que la
  caméra voit au sol devant les caisses.

Image **`rendu\controle_etiquettes.png`** : les 15 produits vus depuis l'allée, étiquettes face à vous.
Produit vu de dos : ajouter `"retourner": true` à sa ligne dans `catalogue_produits.json` (Bloc-notes) ;
vu de profil : remplacer `null` par `90` ou `-90` dans `rot_z_deg`. Puis relancer le script.

## 3. Réglages du rendu (après chaque passage du script)

Toujours dans **Scripting** : **Text > Open** > `preparer_rendu.py` > **Run Script**. Le texte
**`Reglages_Rendu`** doit indiquer `Carte de rendu : OPTIX : NVIDIA GeForce RTX 4060 Laptop GPU`. Le fichier
est enregistré. Le détail des réglages est à la fin de ce guide.

## 4. Images de contrôle

**Fermer Blender**, puis double-clic sur **`images_controle.bat`**. Une fenêtre noire rend les images
450, 700 et 1050, puis ouvre le dossier `rendu\controle\`. Le temps de chaque image est sur la ligne
`Saved: ... Time: 00:45.60`.

Autre méthode, dans Blender : taper le numéro dans **Current Frame** (Timeline), puis
**Render > Render Image** (F12, ou Fn+F12 sur un portable), puis **Image > Save As**.

| Image | À vérifier |
|---|---|
| 450 | Caissière assise sur le tabouret, vêtements mats (ni vinyle ni métal) |
| 700 | Travelling marinades : étiquettes nettes et lisibles |
| 1050 | Vue de dessus : toute la boutique, sans arbre ni zone sombre au sol |

La première image est plus longue (préparation de la carte graphique et de la scène) : seuls les temps
des images suivantes comptent pour estimer la durée du film.

## 5. Rendu final

**Avant** : portable branché sur secteur, mode de performance maximal (Dell : Alienware Command Center
ou Dell Power Manager > Performance), **Paramètres > Système > Alimentation > Écran et mise en veille** :
« Jamais » sur secteur. Couvercle ouvert, grilles d'aération dégagées. Autres logiciels fermés.

**Lancer** : fermer Blender, double-clic sur **`lancer_rendu.bat`**.

- Ce fichier démarre Blender **sans interface** (`blender.exe -b`) : le rendu se fait dans la fenêtre
  noire. **Ne pas la fermer** ; elle peut être réduite.
- Chaque image terminée affiche `Saved: '...\rendu\images\marinor_0123.png'`. Pendant le calcul, la
  ligne `Fra:123 ... | Time:00:21.43 | Remaining:00:12.10 | ... Sample 64/128` donne l'image en cours,
  le temps passé et le temps restant **pour cette image**.
- Suivi : ouvrir `rendu\images\` dans l'Explorateur. Le nombre d'éléments (en bas à gauche) est le
  nombre d'images faites sur 2 040. Double-clic sur la dernière pour la regarder.
- **Arrêter** : Ctrl+C dans la fenêtre noire, puis `O` et Entrée. **Reprendre** : double-clic sur
  `lancer_rendu.bat`. Les images déjà faites sont gardées et l'image interrompue (fichier de 0 Ko) est
  supprimée puis refaite automatiquement.
- À la fin, la fenêtre affiche `Images rendues : 2040 / 2040`.

Durée : environ 35 à 45 s par image avec la RTX 4060, soit 20 à 25 heures pour 2 040 images (deux
nuits, en plusieurs fois si besoin).

## 6. Montage du MP4

1. Ouvrir Blender, **File > New > Video Editing**.
2. **Add > Image/Sequence** → `rendu\images\`, **A** (tout), **Add Image Strip**.
3. **Output Properties** : 1920 × 1080, 24 i/s, fin 2040, sortie `//rendu/Marinor_Ivoire_Film.mp4`,
   Media Type **Video**, **FFmpeg Video**, **MPEG-4**, **H.264**, qualité **High** (ou
   Perceptually Lossless), Encoding Speed **Slow**.
4. Facultatif : **Add > Sound** (musique), Audio Codec **AAC** 192 kbps.
5. **File > Save As** `montage.blend` dans `Dossier de travail` (nécessaire pour que `//` fonctionne),
   puis **Render > Render Animation**.

Résultat : `rendu\Marinor_Ivoire_Film.mp4`, 85 s, Full HD.

## Réglages appliqués par `preparer_rendu.py`

**Render Properties**

| Réglage | Valeur |
|---|---|
| Device | GPU Compute (OptiX, sinon CUDA) |
| Sampling > Render > Noise Threshold | coché, 0.01 |
| Max Samples | 128 |
| Denoise | coché, OpenImageDenoise, Albedo and Normal, Prefilter Accurate, Use GPU |
| Motion Blur | coché, Shutter 0.5 (0.25 pendant le travelling, animé par le script) |
| Performance > Final Render > Persistent Data | coché |
| Color Management | AgX, White Balance 4000 K |

**Output Properties**

| Réglage | Valeur |
|---|---|
| Resolution | 1920 × 1080, 100 % |
| Frame Rate | 24 |
| Frame Range | 1 à 2040, Step 1 |
| Chemin de sortie | `//rendu/images/marinor_` |
| Media Type / File Format | Image / PNG, RGB, 8 bits, compression 15 % |
| Overwrite | décoché |
| Placeholders | coché |

## En cas de problème

| Symptôme | Correction |
|---|---|
| `Out of GPU memory` | Render Properties > **Simplify** coché, **Texture Limit 2048**, Ctrl+S, relancer |
| Plusieurs minutes par image | Le rendu se fait sur le processeur : relancer `preparer_rendu.py`, vérifier `Reglages_Rendu` |
| Textures roses | **File > External Data > Find Missing Files** sur `Dossier de travail` |
| Rendu trop long | Max Samples 96 ou 64 (le débruitage compense) |
| Caissière trop haute / basse | `"z_assise": 0.74` en tête du script (0.72 la descend), relancer l'étape 2 |
