# Soutenance American's Gym : choix et vérifications

Fichiers :
- `Soutenance_American_Gym.pptx` : version principale, 16:9, 40 diapositives, 15 Mo avec les deux vidéos intégrées.
- `Soutenance_American_Gym_sans_videos.pptx` : version de secours de 5,6 Mo. Les vidéos y sont remplacées par une image ; les fichiers vidéo sont dans le dossier `videos/`.

### Correctif d'ouverture

Certaines personnes n'arrivaient pas à ouvrir le fichier. Trois défauts de la première version, venant de l'outil de génération, ont été corrigés :
- identifiants de formes en double sur les diapositives 15, 31 et 32 ;
- 39 déclarations de parties inexistantes (`slideMaster2…40`) dans `[Content_Types].xml` ;
- entrées de dossiers dans le zip et type d'image non standard (`image/jpg`).

Le fichier est maintenant contrôlé par `outils/diag_pptx.py` (0 problème) et par le validateur de schéma. Si l'ouverture échoue encore sur un appareil précis (téléphone, Google Slides, PowerPoint 2007 ou plus ancien), utiliser la version sans vidéos.

## 1. Choix de conception

### Couleurs

Les couleurs viennent de la charte du mémoire (p. 27) :

| Rôle | Couleur | Origine |
|---|---|---|
| Couleur dominante : fonds des diapositives de titre, de section et de fin, titres | Bleu marine `#1D3557` | Charte |
| Accent, utilisé avec parcimonie : numéros, surtitres, étape finale, mots-clés | Rouge `#E63946` | Charte |
| Fond des diapositives de contenu | Blanc `#FFFFFF` | Charte |
| Accent sur fond bleu (problématique, surtitres) | Gris métal `#A8DADC` | Charte |
| Fond des cartes | `#EEF2F6` | Nuance neutre dérivée du bleu, hors charte |
| Texte courant | `#2B3A4F` | Nuance neutre dérivée du bleu, hors charte |
| Légendes | `#6B7A90` | Nuance neutre dérivée du bleu, hors charte |

### Polices

- **Poppins ExtraBold** pour les titres. C'est la « police d'accompagnement » de la charte (p. 24).
- **Poppins** pour le texte.
- **Impact** apparaît seulement dans l'exemple « Aa » de la diapositive Typographie (police du logo).

### Mise en page et contenu

- **Une idée par diapositive**, 6 lignes de texte au maximum.
- **Décor réduit** : pas de formes décoratives, seulement des cartes à fond clair, des icônes et le logo.
- **Visuels** : ils viennent du mémoire (logo, goodies, site web, 3D, captures) et de `travaux.zip` (affiches, flyer, dépliant, kakémono, visuel réseaux sociaux, vidéos).
- **Notes de l'orateur** : chaque diapositive a une note tirée du mémoire, visible en mode Présentateur.

### Animations : une seule règle pour tout le deck

- **Effet** : fondu et glissement de 20 px vers le haut, en 0,5 s, avec une fin adoucie (« ease-out », décélération 100 %).
- **Titres** (surtitre, titre, numéro de section) : ils apparaissent automatiquement à l'arrivée de la diapositive.
- **Contenu** : il apparaît au clic, un clic par bloc. Le nombre de clics par diapositive va de 0 à 5.
- **Diapositives vidéo (31 et 32)** : le 1er clic affiche la fiche technique, le 2e affiche la vidéo, qui démarre ensuite toute seule.
- **Compatibilité** : les effets utilisés sont « Fondu » et une « Trajectoire personnalisée », tous deux disponibles dans PowerPoint 2019.

### Changements par rapport au modèle Nova X

Le modèle a servi uniquement de référence pour la structure et la densité. Je n'ai repris ni ses couleurs, ni ses contenus, ni son logo.

- **Repris** : la logique du déroulé (titre, plan, introduction, problématique, objectifs, structure, charte graphique, supports avec mise en situation, spots, site, outils, coût, conclusion, remerciements).
- **Fusionné** : « Bienvenue » et la page de garde en une seule diapositive de titre. Chaque support (visuel + mise en situation) tient sur une diapositive, d'où 40 diapositives au lieu de 50.
- **Remplacé** : les cercles d'icônes servant de séparateurs deviennent 5 séparateurs numérotés 01 à 05, alignés sur le plan du mémoire.
- **Ajouté (présent dans le mémoire)** : hypothèse, critique de l'existant, cibles, planning sur 8 semaines, règles d'utilisation du logo, recommandations.
- **Retiré (absent de ce mémoire ou sans support)** : calendrier, démonstration en direct, langages PHP et MySQL.

### Formulations condensées

Pour tenir dans 6 lignes, certains textes du mémoire ont été raccourcis sans en changer le sens :
- les objectifs ;
- l'hypothèse ;
- les critiques de l'existant ;
- les verbes associés aux cibles (« Fidéliser / Attirer / Collaborer »).

Les formulations complètes sont dans les notes de l'orateur.

## 2. Chiffres et noms signalés

Je n'ai modifié aucun chiffre ni aucun nom sans le signaler ici.

| Point | Dans le mémoire | Dans le deck |
|---|---|---|
| **Coût total** (p. 54) | Total annoncé : 4 800 000 FCFA. Mais la somme de la colonne Total donne **4 300 000 FCFA**. Les quantités (3 affiches × 600 000, 6 gadgets × 300 000) ne sont pas appliquées dans le sous-total de 1 050 000. | **4 800 000 FCFA** affiché tel quel, sans montant par poste. **À corriger dans le mémoire et dans le deck avant la soutenance.** |
| **Boutique en ligne** (p. 10) | « plateforme Spotify » | **Shopify**, comme le confirme le lien cité p. 11. Coquille du mémoire. |
| **Abonnés TikTok** (p. 10) | « plus de 5 4140 abonnés » (la capture montre 5 414) | Chiffre non affiché. Seules les 27 900 mentions « J'aime » le sont. |
| **Durée du spot 2D** (p. 38-39) | 25 s dans la fiche technique, 30 s au § III.3. La vidéo fournie dure 26 s. | Durée non affichée. |
| **Slogan** (p. 33 et 37) | « au **service** de votre bien-être » | Les visuels et la voix off disent « au **cœur** de votre bien-être ». Le deck ne cite pas le slogan à l'écran. |
| **Format des affiches** (p. 32-33 et 56) | 4 m × 3 m en conception, document de 297 × 210 mm en réalisation | Format non affiché. |
| **Encadrement** | Couverture : « CHAFICK ADJIBADÉ » sans titre. Remerciements : « M. Chafick ADJIBADÉ ». | « M. Chafick ADJIBADÉ » et « Prof. TOA AGNINI Jules Évariste ». Vérifier les titres exacts. |
| **Gris métal `#A8DADC`** | Code donné par la charte | Affiché tel quel. Ce code donne en réalité un bleu-vert pâle, pas un gris : le jury peut le relever. |

## 3. À vérifier avant la soutenance

1. **Installer Poppins** (Regular et ExtraBold, gratuites sur Google Fonts) sur l'ordinateur de soutenance. Sinon, incorporer les polices : *Fichier > Options > Enregistrement > Incorporer les polices dans le fichier*, depuis un PC où Poppins est installé. Sans cela, PowerPoint remplace la police et des textes peuvent déborder.
2. **Corriger le budget** : choisir 4 300 000 ou 4 800 000 FCFA, puis aligner le mémoire et la diapositive 23.
3. **Lancer le diaporama en entier dans PowerPoint 2019** : animations, ordre des clics et lecture des deux vidéos avec le son. L'aperçu utilisé pour mes contrôles ne joue pas les animations.
4. **Vidéos** : elles ont été ré-encodées en H.264 1080p pour alléger le fichier (le spot 2D passe de 45 Mo à 8,6 Mo). Garder les originaux de `travaux.zip` en secours.
5. **Spot 3D** : aucune vidéo dans `travaux.zip`, la diapositive 33 montre seulement le rendu du bâtiment. Ajouter la vidéo si elle existe (*Insertion > Vidéo*).
6. **Qualité des images** : le logo (414 px, extrait du PDF) et les goodies sont en basse définition. Remplacer par les fichiers sources (PNG haute définition ou SVG) pour la projection.
7. **Durée** : 40 diapositives représentent environ 20 minutes. Vérifier le temps accordé et répéter avec les notes de l'orateur.
8. **Projecteur** : vérifier le format 16:9 et la lisibilité du rouge sur fond bleu.
9. **Plan B** : copier le fichier sur clé USB, avec un export PDF (sans vidéos ni animations) et les vidéos séparées.
10. **Cohérence avec le mémoire** : une fois les corrections faites dans le mémoire (coquilles, budget, durées), repasser sur les diapositives concernées (11, 23, 31-33).
