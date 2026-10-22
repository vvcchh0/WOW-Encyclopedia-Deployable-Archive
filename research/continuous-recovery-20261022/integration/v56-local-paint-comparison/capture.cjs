'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const root = process.cwd();
const evidenceRoot = path.join(root, 'research/continuous-recovery-20261022/integration/v56-local-paint-comparison');
const browserReceiptPath = path.join(root, 'research/continuous-recovery-20261022/integration/related-talent-icons-v56/implementation/runs/v56-2026-10-22T12-42-28-056Z/browser-check.json');
const sourceBytes = fs.readFileSync(browserReceiptPath);
const source = JSON.parse(sourceBytes.toString('utf8'));
const chromePath = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const ids = ['warrior-improved-thunder-clap', 'warrior-improved-slam'];
const portPairs = [
  { version: 'v55', port: '24785' },
  { version: 'v56', port: '24786' },
];
const points = [[1100, 600], [700, 650], [400, 780], [1100, 850]];
const report = {
  schema: 'wow-v56-local-paint-comparison/v1',
  source_browser_sha256: crypto.createHash('sha256').update(sourceBytes).digest('hex'),
  chrome_binary: chromePath,
  launch_mode: 'headless Chrome, one new browser process per page, default GPU settings',
  viewport: { width: 1480, height: 1250, deviceScaleFactor: 1 },
  wait_policy: 'networkidle, document.fonts.ready, two animation frames, then 1500ms',
  response_policy: 'same-origin loopback only; all other HTTP(S) origins aborted; no fulfill/substitution',
  response_substitutions: 0,
  external_requests_aborted: [],
  page_errors: [],
  checks: [],
};

async function snapshot(page, targetPath) {
  return page.evaluate(({ routePath, fixedPoints }) => {
    const styleOf = (node) => {
      const s = getComputedStyle(node);
      return {
        display: s.display, visibility: s.visibility, opacity: s.opacity,
        position: s.position, zIndex: s.zIndex, width: s.width, height: s.height,
        color: s.color, backgroundColor: s.backgroundColor, border: s.border,
        overflow: s.overflow, filter: s.filter, transform: s.transform,
        mixBlendMode: s.mixBlendMode, clipPath: s.clipPath,
      };
    };
    const rectOf = (node) => {
      const r = node.getBoundingClientRect();
      return { x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom };
    };
    const imageNodes = Array.from(document.images);
    const images = imageNodes.map((img) => {
      const rect = rectOf(img);
      const style = styleOf(img);
      const visible = style.display !== 'none' && style.visibility !== 'hidden'
        && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0
        && rect.right > 0 && rect.bottom > 0 && rect.x < innerWidth && rect.y < innerHeight;
      return {
        srcAttribute: img.getAttribute('src'), src: img.src, currentSrc: img.currentSrc,
        complete: img.complete, naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight,
        alt: img.alt, visible, style, rect,
      };
    });
    const targetImages = imageNodes.filter((img) => {
      try { return new URL(img.currentSrc || img.src, location.href).pathname === routePath; }
      catch (_) { return false; }
    });
    const targetDetails = targetImages.map((img) => {
      const chain = [];
      let node = img;
      for (let i = 0; node && i < 5; i += 1, node = node.parentElement) {
        chain.push({
          tag: node.tagName, id: node.id || null,
          className: typeof node.className === 'string' ? node.className : null,
          style: styleOf(node), rect: rectOf(node),
        });
      }
      return {
        srcAttribute: img.getAttribute('src'), src: img.src, currentSrc: img.currentSrc,
        complete: img.complete, naturalWidth: img.naturalWidth, naturalHeight: img.naturalHeight,
        style: styleOf(img), rect: rectOf(img), ancestorChain: chain,
      };
    });
    const describeHits = (x, y) => document.elementsFromPoint(x, y).slice(0, 7).map((node) => ({
      tag: node.tagName, id: node.id || null,
      className: typeof node.className === 'string' ? node.className : null,
      src: node.currentSrc || node.src || null, styleAttribute: node.getAttribute('style'),
      computed: styleOf(node), rect: rectOf(node),
    }));
    const pointHits = fixedPoints.map(([x, y]) => ({ x, y, elements: describeHits(x, y) }));
    if (targetImages[0]) {
      const r = targetImages[0].getBoundingClientRect();
      const x = Math.max(0, Math.min(innerWidth - 1, Math.floor(r.x + r.width / 2)));
      const y = Math.max(0, Math.min(innerHeight - 1, Math.floor(r.y + r.height / 2)));
      pointHits.push({ label: 'target-image-center', x, y, elements: describeHits(x, y) });
    }
    return {
      title: document.title,
      location: location.href,
      viewport: { width: innerWidth, height: innerHeight, devicePixelRatio },
      page: { scrollWidth: document.documentElement.scrollWidth, scrollHeight: document.documentElement.scrollHeight,
        bodyBackground: styleOf(document.body).backgroundColor, bodyRect: rectOf(document.body) },
      images, targetImages: targetDetails, pointHits,
    };
  }, { routePath: targetPath, fixedPoints: points });
}

async function captureOne(row, version, port) {
  const targetUrl = new URL(row.saved_link.href);
  if (targetUrl.hostname !== '127.0.0.1' || targetUrl.port !== '24786') {
    throw new Error('Unexpected saved link origin for ' + row.mapping_id + ': ' + targetUrl.origin);
  }
  targetUrl.port = port;
  const allowedOrigin = targetUrl.origin;
  const blocked = [];
  const failed = [];
  const browser = await chromium.launch({
    headless: true,
    executablePath: chromePath,
    args: [],
  });
  try {
    const context = await browser.newContext({
      serviceWorkers: 'block',
      viewport: { width: 1480, height: 1250 },
      deviceScaleFactor: 1,
    });
    await context.route('**/*', async (route) => {
      const u = new URL(route.request().url());
      if ((u.protocol === 'http:' || u.protocol === 'https:') && u.origin !== allowedOrigin) {
        blocked.push({ origin: u.origin, pathname: u.pathname });
        await route.abort();
        return;
      }
      await route.continue();
    });
    const page = await context.newPage();
    page.on('pageerror', (err) => report.page_errors.push({ version, mapping_id: row.mapping_id, message: String(err) }));
    page.on('requestfailed', (req) => failed.push({ url: req.url(), error: req.failure()?.errorText || null }));
    const started = new Date().toISOString();
    const response = await page.goto(targetUrl.href, { waitUntil: 'networkidle', timeout: 30000 });
    if (!response || response.status() !== 200) {
      throw new Error(version + '/' + row.mapping_id + ': document returned ' + (response?.status() ?? 'no response'));
    }
    await page.evaluate(() => document.fonts.ready);
    await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await page.waitForTimeout(1500);
    const details = await snapshot(page, row.on_route);
    const screenshotPath = path.join(evidenceRoot, version + '-' + row.mapping_id + '.png');
    await page.screenshot({ path: screenshotPath, fullPage: false });
    const screenshotSha = crypto.createHash('sha256').update(fs.readFileSync(screenshotPath)).digest('hex');
    const check = {
      version, mapping_id: row.mapping_id, page: row.page, target_route: row.on_route,
      saved_digits_sha256: crypto.createHash('sha256').update(row.saved_link.digits).digest('hex'),
      url: targetUrl.href, allowed_origin: allowedOrigin, document_status: response.status(),
      started_utc: started, captured_utc: new Date().toISOString(),
      off_origin_requests_aborted: blocked, request_failures: failed, ...details,
      screenshot: path.relative(root, screenshotPath).split(path.sep).join('/'),
      screenshot_sha256: screenshotSha,
    };
    await context.close();
    return check;
  } finally {
    await browser.close();
  }
}

(async () => {
  if (fs.existsSync(path.join(evidenceRoot, 'runtime'))) throw new Error('unexpected runtime path collision');
  for (const id of ids) {
    const row = source.talent_checks.find((item) => item.mapping_id === id);
    if (!row || row.status !== 'passed' || !row.saved_link?.href || !row.on_route) {
      throw new Error('Missing accepted saved-template inputs for ' + id);
    }
    for (const server of portPairs) {
      // Cold-start and close Chrome for each of the four local page captures.
      report.checks.push(await captureOne(row, server.version, server.port));
    }
  }
  report.finished_utc = new Date().toISOString();
  report.page_count = report.checks.length;
  report.all_documents_200 = report.checks.length === 4 && report.checks.every((x) => x.document_status === 200);
  report.no_off_origin_requests = report.checks.every((x) => x.off_origin_requests_aborted.length === 0)
    && report.external_requests_aborted.length === 0;
  report.no_page_errors = report.page_errors.length === 0;
  report.target_images_complete = report.checks.every((x) => x.targetImages.length > 0
    && x.targetImages.every((img) => img.complete && img.naturalWidth === 36 && img.naturalHeight === 36));
  report.passed = report.all_documents_200 && report.no_off_origin_requests && report.no_page_errors && report.target_images_complete;
  fs.writeFileSync(path.join(evidenceRoot, 'comparison.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify({
    passed: report.passed, page_count: report.page_count,
    external_requests_aborted: report.external_requests_aborted.length, page_errors: report.page_errors.length,
    target_images_complete: report.target_images_complete,
    screenshot_hashes: report.checks.map((x) => ({ version: x.version, mapping_id: x.mapping_id, sha256: x.screenshot_sha256 })),
  }));
})().catch((error) => {
  report.finished_utc = new Date().toISOString();
  report.fatal_error = String(error?.stack || error);
  fs.writeFileSync(path.join(evidenceRoot, 'comparison.json'), JSON.stringify(report, null, 2) + '\n');
  console.error(error);
  process.exitCode = 1;
});
