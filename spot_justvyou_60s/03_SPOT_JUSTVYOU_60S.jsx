/*
 * =====================================================================
 *  03_SPOT_JUSTVYOU_60S.jsx
 *  Spot publicitaire 2D motion design « Justvyou Property » — 60 s
 * ---------------------------------------------------------------------
 *  Exécution : After Effects > Fichier > Scripts > Exécuter le fichier script...
 *  Compatibilité visée : After Effects CC 2019 (v16) et versions ultérieures.
 *
 *  Placez ce fichier à côté du dossier « assets/ » livré avec lui :
 *    assets/logo_justvyou.png   logo complet (fond transparent)
 *    assets/logo_symbole.png    symbole circulaire seul
 *    assets/logo_texte.png      logotype « JustVyou Property » seul
 *    assets/audio/voix_off.wav  (facultatif) voix off enregistrée
 *    assets/audio/musique.wav   (facultatif) musique
 *  Si ces fichiers manquent, le script continue : logo vectoriel de repli,
 *  dossier 03_AUDIO laissé vide. Tout est signalé dans le rapport final.
 *
 *  CE QUE LE SCRIPT AUTOMATISE
 *   - Composition SPOT_JUSTVYOU_60S (1920×1080, 30 i/s, 60 s) et quatre
 *     pré-compositions de scène (15 s + 20 s + 15 s + 10 s = 60 s).
 *   - Dossiers 01_COMPS, 02_ASSETS, 03_AUDIO, 04_ADJUSTMENTS.
 *   - Solides d'arrière-plan avec effet Dégradé et grain animé par expression.
 *   - Calques texte (Larsseit, ou Montserrat de repli) et animations d'entrée
 *     pop-up, fondu, slide et cascade, toutes pilotées par expressions.
 *   - Maisons, clé, contrat, graphique, immeuble et pictogrammes de contact
 *     en calques de forme, avec ombres portées teintées violet/bleu.
 *   - Logo animé (symbole qui tourne, logotype qui glisse, reflet lumineux).
 *   - Transitions entre scènes (volets or/bleu, iris or).
 *   - Calque d'ajustement final : Lueur, Bruit (grain), aberration
 *     chromatique (si le plug-in est installé) et étalonnage léger.
 *   - Marqueurs de scène, marqueurs de voix off, guides de composition et
 *     calque guide des zones de sécurité.
 *   - Styles de calque (Incrustation en dégradé « Réfléchi » + Lueur interne)
 *     appliqués au mieux via les commandes de menu.
 *
 *  CE QUI RESTE À FAIRE À LA MAIN (voir README.md)
 *   - Personnages : les repères rouges « À ANIMER » sont des calques guides,
 *     non rendus. Dessin, stretch & squash, clignements, sourires, gestuelle,
 *     marche et mouvements de tête se font à la main à partir du storyboard.
 *   - Masques adoucis, rim lights sur la peau, couleurs des styles de calque
 *     (les couleurs d'un dégradé ne sont pas scriptables).
 *   - Enregistrement de la voix off, musique, mixage, rendu final.
 * =====================================================================
 */

(function spotJustvyou60s() {

    // =================================================================
    // 0. PARAMÈTRES GÉNÉRAUX
    // =================================================================
    var CONFIG = {
        nomComp: "SPOT_JUSTVYOU_60S",
        largeur: 1920,
        hauteur: 1080,
        fps: 30,
        duree: 60,
        dossiers: {
            comps: "01_COMPS",
            assets: "02_ASSETS",
            audio: "03_AUDIO",
            ajust: "04_ADJUSTMENTS"
        },
        // Tente d'appliquer Incrustation en dégradé + Lueur interne par les menus.
        // Mettre false si votre version d'After Effects réagit mal.
        stylesDeCalque: true,
        dossierAssets: "assets"
    };

    var W = CONFIG.largeur;
    var H = CONFIG.hauteur;

    var RAPPORT = [];          // lignes du rapport affiché en fin de script
    var F = {};                // dossiers du projet
    var POLICES = {};          // xb = ExtraBold, b = Bold, r = Regular
    var NOM_POLICE = "";
    var LOGO = { complet: null, symbole: null, texte: null };
    var STATS = { tailleMin: 1000, styles: 0, stylesEchecs: 0 };
    var CMD_STYLES = null;

    // Dossier du script (pour retrouver assets/)
    var DOSSIER_SCRIPT = (function () {
        try {
            return (new File($.fileName)).parent.fsName;
        } catch (e) {
            return Folder.desktop.fsName;
        }
    })();

    // -----------------------------------------------------------------
    // Couleurs de la charte (codes fournis, non modifiés)
    // -----------------------------------------------------------------
    function hex(h) {
        return [
            parseInt(h.substr(0, 2), 16) / 255,
            parseInt(h.substr(2, 2), 16) / 255,
            parseInt(h.substr(4, 2), 16) / 255
        ];
    }

    // Mélange linéaire de deux couleurs (k = 0 → c1, k = 1 → c2)
    function melange(c1, c2, k) {
        return [
            c1[0] + (c2[0] - c1[0]) * k,
            c1[1] + (c2[1] - c1[1]) * k,
            c1[2] + (c2[2] - c1[2]) * k
        ];
    }

    var C = {};
    C.BLEU = hex("114491");                       // confiance, sécurité
    C.OR = hex("F7B819");                         // prestige, prospérité
    C.BLANC = [1, 1, 1];                          // fond et respiration
    // Nuances dérivées UNIQUEMENT des couleurs de la charte (pour les dégradés)
    C.BLEU_NUIT = melange(C.BLEU, [0, 0, 0], 0.35);  // bleu assombri
    C.OR_PALE = melange(C.OR, C.BLANC, 0.85);        // or éclairci
    C.BLEU_PALE = melange(C.BLEU, C.BLANC, 0.92);    // bleu éclairci
    // Ombres portées teintées violet/bleu (demandées par le brief)
    C.OMBRE = hex("2F2370");
    // Couleur des repères « À ANIMER » (calques guides, jamais rendus)
    C.REPERE = [0.95, 0.2, 0.25];

    // -----------------------------------------------------------------
    // Découpage temporel : source unique de vérité (secondes)
    // -----------------------------------------------------------------
    var SCENES = [
        { nom: "SC01_CLIENT_PERDU", titre: "Scène 1 — Le client perdu face aux offres confuses", debut: 0, fin: 15 },
        { nom: "SC02_DECOUVERTE_SERVICES", titre: "Scène 2 — Justvyou Property et ses trois services", debut: 15, fin: 35 },
        { nom: "SC03_FAMILLE_SATISFAITE", titre: "Scène 3 — Famille satisfaite dans un logement moderne", debut: 35, fin: 50 },
        { nom: "SC04_LOGO_CONTACTS", titre: "Scène 4 — Logo, slogan, contacts et réseaux", debut: 50, fin: 60 }
    ];

    // Voix off : mêmes timecodes que 01_script_voix_off.md
    var VO = [
        { debut: 0.5, fin: 4.0, texte: "Trouver un logement à Abidjan…" },
        { debut: 4.0, fin: 9.0, texte: "Des annonces partout, des prix flous, des visites qui ne mènent à rien." },
        { debut: 9.0, fin: 12.3, texte: "Trop d'offres, trop de doutes." },
        { debut: 12.3, fin: 14.8, texte: "Et si vous pouviez enfin faire confiance ?" },
        { debut: 15.3, fin: 19.0, texte: "Voici Justvyou Property, votre agence immobilière à Abidjan." },
        { debut: 19.0, fin: 24.0, texte: "Vente : des biens vérifiés et des documents contrôlés." },
        { debut: 24.0, fin: 29.0, texte: "Location : des logements visités pour vous et des contrats clairs." },
        { debut: 29.0, fin: 34.5, texte: "Gestion : nous suivons vos loyers et entretenons votre bien, en toute transparence." },
        { debut: 35.3, fin: 40.0, texte: "Aujourd'hui, cette famille est chez elle, dans un logement moderne." },
        { debut: 40.0, fin: 45.0, texte: "Clés en main, dossier clair, et un conseiller toujours joignable." },
        { debut: 45.0, fin: 49.5, texte: "Acheter, louer ou investir : avancez l'esprit tranquille." },
        { debut: 50.6, fin: 52.6, texte: "Justvyou Property." },
        { debut: 53.3, fin: 55.3, texte: "Trouvez mieux. Vivez mieux." },
        { debut: 55.6, fin: 59.4, texte: "Appelez-nous au 05 55 58 07 24." }
    ];

    // Coordonnées affichées en scène 4 (issues des supports du mémoire)
    var CONTACT = {
        tel: "(+225) 05 55 58 07 24",
        web: "www.justvyou-property.ci",
        mail: "contact@justvyou-property.ci",
        reseaux: "@justvyouproperty",
        lieu: "Zone 4 · Abidjan"
    };

    var NBSP = " "; // espace insécable avant « ? » et « : »

    // =================================================================
    // 1. UTILITAIRES
    // =================================================================

    function note(msg) {
        RAPPORT.push(msg);
    }

    // Arrondi pour écrire des nombres propres dans les expressions
    function n(x) {
        return String(Math.round(x * 1000) / 1000);
    }

    // Timecode mm:ss pour les libellés
    function tc(sec) {
        var m = Math.floor(sec / 60);
        var s = Math.floor(sec - m * 60);
        return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
    }

    // Cherche une propriété par une liste d'identifiants
    // (matchName d'abord, puis noms affichés anglais et français)
    function prop(groupe, ids) {
        for (var i = 0; i < ids.length; i++) {
            try {
                var p = groupe.property(ids[i]);
                if (p !== null && p !== undefined) {
                    return p;
                }
            } catch (e) {}
        }
        return null;
    }

    function regler(groupe, ids, valeur, libelle) {
        var p = prop(groupe, ids);
        if (!p) {
            note("[!] Paramètre introuvable : " + libelle);
            return false;
        }
        try {
            p.setValue(valeur);
            return true;
        } catch (e) {
            note("[!] Réglage impossible (" + libelle + ") : " + e.toString());
            return false;
        }
    }

    // Règle une valeur en pourcentage, quelle que soit l'échelle interne
    // (certains effets stockent 0–255 au lieu de 0–100)
    function reglerPct(groupe, ids, pct, libelle) {
        var p = prop(groupe, ids);
        if (!p) {
            note("[!] Paramètre introuvable : " + libelle);
            return false;
        }
        var v = pct;
        try {
            if (p.hasMax && p.maxValue > 100.5) {
                v = pct * p.maxValue / 100;
            }
        } catch (e) {}
        try {
            p.setValue(v);
            return true;
        } catch (e2) {
            note("[!] Réglage impossible (" + libelle + ") : " + e2.toString());
            return false;
        }
    }

    // Variante silencieuse (styles de calque : noms variables selon les versions)
    function reglerDiscret(groupe, ids, valeur, enPct) {
        var p = prop(groupe, ids);
        if (!p) {
            return false;
        }
        var v = valeur;
        try {
            if (enPct && p.hasMax && p.maxValue > 100.5) {
                v = valeur * p.maxValue / 100;
            }
            p.setValue(v);
            return true;
        } catch (e) {
            return false;
        }
    }

    function expression(p, code, libelle) {
        if (!p) {
            note("[!] Expression non posée (propriété absente) : " + libelle);
            return false;
        }
        try {
            p.expression = code;
            return true;
        } catch (e) {
            note("[!] Expression refusée (" + libelle + ") : " + e.toString());
            return false;
        }
    }

    // Accès rapide aux propriétés de transformation d'un calque
    function tr(calque, matchName) {
        return calque.property("ADBE Transform Group").property(matchName);
    }

    function temps(calque, entree, sortie) {
        calque.inPoint = entree;
        calque.outPoint = sortie;
    }

    // Boîte englobante d'un calque (texte : sans contours ; formes : avec)
    function mesure(calque) {
        return calque.sourceRectAtTime(calque.inPoint, !(calque instanceof TextLayer));
    }

    // Place le point d'ancrage au centre, à gauche ou en bas de la boîte
    function ancre(calque, mode) {
        var r = mesure(calque);
        var ax = r.left + r.width / 2;
        var ay = r.top + r.height / 2;
        if (mode === "gauche") {
            ax = r.left;
        }
        if (mode === "bas") {
            ay = r.top + r.height;
        }
        tr(calque, "ADBE Anchor Point").setValue([ax, ay]);
        return r;
    }

    // Recherche ou création d'un dossier à la racine du projet
    function dossier(nom) {
        var racine = app.project.rootFolder;
        for (var i = 1; i <= racine.numItems; i++) {
            var it = racine.item(i);
            if (it instanceof FolderItem && it.name === nom) {
                return it;
            }
        }
        return app.project.items.addFolder(nom);
    }

    // Importe un fichier du dossier assets/ (null s'il n'existe pas)
    function importer(cheminRelatif, dossierCible) {
        var f = new File(DOSSIER_SCRIPT + "/" + CONFIG.dossierAssets + "/" + cheminRelatif);
        if (!f.exists) {
            return null;
        }
        try {
            var io = new ImportOptions(f);
            var item = app.project.importFile(io);
            item.parentFolder = dossierCible;
            try {
                item.mainSource.alphaMode = AlphaMode.STRAIGHT;
            } catch (e) {}
            return item;
        } catch (e2) {
            note("[!] Import impossible : " + cheminRelatif + " (" + e2.toString() + ")");
            return null;
        }
    }

    // =================================================================
    // 2. POLICES (Larsseit, sinon Montserrat, sinon Arial)
    // =================================================================

    function policeDisponible(ps, compTest) {
        // After Effects 24+ : API officielle
        try {
            if (app.fonts && app.fonts.getFontsByPostScriptName) {
                var r = app.fonts.getFontsByPostScriptName(ps);
                return !!(r && r.length > 0);
            }
        } catch (e) {}
        // Versions antérieures : on applique la police à un calque temporaire
        // et on relit le nom réellement utilisé.
        var ok = false;
        var l = null;
        try {
            l = compTest.layers.addText("Test");
            var tp = l.property("ADBE Text Properties").property("ADBE Text Document");
            var d = tp.value;
            d.font = ps;
            tp.setValue(d);
            ok = (tp.value.font === ps);
        } catch (e2) {
            ok = false;
        }
        try {
            if (l) {
                l.remove();
            }
        } catch (e3) {}
        return ok;
    }

    function premierePolice(liste, compTest) {
        for (var i = 0; i < liste.length; i++) {
            if (policeDisponible(liste[i], compTest)) {
                return liste[i];
            }
        }
        return null;
    }

    function choisirPolices(compTest) {
        var jeux = [
            { nom: "Larsseit", xb: ["Larsseit-ExtraBold"], b: ["Larsseit-Bold"], r: ["Larsseit", "Larsseit-Regular"] },
            { nom: "Montserrat (repli)", xb: ["Montserrat-ExtraBold"], b: ["Montserrat-Bold"], r: ["Montserrat-Regular"] },
            { nom: "Arial (repli ultime)", xb: ["Arial-BoldMT"], b: ["Arial-BoldMT"], r: ["ArialMT"] }
        ];
        for (var i = 0; i < jeux.length; i++) {
            var xb = premierePolice(jeux[i].xb, compTest);
            var b = premierePolice(jeux[i].b, compTest);
            var r = premierePolice(jeux[i].r, compTest);
            if (xb && b && r) {
                POLICES = { xb: xb, b: b, r: r };
                NOM_POLICE = jeux[i].nom;
                if (i === 0) {
                    note("[OK] Police : Larsseit (ExtraBold / Bold / Regular).");
                } else {
                    note("[!] Larsseit n'est pas installée : police utilisée = " + jeux[i].nom + ". Installez Larsseit puis relancez le script pour respecter la charte.");
                }
                return;
            }
        }
        POLICES = { xb: "Montserrat-ExtraBold", b: "Montserrat-Bold", r: "Montserrat-Regular" };
        NOM_POLICE = "Montserrat (non détectée)";
        note("[!] Ni Larsseit ni Montserrat détectées : Montserrat est référencée, After Effects la signalera comme manquante.");
    }

    // =================================================================
    // 3. EXPRESSIONS D'ANIMATION
    //    Toutes calées sur inPoint / outPoint : déplacer ou recadrer un
    //    calque dans la timeline déplace son animation avec lui.
    // =================================================================

    var EXPR = {

        // Fondu d'entrée / sortie, avec atténuation facultative
        fondu: function (dIn, dOut, att) {
            var l = [];
            l.push("// Fondu : entrée " + n(dIn) + " s, sortie " + n(dOut) + " s (calé sur inPoint / outPoint)");
            l.push("var a = ease(time, inPoint, inPoint + " + n(dIn) + ", 0, 1);");
            if (dOut > 0) {
                l.push("var b = ease(time, outPoint - " + n(dOut) + ", outPoint, 1, 0);");
            } else {
                l.push("var b = 1;");
            }
            if (att) {
                l.push("// Atténuation quand l'élément suivant prend le relais");
                l.push("var c = ease(time, " + n(att.t) + ", " + n(att.t + 0.4) + ", 1, " + n(att.niveau) + ");");
            } else {
                l.push("var c = 1;");
            }
            l.push("value * Math.min(a, b) * c;");
            return l.join("\n");
        },

        // Pop-up : ressort amorti (dépassement d'environ 13 %), stretch & squash facultatif
        pop: function (squash, sortie) {
            var l = [];
            l.push("// Pop-up : ressort amorti" + (squash ? " + stretch & squash léger" : ""));
            l.push("var t = time - inPoint;");
            l.push("var w = 2.2 * Math.PI * 2, k = 9;");
            l.push("var s = (t <= 0) ? 0 : 1 - Math.exp(-k * t) * Math.cos(w * t);");
            if (squash) {
                l.push("var q = (t <= 0) ? 0 : 0.12 * Math.exp(-k * t) * Math.sin(w * t);");
            } else {
                l.push("var q = 0;");
            }
            if (sortie) {
                l.push("var o = ease(time, outPoint - 0.25, outPoint, 1, 0);");
            } else {
                l.push("var o = 1;");
            }
            l.push("[value[0] * s * (1 + q) * o, value[1] * s * (1 - q) * o];");
            return l.join("\n");
        },

        // Slide : arrivée décalée de (dx, dy) px avec décélération
        slide: function (dx, dy, d, sortie) {
            var l = [];
            l.push("// Slide : arrivée décalée de [" + n(dx) + ", " + n(dy) + "] px, décélération sur " + n(d) + " s");
            l.push("var kIn = ease(time, inPoint, inPoint + " + n(d) + ", 1, 0);");
            if (sortie) {
                l.push("var kOut = ease(time, outPoint - 0.3, outPoint, 0, 1);");
            } else {
                l.push("var kOut = 0;");
            }
            l.push("add(value, [" + n(dx) + " * kIn - " + n(dx) + " * 0.5 * kOut, " + n(dy) + " * kIn - " + n(dy) + " * 0.5 * kOut]);");
            return l.join("\n");
        },

        // Grain : wiggle(10, 10) rafraîchi à 12 i/s, ramené dans la plage [lo, hi] %
        grain: function (lo, hi) {
            return [
                "// Grain : posterizeTime(12) + wiggle(10, 10), ramené entre " + n(lo) + " et " + n(hi) + " %",
                "posterizeTime(12);",
                "linear(wiggle(10, 10), value - 10, value + 10, " + n(lo) + ", " + n(hi) + ");"
            ].join("\n");
        },

        // Caméra 2D : push-in progressif sur toute la durée du calque
        pushIn: function (amplitude) {
            return [
                "// Push-in : échelle de 100 % à " + n(100 + amplitude) + " % sur la durée du calque",
                "var p = linear(time, inPoint, outPoint, 0, 1);",
                "mul(value, (100 + " + n(amplitude) + " * p) / 100);"
            ].join("\n");
        },

        // Caméra 2D : léger travelling latéral
        derive: function (dx) {
            return [
                "// Travelling latéral lent (" + n(dx) + " px → " + n(-dx) + " px)",
                "add(value, [linear(time, inPoint, outPoint, " + n(dx) + ", " + n(-dx) + "), 0]);"
            ].join("\n");
        }
    };

    // Applique une animation d'entrée (et de sortie) à un calque
    //   type : "pop" | "popSquash" | "slide" | "fondu"
    //   o    : { sortie: bool, dx, dy, attenue: {t, niveau} }
    function animer(calque, type, o) {
        o = o || {};
        var sortie = (o.sortie !== false);
        var dOut = sortie ? 0.3 : 0;
        if (type === "pop" || type === "popSquash") {
            expression(tr(calque, "ADBE Scale"), EXPR.pop(type === "popSquash", sortie), calque.name + " / échelle");
            expression(tr(calque, "ADBE Opacity"), EXPR.fondu(0.15, dOut, o.attenue), calque.name + " / opacité");
        } else if (type === "slide") {
            var dx = (o.dx === undefined) ? 0 : o.dx;
            var dy = (o.dy === undefined) ? 70 : o.dy;
            expression(tr(calque, "ADBE Position"), EXPR.slide(dx, dy, 0.6, sortie), calque.name + " / position");
            expression(tr(calque, "ADBE Opacity"), EXPR.fondu(0.45, dOut, o.attenue), calque.name + " / opacité");
        } else {
            expression(tr(calque, "ADBE Opacity"), EXPR.fondu(0.6, sortie ? 0.4 : 0, o.attenue), calque.name + " / opacité");
        }
        try {
            calque.motionBlur = true;
        } catch (e) {}
    }

    // Cascade lettre par lettre (animateur de texte + sélecteur de plage)
    function cascade(calqueTexte, duree) {
        try {
            var anims = calqueTexte.property("ADBE Text Properties").property("ADBE Text Animators");
            var iA = anims.addProperty("ADBE Text Animator").propertyIndex;
            // Ré-acquisition systématique : addProperty() invalide les références précédentes
            var A = function () {
                return calqueTexte.property("ADBE Text Properties").property("ADBE Text Animators").property(iA);
            };
            A().name = "Cascade d'entrée";
            A().property("ADBE Text Animator Properties").addProperty("ADBE Text Opacity");
            A().property("ADBE Text Animator Properties").property("ADBE Text Opacity").setValue(0);
            A().property("ADBE Text Animator Properties").addProperty("ADBE Text Position 3D");
            var pPos = A().property("ADBE Text Animator Properties").property("ADBE Text Position 3D");
            try {
                pPos.setValue([0, 40, 0]);
            } catch (e1) {
                pPos.setValue([0, 40]);
            }
            var iS = A().property("ADBE Text Selectors").addProperty("ADBE Text Selector").propertyIndex;
            var sel = A().property("ADBE Text Selectors").property(iS);
            sel.property("ADBE Text Percent Offset").expression = [
                "// Cascade : la sélection glisse de 0 à 100 % et libère les lettres une à une",
                "ease(time, inPoint, inPoint + " + n(duree) + ", 0, 100);"
            ].join("\n");
            return true;
        } catch (e) {
            note("[!] Cascade non créée sur « " + calqueTexte.name + " » : fondu simple conservé (" + e.toString() + ").");
            return false;
        }
    }

    // =================================================================
    // 4. FABRIQUES DE CALQUES
    // =================================================================

    // Calque texte. o : { nom, texte, graisse (xb|b|r), taille, couleur, pos,
    //                     aligne ("centre"|"gauche"), interligne, approche,
    //                     entree, sortie, guide }
    function texte(comp, o) {
        var l = comp.layers.addText(o.texte);
        l.name = o.nom;
        var tp = l.property("ADBE Text Properties").property("ADBE Text Document");
        var d = tp.value;
        try {
            d.resetCharStyle();
            d.resetParagraphStyle();
        } catch (e) {}
        d.font = POLICES[o.graisse || "b"];
        d.fontSize = o.taille;
        d.applyFill = true;
        d.fillColor = o.couleur || C.BLEU;
        d.applyStroke = false;
        d.tracking = (o.approche === undefined) ? 0 : o.approche;
        d.justification = (o.aligne === "gauche") ? ParagraphJustification.LEFT_JUSTIFY : ParagraphJustification.CENTER_JUSTIFY;
        if (o.interligne) {
            try {
                d.autoLeading = false;
            } catch (e1) {}
            try {
                d.leading = o.interligne;
            } catch (e2) {}
        }
        tp.setValue(d);
        ancre(l, (o.aligne === "gauche") ? "gauche" : "centre");
        tr(l, "ADBE Position").setValue(o.pos);
        if (o.entree !== undefined) {
            temps(l, o.entree, o.sortie);
        }
        if (o.guide) {
            l.guideLayer = true;
        } else if (o.taille < STATS.tailleMin) {
            STATS.tailleMin = o.taille;
        }
        return l;
    }

    function forme(comp, nom) {
        var l = comp.layers.addShape();
        l.name = nom;
        return l;
    }

    // Ajoute un groupe de formes complet à un calque de forme.
    // spec : { nom, formes: [ {type:"rect", taille, pos, arrondi}
    //                        | {type:"ellipse", taille, pos}
    //                        | {type:"trace", pts, ferme} ],
    //          fond, opaciteFond, contour, epaisseur, pos, rot }
    function groupe(calque, spec) {
        var racine = calque.property("ADBE Root Vectors Group");
        var idx = racine.addProperty("ADBE Vector Group").propertyIndex;
        // Ré-acquisition par index : un addProperty() invalide les références
        function G() {
            return calque.property("ADBE Root Vectors Group").property(idx);
        }
        function V() {
            return G().property("ADBE Vectors Group");
        }
        G().name = spec.nom || ("Groupe " + idx);
        var p;
        for (var i = 0; i < spec.formes.length; i++) {
            var s = spec.formes[i];
            if (s.type === "rect") {
                p = V().addProperty("ADBE Vector Shape - Rect");
                p.property("ADBE Vector Rect Size").setValue(s.taille);
                p.property("ADBE Vector Rect Position").setValue(s.pos || [0, 0]);
                p.property("ADBE Vector Rect Roundness").setValue(s.arrondi || 0);
            } else if (s.type === "ellipse") {
                p = V().addProperty("ADBE Vector Shape - Ellipse");
                p.property("ADBE Vector Ellipse Size").setValue(s.taille);
                p.property("ADBE Vector Ellipse Position").setValue(s.pos || [0, 0]);
            } else {
                p = V().addProperty("ADBE Vector Shape - Group");
                var trace = new Shape();
                trace.vertices = s.pts;
                trace.closed = (s.ferme !== false);
                p.property("ADBE Vector Shape").setValue(trace);
            }
        }
        if (spec.fond) {
            p = V().addProperty("ADBE Vector Graphic - Fill");
            p.property("ADBE Vector Fill Color").setValue(spec.fond);
            if (spec.opaciteFond !== undefined) {
                p.property("ADBE Vector Fill Opacity").setValue(spec.opaciteFond);
            }
        }
        if (spec.contour) {
            p = V().addProperty("ADBE Vector Graphic - Stroke");
            p.property("ADBE Vector Stroke Color").setValue(spec.contour);
            p.property("ADBE Vector Stroke Width").setValue(spec.epaisseur || 4);
            try {
                p.property("ADBE Vector Stroke Line Cap").setValue(2);   // bouts arrondis
                p.property("ADBE Vector Stroke Line Join").setValue(2);  // angles arrondis
            } catch (e) {}
        }
        var t = G().property("ADBE Vector Transform Group");
        if (spec.pos) {
            t.property("ADBE Vector Position").setValue(spec.pos);
        }
        if (spec.rot) {
            t.property("ADBE Vector Rotation").setValue(spec.rot);
        }
        return idx;
    }

    // Solide d'arrière-plan : dégradé (linéaire = 1, radial = 2) + grain
    function fond(comp, nom, c1, c2, depart, arrivee, typeDegrade, animeDegrade) {
        var l = comp.layers.addSolid(C.BLANC, nom, W, H, 1, comp.duration);
        l.source.parentFolder = F.assets;
        l.label = 8;
        var fx = l.property("ADBE Effect Parade").addProperty("ADBE Ramp");
        fx.name = "Dégradé de fond";
        regler(fx, ["ADBE Ramp-0001", "Start of Ramp", "Début de la rampe"], depart, nom + " / début du dégradé");
        regler(fx, ["ADBE Ramp-0002", "Start Color", "Couleur de début"], c1, nom + " / couleur de début");
        regler(fx, ["ADBE Ramp-0003", "End of Ramp", "Fin de la rampe"], arrivee, nom + " / fin du dégradé");
        regler(fx, ["ADBE Ramp-0004", "End Color", "Couleur de fin"], c2, nom + " / couleur de fin");
        regler(fx, ["ADBE Ramp-0005", "Ramp Shape", "Forme de la rampe"], typeDegrade, nom + " / forme du dégradé");
        if (animeDegrade) {
            expression(prop(fx, ["ADBE Ramp-0001", "Start of Ramp", "Début de la rampe"]), [
                "// Dégradé vivant : le centre de lumière dérive lentement",
                "add(value, [Math.sin(time * 0.6) * 120, Math.cos(time * 0.45) * 60]);"
            ].join("\n"), nom + " / dégradé animé");
        }
        var nz = l.property("ADBE Effect Parade").addProperty("ADBE Noise");
        nz.name = "Grain du fond";
        reglerPct(nz, ["ADBE Noise-0001", "Amount of Noise", "Quantité de bruit"], 3, nom + " / grain");
        regler(nz, ["ADBE Noise-0002", "Use Color Noise", "Utiliser du bruit de couleur"], 0, nom + " / grain monochrome");
        expression(prop(nz, ["ADBE Noise-0001", "Amount of Noise", "Quantité de bruit"]), EXPR.grain(2, 4), nom + " / grain animé");
        expression(tr(l, "ADBE Scale"), [
            "// Respiration du fond : 100 % → 103 %",
            "var s = linear(time, inPoint, outPoint, 100, 103);",
            "[s, s];"
        ].join("\n"), nom + " / échelle");
        return l;
    }

    // Null « caméra 2D » : les calques de la scène y sont rattachés
    function camera(comp, nom) {
        var l = comp.layers.addNull(comp.duration);
        l.name = nom;
        l.source.parentFolder = F.assets;
        tr(l, "ADBE Position").setValue([W / 2, H / 2]);
        l.label = 9;
        return l;
    }

    // Rattache à la caméra tous les calques sans parent (hors fonds)
    function rattacher(comp, cam) {
        for (var i = 1; i <= comp.numLayers; i++) {
            var l = comp.layer(i);
            if (l.index === cam.index || l.parent !== null || l.name.indexOf("BG_") === 0) {
                continue;
            }
            l.parent = cam;
        }
    }

    // Ombre portée teintée violet/bleu
    function ombre(calque, distance) {
        var fx;
        try {
            fx = calque.property("ADBE Effect Parade").addProperty("ADBE Drop Shadow");
        } catch (e) {
            note("[!] Ombre portée indisponible sur « " + calque.name + " ».");
            return;
        }
        fx.name = "Ombre teintée";
        regler(fx, ["ADBE Drop Shadow-0001", "Shadow Color", "Couleur de l'ombre"], C.OMBRE, "Ombre / couleur");
        reglerPct(fx, ["ADBE Drop Shadow-0002", "Opacity", "Opacité"], 35, "Ombre / opacité");
        regler(fx, ["ADBE Drop Shadow-0003", "Direction"], 135, "Ombre / direction");
        regler(fx, ["ADBE Drop Shadow-0004", "Distance"], distance || 14, "Ombre / distance");
        regler(fx, ["ADBE Drop Shadow-0005", "Softness", "Adoucissement"], 32, "Ombre / adoucissement");
    }

    // Identifiants des commandes de menu des styles de calque (EN / FR)
    function commandesStyles() {
        if (CMD_STYLES !== null) {
            return CMD_STYLES;
        }
        CMD_STYLES = { degrade: 0, lueur: 0 };
        var noms = {
            degrade: ["Gradient Overlay", "Incrustation en dégradé", "Incrustation dégradé"],
            lueur: ["Inner Glow", "Lueur interne"]
        };
        for (var k in noms) {
            for (var i = 0; i < noms[k].length; i++) {
                try {
                    var id = app.findMenuCommandId(noms[k][i]);
                    if (id) {
                        CMD_STYLES[k] = id;
                        break;
                    }
                } catch (e) {}
            }
        }
        if (!CMD_STYLES.degrade && !CMD_STYLES.lueur) {
            note("[!] Styles de calque : commandes de menu introuvables. Appliquez à la main Incrustation en dégradé (Réfléchi) et Lueur interne sur les maisons et icônes.");
        }
        return CMD_STYLES;
    }

    // Incrustation en dégradé (style « Réfléchi ») + Lueur interne blanche (rim light)
    function styles(comp, calque) {
        if (!CONFIG.stylesDeCalque) {
            return;
        }
        var cmd = commandesStyles();
        if (!cmd.degrade && !cmd.lueur) {
            return;
        }
        try {
            comp.openInViewer();
            for (var i = 1; i <= comp.numLayers; i++) {
                comp.layer(i).selected = false;
            }
            calque.selected = true;
            if (cmd.degrade) {
                app.executeCommand(cmd.degrade);
            }
            if (cmd.lueur) {
                app.executeCommand(cmd.lueur);
            }
            calque.selected = false;
        } catch (e) {
            STATS.stylesEchecs++;
            return;
        }
        var ls = calque.property("ADBE Layer Styles");
        if (!ls) {
            STATS.stylesEchecs++;
            return;
        }
        for (var j = 1; j <= ls.numProperties; j++) {
            var g = ls.property(j);
            var mn = g.matchName;
            if (mn.indexOf("gradientFill") === 0) {
                // Style 4 = Réfléchi ; opacité faible pour ne pas dénaturer les aplats
                reglerDiscret(g, ["gradientFill/type", "Style"], 4, false);
                reglerDiscret(g, ["gradientFill/opacity", "Opacity", "Opacité"], 15, true);
            } else if (mn.indexOf("innerGlow") === 0) {
                reglerDiscret(g, ["innerGlow/color", "Color", "Couleur"], C.BLANC, false);
                reglerDiscret(g, ["innerGlow/opacity", "Opacity", "Opacité"], 40, true);
                reglerDiscret(g, ["innerGlow/blur", "Size", "Taille"], 12, false);
            }
        }
        STATS.styles++;
    }

    // Repère « À ANIMER » pour les personnages (calque guide, jamais rendu)
    function repere(comp, nom, pos, echelle, consigne) {
        var l = forme(comp, "À ANIMER — " + nom);
        groupe(l, { nom: "Tête", formes: [{ type: "ellipse", taille: [110, 130], pos: [0, -300] }], fond: C.REPERE, opaciteFond: 15, contour: C.REPERE, epaisseur: 4 });
        groupe(l, { nom: "Corps", formes: [{ type: "rect", taille: [200, 420], pos: [0, -20], arrondi: 60 }], fond: C.REPERE, opaciteFond: 15, contour: C.REPERE, epaisseur: 4 });
        tr(l, "ADBE Scale").setValue([echelle * 100, echelle * 100]);
        tr(l, "ADBE Position").setValue(pos);
        l.guideLayer = true;
        l.label = 1;
        try {
            l.comment = consigne.replace(/\r/g, " ");
        } catch (e) {}
        var t = texte(comp, {
            nom: "NOTE — " + nom,
            texte: "À ANIMER : " + nom + "\r" + consigne,
            graisse: "r",
            taille: 26,
            couleur: C.REPERE,
            pos: [pos[0], pos[1] + 260 * echelle],
            guide: true
        });
        t.label = 1;
        t.parent = l;
        return l;
    }

    // ---------------------------------------------------------------
    // Illustrations en calques de forme (le premier groupe est au-dessus)
    // ---------------------------------------------------------------

    // Maison 2D flat (≈ 300 × 270 px, sol à y = 140)
    function maison(comp, nom) {
        var l = forme(comp, nom);
        groupe(l, { nom: "Fenêtres", formes: [
            { type: "rect", taille: [52, 46], pos: [-62, 40], arrondi: 4 },
            { type: "rect", taille: [52, 46], pos: [62, 40], arrondi: 4 }
        ], fond: C.BLANC });
        groupe(l, { nom: "Porte", formes: [{ type: "rect", taille: [54, 90], pos: [0, 95], arrondi: 6 }], fond: C.OR });
        groupe(l, { nom: "Toit", formes: [{ type: "trace", pts: [[-150, -10], [0, -130], [150, -10]] }], fond: C.OR });
        groupe(l, { nom: "Cheminée", formes: [{ type: "rect", taille: [34, 70], pos: [80, -85] }], fond: C.BLEU });
        groupe(l, { nom: "Murs", formes: [{ type: "rect", taille: [220, 160], pos: [0, 60], arrondi: 10 }], fond: C.BLEU });
        l.label = 2;
        return l;
    }

    // Accessoires : contrat, clé, graphique
    function accessoire(comp, type, nom) {
        var l = forme(comp, nom);
        if (type === "contrat") {
            groupe(l, { nom: "Coche or", formes: [{ type: "trace", pts: [[-28, 40], [-6, 62], [34, 18]], ferme: false }], contour: C.OR, epaisseur: 14 });
            groupe(l, { nom: "Lignes", formes: [
                { type: "rect", taille: [80, 8], pos: [0, -45], arrondi: 4 },
                { type: "rect", taille: [80, 8], pos: [0, -22], arrondi: 4 },
                { type: "rect", taille: [56, 8], pos: [-12, 1], arrondi: 4 }
            ], fond: C.BLEU, opaciteFond: 45 });
            groupe(l, { nom: "Feuille", formes: [{ type: "rect", taille: [140, 180], arrondi: 10 }], fond: C.BLANC, contour: C.BLEU, epaisseur: 6 });
        } else if (type === "cle") {
            groupe(l, { nom: "Anneau", formes: [{ type: "ellipse", taille: [70, 70], pos: [-45, 0] }], contour: C.OR, epaisseur: 18 });
            groupe(l, { nom: "Tige et dents", formes: [
                { type: "rect", taille: [110, 18], pos: [45, 0] },
                { type: "rect", taille: [16, 34], pos: [85, 17] },
                { type: "rect", taille: [16, 26], pos: [60, 13] }
            ], fond: C.OR });
            tr(l, "ADBE Rotate Z").setValue(-35);
        } else {
            groupe(l, { nom: "Flèche", formes: [
                { type: "trace", pts: [[-62, -5], [-20, -35], [12, -20], [60, -62]], ferme: false },
                { type: "trace", pts: [[40, -66], [64, -66], [64, -42]], ferme: false }
            ], contour: C.BLEU, epaisseur: 8 });
            groupe(l, { nom: "Barres", formes: [
                { type: "rect", taille: [26, 40], pos: [-45, 40] },
                { type: "rect", taille: [26, 70], pos: [0, 25] },
                { type: "rect", taille: [26, 100], pos: [45, 10] }
            ], fond: C.OR });
            groupe(l, { nom: "Carte", formes: [{ type: "rect", taille: [170, 170], arrondi: 12 }], fond: C.BLANC, contour: C.BLEU, epaisseur: 6 });
        }
        l.label = 2;
        return l;
    }

    // Pictogrammes ronds (pastille 60 px)
    function icone(comp, type, nom) {
        var l = forme(comp, nom);
        var B = C.BLANC;
        var e = 3.5;
        var pastille = C.BLEU;
        if (type === "tel") {
            groupe(l, { nom: "Bouton", formes: [{ type: "ellipse", taille: [5, 5], pos: [0, 12] }], fond: B });
            groupe(l, { nom: "Téléphone", formes: [{ type: "rect", taille: [22, 36], arrondi: 5 }], contour: B, epaisseur: e });
        } else if (type === "web") {
            groupe(l, { nom: "Globe", formes: [
                { type: "ellipse", taille: [32, 32] },
                { type: "ellipse", taille: [13, 32] },
                { type: "trace", pts: [[-16, 0], [16, 0]], ferme: false }
            ], contour: B, epaisseur: e });
        } else if (type === "mail") {
            groupe(l, { nom: "Rabat", formes: [{ type: "trace", pts: [[-16, -10], [0, 3], [16, -10]], ferme: false }], contour: B, epaisseur: e });
            groupe(l, { nom: "Enveloppe", formes: [{ type: "rect", taille: [32, 22], arrondi: 3 }], contour: B, epaisseur: e });
        } else if (type === "lieu") {
            groupe(l, { nom: "Point", formes: [{ type: "ellipse", taille: [7, 7], pos: [0, -5] }], fond: B });
            groupe(l, { nom: "Épingle", formes: [{ type: "trace", pts: [[0, 15], [-10, 1], [-11, -6], [-7, -13], [0, -16], [7, -13], [11, -6], [10, 1]] }], contour: B, epaisseur: e });
        } else if (type === "facebook") {
            groupe(l, { nom: "f", formes: [
                { type: "trace", pts: [[2, 16], [2, -4], [4, -11], [11, -14]], ferme: false },
                { type: "trace", pts: [[-5, 0], [10, 0]], ferme: false }
            ], contour: B, epaisseur: 4.5 });
        } else if (type === "instagram") {
            groupe(l, { nom: "Point", formes: [{ type: "ellipse", taille: [4, 4], pos: [8, -8] }], fond: B });
            groupe(l, { nom: "Objectif", formes: [
                { type: "rect", taille: [28, 28], arrondi: 9 },
                { type: "ellipse", taille: [11, 11] }
            ], contour: B, epaisseur: e });
        } else if (type === "whatsapp") {
            groupe(l, { nom: "Queue", formes: [{ type: "trace", pts: [[-11, 8], [-15, 16], [-6, 12]] }], fond: B });
            groupe(l, { nom: "Bulle", formes: [{ type: "ellipse", taille: [28, 28] }], contour: B, epaisseur: e });
        } else if (type === "coche") {
            pastille = C.OR;
            groupe(l, { nom: "Coche", formes: [{ type: "trace", pts: [[-13, 0], [-4, 10], [14, -10]], ferme: false }], contour: C.BLEU, epaisseur: 7 });
        }
        groupe(l, { nom: "Pastille", formes: [{ type: "ellipse", taille: [60, 60] }], fond: pastille });
        l.label = 2;
        return l;
    }

    // Carte d'annonce « confuse » (scène 1) : texte + carton blanc qui flottent
    function carte(comp, libelle, pos, rot, entree, sortie) {
        var t = texte(comp, { nom: "TXT_CARTE — " + libelle, texte: libelle, graisse: "b", taille: 50, couleur: C.BLEU, pos: pos });
        var r = mesure(t);
        var lc = r.width + 100;
        var hc = r.height + 64;
        var c = forme(comp, "CARTE — " + libelle);
        groupe(c, { nom: "Liseré or", formes: [{ type: "rect", taille: [10, hc - 36], pos: [-lc / 2 + 24, 0], arrondi: 5 }], fond: C.OR });
        groupe(c, { nom: "Carton", formes: [{ type: "rect", taille: [lc, hc], arrondi: 18 }], fond: C.BLANC });
        c.moveAfter(t);                       // le carton passe sous le texte
        tr(c, "ADBE Position").setValue(pos);
        temps(c, entree, sortie);
        temps(t, entree, sortie);
        t.parent = c;                          // le texte suit le carton...
        tr(c, "ADBE Rotate Z").setValue(rot);  // ...y compris sa rotation
        c.label = 2;
        ombre(c, 12);
        animer(c, "popSquash");
        expression(tr(c, "ADBE Position"), "// Flottement désordonné\nwiggle(0.8, 18);", c.name + " / flottement");
        expression(tr(c, "ADBE Rotate Z"), "// Oscillation\nwiggle(0.6, 3);", c.name + " / oscillation");
        // Le texte suit l'opacité du carton
        expression(tr(t, "ADBE Opacity"), "// Opacité héritée du carton\nthisLayer.parent.transform.opacity;", t.name + " / opacité");
        return c;
    }

    // Aligne une rangée d'éléments (icônes + textes) centrée sur cx
    //   elements : [{ l: calque, ecart: px après l'élément }]
    function rangee(elements, cx, cy) {
        var largeurs = [];
        var total = 0;
        var i;
        for (i = 0; i < elements.length; i++) {
            var r = ancre(elements[i].l, "centre");
            var sc = tr(elements[i].l, "ADBE Scale").value[0] / 100;
            largeurs[i] = r.width * sc;
            total += largeurs[i];
            if (i < elements.length - 1) {
                total += (elements[i].ecart === undefined) ? 24 : elements[i].ecart;
            }
        }
        var x = cx - total / 2;
        for (i = 0; i < elements.length; i++) {
            tr(elements[i].l, "ADBE Position").setValue([x + largeurs[i] / 2, cy]);
            x += largeurs[i] + ((elements[i].ecart === undefined) ? 24 : elements[i].ecart);
        }
    }

    // Logo animé : symbole qui tourne + logotype qui glisse (+ reflet lumineux)
    function logoAnime(comp, cx, cy, echelle, t0) {
        var res = { symbole: null, texte: [] };
        if (LOGO.symbole && LOGO.texte) {
            var ls = comp.layers.add(LOGO.symbole);
            var lt = comp.layers.add(LOGO.texte);
            var ws = LOGO.symbole.width;
            var wt = LOGO.texte.width;
            ls.name = "LOGO — Symbole";
            lt.name = "LOGO — Logotype";
            tr(ls, "ADBE Scale").setValue([echelle * 100, echelle * 100]);
            tr(lt, "ADBE Scale").setValue([echelle * 100, echelle * 100]);
            // Le logo complet (ws + wt) est centré sur cx
            tr(ls, "ADBE Position").setValue([cx - (wt / 2) * echelle, cy]);
            tr(lt, "ADBE Position").setValue([cx + (ws / 2) * echelle, cy]);
            res.symbole = ls;
            res.texte.push(lt);
        } else {
            // Logo vectoriel de repli (fichiers PNG absents)
            var anneau = forme(comp, "LOGO — Symbole (repli vectoriel)");
            groupe(anneau, { nom: "Anneau", formes: [{ type: "ellipse", taille: [300, 300] }], contour: C.OR, epaisseur: 28 });
            groupe(anneau, { nom: "Boucle", formes: [{ type: "trace", pts: [[-80, 10], [-20, -60], [20, 60], [80, -10]], ferme: false }], contour: C.OR, epaisseur: 22 });
            var k2 = echelle * 2;  // facteur 1 pour une échelle de 50 %
            tr(anneau, "ADBE Scale").setValue([k2 * 100, k2 * 100]);
            tr(anneau, "ADBE Position").setValue([cx - 395 * k2, cy]);
            var t1 = texte(comp, { nom: "LOGO — Justvyou (repli)", texte: "Justvyou", graisse: "xb", taille: Math.round(150 * k2), couleur: C.BLEU, aligne: "gauche", pos: [cx - 175 * k2, cy - 30 * k2] });
            var t2 = texte(comp, { nom: "LOGO — Property (repli)", texte: "Property", graisse: "r", taille: Math.round(65 * k2), couleur: C.OR, aligne: "gauche", pos: [cx - 172 * k2, cy + 85 * k2] });
            res.symbole = anneau;
            res.texte.push(t1);
            res.texte.push(t2);
        }
        var fin = comp.duration;
        temps(res.symbole, t0, fin);
        animer(res.symbole, "pop", { sortie: false });
        expression(tr(res.symbole, "ADBE Rotate Z"), [
            "// Rotation d'entrée du symbole (-120° → 0°)",
            "value + ease(time, inPoint, inPoint + 0.9, -120, 0);"
        ].join("\n"), "Logo / rotation");
        for (var i = 0; i < res.texte.length; i++) {
            temps(res.texte[i], t0 + 0.5, fin);
            animer(res.texte[i], "slide", { dx: -90, dy: 0, sortie: false });
            reflet(res.texte[i], 1.3);
        }
        return res;
    }

    // Reflet lumineux qui balaie un calque (CC Light Sweep, livré avec AE)
    function reflet(calque, delai) {
        try {
            var fx = calque.property("ADBE Effect Parade").addProperty("CC Light Sweep");
            fx.name = "Reflet";
            expression(prop(fx, ["CC Light Sweep-0001", "Center", "Centre"]), [
                "// Le reflet traverse le calque de gauche à droite",
                "var r = thisLayer.sourceRectAtTime(time, false);",
                "[linear(time, inPoint + " + n(delai) + ", inPoint + " + n(delai + 1) + ", r.left - 0.2 * r.width, r.left + 1.2 * r.width), r.top + r.height / 2];"
            ].join("\n"), calque.name + " / reflet");
            regler(fx, ["CC Light Sweep-0004", "Width", "Largeur"], 60, "Reflet / largeur");
        } catch (e) {
            note("[!] CC Light Sweep indisponible : reflet du logo à ajouter à la main.");
        }
    }

    function nouvelleScene(i, couleurFond) {
        var s = SCENES[i];
        var c = app.project.items.addComp(s.nom, W, H, 1, s.fin - s.debut, CONFIG.fps);
        c.parentFolder = F.comps;
        c.bgColor = couleurFond;
        c.motionBlur = true;
        return c;
    }

    // =================================================================
    // 5. SCÈNES
    // =================================================================

    // -----------------------------------------------------------------
    // SCÈNE 1 (00:00 → 00:15) — Le client perdu face aux offres confuses
    // -----------------------------------------------------------------
    function scene1() {
        var c = nouvelleScene(0, C.BLEU_NUIT);
        fond(c, "BG_SC01 — Dégradé radial bleu / bleu nuit", C.BLEU, C.BLEU_NUIT, [960, 420], [960, 1350], 2, true);
        var cam = camera(c, "CAM_SC01 — Caméra 2D (push-in + roulis inquiet)");

        repere(c, "Client perdu", [960, 760], 1.0,
            "Marche, regarde son téléphone (0–4 s), tourne la tête vers les cartes,\r" +
            "fronce les sourcils, se gratte la tête (9 s), lève les yeux vers le haut (12,3 s).");

        // 00:00,5 → 00:04 : question d'ouverture
        var t1 = texte(c, { nom: "TXT_SC01_01 — Trouver un logement", texte: "Trouver un logement\rà Abidjan" + NBSP + "?", graisse: "xb", taille: 96, interligne: 110, couleur: C.BLANC, pos: [960, 250], entree: 0.5, sortie: 4.0 });
        animer(t1, "slide");

        // 00:04 → 00:09,2 : les annonces confuses envahissent l'écran
        var cartes = [
            ["Prix flous" + NBSP + "?", [430, 330], -6],
            ["Frais cachés" + NBSP + "?", [1490, 300], 5],
            ["Visite annulée", [380, 720], 4],
            ["Annonce expirée", [1550, 700], -4],
            ["Photos trompeuses", [560, 925], -3],
            ["Propriétaire injoignable", [1345, 920], 3]
        ];
        for (var i = 0; i < cartes.length; i++) {
            carte(c, cartes[i][0], cartes[i][1], cartes[i][2], 4.0 + i * 0.55, 9.2);
        }

        // 00:09,2 → 00:12,3 : le constat
        var t2 = texte(c, { nom: "TXT_SC01_02 — Trop d'offres", texte: "Trop d’offres.\rTrop de doutes.", graisse: "xb", taille: 120, interligne: 136, couleur: C.BLANC, pos: [960, 470], entree: 9.2, sortie: 12.3 });
        animer(t2, "pop");

        // 00:12,3 → 00:15 : la promesse (en or)
        var t3 = texte(c, { nom: "TXT_SC01_03 — Faire confiance", texte: "Et si vous pouviez\renfin faire confiance" + NBSP + "?", graisse: "xb", taille: 84, interligne: 100, couleur: C.OR, pos: [960, 300], entree: 12.3, sortie: 15.0 });
        animer(t3, "slide");

        rattacher(c, cam);
        expression(tr(cam, "ADBE Scale"), EXPR.pushIn(8), "CAM_SC01 / push-in");
        expression(tr(cam, "ADBE Rotate Z"), "// Roulis inquiet (confusion du client)\nwiggle(0.5, 1.2);", "CAM_SC01 / roulis");
        return c;
    }

    // -----------------------------------------------------------------
    // SCÈNE 2 (00:15 → 00:35) — Justvyou Property et ses trois services
    // -----------------------------------------------------------------
    function scene2() {
        var c = nouvelleScene(1, C.BLANC);
        var fin = c.duration;
        fond(c, "BG_SC02 — Dégradé radial blanc / bleu pâle", C.BLANC, C.BLEU_PALE, [960, 480], [960, 1500], 2, false);
        var cam = camera(c, "CAM_SC02 — Caméra 2D (push-in + travelling)");

        // 00:15,3 → 00:19 : apparition de la marque
        var logo;
        if (LOGO.complet) {
            logo = c.layers.add(LOGO.complet);
            logo.name = "LOGO — Complet";
            tr(logo, "ADBE Scale").setValue([42, 42]);
            tr(logo, "ADBE Position").setValue([960, 400]);
            temps(logo, 0.3, 4.0);
            animer(logo, "pop");
        } else {
            var lg = logoAnime(c, 960, 400, 0.42, 0.3);
            lg.symbole.outPoint = 4.0;
            for (var j = 0; j < lg.texte.length; j++) {
                lg.texte[j].outPoint = 4.0;
            }
        }
        var st = texte(c, { nom: "TXT_SC02_00 — Votre agence", texte: "Votre agence immobilière à Abidjan", graisse: "b", taille: 64, couleur: C.BLEU, pos: [960, 640], entree: 0.9, sortie: 4.0 });
        animer(st, "slide");

        // 00:19 → 00:35 : les trois services, colonne par colonne
        var cols = [
            { x: 480, t: 4.0, titre: "VENTE", desc: "Biens vérifiés\rDocuments contrôlés", acc: "contrat" },
            { x: 960, t: 9.0, titre: "LOCATION", desc: "Logements visités\rContrats clairs", acc: "cle" },
            { x: 1440, t: 14.0, titre: "GESTION", desc: "Loyers suivis\rBien entretenu", acc: "graphique" }
        ];
        for (var i = 0; i < cols.length; i++) {
            var k = cols[i];
            var att = (i < cols.length - 1) ? { t: cols[i + 1].t, niveau: 0.6 } : null;

            var m = maison(c, "MAISON " + (i + 1) + " — " + k.titre);
            ancre(m, "bas");
            tr(m, "ADBE Position").setValue([k.x, 570]);
            temps(m, k.t, fin);

            var a = accessoire(c, k.acc, "ACCESSOIRE " + (i + 1) + " — " + k.acc);
            ancre(a, "centre");
            tr(a, "ADBE Scale").setValue([80, 80]);
            tr(a, "ADBE Position").setValue([k.x + 125, 515]);
            temps(a, k.t + 0.5, fin);
            // Parentage AVANT les expressions (sinon parent à l'échelle 0)
            a.parent = m;

            animer(m, "popSquash", { attenue: att });
            animer(a, "popSquash", { attenue: att });
            if (k.acc === "cle") {
                expression(tr(a, "ADBE Rotate Z"), "// La clé tourne dans la serrure\nvalue + ease(time, inPoint + 0.5, inPoint + 1.0, 0, 90);", a.name + " / rotation");
            }
            ombre(m, 16);
            ombre(a, 10);
            styles(c, m);
            styles(c, a);

            var tt = texte(c, { nom: "TXT_SC02 — " + k.titre, texte: k.titre, graisse: "xb", taille: 80, approche: 40, couleur: C.BLEU, pos: [k.x, 690], entree: k.t + 0.3, sortie: fin });
            animer(tt, "slide");

            var barre = forme(c, "SOULIGNÉ OR — " + k.titre);
            groupe(barre, { nom: "Barre", formes: [{ type: "rect", taille: [140, 8], arrondi: 4 }], fond: C.OR });
            tr(barre, "ADBE Position").setValue([k.x, 745]);
            temps(barre, k.t + 0.6, fin);
            expression(tr(barre, "ADBE Scale"), "// Le soulignement se déploie depuis le centre\nvar g = ease(time, inPoint, inPoint + 0.5, 0, 100);\n[value[0] * g / 100, value[1]];", barre.name + " / déploiement");
            expression(tr(barre, "ADBE Opacity"), EXPR.fondu(0.2, 0.3, att ? { t: att.t, niveau: 0 } : null), barre.name + " / opacité");

            var td = texte(c, { nom: "TXT_SC02 — " + k.titre + " (détail)", texte: k.desc, graisse: "r", taille: 46, interligne: 58, couleur: C.BLEU, pos: [k.x, 815], entree: k.t + 0.7, sortie: fin });
            animer(td, "fondu");
        }

        rattacher(c, cam);
        expression(tr(cam, "ADBE Scale"), EXPR.pushIn(4), "CAM_SC02 / push-in");
        expression(tr(cam, "ADBE Position"), EXPR.derive(15), "CAM_SC02 / travelling");
        return c;
    }

    // -----------------------------------------------------------------
    // SCÈNE 3 (00:35 → 00:50) — Famille satisfaite, logement moderne à Abidjan
    // -----------------------------------------------------------------
    function scene3() {
        var c = nouvelleScene(2, C.OR_PALE);
        fond(c, "BG_SC03 — Dégradé vertical blanc / or pâle", C.BLANC, C.OR_PALE, [960, 0], [960, 1080], 1, false);
        var cam = camera(c, "CAM_SC03 — Caméra 2D (push-in + travelling)");

        // Halo de soleil derrière l'immeuble
        var soleil = forme(c, "HALO — Soleil");
        groupe(soleil, { nom: "Disque", formes: [{ type: "ellipse", taille: [760, 760] }], fond: C.OR, opaciteFond: 35 });
        tr(soleil, "ADBE Position").setValue([1480, 420]);
        try {
            var flou = soleil.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2");
            regler(flou, ["ADBE Gaussian Blur 2-0001", "Blurriness", "Flou"], 120, "Halo / flou");
        } catch (e) {
            note("[!] Flou gaussien indisponible sur le halo.");
        }
        animer(soleil, "fondu", { sortie: false });

        // Immeuble moderne (sol à y = 0, ancré en bas)
        var im = forme(c, "IMMEUBLE — Logement moderne");
        var fen = [];
        var xs = [-190, 0, 190];
        var ys = [-470, -340, -210];
        for (var a = 0; a < 3; a++) {
            for (var b = 0; b < 3; b++) {
                fen.push({ type: "rect", taille: [120, 84], pos: [xs[b], ys[a]], arrondi: 6 });
            }
        }
        groupe(im, { nom: "Fenêtres éclairées", formes: fen, fond: C.OR });
        groupe(im, { nom: "Balcons", formes: [
            { type: "rect", taille: [600, 12], pos: [0, -415], arrondi: 6 },
            { type: "rect", taille: [600, 12], pos: [0, -285], arrondi: 6 },
            { type: "rect", taille: [600, 12], pos: [0, -155], arrondi: 6 }
        ], fond: C.BLANC });
        groupe(im, { nom: "Entrée vitrée", formes: [{ type: "rect", taille: [150, 120], pos: [0, -60], arrondi: 6 }], fond: C.BLANC, opaciteFond: 85 });
        groupe(im, { nom: "Toiture", formes: [{ type: "rect", taille: [700, 30], pos: [0, -585], arrondi: 4 }], fond: C.OR });
        groupe(im, { nom: "Façade", formes: [{ type: "rect", taille: [640, 570], pos: [0, -285], arrondi: 6 }], fond: C.BLEU });
        groupe(im, { nom: "Ombre au sol", formes: [{ type: "rect", taille: [1000, 18], pos: [0, 9], arrondi: 9 }], fond: C.BLEU, opaciteFond: 25 });
        ancre(im, "bas");
        tr(im, "ADBE Position").setValue([1480, 975]);
        im.label = 2;
        ombre(im, 20);
        styles(c, im);
        animer(im, "slide", { dy: 120, sortie: false });

        repere(c, "Famille (2 parents + 1 enfant)", [1060, 780], 0.9,
            "Sourires, clignements, l'enfant court vers la porte (35–40 s),\r" +
            "un parent reçoit les clés et serre la main du conseiller (40–45 s).");

        // 00:35,4 → 00:40 : titre
        var t1 = texte(c, { nom: "TXT_SC03_01 — Chez vous, enfin", texte: "Chez vous, enfin.", graisse: "xb", taille: 110, couleur: C.BLEU, aligne: "gauche", pos: [192, 240], entree: 0.4, sortie: 5.0 });
        animer(t1, "slide");

        // 00:40 → 00:45 : trois bénéfices avec coches
        var puces = ["Clés en main", "Dossier clair", "Conseiller joignable"];
        for (var i = 0; i < puces.length; i++) {
            var y = 430 + i * 100;
            var t = 5.0 + i * 0.5;
            var ic = icone(c, "coche", "COCHE " + (i + 1));
            tr(ic, "ADBE Position").setValue([230, y]);
            temps(ic, t, 10.0);
            animer(ic, "popSquash");
            var tx = texte(c, { nom: "TXT_SC03_02 — " + puces[i], texte: puces[i], graisse: "b", taille: 60, couleur: C.BLEU, aligne: "gauche", pos: [290, y], entree: t + 0.1, sortie: 10.0 });
            animer(tx, "slide", { dx: -40, dy: 0 });
        }

        // 00:45 → 00:50 : message final de la scène
        var t3 = texte(c, { nom: "TXT_SC03_03 — Esprit tranquille", texte: "Acheter, louer ou investir" + NBSP + ":\ravancez l’esprit tranquille.", graisse: "xb", taille: 72, interligne: 86, couleur: C.BLEU, aligne: "gauche", pos: [192, 250], entree: 10.0, sortie: 15.0 });
        animer(t3, "slide");

        rattacher(c, cam);
        expression(tr(cam, "ADBE Scale"), EXPR.pushIn(5), "CAM_SC03 / push-in");
        expression(tr(cam, "ADBE Position"), EXPR.derive(-20), "CAM_SC03 / travelling");
        return c;
    }

    // -----------------------------------------------------------------
    // SCÈNE 4 (00:50 → 01:00) — Logo animé, slogan, contacts, réseaux
    // -----------------------------------------------------------------
    function scene4() {
        var c = nouvelleScene(3, C.BLANC);
        fond(c, "BG_SC04 — Dégradé radial blanc / or pâle", C.BLANC, C.OR_PALE, [960, 400], [960, 1400], 2, false);
        var cam = camera(c, "CAM_SC04 — Caméra 2D (push-in léger)");

        // 00:50,4 : logo
        logoAnime(c, 960, 330, 0.5, 0.4);

        // 00:53,3 : slogan en cascade + soulignement or
        var sl = texte(c, { nom: "TXT_SC04_01 — Slogan", texte: "Trouvez mieux. Vivez mieux.", graisse: "xb", taille: 92, couleur: C.BLEU, pos: [960, 585], entree: 3.3, sortie: c.duration });
        cascade(sl, 0.9);
        animer(sl, "fondu", { sortie: false });
        var barre = forme(c, "SOULIGNÉ OR — Slogan");
        groupe(barre, { nom: "Barre", formes: [{ type: "rect", taille: [260, 8], arrondi: 4 }], fond: C.OR });
        tr(barre, "ADBE Position").setValue([960, 650]);
        temps(barre, 3.9, c.duration);
        expression(tr(barre, "ADBE Scale"), "// Le soulignement se déploie depuis le centre\nvar g = ease(time, inPoint, inPoint + 0.5, 0, 100);\n[value[0] * g / 100, value[1]];", barre.name + " / déploiement");

        // 00:55,5 → 01:00 : contacts (3 rangées décalées de 0,5 s)
        var fin = c.duration;
        var tel = icone(c, "tel", "ICÔNE — Téléphone");
        tr(tel, "ADBE Scale").setValue([120, 120]);
        var tTel = texte(c, { nom: "TXT_SC04_02 — Téléphone", texte: CONTACT.tel, graisse: "xb", taille: 64, couleur: C.BLEU, pos: [960, 730] });
        rangee([{ l: tel, ecart: 24 }, { l: tTel }], 960, 730);

        var web = icone(c, "web", "ICÔNE — Site web");
        var tWeb = texte(c, { nom: "TXT_SC04_03 — Site web", texte: CONTACT.web, graisse: "b", taille: 40, couleur: C.BLEU, pos: [960, 830] });
        var mail = icone(c, "mail", "ICÔNE — E-mail");
        var tMail = texte(c, { nom: "TXT_SC04_04 — E-mail", texte: CONTACT.mail, graisse: "b", taille: 40, couleur: C.BLEU, pos: [960, 830] });
        rangee([{ l: web, ecart: 18 }, { l: tWeb, ecart: 80 }, { l: mail, ecart: 18 }, { l: tMail }], 960, 830);

        var fb = icone(c, "facebook", "ICÔNE — Facebook");
        var ig = icone(c, "instagram", "ICÔNE — Instagram");
        var wa = icone(c, "whatsapp", "ICÔNE — WhatsApp");
        var tRs = texte(c, { nom: "TXT_SC04_05 — Réseaux sociaux", texte: CONTACT.reseaux, graisse: "b", taille: 40, couleur: C.BLEU, pos: [960, 910] });
        var lieu = icone(c, "lieu", "ICÔNE — Localisation");
        var tLieu = texte(c, { nom: "TXT_SC04_06 — Localisation", texte: CONTACT.lieu, graisse: "b", taille: 40, couleur: C.BLEU, pos: [960, 910] });
        rangee([{ l: fb, ecart: 12 }, { l: ig, ecart: 12 }, { l: wa, ecart: 18 }, { l: tRs, ecart: 80 }, { l: lieu, ecart: 18 }, { l: tLieu }], 960, 910);

        var lignes = [[tel, tTel], [web, tWeb, mail, tMail], [fb, ig, wa, tRs, lieu, tLieu]];
        for (var i = 0; i < lignes.length; i++) {
            for (var j = 0; j < lignes[i].length; j++) {
                temps(lignes[i][j], 5.5 + i * 0.5, fin);
                animer(lignes[i][j], "slide", { dy: 40, sortie: false });
            }
        }

        rattacher(c, cam);
        expression(tr(cam, "ADBE Scale"), EXPR.pushIn(2), "CAM_SC04 / push-in");
        return c;
    }

    // =================================================================
    // 6. COMPOSITION PRINCIPALE : transitions, ajustement, marqueurs, guides
    // =================================================================

    // Volet : deux bandes (tête + traîne) qui couvrent tout l'écran à t = coupe
    function volet(main, nom, coupe, sens, cTete, cTraine) {
        var l = forme(main, nom);
        groupe(l, { nom: "Bande de tête", formes: [{ type: "rect", taille: [2200, 1300] }], fond: cTete });
        groupe(l, { nom: "Bande de traîne", formes: [{ type: "rect", taille: [2200, 1300], pos: [-sens * 300, 0] }], fond: cTraine });
        temps(l, coupe - 0.45, coupe + 0.45);
        var x0 = (sens > 0) ? -1500 : 3420;
        var x1 = (sens > 0) ? 3420 : -1500;
        expression(tr(l, "ADBE Position"), [
            "// Volet : traverse l'écran et le couvre entièrement à t = " + n(coupe) + " s (coupe franche dessous)",
            "var x = ease(time, " + n(coupe - 0.45) + ", " + n(coupe + 0.45) + ", " + x0 + ", " + x1 + ");",
            "[x, value[1]];"
        ].join("\n"), nom);
        l.motionBlur = true;
        l.label = 11;
        return l;
    }

    // Iris : disque or qui se referme sur la coupe puis se dissout
    function iris(main, nom, coupe) {
        var l = forme(main, nom);
        groupe(l, { nom: "Disque or", formes: [{ type: "ellipse", taille: [2300, 2300] }], fond: C.OR });
        temps(l, coupe - 0.45, coupe + 0.4);
        expression(tr(l, "ADBE Scale"), [
            "// Iris : 0 % → 100 % jusqu'à la coupe (" + n(coupe) + " s)",
            "var s = ease(time, inPoint, " + n(coupe) + ", 0, 100);",
            "[s, s];"
        ].join("\n"), nom + " / échelle");
        expression(tr(l, "ADBE Opacity"), [
            "// Dissolution après la coupe",
            "ease(time, " + n(coupe) + ", outPoint, 100, 0);"
        ].join("\n"), nom + " / opacité");
        l.label = 11;
        return l;
    }

    function ajustementFinal(main) {
        var l = main.layers.addSolid(C.BLANC, "ADJ_FINAL — Lueur · Grain · Aberration · Étalonnage", W, H, 1, main.duration);
        l.adjustmentLayer = true;
        l.source.parentFolder = F.ajust;
        l.label = 5;

        // 1) Lueur (Glow) : seuil, rayon, intensité
        var fx;
        try {
            fx = l.property("ADBE Effect Parade").addProperty("ADBE Glo2");
            fx.name = "Lueur douce";
            reglerPct(fx, ["ADBE Glo2-0002", "Glow Threshold", "Seuil de lueur"], 85, "Lueur / seuil");
            regler(fx, ["ADBE Glo2-0003", "Glow Radius", "Rayon de lueur"], 22, "Lueur / rayon");
            regler(fx, ["ADBE Glo2-0004", "Glow Intensity", "Intensité de lueur"], 0.3, "Lueur / intensité");
        } catch (e1) {
            note("[!] Effet Lueur indisponible.");
        }

        // 2) Grain : Bruit 5–8 % animé par posterizeTime(12) + wiggle(10, 10)
        try {
            fx = l.property("ADBE Effect Parade").addProperty("ADBE Noise");
            fx.name = "Grain";
            reglerPct(fx, ["ADBE Noise-0001", "Amount of Noise", "Quantité de bruit"], 6.5, "Grain / quantité");
            regler(fx, ["ADBE Noise-0002", "Use Color Noise", "Utiliser du bruit de couleur"], 0, "Grain / monochrome");
            expression(prop(fx, ["ADBE Noise-0001", "Amount of Noise", "Quantité de bruit"]), EXPR.grain(5, 8), "Grain / expression");
        } catch (e2) {
            note("[!] Effet Bruit indisponible.");
        }

        // 3) Aberration chromatique : Quick Chromatic Aberration si installé
        var ca = trouverEffet(/quick\s*chromatic/i) || trouverEffet(/chromati/i, /VR/);
        if (ca) {
            try {
                fx = l.property("ADBE Effect Parade").addProperty(ca.matchName);
                fx.name = "Aberration chromatique";
                note("[OK] Aberration chromatique : « " + ca.displayName + " » ajoutée (doser l'intensité au plus bas, 1 à 3 px).");
            } catch (e3) {
                note("[!] Aberration chromatique trouvée mais non applicable : " + ca.displayName);
            }
        } else {
            note("[!] Quick Chromatic Aberration non installé : installez le plug-in (gratuit) puis ajoutez-le sur ADJ_FINAL, entre « Grain » et « Étalonnage léger ».");
        }

        // 4) Étalonnage léger (en haut de la pile) : ombres bleutées, blancs à peine chauds
        try {
            fx = l.property("ADBE Effect Parade").addProperty("ADBE Tint");
            fx.name = "Étalonnage léger";
            regler(fx, ["ADBE Tint-0001", "Map Black To", "Remplacer le noir par"], C.BLEU_NUIT, "Étalonnage / noirs");
            regler(fx, ["ADBE Tint-0002", "Map White To", "Remplacer le blanc par"], melange(C.BLANC, C.OR, 0.04), "Étalonnage / blancs");
            reglerPct(fx, ["ADBE Tint-0003", "Amount to Tint", "Quantité de teinte"], 8, "Étalonnage / quantité");
        } catch (e4) {
            note("[!] Effet Teinte indisponible : étalonnage à faire à la main (Lumetri).");
        }
        return l;
    }

    // Recherche d'un effet installé (nom affiché ou matchName)
    function trouverEffet(re, exclure) {
        try {
            for (var i = 0; i < app.effects.length; i++) {
                var e = app.effects[i];
                var nom = e.displayName + " " + e.matchName;
                if (re.test(nom) && !(exclure && exclure.test(nom))) {
                    return e;
                }
            }
        } catch (er) {}
        return null;
    }

    // Marqueurs de scène (chronologie de la composition)
    function marqueurs(main) {
        var cible = null;
        try {
            cible = main.markerProperty;
        } catch (e) {}
        if (!cible) {
            var nl = main.layers.addNull(main.duration);
            nl.name = "MARQUEURS — Scènes";
            nl.source.parentFolder = F.assets;
            cible = nl.property("ADBE Marker");
            note("[!] Marqueurs de composition non scriptables dans cette version : posés sur le calque « MARQUEURS — Scènes ».");
        }
        for (var i = 0; i < SCENES.length; i++) {
            var s = SCENES[i];
            var mv = new MarkerValue(s.titre + " (" + tc(s.debut) + " → " + tc(s.fin) + ")");
            mv.duration = s.fin - s.debut;
            try {
                mv.label = i + 1;
            } catch (e2) {}
            cible.setValueAtTime(s.debut, mv);
        }
        var mf = new MarkerValue("FIN — 01:00 (dernière image : 00:59:29)");
        cible.setValueAtTime(main.duration - 1 / CONFIG.fps, mf);
    }

    // Repères de voix off (calque null guide, un marqueur par réplique)
    function voSync(main) {
        var l = main.layers.addNull(main.duration);
        l.name = "VO_SYNC — Repères voix off";
        l.source.parentFolder = F.assets;
        l.guideLayer = true;
        l.label = 14;
        var mk = l.property("ADBE Marker");
        for (var i = 0; i < VO.length; i++) {
            var mv = new MarkerValue("VO " + (i + 1) + " — « " + VO[i].texte + " »");
            mv.duration = VO[i].fin - VO[i].debut;
            mk.setValueAtTime(VO[i].debut, mv);
        }
        return l;
    }

    // Guides de composition + calque guide des zones de sécurité
    function guides(main) {
        var v = [192, 640, 960, 1280, 1728];
        var h = [108, 360, 540, 720, 972];
        var ok = true;
        try {
            for (var i = 0; i < v.length; i++) {
                main.addGuide(1, v[i]);   // 1 = vertical
            }
            for (var j = 0; j < h.length; j++) {
                main.addGuide(0, h[j]);   // 0 = horizontal
            }
        } catch (e) {
            ok = false;
        }
        note(ok ? "[OK] Guides posés : tiers, centre et zone titre (10 %)."
                : "[!] Guides non scriptables dans cette version : utilisez le calque « GUIDES — Zones de sécurité ».");

        var l = forme(main, "GUIDES — Zones de sécurité (non rendu)");
        groupe(l, { nom: "Action safe 90 %", formes: [{ type: "rect", taille: [1728, 972] }], contour: C.OR, epaisseur: 2 });
        groupe(l, { nom: "Title safe 80 %", formes: [{ type: "rect", taille: [1536, 864] }], contour: C.REPERE, epaisseur: 2 });
        groupe(l, { nom: "Croix centrale", formes: [
            { type: "trace", pts: [[-40, 0], [40, 0]], ferme: false },
            { type: "trace", pts: [[0, -40], [0, 40]], ferme: false }
        ], contour: C.REPERE, epaisseur: 2 });
        groupe(l, { nom: "Tiers", formes: [
            { type: "trace", pts: [[-320, -540], [-320, 540]], ferme: false },
            { type: "trace", pts: [[320, -540], [320, 540]], ferme: false },
            { type: "trace", pts: [[-960, -180], [960, -180]], ferme: false },
            { type: "trace", pts: [[-960, 180], [960, 180]], ferme: false }
        ], contour: C.BLANC, epaisseur: 1 });
        l.guideLayer = true;
        l.label = 1;
        l.locked = true;
    }

    // Audio facultatif : assets/audio/voix_off.* et assets/audio/musique.*
    function audio(main) {
        var pistes = [
            { nom: "AUDIO — Voix off", fichiers: ["audio/voix_off.wav", "audio/voix_off.mp3"], niveau: 0 },
            { nom: "AUDIO — Musique", fichiers: ["audio/musique.wav", "audio/musique.mp3"], niveau: -14 }
        ];
        var trouve = 0;
        for (var i = 0; i < pistes.length; i++) {
            for (var j = 0; j < pistes[i].fichiers.length; j++) {
                var it = importer(pistes[i].fichiers[j], F.audio);
                if (it) {
                    var l = main.layers.add(it);
                    l.name = pistes[i].nom;
                    l.moveToEnd();
                    try {
                        l.property("ADBE Audio Group").property("ADBE Audio Levels").setValue([pistes[i].niveau, pistes[i].niveau]);
                    } catch (e) {}
                    trouve++;
                    break;
                }
            }
        }
        if (trouve === 0) {
            note("[i] 03_AUDIO vide : déposez voix_off.wav et musique.wav dans assets/audio/ puis relancez, ou importez-les à la main.");
        } else {
            note("[OK] Pistes audio importées : " + trouve + ".");
        }
    }

    // Supprime le dossier « Solids / Solides » créé automatiquement s'il est vide
    function nettoyerSolides() {
        var racine = app.project.rootFolder;
        for (var i = racine.numItems; i >= 1; i--) {
            var it = racine.item(i);
            if (it instanceof FolderItem && (it.name === "Solids" || it.name === "Solides") && it.numItems === 0) {
                try {
                    it.remove();
                } catch (e) {}
            }
        }
    }

    // Vérifications demandées par le brief
    function verifier(main, calquesScenes) {
        var ok = true;
        if (Math.abs(main.duration - 60) > 0.0001) {
            ok = false;
            note("[!] Durée de la composition : " + main.duration + " s (attendu : 60 s).");
        }
        if (Math.abs(main.frameRate - 30) > 0.0001 || main.width !== 1920 || main.height !== 1080) {
            ok = false;
            note("[!] Paramètres de composition inattendus.");
        }
        for (var i = 0; i < calquesScenes.length; i++) {
            var l = calquesScenes[i];
            if (Math.abs(l.inPoint - SCENES[i].debut) > 0.0001 || Math.abs(l.outPoint - SCENES[i].fin) > 0.0001) {
                ok = false;
                note("[!] " + SCENES[i].nom + " : " + l.inPoint + " → " + l.outPoint + " s (attendu " + SCENES[i].debut + " → " + SCENES[i].fin + ").");
            }
            if (i > 0 && Math.abs(l.inPoint - calquesScenes[i - 1].outPoint) > 0.0001) {
                ok = false;
                note("[!] Discontinuité entre " + SCENES[i - 1].nom + " et " + SCENES[i].nom + ".");
            }
        }
        if (ok) {
            note("[OK] 1920×1080, 30 i/s, 60 s ; scènes contiguës 00:00 → 00:15 → 00:35 → 00:50 → 01:00 (1 800 images).");
        }
        note((STATS.tailleMin >= 40 ? "[OK]" : "[!]") + " Plus petit corps de texte affiché : " + STATS.tailleMin + " px (minimum retenu : 40 px en 1080p).");
        if (CONFIG.stylesDeCalque && (STATS.styles > 0 || STATS.stylesEchecs > 0)) {
            note("[i] Styles de calque appliqués sur " + STATS.styles + " calque(s)" + (STATS.stylesEchecs ? ", " + STATS.stylesEchecs + " échec(s)" : "") + ". Couleurs du dégradé à régler à la main (non scriptables).");
        }
    }

    // =================================================================
    // 7. CONSTRUCTION
    // =================================================================
    function construire() {
        if (!app.project) {
            app.newProject();
        }

        // Dossiers
        F.comps = dossier(CONFIG.dossiers.comps);
        F.assets = dossier(CONFIG.dossiers.assets);
        F.audio = dossier(CONFIG.dossiers.audio);
        F.ajust = dossier(CONFIG.dossiers.ajust);

        // Composition principale
        for (var k = 1; k <= app.project.numItems; k++) {
            var it = app.project.item(k);
            if (it instanceof CompItem && it.name === CONFIG.nomComp) {
                note("[i] Une composition « " + CONFIG.nomComp + " » existait déjà : une nouvelle a été créée à côté.");
                break;
            }
        }
        var main = app.project.items.addComp(CONFIG.nomComp, W, H, 1, CONFIG.duree, CONFIG.fps);
        main.parentFolder = F.comps;
        main.bgColor = C.BLANC;
        main.motionBlur = true;

        choisirPolices(main);

        // Logo
        LOGO.complet = importer("logo_justvyou.png", F.assets);
        LOGO.symbole = importer("logo_symbole.png", F.assets);
        LOGO.texte = importer("logo_texte.png", F.assets);
        if (LOGO.complet && LOGO.symbole && LOGO.texte) {
            note("[OK] Logo importé depuis assets/ (3 PNG).");
        } else {
            note("[!] PNG du logo absents de « " + DOSSIER_SCRIPT + "/assets » : logo vectoriel de repli utilisé.");
        }

        // Scènes (pré-compositions)
        var comps = [scene1(), scene2(), scene3(), scene4()];
        var noms = ["SC01 — Client perdu", "SC02 — Découverte & services", "SC03 — Famille satisfaite", "SC04 — Logo & contacts"];
        var calquesScenes = [];
        for (var i = 0; i < comps.length; i++) {
            var l = main.layers.add(comps[i]);
            l.startTime = SCENES[i].debut;
            l.name = noms[i] + " (" + tc(SCENES[i].debut) + "–" + tc(SCENES[i].fin) + ")";
            l.label = 10 + i;
            calquesScenes.push(l);
        }

        // Transitions au-dessus des scènes
        volet(main, "TR_01 — Volet or / bleu (00:15)", 15, 1, C.OR, C.BLEU);
        volet(main, "TR_02 — Volet bleu / or (00:35)", 35, -1, C.BLEU, C.OR);
        iris(main, "TR_03 — Iris or (00:50)", 50);

        // Ajustement final, repères, guides, audio
        ajustementFinal(main);
        voSync(main);
        marqueurs(main);
        guides(main);
        audio(main);
        nettoyerSolides();

        verifier(main, calquesScenes);

        main.openInViewer();
        main.time = 0;
    }

    // =================================================================
    // 8. EXÉCUTION
    // =================================================================
    app.beginUndoGroup("Spot Justvyou Property 60 s");
    try {
        construire();
        RAPPORT.unshift("SPOT_JUSTVYOU_60S créé. Police : " + NOM_POLICE + ".", "");
        RAPPORT.push("", "À faire à la main : personnages (repères rouges « À ANIMER »), masques adoucis, rim lights peau, voix off et musique, rendu.");
    } catch (err) {
        RAPPORT.unshift("ERREUR : " + err.toString() + (err.line ? " (ligne " + err.line + ")" : ""), "Le projet peut être partiellement construit : Édition > Annuler pour revenir en arrière.", "");
    } finally {
        app.endUndoGroup();
    }
    $.writeln(RAPPORT.join("\n"));
    alert(RAPPORT.join("\n"), "Justvyou Property — rapport");

})();
