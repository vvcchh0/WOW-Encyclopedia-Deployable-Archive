// Read real local v54 output; no image fulfillment or page mutation.
const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..');
const port=Number(process.argv[2]||24784),origin=`http://127.0.0.1:${port}`;
const base=origin+'/WOW-Encyclopedia-Deployable-Archive';
const map=JSON.parse(fs.readFileSync(path.join(__dirname,'integration/related-faction-icons-v54/input-map.json')));
const pages=[...new Set(map.entries.flatMap(e=>e.page_routes))];
const output=path.join(__dirname,'root-v54-faction-browser-acceptance.json');
for(const k of ['TEMP','TMP','TMPDIR'])process.env[k]=path.join(root,'.scratch/test-temp-20261022');
fs.mkdirSync(process.env.TEMP,{recursive:true});
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext({serviceWorkers:'block',viewport:{width:1450,height:1050}});
 const external=[],errors=[],http=[],pending=[],responses=[];
 const report={schema:'wow-root-v54-faction-browser-acceptance/v1',accepted:false,started_utc:new Date().toISOString(),pages:[],payloads:[],request_fulfillment:false};
 await context.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin===origin||['data:','blob:','about:'].includes(u.protocol))return r.continue();external.push(r.request().url());return r.abort();});
 const page=await context.newPage();
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('response',r=>{
  if(r.status()>=400)http.push({url:r.url(),status:r.status()});
  const entry=map.entries.find(e=>r.url()===base+e.route);
  if(entry)pending.push((async()=>{const body=await r.body();const h=hash(body);assert.equal(r.status(),200);assert.equal(body.length,entry.length);assert.equal(h,entry.sha256);assert(r.headers()['content-type'].startsWith('image/jpeg'));responses.push({url:r.url(),sha256:h,length:body.length,status:r.status()});})());
 });
 try{
  for(const entry of map.entries){
   const r=await context.request.get(base+entry.route);assert.equal(r.status(),200);
   const body=await r.body();assert.equal(body.length,entry.length);assert.equal(hash(body),entry.sha256);
   assert(r.headers()['content-type'].startsWith('image/jpeg'));
   report.payloads.push({route:entry.route,length:body.length,sha256:hash(body),mime:r.headers()['content-type']});
  }
  for(const route of pages){
   const r=await page.goto(base+route+'.html',{waitUntil:'load',timeout:60000});assert.equal(r.status(),200);
   const notice=page.locator('#__offline-related-faction-icons');assert.equal(await notice.count(),1);assert(await notice.isVisible());
   assert((await notice.innerText()).includes('2015'));
   assert.equal(await notice.locator('a').getAttribute('href'),'/WOW-Encyclopedia-Deployable-Archive/__offline/related-faction-icons.json');
   const hasReputation=await page.locator('#slot0 a').count();
   const row={route,status:r.status(),notice_visible:true,brackets:[],remaining_placeholders:[]};
   const groups=[];
   for(const faction of ['alliance','horde']){
    const tab=page.locator('#'+faction+'Button a');
    if(await tab.isVisible()&&(await tab.innerText()).trim())groups.push({faction,click:true});
   }
   if(!groups.length){
    for(const faction of ['alliance','horde'])if(await page.locator('#'+faction+'Rewards').isVisible())groups.push({faction,click:false});
   }
   assert(groups.length>0);row.visible_reward_groups=groups;
   const tiers=hasReputation?await page.evaluate(()=>[0,1,2,3].filter(t=>getComputedStyle(document.querySelector('#slot'+t)).display!=='none')):[0];
   row.available_reputation_tiers=tiers;
   row.original_control_workarounds=[];
   const chooseTier=async t=>{
    if(await page.evaluate(()=>getComputedStyle(document.querySelector('#dropBox')).overflow!=='visible'))await page.locator('.dropDownArrow').click();
    await page.locator('#slot'+t+' a').click();
    await page.waitForFunction(w=>window.levelBracket===w&&window.previousListItem===w,t,{timeout:5000});
   };
   for(const tier of tiers){
    if(hasReputation){
     const initial=await page.evaluate(()=>({levelBracket,previousListItem}));
     if(initial.previousListItem===tier&&initial.levelBracket!==tier){
      const alternate=tiers.find(x=>x!==tier);assert(alternate!==undefined);
      row.original_control_workarounds.push({target:tier,initial,intermediate:alternate,reason:'Historical page initializes levelBracket without updating previousListItem; choose another visible tier first.'});
      await chooseTier(alternate);
     }
     await chooseTier(tier);
     assert.equal(await page.evaluate(()=>levelBracket),tier);
    }
    for(const {faction,click} of groups){
     const tab=page.locator('#'+faction+'Button a');const label=(await tab.innerText()).trim();
     if(click)await tab.click();
     await page.waitForFunction(f=>getComputedStyle(document.querySelector('#'+f+'Rewards')).visibility==='visible',faction,{timeout:5000});
     const table=page.locator('#'+faction+'Rewards');assert(await table.isVisible());
     const values=await table.locator('img[src*="/__offline/related-faction-icons/"]').evaluateAll(async nodes=>Promise.all(nodes.map(async el=>{
      await el.decode();const rect=el.getBoundingClientRect(),cell=el.closest('td').getBoundingClientRect();
      return{src:el.getAttribute('src'),naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight,width:rect.width,height:rect.height,fits_cell:rect.x>=cell.x&&rect.y>=cell.y&&rect.right<=cell.right&&rect.bottom<=cell.bottom};
     })));
     const expected=await page.evaluate(f=>RewardItems.filter(x=>x.playerFaction===f&&x.itemHTML!=='none'&&String(x.itemIcon).includes('/__offline/related-faction-icons/')).length,faction);
     assert.equal(values.length,expected,route+' '+tier+' '+faction);
     for(const v of values){assert.equal(v.naturalWidth,36);assert.equal(v.naturalHeight,36);assert.equal(v.width,36);assert.equal(v.height,36);assert(v.fits_cell);}
     let tooltip=null;
     if(values.length){
      const icon=table.locator('img[src*="/__offline/related-faction-icons/"]').first();
      const link=icon.locator('xpath=..');const itemName=(await link.locator('.style_name').innerText()).trim();
      await link.locator('.style_name').hover();await page.waitForTimeout(80);
      const tip=page.locator('#toolTipBox');assert(await tip.isVisible());tooltip=(await tip.innerText()).replace(/\s+/g,' ').trim();
      assert(tooltip.includes(itemName),route+' tooltip '+itemName);
      await page.mouse.move(5,5);
     }
     row.brackets.push({tier,faction,tab_label:label,icons:values,expected_icons:expected,tooltip_excerpt:tooltip?tooltip.slice(0,200):null});
    }
   }
   row.remaining_placeholders=await page.locator('img[src*="missing-image"],img[data-offline-missing]').evaluateAll(nodes=>nodes.map(n=>({src:n.getAttribute('src'),requested:n.getAttribute('data-offline-missing')})));
   assert(!row.remaining_placeholders.some(v=>map.entries.some(e=>(v.src||'').includes(encodeURIComponent(e.target_route))||(v.requested||'').includes(e.target_route))));
   if(route.includes('aldor-scryers')||route.includes('zangarpvp')){
    await page.locator('#allianceButton a').click();
    await page.locator('#allianceButton').scrollIntoViewIfNeeded();
    const name=route.includes('aldor-scryers')?'aldor':'zangarmarsh';
    await page.screenshot({path:path.join(__dirname,'faction-v54-'+name+'.png')});
   }
   report.pages.push(row);
  }
  await Promise.all(pending);
  const seen=new Set(responses.map(r=>r.url));assert.equal(seen.size,3);
  assert.equal(errors.length,0);assert.equal(external.length,0);assert.equal(http.length,0);
  report.accepted=true;
 }catch(e){report.failure=String(e);throw e;}
 finally{
  await Promise.allSettled(pending);report.finished_utc=new Date().toISOString();report.page_errors=errors;report.external_requests=external;report.http_errors=http;report.actual_image_responses=responses;
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();
  console.log(JSON.stringify({accepted:report.accepted,pages:report.pages.length,actual_image_responses:responses.length,failure:report.failure||null}));
 }
})().catch(e=>{console.error(e);process.exitCode=1});
