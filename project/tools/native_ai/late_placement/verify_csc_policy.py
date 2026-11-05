"""Check the main CSC Lua rules against an actual reconciled native ledger."""

import argparse
import json
from pathlib import Path
import sys

from calibrate import calibrate

ROOT = Path(__file__).resolve().parents[4]
POLICY = ROOT / 'Civ Supply Chains/Lua_UI/AI/CSC_AI_QuarterPlacement.lua'


def check(analysis, dependencies):
    sys.path.insert(0, str(dependencies.resolve()))
    from lupa.lua51 import LuaRuntime

    lua = LuaRuntime()
    lua.execute(POLICY.read_text(encoding='utf-8-sig'))
    evaluate = lua.globals().CSC_AI_QuarterPlacement.BakersAdjustment
    reference = calibrate(analysis)
    site = lua.table(districtType=reference['district'], legal=True, hills=False, riverEdges=0)
    buildings = lua.table()
    for item in reference['buildings']:
        buildings[item['building']] = lua.table(rawQ8=item['raw_q8'], rootCreditsQ8=lua.table())
    for item in reference['root_receipts']:
        buildings[item['building']].rootCreditsQ8[item['modifier']] = item['credit_q8']
    forecast = lua.table(beforeQ8=reference['before_aggregation_q8'],
                         nativeQ8=reference['expected_native_q8'], buildings=buildings)
    assert evaluate(site, forecast) == reference['delta_q8']
    site.riverEdges = 2
    assert evaluate(site, forecast) is None
    site.riverEdges, site.hills = 0, True
    assert evaluate(site, forecast) is None
    site.hills = False
    forecast.nativeQ8 += 1
    assert evaluate(site, forecast) is None
    forecast.nativeQ8 -= 1
    root = reference['root_receipts'][0]
    buildings[root['building']].rootCreditsQ8[root['modifier']] = None
    assert evaluate(site, forecast) is None
    return reference


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--analysis', type=Path, required=True)
    parser.add_argument('--dependencies', type=Path, required=True)
    args = parser.parse_args()
    result = check(json.loads(args.analysis.read_text(encoding='utf-8-sig')), args.dependencies)
    print(json.dumps(dict(verified=True, delta_q8=result['delta_q8'], corrected_q8=result['corrected_q8'])))
