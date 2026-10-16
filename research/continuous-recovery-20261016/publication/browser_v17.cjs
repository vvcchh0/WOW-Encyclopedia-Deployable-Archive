const fs = require('fs');
const crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = process.cwd();
const out = root + '/research/continuous-recovery-20261016/publication/';
const base = 'http://127.0.0.1:29013/WOW-Encyclopedia-Deployable-Archive/';
const read = p => JSON.parse(fs.readFileSync(root + '/' + p, 'utf8'));
const provenance = read('.scratch/pages-resources-20261016-v17/export-provenance.json');
const byRoute = Object.fromEntries(provenance.files.map(x => [x.route, x]));
const news = read('research/continuous-recovery-20261016/integration/v17-primary-news-image-source-map.json').items;
const compact = read('research/continuous-recovery-20261016/local-audit/all-news/compact-first20.json').items;
const guides = read('research/continuous-recovery-20261016/integration/guide-previews-source-map.json').groups;
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const urlFor = route => base + byRoute[route].output_path;

(async () => {
  let browser;
  const report = {started_utc:new Date().toISOString(),accepted:false,checks:[],errors:[],external_requests:[],screenshots:[]};
  function check(name, accepted, detail={}) {
    report.checks.push({name,accepted,...detail});
    if (!accepted) throw Error(name + ': ' + JSON.stringify(detail));
  }
  try {
    browser = await chromium.launch({headless:true});
    const context = await browser.newContext({viewport:{width:1400,height:1000}});
    await context.route('**/*', route => {
      const request = route.request(), url = new URL(request.url());
      if (url.origin === 'http://127.0.0.1:29013' && ['GET','HEAD'].includes(request.method())) return route.continue();
      report.external_requests.push({url:request.url(),method:request.method()});
      return route.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', e => report.errors.push(String(e)));
    for (const group of guides) {
      await page.goto(urlFor(group.gallery_route), {waitUntil:'networkidle'});
      const section = page.locator('.offline-guide-preview-section');
      check('one guide section',await section.count()===1,{gallery:group.gallery_route});
      check('guide link',await section.locator('.offline-guide-preview-guide').getAttribute('href')===byRoute[group.guide_route].static_url,{gallery:group.gallery_route});
      check('guide card count',await section.locator('img').count()===group.previews.length,{gallery:group.gallery_route});
      for (const image of group.previews) {
        const img = section.locator('a[data-guide-preview-route="'+image.route+'"] img');
        await img.scrollIntoViewIfNeeded();
        await img.waitFor({state:'visible'});
        await page.waitForFunction(el=>el.complete && el.naturalWidth>0,await img.elementHandle());
        const state = await img.evaluate(el=>({url:el.currentSrc,width:el.naturalWidth,height:el.naturalHeight,complete:el.complete}));
        const response = await context.request.get(state.url);
        const bytes = await response.body();
        check('guide preview bytes',response.status()===200 && bytes.length===image.length && sha(bytes)===image.sha256 && state.complete,{gallery:group.gallery_route,route:image.route,state});
      }
      const screenshot = 'v17-guide-'+group.group_id+'.png';
      await section.screenshot({path:out+screenshot});
      report.screenshots.push(screenshot);
      const first = section.locator('a[data-guide-preview-route]').first();
      const target = await first.getAttribute('href');
      await first.click();
      await page.waitForURL(new URL(target,base).href);
      check('preview link opens image',page.url()===new URL(target,base).href,{gallery:group.gallery_route});
      await page.goto(urlFor(group.gallery_route),{waitUntil:'networkidle'});
      const before = (await page.locator('#pageNum').innerText()).trim();
      await page.locator('a[href="javascript:galleryNext();"]').first().click();
      await page.waitForFunction(previous=>document.getElementById('pageNum').innerText.trim()!==previous,before,{timeout:2000});
      const after = (await page.locator('#pageNum').innerText()).trim();
      check('original pagination',before!==after && await page.locator('.offline-guide-preview-section img').count()===group.previews.length,{gallery:group.gallery_route,before,after});
      await page.goto(urlFor(group.gallery_route)+'#1',{waitUntil:'networkidle'});
      await page.waitForTimeout(400);
      const hashState = await page.evaluate(()=>({hash:location.hash,index:window.nowViewing,total:window.shotList?.length}));
      check('original gallery hash',hashState.hash==='#1' && Number.isInteger(hashState.index) && hashState.index>=0 && hashState.index<hashState.total,{gallery:group.gallery_route,state:hashState});
    }
    for (const image of news) {
      const evidence = compact.find(x=>x.raw_url===image.logical_url);
      const route = evidence ? evidence.page_routes[0] : image.logical_url.includes('/06-07/') ? '/news/rss-07-2006.xml' : '/news/rss-01-2007.xml';
      if (page.url()!==urlFor(route)) await page.goto(urlFor(route),{waitUntil:'networkidle'});
      const imageRoute = new URL(image.logical_url).pathname;
      const img = page.locator('img[src="'+byRoute[imageRoute].static_url+'"]').first();
      check('news reference present',await img.count()===1,{route,image:imageRoute});
      if (!(await img.isVisible())) {
        const holder = await img.evaluate(el=>el.closest('.news-item')?.parentElement?.id || null);
        if (!holder) throw Error('Hidden news image without expandable article: '+imageRoute);
        await page.locator('#'+holder+' h1').first().click();
        await img.waitFor({state:'visible'});
      }
      await img.scrollIntoViewIfNeeded();
      await page.waitForFunction(el=>el.complete && el.naturalWidth>0,await img.elementHandle());
      const state = await img.evaluate(el=>({url:el.currentSrc,width:el.naturalWidth,height:el.naturalHeight}));
      const response = await context.request.get(state.url), bytes = await response.body();
      check('expanded news image',await img.isVisible() && response.status()===200 && bytes.length===image.length && sha(bytes)===image.sha256 && state.width===image.dimensions[0] && state.height===image.dimensions[1],{route,image:imageRoute,state});
      if (image.logical_url.endsWith('/smallcaps/h.gif')) {
        const holder = await img.evaluate(el=>el.closest('.news-item')?.parentElement?.id);
        if (holder) { await page.locator('#'+holder).screenshot({path:out+'v17-news-glyph.png'}); report.screenshots.push('v17-news-glyph.png'); }
      }
    }
    await page.goto(urlFor('/news/rss-08-2007.xml'),{waitUntil:'networkidle'});
    check('August news retained',await page.locator('.hoverContainer h1').count()===50);
    await page.goto(urlFor('/info/encyclopedia/index.xml'),{waitUntil:'networkidle'});
    check('encyclopedia retained',(await page.locator('body').innerText()).includes('Warcraft Encyclopedia'));
    report.accepted = report.errors.length===0 && report.external_requests.length===0 && report.checks.every(x=>x.accepted);
  } catch (e) {report.errors.push(e.stack || String(e));}
  finally {
    report.finished_utc = new Date().toISOString();
    if(browser) await browser.close();
    fs.writeFileSync(out+'root-v17-browser-acceptance.json',JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify({accepted:report.accepted,checks:report.checks.length,errors:report.errors,external:report.external_requests.length}));
    if(!report.accepted) process.exitCode=1;
  }
})();
