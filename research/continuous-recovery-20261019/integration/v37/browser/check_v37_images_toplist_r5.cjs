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
const DEFAULT_RESULT = path.join(BROWSER_DIR, 'results/v37-browser-r5.json');
const DEFAULT_SCREENSHOTS = path.join(BROWSER_DIR, 'screenshots-r5');
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
  const args = { input: DEFAULT_INPUT, result: DEFAULT_RESULT, screenshots: DEFAULT_SCREENSHOTS, go: false, rootGo: false, preflight: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--input') args.input = path.resolve(argv[++i]);
    else if (arg === '--result') args.result = path.resolve(argv[++i]);
    else if (arg === '--screenshots') args.screenshots = path.resolve(argv[++i]);
    else if (arg === '--go') args.go = true;
    else if (arg === '--root-browser-go') args.rootGo = true;
    else if (arg === '--preflight') args.preflight = true;
    else throw new Error(`unknown argument: ${arg}`);
  }
  if (args.preflight ? (args.go || args.rootGo) : (!args.go || !args.rootGo)) throw new Error(args.preflight ? 'preflight cannot include browser execution flags' : 'browser execution requires --go --root-browser-go');
  args.input = inside(args.input, path.dirname(BROWSER_DIR), 'browser plan');
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
function canonicalOutputPath(raw, base = 'http://127.0.0.1/') {
  try {
    const parsed = new URL(raw || '', base);
    let value = parsed.pathname;
    try { value = decodeURIComponent(value); } catch (_) { /* preserve encoded evidence */ }
    const marker = value.indexOf(BASE_PATH);
    return normalizePath(marker >= 0 ? value.slice(marker + BASE_PATH.length) : value);
  } catch (_) { return ''; }
}
function targetOutputPath(original) {
  return canonicalOutputPath(original, 'http://www.worldofwarcraft.com/');
}
function backgroundContainsOutputPath(raw, expectedPath, base = 'http://127.0.0.1/') {
  if (!expectedPath || !raw || raw === 'none') return false;
  for (const match of String(raw).matchAll(/url\((?:"|')?([^"')]+)(?:"|')?\)/gi)) {
    if (canonicalOutputPath(match[1], base) === expectedPath) return true;
  }
  return false;
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
function latestRequest(report, outputPath) {
  const wanted = normalizePath(outputPath);
  for (let index = report.server_requests.length - 1; index >= 0; index -= 1) {
    if (normalizePath(report.server_requests[index].path) === wanted && report.server_requests[index].status === 200) return report.server_requests[index];
  }
  return null;
}
function assetHttpAssertion(report, outputPath, expected) {
  const request = latestRequest(report, outputPath);
  if (!request || !expected) return { exact: false, request, expected: expected || null };
  const expectedMime = String(expected.mime || '').toLowerCase().split(';')[0];
  const actualMime = String(request.mime || '').toLowerCase().split(';')[0];
  return {
    exact: request.status === 200 && request.length === Number(expected.derived_length) && request.sha256 === expected.derived_sha256 && actualMime === expectedMime,
    request,
    expected: { length: Number(expected.derived_length), sha256: expected.derived_sha256, mime: expectedMime },
    mime_exact: actualMime === expectedMime,
    length_exact: request.length === Number(expected.derived_length),
    sha256_exact: request.sha256 === expected.derived_sha256,
  };
}
async function inspectNews(page, origin, targets, expectedByPath, report) {
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
  }, wanted);
  const facts = [];
  for (const target of targets) {
    const outputPath = normalizePath(target.served_output_path);
    const probe = await probeAsset(page, origin, outputPath);
    const matches = dom[outputPath] || [];
    const visible = matches.some(row => row.visible);
    const http = assetHttpAssertion(report, outputPath, expectedByPath.get(outputPath));
    const naturalExact = matches.some(row => Array.isArray(row.natural) && row.natural[0] > 0 && row.natural[1] > 0 && Array.isArray(target.dimensions) && row.natural[0] === Number(target.dimensions[0]) && row.natural[1] === Number(target.dimensions[1]));
    const domPass = matches.some(row => row.visible && row.complete && !row.decode_error && Array.isArray(row.natural) && row.natural[0] > 0 && row.natural[1] > 0 && Array.isArray(target.dimensions) && row.natural[0] === Number(target.dimensions[0]) && row.natural[1] === Number(target.dimensions[1]));
    const assetPass = http.exact && probe.loaded && !probe.decode_error && Array.isArray(probe.natural) && probe.natural[0] === Number(target.dimensions[0]) && probe.natural[1] === Number(target.dimensions[1]);
    const status = assetPass && domPass ? 'passed' : (assetPass ? 'asset_http_passed_dom_pending' : 'failed_asset_http');
    facts.push({ original: target.original, output_path: outputPath, expected_length: target.length, expected_dimensions: target.dimensions, asset_probe: probe, http_assertion: http, dom_matches: matches, dom_pass: domPass, status });
  }
  return facts;
}
async function collectToplistState(page) {
  return page.evaluate(() => {
    const visible = element => {
      if (!element) return false;
      const style = getComputedStyle(element), rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
    };
    const pathOf = raw => { try { return new URL(raw || '', document.baseURI).pathname; } catch (_) { return ''; } };
    const row = element => {
      const rect = element.getBoundingClientRect();
      return { href: element.href || null, text: (element.innerText || '').trim().slice(0, 160), background_image: getComputedStyle(element).backgroundImage || 'none', rect: [rect.width, rect.height], visible: visible(element) };
    };
    const body = document.body;
    const stats = document.querySelector('#stats');
    const spells = document.spells || null;
    const errorNodes = Array.from(document.querySelectorAll('*')).filter(element => {
      const id = String(element.id || '').toLowerCase();
      const classes = String(element.className || '').toLowerCase();
      return (id.includes('error') || classes.split(/\s+/).includes('error')) && visible(element);
    }).slice(0, 20).map(element => ({ id: element.id || null, class_name: element.className || null, text: (element.innerText || '').trim().slice(0, 300) }));
    const css = ['body.wide a.next', 'body.wide a.prev'].map(selector => {
      const elements = Array.from(document.querySelectorAll(selector));
      return { selector, matches: elements.length, visible: elements.filter(visible).length, rows: elements.map(row) };
    });
    return {
      ready_state: document.readyState,
      runtime: {
        typeof_Prototype: typeof window.Prototype,
        Prototype_Version: window.Prototype ? String(window.Prototype.Version || '') : null,
        typeof_init: typeof window.init,
        onload_source_present: typeof window.onload === 'function',
      },
      body_class: body ? body.className : null,
      body_wide: !!body && body.classList.contains('wide'),
      title: document.title,
      text_length: body ? (body.innerText || '').length : 0,
      text_excerpt: body ? (body.innerText || '').trim().slice(0, 1200) : '',
      data_state: spells ? {
        layout_type: spells.layoutType ?? null,
        page_length: spells.pageLength ?? null,
        num_of_tables: spells.numOfTables ?? null,
        active_tables: spells.activeTables ?? null,
        search_pattern: spells.searchPattern ?? null,
        search_matches: spells.searchMatches ?? null,
        data_keys: spells.data && typeof spells.data === 'object' ? Object.keys(spells.data).length : null,
      } : null,
      containers: {
        info: { exists: !!document.querySelector('#infoContainer'), visible: visible(document.querySelector('#infoContainer')) },
        intro: { exists: !!document.querySelector('#intro'), visible: visible(document.querySelector('#intro')), text: (document.querySelector('#intro')?.innerText || '').trim().slice(0, 300) },
        stats: { exists: !!stats, visible: visible(stats), rows: stats ? stats.querySelectorAll('tr').length : 0, ranking_tables: stats ? stats.querySelectorAll('table.statsTable').length : 0, text: (stats?.innerText || '').trim().slice(0, 500) },
        search_info: { exists: !!document.querySelector('#searchInfo'), visible: visible(document.querySelector('#searchInfo')), text: (document.querySelector('#searchInfo')?.innerText || '').trim() },
        query_info: { exists: !!document.querySelector('#queryInfo'), visible: visible(document.querySelector('#queryInfo')), text: (document.querySelector('#queryInfo')?.innerText || '').trim().slice(0, 500) },
        error_nodes: errorNodes,
      },
      navigation: {
        next: (() => { const node = Array.from(document.querySelectorAll('body.wide a.next')).find(visible); return node ? row(node) : { visible: false, matches: document.querySelectorAll('body.wide a.next').length }; })(),
        prev: (() => { const node = Array.from(document.querySelectorAll('body.wide a.prev')).find(visible); return node ? row(node) : { visible: false, matches: document.querySelectorAll('body.wide a.prev').length }; })(),
      },
      links: Array.from(document.querySelectorAll('a[href]')).slice(0, 80).map(element => ({ text: (element.innerText || '').trim().slice(0, 120), href: element.getAttribute('href'), visible: visible(element) })),
      scripts: Array.from(document.querySelectorAll('script[src]')).map(script => ({ src: script.src, path: pathOf(script.src) })),
      css_candidates: css,
      hidden_lion_top_matches: document.querySelectorAll('#lion-top').length,
    };
  });
}
function findCssLocalAsset(outputRoot, target) {
  const cssPath = path.join(outputRoot, 'toplist/includes-client/css/styles-en.css');
  const expectedPath = targetOutputPath(target.original);
  if (!fs.existsSync(cssPath)) return { css_path: cssPath, local_path: null, raw: null, expected_output_path: expectedPath, exact_target_url: false, error: 'stylesheet missing' };
  const text = fs.readFileSync(cssPath, 'utf8');
  const observed = [];
  for (const match of text.matchAll(/url\((?:"|')?([^"')]+)(?:"|')?\)/gi)) {
    const raw = match[1];
    const outputPath = canonicalOutputPath(raw);
    observed.push({ raw, output_path: outputPath });
    if (outputPath === expectedPath) {
      return { css_path: cssPath, local_path: expectedPath, raw, expected_output_path: expectedPath, exact_target_url: true, observed_output_paths: observed };
    }
  }
  return { css_path: cssPath, local_path: null, raw: null, expected_output_path: expectedPath, exact_target_url: false, observed_output_paths: observed, error: 'exact project-relative target URL absent from derived stylesheet' };
}
async function inspectToplist(page, origin, plan, expectedByPath, outputRoot, report) {
  const pageLoad = await gotoPage(page, origin, 'toplist/index.html');
  const initial = await collectToplistState(page);
  const transitions = [];
  if (initial.navigation.next && initial.navigation.next.visible) {
    try {
      await page.locator('body.wide a.next:visible').first().click({ timeout: 5000 });
      await page.waitForTimeout(700);
      const afterNext = await collectToplistState(page);
      transitions.push({ action: 'next', state: afterNext });
      if (afterNext.navigation.prev && afterNext.navigation.prev.visible) {
        await page.locator('body.wide a.prev:visible').first().click({ timeout: 5000 });
        await page.waitForTimeout(700);
        transitions.push({ action: 'prev', state: await collectToplistState(page) });
      }
    } catch (error) {
      transitions.push({ action: 'next_then_prev', error: String(error && error.stack || error) });
    }
  } else {
    transitions.push({ action: 'next_then_prev', status: 'pending_no_visible_next_control' });
  }
  const css = [];
  for (const target of plan.toplist.css_targets || []) {
    const local = findCssLocalAsset(outputRoot, target);
    let localProbe = null;
    let http = null;
    if (local.local_path) {
      localProbe = await probeAsset(page, origin, local.local_path);
      http = assetHttpAssertion(report, local.local_path, expectedByPath.get(normalizePath(local.local_path)));
    }
    const candidate = initial.css_candidates.find(row => row.selector === target.references?.[0]?.selector || row.selector === (target.original.includes('next-wide') ? 'body.wide a.next' : 'body.wide a.prev')) || null;
    const expectedPath = targetOutputPath(target.original);
    const exactBackgroundRows = candidate ? candidate.rows.filter(row => row.visible && backgroundContainsOutputPath(row.background_image, expectedPath)) : [];
    const visibleEntry = exactBackgroundRows.length > 0;
    const decodedLocal = !!localProbe && localProbe.loaded && !localProbe.decode_error && !!http && http.exact;
    css.push({ original: target.original, target_output_path: expectedPath, source_page: target.source_page, references: target.references, local_asset: local, local_probe: localProbe, http_assertion: http, exact_background_matches: exactBackgroundRows, visible_entry: visibleEntry, status: visibleEntry && decodedLocal ? 'passed_visible_decoded' : (decodedLocal ? 'pending_no_exact_visible_entry' : (local.exact_target_url ? 'pending_local_asset_or_decode' : 'pending_no_exact_stylesheet_target_reference')) });
  }
  const expected_scripts = ['toplist/includes-client/js/prototype.js', 'toplist/includes-client/js/logic.js'].map(outputPath => ({ output_path: outputPath, provenance: expectedByPath.get(outputPath) || null, http_assertion: assetHttpAssertion(report, outputPath, expectedByPath.get(outputPath)) }));
  return { page: pageLoad, initial, transitions, css_candidates: css, expected_scripts, script_runtime: initial.runtime, data_and_error_state: { data_state: initial.data_state, containers: initial.containers }, navigation_exercised: transitions.some(row => row.action === 'next') };
}
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const plan = readJson(args.input, 'v37 browser plan');
  if (args.preflight) {
    if (plan.status !== 'prepared_waiting_root_v37_browser_go') throw new Error('v37 browser plan is not waiting for root browser GO');
    if (plan.network_requests !== 0 || plan.export_executed !== true) throw new Error('v37 browser plan output/export gate failed');
    if (plan.scope?.new_image_target_count !== 21 || plan.scope?.css_target_count !== 2 || plan.scope?.native_toggle_target_count !== 0) throw new Error('v37 browser plan coverage gate failed');
    process.stdout.write(JSON.stringify({
      status: 'preflight_passed',
      input: { path: args.input, absolute: path.isAbsolute(args.input), sha256: sha256File(args.input) },
      result: { path: args.result, absolute: path.isAbsolute(args.result), inside_browser_dir: args.result === BROWSER_DIR || args.result.startsWith(BROWSER_DIR + path.sep) },
      screenshots: { path: args.screenshots, absolute: path.isAbsolute(args.screenshots), inside_browser_dir: args.screenshots === BROWSER_DIR || args.screenshots.startsWith(BROWSER_DIR + path.sep) },
      browser_started: false,
      server_started: false,
      network_requests: 0,
    }));
    return;
  }
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
    schema: 'wow-recovery.integration.v37-browser-result-r5.v1', status: 'running', started_utc: new Date().toISOString(),
    input: { path: path.relative(ROOT, args.input).replace(/\\/g, '/'), sha256: sha256File(args.input) },
    output: { path: '.scratch/pages-resources-20261019-v37', provenance_sha256: sha256File(provenancePath), actual_files: 9114 },
    coverage: { news_targets: targets.length, css_targets: plan.scope.css_target_count, toplist_pages: 1, native_toggle_targets: 0 },
    asset_requests: [], server_requests: [], server_errors: [], external_requests: [], page_errors: [], console_errors: [], screenshots: [],
    news: null, toplist: null, assertions: null,
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
    report.news = { page: newsLoad, facts: await inspectNews(newsPage, origin, targets, expectedByPath, report) };
    const first = report.news.facts.find(row => row.dom_matches.some(match => match.visible));
    if (first) { await newsPage.evaluate(outputPath => { const wanted = String(outputPath).replace(/^\/+/, ''); const node = Array.from(document.querySelectorAll('img')).find(img => { try { const p = new URL(img.currentSrc || img.src, document.baseURI).pathname; return p.endsWith('/' + wanted); } catch (_) { return false; } }); if (node) node.scrollIntoView({ block: 'center', inline: 'nearest' }); }, first.output_path); }
    const newsShot = path.join(args.screenshots, 'v37-news-static-r5.png'); await newsPage.screenshot({ path: newsShot, type: 'png' }); report.screenshots.push({ path: path.relative(ROOT, newsShot).replace(/\\/g, '/'), sha256: sha256File(newsShot) });
    await newsPage.close();
    const toplistPage = await context.newPage();
    toplistPage.on('pageerror', error => report.page_errors.push({ page: 'toplist', message: String(error && error.message || error), stack: String(error && error.stack || '') }));
    toplistPage.on('console', msg => { if (msg.type() === 'error') report.console_errors.push({ page: 'toplist', text: msg.text() }); });
    report.toplist = await inspectToplist(toplistPage, origin, plan, expectedByPath, outputRoot, report);
    const topShot = path.join(args.screenshots, 'v37-toplist-r5.png'); await toplistPage.screenshot({ path: topShot, type: 'png' }); report.screenshots.push({ path: path.relative(ROOT, topShot).replace(/\\/g, '/'), sha256: sha256File(topShot) });
    await toplistPage.close(); await context.close();
    report.local_requests = report.server_requests.length;
    const newsAssetHttpPass = report.news.facts.every(row => row.http_assertion && row.http_assertion.exact && row.asset_probe.loaded && !row.asset_probe.decode_error && Array.isArray(row.asset_probe.natural) && row.asset_probe.natural[0] === Number(row.expected_dimensions[0]) && row.asset_probe.natural[1] === Number(row.expected_dimensions[1]));
    const newsDomPass = report.news.facts.every(row => row.dom_pass === true);
    const cssAssetPass = report.toplist.css_candidates.every(row => row.local_asset && row.local_asset.exact_target_url === true && row.local_probe && row.local_probe.loaded && !row.local_probe.decode_error && row.http_assertion && row.http_assertion.exact);
    const runtime = report.toplist.script_runtime || {};
    const toplistRuntimePass = report.toplist.page && report.toplist.page.status === 200 && runtime.typeof_Prototype === 'object' && runtime.typeof_init === 'function' && report.toplist.initial && report.toplist.initial.body_wide === true;
    const noErrors = report.external_requests.length === 0 && report.server_errors.length === 0 && report.page_errors.length === 0 && report.console_errors.length === 0;
    const pending = {
      news_dom_rows: report.news.facts.filter(row => !row.dom_pass).map(row => ({ original: row.original, output_path: row.output_path, status: row.status })),
      css_visibility: report.toplist.css_candidates.filter(row => row.status !== 'passed_visible_decoded').map(row => ({ original: row.original, target_output_path: row.target_output_path, status: row.status, exact_stylesheet_target_url: !!row.local_asset?.exact_target_url, visible_entry: row.visible_entry, exact_background_matches: row.exact_background_matches })),
      toplist_data: report.toplist.initial.containers.stats.rows === 0 || report.toplist.initial.data_state === null ? [{ stats_rows: report.toplist.initial.containers.stats.rows, data_state: report.toplist.initial.data_state }] : [],
      toplist_navigation: report.toplist.transitions.some(row => row.action === 'next') ? [] : [{ status: 'not_exercised', reason: 'no visible body.wide a.next control' }],
    };
    const mandatory = { new_assets_exact_http_mime_dimensions: newsAssetHttpPass, news_dom_visible_complete_decoded_dimensions: newsDomPass, toplist_runtime_init_default_wide: toplistRuntimePass, css_files_local_get_decode: cssAssetPass, external_requests_zero: report.external_requests.length === 0, server_errors_zero: report.server_errors.length === 0, page_and_console_errors_zero: report.page_errors.length === 0 && report.console_errors.length === 0 };
    const mandatoryPass = Object.values(mandatory).every(Boolean);
    const pendingCount = Object.values(pending).reduce((sum, value) => sum + value.length, 0);
    report.assertions = { mandatory, mandatory_pass: mandatoryPass, pending, pending_count: pendingCount, overall: mandatoryPass && pendingCount === 0 ? 'passed' : (mandatoryPass ? 'completed_with_pending' : 'completed_with_mandatory_failures'), note: 'A zero-error result does not override pending DOM/CSS/data rows.' };
    report.status = mandatoryPass && pendingCount === 0 ? 'completed_passed' : (mandatoryPass ? 'completed_with_pending' : 'completed_with_failures');
  } finally {
    if (browser) await browser.close().catch(() => {});
    await closeServer(server);
  }
  report.finished_utc = new Date().toISOString();
  fs.writeFileSync(args.result, JSON.stringify(report, null, 2) + '\n', 'utf8');
  process.stdout.write(JSON.stringify({ status: report.status, result: args.result, target_count: targets.length, external_requests: report.external_requests.length, page_errors: report.page_errors.length, server_errors: report.server_errors.length }));
}
main().catch(error => { process.stderr.write(String(error && error.stack || error)); process.exitCode = 1; });
