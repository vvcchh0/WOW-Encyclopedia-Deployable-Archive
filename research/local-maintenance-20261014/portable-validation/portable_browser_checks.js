#!/usr/bin/env node
/* Six bounded Playwright scenarios for the extracted portable browser bundle. */

const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  return index < 0 ? fallback : process.argv[index + 1];
}

const baseUrl = option('--base-url');
const site = path.resolve(option('--site', '.'));
const output = path.resolve(option('--output', 'portable-browser-validation.json'));
const mobileScreenshot = path.resolve(option('--mobile-screenshot', 'portable-mobile-login-history.png'));
const unknownScreenshot = path.resolve(option('--unknown-screenshot', 'portable-unknown404-query.png'));
const playwrightModule = option('--playwright-module', 'playwright');
const browserPath = option('--browser');
const { chromium } = require(playwrightModule);

if (!baseUrl) throw new Error('--base-url is required');
const base = new URL(baseUrl);
if (base.protocol !== 'http:' || base.hostname !== '127.0.0.1' || !base.pathname.endsWith('/')) {
  throw new Error(`base URL must be loopback with a trailing prefix: ${baseUrl}`);
}
const origin = base.origin;
const prefix = base.pathname;

const report = {
  schema: 'wow-encyclopedia-portable-browser-validation/v1',
  checkedAt: new Date().toISOString(),
  site,
  baseUrl,
  prefix,
  method: 'Fresh Chrome contexts; six local scenarios; external and non-GET requests aborted before network access.',
  launch: {
    headless: true,
    browser: browserPath,
    ignoreDefaultArgs: ['--disable-client-side-phishing-detection'],
    serviceWorkers: 'block'
  },
  scenarios: [],
  externalRequests: [],
  postAttempts: [],
  nonGetRequests: [],
  observed404: [],
  consoleErrors: [],
  pageErrors: [],
  requestFailures: [],
  expected: {
    knownMissing404: [],
    unknown404Console: [],
    swfObjectSrcNone: []
  },
  failures: [],
  passed: false
};

let expectedUnknown404ConsoleUrl = null;
const generic404ConsoleText = 'Failed to load resource: the server responded with a status of 404 (Not Found)';

const counters = { external: 0, post: 0, nonGet: 0, console: 0, page: 0, request: 0 };
function pushCapped(array, value, counterName, limit = 80) {
  counters[counterName] += 1;
  if (array.length < limit) array.push(value);
}

function urlFor(relative) {
  return baseUrl + relative;
}

function localUrl(url) {
  return url.origin === origin && url.pathname.startsWith(prefix);
}

function contextFor(javaScriptEnabled, viewport) {
  return browser.newContext({
    javaScriptEnabled,
    viewport,
    serviceWorkers: 'block'
  }).then(async context => {
    await context.route('**/*', async route => {
      const request = route.request();
      let url;
      try { url = new URL(request.url()); } catch (_) {
        pushCapped(report.externalRequests, { url: request.url(), method: request.method(), reason: 'invalid-url' }, 'external');
        await route.abort('blockedbyclient');
        return;
      }
      if (request.method() === 'POST') {
        pushCapped(report.postAttempts, { url: request.url(), path: url.pathname, bytes: (request.postData() || '').length }, 'post');
        await route.abort('blockedbyclient');
        return;
      }
      if (request.method() !== 'GET' && request.method() !== 'HEAD') {
        pushCapped(report.nonGetRequests, { url: request.url(), method: request.method(), path: url.pathname }, 'nonGet');
        await route.abort('blockedbyclient');
        return;
      }
      if (!localUrl(url)) {
        pushCapped(report.externalRequests, { url: request.url(), method: request.method(), path: url.pathname }, 'external');
        await route.abort('blockedbyclient');
        return;
      }
      await route.continue();
    });
    return context;
  });
}

function attachTelemetry(page, scenario) {
  page.on('response', response => {
    if (response.status() === 404) {
      const value = { scenario, path: new URL(response.url()).pathname, status: response.status() };
      report.observed404.push(value);
    }
  });
  page.on('console', message => {
    if (message.type() !== 'error') return;
    const text = message.text();
    const value = { scenario, text: text.slice(0, 600), location: message.location() };
    pushCapped(report.consoleErrors, value, 'console');
    if (/object-src\s+["']none["']/i.test(text) || /Loading plugin data/i.test(text)) {
      report.expected.swfObjectSrcNone.push(value);
    }
  });
  page.on('pageerror', error => {
    pushCapped(report.pageErrors, { scenario, text: String(error).slice(0, 600) }, 'page');
  });
  page.on('requestfailed', request => {
    const value = { scenario, url: request.url(), method: request.method(), failure: request.failure() };
    pushCapped(report.requestFailures, value, 'request');
  });
}

async function openPage(context, scenario, relative, waitUntil = 'domcontentloaded') {
  const page = await context.newPage();
  attachTelemetry(page, scenario);
  const response = await page.goto(urlFor(relative), { waitUntil, timeout: 30000 });
  await page.waitForTimeout(150);
  return { page, response };
}

async function scenario(name, run) {
  try {
    const result = await run();
    report.scenarios.push({ name, passed: true, ...result });
  } catch (error) {
    const text = String(error && error.stack ? error.stack : error);
    report.scenarios.push({ name, passed: false, error: text.slice(0, 1600) });
    report.failures.push({ name, error: text.slice(0, 1600) });
  }
}

async function checkOldXmlModes() {
  const query = '?portable=1&requested=%3Csafe%3E';
  const modes = [];
  for (const javaScriptEnabled of [true, false]) {
    const context = await contextFor(javaScriptEnabled, { width: 1440, height: 1000 });
    try {
      const opened = await openPage(context, `old-xml-js=${javaScriptEnabled}`, `info/encyclopedia/index.xml${query}`);
      assert.ok(opened.response, 'old XML page did not return a response');
      assert.equal(opened.response.status(), 200);
      const final = new URL(opened.page.url());
      assert.equal(final.pathname, `${prefix}info/encyclopedia/index.xml.html`);
      assert.equal(final.search, query);
      assert.match(await opened.page.title(), /Warcraft Encyclopedia/i);
      modes.push({ javaScriptEnabled, finalPath: final.pathname, query: final.search });
      await opened.page.close();
    } finally {
      await context.close();
    }
  }
  return { modes };
}

async function checkEncyclopedia() {
  const context = await contextFor(true, { width: 1440, height: 1000 });
  try {
    const opened = await openPage(context, 'encyclopedia-menu-elune-search', 'info/encyclopedia/index.xml.html');
    const before = await opened.page.locator('#TopLevel').evaluate(element => getComputedStyle(element).display);
    await opened.page.locator('#minimizerText').click();
    const after = await opened.page.locator('#TopLevel').evaluate(element => getComputedStyle(element).display);
    assert.notEqual(before, after);
    await opened.page.locator('#searchBox').fill('Elune');
    await opened.page.locator('#searchType').selectOption('encyclopedia');
    await opened.page.locator('.searchBoxButton a').first().click();
    await opened.page.waitForURL(/\/info\/encyclopedia\/[0-9]+\.xml\.html/, { timeout: 15000 });
    const title = await opened.page.title();
    assert.match(title, /Elune/i);
    const final = new URL(opened.page.url());
    await opened.page.close();
    return { menuChanged: true, searchTarget: final.pathname, title };
  } finally {
    await context.close();
  }
}

async function checkMobileLogin() {
  const context = await contextFor(false, { width: 390, height: 844 });
  try {
    const opened = await openPage(context, 'mobile-login-history-js-off', 'visa/reward/wow-login.html');
    assert.ok(opened.response, 'mobile login page did not return a response');
    assert.equal(opened.response.status(), 200);
    assert.match(await opened.page.title(), /Historical Exhibit/i);
    const state = await opened.page.evaluate(() => ({
      forms: document.forms.length,
      editable: document.querySelectorAll('input,select,textarea,button,[contenteditable="true"]').length,
      historical: /historical exhibit/i.test(document.body.innerText)
    }));
    assert.equal(state.forms, 0);
    assert.equal(state.editable, 0);
    assert.equal(state.historical, true);
    await opened.page.screenshot({ path: mobileScreenshot, fullPage: true });
    await opened.page.close();
    return { viewport: { width: 390, height: 844 }, state, screenshot: mobileScreenshot };
  } finally {
    await context.close();
  }
}

async function checkUnknown404() {
  const context = await contextFor(true, { width: 1440, height: 1000 });
  try {
    const query = '?source=portable&requested=%3Cscript%3Ewindow.__PORTABLE_QUERY_EXECUTED__%3D1%3C%2Fscript%3E';
    expectedUnknown404ConsoleUrl = urlFor(`__portable-browser-unknown__.html${query}`);
    const opened = await openPage(context, 'unknown404-query', `__portable-browser-unknown__.html${query}`);
    assert.ok(opened.response, 'unknown route did not return a response');
    assert.equal(opened.response.status(), 404);
    const state = await opened.page.evaluate(() => ({
      title: document.title,
      detailsText: document.querySelector('#details')?.innerText || '',
      detailsHtml: document.querySelector('#details')?.innerHTML || '',
      marker: window.__PORTABLE_QUERY_EXECUTED__ || null
    }));
    assert.match(state.detailsText, /<script>window\.__PORTABLE_QUERY_EXECUTED__=1<\/script>/);
    assert.doesNotMatch(state.detailsHtml, /<script>window\.__PORTABLE_QUERY_EXECUTED__=1<\/script>/);
    assert.equal(state.marker, null);
    await opened.page.screenshot({ path: unknownScreenshot, fullPage: true });
    await opened.page.close();
    return { status: 404, queryTextEscaped: true, screenshot: unknownScreenshot };
  } finally {
    await context.close();
  }
}

async function checkFlashPage(name, relative, expectedDataCount) {
  const context = await contextFor(true, { width: 1440, height: 1000 });
  try {
    const opened = await openPage(context, name, relative);
    assert.ok(opened.response, `${relative} did not return a response`);
    assert.equal(opened.response.status(), 200);
    const state = await opened.page.evaluate(() => {
      const objects = [...document.querySelectorAll('object')];
      const archive = objects.map(object => object.getAttribute('data-archive-codebase')).filter(Boolean);
      const externalInstall = objects
        .map(object => object.getAttribute('codebase'))
        .filter(value => value && /^https?:\/\/[^/]+\/pub\/shockwave\/cabs\/flash\//i.test(value));
      const csp = [...document.querySelectorAll('meta')]
        .find(meta => (meta.getAttribute('http-equiv') || '').toLowerCase() === 'content-security-policy')
        ?.getAttribute('content') || '';
      return {
        objectCount: objects.length,
        dataArchiveCodebaseCount: archive.length,
        dataArchiveCodebase: archive,
        externalInstallCodebaseCount: externalInstall.length,
        remainingLocalCodebase: objects.map(object => object.getAttribute('codebase')).filter(Boolean),
        cspObjectSrcNone: /object-src\s+["']none["']/i.test(csp)
      };
    });
    assert.equal(state.dataArchiveCodebaseCount, expectedDataCount);
    assert.equal(state.externalInstallCodebaseCount, 0);
    assert.equal(state.cspObjectSrcNone, true);
    report.expected.swfObjectSrcNone.push({ scenario: name, route: relative, cspObjectSrcNone: true });
    await opened.page.close();
    return { route: relative, state };
  } finally {
    await context.close();
  }
}

let browser;
(async () => {
  try {
    browser = await chromium.launch({
      headless: true,
      ...(browserPath ? { executablePath: browserPath } : {}),
      ignoreDefaultArgs: ['--disable-client-side-phishing-detection']
    });

    await scenario('old-xml-js-on-off', checkOldXmlModes);
    await scenario('encyclopedia-menu-elune-search', checkEncyclopedia);
    await scenario('mobile-login-history-js-off', checkMobileLogin);
    await scenario('unknown404-query-safety', checkUnknown404);
    await scenario('socketeditems-flash', () => checkFlashPage('socketeditems-flash', 'info/items/socketeditems.html', 5));
    await scenario('dancing-flash', () => checkFlashPage('dancing-flash', 'info/races/dancing.html', 1));

    report.expected.knownMissing404 = report.observed404.filter(item => item.scenario === 'unknown404-query');
    report.expected.unknown404Console = report.consoleErrors.filter(item => (
      item.scenario === 'unknown404-query' &&
      item.location?.url === expectedUnknown404ConsoleUrl &&
      item.text === generic404ConsoleText
    ));
    const unexpected404 = report.observed404.filter(item => item.scenario !== 'unknown404-query');
    if (unexpected404.length) report.failures.push({ name: 'unexpected-local-404', details: unexpected404.slice(0, 20) });
    if (report.externalRequests.length || counters.external) report.failures.push({ name: 'external-requests-blocked', count: counters.external, requests: report.externalRequests });
    if (report.postAttempts.length || counters.post) report.failures.push({ name: 'POST-attempts-blocked', count: counters.post, requests: report.postAttempts });
    if (report.nonGetRequests.length || counters.nonGet) report.failures.push({ name: 'non-GET-requests-blocked', count: counters.nonGet, requests: report.nonGetRequests });
    if (counters.page) report.failures.push({ name: 'page-errors', count: counters.page, errors: report.pageErrors });
    const expectedConsole = report.consoleErrors.filter(item => (
      /object-src\s+["']none["']/i.test(item.text) ||
      /Loading plugin data/i.test(item.text) ||
      report.expected.unknown404Console.includes(item)
    ));
    const unexpectedConsole = report.consoleErrors.filter(item => !expectedConsole.includes(item));
    if (unexpectedConsole.length) report.failures.push({ name: 'unexpected-console-errors', errors: unexpectedConsole });
    if (!report.expected.knownMissing404.length) report.failures.push({ name: 'missing-404-evidence', error: 'unknown route did not yield the expected local 404 response' });
  } catch (error) {
    report.failures.push({ name: 'runner', error: String(error && error.stack ? error.stack : error).slice(0, 2000) });
  } finally {
    if (browser) await browser.close();
    report.counts = {
      scenarios: report.scenarios.length,
      passedScenarios: report.scenarios.filter(item => item.passed).length,
      externalRequests: counters.external,
      postAttempts: counters.post,
      nonGetRequests: counters.nonGet,
      consoleErrors: counters.console,
      pageErrors: counters.page,
      requestFailures: counters.request,
      expected404: report.expected.knownMissing404.length,
      expectedSwfCspEvents: report.expected.swfObjectSrcNone.length
    };
    report.passed = report.failures.length === 0;
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n', 'utf8');
    console.log(JSON.stringify({ passed: report.passed, scenarios: report.scenarios.length, failures: report.failures, output }));
    if (!report.passed) process.exitCode = 1;
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
