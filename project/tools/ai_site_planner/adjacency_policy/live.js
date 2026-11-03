 'use strict';
const PROFILE='csc-adjacency-policy-v1',SPEC=__SPEC__,CONFIG=__CONFIG__;
function requireCondition(v,m){if(!v)throw Error(m);}
function int(v,a,b){return Number.isInteger(v)&&v>=a&&v<=b;}
function normalizedPath(v){return v.replaceAll('/','\\').toLowerCase();}
requireCondition(CONFIG.profile===PROFILE&&CONFIG.width>0&&CONFIG.height>0,'Explicit adjacency policy config required');
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

const state=Memory.alloc(524288),header=Memory.alloc(69*4),table=Memory.alloc(128*20),snap=Memory.alloc(200000);
const kernel=new CModule(__KERNEL_C__,{state,query_memory:Process.getModuleByName('kernel32.dll').getExportByName('VirtualQuery')});
requireCondition(new NativeFunction(kernel.state_size,'uint',[])()<=524288,'State capacity');
new NativeFunction(kernel.initialize,'void',[])();
const publishNative=new NativeFunction(kernel.publish,'int',['pointer','pointer','pointer']);
const modeNative=new NativeFunction(kernel.set_mode,'int',['int']);
const snapshotNative=new NativeFunction(kernel.snapshot,'uint',['pointer','uint']);
let entries=[],version=0,started=false,frozen=false,installationError=null;const listeners=[];
function snapshot(){const n=snapshotNative(snap,50000);requireCondition(n>=10&&n<=50000,'Snapshot capacity');
 const w=Array.from({length:n},(_,i)=>snap.add(i*4).readS32());requireCondition(n===10+w[2]*11,'Snapshot framing');
 const kinds=['net','cache','best','pv'];
 return {profile:PROFILE,read_only:false,version:w[8],entries,stats:{mode:w[0],active:w[1],records:w[2],callbacks:w[3]>>>0,admitted:w[4]>>>0,changed:w[5]>>>0,errors:w[6]>>>0,fatal:w[7],entryCount:w[9]},
 records:Array.from({length:w[2]},(_,i)=>{const r=w.slice(10+i*11,21+i*11);return {player:r[0],city:r[1],district:r[2],plot:r[3],x:r[4],y:r[5],base:r[6],result:r[7],reason:r[8],eligible:r[9],k:kinds[r[10]]};})};
}
async function drain(){modeNative(0);const deadline=Date.now()+5000;while(snapshot().stats.active){requireCondition(Date.now()<deadline,'Native drain timed out');await new Promise(r=>setTimeout(r,10));}}
function validateRows(rows){requireCondition(Array.isArray(rows)&&rows.length<=128,'Policy capacity');const cities=new Set();
 for(const e of rows){requireCondition(int(e.player,0,63)&&CONFIG.originalAI.includes(e.player)&&int(e.city,0,2147483647)&&CONFIG.districtIndices.includes(e.district)&&int(e.plot,0,CONFIG.width*CONFIG.height-1)&&e.delta===1048576,'Invalid policy entry');
 const key=e.player+':'+e.city;requireCondition(!cities.has(key),'Duplicate city');cities.add(key);}}
function writePolicy(rows,next){validateRows(rows);requireCondition(int(next,1,1000)&&next>version,'Monotonic version');
 const h=[CONFIG.width,CONFIG.height,CONFIG.districtCount,next,rows.length,...Array.from({length:64},(_,i)=>CONFIG.originalAI.includes(i)?1:0)];
 h.forEach((v,i)=>header.add(i*4).writeS32(v));rows.forEach((e,i)=>[e.player,e.city,e.district,e.plot,e.delta].forEach((v,j)=>table.add(i*20+j*4).writeS32(v)));
 requireCondition(publishNative(header,table,module.base.add(0x3e30be))===0,'Native publication refused');entries=rows;version=next;requireCondition(modeNative(2)===0,'Enable refused');return snapshot();}
rpc.exports={
 status(){return {profile:PROFILE,read_only:false,installed:listeners.length===4&&!installationError,hooks:listeners.length,enabled:snapshot().stats.mode!==0,module_path:module.path,module_size:module.size,loaded_timestamp:loadedTimestamp,validated_entry_fingerprints:SPEC.functions,config:CONFIG,installation_error:installationError};},
 start(){requireCondition(!started&&!frozen&&listeners.length===4&&!installationError,'Single start');started=true;return writePolicy([],1);},
 async publish(packet){requireCondition(started&&!frozen,'Publication phase');validateRows(packet.entries);requireCondition(packet.version>version,'Policy version');await drain();const previous=snapshot();const current=writePolicy(packet.entries,packet.version);return {previous,current};},
 snapshot,
 async freeze(){frozen=true;await drain();return snapshot();}
};
try{
 listeners.push(Interceptor.attach(addresses.DistrictNetValue,{onEnter:kernel.on_enter,onLeave:kernel.on_leave}));
 listeners.push(Interceptor.attach(addresses.CalculateDistrictValues,{onEnter:kernel.cache_enter,onLeave:kernel.cache_leave}));
 listeners.push(Interceptor.attach(addresses.GetBestDistrict,{onEnter:kernel.best_enter,onLeave:kernel.best_leave}));
 listeners.push(Interceptor.attach(addresses.PresentValueOf,{onEnter:kernel.pv_enter,onLeave:kernel.pv_leave}));Interceptor.flush();
}catch(e){installationError=String(e.stack||e);modeNative(0);}
// Retain all callbacks until the held game process exits. No detach/unload RPC.
