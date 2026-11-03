'use strict';
// Four city boundaries only. Passive reads; no engine calls or mutation.
const IZ_POINTS={CalculateDistrictValues:0x3dfee0,GetBestBuilding:0x3e4710,QueueNextBuild:0x3e8190,BuildBuilding:0x3df040};
function validateIndustrialConfig(c){
 if(c.profile!=='industrial-zone-decision-v1'||c.mappingVerified!==true)throw Error('Explicit reviewed IZ mapping required');
 for(const [key,lo,hi]of[['buildingIndexLimit',1,4096]])
  if(!Number.isInteger(c[key])||c[key]<lo||c[key]>hi)throw Error('Invalid IZ scope/index bound: '+key);
 if(!Array.isArray(c.targets)||c.targets.length<1||c.targets.length>2)throw Error('One or two declared IZ targets required');
 const targetKeys=new Set();
 for(const t of c.targets){
  if(!t||!Number.isInteger(t.player)||t.player<1||t.player>61||!Number.isInteger(t.city)||t.city<0||t.city>2147483647)throw Error('Invalid IZ target');
  const key=t.player+':'+t.city;if(targetKeys.has(key))throw Error('Duplicate IZ target');targetKeys.add(key);
 }
 for(const key of['workshopIndex','factoryIndex'])if(!Number.isInteger(c[key])||c[key]<0||c[key]>=c.buildingIndexLimit)throw Error('Invalid IZ mapped index: '+key);
 if(c.workshopIndex===c.factoryIndex||c.workshopType!=='BUILDING_WORKSHOP'||c.factoryType!=='BUILDING_FACTORY')throw Error('Wrong IZ building identities');
 for(const [key,value]of Object.entries({maxPairs:64,maxCallbacks:10000,maxRows:64,maxThreads:8,maxScopeDepth:16}))if(c[key]!==value)throw Error('Unreviewed IZ bound: '+key);
}
function makeIndustrialObserver(io,cfg){
 validateIndustrialConfig(cfg);
 let started=false,enabled=false,frozen=false,saturated=false,stopReason=null,seq=0,next=0,pending=0,freezePending=null;
 const lastCalculations=new Map(),targetKeys=new Set(cfg.targets.map(t=>t.player+':'+t.city));
 const records=[],stacks=new Map(),stats={callbacks:0,completedPairs:0,errors:0,identityChanges:0,budgetSuppressed:0};
 const diagnostics=Object.fromEntries(Object.keys(IZ_POINTS).map(k=>[k,{entries:0,accepted:0,rejected:{}}]));
 const nil=p=>p===null||p===undefined||p==='0x0';
 function stop(reason){enabled=false;saturated=true;if(stopReason===null)stopReason=reason;}
 function fail(reason){stats.errors++;stop(reason);}
 function tick(){if(!started||frozen)return;stats.callbacks++;if(stats.callbacks>=cfg.maxCallbacks)stop('callback_budget');}
 function read(p,o,t,e,key){const v=io.read(p,o,t);if(v.error){e[key]=v.error;fail('read_error');return null;}return v.value;}
 function identity(object,e){const p=read(object,0x90,'ptr',e,'cityPointer');if(nil(p))return null;return{pointer:p,owner:read(p,0xd8,'i32',e,'owner'),city:read(p,0xa8,'i32',e,'city')};}
 const same=(a,b)=>a&&b&&a.pointer===b.pointer&&a.owner===b.owner&&a.city===b.city;
 function cache(object,who,e){
  const rows=read(object,0x4d8,'u32',e,'cacheRows');
  const result={status:'unready',rows,workshopQ8:null,factoryQ8:null,freshness:'not_established_by_this_observer'};
  if(rows===null){result.status='read_error';return result;}
  if(rows===0)return result; // Preserve native early-return boundary before pointer access.
  if(rows>cfg.maxRows){result.status='invalid_rows';fail('cache_rows');return result;}
  const first=read(object,0x4c8,'ptr',e,'firstRow'),payload=read(object,0x4f0,'ptr',e,'buildingPayload');
  const length=read(object,0x500,'u32',e,'buildingLength'),capacity=read(object,0x4f8,'u32',e,'buildingCapacity');
  Object.assign(result,{firstRow:first,payload,length,capacity});
  if(nil(first)||nil(payload)){result.status='missing_pointer';fail('cache_pointer');return result;}
  if(length!==rows*cfg.buildingIndexLimit||capacity===null||capacity<length||capacity>cfg.maxRows*4096){result.status='invalid_vector_bounds';fail('cache_bounds');return result;}
  const alias=read(first,0x28,'ptr',e,'firstBuildingPayload');
  const xy={x:read(first,8,'i32',e,'firstX'),y:read(first,12,'i32',e,'firstY')};
  const cityXY={x:read(who.pointer,0xc0,'i32',e,'cityX'),y:read(who.pointer,0xc4,'i32',e,'cityY')};
  Object.assign(result,{firstBuildingPayload:alias,firstXY:xy,cityXY,aliasVerified:alias===payload,cityCenterVerified:xy.x===cityXY.x&&xy.y===cityXY.y&&xy.x!==null&&xy.y!==null});
  if(!result.aliasVerified||!result.cityCenterVerified){result.status='alias_or_city_center_mismatch';fail('cache_alias');return result;}
  result.workshopQ8=read(payload,cfg.workshopIndex*4,'i32',e,'workshopQ8');
  result.factoryQ8=read(payload,cfg.factoryIndex*4,'i32',e,'factoryQ8');
  result.status=result.workshopQ8===null||result.factoryQ8===null?'read_error':'observed';return result;
 }
 function topQueue(thread){const s=stacks.get(thread)||[];for(let i=s.length-1;i>=0;i--)if(s[i].kind==='QueueNextBuild')return s[i];return null;}
 function enter(kind,a){
  if(!Object.hasOwn(IZ_POINTS,kind))throw Error('Unknown IZ boundary');
  tick();if(!started||frozen)return null;
  const d=diagnostics[kind];d.entries++;
  const reject=reason=>{d.rejected[reason]=(d.rejected[reason]||0)+1;return null;};
  if(!enabled){stats.budgetSuppressed++;return reject('stopped');}
  const errors={},who=identity(a.object,errors);
  if(!who||!targetKeys.has(who.owner+':'+who.city))return reject('owner_or_city');
  const s=stacks.get(a.thread)||[];
  if(!stacks.has(a.thread)&&stacks.size>=cfg.maxThreads){fail('thread_bound');return reject('thread_bound');}
  if(s.length>=cfg.maxScopeDepth){fail('scope_depth');return reject('scope_depth');}
  if(records.length+pending>=cfg.maxPairs){stop('pair_budget');return reject('pair_budget');}
  if(kind==='BuildBuilding'&&(!Number.isInteger(a.buildingIndex)||a.buildingIndex<0||a.buildingIndex>=cfg.buildingIndexLimit)){fail('build_index');return reject('build_index');}
  const q=topQueue(a.thread),call={kind,args:Object.assign({},a),identity:who,callId:++next,entrySequence:++seq,queueCallId:q&&same(q.identity,who)?q.callId:null,lastCompletedCalculationId:lastCalculations.get(who.owner+':'+who.city)||null,
   entry:{identity:who,readErrors:errors}};
  call.entry.cache=cache(a.object,who,errors);
  if(kind==='GetBestBuilding')call.entry.flags={r8ByteRaw:a.r8ByteRaw,r9ByteRaw:a.r9ByteRaw};
  if(kind==='BuildBuilding'){
   call.entry.requestedBuildingIndex=a.buildingIndex;
   call.entry.requestedValueQ8=read(a.score,0,'i32',errors,'requestedValueQ8');
  }
  if(!enabled&&stopReason!=='pair_budget')return reject('entry_read_or_bounds');
  s.push(call);stacks.set(a.thread,s);pending++;d.accepted++;
  if(records.length+pending===cfg.maxPairs)stop('pair_budget');
  return call;
 }
 function leave(call,signedReturn,rawReturn,lowByte){
  tick();if(!call)return;
  const s=stacks.get(call.args.thread)||[];
  if(s[s.length-1]!==call){fail('scope_unbalanced');}else s.pop();
  const errors={},out={sequence:++seq,readErrors:errors};
  if(frozen)out.inertReason='frozen_before_return';
  else if(stats.errors)out.inertReason='observer_error';
  else{
   const who=identity(call.args.object,errors);out.identity=who;out.identityCorrelated=same(call.identity,who);
   if(!out.identityCorrelated){stats.identityChanges++;stop('identity_changed');out.inertReason='identity_changed';}
   else{
    out.cache=cache(call.args.object,who,errors);
    if(call.kind==='GetBestBuilding'){
     out.selectedBuildingIndex=signedReturn;out.selectedValueQ8=null;
     if(signedReturn===-1)out.selectionStatus='no_building';
     else if(Number.isInteger(signedReturn)&&signedReturn>=0&&signedReturn<cfg.buildingIndexLimit){out.selectionStatus='valid_index';out.selectedValueQ8=read(call.args.output,0,'i32',errors,'selectedValueQ8');}
     else{out.selectionStatus='invalid_return_index';fail('winner_index');}
    }else if(call.kind==='BuildBuilding'){
     if(!Number.isInteger(lowByte)||lowByte<0||lowByte>255){fail('invalid_return_AL');out.inertReason='invalid_return_AL';}
     else{out.returnAL=lowByte;out.accepted=lowByte!==0;}out.rawReturnUninterpreted=rawReturn;
    }else out.rawReturnUninterpreted=rawReturn; // Both other boundaries return void.
   }
  }
  records.push({kind:call.kind,callId:call.callId,entrySequence:call.entrySequence,thread:call.args.thread,callerRva:call.args.callerRva,queueCallId:call.queueCallId,
   lastCompletedCalculationId:call.lastCompletedCalculationId,entry:call.entry,leave:out});
  pending--;stats.completedPairs++;
  if(call.kind==='CalculateDistrictValues'&&!out.inertReason&&out.cache&&out.cache.status==='observed')lastCalculations.set(call.identity.owner+':'+call.identity.city,call.callId);
 }
 return{stats,enter,leave,abort:fail,start(){if(started||frozen)throw Error('IZ observer cannot restart');started=true;enabled=true;return{enabled};},
  status(){return{enabled};},snapshot(){return{profile:cfg.profile,read_only:true,paired:true,enabled,saturated,stopReason,records,stats,diagnostics,pendingPairs:pending,frozenPendingPairs:freezePending};},
  freeze(){if(!frozen)freezePending=pending;frozen=true;enabled=false;return this.snapshot();}};
}
function decodeIndustrialArgs(kind,c,thread,callerRva){return{object:c.rcx.toString(),thread,callerRva,
 output:kind==='GetBestBuilding'?c.rdx.toString():null,r8ByteRaw:kind==='GetBestBuilding'?c.r8.toUInt32()&255:null,r9ByteRaw:kind==='GetBestBuilding'?c.r9.toUInt32()&255:null,
 buildingIndex:kind==='BuildBuilding'?c.rdx.toInt32():null,score:kind==='BuildBuilding'?c.r8.toString():null};}
function createIndustrialMemoryIO(api){return{read(address,offset,type){
 const size={ptr:8,i32:4,u32:4}[type];if(!Number.isSafeInteger(offset)||offset<0||!size)return{value:null,error:'invalid_argument'};
 try{
  const p=api.ptr(address),max=api.ptr('0x7fffffffffff');if(p.isNull())return{value:null,error:'null_pointer'};
  if(p.compare(api.ptr('0x10000'))<0||p.compare(max)>0)return{value:null,error:'noncanonical_pointer'};
  const point=p.add(offset),last=point.add(size-1);if(point.compare(p)<0||last.compare(point)<0||last.compare(max)>0)return{value:null,error:'address_overflow'};
  const range=api.findRangeByAddress(point);if(!range||!range.protection.includes('r')||last.compare(range.base.add(range.size))>=0)return{value:null,error:'unreadable_span'};
  return{value:type==='ptr'?point.readPointer().toString():type==='u32'?point.readU32():point.readS32()};
 }catch(_){return{value:null,error:'read_exception'};}
}};}
if(typeof module!=='undefined'&&module.exports)module.exports={IZ_POINTS,validateIndustrialConfig,makeIndustrialObserver,decodeIndustrialArgs,createIndustrialMemoryIO};
else{
 const spec=__SPEC__,cfg=__CONFIG__;validateIndustrialConfig(cfg);
 const m=Process.getModuleByName('GameCore_XP2_FinalRelease.dll');
 if(m.path.toLowerCase()!==spec.path.toLowerCase()||m.size!==spec.image_size)throw Error('Loaded IZ module path/size mismatch');
 if(Process.enumerateModules().some(x=>/GameCore_XP2_CE/i.test(x.name)))throw Error('CE proxy loaded');
 const pe=m.base.add(m.base.add(0x3c).readU32());if(pe.add(8).readU32()!==spec.timestamp)throw Error('Loaded IZ module timestamp mismatch');
 if(spec.functions.length!==4||new Set(spec.functions.map(f=>f.name)).size!==4)throw Error('Wrong IZ hook set');
 for(const f of spec.functions){if(IZ_POINTS[f.name]!==f.rva)throw Error('Unreviewed IZ boundary');const bytes=Array.from(new Uint8Array(m.base.add(f.rva).readByteArray(32))).map(v=>v.toString(16).padStart(2,'0')).join('');if(bytes!==f.bytes)throw Error('IZ boundary fingerprint mismatch');}
 const io=createIndustrialMemoryIO({ptr,findRangeByAddress:p=>Process.findRangeByAddress(p)}),ob=makeIndustrialObserver(io,cfg),hooks=[];
 for(const f of spec.functions)hooks.push(Interceptor.attach(m.base.add(f.rva),{
  onEnter(){this.observation=null;try{const r=this.returnAddress,caller=r.compare(m.base)>=0&&r.compare(m.base.add(m.size))<0?r.sub(m.base).toString():null;this.observation=ob.enter(f.name,decodeIndustrialArgs(f.name,this.context,this.threadId,caller));}catch(_){ob.abort('entry_exception');}},
  onLeave(ret){try{ob.leave(this.observation,ret.toInt32(),ret.toString(),ret.toUInt32()&255);}catch(_){ob.abort('leave_exception');}}
 }));
 rpc.exports={status(){return{installed:true,hooks:hooks.length,enabled:ob.status().enabled,module_path:m.path,module_size:m.size,loaded_timestamp:pe.add(8).readU32(),validated_entry_fingerprints:spec.functions,config:cfg,read_only:true};},
  start(){return ob.start();},snapshot(){return ob.snapshot();},freeze(){return ob.freeze();}};
}
