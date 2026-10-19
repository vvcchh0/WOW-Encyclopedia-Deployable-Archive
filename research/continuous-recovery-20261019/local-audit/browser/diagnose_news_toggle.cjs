const fs = require('fs');
const http = require('http');
const path = require('path');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../..');
const OUTPUT = path.join(ROOT, '.scratch/pages-resources-20261018-v33');
const PREFIX = '/WOW-Encyclopedia-Deployable-Archive/';
const PAGE_PATH = 'news/rss-08-2007.xml.html';
const IDS = ['news8-22-07-697', 'news8-20-07-982'];
const TARGETS = ['news/images/07-08/wow-bc.jpg', 'news/images/07-08/tcg02.jpg'];

function serve(root) {
  return http.createServer((req, res) => {
    if (!req.url.startsWith(PREFIX)) { res.writeHead(404); return res.end(); }
    const rel = decodeURIComponent(req.url.slice(PREFIX.length).split('?')[0]);
    const file = path.resolve(root, rel);
    if (file !== root && !file.startsWith(root + path.sep)) { res.writeHead(400); return res.end(); }
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end(); }
    const mime = file.endsWith('.html') ? 'text/html' : file.endsWith('.js') ? 'text/javascript' : file.endsWith('.jpg') ? 'image/jpeg' : 'image/gif';
    res.writeHead(200, { 'content-type': mime });
    fs.createReadStream(file).pipe(res);
  });
}

(async () => {
  const server = serve(OUTPUT); await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const port = server.address().port;
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  const log = { url: null, errors: [], requests: [], ids: [], anchors: [], transitions: [] };
  page.on('pageerror', e => log.errors.push({ message: String(e), stack: String(e.stack || '') }));
  page.on('request', req => { if (!req.url().startsWith(`http://127.0.0.1:${port}/`)) { req.abort().catch(() => {}); log.requests.push(req.url()); } });
  page.on('framenavigated', frame => { if (frame === page.mainFrame()) log.transitions.push(page.url()); });
  const base = `http://127.0.0.1:${port}${PREFIX}`;
  await page.goto(`${base}${PAGE_PATH}`, { waitUntil: 'networkidle' });
  log.url = page.url();
  for (const id of IDS) {
    const entry = page.locator(`#${id}`);
    log.ids.push({ id, before: await entry.evaluate(e => ({ className: e.className, display: getComputedStyle(e).display, box: [e.getBoundingClientRect().width, e.getBoundingClientRect().height] })) });
    const parent = entry.locator('.hoverContainer').first();
    await parent.click({ noWaitAfter: true });
    await page.waitForFunction(expected => { const e = document.getElementById(expected); return e && [...e.classList].some(c => c.startsWith('news-expand')) && ![...e.classList].some(c => c.startsWith('news-collapse')); }, id);
    log.ids[log.ids.length - 1].after = await entry.evaluate(e => ({ className: e.className, display: getComputedStyle(e).display, box: [e.getBoundingClientRect().width, e.getBoundingClientRect().height] }));
  }
  for (const target of TARGETS) {
    const anchor = page.locator(`a[href*="${target}"]`).first();
    log.anchors.push({ target, count: await anchor.count(), before: await anchor.evaluate(e => ({ href: e.href, outer: e.outerHTML, box: [e.getBoundingClientRect().width, e.getBoundingClientRect().height] })) });
    const before = page.url();
    const popup = context.waitForEvent('page', { timeout: 2500 }).catch(() => null);
    await anchor.click({ noWaitAfter: true });
    await page.waitForTimeout(1000);
    const opened = await popup;
    log.anchors[log.anchors.length - 1].after = { page: page.url(), before, popup: opened ? opened.url() : null, imageFacts: await page.locator('img').evaluateAll((els, needle) => els.filter(e => (e.src || '').includes(needle)).map(e => ({ src: e.src, natural: [e.naturalWidth, e.naturalHeight], box: [e.getBoundingClientRect().width, e.getBoundingClientRect().height] })), target), screenie: await page.locator('#Screenie,#Screenie2,#redBlock').evaluateAll(els => els.map(e => ({ id: e.id, className: e.className, style: e.getAttribute('style'), html: e.outerHTML.slice(0, 2000), box: [e.getBoundingClientRect().width, e.getBoundingClientRect().height] }))) };
    const close = page.locator('#Screenie2,[title="Close"]');
    if (await close.count() && await close.first().isVisible()) await close.first().click({ force: true }).catch(() => {});
    if (opened) await opened.close().catch(() => {});
    if (page.url() !== before) { await page.goto(`${base}${PAGE_PATH}`, { waitUntil: 'networkidle' }); for (const id of IDS) { const entry = page.locator(`#${id}`); if (await entry.evaluate(e => [...e.classList].some(c => c.startsWith('news-collapse')))) { await entry.locator('.hoverContainer').first().click({ noWaitAfter: true }); await page.waitForFunction(expected => { const e = document.getElementById(expected); return e && [...e.classList].some(c => c.startsWith('news-expand')) && ![...e.classList].some(c => c.startsWith('news-collapse')); }, id); } } }
  }
  console.log(JSON.stringify(log, null, 2));
  await context.close(); await browser.close(); await new Promise(resolve => server.close(resolve));
})().catch(error => { console.error(error.stack || error); process.exitCode = 1; });
