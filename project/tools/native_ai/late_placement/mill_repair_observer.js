'use strict';

// Patched Steam XP2. Observe the ordinary building score, the native building
// choice and a BuildBuilding attempt for one existing damaged Mill. Never write.
const MILL_VALUE = 0x52a050;
const ORDINARY_RETURN = 0x3e3ee2;
const BEST_BUILDING = 0x3e4710;
const REQUIREMENTS = 0x0f61c0;
const REQUIREMENTS_RETURN = 0x3e48bb;
const BUILD_BUILDING = 0x3df040;
const CITY_BUILD_CITY = 0x90, CITY_OWNER = 0xd8, CITY_ID = 0xa8;
const CITY_ROWS = 0x4c8, CITY_ROW_COUNT = 0x4d8, ROW_BUILDING_SCORES = 0x28;
const memory = createStudyMemoryIO({ptr, findRangeByAddress: address => Process.findRangeByAddress(address)});
const records = [], selection = new Map();
let enabled = false, installed = false, boundary = null, fault = null, active = 0;

function read(pointer, offset, type) {
    const result = memory.read(pointer.toString(), offset, type);
    if (result.error) throw Error(`${type} at ${offset}: ${result.error}`);
    return result.value;
}

function add(record) {
    if (records.length >= 4096) throw Error('Mill observer evidence budget');
    records.push({boundary, ...record});
}

function protect(operation) {
    try { operation(); }
    catch (error) { enabled = false; fault = String(error); }
}

function init(spec, scope) {
    const normalize = value => value.replace(/\\/g, '/').toLowerCase();
    if (installed || Process.platform !== 'windows' || Process.arch !== 'x64' || Process.pointerSize !== 8)
        throw Error('Expected first installation on Windows x64');
    const modules = Process.enumerateModules();
    if (modules.some(module => /GameCore_XP2_(?:CE|CSC)/i.test(module.name))) throw Error('Unexpected native carrier');
    const core = modules.find(module => normalize(module.path) === normalize(spec.path));
    if (!core || core.size !== spec.image_size || scope.player !== 3 || scope.city !== 131073 ||
        !Number.isInteger(scope.mill) || scope.mill < 0 || scope.mill >= 4096)
        throw Error('Expected the qualified Boston repair fixture');

    const address = rva => core.base.add(rva);
    const caller = invocation => invocation.returnAddress.sub(core.base).toInt32();
    const target = city => read(city, CITY_OWNER, 'i32') === scope.player && read(city, CITY_ID, 'i32') === scope.city;
    const cityOf = build => ptr(read(build, CITY_BUILD_CITY, 'ptr'));
    for (const [rva, prefix] of [
        [MILL_VALUE, '4c894424188954241055535741544155'],
        [BEST_BUILDING, '44884c24204488442418488954241055'],
        [BUILD_BUILDING, '48895c241048896c2418565741564881'],
    ]) {
        const bytes = Array.from(new Uint8Array(address(rva).readByteArray(prefix.length / 2)),
            value => value.toString(16).padStart(2, '0')).join('');
        if (bytes !== prefix) throw Error(`Function prefix at ${rva.toString(16)}`);
    }
    for (const [rva, expected] of [[ORDINARY_RETURN, MILL_VALUE], [REQUIREMENTS_RETURN, REQUIREMENTS]]) {
        const end = address(rva);
        if (end.sub(5).readU8() !== 0xe8 || !end.add(end.sub(4).readS32()).equals(address(expected)))
            throw Error(`Caller fingerprint at ${rva.toString(16)}`);
    }

    function observe(rva, enter, leave) {
        Interceptor.attach(address(rva), {
            onEnter(args) {
                if (!enabled) return;
                protect(() => { this.sample = enter(args, this); if (this.sample) active++; });
            },
            onLeave(result) {
                if (!this.sample) return;
                active--;
                protect(() => leave(this.sample, result));
            },
        });
    }
    observe(MILL_VALUE, (a, invocation) => {
        if (caller(invocation) !== ORDINARY_RETURN || a[1].toInt32() !== scope.mill || !target(a[6])) return;
        if (read(a[7], 0, 'i32') !== -9999 || read(a[7], 4, 'i32') !== -9999) throw Error('Expected ordinary coordinates');
        return {out: a[0], ready: a[3].toInt32(), horizon: a[4].toInt32()};
    }, (sample, result) => {
        if (!result.equals(sample.out)) throw Error('Unexpected building value return');
        add({kind: 'value', q8: read(result, 0, 'i32'), ready: sample.ready, horizon: sample.horizon});
    });
    observe(BEST_BUILDING, (a, invocation) => {
        if (!target(cityOf(a[0]))) return;
        const count = read(a[0], CITY_ROW_COUNT, 'u32');
        if (!count || count > 37) return;
        const vector = ptr(read(read(a[0], CITY_ROWS, 'ptr'), ROW_BUILDING_SCORES, 'ptr'));
        if (vector.isNull()) return;
        const sample = {out: a[1], thread: invocation.threadId, caller: caller(invocation),
            flags: [a[2].toInt32() & 255, a[3].toInt32() & 255],
            millQ8: read(vector, scope.mill * 4, 'i32'), requirements: null};
        if (selection.has(sample.thread)) throw Error('Nested target building choice');
        selection.set(sample.thread, sample);
        return sample;
    }, (sample, result) => {
        selection.delete(sample.thread);
        const winner = result.toInt32();
        add({kind: 'choice', caller: sample.caller, flags: sample.flags, millQ8: sample.millQ8,
            requirements: sample.requirements, winner, winnerQ8: winner < 0 ? null : read(sample.out, 0, 'i32')});
    });
    observe(REQUIREMENTS, (a, invocation) => {
        if (caller(invocation) !== REQUIREMENTS_RETURN || a[1].toInt32() !== scope.mill) return;
        return selection.get(invocation.threadId);
    }, (sample, result) => { sample.requirements = Boolean(result.toInt32() & 255); });
    observe(BUILD_BUILDING, (a, invocation) => {
        if (target(cityOf(a[0]))) return {building: a[1].toInt32(), caller: caller(invocation)};
    }, (sample, result) => add({kind: 'request', ...sample, accepted: Boolean(result.toInt32() & 255)}));
    Interceptor.flush();
    installed = true;
    return true;
}

rpc.exports = {
    init,
    advance(turn) { boundary = turn; enabled = true; },
    snapshot() { return {records, active, fault}; },
    freeze() { enabled = false; return {records, active, fault}; },
};
