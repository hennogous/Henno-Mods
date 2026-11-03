'use strict';
// Two reviewed boundaries. Passive scalar memory reads; no native function calls.
function validateBuildingConfig(cfg) {
 if(cfg.profile!=='granary-decision-v1'||cfg.player!==3||cfg.city!==196610||cfg.buildingIndex!==3||cfg.buildingType!=='BUILDING_GRANARY'||cfg.maxPairs!==64)
  throw Error('Wrong reviewed Granary scope');
 if(cfg.mappingVerified!==true||!Number.isInteger(cfg.buildingIndexLimit)||cfg.buildingIndexLimit<=3||cfg.buildingIndexLimit>4096)
  throw Error('Reviewed native building mapping required');
}
function makeBuildingDecisionObserver(io,cfg) {
 validateBuildingConfig(cfg);
 let started=false,enabled=false,frozen=false,saturated=false,seq=0,pending=0,freezePendingAt=null;
 const records=[],queues=new Map();
 const stats={calls:0,completedPairs:0,errors:0,identityChanges:0,budgetSuppressed:0};
 const diagnostics={GetBestBuilding:{entries:0,accepted:0,rejected:{}},QueueNextBuild:{entries:0,accepted:0,rejected:{}}};
 const nil=p=>p===null||p===undefined||p==='0x0';
 function read(p,offset,type,errors,key) {
  const result=io.read(p,offset,type);
  if(result.error){stats.errors++;errors[key]=result.error;return null;}
  return result.value;
 }
 function identity(object,errors) {
  const pointer=read(object,0x90,'ptr',errors,'cityPointer');
  if(nil(pointer))return null;
  return{pointer,owner:read(pointer,0xd8,'i32',errors,'owner'),city:read(pointer,0xa8,'i32',errors,'city')};
 }
 function same(a,b){return a&&b&&a.pointer===b.pointer&&a.owner===b.owner&&a.city===b.city;}
 function scalarArray(object,offset,errors,label) {
  const container=read(object,offset,'ptr',errors,label+'Object');
  if(nil(container))return{status:'unavailable_object',value:null};
  const data=read(container,0x28,'ptr',errors,label+'Array');
  if(nil(data))return{status:'unavailable_array',value:null};
  // Mapping gate bounds the fixed index; memory IO verifies the complete span.
  const value=read(data,cfg.buildingIndex*4,'i32',errors,label+'Value');
  return{status:value===null?'read_error':'observed',value};
 }
 function signal(object,errors) {
  const pref=scalarArray(object,0x208,errors,'preference');
  const ready=read(object,0x4d8,'i32',errors,'cacheReady');
  // The established native early-return gate means a zero ready flag does not
  // authorize dereferencing the cache. Unready/missing is never a free score.
  const cache=ready===null?{status:'unknown_ready',value:null}:ready===0?{status:'unready',value:null}:scalarArray(object,0x4c8,errors,'cache');
  return{buildingIndex:cfg.buildingIndex,preferenceStatus:pref.status,favoredRaw:pref.value,
   preferenceSign:pref.value===null?null:Math.sign(pref.value),cacheReadyRaw:ready,
   cacheStatus:cache.status,cachedValueQ8:cache.value,
   cacheFreshness:'not_established_by_this_observer'};
 }
 function top(thread){const stack=queues.get(thread)||[];return stack.length?stack[stack.length-1]:null;}
 function callerScope(callerRva,queue) {
  const address=typeof callerRva==='string'?callerRva.toLowerCase():null;
  if(address==='0x3e160a')return'CheckForUnitOrBuilding';
  if(queue)return'nested_QueueNextBuild';
  if(address==='0x3e849c')return'known_QueueNextBuild_callsite_without_parent';
  return'other_or_unknown_caller';
 }
 function enter(kind,args) {
  const diagnostic=diagnostics[kind];if(!diagnostic)throw Error('Unreviewed boundary');
  if(!started||frozen)return null;
  diagnostic.entries++;
  const reject=reason=>{diagnostic.rejected[reason]=(diagnostic.rejected[reason]||0)+1;return null;};
  if(!enabled){stats.budgetSuppressed++;return reject('saturated');}
  const errors={},who=identity(args.object,errors);
  if(!who||who.owner!==cfg.player||who.city!==cfg.city)return reject('owner_or_city');
  if(records.length+pending>=cfg.maxPairs){saturated=true;enabled=false;stats.budgetSuppressed++;return reject('pair_budget');}
  const parent=top(args.thread);
  const call={kind,args:Object.assign({},args),identity:who,callId:++stats.calls,entrySequence:++seq,
   queueCallId:parent?parent.callId:null,callerScope:callerScope(args.callerRva,parent),entry:{identity:who,readErrors:errors}};
  if(kind==='GetBestBuilding') {
   call.entry.targetSignal=signal(args.object,errors);
   call.entry.flags={r8ByteRaw:args.r8ByteRaw,r9ByteRaw:args.r9ByteRaw,semantics:'raw ABI bytes; not named policy flags'};
  } else {const stack=queues.get(args.thread)||[];stack.push(call);queues.set(args.thread,stack);}
  pending++;diagnostic.accepted++;
  if(records.length+pending===cfg.maxPairs){saturated=true;enabled=false;}
  return call;
 }
 function leave(call,signedReturn,rawReturn) {
  if(!call)return;
  if(call.kind==='QueueNextBuild') {
   const stack=queues.get(call.args.thread)||[];
   if(stack[stack.length-1]===call)stack.pop();else stats.errors++;
  }
  const errors={},out={sequence:++seq,readErrors:errors};
  if(frozen)out.inertReason='frozen_before_return';
  else {
   const who=identity(call.args.object,errors);out.identity=who;out.identityCorrelated=same(call.identity,who);
   if(!out.identityCorrelated){stats.identityChanges++;out.inertReason='identity_changed';}
   else if(call.kind==='GetBestBuilding') {
    // Fixed Granary values are observed even when another building (or -1) is
    // returned. The output pointer belongs to the winner, never to the Granary.
    out.targetSignal=signal(call.args.object,errors);
    out.selectedBuildingIndex=signedReturn;out.selectedValueQ8=null;
    if(signedReturn===-1)out.selectionStatus='no_building';
    else if(Number.isInteger(signedReturn)&&signedReturn>=0&&signedReturn<cfg.buildingIndexLimit) {
     out.selectionStatus='valid_index';out.selectedValueQ8=read(call.args.output,0,'i32',errors,'selectedValue');
    } else {out.selectionStatus='invalid_return_index';stats.errors++;}
   } else out.rawReturnUninterpreted=rawReturn;
  }
  records.push({kind:call.kind,callId:call.callId,entrySequence:call.entrySequence,thread:call.args.thread,
   callerRva:call.args.callerRva,callerScope:call.callerScope,queueCallId:call.queueCallId,entry:call.entry,leave:out});
  pending--;stats.completedPairs++;
 }
 return{stats,enter,leave,start(){if(started||frozen)throw Error('Observer cannot restart');started=true;enabled=true;return{enabled};},
  status(){return{enabled};},snapshot(){return{profile:cfg.profile,read_only:true,paired:true,enabled,saturated,records,stats,diagnostics,pendingPairs:pending,frozenPendingPairs:freezePendingAt};},
  freeze(){if(!frozen)freezePendingAt=pending;frozen=true;enabled=false;return this.snapshot();}};
}
function decodeBuildingDecisionArgs(kind,context,thread,callerRva) {
 return{object:context.rcx.toString(),output:kind==='GetBestBuilding'?context.rdx.toString():null,
  r8ByteRaw:kind==='GetBestBuilding'?(context.r8.toUInt32()&255):null,
  r9ByteRaw:kind==='GetBestBuilding'?(context.r9.toUInt32()&255):null,thread,callerRva};
}
function createMemoryIO(api) {
 return{read(address,offset,type) {
  if(!Number.isSafeInteger(offset)||offset<0||!['ptr','i32'].includes(type))return{value:null,error:'argument_missing'};
  if(address===null||address===undefined)return{value:null,error:'null_pointer'};
  try {
   const base=api.ptr(address),max=api.ptr('0x7fffffffffff');if(base.isNull())return{value:null,error:'null_pointer'};
   if(base.compare(api.ptr('0x10000'))<0||base.compare(max)>0)return{value:null,error:'noncanonical_pointer'};
   const point=base.add(offset),last=point.add((type==='ptr'?8:4)-1);
   if(point.compare(base)<0||last.compare(point)<0||last.compare(max)>0)return{value:null,error:'address_overflow'};
   const range=api.findRangeByAddress(point);
   if(!range||!range.protection.includes('r')||last.compare(range.base.add(range.size))>=0)return{value:null,error:'unreadable_span'};
   return{value:type==='ptr'?point.readPointer().toString():point.readS32()};
  } catch(_){return{value:null,error:'read_exception'};}
 }};
}
if(typeof module!=='undefined'&&module.exports)module.exports={makeBuildingDecisionObserver,decodeBuildingDecisionArgs,createMemoryIO,validateBuildingConfig};
else {
 const spec=__SPEC__,cfg=__CONFIG__;validateBuildingConfig(cfg);
 const nativeModule=Process.getModuleByName('GameCore_XP2_FinalRelease.dll');
 if(nativeModule.path.toLowerCase()!==spec.path.toLowerCase()||nativeModule.size!==spec.image_size)throw Error('Loaded module path/size mismatch');
 if(Process.enumerateModules().some(m=>/GameCore_XP2_CE/i.test(m.name)))throw Error('CE proxy loaded');
 const pe=nativeModule.base.add(nativeModule.base.add(0x3c).readU32());
 if(pe.add(8).readU32()!==spec.timestamp)throw Error('Loaded module timestamp mismatch');
 const expected={GetBestBuilding:0x3e4710,QueueNextBuild:0x3e8190};
 if(spec.functions.length!==2||new Set(spec.functions.map(f=>f.name)).size!==2)throw Error('Wrong reviewed hook set');
 for(const f of spec.functions) {
  if(expected[f.name]!==f.rva)throw Error('Unreviewed RVA');
  const bytes=Array.from(new Uint8Array(nativeModule.base.add(f.rva).readByteArray(32))).map(x=>x.toString(16).padStart(2,'0')).join('');
  if(bytes!==f.bytes)throw Error('Entry fingerprint mismatch');
 }
 const io=createMemoryIO({ptr,findRangeByAddress:p=>Process.findRangeByAddress(p)}),observer=makeBuildingDecisionObserver(io,cfg),hooks=[];
 for(const f of spec.functions)hooks.push(Interceptor.attach(nativeModule.base.add(f.rva),{
  onEnter(){this.observation=null;try {
   const ret=this.returnAddress,caller=ret.compare(nativeModule.base)>=0&&ret.compare(nativeModule.base.add(nativeModule.size))<0?ret.sub(nativeModule.base).toString():null;
   this.observation=observer.enter(f.name,decodeBuildingDecisionArgs(f.name,this.context,this.threadId,caller));
  }catch(_){observer.stats.errors++;}},
  onLeave(ret){try{observer.leave(this.observation,ret.toInt32(),ret.toString());}catch(_){observer.stats.errors++;}}
 }));
 rpc.exports={status(){return{installed:true,hooks:hooks.length,enabled:observer.status().enabled,module_path:nativeModule.path,module_size:nativeModule.size,
  loaded_timestamp:pe.add(8).readU32(),validated_entry_fingerprints:spec.functions,config:cfg,read_only:true};},
  start(){return observer.start();},snapshot(){return observer.snapshot();},freeze(){return observer.freeze();}};
}
