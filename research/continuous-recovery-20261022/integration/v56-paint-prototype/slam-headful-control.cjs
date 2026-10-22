'use strict';

// One unmodified headful Chrome control page requested after review of the 3-page paint prototype.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const assert = require('assert');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../..');
const INPUT_REPORT = path.join(ROOT, 'research/continuous-recovery-20261022/integration/related-talent-icons-v56/implementation/runs/v56-2026-10-22T12-42-28-056Z/browser-check.json');
const TARGET_ID = 'warrior-improved-slam';
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
function sha256(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }
function stamp() { return new Date().toISOString().replace(/[:.]/g, '-'); }

async function main() {
  const inputBytes = fs.readFileSync(INPUT_REPORT);
  const input = JSON.parse(inputBytes.toString('utf8'));
  const target = input.talent_checks.find(row => row.mapping_id === TARGET_ID);
  assert(target && target.saved_link && target.saved_link.href, 'no saved link for target');
  const savedUrl = new URL(target.saved_link.href);
  assert(savedUrl.origin === 'http://127.0.0.1:24786', 'saved URL is not loopback');

  const runDir = path.join(__dirname, 'runs', 'slam-control-' + stamp());
  fs.mkdirSync(runDir, { recursive: true });
  const report = {
    schema: 'wow-v56-paint-prototype-slam-control/v1',
    started_utc: new Date().toISOString(),
    status: 'running',
    product_css_injection: false,
    production_acceptance: false,
    browser: { executable: CHROME, headed: true, launch_args: [], viewport: { width: 1480, height: 1250 }, device_scale_factor: 1, gpu_flags_overridden: false },
    saved_template: { mapping_id: TARGET_ID, href: savedUrl.href, digits: target.saved_link.digits, source_report: path.relative(ROOT, INPUT_REPORT).split(path.sep).join('/'), source_report_sha256: sha256(inputBytes) },
    policy: { same_origin_only: 'http://127.0.0.1:24786', off_origin: 'abort and record', fulfill_or_substitution: false, css_injection: false, wait: 'networkidle, document.fonts.ready, 2 requestAnimationFrame, 1000ms, then viewport screenshot' },
    external_requests_aborted: [], http_errors: [], request_failures: [], page_errors: []
  };
  let browser, context;
  try {
    browser = await chromium.launch({ headless: false, executablePath: CHROME });
    context = await browser.newContext({ serviceWorkers: 'block', viewport: { width: 1480, height: 1250 }, deviceScaleFactor: 1 });
    await context.route('**/*', async route => {
      let url;
      try { url = new URL(route.request().url()); } catch (_) { return route.continue(); }
      if (['data:', 'blob:', 'about:'].includes(url.protocol)) return route.continue();
      if (url.origin !== 'http://127.0.0.1:24786') {
        report.external_requests_aborted.push({ url: route.request().url(), resource_type: route.request().resourceType() });
        return route.abort();
      }
      return route.continue();
    });
    context.on('requestfailed', request => report.request_failures.push({ url: request.url(), failure: request.failure() && request.failure().errorText }));
    const page = await context.newPage();
    page.on('pageerror', error => report.page_errors.push(String(error)));
    page.on('response', response => { if (response.status() >= 400) report.http_errors.push({ url: response.url(), status: response.status() }); });
    const response = await page.goto(savedUrl.href, { waitUntil: 'load', timeout: 60000 });
    assert(response && response.status() === 200, 'saved talent page did not return 200');
    await page.waitForLoadState('networkidle', { timeout: 60000 });
    await page.evaluate(async () => {
      if (document.fonts && document.fonts.ready) await document.fonts.ready;
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    });
    await page.waitForTimeout(1000);
    report.navigation_status = response.status();
    report.page = await page.evaluate(() => ({ title: document.title, href: location.href, img_count: document.images.length }));
    report.images = await page.evaluate(() => Array.from(document.images, (img, index) => {
      const rect = img.getBoundingClientRect();
      const cs = getComputedStyle(img);
      const parents = [];
      let node = img.parentElement;
      for (let depth = 1; node && depth <= 4; depth++, node = node.parentElement) {
        const r = node.getBoundingClientRect(), s = getComputedStyle(node);
        parents.push({ depth, tag: node.tagName, id: node.id || null, class_name: typeof node.className === 'string' ? node.className : null,
          display: s.display, visibility: s.visibility, opacity: s.opacity,
          visible: s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity) > 0 && r.width > 0 && r.height > 0,
          rect: { x: Number(r.x.toFixed(3)), y: Number(r.y.toFixed(3)), width: Number(r.width.toFixed(3)), height: Number(r.height.toFixed(3)) } });
      }
      return { index, src: img.src, current_src: img.currentSrc, complete: img.complete, natural_width: img.naturalWidth, natural_height: img.naturalHeight,
        visibility: cs.visibility, display: cs.display, opacity: cs.opacity,
        visible: cs.display !== 'none' && cs.visibility !== 'hidden' && Number(cs.opacity) > 0 && rect.width > 0 && rect.height > 0,
        rect: { x: Number(rect.x.toFixed(3)), y: Number(rect.y.toFixed(3)), width: Number(rect.width.toFixed(3)), height: Number(rect.height.toFixed(3)) }, parents };
    }));
    report.target_images = report.images.filter(row => row.src.includes('/warrior/images/fury/improvedslam'));
    report.loaded_image_count = report.images.filter(row => row.complete && row.natural_width > 0 && row.natural_height > 0).length;
    const screenshot = path.join(runDir, 'control.png');
    await page.screenshot({ path: screenshot, fullPage: false });
    report.screenshot = path.relative(ROOT, screenshot).split(path.sep).join('/');
    report.screenshot_sha256 = sha256(fs.readFileSync(screenshot));
    report.status = 'unmodified_headful_control_captured';
  } catch (error) {
    report.status = 'failed';
    report.error = String(error && error.stack || error);
    process.exitCode = 1;
  } finally {
    if (context) await context.close();
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    report.report_path = path.relative(ROOT, path.join(runDir, 'report.json')).split(path.sep).join('/');
    fs.writeFileSync(path.join(runDir, 'report.json'), JSON.stringify(report, null, 2) + '\n');
    process.stdout.write(JSON.stringify({ status: report.status, images: report.images && report.images.length, loaded: report.loaded_image_count, target_images: report.target_images && report.target_images.length, external: report.external_requests_aborted.length, screenshot: report.screenshot, report: report.report_path, failure: report.error || null }) + '\n');
  }
}

main().catch(error => { process.stderr.write(String(error && error.stack || error) + '\n'); process.exitCode = 1; });
