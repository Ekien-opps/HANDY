# Rendu final : VISUEL_INVITE

`final.html` contient l'animation (mêmes timings et courbes que le guide After Effects).
Les fonds `hd_*.png` ont été reconstruits en haute définition à partir des réglages du PSD :
masques, Luminosité/Contraste (+11 / +31 à 63 %, appliqué à travers son masque) et assombrissement.

La police **Cream Heavy** n'est pas versionnée (police commerciale). Pour relancer le rendu,
place `Cream-Heavy.ttf` dans `assets/`, puis lance :

    node ../render-final.js . final.html master.mkv 30 2 1920 1040 8

Paramètres : 30 i/s, suréchantillonnage ×2, sortie 1920 × 1040, 8 sous-images de flou de bougé.
