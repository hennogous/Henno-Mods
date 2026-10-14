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
    assert g.CSC_Adjacency.SourceName(river,2)=='River edges'
    lua.execute('GameInfo.Districts=info({{DistrictType="DISTRICT_NATIVE",Name="Native district"}})')
    assert g.CSC_Adjacency.SourceName(rule('FROM_RINGS_CAO_DISTRICT','DISTRICT_NATIVE'))=='[ICON_DISTRICT_NATIVE]Native district'
    assert g.CSC_Adjacency.SourceName(rule('FROM_RINGS_CAO_DISTRICT','MISSING'))=='matching object'
    # District descriptions already explain these rules. No automatic appendix.
    assert 'LOC_CSC_ADJ_HEADING' not in text
    assert not (CODE/'ToolTipLoader_CSCAdjacency.lua').exists()
    actions=json.loads((ROOT/'project/modbuddy/CivSupplyChains.actions.json').read_text(encoding='utf-8-sig'))
    for block in actions['blocks'].values():
        for action in block:
            assert not any('ToolTipLoader_CSCAdjacency' in name for name in action.get('files',[]))
    assert 'ToolTipLoader_CSCAdjacency' not in (ROOT/'Civ Supply Chains/Civ Supply Chains.civ6proj').read_text(encoding='utf-8-sig')
    print(f'PASS: {cases} MAB placement sentences; missing GameInfo tables; redundant district tooltip hook removed')



if __name__=='__main__': main()
