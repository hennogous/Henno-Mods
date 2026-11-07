'use strict';
// Finite observer only: no game/Lua calls, score writes or requested actions.
const STUDY_SHA='324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c';
// The November Steam hotfix has identical XP2 instructions and mapped layout.
// See late_placement/audit_xp2_hotfix.py. Both loaded identities remain pinned.
const STUDY_TARGET_TIMESTAMPS=new Map([
 [STUDY_SHA,1719431003],
 ['092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f',1793649108],
]);
const STUDY_POINTS={
 BuildingValue:[0x52b900,'44894c24204c894424188954241048894c24085557488dac2428feffff4881ec'],
 ModifierValue:[0x529ed0,'488bc455574154415641574881ec20010000498b384d8bf9418b68104c8be248'],
 AnalyzeModifier:[0x48e9e0,'40535741564883ec20ff81c800000032c083b9c8000000044d8bf0488bda488b'],
 AmenityValue:[0x5272a0,'48895c241044894c24204c8944241848894c2408555657415441554156415748'],
 BaseYield:[0x4818c0,'40534883ec50488bda4d85c0750832c04883c4505bc348837a78000f849b0000'],
 CalculateDistrictValues:[0x3dfee0,'4c8bdc41554881eca000000083b9d8040000004c8be90f84ae030000488b91c8'],
};
const STUDY_TYPES=[
 ...['RIVER_ACCESS','NO_RIVER_ACCESS','WIND_MILL','WATER_MILL','BAKERY','CAFE','STAGE_2_SERVICE','STAGE_3_SERVICE','STAGE_4_SERVICE_ENTER','STAGE_4_SERVICE_WATER'].map(x=>'BUILDING_CSC_BAKERS_'+x),
 ...['TEXTILE_WORKSHOP','TAILOR','FASHION_HOUSE','STAGE_2_SERVICE','STAGE_3_SERVICE','STAGE_4_SERVICE','STAGE_4_SERVICE_BOLSHOI','STAGE_4_SERVICE_BROADWAY','STAGE_4_SERVICE_SYDNEY'].map(x=>'BUILDING_CSC_TAILORS_'+x),
];
const STUDY_LIMITS={maxPairs:16384,maxCallbacks:300000,maxThreads:8,maxDepth:16,maxRows:37,maxModifierName:256};
const GRANARY_STUDY_LIMITS={...STUDY_LIMITS,maxPairs:2048,maxCallbacks:20000};
function validateStudyConfig(c){
 const integer=(v,a,b)=>Number.isInteger(v)&&v>=a&&v<=b;
 if(c.profile==='trebizond-granary-components-v1'){
  if(c.mappingVerified!==true||c.buildings?.length!==1||c.buildings[0].type!=='BUILDING_GRANARY'||
     c.buildings[0].index!==3||c.targets?.length!==1||c.targets[0].player!==1||c.targets[0].city!==327684)
   throw Error('Reviewed Trebizond Granary mapping required');
  for(const [k,v]of Object.entries(GRANARY_STUDY_LIMITS))if(c[k]!==v)throw Error('Unreviewed Granary bound '+k);
  return;
 }
 if(c.profile!=='mill-building-study-v1'||c.mappingVerified!==true)throw Error('Reviewed study mapping required');
 if(!integer(c.buildingCount,19,4096)||!integer(c.districtCount,2,4096))throw Error('Definition bounds');
 if(!Array.isArray(c.districtIndices)||c.districtIndices.length!==2||new Set(c.districtIndices).size!==2||c.districtIndices.some(x=>!integer(x,1,c.districtCount-1)))throw Error('Two loaded district indices required');
 if(!integer(c.mapWidth,1,256)||!integer(c.mapHeight,1,256))throw Error('Map bounds');
 if(!Array.isArray(c.buildings)||c.buildings.length!==19||new Set(c.buildings.map(x=>x.index)).size!==19||
    c.buildings.some(x=>!STUDY_TYPES.includes(x.type)||!integer(x.index,0,c.buildingCount-1))||
    new Set(c.buildings.map(x=>x.type)).size!==19)throw Error('Nineteen exact CSC definitions required');
 if(!Array.isArray(c.targets)||c.targets.length!==2||new Set(c.targets.map(x=>x.player)).size!==2||c.targets.some(x=>![1,2].includes(x.player)||!integer(x.city,0,2147483647)))throw Error('Explicit AI1/2 target cities required');
 for(const [k,v]of Object.entries(STUDY_LIMITS))if(c[k]!==v)throw Error('Unreviewed bound '+k);
}
function makeStudyObserver(io,cfg){
 validateStudyConfig(cfg);
 cfg=JSON.parse(JSON.stringify(cfg)); // Caller cannot widen the reviewed window.
 // This immutable allowlist is a study contract, not a general capture API.
 const targets=new Set(cfg.targets.map(x=>x.player+':'+x.city)),family=new Set(cfg.buildings.map(x=>x.index));
 const stacks=new Map(),records=[],faults=[];
 let started=false,accepting=false,freezing=false,frozen=false,pending=0,pairedPending=0,next=0,sequence=0,stopReason=null;
 const stats={callbacks:0,acceptedPairs:0,completedPairs:0,barriers:0,suppressed:0,errors:0};
 const counts=Object.fromEntries(Object.keys(STUDY_POINTS).map(x=>[x,{entries:0,accepted:0}]));
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
  if(paired&&!f.parentId){for(let i=s.length-1;i>=0;i--){if(s[i].barrier)break;if(s[i].paired){f.parentId=s[i].id;break;}}}
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
  // CalculateDistrictValues edits FAutoVariable+508. Its edit helper returns
  // +10, so retain the actual district matrix separately from row bindings.
  const districtMutable=read(object,0x518,'ptr'),districtLength=read(object,0x528,'u32'),districtCapacity=read(object,0x520,'u32');
  if(districtLength!==rows*cfg.districtCount||districtCapacity<districtLength||districtCapacity>37*4096||nil(districtMutable))throw Error('district_vector_bounds');
  out.mutableDistrictPointer=districtMutable;out.mutableDistrictLength=districtLength;out.mutableDistrictCapacity=districtCapacity;
  // Record both identities: native district aggregation reads the row vector;
  // dependent propagation writes the mutable vector. Never substitute one.
  out.rawPointer=raw;out.mutablePointer=mutable;out.rawAliasesMutable=raw===mutable;
  for(const b of cfg.buildings){out.rawBuildingQ8.push({index:b.index,type:b.type,value:read(raw,b.index*4,'i32')});out.mutableBuildingQ8.push({index:b.index,type:b.type,value:read(mutable,b.index*4,'i32')});}
  for(let i=0;i<rows;i++){
   const row=io.add(base,i*0x78),rx=read(row,8,'i32'),ry=read(row,12,'i32');
   if(rx<0||ry<0||rx>=cfg.mapWidth||ry>=cfg.mapHeight)throw Error('row_coordinate_bound');
   const scores=read(row,0x20,'ptr');if(nil(scores))throw Error('null_district_scores');
   const mutableRow=io.add(districtMutable,i*cfg.districtCount*4);
   out.districtRows.push({row:i,x:rx,y:ry,plot:ry*cfg.mapWidth+rx,eligible:read(row,0x55,'u8'),owned:read(row,0x5a,'u8'),adjacentOwned:read(row,0x57,'u8'),rawPointer:scores,mutableRowPointer:mutableRow,rawAliasesMutable:scores===mutableRow,
    districtValues:cfg.districtIndices.map(district=>({district,value:read(scores,district*4,'i32')})),
    mutableDistrictValues:cfg.districtIndices.map(district=>({district,value:read(mutableRow,district*4,'i32')}))});
  }
  out.status='observed';return out;
 }
 function analysis(p){
  const district=read(p,0x78,'ptr'),city=read(p,0x70,'ptr');
  const result={pointer:p,candidateBuilding:read(p,4,'i32'),cityId:read(p,0x14,'i32'),cityPointer:city,districtPointer:district,playerPointer:read(p,0x80,'ptr'),plotPointer:read(p,0x88,'ptr'),ready:read(p,0xb4,'i32'),horizon:read(p,0xb8,'i32'),discountFloat:read(p,0xbc,'f32'),yieldIndex:read(p,0x64,'i32'),accumulator:read(p,0xc0,'i32'),nativeRecursionDepth:read(p,0xc8,'i32')};
  result.districtType=nil(district)?null:read(district,0xf0,'i32');
  return result;
 }
 // The 64-byte compiled modifier stores a standard MSVC string, not a C string.
 // Read exactly its verified size: no pointer scanning, allocation or engine call.
 function modifier(p){
  const size=read(p,0x28,'u64'),capacity=read(p,0x30,'u64');
  if(!Number.isSafeInteger(size)||!Number.isSafeInteger(capacity)||size<0||size>cfg.maxModifierName||capacity<size||capacity>4096)throw Error('modifier_name_bound');
  const namePointer=capacity<16?io.add(p,0x18):read(p,0x18,'ptr');
  const raw=size?io.readBytes(namePointer,0,size):{value:[]};
  if(raw.error)throw Error('modifier_name_read: '+raw.error);
  if(raw.value.length!==size||raw.value.some(x=>!Number.isInteger(x)||x<0x20||x>0x7e))throw Error('modifier_name_encoding');
  const effect=read(p,0,'ptr'),collection=read(p,8,'ptr');
  const method=(object,offset)=>{if(nil(object))return null;const vtable=read(object,0,'ptr');if(nil(vtable))throw Error('null_analyzer_vtable');return read(vtable,offset,'ptr');};
  return{pointer:p,name:String.fromCharCode(...raw.value),nameSize:size,nameCapacity:capacity,effectPointer:effect,collectionPointer:collection,
   effectAnalyzePointer:method(effect,8),collectionNextPointer:method(collection,8),subjectRequirementHash:read(p,0x10,'u32'),dataPointer:read(p,0x38,'ptr')};
 }
 function enter(kind,a){
  if(!Object.hasOwn(STUDY_POINTS,kind))throw Error('Unknown boundary');
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
   // Collection iterators can legitimately replace the subject city/district.
   // Attribute to the enclosing BuildingValue, retaining actual subject context.
   if(kind==='AmenityValue'){
    const recipient=who(a.city);
    if(!recipient||!Number.isInteger(recipient.player)||recipient.player<0||recipient.player>63||!Number.isInteger(recipient.city)||recipient.city<0)throw Error('amenity_recipient_identity');
    const entry={buildingCallId:parent.id,building:parent.entry.building,identity:parent.identity,recipient,
     recipientIsRootOwner:recipient.player===parent.identity.player,
     count:a.count,discountQ8:read(a.discount,0,'i32'),ready:a.ready,horizon:a.horizon};
    return push({kind,thread:a.thread,args:a,identity:parent.identity,entry},true);
   }
   const entry={buildingCallId:parent.id,building:parent.entry.building,identity:parent.identity,analysis:analysis(a.analysis)};
   entry.rootCityMatch=entry.analysis.cityPointer===parent.identity.pointer;
   entry.rootCandidateMatch=entry.analysis.candidateBuilding===parent.entry.building;
   if(kind==='BaseYield'){
    if(nil(a.data))return null;
    entry.amount=read(a.data,8,'i32');entry.effectYieldIndex=read(a.data,12,'i32');
   }else if(kind==='AnalyzeModifier')entry.modifier=modifier(a.descriptor);
   else{
    const count=read(a.vector,0x10,'u32'),capacity=read(a.vector,8,'u32');
    if(count>4096||capacity<count||capacity>4096)throw Error('modifier_vector_bound');
    entry.modifierCount=count;entry.descriptorBase=read(a.vector,0,'ptr');
    if(count&&nil(entry.descriptorBase))throw Error('null_modifier_vector');
   }
   return push({kind,thread:a.thread,args:a,identity:parent.identity,entry},true);
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
   }else if(f.kind==='BaseYield'||f.kind==='AnalyzeModifier'){
    leave.analysis=analysis(f.args.analysis);
    leave.accumulatorDelta=leave.analysis.accumulator-f.entry.analysis.accumulator;
    if(f.kind==='AnalyzeModifier'){leave.accepted=Number(BigInt(returnPointer)&255n);if(leave.accepted!==0&&leave.accepted!==1)throw Error('modifier_boolean_return');}
    // AnalyzeModifier resets/assigns its accumulator. Its AFTER value, not delta,
    // is the whole-utility result consumed by the enclosing ModifierValue.
   }else{
    if(returnPointer!==f.args.out)throw Error('output_pointer_changed');
    leave.valueQ8=read(f.args.out,0,'i32');
   }
  }catch(e){leave.incompleteReason=String(e);fault(String(e));}
  if(stopReason==='pair_budget'||stopReason==='callback_budget')leave.captureMayBeIncomplete=stopReason;
  const record={kind:f.kind,id:f.id,thread:f.thread,entrySequence:f.entrySequence,parentId:f.parentId||null,callerRva:f.args.callerRva||null,entry:f.entry,leave};
  records.push(record);
  stats.completedPairs++;
  return record;
 }
 function status(){return{profile:cfg.profile,read_only:true,started,enabled:accepting,freezing,frozen,pendingPairs:pairedPending,pendingFrames:pending,stopReason,stats:{...stats},counts:JSON.parse(JSON.stringify(counts)),faults:[...faults]};}
 return{enter,leave,fault,start(){if(started||frozen||stats.errors)throw Error('Single clean window required');started=true;accepting=true;return status();},
  status,snapshot(){return{...status(),records:[...records],config:cfg};},
  requestFreeze(){accepting=false;freezing=true;return status();},finishFreeze(){if(pending!==0)throw Error('Native callbacks remain in flight');frozen=true;return this.snapshot();}};
}
function createStudyMemoryIO(api){return{
 add(address,offset){return api.ptr(address).add(offset).toString();},
 read(address,offset,type){
  const size={ptr:8,u64:8,i32:4,u32:4,u8:1,f32:4}[type];
  if(!Number.isSafeInteger(offset)||offset<0||!size)return{error:'invalid_argument',value:null};
  try{
   const p=api.ptr(address),max=api.ptr('0x7fffffffffff');
   if(p.isNull()||p.compare(api.ptr('0x10000'))<0||p.compare(max)>0)return{error:'noncanonical_pointer',value:null};
   const start=p.add(offset),end=start.add(size-1);
   if(start.compare(p)<0||end.compare(start)<0||end.compare(max)>0)return{error:'address_overflow',value:null};
   const r=api.findRangeByAddress(start);
   if(!r||!r.protection.includes('r')||end.compare(r.base.add(r.size))>=0)return{error:'unreadable_span',value:null};
   const value=type==='ptr'?start.readPointer().toString():type==='i32'?start.readS32():type==='u32'?start.readU32():type==='u8'?start.readU8():type==='u64'?start.readU64().toNumber():start.readFloat();
   if(type==='f32'&&!Number.isFinite(value))return{error:'nonfinite_float',value:null};
   return{value};
  }catch(_){return{error:'read_exception',value:null};}
 },
 readBytes(address,offset,count){
  if(!Number.isSafeInteger(offset)||offset<0||!Number.isSafeInteger(count)||count<1||count>256)return{error:'invalid_byte_span',value:null};
  try{
   const p=api.ptr(address),max=api.ptr('0x7fffffffffff'),start=p.add(offset),end=start.add(count-1);
   if(p.isNull()||p.compare(api.ptr('0x10000'))<0||start.compare(p)<0||end.compare(start)<0||end.compare(max)>0)return{error:'invalid_byte_pointer',value:null};
   const r=api.findRangeByAddress(start);
   if(!r||!r.protection.includes('r')||end.compare(r.base.add(r.size))>=0)return{error:'unreadable_byte_span',value:null};
   return{value:Array.from(new Uint8Array(start.readByteArray(count)))};
  }catch(_){return{error:'byte_read_exception',value:null};}
 }
};}
function decodeStudyArgs(kind,a,thread,callerRva){
 const common={thread,callerRva};
 if(kind==='CalculateDistrictValues')return{...common,object:a[0].toString()};
 if(kind==='BuildingValue')return{...common,out:a[0].toString(),building:a[1].toInt32(),discount:a[2].toString(),ready:a[3].toInt32(),horizon:a[4].toInt32(),player:a[5].toString(),city:a[6].toString(),coordinates:a[7].toString(),changes:a[8].toString()};
 if(kind==='AmenityValue')return{...common,out:a[0].toString(),player:a[1].toString(),city:a[2].toString(),count:a[3].toInt32(),discount:a[4].toString(),ready:a[5].toInt32(),horizon:a[6].toInt32()};
 if(kind==='AnalyzeModifier')return{...common,analysis:a[0].toString(),descriptor:a[1].toString(),changes:a[2].toString()};
 if(kind==='ModifierValue')return{...common,out:a[0].toString(),analysis:a[1].toString(),vector:a[2].toString(),changes:a[3].toString()};
 return{...common,analysis:a[1].toString(),data:a[2].toString()};
}
function installStudyRuntime(createExtension){
 let observer=null,moduleInfo=null,listeners=[],initError=null,validated=null,extension=null;
 const pathKey=p=>String(p).replace(/\\/g,'/').toLowerCase();
 function init(spec,cfg){
  if(observer||listeners.length||initError)throw Error('Single initialization only');
  try{
   validateStudyConfig(cfg);
   if(Process.platform!=='windows'||Process.arch!=='x64'||Process.pointerSize!==8)throw Error('Windows x64 required');
   const timestamp=STUDY_TARGET_TIMESTAMPS.get(spec.sha256);
   if(timestamp===undefined||spec.image_size!==12976128||spec.timestamp!==timestamp||typeof spec.path!=='string')throw Error('Unreviewed original GameCore identity');
   if(Process.enumerateModules().some(m=>/GameCore_XP2_(?:CE|CSC)/i.test(m.name)))throw Error('Native carrier conflict');
   const matches=Process.enumerateModules().filter(m=>pathKey(m.path)===pathKey(spec.path));
   if(matches.length!==1)throw Error('Exact loaded original module required');
   const m=matches[0];if(m.size!==spec.image_size||m.base.readU16()!==0x5a4d)throw Error('Module size/header');
   const off=m.base.add(0x3c).readU32();if(off<0x40||off>m.size-0x58)throw Error('PE header offset');
   const pe=m.base.add(off);
   if(pe.readU32()!==0x4550||pe.add(0x18).readU16()!==0x20b||pe.add(8).readU32()!==spec.timestamp||pe.add(0x50).readU32()!==spec.image_size)throw Error('Loaded PE identity');
   if(!Array.isArray(spec.functions)||spec.functions.length!==6||new Set(spec.functions.map(f=>f.name)).size!==6)throw Error('Six exact hooks required');
   for(const f of spec.functions){
    const expected=STUDY_POINTS[f.name];if(!expected||expected[0]!==f.rva||expected[1]!==f.bytes)throw Error('Unreviewed function');
    const actual=Array.from(new Uint8Array(m.base.add(f.rva).readByteArray(32)),b=>b.toString(16).padStart(2,'0')).join('');
    if(actual!==f.bytes)throw Error('Loaded entry fingerprint '+f.name);
   }
   moduleInfo={path:m.path,size:m.size,base:m.base.toString(),timestamp:spec.timestamp,sha256_host_verified:spec.sha256};validated=spec.functions;
   const io=createStudyMemoryIO({ptr,findRangeByAddress:p=>Process.findRangeByAddress(p)});
   observer=makeStudyObserver(io,cfg);
   if(createExtension)extension=createExtension(m,io,cfg);
   for(const f of spec.functions)listeners.push(Interceptor.attach(m.base.add(f.rva),{
    onEnter(args){this.capture=null;try{const r=this.returnAddress,caller=r.compare(m.base)>=0&&r.compare(m.base.add(m.size))<0?r.sub(m.base).toString():null;this.capture=observer.enter(f.name,decodeStudyArgs(f.name,args,this.threadId,caller));}catch(e){observer.fault('entry '+f.name+': '+String(e));}},
    onLeave(ret){try{
     const record=observer.leave(this.capture,ret.toString());
     if(extension&&record?.kind==='CalculateDistrictValues'&&!record.leave.incompleteReason&&!observer.status().stopReason)
      extension.calculated(record,this.capture.args.object);
    }catch(e){observer.fault('leave '+f.name+': '+String(e));}},
   }));
   Interceptor.flush();return rpc.exports.status();
  }catch(e){initError=String(e);if(observer)observer.fault(initError);throw e;}
 }
 rpc.exports={init,start(){if(!observer||listeners.length!==6||initError)throw Error('Complete disabled installation required');const state=observer.start();if(extension)extension.start();return state;},
  status(){return{installed:listeners.length===6&&!initError,hooks:listeners.length,initError,module:moduleInfo,validated_entry_fingerprints:validated,...(observer?observer.status():{enabled:false,read_only:true})};},
  snapshot(){if(!observer)throw Error('Not initialized');const state=observer.snapshot();return extension?{...state,late:extension.snapshot()}:state;},
  async freeze(){if(!observer)throw Error('Not initialized');if(extension)extension.stop();observer.requestFreeze();const deadline=Date.now()+5000;
   while(observer.status().pendingFrames!==0){if(Date.now()>=deadline)throw Error('Callback drain deadline; preserve attached owner');await new Promise(resolve=>setTimeout(resolve,10));}
   const state=observer.finishFreeze();return extension?{...state,late:extension.snapshot()}:state;}
 };
 // Deliberately no detach/unload/reconfigure RPC while native code is alive.
}
if(typeof module!=='undefined'&&module.exports)module.exports={STUDY_SHA,STUDY_POINTS,STUDY_TYPES,STUDY_LIMITS,validateStudyConfig,makeStudyObserver,createStudyMemoryIO,decodeStudyArgs};
else if(typeof CSC_LATE_PLACEMENT_COMPOSITE==='undefined')installStudyRuntime();
