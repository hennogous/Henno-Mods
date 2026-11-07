'use strict';

// Read the ordinary improvement proposal and the site selector on patched XP2.
// A nonempty reservation handle excludes the row only if the lookup resolves.
const CHECK_IMPROVEMENT = 0x3e1150;
const ANALYZE_TERRAIN = 0x3dec40;
const BEST_LOCATION = 0x3e5750;
const FIND_RESERVATION = 0x4019f0;
const LOCATION_CALLERS = new Map([
    [0x3e11a5, 'ordinary-proposal'],
    [0x3d75c1, 'boost-resource-check'],
    [0x3d7667, 'boost-specific-resource-check'],
    [0x481501, 'unit-charge-effect'],
    [0x55ae9b, 'trigger-empire-location'],
    [0x55b010, 'trigger-city-location'],
    [0x55b102, 'trigger-plot-location'],
    [0x55d619, 'choose-improvement-node'],
]);
const RESERVATION_RETURN = 0x3e5813;
const TERRAIN_RESERVATION_RETURN = 0x3dee50;
const LAYOUT = {
    city: 0x90, owner: 0xd8, cityId: 0xa8, bestType: 0x250,
    treeSlot: 0x430, treeId: 0xc, rows: 0x4c8, count: 0x4d8, stride: 0x78,
    x: 8, y: 12, improvementScores: 0x30, reservation: 0x48,
    selectable: 0x54, owned: 0x5a, plotCoordinates: 0x28,
};
const memory = createStudyMemoryIO({ptr, findRangeByAddress: value => Process.findRangeByAddress(value)});
const records = [], selections = new Map(), terrain = new Map();
let installed = false, enabled = false, active = 0, boundary = null, fault = null;

function read(address, offset, type) {
    const value = memory.read(address.toString(), offset, type);
    if (value.error) throw Error(`Supplier read ${type} at ${offset}: ${value.error}`);
    return value.value;
}

function add(record) {
    if (records.length >= 1024) throw Error('Supplier observer evidence budget');
    records.push({boundary, ...record});
}

function init(spec, scope) {
    if (installed || Process.platform !== 'windows' || Process.arch !== 'x64' || Process.pointerSize !== 8)
        throw Error('Expected first installation on Windows x64');
    const normalized = path => path.replace(/\\/g, '/').toLowerCase();
    const modules = Process.enumerateModules();
    const core = modules.find(module => normalized(module.path) === normalized(spec.path));
    const carriers = modules.filter(module => /GameCore_XP2_(?:CE|CSC)/i.test(module.name));
    const expectedCarrier = scope.cePath
        ? carriers.length === 1 && normalized(carriers[0].path) === normalized(scope.cePath)
        : carriers.length === 0;
    if (!core || core.size !== spec.image_size || !expectedCarrier
        || scope.player !== 3 || scope.city !== 131073 || scope.plot !== 796 || scope.x !== 56 || scope.y !== 10
        || !Number.isInteger(scope.pasture) || scope.pasture < 0 || scope.pasture >= 256)
        throw Error('Expected the qualified Boston Cattle scope');
    const address = rva => core.base.add(rva);
    for (const [rva, expected] of [
        [CHECK_IMPROVEMENT, '4c8bdc574881ec10010000488b8130040000'],
        [ANALYZE_TERRAIN, '48894c240853565741554157'],
        [BEST_LOCATION, '44884c242048894c2408415541574883ec684c63ea458bf84183fdff750b33c0'],
        [FIND_RESERVATION, '448bc283faff74454c8b9110010000'],
    ]) {
        const bytes = Array.from(new Uint8Array(address(rva).readByteArray(expected.length / 2)),
            value => value.toString(16).padStart(2, '0')).join('');
        if (bytes !== expected) throw Error(`Supplier function prefix ${rva.toString(16)}`);
    }
    for (const [returnRva, callee] of [...Array.from(LOCATION_CALLERS.keys(), rva => [rva, BEST_LOCATION]),
        [RESERVATION_RETURN, FIND_RESERVATION],
        [TERRAIN_RESERVATION_RETURN, FIND_RESERVATION]]) {
        const end = address(returnRva);
        if (end.sub(5).readU8() !== 0xe8 || !end.add(end.sub(4).readS32()).equals(address(callee)))
            throw Error(`Supplier caller fingerprint ${returnRva.toString(16)}`);
    }
    const l = LAYOUT;
    const caller = invocation => invocation.returnAddress.sub(core.base).toInt32();
    const ownerCity = build => {
        const city = read(build, l.city, 'ptr');
        if (read(city, l.owner, 'i32') !== scope.player) return null;
        return read(city, l.cityId, 'i32');
    };
    const target = build => ownerCity(build) === scope.city;
    const slot = build => read(read(build, l.treeSlot, 'ptr'), l.treeId, 'i32');
    const coordinatesMatch = (row, x, y) => read(row, l.x, 'i32') === x && read(row, l.y, 'i32') === y;
    const score = (row, index) => read(read(row, l.improvementScores, 'ptr'), index * 4, 'i32');
    function findRow(build, x, y) {
        const count = read(build, l.count, 'u32');
        if (count > 37) throw Error('Unexpected CityBuild radius');
        const rows = ptr(read(build, l.rows, 'ptr'));
        for (let i = 0; i < count; i++) {
            const row = rows.add(i * l.stride);
            if (coordinatesMatch(row, x, y)) return row;
        }
        return null;
    }
    function census(build) {
        const row = findRow(build, scope.x, scope.y);
        return row && {
            pastureQ8: score(row, scope.pasture),
            reservation: read(read(row, l.reservation, 'ptr'), 0, 'i32'),
            flags: [read(row, l.selectable, 'u8'), read(row, l.owned, 'u8')],
        };
    }
    function watch(rva, enter, leave) {
        Interceptor.attach(address(rva), {
            onEnter(args) {
                if (!enabled) return;
                try { this.sample = enter(args, this); if (this.sample) active++; }
                catch (error) { fault = String(error); enabled = false; }
            },
            onLeave(result) {
                if (!this.sample) return;
                active--;
                try { leave(this.sample, result); }
                catch (error) { fault = String(error); enabled = false; }
            },
        });
    }
    watch(CHECK_IMPROVEMENT, a => {
        if (target(a[0])) return {build: a[0], before: slot(a[0]), type: read(a[0], l.bestType, 'i32'), site: census(a[0])};
    }, ({build, before, type, site}) => add({kind: 'proposal', before, after: slot(build), type, site}));
    watch(ANALYZE_TERRAIN, (a, invocation) => {
        if (!target(a[0])) return;
        const sample = {thread: invocation.threadId, build: a[0], reservationResolved: null};
        terrain.set(sample.thread, sample);
        return sample;
    }, ({thread, build, reservationResolved}) => {
        terrain.delete(thread);
        add({kind: 'terrain', type: read(build, l.bestType, 'i32'), site: census(build), reservationResolved});
    });
    watch(BEST_LOCATION, (a, invocation) => {
        const route = LOCATION_CALLERS.get(caller(invocation));
        if (!route) return;
        const city = ownerCity(a[0]);
        if (city === null) return;
        const row = findRow(a[0], scope.x, scope.y);
        if (!row && city !== scope.city) return;
        const thread = invocation.threadId;
        if (selections.has(thread)) throw Error('Nested supplier selector');
        const type = a[1].toInt32();
        const sample = {thread, build: a[0], city, type, route, reservationResolved: null,
                        targetQ8: row && type >= 0 && type < 256 ? score(row, type) : null};
        selections.set(thread, sample);
        return sample;
    }, ({thread, build, city, type, route, targetQ8, reservationResolved}, result) => {
        selections.delete(thread);
        let plot = null;
        if (!result.isNull()) {
            const span = memory.readBytes(result.toString(), l.plotCoordinates, 4);
            if (span.error) throw Error(`Supplier returned plot coordinates: ${span.error}`);
            const coords = new DataView(Uint8Array.from(span.value).buffer);
            plot = [coords.getInt16(0, true), coords.getInt16(2, true)];
        }
        const row = plot && findRow(build, ...plot);
        add({kind: 'location', city, route, type, plot, q8: row ? score(row, type) : null, targetQ8, reservationResolved});
    });
    watch(FIND_RESERVATION, (a, invocation) => {
        const from = caller(invocation);
        if (from === RESERVATION_RETURN) {
            const sample = selections.get(invocation.threadId);
            if (sample && coordinatesMatch(invocation.context.rdi, scope.x, scope.y)) return sample;
        } else if (from === TERRAIN_RESERVATION_RETURN) {
            const sample = terrain.get(invocation.threadId);
            if (sample && coordinatesMatch(invocation.context.r15, scope.x, scope.y)) return sample;
        }
    }, (sample, result) => { sample.reservationResolved = !result.isNull(); });
    Interceptor.flush();
    installed = true;
    return true;
}

rpc.exports = {
    init,
    advance(turn) { boundary = turn; enabled = !fault; },
    snapshot() { return {records, active, fault}; },
    freeze() { enabled = false; return {records, active, fault}; },
};
