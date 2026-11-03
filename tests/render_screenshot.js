// Regenerates the screenshot fixture for case 03 from the case 02 page.
// Needs Node and Playwright with Chromium:
//   node tests/render_screenshot.js
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const cases = path.join(__dirname, "cases");
  const page_html = path.join(cases, "02-en-dead-controls-live", "page.html");
  const out = path.join(cases, "03-en-dead-controls-screenshot", "screenshot.png");
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
  await page.goto("file://" + page_html);
  // Freeze the pulsing dot so the image is the same on every run.
  await page.addStyleTag({ content: ".dot { animation: none !important; }" });
  await page.screenshot({ path: out, fullPage: true });
  await browser.close();
  console.log("wrote " + out);
})();
