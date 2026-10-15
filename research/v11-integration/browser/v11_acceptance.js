/*
 * Focused browser acceptance for the root-owned v11 Pages export.
 *
 * The runner never starts a server.  It is usable only with --server-ready,
 * accepts loopback GET/HEAD requests under the supplied project prefix, and
 * records the exact final export/provenance/route-map hashes used at runtime.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  return index < 0 || index + 1 >= process.argv.length ? fallback : process.argv[index + 1];
}

function hasFlag(name) { return process.argv.includes(name); }
function sha256Hex(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function fail(message) { throw new Error(message); }
function expect(condition, message) { if (!condition) fail(message); }

function normalizePrefix(value) {
  let prefix = String(value || '/');
  if (!prefix.startsWith('/')) prefix = `/${prefix}`;
  if (!prefix.endsWith('/')) prefix += '/';
  if (prefix.includes('..')) fail(`unsafe project prefix: ${prefix}`);
  return prefix.replace(/\/{2,}/g, '/');
}

function loopbackHost(hostname) {
  const host = String(hostname || '').toLowerCase().replace(/^\[|\]$/g, '');
  return host === '127.0.0.1' || host === 'localhost' || host === '::1';
}

const repoRoot = path.resolve(__dirname, '..', '..', '..');
const baseUrlText = option('--base-url', 'http://127.0.0.1:29007');
const prefix = normalizePrefix(option('--prefix', '/WOW-Encyclopedia-Deployable-Archive/'));
const timeoutMs = Number(option('--timeout-ms', '30000'));
const settleMs = Number(option('--settle-ms', '350'));
const playwrightModule = option('--playwright-module', 'playwright');
const output = path.resolve(repoRoot, option('--output', 'research/v11-integration/browser/v11-browser-receipt.json'));
const screenshotDir = path.resolve(repoRoot, option('--screenshot-dir', 'research/v11-integration/browser/screenshots'));
const manifestPath = path.resolve(repoRoot, option('--manifest', '.scratch/offline-navigation-20261015-v11/build-manifest.json'));
const provenancePath = path.resolve(repoRoot, option('--provenance', '.scratch/pages-resources-20261015-v11/export-provenance.json'));
const routeMapPath = path.resolve(repoRoot, option('--route-map', '.scratch/pages-resources-20261015-v11/__offline/route-map.json'));
const productionPath = path.resolve(repoRoot, option('--production', 'tools/export_github_pages.py'));
const sourceReceiptPath = path.resolve(repoRoot, option('--source-receipt', 'research/v11-integration/source/v11-source-receipt.json'));
const sourceMapPath = path.resolve(repoRoot, option('--source-map', 'research/v11-integration/source/v11-additions-source-map.json'));
const selectedPath = path.resolve(repoRoot, option('--selected', 'research/continuous-recovery-20261015/selected-news-assets13-source-map.json'));
const acceptancePath = path.resolve(repoRoot, option('--acceptance', 'research/continuous-recovery-20261015/news-assets13-acceptance.json'));
const rssMapPath = path.resolve(repoRoot, option('--rss-map', 'research/v10-integration/source/v10-additions-source-map.json'));
const referenceBrowserPath = path.resolve(repoRoot, option('--reference-browser-receipt', 'research/v10-integration/browser/v10-browser-receipt.json'));
const onlyChecks = String(option('--only', '')).split(',').map(value => value.trim()).filter(Boolean);

const EXPECTED = {
  manifest: 'bb3c398edc7baab8ee185428a9674afa6b53d5709c313cd69d894ceaeca530db',
  sourceReceipt: '7faca80435f1cb5582ee35b84047708b9983737770f8a59f6f57b58b578455dd',
  sourceMap: 'b9bf3562412396a6c2dca5543e70c706718964bbb3182d379e9c8d0dce5af3b4',
  selected: '08f6e4bfc836eb56c4704c6f23582f1bc3f37a4d985d2dbde66ac281f649b8a3',
  acceptance: 'e9748d3a9f7a5d2483766262856c621fbfa05a8a2bb58d3ebd77b51161e5099c',
  rssMap: '369a458b2942da1aadfbf1a5f072ba3df971d43bc34a8e7c570f788214595a74',
  referenceBrowser: 'bbe3f59f364bb465c3cee320cdfd3dea459cc80191ed670b0ff9c9a532cbbbd8',
};

const report = {
  schema: 'wow-recovery.core-source-v11-browser-receipt.v1',
  status: 'prepared',
  started_utc: new Date().toISOString(),
  finished_utc: null,
  server_ready_flag: hasFlag('--server-ready'),
  base_url: baseUrlText,
  prefix,
  method: 'Loopback server only; Playwright GET/HEAD requests are restricted to the supplied origin and prefix; other methods and external origins are blocked; no server is started by this runner.',
  scope: {
    rss_paths: 7,
    newsarchive_css: { route: '/news/newsarchive.css', bytes: 109, selectors: ['.news-border-left', '.news-border-right', '#contentContainer img'] },
    new_image_instances: {
      identities: ['/news/images/08-01/01-10-08-01.jpg', '/news/images/08-02/arenatourney2.gif'],
      page_coverage: { '/news/rss-01-2008.xml': ['/news/images/08-01/01-10-08-01.jpg'], '/news/rss-02-2008.xml': ['/news/images/08-01/01-10-08-01.jpg', '/news/images/08-02/arenatourney2.gif'] },
      note: 'The report records every matching real img element; duplicate original GIF references remain multiplicity evidence rather than being collapsed.',
    },
    common12_viewer: { route: '/wrath/art.xml', query: 's=12', expected_index: 12 },
  },
  inputs: {},
  checks: [],
  requests: [],
  responses: [],
  route_decisions: [],
  request_failed: [],
  page_errors: [],
  console_errors: [],
  screenshots: [],
  failures: [],
  notes: [],
};

let activeCheck = 'setup';
let baseUrl;
let browser;
let rssTargets = [];
let assetTargets = [];
let expectedViewerImage = null;
let provenanceJson = null;
let routeMapJson = null;

function relative(file) { return path.relative(repoRoot, file).replace(/\\/g, '/'); }

function readJsonInput(label, absolutePath, expectedSha256 = null) {
  if (!fs.existsSync(absolutePath)) fail(`input not found: ${relative(absolutePath)}`);
  const data = fs.readFileSync(absolutePath);
  const sha256 = sha256Hex(data);
  report.inputs[label] = { path: relative(absolutePath), exists: true, bytes: data.length, sha256 };
  if (expectedSha256) {
    report.inputs[label].expected_sha256 = expectedSha256;
    if (sha256 !== expectedSha256) fail(`${label} SHA changed: ${sha256} != ${expectedSha256}`);
  }
  return JSON.parse(data.toString('utf8'));
}

function readFileBinding(label, absolutePath, expectedSha256 = null) {
  if (!fs.existsSync(absolutePath)) fail(`input not found: ${relative(absolutePath)}`);
  const data = fs.readFileSync(absolutePath);
  const sha256 = sha256Hex(data);
  report.inputs[label] = { path: relative(absolutePath), exists: true, bytes: data.length, sha256 };
  if (expectedSha256) {
    report.inputs[label].expected_sha256 = expectedSha256;
    if (sha256 !== expectedSha256) fail(`${label} SHA changed: ${sha256} != ${expectedSha256}`);
  }
  return data;
}

function sourceAssetByRoute(sourceMap, route) {
  const entry = (sourceMap.entries || []).find(item => String(item.derived_route || '') === route);
  if (!entry) fail(`v11 source map missing ${route}`);
  return entry;
}

function sourceBytes(entry) { return Number(entry.body_bytes ?? entry.content_length); }
function sourceSha(entry) { return String(entry.body_sha256 || entry.sha256 || ''); }

function publishedPathFor(route) {
  const files = Array.isArray(provenanceJson && provenanceJson.files) ? provenanceJson.files : [];
  const item = files.find(candidate => String(candidate.route || '') === route || String(candidate.source_route || '') === route);
  if (item && item.output_path) return String(item.output_path).replace(/\\/g, '/').replace(/^\/+/, '');
  const aliases = (routeMapJson && routeMapJson.aliases) || {};
  const mapped = aliases[route];
  if (mapped) {
    const value = String(mapped).replace(/\\/g, '/');
    const prefixText = prefix.replace(/\/$/, '');
    return value.startsWith(prefixText + '/') ? value.slice(prefixText.length + 1) : value.replace(/^\/+/, '');
  }
  return route.replace(/^\/+/, '') + (route.endsWith('.xml') ? '.html' : '');
}

function routeUrl(relativePath, query = '') {
  const url = new URL(baseUrl.href);
  url.pathname = prefix + String(relativePath || '').replace(/^\/+/, '');
  url.search = query;
  url.hash = '';
  return url.toString();
}

function requestClass(value, method) {
  let url;
  try { url = new URL(value); } catch (_) { return 'invalid-url'; }
  if (!['http:', 'https:'].includes(url.protocol)) return 'non-http';
  const local = url.origin === baseUrl.origin && url.pathname.startsWith(prefix);
  if (!local) return url.origin === baseUrl.origin ? 'local-outside-prefix' : 'external-origin';
  return ['GET', 'HEAD'].includes(String(method).toUpperCase()) ? 'local-allowed' : 'local-non-get';
}

function attachPage(page) {
  page.on('request', request => report.requests.push({ check: activeCheck, method: request.method(), url: request.url(), resource_type: request.resourceType(), class: requestClass(request.url(), request.method()) }));
  page.on('response', response => report.responses.push({ check: activeCheck, method: response.request().method(), url: response.url(), status: response.status(), resource_type: response.request().resourceType() }));
  page.on('requestfailed', request => report.request_failed.push({ check: activeCheck, method: request.method(), url: request.url(), resource_type: request.resourceType(), failure: request.failure() }));
  page.on('pageerror', error => report.page_errors.push({ check: activeCheck, error: String(error) }));
  page.on('console', message => {
    if (['error', 'warning'].includes(message.type())) report.console_errors.push({ check: activeCheck, type: message.type(), text: message.text() });
  });
}

function inputSetup() {
  const manifest = readJsonInput('v11_manifest', manifestPath, EXPECTED.manifest);
  const sourceReceipt = readJsonInput('v11_source_receipt', sourceReceiptPath, EXPECTED.sourceReceipt);
  const sourceMap = readJsonInput('v11_source_map', sourceMapPath, EXPECTED.sourceMap);
  const selected = readJsonInput('selected_news_assets13', selectedPath, EXPECTED.selected);
  const acceptance = readJsonInput('news_assets13_acceptance', acceptancePath, EXPECTED.acceptance);
  const rssMap = readJsonInput('v10_rss_source_map', rssMapPath, EXPECTED.rssMap);
  const reference = readJsonInput('v10_common12_reference_receipt', referenceBrowserPath, EXPECTED.referenceBrowser);
  provenanceJson = readJsonInput('final_export_provenance', provenancePath);
  routeMapJson = readJsonInput('final_export_route_map', routeMapPath);
  readFileBinding('production_exporter', productionPath);
  const files = Array.isArray(manifest.files) ? manifest.files : [];
  const routes = new Set(files.map(item => String(item.route || '')));
  expect(files.length === 8341, `v11 manifest route count ${files.length} != 8341`);
  expect(Object.keys(manifest.route_aliases || {}).length === 183, 'v11 alias count is not 183');
  expect(sourceReceipt.status === 'mirror_only_pending_root_export', `unexpected source receipt status ${sourceReceipt.status}`);
  expect(sourceReceipt.source_count && sourceReceipt.source_count.v11 === 8341, 'v11 receipt count mismatch');
  expect(Array.isArray(sourceMap.entries) && sourceMap.entries.length === 3, 'v11 source map does not contain exactly three assets');
  expect(selected.entity_count === 3 && Array.isArray(selected.entries) && selected.entries.length === 3, 'selected news-assets13 count mismatch');
  expect(acceptance.accepted === true && acceptance.valid_entities === 3, 'news-assets13 acceptance is not accepted');
  for (const item of sourceMap.entries) expect(routes.has(String(item.derived_route)), `manifest missing v11 route ${item.derived_route}`);
  rssTargets = (rssMap.entries || []).filter(item => String(item.derived_route || '').startsWith('/news/rss-')).map(item => {
    const provenance = item.selection_provenance || {};
    const dateKeys = Object.keys(provenance.article_posted_dates || {});
    const firstDate = dateKeys[0] || '';
    const parts = firstDate.split('-');
    const title = String(item.title || '').split('->').pop().trim();
    return {
      route: String(item.derived_route),
      published_path: publishedPathFor(String(item.derived_route)),
      title,
      title_month_matches_url: item.title_month_matches_url,
      source_anomaly: item.source_anomaly || null,
      expected_date_pattern: firstDate ? `${Number(parts[0])}-\\d{1,2}-${parts[2] || ''}` : null,
    };
  });
  expect(rssTargets.length === 7, `RSS target count ${rssTargets.length} != 7`);
  report.inputs.rss_targets = rssTargets;
  assetTargets = [
    { route: '/news/images/08-01/01-10-08-01.jpg', pages: ['/news/rss-01-2008.xml', '/news/rss-02-2008.xml'], expand_title_by_page: { '/news/rss-01-2008.xml': 'Introducing BlizzCast', '/news/rss-02-2008.xml': 'BlizzCast Episode 2' } },
    { route: '/news/images/08-02/arenatourney2.gif', pages: ['/news/rss-02-2008.xml'], expand_title_by_page: { '/news/rss-02-2008.xml': 'Arena Tournament Realm Is Live on the PTR' } },
  ].map(item => ({ ...item, source: sourceAssetByRoute(sourceMap, item.route), published_path: publishedPathFor(item.route) }));
  const common12 = (reference.checks || []).find(item => item.name === 'wrath:card-center-to-viewer-s12' && item.passed === true);
  expect(common12 && common12.image && common12.image.sha256, 'accepted v10 common12 reference image is missing');
  expectedViewerImage = { bytes: Number(common12.image.bytes), sha256: String(common12.image.sha256), mime: String(common12.image.content_type || 'image/jpeg').split(';')[0].toLowerCase() };
  report.inputs.reference_common12 = { sha256: expectedViewerImage.sha256, bytes: expectedViewerImage.bytes, mime: expectedViewerImage.mime, reference_check: common12.name };
  report.inputs.published_routes = { rss: rssTargets.map(item => ({ source_route: item.route, published_path: item.published_path })), css: publishedPathFor('/news/newsarchive.css'), assets: assetTargets.map(item => ({ route: item.route, published_path: item.published_path })), viewer: publishedPathFor('/wrath/art.xml') };
  return { manifest, sourceReceipt, sourceMap, selected, acceptance };
}

async function navigate(page, relativePath, query = '') {
  const requested = routeUrl(relativePath, query);
  const response = await page.goto(requested, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
  if (!response) fail(`no response for ${relativePath}${query}`);
  await page.waitForTimeout(settleMs);
  return { requested, response, finalUrl: page.url(), state: await inspectPage(page) };
}

async function inspectPage(page) {
  return page.evaluate(() => {
    const body = document.body;
    const text = (body && (body.innerText || body.textContent) || '').replace(/\s+/g, ' ').trim();
    return {
      title: document.title,
      visibleTextLength: text.length,
      bodyText: text.slice(0, 40000),
      headings: [...document.querySelectorAll('h1,h2,h3')].map(node => (node.innerText || node.textContent || '').replace(/\s+/g, ' ').trim()).filter(Boolean),
      dates: [...document.querySelectorAll('.date,[class*="date"],time,.posted-date')].map(node => (node.innerText || node.textContent || '').replace(/\s+/g, ' ').trim()).filter(Boolean),
      url: location.href,
    };
  });
}

async function browserFetch(page, target, decodeImage = false) {
  return page.evaluate(async ({ target, decodeImage }) => {
    try {
      const response = await fetch(target, { cache: 'no-store' });
      const bytes = new Uint8Array(await response.arrayBuffer());
      const digest = await crypto.subtle.digest('SHA-256', bytes);
      const sha256 = [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2, '0')).join('');
      let decoded = null;
      let naturalWidth = 0;
      let naturalHeight = 0;
      if (decodeImage) {
        const objectUrl = URL.createObjectURL(new Blob([bytes], { type: response.headers.get('content-type') || 'application/octet-stream' }));
        const image = new Image();
        await new Promise(resolve => { image.onload = resolve; image.onerror = resolve; image.src = objectUrl; });
        try { if (image.decode) await image.decode(); } catch (_) { /* onload remains evidence */ }
        decoded = image.naturalWidth > 0 && image.naturalHeight > 0;
        naturalWidth = image.naturalWidth;
        naturalHeight = image.naturalHeight;
        URL.revokeObjectURL(objectUrl);
      }
      return { url: target, served_url: response.url, status: response.status, bytes: bytes.byteLength, sha256, content_type: response.headers.get('content-type') || '', text: decodeImage ? null : new TextDecoder().decode(bytes), decoded, natural_width: naturalWidth, natural_height: naturalHeight };
    } catch (error) {
      return { url: target, served_url: '', status: 0, bytes: 0, sha256: '', content_type: '', text: null, decoded: false, natural_width: 0, natural_height: 0, error: String(error) };
    }
  }, { target, decodeImage });
}

async function inspectAssetDom(page, route, expectedPath) {
  return page.evaluate(({ targetRoute, expectedPath }) => {
    const expected = String(expectedPath || '').replace(/^\/+/, '');
    const fallbackExpected = String(targetRoute || '').replace(/^\/+/, '');
    const normalizedPath = value => {
      try { return new URL(value, document.baseURI).pathname.replace(/^\/+/, ''); } catch (_) { return ''; }
    };
    return [...document.images].filter(image => {
      const candidates = [image.getAttribute('src'), image.currentSrc, image.src].filter(Boolean);
      return candidates.some(value => {
        const actual = normalizedPath(value);
        return actual === expected || actual === fallbackExpected;
      });
    }).map(image => {
    const rect = image.getBoundingClientRect();
    const style = getComputedStyle(image);
    return { src_attribute: image.getAttribute('src') || '', current_src: image.currentSrc || image.src || '', visible: Boolean(image.getClientRects().length && rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0'), natural_width: image.naturalWidth, natural_height: image.naturalHeight, rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height } };
    });
  }, { targetRoute: route, expectedPath });
}

async function accordionSnapshot(entry, expectedPath, targetRoute) {
  return entry.evaluate((root, values) => {
    const expected = String(values.expectedPath || '').replace(/^\/+/, '');
    const fallbackExpected = String(values.targetRoute || '').replace(/^\/+/, '');
    const normalizedPath = value => {
      try { return new URL(value, document.baseURI).pathname.replace(/^\/+/, ''); } catch (_) { return ''; }
    };
    const state = node => {
      if (!node) return null;
      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return {
        display: style.display,
        visibility: style.visibility,
        opacity: style.opacity,
        hidden: Boolean(node.hidden),
        has_client_rects: Boolean(node.getClientRects().length),
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        visible: Boolean(node.getClientRects().length && rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0'),
      };
    };
    const image = [...root.querySelectorAll('img')].find(node => {
      const candidates = [node.getAttribute('src'), node.currentSrc, node.src].filter(Boolean);
      return candidates.some(value => {
        const actual = normalizedPath(value);
        return actual === expected || actual === fallbackExpected;
      });
    });
    const control = root.querySelector('li.news-toggle a');
    const heading = root.querySelector('h1');
    const item = root.querySelector('.news-item');
    const description = root.querySelector('description');
    return {
      entry_id: root.id || '',
      heading: heading ? (heading.innerText || heading.textContent || '').replace(/\s+/g, ' ').trim() : '',
      control_href: control ? control.getAttribute('href') || '' : '',
      control: state(control),
      news_item: state(item),
      description: state(description),
      target_image: image ? { ...state(image), src_attribute: image.getAttribute('src') || '', current_src: image.currentSrc || image.src || '', natural_width: image.naturalWidth, natural_height: image.naturalHeight } : null,
    };
  }, { expectedPath, targetRoute });
}

async function expandNewsEntry(page, title, expectedPath, targetRoute) {
  const headings = page.locator('h1');
  let heading = null;
  for (let index = 0; index < await headings.count(); index += 1) {
    const candidate = headings.nth(index);
    const candidateText = (await candidate.textContent()) || (await candidate.innerText()) || '';
    if (candidateText.replace(/\s+/g, ' ').trim() === title) {
      heading = candidate;
      break;
    }
  }
  expect(heading, `accordion heading not found: ${title}`);
  const entry = heading.locator('xpath=ancestor::div[starts-with(@id, "news") and starts-with(@class, "news-")]').first();
  expect(await entry.count() === 1, `accordion entry not unique for ${title}`);
  const toggle = entry.locator('li.news-toggle a').first();
  expect(await toggle.count() === 1, `accordion toggle not found for ${title}`);
  const hover = entry.locator('.hoverContainer').first();
  expect(await hover.count() === 1, `accordion hoverContainer not found for ${title}`);
  const control = entry.locator('h1 a').first();
  expect(await control.count() === 1, `accordion title link not found for ${title}`);
  const before = await accordionSnapshot(entry, expectedPath, targetRoute);
  const toggleHref = await toggle.getAttribute('href');
  const titleHref = await control.getAttribute('href');
  const onclick = await hover.getAttribute('onclick');
  await control.click({ timeout: timeoutMs });
  await page.waitForTimeout(settleMs);
  const after = await accordionSnapshot(entry, expectedPath, targetRoute);
  expect(after.entry_id && after.heading === title, `accordion identity changed after click: ${JSON.stringify(after)}`);
  return { title, click: { method: 'Playwright locator.click', selector: 'h1 a', title_href: titleHref, hover_onclick: onclick, toggle_href: toggleHref, performed: true }, before, after };
}

function selectedCheck(name) {
  if (!onlyChecks.length) return true;
  return onlyChecks.some(token => name === token || name.startsWith(`${token}:`));
}

async function runCheck(name, fn) {
  activeCheck = name;
  const started = Date.now();
  try {
    const result = await fn();
    report.checks.push({ name, passed: true, elapsed_ms: Date.now() - started, ...(result || {}) });
  } catch (error) {
    const item = { name, passed: false, elapsed_ms: Date.now() - started, error: String(error) };
    report.checks.push(item);
    report.failures.push(item);
  }
}

async function runSelectedCheck(name, fn) {
  if (!selectedCheck(name)) {
    report.checks.push({ name, skipped: true });
    return;
  }
  return runCheck(name, fn);
}

function screenshotPath(label) { return path.join(screenshotDir, label.replace(/[^a-z0-9_.-]+/gi, '_') + '.png'); }
function recordScreenshot(label, file) { const data = fs.readFileSync(file); report.screenshots.push({ label, path: relative(file), bytes: data.length, sha256: sha256Hex(data) }); }

function knownGapUrl(value) {
  try {
    const url = new URL(value);
    if (/\/wrath\/images\/layout\/ssborder1\.png$/i.test(url.pathname)) return true;
    if (/\/wrath\/images\/artwork\/(?:ss(?:2|4|5|7|8|10|11)|en_us\/ss1)\.jpg$/i.test(url.pathname)) return true;
    return false;
  } catch (_) { return false; }
}

async function viewerState(page) {
  return page.evaluate(() => {
    const current = document.getElementById('dCurrent');
    const total = document.getElementById('dTotal');
    const screen = document.getElementById('Screenie');
    const image = window.screenImage;
    const number = value => Number.isFinite(Number(value)) ? Number(value) : null;
    return { url: location.href, d_current: number(current && current.textContent), d_total: number(total && total.textContent), now_viewing: number(window.nowViewing), shot_list_length: Array.isArray(window.shotList) ? window.shotList.length : null, screen_background: screen ? screen.style.backgroundImage : '', screen_image: image ? { src: image.src || '', complete: image.complete, natural_width: image.naturalWidth, natural_height: image.naturalHeight } : null };
  });
}

async function main() {
  if (!hasFlag('--server-ready')) {
    report.status = 'not_run_server_ready_flag_missing';
    report.finished_utc = new Date().toISOString();
    report.notes.push('No browser was started; --server-ready is required after coordinator confirmation of loopback port 29007.');
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    console.error(JSON.stringify(report));
    process.exitCode = 2;
    return;
  }
  try {
    baseUrl = new URL(baseUrlText);
    expect(baseUrl.protocol === 'http:', `base URL must use http loopback: ${baseUrlText}`);
    expect(loopbackHost(baseUrl.hostname), `base URL is not loopback: ${baseUrlText}`);
    expect(baseUrl.pathname === '/' || baseUrl.pathname === '', `base URL must not include a path: ${baseUrlText}`);
    expect(Number.isFinite(timeoutMs) && timeoutMs > 0, `invalid timeout: ${timeoutMs}`);
    report.inputs.runner = { path: relative(__filename), sha256: sha256Hex(fs.readFileSync(__filename)), bytes: fs.statSync(__filename).size };
    report.command = { argv: process.argv.slice(1), node: process.execPath, cwd: repoRoot };
    inputSetup();
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.mkdirSync(screenshotDir, { recursive: true });
    const { chromium } = require(playwrightModule);
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, serviceWorkers: 'block' });
    await context.route('**/*', async route => {
      const request = route.request();
      const classification = requestClass(request.url(), request.method());
      const allowed = classification === 'local-allowed';
      report.route_decisions.push({ check: activeCheck, method: request.method(), url: request.url(), resource_type: request.resourceType(), class: classification, action: allowed ? 'continue' : 'abort' });
      if (allowed) return route.continue();
      return route.abort();
    });
    const page = await context.newPage();
    attachPage(page);

    for (const target of rssTargets) {
      await runSelectedCheck(`rss:${target.route}`, async () => {
        const loaded = await navigate(page, target.published_path);
        expect(loaded.response.status() === 200, `${target.route} HTTP ${loaded.response.status()}`);
        expect(loaded.state.visibleTextLength > 20, `${target.route} has no visible body text`);
        expect(loaded.state.title.includes(target.title), `${target.route} title lost ${target.title}`);
        const dateMatch = target.expected_date_pattern ? new RegExp(`(?:^|\\D)${target.expected_date_pattern}(?:\\D|$)`).exec(loaded.state.bodyText) : null;
        expect(dateMatch, `${target.route} has no posted-date evidence matching ${target.expected_date_pattern}`);
        return { published_path: target.published_path, status: loaded.response.status(), final_url: loaded.finalUrl, title: loaded.state.title, headings: loaded.state.headings.slice(0, 12), date_evidence: dateMatch[0], source_anomaly: target.source_anomaly, title_month_matches_url: target.title_month_matches_url };
      });
    }

    await runSelectedCheck('newsarchive:css-http-and-real-dom-computed-rules', async () => {
      const cssEntry = (() => {
        const map = JSON.parse(fs.readFileSync(sourceMapPath, 'utf8'));
        return sourceAssetByRoute(map, '/news/newsarchive.css');
      })();
      const loaded = await navigate(page, publishedPathFor('/news/rss-01-2008.xml'));
      expect(loaded.response.status() === 200, `CSS host page HTTP ${loaded.response.status()}`);
      const css = await browserFetch(page, routeUrl(publishedPathFor('/news/newsarchive.css')), false);
      const expectedMime = String(cssEntry.mime || 'text/css').split(';')[0].toLowerCase();
      expect(css.status === 200 && css.bytes === sourceBytes(cssEntry) && css.sha256 === sourceSha(cssEntry), `newsarchive.css payload mismatch: ${JSON.stringify(css)}`);
      expect(css.content_type.toLowerCase().split(';')[0] === expectedMime, `newsarchive.css MIME mismatch: ${css.content_type}`);
      const computed = await page.evaluate(() => {
        const borders = [...document.querySelectorAll('.news-border-left, .news-border-right')].slice(0, 6).map(node => ({ class_name: node.className, display: getComputedStyle(node).display, visibility: getComputedStyle(node).visibility, rect: (() => { const r = node.getBoundingClientRect(); return { width: r.width, height: r.height }; })() }));
        const images = [...document.querySelectorAll('#contentContainer img')].slice(0, 6).map(node => ({ display: getComputedStyle(node).display, visibility: getComputedStyle(node).visibility, rect: (() => { const r = node.getBoundingClientRect(); return { width: r.width, height: r.height }; })() }));
        const link = [...document.querySelectorAll('link[rel~="stylesheet"]')].find(node => { try { return new URL(node.href, document.baseURI).pathname.endsWith('/news/newsarchive.css'); } catch (_) { return false; } });
        return { stylesheet_link: link ? link.href : '', stylesheet_loaded: Boolean(link && link.sheet), border_count: borders.length, borders, content_image_count: images.length, content_images: images };
      });
      expect(computed.stylesheet_loaded, `newsarchive.css is not attached to real DOM: ${JSON.stringify(computed)}`);
      expect(computed.border_count > 0 && computed.borders.every(item => item.display === 'none'), `news border computed rules mismatch: ${JSON.stringify(computed.borders)}`);
      expect(computed.content_image_count > 0 && computed.content_images.every(item => item.display === 'block'), `content image computed rules mismatch: ${JSON.stringify(computed.content_images)}`);
      const shot = screenshotPath('newsarchive-css-real-dom');
      await page.screenshot({ path: shot, fullPage: true });
      recordScreenshot('newsarchive-css-real-dom', shot);
      return { css_payload: { route: '/news/newsarchive.css', published_path: publishedPathFor('/news/newsarchive.css'), ...css, expected_sha256: sourceSha(cssEntry), expected_bytes: sourceBytes(cssEntry) }, computed };
    });

    await runSelectedCheck('news-assets:three-real-page-instances', async () => {
      const instances = [];
      for (const target of assetTargets) {
        for (const sourceRoute of target.pages) {
          const rssTarget = rssTargets.find(item => item.route === sourceRoute);
          expect(rssTarget, `asset page target missing ${sourceRoute}`);
          const loaded = await navigate(page, rssTarget.published_path);
          const expandTitle = target.expand_title_by_page[sourceRoute];
          expect(expandTitle, `accordion title missing for ${target.route} on ${sourceRoute}`);
          const expansion = await expandNewsEntry(page, expandTitle, new URL(routeUrl(target.published_path)).pathname, target.route);
          const dom = await inspectAssetDom(page, target.route, new URL(routeUrl(target.published_path)).pathname);
          expect(dom.length > 0, `${target.route} has no real img element on ${sourceRoute}`);
          const payload = await browserFetch(page, routeUrl(target.published_path), true);
          const expectedMime = String(target.source.mime || '').split(';')[0].toLowerCase();
          expect(payload.status === 200 && payload.bytes === sourceBytes(target.source) && payload.sha256 === sourceSha(target.source), `${target.route} payload mismatch on ${sourceRoute}: ${JSON.stringify(payload)}`);
          expect(payload.content_type.toLowerCase().split(';')[0] === expectedMime && payload.decoded, `${target.route} MIME/decode mismatch on ${sourceRoute}: ${JSON.stringify(payload)}`);
          expect(dom.some(item => item.visible && item.natural_width > 0 && item.natural_height > 0), `${target.route} has no visible decoded DOM instance on ${sourceRoute}: ${JSON.stringify(dom)}`);
          const screenshotLabel = `news-assets-expanded-${sourceRoute.replace(/[^a-z0-9]+/gi, '-')}-${target.route.split('/').pop()}`;
          const shot = screenshotPath(screenshotLabel);
          await page.screenshot({ path: shot, fullPage: true });
          recordScreenshot(screenshotLabel, shot);
          instances.push({ source_page: sourceRoute, published_path: rssTarget.published_path, route: target.route, article_title: expandTitle, accordion: expansion, payload, dom_instances: dom });
        }
      }
      return { unique_assets: assetTargets.map(item => ({ route: item.route, source_sha256: sourceSha(item.source), source_bytes: sourceBytes(item.source), mime: item.source.mime })), real_instances: instances, gif_animation: 'static first-frame/decode evidence only; animation timing was not claimed' };
    });

    await runSelectedCheck('wrath:common12-viewer-regression', async () => {
      const viewerPath = publishedPathFor('/wrath/art.xml');
      const loaded = await navigate(page, viewerPath, '?s=12');
      expect(loaded.response.status() === 200, `viewer HTTP ${loaded.response.status()}`);
      await page.waitForFunction(() => Boolean(document.getElementById('dCurrent') && document.getElementById('dTotal') && window.screenImage), { timeout: timeoutMs });
      const state = await viewerState(page);
      expect(state.d_current === 12 && state.d_total === 13 && state.shot_list_length === 13, `common12 viewer state mismatch: ${JSON.stringify(state)}`);
      const imagePath = publishedPathFor('/wrath/images/artwork/ss12.jpg');
      const payload = await browserFetch(page, routeUrl(imagePath), true);
      expect(payload.status === 200 && payload.bytes === expectedViewerImage.bytes && payload.sha256 === expectedViewerImage.sha256 && payload.content_type.toLowerCase().split(';')[0] === expectedViewerImage.mime && payload.decoded, `common12 image mismatch: ${JSON.stringify(payload)}`);
      const displayed = await page.evaluate(() => ({ screen_image: window.screenImage ? { src: window.screenImage.src || '', natural_width: window.screenImage.naturalWidth, natural_height: window.screenImage.naturalHeight } : null, background: document.getElementById('Screenie') ? document.getElementById('Screenie').style.backgroundImage : '' }));
      expect(displayed.screen_image && new URL(displayed.screen_image.src).pathname.endsWith('/wrath/images/artwork/ss12.jpg'), `screenImage does not display common12: ${JSON.stringify(displayed)}`);
      expect(/ss12\.jpg/i.test(displayed.background), `#Screenie does not display common12 background: ${JSON.stringify(displayed)}`);
      const shot = screenshotPath('wrath-viewer-common12');
      await page.screenshot({ path: shot, fullPage: true });
      recordScreenshot('wrath-viewer-common12', shot);
      return { viewer_path: viewerPath, final_url: loaded.finalUrl, state, image_path: imagePath, image: payload, displayed };
    });
    await context.close();
    report.status = report.failures.length ? 'completed_with_failures' : (onlyChecks.length ? 'completed_with_skips' : 'passed');
  } catch (error) {
    report.status = 'runner_error';
    report.failures.push({ name: 'runner', error: String(error) });
  } finally {
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    const blocked = report.route_decisions.filter(item => item.action === 'abort');
    const known404 = report.responses.filter(item => item.status === 404 && knownGapUrl(item.url));
    const unexpected404 = report.responses.filter(item => item.status === 404 && !knownGapUrl(item.url));
    const generic404Console = report.console_errors.filter(item => /Failed to load resource: the server responded with a status of 404/i.test(item.text));
    const unexpectedConsole = report.console_errors.filter(item => !/Failed to load resource: the server responded with a status of 404/i.test(item.text));
    report.summary = {
      checks: report.checks.length,
      executed_checks: report.checks.filter(item => item.skipped !== true).length,
      passed_checks: report.checks.filter(item => item.passed === true).length,
      failed_checks: report.checks.filter(item => item.passed === false).length,
      skipped_checks: report.checks.filter(item => item.skipped === true).length,
      requests: report.requests.length,
      responses: report.responses.length,
      blocked_requests: blocked.length,
      disallowed_requests: blocked.length,
      request_failed: report.request_failed.length,
      page_errors: report.page_errors.length,
      console_errors: report.console_errors.length,
      generic_404_console_errors: generic404Console.length,
      unexpected_console_errors: unexpectedConsole.length,
      known_gap_404_responses: known404.length,
      unexpected_404_responses: unexpected404.length,
      screenshots: report.screenshots.length,
    };
    if (blocked.length) report.failures.push({ name: 'request-safety-gate', error: `Blocked requests observed: ${blocked.length}` });
    if (unexpected404.length) report.failures.push({ name: 'unexpected-404s', error: `Unexpected 404 responses: ${unexpected404.map(item => item.url).join(', ')}` });
    if (report.request_failed.length) report.failures.push({ name: 'request-failures', error: `Failed requests observed: ${report.request_failed.length}` });
    if (report.page_errors.length) report.failures.push({ name: 'page-errors', error: `Page errors observed: ${report.page_errors.length}` });
    if (unexpectedConsole.length) report.failures.push({ name: 'unexpected-console', error: `Unexpected console errors/warnings observed: ${unexpectedConsole.length}` });
    if (known404.length) report.notes.push(`Known artwork/border gap responses retained separately: ${known404.length}; they are not counted as recovered assets.`);
    report.passed = report.failures.length === 0 && (report.status === 'passed' || (onlyChecks.length > 0 && report.summary.passed_checks > 0));
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ status: report.status, passed: report.passed, checks: report.summary.checks, executed_checks: report.summary.executed_checks, passed_checks: report.summary.passed_checks, failed_checks: report.summary.failed_checks, failures: report.failures.length, blocked_requests: report.summary.blocked_requests, known_gap_404_responses: report.summary.known_gap_404_responses, unexpected_404_responses: report.summary.unexpected_404_responses, screenshots: report.summary.screenshots, output }));
    if (!report.passed && report.status !== 'not_run_server_ready_flag_missing') process.exitCode = 1;
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
