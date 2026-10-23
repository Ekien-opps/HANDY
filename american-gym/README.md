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

---

# Affiche v2 — pictos descendus aux chevilles

Les pictos Sport / Santé / Bien-être (textes et séparateurs rouges compris) sont
descendus au niveau des chevilles de la sportive (centre des cercles à y = 530)
et agrandis à 115 %. L'axe horizontal du bloc est conservé. Le fond qu'ils
occupaient (zone sombre et gazon) est reconstitué. Aucun autre pixel n'est
modifié : seule la zone x 50–398 / y 410–584 change.

| Fichier | Contenu |
|---|---|
| `american_gym_v2_pictos_chevilles.png` / `.jpg` | Image finale |
| `american_gym_v2_pictos_chevilles.psd` | PSD multi-calques |
| `avant_apres_v2_pictos.png` | Comparaison avant / après |
| `affiche_v2.webp` | Affiche source v2 |

Calques du PSD (de haut en bas) : « Affiche finale aplatie » (masqué) ;
**03 — Pictos** : 5 calques réellement détourés (Sport, Santé, Bien-être et
2 séparateurs) qu'on peut déplacer, redimensionner ou styliser, le fond derrière
étant propre ; **02 — Fond reconstitué** (avec masque de fusion) ;
**01 — Affiche d'origine** (verrouillée).

```bash
python3 deplacer_pictos.py affiche_v2.webp .
python3 build_psd_v2.py affiche_v2.webp . american_gym_v2_pictos_chevilles.psd
```
