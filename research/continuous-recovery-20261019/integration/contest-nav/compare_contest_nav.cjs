/*
 * Loopback-only before/after browser evidence for the contest navigation fix.
 * This serves frozen v33 files and swaps only navtreefunctions.js in the
 * derived variant. It never contacts the network or edits the frozen output.
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../..');
const INTEGRATION_ROOT = path.resolve(__dirname);
const OUTPUT_ROOT = path.join(ROOT, '.scratch/pages-resources-20261018-v33');
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const PAGE_ROUTE = '/contests/05-05-25/winners.html';
const NAV_ROUTE = '/shared/wow-com/includes-client/navtreefunctions.js';
const BINDINGS_PATH = path.join(INTEGRATION_ROOT, 'browser-fixture-bindings.json');
const DERIVED_PATH = path.join(INTEGRATION_ROOT, 'fixtures/navtreefunctions.derived.js');
const RESULTS_PATH = path.join(INTEGRATION_ROOT, 'results/contest-nav-before-after.json');

function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function readJson(file) { return JSON.parse(fs.readFileSync(file, 'utf8')); }
function inside(file, base) {
  const resolved = path.resolve(file);
  const root = path.resolve(base);
  if (resolved !== root && !resolved.startsWith(root + path.sep)) throw new Error(`path escapes root: ${file}`);
  return resolved;
}
function mime(file) {
  const ext = path.extname(file).toLowerCase();
  return ({
    '.html': 'text/html; charset=utf-8', '.xml': 'application/xml; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
    '.gif': 'image/gif', '.png': 'image/png', '.svg': 'image/svg+xml',
  })[ext] || 'application/octet-stream';
}
function localFile(urlPath) {
  if (!urlPath.startsWith(BASE_PATH)) return null;
  const relative = decodeURIComponent(urlPath.slice(BASE_PATH.length));
  if (!relative || relative.includes('\0')) return null;
  const file = inside(path.join(OUTPUT_ROOT, relative), OUTPUT_ROOT);
  return fs.existsSync(file) && fs.statSync(file).isFile() ? file : null;
}
function createServer(variant) {
  let localRequests = 0;
  const server = http.createServer((request, response) => {
    const requestUrl = new URL(request.url, 'http://127.0.0.1');
    const file = localFile(requestUrl.pathname);
    if (!file) {
      response.statusCode = 404;
      response.end('not found');
      return;
    }
    localRequests += 1;
    let body = fs.readFileSync(file);
    if (variant === 'derived' && requestUrl.pathname === BASE_PATH + NAV_ROUTE.slice(1)) body = fs.readFileSync(DERIVED_PATH);
    response.writeHead(200, { 'Content-Type': mime(file), 'Content-Length': body.length, 'Cache-Control': 'no-store' });
    response.end(body);
  });
  return { server, getLocalRequests: () => localRequests };
}
async function listen(server) {
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  const address = server.address();
  return `http://127.0.0.1:${address.port}`;
}
async function close(server) {
  await new Promise(resolve => server.close(() => resolve()));
}
async function inspectVariant(browser, variant) {
  const holder = createServer(variant);
  const origin = await listen(holder.server);
  const externalRequests = [];
  const failedRequests = [];
  const pageErrors = [];
  const context = await browser.newContext();
  await context.route('**/*', async route => {
    const requestUrl = new URL(route.request().url());
    if (requestUrl.hostname !== '127.0.0.1' && requestUrl.hostname !== 'localhost') {
      externalRequests.push(route.request().url());
      await route.abort();
      return;
    }
    await route.continue();
  });
  const page = await context.newPage();
  page.on('pageerror', error => pageErrors.push({ message: error.message, stack: error.stack || null }));
  page.on('requestfailed', request => failedRequests.push({ url: request.url(), error: request.failure() && request.failure().errorText }));
  const url = origin + BASE_PATH + PAGE_ROUTE.slice(1);
  let gotoError = null;
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(1200);
  } catch (error) {
    gotoError = String(error && error.stack || error);
  }
  const observed = await page.evaluate(() => ({
    result: typeof window.result === 'undefined' ? null : String(window.result),
    resultType: typeof window.result,
    menuLabel: typeof window.Menu1_6_4 === 'undefined' ? null : String(window.Menu1_6_4[0]),
    bodyText: document.body ? document.body.innerText : '',
    title: document.title,
    images: Array.from(document.images).map(image => ({ src: image.getAttribute('src'), complete: image.complete, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight })),
    imageLinks: Array.from(document.querySelectorAll('a')).filter(anchor => anchor.querySelector('img')).map(anchor => ({ href: anchor.getAttribute('href'), image: anchor.querySelector('img').getAttribute('src') })),
    contestText: Array.from(document.querySelectorAll('body *')).filter(node => /contest/i.test(node.textContent || '')).slice(0, 12).map(node => (node.textContent || '').trim().slice(0, 200)),
  }));
  const result = {
    variant,
    url,
    goto_error: gotoError,
    nav_result: observed.result,
    nav_result_type: observed.resultType,
    menu_label: observed.menuLabel,
    title: observed.title,
    body_text_sha256: sha256(Buffer.from(observed.bodyText, 'utf8')),
    body_text_length: observed.bodyText.length,
    contest_text: observed.contestText,
    images: observed.images,
    image_links: observed.imageLinks,
    page_errors: pageErrors,
    failed_requests: failedRequests,
    external_requests: externalRequests,
    local_requests: holder.getLocalRequests(),
  };
  await context.close();
  await close(holder.server);
  return result;
}
async function main() {
  const bindings = readJson(BINDINGS_PATH);
  if (!fs.existsSync(DERIVED_PATH)) throw new Error('missing derived fixture');
  if (sha256(fs.readFileSync(DERIVED_PATH)) !== bindings.derived.sha256) throw new Error('derived fixture SHA mismatch');
  const browser = await chromium.launch({ headless: true });
  try {
    const before = await inspectVariant(browser, 'original');
    const after = await inspectVariant(browser, 'derived');
    const result = {
      schema: 'contest-nav-browser-comparison-v1',
      network_requests: before.external_requests.length + after.external_requests.length,
      source_bindings: bindings,
      before,
      after,
      assertions: {
        before_nav_result: before.nav_result,
        after_nav_result: after.nav_result,
        after_restores_contests_parent: after.nav_result === '1_6_4' && after.menu_label === 'Contests',
        body_text_same: before.body_text_sha256 === after.body_text_sha256,
        image_links_same: JSON.stringify(before.image_links) === JSON.stringify(after.image_links),
        external_requests_zero: before.external_requests.length === 0 && after.external_requests.length === 0,
      },
    };
    if (result.network_requests !== 0 || !result.assertions.after_restores_contests_parent) throw new Error(`browser comparison failed: ${JSON.stringify(result.assertions)}`);
    fs.mkdirSync(path.dirname(RESULTS_PATH), { recursive: true });
    fs.writeFileSync(RESULTS_PATH, JSON.stringify(result, null, 2) + '\n', 'utf8');
    process.stdout.write(JSON.stringify({ result: RESULTS_PATH, assertions: result.assertions }) + '\n');
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error && error.stack || error); process.exitCode = 1; });
