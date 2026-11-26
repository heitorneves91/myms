// Optional SVG -> PNG preview renderer. Install playwright-core outside the repo:
// npm install --prefix /tmp/myms-electrical-tools playwright-core@1.56.1 --no-audit --no-fund
// NODE_PATH=/tmp/myms-electrical-tools/node_modules node scripts/render_electrical_schematic.cjs
const {chromium} = require('playwright-core');
const path = require('path');
const root = path.resolve(__dirname, '..');
(async () => {
  const browser = await chromium.launch({executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
    headless: true, args: ['--no-sandbox']});
  try {
    for (const [name, height] of [['01-power', 1420], ['02-control-and-sensors', 1380]]) {
      const page = await browser.newPage({viewport: {width: 1800, height}, deviceScaleFactor: 1});
      await page.goto('file://' + path.join(root, 'docs/electrical', name + '.svg'));
      const outside = await page.evaluate(() => [...document.querySelectorAll('text')].filter(node => {
        const box = node.getBBox();
        return box.x < 0 || box.y < 0 || box.x + box.width > 1800 || box.y + box.height > innerHeight;
      }).map(node => node.textContent));
      if (outside.length) throw Error(name + ': text outside drawing: ' + outside.join(', '));
      await page.screenshot({path: path.join(root, 'docs/electrical', name + '.png')});
      await page.close();
    }
    console.log('Two schematic previews rendered; text bounds passed');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
