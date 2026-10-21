"use strict";
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const assert = require('assert/strict');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const PORT = Number(process.env.PREVIEW_PORT || 59575);
const BASE = `http://127.0.0.1:${PORT}/WOW-Encyclopedia-Deployable-Archive`;
const OUT = path.join(__dirname, 'v40-browser-r2-screenshots');
fs.mkdirSync(OUT, { recursive: true });
async function capture(locator, name) {
  const file = path.join(OUT, name + '.png');
  await locator.screenshot({ path: file, timeout: 10000 });
  const bytes = fs.readFileSync(file);
  return { path: 'v40-browser-r2-screenshots/' + name + '.png', bytes: bytes.length,
    sha256: crypto.createHash('sha256').update(bytes).digest('hex') };
}
async function pair(page, locator, stem) {
  const a = await capture(locator, stem + '-a');
  await page.waitForTimeout(1100);
  const b = await capture(locator, stem + '-b');
  return { captures: [a,b], changed_pixels: a.sha256 !== b.sha256 };
}
(async () => {
  const started = new Date().toISOString();
  const browser = await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const context = await browser.newContext({viewport:{width:1440,height:1000},serviceWorkers:'block'});
  const external = [], requests = [];
  await context.route('**/*', route => {
    const u = new URL(route.request().url());
    if (u.protocol === 'http:' && u.hostname === '127.0.0.1' && u.port === String(PORT)) return route.continue();
    if (['data:','blob:','about:'].includes(u.protocol)) return route.continue();
    external.push(u.href); return route.abort();
  });
  context.on('request', r => requests.push(r.url()));
  const rows=[];
  try {
    for (const [kind,route] of [
      ['socket','/info/items/socketeditems.html'], ['dance','/info/races/dancing.html'],
      ['tuskarr','/wrath/features/factions/tuskarr.xml.html'], ['downloads','/downloads/index.html'],
      ['encyclopedia','/info/encyclopedia/index.xml.html'], ['historical-news','/news/wow-news2004.html'],
      ['historical-login','/visa/reward/login.html'],
    ]) {
      const page=await context.newPage(), errors=[], failed=[], responses=[], successful=new Set();
      page.on('pageerror',e=>errors.push(String(e)));
      page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()?.errorText}));
      page.on('response',r=>{if(r.status()>=400)responses.push({url:r.url(),status:r.status()}); else if(r.status()===200)successful.add(r.url());});
      const response=await page.goto(BASE+route,{waitUntil:'networkidle',timeout:25000});
      const row={kind,route,status:response?.status(),errors,failed,http_errors:responses};
      assert.equal(row.status,200);
      if (['socket','dance','tuskarr'].includes(kind)) {
        await page.waitForFunction(()=>window.__offlineFlash?.done,null,{timeout:20000});
        await page.waitForTimeout(700);
        row.flash=await page.evaluate(()=>JSON.parse(JSON.stringify(window.__offlineFlash)));
        row.players=await page.locator('ruffle-player').count();
        if(kind==='socket'){
          assert.equal(row.players,5); row.visual=[];
          for(let i=0;i<5;i++) row.visual.push(await pair(page,page.locator('ruffle-player').nth(i),'socket-'+i));
        } else if(kind==='dance'){
          assert.equal(row.players,1);
          row.visual_initial=await pair(page,page.locator('#flashImage ruffle-player'),'dwarf');
          const before=requests.filter(u=>u.includes('.swf')).length;
          await page.locator('select[onchange*="reloadRace"]').selectOption('1');
          await page.waitForFunction(()=>window.__offlineFlash.selection.status==='unavailable');
          row.unavailable=await page.locator('#flashImage').innerText();
          assert.equal(await page.locator('#flashImage ruffle-player').count(),0);
          assert.equal(requests.filter(u=>u.includes('.swf')).length,before);
          await page.locator('select[onchange*="reloadRace"]').selectOption('0');
          await page.waitForFunction(()=>window.__offlineFlash.selection.status==='displayed');
          assert.equal(await page.locator('#flashImage ruffle-player').count(),1);
          row.downloads=await page.locator('#dl_transparent,#dl_black,#dl_avatar').evaluateAll(es=>es.map(e=>e.href));
          assert.equal(row.downloads.length,3);
          for(const href of row.downloads) assert(new URL(href).pathname.endsWith('/__offline/missing.html'));
          row.visual_returned=await capture(page.locator('#flashImage ruffle-player'),'dwarf-returned');
        } else {
          assert.equal(row.players,1);
          assert.equal(await page.locator('#flashchar').first().locator('ruffle-player').count(),1);
          row.visual=await pair(page,page.locator('ruffle-player'),'tuskarr');
        }
      } else {
        assert.equal(await page.locator('script[data-offline-flash]').count(),0);
        assert.equal(await page.locator('ruffle-player').count(),0);
        if(kind==='downloads'){
          const image=page.locator('#goblue6');
          row.before=await image.getAttribute('src'); await image.hover();
          row.hover=await image.getAttribute('src'); await page.mouse.move(0,0); await page.waitForTimeout(150);
          row.after=await image.getAttribute('src');
          assert.notEqual(row.before,row.hover); assert.equal(row.before,row.after);
          row.snapshot=await capture(image,'downloads-hover-restored');
        } else if(kind==='historical-news'){
          const image=page.locator('img[src$="/news/images/04-12/ordernow.jpg"]').first();
          row.artwork=await image.evaluate(e=>({width:e.naturalWidth,height:e.naturalHeight,anchor:!!e.closest('a'),form:!!e.closest('form')}));
          assert.equal(row.artwork.width,210); assert(!row.artwork.anchor && !row.artwork.form);
        } else if(kind==='historical-login'){
          row.exhibit=await page.locator('main.historical-exhibit').innerText();
          assert.equal(await page.locator('form,input[type=password],input[type=email]').count(),0);
        } else {
          row.title=await page.title();
          row.hidden_labels=await page.locator('.mainNav em').allTextContents();
          assert(row.hidden_labels.includes('Game Guide'));
        }
      }
      row.failed_without_success=failed.filter(r=>r.error!=='net::ERR_ABORTED'||!successful.has(r.url));
      rows.push(row);
      fs.writeFileSync(path.join(__dirname,'v40-browser-r2-progress.json'),JSON.stringify({accepted:false,last_kind:kind,rows},null,2)+'\n');
      assert.equal(errors.length,0,kind+': script error');
      assert.equal(row.failed_without_success.length,0,kind+': failed without successful response '+JSON.stringify(row.failed_without_success));
      assert.equal(responses.length,0,kind+': HTTP error');
      await page.close();
    }
    assert.equal(external.length,0);
    const result={accepted:true,started_utc:started,finished_utc:new Date().toISOString(),base_url:BASE,version:'v40',
      external_requests:external,loopback_request_count:requests.length,swf_requests:requests.filter(u=>u.includes('.swf')),rows};
    fs.writeFileSync(path.join(__dirname,'v40-browser-r2-result.json'),JSON.stringify(result,null,2)+'\n');
    console.log(JSON.stringify({accepted:true,pages:rows.length,external_requests:external.length,loopback_requests:requests.length}));
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
