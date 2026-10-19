# Guide d'animation After Effects : VISUEL_INVITE

Fichier source : `VISUEL_INVITE.psd` (700 × 379 px).
Aperçu du rendu attendu : `animatic_visuel-invite.mp4`. Il utilise exactement les timings et courbes de ce guide.

> Dans l'animatic, **Cream Heavy** (le mot « Ephrem ») est remplacée par une police proche, faute de disponibilité ici. Dans After Effects, garde bien Cream Heavy.

---

## 0. Intention artistique : « Le lever de rideau »

**La bande crème monte comme un rideau de scène.** Elle installe l'espace, puis les informations s'y déposent, avec une logique de lecture du haut vers le bas.

| Règle | Application |
|---|---|
| **Une direction principale** | Les textes montent depuis une ligne invisible (Track Matte). |
| **Une seule exception** | Le pied de page sort latéralement du filet or, qui joue le rôle de « source ». |
| **Trois courbes** | Expo Out (apparitions), In-Out (tracés), Ressort (signature). |
| **Une seule signature rebondie** | **« Ephrem » en Cream Heavy** : la police « gourmande » de la charte gagne un petit ressort lettre par lettre. C'est le seul élément qui rebondit. |
| **Décalages réguliers** | 2 images entre deux lettres ou mots d'accroche, 4 images entre deux lignes de titre, 1 image entre deux mots du thème. |
| **Une anticipation** | Le filet or se comprime avant de « libérer » le lieu. |
| **Lumière finale** | Un reflet sur le logo, puis un reflet qui traverse le bandeau en verre dépoli. |

### Éléments fixes (conformes à ta demande)

| Calques PSD | Traitement |
|---|---|
| Fond bordeaux, Dégradé rouge passion (haut) | Immobiles |
| Texture motif Marin'Or | Quasi immobile : dérive de ±3 px |
| Motif Marin'Or (en haut à droite) | Quasi immobile : rotation de 0,3°/s |
| Photo façade ISTC, Luminosité/Contraste 1, Assombrissement bas | Quasi immobiles : très lent zoom avant de 100 → 103 % sur 10 s |

Tout le reste s'anime : bande crème, logos, pastille, textes, bandeau, filet.

---

## 1. Préparation

1. **Définition.** Le PSD fait 700 × 379 px : c'est petit pour une vidéo, et 379 est impair, ce que refuse l'export H.264.
   - **Si c'est une copie allégée**, travaille avec ton fichier en pleine définition.
   - **Sinon**, travaille en **1400 × 758** (×2, dimensions paires). Toutes les valeurs de ce guide sont données dans ce format.
2. **Import** : *Fichier > Importer*, type **Composition – Conserver la taille des calques**, avec **Styles de calques modifiables**.
3. **Passage en 1400 × 758** : ouvre la compo, puis *Fichier > Scripts > Scale Composition.jsx* avec un facteur de **2**.
   - Textes et formes restent nets.
   - Les images (photo, logos) seront un peu douces. Remplace les logos par leurs versions HD : `sources-psd/src/assets/logo_marinor.png` et `logo_istc.png`.
4. **Groupe « Photo ISTC »** : **ne l'aplatis pas**. Laisse-le en précomposition fixe, car il contient le réglage Luminosité/Contraste écrêté sur la photo.
   - Si ce réglage ne s'affiche pas comme dans Photoshop, transforme le groupe en **objet dynamique** dans Photoshop avant l'import.
5. **Aplatir les autres dossiers** (Logos, Titre, Bandeau infos, Thème, Pied de page) :
   - ouvre la précomp, coupe ses calques, colle-les dans la compo principale, puis supprime la précomp vide ;
   - tu obtiens une seule timeline.
6. **Textes** : *Calque > Créer > Convertir en texte modifiable*. Cream Heavy et Montserrat doivent être installées.
7. **Titre en 3 calques.** Duplique « Titre – Soutenance… » en 3 calques et garde une seule ligne par calque : « Soutenance de », « Licence », « Professionnelle ». Chaque ligne aura son propre masque.
8. **Contour du bandeau en calque de forme** (nécessaire pour le Trim Paths). Masque le calque PSD « Bandeau – contour », puis crée un calque de forme :
   - Position du calque [0, 0], Point d'ancrage [0, 0] ;
   - *Rectangle* : Position **380,8 ; 513,7**, Taille **637,3 × 128,3**, Arrondi **19,6** ;
   - *Contour* : **1,1 px**, blanc, opacité **28 %** ;
   - *Trim Paths*.
9. **Points d'ancrage** :
   - au centre : logo Marin'Or, pastille, logo ISTC, séparateur du bandeau, filet or, fond du bandeau ;
   - **base de la lettre** pour « Ephrem » : c'est le comportement par défaut des animateurs de texte.
10. **Flou de bougé** : active-le sur tout ce qui bouge. Angle 180°, phase −90°, 16 échantillons.
11. **Marqueurs** (touche `*` du pavé numérique) : un marqueur de calque au temps de départ du §2, sur chaque texte animé par expression.

---

## 2. Timeline (30 i/s, SS:II = secondes:images, compo 1400 × 758)

| # | Début | Fin | Élément | Mouvement | Courbe |
|---|---|---|---|---|---|
| 0 | 00:00 | 10:00 | Fond, motifs, photo | Fixes : dérive, rotation et zoom discrets | Expression |
| 1 | 00:06 | 01:00 | **Bande crème** (Rectangle 1) | Position Y +140 px → 0 : le rideau monte | Expo Out |
| 2 | 00:12 | 01:12 | **Logo Marin'Or** | Masque ovale qui s'ouvre + échelle 94 → 100 % | Expo Out |
| 3 | 00:18 | 01:09 | Pastille blanche ISTC | Échelle 90 → 100 %, opacité 0 → 100 | Expo Out |
| 4 | 00:22 | 01:10 | Logo ISTC | Échelle 96 → 100 %, opacité (4 images après la pastille) | Expo Out |
| 5 | 01:00 | 02:04 | **« Ephrem »** (Cream Heavy) | Lettre par lettre, échelle 0 → 100 % en **ressort**, 2 images d'écart | Ressort |
| 6 | 01:10 | 02:01 | « vous invite à sa » | Mot à mot, Y +8 → 0 et opacité, 2 images d'écart | Expo Out |
| 7 | 01:12 / 01:16 / 01:20 | 02:06 / 02:10 / 02:14 | **Titre** (3 lignes) | Chaque ligne monte sous son masque (+72 px → 0) | Expo Out |
| 8 | 01:24 | 02:24 | Contour du bandeau | Trim Paths depuis le centre haut, dans les 2 sens | In-Out |
| 9 | 02:00 | 02:20 | Fond translucide du bandeau | Opacité 0 → 14 %, échelle 96 → 100 % | Expo Out |
| 10 | 02:04 | 02:22 | Séparateur du bandeau | Échelle Y 0 → 100 % (centre) | Expo Out |
| 11 | 02:06 | 02:27 | « Vendredi 23 » | Montée sous masque (+60 px → 0) | Expo Out |
| 12 | 02:09 | 03:00 | « Octobre · 11H30 » | Y +14 → 0 et opacité ; **les chiffres de 11H30 défilent** | Expo Out |
| 13 | 02:10 | 03:01 | « ISTC » | Montée sous masque (+60 px → 0) | Expo Out |
| 14 | 02:13 | 03:01 | « Polytechnique · Abidjan » | Y +14 → 0 et opacité | Expo Out |
| 15 | 02:18 | 03:06 | Libellé THÈME | Interlettrage qui se resserre + opacité | Expo Out |
| 16 | 02:24 | 03:24 | Texte du thème | Mot à mot, 1 image d'écart : Y +12 → 0, opacité, flou 3 → 0 | Expo Out |
| 17 | 02:24 | 03:18 | **Filet vertical or** | Échelle Y 0 → 100 % depuis le centre | In-Out |
| 18 | 03:18 | 03:27 | Filet : anticipation | Échelle Y 100 → 90 % (03:21) → 100 % | In puis Out |
| 19 | 03:21 | 04:09 | Libellé LIEU | Sort du filet : X −60 → 0 sous masque, opacité | Expo Out |
| 20 | 03:24 | 04:15 | « Salle Victor Merry » | Sort du filet : X −120 → 0 sous masque, opacité | Expo Out |
| 21 | 04:20 | 05:14 | Reflet sur le logo Marin'Or | CC Light Sweep, de gauche à droite | In-Out |
| 22 | 05:00 | 06:00 | **Reflet sur le verre du bandeau** | Bande lumineuse oblique qui traverse le bandeau | In-Out |
| 23 | 06:00 | 10:00 | Tenue | Image complète et lisible | — |

Rythme global :
- **0–1,2 s** : le décor se met en place (rideau, logos) ;
- **1–2,5 s** : le message (Ephrem, titre) ;
- **2–4,5 s** : les informations, en cascade de haut en bas ;
- **4,7–6 s** : la lumière ;
- **6–10 s** : la lecture.

---

## 3. Techniques par élément

### 3.1 Bande crème : le rideau
- Position Y : **+140 px → 0**, de 00:06 à 01:00, en Expo Out.
- Elle part hors cadre, donc sans fondu : c'est sa vitesse qui fait l'élégance.
- Elle ne dépasse pas sa position finale : pas de rebond.

### 3.2 Logo Marin'Or
- **Masque ellipse** à la forme du badge : Expansion de masque −150 → 0 px, contour progressif de 20 px.
- **Échelle** 94 → 100 % ; **Opacité** 0 → 100 % sur les 9 premières images.
- **Reflet** à 04:20 avec CC Light Sweep : direction 15°, largeur 30, intensité 40, bord 0, forme Smooth. Anime le Centre de la gauche hors du logo jusqu'à la droite hors du logo, en 24 images, courbe In-Out.

### 3.3 Pastille et logo ISTC
- La pastille apparaît d'abord : échelle 90 → 100 % et opacité.
- 4 images plus tard, le logo ISTC suit : échelle 96 → 100 % et opacité.
- Ce léger décalage donne l'impression que le logo « se dépose » dans la pastille.

### 3.4 Accroche : « Ephrem vous invite à sa »
Il n'y a qu'un calque de texte, avec **deux animateurs** pilotés par expression (§5.1 et §5.2) :

| Animateur | Propriétés | Basé sur | Agit sur | Expression | Marqueur |
|---|---|---|---|---|---|
| 1 | Échelle 0 %, Opacité 0 % | Caractères | Les 6 lettres de « Ephrem » | Ressort (§5.2) | 01:00 |
| 2 | Position (0, 8), Opacité 0 % | Mots | À partir du 2ᵉ mot | Révélation (§5.1), premier = 2, décalage = 10 images | même marqueur |

Les lettres de Cream Heavy « poussent » depuis leur ligne de base avec environ 10 % de dépassement, puis se posent. Le reste de la phrase suit sobrement.

### 3.5 Titre (3 calques d'une ligne)
- Sur chaque calque : Position Y **+72 → 0** en Expo Out, sur 24 images.
- Départs : 01:12, 01:16 et 01:20, soit 4 images d'écart.
- **Track Matte** : un rectangle par ligne, en **Cache alpha**, dont le bas passe juste sous la ligne de base. La ligne monte depuis une fente invisible.
- Variante plus riche : ajoute un animateur Flou (6 → 0) piloté par la même courbe.

### 3.6 Bandeau infos (effet « verre dépoli »)
1. **Contour** : Trim Paths **Début 50 → 0 %** et **Fin 50 → 100 %**, de 01:24 à 02:24, courbe In-Out. Règle le **Décalage** pour que le départ soit au **centre haut**, au-dessus du séparateur.
2. **Fond translucide** : opacité 0 → 14 % et échelle 96 → 100 % (02:00–02:20). La plaque de verre « se remplit » une fois tracée.
3. **Séparateur** : échelle Y depuis le centre (02:04–02:22).
4. **« Vendredi 23 » et « ISTC »** : montée sous masque de +60 px → 0, chacun avec son rectangle en Cache alpha.
5. **« Octobre · 11H30 » et « Polytechnique · Abidjan »** : Y +14 → 0 et opacité.
6. **Défilement de l'heure** : sur « Octobre · 11H30 », ajoute un animateur **Décalage de caractères** :
   - *Plage de caractères : Préserver la casse et les chiffres* ;
   - sélecteur d'expression du §5.3, qui ne touche que les 4 chiffres ;
   - images clés sur Décalage de caractères : **9 → 0**, de 02:09 à 03:00, en Expo Out.
7. **Reflet sur le verre** (05:00–06:00) :
   - un calque de forme rectangle de 160 × 260 px, en **dégradé linéaire** transparent → blanc 28 % → transparent, avec **Inclinaison** −20° dans la *Transformation* du groupe ;
   - sa Position X va de la gauche hors du bandeau jusqu'à la droite hors du bandeau, courbe In-Out ;
   - **Track Matte** : *Cache alpha* sur une copie du « Bandeau – fond translucide » réglée à 100 % d'opacité ;
   - c'est le détail « haut de gamme » de la fin.

### 3.7 Thème (dans la bande crème)
- Libellé **THÈME** : opacité 0 → 100 et interlettrage qui se resserre (02:18–03:06).
- Texte : animateurs Position (0, 12), Opacité 0 % et Flou 3, **basés sur les mots**, sélecteur du §5.1 (premier = 1, délai 1, durée 18). Marqueur à 02:24.

### 3.8 Pied de page : le filet comme source
1. **Filet vertical or** : échelle Y 0 → 100 % depuis le centre (02:24–03:18), courbe In-Out.
2. **Anticipation** : échelle Y 100 → **90 %** (03:18–03:21, courbe In), puis → 100 % (03:21–03:27, courbe Out). Le filet se « charge ».
3. **LIEU**, puis **Salle Victor Merry** 3 images après :
   - Position X −60 et −120 px → 0, opacité 0 → 100, en Expo Out ;
   - **Track Matte** : un rectangle qui commence au bord droit du filet, en Cache alpha. Les textes semblent naître du filet.

---

## 4. Courbes : réglages exacts du Graph Editor

Clic droit sur une image clé, puis *Assistant d'images clés > Vélocité d'image clé*. Dans les formules, **Δ/T** est la vitesse moyenne (écart de valeur ÷ durée en secondes).

| Nom | Équivalent CSS | Clé de départ (sortante) | Clé d'arrivée (entrante) |
|---|---|---|---|
| **Expo Out** (apparitions) | cubic-bezier(.16, 1, .3, 1) | Influence **16 %**, vitesse **6,25 × Δ/T** | Influence **70 %**, vitesse **0** |
| **In-Out** (tracés) | cubic-bezier(.65, 0, .35, 1) | Influence **65 %**, vitesse 0 | Influence **65 %**, vitesse 0 |
| **In** (compression) | cubic-bezier(.55, 0, 1, .45) | Influence **55 %**, vitesse 0 | Influence 0,1 %, linéaire |
| **Out** (détente) | cubic-bezier(.33, 1, .68, 1) | Influence **33 %**, vitesse **3 × Δ/T** | Influence **32 %**, vitesse 0 |

Exemples calculés :
- **Bande crème**, 140 px en 24 images (0,8 s) : Δ/T = 175 px/s.
  - Clé 1 : 16 %, 1094 px/s.
  - Clé 2 : 70 %, 0.
- **Ligne de titre**, 72 px en 24 images : Δ/T = 90 px/s.
  - Clé 1 : 16 %, 562 px/s.
  - Clé 2 : 70 %, 0.
- **Salle Victor Merry**, 120 px en 21 images (0,7 s) : Δ/T = 171 px/s.
  - Clé 1 : 16 %, 1071 px/s.
  - Clé 2 : 70 %, 0.

Dans le graphique de vitesse, l'Expo Out montre un pic immédiat suivi d'une longue traîne jusqu'à 0. N'utilise pas l'Easy Ease par défaut (F9) pour les apparitions : il paraît mou.

---

## 5. Expressions à copier-coller

Sélecteurs d'expression : sur un animateur, fais *Ajouter > Sélecteur > Expression*, supprime le Sélecteur de plage, puis règle **Basé sur**. Les valeurs de l'animateur sont les valeurs de départ.

### 5.1 Révélation décalée « Expo Out » (mots, lignes, caractères)
```javascript
var premier = 1;    // 1re unité animée (2 = ignorer « Ephrem » dans l'accroche)
var decalage = 0;   // images de retard après le marqueur
var delai = 1;      // images entre deux unités
var duree = 18;     // images par unité
var fd = thisComp.frameDuration;
var t0 = ((marker.numKeys > 0) ? marker.key(1).time : inPoint) + decalage * fd;
var a = 0;
if (textIndex >= premier) {
  var t = (time - t0 - (textIndex - premier) * delai * fd) / (duree * fd);
  t = Math.min(Math.max(t, 0), 1);
  var e = (t >= 1) ? 1 : 1 - Math.pow(2, -10 * t);
  a = 100 * (1 - e);
}
[a, a, a];
```

Réglages :

| Calque | premier | decalage | delai | duree |
|---|---|---|---|---|
| Accroche, animateur mots | 2 | 10 | 2 | 15 |
| Texte du thème | 1 | 0 | 1 | 18 |

### 5.2 Ressort lettre par lettre : « Ephrem »
Basé sur **Caractères**, marqueur à 01:00.
```javascript
var n = 6;          // lettres de « Ephrem »
var delai = 2;      // images entre deux lettres
var fd = thisComp.frameDuration;
var a = 0;
if (textIndex <= n) {
  var t = time - marker.key(1).time - (textIndex - 1) * delai * fd;
  var s = (t <= 0) ? 0 : 1 - Math.exp(-7 * t) * Math.cos(2 * Math.PI * 1.5 * t);
  a = 100 * (1 - s);   // négatif pendant le dépassement : l'échelle passe un peu au-dessus de 100 %
}
[a, a, a];
```

Réglages du ressort :
- environ 10 % de dépassement, stabilisé en 0,8 s ;
- `7` règle l'amortissement : plus haut, il rebondit moins ;
- `1.5` règle la fréquence.

### 5.3 Défilement des chiffres de « 11H30 »
Sélecteur d'expression basé sur les **Caractères**, dans l'animateur Décalage de caractères.
```javascript
// « Octobre · 11H30 » : positions des 4 chiffres (le H ne bouge pas)
var chiffres = [11, 12, 14, 15];
var a = (chiffres.indexOf(textIndex) >= 0) ? 100 : 0;
[a, a, a];
```
Si tu modifies le texte, recompte les positions (espaces compris, à partir de 1).

### 5.4 Présence discrète des éléments fixes
```javascript
// Précomp « Photo ISTC » – Échelle : zoom 100 → 103 % sur 10 s
// (place son point d'ancrage vers la droite de l'image, sur la façade)
value + [0.3 * time, 0.3 * time];
```
```javascript
// Texture motif Marin'Or – Position : dérive lente
value + [3 * Math.sin(time * 0.5), 2 * Math.sin(time * 0.4)];
```
```javascript
// Motif Marin'Or (en haut à droite) – Rotation
value + 0.3 * time;
```

---

## 6. Export

- **Master** : ProRes 422 HQ ou séquence PNG en 1400 × 758.
- **Diffusion** (WhatsApp, réseaux) : H.264 en 1400 × 758 ou 1920 × 1040, 30 i/s, débit variable 2 passes, 10–14 Mb/s.
- Pour un statut WhatsApp en boucle, la tenue de 06:00 à 10:00 suffit.
