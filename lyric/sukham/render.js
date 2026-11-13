// usage: node render.js preview t1,t2,...  <outdir>
//        node render.js full <song_audio> <out.mp4> [silent_out.mp4]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const [, , mode, a1, a2, a3] = process.argv;
const TOTAL = 31.6, FPS = 30;
(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto('file://' + path.resolve(__dirname, 'scene.html'));
  await page.evaluate(() => window.__ready);
  if (mode === 'preview') {
    for (const t of a1.split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(a2, `p_${t.toFixed(2)}.png`) });
    }
  } else {
    const silent = a3 || a2.replace(/\.mp4$/, '_nomusic.mp4');
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', String(FPS), silent], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = Math.round(TOTAL * FPS), t0 = Date.now();
    for (let i = 0; i < N; i++) {
      await page.evaluate(t => window.render(t), i / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`frame ${i}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    await new Promise(r => spawn('ffmpeg', ['-v', 'error', '-y', '-i', silent, '-i', a1, '-map', '0:v', '-map', '1:a',
      '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', a2], { stdio: 'inherit' }).on('close', r));
    console.log('done', a2, silent);
  }
  await browser.close();
})();
