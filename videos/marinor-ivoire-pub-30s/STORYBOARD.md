---
format: 1920x1080
duration: 30s
message: "Les saveurs authentiques de Côte d'Ivoire, 100 % naturelles, pour relever simplement tous vos plats — Marin'Or Ivoire, le goût en or."
arc: Question (accroche) → Doute (problème) → Promesse (le feu) → Preuve (terroir) → Révélation (la gamme) → Usage & partage → Signature + CTA
audience: Décideurs de grandes entreprises (pièce portfolio) — cible finale : foyers ivoiriens qui cuisinent
mode: collaborative
version: 2
---

# Marin'Or Ivoire — « Le goût en or » · storyboard v2 (plan validé, minutage voix réel)

## Décisions

- **Message :** Les saveurs authentiques de Côte d'Ivoire, 100 % naturelles, relèvent simplement tous vos plats.
- **Public & arc :** des décideurs qui jugent un savoir-faire ; arc en 7 temps (scénario client condensé) : question → doute → promesse → preuve → révélation → partage → signature.
- **Format :** 1920×1080, 30,0 s, voix off FR (Kokoro « ff_siwis », vitesse 1.08, 7 fichiers `assets/audio/vo/vo-0N.wav`), musique + sound design. Pas de sous-titres.
- **Le fil conducteur (spine) : « le trait d'or ».** Traînée de poussière d'épices dorée (dégradé exact de la feuille du logo #F9A825 → #FBD021) présente dans chaque séquence, qui dessine enfin la feuille dorée du logo (07).
- **Objet-héros & rappel :** le **plat dressé** (attiéké, poisson braisé, alloco, piment) — 03 → centre de la table en 06 → son assiette devient le badge du logo en 07.
- **Marque :** `frame.md` (palette, polices, illustration 2,5D, notes de production, raccords).
- **Rythme :** rapide → tendu → travelling chaud → éclosion → flash → construction-héros → doux → signature + **plan tenu** (28,9–30,0 s). Direction unique : vers la gauche.
- **Interdits :** aucune image/vidéo IA ; aucune photo de stock ; aucun faux produit ; pas de RadioTime Tooled hors logo ; pas de texte en dégradé sauf le reflet sur « Le goût en or » ; pas de glitch ; ni diaporama ni économiseur d'écran.
- **Placement voix (global) :** vo-01 @0,45 · vo-02 @4,35 · vo-03 @8,30 · vo-04 @12,15 · vo-05 @16,45 · vo-06 @22,70 · vo-07 @27,05.
- **Raccords :** A (4,0 s) aplat #2a070d · B (8,0 s) aplat or · C (12,0 s) aplat crème #FFECD1 · D (16,0 s) lumière #FFF3D6 · E (22,5 s) zoom pot Marinade Poisson + crème · F (26,5 s) aplat #7B1421.

## Frame 1 — Accroche « La pincée d'or » (0,0–4,0 s, ~4,0 s)

- scene: Ballet d'icônes culinaires 2,5D autour de la question « Envie de relever le goût de vos plats du quotidien ? »
- duration: 4s
- poster: 3.0s
- transition_in: cut
- status: animated
- src: compositions/01-accroche.html
- voiceover: "Envie de relever le goût de vos plats du quotidien ?"
- vo_cues_local: voix 0,45–3,01 · « relever le goût » 0,75–1,30 · « plats du quotidien » 2,00–2,90
- blueprint: kinetic-type-beats
- rules: spring-pop-entrance, orbit-3d-entry
- focal: la question en Cream Heavy (centre) ; secondaire : l'anneau d'icônes
- audio_cue: pluck de balafon par icône ; « ffft » de pincée à 1,1 s

**Monde.** Une cuisine baignée de lumière douce, de l'énergie, de l'appétit. Toile Crème Douce #FFECD1, grande lueur radiale Or Épicé (≈20 %) derrière le texte, grain léger, quelques grains d'épices dorés qui flottent (8–12 points, dérive lente).

**Séquence (temps locaux) :**
- Scene 1 (0,00–0,90 s) : huit icônes 2,5D (piment rouge, gousse d'ail, feuille de laurier, grains de poivre, oignon rouge, cuillère en bois, mortier & pilon, petite marmite) **jaillissent** (spring-pop, back.out, stagger 0,06 s) depuis le centre vers un anneau elliptique (rayon ≈ 720×330 px) ; première icône visible à 0,10 s. Taille ≈ 150–190 px.
- Scene 2 (0,45–3,00 s) : la question se **construit mot à mot** sur la voix, Cream Heavy bordeaux #7B1421, 2 lignes centrées, ~104 px : « Envie de relever le goût » / « de vos plats du quotidien ? ». Mots en `back.out(1.6)` 0,40 s (y 40→0, scale .9→1, opacity). Les mots « relever le goût » apparaissent EN OR (#F9A825) à 0,75–1,30 s ; sous eux, le **trait d'or se dessine** gauche→droite (chemin SVG pinceau, stroke dégradé or, épaisseur 10–14 px, strokeDashoffset 0,45 s) et lâche une petite **pincée** de poussière dorée (10–16 particules déterministes qui retombent).
- Scene 3 (0,90–3,50 s) : l'anneau d'icônes **orbite** lentement en 3D (orbit-3d-entry : ellipse, profondeur translateZ, sine.inOut), chaque icône respire (scale ±3 %).
- Scene 4 — raccord A (3,50–4,00 s) : les icônes sont **aspirées** vers le point du « ? » (scale→0.2, power3.in) ; depuis ce point, un **iris** circulaire #2a070d s'ouvre (clip-path circle 0→2300 px, power2.in) et **couvre tout le cadre à 3,95 s**. ÉTAT DE SORTIE : plein cadre #2a070d.

**Contrainte.** Pas d'icônes clipart plates : volume, reflet, ombre teintée (voir frame.md). **Pourquoi.** Accroche en langage du bénéfice.

## Frame 2 — Le doute (4,0–8,0 s, ~4,0 s)

- scene: Contenants industriels anonymes « Additifs », « Exhausteurs artificiels », « Conservateurs », rayés par le trait d'or et réduits en poussière dorée
- duration: 4s
- poster: 2.6s
- transition_in: cut (raccord A)
- status: animated
- src: compositions/02-doute.html
- voiceover: "Sans additifs ni substances douteuses pour votre santé ?"
- vo_cues_local: voix 0,35–3,38 · « Sans additifs » 0,35–1,14 · « substances douteuses » 1,27–2,40 · « votre santé » 2,60–3,26
- blueprint: compose
- rules: spring-pop-entrance, css-marker-patterns, particle-burst
- focal: le trio de contenants (centre-bas) ; secondaire : la question (haut)
- audio_cue: battement grave à 0,4 s ; pulsation d'alerte ; « swish » à 2,55 s ; effritement à 2,75 s

**Monde.** Un doute qui s'installe, nuit d'inquiétude — sans tomber dans la peur. Fond radial Bordeaux #7B1421 (centre) → #2a070d (bords), vignette, halo rouge #A40C21 qui pulse lentement derrière les contenants.

**Séquence (temps locaux) :**
- Scene 1 — entrée raccord A (0,00–0,35 s) : ÉTAT D'ENTRÉE plein cadre #2a070d (overlay opacity 1) qui s'efface (opacity 1→0, power1.out).
- Scene 2 (0,30–1,20 s) : trois contenants génériques SANS marque (un cube de bouillon emballé façon papier aluminium, un flacon en plastique, un pot à couvercle) **tombent** en rang au centre-bas (y −700→0, rebond back.out, stagger 0,12 s), chacun avec une étiquette blanche Montserrat 700 bordeaux : « Additifs », « Exhausteurs artificiels », « Conservateurs ». Taille contenants ≈ 260–320 px de haut, espacés de 420 px.
- Scene 3 (0,35–3,30 s) : texte en haut (y ≈ 200), Montserrat 700 blanc 64 px sur 2 lignes : « Sans additifs ni substances douteuses » / « pour votre santé ? » — révélé par groupes de mots sur la voix (« Sans additifs » 0,35 ; « ni substances douteuses » 1,27 ; « pour votre santé ? » 2,60), « votre santé » en Jaune Soleil #FBD021. Le halo d'alerte pulse 2× (0,9 s et 1,9 s).
- Scene 4 (2,50–2,95 s) : le **trait d'or** (pinceau doré épais 18 px, dégradé or) **raye d'un seul geste vers la gauche** les trois étiquettes (css-marker strike, power3.inOut 0,40 s).
- Scene 5 (2,75–3,45 s) : les contenants **s'effritent** en poussière (particle-burst déterministe, 40–60 particules par contenant, couleurs bordeaux/brun qui virent à l'or en retombant), les contenants scale→0 + opacity.
- Scene 6 — raccord B (3,45–4,00 s) : le trait d'or s'**épaissit** en bande diagonale (≈115°) qui balaie vers la gauche et **couvre tout le cadre à 3,95 s**, fond `linear-gradient(115deg,#F9A825,#FBD021)`. ÉTAT DE SORTIE : plein cadre or.

**Contrainte.** Aucune marque concurrente, pas de tête de mort. **Pourquoi.** Le problème santé ; prépare « 100 % naturel ».

## Frame 3 — Le feu (8,0–12,0 s, ~4,0 s)

- scene: Travelling latéral sur trois stations — marmite fumante, grillades sur braise, plat ivoirien dressé
- duration: 4s
- poster: 2.6s
- transition_in: cut (raccord B)
- status: animated
- src: compositions/03-le-feu.html
- voiceover: "Pour vos sauces, vos grillades… et tous vos plats,"
- vo_cues_local: voix 0,30–2,43 · « sauces » 0,40–0,65 · « grillades » 1,05–1,55 · « tous vos plats » 1,75–2,30
- blueprint: spatial-pan-stations
- rules: nudge-curve, svg-icon-enrichment, sine-wave-loop, motion-blur-streak
- focal: la station centrée à chaque instant ; secondaire : la chip-mot
- audio_cue: crépitement 0,1 s ; grésillement 1,2 s ; « ding » d'assiette 1,9 s

**Monde.** La chaleur d'une cuisine ivoirienne : un long plan de travail continu (bois chaud / carrelage crème), lumière dorée rasante, braises. Fond crème #FFECD1 avec bande basse plan de travail (bois brun teinté bordeaux), lueur orange chaude derrière chaque foyer.

**Séquence (temps locaux) :** un « rail » horizontal de 3 stations de 1920 px chacune (largeur totale 5760 px) qui **glisse vers la gauche** par paliers (nudge-curve : power2.inOut, avec léger flou de vitesse entre stations).
- Scene 1 — entrée raccord B (0,00–0,45 s) : ÉTAT D'ENTRÉE plein cadre or (même dégradé 115°) qui **s'efface vers la gauche** (clip-path polygone diagonal qui file vers la gauche) en révélant la station 1.
- Scene 2 (0,00–1,00 s) : **Station 1 « Sauces »** — marmite en fonte noire-bordeaux sur un foyer à flammes (flammes SVG or/rouge animées sinus), sauce graine rouge-orangé qui **bouillonne** (bulles qui gonflent/éclatent), vapeur en 3 volutes qui montent. Chip « Sauces » (Montserrat 700 30 px, fond bordeaux, texte blanc, pill) posée en bas-gauche de la station à 0,40 s (spring-pop).
- Scene 3 (0,85–1,25 s) : pan vers station 2 (x −1920).
- Scene 4 (1,05–1,85 s) : **Station 2 « Grillades »** — grille sur braises rougeoyantes (braises = petits points or/rouge qui pulsent, ce sont le trait d'or), un poisson braisé (tilapia doré, marques de grill) + 2 brochettes de viande, fumée légère. Chip « Grillades » à 1,05 s.
- Scene 5 (1,65–2,05 s) : pan vers station 3 (x −3840).
- Scene 6 (1,85–3,30 s) : **Station 3 « Tous vos plats »** — assiette ronde vue de 3/4 (bord bordeaux #7B1421 + intérieur blanc) : dôme d'attiéké (semoule crème texturée), poisson braisé, rondelles d'alloco (banane plantain frite dorée), piment frais rouge + rondelles d'oignon/tomate ; vapeur. C'est **l'objet-héros** (il revient en 06). Chip « Tous vos plats » à 1,85 s. Légère poussée caméra (scale 1→1.06) jusqu'à 3,3 s.
- Scene 7 — raccord C (3,30–4,00 s) : la vapeur du plat **monte et s'épaissit** ; un voile crème #FFECD1 monte du bas (translateY 100%→0 avec bord supérieur dégradé doux) et **couvre tout le cadre à 3,95 s**. ÉTAT DE SORTIE : plein cadre #FFECD1.

**Contrainte.** Plats ivoiriens, pas de cuisine générique. **Pourquoi.** La promesse : tous les usages.

## Frame 4 — Le terroir (12,0–16,0 s, ~4,0 s)

- scene: Ingrédients ivoiriens 2,5D/3D en orbite autour du tampon « 100 % NATUREL » et du titre « Ingrédients 100 % naturels » / « de Côte d'Ivoire »
- duration: 4s
- poster: 3.0s
- transition_in: cut (raccord C)
- status: animated
- src: compositions/04-terroir.html
- voiceover: "des épices et marinades cent pour cent naturelles, de Côte d'Ivoire."
- vo_cues_local: voix 0,15–3,80 · « épices et marinades » 0,15–1,20 · « cent pour cent naturelles » 1,40–2,66 · « de Côte d'Ivoire » 2,80–3,64
- blueprint: constellation-hub
- rules: orbit-3d-entry, depth-scatter-assemble, physics-press-reaction, ambient-glow-bloom
- focal: le tampon + titre (centre) ; secondaire : la constellation d'ingrédients
- audio_cue: souffle végétal 0,2 s ; « TAMP » 1,45 s ; carillon 2,85 s ; montée lumineuse 3,5 s

**Monde.** Le potager ivoirien, frais et vivant. Fond Vert Nature #2a5519 avec lueur radiale Vert Vif #376f23 (ambient-glow-bloom qui respire), feuilles en silhouette très sombres floues dans les coins (profondeur), poussière d'or qui orbite.

**Séquence (temps locaux) :**
- Scene 1 — entrée raccord C (0,00–0,50 s) : ÉTAT D'ENTRÉE plein cadre crème #FFECD1 qui **se lève** vers le haut (translateY 0→−110 %, bord inférieur dégradé doux), révélant le vert.
- Scene 2 (0,15–1,40 s) : dix ingrédients 3D (piment rouge, tomate, oignon violet, tête d'ail, gingembre, gombo, aubergine africaine (garden egg, blanc-jaune-vert), arachides en coque, noix de palme (rouge-orangé), feuille de basilic) **surgissent de la profondeur** (depth-scatter-assemble : translateZ −900→0, rotateX/Y déterministes, power3.out, stagger 0,07 s) jusqu'à leurs places sur une orbite elliptique (≈ 760×340 px) autour du centre. Taille 120–200 px.
- Scene 3 (1,40–1,75 s) : le tampon rond **« 100 % NATUREL »** (Ø 230 px, blanc sur Vert Vif, double anneau, texte Montserrat 800 sur cercle ou centré) **s'imprime** au-dessus du titre (physics-press-reaction : scale 1.6→0.92→1, rotation −8°, petite secousse de l'orbite).
- Scene 4 (1,45–2,70 s) : titre Cream Heavy blanc 96 px « Ingrédients 100 % naturels » (révélé par mots sur « cent pour cent naturelles »).
- Scene 5 (2,80–3,60 s) : sous-ligne Montserrat 700 Jaune Soleil 48 px « de Côte d'Ivoire » + **filet tricolore** sous elle (3 segments : Or Épicé #F9A825 · Blanc · Vert Vif #376f23, 360×8 px) qui se **dessine** gauche→droite (scaleX).
- Scene 6 (1,40–3,55 s) : la constellation **orbite** (orbit-3d-entry, sine.inOut) ; ingrédients respirent.
- Scene 7 — raccord D (3,55–4,00 s) : les ingrédients **foncent vers la caméra** (scale→3, blur→16 px, power3.in) ; une **lumière chaude** radiale (#FBD021 → #FFF3D6) s'épanouit du centre et **couvre tout le cadre à 3,97 s**. ÉTAT DE SORTIE : plein cadre #FFF3D6.

**Contrainte.** Pas de carte approximative. **Pourquoi.** Preuve d'authenticité (axe 1).

## Frame 5 — La gamme (16,0–22,5 s, ~6,5 s) · PIÈCE MAÎTRESSE

- scene: Révélation des 15 produits réels famille par famille, pastille-famille fixe qui change de mot, line-up final « Une gamme complète »
- duration: 6.5s
- poster: 5.6s
- transition_in: cut (raccord D, + overlay light-leak posé par l'assembleur)
- status: animated
- src: compositions/05-gamme.html
- voiceover: "Marin'Or Ivoire : épices, marinades, pâte d'arachide et huile rouge. Toute une gamme pour vous."
- vo_cues_local: voix 0,45–5,25 · « Marin'Or Ivoire » 0,45–1,46 · « épices » 1,63 · « marinades » 2,05 · « pâte d'arachide » 2,54 · « huile rouge » 3,45 · « Toute une gamme pour vous » 4,18–5,11
- blueprint: grid-card-assemble
- rules: waterfall-entry, spring-pop-entrance, ambient-glow-bloom
- focal: le line-up de produits ; secondaire : la pastille-famille
- assets: ../assets/brand/logo-anim.svg ; 15 packshots ../assets/products/<id>@2x.png (ids dans frame.md)
- audio_cue: montée 0,0 s ; « tok » par famille (1,63 / 2,05 / 2,54 / 3,45) ; scintillement 4,3 s

**Monde.** Une vitrine premium, l'écrin du badge Marin'Or. Fond radial Rouge Passion #A40C21 (centre) → Bordeaux #7B1421 (bords) — exactement le dégradé du badge. Grand ovale blanc 8 px en filigrane (≈ 1700×860, opacité 0,18, forme du badge) qui respire. Sol : légère réflexion/ombre douce sous les produits. Lueur or derrière le line-up (ambient-glow-bloom).

**Séquence (temps locaux) :**
- Scene 1 — entrée raccord D (0,00–0,50 s) : ÉTAT D'ENTRÉE plein cadre #FFF3D6 qui s'efface (opacity 1→0, le centre se dégage en premier via masque radial).
- Scene 2 (0,40–1,50 s) : logo (img, ≈ 360 px de large) **apparaît** en haut-centre (y ≈ 70–260) sur « Marin'Or Ivoire » (spring-pop).
- Scene 3 (1,55–4,10 s) : **pastille-famille fixe** au centre (y ≈ 300, pill crème #FFECD1, texte Cream Heavy bordeaux 48 px) dont le mot **change en place** (fixed-anchor-cycle : sortie y −30 + entrée y +30, 0,22 s) sur la voix : « Épices » (1,63) → « Marinades » (2,05) → « Pâte d'arachide » (2,54) → « Huile rouge » (3,45). À chaque mot, sa famille **entre en cascade depuis la droite** (waterfall-entry vers la gauche, x +500→0, rotation légère, power3.out, stagger 0,04 s) :
  - 1,63 s — les **10 sachets** (bouillon-poulet, poudre-djoumble, puree-ail, epice-poisson, poudre-poisson, poudre-crevette, piment-poudre, paprika, epice-poulet, graines-akpi) en **arc** au rang arrière (hauteur ≈ 250 px chacun, arc centré y ≈ 560, chevauchement léger, les extrêmes légèrement plus bas et tournés ±6°).
  - 2,05 s — **Marinade Poulet, Marinade Mixte, Marinade Poisson** au premier rang (hauteur ≈ 330 px).
  - 2,54 s — **Pâte d'arachide** au premier rang (hauteur ≈ 230 px).
  - 3,45 s — **Huile rouge** au premier rang (hauteur ≈ 400 px).
  Premier rang de gauche à droite : Marinade Poulet · Huile rouge · Pâte d'arachide (centre, devant) · Marinade Mixte · Marinade Poisson — sols alignés (base y ≈ 1000).
- Scene 4 (4,18–5,40 s) : la pastille devient **« Une gamme complète »** (même mécanique) ; un **reflet d'or** (bande diagonale blanche-or, opacité 0,5, mix-blend screen) **balaie** tout le line-up de gauche à droite (shimmer) à 4,3–5,1 s ; légère poussée caméra (scale 1→1.04).
- Scene 5 — raccord E (6,05–6,50 s) : la caméra **pousse sur le pot Marinade Poisson** (scale 1→2.4 centré sur lui, blur 0→18 px, power3.in) ; un voile crème #FFECD1 monte de 0→1 entre 6,25 et 6,48 s. ÉTAT DE SORTIE : plein cadre #FFECD1.

**Contrainte.** Packshots jamais recolorés ni déformés ; aucun chiffre de gamme. **Pourquoi.** Le cœur commercial.

## Frame 6 — Le geste & la table (22,5–26,5 s, ~4,0 s)

- scene: Gros plan du geste simple (poisson badigeonné de marinade, épices versées dans la marmite) puis recul jusqu'à la table familiale vue du dessus
- duration: 4s
- poster: 2.8s
- transition_in: cut (raccord E)
- status: animated
- src: compositions/06-partage.html
- voiceover: "Simple à utiliser, à déguster en famille et entre amis."
- vo_cues_local: voix 0,20–3,21 · « Simple à utiliser » 0,20–1,24 · « à déguster en famille et entre amis » 1,45–3,08
- blueprint: zoom-out-workspace-reveal
- rules: svg-path-draw, particle-burst, multi-phase-camera
- focal: phase A le geste ; phase B la table + titre
- assets: ../assets/products/marinade-poisson@2x.png ; ../assets/products/epice-poisson@2x.png
- audio_cue: pinceau 0,25 s ; épices versées 0,9 s ; ambiance douce 1,6 s ; tintement de verres 2,6 s

**Monde.** Phase A : plan de travail clair, macro, gestes nets. Phase B : la chaleur d'un repas partagé vu du dessus — nappe Rose Poudre #F6E8EA à motif discret bordeaux, lumière douce.

**Séquence (temps locaux) :**
- Scene 1 — entrée raccord E (0,00–0,30 s) : ÉTAT D'ENTRÉE plein cadre #FFECD1 (opacity 1→0) ; le pot **Marinade Poisson** (packshot, ≈ 520 px de haut, à gauche x ≈ 280) se pose depuis scale 1.5 + blur 18 px → 1 + 0 (expo.out 0,45 s).
- Scene 2 (0,20–1,10 s) : **Phase A — le geste.** Au centre-droite, un poisson (tilapia 2,5D) sur une planche ; un pinceau de cuisine **badigeonne** : la marinade (couche orange-rouge brillante) **se dessine** sur le poisson en 3 coups (svg-path-draw / clip-path, 0,25 s chacun). Chip « Simple à utiliser » (pill bordeaux, Montserrat 700 blanc 30 px) en haut-gauche à 0,25 s.
- Scene 3 (0,75–1,40 s) : le sachet **Épice Spéciale Poisson** (packshot ≈ 360 px) entre par la droite, **s'incline** (rotation −35°) et **verse** une coulée de poussière dorée (particle-burst en flux, 60–90 particules déterministes = le trait d'or) dans une marmite au premier plan.
- Scene 4 (1,30–3,40 s) : **Phase B — recul continu** (multi-phase-camera / zoom-out : tout le décor macro se réduit — scale 1→0.28 — et devient le centre d'une **table ronde vue du dessus**). Sur la table (Ø ≈ 1000 px) : au centre le **plat dressé de la Frame 3** (même assiette à bord bordeaux #7B1421, attiéké, poisson braisé, alloco, piment, vu du dessus), 6 assiettes autour, verres, et 6 **bras stylisés** (manches aux couleurs de la palette : bordeaux, vert vif, or, rose poudre, crème, rouge passion ; mains en tons bruns chauds) qui **entrent** depuis le bord du cadre et se servent (stagger), puis deux verres **trinquent** à 2,6 s (petite étincelle d'or).
- Scene 5 (1,45–3,10 s) : titre Cream Heavy bordeaux 88 px sur bande crème en haut ou bas du cadre : « À déguster en famille et entre amis » — révélé par mots sur la voix.
- Scene 6 — raccord F (3,45–4,00 s) : la caméra **plonge** sur l'assiette centrale (scale ×6 centré sur elle, power3.in) jusqu'à ce que son bord bordeaux **couvre tout le cadre à 3,97 s**. ÉTAT DE SORTIE : plein cadre #7B1421.

**Contrainte.** Personnages suggérés par bras/mains, pas de visages. **Pourquoi.** Axes 2 (convivialité) et 3 (simplicité).

## Frame 7 — Le goût en or (26,5–30,0 s, ~3,5 s)

- scene: Le logo s'assemble calque par calque, packshot, slogan « Le goût en or », coordonnées et CTA « Commandez dès maintenant » ; plan tenu final
- duration: 3.5s
- poster: 3.3s
- transition_in: cut (raccord F)
- status: animated
- src: compositions/07-signature.html
- voiceover: "Marin'Or Ivoire, le goût en or !"
- vo_cues_local: voix 0,55–2,41 · « Marin'Or Ivoire » 0,55–1,45 · « le goût en or » 1,53–2,25
- blueprint: logo-assemble-lockup
- rules: svg-path-draw, scale-swap-transition
- focal: le logo (centre-haut) ; secondaire : slogan, puis barre contact/CTA
- assets: ../assets/brand/logo-anim.svg (INLINE) ; packshots ../assets/products/epice-poisson@2x.png, paprika@2x.png, pate-arachide@2x.png, marinade-poulet@2x.png, huile-rouge@2x.png, marinade-poisson@2x.png
- audio_cue: whoosh de morph 0,05 s ; accord final 0,6 s ; carillon doré 1,6 s ; tenue 2,4 s

**Monde.** La signature, l'écrin. Fond radial Bordeaux : centre #A40C21 → bords #5c0f19 (vignette teintée), fine poussière d'or qui retombe lentement puis se fige.

**Séquence (temps locaux) :**
- Scene 1 — entrée raccord F (0,00–0,55 s) : ÉTAT D'ENTRÉE plein cadre #7B1421. Le **badge ovale** du logo (Calque_1, forme cls-5) **se contracte** depuis ≈ 4× sa taille jusqu'à sa taille finale (logo ≈ 1000 px de large, centré, y ≈ 90–620) (scale-swap, power3.out), pendant que le fond s'assombrit vers sa vignette.
- Scene 2 (0,35–0,95 s) : le **liseré blanc** (cls-2) **se dessine** (svg-path-draw, strokeDashoffset, 0,55 s) ; l'**éléphant** blanc (Calque_2, 2e path) **apparaît** en ressort ; la **feuille dorée** (cls-3) **pousse** depuis sa base (scale 0→1, transform-origin bas-gauche, back.out) — le trait d'or s'y achève.
- Scene 3 (0,55–1,45 s) : « Marin'Or » puis « Ivoire » (Calque_3, paths blancs) **se révèlent** par masque gauche→droite (clip-path inset 0 100% 0 0 → 0) sur la voix ; le **point doré** (cls-4) **tombe** sur le « i » à 1,40 s avec une petite étincelle.
- Scene 4 (1,50–2,30 s) : sous le logo, « Le goût en or » Cream Heavy Jaune Soleil #FBD021 110 px (y ≈ 690) **monte** (y 30→0) ; UN **reflet d'or** (shimmer : bande claire qui traverse les lettres, la seule exception au « pas de texte en dégradé ») à 1,9–2,4 s. En même temps, packshots **glissent** en place depuis les bords : à gauche Épice Spéciale Poisson, Paprika, Pâte d'arachide ; à droite Marinade Poulet, Huile rouge, Marinade Poisson (hauteur 280–380 px, bases alignées y ≈ 900, légèrement en éventail, sous/à côté du logo sans le toucher).
- Scene 5 (1,90–2,45 s) : barre bas (y ≈ 950–1010) Montserrat 600 blanc 30 px : « ☎ +225 01 53 70 26 14 » · « marinorivoire.com » · icônes simples Facebook / Instagram / LinkedIn (glyphes vectoriels blancs dessinés) + « @marinorivoire » ; et la chip CTA **« Commandez dès maintenant »** (pill crème #FFECD1, Montserrat 700 bordeaux 32 px) centrée au-dessus de la barre (y ≈ 860) — légère pulsation unique à 2,3 s.
- Scene 6 — **plan tenu** (2,45–3,50 s) : tout se fige ; rien ne bouge.

**Contrainte.** Logo jamais recoloré ni déformé (transforms uniformes uniquement). **Pourquoi.** Signature mémorisable + action claire.
