'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const repoRoot = path.resolve(__dirname, '..', '..', '..');
const baseUrlText = 'http://127.0.0.1:29008';
const prefix = '/WOW-Encyclopedia-Deployable-Archive/';
const route = '/news/rss-07-2007.xml.html';
const entryId = 'news7-30-07-513';
const output = path.resolve(repoRoot, 'research/continuous-recovery-20261015/news-toggle-review/news-toggle-review-receipt.json');
const settleMs = 300;

const cases = [
  { id: 'heading-locator-click', action: 'Playwright locator.click on h1 a', target: 'heading' },
  { id: 'li-center-click', action: 'Playwright locator.click on li.news-toggle at its center', target: 'li' },
  { id: 'toggle-anchor-center-click', action: 'Playwright locator.click on li.news-toggle a at its center', target: 'anchor' },
  { id: 'heading-enter', action: 'focus h1 a then Playwright locator.press("Enter")', target: 'heading-enter' },
];

function sha256Hex(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function fail(message) { throw new Error(message); }
function expect(condition, message) { if (!condition) fail(message); }
function relative(file) { return path.relative(repoRoot, file).replace(/\\/g, '/'); }

const report = {
  schema: 'wow-recovery.news-toggle-review.v1',
  status: 'prepared',
  started_utc: new Date().toISOString(),
  finished_utc: null,
  base_url: baseUrlText,
  prefix,
  route,
  entry_id: entryId,
  policy: 'Loopback origin and deployment prefix only; GET/HEAD only; no DOM style or handler changes; no force clicks; no direct toggleEntry calls.',
  runner: {},
  cases: [],
  requests: [],
  responses: [],
  route_decisions: [],
  request_failed: [],
  page_errors: [],
  console_errors: [],
  failures: [],
  notes: [
    'Each case uses a fresh browser context and the same exported July entry.',
    'A collapsed after-state is recorded as observed behavior, not converted into a runner failure.',
  ],
};

function requestClass(value, method, baseUrl) {
  let url;
  try { url = new URL(value); } catch (_) { return 'invalid-url'; }
  if (!['http:', 'https:'].includes(url.protocol)) return 'non-http';
  const local = url.origin === baseUrl.origin && url.pathname.startsWith(prefix);
  if (!local) return url.origin === baseUrl.origin ? 'local-outside-prefix' : 'external-origin';
  return ['GET', 'HEAD'].includes(String(method).toUpperCase()) ? 'local-allowed' : 'local-non-get';
}

function targetUrl(baseUrl) {
  const url = new URL(baseUrl.href);
  url.pathname = prefix + route.replace(/^\/+/, '');
  return url.toString();
}

async function captureState(entry) {
  return entry.evaluate(root => {
    const rectOf = node => {
      if (!node) return null;
      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return {
        display: style.display,
        visibility: style.visibility,
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        has_client_rects: Boolean(node.getClientRects().length),
        visible: Boolean(node.getClientRects().length && rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden'),
      };
    };
    const attr = node => node ? {
      href: node.getAttribute('href') || '',
      onclick: node.getAttribute('onclick') || '',
      box: rectOf(node),
    } : null;
    const heading = root.querySelector('h1 a');
    const li = root.querySelector('li.news-toggle');
    const anchor = li ? li.querySelector('a') : null;
    const hover = root.querySelector('.hoverContainer');
    const item = root.querySelector('.news-item');
    const description = root.querySelector('description');
    return {
      ancestor: { id: root.id || '', class_name: root.className || '' },
      heading: attr(heading),
      li: attr(li),
      toggle_anchor: attr(anchor),
      hover_onclick: hover ? hover.getAttribute('onclick') || '' : '',
      news_item: rectOf(item),
      description: rectOf(description),
    };
  });
}

function centerOf(box) {
  if (!box || !box.rect) return null;
  return { x: box.rect.x + box.rect.width / 2, y: box.rect.y + box.rect.height / 2 };
}

async function runCase(browser, spec, baseUrl) {
  const result = {
    id: spec.id,
    action: spec.action,
    target: spec.target,
    executed: false,
    passed: false,
    before: null,
    after: null,
    interaction: {},
    error: null,
    requests: 0,
    responses: 0,
  };
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, serviceWorkers: 'block' });
  let page;
  try {
    await context.route('**/*', async intercepted => {
      const request = intercepted.request();
      const classification = requestClass(request.url(), request.method(), baseUrl);
      const allowed = classification === 'local-allowed';
      report.route_decisions.push({ case_id: spec.id, method: request.method(), url: request.url(), resource_type: request.resourceType(), class: classification, action: allowed ? 'continue' : 'abort' });
      if (allowed) return intercepted.continue();
      return intercepted.abort();
    });
    page = await context.newPage();
    page.on('request', request => {
      report.requests.push({ case_id: spec.id, method: request.method(), url: request.url(), resource_type: request.resourceType(), class: requestClass(request.url(), request.method(), baseUrl) });
      result.requests += 1;
    });
    page.on('response', response => {
      report.responses.push({ case_id: spec.id, method: response.request().method(), url: response.url(), status: response.status(), resource_type: response.request().resourceType() });
      result.responses += 1;
    });
    page.on('requestfailed', request => report.request_failed.push({ case_id: spec.id, method: request.method(), url: request.url(), failure: request.failure() }));
    page.on('pageerror', error => report.page_errors.push({ case_id: spec.id, error: String(error) }));
    page.on('console', message => {
      if (['error', 'warning'].includes(message.type())) report.console_errors.push({ case_id: spec.id, type: message.type(), text: message.text() });
    });

    const response = await page.goto(targetUrl(baseUrl), { waitUntil: 'domcontentloaded', timeout: 30000 });
    expect(response, 'target navigation returned no response');
    expect(response.status() === 200, `target navigation HTTP ${response.status()}`);
    await page.waitForTimeout(settleMs);
    const entry = page.locator(`#${entryId}`);
    expect(await entry.count() === 1, `entry #${entryId} count mismatch`);
    const heading = entry.locator('h1 a').first();
    const li = entry.locator('li.news-toggle').first();
    const anchor = li.locator('a').first();
    expect(await heading.count() === 1 && await li.count() === 1 && await anchor.count() === 1, 'target controls missing');
    result.before = await captureState(entry);
    const headingBox = await heading.boundingBox();
    const liBox = await li.boundingBox();
    const anchorBox = await anchor.boundingBox();
    result.interaction = {
      heading_box: headingBox,
      li_box: liBox,
      anchor_box: anchorBox,
      heading_center: headingBox ? { x: headingBox.x + headingBox.width / 2, y: headingBox.y + headingBox.height / 2 } : null,
      li_center: liBox ? { x: liBox.x + liBox.width / 2, y: liBox.y + liBox.height / 2 } : null,
      anchor_center: anchorBox ? { x: anchorBox.x + anchorBox.width / 2, y: anchorBox.y + anchorBox.height / 2 } : null,
      method: spec.action,
    };
    if (spec.target === 'heading') {
      expect(headingBox, 'heading has no bounding box');
      await heading.click({ position: { x: headingBox.width / 2, y: headingBox.height / 2 } });
      result.interaction.coordinate = result.interaction.heading_center;
    } else if (spec.target === 'li') {
      expect(liBox, 'li has no bounding box');
      await li.click({ position: { x: liBox.width / 2, y: liBox.height / 2 } });
      result.interaction.coordinate = result.interaction.li_center;
    } else if (spec.target === 'anchor') {
      expect(anchorBox, 'toggle anchor has no bounding box');
      await anchor.click({ position: { x: anchorBox.width / 2, y: anchorBox.height / 2 } });
      result.interaction.coordinate = result.interaction.anchor_center;
    } else if (spec.target === 'heading-enter') {
      await heading.focus();
      await heading.press('Enter');
      result.interaction.focus_center = result.interaction.heading_center;
      result.interaction.coordinate = null;
    } else {
      fail(`unknown case target ${spec.target}`);
    }
    result.executed = true;
    await page.waitForTimeout(settleMs);
    result.after = await captureState(entry);
    result.passed = true;
    result.observed_transition = {
      before_class: result.before.ancestor.class_name,
      after_class: result.after.ancestor.class_name,
      before_news_item_visible: result.before.news_item && result.before.news_item.visible,
      after_news_item_visible: result.after.news_item && result.after.news_item.visible,
      before_description_visible: result.before.description && result.before.description.visible,
      after_description_visible: result.after.description && result.after.description.visible,
      final_expanded: Boolean(result.after.news_item && result.after.news_item.visible),
    };
  } catch (error) {
    result.error = String(error);
    report.failures.push({ case_id: spec.id, error: result.error });
  } finally {
    await context.close();
  }
  report.cases.push(result);
}

async function main() {
  let browser;
  try {
    const baseUrl = new URL(baseUrlText);
    expect(baseUrl.protocol === 'http:' && baseUrl.hostname === '127.0.0.1', `non-loopback base URL ${baseUrlText}`);
    report.runner = { path: relative(__filename), bytes: fs.statSync(__filename).size, sha256: sha256Hex(fs.readFileSync(__filename)), node: process.execPath, cwd: repoRoot };
    const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
    browser = await chromium.launch({ headless: true });
    for (const spec of cases) await runCase(browser, spec, baseUrl);
    report.status = report.failures.length ? 'completed_with_failures' : 'passed';
  } catch (error) {
    report.status = 'runner_error';
    report.failures.push({ case_id: 'runner', error: String(error) });
  } finally {
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    const all404 = report.responses.filter(item => item.status === 404);
    report.summary = {
      cases: report.cases.length,
      executed_cases: report.cases.filter(item => item.executed).length,
      completed_cases: report.cases.filter(item => item.passed).length,
      failed_cases: report.cases.filter(item => item.passed === false).length,
      expanded_after_cases: report.cases.filter(item => item.observed_transition && item.observed_transition.final_expanded).length,
      collapsed_after_cases: report.cases.filter(item => item.observed_transition && !item.observed_transition.final_expanded).length,
      requests: report.requests.length,
      responses: report.responses.length,
      blocked_requests: report.route_decisions.filter(item => item.action === 'abort').length,
      request_failed: report.request_failed.length,
      page_errors: report.page_errors.length,
      console_errors: report.console_errors.length,
      response_404: all404.length,
    };
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ status: report.status, cases: report.summary.cases, executed: report.summary.executed_cases, completed: report.summary.completed_cases, expanded_after: report.summary.expanded_after_cases, collapsed_after: report.summary.collapsed_after_cases, failures: report.failures.length, blocked: report.summary.blocked_requests, response_404: report.summary.response_404, output }));
    if (report.status !== 'passed') process.exitCode = 1;
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
