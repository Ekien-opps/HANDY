#!/usr/bin/env node
// Export one HyperFrames scene, frozen at a local time, as a layered SVG (+ reference PNG + QA diff).
//
//   node tools/svg-export/export.mjs --scene 03-le-feu --time 0.75 --out exports/svg/03-sauces.svg \
//        [--title "03 — Le feu · Sauces"] [--force "#sel{opacity:1}; .x{display:none}"] [--qa]
//
// Writes <out>.svg, <out-without-ext>.ref.png (true render) and, with --qa, <out>.qa.png
// (the SVG re-rendered in Chrome) + <out>.diff.png, and prints a mean-absolute-difference score.
import { createRequire } from "node:module";
import http from "node:http";
import { readFile, writeFile, mkdir, stat } from "node:fs/promises";
import { dirname, extname, join, resolve } from "node:path";
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
if (!args.scene || args.time === undefined || !args.out) {
  console.error("usage: export.mjs --scene <id> --time <s> --out <file.svg> [--title t] [--force css] [--qa]");
  process.exit(2);
}
const out = resolve(PROJ, args.out);
const stem = out.slice(0, -extname(out).length);

const MIME = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".ttf": "font/ttf", ".woff2": "font/woff2", ".json": "application/json", ".wav": "audio/wav" };
const server = http.createServer(async (req, res) => {
  try {
    const p = join(PROJ, decodeURIComponent(new URL(req.url, "http://x").pathname));
    if (!p.startsWith(PROJ)) { res.writeHead(403).end(); return; }
    const st = await stat(p);
    if (st.isDirectory()) { res.writeHead(404).end(); return; }
    res.writeHead(200, { "content-type": MIME[extname(p)] || "application/octet-stream" });
    res.end(await readFile(p));
  } catch { res.writeHead(404).end(); }
});
await new Promise(r => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch({ executablePath: CHROME, args: ["--disable-gpu", "--font-render-hinting=none"] });
try {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", e => errors.push(String(e)));
  await page.goto(`${base}/tools/svg-harness.html`);
  const tls = await page.evaluate(id => window.__hfLoadScene(id), args.scene);
  if (!tls.includes(args.scene)) throw new Error(`timeline ${args.scene} not registered (got ${tls.join(",")}); page errors: ${errors.join(" | ")}`);
  await page.evaluate(([id, t]) => window.__hfSeek(id, t), [args.scene, parseFloat(args.time)]);
  if (args.force && args.force !== true) await page.addStyleTag({ content: args.force }); // write !important yourself
  await page.waitForTimeout(150);
  if (args.eval) { console.log(JSON.stringify(await page.evaluate(args.eval), null, 1)); process.exitCode = 0; throw "__eval_done__"; }
  await mkdir(dirname(out), { recursive: true });
  await page.screenshot({ path: `${stem}.ref.png` });

  await page.addScriptTag({ path: join(HERE, "serialize.js") });
  const { svg, stats } = await page.evaluate(([title, scene]) => window.__hfToSVG({ title, stripPrefix: "" }), [args.title || args.scene, args.scene]);
  // Illustrator-friendly links
  const svgOut = svg.replace(/<(use|image)([^>]*?)\shref="/g, "<$1$2 xlink:href=\"");
  await writeFile(out, svgOut);
  const kb = Math.round(Buffer.byteLength(svgOut) / 1024);
  console.log(JSON.stringify({ out: args.out, kb, stats, pageErrors: errors }));

  if (args.qa) {
    const qa = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
    const fontCss = (await readFile(join(PROJ, "tools/svg-harness.html"), "utf8")).match(/@font-face[^}]+}/g).join("\n");
    await qa.goto(`${base}/tools/svg-harness.html`);
    await qa.evaluate(([css, s]) => {
      document.body.innerHTML = `<style>${css} html,body{margin:0;background:#000}</style>` + s.replace(/^<\?xml[^>]*>/, "");
    }, [fontCss, svgOut]);
    await qa.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.querySelectorAll("image")].map(() => 0)); });
    await qa.waitForTimeout(400);
    await qa.screenshot({ path: `${stem}.qa.png` });
    // pixel diff in-page
    const score = await qa.evaluate(async ([a, b]) => {
      const load = src => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = src; });
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
      x.putImageData(diff, 0, 0);
      return { meanAbsDiff: +(sum / (1920 * 1080)).toFixed(2), pctPixelsOff: +(100 * bad / (1920 * 1080)).toFixed(2), diffPng: c.toDataURL("image/png") };
    }, [`${base}/${args.out.replace(/\.svg$/, ".ref.png")}`, `${base}/${args.out.replace(/\.svg$/, ".qa.png")}`]);
    await writeFile(`${stem}.diff.png`, Buffer.from(score.diffPng.split(",")[1], "base64"));
    console.log(JSON.stringify({ qa: { meanAbsDiff: score.meanAbsDiff, pctPixelsOff: score.pctPixelsOff, ref: `${stem}.ref.png`, render: `${stem}.qa.png`, diff: `${stem}.diff.png` } }));
  }
} catch (e) { if (e !== "__eval_done__") throw e; } finally {
  await browser.close();
  server.close();
}
