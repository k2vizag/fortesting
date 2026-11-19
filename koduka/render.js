// usage: node render.js data.json preview t1,t2,... <outdir>     (PNG frames)
//        node render.js data.json full <out_silent.mp4> [fps]     (scene layer video, no audio)
// data.json: {total, scenes:[{a,b,key,seed}]}
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const [, , dataFile, mode, a1, a2] = process.argv;
const D = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('PAGE ERROR', e.message); process.exit(1); });
  await page.addInitScript(d => { window.__DATA__ = d; }, D);
  await page.goto('file://' + path.resolve(__dirname, 'sil.html'));
  await page.evaluate(() => window.__ready);
  if (mode === 'preview') {
    for (const t of a1.split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(a2, `p_${t.toFixed(2)}.png`) });
    }
  } else {
    const FPS = Number(a2 || 30);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), a1], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = Math.round(D.total * FPS), t0 = Date.now();
    for (let i = 0; i < N; i++) {
      await page.evaluate(t => window.render(t), i / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 90 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 600 === 0) console.log(`frame ${i}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
