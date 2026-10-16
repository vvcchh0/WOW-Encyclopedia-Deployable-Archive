const fs = require('fs');
const crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const root = process.cwd();
const base = 'http://127.0.0.1:29014/WOW-Encyclopedia-Deployable-Archive/';
const output = root + '/.scratch/pages-resources-20261016-v18/';
const provenance = JSON.parse(fs.readFileSync(output + 'export-provenance.json', 'utf8'));
const map = JSON.parse(fs.readFileSync(root + '/research/continuous-recovery-20261016/integration/v18-guide-previews/guide-previews-source-map-v2.json', 'utf8'));
const city = map.groups.find(group => group.group_id === 'city-attacks');
const byRoute = Object.fromEntries(provenance.files.map(item => [item.route, item]));
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const reportPath = root + '/research/continuous-recovery-20261016/publication/root-v18-browser-acceptance.json';
const screenshotPath = root + '/research/continuous-recovery-20261016/publication/root-city-attacks-v18.png';

(async () => {
  const report = {schema:'wow-recovery.root.v18.city-browser-acceptance.v1', base, port:29014, accepted:false, checks:[], errors:[], external_requests:[], screenshots:[]};
  let browser;
  const check = (name, accepted, detail={}) => {
    report.checks.push({name, accepted, ...detail});
    if (!accepted) throw Error(name + ': ' + JSON.stringify(detail));
  };
  try {
    if (!city || city.previews.length !== 3) throw Error('v2 map City Attacks group is not exactly three previews');
    browser = await chromium.launch({headless:true});
    const context = await browser.newContext({viewport:{width:1400,height:1000}});
    await context.route('**/*', route => {
      const request = route.request();
      const url = new URL(request.url());
      if (url.origin === 'http://127.0.0.1:29014' && ['GET','HEAD'].includes(request.method())) return route.continue();
      report.external_requests.push({url:request.url(), method:request.method()});
      return route.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', error => report.errors.push(String(error)));
    const galleryUrl = base + 'pvp/worldpvp/cityattacks-gallery.html';
    await page.goto(galleryUrl, {waitUntil:'networkidle'});
    const section = page.locator('.offline-guide-preview-section');
    check('city gallery loaded', page.url() === galleryUrl, {url:page.url()});
    check('one City preview section', await section.count() === 1);
    check('City card count', await section.locator('img').count() === 3);
    const cityMarkup = await page.content();
    check('original dynamic gallery retained', cityMarkup.includes('galleryNext') && /numShots\s*=\s*102/.test(cityMarkup));
    const guideHref = await section.locator('.offline-guide-preview-guide').getAttribute('href');
    check('original guide link', new URL(guideHref, base).href === base + 'info/basics/pvpcombat.html', {guideHref});
    for (const image of city.previews) {
      const img = section.locator('a[data-guide-preview-route="' + image.route + '"] img');
      await img.scrollIntoViewIfNeeded();
      await img.waitFor({state:'visible'});
      const handle = await img.elementHandle();
      await page.waitForFunction(el => el.complete && el.naturalWidth > 0, handle);
      const state = await img.evaluate(el => ({url:el.currentSrc, width:el.naturalWidth, height:el.naturalHeight, complete:el.complete}));
      const response = await context.request.get(state.url);
      const bytes = await response.body();
      const record = byRoute[image.route];
      check('City preview bytes', response.status() === 200 && bytes.length === image.length && sha(bytes) === image.sha256 && record && record.derived_sha256 === image.sha256 && state.complete && state.width === 171 && state.height === 122, {route:image.route, state, bytes:bytes.length});
    }
    await section.screenshot({path:screenshotPath});
    report.screenshots.push(screenshotPath.replace(root + '/', ''));
    const first = section.locator('a[data-guide-preview-route]').first();
    const target = await first.getAttribute('href');
    await first.click();
    await page.waitForURL(new URL(target, base).href);
    check('preview link opens local image', page.url() === new URL(target, base).href, {url:page.url()});
    await page.goto(galleryUrl, {waitUntil:'networkidle'});
    const before = (await page.locator('#pageNum').innerText()).trim();
    await page.locator('a[href="javascript:galleryNext();"]').first().click();
    await page.waitForFunction(previous => document.getElementById('pageNum').innerText.trim() !== previous, before, {timeout:2000});
    const after = (await page.locator('#pageNum').innerText()).trim();
    check('native original pagination retained', before !== after && await page.locator('.offline-guide-preview-section img').count() === 3, {before,after});
    await page.goto(galleryUrl+'#1', {waitUntil:'networkidle'});
    await page.waitForTimeout(400);
    const hashState = await page.evaluate(()=>({hash:location.hash,index:window.nowViewing,total:window.shotList?.length}));
    check('original hash selection retained', hashState.hash === '#1' && Number.isInteger(hashState.index) && hashState.index>=0 && hashState.index<hashState.total, {state:hashState});
    await page.locator('.offline-guide-preview-guide').click();
    await page.waitForURL(base+'info/basics/pvpcombat.html');
    check('native guide navigation', page.url()===base+'info/basics/pvpcombat.html');
    report.accepted = report.errors.length === 0 && report.external_requests.length === 0 && report.checks.every(item => item.accepted);
  } catch (error) {
    report.errors.push(error.stack || String(error));
  } finally {
    report.finished_utc = new Date().toISOString();
    if (browser) await browser.close();
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({accepted:report.accepted, checks:report.checks.length, errors:report.errors, external:report.external_requests.length}));
    if (!report.accepted) process.exitCode = 1;
  }
})();
