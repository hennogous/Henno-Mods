'use strict';
// Finite observer only: no game/Lua calls, score writes or requested actions.
const BAKERS_SHA='324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c';
const BAKERS_POINTS={
 BuildingValue:[0x52b900,'44894c24204c894424188954241048894c24085557488dac2428feffff4881ec'],
 ModifierValue:[0x529ed0,'488bc455574154415641574881ec20010000498b384d8bf9418b68104c8be248'],
 BaseYield:[0x4818c0,'40534883ec50488bda4d85c0750832c04883c4505bc348837a78000f849b0000'],
 CalculateDistrictValues:[0x3dfee0,'4c8bdc41554881eca000000083b9d8040000004c8be90f84ae030000488b91c8'],
};
const BAKERS_TYPES=['RIVER_ACCESS','NO_RIVER_ACCESS','WIND_MILL','WATER_MILL','BAKERY','CAFE'].map(x=>'BUILDING_CSC_BAKERS_'+x);
function validateBakersConfig(c){
 const integer=(v,a,b)=>Number.isInteger(v)&&v>=a&&v<=b;
 if(c.profile!=='bakers-components-v1'||c.mappingVerified!==true)throw Error('Reviewed Bakers mapping required');
 if(!integer(c.buildingCount,1,4096)||!integer(c.districtCount,1,4096)||!integer(c.districtIndex,0,c.districtCount-1))throw Error('Definition bounds');
 if(!integer(c.mapWidth,1,256)||!integer(c.mapHeight,1,256))throw Error('Map bounds');
 if(!Array.isArray(c.buildings)||c.buildings.length!==6||new Set(c.buildings.map(x=>x.index)).size!==6||
    c.buildings.some(x=>!BAKERS_TYPES.includes(x.type)||!integer(x.index,0,c.buildingCount-1))||
    new Set(c.buildings.map(x=>x.type)).size!==6)throw Error('Six exact Bakers definitions required');
 if(!Array.isArray(c.targets)||c.targets.length!==2||
    JSON.stringify(c.targets.map(x=>[x.player,x.city]).sort((a,b)=>a[0]-b[0]))!==JSON.stringify([[3,65536],[5,65536]]))throw Error('Only declared Delhi/Majapahit targets');
 for(const [k,v]of Object.entries({maxPairs:4096,maxCallbacks:200000,maxThreads:8,maxDepth:16,maxRows:37}))if(c[k]!==v)throw Error('Unreviewed bound '+k);
}
function makeBakersObserver(io,cfg){
 validateBakersConfig(cfg);
 cfg=JSON.parse(JSON.stringify(cfg)); // Caller cannot widen the reviewed window.
 const targets=new Set(cfg.targets.map(x=>x.player+':'+x.city)),family=new Set(cfg.buildings.map(x=>x.index));
 const stacks=new Map(),records=[],faults=[];
 let started=false,accepting=false,freezing=false,frozen=false,pending=0,pairedPending=0,next=0,sequence=0,stopReason=null;
 const stats={callbacks:0,acceptedPairs:0,completedPairs:0,barriers:0,suppressed:0,errors:0};
 const counts=Object.fromEntries(Object.keys(BAKERS_POINTS).map(x=>[x,{entries:0,accepted:0}]));
 const nil=p=>p===null||p===undefined||p==='0x0';
 const stack=t=>stacks.get(t)||[];
 function stop(reason){accepting=false;stopReason=stopReason||reason;}
 function fault(reason){stats.errors++;stop(reason);if(faults.length<16)faults.push({sequence:++sequence,reason});}
 function read(p,o,t){const r=io.read(p,o,t);if(r.error)throw Error('read '+t+' '+o+': '+r.error);return r.value;}
 function who(p){if(nil(p))return null;return{pointer:p,player:read(p,0xd8,'i32'),city:read(p,0xa8,'i32')};}
 const targeted=w=>w&&targets.has(w.player+':'+w.city);
 const same=(a,b)=>a&&b&&a.pointer===b.pointer&&a.player===b.player&&a.city===b.city;
 function currentBuilding(t){const s=stack(t);for(let i=s.length-1;i>=0;i--){if(s[i].barrier)return null;if(s[i].kind==='BuildingValue')return s[i];}return null;}
 function push(f,paired){
  const s=stack(f.thread);
  if((!stacks.has(f.thread)&&stacks.size>=cfg.maxThreads)||s.length>=cfg.maxDepth){fault('scope_bound');return null;}
  if(paired&&records.length+pairedPending>=cfg.maxPairs){stop('pair_budget');stats.suppressed++;return null;}
  f.id=++next;f.entrySequence=++sequence;f.paired=paired;
  s.push(f);stacks.set(f.thread,s);pending++;
  if(paired){pairedPending++;stats.acceptedPairs++;counts[f.kind].accepted++;}
  else stats.barriers++;
  return f;
 }
 function barrier(kind,a){if(!stack(a.thread).length)return null;return push({kind,thread:a.thread,barrier:true},false);}
 function cache(object,w){
  const rows=read(object,0x4d8,'u32'),out={rows,status:'unready',rawBuildingQ8:[],mutableBuildingQ8:[],districtRows:[]};
  if(rows===0)return out;
  if(rows>cfg.maxRows)throw Error('row_count_bound');
  const base=read(object,0x4c8,'ptr');if(nil(base))throw Error('null_rows');
  const x=read(base,8,'i32'),y=read(base,12,'i32');
  if(x!==read(w.pointer,0xc0,'i32')||y!==read(w.pointer,0xc4,'i32'))throw Error('row0_not_city_center');
  const raw=read(base,0x28,'ptr'),mutable=read(object,0x4f0,'ptr');
  const length=read(object,0x500,'u32'),capacity=read(object,0x4f8,'u32');
  if(length!==rows*cfg.buildingCount||capacity<length||capacity>37*4096||nil(raw)||nil(mutable))throw Error('building_vector_bounds');
  // Record both identities: native district aggregation reads the row vector;
  // dependent propagation writes the mutable vector. Never substitute one.
  out.rawPointer=raw;out.mutablePointer=mutable;out.rawAliasesMutable=raw===mutable;
  for(const b of cfg.buildings){out.rawBuildingQ8.push({index:b.index,type:b.type,value:read(raw,b.index*4,'i32')});out.mutableBuildingQ8.push({index:b.index,type:b.type,value:read(mutable,b.index*4,'i32')});}
  for(let i=0;i<rows;i++){
   const row=io.add(base,i*0x78),rx=read(row,8,'i32'),ry=read(row,12,'i32');
   if(rx<0||ry<0||rx>=cfg.mapWidth||ry>=cfg.mapHeight)throw Error('row_coordinate_bound');
   const scores=read(row,0x20,'ptr');if(nil(scores))throw Error('null_district_scores');
   out.districtRows.push({row:i,x:rx,y:ry,plot:ry*cfg.mapWidth+rx,eligible:read(row,0x55,'u8'),owned:read(row,0x5a,'u8'),adjacentOwned:read(row,0x57,'u8'),value:read(scores,cfg.districtIndex*4,'i32')});
  }
  out.status='observed';return out;
 }
 function analysis(p){
  const district=read(p,0x78,'ptr'),city=read(p,0x70,'ptr');
  const result={pointer:p,candidateBuilding:read(p,4,'i32'),cityId:read(p,0x14,'i32'),cityPointer:city,districtPointer:district,playerPointer:read(p,0x80,'ptr'),plotPointer:read(p,0x88,'ptr'),ready:read(p,0xb4,'i32'),horizon:read(p,0xb8,'i32'),discountFloat:read(p,0xbc,'f32'),yieldIndex:read(p,0x64,'i32'),accumulator:read(p,0xc0,'i32')};
  result.districtType=nil(district)?null:read(district,0xf0,'i32');
  return result;
 }
 function enter(kind,a){
  if(!Object.hasOwn(BAKERS_POINTS,kind))throw Error('Unknown boundary');
  if(!started||frozen)return null;
  stats.callbacks++;counts[kind].entries++;
  if(stats.callbacks>cfg.maxCallbacks){stop('callback_budget');return barrier(kind,a);}
  if(stats.errors)return barrier(kind,a);
  const nested=!!currentBuilding(a.thread);
  if((!accepting&&!nested)||(freezing&&!nested))return barrier(kind,a);
  try{
   if(kind==='BuildingValue'){
    if(!family.has(a.building))return barrier(kind,a);
    const identity=who(a.city);if(!targeted(identity))return barrier(kind,a);
    const entry={identity,building:a.building,buildingType:cfg.buildings.find(b=>b.index===a.building).type,discountQ8:read(a.discount,0,'i32'),ready:a.ready,horizon:a.horizon,
     coordinates:{x:read(a.coordinates,0,'i32'),y:read(a.coordinates,4,'i32')}};
    return push({kind,thread:a.thread,args:a,identity,entry},true);
   }
   if(kind==='CalculateDistrictValues'){
    const identity=who(read(a.object,0x90,'ptr'));if(!targeted(identity))return null;
    return push({kind,thread:a.thread,args:a,identity,entry:{identity,cache:cache(a.object,identity)}},true);
   }
   const parent=currentBuilding(a.thread);if(!parent)return null;
   const entry={buildingCallId:parent.id,building:parent.entry.building,identity:parent.identity,analysis:analysis(a.analysis)};
   if(entry.analysis.cityPointer!==parent.identity.pointer||entry.analysis.candidateBuilding!==parent.entry.building)throw Error('nested_analysis_identity');
   if(kind==='BaseYield'){
    if(nil(a.data))return null;
    entry.amount=read(a.data,8,'i32');entry.effectYieldIndex=read(a.data,12,'i32');
   }else{
    const count=read(a.vector,0x10,'u32'),capacity=read(a.vector,8,'u32');
    if(count>4096||capacity<count||capacity>4096)throw Error('modifier_vector_bound');
    entry.modifierCount=count;
   }
   return push({kind,thread:a.thread,args:a,identity:parent.identity,entry,parentId:parent.id},true);
  }catch(e){fault(String(e));return barrier(kind,a);}
 }
 function leave(f,returnPointer){
  if(!f)return;
  const s=stack(f.thread);
  if(s[s.length-1]!==f){fault('unbalanced_scope');return;}
  s.pop();if(!s.length)stacks.delete(f.thread);pending--;
  if(!f.paired)return;
  pairedPending--;
  const leave={sequence:++sequence};
  try{
   if(stats.errors)leave.incompleteReason='observer_fault';
   else if(f.kind==='CalculateDistrictValues'){
    const w=who(read(f.args.object,0x90,'ptr'));if(!same(w,f.identity))throw Error('city_identity_changed');
    leave.identity=w;leave.cache=cache(f.args.object,w);
   }else if(f.kind==='BaseYield'){
    leave.analysis=analysis(f.args.analysis);
    if(leave.analysis.cityPointer!==f.entry.analysis.cityPointer||leave.analysis.candidateBuilding!==f.entry.analysis.candidateBuilding)throw Error('analysis_identity_changed');
    leave.accumulatorDelta=leave.analysis.accumulator-f.entry.analysis.accumulator;
   }else{
    if(returnPointer!==f.args.out)throw Error('output_pointer_changed');
    leave.valueQ8=read(f.args.out,0,'i32');
   }
  }catch(e){leave.incompleteReason=String(e);fault(String(e));}
  if(stopReason==='pair_budget'||stopReason==='callback_budget')leave.captureMayBeIncomplete=stopReason;
  records.push({kind:f.kind,id:f.id,thread:f.thread,entrySequence:f.entrySequence,parentId:f.parentId||null,callerRva:f.args.callerRva||null,entry:f.entry,leave});
  stats.completedPairs++;
 }
 function status(){return{profile:cfg.profile,read_only:true,started,enabled:accepting,freezing,frozen,pendingPairs:pairedPending,pendingFrames:pending,stopReason,stats:{...stats},counts:JSON.parse(JSON.stringify(counts)),faults:[...faults]};}
 return{enter,leave,fault,start(){if(started||frozen||stats.errors)throw Error('Single clean window required');started=true;accepting=true;return status();},
  status,snapshot(){return{...status(),records:[...records],config:cfg};},
  requestFreeze(){accepting=false;freezing=true;return status();},finishFreeze(){if(pending!==0)throw Error('Native callbacks remain in flight');frozen=true;return this.snapshot();}};
}
function createBakersMemoryIO(api){return{
 add(address,offset){return api.ptr(address).add(offset).toString();},
 read(address,offset,type){
  const size={ptr:8,i32:4,u32:4,u8:1,f32:4}[type];
  if(!Number.isSafeInteger(offset)||offset<0||!size)return{error:'invalid_argument',value:null};
  try{
   const p=api.ptr(address),max=api.ptr('0x7fffffffffff');
   if(p.isNull()||p.compare(api.ptr('0x10000'))<0||p.compare(max)>0)return{error:'noncanonical_pointer',value:null};
   const start=p.add(offset),end=start.add(size-1);
   if(start.compare(p)<0||end.compare(start)<0||end.compare(max)>0)return{error:'address_overflow',value:null};
   const r=api.findRangeByAddress(start);
   if(!r||!r.protection.includes('r')||end.compare(r.base.add(r.size))>=0)return{error:'unreadable_span',value:null};
   const value=type==='ptr'?start.readPointer().toString():type==='i32'?start.readS32():type==='u32'?start.readU32():type==='u8'?start.readU8():start.readFloat();
   if(type==='f32'&&!Number.isFinite(value))return{error:'nonfinite_float',value:null};
   return{value};
  }catch(_){return{error:'read_exception',value:null};}
 }
};}
function decodeBakersArgs(kind,a,thread,callerRva){
 const common={thread,callerRva};
 if(kind==='CalculateDistrictValues')return{...common,object:a[0].toString()};
 if(kind==='BuildingValue')return{...common,out:a[0].toString(),building:a[1].toInt32(),discount:a[2].toString(),ready:a[3].toInt32(),horizon:a[4].toInt32(),player:a[5].toString(),city:a[6].toString(),coordinates:a[7].toString(),changes:a[8].toString()};
 if(kind==='ModifierValue')return{...common,out:a[0].toString(),analysis:a[1].toString(),vector:a[2].toString(),changes:a[3].toString()};
 return{...common,analysis:a[1].toString(),data:a[2].toString()};
}
if(typeof module!=='undefined'&&module.exports)module.exports={BAKERS_SHA,BAKERS_POINTS,BAKERS_TYPES,validateBakersConfig,makeBakersObserver,createBakersMemoryIO,decodeBakersArgs};
else{
 let observer=null,moduleInfo=null,listeners=[],initError=null,validated=null;
 const pathKey=p=>String(p).replace(/\\/g,'/').toLowerCase();
 function init(spec,cfg){
  if(observer||listeners.length||initError)throw Error('Single initialization only');
  try{
   validateBakersConfig(cfg);
   if(Process.platform!=='windows'||Process.arch!=='x64'||Process.pointerSize!==8)throw Error('Windows x64 required');
   if(spec.sha256!==BAKERS_SHA||spec.image_size!==12976128||spec.timestamp!==1719431003||typeof spec.path!=='string')throw Error('Unreviewed original GameCore identity');
   if(Process.enumerateModules().some(m=>/GameCore_XP2_(?:CE|CSC)/i.test(m.name)))throw Error('Native carrier conflict');
   const matches=Process.enumerateModules().filter(m=>pathKey(m.path)===pathKey(spec.path));
   if(matches.length!==1)throw Error('Exact loaded original module required');
   const m=matches[0];if(m.size!==spec.image_size||m.base.readU16()!==0x5a4d)throw Error('Module size/header');
   const off=m.base.add(0x3c).readU32();if(off<0x40||off>m.size-0x58)throw Error('PE header offset');
   const pe=m.base.add(off);
   if(pe.readU32()!==0x4550||pe.add(0x18).readU16()!==0x20b||pe.add(8).readU32()!==spec.timestamp||pe.add(0x50).readU32()!==spec.image_size)throw Error('Loaded PE identity');
   if(!Array.isArray(spec.functions)||spec.functions.length!==4||new Set(spec.functions.map(f=>f.name)).size!==4)throw Error('Four exact hooks required');
   for(const f of spec.functions){
    const expected=BAKERS_POINTS[f.name];if(!expected||expected[0]!==f.rva||expected[1]!==f.bytes)throw Error('Unreviewed function');
    const actual=Array.from(new Uint8Array(m.base.add(f.rva).readByteArray(32)),b=>b.toString(16).padStart(2,'0')).join('');
    if(actual!==f.bytes)throw Error('Loaded entry fingerprint '+f.name);
   }
   moduleInfo={path:m.path,size:m.size,base:m.base.toString(),timestamp:spec.timestamp,sha256_host_verified:spec.sha256};validated=spec.functions;
   const io=createBakersMemoryIO({ptr,findRangeByAddress:p=>Process.findRangeByAddress(p)});
   observer=makeBakersObserver(io,cfg);
   for(const f of spec.functions)listeners.push(Interceptor.attach(m.base.add(f.rva),{
    onEnter(args){this.capture=null;try{const r=this.returnAddress,caller=r.compare(m.base)>=0&&r.compare(m.base.add(m.size))<0?r.sub(m.base).toString():null;this.capture=observer.enter(f.name,decodeBakersArgs(f.name,args,this.threadId,caller));}catch(e){observer.fault('entry '+f.name+': '+String(e));}},
    onLeave(ret){try{observer.leave(this.capture,ret.toString());}catch(e){observer.fault('leave '+f.name+': '+String(e));}},
   }));
   Interceptor.flush();return rpc.exports.status();
  }catch(e){initError=String(e);if(observer)observer.fault(initError);throw e;}
 }
 rpc.exports={init,start(){if(!observer||listeners.length!==4||initError)throw Error('Complete disabled installation required');return observer.start();},
  status(){return{installed:listeners.length===4&&!initError,hooks:listeners.length,initError,module:moduleInfo,validated_entry_fingerprints:validated,...(observer?observer.status():{enabled:false,read_only:true})};},
  snapshot(){if(!observer)throw Error('Not initialized');return observer.snapshot();},
  async freeze(){if(!observer)throw Error('Not initialized');observer.requestFreeze();const deadline=Date.now()+5000;
   while(observer.status().pendingFrames!==0){if(Date.now()>=deadline)throw Error('Callback drain deadline; preserve attached owner');await new Promise(resolve=>setTimeout(resolve,10));}
   return observer.finishFreeze();}
 };
 // Deliberately no detach/unload/reconfigure RPC while native code is alive.
}
