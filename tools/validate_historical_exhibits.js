#!/usr/bin/env node
/*
 * Validate the derived historical-exhibit pages in fresh local Chrome
 * contexts.  The server is deliberately static: every request must resolve
 * to a file below --site, and every non-local request is aborted before it can
 * leave the browser.  This runner is evidence generation, not a deployment
 * server and does not bypass browser security.
 */
const fs = require('fs');
const http = require('http');
const path = require('path');
const assert = require('assert/strict');

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  return index < 0 ? fallback : process.argv[index + 1];
}

const site = path.resolve(option('--site', '.scratch/pages-resources-20261014-next'));
const output = path.resolve(option('--output', 'research/historical-exhibits-20261014/browser/validation.json'));
const prefix = option('--prefix', '/WOW-Encyclopedia-Deployable-Archive/');
const browserPath = option('--browser', undefined);
const playwrightModule = option('--playwright-module', 'playwright');
const { chromium } = require(playwrightModule);

const P0 = [
  'visa/reward/index.html',
  'visa/reward/login.html',
  'visa/reward/wow-login.html',
  'visa/reward.html',
];
const P1 = [
  'visa/index.html',
  'visa.html',
  'misc/deals.html',
  'misc/beta-signup.html',
  'misc/promotion.html',
  'community/stories/submit.html',
  'contests/l70etc-musicvideo/submit.html',
  'policy/index.html',
  'downloads/index.html',
  'downloads/other-downloads.html',
  'downloads/languagepack-en.xml.html',
  'downloads/languagepack-es.xml.html',
  'ui/index.html',
  'info/encyclopedia/index.xml.html',
];

const mime = {
  '.html': 'text/html; charset=utf-8',
  '.xml': 'application/xml; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.gif': 'image/gif',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
};

const report = {
  checkedAt: new Date().toISOString(),
  site,
  prefix,
  method: 'Fresh local Chrome contexts; exact static files only; non-local requests and non-GET requests aborted before network access.',
  p0: [],
  p1: [],
  aliases: [],
  crossPage: [],
  screenshots: [],
  deniedRequests: [],
  postAttempts: [],
  pageErrors: [],
  consoleErrors: [],
  expectedWarnings: { legacySwfBlockedByObjectSrc: [] },
  failures: [],
};

function textHas(text, patterns) {
  return patterns.some(pattern => pattern.test(text));
}

function dedupe(list) {
  return [...new Set(list)];
}

async function main() {
  fs.mkdirSync(path.dirname(output), { recursive: true });
  assert(fs.existsSync(site), `site directory does not exist: ${site}`);
  const server = http.createServer((request, response) => {
    try {
      const requestUrl = new URL(request.url, 'http://127.0.0.1');
      if (!requestUrl.pathname.startsWith(prefix)) throw new Error('outside prefix');
      let relative = decodeURIComponent(requestUrl.pathname.slice(prefix.length));
      if (!relative) relative = 'index.html';
      if (relative.endsWith('/')) relative += 'index.html';
      const file = path.resolve(site, relative);
      if (!(file === site || file.startsWith(site + path.sep))) throw new Error('outside site');
      if (!fs.statSync(file).isFile()) throw new Error('not a file');
      const body = fs.readFileSync(file);
      response.writeHead(200, {
        'Content-Type': mime[path.extname(file).toLowerCase()] || 'application/octet-stream',
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff',
      });
      response.end(body);
    } catch (_) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end('Not found');
    }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({
    headless: true,
    // Keep Chrome's Safe Browsing/phishing protection enabled. Playwright's
    // default launch flags include this one disable switch, so remove only
    // that switch from its generated argument list.
    ignoreDefaultArgs: ['--disable-client-side-phishing-detection'],
    ...(browserPath ? { executablePath: browserPath } : {}),
  });

  async function makeContext(javaScriptEnabled, viewport) {
    const mobile = viewport.width <= 500;
    const context = await browser.newContext({
      javaScriptEnabled,
      viewport,
      isMobile: mobile,
      hasTouch: mobile,
      deviceScaleFactor: 1,
      serviceWorkers: 'block',
    });
    await context.route('**/*', route => {
      const request = route.request();
      let requestUrl;
      try { requestUrl = new URL(request.url()); } catch (_) { requestUrl = null; }
      const local = requestUrl && requestUrl.origin === origin && requestUrl.pathname.startsWith(prefix);
      if (!local || !['GET', 'HEAD'].includes(request.method())) {
        const entry = { method: request.method(), url: request.url() };
        if (request.method() !== 'GET' && request.method() !== 'HEAD') report.postAttempts.push(entry);
        else report.deniedRequests.push(entry);
        return route.abort();
      }
      return route.continue();
    });
    return context;
  }

  async function inspect(page, route, options = {}) {
    const errors = [];
    page.on('pageerror', error => { errors.push(String(error)); report.pageErrors.push({ route, error: String(error) }); });
    page.on('console', message => {
      if (message.type() === 'error') {
        const entry = { route, text: message.text() };
        errors.push(`console: ${message.text()}`);
        report.consoleErrors.push(entry);
      }
    });
    const response = await page.goto(origin + prefix + route, { waitUntil: 'domcontentloaded', timeout: 30000 });
    assert(response, `no response for ${route}`);
    assert.equal(response.status(), 200, `${route} HTTP ${response.status()}`);
    if (options.waitMs) await page.waitForTimeout(options.waitMs);
    // A legacy alias is a real meta-refresh document.  Give the browser a
    // bounded settling window before evaluating the canonical exhibit, or a
    // navigation can destroy the evaluation context between DOM reads.
    if (options.expectedPath) {
      await page.waitForURL(url => {
        try { return new URL(url).pathname.endsWith(options.expectedPath); } catch (_) { return false; }
      }, { waitUntil: 'domcontentloaded', timeout: 5000 });
      await page.waitForTimeout(250);
      assert(new URL(page.url()).pathname.endsWith(options.expectedPath), `${route} did not settle on ${options.expectedPath}: ${page.url()}`);
    }
    const state = await page.evaluate(() => {
      const visible = element => {
        const style = getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) !== 0 && rect.width > 0 && rect.height > 0;
      };
      const firstScreen = [...document.querySelectorAll('body *')]
        .filter(visible)
        .filter(element => {
          const rect = element.getBoundingClientRect();
          return rect.top < innerHeight && rect.bottom > 0;
        })
        .map(element => element.innerText || element.alt || '')
        .join(' ')
        .replace(/\s+/g, ' ')
        .trim();
      const visibleControls = [...document.querySelectorAll('input,select,textarea,[contenteditable="true"]')]
        .filter(visible)
        .map(element => ({
          tag: element.tagName,
          type: element.type || null,
          name: element.name || element.id || '',
          form: element.form ? (element.form.name || element.form.id || '') : '',
          autocomplete: element.autocomplete || '',
        }));
      const localCandidates = [...document.querySelectorAll('a[href],link[href],img[src],script[src],iframe[src],form[action]')]
        .map(element => ({
          kind: element.tagName.toLowerCase(),
          url: element.href || element.src || element.action || '',
          text: (element.innerText || element.alt || '').replace(/\s+/g, ' ').trim().slice(0, 140),
        }));
      const accountLabels = ['Create Account', 'Manage Account', 'Retrieve Password'];
      const historicalAccountLinks = accountLabels.map(label => {
        const link = [...document.querySelectorAll('a')].find(element => (element.innerText || '').replace(/\s+/g, ' ').trim().toLowerCase().includes(label.toLowerCase()));
        if (!link) return { label, found: false, href: '', ancestorText: '', historicalContext: false };
        const contexts = [];
        let node = link.parentElement;
        for (let depth = 0; node && depth < 4; depth += 1, node = node.parentElement) {
          contexts.push((node.innerText || '').replace(/\s+/g, ' ').trim());
        }
        const ancestorText = contexts.join(' ').slice(0, 700);
        return {
          label,
          found: true,
          href: link.href || '',
          ancestorText,
          historicalContext: /(?:historical|archiv(?:e|ed)|2008|retired|inactive|no longer|not available|停用|历史|归档)/i.test(ancestorText),
        };
      });
      const controls = [...document.querySelectorAll('button,a')]
        .filter(visible)
        .map(element => ({ tag: element.tagName, text: (element.innerText || '').replace(/\s+/g, ' ').trim(), href: element.href || '' }))
        .filter(item => item.text);
      const banner = document.querySelector('#__offline-pages-banner, [data-offline-banner]');
      const clone = document.body.cloneNode(true);
      clone.querySelectorAll('#__offline-pages-banner, [data-offline-banner],script,style,noscript').forEach(element => element.remove());
      // Detached clones do not reliably implement innerText in Chromium.
      // textContent is stable after the non-content nodes are removed above.
      const exhibitText = (clone.textContent || '').replace(/\s+/g, ' ').trim();
      return {
        title: document.title,
        bodyText: (document.body.innerText || '').replace(/\s+/g, ' ').trim(),
        firstScreen,
        exhibitText,
        viewport: { width: innerWidth, height: innerHeight },
        screenWidth: screen.width,
        metaViewport: document.querySelector('meta[name="viewport"]')?.content || '',
        scrollWidth: Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0),
        localCandidates,
        historicalAccountLinks,
        visibleControls,
        controls,
        bannerPresent: Boolean(banner),
      };
    });
    state.pageErrors = errors;
    if (options.mobile) {
      assert.equal(state.viewport.width, 390, `${route} mobile layout viewport is not 390px`);
      assert.equal(state.screenWidth, 390, `${route} mobile screen width is not 390px`);
      assert(/(?:^|,)\s*width\s*=\s*device-width/i.test(state.metaViewport), `${route} lacks an effective device-width viewport meta`);
    }
    if (!options.allowFixedWidth) {
      assert(state.scrollWidth <= state.viewport.width + 2, `${route} horizontal overflow: ${state.scrollWidth}px > ${state.viewport.width}px`);
    }
    const external = state.localCandidates.filter(item => /^https?:\/\//i.test(item.url) && !item.url.startsWith(origin + prefix));
    assert.deepEqual(external, [], `${route} has non-local links/resources`);
    const editable = state.visibleControls.filter(item => {
      const context = `${item.name} ${item.form} ${item.autocomplete}`.toLowerCase();
      return !/search|query|language/.test(context);
    });
    assert.deepEqual(editable, [], `${route} has editable non-search controls`);
    return state;
  }

  function assertExhibitState(route, state, requireFirstScreen = true) {
    const identity = /(?:unofficial|independent archive|not affiliated|historical archive|historical exhibit|preservation)/i;
    const timeOrStatus = /(?:2008|historical|archived|archive|no longer|not available|inactive|discontinued|retired|ended|停用|历史|归档)/i;
    const caution = /(?:do not|don't|never|no (?:real|user|personal)|not (?:a|for) (?:login|service)|请勿|不要|不收集)/i;
    assert(identity.test(state.exhibitText), `${route} lacks independent archive/exhibit identity outside the generic banner`);
    assert(timeOrStatus.test(state.exhibitText), `${route} lacks historical or inactive status outside the generic banner`);
    assert(caution.test(state.exhibitText), `${route} lacks a no-data/no-service caution outside the generic banner`);
    if (requireFirstScreen) {
      assert(identity.test(state.firstScreen), `${route} first screen lacks archive identity`);
      assert(timeOrStatus.test(state.firstScreen), `${route} first screen lacks historical status`);
    }
    const operational = state.controls.filter(item => {
      const text = item.text.toLowerCase();
      if (!text) return false;
      if (/(?:view|read|see|open|display|exhibit|archive|历史|查看)/.test(text)) return false;
      return /^(?:log\s*in|login|apply(?: now)?|sign\s*up|submit|redeem|create account|retrieve password|download now|立即申请|登录|报名|提交|兑换)$/.test(text);
    });
    assert.deepEqual(operational, [], `${route} retains a current-operation CTA`);
  }

  async function record(group, name, run) {
    try {
      const result = await run();
      report[group].push({ name, passed: true, ...result });
    } catch (error) {
      const item = { name, passed: false, error: String(error) };
      report[group].push(item);
      report.failures.push(item);
    }
  }

  try {
    const modes = [
      { name: 'desktop-js', javaScriptEnabled: true, viewport: { width: 1440, height: 1000 } },
      { name: 'mobile-js', javaScriptEnabled: true, viewport: { width: 390, height: 844 } },
      { name: 'desktop-no-js', javaScriptEnabled: false, viewport: { width: 1440, height: 1000 } },
    ];
    for (const mode of modes) {
      const context = await makeContext(mode.javaScriptEnabled, mode.viewport);
      for (const route of P0) {
        await record('p0', `${mode.name}:${route}`, async () => {
          const page = await context.newPage();
          try {
            const alias = route === 'visa/reward.html';
            const state = await inspect(page, route, {
              waitMs: alias ? 250 : (mode.javaScriptEnabled ? 250 : 0),
              mobile: mode.name === 'mobile-js',
              expectedPath: alias ? '/visa/reward/index.html' : undefined,
            });
            assertExhibitState(route, state, mode.name !== 'desktop-js' || true);
            if (mode.name === 'desktop-js' && route === 'visa/reward/index.html' || mode.name === 'mobile-js' && route === 'visa/reward/wow-login.html' || mode.name === 'desktop-no-js' && route === 'visa/reward/login.html') {
              const screenshot = path.join(path.dirname(output), mode.name + '-' + route.replace(/[^a-z0-9]+/gi, '_') + '.png');
              await page.screenshot({ path: screenshot, fullPage: false });
              report.screenshots.push(screenshot);
            }
            return { route, mode: mode.name, title: state.title, firstScreen: state.firstScreen.slice(0, 700), dimensions: state.viewport, scrollWidth: state.scrollWidth };
          } finally { await page.close(); }
        });
      }
      await context.close();
    }

    const p1Context = await makeContext(true, { width: 1440, height: 1000 });
    for (const route of P1) {
      await record('p1', route, async () => {
        const page = await p1Context.newPage();
        try {
          const state = await inspect(page, route, { waitMs: 250, allowFixedWidth: true });
          if (route === 'info/encyclopedia/index.xml.html') {
            const globalArchiveIdentity = /(?:unofficial|independent archive|not affiliated|historical preservation|historical archive|归档)/i.test(state.bodyText);
            const historicalAccountNavigation = /(?:account|create account|manage account|retrieve password|login|账号|创建账号|管理账号|取回密码)/i.test(state.bodyText);
            assert(globalArchiveIdentity, `${route} lacks global archive identity`);
            assert(historicalAccountNavigation, `${route} lacks historical account navigation`);
            for (const link of state.historicalAccountLinks) {
              assert(link.found, `${route} is missing ${link.label}`);
              assert(/\/__offline\/missing\.html(?:\?|$)/i.test(link.href), `${route} ${link.label} does not remain a local missing-resource target: ${link.href}`);
              assert(link.historicalContext, `${route} ${link.label} lacks local historical context`);
            }
            return { route, title: state.title, globalArchiveIdentity, historicalAccountNavigation, historicalAccountLinks: state.historicalAccountLinks, controls: state.visibleControls.length };
          }
          const status = /(?:2008|historical|archived|archive|no longer|not available|inactive|discontinued|retired|ended|停用|历史|归档)/i.test(state.exhibitText);
          assert(status, `${route} lacks a historical/inactive business marker outside the generic banner`);
          return { route, title: state.title, historicalMarker: status, controls: state.visibleControls.length };
        } finally { await page.close(); }
      });
    }
    await p1Context.close();

    // visa/reward.html is a P0 alias and receives the same three-mode checks
    // as the canonical reward and login routes.  visa.html remains P1 above:
    // it points at the card marketing page and may retain its historical
    // fixed-width layout.
    const aliasContext = await makeContext(true, { width: 1440, height: 1000 });
    await record('aliases', 'visa/reward.html', async () => {
      const page = await aliasContext.newPage();
      try {
        const state = await inspect(page, 'visa/reward.html', { waitMs: 250, expectedPath: '/visa/reward/index.html' });
        assertExhibitState('visa/reward.html', state, true);
        return { route: 'visa/reward.html', title: state.title };
      } finally { await page.close(); }
    });
    await aliasContext.close();

    const linkContext = await makeContext(true, { width: 1440, height: 1000 });
    const page = await linkContext.newPage();
    await record('crossPage', 'P0 exhibit links and old aliases resolve locally', async () => {
      const state = await inspect(page, 'visa/reward/index.html', { waitMs: 250 });
      const targets = dedupe(state.localCandidates
        .filter(item => item.kind === 'a')
        .map(item => new URL(item.url).pathname)
        .filter(item => P0.some(route => item.endsWith('/' + route))));
      assert(targets.length >= 2, `P0 entry exposes ${targets.length} local exhibit targets`);
      const checks = [];
      for (const target of targets) {
        const route = target.slice(prefix.length);
        const response = await page.goto(origin + prefix + route, { waitUntil: 'domcontentloaded' });
        checks.push({ route, status: response && response.status() });
        assert(response && response.status() === 200, `${route} did not resolve locally`);
      }
      return { targets, checks };
    });
    await page.close();
    await linkContext.close();
  } catch (error) {
    report.failures.push({ name: 'runner', error: String(error) });
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
    const expectedSwf = report.consoleErrors.filter(entry => /loading plugin data from .*violates the following content security policy directive: ["']?object-src ["']?none/i.test(entry.text));
    const unexpectedConsoleErrors = report.consoleErrors.filter(entry => !expectedSwf.includes(entry));
    report.expectedWarnings.legacySwfBlockedByObjectSrc = expectedSwf;
    for (const entry of report.pageErrors) {
      report.failures.push({ name: `unexpected-page-error:${entry.route}`, error: `${entry.error}` });
    }
    for (const entry of unexpectedConsoleErrors) {
      report.failures.push({ name: `unexpected-console-error:${entry.route}`, error: entry.text });
    }
    report.deniedRequests = report.deniedRequests.slice(0, 100);
    report.passed = report.failures.length === 0 && report.deniedRequests.length === 0 && report.postAttempts.length === 0;
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({
      passed: report.passed,
      p0: report.p0.length,
      p1: report.p1.length,
      aliases: report.aliases.length,
      crossPage: report.crossPage.length,
      screenshots: report.screenshots.length,
      deniedRequests: report.deniedRequests.length,
      postAttempts: report.postAttempts.length,
      failures: report.failures.length,
      output,
    }));
    if (!report.passed) process.exitCode = 1;
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
