#!/usr/bin/env node
// List the direct children of one element of an exported SVG (index for :nth-child, tag, id, bbox, on-canvas %, a fill hint)
//   node tools/svg-export/children.mjs --svg exports/svg/x.svg --sel "#lefeu-st1" [--crop out.png]
import { createRequire } from "node:module";
import { readFile } from "node:fs/promises";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require("/opt/node-tools/node_modules/playwright-core");
const PROJ = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const a = Object.fromEntries(process.argv.slice(2).reduce((acc, x, i, arr) => { if (x.startsWith("--")) acc.push([x.slice(2), arr[i + 1]]); return acc; }, []));
const svg = (await readFile(resolve(PROJ, a.svg), "utf8")).replace(/^<\?xml[^>]*>/, "");
const b = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args: ["--disable-gpu"] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.setContent(`<html><body style="margin:0">${svg}</body></html>`);
const rows = await p.evaluate((sel) => {
  const el = document.querySelector("svg").querySelector(sel);
  if (!el) return ["not found: " + sel];
  return [...el.children].map((c, i) => {
    const r = c.getBoundingClientRect();
    const ix = Math.max(0, Math.min(r.right, 1920) - Math.max(r.left, 0)), iy = Math.max(0, Math.min(r.bottom, 1080) - Math.max(r.top, 0));
    const on = r.width * r.height ? Math.round(100 * ix * iy / (r.width * r.height)) : 0;
    const fill = c.getAttribute("fill") || (c.querySelector("[fill]") && c.querySelector("[fill]").getAttribute("fill")) || "";
    return `${String(i + 1).padStart(3)}  <${c.localName}${c.id ? " #" + c.id : ""}${c.getAttribute("data-name") ? ' "' + c.getAttribute("data-name") + '"' : ""}>  bbox=[${[r.left, r.top, r.width, r.height].map(Math.round)}] on=${on}% nodes=${c.querySelectorAll("*").length} fill=${fill.slice(0, 28)}${c.localName === "text" ? ' “' + c.textContent + '”' : ""}`;
  });
}, a.sel);
console.log(rows.join("\n"));
await b.close();
