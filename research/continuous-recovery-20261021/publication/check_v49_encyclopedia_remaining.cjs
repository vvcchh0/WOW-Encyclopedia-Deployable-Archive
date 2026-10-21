// Complete only the three pages not reached by the earlier 49-page audit.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../../..');
for(const k of ['TEMP','TMP','TMPDIR'])process.env[k]=path.join(root,'.scratch/test-temp-20261021');
const base='http://127.0.0.1:24770/WOW-Encyclopedia-Deployable-Archive';
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const site=path.join(root,'.scratch/pages-resources-20261021-v49');
const output=path.join(__dirname,'root-v49-encyclopedia-completion.json');
(async()=>{
 assert(!fs.existsSync(output));
 const started=new Date().toISOString(),pages=[],errors=[],failed=[],external=[],httpErrors=[];
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const context=await browser.newContext({serviceWorkers:'block',viewport:{width:1440,height:1000}});
 await context.route('**/*',r=>{
  const u=new URL(r.request().url());
  if(u.origin==='http://127.0.0.1:24770'||['data:','blob:','about:'].includes(u.protocol))return r.continue();
  external.push(r.request().url());return r.abort();
 });
 const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
 page.on('requestfailed',r=>failed.push({url:r.url(),failure:r.failure()}));
 page.on('response',r=>{if(r.status()>=400)httpErrors.push({url:r.url(),status:r.status()})});
 try{
  for(const id of [350,361,367]){
   const route=`/info/encyclopedia/${id}.xml.html`;
   const response=await page.goto(base+route,{waitUntil:'load',timeout:60000});assert.equal(response.status(),200);
   const record=await page.evaluate(()=>{
    const avatar=document.getElementById('avatarImageContainer');
    const missing=[...document.images].filter(i=>i.currentSrc.includes('missing-image.svg'));
    return {title:document.title,body_text_length:document.body.innerText.length,
     avatar:avatar?{background:getComputedStyle(avatar).backgroundImage,width:avatar.offsetWidth,height:avatar.offsetHeight}:null,
     img_placeholders:missing.length,normal_images:document.images.length,
     zero_natural_images:[...document.images].filter(i=>!i.naturalWidth).length};
   });
   assert(record.title&&record.body_text_length>1000);
   const file=route.slice(1),old=path.join(root,'.scratch/pages-resources-20261021-v48',file);
   assert.equal(sha(fs.readFileSync(path.join(site,file))),sha(fs.readFileSync(old)));
   pages.push({route,status:response.status(),page_bytes_unchanged_from_v48:true,...record});
  }
  const receipt={accepted:!errors.length&&!failed.length&&!external.length&&!httpErrors.length,
   scope:'Three previously uncompleted encyclopedia pages; the preceding 49-page evidence remains a separate v48 run.',
   version:'v49',started_utc:started,finished_utc:new Date().toISOString(),actual_browser:'Chrome',
   asset_fulfillments:0,unmodified_export_served:true,export_provenance_sha256:sha(fs.readFileSync(path.join(site,'export-provenance.json'))),
   pages,page_errors:errors,request_failures:failed,external_requests:external,http_errors:httpErrors};
  fs.writeFileSync(output,JSON.stringify(receipt,null,2)+'\n');assert(receipt.accepted);
  console.log(JSON.stringify({accepted:true,pages:pages.length,known_avatar_placeholders:pages.filter(p=>p.avatar?.background.includes('missing-image.svg')).length}));
 }finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
