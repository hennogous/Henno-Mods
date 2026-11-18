"""Placement-text regression: localized yields, class names, counts and distance.

Uses generated CSC localization, a small formatter for the exercised Civ plural
syntax, and the reference's English templates read-only. This checks sentences;
native on-screen rendering remains a separate review.
"""
import argparse
import json
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from test_parity import CODE,ROOT,TESTS,lua_value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--dependencies',type=Path,required=True)
    args=parser.parse_args()
    sys.path.insert(0,str(args.dependencies))
    from lupa import LuaRuntime
    db=sqlite3.connect(':memory:'); db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE LocalizedText(Language TEXT,Tag TEXT,Text TEXT,PRIMARY KEY(Language,Tag))')
    for name in ['CSC_ALL_TEXT','CSC_ADJACENCY_TEXT','CSC_ADJACENCY_SOURCES_TEXT']:
        db.executescript((ROOT/'Civ Supply Chains/Text'/f'{name}.sql').read_text(encoding='utf-8-sig'))
    for name in ['Schema','Sources']:
        db.executescript((CODE/f'CSC_Adjacency{name}.sql').read_text(encoding='utf-8-sig'))
    text={row['Tag']:row['Text'] for row in db.execute('SELECT * FROM LocalizedText')}
    text.update(LOC_YIELD_PRODUCTION='Production',LOC_YIELD_GOLD='Gold')
    reference=ET.parse(args.reference/'Localization/MAB_en_US.xml')
    text.update({row.attrib['Tag']:row.findtext('Text') for row in reference.findall('.//Row')})
    def lookup(key,*values):
        values=tuple(text.get(value,value) if isinstance(value,str) else value for value in values)
        result=text.get(key,key)
        assert isinstance(result,str),'Missing localized name'
        plural=re.compile(r'\{(\d+)[^{}]*:\s*plural\s+1\?([^;]*);\s*other\?([^;]*);\}')
        while plural.search(result):
            result=plural.sub(lambda match:match.group(2) if values[int(match.group(1))-1]==1 else match.group(3),result)
        return re.sub(r'\{(\d+)[^{}]*\}',lambda match:str(values[int(match.group(1))-1]),result)
    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.execute((TESTS/'world.lua').read_text(encoding='utf-8'))
    def include(name): lua.execute((CODE/f'{name}.lua').read_text(encoding='utf-8-sig'))
    g=lua.globals(); g.include=include; g.Locale.Lookup=lookup
    for table in ['Sources','Providers','Objects']:
        rows=[dict(row) for row in db.execute('SELECT * FROM CSC_Adjacency'+table)]
        lua.execute('GameInfo.CSC_Adjacency'+table+'=info('+lua_value(rows)+')')
    lua.execute('GameInfo.Yields=info({{Index=0,YieldType="YIELD_PRODUCTION",Name="LOC_YIELD_PRODUCTION",IconString="[ICON_Production]"},{Index=1,YieldType="YIELD_GOLD",Name="LOC_YIELD_GOLD",IconString="[ICON_Gold]"}})')
    include('CSC_AdjacencyPresentation')
    g.CSC_Adjacency.Objects.CLASS_TEST=lua.table_from({'Name':'LOC_CLASS_CSC_BASE_NAME'})
    g.CSC_Adjacency.Objects.CLASS_SALES=lua.table_from({'Name':'LOC_CLASS_CSC_SALES_NAME'})
    def rule(source='FROM_RINGS_TYPETAG_RESOURCE',obj='CLASS_TEST',yield_type='YIELD_PRODUCTION',provider='SelfBonus',distance=1):
        return lua.table_from({'AdjacencyType':source,'CustomAdjacentObject':obj,'YieldType':yield_type,
            'ProvideType':provider,'YieldChange':1,'MinRings':distance,'MaxRings':distance,
            'ModifierOwner':'DistrictModifiers','Only':'Human&AI'})
    cases=0
    for count in [1,2,4]:
        for source,obj,yield_type in [('FROM_RINGS_TYPETAG_RESOURCE','CLASS_TEST','YIELD_PRODUCTION'),
                                      ('FROM_RINGS_TYPETAG_DISTRICT','CLASS_SALES','YIELD_GOLD')]:
            r=rule(source,obj,yield_type)
            actual=g.CSC_Adjacency.PreviewLine(r,count,count)
            expected=lookup('LOC_RUIVO_'+source,'+'+str(count),g.CSC_Adjacency.YieldText(r,count),count,
                            g.CSC_Adjacency.SourceName(r,count),'adjacent')
            assert actual==expected,(actual,expected)
            assert '(' not in actual and 'LOC_' not in actual
            cases+=1
    assert g.CSC_Adjacency.PreviewLine(rule(),1,1)=='+1 [ICON_Production]Production from the adjacent [ICON_CSC_BASE] Base Materials resource.'
    assert g.CSC_Adjacency.PreviewLine(rule('FROM_RIVER_CROSSING','NONE'),1,2)=='+1 [ICON_Production]Production from 2 adjacent River edges.'
    assert g.CSC_Adjacency.PreviewLine(rule('FROM_RINGS_CAO_TERRAIN_SETS','IsHills',distance=0),1,1)=='+1 [ICON_Production]Production from the local Hills terrain.'
    assert 'nearby' in g.CSC_Adjacency.PreviewLine(rule(distance=3),1,1)
    assert '-1 [ICON_Production]Production' in g.CSC_Adjacency.PreviewLine(rule(),-1,1)
    # Terrain bonuses lead the badge, followed by visible materials and goods.
    quarter='DISTRICT_CSC_BAKERS_QUARTER'
    sources=[
        ('FROM_RINGS_TYPETAG_DISTRICT','CLASS_CSC_BAKERS_GOODS_PROVIDER','Rural Community'),
        ('FROM_RINGS_TYPETAG_RESOURCE','CLASS_CSC_BAKERS_BASE','Base Materials'),
        ('FROM_RINGS_TYPETAG_RESOURCE','CLASS_CSC_BAKERS_SPEC','Specialty Materials'),
    ]
    for _,tag,label in sources:
        g.CSC_Adjacency.Objects[tag]=lua.table_from({'Name':label})
    g.CSC_Adjacency.ByDistrict[quarter]=lua.table_from(
        [rule(source,tag) for source,tag,_ in sources] + [
            rule('FROM_RIVER_CROSSING','NONE'),
            rule('FROM_RINGS_CAO_TERRAIN_SETS','IsHills',distance=0),
        ])
    original_count=g.CSC_Adjacency.Count
    for visible, expected in (({'BASE','SPEC'},[3,4,1,2,0]), ({'BASE'},[3,4,1,0]), (set(),[3,4,0])):
        g.CSC_Adjacency.Count=lambda r,*_: int(
            r.AdjacencyType!='FROM_RINGS_TYPETAG_RESOURCE' or r.CustomAdjacentObject.rsplit('_',1)[1] in visible)
        _,tooltip,_=g.CSC_Adjacency.Preview(quarter,g.center,g.city)
        labels=[label for _,_,label in sources]+['River','Hills']
        lines=tooltip.split('[NEWLINE]')
        assert len(lines)==len(expected) and all(labels[index] in line for line,index in zip(lines,expected)), tooltip
    g.CSC_Adjacency.Count=original_count
    # Unused fork capabilities retain their encoding/icons, without shipping
    # speculative effect names. Text is added alongside an actual CSC rule.
    assert g.CSC_Adjacency.AmountText(rule(provider='SelfMultiplier'),-10)=='-10%'
    assert g.CSC_Adjacency.ValueIcon(rule(provider='SelfLoyalty'),-1)=='[ICON_PressureDown]'
    assert not any(key.startswith('LOC_CSC_ADJ_YIELD_') for key in text)
    assert {key for key in text if key.startswith('LOC_CSC_ADJ_SOURCE_')}=={
        'LOC_CSC_ADJ_SOURCE_GENERIC','LOC_CSC_ADJ_SOURCE_FROM_RIVER_CROSSING'}
    assert {key for key in text if key.startswith('LOC_CSC_ADJ_TERRAIN_')}=={'LOC_CSC_ADJ_TERRAIN_IsHills'}
    for row in db.execute('SELECT Name FROM CSC_AdjacencySources'):
        assert row['Name'] in text, row['Name']
    # Native GameInfo returns nil for absent tables. The general world mock
    # creates empty tables automatically, which previously hid this crash.
    lua.execute('GameInfo.ResourceClasses=nil; setmetatable(GameInfo,nil)')
    river=rule('FROM_RIVER_CROSSING','NONE')
    assert g.CSC_Adjacency.SourceName(river,1)=='River edge'
    assert g.CSC_Adjacency.SourceName(river,2)=='River edges'
    lua.execute('GameInfo.Buildings=info({{BuildingType="BUILDING_CSC_BAKERS_WATER_MILL",Name="Water Mill"},'
                '{BuildingType="BUILDING_CSC_BAKERS_WIND_MILL",Name="Wind Mill"}})')
    hills=rule('FROM_RINGS_CAO_TERRAIN_SETS','IsHills',distance=0)
    for mill_rule, mill, amount, count, expected in (
        (river, 'WATER', 2, 4, '+2 [ICON_Production]Production from 4 adjacent River edges (Water Mill).'),
        (hills, 'WIND', 1, 1, '+1 [ICON_Production]Production from the local Hills terrain (Wind Mill).'),
    ):
        mill_rule.ID=f'TEST_{mill}_MILL'
        mill_rule.WhoIsTheOwner=f'BUILDING_CSC_BAKERS_{mill}_MILL'
        g.CSC_Adjacency.UnitSteps[mill_rule.ID]=amount
        assert g.CSC_Adjacency.PreviewLine(mill_rule,amount,count)==expected
        dim='[COLOR:Gray]'
        forecast=dim+expected.replace('[ICON_Production]','[ENDCOLOR][ICON_CSC_MILL_PRODUCTION]'+dim)+'[ENDCOLOR]'
        assert g.CSC_Adjacency.PreviewLine(mill_rule,amount,count,True)==forecast
    lua.execute("""GameInfo.Districts=info({{DistrictType="DISTRICT_CSC_BAKERS_QUARTER",Name="Bakers' Quarter"}})""")
    district_return=rule('FROM_RINGS_CAO_DISTRICT','DISTRICT_CSC_BAKERS_QUARTER','YIELD_GOLD')
    assert g.CSC_Adjacency.PreviewLine(district_return,1,1)=="+1 [ICON_Gold]Gold from the adjacent Bakers' Quarter district."
    assert g.CSC_Adjacency.SourceName(rule('FROM_RINGS_CAO_DISTRICT','MISSING'))=='matching object'
    # The native district list gets only base returns from adjacent Quarters.
    customer='DISTRICT_COMMERCIAL_HUB'
    unique='DISTRICT_TEST_UNIQUE_HUB'
    tailors='DISTRICT_CSC_TAILORS_QUARTER'
    rows=[
        dict(ID='B_TAILORS',DistrictType=customer,CustomAdjacentObject=tailors,YieldType='YIELD_PRODUCTION'),
        dict(ID='A_BAKERS',DistrictType=customer,CustomAdjacentObject=quarter,YieldType='YIELD_GOLD'),
        dict(ID='C_POLICY',DistrictType=customer,CustomAdjacentObject=quarter,YieldType='YIELD_GOLD',
             ModifierOwner='PolicyModifiers'),
        dict(ID='D_UNIQUE',DistrictType=unique,CustomAdjacentObject=quarter,YieldType='YIELD_GOLD'),
        dict(ID='E_NON_QUARTER',DistrictType=customer,CustomAdjacentObject='DISTRICT_HARBOR',YieldType='YIELD_GOLD'),
    ]
    defaults=dict(ModifierOwner='DistrictModifiers',ProvideType='SelfBonus',AdjacencyType='FROM_RINGS_CAO_DISTRICT',
                  MinRings=1,Rings=1,YieldChange=1)
    lua.execute('GameInfo.CSC_AdjacencyRules=info('+lua_value([defaults | row for row in rows])+')')
    lua.execute("""GameInfo.Districts=info({
        {Index=123,DistrictType="DISTRICT_COMMERCIAL_HUB"},
        {DistrictType="DISTRICT_TEST_UNIQUE_HUB"},
        {DistrictType="DISTRICT_CSC_BAKERS_QUARTER",Name="LOC_BAKERS_TEST"},
        {DistrictType="DISTRICT_CSC_TAILORS_QUARTER",Name="LOC_TAILORS_TEST"},
        {DistrictType="DISTRICT_HARBOR",Name="LOC_HARBOR_TEST"}
    })
    ToolTipHelper = { GetAdjacencyBonuses = function(t, field, key)
        if key == "DISTRICT_COMMERCIAL_HUB" then return {"native first", "native second"} end
        return {}
    end }
    """)
    calls=[]
    def stock_lookup(*args):
        calls.append(args)
        return lookup(args[0],*args[1:])
    g.Locale.Lookup=stock_lookup
    include('ToolTipLoader_CSCQuarterCustomers')
    get_bonuses=g.ToolTipHelper.GetAdjacencyBonuses
    tag='LOC_TYPE_TRAIT_ADJACENT_BONUS'
    assert list(get_bonuses(None,'DistrictType',customer).values())==['native first','native second',tag,tag]
    assert calls==[
        (tag,1,'[ICON_Gold]','LOC_YIELD_GOLD',1,'LOC_BAKERS_TEST'),
        (tag,1,'[ICON_Production]','LOC_YIELD_PRODUCTION',1,'LOC_TAILORS_TEST'),
    ]
    assert list(get_bonuses(None,'DistrictType',123).values())==[tag,tag]
    assert list(get_bonuses(None,'DistrictType',unique).values())==[tag]
    assert list(get_bonuses(None,'DistrictType','DISTRICT_HARBOR').values())==[]
    assert list(get_bonuses(None,'ImprovementType',customer).values())==['native first','native second']
    # Keep the retired general-purpose district appendix out of the package.
    assert 'LOC_CSC_ADJ_HEADING' not in text
    assert not (CODE/'ToolTipLoader_CSCAdjacency.lua').exists()
    actions=json.loads((ROOT/'project/modbuddy/CivSupplyChains.actions.json').read_text(encoding='utf-8-sig'))
    for block in actions['blocks'].values():
        for action in block:
            assert not any('ToolTipLoader_CSCAdjacency' in name for name in action.get('files',[]))
    assert 'ToolTipLoader_CSCAdjacency' not in (ROOT/'Civ Supply Chains/Civ Supply Chains.civ6proj').read_text(encoding='utf-8-sig')
    customer_loader='Lua_UI/Adjacencies/ToolTipLoader_CSCQuarterCustomers.lua'
    assert any(customer_loader in action.get('files',[]) for action in actions['blocks']['inGameActions'])
    print(f'PASS: {cases} MAB placement sentences, missing GameInfo tables, and native-style Quarter customer entries')



if __name__=='__main__': main()
