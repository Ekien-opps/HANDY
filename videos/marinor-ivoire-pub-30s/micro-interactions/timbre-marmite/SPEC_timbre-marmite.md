# Timbre « Marmite chaude » : micro-interaction de 1 s
### Spécifications de production et prompt d'animation · Direction artistique et Lead Motion Design 3D · v2

> **L'intention en une phrase.** La marmite sous pression soulève son couvercle et lâche une langue de feu graphique, puis la ravale en se refermant. C'est ce choc qui fend le timbre. Trois temps forts nets en une seconde, une causalité lisible et une fin figée.

**Données de référence**

| Élément | Valeur |
|---|---|
| Durée | 60 images à 60 i/s, f0 → f59, soit **1,000 s**. f59 commence à 0,983 s, le clip se termine à 1,000 s. |
| Fond | aucun (alpha) |
| Texte | aucun |
| Asset | « Animated Cooking Series for Artgrid », timbre de 517,16 × 640 u, marmite raster de 512 px |

---

## 0. Le seul point à valider avec vous

**Les flammes imprimées au bas du timbre** (orange anguleux et paillettes) font partie de l'illustration du timbre. Par défaut, elles restent **imprimées et statiques de f0 à f59** : elles ne bougent pas, ne scintillent pas et ne sont pas éclairées. La flamme qui sort de la marmite est la seule flamme animée, et elle meurt au claquement.

*Variante possible :* les flammes imprimées se « refroidissent » à f28, avec −35 % de saturation et −15 % de luminance, maintenus jusqu'à f59. Le « tout est éteint » devient alors absolu, au prix d'une retouche de l'illustration d'origine.

## 1. Ce que l'on retient de la référence (mouvement uniquement)

La référence est une vidéo à 30 i/s : un timbre avec une icône centrale. On n'en retient que la mécanique de la déchirure.

**Ce qu'elle fait :**
- **une fracture sèche**, propagée en 2 ou 3 images (70 à 100 ms), sans flou de mouvement ;
- **un tracé ramifié** : un tronc en zigzag diagonal du haut-gauche vers le bas-droite qui traverse l'icône, une branche vers le bord droit, une branche vers le bas ;
- **des lèvres blanches** (on voit le papier) ;
- **des fragments qui s'écartent peu**, puis restent figés longtemps.

**Notre apport :**
- **une cause** : le claquement du couvercle déchire le papier ;
- **une matière** : la tranche du papier, des fibres, une légère inclinaison qui accroche la lumière ;
- **une fluidité** : un front de fissure à vitesse constante, puis un ressort amorti au lieu d'un arrêt sec.

Au plus large, l'écart entre fragments atteint environ 4 % de la largeur du timbre.

## 2. Fiche technique

| Paramètre | Valeur | Pourquoi |
|---|---|---|
| Cadence | **60 i/s** | Le claquement atteint environ 10°/image. À 30 i/s, il deviendrait stroboscopique et le ressort tomberait « en escalier ». |
| Durée | **60 images = 1,000 s exactement**. Variante de sécurité : 57 images (950 ms), en coupant 3 images de la tenue finale. | Consigne ≤ 1 s. Chaque livrable est contrôlé avec `ffprobe` : durée du conteneur ≤ 1,000 s. |
| Version 30 i/s | **Rendue nativement depuis les clés**, et non en supprimant une image sur deux | Les temps forts tombent alors sur les images 4, 14 et 18. |
| Canevas | **1080 × 1350 px (4:5) @1x**. Master **@2x : 2160 × 2700**, toutes les valeurs × 2. | Le format épouse celui du timbre et s'intègre aux grilles de portfolio. |
| Échelle | **1 u = 1,8 px @1x**, timbre décalé de (74,55 ; 99) px | Marges ≥ 74 px. Déplacement maximal d'un fragment : environ 34 px (au pic). |
| Fond | **alpha = 0 strict** hors silhouette | Ni sol, ni ombre portée, ni halo hors du timbre. |
| Texte | **zéro** | Aucun calque texte, aucune lettre, aucun chiffre, aucune oblitération. |
| Couleur | sRGB, projet en 16 bpc, sans gamma linéaire. Rendu 3D en *View Transform = Standard*. | Les codes hex de la charte restent exacts. |

**Conversion asset → canevas @1x :** `x_px = 74,55 + 1,8 × x_u` · `y_px = 99 + 1,8 × y_u`

## 3. Géométrie de référence (px @1x)

| Élément | Valeur |
|---|---|
| Papier blanc perforé #FFFFFF | x 74,6 → 999,3 · y 99 → 1239,6 (≈ 925 × 1141 px) |
| Perforations | Creux en demi-cercle de Ø ≈ 37 px et ≈ 18 px de profondeur. Pas ≈ 76 px sur les côtés (14 creux par côté), ≈ 71 px en haut et en bas (12 creux), quarts de creux aux coins. |
| Tranche du papier #4D4D4D | même silhouette, décalée de (+6,16 ; +6,16) px |
| **Vignette = limite dure de l'action** | x 136,1 → 937,7 · y 160,6 → 1177,9 (801,5 × 1017,3) |
| Dégradé de la vignette | Vertical, légèrement incliné. Haut ≈ #53813F, puis #759663, #D1D0C3, **#F6E8EA** (≈ 48 % de la hauteur), #F1DCDF, #E6BFC4, #D58F99, #BC4E5D, **#A40C21** en bas. |
| **Zone de sécurité** (retrait de 24 px) | x 160,1 → 913,7 · y 184,6 → 1153,9 |
| Marmite au repos (contour compris) | x 163,9 → 899,7 · y 410,9 → 1051,6. Sommet du bouton à y ≈ 441, joint couvercle/cuve à y ≈ 762. Ouverture de la cuve : ellipse de centre (531 ; 640), ≈ 540 × 245. |
| **B**, ancre d'écrasement (base de la cuve) | (537 ; 1030) |
| **H**, charnière du couvercle (extrémité gauche de la lèvre) | (267 ; 656) |
| **C**, centre du couvercle (pivot des rebonds) | (535 ; 611) |
| **E**, point d'émission de la flamme (dans l'ouverture, côté droit) | (627 ; 647). Axe incliné de **+14°** vers la droite. Base 240 px, hauteur 100 % (H_fl) = 376 px. |
| Pic d'ouverture (f12) | Pointe de flamme en **(732 ; 224)** : 63 px sous le haut de la vignette, 39 px sous la ligne de sécurité. Bord libre du couvercle ≈ (675 ; 272), sommet du bouton ≈ 231. |
| Déchirure | Amorce **S** (92,8 ; 479,2), creux gauche · nœud **N** (635 ; 823) · sortie droite **E_R** (981,0 ; 783,4), creux droit · sortie basse **E_B** (714,7 ; 1221,5), creux du bas |

*Les points H, C, B et E et les poses du couvercle au pic sont à recaler au pixel sur le découpage final (§ 4). Les angles du couvercle sont des valeurs écran : ils valent pour l'option 3D et pour l'option 2,5D.*

## 4. Préparation des assets

### 4.1 Audit de l'asset
1. **La marmite est un raster unique de 512 × 512.**
   - Elle n'a ni couvercle séparé, ni intérieur, ni dessous de couvercle.
   - Il faut l'agrandir de ×1,44 @1x et de ×2,9 @2x.
2. **Le contour blanc fait partie du raster** : 21 px sur l'image de 512 px, soit 30 px @1x (≈ 17 u). Il est intact partout, sauf un rognage d'environ 1 px en coupe droite sur l'anse droite. On le reconstruit par union (voir § 4.2).
3. **Les flammes imprimées débordent de la vignette** de 4 u (7 px). Le matte de la vignette les rogne. C'est un choix assumé et invisible.
4. **La texture pailletée** est en mode Écran. Elle doit toujours être posée sur la vignette opaque, à l'intérieur d'un même précomp.

### 4.2 Marmite, option A : reconstruction 3D « clay » (recommandée)

**Pipeline hybride.** La marmite est faite en 3D (Blender 4.2+ ou Cinema 4D/Redshift). La flamme, le timbre, la déchirure et les mattes sont faits en 2D dans After Effects.

**Modélisation** (D = diamètre de la cuve)
- **Cuve :** cylindre de 64 segments, hauteur 0,55 D, avec une vraie paroi intérieure et un vrai fond (Solidify 0,03 D).
- **Couvercle :** objet de révolution, Ø 1,02 D, dôme de 0,10 D, jupe de 0,05 D.
- **Bouton :** Ø 0,30 D.
- **Anses :** boucles à section carrée arrondie.
- **Finition :** Bevel 4 segments + Weighted Normal. Aucune arête vive.

**Matériaux** (mats, Metallic 0, Roughness 0,6). Les couleurs sont mesurées sur l'icône.

| Pièce | Couleurs |
|---|---|
| Couvercle | #B1BAC1, liseré #C7CED4 |
| Cuve | #66747D, ombre #44525B |
| Bouton | #57646D, flanc #2F3A3E |
| Anses | #946A48, ombre #643E23 |
| **Intérieur** (nouveau) | fond #1C2327, paroi #33404A |
| **Dessous du couvercle** (nouveau) | #8F99A0 → #6F7A82 |

**Caméra :** 100 mm, élévation 24° ± 3°, lacet ≈ −28°. On cale le rendu par superposition sur l'icône, à ≤ 3 px près @2x.

**Lumières**
- Key en area light haut-gauche avant.
- Fill à droite, à 20 %.
- Rim arrière-droit, à 30 %.
- AO à 0,15 D.
- **Point light de flamme** #FFA53A placée dans la cuve. Sa puissance est pilotée par le *FIRE_OUT* (§ 6.3).
- Film transparent, sans sol.

**Contour sticker :** on dilate l'alpha de l'union des pièces, flamme exclue, avec un Contour extérieur de **30 px @1x**, #FFFFFF. On n'utilise ni inverted hull ni Line Art, qui dessineraient le joint couvercle/cuve.

**Hiérarchie du rig**
```
CTRL_SQUASH (ancre B)
├─ BODY  (cuve, intérieur, anses)
├─ LID_H (pivot H : ouverture, fermeture)
│   └─ LID_C (pivot C : frémissement, rebonds)
│       └─ KNOB (rotation secondaire ≤ 3° autour de sa base, sans retard de position)
└─ FLAME_EMITTER (E)
```
- **Les valeurs du couvercle sont relatives à la lèvre écrasée** : le repérage à f28 est exact quel que soit l'écrasement.
- Un slider `CTRL_LID › open_deg` (angle d'ouverture en degrés, positif) est exporté de Blender en CSV et importé dans AE.

**Passes rendues** (PNG 16 bits RGBA droit, cadre exact du timbre)
- `POT_FULL`
- `FRONT_MATTE` : paroi avant, demi-lèvre avant, anse avant. La base de la flamme passe derrière.
- `LID_UNDER_MATTE`

**Rendu :** EEVEE à 64 échantillons ou Cycles à 256 + OIDN, filtre de 1,0 px. L'obturateur se règle par image dans Blender, selon le § 7.

### 4.3 Marmite, option B : 2,5D dans After Effects (variante UI ou Lottie, délai < 1 jour)
1. Agrandir le raster ×4 (Real-ESRGAN ou Gigapixel). Écart de couleur toléré : ΔE ≤ 2.
2. Découper `LID` (dôme et jupe, en suivant le joint #2B363C), `KNOB`, `BODY`, `HANDLE_L` et `HANDLE_R`.
3. Repeindre ce qui est caché, dans le même modelé clay : la lèvre et l'intérieur (#1C2327 → #33404A), la bande de cuve sous la jupe et l'anse droite masquée.
4. Reprendre **la même hiérarchie et les mêmes poses écran** (−36° au pic). On simule la perspective avec l'échelle Y du couvercle (100 → 70 % au pic) et CC Power Pin.
5. Pour un livrable **Lottie**, redessiner la marmite en 6 à 8 aplats vectoriels. Un raster ne passe pas proprement en Lottie.

### 4.4 Flamme (calques de forme AE, dans le langage des flammes imprimées)

**Forme**
- Arêtes droites, aucune courbe.
- **Pointes aiguës de 26 à 30°** (mesurées sur l'asset).
- 5 langues asymétriques penchées vers l'extérieur : centrale à 1,00 H_fl, flancs à 0,70 et 0,62, extérieures à 0,40 et 0,35.
- Objet graphique plat : **ce n'est pas un feu réaliste**.

**Couches**

| Calque | Construction et couleur |
|---|---|
| `FL_OUT` | dégradé **#FF6B31 → #FFA53A** |
| `FL_MID` | Décaler les tracés −36 px @2x (10 u), jointure Angle, **#F9A825** |
| `FL_CORE` | −74 px @2x, **#FBD021** |
| `FL_GLITTER` | texture pailletée en Écran à 70 %, matte = cœur |
| `FL_EDGE` (optionnel) | filet #FFECD1 |
| `FL_GLOW` | flou de 24 px, Écran à 35 % |

**Animation**
- 4 poses dessinées, toutes avec le même nombre de sommets :
  - P0 : germe à 8 % ;
  - P1 : jaillissement ;
  - P2 : pic ;
  - P3 : variation.
- Scintillement **« sur deux images »**.
- Agiter les tracés : taille 10,8 px @2x, Points : Angle, Agitations/s à 0.
- Sur la Phase temporelle : `posterizeTime(30); time*720`.
- **Interdits :** Turbulent Displace (il arrondit les angles) et tout flou sur la géométrie de la flamme.

**Petites tailles**
- Base d'une langue ≥ 12 u.
- Écart entre couches ≥ 10 u.
- Variante UI (≤ 300 px de haut) : 3 langues, grain ×2, sans `FL_EDGE`.

### 4.5 Structure de composition
Précomp **`PICTURE`**, sous le track matte `MATTE_VIGNETTE` appliqué en dernier. De bas en haut :
1. `VIGNETTE`, opaque. Les modes Écran et Incrustation se calculent sur elle.
2. `FLAMMES_IMPRIMÉES`, **statique**.
3. Marmite complète : `POT_FULL`, ou les calques de l'option B, avec le contour d'union.
4. `FLAME`, puis le glow et le light-wrap.
5. `POT_FULL` × `FRONT_MATTE`.
6. `PAILLETTES_IMPRIMÉES`, en Écran, **statique**. Elle passe au-dessus du bas de la marmite, comme dans l'asset.

Précomp **`STAMP_MASTER`**, de bas en haut : `PAPER_GREY`, `PAPER_WHITE`, `PICTURE`. Une variante `STAMP_MASTER_NOGREY` sert à construire les fragments.

## 5. Chronométrie image par image (60 i/s)

Les valeurs du couvercle sont relatives à la lèvre, sous `CTRL_SQUASH`. **Toutes les valeurs de la flamme sont clées image par image**, sans courbe nommée.

| Img | ms | Phase | Couvercle (rot / ΔY) | Flamme sY / sX · pointe y | `CTRL_SQUASH` sX/sY | Papier | Flou |
|---|---|---|---|---|---|---|---|
| f0 | 0 | **Repos** (image d'affiche) | 0° / 0 | — | 100/100 | intact | 0° |
| f1–f6 | 17–100 | **Frémissement** : le couvercle vibre sans se soulever | ΔX +1,5 / −1 / +1,5 / −1,5 / +1 / 0 px | — | 100/100 | — | 0° |
| f7 | 117 | **Compression** | 0° / +2 | — | 100,5/98,5 | — | 0° |
| **f8** | 133 | **Pop, temps fort 1** (pivot H) | −17,6° / −15,4 | lueur de fente #FFECD1 à 40 % | 99,5/102 | — | 180° |
| f9 | 150 | ouverture | −28,2° / −25,9 | **naissance** 35 / 60 | 99,8/101 | — | 180° |
| f10 | 167 | | −33,7° / −31,3 | 80 / 75 + smear (§ 6.2) · pointe y ≈ 268 | 100/100 | — | 180° |
| f11 | 183 | | −35,7° / −33,3 | 108 / 88 | — | — | 90° |
| **f12** | 200 | **Pic** | **−36° / −33,6** | **116 / 95** · pointe **(732 ; 224)** | — | — | 90° |
| f13 | 217 | stabilisation | −35° / −33,2 | 108 / 102 | — | — | 90° |
| f14 | 233 | | −33° / −32,4 | 100, pose A | — | — | 90° |
| f15–f19 | 250–317 | **Flottement** comme une soupape | ±1,5° / ±2 px autour de −32° / −32 | poses A/B/C sur deux images, 97–104 % | — | — | 90° |
| f20 | 333 | **Armement** | −34° / −34,4 | 104, pose C | — | — | 90° |
| f21 | 350 | | −35° / −35,2 | **100** (base de l'expression) | — | — | 90° |
| f22 | 367 | **Fermeture et extinction** | −34,3° / −34,5 | 98,5 | — | — | 90° |
| f23 | 383 | | −32,1° / −32,3 | 93,7 | — | — | 90° |
| f24 | 400 | | −28,6° / −28,7 | 86, le bord du couvercle occulte la flamme | — | — | 180° |
| f25 | 417 | | −23,6° / −23,7 | 74 | — | — | 180° |
| f26 | 433 | | −17,1° / −17,3 | 58,5 | — | — | 270° |
| f27 | 450 | | −9,3° / −9,3 | 37, jet aplati dans la fente | — | — | 270° |
| **f28** | 467 | **Claquement, temps fort 2** | **0° / 0** (repérage au pixel) | **0 : éteinte. FIRE_OUT = 1** | **101/96,5** | — | **0°** |
| f29 | 483 | rebond (pivot C) | +1,8° / −6 | 0 | 100,5/98,8 | — | 45° |
| f30 | 500 | | +0,6° / −2,4 | 0 | 99,6/100,8 | — | 45° |
| f31 | 517 | 2ᵉ contact | 0 / 0 | 0 | 100,2/99,6 | — | 45° |
| f32 | 533 | | −0,5° / −1,6 | 0 | 100/100 | — | 0° |
| f33 | 550 | **Prélude** | 0 / 0 | 0 | 100/100 | **intérieur figé**. Marque de stress blanche (10 px) au creux S. | 0° |
| f34 | 567 | **Amorce de la fissure** | — | — | — | front du tronc à **27 %** (lèvres pleine largeur derrière le front) | 0° |
| f35 | 583 | propagation | — | — | — | tronc à **95 %** | 0° |
| **f36** | 600 | **Déchirure, temps fort 3** | — | — | — | tronc, branche A et branche B à **100 %**. Les 3 fragments se libèrent : **×0,60** | **0°** |
| f37 | 617 | séparation | — | — | — | ×1,10, la tranche du papier apparaît | 90° |
| **f38** | 633 | **Pic de séparation** | — | — | — | **×1,35** | 45° |
| f39–f46 | 650–767 | ressort amorti | — | — | — | ×1,23 → 1,00 → **0,88** → 0,92 → 1,00 → 1,04 → 1,03 → 1,00 | 0° |
| f47 | 783 | **Repos** | — | — | — | ×1,00 imposé (écart résiduel ≤ 0,5 px) | 0° |
| **f48–f59** | 800–983 | **Tenue finale** (12 images, 200 ms) | — | — | — | figé, sans bruit | 0° |

**Lecture du rythme**
- Les temps forts tombent sur des images paires : f8, f28, f36.
- L'écart entre eux se resserre : 20 images, puis 8, puis 12 images de silence.
- **Le timbre ne bouge pas avant f33.** Le choc reste dans la vignette : écrasement de la marmite et rebond du couvercle.
- Ordre conforme à la consigne : ouverture (f8) → flamme (f9–f27) → **fermeture et extinction de f22 à f28, flamme à 0 sur l'image même du contact** → déchirure juste après (f33/f34, soit 100 ms).

**Variante « tressautement »** (en option, à valider). De f1 à f6, le couvercle se soulève trois fois de 3, 5 puis 7 px autour de C, sans lumière dans la fente. Elle est désactivée par défaut, pour ne pas lire « plusieurs ouvertures ».

## 6. Mécaniques clés

### 6.1 Ouverture
- Le couvercle frémit sans s'ouvrir (f1–f6), s'enfonce (f7), puis **saute** : 49 % de la course est parcourue en une seule image (f8).
- La cuve s'étire légèrement (99,5/102).
- Le bouton n'a qu'une rotation secondaire de 3° au plus, sans décalage de position.
- En 3D, l'ouverture d'environ 38° réels dépasse la vue de tranche : on voit **le dessous du couvercle, chauffé en orange**.

### 6.2 Flamme
- Elle naît **1 image après** le couvercle.
- La vitesse se lit par un **smear dessiné** à f10 : la langue centrale est étirée à 130 % de *sa longueur courante*, soit environ 104 % H_fl, avec la pointe à y ≈ 268. Ce n'est pas un flou.
- **Plafond absolu :** hauteur totale, smear compris, ≤ 120 % H_fl. Le glow compris, la pointe reste à y ≥ 200.
- Pic à 116 % à f12, puis stabilisation.
- Pendant le flottement, elle lèche le bord libre du couvercle.
- **Aucune partie de la flamme ne se détache** de la marmite.

### 6.3 Fermeture et extinction simultanées

**1. Occlusion (guillotine)**
- Ordre : `intérieur < FLAMME < paroi avant + anses < COUVERCLE`.
- En redescendant, le couvercle recouvre la flamme.

**2. Matte de fente**
- Un quadrilatère entre la lèvre et le dessous du couvercle, parenté à H, sert d'alpha matte à la base de la flamme.
- Son aire devient **nulle à f28**.

**3. Lien mathématique** (expression sur l'échelle de `FLAME_RIG`, ancre en E)

```js
// FLAMME › Échelle : de f22 à f28, la flamme est esclave de l'angle du couvercle ; à partir de f28 elle vaut 0, rebonds compris
var a = Math.abs(thisComp.layer("CTRL_LID").effect("open_deg")("Slider"));
var f = timeToFrames(time);
if (f < 22) value;
else if (f >= 28) [value[0], 0];
else { var k = Math.pow(clamp(a / 35, 0, 1), 0.75); [value[0] * (0.7 + 0.3 * k), value[1] * k]; }
```

L'échelle de base est clée à 100 % à f21. Résultat : 98,5 → 93,7 → 86 → 74 → 58,5 → 37 → **0**.

**4. Interrupteur `FIRE_OUT`**
- C'est un null avec une case à cocher, clé en **maintien (hold)** : 0 jusqu'à f27, **1 à partir de f28**.
- Il force à 0 l'opacité ou la puissance de **tout ce qui est feu** : flamme, glow, paillettes de flamme, lueur de fente, solide orange en Incrustation, light-wrap du dessous du couvercle, point light (Blender : puissance clée à 0 en interpolation *Constant* à f28).
- Il s'applique **quoi que fasse le couvercle**. Pendant les rebonds f29–f32, la fente s'ouvre « froide » : intérieur #1C2327, dessous gris.

**Ni fumée, ni braise, ni étincelle.** Le claquement met fin au feu, et rien ne le prolonge.

### 6.4 Déchirure

**Tracé** (px @1x)
- Segments longs de 90 à 165 px, crans courts de 25 à 35 px, à 40–60° de la direction principale.
- Bruit fractal de 2 à 4 px, pour lire « papier » et non « vecteur ».

| Branche | Points |
|---|---|
| **Tronc** (≈ 692 px) | S(92,8 ; 479,2) → (207 ; 552) → (233 ; 537) → (345 ; 637) → (372 ; 623) → (491 ; 733) → (519 ; 720) → **N(635 ; 823)** |
| **Branche A** (≈ 364 px) | N → (724 ; 797) → (745 ; 813) → (849 ; 785) → (871 ; 800) → **E_R(981,0 ; 783,4)** |
| **Branche B** (≈ 430 px) | N → (657 ; 913) → (638 ; 936) → (670 ; 1049) → (652 ; 1077) → **E_B(714,7 ; 1221,5)** |

**Règles de tracé**
- Chaque extrémité tombe **au fond d'un creux de perforation du papier blanc**, là où le papier cède.
- Pour la découpe, on prolonge chaque coupe au-delà de la silhouette : jusqu'à (60 ; 479,2), (1014 ; 783,4) et (714,7 ; 1255).
- Le tronc coupe la cuve et le bord avant-gauche du couvercle, mais **épargne le bouton**.

**Ce que « fluide » veut dire ici**
- Le front avance à **vitesse constante, environ 470 px/image**, et démarre à f33,6.
- Le tronc est à 27 % à f34, à 95 % à f35, puis les deux branches finissent ensemble à f36.
- Les lèvres apparaissent en pleine largeur derrière le front. Les fragments se posent ensuite sur un **ressort amorti**.
- Pas de flou : on obtient la netteté sans saccade.

**Fragments** (libérés ensemble à f36 ; chacun pivote autour de son dernier point attaché)

| Fragment | Surface | Pivot | Final ×1,00 (f47 → f59) | Pic ×1,35 (f38) |
|---|---|---|---|---|
| **F1** haut (bouton, couvercle, haut de la cuve) | 52,6 % | E_R | rot **+1,1°**, T(−2,4 ; −4,8), rotY −2° | +1,5°, T(−3,2 ; −6,5), rotY −2,7° |
| **F2** bas-gauche (anse gauche) | 33,1 % | E_B | rot **−0,8°**, T(−6,4 ; +4,8), rotX +1,5° | −1,1°, T(−8,6 ; +6,5), rotX +2,0° |
| **F3** bas-droit | 14,3 % | E_B | rot **+0,8°**, T(+6,4 ; +4,8), rotY +1,5° | +1,1°, T(+8,6 ; +6,5), rotY +2,0° |

**Écartements au repos**
- La déchirure s'ouvre en éventail depuis S : environ 40 px au point S, environ 19 px au nœud N.
- Branche B : de 24 à 13 px.
- Branche A : de 3 à 15 px. C'est voulu : elle reste presque fermée, côté charnière.

**Ressort :** ζ 0,32 à 10 Hz, soit `stiffness 3948, damping 40.2, mass 1`. Sinon, utiliser les multiplicateurs × du tableau.

**Matière**
- **Lèvres fibreuses #FFFFFF**
  - Larges sur F1 (8 à 11 px), étroites sur F2 et F3 (3 à 5 px).
  - Bords irréguliers : bordure 5 px, échelle 35, évolution figée.
  - En @2x seulement : 20 à 30 micro-fibres.
  - Liseré intérieur de 1 px #4D4D4D à 25 %.
- **Tranche du papier**
  - Pour chaque fragment, une **copie vectorielle grise** : silhouette ∩ forme du fragment, #4D4D4D, décalée de (+6,16 ; +6,16) px, solidaire du fragment.
  - Empilement F1 < F2 < F3 : aucune tranche ne déborde sur un fragment voisin.
  - L'inclinaison se lit par la lumière (±3 à 5 % de luminance), jamais par une déformation.
- **Interstices :** de vrais trous, alpha 0, sans ombre sur le fond.

**Construction sans couture**
1. Les 3 formes sortent d'un seul tracé passé dans **Pathfinder > Diviser** : elles partagent exactement leurs sommets.
2. `FRAG_i` = `STAMP_MASTER_NOGREY` sous le matte `FRAG_i_SHAPE`. La vignette entière (marmite, flammes, dégradé) se déchire avec le papier.
3. Jusqu'à f35, `STAMP_MASTER` reste intact **sous** les fragments, ce qui supprime le liseré d'anticrénelage le long des mattes jointifs. On l'éteint à f36, au moment où les fragments bougent.
4. Contrôle en mode Différence à f33 : écart ≤ 1/255.
5. Les lèvres sont révélées par Trim Paths **à vitesse constante** (voir plus haut).

### 6.5 Confinement « strictement dans le timbre »

**Limite dure : la vignette**
- Tout le précomp `PICTURE` est sous le matte : marmite complète, flamme, glow, light-wrap, flammes et paillettes imprimées.
- Le glow et le flou sont calculés **à l'intérieur** du précomp, et le matte s'applique en dernier.

**Zone de sécurité (24 px)**
- **Aucune pose clé n'y entre** : couvercle, bouton, flamme et glow compris.
- La cuve est plafonnée à sX ≤ 101 %. Son bord gauche atteint alors x = 160,2, donc il reste ≥ 160,1.
- Le matte n'est qu'une assurance : une flamme visiblement rognée est une erreur d'animation.

**Le timbre lui-même ne bouge pas avant f33.** Ensuite, seul le papier bouge, et l'intérieur reste figé.

## 7. Courbes et flou de mouvement : table unique

| Usage | Courbe |
|---|---|
| Ouverture (pop), f7 → f12 | `cubic-bezier(0.33, 1, 0.68, 1)` |
| Stabilisation et flottement, f12 → f15 | `cubic-bezier(0.37, 0, 0.63, 1)` |
| Armement | `cubic-bezier(0.5, 1, 0.89, 1)` |
| Claquement, f21 → f28 (sans freinage au contact) | `cubic-bezier(0.11, 0, 0.5, 0)` |
| Flamme | **clés image par image** (§ 5), puis expression (§ 6.3) |
| Front de fissure | `linear`, 470 px/image |
| Fragments | ressort ζ 0,32 / 10 Hz (ou clés ×) |

| Images | Obturateur | Ce qui est flouté |
|---|---|---|
| f0–f7 | 0° | — |
| f8–f10 | 180° | couvercle et écrasement de la cuve |
| f11–f23 | 90° | couvercle |
| f24–f25 | 180° | couvercle |
| f26–f27 | 270° | couvercle |
| **f28** | **0°** | — (image du contact, nette) |
| f29–f31 | 45° | couvercle et cuve |
| f32–**f36** | **0°** | — (fissure et libération nettes) |
| f37 | 90° | fragments |
| f38 | 45° | fragments |
| f39–f59 | 0° | — |
| Flamme | 0° en permanence | sa vitesse passe par le smear et les poses sur deux images |

**Mise en œuvre de l'obturateur**
- Dans Blender, l'obturateur se clé par image.
- Dans AE, l'angle d'obturateur de la composition ne se clé pas. On utilise **Pixel Motion Blur** (Shutter Control : Manual, angle clé) ou CC Force Motion Blur sur les calques concernés.

## 8. Rendu, alpha et livrables

**Alpha**
- PNG en alpha **droit**, EXR en **prémultiplié**, toujours interprétés explicitement.
- Hors silhouette, **alpha = 0 strict**. Ce contrôle s'applique aux masters PNG et ProRes : la compression avec perte du WebM et du HEVC introduit un léger bruit dans l'alpha.

| Livrable | Spécifications | Usage |
|---|---|---|
| **Séquence PNG (master)** | RGBA 16 bits, alpha droit, 2160 × 2700, images 0000 à 0059 | archive, source unique |
| **ProRes 4444 XQ** | 2160 × 2700 et 1080 × 1350, 60p, alpha, étiqueté BT.709 | reel portfolio, Premiere, Resolve |
| **WebM VP9 + alpha** | 1080 × 1350 et 432 × 540, CRF 20, ≤ 1,5 Mo | Chrome, Edge, Firefox |
| **HEVC + alpha** (hvc1) | 1080 × 1350, 60p, ≤ 2 Mo | Safari macOS et iOS |
| **WebP animé / APNG** | 240 × 300, 480 × 600, 720 × 900, lecture unique | UI. WebP : durées par image alternées 17/16/17 ms (1000 ms au total). APNG : délai de 1/60 s. |
| Lottie / dotLottie | uniquement avec l'option B en vectoriel, ≤ 120 Ko gzip | web et app légers |

```bash
M=MOR_stampPot-tear_v002_2160x2700_%04d.png
TAG="-colorspace bt709 -color_primaries bt709 -color_trc bt709"
# ProRes 4444 XQ (master 2x)
ffmpeg -framerate 60 -i $M -vf "scale=out_color_matrix=bt709:out_range=tv" \
  -c:v prores_ks -profile:v 4444xq -pix_fmt yuva444p10le -alpha_bits 16 -vendor apl0 $TAG \
  MOR_stampPot-tear_v002_2160x2700_60p_PR4444XQ.mov
# WebM VP9 + alpha 1080 (réduction exacte 2:1, prémultipliée)
ffmpeg -framerate 60 -i $M -vf "premultiply=inplace=1,scale=1080:1350:flags=area,unpremultiply=inplace=1,scale=out_color_matrix=bt709:out_range=tv" \
  -c:v libvpx-vp9 -pix_fmt yuva420p -crf 20 -b:v 0 -auto-alt-ref 0 -row-mt 1 $TAG \
  MOR_stampPot-tear_v002_1080x1350_60p_vp9a.webm
# HEVC + alpha 1080 (macOS, VideoToolbox : bgra obligatoire pour l'alpha)
ffmpeg -framerate 60 -i $M -vf "premultiply=inplace=1,scale=1080:1350:flags=area,unpremultiply=inplace=1,format=bgra" \
  -c:v hevc_videotoolbox -alpha_quality 0.9 -b:v 8M -tag:v hvc1 $TAG \
  MOR_stampPot-tear_v002_1080x1350_60p_hevca.mov
# Contrôle de durée (≤ 1,000 s) et du nombre d'images (60)
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames:format=duration <fichier>
```
Pour les déclinaisons 1080 en ProRes et 432 × 540 en VP9, on reprend les mêmes chaînes en changeant `scale`.

**Intégration web**
- Lecture unique, sans boucle : la vidéo se fige sur f59.
- Déclenchement au survol, ou à 50 % de visibilité via un IntersectionObserver.
- Avec `prefers-reduced-motion`, on affiche l'image f59.
- Pas de piste audio dans les fichiers vidéo, pour éviter tout décalage d'encodeur. Le son éventuel est livré à part.

```html
<video muted playsinline preload="auto" poster="MOR_stampPot-tear_v002_1080x1350_f00.png" width="1080" height="1350">
  <source src="MOR_stampPot-tear_v002_1080x1350_60p_hevca.mov" type='video/quicktime; codecs="hvc1"'>
  <source src="MOR_stampPot-tear_v002_1080x1350_60p_vp9a.webm" type="video/webm">
</video>
```

**Nommage**
- Fichiers : `MOR_stampPot-tear_v###_<L>x<H>_<fps>p_<codec>`, versions incrémentées, jamais « final ».
- Préfixes de calques : `CTRL_`, `POT_`, `FL_`, `FRAG_`, `FIBER_`, `MATTE_`.

## 9. Check-list QA

**Temps**
- [ ] 60 images à 60 i/s. Durée du conteneur ≤ 1,000 s sur **chaque** livrable (ffprobe).
- [ ] La version 30 i/s est rendue depuis les clés, avec les temps forts aux images 4, 14 et 18.
- [ ] Ordre respecté : pop f8 → flamme f9–f27 → fermeture et extinction f22→f28 → fissure f34–f36.

**Extinction**
- [ ] Flamme à 0 et `FIRE_OUT` = 1 **à f28 et après**.
- [ ] **Aucun pixel orange dans la cuve ni sous le couvercle** de f28 à f59, rebonds compris.
- [ ] Aucune partie de la flamme ne se détache. Ni fumée, ni braise.
- [ ] Flammes imprimées identiques à f0 sur les 60 images (écart = 0 en mode Différence), sauf si la variante « refroidies » est validée.

**Limites**
- [ ] Rendu « PICTURE seule » : alpha = 0 hors de la vignette sur les 60 images.
- [ ] Boîte englobante de la marmite et de la flamme, image par image : rien dans la bande de 24 px. Smear ≤ 120 % H_fl.
- [ ] Timbre identique à f0 jusqu'à f32 (mode Différence = 0 hors vignette).
- [ ] Repérage exact à f28 : le contour du couvercle se fond dans celui de la cuve écrasée, à 0 px près.

**Déchirure**
- [ ] Les 3 extrémités tombent au fond d'un creux de perforation.
- [ ] Aucun pont de papier.
- [ ] Aucune couture : écart ≤ 1/255 à f33, puis tranche sans débord.
- [ ] Front à vitesse constante. f28 et f36 nettes, sans flou.

**Alpha et rendu**
- [ ] Contrôle sur #000, #FFF, #808080, sur un damier et sur les couleurs de la charte (#2A5519, #7B1421, #FFECD1).
- [ ] Codes hex de la charte respectés à ΔE2000 ≤ 3.
- [ ] Lisible à 300 px et à 64 px de haut.

**Exclusions**
- [ ] Aucun calque texte (comptage par script).
- [ ] Ni lettre, ni chiffre, ni oblitération, ni filigrane.
- [ ] f59 est une affiche propre.

---

## 10. Prompt d'animation

*Règle d'écriture des prompts IA :*
- *aucune onomatopée et aucun mot en capitales, qui déclenchent du lettrage ;*
- *timbre décrit comme vierge (aucune valeur, aucun pays, aucune oblitération) ;*
- *les temps sont des débuts d'image (f59 = 0,983 s, fin du clip à 1,000 s).*

### 10.1 Prompt maître (EN) : générateurs IA et brief motion designer

```text
[Format] A 1.0-second micro-animation: 60 frames at 60 fps (frame 59 starts at 0.983 s, the clip ends at 1.000 s), portrait 4:5, 1080×1350 px, one single isolated object. Background: none, fully transparent alpha channel (if the tool cannot output alpha: a perfectly flat, uniform pure blue #0033FF backdrop for chroma keying, no gradient, no shadow, no reflection). Locked-off camera, straight-on front view, orthographic look, no camera movement of any kind.

[Subject] One modern flat-illustrated postage stamp, blank — no denomination, no country name, no postmark — upright and centered: white paper (#FFFFFF), about 925×1141 px, with a regular scalloped perforated edge (half-circle notches about 37 px wide and 18 px deep, spaced about 76 px on the sides and 71 px on the top and bottom), and a flat dark grey (#4D4D4D) copy of the silhouette offset 6 px right and 6 px down, reading as paper thickness. Inside: a rectangular picture area (802×1017 px, 62 px white margin) with a smooth vertical gradient: leaf green #53813F at the top, sage #759663, greige #D1D0C3, powder pink #F6E8EA just above mid-height, dusty rose #D58F99, crimson #A40C21 at the bottom. Printed along the bottom of the picture area: flat graphic flames made of sharp angular zigzag spikes in an orange gradient (#FFA53A to #FF6B31) with a fine golden-pink glitter grain; these printed flames are part of the static artwork and never move, flicker, grow or glow. Centered, overlapping them: a soft-3D clay cooking pot icon in three-quarter view from slightly above — matte blue-grey body (#66747D lit, #44525B shadow), domed pale grey lid (#B1BAC1) with a lighter rim (#C7CED4), round dark slate knob (#57646D), two rounded brown wooden handles (#946A48), the whole pot wrapped in a thick white die-cut sticker outline (about 30 px). Soft top-left key light, gentle ambient occlusion, no cast shadow. The pot's and the stamp's design and colours stay the same throughout; only the described lid motion, pot squash and tear change shapes.

[Action, exact timing at 60 fps]
0.000–0.100 s (frames 0–6): the closed lid trembles sideways by 1–1.5 px under pressure without lifting.
0.117 s (frame 7): the lid sinks 2 px and the pot compresses slightly (height −1.5%).
0.133–0.200 s (frames 8–12): the pot opens. The lid snaps open, hinging on the left end of its rim; its right edge flips up to about 36° and the lid rises about 34 px, half of the travel in a single frame, with a very fast ease-out. The dark charcoal interior (#1C2327) appears and the underside of the lid glows warm orange.
0.150–0.200 s (frames 9–12): a flame bursts out of the open side, leaning 14° to the right. It is made of stylised, faceted tongues with sharp 26–30° tips, in the same angular language as the printed flames: outer #FF6B31 to #FFA53A, middle #F9A825, core #FBD021, with the same glitter grain. It overshoots to 116% at frame 12, and its highest tip stays at least 60 px below the top edge of the picture area. Speed reads through a drawn stretch of the tip at frame 10, never through blur on the flame. No part of the flame ever separates from the pot.
0.200–0.350 s (frames 12–21): the lid floats on the flame like a pressure valve (±1.5°, ±2 px); the flame flickers, animated on twos for a crisp graphic feel.
0.367–0.467 s (frames 22–28): the pot closes and the flame dies at the same time, in one single motion. The lid slams down with a gravity-like accelerating ease-in; its descending edge cuts the flame off, and the flame's height follows the lid angle (98%, 94%, 86%, 74%, 58%, 37%), reaching exactly zero on the very frame the lid lands (frame 28). From that frame on, the flame and every trace of its glow are gone for good, even while the lid bounces. No smoke, no embers, no sparks.
0.467–0.550 s (frames 28–33): the pot squashes slightly (height −3.5%, width +1%) and recovers; the lid bounces once by about 6 px, then a tiny 1.6 px, and settles. Only the pot moves; the stamp itself stays perfectly still. From frame 33 nothing inside the picture area moves any more.

[Containment] The lid, the knob, the flame, its glow and every moving part stay strictly inside the stamp's inner picture rectangle, with a 24 px safety margin. Nothing ever overlaps the white perforated border or leaves the stamp. The stamp does not move at all before the tear.

[Tear, right after the lid lands]
0.567–0.600 s (frames 34–36): a branched crack propagates smoothly and continuously across the stamp at constant speed. It starts at the bottom of a perforation notch on the left edge (about 33% down), zigzags diagonally through the pot, sparing the knob, to a node at about 61% across and 63% down, then splits into one branch to the right edge and one to the bottom edge, each ending in a perforation notch. The edges are crisp, with no blur.
0.600–0.783 s (frames 36–47): the stamp separates into three clean paper fragments that glide apart with a soft, damped spring (peak at frame 38) and settle, the tear fanning open from the left: a gap of about 40 px at the left edge narrowing to about 20 px at the node, rotations of 0.8 to 1.5°, and a slight 3D tilt (at most 3°) that catches the light. The upper fragment, carrying the lid and the knob, opens the most. The torn edges are crisp white fibrous paper lips (3 to 11 px, wider on the upper piece) with the grey paper thickness visible; the gaps are fully transparent.
0.800–0.983 s (frames 48–59): a perfectly still final hold on the torn stamp. It is paper tearing, not burning: no char, no scorch.

[Style] Premium 3D-icon motion design: soft clay render for the pot, flat graphic flames, readable even at small size, snappy and satisfying, three crisp beats (opening, closing, tearing), top-studio polish. Motion blur only on the lid moves and the fragment separation; the landing frame and the crack stay razor sharp. Total duration 1.0 second maximum. No text, no letters, no numbers anywhere.
```

### 10.2 Prompts négatifs (EN)

**A. Génération en temps réel (1 s)**
```text
text, letters, words, numbers, typography, onomatopoeia, comic sound-effect lettering, speech bubble, stamp denomination, value, price, country name, postmark, cancellation lines, rubber ink stamp, signature, logo, watermark, UI, subtitles,
background scene, table, desk, envelope, paper backdrop, floor, wall, gradient backdrop, vignette around the frame, shadow on the background, drop shadow outside the stamp, reflection, bokeh, depth of field, lens flare, glow leaking outside the stamp,
hands, fingers, people, kitchen, stove, food, liquid, steam, smoke, embers, sparks, detached flame, flame after the lid closes, glow after the lid closes, flickering bottom flames, animated printed flames, extra pots, extra objects,
photorealistic fire, volumetric fire, fire spreading to the paper, burning paper, charred or scorched edges, ash,
camera movement, pan, tilt, zoom, dolly, orbit, camera shake, handheld, stamp moving, shaking or drifting before the tear,
warping, morphing, melting, jelly deformation, change of pot design, change of colours, extra handles, missing knob,
slow motion look, frame drops, motion blur on the crack, blurry, low resolution, compression artifacts, noise
```
**B. Génération étirée (3 à 5 s, à recaler à 1 s)** : la même liste, **sans** `slow motion look`.

### 10.3 Prompt maître (FR) : brief motion designer

```text
[Format] Micro-animation de 1,0 seconde : 60 images à 60 i/s (l'image 59 commence à 0,983 s, le clip se termine à 1,000 s), portrait 4:5, 1080 × 1350 px, un seul objet isolé. Fond : aucun, canal alpha entièrement transparent (à défaut : fond bleu pur #0033FF parfaitement plat pour l'incrustation). Caméra verrouillée, vue de face, rendu orthographique, aucun mouvement de caméra.

[Sujet] Un timbre-poste moderne en illustration plate, vierge (aucune valeur, aucun pays, aucune oblitération), droit et centré : papier blanc #FFFFFF d'environ 925 × 1141 px à bord dentelé régulier (creux en demi-cercle d'environ 37 px de large et 18 px de profondeur, espacés d'environ 76 px sur les côtés et 71 px en haut et en bas), doublé d'une copie gris foncé #4D4D4D de la silhouette décalée de 6 px vers la droite et 6 px vers le bas (l'épaisseur du papier). À l'intérieur : une zone d'image rectangulaire (802 × 1017 px, marge blanche de 62 px) en dégradé vertical, vert feuille #53813F en haut, sauge #759663, grège #D1D0C3, rose poudre #F6E8EA juste au-dessus de la mi-hauteur, vieux rose #D58F99, cramoisi #A40C21 en bas. Imprimées au bas de la zone : des flammes graphiques plates en pointes anguleuses, dégradé orange #FFA53A → #FF6B31, avec un grain pailleté or-rose ; ces flammes imprimées font partie de l'illustration statique et ne bougent, ne scintillent, ne grandissent ni ne brillent jamais. Au centre, chevauchant ces flammes : une icône de marmite en 3D douce « pâte à modeler », vue de trois quarts légèrement plongeante — cuve gris-bleu mat (#66747D côté lumière, #44525B côté ombre), couvercle bombé gris clair #B1BAC1 à liseré #C7CED4, bouton ardoise #57646D, deux anses arrondies en bois brun #946A48, le tout entouré d'un épais contour blanc de type sticker (environ 30 px). Lumière douce haut-gauche, occlusion légère, aucune ombre portée. Le design et les couleurs de la marmite et du timbre restent les mêmes ; seuls le mouvement du couvercle, l'écrasement de la marmite et la déchirure décrits changent les formes.

[Action, timing exact à 60 i/s]
0,000–0,100 s (images 0–6) : le couvercle fermé frémit latéralement de 1 à 1,5 px sous la pression, sans se soulever.
0,117 s (image 7) : le couvercle s'enfonce de 2 px et la marmite se tasse légèrement (hauteur −1,5 %).
0,133–0,200 s (images 8–12) : la marmite s'ouvre. Le couvercle s'ouvre d'un coup en pivotant sur l'extrémité gauche de sa lèvre ; son bord droit se soulève jusqu'à environ 36° et il monte d'environ 34 px, la moitié de la course en une seule image, avec une décélération très rapide. L'intérieur anthracite (#1C2327) apparaît et le dessous du couvercle s'éclaire en orange chaud.
0,150–0,200 s (images 9–12) : une flamme jaillit du côté ouvert, inclinée de 14° vers la droite. Elle est faite de langues stylisées et facettées aux pointes aiguës de 26 à 30°, dans le même langage anguleux que les flammes imprimées : extérieur #FF6B31 → #FFA53A, milieu #F9A825, cœur #FBD021, avec le même grain pailleté. Elle dépasse à 116 % à l'image 12, et sa pointe la plus haute reste au moins 60 px sous le bord haut de la zone d'image. La vitesse se lit par un étirement dessiné de la pointe à l'image 10, jamais par du flou sur la flamme. Aucune partie de la flamme ne se détache de la marmite.
0,200–0,350 s (images 12–21) : le couvercle flotte sur la flamme comme une soupape (±1,5°, ±2 px) ; la flamme scintille, animée sur deux images pour un rendu graphique net.
0,367–0,467 s (images 22–28) : la marmite se ferme et la flamme s'éteint en même temps, en un seul mouvement. Le couvercle retombe en accélérant comme sous l'effet de la gravité ; son bord descendant sectionne la flamme, dont la hauteur suit l'angle du couvercle (98 %, 94 %, 86 %, 74 %, 58 %, 37 %), jusqu'à zéro exactement sur l'image où le couvercle se pose (image 28). À partir de cette image, la flamme et toute trace de sa lueur ont disparu pour de bon, même pendant les rebonds du couvercle. Ni fumée, ni braise, ni étincelle.
0,467–0,550 s (images 28–33) : la marmite s'écrase légèrement (hauteur −3,5 %, largeur +1 %) puis se reprend ; le couvercle rebondit une fois d'environ 6 px, puis d'à peine 1,6 px, et se pose. Seule la marmite bouge ; le timbre reste parfaitement immobile. À partir de l'image 33, plus rien ne bouge dans la zone d'image.

[Confinement] Le couvercle, le bouton, la flamme, sa lueur et toute partie mobile restent strictement dans le rectangle intérieur du timbre, avec une marge de sécurité de 24 px. Rien ne chevauche jamais la bordure perforée blanche ni ne sort du timbre. Le timbre ne bouge pas avant la déchirure.

[Déchirure, juste après la pose du couvercle]
0,567–0,600 s (images 34–36) : une fissure ramifiée se propage de façon fluide et continue, à vitesse constante, à travers le timbre. Elle part du fond d'un creux de perforation du bord gauche (environ 33 % de la hauteur), zigzague en diagonale à travers la marmite en épargnant le bouton jusqu'à un nœud situé à environ 61 % de la largeur et 63 % de la hauteur, puis se divise en une branche vers le bord droit et une branche vers le bord bas, chacune finissant dans un creux de perforation. Bords nets, sans flou.
0,600–0,783 s (images 36–47) : le timbre se sépare en trois fragments de papier nets, qui s'écartent en glissant avec un ressort doux et amorti (pic à l'image 38) puis se posent. La déchirure s'ouvre en éventail depuis la gauche : environ 40 px au bord gauche, environ 20 px au nœud, rotations de 0,8 à 1,5°, légère inclinaison 3D (3° au plus) qui accroche la lumière. Le fragment du haut, qui porte le couvercle et le bouton, s'ouvre le plus. Bords déchirés : lèvres de papier blanches et fibreuses (3 à 11 px, plus larges sur le fragment du haut), épaisseur grise visible ; les interstices sont entièrement transparents.
0,800–0,983 s (images 48–59) : tenue parfaitement immobile sur le timbre déchiré. C'est du papier qui se déchire, pas qui brûle : ni carbonisation, ni roussi.

[Style] Motion design d'icône 3D haut de gamme : rendu « pâte à modeler » doux pour la marmite, flammes graphiques plates, lisible même en petit, vif et satisfaisant, trois temps nets (ouverture, fermeture, déchirure), finition de grand studio. Flou de mouvement uniquement sur les mouvements du couvercle et l'écartement des fragments ; l'image où le couvercle se pose et la fissure restent parfaitement nettes. Durée totale de 1,0 seconde au maximum. Aucun texte, aucune lettre, aucun chiffre nulle part.
```

### 10.4 Version compacte (< 1 000 caractères)

```text
Locked-off front view, orthographic look, 1 second at 60 fps, transparent background (or flat #0033FF). A blank modern flat-illustrated postage stamp (no value, no postmark): white scalloped perforated border, grey offset edge, green-to-powder-pink-to-crimson gradient picture, static printed angular orange flames at the bottom. In it, a soft-3D clay cooking pot (blue-grey body, pale domed lid, dark knob, brown handles, thick white sticker outline). The lid pops open on its left rim and a stylised angular orange-gold flame bursts out; then the lid slams shut and the flame dies in the same motion, zero on the landing frame, no smoke, no glow after. All action stays inside the picture area; the stamp stays still. Right after, a crack runs smoothly across the stamp along a branched zigzag; three paper pieces with white fibrous edges glide 20–40 px apart and settle. No letters, numbers or postmarks.
```

### 10.5 Variante par images clés (image-to-video) : **3 clips, 60 images au total**

Les images clés se fabriquent **hors IA** :
- le rendu du .ai à 1080 × 1350 sur #0033FF ;
- le couvercle découpé pour K1 ;
- la déchirure vectorielle dans Illustrator pour K3.

**K2 est obligatoire** : il verrouille l'image d'extinction.

| Image clé | Image | Temps | Description à donner (EN) |
|---|---|---|---|
| **K0** | f0 | 0,000 s | front orthographic view of the blank stamp on flat #0033FF; clay pot, lid closed; intact stamp; printed bottom flames static; no flame from the pot; no letters |
| **K1** | f12 | 0,200 s | same stamp untouched; lid hinged open about 36° on its left rim; dark interior; stylised angular orange-gold flame bursting out, leaning right, tip 60 px below the top of the picture area; orange glow under the lid; everything inside the picture area; no letters |
| **K2** | f28 | 0,467 s | same stamp, intact and still; lid shut; pot squashed slightly (height −3.5%); no flame and no glow from the pot; printed bottom flames unchanged; no smoke; no letters |
| **K3** | f59 | 0,983 s | same stamp torn into three paper fragments along the branched zigzag crack (left notch → node → right notch / bottom notch), gaps of 20 to 40 px, rotations of about 1°, crisp white fibrous edges, grey thickness; pot closed; not burnt; flat #0033FF; no letters |

| Clip | Raccord | Cible | Prompt (EN) |
|---|---|---|---|
| **A** | K0 → K1 | **12 intervalles** (f0–f12), 0,200 s | `Locked camera. The lid pops open on its left rim and a stylised angular flame bursts out, staying inside the stamp's picture area. The stamp does not move. Fast and snappy. No letters.` |
| **B** | K1 → K2 | **16 intervalles** (f12–f28), 0,267 s | `Locked camera. The lid floats, then slams shut; the flame stays inside the picture area and shrinks to zero exactly as the lid lands; no flame, glow or smoke afterwards. The stamp does not move. No letters.` |
| **C** | K2 → K3 | **31 intervalles** (f28–f59), 0,517 s | `Locked camera. The lid bounces slightly and settles, then a crack runs smoothly across the stamp and it tears into three paper pieces that glide apart with a soft spring and settle. No burning. No letters.` |

Au total : 12 + 16 + 31 = **59 intervalles, soit 60 images = 1,000 s**. On recale chaque clip sur sa cible en images. Les raccords K1 et K2 ne sont comptés qu'une fois.

### 10.6 Notes de production IA

**Alpha**
- On génère sur **#0033FF**. Le bleu est la seule famille de teinte absente de l'asset : le haut de la vignette est vert, le bas rose et rouge, les flammes orange et jaune, la bordure et les contours blanc et noir. Le gris-bleu de la cuve n'est saturé qu'à 15 à 25 %.
- Réglages Keylight : Screen Colour #0033FF, Clip Black 15–20, Clip White 80–85, Shrink −1 px.

**Pipeline recommandé**
- Le clip IA sert de **référence de mouvement (animatique)**. On reconstruit ensuite selon les § 4 à 6.
- **La déchirure se fait toujours dans After Effects** : les modèles déforment une fracture sur un dessin rigide.

**Tenir la seconde**
- Avec une génération étirée (prompt négatif B) : 3 à 5 s, `the action fills the whole clip`, puis compression à 60 images.
- **Ne jamais interpoler à travers f28, ni de f33 à f38.**

**Timbre immobile**
- En image-to-video, la caméra est en « static », l'intensité de mouvement est basse et le pinceau de mouvement est limité à la marmite.
- En post-production, on repose la bordure vectorielle par-dessus et on vérifie en mode Différence par rapport à f0 : l'image doit rester noire jusqu'à f32.

**Itérations**
- Seed figée, une seule variable modifiée à la fois, lots de 4.
- Chaque prise est notée de 0 à 2 sur six critères : identité de la marmite, séparation du couvercle, flamme anguleuse, extinction simultanée, timbre immobile, absence de texte.
- **Toute prise contenant une lettre, un chiffre ou une oblitération est rejetée.**

---

## 11. Design sonore (optionnel, livré à part, lecture en sourdine par défaut)

| Image | t (s) | Son |
|---|---|---|
| f1–f6 | 0,017–0,100 | frémissement métallique très léger, −30 dBFS |
| f8 | 0,133 | décollement sec du couvercle et départ de l'allumage (sous-grave 60–90 Hz + souffle montant), crête −8 dBFS |
| f12–f21 | 0,200–0,350 | crépitement bref, calé sur les poses sur deux images |
| f22–f27 | 0,367–0,450 | souffle inversé (aspiration) |
| **f28** | 0,467 | **claquement** sec de métal mat et étouffement, −6 dBFS, sans réverbération |
| **f34–f36** | 0,567–0,600 | **déchirure de papier** sèche de 50 à 80 ms, aigus 4 à 8 kHz |
| f36–f40 | 0,600–0,667 | micro-craquement de fibres, −30 dBFS |

Livraison : WAV 48 kHz / 24 bits, 1,000 s, crête vraie ≤ −1 dBTP. Le fichier est livré séparément, et non muxé dans les vidéos.
