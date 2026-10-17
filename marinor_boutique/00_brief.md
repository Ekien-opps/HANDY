# CAHIER DES CHARGES : Bâtiment 3D Boutique Marin'Or Ivoire

Document de référence. À relire au début de chaque nouvelle conversation, avec `elements.csv`.

---

## 0. Objectif

Construire **le bâtiment seul**, en 3D, dans **Blender 5.1**, pour une boutique de marinades, épices, essentiels et dégustation.

**Inclus** : sol, murs, vitrines et cadres, portes à pivot, plafond, toit, acrotères, auvent, enseigne extérieure avec logo, seuils, plinthes, chambranles, sanitaires (WC et lavabo), tableau électrique, grille de ventilation, éclairage (spots et suspensions), tapis d'entrée avec logo, comptoir caisse en L.

**Exclus** : tout le mobilier (étagères, présentoirs, tables, tabourets, plantes, frigo, caisse enregistreuse, miroir, porte-papier, etc.) et tous les produits. Le client place lui-même son mobilier et ses produits. Des **marqueurs vides** (`Zone_...`) indiquent où les placer.

**Ambiance** : chaleureuse et naturelle. Bois, terre cuite, crème, bordeaux. Éclairage 2700 K.

---

## 1. Convention de coordonnées (obligatoire)

- **Unité** : mètre.
- **Origine (0,0,0)** : coin extérieur avant gauche du bâtiment.
- **X** : largeur, de gauche à droite (0 à 8,40).
- **Y** : profondeur, de la rue (0, façade) au fond (7,20).
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
| `materiau` | Nom du matériau `MAT_...` |
| `notes` | Indications (ex. « enfant de 030 ») |

### Types

| Type | Création | Dimensions |
|---|---|---|
| `box` | Pavé | dim_x × dim_y × dim_z |
| `glass` | Pavé avec `MAT_Verre_Clair` transparent (alpha 0,3 à 0,4, mode blend) | dim_x × dim_y × dim_z |
| `door` | Vantail (pavé). Enfant du pivot indiqué dans `notes`, sans bouger sa position mondiale | dim_x × dim_y × dim_z |
| `plane` | Plan. Avec rot_x = 90, il est vertical, face vers -Y | dim_x = largeur, dim_y = hauteur |
| `cylinder` | Cylindre vertical | dim_x = dim_y = diamètre, dim_z = hauteur |
| `empty` | Objet vide (pivots, zones, emplacement caisse) | ignorées |
| `spot` | Lampe Spot 2700 K (#FFB46B) pointée vers -Z, plus un disque émissif de 0,10 m | ignorées |
| `suspension` | Abat-jour cylindrique + lampe Point 2700 K au centre, à z = 2,10 | ignorées |
| `area_light` | Lampe Area 2700 K, taille dim_x × dim_y, orientée vers -Y | dim_x × dim_y |

### Portes à pivot

- Chaque `Pivot_...` est un objet vide placé au gond.
- Chaque vantail (`type door` ou `glass`) est enfant du pivot indiqué dans `notes`. Il garde sa position mondiale.
- Pour ouvrir une porte, on tourne le pivot autour de Z.

---

### Collections (noms exacts)

`Sol`, `Murs_exterieurs`, `Murs_interieurs`, `Cloisons`, `Ouvertures`, `Toit`, `Toit_plafond`, `Enseigne`, `Eclairage`, `Decor_sol`, `Comptoir_caisse`, `Sanitaires`, `Local_technique`, `Zones`.

---

## 2. Dimensions retenues

| Élément | Valeur |
|---|---|
| Façade (largeur extérieure) | 8,40 m |
| Profondeur totale | 7,20 m |
| Surface d'enveloppe | 60,48 m² |
| Hauteur sous plafond | 3,00 m |
| Murs extérieurs | 0,20 m d'épaisseur |
| Cloisons intérieures | 0,10 m d'épaisseur |
| Dalle de toit | 0,20 m (z 3,00 à 3,20) |
| Acrotères | 0,40 m de haut (z 3,20 à 3,60), 0,20 m d'épaisseur |
| Vitrines | 2,40 × 2,40 m, allège 0,40 m, linteau à 2,80 m |
| Porte d'entrée double | 1,60 m, 2 vantaux de 0,80 m, h. 2,40 m |
| Imposte vitrée | z 2,40 à 2,80 |
| Porte staff (réserve) | 0,90 m × 2,20 m |
| Portes vestiaire et WC | 0,80 m × 2,10 m |
| Auvent | porte-à-faux de 1,00 m, z 2,80 à 2,90, largeur 8,40 m |
| Enseigne | 6,80 m × 0,60 m, en saillie de 0,20 m, z 2,95 à 3,55. Logo centré de 0,95 × 0,54 m |
| Comptoir caisse en L | barre 2,60 × 0,70 m + retour 0,70 × 0,70 m, h. 1,00 m |

### Surfaces

- **Réserve** : 3,80 × 3,20 = 12,16 m²
- **Toilettes et vestiaire** : 2,40 × 2,10 = 5,04 m²
- **Back-office total** : 17,2 m². Le cahier initial indiquait 15 m² ; la cote réelle a été retenue.
- **Surface de vente** : 60,48 − 17,2 = 43,3 m².

### Circulation

- **Axe principal libre** : x 3,40 à 5,40, de l'entrée au comptoir. Largeur minimum 1,30 m.
- Allées secondaires : 1,00 m minimum.

---

## 3. Plan et zones (marqueurs vides, à titre indicatif)

| Zone | Position (x, y) | Dimensions |
|---|---|---|
| Accueil / tapis | 3,40–5,00 ; 0,20–1,40 | devant la porte |
| Mur de marque | mur gauche, y 0,40–3,60 | 3,20 m |
| Épices | 0,60–2,60 ; 0,60–2,90 | présentoirs muraux et îlots |
| Assise (2 à 3 places) | 0,60–2,60 ; 3,00–3,90 | attente ou atelier |
| Essentiels | 5,40–7,20 ; 0,60–1,90 | pâte d'arachide, huile rouge |
| Table de dégustation | 5,60–7,40 ; 2,40–3,30 | 1,80 × 0,90 m |
| Marinades | mur droit, x 7,40–8,00 ; y 0,40–3,80 | 3,40 m linéaires |
| Caisse et comptoir | 3,90–6,50 ; 3,50–4,90 | comptoir déjà construit |
| Emballage cadeau | 3,80–6,00 ; 4,90–7,00 | derrière le comptoir |
| Réserve | 0,20–3,80 ; 4,00–7,00 | rayonnages à placer |
| Vestiaire | 6,00–7,20 ; 5,10–7,00 | |
| Toilettes staff | 7,20–8,20 ; 5,10–7,00 | sanitaires déjà posés |

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
| `MAT_Sol_BetonCire` | Sol de la réserve | `MAT_Sol_BetonCire_color.jpg` | #b9aea0 |
| `MAT_Sol_Carrelage_Blanc` | Sol vestiaire et WC | `MAT_Sol_Carrelage_Blanc_color.jpg` | #f2efe8 |
| `MAT_Mur_Creme` | Murs latéraux et cloisons | `MAT_Mur_Creme_color.jpg` (optionnelle) | #FFECD1 |
| `MAT_Mur_Bordeaux` | Façade et mur du fond | `MAT_Mur_Bordeaux_color.jpg` (optionnelle) | #7B1421 |
| `MAT_Lambris_Bois` | Lambris bas des murs latéraux | `MAT_Lambris_Bois_color.jpg` | #a0724a |
| `MAT_Bois_Clair` | Comptoir, portes intérieures, chambranles, plinthes | `MAT_Bois_Clair_color.jpg` | #d2b48c |
| `MAT_Plan_Comptoir` | Plan de travail | (couleur unie) | #e9e3d6 |
| `MAT_Laiton_Brosse` | Caisson enseigne, liseré comptoir, suspensions, robinet | `MAT_Laiton_Brosse_color.jpg` (optionnelle) | #F9A825 |
| `MAT_Alu_Cadre` | Cadres, seuils, auvent, grille | (couleur unie) | #2b2b2b |
| `MAT_Verre_Clair` | Vitrines, imposte, vantaux | (transparent) | #ffffff |
| `MAT_Toit_Etancheite` | Dalle de toit, acrotères | `MAT_Toit_Etancheite_color.jpg` (optionnelle) | #d9d6cf |
| `MAT_Plafond_Blanc` | Plafond, tableau électrique | (couleur unie) | #FFFFFF |
| `MAT_Sanitaire_Blanc` | WC, réservoir, lavabo | (couleur unie, brillant) | #FFFFFF |
| `MAT_Tapis_Fibre` | Tapis d'entrée | `MAT_Tapis_Fibre_color.jpg` | #7B1421 |
| `MAT_Logo` | Logo sur l'enseigne et sur le tapis | `MAT_Logo_color.png` (fond transparent) | #FFECD1 |
| `MAT_Lumiere_Emissive` | Disques des spots | (émissif) | #fff1d6 |

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

## 5. Éléments du bâtiment (décisions prises)

| Élément | Décision |
|---|---|
| **Auvent** | Dalle en porte-à-faux de 1,00 m, au-dessus des vitrines, sous l'enseigne. Largeur 8,40 m. Pas de toile. |
| **Cadres** | Parcloses aluminium autour des vitrines et de l'imposte, montants et traverse sur les vantaux. |
| **Seuils** | Aluminium, sous la porte d'entrée et les portes intérieures. |
| **Plinthes** | Bois clair sur la façade intérieure et le fond. Pas de plinthe sur les murs latéraux (lambris). |
| **Chambranles** | Bois clair côté salle de vente, sur les portes intérieures. |
| **Sanitaires** | WC avec réservoir, lavabo sur pied avec robinet. Posés dans le bâtiment, pas en mobilier. |
| **Local technique** | Tableau électrique sur la cloison du vestiaire. |
| **Ventilation** | Grille dans le WC. |
| **Logo tapis** | Plan avec le logo, posé au-dessus du tapis (décalque). |

---

## 6. Règles de construction (pour le script)

1. **Aucune fusion** : chaque ligne de `elements.csv` est un objet séparé, nommé exactement comme la colonne `nom`.
2. **Collections** : une collection par valeur de la colonne `collection`.
3. **Toit supprimable** : `Toit_dalle`, `Acrotere_*`, `Auvent_dalle` et `Plafond_interieur` sont des objets séparés. Les supprimer ne doit rien casser.
4. **Portes** : pivots et vantaux comme décrit au §1.
5. **Textures** : chemin relatif au `.blend` (`//textures/`), défini en constante en tête de script.
6. **Logo** : `textures/MAT_Logo_color.png`. S'il est absent, plan de couleur crème et avertissement. Le ratio du plan suit celui de l'image.
7. **Éclairage** : vraies lampes Blender, 2700 K. Intensité à régler par l'utilisateur.
8. **Zones** : marqueurs vides, rien de visible.
9. **Aucun mobilier, aucun produit**, même décoratif.
10. **Relançable** : au démarrage, le script supprime les objets, collections et matériaux qu'il a créés.
11. **Sortie** : un fichier `.py` complet, sans dépendance externe, exécutable dans l'éditeur de script de Blender 5.1. À la fin, il enregistre `magasin_marinor.blend` dans le même dossier.
12. **Rapport console** : nombre d'objets créés, textures manquantes, erreurs.

---

## 7. Prompt de génération

> Écris un script Python complet pour **Blender 5.1**, exécutable dans l'éditeur de script, sans dépendance externe, qui construit le bâtiment de la boutique Marin'Or Ivoire.
>
> Fichiers dans le même dossier que le `.blend` : `00_brief.md` (à respecter à la lettre) et `elements.csv` (128 lignes).
>
> - Lis `elements.csv` et crée un objet par ligne. Respecte la convention du §1 : origine, centre des objets, dimensions selon le type, rotations.
> - Crée une collection par valeur de la colonne `collection`.
> - Crée les matériaux `MAT_...` avec leur nom exact, une seule fois, et réutilise-les.
> - Pour `door` et `glass` : le vantail devient enfant du pivot indiqué dans `notes` (« enfant de 030 »), sans bouger sa position mondiale.
> - Pour `spot`, `suspension` et `area_light` : crée les lampes décrites au §1, en 2700 K.
> - Pour `plane` : rot_x = 90 le rend vertical. Pour `Enseigne_logo` et `Tapis_logo`, applique `MAT_Logo`.
> - Charge les textures 1024 × 1024 depuis `//textures/` avec le nom du matériau (§4). Si absente : couleur de secours, avertissement console, pas d'erreur.
> - Ne crée aucun mobilier, aucun produit, aucun objet absent du CSV.
> - Au démarrage, supprime les objets, collections et matériaux créés par le script, pour pouvoir relancer sans erreur.
> - À la fin, enregistre `magasin_marinor.blend` dans le même dossier, puis affiche le rapport (objets créés, textures manquantes, erreurs).
> - Donne le script complet, en un seul bloc. Indique ensuite la seule ligne à modifier pour changer le dossier des textures.

---

## 8. Contenu du zip (à respecter)

```
marinor_boutique/
├── 00_brief.md
├── elements.csv                      (128 lignes)
├── colorimetrie_marque.txt           (charte de la marque)
└── textures/
    ├── MAT_Sol_Terracotta_color.jpg
    ├── MAT_Sol_BetonCire_color.jpg
    ├── MAT_Sol_Carrelage_Blanc_color.jpg
    ├── MAT_Lambris_Bois_color.jpg
    ├── MAT_Bois_Clair_color.jpg
    ├── MAT_Tapis_Fibre_color.jpg
    └── MAT_Logo_color.png            (logo, fond transparent)
```

Textures optionnelles non fournies (couleurs de secours utilisées) : `MAT_Laiton_Brosse`, `MAT_Mur_Creme`, `MAT_Mur_Bordeaux`, `MAT_Toit_Etancheite`.

Le tapis a une texture gris rayé. Sa teinte se modifie dans le matériau `MAT_Tapis_Fibre` si besoin.

## 9. Validation

Je ne peux pas exécuter Blender ici. Tu testes le script et me renvoies le message complet de la console en cas d'erreur.
