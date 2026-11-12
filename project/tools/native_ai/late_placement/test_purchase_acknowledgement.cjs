// Synthetic gate/dispatch checks. These do not prove native ABI or foundation;
// independent disassembly, live paired evidence and physical snapshots do that.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
function scenario(mode='normal') {
    const cells=new Map(),calls=[],fingerprints=[];
    const contract=0x10000,city=0x20000,game=0x30000,map=0x40000,plot=0x50000,attributes=0x60000;
    let nextScratch=0x200000;
    class Pointer {
        constructor(value){this.value=Number(value);}
        toString(){return String(this.value);}
        add(n){return new Pointer(this.value+n);}
        isNull(){return this.value===0;}
        writeS32(value){
            assert(this.value>=0x200000,'Only scratch may be directly written');
            cells.set(this.value,value);
        }
    }
    const ptr=value=>new Pointer(value),put=(p,o,v)=>cells.set(p+o,v);
    const read=(p,o,type)=>{
        // Enforce the real adapter vocabulary; ignoring type let unsupported
        // i8 pass the first fixture and fail before mutation in the live probe.
        if(type!==undefined)assert(['ptr','i32','u8'].includes(type),'Unsupported adapter type');
        assert(cells.has(Number(p)+o),'Unmapped fixture read');const value=cells.get(Number(p)+o);
        if(type==='u8')assert(value>=0&&value<=255,'Unsigned byte out of range');
        return value;
    };
    put(0,0xb8aa68,game);put(game,0x248,map);put(city,0xd8,3);put(city,0xa8,458758);
    put(contract,0xb0,3);put(plot,0x28,(10<<16)|48);put(attributes,0x1c,3);put(attributes,0xc,458758);
    const context={ptr,Memory:{alloc(size){const result=ptr(nextScratch);nextScratch+=size;return result;}},
        NativeFunction:function(address,result,args,options){
            const rva=Number(address);
            return(...values)=>{
                if(rva===0x52d00){
                    assert.equal(result,'pointer');assert.equal(args.length,2);
                    assert.equal(Number(values[0]),map);
                    assert.equal(read(values[1],0),48);assert.equal(read(values[1],4),10);
                    calls.push('map');return ptr(mode==='null-plot'?0:plot);
                }
                if(rva===0x5f090){
                    assert.equal(Number(values[0]),plot);calls.push('attributes');
                    if(mode==='state-changed')put(contract,0xb0,5);
                    return ptr(mode==='null-attributes'?0:attributes);
                }
                assert.equal(rva,0x64a6d0);assert.equal(result,'void');
                assert.equal(options.abi,'win64');assert.equal(options.scheduling,'exclusive');
                assert.equal(Number(values[0]),contract+0xa0);assert.equal(read(values[1],0),7);
                calls.push('tracked-assignment');
                if(mode!=='setter-failed')put(contract,0xb0,7);
            };
        }};
    vm.createContext(context);vm.runInContext(fs.readFileSync(__dirname+'/purchase_acknowledgement.js','utf8'),context);
    const scope={player:3,city:458758,plots:[788],repairOwnedPurchase:true,
        observeLifecycle:true,observeExecution:true,observeLineage:true};
    const acknowledgement=context.createPurchasedContractAcknowledgement({core:{base:ptr(0)},scope,read,
        fingerprint:(...args)=>fingerprints.push(args)});
    assert.deepEqual(fingerprints.map(r=>r[0]),[0x52d00,0x5f090,0x4c210,0x64a6d0]);
    const binding={contractId:4316,ownerControl:59375659,rootTreeId:59244585,
        originCity:458758,originCityPointer:String(city),plot:788,x:48,y:10};
    const state={contractStatus:3,contractVtableRva:0x9fa930,executeRva:0x3f82c0,updateRva:0x3fa260,eligibilityRva:0x3fa880};
    const payment={player:3,city:458758,plot:788,turn:203,deltaMatched:true,deltaQ8:-10240,measuredDeltaQ8:-10240,
        contractId:4316,contractPointer:String(contract),ownerControl:59375659,rootTreeId:59244585};
    if(mode==='no-payment')payment.deltaMatched=false;
    if(mode==='wrong-payment-city')payment.city=1;
    if(mode==='wrong-payment-delta')payment.measuredDeltaQ8=-10239;
    if(mode==='wrong-payment-contract')payment.contractId=4317;
    if(mode==='wrong-payment-pointer')payment.contractPointer=String(contract+1);
    if(mode==='wrong-payment-control')payment.ownerControl++;
    if(mode==='wrong-payment-tree')payment.rootTreeId++;
    if(mode==='unknown-city')binding.originCity=null;
    if(mode==='unknown-pointer')binding.originCityPointer=null;
    if(mode==='executing')state.contractStatus=5;
    if(mode==='foreign-owner')put(attributes,0x1c,2);
    if(mode==='unowned')put(attributes,0x1c,255);
    if(mode==='null-game')put(0,0xb8aa68,0);
    if(mode==='null-map')put(game,0x248,0);
    if(mode==='wrong-purchase-city')put(attributes,0xc,1);
    if(mode==='wrong-coordinates')put(plot,0x28,(10<<16)|49);
    if(mode==='city-changed')put(city,0xa8,1);
    if(mode==='dispatch-changed')state.updateRva=0x123456;
    acknowledgement.observeDebit(payment);
    const beforeWrite=()=>{if(mode==='journal-full')throw Error('Journal capacity');calls.push('journal');};
    let outcome,error;
    try {outcome=acknowledgement.tryAcknowledge(ptr(contract),binding,state,mode==='stale-payment'?206:203,
        mode==='no-journal'?undefined:beforeWrite);}
    catch(e){error=String(e);}
    if(mode==='normal'){
        assert.equal(acknowledgement.tryAcknowledge(ptr(contract),binding,state,204),null);
    }
    return {outcome,error,calls,status:read(ptr(contract),0xb0)};
}
let r=scenario();assert.equal(r.error,undefined);assert.equal(r.outcome.acknowledged,true);
assert.equal(r.outcome.before,3);assert.equal(r.outcome.after,7);assert.equal(r.outcome.measuredPaymentQ8,-10240);
assert.deepEqual(r.calls,['map','attributes','journal','tracked-assignment']);assert.equal(r.status,7);
for(const mode of ['no-payment','wrong-payment-city','wrong-payment-delta','wrong-payment-contract','wrong-payment-pointer',
    'wrong-payment-control','wrong-payment-tree','unknown-city','unknown-pointer','executing','stale-payment']){
    r=scenario(mode);assert.equal(r.error,undefined,mode);assert.equal(r.outcome,null,mode);
    assert.deepEqual(r.calls,[],mode);assert.equal(r.status,3,mode);
}
for(const mode of ['foreign-owner','unowned','wrong-purchase-city','null-plot','null-attributes','null-game','null-map']){
    r=scenario(mode);assert.equal(r.error,undefined,mode);assert.equal(r.outcome.acknowledged,false,mode);
    assert(!r.calls.includes('tracked-assignment'),mode);assert.equal(r.status,3,mode);
}
for(const [mode,pattern]of [['wrong-coordinates',/coordinates differ/],['city-changed',/city identity changed/],
    ['dispatch-changed',/dispatch differs/],['state-changed',/state changed before/],
    ['no-journal',/reserved write journal/],['journal-full',/Journal capacity/]]){
    r=scenario(mode);assert.match(r.error,pattern,mode);assert(!r.calls.includes('tracked-assignment'),mode);
}
r=scenario('setter-failed');assert.match(r.error,/did not land/);assert.equal(r.outcome,undefined);
console.log('Purchase acknowledgement gates: paired payment, fresh owner/city, dispatch, tracked setter and deduplication passed');
