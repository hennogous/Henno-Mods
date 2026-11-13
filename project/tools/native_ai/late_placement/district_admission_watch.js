'use strict';
// Diagnostic-only: live Quarter requests -> native admission -> rejection flags.
// The controller starts this at an inactive saved turn and freezes it before
// MainMenu. No Lua/native function calls, game-data writes, argument changes or
// return replacements occur. Never infer a production loss from absent SUBMITTED:
// ReceiveContract validates before appending/logging an accepted request.
const ADMISSION_SHA = '092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f';
const ADMISSION_POINTS = {receive:0x3e9500, validate:0x3fa8e0, zone:0xf97b0,
  districtCount:0x11eb20, allowedCount:0x11eae0};
let moduleSpec, config, installed=false, enabled=false, frozen=false, stopReason=null;
let sequence=0, callID=0, active=0, interval=null;
const records=[], faults=[], hooks=[], stacks=new Map();
const totals={receive:0, validate:0, zone:0, unresolvedHandle:0};
const stack=t=>stacks.get(t)||[];
const top=(t,kind)=>{const s=stack(t);for(let i=s.length-1;i>=0;i--)if(s[i].kind===kind)return s[i];return null;};
function fault(error) {
  enabled=false; stopReason=stopReason||'observation_fault';
  if(faults.length<16)faults.push(String(error));
}
function emit(kind, fields) {
  if(records.length>=config.maxRecords){enabled=false;stopReason=stopReason||'record_bound';return;}
  records.push(Object.assign({sequence:++sequence,kind,window:interval&&{...interval}},fields));
}
function push(thread, frame) {
  const s=stack(thread);
  if(s.length>=16||(!stacks.has(thread)&&stacks.size>=16))throw Error('native scope bound');
  s.push(frame);stacks.set(thread,s);active++;
}
function pop(thread, frame) {
  const s=stack(thread);
  if(s[s.length-1]!==frame){fault('unpaired native callback');return;}
  s.pop();active--;if(!s.length)stacks.delete(thread);
}
function city(build) {
  const p=build.add(0x90).readPointer();if(p.isNull())return null;
  return {player:p.add(0xd8).readS32(),city:p.add(0xa8).readS32(),
    population:p.add(0x268).readS32(),cityPointer:p.toString(),buildPointer:build.toString()};
}
function request(p) {
  if(p.isNull())return null;
  // q8 is signed native utility (256 per whole point), not Gold. It joins
  // the tree's truncated value to this request; recording it changes no bid.
  return {pointer:p.toString(),contract:p.add(0x110).readS32(),state:p.add(0xb0).readS32(),
    district:p.add(0x1a8).readS32(),unit:p.add(0x178).readS32(),building:p.add(0x190).readS32(),
    requiredCity:p.add(0x1d8).readS32(),q8:p.add(0x158).readS32(),
    x:p.add(0x1c0).readS32(),y:p.add(0x1c4).readS32()};
}
const relevant=(who,r)=>who&&who.player>=1&&who.player<=5&&r&&
  [36,37].includes(r.district)&&r.unit===-1&&r.building===-1;
function snapshot() {
  return {installed,hooks:hooks.length,frozen,active,stopReason,
    totals:{...totals},faults:[...faults],records:[...records]};
}
function attach(name, callbacks) {
  hooks.push(Interceptor.attach(Process.getModuleByName(moduleSpec.name).base.add(ADMISSION_POINTS[name]),callbacks));
}
rpc.exports={
  init(spec,cfg) {
    if(installed||hooks.length)throw Error('Admission observer already initialized');
    if(Process.arch!=='x64'||Process.pointerSize!==8||spec.sha256!==ADMISSION_SHA||
       spec.name!=='GameCore_XP2_FinalRelease.dll'||cfg.maxRecords!==10000||
       !Number.isInteger(cfg.start)||!Number.isInteger(cfg.through)||
       cfg.through<=cfg.start||cfg.through-cfg.start>30)throw Error('Unqualified admission profile');
    moduleSpec=spec;config=cfg;interval={after:cfg.start,through:cfg.start};
    const mod=Process.getModuleByName(spec.name);
    if(mod.path.replace(/\\/g,'/').toLowerCase()!==spec.path.replace(/\\/g,'/').toLowerCase()||
       mod.size!==spec.imageSize)throw Error('Different loaded admission module');
    const pe=mod.base.add(0x3c).readU32();
    if(mod.base.add(pe+8).readU32()!==spec.timestamp)throw Error('Different loaded PE timestamp');
    // Verify every entry before installing the first trampoline. Whole-file SHA
    // verification is host-side; this detects a CE/other detour at these entries.
    for(const [name,rva]of Object.entries(ADMISSION_POINTS)) {
      const point=spec.points[name];
      if(point.rva!==rva||!/^[0-9a-f]{64}$/.test(point.prefix))throw Error('Wrong entry profile '+name);
      const bytes=new Uint8Array(mod.base.add(rva).readByteArray(32));
      const actual=Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('');
      if(actual!==point.prefix)throw Error('Loaded entry differs '+name);
    }
    try {
      // Windows x64: RCX=this CityBuild, RDX=ContractHandle*. The handle's +0
      // cache is safe to inspect. A null cache may need a resolving native call;
      // record that omission rather than invoking it and mutating the cache.
      attach('receive',{
        onEnter(args){this.frame=null;if(!enabled)return;
          try {const who=city(args[0]),p=args[1].readPointer();
            if(p.isNull()){totals.unresolvedHandle++;return;}
            // Receive accepts several contract classes. Qualify its Validate
            // vtable slot before reading the UnitRequest-only trailing fields.
            const validate=p.readPointer().add(0x98).readPointer();
            const expected=Process.getModuleByName(moduleSpec.name).base.add(ADMISSION_POINTS.validate);
            if(!validate.equals(expected))return;
            const r=request(p);if(!relevant(who,r))return;
            const f={kind:'receive',id:++callID,who,request:r,pointer:p};
            push(this.threadId,f);this.frame=f;totals.receive++;
            emit('receive-enter',{id:f.id,...who,request:r});
          }catch(e){fault(e);}},
        onLeave(ret){const f=this.frame;if(!f)return;
          try {emit('receive-leave',{id:f.id,...f.who,request:request(f.pointer),
            accepted:(ret.toUInt32()&255)!==0});}
          catch(e){fault(e);}finally{pop(this.threadId,f);}}
      });
      // RCX=request, RDX=CityBuild. Building/unit precedence is excluded above.
      // AL is the native bool. Matching receive IDs join immediate admission to
      // the eventual request state; validations outside Receive are kept too.
      attach('validate',{
        onEnter(args){this.frame=null;if(!enabled)return;
          try {const who=city(args[1]),r=request(args[0]);if(!relevant(who,r))return;
            const parent=top(this.threadId,'receive');
            const f={kind:'validate',id:++callID,who,request:r,pointer:args[0],
              receive:parent&&parent.request.pointer===r.pointer?parent.id:null};
            push(this.threadId,f);this.frame=f;totals.validate++;
            emit('validate-enter',{id:f.id,receive:f.receive,...who,request:r});
          }catch(e){fault(e);}},
        onLeave(ret){const f=this.frame;if(!f)return;
          try {emit('validate-leave',{id:f.id,receive:f.receive,...f.who,
              request:request(f.pointer),accepted:(ret.toUInt32()&255)!==0});}
          catch(e){fault(e);}finally{pop(this.threadId,f);}}
      });
      // CanZone RCX=BuildQueue, EDX=District, R8=XY(two i32), R9=requirements.
      // Requirements +1 is an independent invalid-site byte; +0x20 is the native
      // population-block payload, not the next growth threshold. Allowed slots
      // can increase before the raw payload's population number is reached.
      // Validate rejects these flags even if CanZone's
      // return bool is true. Preserve flags rather than inventing a single reason.
      attach('zone',{
        onEnter(args){this.frame=null;if(!enabled)return;
          try {const v=top(this.threadId,'validate');if(!v||args[1].toInt32()!==v.request.district)return;
            if(args[0].add(0x1e8).readPointer().toString()!==v.who.cityPointer)
              throw Error('CanZone city identity differs from Validate');
            const f={kind:'zone',id:++callID,validate:v.id,receive:v.receive,who:v.who,
              district:args[1].toInt32(),x:args[2].readS32(),y:args[2].add(4).readS32(),
              requirements:args[3],counts:[],allowed:[]};
            if(f.requirements.isNull())throw Error('Null CanZone requirements');
            push(this.threadId,f);this.frame=f;totals.zone++;
          }catch(e){fault(e);}},
        onLeave(ret){const f=this.frame;if(!f)return;
          try {emit('zone',{id:f.id,validate:f.validate,receive:f.receive,...f.who,
            district:f.district,x:f.x,y:f.y,result:(ret.toUInt32()&255)!==0,
            invalidSite:f.requirements.add(1).readU8(),
            requiredPopulation:f.requirements.add(0x20).readS32(),
            districtCounts:f.counts,allowedCounts:f.allowed});}
          catch(e){fault(e);}finally{pop(this.threadId,f);}}
      });
      for(const [name,field]of [['districtCount','counts'],['allowedCount','allowed']])attach(name,{
        onEnter(args){this.zone=enabled?top(this.threadId,'zone'):null;this.flags=null;
          try {if(this.zone&&name==='districtCount'){
            // Five bool arguments after RCX, including the two stack arguments.
            // The native capacity query's flags are 1,0,1,0,0 and count claimed
            // incomplete districts too. Keep other nested calls distinguishable.
            this.flags=Array.from({length:5},(_,i)=>args[i+1].toInt32()&255);
          }}catch(e){fault(e);}},
        onLeave(ret){if(!this.zone)return;
          try {if(this.zone[field].length>=8)throw Error('Repeated capacity read bound');
            this.zone[field].push(name==='districtCount'?{value:ret.toInt32(),flags:this.flags}:
              ret.toInt32());}catch(e){fault(e);}}
      });
      installed=true;
    }catch(e){fault(e);}
    return {installed,hooks:hooks.length,enabled,stopReason,faults:[...faults]};
  },
  start(){if(!installed||frozen||stopReason)throw Error('Observer not ready');enabled=true;return true;},
  window(after,through){
    if(!enabled||!Number.isInteger(after)||!Number.isInteger(through)||after<config.start||
       through<=after||through>config.through||after<interval.after)throw Error('Invalid controller interval');
    interval={after,through};return true;
  },
  freeze(){enabled=false;frozen=active===0;return snapshot();}
};
