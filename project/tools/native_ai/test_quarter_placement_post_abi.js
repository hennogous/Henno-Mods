'use strict';
const assert=require('assert'),fs=require('fs'),M=require('./quarter_placement_post_observer.js');
const cfg={profile:'quarter-placement-post-v2',player:3,city:131073,districtType:'DISTRICT_CSC_BAKERS_QUARTER',districtIndex:11,districtIndexLimit:20,privateYieldDefaultValue:1,privateYieldIndex:7,yieldIndexLimit:12,mappingVerified:true,mapWidth:74,mapHeight:46,maxPairs:64,maxChoices:32,maxRows:64,maxScopeDepth:16,maxThreads:8,maxNormalizations:512,maxValuesPerNet:4,maxCallbacks:1000000,maxTrackedMs:300000};
const add=(p,o)=>'0x'+(BigInt(p)+BigInt(o)).toString(16);
const reg=v=>({toString:()=>typeof v==='string'?v:'0x'+BigInt.asUintN(64,BigInt(v)).toString(16),toInt32:()=>Number(BigInt.asIntN(32,BigInt(v)))});
function context(name,raw=4,index=7){return{rsp:reg('0x800000'),rbp:reg('0x810000'),rax:reg(name==='own_normalize_post'?'0x810040':name==='wrapper_normalize_post'?'0x800070':'0x800058'),r12:reg(raw),r14:reg(index),r13:reg(index),r8:reg(99),rcx:reg('0xdeadbeef')};}
let checks=0;function test(name,fn){fn();checks++;console.log('PASS '+name);}
function setup(){
 const mem=new Map(),city='0x200000',plot='0x300000',row='0x400000';let reads=0;
 const put=(p,o,t,v)=>mem.set(add(p,o)+':'+t,v);
 const io={add,offset:(a,b)=>Number(BigInt(a)-BigInt(b)),read(p,o,t){reads++;const k=add(p,o)+':'+t;return mem.has(k)?{value:mem.get(k)}:{error:'fixture_unmapped'};}};
 for(const[o,t,v]of[[0x64,'i32',10],[0x68,'i32',10],[0x70,'i16',3],[0x74,'i32',131073]])put(row,o,t,v);
 put(city,0xd8,'i32',3);put(city,0xa8,'i32',131073);put(plot,0x28,'i16',10);put(plot,0x2a,'i16',10);put('0x600000',0,'i32',256);
 const o=M.makePlacementObserver(io,cfg);o.start();o.enter('city_evaluation',{thread:1,row});
 const frame=o.enter('district_value',{thread:1,output:'0x600200',districtIndex:11,discount:'0x600000',readyTurn:1,horizon:10,plot,city});
 function post(name,value,raw=4,index=7,override={}){const a=Object.assign(M.decodePostPoint(name,context(name,raw,index),1,io),override);put(a.rax,0,'i32',value);o.point(name,a);return a;}
 return{o,frame,put,post,io,reads:()=>reads};
}
test('exact10 local hookpoints and no hot global hooks',()=>{
 const points={district_value:0x52d500,net_value:0x52a440,wrapper_normalize_post:0x52d91d,own_normalize_post:0x52d9cc,competing_normalize_post:0x52dceb,competitor_compare:0x52ddbb,competitor_merge:0x52ddd3,city_evaluation:0x3e2aa0,get_best_district:0x3e4a50,try_reserve:0x3ea040};
 assert.deepStrictEqual(M.POINTS,points);assert.equal(Object.keys(M.POINTS).length,10);
 assert(!Object.values(M.POINTS).includes(0x52b110));assert(!Object.values(M.POINTS).includes(0x52b1bb));assert(!Object.values(M.POINTS).includes(0x4b6d70));
 const s=fs.readFileSync(__dirname+'/quarter_placement_post_observer.js','utf8');assert(s.includes('spec.functions.length!==10'));assert(!s.includes("kind==='normalize'"));assert(!s.includes("kind==='normalize_bonus'"));
});
test('wrapper post decode uses preserved R12D raw/R14D yield and RSP70 output',()=>{
 const c=context('wrapper_normalize_post',-4,7);c.r13=reg(11);
 const a=M.decodePostPoint('wrapper_normalize_post',c,1,{add});assert.equal(a.rawInteger,-4);assert.equal(a.yieldIndex,7);assert.equal(a.expectedOutput,'0x800070');assert.equal(a.rax,'0x800070');
});
test('own post decode uses R14D and RBP40; raw staysnull',()=>{
 const c=context('own_normalize_post',999,3);c.r13=reg(11);const a=M.decodePostPoint('own_normalize_post',c,1,{add});assert.equal(a.rawInteger,null);assert.equal(a.yieldIndex,3);assert.equal(a.expectedOutput,'0x810040');
});
test('competing decode uses R13D BEFORE increment and RSP58; raw staysnull',()=>{
 const c=context('competing_normalize_post',999,5);c.r14=reg(11);const a=M.decodePostPoint('competing_normalize_post',c,1,{add});assert.equal(a.rawInteger,null);assert.equal(a.yieldIndex,5);assert.equal(a.expectedOutput,'0x800058');
});
for(const kind of Object.keys(M.POST_GROUPS)){
 test(kind+' validates local output pointer BEFORE reading',()=>{const x=setup(),a=M.decodePostPoint(kind,context(kind),1,x.io);a.rax='0xdeadbeef';const before=x.reads();x.o.point(kind,a);assert.equal(x.reads(),before);assert.equal(x.o.snapshot().stopReason,'post_output_pointer');assert.equal(x.o.status().enabled,false);});
 test(kind+' validates yield bound BEFORE reading',()=>{const x=setup(),a=M.decodePostPoint(kind,context(kind,4,12),1,x.io);const before=x.reads();x.o.point(kind,a);assert.equal(x.reads(),before);assert.equal(x.o.snapshot().stopReason,'yield_index');});
}
test('wrapper preserves DIRECT raw and normalized; optional coefficient only INFERRED',()=>{
 const x=setup();x.post('wrapper_normalize_post',1280);const n=x.frame.normalizations[0];assert.equal(n.rawInteger,4);assert.equal(n.rawStatus,'DIRECT_PRESERVED_REGISTER');assert.equal(n.rawInputQ8,null);assert.equal(n.normalizedQ8,1280);assert.equal(n.normalizedStatus,'DIRECT_OUTPUT_POINTER');assert.equal(n.effectiveBonusQ8,null);assert.equal(n.privateBiasInference.status,'INFERRED_CONDITIONAL');assert.equal(n.privateBiasInference.cappedPrivateBonusQ8,64);assert.equal(n.privateBiasInference.uncappedBonusQ8,null);assert.equal(n.privateBiasInference.noOverflowUniversallyProven,false);
});
test('own and competing never reconstruct raw or carry wrapper inference',()=>{
 const x=setup();x.post('wrapper_normalize_post',1280);
 for(const kind of ['own_normalize_post','competing_normalize_post'])x.post(kind,1280,999);
 for(const n of x.frame.normalizations.slice(1)){assert.equal(n.rawInteger,null);assert.equal(n.rawInputQ8,null);assert.equal(n.rawStatus,'UNOBSERVED_MUTATED_INPUT');assert.equal(n.normalizedQ8,1280);assert.equal(n.privateBiasInference.status,'UNOBSERVED');assert.equal(n.privateBiasInference.cappedPrivateBonusQ8,null);assert.equal(n.effectiveBonusQ8,null);}
});
test('real yield normalized outputs retained with no private inference',()=>{const x=setup();x.post('wrapper_normalize_post',1308,4,1);assert.equal(x.frame.normalizations[0].normalizedQ8,1308);assert.equal(x.frame.normalizations[0].privateBiasInference.reason,'not_private_wrapper');});
test('zero/unowned-wrapper compatible raw gives no invented coefficient',()=>{const x=setup();x.post('wrapper_normalize_post',0,0);assert.equal(x.frame.normalizations[0].privateBiasInference.reason,'zero_or_unknown_raw');assert.equal(x.frame.normalizations[0].privateBiasInference.cappedPrivateBonusQ8,null);});
test('inference exact integer factor/negative raw/cap cases',()=>{
 for(const[raw,out,want]of[[4,1280,64],[-4,-1280,64],[1,2560,2304],[3,0,-256]]){const r=M.inferPrivateBias(cfg,'wrapper',7,raw,out);assert.equal(r.status,'INFERRED_CONDITIONAL');assert.equal(r.cappedPrivateBonusQ8,want);assert.equal(r.uncappedBonusQ8,null);}
});
test('inference declines rounding/shiftwrap/negativefactor/outofcap/unknown/default mismatch',()=>{
 for(const[conf,group,index,raw,out,why]of[
  [cfg,'wrapper',7,3,1000,'nonintegral_factor'],
  [cfg,'wrapper',7,8388608,1073741824,'raw_shift_may_overflow'],
  [cfg,'wrapper',7,1,-1,'factor_outside_inference_bounds'],
  [cfg,'wrapper',7,1,2561,'factor_outside_inference_bounds'],
  [cfg,'wrapper',7,null,0,'zero_or_unknown_raw'],
  [cfg,'wrapper',7,1,NaN,'invalid_normalized'],
  [Object.assign({},cfg,{privateYieldDefaultValue:0.5}),'wrapper',7,4,1280,'default_not_one'],
  [cfg,'own_static',7,4,1280,'not_private_wrapper']
 ]){const r=M.inferPrivateBias(conf,group,index,raw,out);assert.equal(r.status,'UNOBSERVED');assert.equal(r.reason,why);assert.equal(r.cappedPrivateBonusQ8,null);}
});
test('prevalidatedDefault1 required; legacy profile rejected',()=>{assert.throws(()=>M.configValid(Object.assign({},cfg,{privateYieldDefaultValue:undefined})));assert.throws(()=>M.configValid(Object.assign({},cfg,{profile:'quarter-placement-v1'})));});
test('wrong thread has no output reads and no correlation',()=>{const x=setup(),a=M.decodePostPoint('wrapper_normalize_post',context('wrapper_normalize_post'),2,x.io),before=x.reads();x.o.point('wrapper_normalize_post',a);assert.equal(x.reads(),before);assert.equal(x.frame.normalizations.length,0);});
test('unreadable direct output is fatal without fabrication',()=>{const x=setup(),a=M.decodePostPoint('wrapper_normalize_post',context('wrapper_normalize_post'),1,x.io);x.o.point('wrapper_normalize_post',a);assert.equal(x.o.status().enabled,false);assert.equal(x.frame.normalizations.length,0);});
test('512record bound checked before post output read',()=>{const x=setup();x.frame.normalizations.length=512;const before=x.reads();x.o.point('wrapper_normalize_post',M.decodePostPoint('wrapper_normalize_post',context('wrapper_normalize_post'),1,x.io));assert.equal(x.reads(),before);assert.equal(x.o.snapshot().stopReason,'normalization_frame_bound');});
test('freeze leaves post listeners inert',()=>{const x=setup();x.o.freeze();const before=x.reads();x.post('wrapper_normalize_post',1280);assert.equal(x.reads(),before);assert.equal(x.frame.normalizations.length,0);});
console.log(checks+' focused postsite checks passed');

