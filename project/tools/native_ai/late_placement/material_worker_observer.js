'use strict';

// Scoped replay of ordinary worker recruitment and protection, Windows XP2
// hotfix 092abfbb. The matching replay verifies the mapped game binaries.
// Gather the unit IDs actually under a job's control and the two native
// recruitment pools. The optional matched arm swaps two native tree updates.
const RECRUIT_WORKERS = 0x403190;
const FIND_UNIT_RETURN = 0x55523f;
const CHOOSE_WORKER = 0x553570;
const OFFER_CONTROLLED_UNITS = 0x543830;
const PROTECT_WORKER_UPDATE = 0x558870;
const READ_CONTROLLED_UNITS = 0x401ba0;
const PROTECT_UNIT_LIST_RETURN = 0x558981;
const UNIT_REQUEST_UNIT_CREATED = 0x3f9fa0;
const LUA_UNIT_BUILD_CHARGES = 0x6fde00;
const TREE_MANAGER_DO_TURN = 0x5639b0;
const TREE_UPDATE = 0x544360;
const MANAGER_UPDATE_RETURN = 0x5639ea;
const GAME_INSTANCE_SLOT = 0xb8aa68;
const GAME_TURN = 0xc0;
const CONTROL_PLAYER = 0x90;
const PLAYER_ID = 0xd8, PLAYER_UNITS = 0x6c8;
const UNIT_LIST_HEAD = 0xd0, UNIT_NODE_NEXT = 0x10;
const UNIT_ID = 0xb0, UNIT_TYPE = 0xc8, UNIT_X = 0xf8, UNIT_Y = 0xfc;
const UNIT_PROCESSED = 0x258, UNIT_DEPARTING = 0x2e8, UNIT_CONTROLLER = 0x300;
// The gameplay Lua Unit:GetBuildCharges wrapper at 6fde00 reads this field.
const UNIT_BUILD_CHARGES = 0x538;
const FIND_TARGET = 0x10, VECTOR_COUNT = 0x10;
const TREE_IMPROVEMENT = 0x2b8, TREE_CITY = 0x2f0, TREE_PLOT = 0x308;
const TREE_ALLOWS_RECRUITING = 0x180, TREE_CONTROL_ID = 0x1b0;
const TREE_REQUEST_PRIORITY = 0x1e0, TREE_PRESENT_VALUE = 0x210;
const TREE_OWNER = 0x228, TREE_OWNER_PLAYER = 0x330;
const MANAGER_TREE_HEAD = 0x388, MANAGER_TREE_NEXT = 0x10;
const TREE_NODE_COUNT = 0xa0, TREE_ROOT_STATUS = 0x108, TREE_SUSPENDED = 0x168;
const CITY_ID = 0xa8, CITY_OWNER = 0xd8, PLOT_COORDINATES = 0x28;
const REQUEST_STATE = 0xb0, REQUEST_ID = 0x110, REQUEST_CONTROLLER = 0x128;
const REQUEST_PLAYER = 0x140, REQUEST_UNIT = 0x178, REQUEST_KEEP_CONTROL = 0x1f0;
const MAX_UNITS = 512, MAX_EVENTS = 1024;
const MAX_TREES = 512;
// Build 26595377. Instruction and caller guards make this separate from the
// old Kish profile. The Axum route only observes the normal worker pass.
const AXUM_CORE_SHA = '4de40abf7c739f53c1f3f825863ace84dc220e5a42d87620e56fceaf3fbd4dc8';
const AXUM_BUILD_UPDATE = 0x551ac0, AXUM_BUILD_EXECUTE = 0x5513a0;
const NODE_WORKER = 0x50, NODE_IMPROVEMENT = 0x54, NODE_REPAIR = 0x58;
const AXUM_OPERATIONS = [
    [0x671e80, 0x5514f4, 'repair', '48895c241848896c2420564883ec30'],
    [0x665af0, 0x5514fb, 'build', '48896c2418488974242041564883ec30'],
    [0x74a420, 0x55150a, 'adjacent-build', '48895c2418555641574883ec30498bd8'],
    [0x665af0, 0x55163d, 'build', '48896c2418488974242041564883ec30'],
];

const memory = createStudyMemoryIO({ptr, findRangeByAddress: address => Process.findRangeByAddress(address)});
const events = [];
const recruiting = new Map(), protecting = new Map(), jobControllers = new Map();
let accepting = false, initialized = false, active = 0, fault = null, eventLimit = MAX_EVENTS;
let snapshotRoster = null;

function read(object, offset, type) {
    const result = memory.read(object.toString(), offset, type);
    if (result.error) throw Error(`Worker observation ${type} at ${offset}: ${result.error}`);
    return result.value;
}

function pointer(object, offset) { return ptr(read(object, offset, 'ptr')); }

function capture(event) {
    if (events.length >= eventLimit) throw Error('Worker observer evidence budget');
    events.push(event);
}

function guarded(action) {
    try { return action(); }
    catch (error) { accepting = false; fault ??= String(error); }
}

function unitState(unit) {
    return {unit: read(unit, UNIT_ID, 'i32'), x: read(unit, UNIT_X, 'i32'), y: read(unit, UNIT_Y, 'i32'),
        controller: read(unit, UNIT_CONTROLLER, 'i32'), processed: read(unit, UNIT_PROCESSED, 'u8'),
        departing: read(unit, UNIT_DEPARTING, 'u8'), charges: read(unit, UNIT_BUILD_CHARGES, 'i32')};
}

function roster(player, builder) {
    const collection = pointer(player, PLAYER_UNITS);
    const result = [];
    let node = pointer(collection, UNIT_LIST_HEAD);
    for (let count = 0; !node.isNull(); count++) {
        if (count === MAX_UNITS) throw Error('Worker roster exceeds capture limit');
        const unit = pointer(node, 0);
        if (read(unit, UNIT_TYPE, 'i32') === builder) result.push(unitState(unit));
        node = pointer(node, UNIT_NODE_NEXT);
    }
    return result;
}

function vector(vectorObject, stride, get) {
    const count = read(vectorObject, VECTOR_COUNT, 'u32');
    if (count > MAX_UNITS) throw Error('Worker vector exceeds capture limit');
    const result = [];
    const data = pointer(vectorObject, 0);
    for (let i = 0; i < count; i++) {
        const item = get(data, i * stride);
        if (item !== null) result.push(item);
    }
    return {count, items: result};
}

function tileDistance(x, y, tx, ty) {
    // The fixture is away from the wrapping boundary. Convert odd rows to
    // axial coordinates so the shortlist uses hex distance, not square distance.
    const q = x - (y - (y & 1)) / 2, tq = tx - (ty - (ty & 1)) / 2;
    return Math.max(Math.abs(q - tq), Math.abs(y - ty), Math.abs(q - tq + y - ty));
}

function attachEarlyDispatch(address, turn, returnRva, scope, targetsOfTree) {
    const phases = new Map();
    const testFinish = scope.earlyDispatch === 'finish';
    const firstInPass = scope.earlyDispatch === 'first' || testFinish;
    const eligible = (tree, priority) => {
        if (read(tree, TREE_REQUEST_PRIORITY, 'i32') !== priority || read(tree, TREE_SUSPENDED, 'u8') ||
            !read(tree, TREE_NODE_COUNT, 'u32')) return false;
        const status = read(pointer(tree, TREE_ROOT_STATUS), 0, 'i32');
        return status === 0 || status === 5;
    };
    function job(tree, scope) {
        const city = pointer(tree, TREE_CITY), site = pointer(tree, TREE_PLOT);
        const improvement = read(tree, TREE_IMPROVEMENT, 'i32');
        if (city.isNull() || site.isNull() || improvement < 0 || improvement >= 256 ||
            read(city, CITY_OWNER, 'i32') !== scope.player) return null;
        const coordinate = read(site, PLOT_COORDINATES, 'u32');
        return {tree, x: coordinate & 0xffff, y: coordinate >>> 16, improvement,
            city: read(city, CITY_ID, 'i32'), controller: read(tree, TREE_CONTROL_ID, 'i32'),
            value: read(tree, TREE_PRESENT_VALUE, 'i32') >> 8};
    }
    function schedule(call, partner, target, sample) {
        if (phases.has(call.threadId)) throw Error('Nested game tree manager pass');
        call.dispatch = {earlyTree: partner, repairTree: target, sample, promoted: false, deferred: false};
        phases.set(call.threadId, call.dispatch);
    }
    // Both stock updates still run exactly once at their ordinary priority.
    // Change only their order in this diagnostic. Unit recruitment, movement,
    // danger, ownership, work legality and production remain engine decisions.
    Interceptor.attach(address(TREE_MANAGER_DO_TURN), {
        onEnter(args) {
            if (!accepting || args[1].toInt32() !== 2) return;
            guarded(() => {
                const now = turn();
                const finishTurn = testFinish && now === 173;
                if (!finishTurn && (now < 161 || now > 172 || firstInPass && now !== 172)) return;
                const manager = args[0], player = pointer(manager, TREE_OWNER_PLAYER);
                if (player.isNull() || read(player, PLAYER_ID, 'i32') !== scope.player) return;
                const near = roster(player, scope.builder).filter(unit => !unit.processed && !unit.departing &&
                    unit.charges > 0 && tileDistance(unit.x, unit.y, 42, 29) <= 2);
                if (!near.length) return;
                const preceding = [];
                let target;
                const head = pointer(manager, MANAGER_TREE_HEAD);
                for (let node = head, count = 0; !node.isNull();
                    node = pointer(node, MANAGER_TREE_NEXT)) {
                    if (++count > MAX_TREES) throw Error('Early Builder test exceeded tree traversal bound');
                    const tree = pointer(node, 0);
                    if (!eligible(tree, 2) || !pointer(tree, TREE_OWNER).equals(manager)) continue;
                    const candidate = job(tree, scope);
                    if (!candidate) continue;
                    if (candidate.city === scope.city && candidate.improvement === scope.improvement &&
                        targetsOfTree(tree) === 2188) {
                        target = candidate;
                        break;
                    }
                    preceding.push(candidate);
                }
                if (!target || target.value <= 0) return;
                const first = pointer(head, 0);
                if (first.equals(target.tree)) return;
                if (finishTurn) {
                    // A Builder already on the reserved pillaged tile can
                    // finish immediately if stock protection and repair permit.
                    // Test one such turn before competing work can reassign it.
                    // Keep the normal comparison when the Builder still needs
                    // to travel. Repair itself spends movement and no charge.
                    const worker = near.find(unit => unit.x === target.x && unit.y === target.y &&
                        unit.controller === target.controller);
                    if (!worker) {
                        capture({kind: 'finish-window', turn: now, crew: near});
                        return;
                    }
                    schedule(this, first, target.tree, {kind: 'finish-window', turn: now, worker,
                        displacedFirstActive: eligible(first, 2)});
                    return;
                }
                for (const earlier of preceding) {
                    // Give the live repair first access only over lower-valued
                    // work seeking the same Builder. Keep a 32-utility margin
                    // during the probe and leave military priorities alone.
                    if (earlier.value <= 0 || target.value < earlier.value + 32) continue;
                    const worker = near.find(unit => unit.controller === earlier.controller ||
                        unit.controller === -1 && tileDistance(unit.x, unit.y, earlier.x, earlier.y) <= 2);
                    if (worker) {
                        const {tree: earlyTree, ...earlyJob} = earlier;
                        const {tree: repairTree, ...repairJob} = target;
                        // The first replay still let an independent tree take
                        // the Builder before the selected holder's slot. This
                        // single-turn variant tries the first native update in
                        // the pass, using the same identified, releasable holder.
                        if (firstInPass && (worker.controller !== earlier.controller ||
                            !read(earlyTree, TREE_ALLOWS_RECRUITING, 'u8'))) continue;
                        const partner = firstInPass ? first : earlyTree;
                        schedule(this, partner, repairTree, {kind: 'early-dispatch', turn: now,
                            earlier: earlyJob, supplier: repairJob, worker, firstInPass,
                            displacedFirstActive: firstInPass && eligible(first, 2)});
                        return;
                    }
                }
            });
        },
        onLeave() {
            const phase = this.dispatch;
            if (!phase) return;
            phases.delete(this.threadId);
            guarded(() => {
                if (phase.promoted !== phase.deferred) throw Error('Native tree update pair was incomplete');
                if (phase.promoted) capture(phase.sample);
            });
        },
    });
    Interceptor.attach(address(TREE_UPDATE), {
        onEnter(args) {
            // Finish an opened swap even if diagnostic logging hit its cap.
            const phase = phases.get(this.threadId);
            if (!phase || returnRva(this) !== MANAGER_UPDATE_RETURN) return;
            if (!phase.promoted && args[0].equals(phase.earlyTree)) {
                args[0] = phase.repairTree;
                phase.promoted = true;
            } else if (phase.promoted && !phase.deferred && args[0].equals(phase.repairTree)) {
                args[0] = phase.earlyTree;
                phase.deferred = true;
            }
        },
    });
}

function initialize(spec, scope) {
    if (initialized || Process.platform !== 'windows' || Process.arch !== 'x64' || Process.pointerSize !== 8)
        throw Error('Worker observer requires one Windows x64 game session');
    const normalize = path => path.replace(/\\/g, '/').toLowerCase();
    const modules = Process.enumerateModules();
    const game = modules.find(module => normalize(module.path) === normalize(spec.path));
    if (!game || game.size !== spec.image_size || !modules.some(module => normalize(module.path) === normalize(scope.cePath)))
        throw Error('Unexpected game or CE module');
    const axum = scope.axum === true;
    if (scope.player !== 5 || scope.city !== 131073 || !Number.isInteger(scope.builder) ||
        scope.builder < 0 || scope.builder >= 4096 || !Number.isInteger(scope.improvement) ||
        scope.improvement < 0 || scope.improvement >= 4096)
        throw Error('Worker observer requires a verified material fixture');
    const targets = new Map(scope.plots.map(site => [`${site.x},${site.y}`, site.plot]));
    const correctPlots = axum
        ? spec.sha256 === AXUM_CORE_SHA && !scope.earlyDispatch &&
            targets.get('52,24') === 1828 && targets.get('53,26') === 1977
        : targets.get('40,28') === 2112 && targets.get('42,29') === 2188;
    if (targets.size !== 2 || !correctPlots)
        throw Error('Worker observer scope differs from the verified fixture');
    if (axum) eventLimit = 8192;

    const address = rva => game.base.add(rva);
    const returnRva = invocation => invocation.returnAddress.sub(game.base).toInt32();
    const turn = () => read(pointer(address(GAME_INSTANCE_SLOT), 0), GAME_TURN, 'i32');
    if (scope.snapshotOnly) {
        if (!axum) throw Error('Boundary-only readback requires the Axum profile');
        // The checked global player lookup reads Game + 0x240, then the
        // player pointer array at +0x20. Read it only on an inactive boundary.
        const lookup = memory.readBytes(address(0x44f00).toString(), 0, 14);
        const slots = memory.readBytes(address(0x63d100).toString(), 0, 19);
        const hex = bytes => bytes.value?.map(v => v.toString(16).padStart(2, '0')).join('');
        if (hex(lookup) !== '8bd1488b0d5f5bb400e9f2815f00' ||
            hex(slots) !== '488b89400200004c63c2488b41204a8b04c0c3')
            throw Error('Axum player lookup fingerprint changed');
        const gamePlayers = 0x240, playerArray = 0x20;
        snapshotRoster = expected => {
            const state = pointer(address(GAME_INSTANCE_SLOT), 0);
            const array = pointer(pointer(state, gamePlayers), playerArray);
            const player = pointer(array, scope.player * Process.pointerSize);
            if (read(player, PLAYER_ID, 'i32') !== scope.player || turn() !== expected)
                throw Error('Unexpected player or clock at Axum boundary');
            return {turn: expected, player: scope.player, builders: roster(player, scope.builder)};
        };
        initialized = true;
        return true;
    }
    const recruitEntry = axum ? 0x403170 : RECRUIT_WORKERS;
    const recruitCaller = axum ? 0x55527f : FIND_UNIT_RETURN;
    const chooseEntry = axum ? 0x5535b0 : CHOOSE_WORKER;
    const releaseEntry = axum ? 0x543870 : OFFER_CONTROLLED_UNITS;
    const protectEntry = axum ? 0x5588b0 : PROTECT_WORKER_UPDATE;
    const controlledEntry = axum ? 0x401b80 : READ_CONTROLLED_UNITS;
    const controlledCaller = axum ? 0x5589c1 : PROTECT_UNIT_LIST_RETURN;
    const completedEntry = axum ? 0x3f9f80 : UNIT_REQUEST_UNIT_CREATED;
    const chargeEntry = axum ? 0x6fde40 : LUA_UNIT_BUILD_CHARGES;
    const workerManager = axum ? 0x5639f0 : TREE_MANAGER_DO_TURN;
    const workerUpdate = axum ? 0x5443a0 : TREE_UPDATE;
    const workerReturn = axum ? 0x563a2a : MANAGER_UPDATE_RETURN;
    for (const [rva, expected] of [
        [recruitEntry, '4d85c90f8451060000488bc44c8948'],
        [recruitCaller - 5, axum ? 'e8f1deeaff' : 'e851dfeaff'],
        [chooseEntry, '488bc448895010488948085553565741'],
        [releaseEntry, '48895c241048897424185557415441'],
        [protectEntry, '48895c2418555657415541564883ec60'],
        [controlledEntry, '48895c241048896c2418574883ec2041'],
        [controlledCaller - 5, axum ? 'e8bf91eaff' : 'e81f92eaff'],
        [completedEntry, '4889742418574883ec208b8178010000'],
        [chargeEntry, '40534883ec2041b001ba01000000488b'],
        // The manager and tree are already detoured by the dev CE package.
        // This passive profile does not attach to their modified entries.
        ...(axum ? [
            [AXUM_BUILD_UPDATE, '48895424105553565741544156488bec'],
            [AXUM_BUILD_EXECUTE, '48895c241048896c2418574883ec7048'],
            ...AXUM_OPERATIONS.map(([rva, , , prefix]) => [rva, prefix]),
        ] : [
            [workerManager, '48895c240848896c2410488974241848897c242041564883ec20488b99880300'],
            [workerUpdate, '895424105341554883ec58488bd9448bea8b89a000000085c90f849f01000048'],
            [workerReturn - 5, 'e87609feff'],
        ]),
    ]) {
        const bytes = memory.readBytes(address(rva).toString(), 0, expected.length / 2);
        if (bytes.error || bytes.value.map(v => v.toString(16).padStart(2, '0')).join('') !== expected)
            throw Error(`Worker observer code changed at ${rva.toString(16)}`);
    }
    const targetsOfTree = tree => {
        const plot = pointer(tree, TREE_PLOT);
        if (plot.isNull()) return undefined;
        const raw = read(plot, PLOT_COORDINATES, 'u32');
        return targets.get(`${raw & 0xffff},${raw >>> 16}`);
    };
    const pool = object => vector(object, 8, (data, offset) => {
        const unit = pointer(data, offset);
        return !unit.isNull() && read(unit, UNIT_TYPE, 'i32') === scope.builder ? unitState(unit) : null;
    });

    function observe(rva, enter, leave) {
        Interceptor.attach(address(rva), {
            onEnter(args) {
                if (!accepting) return;
                this.workerSample = guarded(() => {
                    if (axum && (turn() < 114 || turn() > 155)) return;
                    return enter(args, this);
                });
                if (this.workerSample) active++;
            },
            onLeave(value) {
                if (!this.workerSample) return;
                active--;
                guarded(() => leave(this.workerSample, value));
            },
        });
    }

    observe(recruitEntry, (args, call) => {
        if (returnRva(call) !== recruitCaller || args[3].isNull()) return;
        // Trusted callback arguments from the checked entry points. Filter
        // other players before reading range-checked diagnostic detail.
        const player = args[0].add(CONTROL_PLAYER).readPointer();
        if (player.isNull() || player.add(PLAYER_ID).readS32() !== scope.player) return;
        const location = pointer(args[3], FIND_TARGET);
        if (location.isNull()) return;
        const plot = targets.get(`${read(location, 0, 'i32')},${read(location, 4, 'i32')}`);
        if (plot === undefined) return;
        // FindAvailableUnit passes request/recruit priority and whole
        // Present Value separately. The latter enters the managed-unit pool
        // request after trying the available uncontrolled units.
        const sample = {kind: 'recruit', turn: turn(), plot, priority: args[1].toInt32(),
            controller: args[2].toInt32(), presentValue: args[4].toInt32(),
            before: roster(player, scope.builder), pools: []};
        if (sample.controller >= 0) jobControllers.set(sample.controller, plot);
        if (recruiting.has(call.threadId)) throw Error('Unexpected nested worker recruitment');
        recruiting.set(call.threadId, {sample, evaluator: args[3]});
        return {sample, player, thread: call.threadId};
    }, ({sample, player, thread}) => {
        recruiting.delete(thread);
        capture({...sample, after: roster(player, scope.builder)});
    });
    observe(chooseEntry, (args, call) => {
        const frame = recruiting.get(call.threadId);
        if (!frame || !frame.evaluator.equals(args[0])) return;
        return {frame, vector: args[1], candidates: pool(args[1])};
    }, ({frame, vector: units, candidates}, value) => {
        const selected = Boolean(value.toInt32() & 0xff);
        frame.sample.pools.push({candidates, selected: selected ? pool(units) : null});
    });
    // A tree may offer one of its controlled units to a stronger request.
    // Keep the two bid inputs beside the returned IDs. The offer is still
    // subject to the receiving evaluator and is separate from assignment.
    observe(releaseEntry, (args, call) => {
        const recruitingJob = recruiting.get(call.threadId)?.sample;
        if (!recruitingJob && !jobControllers.size) return;
        const tree = args[0];
        const holder = tree.add(TREE_CONTROL_ID).readS32();
        const heldJob = jobControllers.get(holder);
        if (!recruitingJob && heldJob === undefined) return;
        const owner = pointer(tree, TREE_OWNER);
        if (owner.isNull()) return;
        const player = pointer(owner, TREE_OWNER_PLAYER);
        if (player.isNull() || read(player, PLAYER_ID, 'i32') !== scope.player) return;
        const sample = {kind: 'release-offer', turn: turn(), plot: heldJob ?? recruitingJob.plot, holder,
            holderAllowsRecruiting: read(tree, TREE_ALLOWS_RECRUITING, 'u8') !== 0,
            holderPriority: read(tree, TREE_REQUEST_PRIORITY, 'i32'),
            holderValue: read(tree, TREE_PRESENT_VALUE, 'i32') >> 8, requester: args[5].toInt32(),
            requesterPriority: args[2].toInt32(), requesterValue: args[3].toInt32(),
            requesterOverride: (args[4].toInt32() & 0xff) !== 0};
        return {sample, units: args[1], heldJob};
    }, ({sample, units, heldJob}) => {
        const offered = vector(units, 4, (data, offset) => read(data, offset, 'i32'));
        if (heldJob !== undefined || offered.count) capture({...sample, offered});
    });
    observe(protectEntry, (args, call) => {
        const player = args[1], tree = args[2];
        if (player.isNull() || player.add(PLAYER_ID).readS32() !== scope.player || tree.isNull() ||
            (!axum && read(tree, TREE_IMPROVEMENT, 'i32') !== scope.improvement)) return;
        const city = pointer(tree, TREE_CITY);
        if (city.isNull() || read(city, CITY_OWNER, 'i32') !== scope.player ||
            read(city, CITY_ID, 'i32') !== scope.city) return;
        const plot = targetsOfTree(tree);
        if (plot === undefined) return;
        const sample = {kind: 'protect', turn: turn(), plot, roster: roster(player, scope.builder)};
        if (protecting.has(call.threadId)) throw Error('Unexpected nested worker protection');
        protecting.set(call.threadId, sample);
        return {sample, thread: call.threadId};
    }, ({sample, thread}, value) => {
        protecting.delete(thread);
        capture({...sample, status: value.toInt32()});
    });
    observe(controlledEntry, (args, call) => {
        const sample = protecting.get(call.threadId);
        if (!sample || returnRva(call) !== controlledCaller) return;
        return {sample, controller: args[1].toInt32(), vector: args[2]};
    }, ({sample, controller, vector: units}) => {
        sample.controller = controller;
        sample.units = vector(units, 4, (data, offset) => read(data, offset, 'i32'));
        if (controller >= 0) jobControllers.set(controller, sample.plot);
    });
    // More than one waiting ordinary contract can complete when the same
    // Builder is born. Capture each observed controller change in order.
    observe(completedEntry, args => {
        const request = args[0], unit = args[1];
        if (request.add(REQUEST_PLAYER).readS32() !== scope.player ||
            request.add(REQUEST_UNIT).readS32() !== scope.builder ||
            unit.add(UNIT_TYPE).readS32() !== scope.builder) return;
        const state = read(request, REQUEST_STATE, 'i32');
        if (state !== 3 && state !== 5) return;
        return {request, unit, sample: {kind: 'builder-created', turn: turn(), trainingCity: args[2].toInt32(),
            request: read(request, REQUEST_ID, 'i32'), controller: read(request, REQUEST_CONTROLLER, 'i32'),
            keepControl: read(request, REQUEST_KEEP_CONTROL, 'u8'), state, before: unitState(unit)}};
    }, ({request, unit, sample}) => {
        const state = read(request, REQUEST_STATE, 'i32');
        if (state !== sample.state) capture({...sample, stateAfter: state, after: unitState(unit)});
    });
    if (axum) {
        const executing = new Map();
        // Node fields are chosen by Update and consumed by Execute. The
        // operation request below records what Execute actually submitted
        // to its constructor, independently of the CSV description.
        const nodeState = node => ({unit: read(node, NODE_WORKER, 'i32'),
            improvement: read(node, NODE_IMPROVEMENT, 'i32'), repair: read(node, NODE_REPAIR, 'u8')});
        const job = (node, tree, player) => {
            if (tree.isNull() || player.isNull() || player.add(PLAYER_ID).readS32() !== scope.player) return;
            const city = pointer(tree, TREE_CITY);
            if (city.isNull() || read(city, CITY_ID, 'i32') !== scope.city) return;
            const plot = targetsOfTree(tree);
            if (plot === undefined) return;
            return {turn: turn(), plot, controller: read(tree, TREE_CONTROL_ID, 'i32'),
                planned: read(tree, TREE_IMPROVEMENT, 'i32'), node: nodeState(node),
                roster: roster(player, scope.builder)};
        };
        observe(AXUM_BUILD_UPDATE, args => {
            const before = job(args[0], args[2], args[1]);
            if (before) return {before, node: args[0]};
        }, ({before, node}, value) => capture({kind: 'build-update', ...before,
            after: nodeState(node), status: value.toInt32()}));
        observe(AXUM_BUILD_EXECUTE, (args, call) => {
            const sample = job(args[0], args[1], args[3]);
            if (!sample) return;
            if (executing.has(call.threadId)) throw Error('Unexpected nested Build Improvement');
            sample.requests = [];
            executing.set(call.threadId, sample);
            return {sample, thread: call.threadId};
        }, ({sample, thread}) => {
            executing.delete(thread);
            capture({kind: 'build-execute', ...sample});
        });
        for (const rva of new Set(AXUM_OPERATIONS.map(([entry]) => entry))) {
            observe(rva, (args, call) => {
                const sample = executing.get(call.threadId);
                if (!sample) return;
                const operation = AXUM_OPERATIONS.find(([entry, caller]) =>
                    entry === rva && caller === returnRva(call));
                if (operation) sample.requests.push({kind: operation[2], improvement: args[0].toInt32()});
            }, () => {});
        }
    }
    if (scope.earlyDispatch) attachEarlyDispatch(address, turn, returnRva, scope, targetsOfTree);
    Interceptor.flush();
    initialized = accepting = true;
    return true;
}

rpc.exports = {
    init: initialize,
    boundary(turn) {
        if (!snapshotRoster) throw Error('Boundary-only reads were not initialized');
        return snapshotRoster(turn);
    },
    freeze() {
        accepting = false;
        return {active, fault, events};
    },
};
