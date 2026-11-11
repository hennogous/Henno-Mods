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
]);
class Pointer {
    constructor(value) { this.value = Number(value); }
    add(offset) { return new Pointer(this.value + offset); }
    toString() { return String(this.value); }
    toInt32() { return this.value | 0; }
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
const plotFund = 0x50000, slushFund = 0x50008, game = 0x60000, debit = 0x70000;
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
assert.deepEqual(result.records.slice(4).map(r => r.kind),
    ['quote', 'debit-call', 'debit-return', 'annex-return']);
assert(result.records.slice(4).every(r => r.plot === 400 && r.city === 524295 && r.turn === 203));
assert.equal(result.records[5].deltaQ8, -25600);
assert.equal(result.records[6].deltaQ8, -25600);
assert.equal(hooks.size, 0);
console.log('Purchase observer: signed Q8, savings boundaries, player/plot filters and detach passed');
