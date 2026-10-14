#!/usr/bin/env node
/* Check the generated image collection using local files and fresh Chrome. */
const fs = require('fs');
const path = require('path');
const http = require('http');
const assert = require('assert/strict');
const option = (name, fallback) => { const i = process.argv.indexOf(name); return i < 0 ? fallback : process.argv[i + 1]; };
const site = path.resolve(option('--site', '.scratch/pages-resources-20261014-next'));
const output = path.resolve(option('--output', 'research/related-sites-20261014/integration/catalog-browser-validation.json'));
const { chromium } = require(option('--playwright-module', 'playwright'));
const provenance = JSON.parse(fs.readFileSync(path.join(site, 'export-provenance.json'), 'utf8'));
const prefix = provenance.base_path;
const images = provenance.files.filter(x => x.role === 'image_overlay' && x.supplement_strategy === 'explicit_supplement_image_overlay');
const report = { checkedAt: new Date().toISOString(), cards: 0, loaded: [], externalRequests: [], failures: [] };

async function main() {
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const types = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.json': 'application/json', '.jpg': 'image/jpeg', '.gif': 'image/gif', '.svg': 'image/svg+xml' };
  const server = http.createServer((req, res) => {
    try {
      const url = new URL(req.url, 'http://localhost');
      assert(url.pathname.startsWith(prefix));
      const file = path.resolve(site, decodeURIComponent(url.pathname.slice(prefix.length)));
      assert(file.startsWith(site + path.sep));
      const data = fs.readFileSync(file);
      res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
      res.end(data);
    } catch (_) { res.writeHead(404); res.end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch({ headless: true, executablePath: option('--browser', undefined) });
  const context = await browser.newContext({ viewport: { width: 1400, height: 1000 } });
  await context.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.origin !== origin || !url.pathname.startsWith(prefix) || route.request().method() !== 'GET') {
      report.externalRequests.push(route.request().url()); return route.abort();
    }
    return route.continue();
  });
  const page = await context.newPage();
  try {
    await page.goto(origin + prefix + '__offline/related-images/index.html', { waitUntil: 'load' });
    report.cards = await page.locator('article.related-image-card').count();
    assert.equal(report.cards, images.length);
    report.loaded = await page.locator('article.related-image-card img').evaluateAll(async elements => {
      return await Promise.all(elements.map(async img => {
        img.loading = 'eager'; await img.decode();
        return { src: img.src, width: img.naturalWidth, height: img.naturalHeight };
      }));
    });
    for (const img of report.loaded) {
      assert(img.width > 0 && img.height > 0);
      assert(images.some(x => origin + x.static_url === img.src));
    }
    const times = await page.locator('article time').evaluateAll(elements => elements.map(x => x.dateTime));
    assert.equal(times.length, report.cards);
    assert(times.every(x => !Number.isNaN(Date.parse(x))));
    assert.equal(await page.locator('form,input,select,textarea,button').count(), 0);
    assert.equal(report.externalRequests.length, 0);
    await page.screenshot({ path: output.replace(/\.json$/, '.png'), fullPage: false });
  } catch (error) { report.failures.push(String(error)); }
  finally {
    await context.close(); await browser.close(); await new Promise(resolve => server.close(resolve));
    report.passed = !report.failures.length;
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  }
  console.log(JSON.stringify({ passed: report.passed, cards: report.cards, loaded: report.loaded.length, failures: report.failures }));
  if (!report.passed) process.exitCode = 1;
}
main().catch(error => { console.error(error); process.exitCode = 1; });
