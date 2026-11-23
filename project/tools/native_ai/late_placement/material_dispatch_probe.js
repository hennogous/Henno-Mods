'use strict';

// Matched replay only, Windows Steam XP2 092abfbb. At the ordinary admission
// boundary, let an exact supplier compete for a vacant city work slot. At
// ReleaseUnits, price an on-site worker's chance to finish, then let the stock
// recruitment and protection nodes make all decisions.
const CHECK_IMPROVEMENT = 0x3e1150;
const BEST_LOCATION = 0x3e5750;
const RELEASE_UNITS = 0x543830;
const GAME_INSTANCE = 0xb8aa68;
const GAME_TURN = 0xc0;
const CITY_BUILD = {city: 0x90, bestType: 0x250, slot: 0x430, slotId: 0xc, rows: 0x4c8, count: 0x4d8};
const ROW = {stride: 0x78, x: 8, y: 12, scores: 0x30};
const CITY = {owner: 0xd8, id: 0xa8};
const TREE = {allowsRecruit: 0x180, control: 0x1b0, priority: 0x1e0, value: 0x210,
    owner: 0x228, kind: 0x2b8, city: 0x2f0, plot: 0x308};
const OWNER_PLAYER = 0x330;
const PLAYER = {id: 0xd8, units: 0x6c8};
const UNIT_LIST = {head: 0xd0, next: 0x10};
const UNIT = {id: 0xb0, type: 0xc8, x: 0xf8, y: 0xfc, departing: 0x2e8, control: 0x300, charges: 0x538};
const PLOT_COORDINATES = 0x28;
const ADMISSION_BONUS_Q8 = 72 * 256;
const FINISH_BONUS = 48;

let enabled = false, armed = new Set(), fault = null, active = 0;
const samples = [];
function record(sample) {
    if (samples.length >= 512) throw Error('Dispatch trace exceeded 512 records');
    samples.push(sample);
}

function init(spec, scope) {
    if (Process.platform !== 'windows' || Process.arch !== 'x64' || ![131073, 393221].includes(scope.city)
        || scope.player !== 5 || !Number.isInteger(scope.farm) || !Number.isInteger(scope.builder))
        throw Error('Expected the matched Babylonian supplier replay');
    const normalize = file => file.replace(/\\/g, '/').toLowerCase();
    const modules = Process.enumerateModules();
    const core = modules.find(module => normalize(module.path) === normalize(spec.path));
    if (!core || core.size !== spec.image_size || !modules.some(module => normalize(module.path) === normalize(scope.cePath)))
        throw Error('Loaded XP2 or CE identity differs');
    const sites = new Map(scope.plots.map(site => [site.plot, site]));
    const expected = scope.city === 131073 ? ['2188:42,29'] : ['1975:51,26', '2047:49,27'];
    if (scope.plots.map(s => `${s.plot}:${s.x},${s.y}`).join('|') !== expected.join('|'))
        throw Error('Unexpected supplier plots');
    const address = rva => core.base.add(rva);
    for (const [rva, bytes] of [
        [CHECK_IMPROVEMENT, '4c8bdc574881ec10010000488b8130040000'],
        [BEST_LOCATION, '44884c242048894c2408415541574883ec684c63ea458bf84183fdff750b33c0'],
        [RELEASE_UNITS, '48895c241048897424185557415441'],
    ]) {
        const actual = Array.from(new Uint8Array(address(rva).readByteArray(bytes.length / 2)),
            byte => byte.toString(16).padStart(2, '0')).join('');
        if (actual !== bytes) throw Error(`Dispatch function bytes changed at ${rva.toString(16)}`);
    }
    const bestLocation = new NativeFunction(address(BEST_LOCATION), 'pointer', ['pointer', 'int', 'int', 'uchar']);
    const turn = () => address(GAME_INSTANCE).readPointer().add(GAME_TURN).readS32();
    const isCity = city => !city.isNull() && city.add(CITY.owner).readS32() === scope.player
        && city.add(CITY.id).readS32() === scope.city;
    const coordinates = plot => [plot.add(PLOT_COORDINATES).readS16(), plot.add(PLOT_COORDINATES + 2).readS16()];
    const locationMatches = (plot, site) => {
        if (plot.isNull()) return false;
        const [x, y] = coordinates(plot);
        return x === site.x && y === site.y;
    };
    function findRow(build, x, y) {
        const count = build.add(CITY_BUILD.count).readU32();
        if (count > 128) throw Error('Unexpected CityBuild plot row count');
        let row = build.add(CITY_BUILD.rows).readPointer();
        for (let index = 0; index < count; index++, row = row.add(ROW.stride))
            if (row.add(ROW.x).readS32() === x && row.add(ROW.y).readS32() === y) return row;
        return null;
    }
    const score = (row, kind) => row.add(ROW.scores).readPointer().add(kind * 4);
    const guard = action => { try { return action(); } catch (error) { enabled = false; fault ??= String(error); } };

    Interceptor.attach(address(CHECK_IMPROVEMENT), {
        onEnter(args) {
            if (!enabled || !armed.size) return;
            const build = args[0];
            if (!isCity(build.add(CITY_BUILD.city).readPointer())) return;
            this.sample = guard(() => {
                const slot = build.add(CITY_BUILD.slot).readPointer().add(CITY_BUILD.slotId);
                const typeField = build.add(CITY_BUILD.bestType);
                const before = slot.readS32(), type = typeField.readS32();
                const sample = {kind: 'admission', turn: turn(), before, type};
                const frame = {sample, slot};
                if (before !== -1) return frame;
                if (type < -1 || type > 255) throw Error('Unexpected improvement index');
                const stock = type >= 0 ? bestLocation(build, type, -1, 0) : ptr(0);
                const stockRow = stock.isNull() ? null : findRow(build, ...coordinates(stock));
                const stockQ8 = stockRow ? score(stockRow, type).readS32() : 0;
                sample.stock = stock.isNull() ? null : coordinates(stock);
                sample.stockQ8 = stockQ8;
                sample.candidates = [...armed].map(plot => {
                    const site = sites.get(plot), row = findRow(build, site.x, site.y);
                    const field = row ? score(row, scope.farm) : null;
                    return {site, field, q8: field ? field.readS32() : 0};
                }).filter(candidate => candidate.q8 > 0);
                const candidates = sample.candidates.sort((a, b) => b.q8 - a.q8 || a.site.plot - b.site.plot);
                sample.candidates = candidates.map(({site, q8}) => ({plot: site.plot, q8}));
                if (!scope.apply || (type === scope.farm && candidates.some(({site}) => locationMatches(stock, site))))
                    return frame;
                for (const {site, field, q8} of candidates) {
                    const adjusted = q8 + ADMISSION_BONUS_Q8;
                    if (adjusted > 0x7fffffff || adjusted <= stockQ8) continue;
                    // The selector's third argument filters a resource type.
                    // Raise a single row, then ask stock selection whether it
                    // wins and is unreserved. A repair uses ordinary legality.
                    field.writeS32(adjusted);
                    let retained = false;
                    try {
                        const target = bestLocation(build, scope.farm, -1, site.pillaged ? 0 : 1);
                        if (!locationMatches(target, site)) continue;
                        typeField.writeS32(scope.farm);
                        frame.restore = () => { typeField.writeS32(type); field.writeS32(q8); };
                        sample.adjustedQ8 = adjusted;
                        sample.chosen = site.plot;
                        retained = true;
                        break;
                    } finally {
                        if (!retained) field.writeS32(q8);
                    }
                }
                return frame;
            });
            if (this.sample) active++;
        },
        onLeave() {
            if (!this.sample) return;
            active--;
            guard(() => {
                const {sample, slot, restore} = this.sample;
                if (restore) restore();
                record({...sample, after: slot.readS32()});
            });
        },
    });

    function onSiteWorker(player, controller, site) {
        let node = player.add(PLAYER.units).readPointer().add(UNIT_LIST.head).readPointer();
        for (let count = 0; !node.isNull(); count++, node = node.add(UNIT_LIST.next).readPointer()) {
            if (count === 512) throw Error('Unexpected replay unit roster size');
            const unit = node.readPointer();
            if (unit.add(UNIT.type).readS32() === scope.builder && unit.add(UNIT.control).readS32() === controller
                && unit.add(UNIT.x).readS32() === site.x && unit.add(UNIT.y).readS32() === site.y
                && unit.add(UNIT.departing).readU8() === 0 && unit.add(UNIT.charges).readS32() > 0)
                return unit.add(UNIT.id).readS32();
        }
        return null;
    }
    Interceptor.attach(address(RELEASE_UNITS), {
        onEnter(args) {
            if (!enabled || !armed.size) return;
            this.release = guard(() => {
                const tree = args[0], owner = tree.add(TREE.owner).readPointer();
                if (owner.isNull()) return;
                const player = owner.add(OWNER_PLAYER).readPointer();
                if (player.isNull() || player.add(PLAYER.id).readS32() !== scope.player) return;
                // Check the improvement and city only for the two known replay
                // cities. Equal-priority requests with override retain stock behavior.
                const priority = tree.add(TREE.priority).readS32(), request = args[3].toInt32();
                const holding = tree.add(TREE.value).readS32() >> 8;
                if (tree.add(TREE.allowsRecruit).readU8() === 0 || priority !== args[2].toInt32() || (args[4].toInt32() & 0xff)
                    || request <= holding || request - holding > FINISH_BONUS) return;
                if (tree.add(TREE.kind).readS32() !== scope.farm || !isCity(tree.add(TREE.city).readPointer())) return;
                const plot = tree.add(TREE.plot).readPointer();
                const site = [...armed].map(index => sites.get(index)).find(site => locationMatches(plot, site));
                const controller = tree.add(TREE.control).readS32();
                if (!site || controller < 0 || controller === args[5].toInt32()) return;
                const unit = onSiteWorker(player, controller, site);
                if (unit === null) return;
                if (scope.apply) args[3] = ptr(Math.max(0, request - FINISH_BONUS));
                active++;
                return {kind: 'finish-preference', turn: turn(), plot: site.plot, unit, request, holding, applied: scope.apply};
            });
        },
        onLeave(result) {
            if (!this.release) return;
            active--;
            guard(() => {
                // ReleaseUnits returns the caller-owned vector of offered
                // worker IDs. Native recruitment still has to accept one.
                const count = result.add(0x10).readU32();
                if (count > 512) throw Error('Unexpected release output size');
                const ids = result.readPointer();
                const offered = Array.from({length: count}, (_, index) => ids.add(index * 4).readS32());
                record({...this.release, offered});
            });
        },
    });
    Interceptor.flush();
    return true;
}

rpc.exports = {
    init,
    arm(plots) { armed = new Set(plots); enabled = !fault; },
    freeze() { enabled = false; return {samples, fault, active}; },
};
