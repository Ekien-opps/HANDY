/*
 * =============================================================================
 *  MARIN'OR IVOIRE - ANIMATION DU LOGO
 *  Script After Effects (ExtendScript .jsx) - testé pour la syntaxe AE 2026
 * =============================================================================
 *
 *  Utilisation :
 *    Fichier > Scripts > Exécuter le fichier de script...  ->  ce fichier
 *
 *  Le script cherche d'abord les PNG dans le dossier du script. S'il ne les
 *  trouve pas tous, il vous demande de sélectionner le dossier qui les contient.
 *
 *  Fichiers attendus (la recherche tolère accents, espaces et majuscules) :
 *    - Forme de fond rouge ovale.png
 *    - Texte Marin'.png
 *    - Texte Or.png
 *    - Texte Ivoire.png
 *    - Point doré.png   (ou "Point dor .png", "Point dor#U00e9.png"...)
 *    - Oreille.png      (oreille dorée de l'éléphant)
 *    - Calque7.png      (corps blanc de l'éléphant)
 *
 *  Ce qui est créé :
 *    Composition 1920x1080, 60 i/s, 5 s, avec :
 *      LOGO_MASTER (nul)        -> place et met à l'échelle tout le logo
 *       ├─ ELEPHANT_CTRL (nul)  -> zoom d'intro + recul vers la position finale
 *       │   └─ Corps éléphant   -> barrissement (rotation + squash/stretch)
 *       │       ├─ Oreille      -> ondulation souple
 *       │       ├─ Paupières    -> plissement des yeux (squint)
 *       │       └─ Ondes 1..3   -> ondes sonores du barrit (optionnel)
 *       ├─ Texte Marin' / Or / Ivoire -> écriture au feutre (Linear Wipe)
 *       ├─ Point doré           -> pop "slime" avec squash & stretch
 *       └─ Fond ovale rouge     -> apparition douce en arrière-plan
 *
 *  Toutes les coordonnées des pièces sont exprimées en pixels NATIFS des PNG,
 *  relatives au centre de l'ovale (mesurées sur logo.png). Pour tout ajuster,
 *  modifiez les blocs CONFIG, TIMING et LAYOUT ci-dessous.
 * =============================================================================
 */

(function MarinOrIvoireLogoAnimation() {

    // =========================================================================
    // 0. CONFIGURATION GÉNÉRALE
    // =========================================================================
    var CONFIG = {
        compName: "Marin'Or Ivoire - Logo Anim",
        width: 1920,
        height: 1080,
        fps: 60,
        duration: 5,
        bgColor: [0.07, 0.03, 0.04],     // fond de compo (aperçu uniquement)

        logoWidth: 1500,                 // largeur finale de l'ovale à l'écran (px)
        logoCenter: [960, 540],          // centre du logo final dans la compo

        elephantIntroHeight: 640,        // hauteur de l'éléphant "en grand" (px)
        elephantIntroOffsetY: 0,         // décalage vertical de l'intro (px écran)

        motionBlur: true,                // flou de mouvement sur les calques animés
        soundWaves: true,                // ondes sonores dorées pendant le barrit
        gold: [250 / 255, 191 / 255, 35 / 255],  // or du logo (#FABF23)

        writeAngle: 260,                 // angle du Linear Wipe (270 = gauche->droite pur ;
                                         //  250-265 = bord penché comme l'écriture script)
        writeFeather: 70                 // douceur du bord "feutre" (px natifs)
    };

    // =========================================================================
    // 0b. TIMING (secondes) - modifiez ici pour décaler toute une séquence
    // =========================================================================
    var TIMING = {
        // --- 1. Apparition & barrissement (0.0 - 1.8 s) ---
        introStart:      0.00,
        introEnd:        0.52,
        squintStart:     0.30,   // les yeux commencent à se plisser
        squintClosed:    0.44,   // yeux plissés
        trumpetStart:    0.45,   // anticipation (la tête plonge)
        trumpetPeak:     0.80,   // tête levée : barrit !
        trumpetHoldEnd:  1.25,   // fin du tremblement
        trumpetEnd:      1.58,   // retour au repos
        eyesReopenStart: 1.35,   // les yeux se rouvrent dès la fin du barrit
        eyesOpen:        1.50,
        earStart:        0.25,
        earSettle:       1.50,

        // --- 2. Repliement du logo & écriture du texte (1.8 - 3.2 s) ---
        shrinkStart:     1.80,
        shrinkLand:      2.38,
        shrinkSettle:    2.62,
        marinStart:      1.98,
        marinEnd:        2.60,
        orStart:         2.58,
        orEnd:           2.86,
        ivoireStart:     2.72,
        ivoireEnd:       3.20,

        // --- 3. Point doré & fond ovale (3.2 - 4.5 s) ---
        pointStart:      3.20,
        pointEnd:        3.86,
        ovalStart:       3.20,
        ovalEnd:         4.50
    };

    // =========================================================================
    // 0c. LAYOUT - position des pièces dans le logo final
    //     (pixels natifs des PNG, origine = centre de l'ovale)
    // =========================================================================
    var LAYOUT = {
        body:   [-272.3, -929.3],
        ear:    [ 231.3, -868.9],
        marin:  [-767.4,  -21.0],
        or_:    [1928.3,   12.7],
        ivoire: [   0.5,  873.7],
        point:  [ 134.8, -157.6],

        // Repères dans Calque7.png (corps, taille de référence 732 x 858)
        bodyRefSize:  [732, 858],
        bodyPivot:    [360, 800],        // pivot du barrissement (base de la tête)
        eyeCenter:    [392.7, 160.5],    // centre du trou de l'œil
        eyeRadius:    53.5,
        waveOrigin:   [60, 640],         // départ des ondes (devant la défense)

        // Repère dans Oreille.png (taille de référence 815 x 771)
        earRefSize:   [815, 771],
        earPivot:     [40, 600],         // attache de l'oreille côté tête

        pointRise:    60                 // profondeur (px natifs) d'où sort le point
    };

    // Rythme d'écriture : poids relatif de chaque "trait" de feutre.
    // Un poids = une lettre environ ; le stylo marque une micro-pause entre deux.
    var WRITE_RHYTHM = {
        marin:  [1.35, 0.90, 0.70, 0.45, 0.80, 0.35],   // M a r i n '
        or_:    [1.40, 0.80],                           // O r
        ivoire: [0.80, 0.90, 0.85, 0.45, 0.65, 0.95]    // I v o i r e
    };

    // =========================================================================
    // OUTILS
    // =========================================================================

    function normalizeName(name) {
        var s = name;
        try { s = decodeURI(s); } catch (e) {}
        s = s.toLowerCase();
        s = s.replace(/#u00e9/g, "e").replace(/#u00e8/g, "e");
        s = s.replace(/[àâä]/g, "a")
             .replace(/[éèêë]/g, "e")
             .replace(/[îï]/g, "i")
             .replace(/[ôö]/g, "o")
             .replace(/[ùûü]/g, "u");
        s = s.replace(/\.png$/, "");
        return s.replace(/[^a-z0-9]/g, "");
    }

    // Associe un nom de fichier normalisé à une pièce du logo
    function classify(n) {
        if (n === "logo") return null;
        if (/oreille/.test(n)) return "ear";
        if (/ovale|oval|fond/.test(n)) return "oval";
        if (/marin/.test(n)) return "marin";
        if (/ivoire/.test(n)) return "ivoire";
        if (/point/.test(n)) return "point";
        if (/(^|texte)or$/.test(n)) return "or_";
        if (/calque7|corps|elephant/.test(n)) return "body";
        return null;
    }

    var REQUIRED = ["oval", "marin", "or_", "ivoire", "point", "ear", "body"];

    function scanFolder(folder) {
        var found = {};
        if (!folder || !folder.exists) return found;
        var files = folder.getFiles();
        for (var i = 0; i < files.length; i++) {
            var f = files[i];
            if (!(f instanceof File) || !/\.png$/i.test(f.name)) continue;
            var key = classify(normalizeName(f.name));
            if (key && !found[key]) found[key] = f;
        }
        return found;
    }

    function missingKeys(found) {
        var miss = [];
        for (var i = 0; i < REQUIRED.length; i++) {
            if (!found[REQUIRED[i]]) miss.push(REQUIRED[i]);
        }
        return miss;
    }

    function locateFiles() {
        var scriptFolder = null;
        try { scriptFolder = new File($.fileName).parent; } catch (e) {}
        var found = scanFolder(scriptFolder);
        if (missingKeys(found).length === 0) return found;

        var picked = Folder.selectDialog("Sélectionnez le dossier contenant les PNG du logo Marin'Or Ivoire");
        if (!picked) return null;
        found = scanFolder(picked);
        var miss = missingKeys(found);
        if (miss.length) {
            alert("Fichiers introuvables dans le dossier :\n- " + miss.join("\n- "));
            return null;
        }
        return found;
    }

    function importPNG(file, parentFolder) {
        var io = new ImportOptions(file);
        io.importAs = ImportAsType.FOOTAGE;
        io.sequence = false;
        var item = app.project.importFile(io);
        try { item.mainSource.alphaMode = AlphaMode.STRAIGHT; } catch (e) {}
        item.parentFolder = parentFolder;
        return item;
    }

    function parentTo(child, parent) {
        // "WithJump" : on garde les valeurs telles quelles, elles seront
        // définies ensuite directement dans l'espace du parent.
        if (child.setParentWithJump) child.setParentWithJump(parent);
        else child.parent = parent;
    }

    function easeArray(prop, influence) {
        var dims = 1;
        if (prop.propertyValueType === PropertyValueType.TwoD) dims = 2;
        else if (prop.propertyValueType === PropertyValueType.ThreeD) dims = 3;
        var arr = [];
        for (var i = 0; i < dims; i++) arr.push(new KeyframeEase(0, influence));
        return arr;
    }

    /*
     * Pose des clés lissées.
     *   keys = [[temps, valeur, influenceEntrée, influenceSortie], ...]
     *   Les influences (0.1 - 100) sont optionnelles : défaut = defaultInf.
     *   Influence élevée = départ/arrivée plus doux (plus de "poids").
     */
    function animate(prop, keys, defaultInf) {
        var i, idx, inInf, outInf;
        for (i = 0; i < keys.length; i++) prop.setValueAtTime(keys[i][0], keys[i][1]);
        for (i = 0; i < keys.length; i++) {
            idx = prop.nearestKeyIndex(keys[i][0]);
            inInf = (keys[i].length > 2) ? keys[i][2] : defaultInf;
            outInf = (keys[i].length > 3) ? keys[i][3] : inInf;
            prop.setInterpolationTypeAtKey(idx, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
            prop.setTemporalEaseAtKey(idx, easeArray(prop, inInf), easeArray(prop, outInf));
        }
        if (prop.isSpatial) straightenPath(prop);
    }

    // Clés "maintien" (on/off), pour l'affichage des paupières
    function animateHold(prop, keys) {
        for (var i = 0; i < keys.length; i++) {
            var idx = prop.addKey(keys[i][0]);
            prop.setValueAtKey(idx, keys[i][1]);
            prop.setInterpolationTypeAtKey(idx, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
        }
    }

    // Trajectoires de position en ligne droite (pas de boucle auto-Bézier)
    function straightenPath(prop) {
        for (var i = 1; i <= prop.numKeys; i++) {
            try {
                var zero = (prop.keyValue(i).length === 3) ? [0, 0, 0] : [0, 0];
                prop.setSpatialAutoBezierAtKey(i, false);
                prop.setSpatialContinuousAtKey(i, false);
                prop.setSpatialTangentsAtKey(i, zero, zero);
            } catch (e) {}
        }
    }

    function tr(layer, name) {
        return layer.property("ADBE Transform Group").property(name);
    }

    function setAnchor(layer, xy) { tr(layer, "ADBE Anchor Point").setValue(xy); }

    // Place un calque dont on connaît le CENTRE dans l'espace du parent,
    // tout en utilisant un point d'ancrage personnalisé (pivot).
    function placeWithPivot(layer, centerInParent, pivot) {
        var w = layer.source.width, h = layer.source.height;
        setAnchor(layer, pivot);
        tr(layer, "ADBE Position").setValue([
            centerInParent[0] + (pivot[0] - w / 2),
            centerInParent[1] + (pivot[1] - h / 2)
        ]);
    }

    function add(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
    function mul(a, k) { return [a[0] * k, a[1] * k]; }

    function polishLayer(layer) {
        try { layer.quality = LayerQuality.BEST; } catch (e) {}
        try { layer.samplingQuality = LayerSamplingQuality.BICUBIC; } catch (e2) {}
        if (CONFIG.motionBlur) { try { layer.motionBlur = true; } catch (e3) {} }
    }

    // Cercle Bézier à 4 sommets (ordre : gauche, haut, droite, bas)
    function circleShape(c, r) {
        var k = 0.5523 * r;
        var s = new Shape();
        s.vertices    = [[c[0] - r, c[1]], [c[0], c[1] - r], [c[0] + r, c[1]], [c[0], c[1] + r]];
        s.inTangents  = [[0, k], [-k, 0], [0, -k], [k, 0]];
        s.outTangents = [[0, -k], [k, 0], [0, k], [-k, 0]];
        s.closed = true;
        return s;
    }

    // Œil plissé "content" : fente en arc (mêmes 4 sommets que le cercle
    // pour que la morphose cercle -> fente soit propre)
    function squintShape(c, r) {
        var s = new Shape();
        s.vertices    = [[c[0] - 0.95 * r, c[1] + 0.15 * r], [c[0], c[1] - 0.30 * r],
                         [c[0] + 0.95 * r, c[1] + 0.15 * r], [c[0], c[1] - 0.04 * r]];
        s.inTangents  = [[0, 0], [-0.55 * r, 0], [0, 0], [0.50 * r, 0]];
        s.outTangents = [[0, 0], [0.55 * r, 0], [0, 0], [-0.50 * r, 0]];
        s.closed = true;
        return s;
    }

    // Arc ouvert "(" de rayon 100 (onde sonore tournée vers la gauche)
    function arcShape() {
        var s = new Shape();
        s.vertices    = [[-70.7, -70.7], [-100, 0], [-70.7, 70.7]];
        s.inTangents  = [[0, 0], [0, -26.5], [-18.7, -18.7]];
        s.outTangents = [[-18.7, 18.7], [0, 26.5], [0, 0]];
        s.closed = false;
        return s;
    }

    // Effet "écriture au feutre" : Linear Wipe à bord doux et rythme irrégulier
    function writeOn(layer, tStart, tEnd, weights) {
        var fx = layer.property("ADBE Effect Parade").addProperty("ADBE Linear Wipe");
        fx.name = "Ecriture feutre";
        fx.property(2).setValue(CONFIG.writeAngle);     // Wipe Angle
        fx.property(3).setValue(CONFIG.writeFeather);   // Feather

        var total = 0, acc = 0, i;
        for (i = 0; i < weights.length; i++) total += weights[i];
        var keys = [[tStart, 100, 40, 25]];
        for (i = 0; i < weights.length; i++) {
            acc += weights[i];
            var t = tStart + (tEnd - tStart) * (i + 1) / weights.length;
            // micro-pause du stylo entre deux lettres (vitesse nulle sur la clé)
            keys.push([t, 100 - 100 * acc / total, 45, 35]);
        }
        animate(fx.property(1), keys, 40);              // Transition Completion
        layer.inPoint = tStart;
    }

    // =========================================================================
    // PROGRAMME PRINCIPAL
    // =========================================================================
    function main() {
        if (!app.project) app.newProject();

        var files = locateFiles();
        if (!files) return;

        // ---------------------------------------------------------------------
        // Import & organisation du projet
        // ---------------------------------------------------------------------
        var root = app.project.items.addFolder(CONFIG.compName);
        var footFolder = app.project.items.addFolder("PNG Logo");
        footFolder.parentFolder = root;

        var src = {};
        for (var i = 0; i < REQUIRED.length; i++) {
            src[REQUIRED[i]] = importPNG(files[REQUIRED[i]], footFolder);
        }

        var comp = app.project.items.addComp(CONFIG.compName, CONFIG.width, CONFIG.height,
                                             1, CONFIG.duration, CONFIG.fps);
        comp.parentFolder = root;
        comp.bgColor = CONFIG.bgColor;
        comp.motionBlur = CONFIG.motionBlur;

        // Échelle globale : les pièces sont à 100 % dans LOGO_MASTER,
        // c'est le nul maître qui ramène le logo à CONFIG.logoWidth.
        var masterScale = CONFIG.logoWidth / src.oval.width * 100;

        // Facteurs de correction si les PNG n'ont pas la taille de référence
        var bsx = src.body.width / LAYOUT.bodyRefSize[0];
        var bsy = src.body.height / LAYOUT.bodyRefSize[1];
        var esx = src.ear.width / LAYOUT.earRefSize[0];
        var esy = src.ear.height / LAYOUT.earRefSize[1];

        // ---------------------------------------------------------------------
        // Création des calques (du bas vers le haut de la pile)
        // ---------------------------------------------------------------------
        var lOval   = comp.layers.add(src.oval);   lOval.name   = "Fond ovale rouge";
        var lIvoire = comp.layers.add(src.ivoire); lIvoire.name = "Texte Ivoire";
        var lOr     = comp.layers.add(src.or_);    lOr.name     = "Texte Or";
        var lPoint  = comp.layers.add(src.point);  lPoint.name  = "Point doré";   // sous "Marin'" : il sort du i
        var lMarin  = comp.layers.add(src.marin);  lMarin.name  = "Texte Marin'";
        var lEar    = comp.layers.add(src.ear);    lEar.name    = "Oreille dorée";

        var waves = [];
        if (CONFIG.soundWaves) {
            for (i = 0; i < 3; i++) {
                var w = comp.layers.addShape();
                w.name = "Onde sonore " + (i + 1);
                waves.push(w);
            }
        }

        var lBody = comp.layers.add(src.body);     lBody.name   = "Corps éléphant";

        var eyeR = LAYOUT.eyeRadius * Math.min(bsx, bsy);
        var lidSize = Math.ceil(eyeR * 2.7);
        var lLids = comp.layers.addSolid([1, 1, 1], "Paupières (squint)", lidSize, lidSize, 1, CONFIG.duration);

        var nElephant = comp.layers.addNull(CONFIG.duration); nElephant.name = "ELEPHANT_CTRL";
        var nMaster   = comp.layers.addNull(CONFIG.duration); nMaster.name   = "LOGO_MASTER";

        // ---------------------------------------------------------------------
        // Hiérarchie (parentage)
        // ---------------------------------------------------------------------
        parentTo(nElephant, nMaster);
        parentTo(lBody, nElephant);
        parentTo(lEar, lBody);
        parentTo(lLids, lBody);
        for (i = 0; i < waves.length; i++) parentTo(waves[i], lBody);
        parentTo(lMarin, nMaster);
        parentTo(lOr, nMaster);
        parentTo(lIvoire, nMaster);
        parentTo(lPoint, nMaster);
        parentTo(lOval, nMaster);

        var all = [lOval, lIvoire, lOr, lPoint, lMarin, lEar, lBody, lLids];
        for (i = 0; i < all.length; i++) polishLayer(all[i]);
        for (i = 0; i < waves.length; i++) polishLayer(waves[i]);

        // ---------------------------------------------------------------------
        // Mise en place statique (logo final)
        // ---------------------------------------------------------------------
        setAnchor(nMaster, [0, 0]);
        tr(nMaster, "ADBE Position").setValue(CONFIG.logoCenter);
        tr(nMaster, "ADBE Scale").setValue([masterScale, masterScale, 100]);

        // Centre du groupe éléphant (corps + oreille) dans l'espace du logo
        var bW = src.body.width, bH = src.body.height, eW = src.ear.width, eH = src.ear.height;
        var gx0 = Math.min(LAYOUT.body[0] - bW / 2, LAYOUT.ear[0] - eW / 2);
        var gx1 = Math.max(LAYOUT.body[0] + bW / 2, LAYOUT.ear[0] + eW / 2);
        var gy0 = Math.min(LAYOUT.body[1] - bH / 2, LAYOUT.ear[1] - eH / 2);
        var gy1 = Math.max(LAYOUT.body[1] + bH / 2, LAYOUT.ear[1] + eH / 2);
        var groupCenter = [(gx0 + gx1) / 2, (gy0 + gy1) / 2];
        var groupHeight = gy1 - gy0;

        setAnchor(nElephant, [0, 0]);
        tr(nElephant, "ADBE Position").setValue(groupCenter);

        // Corps : centre relatif au groupe, ancre sur le pivot du barrissement
        var bodyPivot = [LAYOUT.bodyPivot[0] * bsx, LAYOUT.bodyPivot[1] * bsy];
        placeWithPivot(lBody, add(LAYOUT.body, mul(groupCenter, -1)), bodyPivot);

        // Oreille : centre exprimé en pixels du corps (elle suit le corps au pixel près)
        var earCenterInBody = add([bW / 2, bH / 2], add(LAYOUT.ear, mul(LAYOUT.body, -1)));
        placeWithPivot(lEar, earCenterInBody, [LAYOUT.earPivot[0] * esx, LAYOUT.earPivot[1] * esy]);

        // Textes, point et ovale (centrés sur leur position finale)
        tr(lMarin, "ADBE Position").setValue(LAYOUT.marin);
        tr(lOr, "ADBE Position").setValue(LAYOUT.or_);
        tr(lIvoire, "ADBE Position").setValue(LAYOUT.ivoire);
        tr(lOval, "ADBE Position").setValue([0, 0]);

        // Marqueurs de compo pour repérer les séquences
        try {
            comp.markerProperty.setValueAtTime(TIMING.introStart, new MarkerValue("1. Apparition & barrit"));
            comp.markerProperty.setValueAtTime(TIMING.shrinkStart, new MarkerValue("2. Repliement & texte"));
            comp.markerProperty.setValueAtTime(TIMING.pointStart, new MarkerValue("3. Point doré & ovale"));
        } catch (eM) {}

        // =====================================================================
        // 1. APPARITION & BARRISSEMENT DE L'ÉLÉPHANT  (0.0 s - 1.8 s)
        // =====================================================================

        // --- 1a. Apparition en GRAND au centre ------------------------------
        // Échelle du contrôleur pour que l'éléphant fasse ~elephantIntroHeight px
        var introScale = CONFIG.elephantIntroHeight / (groupHeight * masterScale / 100) * 100;
        var introPos = [0, CONFIG.elephantIntroOffsetY / (masterScale / 100)];
        var sElephant = tr(nElephant, "ADBE Scale");
        var pElephant = tr(nElephant, "ADBE Position");

        animate(sElephant, [
            [TIMING.introStart,        [introScale * 0.70,  introScale * 0.70,  100], 33, 10],
            [TIMING.introStart + 0.24, [introScale * 1.05,  introScale * 1.05,  100], 50],
            [TIMING.introStart + 0.40, [introScale * 0.985, introScale * 0.985, 100], 50],
            [TIMING.introEnd,          [introScale,         introScale,         100], 70],
            // --- (2) recul : petite anticipation puis retour à 100 % ---
            [TIMING.shrinkStart,        [introScale,        introScale,        100], 60],
            [TIMING.shrinkStart + 0.12, [introScale * 1.04, introScale * 1.04, 100], 45, 25],
            [TIMING.shrinkLand,         [97, 97, 100], 85, 50],
            [TIMING.shrinkLand + 0.14,  [101.5, 101.5, 100], 50],
            [TIMING.shrinkSettle,       [100, 100, 100], 70]
        ], 50);

        animate(pElephant, [
            [TIMING.introStart,         introPos, 50],
            [TIMING.shrinkStart + 0.12, introPos, 30, 25],
            [TIMING.shrinkLand,         groupCenter, 85]
        ], 50);

        // Fondu d'entrée rapide (l'opacité ne se transmet pas par parentage)
        animate(tr(lBody, "ADBE Opacity"), [[TIMING.introStart, 0], [TIMING.introStart + 0.16, 100]], 40);
        animate(tr(lEar, "ADBE Opacity"),  [[TIMING.introStart, 0], [TIMING.introStart + 0.16, 100]], 40);

        // --- 1b. Barrissement : anticipation, tête levée, tremblement --------
        // Rotation positive = horaire = la trompe (à gauche) se lève.
        var rBody = tr(lBody, "ADBE Rotate Z");
        animate(rBody, [
            [TIMING.trumpetStart,          0],
            [TIMING.trumpetStart + 0.15,  -4],    // anticipation : la tête plonge
            [TIMING.trumpetPeak,          11],    // BARRIT
            [TIMING.trumpetHoldEnd,        9],
            [TIMING.trumpetEnd - 0.16,    -2],    // léger dépassement au retour
            [TIMING.trumpetEnd,            0]
        ], 55);

        animate(tr(lBody, "ADBE Scale"), [
            [TIMING.trumpetStart,         [100, 100, 100]],
            [TIMING.trumpetStart + 0.15,  [103,  96, 100]],   // compression
            [TIMING.trumpetPeak,          [ 96, 106, 100]],   // étirement
            [TIMING.trumpetHoldEnd,       [ 97, 104, 100]],
            [TIMING.trumpetEnd - 0.16,    [101.5, 98.5, 100]],
            [TIMING.trumpetEnd,           [100, 100, 100]]
        ], 55);

        // Tremblement de la voix pendant le barrit (modifiable dans l'expression)
        rBody.expression =
            "// Tremblement du barrit\n" +
            "var t1 = " + TIMING.trumpetPeak + ", t2 = " + TIMING.trumpetHoldEnd + ";\n" +
            "var amp = 1.6, freq = 22;\n" +
            "var env = linear(time, t1, t1 + 0.08, 0, 1) * linear(time, t2 - 0.12, t2, 1, 0);\n" +
            "value + env * amp * (0.6 * Math.sin(time * freq * 2 * Math.PI) + 0.4 * Math.sin(time * freq * 1.7 * 2 * Math.PI));";

        // --- 1c. Yeux plissés (squint) puis réouverture ----------------------
        // Le trou de l'œil est recouvert par un solide blanc dont le masque
        // "Soustraire" passe d'un cercle (œil ouvert) à une fente en arc.
        var eyeCenter = [LAYOUT.eyeCenter[0] * bsx, LAYOUT.eyeCenter[1] * bsy];
        var lidC = [lidSize / 2, lidSize / 2];
        setAnchor(lLids, lidC);
        tr(lLids, "ADBE Position").setValue(eyeCenter);

        var masks = lLids.property("ADBE Mask Parade");
        var mCover = masks.addProperty("ADBE Mask Atom");
        mCover.name = "Couverture";
        mCover.maskMode = MaskMode.ADD;
        mCover.property("ADBE Mask Shape").setValue(circleShape(lidC, eyeR * 1.25));

        var mEye = masks.addProperty("ADBE Mask Atom");
        mEye.name = "Fente de l'oeil";
        mEye.maskMode = MaskMode.SUBTRACT;
        mEye.property("ADBE Mask Feather").setValue([1, 1]);
        var eyeOpenShape = circleShape(lidC, eyeR + 1.5);
        var eyeSquintShape = squintShape(lidC, eyeR);
        animate(mEye.property("ADBE Mask Shape"), [
            [TIMING.squintStart,     eyeOpenShape],
            [TIMING.squintClosed,    eyeSquintShape, 70],
            [TIMING.eyesReopenStart, eyeSquintShape],
            [TIMING.eyesOpen,        eyeOpenShape, 75]
        ], 60);

        animateHold(tr(lLids, "ADBE Opacity"), [
            [0, 0],
            [TIMING.squintStart, 100],
            [TIMING.eyesOpen + 1 / CONFIG.fps, 0]
        ]);

        // --- 1d. Oreille : ondulation souple qui se stabilise vite ----------
        var rEar = tr(lEar, "ADBE Rotate Z");
        animate(rEar, [
            [TIMING.earStart,          0],
            [TIMING.earStart + 0.25,  -7],
            [TIMING.earStart + 0.50,   5],
            [TIMING.earStart + 0.73,  -3],
            [TIMING.earStart + 0.93,   1.5],
            [TIMING.earStart + 1.11,  -0.5],
            [TIMING.earSettle,         0],
            // traîne pendant le recul (follow-through)
            [TIMING.shrinkStart + 0.05, 0],
            [TIMING.shrinkStart + 0.30, -4],
            [TIMING.shrinkLand + 0.06,   2],
            [TIMING.shrinkSettle + 0.05, 0]
        ], 60);

        // --- 1e. Ondes sonores dorées (optionnel) ---------------------------
        var waveOrigin = [LAYOUT.waveOrigin[0] * bsx, LAYOUT.waveOrigin[1] * bsy];
        for (i = 0; i < waves.length; i++) {
            var wl = waves[i];
            var grp = wl.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
            grp.name = "Arc";
            var gc = grp.property("ADBE Vectors Group");
            gc.addProperty("ADBE Vector Shape - Group").property("ADBE Vector Shape").setValue(arcShape());
            var stroke = gc.addProperty("ADBE Vector Graphic - Stroke");
            stroke.property("ADBE Vector Stroke Color").setValue(CONFIG.gold);
            stroke.property("ADBE Vector Stroke Line Cap").setValue(2);   // bout arrondi

            setAnchor(wl, [0, 0]);
            tr(wl, "ADBE Position").setValue(waveOrigin);
            tr(wl, "ADBE Rotate Z").setValue(-12);

            var w0 = TIMING.trumpetPeak + i * 0.13;
            var w1 = w0 + 0.42;
            animate(tr(wl, "ADBE Scale"), [[w0, [40, 40, 100], 10, 20], [w1, [230, 230, 100], 70]], 50);
            animate(stroke.property("ADBE Vector Stroke Width"), [[w0, 16], [w1, 6]], 50);
            animate(tr(wl, "ADBE Opacity"), [[w0, 0], [w0 + 0.07, 100, 30], [w1, 0, 60]], 40);
            wl.inPoint = w0;
            wl.outPoint = w1 + 1 / CONFIG.fps;
        }

        // =====================================================================
        // 2. REPLIEMENT DU LOGO & ÉCRITURE DU TEXTE  (1.8 s - 3.2 s)
        // =====================================================================
        // Le recul de l'éléphant est posé plus haut sur ELEPHANT_CTRL
        // (clés à partir de TIMING.shrinkStart). Corps + oreille + paupières
        // étant parentés, ils rétrécissent ensemble sans aucun décalage.

        writeOn(lMarin,  TIMING.marinStart,  TIMING.marinEnd,  WRITE_RHYTHM.marin);
        writeOn(lOr,     TIMING.orStart,     TIMING.orEnd,     WRITE_RHYTHM.or_);
        writeOn(lIvoire, TIMING.ivoireStart, TIMING.ivoireEnd, WRITE_RHYTHM.ivoire);

        // =====================================================================
        // 3. POP DU POINT DORÉ & FOND OVALE  (3.2 s - 4.5 s)
        // =====================================================================

        // --- 3a. Point du "i" : pop élastique type slime --------------------
        // Ancre en bas du point : il s'écrase sur le i et s'étire vers le haut.
        var pW = src.point.width, pH = src.point.height;
        setAnchor(lPoint, [pW / 2, pH]);
        var pFinal = add(LAYOUT.point, [0, pH / 2]);
        var pRise = LAYOUT.pointRise;
        var t = TIMING.pointStart, d = TIMING.pointEnd - TIMING.pointStart;

        animate(tr(lPoint, "ADBE Position"), [
            [t,              add(pFinal, [0, pRise]), 20],
            [t + d * 0.18,   add(pFinal, [0, -pH * 0.30]), 60],    // jaillit au-dessus
            [t + d * 0.36,   pFinal, 70],                           // retombe
            [t + d * 0.52,   add(pFinal, [0, -pH * 0.06]), 50],     // petit rebond
            [t + d * 0.68,   pFinal, 60]
        ], 50);

        animate(tr(lPoint, "ADBE Scale"), [
            [t,              [  0,   0, 100], 20],
            [t + d * 0.18,   [ 60, 145, 100], 45],   // stretch (étiré en sortant)
            [t + d * 0.36,   [138,  68, 100], 55],   // squash (écrasé à l'impact)
            [t + d * 0.52,   [ 86, 117, 100], 50],
            [t + d * 0.68,   [108,  94, 100], 50],
            [t + d * 0.84,   [ 97, 103, 100], 50],
            [t + d,          [100, 100, 100], 70]
        ], 50);
        lPoint.inPoint = t;

        // --- 3b. Fond ovale rouge : apparition douce ------------------------
        animate(tr(lOval, "ADBE Opacity"), [
            [TIMING.ovalStart, 0, 50, 40],
            [TIMING.ovalStart + 0.70, 100, 70]
        ], 50);
        animate(tr(lOval, "ADBE Scale"), [
            [TIMING.ovalStart,        [ 92,  92, 100], 50, 30],
            [TIMING.ovalEnd - 0.30,   [100.8, 100.8, 100], 60],
            [TIMING.ovalEnd,          [100, 100, 100], 75]
        ], 50);
        lOval.inPoint = TIMING.ovalStart;

        // ---------------------------------------------------------------------
        // Finitions
        // ---------------------------------------------------------------------
        nMaster.label = 11;
        nElephant.label = 11;
        lLids.label = 2;
        comp.time = 0;
        comp.openInViewer();
    }

    app.beginUndoGroup("Marin'Or Ivoire - Animation du logo");
    try {
        main();
    } catch (err) {
        alert("Erreur pendant la création de l'animation :\n" + err.toString() +
              (err.line ? "\n(ligne " + err.line + ")" : ""));
    }
    app.endUndoGroup();

})();
