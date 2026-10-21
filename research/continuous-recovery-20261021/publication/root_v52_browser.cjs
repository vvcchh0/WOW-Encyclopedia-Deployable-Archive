// Actual Chrome checks of the unmodified Arathi guide and all20 restored previews.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../../..'),site=path.join(root,'.scratch/pages-resources-20261021-v52');
const base='http://127.0.0.1:24774/WOW-Encyclopedia-Deployable-Archive',out=path.join(__dirname,'root-v52-browser-acceptance.json');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const review=JSON.parse(fs.readFileSync(path.join(root,'research/continuous-recovery-20261021/local-audit/underdev-final-routing-review/underdev-final-routing-review.json')));
const code=JSON.parse(fs.readFileSync(path.join(__dirname,'root-v52-code-acceptance.json')));
for(const key of ['TEMP','TMP','TMPDIR'])process.env[key]=path.join(root,'.scratch/test-temp-20261021');
(async()=>{
 assert(!fs.existsSync(out));const started=new Date().toISOString(),external=[],errors=[],failed=[],http=[];
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext({serviceWorkers:'block',viewport:{width:1440,height:1050}});
 await context.route('**/*',r=>{const u=new URL(r.request().url());
  if(u.origin==='http://127.0.0.1:24774'||['data:','blob:','about:'].includes(u.protocol))return r.continue();
  external.push(r.request().url());return r.abort();});
 const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
 page.on('requestfailed',r=>failed.push({url:r.url(),error:r.failure()}));
 page.on('response',r=>{if(r.status()>=400)http.push({url:r.url(),status:r.status()})});
 try{
  const route='/pvp/battlegrounds/info-arathi.html',response=await page.goto(base+route,{waitUntil:'load',timeout:60000});
  assert.equal(response.status(),200);assert.equal(await page.evaluate(()=>window.path),'/WOW-Encyclopedia-Deployable-Archive/info/underdev/');
  const checks=[];
  for(const target of review.targets){
   const url=base+target.proposed_intended_route;
   const count=await page.locator(`img[src="/WOW-Encyclopedia-Deployable-Archive${target.proposed_intended_route}"]`).count();
   if(target.route_map_exact_exists){
    assert.equal(count,1,target.filename);const img=page.locator(`img[src="/WOW-Encyclopedia-Deployable-Archive${target.proposed_intended_route}"]`);
    await img.evaluate(el=>el.decode());assert(await img.isVisible());
    const actual=await img.evaluate(el=>({width:el.naturalWidth,height:el.naturalHeight,src:el.currentSrc}));
    const expected=code.existing_decoded_images.find(row=>row.route===target.proposed_intended_route);
    assert.deepEqual([actual.width,actual.height],expected.dimensions);assert.equal(actual.src,url);
    checks.push({route:target.proposed_intended_route,rendered:true,...actual});
   }else{assert.equal(count,0);checks.push({route:target.proposed_intended_route,rendered:false,reason:'exact image remains uncollected'})}
  }
  assert.equal(checks.filter(row=>row.rendered).length,20);assert.equal(checks.filter(row=>!row.rendered).length,2);
  const malformed=await page.locator('img').evaluateAll(nodes=>nodes.map(n=>n.currentSrc||n.src).filter(src=>src.includes('index.htmlimages')));
  assert.deepEqual(malformed,[]);
  const shots=path.join(__dirname,'v52-screenshots');fs.mkdirSync(shots,{recursive:true});
  await page.locator('img[src="/WOW-Encyclopedia-Deployable-Archive/info/underdev/images/arathi/ss5-thumb.jpg"]').screenshot({path:path.join(shots,'arathi-ss5.png')});
  await page.locator('img[src="/WOW-Encyclopedia-Deployable-Archive/info/underdev/images/arathi/ss30-thumb.jpg"]').screenshot({path:path.join(shots,'arathi-ss30.png')});
  const report={accepted:!external.length&&!errors.length&&!failed.length&&!http.length,version:'v52',
   started_utc:started,finished_utc:new Date().toISOString(),actual_browser:'Chrome',asset_fulfillments:0,
   unmodified_export_served:true,network_scope:'loopback only',pages:[{route,status:200,images:checks,restored_previews:20,remaining_previews:2}],
   external_requests:external,page_errors:errors,request_failures:failed,http_errors:http,
   export_provenance_sha256:sha(fs.readFileSync(path.join(site,'export-provenance.json'))),
   prior_browser_reuse:'All other v51 pages, images, scripts and lore helper are verified byte-identical by the full tree acceptance.'};
  fs.writeFileSync(path.join(__dirname,'v52-browser-execution.json'),JSON.stringify(report,null,2)+'\n');
  assert(report.accepted,JSON.stringify({external,errors,failed,http}));fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({accepted:true,pages:1,restored_previews:20,remaining_previews:2}));
 }finally{await context.close();await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
