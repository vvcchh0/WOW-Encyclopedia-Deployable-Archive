/* Read-only loopback verification of the accepted v39 news delta. */
const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const ROOT = path.resolve(__dirname, '../../..');
const PLAN = path.join(__dirname, 'root-v39-browser-plan.json');
const RESULT = path.join(__dirname, 'v39-browser-result.json');
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const assert = (ok, text) => { if (!ok) throw new Error(text); };
const mime = name => ({'.html':'text/html; charset=utf-8','.xml':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.gif':'image/gif','.svg':'image/svg+xml','.ico':'image/x-icon'})[path.extname(name).toLowerCase()] || 'application/octet-stream';

async function main() {
  assert(!fs.existsSync(RESULT), 'preserve prior browser result');
  const plan = read(PLAN);
  assert(plan.accepted && plan.root_browser_go, 'missing root browser GO');
  const site = path.resolve(ROOT, plan.site), prefix = plan.base_path;
  assert(site.startsWith(ROOT + path.sep), 'site outside workspace');
  const provenanceData = fs.readFileSync(path.join(site, 'export-provenance.json'));
  assert(sha(provenanceData) === plan.export_provenance_sha256, 'provenance changed');
  const files = new Map(JSON.parse(provenanceData).files.map(r => [r.output_path, r]));
  const report = {accepted:false, started_utc:new Date().toISOString(), site:plan.site,
    export_provenance_sha256:plan.export_provenance_sha256, plan_sha256:sha(fs.readFileSync(PLAN)),
    checks:[], server_requests:[], external_requests:[], console_errors:[], page_errors:[], server_errors:[]};
  let browser, server;
  const timer = setTimeout(() => { process.stderr.write('browser hard timeout\n'); process.exit(124); }, 150000);
  try {
    server = http.createServer((req, res) => {
      try {
        const url = new URL(req.url, 'http://127.0.0.1');
        assert(['GET','HEAD'].includes(req.method), 'unexpected HTTP method');
        assert(url.pathname.startsWith(prefix), 'outside archive prefix');
        const relative = decodeURIComponent(url.pathname.slice(prefix.length));
        assert(relative && !relative.includes('\\') && !relative.includes('\0') && !relative.includes(':') && !relative.split('/').includes('..'), 'invalid relative path');
        const file = path.resolve(site, relative);
        assert(file.startsWith(site + path.sep), 'path escapes site');
        const expected = files.get(relative);
        assert(expected || relative === 'export-provenance.json', 'undeclared file: ' + relative);
        const data = fs.readFileSync(file), actual = sha(data);
        assert(!expected || actual === expected.derived_sha256 && data.length === expected.derived_length, 'object changed: ' + relative);
        report.server_requests.push({path:relative, method:req.method, status:200, sha256:actual, bytes:data.length, mime:mime(file)});
        res.writeHead(200, {'Content-Type':mime(file),'Content-Length':data.length,'Cache-Control':'no-store'});
        res.end(req.method === 'HEAD' ? undefined : data);
      } catch (error) {
        report.server_errors.push({url:req.url, error:String(error)});
        res.writeHead(404); res.end();
      }
    });
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    const origin = `http://127.0.0.1:${server.address().port}`;
    browser = await chromium.launch({headless:true});
    const context = await browser.newContext({viewport:{width:1365,height:900}});
    await context.route('**/*', route => {
      const url = new URL(route.request().url());
      if (url.origin === origin) return route.continue();
      report.external_requests.push({url:route.request().url(), type:route.request().resourceType()});
      return route.abort();
    });
    const page = await context.newPage();
    page.on('pageerror', error => report.page_errors.push(String(error)));
    page.on('console', message => { if (message.type() === 'error') report.console_errors.push({text:message.text(),location:message.location()}); });
    for (const check of plan.checks) {
      const response = await page.goto(origin + prefix + check.page, {waitUntil:'networkidle',timeout:30000});
      assert(response.status() === 200, 'page HTTP failed: ' + check.page);
      const row = {page:check.page, status:response.status(), images:[]};
      for (const target of check.images || []) {
        const locator = page.locator('img');
        const candidates = await locator.evaluateAll((elements, src) => elements.map((el, index) => ({index, path:new URL(el.currentSrc || el.src, document.baseURI).pathname})).filter(el => el.path === src), prefix + target.path);
        assert(candidates.length === 1, 'image entry count: ' + target.path);
        const image = page.locator('img').nth(candidates[0].index);
        await image.scrollIntoViewIfNeeded();
        const info = await image.evaluate(async el => { await el.decode(); const box=el.getBoundingClientRect(); return {path:new URL(el.currentSrc).pathname,complete:el.complete,width:el.naturalWidth,height:el.naturalHeight,display_width:box.width,display_height:box.height,inside_anchor:!!el.closest('a'),inside_form:!!el.closest('form'),figure:el.closest('figure')?.innerText || null}; });
        assert(await image.isVisible() && info.complete && info.width === target.width && info.height === target.height && info.display_width>0 && info.display_height>0, 'image not visibly decoded: ' + target.path);
        if (target.static_exhibit) {
          assert(!info.inside_anchor && !info.inside_form && /Historical 2004 promotional artwork/i.test(info.figure || ''), 'promotion not static exhibit');
          const entry = image.locator('xpath=ancestor::div[contains(concat(" ", normalize-space(@class), " "), " postContainer ")][1]');
          const text = await entry.innerText();
          assert(/12\/16\/04/.test(text), 'historical date missing');
          assert(!/Head to our online store and get your copy now|by purchasing your copy.*today/i.test(text), 'current order instruction retained');
          assert(await entry.locator('a').count() === 0, 'store action retained in exhibit entry');
        }
        row.images.push({path:target.path, ...info});
        const shots = path.join(__dirname, 'v39-browser-screenshots');
        fs.mkdirSync(shots, {recursive:true});
        const screenshot = path.join(shots, path.basename(target.path) + '.png');
        const entry = image.locator('xpath=ancestor::div[contains(concat(" ", normalize-space(@class), " "), " postContainer ")][1]');
        await (await entry.count() ? entry : image).screenshot({path:screenshot});
        row.images[row.images.length-1].screenshot = path.relative(ROOT, screenshot).replace(/\\/g,'/');
      }
      report.checks.push(row);
    }
    assert(report.external_requests.length === 0 && report.server_errors.length === 0 && report.page_errors.length === 0 && report.console_errors.length === 0, 'browser/network errors');
    report.accepted = true;
  } catch (error) { report.error = String(error.stack || error); }
  finally {
    if (browser) await browser.close();
    if (server) await new Promise(resolve => server.close(resolve));
    clearTimeout(timer);
    report.finished_utc = new Date().toISOString();
    fs.writeFileSync(RESULT, JSON.stringify(report,null,2)+'\n', {flag:'wx'});
  }
  process.stdout.write(JSON.stringify({accepted:report.accepted,pages:report.checks.length,requests:report.server_requests.length,error:report.error})+'\n');
  if (!report.accepted) process.exitCode = 1;
}
main().catch(error => { process.stderr.write(String(error.stack || error)); process.exitCode=1; });
