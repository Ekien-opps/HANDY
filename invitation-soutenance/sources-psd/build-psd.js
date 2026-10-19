// Convertit une page HTML « calquée » (éléments [data-l]) en PSD multicalque :
// textes éditables, formes vectorielles, images, masques et effets de calque.
// Usage : node build-psd.js <dossier-src> <dossier-sortie> <page.html>...
const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { writePsd } = require('ag-psd');
const { PNG } = require('pngjs');

const [srcDir, outDir, ...pages] = process.argv.slice(2);

const MIME = { '.html': 'text/html', '.png': 'image/png', '.jpg': 'image/jpeg' };
function serve(root) {
  return new Promise(resolve => {
    const srv = http.createServer((req, res) => {
      const f = path.join(root, decodeURIComponent(req.url.split('?')[0]));
      if (!f.startsWith(root) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
      res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}

const hex = h => ({ r: parseInt(h.slice(1, 3), 16), g: parseInt(h.slice(3, 5), 16), b: parseInt(h.slice(5, 7), 16) });

function decodePng(buf) {
  const p = PNG.sync.read(buf);
  return { width: p.width, height: p.height, data: new Uint8ClampedArray(p.data.buffer, p.data.byteOffset, p.data.length) };
}

// Recadre une image RGBA sur ses pixels non transparents.
function trim(img, left, top) {
  const { width: w, height: h, data } = img;
  let x0 = w, y0 = h, x1 = -1, y1 = -1;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    if (data[(y * w + x) * 4 + 3]) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; }
  }
  if (x1 < 0) return null;
  const nw = x1 - x0 + 1, nh = y1 - y0 + 1, out = new Uint8ClampedArray(nw * nh * 4);
  for (let y = 0; y < nh; y++) out.set(data.subarray(((y + y0) * w + x0) * 4, ((y + y0) * w + x1 + 1) * 4), y * nw * 4);
  return { img: { width: nw, height: nh, data: out }, left: left + x0, top: top + y0 };
}

function rectPath(x, y, w, h, r) {
  const k = (pts) => ({ linked: !!r, points: pts });
  if (!r) {
    const c = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
    return [{ open: false, operation: 'combine', fillRule: 'non-zero', knots: c.map(([a, b]) => ({ linked: false, points: [a, b, a, b, a, b] })) }];
  }
  const m = r * 0.5523;
  return [{ open: false, operation: 'combine', fillRule: 'non-zero', knots: [
    k([x + r - m, y, x + r, y, x + r, y]), k([x + w - r, y, x + w - r, y, x + w - r + m, y]),
    k([x + w, y + r - m, x + w, y + r, x + w, y + r]), k([x + w, y + h - r, x + w, y + h - r, x + w, y + h - r + m]),
    k([x + w - r + m, y + h, x + w - r, y + h, x + w - r, y + h]), k([x + r, y + h, x + r, y + h, x + r - m, y + h]),
    k([x, y + h - r + m, x, y + h - r, x, y + h - r]), k([x, y + r, x, y + r, x, y + r - m]),
  ] }];
}

function vectorContent(fill) {
  if (typeof fill === 'string') return { type: 'color', color: hex(fill) };
  return {
    type: 'solid', name: 'Dégradé Marin\'Or', smoothness: 1,
    style: fill.grad, angle: fill.angle || 0, scale: fill.scale || 1, align: true, dither: false,
    offset: fill.offset || { x: 0, y: 0 },
    colorStops: fill.stops.map(([c, , l]) => ({ color: hex(c), location: l, midpoint: 0.5 })),
    opacityStops: fill.stops.map(([, o, l]) => ({ opacity: o, location: l, midpoint: 0.5 })),
  };
}

function effects(fx, dsf) {
  if (!fx) return undefined;
  const e = {};
  if (fx.shadow) e.dropShadow = [{
    present: true, showInDialog: true, enabled: true, blendMode: 'multiply', color: { r: 0, g: 0, b: 0 },
    opacity: fx.shadow.opacity, angle: 90, useGlobalLight: false, antialiased: false, layerConceals: true,
    distance: { units: 'Pixels', value: fx.shadow.y * dsf }, size: { units: 'Pixels', value: fx.shadow.blur * dsf },
    choke: { units: 'Pixels', value: 0 },
  }];
  if (fx.overlay) e.solidFill = [{ present: true, showInDialog: true, enabled: true, blendMode: 'normal', color: hex(fx.overlay), opacity: 1 }];
  return e;
}

// Masque de fusion en dégradé (linéaire vertical/horizontal ou radial « farthest-corner » façon CSS).
function gradientMask(spec, layer, el) {
  const stops = spec.stops || [[spec.from, 1], [spec.to, 0]];
  const at = t => {
    if (t <= stops[0][0]) return stops[0][1];
    for (let i = 1; i < stops.length; i++) if (t <= stops[i][0]) {
      const [t0, a0] = stops[i - 1], [t1, a1] = stops[i];
      return a0 + (a1 - a0) * (t - t0) / (t1 - t0);
    }
    return stops[stops.length - 1][1];
  };
  let cx, cy, rx, ry;
  if (spec.type === 'radial') {
    cx = el.x + spec.cx * el.w; cy = el.y + spec.cy * el.h;
    rx = Math.max(cx - el.x, el.x + el.w - cx) * Math.SQRT2; ry = Math.max(cy - el.y, el.y + el.h - cy) * Math.SQRT2;
  }
  const w = layer.right - layer.left, h = layer.bottom - layer.top, data = new Uint8ClampedArray(w * h * 4);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const X = layer.left + x + 0.5, Y = layer.top + y + 0.5;
    const t = spec.type === 'radial' ? Math.hypot((X - cx) / rx, (Y - cy) / ry)
      : spec.dir === 'h' ? (X - el.x) / el.w : (Y - el.y) / el.h;
    const i = (y * w + x) * 4; data[i] = data[i + 1] = data[i + 2] = Math.round(255 * at(t)); data[i + 3] = 255;
  }
  return { top: layer.top, left: layer.left, right: layer.right, bottom: layer.bottom, defaultColor: 0, imageData: { width: w, height: h, data } };
}

const SOLO_CSS = `[data-l]{visibility:hidden!important}
[data-l].solo{visibility:visible!important;opacity:1!important;-webkit-mask-image:none!important;mask-image:none!important;text-shadow:none!important}
html,body,.page{background:transparent!important}`;

async function build(browser, base, file) {
  const html = fs.readFileSync(path.join(srcDir, file), 'utf8');
  const meta = JSON.parse(html.match(/name="psd" content='([^']+)'/)[1]);
  const { dsf, w: W, h: H } = meta;
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: dsf });
  await page.goto(`${base}/${file}`, { waitUntil: 'networkidle' });
  await page.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); });

  const composite = decodePng(await page.screenshot());
  fs.writeFileSync(path.join(outDir, meta.out + '_apercu.png'), PNG.sync.write(Object.assign(new PNG({ width: composite.width, height: composite.height }), { data: Buffer.from(composite.data) })));

  const infos = await page.evaluate(() => {
    const FONT = { 400: 'Regular', 500: 'Medium', 600: 'SemiBold', 700: 'Bold' };
    const rgb = s => { const m = s.match(/[\d.]+/g).map(Number); return { r: m[0], g: m[1], b: m[2] }; };
    return [...document.querySelectorAll('[data-l]')].map((el, i) => {
      el.dataset.idx = i;
      const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
      const o = {
        idx: i, name: el.dataset.l, group: el.dataset.g, kind: el.dataset.k,
        rect: { x: r.left, y: r.top, w: r.width, h: r.height },
        opacity: parseFloat(el.dataset.o || '1'),
        psd: el.dataset.psd ? JSON.parse(el.dataset.psd) : null,
        mask: el.dataset.mask ? JSON.parse(el.dataset.mask) : null,
        fx: el.dataset.fx ? JSON.parse(el.dataset.fx) : null,
      };
      if (o.kind === 'text') {
        const runs = [];
        const push = (text, node) => {
          const s = getComputedStyle(node);
          const w = parseInt(s.fontWeight, 10), it = s.fontStyle === 'italic';
          const style = { font: 'Montserrat-' + (FONT[w] === 'Regular' && it ? '' : FONT[w]) + (it ? 'Italic' : ''), color: rgb(s.color) };
          const last = runs[runs.length - 1];
          if (last && last.style.font === style.font && JSON.stringify(last.style.color) === JSON.stringify(style.color)) last.text += text;
          else runs.push({ text, style });
        };
        const walk = n => n.childNodes.forEach(c => {
          if (c.nodeType === 3) push(c.textContent.replace(/\s+/g, ' '), n);
          else if (c.nodeName === 'BR') push('\n', n);
          else walk(c);
        });
        walk(el);
        const mk = document.createElement('span');
        mk.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
        el.insertBefore(mk, el.firstChild);
        const baseline = mk.getBoundingClientRect().top;
        mk.remove();
        const fs = parseFloat(cs.fontSize);
        const ls = cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing);
        const lh = cs.lineHeight.endsWith('px') ? parseFloat(cs.lineHeight) : parseFloat(cs.lineHeight) * fs;
        const align = cs.textAlign === 'center' ? 'center' : cs.textAlign === 'right' || cs.textAlign === 'end' ? 'right' : 'left';
        const ax = align === 'center' ? (r.left + r.right) / 2 : align === 'right' ? r.right : r.left;
        o.text = { runs, baseline, ax, align, fontSize: fs, tracking: Math.round(ls / fs * 1000), leading: lh };
      }
      return o;
    });
  });

  await page.addStyleTag({ content: SOLO_CSS });
  const groups = new Map(), children = [];
  for (const L of infos) {
    let img, left, top;
    if (L.kind === 'img') {
      const wpx = Math.round(L.rect.w * dsf), hpx = Math.round(L.rect.h * dsf);
      const url = await page.evaluate(([idx, w, h]) => {
        const el = document.querySelector(`[data-idx="${idx}"]`), c = document.createElement('canvas');
        c.width = w; c.height = h;
        const ctx = c.getContext('2d'); ctx.imageSmoothingQuality = 'high'; ctx.drawImage(el, 0, 0, w, h);
        return c.toDataURL('image/png');
      }, [L.idx, wpx, hpx]);
      img = decodePng(Buffer.from(url.split(',')[1], 'base64'));
      left = Math.round(L.rect.x * dsf); top = Math.round(L.rect.y * dsf);
    } else {
      const pad = 3;
      const x0 = Math.max(0, Math.floor(L.rect.x - pad)), y0 = Math.max(0, Math.floor(L.rect.y - pad));
      const x1 = Math.min(W, Math.ceil(L.rect.x + L.rect.w + pad)), y1 = Math.min(H, Math.ceil(L.rect.y + L.rect.h + pad));
      await page.evaluate(i => document.querySelector(`[data-idx="${i}"]`).classList.add('solo'), L.idx);
      img = decodePng(await page.screenshot({ clip: { x: x0, y: y0, width: x1 - x0, height: y1 - y0 }, omitBackground: true }));
      await page.evaluate(i => document.querySelector(`[data-idx="${i}"]`).classList.remove('solo'), L.idx);
      left = x0 * dsf; top = y0 * dsf;
    }
    const t = trim(img, left, top);
    if (!t) { console.warn('calque vide :', L.name); continue; }
    const layer = {
      name: L.name, opacity: L.opacity, blendMode: 'normal',
      left: t.left, top: t.top, right: t.left + t.img.width, bottom: t.top + t.img.height,
      imageData: t.img,
    };
    const fx = effects(L.fx, dsf);
    if (fx) layer.effects = fx;
    const elRect = { x: L.rect.x * dsf, y: L.rect.y * dsf, w: L.rect.w * dsf, h: L.rect.h * dsf };
    if (L.mask) layer.mask = gradientMask(L.mask, layer, elRect);
    if (L.kind === 'shape') {
      const p = L.psd;
      layer.vectorMask = { paths: rectPath(elRect.x, elRect.y, elRect.w, elRect.h, (p.r || 0) * dsf) };
      if (p.stroke) {
        layer.vectorFill = { type: 'color', color: hex(p.stroke.color) };
        layer.vectorStroke = {
          strokeEnabled: true, fillEnabled: !!p.fill, lineWidth: { units: 'Points', value: p.stroke.w * dsf },
          lineDashOffset: { units: 'Points', value: 0 }, miterLimit: 100, lineCapType: 'butt', lineJoinType: 'miter',
          lineAlignment: 'inside', scaleLock: false, strokeAdjust: false, lineDashSet: [], blendMode: 'normal', opacity: 1,
          content: { type: 'color', color: hex(p.stroke.color) }, resolution: 72,
        };
        if (p.fill) layer.vectorFill = vectorContent(p.fill);
      } else {
        layer.vectorFill = vectorContent(p.fill);
      }
    }
    if (L.kind === 'text') {
      const T = L.text;
      const styleOf = s => ({
        font: { name: s.font }, fontSize: T.fontSize * dsf, fillColor: s.color, tracking: T.tracking,
        autoLeading: false, leading: T.leading * dsf, autoKerning: true,
      });
      layer.text = {
        text: T.runs.map(r => r.text).join(''),
        transform: [1, 0, 0, 1, T.ax * dsf, T.baseline * dsf],
        antiAlias: 'smooth', shapeType: 'point',
        style: styleOf(T.runs[0].style),
        styleRuns: T.runs.map(r => ({ length: r.text.length, style: styleOf(r.style) })),
        paragraphStyle: { justification: T.align },
      };
    }
    if (!groups.has(L.group)) { const g = { name: L.group, opened: true, children: [] }; groups.set(L.group, g); children.push(g); }
    groups.get(L.group).children.push(layer);
  }
  await page.close();

  const psd = {
    width: W * dsf, height: H * dsf, channels: 3, bitsPerChannel: 8, colorMode: 3,
    imageResources: { resolutionInfo: { horizontalResolution: 72, horizontalResolutionUnit: 'PPI', widthUnit: 'Inches', verticalResolution: 72, verticalResolutionUnit: 'PPI', heightUnit: 'Inches' } },
    imageData: composite,
    children,
  };
  const buf = writePsd(psd, { generateThumbnail: false, noBackground: true });
  fs.writeFileSync(path.join(outDir, meta.out + '.psd'), Buffer.from(buf));
  console.log(meta.out + '.psd', (buf.byteLength / 1048576).toFixed(1) + ' Mo', infos.length + ' calques');
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const srv = await serve(path.resolve(srcDir));
  const base = `http://127.0.0.1:${srv.address().port}`;
  const browser = await chromium.launch();
  for (const f of pages) await build(browser, base, f);
  await browser.close();
  srv.close();
})().catch(e => { console.error(e); process.exit(1); });
