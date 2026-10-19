// Rendu final « qualité export After Effects » :
// suréchantillonnage ×2, flou de bougé par accumulation de sous-images (obturateur 180°, phase −90°),
// sortie maître sans perte (FFV1) via ffmpeg.
// Usage : node render-final.js <dossier> <page.html> <sortie.mkv> <fps> <dsf> <largeur> <hauteur> <echantillons> [freeze]
const http = require('http'), fs = require('fs'), path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');
const { PNG } = require('pngjs');
const [dir, page, out, FPS, DSF, OW, OH, N, freeze] = process.argv.slice(2);
const fps = +FPS, dsf = +DSF, samples = +N, CW = 1400, CH = 758, DUR = 10;
const MOTION = [5, 182];   // plage (en images à 30 i/s) où quelque chose bouge vraiment
const root = path.resolve(dir);
const MIME = { '.html': 'text/html', '.png': 'image/png', '.jpg': 'image/jpeg', '.ttf': 'font/ttf' };
const srv = http.createServer((q, r) => {
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!f.startsWith(root) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r);
}).listen(0, '127.0.0.1', async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: CW, height: CH }, deviceScaleFactor: dsf });
  await pg.goto(`http://127.0.0.1:${srv.address().port}/${page}`, { waitUntil: 'networkidle' });
  await pg.evaluate(async fr => { window.FREEZE = fr; await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); }, freeze === 'freeze');
  if (!(await pg.evaluate(() => document.fonts.check('900 28px "Cream Heavy"')))) throw new Error('Cream Heavy non chargée');
  const W = Math.round(CW * dsf), H = Math.round(CH * dsf);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', `${W}x${H}`, '-r', String(fps), '-i', '-',
    '-vf', `scale=${OW}:${OH}:flags=lanczos+accurate_rnd+full_chroma_int`, '-c:v', 'ffv1', '-level', '3', '-pix_fmt', 'gbrp', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const write = buf => new Promise(res => ff.stdin.write(buf) ? res() : ff.stdin.once('drain', res));
  const total = DUR * fps, k30 = 30 / fps;
  const sum = new Uint16Array(W * H * 3), rgb = Buffer.alloc(W * H * 3);
  const t0 = Date.now();
  for (let i = 0; i < total; i++) {
    const fc = i * k30, n = fc >= MOTION[0] && fc <= MOTION[1] ? samples : 1;
    sum.fill(0);
    for (let s = 0; s < n; s++) {
      const f = n === 1 ? fc : fc + ((s + 0.5) / n - 0.5) * 0.5 * k30;
      await pg.evaluate(([f, fc]) => window.render(f, fc), [f, fc]);
      let { data, width, height } = PNG.sync.read(await pg.screenshot());
      if (width !== W || height !== H) throw new Error(`taille ${width}x${height} ≠ ${W}x${H}`);
      for (let p = 0, q = 0; p < data.length; p += 4, q += 3) { sum[q] += data[p]; sum[q + 1] += data[p + 1]; sum[q + 2] += data[p + 2]; }
    }
    for (let q = 0; q < sum.length; q++) rgb[q] = Math.round(sum[q] / n);
    await write(rgb);
    if (i % 30 === 0) console.log(`image ${i}/${total}  (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
  }
  ff.stdin.end();
  await new Promise(res => ff.on('close', res));
  await b.close(); srv.close();
  console.log('ok', out);
});
