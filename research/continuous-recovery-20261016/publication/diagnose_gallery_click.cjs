const fs=require('fs');
const {chromium}=require('C:/Users/17630/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true}), results=[];
 for(const port of [29012,29013]){
  const page=await browser.newPage(), consoleErrors=[];
  page.on('console',m=>{if(m.type()==='error') consoleErrors.push(m.text())});
  await page.goto('http://127.0.0.1:'+port+'/WOW-Encyclopedia-Deployable-Archive/info/professions/fishing-gallery.html',{waitUntil:'networkidle'});
  const state=()=>page.evaluate(()=>({page:currentPage,pages:numPages,number:document.getElementById('pageNum').innerText,fn:typeof galleryNext,href:[...document.querySelectorAll('a')].filter(a=>a.getAttribute('href')?.includes('galleryNext')).map(a=>({href:a.getAttribute('href'),onclick:a.getAttribute('onclick')}))}));
  const before=await state();
  await page.locator('a[href="javascript:galleryNext();"]').first().click();
  await page.waitForTimeout(300);
  const click=await state();
  await page.evaluate(()=>galleryNext());
  const manual=await state();
  results.push({port,before,click,manual,consoleErrors});
  await page.close();
 }
 await browser.close();
 fs.writeFileSync('research/continuous-recovery-20261016/publication/gallery-click-diagnostic.json',JSON.stringify(results,null,2)+'\n');
 console.log(JSON.stringify(results));
})().catch(e=>{console.error(e);process.exitCode=1});
