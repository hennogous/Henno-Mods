'use strict';

// Purchase evidence for the audited Windows XP2 hotfix 092abfbb.
// Four sites are inside the plot branch of Purchase::Start (680f70).
// RDI is the buying City; RBP+0x67/0x6b hold its target XY throughout.
// The quote is whole Gold. The debit's low signed dword is Q8 Gold.
// The returned debit call records its preserved argument, not a measured
// treasury balance change. Pair command receipts with Gameplay ownership.
// Two earlier sites in Economic::TryPurchasePlot (459090) expose each city's
// quote and the selected city's savings gates. They do not submit a purchase.
// Default mode is read-only. Explicit Szeged prototype mode can exclude a
// competing buyer by changing its positive quote result to -1, after proving
// the selected Quarter/site and contract's originating city. It never changes
// price calculation, funds, payment or ownership directly. This is diagnostic
// tooling, not CSC shipping policy or a finished CE lifecycle implementation.
const PlotQuoteReturn = 0x681346;
const GoldDebitCall = 0x681379;
const GoldDebitReturn = 0x68137e;
const PlotAnnexReturn = 0x6813a2;
const TargetedCityQuoteReturn = 0x459169;
const TargetedSavingsCheck = 0x45918f;
// TryPurchasePlot saves its original Economic receiver at entry RSP+8.
// Seven pushes and its 0x80-byte frame put that slot at RSP+0xc0 here.
// The slot is overwritten later in this routine: read only at 45918f.
// Names/offsets come from 092abfbb's byte-matched reference, constructor,
// DoTurnActivate and Spend (AI-N114). Read failures latch a diagnostic fault;
// no guessed zero balance is emitted and no target memory is written.
const EconomicReceiverOnStack = 0xc0;
const EconomicPlayerOffset = 0x98;
const EconomicAccountedBalanceOffset = 0x120;
const EconomicTotalWeightOffset = 0x1c8;
const EconomicWeightsOffset = 0x1e0;
const EconomicWeightsCountOffset = 0x1f0;
const EconomicSavingsOffset = 0x250;
const PlayerTreasuryOffset = 0x780;
const TreasuryGoldOffset = 0xa8;
// Optional read-only lineage for fresh district plans. These midpoints follow
// tree installation and purchase-contract initialization, before registers are
// reused. They add no purchase, required buyer or native call. Reloaded plans
// with no observed creation remain explicitly unknown.
const DistrictTreeInstalled = 0x3e10fd; // RDI CityBuild, RBX child tree, ESI root tree ID.
const PurchaseInitialized = 0x55dc9f; // R15 contract, RSI executing tree, RBP player.
const CityBuildCityOffset = 0x90;
const TreeParentOffset = 0x120;
const TreeControlOffset = 0x1b0;
const TreeIdOffset = 0x1c8;
const ContractIdOffset = 0x110;
const ContractControlOffset = 0x128;
const ContractPlayerOffset = 0x140;
const ContractTargetOffset = 0x178;
const PlayerIdOffset = 0xd8;
const DistrictSelectionReturn = 0x3e0f3c; // RAX district, RDI CityBuild, RBP+40 XY.
const DistrictSelectionXY = 0x40;
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
        const prototypeBuyer = scope.prototypeBuyer;
        if (prototypeBuyer !== undefined && prototypeBuyer !== null &&
            (!['observe', 'restrict'].includes(prototypeBuyer) || scope.observeLineage !== true ||
                scope.player !== 2 || scope.city !== 589829 || scope.district !== 37 ||
                targets.size !== 1 || !targets.has(1365) || scope.selectorObserverVerified !== true))
            throw Error('Unexpected required-buyer prototype scope');
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
        fingerprint(0x459095, '48894c2408'); // Saved Economic receiver.
        fingerprint(0x4590a5, '4881ec80000000488be9'); // Audited frame size.
        const createdTrees = new Map(), knownContracts = new Map(), pendingSelections = new Map();
        const emit = receipt => {
            if (records.length >= 512) throw Error('Purchase trace capacity');
            records.push(receipt);
            if (scope.streamRecords) send({kind: 'plot-purchase-receipt', receipt});
        };
        const fail = error => {
            fault = String(error);
            if (scope.streamRecords) send({kind: 'plot-purchase-fault', fault});
        };
        const turnNow = () => read(ptr(read(gameSlot, 0, 'ptr')), GameTurnOffset, 'i32');
        const ancestry = tree => {
            const path = [], seen = new Set();
            while (!tree.isNull()) {
                const key = tree.toString();
                if (seen.has(key) || path.length >= 32) throw Error('Invalid purchase tree ancestry');
                seen.add(key); path.push(tree);
                const parent = ptr(read(tree, TreeParentOffset, 'ptr'));
                if (parent.isNull()) return {path, root: tree};
                tree = parent;
            }
            throw Error('Missing purchase tree');
        };
        const validatedContract = targetPointer => {
            const binding = knownContracts.get(targetPointer.toString());
            if (!binding) return null;
            const contract = ptr(binding.contract);
            if (read(contract, ContractIdOffset, 'i32') !== binding.contractId ||
                read(contract, ContractControlOffset, 'i32') !== binding.ownerControl ||
                read(contract, ContractPlayerOffset, 'i32') !== scope.player ||
                read(contract, ContractTargetOffset, 'i32') !== binding.x ||
                read(contract, ContractTargetOffset + 4, 'i32') !== binding.y)
                throw Error('Retained purchase contract identity changed');
            return binding;
        };
        if (prototypeBuyer) {
            // The already initialized selector observer verified the complete
            // original call/return window, then Frida patched the return point.
            // Verify the untouched call and XY initialization here, and attach
            // another listener to that same Frida interception point. Checking
            // the original return bytes again would reject our own first hook.
            fingerprint(DistrictSelectionReturn - 5, 'e8143b0000');
            fingerprint(0x3e0f29, 'c74540f1d8ffffc74544f1d8ffff');
            listeners.push(Interceptor.attach(core.base.add(DistrictSelectionReturn), function () {
                if (fault) return;
                try {
                    // Every selector return invalidates that thread's older
                    // selection, including failures and another city's call.
                    // Installation must consume the same build/frame/turn.
                    pendingSelections.delete(this.threadId);
                    if (!Number.isInteger(this.threadId)) throw Error('Missing selector thread identity');
                    const city = ptr(read(this.context.rdi, CityBuildCityOffset, 'ptr'));
                    if (read(city, CityOwnerOffset, 'i32') !== scope.player ||
                        read(city, CityIdOffset, 'i32') !== scope.city) return;
                    const district = this.context.rax.toInt32();
                    if (district < -1 || district >= 4096) throw Error('Invalid selected district');
                    const selection = {turn: turnNow(), build: this.context.rdi.toString(),
                        frame: this.context.rbp.toString(), district, plot: null};
                    if (district !== -1) {
                        const x = read(this.context.rbp, DistrictSelectionXY, 'i32');
                        const y = read(this.context.rbp, DistrictSelectionXY + 4, 'i32');
                        if (x < 0 || x >= scope.width || y < 0 || y >= scope.height)
                            throw Error('Invalid district selection target');
                        selection.plot = y * scope.width + x;
                        if (pendingSelections.size >= 16) throw Error('Selector binding capacity');
                        pendingSelections.set(this.threadId, selection);
                    }
                    emit({kind: 'buyer-prototype-selection', player: scope.player, city: scope.city, ...selection});
                } catch (error) { fail(error); }
            }));
        }
        if (scope.observeLineage === true) {
            if (!Number.isInteger(scope.city) || scope.city < 0) throw Error('Missing lineage city scope');
            fingerprint(DistrictTreeInstalled, '488d8b70020000440fb64540');
            fingerprint(PurchaseInitialized, '488bd0488d4c2430e834f8e9ff');
            listeners.push(Interceptor.attach(core.base.add(DistrictTreeInstalled), function () {
                if (fault) return;
                try {
                    const city = ptr(read(this.context.rdi, CityBuildCityOffset, 'ptr'));
                    if (read(city, CityOwnerOffset, 'i32') !== scope.player ||
                        read(city, CityIdOffset, 'i32') !== scope.city) return;
                    const tree = this.context.rbx, chain = ancestry(tree);
                    const treeId = read(chain.root, TreeIdOffset, 'i32');
                    if (treeId !== this.context.rsi.toInt32()) throw Error('Installed root tree identity differs');
                    if (createdTrees.size >= 64) throw Error('District tree binding capacity');
                    const binding = {city: scope.city, treeId, tree: tree.toString(),
                        root: chain.root.toString(), control: read(chain.root, TreeControlOffset, 'i32')};
                    if (prototypeBuyer) {
                        const pending = pendingSelections.get(this.threadId);
                        pendingSelections.delete(this.threadId);
                        binding.selection = pending && pending.build === this.context.rdi.toString() &&
                            pending.frame === this.context.rbp.toString() && pending.turn === turnNow() ? pending : null;
                    }
                    createdTrees.set(tree.toString(), binding);
                    emit({kind: 'district-tree-created', turn: turnNow(), player: scope.player, ...binding});
                } catch (error) { fail(error); }
            }));
            listeners.push(Interceptor.attach(core.base.add(PurchaseInitialized), function () {
                if (fault) return;
                try {
                    if (read(this.context.rbp, PlayerIdOffset, 'i32') !== scope.player) return;
                    const contract = this.context.r15;
                    const x = read(contract, ContractTargetOffset, 'i32');
                    const y = read(contract, ContractTargetOffset + 4, 'i32');
                    if (x < 0 || x >= scope.width || y < 0 || y >= scope.height) throw Error('Invalid contract target');
                    const plot = y * scope.width + x;
                    if (!targets.has(plot)) return;
                    const chain = ancestry(this.context.rsi);
                    const ownerControl = read(contract, ContractControlOffset, 'i32');
                    const rootTreeId = read(chain.root, TreeIdOffset, 'i32');
                    // Control IDs are not city IDs. Join only an observed
                    // creation on this ancestry with the same root identity;
                    // pointer reuse or an unobserved/reloaded tree is unknown.
                    const origins = chain.path.map(tree => createdTrees.get(tree.toString()))
                        .filter(origin => origin && origin.treeId === rootTreeId &&
                            origin.root === chain.root.toString() && origin.control === ownerControl);
                    const cities = [...new Set(origins.map(origin => origin.city))];
                    if (read(contract, ContractPlayerOffset, 'i32') !== scope.player ||
                        ownerControl !== read(chain.root, TreeControlOffset, 'i32'))
                        throw Error('Purchase contract/root owner differs');
                    const binding = {contract: contract.toString(), contractId: read(contract, ContractIdOffset, 'i32'),
                        ownerControl, plot, x, y, rootTreeId,
                        executingTree: this.context.rsi.toString(), originCity: cities.length === 1 ? cities[0] : null};
                    if (prototypeBuyer) {
                        // The nearest observed ancestor must be this exact
                        // invocation's selected Quarter and target. An old
                        // matching ancestor cannot authorize a different plan.
                        const selection = origins[0] && origins[0].selection;
                        binding.requiredBuyerAuthorized = binding.originCity === scope.city &&
                            !!selection && selection.district === scope.district && selection.plot === plot;
                        binding.selectedDistrict = selection ? selection.district : null;
                    }
                    if (knownContracts.size >= 64) throw Error('Purchase binding capacity');
                    knownContracts.set(contract.add(ContractTargetOffset).toString(), binding);
                    emit({kind: 'purchase-contract-created', turn: turnNow(), player: scope.player, ...binding});
                } catch (error) { fail(error); }
            }));
        }
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
            context => {
                const originalGold = context.rax.toInt32();
                if (!prototypeBuyer) return {gold: originalGold};
                const binding = validatedContract(context.r12);
                const authorized = !!binding && binding.requiredBuyerAuthorized === true &&
                    binding.originCity === scope.city && binding.selectedDistrict === scope.district;
                const buyerCity = read(context.rbp, CityIdOffset, 'i32');
                const excluded = prototypeBuyer === 'restrict' && authorized &&
                    originalGold > 0 && buyerCity !== binding.originCity;
                // All identity/read/capacity validation happens before this
                // sole register write. It is just ahead of TEST/JLE and the
                // cheapest-positive comparison. Preserve the intended quote,
                // including rejection, and leave every unrelated request alone.
                const gold = excluded ? -1 : originalGold;
                const receipt = {gold, originalGold, buyerRestriction: prototypeBuyer,
                    bindingKnown: !!binding, authorized, excluded,
                    requiredBuyer: authorized ? binding.originCity : null,
                    contractId: binding ? binding.contractId : null};
                if (excluded) context.rax = ptr(-1);
                // A later diagnostic fault invalidates this run; it cannot
                // undo exclusions already made in this native attempt.
                return receipt;
            });
        attach(TargetedSavingsCheck, 'targeted-savings', targetedLocation('r14'), context => {
            const plotFund = ptr(read(context.rsp, 0xd0, 'ptr'));
            const slushFund = ptr(read(context.rsp, 0xd8, 'ptr'));
            const plotQ8 = read(plotFund, 0, 'i32');
            const slushQ8 = read(slushFund, 0, 'i32');
            const gold = context.r15.toInt32();
            const factorQ8 = context.rdi.toInt32();
            const minimumPlotFundQ8 = gold * factorQ8;
            let lineage;
            if (scope.observeLineage === true) {
                // Match an observed live target pointer; never infer an object
                // by subtracting a guessed offset from an arbitrary XY pointer.
                const binding = validatedContract(context.r12);
                lineage = {known: false};
                if (binding) {
                    lineage = {known: true, contractId: binding.contractId, ownerControl: binding.ownerControl,
                        originCity: binding.originCity, rootTreeId: binding.rootTreeId};
                }
            }
            const economic = ptr(read(context.rsp, EconomicReceiverOnStack, 'ptr'));
            const savings = ptr(read(economic, EconomicSavingsOffset, 'ptr'));
            // Match the saved receiver to the same live funds being tested.
            // A readable unrelated pointer must not qualify as Economic.
            if (savings.toString() !== slushFund.toString() ||
                savings.add(8).toString() !== plotFund.toString() ||
                read(economic, EconomicWeightsCountOffset, 'i32') !== 4)
                throw Error('Economic receiver/fund layout differs');
            const player = ptr(read(economic, EconomicPlayerOffset, 'ptr'));
            const treasury = ptr(read(player, PlayerTreasuryOffset, 'ptr'));
            const treasuryQ8 = read(treasury, TreasuryGoldOffset, 'i32');
            const accountedQ8 = read(economic, EconomicAccountedBalanceOffset, 'i32');
            const weights = ptr(read(economic, EconomicWeightsOffset, 'ptr'));
            const savingsQ8 = [0, 4, 8, 12].map(offset => read(savings, offset, 'i32'));
            const savingWeights = [0, 4, 8, 12].map(offset => read(weights, offset, 'i32'));
            const totalWeight = read(economic, EconomicTotalWeightOffset, 'i32');
            if (savingWeights.some(weight => weight < 0) || totalWeight <= 0 ||
                savingWeights.reduce((sum, weight) => sum + weight, 0) !== totalWeight)
                throw Error('Unexpected Economic saving weights');
            // These predicates reconstruct the next native checks. They do
            // not claim the branch ran, nor that command validation passed.
            // Restrict the arithmetic to the non-overflow range seen in the
            // audited signed-Q8 path before using JS's exact integer numbers.
            if (gold <= 0 || gold > 0x7fffff || factorQ8 < 0 || factorQ8 > 256 ||
                plotQ8 + slushQ8 > 0x7fffffff || plotQ8 + slushQ8 < -0x80000000)
                throw Error('Unexpected targeted purchase arithmetic range');
            return {gold, plotQ8, slushQ8, factorQ8, minimumPlotFundQ8,
                treasuryQ8, accountedQ8, unaccountedQ8: treasuryQ8 - accountedQ8,
                savingsQ8, savingWeights, totalWeight, ...(lineage ? {lineage} : {}),
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
