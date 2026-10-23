# Dépliant 3 volets American's Gym — fichiers pour Illustrator

Format : A4 à l'italienne (297 × 210 mm), pli roulé en 3 volets, recto et verso.
- Extérieur : rabat (97 mm) · dos (100 mm) · couverture (100 mm)
- Intérieur : à propos (100 mm) · services (100 mm) · formules (97 mm, volet replié)

## Fichiers

| Fichier | Usage |
|---|---|
| `american_gym_depliant_exterieur.svg` | **À ouvrir dans Illustrator** : extérieur, textes modifiables |
| `american_gym_depliant_interieur.svg` | **À ouvrir dans Illustrator** : intérieur, textes modifiables |
| `american_gym_depliant_impression.pdf` | PDF 2 pages avec 3 mm de fond perdu, polices incorporées |
| `apercu_exterieur.png`, `apercu_interieur.png` | Aperçus |
| `images/` | Photos et logo (à remplacer par des versions HD) |
| `../fonts/` | Polices Montserrat utilisées |

## Ouverture dans Illustrator

1. **Installer d'abord les polices Montserrat** : celles du dossier `fonts/`,
   ou mieux, la famille complète via Adobe Fonts (gratuite avec Creative Cloud).
   Sinon, Illustrator remplace la police à l'ouverture.
2. Fichier › Ouvrir › choisir le `.svg`. Le plan de travail fait 297 × 210 mm.
   Les fonds dépassent de 3 mm pour le fond perdu.
3. Chaque volet est un groupe nommé (`Volet_A_rabat`, `Volet_C_couverture`…),
   et chaque élément un sous-groupe (`C_accroche`, `B_contact`…).
   Tous les textes sont du vrai texte modifiable, et toutes les formes sont vectorielles.
4. Supprimer le groupe `REPERES_pliage_a_masquer` (lignes bleues des plis) avant impression,
   ou le transformer en repères (Affichage › Repères › Créer des repères).
5. Fichier › Enregistrer sous › Adobe Illustrator (.ai).
6. Pour l'imprimeur : Fichier › Mode colorimétrique du document › CMJN, puis
   exporter en PDF avec fond perdu de 3 mm.

## À compléter avant impression

- Horaires d'ouverture (`__h__ – __h__`)
- Tarifs des formules (`____ FCFA`)
- Adresse précise (actuellement « Abobo, Abidjan — Côte d'Ivoire »)
- Photos en haute définition : les visuels actuels viennent des affiches
  (environ 75 à 100 dpi à la taille du dépliant), alors que l'impression demande 300 dpi.
  Remplacer via le panneau Liens d'Illustrator (Remplacer).

## Régénérer

```bash
python3 generer_depliant.py
NODE_PATH=$(npm root -g) node rendu.js
```
