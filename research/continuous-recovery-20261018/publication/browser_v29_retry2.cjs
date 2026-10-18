const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = process.cwd(), run = path.join(root, 'research/continuous-recovery-20261018');
const out = path.join(run, 'publication'), site = path.join(root, '.scratch/pages-resources-20261018-v29');
const prefix = '/WOW-Encyclopedia-Deployable-Archive', origin = 'http://127.0.0.1:29029', base = origin + prefix + '/';
const read = p => JSON.parse(fs.readFileSync(p)), sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const entries = read(path.join(run, 'integration/v29/v29-primary-source-map.json')).items;
const references = read(path.join(out, 'v29-export-expectations.json')).new_static_marker_references;
const byOriginal = new Map(entries.map(item => [item.original, item]));
const report = { started_utc: new Date().toISOString(), accepted: false, checks: [], errors: [], external_requests: [], screenshots: [] };
const receipt = path.join(out, 'root-v29-browser-retry2-acceptance.json');
if (fs.existsSync(receipt)) throw Error('Preserve completed browser receipt');
report.prior_attempt = {path:'root-v29-browser-acceptance.json',sha256:sha(fs.readFileSync(path.join(out,'root-v29-browser-acceptance.json')))};
report.test_correction = 'The original 9-million-subscriber caption is hidden until mouseover. Check the preserved hover interaction rather than expecting an initially visible caption. Alternating news rows use news-collapsealt/news-expandalt; preserve their real toggle and check the class prefix. Exported bytes are unchanged.';
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
    await new Promise((resolve, reject) => { server.once('error', reject); server.listen(29029, '127.0.0.1', resolve); });
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1400, height: 1000 } });
    context.setDefaultTimeout(12000);
    await context.route('**/*', request => {
      if (new URL(request.request().url()).origin === origin && ['GET', 'HEAD'].includes(request.request().method())) return request.continue();
      report.external_requests.push(request.request().url()); return request.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', error => report.errors.push(String(error)));
    check('exact40new original resources since live v28', entries.length === 40 && byOriginal.size === 40);
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
        if (route === 'news/images/07-07/9000caption.png') {
          const image = page.locator('#caption > img[src$="/' + route + '"]');
          check('caption reference replaced', await image.count() === count, {page:name,route,count:await image.count(),expected:count});
          const id = await image.evaluate(el=>{let p=el;while(p&&!/^news\d/.test(p.id||''))p=p.parentElement;return p?.id;});
          const entry = page.locator('[id="'+id+'"]');
          if ((await entry.getAttribute('class')).startsWith('news-collapse')) {await entry.locator('.news-toggle a').first().click();await page.waitForFunction(id=>document.getElementById(id).className.startsWith('news-expand'),id);}
          const hover = image.locator('xpath=../..');
          check('original caption starts hidden', !await image.isVisible());
          await hover.scrollIntoViewIfNeeded();await hover.hover({position:{x:50,y:100}});await image.waitFor({state:'visible'});
          const dimensions = await image.evaluate(el=>[el.naturalWidth,el.naturalHeight]);
          check('restored image visible', await image.isVisible() && JSON.stringify(dimensions)===JSON.stringify(item.dimensions), {page:name,route,dimensions});
          await page.mouse.move(0,0);await image.waitFor({state:'hidden'});
          check('original caption hides on mouseout', !await image.isVisible());
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
    check('all40actual displayed references visible', report.checks.filter(item => item.name === 'restored image visible').length === 40);
    for (const name of [...pages.keys()]) {
      await page.goto(base + name, {waitUntil:'networkidle'});
      const reference = pages.get(name)[0], route = outputPath(byOriginal.get(reference.original));
      const image = page.locator('img[src$="/' + route + '"]').first();
      const id = await image.evaluate(el => {let p=el;while(p&&!/^news\d/.test(p.id||''))p=p.parentElement;return p?.id;});
      check('newly illustrated article has its original entry', !!id, {page:name,route});
      const entry = page.locator('[id="' + id + '"]');
      const toggle = entry.locator('.news-toggle a').first();
      if (!await image.isVisible()) {await toggle.click();await image.waitFor({state:'visible'});}
      await image.scrollIntoViewIfNeeded();
      await toggle.click();await image.waitFor({state:'hidden'});
      check('newly illustrated article collapses', !await image.isVisible(), {page:name});
      await toggle.click();await image.waitFor({state:'visible'});
      check('newly illustrated article reopens', await image.isVisible(), {page:name});
      if (name === 'news/rss-06-2007.xml.html' || name === 'news/rss-10-2007.xml.html') {
        await image.scrollIntoViewIfNeeded();
        const png = 'v29-' + name.replaceAll('/', '-') + '.png';
        await page.screenshot({path:path.join(out,png),fullPage:false});report.screenshots.push(png);
      }
    }
    check('no external requests', report.external_requests.length === 0);
    check('no browser errors', report.errors.length === 0);
    report.accepted = true;
  } catch (error) {
    report.errors.push(String(error));report.accepted = false;
  } finally {
    report.finished_utc = new Date().toISOString();
    report.export_provenance_sha256 = sha(fs.readFileSync(path.join(site, 'export-provenance.json')));
    fs.writeFileSync(receipt,JSON.stringify(report,null,2)+'\n');
    if (browser) await browser.close();
    await new Promise(resolve=>server.close(resolve));
    console.log(JSON.stringify({accepted:report.accepted,checks:report.checks.length,errors:report.errors,external_requests:report.external_requests.length}));
    if (!report.accepted) process.exitCode = 1;
  }
})();
