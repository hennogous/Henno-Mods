'use strict';

// Read-only replay scout for Windows XP2 hotfix 092abfbb. At the ordinary
// GetBestDistrict return, screen owned, unreserved Quarter rows for a strict
// margin small enough for the actual CSC weak-site deduction to matter.
// This is a lead for a matched replay, since a NetValue change may affect
// downstream forecasts. No input to the selector or game state is changed.
const SelectorReturnRva = 0x3e0f3c;
const SelectorCallerFingerprint = 'e8143b00008bd883f8ff0f84e9010000';
const CityBuildCity = 0x90;
const CityId = 0xa8;
const CityOwner = 0xd8;
const PlotRows = 0x4c8;
const PlotRowCount = 0x4d8;
const RowSize = 0x78;
const RowX = 0x08;
const RowY = 0x0c;
const RowScores = 0x20;
const RowReservation = 0x48;
const RowEligible = 0x55;
const RowOwned = 0x5a;
const WinnerXY = 0x40;
const GameInstance = 0xb8aa68;
const GameTurn = 0xc0;
const InvalidScoreQ8 = -9999 * 256;
const memory = createStudyMemoryIO({ptr, findRangeByAddress: p => Process.findRangeByAddress(p)});
const records = [];
let listener, fault;
let compared = 0;

function read(address, offset, type) {
    const result = memory.read(address.toString(), offset, type);
    if (result.error) throw Error(`${type} at ${offset}: ${result.error}`);
    return result.value;
}

function readPointer(address, offset) {
    return ptr(read(address, offset, 'ptr'));
}

rpc.exports = {
    init(spec, scope) {
        const normalize = path => path.replace(/\\/g, '/').toLowerCase();
        const modules = Process.enumerateModules();
        const core = modules.find(module => normalize(module.path) === normalize(spec.path));
        const carrier = modules.find(module => normalize(module.path) === normalize(scope.cePath));
        if (listener || Process.platform !== 'windows' || Process.arch !== 'x64' ||
            !core || core.size !== spec.image_size || !carrier ||
            !Number.isInteger(scope.width) || scope.width < 1 || scope.width > 256 ||
            !Number.isInteger(scope.height) || scope.height < 1 || scope.height > 256 ||
            !Array.isArray(scope.sites) || scope.sites.length > 4096)
            throw Error('Unexpected native district scout scope');
        const targets = new Map();
        for (const site of scope.sites) {
            if (!Number.isInteger(site.district) || site.district < 1 || site.district >= scope.districtCount ||
                !Number.isInteger(site.plot) || site.plot < 0 || site.plot >= scope.width * scope.height ||
                ![-65536, -32768].includes(site.delta))
                throw Error('Invalid Quarter deduction');
            const key = `${site.player}:${site.city}`;
            if (!targets.has(key)) targets.set(key, new Map());
            const byPlot = targets.get(key);
            if (!byPlot.has(site.plot)) byPlot.set(site.plot, []);
            byPlot.get(site.plot).push(site);
        }
        const address = core.base.add(SelectorReturnRva);
        const actual = Array.from(new Uint8Array(address.sub(5).readByteArray(
            SelectorCallerFingerprint.length / 2)), b => b.toString(16).padStart(2, '0')).join('');
        if (actual !== SelectorCallerFingerprint) throw Error('District selector fingerprint differs');
        const gameSlot = core.base.add(GameInstance);
        listener = Interceptor.attach(address, function () {
            if (fault) return;
            try {
                const build = this.context.rdi;
                const city = readPointer(build, CityBuildCity);
                const siteMap = targets.get(`${read(city, CityOwner, 'i32')}:${read(city, CityId, 'i32')}`);
                if (!siteMap) return;
                ++compared;
                const type = this.context.rax.toInt32();
                if (type < 0) return;
                if (type >= scope.districtCount) throw Error('Unexpected winner type');
                const x = read(this.context.rbp, WinnerXY, 'i32');
                const y = read(this.context.rbp, WinnerXY + 4, 'i32');
                const winnerPlot = y * scope.width + x;
                const rows = readPointer(build, PlotRows);
                const count = read(build, PlotRowCount, 'u32');
                if (count > 37) throw Error('Unexpected CityBuild row count');
                let winner;
                const candidates = [];
                for (let index = 0; index < count; ++index) {
                    const row = rows.add(index * RowSize);
                    const rx = read(row, RowX, 'i32'), ry = read(row, RowY, 'i32');
                    if (rx < 0 || rx >= scope.width || ry < 0 || ry >= scope.height) continue;
                    const plot = ry * scope.width + rx;
                    if (plot === winnerPlot)
                        winner = read(readPointer(row, RowScores), type * 4, 'i32');
                    const sites = siteMap.get(plot);
                    if (!sites || !read(row, RowEligible, 'u8') || !read(row, RowOwned, 'u8')) continue;
                    const reservation = readPointer(row, RowReservation);
                    // The selector's unreserved row takes the default
                    // threshold. Leave any other handle for a focused trace.
                    if (reservation.isNull() || read(reservation, 0, 'i32') !== -1) continue;
                    const scores = readPointer(row, RowScores);
                    for (const site of sites) {
                        if (plot === winnerPlot && site.district === type) continue;
                        const q8 = read(scores, site.district * 4, 'i32');
                        if (q8 > InvalidScoreQ8) candidates.push({...site, q8});
                    }
                }
                if (winner === undefined) throw Error('Native winner row is missing');
                const turn = read(readPointer(gameSlot, 0), GameTurn, 'i32');
                for (const site of candidates) {
                    const gap = winner - site.q8;
                    if (gap >= 0 && gap < -site.delta) {
                        if (records.length >= 512) throw Error('Native scout trace capacity');
                        records.push({turn, site, winner: {district: type, plot: winnerPlot, q8: winner}, gap});
                    }
                }
            } catch (error) {
                fault = String(error);
            }
        });
        Interceptor.flush();
        return true;
    },
    freeze() {
        if (listener) listener.detach();
        return {records, compared, fault: fault || null};
    },
};
