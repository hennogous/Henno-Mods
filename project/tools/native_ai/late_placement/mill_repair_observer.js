'use strict';

// Patched Steam XP2. Observe the ordinary building score, the native building
// choice and a BuildBuilding attempt for one Mill or Granary. An explicit
// matched diagnostic can add a bounded preference to the eligible comparison.
const MILL_VALUE = 0x52a050;
const ORDINARY_RETURN = 0x3e3ee2;
const BEST_BUILDING = 0x3e4710;
const REQUIREMENTS = 0x0f61c0;
const REQUIREMENTS_RETURN = 0x3e48bb;
const BUILD_BUILDING = 0x3df040;
const BUILD_PROJECT = 0x3df4b0;
const PROJECT_CAN_ADVANCE = 0x0f55f0;
const PROJECT_CAN_ADVANCE_RETURN = 0x3df4e5;
const PROJECT_VALIDATE_OPERATION_RETURN = 0x3df568;
const BEST_PROJECT = 0x3e5960;
const PROJECT_COMPARISON = 0x3e59fe;
const QUEUE_BEST_PROJECT_RETURN = 0x3e84ab;
const QUEUE_NEXT_BUILD = 0x3e8190;
const CONTRACT_VALIDATE = 0x3fa8e0;
const CONTRACT_UPDATE = 0x3fa5e0;
const CONTRACT_EXECUTE = 0x3f8310;
const BUILDING_COMPARISON = 0x3e49da;
const ORDINARY_BEST_BUILDING_RETURN = 0x3e160a;
const THREAT_BEST_BUILDING_RETURN = 0x3ea73b;
const QUEUE_BEST_BUILDING_RETURN = 0x3e849c;
const DIAGNOSTIC_MILL_BID_Q8 = 98304;
const MELBOURNE_NOMINATION_Q8 = 448 * 256;
const NORMALIZE_BUILDING_YIELD = 0x52b110;
const DISCOUNT_BUILDING_INCOME = 0x528310;
const CITY_BUILDING_YIELD_CHANGE = 0x10c0e0;
const INTRINSIC_YIELD_RETURN = 0x52bb71;
// BuildingValue reads the city's existing building-specific yield changes
// separately from the building definition's intrinsic yield rows.
const CITY_BUILDING_YIELD_RETURN = 0x52bd7f;
const DYNAMIC_YIELD_NORMALIZE_RETURN = 0x52bda1;
const INCOME_READY_RETURN = 0x52c3ad;
const INCOME_HORIZON_RETURN = 0x52c3cd;
const QUEUE_FALLBACK_COMPARISON = 0x3e8741;
const QUEUE_OFFER_GATE = 0x3e86d2;
const DEFAULT_UNIT_RETURN = 0x3e8836;
const DEFAULT_PROJECT_RETURN = 0x3e88e5;
const GENERIC_UNIT_RETURN = 0x3e899f;
const RECEIVE_VALIDATE_RETURN = 0x3e9529;
const QUEUE_VALIDATE_RETURN = 0x3e82c3;
const QUEUE_UPDATE_RETURN = 0x3e82dc;
const QUEUE_EXECUTE_RETURN = 0x3e8715;
const CITY_BUILD_CITY = 0x90, CITY_OWNER = 0xd8, CITY_ID = 0xa8;
const CITY_BUILD_QUEUE = 0x10d0;
const CITY_ROWS = 0x4c8, CITY_ROW_COUNT = 0x4d8, ROW_BUILDING_SCORES = 0x28;
// UnitRequestContract represents building, district and unit offers. These
// offsets are read only on calls to that type's own virtual methods.
const CONTRACT_STATUS = 0xb0, CONTRACT_ID = 0x110, CONTRACT_VALUE = 0x158;
const CONTRACT_UNIT = 0x178, CONTRACT_BUILDING = 0x190, CONTRACT_DISTRICT = 0x1a8;
const QUEUE_BUILDING_ID_FRAME = 0x7f, QUEUE_BUILDING_VALUE_FRAME = 0x77;
const QUEUE_PROJECT_ID_FRAME_BACK = 0x51;
const memory = createStudyMemoryIO({ptr, findRangeByAddress: address => Process.findRangeByAddress(address)});
const records = [], selection = new Map(), queuePass = new Map();
let enabled = false, installed = false, boundary = null, fault = null, active = 0;
let queueSequence = 0;
let exchangeComponents = null;
let exchangeMode = null;
const exchangeIncome = [];

function read(pointer, offset, type) {
    const result = memory.read(pointer.toString(), offset, type);
    if (result.error) throw Error(`${type} at ${offset}: ${result.error}`);
    return result.value;
}

function add(record) {
    if (records.length >= 4096) throw Error('Mill observer evidence budget');
    records.push({boundary, ...record});
}

function protect(operation) {
    try { operation(); }
    catch (error) { enabled = false; fault = String(error); }
}

function init(spec, scope) {
    const normalize = value => value.replace(/\\/g, '/').toLowerCase();
    if (installed || Process.platform !== 'windows' || Process.arch !== 'x64' || Process.pointerSize !== 8)
        throw Error('Expected first installation on Windows x64');
    const modules = Process.enumerateModules();
    const carriers = modules.filter(module => /GameCore_XP2_(?:CE|CSC)/i.test(module.name));
    const expectedCarrier = scope.cePath
        ? carriers.length === 1 && normalize(carriers[0].path) === normalize(scope.cePath)
        : carriers.length === 0;
    if (!expectedCarrier) throw Error('Unexpected native carrier');
    const core = modules.find(module => normalize(module.path) === normalize(spec.path));
    const boston = scope.player === 3 && scope.city === 131073;
    const building = scope.granary ?? scope.mill;
    const granary = scope.granary !== undefined;
    const observedCity = Number.isInteger(scope.player) && scope.player > 0 && scope.player < 64
        && Number.isInteger(scope.city) && scope.city >= 0;
    if (!core || core.size !== spec.image_size || !observedCity ||
        !Number.isInteger(building) || building < 0 || building >= 4096)
        throw Error('Expected a verified city and building scope');
    const bid = scope.millBidQ8 ?? 0;
    const nominationBid = scope.nominationBidQ8 ?? 0;
    if (granary && (scope.mill !== undefined || bid || nominationBid || scope.screenProjectEligibility))
        throw Error('Unexpected Mill or project intervention in a Granary scope');
    const granaryBid = scope.granaryNominationQ8 ?? 0;
    if (granaryBid !== 0 && (!scope.cePath || scope.player !== 1 || scope.city !== 327684 ||
        scope.granary !== 3 || granaryBid !== 288 * 256))
        throw Error('Unsupported Trebizond Granary nomination preference');
    let granaryBidApplied = false;
    const melbourne = scope.player === 4 && scope.city === 131073 && scope.mill === 139;
    const captureComponents = scope.granaryComponents || scope.millOpeningComponents;
    const exchangeYields = new Set([scope.foodYieldIndex, scope.productionYieldIndex, scope.goldYieldIndex]);
    if (captureComponents && (!scope.cePath || exchangeYields.size !== 3 ||
        [...exchangeYields].some(index => !Number.isInteger(index) || index < 0) ||
        bid || nominationBid || granaryBid || scope.screenProjectEligibility ||
        (scope.granaryComponents && (scope.player !== 1 || scope.city !== 327684 || scope.granary !== 3)) ||
        (scope.millOpeningComponents && (!melbourne || granary))))
        throw Error('Expected a pinned read-only exchange forecast scope');
    if (bid !== 0 && (!boston || !scope.cePath || bid !== DIAGNOSTIC_MILL_BID_Q8))
        throw Error('Unsupported diagnostic Mill preference');
    if (nominationBid !== 0 && (!melbourne || !scope.cePath || nominationBid !== MELBOURNE_NOMINATION_Q8 || bid))
        throw Error('Unsupported Wind Mill nomination preference');
    if (scope.screenProjectEligibility && (!boston || !scope.cePath || bid || nominationBid))
        throw Error('The isolated project eligibility diagnostic requires CE and no Mill bid');
    const captureQueueOperands = scope.cePath || scope.captureQueueOperands;
    const componentPoints = captureComponents ? ['BuildingValue', 'ModifierValue', 'AnalyzeModifier'] : [];

    const address = rva => core.base.add(rva);
    const caller = invocation => invocation.returnAddress.sub(core.base).toInt32();
    const target = city => read(city, CITY_OWNER, 'i32') === scope.player && read(city, CITY_ID, 'i32') === scope.city;
    const cityOf = build => ptr(read(build, CITY_BUILD_CITY, 'ptr'));
    const contract = object => ({
        id: read(object, CONTRACT_ID, 'i32'), status: read(object, CONTRACT_STATUS, 'i32'),
        q8: read(object, CONTRACT_VALUE, 'i32'), building: read(object, CONTRACT_BUILDING, 'i32'),
        unit: read(object, CONTRACT_UNIT, 'i32'), district: read(object, CONTRACT_DISTRICT, 'i32'),
    });
    for (const [rva, expected] of [
        scope.cePath
            ? [ORDINARY_RETURN, '4c8ba5b00000004963d78b00498b4c2428']
            : [MILL_VALUE, '4c894424188954241055535741544155'],
        [BEST_BUILDING, '44884c24204488442418488954241055'],
        [BUILD_BUILDING, '48895c241048896c2418565741564881'],
        [QUEUE_NEXT_BUILD, '40554157488d6c24b14881ecf8000000'],
        [CONTRACT_VALIDATE, '488954241048894c240855574156'],
        [CONTRACT_UPDATE, '40555657488bec4883ec3083b990010000ff'],
        [CONTRACT_EXECUTE, '405553574156488d6c24c14881eca8000000'],
        [RECEIVE_VALIDATE_RETURN - 7, '41ff9098000000'],
        [QUEUE_VALIDATE_RETURN - 7, '41ff9098000000'],
        [QUEUE_UPDATE_RETURN - 4, '41ff5068'],
        [QUEUE_EXECUTE_RETURN - 4, '41ff5038'],
        ...componentPoints.map(kind => STUDY_POINTS[kind]),
        ...(componentPoints.length ? [
            [NORMALIZE_BUILDING_YIELD, '48895c240848896c2410488974242057'],
            [DISCOUNT_BUILDING_INCOME, '40565741564883ec70418bf14c8bf2'],
        ] : []),
        ...(scope.millOpeningComponents ? [
            [CITY_BUILDING_YIELD_CHANGE, '48895c240848896c2410488974241857'],
        ] : []),
        ...(captureQueueOperands ? [
            [BUILDING_COMPARISON, '443b367e11448936'],
            [QUEUE_OFFER_GATE, '8d9700ffffff3990580100007c3d'],
            [QUEUE_FALLBACK_COMPARISON, '8b457f83f8ff0f84c50000008b5d77'],
            [DEFAULT_UNIT_RETURN, '84c00f8456010000'],
            [DEFAULT_PROJECT_RETURN, '84c00f84a7000000'],
            [GENERIC_UNIT_RETURN, '8bd883f8ff0f84b2000000'],
            [BUILD_PROJECT, '48895c241848896c2420564883ec60'],
            [PROJECT_CAN_ADVANCE_RETURN, '84c075124c8d5c2460'],
            [PROJECT_VALIDATE_OPERATION_RETURN, '84c075054032f6'],
        ] : []),
        ...(scope.screenProjectEligibility ? [
            [PROJECT_CAN_ADVANCE, '4c894c242044884424188954241048894c2408'],
            [BEST_PROJECT, '4056415641574883ec20'],
            [PROJECT_COMPARISON, '413b0e7e0541890e8bf3'],
            [QUEUE_BEST_PROJECT_RETURN - 5, 'e8b5d4ffff8945af'],
        ] : []),
    ]) {
        const bytes = Array.from(new Uint8Array(address(rva).readByteArray(expected.length / 2)),
            value => value.toString(16).padStart(2, '0')).join('');
        if (bytes !== expected) throw Error(`Unexpected code at ${rva.toString(16)}`);
    }
    for (const [rva, expected] of [[ORDINARY_RETURN, MILL_VALUE], [REQUIREMENTS_RETURN, REQUIREMENTS],
        [ORDINARY_BEST_BUILDING_RETURN, BEST_BUILDING], ...(componentPoints.length ? [
            [INTRINSIC_YIELD_RETURN, NORMALIZE_BUILDING_YIELD],
            [INCOME_READY_RETURN, DISCOUNT_BUILDING_INCOME],
            [INCOME_HORIZON_RETURN, DISCOUNT_BUILDING_INCOME],
        ] : []), ...(scope.millOpeningComponents ? [
            [CITY_BUILDING_YIELD_RETURN, CITY_BUILDING_YIELD_CHANGE],
            [DYNAMIC_YIELD_NORMALIZE_RETURN, NORMALIZE_BUILDING_YIELD],
        ] : [])]) {
        const end = address(rva);
        if (end.sub(5).readU8() !== 0xe8 || !end.add(end.sub(4).readS32()).equals(address(expected)))
            throw Error(`Caller fingerprint at ${rva.toString(16)}`);
    }

    function observe(rva, enter, leave) {
        Interceptor.attach(address(rva), {
            onEnter(args) {
                if (!enabled) return;
                protect(() => { this.sample = enter(args, this); if (this.sample) active++; });
            },
            onLeave(result) {
                if (!this.sample) return;
                active--;
                protect(() => leave(this.sample, result));
            },
        });
    }
    if (componentPoints.length) {
        exchangeMode = granary ? 'granary' : 'millOpening';
        exchangeComponents = makeStudyObserver(memory, {
            profile: granary ? 'trebizond-granary-components-v1' : 'melbourne-wind-mill-opening-v1',
            mappingVerified: true,
            buildings: [{type: granary ? 'BUILDING_GRANARY' : 'BUILDING_CSC_BAKERS_WIND_MILL', index: building}],
            targets: [{player: scope.player, city: scope.city}], ...EXCHANGE_STUDY_LIMITS,
        });
        // Most native valuation calls belong to other buildings and cities.
        // Enter the detailed recorder only inside a matched valuation frame.
        const threads = new Map();
        const referenceCounts = new Map();
        let referencePlayer = null;
        for (const kind of componentPoints) {
            observe(STUDY_POINTS[kind][0], (args, invocation) => {
                const thread = invocation.threadId;
                const stack = threads.get(thread) ?? [];
                if (!stack.length && (kind !== 'BuildingValue' ||
                    args[1].toInt32() !== building || args[6].isNull() || !target(args[6]))) return;
                const frame = exchangeComponents.enter(kind, decodeStudyArgs(kind, args, thread, caller(invocation)));
                if (!frame) return;
                if (kind === 'BuildingValue' && frame.paired) referencePlayer = args[5];
                stack.push(frame);
                threads.set(thread, stack);
                return {frame, thread};
            }, ({frame, thread}, result) => {
                exchangeComponents.leave(frame, result.toString());
                const stack = threads.get(thread);
                if (stack.pop() !== frame) throw Error('Unbalanced exchange valuation frame');
                if (!stack.length) threads.delete(thread);
            });
        }
        // Separate observations for the native intrinsic yield and the two
        // endpoints of its income stream. Neither helper is called by the probe.
        const recordIncome = ({out, ...sample}, result) => {
            if (!result.equals(out) || exchangeIncome.length >= 1024)
                throw Error('Unexpected exchange income return or capture bound');
            exchangeIncome.push({...sample, valueQ8: read(out, 0, 'i32')});
        };
        function buildingFrame(invocation) {
            const frame = threads.get(invocation.threadId)?.at(-1);
            return frame?.kind === 'BuildingValue' && frame.paired ? frame : null;
        }
        if (scope.millOpeningComponents) {
            observe(CITY_BUILDING_YIELD_CHANGE, (args, invocation) => {
                const yieldIndex = args[2].toInt32();
                if (caller(invocation) !== CITY_BUILDING_YIELD_RETURN || args[1].toInt32() !== building ||
                    !exchangeYields.has(yieldIndex)) return;
                const frame = buildingFrame(invocation);
                if (frame) return {buildingCallId: frame.id, kind: 'dynamic-yield-input', yieldIndex};
            }, (sample, result) => {
                if (exchangeIncome.length >= 1024) throw Error('Exchange income capture bound');
                exchangeIncome.push({...sample, amount: result.toInt32()});
            });
        }
        observe(NORMALIZE_BUILDING_YIELD, (args, invocation) => {
            const yieldIndex = args[2].toInt32();
            const from = caller(invocation);
            if (!exchangeYields.has(yieldIndex)) return;
            const frame = buildingFrame(invocation);
            if (scope.millOpeningComponents && frame && from === DYNAMIC_YIELD_NORMALIZE_RETURN)
                return {out: args[0], buildingCallId: frame.id, kind: 'dynamic-yield-normalized',
                    inputQ8: read(args[1], 0, 'i32'), yieldIndex};
            if (from !== INTRINSIC_YIELD_RETURN) return;
            if (frame && (!granary || yieldIndex === scope.foodYieldIndex))
                return {out: args[0], buildingCallId: frame.id, kind: 'intrinsic-yield',
                    inputQ8: read(args[1], 0, 'i32'), yieldIndex};
            if (granary && yieldIndex === scope.foodYieldIndex) return;
            // NormalizeYields receives the same player valuation object as
            // BuildingValue. A different city or building can provide a yield
            // weight for that player. Its score and timing are unrelated.
            if (!referencePlayer || referencePlayer.isNull() || !args[3].equals(referencePlayer)) return;
            const count = referenceCounts.get(yieldIndex) ?? 0;
            if (count >= 16) return;
            const inputQ8 = read(args[1], 0, 'i32');
            if (inputQ8 <= 0) return;
            referenceCounts.set(yieldIndex, count + 1);
            return {out: args[0], kind: 'reference-yield', inputQ8, yieldIndex};
        }, recordIncome);
        observe(DISCOUNT_BUILDING_INCOME, (args, invocation) => {
            const from = caller(invocation);
            if (from !== INCOME_READY_RETURN && from !== INCOME_HORIZON_RETURN) return;
            const frame = buildingFrame(invocation);
            if (frame) return {out: args[0], buildingCallId: frame.id,
                kind: from === INCOME_READY_RETURN ? 'income-ready' : 'income-horizon',
                inputQ8: read(args[1], 0, 'i32'), discountQ8: read(args[2], 0, 'i32'),
                turns: args[3].toInt32()};
        }, recordIncome);
    }
    if (scope.cePath) {
        // CE owns the Building NetValue entry. Read the ordinary caller's
        // returned score before it is copied into the building row.
        Interceptor.attach(address(ORDINARY_RETURN), function () {
            if (!enabled || this.context.r15.toInt32() !== building) return;
            protect(() => {
                const c = this.context;
                if (target(c.rsi)) {
                    add({kind: 'value', q8: read(c.rax, 0, 'i32'), ready: c.r12.toInt32(),
                        horizon: read(c.rsp, 0x78, 'i32')});
                }
            });
        });
    } else {
        observe(MILL_VALUE, (a, invocation) => {
        if (caller(invocation) !== ORDINARY_RETURN || a[1].toInt32() !== building || !target(a[6])) return;
            if (read(a[7], 0, 'i32') !== -9999 || read(a[7], 4, 'i32') !== -9999) throw Error('Expected ordinary coordinates');
            return {out: a[0], ready: a[3].toInt32(), horizon: a[4].toInt32()};
        }, (sample, result) => {
            if (!result.equals(sample.out)) throw Error('Unexpected building value return');
            add({kind: 'value', q8: read(result, 0, 'i32'), ready: sample.ready, horizon: sample.horizon});
        });
    }
    observe(BEST_BUILDING, (a, invocation) => {
        if (!target(cityOf(a[0]))) return;
        const count = read(a[0], CITY_ROW_COUNT, 'u32');
        if (!count || count > 37) return;
        const vector = ptr(read(read(a[0], CITY_ROWS, 'ptr'), ROW_BUILDING_SCORES, 'ptr'));
        if (vector.isNull()) return;
        const sample = {out: a[1], thread: invocation.threadId, caller: caller(invocation),
            flags: [a[2].toInt32() & 255, a[3].toInt32() & 255],
            buildingQ8: read(vector, building * 4, 'i32'), requirements: null};
        if (selection.has(sample.thread)) throw Error('Nested target building choice');
        selection.set(sample.thread, sample);
        return sample;
    }, (sample, result) => {
        selection.delete(sample.thread);
        const winner = result.toInt32();
        add({kind: 'choice', caller: sample.caller, flags: sample.flags,
            [granary ? 'granaryQ8' : 'millQ8']: sample.buildingQ8,
            requirements: sample.requirements, winner, winnerQ8: winner < 0 ? null : read(sample.out, 0, 'i32')});
    });
    observe(REQUIREMENTS, (a, invocation) => {
        if (caller(invocation) !== REQUIREMENTS_RETURN || a[1].toInt32() !== building) return;
        return selection.get(invocation.threadId);
    }, (sample, result) => { sample.requirements = Boolean(result.toInt32() & 255); });
    observe(BUILD_BUILDING, (a, invocation) => {
        if (target(cityOf(a[0]))) return {building: a[1].toInt32(), caller: caller(invocation)};
    }, (sample, result) => add({kind: 'request', ...sample, accepted: Boolean(result.toInt32() & 255)}));
    // Queue passes group individual offers even when several decisions occur
    // in a sampling segment. Receive validation is earlier and has no pass.
    observe(QUEUE_NEXT_BUILD, (a, invocation) => {
        if (!target(cityOf(a[0]))) return;
        const thread = invocation.threadId;
        if (queuePass.has(thread)) throw Error('Nested target city queue pass');
        const pass = ++queueSequence;
        queuePass.set(thread, pass);
        add({kind: 'queue-begin', pass});
        return {thread, pass};
    }, sample => {
        queuePass.delete(sample.thread);
        add({kind: 'queue-end', pass: sample.pass});
    });
    if (captureQueueOperands) {
        // The candidate reached the comparison after the actual requirements
        // gates and native value transformations. R14 is its effective Q8.
        Interceptor.attach(address(BUILDING_COMPARISON), function () {
            if (!enabled || this.context.r12.toInt32() !== building) return;
            const sample = selection.get(this.threadId);
            if (!sample) return;
            protect(() => {
                const c = this.context;
                const effectiveQ8 = c.r14.toInt32();
                // The engine has already checked this candidate's requirements.
                // CMP consumes R14D and the winning branch copies it to the
                // output score. Keep the cache, other candidates and queue intact.
                const scoped = boundary === 261 && sample.requirements === true &&
                    sample.flags[0] === 1 && sample.flags[1] === 0 &&
                    (sample.caller === THREAT_BEST_BUILDING_RETURN || sample.caller === QUEUE_BEST_BUILDING_RETURN);
                // The ordinary 0/0 proposal remains subject to the unit
                // comparison and the independent production contract gate.
                const nomination = boundary === 125 && sample.requirements === true &&
                    sample.flags[0] === 0 && sample.flags[1] === 0 && sample.caller === ORDINARY_BEST_BUILDING_RETURN;
                // Apply once at the measured ordinary comparison, after the
                // requirements pass. Keep the native offer and queue prices.
                const trebizond = granaryBid && !granaryBidApplied && boundary === 150 &&
                    sample.requirements === true && sample.flags[0] === 0 && sample.flags[1] === 0 &&
                    sample.caller === ORDINARY_BEST_BUILDING_RETURN && effectiveQ8 === 46458;
                const millPreference = nomination ? nominationBid : (scoped ? bid : 0);
                const preference = trebizond ? granaryBid : millPreference;
                const deltaQ8 = effectiveQ8 > 0 && effectiveQ8 <= 0x7fffffff - preference ? preference : 0;
                add({kind: granary ? 'granary-compare' : 'mill-compare', caller: sample.caller, effectiveQ8, deltaQ8,
                    incumbentQ8: read(c.rsi, 0, 'i32')});
                if (deltaQ8) {
                    c.r14 = ptr(effectiveQ8 + deltaQ8);
                    if (trebizond) granaryBidApplied = true;
                }
            });
        });
        function queuePoint(rva, capture) {
            Interceptor.attach(address(rva), function () {
                if (!enabled) return;
                const pass = queuePass.get(this.threadId);
                if (pass !== undefined) protect(() => add({pass, ...capture(this.context)}));
            });
        }
        // This point follows contract arbitration. Compare the three
        // default categories using the same operands the native queue uses.
        queuePoint(QUEUE_FALLBACK_COMPARISON, c => ({
            kind: 'default-compare',
            building: read(c.rbp, QUEUE_BUILDING_ID_FRAME, 'i32'),
            buildingQ8: read(c.rbp, QUEUE_BUILDING_VALUE_FRAME, 'i32'),
            unit: c.r13.toInt32(), unitQ8: c.rdi.toInt32(),
            project: read(c.rbp.sub(QUEUE_PROJECT_ID_FRAME_BACK), 0, 'i32'), projectQ8: c.rsi.toInt32(),
        }));
        // The top validated offer first faces the best unit minus one unit,
        // then the best project. Only read fields shared by base contracts.
        queuePoint(QUEUE_OFFER_GATE, c => ({
            kind: 'offer-gate',
            offerId: read(c.rax, CONTRACT_ID, 'i32'),
            offerQ8: read(c.rax, CONTRACT_VALUE, 'i32'),
            unitQ8: c.rdi.toInt32(),
            projectQ8: c.rsi.toInt32(),
        }));
        queuePoint(DEFAULT_UNIT_RETURN, c => ({kind: 'default-unit', accepted: Boolean(c.rax.toInt32() & 255)}));
        queuePoint(DEFAULT_PROJECT_RETURN, c => ({kind: 'default-project', accepted: Boolean(c.rax.toInt32() & 255)}));
        queuePoint(GENERIC_UNIT_RETURN, c => ({kind: 'generic-unit', unit: c.rax.toInt32()}));
        const projects = new Map();
        observe(BUILD_PROJECT, (args, invocation) => {
            const thread = invocation.threadId;
            const pass = queuePass.get(thread);
            if (pass === undefined || !target(cityOf(args[0]))) return;
            if (projects.has(thread)) throw Error('Nested target project attempt');
            const sample = {thread, pass, project: args[1].toInt32(), canAdvance: null, operationEligible: null};
            projects.set(thread, sample);
            return sample;
        }, ({thread, ...sample}, result) => {
            projects.delete(thread);
            add({kind: 'project-attempt', ...sample, accepted: Boolean(result.toInt32() & 255)});
        });
        for (const [rva, field] of [[PROJECT_CAN_ADVANCE_RETURN, 'canAdvance'],
            [PROJECT_VALIDATE_OPERATION_RETURN, 'operationEligible']]) {
            Interceptor.attach(address(rva), function () {
                const sample = projects.get(this.threadId);
                if (enabled && sample) sample[field] = Boolean(this.context.rax.toInt32() & 255);
            });
        }
    }
    if (scope.screenProjectEligibility) {
        // Same Win64 call as BuildProject: this=BuildQueue, project index,
        // two false flags and a null optional failure-reporter pointer.
        const canAdvance = new NativeFunction(address(PROJECT_CAN_ADVANCE), 'uint8',
            ['pointer', 'uint32', 'uint8', 'pointer', 'uint8']);
        const candidates = new Map();
        observe(BEST_PROJECT, (args, invocation) => {
            const thread = invocation.threadId;
            const pass = queuePass.get(thread);
            if (boundary !== 261 || pass === undefined || caller(invocation) !== QUEUE_BEST_PROJECT_RETURN) return;
            const city = cityOf(args[0]);
            if (!target(city)) return;
            if (candidates.has(thread)) throw Error('Nested target project ranking');
            const sample = {thread, pass, buildQueue: city.add(CITY_BUILD_QUEUE), scoreOut: args[1]};
            candidates.set(thread, sample);
            return sample;
        }, ({thread, pass, scoreOut}, result) => {
            candidates.delete(thread);
            add({kind: 'project-winner', pass, project: result.toInt32(), q8: read(scoreOut, 0, 'i32')});
        });
        Interceptor.attach(address(PROJECT_COMPARISON), function () {
            if (!enabled) return;
            const sample = candidates.get(this.threadId);
            if (!sample) return;
            protect(() => {
                const c = this.context;
                const q8 = c.rcx.toInt32(), incumbentQ8 = read(c.r14, 0, 'i32');
                if (q8 <= incumbentQ8) return;
                const project = c.rbx.toInt32();
                if (project < 0 || project >= 4096) throw Error('Invalid project candidate index');
                const legal = canAdvance(sample.buildQueue, project, 0, ptr(0), 0) !== 0;
                add({kind: 'project-screen', pass: sample.pass, project, q8, incumbentQ8, legal});
                // Native JLE skips the row. Preserve the incumbent and let
                // the loop rank subsequent candidates without changing caches.
                if (!legal) c.rcx = ptr(incumbentQ8 >>> 0);
            });
        });
    }
    observe(CONTRACT_VALIDATE, (a, invocation) => {
        const from = caller(invocation);
        if (from !== RECEIVE_VALIDATE_RETURN && from !== QUEUE_VALIDATE_RETURN) return;
        if (!target(cityOf(a[1]))) return;
        const pass = queuePass.get(invocation.threadId) ?? null;
        if (from === QUEUE_VALIDATE_RETURN && pass === null) throw Error('Missing queue validation pass');
        return {pass, from, offer: contract(a[0])};
    }, (sample, result) => add({kind: 'contract-validate', ...sample, eligible: Boolean(result.toInt32() & 255)}));
    observe(CONTRACT_UPDATE, (a, invocation) => {
        if (caller(invocation) !== QUEUE_UPDATE_RETURN || !target(cityOf(a[1]))) return;
        const pass = queuePass.get(invocation.threadId);
        if (pass === undefined) throw Error('Missing queue update pass');
        return {pass, object: a[0], before: contract(a[0])};
    }, ({pass, object, before}) => {
        const after = contract(object);
        if (after.id !== before.id) throw Error('Contract identity changed in Update');
        add({kind: 'contract-update', pass, before, after});
    });
    observe(CONTRACT_EXECUTE, (a, invocation) => {
        if (caller(invocation) !== QUEUE_EXECUTE_RETURN || !target(cityOf(a[1]))) return;
        const pass = queuePass.get(invocation.threadId);
        if (pass === undefined) throw Error('Missing contract execution pass');
        return {pass, offer: contract(a[0])};
    }, (sample, result) => add({kind: 'contract-execute', ...sample, accepted: Boolean(result.toInt32() & 255)}));
    Interceptor.flush();
    installed = true;
    return true;
}

rpc.exports = {
    init,
    advance(turn) {
        boundary = turn;
        if (exchangeComponents) exchangeComponents.start();
        enabled = true;
    },
    snapshot() { return {records, active, fault}; },
    freeze() {
        enabled = false;
        const result = {records, active, fault};
        if (exchangeComponents && !active) {
            exchangeComponents.requestFreeze();
            // Preserve the archived Granary receipt shape.
            result[exchangeMode + 'Components'] = exchangeComponents.finishFreeze();
            result[exchangeMode + 'Income'] = exchangeIncome;
        }
        return result;
    },
};
