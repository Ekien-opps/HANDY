# Soutenance Marin'Or Ivoire : notes de conception et vérifications

Mémoire : *Conception et réalisation de supports de communication pour la promotion de Marin'Or Ivoire*, Ekien Kouadio Constant Ephrem, ISTC Polytechnique, 2025-2026.

## 1. Fichiers livrés

| Fichier | Contenu |
|---|---|
| `Soutenance_MarinOr_Ivoire.pptx` (40 Mo) | Version principale : 47 diapositives 16:9, Morph sur toutes les diapositives, 15 produits en vrais modèles 3D (diapositives 13 à 18), 3 vidéos, notes de l'orateur avec durée. |
| `Soutenance_MarinOr_Ivoire_SECOURS_sans3D.pptx` (31 Mo) | Même deck, les modèles 3D remplacés par leurs images rendues. Morph identique (déplacements et zooms), sans la rotation 3D en direct. À garder sur la clé USB si la machine de soutenance refuse la 3D. |
| `source/` | Scripts qui génèrent le deck (Python et three.js), pour refaire une version après correction. |

## 2. Choix de design

### Couleurs (charte du mémoire, p. 40)

| Rôle dans le deck | Couleur | Code |
|---|---|---|
| Titres sur fond clair, panneaux, barres | Bordeaux Profond | `#7B1421` |
| Repères de section sur fond clair, valeurs « non conforme » | Rouge Passion | `#A40C21` |
| Numéros, anneau, lignes de lumière, accents sur fond foncé | Or Épicé | `#F9A825` |
| Reflet chaud des titres, dégradés | Jaune Soleil | `#FBD021` |
| Textes sur fond foncé, dégradé des titres | Crème Douce | `#FFECD1` |
| Fond de la partie site web (diapositives 38 à 43) | Rose Poudre | `#F6E8EA` |
| Valeur « conformes » (diapositive 43) | Vert Nature | `#2A5519` |
| Texte courant sur fond clair | Noir Intense | `#000000` |
| Cartes, cadre des vidéos | Blanc Pureté | `#FFFFFF` |

Deux teintes **dérivées** (non présentes dans la charte, signalées) :

- `#2A070D` : Bordeaux Profond assombri, fond des diapositives foncées.
- `#FFF6EA` : Crème Douce éclaircie, fond des diapositives claires. La Crème pure, trop saturée en grande surface, sert aux reflets.

### Polices

- **Cream Heavy** : titres et chiffres forts.
- **Montserrat** (Medium, SemiBold) : textes, repères, légendes.
- **RadioTime Tooled** : non utilisée comme police, conformément à la charte (réservée au logotype). Elle apparaît seulement dans les images du logo.
- Le thème du fichier est réglé sur ces polices et sur les 10 couleurs de la charte. Une diapositive ajoutée restera donc dans la charte.

### Logo

- Version **couleur** sur les fonds clairs, version **blanche** sur les fonds foncés (fichiers que tu m'as envoyés), conformément à la p. 38.
- Il est petit en haut à droite, sauf sur les diapositives où il est le sujet (1, 5, 21, 47).

## 3. Écarts par rapport à Nova X

Repris de Nova X : la **structure** seulement, à savoir :

- page d'accueil, page de garde, plan ;
- problématique, objectifs, charte (logo, typographie, couleurs, déclinaisons, interdits, mise en application, animation), axes ;
- intercalaires numérotés, puis pour chaque support le visuel final et sa mise en situation ;
- spots, calendrier, coût, conclusion, remerciements ;
- une idée et un visuel dominant par diapositive, très peu de texte.

Différences volontaires :

1. **Couleurs, logo et contenus** : aucun repris de Nova X (bleu et orange abandonnés au profit du bordeaux, de l'or et de la crème de Marin'Or).
2. **Grand demi-cercle orange** de Nova X remplacé par un anneau or fin, mobile, qui sert de repère de « caméra ».
3. **Section produits en 3D** (6 diapositives) ajoutée : elle n'existe pas dans Nova X.
4. **Intercalaires** : numéro en contour au-dessus du titre (Nova X utilise une icône dans un cercle).
5. **Pas de diapositive « Outils / Logiciels »** comme dans Nova X : les logiciels sont cités sur les diapositives concernées et dans les notes. La place a servi à la base de données et aux tests.
6. **Pas de calendrier imprimé** (support propre à Nova X) : le calendrier de réalisation est présenté comme dans le mémoire (Tableau 2).

## 4. Effets : natifs, simulés, approximatifs

| Effet demandé | Réalisation | Ce qui est approximatif |
|---|---|---|
| Morph sur tout le deck, mouvement de caméra continu | Transition Morph native sur les 47 diapositives (1,4 à 2 s). Objets de même nom `!!…` d'une diapositive à l'autre : fond (couleur interpolée), motif de la marque, halo, anneau, titres, logo, images. Le motif glisse d'environ 0,2 po à chaque diapositive (panoramique doux) et grossit de 16 % sur les intercalaires (changement de focale). | L'easing de Morph n'est pas réglable : c'est celui de PowerPoint, doux par défaut. Entre deux images différentes de même nom, Morph fait un fondu enchaîné pendant le déplacement. |
| Morph 3D des 15 produits | Vrais modèles 3D (glTF) dans PowerPoint, même nom sur les 6 diapositives : ils apparaissent en orbite (13), se posent alignés (14), travelling avant sur les marinades (15), grille des épices (16), essentiels en gros plan (17), présentoir en gradins (18). Rotation et position interpolées par Morph. | Les modèles ont été allégés (environ 107 000 triangles à 22 000-32 000) pour rester fluides. L'échelle des modèles est déduite de l'exemple officiel Microsoft : à vérifier sur la machine (voir § 6). |
| Ombres de contact des produits | Ellipses en dégradé radial transparent sous chaque produit. Absentes sur la diapositive 13 : elles « apparaissent » quand les produits se posent sur la 14. | Ce ne sont pas des ombres calculées par la 3D. |
| Flou de profondeur | Diapositive 18 uniquement : photo du plat traditionnel pré-floutée derrière les produits (vrai flou, au service de l'envie de manger). | Pas de flou en direct sur la 3D (impossible dans PowerPoint). |
| Flou de mouvement | Volontairement non utilisé : rien dans le récit ne le justifiait. | — |
| Grain subtil | Image PNG de bruit monochrome (environ 5,5 % d'opacité), identique sur toutes les diapositives : il ne scintille pas pendant Morph. | Grain fixe, pas animé comme un vrai grain de film. |
| Reflets de bord (rim light) | Titres sur fond foncé en dégradé crème vers or chaud ; arêtes dorées en dégradé sur les gradins (18) ; lumières PowerPoint par défaut sur les modèles 3D. | Simulation par dégradés. |
| Aberration chromatique très discrète | Deux copies du titre décalées de 0,02 po, en Rouge Passion et Jaune Soleil très transparents, sur les diapositives foncées clés (1, 13, 18, 19, 28, 37, 47). | Statique. Selon le projecteur, elle peut devenir invisible. |
| Dégradés, vignettage, halo | Dégradés natifs avec transparence, vignette PNG sur les fonds foncés, halos qui dérivent d'une diapositive à l'autre. | — |
| Points lumineux « épices » | Image pré-rendue de particules dorées floues (1, 18, 47). | — |

Compatibilité PowerPoint 2019 :

- Morph et modèles 3D : oui (Office 2019 et Microsoft 365, Windows et Mac).
- PowerPoint 2016 ou antérieur, LibreOffice, Google Slides : la transition devient un fondu et les modèles 3D s'affichent comme leurs images. Le contenu reste complet.

## 5. Contrôle qualité effectué

| Vérification | Résultat |
|---|---|
| Nombre de diapositives | **47** (dans la fourchette 45-47). |
| Limite de 6 lignes | Mesurée avec les vraies polices, repère de section compris (hors numéro de page), en comptant comme une seule ligne des colonnes côte à côte. **0 diapositive au-dessus de 6** ; maximum 6. |
| Validité du fichier | Validateur officiel Microsoft Open XML SDK 3.1 : **0 erreur**. Les 90 modèles 3D, validés un par un contre le schéma Office 2019 : **0 erreur** (le contrôle détecte bien une erreur volontairement injectée). Le schéma Morph n'est pas connu du SDK ; son XML suit la forme écrite par PowerPoint. |
| Noms Morph | Aucun nom en double dans une même diapositive. |
| Chiffres | Tous les nombres des diapositives et des notes ont été comparés automatiquement au texte du mémoire : tous présents, sauf 2 sommes calculées (voir § 6). |
| Lisibilité et contraste | Bordeaux sur crème : environ 10:1. Crème sur bordeaux foncé : environ 16:1. Noir sur clair : environ 19:1. L'or n'est jamais utilisé pour du texte courant sur fond clair (contraste insuffisant), seulement en grands chiffres décoratifs ou sur fond foncé. Texte courant à 16 pt minimum ; légendes à 12-13 pt. |
| Rendu | Les 47 diapositives ont été rendues et relues visuellement (rendu LibreOffice, qui affiche les images de secours à la place de la 3D). |

## 6. Liste de vérifications avant la soutenance

### a) Chiffres et incohérences à recontrôler (dans le mémoire ou à l'oral)

1. **Spot 2D**
   - Le mémoire annonce 60 s (p. 49 et 98) ; le fichier `2D_final_.mp4` dure **41 s**.
   - La p. 50 dit « gamme complète de **12** produits » dans la description visuelle et « **15** produits » dans la voix off.
2. **Spot 3D** : le mémoire annonce 40 à 60 s (p. 50 et 99) ; le film dure **1 min 31 s**.
3. **Animation du logo** : le mémoire indique 7 s à 29,97 images/s (Tableau 4) ; le fichier dure **5 s à 60 images/s**. Le deck ne cite aucune de ces durées.
4. **Tests 10 et 11** : encore marqués « [À vérifier] » dans le Tableau 16 (p. 111). La diapositive 43 affiche « 2 à vérifier ». Mets à jour le mémoire et la diapositive si les tests ont été faits.
5. **Test 17 « non conforme »** (smartphone), alors que la p. 68 affirme une « adaptation aux écrans de smartphone ». Prépare une réponse.
6. **Figures 48, 51 et 54** (maquettes des 3 affiches) : dans le Word, c'est **la même image** pour les trois.
7. **Adresse du site** : `marinorivoire.ci` dans le mémoire (p. 51) et sur les affiches, mais `marinorivoire.com` sur l'écran de fin des spots.
8. **Conditionnements et noms**
   - Le Tableau 1 indique Purée d'ail « Pot » et Huile rouge « Bidon » ; les modèles 3D montrent un sachet et une bouteille.
   - Noms courts sur les emballages (« Poudre de Crevette », « Bouillon de Poulet ») et noms du mémoire (« Poudre de crevettes séchées », « Bouillon bio de poulet »). Le deck utilise les noms du mémoire.
9. **Dépliant** : le verso présente 3 + 10 = 13 produits ; les deux épices spéciales manquent.
10. **Diapositive 45** : « Spots 2D et 3D : 2 400 000 » et « Supports imprimés : 600 000 » sont **des sommes que j'ai calculées** (900 000 + 1 500 000 ; 300 000 + 3 × 100 000). Les lignes détaillées sont dans les notes. Total 7 000 000 FCFA conforme au Tableau 3.
11. **Diapositive 9** : la phrase « diagnostic empirique et analyse comparative des marques concurrentes » vient de ton message, **pas du mémoire**. Ajoute-la au mémoire ou assume-la à l'oral.
12. **Hypothèse** : la conclusion du mémoire ne dit pas explicitement si elle est vérifiée. Le deck n'affirme rien à ce sujet ; prépare la réponse.
13. Les captures du site (diapositives 39 à 41) montrent des **prix** qui ne figurent pas dans le mémoire.
14. Textes condensés : certains passages ont été raccourcis pour tenir en 6 lignes (par exemple diapositive 16, synthèse des usages du Tableau 1). Aucun chiffre ni nom n'a été modifié.

### b) Polices à installer sur la machine de soutenance

- **Cream Heavy** (`Cream-Heavy.ttf`, dans ton Drive).
- **Montserrat** Medium, SemiBold, Regular et Bold (`montserrat.zip`, fichiers `.ttf`).
- Clic droit, puis « Installer pour tous les utilisateurs », puis redémarrer PowerPoint.
- Plus sûr encore : sur ton propre PC, ouvre le .pptx, va dans *Fichier › Options › Enregistrer › Incorporer les polices dans le fichier* (toutes les polices), puis enregistre. Cream Heavy et Montserrat autorisent l'incorporation.
- Cream Heavy est une police commerciale (Paulo Goode) : vérifie ta licence.

### c) Test de la 3D et de Morph sur la machine de soutenance (au moins la veille)

1. Version de PowerPoint : 2019, 2021 ou Microsoft 365. Morph et la 3D n'existent pas dans PowerPoint 2016. Si c'est 2016, utilise la version SECOURS (fondus au lieu de Morph).
2. Ouvre le fichier, puis lance le diaporama depuis la diapositive 12 et avance jusqu'à la 19 :
   - les 15 produits doivent apparaître, se poser, puis zoomer ;
   - vérifie la fluidité (si ça saccade : fermer les autres logiciels, brancher le secteur, mode performances).
3. **Taille des produits 3D** : si un produit paraît trop grand ou trop petit, garde la version SECOURS, ou sélectionne le modèle et utilise *Modèle 3D › Panoramique et zoom*. L'échelle a été calculée d'après l'exemple officiel Microsoft, mais n'a pas pu être testée dans PowerPoint ici.
4. Vidéos (diapositives 27, 35, 36) : **clique sur la vidéo** pour la lancer (clic sur le cadre, pas sur le fond). Vérifie le son du vidéoprojecteur.
5. Teste les deux fichiers sur l'ordinateur et le projecteur réels : couleurs (le bordeaux foncé peut boucher sur un projecteur faible), lisibilité des légendes en 12 pt au fond de la salle.
6. Copie les deux fichiers et les polices sur une clé USB.

### d) Durée par diapositive

Ces durées figurent aussi au début des notes de l'orateur, entre crochets. Total **14 min 20 s** pour 15 min : environ 40 s de marge. Les transitions Morph (1,4 à 2 s) se font pendant que tu parles.

| N° | Diapositive | Durée | Cumul |
|---|---|---|---|
| 1 | Bienvenue | 10 s | 0:10 |
| 2 | Conception et réalisation de supports de communi | 20 s | 0:30 |
| 3 | Plan de la présentation | 15 s | 0:45 |
| 4 | Contexte | 20 s | 1:05 |
| 5 | Marin'Or Ivoire | 20 s | 1:25 |
| 6 | Constats de l'existant | 25 s | 1:50 |
| 7 | Comment concevoir et réaliser des supports de co | 25 s | 2:15 |
| 8 | Hypothèse | 20 s | 2:35 |
| 9 | Méthodologie qualitative | 25 s | 3:00 |
| 10 | Objectifs | 20 s | 3:20 |
| 11 | Public cible | 20 s | 3:40 |
| 12 | Trois axes de communication | 20 s | 4:00 |
| 13 | Présentation des produits | 10 s | 4:10 |
| 14 | 15 produits, 3 familles | 20 s | 4:30 |
| 15 | Les Marinades | 18 s | 4:48 |
| 16 | Les Épices | 18 s | 5:06 |
| 17 | Les Essentiels | 14 s | 5:20 |
| 18 | Le vrai goût de chez nous | 15 s | 5:35 |
| 19 | Identité visuelle et charte graphique | 8 s | 5:43 |
| 20 | Trois pistes explorées | 22 s | 6:05 |
| 21 | Le logo retenu | 25 s | 6:30 |
| 22 | Zone de protection et déclinaisons | 15 s | 6:45 |
| 23 | Les interdits | 10 s | 6:55 |
| 24 | Typographie | 18 s | 7:13 |
| 25 | Colorimétrie | 18 s | 7:31 |
| 26 | Mise en application | 15 s | 7:46 |
| 27 | Animation du logotype | 12 s | 7:58 |
| 28 | Supports print et audiovisuels | 8 s | 8:06 |
| 29 | Le vrai goût de chez nous | 18 s | 8:24 |
| 30 | Le goût qui rassemble | 15 s | 8:39 |
| 31 | Marinez, Cuisez, Régalez-vous | 15 s | 8:54 |
| 32 | Dépliant trois volets | 20 s | 9:14 |
| 33 | Marinez, Cuisez, Régalez-vous ! | 15 s | 9:29 |
| 34 | Le goût qui rassemble ! | 15 s | 9:44 |
| 35 | Spot 2D | 25 s | 10:09 |
| 36 | Spot 3D | 25 s | 10:34 |
| 37 | Le site web : une boutique en ligne | 8 s | 10:42 |
| 38 | Structure de navigation | 20 s | 11:02 |
| 39 | Accueil et gammes | 20 s | 11:22 |
| 40 | Commander et payer | 25 s | 11:47 |
| 41 | Le back-office | 18 s | 12:05 |
| 42 | Base de données | 20 s | 12:25 |
| 43 | Tests fonctionnels | 25 s | 12:50 |
| 44 | 63 jours de réalisation | 20 s | 13:10 |
| 45 | Coût estimatif : 7 000 000 FCFA | 20 s | 13:30 |
| 46 | Conclusion | 35 s | 14:05 |
| 47 | Merci de votre attention | 15 s | 14:20 |

