'use strict';
// Two reviewed consumers only. Native data reads; no calls, writes or return replacement.
function makeWorkObserver(io,cfg){
 let enabled=false,started=false,frozen=false,saturated=false,seq=0,pending=0,freezePendingAt=null;
 const records=[];
 const stats={calls:0,completedPairs:0,errors:0,identityChanges:0,budgetSuppressed:0};
 const diagnostics={CheckForImprovement:{entries:0,accepted:0,rejected:{}},DecodeTrigger:{entries:0,accepted:0,rejected:{}}};
 const names=new Map((cfg.improvementCatalog||[]).map(r=>[r.index,r.type]));
 const nil=p=>p===null||p===undefined||p==='0x0';
 function read(p,o,t,e,k){const r=io.read(p,o,t);if(r.error){stats.errors++;e[k]=r.error;return null;}return r.value;}
 function city(p,e){if(nil(p))return null;return{pointer:p,owner:read(p,0xd8,'i32',e,'owner'),id:read(p,0xa8,'i32',e,'city')};}
 function same(a,b){return a&&b&&a.pointer===b.pointer&&a.owner===b.owner&&a.id===b.id;}
 function handle(node,offset,indexOffset,stride,e,label){
  if(nil(node))return{status:'unknown_node_null'};
  const manager=read(node,offset,'ptr',e,label+'Manager'),index=read(node,indexOffset,'u32',e,label+'Index');
  const out={manager,index,status:'unknown_unbound'};
  if(nil(manager)||index===null||index===0xffffffff)return out;
  const data=read(manager,0,'ptr',e,label+'Data'),count=read(manager,0x10,'u32',e,label+'Count');Object.assign(out,{data,count});
  if(count===null||count>65536){out.status='unknown_manager_count';return out;}
  if(index>=count){out.status='unknown_index_out_of_range';return out;}
  if(nil(data)){out.status='unknown_data_null';return out;}
  out.status='bound';out.address=io.add(data,index*stride);return out;
 }
 function outputs(node,e){
  const priority=handle(node,0x80,0x8c,8,e,'priority');
  priority.valueRaw=priority.status==='bound'?read(priority.address,0,'i32',e,'priorityValue'):null;
  priority.semantic='bound output raw only; unbound native stack fallback unknown';
  const location=handle(node,0x50,0x5c,0x0c,e,'location');
  if(location.status==='bound'){location.x=read(location.address,0,'i32',e,'locationX');location.y=read(location.address,4,'i32',e,'locationY');}
  const improvements=handle(node,0x20,0x2c,0x20,e,'improvements');
  if(improvements.status==='bound'){
   const p=improvements.address;improvements.vector={data:read(p,0,'ptr',e,'vectorData'),capacity:read(p,8,'u32',e,'vectorCapacity'),count:read(p,0x10,'u32',e,'vectorCount'),entries:[]};
   const v=improvements.vector;
   if(v.count===null||v.capacity===null||v.count>v.capacity||v.count>8||v.capacity>65536)v.status='unknown_vector_bounds';
   else if(v.count>0&&nil(v.data))v.status='unknown_vector_data_null';
   else{v.status='observed';for(let i=0;i<v.count;i++)v.entries.push({index:read(v.data,i*0x0c,'i32',e,'improvementIndex'+i),raw_word4:read(v.data,i*0x0c+4,'i32',e,'improvementWord4_'+i),raw_word8:read(v.data,i*0x0c+8,'i32',e,'improvementWord8_'+i)});}
  }
  return{priority,location,improvements};
 }
 function parentRoot(tree,e){
  const chain=[],seen=new Set();let p=tree;
  for(let i=0;i<8;i++){
   if(nil(p))return{status:'unknown_null',chain,rootID:null,controlID:null};
   if(seen.has(p))return{status:'unknown_cycle',chain,rootID:null,controlID:null};
   seen.add(p);chain.push(p);const parent=read(p,0x120,'ptr',e,'parent'+i);
   if(parent===null)return{status:'unknown_read',chain,rootID:null,controlID:null};
   if(nil(parent))return{status:'observed',chain,rootPointer:p,rootID:read(p,0x1c8,'i32',e,'rootID'),controlID:read(p,0x1b0,'i32',e,'rootControlID')};
   p=parent;
  }
  return{status:'unknown_chain_limit',chain,rootID:null,controlID:null};
 }
 function indexStatus(index){return index===null?'unknown_read':index===-1?'sentinel':names.has(index)?'catalogued':'unknown_index';}
 function originalPlot(plot,e){
  if(nil(plot))return{status:'unknown_plot_null'};
  const x=read(plot,0x28,'i16',e,'plotX'),y=read(plot,0x2a,'i16',e,'plotY');
  const valid=x!==null&&y!==null&&x>=0&&y>=0&&(!Number.isInteger(cfg.mapWidth)||x<cfg.mapWidth)&&(!Number.isInteger(cfg.mapHeight)||y<cfg.mapHeight);
  return{status:x===null||y===null?'unknown_read':valid?'observed':'invalid_coordinates',x,y};
 }
 function state(kind,a,e){
  if(kind==='CheckForImprovement'){
   // Reread the backing slot pointer on EACH phase: native edit may replace it.
   const slotPointer=read(a.object,0x430,'ptr',e,'slotPointer'),nameObject=read(a.object,0x408,'ptr',e,'nameObject');
   const namePointer=nil(nameObject)?null:read(nameObject,0x18,'ptr',e,'namePointer');
   const index=read(a.object,0x250,'i32',e,'bestImprovementIndex');
   return{bestImprovementIndex:index,bestImprovementType:names.get(index)||null,bestImprovementIndexStatus:indexStatus(index),slotPointer,
    slotRaw:nil(slotPointer)?null:read(slotPointer,0x0c,'i32',e,'slotRaw'),configuredNamePointer:namePointer,
    configuredNameFirstByte:nil(namePointer)?null:read(namePointer,0,'u8',e,'nameFirstByte'),requestedControlPriorityRaw:read(a.object,0x198,'i32',e,'requestedPriority')};
  }
  // Fresh handles, manager/data pointers and vector headers on every phase.
  const index=read(a.tree,0x2b8,'i32',e,'triggerImprovementIndex'),plot=read(a.tree,0x308,'ptr',e,'originalPlotPointer');
  return{tree:a.tree,root:parentRoot(a.tree,e),triggerImprovementIndex:index,triggerImprovementType:names.get(index)||null,triggerImprovementIndexStatus:indexStatus(index),
   triggerMarkerRaw:read(a.tree,0x330,'u8',e,'triggerMarker'),originalPlotPointer:plot,
   originalPlot:originalPlot(plot,e),
   initialValueRaw:read(a.tree,0x340,'i32',e,'initialValue'),configuredPriorityRaw:read(a.tree,0x288,'i32',e,'configuredPriority'),outputs:outputs(a.node,e)};
 }
 function enter(kind,a){
  const d=diagnostics[kind];if(!d)throw Error('Unknown observer boundary');
  if(!started||frozen)return null;d.entries++;
  const reject=why=>{d.rejected[why]=(d.rejected[why]||0)+1;return null;};
  if(!enabled){stats.budgetSuppressed++;return reject('saturated');}
  const errors={};let cp;
  if(kind==='CheckForImprovement')cp=read(a.object,0x90,'ptr',errors,'cityPointer');
  else{
   a.tree=read(a.stack,0x28,'ptr',errors,'fifthArgumentTree'); // R9 is AI instance, NOT this fifth argument.
   if(nil(a.tree))return reject('tree_null');
   cp=read(a.tree,0x2f0,'ptr',errors,'treeCityPointer');
  }
  if(nil(cp))return reject(kind==='DecodeTrigger'?'global_or_city_null':'city_null');
  const identity=city(cp,errors);
  if(!identity||identity.owner!==cfg.player||identity.id!==cfg.city)return reject('owner_or_city');
  d.matchedCity=(d.matchedCity||0)+1;
  if(kind==='DecodeTrigger'){
   const index=read(a.tree,0x2b8,'i32',errors,'scopeImprovementIndex'),marker=read(a.tree,0x330,'u8',errors,'scopeImprovementMarker');
   if(index===null||marker===null)return reject('payload_read_error');
   if(index< -1||(index>=0&&!names.has(index))){
    stats.errors++;d.invalidPayloadExamples=d.invalidPayloadExamples||[];
    if(d.invalidPayloadExamples.length<4)d.invalidPayloadExamples.push({indexRaw:index,markerRaw:marker,status:'unknown_invalid_improvement_index'});
    return reject('invalid_improvement_index');
   }
   if(index===-1&&marker===0)return reject('non_improvement_payload');
  }
  if(records.length+pending>=cfg.maxPairs){saturated=true;enabled=false;stats.budgetSuppressed++;return reject('pair_budget');}
  const call={kind,args:Object.assign({},a),identity,entrySequence:++seq,callId:++stats.calls,entry:{identity,raw:state(kind,a,errors),readErrors:errors}};
  pending++;d.accepted++;
  if(records.length+pending===cfg.maxPairs){saturated=true;enabled=false;}
  return call;
 }
 function leave(call,rawReturn,signedReturn){
  if(!call)return;
  const errors={};let leave={sequence:++seq,rawReturnUninterpreted:rawReturn};
  if(call.kind==='DecodeTrigger')leave.rawReturnS32=signedReturn; // No enum/status label inferred.
  if(frozen)leave.inertReason='frozen_before_return';
  else{
   const a=call.args,cp=read(call.kind==='CheckForImprovement'?a.object:a.tree,call.kind==='CheckForImprovement'?0x90:0x2f0,'ptr',errors,'cityPointer');
   const identity=city(cp,errors);leave.identity=identity;leave.identityCorrelated=same(call.identity,identity);
   if(!leave.identityCorrelated){stats.identityChanges++;leave.inertReason='identity_changed';}
   else leave.raw=state(call.kind,a,errors);
  }
  leave.readErrors=errors;records.push({kind:call.kind,callId:call.callId,entrySequence:call.entrySequence,thread:call.args.thread,callerRva:call.args.callerRva,entry:call.entry,leave});pending--;stats.completedPairs++;
 }
 return{stats,enter,leave,start(){if(started)throw Error('Observer cannot restart');started=true;enabled=true;return{enabled};},
 status(){return{enabled};},snapshot(){return{read_only:true,paired:true,enabled,saturated,records,stats,diagnostics,pendingPairs:pending,frozenPendingPairs:freezePendingAt};},
 freeze(){if(!frozen)freezePendingAt=pending;frozen=true;enabled=false;return this.snapshot();}};
}
function createMemoryIO(api){return{
 add:(p,n)=>api.ptr(p).add(n).toString(),
 read(address,offset,type){
  const sizes={ptr:8,u8:1,i16:2,i32:4,u32:4};if(!Number.isSafeInteger(offset)||offset<0||!sizes[type])return{value:null,error:'argument_missing'};
  try{
   const base=api.ptr(address),max=api.ptr('0x7fffffffffff');if(base.isNull())return{value:null,error:'null_pointer'};
   if(base.compare(api.ptr('0x10000'))<0||base.compare(max)>0)return{value:null,error:'noncanonical_pointer'};
   const p=base.add(offset),last=p.add(sizes[type]-1);if(p.compare(base)<0||last.compare(p)<0||last.compare(max)>0)return{value:null,error:'address_overflow'};
   const range=api.findRangeByAddress(p);if(!range||!range.protection.includes('r')||last.compare(range.base.add(range.size))>=0)return{value:null,error:'unreadable_span'};
   return{value:type==='ptr'?p.readPointer().toString():type==='u8'?p.readU8():type==='i16'?p.readS16():type==='u32'?p.readU32():p.readS32()};
  }catch(_){return{value:null,error:'read_exception'};}
 }
};}
if(typeof module!=='undefined'&&module.exports)module.exports={makeWorkObserver,createMemoryIO};
else{
 const spec=__SPEC__,cfg=__CONFIG__,m=Process.getModuleByName('GameCore_XP2_FinalRelease.dll');
 if(m.path.toLowerCase()!==spec.path.toLowerCase()||m.size!==spec.image_size)throw Error('Loaded module path/size mismatch');
 if(Process.enumerateModules().some(x=>/GameCore_XP2_CE/i.test(x.name)))throw Error('CE proxy loaded');
 const pe=m.base.add(m.base.add(0x3c).readU32());if(pe.add(8).readU32()!==spec.timestamp)throw Error('Loaded timestamp mismatch');
 const expected={CheckForImprovement:0x3e1150,DecodeTrigger:0x55a680};
 if(spec.functions.length!==2||new Set(spec.functions.map(f=>f.name)).size!==2)throw Error('Wrong hook set');
 for(const f of spec.functions){if(expected[f.name]!==f.rva)throw Error('Unreviewed boundary');const bytes=Array.from(new Uint8Array(m.base.add(f.rva).readByteArray(32))).map(b=>b.toString(16).padStart(2,'0')).join('');if(bytes!==f.bytes)throw Error('Entry fingerprint mismatch');}
 if(m.base.add(0xabdc48).readU8()!==0)throw Error('Configured-name comparison byte changed');
 if(cfg.player!==3||cfg.city!==655369||cfg.maxPairs!==64||!Array.isArray(cfg.improvementCatalog)||cfg.improvementCatalog.length>256)throw Error('Wrong scope/catalog');
 const io=createMemoryIO({ptr,findRangeByAddress:p=>Process.findRangeByAddress(p)}),ob=makeWorkObserver(io,cfg),hooks=[];
 for(const f of spec.functions)hooks.push(Interceptor.attach(m.base.add(f.rva),{
  onEnter(){this.observation=null;try{const ret=this.returnAddress;const caller=ret.compare(m.base)>=0&&ret.compare(m.base.add(m.size))<0?ret.sub(m.base).toString():null;
   this.observation=ob.enter(f.name,{object:this.context.rcx.toString(),node:this.context.rcx.toString(),stack:this.context.rsp.toString(),aiInstance:this.context.r9.toString(),thread:this.threadId,callerRva:caller});
  }catch(_){ob.stats.errors++;}},
  onLeave(ret){try{ob.leave(this.observation,ret.toString(),ret.toInt32());}catch(_){ob.stats.errors++;}}
 }));
 rpc.exports={status(){return{installed:true,hooks:hooks.length,enabled:ob.status().enabled,module_path:m.path,module_size:m.size,loaded_timestamp:pe.add(8).readU32(),validated_entry_fingerprints:spec.functions,config:cfg,comparisonByte:0,read_only:true};},start(){return ob.start();},snapshot(){return ob.snapshot();},freeze(){return ob.freeze();}};
}
