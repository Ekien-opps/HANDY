#!/usr/bin/env node
// Illustrator-compatibility pass for organised SVGs (rendering in browsers stays identical):
//  • pathLength + stroke-dasharray/dashoffset → real lengths (Illustrator ignores pathLength)
//  • text paint-order="stroke fill" → stroke copy behind + fill copy in front (Illustrator ignores paint-order)
//  • <feDropShadow> (SVG 2) → SVG 1.1 chain (feGaussianBlur/feOffset/feFlood/feComposite/feMerge)
//   node tools/svg-export/compat.mjs exports/final/a.svg [b.svg ...]
import { createRequire } from "node:module";
import { readFile, writeFile } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/node-tools/node_modules/playwright-core");
const PROJ = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const browser = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--disable-gpu"] });
try {
  for (const f of process.argv.slice(2)) {
    const path = resolve(PROJ, f);
    const raw = await readFile(path, "utf8");
    const head = (raw.match(/^(<\?xml[^>]*>\s*(<!--[\s\S]*?-->\s*)?)/) || ["", ""])[1];
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    await page.setContent(`<html><body style="margin:0">${raw.slice(head.length)}</body></html>`);
    const out = await page.evaluate(() => {
      const svg = document.querySelector("svg");
      const NS = "http://www.w3.org/2000/svg";
      const st = { pathLength: 0, paintOrder: 0, dropShadow: 0 };
      // 1) pathLength
      svg.querySelectorAll("[pathLength]").forEach(el => {
        const pl = parseFloat(el.getAttribute("pathLength"));
        let L = 0; try { L = el.getTotalLength(); } catch (e) { return; }
        if (!(pl > 0) || !(L > 0)) { el.removeAttribute("pathLength"); return; }
        const k = L / pl;
        const da = el.getAttribute("stroke-dasharray"), dof = el.getAttribute("stroke-dashoffset");
        const cs = getComputedStyle(el);
        const daV = da || (cs.strokeDasharray !== "none" ? cs.strokeDasharray : null);
        const doV = dof || (cs.strokeDashoffset && cs.strokeDashoffset !== "0px" ? cs.strokeDashoffset : null);
        if (daV) {
          const nums = daV.replace(/px/g, "").split(/[ ,]+/).map(Number);
          const offs = doV ? parseFloat(doV) : 0;
          const fullyDrawn = nums.length && nums.every(n => n >= pl - 0.01) && Math.abs(offs) < 0.01;
          if (fullyDrawn) { el.removeAttribute("stroke-dasharray"); el.removeAttribute("stroke-dashoffset"); }
          else { el.setAttribute("stroke-dasharray", nums.map(n => +(n * k).toFixed(3)).join(" ")); if (doV) el.setAttribute("stroke-dashoffset", +(offs * k).toFixed(3)); }
        }
        el.removeAttribute("pathLength"); st.pathLength++;
      });
      // 2) paint-order on text
      svg.querySelectorAll("text[paint-order]").forEach(t => {
        const po = t.getAttribute("paint-order");
        if (!/^stroke/.test(po) || !t.getAttribute("stroke") || t.getAttribute("stroke") === "none") { t.removeAttribute("paint-order"); return; }
        const back = t.cloneNode(true);
        back.removeAttribute("id"); back.removeAttribute("paint-order");
        back.setAttribute("data-name", "Contour (derrière)");
        const front = t; front.removeAttribute("paint-order");
        ["stroke", "stroke-width", "stroke-opacity", "stroke-linejoin"].forEach(a => front.removeAttribute(a));
        // shadow filter only on the back copy (it sits underneath anyway)
        if (front.getAttribute("filter")) front.removeAttribute("filter");
        const g = document.createElementNS(NS, "g");
        if (t.id) { g.setAttribute("id", t.id); t.removeAttribute("id"); }
        g.setAttribute("data-name", t.getAttribute("data-name") || ("Texte « " + t.textContent.trim() + " »"));
        t.replaceWith(g); g.appendChild(back); g.appendChild(front);
        front.setAttribute("data-name", "Remplissage");
        st.paintOrder++;
      });
      // 3) feDropShadow → SVG 1.1
      svg.querySelectorAll("feDropShadow").forEach((d, i) => {
        const f = d.parentElement;
        const inp = d.getAttribute("in") || "SourceGraphic";
        const res = d.getAttribute("result") || `ds${i}`;
        const dx = d.getAttribute("dx") || "0", dy = d.getAttribute("dy") || "0", sd = d.getAttribute("stdDeviation") || "0";
        const col = d.getAttribute("flood-color") || "#000", op = d.getAttribute("flood-opacity") || "1";
        const mk = (tag, attrs) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; };
        const p = `${res}_`;
        const nodes = [
          mk("feGaussianBlur", { in: inp === "SourceGraphic" ? "SourceAlpha" : inp, stdDeviation: sd, result: p + "b" }),
          mk("feOffset", { in: p + "b", dx, dy, result: p + "o" }),
          mk("feFlood", { "flood-color": col, "flood-opacity": op, result: p + "c" }),
          mk("feComposite", { in: p + "c", in2: p + "o", operator: "in", result: p + "s" }),
        ];
        const merge = mk("feMerge", { result: res });
        merge.appendChild(mk("feMergeNode", { in: p + "s" }));
        merge.appendChild(mk("feMergeNode", { in: inp }));
        nodes.push(merge);
        nodes.forEach(n => f.insertBefore(n, d));
        d.remove(); st.dropShadow++;
      });
      return { svg: new XMLSerializer().serializeToString(svg), st };
    });
    await page.close();
    await writeFile(path, head + out.svg);
    console.log(JSON.stringify({ file: f, ...out.st }));
  }
} finally { await browser.close(); }
