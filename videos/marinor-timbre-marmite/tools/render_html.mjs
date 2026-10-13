// Rasterize one or more local HTML files with the same headless Chromium HyperFrames uses.
// Usage: node tools/render_html.mjs <in.html> <out.png> <width> <height> [deviceScaleFactor] [transparent(0|1)]
//        node tools/render_html.mjs --batch <jobs.json>   (jobs: [{html,out,width,height,dpr,transparent}])
// Deterministic: no animation, waits for all <img>/<image> to load and two rAFs before the screenshot.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("/opt/node-tools/node_modules/playwright-core");
const CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";

async function renderOne(browser, job) {
  const ctx = await browser.newContext({
    viewport: { width: job.width, height: job.height },
    deviceScaleFactor: job.dpr || 1,
  });
  const page = await ctx.newPage();
  await page.goto(pathToFileURL(path.resolve(job.html)).href, { waitUntil: "load" });
  await page.evaluate(async () => {
    const imgs = [...document.images].map((i) => (i.decode ? i.decode().catch(() => {}) : null));
    await Promise.all(imgs);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  });
  await page.screenshot({ path: job.out, omitBackground: !!job.transparent, fullPage: false });
  await ctx.close();
}

const args = process.argv.slice(2);
let jobs;
if (args[0] === "--batch") {
  jobs = JSON.parse(fs.readFileSync(args[1], "utf8"));
} else {
  const [html, out, w, h, dpr, tr] = args;
  jobs = [{ html, out, width: +w, height: +h, dpr: dpr ? +dpr : 1, transparent: tr === "1" }];
}
const browser = await chromium.launch({
  executablePath: CHROME,
  args: ["--allow-file-access-from-files", "--disable-gpu", "--force-color-profile=srgb", "--font-render-hinting=none"],
});
for (const j of jobs) await renderOne(browser, j);
await browser.close();
