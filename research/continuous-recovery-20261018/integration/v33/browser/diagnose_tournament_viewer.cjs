/* Read-only v32/v33 tournament screenie viewer probe. */
const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { URL } = require('url');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../../..');
const BASE = '/WOW-Encyclopedia-Deployable-Archive/';
const PAGE = 'pvp/tournament/index.xml.html';
const OUTPUTS = { v32: path.join(ROOT, '.scratch/pages-resources-20261018-v32'), v33: path.join(ROOT, '.scratch/pages-resources-20261018-v33') };
const RESULT = path.join(ROOT, 'research/continuous-recovery-20261018/integration/v33/browser/results/tournament-viewer-baseline.json');
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const mime = file => ({'.html':'text/html; charset=utf-8','.xml':'application/xml; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.gif':'image/gif','.svg':'image/svg+xml'}[path.extname(file).toLowerCase()] || 'application/octet-stream');

function safeFile(root, requestUrl) {
  const raw = decodeURIComponent(String(requestUrl).split('?', 1)[0].split('#', 1)[0]);
  if (!raw.startsWith(BASE)) return null;
  const candidate = path.resolve(root, raw.slice(BASE.length));
  const rel = path.relative(path.resolve(root), candidate);
  return rel.startsWith('..') || path.isAbsolute(rel) ? null : candidate;
}
function serve(label, outputRoot) {
  return new Promise((resolve, reject) => {
    const server = http.createServer((req, res) => {
      let file = null;
      try { file = safeFile(outputRoot, req.url); } catch (_) {}
      if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end('not found'); }
      res.writeHead(200, {'content-type': mime(file), 'cache-control': 'no-store'});
      if (req.method === 'HEAD') return res.end();
      fs.createReadStream(file).pipe(res);
    });
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => { const a = server.address(); resolve({label, outputRoot, server, origin: `http://127.0.0.1:${a.port}`, port: String(a.port)}); });
  });
}
function norm(value, origins) {
  let text = String(value || '');
  for (const origin of origins) text = text.split(origin).join('http://127.0.0.1:PORT');
  return text;
}
function viewerSnapshot() {
  const visible = element => { const s = getComputedStyle(element); const r = element.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0 && r.width > 0 && r.height > 0; };
  const nodes = Array.from(document.querySelectorAll('[id*="screenie" i],[class*="screenie" i],[id*="lightbox" i],[class*="lightbox" i],[id*="overlay" i],[class*="overlay" i]'));
  const describe = element => ({tag: element.tagName, id: element.id || '', className: typeof element.className === 'string' ? element.className : '', visible: visible(element), text: (element.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 160), html: element.outerHTML.slice(0, 600)});
  const nodeImages = nodes.flatMap(node => Array.from(node.querySelectorAll('img')));
  const targetImages = Array.from(document.images).filter(image => (image.src || '').toLowerCase().includes('ss5') || nodeImages.includes(image));
  return {
    jquery: {type: typeof window.jQuery, version: window.jQuery && window.jQuery.fn ? window.jQuery.fn.jquery : null, colorbox: window.jQuery && window.jQuery.fn ? typeof window.jQuery.fn.colorbox : null, lightbox: window.jQuery && window.jQuery.fn ? typeof window.jQuery.fn.lightBox : null},
    nodes: nodes.slice(0, 20).map(describe),
    backgrounds: nodes.slice(0, 20).map(element => ({id: element.id || '', backgroundImage: getComputedStyle(element).backgroundImage, visible: visible(element), width: element.getBoundingClientRect().width, height: element.getBoundingClientRect().height})),
    images: targetImages.map(image => ({src: image.src, complete: image.complete, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight, visible: visible(image)})),
    bodyTextLength: document.body ? (document.body.innerText || '').length : 0,
    bodyTextSha256Input: document.body ? (document.body.innerText || '') : '',
  };
}
async function backgroundLoadProbe(page) {
  return page.evaluate(async () => {
    const nodes = Array.from(document.querySelectorAll('[id*="screenie" i],[class*="screenie" i],[id*="lightbox" i],[class*="lightbox" i],[id*="overlay" i],[class*="overlay" i]'));
    const entries = nodes.map(element => ({id: element.id || '', backgroundImage: getComputedStyle(element).backgroundImage})).flatMap(entry => {
      const match = String(entry.backgroundImage || '').match(/url\(["']?(.*?)["']?\)/i);
      return match ? [{...entry, url: match[1]}] : [];
    });
    return Promise.all(entries.map(entry => new Promise(resolve => {
      const image = new Image(); let done = false;
      const finish = status => { if (done) return; done = true; resolve({...entry, status, naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight, complete: image.complete}); };
      image.onload = () => finish('loaded'); image.onerror = () => finish('error'); image.src = entry.url;
      setTimeout(() => finish('timeout'), 1500);
    })));
  });
}
async function one(context, info, origins) {
  const page = await context.newPage();
  const pageErrors = [], failed = [], consoleErrors = [];
  page.on('pageerror', error => pageErrors.push({message: String(error.message || ''), stack: norm(error.stack || '', origins), url: norm(page.url(), origins)}));
  page.on('console', message => { if (message.type() === 'error' || message.type() === 'warning') consoleErrors.push({type: message.type(), text: message.text(), location: message.location()}); });
  page.on('requestfailed', request => failed.push({url: norm(request.url(), origins), failure: request.failure() && request.failure().errorText}));
  const target = `${info.origin}${BASE}${PAGE}`;
  let gotoStatus = 'no_response', navigationError = null;
  try { const response = await page.goto(target, {waitUntil: 'domcontentloaded', timeout: 12000}); gotoStatus = response ? `http_${response.status()}` : 'no_response'; } catch (error) { navigationError = String(error && error.stack || error); }
  await page.waitForTimeout(700);
  let before = null, click = null, after = null;
  try { before = await page.evaluate(viewerSnapshot); } catch (error) { before = {evaluateError: String(error && error.stack || error)}; }
  if (before && !before.evaluateError) before.backgroundLoads = await backgroundLoadProbe(page);
  const scripts = await page.evaluate(() => Array.from(document.scripts).filter(script => script.src).map(script => script.src));
  let control = page.locator('a[rel="screenie"]').filter({has: page.locator('[src*="ss5"]')});
  let matchedCount = await control.count();
  if (!matchedCount) {
    const all = await page.locator('a[rel="screenie"]').evaluateAll(elements => elements.map((element, index) => ({index, href: element.getAttribute('href') || '', html: element.outerHTML.slice(0, 600)})));
    const index = all.findIndex(item => /ss5\.jpg/i.test(item.href) || /ss5\.jpg/i.test(item.html));
    if (index >= 0) { matchedCount = 1; control = page.locator('a[rel="screenie"]').nth(index); }
  }
  if (matchedCount) {
    try { await control.first().click({force: true}); click = {ok: true, count: matchedCount}; } catch (error) { click = {ok: false, count: matchedCount, error: String(error && error.stack || error)}; }
  } else click = {ok: false, count: 0, error: 'ss5 screenie control not found'};
  await page.waitForTimeout(900);
  try { after = await page.evaluate(viewerSnapshot); } catch (error) { after = {evaluateError: String(error && error.stack || error)}; }
  if (after && !after.evaluateError) after.backgroundLoads = await backgroundLoadProbe(page);
  const scriptRecords = scripts.map(src => {
    try {
      const parsed = new URL(src); const rel = parsed.pathname.split(BASE).pop(); const file = path.join(info.outputRoot, rel); return {url: norm(src, origins), path: rel, sha256: fs.existsSync(file) ? sha256(fs.readFileSync(file)) : null, bytes: fs.existsSync(file) ? fs.statSync(file).size : null};
    } catch (_) { return {url: norm(src, origins), path: null, sha256: null, bytes: null}; }
  });
  await page.close();
  for (const snapshot of [before, after]) if (snapshot && snapshot.bodyTextSha256Input !== undefined) { snapshot.bodyTextSha256 = sha256(snapshot.bodyTextSha256Input); delete snapshot.bodyTextSha256Input; }
  return {version: info.label, page: PAGE, target: norm(target, origins), gotoStatus, navigationError, control: click, pageErrors, consoleErrors, failedRequests: failed, afterUrl: norm(page.url(), origins), scriptRecords, before, after};
}
async function main() {
  for (const output of Object.values(OUTPUTS)) if (!fs.existsSync(path.join(output, PAGE))) throw new Error(`missing ${PAGE} in ${output}`);
  const servers = [], external = []; let browser;
  try {
    servers.push(await serve('v32', OUTPUTS.v32), await serve('v33', OUTPUTS.v33));
    const origins = servers.map(server => server.origin), ports = new Set(servers.map(server => server.port));
    browser = await chromium.launch({headless: true}); const context = await browser.newContext({serviceWorkers: 'block'});
    await context.route('**/*', route => { const u = new URL(route.request().url()); if (u.hostname === '127.0.0.1' && ports.has(u.port)) return route.continue(); external.push({url: route.request().url(), resourceType: route.request().resourceType()}); return route.abort(); });
    const rows = {}; for (const server of servers) rows[server.label] = await one(context, server, origins);
    await context.close();
    const result = {schema: 'tournament-viewer-baseline-v1', checked_utc: new Date().toISOString(), page: PAGE, method: {browser: 'Playwright Chromium headless', local_only: true, click: 'one a[rel="screenie"] control targeting ss5.jpg', external_requests_intercepted: external.length}, external_requests: external, versions: rows, comparison: {page_error_signatures_identical: JSON.stringify(rows.v32.pageErrors.map(error => [error.message, error.stack])) === JSON.stringify(rows.v33.pageErrors.map(error => [error.message, error.stack])), script_records_identical: JSON.stringify(rows.v32.scriptRecords.map(record => [record.path, record.sha256, record.bytes])) === JSON.stringify(rows.v33.scriptRecords.map(record => [record.path, record.sha256, record.bytes])), body_visible: {v32: !!(rows.v32.after && rows.v32.after.bodyTextLength > 0), v33: !!(rows.v33.after && rows.v33.after.bodyTextLength > 0)}, after_viewer_images: {v32: rows.v32.after && rows.v32.after.images, v33: rows.v33.after && rows.v33.after.images}}};
    fs.mkdirSync(path.dirname(RESULT), {recursive: true}); fs.writeFileSync(RESULT, JSON.stringify(result, null, 2) + '\n', 'utf8'); console.log(JSON.stringify({result, sha256: sha256(fs.readFileSync(RESULT))}, null, 2));
  } finally { if (browser) await browser.close().catch(() => {}); await Promise.all(servers.map(server => new Promise(resolve => server.server.close(() => resolve())))); }
}
main().catch(error => { console.error(error && error.stack || error); process.exitCode = 1; });

