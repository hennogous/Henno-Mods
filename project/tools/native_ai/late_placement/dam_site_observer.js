'use strict';

// Windows XP2 hotfix 092abfbb. Observe CheckForDistrict just after its
// GetBestDistrict call. RDI holds CityBuild and RBP+0x40 holds the output XY.
// This caller is outside the two CE detours. The separate matched repair
// treatment is opt-in. Dam and selector-only probes are read-only.
// The scope supplies either legal Dam footprints or an existing Quarter.
const BEST_DISTRICT_RETURN = 0x3e0f3c;
const CHECK_FOR_DISTRICT = 0x3e0ee0;
const GET_BEST_DISTRICT_THRESHOLD = 0x3e4b19;
const DEFAULT_DISTRICT_THRESHOLD = 0xb66cb0;
const CITY = 0x90, CITY_ID = 0xa8, CITY_OWNER = 0xd8;
const ROWS = 0x4c8, ROW_COUNT = 0x4d8, ROW_SIZE = 0x78;
const ROW_X = 8, ROW_Y = 12, ROW_SCORES = 0x20, ROW_RESERVATION = 0x48;
const ROW_ELIGIBLE = 0x55, ROW_FRONTIER = 0x57, ROW_OWNED = 0x5a;
const DISTRICT_TREE = 0x430, TREE_ID = 8;
const WINNER_XY = 0x40;
const GAME_INSTANCE_SLOT = 0xb8aa68, GAME_TURN = 0xc0;
const memory = createStudyMemoryIO({ptr, findRangeByAddress: address => Process.findRangeByAddress(address)});
const records = [];
let installed = false, enabled = false, fault = null;

function read(address, offset, type) {
    const result = memory.read(address.toString(), offset, type);
    if (result.error) throw Error(`${type} at ${offset}: ${result.error}`);
    return result.value;
}

rpc.exports = {
    init(spec, scope) {
        const normalize = path => path.replace(/\\/g, '/').toLowerCase();
        const bounded = (number, limit) => Number.isInteger(number) && number >= 0 && number < limit;
        if (installed || Process.platform !== 'windows' || Process.arch !== 'x64' || Process.pointerSize !== 8 ||
            !bounded(scope.player, 64) || !bounded(scope.city, 0x80000000) ||
            !bounded(scope.width, 257) || !bounded(scope.height, 257) || !scope.width || !scope.height ||
            !bounded(scope.districtCount, 4097) || !bounded(scope.district, scope.districtCount) ||
            !Array.isArray(scope.plots) || !scope.plots.length || scope.plots.length > 38 ||
            scope.plots.some(plot => !bounded(plot, scope.width * scope.height)))
            throw Error('Expected a verified district selector scope');
        const modules = Process.enumerateModules();
        const carriers = modules.filter(module => /GameCore_XP2_(?:CE|CSC)/i.test(module.name));
        const core = modules.find(module => normalize(module.path) === normalize(spec.path));
        if (!core || core.size !== spec.image_size || carriers.length !== 1 ||
            normalize(carriers[0].path) !== normalize(scope.cePath)) throw Error('Unexpected native carrier');
        const address = core.base.add(BEST_DISTRICT_RETURN);
        const fingerprint = (point, expected) => {
            const actual = Array.from(new Uint8Array(point.readByteArray(expected.length / 2)),
                byte => byte.toString(16).padStart(2, '0')).join('');
            if (actual !== expected) throw Error(`District selector fingerprint differs at ${point}`);
        };
        fingerprint(address.sub(5), 'e8143b00008bd883f8ff0f84e9010000');
        const gameSlot = core.base.add(GAME_INSTANCE_SLOT);
        const targets = new Set(scope.plots);
        const currentTurn = () => read(read(gameSlot, 0, 'ptr'), GAME_TURN, 'i32');
        const record = receipt => {
            if (records.length >= 64) throw Error('District selector evidence bound');
            records.push(receipt);
            if (scope.offerRepair && receipt.kind.startsWith('repair-'))
                send({kind: 'quarter-repair-receipt', receipt});
        };
        const isTarget = build => {
            const city = read(build, CITY, 'ptr');
            return read(city, CITY_OWNER, 'i32') === scope.player && read(city, CITY_ID, 'i32') === scope.city;
        };
        const protect = callback => {
            if (!enabled) return;
            try { callback(); }
            catch (error) { enabled = false; fault = String(error); }
        };
        const offerRepair = scope.offerRepair ? makeQuarterRepairOffer(core, scope, fingerprint,
            currentTurn, record, protect) : null;
        if (scope.traceTree) {
            const check = core.base.add(CHECK_FOR_DISTRICT);
            const threshold = core.base.add(GET_BEST_DISTRICT_THRESHOLD);
            const defaultThreshold = core.base.add(DEFAULT_DISTRICT_THRESHOLD);
            fingerprint(check, '405557488d6c24d84881ec28010000488b8130040000');
            fingerprint(threshold.sub(22), '4885c0740a488b46484883c004eb07488d05972178008b384533f633ed4d85ff');
            Interceptor.attach(check, {
                onEnter(args) {
                    protect(() => {
                        if (!isTarget(args[0])) return;
                        const tree = read(args[0], DISTRICT_TREE, 'ptr');
                        const id = read(tree, TREE_ID, 'i32'), turn = currentTurn();
                        record({kind: 'check', turn, tree: id});
                        if (offerRepair && id === -1 && turn === 201) this.repairBuild = args[0];
                    });
                },
                onLeave() {
                    if (!this.repairBuild) return;
                    protect(() => {
                        const selection = records.find(row => row.kind === 'selection' && row.turn === 201);
                        const threshold = records.find(row => row.kind === 'threshold' && row.turn === 201);
                        if (!selection) throw Error('The matched turn-201 district comparison did not occur');
                        const tree = read(this.repairBuild, DISTRICT_TREE, 'ptr');
                        offerRepair(this.repairBuild, read(tree, TREE_ID, 'i32'), selection, threshold);
                    });
                },
            });
            // The selector has resolved the row's reservation through Manager::Find.
            // RAX addresses the threshold it will actually compare, RSI the row,
            // and RBP still holds CityBuild before reuse by the district-type loop.
            Interceptor.attach(threshold, function () {
                protect(() => {
                    const row = this.context.rsi;
                    const x = read(row, ROW_X, 'i32'), y = read(row, ROW_Y, 'i32');
                    const plot = y * scope.width + x;
                    if (!targets.has(plot) || !isTarget(this.context.rbp)) return;
                    const thresholdValue = this.context.rax;
                    record({kind: 'threshold', turn: currentTurn(), plot,
                        liveReservation: !thresholdValue.equals(defaultThreshold),
                        minimumExclusiveQ8: read(thresholdValue, 0, 'i32')});
                });
            });
        }
        Interceptor.attach(address, function () {
            protect(() => {
                const build = this.context.rdi;
                if (!isTarget(build)) return;
                const turn = currentTurn();
                const district = this.context.rax.toInt32();
                const winner = district === -1 ? null : {
                    district, x: read(this.context.rbp, WINNER_XY, 'i32'),
                    y: read(this.context.rbp, WINNER_XY + 4, 'i32'),
                };
                if (winner && (!bounded(district, scope.districtCount) ||
                    !bounded(winner.x, scope.width) || !bounded(winner.y, scope.height)))
                    throw Error('Unexpected native district winner');
                const count = read(build, ROW_COUNT, 'u32');
                if (count > 37) throw Error('Unexpected CityBuild row count');
                const rows = ptr(read(build, ROWS, 'ptr'));
                const sites = [];
                for (let index = 0; index < count; index++) {
                    const row = rows.add(index * ROW_SIZE);
                    const x = read(row, ROW_X, 'i32'), y = read(row, ROW_Y, 'i32');
                    if (!bounded(x, scope.width) || !bounded(y, scope.height)) continue;
                    const plot = y * scope.width + x;
                    if (!targets.has(plot) && !(winner && winner.x === x && winner.y === y)) continue;
                    const scores = ptr(read(row, ROW_SCORES, 'ptr'));
                    if (winner && winner.x === x && winner.y === y)
                        winner.q8 = read(scores, district * 4, 'i32');
                    if (targets.has(plot)) {
                        const reservation = ptr(read(row, ROW_RESERVATION, 'ptr'));
                        sites.push({plot, q8: scores.isNull() ? null : read(scores, scope.district * 4, 'i32'),
                            eligible: read(row, ROW_ELIGIBLE, 'u8'), owned: read(row, ROW_OWNED, 'u8'),
                            frontier: read(row, ROW_FRONTIER, 'u8'),
                            reservation: reservation.isNull() ? null : read(reservation, 0, 'i32')});
                    }
                }
                if (winner && winner.q8 === undefined) throw Error('Native winner row is absent');
                record({kind: 'selection', turn, winner, sites});
            });
        });
        Interceptor.flush();
        installed = true;
        return true;
    },
    advance() { enabled = true; },
    freeze() { enabled = false; return {records, fault, active: 0}; },
};
