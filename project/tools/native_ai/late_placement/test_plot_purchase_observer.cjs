// Synthetic register/memory fixtures validate diagnostic decoding and filters.
// They cannot establish the native ABI; Ghidra and live receipts do that.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const cells = new Map();
const hooks = new Map();
const streamed = [];
const instructions = new Map([
    [0x681346, '8bf085c00f8eca000000'],
    [0x681379, 'e8621fccff8b4567488d8f800b0000'],
    [0x6813a2, '0fb787d80000004c8d4567'],
    [0x71c63e, '8bd885c00f8e27020000'],
    [0x71c671, 'e86a6cc2ff8b4538488d8f800b0000'],
    [0x71c69a, '0fb787d80000004c8d4538'],
    [0x459169, '85c07e104d85f67405'],
    [0x45918f, '488bac24d0000000418bdfc1e308'],
    [0x459095, '48894c2408'],
    [0x4590a5, '4881ec80000000488be9'],
    [0x3e10fd, '488d8b70020000440fb64540'],
    [0x55dc9f, '488bd0488d4c2430e834f8e9ff'],
    [0x3e0f37, 'e8143b0000'],
    [0x3e0f29, 'c74540f1d8ffffc74544f1d8ffff'],
    [0x4591f3, '84c00f84ca000000'],
    [0x45921f, '84c00f849e000000'],
    [0x459241, '418bc5488d9424c0000000'],
    [0x11b100, '405556415441564157'],
    [0x616a0, '448944241889542410'],
    [0x457515,'84c074094883c310'],
    [0x45755f,'84c0740f488bcb488bd7'],
    [0x55a056,'8b88b000000083f905'],
]);
class Pointer {
    constructor(value) { this.value = Number(value); }
    add(offset) { return new Pointer(this.value + offset); }
    toString() { return String(this.value); }
    toInt32() { return this.value | 0; }
    isNull() { return this.value === 0; }
    readByteArray(size) {
        const bytes = Buffer.from(instructions.get(this.value) || '', 'hex');
        assert.equal(bytes.length, size);
        return Uint8Array.from(bytes).buffer;
    }
}
const ptr = value => new Pointer(value);
const put = (base, offset, value) => cells.set(base + offset, value);
const context = {rpc: {exports: {}}, ptr, send: message => streamed.push(message), Process: {
    platform: 'windows', arch: 'x64',
    enumerateModules: () => [{path: 'pinned.dll', size: 123, base: ptr(0)}],
    findRangeByAddress: () => { throw Error('Unexpected direct range read'); },
}, createStudyMemoryIO: () => ({read(base, offset, type) {
    const address = Number(base) + offset;
    if (!cells.has(address)) return {error: 'Unmapped synthetic address'};
    const value = cells.get(address);
    return {value: type === 'ptr' ? String(value) : value};
}}), Interceptor: {
    attach(address, callback) {
        hooks.set(address.value, callback);
        return {detach() { hooks.delete(address.value); }};
    }, flush() {},
}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(__dirname + '/plot_purchase_observer.js', 'utf8'), context);
assert(context.rpc.exports.init({path: 'pinned.dll', image_size: 123},
    {player: 1, width: 74, height: 46, plots: [401], allCommandPlots: true, streamRecords: true}));
const city = 0x10000, xy = 0x20000, frame = 0x30000, stack = 0x40000;
const slushFund = 0x50000, plotFund = slushFund + 8, game = 0x60000, debit = 0x70000;
const economic = 0x80000, player = 0x90000, treasury = 0xa0000, weights = 0xb0000;
put(stack, 0xc0, economic); put(economic, 0x98, player);
put(economic, 0x120, 128000); put(economic, 0x250, slushFund);
put(economic, 0x1e0, weights); put(economic, 0x1f0, 4); put(economic, 0x1c8, 9);
put(player, 0x780, treasury); put(treasury, 0xa8, 130560);
[3,4,1,1].forEach((weight,i) => put(weights, i*4, weight));
put(slushFund, 4, 8000); put(slushFund, 12, 12000);
put(city, 0xd8, 1); put(city, 0xa8, 524295);
put(xy, 0, 31); put(xy, 4, 5);
put(frame, 0x67, 31); put(frame, 0x6b, 5);
put(0, 0xb8aa68, game); put(game, 0xc0, 203);
put(stack, 0xd0, plotFund); put(stack, 0xd8, slushFund);
put(plotFund, 0, 6400); put(slushFund, 0, 19200); put(debit, 0, -25600);
const registers = {rbp: ptr(city), r12: ptr(xy), rax: ptr(100),
    r14: ptr(city), r15: ptr(100), rdi: ptr(64), rsp: ptr(stack)};
const fire = (site, overrides = {}, threadId = 7) => {
    const cpu={...registers,...overrides};
    hooks.get(site).call({context:cpu,threadId});
    return cpu;
};
fire(0x459169);
fire(0x45918f); // Exact equality passes both native savings comparisons.
put(plotFund, 0, 6399); put(slushFund, 0, 19201);
fire(0x45918f); // Enough combined Gold, insufficient earmarked plot fund.
put(plotFund, 0, 6400); put(slushFund, 0, 19199);
fire(0x45918f); // Plot fund passes, combined funds miss by one Q8 unit.
put(xy, 0, 30);
fire(0x459169); // Untargeted Economic quote is filtered.
put(city, 0xd8, 2);
fire(0x681346, {rdi: ptr(city), rbp: ptr(frame)}); // Foreign player filtered.
put(city, 0xd8, 1); put(frame, 0x67, 30);
const command = {rdi: ptr(city), rbp: ptr(frame), rsi: ptr(-25600), rdx: ptr(debit), rcx:ptr(treasury),r14:ptr(treasury)};
fire(0x681346, command); // Other own paid plot is a potential positive control.
fire(0x681379, command); put(treasury,0xa8,104960); fire(0x68137e, command); fire(0x6813a2, command);
const result = JSON.parse(JSON.stringify(context.rpc.exports.freeze()));
assert.equal(result.fault, null);
assert.equal(result.records.length, 8);
assert.equal(streamed.length, 8);
assert(streamed.every(m => m.kind === 'plot-purchase-receipt'));
assert.equal(result.records[0].gold, 100);
assert.deepEqual(result.records.slice(1, 4).map(r => [r.passesPlotFund, r.passesCombinedFunds]),
    [[true, true], [false, true], [true, false]]);
assert.equal(result.records[1].factorQ8, 64);
assert.equal(result.records[1].minimumPlotFundQ8, 6400);
assert.equal(result.records[1].treasuryQ8, 130560);
assert.equal(result.records[1].accountedQ8, 128000);
assert.equal(result.records[1].unaccountedQ8, 2560);
assert.deepEqual(result.records[1].savingsQ8, [19200,8000,6400,12000]);
assert.deepEqual(result.records[1].savingWeights, [3,4,1,1]);
assert.equal(result.records[1].totalWeight, 9);
assert.deepEqual(result.records.slice(4).map(r => r.kind),
    ['quote', 'debit-call', 'debit-return', 'annex-return']);
assert(result.records.slice(4).every(r => r.plot === 400 && r.city === 524295 && r.turn === 203));
assert.equal(result.records[5].deltaQ8, -25600);
assert.equal(result.records[6].deltaQ8, -25600);
assert.equal(result.records[5].treasuryBeforeQ8,130560);
assert.equal(result.records[6].treasuryBeforeQ8,130560);
assert.equal(result.records[6].treasuryAfterQ8,104960);
assert.equal(result.records[6].measuredDeltaQ8,-25600);
assert.equal(result.records[6].deltaMatched,true);
assert.equal(result.pendingDebits,0);
put(treasury,0xa8,130560);
assert.equal(hooks.size, 0);
// A stale receiver or incomplete read is a failed observation, not a valid
// zero balance. Freeze still detaches; later callbacks stay suppressed.
for (const [label, breakRead, restoreRead, pattern] of [
    ['receiver', () => put(economic,0x250,slushFund+4),
        () => put(economic,0x250,slushFund), /receiver\/fund layout/],
    ['Treasury', () => cells.delete(treasury+0xa8),
        () => put(treasury,0xa8,130560), /Unmapped synthetic address/],
    ['weights', () => put(economic,0x1c8,10),
        () => put(economic,0x1c8,9), /saving weights/],
]) {
    streamed.length=0;
    const isolated={...context,rpc:{exports:{}}};
    vm.createContext(isolated);
    vm.runInContext(fs.readFileSync(__dirname+'/plot_purchase_observer.js','utf8'),isolated);
    isolated.rpc.exports.init({path:'pinned.dll',image_size:123},
        {player:1,width:74,height:46,plots:[401],streamRecords:true});
    put(xy,0,31);
    breakRead();fire(0x45918f);restoreRead();
    fire(0x459169); // Valid input after the fault must not be counted.
    const failure=isolated.rpc.exports.freeze();
    assert.match(failure.fault,pattern,label);
    assert.equal(failure.records.length,0,label);
    assert.equal(streamed.length,1,label);
    assert.equal(streamed[0].kind,'plot-purchase-fault',label);
    assert.equal(hooks.size,0,label);
}
// Optional lineage joins exact tree creation to contract initialization,
// then matches the observed XY pointer at the attempt. No city/control-ID
// equality or arbitrary subtraction from an XY pointer is permitted.
streamed.length=0;
const lineageContext={...context,rpc:{exports:{}}};
vm.createContext(lineageContext);
vm.runInContext(fs.readFileSync(__dirname+'/plot_purchase_observer.js','utf8'),lineageContext);
lineageContext.rpc.exports.init({path:'pinned.dll',image_size:123},
    {player:1,city:524295,width:74,height:46,plots:[401],streamRecords:true,observeLineage:true});
const contract=0xc0000, root=0xd0000, child=0xd1000, build=0xe0000;
put(build,0x90,city);put(root,0x120,0);put(child,0x120,root);
put(root,0x1c8,91);put(root,0x1b0,4001);put(player,0xd8,1);
put(contract,0x110,4333);put(contract,0x128,4001);put(contract,0x140,1);
put(contract,0x178,31);put(contract,0x17c,5);
fire(0x3e10fd,{rdi:ptr(build),rbx:ptr(child),rsi:ptr(91)});
fire(0x55dc9f,{r15:ptr(contract),rsi:ptr(child),rbp:ptr(player)});
fire(0x45918f,{r12:ptr(contract+0x178)});
fire(0x45918f); // Same XY in another buffer has no known contract binding.
const unobservedContract=0xc1000, unobservedTree=0xd2000;
put(unobservedTree,0x120,0);put(unobservedTree,0x1c8,92);put(unobservedTree,0x1b0,4002);
put(unobservedContract,0x110,4334);put(unobservedContract,0x128,4002);put(unobservedContract,0x140,1);
put(unobservedContract,0x178,31);put(unobservedContract,0x17c,5);
fire(0x55dc9f,{r15:ptr(unobservedContract),rsi:ptr(unobservedTree),rbp:ptr(player)});
fire(0x45918f,{r12:ptr(unobservedContract+0x178)});
put(contract,0x110,4334);
fire(0x45918f,{r12:ptr(contract+0x178)});
fire(0x459169); // Suppressed after stale identity fault.
const lineage=lineageContext.rpc.exports.freeze();
assert.match(lineage.fault,/Retained purchase contract identity changed/);
assert.equal(lineage.records.length,6);
assert.equal(lineage.records[0].city,524295);
assert.equal(lineage.records[1].originCity,524295);
assert.equal(lineage.records[1].ownerControl,4001);
assert.equal(lineage.records[2].lineage.contractId,4333);
assert.equal(lineage.records[2].lineage.originCity,524295);
assert.equal(lineage.records[2].lineage.known,true);
assert.equal(lineage.records[3].lineage.known,false);
assert.equal(lineage.records[4].originCity,null);
assert.equal(lineage.records[5].lineage.known,true);
assert.equal(lineage.records[5].lineage.originCity,null);
assert.equal(streamed.length,7);
assert.equal(streamed[6].kind,'plot-purchase-fault');
assert.equal(hooks.size,0);

function buyerPrototype(options={}) {
    streamed.length=0;
    const isolated={...context,rpc:{exports:{}}};
    vm.createContext(isolated);
    vm.runInContext(fs.readFileSync(__dirname+'/plot_purchase_observer.js','utf8'),isolated);
    isolated.rpc.exports.init({path:'pinned.dll',image_size:123},
        {player:2,city:589829,district:37,width:74,height:46,plots:[1365],
            streamRecords:true,observeLineage:true,prototypeBuyer:options.mode||'restrict',
            selectorObserverVerified:true});
    const other=0xf0000, alternateBuild=0xe1000;
    put(city,0xd8,2);put(city,0xa8,options.otherOrigin?524292:589829);
    put(other,0xd8,2);put(other,0xa8,524292);
    put(player,0xd8,2);put(build,0x90,city);put(alternateBuild,0x90,city);
    put(root,0x120,0);put(root,0x1c8,91);put(root,0x1b0,4001);
    put(child,0x120,root);
    put(contract,0x110,4333);put(contract,0x128,4001);put(contract,0x140,2);
    put(contract,0x178,33);put(contract,0x17c,18);
    put(xy,0,33);put(xy,4,18);
    const plot=options.selectedPlot===undefined?1365:options.selectedPlot;
    put(frame,0x40,plot%74);put(frame,0x44,Math.floor(plot/74));
    if (!options.noSelection) {
        fire(0x3e0f3c,{rdi:ptr(build),rbp:ptr(frame),rax:ptr(options.district===undefined?37:options.district)});
        if (options.failedAfterMatch)
            fire(0x3e0f3c,{rdi:ptr(build),rbp:ptr(frame),rax:ptr(-1)});
        if (options.replacedAfterMatch)
            fire(0x3e0f3c,{rdi:ptr(build),rbp:ptr(frame),rax:ptr(6)});
        if (options.otherSelectorAfterMatch) {
            put(alternateBuild,0x90,other);
            fire(0x3e0f3c,{rdi:ptr(alternateBuild),rbp:ptr(frame+512),rax:ptr(37)});
            put(alternateBuild,0x90,city);
        }
    }
    fire(0x3e10fd,{rdi:ptr(options.otherBuild?alternateBuild:build),
        rbp:ptr(options.otherFrame?frame+256:frame),rbx:ptr(child),rsi:ptr(91)},options.otherThread?8:7);
    fire(0x55dc9f,{r15:ptr(contract),rsi:ptr(child),rbp:ptr(player)});
    if (options.staleContract) put(contract,0x110,4334);
    if (options.staleControl) put(contract,0x128,4002);
    if (options.stalePlayer) put(contract,0x140,3);
    if (options.staleTarget) put(contract,0x178,32);
    if (options.fillCapacity) {
        const remaining=512-streamed.length;
        for(let i=0;i<remaining;i++)
            fire(0x459169,{rbp:ptr(city),r12:ptr(contract+0x178),rax:ptr(85)});
    }
    const original=options.gold===undefined?85:options.gold;
    const cpu=fire(0x459169,{rbp:ptr(options.intendedBuyer?city:other),
        r12:ptr(options.unknownPointer?xy:contract+0x178),rax:ptr(original)});
    const result=JSON.parse(JSON.stringify(isolated.rpc.exports.freeze()));
    assert.equal(hooks.size,0);
    return {cpu,result};
}
let probe=buyerPrototype();
assert.equal(probe.result.fault,null);
assert.equal(probe.cpu.rax.toInt32(),-1);
assert.equal(probe.result.records.at(-1).originalGold,85);
assert.equal(probe.result.records.at(-1).excluded,true);
assert.equal(probe.result.records.at(-1).requiredBuyer,589829);
for(const options of [{mode:'observe'},{intendedBuyer:true},{gold:-1},{gold:0},
        {district:36},{selectedPlot:1364},{noSelection:true},{otherOrigin:true},
        {failedAfterMatch:true},{replacedAfterMatch:true},{otherFrame:true},
        {otherBuild:true},{otherThread:true},{unknownPointer:true},{otherSelectorAfterMatch:true}]) {
    probe=buyerPrototype(options);
    assert.equal(probe.result.fault,null,JSON.stringify(options));
    assert.equal(probe.cpu.rax.toInt32(),options.gold===undefined?85:options.gold,JSON.stringify(options));
    assert.equal(probe.result.records.at(-1).excluded,false,JSON.stringify(options));
}
for(const [options,pattern] of [[{staleContract:true},/identity changed/],
        [{staleControl:true},/identity changed/],[{stalePlayer:true},/identity changed/],
        [{fillCapacity:true},/trace capacity/]]) {
    probe=buyerPrototype(options);
    assert.match(probe.result.fault,pattern);
    assert.equal(probe.cpu.rax.toInt32(),85); // Failure precedes the native write.
    assert(probe.result.records.every(row=>!row.excluded));
}
// A changed target outside the explicit prototype scope is ignored before
// any binding is used. It must not authorize a write or fabricate a receipt.
probe=buyerPrototype({staleTarget:true});
assert.equal(probe.result.fault,null);
assert.equal(probe.cpu.rax.toInt32(),85);
assert(probe.result.records.every(row=>!row.excluded));
// Actual Treasury measurements are distinct from the preserved debit argument.
// Pair threads/stacks without inventing success for an incomplete/mismatched
// callback. Interleaving may include another synchronous debit in the interval;
// keep its measured mismatch rather than silently attributing only our delta.
function debitCase(mode,handler='base') {
    const fresh={...context,rpc:{exports:{}}};vm.createContext(fresh);
    vm.runInContext(fs.readFileSync(__dirname+'/plot_purchase_observer.js','utf8'),fresh);
    fresh.rpc.exports.init({path:'pinned.dll',image_size:123},
        {player:1,width:74,height:46,plots:[401],allCommandPlots:true});
    put(city,0xd8,1);put(city,0xa8,524295);put(frame,0x67,30);put(frame,0x6b,5);
    put(game,0xc0,203);put(treasury,0xa8,130560);
    const xp1=handler==='xp1',call=xp1?0x71c671:0x681379,returnedSite=xp1?0x71c676:0x68137e;
    const treasuryRegister=xp1?'r15':'r14',deltaRegister=xp1?'rbx':'rsi';
    const nativeCommand={...command,[treasuryRegister]:ptr(treasury),[deltaRegister]:ptr(-25600)};
    put(frame,0x38,30);put(frame,0x3c,5);
    if(mode==='missing-thread')hooks.get(call).call({context:{...registers,...nativeCommand}});
    else if(mode==='wrong-receiver')fire(call,{...nativeCommand,[treasuryRegister]:ptr(treasury+4096)});
    else {
        fire(call,nativeCommand);
        if(mode==='duplicate')fire(call,nativeCommand);
        else if(mode==='capacity')for(let thread=8;thread<=39;thread++)fire(call,nativeCommand,thread);
        else if(mode==='interleaved') {
            fire(call,nativeCommand,8);put(treasury,0xa8,104960);fire(returnedSite,nativeCommand,8);
            put(treasury,0xa8,79360);fire(returnedSite,nativeCommand,7);
        } else if(mode!=='missing-return') {
            put(treasury,0xa8,104960);
            const returned={...nativeCommand};let thread=7;
            if(mode==='wrong-thread')thread=8;
            if(mode==='wrong-stack')returned.rsp=ptr(stack+8);
            if(mode==='wrong-treasury')returned[treasuryRegister]=ptr(treasury+4096);
            if(mode==='wrong-argument')returned[deltaRegister]=ptr(-25599);
            if(mode==='wrong-city-pointer') {
                put(city+4096,0xd8,1);put(city+4096,0xa8,524295);returned.rdi=ptr(city+4096);
            }
            fire(mode==='cross-handler'?(xp1?0x68137e:0x71c676):returnedSite,returned,thread);
        }
    }
    return JSON.parse(JSON.stringify(fresh.rpc.exports.freeze()));
}
let debits=debitCase('normal');assert.equal(debits.fault,null);assert.equal(debits.pendingDebits,0);
assert.equal(debits.records[1].measuredDeltaQ8,-25600);assert.equal(debits.records[1].deltaMatched,true);
assert.equal(debits.records[0].threadId,7);assert.equal(debits.records[1].callerStack,String(stack));
debits=debitCase('interleaved');assert.equal(debits.fault,null);assert.equal(debits.pendingDebits,0);
assert.deepEqual(debits.records.filter(r=>r.kind==='debit-return').map(r=>[r.threadId,r.measuredDeltaQ8,r.deltaMatched]),
    [[8,-25600,true],[7,-51200,false]]);
for(const [mode,pattern]of [['missing-return',/Unreturned/],['wrong-thread',/Unmatched/],
        ['wrong-stack',/Unmatched/],['wrong-treasury',/Unmatched/],['wrong-argument',/Unmatched/],
        ['wrong-city-pointer',/Unmatched/],['missing-thread',/Ambiguous/],
        ['wrong-receiver',/receiver differs/],['duplicate',/Ambiguous/],['capacity',/excessive/]]) {
    debits=debitCase(mode);assert.match(debits.fault,pattern,mode);
    assert(debits.records.every(r=>r.kind!=='debit-return'),mode);
}
// Same decoding/failure contract for the expansion handler that the live game
// actually dispatched. Its own frame/register layout must not borrow the base
// handler's values. Cross-handler returns never complete a pending payment.
debits=debitCase('normal','xp1');assert.equal(debits.fault,null);
assert.equal(debits.records[1].handler,'xp1');assert.equal(debits.records[1].measuredDeltaQ8,-25600);
assert.equal(debits.records[1].deltaMatched,true);
for(const mode of ['missing-return','wrong-thread','wrong-stack','wrong-treasury','wrong-argument',
    'wrong-city-pointer','missing-thread','wrong-receiver','duplicate','capacity','cross-handler']) {
    debits=debitCase(mode,'xp1');assert(debits.fault,mode);
    assert(debits.records.every(r=>r.kind!=='debit-return'),mode);
}
// Verify positive whole-Gold quote and matching annex use XP1's XY slots.
{
    const fresh={...context,rpc:{exports:{}}};vm.createContext(fresh);
    vm.runInContext(fs.readFileSync(__dirname+'/plot_purchase_observer.js','utf8'),fresh);
    fresh.rpc.exports.init({path:'pinned.dll',image_size:123},{player:1,width:74,height:46,plots:[401]});
    put(frame,0x38,31);put(frame,0x3c,5);put(frame,0x67,30);put(frame,0x6b,5);
    fire(0x71c63e,{rdi:ptr(city),rbp:ptr(frame),rax:ptr(40)});
    fire(0x71c69a,{rdi:ptr(city),rbp:ptr(frame)});
    const xp=fresh.rpc.exports.freeze();assert.equal(xp.fault,null);
    assert.equal(xp.records.length,2);assert.equal(xp.records[0].gold,40);
    assert(xp.records.every(r=>r.handler==='xp1'&&r.plot===401));
}
function executionCase(mode) {
    const fresh={...context,rpc:{exports:{}},Process:{...context.Process,
        enumerateModules:()=>[{path:'pinned.dll',size:0x1000000,base:ptr(0)}]}};
    vm.createContext(fresh);vm.runInContext(fs.readFileSync(__dirname+'/plot_purchase_observer.js','utf8'),fresh);
    fresh.rpc.exports.init({path:'pinned.dll',image_size:0x1000000},
        {player:1,width:74,height:46,plots:[401],observeExecution:true});
    put(city,0xd8,1);put(city,0xa8,524295);put(game,0xc0,203);
    put(xy,0,31);put(xy,4,5);put(player,0xd8,1);put(player,0x288,1);
    const culture=0x100000,plotInstance=0x110000;
    put(culture,0,city);put(plotInstance,0x28,(5<<16)|31);
    if(mode==='bad-economic-player')put(player,0xd8,2);
    fire(0x4591f3,{r14:ptr(city),rax:ptr(1)});
    if(mode==='denied') {
        put(player,0x288,0);fire(0x45921f,{r14:ptr(city),rax:ptr(256)}); // AL0 despite nonzeroRAX.
    }else if(mode!=='bad-economic-player') {
        fire(0x45921f,{r14:ptr(city),rax:ptr(1)});
        fire(0x459241,{r14:ptr(city),rax:ptr(0)}); // Return is not a successBoolean.
    }
    const annex={context:{rcx:ptr(culture),rdx:ptr(xy)},returnAddress:ptr(mode==='outside-caller'?0x2000000:0x6813a2)};
    const owner={context:{rcx:ptr(plotInstance),rdx:ptr(1),r8:ptr(524295)},returnAddress:ptr(0x4c63a)};
    hooks.get(0x11b100).onEnter.call(annex);
    if(mode!=='missing-annex-return')hooks.get(0x11b100).onLeave.call(annex);
    hooks.get(0x616a0).onEnter.call(owner);hooks.get(0x616a0).onLeave.call(owner);
    return JSON.parse(JSON.stringify(fresh.rpc.exports.freeze()));
}
let execution=executionCase('normal');assert.equal(execution.fault,null);assert.equal(execution.pendingExecutions,0);
assert.deepEqual(execution.records.map(r=>r.kind),['targeted-request-built','targeted-command-checked',
    'targeted-command-returned','culture-annex-return','plot-set-owner-return']);
assert.equal(execution.records[0].requestBuilt,true);assert.equal(execution.records[1].commandAdmitted,true);
assert.equal(execution.records[2].managerStartReturned,true);assert(!('success'in execution.records[2]));
assert.equal(execution.records[3].callerRva,0x6813a2);assert.equal(execution.records[4].requestedCity,524295);
assert(execution.records.every(r=>!['quote','debit-call','debit-return'].includes(r.kind)));
execution=executionCase('denied');assert.equal(execution.fault,null);
assert.equal(execution.records[1].commandAdmitted,false);assert.equal(execution.records[1].playerTurnActive,false);
execution=executionCase('outside-caller');assert.equal(execution.fault,null);
assert.equal(execution.records.find(r=>r.kind==='culture-annex-return').callerRva,null);
execution=executionCase('missing-annex-return');assert.match(execution.fault,/Unreturned observed execution/);
assert.equal(execution.pendingExecutions,1);assert(!execution.records.some(r=>r.kind==='culture-annex-return'));
execution=executionCase('bad-economic-player');assert.match(execution.fault,/Execution Economic player differs/);
// Lifecycle receipts require a freshly observed contract, revalidate identity
// and record actual dispatch instead of assuming the base class. AL describes
// eligibility only; no completion or successful removal field is synthesized.
function lifecycleCase(mode) {
    const acknowledgementMode=mode.startsWith('ack-journal');let writeAttempts=0;
    const fresh={...context,rpc:{exports:{}},Process:{...context.Process,
        enumerateModules:()=>[{path:'pinned.dll',size:0x1000000,base:ptr(0)}]}};
    if(acknowledgementMode)fresh.createPurchasedContractAcknowledgement=()=>({observeDebit(){},
        tryAcknowledge(contract,binding,state,turn,beforeWrite){
            beforeWrite();++writeAttempts;
            if(mode==='ack-journal-race')fire(0x459169); // Cannot take the reserved outcome slot.
            return {acknowledged:true,before:3,after:7};
        }});
    vm.createContext(fresh);vm.runInContext(fs.readFileSync(__dirname+'/plot_purchase_observer.js','utf8'),fresh);
    fresh.rpc.exports.init({path:'pinned.dll',image_size:0x1000000},
        {player:1,city:524295,district:36,width:74,height:46,plots:[401],observeLineage:true,
            observeLifecycle:true,observeExecution:mode==='payment-binding',repairOwnedPurchase:acknowledgementMode,
            streamRecords:acknowledgementMode});
    put(city,0xd8,1);put(city,0xa8,524295);put(build,0x90,city);
    put(root,0x120,0);put(child,0x120,root);put(root,0x1c8,91);put(root,0x1b0,4001);
    put(contract,0x110,4333);put(contract,0x128,4001);put(contract,0x140,1);
    put(contract,0x178,31);put(contract,0x17c,5);put(contract,0xb0,0);
    put(contract,0,0x9fa930);put(0x9fa930,0x20,0x3f82c0);
    put(0x9fa930,0x50,0x3fa260);put(0x9fa930,0x80,0x3fa880);
    put(player,0xd8,1);put(economic,0x98,player);
    put(player,0x288,1);put(xy,0,31);put(xy,4,5);
    const treePlot=0x130000;put(treePlot,0x28,(5<<16)|31);
    put(child,0x2f0,city);put(child,0x308,treePlot);put(child,0x29c,36);
    const handle=0x120000;put(handle,0,contract);
    fire(0x3e10fd,{rdi:ptr(build),rbx:ptr(child),rsi:ptr(91)});
    fire(0x55dc9f,{r15:ptr(contract),rsi:ptr(child),rbp:ptr(player)});
    put(contract,0xb0,3);
    if(mode==='stale')put(contract,0x110,4334);
    if(mode==='unknown')put(handle,0,contract+4096);
    if(acknowledgementMode) {
        const limit=mode==='ack-journal-full'?509:508;
        for(let count=streamed.length;count<limit;count++)fire(0x459169);
        fire(0x55a056,{rax:ptr(contract),r14:ptr(child)});
        return {...JSON.parse(JSON.stringify(fresh.rpc.exports.freeze())),writeAttempts};
    }
    if(mode==='payment-binding') {
        fire(0x45921f,{r14:ptr(city),r12:ptr(contract+0x178),rax:ptr(1)});
        put(frame,0x67,31);put(frame,0x6b,5);put(treasury,0xa8,130560);
        fire(0x681379,command);put(treasury,0xa8,104960);fire(0x68137e,command);
        fire(0x459241,{r14:ptr(city),r12:ptr(contract+0x178)});
        return JSON.parse(JSON.stringify(fresh.rpc.exports.freeze()));
    }
    fire(0x457515,{r15:ptr(economic),rbx:ptr(handle),rax:ptr(1)});
    fire(0x45755f,{r15:ptr(economic),rdi:ptr(handle),rax:ptr(256)}); // ALfalse.
    fire(0x55a056,{rax:ptr(mode==='unknown'?contract+4096:contract)});
    return JSON.parse(JSON.stringify(fresh.rpc.exports.freeze()));
}
let lifecycle=lifecycleCase('normal');assert.equal(lifecycle.fault,null);
assert.deepEqual(lifecycle.records.map(r=>r.kind),['district-tree-created','purchase-contract-created',
    'purchase-economic-eligibility','purchase-economic-eligibility','purchase-decorator-status']);
assert.equal(lifecycle.records[1].contractStatus,0);
assert.equal(lifecycle.records[2].eligible,true);assert.equal(lifecycle.records[3].eligible,false);
assert(lifecycle.records.slice(2).every(r=>r.contractStatus===3&&r.contractVtableRva===0x9fa930&&
    r.executeRva===0x3f82c0&&r.updateRva===0x3fa260&&r.eligibilityRva===0x3fa880));
assert(lifecycle.records.every(r=>!('removed'in r)&&!('completed'in r)));
lifecycle=lifecycleCase('unknown');assert.equal(lifecycle.fault,null);assert.equal(lifecycle.records.length,2);
lifecycle=lifecycleCase('stale');assert.match(lifecycle.fault,/identity changed/);
assert.equal(lifecycle.records.length,2);
lifecycle=lifecycleCase('payment-binding');assert.equal(lifecycle.fault,null);
let linked=lifecycle.records.find(r=>r.kind==='debit-return');assert.equal(linked.contractId,4333);
assert.equal(linked.contractPointer,String(contract));assert.equal(linked.ownerControl,4001);
assert.equal(linked.rootTreeId,91);assert.equal(lifecycle.pendingCommands,0);
for(const mode of ['ack-journal-full','ack-journal-exact','ack-journal-race']) {
    streamed.length=0;lifecycle=lifecycleCase(mode);assert.equal(lifecycle.pendingAcknowledgements,0,mode);
    if(mode==='ack-journal-full'){
        assert.match(lifecycle.fault,/journal capacity/);assert.equal(lifecycle.writeAttempts,0);
        assert(!lifecycle.records.some(r=>r.kind==='purchase-acknowledgement-intent'));
    }else{
        assert.equal(lifecycle.writeAttempts,1);assert.equal(lifecycle.records.length,512);
        assert.equal(lifecycle.records.at(-2).kind,'purchase-acknowledgement-intent');
        assert.equal(lifecycle.records.at(-1).acknowledged,true);
        if(mode==='ack-journal-race')assert.match(lifecycle.fault,/trace capacity/);
        else assert.equal(lifecycle.fault,null);
    }
}
console.log('Purchase observer: measured debits, admission/execution, acquisition callers, lineage and guarded detach passed');

// Read-only routine decoding: the row feature is not the improvement, the
// maximum can be negative, and cached XY/funds do not imply admission/payment.
{
hooks.clear();
vm.runInContext(fs.readFileSync(__dirname+'/routine_supplier_observer.js','utf8'),context);
const build=0xc0000,rows=0xd0000,values=0xe0000,manager=0xf0000,node=0x100000;
put(city,0xd8,1);put(city,0xa8,524295);put(build,0x90,city);
put(build,0x4c8,rows);put(build,0x4d8,2);put(build,0x488,2);
put(build,0x238,47);put(build,0x23c,11);
for(let i=0;i<2;i++) {
    const row=rows+i*0x78,v=values+i*16;
    put(row,0,4+i);put(row,4,i===0?-1:7);put(row,0x57,1);
    put(row,8,47+i);put(row,12,11);put(row,0x30,v);
    put(v,0,i===0?100:-10);put(v,4,i===0?200:-20);
}
put(player,0xd8,1);put(player,0x6d0,manager);put(manager,0xd0,node);
put(node,0,city);put(node,0x10,0);put(city,0x1948,build);
put(economic,0x250,slushFund);put(slushFund,0,10000);put(slushFund,8,20000);
const routineRows=[],routineFaults=[],routineListeners=[];
context.observeRoutineSupplier({core:{base:ptr(0)},scope:{player:1,city:524295,width:74,height:46,plots:[861]},
    read:(p,o,t)=>{const value=cells.get(Number(p.toString())+o);assert.notEqual(value,undefined);return t==='ptr'?String(value):value;},
    fingerprint:(rva,bytes)=>assert([0x3de990,0x458530].includes(rva)&&bytes.length===32),
    emit:r=>routineRows.push(r),fail:e=>routineFaults.push(String(e)),turnNow:()=>216,listeners:routineListeners});
const invocation={};hooks.get(0x3de990).onEnter.call(invocation,[ptr(build)]);
hooks.get(0x3de990).onLeave.call(invocation);
hooks.get(0x458530).onEnter.call({},[ptr(economic)]);
assert.equal(routineFaults.length,0);assert.equal(routineRows.length,2);
assert.equal(routineRows[0].frontier[0].maximumQ8,200);
assert.equal(routineRows[0].frontier[0].improvement,1);
assert.equal(routineRows[0].frontier[0].scoresQ8[1],200);
assert.equal(routineRows[0].frontier[1].feature,7);
assert.equal(routineRows[0].frontier[1].maximumQ8,-10);
assert.equal(routineRows[1].cached.x,47);assert.equal(routineRows[1].plotFundQ8,20000);
put(build,0x4d8,257);hooks.get(0x3de990).onLeave.call(invocation);
assert.match(routineFaults[0],/row bounds/);
hooks.get(0x458530).onEnter.call({},[ptr(economic)]);assert.equal(routineRows.length,2);
routineListeners.forEach(listener=>listener.detach());assert.equal(hooks.size,0);
console.log('Routine supplier observer: bounded rows, feature/max fields, cached XY/funds and fault latch passed');
}
