// Execute the viewer's actual geometry functions as source-level unit checks.
// No browser or UI automation is involved.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(__dirname+'/viewer.js','utf8').replace(/\r\n/g,'\n');
const functions=['matches','clearable','compute','visibleSites'].map(name=>{
 const start=source.indexOf('  function '+name+'('),end=source.indexOf('\n  ',start+3);
 if(name==='compute'){const stop=source.indexOf('\n  function visibleSites',start);return source.slice(start,stop);}
 return source.slice(start,end);
}).join('\n');
const bundle=JSON.parse(fs.readFileSync(process.argv[2]||'project/snapshots/map-lab/maps.json','utf8'));
let checks=0;
for(const map of bundle.maps){
 const values={filter:{value:'land_both'},distinct:{checked:false},supply:{value:'both'},continent:{value:'-1'}};
 const context=vm.createContext({current:map,plots:map.data.plots,definitions:map.definitions,
  resources:Object.fromEntries(map.data.resources.map(r=>[r.type,r])),features:Object.fromEntries(map.data.features.map(f=>[f.type,f])),
  cache:{},quarter:'BAKERS',$:id=>values[id],Set,Map});
 vm.runInContext(source.match(/  const flags=\(\)=>.*\n/)[0]+source.match(/  const inRegion=.*\n/)[0]+functions,context);
 for(const q of Object.keys(map.definitions))context.cache[q]=vm.runInContext(`compute('${q}')`,context);
 const regions=map.continents||[{id:-1,quarters:map.reference}];
 for(const region of regions){values.continent.value=String(region.id);
  for(const row of region.quarters)for(const mask of ['land','common_clearable','harvest_aware'])for(const mode of ['base','both']){
   const key=mask+'_'+mode;if(row[key]===undefined)continue;
   values.filter.value=mask+'_both';values.supply.value=mode;values.distinct.checked=false;
   assert.equal(vm.runInContext(`visibleSites('${row.quarter}').size`,context),row[key],`${map.id}/${region.id}/${row.quarter}/${key}`);checks++;
   if(mode==='both'&&row[key+'_distinct']!==undefined){values.distinct.checked=true;assert.equal(vm.runInContext(`visibleSites('${row.quarter}').size`,context),row[key+'_distinct']);checks++;}
  }
 }
}
console.log(JSON.stringify({maps:bundle.maps.length,geometryChecks:checks,passed:true}));
