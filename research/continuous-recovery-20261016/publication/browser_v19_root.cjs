// Root runtime acceptance: actual visible images, HTTP bytes and retained gallery.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=process.cwd(),site=path.join(root,'.scratch/pages-resources-20261016-v19');
const out=path.join(root,'research/continuous-recovery-20261016/publication');
const prefix='/WOW-Encyclopedia-Deployable-Archive',origin='http://127.0.0.1:29015',base=origin+prefix+'/';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const inputs=JSON.parse(fs.readFileSync(path.join(root,'research/continuous-recovery-20261016/integration/v19-primary-news-source-map.json'))).items.slice(-10);
const news=fs.readdirSync(path.join(site,'news')).filter(n=>n.endsWith('.html'));
const report={checked_utc:new Date().toISOString(),accepted:false,checks:[],errors:[],external_requests:[],screenshots:[]};
function check(name,accepted,detail={}) {report.checks.push({name,accepted,...detail});if(!accepted)throw Error(name+': '+JSON.stringify(detail));}
const server=http.createServer((req,res)=>{
  let rel;try{const u=new URL(req.url,origin);if(!u.pathname.startsWith(prefix+'/'))throw Error();rel=decodeURIComponent(u.pathname.slice(prefix.length+1));}catch{res.writeHead(400);return res.end();}
  const file=path.resolve(site,rel);if(!file.startsWith(site+path.sep)||!['GET','HEAD'].includes(req.method)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);return res.end();}
  const mime={'.html':'text/html','.js':'text/javascript','.json':'application/json','.css':'text/css','.gif':'image/gif','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml'}[path.extname(file)]||'application/octet-stream';
  res.writeHead(200,{'content-type':mime});if(req.method==='HEAD')return res.end();fs.createReadStream(file).pipe(res);
});
(async()=>{let browser;try{
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(29015,'127.0.0.1',resolve);});
  browser=await chromium.launch({headless:true});const context=await browser.newContext({viewport:{width:1400,height:1000}});
  await context.route('**/*',route=>{const q=route.request();if(new URL(q.url()).origin===origin&&['GET','HEAD'].includes(q.method()))return route.continue();report.external_requests.push({url:q.url(),method:q.method()});return route.abort();});
  const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
  for(const item of inputs){
    const route=new URL(item.logical_url).pathname;
    const preferred=route.includes('news-sc2')?'rss-05-2007.xml.html':route.includes('blizzconlogo')?'wow-news-06-2005.html':null;
    const name=preferred||news.find(n=>fs.readFileSync(path.join(site,'news',n),'utf8').includes(prefix+route));
    if(!name)throw Error('No news page for '+route);
    const response=await page.goto(base+'news/'+name,{waitUntil:'networkidle'});check('news page',response.status()===200,{page:name});
    let img=page.locator('img').filter({visible:true});
    const selector='img[src$="'+route+'"]';img=page.locator(selector).first();
    check('news image exists',await img.count()===1,{route,page:name});
    if(!await img.isVisible()){
      const id=await img.evaluate(el=>{let p=el;while(p&&!/^news\d/.test(p.id||''))p=p.parentElement;return p?.id?.slice(4);});
      if(id)await page.evaluate(id=>window.toggleEntry(id),id);
    }
    await img.scrollIntoViewIfNeeded();await img.waitFor({state:'visible'});
    const handle=await img.elementHandle();await page.waitForFunction(el=>el.complete&&el.naturalWidth>0,handle);
    const state=await img.evaluate(el=>({src:el.currentSrc,width:el.naturalWidth,height:el.naturalHeight}));
    const fetched=await context.request.get(state.src),bytes=await fetched.body();
    check('visible original bytes',fetched.status()===200&&bytes.length===item.length&&sha(bytes)===item.sha256&&state.width===item.dimensions[0]&&state.height===item.dimensions[1],{route,state,bytes:bytes.length,sha256:sha(bytes)});
    if(route.includes('news-sc2')||route.includes('blizzconlogo')){const name=path.basename(route)+'.png';await img.screenshot({path:path.join(out,'v19-root-'+name)});report.screenshots.push('research/continuous-recovery-20261016/publication/v19-root-'+name);}
  }
  await page.goto(base+'pvp/worldpvp/cityattacks-gallery.html',{waitUntil:'networkidle'});
  check('City previews retained',await page.locator('.offline-guide-preview-section img').count()===3);
  const before=(await page.locator('#pageNum').innerText()).trim();await page.locator('a[href="javascript:galleryNext();"]').first().click();
  await page.waitForFunction(v=>document.getElementById('pageNum').innerText.trim()!==v,before);
  check('native gallery pagination retained',(await page.locator('#pageNum').innerText()).trim()!==before);
  const encyclopedia=await page.goto(base+'info/encyclopedia/index.xml.html',{waitUntil:'networkidle'});
  check('encyclopedia retained',encyclopedia.status()===200&&(await page.content()).includes('Warcraft Encyclopedia'));
  check('no external requests',report.external_requests.length===0);check('no page errors',report.errors.length===0);
  report.accepted=true;
}catch(e){report.errors.push(e.stack||String(e));}finally{
  if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));report.finished_utc=new Date().toISOString();
  const file=path.join(out,'root-v19-browser-acceptance.json');if(fs.existsSync(file))throw Error('Refuse overwrite');fs.writeFileSync(file,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({accepted:report.accepted,checks:report.checks.length,errors:report.errors,external_requests:report.external_requests.length}));if(!report.accepted)process.exitCode=1;
}})();
