# Spot publicitaire 2D motion design — Justvyou Property (60 s)

Livrables du brief `prompt_spot_justvyou_60s.pdf`, établis à partir du mémoire *Conception et réalisation de supports de communication pour la promotion de l'entreprise immobilière Justvyou Property*.

| # | Fichier | Contenu |
|---|---|---|
| 1 | [`01_script_voix_off.md`](01_script_voix_off.md) | Voix off complète, tableau de synchronisation (timecode, voix off, texte à l'écran, action visuelle), règles de lisibilité |
| 2 | [`02_storyboard.md`](02_storyboard.md) et [`storyboard/`](storyboard) | Storyboard des 4 scènes avec 8 vignettes SVG (positions identiques au script), caméra, couleurs, transitions, tableau automatisé / à la main |
| 3 | [`03_SPOT_JUSTVYOU_60S.jsx`](03_SPOT_JUSTVYOU_60S.jsx) | Script ExtendScript pour After Effects, commenté en français |
| — | [`assets/`](assets) | Logo fourni en PNG transparent : complet, symbole seul, logotype seul (importés par le script) |

## Exécuter le script

1. Copiez tout le dossier `spot_justvyou_60s/` sur le poste. Le script cherche ses fichiers dans `assets/`, à côté de lui.
2. *(Facultatif)* Installez la police **Larsseit** (ExtraBold, Bold, Regular) et le plug-in gratuit **Quick Chromatic Aberration**.
3. *(Facultatif)* Déposez `voix_off.wav` et `musique.wav` dans `assets/audio/`.
4. Dans After Effects (CC 2019 ou plus récent) : **Fichier > Scripts > Exécuter le fichier script…**, puis choisissez `03_SPOT_JUSTVYOU_60S.jsx`.
5. Un rapport s'affiche à la fin : police utilisée, logo importé ou non, plug-ins trouvés, vérifications de durée.
6. Tout est regroupé dans un seul historique d'annulation : **Édition > Annuler** supprime l'ensemble.

### Ce que le script crée

```
01_COMPS/
   SPOT_JUSTVYOU_60S         1920×1080 · 30 i/s · 60 s
   SC01_CLIENT_PERDU         15 s  (00:00 → 00:15)
   SC02_DECOUVERTE_SERVICES  20 s  (00:15 → 00:35)
   SC03_FAMILLE_SATISFAITE   15 s  (00:35 → 00:50)
   SC04_LOGO_CONTACTS        10 s  (00:50 → 01:00)
02_ASSETS/       logos PNG, solides de fond (dégradé + grain), nulls caméra
03_AUDIO/        voix off et musique si fournies, sinon vide
04_ADJUSTMENTS/  ADJ_FINAL : Lueur · Grain · Aberration chromatique · Étalonnage léger
```

La composition principale contient aussi :
- les 4 scènes, bout à bout ;
- 3 transitions : volet or/bleu à 15 s, volet bleu/or à 35 s, iris or à 50 s ;
- le calque d'ajustement final ;
- un null guide `VO_SYNC` portant un marqueur par réplique de voix off ;
- des marqueurs de scène dans la chronologie ;
- des guides de composition (tiers, centre, zone titre) et un calque guide des zones de sécurité (90 % et 80 %).

Les animations de texte (pop-up, fondu, slide, cascade), le grain, la caméra 2D et les transitions sont pilotés **par expressions calées sur l'inPoint et l'outPoint** de chaque calque. Déplacer ou recadrer un calque dans la timeline déplace son animation avec lui, sans clé à reprendre.

### Ce qui reste à animer à la main

- **Personnages** : le client (scène 1), la famille et le conseiller (scène 3). Le script pose à leur place des **repères rouges « À ANIMER »**, en calques guides non rendus, avec la consigne dans le commentaire du calque. À faire : dessin, stretch & squash léger, clignements, paupières, sourires, gestuelle des mains, marche, mouvements de tête.
- **Masques adoucis** (Feather) et **rim lights blanches** sur la peau.
- **Styles de calque** : le script tente d'appliquer Incrustation en dégradé (« Réfléchi », 15 %) et Lueur interne (blanche, 40 %) sur les maisons, les accessoires et l'immeuble, via les commandes de menu. Les **couleurs d'un dégradé ne sont pas scriptables** : réglez-les à la main (par exemple blanc → transparent, mode Incrustation). Si les commandes ne sont pas trouvées, le rapport le signale.
- **Audio** : enregistrement de la voix off d'après `01_script_voix_off.md`, choix de la musique, sound design (swooshes aux transitions), mixage.
- **Rendu** : H.264, 1920×1080, 30 i/s, 60 s.

## Vérifications effectuées avant livraison

- **Durée :** 15 + 20 + 15 + 10 = **60 s** (1 800 images à 30 i/s). Les scènes sont contiguës à 00:15, 00:35 et 00:50, et le script le revérifie à l'exécution.
- **Transitions :** les volets sont centrés sur x = 960 à 15,0 s et 35,0 s, et couvrent alors tout l'écran (2 × 2 200 px de large). L'iris atteint 99 % dès 49,97 s : son diamètre de 2 300 px dépasse la diagonale de l'image (2 203 px).
- **Lisibilité 1080p :** corps minimum de 40 px. Tous les textes sont dans la zone titre (192 à 1 728 × 108 à 972), y compris la rangée de contacts la plus large (de 260 à environ 1 660 px). Chaque message reste affiché au moins 2,5 s.
- **Syntaxe JSX :**
  - Analyse réussie en **ECMAScript 3**, le dialecte d'ExtendScript, mots réservés interdits comme noms de propriété.
  - Exécution complète contre une maquette du modèle objet d'After Effects dans 3 scénarios : Larsseit installée, Montserrat de repli, sans fichiers `assets/`.
  - Les 141 à 151 expressions posées ont été évaluées à 5 instants chacune, sans erreur.
  - Ces tests valident la logique du script, pas le comportement d'After Effects lui-même. Le premier lancement dans AE reste la vérification finale.
- Fichier enregistré en **UTF-8 avec BOM**, pour que les accents s'affichent correctement dans After Effects sous Windows.

## Hypothèses

Les informations absentes du brief ont été complétées par la valeur la plus cohérente :

| Sujet | Valeur retenue | Source ou raison |
|---|---|---|
| Téléphone | **(+225) 05 55 58 07 24** | Affiche et flyer du mémoire (« Contactez-nous 05-55-58-07-24 ») ; indicatif +225 ajouté pour les investisseurs de la diaspora |
| E-mail | **contact@justvyou-property.ci** | Page Contact du site web du mémoire |
| Site web | **www.justvyou-property.ci** | Déduit du domaine de l'e-mail (aucune URL publique dans le mémoire) |
| Réseaux sociaux | Facebook, Instagram, WhatsApp, **@justvyouproperty** | Les trois icônes figurent sur les supports du mémoire ; l'identifiant est une hypothèse à confirmer |
| Localisation | **Zone 4 · Abidjan** | Siège indiqué sur la page Contact (Boulevard de Marseille, Zone 4) |
| Écriture du nom | « Justvyou Property » dans les textes, logo fourni tel quel (« JustVyou ») | Le brief et le mémoire écrivent « Justvyou » |
| Police | Larsseit ExtraBold / Bold / Regular, sinon Montserrat (signalé), sinon Arial | Brief |
| Nuances de dégradé | Bleu assombri `#0B2C5E`, or éclairci `#FEF4DC`, bleu éclairci `#ECF0F6` | Mélanges des seules couleurs de la charte avec du noir ou du blanc ; les codes `#114491` et `#F7B819` ne sont pas modifiés |
| Ombres | Violet-bleu `#2F2370`, 35 %, direction 135°, adoucissement 32 | Brief : « ombres portées teintées (violet/bleu) » |
| Grain | `posterizeTime(12); wiggle(10, 10)` **ramené dans 5–8 %** par `linear()` | Utilisé seul, `wiggle(10, 10)` autour de 6,5 % irait de −3,5 à 16,5 % et sortirait de la plage demandée |
| Aberration chromatique | Quick Chromatic Aberration si installé (recherché parmi les effets disponibles), sinon signalé | Ce plug-in n'est pas livré avec After Effects |
| Étalonnage léger | Effet Teinte à 8 % | Natif et entièrement scriptable, contrairement aux réglages de Lumetri |
| Personnages | Client de 30 à 40 ans ; famille de deux parents et un enfant ; un conseiller | Cibles du brief (particuliers, familles, investisseurs) |
| Version d'After Effects | CC 2019 (v16) ou plus récent | Guides de composition et détection des polices utilisés « au mieux » |
| Voix off | Débit d'environ 2 mots/s, 111 mots | Ton chaleureux et posé ; le spot doit aussi fonctionner sans le son |
