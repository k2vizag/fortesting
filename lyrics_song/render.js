// usage: node render.js <data.json> <out.mp4> <audio> [preview t1,t2]
const { chromium } = require('playwright'); const { spawn } = require('child_process');
const fs = require('fs'); const path = require('path');
const [, , dj, out, audio, mode, arg] = process.argv;
const data = JSON.parse(fs.readFileSync(dj, 'utf8'));
(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.addInitScript(d => { window.__DATA__ = d; }, data);
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto('file://' + path.resolve(__dirname, 'lyrics.html'));
  await page.evaluate(() => window.__ready);
  if (mode === 'preview') {
    for (const t of arg.split(',').map(Number)) { await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: `${out}_${t.toFixed(2)}.png` }); }
  } else {
    const fps = 30, N = Math.round(data.total * fps);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-i', audio,
      '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
      '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < N; i++) { await page.evaluate(t => window.render(t), i / fps);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 450 === 0) console.log(`frame ${i}/${N}`); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log('done', out);
  }
  await browser.close();
})();
