/*
 * Bounded, loopback-only v38 browser check.
 *
 * This harness is prepared for a later root browser GO. It checks the 21 new
 * image overlays on their real news page and checks the real Toplist init,
 * ranking/navigation DOM, and two wide-layout CSS candidates. It never
 * reveals hidden DOM or injects controls. Every local asset probe is compared
 * with the v38 export provenance record; unresolved DOM/CSS rows remain
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
const DEFAULT_INPUT = path.join(BROWSER_DIR, '..', 'v38-browser-plan-r1.json');
const DEFAULT_RESULT = path.join(BROWSER_DIR, 'results/v38-browser-r1.json');
const DEFAULT_SCREENSHOTS = path.join(BROWSER_DIR, 'screenshots-r1');
const OUTPUT_ROOT = path.join(ROOT, '.scratch/pages-resources-20261019-v38');

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
function outputFileStats(root) {
  let count = 0, bytes = 0;
  const visit = directory => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, entry.name);
      if (entry.isDirectory()) visit(file);
      else if (entry.isFile()) { count += 1; bytes += fs.statSync(file).size; }
    }
  };
  visit(root);
  return { count, bytes };
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
      const requestRecord = { url: request.url || '/', path: requestUrl.pathname, method: request.method || null };
      if (!['GET', 'HEAD'].includes(request.method)) {
        report.server_requests.push({ ...requestRecord, status: 405, outside_base: !requestUrl.pathname.startsWith(BASE_PATH) });
        response.writeHead(405); return response.end();
      }
      if (!requestUrl.pathname.startsWith(BASE_PATH)) {
        report.server_requests.push({ ...requestRecord, status: 404, outside_base: true });
        response.writeHead(404); return response.end();
      }
      const relative = normalizePath(decodeURIComponent(requestUrl.pathname.slice(BASE_PATH.length)));
      if (!relative || relative.includes('\\') || relative.includes('\0') || relative.split('/').includes('..')) {
        report.server_requests.push({ ...requestRecord, path: relative, status: 400, outside_base: false });
        response.writeHead(400); return response.end();
      }
      const file = inside(path.join(outputRoot, relative), outputRoot, 'output request');
      if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
        report.server_requests.push({ ...requestRecord, path: relative, status: 404, outside_base: false });
        response.writeHead(404); return response.end();
      }
      const body = fs.readFileSync(file);
      const expected = expectedByPath.get(relative);
      const actualSha = sha256(body);
      const servedRecord = { ...requestRecord, path: relative, status: 200, mime: mime(file), length: body.length, sha256: actualSha, outside_base: false };
      if (expected) {
        servedRecord.expected_sha256 = expected.derived_sha256;
        servedRecord.expected_length = expected.derived_length;
        servedRecord.exact = actualSha === expected.derived_sha256 && body.length === Number(expected.derived_length);
      }
      report.server_requests.push(servedRecord);
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
    const ownDateKeys = spells && spells.data && typeof spells.data === 'object'
      ? Object.keys(spells.data).filter(key => Object.prototype.hasOwnProperty.call(spells.data, key) && /^\d{8}$/.test(key))
      : [];
    const daysSelector = document.querySelector('#numTablesSelect');
    const visibleNoData = Array.from(document.querySelectorAll('.noData')).filter(visible).map(element => ({
      selector: element.id ? `#${element.id}` : element.tagName.toLowerCase(),
      text: (element.innerText || '').trim().slice(0, 300),
    }));
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
        data_keys: ownDateKeys.length,
        date_data_keys: ownDateKeys,
        date_data_count: ownDateKeys.length,
        has_date_data: ownDateKeys.length > 0,
      } : null,
      days_selector: {
        exists: !!daysSelector,
        visible: visible(daysSelector),
        id: daysSelector ? daysSelector.id : null,
        value: daysSelector ? String(daysSelector.value || '') : null,
        options: daysSelector ? Array.from(daysSelector.options || []).map(option => ({ value: option.value, text: (option.textContent || '').trim() })) : [],
        onchange: daysSelector ? daysSelector.getAttribute('onchange') : null,
      },
      historical_missing_notice: {
        empty_table_count: stats ? stats.querySelectorAll('tbody.emptyTable').length : 0,
        visible_no_data: visibleNoData,
        known_limitation: ownDateKeys.length === 0 ? 'No own 8-digit date data keys observed; historical data and missing notices remain pending; emptyTable rows are not data.' : null,
      },
      containers: {
        info: { exists: !!document.querySelector('#infoContainer'), visible: visible(document.querySelector('#infoContainer')) },
        intro: { exists: !!document.querySelector('#intro'), visible: visible(document.querySelector('#intro')), text: (document.querySelector('#intro')?.innerText || '').trim().slice(0, 300) },
        stats: { exists: !!stats, visible: visible(stats), rows: stats ? stats.querySelectorAll('tr').length : 0, ranking_tables: stats ? stats.querySelectorAll('table.statsTable').length : 0, empty_tables: stats ? stats.querySelectorAll('tbody.emptyTable').length : 0, no_data: visibleNoData, text: (stats?.innerText || '').trim().slice(0, 500) },
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
  const daysSpec = plan.toplist?.days_selector || {};
  const daysTransitions = [];
  const observedOnchange = initial.days_selector?.onchange || null;
  const expectedOnchange = daysSpec.expected_onchange || null;
  if (initial.days_selector?.exists && initial.days_selector?.visible && observedOnchange === expectedOnchange) {
    try {
      const selector = page.locator('#numTablesSelect');
      await selector.selectOption('1');
      await page.waitForTimeout(350);
      daysTransitions.push({ action: 'days_initial_1', state: await collectToplistState(page) });
      await selector.selectOption('2');
      await page.waitForTimeout(700);
      daysTransitions.push({ action: 'days_1_to_2', state: await collectToplistState(page) });
      await selector.selectOption('1');
      await page.waitForTimeout(700);
      daysTransitions.push({ action: 'days_2_to_1', state: await collectToplistState(page) });
    } catch (error) {
      daysTransitions.push({ action: 'days_1_to_2_to_1', status: 'error', error: String(error && error.stack || error) });
    }
  } else {
    daysTransitions.push({
      action: 'days_1_to_2_to_1',
      status: initial.days_selector?.exists ? 'source_onchange_mismatch' : 'no_entry',
      expected_onchange: expectedOnchange,
      observed_onchange: observedOnchange,
    });
  }
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
    transitions.push({ action: 'next_then_prev', status: 'no_entry', reason: 'no visible body.wide a.next control' });
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
    const candidateHasVisibleDom = !!candidate && candidate.matches > 0 && candidate.visible > 0;
    const exactBackgroundRows = candidateHasVisibleDom ? candidate.rows.filter(row => row.visible && backgroundContainsOutputPath(row.background_image, expectedPath)) : [];
    const visibleEntry = exactBackgroundRows.length > 0;
    const decodedLocal = !!localProbe && localProbe.loaded && !localProbe.decode_error && !!http && http.exact;
    const status = !candidateHasVisibleDom
      ? 'no_entry'
      : (visibleEntry && decodedLocal ? 'passed_visible_decoded' : (decodedLocal ? 'pending_no_exact_visible_entry' : (local.exact_target_url ? 'pending_local_asset_or_decode' : 'pending_no_exact_stylesheet_target_reference')));
    css.push({ original: target.original, target_output_path: expectedPath, source_page: target.source_page, references: target.references, local_asset: local, local_probe: localProbe, http_assertion: http, exact_background_matches: exactBackgroundRows, visible_entry: visibleEntry, no_entry_reason: !candidateHasVisibleDom ? 'no visible body.wide next/prev DOM element; computed background was not used as evidence' : null, status });
  }
  const expected_scripts = ['toplist/includes-client/js/prototype.js', 'toplist/includes-client/js/logic.js'].map(outputPath => ({ output_path: outputPath, provenance: expectedByPath.get(outputPath) || null, http_assertion: assetHttpAssertion(report, outputPath, expectedByPath.get(outputPath)) }));
  const dayStates = daysTransitions.filter(row => row.state).map(row => ({ action: row.action, num_of_tables: row.state.data_state?.num_of_tables ?? null, empty_table_count: row.state.containers?.stats?.empty_tables ?? null, own_date_data_count: row.state.data_state?.date_data_count ?? null }));
  return { page: pageLoad, initial, transitions, days_selector_observation: { expected_onchange: expectedOnchange, observed_onchange: observedOnchange, source_match: observedOnchange === expectedOnchange, initial: initial.days_selector, transitions: daysTransitions, checks: { sequence: dayStates.map(row => row.action), num_of_tables: dayStates.map(row => row.num_of_tables), empty_table_counts: dayStates.map(row => row.empty_table_count), own_date_data_counts: dayStates.map(row => row.own_date_data_count), data_http_request_count: report.server_requests.filter(row => normalizePath(row.path).startsWith('toplist/data/')).length }, historical_missing_notice: initial.historical_missing_notice }, css_candidates: css, expected_scripts, script_runtime: initial.runtime, data_and_error_state: { data_state: initial.data_state, containers: initial.containers, historical_missing_notice: initial.historical_missing_notice }, navigation_exercised: transitions.some(row => row.action === 'next') };
}
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const plan = readJson(args.input, 'v38 browser plan');
  const scopePass = plan.scope?.new_image_target_count === 21
    && plan.scope?.css_target_count === 2
    && plan.scope?.toplist_page_target_count === 1
    && plan.scope?.toplist_script_target_count === 2
    && plan.scope?.native_toggle_target_count === 0;
  const templateStatus = plan.status === 'template_waiting_v38_export';
  const finalStatus = plan.status === 'prepared_waiting_root_v38_browser_go';
  if (args.preflight) {
    if (!templateStatus && !finalStatus) throw new Error('v38 browser plan is neither an export template nor waiting for root browser GO');
    if (plan.network_requests !== 0 || !scopePass) throw new Error('v38 browser plan network/scope gate failed');
    process.stdout.write(JSON.stringify({
      status: 'preflight_passed',
      input: { path: args.input, absolute: path.isAbsolute(args.input), sha256: sha256File(args.input) },
      result: { path: args.result, absolute: path.isAbsolute(args.result), inside_browser_dir: args.result === BROWSER_DIR || args.result.startsWith(BROWSER_DIR + path.sep) },
      screenshots: { path: args.screenshots, absolute: path.isAbsolute(args.screenshots), inside_browser_dir: args.screenshots === BROWSER_DIR || args.screenshots.startsWith(BROWSER_DIR + path.sep) },
      browser_started: false,
      server_started: false,
      network_requests: 0,
      template_waiting_for_export: templateStatus,
      output_provenance_sha256: plan.output_provenance?.sha256 || null,
    }));
    return;
  }
  if (!finalStatus) throw new Error('v38 browser plan is not waiting for root browser GO');
  if (plan.network_requests !== 0 || plan.export_executed !== true || !scopePass) throw new Error('v38 browser plan output/export/scope gate failed');
  if (!plan.output_provenance?.sha256) throw new Error('v38 browser plan lacks real export provenance SHA');
  const provenancePath = path.resolve(ROOT, plan.output_provenance.path || '.scratch/pages-resources-20261019-v38/export-provenance.json');
  const provenance = readJson(provenancePath, 'v38 provenance');
  if (sha256File(provenancePath) !== plan.output_provenance.sha256) throw new Error('v38 provenance SHA differs from browser plan');
  const outputRoot = inside(OUTPUT_ROOT, path.join(ROOT, '.scratch'), 'v38 output');
  if (!fs.existsSync(outputRoot)) throw new Error(`missing v38 output: ${outputRoot}`);
  const actualOutputStats = outputFileStats(outputRoot);
  const expectedByPath = new Map((provenance.files || []).map(row => [normalizePath(row.output_path), row]));
  const targets = plan.targets || [];
  if (targets.length !== 21) throw new Error(`expected 21 targets, found ${targets.length}`);
  const report = {
    schema: 'wow-recovery.integration.v38-browser-result-r1.v1', status: 'running', started_utc: new Date().toISOString(),
    input: { path: path.relative(ROOT, args.input).replace(/\\/g, '/'), sha256: sha256File(args.input) },
    output: { path: '.scratch/pages-resources-20261019-v38', provenance_sha256: sha256File(provenancePath), actual_files: actualOutputStats.count, tree_bytes: actualOutputStats.bytes, declared_files: provenance.stats?.output_files ?? provenance.files?.length ?? null },
    coverage: { news_targets: targets.length, css_targets: plan.scope.css_target_count, toplist_pages: plan.scope.toplist_page_target_count, native_toggle_targets: 0 },
    asset_requests: [], server_requests: [], server_errors: [], external_requests: [], page_errors: [], console_messages: [], console_errors: [], screenshots: [],
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
    newsPage.on('console', msg => { const record = { page: 'news', type: msg.type(), text: msg.text(), location: msg.location() }; report.console_messages.push(record); if (msg.type() === 'error') report.console_errors.push(record); });
    const newsLoad = await gotoPage(newsPage, origin, 'news/wow-news2004.html');
    report.news = { page: newsLoad, facts: await inspectNews(newsPage, origin, targets, expectedByPath, report) };
    const first = report.news.facts.find(row => row.dom_matches.some(match => match.visible));
    if (first) { await newsPage.evaluate(outputPath => { const wanted = String(outputPath).replace(/^\/+/, ''); const node = Array.from(document.querySelectorAll('img')).find(img => { try { const p = new URL(img.currentSrc || img.src, document.baseURI).pathname; return p.endsWith('/' + wanted); } catch (_) { return false; } }); if (node) node.scrollIntoView({ block: 'center', inline: 'nearest' }); }, first.output_path); }
    const newsShot = path.join(args.screenshots, 'v38-news-static-r1.png'); await newsPage.screenshot({ path: newsShot, type: 'png' }); report.screenshots.push({ path: path.relative(ROOT, newsShot).replace(/\\/g, '/'), sha256: sha256File(newsShot) });
    await newsPage.close();
    const toplistPage = await context.newPage();
    toplistPage.on('pageerror', error => report.page_errors.push({ page: 'toplist', message: String(error && error.message || error), stack: String(error && error.stack || '') }));
    toplistPage.on('console', msg => { const record = { page: 'toplist', type: msg.type(), text: msg.text(), location: msg.location() }; report.console_messages.push(record); if (msg.type() === 'error') report.console_errors.push(record); });
    report.toplist = await inspectToplist(toplistPage, origin, plan, expectedByPath, outputRoot, report);
    const topShot = path.join(args.screenshots, 'v38-toplist-r1.png'); await toplistPage.screenshot({ path: topShot, type: 'png' }); report.screenshots.push({ path: path.relative(ROOT, topShot).replace(/\\/g, '/'), sha256: sha256File(topShot) });
    await toplistPage.close(); await context.close();
    report.local_requests = report.server_requests.length;
    report.toplist_data_requests = report.server_requests.filter(row => normalizePath(row.path).startsWith('toplist/data/'));
    const expectedPaths = new Set(expectedByPath.keys());
    report.unrecorded_local_requests = report.server_requests.filter(row => row.path && !expectedPaths.has(normalizePath(row.path)) && !String(row.path).startsWith('toplist/data/'));
    const newsAssetHttpPass = report.news.facts.every(row => row.http_assertion && row.http_assertion.exact && row.asset_probe.loaded && !row.asset_probe.decode_error && Array.isArray(row.asset_probe.natural) && row.asset_probe.natural[0] === Number(row.expected_dimensions[0]) && row.asset_probe.natural[1] === Number(row.expected_dimensions[1]));
    const newsDomPass = report.news.facts.every(row => row.dom_pass === true);
    const cssAssetPass = report.toplist.css_candidates.every(row => row.local_asset && row.local_asset.exact_target_url === true && row.local_probe && row.local_probe.loaded && !row.local_probe.decode_error && row.http_assertion && row.http_assertion.exact);
    const runtime = report.toplist.script_runtime || {};
    const toplistRuntimePass = report.toplist.page && report.toplist.page.status === 200 && runtime.typeof_Prototype === 'object' && runtime.typeof_init === 'function' && report.toplist.initial && report.toplist.initial.body_wide === true;
    const noErrors = report.external_requests.length === 0 && report.server_errors.length === 0 && report.page_errors.length === 0 && report.console_errors.length === 0;
    const pending = {
      news_dom_rows: report.news.facts.filter(row => !row.dom_pass).map(row => ({ original: row.original, output_path: row.output_path, status: row.status })),
      css_visibility: report.toplist.css_candidates.filter(row => row.status !== 'passed_visible_decoded').map(row => ({ original: row.original, target_output_path: row.target_output_path, status: row.status, exact_stylesheet_target_url: !!row.local_asset?.exact_target_url, visible_entry: row.visible_entry, no_entry_reason: row.no_entry_reason, exact_background_matches: row.exact_background_matches })),
      toplist_data: report.toplist.initial.data_state && report.toplist.initial.data_state.date_data_count === 0 ? [{ data_state: report.toplist.initial.data_state, historical_missing_notice: report.toplist.initial.historical_missing_notice }] : [],
      toplist_navigation: report.toplist.transitions.some(row => row.action === 'next') ? [] : [{ status: 'no_entry', reason: 'no visible body.wide a.next control' }],
      days_selector: report.toplist.days_selector_observation.source_match && report.toplist.days_selector_observation.transitions.some(row => row.action === 'days_1_to_2') && report.toplist.days_selector_observation.transitions.some(row => row.action === 'days_2_to_1') ? [] : [report.toplist.days_selector_observation],
      unrecorded_local_requests: report.unrecorded_local_requests,
    };
    const mandatory = { new_assets_exact_http_mime_dimensions: newsAssetHttpPass, news_dom_visible_complete_decoded_dimensions: newsDomPass, toplist_runtime_init_default_wide: toplistRuntimePass, css_files_local_get_decode: cssAssetPass, toplist_data_requests_recorded: report.toplist_data_requests.every(row => report.server_requests.includes(row)), toplist_data_http_requests_zero: report.toplist_data_requests.length === 0, unrecorded_local_requests_zero: report.unrecorded_local_requests.length === 0, external_requests_zero: report.external_requests.length === 0, server_errors_zero: report.server_errors.length === 0, page_and_console_errors_zero: report.page_errors.length === 0 && report.console_errors.length === 0 };
    const mandatoryPass = Object.values(mandatory).every(Boolean);
    const pendingCount = Object.values(pending).reduce((sum, value) => sum + value.length, 0);
    report.assertions = { mandatory, mandatory_pass: mandatoryPass, pending, pending_count: pendingCount, overall: mandatoryPass && pendingCount === 0 ? 'passed' : (mandatoryPass ? 'completed_with_pending' : 'completed_with_mandatory_failures'), note: 'A zero-error result does not override pending DOM/CSS/data rows; no own date data keys and no visible CSS navigation entry remain explicit limitations.' };
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
