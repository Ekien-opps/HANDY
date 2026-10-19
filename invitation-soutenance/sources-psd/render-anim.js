// Rend l'animatic image par image (30 i/s) puis l'encode en MP4.
const http = require('http'), fs = require('fs'), path = require('path');
const { execFileSync } = require('child_process');
const { chromium } = require('playwright');
const [srcDir, page, out, scale = '0.5'] = process.argv.slice(2);
const root = path.resolve(srcDir), frames = path.join(path.dirname(out), 'frames');
fs.rmSync(frames, { recursive: true, force: true }); fs.mkdirSync(frames, { recursive: true });
const MIME = { '.html': 'text/html', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = http.createServer((q, r) => {
  const f = path.join(root, decodeURIComponent(q.url.split('?')[0]));
  if (!f.startsWith(root) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r);
}).listen(0, '127.0.0.1', async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 2500, height: 1429 }, deviceScaleFactor: +scale });
  await pg.goto(`http://127.0.0.1:${srv.address().port}/${page}`, { waitUntil: 'networkidle' });
  await pg.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map(i => i.decode())); });
  const end = await pg.evaluate(() => window.END);
  for (let f = 0; f <= end; f++) {
    await pg.evaluate(f => window.render(f), f);
    await pg.screenshot({ path: path.join(frames, String(f).padStart(4, '0') + '.png') });
  }
  await b.close(); srv.close();
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '30', '-i', path.join(frames, '%04d.png'),
    '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', out]);
  console.log('ok', out, end + 1, 'images');
});
