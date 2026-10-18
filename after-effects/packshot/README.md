# Packshot Marin'Or Ivoire : animation bas → haut, sans fond

- `MarinOr_Packshot_Anim.jsx` : dans After Effects, **Fichier > Scripts > Exécuter le fichier de script...**. Le script crée une compo 1920×1080, 60 i/s, 3 s, sans fond. Il l'ajoute aussi à la file de rendu avec un module de sortie qui garde l'alpha (« High Quality with Alpha »).
- `packshot_alpha.webm` : vidéo à fond transparent (VP9 + alpha), prête pour le web.
- `packshot_apercu_fond_creme.mp4` : simple aperçu sur fond crème, **sans** transparence.

Positions, durées et ordre de la cascade se règlent dans les blocs `LAYOUT` et `TIMING` du script.
