'use strict';
const state = Memory.alloc(16384), harnessState=Memory.alloc(16);
const win=Process.getModuleByName('kernel32.dll');
const kernel = new CModule(__KERNEL_C__,{state,query_memory:win.getExportByName('VirtualQuery')});
const target = new CModule(__TARGET_C__,{harness:harnessState,create_thread:win.getExportByName('CreateThread'),wait_one:win.getExportByName('WaitForSingleObject'),close_handle:win.getExportByName('CloseHandle')});
const stateSize=new NativeFunction(kernel.state_size,'uint',[])();
if(stateSize>16384)throw Error('State capacity');
new NativeFunction(kernel.initialize,'void',[])();
const configNative=new NativeFunction(kernel.configure,'int',['pointer','pointer']);
const modeNative=new NativeFunction(kernel.set_mode,'int',['int']);
const snapshotNative=new NativeFunction(kernel.snapshot,'uint',['pointer','uint']);
const evaluateNative=new NativeFunction(kernel.evaluate,'int',['pointer','pointer']);
const row=Memory.alloc(0x78),city=Memory.alloc(0x200),plot=Memory.alloc(0x100);
const cityBuild=Memory.alloc(0x500),scoreVector=Memory.alloc(20*4),coordinatesOut=Memory.alloc(8);
row.add(8).writeS32(10);row.add(12).writeS32(10);row.add(0x55).writeU8(1);row.add(0x5a).writeU8(1);
row.add(0x70).writeS16(3);row.add(0x74).writeS32(131073);
city.add(0xd8).writeS32(3);city.add(0xa8).writeS32(131073);
plot.writeS32(256);plot.add(0x28).writeS16(10);plot.add(0x2a).writeS16(10);
row.add(0x20).writePointer(scoreVector);scoreVector.add(11*4).writeS32(768);
cityBuild.add(0x90).writePointer(city);cityBuild.add(0x4c8).writePointer(row);
cityBuild.add(0x4d8).writeU32(1);cityBuild.add(0x80).writeS32(11);
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
const packet=Memory.alloc(64),outBuffer=Memory.alloc(16),out=outBuffer.add(4),discount=Memory.alloc(4),snap=Memory.alloc(8192);
const readOnlyPage=Memory.alloc(Process.pageSize);
if(!Memory.protect(readOnlyPage,Process.pageSize,'r--'))throw Error('Read-only test page protection');
const validNative=new NativeFunction(kernel.valid_span,'int',['pointer','uint64','int']);
discount.writeS32(512);outBuffer.writeU32(0xa55ac33c);outBuffer.add(8).writeU32(0x11223344);
const parallel=new NativeFunction(target.parallel_calls,'int',['pointer','uint','pointer','pointer','pointer','uint']);
function configure(delta=256,human=0,currentHuman=0,plotIndex=750){
 const words=[7,41,3,3,131073,11,plotIndex,delta,human,currentHuman,74,46,128,20];
 words.forEach((v,i)=>packet.add(i*4).writeS32(v));return configNative(packet,returnAddress);
}
function snapshot(){const n=snapshotNative(snap,2048);if(n>2048)throw Error('Snapshot overflow');const words=[];for(let i=0;i<n;i++)words.push(snap.add(i*4).readS32());return {header:words.slice(0,10),records:Array.from({length:words[2]},(_,i)=>words.slice(10+i*11,21+i*11))};}
rpc.exports={
 info(){return {frida:Frida.version,arch:Process.arch,pointerSize:Process.pointerSize,pid:Process.id,stateSize,caller:returnAddress.toString(),target:target.score.toString(),invocationBytes:snapshot().header[8]};},
 configure(delta,human,currentHuman,plotIndex){return configure(delta,human,currentHuman,plotIndex);},
 configurepacket(words){if(!Array.isArray(words)||words.length!==14||words.some(v=>!Number.isInteger(v)||v< -2147483648||v>2147483647))throw Error('Exact14int32 packet required');words.forEach((v,i)=>packet.add(i*4).writeS32(v));return configNative(packet,returnAddress);},
 validspan(){return {null_read:!!validNative(ptr(0),4,0),null_write:!!validNative(ptr(0),4,1),unmapped_read:!!validNative(ptr(1),4,0),readable_read:!!validNative(readOnlyPage,4,0),read_only_write:!!validNative(readOnlyPage,4,1),writable_write:!!validNative(out,4,1)};},
 monitors(){const before=snapshot().header[2],calls=harnessState.add(8).readU32();
  cacheProbe(cityBuild);const best=bestProbe(cityBuild,coordinatesOut),bestXY=[coordinatesOut.readS32(),coordinatesOut.add(4).readS32()];
  const pvPointer=pvProbe(cityBuild,out,11,plot).equals(out),pv=out.readS32();
  cityBuild.add(0x80).writeS32(-1);const noBest=bestProbe(cityBuild,coordinatesOut);cityBuild.add(0x80).writeS32(11);
  const nullPointer=pvProbe(cityBuild,out,11,ptr(0)).equals(out),nullPV=out.readS32(),s=snapshot();
  return {best,bestXY,pvPointer,pv,noBest,nullPointer,nullPV,monitorCalls:harnessState.add(8).readU32()-calls,
   records:s.records.slice(before),active:s.header[1],errors:s.header[6],fatal:s.header[9]};},
 mode(value){return modeNative(value);},
 invoke(base,district=11,badReturn=0){plot.writeS32(base);plot.add(4).writeS32(badReturn);const before=harnessState.readU32();const p=call(out,district,discount,3,50,plot,city,row);return {score:out.readS32(),samePointer:p.equals(out),originalCalls:harnessState.readU32()-before};},
 evaluate(words){if(!Array.isArray(words)||words.length!==14||words.some(v=>!Number.isInteger(v)||v< -2147483648||v>2147483647))throw Error('Exact14int32 packet required');words.forEach((v,i)=>packet.add(i*4).writeS32(v));const reason=evaluateNative(packet,out);return {score:out.readS32(),reason};},
 bulk(count,district=12){const start=Date.now(),before=harnessState.readU32();bulk(stub,count,row,city,plot,district);return {count:harnessState.readU32()-before,milliseconds:Date.now()-start,snapshot:snapshot()};},
 snapshot,
 setflags(build,owned,purchase){row.add(0x55).writeU8(build);row.add(0x5a).writeU8(owned);row.add(0x57).writeU8(purchase);},
 guards(){return {prefix:outBuffer.readU32(),suffix:outBuffer.add(8).readU32(),argErrors:harnessState.add(4).readS32()};},
 recursive(base){plot.add(8).writeS32(1);plot.add(4).writeS32(0);plot.writeS32(base);try{const before=harnessState.readU32();const p=call(out,11,discount,3,50,plot,city,row);return {score:out.readS32(),samePointer:p.equals(out),originalCalls:harnessState.readU32()-before};}finally{plot.add(8).writeS32(0);}},
 parallel(count){if(!Number.isInteger(count)||count<1||count>250000)throw Error('Bounded count');const before=harnessState.readU32(),start=Date.now();const result=parallel(stub,count,row,city,plot,12);return {result,count:harnessState.readU32()-before,milliseconds:Date.now()-start,snapshot:snapshot()};},
 finish(){modeNative(0);if(snapshot().header[1])throw Error('Pending invocation');listener.detach();monitorListeners.forEach(l=>l.detach());Interceptor.flush();return snapshot();}
};
