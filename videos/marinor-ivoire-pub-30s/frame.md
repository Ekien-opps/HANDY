---
version: 1
name: Marin'Or Ivoire — Frame (video / frame layer)
description: >
  Charte vidéo de Marin'Or Ivoire pour la pub 30 s (1920×1080). Atomes sacrés : la palette client à 10 couleurs,
  Cream Heavy (titres) + Montserrat 500/600/700 (texte), le badge ovale bordeaux à liseré blanc du logo, le trait
  d'or (dégradé Or Épicé → Jaune Soleil de la feuille du logo). Composition libre, cadrée pour la vidéo.
unit: the frame — 1920×1080
principle: atoms are sacred · composition is free · copy comes from the brief

colors:
  noir: "#000000"           # Noir Intense — textes, contraste
  blanc: "#FFFFFF"          # Blanc Pureté — respiration, liseré du badge
  vert-nature: "#2a5519"    # fraîcheur, naturalité — fond du chapitre terroir
  vert-vif: "#376f23"       # vitalité — lueurs / accents du chapitre terroir
  bordeaux: "#7B1421"       # COULEUR PRINCIPALE — badge logo, fonds premium
  rouge-passion: "#A40C21"  # cœur du dégradé radial du badge, intensité des saveurs
  rose-poudre: "#F6E8EA"    # fonds doux, élégance
  or-epice: "#F9A825"       # accent chaleureux — début du trait d'or
  jaune-soleil: "#FBD021"   # luminosité — fin du trait d'or
  creme: "#FFECD1"          # Crème Douce — toile de base claire, respiration

gradients:
  badge: "radial-gradient(circle at 50% 50%, #A40C21 0%, #7B1421 100%)"   # exact logo badge fill
  trait-or: "linear-gradient(90deg, #F9A825 0%, #FBD021 85%)"             # exact logo leaf fill

typography:
  display-hero: { fontFamily: "Cream Heavy", px: 132, weight: 900, lineHeight: 0.98, tracking: "-0.005em" }
  display:      { fontFamily: "Cream Heavy", px: 96,  weight: 900, lineHeight: 1.0 }
  headline:     { fontFamily: "Cream Heavy", px: 72,  weight: 900, lineHeight: 1.04 }
  sub:          { fontFamily: "Montserrat", px: 44, weight: 600, lineHeight: 1.2 }
  body:         { fontFamily: "Montserrat", px: 34, weight: 500, lineHeight: 1.3 }
  label:        { fontFamily: "Montserrat", px: 26, weight: 700, tracking: "0.16em", upper: true }
  chip:         { fontFamily: "Montserrat", px: 30, weight: 700, tracking: "0.04em" }
  contact:      { fontFamily: "Montserrat", px: 30, weight: 600 }

fonts:
  "Cream Heavy": "assets/fonts/Cream-Heavy.ttf"
  "Montserrat": "assets/fonts/Montserrat-latin.woff2 + Montserrat-latin-ext.woff2 (variable 100–900)"
  "RadioTime Tooled": "EXCLUSIVE au logo — jamais utilisée en texte ; le logo est toujours le SVG fourni"

spacing:
  safe-x: "120px"
  safe-y: "90px"
  rule: "4px"
  badge-stroke: "8px"   # liseré blanc intérieur du badge (15/1276 de la largeur du logo, mis à l'échelle)
  radius-chip: "999px"

components:
  logo:
    source: "assets/brand/logo-anim.svg (calques : Calque_1 badge+liseré, Calque_3 lettrage, Calque_2 éléphant+feuille)"
    rule: "jamais recoloré, jamais déformé ; animé calque par calque uniquement"
  badge-oval:
    fill: "{gradients.badge}"
    stroke: "{spacing.badge-stroke} {colors.blanc}, inset"
    description: "écho du logo — cadre premium pour titres et packshots"
  chip:
    backgroundColor: "{colors.bordeaux} (texte blanc) / {colors.creme} (texte bordeaux)"
    rounded: "{spacing.radius-chip}"
    typography: "{typography.chip}"
  stamp-naturel:
    shape: "cercle 220px, double anneau"
    colors: "{colors.vert-nature} + texte {colors.blanc}"
    text: "100 % NATUREL"
    description: "écho du badge « 100% NATUREL » des sachets"
  trait-or:
    fill: "{gradients.trait-or}"
    description: "LE fil conducteur — poussière d'épices / trait doré qui relie chaque séquence"
  packshot:
    source: "assets/products/<id>.png (@2x pour les gros plans) — détourés depuis la planche client"
    shadow: "ombre portée douce au sol, rgba(42,8,14,0.35), blur 30px"
    rule: "jamais recolorés, jamais déformés (scale uniforme seulement)"

do:
  - Toile claire Crème Douce par défaut (food = clair) ; Bordeaux pour les moments premium (gamme, logo).
  - Une couleur d'accent par plan : l'or. Le reste de la palette sert les chapitres (vert = terroir).
  - Titres Cream Heavy en Bordeaux sur crème, en Blanc / Jaune Soleil sur Bordeaux ou Vert.
  - Le trait d'or apparaît dans chaque séquence.
dont:
  - Pas de RadioTime Tooled hors logo.
  - Pas de texte en dégradé, sauf UNE fois : le reflet doré (shimmer) sur « le goût en or ».
  - Pas de gris neutre : ombres et neutres teintés bordeaux.
  - Pas de dégradé linéaire plein écran sur fond sombre (banding) — radial uniquement.
  - Aucune image générée par IA ; aucun faux produit : seuls les 15 packshots réels.
---

## Overview

Premium, chaleureux, gourmand, authentique. Le badge ovale bordeaux du logo est la forme-mère ; le trait d'or (la feuille
du logo) est le geste-mère. Les icônes et le décor culinaire sont des illustrations vectorielles 2,5D (dégradés,
reflets spéculaires, ombres teintées) construites en SVG/CSS — jamais de photo de stock.

## Chapitres colorés

| Séquence | Monde | Fond |
|---|---|---|
| 01 Accroche | cuisine claire | Crème Douce + lueur radiale Or 18 % |
| 02 Le doute | nuit inquiète | Bordeaux assombri vers le noir (radial #7B1421 → #2a070d) |
| 03 Le feu | chaleur | Crème → braises Rouge Passion / Or |
| 04 Le terroir | nature | Vert Nature + lueur Vert Vif |
| 05 La gamme | premium | Badge radial Rouge Passion → Bordeaux |
| 06 Le partage | convivial | Crème Douce / Rose Poudre |
| 07 Le goût en or | signature | Badge radial Rouge Passion → Bordeaux |
