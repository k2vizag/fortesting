// node title.js <outdir> <seconds>  -> PNG frames of the title at 30 fps
const { chromium } = require('playwright'); const path = require('path');
const [, , out, secs] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(__dirname, 'title.html')); await p.evaluate(() => window.__ready);
  const N = Math.round(+secs * 30);
  for (let i = 0; i < N; i++) { await p.evaluate(t => window.render(t), i / 30);
    await p.screenshot({ path: `${out}/t_${String(i).padStart(4, '0')}.png`, omitBackground: true }); }
  await b.close(); console.log('frames', N);
})();
