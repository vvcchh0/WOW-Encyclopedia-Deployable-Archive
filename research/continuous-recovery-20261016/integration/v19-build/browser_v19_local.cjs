const fs = require('fs');
const path = require('path');
const http = require('http');
const crypto = require('crypto');
const { chromium } = require('playwright');

const repo = path.resolve(__dirname, '../../../..');
const outputRoot = path.join(repo, '.scratch', 'pages-resources-20261016-v19');
const basePath = '/WOW-Encyclopedia-Deployable-Archive';
const host = '127.0.0.1';
const port = 29019;
const outputPath = path.join(__dirname, 'browser-v19-local.json');

const targets = [
  {
    page: 'news/rss-08-2006.xml.html',
    label: 'old-month-w',
    routes: ['/new-hp/images/smallcaps/w.gif'],
  },
  {
    page: 'news/rss-10-2006.xml.html',
    label: 'old-month-i-p',
    routes: ['/new-hp/images/smallcaps/i.gif', '/new-hp/images/smallcaps/p.gif'],
  },
  {
    page: 'news/rss-08-2007.xml.html',
    label: 'august-shop-wrath',
    routes: ['/new-hp/images/icons/news-shop.gif', '/new-hp/images/icons/news-wrath.gif'],
  },
  {
    page: 'news/rss-05-2007.xml.html',
    label: 'news-community-sc2',
    routes: ['/new-hp/images/icons/news-community.gif', '/new-hp/images/news-sc2.jpg'],
  },
  {
    page: 'news/wow-news-06-2005.html',
    label: 'blizzcon',
    routes: ['/news/images/05-06/blizzconlogo.jpg'],
  },
];

const expectedFiles = new Map([
  ['/new-hp/images/smallcaps/w.gif', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/01-w.gif'],
  ['/new-hp/images/smallcaps/i.gif', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/02-i.gif'],
  ['/new-hp/images/smallcaps/p.gif', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/03-p.gif'],
  ['/news/images/05-06/blizzconlogo.jpg', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/04-blizzconlogo.jpg'],
  ['/new-hp/images/icons/news-community.gif', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/05-news-community.gif'],
  ['/new-hp/images/icons/news-alert.gif', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/06-news-alert.gif'],
  ['/new-hp/images/icons/news-shop.gif', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/07-news-shop.gif'],
  ['/new-hp/images/icons/news-wrath.gif', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/08-news-wrath.gif'],
  ['/new-hp/images/icons/news-realms.gif', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/09-news-realms.gif'],
  ['/new-hp/images/news-sc2.jpg', 'research/continuous-recovery-20261016/integration/accepted-images/news-v19/10-news-sc2.jpg'],
]);

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function servePath(urlPath) {
  if (!urlPath.startsWith(basePath)) return null;
  let relative = decodeURIComponent(urlPath.slice(basePath.length)).replace(/^\/+/, '');
  if (!relative || relative.includes('..')) return null;
  const file = path.resolve(outputRoot, relative);
  if (!file.startsWith(path.resolve(outputRoot) + path.sep)) return null;
  return file;
}

function contentType(file) {
  const ext = path.extname(file).toLowerCase();
  return ({ '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.xml': 'application/xml', '.svg': 'image/svg+xml', '.gif': 'image/gif', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.woff': 'font/woff', '.woff2': 'font/woff2' })[ext] || 'application/octet-stream';
}

async function main() {
  const requests = [];
  const server = http.createServer((req, res) => {
    const file = servePath(new URL(req.url, `http://${host}:${port}`).pathname);
    if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
      res.statusCode = 404;
      res.end('not found');
      return;
    }
    res.statusCode = 200;
    res.setHeader('Content-Type', contentType(file));
    fs.createReadStream(file).pipe(res);
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(port, host, resolve);
  });

  let browser;
  let result;
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    await context.route('**/*', async route => {
      const url = new URL(route.request().url());
      if (url.hostname !== host || String(url.port) !== String(port)) {
        requests.push({ url: route.request().url(), blocked: true, resourceType: route.request().resourceType() });
        await route.abort();
      } else {
        requests.push({ url: route.request().url(), blocked: false, resourceType: route.request().resourceType() });
        await route.continue();
      }
    });
    const page = await context.newPage();
    const pageResults = [];
    for (const spec of targets) {
      const url = `http://${host}:${port}${basePath}/${spec.page}`;
      const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(250);
      const expected = await page.evaluate((routes) => routes.map(route => {
        const candidates = Array.from(document.images).filter(img => {
          try { return new URL(img.currentSrc || img.src, document.baseURI).pathname.endsWith(route); } catch { return false; }
        });
        return {
          route,
          count: candidates.length,
          complete: candidates.map(img => img.complete),
          natural: candidates.map(img => [img.naturalWidth, img.naturalHeight]),
          currentSrc: candidates.map(img => img.currentSrc || img.src),
        };
      }), spec.routes);
      const direct = [];
      for (const route of spec.routes) {
        const fetched = await page.evaluate(async ({ route, basePath }) => {
          const response = await fetch(`${location.origin}${basePath}${route}`, { cache: 'no-store' });
          const body = await response.arrayBuffer();
          return { status: response.status, bytes: body.byteLength, contentType: response.headers.get('content-type') };
        }, { route, basePath });
        const rel = expectedFiles.get(route);
        const local = path.join(repo, rel);
        const bytes = fs.readFileSync(local);
        direct.push({ route, ...fetched, local_sha256: sha256(bytes), local_bytes: bytes.length, local_path: rel });
      }
      pageResults.push({ label: spec.label, page: spec.page, status: response ? response.status() : null, expected, direct });
    }
    const blockedExternal = requests.filter(item => item.blocked);
    const checks = [];
    for (const item of pageResults) {
      for (const target of item.expected) {
        checks.push({ page: item.page, route: target.route, present: target.count > 0, loaded: target.count > 0 && target.complete.every(Boolean) && target.natural.every(dim => dim[0] > 0 && dim[1] > 0) });
      }
      for (const fetched of item.direct) {
        checks.push({ page: item.page, route: fetched.route, status_200: fetched.status === 200, bytes_match: fetched.bytes === fetched.local_bytes });
      }
    }
    result = {
      schema: 'v19_local_browser_acceptance_v1',
      checked_utc: new Date().toISOString(),
      accepted: blockedExternal.length === 0 && checks.every(check => Object.values(check).slice(2).every(Boolean)),
      server: { host, port, output: '.scratch/pages-resources-20261016-v19' },
      external_requests_blocked: blockedExternal.length,
      requests_total: requests.length,
      pages: pageResults,
      checks,
    };
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
  if (fs.existsSync(outputPath)) throw new Error(`refusing overwrite ${outputPath}`);
  fs.writeFileSync(outputPath, `${JSON.stringify(result, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify({ output: path.relative(repo, outputPath), accepted: result.accepted, pages: result.pages.length, checks: result.checks.length, blocked_external: result.external_requests_blocked, requests: result.requests_total }, null, 2));
  if (!result.accepted) process.exitCode = 2;
}

main().catch(error => { console.error(error.stack || error); process.exitCode = 1; });
