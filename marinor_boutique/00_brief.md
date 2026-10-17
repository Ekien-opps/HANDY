# CAHIER DES CHARGES : Magasin 3D Marin'Or Ivoire (version 3)

Document de référence. À relire au début de chaque nouvelle conversation, avec `elements.csv`.

**Version 3** : le magasin ne change pas. Son éclairage est fortement renforcé, sans coin sombre : dalles LED encastrées, lécheurs de murs au-dessus des étagères et spots plus puissants. Le magasin est posé dans un **décor urbain de Cocody Riviera (Abidjan) à l'heure dorée** : `marinor_environnement.py`, §9.

**Version 2** : surface agrandie de 60 à 384 m², mobilier et équipements de caisse inclus, locaux du personnel regroupés derrière un couloir fermé (les toilettes et le vestiaire ne sont jamais visibles depuis la salle de vente). Plan inspiré d'une supérette : locaux du personnel au fond, étagères murales sur le pourtour, vitrines réfrigérées au fond, gondoles en îlots, bacs de vrac au centre, caisses et bornes près de l'entrée.

---

## 0. Objectif

Construire **le magasin meublé**, en 3D, dans **Blender 5.1**, pour une boutique de marinades, épices, essentiels et dégustation.

**Inclus** : bâtiment (sols, murs, vitrines et cadres, portes à pivot, plafond, toit, acrotères, auvent, enseigne avec logo, seuils, plinthes, chambranles, lambris, mur de marque avec logo), **mobilier** (étagères murales, gondoles, présentoirs à bacs, vitrines réfrigérées, tables hautes, tabourets, banc, plantes), **caisses équipées** (2 comptoirs en L avec écran caissier, afficheur client, clavier, scanner, TPE, imprimante à tickets, tiroir-caisse, unité centrale ; 2 bornes libre-service), **locaux du personnel** meublés (rayonnages de réserve, bureau, vestiaire avec casiers, salle de pause, WC avec miroir et porte-papier, local technique), éclairage.

**Exclus** : les **produits** (pots, sachets, bouteilles). Le client les place lui-même. Des **marqueurs vides** (`Zone_...`) indiquent les rayons.

**Ambiance** : chaleureuse et naturelle. Bois, terre cuite, crème, bordeaux. Éclairage d'accent 2700 K (spots, suspensions, enseigne), éclairage général 3300 K blanc chaud (dalles LED, lécheurs de murs).

---

## 1. Convention de coordonnées (obligatoire)

- **Unité** : mètre.
- **Origine (0,0,0)** : coin extérieur avant gauche du bâtiment.
- **X** : largeur, de gauche à droite (0 à 24,00).
- **Y** : profondeur, de la rue (0, façade) au fond (16,00).
- **Z** : hauteur, sol à 0.

### Colonnes de `elements.csv`

| Colonne | Signification |
|---|---|
| `id` | Numéro de ligne, sert de référence |
| `nom` | Nom exact de l'objet Blender |
| `type` | Voir tableau des types ci-dessous |
| `collection` | Collection Blender où ranger l'objet |
| `x, y, z` | **Centre** de l'objet |
| `dim_x, dim_y, dim_z` | Dimensions (voir types) |
| `rot_x_deg` | Rotation autour de X (90 = plan vertical) |
| `rot_z_deg` | Rotation autour de Z |
| `materiau` | Nom du matériau `MAT_...` (matériau principal pour un meuble) |
| `notes` | Indications (ex. « enfant de 030 ») |

### Types : bâtiment

| Type | Création | Dimensions |
|---|---|---|
| `box` | Pavé | dim_x × dim_y × dim_z |
| `glass` | Pavé avec `MAT_Verre_Clair` transparent (alpha 0,35, mode blend) | dim_x × dim_y × dim_z |
| `door` | Vantail (pavé). Enfant du pivot indiqué dans `notes`, sans bouger sa position mondiale | dim_x × dim_y × dim_z |
| `plane` | Plan. Avec rot_x = 90, il est vertical, face vers -Y (rot_z = 90 : face vers +X) | dim_x = largeur, dim_y = hauteur |
| `cylinder` | Cylindre vertical (rot_x = 90 : couché, axe selon Y) | dim_x = dim_y = diamètre, dim_z = hauteur |
| `empty` | Objet vide (pivots, zones) | ignorées |
| `spot` | Lampe Spot 2700 K (#FFB46B) pointée vers -Z, plus un disque émissif de 0,10 m sous le plafond | ignorées |
| `suspension` | Abat-jour cylindrique + lampe Point 2700 K au centre, au bas de l'abat-jour | diamètre × hauteur de l'abat-jour |
| `area_light` | Lampe Area 2700 K, taille dim_x × dim_y, tournée vers l'enseigne (+Y) | dim_x × dim_y |
| `panneau_led` | Dalle LED encastrée (version 3) : diffuseur émissif sous le plafond + lampe Area 3300 K de la taille de la dalle, vers le bas, invisible à la caméra | dim_x × dim_y × épaisseur |
| `ruban_led` | Lécheur de mur (version 3) : profilé émissif au plafond + lampe Area 3300 K inclinée de rot_x vers l'avant du repère des meubles (-Y), orientée par rot_z (180 = vers +Y, 90 = vers +X, -90 = vers -X) | longueur × largeur × épaisseur |

### Types : meubles

Un meuble = **un seul objet**, fait de plusieurs pièces et de plusieurs matériaux. Repère : dim_x = largeur, dim_y = profondeur, dim_z = hauteur, **face avant vers -Y** avant rotation. `rot_z` oriente le meuble : 90 = face vers +X, -90 = face vers -X, 180 = face vers +Y.

| Type | Description | Matériaux (le 1er vient du CSV) |
|---|---|---|
| `etagere_murale` | Étagère simple face : fond contre le mur, joues, socle, tablettes tous les 0,38 m avec porte-étiquettes, fronton bordeaux | principal, Alu, Bordeaux |
| `gondole` | Îlot double face : socle, panneau central, joues bordeaux aux extrémités, tablettes des deux côtés | principal, Alu, Bordeaux |
| `presentoir_vrac` | Présentoir en gradins avec bacs ouverts (épices en vrac) | principal, Lambris_Bois |
| `frigo` | Vitrine réfrigérée : caisson, portes vitrées, clayettes, éclairage intérieur émissif | principal, Verre, Alu, Émissif |
| `rayonnage` | Rayonnage métallique de réserve, 4 montants, 5 niveaux | principal |
| `table` | Plateau + 4 pieds (sert aussi pour les bancs) | principal, Alu |
| `tabouret` | Assise ronde, 4 pieds, repose-pieds | principal, Alu |
| `chaise` | Assise, 4 pieds, dossier côté +Y | principal, Alu |
| `plante` | Pot, terre, tronc, feuillage | principal (pot), Végétal, Lambris_Bois |
| `ecran` | Écran sur pied, dalle légèrement lumineuse vers -Y | principal, Écran |
| `scanner` | Scanner code-barres sur socle, tête inclinée | principal, Écran |
| `tpe` | Terminal de paiement, écran sur le dessus | principal, Écran |
| `borne` | Borne libre-service : fût, tête avec vitre de scanner, écran incliné | principal, Écran, Plastique_Noir, Verre |
| `casiers` | Casiers de vestiaire, portes en grille de 0,40 m sur 2 rangs, poignées | principal (portes), Laque_Blanche, Alu |

### Portes à pivot

- Chaque `Pivot_...` est un objet vide placé au gond.
- Toute ligne dont les notes contiennent « enfant de NNN » devient enfant de l'objet NNN, sans bouger sa position mondiale : vantaux, et cadres aluminium des vantaux vitrés d'entrée.
- Pour ouvrir une porte, on tourne le pivot autour de Z.

---

### Collections (noms exacts)

`Sol`, `Murs_exterieurs`, `Murs_interieurs`, `Cloisons`, `Ouvertures`, `Toit`, `Toit_plafond`, `Enseigne`, `Eclairage`, `Decor_sol`, `Mobilier_vente`, `Mobilier_degustation`, `Plantes`, `Comptoir_caisse`, `Equipement_caisse`, `Mobilier_back_office`, `Sanitaires`, `Local_technique`, `Zones`.

---

## 2. Dimensions retenues

| Élément | Valeur |
|---|---|
| Façade (largeur extérieure) | 24,00 m |
| Profondeur totale | 16,00 m |
| Surface d'enveloppe | 384 m² |
| Hauteur sous plafond | 3,50 m (plafond z 3,47 à 3,50) |
| Murs extérieurs | 0,20 m d'épaisseur |
| Cloisons intérieures | 0,10 m d'épaisseur |
| Dalle de toit | 0,20 m (z 3,50 à 3,70) |
| Acrotères | 0,40 m de haut (z 3,70 à 4,10), 0,20 m d'épaisseur |
| Vitrines | 6 vitrines de 3,20 × 2,60 m, allège 0,40 m, linteau à 3,00 m |
| Porte d'entrée double | au centre (x 11,10 à 12,90), 2 vantaux vitrés de 0,90 m, h. 2,40 m |
| Imposte vitrée | z 2,40 à 3,00 |
| Porte de réserve (salle) | double, 1,60 m × 2,20 m |
| Porte staff (salle → couloir) | 0,90 m × 2,20 m |
| Portes des pièces du personnel | 0,80 à 0,90 m × 2,20 m |
| Porte de livraison | 1,20 m × 2,20 m, mur du fond, dans la réserve |
| Auvent | porte-à-faux de 1,20 m, z 3,00 à 3,10, largeur 24,00 m |
| Enseigne | 10,00 m × 0,80 m, en saillie de 0,20 m, z 3,20 à 4,00. Logo centré, hauteur 0,70 m |
| Comptoirs de caisse en L (×2) | barre 2,60 × 0,70 m + retour 0,70 × 0,70 m, h. 1,00 m, plan à 1,04 m |

### Surfaces

- **Salle de vente** : 23,60 × 11,80 = 278 m² (y 0,20 à 12,00).
- **Réserve** : 8,85 × 3,70 = 33 m².
- **Couloir du personnel** : 14,70 × 1,40 = 21 m².
- **Bureau** 8,6 m², **WC** 3,7 m², **vestiaire** 6,8 m², **salle de pause** 8,1 m², **local technique** 4,2 m².

### Circulation

- **Axe principal** : de l'entrée (x 12) au mur du fond, coupé par deux présentoirs à bacs avec 1,70 m libre de chaque côté.
- Allées entre gondoles : 1,60 m minimum. Allées le long des étagères murales : 1,80 m minimum.
- File d'attente des caisses : y 4,10 à 5,60.

### Règle d'intimité (version 2)

**Aucune porte des toilettes ni du vestiaire ne donne sur la salle de vente.** Les locaux du personnel sont derrière la cloison y = 12,05. On y entre par la porte staff (x 22,30 à 23,20) qui ouvre sur un couloir fermé ; le WC et le vestiaire ouvrent sur ce couloir, loin de la porte staff. Vérifié par lancer de rayons depuis 1 081 positions de client à 1,60 m : intérieur du WC, intérieur du vestiaire et leurs portes ne sont visibles depuis aucune position, même avec toutes les portes du personnel ouvertes.

---

## 3. Plan et zones (marqueurs vides)

| Zone | Position (x ; y) | Contenu |
|---|---|---|
| Accueil | 10,80–13,20 ; 0,20–1,80 | tapis avec logo |
| Dégustation | 1,60–8,20 ; 1,60–4,00 | 2 tables hautes, 8 tabourets, 4 suspensions |
| Mur de marque | mur gauche, y 1,80–3,40 | grand logo |
| Caisses | 14,40–21,20 ; 2,70–4,10 | 2 comptoirs équipés, caissier côté façade |
| Bornes | 22,40–23,00 ; 1,90–3,70 | 2 bornes libre-service |
| Épices | 0,20–9,30 ; 4,60–11,80 | 6 étagères murales gauche, 3 gondoles |
| Vrac | 11,00–13,00 ; 5,80–9,40 | 2 présentoirs à bacs |
| Essentiels | 14,70–21,30 ; 5,60–9,20 | 3 gondoles (pâte d'arachide, huile rouge) |
| Marinades | mur droit, y 5,20–11,20 | 5 étagères murales |
| Produits frais | 1,00–6,00 ; fond | 4 vitrines réfrigérées |
| Mur du fond | 9,60–21,60 ; fond | 10 étagères murales |
| Réserve | 0,20–9,00 ; 12,10–15,80 | 5 rayonnages, table de préparation |
| Bureau | 9,10–13,00 ; 13,60–15,80 | bureau, chaise, écran, armoire |
| Toilettes du personnel | 13,10–14,80 ; 13,60–15,80 | WC, lavabo, miroir, porte-papier |
| Vestiaire | 14,90–18,00 ; 13,60–15,80 | casiers, banc, miroir |
| Salle de pause | 18,10–21,80 ; 13,60–15,80 | kitchenette, frigo, table, 2 chaises |
| Local technique | 21,90–23,80 ; 13,60–15,80 | tableau électrique, baie informatique |

---

## 4. Matériaux et textures

### Règle de nommage (unique)

**Le fichier de texture porte exactement le nom du matériau**, avec l'extension, dans le dossier `textures/` à côté du `.blend`.

Exemple : le matériau `MAT_Sol_Terracotta` utilise `textures/MAT_Sol_Terracotta_color.jpg`.

Les fichiers `_roughness.jpg` et `_normal.jpg` sont optionnels, avec le même préfixe.

### Liste des matériaux

| Matériau | Utilisé pour | Texture à fournir | Couleur de secours |
|---|---|---|---|
| `MAT_Sol_Terracotta` | Sol de la salle de vente | `MAT_Sol_Terracotta_color.jpg` | #c97a52 |
| `MAT_Sol_BetonCire` | Sol réserve, couloir, local technique | `MAT_Sol_BetonCire_color.jpg` | #b9aea0 |
| `MAT_Sol_Carrelage_Blanc` | Sol WC, vestiaire, salle de pause | `MAT_Sol_Carrelage_Blanc_color.jpg` | #f2efe8 |
| `MAT_Mur_Creme` | Murs latéraux et cloisons | `MAT_Mur_Creme_color.jpg` (optionnelle) | #FFECD1 |
| `MAT_Mur_Bordeaux` | Façade, mur du fond, joues de gondoles, frontons, portes de casiers | `MAT_Mur_Bordeaux_color.jpg` (optionnelle) | #7B1421 |
| `MAT_Lambris_Bois` | Lambris bas, bacs de vrac, troncs | `MAT_Lambris_Bois_color.jpg` | #a0724a |
| `MAT_Bois_Clair` | Comptoirs, étagères, gondoles, tables, portes intérieures, sol du bureau | `MAT_Bois_Clair_color.jpg` | #d2b48c |
| `MAT_Plan_Comptoir` | Plans de travail des caisses | (couleur unie) | #e9e3d6 |
| `MAT_Laiton_Brosse` | Caisson enseigne, liserés, suspensions, robinet | `MAT_Laiton_Brosse_color.jpg` (optionnelle) | #F9A825 |
| `MAT_Alu_Cadre` | Cadres, seuils, auvent, pieds, porte-étiquettes | (couleur unie) | #2b2b2b |
| `MAT_Verre_Clair` | Vitrines, imposte, vantaux, portes de frigos | (transparent) | #ffffff |
| `MAT_Toit_Etancheite` | Dalle de toit, acrotères | `MAT_Toit_Etancheite_color.jpg` (optionnelle) | #d9d6cf |
| `MAT_Plafond_Blanc` | Plafond, tableau électrique | (couleur unie) | #FFFFFF |
| `MAT_Sanitaire_Blanc` | WC, réservoir, lavabo, porte-papier | (couleur unie, brillant) | #FFFFFF |
| `MAT_Tapis_Fibre` | Tapis d'entrée | `MAT_Tapis_Fibre_color.jpg` | #7B1421 |
| `MAT_Logo` | Logo enseigne, tapis, mur de marque | `MAT_Logo_color.png` (fond transparent) | #FFECD1 |
| `MAT_Lumiere_Emissive` | Disques des spots, éclairage des frigos | (émissif) | #fff1d6 |
| `MAT_Panneau_LED` | Diffuseurs des dalles LED et des lécheurs (version 3) | (émissif) | #fff4e2 |
| `MAT_Laque_Blanche` | Frigos, bornes, armoire, caissons de casiers | (couleur unie) | #f4f1ea |
| `MAT_Metal_Galva` | Rayonnages de réserve | (couleur unie, métal) | #a3a8ad |
| `MAT_Plastique_Noir` | Écrans, clavier, scanner, TPE, imprimante, tiroir-caisse, unités centrales | (couleur unie) | #161616 |
| `MAT_Ecran` | Dalles d'écran (légèrement lumineuses) | (couleur unie) | #0b1118 |
| `MAT_Cuir_Bordeaux` | Assises des tabourets | (couleur unie) | #5c1018 |
| `MAT_Pot` | Pots des plantes | (couleur unie) | #b5653d |
| `MAT_Vegetal` | Feuillage | (couleur unie) | #2a5519 (Vert Nature) |
| `MAT_Miroir` | Miroirs du WC et du vestiaire | (métal poli) | #ffffff |

### Textures à fournir, par ordre de priorité

**Indispensables** :
1. `MAT_Sol_Terracotta_color.jpg`
2. `MAT_Sol_BetonCire_color.jpg`
3. `MAT_Sol_Carrelage_Blanc_color.jpg`
4. `MAT_Lambris_Bois_color.jpg`
5. `MAT_Bois_Clair_color.jpg`
6. `MAT_Tapis_Fibre_color.jpg`
7. `MAT_Logo_color.png` (logo officiel, fond transparent)

**Optionnelles** : `MAT_Laiton_Brosse`, `MAT_Mur_Creme`, `MAT_Mur_Bordeaux`, `MAT_Toit_Etancheite`.

Format : JPG, **1024 × 1024 px**, texture répétable, raccord sans couture.

### Règles

- Un matériau par nom `MAT_...`, créé une seule fois et réutilisé sur tous les objets qui le portent.
- Si une texture manque : couleur de secours et avertissement dans la console, sans erreur.
- Les couleurs de secours suivent la charte de la marque (`colorimetrie_marque.txt`). Cette charte est une orientation, pas une règle rigide.
- Pour changer une texture dans Blender : on modifie le matériau, jamais la géométrie.

---

## 5. Éléments (décisions prises)

| Élément | Décision |
|---|---|
| **Auvent** | Dalle en porte-à-faux de 1,20 m, au-dessus des vitrines, sous l'enseigne. Largeur 24,00 m. Pas de toile. |
| **Cadres** | Parcloses aluminium autour des vitrines et de l'imposte ; montants, traverse et soubassement sur les vantaux d'entrée, qui pivotent avec eux. |
| **Seuils** | Aluminium, sous toutes les portes. |
| **Plinthes** | Bois clair sur la cloison du fond côté vente. Pas de plinthe sur les murs latéraux (lambris). |
| **Chambranles** | Bois clair côté salle de vente, sur la porte de réserve et la porte staff. |
| **Caisses** | Caissier côté façade, client côté salle. Écran caissier, afficheur client, TPE et liseré laiton tournés vers le client. Unité centrale au sol, sous le comptoir. |
| **Sanitaires** | WC avec réservoir, lavabo sur pied avec robinet, miroir, porte-papier. Accès par le couloir du personnel uniquement. |
| **Local technique** | Tableau électrique et baie informatique. |
| **Ventilation** | Grille dans le WC, sur le mur du fond. |
| **Logo** | Enseigne, tapis d'entrée (décalque) et mur de marque. Le ratio des plans suit celui de l'image. |

---

## 6. Règles de construction (pour le script)

1. **Aucune fusion** : chaque ligne de `elements.csv` est un objet séparé, nommé exactement comme la colonne `nom`. Un meuble est un seul objet.
2. **Collections** : une collection par valeur de la colonne `collection`.
3. **Toit supprimable** : `Toit_dalle`, `Acrotere_*`, `Auvent_dalle` et `Plafond_interieur` sont des objets séparés. Les supprimer ne doit rien casser.
4. **Portes** : pivots et vantaux comme décrit au §1.
5. **Textures** : chemin relatif au `.blend` (`//textures/`), défini en constante en tête de script.
6. **Logo** : `textures/MAT_Logo_color.png`. S'il est absent, plan de couleur crème et avertissement. Le ratio du plan suit celui de l'image.
7. **Éclairage** : vraies lampes Blender, 2700 K (accents) et 3300 K (général). Les lampes d'un même type partagent leurs réglages ; les puissances sont des constantes en tête de `marinor_batiment.py` (§10).
8. **Zones** : marqueurs vides, rien de visible.
9. **Aucun produit**, même décoratif.
10. **Relançable** : au démarrage, le script supprime les objets, collections et matériaux qu'il a créés.
11. **Sortie** : un fichier `.py` complet, sans dépendance externe, exécutable dans l'éditeur de script de Blender 5.1. À la fin, il enregistre `magasin_marinor.blend` dans le même dossier.
12. **Rapport console** : nombre d'objets créés, textures manquantes, erreurs.
13. **Plan** : `elements.csv` est produit par `generer_elements.py` (Python 3 seul). Pour modifier le plan, on modifie ce générateur (ou directement le CSV), puis on relance le script Blender.

---

## 7. Fichiers

```
marinor_boutique/
├── 00_brief.md
├── elements.csv                      (produit par generer_elements.py)
├── generer_elements.py               (plan du magasin)
├── marinor_batiment.py               (script Blender 5.1 : le magasin)
├── marinor_environnement.py          (script Blender 5.1 : décor de Cocody, §9)
├── generer_textures_env.py           (refait les textures de végétation, Pillow)
├── colorimetrie_marque.txt           (charte de la marque)
└── textures/
    ├── env/                          (feuillages, palmes, fleurs, haie : PNG transparents)
    ├── MAT_Sol_Terracotta_color.jpg
    ├── MAT_Sol_BetonCire_color.jpg
    ├── MAT_Sol_Carrelage_Blanc_color.jpg
    ├── MAT_Lambris_Bois_color.jpg
    ├── MAT_Bois_Clair_color.jpg
    ├── MAT_Tapis_Fibre_color.jpg
    └── MAT_Logo_color.png            (logo, fond transparent)
```

Textures optionnelles non fournies (couleurs de secours utilisées) : `MAT_Laiton_Brosse`, `MAT_Mur_Creme`, `MAT_Mur_Bordeaux`, `MAT_Toit_Etancheite`.

Le tapis a une texture gris rayé. Sa teinte se modifie dans le nœud « Teinte » du matériau `MAT_Tapis_Fibre`.

## 8. Validation

Le script est testé avec Blender 5.1.2 (module Python) : construction sans erreur, relancement sans doublon, centres et dimensions conformes au CSV, aucune collision entre meubles et murs, test de visibilité des locaux du personnel (§2). En cas d'erreur chez vous, renvoyer le contenu du texte Blender `Rapport_Marinor` ou le message complet de la console.

Version 3 : le décor est testé de la même façon (rapport `Rapport_Cocody`, 0 erreur, relancement sans doublon) et par des rendus Cycles des cinq caméras et de l'intérieur.

---

## 9. Décor urbain : Cocody Riviera à l'heure dorée (version 3)

Script : `marinor_environnement.py`. On l'exécute dans Blender 5.1 comme le script du magasin. Si le magasin n'est pas dans la scène, il lance d'abord `marinor_batiment.py`. Il enregistre `marinor_cocody.blend` (le fichier `magasin_marinor.blend` reste le magasin seul). Il est relançable : tout ce qu'il crée porte la marque `marinor_env`. Le décor est reproductible : la constante `GRAINE` fixe le tirage aléatoire (même graine = même rue).

### Implantation du magasin

- Le magasin garde ses coordonnées : façade sur y = 0, rue du côté des y négatifs, sol fini à z = 0.
- **Parcelle** x -4 à 38, y -7 à 20 :
  - **parvis pavé** en pente douce de 1,8 % (z -0,025 au pied de la façade, -0,15 au trottoir), avec un seuil de 2,5 cm à l'entrée et 9 places de parking marquées ;
  - **allée de service** à gauche, fermée par un portail plein à l'alignement de la façade, qui mène à la cour arrière et à la porte de livraison ;
  - **jardin** à droite, derrière une grande jardinière basse plantée de palmiers royaux, et un mur blanc couvert de bougainvilliers ;
  - **murs de clôture** blancs (bas devant, 2,60 m sur les côtés et au fond) ;
  - **soubassement** gris de 25 cm au pied des murs extérieurs.
- **Bateau** : bordure abaissée et accotement pavé devant le parvis, pour l'accès des voitures.

### Profil de l'avenue (y), côté magasin puis côté opposé

| Bande | y | Niveau z |
|---|---|---|
| Limite des parcelles (murs) | -7,00 | |
| Bande plantée (haie, massifs) | -7,80 à -7,00 | -0,18 |
| Trottoir pavé | -9,60 à -7,80 | -0,15 |
| Accotement engazonné, arbres, lampadaires | -11,20 à -9,60 | -0,16 |
| Bordure béton | -11,35 à -11,20 | -0,15 |
| Chaussée 2 × 1 voie, axe discontinu, lignes de rive, caniveaux | -19,35 à -11,35 | -0,30 |
| Bordure, accotement, trottoir, bande plantée (côté opposé) | -19,35 à -23,70 | idem |

### Contenu

- **Villas contemporaines**, des deux côtés, sur 1 km :
  - hauts murs blancs à piliers, chaperons et appliques allumées, parfois surmontés d'une grille ;
  - portail et portillon en fer forgé noir (barreaux, pointes de lance, volutes) ;
  - maison à étage en porte-à-faux, dalles débordantes, grandes baies sombres, claustras bois, bande de pierre ; une sur trois a un toit à quatre pans.
- **Végétation** :
  - arbres d'alignement : flamboyants en fleurs, manguiers, palmiers royaux, fromagers à contreforts ;
  - jardins : cocotiers, bananiers ;
  - au pied des murs : hibiscus, bougainvilliers en cascade, haies taillées ;
  - sur les accotements : touffes d'herbe.
- **Arrière-quartier** de maisons et de jardins arborés, canopée lointaine, collines et silhouettes d'immeubles dans la brume.
- **Voitures** :
  - SUV noir et berline blanche sur le parking du magasin ;
  - SUV bleu nuit, berlines et SUV dans l'avenue, sur leur voie (circulation à droite).
- **Agent de sécurité** en uniforme devant un portail, avec une plaque « RIVIERA 3 » sur le mur.
- **Lumière** :
  - soleil bas de sud-ouest, à 17° de hauteur, 3600 K, ombres longues ;
  - ciel physique bleu avec nuages dorés côté soleil ;
  - brume chaude au loin.
- **Caméras** :

  | Caméra | Vue |
  |---|---|
  | `CAM_Avenue_Cocody` (active) | depuis la chaussée, comme la photo de référence |
  | `CAM_Facade_Boutique` | façade vue du trottoir d'en face |
  | `CAM_Trois_Quarts` | magasin de trois-quarts depuis la chaussée |
  | `CAM_Parvis_Entree` | entrée et intérieur à travers la vitrine |
  | `CAM_Drone` | vue aérienne |

### Matériaux du décor

- **Préfixe** : ils commencent par `ENV_`.
- **Procéduraux** : sans fichier image (asphalte, pavés, gazon, enduits, écorces, peintures de voiture, etc.).
- **Cartes de végétation** : les feuillages sont des plans avec les PNG transparents de `textures/env/`, produits par `generer_textures_env.py`.
- **Brume** : chaque matériau passe par le groupe de nœuds `ENV_Brume`, qui ajoute la brume selon la distance à la caméra.
- **Vitrines du magasin** : avec `VITRAGE_REALISTE_MAGASIN = True` (réglage par défaut), le matériau `MAT_Verre_Clair` devient un verre clair (transparent + reflet de Fresnel) dans `marinor_cocody.blend`, pour que l'intérieur éclairé se voie depuis la rue. La géométrie du magasin et `marinor_batiment.py` ne changent pas.

### Réglages (constantes en tête de `marinor_environnement.py`)

- **Soleil** : `SOLEIL_ELEVATION_DEG`, `SOLEIL_AZIMUT_DEG`, `SOLEIL_PUISSANCE`, `SOLEIL_TEMPERATURE_K`.
- **Ciel** : `CIEL_PUISSANCE`, `CIEL_NUAGES`, `LUMINOSITE_NUAGES`.
- **Brume** : `BRUME_DISTANCE_M`, `BRUME_FORCE`.
- **Rendu** : `EXPOSITION`, `MOTEUR` (Cycles par défaut, EEVEE possible), `RESOLUTION`, `ECHANTILLONS_CYCLES`, `CAMERA_ACTIVE`.
- **Rue** : `GRAINE` pour une autre rue.
- **Vue dégagée** : `VUE_DEGAGEE_FACADE` et `VUE_DEGAGEE_NORD` gardent la façade au soleil en écartant les grands arbres côté ouest.

Pour le rendu final, Cycles sur carte graphique (Préférences > Système > Cycles Render Devices), 256 échantillons, débruitage actif. Le fichier est déjà réglé ainsi, à part le choix de la carte graphique.

---

## 10. Éclairage du magasin (version 3)

| Source | Nombre | Réglage (en tête de `marinor_batiment.py`) | Version 2 |
|---|---|---|---|
| Spots 2700 K, angle 100° | 36 | `PUISSANCE_SPOT_W = 100` | 60 W, 80° |
| Suspensions 2700 K | 6 | `PUISSANCE_SUSPENSION_W = 60` | 40 W |
| Enseigne (Area 2700 K) | 1 | `PUISSANCE_ENSEIGNE_W = 120` | 35 W |
| Dalles LED 3300 K encastrées (0,60 m ; 0,45 m dans le WC et le local technique) | 29 en salle, 13 dans les locaux du personnel | `PUISSANCE_DALLE_W_M2 = 90` (32 W par dalle de 0,60 m) | aucune |
| Lécheurs de murs 3300 K (étagères gauche, droite, fond, vitrines réfrigérées) | 4 | `PUISSANCE_LECHEUR_W_M = 20` par mètre | aucun |

- **Emplacement des dalles** : elles sont au milieu des mailles de spots, avec une rangée le long des vitrines et une le long du fond. Les lécheurs sont au plafond, à environ 1 m des étagères, inclinés de 35° vers elles. Chaque pièce du personnel a au moins une dalle.
- **Numérotation** : les nouvelles lignes sont ajoutées à la fin de `elements.csv` (lignes 326 à 371), donc les numéros des lignes existantes, et les « enfant de NNN », ne changent pas.
- **Réglage global** : pour tout éclaircir ou assombrir d'un coup, on modifie `EXPOSITION` (décor) ou l'exposition de la vue dans Blender (Rendu > Gestion des couleurs).
