#!/usr/bin/env node
// Render an SVG in Chrome (with the brand fonts) and compare it to a reference PNG,
// and/or print an inspection tree of its named groups.
//
//   node tools/svg-export/qa.mjs --svg exports/svg/x.svg --ref exports/svg/x.ref.png [--out /tmp/x]   → diff score + <out>.qa.png/.diff.png/.side.jpg
//   node tools/svg-export/qa.mjs --svg exports/svg/x.svg --inspect [--depth 6]                       → JSON tree: id, label, bbox, onCanvas%, nodes
import { createRequire } from "node:module";
import { readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("/opt/node-tools/node_modules/playwright-core");
const HERE = dirname(fileURLToPath(import.meta.url));
const PROJ = resolve(HERE, "../..");
const CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, arr) => {
  if (a.startsWith("--")) acc.push([a.slice(2), arr[i + 1] && !arr[i + 1].startsWith("--") ? arr[i + 1] : true]);
  return acc;
}, []));
const svgPath = resolve(PROJ, args.svg);
const svgText = (await readFile(svgPath, "utf8")).replace(/^<\?xml[^>]*>/, "");
const harness = await readFile(join(PROJ, "tools/svg-harness.html"), "utf8");
let fontCss = harness.match(/@font-face[^}]+}/g).join("\n");
for (const m of [...fontCss.matchAll(/url\("\.\.\/(assets\/fonts\/[^"]+)"\)/g)]) {
  const b64 = (await readFile(join(PROJ, m[1]))).toString("base64");
  const mime = m[1].endsWith(".ttf") ? "font/ttf" : "font/woff2";
  fontCss = fontCss.replace(m[0], `url("data:${mime};base64,${b64}")`);
}

const browser = await chromium.launch({ executablePath: CHROME, args: ["--disable-gpu", "--font-render-hinting=none", "--allow-file-access-from-files"] });
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${fontCss} html,body{margin:0;background:#000;width:1920px;height:1080px;overflow:hidden}</style></head><body>${svgText}</body></html>`, { waitUntil: "load" });
  await page.evaluate(async () => { await document.fonts.ready; });
  await page.waitForTimeout(300);

  if (args.inspect) {
    const depth = parseInt(args.depth || "6", 10);
    const tree = await page.evaluate((maxDepth) => {
      const svg = document.querySelector("svg");
      const area = (r) => Math.max(0, r.width) * Math.max(0, r.height);
      function walk(el, d) {
        const out = [];
        for (const c of el.children) {
          if (["defs", "title", "desc", "style"].includes(c.localName)) continue;
          const r = c.getBoundingClientRect();
          const ix = Math.max(0, Math.min(r.right, 1920) - Math.max(r.left, 0)), iy = Math.max(0, Math.min(r.bottom, 1080) - Math.max(r.top, 0));
          const on = area(r) ? Math.round(100 * ix * iy / area(r)) : 0;
          const node = { tag: c.localName, id: c.id || undefined, label: c.getAttribute("data-name") || undefined, bbox: [r.left, r.top, r.width, r.height].map(Math.round), onCanvasPct: on, nodes: c.querySelectorAll("*").length };
          if (c.localName === "text") node.text = c.textContent.slice(0, 60);
          if (c.localName === "g" && d < maxDepth) { const k = walk(c, d + 1); if (k.length) node.children = k; }
          out.push(node);
        }
        return out;
      }
      return walk(svg, 0);
    }, depth);
    console.log(JSON.stringify(tree, null, 1));
  }

  if (args.ref) {
    const outStem = args.out ? resolve(PROJ, args.out) : svgPath.replace(/\.svg$/, "");
    await page.screenshot({ path: `${outStem}.qa.png` });
    const ref = await readFile(resolve(PROJ, args.ref));
    const qa = await readFile(`${outStem}.qa.png`);
    const r = await page.evaluate(async ([a, b]) => {
      const load = src => new Promise(res => { const i = new Image(); i.onload = () => res(i); i.src = src; });
      const [ia, ib] = await Promise.all([load(a), load(b)]);
      const c = document.createElement("canvas"); c.width = 1920; c.height = 1080; const x = c.getContext("2d");
      x.drawImage(ia, 0, 0); const da = x.getImageData(0, 0, 1920, 1080).data;
      x.clearRect(0, 0, 1920, 1080); x.drawImage(ib, 0, 0); const db = x.getImageData(0, 0, 1920, 1080).data;
      const diff = x.createImageData(1920, 1080); let sum = 0, bad = 0;
      for (let i = 0; i < da.length; i += 4) {
        const d = (Math.abs(da[i] - db[i]) + Math.abs(da[i + 1] - db[i + 1]) + Math.abs(da[i + 2] - db[i + 2])) / 3;
        sum += d; if (d > 40) bad++;
        const v = Math.min(255, d * 3); diff.data[i] = v; diff.data[i + 1] = v * 0.3; diff.data[i + 2] = 0; diff.data[i + 3] = 255;
      }
      x.putImageData(diff, 0, 0); const diffUrl = c.toDataURL("image/png");
      // side-by-side preview: ref | svg | diff at 1/3 scale
      const s = document.createElement("canvas"); s.width = 1920; s.height = 360; const y = s.getContext("2d");
      y.drawImage(ia, 0, 0, 640, 360); y.drawImage(ib, 640, 0, 640, 360); const di = await load(diffUrl); y.drawImage(di, 1280, 0, 640, 360);
      return { meanAbsDiff: +(sum / (1920 * 1080)).toFixed(2), pctPixelsOff: +(100 * bad / (1920 * 1080)).toFixed(2), diffUrl, sideUrl: s.toDataURL("image/jpeg", 0.8) };
    }, [`data:image/png;base64,${ref.toString("base64")}`, `data:image/png;base64,${qa.toString("base64")}`]);
    await writeFile(`${outStem}.diff.png`, Buffer.from(r.diffUrl.split(",")[1], "base64"));
    await writeFile(`${outStem}.side.jpg`, Buffer.from(r.sideUrl.split(",")[1], "base64"));
    console.log(JSON.stringify({ meanAbsDiff: r.meanAbsDiff, pctPixelsOff: r.pctPixelsOff, side: `${outStem}.side.jpg`, diff: `${outStem}.diff.png` }));
  }
} finally {
  await browser.close();
}
