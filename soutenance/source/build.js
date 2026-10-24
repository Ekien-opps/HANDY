// Deck de soutenance — CAMARA BINTOU ÉPSE HOZAN — American's Gym
// Contenu : mémoire PDF. Couleurs : ancien deck « Présentation1 DAME HOZAN finale ».
// Convention d'animation (appliquée ensuite par animate.py) :
//   titre (placeholder) et objets "t_*"  -> automatique
//   objets "cN_*"                         -> clic N
//   autres objets                         -> statiques
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const sharp = require("sharp");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const Lu = require("react-icons/lu");

const ASSETS = path.join(__dirname, "..", "assets");
const A = (f) => path.join(ASSETS, f);
const OUT = process.argv[2] || path.join(__dirname, "deck.pptx");
const SKILL = process.env.PPTX_SKILL;
const { applyTheme } = require(path.join(SKILL, "scripts/apply_theme.js"));

// ---------- Charte (couleurs de l'ancien PowerPoint) ----------
const HEX = {
  red: "C00000", redDark: "7E0000", blue: "012F99", navy: "002060",
  white: "FFFFFF", light: "F3F4F8", gray: "5B6478", line: "D9DEE8",
};
const THEME = {
  name: "American's Gym — Soutenance",
  headFontFace: "Poppins",
  bodyFontFace: "Poppins",
  colors: {
    dk1: HEX.navy, lt1: HEX.white, dk2: HEX.blue, lt2: HEX.light,
    accent1: HEX.red, accent2: HEX.blue, accent3: HEX.redDark,
    accent4: HEX.gray, accent5: HEX.line, accent6: HEX.navy,
    hlink: HEX.blue, folHlink: HEX.redDark,
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.author = "CAMARA BINTOU ÉPSE HOZAN";
pres.title = "Conception et réalisation de supports de communication — American's Gym";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const NAVY = C.text1, BLUE = C.text2, WHITE = C.background1, LIGHT = C.background2;
const RED = C.accent1, GRAY = C.accent4, LINE = C.accent5;

// ---------- Utilitaires ----------
const imgSize = {};
async function loadSizes() {
  for (const f of fs.readdirSync(ASSETS)) {
    if (!/\.(png|jpe?g)$/i.test(f)) continue;
    const m = await sharp(A(f)).metadata();
    imgSize[f] = { w: m.width, h: m.height };
  }
}
async function icon(name, hex, size = 256) {
  const el = React.createElement(Lu[name], { color: "#" + hex, size: String(size) });
  const svg = ReactDOMServer.renderToStaticMarkup(el);
  const buf = await sharp(Buffer.from(svg)).resize(size, size).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
async function poster(file) {
  const buf = await sharp(A(file)).resize(1280).jpeg({ quality: 85 }).toBuffer();
  return "data:image/jpeg;base64," + buf.toString("base64");
}
// image contenue dans une boîte (centrée)
function fit(file, box) {
  const s = imgSize[file];
  const r = s.w / s.h;
  let w = box.w, h = box.w / r;
  if (h > box.h) { h = box.h; w = box.h * r; }
  return { x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h };
}
const shadow = () => ({ type: "outer", blur: 10, offset: 2, angle: 90, color: "000000", opacity: 0.16 });
let seq = 0;
const nm = (prefix) => `${prefix}_${++seq}`;

function T(slide, text, o) {
  slide.addText(text, Object.assign({ isTextBox: true, margin: 0, color: NAVY, fontSize: 16, valign: "top" }, o));
}
function card(slide, o, name, fill = LIGHT) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: o.x, y: o.y, w: o.w, h: o.h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: name,
  });
}
async function iconCircle(slide, x, y, d, iconName, name, opts = {}) {
  const fill = opts.fill || LIGHT;
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 }, objectName: name });
  const pad = d * 0.25;
  slide.addImage({ data: await icon(iconName, opts.color || HEX.blue), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, objectName: name + "i" });
}
function img(slide, file, box, name, withShadow = true) {
  const g = fit(file, box);
  const o = Object.assign({ path: A(file), objectName: name }, g);
  if (withShadow) o.shadow = shadow();
  slide.addImage(o);
  return g;
}

// ---------- Layouts ----------
function defineLayouts() {
  const num = { x: 12.36, y: 6.86, w: 0.46, h: 0.4, color: "FFFFFF", fontSize: 10, fontFace: "Poppins", align: "center", valign: "middle" };
  pres.defineSlideMaster({
    title: "CONTENU",
    background: { color: "FFFFFF" },
    objects: [
      { shape: { type: "hexagon", options: { x: 12.36, y: 6.86, w: 0.46, h: 0.4, fill: { color: HEX.red }, line: { color: HEX.red, width: 0 } } } },
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.42, w: 12.1, h: 0.85, fontSize: 28, bold: true, color: HEX.blue, align: "left", valign: "middle", margin: 0 }, text: "" } },
    ],
    slideNumber: num,
  });
  pres.defineSlideMaster({
    title: "SECTION",
    background: { path: A("bg_red.png") },
    objects: [
      { placeholder: { options: { name: "kicker", type: "body", x: 0.9, y: 2.55, w: 9, h: 0.55, fontSize: 16, bold: true, color: "FFFFFF", charSpacing: 4, align: "left", valign: "bottom", margin: 0 }, text: "" } },
      { placeholder: { options: { name: "title", type: "title", x: 0.9, y: 3.2, w: 10.5, h: 1.3, fontSize: 48, bold: true, color: "FFFFFF", align: "left", valign: "top", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "OUVERTURE",
    background: { path: A("bg_red.png") },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.75, w: 7.75, h: 2.2, fontSize: 28, bold: true, color: "FFFFFF", align: "left", valign: "top", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "CLOTURE",
    background: { path: A("bg_red.png") },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 4.3, w: 12.13, h: 0.9, fontSize: 40, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0 }, text: "" } },
    ],
  });
}

let section = "";
function sect(title) { pres.addSection({ title }); section = title; }
function content(title, notes) {
  const s = pres.addSlide({ masterName: "CONTENU", sectionTitle: section });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}
function divider(kicker, title, notes) {
  const s = pres.addSlide({ masterName: "SECTION", sectionTitle: section });
  s.addText(kicker, { placeholder: "kicker" });
  s.addText(title, { placeholder: "title" });
  if (notes) s.addNotes(notes);
  return s;
}

// ---------- Diapositives ----------
async function build() {
  await loadSizes();
  defineLayouts();

  // 1 — Ouverture
  sect("Ouverture");
  {
    const s = pres.addSlide({ masterName: "OUVERTURE", sectionTitle: section });
    s.addImage(Object.assign({ path: A("istc.png"), objectName: "logo_istc" }, fit("istc.png", { x: 0.45, y: 0.3, w: 2.1, h: 1.25 })));
    card(s, { x: 8.75, y: 1.3, w: 3.98, h: 3.98 }, "carte_logo", WHITE);
    s.addImage(Object.assign({ path: A("logo.png"), objectName: "logo_ag" }, fit("logo.png", { x: 9.05, y: 1.6, w: 3.38, h: 3.38 })));
    s.addText("Conception et réalisation de supports de communication pour la promotion de la structure de sport «\u00A0American's\u00A0Gym\u00A0»", { placeholder: "title" });
    T(s, "Licence professionnelle Arts et Images Numériques · 2025-2026", { x: 0.6, y: 4.25, w: 7.75, h: 0.4, fontSize: 14, color: WHITE, objectName: "t_sous_titre" });
    const cols = [
      ["Présentée par", "CAMARA BINTOU ÉPSE HOZAN"],
      ["Directeur de mémoire", "M. CHAFICK ADJIBADÉ"],
      ["Superviseur", "Prof. TOA AGNINI JULES ÉVARISTE"],
    ];
    cols.forEach(([lab, name], i) => {
      const x = 0.6 + i * 4.1;
      T(s, [
        { text: lab, options: { fontSize: 11, color: WHITE, transparency: 20, breakLine: true } },
        { text: name, options: { fontSize: 13, bold: true, color: WHITE } },
      ], { x, y: 5.75, w: 3.95, h: 0.75, paraSpaceAfter: 2, objectName: `c1_nom${i}` });
    });
    s.addNotes(
      "Monsieur le Président du jury, honorables membres du jury, chers invités, bonjour.\n\n" +
      "Je suis CAMARA BINTOU épouse HOZAN, étudiante en Licence professionnelle Arts et Images Numériques à l'ISTC Polytechnique, promotion 2023-2026. " +
      "J'ai l'honneur de vous présenter mon mémoire, réalisé sous la direction de M. CHAFICK ADJIBADÉ et sous la supervision du Professeur TOA AGNINI Jules Évariste, Professeur Titulaire d'Université.\n\n" +
      "Il porte sur la conception et la réalisation de supports de communication pour la promotion de la structure de sport « American's Gym »."
    );
  }

  // 2 — Plan
  {
    const s = content("Plan de présentation",
      "Notre présentation s'articule autour de cinq temps : l'introduction et la problématique, le cadre d'étude, l'étude technique, la réalisation des supports, puis la conclusion.");
    const items = ["Introduction", "Cadre d'étude", "Étude technique", "Réalisation des supports", "Conclusion"];
    items.forEach((t, i) => {
      const x = 0.6 + i * 2.47, y = 2.35, w = 2.27, h = 2.7;
      card(s, { x, y, w, h }, `c1_card${i}`);
      T(s, String(i + 1).padStart(2, "0"), { x: x + 0.3, y: y + 0.35, w: 1.6, h: 0.75, fontSize: 36, bold: true, color: RED, objectName: `c1_num${i}` });
      T(s, t, { x: x + 0.3, y: y + 1.35, w: w - 0.5, h: 1.0, fontSize: 17, bold: true, color: NAVY, objectName: `c1_lab${i}` });
    });
  }

  // 3..8 — Introduction
  sect("Introduction");
  divider("01", "Introduction", "[Transition] Commençons par le contexte de notre étude et la problématique qui en découle.");
  {
    const s = content("Une concurrence de plus en plus forte",
      "Dans un environnement marqué par une concurrence de plus en plus forte, la communication constitue aujourd'hui un levier stratégique indispensable au développement et à la pérennité des entreprises. " +
      "Le secteur du sport et du fitness n'échappe pas à cette réalité : avec l'essor des salles de sport et des agences spécialisées dans les activités sportives, il devient essentiel de se démarquer par des actions de communication efficaces, cohérentes et innovantes.");
    const cards = [
      ["LuMegaphone", "La communication, un levier stratégique indispensable"],
      ["LuTrendingUp", "L'essor des salles de sport et des agences sportives"],
      ["LuSparkles", "Se démarquer par une communication efficace, cohérente et innovante"],
    ];
    for (let i = 0; i < cards.length; i++) {
      const x = 0.6 + i * 4.13, y = 1.85, w = 3.83, h = 3.95, g = `c${i + 1}`;
      card(s, { x, y, w, h }, `${g}_card`);
      await iconCircle(s, x + 0.4, y + 0.45, 0.95, cards[i][0], `${g}_ic`, { fill: WHITE });
      T(s, cards[i][1], { x: x + 0.4, y: y + 1.7, w: w - 0.8, h: 1.9, fontSize: 18, bold: true, color: NAVY, objectName: `${g}_txt` });
    }
  }
  {
    const s = content("Thème de l'étude",
      "C'est dans ce cadre que s'inscrit notre thème : « Conception et réalisation de supports de communication pour la promotion de la structure de sport American's Gym ».");
    card(s, { x: 0.6, y: 1.75, w: 12.13, h: 4.55 }, "c1_card");
    T(s, "« Conception et réalisation de supports de communication pour la promotion de la structure de sport American's Gym »", {
      x: 1.4, y: 2.1, w: 10.53, h: 3.85, fontSize: 30, bold: true, color: BLUE, align: "center", valign: "middle", objectName: "c1_theme",
    });
  }
  {
    const s = content("Problématique",
      "Dans un environnement fortement concurrentiel, les structures de sport doivent développer une communication performante pour accroître leur visibilité, attirer de nouveaux adhérents et fidéliser leur clientèle. " +
      "American's Gym ne fait pas exception : malgré la diversité de ses activités et la qualité de ses prestations, la structure souffre d'une visibilité limitée, faute de supports de communication professionnels et harmonisés.\n\n" +
      "D'où notre question centrale : comment la conception et la réalisation de supports de communication imprimés et numériques peuvent-elles contribuer à améliorer la visibilité, renforcer l'image de marque et promouvoir efficacement les activités d'American's Gym ?");
    card(s, { x: 0.6, y: 1.75, w: 12.13, h: 4.55 }, "c1_card");
    s.addShape(pres.shapes.OVAL, { x: 1.15, y: 3.35, w: 1.35, h: 1.35, fill: { color: RED }, line: { color: RED, width: 0 }, objectName: "c1_rond" });
    T(s, "?", { x: 1.15, y: 3.35, w: 1.35, h: 1.35, fontSize: 48, bold: true, color: WHITE, align: "center", valign: "middle", objectName: "c1_q" });
    T(s, "Comment la conception et la réalisation de supports de communication imprimés et numériques peuvent-elles contribuer à améliorer la visibilité, renforcer l'image de marque et promouvoir efficacement les activités d'American's Gym ?", {
      x: 3.0, y: 2.05, w: 9.2, h: 3.95, fontSize: 22, color: NAVY, valign: "middle", objectName: "c1_txt",
    });
  }
  {
    const s = content("Quatre objectifs",
      "Pour répondre à cette interrogation, notre étude poursuit quatre objectifs : concevoir une identité visuelle cohérente adaptée à American's Gym ; réaliser des supports imprimés répondant aux besoins de communication de la structure ; " +
      "produire des contenus audiovisuels en 2D et en 3D destinés à la promotion des activités ; et développer un site web moderne pour présenter les services et renforcer la présence numérique de la structure.");
    const items = [
      ["LuPalette", "Concevoir une identité visuelle cohérente"],
      ["LuPrinter", "Réaliser des supports imprimés"],
      ["LuClapperboard", "Produire des contenus 2D et 3D"],
      ["LuGlobe", "Développer un site web moderne"],
    ];
    for (let i = 0; i < items.length; i++) {
      const x = 0.6 + i * 3.1, y = 1.85, w = 2.85, h = 3.95, g = `c${i + 1}`;
      card(s, { x, y, w, h }, `${g}_card`);
      T(s, String(i + 1).padStart(2, "0"), { x: x + 0.35, y: y + 0.4, w: 1, h: 0.5, fontSize: 16, bold: true, color: RED, objectName: `${g}_n` });
      await iconCircle(s, x + 0.35, y + 1.0, 0.95, items[i][0], `${g}_ic`, { fill: WHITE });
      T(s, items[i][1], { x: x + 0.35, y: y + 2.2, w: w - 0.7, h: 1.4, fontSize: 18, bold: true, color: NAVY, objectName: `${g}_t` });
    }
  }
  {
    const s = content("Hypothèse",
      "L'hypothèse retenue est que la mise en œuvre d'une stratégie de communication fondée sur des supports graphiques et numériques professionnels permettra d'améliorer significativement la notoriété d'American's Gym, de renforcer son image de marque et d'accroître sa capacité à attirer et fidéliser sa clientèle.");
    card(s, { x: 0.6, y: 1.75, w: 2.4, h: 4.55 }, "c1_bloc", BLUE);
    s.addImage({ data: await icon("LuLightbulb", HEX.white), x: 1.25, y: 3.47, w: 1.1, h: 1.1, objectName: "c1_ic" });
    T(s, "La mise en œuvre d'une stratégie de communication fondée sur des supports graphiques et numériques professionnels permettra d'améliorer significativement la notoriété d'American's Gym, de renforcer son image de marque et d'accroître sa capacité à attirer et fidéliser sa clientèle.", {
      x: 3.5, y: 1.75, w: 9.23, h: 4.55, fontSize: 21, color: NAVY, valign: "middle", objectName: "c1_txt",
    });
  }

  // 9..16 — Cadre d'étude
  sect("Cadre d'étude");
  divider("02 · PREMIÈRE PARTIE", "Cadre d'étude", "[Transition] Abordons à présent le cadre d'étude : la structure American's Gym et l'analyse de sa communication existante.");
  {
    const s = content("American's Gym en bref",
      "American's Gym Dokui est un club de fitness, de musculation et de sports de combat situé à Abidjan, dans le quartier d'Abobo Dokui. " +
      "Son concept repose sur un brassage entre le savoir-faire américain et l'hospitalité ivoirienne : la salle est équipée de machines de musculation et de cardio-training de dernière génération importées des États-Unis. " +
      "Elle propose la musculation et le fitness, la boxe, le taekwondo, ainsi que des séances dédiées aux femmes voilées.");
    const rows = [
      ["LIEU", "Abobo-Dokui, Abidjan"],
      ["CONCEPT", "Brassage États-Unis – Côte d'Ivoire"],
      ["ÉQUIPEMENTS", "Dernière génération, importés des USA"],
      ["DISCIPLINES", "Musculation, fitness, boxe, taekwondo"],
    ];
    rows.forEach(([k, v], i) => {
      const y = 2.0 + i * 1.08;
      card(s, { x: 0.6, y, w: 6.9, h: 0.82 }, `c${i + 1}_bg`);
      T(s, k, { x: 0.9, y, w: 1.9, h: 0.82, fontSize: 12, bold: true, color: RED, charSpacing: 1, valign: "middle", objectName: `c${i + 1}_k` });
      T(s, v, { x: 2.85, y, w: 4.5, h: 0.82, fontSize: 16, color: NAVY, valign: "middle", objectName: `c${i + 1}_v` });
    });
    img(s, "batiment3d.png", { x: 7.9, y: 2.0, w: 4.83, h: 4.06 }, "c5_img");
  }
  {
    const s = content("Une organisation structurée",
      "La gouvernance repose sur une structure claire. À la direction : le PDG, Djakaria KONATÉ, épaulé par un Vice-Président, DEMBÉLÉ Lassana, et un Manager Général, Alassane KONATÉ. " +
      "Le pôle administratif réunit un Trésorier et Manager adjoint, Moussa TRAORÉ, une Secrétaire Générale, Djeneba KONATÉ, et une Secrétaire adjointe, Mariam KONATÉ. " +
      "Le staff technique compte des coachs sportifs, des coachs de boxe et de taekwondo, et une coach dédiée aux cours pour femmes voilées.");
    img(s, "equipe.png", { x: 0.6, y: 1.6, w: 3.8, h: 5.05 }, "c1_img");
    const rows = [
      ["LuUsers", "PDG : ", "Djakaria KONATÉ", 1],
      ["LuUsers", "Vice-Président : ", "DEMBÉLÉ Lassana", 1],
      ["LuUsers", "Manager Général : ", "Alassane KONATÉ", 1],
      ["LuBriefcase", "Administration : ", "trésorerie et secrétariat général", 2],
      ["LuDumbbell", "Staff technique : ", "coachs sport, boxe, taekwondo", 3],
    ];
    for (let i = 0; i < rows.length; i++) {
      const [ic, k, v, g] = rows[i];
      const y = 1.85 + i * 0.95;
      await iconCircle(s, 4.95, y, 0.7, ic, `c${g}_ic${i}`);
      T(s, [{ text: k, options: { bold: true, color: BLUE } }, { text: v, options: { color: NAVY } }], { x: 5.9, y, w: 6.8, h: 0.7, fontSize: 17, valign: "middle", objectName: `c${g}_t${i}` });
    }
  }
  {
    const s = content("Vision et valeurs",
      "American's Gym ambitionne de devenir la salle de sport de référence en Côte d'Ivoire, en combinant l'excellence des technologies américaines avec les valeurs d'accueil, de proximité et de convivialité ivoiriennes, et d'ouvrir d'autres salles dans d'autres communes. " +
      "Elle fonde son action sur l'excellence, l'innovation, la discipline, la performance, le respect, le professionnalisme, le bien-être, la santé et l'esprit d'équipe.");
    card(s, { x: 0.6, y: 1.7, w: 12.13, h: 1.85 }, "c1_bg");
    T(s, "VISION", { x: 1.0, y: 1.95, w: 3, h: 0.35, fontSize: 12, bold: true, color: RED, charSpacing: 2, objectName: "c1_k" });
    T(s, "Devenir la salle de sport de référence en Côte d'Ivoire, en alliant technologies américaines et convivialité ivoirienne", { x: 1.0, y: 2.35, w: 11.3, h: 0.95, fontSize: 19, bold: true, color: NAVY, objectName: "c1_v" });
    const vals = ["Excellence", "Innovation", "Discipline", "Performance", "Respect", "Professionnalisme", "Bien-être", "Santé et esprit d'équipe"];
    vals.forEach((v, i) => {
      const x = 0.6 + (i % 4) * 3.1, y = 4.0 + Math.floor(i / 4) * 1.1;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 2.85, h: 0.8, rectRadius: 0.4, fill: { color: WHITE }, line: { color: BLUE, width: 1.25 }, objectName: `c2_v${i}` });
      T(s, v, { x, y, w: 2.85, h: 0.8, fontSize: 15, bold: true, color: BLUE, align: "center", valign: "middle", objectName: `c2_vt${i}` });
    });
  }
  {
    const s = content("Une présence numérique déjà active",
      "Côté digital, American's Gym dispose d'une page Facebook active d'environ 1 300 abonnés, principalement consacrée aux vidéos d'ambiance et aux fiches produits, " +
      "et d'un compte TikTok de plus de 5 400 abonnés générant environ 27 900 mentions « J'aime », axé sur le coaching en direct et la démonstration d'exercices. " +
      "La structure dispose aussi d'une boutique en ligne sur Shopify pour la vente de produits.\n\n[À VÉRIFIER : le mémoire indique « 5 4140 abonnés » et « Spotify » ; la capture TikTok affiche 5 414.]");
    const stats = [["≈ 1 300", "abonnés Facebook"], ["5 414", "abonnés TikTok"], ["27 900", "mentions « J'aime » TikTok"]];
    stats.forEach(([n, l], i) => {
      const y = 1.95 + i * 1.5;
      T(s, n, { x: 0.6, y, w: 2.75, h: 0.9, fontSize: 40, bold: true, color: RED, valign: "middle", objectName: `c1_n${i}` });
      T(s, l, { x: 3.45, y, w: 2.3, h: 0.9, fontSize: 15, color: NAVY, valign: "middle", objectName: `c1_l${i}` });
    });
    img(s, "tiktok.png", { x: 6.15, y: 1.65, w: 3.2, h: 4.95 }, "c2_tk");
    img(s, "facebook.png", { x: 9.53, y: 1.65, w: 3.2, h: 4.95 }, "c2_fb");
  }
  {
    const s = content("Critique de l'existant",
      "L'analyse de l'existant fait apparaître plusieurs faiblesses. D'abord l'identité visuelle : la mention « DOKUI » a été ajoutée sous le ruban sans respecter les proportions, avec une typographie bâton standard. " +
      "Ensuite, les affiches de promotion des produits utilisent des codes vert fluo ou marron, déconnectés de l'identité de la marque. " +
      "Sur le web, la boutique renvoie vers une URL Shopify non personnalisée, et l'identifiant TikTok @amricains.gym.dok contient une faute. " +
      "Enfin, la ligne éditoriale mélange musculation et publicités pour des thés minceur ou des gels douche, avec des vidéos brutes non montées.");
    const items = [
      ["LuShieldAlert", "Logo décliné hors charte", "Mention « DOKUI » ajoutée sous le ruban"],
      ["LuPalette", "Visuels hors charte", "Codes vert fluo ou marron"],
      ["LuLink", "URL non personnalisée", "Lien Shopify sans nom de domaine"],
      ["LuShuffle", "Ligne éditoriale confuse", "Sport et cosmétiques mélangés"],
    ];
    for (let i = 0; i < items.length; i++) {
      const x = 0.6 + (i % 2) * 6.18, y = 1.8 + Math.floor(i / 2) * 2.4, g = `c${i + 1}`;
      card(s, { x, y, w: 5.95, h: 2.1 }, `${g}_bg`);
      await iconCircle(s, x + 0.4, y + 0.6, 0.9, items[i][0], `${g}_ic`, { fill: WHITE, color: HEX.red });
      T(s, items[i][1], { x: x + 1.6, y: y + 0.5, w: 4.1, h: 0.5, fontSize: 18, bold: true, color: NAVY, objectName: `${g}_h` });
      T(s, items[i][2], { x: x + 1.6, y: y + 1.05, w: 4.1, h: 0.5, fontSize: 15, color: GRAY, objectName: `${g}_d` });
    }
  }
  {
    const s = content("Conséquences pour la marque",
      "Ces faiblesses ont des conséquences directes. Une baisse de la crédibilité de la marque, car un lien non personnalisé ou des fautes dans les identifiants officiels sont associés à un manque de sérieux. " +
      "Une perte d'efficacité publicitaire, les prospects pour les abonnements étant noyés parmi des publications de produits de beauté. " +
      "Une mauvaise visibilité et un manque de supports. Enfin, un déficit d'image face à une concurrence qui se professionnalise rapidement à Abidjan, qui empêche de justifier des tarifs d'abonnement premium.");
    const rows = [
      ["LuTrendingDown", "Baisse de la crédibilité", "Lien non personnalisé, fautes dans les identifiants"],
      ["LuMegaphoneOff", "Perte d'efficacité publicitaire", "Abonnements noyés parmi les produits de beauté"],
      ["LuEyeOff", "Mauvaise visibilité", "Manque de supports de communication"],
      ["LuSwords", "Déficit d'image", "Tarifs premium difficiles à justifier face à la concurrence"],
    ];
    for (let i = 0; i < rows.length; i++) {
      const y = 1.75 + i * 1.18, g = `c${i + 1}`;
      card(s, { x: 0.6, y, w: 12.13, h: 0.98 }, `${g}_bg`);
      await iconCircle(s, 0.9, y + 0.17, 0.64, rows[i][0], `${g}_ic`, { fill: WHITE, color: HEX.red });
      T(s, rows[i][1], { x: 1.85, y, w: 4.3, h: 0.98, fontSize: 17, bold: true, color: NAVY, valign: "middle", objectName: `${g}_h` });
      T(s, rows[i][2], { x: 6.25, y, w: 6.2, h: 0.98, fontSize: 15, color: GRAY, valign: "middle", objectName: `${g}_d` });
    }
  }
  {
    const s = content("Solutions proposées",
      "Pour y remédier, nous proposons deux familles de solutions. Côté imprimé : uniformiser la signalétique extérieure avec le logo officiel, créer des welcome packs et des cartes de membre aux couleurs de la charte, et un packaging de marque propre « American's Gym Nutrition ». " +
      "Côté digital : acheter un nom de domaine personnalisé lié à Shopify, corriger l'identifiant TikTok en @americans.gym.dokui, créer des gabarits réutilisables pour les publications, et isoler les produits dans un compte secondaire « American's Nutrition » ou une story à la une.");
    const cols = [
      ["LuPrinter", "Supports imprimés", ["Signalétique extérieure uniformisée", "Welcome packs et cartes de membre", "Packaging « American's Gym Nutrition »"]],
      ["LuGlobe", "Supports digitaux", ["Nom de domaine personnalisé", "Identifiant TikTok @americans.gym.dokui", "Gabarits de publications réutilisables", "Compte « American's Nutrition » dédié"]],
    ];
    for (let c = 0; c < 2; c++) {
      const x = 0.6 + c * 6.18, y = 1.7, g = `c${c + 1}`;
      card(s, { x, y, w: 5.95, h: 4.75 }, `${g}_bg`);
      await iconCircle(s, x + 0.4, y + 0.35, 0.7, cols[c][0], `${g}_ic`, { fill: WHITE });
      T(s, cols[c][1], { x: x + 1.3, y: y + 0.35, w: 4.3, h: 0.7, fontSize: 19, bold: true, color: BLUE, valign: "middle", objectName: `${g}_h` });
      T(s, cols[c][2].map((t, i, a) => ({ text: t, options: { bullet: { indent: 18 }, breakLine: i < a.length - 1 } })),
        { x: x + 0.45, y: y + 1.4, w: 5.25, h: 3.1, fontSize: 16, color: NAVY, paraSpaceAfter: 16, objectName: `${g}_l` });
    }
  }

  // 17..31 — Étude technique
  sect("Étude technique");
  divider("03 · DEUXIÈME PARTIE", "Étude technique", "[Transition] Passons à l'étude technique : le cahier des charges, l'identité visuelle et la conception des supports.");
  {
    const s = content("Objectif du cahier des charges",
      "L'objectif principal du projet est de concevoir et de réaliser un ensemble de supports de communication imprimés et numériques destinés à renforcer la visibilité et la notoriété d'American's Gym Dokui. " +
      "Les supports s'adressent aux clients actuels, pour les fidéliser ; aux clients potentiels — jeunes, adultes, travailleurs, étudiants ; aux partenaires potentiels — entreprises, marques de nutrition, assurances, établissements scolaires ; " +
      "aux professionnels de l'industrie — coachs, préparateurs, fédérations, nutritionnistes ; et au grand public. La langue principale est le français, avec quelques expressions en anglais pour rappeler l'identité américaine.");
    T(s, "Concevoir et réaliser des supports imprimés et numériques pour renforcer la visibilité et la notoriété d'American's Gym Dokui", { x: 0.6, y: 1.75, w: 11.6, h: 1.2, fontSize: 22, bold: true, color: NAVY, objectName: "c1_obj" });
    T(s, "CIBLES", { x: 0.6, y: 3.55, w: 3, h: 0.4, fontSize: 12, bold: true, color: RED, charSpacing: 2, objectName: "c2_k" });
    const cibles = ["Clients actuels", "Clients potentiels", "Partenaires potentiels", "Professionnels de l'industrie", "Grand public"];
    for (let i = 0; i < cibles.length; i++) {
      const x = 0.6 + i * 2.47;
      card(s, { x, y: 4.05, w: 2.27, h: 1.75 }, `c2_b${i}`);
      await iconCircle(s, x + 0.25, 4.3, 0.6, ["LuUserCheck", "LuUserPlus", "LuHandshake", "LuBadgeCheck", "LuUsers"][i], `c2_ic${i}`, { fill: WHITE });
      T(s, cibles[i], { x: x + 0.25, y: 4.05 + 0.95, w: 1.85, h: 0.7, fontSize: 14, bold: true, color: NAVY, objectName: `c2_t${i}` });
    }
  }
  {
    const s = content("Un logo hybride, quatre symboles",
      "Le logo retenu représente une main tenant un haltère, surmontée d'étoiles et accompagnée du nom « American's Gym ». " +
      "Le poing et l'haltère font référence à la force brute, à la musculation et à la détermination. Les étoiles renvoient à la fierté américaine, à l'histoire et à la tradition. " +
      "Le ruban « American's » établit une identité de marque forte et exclusive, et l'ensemble forme un logo hybride qui intègre tous ces éléments pour créer une image puissante et cohérente.");
    card(s, { x: 4.42, y: 1.7, w: 4.5, h: 4.75 }, "c1_bg");
    img(s, "logo.png", { x: 4.67, y: 1.95, w: 4.0, h: 4.25 }, "c1_logo", false);
    const call = [
      ["Poing et haltère", "Force et détermination", 0.6, 2.25, "left", 2],
      ["Étoiles", "Fierté américaine", 9.33, 2.25, "left", 3],
      ["Ruban « American's »", "Identité de marque forte", 0.6, 4.55, "left", 4],
      ["Logo complet", "Image puissante et cohérente", 9.33, 4.55, "left", 5],
    ];
    call.forEach(([h, d, x, y, al, g], i) => {
      T(s, [
        { text: h, options: { fontSize: 18, bold: true, color: BLUE, breakLine: true } },
        { text: d, options: { fontSize: 15, color: NAVY } },
      ], { x, y, w: 3.4, h: 1.1, align: al, paraSpaceAfter: 4, objectName: `c${g}_t${i}` });
    });
  }
  {
    const s = content("Couleurs de la charte graphique",
      "La palette du logo s'inspire du drapeau américain : bleu marine, rouge vif et blanc, complétés par un gris métal pour les reliefs de l'haltère. " +
      "Le bleu symbolise la confiance, la rigueur, le professionnalisme et la discipline requise pour l'entraînement. Le rouge incarne l'énergie, le courage, la passion et la performance. " +
      "Le blanc représente la clarté, la propreté des installations et l'accessibilité à tous. Les couleurs sont définies en CMJN pour l'impression et en RVB pour le numérique.");
    const sw = [
      ["1D3557", "Bleu", "#1D3557", "Confiance, rigueur, discipline"],
      ["E63946", "Rouge", "#E63946", "Énergie, courage, performance"],
      ["FFFFFF", "Blanc", "#FFFFFF", "Clarté, propreté, accessibilité"],
      ["A8DADC", "Gris métal", "#A8DADC", "Reliefs métalliques de l'haltère"],
    ];
    sw.forEach(([hex, name, code, mean], i) => {
      const x = 0.6 + i * 3.1, g = `c${i + 1}`;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.75, w: 2.85, h: 1.9, rectRadius: 0.12, fill: { color: hex }, line: { color: hex === "FFFFFF" ? HEX.line : hex, width: 1 }, objectName: `${g}_sw` });
      T(s, name, { x, y: 3.9, w: 2.85, h: 0.45, fontSize: 18, bold: true, color: NAVY, objectName: `${g}_n` });
      T(s, code, { x, y: 4.35, w: 2.85, h: 0.4, fontSize: 14, color: GRAY, objectName: `${g}_c` });
      T(s, mean, { x, y: 4.9, w: 2.75, h: 0.9, fontSize: 15, color: NAVY, objectName: `${g}_m` });
    });
  }
  {
    const s = content("Typographie",
      "La famille typographique retenue est une police sans empattement, moderne, lisible et adaptée aux supports imprimés comme numériques. " +
      "Pour le logo, le style approchant est Impact ou College Bold, en gras pour renforcer l'impact visuel et traduire la puissance de la marque. " +
      "Pour les supports de communication, la police d'accompagnement est Poppins ExtraBold, les textes secondaires utilisant des graisses régulières. " +
      "Le logotype compte 13 caractères sur deux lignes : AMERICAN'S, 10 caractères, et GYM, 3 caractères.");
    const cards = [
      ["LOGOTYPE", "Impact · College Bold", "Style approchant, en gras", "Impact"],
      ["SUPPORTS DE COMMUNICATION", "Poppins ExtraBold", "Textes secondaires en graisse régulière", "Poppins"],
    ];
    cards.forEach(([k, n, d, font], i) => {
      const x = 0.6 + i * 6.18, g = `c${i + 1}`;
      card(s, { x, y: 1.7, w: 5.95, h: 4.75 }, `${g}_bg`);
      T(s, "Aa", { x: x + 0.5, y: 1.95, w: 4, h: 1.9, fontSize: 96, bold: true, color: BLUE, fontFace: font, valign: "middle", objectName: `${g}_aa` });
      T(s, k, { x: x + 0.5, y: 4.15, w: 5, h: 0.4, fontSize: 12, bold: true, color: RED, charSpacing: 2, objectName: `${g}_k` });
      T(s, n, { x: x + 0.5, y: 4.6, w: 5, h: 0.5, fontSize: 20, bold: true, color: NAVY, objectName: `${g}_n` });
      T(s, d, { x: x + 0.5, y: 5.2, w: 5.1, h: 0.45, fontSize: 15, color: GRAY, objectName: `${g}_d` });
    });
  }
  {
    const s = content("Le logo décliné sur six supports",
      "Le logo est destiné à être utilisé sur différents supports : la carte de visite, le t-shirt, la casquette, le sac de sport, les bouteilles d'eau et le stylo.");
    const items = [["carte.jpg", "Carte de visite"], ["tshirt.jpg", "T-shirt"], ["casquette.png", "Casquette"], ["sac.jpg", "Sac de sport"], ["gourdes.jpg", "Bouteilles d'eau"], ["stylo.png", "Stylo"]];
    items.forEach(([f, cap], i) => {
      const x = 0.6 + (i % 3) * 4.15, y = 1.6 + Math.floor(i / 3) * 2.55, g = `c${Math.floor(i / 3) + 1}`;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.83, h: 1.95, rectRadius: 0.12, fill: { color: WHITE }, line: { color: LINE, width: 1 }, objectName: `${g}_bg${i}` });
      img(s, f, { x: x + 0.12, y: y + 0.12, w: 3.59, h: 1.71 }, `${g}_im${i}`, false);
      T(s, cap, { x, y: y + 2.02, w: 3.83, h: 0.35, fontSize: 14, bold: true, color: NAVY, objectName: `${g}_cap${i}` });
    });
  }
  {
    const s = content("Quatre interdits",
      "Pour préserver la cohérence de l'identité, quatre interdits sont fixés : ne pas déformer ou étirer le logo ; ne pas changer ses couleurs ; ne pas ajouter d'éléments graphiques supplémentaires ; et ne pas supprimer le texte GYM et les étoiles autour.");
    img(s, "interdits.jpg", { x: 0.6, y: 1.7, w: 6.2, h: 4.75 }, "c1_img", false);
    const rows = ["Ne pas déformer ou étirer le logo", "Ne pas changer les couleurs du logo", "Ne pas ajouter d'éléments graphiques", "Ne pas supprimer « GYM » ni les étoiles"];
    for (let i = 0; i < rows.length; i++) {
      const y = 2.0 + i * 1.05;
      await iconCircle(s, 7.25, y, 0.62, "LuX", `c${i + 2}_ic`, { color: HEX.red });
      T(s, rows[i], { x: 8.1, y, w: 4.63, h: 0.62, fontSize: 16, color: NAVY, valign: "middle", objectName: `c${i + 2}_t` });
    }
  }
  {
    const s = content("Supports imprimés : formats retenus",
      "Les supports imprimés comprennent deux affiches au format 4 m × 3 m, avec logo, accroche, slogan, contacts et image ; un flyer au format A5 présentant les tarifs ; " +
      "un dépliant trois volets de six pages présentant les installations, les tarifs, les compléments alimentaires et l'accès ; et un kakémono de 85 × 200 cm pour l'accueil et les événements.\n\n" +
      "[À VÉRIFIER : le flyer est indiqué A4 en conception et A5 en réalisation ; le dépliant « 84 cm / 29,7 cm ».]");
    const hdr = (t) => ({ text: t, options: { bold: true, color: HEX.white, fill: { color: HEX.blue }, fontSize: 14 } });
    const rows = [
      [hdr("Support"), hdr("Format"), hdr("Contenu clé")],
      ["Affiches (×2)", "4 m × 3 m", "Accroche, slogan, contacts, image"],
      ["Flyer", "A5 · 14,8 × 21 cm", "Accroche commerciale et tarifs"],
      ["Dépliant", "3 volets · 6 pages", "Installations, tarifs, compléments, accès"],
      ["Kakémono", "85 × 200 cm", "Logo, accroche, slogan, appel à l'action"],
    ].map((r, ri) => r.map((c) => (typeof c === "string" ? { text: c, options: { fill: { color: ri % 2 ? HEX.white : HEX.light }, bold: false } } : c)));
    s.addTable(rows, {
      x: 0.6, y: 1.85, w: 12.13, colW: [3.0, 3.4, 5.73], rowH: 0.82, fontSize: 16, fontFace: "Poppins", color: HEX.navy, valign: "middle",
      margin: [0, 0.2, 0, 0.25], border: { type: "solid", pt: 0.75, color: HEX.line }, objectName: "c1_table",
    });
  }
  {
    const s = content("Slogan de campagne",
      "Le slogan de campagne est : « American's Gym, l'excellence du fitness au cœur de votre bien-être ». Il est repris sur l'ensemble des supports et en signature des spots. " +
      "Il est accompagné de deux accroches : « Votre bien-être, notre priorité ! » et « Chaque séance est un pas de plus vers votre bien-être ».\n\n" +
      "[À VÉRIFIER : le mémoire écrit « au service de votre bien-être » dans la conception des affiches et « au cœur de votre bien-être » dans les spots et sur les visuels.]");
    T(s, [
      { text: "« American's Gym, l'excellence du fitness", options: { color: BLUE, breakLine: true } },
      { text: "au cœur de votre bien-être", options: { color: RED } },
      { text: ". »", options: { color: BLUE } },
    ], { x: 0.9, y: 1.9, w: 11.53, h: 2.3, fontSize: 34, bold: true, align: "center", valign: "middle", objectName: "c1_slogan" });
    card(s, { x: 1.9, y: 4.6, w: 9.53, h: 1.55 }, "c2_bg");
    T(s, [
      { text: "ACCROCHES", options: { fontSize: 12, bold: true, color: RED, charSpacing: 2, breakLine: true } },
      { text: "« Votre bien-être, notre priorité ! » · « Chaque séance est un pas de plus vers votre bien-être »", options: { fontSize: 15, color: NAVY } },
    ], { x: 2.3, y: 4.75, w: 8.73, h: 1.25, align: "center", valign: "middle", paraSpaceAfter: 4, objectName: "c2_acc" });
  }
  {
    const s = content("Deux spots promotionnels",
      "Le spot animatique 2D présente de manière dynamique les activités et les services d'American's Gym Dokui, en motion design : une onde cardiaque se transforme en barre de musculation, les équipements s'animent, puis une scène de groupe illustre la convivialité avant l'apparition du logo et du slogan. " +
      "Le spot 3D propose une immersion dans la salle modélisée en 3D, en trois séquences : l'ambiance, l'action et la signature. Les deux spots sont en 1920 × 1080 pixels ; réalisation et montage : CAMARA BINTOU.\n\n" +
      "[À VÉRIFIER : la fiche technique du spot 2D indique 25 secondes, la section « Durée » 30 secondes ; le fichier vidéo dure 26 secondes.]");
    const sp = [["poster_2d.jpg", "Spot 2D", "Animation 2D · 25 secondes · 1920 × 1080 px"], ["batiment3d.png", "Spot 3D", "Animation 3D · 30 secondes · 1920 × 1080 px"]];
    sp.forEach(([f, h, d], i) => {
      const x = 0.6 + i * 6.18, g = `c${i + 1}`;
      card(s, { x, y: 1.6, w: 5.95, h: 4.65 }, `${g}_bg`);
      img(s, f, { x: x + 0.3, y: 1.9, w: 5.35, h: 3.0 }, `${g}_im`, false);
      T(s, h, { x: x + 0.3, y: 5.05, w: 5.35, h: 0.45, fontSize: 19, bold: true, color: BLUE, objectName: `${g}_h` });
      T(s, d, { x: x + 0.3, y: 5.5, w: 5.35, h: 0.45, fontSize: 15, color: NAVY, objectName: `${g}_d` });
    });
    T(s, "Réalisation et montage : CAMARA BINTOU", { x: 0.6, y: 6.45, w: 8, h: 0.35, fontSize: 13, color: GRAY, objectName: "c3_cred" });
  }
  {
    const s = content("Arborescence du site web",
      "Le site vitrine est pensé comme le point central de l'écosystème numérique : il vise à crédibiliser la structure, à présenter l'espace sportif et à permettre la commande de compléments alimentaires. " +
      "Depuis la page d'accueil, le menu de navigation conduit à cinq rubriques : À propos, Nos équipements, Boutique, Tarifs et abonnements, et Contacts.");
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 5.37, y: 1.9, w: 2.6, h: 0.85, rectRadius: 0.12, fill: { color: BLUE }, line: { color: BLUE, width: 0 }, objectName: "c1_root" });
    T(s, "Accueil", { x: 5.37, y: 1.9, w: 2.6, h: 0.85, fontSize: 18, bold: true, color: WHITE, align: "center", valign: "middle", objectName: "c1_roott" });
    const kids = ["À propos", "Nos équipements", "Boutique", "Tarifs & abonnements", "Contacts"];
    const cw = 2.25, gap = (12.13 - 5 * cw) / 4;
    const lc = { color: HEX.line, width: 1.5 };
    const cx = (i) => 0.6 + i * (cw + gap) + cw / 2;
    s.addShape(pres.shapes.LINE, { x: 6.67, y: 2.75, w: 0, h: 0.6, line: lc, objectName: "c2_l0" });
    s.addShape(pres.shapes.LINE, { x: cx(0), y: 3.35, w: cx(4) - cx(0), h: 0, line: lc, objectName: "c2_l1" });
    kids.forEach((k, i) => {
      const x = 0.6 + i * (cw + gap);
      s.addShape(pres.shapes.LINE, { x: cx(i), y: 3.35, w: 0, h: 0.6, line: lc, objectName: `c2_v${i}` });
      card(s, { x, y: 3.95, w: cw, h: 1.15 }, `c2_b${i}`);
      T(s, k, { x: x + 0.1, y: 3.95, w: cw - 0.2, h: 1.15, fontSize: 15, bold: true, color: NAVY, align: "center", valign: "middle", objectName: `c2_t${i}` });
    });
    T(s, "Le menu de navigation relie la page d'accueil aux cinq rubriques du site", { x: 0.6, y: 5.6, w: 12.13, h: 0.45, fontSize: 15, color: GRAY, align: "center", objectName: "c3_cap" });
  }
  {
    const s = content("Langages et base de données",
      "Le site est structuré en HTML, mis en forme en CSS — couleurs, typographies, espacements, animations et adaptation aux écrans — et rendu interactif grâce à JavaScript : menus dynamiques, animations, formulaires et réservations. " +
      "La base de données a été modélisée avec la méthode MERISE, retenue pour sa capacité à garantir la cohérence des données. Le passage du MCD au MLD aboutit à trois tables : t_admin, t_devis et t_utilisateur.");
    const tiles = [
      ["HTML", "Structure des pages", BLUE], ["CSS", "Mise en forme graphique", BLUE], ["JavaScript", "Interactivité du site", BLUE],
      ["MERISE", "Méthode d'analyse retenue", RED], ["MCD → MLD", "Du modèle conceptuel au logique", RED], ["3 tables", "t_admin · t_devis · t_utilisateur", RED],
    ];
    tiles.forEach(([h, d, col], i) => {
      const x = 0.6 + (i % 3) * 4.15, y = 1.75 + Math.floor(i / 3) * 2.4, g = `c${Math.floor(i / 3) + 1}`;
      card(s, { x, y, w: 3.83, h: 2.1 }, `${g}_b${i}`);
      T(s, h, { x: x + 0.4, y: y + 0.45, w: 3.1, h: 0.6, fontSize: 24, bold: true, color: col, objectName: `${g}_h${i}` });
      T(s, d, { x: x + 0.4, y: y + 1.15, w: 3.2, h: 0.5, fontSize: 15, color: NAVY, objectName: `${g}_d${i}` });
    });
  }
  {
    const s = content("Logiciels de création",
      "Côté création, nous avons utilisé Adobe Illustrator pour le logo et les supports vectoriels, Adobe Photoshop pour la retouche et les visuels, Adobe After Effects pour le motion design, Adobe Premiere Pro pour le montage des spots et Adobe Dreamweaver comme environnement de développement du site. " +
      "Pour le spot 3D, la modélisation a été réalisée sous Blender, le montage et le bruitage sous Premiere Pro et le rendu final avec Twinmotion.");
    const sw = [
      ["Ai", "Illustrator", "Logo et supports vectoriels"], ["Ps", "Photoshop", "Retouche et visuels"], ["Ae", "After Effects", "Motion design 2D"],
      ["Pr", "Premiere Pro", "Montage des spots"], ["Dw", "Dreamweaver", "Développement du site"],
    ];
    sw.forEach(([ab, n, d], i) => {
      const x = 0.6 + i * 2.47, g = "c1";
      card(s, { x, y: 1.75, w: 2.27, h: 3.75 }, `${g}_b${i}`);
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.3, y: 2.05, w: 1.0, h: 1.0, rectRadius: 0.14, fill: { color: NAVY }, line: { color: NAVY, width: 0 }, objectName: `${g}_sq${i}` });
      T(s, ab, { x: x + 0.3, y: 2.05, w: 1.0, h: 1.0, fontSize: 26, bold: true, color: WHITE, align: "center", valign: "middle", objectName: `${g}_ab${i}` });
      T(s, n, { x: x + 0.3, y: 3.35, w: 1.85, h: 0.45, fontSize: 16, bold: true, color: NAVY, objectName: `${g}_n${i}` });
      T(s, d, { x: x + 0.3, y: 3.85, w: 1.8, h: 0.95, fontSize: 14, color: GRAY, objectName: `${g}_d${i}` });
    });
    T(s, "Spot 3D : modélisation sous Blender, montage Premiere Pro, rendu Twinmotion", { x: 0.6, y: 5.85, w: 12.13, h: 0.45, fontSize: 15, color: NAVY, objectName: "c2_3d" });
  }
  {
    const s = content("8 semaines de réalisation",
      "La réalisation du projet s'est étalée sur huit semaines. Semaines 1 et 2 : analyse du besoin, recherches créatives et validation de la charte graphique. " +
      "Semaines 3 et 4 : conception et réalisation des supports print — affiches, dépliants, kakémonos, gadgets — et de la maquette 3D. Semaines 5 et 6 : post-production des spots 2D et 3D. " +
      "Semaines 7 et 8 : réalisation des interfaces du site vitrine, intégration des contenus, tests et corrections.");
    const st = [
      ["Semaines 1-2", "Analyse du besoin, recherches créatives, validation de la charte"],
      ["Semaines 3-4", "Supports print, gadgets et maquette 3D"],
      ["Semaines 5-6", "Post-production des spots 2D et 3D"],
      ["Semaines 7-8", "Site web vitrine : interfaces, intégration, tests"],
    ];
    s.addShape(pres.shapes.LINE, { x: 0.6, y: 2.62, w: 12.13, h: 0, line: { color: HEX.line, width: 2 }, objectName: "c1_axe" });
    st.forEach(([w, d], i) => {
      const x = 0.6 + i * 3.1, g = `c${i + 1}`;
      s.addShape(pres.shapes.OVAL, { x, y: 2.44, w: 0.36, h: 0.36, fill: { color: RED }, line: { color: WHITE, width: 2 }, objectName: `${g}_pt` });
      T(s, w, { x, y: 1.75, w: 2.85, h: 0.45, fontSize: 16, bold: true, color: RED, objectName: `${g}_w` });
      card(s, { x, y: 3.15, w: 2.85, h: 2.6 }, `${g}_bg`);
      T(s, d, { x: x + 0.3, y: 3.45, w: 2.3, h: 2.1, fontSize: 16, color: NAVY, objectName: `${g}_d` });
    });
  }
  {
    const s = content("Coût global du projet",
      "Le coût global de réalisation du projet est estimé à 4 800 000 FCFA. Il couvre la conception du logotype et de la charte graphique, les maquettes 2D et 3D, les supports imprimés et les gadgets, le synopsis et la post-production des spots, ainsi que les interfaces du site web et l'hébergement.\n\n" +
      "[À CORRIGER AVANT LA SOUTENANCE : dans le tableau 2 du mémoire, la somme des totaux partiels donne 4 300 000 FCFA, et non 4 800 000 FCFA.]");
    card(s, { x: 0.6, y: 1.75, w: 5.95, h: 4.55 }, "c1_bg", BLUE);
    T(s, "4 800 000", { x: 1.0, y: 2.55, w: 5.3, h: 1.2, fontSize: 60, bold: true, color: WHITE, objectName: "c1_n" });
    T(s, "FCFA", { x: 1.0, y: 3.75, w: 5, h: 0.6, fontSize: 24, bold: true, color: WHITE, objectName: "c1_u" });
    T(s, "Estimation budgétaire globale", { x: 1.0, y: 4.55, w: 5, h: 0.45, fontSize: 15, color: WHITE, transparency: 15, objectName: "c1_l" });
    const postes = ["Logotype et charte graphique", "Maquettes 2D et 3D", "Supports imprimés et gadgets", "Synopsis et post-production", "Site web et hébergement"];
    for (let i = 0; i < postes.length; i++) {
      const y = 1.75 + i * 0.93;
      card(s, { x: 6.78, y, w: 5.95, h: 0.75 }, `c2_b${i}`);
      T(s, postes[i], { x: 7.1, y, w: 5.4, h: 0.75, fontSize: 16, color: NAVY, valign: "middle", objectName: `c2_t${i}` });
    }
  }

  // 32..44 — Réalisation
  sect("Réalisation des supports");
  divider("04 · TROISIÈME PARTIE", "Réalisation des supports", "[Transition] Voici à présent les supports réalisés, en commençant par les supports imprimés.");
  function pair(title, notes, a, b, capA, capB) {
    const s = content(title, notes);
    const boxes = [{ x: 0.6, y: 1.65, w: 5.95, h: 4.4 }, { x: 6.78, y: 1.65, w: 5.95, h: 4.4 }];
    [[a, capA], [b, capB]].forEach(([f, cap], i) => {
      const g = img(s, f, boxes[i], `c${i + 1}_im`);
      T(s, cap, { x: boxes[i].x, y: g.y + g.h + 0.15, w: 5.95, h: 0.4, fontSize: 14, color: GRAY, align: "center", objectName: `c${i + 1}_cap` });
    });
    return s;
  }
  pair("Affiche 1 et sa mise en situation",
    "La première affiche met en avant l'identité particulière de la salle, caractérisée par le brassage entre la Côte d'Ivoire et les États-Unis. " +
    "Elle porte le logo officiel, l'accroche « American's Gym, votre bien-être, notre priorité ! », le slogan de campagne et les contacts : 07 88 48 18 72, Facebook, Instagram et TikTok. Ici, en situation sur un panneau en bordure de route.",
    "affiche1.png", "affiche1_situ.jpg", "Affiche finale", "Mise en situation");
  pair("Affiche 2 et sa mise en situation",
    "La deuxième affiche vise un effet persuasif et mémorable, avec le logo, une accroche, le slogan de campagne et les contacts. La voici en situation, en grand format.\n\n" +
    "[À VÉRIFIER : le mémoire donne pour accroche « Chaque séance est un pas de plus vers votre bien-être », alors que l'affiche porte « Plus fort chaque jour, mieux dans votre peau ».]",
    "affiche2.png", "affiche2_situ.png", "Affiche finale", "Mise en situation");
  pair("Flyer tarifaire et sa mise en situation",
    "Le flyer s'inscrit dans une démarche de communication commerciale : il présente de manière synthétique les services, les tarifs et les avantages d'American's Gym Dokui. " +
    "Il est conçu pour être consulté en version imprimée comme sur les réseaux sociaux.\n\n[À VÉRIFIER : le titre du flyer affiche « AMERICAN'S GYMS ».]",
    "flyer.jpg", "flyer_situ.jpg", "Flyer final", "Mise en situation");
  pair("Dépliant trois volets : recto et verso",
    "Le dépliant, réalisé sous Adobe Illustrator, présente la structure en détail sur trois volets et six pages : la couverture avec le logo, un visuel et le slogan ; les installations et les tarifs ; le catalogue des compléments alimentaires ; et au dos, le plan d'accès, les contacts et les horaires.",
    "depliant_recto.png", "depliant_verso.png", "Recto", "Verso");
  {
    const s = content("Le dépliant en situation",
      "Voici le dépliant en situation. Son contenu s'organise ainsi : volet 1, la couverture ; volets 2 et 3, les installations et les tarifs d'abonnement ; volets 4 et 5, les compléments alimentaires ; volet 6, le plan d'accès à Abobo Dokui, les contacts et les horaires d'ouverture.");
    img(s, "depliant_situ.png", { x: 0.6, y: 1.65, w: 6.6, h: 4.95 }, "c1_im");
    const rows = [["Volet 1", "Logo, visuel, slogan"], ["Volets 2-3", "Installations et tarifs"], ["Volets 4-5", "Compléments alimentaires"], ["Volet 6", "Accès, contacts, horaires"]];
    rows.forEach(([k, v], i) => {
      const y = 1.9 + i * 1.12;
      card(s, { x: 7.6, y, w: 5.13, h: 0.88 }, `c2_b${i}`);
      T(s, [{ text: k + "  ", options: { bold: true, color: RED } }, { text: v, options: { color: NAVY } }], { x: 7.9, y, w: 4.7, h: 0.88, fontSize: 16, valign: "middle", objectName: `c2_t${i}` });
    });
  }
  {
    const s = content("Kakémono et sa mise en situation",
      "Le kakémono est destiné aux espaces d'accueil, aux événements sportifs et aux opérations promotionnelles. Sa composition repose sur une lecture verticale et hiérarchisée : le logo, l'accroche « votre bien-être, notre priorité ! », le slogan, les coordonnées et un appel à l'action : « Rejoignez la communauté American's Gym Dokui ». " +
      "Il a été réalisé sous Photoshop, au format 85 × 200 cm, en 300 pixels par pouce et en CMJN.");
    img(s, "kakemono.jpg", { x: 0.6, y: 1.6, w: 2.4, h: 5.05 }, "c1_im");
    img(s, "kakemono_situ.jpg", { x: 3.3, y: 1.6, w: 3.7, h: 5.05 }, "c2_im");
    const rows = [["Format", "85 × 200 cm, CMJN"], ["Appel à l'action", "« Rejoignez la communauté American's Gym Dokui »"], ["Usage", "Accueil, événements sportifs"]];
    rows.forEach(([k, v], i) => {
      const y = 1.85 + i * 1.45;
      card(s, { x: 7.4, y, w: 5.33, h: 1.2 }, `c3_b${i}`);
      T(s, [{ text: k + " : ", options: { bold: true, color: RED } }, { text: v, options: { color: NAVY } }], { x: 7.7, y, w: 4.85, h: 1.2, fontSize: 16, valign: "middle", objectName: `c3_t${i}` });
    });
  }
  {
    const s = content("Visuel pour les réseaux sociaux",
      "Les visuels digitaux sont destinés à Facebook, Instagram et TikTok. Ils ont été conçus sous Photoshop, avec l'objectif de créer une continuité visuelle entre les supports imprimés et numériques, pour une identification rapide de la marque American's Gym Dokui.");
    img(s, "reseaux.jpg", { x: 0.6, y: 1.65, w: 7.2, h: 4.95 }, "c1_im");
    const rows = [["Diffusion", "Facebook, Instagram, TikTok"], ["Accroche", "« Chaque séance est un pas de plus vers votre bien-être »"], ["Objectif", "Continuité visuelle print et digital"]];
    rows.forEach(([k, v], i) => {
      const y = 1.85 + i * 1.45;
      card(s, { x: 8.15, y, w: 4.58, h: 1.2 }, `c2_b${i}`);
      T(s, [{ text: k + " : ", options: { bold: true, color: RED } }, { text: v, options: { color: NAVY } }], { x: 8.4, y, w: 4.15, h: 1.2, fontSize: 16, valign: "middle", objectName: `c2_t${i}` });
    });
  }
  async function video(title, notes, file, cover) {
    const s = content(title, notes);
    s.addMedia({ type: "video", path: A(file), cover: await poster(cover), x: 1.87, y: 1.55, w: 9.6, h: 5.4, objectName: "video" });
  }
  await video("Animation du logo",
    "L'animation du logo a été réalisée sous Adobe After Effects : les éléments textuels du logo sont animés en position, opacité et rotation grâce aux images-clés, puis la séquence est exportée au format MP4.\n\n[Lancer la vidéo — environ 12 secondes]",
    "logo_anim.mp4", "poster_logo.jpg");
  await video("Spot animatique 2D",
    "Le spot 2D, réalisé sous After Effects, enchaîne quatre séquences : une onde cardiaque qui devient barre de musculation, les équipements qui s'animent, une scène de groupe autour d'un coach, puis le logo et le slogan.\n\n[Lancer la vidéo — environ 26 secondes]",
    "spot2d.mp4", "poster_2d.jpg");
  await video("Spot animatique 3D",
    "Le spot 3D propose une immersion dans le bâtiment d'American's Gym modélisé sous Blender, monté sous Premiere Pro, en trois séquences : l'ambiance, l'action et la signature.\n\n[Lancer la vidéo — environ 30 secondes]\n[À VÉRIFIER : version finale de la vidéo 3D (le rendu Twinmotion du mémoire diffère de cette vidéo).]",
    "spot3d.mp4", "poster_3d.jpg");
  {
    const s = content("Site web vitrine : la page d'accueil",
      "Nous en arrivons au site web vitrine. La page d'accueil présente brièvement l'ensemble des éléments de l'entreprise et donne accès au menu de navigation.\n\n[Option : basculer sur le site en direct, puis revenir à la présentation.]");
    img(s, "web_accueil.png", { x: 0.6, y: 1.65, w: 12.13, h: 4.95 }, "c1_im");
  }
  {
    const s = content("Les rubriques du site",
      "Les autres pages : « À propos » présente l'histoire, la vision et les valeurs ; « Nos équipements » montre les installations et machines de pointe ; « Boutique » propose les compléments ; « Tarifs » présente la grille Pass journée, mensuel et annuel ; et « Contacts » réunit le formulaire, la carte et les coordonnées.");
    const pages = [["web_apropos.png", "À propos"], ["web_equip.png", "Nos équipements"], ["web_boutique.png", "Boutique"], ["web_tarifs.png", "Tarifs"], ["web_contact.png", "Contacts"]];
    pages.forEach(([f, cap], i) => {
      const row = i < 3 ? 0 : 1;
      const x = row === 0 ? 0.6 + i * 4.15 : 2.675 + (i - 3) * 4.15;
      const y = 1.6 + row * 2.55;
      const g = img(s, f, { x, y, w: 3.83, h: 1.85 }, `c${row + 1}_im${i}`);
      T(s, cap, { x, y: g.y + g.h + 0.1, w: 3.83, h: 0.35, fontSize: 14, bold: true, color: NAVY, align: "center", objectName: `c${row + 1}_cap${i}` });
    });
  }

  // 45..48 — Conclusion
  sect("Conclusion");
  divider("05", "Conclusion", "[Transition] Pour conclure.");
  {
    const s = content("Une réponse concrète à la problématique",
      "Au terme de cette étude, l'analyse de l'existant a mis en évidence la nécessité de renforcer la cohérence de l'identité visuelle et de mieux structurer la présence de la salle. " +
      "Nous avons conçu des supports complémentaires : affiches, flyer, dépliant, kakémono, visuels pour les réseaux sociaux, productions 2D et 3D et un site web. " +
      "Toutefois, ces supports ne suffisent pas seuls : les résultats dépendront de la qualité de la diffusion, de la régularité des publications et de l'adaptation des messages. " +
      "Nous recommandons donc à American's Gym une stratégie de communication cohérente, durable et évaluée.");
    const cards = [
      ["LuCircleCheck", "Réalisé", "Identité visuelle, supports imprimés et digitaux, spots 2D et 3D, site web"],
      ["LuRepeat", "Condition", "Une diffusion régulière et des messages adaptés aux publics visés"],
      ["LuTarget", "Recommandation", "Une stratégie de communication cohérente, durable et évaluée"],
    ];
    for (let i = 0; i < cards.length; i++) {
      const x = 0.6 + i * 4.15, g = `c${i + 1}`;
      card(s, { x, y: 1.75, w: 3.83, h: 4.55 }, `${g}_bg`);
      await iconCircle(s, x + 0.4, 2.15, 0.9, cards[i][0], `${g}_ic`, { fill: WHITE });
      T(s, cards[i][1], { x: x + 0.4, y: 3.35, w: 3.0, h: 0.5, fontSize: 19, bold: true, color: BLUE, objectName: `${g}_h` });
      T(s, cards[i][2], { x: x + 0.4, y: 3.95, w: 3.05, h: 1.9, fontSize: 16, color: NAVY, objectName: `${g}_d` });
    }
  }
  {
    const s = content("Mesurer les effets après diffusion",
      "Il sera nécessaire d'évaluer les effets des supports après leur mise en œuvre, à partir d'indicateurs tels que les interactions numériques, les demandes d'inscription et l'évolution du nombre d'adhérents. " +
      "La communication apparaîtra alors non seulement comme un outil de présentation, mais aussi comme un levier d'accompagnement du développement de la structure.");
    T(s, "Les supports ne suffisent pas, à eux seuls : leurs effets devront être évalués après leur mise en œuvre.", { x: 0.6, y: 1.7, w: 11.5, h: 1.0, fontSize: 20, color: NAVY, objectName: "c1_t" });
    const ind = [["LuMousePointerClick", "Interactions numériques"], ["LuUserPlus", "Demandes d'inscription"], ["LuChartLine", "Évolution du nombre d'adhérents"]];
    for (let i = 0; i < ind.length; i++) {
      const x = 0.6 + i * 4.15, g = `c${i + 2}`;
      await iconCircle(s, x + 1.37, 3.2, 1.1, ind[i][0], `${g}_ic`, { color: HEX.red });
      T(s, ind[i][1], { x, y: 4.55, w: 3.83, h: 0.9, fontSize: 18, bold: true, color: NAVY, align: "center", objectName: `${g}_t` });
    }
  }
  {
    const s = pres.addSlide({ masterName: "CLOTURE", sectionTitle: section });
    card(s, { x: 5.37, y: 0.9, w: 2.6, h: 2.6 }, "carte_logo", WHITE);
    s.addImage(Object.assign({ path: A("logo.png"), objectName: "logo_ag" }, fit("logo.png", { x: 5.52, y: 1.05, w: 2.3, h: 2.3 })));
    s.addText("Merci pour votre attention", { placeholder: "title" });
    T(s, "American's Gym, l'excellence du fitness au cœur de votre bien-être.", { x: 0.6, y: 5.25, w: 12.13, h: 0.5, fontSize: 18, italic: true, color: WHITE, align: "center", objectName: "c1_slogan" });
    T(s, "CAMARA BINTOU ÉPSE HOZAN · ISTC Polytechnique", { x: 0.6, y: 6.3, w: 12.13, h: 0.4, fontSize: 13, color: WHITE, transparency: 20, align: "center", objectName: "c1_nom" });
    s.addNotes("Je vous remercie pour votre attention et reste à votre disposition pour répondre à vos questions.");
  }

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("written", OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
