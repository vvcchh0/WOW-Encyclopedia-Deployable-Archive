const fs = require('fs');
const path = require('path');
const http = require('http');
const { URL } = require('url');
const crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../..');
const OUTPUT = path.join(ROOT, '.scratch/pages-resources-20261018-v33');
const BASE_PATH = '/WOW-Encyclopedia-Deployable-Archive/';
const RESULT = path.join(__dirname, 'results', 'visibility-collectors.json');

function sha256(data) { return crypto.createHash('sha256').update(data).digest('hex'); }
function mime(file) { const ext = path.extname(file).toLowerCase(); return ({ '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.jpg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.svg': 'image/svg+xml' })[ext] || 'application/octet-stream'; }

async function main() {
  let server, browser, context;
  const result = { schema: 'wow-recovery.local-audit.v33-visibility-diagnostic.v1', page: 'news/wow-news2004.html', needle: 'shared/wow-com/images/advertising/04-09/collectors.jpg', external_requests: [], request_failures: [], page_errors: [] };
  try {
    server = http.createServer((req, res) => {
      try {
        const url = new URL(req.url || '/', 'http://127.0.0.1');
        if (!url.pathname.startsWith(BASE_PATH)) throw new Error('route');
        const relative = decodeURIComponent(url.pathname.slice(BASE_PATH.length));
        if (!relative || relative.includes('..') || relative.includes('\\')) throw new Error('unsafe');
        const file = path.resolve(OUTPUT, relative);
        if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end(); }
        res.writeHead(200, { 'content-type': mime(file), 'cache-control': 'no-store' });
        fs.createReadStream(file).pipe(res);
      } catch (_) { res.writeHead(400); res.end(); }
    });
    await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
    const address = server.address();
    const base = `http://127.0.0.1:${address.port}${BASE_PATH}`;
    browser = await chromium.launch({ headless: true });
    context = await browser.newContext({ viewport: { width: 1550, height: 1100 } });
    await context.route('**/*', route => {
      if (route.request().url().startsWith(base)) return route.continue();
      result.external_requests.push(route.request().url());
      return route.abort();
    });
    context.on('requestfailed', request => { if (!request.url().startsWith(base)) result.request_failures.push({ url: request.url(), failure: request.failure() }); });
    const page = await context.newPage();
    page.on('pageerror', error => result.page_errors.push({ url: page.url(), message: String(error), stack: String(error.stack || '') }));
    const response = await page.goto(`${base}news/wow-news2004.html`, { waitUntil: 'networkidle' });
    result.status = response && response.status();
    result.url = page.url();
    result.dom = await page.locator('a[href]').evaluateAll(elements => {
      const matches = elements.filter(element => (element.getAttribute('href') || '').includes('shared/wow-com/images/advertising/04-09/collectors.jpg'));
      return matches.map(element => {
        const chain = [];
        for (let current = element; current && chain.length < 8; current = current.parentElement) {
          const style = getComputedStyle(current), rect = current.getBoundingClientRect();
          chain.push({ tag: current.tagName, id: current.id || '', className: String(current.className || ''), inline: current.getAttribute('style') || '', display: style.display, visibility: style.visibility, opacity: style.opacity, width: rect.width, height: rect.height, text: (current.textContent || '').trim().slice(0, 120) });
        }
        const image = element.querySelector('img');
        const imageStyle = image ? getComputedStyle(image) : null;
        const imageRect = image ? image.getBoundingClientRect() : null;
        return { href: element.getAttribute('href'), visible: (() => { const style = getComputedStyle(element), rect = element.getBoundingClientRect(); return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0; })(), chain, image: image ? { src: image.getAttribute('src'), complete: image.complete, natural: [image.naturalWidth, image.naturalHeight], display: imageStyle.display, visibility: imageStyle.visibility, width: imageRect.width, height: imageRect.height } : null };
      });
    });
    result.native_controls = await page.locator('[onclick]').evaluateAll(elements => elements.filter(element => String(element.getAttribute('onclick') || '').includes('toggle')).slice(0, 20).map(element => { const s=getComputedStyle(element),r=element.getBoundingClientRect(); return { tag:element.tagName,id:element.id||'',className:String(element.className||''),onclick:element.getAttribute('onclick'),text:(element.textContent||'').trim().slice(0,80),display:s.display,visibility:s.visibility,width:r.width,height:r.height }; }));
    result.page_text_context = await page.locator('body').innerText();
    result.accepted = result.status === 200 && result.dom.length > 0 && result.external_requests.length === 0 && result.request_failures.length === 0;
  } catch (error) { result.accepted = false; result.error = String(error && error.stack || error); }
  finally {
    if (context) await context.close().catch(() => {});
    if (browser) await browser.close().catch(() => {});
    if (server) await new Promise(resolve => server.close(resolve));
    fs.mkdirSync(path.dirname(RESULT), { recursive: true });
    fs.writeFileSync(RESULT, JSON.stringify(result, null, 2) + '\n', 'utf8');
    console.log(JSON.stringify({ result: RESULT, sha256: sha256(fs.readFileSync(RESULT)), accepted: result.accepted, matches: result.dom ? result.dom.length : 0, external: result.external_requests ? result.external_requests.length : 0, errors: result.page_errors ? result.page_errors.length : 0 }, null, 2));
  }
}
main();
