// Read the exported files in actual Chrome; no interception supplies assets or changes the DOM.
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const port = '24763';
const base = `http://127.0.0.1:${port}/WOW-Encyclopedia-Deployable-Archive`;
const out = path.join(__dirname, 'root-v45-browser-acceptance.json');
const shots = path.join(__dirname, 'v45-screenshots-r2');
(async () => {
  assert(!fs.existsSync(out));
  fs.mkdirSync(shots, {recursive:true});
  const started = new Date().toISOString();
  const browser = await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const context = await browser.newContext({serviceWorkers:'block', viewport:{width:1440,height:1050}});
  const external = [], errors = [], failed = [], responses = [];
  await context.route('**/*', route => {
    const u = new URL(route.request().url());
    if ((u.hostname === '127.0.0.1' && u.port === port) || ['data:','blob:','about:'].includes(u.protocol)) return route.continue();
    external.push(route.request().url()); return route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(String(e)));
  page.on('requestfailed', r => failed.push({url:r.url(),error:r.failure()}));
  page.on('response', r => responses.push({url:r.url(),status:r.status()}));
  const pages = [];
  async function go(route) {
    const response = await page.goto(base+route,{waitUntil:'load',timeout:20000});
    assert.equal(response.status(),200,route);
    await page.waitForTimeout(150);
    return {route,status:response.status(),final_url:page.url(),title:await page.title()};
  }
  try {
    const tinfoil = await go('/info/items/tinfoilhat.xml.html');
    tinfoil.tooltip = await page.locator('div.tooltip').evaluate(el => ({
      text:el.innerText, width:el.getBoundingClientRect().width,
      backgrounds:[...el.querySelectorAll('td')].map(td=>getComputedStyle(td).backgroundImage),
    }));
    assert.equal(tinfoil.tooltip.width,300);
    assert(tinfoil.tooltip.text.includes('Tinfoil Hat'));
    const expected = ['ttip-tl.png','ttip-tr.png','ttip-t.png','ttip-l.png','ttip-r.png','ttipbg.png','ttip-bl.png','ttip-br.png','ttip-b.png'];
    for(const name of expected) {
      const url = base+'/wrath/images/layout/'+name;
      assert(tinfoil.tooltip.backgrounds.some(bg=>bg.includes(url)),name);
      assert(responses.some(r=>r.url===url && r.status===200),name+' was not actually served');
    }
    assert(!tinfoil.tooltip.backgrounds.some(bg=>bg.includes('missing-image')));
    await page.locator('div.tooltip').screenshot({path:path.join(shots,'tinfoil-tooltip.png'),animations:'disabled'});
    await page.screenshot({path:path.join(shots,'tinfoil-page.png'),fullPage:true,animations:'disabled'});
    pages.push(tinfoil);
    const molten = await go('/moltencore/index.html');
    const arrow = page.locator('.footer .legal q img');
    molten.arrow = await arrow.evaluate(img=>({src:img.currentSrc,width:img.naturalWidth,height:img.naturalHeight,
      href:img.closest('a')?.getAttribute('href'),label:img.parentElement.innerText}));
    assert.equal(molten.arrow.src,base+'/wrath/images/layout/backarrow.gif');
    assert.equal(molten.arrow.width,24); assert.equal(molten.arrow.height,24);
    await page.locator('.footer').screenshot({path:path.join(shots,'moltencore-footer.png'),animations:'disabled'});
    await arrow.click();
    await page.waitForURL(url=>url.pathname.endsWith('/index.xml.html'),{timeout:10000});
    await page.waitForLoadState('load');
    assert(page.url().startsWith(base+'/'));
    assert(!page.url().includes('/__offline/missing'));
    molten.return_click_url = page.url(); pages.push(molten);
    const news = await go('/news/wow-news-06-2005.html');
    const entry = page.getByRole('link',{name:'View historical contest',exact:true});
    assert.equal(await entry.count(),1);
    await entry.click(); await page.waitForLoadState('load');
    news.entry_click_url = page.url();
    assert(page.url().endsWith('/contests/05-06-09/index.html'));
    pages.push(news);
    const contest = {route:'/contests/05-06-09/index.html', final_url:page.url()};
    const text = await page.locator('body').innerText();
    assert(text.includes('Blizzard announced a giveaway'));
    assert(text.includes('planned publication of the winners'));
    contest.note = await page.locator('p.historical-rules-note').innerText();
    assert.equal(await page.locator('p.historical-rules-note a').count(),0);
    assert.equal(await page.locator('img[src*="continue" i]').count(),0);
    await page.locator('p.historical-rules-note').screenshot({path:path.join(shots,'contest-note.png'),animations:'disabled'});
    pages.push(contest);
    const program = await go('/misc/fan-site-program.html');
    assert((await page.locator('body').innerText()).includes('This historical exhibit does not accept applications.'));
    assert.equal(await page.locator('a[href^="mailto:"],input[type=password],input[type=email],input[type=file]').count(),0);
    pages.push(program);
    const receipt = {accepted:errors.length===0 && failed.length===0 && external.length===0,version:'v45',started_utc:started,finished_utc:new Date().toISOString(),
      actual_browser:'Chrome',unmodified_export_served:true,network_scope:'loopback only',pages,
      page_errors:errors,request_failures:failed,external_requests:external,
      http_errors:responses.filter(r=>r.status>=400),screenshots_dir:'v45-screenshots-r2',
      prior_talent_browser_reuse:'Nine v44 talent HTML files and all talent scripts/data are byte-identical; v45 tree acceptance separately verifies the runtime differs only by route-map entries.'};
    fs.writeFileSync(path.join(__dirname,'root-v45-browser-attempt2.json'),JSON.stringify(receipt,null,2)+'\n');
    assert.equal(errors.length,0,JSON.stringify(errors));
    assert.equal(failed.length,0,JSON.stringify(failed));
    assert.equal(external.length,0,JSON.stringify(external));
    fs.writeFileSync(out,JSON.stringify(receipt,null,2)+'\n');
    console.log(JSON.stringify({accepted:true,pages:pages.length,http_errors:receipt.http_errors.length}));
  } finally {await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
