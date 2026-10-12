---
format: 1920x1080
duration: 30s
message: "Les saveurs authentiques de Côte d'Ivoire, 100 % naturelles, pour relever simplement tous vos plats — Marin'Or Ivoire, le goût en or."
arc: Question (accroche) → Doute (problème) → Promesse (le feu) → Preuve (terroir) → Révélation (la gamme) → Usage & partage → Signature + CTA
audience: Décideurs de grandes entreprises (pièce portfolio) — cible finale : foyers ivoiriens qui cuisinent
mode: collaborative
version: 1
---

# Marin'Or Ivoire — « Le goût en or » · storyboard v1

## Décisions

- **Message :** Les saveurs authentiques de Côte d'Ivoire, 100 % naturelles, relèvent simplement tous vos plats.
- **Public & arc :** des décideurs qui jugent un savoir-faire ; arc en 7 temps (scénario client condensé) : question → doute → promesse → preuve → révélation → partage → signature.
- **Format :** 1920×1080, 30,0 s, voix off FR (Kokoro « Siwis », ~21 s de parole mesurée), musique + sound design. Pas de sous-titres → pas de zone d'exclusion basse, mais marges de sécurité 120 px / 90 px.
- **Le fil conducteur (spine) : « le trait d'or ».** Une traînée de poussière d'épices dorée (dégradé exact de la feuille du logo #F9A825 → #FBD021) traverse chaque séquence : pincée qui souligne la question (01), trait qui raye les additifs (02), braise sous la grille (03), orbite autour du terroir (04), reflet qui balaie la gamme (05), épices versées dans la marmite (06), et elle dessine enfin la feuille dorée du logo (07).
- **Objet-héros & rappel :** le **plat dressé** apparaît en 03 (fin du travelling) et revient au centre de la table en 06 ; son assiette ronde devient le badge ovale du logo en 07.
- **Marque :** voir `frame.md` — palette client 10 couleurs ; Cream Heavy (titres) + Montserrat 500/600/700 ; logo SVG calqué ; 15 packshots réels détourés.
- **Rythme :** rapide (01) → tendu (02) → travelling chaud (03) → éclosion (04) → SHADER → construction-héros (05) → doux (06) → signature + **plan tenu** (07). Direction de déplacement unique : **vers la gauche** (vertical seulement pour la vapeur).
- **Plan tenu :** 28,9 → 30,0 s — le pack final se fige, rien ne bouge, la signature respire.
- **Interdits :** aucune image/vidéo générée par IA ; aucune photo de stock ; aucun faux produit ; pas de RadioTime Tooled hors logo ; pas de texte en dégradé sauf le reflet sur « le goût en or » ; pas d'effet « glitch/tech » (hors-sujet pour l'alimentaire) ; éviter le **diaporama** (chaque plan = une nouvelle carte) et l'**économiseur d'écran** (mouvement qui ne dit rien).
- **Vérité :** les packshots et le logo sont les fichiers réels du client ; les plats, légumes et ustensiles sont des illustrations vectorielles — c'est revendiqué comme du motion design.

## Frame 1 — Accroche « La pincée d'or » (0,0–4,0 s, ~4,0 s)

- scene: Ballet d'icônes culinaires 2,5D autour de la question « Envie de relever le goût de vos plats du quotidien ? »
- duration: 4s
- poster: 3.0s
- transition_in: cut
- status: outline
- src: compositions/01-accroche.html
- voiceover: "Envie de relever le goût de vos plats du quotidien ?"
- blueprint: kinetic-type-beats
- rules: spring-pop-entrance, orbit-3d-entry, svg-path-draw, sine-wave-loop
- audio_cue: 0,1 s pluck de balafon par icône (8 notes, montée) ; 2,4 s « ffft » de pincée sur le trait d'or

**À l'écran.** Toile Crème Douce, lueur radiale or. Huit icônes 2,5D (piment, gousse d'ail, feuille de laurier, grains de poivre, oignon, cuillère en bois, mortier & pilon, marmite) **jaillissent** en ressort en anneau (stagger 0,05 s) puis **orbitent** lentement en profondeur. Au centre, la question se **construit** mot à mot en Cream Heavy bordeaux sur 2 lignes : « Envie de relever le goût » / « de vos plats du quotidien ? ». « relever le goût » passe en or ; sous ces mots, le **trait d'or se dessine** (pincée de poussière d'épices qui retombe).
**Mouvement.** Première icône visible à 0,1 s. Mots en `back.out(1.6)` 0,45 s, icônes `expo.out`, orbite `sine.inOut`.
**Sortie.** Les icônes sont **aspirées** dans le point du « ? », qui s'ouvre en iris sombre (bordeaux nuit) → Frame 2.
**Contrainte.** Pas d'icônes « clipart » plates : chaque icône a volume (dégradé), reflet et ombre teintée.
**Pourquoi.** Accroche en langage du bénéfice (« relever le goût ») — pose le désir avant le produit.

## Frame 2 — Le doute (4,0–8,0 s, ~4,0 s)

- scene: Produits d'assaisonnement industriels anonymes étiquetés « Additifs », « Exhausteurs artificiels », « Conservateurs », rayés par le trait d'or et réduits en poussière
- duration: 4s
- poster: 6.6s
- transition_in: circle-iris (depuis le point du « ? »)
- status: outline
- src: compositions/02-doute.html
- voiceover: "Sans additifs ni substances douteuses pour votre santé ?"
- blueprint: kinetic-type-beats
- rules: spring-pop-entrance, css-marker-patterns, particle-burst, sine-wave-loop
- audio_cue: 4,2 s battement grave + pulsation d'alerte ; 6,3 s « swish » du trait d'or ; 6,5 s effritement sablé

**À l'écran.** Fond Bordeaux assombri (radial #7B1421 → #2a070d), vignette. Trois contenants génériques sans marque (cube de bouillon emballé, flacon, pot à étiquette chimique « E-xxx ») **tombent** et rebondissent en rang ; étiquettes Montserrat : « Additifs », « Exhausteurs artificiels », « Conservateurs ». Un halo rouge **pulse** derrière eux. Texte haut : « Sans additifs ni substances douteuses » / « pour votre santé ? » (Montserrat 700 blanc, « votre santé » en Jaune Soleil). À 6,3 s le **trait d'or raye** les trois étiquettes d'un seul geste vers la gauche ; les contenants s'**effritent** en poussière qui devient dorée.
**Sortie.** Le trait d'or s'épaissit en bande diagonale qui **balaie** l'écran vers la gauche → Frame 3.
**Contrainte.** Aucune marque concurrente identifiable ; pas de tête de mort ni de visuel anxiogène excessif — un doute, pas une peur.
**Pourquoi.** Le problème du scénario (santé) ; prépare la promesse « 100 % naturel ».

## Frame 3 — Le feu (8,0–12,0 s, ~4,0 s)

- scene: Travelling latéral sur trois stations de cuisine — marmite fumante, grillades sur braise, plat ivoirien dressé
- duration: 4s
- poster: 10.6s
- transition_in: diagonal gold wipe (vers la gauche)
- status: outline
- src: compositions/03-le-feu.html
- voiceover: "Pour vos sauces, vos grillades… et tous vos plats,"
- blueprint: spatial-pan-stations
- rules: svg-icon-enrichment, sine-wave-loop, motion-blur-streak
- audio_cue: 8,1 s crépitement de feu ; 9,2 s grésillement de grill ; 10,4 s petit « ding » d'assiette posée

**À l'écran.** Un plan de travail continu, la caméra **glisse vers la gauche** sur 3 stations, chacune ancrée sur le mot de la voix off : **« Sauces »** (marmite en fonte sur flammes, sauce graine qui bouillonne, vapeur en volutes) → **« Grillades »** (grille sur braises rougeoyantes, poisson braisé + brochettes, fumée, braises = trait d'or) → **« Tous vos plats »** (assiette vue de 3/4 : attiéké, poisson braisé, alloco, piment frais ; vapeur). Les mots se **posent** en chips Montserrat bordeaux sur crème, ancrés bas-gauche de chaque station.
**Mouvement.** Pan `power2.inOut` par paliers (nudge-curve), flou de vitesse léger entre stations ; flammes/vapeur en boucle sinus.
**Sortie.** La vapeur du plat **monte** et remplit l'écran → Frame 4 (balayage vertical).
**Contrainte.** Pas de cuisine générique « occidentale » : les plats sont ivoiriens.
**Pourquoi.** La promesse : tous les usages (sauces, grillades, tout plat).

## Frame 4 — Le terroir (12,0–16,0 s, ~4,0 s)

- scene: Légumes et ingrédients ivoiriens 2,5D/3D en orbite autour du tampon « 100 % NATUREL » et du titre « Ingrédients 100 % naturels de Côte d'Ivoire »
- duration: 4s
- poster: 14.6s
- transition_in: steam rise (balayage vertical vers le haut)
- status: outline
- src: compositions/04-terroir.html
- voiceover: "des épices et marinades cent pour cent naturelles, de Côte d'Ivoire."
- blueprint: constellation-hub
- rules: orbit-3d-entry, depth-scatter-assemble, physics-press-reaction, ambient-glow-bloom
- audio_cue: 12,2 s souffle végétal ; 13,6 s « TAMP » du tampon ; 15,2 s carillon léger

**À l'écran.** Fond Vert Nature, lueur Vert Vif. Dix ingrédients 3D (piment rouge, tomate, oignon violet, ail, gingembre, gombo, aubergine africaine, arachides, noix de palme, feuille de basilic) **surgissent de la profondeur** (rotateX/Y + translateZ) et se posent en orbite elliptique. Au centre, le tampon rond **« 100 % NATUREL »** (blanc sur vert, double anneau, écho du badge des sachets) **s'imprime** avec un rebond. Titre Cream Heavy blanc : « Ingrédients 100 % naturels » / sous-ligne Montserrat Jaune Soleil : « de Côte d'Ivoire » soulignée d'un filet tricolore **or · blanc · vert** (couleurs du drapeau ivoirien, tirées de la palette).
**Sortie.** Les ingrédients **foncent vers la caméra** ; un flash de lumière chaude (shader light-leak) → Frame 5.
**Contrainte.** Pas de carte géographique approximative ; l'origine est dite par le filet tricolore et le texte.
**Pourquoi.** La preuve d'authenticité — l'axe 1 du client.

## Frame 5 — La gamme (16,0–22,5 s, ~6,5 s) · PIÈCE MAÎTRESSE

- scene: Révélation des 15 produits réels, famille par famille, jusqu'au line-up complet sous le logo
- duration: 6.5s
- poster: 21.8s
- transition_in: light-leak (shader)
- status: outline
- src: compositions/05-gamme.html
- voiceover: "Marin'Or Ivoire : épices, marinades, pâte d'arachide et huile rouge. Toute une gamme pour vous."
- blueprint: grid-card-assemble
- rules: fixed-anchor-cycle, waterfall-entry, spring-pop-entrance, ambient-glow-bloom
- registry: shimmer-sweep, light-leak
- audio_cue: 16,0 s montée lumineuse ; chaque famille = un « tok » de percussion calé sur le mot ; 21,6 s scintillement

**À l'écran.** Fond badge (radial Rouge Passion → Bordeaux), grand ovale blanc 8 px en filigrane (écho du liseré du logo). Logo SVG en haut-centre (petit). Une **pastille-famille fixe** au centre-haut **change de mot** en suivant la voix : « Épices » → « Marinades » → « Pâte d'arachide » → « Huile rouge ». À chaque mot, sa famille **entre en cascade** depuis la droite et se place dans un line-up en arc : **10 sachets** en arc au fond, puis au premier rang **Marinade Poulet · Marinade Mixte · Marinade Poisson**, **Pâte d'arachide**, **Huile rouge**. Ombres portées douces au sol. À 21,0 s la pastille devient « **Une gamme complète** » et un **reflet d'or balaie** tout le line-up.
**Sortie.** Poussée (zoom-through) sur le pot **Marinade Poisson** → raccord sur Frame 6.
**Contrainte.** Packshots jamais recolorés ni déformés ; aucun chiffre de gamme annoncé.
**Pourquoi.** Le cœur commercial : toute la gamme, réelle, désirable.

## Frame 6 — Le geste & la table (22,5–26,5 s, ~4,0 s)

- scene: Gros plan du geste simple (poisson badigeonné, épices versées dans la marmite) puis recul jusqu'à la table familiale vue du dessus
- duration: 4s
- poster: 25.6s
- transition_in: match-cut (pot Marinade Poisson)
- status: outline
- src: compositions/06-partage.html
- voiceover: "Simple à utiliser, à déguster en famille et entre amis."
- blueprint: zoom-out-workspace-reveal
- rules: svg-path-draw, particle-burst, multi-phase-camera
- audio_cue: 22,6 s pinceau humide ; 23,4 s épices versées (shaker) ; 24,6 s rires/ambiance douce (synthé léger) ; 25,2 s tintement de verres

**À l'écran.** Phase A (22,5–24,2 s) — macro sur fond Crème : un pinceau **badigeonne** le poisson (la marinade se **dessine** en couches brillantes), le sachet « Épice Spéciale Poisson » s'**incline** et **verse** la poussière d'or dans la marmite. Chip : « Simple à utiliser ». Phase B (24,2–26,5 s) — **recul continu** jusqu'à une table ronde vue du dessus (nappe Rose Poudre à motif bordeaux) : au centre le **plat dressé de Frame 3** (rappel), 6 assiettes, verres, bras stylisés (manches aux couleurs de la palette) qui se servent et **trinquent** (étincelle d'or). Titre Cream Heavy bordeaux : « À déguster en famille et entre amis ».
**Sortie.** La caméra **plonge** sur l'assiette centrale ; elle **se transforme** en badge ovale du logo → Frame 7.
**Contrainte.** Personnages suggérés (bras/mains), pas de visages illustrés approximatifs.
**Pourquoi.** Axes 2 (convivialité) et 3 (simplicité).

## Frame 7 — Le goût en or (26,5–30,0 s, ~3,5 s)

- scene: Le logo s'assemble calque par calque, packshot de la gamme, slogan, coordonnées et appel à l'action ; plan tenu final
- duration: 3.5s
- poster: 29.5s
- transition_in: morph (assiette → badge)
- status: outline
- src: compositions/07-signature.html
- voiceover: "Marin'Or Ivoire, le goût en or !"
- blueprint: logo-assemble-lockup
- rules: svg-path-draw, scale-swap-transition, spring-pop-entrance
- registry: shimmer-sweep
- audio_cue: 26,6 s whoosh de morph ; 27,1 s accord final ; 27,9 s carillon doré sur le point d'or ; 28,9 s silence musical (tenue)

**À l'écran.** Le badge bordeaux se **remplit**, le liseré blanc **se dessine** (stroke), l'éléphant **apparaît** en ressort, la feuille dorée **pousse** depuis sa tige (le trait d'or s'y achève), « Marin'Or » puis « Ivoire » se **révèlent** par masque gauche→droite, le point doré **tombe** sur le « i » avec une étincelle. Sous le logo : « **Le goût en or** » en Cream Heavy Jaune Soleil, **reflet d'or** unique. Packshot : 3 produits à gauche (Épice Spéciale Poisson, Paprika, Pâte d'arachide), 3 à droite (Marinade Poulet, Huile rouge, Marinade Poisson) **glissent** en place. Bas d'écran, barre de contact Montserrat blanc : « ☎ +225 01 53 70 26 14 · marinorivoire.com · f ◎ in @marinorivoire » + chip CTA crème/bordeaux « **Commandez dès maintenant** ».
**Plan tenu.** 28,9–30,0 s : tout est figé.
**Contrainte.** Logo jamais recoloré ni déformé ; pas d'écran de fin statique dès l'entrée — l'assemblage occupe 27–28,9 s.
**Pourquoi.** Signature mémorisable + action claire pour le spectateur.
