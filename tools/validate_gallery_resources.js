#!/usr/bin/env node
/* Check restored screenshot resources in the unmodified local export. */
const fs = require('fs');
const http = require('http');
const path = require('path');
const assert = require('assert/strict');

function option(name, fallback) {
  const i = process.argv.indexOf(name);
  return i < 0 ? fallback : process.argv[i + 1];
}
const site = path.resolve(option('--site', '.scratch/pages-resources-20261014'));
const output = path.resolve(option('--output', 'research/resource-integration-20261014/browser-validation.json'));
const { chromium } = require(option('--playwright-module', 'playwright'));
const browserPath = option('--browser', undefined);
const prefix = JSON.parse(fs.readFileSync(path.join(site, 'export-provenance.json'), 'utf8')).base_path;
const report = { checkedAt: new Date().toISOString(), site, galleries: [], imageEntities: [], restoredPairs: [], errors: [], externalRequests: [], posts: [] };
const types = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.gif': 'image/gif', '.png': 'image/png', '.jpg': 'image/jpeg' };

async function main() {
  const server = http.createServer((req, res) => {
    try {
      const url = new URL(req.url, 'http://localhost');
      assert(url.pathname.startsWith(prefix));
      const target = path.resolve(site, decodeURIComponent(url.pathname.slice(prefix.length)) || 'index.html');
      assert(target.startsWith(site + path.sep));
      const body = fs.readFileSync(target);
      res.writeHead(200, { 'Content-Type': types[path.extname(target)] || 'application/octet-stream' });
      res.end(body);
    } catch (_) { res.writeHead(404); res.end('Not found'); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch({ headless: true, ...(browserPath ? { executablePath: browserPath } : {}) });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  await context.route('**/*', route => {
    const req = route.request();
    if (req.method() !== 'GET') { report.posts.push(req.method()); return route.abort(); }
    const url = new URL(req.url());
    if (url.origin !== origin || !url.pathname.startsWith(prefix)) {
      report.externalRequests.push(req.url());
      return route.abort();
    }
    return route.continue();
  });
  const page = await context.newPage();
  try {
    for (const relative of ['info/dungeons/karazhan-gallery.html', 'info/dungeons/black-temple-gallery.html', 'info/professions/fishing-gallery.html']) {
      await page.goto(origin + prefix + relative, { waitUntil: 'load' });
      const state = await page.evaluate(() => ({ shots: shotList.length, first: shotList[0], last: shotList[shotList.length - 1], page: document.getElementById('pageNum').textContent, missing: window.__WOWPages.mapImage('/info/dungeons/images/karazhan/ss999999.jpg') }));
      assert(state.shots > 0);
      assert(state.first.startsWith(prefix) && state.first.endsWith('.jpg'));
      assert(!state.first.includes('__offline/missing'));
      assert(state.missing.includes('__offline/missing-image.svg'));
      await page.evaluate(() => galleryNext());
      const next = await page.locator('#pageNum').textContent();
      assert.notEqual(next, state.page);
      report.galleries.push({ relative, ...state, nextPage: next, passed: true });
    }

    const provenance = JSON.parse(fs.readFileSync(path.join(site, 'export-provenance.json'), 'utf8'));
    const overlays = provenance.files.filter(x => x.role === 'image_overlay');
    for (const entity of overlays) {
      const url = origin + entity.static_url;
      const loaded = await page.evaluate(url => new Promise(resolve => {
        const img = new Image(); img.onload = () => resolve({ width: img.naturalWidth, height: img.naturalHeight, src: img.src });
        img.onerror = () => resolve({ error: true, src: img.src }); img.src = url;
      }), url);
      assert(!loaded.error && loaded.width > 0 && loaded.height > 0, entity.route);
      assert.equal(loaded.src, url, entity.route + ' must use the restored entity');
      report.imageEntities.push({ route: entity.route, ...loaded, passed: true });
    }

    const restored = overlays.filter(x => /^\/info\/dungeons\/images\/karazhan\/ss\d+\.jpg$/.test(x.route));
    for (const entity of restored) {
      const thumb = entity.route.replace(/\.jpg$/, '-thumb.jpg');
      if (!overlays.some(x => x.route === thumb)) continue;
      await page.goto(origin + prefix + 'info/dungeons/karazhan-gallery.html', { waitUntil: 'load' });
      const state = await page.evaluate(({ full, thumb }) => {
        const index = shotList.findIndex(x => x.endsWith(full));
        if (index < 0) return { error: 'shot absent' };
        currentPage = Math.floor(index / shotsPerPage); printPages();
        const image = Array.from(document.querySelectorAll('#galleryPictures img')).find(x => new URL(x.src).pathname.endsWith(thumb));
        omegaLightBox(index);
        return { index, thumbnail: image && image.src, full: window.__WOWPages.mapImage(shotList[index]) };
      }, { full: entity.route, thumb });
      assert(!state.error && state.thumbnail && state.full.endsWith(entity.route));
      await page.waitForFunction(() => window.screenImage && screenImage.complete && screenImage.naturalWidth > 0);
      const dimensions = await page.evaluate(() => ({ width: screenImage.naturalWidth, height: screenImage.naturalHeight, thumbnailLoaded: Array.from(document.querySelectorAll('#galleryPictures img')).some(x => x.complete && x.naturalWidth > 100) }));
      assert(dimensions.width > 100 && dimensions.height > 100 && dimensions.thumbnailLoaded);
      report.restoredPairs.push({ full: entity.route, thumb, ...state, ...dimensions, passed: true });
      if (report.restoredPairs.length === 1) await page.screenshot({ path: output.replace(/\.json$/, '.png'), fullPage: false });
    }
    assert.equal(report.externalRequests.length, 0);
    assert.equal(report.posts.length, 0);
  } catch (error) {
    report.errors.push(String(error));
  } finally {
    await context.close(); await browser.close(); await new Promise(resolve => server.close(resolve));
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  }
  console.log(JSON.stringify({ galleries: report.galleries.length, imageEntities: report.imageEntities.length, restoredPairs: report.restoredPairs.length, errors: report.errors, externalRequests: report.externalRequests.length, output }));
  if (report.errors.length) process.exitCode = 1;
}
main().catch(error => { console.error(error); process.exitCode = 1; });
