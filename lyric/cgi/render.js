// usage: node render.js preview t1,t2,... <outdir>
//        node render.js full <song_audio> <out.mp4> <silent_out.mp4> [workers=2]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..', '..');
const TOTAL = 60.0, FPS = 30;
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.ttf': 'font/ttf', '.json': 'application/json' };
function serve() {
  return new Promise(res => { const s = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0])); if (!f.startsWith(ROOT) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(r); }); s.listen(0, '127.0.0.1', () => res(s)); });
}
async function openPage(browser, port) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message)); page.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await page.goto(`http://127.0.0.1:${port}/lyric/cgi/index.html`); await page.waitForFunction(() => window.__ready && window.render, null, { timeout: 120000 }); await page.evaluate(() => window.__ready);
  return page;
}
const launch = () => chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
async function chunk(port, f0, f1, out) {
  const browser = await launch(); const page = await openPage(browser, port);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', String(FPS), out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let i = f0; i < f1; i++) {
    await page.evaluate(t => window.render(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if ((i - f0) % 60 === 0) console.log(`[${f0}-${f1}] frame ${i} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await browser.close();
}
(async () => {
  const [, , mode, a1, a2, a3, a4] = process.argv; const srv = await serve(); const port = srv.address().port;
  if (mode === 'preview') {
    const browser = await launch(); const page = await openPage(browser, port);
    for (const t of a1.split(',').map(Number)) { const s = Date.now(); await page.evaluate(t => window.render(t), t); await page.screenshot({ path: path.join(a2, `c_${t.toFixed(2).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 90 }); console.log(t, Date.now() - s, 'ms'); }
    await browser.close();
  } else {
    const workers = +(a4 || 2), N = Math.round(TOTAL * FPS), per = Math.ceil(N / workers), parts = [];
    await Promise.all(Array.from({ length: workers }, (_, w) => { const out = a3.replace(/\.mp4$/, `_part${w}.mp4`); parts.push(out); return chunk(port, w * per, Math.min(N, (w + 1) * per), out); }));
    const list = a3.replace(/\.mp4$/, '_list.txt'); fs.writeFileSync(list, parts.map(p => `file '${p}'`).join('\n'));
    await new Promise(r => spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', a3], { stdio: 'inherit' }).on('close', r));
    await new Promise(r => spawn('ffmpeg', ['-v', 'error', '-y', '-i', a3, '-i', a1, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', String(TOTAL), '-movflags', '+faststart', a2], { stdio: 'inherit' }).on('close', r));
    parts.forEach(p => fs.unlinkSync(p)); fs.unlinkSync(list); console.log('done', a2, a3);
  }
  srv.close();
})();
