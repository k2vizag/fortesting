// usage: node render_song.js data.json out_dir preview t1,t2 | full audio.wav out.mp4
const { chromium } = require('playwright'); const { spawn } = require('child_process');
const fs = require('fs'); const path = require('path');
const [, , dataP, outDir, mode, a1, a2] = process.argv;
const data = JSON.parse(fs.readFileSync(dataP, 'utf8'));
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.addInitScript(d => { window.__DATA__ = d; }, data);
  p.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await p.goto('file://' + path.resolve(__dirname, 'lyric.html')); await p.evaluate(() => window.__ready); await p.waitForTimeout(300);
  if (mode === 'preview') {
    for (const t of a1.split(',').map(Number)) { await p.evaluate(t => window.render(t), t);
      await p.screenshot({ path: path.join(outDir, `ly_${t.toFixed(2)}.png`) }); }
  } else {
    const fps = 30, N = Math.round(data.total * fps);
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-i', a1,
      '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
      '-shortest', '-movflags', '+faststart', a2], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < N; i++) { await p.evaluate(t => window.render(t), i / fps);
      const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 300 === 0) console.log('frame', i, '/', N); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log('done', a2);
  }
  await b.close();
})();
