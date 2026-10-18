const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=process.cwd(),run=path.join(root,'research/continuous-recovery-20261018'),out=path.join(run,'publication');
const site=path.join(root,'.scratch/pages-resources-20261018-v30'),prefix='/WOW-Encyclopedia-Deployable-Archive';
const origin='http://127.0.0.1:29030',base=origin+prefix+'/';
const read=p=>JSON.parse(fs.readFileSync(p)),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const entries=['primary','supplement'].flatMap(role=>read(path.join(run,`integration/v30/v30-${role}-source-map.json`)).items);
const route=item=>{const u=new URL(item.original);return u.hostname==='www.worldofwarcraft.com'?u.pathname.slice(1):'_origins/'+u.hostname+u.pathname;};
const byRoute=new Map(entries.map(item=>[route(item),item]));
const receipt=path.join(out,'root-v30-browser-retry1-acceptance.json');
if(fs.existsSync(receipt))throw Error('Preserve completed browser receipt');
const report={accepted:false,started_utc:new Date().toISOString(),checks:[],errors:[],external_requests:[],screenshots:[],scope:'33 original resources; five affected pages, equipment tabs, seven profession selectors and 21 recipes, socket tooltip and story illustration popup.'};
report.prior_attempt={path:'root-v30-browser-acceptance.json',sha256:sha(fs.readFileSync(path.join(out,'root-v30-browser-acceptance.json')))};report.test_correction='Wait for javascript URL recipe dispatch before checking text; separately retain any actual page errors.';
const started=Date.now();
function check(name,ok,data={}){report.checks.push({name,accepted:!!ok,...data});if(!ok)throw Error(name+JSON.stringify(data));if(Date.now()-started>300000)throw Error('Five minute browser deadline');}
const server=http.createServer((req,res)=>{let relative;try{const u=new URL(req.url,origin);if(!u.pathname.startsWith(prefix+'/')||!['GET','HEAD'].includes(req.method))throw Error();relative=decodeURIComponent(u.pathname.slice(prefix.length+1));}catch{res.writeHead(400);return res.end();}const p=path.resolve(site,relative);if(!p.startsWith(site+path.sep)||!fs.existsSync(p)||!fs.statSync(p).isFile()){res.writeHead(404);return res.end();}res.writeHead(200,{'content-type':({'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.jpg':'image/jpeg','.gif':'image/gif','.png':'image/png','.svg':'image/svg+xml'})[path.extname(p)]||'application/octet-stream'});if(req.method==='HEAD')return res.end();fs.createReadStream(p).pipe(res);});
async function decoded(locator,item,label){await locator.waitFor({state:'visible'});await locator.scrollIntoViewIfNeeded();await locator.evaluate(el=>el.decode());const dimensions=await locator.evaluate(el=>[el.naturalWidth,el.naturalHeight]);check(label,JSON.stringify(dimensions)===JSON.stringify(item.dimensions),{route:route(item),dimensions});}
async function screenshot(page,name){await page.screenshot({path:path.join(out,name)});report.screenshots.push(name);}
(async()=>{let browser;try{
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(29030,'127.0.0.1',resolve);});
  browser=await chromium.launch({headless:true});const context=await browser.newContext({viewport:{width:1600,height:1100}});context.setDefaultTimeout(10000);
  await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin&&['GET','HEAD'].includes(r.request().method()))return r.continue();report.external_requests.push(r.request().url());return r.abort();});
  context.on('page',p=>p.on('pageerror',e=>report.errors.push(String(e))));const page=await context.newPage();
  check('exact33 distinct new image routes',entries.length===33&&byRoute.size===33);
  for(const item of entries){const response=await context.request.get(base+route(item)),bytes=await response.body();check('original resource served',response.status()===200&&response.headers()['content-type']===item.mime&&bytes.length===item.length&&sha(bytes)===item.sha256,{route:route(item)});}
  const go=async name=>{const response=await page.goto(base+name,{waitUntil:'networkidle'});check('affected page opens',response.status()===200,{page:name});};
  await go('pvp/tournament/items.xml.html');let icons=0;const seen=new Set();
  for(const tab of ['general','weapons','accessories','enchantments','gems','plate','mail','leather','cloth','pets']){
    await page.locator(`a[rel="tab-${tab}"]`).click();const panel=page.locator('#tab-'+tab);check('original equipment tab selected',await panel.isVisible(),{tab});
    for(const [relative,item]of byRoute){if(!relative.startsWith('_origins/www.wowarmory.com/'))continue;for(const image of await panel.locator('img[src$="/'+relative+'"]').all()){await decoded(image,item,'equipment image visible');icons++;seen.add(relative);}}
  }
  check('all112 equipment icon references displayed',icons===112,{actual:icons});check('all12 US equipment images displayed',seen.size===12,{actual:seen.size});
  await page.locator('a[rel="tab-plate"]').click();await screenshot(page,'v30-equipment-tabs-retry1.png');
  await go('community/tournaments/euregionals/index.html');const eu=entries.find(x=>x.original.includes('armory.wow-europe.com'));
  const classes=page.locator('img[src$="/'+route(eu)+'"]');check('six regional class icon references',await classes.count()===6);for(const image of await classes.all())await decoded(image,eu,'regional class icon visible');
  await go('burningcrusade/townhall/professions.html');const reagentSeen=new Set();
  for(let profession=0;profession<7;profession++){
    if(profession){await page.locator('#dropBox > div[onclick]').click();await page.locator('#slot'+profession+' a').click();}
    check('original profession selector updates',await page.locator('#slotZero').innerText()!==''&&await page.locator('#recipeList a').count()===3,{profession});
    for(let recipe=0;recipe<3;recipe++){
      const link=page.locator('#recipeList a').nth(recipe),name=await link.innerText();await link.click();await page.waitForFunction(expected=>document.getElementById('recipeName').innerText===expected,name);check('original recipe selection updates',await page.locator('#recipeName').innerText()===name,{profession,recipe,recipe_name:name});
      for(const [relative,item]of byRoute){if(!/professions\/reagent\d+\.gif$/.test(relative))continue;for(const image of await page.locator('.reagentColumn img[src$="/'+relative+'"]').all()){await decoded(image,item,'dynamic recipe reagent visible');reagentSeen.add(relative);}}
      if(profession===1&&recipe===0){await page.locator('#recipeIcon').hover();const socket=page.locator('#toolBox .sBlu');await socket.waitFor({state:'visible'});const source=await socket.evaluate(el=>getComputedStyle(el).backgroundImage);const blue=entries.find(x=>x.original.endsWith('/blusocket.gif'));check('blue socket tooltip uses recovered background',source.includes('/'+route(blue)));const dimensions=await socket.evaluate(async el=>{const u=getComputedStyle(el).backgroundImage.match(/url\(["']?(.*?)["']?\)/)[1],img=new Image();img.src=u;await img.decode();return[img.naturalWidth,img.naturalHeight];});check('blue socket tooltip image decodes',JSON.stringify(dimensions)===JSON.stringify(blue.dimensions));await screenshot(page,'v30-profession-tooltip-retry1.png');await page.mouse.move(0,0);}
    }
  }
  const expectedReagents=entries.filter(x=>/professions\/reagent\d+\.gif$/.test(route(x))).length;check('all recovered reagents exercised through recipe controls',reagentSeen.size===expectedReagents,{actual:reagentSeen.size,expected:expectedReagents});
  await go('insider/12/magtheridon.xml.html');const mag=entries.find(x=>x.original.endsWith('/12-magtheridon-magbig2.jpg'));const magImage=page.locator('img[src$="/'+route(mag)+'"]');check('Magtheridon illustration reference',await magImage.count()===1);await decoded(magImage,mag,'Magtheridon original illustration visible');await screenshot(page,'v30-magtheridon-retry1.png');
  await go('burningcrusade/townhall/story.html');const concept=entries.find(x=>x.original.endsWith('/war3x/images/screens/concept/ss01.jpg'));
  const chapters=await page.locator('[id^="link"][href*="jumpChapter"]').count();check('story chapter controls available',chapters>0);let opened=false;
  for(let chapter=0;chapter<chapters;chapter++){await page.locator('#link'+chapter).click();const link=page.locator('a[href*="'+route(concept)+'"]');if(!await link.count())continue;const [popup]=await Promise.all([page.waitForEvent('popup'),link.click()]);await popup.waitForLoadState('domcontentloaded');const art=popup.locator('img[src$="/'+route(concept)+'"]');await decoded(art,concept,'story artwork opens through original popup control');await screenshot(popup,'v30-story-artwork-retry1.png');await popup.close();opened=true;break;}
  check('story artwork popup was exercised',opened);
  await go('__offline/related-images/index.html');for(const item of entries.filter(x=>new URL(x.original).hostname!=='www.worldofwarcraft.com'))check('supplement catalog includes exact origin image',await page.locator('img[src$="/'+route(item)+'"]').count()===1,{original:item.original});
  check('no external requests',report.external_requests.length===0);check('no browser errors',report.errors.length===0);report.accepted=true;
}catch(error){report.errors.push(String(error));}finally{report.finished_utc=new Date().toISOString();report.export_provenance_sha256=sha(fs.readFileSync(path.join(site,'export-provenance.json')));fs.writeFileSync(receipt,JSON.stringify(report,null,2)+'\n');if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));console.log(JSON.stringify({accepted:report.accepted,checks:report.checks.length,errors:report.errors,external_requests:report.external_requests}));if(!report.accepted)process.exitCode=1;}})();
