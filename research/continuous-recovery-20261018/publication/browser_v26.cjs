const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = process.cwd(), run = path.join(root, 'research/continuous-recovery-20261018');
const out = path.join(run, 'publication'), site = path.join(root, '.scratch/pages-resources-20261018-v26');
const prefix = '/WOW-Encyclopedia-Deployable-Archive', origin = 'http://127.0.0.1:29026', base = origin + prefix + '/';
const read = p => JSON.parse(fs.readFileSync(p)), sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const neighbor = read(path.join(out, 'root-neighbors5-source-acceptance.json')).accepted_images;
const news = read(path.join(out, 'root-news9-source-acceptance.json')).accepted_images;
const newsRows = new Map(read(path.join(run, 'local-audit/news-transport-unknowns-v25.json')).rows.map(item => [item.original, item]));
const provenance = read(path.join(site, 'export-provenance.json'));
const records = new Map(provenance.files.map(item => [item.route, item]));
const report = { started_utc: new Date().toISOString(), accepted: false, checks: [], errors: [], external_requests: [], screenshots: [] };
const receipt = path.join(out, 'root-v26-browser-acceptance.json');
if (fs.existsSync(receipt)) throw Error('Preserve completed browser receipt');
const started = Date.now();
function check(name, ok, data = {}) {
  report.checks.push({ name, accepted: ok, ...data });
  if (!ok) throw Error(name + JSON.stringify(data));
  if (Date.now() - started > 240000) throw Error('Browser check deadline');
}
const server = http.createServer((req, res) => {
  let rel;
  try {
    const url = new URL(req.url, origin);
    if (!url.pathname.startsWith(prefix + '/') || !['GET', 'HEAD'].includes(req.method)) throw Error();
    rel = decodeURIComponent(url.pathname.slice(prefix.length + 1));
  } catch { res.writeHead(400); return res.end(); }
  const file = path.resolve(site, rel);
  if (!file.startsWith(site + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': ({ '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.jpg': 'image/jpeg', '.gif': 'image/gif', '.png': 'image/png', '.svg': 'image/svg+xml' })[path.extname(file)] || 'application/octet-stream' });
  if (req.method === 'HEAD') return res.end();
  fs.createReadStream(file).pipe(res);
});
(async () => {
  let browser;
  try {
    await new Promise((resolve, reject) => { server.once('error', reject); server.listen(29026, '127.0.0.1', resolve); });
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1400, height: 1000 } });
    context.setDefaultTimeout(12000);
    await context.route('**/*', request => {
      if (new URL(request.request().url()).origin === origin && ['GET', 'HEAD'].includes(request.request().method())) return request.continue();
      report.external_requests.push(request.request().url()); return request.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', error => report.errors.push(String(error)));
    for (const item of [...neighbor, ...news]) {
      const route = new URL(item.original).pathname, response = await context.request.get(origin + prefix + route), bytes = await response.body();
      check('new original bytes served', response.status() === 200 && bytes.length === item.length && sha(bytes) === item.sha256, { route });
    }
    const shotPages = new Set();
    for (const item of news) {
      const route = new URL(item.original).pathname, name = newsRows.get(item.original).v25_missing_marker_refs[0].page;
      const response = await page.goto(base + name, { waitUntil: 'networkidle' });
      check('news page opens', response.status() === 200, { page: name });
      const images = page.locator('img[src$="' + route + '"]');
      check('news occurrences replaced', await images.count() === newsRows.get(item.original).v25_missing_marker_refs.length, { route, count: await images.count() });
      for (const image of await images.all()) {
        if (!await image.isVisible()) {
          const id = await image.evaluate(el => { let p = el; while (p && !/^news\d/.test(p.id || '')) p = p.parentElement; return p?.id?.slice(4); });
          check('hidden article toggle exists', !!id, { route });
          await page.evaluate(id => window.toggleEntry(id), id);
        }
        await image.scrollIntoViewIfNeeded(); await image.waitFor({ state: 'visible' });
        await page.waitForFunction(el => el.complete && el.naturalWidth > 0, await image.elementHandle());
        const dimensions = await image.evaluate(el => [el.naturalWidth, el.naturalHeight]);
        check('restored news image visible', JSON.stringify(dimensions) === JSON.stringify(item.dimensions), { route, dimensions });
      }
      if (!shotPages.has(name)) {
        shotPages.add(name); const file = 'v26-news-' + path.basename(name) + '.png';
        await page.screenshot({ path: path.join(out, file), fullPage: false }); report.screenshots.push(file);
      }
    }
    for (const group of provenance.guide_image_collections.groups) {
      for (const key of ['guide_route', 'gallery_route']) {
        const response = await page.goto(base + records.get(group[key]).output_path, { waitUntil: 'networkidle' });
        check('guide collection page opens', response.status() === 200, { route: group[key] });
        const section = page.locator('.offline-guide-image-collection');
        check('guide collection count', await section.locator('img').count() === group.images.length, { group: group.group_id, count: await section.locator('img').count() });
        const additions = neighbor.filter(item => /\/ss\d+\.jpg$/.test(new URL(item.original).pathname) && group.images.some(image => image.original === item.original));
        for (const item of additions) {
          const route = new URL(item.original).pathname, image = section.locator('img[src$="' + route + '"]').first();
          await image.scrollIntoViewIfNeeded(); await page.waitForFunction(el => el.complete && el.naturalWidth > 0, await image.elementHandle());
          const dimensions = await image.evaluate(el => [el.naturalWidth, el.naturalHeight]);
          check('new guide image visible', JSON.stringify(dimensions) === JSON.stringify(item.dimensions), { route });
          check('guide original link', (await image.evaluate(el => el.closest('a')?.getAttribute('href')))?.endsWith(route), { route });
        }
        if (additions.length && key === 'guide_route') { const file = 'v26-guide-' + group.group_id + '.png'; await page.screenshot({ path: path.join(out, file), fullPage: false }); report.screenshots.push(file); }
      }
    }
    check('four new guide originals rendered at both entrances', report.checks.filter(item => item.name === 'new guide image visible').length === 8);
    await page.goto(base + '__offline/related-images/index.html', { waitUntil: 'networkidle' });
    for (const item of neighbor) { const route = new URL(item.original).pathname; check('material catalog link', await page.locator('a[href$="' + route + '"]').count() > 0, { route }); }
    await page.goto(base + 'pvp/worldpvp/cityattacks-gallery.html', { waitUntil: 'networkidle' });
    check('City three guide previews retained', await page.locator('.offline-guide-preview-section img').count() === 3);
    const before = (await page.locator('#pageNum').innerText()).trim(); await page.locator('a[href="javascript:galleryNext();"]').first().click();
    await page.waitForFunction(value => document.getElementById('pageNum').innerText.trim() !== value, before); check('gallery pagination retained', true);
    const response = await page.goto(base + 'info/encyclopedia/index.xml.html', { waitUntil: 'networkidle' });
    check('encyclopedia opens', response.status() === 200 && (await page.content()).includes('Warcraft Encyclopedia'));
    check('no external requests', report.external_requests.length === 0); check('no page errors', report.errors.length === 0);
    report.accepted = true;
  } catch (error) { report.errors.push(error.stack || String(error)); }
  finally {
    if (browser) await browser.close(); await new Promise(resolve => server.close(resolve));
    report.finished_utc = new Date().toISOString(); fs.writeFileSync(receipt, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ accepted: report.accepted, checks: report.checks.length, errors: report.errors, external_requests: report.external_requests.length }));
    if (!report.accepted) process.exitCode = 1;
  }
})();
