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
    [0x459169, '85c07e104d85f67405'],
    [0x45918f, '488bac24d0000000418bdfc1e308'],
    [0x459095, '48894c2408'],
    [0x4590a5, '4881ec80000000488be9'],
    [0x3e10fd, '488d8b70020000440fb64540'],
    [0x55dc9f, '488bd0488d4c2430e834f8e9ff'],
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
const fire = (site, overrides = {}) => hooks.get(site).call({context: {...registers, ...overrides}});
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
const command = {rdi: ptr(city), rbp: ptr(frame), rsi: ptr(-25600), rdx: ptr(debit)};
fire(0x681346, command); // Other own paid plot is a potential positive control.
fire(0x681379, command); fire(0x68137e, command); fire(0x6813a2, command);
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
console.log('Purchase observer: Q8, funds, lineage, unknown/stale bindings, filters and detach passed');
