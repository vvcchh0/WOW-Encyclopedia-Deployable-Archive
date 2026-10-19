/*
 * Bounded, loopback-only v37 browser check.
 *
 * This harness is prepared for a later root browser GO. It checks the 21 new
 * image overlays on their real news page and checks the real Toplist init,
 * ranking/navigation DOM, and two wide-layout CSS candidates. It never
 * reveals hidden DOM or injects controls. Every local asset probe is compared
 * with the frozen v37 provenance record; unresolved DOM/CSS rows remain
 * explicit in the result.
 */
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../../..');
const BROWSER_DIR = path.resolve(__dirname);
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const DEFAULT_INPUT = path.join(BROWSER_DIR, '..', 'v37-browser-plan-r2.json');
const DEFAULT_RESULT = path.join(BROWSER_DIR, 'results/v37-browser-r1.json');
const DEFAULT_SCREENSHOTS = path.join(BROWSER_DIR, 'screenshots-r1');
const OUTPUT_ROOT = path.join(ROOT, '.scratch/pages-resources-20261019-v37');

function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function sha256File(file) { return sha256(fs.readFileSync(file)); }
function normalizePath(value) { return String(value || '').replace(/^\/+/, '').replace(/\\/g, '/'); }
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
  args.input = inside(args.input, BROWSER_DIR.parent, 'browser plan');
  args.result = inside(args.result, BROWSER_DIR, 'browser result');
  args.screenshots = inside(args.screenshots, BROWSER_DIR, 'screenshots');
  if (fs.existsSync(args.result)) throw new Error(`refusing existing browser result: ${args.result}`);
  return args;
}
function outputUrl(origin, outputPath) {
  const encoded = normalizePath(outputPath).split('/').map(part => encodeURIComponent(part)).join('/');
  return `${origin}${BASE_PATH}${encoded}`;
}
function pathFromUrl(raw, base = 'http://127.0.0.1/') {
  try {
    const value = new URL(raw || '', base).pathname;
    const marker = value.indexOf(BASE_PATH);
    return normalizePath(marker >= 0 ? value.slice(marker + BASE_PATH.length) : value);
  } catch (_) { return ''; }
}
function createServer(outputRoot, expectedByPath, report) {
  const server = http.createServer((request, response) => {
    try {
      const requestUrl = new URL(request.url || '/', 'http://127.0.0.1');
      if (!requestUrl.pathname.startsWith(BASE_PATH) || !['GET', 'HEAD'].includes(request.method)) {
        response.writeHead(404); return response.end();
      }
      const relative = normalizePath(decodeURIComponent(requestUrl.pathname.slice(BASE_PATH.length)));
      if (!relative || relative.includes('\\') || relative.includes('\0') || relative.split('/').includes('..')) {
        response.writeHead(400); return response.end();
      }
      const file = inside(path.join(outputRoot, relative), outputRoot, 'output request');
      if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
        report.server_requests.push({ path: relative, method: request.method, status: 404 });
        response.writeHead(404); return response.end();
      }
      const body = fs.readFileSync(file);
      const expected = expectedByPath.get(relative);
      const actualSha = sha256(body);
      const requestRecord = { path: relative, method: request.method, status: 200, mime: mime(file), length: body.length, sha256: actualSha };
      if (expected) {
        requestRecord.expected_sha256 = expected.derived_sha256;
        requestRecord.expected_length = expected.derived_length;
        requestRecord.exact = actualSha === expected.derived_sha256 && body.length === Number(expected.derived_length);
      }
      report.server_requests.push(requestRecord);
      response.writeHead(200, { 'Content-Type': mime(file), 'Content-Length': body.length, 'Cache-Control': 'no-store' });
      if (request.method === 'HEAD') return response.end();
      response.end(body);
    } catch (error) {
      report.server_errors.push(String(error && error.stack || error));
      response.writeHead(400); response.end();
    }
  });
  return server;
}
async function listen(server) {
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  return `http://127.0.0.1:${server.address().port}`;
}
async function closeServer(server) { if (server) await new Promise(resolve => server.close(() => resolve())); }
async function gotoPage(page, origin, outputPath) {
  const url = outputUrl(origin, outputPath);
  try {
    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(350);
    return { url, status: response && response.status(), content_type: response && response.headers()['content-type'] || null, error: null };
  } catch (error) {
    return { url, status: null, content_type: null, error: String(error && error.stack || error) };
  }
}
async function probeAsset(page, origin, outputPath) {
  const url = outputUrl(origin, outputPath);
  return page.evaluate(async targetUrl => new Promise(resolve => {
    const image = new Image();
    let settled = false;
    const finish = value => { if (!settled) { settled = true; resolve(value); } };
    const timer = setTimeout(() => finish({ url: targetUrl, loaded: false, natural: [image.naturalWidth, image.naturalHeight], error: 'probe timeout' }), 12000);
    image.onload = async () => {
      clearTimeout(timer);
      let decodeError = null;
      try { await image.decode(); } catch (error) { decodeError = String(error && error.message || error); }
      finish({ url: targetUrl, loaded: true, natural: [image.naturalWidth, image.naturalHeight], complete: image.complete, decode_error: decodeError });
    };
    image.onerror = () => { clearTimeout(timer); finish({ url: targetUrl, loaded: false, natural: [image.naturalWidth, image.naturalHeight], error: 'image error' }); };
    image.src = targetUrl;
  }), url);
}
async function inspectNews(page, origin, targets) {
  const wanted = targets.map(target => ({ path: normalizePath(target.served_output_path), original: target.original }));
  const dom = await page.evaluate(async rows => {
    const wanted = new Map(rows.map(row => [row.path, row]));
    const pathname = raw => {
      try {
        const value = new URL(raw || '', document.baseURI).pathname;
        const marker = value.indexOf('/WOW-Encyclopedia-Deployable-Archive/');
        return String(marker >= 0 ? value.slice(marker + '/WOW-Encyclopedia-Deployable-Archive/'.length) : value).replace(/^\/+/, '').replace(/\\/g, '/');
      } catch (_) { return ''; }
    };
    const visible = element => {
      const style = getComputedStyle(element), rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
    };
    const selector = element => {
      const tag = element.tagName.toLowerCase();
      const id = element.id ? `#${element.id}` : '';
      const classes = String(element.className || '').split(/\s+/).filter(Boolean).slice(0, 3).map(value => `.${value}`).join('');
      return `${tag}${id}${classes}`;
    };
    const facts = new Map(rows.map(row => [row.path, []]));
    for (const element of Array.from(document.querySelectorAll('img'))) {
      const source = element.currentSrc || element.getAttribute('src') || '';
      const targetPath = pathname(source);
      if (!wanted.has(targetPath)) continue;
      let decodeError = null;
      try { await element.decode(); } catch (error) { decodeError = String(error && error.message || error); }
      const rect = element.getBoundingClientRect();
      const figure = element.closest('figure');
      facts.get(targetPath).push({
        kind: 'img', selector: selector(element), src: source, current_src: element.currentSrc || null,
        natural: [element.naturalWidth, element.naturalHeight], complete: !!element.complete,
        decode_error: decodeError, visible: visible(element), box: [rect.width, rect.height],
        figure: !!figure, figcaption: figure ? String(figure.querySelector('figcaption')?.textContent || '').trim() : null,
      });
    }
    return Object.fromEntries(Array.from(facts.entries()));
  });
  const facts = [];
  for (const target of targets) {
    const outputPath = normalizePath(target.served_output_path);
    const probe = await probeAsset(page, origin, outputPath);
    const matches = dom[outputPath] || [];
    const visible = matches.some(row => row.visible);
    const status = probe.loaded && !probe.decode_error && visible ? 'passed' : (probe.loaded && !probe.decode_error ? 'asset_only_pending_dom' : 'failed');
    facts.push({ original: target.original, output_path: outputPath, expected_length: target.length, expected_dimensions: target.dimensions, asset_probe: probe, dom_matches: matches, status });
  }
  return facts;
}
async function inspectToplist(page, origin, plan, expectedByPath) {
  const pageLoad = await gotoPage(page, origin, 'toplist/index.html');
  const dom = await page.evaluate(async () => {
    const visible = element => {
      const style = getComputedStyle(element), rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
    };
    const pathOf = raw => {
      try { return new URL(raw || '', document.baseURI).pathname; } catch (_) { return ''; }
    };
    const body = document.body;
    const css = [];
    for (const selector of ['body.wide a.next', 'body.wide a.prev']) {
      const elements = Array.from(document.querySelectorAll(selector));
      css.push({ selector, matches: elements.length, visible: elements.filter(visible).length, rows: elements.map(element => ({ href: element.href || null, background_image: getComputedStyle(element).backgroundImage || 'none', rect: (() => { const r = element.getBoundingClientRect(); return [r.width, r.height]; })(), visible: visible(element) })) });
    }
    return {
      ready_state: document.readyState,
      body_class: body ? body.className : null,
      body_wide: !!body && body.classList.contains('wide'),
      title: document.title,
      text_length: body ? (body.innerText || '').length : 0,
      text_excerpt: body ? (body.innerText || '').trim().slice(0, 1200) : '',
      links: Array.from(document.querySelectorAll('a[href]')).slice(0, 80).map(a => ({ text: (a.innerText || '').trim().slice(0, 120), href: a.getAttribute('href'), visible: visible(a) })),
      scripts: Array.from(document.querySelectorAll('script[src]')).map(script => ({ src: script.src, path: pathOf(script.src) })),
      css_candidates: css,
      hidden_lion_top_matches: document.querySelectorAll('#lion-top').length,
    };
  });
  const css = [];
  for (const row of dom.css_candidates) {
    const elements = row.rows.filter(item => item.visible && item.background_image && item.background_image !== 'none');
    const assetRows = [];
    for (const element of elements) {
      const match = /url\((?:"|')?([^"')]+)(?:"|')?\)/i.exec(element.background_image);
      if (!match) { assetRows.push({ ...element, status: 'visible_without_decodable_url' }); continue; }
      const outputPath = pathFromUrl(match[1], `${origin}/`);
      const probe = outputPath ? await probeAsset(page, origin, outputPath) : { loaded: false, error: 'background is not local' };
      assetRows.push({ ...element, output_path: outputPath || null, probe, status: probe.loaded && !probe.decode_error ? 'visible_decoded' : 'visible_pending_decode' });
    }
    css.push({ selector: row.selector, matches: row.matches, visible: row.visible, rows: assetRows, status: assetRows.some(item => item.status === 'visible_decoded') ? 'passed' : 'pending_real_visible_decode' });
  }
  return { page: pageLoad, dom: { ...dom, css_candidates: css }, expected_scripts: ['toplist/includes-client/js/prototype.js', 'toplist/includes-client/js/logic.js'].map(outputPath => ({ output_path: outputPath, provenance: expectedByPath.get(outputPath) || null })) };
}
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const plan = readJson(args.input, 'v37 browser plan');
  if (plan.status !== 'prepared_waiting_root_v37_browser_go') throw new Error('v37 browser plan is not waiting for root browser GO');
  if (plan.network_requests !== 0 || plan.export_executed !== true) throw new Error('v37 browser plan output/export gate failed');
  if (plan.scope?.new_image_target_count !== 21 || plan.scope?.css_target_count !== 2 || plan.scope?.native_toggle_target_count !== 0) throw new Error('v37 browser plan coverage gate failed');
  const provenancePath = path.join(ROOT, '.scratch/pages-resources-20261019-v37/export-provenance.json');
  const provenance = readJson(provenancePath, 'v37 provenance');
  if (plan.output_provenance?.sha256 && sha256File(provenancePath) !== plan.output_provenance.sha256) throw new Error('v37 provenance SHA differs from browser plan');
  const outputRoot = inside(OUTPUT_ROOT, path.join(ROOT, '.scratch'), 'v37 output');
  if (!fs.existsSync(outputRoot)) throw new Error(`missing v37 output: ${outputRoot}`);
  const expectedByPath = new Map((provenance.files || []).map(row => [normalizePath(row.output_path), row]));
  const targets = plan.targets || [];
  if (targets.length !== 21) throw new Error(`expected 21 targets, found ${targets.length}`);
  const report = {
    schema: 'wow-recovery.integration.v37-browser-result.v1', status: 'running', started_utc: new Date().toISOString(),
    input: { path: path.relative(ROOT, args.input).replace(/\\/g, '/'), sha256: sha256File(args.input) },
    output: { path: '.scratch/pages-resources-20261019-v37', provenance_sha256: sha256File(provenancePath), actual_files: 9114 },
    coverage: { news_targets: targets.length, css_targets: plan.scope.css_target_count, toplist_pages: 1, native_toggle_targets: 0 },
    asset_requests: [], server_requests: [], server_errors: [], external_requests: [], page_errors: [], console_errors: [], screenshots: [],
    news: null, toplist: null,
  };
  fs.mkdirSync(path.dirname(args.result), { recursive: true }); fs.mkdirSync(args.screenshots, { recursive: true });
  let server = null, browser = null;
  try {
    server = createServer(outputRoot, expectedByPath, report);
    const origin = await listen(server);
    report.origin = origin;
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1365, height: 900 } });
    await context.route('**/*', async route => {
      const requestUrl = new URL(route.request().url());
      const allowed = requestUrl.hostname === '127.0.0.1' && Number(requestUrl.port) === Number(new URL(origin).port);
      if (!allowed && !['data:', 'blob:'].includes(requestUrl.protocol)) {
        report.external_requests.push({ url: route.request().url(), resource_type: route.request().resourceType(), method: route.request().method() });
        return route.abort();
      }
      return route.continue();
    });
    const newsPage = await context.newPage();
    newsPage.on('pageerror', error => report.page_errors.push({ page: 'news', message: String(error && error.message || error), stack: String(error && error.stack || '') }));
    newsPage.on('console', msg => { if (msg.type() === 'error') report.console_errors.push({ page: 'news', text: msg.text() }); });
    const newsLoad = await gotoPage(newsPage, origin, 'news/wow-news2004.html');
    report.news = { page: newsLoad, facts: await inspectNews(newsPage, origin, targets) };
    const first = report.news.facts.find(row => row.dom_matches.some(match => match.visible));
    if (first) { await newsPage.evaluate(outputPath => { const wanted = String(outputPath).replace(/^\/+/, ''); const node = Array.from(document.querySelectorAll('img')).find(img => { try { const p = new URL(img.currentSrc || img.src, document.baseURI).pathname; return p.endsWith('/' + wanted); } catch (_) { return false; } }); if (node) node.scrollIntoView({ block: 'center', inline: 'nearest' }); }, first.output_path); }
    const newsShot = path.join(args.screenshots, 'v37-news-static.png'); await newsPage.screenshot({ path: newsShot, type: 'png' }); report.screenshots.push({ path: path.relative(ROOT, newsShot).replace(/\\/g, '/'), sha256: sha256File(newsShot) });
    await newsPage.close();
    const toplistPage = await context.newPage();
    toplistPage.on('pageerror', error => report.page_errors.push({ page: 'toplist', message: String(error && error.message || error), stack: String(error && error.stack || '') }));
    toplistPage.on('console', msg => { if (msg.type() === 'error') report.console_errors.push({ page: 'toplist', text: msg.text() }); });
    report.toplist = await inspectToplist(toplistPage, origin, plan, expectedByPath);
    const topShot = path.join(args.screenshots, 'v37-toplist.png'); await toplistPage.screenshot({ path: topShot, type: 'png' }); report.screenshots.push({ path: path.relative(ROOT, topShot).replace(/\\/g, '/'), sha256: sha256File(topShot) });
    await toplistPage.close(); await context.close();
    report.local_requests = report.server_requests.length;
    report.status = report.external_requests.length === 0 && report.server_errors.length === 0 ? 'completed' : 'completed_with_failures';
  } finally {
    if (browser) await browser.close().catch(() => {});
    await closeServer(server);
  }
  report.finished_utc = new Date().toISOString();
  fs.writeFileSync(args.result, JSON.stringify(report, null, 2) + '\n', 'utf8');
  process.stdout.write(JSON.stringify({ status: report.status, result: args.result, target_count: targets.length, external_requests: report.external_requests.length, page_errors: report.page_errors.length, server_errors: report.server_errors.length }));
}
main().catch(error => { process.stderr.write(String(error && error.stack || error)); process.exitCode = 1; });
