# Marin'Or Ivoire — mise en scène finale 3D (Blender 5.1)

Plan-séquence de 85 s (2 040 images, 24 i/s) dans la boutique de Cocody Riviera :
survol aérien, zoom sur la boutique, ouverture des portes automatiques, passage à la
caisse, travelling latéral au ras des marinades, vue de dessus (plafond escamoté), visite
des locaux du personnel, sortie par les portes et plan large final sur la façade.

## Fichiers

| Fichier | Rôle |
|---|---|
| `marinor_mise_en_scene.py` | Script Blender 5.1 : produits, personnages Mixamo, portes, plafond, caméra, rendu. Relançable. |
| `catalogue_produits.json` | Les 15 produits : nom, catégorie, archive OBJ, hauteur réelle, orientation, couleur. |
| `generer_signaletique.py` | Python 3 + Pillow : refait les étiquettes, panneaux, cartons et plaques de porte. |
| `textures/signaletique/` | Les 60 textures générées (déjà prêtes). |
| `GUIDE_RENDU.md` | Guide pas à pas jusqu'au film MP4 final. |

## Installation dans le dossier `marinor_boutique/`

Copier le contenu de ce dossier à côté de `marinor_cocody.blend`, puis :

```
marinor_boutique/
├── marinor_cocody.blend
├── marinor_mise_en_scene.py
├── catalogue_produits.json
├── elements.csv
├── textures/signaletique/          (ce dépôt)
├── produits/                       les 15 zip « MarinOr_..._OBJ.zip » (contenu de Les Produits.zip)
└── personnages/                    les FBX Mixamo (contenu de « Animations pus trouvées.zip »)
```

Le dossier `textures/signaletique/` doit être à côté du script ; s'il a été décompressé ailleurs dans le
dossier du projet, le script le retrouve et l'indique dans la console.

Ouvrir `marinor_cocody.blend` dans Blender 5.1, onglet Scripting, ouvrir
`marinor_mise_en_scene.py`, Exécuter. Le script enregistre `marinor_film.blend` et écrit
un rapport dans le texte Blender `Rapport_Film` (produits importés, instances, personnages,
avertissements). En ligne de commande :

```
blender marinor_cocody.blend --background --python marinor_mise_en_scene.py
blender marinor_film.blend --background --render-anim
```

## Étape 1 — rangement des produits

Chaque produit est importé une fois, mis à sa hauteur réelle (`hauteur_m`), puis répété par
instances (Geometry Nodes) : environ 8 000 produits en rayon pour un fichier léger.

| Meuble (brief §3) | Contenu |
|---|---|
| 6 étagères murales gauche | Épices : 9 doypacks 100 g en blocs verticaux, 2 par étagère |
| 3 gondoles G (2 faces) | Épices, 3 blocs par face |
| 5 étagères murales droite | Marinades 500 g (Poulet, Poisson, Mixte) |
| 3 gondoles D (2 faces) | Essentiels : pâte d'arachide 1 kg, huile rouge |
| 4 vitrines réfrigérées | Marinades fraîches (1 par vitrine) et purée d'ail |
| 10 étagères du mur du fond | Toute la gamme, de gauche à droite : épices, marinades, essentiels, purée |
| 2 présentoirs à bacs | 16 bacs d'épices en vrac (monticules, chevalets, pelles doseuses) |
| Tables de dégustation | Plateaux, ramequins de sauce, produits ouverts |
| Réserve | Cartons imprimés Marin'Or sur les 5 rayonnages, palette près de la livraison |

En plus : une étiquette de rayon par bloc de produits, des panneaux suspendus ou muraux
(Épices, Marinades, Essentiels, Produits frais, Vrac, Dégustation, Caisses, Toute la gamme)
et des plaques sur les portes du personnel. Aucun prix n'est inscrit : renseigner `PRIX`
dans `generer_signaletique.py` puis relancer ce script pour les ajouter.

**Orientation automatique des étiquettes** : pour chaque produit, le script lit sa texture et
tourne vers l'allée la face la plus imprimée (logo, photo), face plane d'un doypack comme
centre de l'étiquette d'une bouteille. L'angle retenu est écrit dans le rapport
(« Orientation des étiquettes »). Le script rend aussi `rendu/controle_etiquettes.png` : les 15 produits vus
depuis l'allée, pour tout vérifier d'un coup d'œil. Pour forcer un angle, remplacer `null` par 0, 90, 180 ou
-90 dans `rot_z_deg` du produit (`catalogue_produits.json`).

## Étape 2 — personnages Mixamo

| Rôle | Fichiers | Placement |
|---|---|---|
| Caissière assise | `Ch41…` (maillage) + `Ch41…Sitting Talking` | Caisse 1, sur un tabouret haut créé pour elle, micro-animations en boucle. Sa hauteur est mesurée sur son maillage (dessous des fesses = dessus de l'assise) et un dégagement pour les jambes est creusé sous le comptoir (booléen non destructif) |
| Employé rayon épices | `Ch12…Walking` | Boucle entre les gondoles G, 1,26 m/s |
| Employé rayon essentiels | `Ch28…Walking` | Boucle entre les gondoles D, décalée |
| Agent de sécurité | `Ch18…Idle Looking` | Dehors, à gauche des portes, sous l'auvent |

La vitesse de marche est mesurée sur le pied d'appui de l'animation, pour que les pieds ne
glissent pas. Les préfixes d'os Mixamo (`mixamorig4:`…) sont harmonisés automatiquement.

## Étape 3 — caméra

| Temps | Plan |
|---|---|
| 0:00–0:08 | Survol aérien rapide de Cocody Riviera |
| 0:08–0:13 | Zoom progressif sur la façade, mise au point sur la boutique |
| 0:12–0:16 | Ouverture des portes automatiques, entrée |
| 0:16–0:21 | Passage au ras de la caisse et de la caissière |
| 0:24–0:34 | Travelling latéral en gros plan le long des marinades |
| 0:35–0:45 | Élévation, plafond escamoté, vue de dessus de toute la boutique |
| 0:47–1:11 | Porte staff, couloir, salle de pause, vestiaire, bureau, réserve (les toilettes restent fermées, règle d'intimité du brief) |
| 1:11–1:25 | Retour en salle, sortie par les portes, plan large final sur la façade |

Toutes les cotes de la caméra sont dans `CAMERA_CLES`, en tête du script, et les portes
dans `PORTES`.

Réglages de rendu : Cycles, 1920 × 1080, 128 échantillons avec débruitage, flou de
mouvement, sortie MP4 H.264 dans `rendu/`. La balance des blancs de la caméra
(`BALANCE_BLANCS_K = 4000`) atténue la dominante orange de l'éclairage 2700 K ; mettre
6500 pour revenir au neutre. Pour le rendu final, activer la carte graphique (Préférences >
Système > Cycles Render Devices).
