'use strict';
// Diagnostic only. XP2 SHA092abfbb, text-identical reference SHA324c51e9.
// Observe the raw matrix before ordinary activation and the exact candidate
// utility read by GetBestDistrict's reservation comparison. CE owns its entry
// hooks; these three unpatched sites avoid overlapping those trampolines. No
// native calls, game-data writes, callbacks into Lua or forced choices.
const points={activate:0x3e2820,aggregate:0x3e2941,compare:0x3e4b2c};
const guards={activate:'4053564883ec38410fb6d8488bf1',aggregate:'488bcee857dcffff',compare:'3bcf7e463bcb7c42'};
const layout={city:0x90,owner:0xd8,id:0xa8,rows:0x4c8,count:0x4d8,
 rowSize:0x78,x:8,y:12,scores:0x20,reservation:0x48,rowOwner:0x70,rowCity:0x74};
let module,config,enabled=false;const hooks=[],records=[],faults=[];
function integer(p,o){return p.add(o).readS32();}
function emit(row){if(records.length>=2048)throw Error('Customer comparison journal bound');records.push(row);}
function fail(e){enabled=false;if(faults.length<8)faults.push(String(e));}
function turn(){return integer(module.base.add(0xb8aa68).readPointer(),0xc0);}
function matches(row,target){return row.add(layout.rowOwner).readS16()===target.player&&
 integer(row,layout.rowCity)===target.city&&integer(row,layout.x)===target.x&&integer(row,layout.y)===target.y;}
function snapshot(build,kind){
 const city=build.add(layout.city).readPointer(),player=integer(city,layout.owner),id=integer(city,layout.id);
 const targets=config.targets.filter(t=>t.player===player&&t.city===id);if(!targets.length)return;
 const count=build.add(layout.count).readU32();if(count>37)throw Error('Customer row bound');
 const start=build.add(layout.rows).readPointer();
 for(let i=0;i<count;i++){
  const row=start.add(i*layout.rowSize);
  for(const target of targets)if(matches(row,target))emit({kind,turn:turn(),...target,
   valueQ8:integer(row.add(layout.scores).readPointer(),target.district*4),
   reservationId:row.add(layout.reservation).readPointer().readS32()});
 }
}
rpc.exports={
 init(spec,cfg){
  if(hooks.length||Process.platform!=='windows'||Process.arch!=='x64'||
   spec.sha256!=='092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f'||
   !Array.isArray(cfg.targets)||!cfg.targets.length||cfg.targets.length>8)throw Error('Unqualified customer scope');
  module=Process.getModuleByName('GameCore_XP2_FinalRelease.dll');config=cfg;
  if(module.size!==12976128||module.path.replace(/\\/g,'/').toLowerCase()!==spec.path.replace(/\\/g,'/').toLowerCase())
   throw Error('Customer native image differs');
  for(const[name,rva]of Object.entries(points)){
   const expected=guards[name],bytes=new Uint8Array(module.base.add(rva).readByteArray(expected.length/2));
   const actual=Array.from(bytes,b=>b.toString(16).padStart(2,'0')).join('');
   if(actual!==expected)throw Error('Customer native site differs: '+name);
  }
  hooks.push(Interceptor.attach(module.base.add(points.activate),{onEnter(args){if(!enabled)return;
   try{
    if(args[2].toInt32()&255)snapshot(args[0],'before');
   }catch(e){fail(e);}
  }}));
  // Preserve the original aggregation CALL and its exact return address: CE's
  // guarded late policy checks that address. Observe at the returned-to code,
  // where RSI is still CityBuild*, before the subsequent district comparison.
  hooks.push(Interceptor.attach(module.base.add(points.aggregate),function(){if(!enabled)return;
   try{snapshot(this.context.rsi,'aggregate');}catch(e){fail(e);}
  }));
  hooks.push(Interceptor.attach(module.base.add(points.compare),function(){if(!enabled)return;
   try{
    const c=this.context,row=c.rsi,district=c.r14.toInt32();
    for(const target of config.targets)if(target.district===district&&matches(row,target)){
     const valueQ8=c.rcx.toInt32();
     if(valueQ8!==integer(row.add(layout.scores).readPointer(),district*4))throw Error('Customer compared value differs');
     emit({kind:'compare',turn:turn(),...target,valueQ8,reservationQ8:c.rdi.toInt32(),bestSoFarQ8:c.rbx.toInt32()});
    }
   }catch(e){fail(e);}
  }));
  enabled=true;return{installed:true,hooks:hooks.length};
 },
 freeze(){enabled=false;return{records,faults,hooks:hooks.length};}
};
