// Actual local Chrome checks of the changed banner and retained guide controls.
const fs=require('fs'), path=require('path'), assert=require('assert'), crypto=require('crypto');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'), port=Number(process.argv[2]||24783);
const origin=`http://127.0.0.1:${port}`, base=origin+'/WOW-Encyclopedia-Deployable-Archive';
const out=path.join(__dirname,'root-v53-browser-acceptance.json');
for(const k of ['TEMP','TMP','TMPDIR']) process.env[k]=path.join(root,'.scratch/test-temp-20261022');
fs.mkdirSync(process.env.TEMP,{recursive:true});
(async()=>{
 const started=new Date().toISOString(), external=[], errors=[], httpErrors=[];
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext({serviceWorkers:'block',viewport:{width:1450,height:1050}});
 await context.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin===origin||['data:','blob:','about:'].includes(u.protocol))return r.continue();external.push(r.request().url());return r.abort();});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));page.on('response',r=>{if(r.status()>=400)httpErrors.push({url:r.url(),status:r.status()})});
 const report={schema:'wow-root-v53-browser-acceptance/v1',accepted:false,started_utc:started,pages:[]};
 try{
  let response=await page.goto(base+'/burningcrusade/townhall/professions.html',{waitUntil:'load',timeout:60000});assert.equal(response.status(),200);
  const banner=page.locator('img[src*="/__offline/related-guide-images/professions-page-title.png"]');
  await banner.waitFor({state:'attached',timeout:15000});
  const bannerInfo=await banner.evaluate(async el=>{await el.decode();const b=el.getBoundingClientRect();return{src:el.getAttribute('src'),naturalWidth:el.naturalWidth,naturalHeight:el.naturalHeight,width:b.width,height:b.height,x:b.x,y:b.y,complete:el.complete}});
  assert.equal(bannerInfo.naturalWidth,324);assert.equal(bannerInfo.naturalHeight,72);assert(bannerInfo.width>0&&bannerInfo.height>0);
  const payload=await context.request.get(origin+bannerInfo.src);assert.equal(payload.status(),200);const bytes=await payload.body();
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),'33caa0898bfce8e5d6e92e3bfca2cd5505c3784316b36e800ed0a3069e8e2a8b');
  const notice=page.locator('#__offline-related-guide-images');assert.equal(await notice.count(),1);assert(await notice.isVisible());
  assert.equal(await notice.locator('a').getAttribute('href'),'https://archivecraft.com/burningcrusade/townhall/professions/');
  await page.screenshot({path:path.join(__dirname,'professions-v53.png'),fullPage:false});
  const chapters=[];
  for(const n of [1,2,3,0]){await page.locator('#link'+n).click();await page.waitForTimeout(160);chapters.push({chapter:n,visible:await page.locator('#link'+n).isVisible(),banner_visible:await banner.isVisible()});}
  const missing=await page.locator('img[src*="missing-image"],img[data-offline-missing]').evaluateAll(nodes=>nodes.map(n=>({src:n.getAttribute('src'),target:n.getAttribute('data-offline-missing')})));
  assert(!missing.some(i=>(i.src||'').includes('page-title.png')||(i.target||'').includes('professions/page-title.png')));
  report.pages.push({route:'/burningcrusade/townhall/professions.html',status:200,banner:bannerInfo,payload_bytes:bytes.length,notice_visible:true,chapters,remaining_image_placeholders:missing});
  response=await page.goto(base+'/burningcrusade/townhall/bestiary.html',{waitUntil:'load',timeout:60000});assert.equal(response.status(),200);
  await page.locator('a[href="javascript:moveItem(0);"]').click();await page.waitForTimeout(300);
  const broken=await page.locator('img[src*="/__offline/related-guide-images/thumb-thebroken.jpg"]').evaluateAll(async nodes=>Promise.all(nodes.map(async n=>{await n.decode();return{src:n.getAttribute('src'),width:n.naturalWidth,height:n.naturalHeight,visible:!!(n.getBoundingClientRect().width&&n.getBoundingClientRect().height)}})));
  assert(broken.length>=1&&broken.every(x=>x.width===237&&x.height===184));
  report.pages.push({route:'/burningcrusade/townhall/bestiary.html',status:200,retained_broken_images:broken});
  response=await page.goto(base+'/info/basics/dungeons.html',{waitUntil:'load',timeout:60000});assert.equal(response.status(),200);
  const deadmines=await page.locator('img[src*="/screenshots/images/basics/dungeons/"]').evaluateAll(async nodes=>Promise.all(nodes.map(async n=>{await n.decode();return{src:n.getAttribute('src'),width:n.naturalWidth,height:n.naturalHeight}})));
  assert.equal(deadmines.length,10);assert(deadmines.every(x=>x.width>0&&x.height>0));
  report.pages.push({route:'/info/basics/dungeons.html',status:200,retained_previews:deadmines});
  assert.equal(errors.length,0);assert.equal(external.length,0);assert.equal(httpErrors.length,0);report.accepted=true;
 }catch(e){report.failure=String(e);throw e;}
 finally{report.finished_utc=new Date().toISOString();report.external_requests=external;report.page_errors=errors;report.http_errors=httpErrors;fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');await context.close();await browser.close();console.log(JSON.stringify({accepted:report.accepted,pages:report.pages.length,failure:report.failure||null}));}
})().catch(e=>{console.error(e);process.exitCode=1});
