// usage: node render.js data.json preview t1,t2,... <outdir>
//        node render.js data.json full <song_audio> <out.mp4>
// data.json: {total, font, title, start (seconds into the song), lines:[{a,b,t}], scenes:[{a,b,key}]}
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'), path = require('path');
const [, , dataFile, mode, a1, a2] = process.argv;
const D = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
if (D.scenesFile) D.extraSrc = fs.readFileSync(path.resolve(path.dirname(dataFile), D.scenesFile), 'utf8'); const FPS = 30;
(async () => {
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.addInitScript(d => { window.__DATA__ = d; }, D);
  await page.goto('file://' + path.resolve(__dirname, 'chalk.html'));
  await page.evaluate(() => window.__ready);
  if (mode === 'preview') {
    for (const t of a1.split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(a2, `p_${t.toFixed(2)}.png`) });
    }
  } else {
    const silent = a2.replace(/\.mp4$/, '_silent.mp4');
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', String(FPS), silent], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = Math.round(D.total * FPS), t0 = Date.now();
    for (let i = 0; i < N; i++) {
      await page.evaluate(t => window.render(t), i / FPS);
      const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 300 === 0) console.log(`frame ${i}/${N} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    // song cut [start, start+total] with fade in/out
    const af = `afade=t=in:st=0:d=${D.fadeIn ?? 0.4},afade=t=out:st=${(D.total - 0.6).toFixed(2)}:d=0.6,loudnorm=I=-14:TP=-1.5:LRA=11`;
    // optional cuts: D.segments = [[songStart, songEnd], ...] joined with tiny fades (pauses removed)
    const segs = D.segments || [[D.start, D.start + D.total]];
    const fc = segs.map(([a, b], i) => `[1:a]atrim=${a}:${b},asetpts=PTS-STARTPTS${i ? ',afade=t=in:d=0.06' : ''}${i < segs.length - 1 ? `,afade=t=out:st=${(b - a - 0.06).toFixed(3)}:d=0.06` : ''}[s${i}]`).join(';')
      + ';' + segs.map((_, i) => `[s${i}]`).join('') + `concat=n=${segs.length}:v=0:a=1,${af}[aout]`;
    await new Promise(r => spawn('ffmpeg', ['-v', 'error', '-y', '-i', silent, '-i', a1,
      '-filter_complex', fc, '-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', a2], { stdio: 'inherit' }).on('close', r));
    fs.unlinkSync(silent);
    console.log('done', a2);
  }
  await browser.close();
})();
