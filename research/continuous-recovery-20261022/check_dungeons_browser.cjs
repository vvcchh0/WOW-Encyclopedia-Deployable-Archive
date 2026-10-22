// Inspect the accepted v52 dungeon page without fetching remote resources.
const fs = require('fs'), path = require('path'), assert = require('assert');
const {chromium} = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.resolve(__dirname, '../..');
const base = 'http://127.0.0.1:24782/WOW-Encyclopedia-Deployable-Archive';
const out = path.join(__dirname, 'dungeons-v52-browser-inspection.json');
for (const key of ['TEMP','TMP','TMPDIR']) process.env[key] = path.join(root, '.scratch/test-temp-20261022');
fs.mkdirSync(process.env.TEMP, {recursive:true});
(async()=>{
  const started = new Date().toISOString(), external = [], errors = [], responses = [];
  const browser = await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const context = await browser.newContext({serviceWorkers:'block', viewport:{width:1500,height:1050}});
  await context.route('**/*', r=>{const u = new URL(r.request().url());
    if (u.origin==='http://127.0.0.1:24782' || ['data:','blob:','about:'].includes(u.protocol)) return r.continue();
    external.push(r.request().url()); return r.abort();});
  const page = await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('response',r=>{if(r.status()>=400)responses.push({url:r.url(),status:r.status()})});
  try {
    const response = await page.goto(base+'/info/basics/dungeons.html',{waitUntil:'load',timeout:60000});
    assert.equal(response.status(),200);
    const images = await page.locator('img[src*="/screenshots/images/basics/dungeons/"]').evaluateAll(async nodes=>Promise.all(nodes.map(async el=>{
      let decoded=true; try{await el.decode()}catch(e){decoded=false}
      return {src:el.getAttribute('src'),width:el.naturalWidth,height:el.naturalHeight,decoded,
        rendered_width:el.getBoundingClientRect().width,rendered_height:el.getBoundingClientRect().height,
        href:el.closest('a')?.getAttribute('href')||null};
    })));
    const originals=[];
    for (const item of images.filter(i=>i.href)) {
      const resp=await context.request.get('http://127.0.0.1:24782'+item.href);
      originals.push({href:item.href,status:resp.status(),bytes:(await resp.body()).length,type:resp.headers()['content-type']});
    }
    const missing = await page.locator('[data-offline-missing], .offline-missing-image').count();
    await page.screenshot({path:path.join(__dirname,'dungeons-v52.png'),fullPage:true});
    const report={checked_utc:started,finished_utc:new Date().toISOString(),version:'v52',route:'/info/basics/dungeons.html',
      images, originals, missing_marker_count:missing, external_requests:external,page_errors:errors,http_errors:responses,
      scope:'Actual unmodified local Chrome rendering and same-origin full-size responses; no remote downloads.'};
    fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }finally{await context.close();await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
