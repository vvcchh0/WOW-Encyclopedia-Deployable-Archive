/*
 * Bounded, loopback-only v36 visual check.  It is prepared for a later root
 * browser GO and is deliberately strict about evidence: every accepted image
 * gets a local byte/decode probe, while rendered visibility is reported only
 * when the real page DOM or computed CSS exposes it.
 */
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../../..');
const BROWSER_DIR = path.resolve(__dirname);
const PLAN_ROOT = path.resolve(BROWSER_DIR, '..');
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const DEFAULT_INPUT = path.join(PLAN_ROOT, 'v36-browser-plan-r1.json');
const DEFAULT_RESULT = path.join(BROWSER_DIR, 'results/v36-browser-r1.json');
const DEFAULT_SCREENSHOTS = path.join(BROWSER_DIR, 'screenshots-r1');

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
  args.input = inside(args.input, PLAN_ROOT, 'browser plan');
  args.result = inside(args.result, BROWSER_DIR, 'browser result');
  args.screenshots = inside(args.screenshots, BROWSER_DIR, 'screenshots');
  if (fs.existsSync(args.result)) throw new Error(`refusing existing browser result: ${args.result}`);
  return args;
}
function routeToOutput(files, route) {
  const wanted = normalizePath(route);
  const slash = `/${wanted}`;
  return files.find(row => normalizePath(row.output_path) === wanted || row.route === slash || normalizePath(row.route) === wanted || normalizePath(row.source_offline_path).endsWith(`/site/${wanted}`)) || null;
}
function outputRecord(files, outputPath) {
  const wanted = normalizePath(outputPath);
  return files.find(row => normalizePath(row.output_path) === wanted) || null;
}
function findStylesheetPages(outputRoot, files, cssRoute) {
  const normalized = normalizePath(cssRoute);
  const prefix = normalized.slice(0, normalized.lastIndexOf('/')) + '/';
  const basename = path.posix.basename(normalized);
  const candidates = [];
  for (const record of files) {
    const outputPath = normalizePath(record.output_path);
    if (!String(record.mime || '').toLowerCase().startsWith('text/html') || !outputPath.startsWith(prefix)) continue;
    const file = path.join(outputRoot, outputPath);
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) continue;
    const text = fs.readFileSync(file, 'utf8');
    if (text.includes(basename) || text.includes(normalized) || text.includes(`/${normalized}`)) candidates.push(record);
  }
  return candidates;
}
function outputUrl(origin, outputPath) {
  const encoded = normalizePath(outputPath).split('/').map(part => encodeURIComponent(part)).join('/');
  return `${origin}${BASE_PATH}${encoded}`;
}
function pathFromRaw(raw, base) {
  try {
    const pathname = new URL(raw || '', base).pathname;
    const marker = pathname.indexOf(BASE_PATH);
    return normalizePath(marker >= 0 ? pathname.slice(marker + BASE_PATH.length) : pathname);
  } catch (_) { return ''; }
}
function createServer(outputRoot, expectedByPath, report) {
  let localRequests = 0;
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
      if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { response.writeHead(404); return response.end(); }
      const body = fs.readFileSync(file);
      localRequests += 1;
      const expected = expectedByPath.get(relative);
      if (expected) {
        const actualSha = sha256(body);
        const actualMime = mime(file);
        report.asset_requests.push({
          path: relative, method: request.method, status: 200, mime: actualMime, length: body.length,
          sha256: actualSha, expected_sha256: expected.derived_sha256, expected_length: expected.derived_length,
          expected_mime: expected.mime || null,
          exact: actualSha === expected.derived_sha256 && body.length === Number(expected.derived_length) && actualMime.toLowerCase().startsWith(String(expected.mime || actualMime).toLowerCase().split(';')[0]),
        });
      }
      response.writeHead(200, { 'Content-Type': mime(file), 'Content-Length': body.length, 'Cache-Control': 'no-store' });
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
async function openPage(page, origin, outputPath) {
  const url = outputUrl(origin, outputPath);
  try {
    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(350);
    return { url, status: response && response.status(), mime: response && response.headers()['content-type'] || null, error: null };
  } catch (error) {
    return { url, status: null, mime: null, error: String(error && error.stack || error) };
  }
}
async function directAssetProbe(page, origin, outputPath) {
  const url = outputUrl(origin, outputPath);
  return page.evaluate(async targetUrl => new Promise(resolve => {
    const image = new Image();
    let settled = false;
    const finish = row => { if (!settled) { settled = true; resolve(row); } };
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
async function inspectPageTargets(page, rows) {
  const expected = rows.map(row => ({ index: row.index, path: normalizePath(row.served_output_path), mode: row.verification_mode }));
  return page.evaluate(async targets => {
    const wanted = new Map(targets.map(row => [row.path, row]));
    const facts = new Map(targets.map(row => [row.index, []]));
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
    const add = (targetPath, fact) => {
      const row = wanted.get(targetPath);
      if (row) facts.get(row.index).push(fact);
    };
    for (const element of Array.from(document.querySelectorAll('img'))) {
      const source = element.currentSrc || element.getAttribute('src') || '';
      const targetPath = pathname(source);
      if (!wanted.has(targetPath)) continue;
      let decodeError = null;
      try { await element.decode(); } catch (error) { decodeError = String(error && error.message || error); }
      const rect = element.getBoundingClientRect();
      const figure = element.closest('figure');
      add(targetPath, {
        kind: 'img', selector: selector(element), src: source, current_src: element.currentSrc || null,
        natural: [element.naturalWidth, element.naturalHeight], complete: !!element.complete,
        decode_error: decodeError, visible: visible(element), box: [rect.width, rect.height],
        figure: !!figure, figcaption: figure ? String(figure.querySelector('figcaption')?.textContent || '').trim() : null,
      });
    }
    for (const element of Array.from(document.querySelectorAll('*'))) {
      const background = getComputedStyle(element).backgroundImage || '';
      if (!background || background === 'none') continue;
      const urls = Array.from(background.matchAll(/url\((?:"|')?([^"')]+)(?:"|')?\)/g));
      for (const match of urls) {
        const targetPath = pathname(match[1]);
        if (!wanted.has(targetPath)) continue;
        const rect = element.getBoundingClientRect();
        const figure = element.closest('figure');
        add(targetPath, {
          kind: 'background', selector: selector(element), background_image: background,
          background_url: match[1], visible: visible(element), box: [rect.width, rect.height],
          figure: !!figure, figcaption: figure ? String(figure.querySelector('figcaption')?.textContent || '').trim() : null,
        });
      }
    }
    return targets.map(row => ({ index: row.index, path: row.path, facts: facts.get(row.index) || [] }));
  }, expected);
}
async function auditVisa(page) {
  return page.evaluate(() => {
    const localHost = location.host;
    const links = Array.from(document.querySelectorAll('a[href]')).map(anchor => {
      const href = anchor.href || '';
      let external = false;
      try { external = new URL(href, document.baseURI).host !== localHost; } catch (_) { external = true; }
      return { href, text: String(anchor.textContent || '').trim(), external };
    });
    const prohibited = links.filter(row => row.external || /apply|signup|sign-up|register|account|bank|issuer|activate|credit-card|creditcard/i.test(row.href));
    return {
      forms: document.querySelectorAll('form').length,
      flash_objects: document.querySelectorAll('object,embed,applet').length,
      mouse_controls: document.querySelectorAll('[onmouseover],[onmouseout],[onclick]').length,
      figures: Array.from(document.querySelectorAll('figure')).map(figure => ({ visible: (() => { const s = getComputedStyle(figure), r = figure.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && r.width > 0 && r.height > 0; })(), caption: String(figure.querySelector('figcaption')?.textContent || '').trim() })),
      prohibited_links: prohibited,
      local_links: links.filter(row => !row.external),
    };
  });
}
async function capture(page, screenshotPath, targetPath) {
  await page.evaluate(pathValue => {
    const pathOf = raw => { try { const value = new URL(raw || '', document.baseURI).pathname; const marker = value.indexOf('/WOW-Encyclopedia-Deployable-Archive/'); return String(marker >= 0 ? value.slice(marker + '/WOW-Encyclopedia-Deployable-Archive/'.length) : value).replace(/^\/+/, ''); } catch (_) { return ''; } };
    const target = Array.from(document.images).find(image => pathOf(image.currentSrc || image.getAttribute('src') || '') === pathValue);
    if (target) target.scrollIntoView({ block: 'center', inline: 'nearest' });
  }, normalizePath(targetPath));
  fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
  await page.screenshot({ path: screenshotPath, fullPage: false });
}
function pageResultFor(rows, route, outputPath) {
  return { route, output_path: outputPath, target_indices: rows.map(row => row.index), status: null, mime: null, error: null };
}
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const started = Date.now();
  const plan = readJson(args.input, 'v36 browser plan');
  if (plan.status !== 'prepared_waiting_root_browser_go') throw new Error(`unexpected plan status: ${plan.status}`);
  if (plan.scope?.network_requests !== 0 || plan.scope?.export_executed_by_plan !== false) throw new Error('v36 browser plan offline/export gate failed');
  if (plan.coverage?.target_count !== 51 || plan.coverage?.reference_count !== 53) throw new Error('v36 browser plan coverage mismatch');
  const outputRoot = inside(path.join(ROOT, plan.scope.output_root), path.join(ROOT, '.scratch'), 'v36 output');
  if (!fs.existsSync(outputRoot) || !fs.statSync(outputRoot).isDirectory()) throw new Error(`missing v36 output: ${outputRoot}`);
  const provenancePath = inside(path.join(outputRoot, 'export-provenance.json'), outputRoot, 'v36 provenance');
  if (sha256File(provenancePath) !== plan.scope.provenance_sha256) throw new Error('v36 provenance SHA mismatch');
  const provenance = readJson(provenancePath, 'v36 provenance');
  const files = Array.isArray(provenance.files) ? provenance.files : [];
  const targets = Array.isArray(plan.targets) ? plan.targets : [];
  if (targets.length !== 51) throw new Error(`expected 51 targets, got ${targets.length}`);
  const expectedByPath = new Map();
  for (const target of targets) {
    const record = outputRecord(files, target.served_output_path);
    if (!record || !record.derived_sha256 || record.derived_length === undefined) throw new Error(`missing provenance target: ${target.served_output_path}`);
    expectedByPath.set(normalizePath(target.served_output_path), record);
  }
  const report = {
    schema: 'wow-recovery.integration.v36-browser-result.v1', accepted: false, browser_executed: false,
    started_utc: new Date().toISOString(), finished_utc: null,
    input: { path: path.relative(ROOT, args.input).replace(/\\/g, '/'), sha256: sha256File(args.input) },
    output: { path: plan.scope.output_root, provenance_sha256: plan.scope.provenance_sha256 },
    coverage: plan.coverage, target_results: [], pages: [], direct_asset_probes: [],
    asset_requests: [], external_requests: [], request_failures: [], console: [], page_errors: [], server_errors: [],
    screenshots: [], assertions: {}, errors: [], local_requests: 0,
  };
  let holder = null, browser = null, context = null, page = null, origin = null;
  const uiFacts = new Map(targets.map(row => [row.index, []]));
  const pageAssignments = new Map();
  const pendingPageReasons = new Map();
  try {
    for (const target of targets) {
      if (target.display_class === 'css_static_reference') {
        const candidates = findStylesheetPages(outputRoot, files, target.route);
        target.associated_pages = candidates.map(row => normalizePath(row.output_path));
        if (!candidates.length) pendingPageReasons.set(target.index, `no HTML output references stylesheet ${target.route}`);
        for (const candidate of candidates) {
          const outputPath = normalizePath(candidate.output_path);
          if (!pageAssignments.has(outputPath)) pageAssignments.set(outputPath, { route: target.route, rows: [] });
          pageAssignments.get(outputPath).rows.push(target);
        }
      } else {
        const pageRecord = routeToOutput(files, target.route);
        if (!pageRecord) pendingPageReasons.set(target.index, `no derived HTML output for source route ${target.route}`);
        else {
          const outputPath = normalizePath(pageRecord.output_path);
          if (!pageAssignments.has(outputPath)) pageAssignments.set(outputPath, { route: target.route, rows: [] });
          pageAssignments.get(outputPath).rows.push(target);
        }
      }
    }
    holder = createServer(outputRoot, expectedByPath, report);
    origin = await listen(holder.server);
    const localOrigin = new URL(origin).origin;
    browser = await chromium.launch({ headless: true });
    context = await browser.newContext({ viewport: { width: 1500, height: 1000 } });
    context.setDefaultTimeout(12000);
    await context.route('**/*', route => {
      const requestUrl = route.request().url();
      try { if (new URL(requestUrl).origin === localOrigin) return route.continue(); } catch (_) {}
      report.external_requests.push(requestUrl);
      return route.abort();
    });
    page = await context.newPage();
    page.on('console', message => report.console.push({ type: message.type(), text: message.text(), location: message.location() }));
    page.on('pageerror', error => report.page_errors.push({ url: page.url(), message: String(error), stack: String(error.stack || '') }));
    page.on('requestfailed', request => report.request_failures.push({ url: request.url(), failure: request.failure() }));

    for (const target of targets) {
      const probe = await directAssetProbe(page, origin, target.served_output_path);
      report.direct_asset_probes.push({ index: target.index, original: target.original, served_output_path: target.served_output_path, ...probe });
    }
    for (const [outputPath, spec] of pageAssignments.entries()) {
      const pageRow = pageResultFor(spec.rows, spec.route, outputPath);
      const opened = await openPage(page, origin, outputPath);
      Object.assign(pageRow, opened);
      report.pages.push(pageRow);
      if (opened.status !== 200) {
        for (const target of spec.rows) pendingPageReasons.set(target.index, `page load status ${opened.status || 'unknown'} for ${outputPath}`);
        continue;
      }
      const facts = await inspectPageTargets(page, spec.rows);
      for (const row of facts) {
        const list = uiFacts.get(row.index) || [];
        list.push(...row.facts.map(fact => ({ ...fact, page_output: outputPath })));
        uiFacts.set(row.index, list);
      }
      if (outputPath === 'news/wow-news2004.html') {
        const first = spec.rows.find(row => row.display_class === 'static_source_reference');
        const file = inside(path.join(args.screenshots, 'v36-news-static.png'), BROWSER_DIR, 'news screenshot');
        await capture(page, file, first && first.served_output_path);
        report.screenshots.push(path.resolve(file));
      }
      if (outputPath === 'visa/index.html') {
        report.visa_audit = await auditVisa(page);
        const first = spec.rows.find(row => row.display_class === 'visa_exhibit_figure');
        const file = inside(path.join(args.screenshots, 'v36-visa-exhibit.png'), BROWSER_DIR, 'Visa screenshot');
        await capture(page, file, first && first.served_output_path);
        report.screenshots.push(path.resolve(file));
      }
      if (spec.rows.some(row => row.verification_mode === 'source_style_or_background_decode')) {
        const first = spec.rows.find(row => row.verification_mode === 'source_style_or_background_decode');
        const file = inside(path.join(args.screenshots, 'v36-background-static.png'), BROWSER_DIR, 'background screenshot');
        await capture(page, file, first && first.served_output_path);
        report.screenshots.push(path.resolve(file));
      }
    }
    report.browser_executed = true;
  } catch (error) {
    report.errors.push(String(error && error.stack || error));
  } finally {
    report.local_requests = holder ? holder.getLocalRequests() : 0;
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
    await closeServer(holder && holder.server);
  }
  const probeByIndex = new Map(report.direct_asset_probes.map(row => [row.index, row]));
  for (const target of targets) {
    const facts = uiFacts.get(target.index) || [];
    const visibleFacts = facts.filter(fact => fact.visible && (fact.kind === 'background' || (fact.kind === 'img' && !fact.decode_error && fact.natural && fact.natural[0] > 0 && fact.natural[1] > 0)));
    let pendingReason = pendingPageReasons.get(target.index) || null;
    let displayed = false;
    if (target.display_class === 'visa_exhibit_figure') displayed = visibleFacts.some(fact => fact.figure);
    else if (target.verification_mode === 'source_style_or_background_decode' || target.verification_mode === 'css_background_decode') displayed = visibleFacts.some(fact => fact.kind === 'background');
    else displayed = visibleFacts.some(fact => fact.kind === 'img');
    if (!displayed && !pendingReason) pendingReason = facts.length ? 'real page match exists but no visible decoded match' : 'no real DOM/CSS match on resolved page';
    report.target_results.push({
      index: target.index, original: target.original, served_output_path: target.served_output_path,
      route: target.route, display_class: target.display_class, reference_kinds: target.reference_kinds,
      references: target.references.map(ref => ({ source_page: ref.source_page, source_page_sha256: ref.source_page_sha256, line: ref.line, column: ref.column, reference_kind: ref.reference_kind, property: ref.property })),
      direct_probe: probeByIndex.get(target.index) || null, ui_facts: facts, displayed, pending_reason: displayed ? null : pendingReason,
    });
  }
  const exactAssetPaths = new Set(report.asset_requests.filter(row => row.exact).map(row => row.path));
  const exactProbes = report.direct_asset_probes.filter(row => row.loaded && !row.decode_error && row.natural[0] > 0 && row.natural[1] > 0 && exactAssetPaths.has(normalizePath(row.served_output_path))).length;
  const visaRows = report.target_results.filter(row => row.display_class === 'visa_exhibit_figure');
  const visaAudit = report.visa_audit || { forms: null, flash_objects: null, mouse_controls: null, prohibited_links: null };
  report.assertions = {
    target_count_51: targets.length === 51,
    reference_count_53: plan.coverage.reference_count === 53,
    direct_asset_probe_count_51: report.direct_asset_probes.length === 51,
    direct_asset_decode_all: exactProbes === 51,
    direct_asset_http_exact_all: targets.every(row => exactAssetPaths.has(normalizePath(row.served_output_path))),
    ui_rows_accounted: report.target_results.length === 51 && report.target_results.every(row => row.displayed || row.pending_reason),
    ui_pending_zero: report.target_results.every(row => row.displayed),
    visa_figures_visible: visaRows.length === 6 && visaRows.every(row => row.displayed),
    visa_no_business_controls: visaAudit.forms === 0 && visaAudit.flash_objects === 0 && visaAudit.mouse_controls === 0 && Array.isArray(visaAudit.prohibited_links) && visaAudit.prohibited_links.length === 0,
    external_requests_zero: report.external_requests.length === 0,
    request_failures_zero: report.request_failures.length === 0,
    server_errors_zero: report.server_errors.length === 0,
    page_errors_zero: report.page_errors.length === 0,
  };
  report.accepted = report.browser_executed && Object.values(report.assertions).every(Boolean);
  report.finished_utc = new Date().toISOString();
  fs.mkdirSync(path.dirname(args.result), { recursive: true });
  fs.writeFileSync(args.result, JSON.stringify(report, null, 2) + '\n', 'utf8');
  process.stdout.write(JSON.stringify({ result: args.result, result_sha256: sha256File(args.result), accepted: report.accepted, assertions: report.assertions, elapsed_seconds: (Date.now() - started) / 1000 }) + '\n');
  if (!report.accepted) process.exitCode = 1;
}
main().catch(error => { console.error(error && error.stack || error); process.exitCode = 1; });
