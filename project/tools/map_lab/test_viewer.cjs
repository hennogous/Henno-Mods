// Browser-level checks against all 120 published Quarter/map results.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require('C:/Users/Shadow/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(process.argv[2]||require('node:url').pathToFileURL(path.resolve('project/snapshots/map-lab/index.html')).href);
 await page.waitForFunction(()=>window.MapLab?.counts().length===8);
 const maps=await page.evaluate(()=>MapLab.bundle.maps.map(m=>({group:m.group,number:m.number,reference:m.reference})));
 let checks=0;
 for(const m of maps){
  await page.selectOption('#setup',m.group);await page.selectOption('#landscape',String(m.number));
  for(const filter of ['land_both','common_clearable_both','harvest_aware_both']){
   await page.selectOption('#filter',filter);
   const counts=await page.evaluate(()=>MapLab.counts());
   for(const r of m.reference){const actual=counts.find(c=>c.quarter===r.quarter);assert.equal(actual.sites,r[filter],`${m.group}/${m.number}/${r.quarter}/${filter}`);assert.equal(actual.base,r.base_source_tiles);assert.equal(actual.spec,r.spec_source_tiles);checks++;}
  }
  await page.selectOption('#filter','land_both');await page.check('#distinct');
  for(const c of await page.evaluate(()=>MapLab.counts()))assert.equal(c.sites,m.reference.find(r=>r.quarter===c.quarter).distinct_source_tiles);
  await page.uncheck('#distinct');
 }
 await page.selectOption('#setup','vanilla-abundant');await page.selectOption('#landscape','2');
 await page.click('[data-quarter="TAILORS"]');assert.equal(await page.evaluate(()=>MapLab.snapshot().quarter),'TAILORS');
 for(const id of ['base','spec','sites','labels','features']){await page.uncheck('#'+id);await page.check('#'+id);}
 await page.fill('#search','Silver');await page.fill('#search','');
 const zoom=await page.evaluate(()=>MapLab.snapshot().zoom);await page.click('#zoomIn');assert.ok((await page.evaluate(()=>MapLab.snapshot().zoom))>zoom);
 await page.click('#fit');await page.locator('#map').click({position:{x:350,y:250}});assert.ok(await page.evaluate(()=>MapLab.snapshot().selected!==null));
 await page.mouse.move(10,10);
 await page.screenshot({path:path.resolve('project/snapshots/map-lab/viewer-desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.resolve('project/snapshots/map-lab/viewer-mobile.png'),fullPage:true});
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Mobile horizontal overflow');
 await page.setViewportSize({width:1440,height:1000});
 await page.locator('#importFile').setInputFiles(path.resolve('project/snapshots/map-lab/experiments.json'));
 await page.waitForFunction(()=>MapLab.bundle.maps.length===19);
 assert.equal(await page.locator('#notice').isVisible(),true,'Emulated maps need a prominent notice');
 const imported=await page.evaluate(()=>MapLab.bundle.maps.slice(15).map(m=>({group:m.group,number:m.number,reference:m.reference})));
 for(const m of imported){
  await page.selectOption('#setup',m.group);await page.selectOption('#landscape',String(m.number));
  const counts=await page.evaluate(()=>MapLab.counts());
  for(const c of counts)assert.equal(c.sites,m.reference.find(r=>r.quarter===c.quarter).land_both);
 }
 await page.mouse.move(10,10);await page.screenshot({path:path.resolve('project/snapshots/map-lab/viewer-offline.png'),fullPage:true});
 assert.deepEqual(errors,[]);
 fs.writeFileSync('project/snapshots/map-lab/viewer-validation.json',JSON.stringify({maps:maps.length,quarterFilterChecks:checks,distinctChecks:120,importedExperiments:imported.length,browserErrors:errors,passed:true},null,2));
 console.log(JSON.stringify({maps:maps.length,quarterFilterChecks:checks,distinctChecks:120,passed:true}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
