const puppeteer = require('puppeteer');
const path = require('path');

const filePath = 'file://' + path.resolve(__dirname, 'index.html');

const viewports = [
  { name: 'desktop',  width: 1440, height: 900  },
  { name: 'tablet',   width: 768,  height: 1024 },
  { name: 'mobile',   width: 390,  height: 844  },
];

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });

  for (const vp of viewports) {
    const page = await browser.newPage();
    await page.setViewport({ width: vp.width, height: vp.height, deviceScaleFactor: 2 });
    await page.goto(filePath, { waitUntil: 'networkidle0' });

    // Let fonts/animations settle
    await new Promise(r => setTimeout(r, 800));

    const outFile = path.join(__dirname, `screenshot-${vp.name}.png`);
    await page.screenshot({ path: outFile, fullPage: true });
    console.log(`✓ ${vp.name} (${vp.width}×${vp.height}) → ${outFile}`);
    await page.close();
  }

  await browser.close();
  console.log('\nAll screenshots saved.');
})();
