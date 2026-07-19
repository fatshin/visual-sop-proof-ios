import { mkdir } from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const [url, outputDirectory] = process.argv.slice(2);

if (!url || !outputDirectory) {
  console.error("Usage: capture_web_demo.mjs <url> <output-directory>");
  process.exit(1);
}

await mkdir(outputDirectory, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  executablePath:
    process.env.PLAYWRIGHT_CHROME_PATH ??
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const page = await browser.newPage({
  viewport: { width: 1280, height: 720 },
  deviceScaleFactor: 1,
});

try {
  await page.goto(url, { waitUntil: "networkidle" });
  await page.locator("#top").scrollIntoViewIfNeeded();
  await page.screenshot({
    path: path.join(outputDirectory, "01-overview.png"),
  });

  await page.locator("#demo").scrollIntoViewIfNeeded();
  await page.locator("button.run-button").click();
  await page.locator(".result-panel.is-visible").waitFor();
  await page.waitForTimeout(350);
  await page.screenshot({
    path: path.join(outputDirectory, "02-result.png"),
  });

  await page.locator("#method").scrollIntoViewIfNeeded();
  await page.waitForTimeout(200);
  await page.screenshot({
    path: path.join(outputDirectory, "03-method.png"),
  });
} finally {
  await browser.close();
}
