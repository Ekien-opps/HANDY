// Preview renders of the OBJ with three.js in headless Chromium (transparent PNGs).
// Usage: node tools/render_preview.mjs <produit> [w] [h]  -> renders/<produit>/apercu_*.png + build/<produit>/<name>.glb
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("/opt/node-tools/node_modules/playwright-core");

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const [product, w = "1600", h = "2000"] = process.argv.slice(2);
if (!product) { console.error("usage: node tools/render_preview.mjs <produit> [w] [h]"); process.exit(1); }
const outDir = path.join(ROOT, "renders", product);
const cfg = JSON.parse(fs.readFileSync(path.join(ROOT, "build", product, "preview.json"), "utf8"));
fs.mkdirSync(outDir, { recursive: true });

const MIME = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".png": "image/png", ".webp": "image/webp", ".obj": "text/plain", ".mtl": "text/plain", ".json": "application/json" };
const server = http.createServer((req, res) => {
  const p = path.join(ROOT, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (!p.startsWith(ROOT) || !fs.existsSync(p) || fs.statSync(p).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { "Content-Type": MIME[path.extname(p)] || "application/octet-stream" });
  fs.createReadStream(p).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const port = server.address().port;

const browser = await chromium.launch({
  executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
  args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"],
});
const page = await browser.newPage({ viewport: { width: +w, height: +h } });
page.on("console", (m) => { if (m.type() === "error") console.error("[page]", m.text()); });
page.on("pageerror", (e) => console.error("[pageerror]", e.message));
await page.goto(`http://127.0.0.1:${port}/tools/preview.html?w=${w}&h=${h}&cfg=../build/${product}/preview.json`);
await page.waitForFunction(() => window.__ready === true, null, { timeout: 180000 });

const VIEWS = [
  ["face", 0, 3, 62],
  ["trois-quarts", 34, 9, 62],
  ["dos", 180, 3, 62],
  ["profil", 90, 3, 62],
  ["plongee", -24, 22, 64],
];
for (const [name, az, el, d] of VIEWS) {
  const t0 = Date.now();
  const url = await page.evaluate(([a, e, dd]) => window.renderView(a, e, dd), [az, el, d]);
  fs.writeFileSync(path.join(outDir, `apercu_${name}.png`), Buffer.from(url.split(",")[1], "base64"));
  console.log(name, Date.now() - t0, "ms");
}
{
  const glb = path.join(ROOT, "build", product, cfg.name + ".glb");
  const b64 = await page.evaluate(() => window.exportGLB());
  fs.writeFileSync(glb, Buffer.from(b64, "base64"));
  console.log("glb", glb);
}
await browser.close();
server.close();
