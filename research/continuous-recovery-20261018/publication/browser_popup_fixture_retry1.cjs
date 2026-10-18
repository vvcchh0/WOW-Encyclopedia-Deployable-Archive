const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=process.cwd(),pub=path.join(root,'research/continuous-recovery-20261018/publication');
const site=path.join(root,'.scratch/pages-resources-20261018-v30'),fixture=path.join(pub,'runtime-fixture-popup');
const origin='http://127.0.0.1:29032',prefix='/WOW-Encyclopedia-Deployable-Archive/',base=origin+prefix;
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const dest=path.join(pub,'root-popup-fixture-browser-retry1-acceptance.json');
if(fs.existsSync(dest))throw Error('Preserve receipt');
const report={accepted:false,fixture_only:true,network_requests:0,started_utc:new Date().toISOString(),checks:[],errors:[],external_requests:[]};
function check(name,ok,data={}){report.checks.push({name,accepted:!!ok,...data});if(!ok)throw Error(name);}
const server=http.createServer((req,res)=>{let rel;try{const u=new URL(req.url,origin);if(!u.pathname.startsWith(prefix)||!['GET','HEAD'].includes(req.method))throw Error();rel=decodeURIComponent(u.pathname.slice(prefix.length));}catch{res.writeHead(400);return res.end();}const fallback=path.resolve(site,rel),override=path.resolve(fixture,rel),p=fs.existsSync(override)?override:fallback;if(!fallback.startsWith(site+path.sep)||!p.startsWith(root+path.sep)||!fs.existsSync(p)||!fs.statSync(p).isFile()){res.writeHead(404);return res.end();}res.writeHead(200,{'content-type':({'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.jpg':'image/jpeg','.gif':'image/gif','.png':'image/png','.svg':'image/svg+xml'})[path.extname(p)]||'application/octet-stream'});fs.createReadStream(p).pipe(res);});
(async()=>{let browser;try{
 await new Promise((a,b)=>{server.once('error',b);server.listen(29032,'127.0.0.1',a);});
 browser=await chromium.launch({headless:true});const context=await browser.newContext({viewport:{width:1500,height:1000}});context.setDefaultTimeout(10000);
 context.on('page',p=>p.on('pageerror',e=>report.errors.push(String(e))));
 await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();report.external_requests.push(r.request().url());return r.abort();});
 const page=await context.newPage();await page.goto(base+'burningcrusade/townhall/story.html',{waitUntil:'networkidle'});
 await page.locator('#link4').click();await page.waitForFunction(()=>window.currentItem===4);
 const link=page.locator('a[href*="_origins/www.blizzard.com/war3x/images/screens/concept/ss01.jpg"]');
 const [popup]=await Promise.all([context.waitForEvent('page'),link.locator('img').click()]);
 await popup.waitForLoadState('domcontentloaded');check('actual story artwork click opens persistent local image',popup.url()===base+'_origins/www.blizzard.com/war3x/images/screens/concept/ss01.jpg');
 const art=popup.locator('img');await art.evaluate(el=>el.decode());const dimensions=await art.evaluate(el=>[el.naturalWidth,el.naturalHeight]);check('original 750x600 artwork decodes',JSON.stringify(dimensions)==='[750,600]',{dimensions});
 check('image popup has no opener',await popup.evaluate(()=>window.opener===null));await popup.waitForTimeout(1000);check('popup remains open',!popup.isClosed());
 await popup.screenshot({path:path.join(pub,'popup-fixture-story-artwork.png')});await popup.close();
 await page.goto(base+'insider/11/arena.xml.html',{waitUntil:'networkidle'});
 const arena=page.locator('a[href*="popUpOmega"][href*="ss1.jpg"]').first();check('original arena full-size image control exists',await arena.count()===1);
 const [missing]=await Promise.all([context.waitForEvent('page'),arena.locator('img').click()]);await missing.waitForLoadState('domcontentloaded');check('uncollected full-size image opens local missing marker',missing.url().startsWith(base+'__offline/missing-image.svg?'));await missing.close();
 check('no external requests',report.external_requests.length===0);check('no browser errors',report.errors.length===0);report.accepted=true;
}catch(e){report.errors.push(String(e));}finally{report.finished_utc=new Date().toISOString();report.tool_sha256=sha(fs.readFileSync(path.join(root,'tools/export_github_pages.py')));report.fixture_receipt_sha256=sha(fs.readFileSync(path.join(fixture,'fixture-receipt.json')));fs.writeFileSync(dest,JSON.stringify(report,null,2)+'\n');if(browser)await browser.close();await new Promise(r=>server.close(r));console.log(JSON.stringify(report));if(!report.accepted)process.exitCode=1;}})();
