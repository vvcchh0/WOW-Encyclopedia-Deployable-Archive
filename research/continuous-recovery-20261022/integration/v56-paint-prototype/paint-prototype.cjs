'use strict';

// Bounded local paint-compositing prototype. This is not product code or formal acceptance.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const assert = require('assert');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const ROOT = path.resolve(__dirname, '../../../..');
const INPUT_REPORT = path.join(ROOT, 'research/continuous-recovery-20261022/integration/related-talent-icons-v56/implementation/runs/v56-2026-10-22T12-42-28-056Z/browser-check.json');
const OUTPUT_ROOT = path.join(__dirname, 'runs');
const TARGET_ID = 'warrior-improved-thunder-clap';
const VARIANTS = [
  { id: 'control', css: null },
  { id: 'body-translate-z', css: 'body{transform:translateZ(0)}' },
  { id: 'img-translate-z', css: 'img{transform:translateZ(0)}' }
];
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';

function sha256(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }
function nowStamp() { return new Date().toISOString().replace(/[:.]/g, '-'); }
function round(value) { return Number(value.toFixed(3)); }
function getSavedHref() {
  const report = JSON.parse(fs.readFileSync(INPUT_REPORT, 'utf8'));
  const row = report.talent_checks.find(entry => entry.mapping_id === TARGET_ID);
  assert(row && row.saved_link && row.saved_link.href, 'v56 browser report has no saved-link href for target');
  const href = new URL(row.saved_link.href);
  assert(href.origin === 'http://127.0.0.1:24786', 'saved link is outside the expected loopback origin');
  return { href: href.href, digits: row.saved_link.digits, report_path: path.relative(ROOT, INPUT_REPORT).split(path.sep).join('/'), report_sha256: sha256(fs.readFileSync(INPUT_REPORT)) };
}

async function settlePage(page) {
  await page.waitForLoadState('networkidle', { timeout: 60000 });
  await page.evaluate(async () => {
    if (document.fonts && document.fonts.ready) await document.fonts.ready;
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  });
  await page.waitForTimeout(1000);
}

async function collectImageMetrics(page) {
  return await page.evaluate(() => {
    const occurrences = new Map();
    return Array.from(document.images, (img, index) => {
    const rect = img.getBoundingClientRect();
    const style = getComputedStyle(img);
    let route = null, source_key = null;
    try {
      const src = new URL(img.currentSrc || img.src, location.href);
      route = src.pathname;
      route = route.replace(/^\/WOW-Encyclopedia-Deployable-Archive(?=\/)/, '');
      source_key = route + src.search;
    } catch (_) {}
    const route_occurrence = source_key === null ? index : (occurrences.get(source_key) || 0);
    if (source_key !== null) occurrences.set(source_key, route_occurrence + 1);
    const visible = style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0;
    return {
      index,
      route,
      source_key,
      route_occurrence,
      complete: img.complete,
      natural_width: img.naturalWidth,
      natural_height: img.naturalHeight,
      visibility: style.visibility,
      display: style.display,
      opacity: style.opacity,
      visible,
      rect: { x: Number(rect.x.toFixed(3)), y: Number(rect.y.toFixed(3)), width: Number(rect.width.toFixed(3)), height: Number(rect.height.toFixed(3)), top: Number(rect.top.toFixed(3)), right: Number(rect.right.toFixed(3)), bottom: Number(rect.bottom.toFixed(3)), left: Number(rect.left.toFixed(3)) }
    };
    });
  });
}

async function runVariant(browser, variant, saved, runDir) {
  // A new incognito context per variant isolates cookies and image cache while sharing the same Chrome/GPU process.
  const context = await browser.newContext({ serviceWorkers: 'block', viewport: { width: 1480, height: 1250 }, deviceScaleFactor: 1 });
  const externalRequests = [];
  const httpErrors = [];
  const pageErrors = [];
  const contextFailures = [];
  await context.route('**/*', async route => {
    const request = route.request();
    let url;
    try { url = new URL(request.url()); } catch (_) { return route.continue(); }
    if (['data:', 'blob:', 'about:'].includes(url.protocol)) return route.continue();
    if (url.origin !== 'http://127.0.0.1:24786') {
      externalRequests.push({ url: request.url(), resource_type: request.resourceType() });
      return route.abort();
    }
    return route.continue();
  });
  context.on('requestfailed', request => contextFailures.push({ url: request.url(), failure: request.failure() && request.failure().errorText }));
  const page = await context.newPage();
  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('response', response => { if (response.status() >= 400) httpErrors.push({ url: response.url(), status: response.status() }); });
  try {
    const response = await page.goto(saved.href, { waitUntil: 'load', timeout: 60000 });
    assert(response && response.status() === 200, 'saved talent page did not return 200: ' + saved.href);
    if (variant.css) {
      await page.addStyleTag({ content: variant.css });
      await settlePage(page);
    } else {
      await settlePage(page);
    }
    const pageInfo = await page.evaluate(targetId => {
      const selected = Array.from(document.querySelectorAll('[data-talent-id], .talent, img')).find(node => (node.getAttribute('data-talent-id') || '').includes(targetId));
      return { title: document.title, href: location.href, img_count: document.images.length, body_rect: (() => { const r = document.body.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; })(), target_probe: selected ? selected.outerHTML.slice(0, 500) : null };
    }, TARGET_ID);
    const images = await collectImageMetrics(page);
    const targetImages = images.filter(image => image.route && image.route.includes('/warrior/images/arms/improvedthunderclap'));
    const screenshot = path.join(runDir, variant.id + '.png');
    await page.screenshot({ path: screenshot, fullPage: false });
    return {
      id: variant.id,
      injected_css: variant.css,
      navigation_status: response.status(),
      page: pageInfo,
      image_count: images.length,
      loaded_image_count: images.filter(image => image.complete && image.natural_width > 0 && image.natural_height > 0).length,
      visible_image_count: images.filter(image => image.visible).length,
      target_images: targetImages,
      images,
      screenshot: path.relative(ROOT, screenshot).split(path.sep).join('/'),
      screenshot_sha256: sha256(fs.readFileSync(screenshot)),
      external_requests_aborted: externalRequests,
      http_errors: httpErrors,
      page_errors: pageErrors,
      request_failures: contextFailures
    };
  } finally {
    await context.close();
  }
}

async function main() {
  const saved = getSavedHref();
  fs.mkdirSync(OUTPUT_ROOT, { recursive: true });
  const runDir = path.join(OUTPUT_ROOT, 'paint-' + nowStamp());
  fs.mkdirSync(runDir, { recursive: false });
  const report = {
    schema: 'wow-v56-paint-compositing-prototype/v1',
    started_utc: new Date().toISOString(),
    status: 'running',
    purpose: 'Three cold-page v56 render comparison for the saved Warrior Improved Thunder Clap template.',
    production_acceptance: false,
    browser: { executable: CHROME, headed: true, launch_args: [], viewport: { width: 1480, height: 1250 }, device_scale_factor: 1, gpu_flags_overridden: false },
    saved_template: saved,
    policy: { same_origin_only: 'http://127.0.0.1:24786', external_requests: 'aborted', response_fulfillment: false, pages_serial: true, context_per_variant: true, wait: 'networkidle, document.fonts.ready, 2 requestAnimationFrame, 1000ms, then viewport screenshot' },
    variants: []
  };
  let browser;
  try {
    browser = await chromium.launch({ headless: false, executablePath: CHROME });
    for (const variant of VARIANTS) report.variants.push(await runVariant(browser, variant, saved, runDir));
    const byVariant = new Map(report.variants.map(variant => [variant.id, new Map(variant.images.map(image => [image.source_key + '|' + image.route_occurrence, image]))]));
    const sharedKeys = Array.from(byVariant.get('control').keys()).filter(key => byVariant.get('body-translate-z').has(key) && byVariant.get('img-translate-z').has(key));
    report.shared_image_count = sharedKeys.length;
    report.shared_image_key_rule = 'normalized source URL path and query plus zero-based occurrence of that source URL in document.images';
    report.shared_image_keys = sharedKeys;
    report.metric_comparison_to_control = Object.fromEntries(['body-translate-z', 'img-translate-z'].map(id => {
      let rect_changed = 0, visibility_changed = 0, natural_size_changed = 0;
      let max_rect_delta = 0;
      for (const key of sharedKeys) {
        const base = byVariant.get('control').get(key), compared = byVariant.get(id).get(key);
        if (['x', 'y', 'width', 'height', 'top', 'right', 'bottom', 'left'].some(field => base.rect[field] !== compared.rect[field])) rect_changed++;
        if (base.visible !== compared.visible || base.visibility !== compared.visibility || base.display !== compared.display || base.opacity !== compared.opacity) visibility_changed++;
        if (base.natural_width !== compared.natural_width || base.natural_height !== compared.natural_height) natural_size_changed++;
        for (const field of ['x', 'y', 'width', 'height', 'top', 'right', 'bottom', 'left']) max_rect_delta = Math.max(max_rect_delta, Math.abs(base.rect[field] - compared.rect[field]));
      }
      return [id, { common_images: sharedKeys.length, rect_changed, max_rect_delta_css_px: round(max_rect_delta), visibility_changed, natural_size_changed }];
    }));
    report.status = 'three_variants_captured';
  } catch (error) {
    report.status = 'failed';
    report.error = String(error && error.stack || error);
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    report.report_path = path.relative(ROOT, path.join(runDir, 'report.json')).split(path.sep).join('/');
    fs.writeFileSync(path.join(runDir, 'report.json'), JSON.stringify(report, null, 2) + '\n');
    process.stdout.write(JSON.stringify({ status: report.status, variants: report.variants.map(item => ({ id: item.id, screenshot: item.screenshot, images: item.image_count })), shared_image_count: report.shared_image_count || 0, report: report.report_path, failure: report.error || null }) + '\n');
  }
}

main().catch(error => { process.stderr.write(String(error && error.stack || error) + '\n'); process.exitCode = 1; });
