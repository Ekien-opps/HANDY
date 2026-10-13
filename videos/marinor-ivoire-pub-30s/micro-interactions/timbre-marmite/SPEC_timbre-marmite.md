# Timbre « Marmite chaude » — micro-interaction 1 s
### Spécifications de production & prompt d'animation · Direction artistique / Lead Motion Design 3D

> **L'intention en une phrase.** Une marmite sous pression soulève son couvercle, crache une langue de feu graphique, la ravale en claquant, et c'est ce choc qui fend le timbre : trois coups secs (*pop · clac · crac*) en une seconde, avec une causalité lisible et une fin nette et figée.

**Version :** v1 · **Durée :** 60 images à 60 i/s = **1,000 s** · **Fond :** aucun (alpha) · **Texte :** aucun

---

## 1. Ce que l'on retient de la référence (mouvement uniquement)

- Les données : vidéo de référence à 30 i/s, timbre à icône centrale. On n'en retient que la mécanique de la déchirure.
- **La fracture est sèche** : elle se propage en 2 à 3 images (70 à 100 ms), sans flou de mouvement.
- **Le tracé est ramifié** :
  - un tronc en zigzag en diagonale, du haut-gauche vers le bas-droite, qui traverse l'icône ;
  - une branche vers le bord droit ;
  - une branche vers le bord bas.
- **Les lèvres sont blanches** (on voit le papier).
- **Les fragments bougent à peine**, de 1 à 2 % de la largeur du timbre, puis restent figés longtemps.

C'est cette économie qui rend la déchirure satisfaisante, et on la conserve. Notre apport :
- **une cause** : le claquement du couvercle déchire le papier ;
- **une matière** : épaisseur du papier, fibres, légère inclinaison 3D qui accroche la lumière ;
- **un ressort amorti** au lieu d'un arrêt sec.

## 2. Fiche technique

| Paramètre | Valeur | Pourquoi |
|---|---|---|
| Cadence | **60 i/s** | Le claquement atteint environ 10°/image. À 30 i/s on obtiendrait un effet stroboscopique et un ressort « en escalier ». |
| Durée | **60 images, f0 → f59 = 1,000 s**. Variante de sécurité : 57 images (950 ms), en coupant 3 images de la tenue finale. | Les 3 impacts (f8, f28, f36) tombent sur des images paires : une déclinaison à 30 i/s (f/2) n'en perd aucun. |
| Canevas | **1080 × 1350 px (4:5) @1x**. Master **@2x : 2160 × 2700**, toutes valeurs × 2. | Le format épouse le timbre et convient aux grilles de portfolio. |
| Échelle du timbre | **1 u (point de l'asset) = 1,8 px @1x**. Timbre de 931 × 1152 px, centré, décalage (74,55 ; 99) px. | Marges ≥ 74 px : les fragments se déplacent au maximum d'environ 25 px. |
| Fond | **Alpha 0 strict** hors silhouette : ni sol, ni ombre portée, ni halo. | Consigne 4. |
| Texte | **Zéro**. Aucun calque texte dans le projet, aucune lettre ni aucun chiffre dans l'image. | Consigne 5. |
| Couleur | Projet en sRGB, 16 bpc, sans gamma linéaire. Rendu 3D en *View Transform = Standard*. | Les codes hex de la charte restent exacts. |

**Conversion asset → canevas @1x :** `x_px = 74,55 + 1,8 × x_u` · `y_px = 99 + 1,8 × y_u`

## 3. Géométrie de référence (px @1x, canevas 1080 × 1350)

| Élément | Valeur |
|---|---|
| Silhouette perforée blanche #FFFFFF | x 74,6 → 999,3 · y 99 → 1244,8. Perforations en demi-cercle, pas ≈ 37 px. |
| Épaisseur papier #4D4D4D | Même silhouette décalée de (+6,2 ; +6,2) px |
| **Vignette = limite de l'action** | x 136,2 → 937,7 · y 160,6 → 1177,9 (801,5 × 1017,3), marge blanche de 62 px. Dégradé : #376F23 → #759663 → #D1D0C3 → **#F6E8EA** (56 %) → #E6BFC4 → #D58F99 → #BC4E5D → #A40C21 |
| **Zone de sécurité de l'action** (retrait de 24 px) | x 160,2 → 913,7 · y 184,6 → 1153,9. **Aucune pose clé n'y entre.** |
| Marmite au repos (contour sticker compris) | x 164 → 898 · y 411 → 1050. Joint couvercle/cuve y ≈ 762, sommet du bouton y ≈ 452. Ellipse d'ouverture : centre (531 ; 640), environ 540 × 245. |
| **H**, charnière du couvercle (lèvre arrière-gauche) | (267 ; 656) |
| **C**, centre du couvercle (claquements, rebonds) | (535 ; 611) |
| **B**, ancre d'écrasement (base de la cuve) | (537 ; 1030) |
| **E**, émetteur de flamme (lèvre côté ouvert) | (627 ; 647). Axe incliné de **+14°** vers la droite. Base 240 px, hauteur 100 % = 376 px. |
| Pic d'ouverture (f12) | Pointe de flamme à **(732 ; 224)**, sommet du bouton à y ≈ 231, bord libre du couvercle à (675 ; 272). Tout reste **sous y = 184,6**. |
| Déchirure | **S** amorce (99 ; 485) · **N** nœud (635 ; 823) · **E_R** sortie droite (981 ; 789) · **E_B** sortie basse (680 ; 1227) |

*Les points H, C, B et E sont à caler au pixel sur le découpage final de la marmite (voir § 4).*

## 4. Préparation des assets

### 4.1 Audit (points bloquants)
1. **La marmite est un raster unique de 512 × 512** (« Stylized Cooking Pot Icon… »). Elle n'a ni couvercle séparé, ni intérieur, ni dessous de couvercle. Agrandie, elle passe à ×1,44 @1x et ×2,9 @2x : on perd en netteté.
2. **Le contour blanc est inclus dans le raster.** Il est tronqué par les bords de l'image au niveau des anses (épaisseur de 1 à 2 px à cet endroit). Il faut le reconstruire.
3. **Les flammes du bas débordent de la vignette** de 4 u (7 px @1x). Le matte les rogne. C'est un choix assumé et invisible.
4. **La texture pailletée** (img-003) est en mode Écran. Elle doit rester posée sur la vignette opaque, jamais sur l'alpha transparent.

### 4.2 Marmite : option A, reconstruction 3D « clay » (recommandée)
**Recommandation : un pipeline hybride.** La marmite est en 3D (Blender 4.2+ ou Cinema 4D/Redshift). La flamme, le timbre, la déchirure et les mattes sont en 2D dans After Effects, dans le langage graphique plat du timbre.

- **Modélisation** (D = diamètre de la cuve) :
  - cuve : cylindre de 64 segments, hauteur 0,55 D, avec une vraie paroi et un fond intérieurs (Solidify 0,03 D) ;
  - couvercle : révolution, Ø 1,02 D, dôme de 0,10 D, jupe de 0,05 D ;
  - bouton : Ø 0,30 D, col de 0,18 D ;
  - anses : boucles à section carrée arrondie ;
  - finition : Bevel de 4 segments + Weighted Normal. Aucune arête vive : le look clay vient des congés.
- **Matériaux** : mats, Metallic 0, Roughness 0,6. Couleurs cibles rendues, mesurées sur l'icône :

  | Élément | Couleurs cibles |
  |---|---|
  | Couvercle | #B1BAC1, liseré #C7CED4 |
  | Cuve | #66747D, ombre #44525B |
  | Bouton | #57646D, flanc #2F3A3E |
  | Anses | #946A48, ombre #643E23 |
  | **Intérieur** (nouveau) | fond #1C2327, paroi #33404A |
  | **Dessous du couvercle** (nouveau) | #8F99A0 → #6F7A82 |

- **Caméra** : 100 mm, élévation 24° ± 3°, lacet de la marmite ≈ −28°. Calage par superposition sur le rendu de l'icône, tolérance ≤ 3 px @2x.
- **Lumière** :
  - key en area light haut-gauche avant ; fill à droite à 20 % ; rim arrière-droit à 30 % ; AO à 0,15 D ;
  - **point light flamme** #FFA53A dans la cuve, puissance indexée sur la hauteur de flamme. Elle réchauffe l'intérieur, la lèvre et le dessous du couvercle.
  - Film transparent, aucun sol.
- **Contour sticker** :
  - c'est une découpe : la **dilatation de l'alpha de l'union des pièces**, flamme exclue (Style de calque > Contour extérieur, **30 px @1x** (≈ 17 u, mesuré sur le raster : 21 px à 512), #FFFFFF) ;
  - pas d'inverted hull, ni de Freestyle, ni de Line Art, qui dessineraient un trait au joint couvercle/cuve.
- **Rig `CTRL_LID`** :
  - charnière sur la **lèvre arrière-gauche** : le bord droit et avant se soulève, ce qui dégage le côté droit pour la flamme ;
  - le bouton est enfant du couvercle, avec 1 image de retard ;
  - on exporte la courbe d'ouverture normalisée 0 → 1, qui pilote l'extinction (§ 6.3).
- **Passes** (PNG 16 bits RGBA droit, cadre exact du timbre) :
  - `POT_FULL` ;
  - `FRONT_MATTE` : paroi avant, demi-lèvre avant, anse avant. Il permet de faire passer la base de la flamme derrière la paroi ;
  - `LID_UNDER_MATTE` : pour le light-wrap orange.
- **Rendu** : EEVEE à 64 échantillons ou Cycles à 256 + OIDN, filtre de 1,0 px. Flou de mouvement seulement en f8–f12 et f22–f28.

### 4.3 Marmite : option B, 2,5D dans After Effects (variante UI/Lottie, délai < 1 j)
1. Agrandir le raster ×4 (Real-ESRGAN ou Gigapixel). Contrôler les couleurs : ΔE ≤ 2.
2. Découper dans Photoshop `LID` (dôme et jupe, le long du joint #2B363C), `KNOB`, `BODY`, `HANDLE_L` et `HANDLE_R`.
3. Repeindre les zones cachées dans le même modelé clay :
   - lèvre et intérieur #1C2327 → #33404A ;
   - bande de cuve sous la jupe ;
   - anse droite masquée.
4. Ancre de `LID` sur H.
5. Ouverture simulée, 22° au maximum : rotation, échelle Y de 100 à 70 % (raccourci de perspective), CC Power Pin.
6. Contour sticker : précomp d'union, puis Contour extérieur.
7. **Limite Lottie** : un raster ne passe pas proprement. Pour un livrable Lottie, redessiner la marmite en 6 à 8 aplats vectoriels.

### 4.4 Flamme (calques de forme AE, dans le langage des flammes du timbre)
- **Forme** :
  - arêtes droites, aucune courbe, **pointes aiguës de 26 à 30°** (mesurées sur l'asset) ;
  - 5 langues asymétriques penchées vers l'extérieur ;
  - langue centrale à la hauteur H, langues de flanc à 0,70 H et 0,62 H, langues extérieures à 0,40 H et 0,35 H ;
  - objet graphique plat : **pas un feu réaliste**.
- **Couches** :
  - `FL_OUT` : dégradé **#FF6B31 → #FFA53A** ;
  - `FL_MID` : Décaler les tracés −32 px @2x, jointure Angle, **#F9A825** ;
  - `FL_CORE` : −70 px @2x, **#FBD021** ;
  - `FL_GLITTER` : texture pailletée de l'asset, mode Écran à 70 %, matte = cœur ;
  - `FL_EDGE` (optionnel) : filet #FFECD1 sur les arêtes gauches ;
  - `FL_GLOW` : copie floutée de 24 px, mode Écran à 35 %.
- **Animation** :
  - **4 poses dessinées** : P0 germe 8 %, P1 jaillissement 116 % étiré, P2 pic 100 %, P3 variation 98 % ;
  - nombre de sommets identique sur toutes les poses ;
  - scintillement **« sur deux images »** (formes A/B/C renouvelées toutes les 2 images, transformations à chaque image) ;
  - Agiter les tracés, Points : Angle, taille 3 u, en `posterizeTime(30)`.
  - **Interdits** : Turbulent Displace (il arrondit les angles) et flou sur la géométrie de flamme.
- **Netteté en petite taille** :
  - langue ≥ 12 u à la base, écart ≥ 10 u entre les couches ;
  - variante UI (≤ 300 px de haut) : 3 langues, grain ×2, sans `FL_EDGE`.

### 4.5 Timbre
`STAMP_MASTER`, de bas en haut :
1. `PAPER_GREY` (#4D4D4D, décalé)
2. `PAPER_WHITE`
3. `VIGNETTE` (dégradé de l'asset, stops inchangés)
4. `ACTION` (précomp sous matte, voir § 6.5)
5. `MATTE_VIGNETTE` (guide invisible)

Une variante `STAMP_MASTER_NOGREY` sert aux fragments.

## 5. Chronométrie image par image (60 i/s)

Abréviations :
- **Couvercle** : rotation écran / ΔY en px. Pivot **H** pendant l'ouverture et la fermeture, pivot **C** pendant les claquements et les rebonds.
- **Flamme** : sY/sX, ancrées en **E**.
- **Cuve** : sX/sY, ancrées en **B**.
- **×** : multiplicateur des transformations finales des fragments (§ 6.4).
- Les angles du couvercle sont des valeurs 2D proxy. En 3D, on cale l'angle réel pour que la projection passe par ces poses.

| Img | ms | Phase | Couvercle | Flamme | Cuve sX/sY | Timbre / fragments | Courbe · flou |
|---|---|---|---|---|---|---|---|
| f0 | 0 | **Repos** (image-affiche) | 0° / 0 | — | 100/100 | intact | — |
| f1 | 17 | Anticipation : claquement 1 (pivot C) | −1,5° / −3 | — | 100/100 | — | 1 clé/image · 0° |
| f2 | 33 | contact | 0 / 0 | — | 100,5/99,5 | — | |
| f3 | 50 | claquement 2 | +2° / −5 | — | 100/100 | — | amplitude croissante |
| f4 | 67 | contact | 0 / 0 | — | 101/99 | — | |
| f5 | 83 | claquement 3 | −2,5° / −7 | lueur de fente #FBD021 à 20 % | 100/100 | — | la lumière précède le feu |
| f6 | 100 | contact | 0 / 0 | lueur à 0 | 101/99 | — | |
| f7 | 117 | **Compression** | 0° / **+2** | — | **102/97** | — | le couvercle s'enfonce |
| **f8** | 133 | **POP, impact 1** (pivot H) | −17,6° / −16,4 | flash de fente #FFECD1 à 40 % | **98/103** | — | `cubic-bezier(0.33,1,0.68,1)` f7→f12 · 180° |
| f9 | 150 | ouverture | −28,2° / −26,3 | **naissance** : sY 35 %, sX 60 % | 99/101,5 | — | flamme `cubic-bezier(0.34,1.56,0.64,1)` f8→f14 |
| f10 | 167 | | −33,7° / −31,4 | sY 80 %, sX 75 %, smear de pointe à 130 % | 100/100 | — | 180° |
| f11 | 183 | | −35,7° / −33,4 | 108 / 88 | — | — | 90° |
| **f12** | 200 | **Pic d'ouverture** | **−36° / −33,6** | **pic à 116 %**, pointe en (732 ; 224) | — | — | `cubic-bezier(0.37,0,0.63,1)` f12→f15 |
| f13 | 217 | stabilisation | −34,6° / −32,8 | 108 / 102 | — | — | |
| f14 | 233 | | −33° / −32,2 | 100 %, pose A | — | — | |
| f15–f19 | 250–317 | **Flottement** | ±1,5° / ±2 px autour de −32° / −32 | poses A/B/C sur deux images, 97–104 % | — | — | 1 clé/image · 90° |
| f20 | 333 | **Armement** | −34° / −34,4 | C 104 % | — | — | `cubic-bezier(0.5,1,0.89,1)` |
| f21 | 350 | | −35° / −35,2 | A 106 % (dernière bouffée) | — | — | |
| f22 | 367 | **Fermeture et extinction** | −34,3° / −34,5 | 98 % (liée à l'angle) | — | — | `cubic-bezier(0.11,0,0.5,0)` f21→f28 · 90° |
| f23 | 383 | | −32,1° / −32,3 | 94 % | — | — | |
| f24 | 400 | | −28,6° / −28,7 | 86 %, occlusion par le bord du couvercle | — | — | 180° |
| f25 | 417 | | −23,6° / −23,7 | 74 %. **Pincement** : les 30 % du haut se détachent (+14 px/image) | — | — | |
| f26 | 433 | | −17,1° / −17,3 | 58 %, la langue détachée se refroidit (pointes #A40C21) | — | — | 270° |
| f27 | 450 | | −9,3° / −9,3 | 37 % : jet aplati dans la fente | — | — | 270° |
| **f28** | 467 | **CLAC, impact 2** | **0° / 0** (repérage au pixel) | **0 % : éteinte**, langue comprise | **105/94** | micro-secousse : ΔY +4, +0,5°, éch. 99,2 % | **0° forcé** |
| f29 | 483 | rebond (pivot C) | −6 px, +1,8° | — | 102/98 | ΔY −2,4, −0,35°, 100,4 % | 45° |
| f30 | 500 | | −2,4 px, +0,6° | — | 98,5/102,5 | +1,6, +0,2° | |
| f31 | 517 | 2ᵉ contact | 0 / 0 | — | 99,5/100,8 | −0,8, −0,1° | |
| f32 | 533 | | −1,6 px, −0,5° | — | 100,3/99,7 | 0 | 0° |
| f33 | 550 | **Tension** | 0 / 0 | — | 100/100 | **intérieur figé**. Le papier se tend (sX 100,5 / sY 99,7) avec une marque de stress blanche de 10 px au creux S. | — |
| f34 | 567 | **Amorce de déchirure** | — | — | — | entaille au creux S, front principal à 25 % | front **linéaire** · 0° |
| f35 | 583 | propagation | — | — | — | front principal à 100 % (jusqu'à N), branche A à 40 %, branche B à 35 %. **F1 démarre** : +0,4°, T(−0,8 ; −1,6). | 0° |
| **f36** | 600 | **CRAC, impact 3** | — | — | — | branches à 100 %, 3 fragments libres, **×0,60** | ressort ζ 0,32 / 10 Hz · 90° |
| f37 | 617 | séparation | — | — | — | ×1,10, l'épaisseur devient visible | 90° |
| **f38** | 633 | **Pic de séparation** | — | — | — | **×1,35** | 45° |
| f39 → f46 | 650–767 | ressort amorti | — | — | — | ×1,23 → 1,00 → **0,88** → 0,92 → 1,00 → 1,04 → 1,03 → 1,00 | 0° |
| f47 | 783 | **Repos** | — | — | — | ×1,00 imposé (résidu ≤ 0,5 px) | |
| **f48–f59** | 800–983 | **Tenue finale** (12 images, 200 ms) | — | — | — | figé, zéro bruit, zéro « boil » | |

**Rythme** : l'écart entre impacts se resserre (20 images entre le pop et le clac, 8 entre le clac et le crac), puis viennent 12 images de silence, qui sont la récompense. Le déroulé est conforme à la consigne :
- ouverture f8 ;
- flamme f9–f27 ;
- **fermeture et extinction de f22 à f28, flamme à 0 % sur l'image même du contact** ;
- déchirure dès f33/f34, soit 100 ms après le contact.

## 6. Mécaniques clés

### 6.1 Ouverture
- Le couvercle « tousse » trois fois, d'amplitude croissante, s'enfonce (f7), puis **saute** : 49 % de la course est parcourue en une seule image (f8).
- Le bouton suit avec 1 image de retard.
- La cuve s'étire (98/103), puis revient.
- En 3D, l'ouverture (≈ 38° réels) dépasse la vue de tranche. Le **dessous du couvercle, chauffé en orange**, apparaît : c'est la plus-value de la 3D.

### 6.2 Flamme
- Elle part **1 image après** le couvercle. Sa vitesse se lit par le **smear dessiné** à f10 (pointe étirée à 130 %), pas par le flou.
- Pic à 116 % à f12, puis stabilisation.
- Pendant le flottement, elle « lèche » le bord libre du couvercle, qui flotte comme une soupape.
- Sa lumière (point light ou solide #FF6B31 en Incrustation à 30 % × ouverture) reste dans la vignette.

### 6.3 Fermeture et extinction **simultanées** : trois verrous

**1. Occlusion (guillotine)**
- Ordre des calques : `intérieur < FLAMME < paroi avant + anses < COUVERCLE`.
- En redescendant, le couvercle recouvre la flamme par le haut. En 3D, l'occlusion est native.

**2. Matte de fente**
- Quadrilatère entre la lèvre et le dessous du couvercle, parenté à H, utilisé comme alpha matte de la base de la flamme.
- Son aire devient **nulle à f28**.

**3. Lien mathématique** (expression AE sur l'échelle de la flamme, ancre en E)
```js
// FLAMME › Échelle — de f22 à f28, la flamme est esclave de l'angle du couvercle
var a = Math.abs(thisComp.layer("COUVERCLE_H").transform.rotation);
if (timeToFrames(time) < 22) value; else {
  var k = Math.pow(clamp(a / 35, 0, 1), 0.75);   // 1 → 0 exactement au contact
  [value[0] * (0.7 + 0.3 * k), value[1] * k];     // s'aplatit en jet, puis s'éteint
}
```
Opacité de la flamme : `timeToFrames(time) >= 28 ? 0 : value`.

**Résultat** :
- la flamme passe de 98 à 94, 86, 74, 58, 37, puis **0 %** ;
- la langue détachée par pincement à f25 meurt aussi à f28 ;
- **aucune fumée, aucune braise** : le claquement met fin au feu, et rien ne le prolonge.

### 6.4 Déchirure

**Tracé** (px @1x). Les segments longs font 90 à 160 px. Les crans courts font 26 à 32 px, à ±60–80° de la direction principale. On ajoute un bruit fractal de 2 à 4 px pour lire « papier » et non « vecteur ».

| Branche | Points |
|---|---|
| **Tronc** | S(99 ; 485) → (207 ; 552) → (233 ; 537) → (345 ; 637) → (372 ; 623) → (491 ; 733) → (519 ; 720) → **N(635 ; 823)** |
| **Branche A** (vers la droite) | N → (724 ; 797) → (745 ; 813) → (849 ; 785) → (871 ; 800) → **E_R(981 ; 789)** |
| **Branche B** (vers le bas) | N → (657 ; 913) → (638 ; 936) → (670 ; 1049) → (652 ; 1077) → **E_B(680 ; 1227)** |

**Règles de tracé** :
- chaque extrémité tombe **dans un creux de perforation**, là où le papier cède ;
- le tronc coupe la cuve et le bord avant-gauche du couvercle, et **épargne le bouton** : l'icône reste lisible sur F1.

**Vitesse** : environ 450 px/image. Le front est **linéaire** (une fracture va à vitesse constante). Les lèvres apparaissent pleine largeur juste derrière le front. Pas de flou.

**Fragments.** Chaque fragment pivote autour de son dernier point attaché.

| Fragment | Surface | Pivot | Final ×1,00 (f47 → f59) | Pic ×1,35 (f38) |
|---|---|---|---|---|
| **F1** haut (bouton, couvercle, haut de la cuve) | ≈ 57 % | E_R | rot **+1,1°**, T(−2,4 ; −4,8), rotY −2° | +1,5°, T(−3,2 ; −6,5), rotY −4° |
| **F2** bas-gauche (anse gauche) | ≈ 28 % | E_B | rot **−0,8°**, T(−6,4 ; +4,8), rotX +1,5° | −1,1°, T(−8,6 ; +6,5), rotX +3° |
| **F3** bas-droit | ≈ 15 % | E_B | rot **+0,8°**, T(+6,4 ; +4,8), rotY +1,5° | +1,1°, T(+8,6 ; +6,5), rotY +3° |

- Écartements au repos : **≈ 40 px au point S**, qui se resserrent à ≈ 19 px au nœud N ; ≈ 20 px sur la branche A ; ≈ 24 → 13 px sur la branche B.
- Ressort : ζ 0,32, 10 Hz. Pour un moteur de ressort : `stiffness 4400, damping 42, mass 1`.

**Matière** :
- **Lèvres fibreuses #FFFFFF.** Lèvre large (8 à 11 px) sur F1, étroite (3 à 5 px) sur F2 et F3 : la couche imprimée se décolle d'un seul côté.
  - Bords irréguliers : bordure 5 px, échelle 35, évolution figée.
  - En @2x seulement : 20 à 30 micro-fibres de 1 à 3 px.
  - Liseré intérieur de 1 px en #4D4D4D à 25 %, pour rester lisible sur un fond blanc.
- **Épaisseur.** Ombre portée #4D4D4D, opacité 100 %, adoucissement 0, distance 8,8 px @1x à 135°. On retrouve exactement l'épaisseur de l'asset. Au pic d'inclinaison, la tranche visible atteint 5 à 8 px.
- **Inclinaison 3D.** Caméra AE à un nœud, zoom ≥ 4000 px, rendu quasi orthographique. L'inclinaison se lit **par la lumière** (±3 à 5 % de luminance) et par la tranche, jamais par une déformation de perspective.
- **Interstice** : vrai trou, alpha 0, sans ombre sur le fond.

**Construction sans couture** :
1. Les 3 formes sortent d'un seul tracé passé dans **Pathfinder > Diviser** : elles partagent exactement leurs sommets.
2. `FRAG_i` = une instance de `STAMP_MASTER_NOGREY` sous le matte `FRAG_i_SHAPE`. Tout le contenu de la vignette (marmite, flammes, dégradé) se déchire avec son fragment, sans parentage manuel.
3. Jusqu'à f32, le timbre est affiché intact. **Bascule sur les fragments à f33**, superposés au pixel près (contrôle en mode Différence = 0, écart ≤ 1/255).
4. Les lèvres sont révélées par Trim Paths de 0 à 100 % entre f34 et f36, depuis S vers N, puis sur les deux branches en même temps.

### 6.5 Confinement « strictement dans le timbre »

**Frontière dure : la vignette.**
- Couvercle, bouton, flamme, glow, light-wrap, flammes du bas et paillettes vivent dans le précomp `ACTION`.
- Ce précomp est sous un **track matte alpha** `MATTE_VIGNETTE` (801,5 × 1017,3 px en (136,2 ; 160,6), contour progressif 0).
- Glow et flou sont calculés **dans** `ACTION`. Le matte s'applique en dernier.

**Frontière de conception : la zone de sécurité** (retrait de 24 px).
- Aucune pointe ni aucun bord n'y entre.
- **Le matte est une assurance invisible.** Une flamme visiblement rognée par le matte est une erreur d'animation.

**Ordre des événements.**
- La silhouette perforée ne change qu'à la déchirure.
- **Tout l'intérieur est mort et figé dès f33**. Après, seul le papier bouge.

## 7. Courbes et flou de mouvement

| Usage | Courbe |
|---|---|
| Ouverture (pop) | `cubic-bezier(0.33, 1, 0.68, 1)` |
| Naissance de la flamme (dépassement) | `cubic-bezier(0.34, 1.56, 0.64, 1)` |
| Stabilisation et flottement | `cubic-bezier(0.37, 0, 0.63, 1)` |
| Armement | `cubic-bezier(0.5, 1, 0.89, 1)` |
| Claquement (sans freinage au contact) | `cubic-bezier(0.11, 0, 0.5, 0)` |
| Front de fissure | `linear` |
| Fragments | ressort ζ 0,32 / 10 Hz (ou clés ×) |

Aucune transformation n'est en linéaire, sauf le front de fissure.

| Phase | Images | Obturateur |
|---|---|---|
| Claquements d'anticipation | f1–f7 | 0° (des micro-amplitudes floutées deviennent de la bouillie) |
| Pop | f8–f10 | **180°**, 16 échantillons |
| Pic, flottement, armement | f11–f23 | 90° |
| Claquement | f24–f27 | 180° → **270°** |
| **Impact** | **f28** | **0° forcé** (image du coup nette comme un rasoir) |
| Rebonds | f29–f33 | 45° → 0° |
| **Fissure** | **f34–f36** | **0°** (une révélation, pas un mouvement) |
| Séparation | f36–f38 | 90° → 45° |
| Ressort et tenue | f39–f59 | 0° |
| Flamme (toutes phases) | — | 0° sur la géométrie : la vitesse passe par le smear et les poses sur deux images |

## 8. Rendu, alpha et livrables

**Propreté de l'alpha** :
- PNG en alpha **droit**, EXR en **prémultiplié**. Toujours interpréter explicitement, jamais en mode « Deviner ».
- Les modes Écran ou Ajout et les glows sont toujours posés sur la vignette opaque. Les seuls bords semi-transparents sont l'anticrénelage des perforations, des fragments et des fibres.
- Hors silhouette : **alpha = 0 strict**. Aucun pixel ne doit avoir un alpha de 1 à 3/255.

| Livrable | Spécifications | Usage |
|---|---|---|
| **Séquence PNG (maître)** | RGBA 16 bits, alpha droit, 2160 × 2700, images 0000–0059 | archive, source de tous les encodages |
| **ProRes 4444 XQ** (.mov) | 2160 × 2700 et 1080 × 1350, 60p, alpha droit | reel portfolio, Premiere, Resolve |
| **WebM VP9 + alpha** | 1080 × 1350 et 432 × 540, CRF 20, ≤ 1,5 Mo | web (Chrome, Edge, Firefox) |
| **HEVC + alpha** (.mov hvc1) | 1080 × 1350, 60p, ≤ 2 Mo | Safari macOS et iOS |
| **WebP animé / APNG** | 240 × 300, 480 × 600, 720 × 900, lecture unique | UI |
| Lottie / dotLottie | seulement avec l'option B en vectoriel, ≤ 120 Ko gzip | web et app légers |

```bash
# ProRes 4444 XQ (master)
ffmpeg -framerate 60 -i MOR_stampPot-tear_v001_2160x2700_%04d.png -c:v prores_ks -profile:v 4444xq \
  -pix_fmt yuva444p10le -alpha_bits 16 -vendor apl0 MOR_stampPot-tear_v001_2160x2700_60p_PR4444XQ.mov
# WebM VP9 + alpha (redimensionnement prémultiplié pour éviter les franges)
ffmpeg -framerate 60 -i MOR_stampPot-tear_v001_2160x2700_%04d.png \
  -vf "premultiply=inplace=1,scale=1080:1350:flags=lanczos,unpremultiply=inplace=1" \
  -c:v libvpx-vp9 -pix_fmt yuva420p -crf 20 -b:v 0 -auto-alt-ref 0 -row-mt 1 MOR_stampPot-tear_v001_1080x1350_60p_vp9a.webm
# HEVC + alpha (macOS, VideoToolbox)
ffmpeg -framerate 60 -i MOR_stampPot-tear_v001_1080x1350_%04d.png -c:v hevc_videotoolbox \
  -alpha_quality 0.9 -b:v 8M -tag:v hvc1 MOR_stampPot-tear_v001_1080x1350_60p_hevca.mov
```

**Intégration web** :
- Lecture **unique, sans boucle** : la vidéo se fige sur f59. Le passage de déchiré à intact ne boucle pas proprement.
- Déclenchement au survol, ou au scroll via un IntersectionObserver à 50 %.
- Avec `prefers-reduced-motion` : afficher l'image fixe f59.
- Image `poster` = f0.

```html
<video muted playsinline preload="auto" poster="stamp_f00.png" width="1080" height="1350">
  <source src="stamp_hevc_alpha.mov" type='video/quicktime; codecs="hvc1"'>
  <source src="stamp_vp9_alpha.webm" type="video/webm">
</video>
```

**Nommage** : `MOR_stampPot-tear_v###_<L>x<H>_<fps>p_<codec>`, versions incrémentées, jamais « final ». Préfixes des calques : `CTRL_`, `POT_`, `FL_`, `FRAG_`, `FIBER_`, `MATTE_`.

## 9. Check-list QA

**Temps**
- [ ] 60 images exactes à 60 i/s (vérification `ffprobe -count_frames`) ; 30 images en 30 i/s.
- [ ] Ordre : pop à f8 → flamme f9–f27 → fermeture et extinction f22→f28 → fissure f34–f36.
- [ ] La flamme est **à 0 % à f28 et après**. Rien ne la prolonge (ni fumée, ni braise).
- [ ] La déchirure démarre au plus tard 6 images après le contact (f34).

**Limites**
- [ ] Rendu de contrôle « ACTION seule » : alpha = 0 hors de la vignette sur les 60 images (script avec seuil).
- [ ] Aucune pose clé dans la bande de sécurité de 24 px. Le matte ne rogne rien de visible.
- [ ] Hors silhouette : alpha = 0 strict. Marge ≥ 64 px au bord du canevas @2x.

**Alpha et look**
- [ ] Contrôle sur #000, #FFF, #808080, damier et couleurs de la charte (#2A5519, #7B1421, #FFECD1) : aucun halo sur les perforations, le contour ou les fibres.
- [ ] Aucune couture de f0 à f32, aucun saut à la bascule de f33 (écart ≤ 1/255).
- [ ] Repérage parfait à f28 : le contour du couvercle se fond dans celui de la cuve à 0 px près.
- [ ] Codes hex conformes, ΔE2000 ≤ 3 : stops de la vignette, flammes, échantillons de la marmite.
- [ ] Lecture claire à 300 px et à 64 px de haut : l'ouverture, la flamme et la déchirure restent identifiables.

**Exclusions**
- [ ] Aucun calque texte (comptage par script ExtendScript). Ni lettre, ni chiffre, ni oblitération, ni filigrane.
- [ ] Dernière image (f59) : affiche propre et nette, utilisable telle quelle en vignette.

---

## 10. Prompt d'animation

### 10.1 Prompt maître (EN) : générateurs IA et brief motion designer

```text
[FORMAT] A 1.0-second micro-animation: 60 frames at 60 fps, portrait 4:5, 1080×1350 px, one single isolated object. Background: none — fully transparent alpha channel. (If the tool cannot output alpha: a perfectly flat, uniform pure blue #0033FF backdrop for chroma keying — no gradient, no shadow, no reflection.) Locked-off camera, straight-on front view, orthographic look (very long lens, zero perspective distortion). No camera movement of any kind.

[SUBJECT] One vintage postage stamp, upright and centered, 931×1152 px. Border: flat white paper (#FFFFFF) with a regular scalloped perforated edge (half-circle perforations, ~37 px pitch), plus a flat dark grey (#4D4D4D) copy of the perforated silhouette offset 6 px right and 6 px down, reading as paper thickness. Inside: a rectangular picture area (802×1017 px, 62 px white margin) with a smooth vertical gradient — deep leaf green #376F23 at the top, sage #759663, greige #D1D0C3, powder pink #F6E8EA just below mid-height, dusty rose #D58F99, crimson #A40C21 at the bottom. Along the bottom of the picture area: flat graphic flames made of sharp angular zigzag spikes in an orange gradient (#FFA53A to #FF6B31) with a fine golden-pink glitter grain in screen blend. Centered, overlapping those flames: a soft-3D "clay" cooking pot icon in three-quarter view from slightly above — matte blue-grey cylindrical body (#66747D lit side, #44525B shadow side), domed pale grey lid (#B1BAC1) with a lighter rim (#C7CED4), round dark slate knob (#57646D), two rounded brown wooden handles (#946A48), the whole pot wrapped in a thick white die-cut sticker outline (~30 px). Soft top-left key light, gentle ambient occlusion, no cast shadow. Design, colours and proportions stay identical from first to last frame.

[ACTION — exact timing at 60 fps]
0.000–0.117 s (f0–7), pressure: the lid chatters three times with growing amplitude (3, 5, 7 px), then the lid sinks 2 px and the pot compresses (height −3%).
0.133 s (f8), POP: the lid snaps open, hinging on its back-left rim; its right/front edge flips up to about 36° and the lid lifts ~34 px, with a very fast ease-out (half the travel in one frame). The knob follows one frame late. The pot's dark charcoal interior (#1C2327) is revealed; the lid's underside glows warm orange.
0.150–0.200 s (f9–12), a flame bursts out of the open side, leaning 14° to the right: stylised, faceted tongues with sharp 26–30° tips, in the same angular language as the stamp's bottom flames — outer #FF6B31→#FFA53A, mid #F9A825, core #FBD021, the same glitter grain. Springy overshoot to 116% at f12; its highest tip stays at least 60 px below the top edge of the picture area. A drawn speed-smear on the tip at f10, no blur on the flame.
0.200–0.350 s (f12–21), hang: the lid floats on the flame like a pressure valve (±1.5°, ±2 px); the flame flickers, animated on twos for a crisp graphic feel.
0.367–0.467 s (f22–28), CLOSE AND EXTINGUISH SIMULTANEOUSLY, in one single motion: the lid slams down with a gravity-like accelerating ease-in; the descending lid edge guillotines the flame, whose height is driven by the lid angle (98%, 94%, 86%, 74%, 58%, 37%…) — the top third of the flame pinches off and cools to crimson — and the flame reaches exactly zero on the very frame the lid lands (f28). No smoke, no embers, no sparks: the slam ends the fire.
0.467–0.550 s (f28–33), impact: the pot squashes (105/94%) and rebounds; the lid bounces 6 px twice and settles; the whole stamp gives a tiny 4 px / 0.5° shudder, then holds still. From f33 nothing inside the picture moves any more.

[CONTAINMENT] The lid, the flame, its glow and every moving part stay strictly inside the stamp's inner picture rectangle with a 24 px safety margin; nothing ever overlaps the white perforated border or leaves the stamp. Apart from the tiny shudder at the slam, the stamp does not move until the tear.

[TEAR — right after the slam]
0.567–0.600 s (f34–36): a sharp, branched crack shoots across the stamp in 3 frames, starting in a perforation notch on the left edge (~33% down), zigzagging diagonally through the pot (missing the knob) to a node at ~61% across / 63% down, then splitting into one branch to the right edge and one branch to the bottom edge, each ending in a perforation notch. Crisp, no motion blur.
0.600–0.783 s (f36–47): the stamp separates into three clean paper fragments that spring apart with a damped overshoot (peak at f38) and settle: gaps of ~40 px at the left start narrowing to ~20 px, rotations of 0.8–1.5°, a slight 3D tilt (≤4°) that catches the light. The upper fragment, carrying the lid and the knob, opens the most. Torn edges are crisp white fibrous paper lips (3–11 px, wider on the upper piece) with the grey paper thickness visible; the gaps are fully transparent.
0.800–1.000 s (f48–59): perfectly still final hold on the torn stamp.
It is paper tearing, not burning: no char, no scorch.

[STYLE] Premium 3D-icon motion design: soft clay render for the pot, flat graphic flames, readable even at small size, ultra-snappy and satisfying, three crisp hits (pop · slam · crack), top-studio polish. Motion blur only on the lid moves; the impact frame and the tear stay razor sharp. Total duration 1.0 second maximum. No text, letters or numbers anywhere.
```

### 10.2 Prompt négatif (EN)

```text
text, letters, words, numbers, typography, denomination value, price, country name, postmark, cancellation lines, rubber ink stamp, signature, logo, watermark, UI, subtitles,
background scene, table, desk, envelope, paper backdrop, floor, wall, gradient backdrop, vignette around the frame, shadow on the background, drop shadow outside the stamp, reflection, bokeh, depth of field, lens flare, glow leaking outside the stamp,
hands, fingers, people, kitchen, stove, food, soup, liquid, steam, smoke, embers, sparks, extra pots, extra objects,
photorealistic fire, volumetric fire, fire spreading to the paper, burning paper, charred or scorched edges, ash,
camera movement, pan, tilt, zoom, dolly, orbit, camera shake, handheld, stamp sliding or rotating before the tear,
warping, morphing, melting, jelly deformation, change of pot design, change of colours, extra handles, missing knob,
slow motion look, frame drops, motion blur on the tear, blurry, low resolution, compression artifacts, noise
```

### 10.3 Prompt maître (FR) : brief motion designer

```text
[FORMAT] Micro-animation de 1,0 seconde : 60 images à 60 i/s, portrait 4:5, 1080 × 1350 px, un seul objet isolé. Fond : aucun, canal alpha entièrement transparent (à défaut : fond bleu pur #0033FF parfaitement plat pour l'incrustation). Caméra verrouillée, vue de face, rendu orthographique, aucun mouvement de caméra.

[SUJET] Un timbre-poste vintage, droit et centré, 931 × 1152 px. Bordure : papier blanc plat #FFFFFF à bord dentelé régulier (perforations en demi-cercle, pas ≈ 37 px), doublée d'une copie gris foncé #4D4D4D de la silhouette perforée décalée de 6 px vers la droite et 6 px vers le bas (l'épaisseur du papier). À l'intérieur : une zone d'image rectangulaire (802 × 1017 px, marge blanche de 62 px) en dégradé vertical, vert feuille #376F23 en haut, sauge #759663, grège #D1D0C3, rose poudre #F6E8EA juste sous la mi-hauteur, vieux rose #D58F99, cramoisi #A40C21 en bas. En bas de la zone : des flammes graphiques plates en pointes anguleuses, dégradé orange #FFA53A → #FF6B31, recouvertes d'un grain pailleté or-rose en mode Écran. Au centre, chevauchant ces flammes : une icône de marmite en 3D douce « pâte à modeler », vue de trois quarts légèrement plongeante — cuve cylindrique gris-bleu mat (#66747D côté lumière, #44525B côté ombre), couvercle bombé gris clair #B1BAC1 à liseré #C7CED4, bouton ardoise #57646D, deux anses arrondies en bois brun #946A48, le tout entouré d'un épais contour blanc de type sticker (≈ 30 px). Lumière douce haut-gauche, occlusion légère, aucune ombre portée. Design, couleurs et proportions identiques de la première à la dernière image.

[ACTION — timing exact à 60 i/s]
0,000–0,117 s (i0–7), pression : le couvercle claque trois fois, d'amplitude croissante (3, 5, 7 px), puis s'enfonce de 2 px pendant que la cuve se tasse (hauteur −3 %).
0,133 s (i8), POP : le couvercle s'ouvre d'un coup en pivotant sur sa lèvre arrière-gauche ; son bord droit et avant se soulève jusqu'à ≈ 36° et l'ensemble monte d'environ 34 px, avec une décélération très rapide (la moitié de la course en une image). Le bouton suit avec une image de retard. L'intérieur anthracite (#1C2327) apparaît ; le dessous du couvercle s'éclaire en orange chaud.
0,150–0,200 s (i9–12), une flamme jaillit du côté ouvert, inclinée de 14° vers la droite : langues stylisées et facettées, pointes aiguës de 26 à 30°, dans le même langage anguleux que les flammes du bas du timbre — extérieur #FF6B31 → #FFA53A, milieu #F9A825, cœur #FBD021, même grain pailleté. Dépassement élastique à 116 % (i12) ; sa pointe la plus haute reste au moins 60 px sous le bord haut de la zone d'image. Un étirement dessiné de la pointe à i10, aucun flou sur la flamme.
0,200–0,350 s (i12–21), suspension : le couvercle flotte sur la flamme comme une soupape (±1,5°, ±2 px) ; la flamme scintille, animée sur deux images pour un rendu graphique net.
0,367–0,467 s (i22–28), FERMETURE ET EXTINCTION SIMULTANÉES, en un seul mouvement : le couvercle retombe en accélérant comme sous l'effet de la gravité ; son bord descendant sectionne la flamme, dont la hauteur est pilotée par l'angle du couvercle (98 %, 94 %, 86 %, 74 %, 58 %, 37 %…) — le tiers supérieur se détache et se refroidit en cramoisi — et la flamme atteint exactement zéro sur l'image même où le couvercle se pose (i28). Ni fumée, ni braise, ni étincelle : le claquement met fin au feu.
0,467–0,550 s (i28–33), impact : la cuve s'écrase (105/94 %) puis rebondit ; le couvercle rebondit deux fois de 6 px et se pose ; le timbre entier frissonne d'à peine 4 px / 0,5°, puis s'immobilise. À partir de i33, plus rien ne bouge à l'intérieur de la zone d'image.

[CONFINEMENT] Le couvercle, la flamme, sa lueur et toute partie mobile restent strictement dans le rectangle intérieur du timbre, avec une marge de sécurité de 24 px ; rien ne chevauche jamais la bordure perforée blanche ni ne sort du timbre. Hormis le frisson au claquement, le timbre ne bouge pas avant la déchirure.

[DÉCHIRURE — juste après le claquement]
0,567–0,600 s (i34–36) : une fissure nette et ramifiée traverse le timbre en 3 images. Elle part d'un creux de perforation du bord gauche (≈ 33 % de la hauteur), zigzague en diagonale à travers la marmite (en épargnant le bouton) jusqu'à un nœud à ≈ 61 % de la largeur et 63 % de la hauteur, puis se divise en une branche vers le bord droit et une branche vers le bord bas, chacune finissant dans un creux de perforation. Nette, sans flou.
0,600–0,783 s (i36–47) : le timbre se sépare en trois fragments de papier nets, qui s'écartent avec un dépassement amorti (pic à i38) puis se posent : écart de ≈ 40 px au départ gauche qui se resserre vers ≈ 20 px, rotations de 0,8 à 1,5°, légère inclinaison 3D (≤ 4°) qui accroche la lumière. Le fragment du haut, qui porte le couvercle et le bouton, s'ouvre le plus. Bords déchirés : lèvres de papier blanches et fibreuses (3 à 11 px, plus larges sur le fragment du haut), épaisseur grise visible ; les interstices sont entièrement transparents.
0,800–1,000 s (i48–59) : tenue parfaitement immobile sur le timbre déchiré.
C'est du papier qui se déchire, pas qui brûle : ni carbonisation, ni roussi.

[STYLE] Motion design d'icône 3D haut de gamme : rendu « pâte à modeler » doux pour la marmite, flammes graphiques plates, lisible même en petit, ultra-vif et satisfaisant, trois coups nets (pop · clac · crac), finition de grand studio. Flou de mouvement uniquement sur les mouvements du couvercle ; l'image d'impact et la déchirure restent parfaitement nettes. Durée totale : 1,0 seconde maximum. Aucun texte, aucune lettre, aucun chiffre nulle part.
```

### 10.4 Version compacte (< 1 000 caractères, pour les outils limités)

```text
Locked-off front view, orthographic look, 1 second, 60 fps. A vintage postage stamp (white scalloped perforated border, grey offset edge, green-to-powder-pink-to-crimson vertical gradient picture, flat angular orange glitter flames at the bottom) holding a soft-3D clay cooking pot icon (blue-grey body, pale grey domed lid, dark knob, brown wooden handles, thick white sticker outline). The lid chatters, pops open on its back-left rim, a stylised angular orange-gold flame bursts out; then the lid slams shut and snuffs the flame in the same motion — flame at zero on the landing frame, no smoke. Everything strictly inside the stamp's picture area. Right after, the stamp tears crisply along a branched zigzag crack into three paper pieces with white fibrous edges that spring apart a few pixels and settle. Snappy, satisfying, premium. Transparent background (or flat #0033FF). No text.
```

### 10.5 Variante par images clés (image-to-video, première et dernière image)

Avec seulement une première et une dernière image où le couvercle est fermé, la plupart des modèles **sautent l'ouverture**. Il faut donc enchaîner deux générations raccordées sur K1. Les images clés se fabriquent hors IA :
- rendu du .ai à 1080 × 1350 sur #0033FF ;
- couvercle découpé pour K1 ;
- déchirure vectorielle dans Illustrator pour K3.

```text
K0 — START (f0, 0.000 s): front orthographic view of the stamp on flat #0033FF; clay pot with lid closed; intact stamp; no flame above the pot; no text.
K1 — PEAK (f12, 0.200 s): same stamp untouched; lid hinged open ~36° on its back-left rim, dark interior visible, stylised angular orange-gold flame bursting out leaning right, tip 60 px below the top of the picture area, orange glow under the lid; all inside the picture area; no text.
K2 — IMPACT (f28, 0.467 s, optional): same stamp; lid shut; pot slightly squashed; no flame, no smoke; no text.
K3 — END (f59, 1.000 s): same stamp torn into three paper fragments along the branched zigzag crack (left notch → node → right edge / bottom edge), separated by ~20–40 px, rotated ~1°, crisp white fibrous edges, grey thickness; pot closed; not burnt; flat #0033FF; no text.
Clip A (K0→K1): "Locked camera. The lid pops open on its back-left rim and a stylised angular flame bursts out, staying inside the stamp's picture area. The stamp does not move. Fast, snappy. No text."
Clip B (K1→K3): "Locked camera. The lid slams shut and snuffs the flame in the same motion, then the stamp tears crisply into three paper pieces that spring apart slightly and settle. No smoke, no burning. No text."
```

### 10.6 Notes de production IA

**Alpha.**
- La plupart des générateurs sortent du H.264/H.265 sans alpha. On génère alors sur **#0033FF**, puis on détoure.
- Pourquoi pas les autres couleurs :
  - pas le vert : le tiers haut de la vignette est vert ;
  - pas le magenta ni le rouge : toute la moitié basse est rose ou rouge ;
  - pas l'orange ni le jaune : ce sont les flammes ;
  - pas le blanc ni le noir : ce sont la bordure et les contours.
- Le bleu est la seule famille de teinte absente. Le gris-bleu de la cuve n'est saturé qu'à 15–25 %.
- Keylight : Screen Colour #0033FF, Clip Black 15–20, Clip White 80–85, Shrink −1 px.

**Pipeline recommandé.**
- Le clip IA sert de **référence de mouvement (animatique)**, puis on reconstruit selon les § 4 à 6. Les modèles déforment une fracture sur un dessin rigide : **la déchirure se fait toujours dans After Effects**.
- Alternative hybride : générer uniquement la zone intérieure de la vignette, qui est opaque (donc sans alpha nécessaire), puis la caler sous la bordure vectorielle d'origine.

**Tenir la seconde.**
- Générer 3 à 5 s en demandant `slow motion, the action fills the whole clip`, puis compresser à 1 s. Par exemple, 3 s à 20 i/s donnent 60 images.
- **Ne jamais interpoler à travers f28 ni f34–f38** (images fantômes, fissure molle).

**Garder le timbre immobile.**
- Image-to-video avec K0 en première image, caméra « static », intensité de mouvement basse, pinceau de mouvement limité à la marmite.
- En post, reprendre la bordure vectorielle par-dessus chaque image et contrôler en mode Différence par rapport à f0 : noir jusqu'à f27.

**Itérations.**
- Figer la seed et ne changer qu'une variable à la fois. Générer par lots de 4.
- Noter chaque prise de 0 à 2 sur 6 critères : identité de la marmite, séparation du couvercle, flamme anguleuse, fermeture et extinction simultanées, timbre immobile, absence de texte.
- **Rejeter immédiatement toute prise avec une lettre, un chiffre ou une oblitération.**

---

## 11. Design sonore (optionnel, lecture par défaut en sourdine)

| Image | t (s) | Signal |
|---|---|---|
| f1–f6 | 0,017–0,100 | « tik-tik-tik » métal léger, 3 à 5 kHz, −24 dBFS |
| f8 | 0,133 | « pok » de décollement + début de « fwoomp » d'allumage (sous-grave 60–90 Hz et souffle qui monte), crête −8 dBFS |
| f12–f21 | 0,200–0,350 | crépitement bref, calé sur les poses « sur deux images » |
| f22–f27 | 0,367–0,450 | souffle inversé (aspiration) |
| **f28** | 0,467 | **« clac »** sec de métal mat + « pfft » d'étouffement, −6 dBFS, sans réverbération |
| **f34–f36** | 0,567–0,600 | **déchirure papier** sèche de 50 à 80 ms, aigus 4 à 8 kHz |
| f36–f40 | 0,600–0,667 | micro-craquement de fibres, −30 dBFS |

Livraison audio : WAV 48 kHz / 24 bits, 1,000 s, crête vraie ≤ −1 dBTP.
