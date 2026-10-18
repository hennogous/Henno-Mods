// Full viewer execution against a small DOM/canvas fixture, without a browser.
// Checks control wiring and before/after data; does not claim visual rendering QA.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const bundle=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
if(process.argv.includes('--preview-only')){bundle.maps=bundle.maps.filter(m=>m.group==='csc-assist');bundle.default_group='csc-assist';}
// Import-style profiles in the in-memory fixture; historical files stay intact.
for(const m of bundle.maps.filter(m=>m.group==='csc-helper-lua'))m.assistance.abundance={targets:{TAILORS:1,GOLDSMITHS:1/2},nominal_density:54,scale:54/33,max_per_continent:7,max_per_map:16};
const source=fs.readFileSync(__dirname+'/viewer.js','utf8');
const html=fs.readFileSync(__dirname+'/viewer.template.html','utf8');
class Element {
 constructor(tag='div'){this.tagName=tag;this.children=[];this.listeners={};this._text='';this._value='';this.style={};this.dataset={};this.classList={remove(){},add(){}};this.checked=false;this.hidden=false;}
 get options(){return this.children.filter(c=>c.tagName==='option');}
 get value(){return this.tagName==='select'?(this.options.some(o=>o.value===this._value)?this._value:this.options[0]?.value||''):this._value;}
 set value(v){this._value=String(v);}
 append(...xs){this.children.push(...xs);}
 replaceChildren(...xs){this.children=xs;this._text='';}
 set textContent(v){this._text=String(v);this.children=[];}
 get textContent(){return this._text+this.children.map(c=>c.textContent).join('');}
 addEventListener(event,fn){this.listeners[event]=fn;}
 setAttribute(k,v){this[k]=v;}
 getBoundingClientRect(){return {width:1100,height:650,left:0,top:0};}
 setPointerCapture(){}
}
const nodes={};for(const match of html.matchAll(/<([\w]+)[^>]*\bid="([^"]+)"[^>]*>/g)){const el=new Element(match[1]);el.checked=/\bchecked\b/.test(match[0]);nodes[match[2]]=el;}
for(const match of html.matchAll(/<select id="([^"]+)"[^>]*>(.*?)<\/select>/gs))for(const opt of match[2].matchAll(/<option value="([^"]+)"[^>]*>(.*?)<\/option>/gs)){const el=new Element('option');el.value=opt[1];el.textContent=opt[2];nodes[match[1]].append(el);}
nodes['map-data'].textContent=JSON.stringify(bundle);
let drawCalls=0;const ctx=new Proxy({measureText:s=>({width:s.length*6})},{get:(target,k)=>k in target?target[k]:(()=>{drawCalls++;})});nodes.map.getContext=()=>ctx;
const window={},context=vm.createContext({window,document:{getElementById:id=>{assert.ok(nodes[id],id);return nodes[id];},createElement:t=>new Element(t),createTextNode:s=>Object.assign(new Element('text'),{textContent:s})},devicePixelRatio:1,ResizeObserver:class{constructor(fn){this.fn=fn;}observe(){this.fn();}},console});
vm.runInContext(source,context);assert.equal(window.MapLab.snapshot().id,(bundle.default_group||'csc-assist')+'-1');assert.equal(nodes.filter.value,'common_clearable_both');
let checks=0;
const change=(id,value)=>{nodes[id].value=value;nodes[id].listeners.change({});};
if(process.argv.includes('--implemented')){
 for(const m of bundle.maps){
  change('setup',m.group);change('landscape',m.number);
  assert.equal(window.MapLab.snapshot().id,m.id);assert.equal(nodes.abundancePanel.hidden,false);
  assert.equal(nodes.abundanceTable.children[1].children.length,new Set(bundle.maps.map(x=>x.group)).size);
  assert.match(nodes.status.textContent,/Native Civ map/);assert.match(nodes.assistanceHelp.textContent,/individual copies/);
  const coverage=nodes.coverageTable.children[1].children;
  assert.notEqual(coverage[0].children[3].textContent,'—');assert.notEqual(coverage[1].children[3].textContent,'—');
  for(let i=2;i<8;i++)assert.equal(coverage[i].children[3].textContent,'—');
  const rows=nodes.additionTable.children[1].children;assert.equal(rows.length,m.assistance.additions.length);
  for(let i=0;i<rows.length;i++)assert.equal(rows[i].children[7].textContent,String(m.assistance.additions[i].quantity));
  for(const when of ['before','after']){
   change('version',when);const census=(when==='before'?m.assistance.before_continents:m.continents).find(c=>c.id===-1);
   for(const row of window.MapLab.counts()){assert.equal(row.sites,census.quarters.find(q=>q.quarter===row.quarter).common_clearable_both);checks++;}
  }
 }
 console.log(JSON.stringify({passed:true,nativeMaps:bundle.maps.length,beforeAfterChecks:checks,quantityColumnsVerified:true,designOnlyTargetsExcluded:true,visualRenderingTested:false}));process.exit(0);
}
if(process.argv.includes('--abundance')){
 const setups=[...new Set(bundle.maps.map(m=>m.group))];assert.equal(setups.length,8);
 for(const m of bundle.maps){
  change('setup',m.group);change('landscape',m.number);
  assert.equal(window.MapLab.snapshot().id,m.id);assert.equal(nodes.abundancePanel.hidden,false);
  assert.equal(nodes.abundanceTable.children[1].children.length,8);
  assert.equal(nodes.additionTable.children[1].children.length,m.assistance.additions.length);
  assert.match(nodes.status.textContent,/Offline abundance study/);
  assert.match(nodes.assistanceHelp.textContent,/ten|10/);
  if(m.number===1)for(const button of [...nodes.quarters.children]){
   const q=button.dataset.quarter;button.listeners.click();
   const rows=nodes.abundanceTable.children[1].children;
   for(let i=0;i<setups.length;i++){
    const maps=bundle.maps.filter(x=>x.group===setups[i]);const values=when=>maps.flatMap(x=>(when==='before'?x.assistance.before_continents:x.continents).filter(c=>c.id!==-1).map(c=>c.quarters.find(y=>y.quarter===q)));
    const b=values('before'),a=values('after'),count=rs=>rs.filter(r=>r.common_clearable_both>0).length;
    assert.equal(rows[i].children[1].textContent,`${count(b)}/${a.length} → ${count(a)}/${a.length}`);checks++;
   }
  }
  for(const when of ['before','after']){
   change('version',when);const census=(when==='before'?m.assistance.before_continents:m.continents).find(c=>c.id===-1);
   for(const row of window.MapLab.counts()){assert.equal(row.sites,census.quarters.find(q=>q.quarter===row.quarter).common_clearable_both);checks++;}
  }
 }
 console.log(JSON.stringify({passed:true,maps:bundle.maps.length,aggregateQuarterChecks:checks,drawCalls,visualRenderingTested:false}));process.exit(0);
}
if(!process.argv.includes('--controls-only'))for(const preview of bundle.maps.filter(m=>m.assistance)){
 change('setup',preview.group);
 change('landscape',preview.number);
 assert.equal(nodes.assistancePanel.hidden,false);
 assert.equal(nodes.additionTable.children[1].children.length,preview.assistance.additions.length);
 for(const region of preview.continents){change('continent',region.id);
  for(const filter of ['land','common_clearable','harvest_aware']){change('filter',filter+'_both');
   for(const mode of ['base','both']){change('supply',mode);
    for(const when of (preview.native_comparison?.automatic?['before','offline','preview','after']:preview.native_comparison?['before','preview','after']:['before','after'])){change('version',when);
     const census=(when==='before'?preview.assistance.before_continents:when==='offline'?bundle.maps.find(m=>m.id===preview.native_comparison.offline_preview_id).continents:when==='preview'?bundle.maps.find(m=>m.id===preview.native_comparison.preview_id).continents:preview.continents).find(c=>c.id===region.id);
     for(const row of window.MapLab.counts()){assert.equal(row.sites,census.quarters.find(q=>q.quarter===row.quarter)[filter+'_'+mode]);checks++;}
    }
   }
  }
 }
 change('continent',-1);change('version','after');
 if(preview.native_comparison){assert.match(nodes.status.textContent,preview.native_comparison.automatic?/Automatic CSC Lua/:/Civ API test/);assert.equal(nodes.coverageTable.children[0].children[0].children.length,preview.native_comparison.automatic?7:6);assert.match(nodes.assistanceHelp.textContent,/native habitat checks/);}
 const rows=nodes.additionTable.children[1].children;
 if(rows.length){rows[0].children[2].children[0].listeners.click();assert.equal(window.MapLab.snapshot().selected,preview.assistance.additions[0].plot);rows[0].children[5].children[0].listeners.click();assert.equal(window.MapLab.snapshot().selected,preview.assistance.additions[0].center);}
}
if(!process.argv.includes('--preview-only')){
 const automatic=bundle.maps.filter(m=>m.group==='csc-helper-lua');
 if(automatic.length){
  change('setup','csc-helper-lua');
  assert.equal(nodes.coverageTable.children[1].children[1].children[5].textContent,'≈15/15');
  assert.equal(nodes.coverageTable.children[1].children[6].children[5].textContent,'≈8/15');
  assert.match(nodes.assistanceHelp.textContent,/163.6%/);
 }
 change('setup','luxuries-4');assert.equal(nodes.assistancePanel.hidden,true);assert.equal(nodes.versionField.hidden,true);
}
change('setup','csc-assist');change('continent',-1);change('version','before');assert.match(nodes.status.textContent,/CSC helper preview/);
assert.ok(drawCalls>0);console.log(JSON.stringify({passed:true,viewerControlChecks:checks,drawCalls,visualRenderingTested:false}));
