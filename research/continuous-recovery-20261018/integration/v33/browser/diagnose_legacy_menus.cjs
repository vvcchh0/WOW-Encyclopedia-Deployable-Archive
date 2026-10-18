/* Read-only v32/v33 legacy-menu baseline diagnostic.
 *
 * This is deliberately independent of check_v33_browser.cjs.  It starts two
 * loopback-only static servers, one for each frozen output, and records the
 * same four legacy pages under both outputs.  Every non-loopback request is
 * aborted and recorded; this script never edits a generated page.
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../../..');
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const PAGES = [
  'downloads/wallpapers/wallpaper107.html',
  'pvp/battlegrounds-part2.html',
  'pvp/battlegrounds.html',
  'pvp/battlegrounds/enemies-alterac.html',
];
const OUTPUTS = {
  v32: path.join(ROOT, '.scratch/pages-resources-20261018-v32'),
  v33: path.join(ROOT, '.scratch/pages-resources-20261018-v33'),
};
const RESULT = path.join(ROOT, 'research/continuous-recovery-20261018/integration/v33/browser/results/legacy-menu-baseline-diagnostic.json');

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}

function mimeFor(file) {
  const ext = path.extname(file).toLowerCase();
  return ({
    '.html': 'text/html; charset=utf-8', '.htm': 'text/html; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8', '.xml': 'application/xml; charset=utf-8',
    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
    '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp',
    '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.woff': 'font/woff',
    '.woff2': 'font/woff2', '.txt': 'text/plain; charset=utf-8',
  })[ext] || 'application/octet-stream';
}

function safePath(root, requestPath) {
  const raw = decodeURIComponent(requestPath.split('?', 1)[0].split('#', 1)[0]);
  if (!raw.startsWith(BASE_PATH)) return null;
  const relative = raw.slice(BASE_PATH.length).replace(/^\/+/, '');
  const candidate = path.resolve(root, relative);
  const relativeToRoot = path.relative(path.resolve(root), candidate);
  if (relativeToRoot.startsWith('..') || path.isAbsolute(relativeToRoot)) return null;
  return candidate;
}

function makeServer(label, outputRoot) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      let target;
      try { target = safePath(outputRoot, req.url || '/'); } catch (_) { target = null; }
      if (!target || !fs.existsSync(target) || !fs.statSync(target).isFile()) {
        res.statusCode = 404;
        res.setHeader('Content-Type', 'text/plain; charset=utf-8');
        res.end('not found');
        return;
      }
      res.statusCode = 200;
      res.setHeader('Content-Type', mimeFor(target));
      res.setHeader('Cache-Control', 'no-store');
      if (req.method === 'HEAD') { res.end(); return; }
      fs.createReadStream(target).on('error', () => {
        if (!res.headersSent) res.statusCode = 500;
        res.end();
      }).pipe(res);
    });
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      resolve({ label, outputRoot, server, port: address.port, origin: `http://127.0.0.1:${address.port}` });
    });
  });
}

function normalizeStack(value, origins) {
  let text = String(value || '');
  for (const origin of origins) text = text.split(origin).join('http://127.0.0.1:PORT');
  return text.replace(/\/v(?:32|33)\//g, '/vVERSION/');
}

function normalizeUrl(value, origins) {
  let text = String(value || '');
  for (const origin of origins) text = text.split(origin).join('http://127.0.0.1:PORT');
  return text;
}

function errorSignature(error, origins) {
  return `${String(error.message || '')}\n${normalizeStack(error.stack || '', origins)}`;
}

async function collectPage(context, version, serverInfo, pagePath, origins) {
  const page = await context.newPage();
  const pageErrors = [];
  const consoleErrors = [];
  const failedRequests = [];
  const navigationErrors = [];
  page.on('pageerror', error => {
    pageErrors.push({
      message: String(error.message || ''),
      stack: normalizeStack(error.stack || '', origins),
      url: normalizeUrl(page.url(), origins),
    });
  });
  page.on('console', message => {
    if (message.type() === 'error' || message.type() === 'warning') {
      consoleErrors.push({ type: message.type(), text: message.text(), location: message.location() });
    }
  });
  page.on('requestfailed', request => {
    failedRequests.push({
      url: normalizeUrl(request.url(), origins),
      method: request.method(),
      failure: request.failure() && request.failure().errorText,
    });
  });

  const targetUrl = `${serverInfo.origin}${BASE_PATH}${pagePath}`;
  let gotoStatus = 'ok';
  try {
    const response = await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 12000 });
    gotoStatus = response ? `http_${response.status()}` : 'no_response';
  } catch (error) {
    gotoStatus = 'error';
    navigationErrors.push(String(error && error.stack || error));
  }
  await page.waitForTimeout(700);

  let snapshot = null;
  try {
    snapshot = await page.evaluate(() => {
      const visible = element => {
        if (!element) return false;
        const style = getComputedStyle(element);
        const rect = element.getBoundingClientRect();
        return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0' && rect.width > 0 && rect.height > 0;
      };
      const attrs = element => ({
        tag: element.tagName,
        id: element.id || '',
        className: typeof element.className === 'string' ? element.className : '',
        href: element.getAttribute('href') || '',
        onmouseover: element.getAttribute('onmouseover') || '',
        onclick: element.getAttribute('onclick') || '',
        text: (element.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160),
      });
      const candidates = Array.from(document.querySelectorAll('[onmouseover], [onclick], [onmouseout], a, area'))
        .filter(element => {
          const text = [element.id, element.className, element.getAttribute('href'), element.getAttribute('onmouseover'), element.getAttribute('onclick')].join(' ');
          return /menu|Menu|showMenu|toggleMenu|worldpvp|battleground|wallpaper/i.test(text);
        });
      const menuNodes = Array.from(document.querySelectorAll('[id*="menu" i], [class*="menu" i], nav'));
      const scripts = Array.from(document.scripts).map(script => ({
        src: script.src || '',
        inline: !script.src,
        textLength: script.src ? 0 : (script.textContent || '').length,
      }));
      const bodyText = document.body ? (document.body.innerText || '') : '';
      return {
        title: document.title || '',
        bodyExists: !!document.body,
        bodyTextLength: bodyText.length,
        bodyTextSha256Input: bodyText,
        bodyVisible: !!document.body && visible(document.body),
        headingText: Array.from(document.querySelectorAll('h1,h2,h3')).filter(visible).slice(0, 8).map(element => (element.textContent || '').replace(/\s+/g, ' ').trim()),
        visibleMenuNodes: menuNodes.filter(visible).length,
        menuNodeCount: menuNodes.length,
        visibleNavNodes: Array.from(document.querySelectorAll('nav')).filter(visible).length,
        anchorCount: document.querySelectorAll('a').length,
        areaCount: document.querySelectorAll('area').length,
        imageCount: document.images.length,
        globalTypes: {
          Menu: typeof window.Menu,
          Menu2: typeof window.Menu2,
          Menu3: typeof window.Menu3,
          showMenu: typeof window.showMenu,
          toggleMenu: typeof window.toggleMenu,
        },
        candidates: candidates.slice(0, 12).map(attrs),
        scripts,
      };
    });
    snapshot.bodyTextSha256 = sha256(snapshot.bodyTextSha256Input || '');
    delete snapshot.bodyTextSha256Input;
  } catch (error) {
    snapshot = { evaluateError: String(error && error.stack || error) };
  }

  const probeResults = [];
  let legacyHandlerProbe = null;
  if (snapshot && Array.isArray(snapshot.candidates) && snapshot.candidates.length) {
    try {
      const rawProbes = await page.evaluate(() => {
        const elements = Array.from(document.querySelectorAll('[onmouseover], [onclick], [onmouseout], a, area'))
          .filter(element => {
            const text = [element.id, element.className, element.getAttribute('href'), element.getAttribute('onmouseover'), element.getAttribute('onclick')].join(' ');
            return /menu|Menu|showMenu|toggleMenu|worldpvp|battleground|wallpaper/i.test(text);
          }).slice(0, 12);
        return elements.map((element, index) => {
          const before = window.location.href;
          const result = { index, id: element.id || '', tag: element.tagName, before, dispatched: false, defaultPrevented: null };
          try {
            const event = new MouseEvent('mouseover', { bubbles: true, cancelable: true, view: window });
            result.defaultPrevented = !element.dispatchEvent(event);
            result.dispatched = true;
          } catch (error) {
            result.error = String(error && error.message || error);
          }
          result.after = window.location.href;
          return result;
        });
      });
      probeResults.push(...rawProbes);
      await page.waitForTimeout(250);
    } catch (error) {
      probeResults.push({ evaluateError: String(error && error.stack || error) });
    }
  }

  // The r1 browser run exercised legacy inline handlers indirectly while
  // walking image controls.  Dispatch the bounded handler set as a separate
  // probe so a load-only visit cannot incorrectly hide those old faults.  No
  // ordinary links are clicked: only hover/out handlers and the DIV menu
  // buttons whose inline action is explicitly toggleNewMenu are dispatched.
  try {
    legacyHandlerProbe = await page.evaluate(() => {
      const handlers = Array.from(document.querySelectorAll('[onmouseover], [onmouseout]')).slice(0, 240);
      let over = 0, out = 0, handlerErrors = [];
      for (const element of handlers) {
        try { element.dispatchEvent(new MouseEvent('mouseover', { bubbles: true, cancelable: true, view: window })); over++; } catch (error) { handlerErrors.push(String(error && error.message || error)); }
        try { element.dispatchEvent(new MouseEvent('mouseout', { bubbles: true, cancelable: true, view: window })); out++; } catch (error) { handlerErrors.push(String(error && error.message || error)); }
      }
      const menuButtons = Array.from(document.querySelectorAll('[onclick*="toggleNewMenu"]')).slice(0, 12);
      let menuClicks = 0;
      for (const element of menuButtons) {
        try { element.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window })); menuClicks++; } catch (error) { handlerErrors.push(String(error && error.message || error)); }
      }
      return { handlerCount: handlers.length, over, out, menuButtonCount: menuButtons.length, menuClicks, handlerErrors };
    });
    await page.waitForTimeout(500);
  } catch (error) {
    legacyHandlerProbe = { evaluateError: String(error && error.stack || error) };
  }

  let postProbeUrl = normalizeUrl(page.url(), origins);
  let scriptUrls = [];
  if (snapshot && Array.isArray(snapshot.scripts)) {
    scriptUrls = snapshot.scripts.filter(item => item.src).map(item => normalizeUrl(item.src, origins));
  }
  const scriptPathSet = Array.from(new Set(scriptUrls.map(value => {
    try { return new URL(value).pathname; } catch (_) { return value; }
  }))).sort();
  const stackScriptPaths = Array.from(new Set(pageErrors.flatMap(error => {
    const matches = error.stack.match(/(?:https?:\/\/[^\s)]+|\/[^\s)]+):(\d+):(\d+)/g) || [];
    return matches.map(value => value.replace(/:\d+:\d+$/, '').replace(/^https?:\/\/[^/]+/, ''));
  }))).sort();

  await page.close();
  return {
    version,
    page: pagePath,
    targetUrl,
    gotoStatus,
    navigationErrors,
    pageErrors,
    pageErrorSignatures: pageErrors.map(error => errorSignature(error, origins)),
    consoleErrors,
    failedRequests,
    postProbeUrl,
    scripts: scriptUrls,
    scriptPathSet,
    stackScriptPaths,
    snapshot,
    menuProbe: { candidates: probeResults, legacyHandlers: legacyHandlerProbe },
    bodyUsable: !!(snapshot && snapshot.bodyExists && snapshot.bodyVisible && snapshot.bodyTextLength > 0),
    menuDomAvailable: !!(snapshot && snapshot.visibleMenuNodes > 0),
    menuProbeDispatched: probeResults.filter(item => item.dispatched).length,
  };
}

function comparePage(v32, v33) {
  const v32Errors = new Set(v32.pageErrorSignatures);
  const v33Errors = new Set(v33.pageErrorSignatures);
  const v32Scripts = new Set(v32.scriptPathSet);
  const v33Scripts = new Set(v33.scriptPathSet);
  return {
    page_error_signatures_identical: v32Errors.size === v33Errors.size && [...v32Errors].every(value => v33Errors.has(value)),
    page_error_count: { v32: v32.pageErrors.length, v33: v33.pageErrors.length },
    script_path_sets_identical: v32Scripts.size === v33Scripts.size && [...v32Scripts].every(value => v33Scripts.has(value)),
    scripts_only_v32: [...v32Scripts].filter(value => !v33Scripts.has(value)).sort(),
    scripts_only_v33: [...v33Scripts].filter(value => !v32Scripts.has(value)).sort(),
    body_text_sha256_identical: v32.snapshot && v33.snapshot && v32.snapshot.bodyTextSha256 === v33.snapshot.bodyTextSha256,
    body_usable_same: v32.bodyUsable === v33.bodyUsable,
    menu_globals_same: JSON.stringify(v32.snapshot && v32.snapshot.globalTypes) === JSON.stringify(v33.snapshot && v33.snapshot.globalTypes),
    menu_dom_available: { v32: v32.menuDomAvailable, v33: v33.menuDomAvailable },
    errors_same_legacy_signature: v32Errors.size > 0 && v32Errors.size === v33Errors.size && [...v32Errors].every(value => v33Errors.has(value)),
  };
}

async function main() {
  for (const [label, output] of Object.entries(OUTPUTS)) {
    if (!fs.existsSync(output)) throw new Error(`missing frozen ${label} output: ${output}`);
    for (const page of PAGES) {
      if (!fs.existsSync(path.join(output, page))) throw new Error(`missing ${label} page: ${page}`);
    }
  }
  fs.mkdirSync(path.dirname(RESULT), { recursive: true });
  const servers = [];
  const externalRequests = [];
  const localPorts = new Set();
  let browser;
  try {
    servers.push(await makeServer('v32', OUTPUTS.v32));
    servers.push(await makeServer('v33', OUTPUTS.v33));
    for (const server of servers) localPorts.add(String(server.port));
    const origins = servers.map(server => server.origin);
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ serviceWorkers: 'block' });
    await context.route('**/*', async route => {
      const requestUrl = new URL(route.request().url());
      const local = requestUrl.hostname === '127.0.0.1' && localPorts.has(requestUrl.port);
      if (local) return route.continue();
      externalRequests.push({ url: route.request().url(), method: route.request().method(), resourceType: route.request().resourceType() });
      return route.abort();
    });
    const pages = {};
    for (const pagePath of PAGES) {
      const versionResults = {};
      for (const server of servers) {
        versionResults[server.label] = await collectPage(context, server.label, server, pagePath, origins);
      }
      pages[pagePath] = {
        v32: versionResults.v32,
        v33: versionResults.v33,
        comparison: comparePage(versionResults.v32, versionResults.v33),
      };
    }
    await context.close();
    const result = {
      schema: 'legacy-menu-baseline-diagnostic-v1',
      checked_utc: new Date().toISOString(),
      method: {
        browser: 'Playwright Chromium headless',
        servers: servers.map(server => ({ version: server.label, origin: server.origin, output_root: path.relative(ROOT, server.outputRoot).replace(/\\/g, '/') })),
        pages: PAGES,
        external_requests_intercepted: externalRequests.length,
        menu_probe: 'DOM visibility and bounded mouseover dispatch on menu-like anchors/areas; no navigation or source mutation',
        interpretation: 'An equal error signature and script path set across v32/v33 is evidence that a legacy runtime fault predates the v33 image-link changes; it is not a proof that every browser behavior is historically identical.',
      },
      external_requests: externalRequests,
      pages,
    };
    fs.writeFileSync(RESULT, JSON.stringify(result, null, 2) + '\n', 'utf8');
    console.log(JSON.stringify({ result: path.relative(ROOT, RESULT).replace(/\\/g, '/'), external_requests: externalRequests.length, pages: PAGES.length, versions: 2 }, null, 2));
  } finally {
    if (browser) await browser.close().catch(() => {});
    await Promise.all(servers.map(server => new Promise(resolve => server.server.close(() => resolve()))));
  }
}

main().catch(error => {
  console.error(error && error.stack || error);
  process.exitCode = 1;
});

