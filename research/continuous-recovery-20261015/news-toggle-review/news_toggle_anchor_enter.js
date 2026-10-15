'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const repoRoot = path.resolve(__dirname, '..', '..', '..');
const baseUrl = new URL('http://127.0.0.1:29008');
const prefix = '/WOW-Encyclopedia-Deployable-Archive/';
const route = '/news/rss-07-2007.xml.html';
const entryId = 'news7-30-07-513';
const output = path.resolve(repoRoot, 'research/continuous-recovery-20261015/news-toggle-review/news-toggle-anchor-enter-receipt.json');

function sha256Hex(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function expect(condition, message) { if (!condition) throw new Error(message); }
function relative(file) { return path.relative(repoRoot, file).replace(/\\/g, '/'); }
function classify(value, method) {
  let url;
  try { url = new URL(value); } catch (_) { return 'invalid-url'; }
  if (url.origin !== baseUrl.origin || !url.pathname.startsWith(prefix)) return 'outside-loopback-prefix';
  return ['GET', 'HEAD'].includes(String(method).toUpperCase()) ? 'local-allowed' : 'local-non-get';
}
function targetUrl() {
  const url = new URL(baseUrl.href);
  url.pathname = prefix + route.replace(/^\/+/, '');
  return url.toString();
}

async function state(entry) {
  return entry.evaluate(root => {
    const shape = node => {
      if (!node) return null;
      const rect = node.getBoundingClientRect();
      const style = getComputedStyle(node);
      return {
        display: style.display,
        visibility: style.visibility,
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        visible: Boolean(node.getClientRects().length && rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden'),
      };
    };
    const anchor = root.querySelector('li.news-toggle a');
    const li = root.querySelector('li.news-toggle');
    const item = root.querySelector('.news-item');
    const description = root.querySelector('description');
    return {
      ancestor: { id: root.id || '', class_name: root.className || '' },
      toggle_anchor: anchor ? { href: anchor.getAttribute('href') || '', bbox: shape(anchor) } : null,
      toggle_li: li ? shape(li) : null,
      news_item: shape(item),
      description: shape(description),
    };
  });
}

async function activeInfo(page) {
  return page.evaluate(() => {
    const active = document.activeElement;
    const ancestor = active && active.closest('[id^="news"]');
    return {
      tag: active ? active.tagName : '',
      href: active && active.getAttribute ? active.getAttribute('href') || '' : '',
      ancestor_id: ancestor ? ancestor.id || '' : '',
      ancestor_class: ancestor ? ancestor.className || '' : '',
    };
  });
}

async function main() {
  const report = {
    schema: 'wow-recovery.news-toggle-anchor-enter.v1',
    status: 'prepared',
    started_utc: new Date().toISOString(),
    finished_utc: null,
    base_url: baseUrl.href,
    prefix,
    route,
    entry_id: entryId,
    policy: 'One fresh context; loopback deployment prefix only; GET/HEAD only; no direct function calls, style/handler edits, or force clicks.',
    runner: { path: relative(__filename), bytes: fs.statSync(__filename).size, sha256: sha256Hex(fs.readFileSync(__filename)), node: process.execPath, cwd: repoRoot },
    executed: false,
    passed: false,
    before: null,
    after: null,
    active_before_enter: null,
    active_after_enter: null,
    toggle_anchor_bbox: null,
    toggle_li_bbox: null,
    requests: [],
    responses: [],
    route_decisions: [],
    request_failed: [],
    page_errors: [],
    console_errors: [],
    failures: [],
  };
  let browser;
  try {
    const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, serviceWorkers: 'block' });
    await context.route('**/*', async intercepted => {
      const req = intercepted.request();
      const classification = classify(req.url(), req.method());
      const allowed = classification === 'local-allowed';
      report.route_decisions.push({ method: req.method(), url: req.url(), resource_type: req.resourceType(), class: classification, action: allowed ? 'continue' : 'abort' });
      if (allowed) return intercepted.continue();
      return intercepted.abort();
    });
    const page = await context.newPage();
    page.on('request', req => report.requests.push({ method: req.method(), url: req.url(), resource_type: req.resourceType(), class: classify(req.url(), req.method()) }));
    page.on('response', response => report.responses.push({ method: response.request().method(), url: response.url(), status: response.status(), resource_type: response.request().resourceType() }));
    page.on('requestfailed', req => report.request_failed.push({ method: req.method(), url: req.url(), failure: req.failure() }));
    page.on('pageerror', error => report.page_errors.push(String(error)));
    page.on('console', message => { if (['error', 'warning'].includes(message.type())) report.console_errors.push({ type: message.type(), text: message.text() }); });
    const response = await page.goto(targetUrl(), { waitUntil: 'domcontentloaded', timeout: 30000 });
    expect(response && response.status() === 200, `navigation HTTP ${response && response.status()}`);
    await page.waitForTimeout(300);
    const entry = page.locator(`#${entryId}`);
    const anchor = entry.locator('li.news-toggle a').first();
    const li = entry.locator('li.news-toggle').first();
    expect(await entry.count() === 1 && await anchor.count() === 1 && await li.count() === 1, 'narrow toggle anchor target missing');
    report.before = await state(entry);
    report.toggle_anchor_bbox = await anchor.boundingBox();
    report.toggle_li_bbox = await li.boundingBox();
    await anchor.focus();
    report.active_before_enter = await activeInfo(page);
    expect(report.active_before_enter.tag === 'A' && report.active_before_enter.ancestor_id === entryId, `focus did not land on narrow toggle anchor: ${JSON.stringify(report.active_before_enter)}`);
    await anchor.press('Enter');
    report.executed = true;
    await page.waitForTimeout(300);
    report.active_after_enter = await activeInfo(page);
    report.after = await state(entry);
    report.passed = true;
    report.status = 'passed';
    await context.close();
  } catch (error) {
    report.status = 'completed_with_failure';
    report.failures.push(String(error));
  } finally {
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    report.summary = {
      executed: report.executed ? 1 : 0,
      passed: report.passed ? 1 : 0,
      failures: report.failures.length,
      blocked_requests: report.route_decisions.filter(item => item.action === 'abort').length,
      request_failed: report.request_failed.length,
      page_errors: report.page_errors.length,
      console_errors: report.console_errors.length,
      responses_404: report.responses.filter(item => item.status === 404).length,
      after_news_item_visible: Boolean(report.after && report.after.news_item && report.after.news_item.visible),
    };
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ status: report.status, executed: report.summary.executed, passed: report.summary.passed, after_visible: report.summary.after_news_item_visible, failures: report.summary.failures, blocked: report.summary.blocked_requests, response_404: report.summary.responses_404, output }));
    if (!report.passed) process.exitCode = 1;
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
