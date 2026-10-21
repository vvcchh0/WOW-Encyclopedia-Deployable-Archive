// Parent's narrow browser check of the new entry and historical-program behavior.
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { chromium } = require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const out = path.join(__dirname, 'root-v43-entry-browser.json');
const base = 'http://127.0.0.1:54464/WOW-Encyclopedia-Deployable-Archive';
(async () => {
  assert(!fs.existsSync(out));
  const browser = await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const context = await browser.newContext({serviceWorkers:'block', viewport:{width:1440,height:1000}});
  const blocked = [], errors = [], failed = [];
  await context.route('**/*', route => {
    const u = new URL(route.request().url());
    if ((u.hostname === '127.0.0.1' && u.port === '54464') || ['data:','blob:','about:'].includes(u.protocol)) return route.continue();
    blocked.push(route.request().url()); return route.abort();
  });
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(String(e)));
  page.on('requestfailed', req => failed.push({url:req.url(),error:req.failure()}));
  try {
    const news = await page.goto(base+'/news/wow-news-06-2005.html', {waitUntil:'load',timeout:20000});
    assert.equal(news.status(),200);
    const text = await page.locator('#main-content').innerText();
    assert(text.includes('Insider Battlegrounds Screen Shot Contest'));
    assert(text.includes('June 20th, 2005'));
    const entry = page.getByRole('link',{name:'Submit a Screenshot',exact:true});
    assert.equal(await entry.count(),1);
    const target = await entry.getAttribute('href');
    assert.equal(target,'/WOW-Encyclopedia-Deployable-Archive/contests/05-06-09/index.html');
    await entry.click(); await page.waitForLoadState('load');
    const contestUrl = page.url();
    assert(contestUrl.endsWith('/contests/05-06-09/index.html'));
    const contest = await page.locator('body').innerText();
    assert(contest.includes('The historical contest invited players'));
    assert(contest.includes('planned publication of the winners'));
    const program = await page.goto(base+'/misc/fan-site-program.html',{waitUntil:'load',timeout:20000});
    assert.equal(program.status(),200);
    const programText = await page.locator('body').innerText();
    assert(programText.includes('This historical exhibit does not accept applications.'));
    assert.equal(await page.locator('a[href^="mailto:"]').count(),0);
    assert.equal(await page.locator('input[type=password],input[type=email],input[type=file]').count(),0);
    assert.equal(errors.length,0); assert.equal(failed.length,0); assert.equal(blocked.length,0);
    fs.writeFileSync(out,JSON.stringify({accepted:true,checked_utc:new Date().toISOString(),version:'v43',
      actual_browser:'Chrome',news_two_article_phrases:true,contest_entry_href:target,contest_entry_click_url:contestUrl,
      contest_describes_invitation_and_planned_winners:true,program_application_service_inactive:true,
      page_errors:errors,request_failures:failed,external_requests:blocked,
      limitation:'The old news CTA and contest Continue image are queued for historical wording in the next derived version.'},null,2)+'\n');
    console.log(JSON.stringify({accepted:true,checks:6}));
  } finally { await context.close(); await browser.close(); }
})().catch(e => { console.error(e); process.exitCode=1; });
