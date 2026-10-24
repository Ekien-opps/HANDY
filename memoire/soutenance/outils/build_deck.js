// Deck de soutenance — American's Gym (CAMARA BINTOU ÉPSE HOZAN)
// Contenu : mémoire assemblé ; visuels : mémoire + travaux.zip
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const Lu = require("react-icons/lu");
const sizeMod = require("image-size");
const sizeOf = sizeMod.imageSize || sizeMod.default || sizeMod;
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const A = (f) => path.join(__dirname, "assets", f);
const OUT = process.argv[2] || path.join(__dirname, "soutenance.pptx");

// ---------------------------------------------------------------- charte
const HEX = {
  navy: "1D3557", red: "E63946", white: "FFFFFF", metal: "A8DADC",
  ink: "2B3A4F", tint: "EEF2F6", muted: "6B7A90", deep: "142640",
};
const THEME = {
  name: "American's Gym",
  headFontFace: "Poppins ExtraBold",
  bodyFontFace: "Poppins",
  colors: {
    dk1: HEX.navy, lt1: HEX.white, dk2: HEX.ink, lt2: HEX.tint,
    accent1: HEX.red, accent2: HEX.metal, accent3: HEX.navy, accent4: HEX.muted,
    accent5: HEX.deep, accent6: "F7D7DA", hlink: HEX.red, folHlink: HEX.navy,
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.author = "CAMARA BINTOU ÉPSE HOZAN";
pres.company = "ISTC Polytechnique";
pres.title = "Soutenance — Supports de communication American's Gym";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333, H = 7.5, X = 0.75, CW = W - 2 * X;

// ---------------------------------------------------------------- layouts
const footer = "CAMARA BINTOU ÉPSE HOZAN  ·  Licence professionnelle Arts et Images Numériques  ·  ISTC Polytechnique";
pres.defineSlideMaster({
  title: "AG_CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "eyebrow", type: "body", x: X, y: 0.5, w: CW, h: 0.34, fontSize: 11, bold: true,
        color: C.accent1, charSpacing: 2, margin: 0, valign: "top", align: "left" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: X, y: 0.84, w: CW, h: 1.0, fontSize: 30,
        fontFace: THEME.headFontFace, color: C.text1, margin: 0, valign: "top", align: "left" }, text: "" } },
    { text: { text: footer, options: { x: X, y: 6.98, w: 10, h: 0.28, fontSize: 9, color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: W - X - 0.6, y: 6.98, w: 0.6, h: 0.28, fontSize: 9, color: C.accent4, align: "right", margin: 0 },
});
pres.defineSlideMaster({
  title: "AG_DIVIDER",
  background: { color: C.text1 },
  objects: [
    { image: { path: A("logo_ag.png"), x: W - X - 1.25, y: 6.25, w: 1.25, h: 1.25 * 314 / 414 } },
    { placeholder: { options: { name: "num", type: "body", x: X, y: 2.15, w: 4, h: 1.5, fontSize: 80,
        fontFace: THEME.headFontFace, color: C.accent1, margin: 0, valign: "bottom", align: "left" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: X, y: 3.75, w: 10.5, h: 1.3, fontSize: 40,
        fontFace: THEME.headFontFace, color: C.background1, margin: 0, valign: "top", align: "left" }, text: "" } },
  ],
  slideNumber: { x: W - X - 0.6, y: 0.5, w: 0.6, h: 0.28, fontSize: 9, color: C.accent2, align: "right", margin: 0 },
});
pres.defineSlideMaster({
  title: "AG_STATEMENT",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "eyebrow", type: "body", x: X, y: 1.25, w: CW, h: 0.34, fontSize: 11, bold: true,
        color: C.accent2, charSpacing: 2, margin: 0, valign: "top", align: "left" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: X, y: 1.8, w: 10.6, h: 3.9, fontSize: 30,
        fontFace: THEME.headFontFace, color: C.background1, margin: 0, valign: "top", align: "left", lineSpacingMultiple: 1.1 }, text: "" } },
  ],
  slideNumber: { x: W - X - 0.6, y: 6.98, w: 0.6, h: 0.28, fontSize: 9, color: C.accent2, align: "right", margin: 0 },
});
pres.defineSlideMaster({ title: "AG_TITLE", background: { color: C.text1 }, objects: [] });

// ---------------------------------------------------------------- helpers
const iconCache = {};
async function icon(name, hex, px = 256) {
  const key = name + hex;
  if (!iconCache[key]) {
    const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Lu[name], { color: "#" + hex, size: px, strokeWidth: 1.75 }));
    const buf = await sharp(Buffer.from(svg)).resize(px, px).png().toBuffer();
    iconCache[key] = "image/png;base64," + buf.toString("base64");
  }
  return iconCache[key];
}
function fit(file, x, y, w, h, align = "c") {
  const d = sizeOf(fs.readFileSync(A(file)));
  const r = Math.min(w / d.width, h / d.height);
  const iw = d.width * r, ih = d.height * r;
  const ix = align === "l" ? x : align === "r" ? x + w - iw : x + (w - iw) / 2;
  return { x: ix, y: y + (h - ih) / 2, w: iw, h: ih };
}
const shadow = () => ({ type: "outer", color: HEX.navy, opacity: 0.16, blur: 14, offset: 4, angle: 90 });
function img(s, file, box, name, opts = {}) {
  const b = fit(file, box.x, box.y, box.w, box.h, opts.align);
  s.addImage({ path: A(file), ...b, objectName: name, altText: opts.alt || name,
    ...(opts.noShadow ? {} : { shadow: shadow() }) });
  return b;
}
function text(s, t, o, name) {
  s.addText(t, { isTextBox: true, margin: 0, fontSize: 16, color: C.text2, valign: "top", objectName: name, ...o });
}
function card(s, x, y, w, h, name, fill = C.background2) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { type: "none" }, objectName: name });
}
async function iconDisc(s, ic, x, y, d, name, bg = C.text1, fg = HEX.white) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { type: "none" }, objectName: name + "_disc" });
  const p = d * 0.25;
  s.addImage({ data: await icon(ic, fg), x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p, objectName: name + "_ico", altText: "" });
}
function content(sec, eyebrow, title, notes) {
  const s = pres.addSlide({ masterName: "AG_CONTENT", sectionTitle: sec });
  s.addText(eyebrow, { placeholder: "eyebrow" });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function divider(sec, num, title, notes) {
  pres.addSection({ title: sec });
  const s = pres.addSlide({ masterName: "AG_DIVIDER", sectionTitle: sec });
  s.addText(num, { placeholder: "num" });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function caption(s, t, x, y, w, name, align = "left") {
  text(s, t, { x, y, w, h: 0.3, fontSize: 11, color: C.accent4, align }, name);
}

(async () => {
  // =========================================================== 1. Titre
  pres.addSection({ title: "Ouverture" });
  let s = pres.addSlide({ masterName: "AG_TITLE", sectionTitle: "Ouverture" });
  card(s, X, 0.55, 1.55, 1.2, "T_istc_chip", C.background1);
  s.addImage({ path: A("logo_istc.png"), ...fit("logo_istc.png", X + 0.12, 0.62, 1.31, 1.06), objectName: "T_istc", altText: "Logo ISTC Polytechnique" });
  text(s, "SOUTENANCE DE LICENCE PROFESSIONNELLE  ·  ARTS ET IMAGES NUMÉRIQUES  ·  2025-2026",
    { x: X, y: 2.2, w: 9.2, h: 0.3, fontSize: 10, bold: true, color: C.accent2, charSpacing: 1 }, "T_eyebrow");
  text(s, "Conception et réalisation de supports de communication pour la promotion de la structure de sport « American’s Gym »",
    { x: X, y: 2.6, w: 8.2, h: 2.0, fontSize: 28, fontFace: THEME.headFontFace, color: C.background1, lineSpacingMultiple: 1.05 }, "T_title");
  s.addImage({ path: A("logo_ag.png"), ...fit("logo_ag.png", 9.25, 1.9, 3.35, 3.0), objectName: "T_logo", altText: "Logo American's Gym" });
  text(s, [
    { text: "Présenté par  ", options: { color: C.accent2 } },
    { text: "CAMARA BINTOU ÉPSE HOZAN", options: { bold: true, color: C.background1 } },
  ], { x: X, y: 5.2, w: 8.4, h: 0.4, fontSize: 16 }, "C1_presente");
  text(s, [
    { text: "Directeur de mémoire  ", options: { color: C.accent2 } },
    { text: "M. Chafick ADJIBADÉ", options: { color: C.background1 } },
  ], { x: X, y: 5.85, w: 5.4, h: 0.35, fontSize: 12 }, "C1_directeur");
  text(s, [
    { text: "Superviseur  ", options: { color: C.accent2 } },
    { text: "Prof. TOA AGNINI Jules Évariste", options: { color: C.background1 } },
  ], { x: X + 5.6, y: 5.85, w: 6.3, h: 0.35, fontSize: 12 }, "C1_superviseur");
  s.addNotes("Mesdames et Messieurs les membres du jury, je vous présente mon mémoire de Licence professionnelle en Arts et Images Numériques : la conception et la réalisation de supports de communication pour la promotion de la structure de sport American's Gym. Travail dirigé par M. Chafick ADJIBADÉ, sous la supervision du Prof. TOA AGNINI Jules Évariste.");

  // =========================================================== 2. Plan
  s = content("Ouverture", "PLAN", "Plan de la présentation",
    "La présentation suit le plan du mémoire : introduction et problématique, cadre d'étude, étude technique, réalisation des supports, puis conclusion.");
  const plan = ["Introduction et problématique", "Cadre d’étude", "Étude technique", "Réalisation des supports", "Conclusion"];
  plan.forEach((p, i) => {
    const y = 2.1 + i * 0.9;
    text(s, "0" + (i + 1), { x: X, y, w: 1.2, h: 0.7, fontSize: 30, fontFace: THEME.headFontFace, color: C.accent1, valign: "middle" }, "C1_n" + i);
    text(s, p, { x: X + 1.3, y, w: 8, h: 0.7, fontSize: 22, bold: true, color: C.text1, valign: "middle" }, "C1_t" + i);
    if (i < 4) s.addShape(pres.shapes.LINE, { x: X + 1.3, y: y + 0.8, w: 7.5, h: 0, line: { color: "D5DCE5", width: 1 }, objectName: "C1_sep" + i });
  });
  s.addImage({ path: A("logo_ag.png"), ...fit("logo_ag.png", 9.4, 2.4, 3.2, 3.6), objectName: "C1_logo", altText: "Logo American's Gym" });

  // =========================================================== 01 Introduction
  divider("01 · Introduction", "01", "Introduction et problématique",
    "Je commence par le contexte et la question qui a guidé ce travail.");

  s = content("01 · Introduction", "01  ·  INTRODUCTION", "La communication, un levier stratégique",
    "Le secteur du sport et du fitness connaît un essor des salles et des agences spécialisées. Pour se démarquer, une structure comme American's Gym doit s'appuyer sur des supports adaptés à sa cible et à son positionnement, afin d'accroître sa notoriété, d'attirer de nouveaux adhérents et de fidéliser sa clientèle.");
  text(s, "Avec l’essor des salles de sport, il devient essentiel de se démarquer par des actions de communication efficaces, cohérentes et innovantes.",
    { x: X, y: 2.15, w: 9.6, h: 0.95, fontSize: 18, color: C.text2 }, "C1_lead");
  const intro = [["LuMegaphone", "Accroître sa notoriété"], ["LuUserPlus", "Attirer de nouveaux adhérents"], ["LuHeartHandshake", "Fidéliser sa clientèle"]];
  const iw3 = (CW - 2 * 0.35) / 3;
  for (let i = 0; i < 3; i++) {
    const x = X + i * (iw3 + 0.35);
    card(s, x, 3.6, iw3, 2.6, "C2_card" + i);
    await iconDisc(s, intro[i][0], x + 0.4, 3.95, 0.9, "C2_i" + i);
    text(s, intro[i][1], { x: x + 0.4, y: 5.1, w: iw3 - 0.8, h: 0.8, fontSize: 18, bold: true, color: C.text1 }, "C2_t" + i);
  }

  s = pres.addSlide({ masterName: "AG_STATEMENT", sectionTitle: "01 · Introduction" });
  s.addText("PROBLÉMATIQUE", { placeholder: "eyebrow" });
  s.addText([
    { text: "Comment la conception et la réalisation de supports de communication imprimés et numériques peuvent-elles contribuer à " },
    { text: "améliorer la visibilité", options: { color: C.accent2 } },
    { text: ", " },
    { text: "renforcer l’image de marque", options: { color: C.accent2 } },
    { text: " et " },
    { text: "promouvoir efficacement les activités", options: { color: C.accent2 } },
    { text: " d’American’s Gym ?" },
  ], { placeholder: "title" });
  s.addNotes("Malgré la diversité de ses activités et la qualité de ses prestations, American's Gym souffre d'une visibilité limitée, faute de supports de communication professionnels et harmonisés. D'où la question centrale de l'étude.");

  s = content("01 · Introduction", "01  ·  OBJECTIFS", "Quatre objectifs",
    "Pour répondre à cette question, l'étude poursuit quatre objectifs : une identité visuelle cohérente, des supports imprimés, des contenus audiovisuels 2D et 3D, et un site web moderne.");
  const obj = [["LuPalette", "Une identité visuelle cohérente"], ["LuPrinter", "Des supports imprimés"],
    ["LuClapperboard", "Des contenus audiovisuels 2D et 3D"], ["LuGlobe", "Un site web moderne"]];
  const ow = (CW - 0.35) / 2;
  for (let i = 0; i < 4; i++) {
    const x = X + (i % 2) * (ow + 0.35), y = 2.2 + Math.floor(i / 2) * 2.15;
    card(s, x, y, ow, 1.85, `C${i + 1}_card`);
    await iconDisc(s, obj[i][0], x + 0.4, y + 0.47, 0.9, `C${i + 1}_i`);
    text(s, obj[i][1], { x: x + 1.65, y: y + 0.4, w: ow - 2.05, h: 1.05, fontSize: 18, bold: true, color: C.text1, valign: "middle" }, `C${i + 1}_t`);
  }

  s = content("01 · Introduction", "01  ·  HYPOTHÈSE", "Hypothèse de recherche",
    "L'hypothèse retenue : une stratégie de communication fondée sur des supports graphiques et numériques professionnels permettra d'améliorer significativement la notoriété d'American's Gym, de renforcer son image de marque et d'accroître sa capacité à attirer et fidéliser sa clientèle.");
  text(s, "Des supports graphiques et numériques professionnels permettront :",
    { x: X, y: 2.25, w: CW, h: 0.6, fontSize: 18, color: C.text2 }, "C1_lead");
  const hyp = [["LuTrendingUp", "D’améliorer la notoriété"], ["LuAward", "De renforcer l’image de marque"], ["LuUsers", "D’attirer et fidéliser la clientèle"]];
  for (let i = 0; i < 3; i++) {
    const x = X + i * (iw3 + 0.35);
    card(s, x, 3.6, iw3, 2.6, "C2_card" + i);
    await iconDisc(s, hyp[i][0], x + 0.4, 3.95, 0.9, "C2_i" + i, C.accent1);
    text(s, hyp[i][1], { x: x + 0.4, y: 5.1, w: iw3 - 0.8, h: 0.8, fontSize: 18, bold: true, color: C.text1 }, "C2_t" + i);
  }

  // =========================================================== 02 Cadre d'étude
  divider("02 · Cadre d’étude", "02", "Cadre d’étude",
    "Deuxième temps : la structure étudiée et l'analyse de sa communication existante.");

  s = content("02 · Cadre d’étude", "02  ·  LA STRUCTURE", "Un brassage Côte d’Ivoire – États-Unis",
    "American's Gym Dokui est un club de fitness, de musculation et de sports de combat situé à Abidjan, dans le quartier d'Abobo-Dokui. Son concept associe des équipements de musculation et de cardio-training importés des États-Unis à un accueil adapté aux réalités ivoiriennes. La direction est assurée par le PDG Djakaria KONATÉ.");
  const facts = [["LuDumbbell", "Fitness, musculation et sports de combat"], ["LuMapPin", "Implanté à Abobo-Dokui, Abidjan"],
    ["LuFlag", "Équipements importés des États-Unis"], ["LuUsers", "Dirigé par Djakaria KONATÉ, PDG"]];
  for (let i = 0; i < 4; i++) {
    const y = 2.25 + i * 1.08;
    await iconDisc(s, facts[i][0], X, y, 0.72, `C${i < 2 ? 1 : 2}_f${i}`, C.background2, HEX.navy);
    text(s, facts[i][1], { x: X + 1.0, y: y + 0.06, w: 6.4, h: 0.6, fontSize: 17, color: C.text1, valign: "middle" }, `C${i < 2 ? 1 : 2}_ft${i}`);
  }
  img(s, "equipe.jpg", { x: 8.55, y: 1.95, w: 4.0, h: 4.8 }, "C3_equipe", { alt: "Affiche de présentation de l'équipe d'American's Gym" });

  s = content("02 · Cadre d’étude", "02  ·  LES SERVICES", "Une offre diversifiée et inclusive",
    "Musculation et fitness avec coaching personnalisé ; sports de combat (boxe anglaise / pieds-poings et taekwondo) ; une offre inclusive avec des séances dédiées aux femmes voilées ; enfin la vente de compléments alimentaires et de produits de soin.");
  const serv = [["LuDumbbell", "Musculation et fitness"], ["LuSwords", "Boxe et taekwondo"],
    ["LuHeart", "Séances dédiées aux femmes voilées"], ["LuShoppingBag", "Compléments et soins"]];
  const sw4 = (CW - 3 * 0.3) / 4;
  for (let i = 0; i < 4; i++) {
    const x = X + (i % 2) * (ow + 0.35), y = 2.2 + Math.floor(i / 2) * 2.15;
    card(s, x, y, ow, 1.85, "C1_card" + i);
    await iconDisc(s, serv[i][0], x + 0.4, y + 0.47, 0.9, "C1_i" + i, i === 2 ? C.accent1 : C.text1);
    text(s, serv[i][1], { x: x + 1.65, y: y + 0.4, w: ow - 2.05, h: 1.05, fontSize: 18, bold: true, color: C.text1, valign: "middle" }, "C1_t" + i);
  }

  s = content("02 · Cadre d’étude", "02  ·  CANAUX DIGITAUX", "Une présence numérique déjà active",
    "Facebook : une page active d'environ 1 300 abonnés, surtout des vidéos d'ambiance et des fiches produits. TikTok : environ 27 900 mentions J'aime, axé sur le coaching en direct. Une boutique en ligne hébergée sur Shopify (le mémoire écrit « Spotify » p. 10 : coquille à corriger).");
  const stats = [["≈ 1 300", "abonnés sur Facebook"], ["27 900", "mentions « J’aime » sur TikTok"], ["Shopify", "boutique en ligne"]];
  stats.forEach((st, i) => {
    const y = 2.2 + i * 1.5;
    text(s, st[0], { x: X, y, w: 5.6, h: 0.8, fontSize: 40, fontFace: THEME.headFontFace, color: i === 2 ? C.text1 : C.accent1 }, "C1_sn" + i);
    text(s, st[1], { x: X, y: y + 0.78, w: 5.6, h: 0.4, fontSize: 15, color: C.text2 }, "C1_sl" + i);
  });
  img(s, "tiktok.jpg", { x: 7.0, y: 1.95, w: 2.65, h: 4.75 }, "C2_tiktok", { alt: "Capture du compte TikTok" });
  img(s, "facebook.jpg", { x: 9.9, y: 1.95, w: 2.65, h: 4.75 }, "C2_facebook", { alt: "Capture de la page Facebook" });

  s = content("02 · Cadre d’étude", "02  ·  CRITIQUE DE L’EXISTANT", "Une image de marque fragilisée",
    "Logo d'origine puissant mais mention DOKUI ajoutée sans respect des proportions ; affiches produits aux codes vert fluo ou marron déconnectés de l'identité ; lien boutique shopify.com non personnalisé et identifiant TikTok @amricains.gym.dok mal orthographié ; ligne éditoriale de type catalogue et vidéos brutes sans montage. Conséquences : baisse de crédibilité et déficit d'image face à la concurrence.");
  img(s, "logo_ancien.jpg", { x: X, y: 2.15, w: 3.9, h: 3.6 }, "C1_logo", { alt: "Logo existant avec la mention DOKUI" });
  caption(s, "Logo existant, mention « DOKUI » ajoutée", X, 5.95, 3.9, "C1_cap");
  const crit = ["Logo décliné sans respect de la charte", "Visuels promotionnels sans code couleur commun",
    "Lien boutique non personnalisé, identifiant TikTok mal orthographié", "Ligne éditoriale confuse, vidéos brutes"];
  for (let i = 0; i < 4; i++) {
    const y = 2.15 + i * 1.12;
    text(s, "0" + (i + 1), { x: 5.3, y, w: 0.7, h: 0.5, fontSize: 18, fontFace: THEME.headFontFace, color: C.accent1 }, `C${i + 2}_n`);
    text(s, crit[i], { x: 6.05, y: y + 0.02, w: 6.5, h: 0.9, fontSize: 17, color: C.text1 }, `C${i + 2}_t`);
  }

  // =========================================================== 03 Étude technique
  divider("03 · Étude technique", "03", "Étude technique",
    "Troisième temps : le cahier des charges et la nouvelle identité visuelle.");

  s = content("03 · Étude technique", "03  ·  CAHIER DES CHARGES", "Les cibles de la communication",
    "Trois cibles principales : les clients actuels à fidéliser ; les clients potentiels (jeunes, adultes, travailleurs, étudiants) à attirer ; les partenaires potentiels (entreprises, marques de nutrition, institutions). Le cahier des charges cite aussi les professionnels de l'industrie (coachs, kinésithérapeutes, nutritionnistes) et le grand public.");
  const cib = [["LuHeartHandshake", "Clients actuels", "Fidéliser"], ["LuUserPlus", "Clients potentiels", "Attirer"], ["LuHandshake", "Partenaires potentiels", "Collaborer"]];
  for (let i = 0; i < 3; i++) {
    const x = X + i * (iw3 + 0.35);
    card(s, x, 2.3, iw3, 3.9, "C1_card" + i);
    await iconDisc(s, cib[i][0], x + 0.4, 2.7, 1.0, "C1_i" + i);
    text(s, cib[i][1], { x: x + 0.3, y: 4.05, w: iw3 - 0.6, h: 0.5, fontSize: 18, bold: true, color: C.text1 }, "C1_t" + i);
    text(s, cib[i][2], { x: x + 0.3, y: 4.6, w: iw3 - 0.6, h: 0.45, fontSize: 16, color: C.accent1, bold: true }, "C1_v" + i);
  }

  s = content("03 · Étude technique", "03  ·  PLANNING", "Un projet réalisé en 8 semaines",
    "Semaines 1-2 : analyse du besoin, recherches créatives et validation de la charte. Semaines 3-4 : supports print et maquette 3D. Semaines 5-6 : post-production des spots 2D et 3D. Semaines 7-8 : interfaces du site vitrine, intégration des contenus, tests et corrections.");
  const steps = ["Analyse et charte graphique", "Supports print et maquette 3D", "Spots animatiques 2D et 3D", "Site web, intégration et tests"];
  const gx = X + 4.6, gw8 = (CW - 4.6) / 8;
  for (let k = 0; k < 8; k++) {
    text(s, "S" + (k + 1), { x: gx + k * gw8, y: 2.15, w: gw8, h: 0.35, fontSize: 12, bold: true, color: C.accent4, align: "center" }, "C1_w" + k);
    if (k > 0) s.addShape(pres.shapes.LINE, { x: gx + k * gw8, y: 2.6, w: 0, h: 3.75, line: { color: "E1E6EC", width: 1 }, objectName: "C1_g" + k });
  }
  steps.forEach((st, i) => {
    const y = 2.75 + i * 0.95;
    text(s, st, { x: X, y, w: 4.4, h: 0.6, fontSize: 17, bold: true, color: C.text1, valign: "middle" }, `C${i + 1}_t`);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: gx + i * 2 * gw8 + 0.06, y: y + 0.08, w: 2 * gw8 - 0.12, h: 0.44, rectRadius: 0.08,
      fill: { color: i === 3 ? C.accent1 : C.text1 }, line: { type: "none" }, objectName: `C${i + 1}_bar` });
  });

  s = content("03 · Étude technique", "03  ·  IDENTITÉ VISUELLE", "De l’esquisse au logo final",
    "La recherche s'est concentrée sur des symboles forts de la force athlétique, l'haltère et le poing fermé, associés à l'imagerie américaine : étoiles, rouge, blanc et bleu. Le logo retenu représente une main tenant un haltère, surmontée d'étoiles, avec le nom American's Gym.");
  img(s, "esquisse.jpg", { x: X, y: 2.2, w: 5.2, h: 3.6 }, "C1_esq", { alt: "Esquisse du logo" });
  caption(s, "Esquisse : haltère, poing fermé, étoiles", X, 6.0, 5.2, "C1_cap");
  s.addImage({ data: await icon("LuArrowRight", HEX.red), x: 6.3, y: 3.65, w: 0.7, h: 0.7, objectName: "C2_arrow", altText: "" });
  s.addImage({ path: A("logo_ag.png"), ...fit("logo_ag.png", 7.4, 2.2, 5.2, 3.6), objectName: "C2_logo", altText: "Logo final American's Gym" });
  caption(s, "Logo final : une main tenant un haltère, surmontée d’étoiles", 7.4, 6.0, 5.2, "C2_cap");

  s = content("03 · Étude technique", "03  ·  CHARTE GRAPHIQUE", "Un logo hybride, quatre symboles",
    "Le poing et l'haltère : la force brute, la musculation et la détermination. Les étoiles : la fierté américaine, l'histoire et la tradition. Le texte AMERICAN'S : une identité de marque forte et exclusive. Le ruban GYM : le nom du logo hybride qui réunit tous ces éléments en une image puissante et cohérente.");
  const parts = [["logo_poing.jpg", "Force et détermination"], ["logo_etoiles.jpg", "Fierté américaine"], ["logo_texte.jpg", "Identité de marque"], ["logo_ruban.jpg", "Image cohérente"]];
  parts.forEach((p, i) => {
    const x = X + i * (sw4 + 0.3);
    card(s, x, 2.3, sw4, 3.9, "C1_card" + i);
    s.addImage({ path: A(p[0]), ...fit(p[0], x + 0.3, 2.6, sw4 - 0.6, 2.2), objectName: "C1_img" + i, altText: p[1] });
    text(s, p[1], { x: x + 0.15, y: 5.1, w: sw4 - 0.3, h: 0.5, fontSize: 14, bold: true, color: C.text1, align: "center" }, "C1_t" + i);
  });

  s = content("03 · Étude technique", "03  ·  TYPOGRAPHIE", "Deux familles sans empattement",
    "Le logo utilise une police au style approchant Impact ou College Bold, en gras pour l'impact visuel. Les supports de communication utilisent Poppins ExtraBold ; les textes secondaires sont en graisse régulière pour la lisibilité.");
  const tw2 = (CW - 0.35) / 2;
  [["Impact", "Logo", "Impact / College Bold (style approchant)"], [THEME.headFontFace, "Supports", "Poppins ExtraBold"]].forEach((t, i) => {
    const x = X + i * (tw2 + 0.35);
    card(s, x, 2.25, tw2, 4.0, `C${i + 1}_card`);
    text(s, "Aa", { x: x + 0.5, y: 2.55, w: 3, h: 1.9, fontSize: 110, fontFace: t[0], color: C.text1 }, `C${i + 1}_aa`);
    text(s, t[1].toUpperCase(), { x: x + 0.5, y: 4.75, w: tw2 - 1, h: 0.35, fontSize: 11, bold: true, color: C.accent1, charSpacing: 2 }, `C${i + 1}_lab`);
    text(s, t[2], { x: x + 0.5, y: 5.15, w: tw2 - 1, h: 0.5, fontSize: 18, bold: true, color: C.text1 }, `C${i + 1}_name`);
  });

  s = content("03 · Étude technique", "03  ·  COLORIMÉTRIE", "Une palette inspirée du drapeau américain",
    "Codes officiels : bleu #1D3557, blanc #FFFFFF, rouge #E63946 et gris métal #A8DADC. Le bleu symbolise la confiance et la rigueur ; le rouge l'énergie, le courage et la passion ; le blanc la clarté et l'accessibilité. Le gris métal sert aux reliefs de l'haltère. Couleurs définies en CMJN pour l'impression et RVB pour le numérique.");
  const cols = [["1D3557", "Bleu", "FFFFFF"], ["E63946", "Rouge", "FFFFFF"], ["FFFFFF", "Blanc", "1D3557"], ["A8DADC", "Gris métal", "1D3557"]];
  cols.forEach((c, i) => {
    const x = X + i * (sw4 + 0.3);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.25, w: sw4, h: 3.2, rectRadius: 0.12, fill: { color: c[0] },
      line: c[0] === "FFFFFF" ? { color: "D5DCE5", width: 1 } : { type: "none" }, objectName: "C1_sw" + i });
    text(s, [{ text: c[1] + "  ", options: { bold: true } }, { text: "#" + c[0] }],
      { x: x + 0.3, y: 4.85, w: sw4 - 0.5, h: 0.4, fontSize: 14, color: c[2] }, "C1_swl" + i);
  });
  text(s, [
    { text: "Bleu ", options: { bold: true, color: C.text1 } }, { text: "confiance    " },
    { text: "Rouge ", options: { bold: true, color: C.accent1 } }, { text: "énergie    " },
    { text: "Blanc ", options: { bold: true, color: C.text1 } }, { text: "clarté" },
  ], { x: X, y: 5.8, w: CW, h: 0.45, fontSize: 16 }, "C2_sens");

  s = content("03 · Étude technique", "03  ·  RÈGLES D’UTILISATION", "Ce qu’il ne faut pas faire",
    "Interdits visuels : ne pas déformer ou étirer le logo ; ne pas changer ses couleurs ; ne pas ajouter d'éléments graphiques ; ne pas supprimer le texte GYM ni les étoiles. Sur fond foncé, détourer le ruban d'un fin liseré blanc ou utiliser la version monochrome blanche.");
  img(s, "interdits.jpg", { x: X, y: 2.15, w: 6.0, h: 3.9 }, "C1_img", { alt: "Exemples d'usages interdits du logo" });
  const forb = ["Déformer ou étirer le logo", "Changer les couleurs", "Ajouter des éléments graphiques", "Supprimer « GYM » ou les étoiles"];
  for (let i = 0; i < 4; i++) {
    const y = 2.3 + i * 0.95;
    s.addImage({ data: await icon("LuCircleX", HEX.red), x: 7.3, y: y + 0.05, w: 0.48, h: 0.48, objectName: "C2_x" + i, altText: "" });
    text(s, forb[i], { x: 8.0, y, w: 4.6, h: 0.6, fontSize: 17, color: C.text1, valign: "middle" }, "C2_t" + i);
  }

  s = content("03 · Étude technique", "03  ·  DÉCLINAISONS", "Le logo appliqué aux supports de marque",
    "Le logo est appliqué sur la carte de visite, le polo, la casquette, le sac de sport, les gourdes et le stylo, pour une présence de marque cohérente au quotidien.");
  const gd = [["g_cartes.jpg", "Carte de visite"], ["g_polo.jpg", "T-shirt"], ["g_casquette.jpg", "Casquette"], ["g_sac.jpg", "Sac de sport"], ["g_gourdes.jpg", "Gourdes"], ["g_stylo.jpg", "Stylo"]];
  const gw = (CW - 2 * 0.35) / 3;
  gd.forEach((g, i) => {
    const x = X + (i % 3) * (gw + 0.35), y = 2.05 + Math.floor(i / 3) * 2.45;
    const grp = i < 3 ? "C1" : "C2";
    card(s, x, y, gw, 2.0, grp + "_card" + i, C.background2);
    s.addImage({ path: A(g[0]), ...fit(g[0], x + 0.15, y + 0.15, gw - 0.3, 1.7), objectName: grp + "_img" + i, altText: g[1] });
    caption(s, g[1], x, y + 2.03, gw, grp + "_cap" + i);
  });

  s = content("03 · Étude technique", "03  ·  OUTILS", "Logiciels et langages",
    "Création graphique : Adobe Illustrator et Photoshop. Animation et vidéo : After Effects, Premiere Pro et Blender, avec Twinmotion pour le rendu final du spot 3D. Web : Adobe Dreamweaver, HTML, CSS et JavaScript ; la base de données est modélisée avec la méthode MERISE (MCD, MLD).");
  const tools = [
    ["Création graphique", ["sw_ai.png", "sw_ps.png"], "Illustrator, Photoshop"],
    ["Animation et vidéo", ["sw_ae.png", "sw_pr.png"], "After Effects, Premiere Pro, Blender"],
    ["Site web", ["sw_dw.png"], "Dreamweaver, HTML, CSS, JavaScript"],
  ];
  tools.forEach((t, i) => {
    const x = X + i * (iw3 + 0.35), g = `C${i + 1}`;
    card(s, x, 2.25, iw3, 3.4, g + "_card");
    t[1].forEach((f, k) => s.addImage({ path: A(f), x: x + 0.4 + k * 1.05, y: 2.65, w: 0.85, h: 0.85, objectName: g + "_logo" + k, altText: "" }));
    text(s, t[0], { x: x + 0.4, y: 3.9, w: iw3 - 0.8, h: 0.5, fontSize: 19, bold: true, color: C.text1 }, g + "_t");
    text(s, t[2], { x: x + 0.4, y: 4.45, w: iw3 - 0.6, h: 1.2, fontSize: 14, color: C.text2 }, g + "_d");
  });

  s = content("03 · Étude technique", "03  ·  COÛT DU PROJET", "Estimation budgétaire",
    "Le tableau 2 du mémoire estime le coût global à 4 800 000 FCFA, réparti entre l'identité visuelle, les maquettes et spots 2D et 3D, les supports imprimés et gadgets, et le site web avec son hébergement. ATTENTION : vérifier le tableau avant la soutenance, la somme des lignes donne 4 300 000 FCFA.");
  card(s, X, 2.25, 6.2, 4.0, "C1_card", C.text1);
  s.addImage({ data: await icon("LuWallet", HEX.metal), x: X + 0.5, y: 2.65, w: 0.75, h: 0.75, objectName: "C1_ico", altText: "" });
  text(s, "4 800 000", { x: X + 0.5, y: 3.65, w: 5.4, h: 1.1, fontSize: 54, fontFace: THEME.headFontFace, color: C.background1 }, "C1_num");
  text(s, "FCFA, coût global estimé", { x: X + 0.5, y: 4.85, w: 5.4, h: 0.5, fontSize: 18, color: C.accent2 }, "C1_lab");
  const postes = ["Identité visuelle : logotype et charte", "Maquettes et spots 2D, 3D", "Supports imprimés et gadgets", "Site web et hébergement"];
  for (let i = 0; i < postes.length; i++) {
    const y = 2.35 + i * 0.98;
    s.addImage({ data: await icon("LuCircleCheck", HEX.navy), x: 7.4, y: y + 0.08, w: 0.45, h: 0.45, objectName: "C2_ck" + i, altText: "" });
    text(s, postes[i], { x: 8.05, y, w: 4.55, h: 0.6, fontSize: 17, color: C.text1, valign: "middle" }, "C2_t" + i);
  }

  // =========================================================== 04 Réalisation
  divider("04 · Réalisations", "04", "Réalisation des supports",
    "Quatrième temps : les supports réalisés, imprimés, audiovisuels et numériques.");

  function duo(eyebrow, title, a, ca, b, cb, notes) {
    const s = content("04 · Réalisations", eyebrow, title, notes);
    const hw = (CW - 0.4) / 2;
    const bl = img(s, a, { x: X, y: 2.1, w: hw, h: 4.1 }, "C1_a", { alt: ca });
    caption(s, ca, bl.x, bl.y + bl.h + 0.12, bl.w, "C1_ca");
    const br = img(s, b, { x: X + hw + 0.4, y: 2.1, w: hw, h: 4.1 }, "C2_b", { alt: cb });
    caption(s, cb, br.x, br.y + br.h + 0.12, br.w, "C2_cb");
    return s;
  }
  duo("04  ·  AFFICHE 1", "Le brassage Côte d’Ivoire – États-Unis", "affiche1.jpg", "Visuel final", "affiche1_situ.jpg", "Mise en situation",
    "La première affiche met en avant l'identité particulière de la salle : le brassage entre la Côte d'Ivoire et les États-Unis, perceptible dans le nom American's Gym et les équipements venus des États-Unis. Réalisée sous Adobe Photoshop.");
  duo("04  ·  AFFICHE 2", "Un message persuasif et mémorable", "affiche2.jpg", "Visuel final", "affiche2_situ.jpg", "Mise en situation",
    "La deuxième affiche vise un effet persuasif et mémorable : logo officiel, accroche, slogan et contacts (07 88 48 18 72, Facebook, Instagram, TikTok).");
  duo("04  ·  FLYER", "Les tarifs en un coup d’œil", "flyer.jpg", "Flyer final", "flyer_situ.jpg", "Mise en situation",
    "Le flyer présente de manière synthétique les services, les tarifs et les avantages d'American's Gym Dokui. Il est consultable en version imprimée comme sur les réseaux sociaux. Format A4.");

  s = content("04 · Réalisations", "04  ·  DÉPLIANT", "Un dépliant trois volets",
    "Dépliant en trois volets, six pages, plié en accordéon. Couverture avec logo, visuel et slogan ; présentation des installations et des tarifs ; catalogue des compléments ; dos avec plan d'accès à Abobo-Dokui, contacts et horaires. Réalisé sous Adobe Illustrator.");
  const dm = img(s, "depliant_mock.jpg", { x: X, y: 2.05, w: 6.6, h: 4.25 }, "C1_mock", { alt: "Mise en situation du dépliant", align: "l" });
  caption(s, "Mise en situation", dm.x, dm.y + dm.h + 0.12, dm.w, "C1_cap");
  const d1 = img(s, "depliant_ext.jpg", { x: 7.75, y: 2.05, w: 4.83, h: 2.0 }, "C2_ext", { alt: "Dépliant, face extérieure", align: "l" });
  caption(s, "Face extérieure", d1.x, d1.y + d1.h + 0.08, d1.w, "C2_cap1");
  const d2 = img(s, "depliant_int.jpg", { x: 7.75, y: 4.45, w: 4.83, h: 1.85 }, "C3_int", { alt: "Dépliant, face intérieure", align: "l" });
  caption(s, "Face intérieure", d2.x, d2.y + d2.h + 0.08, d2.w, "C3_cap2");

  s = content("04 · Réalisations", "04  ·  KAKÉMONO", "Une lecture verticale et hiérarchisée",
    "Le kakémono, au format 85 × 200 cm, est destiné aux espaces d'accueil, aux événements sportifs et aux opérations promotionnelles : logo en partie haute, accroche, slogan, coordonnées et appel à l'action « Rejoignez la communauté American's Gym Dokui ». Réalisé sous Photoshop, en CMJN à 300 pixels par pouce.");
  const k1 = img(s, "kakemono.jpg", { x: X, y: 1.95, w: 2.3, h: 4.45 }, "C1_k", { alt: "Kakémono final", align: "l" });
  caption(s, "Kakémono final", k1.x, k1.y + k1.h + 0.1, 2.6, "C1_cap");
  const k2 = img(s, "kakemono_situ.jpg", { x: 3.55, y: 1.95, w: 3.3, h: 4.45 }, "C2_k", { alt: "Mise en situation du kakémono", align: "l" });
  caption(s, "Mise en situation", k2.x, k2.y + k2.h + 0.1, k2.w, "C2_cap");
  const kak = [["Format", "85 × 200 cm"], ["Usage", "Accueil, événements sportifs"]];
  kak.forEach((k, i) => {
    const y = 2.2 + i * 1.3;
    text(s, k[0].toUpperCase(), { x: 7.4, y, w: 5.2, h: 0.35, fontSize: 11, bold: true, color: C.accent1, charSpacing: 2 }, "C3_l" + i);
    text(s, k[1], { x: 7.4, y: y + 0.38, w: 5.2, h: 0.8, fontSize: 17, color: C.text1 }, "C3_v" + i);
  });

  s = content("04 · Réalisations", "04  ·  SUPPORTS DIGITAUX", "Des visuels pour les réseaux sociaux",
    "Les visuels sont destinés à Facebook, Instagram et TikTok, au format carré 1080 × 1080 pixels pour les publications et en formats verticaux pour les stories. Objectif : une continuité visuelle entre supports imprimés et numériques.");
  const rs = img(s, "reseau.jpg", { x: X, y: 2.05, w: 6.6, h: 4.25 }, "C1_img", { alt: "Visuel réseaux sociaux", align: "l" });
  caption(s, "Affiche réseaux sociaux", rs.x, rs.y + rs.h + 0.12, rs.w, "C1_cap");
  const dig = [["LuSmartphone", "Facebook, Instagram, TikTok"], ["LuShapes", "Format carré 1080 × 1080 pixels"], ["LuRepeat", "Continuité avec les supports imprimés"]];
  for (let i = 0; i < 3; i++) {
    const y = 2.3 + i * 1.3;
    await iconDisc(s, dig[i][0], 7.9, y, 0.75, "C2_d" + i, C.background2, HEX.navy);
    text(s, dig[i][1], { x: 8.9, y: y + 0.05, w: 3.7, h: 0.7, fontSize: 17, color: C.text1, valign: "middle" }, "C2_t" + i);
  }

  async function video(eyebrow, title, file, poster, facts, notes) {
    const s = content("04 · Réalisations", eyebrow, title, notes);
    const vw = 7.6, vh = vw * 9 / 16;
    const cover = "image/jpeg;base64," + fs.readFileSync(A(poster)).toString("base64");
    if (process.env.NO_VIDEO) {
      s.addImage({ path: A(poster), x: X, y: 2.1, w: vw, h: vh, objectName: "C2_poster", altText: "Image extraite de la vidéo", shadow: shadow() });
      caption(s, "Vidéo fournie séparément : " + file.replace("_web", ""), X, 2.1 + vh + 0.12, vw, "C2_cap");
    } else {
      s.addMedia({ type: "video", path: A(file), cover, x: X, y: 2.1, w: vw, h: vh, objectName: "V2_video" });
    }
    facts.forEach((f, i) => {
      const y = 2.2 + i * 1.08;
      text(s, f[0].toUpperCase(), { x: 9.0, y, w: 3.6, h: 0.32, fontSize: 11, bold: true, color: C.accent1, charSpacing: 2 }, "C1_l" + i);
      text(s, f[1], { x: 9.0, y: y + 0.34, w: 3.6, h: 0.6, fontSize: 17, color: C.text1 }, "C1_v" + i);
    });
    return s;
  }
  await video("04  ·  ANIMATION DU LOGO", "Le logo prend vie", "anim_logo_web.mp4", "anim_logo_poster.jpg",
    [["Logiciel", "Adobe After Effects"], ["Technique", "Animation des éléments textuels"], ["Export", "Format MP4"]],
    "Animation du logo réalisée sous Adobe After Effects : les éléments textuels du logo sont animés (position, opacité, rotation) puis synchronisés par images-clés, avant un export au format MP4 avec la piste audio.");
  await video("04  ·  SPOT 2D", "Un spot animé en motion design", "spot2d_web.mp4", "spot2d_poster.jpg",
    [["Type", "Animation 2D"], ["Format", "1920 × 1080 pixels"], ["Réalisation et montage", "CAMARA BINTOU"]],
    "Le spot 2D présente de façon dynamique les activités et services d'American's Gym Dokui : les équipements s'animent en rythme, puis une scène de groupe illustre la convivialité, avant la signature « American's Gym, l'excellence du fitness au cœur de votre bien-être ». (Durée annoncée : 25 s dans la fiche technique, 30 s plus loin : à harmoniser ; la vidéo fournie dure 26 s.)");

  s = content("04 · Réalisations", "04  ·  SPOT 3D", "Les locaux modélisés en 3D",
    "Le spot 3D présente l'image moderne et professionnelle des locaux : une caméra virtuelle traverse la salle modélisée, met en valeur les équipements et les jeux de lumière. Modélisation sous Blender, montage et bruitage sous Premiere Pro, rendu final sous Twinmotion. Durée : 30 secondes, 1920 × 1080 pixels.");
  const b3 = img(s, "3d_batiment.jpg", { x: X, y: 2.05, w: 7.6, h: 4.25 }, "C1_img", { alt: "Modélisation 3D du bâtiment American's Gym", align: "l" });
  caption(s, "Modélisation du bâtiment d’American’s Gym", b3.x, b3.y + b3.h + 0.12, b3.w, "C1_cap");
  [["Durée", "30 secondes"], ["Outils", "Blender, Premiere Pro, Twinmotion"]].forEach((f, i) => {
    const y = 2.2 + i * 1.08;
    text(s, f[0].toUpperCase(), { x: 9.0, y, w: 3.6, h: 0.32, fontSize: 11, bold: true, color: C.accent1, charSpacing: 2 }, "C2_l" + i);
    text(s, f[1], { x: 9.0, y: y + 0.34, w: 3.6, h: 0.6, fontSize: 17, color: C.text1 }, "C2_v" + i);
  });

  s = content("04 · Réalisations", "04  ·  SITE WEB", "Le site vitrine, cœur de l’écosystème numérique",
    "Le site vitrine est le point central de l'écosystème numérique : il crédibilise la structure, présente l'espace sportif et permet la commande de compléments alimentaires. Six rubriques : Accueil, À propos, Nos équipements, Boutique, Tarifs et abonnements, Contacts.");
  const rootW = 2.6;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: W / 2 - rootW / 2, y: 2.3, w: rootW, h: 0.85, rectRadius: 0.1, fill: { color: C.text1 }, line: { type: "none" }, objectName: "C1_root" });
  text(s, "Accueil", { x: W / 2 - rootW / 2, y: 2.3, w: rootW, h: 0.85, fontSize: 18, bold: true, color: C.background1, align: "center", valign: "middle" }, "C1_roott");
  const kids = ["À propos", "Nos équipements", "Boutique", "Tarifs et abonnements", "Contacts"];
  const kw = (CW - 4 * 0.25) / 5;
  s.addShape(pres.shapes.LINE, { x: W / 2, y: 3.15, w: 0, h: 0.55, line: { color: HEX.metal, width: 2 }, objectName: "C2_v" });
  s.addShape(pres.shapes.LINE, { x: X + kw / 2, y: 3.7, w: CW - kw, h: 0, line: { color: HEX.metal, width: 2 }, objectName: "C2_h" });
  kids.forEach((k, i) => {
    const x = X + i * (kw + 0.25);
    s.addShape(pres.shapes.LINE, { x: x + kw / 2, y: 3.7, w: 0, h: 0.5, line: { color: HEX.metal, width: 2 }, objectName: "C2_l" + i });
    card(s, x, 4.2, kw, 1.2, "C2_c" + i);
    text(s, k, { x: x + 0.1, y: 4.2, w: kw - 0.2, h: 1.2, fontSize: 15, bold: true, color: C.text1, align: "center", valign: "middle" }, "C2_t" + i);
  });

  s = content("04 · Réalisations", "04  ·  SITE WEB", "La page d’accueil",
    "L'onglet Accueil présente brièvement l'ensemble des éléments de l'entreprise et donne accès au menu de navigation.");
  const wa = img(s, "web_accueil.jpg", { x: X, y: 2.0, w: CW, h: 4.3 }, "C1_img", { alt: "Page d'accueil du site American's Gym" });
  caption(s, "Page « Accueil »", wa.x, wa.y + wa.h + 0.12, wa.w, "C1_cap");

  s = content("04 · Réalisations", "04  ·  SITE WEB", "Les pages du site",
    "À propos : histoire, vision et valeurs. Nos équipements. Boutique : catalogue filtrable de compléments. Tarifs et abonnements. Contacts : formulaire, carte interactive d'Abobo-Dokui, téléphone, Gmail et réseaux sociaux.");
  const pages = [["web_apropos.jpg", "À propos"], ["web_equip.jpg", "Nos équipements"], ["web_boutique.jpg", "Boutique"], ["web_tarifs.jpg", "Tarifs et abonnements"]];
  const pw2 = (CW - 0.4) / 2;
  pages.forEach((p, i) => {
    const x = X + (i % 2) * (pw2 + 0.4), y = 1.95 + Math.floor(i / 2) * 2.45;
    const b = img(s, p[0], { x, y, w: pw2, h: 1.95 }, (i < 2 ? "C1" : "C2") + "_img" + i, { alt: "Page " + p[1] });
    caption(s, p[1], b.x, b.y + b.h + 0.08, b.w, (i < 2 ? "C1" : "C2") + "_cap" + i);
  });

  // =========================================================== 05 Conclusion
  divider("05 · Conclusion", "05", "Conclusion",
    "Pour conclure, je reviens sur la problématique et propose des recommandations.");

  s = content("05 · Conclusion", "05  ·  CONCLUSION", "Une réponse concrète à la problématique",
    "Les travaux réalisés montrent que la création de supports de communication visuelle et numérique est un moyen pertinent de valoriser l'identité d'American's Gym et de soutenir sa promotion. Toutefois, la conception ne suffit pas à elle seule : les résultats dépendront de la qualité de la diffusion, de la régularité des publications et de la continuité des actions.");
  const conc = [["LuPalette", "Une identité visuelle cohérente"], ["LuLayers", "Des supports imprimés, audiovisuels et numériques complémentaires"], ["LuAward", "Une image plus professionnelle de la structure"]];
  for (let i = 0; i < 3; i++) {
    const y = 2.2 + i * 1.3;
    await iconDisc(s, conc[i][0], X, y, 0.85, `C${i + 1}_i`, i === 2 ? C.accent1 : C.text1);
    text(s, conc[i][1], { x: X + 1.2, y: y + 0.05, w: 10.6, h: 0.75, fontSize: 19, bold: true, color: C.text1, valign: "middle" }, `C${i + 1}_t`);
  }

  s = content("05 · Conclusion", "05  ·  RECOMMANDATIONS", "Pour une communication durable",
    "Nous recommandons à American's Gym une stratégie de communication cohérente et durable : utilisation harmonisée des supports, actualisation régulière des contenus numériques, puis évaluation des effets à partir d'indicateurs comme les interactions numériques, les demandes d'inscription et l'évolution du nombre d'adhérents.");
  const reco = [["LuTarget", "Adopter une stratégie cohérente et durable"], ["LuRepeat", "Actualiser régulièrement les contenus"], ["LuChartLine", "Mesurer : interactions, inscriptions, adhérents"]];
  for (let i = 0; i < 3; i++) {
    const x = X + i * (iw3 + 0.35);
    card(s, x, 2.3, iw3, 3.9, `C${i + 1}_card`);
    await iconDisc(s, reco[i][0], x + 0.4, 2.7, 1.0, `C${i + 1}_i`);
    text(s, reco[i][1], { x: x + 0.3, y: 4.05, w: iw3 - 0.6, h: 1.6, fontSize: 16, bold: true, color: C.text1 }, `C${i + 1}_t`);
  }

  s = pres.addSlide({ masterName: "AG_STATEMENT", sectionTitle: "05 · Conclusion" });
  s.addText("FIN DE LA PRÉSENTATION", { placeholder: "eyebrow" });
  s.addText("Merci de votre attention", { placeholder: "title" });
  s.addImage({ path: A("logo_ag.png"), ...fit("logo_ag.png", 8.9, 2.0, 3.7, 3.4), objectName: "C1_logo", altText: "Logo American's Gym" });
  text(s, "CAMARA BINTOU ÉPSE HOZAN", { x: X, y: 3.3, w: 7.5, h: 0.45, fontSize: 18, bold: true, color: C.background1 }, "C1_nom");
  text(s, "Licence professionnelle Arts et Images Numériques  ·  ISTC Polytechnique  ·  2025-2026",
    { x: X, y: 3.8, w: 8, h: 0.4, fontSize: 12, color: C.accent2 }, "C1_sub");
  s.addNotes("Je vous remercie de votre attention et me tiens à votre disposition pour vos questions.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("ok", OUT);
})().catch((e) => { console.error(e); process.exit(1); });
