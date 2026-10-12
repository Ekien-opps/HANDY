#!/usr/bin/env node
// Reorganise an exported scene SVG into named, designer-friendly layers (Illustrator / Figma),
// driven by a JSON plan, then optionally QA it against the reference render.
//
//   node tools/svg-export/organize.mjs --svg exports/svg/x.svg --plan plans/x.json --out exports/final/x.svg [--ref exports/svg/x.ref.png]
//
// Plan format:
// {
//   "title": "03 — Le feu · Sauces",
//   "pruneOffCanvas": true,                 // drop every drawable fully outside the 1920×1080 artboard
//   "remove": ["css selector", ...],        // drop these subtrees (e.g. invisible helpers)
//   "layers": [                              // painted bottom → top, in this order
//     { "id": "Fond", "label": "Fond", "items": [
//         { "sel": "css selector", "id": "Mur_carrelage", "label": "Mur carrelé" }, ...] },
//     ...
//   ]
// }
// Each item's matched element (first match, or all matches with "all": true) is moved into its layer
// inside a wrapper that carries the attributes of its former ancestors (transform, opacity, clip-path,
// mask, filter, style) so it renders exactly as before. Items keep document (paint) order inside a layer.
// Anything still visible and not assigned is reported (and collected into a final "A_trier" layer).
import { createRequire } from "node:module";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const require = createRequire(import.meta.url);
const { chromium } = require("/opt/node-tools/node_modules/playwright-core");
const HERE = dirname(fileURLToPath(import.meta.url));
const PROJ = resolve(HERE, "../..");
const CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, arr) => {
  if (a.startsWith("--")) acc.push([a.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : true]);
  return acc;
}, []));
const svgText = (await readFile(resolve(PROJ, args.svg), "utf8")).replace(/^<\?xml[^>]*>/, "");
const plan = JSON.parse(await readFile(resolve(PROJ, args.plan), "utf8"));

const browser = await chromium.launch({ executablePath: CHROME, args: ["--disable-gpu"] });
let result;
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#000}</style></head><body>${svgText}</body></html>`);
  result = await page.evaluate((plan) => {
    const NS = "http://www.w3.org/2000/svg";
    const svg = document.querySelector("svg");
    const report = { missing: [], unassigned: [], removed: 0, pruned: 0 };
    const isDef = (el) => !!el.closest("defs,clipPath,mask,linearGradient,radialGradient,pattern,filter,symbol,marker");
    const DRAW = "path,rect,circle,ellipse,line,polyline,polygon,text,image,use";
    const onCanvas = (el) => { const r = el.getBoundingClientRect(); return r.right > 0 && r.bottom > 0 && r.left < 1920 && r.top < 1080 && (r.width > 0 || r.height > 0); };

    for (const sel of plan.remove || []) svg.querySelectorAll(sel).forEach(e => { if (!isDef(e)) { e.remove(); report.removed++; } });

    const CARRY = ["transform", "opacity", "clip-path", "mask", "filter", "style", "fill", "stroke", "stroke-width", "fill-opacity", "stroke-opacity", "font-family", "font-size", "font-weight", "letter-spacing", "fill-rule", "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "paint-order", "visibility"];
    // wrapper chain reproducing everything the ancestors applied
    function wrapWithAncestors(el) {
      const chain = [];
      for (let a = el.parentElement; a && a !== svg; a = a.parentElement) chain.unshift(a);
      let outer = null, inner = null;
      for (const a of chain) {
        const attrs = CARRY.filter(n => a.hasAttribute(n));
        if (!attrs.length) continue;
        const g = document.createElementNS(NS, "g");
        attrs.forEach(n => g.setAttribute(n, a.getAttribute(n)));
        if (inner) inner.appendChild(g); else outer = g;
        inner = g;
      }
      return { outer, inner };
    }

    const layersOut = [];
    const taken = new Set();
    const firstPos = (u) => u.first;
    const before = (a, b) => (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1);
    // resolve an item (leaf selector or named group of parts) into a unit tree, recording first doc position
    function resolveItem(it, where) {
      if (it.parts) {
        const kids = it.parts.map(p => resolveItem(p, where)).flat().filter(Boolean);
        if (!kids.length) { report.missing.push(`${where} ← groupe ${it.id}`); return []; }
        kids.sort((a, b) => before(a.first, b.first));
        return [{ group: it, kids, first: kids[0].first }];
      }
      const found = it.all ? [...svg.querySelectorAll(it.sel)] : [svg.querySelector(it.sel)].filter(Boolean);
      const usable = found.filter(e => !isDef(e) && !taken.has(e) && ![...taken].some(t => t.contains(e)));
      if (!usable.length) { report.missing.push(`${where} ← ${it.sel}`); return []; }
      usable.forEach(e => taken.add(e));
      return usable.map((e, k) => ({ e, it, k, n: usable.length, first: e }));
    }
    for (const L of plan.layers) {
      const layer = document.createElementNS(NS, "g");
      layer.setAttribute("id", L.id); if (L.label) layer.setAttribute("data-name", L.label);
      const units = L.items.map(it => resolveItem(it, L.id)).flat();
      units.sort((a, b) => before(a.first, b.first));
      layersOut.push({ layer, units });
    }
    // prune AFTER selectors are resolved (pruning shifts :nth-child indices)
    if (plan.pruneOffCanvas) {
      [...svg.querySelectorAll(DRAW)].forEach(e => { if (!isDef(e) && !onCanvas(e)) { e.remove(); report.pruned++; } });
      const alive = (u) => u.group ? (u.kids = u.kids.filter(alive), u.kids.length > 0) : (u.e.isConnected && (u.e.matches(DRAW) || u.e.querySelector(DRAW)));
      layersOut.forEach(L => { L.units = L.units.filter(alive); });
    }
    // capture wrappers for every leaf BEFORE anything moves
    const leafWrap = new Map();
    const allLeaves = (u) => u.group ? u.kids.flatMap(allLeaves) : [u];
    layersOut.forEach(({ units }) => units.flatMap(allLeaves).forEach(l => leafWrap.set(l, wrapWithAncestors(l.e))));
    const sig = (w) => { const parts = []; for (let g = w.outer; g; g = g.firstElementChild && g !== w.inner ? g.firstElementChild : null) { parts.push([...g.attributes].map(a => a.name + "=" + a.value).join("|")); if (g === w.inner) break; } return parts.join(">"); };
    const cloneChain = (w) => { const top = w.outer.cloneNode(false); let cur = top, src = w.outer; while (src !== w.inner) { src = src.firstElementChild; const c = src.cloneNode(false); cur.appendChild(c); cur = c; } return { outer: top, inner: cur }; };
    function placeLeaf(u, intoWrapper) {
      const { e, it, k, n } = u;
      const name = it.id ? (n > 1 ? `${it.id}_${k + 1}` : it.id) : null;
      const lab = it.label ? (n > 1 ? `${it.label} ${k + 1}` : it.label) : null;
      if (intoWrapper) { if (name) { e.setAttribute("id", name); if (lab) e.setAttribute("data-name", lab); } return e; }
      const w = leafWrap.get(u);
      let unit = e;
      if (w.outer) { const c = cloneChain(w); c.inner.appendChild(e); unit = c.outer; }
      if (name) { if (w.outer) e.removeAttribute("id"); unit.setAttribute("id", name); if (lab) unit.setAttribute("data-name", lab); }
      return unit;
    }
    function build(u) {
      if (!u.group) return placeLeaf(u, false);
      const g = document.createElementNS(NS, "g");
      g.setAttribute("id", u.group.id); if (u.group.label) g.setAttribute("data-name", u.group.label);
      // merge consecutive leaf kids that share the same ancestor wrapper chain into ONE wrapper
      const runs = [];
      for (const k of u.kids) {
        const s_ = k.group ? null : (leafWrap.get(k).outer ? sig(leafWrap.get(k)) : "");
        const last = runs[runs.length - 1];
        if (s_ !== null && last && last.sig === s_) last.kids.push(k); else runs.push({ sig: s_, kids: [k] });
      }
      const single = runs.length === 1 && runs[0].sig;
      for (const r of runs) {
        if (r.sig === null) { g.appendChild(build(r.kids[0])); continue; }
        if (!r.sig) { r.kids.forEach(k => g.appendChild(placeLeaf(k, true))); continue; }
        if (single) {
          // the whole group shares one chain: hoist the chain onto the named group itself
          const c = cloneChain(leafWrap.get(r.kids[0]));
          [...c.outer.attributes].forEach(a => g.setAttribute(a.name, a.value));
          let host = g; if (c.outer !== c.inner) { const rest = c.outer.firstElementChild; g.appendChild(rest); host = c.inner; }
          r.kids.forEach(k => host.appendChild(placeLeaf(k, true)));
          continue;
        }
        const c = cloneChain(leafWrap.get(r.kids[0]));
        r.kids.forEach(k => c.inner.appendChild(placeLeaf(k, true)));
        g.appendChild(c.outer);
      }
      return g;
    }
    for (const { layer, units } of layersOut) units.forEach(u => layer.appendChild(build(u)));
    // leftovers: drawables still in the old tree
    const content = [...svg.children].filter(c => !["defs", "title", "desc", "style"].includes(c.localName));
    const left = [];
    content.forEach(c => c.querySelectorAll(DRAW).forEach(d => { if (!isDef(d) && onCanvas(d)) left.push(d); }));
    content.forEach(c => { if (c.localName === "g" || c.matches(DRAW)) c.remove(); });
    for (const { layer } of layersOut) if (layer.childNodes.length) svg.appendChild(layer);
    if (left.length) {
      const extra = document.createElementNS(NS, "g"); extra.setAttribute("id", "A_trier"); extra.setAttribute("data-name", "À trier");
      left.forEach(d => { const { outer, inner } = wrapWithAncestors(d); if (outer) { inner.appendChild(d); extra.appendChild(outer); } else extra.appendChild(d); report.unassigned.push(d.closest("[id]") ? d.closest("[id]").id + " > " + d.localName : d.localName); });
      svg.appendChild(extra);
    }
    function tidy() {
    let changed = true;
    while (changed) {
      changed = false;
      svg.querySelectorAll("g").forEach(g => {
        if (isDef(g)) return;
        if (!g.children.length) { g.remove(); changed = true; return; }
        if (!g.attributes.length && g.parentElement) { g.replaceWith(...g.childNodes); changed = true; return; }
        // absorb a lone child <g> into its parent when that cannot change rendering
        const kids = [...g.childNodes].filter(n => !(n.nodeType === 3 && !n.textContent.trim()));
        if (kids.length === 1 && kids[0].localName === "g") {
          const c = kids[0];
          const blockers = ["transform", "clip-path", "mask", "filter", "style"];
          let parentFree = !blockers.some(b => g.hasAttribute(b));
          const onlyT = (el) => !["clip-path", "mask", "filter", "style"].some(b => el.hasAttribute(b));
          if (!parentFree && g.hasAttribute("transform") && onlyT(g) && onlyT(c) && c.hasAttribute("transform")) {
            const toM = (t) => { const m = t.match(/matrix\(([^)]+)\)/); return m ? new DOMMatrix(m[1].trim().split(/[ ,]+/).map(Number)) : null; };
            const A = toM(g.getAttribute("transform")), B = toM(c.getAttribute("transform"));
            if (A && B) { const C = A.multiply(B); const r = (v) => Math.round(v * 10000) / 10000; c.setAttribute("transform", `matrix(${r(C.a)} ${r(C.b)} ${r(C.c)} ${r(C.d)} ${r(C.e)} ${r(C.f)})`); g.removeAttribute("transform"); parentFree = true; }
          }
          if (parentFree && !(c.hasAttribute("style") && g.hasAttribute("style"))) {
            for (const a of [...c.attributes]) {
              if (a.name === "id" || a.name === "data-name") { if (!g.hasAttribute(a.name)) g.setAttribute(a.name, a.value); continue; }
              if (a.name === "opacity" && g.hasAttribute("opacity")) { g.setAttribute("opacity", String(+(+g.getAttribute("opacity") * +a.value).toFixed(4))); continue; }
              g.setAttribute(a.name, a.value);
            }
            g.replaceChildren(...c.childNodes);
            changed = true;
          }
        }
      });
    }
    const PS = { 500: "Montserrat-Medium", 600: "Montserrat-SemiBold", 700: "Montserrat-Bold", 800: "Montserrat-ExtraBold", 900: "Montserrat-Black", 400: "Montserrat-Regular" };
    svg.querySelectorAll("[font-family]").forEach(t => {
      const fam = t.getAttribute("font-family").replace(/["']/g, "").split(",")[0].trim();
      const w = parseInt(t.getAttribute("font-weight") || getComputedStyle(t).fontWeight || "400", 10);
      if (/^Montserrat$/i.test(fam)) t.setAttribute("font-family", `${PS[w] || "Montserrat-Bold"}, Montserrat`);
      else if (/^Cream/i.test(fam)) t.setAttribute("font-family", "Cream-Heavy, 'Cream Heavy'");
    });
    }
    tidy();
    // drop clip-paths that clip nothing (content already inside the clip rect) → no useless Illustrator clip groups
    const clipRectScreen = (el) => {
      const m = (el.getAttribute("clip-path") || "").match(/url\(#([^)]+)\)/); if (!m) return null;
      const cp = document.getElementById(m[1]); if (!cp || cp.children.length !== 1) return null;
      const sh = cp.children[0];
      let x, y, w, h;
      if (sh.localName === "rect") { x = +sh.getAttribute("x") || 0; y = +sh.getAttribute("y") || 0; w = +sh.getAttribute("width"); h = +sh.getAttribute("height"); }
      else if (sh.localName === "ellipse" || sh.localName === "circle") return null; // curved: keep
      else return null;
      if ((sh.getAttribute("rx") || "0") !== "0" && sh.getAttribute("rx")) return null;
      const ctm = el.getCTM(); if (!ctm) return null;
      let M = new DOMMatrix([ctm.a, ctm.b, ctm.c, ctm.d, ctm.e, ctm.f]);
      if (el.getAttribute("transform")) { // clipPathUnits=userSpaceOnUse → user space of el = parent space × el.transform? getCTM already includes el's own transform
      }
      const t = sh.getAttribute("transform"); if (t) { const tm = t.match(/matrix\(([^)]+)\)/); if (!tm) return null; M = M.multiply(new DOMMatrix(tm[1].split(/[ ,]+/).map(Number))); }
      if (Math.abs(M.b) > 1e-6 || Math.abs(M.c) > 1e-6) return null;
      const p1 = M.transformPoint(new DOMPoint(x, y)), p2 = M.transformPoint(new DOMPoint(x + w, y + h));
      return { l: Math.min(p1.x, p2.x), t: Math.min(p1.y, p2.y), r: Math.max(p1.x, p2.x), b: Math.max(p1.y, p2.y) };
    };
    let unclipped = 0;
    svg.querySelectorAll("[clip-path]").forEach(el => {
      if (isDef(el)) return;
      const c = clipRectScreen(el); if (!c) return;
      const r = el.getBoundingClientRect();
      if (r.left >= c.l - 1 && r.top >= c.t - 1 && r.right <= c.r + 1 && r.bottom <= c.b + 1) { el.removeAttribute("clip-path"); unclipped++; }
    });
    report.uselessClipsRemoved = unclipped;
    // purge defs nobody references any more
    let purged = 0, again = true;
    while (again) {
      again = false;
      const text = new XMLSerializer().serializeToString(svg);
      svg.querySelectorAll("defs [id]").forEach(d => {
        if (d.parentElement.closest("[id]") && d.parentElement.closest("defs") !== d.parentElement && d.parentElement.localName !== "defs") return;
        const id = d.id;
        const refs = text.split(`#${id})`).length - 1 + text.split(`"#${id}"`).length - 1;
        const self = new XMLSerializer().serializeToString(d);
        const selfRefs = self.split(`#${id})`).length - 1 + self.split(`"#${id}"`).length - 1;
        if (refs - selfRefs <= 0) { d.remove(); purged++; again = true; }
      });
    }
    report.defsPurged = purged;
    tidy();
    if (plan.title) { let t = svg.querySelector("title"); if (!t) { t = document.createElementNS(NS, "title"); svg.prepend(t); } t.textContent = plan.title; }
    report.unassigned = [...new Set(report.unassigned)].slice(0, 60);
    return { svg: new XMLSerializer().serializeToString(svg), report };
  }, plan);
} finally {
  await browser.close();
}
const outPath = resolve(PROJ, args.out);
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, `<?xml version="1.0" encoding="UTF-8"?>\n<!-- ${plan.title || ""} — Marin'Or Ivoire · « Le goût en or » · polices : Cream Heavy, Montserrat -->\n` + result.svg.replace(/ xmlns:xlink="http:\/\/www\.w3\.org\/1999\/xlink"(?=[^>]*xmlns:xlink)/, ""));
console.log(JSON.stringify({ out: args.out, kb: Math.round(Buffer.byteLength(result.svg) / 1024), ...result.report }));
if (args.ref) {
  const qa = execFileSync("node", [join(HERE, "qa.mjs"), "--svg", args.out, "--ref", args.ref, "--out", args.out.replace(/\.svg$/, "")], { cwd: PROJ, encoding: "utf8" });
  console.log(qa.trim().split("\n").pop());
}
