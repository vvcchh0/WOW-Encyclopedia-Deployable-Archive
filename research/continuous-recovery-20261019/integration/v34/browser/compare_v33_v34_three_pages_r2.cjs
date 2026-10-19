/* Loopback-only v33/v34 production-page comparison. */
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../../..');
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const PAGES = [
  { name: 'contest-winners', route: 'contests/05-05-25/winners.html' },
  { name: 'contests-index', route: 'contests/index.html' },
  { name: 'ordinary-guide', route: 'info/basics/guide.html' },
];
const OUTPUTS = {
  v33: path.join(ROOT, '.scratch/pages-resources-20261018-v33'),
  v34: path.join(ROOT, '.scratch/pages-resources-20261019-v34'),
};
const REPORT = path.join(__dirname, 'v33-v34-three-pages-r2.json');
const SCREENSHOTS = path.join(__dirname, 'screenshots-r2');

function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function inside(file, base) {
  const resolved = path.resolve(file), root = path.resolve(base);
  if (resolved !== root && !resolved.startsWith(root + path.sep)) throw new Error(`path escapes ${root}: ${file}`);
  return resolved;
}
function mime(file) {
  const ext = path.extname(file).toLowerCase();
  return ({ '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8', '.xml': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.png': 'image/png', '.svg': 'image/svg+xml' })[ext] || 'application/octet-stream';
}
function localFile(root, pathname) {
  if (!pathname.startsWith(BASE_PATH)) return null;
  const relative = decodeURIComponent(pathname.slice(BASE_PATH.length));
  if (!relative || relative.includes('\0') || relative.split('/').includes('..')) return null;
  const file = inside(path.join(root, relative), root);
  return fs.existsSync(file) && fs.statSync(file).isFile() ? file : null;
}
function createServer(root) {
  let localRequests = 0;
  const server = http.createServer((request, response) => {
    try {
      const requestUrl = new URL(request.url || '/', 'http://127.0.0.1');
      const file = localFile(root, requestUrl.pathname);
      if (!file || !['GET', 'HEAD'].includes(request.method)) { response.writeHead(404); return response.end(); }
      localRequests += 1;
      const body = fs.readFileSync(file);
      response.writeHead(200, { 'Content-Type': mime(file), 'Content-Length': body.length, 'Cache-Control': 'no-store' });
      if (request.method === 'HEAD') return response.end();
      response.end(body);
    } catch (_) { response.writeHead(400); response.end(); }
  });
  return { server, getLocalRequests: () => localRequests };
}
async function listen(server) {
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  return `http://127.0.0.1:${server.address().port}`;
}
async function close(server) { await new Promise(resolve => server.close(() => resolve())); }
async function settleClick(context, page, click, timeoutMs = 4000) {
  const before = page.url();
  return new Promise((resolve, reject) => {
    let settled = false;
    const finish = value => { if (settled) return; settled = true; cleanup(); resolve(value); };
    const cleanup = () => { clearTimeout(timer); context.off('page', onPopup); page.off('framenavigated', onNavigate); };
    const onPopup = popup => finish({ kind: 'popup', url: popup.url(), popup });
    const onNavigate = frame => { if (frame === page.mainFrame() && page.url() !== before) finish({ kind: 'same-tab', url: page.url() }); };
    context.on('page', onPopup); page.on('framenavigated', onNavigate);
    const timer = setTimeout(() => finish({ kind: 'none', url: page.url() }), timeoutMs);
    Promise.resolve().then(click).catch(error => { cleanup(); reject(error); });
  });
}
async function inspect(browser, variant, spec) {
  const holder = createServer(OUTPUTS[variant]);
  const origin = await listen(holder.server);
  const externalRequests = [], failedRequests = [], pageErrors = [], menuResponses = [], menuFinished = [], menuFailed = [];
  const context = await browser.newContext({ viewport: { width: 1550, height: 1100 } });
  await context.route('**/*', async route => {
    const requestUrl = new URL(route.request().url());
    if (requestUrl.hostname !== '127.0.0.1' && requestUrl.hostname !== 'localhost') {
      externalRequests.push(route.request().url());
      return route.abort();
    }
    return route.continue();
  });
  const page = await context.newPage();
  const isMenuIframe = value => /\/new-hp\/menus\/menu[1-8]\.htm(?:$|\?)/i.test(value);
  page.on('pageerror', error => pageErrors.push({ message: error.message, stack: error.stack || null }));
  page.on('response', response => { if (isMenuIframe(response.url())) menuResponses.push({ url: response.url(), status: response.status(), content_type: response.headers()['content-type'] || null }); });
  page.on('requestfinished', request => { if (isMenuIframe(request.url())) menuFinished.push(request.url()); });
  page.on('requestfailed', request => {
    const row = { url: request.url(), error: request.failure() && request.failure().errorText };
    failedRequests.push(row);
    if (isMenuIframe(request.url())) menuFailed.push(row);
  });
  const url = origin + BASE_PATH + spec.route;
  let gotoError = null;
  try { await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 }); await page.waitForTimeout(1400); } catch (error) { gotoError = String(error && error.stack || error); }
  const initial = await page.evaluate(() => ({
    result: typeof window.result === 'undefined' ? null : String(window.result),
    resultType: typeof window.result,
    contestsNode: typeof window.Menu1_6_4 === 'undefined' ? null : String(window.Menu1_6_4[0]),
    title: document.title,
    bodyText: (document.body && document.body.innerText || '').slice(0, 4000),
    images: Array.from(document.images).map(image => ({ src: image.getAttribute('src'), complete: image.complete, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight })).slice(0, 80),
    contestLinks: Array.from(document.querySelectorAll('a')).map((a, index) => ({ index, text: (a.innerText || '').trim(), href: a.getAttribute('href'), visible: !!(a.offsetWidth || a.offsetHeight || a.getClientRects().length) })).filter(row => /contests/i.test(`${row.text} ${row.href || ''}`)).slice(0, 20),
    imageLinks: Array.from(document.querySelectorAll('a[rel="screenie"]')).map((a, index) => ({ index, text: (a.innerText || '').trim(), href: a.getAttribute('href'), visible: !!(a.offsetWidth || a.offsetHeight || a.getClientRects().length), image: a.querySelector('img') && a.querySelector('img').getAttribute('src') })).slice(0, 20),
  }));
  let screenshot = null;
  if (variant === 'v34' && spec.name === 'contest-winners') {
    fs.mkdirSync(SCREENSHOTS, { recursive: true });
    screenshot = path.join(SCREENSHOTS, 'winners-v34-r2.png');
    await page.screenshot({ path: screenshot, fullPage: true });
  }
  let contestsClick = null;
  if (spec.name === 'contest-winners') {
    const linkIndex = await page.evaluate(() => Array.from(document.querySelectorAll('a')).findIndex(a => /contests\/index\.html/i.test(a.getAttribute('href') || '') && /contests/i.test(a.innerText || '')));
    if (linkIndex >= 0) {
      contestsClick = await settleClick(context, page, () => page.locator('a').nth(linkIndex).click({ force: true }));
      if (contestsClick.popup) await contestsClick.popup.close().catch(() => {});
    } else contestsClick = { kind: 'missing-candidate' };
  }
  let imageClick = null;
  if (spec.name === 'ordinary-guide') {
    const imageIndex = await page.evaluate(() => Array.from(document.querySelectorAll('a[rel="screenie"]')).findIndex(a => {
      const rect = a.getBoundingClientRect();
      return !!(rect.width || rect.height) && /\.(?:jpg|jpeg|png|gif|webp)(?:[?#]|$)/i.test(a.getAttribute('href') || '');
    }));
    if (imageIndex >= 0) {
      imageClick = await settleClick(context, page, () => page.locator('a[rel="screenie"]').nth(imageIndex).click({ force: true }));
      if (imageClick.popup) { await imageClick.popup.waitForTimeout(500).catch(() => {}); imageClick.popupUrlAfter = imageClick.popup.url(); await imageClick.popup.close().catch(() => {}); }
      imageClick.viewer = await page.evaluate(() => ({
        dumpster: !!document.getElementById('dumpster'),
        screenie: !!document.getElementById('Screenie'),
        background_image: document.getElementById('Screenie') ? document.getElementById('Screenie').style.backgroundImage : null,
        screenie_width: document.getElementById('Screenie') ? document.getElementById('Screenie').style.width : null,
      }));
      if (variant === 'v34' && imageClick.viewer.dumpster) {
        fs.mkdirSync(SCREENSHOTS, { recursive: true });
        screenshot = path.join(SCREENSHOTS, 'guide-viewer-v34-r2.png');
        await page.screenshot({ path: screenshot, fullPage: true });
      }
    } else imageClick = { kind: 'missing-candidate' };
  }
  const after = await page.evaluate(() => ({ url: location.href, result: typeof window.result === 'undefined' ? null : String(window.result), bodyText: (document.body && document.body.innerText || '').slice(0, 4000) }));
  const result = { variant, page: spec, url, goto_error: gotoError, initial, contests_click: contestsClick, image_click: imageClick, screenshot, menu_iframes: { responses: menuResponses, finished: menuFinished, failed: menuFailed }, after, page_errors: pageErrors, failed_requests: failedRequests, external_requests: externalRequests, local_requests: holder.getLocalRequests() };
  await context.close(); await close(holder.server);
  return result;
}
async function main() {
  const browser = await chromium.launch({ headless: true });
  const results = [];
  try {
    for (const variant of ['v33', 'v34']) for (const spec of PAGES) results.push(await inspect(browser, variant, spec));
  } finally { await browser.close(); }
  const report = {
    schema: 'wow-recovery.integration.v33-v34-three-pages-browser-r2.v1',
    pages: PAGES,
    variants: ['v33', 'v34'],
    network_requests: results.reduce((sum, row) => sum + row.external_requests.length, 0),
    screenshots: results.filter(row => row.screenshot).map(row => ({ variant: row.variant, page: row.page.name, path: path.relative(ROOT, row.screenshot).replace(/\\/g, '/') })),
    results,
    assertions: {
      external_requests_zero: results.every(row => row.external_requests.length === 0),
      v34_winners_result: results.find(row => row.variant === 'v34' && row.page.name === 'contest-winners')?.initial.result || null,
      v34_winners_contests_click: results.find(row => row.variant === 'v34' && row.page.name === 'contest-winners')?.contests_click || null,
      v34_guide_image_click: results.find(row => row.variant === 'v34' && row.page.name === 'ordinary-guide')?.image_click || null,
      v34_guide_viewer_created: !!results.find(row => row.variant === 'v34' && row.page.name === 'ordinary-guide')?.image_click?.viewer?.dumpster,
      menu_iframe_html_mime: results.every(row => row.menu_iframes.responses.length === 8 && row.menu_iframes.responses.every(item => /^text\/html(?:;|$)/i.test(item.content_type || ''))),
      menu_iframe_finished: results.every(row => row.menu_iframes.finished.length === 8),
      menu_iframe_failures_zero: results.every(row => row.menu_iframes.failed.length === 0),
    },
  };
  fs.mkdirSync(path.dirname(REPORT), { recursive: true });
  fs.writeFileSync(REPORT, JSON.stringify(report, null, 2) + '\n', 'utf8');
  process.stdout.write(JSON.stringify({ report: REPORT, report_sha256: sha256(fs.readFileSync(REPORT)), screenshots: report.screenshots, assertions: report.assertions }) + '\n');
}
main().catch(error => { console.error(error && error.stack || error); process.exitCode = 1; });
