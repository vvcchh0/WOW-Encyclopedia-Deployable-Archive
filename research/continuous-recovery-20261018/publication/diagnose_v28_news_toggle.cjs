const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = process.cwd(), run = path.join(root, 'research/continuous-recovery-20261018');
const out = path.join(run, 'publication'), site = path.join(root, '.scratch/pages-resources-20261018-v28');
const prefix = '/WOW-Encyclopedia-Deployable-Archive', origin = 'http://127.0.0.1:29028', base = origin + prefix + '/';
const read = p => JSON.parse(fs.readFileSync(p)), sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const entries = ['v27-primary-source-map.json', 'v27-blizzard-supplement-source-map.json'].flatMap(name => read(path.join(run, 'integration/v27', name)).items)
  .concat(read(path.join(run, 'integration/v28/v28-primary-source-map.json')).items);
const references = ['v27', 'v28'].flatMap(v => read(path.join(out, v + '-export-expectations.json')).new_static_marker_references);
const byOriginal = new Map(entries.map(item => [item.original, item]));
const report = { started_utc: new Date().toISOString(), accepted: false, checks: [], errors: [], external_requests: [], screenshots: [] };
const receipt = path.join(out, 'root-v28-browser-retry2-acceptance.json');

report.prior_attempts = ['root-v28-browser-acceptance.json','root-v28-browser-retry1-acceptance.json'].map(name=>({path:name,sha256:sha(fs.readFileSync(path.join(out,name)))}));
report.test_correction = 'Four inline CSS backgrounds need background-image checks; real news-toggle clicks supply the legacy alt argument. A direct one-argument test call had produced news-collapseundefined. Site output is unchanged.';
const started = Date.now();
function check(name, ok, data = {}) {
  report.checks.push({ name, accepted: ok, ...data });
  if (!ok) throw Error(name + JSON.stringify(data));
  if (Date.now() - started > 300000) throw Error('Browser check deadline');
}
function outputPath(item) {
  const url = new URL(item.original);
  return url.hostname === 'www.blizzard.com' ? '_origins/www.blizzard.com' + url.pathname : url.pathname.slice(1);
}
const server = http.createServer((req, res) => {
  let relative;
  try {
    const url = new URL(req.url, origin);
    if (!url.pathname.startsWith(prefix + '/') || !['GET', 'HEAD'].includes(req.method)) throw Error();
    relative = decodeURIComponent(url.pathname.slice(prefix.length + 1));
  } catch { res.writeHead(400); return res.end(); }
  const file = path.resolve(site, relative);
  if (!file.startsWith(site + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': ({ '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.jpg': 'image/jpeg', '.gif': 'image/gif', '.png': 'image/png', '.svg': 'image/svg+xml' })[path.extname(file)] || 'application/octet-stream' });
  if (req.method === 'HEAD') return res.end();
  fs.createReadStream(file).pipe(res);
});
(async()=>{let browser;const logs=[];try{await new Promise(resolve=>server.listen(29028,'127.0.0.1',resolve));browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1400,height:1000}});await page.goto(base+'news/rss-02-2007.xml.html',{waitUntil:'networkidle'});const entry=page.locator('[id="news2-1-07-1212"]');const figure=entry.locator('figure');const state=async label=>{logs.push({label,cls:await entry.getAttribute('class'),visible:await figure.isVisible(),details:await figure.evaluate(el=>{const chain=[];for(let p=el;p&&chain.length<8;p=p.parentElement)chain.push({tag:p.tagName,id:p.id,cls:p.className,display:getComputedStyle(p).display,box:[p.getBoundingClientRect().width,p.getBoundingClientRect().height]});return chain})})};await state('initial');for(let i=0;i<4;i++){await entry.locator('.news-toggle a').click();await state('click'+i);await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await state('frames'+i)}logs.push({toggleDefinition:await page.evaluate(()=>window.toggleEntry.toString())});}catch(e){logs.push({error:String(e)})}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));fs.writeFileSync(path.join(out,'v28-toggle-diagnostic.json'),JSON.stringify(logs,null,2)+'\n');console.log(JSON.stringify(logs.map(x=>({label:x.label,cls:x.cls,visible:x.visible,error:x.error}))))}})();
