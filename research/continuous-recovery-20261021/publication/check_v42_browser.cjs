"use strict";
const fs = require("fs"), path = require("path"), crypto = require("crypto"), assert = require("assert/strict");
const {chromium} = require("C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");
const port = Number(process.argv[2]); assert(port > 0);
const origin = `http://127.0.0.1:${port}`, prefix = "/WOW-Encyclopedia-Deployable-Archive", base = origin + prefix;
const out = path.join(__dirname, "v42-browser-screenshots"); fs.mkdirSync(out, {recursive:true});
const audit = JSON.parse(fs.readFileSync(path.join(__dirname, "../integration/talents/resource-audit/resource-audit.json")));
const expectedMissing = new Set(audit.targets.map(x => x.route));
const result = {accepted:false, started_utc:new Date().toISOString(), site:".scratch/pages-resources-20261021-v42", port,
  talents:[], readers:[], navigation:[], external_requests:[], pageerrors:[], http_errors:[], requestfailed:[], screenshots:[]};
const sha = bytes => crypto.createHash("sha256").update(bytes).digest("hex");
async function shot(page, label) {
  const file = path.join(out,label+".png"); await page.screenshot({path:file}); const data = fs.readFileSync(file);
  result.screenshots.push({path:"v42-browser-screenshots/"+label+".png",bytes:data.length,sha256:sha(data)});
}
function watch(page, label) {
  page.on("pageerror", e=>result.pageerrors.push({label,error:String(e)}));
  page.on("response", r=>{if(r.status()>=400) result.http_errors.push({label,url:r.url(),status:r.status()});});
  page.on("requestfailed",r=>result.requestfailed.push({label,url:r.url(),error:r.failure()?.errorText}));
}
async function talentState(page) {
  return page.evaluate(()=>({available:Number(document.querySelector("#tabPointsAvailable").textContent),
    spent:Number(document.querySelector("#modifyRankPoints").textContent),first:window.rankTop[0][0],
    rendered:document.querySelector("#replaceMeWithTalents").innerHTML.length}));
}
async function readyTalent(page) {
  await page.waitForFunction(()=>typeof rankTop!=="undefined" && rankTop[0] && document.querySelector("#tabPointsAvailable"),null,{timeout:15000});
}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe"});
 const context=await browser.newContext({viewport:{width:1440,height:1000},serviceWorkers:"block"});
 await context.route("**/*",r=>{
   const u=new URL(r.request().url());
   if(u.origin===origin || ["about:","data:","blob:"].includes(u.protocol)) return r.continue();
   result.external_requests.push(u.href); return r.abort();
 });
 try {
  for(const name of ["druid","hunter","mage","paladin","priest","rogue","shaman","warlock","warrior"]){
   const page=await context.newPage();watch(page,name);
   const url=base+`/info/classes/${name}/talents.html`;
   const response=await page.goto(url,{waitUntil:"networkidle",timeout:30000});assert.equal(response.status(),200);
   await readyTalent(page);const before=await talentState(page);assert.equal(before.available,61);assert.equal(before.spent,0);assert(before.rendered>10000);
   await page.locator('img[onclick*="rankTopOnClick"]').first().click({force:true});
   const clicked=await talentState(page);assert.equal(clicked.available,60);assert.equal(clicked.spent,1);assert.equal(clicked.first,1);
   const popupPromise=page.waitForEvent("popup",{timeout:5000});await page.evaluate(()=>saveTheTemplate());
   const popup=await popupPromise;await popup.waitForLoadState("domcontentloaded");
   const savedText=await popup.locator("body").innerText();await popup.close();
   const pattern=new RegExp(prefix+"/info/classes/"+name+"/talents\\.html\\?([0-9]+)");
   const match=savedText.match(pattern);assert(match,name+" local template missing");assert(match[1].startsWith("1"));
   await page.locator("#hideReset0").click({force:true});const reset=await talentState(page);assert.equal(reset.spent,0);assert.equal(reset.available,61);
   await page.goto(origin+match[0],{waitUntil:"networkidle",timeout:30000});await readyTalent(page);
   const restored=await talentState(page);assert.equal(restored.spent,1);assert.equal(restored.available,60);assert.equal(restored.first,1);
   await page.reload({waitUntil:"networkidle",timeout:30000});await readyTalent(page);const reloaded=await talentState(page);assert.equal(reloaded.spent,1);
   if(["druid","shaman","warrior"].includes(name)) await shot(page,"talent-"+name+"-restored");
   result.talents.push({class:name,status:response.status(),before,clicked,reset,template_path:match[0],restored,reloaded});
   await page.close();
  }
  const readerPath="/__offline/related-sites/blizzcast/";
  for(const name of ["index","archive","episode1","episode2","feed"]){
   const page=await context.newPage();watch(page,"reader-"+name);
   const response=await page.goto(base+readerPath+name+".html",{waitUntil:"networkidle",timeout:25000});assert.equal(response.status(),200);
   const blocks=await page.locator("section.transcript-block").count();
   assert.equal(blocks,name==="episode1"?19:name==="episode2"?31:0);
   assert.equal(await page.locator("script,form,input,iframe,object,embed,img,audio,video").count(),0);
   const links=await page.locator("a[href]").evaluateAll(a=>a.map(x=>x.href));
   const checks=[];for(const href of new Set(links)){const u=new URL(href);assert.equal(u.origin,origin);if(u.hash)continue;
    const r=await context.request.get(href);checks.push({path:u.pathname,status:r.status(),known_missing:u.pathname===prefix+"/__offline/missing.html"});assert.equal(r.status(),200);}
   const late=await page.locator(".late-supplement").count();assert.equal(late,["index","archive"].includes(name)?1:0);
   await shot(page,"blizzcast-"+name);
   result.readers.push({name,status:response.status(),blocks,late_supplement:!!late,links:checks});
   if(name==="episode1") {await page.locator('a[href$="/episode2.html"]').first().click();await page.waitForLoadState("networkidle");assert.equal(await page.locator("section.transcript-block").count(),31);result.navigation.push({from:"episode1",to:"episode2",method:"visible anchor click"});}
   await page.close();
  }
  for(const route of ["/downloads/index.html","/news/rss-02-2008.xml.html"]){
   const page=await context.newPage();watch(page,"source-entry"+route);
   const response=await page.goto(base+route,{waitUntil:"networkidle",timeout:25000});assert.equal(response.status(),200);
   const anchors=page.locator('a[href*="/__offline/related-sites/blizzcast/"]');const count=await anchors.count();assert(count>0,route+" no restored entry");
   let clicked=false;for(let i=0;i<count;i++){const a=anchors.nth(i);if(await a.isVisible()){const href=await a.getAttribute("href");await a.click();await page.waitForLoadState("networkidle");assert(page.url().includes(readerPath));result.navigation.push({from:route,to:href,method:"visible original page anchor click"});clicked=true;break;}}
   result.navigation.push({source_page:route,restored_anchors:count,visible_click_tested:clicked});await page.close();
  }
  assert.equal(result.external_requests.length,0);assert.equal(result.pageerrors.length,0);assert.equal(result.requestfailed.length,0);
  const missing=new Set();for(const row of result.http_errors){assert.equal(row.status,404);const u=new URL(row.url);const route=decodeURIComponent(u.pathname.slice(prefix.length));assert(expectedMissing.has(route),row.url);missing.add(route);}
  result.expected_missing_talent_assets=[...missing].sort();result.expected_missing_talent_assets_count=missing.size;
  result.accepted=true;
 } finally {
  result.finished_utc=new Date().toISOString();await browser.close();
  fs.writeFileSync(path.join(__dirname,"v42-browser-result.json"),JSON.stringify(result,null,2)+"\n");
 }
 console.log(JSON.stringify({accepted:result.accepted,talents:result.talents.length,readers:result.readers.length,navigation:result.navigation.length,missing_assets:result.expected_missing_talent_assets_count,external:result.external_requests.length}));
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1;});
