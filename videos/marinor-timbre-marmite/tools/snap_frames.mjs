// Fast preview: load index.html in the same headless Chromium, call window.__renderFrame(f) and screenshot.
// Usage: node tools/snap_frames.mjs <outDir> <frames: "0,8,12" or "0-59"> [bg: transparent|checker|grey] [dpr]
// Writes <outDir>/f<NN>.png (transparent background unless bg given). Prints per-frame timings.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("/opt/node-tools/node_modules/playwright-core");
const CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const [outDir, spec = "0", bg = "transparent", dprArg = "1", dbg = "{}"] = process.argv.slice(2);
const frames = [];
for (const part of spec.split(",")) {
  const m = part.match(/^(\d+(?:\.\d+)?)-(\d+)$/);
  if (m) for (let f = +m[1]; f <= +m[2]; f++) frames.push(f);
  else frames.push(+part);
}
fs.mkdirSync(outDir, { recursive: true });
const browser = await chromium.launch({
  executablePath: CHROME,
  args: ["--allow-file-access-from-files", "--disable-gpu", "--force-color-profile=srgb", "--font-render-hinting=none"],
});
const ctx = await browser.newContext({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: +dprArg });
const page = await ctx.newPage();
page.on("console", (m) => { if (m.type() === "error") console.log("console:", m.text()); });
page.on("pageerror", (e) => console.log("pageerror:", e.message));
await page.addInitScript((d) => { window.__hfDebug = JSON.parse(d); }, dbg);
await page.goto(pathToFileURL(path.join(ROOT, "index.html")).href, { waitUntil: "load" });
{
  const d = JSON.parse(dbg);
  if (d.eval) await page.evaluate((code) => { (0, eval)(code); }, d.eval);
}
if (bg !== "transparent") {
  const css = bg === "checker"
    ? "background-color:#8a8a8a;background-image:linear-gradient(45deg,#757575 25%,transparent 25%,transparent 75%,#757575 75%),linear-gradient(45deg,#757575 25%,transparent 25%,transparent 75%,#757575 75%);background-size:32px 32px;background-position:0 0,16px 16px"
    : `background:${bg}`;
  await page.evaluate((c) => { document.documentElement.style.cssText += ";" + c; document.body.style.background = "transparent"; }, css);
}
for (const f of frames) {
  const t0 = Date.now();
  await page.evaluate(async (fr) => {
    window.__renderFrame(fr);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  }, f);
  const name = path.join(outDir, `f${String(f).padStart(2, "0")}.png`);
  await page.screenshot({ path: name, omitBackground: bg === "transparent" });
  console.log(`f${f} ${Date.now() - t0} ms`);
}
await browser.close();
