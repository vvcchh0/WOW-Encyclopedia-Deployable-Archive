#!/usr/bin/env node
/*
 * Bounded loopback-only browser acceptance for the resource-repair-20261015
 * derived archive.  The runner deliberately requires an explicit 127.0.0.1
 * base URL and blocks every non-local request before it reaches the network.
 */

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function option(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index >= 0) return process.argv[index + 1];
  const inline = process.argv.find(value => value.startsWith(`${name}=`));
  return inline === undefined ? fallback : inline.slice(name.length + 1);
}

const baseUrl = option('--base-url');
if (!baseUrl) throw new Error('--base-url=http://127.0.0.1:port/WOW-Encyclopedia-Deployable-Archive/ is required');

const base = new URL(baseUrl);
if (base.protocol !== 'http:' || base.hostname !== '127.0.0.1' || !base.pathname.endsWith('/')) {
  throw new Error(`--base-url must be an http 127.0.0.1 URL with a trailing prefix: ${baseUrl}`);
}
if (base.search || base.hash) throw new Error('--base-url must not contain a query or fragment');

const output = path.resolve(option('--output', 'research/resource-repair-20261015/browser/browser-check.json'));
const firstScreenshot = path.resolve(option('--first-screenshot', 'research/resource-repair-20261015/browser/ssotd-first-screen.png'));
const lightboxScreenshot = path.resolve(option('--lightbox-screenshot', 'research/resource-repair-20261015/browser/ssotd-1314-lightbox.png'));
const freeTrialsScreenshot = path.resolve(option('--free-trials-screenshot', 'research/resource-repair-20261015/browser/free-trials.png'));
const wallpaperScreenshot = path.resolve(option('--wallpaper-screenshot', 'research/resource-repair-20261015/browser/wrath-wallpapers.png'));
const pvpScreenshot = path.resolve(option('--pvp-screenshot', 'research/resource-repair-20261015/browser/pvp-flash-rewards.png'));
const wallpaperAuditPath = path.resolve(option('--wallpaper-audit', 'research/resource-repair-20261015/wrath-wallpaper-audit.json'));
const playwrightModule = option('--playwright-module', 'playwright');
const browserPath = option('--browser');
const { chromium } = require(playwrightModule);

const origin = base.origin;
const prefix = base.pathname;
const siteRoot = path.resolve(option('--site-root', '.'));
const EXPECTED_SCENARIO_COUNT = 7;
const onlyScenario = option('--only');
const expectedRunCount = onlyScenario ? 1 : EXPECTED_SCENARIO_COUNT;

function readJsonIfPresent(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (_) {
    return null;
  }
}

function sourceMapEvidence(relativePath, predicate) {
  const sourceMap = readJsonIfPresent(path.resolve(siteRoot, relativePath));
  const entry = sourceMap && Array.isArray(sourceMap.files) ? sourceMap.files.find(predicate) : null;
  if (!entry) return null;
  return {
    logical_url: entry.logical_url || null,
    original: entry.original || null,
    local_path: entry.local_path || null,
    mime: entry.mime || entry.response_content_type || null,
    sha256: entry.sha256 || null,
    content_length: entry.content_length || null,
    actual_timestamp: entry.actual_timestamp || entry.entity_observed_capture_timestamp || null,
    indexed_capture_timestamp: entry.indexed_capture_timestamp || null,
    http_status: entry.http_status || null,
    content_class: entry.content_class || null,
    title: entry.title || null,
    temporal_class: entry.temporal_class || null,
    role: entry.role || null,
    source_map_path: entry.source_map_path || null,
    source_url: entry.source_url || null,
    requested_url: entry.requested_url || null,
    cdx_digest: entry.cdx_digest || null,
    cdx_length: entry.cdx_length || null,
    supplement_note: entry.supplement_note || null
  };
}

const wallpaperAudit = readJsonIfPresent(wallpaperAuditPath);
const trialSourceEvidence = sourceMapEvidence(
  'research/navigation-gaps-20261015/wayback-missing/source-map.json',
  item => /\/burningcrusade\/trial\/index\.html/i.test(item.logical_url || '')
);
const wallpaperSourceEvidence = sourceMapEvidence(
  'offline/approved-pages-recovery-map.json',
  item => /\/wrath\/\/wallpapers\.xml$/i.test(item.logical_url || '')
);
const wallpaperComparisonEvidence = sourceMapEvidence(
  'research/navigation-gaps-20261015/wayback-missing/source-map.json',
  item => /\/wrath\/wallpapers\.xml$/i.test(item.logical_url || '')
);
const pvpSourceEvidence = sourceMapEvidence(
  'research/resource-repair-20261015/pvp-pre2008-control/replay/files-map.json',
  item => /\/pvp\/flash-rewards\/?$/i.test(item.logical_url || '')
);
const expectedImages = {
  '/downloads/ssotd/images/screens/ss1314.jpg': {
    sha256: 'cef0bd37c5b34844f7d0d415a3ede71b7e674e467b3c95909e2dec0662c93fe8',
    width: 1024,
    height: 640
  },
  '/downloads/ssotd/images/screens/ss1336.jpg': {
    sha256: '58fcb8db67bc56bf21566fbc05de0d1372a71f4ac4ef65e4eb247ab95abeb289',
    width: 1200,
    height: 750
  }
};

const report = {
  schema: 'wow-encyclopedia-resource-repair-browser-check/v2',
  checkedAt: new Date().toISOString(),
  baseUrl,
  prefix,
  expectedScenarioCount: expectedRunCount,
  onlyScenario: onlyScenario || null,
  policy: {
    browser: 'headless Chromium',
    allowed: ['same-origin loopback HTTP', 'data:', 'blob:', 'about:blank'],
    blockedBeforeNetwork: ['non-loopback requests', 'non-GET/HEAD requests'],
    serviceWorkers: 'block',
    externalNetwork: 'forbidden'
  },
  scenarios: [],
  imageResponses: [],
  imageBodies: [],
  externalRequests: [],
  nonGetRequests: [],
  requestFailures: [],
  consoleErrors: [],
  pageErrors: [],
  observed404: [],
  failures: [],
  passed: false
};

const bodyPromises = [];
let browser;

function urlFor(relative) {
  const clean = String(relative).replace(/^\/+/, '');
  return new URL(clean, base).href;
}

function relativePath(urlText) {
  let url;
  try { url = new URL(urlText); } catch (_) { return urlText; }
  if (url.origin === origin && url.pathname.startsWith(prefix)) {
    return '/' + url.pathname.slice(prefix.length);
  }
  return url.pathname;
}

function isAllowedUrl(urlText) {
  let url;
  try { url = new URL(urlText); } catch (_) { return false; }
  if (url.protocol === 'data:' || url.protocol === 'about:') return true;
  if (url.protocol === 'blob:') return url.origin === origin;
  // The portable pages retain root-absolute legacy asset URLs.  They are
  // still same-origin loopback requests and must be allowed by this guard.
  return url.origin === origin;
}

function capPush(array, value, limit = 120) {
  if (array.length < limit) array.push(value);
}

function attachTelemetry(page, scenario, bodyTargets = new Set()) {
  const pageRequests = [];
  const pageBodyPromises = [];
  page.__resourceRepairRequests = pageRequests;
  page.__resourceRepairBodyPromises = pageBodyPromises;

  page.on('request', request => {
    const item = { method: request.method(), url: request.url(), path: relativePath(request.url()) };
    pageRequests.push(item);
    if (request.method() !== 'GET' && request.method() !== 'HEAD') {
      capPush(report.nonGetRequests, { scenario, ...item });
    }
  });

  page.on('response', response => {
    const itemPath = relativePath(response.url());
    if (response.status() === 404) capPush(report.observed404, { scenario, path: itemPath, url: response.url() });
    if (bodyTargets.has(itemPath)) {
      const contentType = response.headers()['content-type'] || '';
      capPush(report.imageResponses, {
        scenario,
        path: itemPath,
        status: response.status(),
        contentType,
        url: response.url()
      });
      if (response.status() === 200) {
        const promise = response.body().then(buffer => {
          const expected = expectedImages[itemPath];
          report.imageBodies.push({
            scenario,
            path: itemPath,
            status: response.status(),
            contentType,
            length: buffer.length,
            sha256: crypto.createHash('sha256').update(buffer).digest('hex'),
            expectedSha256: expected ? expected.sha256 : null,
            digestMatch: expected ? crypto.createHash('sha256').update(buffer).digest('hex') === expected.sha256 : null
          });
        }).catch(error => {
          report.failures.push({ name: 'image-body-read', scenario, path: itemPath, error: String(error) });
        });
        bodyPromises.push(promise);
        pageBodyPromises.push(promise);
      }
    }
  });

  page.on('requestfailed', request => {
    capPush(report.requestFailures, {
      scenario,
      url: request.url(),
      method: request.method(),
      failure: request.failure()
    });
  });
  page.on('console', message => {
    if (message.type() === 'error') capPush(report.consoleErrors, {
      scenario,
      text: message.text().slice(0, 800),
      location: message.location()
    });
  });
  page.on('pageerror', error => capPush(report.pageErrors, { scenario, text: String(error).slice(0, 1200) }));
  return pageRequests;
}

async function newContext() {
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
    serviceWorkers: 'block'
  });
  await context.route('**/*', async route => {
    const request = route.request();
    const requestUrl = request.url();
    if (request.method() !== 'GET' && request.method() !== 'HEAD') {
      capPush(report.nonGetRequests, {
        scenario: 'route-guard',
        method: request.method(),
        url: requestUrl,
        path: relativePath(requestUrl)
      });
      await route.abort('blockedbyclient');
      return;
    }
    if (!isAllowedUrl(requestUrl)) {
      capPush(report.externalRequests, {
        scenario: 'route-guard',
        method: request.method(),
        url: requestUrl,
        path: relativePath(requestUrl)
      });
      await route.abort('blockedbyclient');
      return;
    }
    await route.continue();
  });
  return context;
}

async function goto(page, relative, waitUntil = 'domcontentloaded') {
  const response = await page.goto(urlFor(relative), { waitUntil, timeout: 30000 });
  assert.ok(response, `no response for ${relative}`);
  return response;
}

async function waitFor(page, predicate, arg, description, timeout = 30000) {
  await page.waitForFunction(predicate, arg, { timeout });
  return description;
}

async function bodyText(page) {
  return page.locator('body').textContent().catch(() => '') || '';
}

async function runScenario(name, fn) {
  try {
    const result = await fn();
    report.scenarios.push({ name, passed: true, ...result });
  } catch (error) {
    const text = String(error && error.stack ? error.stack : error).slice(0, 2400);
    report.scenarios.push({ name, passed: false, error: text });
    report.failures.push({ name, error: text });
  }
}

async function checkSsotdFirstPage() {
  const context = await newContext();
  const page = await context.newPage();
  const requests = attachTelemetry(page, 'ssotd-first-page', new Set(Object.keys(expectedImages)));
  try {
    const response = await goto(page, 'downloads/ssotd/index.html');
    assert.equal(response.status(), 200);
    await waitFor(page, () => (
      Number(window.currentShotNumber) === 1340 &&
      Array.isArray(window.shotList) &&
      window.shotList.length === 1340 &&
      document.querySelector('#pageNum')?.textContent.trim() === '1 of 112'
    ), undefined, 'SSOTD default state');
    await waitFor(page, () => {
      const image = [...document.images].find(item => /ss1336(?:-thumb)?\.jpg$/i.test(new URL(item.currentSrc || item.src, location.href).pathname));
      return Boolean(image && image.complete && image.naturalWidth === 1200 && image.naturalHeight === 750);
    }, undefined, 'ss1336 first-page image', 30000);

    const state = await page.evaluate(() => {
      const image = [...document.images].find(item => /ss1336(?:-thumb)?\.jpg$/i.test(new URL(item.currentSrc || item.src, location.href).pathname));
      return {
        currentShotNumber: window.currentShotNumber,
        shotListLength: window.shotList?.length || 0,
        shotsPerPage: window.shotsPerPage,
        currentPage: window.currentPage,
        numPages: window.numPages,
        pageLabel: document.querySelector('#pageNum')?.textContent.trim() || '',
        galleryClass: document.querySelector('#galleryPictures')?.className || '',
        ss1336: image ? {
          src: image.currentSrc || image.src,
          naturalWidth: image.naturalWidth,
          naturalHeight: image.naturalHeight,
          complete: image.complete
        } : null,
        firstPageImageCount: document.querySelectorAll('#galleryPictures img').length,
        galleryImages: [...document.querySelectorAll('#galleryPictures img')].map(image => ({
          src: image.currentSrc || image.src,
          complete: image.complete,
          naturalWidth: image.naturalWidth,
          naturalHeight: image.naturalHeight
        }))
      };
    });
    assert.equal(state.currentShotNumber, 1340);
    assert.equal(state.shotListLength, 1340);
    assert.equal(state.shotsPerPage, 12);
    assert.equal(state.currentPage, 0);
    assert.equal(state.numPages, 112);
    assert.equal(state.pageLabel, '1 of 112');
    assert.equal(state.firstPageImageCount, 12);
    assert.ok(state.ss1336, 'ss1336 is absent from the default first page');
    assert.equal(state.ss1336.naturalWidth, 1200);
    assert.equal(state.ss1336.naturalHeight, 750);
    assert.match(state.ss1336.src, /ss1336\.jpg$/i, 'ss1336 did not fall back to the full image URL');

    const anachronosHeadRequests = requests.filter(item => item.method === 'HEAD' && /\/downloads\/ssotd\/anachronos\.xml$/i.test(item.path));
    assert.equal(anachronosHeadRequests.length, 0, 'SSOTD issued an anachronos.xml HEAD request');

    await page.screenshot({ path: firstScreenshot, fullPage: true });

    await page.locator('a[href*="galleryNext"]').first().click();
    await waitFor(page, () => window.currentPage === 1 && document.querySelector('#pageNum')?.textContent.trim() === '2 of 112', undefined, 'SSOTD Next');
    const afterNext = await page.evaluate(() => ({ currentPage: window.currentPage, pageLabel: document.querySelector('#pageNum')?.textContent.trim() || '' }));
    await page.locator('a[href*="galleryPrev"]').first().click();
    await waitFor(page, () => window.currentPage === 0 && document.querySelector('#pageNum')?.textContent.trim() === '1 of 112', undefined, 'SSOTD Previous');
    const afterPrevious = await page.evaluate(() => ({ currentPage: window.currentPage, pageLabel: document.querySelector('#pageNum')?.textContent.trim() || '' }));

    const layouts = [];
    for (const [size, count] of [['nine', 9], ['twelve', 12], ['sixteen', 16]]) {
      await page.evaluate(value => window.ThumbSize(value), size);
      await waitFor(page, value => (
        document.querySelector('#galleryPictures')?.classList.contains(value) &&
        window.shotsPerPage === ({ nine: 9, twelve: 12, sixteen: 16 })[value]
      ), size, `SSOTD ${size} layout`);
      layouts.push(await page.evaluate(() => ({
        className: document.querySelector('#galleryPictures')?.className || '',
        shotsPerPage: window.shotsPerPage,
        imageCount: document.querySelectorAll('#galleryPictures img').length,
        pageLabel: document.querySelector('#pageNum')?.textContent.trim() || ''
      })));
      assert.equal(layouts.at(-1).shotsPerPage, count);
    }

    return {
      status: response.status(),
      state,
      anachronosHeadRequests,
      next: afterNext,
      previous: afterPrevious,
      layouts,
      screenshot: firstScreenshot,
      requestCount: requests.length
    };
  } finally {
    await Promise.allSettled(page.__resourceRepairBodyPromises || []);
    await page.close().catch(() => {});
    await context.close();
  }
}

async function checkSsotdHashLightbox() {
  const context = await newContext();
  const page = await context.newPage();
  const requests = attachTelemetry(page, 'ssotd-hash-1314-lightbox', new Set(['/downloads/ssotd/images/screens/ss1314.jpg']));
  try {
    const response = await goto(page, 'downloads/ssotd/index.html#1314');
    assert.equal(response.status(), 200);
    await waitFor(page, () => (
      window.currentShotNumber === 1340 &&
      window.nowViewing === 26 &&
      window.screenImage?.complete &&
      (window.screenImage.naturalWidth || window.screenImage.width) === 1024 &&
      (window.screenImage.naturalHeight || window.screenImage.height) === 640 &&
      document.querySelector('#Screenie') &&
      /ss1314\.jpg/i.test(document.querySelector('#Screenie').style.backgroundImage)
    ), undefined, 'SSOTD #1314 lightbox', 30000);
    await page.waitForTimeout(500);
    const state = await page.evaluate(() => ({
      hash: location.hash,
      currentShotNumber: window.currentShotNumber,
      nowViewing: window.nowViewing,
      lightbox: Boolean(document.querySelector('#Screenie') && document.querySelector('#redBlock')),
      screenImage: window.screenImage ? {
        src: window.screenImage.src,
        complete: window.screenImage.complete,
        width: window.screenImage.naturalWidth || window.screenImage.width,
        height: window.screenImage.naturalHeight || window.screenImage.height
      } : null,
      screenStyle: document.querySelector('#Screenie')?.style.backgroundImage || '',
      visibleWidth: document.querySelector('#Screenie')?.getBoundingClientRect().width || 0,
      visibleHeight: document.querySelector('#Screenie')?.getBoundingClientRect().height || 0
    }));
    assert.equal(state.hash, '#1314');
    assert.equal(state.currentShotNumber, 1340);
    assert.equal(state.nowViewing, 26);
    assert.equal(state.lightbox, true);
    assert.equal(state.screenImage.width, 1024);
    assert.equal(state.screenImage.height, 640);
    assert.match(state.screenImage.src, /ss1314\.jpg$/i);
    assert.ok(state.visibleWidth > 0 && state.visibleHeight > 0, 'lightbox image has no visible box');
    await page.screenshot({ path: lightboxScreenshot, fullPage: true });
    return { status: response.status(), state, screenshot: lightboxScreenshot, requestCount: requests.length };
  } finally {
    await Promise.allSettled(page.__resourceRepairBodyPromises || []);
    await page.close().catch(() => {});
    await context.close();
  }
}

function requestedPathFromHref(href, pageUrl) {
  try {
    const value = new URL(href, pageUrl);
    return value.searchParams.get('requested') || '';
  } catch (_) {
    return '';
  }
}

async function checkArchivedRoutesAndForms() {
  const context = await newContext();
  const page = await context.newPage();
  attachTelemetry(page, 'archived-routes-and-forms');
  try {
    const mainRoutes = [
      { id: 'archivednews', route: 'info/archivednews.html' },
      { id: 'wow-news-06-2006', route: 'news/wow-news-06-2006.html' }
    ];
    const mainResults = [];
    for (const item of mainRoutes) {
      const response = await goto(page, item.route);
      const text = await bodyText(page);
      assert.equal(response.status(), 200, `${item.route} did not return HTTP 200`);
      assert.ok(text.trim().length > 200, `${item.route} has no substantive body text`);
      mainResults.push({ id: item.id, route: item.route, status: response.status(), finalPath: new URL(page.url()).pathname, bodyTextLength: text.trim().length });
      if (item.id === 'archivednews') {
        const state = await page.evaluate(aliasPaths => {
          const links = [...document.querySelectorAll('a[href]')];
          const targetedMissing = links.map(link => ({
            text: (link.textContent || '').trim(),
            href: link.href,
            requested: (() => { try { return new URL(link.href).searchParams.get('requested') || ''; } catch (_) { return ''; } })()
          })).filter(item => aliasPaths.includes(new URL(item.requested || 'http://invalid').pathname));
          const form = document.querySelector('#topSearch');
          return {
            targetedMissing,
            form: form ? {
              method: (form.getAttribute('method') || 'get').toLowerCase(),
              action: form.getAttribute('action') || '',
              searchBox: Boolean(form.querySelector('#searchBox')),
              searchType: Boolean(form.querySelector('#searchType')),
              editableCount: form.querySelectorAll('input,select,textarea,button').length,
              onsubmit: form.getAttribute('onsubmit') || ''
            } : null
          };
        }, [
          '/info/basics/dailyquests.shtml',
          '/info/basics/titles.shtml',
          '/info/basics/benice.shtml',
          '/info/credits.shtml',
          '/info/info/items/armorsets/'
        ]);
        assert.equal(state.targetedMissing.length, 0, 'archivednews still contains targeted missing-resource aliases');
        assert.ok(state.form, 'historical search form is missing');
        assert.notEqual(state.form.method, 'post', 'historical form unexpectedly uses POST');
        assert.equal(state.form.searchBox, true);
        assert.equal(state.form.searchType, true);
        assert.ok(state.form.editableCount >= 2);
        await page.locator('#searchBox').fill('history');
        await page.locator('#searchType').selectOption('site');
        mainResults.at(-1).form = state.form;
        mainResults.at(-1).targetedMissing = state.targetedMissing;
      }
    }

    const aliases = [
      { id: 'dailyquests-shtml', route: 'info/basics/dailyquests.shtml', expectedSuffix: '/info/basics/dailyquests.html' },
      { id: 'titles-shtml', route: 'info/basics/titles.shtml', expectedSuffix: '/info/basics/titles.html' },
      { id: 'benice-shtml', route: 'info/basics/benice.shtml', expectedSuffix: '/info/basics/benice.html' },
      { id: 'credits-shtml', route: 'info/credits.shtml', expectedSuffix: '/info/credits.html' },
      { id: 'double-info-armorsets', route: 'info/info/items/armorsets/', expectedSuffixes: ['/info/items/armorsets.html', '/info/items/armorsets/index.html'] }
    ];
    const aliasResults = [];
    for (const item of aliases) {
      const response = await goto(page, item.route);
      const text = await bodyText(page);
      const finalPath = new URL(page.url()).pathname;
      assert.equal(response.status(), 200, `${item.route} did not return HTTP 200`);
      assert.ok(text.trim().length > 200, `${item.route} resolved without substantive body text`);
      assert.ok(!finalPath.includes('/__offline/missing.html'), `${item.route} resolved to missing.html`);
      const allowedSuffixes = item.expectedSuffixes || [item.expectedSuffix];
      assert.ok(allowedSuffixes.some(suffix => finalPath.endsWith(suffix)), `${item.route} resolved to unexpected path ${finalPath}`);
      aliasResults.push({ id: item.id, requestedRoute: item.route, status: response.status(), finalPath, bodyTextLength: text.trim().length });
    }
    return { main: mainResults, aliases: aliasResults };
  } finally {
    await Promise.allSettled(page.__resourceRepairBodyPromises || []);
    await page.close().catch(() => {});
    await context.close();
  }
}

function parseNavtreeSource(source, sourceKind) {
  const sandbox = {
    navigator: { userAgent: 'node', appVersion: '' },
    console: { log() {}, warn() {}, error() {} }
  };
  let vmError = null;
  try {
    vm.runInNewContext(source, sandbox, { timeout: 3000, filename: 'navtree-main.js' });
  } catch (error) {
    vmError = String(error);
  }
  const parent = Array.isArray(sandbox.Menu1_6) ? sandbox.Menu1_6 : null;
  const entries = [];
  const expression = /Menu1_6_(\d+)\s*=\s*new Array\(\s*bulletImg\s*\+\s*"([^"]+)"/g;
  let match;
  while ((match = expression.exec(source))) entries.push({ id: `Menu1_6_${match[1]}`, name: match[2] });
  return {
    sourceKind,
    vmError,
    parentId: 'Menu1_6',
    parentCount: parent ? parent[3] : null,
    vmParent: parent,
    directEntries: entries,
    directEntryCount: entries.length,
    directNodeIds: [...new Set(entries.map(item => item.id))],
    fanSitesEntries: entries.filter(item => /fan\s*sites/i.test(item.name)),
    fanWallpapersEntries: entries.filter(item => /fan\s*wallpapers/i.test(item.name))
  };
}

async function checkHomeNavigationData() {
  const context = await newContext();
  const page = await context.newPage();
  attachTelemetry(page, 'home-navigation-data');
  try {
    const response = await goto(page, 'index.xml');
    assert.equal(response.status(), 200);
    const home = await page.evaluate(() => {
      const anchors = [...document.querySelectorAll('a[href]')].map(anchor => ({
        text: (anchor.textContent || '').replace(/\s+/g, ' ').trim(),
        href: anchor.getAttribute('href') || '',
        absolute: anchor.href
      }));
      const resources = performance.getEntriesByType('resource').map(entry => entry.name);
      return {
        fanSites: anchors.filter(item => /fan\s*sites/i.test(item.text)),
        fanWallpapers: anchors.filter(item => /fan\s*wallpapers/i.test(item.text)),
        navtreeMainResources: resources.filter(item => /navtree-main\.js/i.test(item)),
        bodyTextLength: (document.body?.textContent || '').trim().length
      };
    });
    assert.ok(home.bodyTextLength > 200);
    assert.ok(home.fanSites.some(item => !/missing\.html/i.test(item.href)) || home.fanSites.length > 0, 'FanSites menu data missing');
    assert.ok(home.fanWallpapers.some(item => !/missing\.html/i.test(item.href)) || home.fanWallpapers.length > 0, 'FanWallpapers menu data missing');

    const menuXml = await page.evaluate(async relative => {
      const response = await fetch(relative);
      return { status: response.status, text: await response.text() };
    }, urlFor('new-hp/layout/menu.xml'));
    assert.equal(menuXml.status, 200);
    const menuData = await page.evaluate(xmlText => {
      const document = new DOMParser().parseFromString(xmlText, 'application/xml');
      const category = [...document.querySelectorAll('category')].find(item => item.getAttribute('name') === 'menuCommunity');
      const items = category ? [...category.querySelectorAll(':scope > menuItem')].map(item => ({ name: item.getAttribute('name'), url: item.getAttribute('url') })) : [];
      return { parentId: 'menuCommunity', parentCount: items.length, items };
    }, menuXml.text);
    assert.equal(menuData.parentCount, 11, 'menuCommunity parent count is not 11');
    assert.ok(menuData.items.some(item => /^fansites$/i.test(item.name) && /community\/fansites\.html/i.test(item.url)));
    assert.ok(menuData.items.some(item => /^fan wallpapers$/i.test(item.name) && /fan-wallpapers/i.test(item.url)));

    let navtreeSource = null;
    let navtreeSourceKind = null;
    const navtreeUrl = urlFor('shared/wow-com/includes-client/navtree-main.js');
    try {
      const fetched = await page.evaluate(async relative => {
        const response = await fetch(relative);
        return { status: response.status, text: await response.text() };
      }, navtreeUrl);
      if (fetched.status === 200 && /Menu1_6/.test(fetched.text)) {
        navtreeSource = fetched.text;
        navtreeSourceKind = home.navtreeMainResources.length ? 'browser-loaded-resource' : 'browser-fetched-loopback';
      }
    } catch (_) {
      // The local source fallback below is intentional when the page route does not expose this legacy script.
    }
    if (!navtreeSource) {
      const localPath = path.resolve(siteRoot, 'offline/site/shared/wow-com/includes-client/navtree-main.js');
      navtreeSource = fs.readFileSync(localPath, 'utf8');
      navtreeSourceKind = 'node-vm-local-source';
    }
    const navtree = parseNavtreeSource(navtreeSource, navtreeSourceKind);
    assert.equal(navtree.vmError, null, `navtree-main.js VM evaluation failed: ${navtree.vmError}`);
    assert.equal(navtree.parentCount, 11, `navtree-main.js ${navtree.parentId} parent count is not 11`);
    assert.ok(navtree.fanSitesEntries.length > 0, 'navtree-main.js Fan Sites node missing');
    assert.ok(navtree.fanWallpapersEntries.length > 0, 'navtree-main.js Fan Wallpapers node missing');
    return { status: response.status(), home, menuData, navtree: { ...navtree, vmParent: undefined } };
  } finally {
    await Promise.allSettled(page.__resourceRepairBodyPromises || []);
    await page.close().catch(() => {});
    await context.close();
  }
}

async function checkFreeTrials() {
  const context = await newContext();
  const page = await context.newPage();
  const requests = attachTelemetry(page, 'free-trials');
  try {
    const response = await goto(page, 'burningcrusade/trial/index.html');
    assert.equal(response.status(), 200);
    const state = await page.evaluate(() => {
      const body = (document.body?.textContent || '').replace(/\s+/g, ' ').trim();
      const anchors = [...document.querySelectorAll('a[href]')].map(anchor => {
        const rawHref = anchor.getAttribute('href') || '';
        const absoluteHref = anchor.href || rawHref;
        const signupLike = /signup(?:\.|\/|\?|_|-)|10dayfreetrial/i.test(`${rawHref} ${absoluteHref}`);
        const missingRoute = /\/__offline\/missing\.html(?:[?#]|$)/i.test(absoluteHref);
        return {
          text: (anchor.textContent || '').replace(/\s+/g, ' ').trim(),
          rawHref,
          href: absoluteHref,
          signupLike,
          active: signupLike && !missingRoute,
          missingRoute
        };
      });
      const scriptCode = [...document.scripts].map(script => `${script.src || ''}\n${script.textContent || ''}`);
      const eventCode = [...document.querySelectorAll('*')].flatMap(element => [...element.attributes]
        .filter(attribute => /^on/i.test(attribute.name))
        .map(attribute => `${attribute.name}=${attribute.value}`));
      const allCode = [...scriptCode, ...eventCode];
      return {
        title: document.title,
        bodyText: body,
        bodyTextLength: body.length,
        historicalMarker: /historical|retired|archive|preservation/i.test(body) && /exhibit/i.test(body),
        forms: document.forms.length,
        formActions: [...document.forms].map(form => form.getAttribute('action') || ''),
        controls: document.querySelectorAll('input, select, textarea, button').length,
        signupLinks: anchors.filter(item => item.signupLike),
        activeSignupLinks: anchors.filter(item => item.active),
        codeTokens: {
          afftrack: allCode.filter(item => /afftrack/i.test(item)).length,
          setCookies: allCode.filter(item => /setCookies\s*\(/i.test(item)).length
        },
        cookie: document.cookie,
        anchorCount: anchors.length
      };
    });
    assert.match(state.bodyText, /\b(?:10|ten)[- ]day(?:\s+free)?\s+trial\b/i, 'Free Trials page lost its historical trial text');
    assert.equal(state.historicalMarker, true, 'Free Trials page has no visible historical-exhibit marker');
    assert.equal(state.forms, 0, 'Free Trials historical exhibit contains a form');
    assert.equal(state.activeSignupLinks.length, 0, 'Free Trials page retains an active signup link');
    assert.equal(state.codeTokens.afftrack, 0, 'Free Trials page retains afftrack code');
    assert.equal(state.codeTokens.setCookies, 0, 'Free Trials page retains setCookies code');
    assert.ok(trialSourceEvidence, 'validated Free Trials source-map evidence is missing');
    assert.equal(trialSourceEvidence.http_status, 200);
    assert.equal(trialSourceEvidence.actual_timestamp, '20080402004057');
    await page.screenshot({ path: freeTrialsScreenshot, fullPage: true });
    return {
      status: response.status(),
      finalPath: new URL(page.url()).pathname,
      sourceEvidence: trialSourceEvidence,
      state,
      requestCount: requests.length
    };
  } finally {
    await Promise.allSettled(page.__resourceRepairBodyPromises || []);
    await page.close().catch(() => {});
    await context.close();
  }
}

async function checkWrathWallpapers() {
  const context = await newContext();
  const page = await context.newPage();
  const requests = attachTelemetry(page, 'wrath-wallpapers');
  try {
    const response = await goto(page, 'wrath/wallpapers.xml');
    assert.equal(response.status(), 200);
    const body = await bodyText(page);
    assert.match(body, /Utgarde Keep/i, 'Wrath Wallpapers page is missing Utgarde Keep');
    assert.match(body, /\bLogo\b/i, 'Wrath Wallpapers page is missing Logo');
    const state = await page.evaluate(() => {
      const wallpaperPattern = /\/wrath\/images\/wallpapers\/(wall\d+)\/\1-(\d+x\d+)\.jpg$/i;
      const links = [...document.querySelectorAll('a[href]')].map(anchor => {
        const href = anchor.getAttribute('href') || '';
        try {
          const url = new URL(href, location.href);
          const match = wallpaperPattern.exec(url.pathname);
          return match ? { href, path: url.pathname, wallId: match[1], size: match[2] } : null;
        } catch (_) {
          return null;
        }
      }).filter(Boolean);
      const sizeCounts = {};
      const setCounts = {};
      for (const item of links) {
        sizeCounts[item.size] = (sizeCounts[item.size] || 0) + 1;
        setCounts[item.wallId] = (setCounts[item.wallId] || 0) + 1;
      }
      const html = document.documentElement?.outerHTML || '';
      const refs = pattern => [...html.matchAll(pattern)].map(match => match[1].toLowerCase());
      const thumbRefs = [...new Set(refs(/(?:\/|&)??(wall\d+\/wall\d+-thumb\.jpg)/gi))];
      const shadowRefs = [...new Set(refs(/(?:\/|&)??(wall\d+\/wall\d+-shadow\.png)/gi))];
      return {
        title: document.title,
        bodyTextLength: (document.body?.textContent || '').replace(/\s+/g, ' ').trim().length,
        originalLinkCount: links.length,
        originalLinks: links,
        sizeCounts,
        setCounts,
        thumbRefs,
        shadowRefs,
        menuRouteAnchors: [...document.querySelectorAll('a[href]')]
          .map(anchor => anchor.href || '')
          .filter(href => /\/wrath\/wallpapers\.xml(?:[?#]|$)/i.test(href))
      };
    });
    assert.ok(wallpaperAudit, `wallpaper audit is missing: ${wallpaperAuditPath}`);
    assert.equal(wallpaperAudit.schema, 'wow-encyclopedia-wrath-wallpaper-audit/v1');
    const expectedSizes = wallpaperAudit.page_content.size_kinds;
    assert.deepEqual(Object.keys(state.sizeCounts).sort(), [...expectedSizes].sort(), 'Wrath wallpaper size set changed');
    assert.equal(state.originalLinkCount, wallpaperAudit.page_content.local_page_wallpaper_link_count);
    assert.equal(state.originalLinkCount, 28);
    assert.deepEqual(state.sizeCounts, Object.fromEntries(expectedSizes.map(size => [size, 4])));
    assert.deepEqual(state.setCounts, { wall2: 7, wall6: 7, wall7: 7, wall8: 7 });
    assert.ok(state.thumbRefs.length >= 4, 'Wrath Wallpapers page has fewer than four thumbnail references');
    assert.ok(state.shadowRefs.length >= 4, 'Wrath Wallpapers page has fewer than four shadow references');
    assert.equal(wallpaperAudit.totals.missing_original_count, 0);
    assert.equal(wallpaperAudit.totals.missing_thumbnail_count, 0);
    assert.equal(wallpaperAudit.totals.missing_shadow_count, 0);
    assert.ok(wallpaperSourceEvidence, 'validated frozen Wrath Wallpapers source-map evidence is missing');
    assert.equal(wallpaperSourceEvidence.actual_timestamp, '20080509072957');
    assert.equal(wallpaperSourceEvidence.role, 'frontier_full_local_page_2008');
    assert.match(wallpaperSourceEvidence.local_path || '', /^offline[\\/]source-entities-pages-recovery[\\/]/i);
    assert.ok(wallpaperComparisonEvidence, 'comparison Wrath Wallpapers source-map evidence is missing');
    assert.equal(wallpaperComparisonEvidence.http_status, 200);
    assert.equal(wallpaperComparisonEvidence.actual_timestamp, '20080402070813');

    const menuResponse = await page.evaluate(async url => {
      const result = await fetch(url);
      return { status: result.status, text: await result.text() };
    }, urlFor('new-hp/js/menu3_var.js'));
    assert.equal(menuResponse.status, 200, 'Wrath menu source did not return HTTP 200');
    const menuMatch = menuResponse.text.match(/Menu14_2_3\s*=\s*new Array\([\s\S]{0,240}?Wallpapers[\s\S]{0,240}?\/wrath\/wallpapers\.xml/i);
    assert.ok(menuMatch, 'Wrath menu does not expose Media > Wallpapers');
    await page.screenshot({ path: wallpaperScreenshot, fullPage: true });
    return {
      status: response.status(),
      finalPath: new URL(page.url()).pathname,
      sourceEvidence: {
        active: wallpaperSourceEvidence,
        comparison: wallpaperComparisonEvidence
      },
      state: {
        title: state.title,
        bodyTextLength: state.bodyTextLength,
        originalLinkCount: state.originalLinkCount,
        sizeCounts: state.sizeCounts,
        setCounts: state.setCounts,
        thumbnailReferenceCount: state.thumbRefs.length,
        shadowReferenceCount: state.shadowRefs.length,
        menuRouteAnchors: state.menuRouteAnchors
      },
      baseline: {
        pagePresent: wallpaperAudit.totals.page_present,
        localWallpaperAssetCount: wallpaperAudit.totals.local_wallpaper_asset_count,
        linkedOriginalCount: wallpaperAudit.totals.linked_original_count,
        existingOriginalCount: wallpaperAudit.totals.existing_original_count,
        missingOriginalCount: wallpaperAudit.totals.missing_original_count,
        linkedThumbnailCount: wallpaperAudit.totals.linked_thumbnail_count,
        existingThumbnailCount: wallpaperAudit.totals.existing_thumbnail_count,
        missingThumbnailCount: wallpaperAudit.totals.missing_thumbnail_count,
        missingShadowCount: wallpaperAudit.totals.missing_shadow_count,
        sets: wallpaperAudit.sets.map(item => ({ id: item.id, title: item.title, linkedOriginalCount: item.linked_original_count }))
      },
      menu: {
        status: menuResponse.status,
        id: 'Menu14_2_3',
        label: 'Wallpapers',
        route: '/wrath/wallpapers.xml',
        matched: true
      },
      requestCount: requests.length
    };
  } finally {
    await Promise.allSettled(page.__resourceRepairBodyPromises || []);
    await page.close().catch(() => {});
    await context.close();
  }
}

async function checkPvpFlashRewards() {
  const context = await newContext();
  const page = await context.newPage();
  const requests = attachTelemetry(page, 'pvp-flash-rewards');
  const dependencyResponses = [];
  page.on('response', response => {
    const itemPath = relativePath(response.url());
    if (/(?:\.swf(?:$|[?#])|activexfix|navtree|menu132|__offline\/)/i.test(itemPath)) {
      capPush(dependencyResponses, {
        path: itemPath,
        url: response.url(),
        status: response.status(),
        contentType: response.headers()['content-type'] || ''
      }, 80);
    }
  });
  const candidateRoutes = ['pvp/flash-rewards/', 'pvp/flash-rewards/index.html'];
  try {
    const attempts = [];
    let selected = null;
    for (const route of candidateRoutes) {
      const response = await goto(page, route);
      const attempt = await page.evaluate(() => {
        const title = document.title || '';
        const clone = document.body ? document.body.cloneNode(true) : null;
        clone?.querySelectorAll('script,style,noscript,template').forEach(node => node.remove());
        const visibleText = (clone?.textContent || '').replace(/\s+/g, ' ').trim();
        const finalPath = window.location.pathname;
        const signature = `${title}\n${visibleText}`;
        const missingPage = /\/__offline\/missing\.html(?:$|[?#])/i.test(finalPath) ||
          /(?:404\s+(?:file\s+)?not\s+found|page\s+not\s+found|invalid-overlay-or-uncollected-site-resource)/i.test(signature);
        return {
          finalPath,
          title,
          visibleTextLength: visibleText.length,
          visibleTextSample: visibleText.slice(0, 500),
          missingPage
        };
      });
      const item = { requestedRoute: route, status: response.status(), ...attempt };
      attempts.push(item);
      if (response.status() === 200 && !attempt.missingPage) {
        selected = item;
        break;
      }
    }

    assert.ok(selected, `PvP route candidates did not produce a usable page: ${JSON.stringify(attempts)}`);
    assert.equal(selected.status, 200, 'PvP Mini Site did not return HTTP 200');
    assert.ok(!selected.missingPage, 'PvP Mini Site resolved to a missing/uncollected page');

    const state = await page.evaluate(() => {
      const clone = document.body ? document.body.cloneNode(true) : null;
      clone?.querySelectorAll('script,style,noscript,template').forEach(node => node.remove());
      const visibleText = (clone?.textContent || '').replace(/\s+/g, ' ').trim();
      const title = document.title || '';
      const signature = `${title}\n${visibleText}`;
      const bodyMissingMarkers = {
        missingRoute: /\/__offline\/missing\.html(?:$|[?#])/i.test(window.location.pathname),
        notFound: /(?:404\s+(?:file\s+)?not\s+found|page\s+not\s+found)/i.test(signature),
        uncollected: /invalid-overlay-or-uncollected-site-resource|\buncollected\b/i.test(signature)
      };

      const objectNodes = [...document.querySelectorAll('object')];
      const embedNodes = [...document.querySelectorAll('embed')];
      const paramNodes = [...document.querySelectorAll('param')];
      const movieRefs = paramNodes
        .filter(node => /^(?:movie|src|data)$/i.test(node.getAttribute('name') || ''))
        .map(node => node.getAttribute('value') || '')
        .filter(Boolean);
      const embedRefs = embedNodes
        .map(node => node.getAttribute('src') || '')
        .filter(Boolean);
      const objectRefs = objectNodes
        .flatMap(node => [node.getAttribute('data') || '', node.getAttribute('codebase') || ''])
        .filter(Boolean);
      const flashReferences = [...new Set([...movieRefs, ...embedRefs, ...objectRefs])]
        .filter(value => /(?:\.swf(?:$|[?#])|shockwave|flash)/i.test(value));

      const unavailableNodes = [...document.querySelectorAll('[data-archive-flash-unavailable]')];
      const unavailableTexts = unavailableNodes.map(node => (node.textContent || '').replace(/\s+/g, ' ').trim()).filter(Boolean);
      const unavailableRects = unavailableNodes.map(node => {
        const rect = node.getBoundingClientRect();
        const style = getComputedStyle(node);
        return {
          width: Math.round(rect.width),
          height: Math.round(rect.height),
          display: style.display,
          visibility: style.visibility,
          text: (node.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 400)
        };
      });
      const anchors = [...document.querySelectorAll('a[href]')].map(anchor => {
        const rawHref = anchor.getAttribute('href') || '';
        let href = anchor.href || rawHref;
        let url = null;
        try { url = new URL(href, location.href); href = url.href; } catch (_) {}
        return {
          text: (anchor.textContent || '').replace(/\s+/g, ' ').trim(),
          rawHref,
          href,
          origin: url?.origin || null,
          path: url?.pathname || null
        };
      });
      const localNavigationLinks = anchors.filter(item =>
        item.origin === location.origin &&
        /(?:archive\s*home|game\s*guide|return)/i.test(item.text) &&
        !/__offline\/missing\.html/i.test(item.href)
      );
      const scripts = [...document.scripts].map(script => ({
        src: script.src || '',
        inline: (script.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 500)
      }));
      const legacyScriptRefs = scripts.filter(item => /(?:activexfix|navtree|menu132|navtreefunctions)/i.test(`${item.src} ${item.inline}`));
      const legacyInlineMarkers = scripts.filter(item => /(?:printSubNav|printRelatedLinks|document\.write|mailto:|Menu\d)/i.test(`${item.src} ${item.inline}`));
      const mailtoLinks = anchors.filter(item => /^mailto:/i.test(item.rawHref));

      const rawDependencyRefs = [...document.querySelectorAll('[src],[href],[data],[background]')]
        .flatMap(node => ['src', 'href', 'data', 'background']
          .map(attribute => node.getAttribute(attribute) || '')
          .filter(Boolean))
        .filter(value => !/^(?:#|mailto:|javascript:|tel:)/i.test(value));
      const dependencyRefs = [...new Set(rawDependencyRefs)];
      const missingDependencyRefs = dependencyRefs.filter(value =>
        /(?:__offline\/missing\.html|__offline\/empty\.js|invalid-overlay-or-uncollected)/i.test(value)
      );
      const resourceEntries = performance.getEntriesByType('resource').map(entry => entry.name);
      const pluginNames = [...(navigator.plugins || [])].map(plugin => plugin.name || '').filter(Boolean);
      const flashPluginDetected = pluginNames.some(name => /shockwave\s+flash|flash\s+player/i.test(name));
      const visibleStaticMarkers = [...new Set([
        /Related Links:/i.test(visibleText) ? 'Related Links' : null,
        /Online Privacy Policy/i.test(visibleText) ? 'Online Privacy Policy' : null,
        /All rights reserved/i.test(visibleText) ? 'copyright' : null,
        /World of Warcraft/i.test(visibleText) ? 'World of Warcraft' : null,
        unavailableTexts.some(text => /intro\.swf/i.test(text)) ? 'Flash unavailable explanation' : null,
        localNavigationLinks.some(item => /archive\s*home/i.test(item.text)) ? 'ArchiveHome link' : null,
        localNavigationLinks.some(item => /game\s*guide/i.test(item.text)) ? 'GameGuide link' : null
      ].filter(Boolean))];
      return {
        finalPath: window.location.pathname,
        title,
        visibleText,
        visibleTextLength: visibleText.length,
        visibleStaticMarkers,
        bodyMissingMarkers,
        flash: {
          objectCount: objectNodes.length,
          embedCount: embedNodes.length,
          paramCount: paramNodes.length,
          movieRefs,
          embedRefs,
          flashReferences,
          pluginNames,
          pluginDetected: flashPluginDetected,
          available: flashPluginDetected,
          execution: 'intentionally-static-unavailable',
          reason: flashPluginDetected
            ? 'A Flash plugin was reported, but the repaired page intentionally presents a static unavailable notice.'
            : 'The repaired page intentionally presents a static unavailable notice because intro.swf was not recovered.'
        },
        fallback: {
          markerCount: unavailableNodes.length,
          texts: unavailableTexts,
          rects: unavailableRects,
          visible: unavailableRects.some(item => item.width > 0 && item.height > 0 && item.display !== 'none' && item.visibility !== 'hidden'),
          mentionsIntroSwf: unavailableTexts.some(text => /intro\.swf/i.test(text)),
          mentionsUnavailable: unavailableTexts.some(text => /(?:unavailable|not recovered|not been recovered|not available|missing)/i.test(text))
        },
        navigation: {
          links: localNavigationLinks,
          archiveHomeLinks: localNavigationLinks.filter(item => /archive\s*home/i.test(item.text)),
          gameGuideLinks: localNavigationLinks.filter(item => /game\s*guide/i.test(item.text)),
          mailtoLinks
        },
        legacyMarkup: {
          scriptCount: scripts.length,
          scripts,
          legacyScriptRefs,
          legacyInlineMarkers,
          mailtoLinks
        },
        dependencies: {
          referenceCount: dependencyRefs.length,
          flashReferences,
          missingReferenceCount: missingDependencyRefs.length,
          missingReferenceRefs: missingDependencyRefs.slice(0, 80),
          resourceEntryCount: resourceEntries.length,
          resourceEntries: resourceEntries.filter(value => /(?:\.swf|activexfix|navtree|menu132|__offline\/)/i.test(value)).slice(0, 80)
        }
      };
    });

    assert.match(state.title, /World of Warcraft PvP Mini Site/i, 'PvP page title is not the preserved Mini Site title');
    assert.ok(state.visibleTextLength > 40, 'PvP page has no visible static body text');
    assert.ok(state.visibleStaticMarkers.length > 0, 'PvP page has no visible static footer/related-links content');
    assert.equal(state.bodyMissingMarkers.missingRoute, false, 'PvP page resolved to missing.html');
    assert.equal(state.bodyMissingMarkers.notFound, false, 'PvP page contains a not-found marker');
    assert.equal(state.bodyMissingMarkers.uncollected, false, 'PvP page contains an uncollected marker');
    assert.equal(state.flash.objectCount, 0, 'PvP repair still exposes a legacy object element');
    assert.equal(state.flash.embedCount, 0, 'PvP repair still exposes a legacy embed element');
    assert.equal(state.legacyMarkup.legacyScriptRefs.length, 0, 'PvP repair still loads historical navigation/ActiveX scripts');
    assert.equal(state.legacyMarkup.legacyInlineMarkers.length, 0, 'PvP repair still contains historical script/mailto generation');
    assert.equal(state.legacyMarkup.mailtoLinks.length, 0, 'PvP repair still exposes mailto actions');
    assert.equal(state.fallback.markerCount > 0, true, 'PvP repair lacks data-archive-flash-unavailable');
    assert.equal(state.fallback.visible, true, 'PvP Flash unavailable explanation is not visibly rendered');
    assert.equal(state.fallback.mentionsIntroSwf, true, 'PvP Flash unavailable explanation does not name intro.swf');
    assert.equal(state.fallback.mentionsUnavailable, true, 'PvP Flash unavailable explanation does not state the missing/unavailable status');
    assert.ok(state.navigation.archiveHomeLinks.length > 0, 'PvP repair lacks a local ArchiveHome link');
    assert.ok(state.navigation.gameGuideLinks.length > 0, 'PvP repair lacks a local GameGuide link');

    const navigationChecks = await page.evaluate(async links => {
      const results = [];
      for (const link of links) {
        try {
          const response = await fetch(link.href, { method: 'GET' });
          results.push({ ...link, status: response.status, finalUrl: response.url });
        } catch (error) {
          results.push({ ...link, status: null, error: String(error) });
        }
      }
      return results;
    }, state.navigation.links);
    assert.ok(navigationChecks.some(item => item.status === 200 && !/__offline\/missing\.html/i.test(item.finalUrl || '')), 'PvP has no usable local return/navigation link');

    const scenarioPageErrors = report.pageErrors.filter(item => item.scenario === 'pvp-flash-rewards');
    const scenarioConsoleErrors = report.consoleErrors.filter(item => item.scenario === 'pvp-flash-rewards');
    assert.equal(scenarioPageErrors.length, 0, `PvP page errors remain: ${JSON.stringify(scenarioPageErrors)}`);
    assert.equal(scenarioConsoleErrors.length, 0, `PvP console errors remain: ${JSON.stringify(scenarioConsoleErrors)}`);

    assert.ok(pvpSourceEvidence, 'validated PvP source-map evidence is missing');
    assert.equal(pvpSourceEvidence.http_status, 200);
    assert.equal(pvpSourceEvidence.actual_timestamp, '20070115223911');
    assert.match(pvpSourceEvidence.title || '', /World of Warcraft PvP Mini Site/i);
    await page.screenshot({ path: pvpScreenshot, fullPage: true });

    const scenario404 = report.observed404.filter(item => item.scenario === 'pvp-flash-rewards');
    const scenarioFailures = report.requestFailures.filter(item => item.scenario === 'pvp-flash-rewards');
    const scenarioExternal = report.externalRequests.filter(item => item.scenario === 'pvp-flash-rewards');
    return {
      status: selected.status,
      routeAttempts: attempts,
      finalPath: state.finalPath,
      sourceEvidence: pvpSourceEvidence,
      state: {
        title: state.title,
        visibleTextLength: state.visibleTextLength,
        visibleTextSample: state.visibleText.slice(0, 800),
        visibleStaticMarkers: state.visibleStaticMarkers,
        bodyMissingMarkers: state.bodyMissingMarkers,
        flash: state.flash,
        fallback: state.fallback,
        navigation: {
          links: navigationChecks,
          archiveHomeLinks: state.navigation.archiveHomeLinks,
          gameGuideLinks: state.navigation.gameGuideLinks,
          mailtoLinks: state.navigation.mailtoLinks
        },
        legacyMarkup: {
          scriptCount: state.legacyMarkup.scriptCount,
          scripts: state.legacyMarkup.scripts,
          legacyScriptRefs: state.legacyMarkup.legacyScriptRefs,
          legacyInlineMarkers: state.legacyMarkup.legacyInlineMarkers,
          mailtoLinks: state.legacyMarkup.mailtoLinks
        },
        dependencies: {
          ...state.dependencies,
          dependencyResponses,
          observed404: scenario404,
          requestFailures: scenarioFailures,
          blockedExternalDependencies: scenarioExternal
        }
      },
      requestCount: requests.length
    };
  } finally {
    await Promise.allSettled(page.__resourceRepairBodyPromises || []);
    await page.close().catch(() => {});
    await context.close();
  }
}

(async () => {
  try {
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.mkdirSync(path.dirname(firstScreenshot), { recursive: true });
    fs.mkdirSync(path.dirname(lightboxScreenshot), { recursive: true });
    fs.mkdirSync(path.dirname(freeTrialsScreenshot), { recursive: true });
    fs.mkdirSync(path.dirname(wallpaperScreenshot), { recursive: true });
    fs.mkdirSync(path.dirname(pvpScreenshot), { recursive: true });
    browser = await chromium.launch({
      headless: true,
      ...(browserPath ? { executablePath: browserPath } : {})
    });

    const scenarios = [
      ['ssotd-first-page-and-layouts', checkSsotdFirstPage],
      ['ssotd-hash-1314-lightbox', checkSsotdHashLightbox],
      ['archived-routes-and-static-form', checkArchivedRoutesAndForms],
      ['home-navigation-data', checkHomeNavigationData],
      ['free-trials', checkFreeTrials],
      ['wrath-wallpapers', checkWrathWallpapers],
      ['pvp-flash-rewards', checkPvpFlashRewards]
    ];
    for (const [name, fn] of scenarios) {
      if (!onlyScenario || onlyScenario === name) await runScenario(name, fn);
    }
  } catch (error) {
    report.failures.push({ name: 'runner', error: String(error && error.stack ? error.stack : error).slice(0, 2400) });
  } finally {
    await Promise.allSettled(bodyPromises);
    if (browser) await browser.close().catch(() => {});
    report.counts = {
      scenarios: report.scenarios.length,
      passedScenarios: report.scenarios.filter(item => item.passed).length,
      externalRequests: report.externalRequests.length,
      nonGetRequests: report.nonGetRequests.length,
      requestFailures: report.requestFailures.length,
      consoleErrors: report.consoleErrors.length,
      pageErrors: report.pageErrors.length,
      observed404: report.observed404.length,
      imageBodies: report.imageBodies.length
    };
    if (report.externalRequests.length) report.failures.push({ name: 'external-requests-blocked', count: report.externalRequests.length, requests: report.externalRequests });
    if (report.nonGetRequests.length) report.failures.push({ name: 'non-get-requests-blocked', count: report.nonGetRequests.length, requests: report.nonGetRequests });
    if (report.pageErrors.length) report.failures.push({ name: 'page-errors', count: report.pageErrors.length, errors: report.pageErrors });
    if (report.consoleErrors.length) report.failures.push({ name: 'console-errors', count: report.consoleErrors.length, errors: report.consoleErrors });
    report.passed = report.failures.length === 0 && report.scenarios.length === expectedRunCount && report.counts.passedScenarios === expectedRunCount;
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n', 'utf8');
    console.log(JSON.stringify({
      passed: report.passed,
      scenarios: report.scenarios.length,
      passedScenarios: report.counts.passedScenarios,
      failures: report.failures,
      output,
      firstScreenshot,
      lightboxScreenshot,
      freeTrialsScreenshot,
      wallpaperScreenshot,
      pvpScreenshot,
      imageBodies: report.imageBodies
    }));
    if (!report.passed) process.exitCode = 1;
  }
})().catch(error => {
  console.error(error);
  process.exitCode = 1;
});

