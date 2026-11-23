// Lua supplies on-site Builders for sole-supplier repairs. Give the native
// improvement tree an earlier update only when it already controls that unit.
// The original tree still checks protection, movement and repair legality.
namespace WorkerDispatch {

// XP2 092abfbb. Manager::DoTurn walks a linked list of trees and calls Update
// once per entry at the supplied priority. It runs the destroy pass afterward.
constexpr uintptr_t ManagerDoTurnRva = 0x5639b0, TreeUpdateRva = 0x544360;
constexpr uintptr_t ManagerUpdateReturnRva = 0x5639ea, GameInstanceRva = 0xb8aa68;
constexpr size_t ManagerPlayer = 0x330, ManagerTreeHead = 0x388, NextListNode = 0x10;
// Update checks node count, root state, native priority and suspension before
// touching the tree. The plot, city and improvement are its live decode fields.
constexpr size_t TreeNodeCount = 0xa0, TreeRoot = 0x108, TreeSuspended = 0x168;
constexpr size_t TreeControl = 0x1b0, TreePriority = 0x1e0;
constexpr size_t TreeValue = 0x210, TreeManager = 0x228;
constexpr size_t PlayerUnits = 0x6c8, UnitHead = 0xd0, UnitID = 0xb0, UnitType = 0xc8;
constexpr size_t UnitX = 0xf8, UnitY = 0xfc, UnitProcessed = 0x258;
constexpr size_t UnitDeparting = 0x2e8, UnitControl = 0x300, UnitCharges = 0x538, GameTurn = 0xc0;
constexpr int WorkerPriority = 2, MaxOffers = 4, MaxScan = 512;

using Update = bool(*)(const Byte*, int);
Update originalManager{}, originalTree{};
bool ready{};
std::atomic<bool> published{};
Receipt finishes{};
unsigned faults{};
// Keep custody attempts until the game clears its policy. Each key costs
// one entry only after a job is moved and there is at most one move per turn.
std::array<std::unordered_set<uint64_t>, MaxPlayers> finishingAttempts;
std::array<int, MaxPlayers> lastTurn{};

void Published(const Policy& packet) {
    finishes = {};
    if (!packet.width) {
        for (auto& attempts : finishingAttempts) attempts.clear();
        lastTurn.fill(-1);
    }
    published.store(packet.materialWorkerCount > 0, std::memory_order_relaxed);
}

bool active_at_priority(const Byte* tree) {
    if (!readable(tree, ImprovementTreePlotOffset + sizeof(const Byte*), false) ||
        !read_field<unsigned>(tree, TreeNodeCount) || read_field<uint8_t>(tree, TreeSuspended) ||
        read_field<int>(tree, TreePriority) != WorkerPriority)
        return false;
    const auto* root = read_field<const Byte*>(tree, TreeRoot);
    if (!readable(root, sizeof(int), false)) return false;
    const int state = read_field<int>(root, 0);
    return state == 0 || state == 5;
}

const Byte* find_unit(const Byte* collection, const MaterialWorkerOffer& offer) {
    auto* node = read_field<const Byte*>(collection, UnitHead);
    for (int count = 0; node && count < MaxScan; ++count) {
        if (!readable(node, NextListNode + sizeof(const Byte*), false)) break;
        const auto* unit = read_field<const Byte*>(node, 0);
        if (readable(unit, UnitCharges + sizeof(int), false) && read_field<int>(unit, UnitID) == offer.unit &&
            read_field<int>(unit, UnitType) == offer.unitType)
            return unit;
        node = read_field<const Byte*>(node, NextListNode);
    }
    return nullptr;
}

struct Assignment {
    MaterialWorkerOffer offer{};
    const Byte* job{};
    int controller{-1};
};

uint64_t assignment_key(int controller, int unit) {
    return (static_cast<uint64_t>(static_cast<uint32_t>(controller)) << 32) | static_cast<uint32_t>(unit);
}

Assignment choose(const Byte* manager, const Byte* head, const Byte* collection, int width,
                  const MaterialWorkerOffer& offer) {
    const auto* unit = find_unit(collection, offer);
    if (!unit || read_field<uint8_t>(unit, UnitProcessed) || read_field<uint8_t>(unit, UnitDeparting) ||
        read_field<int>(unit, UnitCharges) <= 0)
        return {};
    if (read_field<int>(unit, UnitX) != offer.x || read_field<int>(unit, UnitY) != offer.y) return {};
    const int holderId = read_field<int>(unit, UnitControl);
    if (holderId < 0) return {};
    auto* node = head;
    for (int count = 0; node && count < MaxScan; ++count) {
        if (!readable(node, NextListNode + sizeof(const Byte*), false)) break;
        const auto* tree = read_field<const Byte*>(node, 0);
        if (active_at_priority(tree) && read_field<const Byte*>(tree, TreeManager) == manager &&
            read_field<int>(tree, TreeControl) == holderId && read_field<int>(tree, TreeValue) > 0 &&
            read_field<int>(tree, ImprovementTreeKindOffset) == offer.improvement) {
            const auto* city = read_field<const Byte*>(tree, ImprovementTreeCityOffset);
            const auto* plot = read_field<const Byte*>(tree, ImprovementTreePlotOffset);
            if (readable(city, CityOwnerOffset + sizeof(int), false) && readable(plot, PlotYOffset + sizeof(int16_t), false) &&
                read_field<int>(city, CityOwnerOffset) == offer.player && read_field<int>(city, CityIdOffset) == offer.city &&
                read_field<int16_t>(plot, PlotXOffset) == offer.plot % width &&
                read_field<int16_t>(plot, PlotYOffset) == offer.plot / width)
                return {offer, tree, holderId};
        }
        node = read_field<const Byte*>(node, NextListNode);
    }
    return {};
}

struct Pass {
    const Byte* first{};
    const Byte* job{};
    mutable bool moved{}, replaced{};
};
thread_local const Pass* current{};

const Byte* substitute_tree(const Pass& pass, const Byte* tree) {
    if (!pass.moved && tree == pass.first) {
        pass.moved = true;
        return pass.job;
    }
    if (pass.moved && !pass.replaced && tree == pass.job) {
        pass.replaced = true;
        return pass.first;
    }
    return tree;
}

bool update_tree(const Byte* tree, int priority) {
    // Restrict the argument swap to the manager's qualified traversal call.
    // Each tree still executes once. Do not rewrite native lists or priorities.
    if (current && priority == WorkerPriority && _ReturnAddress() ==
        Runtime::GetGameCoreGlobalAt<void*>(ManagerUpdateReturnRva))
        tree = substitute_tree(*current, tree);
    return originalTree(tree, priority);
}

#ifdef CE_AI_DISTRICT_SCORES_TEST
bool test_order() {
    const Byte trees[3]{};
    const Pass pass{&trees[0], &trees[2]};
    const auto* first = substitute_tree(pass, &trees[0]);
    const auto* middle = substitute_tree(pass, &trees[1]);
    const auto* final = substitute_tree(pass, &trees[2]);
    return first == &trees[2] && middle == &trees[1] && final == &trees[0] && pass.moved && pass.replaced;
}

bool test_existing_custody() {
    std::array<Byte, 1> manager{};
    std::array<Byte, NextListNode + sizeof(void*)> unitNode{}, treeNode{};
    std::array<Byte, UnitHead + sizeof(void*)> collection{};
    std::array<Byte, UnitCharges + sizeof(int)> unit{};
    std::array<Byte, ImprovementTreePlotOffset + sizeof(void*)> tree{};
    std::array<Byte, CityOwnerOffset + sizeof(int)> city{};
    std::array<Byte, PlotYOffset + sizeof(int16_t)> plot{};
    const int root = 5;
    const auto put = [](auto& object, size_t offset, auto value) {
        std::memcpy(object.data() + offset, &value, sizeof(value));
    };
    const MaterialWorkerOffer offer{5, 131073, 2188, 1, 4390912, 7, 42, 29};
    put(collection, UnitHead, unitNode.data());
    put(unitNode, 0, unit.data());
    put(unit, UnitID, offer.unit);
    put(unit, UnitType, offer.unitType);
    put(unit, UnitX, offer.x);
    put(unit, UnitY, offer.y);
    put(unit, UnitCharges, 1);
    put(treeNode, 0, tree.data());
    put(tree, TreeRoot, &root);
    put(tree, TreeNodeCount, 1u);
    put(tree, TreeManager, manager.data());
    put(tree, TreeControl, 5);
    put(tree, TreePriority, WorkerPriority);
    put(tree, TreeValue, Q8Units);
    put(tree, ImprovementTreeKindOffset, offer.improvement);
    put(tree, ImprovementTreeCityOffset, city.data());
    put(tree, ImprovementTreePlotOffset, plot.data());
    put(city, CityOwnerOffset, offer.player);
    put(city, CityIdOffset, offer.city);
    put(plot, PlotXOffset, int16_t{42});
    put(plot, PlotYOffset, int16_t{29});

    const auto selected = [&] {
        return choose(manager.data(), treeNode.data(), collection.data(), 74, offer).job == tree.data();
    };
    put(unit, UnitControl, -1);
    if (selected()) return false;
    put(unit, UnitControl, 6);
    if (selected()) return false;
    put(unit, UnitControl, 5);
    if (!selected()) return false;
    put(unit, UnitX, offer.x + 1);
    if (selected()) return false;
    put(unit, UnitX, offer.x);
    put(unit, UnitProcessed, uint8_t{1});
    if (selected()) return false;
    put(unit, UnitProcessed, uint8_t{0});
    put(unit, UnitCharges, 0);
    return !selected();
}
#endif

bool update_manager(const Byte* manager, int priority) {
    if (priority != WorkerPriority || !published.load(std::memory_order_relaxed) || current ||
        !readable(manager, ManagerTreeHead + sizeof(const Byte*), false))
        return originalManager(manager, priority);
    const auto* player = read_field<const Byte*>(manager, ManagerPlayer);
    const auto* head = read_field<const Byte*>(manager, ManagerTreeHead);
    const auto* game = *Runtime::GetGameCoreGlobalAt<const Byte**>(GameInstanceRva);
    if (!readable(player, PlayerUnits + sizeof(const Byte*), false) || !readable(head, sizeof(const Byte*), false) ||
        !readable(game, GameTurn + sizeof(int), false))
        return originalManager(manager, priority);
    const int pid = read_field<int>(player, PlayerIdOffset), turn = read_field<int>(game, GameTurn);
    const auto* collection = read_field<const Byte*>(player, PlayerUnits);
    if (!valid_player(pid) || !readable(collection, UnitHead + sizeof(const Byte*), false))
        return originalManager(manager, priority);

    std::array<MaterialWorkerOffer, MaxOffers> offers{};
    size_t count = 0;
    int width = 0;
    long epoch = 0;
    {
        std::shared_lock guard(policyMutex);
        if (enabled && !faults && policy.allowed[pid] && lastTurn[pid] != turn) {
            width = policy.width;
            epoch = generation;
            for (int i = 0; i < policy.materialWorkerCount && count < offers.size(); ++i) {
                const auto& offer = policy.materialWorkers[i];
                if (offer.player == pid) offers[count++] = offer;
            }
        }
    }
    const auto* first = read_field<const Byte*>(head, 0);
    Assignment selected;
    for (size_t i = 0; i < count; ++i) {
        const auto candidate = choose(manager, head, collection, width, offers[i]);
        if (!candidate.job || candidate.job == first) continue;
        std::unique_lock guard(policyMutex);
        if (!enabled || generation != epoch || lastTurn[pid] == turn) break;
        if (!finishingAttempts[pid].insert(assignment_key(candidate.controller, candidate.offer.unit)).second)
            continue;
        lastTurn[pid] = turn;
        selected = candidate;
        break;
    }
    if (!selected.job) return originalManager(manager, priority);
    const Pass pass{first, selected.job};
    ScopedContext scope(current, pass);
    const bool result = originalManager(manager, priority);
    {
        std::unique_lock guard(policyMutex);
        if (pass.moved != pass.replaced) ++faults;
        if (enabled && generation == epoch && pass.replaced) {
            const auto& q = selected.offer;
            finishes.add({pid, q.city, q.plot, q.improvement, q.unit, selected.controller, turn});
        }
    }
    return result;
}

void Install(const Byte* base) {
    using Runtime::DescribeHook;
    using Runtime::GetGameCoreGlobalAt;
    if (prefix(base, ManagerDoTurnRva, std::to_array<Byte>({0x48,0x89,0x5c,0x24,0x08,0x48,0x89,0x6c,0x24,0x10,0x48,0x89,0x74,0x24,0x18})) &&
        prefix(base, TreeUpdateRva, std::to_array<Byte>({0x89,0x54,0x24,0x10,0x53,0x41,0x55,0x48,0x83,0xec,0x58,0x48,0x8b,0xd9})) &&
        prefix(base, ManagerUpdateReturnRva - 5, std::to_array<Byte>({0xe8,0x76,0x09,0xfe,0xff}))) {
        const Runtime::HookSpec hooks[] = {
            DescribeHook("Material worker priority pass", GetGameCoreGlobalAt<Update>(ManagerDoTurnRva), &update_manager, &originalManager),
            DescribeHook("Material worker tree update", GetGameCoreGlobalAt<Update>(TreeUpdateRva), &update_tree, &originalTree),
        };
        ready = Runtime::InstallHookGroup(hooks);
    }
}

int stage_offer(lua_State* L) {
    const MaterialWorkerOffer offer{hks::checkinteger(L, 1), hks::checkinteger(L, 2), hks::checkinteger(L, 3),
        hks::checkinteger(L, 4), hks::checkinteger(L, 5), hks::checkinteger(L, 6),
        hks::checkinteger(L, 7), hks::checkinteger(L, 8)};
    bool ok;
    {
        std::unique_lock guard(policyMutex);
        ok = staging_valid && ready && !faults && valid_player(offer.player) && staging.allowed[offer.player] &&
            offer.city >= 0 && offer.plot >= 0 && offer.plot < staging.width * staging.height &&
            offer.x == offer.plot % staging.width && offer.y == offer.plot / staging.width &&
            offer.improvement >= 0 && offer.improvement < 4096 && offer.unit >= 0 && offer.unitType >= 0 && offer.unitType < 4096 &&
            staging.materialWorkerCount < static_cast<int>(staging.materialWorkers.size());
        if (ok) {
            const auto end = staging.materialWorkers.begin() + staging.materialWorkerCount;
            const auto paid = std::any_of(staging.builders.begin(), staging.builders.begin() + staging.builderCount,
                [&](const auto& x) {return x.player == offer.player && x.city == offer.city && x.plot == offer.plot &&
                    x.improvement == offer.improvement && x.deltaQ8 > 0;});
            ok = paid && std::count_if(staging.materialWorkers.begin(), end, [&](const auto& x) {return x.player == offer.player;}) < MaxOffers &&
                !std::any_of(staging.materialWorkers.begin(), end, [&](const auto& x) {
                    return x.player == offer.player && (x.plot == offer.plot || x.unit == offer.unit);
                });
        }
        if (ok) staging.materialWorkers[staging.materialWorkerCount++] = offer;
        else staging_valid = false;
    }
    return integer_result(L, ok);
}

} // namespace WorkerDispatch
