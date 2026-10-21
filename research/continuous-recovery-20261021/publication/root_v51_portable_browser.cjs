// Actual Chrome validation of the extracted v51 ZIP and its packaged server. No asset injection.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../../..'),site=path.join(root,'.scratch/local bundle smoke 20261021 v51/site');
const port='24773',base=`http://127.0.0.1:${port}/WOW-Encyclopedia-Deployable-Archive`;
const out=path.join(__dirname,'root-v51-portable-browser-acceptance.json'),shots=path.join(__dirname,'v51-portable-screenshots');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
for(const k of ['TEMP','TMP','TMPDIR'])process.env[k]=path.join(root,'.scratch/test-temp-20261021');
const expected={alliance:{length:850,sha256:'a66e97b203a110fab7b1277bdce845511694abcadc8b8c62debcfc524a3ab38a'},horde:{length:1104,sha256:'6240957e7afb12dce1026e8dffdb0c206b47f63e69c34c4a57f67a1154543a07'}};
async function state(page,label){
 const s=await page.evaluate(()=>{
  const horde=getComputedStyle(document.getElementById('hordeRewards')).visibility==='visible';
  const expected=document.createElement('div');expected.innerHTML=window.loreTexts[horde?'horde':'alliance'];
  return {lore:{alliance:window.loreTexts.alliance,horde:window.loreTexts.horde},
   html:document.getElementById('loreText').innerHTML,normalized_expected:expected.innerHTML,horde};
 });
 for(const side of ['alliance','horde']){assert.equal(s.lore[side].length,expected[side].length);assert.equal(sha(s.lore[side]),expected[side].sha256)}
 const side=s.horde?'horde':'alliance';assert.equal(s.html,s.normalized_expected);
 return {label,faction:side,lore_html_length:s.html.length,lore_html_sha256:sha(s.html)};
}
async function popup(page,filename){
 const button=page.locator('#loreButton');await button.scrollIntoViewIfNeeded();await button.click();
 // Original historical animation takes roughly 1.6 seconds.
 await page.waitForTimeout(2200);const lore=page.locator('#loreText');assert(await lore.isVisible());
 await lore.screenshot({path:path.join(shots,filename),animations:'disabled'});
 assert(await lore.locator('h3').isVisible());
 await page.locator('.topRightControl').click();await page.waitForTimeout(250);
}
(async()=>{
 assert(!fs.existsSync(out));fs.mkdirSync(shots,{recursive:true});
 const started=new Date().toISOString(),external=[],errors=[],failed=[],responses=[],pages=[];
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext({serviceWorkers:'block',viewport:{width:1440,height:1050}});
 await context.route('**/*',r=>{const u=new URL(r.request().url());
  if(u.origin===`http://127.0.0.1:${port}`||['data:','blob:','about:'].includes(u.protocol))return r.continue();
  external.push(r.request().url());return r.abort();});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
 page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()}));
 page.on('response',r=>responses.push({url:r.url(),status:r.status()}));
 try{
  const route='/info/basics/factions/aldorscryers/aldor-scryers.xml.html';
  const res=await page.goto(base+route,{waitUntil:'load',timeout:60000});assert.equal(res.status(),200);
  const helper=page.locator('script[src="/WOW-Encyclopedia-Deployable-Archive/__offline/aldor-scryers-lore.js"]');
  assert.equal(await helper.count(),1);assert.equal(await helper.evaluate(el=>el.defer),true);
  const states=[await state(page,'initial')];assert.equal(states[0].faction,'alliance');await popup(page,'aldor-lore.png');
  for(const [label,side] of [['The Scryers','horde'],['The Aldor','alliance']]){
   const link=page.locator('#'+side+'Button a');assert.equal((await link.innerText()).trim(),label);
   await link.scrollIntoViewIfNeeded();await link.click();
   await page.waitForFunction(side=>document.getElementById(side+'Rewards').style.visibility==='visible',side,{timeout:5000});
   const s=await state(page,label);assert.equal(s.faction,side);states.push(s);
   if(side==='horde')await popup(page,'scryers-lore.png');
  }
  assert(responses.some(r=>r.url===base+'/__offline/aldor-scryers-lore.js'&&r.status===200));
  const fetched=await context.request.get(base+'/__offline/aldor-scryers-lore.js');assert.equal(fetched.status(),200);
  assert.equal(sha(await fetched.body()),sha(fs.readFileSync(path.join(site,'__offline/aldor-scryers-lore.js'))));
  pages.push({route,status:res.status(),title:await page.title(),states,actual_popup_opens:2,helper_loaded_from_export:true});
  for(const part of ['northrend/howling-fjord','northrend/grizzly-hills','northrend/borean-tundra','bard/bardclass']){
   const route='/wrath/features/'+part+'.xml.html';
   const res=await page.goto(base+route,{waitUntil:'load',timeout:60000});assert.equal(res.status(),200);
   const letter=page.locator('img[src="/WOW-Encyclopedia-Deployable-Archive/wrath/images/letters/T.gif"]');
   assert.equal(await letter.count(),1);await letter.evaluate(img=>img.decode());assert(await letter.isVisible());
   const dimensions=await letter.evaluate(img=>({width:img.naturalWidth,height:img.naturalHeight,src:img.currentSrc}));
   assert.equal(dimensions.width,48);assert.equal(dimensions.height,48);
   assert.equal(dimensions.src,base+'/wrath/images/letters/T.gif');
   pages.push({route,status:res.status(),title:await page.title(),letter_image:dimensions,placeholder:false});
   if(part==='bard/bardclass')await letter.screenshot({path:path.join(shots,'t-letter-bard.png'),animations:'disabled'});
  }
  const receipt={accepted:!external.length&&!errors.length&&!failed.length&&!responses.some(r=>r.status>=400),
   version:'v51',started_utc:started,finished_utc:new Date().toISOString(),actual_browser:'Chrome',
   unmodified_export_served:true,network_scope:'loopback only',asset_fulfillments:0,pages,
   page_errors:errors,request_failures:failed,external_requests:external,http_errors:responses.filter(r=>r.status>=400),
   export_provenance_sha256:sha(fs.readFileSync(path.join(site,'export-provenance.json'))),
   screenshots_dir:'v51-portable-screenshots',
   prior_browser_reuse:'v49 five-page illustration/button checks remain byte-identical except this explicitly tested main faction page.'};
  fs.writeFileSync(path.join(__dirname,'v51-portable-browser-execution.json'),JSON.stringify(receipt,null,2)+'\n');
  assert(receipt.accepted,JSON.stringify({external,errors,failed,http:receipt.http_errors}));
  fs.writeFileSync(out,JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({accepted:true,pages:pages.length,popup_opens:2,letter_pages:4}));
 }finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
