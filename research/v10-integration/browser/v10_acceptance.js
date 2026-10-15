/*
 * Focused browser acceptance for the root-owned v10 Pages export.
 *
 * The runner never starts a server. It is intentionally usable only after the
 * coordinator confirms the loopback server and passes --server-ready. Every
 * browser request is restricted to the supplied loopback origin and project
 * prefix, and only GET/HEAD are allowed.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  return index < 0 ? fallback : process.argv[index + 1];
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function sha256Hex(data) {
  return crypto.createHash('sha256').update(data).digest('hex');
}

function normalizePrefix(value) {
  let prefix = String(value || '/');
  if (!prefix.startsWith('/')) prefix = `/${prefix}`;
  if (!prefix.endsWith('/')) prefix += '/';
  if (prefix.includes('..')) throw new Error(`unsafe project prefix: ${prefix}`);
  return prefix.replace(/\/{2,}/g, '/');
}

function loopbackHost(hostname) {
  const host = String(hostname || '').toLowerCase().replace(/^\[|\]$/g, '');
  return host === '127.0.0.1' || host === 'localhost' || host === '::1';
}

function fail(message) {
  throw new Error(message);
}

function expect(condition, message) {
  if (!condition) fail(message);
}

function readJsonInput(relativePath, expectedSha256 = null) {
  const absolute = path.resolve(repoRoot, relativePath);
  if (!fs.existsSync(absolute)) throw new Error(`input not found: ${relativePath}`);
  const data = fs.readFileSync(absolute);
  const actualSha256 = sha256Hex(data);
  if (expectedSha256 && actualSha256 !== expectedSha256) {
    throw new Error(`input SHA changed: ${relativePath}: ${actualSha256} != ${expectedSha256}`);
  }
  return {
    path: relativePath,
    sha256: actualSha256,
    bytes: data.length,
    json: JSON.parse(data.toString('utf8')),
  };
}

const DEFAULT_BASE_URL = 'http://127.0.0.1:29006';
const DEFAULT_PREFIX = '/WOW-Encyclopedia-Deployable-Archive/';
const DEFAULT_OUTPUT = 'research/v10-integration/browser/v10-browser-receipt.json';
const DEFAULT_SCREENSHOT_DIR = 'research/v10-integration/browser/screenshots';
const DEFAULT_MANIFEST = '.scratch/offline-navigation-20261015-v10/build-manifest.json';
const DEFAULT_PROVENANCE = '.scratch/pages-resources-20261015-v10/export-provenance.json';
const DEFAULT_SOURCE_RECEIPT = 'research/v10-integration/source/v10-source-receipt.json';
const DEFAULT_SOURCE_MAP = 'research/v10-integration/source/v10-additions-source-map.json';
const DEFAULT_SELECTED = 'research/continuous-recovery-20261015/selected-v10-final-additions.json';
const DEFAULT_NATIVE_ACCEPTANCE = 'research/continuous-recovery-20261015/native-viewer-acceptance.json';

const EXPECTED_MANIFEST_SHA256 = 'bc664a728da4bb6c5a49b2c2d46bc2837e2ae40e8a09f6e59c6dc755caa83d86';
const EXPECTED_SOURCE_RECEIPT_SHA256 = '23b7e5cdfc9b26aea42e7fe8840670adb38c29d8e6e0486cb298a65911006cd5';
const EXPECTED_SOURCE_MAP_SHA256 = '369a458b2942da1aadfbf1a5f072ba3df971d43bc34a8e7c570f788214595a74';
const EXPECTED_SELECTED_SHA256 = 'c73b02d2f9353402eb4b568640e1359031e25756604cbbc5f21552f0acd52a55';
const EXPECTED_NATIVE_ACCEPTANCE_SHA256 = 'cf20b540bc6ef0bbea97342aec87f73c99231f8a86ac13dc9a2df6027dab1120';

const repoRoot = path.resolve(__dirname, '..', '..', '..');
const baseUrlText = option('--base-url', DEFAULT_BASE_URL);
const prefix = normalizePrefix(option('--prefix', DEFAULT_PREFIX));
const timeoutMs = Number(option('--timeout-ms', '30000'));
const settleMs = Number(option('--settle-ms', '350'));
const playwrightModule = option('--playwright-module', 'playwright');
const output = path.resolve(repoRoot, option('--output', DEFAULT_OUTPUT));
const screenshotDir = path.resolve(repoRoot, option('--screenshot-dir', DEFAULT_SCREENSHOT_DIR));
const manifestPath = path.resolve(repoRoot, option('--manifest', DEFAULT_MANIFEST));
const provenancePath = path.resolve(repoRoot, option('--provenance', DEFAULT_PROVENANCE));
const sourceReceiptPath = path.resolve(repoRoot, option('--source-receipt', DEFAULT_SOURCE_RECEIPT));
const sourceMapPath = path.resolve(repoRoot, option('--source-map', DEFAULT_SOURCE_MAP));
const selectedPath = path.resolve(repoRoot, option('--selected', DEFAULT_SELECTED));
const nativeAcceptancePath = path.resolve(repoRoot, option('--native-acceptance', DEFAULT_NATIVE_ACCEPTANCE));

const report = {
  schema: 'wow-recovery.core-source-v10-browser-receipt.v1',
  status: 'prepared',
  started_utc: new Date().toISOString(),
  finished_utc: null,
  server_ready_flag: hasFlag('--server-ready'),
  base_url: baseUrlText,
  prefix,
  method: 'External loopback server only; Playwright GET/HEAD requests are restricted to the supplied origin and prefix; other methods are blocked; no server is started by this runner.',
  scope: {
    rss_paths: 7,
    artwork_pages: 2,
    artwork_counter_scripts: { common: 12, locale: 1 },
    artwork_cards: { page1: 9, page2: 4, total: 13 },
    artwork_provenance_pairs: { available: [1, 3, 6, 9, 12], missing: [2, 4, 5, 7, 8, 10, 11, 13] },
    viewer_queries: ['s=1', 's=3', 's=13', 'default', 'empty', '0', '-1', '14', 'duplicate', 'unsafe-integer', 'encoded-expression'],
    decorative_border: 'ssborder1.png is tracked separately from content images',
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
let provenanceAssets = {};

function routePath(relative, query = '') {
  const url = new URL(baseUrl.href);
  url.pathname = prefix + String(relative || '').replace(/^\/+/, '');
  url.search = query;
  url.hash = '';
  return url.toString();
}

function localUrl(value) {
  try {
    const url = new URL(value);
    return url.origin === baseUrl.origin && url.pathname.startsWith(prefix);
  } catch (_) {
    return false;
  }
}

function requestClass(value, method) {
  let url;
  try { url = new URL(value); } catch (_) { return 'invalid-url'; }
  if (!['http:', 'https:'].includes(url.protocol)) return 'non-http';
  const local = url.origin === baseUrl.origin && url.pathname.startsWith(prefix);
  if (!local) return url.origin === baseUrl.origin ? 'local-outside-prefix' : 'external-origin';
  return ['GET', 'HEAD'].includes(String(method).toUpperCase()) ? 'local-allowed' : 'local-non-get';
}

function inputEvidence(label, absolutePath, expectedSha256 = null) {
  if (!fs.existsSync(absolutePath)) {
    report.inputs[label] = { path: path.relative(repoRoot, absolutePath), exists: false };
    throw new Error(`input not found: ${path.relative(repoRoot, absolutePath)}`);
  }
  const data = fs.readFileSync(absolutePath);
  const sha256 = sha256Hex(data);
  const item = { path: path.relative(repoRoot, absolutePath), exists: true, bytes: data.length, sha256 };
  if (expectedSha256) item.expected_sha256 = expectedSha256;
  report.inputs[label] = item;
  if (expectedSha256 && sha256 !== expectedSha256) throw new Error(`${label} SHA changed: ${sha256}`);
  return JSON.parse(data.toString('utf8'));
}

function loadInputs() {
  const manifest = inputEvidence('manifest', manifestPath, EXPECTED_MANIFEST_SHA256);
  const sourceReceipt = inputEvidence('source_receipt', sourceReceiptPath, EXPECTED_SOURCE_RECEIPT_SHA256);
  const sourceMap = inputEvidence('source_map', sourceMapPath, EXPECTED_SOURCE_MAP_SHA256);
  const selected = inputEvidence('selected_additions', selectedPath, EXPECTED_SELECTED_SHA256);
  const native = inputEvidence('native_viewer_acceptance', nativeAcceptancePath, EXPECTED_NATIVE_ACCEPTANCE_SHA256);
  const files = Array.isArray(manifest.files) ? manifest.files : [];
  const routes = new Set(files.map(item => String(item.route || '')));
  expect(files.length === 8338, `v10 manifest route count ${files.length} != 8338`);
  expect(sourceReceipt.status === 'mirror_only_pending_root_export', `unexpected source receipt status ${sourceReceipt.status}`);
  expect(sourceReceipt.source_count && sourceReceipt.source_count.v10 === 8338, 'source receipt v10 count is not 8338');
  expect(Array.isArray(sourceMap.entries) && sourceMap.entries.length === 10, 'source map does not contain 10 additions');
  expect(selected.entry_count === 10, `selected additions count ${selected.entry_count} != 10`);
  expect(native.accepted !== false, 'native viewer acceptance is marked rejected');
  report.inputs.manifest.route_count = files.length;
  report.inputs.manifest.new_routes_present = sourceMap.entries.map(item => ({ route: item.derived_route, present: routes.has(item.derived_route) }));
  report.inputs.manifest.route_alias_count = Object.keys(manifest.route_aliases || {}).length;
  report.inputs.source_receipt.source_count = sourceReceipt.source_count;
  report.inputs.source_receipt.manifest_sha256 = sourceReceipt.v10_output && sourceReceipt.v10_output.manifest_sha256;
  report.inputs.native_viewer_acceptance.accepted = native.accepted;
  rssTargets = sourceMap.entries
    .filter(item => String(item.derived_route || '').startsWith('/news/rss-'))
    .map(item => {
      const provenance = item.selection_provenance || {};
      const dateKeys = Object.keys(provenance.article_posted_dates || {});
      const firstDate = dateKeys[0] || '';
      const pieces = firstDate.split('-');
      const month = Number(pieces[0]);
      const year = pieces[2] || '';
      const title = String(item.title || '').split('->').pop().trim();
      const route = String(item.derived_route);
      return {
        logical: route,
        pages: `${route.replace(/^\//, '')}.html`,
        title,
        title_month_matches_url: item.title_month_matches_url,
        source_anomaly: item.source_anomaly || null,
        expected_date_pattern: firstDate ? `${month}-\\d{1,2}-${year}` : null,
        date_keys: dateKeys,
        actual_memento: item.actual_memento,
        source_sha256: item.sha256,
        source_length: item.content_length,
      };
    });
  expect(rssTargets.length === 7, `RSS target count ${rssTargets.length} != 7`);
  report.inputs.rss_targets = rssTargets;
  if (fs.existsSync(provenancePath)) {
    const provenance = inputEvidence('export_provenance', provenancePath);
    for (const item of Array.isArray(provenance.files) ? provenance.files : []) {
      const route = String(item.route || '');
      const outputRoute = item.output_path ? `/${String(item.output_path).replace(/\\/g, '/')}` : '';
      if (/^\/wrath\/images\/artwork\/(?:en_us\/)?ss\d+(?:-thumb)?\.jpg$/i.test(route)) {
        provenanceAssets[route] = {
          bytes: Number(item.derived_length || item.source_length || 0),
          sha256: String(item.derived_sha256 || item.source_sha256 || ''),
          mime: String(item.mime || ''),
        };
      } else if (/^\/wrath\/images\/artwork\/(?:en_us\/)?ss\d+(?:-thumb)?\.jpg$/i.test(outputRoute)) {
        provenanceAssets[outputRoute] = {
          bytes: Number(item.derived_length || item.source_length || 0),
          sha256: String(item.derived_sha256 || item.source_sha256 || ''),
          mime: String(item.mime || ''),
        };
      }
    }
    report.inputs.export_provenance.artwork_asset_count = Object.keys(provenanceAssets).length;
  } else {
    report.inputs.export_provenance = { path: path.relative(repoRoot, provenancePath), exists: false };
    report.notes.push('v10 export provenance was not present during preparation; it is required for the server-ready run.');
  }
  return { manifest, sourceReceipt, sourceMap, selected, native };
}

function attachPage(page) {
  page.on('request', request => {
    report.requests.push({ check: activeCheck, method: request.method(), url: request.url(), resource_type: request.resourceType(), class: requestClass(request.url(), request.method()) });
  });
  page.on('response', response => {
    report.responses.push({ check: activeCheck, method: response.request().method(), url: response.url(), status: response.status(), resource_type: response.request().resourceType() });
  });
  page.on('requestfailed', request => {
    report.request_failed.push({ check: activeCheck, method: request.method(), url: request.url(), resource_type: request.resourceType(), failure: request.failure() });
  });
  page.on('pageerror', error => report.page_errors.push({ check: activeCheck, error: String(error) }));
  page.on('console', message => {
    if (['error', 'warning'].includes(message.type())) report.console_errors.push({ check: activeCheck, type: message.type(), text: message.text() });
  });
}

async function inspectPage(page) {
  return page.evaluate(() => {
    const body = document.body;
    const text = (body && (body.innerText || body.textContent) || '').replace(/\s+/g, ' ').trim();
    const cards = [...document.querySelectorAll('.ssborder a[href]')].map(anchor => {
      const card = anchor.closest('.ssborder') || anchor.parentElement;
      const rect = card ? card.getBoundingClientRect() : null;
      const linkRect = anchor.getBoundingClientRect();
      const styleText = `${card ? card.getAttribute('style') || '' : ''} ${card ? getComputedStyle(card).backgroundImage || '' : ''}`;
      const urls = [...styleText.matchAll(/url\(["']?([^"')]+)["']?\)/gi)].map(match => new URL(match[1], document.baseURI).href);
      const imageRecords = card ? [...card.querySelectorAll('img')].map(image => ({
        src_attribute: image.getAttribute('src') || '', src: image.currentSrc || image.src || '',
        complete: image.complete, natural_width: image.naturalWidth, natural_height: image.naturalHeight,
        rect: (() => { const r = image.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; })(),
      })) : [];
      const href = anchor.href || '';
      const number = Number(new URL(href).searchParams.get('s'));
      return {
        href, number, thumb: urls.find(url => /ss\d+-thumb\.jpg$/i.test(url)) || '',
        card_rect: rect ? { x: rect.x, y: rect.y, width: rect.width, height: rect.height } : null,
        anchor_rect: { x: linkRect.x, y: linkRect.y, width: linkRect.width, height: linkRect.height },
        images: imageRecords,
      };
    }).filter(item => Number.isInteger(item.number) && item.number > 0);
    return {
      title: document.title,
      bodyText: text.slice(0, 30000),
      visibleTextLength: text.length,
      headings: [...document.querySelectorAll('h1,h2,h3')].map(node => (node.innerText || '').replace(/\s+/g, ' ').trim()).filter(Boolean),
      dates: [...document.querySelectorAll('.date,[class*="date"],time')].map(node => (node.innerText || node.textContent || '').replace(/\s+/g, ' ').trim()).filter(Boolean),
      forms: document.querySelectorAll('form').length,
      scripts: [...document.scripts].map(script => ({ src: script.src || '', inline: !script.src && Boolean((script.textContent || '').trim()) })),
      images: [...document.images].map(image => ({ src: image.currentSrc || image.src || '', complete: image.complete, natural_width: image.naturalWidth, natural_height: image.naturalHeight })),
      cards,
      scrollWidth: Math.max(document.documentElement.scrollWidth, body ? body.scrollWidth : 0),
      viewport: { width: innerWidth, height: innerHeight },
      url: location.href,
    };
  });
}

async function navigate(page, relative, query = '', options = {}) {
  const requested = routePath(relative, query);
  const response = await page.goto(requested, { waitUntil: options.waitUntil || 'domcontentloaded', timeout: timeoutMs });
  if (!response) fail(`no response for ${relative}${query}`);
  if (options.settle !== false) await page.waitForTimeout(settleMs);
  return { requested, response, state: await inspectPage(page), finalUrl: page.url() };
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

function shouldRun(name) {
  const only = String(option('--only', '') || '').split(',').map(item => item.trim()).filter(Boolean);
  return only.length === 0 || only.some(item => name === item || name.startsWith(item));
}

async function runSelectedCheck(name, fn) {
  if (!shouldRun(name)) {
    report.checks.push({ name, passed: null, skipped: true, reason: `--only=${option('--only', '')}` });
    return;
  }
  return runCheck(name, fn);
}

function assertPage(loaded, label, expectedPath = null) {
  expect(loaded.response.status() === 200, `${label} HTTP ${loaded.response.status()}`);
  expect(loaded.state.visibleTextLength > 20, `${label} has no visible body text`);
  expect(loaded.state.title.trim().length > 0, `${label} has empty title`);
  if (expectedPath) expect(new URL(loaded.finalUrl).pathname === prefix + expectedPath, `${label} settled at ${loaded.finalUrl}`);
}

async function browserFetchImage(page, target) {
  return page.evaluate(async url => {
    let response;
    let data = new Uint8Array();
    let contentType = '';
    try {
      response = await fetch(url, { cache: 'no-store' });
      contentType = response.headers.get('content-type') || '';
      data = new Uint8Array(await response.arrayBuffer());
    } catch (error) {
      return { url, status: 0, served_url: '', bytes: 0, sha256: '', content_type: '', decoded: false, natural_width: 0, natural_height: 0, error: String(error) };
    }
    const digest = await crypto.subtle.digest('SHA-256', data);
    const sha256 = [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2, '0')).join('');
    let decoded = false;
    let naturalWidth = 0;
    let naturalHeight = 0;
    try {
      const blobUrl = URL.createObjectURL(new Blob([data], { type: contentType || 'application/octet-stream' }));
      const image = new Image();
      await new Promise(resolve => {
        image.onload = () => resolve();
        image.onerror = () => resolve();
        image.src = blobUrl;
      });
      try { if (image.decode) await image.decode(); } catch (_) { /* onload remains evidence */ }
      decoded = image.naturalWidth > 0 && image.naturalHeight > 0;
      naturalWidth = image.naturalWidth;
      naturalHeight = image.naturalHeight;
      URL.revokeObjectURL(blobUrl);
    } catch (_) { /* retain HTTP/hash evidence */ }
    return { url, status: response.status, served_url: response.url, bytes: data.byteLength, sha256, content_type: contentType, decoded, natural_width: naturalWidth, natural_height: naturalHeight };
  }, target);
}

function screenshotPath(label) {
  return path.join(screenshotDir, label.replace(/[^a-z0-9_.-]+/gi, '_') + '.png');
}

function recordScreenshot(label, file) {
  const data = fs.readFileSync(file);
  report.screenshots.push({ label, path: path.relative(repoRoot, file), bytes: data.length, sha256: sha256Hex(data) });
}

function knownGapUrl(value) {
  try {
    const url = new URL(value);
    if (/\/wrath\/images\/layout\/ssborder1\.png$/i.test(url.pathname)) return true;
    const match = url.pathname.match(/\/wrath\/images\/artwork\/(en_us\/)?ss(\d+)(?:-thumb)?\.jpg$/i);
    if (!match) return false;
    const number = Number(match[2]);
    return match[1] ? number === 1 : [2, 4, 5, 7, 8, 10, 11].includes(number);
  } catch (_) {
    return false;
  }
}

function viewerState(page) {
  return page.evaluate(() => {
    const number = value => Number.isFinite(Number(value)) ? Number(value) : null;
    const current = document.getElementById('dCurrent');
    const total = document.getElementById('dTotal');
    const screen = document.getElementById('Screenie');
    const screenLink = document.getElementById('screenLink');
    const image = window.screenImage;
    return {
      url: location.href,
      now_viewing: number(window.nowViewing),
      d_current: number(current && current.textContent),
      d_total: number(total && total.textContent),
      shot_list_length: Array.isArray(window.shotList) ? window.shotList.length : null,
      shot_list: Array.isArray(window.shotList) ? window.shotList.slice() : [],
      screen_link: screenLink ? screenLink.href : '',
      screen_background: screen ? screen.style.backgroundImage : '',
      screen_image: image ? { src: image.src || '', complete: image.complete, natural_width: image.naturalWidth, natural_height: image.naturalHeight } : null,
      sentinel: Number(window.sentinel),
      has_next: typeof window.nextScreen === 'function',
      has_prev: typeof window.prevScreen === 'function',
    };
  });
}

async function waitViewer(page) {
  await page.waitForFunction(() => Boolean(window.shotList && document.getElementById('dCurrent') && document.getElementById('dTotal') && typeof window.nextScreen === 'function' && typeof window.prevScreen === 'function'), { timeout: timeoutMs });
  await page.waitForTimeout(Math.min(settleMs + 250, 1000));
  return viewerState(page);
}

async function clickViewerControl(page, selector, expectedCurrent) {
  const before = await viewerState(page);
  const control = page.locator(selector).first();
  if (await control.count() === 0) return { before, after: before, clicked: false, expected_current: expectedCurrent, note: 'control_missing' };
  await control.click({ timeout: Math.min(timeoutMs, 5000) });
  await page.waitForTimeout(Math.min(timeoutMs, 1500));
  const after = await viewerState(page);
  return { before, after, clicked: true, expected_current: expectedCurrent, index_changed: before.d_current !== after.d_current, expected_index_observed: after.d_current === expectedCurrent, note: after.d_current === expectedCurrent ? 'index_changed_as_expected' : 'adjacent_asset_gap_or_interaction_issue' };
}

async function main() {
  if (!hasFlag('--server-ready')) {
    report.status = 'not_run_server_ready_flag_missing';
    report.finished_utc = new Date().toISOString();
    report.notes.push('No browser was started; coordinator confirmation of loopback port 29006 and --server-ready are required.');
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
    loadInputs();
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.mkdirSync(screenshotDir, { recursive: true });

    const { chromium } = require(playwrightModule);
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, serviceWorkers: 'block' });
    await context.route('**/*', async route => {
      const request = route.request();
      const cls = requestClass(request.url(), request.method());
      const allowed = cls === 'local-allowed';
      report.route_decisions.push({ check: activeCheck, method: request.method(), url: request.url(), resource_type: request.resourceType(), class: cls, action: allowed ? 'continue' : 'abort' });
      if (allowed) return route.continue();
      return route.abort();
    });
    const page = await context.newPage();
    attachPage(page);
    // Browser-only safety observation for the encoded-expression case. This
    // sentinel is never read by or assigned to the viewer/list functions.
    await page.addInitScript(() => { window.sentinel = 0; });

    await runSelectedCheck('rss:seven-new-paths', async () => {
      const results = [];
      for (const target of rssTargets) {
        const loaded = await navigate(page, target.pages);
        assertPage(loaded, target.logical, target.pages);
        const dateRegex = target.expected_date_pattern ? new RegExp(`(?:^|\\D)${target.expected_date_pattern}(?:\\D|$)`) : null;
        const dateMatch = dateRegex ? dateRegex.exec(loaded.state.bodyText) : null;
        expect(loaded.state.title.includes(target.title), `${target.logical} lost source title fragment ${target.title}`);
        // The source title is authoritative document-title evidence. Some
        // captured RSS templates do not repeat that title in visible body
        // text, while their posted dates remain visible in the articles.
        expect(dateMatch, `${target.logical} has no posted-date evidence matching ${target.expected_date_pattern}`);
        results.push({ route: target.logical, pages_path: target.pages, status: loaded.response.status(), final_path: new URL(loaded.finalUrl).pathname, title: loaded.state.title, headings: loaded.state.headings.slice(0, 12), date_evidence: dateMatch && dateMatch[0], title_month_matches_url: target.title_month_matches_url, source_anomaly: target.source_anomaly });
      }
      return { targets: results };
    });

    let galleryPage1;
    let galleryPage2;
    let allCards = [];
    await runSelectedCheck('wrath:artwork-cards-assets-and-hit-area', async () => {
      await page.setViewportSize({ width: 1440, height: 1000 });
      galleryPage1 = await navigate(page, 'wrath/artwork.xml.html');
      assertPage(galleryPage1, 'Wrath artwork page 1', 'wrath/artwork.xml.html');
      await page.waitForFunction(() => Number.isFinite(window.screenshotsCommonTotal) && Number.isFinite(window.screenshotsLocTotal) && Number.isFinite(window.screenshotsTotal) && Number.isFinite(window.screenshotsPerPage) && document.querySelectorAll('.ssborder a[href]').length > 0, { timeout: timeoutMs });
      const first = await inspectPage(page);
      const firstCounters = await page.evaluate(() => ({ common: Number(window.screenshotsCommonTotal), locale: Number(window.screenshotsLocTotal), total: Number(window.screenshotsTotal), per_page: Number(window.screenshotsPerPage), pages: Number(window.pages), current_page: Number(window.currentPage), counter_scripts: [...document.scripts].map(script => script.src).filter(src => /artworkcounter\.js/i.test(src)) }));
      expect(firstCounters.common === 12 && firstCounters.locale === 1 && firstCounters.total === 13, `unexpected artwork counters ${JSON.stringify(firstCounters)}`);
      expect(firstCounters.per_page === 9, `unexpected screenshotsPerPage ${firstCounters.per_page}`);
      expect(firstCounters.counter_scripts.length === 2, `expected two artwork counter scripts, got ${firstCounters.counter_scripts.length}`);
      expect(first.cards.length === 9, `artwork page 1 card count ${first.cards.length}`);
      galleryPage2 = await navigate(page, 'wrath/artwork.xml.html', '?s=2');
      assertPage(galleryPage2, 'Wrath artwork page 2', 'wrath/artwork.xml.html');
      await page.waitForFunction(() => document.querySelectorAll('.ssborder a[href]').length > 0, { timeout: timeoutMs });
      const second = await inspectPage(page);
      expect(second.cards.length === 4, `artwork page 2 card count ${second.cards.length}`);
      allCards = [...first.cards.map(card => ({ page: 1, ...card })), ...second.cards.map(card => ({ page: 2, ...card }))].sort((a, b) => a.number - b.number);
      expect(allCards.length === 13 && allCards.every(card => card.number >= 1 && card.number <= 13), `artwork card number set invalid: ${JSON.stringify(allCards.map(card => card.number))}`);
      const hitArea = allCards.map(card => ({ number: card.number, width: card.anchor_rect.width, height: card.anchor_rect.height }));
      expect(hitArea.every(item => Math.abs(item.width - 243) <= 2 && Math.abs(item.height - 193) <= 2), `artwork anchor hit area not 243x193: ${JSON.stringify(hitArea)}`);
      const imageTargets = allCards.flatMap(card => {
        const number = card.number;
        const full = number <= 12 ? `wrath/images/artwork/ss${number}.jpg` : `wrath/images/artwork/en_us/ss${number - 12}.jpg`;
        const thumb = number <= 12 ? `wrath/images/artwork/ss${number}-thumb.jpg` : `wrath/images/artwork/en_us/ss${number - 12}-thumb.jpg`;
        return [{ number, role: 'full', route: full, url: routePath(full) }, { number, role: 'thumbnail', route: thumb, url: routePath(thumb) }];
      });
      const assetResults = [];
      for (const target of imageTargets) {
        const result = await browserFetchImage(page, target.url);
        const expected = provenanceAssets[`/${target.route}`] || null;
        const exact = Boolean(expected && result.status >= 200 && result.status < 300 && result.bytes === expected.bytes && result.sha256 === expected.sha256 && result.content_type.toLowerCase().split(';')[0] === expected.mime.toLowerCase().split(';')[0] && result.decoded);
        assetResults.push({ ...target, ...result, expected_provenance: expected, provenance_match: exact });
      }
      const pairs = new Map();
      for (const item of assetResults) { if (!pairs.has(item.number)) pairs.set(item.number, []); pairs.get(item.number).push(item); }
      const available = [...pairs.entries()].filter(([, items]) => items.every(item => item.provenance_match)).map(([number]) => number).sort((a, b) => a - b);
      const missing = [...pairs.entries()].filter(([, items]) => items.some(item => !item.provenance_match)).map(([number]) => number).sort((a, b) => a - b);
      expect(JSON.stringify(available) === JSON.stringify([1, 3, 6, 9, 12]), `available image pairs changed: ${JSON.stringify(available)}`);
      expect(JSON.stringify(missing) === JSON.stringify([2, 4, 5, 7, 8, 10, 11, 13]), `missing image pairs changed: ${JSON.stringify(missing)}`);
      const borderRequests = report.responses.filter(item => /ssborder1\.png/i.test(item.url) || /missing-image\.svg/i.test(item.url) && /ssborder1\.png/i.test(decodeURIComponent(item.url))).map(item => ({ url: item.url, status: item.status, resource_type: item.resource_type }));
      const firstShot = screenshotPath('wrath-artwork-page-1');
      await page.goto(routePath('wrath/artwork.xml.html'), { waitUntil: 'domcontentloaded', timeout: timeoutMs });
      await page.screenshot({ path: firstShot, fullPage: true });
      recordScreenshot('wrath-artwork-page-1', firstShot);
      const secondShot = screenshotPath('wrath-artwork-page-2');
      await page.goto(routePath('wrath/artwork.xml.html', '?s=2'), { waitUntil: 'domcontentloaded', timeout: timeoutMs });
      await page.screenshot({ path: secondShot, fullPage: true });
      recordScreenshot('wrath-artwork-page-2', secondShot);
      return { counters: firstCounters, page1_cards: first.cards.length, page2_cards: second.cards.length, hit_area: hitArea, available_pairs: available, missing_pairs: missing, card_images: allCards.map(card => ({ page: card.page, number: card.number, href: card.href, thumb: card.thumb, card_rect: card.card_rect, anchor_rect: card.anchor_rect, images: card.images })), decorative_border_requests: borderRequests };
    });

    await runSelectedCheck('wrath:card-center-to-viewer-s12', async () => {
      // The native descending layout renders page 1 as 13,12,...,5 and
      // page 2 as 4,...,1; common12 is therefore on the unqueried page 1.
      await navigate(page, 'wrath/artwork.xml.html');
      const link = page.locator('.ssborder a[href*="s=12"]').first();
      expect(await link.count() > 0, 'artwork card s=12 not found');
      const rawHref = await link.getAttribute('href');
      const box = await link.boundingBox();
      expect(rawHref && box && box.width >= 239 && box.height >= 189, `card s=12 lacks real 243x193 hit area: ${JSON.stringify({ rawHref, box })}`);
      const actualHref = new URL(rawHref, page.url()).toString();
      const clickPoint = { x: box.x + box.width / 2, y: box.y + box.height / 2 };
      const navigation = page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: timeoutMs });
      await page.mouse.click(clickPoint.x, clickPoint.y);
      const response = await navigation;
      expect(response, `no navigation after center click ${actualHref}`);
      const finalUrl = page.url();
      const final = new URL(finalUrl);
      expect(final.pathname === `${prefix}wrath/art.xml.html` || final.pathname === `${prefix}wrath/art.xml`, `center click landed at ${finalUrl}`);
      expect(final.searchParams.get('s') === '12', `center click query changed: ${finalUrl}`);
      const state = await waitViewer(page);
      expect(response.status() === 200, `viewer s=12 HTTP ${response.status()}`);
      expect(state.d_current === 12 && state.d_total === 13 && state.shot_list_length === 13, `viewer s=12 state mismatch: ${JSON.stringify(state)}`);
      const content = await browserFetchImage(page, routePath('wrath/images/artwork/ss12.jpg'));
      const expected = provenanceAssets['/wrath/images/artwork/ss12.jpg'];
      expect(expected && content.status === 200 && content.sha256 === expected.sha256 && content.bytes === expected.bytes && content.decoded, `viewer s=12 did not fetch the accepted common12 image: ${JSON.stringify(content)}`);
      await page.waitForFunction(() => Boolean(window.screenImage && window.screenImage.complete && window.screenImage.naturalWidth > 0 && /ss12\.jpg/i.test(window.screenImage.src || '') && /ss12\.jpg/i.test(document.getElementById('Screenie')?.style.backgroundImage || '')), { timeout: timeoutMs });
      const displayed = await viewerState(page);
      const expectedImagePath = `${prefix}wrath/images/artwork/ss12.jpg`;
      const screenImagePath = displayed.screen_image ? new URL(displayed.screen_image.src).pathname : '';
      const backgroundMatch = (displayed.screen_background.match(/url\(["']?([^"')]+)["']?\)/i) || [])[1] || '';
      const backgroundPath = backgroundMatch ? new URL(backgroundMatch, finalUrl).pathname : '';
      const expectedMime = String(expected.mime || 'image/jpeg').toLowerCase().split(';')[0];
      expect(screenImagePath === expectedImagePath, `viewer screenImage does not display accepted ss12.jpg: ${JSON.stringify({ screen_image: displayed.screen_image, expectedImagePath })}`);
      expect(backgroundPath === expectedImagePath, `viewer #Screenie background does not display accepted ss12.jpg: ${JSON.stringify({ screen_background: displayed.screen_background, expectedImagePath })}`);
      expect(content.content_type.toLowerCase().split(';')[0] === expectedMime, `viewer ss12 MIME mismatch: ${content.content_type} != ${expectedMime}`);
      const shot = screenshotPath('wrath-viewer-s12');
      await page.screenshot({ path: shot, fullPage: true });
      recordScreenshot('wrath-viewer-s12', shot);
      return { logical_href: actualHref, final_url: finalUrl, response_status: response.status(), click_point: clickPoint, state: displayed, image: content, displayed_image: { screen_image_path: screenImagePath, background_path: backgroundPath, expected_mime: expectedMime }, conclusion: 'viewer_route_and_common12_image_verified' };
    });

    await runSelectedCheck('wrath:viewer-query-parser-and-controls', async () => {
      const viewerCases = [
        { name: 'one', query: '?s=1', expected: 1 },
        { name: 'three', query: '?s=3', expected: 3 },
        { name: 'thirteen', query: '?s=13', expected: 13 },
        { name: 'default', query: '', expected: 1 },
        { name: 'empty', query: '?s=', expected: 1 },
        { name: 'zero', query: '?s=0', expected: 1 },
        { name: 'negative', query: '?s=-1', expected: 1 },
        { name: 'out-of-range', query: '?s=14', expected: 1 },
        { name: 'duplicate', query: '?s=3&s=4', expected: 1 },
        { name: 'unsafe-integer', query: '?s=9007199254740992', expected: 1 },
        { name: 'encoded-expression', query: '?s=sentinel%3D99', expected: 1 },
        { name: 'encoded-three', query: '?s=%33', expected: 3 },
      ];
      const pageStates = [];
      for (const item of viewerCases) {
        const loaded = await navigate(page, 'wrath/art.xml.html', item.query);
        assertPage(loaded, `viewer ${item.name}`, 'wrath/art.xml.html');
        const state = await waitViewer(page);
        expect(state.shot_list_length === 13 && state.d_total === 13, `viewer ${item.name} total mismatch: ${JSON.stringify(state)}`);
        expect(state.d_current === item.expected && state.now_viewing === item.expected - 1, `viewer ${item.name} parser mismatch: ${JSON.stringify(state)}`);
        if (item.name === 'encoded-expression') expect(state.sentinel === 0, `encoded expression changed sentinel: ${JSON.stringify(state)}`);
        expect(localUrl(state.screen_link), `viewer ${item.name} screenLink is not local: ${state.screen_link}`);
        pageStates.push({ name: item.name, query: item.query || '(default)', expected_current: item.expected, state });
      }
      await navigate(page, 'wrath/art.xml.html', '?s=12');
      await waitViewer(page);
      const next = await clickViewerControl(page, '.next-text a, a[href^="javascript:nextScreen"]', 11);
      await navigate(page, 'wrath/art.xml.html', '?s=12');
      await waitViewer(page);
      const previous = await clickViewerControl(page, '.prev-text a, a[href^="javascript:prevScreen"]', 13);
      expect(next.clicked && previous.clicked, `viewer controls missing: ${JSON.stringify({ next, previous })}`);
      const partialAssetGaps = [];
      if (!next.expected_index_observed) partialAssetGaps.push({ control: 'next', expected_current: 11, known_missing_route: '/wrath/images/artwork/ss11.jpg', diagnosis: 'partial_asset_gap_or_interaction_issue' });
      if (!previous.expected_index_observed) partialAssetGaps.push({ control: 'previous', expected_current: 13, known_missing_route: '/wrath/images/artwork/en_us/ss1.jpg', diagnosis: 'partial_asset_gap_or_interaction_issue' });
      if (partialAssetGaps.length) {
        report.notes.push(`Viewer controls did not expose the expected index; retained partial asset-gap diagnostics: ${JSON.stringify(partialAssetGaps)}`);
        throw new Error(`viewer control index assertions failed; partial_asset_gaps=${JSON.stringify(partialAssetGaps)} controls=${JSON.stringify({ next, previous })}`);
      }
      return { cases: pageStates, controls: { next_from_common12_to_common11: next, previous_from_common12_to_locale1: previous }, partial_asset_gaps: [], no_synthetic_shot_list: true };
    });

    await runSelectedCheck('root:roothost-and-index-path-safety', async () => {
      const loaded = await navigate(page, '');
      expect(loaded.response.status() === 200, `Pages root HTTP ${loaded.response.status()}`);
      const bad = report.requests.filter(item => /index\.htmlimages/i.test(item.url));
      expect(bad.length === 0, `index.htmlimages request observed: ${JSON.stringify(bad)}`);
      const viewerHost = await page.evaluate(() => ({ roothost: window.roothost || null, href: location.href }));
      return { status: loaded.response.status(), final_url: loaded.finalUrl, visible_text_length: loaded.state.visibleTextLength, viewer_roothost_observed: viewerHost, index_htmlimages_requests: bad };
    });

    await context.close();
    report.status = report.failures.length ? 'completed_with_failures' : 'passed';
  } catch (error) {
    report.status = 'runner_error';
    report.failures.push({ name: 'runner', error: String(error) });
  } finally {
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    const blocked = report.route_decisions.filter(item => item.action === 'abort');
    const known404 = report.responses.filter(item => item.status === 404 && knownGapUrl(item.url));
    const unexpected404 = report.responses.filter(item => item.status === 404 && !knownGapUrl(item.url));
    const known404Urls = new Set(known404.map(item => item.url));
    const unexpectedConsole = report.console_errors.filter(item => {
      if (/Failed to load resource: the server responded with a status of 404/i.test(item.text)) {
        // Chromium's generic 404 console text often omits the URL. When every
        // observed 404 response is already an accepted content/border gap,
        // classify those generic messages as the same known gap evidence.
        return unexpected404.length > 0 && ![...known404Urls].some(url => item.text.includes(url));
      }
      return true;
    });
    report.summary = {
      checks: report.checks.length,
      passed_checks: report.checks.filter(item => item.passed === true).length,
      failed_checks: report.checks.filter(item => item.passed === false).length,
      skipped_checks: report.checks.filter(item => item.skipped === true).length,
      requests: report.requests.length,
      responses: report.responses.length,
      blocked_requests: blocked.length,
      disallowed_requests: blocked.filter(item => item.class !== 'local-outside-prefix').length,
      request_failed: report.request_failed.length,
      page_errors: report.page_errors.length,
      console_errors: report.console_errors.length,
      unexpected_console_errors: unexpectedConsole.length,
      known_gap_404_responses: known404.length,
      unexpected_404_responses: unexpected404.length,
      known_gap_console_errors: report.console_errors.length - unexpectedConsole.length,
      screenshots: report.screenshots.length,
    };
    if (known404.length) report.notes.push(`Known asset-gap responses retained separately: ${known404.length}; content-image gaps and ssborder1 decorative gap are not counted as recovered assets.`);
    if (unexpected404.length) report.failures.push({ name: 'unexpected-404s', error: `Unexpected 404 responses: ${unexpected404.map(item => item.url).join(', ')}` });
    if (blocked.length) report.failures.push({ name: 'request-safety-gate', error: `Blocked requests observed: ${blocked.length}` });
    if (report.request_failed.length) report.failures.push({ name: 'request-failures', error: `Failed requests observed: ${report.request_failed.length}` });
    if (report.page_errors.length) report.failures.push({ name: 'page-errors', error: `Page errors observed: ${report.page_errors.length}` });
    if (unexpectedConsole.length) report.failures.push({ name: 'unexpected-console', error: `Unexpected console errors/warnings observed: ${unexpectedConsole.length}` });
    report.passed = report.status === 'passed' && report.failures.length === 0;
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ status: report.status, passed: report.passed, checks: report.summary.checks, passed_checks: report.summary.passed_checks, failures: report.failures.length, blocked_requests: report.summary.blocked_requests, unexpected_404_responses: report.summary.unexpected_404_responses, screenshots: report.summary.screenshots, output }));
    if (!report.passed && report.status !== 'not_run_server_ready_flag_missing') process.exitCode = 1;
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
