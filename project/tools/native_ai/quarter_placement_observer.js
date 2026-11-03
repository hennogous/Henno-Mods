'use strict';
// Reviewed current-DLL boundaries only. Passive reads: never call engine methods.
const POINTS={district_value:0x52d500,net_value:0x52a440,normalize:0x52b110,normalize_bonus:0x52b1bb,
 competitor_compare:0x52ddbb,competitor_merge:0x52ddd3,city_evaluation:0x3e2aa0,get_best_district:0x3e4a50,try_reserve:0x3ea040};
const GROUPS={'0x52d91d':'wrapper','0x52d9cc':'own_static','0x52dceb':'competing_static'};
function configValid(c){
 if(c.profile!=='quarter-placement-v1'||c.player!==3||c.city!==131073||c.districtType!=='DISTRICT_CSC_BAKERS_QUARTER'||c.mappingVerified!==true)throw Error('Unreviewed target');
 if(!Number.isInteger(c.districtIndex)||c.districtIndex<0||!Number.isInteger(c.districtIndexLimit)||c.districtIndex>=c.districtIndexLimit||c.districtIndexLimit>4096)throw Error('Native district map missing');
 if(!Number.isInteger(c.privateYieldIndex)||c.privateYieldIndex<0||!Number.isInteger(c.yieldIndexLimit)||c.privateYieldIndex>=c.yieldIndexLimit||c.yieldIndexLimit>64)throw Error('Native yield map missing');
 if(c.mapWidth!==74||c.mapHeight!==46||c.maxPairs!==64||c.maxChoices!==32||c.maxRows!==64||c.maxScopeDepth!==16||c.maxThreads!==8||c.maxNormalizations!==512||c.maxValuesPerNet!==4||c.maxCallbacks!==1000000||c.maxTrackedMs!==300000)throw Error('Unsafe collection bounds');
}
function makePlacementObserver(io,cfg,clock){
 configValid(cfg);clock=clock||(()=>Date.now());
 let started=false,enabled=false,frozen=false,saturated=false,next=0,firstTracked=null,freezePending=null;
 const stacks=new Map(),candidates=new Map(),evaluations=new Map(),choices=[],reservations=[];
 const stats={callbacks:0,completedPairs:0,completedCandidatesTotal:0,errors:0,identityChanges:0,revisionsNotRetained:0,dropped:0,elapsedTrackedMs:0};
 const counters={};let stopReason=null;
 function stop(reason){enabled=false;saturated=true;stopReason=stopReason||reason;}
 function tick(kind){stats.callbacks++;counters[kind]=(counters[kind]||0)+1;if(stats.callbacks>cfg.maxCallbacks)stop('callback_budget');if(firstTracked!==null){stats.elapsedTrackedMs=clock()-firstTracked;if(stats.elapsedTrackedMs>cfg.maxTrackedMs)stop('tracked_time_budget');}}
 function error(reason){stats.errors++;stop(reason);return null;}
 function rd(p,o,t){const r=io.read(p,o,t);return r.error?error('read:'+r.error):r.value;}
 function stack(t){return stacks.get(t)||[];}
 function top(t,k){const a=stack(t);for(let i=a.length-1;i>=0;i--)if(a[i].kind===k)return a[i];return null;}
 function push(kind,a,tracked,extra){const s=stack(a.thread);if(!stacks.has(a.thread)&&stacks.size>=cfg.maxThreads){error('thread_map_bound');return null;}if(s.length>=cfg.maxScopeDepth){error('TLS_depth');return null;}const f=Object.assign({kind,id:++next,args:a,tracked,enteredMs:clock()},extra||{});s.push(f);stacks.set(a.thread,s);return f;}
 function who(p){const owner=rd(p,0xd8,'i32'),city=rd(p,0xa8,'i32');return{pointer:p,player:owner,city};}
 function focus(w){return w&&w.player===cfg.player&&w.city===cfg.city;}
 function xy(p,offset,type){return{x:rd(p,offset,type),y:rd(p,offset+(type==='i16'?2:4),type)};}
 function validXY(v){return v&&Number.isInteger(v.x)&&Number.isInteger(v.y)&&v.x>=0&&v.x<cfg.mapWidth&&v.y>=0&&v.y<cfg.mapHeight;}
 function sameXY(a,b){return a&&b&&a.x===b.x&&a.y===b.y;}
 function row(p){
  const eligible=rd(p,0x55,'u8'),owned=rd(p,0x5a,'u8'),adjacent=rd(p,0x57,'u8');
  const meta={pointer:p,eligibleRaw:eligible,ownedRaw:owned,adjacentOwnedRaw:adjacent};
  if(!eligible||(!owned&&!adjacent))return Object.assign(meta,{status:'native_GetBest_ineligible_unobserved',xy:null,scores:null,targetCacheQ8:null});
  const pos=xy(p,8,'i32');if(!validXY(pos)){error('eligible_row_XY');return Object.assign(meta,{status:'invalid_eligible_XY',xy:pos});}
  const scores=rd(p,0x20,'ptr');return Object.assign(meta,{status:'eligible_scored',xy:pos,scores,targetCacheQ8:rd(scores,cfg.districtIndex*4,'i32')});
 }
 function pointerSlot(pointer,base){const offset=io.offset(pointer,base);if(!Number.isInteger(offset)||offset<0||offset%4||offset>=cfg.districtIndexLimit*4){error('vector_slot_bound');return null;}return offset/4;}
 function enter(kind,a){
  tick(kind+':enter');if(!started||!enabled||frozen)return null;
  if(kind==='city_evaluation'){
   const input=xy(a.row,0x64,'i32');
   // Exact native early return precedes handle/output/cache access.
   if(input.x< -0x270e||input.y< -0x270e){counters.native_sentinel_unobserved=(counters.native_sentinel_unobserved||0)+1;return null;}
   const owner=rd(a.row,0x70,'i16'),city=rd(a.row,0x74,'i32');const tracked=owner===cfg.player&&city===cfg.city;
   if(!tracked&&!stack(a.thread).length)return null;
   const pos=tracked?input:null;if(tracked&&!validXY(pos)){error('row_XY');return null;}
   return push(kind,a,tracked,{identity:{player:owner,city},xy:pos});
  }
  if(kind==='net_value'||kind==='district_value'){
   const e=top(a.thread,'city_evaluation');if(!e)return null;
   let tracked=e.tracked&&a.districtIndex===cfg.districtIndex;
   if(!tracked)return push(kind,a,false);
   const w=who(a.city),pos=xy(a.plot,0x28,'i16');
   if(!focus(w)||!sameXY(pos,e.xy)){stats.identityChanges++;stop('native_city_or_plot_identity');return push(kind,a,false);}
   if(firstTracked===null)firstTracked=clock();
   return push(kind,a,true,{identity:w,xy:pos,row:e.args.row,evaluationCallId:e.id,discountQ8:rd(a.discount,0,'i32'),normalizations:[],compare:null,merge:null,districtValues:[]});
  }
  if(kind==='normalize'){
   const v=top(a.thread,'district_value');if(!v||!v.tracked)return null;
   if(!GROUPS[a.callerRva])return push(kind,a,false);
   if(!Number.isInteger(a.yieldIndex)||a.yieldIndex<0||a.yieldIndex>=cfg.yieldIndexLimit){error('yield_index');return null;}
   return push(kind,a,true,{parent:v.id,group:GROUPS[a.callerRva],yieldIndex:a.yieldIndex,rawInputQ8:rd(a.input,0,'i32'),bonusQ8:null});
  }
  if(kind==='get_best_district'||kind==='try_reserve'){
   const cityPtr=rd(a.object,0x90,'ptr'),w=who(cityPtr);if(!focus(w))return null;
   const count=rd(a.object,0x4d8,'u32'),base=rd(a.object,0x4c8,'ptr');
   if(!Number.isInteger(count)||count<0||count>cfg.maxRows){error('row_count_bound');return null;}
   const rows=[];for(let i=0;i<count;i++){const p=io.add(base,i*0x78),r=row(p);rows.push(r);}
   return push(kind,a,true,{identity:w,rows,xy:kind==='try_reserve'?xy(a.output,0,'i32'):null,scoreInputQ8:kind==='try_reserve'?rd(a.score,0,'i32'):null});
  }
  throw Error('Unreviewed entrypoint');
 }
 function point(kind,a){
  tick(kind);if(!started||!enabled||frozen)return;
  if(kind==='normalize_bonus'){
   const n=top(a.thread,'normalize');if(n&&n.tracked)n.bonusQ8=rd(a.rax,0,'i32');return;
  }
  const v=top(a.thread,'district_value');if(!v||!v.tracked)return;
  if(kind==='competitor_compare'){
   const own=pointerSlot(a.rax,a.r12),best=pointerSlot(a.rcx,a.r12);if(own===null||best===null)return;
   const selected=rd(a.rax,0,'i32'),bestValue=rd(a.rcx,0,'i32');if(own!==cfg.districtIndex||bestValue!==a.edx){error('competitor_vector_identity');return;}
   v.compare={selectedIndex:own,selectedStaticQ8:selected,bestIndex:best,bestStaticQ8:bestValue,bestRegisterQ8:a.edx,preTotalQ8:a.esi};
  }else if(kind==='competitor_merge'){
   if(!v.compare){error('missing_competitor_compare');return;}
   const deduction=v.compare.preTotalQ8-a.esi;
   v.merge={postTotalQ8:a.esi,actualDeductionQ8:deduction};
   if(deduction!==0&&deduction!==v.compare.bestStaticQ8)error('uninterpretable_competitor_deduction');
  }else throw Error('Unreviewed midpoint');
 }
 function leave(f,result){
  tick(f?f.kind+':leave':'untracked:leave');if(!f)return;
  const s=stack(f.args.thread);if(s[s.length-1]!==f){error('TLS_pairing');return;}s.pop();if(!s.length)stacks.delete(f.args.thread);f.endSequence=++next;if(!f.tracked||frozen)return;
  if(f.kind==='normalize'){
   if(result.pointer!==f.args.output){error('normalize_return_pointer');return;}
   const v=top(f.args.thread,'district_value');if(!v||v.id!==f.parent){error('normalize_parent');return;}
   if(v.normalizations.length>=cfg.maxNormalizations){stats.dropped++;stop('normalization_frame_bound');return;}
   v.normalizations.push({group:f.group,yieldIndex:f.yieldIndex,rawInputQ8:f.rawInputQ8,mutableInputExitQ8:rd(f.args.input,0,'i32'),normalizedQ8:rd(f.args.output,0,'i32'),effectiveBonusQ8:f.bonusQ8,cappedBonusQ8:f.bonusQ8===null?null:Math.min(f.bonusQ8,2304),factorNumerator:f.bonusQ8===null?null:256+Math.min(f.bonusQ8,2304),factorDenominator:256});return;
  }
  if(f.kind==='district_value'||f.kind==='net_value'){
   if(result.pointer!==f.args.output){error('score_return_pointer');return;}
   const w=who(f.args.city);if(!focus(w)||w.pointer!==f.identity.pointer){stats.identityChanges++;stop('city_identity_changed');return;}
   const value={callId:f.id,endSequence:f.endSequence,enteredMs:f.enteredMs,kind:f.kind,row:f.row,evaluationCallId:f.evaluationCallId,identity:f.identity,xy:f.xy,districtIndex:f.args.districtIndex,callerRva:f.args.callerRva,discountQ8:f.discountQ8,readyTurn:f.args.readyTurn,horizon:f.args.horizon,resultQ8:rd(f.args.output,0,'i32'),normalizations:f.normalizations,compare:f.compare,merge:f.merge,districtValues:f.districtValues};
   if(f.kind==='district_value'){const n=top(f.args.thread,'net_value');if(n&&n.tracked){if(n.districtValues.length>=cfg.maxValuesPerNet){stats.dropped++;stop('district_values_frame_bound');}else n.districtValues.push(value);}return;}
   if(!candidates.has(f.row)&&candidates.size>=cfg.maxPairs){stats.dropped++;stop('candidate_cache_budget');return;}
   if(candidates.has(f.row))stats.revisionsNotRetained++;candidates.set(f.row,value);stats.completedCandidatesTotal++;stats.completedPairs=candidates.size;return;
  }
  if(f.kind==='city_evaluation'){
   if(rd(f.args.row,0x59,'u8')===0){
    if(!evaluations.has(f.args.row)&&evaluations.size>=cfg.maxPairs){stats.dropped++;stop('evaluation_cache_budget');return;}
    evaluations.set(f.args.row,{callId:f.id,endSequence:f.endSequence,identity:f.identity,status:'native_invisible_unobserved',row:{pointer:f.args.row,xy:null,targetCacheQ8:null}});return;
   }
   const r=row(f.args.row);if(r.status==='eligible_scored'&&!sameXY(r.xy,f.xy)){stats.identityChanges++;stop('row_output_XY_changed');return;}
   if(!evaluations.has(f.args.row)&&evaluations.size>=cfg.maxPairs){stats.dropped++;stop('evaluation_cache_budget');return;}
   evaluations.set(f.args.row,{callId:f.id,endSequence:f.endSequence,identity:f.identity,row:r});return;
  }
  if(f.kind==='get_best_district'){
   if(choices.length>=cfg.maxChoices){stats.dropped++;stop('choice_budget');return;}
   const chosen=result.signed;let pos=null,selected=null;
   if(chosen>=0){if(chosen>=cfg.districtIndexLimit){error('choice_district_index');return;}pos=xy(f.args.output,0,'i32');if(!validXY(pos)){error('choice_XY');return;}selected=f.rows.find(r=>sameXY(r.xy,pos))||null;}
   const dossier=f.rows.map(r=>{
    const e=evaluations.get(r.pointer)||null,c=candidates.get(r.pointer)||null;
    const fresh=!!(r.status==='eligible_scored'&&e&&e.status!=='native_invisible_unobserved'&&c&&c.evaluationCallId===e.callId&&c.endSequence<e.endSequence&&e.endSequence<f.id&&focus(c.identity)&&c.identity.pointer===f.identity.pointer&&e.identity.player===cfg.player&&e.identity.city===cfg.city&&sameXY(c.xy,r.xy)&&sameXY(e.row.xy,r.xy)&&e.row.targetCacheQ8===r.targetCacheQ8);
    return{cache:r,evaluation:e,candidate:c,provenance:fresh?'fresh_matched_eval_net_cache':'missing_or_stale_no_score_proof'};
   });
   choices.push({callId:f.id,enteredMs:f.enteredMs,endSequence:f.endSequence,identity:f.identity,cityBuild:f.args.object,callerRva:f.args.callerRva,districtIndex:chosen,xy:pos,selectedRow:selected,dossier:JSON.parse(JSON.stringify(dossier)),choiceIsReservation:false,nativeTurn:'UNOBSERVED at hook; driver attaches finitewindow'});return;
  }
  if(f.kind==='try_reserve'){
   if(reservations.length>=cfg.maxChoices){stats.dropped++;stop('reservation_budget');return;}
   const localIndex=result.signed;if(localIndex< -1||localIndex>=cfg.mapWidth*cfg.mapHeight){error('reservation_return');return;}
   const cached=f.rows.find(r=>sameXY(r.xy,f.xy));let receipt=null;
   if(localIndex>=0&&cached){const pointer=rd(cached.pointer,0x48,'ptr');receipt={controller:rd(pointer,0,'i32'),scoreQ8:rd(pointer,4,'i32'),purpose:rd(pointer,8,'i32')};}
   const matches=receipt&&receipt.controller===f.args.controller&&receipt.scoreQ8===f.scoreInputQ8&&receipt.purpose===f.args.purpose;
   const links=choices.filter(c=>c.districtIndex===cfg.districtIndex&&c.endSequence<f.id&&c.cityBuild===f.args.object&&c.identity.pointer===f.identity.pointer&&sameXY(c.xy,f.xy)&&cached&&c.selectedRow&&c.selectedRow.pointer===cached.pointer&&c.selectedRow.scores===cached.scores&&c.selectedRow.targetCacheQ8===cached.targetCacheQ8&&cached.targetCacheQ8===f.scoreInputQ8&&c.dossier.some(d=>d.cache.pointer===cached.pointer&&d.provenance==='fresh_matched_eval_net_cache'&&evaluations.get(cached.pointer)&&d.evaluation.callId===evaluations.get(cached.pointer).callId));
   reservations.push({callId:f.id,enteredMs:f.enteredMs,endSequence:f.endSequence,identity:f.identity,callerRva:f.args.callerRva,xy:f.xy,cityLocalPlotIndex:localIndex,controller:f.args.controller,purpose:f.args.purpose,scoreInputQ8:f.scoreInputQ8,storedReservation:receipt,storedReceiptMatches:!!matches,linkedChoiceCallId:links.length===1?links[0].callId:null,linkCount:links.length,districtArgumentPresent:false,linkQualification:links.length===1?'unique same-cache-generation/city/XY/score; driver must confirm same finiteclockwindow+knowncallers; NOT district argument':'missing_or_ambiguous_no_Quarter_reservation_claim'});
  }
 }
 function pending(){let n=0;for(const s of stacks.values())n+=s.filter(f=>f.tracked).length;return n;}
 function snapshot(){return{profile:cfg.profile,read_only:true,paired:true,enabled,saturated,stopReason,stats:Object.assign({},stats),counters,pendingPairs:pending(),frozenPendingPairs:freezePending,candidates:[...candidates.values()],evaluations:[...evaluations.values()],choices,reservations,coverage:'latest complete per-row candidate/evaluation cache, immutable choice-time dossiers; older revisions not retained; no global ranking or reservation absence claim'};}
 return{enter,point,leave,stats,fatal:reason=>error(reason),wants(kind,thread){if(!started||!enabled||frozen)return false;if(kind==='normalize'){const v=top(thread,'district_value');return !!(v&&v.tracked);}if(kind==='net_value'||kind==='district_value')return !!top(thread,'city_evaluation');return true;},ignored(kind){tick(kind+':untracked');},start(){if(started||frozen||saturated||stats.errors||stats.identityChanges)throw Error('No restart or reenable after failure');started=true;enabled=true;return{enabled};},snapshot,status(){return{enabled};},freeze(){freezePending=pending();frozen=true;enabled=false;return snapshot();}};
}
function memoryIO(api){
 return{add:(p,n)=>api.ptr(p).add(n).toString(),offset:(p,b)=>{try{const a=api.ptr(p),base=api.ptr(b);if(a.compare(base)<0)return null;const wide=BigInt(a.sub(base).toString());return wide>BigInt(Number.MAX_SAFE_INTEGER)?null:Number(wide);}catch(_){return null;}},read(p,o,t){
  const sizes={ptr:8,i32:4,u32:4,i16:2,u8:1};if(!Number.isSafeInteger(o)||o<0||!sizes[t])return{error:'invalid_read_arguments'};
  try{const base=api.ptr(p),limit=api.ptr('0x7fffffffffff');if(base.isNull()||base.compare(api.ptr('0x10000'))<0||base.compare(limit)>0)return{error:'invalid_pointer'};
   const at=base.add(o),end=at.add(sizes[t]-1),range=api.find(at);if(at.compare(base)<0||end.compare(at)<0||end.compare(limit)>0||!range||!range.protection.includes('r')||end.compare(range.base.add(range.size))>=0)return{error:'unreadable_span'};
   const value=t==='ptr'?at.readPointer().toString():t==='i32'?at.readS32():t==='u32'?at.readU32():t==='i16'?at.readS16():at.readU8();return{value};
  }catch(_){return{error:'read_exception'};}
 }};
}
if(typeof module!=='undefined'&&module.exports)module.exports={POINTS,GROUPS,configValid,makePlacementObserver,memoryIO};
else{
 const spec=__SPEC__,cfg=__CONFIG__;configValid(cfg);const native=Process.getModuleByName('GameCore_XP2_FinalRelease.dll');
 if(native.path.toLowerCase()!==spec.path.toLowerCase()||native.size!==spec.image_size||Process.enumerateModules().some(m=>/GameCore_XP2_CE/i.test(m.name)))throw Error('Wrong native module');
 const pe=native.base.add(native.base.add(0x3c).readU32());if(pe.add(8).readU32()!==spec.timestamp)throw Error('PE timestamp');
 if(spec.functions.length!==9||new Set(spec.functions.map(f=>f.name)).size!==9)throw Error('Hook set');
 for(const f of spec.functions){if(POINTS[f.name]!==f.rva)throw Error('Unreviewed RVA');const bytes=Array.from(new Uint8Array(native.base.add(f.rva).readByteArray(32))).map(x=>x.toString(16).padStart(2,'0')).join('');if(bytes!==f.bytes)throw Error('Fingerprint');}
 const io=memoryIO({ptr,find:p=>Process.findRangeByAddress(p)}),observer=makePlacementObserver(io,cfg),hooks=[];
 function read(p,o,t){const r=io.read(p,o,t);if(r.error)throw Error(r.error);return r.value;}
 function decode(name,c,thread,ret){
  const a={thread,callerRva:ret?ret.sub(native.base).toString():null};
  if(name==='city_evaluation')a.row=c.rcx.toString();
  if(name==='net_value'||name==='district_value'){Object.assign(a,{output:c.rcx.toString(),districtIndex:c.rdx.toInt32(),discount:c.r8.toString(),readyTurn:c.r9.toInt32(),horizon:read(c.rsp.toString(),0x28,'i32'),plot:read(c.rsp.toString(),0x30,'ptr'),city:read(c.rsp.toString(),0x38,'ptr')});if(name==='district_value')a.mapChanges=read(c.rsp.toString(),0x40,'ptr');}
  if(name==='normalize')Object.assign(a,{output:c.rcx.toString(),input:c.rdx.toString(),yieldIndex:c.r8.toInt32(),playerPointer:c.r9.toString()});
  if(name==='get_best_district'||name==='try_reserve')Object.assign(a,{object:c.rcx.toString(),output:c.rdx.toString()});
  if(name==='try_reserve')Object.assign(a,{controller:c.r8.toInt32(),score:c.r9.toString(),purpose:read(c.rsp.toString(),0x28,'i32')});return a;
 }
 for(const f of spec.functions){
  const midpoint=['normalize_bonus','competitor_compare','competitor_merge'].includes(f.name);
  const listener={onEnter(){this.frame=null;try{if(midpoint){observer.point(f.name,{thread:this.threadId,rax:this.context.rax.toString(),rcx:this.context.rcx.toString(),r12:this.context.r12.toString(),edx:this.context.rdx.toInt32(),esi:this.context.rsi.toInt32()});}else{
   const caller=this.returnAddress.sub(native.base).toString();
   if(!observer.wants(f.name,this.threadId)||(f.name==='normalize'&&!GROUPS[caller])){observer.ignored(f.name);return;}
   this.frame=observer.enter(f.name,decode(f.name,this.context,this.threadId,this.returnAddress));
  }}catch(_){observer.fatal('callback_decode_exception');}}};
  if(!midpoint)listener.onLeave=function(ret){try{observer.leave(this.frame,{pointer:ret.toString(),signed:ret.toInt32()});}catch(_){observer.fatal('callback_leave_exception');}};
  hooks.push(Interceptor.attach(native.base.add(f.rva),listener));
 }
 rpc.exports={start(){return observer.start();},snapshot(){return observer.snapshot();},freeze(){return observer.freeze();},status(){return{installed:true,hooks:hooks.length,enabled:observer.status().enabled,module_path:native.path,module_size:native.size,loaded_timestamp:pe.add(8).readU32(),validated_entry_fingerprints:spec.functions,config:cfg,read_only:true};}};
}
