/*
 * =============================================================================
 *  MARIN'OR IVOIRE - ANIMATION DU PACKSHOT (fond transparent)
 *  Script After Effects (ExtendScript .jsx)
 * =============================================================================
 *
 *  Utilisation :
 *    Fichier > Scripts > Exécuter le fichier de script...  ->  ce fichier
 *
 *  Le script cherche les PNG dans son dossier, sinon il demande le dossier.
 *  Fichiers attendus :
 *    - slogan.png      ("Le goût en or")
 *    - commandez.png   (bouton "Commandez dès maintenant")
 *    - Calque 1.png    (filet noir de séparation)
 *    - infos.png       (téléphone - site - réseaux sociaux)
 *
 *  Animation : chaque élément monte rapidement du bas vers le haut (fondu +
 *  arrivée amortie), en cascade du bas de l'écran vers le haut.
 *  La compo est sans fond et déjà ajoutée à la file d'attente de rendu avec
 *  un module de sortie qui garde la couche alpha (RVB + Alpha).
 *
 *  Pour tout ajuster : blocs CONFIG, LAYOUT et TIMING ci-dessous.
 * =============================================================================
 */

(function MarinOrPackshotAnimation() {

    // =========================================================================
    // 0. CONFIGURATION
    // =========================================================================
    var CONFIG = {
        compName: "Marin'Or Ivoire - Packshot Anim",
        width: 1920,
        height: 1080,
        fps: 60,
        duration: 3,
        motionBlur: true,
        addToRenderQueue: true          // ajoute la compo au rendu avec alpha
    };

    // =========================================================================
    // 0b. LAYOUT - centre de chaque PNG dans la compo (px), échelle en %
    //     Par défaut, le bloc occupe le bas de l'image et laisse le haut
    //     libre pour le logo et le produit.
    // =========================================================================
    var LAYOUT = {
        slogan:    { pos: [960, 598.5],  scale: 100 },
        commandez: { pos: [960, 806.5],  scale: 100 },
        ligne:     { pos: [960, 940],    scale: 100 },
        infos:     { pos: [960, 1001.5], scale: 100 }
    };

    // =========================================================================
    // 0c. TIMING (secondes)
    // =========================================================================
    var TIMING = {
        start:    0.00,     // début de la première entrée
        stagger:  0.09,     // décalage entre deux éléments
        rise:     0.50,     // durée de la montée d'un élément
        distance: 140,      // hauteur de départ sous la position finale (px)
        // Ordre de la cascade : du bas de l'écran vers le haut
        order: ["infos", "ligne", "commandez", "slogan"]
    };

    // =========================================================================
    // OUTILS
    // =========================================================================

    function normalizeName(name) {
        var s = name;
        try { s = decodeURI(s); } catch (e) {}
        s = s.toLowerCase().replace(/\.png$/, "");
        return s.replace(/[^a-z0-9]/g, "");
    }

    function classify(n) {
        if (/slogan|gout/.test(n)) return "slogan";
        if (/commande|bouton|cta/.test(n)) return "commandez";
        if (/infos?|contact/.test(n)) return "infos";
        if (/calque1|ligne|filet|trait/.test(n)) return "ligne";
        return null;
    }

    var REQUIRED = ["slogan", "commandez", "ligne", "infos"];

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

        var picked = Folder.selectDialog("Sélectionnez le dossier contenant les PNG du packshot");
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
     *   Sortie faible = départ rapide ; entrée forte = arrivée amortie.
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
        if (prop.isSpatial) {
            for (i = 1; i <= prop.numKeys; i++) {
                try {
                    var zero = (prop.keyValue(i).length === 3) ? [0, 0, 0] : [0, 0];
                    prop.setSpatialAutoBezierAtKey(i, false);
                    prop.setSpatialContinuousAtKey(i, false);
                    prop.setSpatialTangentsAtKey(i, zero, zero);
                } catch (e) {}
            }
        }
    }

    function tr(layer, name) {
        return layer.property("ADBE Transform Group").property(name);
    }

    function polishLayer(layer) {
        try { layer.quality = LayerQuality.BEST; } catch (e) {}
        try { layer.samplingQuality = LayerSamplingQuality.BICUBIC; } catch (e2) {}
        if (CONFIG.motionBlur) { try { layer.motionBlur = true; } catch (e3) {} }
    }

    // Montée rapide du bas vers le haut, avec fondu et arrivée amortie
    function riseIn(layer, layout, t0) {
        var p = layout.pos, s = layout.scale, d = TIMING.distance, r = TIMING.rise;
        animate(tr(layer, "ADBE Position"), [
            [t0,           [p[0], p[1] + d], 10, 12],     // départ vif
            [t0 + r * 0.8, [p[0], p[1] - 4], 75, 40],     // léger dépassement
            [t0 + r,       p, 70]                          // se pose
        ], 50);
        animate(tr(layer, "ADBE Opacity"), [
            [t0, 0, 10, 20],
            [t0 + r * 0.45, 100, 60]
        ], 50);
        tr(layer, "ADBE Scale").setValue([s, s, 100]);
        layer.inPoint = t0;
    }

    // =========================================================================
    // PROGRAMME PRINCIPAL
    // =========================================================================
    function main() {
        if (!app.project) app.newProject();

        var files = locateFiles();
        if (!files) return;

        var root = app.project.items.addFolder(CONFIG.compName);
        var footFolder = app.project.items.addFolder("PNG Packshot");
        footFolder.parentFolder = root;

        var comp = app.project.items.addComp(CONFIG.compName, CONFIG.width, CONFIG.height,
                                             1, CONFIG.duration, CONFIG.fps);
        comp.parentFolder = root;
        comp.motionBlur = CONFIG.motionBlur;

        // ---------------------------------------------------------------------
        // Calques (sans aucun fond : la compo reste transparente)
        // ---------------------------------------------------------------------
        var names = {
            slogan: "Slogan - Le goût en or",
            commandez: "Bouton - Commandez",
            ligne: "Filet",
            infos: "Infos contact"
        };
        var layers = {};
        for (var i = 0; i < REQUIRED.length; i++) {
            var key = REQUIRED[i];
            var l = comp.layers.add(importPNG(files[key], footFolder));
            l.name = names[key];
            polishLayer(l);
            tr(l, "ADBE Position").setValue(LAYOUT[key].pos);
            layers[key] = l;
        }

        // =====================================================================
        // ANIMATION : cascade du bas vers le haut
        // =====================================================================
        for (i = 0; i < TIMING.order.length; i++) {
            var k = TIMING.order[i];
            riseIn(layers[k], LAYOUT[k], TIMING.start + i * TIMING.stagger);
        }

        // --- Filet : il s'étire aussi depuis le centre ----------------------
        var tLine = TIMING.start + TIMING.stagger * indexOf(TIMING.order, "ligne");
        var ls = LAYOUT.ligne.scale;
        animate(tr(layers.ligne, "ADBE Scale"), [
            [tLine,                    [0, ls, 100], 10, 15],
            [tLine + TIMING.rise * 1.2, [ls, ls, 100], 80]
        ], 50);

        // --- Bouton : petit "pop" d'appel à l'action à l'arrivée -----------
        var tBtn = TIMING.start + TIMING.stagger * indexOf(TIMING.order, "commandez") + TIMING.rise;
        var bs = LAYOUT.commandez.scale;
        animate(tr(layers.commandez, "ADBE Scale"), [
            [tBtn - 0.05, [bs, bs, 100]],
            [tBtn + 0.10, [bs * 1.05, bs * 1.05, 100], 45],
            [tBtn + 0.28, [bs, bs, 100], 70]
        ], 50);

        // ---------------------------------------------------------------------
        // File d'attente de rendu avec couche alpha
        // ---------------------------------------------------------------------
        if (CONFIG.addToRenderQueue) {
            try {
                var rq = app.project.renderQueue.items.add(comp);
                var om = rq.outputModule(1);
                var templates = ["High Quality with Alpha", "Haute qualité avec alpha",
                                 "Lossless with Alpha", "Sans perte avec alpha"];
                for (i = 0; i < templates.length; i++) {
                    try { om.applyTemplate(templates[i]); break; } catch (eT) {}
                }
            } catch (eRQ) {}
        }

        comp.time = 0;
        comp.openInViewer();
    }

    function indexOf(arr, v) {
        for (var i = 0; i < arr.length; i++) if (arr[i] === v) return i;
        return -1;
    }

    app.beginUndoGroup("Marin'Or Ivoire - Animation packshot");
    try {
        main();
    } catch (err) {
        alert("Erreur pendant la création de l'animation :\n" + err.toString() +
              (err.line ? "\n(ligne " + err.line + ")" : ""));
    }
    app.endUndoGroup();

})();
