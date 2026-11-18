"""Offline policy-return SQL, gameplay events and merged native/CSC UI regression.

Reads a gameplay database into memory; never changes the cache or live game.
Use the frozen optional-mod database for broad unique-district coverage.
"""
import argparse
import sqlite3
import sys
import zlib
from pathlib import Path

from test_parity import CODE, ROOT, TESTS, lua_value, untype


EXPECTED = {
    ('BAKERS', 'DISTRICT_COMMERCIAL_HUB', 'POLICY_TOWN_CHARTERS'),
    ('BAKERS', 'DISTRICT_COMMERCIAL_HUB', 'POLICY_ECONOMIC_UNION'),
    ('TAILORS', 'DISTRICT_HARBOR', 'POLICY_NAVAL_INFRASTRUCTURE'),
    ('TAILORS', 'DISTRICT_HARBOR', 'POLICY_ECONOMIC_UNION'),
    ('TAILORS', 'DISTRICT_COMMERCIAL_HUB', 'POLICY_TOWN_CHARTERS'),
    ('TAILORS', 'DISTRICT_COMMERCIAL_HUB', 'POLICY_ECONOMIC_UNION'),
    ('TAILORS', 'DISTRICT_HOLY_SITE', 'POLICY_SCRIPTURE'),
    ('TAILORS', 'DISTRICT_THEATER', 'POLICY_AESTHETICS'),
    ('TAILORS', 'DISTRICT_THEATER', 'POLICY_SPORTS_MEDIA'),
}


def policy_declarations(db):
    for quarter in ('BAKERS', 'TAILORS'):
        pending = ''
        for line in (ROOT / f'Civ Supply Chains/Data/CSC_Q_{quarter}.sql').read_text(encoding='utf-8-sig').splitlines(True):
            pending += line
            if sqlite3.complete_statement(pending):
                if 'INSERT OR IGNORE INTO CSC_QuarterPolicyAdjacencyConfig' in pending:
                    db.executescript(pending)
                pending = ''


def database(source):
    db = sqlite3.connect(':memory:')
    with sqlite3.connect(source.resolve().as_uri() + '?mode=ro', uri=True) as original:
        original.backup(db)
    db.row_factory = sqlite3.Row
    db.create_function('Make_Hash', 1, lambda value: zlib.crc32(value.encode()))
    db.execute('PRAGMA foreign_keys=ON')
    old_violations = {tuple(r) for r in db.execute('PRAGMA foreign_key_check')}
    native = [tuple(r) for r in db.execute("SELECT * FROM PolicyModifiers WHERE ModifierId NOT LIKE 'ATTACH_MOD_CSC_ADJ_%' ORDER BY PolicyType,ModifierId")]
    for name in ('Schema', 'Sources'):
        db.executescript((CODE / f'CSC_Adjacency{name}.sql').read_text(encoding='utf-8-sig'))
    policy_declarations(db)
    configs = {tuple(r) for r in db.execute('SELECT QuarterKey,DistrictType,PolicyType FROM CSC_QuarterPolicyAdjacencyConfig')}
    assert configs == EXPECTED, configs ^ EXPECTED
    for name in ('Processor', 'Modifiers'):
        db.executescript((CODE / f'CSC_Adjacency{name}.sql').read_text(encoding='utf-8-sig'))
    new_violations = {tuple(r) for r in db.execute('PRAGMA foreign_key_check')} - old_violations
    assert not new_violations, new_violations
    assert native == [tuple(r) for r in db.execute("SELECT * FROM PolicyModifiers WHERE ModifierId NOT LIKE 'ATTACH_MOD_CSC_ADJ_%' ORDER BY PolicyType,ModifierId")]
    rules = [dict(r) for r in db.execute("SELECT * FROM CSC_AdjacencyRules WHERE ModifierOwner='PolicyModifiers' ORDER BY ID")]
    expected = set()
    for quarter, district, policy in configs:
        targets = {district} | {r[0] for r in db.execute('SELECT CivUniqueDistrictType FROM DistrictReplaces WHERE ReplacesDistrictType=?', (district,))}
        for target in targets:
            matches = db.execute("SELECT ID FROM CSC_AdjacencyRules WHERE DistrictType=? AND CustomAdjacentObject=? AND ModifierOwner='DistrictModifiers' AND ProvideType='SelfBonus'", (target, f'DISTRICT_CSC_{quarter}_QUARTER')).fetchall()
            assert len(matches) == 1, (quarter, target, matches)
            expected.add(matches[0][0] + '_' + policy)
    assert {r['ID'] for r in rules} == expected
    for rule in rules:
        base_id = rule['ID'].removesuffix('_' + rule['WhoIsTheOwner'])
        base = dict(db.execute('SELECT * FROM CSC_AdjacencyRules WHERE ID=?', (base_id,)).fetchone())
        for key in base:
            if key not in ('ID', 'ModifierOwner', 'WhoIsTheOwner'):
                assert base[key] == rule[key], (rule['ID'], key)
        district_base = db.execute('SELECT ReplacesDistrictType FROM DistrictReplaces WHERE CivUniqueDistrictType=?', (rule['DistrictType'],)).fetchone()
        district_base = district_base[0] if district_base else rule['DistrictType']
        expected_yield = 'YIELD_FOOD' if rule['CustomAdjacentObject'] == 'DISTRICT_CSC_BAKERS_QUARTER' else ('YIELD_PRODUCTION' if district_base == 'DISTRICT_HARBOR' else 'YIELD_CULTURE')
        assert rule['YieldType'] == expected_yield, rule
        for bit in (1,2,4,8,16,32,64,128,256,512):
            modifier = f"MOD_CSC_ADJ_{rule['ID']}_{bit}"
            assert db.execute('SELECT 1 FROM PolicyModifiers WHERE PolicyType=? AND ModifierId=?', (rule['WhoIsTheOwner'], 'ATTACH_' + modifier)).fetchone()
            assert db.execute("SELECT Value FROM ModifierArguments WHERE ModifierId=? AND Name='ModifierId'", ('ATTACH_' + modifier,)).fetchone()[0] == modifier
            action = db.execute('SELECT M.OwnerRequirementSetId,D.CollectionType,D.EffectType FROM Modifiers M JOIN DynamicModifiers D USING(ModifierType) WHERE ModifierId=?', (modifier,)).fetchone()
            assert tuple(action)[1:] == ('COLLECTION_OWNER', 'EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE')
            requirement = db.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?', (action[0],)).fetchone()[0]
            assert db.execute("SELECT Value FROM RequirementArguments WHERE RequirementId=? AND Name='PropertyName'", (requirement,)).fetchone()[0] == f"CSC_ADJ_{rule['ID']}_{bit}"
            assert db.execute("SELECT Value FROM ModifierArguments WHERE ModifierId=? AND Name='Amount'", (modifier,)).fetchone()[0] == str(bit)
    counts = tuple(db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0] for table in ('CSC_AdjacencyRules', 'Modifiers', 'PolicyModifiers'))
    for name in ('Processor', 'Modifiers'):
        db.executescript((CODE / f'CSC_Adjacency{name}.sql').read_text(encoding='utf-8-sig'))
    assert counts == tuple(db.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0] for table in ('CSC_AdjacencyRules', 'Modifiers', 'PolicyModifiers'))
    return db, rules


def lua_checks(db, policy_rules):
    from lupa.lua51 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((TESTS / 'world.lua').read_text(encoding='utf-8'))
    g = lua.globals()

    def include(name):
        if name not in ('Civ6Common', 'MapEnums'):
            lua.execute(untype((CODE / f'{name}.lua').read_text(encoding='utf-8-sig')))

    g.include = include
    for table in ('Districts', 'Policies', 'TypeTags', 'CSC_AdjacencyRules', 'CSC_AdjacencyProviders', 'CSC_AdjacencySources', 'CSC_AdjacencyObjects', 'District_Adjacencies', 'AppealHousingChanges', 'DistrictReplaces', 'PolicyModifiers', 'Modifiers', 'DynamicModifiers', 'ModifierArguments', 'RequirementSets', 'RequirementSetRequirements', 'Requirements', 'RequirementArguments'):
        records = [dict(r) for r in db.execute('SELECT * FROM ' + table)]
        for index, record in enumerate(records):
            record['Index'] = index
        lua.execute('GameInfo.' + table + '=info(' + lua_value(records) + ')')
    # The generic world helper indexes Type keys; real GameInfo also indexes
    # the primary IDs used by modifier and requirement definitions.
    lua.execute('''
        for _,entry in ipairs({{'Modifiers','ModifierId'},{'Requirements','RequirementId'}}) do
            for row in GameInfo[entry[1]]() do GameInfo[entry[1]][row[entry[2]]]=row end
        end
    ''')
    # Standard native yield ordering; wrapper executes the real Firaxis formatter.
    yields = [{'Index': i, 'YieldType': 'YIELD_' + kind.upper(), 'Name': kind, 'IconString': '[ICON_' + kind + ']'} for i,kind in enumerate(('Food','Production','Gold','Science','Culture','Faith'))]
    lua.execute('GameInfo.Yields=info(' + lua_value(yields) + ')')
    lua.execute('''
        activePolicies={};
        for id=0,1 do
            local pid=id;
            local culture={IsPolicyActive=function(_,index) return activePolicies[pid..':'..index]==true end};
            Players[id].GetCulture=function() return culture end;
        end
        -- Real event names; no synthetic PolicyChanged fallback can hide a typo.
        Events={}; GameEvents={};
        for _,name in ipairs({'GovernmentPolicyChanged','GovernmentPolicyObsoleted','GovernmentChanged'}) do
            local callbacks={};
            Events[name]={Add=function(fn) callbacks[#callbacks+1]=fn end,
                Fire=function() for _,fn in ipairs(callbacks) do fn(0) end end};
        end
        function GetYieldString(kind,amount) return GameInfo.Yields[kind].IconString..'+'..string.format('%g',amount) end;
        function prepare(districtType, quarterType, count)
            resetWorld(); activePolicies={};
            for _,p in ipairs(world) do p.district=-1; p.owner=0; end;
            center.district=GameInfo.Districts[districtType].Index; center.complete=true;
            for direction=0,count-1 do
                local p=Map.GetAdjacentPlot(center.x,center.y,direction);
                p.district=GameInfo.Districts[quarterType].Index; p.owner=0;
                p.complete=true;
            end
            center.GetAdjacencyYield=function(_,playerID,cityID,districtIndex,yieldIndex)
                assert(playerID==0 and cityID==city:GetID() and districtIndex==center.district);
                return nativeYields[yieldIndex] or 0;
            end;
            center.GetAdjacencyBonusTooltip=function(_,_,_,_,yieldIndex)
                return 'Native '..yieldIndex,nil;
            end;
            nativeYields={};
        end
        function setPolicy(policyType,playerID)
            activePolicies[(playerID or 0)..':'..GameInfo.Policies[policyType].Index]=true;
        end
    ''')
    include('CSC_AdjacencyGameplay')
    cases = 0
    # Every base and unique district, each policy, and all possible ring-1 counts.
    for rule in policy_rules:
        base_id = rule['ID'].removesuffix('_' + rule['WhoIsTheOwner'])
        for count in range(7):
            g.prepare(rule['DistrictType'], rule['CustomAdjacentObject'], count)
            g.CSC_RefreshAdjacencies()
            assert g.center.GetProperty(g.center, 'CSC_ADJ_' + rule['ID'] + '_ENCODED_AMOUNT') == 0
            g.setPolicy('POLICY_URBAN_PLANNING', 0)
            g.Events.GovernmentPolicyChanged.Fire()
            assert g.center.GetProperty(g.center, 'CSC_ADJ_' + rule['ID'] + '_ENCODED_AMOUNT') == 0
            g.setPolicy(rule['WhoIsTheOwner'], 1)
            g.Events.GovernmentPolicyChanged.Fire()
            assert g.center.GetProperty(g.center, 'CSC_ADJ_' + rule['ID'] + '_ENCODED_AMOUNT') == 0
            g.setPolicy(rule['WhoIsTheOwner'], 0)
            g.Events.GovernmentPolicyChanged.Fire()
            for identity in (base_id, rule['ID']):
                assert g.center.GetProperty(g.center, 'CSC_ADJ_' + identity + '_ENCODED_AMOUNT') == count, (identity, count)
            # Ownership changes remove only the foreign Quarter contribution.
            if count:
                neighbor = g.Map.GetAdjacentPlot(g.center.x, g.center.y, 0)
                neighbor.owner = 1
                g.CSC_RefreshAdjacencies()
                assert g.center.GetProperty(g.center, 'CSC_ADJ_' + rule['ID'] + '_ENCODED_AMOUNT') == count - 1
                neighbor.owner = 0
                neighbor.district = -1
                g.CSC_RefreshAdjacencies()
                assert g.center.GetProperty(g.center, 'CSC_ADJ_' + rule['ID'] + '_ENCODED_AMOUNT') == count - 1
            lua.execute('activePolicies={}'); g.Events.GovernmentPolicyObsoleted.Fire()
            assert g.center.GetProperty(g.center, 'CSC_ADJ_' + rule['ID'] + '_ENCODED_AMOUNT') == 0
            cases += 1
    include('AdjacencyBonusSupport')
    for rule in policy_rules:
        for count in (0,1,2,6):
            g.prepare(rule['DistrictType'], rule['CustomAdjacentObject'], count)
            # Native query returns base adjacency. Theater Culture shares its yield
            # with the Tailors return; multiply native and CSC contributions once each.
            yield_index = g.GameInfo.Yields[rule['YieldType']].Index
            g.nativeYields[yield_index] = 8
            g.setPolicy(rule['WhoIsTheOwner'], 0)
            icons, tooltip, required = g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)
            native_total = 16 if rule['DistrictType'] in ('DISTRICT_THEATER', 'DISTRICT_ACROPOLIS') else 8
            assert icons == g.GetYieldString(rule['YieldType'], native_total + 2 * count), (rule['ID'], icons, count)
            assert required is None
            if count:
                sentence = g.CSC_Adjacency.PreviewLine(lua.table_from(rule), 2 * count, count)
                assert tooltip.count(sentence) == 1, (tooltip, sentence)
            else:
                assert tooltip == 'Native ' + str(yield_index)
            lua.execute('activePolicies={}')
            icons, _, _ = g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)
            assert icons == g.GetYieldString(rule['YieldType'], 8 + count)
            cases += 1
    # Different Quarters contribute different yields to the same Commercial Hub.
    g.prepare('DISTRICT_COMMERCIAL_HUB', 'DISTRICT_CSC_BAKERS_QUARTER', 2)
    lua.execute("Map.GetAdjacentPlot(center.x,center.y,2).district=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index; nativeYields[2]=10; setPolicy('POLICY_ECONOMIC_UNION')")
    icons, _, _ = g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)
    assert icons == '[ICON_Food]+4[NEWLINE][ICON_Gold]+20[NEWLINE][ICON_Culture]+2', icons
    # Exercise every direct vanilla policy effect from the real database. These
    # cases include native-only Campus/Industrial Zone and combined late cards.
    native_cases = [
        ('POLICY_TOWN_CHARTERS', 'DISTRICT_COMMERCIAL_HUB', 'YIELD_GOLD'),
        ('POLICY_ECONOMIC_UNION', 'DISTRICT_COMMERCIAL_HUB', 'YIELD_GOLD'),
        ('POLICY_ECONOMIC_UNION', 'DISTRICT_HARBOR', 'YIELD_GOLD'),
        ('POLICY_NAVAL_INFRASTRUCTURE', 'DISTRICT_HARBOR', 'YIELD_GOLD'),
        ('POLICY_SCRIPTURE', 'DISTRICT_HOLY_SITE', 'YIELD_FAITH'),
        ('POLICY_AESTHETICS', 'DISTRICT_THEATER', 'YIELD_CULTURE'),
        ('POLICY_SPORTS_MEDIA', 'DISTRICT_THEATER', 'YIELD_CULTURE'),
        ('POLICY_NATURAL_PHILOSOPHY', 'DISTRICT_CAMPUS', 'YIELD_SCIENCE'),
        ('POLICY_FIVE_YEAR_PLAN', 'DISTRICT_CAMPUS', 'YIELD_SCIENCE'),
        ('POLICY_FIVE_YEAR_PLAN', 'DISTRICT_INDUSTRIAL_ZONE', 'YIELD_PRODUCTION'),
        ('POLICY_CRAFTSMEN', 'DISTRICT_INDUSTRIAL_ZONE', 'YIELD_PRODUCTION'),
        ('POLICY_COLLECTIVISM', 'DISTRICT_INDUSTRIAL_ZONE', 'YIELD_PRODUCTION'),
    ]
    for policy, district, kind in native_cases:
        replacements = [r[0] for r in db.execute('SELECT CivUniqueDistrictType FROM DistrictReplaces WHERE ReplacesDistrictType=?', (district,))]
        for target in [district] + replacements:
            g.prepare(target, 'DISTRICT_CSC_BAKERS_QUARTER', 0)
            g.nativeYields[g.GameInfo.Yields[kind].Index] = 3
            assert g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)[0] == g.GetYieldString(kind, 3)
            g.setPolicy(policy, 1)  # A foreign player's policy must not affect this badge.
            assert g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)[0] == g.GetYieldString(kind, 3)
            g.setPolicy(policy, 0)
            assert g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)[0] == g.GetYieldString(kind, 6), (policy, target)
            lua.execute('activePolicies={}')
            assert g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)[0] == g.GetYieldString(kind, 3)
            cases += 1
    g.prepare('DISTRICT_INDUSTRIAL_ZONE', 'DISTRICT_CSC_BAKERS_QUARTER', 0)
    lua.execute("nativeYields[1]=3; nativeYields[2]=2; setPolicy('POLICY_FIVE_YEAR_PLAN'); setPolicy('POLICY_COLLECTIVISM')")
    assert g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)[0] == '[ICON_Production]+9[NEWLINE][ICON_Gold]+2'
    # Restore the mixed CSC fixture for the checks below.
    g.prepare('DISTRICT_COMMERCIAL_HUB', 'DISTRICT_CSC_BAKERS_QUARTER', 2)
    lua.execute("Map.GetAdjacentPlot(center.x,center.y,2).district=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index; setPolicy('POLICY_ECONOMIC_UNION')")
    # Pure custom yield with no native adjacency still gets its numeric label.
    lua.execute('nativeYields={}')
    icons, _, _ = g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)
    assert icons == '[ICON_Food]+4[NEWLINE][ICON_Culture]+2', icons
    # Native-only districts and their Housing/required-text behavior pass through.
    g.prepare('DISTRICT_CAMPUS', 'DISTRICT_CSC_BAKERS_QUARTER', 0)
    lua.execute('nativeYields[3]=6')
    assert g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)[0] == '[ICON_Science]+6'
    g.prepare('DISTRICT_NEIGHBORHOOD', 'DISTRICT_CSC_BAKERS_QUARTER', 0)
    assert '[ICON_Housing]+' in g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)[0]
    # City Lights has both repeatable towns and one-per-city boroughs with Housing.
    for district_type, housing in (('DISTRICT_RURALCOMMUNITYA', 1), ('DISTRICT_COREEXPANSIONA', 3)):
        if g.GameInfo.Districts[district_type] is None:
            continue
        is_rural = district_type == 'DISTRICT_RURALCOMMUNITYA'
        if is_rural:
            g.GameInfo.Districts[district_type].OnePerCity = False
        g.prepare(district_type, 'DISTRICT_CSC_BAKERS_QUARTER', 1)
        g.center.appeal = 2
        if is_rural:
            g.center.GetAdjacencyBonusTooltip = lambda *_: ('', None)
        icons, tooltip, _ = g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)
        assert icons == f'[ICON_Housing]+{housing}[NEWLINE][ICON_Food]+1', (district_type, icons)
        assert '[ICON_Food]' in tooltip, (district_type, tooltip)
        if is_rural:
            assert tooltip.startswith('LOC_TYPE_TRAIT_HOUSING 1[NEWLINE]'), tooltip
        else:
            g.nativeYields[1] = 3
            icons, tooltip, _ = g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)
            assert icons == '[ICON_Housing]+3[NEWLINE][ICON_Food]+1[NEWLINE][ICON_Production]+3', icons
            housing_line, native_line, csc_line = tooltip.split('[NEWLINE]')
            assert housing_line.startswith('LOC_DISTRICT_ZONE_NEIGHBORHOOD_TOOLTIP 3 '), housing_line
            assert native_line == 'Native 1', native_line
            assert '[ICON_Food]' in csc_line, csc_line
        g.prepare(district_type, 'DISTRICT_CSC_BAKERS_QUARTER', 0)
        g.center.appeal = 2
        if is_rural:
            g.center.GetAdjacencyBonusTooltip = lambda *_: ('', None)
        else:
            g.nativeYields[1] = 3
        icons, tooltip, _ = g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)
        assert icons == f'[ICON_Housing]+{housing}', icons
        assert 'Native 1' not in tooltip, tooltip
        if is_rural:
            assert tooltip == 'LOC_TYPE_TRAIT_HOUSING 1', tooltip
    # Signed custom additions are summed before formatting, including zero.
    g.prepare('DISTRICT_COMMERCIAL_HUB', 'DISTRICT_CSC_BAKERS_QUARTER', 0)
    lua.execute("CSC_Adjacency.ByDistrict.DISTRICT_COMMERCIAL_HUB={{ID='NEGATIVE',DistrictType='DISTRICT_COMMERCIAL_HUB',ProvideType='SelfBonus',YieldType='YIELD_GOLD',YieldChange=-2,AdjacencyType='FROM_UNCONDITIONAL_BONUS',CustomAdjacentObject='NONE'}}; nativeYields[2]=3")
    assert g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)[0] == '[ICON_Gold]+1'
    lua.execute('nativeYields[2]=2')
    assert g.GetAdjacentYieldBonusString(g.center.district, g.city, g.center)[0] == ''
    for file in CODE.glob('*.lua'):
        lua.compile(untype(file.read_text(encoding='utf-8-sig')))
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--dependencies', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.dependencies))
    db, rules = database(args.database)
    cases = lua_checks(db, rules)
    print(f'PASS: 9 policy mappings, {len(rules)} base/unique rules, {len(rules)*10} policy modifiers; {cases} gameplay/UI cases plus mixed returns, ownership, events, native totals and Housing')


if __name__ == '__main__':
    main()
