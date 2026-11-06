'use strict';

// Patched XP2, audited by audit_xp2_hotfix.py. The aggregation takes CityBuild
// in RCX. The call at 3e293c finishes the district matrix. The
// winner takes CityBuild and an output pair of i32 plot coordinates.
const DISTRICT_AGGREGATION = STUDY_POINTS.CalculateDistrictValues;
const DISTRICT_WINNER = [0x3e4a50, '48894c24085355564154415541574883ec284c8bea488be9e873be3e00488bb5'];
const AGGREGATION_RETURN = 0x3e2941;
const LAYOUT = {
    city: 0x90, cityId: 0xa8, playerId: 0xd8,
    rows: 0x4c8, rowCount: 0x4d8, stride: 0x78, maxRows: 37,
    x: 8, y: 12, rowScores: 0x20, reservation: 0x48, eligible: 0x55, owned: 0x5a,
    matrix: 0x518, matrixCapacity: 0x520, matrixLength: 0x528,
    districtTreeData: 0x430, districtTreeId: 8,
};

const memory = createStudyMemoryIO({ptr, findRangeByAddress: address => Process.findRangeByAddress(address)});
const listeners = [];
const records = [];
let enabled = false;
let window = null;
let armed = false;
let pending = 0;
let writes = 0;
let fault = null;

function read(address, offset, type) {
    const result = memory.read(address, offset, type);
    if (result.error) throw Error(`${type} at ${offset}: ${result.error}`);
    return result.value;
}

function record(receipt) {
    if (records.length >= 512) throw Error('Diagnostic trace capacity');
    records.push(receipt);
}

function identity(object) {
    const city = read(object, LAYOUT.city, 'ptr');
    return `${read(city, LAYOUT.playerId, 'i32')}:${read(city, LAYOUT.cityId, 'i32')}`;
}

function districtTree(object) {
    // CheckForDistrict (3e0ee0) only reaches GetBestDistrict when this ID is -1.
    return read(read(object, LAYOUT.districtTreeData, 'ptr'), LAYOUT.districtTreeId, 'i32');
}

function findRow(object, x, y) {
    const count = read(object, LAYOUT.rowCount, 'u32');
    if (count > LAYOUT.maxRows) throw Error('CityBuild row count exceeds hex range');
    const rows = read(object, LAYOUT.rows, 'ptr');
    for (let index = 0; index < count; index++) {
        const row = memory.add(rows, index * LAYOUT.stride);
        if (read(row, LAYOUT.x, 'i32') === x && read(row, LAYOUT.y, 'i32') === y) return {row, index, count};
    }
    return null;
}

function snapshotSite(object, target, world) {
    const found = findRow(object, target.plot % world.width, Math.floor(target.plot / world.width));
    if (!found || found.index === 0) return {status: 'row-absent'};
    const {row, index, count} = found;
    if (read(row, LAYOUT.owned, 'u8') !== 1 || read(row, LAYOUT.eligible, 'u8') !== 1)
        return {status: 'row-ineligible'};
    const reservation = read(read(row, LAYOUT.reservation, 'ptr'), 0, 'i32');
    // A placement boost must avoid all reservations. A protection deduction
    // may lower the score that would otherwise beat an improvement reserve.
    // The reservation itself is left entirely in native ownership.
    if (reservation !== -1 && !target.protectedPlots) return {status: 'row-reserved'};

    // The score row binds the same cell as the mutable aggregation matrix.
    // Recheck both layouts after return. A reallocated or detached row has no
    // safe write target for this experiment.
    const length = read(object, LAYOUT.matrixLength, 'u32');
    const capacity = read(object, LAYOUT.matrixCapacity, 'u32');
    if (length !== count * world.districtCount || capacity < length || capacity > LAYOUT.maxRows * 4096)
        throw Error('District matrix bounds');
    const scores = read(row, LAYOUT.rowScores, 'ptr');
    const matrix = read(object, LAYOUT.matrix, 'ptr');
    if (scores !== memory.add(matrix, index * world.districtCount * 4)) return {status: 'matrix-detached'};
    const offset = target.district * 4;
    return {status: 'observed', cell: memory.add(scores, offset), value: read(scores, offset, 'i32'), reservation};
}

function safeAlternative(object, target, world) {
    // Limit the calibration to owned, unreserved rows. The native selector can
    // also admit adjacent unowned rows and can outbid existing reservations.
    // We observe the actual returned winner separately after the deduction.
    const count = read(object, LAYOUT.rowCount, 'u32');
    if (count > LAYOUT.maxRows) throw Error('Alternative row count bound');
    const rows = read(object, LAYOUT.rows, 'ptr');
    let best = null;
    for (let index = 1; index < count; index++) {
        const row = memory.add(rows, index * LAYOUT.stride);
        if (!read(row, LAYOUT.owned, 'u8') || !read(row, LAYOUT.eligible, 'u8')) continue;
        const x = read(row, LAYOUT.x, 'i32'), y = read(row, LAYOUT.y, 'i32');
        if (!bounds(x, 0, world.width - 1) || !bounds(y, 0, world.height - 1)) throw Error('Alternative coordinates');
        const plot = y * world.width + x;
        if (target.protectedPlots.includes(plot) || read(read(row, LAYOUT.reservation, 'ptr'), 0, 'i32') !== -1)
            continue;
        const scores = read(row, LAYOUT.rowScores, 'ptr');
        for (let district = 0; district < world.districtCount; district++) {
            const score = read(scores, district * 4, 'i32');
            if (score > (best?.score ?? 0)) best = {plot, district, score};
        }
    }
    return best;
}

function hook(address, enter, leave) {
    listeners.push(Interceptor.attach(address, {
        onEnter(args) {
            this.sample = null;
            if (!enabled) return;
            try {
                this.sample = enter(args, this.returnAddress);
                if (this.sample) pending++;
            } catch (error) {
                fault = String(error);
                enabled = false;
            }
        },
        onLeave(result) {
            if (!this.sample) return;
            pending--;
            if (!enabled) return;
            try { leave(this.sample, result); }
            catch (error) {
                fault = String(error);
                enabled = false;
            }
        },
    }));
}

const bounds = (value, min, max) => Number.isInteger(value) && min <= value && value <= max;

function prepare(world, targets, pulse) {
    if (enabled || pending || armed || fault || writes) throw Error('New window requires a clean zero-write drain');
    const byCity = new Map();
    if (!bounds(world.width, 1, 256) || !bounds(world.height, 1, 256) || !bounds(world.districtCount, 2, 4096)
        || !bounds(targets.length, 1, 64)) throw Error('World or target count bounds');
    for (const target of targets) {
        if (!bounds(target.player, 1, 63) || !bounds(target.city, 0, 0x7fffffff)
            || !bounds(target.plot, 0, world.width * world.height - 1)
            || !bounds(target.district, 1, world.districtCount - 1)) throw Error('Target bounds');
        if (target.protectedPlots && (targets.length !== 1 || !Array.isArray(target.protectedPlots)
            || !bounds(target.protectedPlots.length, 1, 6) || !target.protectedPlots.includes(target.plot)
            || target.protectedPlots.some(plot => !bounds(plot, 0, world.width * world.height - 1))))
            throw Error('Exact protection scope required');
        const key = `${target.player}:${target.city}`;
        if (!byCity.has(key)) byCity.set(key, []);
        byCity.get(key).push(target);
    }
    if (pulse) {
        const protect = Boolean(targets[0].protectedPlots);
        const allowed = protect ? bounds(pulse.delta, -200000, -1) && Number.isInteger(pulse.reservation)
            : bounds(pulse.delta, 1, 200000);
        if (targets.length !== 1 || !allowed || !bounds(pulse.before, 1, 0x7fffffff)
            || !bounds(pulse.native, 1, 0x7fffffff) || !bounds(pulse.native + pulse.delta, 1, 0x7fffffff))
            throw Error('Single calibrated diagnostic bid required');
    }
    records.length = 0;
    window = {world, byCity, pulse};
    armed = true;
}

function install(spec) {
    const pathKey = value => value.replace(/\\/g, '/').toLowerCase();
    if (listeners.length || Process.platform !== 'windows' || Process.arch !== 'x64' || Process.pointerSize !== 8)
        throw Error('First installation on Windows x64 required');
    const modules = Process.enumerateModules();
    if (modules.some(module => /GameCore_XP2_(?:CE|CSC)/i.test(module.name))) throw Error('Native carrier conflict');
    const core = modules.find(module => pathKey(module.path) === pathKey(spec.path));
    if (!core || core.size !== spec.image_size) throw Error('Exact loaded XP2 module required');
    const [aggregate, winner] = [DISTRICT_AGGREGATION, DISTRICT_WINNER].map(([rva, expected]) => {
        const address = core.base.add(rva);
        const actual = Array.from(new Uint8Array(address.readByteArray(32)), b => b.toString(16).padStart(2, '0')).join('');
        if (actual !== expected) throw Error(`XP2 fingerprint at RVA ${rva.toString(16)}`);
        return address;
    });
    hook(aggregate, (args, caller) => {
        if (!caller.equals(core.base.add(AGGREGATION_RETURN))) return null;
        const object = args[0].toString();
        const {world, byCity} = window;
        const sites = byCity.get(identity(object));
        return sites ? {object, sites: sites.map(target => ({target, entry: snapshotSite(object, target, world)}))} : null;
    }, ({object, sites}) => {
        const {world, pulse} = window;
        const tree = districtTree(object);
        for (const {target, entry} of sites) {
            const exit = snapshotSite(object, target, world);
            const {player, city, district, plot} = target;
            const receipt = {kind: 'calculation', player, city, district, plot, entry: entry.status, exit: exit.status,
                tree, sameCell: Boolean(entry.cell && entry.cell === exit.cell),
                reservation: exit.reservation ?? null,
                before: entry.value ?? null, native: exit.value ?? null, final: exit.value ?? null};
            if (!pulse || writes || tree !== -1) { record(receipt); continue; }
            if (!entry.cell || entry.cell !== exit.cell || pulse.before !== entry.value || pulse.native !== exit.value
                || (target.protectedPlots && pulse.reservation !== exit.reservation))
                throw Error('Fresh calculation differs from matched control or moved cells');
            const cell = ptr(exit.cell);
            const range = Process.findRangeByAddress(cell);
            if (!range || !range.protection.includes('w') || cell.add(3).compare(range.base.add(range.size)) >= 0)
                throw Error('Target score cell is not writable');
            receipt.final = exit.value + pulse.delta;
            record(receipt);
            cell.writeS32(receipt.final);
            writes++;
            if (cell.readS32() !== receipt.final) throw Error('Score readback differs');
        }
    });

    hook(winner, args => {
        const object = args[0].toString();
        const sites = window.byCity.get(identity(object));
        return sites ? {object, output: args[1].toString(), target: sites[0]} : null;
    }, ({object, output, target}, result) => {
        const {player, city} = target;
        const {world} = window;
        const district = result.toInt32();
        if (district === -1) { record({kind: 'winner', player, city, district, writes}); return; }
        const x = read(output, 0, 'i32'), y = read(output, 4, 'i32');
        const found = findRow(object, x, y);
        if (!found || !bounds(district, 0, world.districtCount - 1)
            || !bounds(x, 0, world.width - 1) || !bounds(y, 0, world.height - 1)) throw Error('Invalid native winner');
        const scores = read(found.row, LAYOUT.rowScores, 'ptr');
        const receipt = {kind: 'winner', player, city, district, plot: y * world.width + x,
            score: read(scores, district * 4, 'i32'), writes};
        if (target.protectedPlots && !window.pulse) receipt.alternative = safeAlternative(object, target, world);
        record(receipt);
    });
    Interceptor.flush();
    return listeners.length;
}

rpc.exports = {
    init: install, prepare,
    start() {
        if (listeners.length !== 2 || !armed) throw Error('Expected an installed and prepared window');
        armed = false;
        enabled = true;
    },
    async freeze() {
        enabled = false;
        const deadline = Date.now() + 5000;
        while (pending) {
            if (Date.now() >= deadline) throw Error('Native callback drain deadline');
            await new Promise(resolve => setTimeout(resolve, 10));
        }
        return {records, writes, fault, pending};
    },
};
