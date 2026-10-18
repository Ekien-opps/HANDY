# Lower thirds Marin'Or Ivoire

Style inspiré du pack « Lower Thirds Library – Clean Edition » : ligne d'accent, volets obliques en cascade
(or puis ivoire), titre et sous-titre révélés à l'intérieur des volets, sortie en ordre inverse.

- Charte : ivoire `#FFF6E8` (bloc titre), or Marin'Or `#F9A825` (accent, sous-titre), texte noir `#161616`.
- Police : Montserrat Bold / SemiBold (licence SIL OFL), à placer dans `fonts/`
  (https://github.com/JulietaUla/Montserrat).
- Sortie : ProRes 4444 avec canal alpha, 1920 × 1080, 24 i/s.

```
python lower_thirds.py out                     # 12 clips, rangés par ensemble
python piste_et_apercu.py piste.mov apercu.mp4 # piste complète de 1:25 + aperçu H.264
```

Textes, temps de début et durées : liste `SERIE` en tête de `lower_thirds.py`.
