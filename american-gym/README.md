# Affiche American's Gym — suppression du bloc vert

| Fichier | Contenu |
|---|---|
| `american_gym_retouche.png` | Image finale sans perte (1080 × 720) |
| `american_gym_retouche.jpg` | Image finale JPEG qualité 97 |
| `american_gym_retouche.psd` | Fichier Photoshop multi-calques (RVB 8 bits) |
| `avant_apres_zoom.png` | Comparaison avant / après de la zone traitée |
| `affiche_originale.webp` | Affiche source |

## Calques du PSD (du haut vers le bas)

- **Affiche finale aplatie (référence)** — masqué, pour comparer.
- **03 — Éléments graphiques (calques isolés)** — logo, 3 lignes de titre, pictos,
  slogan, bandeau contacts, signature rouge. Chaque calque a un **masque de fusion**
  modifiable (détourage du texte / des formes). On peut y ajouter des styles de calque
  (incrustation de couleur, ombre portée…), des réglages écrêtés, etc.
- **02 — Retouche gazon** — « Gazon reconstitué » + son masque de fusion (bord adouci) ;
  « Repère — zone retouchée » (masqué) montre la zone traitée en rouge.
- **01 — Affiche d'origine** — affiche source intacte, verrouillée.

Le rendu de l'ensemble est identique à `american_gym_retouche.png`.

## Régénérer

```bash
pip install numpy pillow scipy opencv-python-headless psd-tools
python3 retouche_gazon.py affiche_originale.webp .
python3 build_psd.py affiche_originale.webp . american_gym_retouche.psd
```
