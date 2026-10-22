"use strict";
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=process.cwd(), base=path.join(root,'research/continuous-recovery-20261022');
const reportRel='integration/related-talent-icons-v56/implementation/runs/v56-2026-10-22T12-42-28-056Z/browser-check.json';
const source=fs.readFileSync(path.join(base,reportRel));const prior=JSON.parse(source);
assert.strictEqual(prior.status,'browser_checks_passed_pending_parent_review');
const out=path.join(base,'integration/v56-root-visual-recheck');fs.mkdirSync(out,{recursive:false});
const t=path.join(root,'.scratch/test-temp-20261022');process.env.TEMP=t;process.env.TMP=t;process.env.TMPDIR=t;
(async()=>{const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const result={schema:'wow-root-v56-visual-recheck/v1',source_browser_sha256:crypto.createHash('sha256').update(source).digest('hex'),started_utc:new Date().toISOString(),reason:'Two rapid post-allocation captures showed partially painted content; cold saved-template pages are checked after paint settlement.',response_substitutions:0,external_requests:[],page_errors:[],checks:[]};
try{for(const id of ['warrior-improved-thunder-clap','warrior-improved-slam']){
 const row=prior.talent_checks.find(r=>r.mapping_id===id);assert(row && row.status==='passed');
 const u=new URL(row.saved_link.href);assert.strictEqual(u.origin,'http://127.0.0.1:24786');
 const context=await browser.newContext({serviceWorkers:'block',viewport:{width:1480,height:1250},deviceScaleFactor:1});
 await context.route('**/*',route=>{const url=new URL(route.request().url());if(url.origin!==u.origin && !['data:','blob:','about:'].includes(url.protocol)){result.external_requests.push(url.href);return route.abort();}return route.continue();});
 const page=await context.newPage();page.on('pageerror',e=>result.page_errors.push(String(e)));
 await page.goto(u.href,{waitUntil:'networkidle',timeout:30000});
 await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await page.waitForTimeout(1500);
 const image=await page.evaluate(route=>{const img=Array.from(document.images).find(x=>new URL(x.src).pathname.endsWith(route));return img?{complete:img.complete,width:img.naturalWidth,height:img.naturalHeight,src:img.src}:null;},row.on_route);
 assert(image && image.complete && image.width===36 && image.height===36);
 const file=path.join(out,id+'-saved-settled.png');await page.screenshot({path:file,fullPage:false});
 result.checks.push({mapping_id:id,saved_template_url:u.href,expected_digits:row.saved_link.digits,active_image:image,screenshot:path.relative(root,file).split(path.sep).join('/'),screenshot_sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')});
 await context.close();
}assert.strictEqual(result.external_requests.length,0);assert.strictEqual(result.page_errors.length,0);result.automated_checks_passed=true;result.manual_visual_review_pending=true;
}finally{await browser.close();result.finished_utc=new Date().toISOString();fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(result,null,2)+'\n');}
console.log(JSON.stringify({automated_checks_passed:result.automated_checks_passed,checks:result.checks.length}));})().catch(e=>{console.error(e);process.exitCode=1;});
