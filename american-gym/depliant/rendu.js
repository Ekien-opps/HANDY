// Rendu des aperçus PNG et du PDF d'impression (Chromium / Playwright).
// Usage : node rendu.js   (après python3 generer_depliant.py)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const here = __dirname;
const fonts = path.join(here, '..', 'fonts');
const styles = ['Regular', 'Medium', 'SemiBold', 'Bold', 'ExtraBold', 'Black'];
const fontCss = styles.map(s =>
  `@font-face{font-family:'Montserrat-${s}';src:url('file://${fonts}/Montserrat-${s}.ttf');}`).join('');

function page(svgs, w, h) {
  const body = svgs.map(f => `<div class="p">${fs.readFileSync(f, 'utf8').replace(/<\?xml[^>]*>/, '')}</div>`).join('');
  return `<!doctype html><html><head><meta charset="utf-8"><style>${fontCss}
    @page{size:${w}mm ${h}mm;margin:0} html,body{margin:0;padding:0}
    .p{width:${w}mm;height:${h}mm;overflow:hidden;page-break-after:always}
    .p svg{display:block;width:${w}mm;height:${h}mm}</style></head><body>${body}</body></html>`;
}

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }).catch(() => chromium.launch());
  const tmp = path.join(here, '_impression');
  const ctx = await browser.newContext({ deviceScaleFactor: 3 });
  const p = await ctx.newPage();
  for (const side of ['exterieur', 'interieur']) {
    const html = path.join(tmp, `apercu_${side}.html`);
    fs.writeFileSync(html, page([path.join(here, `american_gym_depliant_${side}.svg`)], 297, 210));
    await p.goto('file://' + html);
    await p.evaluate(() => document.fonts.ready);
    await p.setViewportSize({ width: 1123, height: 794 });
    await p.screenshot({ path: path.join(here, `apercu_${side}.png`), clip: { x: 0, y: 0, width: 1123, height: 794 } });
  }
  const html = path.join(tmp, 'impression.html');
  fs.writeFileSync(html, page(['exterieur', 'interieur'].map(s => path.join(tmp, `${s}.svg`)), 303, 216));
  await p.goto('file://' + html);
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.join(here, 'american_gym_depliant_impression.pdf'), width: '303mm', height: '216mm', printBackground: true });
  await browser.close();
  console.log('aperçus PNG + PDF écrits');
})();
