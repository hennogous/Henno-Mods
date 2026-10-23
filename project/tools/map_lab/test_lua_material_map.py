"""Execute the real CSC Lua entry point and planner against native fixtures."""
import argparse
import copy
import json
from pathlib import Path
from offline import OfflineWorld, read
from continent_analysis import continent_census

ROOT=Path(__file__).resolve().parents[3]
SCRIPTS=ROOT/'Civ Supply Chains/Lua_UI/MapGeneration'


def world(source, fixture, args, enabled=1, setting=3, saved=False, turn=0, fail=False, standard=30):
    native=source['data'];w=OfflineWorld(native,args.database,args.game_root,args.workshop_root,1,setting,args.lua_dependencies)
    w.bootstrap();l=w.lua
    l.globals().TEST_STANDARD=standard
    eligibility=read(fixture/'native-eligibility.json')
    eligible={r:{i:True for i in indices} for r,indices in eligibility['eligible'].items()}
    l.globals().TEST_ELIGIBLE=l.table_from(eligible,recursive=True)
    l.globals().TEST_STARTS=l.table_from({i:True for i in native.get('starting_plots',[])})
    l.globals().TEST_IMPROVEMENTS=l.table_from({int(i):v for i,v in eligibility.get('improvements',{}).items()})
    l.globals().TEST_ENABLED=enabled;l.globals().TEST_SAVED=saved;l.globals().TEST_TURN=turn
    l.globals().TEST_SEED=source['settings']['map_seed'];l.globals().TEST_FAIL=fail
    l.execute('''GameConfiguration={GetValue=function(k)if k=='CSC_RESOURCE_MAP_ASSISTANCE' then return TEST_ENABLED elseif k=='CSC_MATERIAL_MAP_DIAGNOSTICS' then return true end end,IsSavedGame=function()return TEST_SAVED end,GetStartTurn=function()return 0 end};
Game.GetCurrentGameTurn=function()return TEST_TURN end;
local old=MapConfiguration.GetValue;MapConfiguration.GetValue=function(k)if k=='RANDOM_SEED' then return TEST_SEED end;return old(k)end;
GameInfo.Districts={};
GameInfo.GlobalParameters={CSC_MATERIAL_MAP_STANDARD_DENSITY={Value=TEST_STANDARD}};
local methods=getmetatable(OFFLINE_DATA.plots[1]).__index;
methods.GetDistrictType=function(self)return -1 end;methods.IsImpassable=function(self)return self.impassable end;
methods.GetOwner=function(self)return self.owner or -1 end;
methods.GetResourceCount=function(self)return self.resource and 1 or 0 end;
methods.GetImprovementType=function(self)return TEST_IMPROVEMENTS[self.index] and 1 or -1 end;
methods.IsStartingPlot=function(self)return TEST_STARTS[self.index] or false end;
ResourceBuilder.CanHaveResource=function(p,r)local name=GameInfo.Resources[r].ResourceType;return not p.resource and TEST_ELIGIBLE[name] and TEST_ELIGIBLE[name][p.index] or false end;
local set=ResourceBuilder.SetResourceType;TEST_WRITES=0;
ResourceBuilder.SetResourceType=function(p,r,n)if r~=-1 then TEST_WRITES=TEST_WRITES+1;if TEST_FAIL and TEST_WRITES==2 then error('injected placement failure')end end;return set(p,r,n)end;
TerrainBuilder.GetRandomNumber=function()error('CSC must not consume shared engine RNG')end;
''')
    def include(name):
        path=SCRIPTS/(name+'.lua');assert path.is_file(),name
        l.execute(path.read_text(encoding='utf-8'),name=str(path))
    l.globals().include=include
    l.execute((SCRIPTS/'CSC_MaterialMap.lua').read_text(encoding='utf-8'))
    return w


def get(w,expression):
    return json.loads(w.lua.eval('CSC_MaterialMapCore.Json('+expression+')'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('bundle','fixtures','database','game-root','workshop-root','lua-dependencies','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--automatic-fixtures',type=Path,help='Original automatic v1 captures, for exact Abundant regression replay')
    args=p.parse_args();bundle=read(args.bundle);results=[];two=None
    for source in (m for m in bundle['maps'] if m['group']=='luxuries-4'):
        fixture=args.fixtures/'csc-helper-native'/f"map-{source['number']:02d}"
        source=copy.deepcopy(source);source['data']=read(fixture/'before.json')
        w=world(source,fixture,args);plan=get(w,"Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT')")
        assert plan['status']=='complete'
        additions=plan['additions'] if isinstance(plan['additions'],list) else []
        prior=next((m for m in bundle['maps'] if m['id']==f"csc-helper-lua-{source['number']}"),None)
        if prior and args.automatic_fixtures and plan['version']<3:
            debug=read(args.automatic_fixtures/'csc-helper-lua'/f"map-{source['number']:02d}"/'automatic-debug.json')
            eligible={r:{i:True for i in values} for r,values in debug['eligible'].items()}
            replay=w.lua.globals().CSC_MaterialMapCore.Plan(w.lua.table_from(debug['before'],recursive=True),w.lua.table_from(debug['definitions'],recursive=True),w.lua.table_from(eligible,recursive=True),source['settings']['map_seed'])
            actual=json.loads(w.lua.globals().CSC_MaterialMapCore.Json(replay))
            assert actual['additions']==prior['assistance']['additions'],'Vanilla Abundant changed with identical native v1 inputs'
        after=copy.deepcopy(source['data'])
        for a in additions:after['plots'][a['plot']]['resource']=a['resource']
        assert len(additions)<=plan['max_per_map']
        assert {row['quarter'] for row in plan['coverage']}=={'BAKERS','TAILORS'}
        assert all(a['quarter']=='TAILORS' for a in additions)
        assert {a['quarter'] for a in plan['attempts']}=={'TAILORS'}
        before_c=continent_census(source['data'],source['definitions']);after_c=continent_census(after,source['definitions'])
        for q in plan['coverage']:
            old=next(c for c in before_c if c['id']==q['continent']);new=next(c for c in after_c if c['id']==q['continent'])
            a=next(r for r in old['quarters'] if r['quarter']==q['quarter']);b=next(r for r in new['quarters'] if r['quarter']==q['quarter'])
            assert (q['base_before'],q['both_before'],q['base_after'],q['both_after'])==(a['common_clearable_base'],a['common_clearable_both'],b['common_clearable_base'],b['common_clearable_both'])
            assert not q['base_before'] or q['base_after'];assert not q['both_before'] or q['both_after']
        first=get(w,'OFFLINE_DATA.plots');w.lua.execute('CSC_InitializeMaterialMap()');assert get(w,'OFFLINE_DATA.plots')==first
        # Re-execute the actual entry script as a save/load would; property guard
        # must prevent all new writes even when its Lua locals are recreated.
        writes=w.lua.globals().TEST_WRITES
        w.lua.execute((SCRIPTS/'CSC_MaterialMap.lua').read_text());assert w.lua.globals().TEST_WRITES==writes
        repeated=world(source,fixture,args);assert get(repeated,"Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT')")==plan
        results.append({'map':source['number'],'additions':len(additions),'coverage':plan['coverage']})
        if len(additions)>=2:two=(source,fixture)
    source=next(m for m in bundle['maps'] if m['group']=='luxuries-4');fixture=args.fixtures/'csc-helper-native'/f"map-{source['number']:02d}"
    for options,reason in (({'enabled':0},'disabled'),({'setting':99},'unsupported resource setting'),({'saved':True},'existing save'),({'turn':10},'past initialization')):
        w=world(source,fixture,args,**options);assert get(w,"Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT')")['reason']==reason;assert w.lua.globals().TEST_WRITES==0
    profiles=[]
    for standard,setting,density in ((30,1,27),(30,2,30),(30,3,33),(30,4,30),(29,1,26),(29,2,29),(29,3,32),(29,4,29),(29,25,54),(29,45,74)):
        w=world(source,fixture,args,setting=setting,standard=standard)
        plan=get(w,"Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT')")
        assert plan['status']=='complete'
        profile=plan['abundance'];assert profile['nominal_density']==density
        assert abs(profile['scale']-density/33)<1e-12
        assert abs(profile['targets']['TAILORS']-min(1,10/15*density/33))<1e-12
        assert set(profile['targets'])=={'BAKERS','TAILORS'}
        assert set(profile['probabilities'])=={'TAILORS'}
        additions=plan['additions'] if isinstance(plan['additions'],list) else []
        assert len(additions)<=plan['max_per_map']
        for cid in {a['continent'] for a in additions}:assert sum(a['continent']==cid for a in additions)<=plan['max_per_continent']
        after=get(w,'OFFLINE_DATA.plots')
        assert all(not p.get('resource') or after[i].get('resource')==p['resource'] for i,p in enumerate(source['data']['plots']))
        assert all(not row['base_before'] or row['base_after'] for row in plan['coverage'])
        assert all(not row['both_before'] or row['both_after'] for row in plan['coverage'])
        assert all(0<=v<=1 for v in profile['probabilities'].values())
        if density==33:assert abs(profile['probabilities']['TAILORS']-7/12)<1e-12
        profiles.append({'standard':standard,'setting':setting,'density':density,'profile':profile,'additions':len(additions)})
    assert two,'Need at least one multi-deposit fixture for rollback'
    w=world(*two,args,fail=True);assert get(w,"Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT')")['status']=='failed'
    actual=get(w,'OFFLINE_DATA.plots')
    assert [p.get('resource') for p in actual]==[p.get('resource') for p in two[0]['data']['plots']]
    # Neither Tailor class exists: force that industry's assistance draw to
    # exercise the planner's two-resource path, without changing shipped odds.
    pair_data=copy.deepcopy(two[0]['data']);tailors=two[0]['definitions']['TAILORS']
    tailor_resources=set(tailors['base']['resources']+tailors['spec']['resources'])
    for tile in pair_data['plots']:
        if tile.get('resource') in tailor_resources:tile.pop('resource')
    w.lua.globals().TEST_PAIR_DATA=w.lua.table_from(pair_data,recursive=True)
    w.lua.globals().TEST_PAIR_DEFINITIONS=w.lua.table_from(two[0]['definitions'],recursive=True)
    w.lua.execute("CSC_MaterialMapCore.Probability.TAILORS=1;TEST_PAIR_PLAN=CSC_MaterialMapCore.Plan(TEST_PAIR_DATA,TEST_PAIR_DEFINITIONS,TEST_ELIGIBLE,TEST_SEED)")
    pairs=get(w,'TEST_PAIR_PLAN');assert any(a['repair_size']==2 for a in pairs['additions'])
    assert any(row['quarter']=='TAILORS' and row['both_after']>0 for row in pairs['coverage'])
    # Loaded optional resource mappings augment designed classes; incomplete
    # vanilla stub mappings must not silently change the six design definitions.
    w.lua.execute("""GameInfo.Resources.RESOURCE_CSC_TEST_FIBRE={ResourceType='RESOURCE_CSC_TEST_FIBRE',Frequency=2,Index=9999};
local old=GameInfo.TypeTags;GameInfo.TypeTags=function()local nextOld=old();local n=0;return function()local r=nextOld();if r then return r end;n=n+1;if n==1 then return {Type='RESOURCE_CSC_TEST_FIBRE',Tag='CLASS_CSC_TAILORS_SPEC'} end end end;
TEST_RESOLVED=CSC_MaterialMapDefinitions.Resolve();""")
    resolved=get(w,'TEST_RESOLVED');assert set(resolved)=={'BAKERS','TAILORS'}
    assert 'RESOURCE_CSC_TEST_FIBRE' in resolved['TAILORS']['spec']['resources']
    result={'passed':True,'version':4,'maps':5,'runtime_scope':['BAKERS','TAILORS'],'entrypoint_guards':True,'repeatable':True,'coverage_matches_census':True,'shared_engine_rng_draws':0,'rollback_verified':True,'two_resource_path':True,'optional_mapping_and_runtime_scope':True,'abundance_profiles':profiles,'maps_result':results}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('maps_result','abundance_profiles')}))


if __name__=='__main__':main()
