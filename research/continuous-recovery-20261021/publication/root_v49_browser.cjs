// Actual Chrome validation of unmodified v49; all resource responses come from the export.
const fs=require('fs'),path=require('path'),assert=require('assert'),crypto=require('crypto');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../../..'),base='http://127.0.0.1:24770/WOW-Encyclopedia-Deployable-Archive';
const site=path.join(root,'.scratch/pages-resources-20261021-v49');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const provSHA=sha(fs.readFileSync(path.join(site,'export-provenance.json')));
const entries=['related-encyclopedia-images','related-guide-images-v49'].flatMap(name=>JSON.parse(fs.readFileSync(path.join(root,`research/continuous-recovery-20261021/integration/${name}/input-map.json`))).entries);
const out=path.join(__dirname,'root-v49-browser-acceptance.json'),shots=path.join(__dirname,'v49-screenshots');
function contrast(a,b){
 const l=rgb=>{const c=rgb.match(/[\d.]+/g).slice(0,3).map(x=>Number(x)/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return c[0]*.2126+c[1]*.7152+c[2]*.0722};
 const x=l(a),y=l(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);
}
(async()=>{
 assert(!fs.existsSync(out));fs.mkdirSync(shots,{recursive:true});
 const started=new Date().toISOString();
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext({serviceWorkers:'block',viewport:{width:1440,height:1050}});
 const external=[],errors=[],failures=[],responses=[];
 await context.route('**/*',route=>{const u=new URL(route.request().url());if(u.origin==='http://127.0.0.1:24770'||['data:','blob:','about:'].includes(u.protocol))return route.continue();external.push(route.request().url());return route.abort();});
 const page=await context.newPage();
 page.on('pageerror',e=>errors.push(String(e)));page.on('requestfailed',r=>failures.push({url:r.url(),error:r.failure()}));page.on('response',r=>responses.push({url:r.url(),status:r.status()}));
 const pages=[];
 try{
  for(const entry of entries){
   const route=entry.page_route+(entry.page_route.endsWith('.xml')?'.html':'');
   const res=await page.goto(base+route,{waitUntil:'load',timeout:20000});assert.equal(res.status(),200);
   if(entry.title==='The Broken'){
     const link=page.getByRole('link',{name:'The Broken',exact:true}).first();await link.scrollIntoViewIfNeeded();await link.click();
   }
   const image=page.locator(`img[src="/WOW-Encyclopedia-Deployable-Archive${entry.route}"]`);await image.waitFor({state:'visible',timeout:7000});await image.evaluate(img=>img.decode());assert.equal(await image.count(),1);
   await image.scrollIntoViewIfNeeded();
   const actual=await image.evaluate(img=>({src:img.currentSrc,width:img.naturalWidth,height:img.naturalHeight,complete:img.complete,rect:{width:img.getBoundingClientRect().width,height:img.getBoundingClientRect().height}}));
   assert.equal(actual.src,base+entry.route);assert(actual.complete);assert.equal(actual.width,entry.width);assert.equal(actual.height,entry.height);assert(actual.rect.width>0&&actual.rect.height>0);
   const note=page.locator('[id^="__offline-related-"][role="note"]').filter({has:page.getByRole('link',{name:'ArchiveCraft',exact:true})});assert.equal(await note.count(),1);
   const source=note.getByRole('link',{name:'ArchiveCraft',exact:true});assert.equal(await source.getAttribute('href'),entry.source_page_url);
   const style=await note.evaluate(el=>({foreground:getComputedStyle(el).color,background:getComputedStyle(el).backgroundColor,height:el.getBoundingClientRect().height}));
   const linkStyle=await source.evaluate(el=>({foreground:getComputedStyle(el).color}));
   assert(contrast(style.foreground,style.background)>=4.5);assert(contrast(linkStyle.foreground,style.background)>=4.5);assert(style.height>=20);
   assert(responses.some(r=>r.url===actual.src&&r.status===200));
   await page.screenshot({path:path.join(shots,path.basename(entry.route)+'.png'),fullPage:true,animations:'disabled'});
   await note.screenshot({path:path.join(shots,path.basename(entry.route)+'-source.png'),animations:'disabled'});
   pages.push({route,status:res.status(),title:await page.title(),image:actual,source_link:await source.getAttribute('href'),note_style:style,source_link_contrast:contrast(linkStyle.foreground,style.background),source_text_contrast:contrast(style.foreground,style.background)});
  }
  const route='/info/basics/factions/aldorscryers/aldor-scryers.xml.html';
  const res=await page.goto(base+route,{waitUntil:'load',timeout:20000});assert.equal(res.status(),200);
  const reward={route,status:res.status(),states:[]};
  for(const [label,side,other] of [['The Scryers','horde','alliance'],['The Aldor','alliance','horde']]){
    const link=page.getByText(label,{exact:true}).first();await link.scrollIntoViewIfNeeded();await link.click();await page.waitForTimeout(150);
    const state=await page.evaluate(()=>({alliance:{visibility:getComputedStyle(document.getElementById('allianceRewards')).visibility,background:getComputedStyle(document.getElementById('allianceButton')).backgroundImage},horde:{visibility:getComputedStyle(document.getElementById('hordeRewards')).visibility,background:getComputedStyle(document.getElementById('hordeButton')).backgroundImage},lore:document.getElementById('loreText').innerText}));
    assert.equal(state[side].visibility,'visible');assert.equal(state[other].visibility,'hidden');
    assert(state.alliance.background.includes(base+'/info/basics/factions/rewardstable/images/button-alliance.jpg'));
    assert(state.horde.background.includes(base+'/info/basics/factions/rewardstable/images/button-horde.jpg'));
    reward.states.push({click:label,...state});
  }
  reward.lore_panel_not_populated=reward.states.every(state=>state.lore==='undefined');
  for(const side of ['alliance','horde'])assert(responses.some(r=>r.url===base+`/info/basics/factions/rewardstable/images/button-${side}.jpg`&&r.status===200));
  assert(!responses.some(r=>r.url.includes('/aldorscryers/images/button-')));
  await page.locator('#allianceButton').screenshot({path:path.join(shots,'aldor-button.png'),animations:'disabled'});
  pages.push(reward);
  const scriptPath='info/basics/factions/rewardstable/scripts/rewardstable-new.js';
  const fetched=await context.request.get(base+'/'+scriptPath);assert.equal(fetched.status(),200);assert.equal(sha(await fetched.body()),sha(fs.readFileSync(path.join(site,scriptPath))));
  const receipt={accepted:errors.length===0&&failures.length===0&&external.length===0,version:'v49',started_utc:started,finished_utc:new Date().toISOString(),actual_browser:'Chrome',unmodified_export_served:true,network_scope:'loopback only',asset_fulfillments:0,pages,page_errors:errors,request_failures:failures,external_requests:external,http_errors:responses.filter(r=>r.status>=400),screenshots_dir:'v49-screenshots',export_provenance_sha256:provSHA,reward_script_bytes_served_unchanged:true};
  fs.writeFileSync(path.join(__dirname,'v49-browser-execution.json'),JSON.stringify(receipt,null,2)+'\n');assert(receipt.accepted,JSON.stringify({errors,failures,external}));
  fs.writeFileSync(out,JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify({accepted:true,pages:pages.length,http_errors:receipt.http_errors.length}));
 }finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
