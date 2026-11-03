'use strict';
const state = Memory.alloc(524288), harnessState=Memory.alloc(16);
const win=Process.getModuleByName('kernel32.dll');
const kernel = new CModule(__KERNEL_C__,{state,query_memory:win.getExportByName('VirtualQuery')});
const target = new CModule(__TARGET_C__,{harness:harnessState,create_thread:win.getExportByName('CreateThread'),wait_one:win.getExportByName('WaitForSingleObject'),close_handle:win.getExportByName('CloseHandle')});
const stateSize=new NativeFunction(kernel.state_size,'uint',[])();
if(stateSize>524288)throw Error('State capacity');
new NativeFunction(kernel.initialize,'void',[])();
const publishNative=new NativeFunction(kernel.publish,'int',['pointer','pointer','pointer']);
const modeNative=new NativeFunction(kernel.set_mode,'int',['int']);
const snapshotNative=new NativeFunction(kernel.snapshot,'uint',['pointer','uint']);

const row=Memory.alloc(0x78*3),city=Memory.alloc(0x200),plot=Memory.alloc(0x100);
const cityBuild=Memory.alloc(0x500),scoreVector=Memory.alloc(20*4),coordinatesOut=Memory.alloc(8);
const extraVectors=[Memory.alloc(20*4),Memory.alloc(20*4)],extraPlots=[Memory.alloc(0x100),Memory.alloc(0x100)];
const reservationCells=[Memory.alloc(12),Memory.alloc(12),Memory.alloc(12)];
reservationCells.forEach((p,i)=>{p.writeS32(-1);p.add(4).writeS32(-2559744);row.add(i*0x78+0x48).writePointer(p);});
row.add(8).writeS32(10);row.add(12).writeS32(10);row.add(0x55).writeU8(1);row.add(0x5a).writeU8(1);
row.add(0x70).writeS16(3);row.add(0x74).writeS32(131073);
city.add(0xd8).writeS32(3);city.add(0xa8).writeS32(131073);
plot.writeS32(256);plot.add(0x28).writeS16(10);plot.add(0x2a).writeS16(10);
row.add(0x20).writePointer(scoreVector);scoreVector.add(11*4).writeS32(768);
cityBuild.add(0x90).writePointer(city);cityBuild.add(0x4c8).writePointer(row);
cityBuild.add(0x4d8).writeU32(1);cityBuild.add(0x80).writeS32(11);
cityBuild.add(0x88).writeS32(20);
// Owned Win64 caller: preserve R12; place stack arguments and row exactly.
const stub=Memory.alloc(Process.pageSize);let returnAddress;
Memory.patchCode(stub,128,code=>{
  const w=new X86Writer(code,{pc:stub});
  w.putBytes([0x41,0x54,0x48,0x83,0xec,0x40]); // pushr12; subrsp64
  w.putBytes([0x4c,0x8b,0xa4,0x24,0x88,0,0,0]); // row eightharg ->r12
  for(const [from,to] of [[0x70,0x20],[0x78,0x28],[0x80,0x30]]){
    w.putBytes([0x48,0x8b,0x84,0x24,from,0,0,0]);w.putBytes([0x48,0x89,0x44,0x24,to]);
  }
  w.putMovRegAddress('rax',target.score);w.putCallReg('rax');returnAddress=stub.add(w.offset);
  w.putBytes([0x48,0x83,0xc4,0x40,0x41,0x5c,0xc3]);w.flush();
});
Memory.protect(stub,Process.pageSize,'r-x');
const call=new NativeFunction(stub,'pointer',['pointer','uint','pointer','int','int','pointer','pointer','pointer']);
const bulk=new NativeFunction(target.run_calls,'uint',['pointer','uint','pointer','pointer','pointer','uint']);
const listener=Interceptor.attach(target.score,{onEnter:kernel.on_enter,onLeave:kernel.on_leave});
const monitorListeners=[
 Interceptor.attach(target.cache_probe,{onEnter:kernel.cache_enter,onLeave:kernel.cache_leave}),
 Interceptor.attach(target.best_probe,{onEnter:kernel.best_enter,onLeave:kernel.best_leave}),
 Interceptor.attach(target.pv_probe,{onEnter:kernel.pv_enter,onLeave:kernel.pv_leave})
];
Interceptor.flush();
const cacheProbe=new NativeFunction(target.cache_probe,'void',['pointer']);
const bestProbe=new NativeFunction(target.best_probe,'int',['pointer','pointer']);
const pvProbe=new NativeFunction(target.pv_probe,'pointer',['pointer','pointer','int','pointer']);

const packet=Memory.alloc(69*4),entryBuffer=Memory.alloc(128*20),snap=Memory.alloc(200000),out=Memory.alloc(8),discount=Memory.alloc(4);discount.writeS32(512);
function snapshot(){const n=snapshotNative(snap,50000);const w=Array.from({length:n},(_,i)=>snap.add(i*4).readS32());return {header:w.slice(0,10),records:Array.from({length:w[2]},(_,i)=>w.slice(10+i*11,21+i*11))};}
function publish(rows,version=1,allowed=[3,5]){[74,46,20,version,rows.length,...Array.from({length:64},(_,i)=>allowed.includes(i)?1:0)].forEach((v,i)=>packet.add(i*4).writeS32(v));rows.forEach((r,i)=>r.forEach((v,j)=>entryBuffer.add(i*20+j*4).writeS32(v)));return publishNative(packet,entryBuffer,returnAddress);}
function invoke(base,d=11,bad=0){plot.writeS32(base);plot.add(4).writeS32(bad);const before=harnessState.readU32();const result=call(out,d,discount,3,50,plot,city,row);return {score:out.readS32(),samePointer:result.equals(out),calls:harnessState.readU32()-before};}
rpc.exports={exercise(){const checks=[];function check(name,actual,expected){checks.push({name,actual,expected,pass:JSON.stringify(actual)===JSON.stringify(expected)});}
 const a=[3,131073,11,750,1048576],b=[5,17,12,751,1048576];
 check('two-city publication',publish([a,b]),0);check('enable',modeNative(2),0);
 check('pointer ABI additive',invoke(100),{score:1048676,samePointer:true,calls:1});
 check('negative native score',invoke(-128),{score:1048448,samePointer:true,calls:1});
 check('zero preserved',invoke(0),{score:0,samePointer:true,calls:1});
 check('sentinel preserved',invoke(-2559744),{score:-2559744,samePointer:true,calls:1});
 check('overflow preserved',invoke(2147483647),{score:2147483647,samePointer:true,calls:1});
 check('wrong district excluded',invoke(256,12),{score:256,samePointer:true,calls:1});
 check('enabled replacement refused',publish([],2),-1);
 city.add(0xd8).writeS32(0);check('human scope excluded',invoke(256),{score:256,samePointer:true,calls:1});city.add(0xd8).writeS32(3);
 city.add(0xd8).writeS32(5);city.add(0xa8).writeS32(17);plot.add(0x28).writeS16(11);row.add(8).writeS32(11);row.add(0x70).writeS16(5);row.add(0x74).writeS32(17);
 check('second city and quarter',invoke(512,12),{score:1049088,samePointer:true,calls:1});
 check('drain',modeNative(0),0);check('duplicate city rejected',publish([a,a],2),-1);check('human entry rejected',publish([[0,0,11,750,1048576]],2),-1);
 check('delta outside declared contract rejected',publish([[3,131073,11,750,1]],2),-1);
 check('refresh empty table',publish([],2),0);check('enable empty',modeNative(2),0);check('removed candidate not changed',invoke(512,12),{score:512,samePointer:true,calls:1});modeNative(0);
 city.add(0xd8).writeS32(3);city.add(0xa8).writeS32(131073);plot.add(0x28).writeS16(10);row.add(8).writeS32(10);row.add(0x70).writeS16(3);row.add(0x74).writeS32(131073);
 check('refresh target',publish([a],3),0);check('version replay rejected',publish([a],3),-1);modeNative(2);
 cityBuild.add(0x84).writeS32(1);const result=invoke(100);scoreVector.add(11*4).writeS32(result.score);cacheProbe(cityBuild);const best=bestProbe(cityBuild,coordinatesOut);const pointer=pvProbe(cityBuild,out,11,plot);
 check('native monitor best',best,11);check('monitor PV pointer',pointer.equals(out),true);check('monitor PV score',out.readS32(),1048676);check('all monitor boundaries',snapshot().records.map(r=>r[10]),[0,1,2,3]);
 check('all arguments forwarded',harnessState.add(4).readU32(),0);modeNative(0);publish([a],4);modeNative(2);
 for(let i=0;i<513;i++)invoke(100);
 const terminal=snapshot();check('mutation budget disables',terminal.header[0],0);check('mutation budget exact512',terminal.header[5],512);check('budget fault explicit',terminal.header[7],1);
 return {checks,final:terminal.header,passed:checks.every(c=>c.pass)};
}};
