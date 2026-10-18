const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = process.cwd(), run = path.join(root, 'research/continuous-recovery-20261018');
const out = path.join(run, 'publication'), site = path.join(root, '.scratch/pages-resources-20261018-v27');
const prefix = '/WOW-Encyclopedia-Deployable-Archive', origin = 'http://127.0.0.1:29027', base = origin + prefix + '/';
const read = p => JSON.parse(fs.readFileSync(p)), sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const expected = read(path.join(out, 'v27-export-expectations.json'));
const entries = ['v27-primary-source-map.json', 'v27-blizzard-supplement-source-map.json'].flatMap(name => read(path.join(run, 'integration/v27', name)).items);
const byOriginal = new Map(entries.map(item => [item.original, item]));
const report = { started_utc: new Date().toISOString(), accepted: false, checks: [], errors: [], external_requests: [], screenshots: [] };
const receipt = path.join(out, 'root-v27-browser-retry1-acceptance.json');
report.prior_attempt = { path: 'root-v27-browser-acceptance.json', sha256: sha(fs.readFileSync(path.join(out, 'root-v27-browser-acceptance.json'))), finding: 'The upgrade GIF is a two-state CSS sprite, not two img elements. Export bytes remain unchanged.' };
if (fs.existsSync(receipt)) throw Error('Preserve completed browser receipt');
const started = Date.now();
function check(name, ok, data = {}) {
  report.checks.push({ name, accepted: ok, ...data });
  if (!ok) throw Error(name + JSON.stringify(data));
  if (Date.now() - started > 240000) throw Error('Browser check deadline');
}
function outputPath(item) {
  const url = new URL(item.original);
  return (url.hostname === 'www.blizzard.com' ? '_origins/www.blizzard.com' + url.pathname : url.pathname.slice(1));
}
const server = http.createServer((req, res) => {
  let relative;
  try {
    const url = new URL(req.url, origin);
    if (!url.pathname.startsWith(prefix + '/') || !['GET', 'HEAD'].includes(req.method)) throw Error();
    relative = decodeURIComponent(url.pathname.slice(prefix.length + 1));
  } catch { res.writeHead(400); return res.end(); }
  const file = path.resolve(site, relative);
  if (!file.startsWith(site + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': ({ '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.jpg': 'image/jpeg', '.gif': 'image/gif', '.png': 'image/png', '.svg': 'image/svg+xml' })[path.extname(file)] || 'application/octet-stream' });
  if (req.method === 'HEAD') return res.end();
  fs.createReadStream(file).pipe(res);
});
(async () => {
  let browser;
  try {
    await new Promise((resolve, reject) => { server.once('error', reject); server.listen(29027, '127.0.0.1', resolve); });
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1400, height: 1000 } });
    context.setDefaultTimeout(12000);
    await context.route('**/*', request => {
      if (new URL(request.request().url()).origin === origin && ['GET', 'HEAD'].includes(request.request().method())) return request.continue();
      report.external_requests.push(request.request().url()); return request.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', error => report.errors.push(String(error)));
    for (const item of entries) {
      const route = outputPath(item), response = await context.request.get(base + route), bytes = await response.body();
      check('new original bytes served', response.status() === 200 && bytes.length === item.length && sha(bytes) === item.sha256 && response.headers()['content-type'] === item.mime, { route });
    }
    const pages = new Map();
    for (const reference of expected.new_static_marker_references) {
      if (!pages.has(reference.page)) pages.set(reference.page, []);
      pages.get(reference.page).push(reference);
    }
    for (const [name, references] of pages) {
      const response = await page.goto(base + name, { waitUntil: 'networkidle' });
      check('affected page opens', response.status() === 200, { page: name });
      const grouped = new Map();
      for (const reference of references) {
        const key = reference.original;
        grouped.set(key, (grouped.get(key) || 0) + 1);
      }
      for (const [original, count] of grouped) {
        const item = byOriginal.get(original), route = outputPath(item);
        if (route === 'news/images/07-02/upgradenow.gif') {
          check('CSS sprite has two source references', count === 2);
          const sprite = page.locator('.upgradenow a');
          check('historical sprite element exists', await sprite.count() === 1);
          if (!await sprite.isVisible()) {
            const id = await sprite.evaluate(el => { let p = el; while (p && !/^news\d/.test(p.id || '')) p = p.parentElement; return p?.id?.slice(4); });
            check('sprite article toggle exists', !!id);
            await page.evaluate(id => window.toggleEntry(id), id);
          }
          await sprite.scrollIntoViewIfNeeded();
          await page.mouse.move(0, 0);
          const normal = await sprite.evaluate(el => ({background: getComputedStyle(el).backgroundImage, position: getComputedStyle(el).backgroundPositionY, width: el.getBoundingClientRect().width, height: el.getBoundingClientRect().height, href: el.getAttribute('href')}));
          const dimensions = await sprite.evaluate(async el => { const image = new Image(); image.src = getComputedStyle(el).backgroundImage.slice(5, -2); await image.decode(); return [image.naturalWidth, image.naturalHeight]; });
          check('normal CSS sprite visible', await sprite.isVisible() && normal.background.includes('/' + route) && normal.position === '0px' && normal.width === 377 && normal.height === 74 && JSON.stringify(dimensions) === JSON.stringify(item.dimensions), {page: name, route, dimensions});
          await sprite.hover();
          const hover = await sprite.evaluate(el => ({background: getComputedStyle(el).backgroundImage, position: getComputedStyle(el).backgroundPositionY}));
          check('hover CSS sprite visible', hover.background.includes('/' + route) && hover.position === '-74px', {page: name, route});
          const target = new URL(normal.href, page.url());
          check('historical upgrade remains local missing exhibit', target.origin === origin && target.pathname === prefix + '/__offline/missing.html');
          continue;
        }
        const images = page.locator('img[src$="/' + route + '"]');
        check('page references replaced', await images.count() === count, { page: name, route, count: await images.count(), expected: count });
        for (const image of await images.all()) {
          if (!await image.isVisible()) {
            const id = await image.evaluate(el => { let p = el; while (p && !/^news\d/.test(p.id || '')) p = p.parentElement; return p?.id?.slice(4); });
            check('historical article toggle exists', !!id, { route });
            await page.evaluate(id => window.toggleEntry(id), id);
          }
          await image.scrollIntoViewIfNeeded();
          await page.waitForFunction(el => el.complete && el.naturalWidth > 0, await image.elementHandle());
          const dimensions = await image.evaluate(el => [el.naturalWidth, el.naturalHeight]);
          check('restored image visible', await image.isVisible() && JSON.stringify(dimensions) === JSON.stringify(item.dimensions), { page: name, route, dimensions });
        }
      }
      const file = 'v27-news-' + path.basename(name) + '.png';
      await page.screenshot({ path: path.join(out, file), fullPage: false }); report.screenshots.push(file);
    }
    check('all31actual references visible', report.checks.filter(item => ['restored image visible', 'normal CSS sprite visible', 'hover CSS sprite visible'].includes(item.name)).length === 31);
    await page.goto(base + '__offline/related-images/index.html', { waitUntil: 'networkidle' });
    for (const item of entries.filter(item => new URL(item.original).hostname === 'www.blizzard.com')) {
      const route = outputPath(item);
      check('Blizzard source has distinct catalog route', await page.locator('a[href$="/' + route + '"]').count() > 0, { route });
    }
    const provenance = read(path.join(site, 'export-provenance.json'));
    check('guide collection39retained', provenance.guide_image_collections.image_count === 39);
    check('no external requests', report.external_requests.length === 0);
    check('no page errors', report.errors.length === 0);
    report.export_provenance_sha256 = sha(fs.readFileSync(path.join(site, 'export-provenance.json')));
    report.accepted = true;
  } catch (error) { report.errors.push(error.stack || String(error)); }
  finally {
    if (browser) await browser.close(); await new Promise(resolve => server.close(resolve));
    report.finished_utc = new Date().toISOString(); fs.writeFileSync(receipt, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ accepted: report.accepted, checks: report.checks.length, errors: report.errors, external_requests: report.external_requests.length }));
    if (!report.accepted) process.exitCode = 1;
  }
})();
