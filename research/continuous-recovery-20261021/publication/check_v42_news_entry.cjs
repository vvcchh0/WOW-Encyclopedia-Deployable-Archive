"use strict";
const fs=require("fs"),path=require("path"),assert=require("assert/strict"),crypto=require("crypto");
const {chromium}=require("C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");
const port=Number(process.argv[2]),origin=`http://127.0.0.1:${port}`,base=origin+"/WOW-Encyclopedia-Deployable-Archive";
(async()=>{
 const result={accepted:false,started_utc:new Date().toISOString(),pageerrors:[],external:[],http_errors:[]};
 const browser=await chromium.launch({headless:true,executablePath:"C:/Program Files/Google/Chrome/Application/chrome.exe"});
 const context=await browser.newContext({viewport:{width:1440,height:1000},serviceWorkers:"block"});
 await context.route("**/*",r=>{const u=new URL(r.request().url());if(u.origin===origin||["data:","blob:","about:"].includes(u.protocol))return r.continue();result.external.push(u.href);return r.abort();});
 try {
  const page=await context.newPage();page.on("pageerror",e=>result.pageerrors.push(String(e)));
  page.on("response",r=>{if(r.status()>=400)result.http_errors.push({url:r.url(),status:r.status()});});
  const response=await page.goto(base+"/news/rss-02-2008.xml.html",{waitUntil:"networkidle"});assert.equal(response.status(),200);
  const entry=page.locator('[id="news2-28-08-583"]');result.initial_class=await entry.getAttribute("class");
  await entry.locator(".hoverContainer").click();
  const link=entry.locator('a[href$="/blizzcast/episode2.html"]').filter({hasText:"check out the transcript"});
  assert(await link.isVisible());result.expanded_class=await entry.getAttribute("class");
  const file=path.join(__dirname,"v42-browser-screenshots/news-blizzcast-expanded.png");await entry.screenshot({path:file});
  const bytes=fs.readFileSync(file);result.screenshot={path:"v42-browser-screenshots/news-blizzcast-expanded.png",bytes:bytes.length,sha256:crypto.createHash("sha256").update(bytes).digest("hex")};
  await link.click();await page.waitForLoadState("networkidle");assert(page.url().endsWith("/blizzcast/episode2.html"));
  result.destination=page.url();result.transcript_blocks=await page.locator("section.transcript-block").count();assert.equal(result.transcript_blocks,31);
  assert.equal(result.pageerrors.length,0);assert.equal(result.external.length,0);assert.equal(result.http_errors.length,0);result.accepted=true;
 } finally {result.finished_utc=new Date().toISOString();await browser.close();fs.writeFileSync(path.join(__dirname,"v42-news-entry-browser-result.json"),JSON.stringify(result,null,2)+"\n");}
 console.log(JSON.stringify(result));
})().catch(e=>{console.error(e.stack||String(e));process.exitCode=1;});
