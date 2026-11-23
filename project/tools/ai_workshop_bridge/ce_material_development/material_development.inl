// Optional CE consumers for current material work. CSC publishes live, exact
// requests together with the district and improvement packet. The engine owns
// prerequisites, recruitment, city queues, movement and the completed job.
// Included by AIDistrictScores.cpp after the shared packet and ABI helpers.
namespace MaterialDevelopment {

// Windows Steam XP2 hotfix 092abfbb. Each member is qualified with the entry
// bytes below as well as the owning module's full GameCore identity check.
constexpr uintptr_t QueueTechRva = 0x4fa9a0, CompareTechRowsRva = 0x4f60d0;
constexpr uintptr_t QueueCivicRva = 0x418860, CompareCivicRowsRva = 0x40de20;
constexpr uintptr_t BuildFromCityRva = 0x55ba40, InitializeUnitRequestRva = 0x3f9300;
constexpr uintptr_t BuildFromCityUnitReturnRva = 0x55be9c;
constexpr size_t PlayerIdOffset = 0xd8;
constexpr size_t ResearchRowSize = 0x50, FullValueOffset = 0x14;
struct ResearchLayout {
    size_t player, rows, count, goal, owned, turns, step;
};
constexpr ResearchLayout Technology{0x98, 0x200, 0x210, 0x00, 0x18, 0x1c, 0x04};
constexpr ResearchLayout Civic{0x90, 0x4f0, 0x500, 0x08, 0x0c, 0x18, 0x1c};
constexpr size_t ImprovementTreeCityOffset = 0x2f0, ImprovementTreePlotOffset = 0x308;
constexpr size_t ImprovementTreeKindOffset = 0x2b8;
constexpr size_t UnitRequestIdOffset = 0x110;
constexpr int MaxTopics = 4, MaxResearchRows = 4096;
constexpr int MaxResearchQ8 = 64 * Q8Units, MaxRequestQ8 = 128 * Q8Units;

using Byte = unsigned char;
using Clock = std::chrono::steady_clock;
using Queue = void(*)(const Byte*, int);
// Technology's comparator takes an excluded-index pointer in R8. Culture
// takes the index in R8D. Separate signatures preserve both Win64 ABIs.
using CompareTech = const Byte*(*)(const Byte*, const Byte*, const int*);
using CompareCivic = const Byte*(*)(const Byte*, const Byte*, int);
using BuildFromCity = void(*)(void*, const Byte*, void*, const Byte*);
using InitUnitRequest = void*(*)(const Byte*, void*, int, int, int, int, int, int, bool);
Queue originalQueueTech{}, originalQueueCivic{};
CompareTech originalCompareTech{};
CompareCivic originalCompareCivic{};
BuildFromCity originalBuildFromCity{};
InitUnitRequest originalInitUnitRequest{};
bool techReady{}, civicReady{}, builderReady{};
namespace WorkerDispatch { void Published(const Policy& packet); }

struct Receipt {
    unsigned count{};
    std::array<int, 8> first{};
    void add(std::array<int, 8> sample) {
        if (!count++) first = sample;
    }
};
std::array<Receipt, 2> researchReceipts{};
Receipt builderReceipt{};
uint64_t nativeMicros{};
std::array<bool, MaxPlayers> sponsored{};
std::atomic<bool> researchPublished{}, builderPublished{};
// Written under the shared publication lock. Stale native frames may finish
// their original call, but cannot append receipts or claim a new packet slot.
void Published(const Policy& packet) {
    researchReceipts = {};
    builderReceipt = {};
    nativeMicros = 0;
    sponsored.fill(false);
    researchPublished.store(packet.materialResearchCount > 0, std::memory_order_relaxed);
    builderPublished.store(packet.materialRequestCount > 0, std::memory_order_relaxed);
    WorkerDispatch::Published(packet);
}

template <typename Scope> class ScopedContext {
    const Scope*& slot;
    const Scope* previous;
public:
    ScopedContext(const Scope*& target, const Scope& current) : slot(target), previous(target) { slot = &current; }
    ~ScopedContext() { slot = previous; }
    ScopedContext(const ScopedContext&) = delete;
    ScopedContext& operator=(const ScopedContext&) = delete;
};
struct ResearchContext {
    int player{}, kind{};
    const Byte* rows{};
    unsigned count{};
    long generation{};
    std::array<MaterialResearchOffer, MaxTopics> topics{};
    size_t topicCount{};
};
thread_local const ResearchContext* researchContext{};

bool valid_player(int player) { return player >= 0 && player < MaxPlayers; }

void queue_research(const Byte* object, int excluded, int kind, Queue original) {
    const auto layout = kind == 0 ? Technology : Civic;
    ResearchContext context{};
    if (enabled && researchPublished.load(std::memory_order_relaxed) &&
        readable(object, layout.count + sizeof(unsigned), false)) {
        const auto player = read_field<const Byte*>(object, layout.player);
        if (readable(player, PlayerIdOffset + sizeof(int), false)) {
            context.player = read_field<int>(player, PlayerIdOffset);
            context.kind = kind;
            context.rows = read_field<const Byte*>(object, layout.rows);
            context.count = read_field<unsigned>(object, layout.count);
            std::shared_lock guard(policyMutex);
            if (enabled && valid_player(context.player) && policy.allowed[context.player]) {
                context.generation = generation;
                for (int i = 0; i < policy.materialResearchCount && context.topicCount < context.topics.size(); ++i) {
                    const auto& offer = policy.materialResearch[i];
                    if (offer.player == context.player && offer.kind == kind) context.topics[context.topicCount++] = offer;
                }
            }
        }
    }
    ScopedContext scope(researchContext, context);
    original(object, excluded);
}
void queue_tech(const Byte* object, int excluded) { queue_research(object, excluded, 0, originalQueueTech); }
void queue_civic(const Byte* object, int excluded) { queue_research(object, excluded, 1, originalQueueCivic); }

template <typename Compare, typename Excluded>
const Byte* compare_research(int kind, const Byte* first, const Byte* last, int excludedIndex,
    Compare original, Excluded excluded) {
    const auto* context = researchContext;
    if (!context || context->kind != kind || !context->topicCount || context->rows != first ||
        !context->count || context->count > MaxResearchRows)
        return original(first, last, excluded);
    const auto size = context->count * ResearchRowSize;
    if (!readable(first, size, false) || first + size != last) return original(first, last, excluded);
    const auto started = Clock::now();
    const auto layout = kind == 0 ? Technology : Civic;
    // The shipped max-element reads numeric fields only. Compare a copy so
    // no research score persists or is visible to any other engine worker.
    // Convert the winner back to its real row before the queue checks legality.
    std::unique_ptr<Byte[]> copy;
    int matchedRows = 0, firstGoal = -1, firstDelta = 0, firstBase = 0;
    for (unsigned i = 0; i < context->count; ++i) {
        const auto offset = i * ResearchRowSize;
        const auto row = first + offset;
        const int goal = read_field<int>(row, layout.goal);
        const auto end = context->topics.begin() + context->topicCount;
        const auto topic = std::find_if(context->topics.begin(), end, [goal](const auto& a) { return a.index == goal; });
        if (topic == end || row[layout.owned] || read_field<int>(row, layout.turns) < 1 ||
            read_field<int>(row, layout.step) == excludedIndex) continue;
        const int base = read_field<int>(row, FullValueOffset);
        if (base < 0 || base > INT_MAX - topic->deltaQ8) continue;
        if (!copy) {
            copy.reset(new (std::nothrow) Byte[size]);
            if (!copy) return original(first, last, excluded);
            std::memcpy(copy.get(), first, size);
            firstGoal = goal;
            firstBase = base;
            firstDelta = topic->deltaQ8;
        }
        const int adjustedValue = base + topic->deltaQ8;
        std::memcpy(copy.get() + offset + FullValueOffset, &adjustedValue, sizeof adjustedValue);
        ++matchedRows;
    }
    const auto baseline = original(first, last, excluded);
    if (!copy) return baseline;
    const auto result = first + (original(copy.get(), copy.get() + size, excluded) - copy.get());
    std::unique_lock guard(policyMutex);
    if (!enabled || generation != context->generation) return baseline;
    nativeMicros += std::chrono::duration_cast<std::chrono::microseconds>(Clock::now() - started).count();
    researchReceipts[kind].add({context->player, matchedRows, firstGoal, firstBase, firstDelta,
        baseline != last ? read_field<int>(baseline, layout.goal) : -1,
        result != last ? read_field<int>(result, layout.goal) : -1,
        result != last ? read_field<int>(result, layout.step) : -1});
    return result;
}
const Byte* compare_tech(const Byte* first, const Byte* last, const int* excluded) {
    if (!researchContext || !excluded) return originalCompareTech(first, last, excluded);
    return compare_research(0, first, last, *excluded, originalCompareTech, excluded);
}
const Byte* compare_civic(const Byte* first, const Byte* last, int excluded) {
    return compare_research(1, first, last, excluded, originalCompareCivic, excluded);
}

struct BuilderContext {
    MaterialBuilderOffer offer{};
    long generation{};
    bool valid{};
};
thread_local const BuilderContext* builderContext{};

void build_from_city(void* node, const Byte* tree, void* arg, const Byte* playerObject) {
    BuilderContext context{};
    // Ordinary Farm and Mine trees carry their improvement index, city and
    // plot with a zero trigger marker. Use the exact admitted job tuple here.
    // The initializer also checks the native caller and requested unit.
    if (enabled && builderPublished.load(std::memory_order_relaxed) &&
        readable(tree, ImprovementTreePlotOffset + sizeof(const Byte*), false) &&
        readable(playerObject, PlayerIdOffset + sizeof(int), false)) {
        const int player = read_field<int>(playerObject, PlayerIdOffset);
        const auto cityObject = read_field<const Byte*>(tree, ImprovementTreeCityOffset);
        const auto plot = read_field<const Byte*>(tree, ImprovementTreePlotOffset);
        if (valid_player(player) && readable(cityObject, CityOwnerOffset + sizeof(int), false) &&
            read_field<int>(cityObject, CityOwnerOffset) == player && readable(plot, PlotYOffset + sizeof(int16_t), false)) {
            const int city = read_field<int>(cityObject, CityIdOffset);
            const int improvement = read_field<int>(tree, ImprovementTreeKindOffset);
            const int x = read_field<int16_t>(plot, PlotXOffset), y = read_field<int16_t>(plot, PlotYOffset);
            std::shared_lock guard(policyMutex);
            if (enabled && policy.allowed[player] && !sponsored[player] &&
                x >= 0 && x < policy.width && y >= 0 && y < policy.height) {
                const int index = x + y * policy.width;
                const auto begin = policy.materialRequests.begin(), end = begin + policy.materialRequestCount;
                const auto match = std::find_if(begin, end, [=](const auto& offer) {
                    return offer.player == player && offer.city == city && offer.plot == index && offer.improvement == improvement;
                });
                if (match != end) context = {*match, generation, true};
            }
        }
    }
    ScopedContext scope(builderContext, context);
    originalBuildFromCity(node, tree, arg, playerObject);
}

void* initialize_unit_request(const Byte* request, void* output, int unit, int player, int control,
    int priority, int extraValue, int requiredCity, bool keepControl) {
    int delta = 0;
    const auto* context = builderContext;
    // The unit overload takes extra present value in whole utility units.
    // Leave the priority and all other native arguments unchanged. Only the
    // original Build City Improvement request can draw on this exact quote.
    if (context && context->valid && context->offer.player == player && context->offer.unit == unit &&
        reinterpret_cast<uintptr_t>(_ReturnAddress()) == Runtime::GameCoreAddress + BuildFromCityUnitReturnRva &&
        extraValue >= 0 && extraValue <= INT_MAX / Q8Units - MaxRequestQ8 / Q8Units) {
        std::unique_lock guard(policyMutex);
        if (enabled && generation == context->generation && !sponsored[player]) {
            delta = context->offer.deltaQ8 / Q8Units;
            sponsored[player] = true;
        }
    }
    auto result = originalInitUnitRequest(request, output, unit, player, control, priority, extraValue + delta, requiredCity, keepControl);
    if (delta) {
        const int id = readable(request, UnitRequestIdOffset + sizeof(int), false) ? read_field<int>(request, UnitRequestIdOffset) : -1;
        std::unique_lock guard(policyMutex);
        if (enabled && generation == context->generation) builderReceipt.add({player, context->offer.city,
            context->offer.plot, context->offer.improvement, unit, extraValue, extraValue + delta, id});
    }
    return result;
}

template <size_t N> bool prefix(const Byte* base, uintptr_t rva, const std::array<Byte, N>& bytes) {
    return std::memcmp(base + rva, bytes.data(), bytes.size()) == 0;
}
#include "material_worker_dispatch.inl"

void Install(const Byte* base, bool improvementReady) {
    using Runtime::DescribeHook;
    using Runtime::GetGameCoreGlobalAt;
    if (prefix(base, QueueTechRva, std::to_array<Byte>({0x40,0x55,0x53,0x57,0x48,0x8d,0x6c,0x24,0xb9,0x48,0x81,0xec})) &&
        prefix(base, CompareTechRowsRva, std::to_array<Byte>({0x48,0x89,0x5c,0x24,0x08,0x48,0x89,0x7c,0x24,0x10,0x49,0x8b,0xf8}))) {
        const Runtime::HookSpec hooks[] = {
            DescribeHook("Queue material technology", GetGameCoreGlobalAt<Queue>(QueueTechRva), &queue_tech, &originalQueueTech),
            DescribeHook("Compare material technology rows", GetGameCoreGlobalAt<CompareTech>(CompareTechRowsRva), &compare_tech, &originalCompareTech),
        };
        techReady = Runtime::InstallHookGroup(hooks);
    }
    if (prefix(base, QueueCivicRva, std::to_array<Byte>({0x40,0x55,0x41,0x54,0x41,0x57,0x48,0x8d,0x6c,0x24,0xb9})) &&
        prefix(base, CompareCivicRowsRva, std::to_array<Byte>({0x4c,0x8b,0xda,0x4c,0x8b,0xc9,0x48,0x3b,0xca,0x74,0x5e}))) {
        const Runtime::HookSpec hooks[] = {
            DescribeHook("Queue material civic", GetGameCoreGlobalAt<Queue>(QueueCivicRva), &queue_civic, &originalQueueCivic),
            DescribeHook("Compare material civic rows", GetGameCoreGlobalAt<CompareCivic>(CompareCivicRowsRva), &compare_civic, &originalCompareCivic),
        };
        civicReady = Runtime::InstallHookGroup(hooks);
    }
    if (improvementReady &&
        prefix(base, BuildFromCityRva, std::to_array<Byte>({0x40,0x55,0x57,0x41,0x54,0x41,0x55,0x48,0x8d,0x6c,0x24,0xc1})) &&
        prefix(base, InitializeUnitRequestRva, std::to_array<Byte>({0x48,0x89,0x5c,0x24,0x08,0x48,0x89,0x6c,0x24,0x10,0x44,0x89,0x44,0x24,0x18})) &&
        prefix(base, BuildFromCityUnitReturnRva - 5, std::to_array<Byte>({0xe8,0x64,0xd4,0xe9,0xff}))) {
        const Runtime::HookSpec hooks[] = {
            DescribeHook("Material job city recruitment", GetGameCoreGlobalAt<BuildFromCity>(BuildFromCityRva), &build_from_city, &originalBuildFromCity),
            DescribeHook("Material job unit request", GetGameCoreGlobalAt<InitUnitRequest>(InitializeUnitRequestRva), &initialize_unit_request, &originalInitUnitRequest),
        };
        builderReady = Runtime::InstallHookGroup(hooks);
    }
    if (improvementReady) WorkerDispatch::Install(base);
}

int stage_research(lua_State* L) {
    const MaterialResearchOffer offer{hks::checkinteger(L, 1), hks::checkinteger(L, 2),
        hks::checkinteger(L, 3), hks::checkinteger(L, 4)};
    bool ok;
    {
        std::unique_lock guard(policyMutex);
        ok = staging_valid && valid_player(offer.player) && staging.allowed[offer.player] &&
            ((offer.kind == 0 && techReady) || (offer.kind == 1 && civicReady)) && offer.index >= 0 &&
            offer.index < MaxResearchRows && offer.deltaQ8 > 0 && offer.deltaQ8 <= MaxResearchQ8 &&
            staging.materialResearchCount < static_cast<int>(staging.materialResearch.size());
        const auto begin = staging.materialResearch.begin(), end = begin + staging.materialResearchCount;
        if (ok) ok = !std::any_of(begin, end, [&](const auto& a) {
            return a.player == offer.player && a.kind == offer.kind && a.index == offer.index;
        }) && std::count_if(begin, end, [&](const auto& a) { return a.player == offer.player; }) < MaxTopics;
        if (ok) staging.materialResearch[staging.materialResearchCount++] = offer;
        else staging_valid = false;
    }
    return integer_result(L, ok);
}

int stage_builder(lua_State* L) {
    const MaterialBuilderOffer offer{hks::checkinteger(L, 1), hks::checkinteger(L, 2), hks::checkinteger(L, 3),
        hks::checkinteger(L, 4), hks::checkinteger(L, 5), hks::checkinteger(L, 6)};
    bool ok;
    {
        std::unique_lock guard(policyMutex);
        const auto begin = staging.builders.begin(), end = begin + staging.builderCount;
        ok = staging_valid && builderReady && valid_player(offer.player) && staging.allowed[offer.player] &&
            offer.unit >= 0 && offer.unit < MaxResearchRows && offer.deltaQ8 >= Q8Units && offer.deltaQ8 <= MaxRequestQ8 &&
            staging.materialRequestCount < static_cast<int>(staging.materialRequests.size()) &&
            std::any_of(begin, end, [&](const auto& row) {
                return row.player == offer.player && row.city == offer.city && row.plot == offer.plot &&
                    row.improvement == offer.improvement && row.deltaQ8 > 0;
            });
        if (ok) staging.materialRequests[staging.materialRequestCount++] = offer;
        else staging_valid = false;
    }
    return integer_result(L, ok);
}

int status(lua_State* L) {
    char output[1280];
    {
        std::shared_lock guard(policyMutex);
        int n = snprintf(output, sizeof output,
            "{\"abi\":1,\"version\":%d,\"techReady\":%d,\"civicReady\":%d,\"builderReady\":%d,"
            "\"researchLimitQ8\":%d,\"builderLimitQ8\":%d,\"researchOffers\":%d,\"builderOffers\":%d,\"comparisonMicros\":%llu,"
            "\"workerReady\":%d,\"workerFinishOnly\":1,\"workerOffers\":%d,\"workerFaults\":%u",
            policy.version, techReady, civicReady, builderReady, MaxResearchQ8, MaxRequestQ8,
            policy.materialResearchCount, policy.materialRequestCount, static_cast<unsigned long long>(nativeMicros),
            WorkerDispatch::ready && !WorkerDispatch::faults, policy.materialWorkerCount, WorkerDispatch::faults);
        const auto append = [&](const char* name, const Receipt& receipt) {
            const auto& a = receipt.first;
            n += snprintf(output + n, sizeof output - n,
                ",\"%s\":%u,\"%sFirst\":[%d,%d,%d,%d,%d,%d,%d,%d]",
                name, receipt.count, name, a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7]);
        };
        append("tech", researchReceipts[0]);
        append("civic", researchReceipts[1]);
        append("builder", builderReceipt);
        append("workerFinish", WorkerDispatch::finishes);
        output[n] = '}';
        output[n + 1] = 0;
    }
    push_json(L, output, strlen(output));
    return 1;
}

#ifdef CE_AI_DISTRICT_SCORES_TEST
// Exercise the scoped copy and pointer translation against synthetic layouts.
// The ordinary game remains the ABI test for actual rows and native wrappers.
bool test_comparison(int kind) {
    const auto layout = kind == 0 ? Technology : Civic;
    std::array<Byte, 2 * ResearchRowSize> rows{};
    auto* first = rows.data();
    auto* second = first + ResearchRowSize;
    auto* last = second + ResearchRowSize;
    const auto put = [](Byte* row, size_t offset, int value) {
        std::memcpy(row + offset, &value, sizeof value);
    };
    put(first, layout.goal, 11);
    put(first, layout.step, 3);
    put(first, layout.turns, 5);
    put(first, FullValueOffset, 3 * Q8Units);
    put(second, layout.goal, 12);
    put(second, layout.step, 12);
    put(second, layout.turns, 4);
    put(second, FullValueOffset, 5 * Q8Units);
    const auto before = rows;
    const auto fakeCompare = [](const Byte* a, const Byte*, int) {
        const auto b = a + ResearchRowSize;
        return read_field<int>(a, FullValueOffset) > read_field<int>(b, FullValueOffset) ? a : b;
    };
    ResearchContext context{1, kind, first, 2, generation};
    context.topics[0] = {1, kind, 11, 4 * Q8Units};
    context.topicCount = 1;
    ScopedContext scope(researchContext, context);
    const bool wasEnabled = enabled.exchange(true);
    researchReceipts[kind] = {};
    const auto result = compare_research(kind, first, last, -1, fakeCompare, -1);
    const auto excluded = compare_research(kind, first, last, 3, fakeCompare, 3);
    first[layout.owned] = 1;
    const auto owned = compare_research(kind, first, last, -1, fakeCompare, -1);
    first[layout.owned] = 0;
    enabled = wasEnabled;
    const auto& receipt = researchReceipts[kind];
    return result == first && excluded == second && owned == second && rows == before &&
        receipt.count == 1 && receipt.first[5] == 12 && receipt.first[6] == 11 && receipt.first[7] == 3;
}

bool test_builder_scope() {
    // This is the ordinary improvement payload shape seen in the live Farm
    // and Mine traces. All unrelated bytes, including the marker, stay zero.
    constexpr size_t ObservedTriggerMarkerOffset = 0x330;
    std::array<Byte, ObservedTriggerMarkerOffset + 1> tree{};
    std::array<Byte, CityOwnerOffset + sizeof(int)> city{};
    std::array<Byte, PlayerIdOffset + sizeof(int)> player{};
    std::array<Byte, PlotYOffset + sizeof(int16_t)> plot{};
    const auto put = [](auto& data, size_t offset, auto value) {
        std::memcpy(data.data() + offset, &value, sizeof value);
    };
    const auto oldOffer = policy.materialRequests[0];
    const int oldCount = policy.materialRequestCount, oldWidth = policy.width, oldHeight = policy.height;
    const bool oldAllowed = policy.allowed[5], oldSponsored = sponsored[5];
    const bool oldEnabled = enabled.exchange(true), oldPublished = builderPublished.exchange(true);
    const auto oldExecute = originalBuildFromCity;
    policy.width = 74; policy.height = 46;
    policy.allowed[5] = true; sponsored[5] = false;
    policy.materialRequests[0] = {5, 131073, 2112, 1, 1, MaxRequestQ8};
    policy.materialRequestCount = 1;
    put(player, PlayerIdOffset, 5);
    put(city, CityOwnerOffset, 5);
    put(city, CityIdOffset, 131073);
    put(plot, PlotXOffset, int16_t{40});
    put(plot, PlotYOffset, int16_t{28});
    put(tree, ImprovementTreeCityOffset, city.data());
    put(tree, ImprovementTreePlotOffset, plot.data());
    put(tree, ImprovementTreeKindOffset, 1);
    originalBuildFromCity = [](void*, const Byte*, void* result, const Byte*) {
        *static_cast<bool*>(result) = builderContext && builderContext->valid;
    };
    bool matched = false, unrelated = true;
    build_from_city(nullptr, tree.data(), &matched, player.data());
    put(tree, ImprovementTreeKindOffset, 2);
    build_from_city(nullptr, tree.data(), &unrelated, player.data());

    originalBuildFromCity = oldExecute;
    policy.materialRequests[0] = oldOffer;
    policy.materialRequestCount = oldCount;
    policy.width = oldWidth; policy.height = oldHeight;
    policy.allowed[5] = oldAllowed; sponsored[5] = oldSponsored;
    enabled = oldEnabled; builderPublished = oldPublished;
    return matched && !unrelated && !builderContext;
}
#endif

} // namespace MaterialDevelopment
