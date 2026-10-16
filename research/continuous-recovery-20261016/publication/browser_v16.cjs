const fs = require('fs');
const crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = process.cwd();
const out = root + '/research/continuous-recovery-20261016/publication/';
const base = 'http://127.0.0.1:29012/WOW-Encyclopedia-Deployable-Archive/';
const maps = ['v16-primary-news-image-source-map.json', 'v16-eu-image-source-map.json'].map(name =>
  JSON.parse(fs.readFileSync(root + '/research/continuous-recovery-20261016/integration/' + name, 'utf8')));
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
(async () => {
  let browser;
  const report = { started_utc: new Date().toISOString(), accepted: false, checks: [], errors: [], external_requests: [], responses: [] };
  try {
    browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({ viewport: { width: 1400, height: 1000 } });
    await context.route('**/*', route => {
      const req = route.request(), url = new URL(req.url());
      if (url.hostname === '127.0.0.1' && url.port === '29012' && ['GET', 'HEAD'].includes(req.method())) return route.continue();
      report.external_requests.push({ url: req.url(), method: req.method() });
      return route.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', error => report.errors.push(String(error)));
    for (const [name, items] of [
      ['news/rss-07-2006.xml.html', maps[0].items.filter(x => x.logical_url.includes('/06-07/'))],
      ['news/rss-01-2007.xml.html', maps[0].items.filter(x => x.logical_url.includes('/07-01/'))],
    ]) {
      await page.goto(base + name, { waitUntil: 'networkidle' });
      for (const item of items) {
        const path = new URL(item.logical_url).pathname;
        const img = page.locator('img[src="/WOW-Encyclopedia-Deployable-Archive' + path + '"]').first();
        if (await img.count() !== 1) throw Error('News image reference missing: ' + path);
        const holderId = await img.evaluate(el => el.closest('.news-item')?.parentElement?.id || null);
        if (!holderId) throw Error('Missing article holder for ' + path);
        const body = page.locator('#' + holderId + ' .news-item');
        if (!(await body.isVisible())) {
          await page.locator('#' + holderId + ' h1').first().click();
          await body.waitFor({ state: 'visible', timeout: 2000 });
        }
        await img.scrollIntoViewIfNeeded();
        const state = await img.evaluate(el => ({ complete: el.complete, width: el.naturalWidth, height: el.naturalHeight, url: el.currentSrc }));
        const response = await context.request.get(state.url);
        const bytes = await response.body();
        const okay = await img.isVisible() && state.complete && state.width === 130 && state.height === 100 && response.status() === 200 && bytes.length === item.length && sha(bytes) === item.sha256;
        report.checks.push({ name: 'expanded news image', page: name, path, article: holderId, state, accepted: okay });
        if (!okay) throw Error('News image failed: ' + path);
      }
      if (name.includes('07-2006')) await page.locator('#news7-27-06-233').count().then(async count => {
        if (count) await page.locator('#news7-27-06-233').screenshot({ path: out + 'v16-news-expanded.png' });
        else await page.screenshot({ path: out + 'v16-news-expanded.png' });
      });
    }
    await page.goto(base + '__offline/related-images/index.html', { waitUntil: 'networkidle' });
    for (const item of maps[1].items) {
      const path = '/_origins/' + new URL(item.logical_url).hostname + new URL(item.logical_url).pathname;
      const img = page.locator('img[src="/WOW-Encyclopedia-Deployable-Archive' + path + '"]').first();
      if (await img.count() !== 1) throw Error('EU card missing: ' + path);
      await img.scrollIntoViewIfNeeded();
      const state = await img.evaluate(el => ({ complete: el.complete, width: el.naturalWidth, height: el.naturalHeight, url: el.currentSrc }));
      const response = await context.request.get(state.url), bytes = await response.body();
      const okay = state.complete && state.width === item.dimensions[0] && state.height === item.dimensions[1] && response.status() === 200 && bytes.length === item.length && sha(bytes) === item.sha256;
      report.checks.push({ name: 'related EU original image', path, state, accepted: okay });
      if (!okay) throw Error('EU original image failed: ' + path);
    }
    await page.screenshot({ path: out + 'v16-related-eu.png' });
    await page.goto(base + 'news/rss-08-2007.xml.html', { waitUntil: 'networkidle' });
    const titles = await page.locator('h1').count();
    if (titles !== 50) throw Error('August titles regressed');
    report.checks.push({ name: 'retained August 50 articles', accepted: true });
    if (report.errors.length || report.external_requests.length) throw Error('Page errors or external request');
    report.accepted = true;
  } catch (error) {
    report.errors.push(String(error));
  } finally {
    if (browser) await browser.close();
    report.finished_utc = new Date().toISOString();
    fs.writeFileSync(out + 'root-v16-browser-acceptance.json', JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ accepted: report.accepted, checks: report.checks.length, errors: report.errors, external_requests: report.external_requests.length }));
    if (!report.accepted) process.exitCode = 1;
  }
})();
