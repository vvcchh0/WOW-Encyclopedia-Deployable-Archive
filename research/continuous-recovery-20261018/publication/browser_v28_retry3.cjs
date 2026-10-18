const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = process.cwd(), run = path.join(root, 'research/continuous-recovery-20261018');
const out = path.join(run, 'publication'), site = path.join(root, '.scratch/pages-resources-20261018-v28');
const prefix = '/WOW-Encyclopedia-Deployable-Archive', origin = 'http://127.0.0.1:29028', base = origin + prefix + '/';
const read = p => JSON.parse(fs.readFileSync(p)), sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const entries = ['v27-primary-source-map.json', 'v27-blizzard-supplement-source-map.json'].flatMap(name => read(path.join(run, 'integration/v27', name)).items)
  .concat(read(path.join(run, 'integration/v28/v28-primary-source-map.json')).items);
const references = ['v27', 'v28'].flatMap(v => read(path.join(out, v + '-export-expectations.json')).new_static_marker_references);
const byOriginal = new Map(entries.map(item => [item.original, item]));
const report = { started_utc: new Date().toISOString(), accepted: false, checks: [], errors: [], external_requests: [], screenshots: [] };
const receipt = path.join(out, 'root-v28-browser-retry3-acceptance.json');
if (fs.existsSync(receipt)) throw Error('Preserve completed browser receipt');
report.prior_attempts = ['root-v28-browser-acceptance.json','root-v28-browser-retry1-acceptance.json','root-v28-browser-retry2-acceptance.json'].map(name=>({path:name,sha256:sha(fs.readFileSync(path.join(out,name)))}));
report.test_correction = 'Four inline CSS backgrounds need background-image checks; real news-toggle clicks supply the legacy alt argument. A direct one-argument test call had produced news-collapseundefined. The actual legacy javascript-href click changes class asynchronously; wait for hidden/visible states. A focused four-click diagnostic confirmed all transitions. Site output is unchanged.';
const started = Date.now();
function check(name, ok, data = {}) {
  report.checks.push({ name, accepted: ok, ...data });
  if (!ok) throw Error(name + JSON.stringify(data));
  if (Date.now() - started > 300000) throw Error('Browser check deadline');
}
function outputPath(item) {
  const url = new URL(item.original);
  return url.hostname === 'www.blizzard.com' ? '_origins/www.blizzard.com' + url.pathname : url.pathname.slice(1);
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
    await new Promise((resolve, reject) => { server.once('error', reject); server.listen(29028, '127.0.0.1', resolve); });
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1400, height: 1000 } });
    context.setDefaultTimeout(12000);
    await context.route('**/*', request => {
      if (new URL(request.request().url()).origin === origin && ['GET', 'HEAD'].includes(request.request().method())) return request.continue();
      report.external_requests.push(request.request().url()); return request.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', error => report.errors.push(String(error)));
    check('exact67new original resources since live v26', entries.length === 67 && byOriginal.size === 67);
    for (const item of entries) {
      const route = outputPath(item), response = await context.request.get(base + route), bytes = await response.body();
      check('new original bytes served', response.status() === 200 && bytes.length === item.length && sha(bytes) === item.sha256 && response.headers()['content-type'] === item.mime, { route });
    }
    const pages = new Map();
    for (const reference of references) {
      if (!pages.has(reference.page)) pages.set(reference.page, []);
      pages.get(reference.page).push(reference);
    }
    for (const [name, refs] of pages) {
      const response = await page.goto(base + name, { waitUntil: 'networkidle' });
      check('affected page opens', response.status() === 200, { page: name });
      const grouped = new Map();
      for (const reference of refs) grouped.set(reference.original, (grouped.get(reference.original) || 0) + 1);
      for (const [original, oldCount] of grouped) {
        const item = byOriginal.get(original), route = outputPath(item);
        const count = route === 'news/images/07-02/upgradenow.gif' ? 1 : oldCount;
        if (/^news\/images\/07-05\/bullet-(?:armor|magnify|pin|upgrade)\.gif$/.test(route)) {
          const background = page.locator('ul.armoryitemdb > li[style*="/' + route + '"]');
          check('exact inline CSS background reference', await background.count() === count, {page:name, route, count:await background.count(), expected:count});
          if (!await background.isVisible()) {
            const id = await background.evaluate(el => { let p=el; while(p && !/^news\d/.test(p.id||''))p=p.parentElement;return p?.id?.slice(4); });
            check('CSS article toggle exists', !!id); await page.evaluate(id => window.toggleEntry(id,''), id);
          }
          await background.scrollIntoViewIfNeeded();
          const actual = await background.evaluate(async el => { const css=getComputedStyle(el), match=css.backgroundImage.match(/url\(["']?(.*?)["']?\)/); const image=new Image();image.src=match[1];await image.decode();return {source:image.src,dimensions:[image.naturalWidth,image.naturalHeight],repeat:css.backgroundRepeat,width:el.getBoundingClientRect().width,height:el.getBoundingClientRect().height}; });
          check('restored CSS background visible', await background.isVisible() && actual.source.endsWith('/'+route) && JSON.stringify(actual.dimensions)===JSON.stringify(item.dimensions) && actual.repeat==='no-repeat' && actual.width>=26 && actual.height>=26, {page:name,route,actual});
          continue;
        }
        const images = page.locator('img[src$="/' + route + '"]');
        check('page references replaced', await images.count() === count, { page: name, route, count: await images.count(), expected: count });
        for (const image of await images.all()) {
          if (!await image.isVisible()) {
            const id = await image.evaluate(el => { let p = el; while (p && !/^news\d/.test(p.id || '')) p = p.parentElement; return p?.id?.slice(4); });
            check('historical article toggle exists', !!id, { route });
            await page.evaluate(id => window.toggleEntry(id,''), id);
          }
          await image.scrollIntoViewIfNeeded();
          await page.waitForFunction(el => el.complete && el.naturalWidth > 0, await image.elementHandle());
          const dimensions = await image.evaluate(el => [el.naturalWidth, el.naturalHeight]);
          check('restored image visible', await image.isVisible() && JSON.stringify(dimensions) === JSON.stringify(item.dimensions), { page: name, route, dimensions });
        }
      }
    }
    check('all70actual displayed references visible', report.checks.filter(item => ['restored image visible','restored CSS background visible'].includes(item.name)).length === 70);
    await page.goto(base + 'news/rss-02-2007.xml.html', { waitUntil: 'networkidle' });
    const entry = page.locator('[id="news2-1-07-1212"]');
    const figure = entry.locator('figure[data-historical-exhibit="news-upgrade-artwork"]');
    if (!await figure.isVisible()) await entry.locator('.news-toggle a').click();
    await figure.scrollIntoViewIfNeeded();
    const text = await entry.innerText();
    check('news has historical wording', text.includes('2007 Historical Exhibit') && text.includes('Historical steps described in the February 2007 notice') && text.includes('static exhibit artwork'));
    check('news has no operative credential or payment prompt', !/Enter your credit card information|All you need to do|Login to Account Management|Click The Burning Crusade "Download Now"|Follow the link to download The Burning Crusade game client/i.test(text));
    check('artwork has no business action', await figure.locator('a,form,input,button,[onclick],[onmouseover],[onmouseout]').count() === 0);
    check('old hover business target removed', await entry.locator('.upgradenow').count() === 0);
    check('account navigation historical labels retained', (await page.getByText('Historical: Create Account', {exact:true}).count()) > 0 && (await page.getByText('Historical: Manage Account', {exact:true}).count()) > 0 && (await page.getByText('Historical: Retrieve Password', {exact:true}).count()) > 0);
    const image = figure.locator('img');
    const box = await image.boundingBox();
    check('static artwork dimensions preserved', !!box && Math.abs(box.width - 377) < 1 && Math.abs(box.height - 148) < 1);
    const png = 'v28-historical-news-upgrade-retry3.png';
    await page.screenshot({ path: path.join(out, png), fullPage: false }); report.screenshots.push(png);
    await entry.locator('.news-toggle a').click();
    await figure.waitFor({state:'hidden'});
    check('news entry collapse preserved', (await entry.getAttribute('class')) === 'news-collapse' && !await figure.isVisible());
    await entry.locator('.news-toggle a').click();
    await figure.waitFor({state:'visible'});
    check('news entry reopens', (await entry.getAttribute('class')) === 'news-expand' && await figure.isVisible());
    await page.goto(base + 'news/rss-05-2007.xml.html', { waitUntil: 'networkidle' });
    const armory = page.locator('img[src$="/news/images/07-05/itemdbss.jpg"]');
    if (!await armory.isVisible()) {
      const id = await armory.evaluate(el => { let p = el; while (p && !/^news\d/.test(p.id || '')) p = p.parentElement; return p?.id?.slice(4); });
      check('Armory news toggle found', !!id); await page.evaluate(id => window.toggleEntry(id,''), id);
    }
    await armory.scrollIntoViewIfNeeded();
    const newsPng = 'v28-armory-news-retry3.png';
    await page.screenshot({ path: path.join(out, newsPng), fullPage: false }); report.screenshots.push(newsPng);
    await page.goto(base + '__offline/related-images/index.html', { waitUntil: 'networkidle' });
    for (const item of entries.filter(item => new URL(item.original).hostname === 'www.blizzard.com')) {
      check('Blizzard source retains distinct catalog route', await page.locator('a[href$="/' + outputPath(item) + '"]').count() > 0);
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
