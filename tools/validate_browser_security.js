#!/usr/bin/env node
/* Validate the derived archive in fresh local browser contexts. */
const fs = require('fs');
const http = require('http');
const path = require('path');
const assert = require('assert/strict');

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  return index < 0 ? fallback : process.argv[index + 1];
}
const root = path.resolve(option('--site', '.scratch/pages-preview'));
const output = path.resolve(option('--output', '.scratch/browser-security-validation.json'));
const prefix = '/WOW-Encyclopedia-Deployable-Archive/';
const { chromium } = require(option('--playwright-module', 'playwright'));
const browserPath = option('--browser', undefined);
const types = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.gif': 'image/gif', '.png': 'image/png', '.jpg': 'image/jpeg', '.xml': 'application/xml' };
const report = { checkedAt: new Date().toISOString(), site: root, method: 'Unmodified derived files; fresh localhost Chrome contexts, external requests denied, POST intercepted before contacting a server; synthetic test markers only.', pagination: [], forms: [], browsing: [], failures: [], deniedOrigins: [], postAttempts: [] };

async function main() {
  fs.mkdirSync(path.dirname(output), { recursive: true });
  const server = http.createServer((request, response) => {
    try {
      const url = new URL(request.url, 'http://localhost');
      if (!url.pathname.startsWith(prefix)) throw Error('outside project');
      const file = path.resolve(root, decodeURIComponent(url.pathname.slice(prefix.length)) || 'index.html');
      if (!file.startsWith(root + path.sep)) throw Error('outside root');
      const bytes = fs.readFileSync(file);
      response.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
      response.end(bytes);
    } catch (_) { response.writeHead(404); response.end('Not found'); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = 'http://127.0.0.1:' + server.address().port;
  const browser = await chromium.launch({ headless: true, ...(browserPath ? { executablePath: browserPath } : {}) });
  async function context(javaScriptEnabled = true) {
    const context = await browser.newContext({ javaScriptEnabled, viewport: { width: 1440, height: 1000 } });
    await context.route('**/*', route => {
      const request = route.request();
      const url = new URL(request.url());
      if (request.method() === 'POST') {
        report.postAttempts.push({ path: url.pathname, bytes: (request.postData() || '').length });
        return route.fulfill({ status: 200, body: 'Unexpected synthetic POST intercepted.' });
      }
      if (url.origin !== origin || !url.pathname.startsWith(prefix)) {
        report.deniedOrigins.push(url.origin);
        return route.abort();
      }
      return route.continue();
    });
    return context;
  }
  async function record(group, name, run) {
    try { const result = await run(); report[group].push({ name, passed: true, ...result }); }
    catch (error) { report[group].push({ name, passed: false, error: String(error) }); report.failures.push({ name, error: String(error) }); }
  }
  try {
    const paginationContext = await context();
    const cases = [
      ['', 1], ['?s=1', 1], ['?s=2', 2], ['?s=5', 5], ['?s=%32', 2], ['?%73=2', 2],
      ['?s=0', 1], ['?s=-1', 1], ['?s=1.5', 1], ['?s=1e2', 1], ['?s=6', 1],
      ['?s=999999999999999999999999', 1], ['?s=2&s=3', 1], ['?xs=2', 1], ['?s=%2532', 1],
      ['?s=(window.__ARCHIVE_SECURITY_TEST__=1)', 1], ['?s=%28window.__ARCHIVE_SECURITY_TEST__%3D1%29', 1]
    ];
    for (const [query, expected] of cases) {
      await record('pagination', query || 'default', async () => {
        const page = await paginationContext.newPage();
        const errors = []; page.on('pageerror', error => errors.push(String(error)));
        try {
          await page.goto(origin + prefix + 'wrath/screenshots.xml.html' + query, { waitUntil: 'domcontentloaded' });
          const state = await page.evaluate(() => ({ page: window.currentPage, query: window.queryCurrentPage, total: window.queryTotalPages, marker: window.__ARCHIVE_SECURITY_TEST__ ?? null, thumbnails: document.querySelectorAll('.screenindex .ssborder').length, previous: [...document.querySelectorAll('.pagearrow.left a')].map(a => a.search), next: [...document.querySelectorAll('.pagearrow.right a')].map(a => a.search) }));
          assert.equal(state.page, expected); assert.equal(state.query, expected); assert.equal(state.total, 5);
          assert.equal(state.marker, null); assert.equal(state.thumbnails, expected === 5 ? 4 : 9);
          assert.equal(state.previous.length > 0, expected > 1); assert.equal(state.next.length > 0, expected < 5);
          assert.deepEqual(errors, []);
          return { state };
        } finally { await page.close(); }
      });
    }
    await paginationContext.close();

    const businessPages = ['visa/reward/login.html', 'visa/reward/wow-login.html', 'community/stories/submit.html', 'contests/l70etc-musicvideo/submit.html', 'misc/beta-signup.html', 'misc/promotion.html', 'policy/index.html', 'contests/05-12-giveaway/contest.html'];
    for (const javaScriptEnabled of [true, false]) {
      const ctx = await context(javaScriptEnabled);
      for (const file of businessPages) {
        await record('forms', file + ' JS=' + javaScriptEnabled, async () => {
          const page = await ctx.newPage();
          try {
            await page.goto(origin + prefix + file, { waitUntil: 'domcontentloaded' });
            if (javaScriptEnabled) await page.waitForTimeout(250);
            // Playwright DOM evaluation also works with page JavaScript disabled.
            const state = await page.evaluate(() => {
              const allowed = form => form && ['topsearch', 'formdropdownlang', 'searchform1', 'searchform2'].includes((form.name || form.id).toLowerCase().replace(/[^a-z0-9]/g, ''));
              const languageNavigation = el => el.tagName === 'SELECT' && el.name === 'language' && /queryStringAppend\(['"]language['"],this\.value\)/.test(el.getAttribute('onchange') || '');
              return {
                businessForms: [...document.forms].filter(form => !allowed(form)).map(form => form.name || form.id || '(unnamed)'),
                editable: [...document.querySelectorAll('input,select,textarea,button,[contenteditable="true"]')].filter(el => !allowed(el.form) && !languageNavigation(el)).map(el => ({ tag: el.tagName, name: el.name || el.id, type: el.type })),
                activeBusinessHandlers: [...document.querySelectorAll('*')].flatMap(el => [...el.attributes].filter(a => /^on/i.test(a.name) && /(?:\.submit\s*\(|undisable\s*\()/i.test(a.value)).map(a => a.value)),
                archiveNotices: document.querySelectorAll('[data-offline-form="static"]').length,
                historicalExhibits: document.querySelectorAll('.historical-exhibit').length
              };
            });
            assert.deepEqual(state.businessForms, []); assert.deepEqual(state.editable, []); assert.deepEqual(state.activeBusinessHandlers, []);
            if (file !== 'contests/05-12-giveaway/contest.html') assert.ok(state.archiveNotices > 0 || state.historicalExhibits > 0);
            return { state };
          } finally { await page.close(); }
        });
      }
      await ctx.close();
    }

    const ctx = await context();
    const page = await ctx.newPage();
    await record('browsing', 'encyclopedia menu and exact-title search', async () => {
      await page.goto(origin + prefix + 'info/encyclopedia/index.xml.html', { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(400);
      const before = await page.locator('#TopLevel').evaluate(el => getComputedStyle(el).display);
      await page.locator('#minimizerText').click();
      const after = await page.locator('#TopLevel').evaluate(el => getComputedStyle(el).display);
      assert.notEqual(before, after);
      await page.locator('#searchBox').fill('Elune');
      await page.locator('#searchType').selectOption('encyclopedia');
      await page.locator('.searchBoxButton a').click();
      await page.waitForURL(/\/info\/encyclopedia\/[0-9]+\.xml\.html/);
      assert.match(await page.title(), /Elune/i);
      return { target: new URL(page.url()).pathname, title: await page.title() };
    });
    for (const [file, selected] of [['pvp/rewards-class-armor.html', '2'], ['info/basics/factions/warsong/index.html', '0']]) {
      await record('browsing', 'reward filter ' + file, async () => {
        await page.goto(origin + prefix + file, { waitUntil: 'domcontentloaded' });
        const before = await page.locator('#alliance_rewards').innerText();
        await page.locator('select[name="bracketSelector"]').selectOption(selected);
        const state = await page.evaluate(() => ({ bracket: String(window.levelBracket), text: document.getElementById('alliance_rewards').innerText }));
        assert.equal(state.bracket, selected); assert.notEqual(state.text, before);
        return { selected, contentChanged: state.text !== before };
      });
    }
    await record('browsing', 'Argent Dawn local quest selector', async () => {
      await page.goto(origin + prefix + 'info/basics/factions/argent/index.html', { waitUntil: 'domcontentloaded' });
      await page.locator('select[onchange*="changeQuestForRealThisTime"]').selectOption('purpleQuest');
      const state = await page.evaluate(() => ({ blue: document.getElementById('blueQuest').style.display, purple: document.getElementById('purpleQuest').style.display }));
      assert.equal(state.blue, 'none'); assert.equal(state.purple, 'inline');
      return { state };
    });
    await record('browsing', 'iframe fallback keeps archived advertisements local', async () => {
      await page.goto(origin + prefix + 'gadgetzantimes/gt001/auntiefizzle.html', { waitUntil: 'domcontentloaded' });
      const fallback = await page.locator('iframe').first().evaluate(el => el.innerHTML);
      assert.doesNotMatch(fallback, /(?:href|src)=["']https?:\/\/(?:clk|view)\.atdmt\.com/i);
      assert.match(fallback, /WOW-Encyclopedia-Deployable-Archive\/__offline\//);
      return { localized: true };
    });
    await record('browsing', 'static business presentation screenshot', async () => {
      await page.goto(origin + prefix + 'visa/reward/login.html', { waitUntil: 'domcontentloaded' });
      const screenshot = path.join(path.dirname(output), 'static-visa-form.png');
      await page.screenshot({ path: screenshot, fullPage: true });
      return { screenshot };
    });
    await ctx.close();
    assert.deepEqual(report.postAttempts, []);
    report.deniedOrigins = [...new Set(report.deniedOrigins)];
  } catch (error) { report.failures.push({ name: 'runner', error: String(error) }); }
  finally {
    await browser.close(); await new Promise(resolve => server.close(resolve));
    report.passed = report.failures.length === 0;
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ passed: report.passed, pagination: report.pagination.length, forms: report.forms.length, browsing: report.browsing.length, failures: report.failures, output }));
    if (!report.passed) process.exitCode = 1;
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
