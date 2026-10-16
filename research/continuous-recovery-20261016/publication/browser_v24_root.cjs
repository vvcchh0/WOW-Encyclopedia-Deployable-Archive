// Root acceptance of new originals through rendered historical pages.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=process.cwd(),site=path.join(root,'.scratch/pages-resources-20261016-v24');
const out=path.join(root,'research/continuous-recovery-20261016/publication');
const prefix='/WOW-Encyclopedia-Deployable-Archive',origin='http://127.0.0.1:29024',base=origin+prefix+'/';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const receipts=['root-news-content02-source-acceptance.json','root-news-content03-source-acceptance.json'].filter(n=>fs.existsSync(path.join(out,n)));
const inputs=receipts.flatMap(n=>{const d=JSON.parse(fs.readFileSync(path.join(out,n)));if(!d.accepted)throw Error(n);return d.accepted_images;});
const shotPages=new Set();
const news=fs.readdirSync(path.join(site,'news')).filter(n=>n.endsWith('.html'));
const report={checked_utc:new Date().toISOString(),accepted:false,checks:[],errors:[],external_requests:[],screenshots:[]};
function check(name,accepted,detail={}){report.checks.push({name,accepted,...detail});if(!accepted)throw Error(name+': '+JSON.stringify(detail));}
const server=http.createServer((req,res)=>{
  let rel;try{const u=new URL(req.url,origin);if(!u.pathname.startsWith(prefix+'/'))throw Error();rel=decodeURIComponent(u.pathname.slice(prefix.length+1));}catch{res.writeHead(400);return res.end();}
  const file=path.resolve(site,rel);if(!file.startsWith(site+path.sep)||!['GET','HEAD'].includes(req.method)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);return res.end();}
  const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.css':'text/css','.gif':'image/gif','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml'}[path.extname(file)]||'application/octet-stream';
  res.writeHead(200,{'content-type':mime});if(req.method==='HEAD')return res.end();fs.createReadStream(file).pipe(res);
});
(async()=>{let browser;try{
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(29024,'127.0.0.1',resolve);});
 browser=await chromium.launch({headless:true});const context=await browser.newContext({viewport:{width:1400,height:1000}});
 await context.route('**/*',route=>{const q=route.request();if(new URL(q.url()).origin===origin&&['GET','HEAD'].includes(q.method()))return route.continue();report.external_requests.push({url:q.url(),method:q.method()});return route.abort();});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
 for(const item of inputs){
  const route=new URL(item.original).pathname;
  const fetched=await context.request.get(origin+prefix+route),bytes=await fetched.body();
  check('original bytes served',fetched.status()===200&&bytes.length===item.length&&sha(bytes)===item.sha256,{route,bytes:bytes.length,sha256:sha(bytes)});
  if(!route.startsWith('/news/'))continue;
  const name=news.find(n=>fs.readFileSync(path.join(site,'news',n),'utf8').includes(prefix+route));if(!name)throw Error('No page for '+route);
  const response=await page.goto(base+'news/'+name,{waitUntil:'networkidle'});check('news page',response.status()===200,{page:name});
  const img=page.locator('img[src$="'+route+'"]').first();check('new news image exists',await img.count()===1,{route,page:name});
  if(!await img.isVisible()){
   const id=await img.evaluate(el=>{let p=el;while(p&&!/^news\d/.test(p.id||''))p=p.parentElement;return p?.id?.slice(4);});
   if(id)await page.evaluate(id=>window.toggleEntry(id),id);
  }
  await img.scrollIntoViewIfNeeded();await img.waitFor({state:'visible'});
  const handle=await img.elementHandle();await page.waitForFunction(el=>el.complete&&el.naturalWidth>0,handle);
  const state=await img.evaluate(el=>({src:el.currentSrc,width:el.naturalWidth,height:el.naturalHeight}));
  check('new news image visible',state.width===item.dimensions[0]&&state.height===item.dimensions[1],{route,state});
  if(!shotPages.has(name)){shotPages.add(name);const f=path.join(out,'v24-root-news-'+name+'.png');await page.screenshot({path:f,fullPage:false});report.screenshots.push(path.relative(root,f).replaceAll('\\','/'));}
 }
 await page.goto(base+'news/rss-08-2007.xml.html',{waitUntil:'networkidle'});
 const august=page.locator('img[src*="/news/images/07-08/"]');
 check('August all27 image elements restored',await august.count()===27,{count:await august.count()});
 for(const img of await august.all())check('August image decoded',await img.evaluate(el=>el.complete&&el.naturalWidth>0),{src:await img.getAttribute('src')});
 await page.screenshot({path:path.join(out,'v24-root-august.png'),fullPage:false});report.screenshots.push('research/continuous-recovery-20261016/publication/v24-root-august.png');
 await page.goto(base+'pvp/worldpvp/cityattacks-gallery.html',{waitUntil:'networkidle'});
 check('City three previews retained',await page.locator('.offline-guide-preview-section img').count()===3);
 const before=(await page.locator('#pageNum').innerText()).trim();await page.locator('a[href="javascript:galleryNext();"]').first().click();
 await page.waitForFunction(v=>document.getElementById('pageNum').innerText.trim()!==v,before);check('gallery pagination retained',true);
 const encyclopedia=await page.goto(base+'info/encyclopedia/index.xml.html',{waitUntil:'networkidle'});check('encyclopedia retained',encyclopedia.status()===200&&(await page.content()).includes('Warcraft Encyclopedia'));
 for(const [route,count] of [['info/events/loveisintheair/gallery.html',10],['info/events/lunarnewyears/gallery.html',10],['pvp/worldpvp/worldpvp-gallery.html',12]]){await page.goto(base+route,{waitUntil:'networkidle'});const imgs=page.locator('.offline-guide-image-collection img');check('guide collection retained',await imgs.count()===count,{route,count:await imgs.count()});const first=imgs.first();await first.scrollIntoViewIfNeeded();await page.waitForFunction(el=>el.complete&&el.naturalWidth>0,await first.elementHandle());check('guide original decoded',true,{route});}
 check('no external requests',report.external_requests.length===0);check('no page errors',report.errors.length===0);report.accepted=true;
}catch(e){report.errors.push(e.stack||String(e));}finally{
 if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));report.finished_utc=new Date().toISOString();
 const file=path.join(out,'root-v24-browser-acceptance.json');if(fs.existsSync(file))throw Error('Refuse overwrite');fs.writeFileSync(file,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({accepted:report.accepted,checks:report.checks.length,errors:report.errors,external_requests:report.external_requests.length}));if(!report.accepted)process.exitCode=1;
}})();
