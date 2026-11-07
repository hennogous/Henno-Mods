'use strict';

// A null result from the empire-wide boost route skips that city's candidate.
// A null result from the ordinary city route prevents a new improvement tree.
// Both routes keep full native control of other players, sites and work types.
const BEST_IMPROVEMENT_LOCATION = 0x3e5750;
const IMPROVEMENT_CALLERS = {boost: 0x55ae9b, city: 0x3e11a5};
const LOCATION_ENTRY = '44884c242048894c2408415541574883ec684c63ea458bf84183fdff750b33c0';
// ECX holds the signed score. The following JLE skips the row before it can
// win. RDI points to the row and R13D holds the improvement index.
const CANDIDATE_SCORE_GATE = 0x3e5848;
const CANDIDATE_GATE_BYTES = '3b0d621478000f8e91000000';
const REJECTED_SCORE_BITS = '0x80000000';
const CITY_BUILD_LAYOUT = {
    owner: 0x90, playerId: 0xd8, cityId: 0xa8, rows: 0x4c8, count: 0x4d8,
    rowStride: 0x78, rowX: 8, rowY: 12, improvementScores: 0x30,
    plotCoordinates: 0x28,
};
const memory = createStudyMemoryIO({ptr, findRangeByAddress: address => Process.findRangeByAddress(address)});
const records = [];
let listener = null;
let candidateListener = null;
let enabled = false;
let active = 0;
let rejected = 0;
let fault = null;
let boundary = null;

function read(address, offset, type) {
    const result = memory.read(address, offset, type);
    if (result.error) throw Error(`${type} at ${offset}: ${result.error}`);
    return result.value;
}

function scoreFor(object, x, y, farm) {
    const l = CITY_BUILD_LAYOUT;
    const count = read(object, l.count, 'u32');
    if (count > 37) throw Error('CityBuild row count exceeds hex range');
    const rows = read(object, l.rows, 'ptr');
    for (let index = 0; index < count; index++) {
        const row = memory.add(rows, index * l.rowStride);
        if (read(row, l.rowX, 'i32') !== x || read(row, l.rowY, 'i32') !== y) continue;
        return read(read(row, l.improvementScores, 'ptr'), farm * 4, 'i32');
    }
    throw Error('Returned improvement location is absent from CityBuild');
}

function stop(error) {
    enabled = false;
    fault = String(error);
}

function init(spec, scope) {
    const pathKey = value => value.replace(/\\/g, '/').toLowerCase();
    if (listener || Process.platform !== 'windows' || Process.arch !== 'x64' || Process.pointerSize !== 8)
        throw Error('First installation on Windows x64 required');
    const modules = Process.enumerateModules();
    if (modules.some(module => /GameCore_XP2_(?:CE|CSC)/i.test(module.name))) throw Error('Native carrier conflict');
    const core = modules.find(module => pathKey(module.path) === pathKey(spec.path));
    if (!core || core.size !== spec.image_size || scope.player !== 3 || scope.plot !== 796
        || scope.width !== 74 || scope.height !== 46 || !Number.isInteger(scope.farm) || scope.farm < 0 || scope.farm >= 256)
        throw Error('Exact Boston protection scope and loaded XP2 required');
    const address = core.base.add(BEST_IMPROVEMENT_LOCATION);
    const bytes = Array.from(new Uint8Array(address.readByteArray(32)), b => b.toString(16).padStart(2, '0')).join('');
    const callers = new Map();
    for (const [route, rva] of Object.entries(IMPROVEMENT_CALLERS)) {
        const caller = core.base.add(rva);
        if (caller.sub(5).readU8() !== 0xe8 || !caller.add(caller.sub(4).readS32()).equals(address))
            throw Error(`Improvement caller fingerprint for ${route}`);
        callers.set(caller.toString(), route);
    }
    if (bytes !== LOCATION_ENTRY) throw Error('Improvement selector fingerprint');
    const frames = new Map();
    if (scope.filterCandidates) {
        const gate = core.base.add(CANDIDATE_SCORE_GATE);
        const fingerprint = Array.from(new Uint8Array(gate.readByteArray(12)),
            value => value.toString(16).padStart(2, '0')).join('');
        if (fingerprint !== CANDIDATE_GATE_BYTES) throw Error('Improvement candidate gate fingerprint');
        candidateListener = Interceptor.attach(gate, function () {
            if (!enabled) return;
            const sample = frames.get(this.threadId)?.at(-1);
            if (!sample) return;
            try {
                const l = CITY_BUILD_LAYOUT;
                const row = this.context.rdi.toString();
                if (this.context.r13.toInt32() !== scope.farm) throw Error('Improvement index changed in selection');
                const x = read(row, l.rowX, 'i32');
                const y = read(row, l.rowY, 'i32');
                if (x < 0 || x >= scope.width || y < 0 || y >= scope.height) throw Error('Candidate coordinates outside map');
                if (y * scope.width + x !== scope.plot) return;
                const score = this.context.rcx.toInt32();
                if (score !== scoreFor(sample.object, x, y, scope.farm)) throw Error('Candidate score changed in selection');
                // Affect this comparison only. Native rows and remaining
                // candidates keep their original values.
                this.context.rcx = ptr(REJECTED_SCORE_BITS);
                sample.filtered = score;
                rejected++;
            } catch (error) { stop(error); }
        });
    }

    listener = Interceptor.attach(address, {
        onEnter(args) {
            this.sample = null;
            if (candidateListener) {
                this.frames = frames.get(this.threadId) || [];
                frames.set(this.threadId, this.frames);
                this.frames.push(null);
            }
            if (!enabled || args[1].toInt32() !== scope.farm
                || args[2].toInt32() !== -1 || (args[3].toUInt32() & 0xff) !== 0) return;
            const route = callers.get(this.returnAddress.toString());
            if (!route) return;
            try {
                const object = args[0].toString();
                const owner = read(object, CITY_BUILD_LAYOUT.owner, 'ptr');
                if (read(owner, CITY_BUILD_LAYOUT.playerId, 'i32') !== scope.player) return;
                this.sample = {object, route, city: read(owner, CITY_BUILD_LAYOUT.cityId, 'i32')};
                if (this.frames) this.frames[this.frames.length - 1] = this.sample;
                active++;
            } catch (error) { stop(error); }
        },
        onLeave(result) {
            if (this.frames) {
                this.frames.pop();
                if (!this.frames.length) frames.delete(this.threadId);
            }
            if (!this.sample) return;
            active--;
            if (!enabled) return;
            try {
                if (result.isNull()) {
                    if (this.sample.filtered !== undefined) {
                        if (records.length >= 1024) throw Error('Farm trace capacity');
                        records.push({boundary, route: this.sample.route, player: scope.player, city: this.sample.city,
                            plot: -1, filteredScore: this.sample.filtered, blocked: false});
                    }
                    return;
                }
                if (records.length >= 1024) throw Error('Farm trace capacity');
                const span = memory.readBytes(result.toString(), CITY_BUILD_LAYOUT.plotCoordinates, 4);
                if (span.error) throw Error('Returned plot coordinates: ' + span.error);
                const coordinates = new DataView(Uint8Array.from(span.value).buffer);
                const x = coordinates.getInt16(0, true), y = coordinates.getInt16(2, true);
                if (x < 0 || x >= scope.width || y < 0 || y >= scope.height) throw Error('Returned plot bounds');
                const plot = y * scope.width + x;
                const score = scoreFor(this.sample.object, x, y, scope.farm);
                const blocked = plot === scope.plot;
                if (candidateListener && blocked) throw Error('Protected plot passed the candidate filter');
                records.push({boundary, route: this.sample.route, player: scope.player, city: this.sample.city,
                    plot, score, blocked, filteredScore: this.sample.filtered});
                if (blocked) {
                    result.replace(ptr(0));
                    rejected++;
                }
            } catch (error) { stop(error); }
        },
    });
    Interceptor.flush();
    return true;
}

rpc.exports = {
    init,
    advance(turn) {
        if (!listener || fault || !Number.isInteger(turn) || (boundary !== null && turn <= boundary))
            throw Error('Expected monotonic boundary and healthy hook');
        boundary = turn;
        enabled = true;
    },
    snapshot() { return {records, rejected, active, fault}; },
    async freeze() {
        enabled = false;
        const deadline = Date.now() + 5000;
        while (active) {
            if (Date.now() >= deadline) throw Error('Farm guard callback drain deadline');
            await new Promise(resolve => setTimeout(resolve, 10));
        }
        return {records, rejected, active, fault};
    },
};
