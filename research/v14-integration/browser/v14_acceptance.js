/*
 * Focused V14 RSS-path browser acceptance.
 * The selected source map is the fixed nine-page V14 selection (350 articles).
 * This runner never starts a server and permits only loopback GET/HEAD.
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

const repoRoot = path.resolve(__dirname, '..', '..', '..');
const baseUrlText = option('--base-url', 'http://127.0.0.1:29010');
const prefix = String(option('--prefix', '/WOW-Encyclopedia-Deployable-Archive/'))
  .replace(/^\/*/, '/').replace(/\/*$/, '/').replace(/\/{2,}/g, '/');
const timeoutMs = Number(option('--timeout-ms', '30000'));
const settleMs = Number(option('--settle-ms', '350'));
const playwrightModule = option('--playwright-module', 'playwright');
const output = path.resolve(repoRoot, option('--output', 'research/v14-integration/browser/v14-browser-receipt.json'));
const screenshotDir = path.resolve(repoRoot, option('--screenshot-dir', 'research/v14-integration/browser/screenshots'));
const manifestPath = path.resolve(repoRoot, option('--manifest', '.scratch/offline-navigation-20261015-v14/build-manifest.json'));
const provenancePath = path.resolve(repoRoot, option('--provenance', '.scratch/pages-resources-20261015-v14/export-provenance.json'));
const routeMapPath = path.resolve(repoRoot, option('--route-map', '.scratch/pages-resources-20261015-v14/__offline/route-map.json'));
const selectedPath = path.resolve(repoRoot, option('--selected', 'research/continuous-recovery-20261015/selected-final-rss14-source-map.json'));
const acceptancePath = path.resolve(repoRoot, option('--acceptance', 'research/continuous-recovery-20261015/rss20-acceptance.json'));
const acceptanceSecondaryPath = path.resolve(repoRoot, option('--acceptance-secondary', 'research/continuous-recovery-20261015/rss21-acceptance.json'));
const sourceReceiptArg = option('--source-receipt', '');
const sourcePlanArg = option('--source-plan', '');
const sourceReceiptPath = sourceReceiptArg ? path.resolve(repoRoot, sourceReceiptArg) : '';
const sourcePlanPath = sourcePlanArg ? path.resolve(repoRoot, sourcePlanArg) : '';
const productionPath = path.resolve(repoRoot, option('--production-file', 'tools/export_github_pages.py'));
const expectedManifestSha = option('--expected-manifest-sha256', '');
const expectedProvenanceSha = option('--expected-provenance-sha256', '');
const expectedRouteMapSha = option('--expected-route-map-sha256', '');
const expectedSelectedSha = option('--expected-selected-sha256', '7019d82bca12be63f5ad832ae72729c1ac8b8fa3c4c4b6936f2d452f780d166b');
const expectedAcceptanceSha = option('--expected-acceptance-sha256', 'decc5d48b5a55ffff2026299da1b8822ecd7f87d0ec4fa03e771286ebc346de4');
const expectedAcceptanceSecondarySha = option('--expected-acceptance-secondary-sha256', '535f854d7e13573a8a36b6cc8548ef0f20a08314a62beb4ef52ceecec07130cc');
const expectedSourceReceiptSha = option('--expected-source-receipt-sha256', '');
const expectedSourcePlanSha = option('--expected-source-plan-sha256', '');
const expectedProductionSha = option('--expected-production-sha256', '');
const expectedSourceCount = option('--expected-source-count', '');
const expectedAliasCount = option('--expected-alias-count', '');
const toggleRoute = option('--toggle-route', '/news/rss-07-2007.xml');
const toggleEntryId = option('--toggle-entry-id', 'news7-30-07-513');
const TOGGLE_ACTIONS = ['anchor-center', 'anchor-enter'];
const TOGGLE_REPETITIONS = 1;

const EXPECTED = {
  pageCount: 9,
  postedTotal: 350,
  cssSha256: '69915a4eea19ec455a60b89c64ed661fc55d48bc3a724bdffcc91bd2d617aa7b',
  cssBytes: 109,
};

const report = {
  schema: 'wow-recovery.core-source-v14-focused-browser-receipt.v1',
  status: 'prepared',
  started_utc: new Date().toISOString(),
  finished_utc: null,
  server_ready_flag: hasFlag('--server-ready'),
  base_url: baseUrlText,
  prefix,
  method: 'Loopback server only; Playwright GET/HEAD requests are restricted to the supplied origin and prefix; no server is started.',
  scope: {
    selected_map_is_fixed: true,
    selected_page_count: EXPECTED.pageCount,
    expected_total_posted_articles: EXPECTED.postedTotal,
    date_frequency_rule: 'article_posted_date_count must equal the sum of article_posted_dates frequencies; unique date-key count is not used as article count.',
    shared_css: '/news/newsarchive.css',
    shared_css_expected_bytes: EXPECTED.cssBytes,
    shared_css_expected_sha256: EXPECTED.cssSha256,
    one_real_title_click: 'Choose one genuinely default-collapsed news entry from the first selected page, click its visible h1 a once, record before/after state, and save one expanded-entry screenshot.',
    july_toggle_regressions: TOGGLE_ACTIONS.map(name => name + ': one fresh context with two activations, collapsed -> expanded -> collapsed'),
    july_toggle_route: toggleRoute,
    july_toggle_entry_id: toggleEntryId,
    july_anchor_expectation: 'Matched derived news-toggle anchor expected 14px by 11px; original href and nearest hoverContainer onclick are recorded.',
    old_v13_pointer_and_enter_matrix: 'Not rerun as a full matrix; only the two retained July anchor regressions run below.',
    screenshot_limit: 1,
    no_force_click_or_dom_mutation: true,
  },
  inputs: {},
  command: null,
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
let manifestJson;
let provenanceJson;
let routeMapJson;
let targets = [];

function relative(file) { return path.relative(repoRoot, file).replace(/\\/g, '/'); }

function readJsonInput(label, absolutePath, expectedSha256, required = true) {
  if (!absolutePath) {
    report.inputs[label] = { path: null, skipped: true, reason: 'not supplied until final V14 source acceptance' };
    return null;
  }
  if (!fs.existsSync(absolutePath)) {
    if (!required) {
      report.inputs[label] = { path: relative(absolutePath), skipped: true, reason: 'not present in preparation tree' };
      return null;
    }
    fail('input not found: ' + relative(absolutePath));
  }
  const data = fs.readFileSync(absolutePath);
  const sha256 = sha256Hex(data);
  report.inputs[label] = { path: relative(absolutePath), bytes: data.length, sha256 };
  if (expectedSha256) {
    report.inputs[label].expected_sha256 = expectedSha256;
    expect(sha256 === expectedSha256, label + ' SHA changed: ' + sha256 + ' != ' + expectedSha256);
  }
  return JSON.parse(data.toString('utf8'));
}

function readFileBinding(label, absolutePath, expectedSha256) {
  if (!fs.existsSync(absolutePath)) fail('file input not found: ' + relative(absolutePath));
  const data = fs.readFileSync(absolutePath);
  const sha256 = sha256Hex(data);
  report.inputs[label] = { path: relative(absolutePath), bytes: data.length, sha256 };
  if (expectedSha256) {
    report.inputs[label].expected_sha256 = expectedSha256;
    expect(sha256 === expectedSha256, label + ' SHA changed: ' + sha256 + ' != ' + expectedSha256);
  }
  return data;
}

function publishedPathFor(route) {
  const files = Array.isArray(provenanceJson && provenanceJson.files) ? provenanceJson.files : [];
  const item = files.find(candidate => String(candidate.route || '') === route || String(candidate.source_route || '') === route);
  if (item && item.output_path) return String(item.output_path).replace(/\\/g, '/').replace(/^\/+/, '');
  const aliases = (routeMapJson && (routeMapJson.aliases || routeMapJson.route_aliases)) || {};
  if (aliases[route]) return String(aliases[route]).replace(/\\/g, '/').replace(/^\/+/, '');
  return route.replace(/^\/+/, '') + (route.endsWith('.xml') ? '.html' : '');
}

function routeUrl(relativePath) {
  const url = new URL(baseUrl.href);
  url.pathname = prefix + String(relativePath || '').replace(/^\/+/, '');
  url.search = '';
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
  page.on('request', request => report.requests.push({
    check: activeCheck, method: request.method(), url: request.url(),
    resource_type: request.resourceType(), class: requestClass(request.url(), request.method()),
  }));
  page.on('response', response => report.responses.push({
    check: activeCheck, method: response.request().method(), url: response.url(),
    status: response.status(), resource_type: response.request().resourceType(),
  }));
  page.on('requestfailed', request => report.request_failed.push({
    check: activeCheck, method: request.method(), url: request.url(),
    resource_type: request.resourceType(), failure: request.failure(),
  }));
  page.on('pageerror', error => report.page_errors.push({ check: activeCheck, error: String(error) }));
  page.on('console', message => {
    if (['error', 'warning'].includes(message.type())) report.console_errors.push({
      check: activeCheck, type: message.type(), text: message.text(),
    });
  });
}

function sourceRecord(route) {
  const files = Array.isArray(manifestJson && manifestJson.files) ? manifestJson.files : [];
  const record = files.find(item => String(item.route || '') === route);
  expect(record, 'manifest route missing ' + route);
  return record;
}

function routeMonthYear(route) {
  const match = String(route).match(/\/rss-(\d{2})-(\d{4})\.xml$/i);
  expect(match, 'selected route is not an RSS month path: ' + route);
  return { month: Number(match[1]), year: match[2].slice(-2) };
}

function inputSetup() {
  manifestJson = readJsonInput('v14_manifest', manifestPath, expectedManifestSha, true);
  const selectedRaw = readJsonInput('selected_rss_map', selectedPath, expectedSelectedSha, true);
  const acceptance = readJsonInput('rss_acceptance', acceptancePath, expectedAcceptanceSha, true);
  const acceptanceSecondary = readJsonInput('rss21_acceptance', acceptanceSecondaryPath, expectedAcceptanceSecondarySha, true);
  provenanceJson = readJsonInput('final_export_provenance', provenancePath, expectedProvenanceSha, true);
  routeMapJson = readJsonInput('final_export_route_map', routeMapPath, expectedRouteMapSha, true);
  const production = readFileBinding('production_exporter', productionPath, expectedProductionSha);
  const sourceReceipt = readJsonInput('v14_source_receipt', sourceReceiptPath, expectedSourceReceiptSha, false);
  const sourcePlan = readJsonInput('v14_source_plan', sourcePlanPath, expectedSourcePlanSha, false);

  expect(acceptance.accepted === true, 'selected RSS acceptance is not accepted');
  expect(acceptanceSecondary.accepted === true, 'secondary RSS acceptance is not accepted');
  if (sourceReceipt && expectedSourceCount) {
    const count = sourceReceipt.source_count && (sourceReceipt.source_count.v14 || sourceReceipt.source_count.v13 || sourceReceipt.source_count.total);
    expect(Number(count) === Number(expectedSourceCount), 'source receipt count mismatch');
  }
  const rows = Array.isArray(selectedRaw) ? selectedRaw :
    (Array.isArray(selectedRaw.entries) ? selectedRaw.entries : []);
  expect(rows.length === EXPECTED.pageCount,
    'selected page count is not fixed nine: ' + rows.length);
  expect(Array.isArray(manifestJson.files), 'manifest files array missing');
  if (expectedSourceCount) {
    expect(manifestJson.files.length === Number(expectedSourceCount),
      'manifest source count mismatch: ' + manifestJson.files.length);
  }
  const aliases = manifestJson.route_aliases || manifestJson.aliases || {};
  if (expectedAliasCount) {
    expect(Object.keys(aliases).length === Number(expectedAliasCount),
      'manifest alias count mismatch: ' + Object.keys(aliases).length);
  }

  targets = rows.map(row => {
    const route = String(row.target || row.proposed_route || '');
    const routeDate = routeMonthYear(route);
    const dateMap = row.article_posted_dates || {};
    const dates = Object.keys(dateMap);
    const frequencyTotal = dates.reduce((total, date) => total + Number(dateMap[date] || 0), 0);
    const count = Number(row.article_posted_date_count);
    expect(count > 0 && frequencyTotal === count,
      route + ' selected date frequency mismatch: ' + frequencyTotal + ' != ' + count);
    const expectedPattern = new RegExp('^' + routeDate.month + '-\\d{1,2}-' + routeDate.year + '$');
    expect(dates.every(date => expectedPattern.test(date)), route + ' selected month/year mismatch');
    if (row.article_month_matches_url !== undefined) {
      expect(Boolean(row.article_month_matches_url), route + ' selected month flag is false');
    }
    return {
      route,
      published_path: publishedPathFor(route),
      title: String(row.title || ''),
      expected_count: count,
      expected_month: routeDate.month,
      expected_year: routeDate.year,
      source_bytes: Number(row.body_bytes || 0),
      source_sha256: String(row.body_sha256 || ''),
      source_memento: String(row.actual_memento || ''),
      source_event_dates_are_not_article_dates: Boolean(row.source_event_dates_are_not_article_dates),
      unique_date_keys: dates.length,
      date_frequency_total: frequencyTotal,
    };
  });
  const postedTotal = targets.reduce((total, target) => total + target.expected_count, 0);
  expect(postedTotal === EXPECTED.postedTotal,
    'selected posted-date frequency total is not 350: ' + postedTotal);
  const css = sourceRecord('/news/newsarchive.css');
  expect(Number(css.source_length || css.source_bytes || 0) === EXPECTED.cssBytes,
    'newsarchive.css manifest length mismatch');
  expect(String(css.source_sha256 || '') === EXPECTED.cssSha256,
    'newsarchive.css manifest SHA mismatch');
  report.inputs.targets = targets;
  report.inputs.page_count = targets.length;
  report.inputs.posted_total = postedTotal;
  sourceRecord(toggleRoute);
  report.inputs.toggle = {
    route: toggleRoute,
    published_path: publishedPathFor(toggleRoute),
    entry_id: toggleEntryId,
  };
  report.inputs.alias_count = Object.keys(aliases).length;
  report.inputs.css = {
    route: '/news/newsarchive.css',
    published_path: publishedPathFor('/news/newsarchive.css'),
    bytes: EXPECTED.cssBytes,
    sha256: EXPECTED.cssSha256,
  };
  report.inputs.production_exporter = { path: relative(productionPath), sha256: sha256Hex(production) };
  report.inputs.source_manifest_count = manifestJson.files.length;
}

async function navigate(page, target) {
  const publishedPath = typeof target === 'string' ? publishedPathFor(target) : target.published_path;
  const response = await page.goto(routeUrl(publishedPath), { waitUntil: 'domcontentloaded', timeout: timeoutMs });
  expect(response, 'no response for ' + publishedPath);
  await page.waitForTimeout(settleMs);
  return { requested: routeUrl(publishedPath), response, final_url: page.url() };
}

async function fetchPayload(page, relativePath) {
  return page.evaluate(async target => {
    const response = await fetch(target, { cache: 'no-store' });
    const bytes = new Uint8Array(await response.arrayBuffer());
    const digest = await crypto.subtle.digest('SHA-256', bytes);
    const sha256 = [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2, '0')).join('');
    return { url: target, status: response.status, bytes: bytes.byteLength, sha256, content_type: response.headers.get('content-type') || '' };
  }, routeUrl(relativePath));
}

async function pageDates(page) {
  return page.evaluate(() => {
    const normalize = value => (value || '').replace(/\s+/g, ' ').trim();
    const dateTokens = value => (normalize(value).match(/\b\d{1,2}-\d{1,2}-\d{2}\b/g) || []).map(token => {
      const [month, day, year] = token.split('-');
      return String(Number(month)) + '-' + String(Number(day)) + '-' + year;
    });
    const postedNodes = [...document.querySelectorAll('.posted-date')];
    const entryNodes = [...document.querySelectorAll('.news-entry-date')];
    const posted_dates = postedNodes.flatMap(node => dateTokens(node.textContent));
    const entry_dates = entryNodes.flatMap(node => dateTokens(node.textContent));
    const body = normalize(document.body && (document.body.innerText || document.body.textContent));
    return {
      title: document.title,
      url: location.href,
      visible_text_length: body.length,
      headings: [...document.querySelectorAll('h1')].map(node => normalize(node.textContent)).filter(Boolean),
      posted_dates,
      entry_dates,
      posted_node_count: postedNodes.length,
      entry_node_count: entryNodes.length,
    };
  });
}

async function cssDom(page) {
  return page.evaluate(() => {
    const links = [...document.querySelectorAll('link[rel~="stylesheet"]')];
    const link = links.find(node => {
      try { return new URL(node.href, document.baseURI).pathname.endsWith('/news/newsarchive.css'); }
      catch (_) { return false; }
    });
    return { href: link ? link.href : '', attached: Boolean(link && link.sheet), link_count: links.length };
  });
}

async function articleState(entry) {
  return entry.evaluate(root => {
    const state = node => {
      if (!node) return null;
      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return {
        display: style.display,
        visibility: style.visibility,
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        has_client_rects: Boolean(node.getClientRects().length),
        visible: Boolean(node.getClientRects().length && rect.width > 0 && rect.height > 0 &&
          style.display !== 'none' && style.visibility !== 'hidden'),
      };
    };
    const heading = root.querySelector('h1 a');
    const item = root.querySelector('.news-item');
    const description = root.querySelector('description');
    const hover = root.querySelector('.hoverContainer');
    return {
      entry_id: root.id || '',
      class_name: root.className || '',
      heading_text: heading ? (heading.textContent || '').replace(/\s+/g, ' ').trim() : '',
      heading_href: heading ? heading.getAttribute('href') || '' : '',
      parent_onclick: hover ? hover.getAttribute('onclick') || '' : '',
      body: state(document.body),
      news_item: state(item),
      description: state(description),
    };
  });
}

async function expandOne(page, target) {
  const headings = page.locator('h1 a');
  let heading = null;
  let entry = null;
  let before = null;
  for (let index = 0; index < await headings.count(); index += 1) {
    const candidate = headings.nth(index);
    const candidateEntry = candidate.locator('xpath=ancestor::div[starts-with(@id, "news") and starts-with(@class, "news-")]').first();
    if (await candidateEntry.count() !== 1) continue;
    const state = await articleState(candidateEntry);
    const box = await candidate.boundingBox();
    if (box && state.news_item && state.news_item.display === 'none') {
      heading = candidate;
      entry = candidateEntry;
      before = state;
      break;
    }
  }
  expect(heading && entry && before, 'no default-collapsed news entry with visible h1 a found');
  await heading.click({ timeout: timeoutMs });
  await page.waitForTimeout(settleMs);
  const after = await articleState(entry);
  expect(after.news_item && after.news_item.visible && after.description && after.description.visible,
    'title click did not expose article body');
  const screenshot = path.join(screenshotDir, 'v14-title-expanded.png');
  fs.mkdirSync(path.dirname(screenshot), { recursive: true });
  await entry.screenshot({ path: screenshot });
  const data = fs.readFileSync(screenshot);
  report.screenshots.push({
    label: 'v14-title-expanded',
    path: relative(screenshot),
    bytes: data.length,
    sha256: sha256Hex(data),
  });
  return {
    route: target.route,
    entry_id: after.entry_id,
    selected_title: after.heading_text,
    click: { method: 'Playwright locator.click', selector: 'h1 a', performed: true },
    before,
    after,
    screenshot: relative(screenshot),
  };
}

async function toggleSnapshot(entry) {
  return entry.evaluate(root => {
    const state = node => {
      if (!node) return null;
      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return {
        display: style.display,
        visibility: style.visibility,
        opacity: style.opacity,
        hidden: Boolean(node.hidden),
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        has_client_rects: Boolean(node.getClientRects().length),
        visible: Boolean(node.getClientRects().length && rect.width > 0 && rect.height > 0 &&
          style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0'),
      };
    };
    const heading = root.querySelector('h1 a');
    const li = root.querySelector('li.news-toggle');
    const anchor = root.querySelector('li.news-toggle a');
    const hover = root.querySelector('.hoverContainer');
    const item = root.querySelector('.news-item');
    const description = root.querySelector('description');
    return {
      entry_id: root.id || '',
      class_name: root.className || '',
      body: state(document.body),
      news_item: state(item),
      description: state(description),
      li: state(li),
      anchor: state(anchor),
      heading: state(heading),
      href: anchor ? anchor.getAttribute('href') || '' : '',
      parent_onclick: hover ? hover.getAttribute('onclick') || '' : '',
      parent_class: hover ? hover.className || '' : '',
      anchor_text: anchor ? (anchor.textContent || '').replace(/\s+/g, ' ').trim() : '',
      heading_text: heading ? (heading.textContent || '').replace(/\s+/g, ' ').trim() : '',
    };
  });
}

async function findToggleEntry(page) {
  const entry = page.locator('#' + toggleEntryId).first();
  expect(await entry.count() === 1, 'toggle entry not found: ' + toggleEntryId);
  const li = entry.locator('li.news-toggle').first();
  const anchor = li.locator('a').first();
  expect(await li.count() === 1 && await anchor.count() === 1, 'toggle entry news-toggle anchor missing');
  const before = await toggleSnapshot(entry);
  expect(before.entry_id === toggleEntryId, 'toggle entry identity mismatch: ' + before.entry_id);
  expect(before.news_item && !before.news_item.visible, 'toggle entry was not initially collapsed');
  expect(before.description && !before.description.visible, 'toggle description was not initially collapsed');
  return { entry, li, anchor, before };
}

function toggleExpanded(state) {
  return Boolean(state && state.news_item && state.news_item.visible &&
    state.description && state.description.visible);
}

function toggleCollapsed(state) {
  return Boolean(state && state.news_item && !state.news_item.visible &&
    state.description && !state.description.visible);
}

async function activateToggle(control, page, kind) {
  const box = await control.anchor.boundingBox();
  expect(box, 'toggle anchor has no bounding box');
  expect(Math.round(box.width) === 14 && Math.round(box.height) === 11,
    'toggle anchor box is not 14x11: ' + JSON.stringify(box));
  if (kind === 'anchor-center') {
    const coordinates = { x: box.x + box.width / 2, y: box.y + box.height / 2, width: box.width, height: box.height };
    await page.mouse.click(coordinates.x, coordinates.y);
    return { method: 'page.mouse.click', selector: 'li.news-toggle a center', coordinates };
  }
  if (kind === 'anchor-enter') {
    await control.anchor.focus();
    const active_before = await page.evaluate(() => {
      const node = document.activeElement;
      return { tag: node ? node.tagName : '', href: node && node.getAttribute ? node.getAttribute('href') || '' : '' };
    });
    await control.anchor.press('Enter');
    const active_after = await page.evaluate(() => {
      const node = document.activeElement;
      return { tag: node ? node.tagName : '', href: node && node.getAttribute ? node.getAttribute('href') || '' : '' };
    });
    return { method: 'locator.focus + locator.press(Enter)', selector: 'li.news-toggle a', coordinates: null, active_before, active_after };
  }
  fail('unknown July toggle interaction kind: ' + kind);
}

async function runToggleRegression(kind, repetition) {
  const pair = await newContext();
  try {
    const page = pair.page;
    const loaded = await navigate(page, toggleRoute);
    expect(loaded.response.status() === 200, toggleRoute + ' HTTP ' + loaded.response.status());
    const control = await findToggleEntry(page);
    const before = control.before;
    const firstAction = await activateToggle(control, page, kind);
    await page.waitForTimeout(settleMs);
    const afterFirst = await toggleSnapshot(control.entry);
    expect(toggleExpanded(afterFirst), kind + ' first activation did not expand entry');
    const secondAction = await activateToggle(control, page, kind);
    await page.waitForTimeout(settleMs);
    const afterSecond = await toggleSnapshot(control.entry);
    expect(toggleCollapsed(afterSecond), kind + ' second activation did not collapse entry');
    return {
      route: toggleRoute,
      entry_id: toggleEntryId,
      repetition,
      final_url: loaded.final_url,
      before,
      first: { action: firstAction, state: afterFirst },
      second: { action: secondAction, state: afterSecond },
      href: before.href,
      parent_onclick: before.parent_onclick,
      anchor_box: before.anchor && before.anchor.rect ? { width: before.anchor.rect.width, height: before.anchor.rect.height } : null,
      li_box: before.li && before.li.rect ? { width: before.li.rect.width, height: before.li.rect.height } : null,
    };
  } finally {
    await pair.context.close();
  }
}

async function newContext() {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, serviceWorkers: 'block' });
  await context.route('**/*', async route => {
    const request = route.request();
    const classification = requestClass(request.url(), request.method());
    const allowed = classification === 'local-allowed';
    report.route_decisions.push({
      check: activeCheck,
      method: request.method(),
      url: request.url(),
      resource_type: request.resourceType(),
      class: classification,
      action: allowed ? 'continue' : 'abort',
    });
    if (allowed) return route.continue();
    return route.abort();
  });
  const page = await context.newPage();
  attachPage(page);
  return { context, page };
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

function isKnownPlaceholder404(url) {
  try {
    const parsed = new URL(url);
    return /\/__offline\/(?:missing|empty)(?:\.html|\.svg)?$/i.test(parsed.pathname) ||
      /\/missing-image\.svg$/i.test(parsed.pathname);
  } catch (_) { return false; }
}

async function main() {
  if (!hasFlag('--server-ready')) {
    report.status = 'not_run_server_ready_flag_missing';
    report.finished_utc = new Date().toISOString();
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    process.exitCode = 2;
    return;
  }
  try {
    baseUrl = new URL(baseUrlText);
    expect(baseUrl.protocol === 'http:' && ['127.0.0.1', 'localhost', '::1'].includes(baseUrl.hostname.replace(/^\[|\]$/g, '').toLowerCase()),
      'base URL is not loopback: ' + baseUrlText);
    expect(baseUrl.pathname === '/' || baseUrl.pathname === '', 'base URL must not include a path: ' + baseUrlText);
    expect(timeoutMs > 0 && settleMs >= 0, 'invalid timeout/settle values');
    report.inputs.runner = {
      path: relative(__filename),
      bytes: fs.statSync(__filename).size,
      sha256: sha256Hex(fs.readFileSync(__filename)),
    };
    report.command = { argv: process.argv.slice(1), node: process.execPath, cwd: repoRoot };
    inputSetup();
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.mkdirSync(screenshotDir, { recursive: true });
    const { chromium } = require(playwrightModule);
    browser = await chromium.launch({ headless: true });
    const pair = await newContext();
    try {
      const page = pair.page;
      for (const target of targets) {
        await runCheck('rss:' + target.route, async () => {
          const loaded = await navigate(page, target);
          expect(loaded.response.status() === 200, target.route + ' HTTP ' + loaded.response.status());
          const info = await pageDates(page);
          const expectedPattern = new RegExp('^' + target.expected_month + '-\\d{1,2}-' + target.expected_year + '$');
          expect(info.visible_text_length > 100, target.route + ' has no visible body');
          expect(info.title.includes(target.title), target.route + ' title mismatch: ' + info.title);
          expect(info.posted_dates.length === target.expected_count,
            target.route + ' posted-date count ' + info.posted_dates.length + ' != ' + target.expected_count);
          expect(info.entry_dates.length === target.expected_count,
            target.route + ' news-entry-date count ' + info.entry_dates.length + ' != ' + target.expected_count);
          expect(info.posted_dates.every(value => expectedPattern.test(value)), target.route + ' posted-date month/year mismatch');
          expect(info.entry_dates.every(value => expectedPattern.test(value)), target.route + ' news-entry-date month/year mismatch');
          expect(JSON.stringify(info.posted_dates) === JSON.stringify(info.entry_dates),
            target.route + ' posted/news-entry dates diverge');
          return {
            route: target.route,
            published_path: target.published_path,
            status: loaded.response.status(),
            final_url: loaded.final_url,
            title: info.title,
            headings: info.headings,
            expected_count: target.expected_count,
            posted_dates: info.posted_dates,
            entry_dates: info.entry_dates,
            source_memento: target.source_memento,
            source_bytes: target.source_bytes,
            source_sha256: target.source_sha256,
          };
        });
      }

      await runCheck('newsarchive:shared-css-real-response-all-selected-pages', async () => {
        const pages = [];
        for (const target of targets) {
          await navigate(page, target);
          const dom = await cssDom(page);
          const css = await fetchPayload(page, '/news/newsarchive.css');
          expect(dom.attached, target.route + ' newsarchive.css is not attached to real DOM');
          expect(css.status === 200 && css.bytes === EXPECTED.cssBytes && css.sha256 === EXPECTED.cssSha256,
            target.route + ' CSS payload mismatch: ' + JSON.stringify(css));
          expect(css.content_type.toLowerCase().split(';')[0] === 'text/css',
            target.route + ' CSS MIME mismatch: ' + css.content_type);
          pages.push({ route: target.route, dom, css });
        }
        return { page_count: pages.length, css_route: '/news/newsarchive.css', pages };
      });
    } finally {
      await pair.context.close();
    }

    await runCheck('news:one-default-collapsed-title-link-expansion', async () => {
      const first = targets[0];
      const interactionPair = await newContext();
      try {
        const page = interactionPair.page;
        const loaded = await navigate(page, first);
        expect(loaded.response.status() === 200, first.route + ' HTTP ' + loaded.response.status());
        return await expandOne(page, first);
      } finally {
        await interactionPair.context.close();
      }
    });
    for (const kind of TOGGLE_ACTIONS) {
      for (let repetition = 1; repetition <= TOGGLE_REPETITIONS; repetition += 1) {
        await runCheck('july-toggle:' + kind + ':fresh-' + repetition,
          () => runToggleRegression(kind, repetition));
      }
    }
    report.status = report.failures.length ? 'completed_with_failures' : 'passed';
  } catch (error) {
    report.status = 'runner_error';
    report.failures.push({ name: 'runner', error: String(error) });
  } finally {
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    const blocked = report.route_decisions.filter(item => item.action === 'abort');
    const all404 = report.responses.filter(item => item.status === 404);
    const known404 = all404.filter(item => isKnownPlaceholder404(item.url));
    const unknown404 = all404.filter(item => !isKnownPlaceholder404(item.url));
    report.diagnostics = {
      requests: report.requests.length,
      responses: report.responses.length,
      blocked_requests: blocked.length,
      known_placeholder_404: known404,
      unknown_404: unknown404,
      request_failures: report.request_failed,
      page_errors: report.page_errors,
      console_errors: report.console_errors,
    };
    if (blocked.length) report.failures.push({ name: 'request-safety-gate', error: 'Blocked requests observed: ' + blocked.length });
    if (unknown404.length) report.failures.push({ name: 'unknown-404', error: unknown404.map(item => item.url).join(', ') });
    if (report.request_failed.length) report.failures.push({ name: 'request-failures', error: 'Request failures observed: ' + report.request_failed.length });
    if (report.page_errors.length) report.failures.push({ name: 'page-errors', error: 'Page errors observed: ' + report.page_errors.length });
    if (report.console_errors.length) report.failures.push({ name: 'console-errors', error: 'Console errors observed: ' + report.console_errors.length });
    if (report.status === 'passed' && report.failures.length) report.status = 'completed_with_failures';
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  }
}

main().catch(error => {
  report.status = 'runner_error';
  report.failures.push({ name: 'unhandled', error: String(error) });
  report.finished_utc = new Date().toISOString();
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
  process.exitCode = 1;
});
