// Worker-prepared browser QA.  This script is intentionally not a root
// acceptance receipt and is not run by the offline checker.
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const root = process.cwd();
const site = path.join(root, '.scratch/pages-resources-20261016-v23');
const out = path.join(root, 'research/continuous-recovery-20261016/publication');
const prefix = '/WOW-Encyclopedia-Deployable-Archive';
const origin = 'http://127.0.0.1:29023';
const base = origin + prefix + '/';
const reportPath = path.join(out, 'root-v23-browser-acceptance.json');
const collectionMapPath = path.join(root, 'research/continuous-recovery-20261016/integration/v23-guide-image-collection-map-final40.json');
const provenancePath = path.join(site, 'export-provenance.json');
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const report = {
  schema: 'wow-recovery.publication.v23-browser-preparation.v1',
  accepted: false,
  browser_check_passed: false,
  root_acceptance_called: true,
  export_executed: false,
  checks: [],
  errors: [],
  external_requests: [],
  failed_requests: [],
  local_http_errors: [],
  console_errors: [],
  page_errors: [],
  screenshots: [],
};

function check(name, accepted, detail = {}) {
  const item = { name, accepted, ...detail };
  report.checks.push(item);
  if (!accepted) throw new Error(name + ': ' + JSON.stringify(detail));
}

let recordsByRoute=new Map(), canonicalByOutput=new Map();
function localUrl(route) {
  const output=recordsByRoute.get(route)?.output_path || String(route).replace(/^\//, '');
  return base + output;
}

function pathname(value) {
  const p=new URL(value, origin).pathname.replace(prefix, '') || '/'; return canonicalByOutput.get(p)||p;
}

function mimeFor(file) {
  return {
    '.html': 'text/html', '.xml': 'application/xml', '.js': 'text/javascript',
    '.json': 'application/json', '.css': 'text/css', '.gif': 'image/gif',
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
    '.svg': 'image/svg+xml', '.woff': 'font/woff', '.woff2': 'font/woff2',
  }[path.extname(file).toLowerCase()] || 'application/octet-stream';
}

function startServer() {
  const server = http.createServer((req, res) => {
    let relative;
    try {
      const parsed = new URL(req.url, origin);
      if (!parsed.pathname.startsWith(prefix + '/')) throw new Error('outside prefix');
      relative = decodeURIComponent(parsed.pathname.slice(prefix.length + 1));
    } catch {
      res.writeHead(400);
      return res.end();
    }
    const file = path.resolve(site, relative);
    if (!file.startsWith(site + path.sep) || !['GET', 'HEAD'].includes(req.method) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
      report.local_http_errors.push({ method: req.method, path: relative, status: 404 });
      res.writeHead(404);
      return res.end();
    }
    res.writeHead(200, { 'content-type': mimeFor(file), 'cache-control': 'no-store' });
    if (req.method === 'HEAD') return res.end();
    fs.createReadStream(file).pipe(res);
  });
  return server;
}

function loadInputs() {
  const collectionMap = JSON.parse(fs.readFileSync(collectionMapPath, 'utf8'));
  const provenance = JSON.parse(fs.readFileSync(provenancePath, 'utf8'));
  const expectedGroups = {
    'love-is-in-the-air': { count: 10, guide: '/info/events/loveisintheair/index.html', gallery: '/info/events/loveisintheair/gallery.html' },
    'lunar-festival': { count: 10, guide: '/info/events/lunarnewyears/index.html', gallery: '/info/events/lunarnewyears/gallery.html' },
    'world-pvp': { count: 12, guide: '/pvp/worldpvp/index.xml', gallery: '/pvp/worldpvp/worldpvp-gallery.html' },
  };
  const byGroup = new Map();
  for (const group of collectionMap.groups || []) {
    const expected = expectedGroups[group.group_id];
    check('collection map group', !!expected && group.images.length === expected.count, { group: group.group_id, count: group.images.length });
    byGroup.set(group.group_id, { ...expected, images: group.images });
  }
  check('collection map groups', byGroup.size === 3, { groups: [...byGroup.keys()] });
  check('collection map images', [...byGroup.values()].reduce((n, g) => n + g.images.length, 0) === 32);
  const routeRecords = new Map((provenance.files || []).map(item => [item.route, item])); recordsByRoute=routeRecords;canonicalByOutput=new Map(provenance.files.map(x=>['/'+x.output_path,x.route]));
  return { byGroup, routeRecords };
}

async function trackContext(context) {
  await context.route('**/*', route => {
    const request = route.request();
    const requestUrl = new URL(request.url());
    if (requestUrl.origin === origin && ['GET', 'HEAD'].includes(request.method())) return route.continue();
    report.external_requests.push({ url: request.url(), method: request.method() });
    return route.abort();
  });
  context.on('requestfailed', request => report.failed_requests.push({ url: request.url(), failure: request.failure()?.errorText || 'unknown' }));
  context.on('response', response => {
    if (response.status() >= 400 && new URL(response.url()).origin === origin) {
      report.local_http_errors.push({ url: response.url(), status: response.status() });
    }
  });
}

async function verifyImageBytes(context, group) {
  const seen = new Set();
  for (const image of group.images) {
    if (seen.has(image.route)) continue;
    seen.add(image.route);
    const response = await context.request.get(localUrl(image.route));
    const bytes = await response.body();
    check('collection image local bytes', response.status() === 200 && bytes.length === image.length && sha(bytes) === image.sha256, { route: image.route, status: response.status(), length: bytes.length, sha256: sha(bytes) });
  }
}

async function verifyCollectionPage(page, context, groupId, group, pageRole, clickedRoutes) {
  const route = pageRole === 'guide' ? group.guide : group.gallery;
  const response = await page.goto(localUrl(route), { waitUntil: 'networkidle' });
  check('collection page response', response && response.status() === 200, { route, status: response && response.status() });
  const sectionId = `offline-guide-images-${groupId.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toLowerCase()}-${pageRole}`;
  check('collection section unique', await page.locator(`#${sectionId}`).count() === 1, { route, sectionId });
  const cards = page.locator(`#${sectionId} [data-guide-image-route]`);
  check('collection card count', await cards.count() === group.count, { route, count: await cards.count(), expected: group.count });
  const anchor = page.locator(`#${sectionId} a.offline-guide-image-guide`);
  check('collection guide anchor unique', await anchor.count() === 1, { route });
  const anchorHref = await anchor.getAttribute('href');
  check('collection guide anchor local', pathname(anchorHref) === group.guide, { route, href: anchorHref, expected: group.guide });
  for (let index = 0; index < group.count; index += 1) {
    const card = cards.nth(index);
    const image = card.locator('img');
    await image.scrollIntoViewIfNeeded();
    await image.waitFor({ state: 'visible' });
    await page.waitForFunction(el=>el.complete&&el.naturalWidth>0,await image.elementHandle());
    const state = await image.evaluate(el => ({ loading: el.getAttribute('loading'), complete: el.complete, width: el.naturalWidth, height: el.naturalHeight, route: el.getAttribute('data-guide-image-route') || el.closest('[data-guide-image-route]')?.getAttribute('data-guide-image-route') }));
    check('collection image visible and decoded', state.loading === 'lazy' && state.complete && state.width > 0 && state.height > 0, { route, index, state });
    const imageRoute = state.route || await card.getAttribute('data-guide-image-route');
    check('collection image route matches map', imageRoute === group.images[index].route, { route, index, imageRoute, expected: group.images[index].route });
    const href = await card.getAttribute('href');
    check('collection full-size href local', pathname(href) === imageRoute, { route, index, href });
    if (!clickedRoutes.has(imageRoute)) {
      clickedRoutes.add(imageRoute);
      await card.click();
      await page.waitForLoadState('domcontentloaded').catch(() => {});
      check('collection full-size click', pathname(page.url()) === imageRoute, { from: route, imageRoute, landed: pathname(page.url()) });
      await page.goBack({ waitUntil: 'domcontentloaded' }).catch(() => {});
      await page.goto(localUrl(route), { waitUntil: 'networkidle' });
    }
  }
  await page.locator(`#${sectionId}`).scrollIntoViewIfNeeded();
  const screenshot=path.join(out,`v23-root-${groupId}-${pageRole}-${page.viewportSize().width}.png`);
  await page.screenshot({path:screenshot,fullPage:false});report.screenshots.push(path.relative(root,screenshot).replaceAll('\\','/'));
  await anchor.click();
  await page.waitForLoadState('domcontentloaded').catch(() => {});
  check('collection guide anchor click', pathname(page.url()) === group.guide, { from: route, landed: pathname(page.url()), expected: group.guide });
}

async function verifyLegacyPages(page, context, screenshots, label) {
  const city = '/pvp/worldpvp/cityattacks-gallery.html';
  await page.goto(localUrl(city), { waitUntil: 'networkidle' });
  const cityPreviews = page.locator('.offline-guide-preview-section img');
  check('City preserved previews retained', await cityPreviews.count() === 3, { count: await cityPreviews.count() });
  for (const image of await cityPreviews.all()) {
    await image.scrollIntoViewIfNeeded();
    check('City preview decoded', await image.evaluate(el => el.complete && el.naturalWidth > 0), { src: await image.getAttribute('src') });
  }
  const pageNum = page.locator('#pageNum');
  const before = (await pageNum.innerText()).trim();
  await page.locator('a[href="javascript:galleryNext();"]').first().click();
  await page.waitForFunction(value => document.getElementById('pageNum')?.innerText.trim() !== value, before);
  check('City native pagination retained', (await pageNum.innerText()).trim() !== before, { before, after: (await pageNum.innerText()).trim() });
  const augustRoute = '/news/rss-08-2007.xml.html';
  await page.goto(localUrl(augustRoute), { waitUntil: 'networkidle' });
  const august = page.locator('img[src*="/news/images/07-08/"]');
  check('August 27 image elements retained', await august.count() === 27, { count: await august.count() });
  for (const image of await august.all()) {
    await image.scrollIntoViewIfNeeded();
    check('August image decoded', await image.evaluate(el => el.complete && el.naturalWidth > 0), { src: await image.getAttribute('src') });
  }
  const encyclopediaRoute = '/info/encyclopedia/index.xml.html';
  const encyclopedia = await page.goto(localUrl(encyclopediaRoute), { waitUntil: 'networkidle' });
  check('Encyclopedia retained', encyclopedia && encyclopedia.status() === 200 && (await page.content()).includes('Warcraft Encyclopedia'), { status: encyclopedia && encyclopedia.status() });
  const screenshot = path.join(out, `v23-root-${label}.png`);
  await page.screenshot({ path: screenshot, fullPage: false });
  report.screenshots.push(path.relative(root, screenshot).replaceAll('\\', '/'));
}

(async () => {
  let server;
  let browser;
  try {
    fs.mkdirSync(out, { recursive: true });
    if (fs.existsSync(reportPath)) throw new Error(`refusing to overwrite ${reportPath}`);
    check('v23 site exists', fs.existsSync(site));
    const { byGroup } = loadInputs();
    server = startServer();
    await new Promise((resolve, reject) => { server.once('error', reject); server.listen(29023, '127.0.0.1', resolve); });
    browser = await chromium.launch({ headless: true });
    const clickedRoutes = new Set();
    const contexts = [
      ['desktop', { viewport: { width: 1400, height: 1000 } }],
      ['mobile', { viewport: { width: 390, height: 844 }, isMobile: true, deviceScaleFactor: 1 }],
    ];
    for (const [label, options] of contexts) {
      const context = await browser.newContext(options);
      await trackContext(context);
      const page = await context.newPage();
      page.on('pageerror', error => report.page_errors.push({ label, error: String(error) }));
      page.on('console', message => { if (message.type() === 'error') report.console_errors.push({ label, text: message.text() }); });
      for (const [groupId, group] of byGroup.entries()) {
        await verifyImageBytes(context, group);
        await verifyCollectionPage(page, context, groupId, group, 'guide', clickedRoutes);
        await verifyCollectionPage(page, context, groupId, group, 'gallery', clickedRoutes);
      }
      await verifyLegacyPages(page, context, report.screenshots, label);
      await context.close();
    }
    check('all 32 unique full-size routes clicked', clickedRoutes.size === 32, { count: clickedRoutes.size });
    check('no external requests', report.external_requests.length === 0, { count: report.external_requests.length });
    check('no failed requests', report.failed_requests.length === 0, { count: report.failed_requests.length });
    check('no local HTTP errors', report.local_http_errors.length === 0, { count: report.local_http_errors.length });
    check('no console errors', report.console_errors.length === 0, { count: report.console_errors.length });
    check('no page errors', report.page_errors.length === 0, { count: report.page_errors.length });
    report.browser_check_passed = true;report.accepted=true;
  } catch (error) {
    report.errors.push(error.stack || String(error));
  } finally {
    if (browser) await browser.close();
    if (server) await new Promise(resolve => server.close(resolve));
    report.finished_utc = new Date().toISOString();
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ browser_check_passed: report.browser_check_passed, checks: report.checks.length, errors: report.errors.length, external_requests: report.external_requests.length, screenshots: report.screenshots.length }));
    if (!report.browser_check_passed) process.exitCode = 1;
  }
})();
