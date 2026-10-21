# Soutenance Marin'Or Ivoire : notes de conception et vérifications (version 2)

Mémoire : *Conception et réalisation de supports de communication pour la promotion de Marin'Or Ivoire*, Ekien Kouadio Constant Ephrem, ISTC Polytechnique, 2025-2026.

## 1. Fichiers

| Fichier | Contenu |
|---|---|
| `Soutenance_MarinOr_Ivoire.pptx` (35 Mo) | Version principale : **46 diapositives** 16:9. Morph 3D sur la séquence produits uniquement. Une règle d'apparition unique partout ailleurs. Notes de l'orateur avec durée. |
| `Soutenance_MarinOr_Ivoire_SECOURS_sans3D.pptx` (25 Mo) | Identique, mais les modèles 3D sont remplacés par leurs images rendues. Même Morph (déplacements et zooms), sans la rotation 3D en direct. |
| `source/` | Scripts de génération (`deck2.py` = cette version). |

## 2. Ce qui a changé par rapport à la version 1

| Consigne | Application |
|---|---|
| Supprimer la diapositive 1 « Bienvenue » | Supprimée. La page de garde ouvre le deck. **Toute la numérotation recule d'un cran** (voir § 7). |
| Supprimer le cercle doré | L'anneau a disparu de toutes les diapositives. |
| Supprimer overlays, films, textures, motifs | Supprimés : motif de la marque, grain, vignettage, halos lumineux, particules dorées, photo floutée et voile sombre de l'ancienne diapositive 18. |
| Titres sans doublon | Les copies décalées (aberration chromatique) et le dégradé des titres sont supprimés. Chaque titre est désormais une seule zone de texte de couleur unie. |
| Fonds unis ou dégradés intelligents (anciennes 1, 7, 8, 13, 18, 19, 28, 37, 47) | Bordeaux Profond. Dégradé très subtil `#8A1828` → `#68101C` (35°) sur les anciennes 7, 8, 13, 19, 28, 37, 47. **L'ancienne 18 (présentoir) est en `#7B1421` totalement uni.** L'ancienne 1 est supprimée. |
| Palette inspirée de Nour Studio | Voir § 3. |
| Morph conservé sur la séquence produits | Morph sur les anciennes 13 à 18 (**nouvelles 12 à 17**) : position, échelle et rotation 3D inchangées. |
| Morph supprimé ailleurs | Aucune transition sur les 40 autres diapositives. |
| Règle d'apparition unique | Fondu + glissement de 20 px vers le haut, 0,5 s, ease-out. Titres automatiques, reste au clic (voir § 4). |
| Graphiques 44 et 45 | Refaits d'après tes images (voir § 5). Ce sont maintenant les **diapositives 43 et 44**. |

## 3. Couleurs : la logique Nour Studio appliquée à la charte Marin'Or

Retenu de la présentation de référence : la gestion des couleurs seulement. Ni sa structure, ni la place de ses logos, de ses textes ou de ses visuels.

| Principe (Nour Studio) | Équivalent Marin'Or | Codes |
|---|---|---|
| Une couleur de marque profonde, en aplat plein écran, pour les intercalaires et les messages forts | Bordeaux Profond | `#7B1421` (dégradé subtil `#8A1828` → `#68101C`) |
| Fond blanc pour les diapositives de contenu | Blanc Pureté | `#FFFFFF` |
| Cartes dans une teinte très claire de la couleur de marque | Rose Poudre | `#F6E8EA` |
| Titres dans la couleur de marque | Bordeaux Profond | `#7B1421` |
| Texte sombre teinté, plutôt que noir pur | Bordeaux très sombre (**dérivé**) | `#2A070D` |
| Texte secondaire neutre | Gris bordeaux (**dérivé**) | `#6E5A5D` |
| Un seul accent doré, utilisé avec parcimonie (grands chiffres sur fond foncé) | Or Épicé | `#F9A825` |
| Couleurs d'état ponctuelles | Vert Nature `#2A5519`, Rouge Passion `#A40C21` | Diapositive 42 (tests) |

- **Teinte dérivée** `#D9AEB5` : segments clairs des barres de la diapositive 43.
- **Polices** inchangées : Cream Heavy pour les titres et les chiffres, Montserrat pour le texte.
- **Contraste** : titre bordeaux sur blanc environ 10:1 ; texte `#2A070D` sur blanc environ 19:1 ; secondaire `#6E5A5D` sur blanc environ 6,4:1 ; or sur bordeaux environ 5,4:1. L'or n'est jamais posé sur fond blanc pour du texte.

## 4. Animations et transitions

- **Diapositives 12 à 17** (séquence produits) : transition Morph (1,6 à 2 s), objets 3D appariés par nom. Aucune animation d'apparition ajoutée, pour ne pas perturber le Morph.
- **Toutes les autres diapositives** : aucune transition. Une seule règle d'apparition :
  - **Effet** : fondu + glissement de 20 px vers le haut (effet PowerPoint « Flottant entrant » réglé à 20 px, soit 2,78 % de la hauteur d'une diapositive de 720 px).
  - **Durée** : 0,5 s. **Courbe** : ease-out (décélération 100 %).
  - **Déclenchement** : le **titre** apparaît automatiquement à l'ouverture de la diapositive (il en va de même pour le numéro des intercalaires et le logo de la dernière diapositive). Le reste apparaît **au clic**, par blocs logiques : une carte, une image ou un groupe de puces par clic.
  - **Total** : **73 clics** sur le deck. Le nombre par diapositive figure au § 7.
- **Graphiques** (seule exception, à ta demande) : un clic lance la construction, qui s'enchaîne ensuite toute seule (voir § 5).
- **Vidéos** (diapositives 26, 34, 35) : elles apparaissent avec la règle ; **cliquer sur la vidéo** pour la lancer.

## 5. Graphiques sur mesure

- **Diapositive 43, « 63 jours » (inspiration graph2)**
  - En-tête « chiffre clé » : **63 jours**, soit 9 semaines.
  - 4 barres horizontales aux bouts arrondis, découpées par tâche du Tableau 2, en alternance bordeaux et rose clair, comme les deux tons de graph2. Par exemple pour le site web : 10 + 4 + 4 + 3 + 3 + 4 = 28 jours.
  - Traits verticaux discrets = les semaines.
  - Animation : chaque barre se construit segment par segment, en balayage depuis la gauche (ease-out, durée proportionnelle aux jours). La valeur apparaît en fondu à la fin de la barre, puis la barre suivante démarre.
- **Diapositive 44, « 7 000 000 FCFA » (inspiration graph1)**
  - Camembert en « verre dépoli » (parts blanches semi-transparentes, séparées par des jours fins) posé sur un halo Rouge Passion vers Bordeaux, sur un panneau Rose Poudre (l'équivalent du fond gris de graph1).
  - Lignes de rappel vers des étiquettes alignées à droite : pourcentage, poste, montant.
  - Animation : le halo apparaît en fondu, chaque part se dessine en balayage circulaire (ease-out), puis chaque ligne de rappel et son étiquette.
  - ⚠️ Les **pourcentages** (50 / 34 / 9 / 7 %) et les **regroupements** « Spots 2D et 3D : 2 400 000 » et « Supports imprimés : 600 000 » sont **calculés** à partir du Tableau 3. Les montants détaillés sont dans les notes.

## 6. Contrôle qualité

| Vérification | Résultat |
|---|---|
| Nombre de diapositives | **46** (fourchette 45-47 respectée). |
| Limite de 6 lignes | Mesurée avec les vraies polices, repère de section compris. **0 diapositive au-dessus de 6.** |
| Validité du fichier (Open XML SDK 3.1) | **0 erreur** sur les deux fichiers. Les timelines d'animation sont validées par le SDK : le test avec une erreur volontaire la détecte bien. Les 90 modèles 3D, validés un par un : **0 erreur**. |
| Cibles d'animation | Toutes présentes sur leur diapositive ; aucun identifiant de timeline en double ; Morph présent **uniquement** sur 12 à 17. |
| Chiffres | Tous présents dans le mémoire, sauf les valeurs calculées signalées au § 5. |
| Rendu | Les 46 diapositives ont été rendues et relues (LibreOffice, sans 3D ni animations). |

**Non testé ici** : le rendu réel des animations et des modèles 3D dans PowerPoint. LibreOffice n'affiche ni l'un ni l'autre. **Teste le deck sur la machine de soutenance** (voir § 8).

## 7. Durée et déroulé par diapositive

Total **14 min 19 s**. Les durées figurent aussi au début des notes de l'orateur, entre crochets.

| N° | Diapositive | Déclenchement | Durée | Cumul |
|---|---|---|---|---|
| 1 | Conception et réalisation de supports de commu | 1 clic(s) | 25 s | 0:25 |
| 2 | Plan de la présentation | 1 clic(s) | 15 s | 0:40 |
| 3 | Contexte | 1 clic(s) | 20 s | 1:00 |
| 4 | Marin'Or Ivoire | 1 clic(s) | 20 s | 1:20 |
| 5 | Constats de l'existant | 4 clic(s) | 25 s | 1:45 |
| 6 | Comment concevoir et réaliser des supports de  | auto | 25 s | 2:10 |
| 7 | Hypothèse | 2 clic(s) | 20 s | 2:30 |
| 8 | Méthodologie qualitative | 4 clic(s) | 25 s | 2:55 |
| 9 | Objectifs | 2 clic(s) | 20 s | 3:15 |
| 10 | Public cible | 2 clic(s) | 20 s | 3:35 |
| 11 | Trois axes de communication | 3 clic(s) | 20 s | 3:55 |
| 12 | Présentation des produits | Morph 3D | 10 s | 4:05 |
| 13 | 15 produits, 3 familles | Morph 3D | 20 s | 4:25 |
| 14 | Les Marinades | Morph 3D | 18 s | 4:43 |
| 15 | Les Épices | Morph 3D | 18 s | 5:01 |
| 16 | Les Essentiels | Morph 3D | 14 s | 5:15 |
| 17 | Le vrai goût de chez nous | Morph 3D | 15 s | 5:30 |
| 18 | Identité visuelle et charte graphique | auto | 8 s | 5:38 |
| 19 | Trois pistes explorées | 3 clic(s) | 22 s | 6:00 |
| 20 | Le logo retenu | 2 clic(s) | 25 s | 6:25 |
| 21 | Zone de protection et déclinaisons | 2 clic(s) | 15 s | 6:40 |
| 22 | Les interdits | 1 clic(s) | 10 s | 6:50 |
| 23 | Typographie | 3 clic(s) | 18 s | 7:08 |
| 24 | Colorimétrie | 2 clic(s) | 18 s | 7:26 |
| 25 | Mise en application | 2 clic(s) | 15 s | 7:41 |
| 26 | Animation du logotype | 1 clic(s) | 12 s | 7:53 |
| 27 | Supports print et audiovisuels | auto | 8 s | 8:01 |
| 28 | Le vrai goût de chez nous | 2 clic(s) | 18 s | 8:19 |
| 29 | Le goût qui rassemble | 2 clic(s) | 15 s | 8:34 |
| 30 | Marinez, Cuisez, Régalez-vous | 2 clic(s) | 15 s | 8:49 |
| 31 | Dépliant trois volets | 3 clic(s) | 20 s | 9:09 |
| 32 | Marinez, Cuisez, Régalez-vous ! | 2 clic(s) | 15 s | 9:24 |
| 33 | Le goût qui rassemble ! | 2 clic(s) | 15 s | 9:39 |
| 34 | Spot 2D | 1 clic(s) | 25 s | 10:04 |
| 35 | Spot 3D | 1 clic(s) | 25 s | 10:29 |
| 36 | Le site web : une boutique en ligne | auto | 8 s | 10:37 |
| 37 | Structure de navigation | 2 clic(s) | 20 s | 10:57 |
| 38 | Accueil et gammes | 2 clic(s) | 20 s | 11:17 |
| 39 | Commander et payer | 3 clic(s) | 25 s | 11:42 |
| 40 | Le back-office | 2 clic(s) | 18 s | 12:00 |
| 41 | Base de données | 3 clic(s) | 20 s | 12:20 |
| 42 | Tests fonctionnels | 4 clic(s) | 25 s | 12:45 |
| 43 | 63 jours   soit 9 semaines de réalisation | 1 clic(s) | 22 s | 13:07 |
| 44 | Coût estimatif : 7 000 000 FCFA | 1 clic(s) | 22 s | 13:29 |
| 45 | Conclusion | 2 clic(s) | 35 s | 14:04 |
| 46 | Merci de votre attention | 1 clic(s) | 15 s | 14:19 |

## 8. Liste de vérifications avant la soutenance

1. **Machine de soutenance**
   - PowerPoint 2019, 2021 ou 365. Sinon, la version SECOURS : le Morph devient un fondu et les effets d'apparition fonctionnent quand même.
   - Lance le diaporama depuis la diapositive 11 jusqu'à la 18 : Morph 3D fluide, produits à la bonne taille.
   - Si la taille d'un produit est fausse, utilise la version SECOURS.
2. **Animations**
   - Fais une répétition complète en comptant les clics (73).
   - Sur les diapositives 43 et 44, un seul clic lance tout le graphique : attends la fin de la construction (environ 4 s) avant de cliquer à nouveau.
3. **Vidéos** (26, 34, 35) : clic sur la vidéo ; vérifie le son.
4. **Polices** : installe **Cream Heavy** et **Montserrat**, ou enregistre le fichier avec les polices incorporées (*Fichier › Options › Enregistrer*).
5. **Chiffres et incohérences à recontrôler** (inchangés depuis la v1)
   - Spot 2D : 41 s réels contre 60 s dans le mémoire ; « 12 » contre « 15 » produits p. 50.
   - Film 3D : 1 min 31 s contre 40 à 60 s.
   - Logo animé : 5 s / 60 ips contre 7 s / 29,97 ips.
   - Tests 10 et 11 encore « [À vérifier] » ; test 17 non conforme alors que la p. 68 annonce l'adaptation smartphone.
   - Figures 48, 51 et 54 identiques dans le Word.
   - `marinorivoire.ci` contre `.com`.
   - Purée d'ail et huile rouge : conditionnement du Tableau 1 différent des modèles 3D.
   - Dépliant à 13 produits.
   - Phrase méthodologique (diapositive 8) absente du mémoire.
   - Hypothèse non conclue explicitement.
   - Prix visibles sur les captures du site.
6. **Valeurs calculées** de la diapositive 44 (pourcentages, regroupements) : sois prêt à les justifier.
