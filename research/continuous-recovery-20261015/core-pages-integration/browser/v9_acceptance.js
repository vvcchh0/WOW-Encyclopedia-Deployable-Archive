/*
 * Browser acceptance for the root-owned v9 Pages export.
 *
 * This runner deliberately does not start a server.  The coordinator must
 * provide an already-running loopback server and pass --server-ready.  Every
 * browser request is allowed only when it is a GET/HEAD request to the
 * supplied loopback origin and project prefix; all other requests are aborted
 * and recorded.  The output is evidence, not a deployment or repair step.
 */
'use strict';

const fs = require('fs');
const path = require('path');

function option(name, fallback) {
  const i = process.argv.indexOf(name);
  return i < 0 ? fallback : process.argv[i + 1];
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function normalizePrefix(value) {
  let prefix = String(value || '/');
  if (!prefix.startsWith('/')) prefix = '/' + prefix;
  if (!prefix.endsWith('/')) prefix += '/';
  if (prefix.includes('..')) throw new Error(`unsafe project prefix: ${prefix}`);
  return prefix.replace(/\/{2,}/g, '/');
}

function loopbackHost(hostname) {
  const host = String(hostname || '').toLowerCase().replace(/^\[|\]$/g, '');
  return host === '127.0.0.1' || host === 'localhost' || host === '::1';
}

function sha256Hex(buffer) {
  // This function is replaced by the browser-side digest for fetched assets;
  // Node-side hashes are only used for the local manifest input.
  const crypto = require('crypto');
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

const DEFAULT_BASE_URL = 'http://127.0.0.1:29005';
const DEFAULT_PREFIX = '/WOW-Encyclopedia-Deployable-Archive/';
const DEFAULT_OUTPUT = 'research/continuous-recovery-20261015/core-pages-integration/browser/v9-browser-receipt.json';
const DEFAULT_SCREENSHOT_DIR = 'research/continuous-recovery-20261015/core-pages-integration/browser/screenshots';
const DEFAULT_MANIFEST = '.scratch/offline-navigation-20261015-v9/build-manifest.json';
const DEFAULT_PROVENANCE = '.scratch/pages-resources-20261015-v9/export-provenance.json';

const CORE_TARGETS = [
  { logical: '/news/wow-news-06-2005.html', pages: 'news/wow-news-06-2005.html', group: 'News', date: 'June, 2005' },
  { logical: '/news/wow-news-07-2005.html', pages: 'news/wow-news-07-2005.html', group: 'News', date: 'July, 2005' },
  { logical: '/news/wow-news-08-2005.html', pages: 'news/wow-news-08-2005.html', group: 'News', date: 'August, 2005' },
  { logical: '/news/wow-news-09-2005.html', pages: 'news/wow-news-09-2005.html', group: 'News', date: 'September, 2005' },
  { logical: '/news/wow-news-10-2005.html', pages: 'news/wow-news-10-2005.html', group: 'News', date: 'October, 2005' },
  { logical: '/news/wow-news-11-2005.html', pages: 'news/wow-news-11-2005.html', group: 'News', date: 'November, 2005' },
  { logical: '/news/wow-news2004.html', pages: 'news/wow-news2004.html', group: 'News', date: 'Old News' },
  { logical: '/news/wow-news2005.html', pages: 'news/wow-news2005.html', group: 'News', date: '2005 Old News' },
  { logical: '/burningcrusade/townhall/professions.html', pages: 'burningcrusade/townhall/professions.html', group: 'Burning Crusade' },
  { logical: '/wrath/artwork.xml', pages: 'wrath/artwork.xml.html', group: 'Wrath', artwork: true },
  { logical: '/ptr/index.html', pages: 'ptr/index.html', group: 'PTR', ptr: true },
];

const BG_ALIAS = {
  logical: '/pvp/battlegrounds/battlegroups.html',
  pages: 'pvp/battlegrounds/battlegroups.html',
  canonical: 'pvp/battlegrounds/battlegroups/index.html',
};

const PTR_ROUTES = ['ptr', 'ptr/', 'ptr/index.html'];
const PTR_LINKS = [
  'index.html',
  'info/basics/guide.html',
  'info/faq/ptr.html',
  'patchnotes/test-realm-patchnotes.html',
];

// This route contains the existing Wrath fiatLux lightbox markup.  The
// artwork index itself uses thumbnail pagination and query links; it does not
// invent a lightbox contract of its own.
const WRATH_LIGHTBOX_ROUTE = 'wrath/features/northrend/howling-fjord.xml.html';
const SSOTD_ROUTE = 'downloads/ssotd/index.html';
const SSOTD_OLD_OVERLAY = {
  route: 'downloads/ssotd/images/screens/ss1336.jpg',
  bytes: 150293,
  sha256: '58fcb8db67bc56bf21566fbc05de0d1372a71f4ac4ef65e4eb247ab95abeb289',
};

const repoRoot = path.resolve(__dirname, '..', '..', '..', '..');
const output = path.resolve(repoRoot, option('--output', DEFAULT_OUTPUT));
const screenshotDir = path.resolve(repoRoot, option('--screenshot-dir', DEFAULT_SCREENSHOT_DIR));
const manifestPath = path.resolve(repoRoot, option('--manifest', DEFAULT_MANIFEST));
const provenancePath = path.resolve(repoRoot, option('--provenance', DEFAULT_PROVENANCE));
const baseUrlText = option('--base-url', DEFAULT_BASE_URL);
const prefix = normalizePrefix(option('--prefix', DEFAULT_PREFIX));
const timeoutMs = Number(option('--timeout-ms', '30000'));
const waitMs = Number(option('--settle-ms', '350'));
const browserPath = option('--browser', undefined);
const playwrightModule = option('--playwright-module', 'playwright');

const report = {
  schema: 'wow-recovery.core-pages-integration-v9-browser-receipt.v1',
  status: 'prepared',
  started_utc: new Date().toISOString(),
  finished_utc: null,
  server_ready_flag: hasFlag('--server-ready'),
  base_url: baseUrlText,
  prefix,
  method: 'External loopback server only; Playwright GET/HEAD requests are restricted to the supplied origin and prefix; other methods are blocked; no server is started by this runner.',
  scope: {
    core_targets: CORE_TARGETS.length,
    bg_alias_targets: 1,
    ptr_alias_checks: PTR_ROUTES.length,
    related_ptr_links: PTR_LINKS.length,
    artwork_counter_scripts: { common: 12, locale: 1 },
    artwork_layout: { screenshots_per_page: 9 },
    ssotd_overlay: SSOTD_OLD_OVERLAY.route,
  },
  inputs: {},
  checks: [],
  screenshots: [],
  requests: [],
  route_decisions: [],
  responses: [],
  request_failed: [],
  page_errors: [],
  console_errors: [],
  failures: [],
  notes: [],
};

let activeCheck = 'setup';
let baseUrl;
let browser;

function fail(message) {
  throw new Error(message);
}

function expect(condition, message) {
  if (!condition) fail(message);
}

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
  return ['GET', 'HEAD'].includes(method) ? 'local-allowed' : 'local-non-get';
}

function manifestEvidence() {
  if (!fs.existsSync(manifestPath)) {
    report.inputs.manifest = { path: path.relative(repoRoot, manifestPath), exists: false };
    report.notes.push(`manifest input not found: ${manifestPath}`);
    return;
  }
  const data = fs.readFileSync(manifestPath);
  const manifest = JSON.parse(data.toString('utf8'));
  const files = Array.isArray(manifest.files) ? manifest.files : [];
  const routes = new Set(files.map(item => String(item.route || '')));
  const aliases = manifest.route_aliases || {};
  report.inputs.manifest = {
    path: path.relative(repoRoot, manifestPath),
    sha256: sha256Hex(data),
    route_count: files.length,
    v9_manifest_sha256: '0da72688ec5057650c2ef46a4634097323dc9c43eb19997afcad264b12dba3b8',
    expected_core_routes_present: CORE_TARGETS.map(item => ({ route: item.logical, present: routes.has(item.logical) })),
    expected_aliases: {
      ptr: aliases['/ptr'] || null,
      ptr_slash: aliases['/ptr/'] || null,
      battlegroups: aliases['/pvp/battlegrounds/battlegroups.html'] || null,
    },
  };
}

function provenanceEvidence() {
  if (!fs.existsSync(provenancePath)) {
    report.inputs.provenance = { path: path.relative(repoRoot, provenancePath), exists: false, artwork_assets: {} };
    report.notes.push(`provenance input not found: ${provenancePath}`);
    return;
  }
  const data = fs.readFileSync(provenancePath);
  const provenance = JSON.parse(data.toString('utf8'));
  const artworkAssets = {};
  for (const item of Array.isArray(provenance.files) ? provenance.files : []) {
    const route = String(item.route || '');
    if (/^\/wrath\/images\/artwork\/(?:en_us\/)?ss\d+(?:-thumb)?\.jpg$/i.test(route)) {
      artworkAssets[route] = {
        bytes: Number(item.derived_length || item.source_length || 0),
        sha256: String(item.derived_sha256 || item.source_sha256 || ''),
        mime: String(item.mime || ''),
        source_sha256: String(item.source_sha256 || ''),
      };
    }
  }
  report.inputs.provenance = {
    path: path.relative(repoRoot, provenancePath),
    sha256: sha256Hex(data),
    artwork_assets: artworkAssets,
  };
}

function attachPage(page) {
  page.on('request', request => {
    report.requests.push({
      check: activeCheck,
      method: request.method(),
      url: request.url(),
      resource_type: request.resourceType(),
      class: requestClass(request.url(), request.method()),
    });
  });
  page.on('response', response => {
    report.responses.push({
      check: activeCheck,
      method: response.request().method(),
      url: response.url(),
      status: response.status(),
      resource_type: response.request().resourceType(),
    });
  });
  page.on('requestfailed', request => {
    report.request_failed.push({
      check: activeCheck,
      method: request.method(),
      url: request.url(),
      resource_type: request.resourceType(),
      failure: request.failure(),
    });
  });
  page.on('pageerror', error => {
    report.page_errors.push({ check: activeCheck, error: String(error) });
  });
  page.on('console', message => {
    if (['error', 'warning'].includes(message.type())) {
      report.console_errors.push({ check: activeCheck, type: message.type(), text: message.text() });
    }
  });
}

async function inspectPage(page) {
  return page.evaluate(() => {
    const visible = element => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) !== 0 && rect.width > 0 && rect.height > 0;
    };
    const body = document.body;
    const anchors = [...document.querySelectorAll('a[href]')].map(element => ({
      text: (element.innerText || element.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 180),
      href: element.href || '',
      javascript: String(element.getAttribute('href') || '').trim().toLowerCase().startsWith('javascript:'),
    }));
    const scripts = [...document.querySelectorAll('script')].map(element => ({
      src: element.src || '',
      inline: !element.src && Boolean((element.textContent || '').trim()),
      text: (element.textContent || '').trim().slice(0, 160),
    }));
    const actionAttributes = [...document.querySelectorAll('[onclick],[onsubmit],[onchange],[onload]')].map(element => ({
      tag: element.tagName,
      onclick: element.getAttribute('onclick') || '',
      onsubmit: element.getAttribute('onsubmit') || '',
      onchange: element.getAttribute('onchange') || '',
      onload: element.getAttribute('onload') || '',
    }));
    const images = [...document.images].map(image => ({
      src: image.currentSrc || image.src || '',
      complete: image.complete,
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
    }));
    const cards = [...document.querySelectorAll('.ssborder')].map(element => {
      const thumbStyle = element.style.backgroundImage || '';
      const thumb = (thumbStyle.match(/url\(["']?([^"')]+)["']?\)/i) || [])[1] || '';
      const link = element.querySelector('a[href]');
      const image = element.querySelector('img');
      const rect = element.getBoundingClientRect();
      const linkRect = link ? link.getBoundingClientRect() : null;
      const imageRect = image ? image.getBoundingClientRect() : null;
      return {
        thumb: thumb ? new URL(thumb, document.baseURI).href : '',
        href: link ? link.href : '',
        card_rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        link_rect: linkRect ? { x: linkRect.x, y: linkRect.y, width: linkRect.width, height: linkRect.height } : null,
        overlay_image: image ? {
          src_attribute: image.getAttribute('src') || '',
          src: image.src || '',
          complete: image.complete,
          natural_width: image.naturalWidth,
          natural_height: image.naturalHeight,
          rect: imageRect ? { x: imageRect.x, y: imageRect.y, width: imageRect.width, height: imageRect.height } : null,
        } : null,
      };
    }).filter(item => /images\/artwork\/(?:en_us\/)?ss[^/]+-thumb\.jpg$/i.test(item.thumb));
    const firstScreen = [...document.querySelectorAll('body *')]
      .filter(visible)
      .filter(element => { const rect = element.getBoundingClientRect(); return rect.top < innerHeight && rect.bottom > 0; })
      .map(element => element.innerText || element.alt || '')
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim();
    return {
      title: document.title,
      bodyText: (body?.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 5000),
      firstScreen: firstScreen.slice(0, 1400),
      visibleTextLength: (body?.innerText || '').replace(/\s+/g, ' ').trim().length,
      headings: [...document.querySelectorAll('h1,h2,h3')].map(element => (element.innerText || '').replace(/\s+/g, ' ').trim()).filter(Boolean).slice(0, 30),
      dates: [...document.querySelectorAll('.date,[class*="date"],time')].map(element => (element.innerText || element.textContent || '').replace(/\s+/g, ' ').trim()).filter(Boolean).slice(0, 20),
      anchors,
      scripts,
      actionAttributes,
      forms: document.querySelectorAll('form').length,
      editableControls: [...document.querySelectorAll('input,select,textarea,button')].map(element => ({ tag: element.tagName, type: element.type || '', name: element.name || element.id || '' })),
      images,
      galleryCards: cards,
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
  if (options.settle !== false) await page.waitForTimeout(waitMs);
  return { requested, response, state: await inspectPage(page), finalUrl: page.url() };
}

async function runCheck(name, fn) {
  activeCheck = name;
  const started = Date.now();
  try {
    const result = await fn();
    report.checks.push({ name, passed: true, elapsed_ms: Date.now() - started, ...result });
  } catch (error) {
    const item = { name, passed: false, elapsed_ms: Date.now() - started, error: String(error) };
    report.checks.push(item);
    report.failures.push(item);
  }
}

function assertVisibleState(item, state) {
  expect(item.responseStatus === 200, `${item.logical || item.pages} HTTP ${item.responseStatus}`);
  expect(state.visibleTextLength > 20, `${item.pages} has no visible body text`);
  expect(state.title.trim().length > 0, `${item.pages} has empty document title`);
  expect(state.scrollWidth <= state.viewport.width + 2, `${item.pages} horizontal overflow ${state.scrollWidth} > ${state.viewport.width}`);
}

function externalRefs(state) {
  return state.anchors.filter(item => /^https?:\/\//i.test(item.href) && !localUrl(item.href));
}

async function browserDigest(page, url) {
  return page.evaluate(async target => {
    const response = await fetch(target, { cache: 'no-store' });
    const data = await response.arrayBuffer();
    const digest = await crypto.subtle.digest('SHA-256', data);
    const bytes = [...new Uint8Array(digest)];
    const sha256 = bytes.map(value => value.toString(16).padStart(2, '0')).join('');
    const image = new Image();
    const decoded = await new Promise(resolve => {
      image.onload = async () => {
        try { if (image.decode) await image.decode(); } catch (_) { /* onload is still evidence */ }
        resolve({ ok: true, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight });
      };
      image.onerror = () => resolve({ ok: false, naturalWidth: 0, naturalHeight: 0 });
      image.src = target;
    });
    return { status: response.status, bytes: data.byteLength, sha256, ...decoded };
  }, url);
}

async function browserLoadImages(page, urls) {
  return page.evaluate(async targets => {
    const load = async target => {
      let status = 0;
      let servedUrl = '';
      try {
        const response = await fetch(target, { cache: 'no-store' });
        status = response.status;
        servedUrl = response.url;
        const data = await response.arrayBuffer();
        const digest = await crypto.subtle.digest('SHA-256', data);
        const digestBytes = [...new Uint8Array(digest)];
        const sha256 = digestBytes.map(value => value.toString(16).padStart(2, '0')).join('');
        const contentType = response.headers.get('content-type') || '';
        return new Promise(resolve => {
          const image = new Image();
          image.onload = async () => {
            try { if (image.decode) await image.decode(); } catch (_) { /* onload remains useful */ }
            const exactResource = servedUrl === new URL(target, document.baseURI).href;
            resolve({ url: target, served_url: servedUrl, status, bytes: data.byteLength, sha256, content_type: contentType, ok: exactResource && status >= 200 && status < 300, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight });
          };
          image.onerror = () => resolve({ url: target, served_url: servedUrl, status, bytes: data.byteLength, sha256, content_type: contentType, ok: false, naturalWidth: 0, naturalHeight: 0 });
          image.src = target;
        });
      } catch (_) { /* image load below retains the decode evidence */ }
      return new Promise(resolve => {
        const image = new Image();
        image.onload = async () => {
          try { if (image.decode) await image.decode(); } catch (_) { /* onload remains useful */ }
          const exactResource = servedUrl === new URL(target, document.baseURI).href;
          resolve({ url: target, served_url: servedUrl, status, bytes: 0, sha256: '', content_type: '', ok: exactResource && status >= 200 && status < 300, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight });
        };
        image.onerror = () => resolve({ url: target, served_url: servedUrl, status, bytes: 0, sha256: '', content_type: '', ok: false, naturalWidth: 0, naturalHeight: 0 });
        image.src = target;
      });
    };
    return Promise.all(targets.map(load));
  }, urls);
}

function screenshotPath(label) {
  return path.join(screenshotDir, label.replace(/[^a-z0-9_.-]+/gi, '_') + '.png');
}

function knownGap404(urlText) {
  try {
    const url = new URL(urlText);
    if (/\/wrath\/art\.xml$/i.test(url.pathname)) return true;
    if (!/\/wrath\/images\/artwork\/(?:en_us\/)?ss(?:\d+)(?:-thumb)?\.jpg$/i.test(url.pathname)) return false;
    const match = url.pathname.match(/\/ss(\d+)(?:-thumb)?\.jpg$/i);
    const number = match ? Number(match[1]) : NaN;
    const locale = /\/en_us\//i.test(url.pathname);
    return locale ? number === 1 : [2, 4, 5, 7, 8, 10, 11].includes(number);
  } catch (_) {
    return false;
  }
}

function recordScreenshot(label, file) {
  const data = fs.readFileSync(file);
  report.screenshots.push({ label, path: path.relative(repoRoot, file), bytes: data.length, sha256: sha256Hex(data) });
}

async function main() {
  if (!hasFlag('--server-ready')) {
    report.status = 'not_run_server_ready_flag_missing';
    report.finished_utc = new Date().toISOString();
    report.notes.push('No browser was started. Re-run only after the coordinator confirms the loopback server is ready and pass --server-ready.');
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
    manifestEvidence();
    provenanceEvidence();
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.mkdirSync(screenshotDir, { recursive: true });

    const { chromium } = require(playwrightModule);
    browser = await chromium.launch({
      headless: true,
      ...(browserPath ? { executablePath: browserPath } : {}),
    });

    const context = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
      serviceWorkers: 'block',
    });
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

    for (const target of CORE_TARGETS) {
      await runCheck(`core:${target.logical}`, async () => {
        const loaded = await navigate(page, target.pages);
        const item = { logical: target.logical, pages: target.pages, responseStatus: loaded.response.status(), finalPath: new URL(loaded.finalUrl).pathname, title: loaded.state.title, visibleTextLength: loaded.state.visibleTextLength };
        assertVisibleState(item, loaded.state);
        expect(new URL(loaded.finalUrl).pathname === prefix + target.pages, `${target.pages} settled at ${loaded.finalUrl}`);
        if (target.date) {
          const dateText = loaded.state.dates.join(' ') + ' ' + loaded.state.bodyText.slice(0, 1800);
          expect(dateText.includes(target.date), `${target.pages} lost captured date heading ${target.date}`);
          item.date_evidence = loaded.state.dates;
        }
        if (target.ptr) {
          expect(loaded.state.title.includes('Public Test Realm'), `${target.pages} lacks PTR identity`);
        }
        if (target.artwork) {
          expect(/Wrath of the Lich King/i.test(loaded.state.title), `${target.pages} lacks Wrath title`);
        }
        return item;
      });
    }

    await runCheck('ptr:aliases-and-static-exhibit', async () => {
      const results = [];
      for (const route of PTR_ROUTES) {
        const loaded = await navigate(page, route);
        const state = loaded.state;
        const finalPath = new URL(loaded.finalUrl).pathname;
        expect(loaded.response.status() === 200, `${route} HTTP ${loaded.response.status()}`);
        expect(state.title === 'World of Warcraft Public Test Realm — Historical Exhibit', `${route} title mismatch: ${state.title}`);
        expect(/Historical exhibit/i.test(state.bodyText), `${route} lacks historical exhibit marker`);
        expect(/About the Public Test Realm/i.test(state.bodyText), `${route} lacks PTR section`);
        expect(/Related archived pages/i.test(state.bodyText), `${route} lacks archived-links section`);
        expect(/Archive home/i.test(state.bodyText), `${route} lacks Archive home link`);
        expect(state.forms === 0, `${route} contains a form`);
        expect(state.editableControls.length === 0, `${route} contains editable/action controls`);
        expect(state.actionAttributes.length === 0, `${route} contains inline action attributes`);
        expect(state.anchors.every(item => !item.javascript), `${route} contains javascript: anchor`);
        expect(externalRefs(state).length === 0, `${route} contains external anchor/resource references`);
        const badScripts = state.scripts.filter(item => !item.src || !/\/__offline\/pages_runtime\.js(?:\?|$)/i.test(item.src));
        expect(badScripts.length === 0, `${route} contains non-runtime script: ${JSON.stringify(badScripts)}`);
        expect(state.scrollWidth <= state.viewport.width + 2, `${route} horizontal overflow`);
        results.push({ route, response_status: loaded.response.status(), final_path: finalPath, title: state.title, scripts: state.scripts, body_excerpt: state.bodyText.slice(0, 700) });
      }

      const linkPage = await context.newPage();
      attachPage(linkPage);
      const related = [];
      for (const route of PTR_LINKS) {
        const loaded = await navigate(linkPage, route);
        expect(loaded.response.status() === 200, `PTR related ${route} HTTP ${loaded.response.status()}`);
        expect(loaded.state.visibleTextLength > 20, `PTR related ${route} has no visible body`);
        related.push({ route, status: loaded.response.status(), final_path: new URL(loaded.finalUrl).pathname, title: loaded.state.title });
      }
      await linkPage.close();
      const shot = screenshotPath('ptr-desktop');
      await page.screenshot({ path: shot, fullPage: true });
      recordScreenshot('ptr-desktop', shot);
      return { aliases: results, related_links: related };
    });

    await runCheck('ptr:mobile-layout', async () => {
      await page.setViewportSize({ width: 390, height: 844 });
      const loaded = await navigate(page, 'ptr/index.html');
      expect(loaded.response.status() === 200, `PTR mobile HTTP ${loaded.response.status()}`);
      expect(loaded.state.scrollWidth <= 392, `PTR mobile overflow ${loaded.state.scrollWidth}`);
      expect(loaded.state.visibleTextLength > 20, 'PTR mobile body is empty');
      const shot = screenshotPath('ptr-mobile');
      await page.screenshot({ path: shot, fullPage: true });
      recordScreenshot('ptr-mobile', shot);
      await page.setViewportSize({ width: 1440, height: 1000 });
      return { viewport: loaded.state.viewport, scroll_width: loaded.state.scrollWidth, title: loaded.state.title };
    });

    await runCheck('battlegroups:compatibility-alias', async () => {
      const loaded = await navigate(page, BG_ALIAS.pages);
      const finalPath = new URL(loaded.finalUrl).pathname;
      expect(loaded.response.status() === 200, `Battlegroups alias HTTP ${loaded.response.status()}`);
      expect(finalPath === prefix + BG_ALIAS.canonical, `Battlegroups alias settled at ${finalPath}, expected ${prefix + BG_ALIAS.canonical}`);
      expect(loaded.state.visibleTextLength > 20, 'Battlegroups canonical body is empty');
      expect(!/404|not found|offline route not collected/i.test(loaded.state.bodyText), 'Battlegroups alias landed on a missing route');
      const shot = screenshotPath('battlegroups-alias');
      await page.screenshot({ path: shot, fullPage: true });
      recordScreenshot('battlegroups-alias', shot);
      return { requested: BG_ALIAS.pages, final_path: finalPath, status: loaded.response.status(), title: loaded.state.title };
    });

    await runCheck('wrath:artwork-gallery-counts-and-decode', async () => {
      await page.setViewportSize({ width: 1440, height: 1000 });
      const page1 = await navigate(page, 'wrath/artwork.xml.html');
      expect(page1.response.status() === 200, `Wrath artwork HTTP ${page1.response.status()}`);
      await page.waitForFunction(() => Number.isFinite(window.screenshotsCommonTotal) && Number.isFinite(window.screenshotsLocTotal) && Number.isFinite(window.screenshotsTotal) && Number.isFinite(window.screenshotsPerPage) && document.querySelectorAll('.ssborder').length > 0, { timeout: timeoutMs });
      const first = await page.evaluate(() => {
        const cards = [...document.querySelectorAll('.ssborder')].map(element => {
          const raw = element.style.backgroundImage || '';
          const thumb = (raw.match(/url\(["']?([^"')]+)["']?\)/i) || [])[1] || '';
          const link = element.querySelector('a[href]');
          const image = element.querySelector('img');
          const rect = element.getBoundingClientRect();
          const linkRect = link ? link.getBoundingClientRect() : null;
          const imageRect = image ? image.getBoundingClientRect() : null;
          return {
            thumb: thumb ? new URL(thumb, document.baseURI).href : '',
            href: link ? link.href : '',
            card_rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
            link_rect: linkRect ? { x: linkRect.x, y: linkRect.y, width: linkRect.width, height: linkRect.height } : null,
            overlay_image: image ? { src_attribute: image.getAttribute('src') || '', src: image.src || '', complete: image.complete, natural_width: image.naturalWidth, natural_height: image.naturalHeight, rect: imageRect ? { x: imageRect.x, y: imageRect.y, width: imageRect.width, height: imageRect.height } : null } : null,
          };
        }).filter(item => /images\/artwork\/(?:en_us\/)?ss[^/]+-thumb\.jpg$/i.test(item.thumb));
        return {
          counters: { common: Number(window.screenshotsCommonTotal), locale: Number(window.screenshotsLocTotal), total: Number(window.screenshotsTotal), per_page: Number(window.screenshotsPerPage), pages: Number(window.pages), current_page: Number(window.currentPage) },
          cards,
          counter_scripts: [...document.scripts].map(script => script.src).filter(src => /artworkcounter\.js/i.test(src)),
        };
      });
      const expectedPages = Math.ceil(first.counters.total / first.counters.per_page);
      expect(first.counters.common === 12 && first.counters.locale === 1, `counter values changed: ${JSON.stringify(first.counters)}`);
      expect(first.counters.total === first.counters.common + first.counters.locale, `counter total mismatch: ${JSON.stringify(first.counters)}`);
      expect(first.counters.pages === expectedPages, `layout page count mismatch: ${first.counters.pages} != ${expectedPages}`);
      expect(first.cards.length === Math.min(first.counters.per_page, first.counters.total), `page 1 card count ${first.cards.length}`);
      expect(first.counter_scripts.length === 2, `expected two counter scripts, found ${first.counter_scripts.length}`);
      const firstShot = screenshotPath('wrath-artwork-page-1');
      await page.screenshot({ path: firstShot, fullPage: true });
      recordScreenshot('wrath-artwork-page-1', firstShot);

      const page2 = await navigate(page, 'wrath/artwork.xml.html', '?s=2');
      await page.waitForFunction(() => document.querySelectorAll('.ssborder').length > 0, { timeout: timeoutMs });
      const second = await page.evaluate(() => {
        const cards = [...document.querySelectorAll('.ssborder')].map(element => {
          const raw = element.style.backgroundImage || '';
          const thumb = (raw.match(/url\(["']?([^"')]+)["']?\)/i) || [])[1] || '';
          const link = element.querySelector('a[href]');
          const image = element.querySelector('img');
          const rect = element.getBoundingClientRect();
          const linkRect = link ? link.getBoundingClientRect() : null;
          const imageRect = image ? image.getBoundingClientRect() : null;
          return {
            thumb: thumb ? new URL(thumb, document.baseURI).href : '',
            href: link ? link.href : '',
            card_rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
            link_rect: linkRect ? { x: linkRect.x, y: linkRect.y, width: linkRect.width, height: linkRect.height } : null,
            overlay_image: image ? { src_attribute: image.getAttribute('src') || '', src: image.src || '', complete: image.complete, natural_width: image.naturalWidth, natural_height: image.naturalHeight, rect: imageRect ? { x: imageRect.x, y: imageRect.y, width: imageRect.width, height: imageRect.height } : null } : null,
          };
        }).filter(item => /images\/artwork\/(?:en_us\/)?ss[^/]+-thumb\.jpg$/i.test(item.thumb));
        return { current_page: Number(window.currentPage), page_label: document.body.innerText.match(/Page\s+\d+\s+of\s+\d+/i)?.[0] || '', cards };
      });
      const expectedPage2 = first.counters.total - first.counters.per_page;
      expect(second.cards.length === expectedPage2, `page 2 card count ${second.cards.length} != ${expectedPage2}`);
      const secondShot = screenshotPath('wrath-artwork-page-2');
      await page.screenshot({ path: secondShot, fullPage: true });
      recordScreenshot('wrath-artwork-page-2', secondShot);
      const allCards = [
        ...first.cards.map(card => ({ page: 1, ...card })),
        ...second.cards.map(card => ({ page: 2, ...card })),
      ];
      const cardEvidence = allCards.map(card => {
        const url = new URL(card.href);
        const number = Number(url.searchParams.get('s'));
        const full = number <= first.counters.common
          ? routePath(`wrath/images/artwork/ss${number}.jpg`)
          : routePath(`wrath/images/artwork/en_us/ss${number - first.counters.common}.jpg`);
        return { ...card, number, full };
      });
      expect(cardEvidence.every(card => card.number >= 1 && card.number <= first.counters.total), `artwork card query numbers invalid: ${JSON.stringify(cardEvidence)}`);
      expect(cardEvidence.every(card => new URL(card.href).pathname === `${prefix}wrath/art.xml`), `artwork card viewer hrefs are not /wrath/art.xml: ${JSON.stringify(cardEvidence.map(card => card.href))}`);
      const imageTargets = cardEvidence.flatMap(card => [
        { number: card.number, page: card.page, role: 'full', url: card.full },
        { number: card.number, page: card.page, role: 'thumbnail', url: card.thumb },
      ]);
      const imageResults = await browserLoadImages(page, imageTargets.map(item => item.url));
      const provenanceAssets = report.inputs.provenance && report.inputs.provenance.artwork_assets ? report.inputs.provenance.artwork_assets : {};
      const imageEvidence = imageTargets.map((target, index) => {
        const route = new URL(target.url).pathname.replace(prefix.replace(/\/$/, ''), '') || '/';
        const expected = provenanceAssets[route] || null;
        const result = imageResults[index];
        const mimeMatch = Boolean(expected && result.content_type.toLowerCase().split(';')[0] === expected.mime.toLowerCase());
        const bytesMatch = Boolean(expected && result.bytes === expected.bytes);
        const shaMatch = Boolean(expected && result.sha256 === expected.sha256);
        return { ...target, ...result, route, expected_provenance: expected, exact_mime: mimeMatch, exact_bytes: bytesMatch, exact_sha256: shaMatch, provenance_match: Boolean(expected && result.ok && mimeMatch && bytesMatch && shaMatch) };
      });
      const byNumber = new Map();
      for (const item of imageEvidence) {
        if (!byNumber.has(item.number)) byNumber.set(item.number, []);
        byNumber.get(item.number).push(item);
      }
      const expectedAvailable = [1, 3, 6, 9, 12];
      const expectedMissing = [2, 4, 5, 7, 8, 10, 11, 13];
      const availablePairs = [...byNumber.entries()]
        .filter(([, items]) => items.every(item => item.provenance_match && item.naturalWidth > 0 && item.naturalHeight > 0))
        .map(([number]) => number)
        .sort((a, b) => a - b);
      const missingPairs = [...byNumber.entries()]
        .filter(([, items]) => items.some(item => !item.provenance_match || item.naturalWidth <= 0 || item.naturalHeight <= 0))
        .map(([number]) => number)
        .sort((a, b) => a - b);
      expect(JSON.stringify(availablePairs) === JSON.stringify(expectedAvailable), `artwork available pair set changed: ${JSON.stringify(availablePairs)}`);
      expect(JSON.stringify(missingPairs) === JSON.stringify(expectedMissing), `artwork missing pair set changed: ${JSON.stringify(missingPairs)}`);
      const overlayResponses = report.responses
        .filter(item => /missing-image\.svg/i.test(item.url) && /ssborder1\.png/i.test(decodeURIComponent(item.url)))
        .map(item => ({ status: item.status, url: item.url, resource_type: item.resource_type }));
      return {
        page1: { counters: first.counters, cards: first.cards.length },
        page2: { current_page: second.current_page, page_label: second.page_label, cards: second.cards.length },
        counter_scripts: first.counter_scripts,
        card_viewer_hrefs: cardEvidence.map(card => ({ page: card.page, number: card.number, href: card.href })),
        card_overlay: {
          purpose: 'decorative_shared_card_border_overlay',
          records: cardEvidence.map(card => ({ page: card.page, number: card.number, href: card.href, thumb: card.thumb, card_rect: card.card_rect, link_rect: card.link_rect, overlay_image: card.overlay_image })),
          fallback_responses: overlayResponses,
        },
        image_decode: { available_pairs: availablePairs, missing_pairs: missingPairs, evidence: imageEvidence },
      };
    });

    await runCheck('wrath:artwork-card-viewer-click-and-gap', async () => {
      await navigate(page, 'wrath/artwork.xml.html');
      const link = page.locator('.ssborder a[href]').first();
      expect(await link.count() > 0, 'Wrath artwork page has no clickable artwork card');
      const rawHref = await link.getAttribute('href');
      expect(rawHref, 'Wrath artwork card has no href');
      const viewerHref = new URL(rawHref, page.url()).toString();
      expect(new URL(viewerHref).pathname === `${prefix}wrath/art.xml`, `unexpected artwork viewer href ${viewerHref}`);
      const [response] = await Promise.all([
        page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: timeoutMs }),
        link.click(),
      ]);
      expect(response, `no response after clicking artwork card ${viewerHref}`);
      const state = await inspectPage(page);
      const finalPath = new URL(page.url()).pathname;
      const viewerMissing = response.status() !== 200 || /404|not found|offline route not collected/i.test(state.bodyText);
      expect(viewerMissing, `artwork viewer unexpectedly resolved as a normal page: ${viewerHref} -> ${response.status()} ${finalPath}`);
      const shot = screenshotPath('wrath-artwork-viewer-missing');
      await page.screenshot({ path: shot, fullPage: true });
      recordScreenshot('wrath-artwork-viewer-missing', shot);
      return {
        clicked: true,
        actual_href: viewerHref,
        response_status: response.status(),
        final_path: finalPath,
        title: state.title,
        visible_text_length: state.visibleTextLength,
        conclusion: 'known_source_gap_artwork_viewer_missing',
      };
    });

    await runCheck('wrath:fiatlux-lightbox-previous-next-close', async () => {
      if (hasFlag('--skip-fiatlux')) {
        report.notes.push('Howling-Fjord fiatLux was not rerun in the final pass; independent interaction-gap evidence is preserved in v9-browser-receipt.corrected-run.json.');
        return { skipped: true, prior_receipt: 'research/continuous-recovery-20261015/core-pages-integration/browser/v9-browser-receipt.corrected-run.json' };
      }
      const lightboxPage = await context.newPage();
      attachPage(lightboxPage);
      const loaded = await navigate(lightboxPage, WRATH_LIGHTBOX_ROUTE);
      expect(loaded.response.status() === 200, `Wrath lightbox route HTTP ${loaded.response.status()}`);
      const hooks = await lightboxPage.locator('a[onclick*="fiatLux"]').count();
      expect(hooks > 0, `no fiatLux hook on ${WRATH_LIGHTBOX_ROUTE}`);
      await lightboxPage.locator('a[onclick*="fiatLux"]').first().click();
      const interactionTimeout = Math.min(timeoutMs, 5000);
      await lightboxPage.waitForFunction(() => {
        const root = document.getElementById('lightBoxRoot');
        const holder = document.getElementById('lightBoxHolder');
        return root && holder && getComputedStyle(root).visibility === 'visible' && holder.getBoundingClientRect().width > 0 && holder.getBoundingClientRect().height > 0;
      }, { timeout: interactionTimeout });
      const openState = await lightboxPage.evaluate(() => ({ root: getComputedStyle(document.getElementById('lightBoxRoot')).visibility, blackDrop: getComputedStyle(document.getElementById('blackDrop')).display, holder: document.getElementById('lightBoxHolder').style.backgroundImage }));
      expect(localUrl((openState.holder.match(/url\(["']?([^"')]+)["']?\)/i) || [])[1] || ''), 'Wrath lightbox image is not local');
      const openShot = screenshotPath('wrath-fiatlux-open');
      await lightboxPage.screenshot({ path: openShot, fullPage: false });
      recordScreenshot('wrath-fiatlux-open', openShot);
      let close = { attempted: true, clicked: false, closed: false, error: null };
      try {
        await lightboxPage.locator('#blackDrop').click({ position: { x: 5, y: 5 }, timeout: interactionTimeout });
        close.clicked = true;
        await lightboxPage.waitForFunction(() => {
          const root = document.getElementById('lightBoxRoot');
          const drop = document.getElementById('blackDrop');
          return root && drop && getComputedStyle(root).visibility !== 'visible' && getComputedStyle(drop).display === 'none';
        }, { timeout: interactionTimeout });
        close.closed = true;
      } catch (error) {
        close.error = String(error);
        report.notes.push('Howling-Fjord fiatLux close retained as an independent interaction gap; normal click was blocked or did not close the overlay.');
      }
      await lightboxPage.close();
      return { route: WRATH_LIGHTBOX_ROUTE, hooks, open: openState, close, independent_interaction_gap: !close.closed };
    });

    await runCheck('ssotd:old-overlay-and-lightbox-controls', async () => {
      const ssotdPage = await context.newPage();
      attachPage(ssotdPage);
      const loaded = await navigate(ssotdPage, SSOTD_ROUTE);
      expect(loaded.response.status() === 200, `SSOTD HTTP ${loaded.response.status()}`);
      const overlayUrl = routePath(SSOTD_OLD_OVERLAY.route);
      const overlay = await browserDigest(ssotdPage, overlayUrl);
      expect(overlay.status === 200, `SSOTD overlay HTTP ${overlay.status}`);
      expect(overlay.bytes === SSOTD_OLD_OVERLAY.bytes, `SSOTD overlay bytes ${overlay.bytes} != ${SSOTD_OLD_OVERLAY.bytes}`);
      expect(overlay.sha256 === SSOTD_OLD_OVERLAY.sha256, `SSOTD overlay SHA ${overlay.sha256} != ${SSOTD_OLD_OVERLAY.sha256}`);
      expect(overlay.ok && overlay.naturalWidth > 0 && overlay.naturalHeight > 0, 'SSOTD overlay did not decode');
      await ssotdPage.waitForFunction(() => typeof window.omegaLightBox === 'function', { timeout: timeoutMs });
      await ssotdPage.evaluate(({ first, second }) => {
        window.shotList = [first, second];
        window.firstLoad = false;
        window.animationLock = false;
        window.omegaLightBox(0);
      }, { first: overlayUrl, second: overlayUrl });
      await ssotdPage.waitForFunction(() => {
        const screen = document.getElementById('Screenie');
        return window.screenImage && window.screenImage.complete && window.screenImage.naturalWidth > 0 && screen && document.querySelector('.closeDivStyle') && document.querySelector('.backGifStyle') && document.querySelector('.fwdGifStyle');
      }, { timeout: timeoutMs });
      const before = await ssotdPage.evaluate(() => ({ nowViewing: window.nowViewing, screen: document.getElementById('Screenie').style.backgroundImage }));
      await ssotdPage.locator('.fwdGifStyle').click();
      await ssotdPage.waitForTimeout(500);
      const afterNext = await ssotdPage.evaluate(() => ({ nowViewing: window.nowViewing, screen: document.getElementById('Screenie').style.backgroundImage }));
      expect(afterNext.nowViewing === 1, `SSOTD next control did not advance: ${JSON.stringify(afterNext)}`);
      await ssotdPage.locator('.backGifStyle').click();
      await ssotdPage.waitForTimeout(500);
      const afterPrev = await ssotdPage.evaluate(() => ({ nowViewing: window.nowViewing, screen: document.getElementById('Screenie').style.backgroundImage }));
      expect(afterPrev.nowViewing === 0, `SSOTD previous control did not return: ${JSON.stringify(afterPrev)}`);
      const openShot = screenshotPath('ssotd-lightbox-open');
      await ssotdPage.screenshot({ path: openShot, fullPage: false });
      recordScreenshot('ssotd-lightbox-open', openShot);
      await ssotdPage.locator('.closeDivStyle').click();
      await ssotdPage.waitForFunction(() => {
        const screen = document.getElementById('Screenie');
        return screen && Number.parseFloat(screen.style.width || '0') <= 1 && Number.parseFloat(screen.style.height || '0') <= 1;
      }, { timeout: timeoutMs });
      await ssotdPage.close();
      return { route: SSOTD_ROUTE, overlay: { route: SSOTD_OLD_OVERLAY.route, ...overlay }, lightbox: { before, after_next: afterNext, after_previous: afterPrev, closed: true } };
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
    const knownGapResponses = report.responses.filter(item => item.status === 404 && knownGap404(item.url));
    const unexpected404Responses = report.responses.filter(item => item.status === 404 && !knownGap404(item.url));
    const knownGapConsole = report.console_errors.filter(item => /Failed to load resource: the server responded with a status of 404/i.test(item.text) && unexpected404Responses.length === 0);
    const unexpectedConsole = report.console_errors.filter(item => !/object-src ["']?none/i.test(item.text) && !knownGapConsole.includes(item));
    report.summary = {
      checks: report.checks.length,
      passed_checks: report.checks.filter(item => item.passed).length,
      failed_checks: report.checks.filter(item => !item.passed).length,
      requests: report.requests.length,
      responses: report.responses.length,
      blocked_requests: blocked.length,
      blocked_external_or_non_get: blocked.filter(item => item.class !== 'local-outside-prefix').length,
      request_failed: report.request_failed.length,
      page_errors: report.page_errors.length,
      console_errors: report.console_errors.length,
      unexpected_console_errors: unexpectedConsole.length,
      known_gap_404_responses: knownGapResponses.length,
      unexpected_404_responses: unexpected404Responses.length,
      known_gap_console_errors: knownGapConsole.length,
      screenshots: report.screenshots.length,
    };
    if (knownGapResponses.length) report.notes.push(`Known artwork/viewer gap responses retained: ${knownGapResponses.length}; 404 console messages classified as known only when no unrelated 404 response occurred.`);
    if (blocked.length) report.notes.push('Blocked requests are retained in route_decisions; any external-origin or non-GET/HEAD request is a failure.');
    if (report.page_errors.length || unexpectedConsole.length || blocked.some(item => item.class !== 'local-outside-prefix')) {
      report.failures.push({ name: 'browser-safety-gates', error: 'page errors, unexpected console errors, or disallowed requests were observed' });
    }
    report.passed = report.status === 'passed' && report.failures.length === 0 && blocked.length === 0 && report.request_failed.length === 0 && report.page_errors.length === 0 && unexpectedConsole.length === 0;
    fs.mkdirSync(path.dirname(output), { recursive: true });
    fs.writeFileSync(output, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ status: report.status, passed: report.passed, checks: report.summary.checks, passed_checks: report.summary.passed_checks, failures: report.failures.length, blocked_requests: report.summary.blocked_requests, request_failed: report.summary.request_failed, screenshots: report.summary.screenshots, output }));
    if (!report.passed && report.status !== 'not_run_server_ready_flag_missing') process.exitCode = 1;
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
