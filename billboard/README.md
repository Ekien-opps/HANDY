# Panneau publicitaire 3D – Marin'Or Ivoire

Panneau publicitaire sur un seul pied, modélisé pour Blender, avec l'affiche
« Le goût qui rassemble » appliquée sur la face avant.

## Le cadre adapté à l'affiche

Le cadre de la photo de référence est au format 4 × 3 (ratio 1,33). L'affiche
fait 2000 × 1181 px (ratio 1,693). Le cadre a donc été redimensionné pour
l'affiche. Le visuel n'est ni étiré ni rogné :

| Élément | Dimensions |
|---|---|
| Surface d'affiche visible | **5,08 × 3,00 m** (ratio 1,6935, identique au fichier) |
| Cadre hors-tout | 5,34 × 3,26 m (moulure de 13 cm, coupes d'onglet) |
| Profondeur du caisson | 28 cm, plus l'ossature arrière |
| Hauteur sous le panneau | 3,60 m |
| Pied | 0,85 × 0,50 m, habillé de lames verticales, sur platine et massif béton |

Ces valeurs sont réglables en tête de `build_billboard.py` (`POSTER_H`,
`FRAME_W`, `CLEARANCE`…). La largeur est toujours calculée à partir du ratio de
l'affiche.

## Fichiers

- `panneau_marinor.blend` : scène Blender complète, à ouvrir directement. La
  texture est intégrée au fichier, qui contient :
  - collection **Panneau** : affiche, cadre en 6 profilés (traverses haute et
    basse en deux éléments, comme sur la photo), caisson, ossature galvanisée,
    pied, 3 projecteurs ;
  - collection **Environnement** : sol en pavés, lisière d'arbres, ciel Nishita
    et soleil ;
  - collection **Cameras** : `Camera_Face`, `Camera_3-4`, `Camera_Affiche`
    (vue de face) et `Camera_Arriere`.
- `panneau_marinor.glb` : le panneau seul au format glTF, pour d'autres
  logiciels ou pour l'importer dans une autre scène Blender.
- `textures/affiche_marinor_ivoire.png` : l'affiche d'origine.
- `renders/` : aperçus rendus avec Cycles.
- `build_billboard.py` : script qui génère toute la scène.

## Utilisation

Ouvrez `panneau_marinor.blend` dans Blender 4.2 ou une version plus récente,
puis lancez un rendu avec F12. Le moteur est Cycles, avec 96 échantillons et
débruitage.

- **Changer d'affiche** : dans l'éditeur d'images, remplacez l'image du
  matériau `Affiche_MarinOr`. Si le format change, régénérez la scène (voir
  ci-dessous) pour que le cadre suive.
- **Vue de nuit** : réactivez les lampes `Projecteur_Spot0..2` (icônes
  caméra/écran dans l'Outliner), puis baissez `Soleil` et la force du ciel.
- **Régénérer la scène** :

  ```bash
  blender -b -P build_billboard.py -- --render
  ```
