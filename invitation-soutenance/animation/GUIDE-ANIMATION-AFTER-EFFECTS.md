# Guide d'animation After Effects : Proposition 2 (2500 × 1429)

Fichier source : `psd/Proposition-2_Nouveau-format_2500x1429.psd`.
Aperçu du rendu attendu : `animatic_proposition-2.mp4`. Il utilise exactement les timings et courbes de ce guide.

---

## 0. Intention artistique : « Le fil d'or »

Une seule idée guide toute l'animation : **un fil d'or trace la structure, puis le contenu se dévoile de l'intérieur.**

- **Une seule direction de mouvement.** Tout entre par le bas, ou s'ouvre depuis un centre : jamais de la gauche ou de la droite. C'est ce qui crée l'harmonie.
- **Deux courbes seulement** :
  - **Expo Out** pour tout ce qui apparaît (départ vif, arrivée longue et soyeuse) ;
  - **In-Out** pour tout ce qui se trace (cadre, filets).
- **Un seul rebond dans tout le film** : le picto Marin'Or. Il agit comme la « signature » de l'animation. Le reste ne rebondit pas.
- **Décalages réguliers** : 3 images entre deux lettres, 3 images entre deux lignes d'une colonne, 4 images entre deux colonnes, 1 image entre deux mots. Ce rythme constant donne une impression de précision.
- **Masques de révélation (Track Matte)** sur les gros textes : les lettres montent depuis une ligne invisible au lieu d'apparaître en fondu. C'est le marqueur « haut de gamme ».

### Éléments fixes

Ton cahier des charges cite le fond rouge et la photo de l'ISTC, qui appartiennent à la **Proposition 1**. Le fichier joint est la **Proposition 2**. J'ai donc appliqué la règle à ses équivalents :

| Calque PSD | Traitement |
|---|---|
| Fond crème douce | Immobile |
| Halo lumineux (blanc) | Quasi immobile : respiration d'opacité 100 → 94 % sur 8 s |
| Motif Marin'Or – haut gauche / bas droite | Quasi immobiles : dérive de 0,3°/s et ±4 px |

Tout le reste s'anime.

---

## 1. Préparation dans After Effects

1. **Composition** : 2500 × 1429, **30 i/s**, durée **10:00**, pixels carrés, fond #FFECD1.
2. **Import du PSD** : *Fichier > Importer*, type **Composition – Conserver la taille des calques**, cocher **Styles de calques modifiables**.
3. **Aplatir les dossiers.** Chaque dossier PSD arrive en précomposition.
   - Ouvre chaque précomp, sélectionne tous ses calques, coupe (Ctrl/Cmd+X).
   - Reviens dans la compo principale et colle (Ctrl/Cmd+V) : les positions sont conservées, car les précomps font 2500 × 1429.
   - Supprime ensuite la précomp vide.
   - Tu obtiens une seule timeline, indispensable pour régler les décalages.
4. **Textes** : sélectionne tous les calques de texte, puis *Calque > Créer > Convertir en texte modifiable*. Montserrat doit être installée.
5. **Points d'ancrage** (outil Déplacement arrière Y) :
   - au **centre** : logo Marin'Or, picto, séparateurs, filet vertical ;
   - à l'**extrémité intérieure** pour les deux filets de l'ornement : bord droit du filet gauche, bord gauche du filet droit.
6. **Cadre et filet or en calques de forme.** Le Trim Paths exige un tracé After Effects. Masque les deux calques PSD « Cadre bordeaux » et « Filet or épicé », puis crée deux calques de forme :
   - Pour chacun : Position du calque [0, 0], Point d'ancrage [0, 0], puis *Ajouter > Rectangle*, *Contour* et *Trim Paths*.

   | Forme | Position du rectangle | Taille | Contour |
   |---|---|---|---|
   | Cadre bordeaux | 1250 ; 714,5 | 2397 × 1326 | 3 px, #7B1421 |
   | Filet or épicé | 1250 ; 714,5 | 2362,5 × 1291,5 | 1,5 px, #F9A825 |

7. **Flou de bougé** : active-le sur tous les calques animés, plus l'interrupteur de la compo. *Composition > Paramètres > Avancé* : angle d'obturation 180°, phase −90°, 16 échantillons. Il donne aux montées de texte un fondu naturel en mouvement.
8. **Marqueurs de départ.** Sur chaque calque de texte animé par expression, pose un **marqueur de calque** (touche `*` du pavé numérique) au temps de départ du tableau §2. Pour re-caler l'animation, il suffit de déplacer le marqueur.

---

## 2. Timeline (30 i/s, format SS:II = secondes:images)

| # | Début | Fin | Élément | Mouvement | Courbe |
|---|---|---|---|---|---|
| 0 | 00:00 | 10:00 | Fond, halo, motifs | Fixes (respiration et dérive discrètes) | Expression |
| 1 | 00:12 | 01:12 | **Cadre bordeaux** | Trim Paths depuis le centre haut, en 2 sens | In-Out |
| 2 | 00:18 | 01:18 | **Filet or épicé** | Trim Paths depuis le centre bas : contre-mouvement | In-Out |
| 3 | 00:24 | 01:18 | **Filet vertical or** | Échelle Y 0 → 100 % depuis le centre | In-Out |
| 4 | 00:24 | 01:24 | **Logo Marin'Or** | Masque ovale qui s'ouvre + échelle 94 → 100 % | Expo Out |
| 5 | 01:06 | 01:27 | Logo ISTC | Position Y +24 px → 0, opacité 0 → 100 | Expo Out |
| 6 | 01:09 | 01:27 | Séparateur ISTC | Échelle Y 0 → 100 % (centre) | Expo Out |
| 7 | 01:11 / 01:14 | 01:29 / 02:02 | « ISTC POLYTECHNIQUE » / « ABIDJAN » | Montée de ligne sous masque (+44 px → 0) | Expo Out |
| 8 | 01:16 | 02:09 | **INVITATION** | Interlettrage qui se resserre + lettres en fondu (1 image d'écart) | Expo Out |
| 9 | 01:24 | 03:03 | **Ephrem** | Chaque lettre monte sous masque, 3 images d'écart, 24 images par lettre | Expo Out |
| 10 | 02:09 / 02:13 | 03:00 / 03:04 | Phrase d'invitation (2 lignes) | Y +40 → 0, opacité, flou 6 → 0, ligne par ligne | Expo Out |
| 11 | 02:18 | 03:10 | **Picto Marin'Or** | Échelle 0 → 100 % en **ressort**, rotation −25° → 0 | Ressort |
| 12 | 03:10 | 03:19 | Picto : anticipation | Compression 100 → 90 → 100 % | In puis Out |
| 13 | 03:13 | 04:04 | Filets de l'ornement | Échelle X 0 → 100 % depuis le picto : il les « propulse » | Expo Out |
| 14 | 03:12 | 04:06 | Colonne DATE | Libellé, puis valeur, puis sous-ligne (3 images d'écart) | Expo Out |
| 15 | 03:16 | 04:10 | Colonne HEURE (+ séparateur 1) | Idem, avec chiffres qui défilent sur « 11H30 » | Expo Out |
| 16 | 03:20 | 04:14 | Colonne SALLE (+ séparateur 2) | Idem | Expo Out |
| 17 | 04:02 | 04:20 | Libellé THÈME | Interlettrage + opacité | Expo Out |
| 18 | 04:08 | 05:10 | Texte du thème | Mot à mot, 1 image d'écart : Y +16 → 0, opacité, flou 4 → 0 | Expo Out |
| 19 | 05:18 | 06:12 | Reflet sur le logo Marin'Or | CC Light Sweep, de gauche à droite | In-Out |
| 20 | 06:00 | 06:18 | Reflet sur le picto | CC Light Sweep | In-Out |
| 21 | 06:18 | 10:00 | Tenue | Image fixe, lisible : seuls halo et motifs respirent | — |

Rythme global :
- **0–1,5 s** : la structure se trace ;
- **1,5–3 s** : l'identité et le prénom ;
- **3–5,3 s** : les informations ;
- **5,5–6,6 s** : la touche de lumière ;
- **6,6–10 s** : la lecture.

---

## 3. Techniques par élément

### 3.1 Cadre bordeaux et filet or (Trim Paths)
- Trim Paths : **Début 50 → 0 %** et **Fin 50 → 100 %**, avec 2 images clés sur chacune et les mêmes temps. Le trait pousse alors dans les deux sens à la fois.
- Règle **Décalage (Offset)** pour que le départ soit au **centre haut** du cadre, et au **centre bas** du filet or. Les deux traits naissent à l'opposé l'un de l'autre et se croisent : c'est le premier geste élégant du film.
- Courbe In-Out (voir §4).

### 3.2 Filet vertical, séparateurs, filets de l'ornement
- Ce sont des traits droits : une **Échelle** sur un seul axe, avec le point d'ancrage au bon endroit, équivaut à un Trim Paths.
- Filet vertical et séparateurs : ancrage au centre, Échelle Y 0 → 100 %.
- Filets de l'ornement : ancrage côté picto, Échelle X 0 → 100 %. Ils semblent sortir du picto.

### 3.3 Logo Marin'Or : ouverture ovale
- Dessine un **masque ellipse** sur le logo, à la forme de son badge ovale.
- Anime **Expansion de masque** de −300 px à 0, avec un contour progressif de 40 px.
- Ajoute **Échelle 94 → 100 %** et **Opacité 0 → 100 %** sur les 9 premières images.
- À 05:18, pose un **CC Light Sweep** :
  - Direction 15°, Largeur 60, Intensité 40, Bord 0, Forme Smooth ;
  - anime **Centre** de la gauche hors du logo jusqu'à la droite hors du logo, en 24 images, courbe In-Out.

### 3.4 Logo ISTC et texte « ISTC POLYTECHNIQUE / ABIDJAN »
- Logo : Position Y +24 → 0 et Opacité.
- Texte : animateur **Position** (0, 44), basé sur les **Lignes**, avec le sélecteur d'expression du §5.1 (délai 3, durée 18).
- Track Matte : un rectangle juste au-dessus de chaque ligne, en **Cache alpha**, pour que la ligne « sorte » d'une fente invisible.

### 3.5 INVITATION
- **Animateur 1 : Interlettrage.** Départ réglé pour que le mot soit environ 1,5 fois plus large qu'à l'arrivée (environ un cadratin de plus par lettre). Arrivée 0. Avec un sélecteur de plage à 100 %, image clé sur la valeur, de 01:16 à 02:09.
- **Animateur 2 : Opacité 0 %**, basé sur les caractères, sélecteur d'expression du §5.1 (délai 1, durée 12).
- Les lettres convergent et s'allument en même temps : un effet discret mais très « luxe ».

### 3.6 Ephrem : la pièce maîtresse
- Animateur **Position (0, 290)**, basé sur les **Caractères**, sélecteur d'expression du §5.1 (délai 3, durée 24).
- **Track Matte** : un calque de forme rectangle couvrant le mot.
  - Le bas du rectangle passe **sous le jambage du « p »**, sinon le jambage est coupé une fois la lettre posée.
  - Règle « Ephrem » sur **Cache alpha** de ce rectangle.
  - Les lettres montent une à une depuis cette ligne invisible.
- Le flou de bougé fait le reste. Ne mets pas d'opacité : la révélation par le masque est plus nette et plus chic.

### 3.7 Phrase d'invitation
- Animateurs Position (0, 40), Opacité 0 % et **Flou** 6, basés sur les **Lignes**.
- Sélecteur d'expression du §5.1 : délai 4, durée 21.

### 3.8 Picto Marin'Or : le seul rebond
- Échelle et rotation pilotées par l'expression ressort du §5.2 (marqueur à 02:18).
- **Anticipation**. Crée un **Nul** « Picto – anticipation » au centre du picto et apparente-lui le picto. Sur l'Échelle du Nul :
  - 100 % (03:10) → 90 % (03:13), courbe In ;
  - puis → 100 % (03:19), courbe Out.

  Le picto se « charge », puis libère les filets (§3.2) qui partent à 03:13 : une cause, un effet.
- Reflet CC Light Sweep à 06:00, en 18 images.

### 3.9 Infos pratiques (3 colonnes)
- Départs : DATE 03:12, HEURE 03:16, SALLE 03:20, soit 4 images d'écart.
- Dans chaque colonne : libellé (+0), valeur (+3 images), sous-ligne (+6 images).

| Ligne | Animation | Durée |
|---|---|---|
| Libellé | Opacité 0 → 100 et interlettrage qui se resserre légèrement | 18 i |
| Valeur | Position Y +80 → 0 sous Track Matte (rectangle à la hauteur de la ligne) | 21 i |
| Sous-ligne | Position Y +20 → 0 et opacité | 18 i |

- **Option « horloge » sur 11H30**, pour un rendu technique mais maîtrisé :
  - animateur **Décalage de caractères** (Character Offset), Valeur 9, avec *Plage de caractères : Préserver la casse et les chiffres* ;
  - sélecteur de plage animé de 03:19 à 04:10 ;
  - les chiffres défilent puis se posent sur l'heure exacte.
- Séparateurs : Échelle Y depuis le centre, aux départs des colonnes 2 et 3.

### 3.10 Thème
- Libellé « THÈME » : comme les autres libellés.
- Texte : animateurs Position (0, 16), Opacité 0 % et Flou 4, basés sur les **Mots**, sélecteur d'expression du §5.1 (délai 1, durée 18).
- Le thème « s'écrit » de gauche à droite, comme une phrase lue à voix haute.

---

## 4. Courbes : réglages exacts du Graph Editor

Clic droit sur une image clé, puis *Assistant d'images clés > Vélocité d'image clé*. Dans les formules :
- **Δ** est l'écart de valeur entre les 2 clés ;
- **T** est la durée en secondes ;
- **Δ/T** est la vitesse moyenne.

| Nom | Équivalent CSS | Clé de départ (sortante) | Clé d'arrivée (entrante) |
|---|---|---|---|
| **Expo Out** (apparitions) | cubic-bezier(.16, 1, .3, 1) | Influence **16 %**, vitesse **6,25 × Δ/T** | Influence **70 %**, vitesse **0** |
| **In-Out** (tracés) | cubic-bezier(.65, 0, .35, 1) | Influence **65 %**, vitesse 0 | Influence **65 %**, vitesse 0 |
| **In** (compression) | cubic-bezier(.55, 0, 1, .45) | Influence **55 %**, vitesse 0 | Influence 0,1 %, linéaire |
| **Out** (détente) | cubic-bezier(.33, 1, .68, 1) | Influence **33 %**, vitesse **3 × Δ/T** | Influence **32 %**, vitesse 0 |

Exemples calculés :
- **Logo ISTC**, Y +24 px en 21 images (0,7 s) : Δ/T = 34,3 px/s.
  - Clé 1 : 16 %, 214 px/s.
  - Clé 2 : 70 %, 0.
- **Logo Marin'Or**, échelle 94 → 100 % en 30 images (1 s) : Δ/T = 6 %/s.
  - Clé 1 : 16 %, 37,5 %/s.
  - Clé 2 : 70 %, 0.

Dans le **graphique de vitesse**, l'Expo Out doit ressembler à un pic immédiat suivi d'une longue traîne qui descend jusqu'à 0 : c'est cette traîne qui donne le côté « soyeux ».
Évite les courbes en cloche symétriques (Easy Ease F9 par défaut) pour les apparitions : elles paraissent molles.

---

## 5. Expressions à copier-coller

### 5.1 Révélation décalée : *Sélecteur d'expression > Quantité*

Sur un animateur de texte, fais *Ajouter > Sélecteur > Expression*, supprime le Sélecteur de plage, puis choisis **Basé sur** : Caractères, Mots ou Lignes.
Les propriétés de l'animateur (Position, Opacité, Flou…) sont les valeurs de **départ** ; l'expression les ramène à 0.

```javascript
// Révélation décalée « Expo Out ». Départ = 1er marqueur du calque.
var delai = 3;    // images entre deux unités (lettre, mot ou ligne)
var duree = 24;   // images d'animation par unité
var fd = thisComp.frameDuration;
var t0 = (marker.numKeys > 0) ? marker.key(1).time : inPoint;
var t = (time - t0 - (textIndex - 1) * delai * fd) / (duree * fd);
t = Math.min(Math.max(t, 0), 1);
var e = (t >= 1) ? 1 : 1 - Math.pow(2, -10 * t);  // Expo Out
var a = 100 * (1 - e);
[a, a, a];   // la Quantité attend 3 valeurs
```

Réglages utilisés :

| Calque | delai | duree |
|---|---|---|
| Ephrem | 3 | 24 |
| ISTC POLYTECHNIQUE / ABIDJAN | 3 | 18 |
| INVITATION (opacité) | 1 | 12 |
| Phrase d'invitation | 4 | 21 |
| Texte du thème | 1 | 18 |

### 5.2 Ressort du picto

Pose un marqueur sur le calque du picto à 02:18.

```javascript
// Échelle (Scale)
var t = time - marker.key(1).time;
var s = (t <= 0) ? 0 : 1 - Math.exp(-7 * t) * Math.cos(2 * Math.PI * 1.5 * t);
[100 * s, 100 * s];
```
```javascript
// Rotation
var t = time - marker.key(1).time;
var s = (t <= 0) ? 0 : 1 - Math.exp(-7 * t) * Math.cos(2 * Math.PI * 1.5 * t);
-25 * (1 - s);
```

Réglages du ressort :
- environ 10 % de dépassement, stabilisé en 0,8 s ;
- `7` règle l'amortissement : plus haut, il rebondit moins ;
- `1.5` règle la fréquence.

### 5.3 Présence discrète des éléments fixes

```javascript
// Halo lumineux – Opacité : respiration 100 → 94 % sur 8 s
100 - 6 * (1 - Math.cos(2 * Math.PI * time / 8)) / 2;
```
```javascript
// Motif haut gauche – Rotation (mettre −0.3 pour le motif bas droite)
value + 0.3 * time;
```
```javascript
// Motifs – Position : dérive lente de quelques pixels, sans à-coups
value + [4 * Math.sin(time * 0.6), 3 * Math.sin(time * 0.45)];
```

Évite `wiggle()` sur ces calques : même lent, son mouvement aléatoire ne s'accorde pas avec la précision du reste du film.

---

## 6. Export

- **Master** : séquence PNG ou ProRes 422 HQ à 2500 × 1429.
- **Diffusion** (WhatsApp, Instagram, e-mail) : H.264 en **1920 × 1098**, 30 i/s, débit variable 2 passes, 12–16 Mb/s.
  Le H.264 exige des dimensions paires, or 1429 est impair. Redimensionne à la sortie, ou étends la compo à 2500 × 1430 en prolongeant le fond crème d'un pixel.
- Pour un statut WhatsApp en boucle, la tenue de 06:18 à 10:00 suffit : la vidéo reboucle sur un fond identique.
