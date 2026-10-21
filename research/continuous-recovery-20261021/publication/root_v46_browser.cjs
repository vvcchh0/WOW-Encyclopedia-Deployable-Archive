// Observe the unmodified v46 export in Chrome. Only real loopback bytes are served.
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../../..');
const port = '24766';
const base = `http://127.0.0.1:${port}/WOW-Encyclopedia-Deployable-Archive`;
const output = path.join(__dirname, 'root-v46-browser-acceptance.json');
const attempt = path.join(__dirname, 'v46-browser-attempt3.json');
const shots = path.join(__dirname, 'v46-screenshots');
const classes = ['druid','hunter','mage','paladin','priest','rogue','shaman','warlock','warrior'];
const names = ['icon-over-grey','icon-over-green','icon-over-yellow','reset','resetall','printableversion'];
const borders = ['bot-left','bot-right','bot','left','right','top-left','top-right','top'];
const temp = path.join(root, '.scratch/test-temp-20261021');
for (const key of ['TMP','TEMP','TMPDIR']) process.env[key] = temp;
async function state(page) {
  return page.evaluate(() => {
    const prefix = '/WOW-Encyclopedia-Deployable-Archive';
    const images = [...document.images].map(img => ({url:img.currentSrc||img.src,width:img.naturalWidth,height:img.naturalHeight,complete:img.complete}));
    const missing = images.filter(r=>r.url.includes('/__offline/missing-image.svg')).map(r=>{
      const u = new URL(r.url); let value = u.searchParams.get('requested') || '';
      for(let i=0;i<4;i++){try{const next=decodeURIComponent(value);if(next===value)break;value=next;}catch{break;}}
      try {const p=new URL(value,document.baseURI).pathname;return p.startsWith(prefix+'/')?p.slice(prefix.length):p;} catch{return value;}
    });
    const backgrounds = [...document.querySelectorAll('td')].map(td=>getComputedStyle(td).backgroundImage).filter(v=>v.includes('/info/classes/includes-new/images/bot-box/'));
    const overlay = id => {const el=document.getElementById(id);if(!el)return null;const r=el.getBoundingClientRect();return {visible:getComputedStyle(el).display!=='none'&&r.width>0&&r.height>0,url:el.currentSrc||el.src,width:el.naturalWidth,height:el.naturalHeight};};
    return {points:window.rankPoints,first_rank:Number(window.rankTop?.[0]?.[0]),max_rank:Number(window.talent?.[0]?.[2]),
      ui_images:images.filter(r=>r.url.includes('/__offline/related-talent-ui/')),
      missing_paths:[...new Set(missing)].sort(),point_box_backgrounds:[...new Set(backgrounds)].sort(),
      point_box_images:images.filter(r=>r.url.includes('/info/classes/includes-new/images/bot-box/')),
      overlays:{grey:overlay('iconOverGrey0'),green:overlay('iconOverGreen0'),yellow:overlay('iconOverYellow0')},
      notice_text:document.getElementById('__offline-related-talent-icons')?.innerText,
      notice_links:[...document.querySelectorAll('#__offline-related-talent-icons a')].map(a=>a.href)};
  });
}
(async()=>{
  assert(!fs.existsSync(output)&&!fs.existsSync(attempt));fs.mkdirSync(shots,{recursive:true});
  const started=new Date().toISOString();
  const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',
    args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run','--no-default-browser-check']});
  const context=await browser.newContext({viewport:{width:1440,height:1050},serviceWorkers:'block'});
  const external=[],failed=[],errors=[],responses=[],results=[];
  await context.route('**/*',route=>{const u=new URL(route.request().url());if((u.hostname==='127.0.0.1'&&u.port===port)||['data:','blob:','about:'].includes(u.protocol))return route.continue();external.push(route.request().url());return route.abort();});
  context.on('page',p=>{p.on('pageerror',e=>errors.push(String(e)));p.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()}));p.on('response',r=>responses.push({url:r.url(),status:r.status(),mime:r.headers()['content-type']}));});
  let failure=null;
  try {
    for(const name of classes){
      const page=await context.newPage();
      const response=await page.goto(`${base}/info/classes/${name}/talents.html`,{waitUntil:'load',timeout:20000});assert.equal(response.status(),200);
      await page.waitForFunction(()=>window.rankPoints===61&&document.querySelector('img[onclick*="rankTopOnClick(0)"]'));
      await page.waitForTimeout(150);
      const row={class_name:name,states:{initial:await state(page)},printable_clicked:false};
      results.push(row);
      assert.equal(row.states.initial.first_rank,0);assert.equal(row.states.initial.points,61);
      assert(row.states.initial.notice_text.includes('later WotLK 3.3.5a calculator backup'));
      for(const href of row.states.initial.notice_links)assert([base+'/__offline/related-talent-icons.json',base+'/__offline/related-talent-ui.json'].includes(href));
      for(const file of names){const images=row.states.initial.ui_images.filter(r=>r.url===base+'/__offline/related-talent-ui/'+file+'.png');assert(images.length>0,file);assert(images.every(r=>r.complete&&r.width>0&&r.height>0),file);}
      for(const file of borders)assert([...row.states.initial.point_box_backgrounds,...row.states.initial.point_box_images.map(r=>r.url)].some(url=>url.includes('/'+file+'.gif')),name+':'+file);
      const first=page.locator('img[onclick*="rankTopOnClick(0)"]').first();await first.click();
      row.states.first=await state(page);assert.equal(row.states.first.first_rank,1);assert.equal(row.states.first.points,60);
      for(let i=1;i<row.states.initial.max_rank;i++)await first.click();
      row.states.full=await state(page);assert.equal(row.states.full.first_rank,row.states.initial.max_rank);
      if(['druid','hunter','warrior'].includes(name)){
        await page.mouse.move(10,10);await page.screenshot({path:path.join(shots,name+'-max.png'),fullPage:true,animations:'disabled'});
        const popupPromise=context.waitForEvent('page',{timeout:5000});await page.locator('a[onclick*="printableVersion"]').first().click();
        const popup=await popupPromise;await popup.waitForLoadState('load');row.printable_text=(await popup.locator('body').innerText()).replace(/\s+/g,' ').slice(0,350);assert(row.printable_text.length>20);row.printable_clicked=true;await popup.close();
      }
      await page.locator('#hideReset0').click();row.states.reset=await state(page);assert.equal(row.states.reset.points,61);assert.equal(row.states.reset.first_rank,0);
      await first.click();await page.locator('a[onclick*="resetTreeAll"]').first().click();row.states.reset_all=await state(page);assert.equal(row.states.reset_all.points,61);assert.equal(row.states.reset_all.first_rank,0);
      await page.close();
    }
    for(const file of names)assert(responses.some(r=>r.url===base+'/__offline/related-talent-ui/'+file+'.png'&&r.status===200&&r.mime.startsWith('image/png')),file+' actual served PNG');
    for(const file of borders)assert(responses.some(r=>r.url===base+'/info/classes/includes-new/images/bot-box/'+file+'.gif'&&r.status===200),file+' actual served GIF');
    assert.equal(errors.length,0);assert.equal(failed.length,0);assert.equal(external.length,0);
  }catch(e){failure=String(e.stack||e);}
  const receipt={schema:'wow-root-browser-acceptance/v2',accepted:failure===null,version:'v46',started_utc:started,finished_utc:new Date().toISOString(),actual_browser:'Chrome',unmodified_export_served:true,asset_fulfillments:0,network_scope:'loopback only',pages:results,page_errors:errors,request_failures:failed,external_requests:external,http_errors:responses.filter(r=>r.status>=400),served_supplement_objects:responses.filter(r=>r.url.includes('/related-talent-ui/')||r.url.includes('/includes-new/images/bot-box/')),screenshots_dir:'v46-screenshots',failure};
  fs.writeFileSync(attempt,JSON.stringify(receipt,null,2)+'\n');
  await context.close();await browser.close();
  assert(receipt.accepted,failure);assert.equal(results.length,9);fs.writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');
  console.log(JSON.stringify({accepted:true,classes:9,printable_pages:results.filter(r=>r.printable_clicked).length,known_http_error_paths:new Set(receipt.http_errors.map(r=>r.url)).size}));
})().catch(e=>{console.error(e);process.exitCode=1;});
