'use strict';

// Diagnostic ready gate for a committed harvest tree. At ClearPlotNode::Update
// cleanup, EBP holds the return status, RSI the bound coordinates, RBX the
// selected worker and R15 the node. Leave native cleanup on its normal path.
const CLEAR_READY_CLEANUP = 0x55ed39;
const CLEAR_FAILURE_PATH = 0x55ed31;
const CLEAR_FAILURE_PREFIX = 'bd03000000498bc8e8b21b4300';
const CLEAR_READY = 1;
const CLEAR_FAILURE = 3;
const FIXTURE_BUILDER = 2228225;
const CLEAR_LAYOUT = {
    selectedWorker: 0x40, harvestBindings: 0x30, harvestIndex: 0x3c,
    bindingCount: 0x10, harvestStride: 8, unitId: 0xb0, unitOwner: 0x128,
};

function attachClearGate(address, read, add, scope) {
    const prefix = address(CLEAR_FAILURE_PATH);
    const bytes = Array.from(new Uint8Array(prefix.readByteArray(CLEAR_FAILURE_PREFIX.length / 2)),
        value => value.toString(16).padStart(2, '0')).join('');
    if (bytes !== CLEAR_FAILURE_PREFIX) throw Error('Clear Plot status path changed');
    const l = CLEAR_LAYOUT;
    let rejected = false;
    return Interceptor.attach(address(CLEAR_READY_CLEANUP), function () {
        const c = this.context;
        if (!scope.enabled() || c.rbp.toInt32() !== CLEAR_READY || c.rsi.isNull()) return;
        try {
            if (read(c.rsi, 0, 'i32') !== scope.x || read(c.rsi, 4, 'i32') !== scope.y) return;
            if (read(c.rbx, l.unitOwner, 'i32') !== scope.player) return;
            const unit = read(c.rbx, l.unitId, 'i32');
            const selected = c.r15.add(l.selectedWorker);
            if (read(c.r15, l.selectedWorker, 'i32') !== unit) throw Error('Selected Clear Plot worker disagrees');
            const vector = ptr(read(c.r15, l.harvestBindings, 'ptr'));
            const index = read(c.r15, l.harvestIndex, 'i32');
            if (vector.isNull() || index < 0 || index >= read(vector, l.bindingCount, 'u32')) return;
            const entries = ptr(read(vector, 0, 'ptr'));
            if (!read(entries, index * l.harvestStride, 'u8')) return;
            // Reject the first ready call from the Builder recorded in the
            // control fixture. Keep later attempts visible at stock behavior
            // so a persistent reservation or retry cannot look like release.
            const blocked = scope.block && unit === FIXTURE_BUILDER && !rejected;
            if (blocked) {
                const range = Process.findRangeByAddress(selected);
                if (!range || !range.protection.includes('w')
                    || selected.add(3).compare(range.base.add(range.size)) >= 0)
                    throw Error('Clear Plot worker field is not writable');
            }
            add({kind: 'clear-harvest-ready', unit, plot: scope.plot, native: CLEAR_READY,
                 result: blocked ? CLEAR_FAILURE : CLEAR_READY, blocked});
            if (blocked) {
                selected.writeS32(-1);
                c.rbp = ptr(CLEAR_FAILURE);
                rejected = true;
            }
        } catch (error) { scope.fail(error); }
    });
}

// The fixture loader verifies the DLL hashes and the observed starting
// city/supplier state. Check the in-process module paths and instruction
// fingerprint too, before attaching with the hook disabled.
let installed = false;
let enabled = false;
let boundary = null;
let fault = null;
const records = [];

function init(spec, scope) {
    if (installed || Process.platform !== 'windows' || Process.arch !== 'x64' || Process.pointerSize !== 8)
        throw Error('Expected first installation on Windows x64');
    if (scope.player !== 3 || scope.city !== 131073 || scope.plot !== 796 || scope.x !== 56 || scope.y !== 10
        || typeof scope.block !== 'boolean')
        throw Error('Expected the matched Boston harvest fixture');
    const normalize = path => path.replace(/\\/g, '/').toLowerCase();
    const modules = Process.enumerateModules();
    const core = modules.find(module => normalize(module.path) === normalize(spec.path));
    const carriers = modules.filter(module => /GameCore_XP2_(?:CE|CSC)/i.test(module.name));
    if (!core || core.size !== spec.image_size || carriers.length !== 1
        || normalize(carriers[0].path) !== normalize(scope.cePath))
        throw Error('Expected the qualified XP2 and CE modules');
    const memory = createStudyMemoryIO({ptr, findRangeByAddress: value => Process.findRangeByAddress(value)});
    const read = (address, offset, kind) => {
        const result = memory.read(address.toString(), offset, kind);
        if (result.error) throw Error(`Clear Plot read ${kind} at ${offset}: ${result.error}`);
        return result.value;
    };
    const add = record => {
        if (records.length >= 128) throw Error('Clear Plot observer evidence budget');
        records.push({boundary, ...record});
    };
    attachClearGate(rva => core.base.add(rva), read, add, {
        ...scope,
        enabled: () => enabled,
        fail(error) { fault = String(error); enabled = false; },
    });
    Interceptor.flush();
    installed = true;
    return true;
}

rpc.exports = {
    init,
    advance(turn) { boundary = turn; enabled = !fault; },
    snapshot() { return {records, active: 0, fault}; },
    freeze() { enabled = false; return {records, active: 0, fault}; },
};
