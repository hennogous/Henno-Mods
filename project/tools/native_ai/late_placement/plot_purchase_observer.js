'use strict';

// Read-only purchase evidence for the audited Windows XP2 hotfix 092abfbb.
// Four sites are inside the plot branch of Purchase::Start (680f70).
// RDI is the buying City; RBP+0x67/0x6b hold its target XY throughout.
// The quote is whole Gold. The debit's low signed dword is Q8 Gold.
// The returned debit call records its preserved argument, not a measured
// treasury balance change. Pair command receipts with Gameplay ownership.
// Two earlier sites in Economic::TryPurchasePlot (459090) expose each city's
// quote and the selected city's savings gates. They do not submit a purchase.
// All callbacks are read-only diagnostics, never CSC shipping policy.
const PlotQuoteReturn = 0x681346;
const GoldDebitCall = 0x681379;
const GoldDebitReturn = 0x68137e;
const PlotAnnexReturn = 0x6813a2;
const TargetedCityQuoteReturn = 0x459169;
const TargetedSavingsCheck = 0x45918f;
const CityIdOffset = 0xa8;
const CityOwnerOffset = 0xd8;
const TargetXOnFrame = 0x67;
const TargetYOnFrame = 0x6b;
const GameInstanceSlot = 0xb8aa68;
const GameTurnOffset = 0xc0;
const memory = createStudyMemoryIO({ptr, findRangeByAddress: p => Process.findRangeByAddress(p)});
const listeners = [];
const records = [];
let fault = null;

function read(address, offset, type) {
    const result = memory.read(address.toString(), offset, type);
    if (result.error) throw Error(`${type} at ${offset}: ${result.error}`);
    return result.value;
}

rpc.exports = {
    init(spec, scope) {
        const normalize = path => path.replace(/\\/g, '/').toLowerCase();
        const core = Process.enumerateModules().find(m => normalize(m.path) === normalize(spec.path));
        if (listeners.length || Process.platform !== 'windows' || Process.arch !== 'x64' ||
            !core || core.size !== spec.image_size || !Array.isArray(scope.plots) ||
            !scope.plots.length || scope.plots.length > 36 ||
            !Number.isInteger(scope.width) || scope.width < 1 || scope.width > 256 ||
            !Number.isInteger(scope.height) || scope.height < 1 || scope.height > 256 ||
            scope.plots.some(plot => !Number.isInteger(plot) || plot < 0 || plot >= scope.width * scope.height) ||
            !Number.isInteger(scope.player) || scope.player < 0 || scope.player >= 64)
            throw Error('Unexpected plot purchase observation scope');
        const targets = new Set(scope.plots);
        const gameSlot = core.base.add(GameInstanceSlot);
        const fingerprint = (rva, expected) => {
            const actual = Array.from(new Uint8Array(core.base.add(rva).readByteArray(expected.length / 2)),
                b => b.toString(16).padStart(2, '0')).join('');
            if (actual !== expected) throw Error(`Purchase fingerprint differs at ${rva.toString(16)}`);
        };
        fingerprint(PlotQuoteReturn, '8bf085c00f8eca000000');
        fingerprint(GoldDebitCall, 'e8621fccff8b4567488d8f800b0000');
        fingerprint(PlotAnnexReturn, '0fb787d80000004c8d4567');
        fingerprint(TargetedCityQuoteReturn, '85c07e104d85f67405');
        fingerprint(TargetedSavingsCheck, '488bac24d0000000418bdfc1e308');
        const commandLocation = context => ({city: context.rdi,
            x: read(context.rbp, TargetXOnFrame, 'i32'),
            y: read(context.rbp, TargetYOnFrame, 'i32')});
        // At both Economic sites R12 still points to the requested XY.
        // RBP is the quoted City at 459169; R14 is the cheapest positive
        // quote's City at 45918f. Stack slots hold the saved Q8 fund pointers.
        const targetedLocation = cityRegister => context => ({city: context[cityRegister],
            x: read(context.r12, 0, 'i32'), y: read(context.r12, 4, 'i32')});
        const attach = (rva, kind, locate, value, allPlots = false) => {
            listeners.push(Interceptor.attach(core.base.add(rva), function () {
                if (fault) return;
                try {
                    const {city, x, y} = locate(this.context);
                    const player = read(city, CityOwnerOffset, 'i32');
                    if (player !== scope.player) return;
                    if (x < 0 || x >= scope.width || y < 0 || y >= scope.height)
                        throw Error('Invalid purchase coordinates');
                    const plot = y * scope.width + x;
                    if (!targets.has(plot) && !allPlots) return;
                    if (records.length >= 512) throw Error('Purchase trace capacity');
                    const turn = read(ptr(read(gameSlot, 0, 'ptr')), GameTurnOffset, 'i32');
                    const receipt = {kind, turn, player, city: read(city, CityIdOffset, 'i32'), plot};
                    if (value) Object.assign(receipt, value(this.context));
                    records.push(receipt);
                    // Stream bounded observations to the host immediately.
                    // A machine/worker interruption can bypass finally and
                    // must not discard every receipt before endpoint freeze.
                    if (scope.streamRecords) send({kind: 'plot-purchase-receipt', receipt});
                } catch (error) {
                    fault = String(error);
                    if (scope.streamRecords) send({kind: 'plot-purchase-fault', fault});
                }
            }));
        };
        const allCommandPlots = scope.allCommandPlots === true;
        attach(PlotQuoteReturn, 'quote', commandLocation,
            context => ({gold: context.rax.toInt32()}), allCommandPlots);
        attach(GoldDebitCall, 'debit-call', commandLocation,
            context => ({deltaQ8: read(context.rdx, 0, 'i32')}), allCommandPlots);
        attach(GoldDebitReturn, 'debit-return', commandLocation,
            context => ({deltaQ8: context.rsi.toInt32()}), allCommandPlots);
        attach(PlotAnnexReturn, 'annex-return', commandLocation, null, allCommandPlots);
        attach(TargetedCityQuoteReturn, 'targeted-city-quote', targetedLocation('rbp'),
            context => ({gold: context.rax.toInt32()}));
        attach(TargetedSavingsCheck, 'targeted-savings', targetedLocation('r14'), context => {
            const plotFund = ptr(read(context.rsp, 0xd0, 'ptr'));
            const slushFund = ptr(read(context.rsp, 0xd8, 'ptr'));
            const plotQ8 = read(plotFund, 0, 'i32');
            const slushQ8 = read(slushFund, 0, 'i32');
            const gold = context.r15.toInt32();
            const factorQ8 = context.rdi.toInt32();
            const minimumPlotFundQ8 = gold * factorQ8;
            // These predicates reconstruct the next native checks. They do
            // not claim the branch ran, nor that command validation passed.
            // Restrict the arithmetic to the non-overflow range seen in the
            // audited signed-Q8 path before using JS's exact integer numbers.
            if (gold <= 0 || gold > 0x7fffff || factorQ8 < 0 || factorQ8 > 256 ||
                plotQ8 + slushQ8 > 0x7fffffff || plotQ8 + slushQ8 < -0x80000000)
                throw Error('Unexpected targeted purchase arithmetic range');
            return {gold, plotQ8, slushQ8, factorQ8, minimumPlotFundQ8,
                passesPlotFund: plotQ8 >= minimumPlotFundQ8,
                passesCombinedFunds: gold <= Math.floor((plotQ8 + slushQ8) / 256)};
        });
        Interceptor.flush();
        return true;
    },
    freeze() {
        for (const listener of listeners) listener.detach();
        return {records, fault};
    },
};
