const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=process.cwd(),site=path.join(root,'.scratch/pages-resources-20261016-v25'),out=path.join(root,'research/focused-recovery-20261016-2301/publication');
const prefix='/WOW-Encyclopedia-Deployable-Archive',origin='http://127.0.0.1:29025',base=origin+prefix+'/';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const images=JSON.parse(fs.readFileSync(path.join(root,'research/continuous-recovery-20261016/publication/root-neighbors9-source-acceptance.json'))).accepted_images;
const prov=JSON.parse(fs.readFileSync(path.join(site,'export-provenance.json'))),records=new Map(prov.files.map(x=>[x.route,x]));
const report={started_utc:new Date().toISOString(),accepted:false,checks:[],errors:[],external_requests:[]};
function check(name,ok,data={}){report.checks.push({name,accepted:ok,...data});if(!ok)throw Error(name+JSON.stringify(data));}
const server=http.createServer((req,res)=>{let rel;try{let u=new URL(req.url,origin);if(!u.pathname.startsWith(prefix+'/'))throw Error();rel=decodeURIComponent(u.pathname.slice(prefix.length+1));}catch{res.writeHead(400);return res.end();}let file=path.resolve(site,rel);if(!file.startsWith(site+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);return res.end();}res.writeHead(200,{'content-type':({'.html':'text/html','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.gif':'image/gif','.png':'image/png','.json':'application/json'})[path.extname(file)]||'application/octet-stream'});fs.createReadStream(file).pipe(res);});
(async()=>{let browser;try{
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(29025,'127.0.0.1',resolve);});
 browser=await chromium.launch({headless:true});const context=await browser.newContext({viewport:{width:1400,height:1000}});context.setDefaultTimeout(12000);
 await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();report.external_requests.push(r.request().url());return r.abort();});
 const page=await context.newPage();page.on('pageerror',e=>report.errors.push(String(e)));
 for(let image of images){let route=new URL(image.original).pathname,response=await context.request.get(origin+prefix+route),bytes=await response.body();check('new original bytes served',response.status()===200&&sha(bytes)===image.sha256&&bytes.length===image.length,{route});}
 for(let group of prov.guide_image_collections.groups){
  for(let key of ['guide_route','gallery_route']){
   let rel=records.get(group[key]).output_path,response=await page.goto(base+rel,{waitUntil:'networkidle'});check('collection page',response.status()===200,{route:group[key]});let section=page.locator('.offline-guide-image-collection'),imgs=section.locator('img');check('collection count',await imgs.count()===group.images.length,{route:group[key],count:await imgs.count()});
   for(let image of images.filter(x=>x.collection_group===group.group_id)){
    let route=new URL(image.original).pathname,img=section.locator('img[src$="'+route+'"]').first();await img.scrollIntoViewIfNeeded();await page.waitForFunction(el=>el.complete&&el.naturalWidth>0,await img.elementHandle());let dim=await img.evaluate(el=>[el.naturalWidth,el.naturalHeight]);check('new collection image visible',JSON.stringify(dim)===JSON.stringify(image.dimensions),{route});
    let href=await img.evaluate(el=>el.closest('a')?.getAttribute('href'));check('new original link',href?.endsWith(route),{route,href});let file='v25-'+group.group_id+'-'+key+'.png';await page.screenshot({path:path.join(out,file),fullPage:false});
   }
  }
 }
 await page.goto(base+'__offline/related-images/index.html',{waitUntil:'networkidle'});
 for(let image of images){let route=new URL(image.original).pathname;check('new material catalog link',await page.locator('a[href$="'+route+'"]').count()>0,{route});}
 check('no external requests',report.external_requests.length===0);check('no page errors',report.errors.length===0);report.accepted=true;
}catch(e){report.errors.push(e.stack||String(e));}finally{if(browser)await browser.close();await new Promise(r=>server.close(r));report.finished_utc=new Date().toISOString();let dest=path.join(out,'root-v25-browser-acceptance.json');if(fs.existsSync(dest))throw Error('refuse overwrite');fs.writeFileSync(dest,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({accepted:report.accepted,checks:report.checks.length,errors:report.errors,external_requests:report.external_requests.length}));if(!report.accepted)process.exitCode=1;}})();
