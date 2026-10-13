// Rasterize a local HTML/SVG file with headless Chromium, exactly as the composition
// renderer will see it.  Transparent background, deviceScaleFactor 1.
//   node tools/chrome_shot.cjs <in.html|in.svg> <out.png> <width> <height>
const path = require("path");
const { chromium } = require("/opt/node-tools/node_modules/playwright-core");

(async () => {
  const [inp, out, w, h] = process.argv.slice(2);
  const browser = await chromium.launch({
    executablePath: "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    args: ["--force-color-profile=srgb", "--disable-gpu"],
  });
  const page = await browser.newPage({
    viewport: { width: +w, height: +h },
    deviceScaleFactor: 1,
  });
  await page.goto("file://" + path.resolve(inp));
  await page.waitForTimeout(150);
  await page.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width: +w, height: +h } });
  await browser.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
