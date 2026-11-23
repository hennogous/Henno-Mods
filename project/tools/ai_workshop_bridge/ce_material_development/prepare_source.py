"""Apply the material decision consumers to an isolated CE source copy."""

import argparse
from pathlib import Path
import shutil


REPLACEMENTS = (
    ('#include <mutex>', '#include <mutex>\n#include <new>\n#include <unordered_set>'),
    ('constexpr int MaxBuilderBidQ8 = 64 * Q8Units;', '''// Allow larger live transaction quotes only for the exact improvement row.
// This transport bound matches the material request bound. Native eligibility,
// the untuned score and ordinary improvement competition still apply.
constexpr int MaxBuilderBidQ8 = 128 * Q8Units;'''),
    ('struct Policy {', '''struct MaterialResearchOffer { int player, kind, index, deltaQ8; };
struct MaterialBuilderOffer { int player, city, plot, improvement, unit, deltaQ8; };
struct MaterialWorkerOffer { int player, city, plot, improvement, unit, unitType, x, y; };
struct Policy {
    // Bound each material decision list to four entries per AI player.
    int materialResearchCount{}, materialRequestCount{}, materialWorkerCount{};
    std::array<MaterialResearchOffer, MaxPlayers * 4> materialResearch{};
    std::array<MaterialBuilderOffer, MaxPlayers * 4> materialRequests{};
    std::array<MaterialWorkerOffer, MaxPlayers * 4> materialWorkers{};'''),
    ('    value.hasLateEntries = false;', '''    value.materialResearchCount = value.materialRequestCount = value.materialWorkerCount = 0;
    value.hasLateEntries = false;'''),
    ('#include "native/district_candidate_decline_api.inl"', '''#include "native/district_candidate_decline_api.inl"
#include "native/material_development.inl"'''),
    ('            policy = staging;', '''            policy = staging;
            MaterialDevelopment::Published(policy);'''),
    ('    clear_policy(policy);', '''    clear_policy(policy);
    MaterialDevelopment::Published(policy);'''),
    ('    return hooks_ready;\n}\n\nvoid RegisterLua(', '''    if (hooks_ready) MaterialDevelopment::Install(reinterpret_cast<const unsigned char*>(Runtime::GameCoreAddress), builder_ready);
    return hooks_ready;
}

void RegisterLua('''),
    ('    PushLuaMethod(L, l_builder_allow,', '''    PushLuaMethod(L, MaterialDevelopment::stage_research, "CE_AIMaterialResearchBid", hks::LUA_GLOBAL, "CE_AIMaterialResearchBid");
    PushLuaMethod(L, MaterialDevelopment::stage_builder, "CE_AIMaterialBuilderRequestBid", hks::LUA_GLOBAL, "CE_AIMaterialBuilderRequestBid");
    PushLuaMethod(L, MaterialDevelopment::WorkerDispatch::stage_offer, "CE_AIMaterialWorkerFinishOffer", hks::LUA_GLOBAL, "CE_AIMaterialWorkerFinishOffer");
    PushLuaMethod(L, MaterialDevelopment::status, "CE_AIMaterialDevelopmentStatus", hks::LUA_GLOBAL, "CE_AIMaterialDevelopmentStatus");
    PushLuaMethod(L, l_builder_allow,'''),
)


def prepare(source, output):
    source = source.resolve(strict=True)
    output = output.resolve()
    if output.exists() or source in output.parents:
        raise ValueError('Use a new directory outside the input checkout')
    module = Path('CivilizationVI_CommunityExtension') / 'AIDistrictScores.cpp'
    content = (source / module).read_text(encoding='utf-8')
    for anchor, replacement in REPLACEMENTS:
        if content.count(anchor) != 1:
            raise ValueError(f'CE source has an unexpected layout at {anchor!r}')
        content = content.replace(anchor, replacement, 1)

    shutil.copytree(source, output, ignore=shutil.ignore_patterns('.git', '.vs', '__pycache__'))
    (output / module).write_text(content, encoding='utf-8')
    for name in ('material_development.inl', 'material_worker_dispatch.inl'):
        shutil.copy2(Path(__file__).with_name(name), output / module.parent / 'native' / name)
    selftest = output / module.parent / 'native' / 'tests' / 'district_score_checks.inl'
    test_content = selftest.read_text(encoding='utf-8')
    # The base CE test deliberately exercises the full transport limit with a
    # stock value of 29,056 Q8. Update both expectations with the new ceiling.
    for old, new in (
        ('pasture.deltaQ8 == 64 * Q8Units', 'pasture.deltaQ8 == 128 * Q8Units'),
        ('adjusted_builder_score(29056, InvalidScore, pasture) == 45440',
         'adjusted_builder_score(29056, InvalidScore, pasture) == 61824'),
    ):
        if test_content.count(old) != 1:
            raise ValueError(f'CE builder test has an unexpected layout at {old!r}')
        test_content = test_content.replace(old, new, 1)
    anchor = '#undef CHECK'
    if test_content.count(anchor) != 1:
        raise ValueError('CE self-test layout has changed')
    selftest.write_text(test_content.replace(anchor, '''    CHECK(MaterialDevelopment::test_comparison(0));
    CHECK(MaterialDevelopment::test_comparison(1));
    CHECK(MaterialDevelopment::test_builder_scope());
    CHECK(MaterialDevelopment::WorkerDispatch::test_order());
    CHECK(MaterialDevelopment::WorkerDispatch::test_existing_custody());

'''+anchor), encoding='utf-8')
    host = selftest.with_name('selftest.cpp')
    host_content = host.read_text(encoding='utf-8')
    if host_content.count('checks != 259') != 1:
        raise ValueError('CE self-test count has changed')
    host.write_text(host_content.replace('checks != 259', 'checks != 264'), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    prepare(args.source, args.output)
