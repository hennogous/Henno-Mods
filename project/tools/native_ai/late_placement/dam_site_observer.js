'use strict';

// Windows XP2 hotfix 092abfbb. Observe CheckForDistrict just after its
// GetBestDistrict call. RDI holds CityBuild and RBP+0x40 holds the output XY.
// This caller is outside the two CE detours and all reads are observational.
const BEST_DISTRICT_RETURN = 0x3e0f3c;
const CITY = 0x90, CITY_ID = 0xa8, CITY_OWNER = 0xd8;
const ROWS = 0x4c8, ROW_COUNT = 0x4d8, ROW_SIZE = 0x78;
const ROW_X = 8, ROW_Y = 12, ROW_SCORES = 0x20, ROW_RESERVATION = 0x48;
const ROW_ELIGIBLE = 0x55, ROW_FRONTIER = 0x57, ROW_OWNED = 0x5a;
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
            !bounded(scope.districtCount, 4097) || !bounded(scope.dam, scope.districtCount) ||
            !Array.isArray(scope.plots) || !scope.plots.length || scope.plots.length > 38 ||
            scope.plots.some(plot => !bounded(plot, scope.width * scope.height)))
            throw Error('Expected a verified Dam survey scope');
        const modules = Process.enumerateModules();
        const carriers = modules.filter(module => /GameCore_XP2_(?:CE|CSC)/i.test(module.name));
        const core = modules.find(module => normalize(module.path) === normalize(spec.path));
        if (!core || core.size !== spec.image_size || carriers.length !== 1 ||
            normalize(carriers[0].path) !== normalize(scope.cePath)) throw Error('Unexpected native carrier');
        const address = core.base.add(BEST_DISTRICT_RETURN);
        const expected = 'e8143b00008bd883f8ff0f84e9010000';
        const actual = Array.from(new Uint8Array(address.sub(5).readByteArray(expected.length / 2)),
            byte => byte.toString(16).padStart(2, '0')).join('');
        if (actual !== expected) throw Error('CheckForDistrict call-site fingerprint differs');
        const gameSlot = core.base.add(GAME_INSTANCE_SLOT);
        const targets = new Set(scope.plots);
        Interceptor.attach(address, function () {
            if (!enabled) return;
            try {
                const build = this.context.rdi;
                const city = read(build, CITY, 'ptr');
                if (read(city, CITY_OWNER, 'i32') !== scope.player || read(city, CITY_ID, 'i32') !== scope.city)
                    return;
                if (records.length >= 64) throw Error('Dam survey evidence bound');
                const turn = read(read(gameSlot, 0, 'ptr'), GAME_TURN, 'i32');
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
                        sites.push({plot, q8: scores.isNull() ? null : read(scores, scope.dam * 4, 'i32'),
                            eligible: read(row, ROW_ELIGIBLE, 'u8'), owned: read(row, ROW_OWNED, 'u8'),
                            frontier: read(row, ROW_FRONTIER, 'u8'),
                            reservation: reservation.isNull() ? null : read(reservation, 0, 'i32')});
                    }
                }
                if (winner && winner.q8 === undefined) throw Error('Native winner row is absent');
                records.push({turn, winner, sites});
            } catch (error) {
                enabled = false;
                fault = String(error);
            }
        });
        Interceptor.flush();
        installed = true;
        return true;
    },
    advance() { enabled = true; },
    freeze() { enabled = false; return {records, fault, active: 0}; },
};
