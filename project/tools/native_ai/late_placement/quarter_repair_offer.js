'use strict';

// One matched Alexandria diagnostic on Windows XP2 hotfix 092abfbb. The
// calls and layouts below follow CheckForDistrict (3e0ee0), with a separate
// stock one-use tree. The city slot, score cache and production queue stay
// under the game's ownership. This diagnostic is separate from the CE API.
const REPAIR_NATIVE = {
    player: [0x44f00, '8bd1488b0d5f5bb400e972815f00'],
    map: [0x44d40, '488b05215db4004885c07408488b8048'],
    districtAt: [0x11e520, '48895c240848896c2410488974241857'],
    constructTrigger: [0x48c8c0, '83c8ff33d28901894104895108668941'],
    copyTrigger: [0xd6160, '48895c2418574883ec30488d7910488b'],
    alignedFree: [0x9908f0, '48ff25896d0200'],
    emptyString: [0x993b30, '4883ec2865488b042558000000'],
    formatString: [0x993930, '48895424104c894424184c894c242048'],
    assignString: [0x993700, '48895c24184889742420574883ec2048'],
    destroyString: [0x993590, '40534883ec20488b19e892050000483b'],
    createTree: [0x563840, '40534883ec304533c948c74424200000'],
    addController: [0x53feb0, '48895c24104489442418574883ec2048'],
    findController: [0x4019f0, '448bc283faff74454c8b911001000048'],
    destroyTree: [0x563960, '48895c2408574883ec20488bf9418bd8'],
    uninitializeTree: [0x544020, '48895c24104889742418555741544156'],
    decodeCityPlotValueReturn: [0x55afcc, '8b08c1f908010be9a1020000'],
    decodeSuccessEpilogue: [0x55b72b, '4881c440010000415e415d5dc3'],
    submitContract: [0x403c70, '48895c2420564883ec2048833a00488b'],
    executeContract: [0x3f8310, '405553574156488d6c24c14881eca800'],
};

const REPAIR_CITY_PRIORITY = 0x198, REPAIR_CITY_DISTRICT_TEMPLATE = 0x408;
const REPAIR_TEMPLATE_NAME = 0x10;
const REPAIR_CITY_DISTRICTS = 0xb58;
const REPAIR_PLAYER_TREES = 0x6a8, REPAIR_PLAYER_CONTROL = 0x6b0;
const REPAIR_MAP_FIND_PLOT = 0x50, REPAIR_PLOT_OWNERSHIP = 0x30;
const REPAIR_PLOT_CITY_ID = 0xc, REPAIR_PLOT_OWNER = 0x1c;
const REPAIR_DISTRICT_TYPE = 0xf0, REPAIR_DISTRICT_PILLAGED = 0x458;
const REPAIR_TRIGGER_SIZE = 0xe0, REPAIR_TRIGGER_DISTRICT = 0x1c;
const REPAIR_TRIGGER_CITY = 0x70, REPAIR_TRIGGER_PLOT = 0x88, REPAIR_TRIGGER_BUFFER = 0x98;
const REPAIR_TREE_PARENT = 0x120, REPAIR_TREE_CONTROLLER_ID = 0x1b0, REPAIR_TREE_ID = 0x1c8;
const REPAIR_TREE_CONTROLLER = 0x218, REPAIR_TREE_TRIGGER = 0x270;
const REPAIR_TREE_DECODED_Q8 = 0x210, REPAIR_TREE_TRIGGER_BONUS = 0x288, REPAIR_TREE_TRIGGER_BASE = 0x340;
const REPAIR_CONTROLLER_BACKLINK = 0x10;
const REPAIR_CONTRACT_STATE = 0xb0, REPAIR_CONTRACT_ID = 0x110, REPAIR_CONTRACT_OWNER = 0x128;
const REPAIR_CONTRACT_Q8 = 0x158, REPAIR_CONTRACT_DISTRICT = 0x1a8;

function makeQuarterRepairOffer(core, scope, fingerprint, currentTurn, record, protect) {
    const addr = name => core.base.add(REPAIR_NATIVE[name][0]);
    for (const [name, [, bytes]] of Object.entries(REPAIR_NATIVE)) fingerprint(addr(name), bytes);
    const call = (name, result, args) => new NativeFunction(addr(name), result, args);
    const playerFor = call('player', 'pointer', ['int']);
    const editMap = call('map', 'pointer', []);
    const districtAt = call('districtAt', 'pointer', ['pointer', 'pointer']);
    const constructTrigger = call('constructTrigger', 'pointer', ['pointer']);
    const copyTrigger = call('copyTrigger', 'void', ['pointer', 'pointer', 'uint8']);
    const freeTriggerBuffer = call('alignedFree', 'void', ['pointer']);
    const emptyString = call('emptyString', 'pointer', []);
    const formatString = call('formatString', 'void', ['pointer', 'pointer']);
    const assignString = call('assignString', 'void', ['pointer', 'pointer']);
    const destroyString = call('destroyString', 'void', ['pointer']);
    const createTree = call('createTree', 'pointer', ['pointer', 'pointer', 'pointer']);
    const addController = call('addController', 'void', ['pointer', 'pointer', 'int']);
    const findController = call('findController', 'pointer', ['pointer', 'int']);
    const destroyTree = call('destroyTree', 'void', ['pointer', 'int', 'int']);
    const displayName = Memory.allocUtf8String('City Alexandria Troas [CSC Quarter repair]');
    let attempted = false, active = null;
    const contract = object => ({id: read(object, REPAIR_CONTRACT_ID, 'i32'),
        state: read(object, REPAIR_CONTRACT_STATE, 'i32'), q8: read(object, REPAIR_CONTRACT_Q8, 'i32')});

    // At this Decode Trigger call site, R14 is the current tree, RAX points
    // to the city/plot present value and RBX points to the whole-unit sum
    // before this input is added. Use instruction probes so stock node
    // calls keep their original return addresses.
    Interceptor.attach(addr('decodeCityPlotValueReturn'), function () {
        if (!active || !this.context.r14.equals(active.tree)) return;
        protect(() => {
            active.presentQ8 = read(this.context.rax, 0, 'i32');
            active.accumulatedBeforePlot = read(this.context.rbx, 0, 'i32');
        });
    });
    Interceptor.attach(addr('decodeSuccessEpilogue'), function () {
        if (!active || !this.context.r14.equals(active.tree)) return;
        let admitted = false;
        try {
            protect(() => {
                const base = read(active.tree, REPAIR_TREE_TRIGGER_BASE, 'i32');
                const bonus = read(active.tree, REPAIR_TREE_TRIGGER_BONUS, 'i32');
                const q8 = read(active.tree, REPAIR_TREE_DECODED_Q8, 'i32');
                const {expectedQ8, selectorQ8, presentQ8, accumulatedBeforePlot} = active;
                const matchesStock = base === 0 && bonus === 0 && accumulatedBeforePlot === 0 &&
                    presentQ8 === selectorQ8 && q8 === expectedQ8;
                record({kind: 'repair-decode', turn: currentTurn(), q8, expectedQ8, base, bonus,
                    presentQ8: presentQ8 ?? null, accumulatedBeforePlot: accumulatedBeforePlot ?? null,
                    admitted: matchesStock});
                admitted = matchesStock;
            });
        } finally {
            active.presentQ8 = active.accumulatedBeforePlot = undefined;
            // EAX already holds stock success (1). Return the native failure
            // code for this exact diagnostic only, before reservation or bid.
            if (!admitted) this.context.rax = ptr(3);
        }
    });

    // SubmitContract receives the live native handle. Read its already-resolved
    // pointer so observing the request does not acquire or refresh a handle.
    Interceptor.attach(addr('submitContract'), {
        onEnter(args) {
            protect(() => {
                if (!active || !args[0].equals(active.control)) return;
                const request = ptr(read(args[1], 0, 'ptr'));
                if (request.isNull() || read(request, REPAIR_CONTRACT_OWNER, 'i32') !== active.controller) return;
                if (read(request, REPAIR_CONTRACT_DISTRICT, 'i32') !== scope.district)
                    throw Error('Repair tree submitted a different action');
                if (active.request !== undefined) throw Error('Repair tree submitted a second district request');
                active.request = read(request, REPAIR_CONTRACT_ID, 'i32');
                this.repairRequest = request;
            });
        },
        onLeave() {
            if (this.repairRequest) protect(() => record({kind: 'repair-request', turn: currentTurn(),
                ...contract(this.repairRequest)}));
        },
    });
    Interceptor.attach(addr('executeContract'), {
        onEnter(args) {
            protect(() => {
                if (!active || read(args[0], REPAIR_CONTRACT_OWNER, 'i32') !== active.controller) return;
                if (read(args[0], REPAIR_CONTRACT_ID, 'i32') === active.request)
                    this.repairExecution = contract(args[0]);
            });
        },
        onLeave(result) {
            if (this.repairExecution) protect(() => record({kind: 'repair-execute', turn: currentTurn(),
                ...this.repairExecution, result: result.toInt32()}));
        },
    });
    Interceptor.attach(addr('uninitializeTree'), {
        onEnter(args) {
            protect(() => {
                if (active && args[0].equals(active.tree)) this.repairEnding = active;
            });
        },
        onLeave() {
            if (!this.repairEnding) return;
            protect(() => {
                const {control, controller, id} = this.repairEnding;
                record({kind: 'repair-cleanup', turn: currentTurn(), tree: id, controller,
                    released: findController(control, controller).isNull()});
                active = null;
            });
        },
    });

    return function offer(build, stockTree, selection, threshold) {
        if (attempted) return;
        attempted = true;
        const {winner, sites} = selection;
        const [site] = sites;
        if (stockTree === -1 || !winner || winner.district !== 5 || winner.x !== 20 || winner.y !== 31 ||
            winner.q8 !== 1847362 || sites.length !== 1 || site.q8 !== 1445266 || site.eligible !== 1 ||
            site.owned !== 1 || site.reservation !== 6881299 || !threshold || threshold.liveReservation ||
            threshold.minimumExclusiveQ8 !== -2559744)
            throw Error('The exact stock Alexandria repair comparison did not reproduce');

        const city = ptr(read(build, CITY, 'ptr'));
        const player = playerFor(scope.player);
        const map = editMap();
        const coordinates = Memory.alloc(8);
        const x = site.plot % scope.width;
        coordinates.writeS32(x);
        coordinates.add(4).writeS32(Math.floor(site.plot / scope.width));
        const virtual = (object, offset, result, args) => {
            const method = ptr(read(read(object, 0, 'ptr'), offset, 'ptr'));
            if (method.compare(core.base) < 0 || method.compare(core.base.add(core.size)) >= 0)
                throw Error('Unexpected native repair vtable entry');
            return new NativeFunction(method, result, args);
        };
        const plot = virtual(map, REPAIR_MAP_FIND_PLOT, 'pointer', ['pointer', 'pointer'])(map, coordinates);
        const ownership = virtual(plot, REPAIR_PLOT_OWNERSHIP, 'pointer', ['pointer'])(plot);
        if (read(ownership, REPAIR_PLOT_CITY_ID, 'i32') !== scope.city ||
            read(ownership, REPAIR_PLOT_OWNER, 'u8') !== scope.player)
            throw Error('The repair footprint changed owners');
        // Use the same City::Districts lookup as CityBuild::BuildDistrict.
        const district = districtAt(city.add(REPAIR_CITY_DISTRICTS), coordinates);
        if (district.isNull() || read(district, REPAIR_DISTRICT_TYPE, 'i32') !== scope.district ||
            read(district, REPAIR_DISTRICT_PILLAGED, 'u8') !== 1)
            throw Error('The exact pillaged Quarter is absent');

        // Match the game's string and trigger lifetimes. The constructor
        // initializes the no-unlock sentinels for this completed district.
        // Frida keeps an allocation alive through its owning JS pointer. A
        // pointer returned by the native constructor does not own that memory.
        const trigger = Memory.alloc(REPAIR_TRIGGER_SIZE);
        constructTrigger(trigger);
        trigger.add(REPAIR_TRIGGER_DISTRICT).writeS32(scope.district);
        trigger.add(REPAIR_TRIGGER_CITY).writePointer(city);
        trigger.add(REPAIR_TRIGGER_PLOT).writePointer(plot);
        const template = Memory.alloc(8), label = Memory.alloc(8);
        template.writePointer(emptyString());
        label.writePointer(emptyString());
        const manager = ptr(read(player, REPAIR_PLAYER_TREES, 'ptr'));
        const control = ptr(read(player, REPAIR_PLAYER_CONTROL, 'ptr'));
        let tree = ptr(0), id = -1;
        try {
            const definition = read(build, REPAIR_CITY_DISTRICT_TEMPLATE, 'ptr');
            assignString(template, ptr(read(definition, REPAIR_TEMPLATE_NAME, 'ptr')));
            formatString(label, displayName);
            tree = createTree(manager, template, label);
            if (tree.isNull()) throw Error('Native repair tree creation failed');
            id = read(tree, REPAIR_TREE_ID, 'i32');
            if (id === -1 || id === stockTree || !ptr(read(tree, REPAIR_TREE_PARENT, 'ptr')).isNull())
                throw Error('Native repair tree identity differs');
            addController(tree, player, read(build, REPAIR_CITY_PRIORITY, 'i32'));
            const controller = read(tree, REPAIR_TREE_CONTROLLER_ID, 'i32');
            const owner = findController(control, controller);
            if (owner.isNull() || !ptr(read(owner, REPAIR_CONTROLLER_BACKLINK, 'ptr'))
                .equals(tree.add(REPAIR_TREE_CONTROLLER))) throw Error('The repair tree did not acquire its own controller');
            copyTrigger(tree.add(REPAIR_TREE_TRIGGER), trigger, x & 0xff);
            if (read(read(build, DISTRICT_TREE, 'ptr'), TREE_ID, 'i32') !== stockTree)
                throw Error('The ordinary district tree changed during repair admission');
            const expectedQ8 = (site.q8 >> 8) << 8;
            active = {tree, id, control, controller, expectedQ8, selectorQ8: site.q8};
            record({kind: 'repair-tree', turn: currentTurn(), tree: id, stockTree, controller, plot: site.plot,
                stockSelectorQ8: site.q8, expectedQ8, triggerBase: read(tree, REPAIR_TREE_TRIGGER_BASE, 'i32'),
                triggerBonus: read(tree, REPAIR_TREE_TRIGGER_BONUS, 'i32')});
        } catch (error) {
            if (!tree.isNull() && id !== -1 && id !== stockTree) destroyTree(manager, id, -1);
            throw error;
        } finally {
            destroyString(label);
            destroyString(template);
            // This is our own live scratch allocation. Frida's game-memory
            // range enumeration can omit its agent heap, so read it through
            // the allocation handle and free only the native vector buffer.
            const buffer = trigger.add(REPAIR_TRIGGER_BUFFER).readPointer();
            if (!buffer.isNull()) freeTriggerBuffer(buffer);
        }
    };
}
