'use strict';
// Explicit experimental mutation; native callbacks only. Retain until native exit.
function deepFreeze(value){if(value && typeof value==='object'){Object.values(value).forEach(deepFreeze);Object.freeze(value);}return value;}
const SPEC=deepFreeze(__SPEC__),CONFIG=deepFreeze(__CONFIG__);
const PROFILE='district-score-extension-v1';
const EXPECTED_SHA='324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c';
const EXPECTED_FUNCTIONS={
 DistrictNetValue:[0x52a440,'8954241055535657415441554156488d6c24f14881eca0000000448b756f33c0'],
 CalculateDistrictValues:[0x3dfee0,'4c8bdc41554881eca000000083b9d8040000004c8be90f84ae030000488b91c8'],
 GetBestDistrict:[0x3e4a50,'48894c24085355564154415541574883ec284c8bea488be9e873be3e00488bb5'],
 PresentValueOf:[0x3e7f40,'4d63d84c8bd2488bc14183fbff750833c9488bc2890ac34d85c9744d8b81d804']
};
function requireCondition(value,message){if(!value)throw Error(message);}
function normalizedPath(value){return String(value).replace(/\\/g,'/').toLowerCase();}
function int(value,min,max){return Number.isInteger(value)&&value>=min&&value<=max;}
requireCondition(Process.platform==='windows'&&Process.arch==='x64'&&Process.pointerSize===8,'Windows x64 required');
requireCondition(Frida.version==='17.24.3','Pinned Frida version required');
requireCondition(SPEC.sha256===EXPECTED_SHA&&SPEC.image_size===12976128&&SPEC.timestamp===1719431003,'Unreviewed native identity');
requireCondition(Array.isArray(SPEC.functions)&&SPEC.functions.length===4&&new Set(SPEC.functions.map(f=>f.name)).size===4,'Exact four functions required');
for(const f of SPEC.functions){const e=EXPECTED_FUNCTIONS[f.name];requireCondition(e&&f.rva===e[0]&&f.bytes===e[1],'Unreviewed native fingerprint');}
requireCondition(CONFIG.profile===PROFILE&&['baseline','treatment'].includes(CONFIG.mode)&&
 CONFIG.player===4&&CONFIG.city===655369&&CONFIG.districtType==='DISTRICT_CSC_BAKERS_QUARTER'&&
 CONFIG.originalHuman===false&&CONFIG.currentHuman===false&&CONFIG.mappingVerified===true&&
 CONFIG.plot===3076&&CONFIG.plotX===42&&CONFIG.plotY===41&&CONFIG.mapWidth===74&&CONFIG.mapHeight===46&&
 CONFIG.maxChanges===1&&CONFIG.maxRecords===128&&CONFIG.deltaQ8===256&&
 CONFIG.session===7&&CONFIG.epoch===1&&CONFIG.version===1&&
 int(CONFIG.districtCount,1,4096)&&CONFIG.districtIndexLimit===CONFIG.districtCount&&
 int(CONFIG.districtIndex,0,CONFIG.districtCount-1),'Unreviewed immutable target configuration');
requireCondition(typeof SPEC.path==='string'&&SPEC.path.length>0,'Native module path required');
const matchingModules=Process.enumerateModules().filter(m=>normalizedPath(m.path)===normalizedPath(SPEC.path));
requireCondition(matchingModules.length===1,'Exact loaded module path missing or ambiguous');
const module=matchingModules[0];
requireCondition(module.size===SPEC.image_size,'Loaded image size mismatch');
requireCondition(module.base.readU16()===0x5a4d,'Invalid DOS header');
const peOffset=module.base.add(0x3c).readU32();
requireCondition(peOffset>=0x40&&peOffset<=module.size-0x58,'Invalid PE header offset');
const pe=module.base.add(peOffset);
requireCondition(pe.readU32()===0x4550&&pe.add(0x18).readU16()===0x20b,'PE32+ header required');
const loadedTimestamp=pe.add(8).readU32();
requireCondition(loadedTimestamp===SPEC.timestamp&&pe.add(0x50).readU32()===SPEC.image_size,'Loaded PE identity mismatch');
const addresses={};
for(const f of SPEC.functions){
 requireCondition(f.rva>=0&&f.rva+f.bytes.length/2<=module.size,'Fingerprint outside image');
 const address=module.base.add(f.rva);
 const actual=Array.from(new Uint8Array(address.readByteArray(f.bytes.length/2)),v=>v.toString(16).padStart(2,'0')).join('');
 requireCondition(actual===f.bytes,'Loaded entry fingerprint mismatch: '+f.name);addresses[f.name]=address;
}
const state=Memory.alloc(16384),packet=Memory.alloc(64),snapshotBuffer=Memory.alloc(8192);
const windows=Process.getModuleByName('kernel32.dll');
const kernel=new CModule(__KERNEL_C__,{state,query_memory:windows.getExportByName('VirtualQuery')});
const stateSize=new NativeFunction(kernel.state_size,'uint',[])();
requireCondition(stateSize<=16384,'Native state exceeds allocation');
new NativeFunction(kernel.initialize,'void',[])();
const configureNative=new NativeFunction(kernel.configure,'int',['pointer','pointer']);
const modeNative=new NativeFunction(kernel.set_mode,'int',['int']);
const snapshotNative=new NativeFunction(kernel.snapshot,'uint',['pointer','uint']);
const policy=[CONFIG.session,CONFIG.epoch,CONFIG.version,CONFIG.player,CONFIG.city,CONFIG.districtIndex,
 CONFIG.plot,CONFIG.deltaQ8,0,0,CONFIG.mapWidth,CONFIG.mapHeight,CONFIG.maxChanges,CONFIG.districtCount];
policy.forEach((v,i)=>packet.add(i*4).writeS32(v));
requireCondition(configureNative(packet,module.base.add(0x3e30be))===0,'Native disabled configuration rejected');
const listeners=[];
let started=false,frozen=false,installationError=null;
function snapshot(){
 const count=snapshotNative(snapshotBuffer,2048);
 requireCondition(count>=10&&count<=2048,'Native snapshot capacity failure');
 const words=Array.from({length:count},(_,i)=>snapshotBuffer.add(i*4).readS32());
 requireCondition(words[2]>=0&&words[2]<=128&&count===10+words[2]*11,'Native record framing failure');
 const kinds=['net','cache','best','pv'];
 const records=Array.from({length:words[2]},(_,i)=>{
  const w=words.slice(10+i*11,21+i*11);requireCondition(int(w[10],0,3),'Unknown native record kind');
  return {k:kinds[w[10]],player:w[0],city:w[1],district:w[2],plot:w[3],x:w[4],y:w[5],base:w[6],result:w[7],reason:w[8],eligible:w[9]};
 });
 return {profile:PROFILE,read_only:false,stats:{callbacks:words[3]>>>0,admitted:words[4]>>>0,changed:words[5]>>>0,
  errors:words[6]>>>0,records:words[2],suppressed:words[7]>>>0,active:words[1],mode:words[0]},
  records,saturated:words[7]!==0,fatal:words[9]!==0,invocation_bytes:words[8]};
}
rpc.exports={
 status(){const s=snapshot();return {profile:PROFILE,read_only:false,installed:listeners.length===4&&!installationError,enabled:s.stats.mode!==0,
  hooks:listeners.length,module_path:module.path,module_size:module.size,loaded_timestamp:loadedTimestamp,
  validated_entry_fingerprints:SPEC.functions,config:CONFIG,stats:s.stats,saturated:s.saturated,fatal:s.fatal,installation_error:installationError};},
 start(){requireCondition(listeners.length===4&&!installationError,'Complete disabled hook installation required');requireCondition(!started&&!frozen,'Single immutable window only');const before=snapshot();
  requireCondition(before.stats.mode===0&&before.stats.active===0&&!before.fatal,'Native start not quiescent');
  requireCondition(modeNative(CONFIG.mode==='treatment'?2:1)===0,'Native start rejected');started=true;return snapshot();},
 snapshot,
 async freeze(){frozen=true;modeNative(0);const deadline=Date.now()+5000;
  while(true){const s=snapshot();requireCondition(s.stats.mode===0,'Native freeze did not disable');
   if(s.stats.active===0)return s;
   requireCondition(Date.now()<deadline,'Native invocation drain timed out');
   await new Promise(resolve=>setTimeout(resolve,10));
  }
 }
};
// RPC freeze remains available even when only a prefix of hooks attached.
// A failed installation retains its disabled native callbacks until process exit.
try{
 listeners.push(Interceptor.attach(addresses.DistrictNetValue,{onEnter:kernel.on_enter,onLeave:kernel.on_leave}));
 listeners.push(Interceptor.attach(addresses.CalculateDistrictValues,{onEnter:kernel.cache_enter,onLeave:kernel.cache_leave}));
 listeners.push(Interceptor.attach(addresses.GetBestDistrict,{onEnter:kernel.best_enter,onLeave:kernel.best_leave}));
 listeners.push(Interceptor.attach(addresses.PresentValueOf,{onEnter:kernel.pv_enter,onLeave:kernel.pv_leave}));
 Interceptor.flush();
}catch(error){installationError=String(error.stack||error);modeNative(0);}
// Intentionally no detach, dispose, reconfigure, or unload RPC while native lives.
