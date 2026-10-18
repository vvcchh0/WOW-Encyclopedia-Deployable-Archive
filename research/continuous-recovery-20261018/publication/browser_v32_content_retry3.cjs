const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=process.cwd(),run=path.join(root,'research/continuous-recovery-20261018'),pub=path.join(run,'publication'),site=path.join(root,'.scratch/pages-resources-20261018-v32');
const origin='http://127.0.0.1:29035',prefix='/WOW-Encyclopedia-Deployable-Archive/',base=origin+prefix;
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),read=p=>JSON.parse(fs.readFileSync(p));
const entries=read(path.join(run,'integration/v32/v32-primary-source-map.json')).items;
const refs=read(path.join(pub,'v32-export-expectations.json')).new_static_marker_references;
const receipt=path.join(pub,'root-v32-content-browser-retry3-acceptance.json');if(fs.existsSync(receipt))throw Error('Preserve receipt');
const report={accepted:false,started_utc:new Date().toISOString(),checks:[],errors:[],external_requests:[],screenshots:[],scope:'All103 new originals served unchanged; news images and other article illustrations exercised on their source pages. Chart backgrounds and dynamic red socket are covered by separate production browser receipts.'};
const started=Date.now();function check(name,ok,data={}){report.checks.push({name,accepted:!!ok,...data});if(!ok)throw Error(name+JSON.stringify(data));if(Date.now()-started>300000)throw Error('Content check deadline');}
const server=http.createServer((req,res)=>{let rel;try{const u=new URL(req.url,origin);if(!u.pathname.startsWith(prefix)||!['GET','HEAD'].includes(req.method))throw Error();rel=decodeURIComponent(u.pathname.slice(prefix.length));}catch{res.writeHead(400);return res.end();}const p=path.resolve(site,rel);if(!p.startsWith(site+path.sep)||!fs.existsSync(p)||!fs.statSync(p).isFile()){res.writeHead(404);return res.end();}res.writeHead(200,{'content-type':({'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.jpg':'image/jpeg','.gif':'image/gif','.png':'image/png','.svg':'image/svg+xml'})[path.extname(p)]||'application/octet-stream'});fs.createReadStream(p).pipe(res);});
(async()=>{let browser;try{
 await new Promise((a,b)=>{server.once('error',b);server.listen(29035,'127.0.0.1',a);});browser=await chromium.launch({headless:true});const context=await browser.newContext({viewport:{width:1550,height:1100}});context.setDefaultTimeout(10000);
 await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();report.external_requests.push(r.request().url());return r.abort();});const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
 check('exact103 distinct originals',entries.length===103&&new Set(entries.map(x=>x.original)).size===103);
 const byOriginal=new Map(entries.map(x=>[x.original,x]));
 for(const item of entries){const rel=new URL(item.original).pathname.slice(1),response=await context.request.get(base+rel),data=await response.body();check('new original bytes served',response.status()===200&&data.length===item.length&&sha(data)===item.sha256&&response.headers()['content-type']===item.mime,{route:rel});}
 const pages=new Map();for(const ref of refs){if(ref.page==='bcattunement/index.html'||ref.original.endsWith('/redsocket.gif'))continue;if(!pages.has(ref.page))pages.set(ref.page,new Set());pages.get(ref.page).add(ref.original);}
 const seen=new Set(),newsSeen=new Set();
 for(const[name,originals]of pages){const response=await page.goto(base+name,{waitUntil:'networkidle'});check('source page opens',response.status()===200,{page:name});
   await page.evaluate(async()=>{if(window.__WOWPages?.ready)await window.__WOWPages.ready;});
   if(name.startsWith('news/')){
     for(const id of await page.locator('[id^="news"][class^="news-collapse"]').evaluateAll(es=>es.map(e=>e.id).filter(id=>/^news\d/.test(id)))){
       const entry=page.locator('[id="'+id+'"]');await entry.locator('.news-toggle a').first().click();
       await page.waitForFunction(id=>document.getElementById(id).className.startsWith('news-expand'),id);
     }
   }
   for(const original of originals){const item=byOriginal.get(original),rel=new URL(original).pathname.slice(1),images=page.locator('img[src$="/'+rel+'"]');
     if(fs.readFileSync(path.join(site,name),'utf8').includes('src="'+prefix+rel+'"'))await images.first().waitFor({state:'attached'});
     if(!report.first_selector_diagnostic)report.first_selector_diagnostic={selector:'img[src$="/'+rel+'"]',count:await images.count(),url:page.url(),original,images:await page.locator('img').evaluateAll(es=>es.map(e=>e.getAttribute('src')).filter(x=>x?.includes('thumb-02')))};
     if(await images.count()){
       let displayed=0;for(let i=0;i<await images.count();i++){let image=images.nth(i);if(!await image.isVisible()){
         const newsId=await image.evaluate(el=>{let p=el;while(p&&!/^news\d/.test(p.id||''))p=p.parentElement;return p?.id||null;});
         if(newsId){const entry=page.locator('[id="'+newsId+'"]');if((await entry.getAttribute('class')||'').startsWith('news-collapse')){await entry.locator('.news-toggle a').first().click();await page.waitForFunction(id=>document.getElementById(id).className.startsWith('news-expand'),newsId);}}
       }
       if(!await image.isVisible())continue;await image.scrollIntoViewIfNeeded();await image.evaluate(el=>el.decode());const dimensions=await image.evaluate(el=>[el.naturalWidth,el.naturalHeight]);check('source image visible and decoded',JSON.stringify(dimensions)===JSON.stringify(item.dimensions),{page:name,route:rel,dimensions});displayed++;}
       check('at least one original image occurrence displayed',displayed>0,{page:name,route:rel,dom_references:await images.count(),displayed});
     }else{
       const backgrounds=await page.evaluate(async route=>{const values=[];for(const el of document.querySelectorAll('*')){const css=getComputedStyle(el),url=css.backgroundImage;if(!url.includes('/'+route))continue;const bounds=el.getBoundingClientRect();if(css.display==='none'||css.visibility==='hidden'||bounds.width<=0||bounds.height<=0)continue;const parsed=url.match(/url\(["']?(.*?)["']?\)/);if(!parsed)continue;const im=new Image();im.src=parsed[1];await im.decode();values.push({tag:el.tagName,id:el.id,url:im.src,dimensions:[im.naturalWidth,im.naturalHeight]});}return values;},rel);
       check('source CSS image visible and decoded',backgrounds.some(x=>x.url===base+rel&&JSON.stringify(x.dimensions)===JSON.stringify(item.dimensions)),{page:name,route:rel,backgrounds});
     }
     seen.add(original);if(name.startsWith('news/'))newsSeen.add(original);
   }
   if(['insider/10/silvermoon.xml.html','insider/11/arena.xml.html','insider/12/magtheridon.xml.html'].includes(name)){const shot='v32-content-'+name.split('/')[2].replace('.xml.html','')+'.png';await page.screenshot({path:path.join(pub,shot)});report.screenshots.push(shot);}
 }
 check('all49 news originals displayed',newsSeen.size===49,{actual:newsSeen.size});check('all93 ordinary source originals displayed',seen.size===93,{actual:seen.size});
 check('no external requests',report.external_requests.length===0);check('no browser errors',report.errors.length===0);report.accepted=true;
}catch(e){report.errors.push(String(e));}finally{report.finished_utc=new Date().toISOString();report.export_provenance_sha256=sha(fs.readFileSync(path.join(site,'export-provenance.json')));fs.writeFileSync(receipt,JSON.stringify(report,null,2)+'\n');if(browser)await browser.close();await new Promise(r=>server.close(r));console.log(JSON.stringify({accepted:report.accepted,checks:report.checks.length,errors:report.errors,external:report.external_requests}));if(!report.accepted)process.exitCode=1;}})();
