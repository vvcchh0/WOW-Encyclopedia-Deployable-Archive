/* Loopback-only v34 winners -> Contests navigation follow-up. */
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../../..');
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const OUTPUT = path.join(ROOT, '.scratch/pages-resources-20261019-v34');
const REPORT = path.join(__dirname, 'v34-winners-navigation-r3b.json');
const SCREENSHOTS = path.join(__dirname, 'screenshots-r3b');
const ROUTE = 'contests/05-05-25/winners.html';
const TARGET_ROUTE = 'contests/index.html';

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

async function main() {
  const holder = createServer(OUTPUT);
  const origin = await listen(holder.server);
  const externalRequests = [], failedRequests = [], pageErrors = [], menuResponses = [], menuFinished = [], menuFailed = [], targetResponses = [];
  const context = await chromium.launch({ headless: true }).then(browser => browser.newContext({ viewport: { width: 1550, height: 1100 } }).then(pageContext => ({ browser, pageContext })));
  const browser = context.browser, pageContext = context.pageContext;
  const page = await pageContext.newPage();
  const isMenuIframe = value => /\/new-hp\/menus\/menu[1-8]\.htm(?:$|\?)/i.test(value);
  const isTarget = value => new URL(value).pathname.endsWith(`${BASE_PATH}${TARGET_ROUTE}`);
  await pageContext.route('**/*', async route => {
    const requestUrl = new URL(route.request().url());
    if (requestUrl.hostname !== '127.0.0.1' && requestUrl.hostname !== 'localhost') {
      externalRequests.push(route.request().url());
      return route.abort();
    }
    return route.continue();
  });
  page.on('pageerror', error => pageErrors.push({ message: error.message, stack: error.stack || null }));
  page.on('response', response => {
    if (isMenuIframe(response.url())) menuResponses.push({ url: response.url(), status: response.status(), content_type: response.headers()['content-type'] || null });
    if (isTarget(response.url())) targetResponses.push({ url: response.url(), status: response.status(), content_type: response.headers()['content-type'] || null });
  });
  page.on('requestfinished', request => { if (isMenuIframe(request.url())) menuFinished.push(request.url()); });
  page.on('requestfailed', request => {
    const row = { url: request.url(), error: request.failure() && request.failure().errorText };
    failedRequests.push(row);
    if (isMenuIframe(request.url())) menuFailed.push(row);
  });
  const initialUrl = origin + BASE_PATH + ROUTE;
  let gotoError = null;
  let destination = null;
  let clickError = null;
  try {
    await page.goto(initialUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(1400);
    const linkIndex = await page.evaluate(() => Array.from(document.querySelectorAll('a')).findIndex(a => /contests\/index\.html/i.test(a.getAttribute('href') || '') && /contests/i.test(a.innerText || '')));
    if (linkIndex < 0) throw new Error('missing visible Contests navigation candidate');
    const targetResponse = page.waitForResponse(response => isTarget(response.url()) && response.status() === 200, { timeout: 15000 }).catch(() => null);
    await page.locator('a').nth(linkIndex).click({ force: true });
    await targetResponse;
    // The legacy page can report ERR_ABORTED after the target response while
    // the main frame is still committing. Poll the URL, then observe the
    // committed target instead of treating that expected request event as a
    // failed navigation.
    for (let attempt = 0; attempt < 20 && !page.url().endsWith(`${BASE_PATH}${TARGET_ROUTE}`); attempt += 1) await page.waitForTimeout(250);
    if (!page.url().endsWith(`${BASE_PATH}${TARGET_ROUTE}`)) throw new Error(`target URL not committed: ${page.url()}`);
    await page.waitForTimeout(750);
    destination = await page.evaluate(() => ({
      url: location.href,
      title: document.title,
      body_text: (document.body && document.body.innerText || '').slice(0, 4000),
      body_text_length: (document.body && document.body.innerText || '').length,
      result: typeof window.result === 'undefined' ? null : String(window.result),
      contests_node: typeof window.Menu1_6_4 === 'undefined' ? null : String(window.Menu1_6_4[0]),
    }));
  } catch (error) {
    clickError = String(error && error.stack || error);
  }
  const initial = await page.evaluate(() => ({
    url: location.href,
    title: document.title,
    result: typeof window.result === 'undefined' ? null : String(window.result),
    body_text_length: (document.body && document.body.innerText || '').length,
  })).catch(error => ({ evaluate_error: String(error && error.stack || error) }));
  fs.mkdirSync(SCREENSHOTS, { recursive: true });
  const screenshot = path.join(SCREENSHOTS, 'winners-v34-contests-destination-r3b.png');
  if (!clickError && destination) await page.screenshot({ path: screenshot, fullPage: true });
  const report = {
    schema: 'wow-recovery.integration.v34-winners-navigation-browser-r3b.v1',
    route: ROUTE,
    target_route: TARGET_ROUTE,
    server_mime_fix: { '.htm': 'text/html; charset=utf-8' },
    initial_url: initialUrl,
    initial,
    destination,
    click_error: clickError,
    goto_error: gotoError,
    target_responses: targetResponses,
    menu_iframes: { responses: menuResponses, finished: menuFinished, failed: menuFailed },
    page_errors: pageErrors,
    failed_requests: failedRequests,
    external_requests: externalRequests,
    local_requests: holder.getLocalRequests(),
    screenshot: fs.existsSync(screenshot) ? path.relative(ROOT, screenshot).replace(/\\/g, '/') : null,
    assertions: {
      external_requests_zero: externalRequests.length === 0,
      menu_iframe_html_mime: menuResponses.length === 8 && menuResponses.every(item => /^text\/html(?:;|$)/i.test(item.content_type || '')),
      menu_iframe_finished: menuFinished.length === 8,
      menu_iframe_failures_zero: menuFailed.length === 0,
      target_http_200_html: targetResponses.some(item => item.status === 200 && /^text\/html(?:;|$)/i.test(item.content_type || '')),
      target_route_loaded: !!destination && destination.url.endsWith(`${BASE_PATH}${TARGET_ROUTE}`),
      target_title_present: !!destination && destination.title.length > 0,
      target_body_present: !!destination && destination.body_text_length > 0,
      target_contests_result: destination && destination.result,
    },
  };
  fs.writeFileSync(REPORT, JSON.stringify(report, null, 2) + '\n', 'utf8');
  await pageContext.close();
  await browser.close();
  await close(holder.server);
  process.stdout.write(JSON.stringify({ report: REPORT, report_sha256: sha256(fs.readFileSync(REPORT)), screenshot: report.screenshot, assertions: report.assertions }) + '\n');
  if (clickError || !report.assertions.target_http_200_html || !report.assertions.target_route_loaded || !report.assertions.target_body_present) process.exitCode = 1;
}
main().catch(error => { console.error(error && error.stack || error); process.exitCode = 1; });
