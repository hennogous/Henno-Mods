'use strict';

// Purchase evidence for the audited Windows XP2 hotfix 092abfbb.
// Four sites per implementation are inside the plot branch of Purchase::Start.
// Expansion games can dispatch XP1::Purchase::Start (71c3b0), not the base
// implementation (680f70). Nuremberg's live Annex caller71c69a exposed that
// coverage gap. Both implementations are independently fingerprinted below.
// RDI is the buying City; frame locations and preserved registers differ.
// The quote is whole Gold. The debit's low signed dword is Q8 Gold.
// At the existing debit call/return boundaries, pair thread+stack+city+XY and
// measure the receiver's Treasury balance. The preserved argument alone is
// not payment evidence. Pair measured payment with Gameplay city ownership.
// Two earlier sites in Economic::TryPurchasePlot (459090) expose each city's
// quote and the selected city's savings gates. They do not submit a purchase.
// Default mode is read-only. Explicit Szeged prototype mode can exclude a
// competing buyer by changing its positive quote result to -1, after proving
// the selected Quarter/site and contract's originating city. It never changes
// price calculation, funds, payment or ownership directly. This is diagnostic
// tooling, not CSC shipping policy or a finished CE lifecycle implementation.
// The separate explicit repairOwnedPurchase experiment may acknowledge a paid,
// correctly owned contract through the tracked native setter. Default remains
// read-only. That experiment is not evidence of a dynamically integrated fix.
const PlotQuoteReturn = 0x681346;
const GoldDebitCall = 0x681379;
const GoldDebitReturn = 0x68137e;
const PlotAnnexReturn = 0x6813a2;
// XP1 ABI verified against reference SHA324c51e9 text matching hotfix092abfbb:
// RDI=City, R15=Treasury, EBX=negativeQ8 debit after the call; XY=RBP+38/+3c.
// Observe both dispatch targets without changing the handler or game state.
const PurchaseHandlers = [
    {name:'base',quote:PlotQuoteReturn,debit:GoldDebitCall,returned:GoldDebitReturn,
        annex:PlotAnnexReturn,x:0x67,y:0x6b,treasury:'r14',delta:'rsi',
        quoteBytes:'8bf085c00f8eca000000',debitBytes:'e8621fccff8b4567488d8f800b0000',
        annexBytes:'0fb787d80000004c8d4567'},
    {name:'xp1',quote:0x71c63e,debit:0x71c671,returned:0x71c676,
        annex:0x71c69a,x:0x38,y:0x3c,treasury:'r15',delta:'rbx',
        quoteBytes:'8bd885c00f8e27020000',debitBytes:'e86a6cc2ff8b4538488d8f800b0000',
        annexBytes:'0fb787d80000004c8d4538'},
];
const TargetedCityQuoteReturn = 0x459169;
const TargetedSavingsCheck = 0x45918f;
// Optional execution provenance after a qualified quote/fund check. AL is a
// Boolean at the first two TEST instructions. The third boundary proves only
// that Manager::Start returned, not success (EAX is overwritten next).
const TargetedRequestBuilt = 0x4591f3;
const TargetedCommandChecked = 0x45921f;
const TargetedCommandReturned = 0x459241;
const CultureAnnexEntry = 0x11b100;
const PlotSetOwnerEntry = 0x616a0;
const CultureCityOffset = 0;
const PlotCoordinatesOffset = 0x28; // Packed signed16X/signed16Y, XP2 reference.
const PlayerTurnActiveOffset = 0x288; // Lua lIsTurnActive6ee350 and Manager.CanStart13560.
// Optional narrow lifecycle probe, motivated by paid788 remaining in a waiting
// decorator. Both Economic boundaries return from vtable+80 eligibility, NOT
// Update. The decorator boundary resolves the retained contract before reading
// its status. All are byte-audited on reference324c51e9 / hotfix092abfbb text.
const EconomicEligibilityChecks = [
    {rva:0x457515,handle:'rbx',phase:'leading',bytes:'84c074094883c310'},
    {rva:0x45755f,handle:'rdi',phase:'compaction',bytes:'84c0740f488bcb488bd7'},
];
const DecoratorContractStatus = 0x55a056;
const ContractStatusOffset = 0xb0; // Decorator55a030:1/3 waiting,5 executing,7 success.
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
const GameInstanceSlot = 0xb8aa68;
const GameTurnOffset = 0xc0;
const memory = createStudyMemoryIO({ptr, findRangeByAddress: p => Process.findRangeByAddress(p)});
const listeners = [];
const records = [];
let fault = null;
let pendingDebitCount = () => 0;
let pendingExecutionCount = () => 0;
let pendingAcknowledgementCount = () => 0;
let pendingCommandCount = () => 0;

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
        if(scope.observeExecution!==undefined&&typeof scope.observeExecution!=='boolean')
            throw Error('Execution observation must be explicit Boolean');
        if(scope.observeRoutine!==undefined&&(typeof scope.observeRoutine!=='boolean'||
                !Number.isInteger(scope.city)||scope.city<0))
            throw Error('Routine observation requires explicit Boolean and city identity');
        if(scope.observeLifecycle!==undefined&&typeof scope.observeLifecycle!=='boolean')
            throw Error('Lifecycle observation must be explicit Boolean');
        if(scope.observeLifecycle===true&&scope.observeLineage!==true)
            throw Error('Lifecycle observation requires known contract lineage');
        if(scope.repairOwnedPurchase!==undefined&&typeof scope.repairOwnedPurchase!=='boolean')
            throw Error('Purchase repair must be explicit Boolean');
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
        for(const handler of PurchaseHandlers) {
            fingerprint(handler.quote,handler.quoteBytes);
            fingerprint(handler.debit,handler.debitBytes);
            fingerprint(handler.annex,handler.annexBytes);
        }
        fingerprint(TargetedCityQuoteReturn, '85c07e104d85f67405');
        fingerprint(TargetedSavingsCheck, '488bac24d0000000418bdfc1e308');
        fingerprint(0x459095, '48894c2408'); // Saved Economic receiver.
        fingerprint(0x4590a5, '4881ec80000000488be9'); // Audited frame size.
        const createdTrees = new Map(), knownContracts = new Map(), pendingSelections = new Map();
        const pendingDebits = new Map(); // At most32 synchronous observed plot commands.
        const commandBindings=new Map(); // Thread-bound admitted command, retired on return.
        let reservedAcknowledgements=0;
        const acknowledgement=scope.repairOwnedPurchase===true?
            createPurchasedContractAcknowledgement({core,scope,read,fingerprint}):null;
        let executionPending = 0;
        const emit = (receipt,consumeReservation=false) => {
            if(consumeReservation) {
                if(reservedAcknowledgements<1)throw Error('Missing acknowledgement journal reservation');
                --reservedAcknowledgements;
            }
            if (records.length+reservedAcknowledgements >= 512) throw Error('Purchase trace capacity');
            records.push(receipt);
            if (scope.streamRecords) send({kind: 'plot-purchase-receipt', receipt});
        };
        const fail = error => {
            fault = String(error);
            if (scope.streamRecords) send({kind: 'plot-purchase-fault', fault});
        };
        const turnNow = () => read(ptr(read(gameSlot, 0, 'ptr')), GameTurnOffset, 'i32');
        if(scope.observeRoutine===true)
            observeRoutineSupplier({core,scope,read,fingerprint,emit,fail,turnNow,listeners,isFaulted:()=>Boolean(fault)});
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
        const contractState = contract => {
            // Never interpret an arbitrary handle as a purchase contract.
            // A maximum64-entry observed binding set is sufficient here; all
            // fields are revalidated before any status/vtable read. Unknown or
            // reloaded instances remain unobserved, not guessed from city IDs.
            const binding=[...knownContracts.values()].find(row=>row.contract===contract.toString());
            if(!binding)return null;
            validatedContract(contract.add(ContractTargetOffset));
            const vtable=ptr(read(contract,0,'ptr'));
            const relative=address=>{
                const value=Number(address.toString())-Number(core.base.toString());
                if(!Number.isSafeInteger(value)||value<0||value>=core.size)
                    throw Error('Purchase contract dispatch outside audited GameCore');
                return value;
            };
            return {contractId:binding.contractId,ownerControl:binding.ownerControl,
                originCity:binding.originCity,rootTreeId:binding.rootTreeId,
                contractStatus:read(contract,ContractStatusOffset,'i32'),
                contractVtableRva:relative(vtable),
                executeRva:relative(ptr(read(vtable,0x20,'ptr'))),
                updateRva:relative(ptr(read(vtable,0x50,'ptr'))),
                eligibilityRva:relative(ptr(read(vtable,0x80,'ptr')))};
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
                    const binding = {city: scope.city,cityPointer:city.toString(),treeId, tree: tree.toString(),
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
                        executingTree: this.context.rsi.toString(), originCity: cities.length === 1 ? cities[0] : null,
                        originCityPointer:cities.length===1?origins[0].cityPointer:null};
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
                    emit({kind: 'purchase-contract-created', turn: turnNow(), player: scope.player, ...binding,
                        ...(scope.observeLifecycle?contractState(contract):{})});
                } catch (error) { fail(error); }
            }));
        }
        const commandLocation = handler => context => ({city: context.rdi,
            x: read(context.rbp, handler.x, 'i32'),
            y: read(context.rbp, handler.y, 'i32')});
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
                    if (records.length+reservedAcknowledgements >= 512) throw Error('Purchase trace capacity');
                    const turn = read(ptr(read(gameSlot, 0, 'ptr')), GameTurnOffset, 'i32');
                    const receipt = {kind, turn, player, city: read(city, CityIdOffset, 'i32'), plot};
                    if (value) Object.assign(receipt, value(this.context, this.threadId, receipt));
                    // Stream bounded observations to the host immediately.
                    // A machine/worker interruption can bypass finally and
                    // must not discard every receipt before endpoint freeze.
                    emit(receipt);
                } catch (error) {
                    fault = String(error);
                    if (scope.streamRecords) send({kind: 'plot-purchase-fault', fault});
                }
            }));
        };
        const allCommandPlots = scope.allCommandPlots === true;
        for(const handler of PurchaseHandlers) {
            const locate=commandLocation(handler);
            attach(handler.quote, 'quote', locate,
                context => ({handler:handler.name,gold: context.rax.toInt32()}), allCommandPlots);
            attach(handler.debit, 'debit-call', locate,
                (context, thread, receipt) => {
                    // Windowsx64 ABI: RCX is Treasury*, RDX points to signed Q8
                    // delta. Each descriptor's CALL invokes ChangeGoldBalance
                    // RVA3432e0; that routine reads/writes Treasury+a8 via
                    // SetGoldBalance, saturating only on int32 overflow. Read the
                    // actual balance instead of assuming the requested delta ran.
                    const key = `${thread}:${context.rsp}`;
                    if (!Number.isInteger(thread) || thread <= 0 || pendingDebits.has(key) || pendingDebits.size >= 32)
                        throw Error('Ambiguous or excessive pending plot debit');
                    const deltaQ8 = read(context.rdx, 0, 'i32');
                    const treasury = context.rcx;
                    if (treasury.toString() !== context[handler.treasury].toString())
                        throw Error('Plot debit Treasury receiver differs');
                    const beforeQ8 = read(treasury, TreasuryGoldOffset, 'i32');
                    pendingDebits.set(key, {handler:handler.name,treasury: treasury.toString(), beforeQ8, deltaQ8,
                        city: receipt.city, cityPointer: context.rdi.toString(), plot: receipt.plot, turn: receipt.turn,
                        command:commandBindings.get(thread)});
                    return {handler:handler.name,deltaQ8, threadId: thread, callerStack: context.rsp.toString(),
                        treasury: treasury.toString(), treasuryBeforeQ8: beforeQ8};
                }, allCommandPlots);
            attach(handler.returned, 'debit-return', locate,
                (context, thread, receipt) => {
                    // CALL and its following instruction have the same caller
                    // RSP. RCX may be clobbered on return, so borrow only the exact
                    // receiver paired at this thread/stack boundary. Same-address
                    // reuse without a completed pair is an observation failure.
                    const key = `${thread}:${context.rsp}`;
                    const pending = pendingDebits.get(key);
                    if (!Number.isInteger(thread) || thread <= 0 || !pending || pending.handler!==handler.name || pending.city !== receipt.city ||
                        pending.cityPointer !== context.rdi.toString() || pending.treasury !== context[handler.treasury].toString() || pending.plot !== receipt.plot ||
                        pending.turn !== receipt.turn || pending.deltaQ8 !== context[handler.delta].toInt32())
                        throw Error('Unmatched plot debit return');
                    const afterQ8 = read(ptr(pending.treasury), TreasuryGoldOffset, 'i32');
                    pendingDebits.delete(key);
                    const command=pending.command;
                    const binding=command&&command.turn===receipt.turn&&command.city===receipt.city&&command.plot===receipt.plot?
                        {contractId:command.contractId,contractPointer:command.contractPointer,
                            ownerControl:command.ownerControl,rootTreeId:command.rootTreeId}:{};
                    const value={...binding,handler:handler.name,deltaQ8: pending.deltaQ8, threadId: thread, callerStack: context.rsp.toString(), treasury: pending.treasury,
                        treasuryBeforeQ8: pending.beforeQ8, treasuryAfterQ8: afterQ8,
                        measuredDeltaQ8: afterQ8 - pending.beforeQ8,
                        // Notifications inside SetGoldBalance can cause nested
                        // effects. A mismatch stays explicit, never payment success.
                        deltaMatched: afterQ8 - pending.beforeQ8 === pending.deltaQ8};
                    if(acknowledgement)acknowledgement.observeDebit({...receipt,...value});
                    return value;
                }, allCommandPlots);
            attach(handler.annex, 'annex-return', locate,()=>({handler:handler.name}), allCommandPlots);
        }
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
                passesCombinedFunds: gold <= Math.floor((plotQ8 + slushQ8) / 256),
                ...(scope.observeLifecycle&&validatedContract(context.r12)?
                    contractState(context.r12.add(-ContractTargetOffset)):{})};
        });
        if(scope.observeLifecycle===true) {
            for(const boundary of EconomicEligibilityChecks)fingerprint(boundary.rva,boundary.bytes);
            fingerprint(DecoratorContractStatus,'8b88b000000083f905');
            for(const boundary of EconomicEligibilityChecks) {
                listeners.push(Interceptor.attach(core.base.add(boundary.rva),function(){
                    if(fault)return;
                    try {
                        const player=ptr(read(this.context.r15,EconomicPlayerOffset,'ptr'));
                        if(read(player,PlayerIdOffset,'i32')!==scope.player)return;
                        const contract=ptr(read(this.context[boundary.handle],0,'ptr'));
                        const state=contractState(contract);if(!state)return;
                        // ALfalse selects removal in native code. This receipt
                        // observes that predicate, not completion of vector
                        // compaction, destruction or any contract state write.
                        emit({kind:'purchase-economic-eligibility',turn:turnNow(),player:scope.player,
                            phase:boundary.phase,eligible:(this.context.rax.toInt32()&255)!==0,...state});
                    }catch(error){fail(error);}
                }));
            }
            listeners.push(Interceptor.attach(core.base.add(DecoratorContractStatus),function(){
                if(fault)return;
                try {
                    const state=contractState(this.context.rax);if(!state)return;
                    emit({kind:'purchase-decorator-status',turn:turnNow(),player:scope.player,...state});
                    if(acknowledgement) {
                        const binding=validatedContract(this.context.rax.add(ContractTargetOffset));
                        // R14 is the executing tree, not necessarily the root.
                        // Match its live trigger against the independent fresh
                        // creation binding before any mutation. This also tests
                        // the identity path proposed for the future CE adapter.
                        const tree=this.context.r14,chain=ancestry(tree);
                        const city=ptr(read(tree,0x2f0,'ptr')),plot=ptr(read(tree,0x308,'ptr'));
                        if(city.isNull()||plot.isNull())throw Error('Missing executing tree identity');
                        const packed=read(plot,0x28,'i32');
                        const tuple={city:read(city,CityIdOffset,'i32'),player:read(city,CityOwnerOffset,'i32'),
                            district:read(tree,0x29c,'i32'),x:(packed<<16)>>16,y:packed>>16,
                            rootTreeId:read(chain.root,TreeIdOffset,'i32'),rootControl:read(chain.root,TreeControlOffset,'i32')};
                        emit({kind:'purchase-executing-tree',turn:turnNow(),contractId:binding.contractId,...tuple});
                        if(tuple.city!==binding.originCity||city.toString()!==binding.originCityPointer||
                            tuple.player!==scope.player||tuple.district!==scope.district||
                            tuple.x!==binding.x||tuple.y!==binding.y||tuple.rootTreeId!==binding.rootTreeId||
                            tuple.rootControl!==binding.ownerControl)throw Error('Executing tree differs from purchase lineage');
                        const header={turn:turnNow(),player:scope.player,plot:binding.plot,
                            city:binding.originCity,contractId:binding.contractId};
                        let reserved=false;
                        try {
                            const result=acknowledgement.tryAcknowledge(this.context.rax,binding,state,turnNow(),()=>{
                                // Reserve the outcome even if other callbacks
                                // run during a native read/call. No assignment
                                // may precede this journal admission and intent.
                                if(records.length+reservedAcknowledgements+2>512)
                                    throw Error('No acknowledgement journal capacity');
                                ++reservedAcknowledgements;reserved=true;
                                emit({kind:'purchase-acknowledgement-intent',...header});
                            });
                            if(result)emit({kind:'purchase-acknowledgement',...header,...result},reserved);
                            else if(reserved)throw Error('Reserved acknowledgement produced no outcome');
                        }catch(error){
                            if(reserved&&reservedAcknowledgements>0)
                                emit({kind:'purchase-acknowledgement',...header,acknowledged:false,
                                    writeResult:'unverified',error:String(error)},true);
                            throw error;
                        }
                    }
                }catch(error){fail(error);}
            }));
        }
        if (scope.observeExecution === true) {
            // Audited original bytes on SHA092abfbb's text-identical reference.
            // These optional observations resolve ownership without a known
            // paid-branch callback; they never grant admission or issue actions.
            fingerprint(TargetedRequestBuilt,'84c00f84ca000000');
            fingerprint(TargetedCommandChecked,'84c00f849e000000');
            fingerprint(TargetedCommandReturned,'418bc5488d9424c0000000');
            fingerprint(CultureAnnexEntry,'405556415441564157');
            fingerprint(PlotSetOwnerEntry,'448944241889542410');
            const admissionState = context => {
                // The saved Economic receiver remains at callerRSP+c0 until
                // after these three boundaries. Check its player before
                // describing the measured IsTurnActive byte; do not invoke
                // a native getter from a supposedly read-only callback.
                const economic=ptr(read(context.rsp,EconomicReceiverOnStack,'ptr'));
                const player=ptr(read(economic,EconomicPlayerOffset,'ptr'));
                if(read(player,PlayerIdOffset,'i32')!==scope.player)throw Error('Execution Economic player differs');
                return {playerTurnActive:read(player,PlayerTurnActiveOffset,'u8')!==0};
            };
            attach(TargetedRequestBuilt,'targeted-request-built',targetedLocation('r14'),
                context=>({requestBuilt:(context.rax.toInt32()&255)!==0,...admissionState(context)}));
            attach(TargetedCommandChecked,'targeted-command-checked',targetedLocation('r14'),
                (context,thread,receipt)=>{
                    const admitted=(context.rax.toInt32()&255)!==0;
                    const binding=scope.observeLineage?validatedContract(context.r12):null;
                    if(admitted&&binding&&binding.originCity===receipt.city) {
                        if(!Number.isInteger(thread)||thread<=0||commandBindings.has(thread)||commandBindings.size>=32)
                            throw Error('Ambiguous purchase command binding');
                        commandBindings.set(thread,{turn:receipt.turn,city:receipt.city,plot:receipt.plot,
                            contractId:binding.contractId,contractPointer:binding.contract,
                            ownerControl:binding.ownerControl,rootTreeId:binding.rootTreeId});
                    }
                    return {commandAdmitted:admitted,...admissionState(context)};
                });
            attach(TargetedCommandReturned,'targeted-command-returned',targetedLocation('r14'),
                (context,thread)=>{
                    const result={managerStartReturned:true,...admissionState(context),
                        ...(scope.observeLifecycle&&validatedContract(context.r12)?
                            contractState(context.r12.add(-ContractTargetOffset)):{})};
                    commandBindings.delete(thread);
                    return result;
                });
            const caller = address => {
                // Windows user pointers fit53-bit integers. Preserve an outside
                // caller's address with unknownRVA rather than wrapping it into
                // this GameCore's address range or inventing an attribution.
                const absolute=Number(address.toString()),base=Number(core.base.toString());
                if(!Number.isSafeInteger(absolute)||!Number.isSafeInteger(base))throw Error('Unsafe caller pointer');
                const rva=absolute-base;
                return {caller:address.toString(),callerRva:rva>=0&&rva<core.size?rva:null};
            };
            const scopedPlot = (x,y) => x>=0&&x<scope.width&&y>=0&&y<scope.height&&targets.has(y*scope.width+x);
            listeners.push(Interceptor.attach(core.base.add(CultureAnnexEntry),{
                onEnter() {
                    if(fault)return;
                    try {
                        const city=ptr(read(this.context.rcx,CultureCityOffset,'ptr'));
                        if(read(city,CityOwnerOffset,'i32')!==scope.player)return;
                        const x=read(this.context.rdx,0,'i32'),y=read(this.context.rdx,4,'i32');
                        if(!scopedPlot(x,y))return;
                        this.annexReceipt={kind:'culture-annex-return',turn:turnNow(),player:scope.player,
                            city:read(city,CityIdOffset,'i32'),plot:y*scope.width+x,...caller(this.returnAddress)};
                        if(++executionPending>32)throw Error('Execution return capacity');
                    }catch(error){fail(error);}
                },
                onLeave() {
                    if(!this.annexReceipt)return;
                    executionPending--;
                    if(!fault)try{emit(this.annexReceipt);}catch(error){fail(error);}
                }
            }));
            listeners.push(Interceptor.attach(core.base.add(PlotSetOwnerEntry),{
                onEnter() {
                    if(fault)return;
                    try {
                        const packed=read(this.context.rcx,PlotCoordinatesOffset,'i32');
                        const x=(packed<<16)>>16,y=packed>>16;
                        if(!scopedPlot(x,y))return;
                        this.ownerReceipt={kind:'plot-set-owner-return',turn:turnNow(),plot:y*scope.width+x,
                            requestedPlayer:this.context.rdx.toInt32(),requestedCity:this.context.r8.toInt32(),
                            ...caller(this.returnAddress)};
                        if(++executionPending>32)throw Error('Execution return capacity');
                    }catch(error){fail(error);}
                },
                onLeave() {
                    if(!this.ownerReceipt)return;
                    executionPending--;
                    if(!fault)try{emit(this.ownerReceipt);}catch(error){fail(error);}
                }
            }));
            pendingExecutionCount=()=>executionPending;
        }
        Interceptor.flush();
        // Expose unresolved pairs only at freeze; never interpret a call with
        // no observed return as a measured payment or resend the game command.
        pendingDebitCount = () => pendingDebits.size;
        pendingAcknowledgementCount=()=>reservedAcknowledgements;
        pendingCommandCount=()=>commandBindings.size;
        return true;
    },
    freeze() {
        for (const listener of listeners) listener.detach();
        const pendingDebits = pendingDebitCount();
        const pendingExecutions=pendingExecutionCount();
        const pendingAcknowledgements=pendingAcknowledgementCount(),pendingCommands=pendingCommandCount();
        return {records, fault: fault || (pendingDebits ? 'Unreturned observed plot debit' :
            pendingExecutions?'Unreturned observed execution callback':pendingAcknowledgements?
                'Unresolved acknowledgement journal':pendingCommands?'Unreturned purchase command':null),
            pendingDebits,pendingExecutions,pendingAcknowledgements,pendingCommands};
    },
};
