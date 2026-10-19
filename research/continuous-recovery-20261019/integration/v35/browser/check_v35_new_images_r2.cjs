/* Bounded loopback-only browser check for the 24 v35 news images. */
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../../..');
const BROWSER_DIR = path.resolve(__dirname);
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const OUTPUT_ROOT = path.join(ROOT, '.scratch/pages-resources-20261019-v35');
const DEFAULT_INPUT = path.join(BROWSER_DIR, 'v35-browser-input.json');
const DEFAULT_RESULT = path.join(BROWSER_DIR, 'results/v35-new-images-r2.json');
const DEFAULT_SCREENSHOTS = path.join(BROWSER_DIR, 'screenshots-r2');
const MAX_RUNTIME_MS = 300000;

function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function sha256File(file) { return sha256(fs.readFileSync(file)); }
function inside(file, base, label) {
  const resolved = path.resolve(file), root = path.resolve(base);
  if (resolved !== root && !resolved.startsWith(root + path.sep)) throw new Error(`${label} escapes ${root}: ${file}`);
  return resolved;
}
function readJson(file, label) {
  if (!fs.existsSync(file)) throw new Error(`missing ${label}: ${file}`);
  const value = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(`${label} is not an object`);
  return value;
}
function normalizePath(value) { return String(value || '').replace(/^\/+/, '').replace(/\\/g, '/'); }
function mime(file) {
  const ext = path.extname(file).toLowerCase();
  return ({
    '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8',
    '.xml': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
    '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8',
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
    '.png': 'image/png', '.webp': 'image/webp', '.bmp': 'image/bmp',
    '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  })[ext] || 'application/octet-stream';
}
function parseArgs(argv) {
  const args = { input: DEFAULT_INPUT, result: DEFAULT_RESULT, screenshots: DEFAULT_SCREENSHOTS, go: false, rootGo: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--input') args.input = path.resolve(argv[++i]);
    else if (arg === '--result') args.result = path.resolve(argv[++i]);
    else if (arg === '--screenshots') args.screenshots = path.resolve(argv[++i]);
    else if (arg === '--go') args.go = true;
    else if (arg === '--root-browser-go') args.rootGo = true;
    else throw new Error(`unknown argument: ${arg}`);
  }
  if (!args.go || !args.rootGo) throw new Error('browser execution requires --go --root-browser-go');
  args.input = inside(args.input, BROWSER_DIR, 'browser input');
  args.result = inside(args.result, BROWSER_DIR, 'browser result');
  args.screenshots = inside(args.screenshots, BROWSER_DIR, 'screenshots');
  if (fs.existsSync(args.result)) throw new Error(`refusing existing browser result: ${args.result}`);
  return args;
}
function verifyBinding(raw, label) {
  if (!raw || typeof raw !== 'object' || !raw.path || !raw.sha256) throw new Error(`${label} missing path/SHA`);
  const file = inside(path.join(ROOT, raw.path), ROOT, label);
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) throw new Error(`missing ${label}: ${file}`);
  const actual = sha256File(file);
  if (actual.toLowerCase() !== String(raw.sha256).toLowerCase()) throw new Error(`${label} SHA mismatch: ${actual} != ${raw.sha256}`);
  return file;
}
function visibleSnapshot(element) {
  const style = getComputedStyle(element), rect = element.getBoundingClientRect();
  return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
}
function createServer(outputRoot, targetByPath, report) {
  let localRequests = 0;
  const server = http.createServer((request, response) => {
    try {
      const requestUrl = new URL(request.url || '/', 'http://127.0.0.1');
      if (!requestUrl.pathname.startsWith(BASE_PATH) || !['GET', 'HEAD'].includes(request.method)) {
        response.writeHead(404); return response.end();
      }
      const relative = decodeURIComponent(requestUrl.pathname.slice(BASE_PATH.length));
      if (!relative || relative.includes('\\') || relative.includes('\0') || relative.split('/').includes('..')) {
        response.writeHead(400); return response.end();
      }
      const file = inside(path.join(outputRoot, relative), outputRoot, 'output request');
      if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { response.writeHead(404); return response.end(); }
      const body = fs.readFileSync(file);
      const record = { path: relative.replace(/\\/g, '/'), method: request.method, status: 200, mime: mime(file), length: body.length };
      if (targetByPath.has(record.path)) {
        record.sha256 = sha256(body);
        const expected = targetByPath.get(record.path);
        record.expected_sha256 = expected.sha256;
        record.expected_length = expected.length;
        record.exact = record.sha256 === expected.sha256 && record.length === expected.length && record.mime.toLowerCase().startsWith(String(expected.mime).toLowerCase().split(';')[0]);
      }
      report.local_image_or_asset_requests.push(record);
      localRequests += 1;
      response.writeHead(200, { 'Content-Type': record.mime, 'Content-Length': body.length, 'Cache-Control': 'no-store' });
      if (request.method === 'HEAD') return response.end();
      response.end(body);
    } catch (error) {
      report.server_errors.push(String(error && error.stack || error));
      response.writeHead(400); response.end();
    }
  });
  return { server, getLocalRequests: () => localRequests };
}
async function listen(server) {
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  return `http://127.0.0.1:${server.address().port}`;
}
async function closeServer(server) { if (server) await new Promise(resolve => server.close(() => resolve())); }
async function waitForClass(page, id, className) {
  await page.waitForFunction(({ expectedId, expectedClass }) => {
    const element = document.getElementById(expectedId);
    return !!element && String(element.className || '').split(/\s+/).some(value => value === expectedClass || value.startsWith(expectedClass));
  }, { expectedId: id, expectedClass: className }, { timeout: 10000 });
}
async function inspectImages(page, row) {
  const outputPath = normalizePath(row.served_output_path);
  return page.locator('img').evaluateAll(async (elements, expected) => {
    const rows = [];
    for (const element of elements) {
      const rawSrc = element.getAttribute('src') || '';
      let pathname = '';
      try { pathname = new URL(rawSrc, document.baseURI).pathname.replace(/^\/WOW-Encyclopedia-Deployable-Archive\//, ''); } catch (_) {}
      if (pathname !== expected.outputPath) continue;
      let decodeError = null;
      try { await element.decode(); } catch (error) { decodeError = String(error && error.message || error); }
      const style = getComputedStyle(element), rect = element.getBoundingClientRect();
      rows.push({
        src: rawSrc,
        current_src: element.currentSrc || null,
        pathname,
        natural: [element.naturalWidth, element.naturalHeight],
        complete: !!element.complete,
        decode_error: decodeError,
        display: style.display,
        visibility: style.visibility,
        opacity: style.opacity,
        box: [rect.width, rect.height],
        visible: style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0,
      });
    }
    return rows;
  }, { outputPath });
}
async function openPage(page, base, route) {
  const url = `${base}${normalizePath(route)}`;
  const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(400);
  return { url, status: response && response.status(), mime: response && response.headers()['content-type'] || null };
}
async function main() {
  const started = Date.now();
  const args = parseArgs(process.argv.slice(2));
  const input = readJson(args.input, 'v35 browser input');
  if (input.status !== 'prepared_waiting_root_v35_browser_go') throw new Error(`unexpected input status: ${input.status}`);
  if (input.network_requests !== 0 || input.export_executed !== false) throw new Error('browser input is not offline-prepared');
  for (const [name, binding] of Object.entries(input.frozen_bindings || {})) verifyBinding(binding, `binding ${name}`);
  const outputRoot = inside(path.join(ROOT, input.output.path), path.join(ROOT, '.scratch'), 'v35 output');
  if (!fs.existsSync(outputRoot) || !fs.statSync(outputRoot).isDirectory()) throw new Error(`missing promoted v35 output: ${outputRoot}`);
  const provenancePath = inside(path.join(outputRoot, 'export-provenance.json'), outputRoot, 'v35 provenance');
  if (sha256File(provenancePath) !== input.output.provenance_sha256) throw new Error('v35 output provenance SHA mismatch');
  const targets = Array.isArray(input.targets) ? input.targets : [];
  if (targets.length !== 24) throw new Error(`expected 24 targets, got ${targets.length}`);
  const targetByPath = new Map(targets.map(row => [normalizePath(row.served_output_path), row]));
  const staticRows = targets.filter(row => row.display_class === 'postContainer_static_no_toggle');
  const nativeRows = targets.filter(row => row.display_class === 'native_news_toggle');
  const report = {
    schema: 'wow-recovery.integration.v35-browser-result.v1', accepted: false,
    browser_executed: false, started_utc: new Date().toISOString(), finished_utc: null,
    input: { path: path.relative(ROOT, args.input).replace(/\\/g, '/'), sha256: sha256File(args.input) },
    output: { path: input.output.path, provenance_sha256: input.output.provenance_sha256 },
    target_count: targets.length, target_results: [], pages: [], native_toggle: null,
    local_image_or_asset_requests: [], external_requests: [], request_failures: [],
    console: [], page_errors: [], server_errors: [], local_requests: 0,
    screenshots: [], assertions: {}, errors: [],
  };
  let holder = null, browser = null, context = null, page = null, origin = null;
  try {
    holder = createServer(outputRoot, targetByPath, report);
    origin = await listen(holder.server);
    const localOrigin = new URL(origin).origin;
    browser = await chromium.launch({ headless: true });
    context = await browser.newContext({ viewport: { width: 1550, height: 1100 } });
    context.setDefaultTimeout(10000);
    await context.route('**/*', route => {
      const requestUrl = route.request().url();
      try {
        if (new URL(requestUrl).origin === localOrigin) return route.continue();
      } catch (_) {}
      report.external_requests.push(requestUrl);
      return route.abort();
    });
    page = await context.newPage();
    page.on('console', message => report.console.push({ type: message.type(), text: message.text(), location: message.location() }));
    page.on('pageerror', error => report.page_errors.push({ url: page.url(), message: String(error), stack: String(error.stack || '') }));
    page.on('requestfailed', request => report.request_failures.push({ url: request.url(), failure: request.failure() }));
    const staticPage = await openPage(page, origin + BASE_PATH, 'news/wow-news2004.html');
    report.pages.push({ route: 'news/wow-news2004.html', ...staticPage });
    for (const row of staticRows) {
      const facts = await inspectImages(page, row);
      report.target_results.push({ original: row.original, page: row.page_output, display_class: row.display_class, expected: { dimensions: row.dimensions, references: row.reference_count, served_output_path: row.served_output_path }, facts });
    }
    await page.locator('img').evaluateAll((elements, outputPath) => {
      const target = elements.find(element => {
        try { return new URL(element.getAttribute('src') || '', document.baseURI).pathname.replace(/^\/WOW-Encyclopedia-Deployable-Archive\//, '') === outputPath; } catch (_) { return false; }
      });
      if (target) target.scrollIntoView({ block: 'center', inline: 'nearest' });
    }, normalizePath(staticRows[0].served_output_path));
    const staticShot = inside(path.join(args.screenshots, 'v35-news2004-static-first.png'), BROWSER_DIR, 'static screenshot');
    fs.mkdirSync(path.dirname(staticShot), { recursive: true });
    await page.screenshot({ path: staticShot });
    report.screenshots.push(path.relative(ROOT, staticShot).replace(/\\/g, '/'));
    const nativeRow = nativeRows[0];
    if (!nativeRow || nativeRows.length !== 1) throw new Error(`expected one native target, got ${nativeRows.length}`);
    const nativePage = await openPage(page, origin + BASE_PATH, nativeRow.page_output);
    report.pages.push({ route: nativeRow.page_output, ...nativePage });
    const toggleId = nativeRow.native_toggle_ids[0];
    const entry = page.locator(`#${toggleId}`);
    if (await entry.count() !== 1) throw new Error(`missing native toggle #${toggleId}`);
    const toggle = entry.locator('.hoverContainer').first();
    if (await toggle.count() !== 1 || !(await toggle.isVisible())) throw new Error(`native toggle is not visible: #${toggleId}`);
    const initialClass = await entry.getAttribute('class');
    const transitions = [];
    const clickAndWait = async desired => {
      await toggle.click({ noWaitAfter: true });
      await waitForClass(page, toggleId, desired);
      transitions.push({ class: desired });
    };
    if (String(initialClass || '').split(/\s+/).includes('news-expand')) await clickAndWait('news-collapse');
    else await clickAndWait('news-expand');
    const afterFirst = await entry.getAttribute('class');
    if (!String(afterFirst || '').split(/\s+/).includes('news-expand')) await clickAndWait('news-expand');
    const finalClass = await entry.getAttribute('class');
    const nativeFacts = await inspectImages(page, nativeRow);
    report.native_toggle = { id: toggleId, initial_class: initialClass, transitions, final_class: finalClass, clicked: transitions.length > 0, image_facts: nativeFacts };
    const nativeShot = inside(path.join(args.screenshots, 'v35-beowulf-native-toggle.png'), BROWSER_DIR, 'native screenshot');
    await page.locator('img').evaluateAll((elements, outputPath) => {
      const target = elements.find(element => {
        try { return new URL(element.getAttribute('src') || '', document.baseURI).pathname.replace(/^\/WOW-Encyclopedia-Deployable-Archive\//, '') === outputPath; } catch (_) { return false; }
      });
      if (target) target.scrollIntoView({ block: 'center', inline: 'nearest' });
    }, normalizePath(nativeRow.served_output_path));
    await page.screenshot({ path: nativeShot });
    report.screenshots.push(path.relative(ROOT, nativeShot).replace(/\\/g, '/'));
    report.browser_executed = true;
  } catch (error) {
    report.errors.push(String(error && error.stack || error));
  } finally {
    report.local_requests = holder ? holder.getLocalRequests() : 0;
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
    await closeServer(holder && holder.server);
  }
  report.finished_utc = new Date().toISOString();
  const imageRequestByPath = new Map();
  for (const row of report.local_image_or_asset_requests) if (targetByPath.has(row.path) && !imageRequestByPath.has(row.path)) imageRequestByPath.set(row.path, row);
  const staticResults = report.target_results.filter(row => row.display_class === 'postContainer_static_no_toggle');
  const staticDomExact = staticResults.length === 23 && staticResults.every(row => row.facts.length >= Number(row.expected.references || 1) && row.facts.every(fact => JSON.stringify(fact.natural) === JSON.stringify(row.expected.dimensions) && fact.visible && !fact.decode_error));
  const staticHttpExact = staticRows.every(row => { const request = imageRequestByPath.get(normalizePath(row.served_output_path)); return !!request && request.status === 200 && request.exact; });
  const native = report.native_toggle;
  const nativeDomExact = !!native && native.clicked && String(native.final_class || '').split(/\s+/).includes('news-expand') && native.image_facts.length >= 1 && native.image_facts.every(fact => JSON.stringify(fact.natural) === JSON.stringify(nativeRows[0].dimensions) && fact.visible && !fact.decode_error);
  const nativeRequest = nativeRows[0] && imageRequestByPath.get(normalizePath(nativeRows[0].served_output_path));
  const nativeHttpExact = !!nativeRequest && nativeRequest.status === 200 && nativeRequest.exact;
  report.assertions = {
    target_count_24: targets.length === 24,
    static_target_count_23: staticRows.length === 23,
    native_target_count_1: nativeRows.length === 1,
    static_dom_images_exact: staticDomExact,
    static_http_images_exact: staticHttpExact,
    native_toggle_clicked_and_restored: nativeDomExact,
    native_http_image_exact: nativeHttpExact,
    external_requests_zero: report.external_requests.length === 0,
    page_errors_zero: report.page_errors.length === 0,
    request_failures_zero: report.request_failures.length === 0,
    server_errors_zero: report.server_errors.length === 0,
  };
  report.accepted = report.browser_executed && Object.values(report.assertions).every(Boolean);
  fs.mkdirSync(path.dirname(args.result), { recursive: true });
  fs.writeFileSync(args.result, JSON.stringify(report, null, 2) + '\n', 'utf8');
  process.stdout.write(JSON.stringify({ result: args.result, result_sha256: sha256File(args.result), accepted: report.accepted, assertions: report.assertions }) + '\n');
  if (!report.accepted) process.exitCode = 1;
}
main().catch(error => { console.error(error && error.stack || error); process.exitCode = 1; });
