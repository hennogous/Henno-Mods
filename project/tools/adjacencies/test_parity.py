"""Compare CSC SQL/Lua to the frozen MAB database and pinned local fork.

Requires lupa (isolated test dependency); never edits the fork or a runtime DB.
"""
import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CODE = ROOT / 'Civ Supply Chains/Lua_UI/Adjacencies'
TESTS = ROOT / 'project/tests/adjacencies'
PIN = 'd852b8466cf7152f4fd76cacec5fa8c2084d7c0a'


def untype(text):
    return re.sub(r'\s*:\s*(?:number|table|string|boolean|function)\b', '', text)


def lua_value(value):
    if value is None: return 'nil'
    if isinstance(value, bool): return 'true' if value else 'false'
    if isinstance(value, (int,float)): return str(value)
    if isinstance(value, str): return json.dumps(value,ensure_ascii=False)
    if isinstance(value,list): return '{'+','.join(lua_value(x) for x in value)+'}'
    return '{'+','.join('['+lua_value(k)+']='+lua_value(v) for k,v in value.items())+'}'


def reference_functions(text):
    # MAB's public statistical functions are each indented four spaces. Extract
    # their bodies from the read-only reference at test time, never vendor them.
    result={}
    for match in re.finditer(r'^    function (\w+)\(',text,re.M):
        end=re.search(r'^    end\s*$',text[match.end():],re.M)
        if end:
            result[match.group(1)]=untype(text[match.start():match.end()+end.end()])
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--dependencies',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.dependencies: sys.path.insert(0,str(args.dependencies))
    from lupa import LuaRuntime
    args.output.mkdir(parents=True,exist_ok=True)
    head=subprocess.check_output(['git','-C',str(args.reference),'rev-parse','HEAD'],text=True).strip()
    assert head==PIN, f'Reference head {head} differs from pinned {PIN}'
    fixture=json.loads((TESTS/'mab-rules.json').read_text(encoding='utf-8'))
    assert hashlib.sha256(args.database.read_bytes()).hexdigest()==fixture['databaseSha256']
    origin=sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro',uri=True)
    origin.row_factory=sqlite3.Row
    db=sqlite3.connect(':memory:')
    origin.backup(db)
    db.row_factory=sqlite3.Row
    # Civ registers this SQL function for Types triggers. Hash values do not
    # participate in these assertions; this deterministic stand-in is test-only.
    db.create_function('Make_Hash',1,lambda value:zlib.crc32(value.encode()))
    db.execute('PRAGMA foreign_keys=ON')
    for name in ['Schema','Sources','Processor','Modifiers']:
        db.executescript((CODE/f'CSC_Adjacency{name}.sql').read_text(encoding='utf-8-sig'))
    actual=[dict(r) for r in db.execute('SELECT * FROM CSC_AdjacencyRules ORDER BY ID')]
    assert actual==fixture['rules'], 'Generated rules differ from frozen runtime inventory'
    violations=db.execute('PRAGMA foreign_key_check').fetchall()
    new_violations=[tuple(r) for r in violations if str(r[0]).startswith('CSC_')]
    assert not new_violations,new_violations
    for provider in db.execute('SELECT * FROM CSC_AdjacencyProviders'):
        assert db.execute('SELECT 1 FROM Types WHERE Type=?',(provider['EffectType'],)).fetchone(),provider['ProvideType']
        assert db.execute('SELECT 1 FROM DynamicModifiers WHERE ModifierType=?',('MODIFIER_CSC_ADJ_'+provider['ProvideType'],)).fetchone(),provider['ProvideType']
    compiler_reference=(args.reference/'NEW_ADJACENCY_BONUS_BY_RUIVO_CORE_INSERT.sql').read_text(encoding='utf-8-sig')
    reference_providers=dict((kind,modifier) for modifier,kind in re.findall(
        r"'((?:RUIVO_)?MODIFIER_[^']+)'[^\n]*ListA\.ProvideType = '([^']+)'",compiler_reference))
    for provider in db.execute('SELECT * FROM CSC_AdjacencyProviders'):
        old=origin.execute('SELECT CollectionType,EffectType FROM DynamicModifiers WHERE ModifierType=?',
                           (reference_providers[provider['ProvideType']],)).fetchone()
        assert tuple(old)==(provider['CollectionType'],provider['EffectType']),provider['ProvideType']
    # SQL attachment, requirement and signed amount equivalence for all 610 bits.
    for rule in actual:
        for bit in [1,2,4,8,16,32,64,128,256,512]:
            modifier='MOD_CSC_ADJ_'+rule['ID']+'_'+str(bit)
            amount=db.execute('SELECT Value FROM ModifierArguments WHERE ModifierId=? AND Name=\'Amount\'',(modifier,)).fetchone()[0]
            assert float(amount)==(bit if rule['YieldChange']>=0 else -bit)
            effect=db.execute('SELECT D.CollectionType,D.EffectType FROM Modifiers M JOIN DynamicModifiers D USING(ModifierType) WHERE M.ModifierId=?',(modifier,)).fetchone()
            old_effect=origin.execute('SELECT D.CollectionType,D.EffectType FROM Modifiers M JOIN DynamicModifiers D USING(ModifierType) WHERE M.ModifierId=?',(rule['ID']+'_'+str(bit),)).fetchone()
            assert tuple(effect)==tuple(old_effect),(modifier,tuple(effect),tuple(old_effect))
            table='BuildingModifiers' if rule['ModifierOwner']=='BuildingModifiers' else 'DistrictModifiers'
            key='BuildingType' if table=='BuildingModifiers' else 'DistrictType'
            owner=rule['WhoIsTheOwner'] if table=='BuildingModifiers' else rule['DistrictType']
            attached=('ATTACH_' if table=='BuildingModifiers' else '')+modifier
            assert db.execute(f'SELECT 1 FROM {table} WHERE {key}=? AND ModifierId=?',(owner,attached)).fetchone()
    # Dormant fixture proves unique clones retain every option, including flags.
    base,unique=db.execute('SELECT ReplacesDistrictType,CivUniqueDistrictType FROM DistrictReplaces LIMIT 1').fetchone()
    db.execute('INSERT INTO CSC_AdjacencyRules (ID,DistrictType,ApplyForUniqueDistricts,DistrictModifiers,NewMethod,ProvideType,YieldChange,MinRings,MaxRings,MustOwn,AdjacencyType,CustomAdjacentObject) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
               ('FIXTURE_CLONE',base,1,1,1,'SelfLoyalty',-0.5,2,4,1,'FROM_RINGS_CAO_DISTRICT',base))
    for provider in db.execute('SELECT * FROM CSC_AdjacencyProviders').fetchall():
        db.execute('INSERT INTO CSC_AdjacencyRules (ID,DistrictType,ProvideType,YieldChange,AdjacencyType) VALUES (?,?,?,?,?)',
                   ('FIXTURE_NEGATIVE_'+provider['ProvideType'],base,provider['ProvideType'],-0.5,'FROM_UNCONDITIONAL_BONUS'))
    db.executescript((CODE/'CSC_AdjacencyModifiers.sql').read_text(encoding='utf-8'))
    clone=dict(db.execute('SELECT * FROM CSC_AdjacencyRules WHERE ID=?',(unique+'_FIXTURE_CLONE',)).fetchone())
    original=dict(db.execute("SELECT * FROM CSC_AdjacencyRules WHERE ID='FIXTURE_CLONE'").fetchone())
    for field in original:
        if field not in ['ID','DistrictType','ApplyForUniqueDistricts','TraitType']: assert clone[field]==original[field],field
    assert db.execute("SELECT Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_ADJ_FIXTURE_CLONE_512' AND Name='Amount'").fetchone()[0]=='-512'
    for provider in db.execute('SELECT * FROM CSC_AdjacencyProviders'):
        for bit in [1,2,4,8,16,32,64,128,256,512]:
            modifier='MOD_CSC_ADJ_FIXTURE_NEGATIVE_'+provider['ProvideType']+'_'+str(bit)
            assert db.execute("SELECT Value FROM ModifierArguments WHERE ModifierId=? AND Name='Amount'",(modifier,)).fetchone()[0]==str(-bit)
            if provider['ArgumentName']:
                value='FREE_POWER_SOURCE_MISC' if provider['ArgumentName']=='SourceType' else 'YIELD_PRODUCTION'
                assert db.execute('SELECT Value FROM ModifierArguments WHERE ModifierId=? AND Name=?',
                                  (modifier,provider['ArgumentName'])).fetchone()[0]==value

    lua=LuaRuntime(unpack_returned_tuples=True)
    lua.execute((TESTS/'world.lua').read_text(encoding='utf-8'))
    def include(name):
        file=CODE/(name.removesuffix('.lua')+'.lua')
        lua.execute(untype(file.read_text(encoding='utf-8-sig')))
    lua.globals().include=include
    lua.execute((CODE/'CSC_AdjacencyCore.lua').read_text(encoding='utf-8'))
    g=lua.globals()
    sources=[dict(r) for r in db.execute('SELECT * FROM CSC_AdjacencySources')]
    providers=[dict(r) for r in db.execute('SELECT * FROM CSC_AdjacencyProviders')]
    lua.execute('GameInfo.CSC_AdjacencySources=info('+lua_value(sources)+'); GameInfo.CSC_AdjacencyProviders=info('+lua_value(providers)+'); CSC_Adjacency.Initialize()')
    source_names=sorted(list(g.CSC_Adjacency.Sources.keys()))
    assert set(source_names)=={r['AdjacencyType'] for r in sources},'Source metadata differs from evaluator registry'
    stat=(args.reference/'RUIVO_STAT_MODULE_GP.lua').read_text(encoding='utf-8-sig')
    functions=reference_functions(stat)
    needed={n for n in functions if n.startswith('FROM_RINGS_') or n.startswith('FROM_UI_RINGS_') or n.startswith('FROM_SELF_') or n.startswith('FROM_UI_SELF_')}
    needed.update(['RuivoGetRingPlotIndexes','truncate','IsPlayerCanSeeResource','FROM_RIVER_CROSSING'])
    # Visibility metadata is immutable; player knowledge is queried dynamically.
    lua.execute('m_ResourceVisibility={RESOURCE_HIDDEN={Type="Tech",Index=0},RESOURCE_CIVIC={Type="Civic",Index=0}}')
    for name in sorted(needed):
        if name in functions: lua.execute(functions[name])
    lua.execute('ResourceTypeMap={[0]="RESOURCE_VISIBLE",[1]="RESOURCE_HIDDEN",[2]="RESOURCE_CIVIC"}; DistrictTypeMap={[0]="DISTRICT_TEST",[1]="DISTRICT_WONDER"}; FeatureTypeMap={[0]="FEATURE_TEST"}; TerrainTypeMap={[0]="TERRAIN_TEST"}; ImprovementTypeMap={[0]="IMPROVEMENT_TEST"}; TypeTagsMap=CSC_Adjacency.Tags')
    cases=[]
    key_by_source={'CAO_ROUTE':'ROUTE_TEST','CAO_UNIT':'UNIT_TEST','CAO_RESOURCE_CLASS':'RESOURCECLASS_BONUS',
                   'TYPETAG_RESOURCE':'CLASS_TEST','TYPETAG_DISTRICT':'CLASS_DISTRICT_TEST','CAO_RESOURCE':'RESOURCE_VISIBLE',
                   'CAO_IMPROVEMENT':'IMPROVEMENT_TEST','CAO_DISTRICT':'DISTRICT_TEST','CAO_FEATURE':'FEATURE_TEST',
                   'CAO_TERRAIN_SETS':'IsHills','CAO_TERRAIN':'TERRAIN_TEST','DISTRICTS_CAO_YIELD':'YIELD_PRODUCTION',
                   'CAO_YIELD':'YIELD_PRODUCTION','PLOT_PROPERTY':'TEST','PLOT_PROPERTY_HASHED':'TEST',
                   'DISTRICT_PROPERTY':'TEST','DISTRICT_PROPERTY_HASHED':'TEST'}
    property_sources={'FROM_RINGS_PLOT_PROPERTY','FROM_RINGS_PLOT_PROPERTY_HASHED','FROM_RINGS_DISTRICT_PROPERTY','FROM_RINGS_DISTRICT_PROPERTY_HASHED'}
    def rule_for(name,first,last,own,key=None):
        suffix=name.replace('FROM_UI_RINGS_','').replace('FROM_RINGS_','')
        return {'ID':'FIXTURE','AdjacencyType':name,'CustomAdjacentObject':key or key_by_source.get(suffix,'NONE'),
                'MinRings':first,'MaxRings':last,'Rings':last,'MustOwn':own,'YieldChange':1,'YieldType':'YIELD_PRODUCTION',
                'ProvideType':'SelfBonus','ModifierOwner':'DistrictModifiers','DistrictModifiers':1,'Only':'Human&AI'}
    for width,height,wrapped in [(7,7,False),(3,3,True),(2,2,True)]:
        g.resetWorld(width,height,wrapped)
        for name in source_names:
            if not ('RINGS' in name and name in functions): continue
            for first,last in [(0,0),(1,0),(0,1),(1,1),(2,2),(1,3)]:
                for own in [0,1]:
                    rule=rule_for(name,first,last,own)
                    new=g.CSC_Adjacency.Count(lua.table_from(rule),g.center,g.city,0)
                    if name in property_sources:
                        # Fork has a four-argument call to a five-argument property
                        # function. Verify the corrected behavior independently.
                        indexes=g.RuivoGetRingPlotIndexes(g.center.x,g.center.y,first,last) if last else lua.table_from([g.center.index])
                        expected=0
                        for index in indexes.values():
                            plot=g.Map.GetPlotByIndex(index)
                            if name.startswith('FROM_RINGS_PLOT') and own and plot.owner!=0: continue
                            if 'DISTRICT' in name and plot.district<0: continue
                            expected+=plot.properties['HASH_TEST' if 'HASHED' in name else 'TEST']
                    else:
                        expected=g[name](g.center.x,g.center.y,first,last,rule['CustomAdjacentObject'],g.city,own)
                        expected=max(expected,0)
                    assert new==expected,(name,first,last,own,wrapped,new,expected)
                    cases.append({'source':name,'min':first,'max':last,'mustOwn':own,'wrap':wrapped,'width':width,'count':new})
    # Actual Quarter rules compared on a topology populated with real DB types.
    g.resetWorld()
    for table,field in [('Resources','ResourceType'),('Districts','DistrictType'),('Buildings','BuildingType'),
                        ('Tags','Tag'),('Yields','YieldType'),('Technologies','TechnologyType'),('Civics','CivicType')]:
        records=[dict(r) for r in origin.execute('SELECT * FROM '+table)]
        for index,record in enumerate(records): record['Index']=index
        lua.execute('GameInfo.'+table+'=info('+lua_value(records)+')')
    tags=[dict(r) for r in origin.execute('SELECT * FROM TypeTags')]
    objects=[dict(r) for r in db.execute('SELECT * FROM CSC_AdjacencyObjects')]
    lua.execute('GameInfo.TypeTags=info('+lua_value(tags)+'); GameInfo.CSC_AdjacencyObjects=info('+lua_value(objects)+'); GameInfo.CSC_AdjacencyRules=info('+lua_value(actual)+'); CSC_Adjacency.Initialize(); TypeTagsMap=CSC_Adjacency.Tags; ResourceTypeMap={}; DistrictTypeMap={}; for r in GameInfo.Resources() do ResourceTypeMap[r.Index]=r.ResourceType end; for r in GameInfo.Districts() do DistrictTypeMap[r.Index]=r.DistrictType end; m_ResourceVisibility={} ')
    lua.execute('for _,p in ipairs(world) do p.resource=GameInfo.Resources.RESOURCE_WHEAT.Index; p.district=GameInfo.Districts.DISTRICT_THEATER.Index; p.flags.IsHills=true; end')
    for rule in actual:
        expected=g[rule['AdjacencyType']](g.center.x,g.center.y,rule['MinRings'],rule['MaxRings'] or rule['Rings'],rule['CustomAdjacentObject'],g.city,rule['MustOwn'])
        count=g.CSC_Adjacency.Count(lua.table_from(rule),g.center,g.city,0)
        assert count==expected,(rule['ID'],count,expected)
        cases.append({'rule':rule['ID'],'count':count})
    # Restore synthetic tables for focused state transitions and UI tests.
    lua.execute((TESTS/'world.lua').read_text(encoding='utf-8'))
    lua.execute('GameInfo.CSC_AdjacencySources=info('+lua_value(sources)+'); GameInfo.CSC_AdjacencyProviders=info('+lua_value(providers)+'); CSC_Adjacency.Initialize()')
    # Signed fractional totals and bits are verified after decreasing to zero.
    for factor in [-2,-1,-0.5,0,0.5,1,2]:
        rule=rule_for('FROM_RIVER_CROSSING',1,1,0); rule['YieldChange']=factor
        rule=lua.table_from(rule)
        for count in [0,1,2,3,6,1024,0]:
            g.CSC_Adjacency.Write(g.center,rule,count)
            actual_amount=g.truncate(count*factor)
            encoded=max(-1023,min(1023,actual_amount))
            assert g.center.properties['CSC_ADJ_FIXTURE_ACTUAL_AMOUNT']==actual_amount
            decoded=sum(bit*g.center.properties['CSC_ADJ_FIXTURE_'+str(bit)] for bit in [1,2,4,8,16,32,64,128,256,512])
            assert decoded==abs(encoded)
    # Discovery must change counts without rebuilding caches.
    visibility=rule_for('FROM_RINGS_TYPETAG_RESOURCE',1,2,1)
    before=g.CSC_Adjacency.Count(lua.table_from(visibility),g.center,g.city,0)
    g.discoveredTech=True
    after=g.CSC_Adjacency.Count(lua.table_from(visibility),g.center,g.city,0)
    assert after>before
    # Building scope remains empire-wide, and eligibility clears on removal.
    building=rule_for('FROM_RIVER_CROSSING',1,1,0)
    building.update(ModifierOwner='BuildingModifiers',WhoIsTheOwner='BUILDING_MILL',CollectionType='COLLECTION_PLAYER_DISTRICTS')
    assert not g.CSC_Adjacency.Eligible(lua.table_from(building),g.city,0)
    g.otherCity.mill=True
    assert g.CSC_Adjacency.Eligible(lua.table_from(building),g.city,0)
    building['CollectionType']='COLLECTION_CITY_DISTRICTS'
    assert not g.CSC_Adjacency.Eligible(lua.table_from(building),g.city,0)
    g.otherCity.mill=False
    building['CollectionType']='COLLECTION_PLAYER_DISTRICTS'
    assert not g.CSC_Adjacency.Eligible(lua.table_from(building),g.city,0)
    # Specific-Wonder presence: wrong, unfinished, foreign and out-of-band.
    g.resetWorld()
    lua.execute('for _,p in ipairs(world) do p.wonder=-1; end; target=Map.GetAdjacentPlot(center.x,center.y,1); target.wonder=0; target.owner=0; target.complete=true')
    wonder=rule_for('FROM_RINGS_SPECIFIC_WONDER',1,1,0,'BUILDING_WONDER_TEST')
    assert g.CSC_Adjacency.Count(lua.table_from(wonder),g.center,g.city,0)==1
    for field,value in [('wonder',1),('complete',False),('owner',1)]:
        previous=g.target[field]; g.target[field]=value
        assert g.CSC_Adjacency.Count(lua.table_from(wonder),g.center,g.city,0)==0,field
        g.target[field]=previous
    wonder.update(MinRings=2,MaxRings=2)
    assert g.CSC_Adjacency.Count(lua.table_from(wonder),g.center,g.city,0)==0
    # Presentation: signed amount, loyalty icon, CAO priority, visibility, band.
    include('CSC_AdjacencyPresentation')
    loyalty=rule_for('FROM_RIVER_CROSSING',1,1,0); loyalty['ProvideType']='SelfLoyalty'
    assert g.CSC_Adjacency.ValueIcon(lua.table_from(loyalty),-1)=='[ICON_PressureDown]'
    assert g.CSC_Adjacency.ValueString(lua.table_from(loyalty),-1)=='[ICON_PressureDown]-1'
    for direction in range(6):
        neighbor=g.Map.GetAdjacentPlot(g.center.x,g.center.y,direction)
        for plot in g.world.values(): plot.riverE=False; plot.riverSE=False; plot.riverSW=False
        field={0:'riverSW',1:'riverE',2:'riverSE',3:'riverSW',4:'riverE',5:'riverSE'}[direction]
        owner=g.center if direction in [1,2,3] else neighbor
        owner[field]=True
        assert g.CSC_Adjacency.RiverEdge(g.center,neighbor,direction)
        assert sum(bool(g.CSC_Adjacency.RiverEdge(g.center,g.Map.GetAdjacentPlot(g.center.x,g.center.y,d),d)) for d in range(6))==1
    overlay=rule_for('FROM_RINGS_TYPETAG_RESOURCE',1,3,1)
    lua.execute('CSC_Adjacency.ByDistrict.DISTRICT_TEST={'+lua_value(overlay)+'}; CSC_Adjacency.Objects.CLASS_TEST={ArtdefOverlayEntry="CUSTOM_OVERLAY"}')
    g.target.resource=0; g.target.owner=0
    assert g.CSC_Adjacency.EdgeIcon('DISTRICT_TEST',g.center,g.target,g.city,1)=='CUSTOM_OVERLAY'
    g.target.owner=1
    assert g.CSC_Adjacency.EdgeIcon('DISTRICT_TEST',g.center,g.target,g.city,1)==''
    g.target.owner=0; g.target.resource=1; g.discoveredTech=False
    assert g.CSC_Adjacency.EdgeIcon('DISTRICT_TEST',g.center,g.target,g.city,1)==''
    g.discoveredTech=True
    assert g.CSC_Adjacency.EdgeIcon('DISTRICT_TEST',g.center,g.target,g.city,1)=='CUSTOM_OVERLAY'
    lua.execute('CSC_Adjacency.ByDistrict.DISTRICT_TEST[1].MinRings=2')
    assert g.CSC_Adjacency.EdgeIcon('DISTRICT_TEST',g.center,g.target,g.city,1)==''
    # Exercise the real gameplay entry point with the native city-manager shape.
    # City districts use indexed access; only PLAYER districts expose Members.
    gameplay_rule=rule_for('FROM_UNCONDITIONAL_BONUS',0,0,0)
    gameplay_rule['DistrictType']='DISTRICT_TEST'
    lua.execute('GameInfo.CSC_AdjacencyRules=info({'+lua_value(gameplay_rule)+'}); resetWorld(); center.district=0; center.complete=true')
    include('CSC_AdjacencyGameplay')
    assert g.center.properties['CSC_ADJ_FIXTURE_1']==1
    g.center.complete=False
    g.CSC_RefreshAdjacencies()
    assert g.center.properties['CSC_ADJ_FIXTURE_1']==0
    g.center.complete=True
    lua.execute('savedCount=CSC_Adjacency.Count; CSC_Adjacency.Count=function() error("injected fixture failure") end')
    ok,message=lua.eval('pcall(CSC_RefreshAdjacencies)')
    assert not ok and 'injected fixture failure' in message
    lua.execute('CSC_Adjacency.Count=savedCount')
    g.CSC_RefreshAdjacencies()
    assert g.center.properties['CSC_ADJ_FIXTURE_1']==1,'An error must not lock later refreshes'
    g.center.district=-1
    g.CSC_RefreshAdjacencies()
    assert g.center.properties['CSC_ADJ_FIXTURE_1']==0,'Removed districts must clear stale properties'
    lua.execute('resetWorld(); savedProperty=center.GetProperty; center.GetProperty=function() end')
    empty_property=rule_for('FROM_PLOT_PROPERTY',0,0,0,'ABSENT')
    assert g.CSC_Adjacency.Count(lua.table_from(empty_property),g.center,g.city,0)==0
    lua.execute('center.GetProperty=savedProperty; probeUnit=center.units[1]; savedExperience=probeUnit.GetExperience; probeUnit.GetExperience=function() return {} end; ExposedMembers={CSC_Adjacency={GetUnitLevel=function(owner,id) assert(owner==0 and id==1); return 4 end}}')
    unit_levels=rule_for('FROM_UI_RINGS_UNIT_LEVELS',0,0,0)
    assert g.CSC_Adjacency.Count(lua.table_from(unit_levels),g.center,g.city,0)==4
    lua.execute('probeUnit.GetExperience=savedExperience; ExposedMembers=nil')
    # Lua syntax check all shipped modules, including Firaxis dialect annotations.
    for file in CODE.glob('*.lua'):
        lua.compile(untype(file.read_text(encoding='utf-8-sig')))
    report={'referenceCommit':head,'rules':len(actual),'bitModifiers':len(actual)*10,
            'sourceRegistry':source_names,'differentialCases':len(cases),'cases':cases,
            'intentionalCorrections':['Ring-property argument forwarding','Clear stale bits','UI reports encoded cap'],
            'status':'offline parity passed; live gameplay and visual verification pending'}
    (args.output/'parity-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"PASS: {len(actual)} rules, {len(actual)*10} bit modifiers, {len(source_names)} sources, {len(cases)} comparisons")


if __name__=='__main__': main()
