/*
 * Focused V12 RSS-path browser acceptance.
 * This runner never starts a server and only permits loopback GET/HEAD
 * requests under the supplied deployment prefix.
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
const baseUrlText = option('--base-url', 'http://127.0.0.1:29008');
const prefix = String(option('--prefix', '/WOW-Encyclopedia-Deployable-Archive/')).replace(/^\/*/, '/').replace(/\/*$/, '/')
  .replace(/\/{2,}/g, '/');
const timeoutMs = Number(option('--timeout-ms', '30000'));
const settleMs = Number(option('--settle-ms', '350'));
const playwrightModule = option('--playwright-module', 'playwright');
const output = path.resolve(repoRoot, option('--output', 'research/v12-integration/browser/v12-browser-receipt.json'));
const screenshotDir = path.resolve(repoRoot, option('--screenshot-dir', 'research/v12-integration/browser/screenshots'));
const manifestPath = path.resolve(repoRoot, option('--manifest', '.scratch/offline-navigation-20261015-v12/build-manifest.json'));
const provenancePath = path.resolve(repoRoot, option('--provenance', '.scratch/pages-resources-20261015-v12/export-provenance.json'));
const routeMapPath = path.resolve(repoRoot, option('--route-map', '.scratch/pages-resources-20261015-v12/__offline/route-map.json'));
const sourceReceiptPath = path.resolve(repoRoot, option('--source-receipt', 'research/v12-integration/source/v12-source-receipt.json'));
const selectedPath = path.resolve(repoRoot, option('--selected', 'research/continuous-recovery-20261015/selected-rss16-source-map.json'));
const acceptancePath = path.resolve(repoRoot, option('--acceptance', 'research/continuous-recovery-20261015/rss16-acceptance.json'));

const EXPECTED = {
  manifest: '590f06cf30266d0b6fc02a365d9810a564693e9dd67e3051572bfc414a570b16',
  sourceReceipt: '5b935a587487e6eaa25a2ea662710b57fd3a17a3fa72afa2589791591e8c95c1',
  selected: '04cd170e67bb4c7efeb143cb43314ba33ee03ed1837478220d88dabffe6f76eb',
  acceptance: '8dee2630b9e84caca3588fc578c40c8930d68f9d0cd7b3b5f3d0568fbcbe1a43',
  sourceCount: 8344,
  aliasCount: 183,
  cssSha256: '69915a4eea19ec455a60b89c64ed661fc55d48bc3a724bdffcc91bd2d617aa7b',
  cssBytes: 109,
};

const report = {
  schema: 'wow-recovery.core-source-v12-browser-receipt.v1',
  status: 'prepared',
  started_utc: new Date().toISOString(),
  finished_utc: null,
  server_ready_flag: hasFlag('--server-ready'),
  base_url: baseUrlText,
  prefix,
  method: 'Loopback server only; Playwright GET/HEAD requests are restricted to the supplied origin and prefix; no server is started.',
  scope: {
    rss_paths: ['/news/rss-07-2007.xml', '/news/rss-06-2007.xml', '/news/rss-04-2007.xml'],
    expected_posted_dates: { '/news/rss-07-2007.xml': 57, '/news/rss-06-2007.xml': 49, '/news/rss-04-2007.xml': 39 },
    shared_css: '/news/newsarchive.css',
    accordion: 'one real default-collapsed news entry chosen from the July page and expanded by visible h1 a locator.click',
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
let targets = [];
let manifestJson;
let provenanceJson;
let routeMapJson;
let cssRecord;

function relative(file) { return path.relative(repoRoot, file).replace(/\\/g, '/'); }

function readJsonInput(label, absolutePath, expectedSha256 = null) {
  if (!fs.existsSync(absolutePath)) fail(`input not found: ${relative(absolutePath)}`);
  const data = fs.readFileSync(absolutePath);
  const sha256 = sha256Hex(data);
  report.inputs[label] = { path: relative(absolutePath), bytes: data.length, sha256 };
  if (expectedSha256) {
    report.inputs[label].expected_sha256 = expectedSha256;
    expect(sha256 === expectedSha256, `${label} SHA changed: ${sha256} != ${expectedSha256}`);
  }
  return JSON.parse(data.toString('utf8'));
}

function publishedPathFor(route) {
  const files = Array.isArray(provenanceJson && provenanceJson.files) ? provenanceJson.files : [];
  const item = files.find(candidate => String(candidate.route || '') === route || String(candidate.source_route || '') === route);
  if (item && item.output_path) return String(item.output_path).replace(/\\/g, '/').replace(/^\/+/, '');
  const aliases = (routeMapJson && routeMapJson.aliases) || {};
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
  page.on('request', request => report.requests.push({ check: activeCheck, method: request.method(), url: request.url(), resource_type: request.resourceType(), class: requestClass(request.url(), request.method()) }));
  page.on('response', response => report.responses.push({ check: activeCheck, method: response.request().method(), url: response.url(), status: response.status(), resource_type: response.request().resourceType() }));
  page.on('requestfailed', request => report.request_failed.push({ check: activeCheck, method: request.method(), url: request.url(), resource_type: request.resourceType(), failure: request.failure() }));
  page.on('pageerror', error => report.page_errors.push({ check: activeCheck, error: String(error) }));
  page.on('console', message => {
    if (['error', 'warning'].includes(message.type())) report.console_errors.push({ check: activeCheck, type: message.type(), text: message.text() });
  });
}

function sourceRecord(route) {
  const files = Array.isArray(manifestJson && manifestJson.files) ? manifestJson.files : [];
  const record = files.find(item => String(item.route || '') === route);
  expect(record, `manifest route missing ${route}`);
  return record;
}

function inputSetup() {
  manifestJson = readJsonInput('v12_manifest', manifestPath, EXPECTED.manifest);
  const sourceReceipt = readJsonInput('v12_source_receipt', sourceReceiptPath, EXPECTED.sourceReceipt);
  const selected = readJsonInput('selected_rss16', selectedPath, EXPECTED.selected);
  const acceptance = readJsonInput('rss16_acceptance', acceptancePath, EXPECTED.acceptance);
  provenanceJson = readJsonInput('final_export_provenance', provenancePath);
  routeMapJson = readJsonInput('final_export_route_map', routeMapPath);
  expect(Array.isArray(manifestJson.files) && manifestJson.files.length === EXPECTED.sourceCount, `manifest source count mismatch: ${manifestJson.files && manifestJson.files.length}`);
  expect(Object.keys(manifestJson.route_aliases || {}).length === EXPECTED.aliasCount, 'manifest alias count mismatch');
  expect(sourceReceipt.source_count && sourceReceipt.source_count.v12 === EXPECTED.sourceCount, 'source receipt count mismatch');
  expect(selected.entry_count === 3 && Array.isArray(selected.entries) && selected.entries.length === 3, 'RSS16 selection count mismatch');
  expect(acceptance.accepted === true && acceptance.valid_expanded_HTML_entities === 3, 'RSS16 acceptance is not accepted');
  cssRecord = sourceRecord('/news/newsarchive.css');
  expect(Number(cssRecord.source_length || cssRecord.source_bytes || 0) === EXPECTED.cssBytes, 'newsarchive.css manifest length mismatch');
  expect(String(cssRecord.source_sha256 || '') === EXPECTED.cssSha256, 'newsarchive.css manifest SHA mismatch');
  targets = selected.entries.map(item => {
    const route = String(item.target || item.proposed_route || '');
    const dates = Object.keys(item.article_posted_dates || {});
    const first = dates[0] || '';
    const parts = first.split('-');
    return {
      route,
      published_path: publishedPathFor(route),
      title: String(item.title || ''),
      expected_count: Number(item.article_posted_date_count),
      expected_month: Number(parts[0]),
      expected_year: parts[2] || '',
      source_bytes: Number(item.body_bytes),
      source_sha256: String(item.body_sha256 || ''),
      source_memento: String(item.actual_memento || ''),
      source_event_dates_are_not_article_dates: Boolean(item.source_event_dates_are_not_article_dates),
    };
  });
  expect(targets.map(item => item.expected_count).join(',') === '57,49,39', `posted-date counts changed: ${targets.map(item => item.expected_count).join(',')}`);
  report.inputs.targets = targets;
  report.inputs.published_paths = targets.map(item => ({ route: item.route, published_path: item.published_path }));
  report.inputs.css = { route: '/news/newsarchive.css', published_path: publishedPathFor('/news/newsarchive.css'), source_sha256: EXPECTED.cssSha256, source_bytes: EXPECTED.cssBytes };
}

async function navigate(page, target) {
  const requested = routeUrl(target.published_path);
  const response = await page.goto(requested, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
  expect(response, `no response for ${target.route}`);
  await page.waitForTimeout(settleMs);
  return { requested, response, final_url: page.url() };
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

async function pageDates(page, target) {
  return page.evaluate(() => {
    const normalize = value => (value || '').replace(/\s+/g, ' ').trim();
    const dateTokens = value => (normalize(value).match(/\b\d{1,2}-\d{1,2}-\d{2}\b/g) || []).map(token => {
      const [month, day, year] = token.split('-');
      return `${Number(month)}-${Number(day)}-${year}`;
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
    const link = links.find(node => { try { return new URL(node.href, document.baseURI).pathname.endsWith('/news/newsarchive.css'); } catch (_) { return false; } });
    return { href: link ? link.href : '', attached: Boolean(link && link.sheet), link_count: links.length };
  });
}

async function articleState(entry) {
  return entry.evaluate(root => {
    const state = node => {
      if (!node) return null;
      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return { display: style.display, visibility: style.visibility, rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }, has_client_rects: Boolean(node.getClientRects().length), visible: Boolean(node.getClientRects().length && rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden') };
    };
    const heading = root.querySelector('h1 a');
    const item = root.querySelector('.news-item');
    const description = root.querySelector('description');
    const hover = root.querySelector('.hoverContainer');
    const toggle = root.querySelector('li.news-toggle a');
    return { entry_id: root.id || '', class_name: root.className || '', title: heading ? (heading.textContent || '').replace(/\s+/g, ' ').trim() : '', title_href: heading ? heading.getAttribute('href') || '' : '', hover_onclick: hover ? hover.getAttribute('onclick') || '' : '', toggle_href: toggle ? toggle.getAttribute('href') || '' : '', news_item: state(item), description: state(description) };
  });
}

async function expandOne(page, target) {
  const headings = page.locator('h1 a');
  let heading = null;
  let entry = null;
  let before = null;
  for (let index = 0; index < await headings.count(); index += 1) {
    const candidate = headings.nth(index);
    const text = ((await candidate.textContent()) || (await candidate.innerText()) || '').replace(/\s+/g, ' ').trim();
    if (!text) continue;
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
  expect(heading && entry && before, 'no default-collapsed news entry with a visible title link was found');
  await heading.click({ timeout: timeoutMs });
  await page.waitForTimeout(settleMs);
  const after = await articleState(entry);
  expect(after.news_item && after.news_item.visible && after.description && after.description.visible, `accordion did not expose article body: ${JSON.stringify({ before, after })}`);
  const label = `v12-expanded-${target.route.split('/').pop()}-${after.entry_id || 'news'}`.replace(/[^a-z0-9_.-]+/gi, '_');
  const screenshot = path.join(screenshotDir, `${label}.png`);
  await page.screenshot({ path: screenshot, fullPage: true });
  const data = fs.readFileSync(screenshot);
  report.screenshots.push({ label, path: relative(screenshot), bytes: data.length, sha256: sha256Hex(data) });
  return { target_page: target.route, selected_title: after.title, click: { method: 'Playwright locator.click', selector: 'h1 a', performed: true }, before, after };
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
    expect(baseUrl.protocol === 'http:' && ['127.0.0.1', 'localhost', '::1'].includes(baseUrl.hostname.replace(/^\[|\]$/g, '').toLowerCase()), `base URL is not loopback: ${baseUrlText}`);
    expect(baseUrl.pathname === '/' || baseUrl.pathname === '', `base URL must not include a path: ${baseUrlText}`);
    expect(timeoutMs > 0 && settleMs >= 0, 'invalid timeout/settle values');
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

    for (const target of targets) {
      await runCheck(`rss:${target.route}`, async () => {
        const loaded = await navigate(page, target);
        expect(loaded.response.status() === 200, `${target.route} HTTP ${loaded.response.status()}`);
        const info = await pageDates(page, target);
        const expectedPattern = new RegExp(`^${target.expected_month}-\\d{1,2}-${target.expected_year}$`);
        expect(info.visible_text_length > 100, `${target.route} has no visible body`);
        expect(info.title.includes(target.title), `${target.route} title mismatch: ${info.title}`);
        expect(info.posted_dates.length === target.expected_count, `${target.route} posted-date count ${info.posted_dates.length} != ${target.expected_count}`);
        expect(info.entry_dates.length === target.expected_count, `${target.route} news-entry-date count ${info.entry_dates.length} != ${target.expected_count}`);
        expect(info.posted_dates.every(value => expectedPattern.test(value)), `${target.route} posted-date month/year mismatch`);
        expect(info.entry_dates.every(value => expectedPattern.test(value)), `${target.route} news-entry-date month/year mismatch`);
        expect(JSON.stringify(info.posted_dates) === JSON.stringify(info.entry_dates), `${target.route} posted/news-entry dates diverge`);
        return { published_path: target.published_path, status: loaded.response.status(), final_url: loaded.final_url, title: info.title, expected_count: target.expected_count, posted_dates: info.posted_dates, entry_dates: info.entry_dates, source_memento: target.source_memento, source_event_dates_are_not_article_dates: target.source_event_dates_are_not_article_dates };
      });
    }

    await runCheck('newsarchive:shared-css-real-response-all-three-pages', async () => {
      const pages = [];
      for (const target of targets) {
        await navigate(page, target);
        const dom = await cssDom(page);
        const css = await fetchPayload(page, publishedPathFor('/news/newsarchive.css'));
        expect(dom.attached, `${target.route} newsarchive.css is not attached to real DOM`);
        expect(css.status === 200 && css.bytes === EXPECTED.cssBytes && css.sha256 === EXPECTED.cssSha256, `${target.route} CSS payload mismatch: ${JSON.stringify(css)}`);
        expect(css.content_type.toLowerCase().split(';')[0] === 'text/css', `${target.route} CSS MIME mismatch: ${css.content_type}`);
        pages.push({ route: target.route, dom, css });
      }
      return { css_route: '/news/newsarchive.css', expected_sha256: EXPECTED.cssSha256, expected_bytes: EXPECTED.cssBytes, pages };
    });

    await runCheck('news:one-default-collapsed-title-link-expansion', async () => {
      await navigate(page, targets[0]);
      return { expansion: await expandOne(page, targets[0]) };
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
    const all404 = report.responses.filter(item => item.status === 404);
    const knownPlaceholder404 = all404.filter(item => /\/__offline\/(?:missing|empty)/i.test(item.url));
    const unknown404 = all404.filter(item => !knownPlaceholder404.includes(item));
    if (blocked.length) report.failures.push({ name: 'request-safety-gate', error: `Blocked requests observed: ${blocked.length}` });
    if (unknown404.length) report.failures.push({ name: 'unknown-404', error: unknown404.map(item => item.url).join(', ') });
    if (report.request_failed.length) report.failures.push({ name: 'request-failures', error: `Request failures observed: ${report.request_failed.length}` });
    if (report.page_errors.length) report.failures.push({ name: 'page-errors', error: `Page errors observed: ${report.page_errors.length}` });
    if (report.console_errors.some(item => item.type === 'error')) report.failures.push({ name: 'console-errors', error: `Console errors observed: ${report.console_errors.filter(item => item.type === 'error').length}` });
    report.summary = {
      checks: report.checks.length,
      executed_checks: report.checks.filter(item => item.skipped !== true).length,
      passed_checks: report.checks.filter(item => item.passed === true).length,
      failed_checks: report.checks.filter(item => item.passed === false).length,
      requests: report.requests.length,
      responses: report.responses.length,
      blocked_requests: blocked.length,
      request_failed: report.request_failed.length,
      page_errors: report.page_errors.length,
      console_errors: report.console_errors.length,
      unknown_404_responses: unknown404.length,
      placeholder_404_responses: knownPlaceholder404.length,
      screenshots: report.screenshots.length,
    };
    report.passed = report.status === 'passed' && report.failures.length === 0;
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ status: report.status, passed: report.passed, checks: report.summary.checks, executed_checks: report.summary.executed_checks, passed_checks: report.summary.passed_checks, failed_checks: report.summary.failed_checks, failures: report.failures.length, blocked_requests: report.summary.blocked_requests, unknown_404_responses: report.summary.unknown_404_responses, screenshots: report.summary.screenshots, output }));
    if (!report.passed && report.status !== 'not_run_server_ready_flag_missing') process.exitCode = 1;
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
