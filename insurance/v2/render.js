// usage: node render.js <workdir> preview t1,t2,...   |   node render.js <workdir> full
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const [, , work, mode, arg] = process.argv;
const data = JSON.parse(fs.readFileSync(path.join(work, 'data.json'), 'utf8'));
(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.addInitScript(d => { window.__DATA__ = d; }, data);
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto('file://' + path.resolve(__dirname, 'overlay.html'));
  await page.evaluate(() => window.__ready);
  await page.waitForTimeout(300);
  if (mode === 'preview') {
    const ts = arg.split(',').map(Number);
    for (const t of ts) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(work, `ov_${t.toFixed(2)}.png`), omitBackground: true });
    }
  } else {
    const fps = 30, N = Math.round(data.total * fps);
    const out = path.join(work, 'video.mp4');
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-i', path.join(work, 'base.mov'),
      '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
      '-filter_complex', '[0:v][1:v]overlay=0:0:format=auto:shortest=1,format=yuv420p[v]', '-map', '[v]',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-r', String(fps), out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const t0 = Date.now();
    for (let i = 0; i < N; i++) {
      await page.evaluate(t => window.render(t), i / fps);
      const buf = await page.screenshot({ omitBackground: true, type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 300 === 0) console.log(`frame ${i}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    console.log('done', out);
  }
  await browser.close();
})();
