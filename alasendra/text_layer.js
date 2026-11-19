// Renders one transparent 1080x1920 PNG per lyric state: title, current line (filled words in
// yellow-orange, rest white) and the next line in grey. usage: node text_layer.js states.json fontsdir outdir
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [, , sf, fontsDir, outDir] = process.argv;
const D = JSON.parse(fs.readFileSync(sf, 'utf8'));
const te = D.lang === 'te';
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Rama;src:url(file://${fontsDir}/RamaCap.ttf)}
@font-face{font-family:Pop;src:url(file://${fontsDir}/PopB.ttf)}
html,body{margin:0;width:1080px;height:1920px;background:transparent;overflow:hidden}
body{font-family:${te ? 'Rama' : 'Pop'};color:#fff;text-align:center}
#title{position:absolute;top:300px;left:0;right:0;font-size:${te ? 70 : 60}px;
  text-shadow:0 0 18px rgba(255,170,40,.75),0 3px 6px #000}
#cur{position:absolute;top:1170px;left:50px;right:50px;font-size:${te ? 84 : 68}px;line-height:1.35;
  text-shadow:0 4px 10px rgba(0,0,0,.9),0 0 3px #000}
#cur .f{color:#ffc22e;text-shadow:0 0 16px rgba(255,140,30,.8),0 4px 10px rgba(0,0,0,.9),0 0 3px #000}
#next{position:absolute;top:1480px;left:80px;right:80px;font-size:${te ? 56 : 46}px;line-height:1.3;color:rgba(235,235,235,.72);
  text-shadow:0 3px 8px rgba(0,0,0,.9)}
</style></head><body><div id="title"></div><div id="cur"></div><div id="next"></div></body></html>`;
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const hf = path.join(outDir, 'layer.html'); fs.writeFileSync(hf, html);   // file:// page so the local fonts load
  await p.goto('file://' + path.resolve(hf), { waitUntil: 'load' });
  await p.evaluate(t => { document.getElementById('title').textContent = t; return document.fonts.ready; }, D.title);
  await p.evaluate(() => document.fonts.ready);
  const ok = await p.evaluate(() => [document.fonts.check('80px Rama'), document.fonts.check('80px Pop')]);
  if (!ok[te ? 0 : 1]) throw new Error('font not loaded');
  for (let i = 0; i < D.states.length; i++) {
    await p.evaluate(s => {
      const esc = x => x.replace(/&/g, '&amp;').replace(/</g, '&lt;');
      document.getElementById('cur').innerHTML = s.words.map((w, j) => `<span class="${j < s.fill ? 'f' : ''}">${esc(w)}</span>`).join(' ');
      document.getElementById('next').textContent = s.next;
    }, D.states[i]);
    await p.screenshot({ path: path.join(outDir, `s${String(i).padStart(4, '0')}.png`), omitBackground: true });
  }
  await b.close(); console.log(D.lang, D.states.length, 'states');
})();
