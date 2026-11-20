// usage: node shot_bg.js studio_bg.html out.png
const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(process.argv[2])); await p.evaluate(() => window.__ready); await p.waitForTimeout(300);
  await p.screenshot({ path: process.argv[3], omitBackground: true }); await b.close(); })();
