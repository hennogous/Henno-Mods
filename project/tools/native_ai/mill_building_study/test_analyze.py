"""Synthetic native records exercise accounting contracts, not the game engine."""
import copy
import argparse
import importlib.util
from pathlib import Path
import tempfile
import sys
import unittest

spec = importlib.util.spec_from_file_location('mill_analyze', Path(__file__).with_name('analyze.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

BAKERS = 'DISTRICT_CSC_BAKERS_QUARTER'
TAILORS = 'DISTRICT_CSC_TAILORS_QUARTER'
NAMES = ['BUILDING_CSC_BAKERS_' + s for s in
         ('RIVER_ACCESS','NO_RIVER_ACCESS','WIND_MILL','WATER_MILL','BAKERY','CAFE',
          'STAGE_2_SERVICE','STAGE_3_SERVICE','STAGE_4_SERVICE_ENTER','STAGE_4_SERVICE_WATER')]
NAMES += ['BUILDING_CSC_TAILORS_' + s for s in ('TEXTILE_WORKSHOP','TAILOR','FASHION_HOUSE',
          'STAGE_2_SERVICE','STAGE_3_SERVICE','STAGE_4_SERVICE','STAGE_4_SERVICE_BOLSHOI',
          'STAGE_4_SERVICE_BROADWAY','STAGE_4_SERVICE_SYDNEY')]
OWNER = dict(pointer='0x10000', player=1, city=65536)
DEPENDENCIES = DATABASE = None


def context(acc=0, yi=-1):
    return dict(pointer='0x20000', candidateBuilding=2, cityId=65536,
                cityPointer='0x10000', districtPointer='0x30000', playerPointer='0x40000',
                plotPointer='0x50000', ready=2, horizon=10, discountFloat=0.9,
                yieldIndex=yi, accumulator=acc, nativeRecursionDepth=0, districtType=1)


def fixture():
    family = [dict(type=name, index=i) for i, name in enumerate(NAMES)]
    cfg = dict(profile=module.PROFILE, mappingVerified=True, targets=[dict(player=1, city=65536), dict(player=2, city=65536)],
               buildings=family, buildingCount=19, districtCount=3, districtIndices=[1,2], mapWidth=10, mapHeight=10, **module.LIMITS)
    ordinary = {2,3,4,5,10,11,12}
    definitions = [dict(Index=i, BuildingType=n, PrereqDistrict=BAKERS if i < 10 else TAILORS,
                   MustPurchase=i not in ordinary, RequiresPlacement=False, RegionalRange=6 if i==5 else 0,
                   Entertainment=1 if i==5 else 0) for i,n in enumerate(NAMES)]
    world = dict(profile=module.PROFILE, readOnly=True, observerConfig=cfg,
                 mapping=dict(family=family,quarters=[dict(type=BAKERS,index=1),dict(type=TAILORS,index=2)]),
                 yields=[dict(index=0,type='YIELD_PRODUCTION',defaultValue=1.5)], databaseStrings=[],
                 metadata=dict(buildings=definitions,buildingRoots=[],modifiers=[],modifierArguments=[],
                               prerequisites=[],mutualExclusions=[],adjacencyRules=[],unitSteps=[],specialists=[]),
                 targets=[dict(player=p,city=65536,exists=True,human=False,buildings=[dict(type=n,present=False) for n in NAMES],districts=[]) for p in (1,2)])
    trace = dict(profile=module.PROFILE, read_only=True, started=True, enabled=False, frozen=True,
                 pendingPairs=0,pendingFrames=0,stopReason=None,faults=[], config=copy.deepcopy(cfg),records=[])
    return trace, world


def record(kind,rid,start,end,parent=None,entry=None,leave=None,caller=None):
    base = dict(identity=copy.deepcopy(OWNER))
    if kind=='BuildingValue':
        base.update(building=2,buildingType=NAMES[2],discountQ8=230,ready=2,horizon=10,coordinates=dict(x=2,y=2))
    elif kind!='CalculateDistrictValues':
        base.update(buildingCallId=1,building=2)
    base.update(entry or {})
    return dict(kind=kind,id=rid,thread=7,entrySequence=start,parentId=parent,callerRva=caller,
                entry=base,leave=dict(sequence=end,**(leave or {})))


def analyzer_record(rid,start,end,parent,name,ptr='0x60000',acc=3,before=0,yi=-1):
    return record('AnalyzeModifier',rid,start,end,parent,
        dict(analysis=context(before,yi),rootCityMatch=True,rootCandidateMatch=True,
             modifier=dict(pointer=ptr,name=name,nameSize=len(name),nameCapacity=max(15,len(name)),
                           effectPointer='0x70000',collectionPointer='0x80000',effectAnalyzePointer='0x90000',
                           collectionNextPointer='0xa0000',subjectRequirementHash=0,dataPointer='0xb0000')),
        dict(accepted=1,analysis=context(acc,yi),accumulatorDelta=acc-before))


def finish(trace):
    trace['stats']=dict(callbacks=len(trace['records']),acceptedPairs=len(trace['records']),completedPairs=len(trace['records']),errors=0)
    trace['counts']={k:dict(entries=sum(r['kind']==k for r in trace['records']),accepted=sum(r['kind']==k for r in trace['records'])) for k in module.KINDS}
    return trace


def nested_fixture():
    trace,world=fixture()
    world['metadata']['buildingRoots']=[dict(building=NAMES[2],modifier='ROOT')]
    world['metadata']['modifiers']=[dict(ModifierId='ROOT',EffectType='EFFECT_ATTACH_MODIFIER',CollectionType='COLLECTION_CITY_DISTRICTS'),
                                   dict(ModifierId='CHILD',EffectType='EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE',CollectionType='COLLECTION_OWNER')]
    world['metadata']['modifierArguments']=[dict(ModifierId='ROOT',Name='ModifierId',Value='CHILD')]
    trace['records']=[record('BuildingValue',1,1,20,leave=dict(valueQ8=3000)),
        record('ModifierValue',2,2,18,1,dict(analysis=context(),modifierCount=1,descriptorBase='0x60000'),dict(valueQ8=3*256),caller='0x52c955'),
        analyzer_record(3,3,17,2,'ROOT',acc=3,before=99),
        analyzer_record(4,4,8,3,'CHILD',ptr='0x61000',acc=2),
        analyzer_record(5,9,13,3,'CHILD',ptr='0x61000',acc=3,before=2),
        record('AmenityValue',6,5,7,4,dict(recipient=copy.deepcopy(OWNER),recipientIsRootOwner=True,count=1,discountQ8=230,ready=2,horizon=10),dict(valueQ8=1000),caller='0x1234')]
    return finish(trace),world


def cache(values,districts):
    vec=[dict(index=i,type=n,value=values.get(n,0)) for i,n in enumerate(NAMES)]
    rows=[]
    for row,coords in enumerate(((2,2),(3,2))):
        rows.append(dict(row=row,x=coords[0],y=coords[1],plot=coords[1]*10+coords[0],rawAliasesMutable=False,
                    rawPointer='0xc0000',mutableRowPointer=hex(0xd0000+row*12),eligible=1,owned=1,adjacentOwned=1,
                    districtValues=[dict(district=d,value=9999) for d in (1,2)],
                    mutableDistrictValues=[dict(district=d,value=districts[row][d]) for d in (1,2)]))
    return dict(rows=2,status='observed',rawPointer='0xe0000',mutablePointer='0xf0000',rawAliasesMutable=False,
                rawBuildingQ8=copy.deepcopy(vec),mutableBuildingQ8=copy.deepcopy(vec),districtRows=rows,
                mutableDistrictPointer='0xd0000',mutableDistrictLength=6,mutableDistrictCapacity=6)


class AccountingTests(unittest.TestCase):
    def test_nested_attach_uses_final_accumulator_not_deltas_or_child_sum(self):
        trace,world=nested_fixture();result=module.analyze(trace,world)
        self.assertTrue(result['ok'],result['errors'])
        self.assertEqual(result['modifier_values'][0]['derived_q8'],768)
        building=result['building_components'][0]
        self.assertEqual(building['own_modifier_q8'],768)
        self.assertEqual(building['direct_amenity_consumed_q8'],0)
        self.assertEqual(building['unattributed_native_remainder_q8'],2232)

    def test_helper_callsite_separates_unit_or_unknown_subroute(self):
        trace,world=nested_fixture();trace['records'][1]['callerRva']='0x999'
        world['metadata']['buildingRoots']=[]
        result=module.analyze(trace,world)
        self.assertTrue(result['ok'],result['errors'])
        self.assertEqual(result['building_components'][0]['own_modifier_q8'],0)
        self.assertEqual(result['building_components'][0]['other_subroute_helper_ids'],[2])

    def test_wrong_exact_root_or_attach_child_fails(self):
        for which in ('root','child'):
            with self.subTest(which=which):
                trace,world=nested_fixture()
                if which=='root':world['metadata']['buildingRoots'][0]['modifier']='OTHER'
                else:trace['records'][3]['entry']['modifier'].update(name='WRONG',nameSize=5)
                self.assertFalse(module.analyze(trace,world)['ok'])

    def test_partial_pointer_thread_and_inventory_fail(self):
        for case in ('partial','thread','pointer','count','budget','crossing','parent'):
            with self.subTest(case=case):
                trace,world=nested_fixture()
                if case=='partial':trace['records'][3]['leave']['incompleteReason']='read fault'
                if case=='thread':trace['records'][3]['thread']=8
                if case=='pointer':trace['records'][3]['leave']['analysis']['pointer']='0x77777'
                if case=='count':trace['records'][1]['entry']['modifierCount']=2
                if case=='budget':trace['stopReason']='pair_budget'
                if case=='crossing':trace['records'][3]['leave']['sequence']=12
                if case=='parent':trace['records'][3]['parentId']=1
                result=module.analyze(trace,world)
                self.assertFalse(result['ok'])
                self.assertEqual(result['accounting'],'withheld_on_integrity_failure')

    def test_q8_yield_conversion_saturation_and_signed_wrap(self):
        self.assertEqual(module.restore_q8(3,0,{0:1.5}),1152)
        self.assertEqual(module.restore_q8(-3,0,{0:1.5}),-1152)
        self.assertEqual(module.restore_q8(2**30,-1,{}),0x7fffff00)
        self.assertEqual(module.i32(0x7fffffff+1),-2**31)

    def test_compact_dictionary_and_invalid_reference(self):
        trace,world=fixture()
        world['databaseStrings']=['long_building_type']
        world['metadata']={'sample':dict(columns=['id','unused'],rows=[[{'s':1},'ABSENT']],absent='ABSENT')}
        self.assertEqual(module.expand_metadata(world),{'sample':[{'id':'long_building_type'}]})
        world['metadata']['sample']['rows'][0][0]={'s':0}
        self.assertFalse(module.analyze(finish(trace),world)['ok'])
        world['metadata']['sample']['rows']=[[1]]
        self.assertRaises(ValueError,module.expand_metadata,world)

    def test_direct_regional_amenity_cap_and_foreign_recipient(self):
        trace,world=fixture()
        bv=record('BuildingValue',1,1,10,entry=dict(building=5,buildingType=NAMES[5]),leave=dict(valueQ8=20000))
        trace['records']=[bv]
        for rid,start in ((2,2),(3,5)):
            trace['records'].append(record('AmenityValue',rid,start,start+2,1,
                dict(building=5,recipient=dict(pointer='0x90000',player=2,city=42),recipientIsRootOwner=False,
                     count=1,discountQ8=230,ready=2,horizon=10),dict(valueQ8=9000),caller='0x52c4cb'))
        result=module.analyze(finish(trace),world)
        self.assertTrue(result['ok'],result['errors'])
        b=result['building_components'][0]
        self.assertEqual(b['direct_amenity_raw_q8'],18000)
        self.assertEqual(b['direct_amenity_consumed_q8'],12800)
        self.assertEqual(b['unattributed_native_remainder_q8'],7200)

    def test_actual_mutable_aggregation_canonical_water_hidden_and_two_districts(self):
        trace,world=fixture()
        world['metadata']['mutualExclusions']=[dict(Building=NAMES[2],MutuallyExclusiveBuilding=NAMES[3]),
                                               dict(Building=NAMES[3],MutuallyExclusiveBuilding=NAMES[2])]
        vals={NAMES[2]:100,NAMES[3]:200,NAMES[0]:500,NAMES[10]:300}
        before=cache(vals,[{1:50,2:70},{1:60,2:-1}]);after=cache(vals,[{1:100,2:300},{1:160,2:-1}])
        trace['records']=[record('CalculateDistrictValues',1,1,2,entry=dict(cache=before),leave=dict(identity=OWNER,cache=after))]
        result=module.analyze(finish(trace),world)
        self.assertTrue(result['ok'],result['errors'])
        d=result['district_aggregations'][0]['districts']
        self.assertEqual([x['source_derived_sum_q8'] for x in d],[100,300])
        self.assertTrue(all(x['status']=='exact_source_state_aggregation_match' for x in d))
        reasons={b['type']:b['reasons'] for b in d[0]['buildings']}
        self.assertIn('must_purchase',reasons[NAMES[0]])
        self.assertIn('lower_index_mutual_canonical:'+NAMES[2],reasons[NAMES[3]])
        self.assertEqual(d[0]['rows'][1]['raw_after_q8'],9999)

    def test_aggregation_mismatch_is_visible_not_no_uplift_claim(self):
        trace,world=fixture();values={NAMES[2]:100}
        before=cache(values,[{1:50,2:70},{1:60,2:-1}]);after=copy.deepcopy(before)
        trace['records']=[record('CalculateDistrictValues',1,1,2,entry=dict(cache=before),leave=dict(identity=OWNER,cache=after))]
        result=module.analyze(finish(trace),world)
        self.assertTrue(result['ok'])
        self.assertEqual(result['district_aggregations'][0]['districts'][0]['status'],'source_state_mismatch_or_unknown')
        self.assertTrue(result['warnings'])

    def test_exact_mill_topology_does_not_misclassify_workshop_bits(self):
        trace,world=fixture();db=world['metadata']
        for index,cap in ((2,1),(3,3)):
            rule='RULE_'+str(index)
            db['adjacencyRules'].append(dict(ID=rule,WhoIsTheOwner=NAMES[index]))
            db['unitSteps'].append(dict(ID=rule,MaxAmount=cap))
            for step in range(1,cap+1):
                child='MOD_CSC_ADJ_'+rule+'_STEP_'+str(step);root='ATTACH_'+child
                db['buildingRoots'].append(dict(building=NAMES[index],modifier=root))
                db['modifierArguments'] += [dict(ModifierId=root,Name='ModifierId',Value=child),dict(ModifierId=child,Name='Amount',Value=1)]
                db['modifiers'] += [dict(ModifierId=root,EffectType='EFFECT_ATTACH_MODIFIER',CollectionType='COLLECTION_CITY_DISTRICTS'),
                                   dict(ModifierId=child,EffectType='EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE',CollectionType='COLLECTION_OWNER')]
        db['buildingRoots'].append(dict(building=NAMES[10],modifier='DOCKMASTER_512'))
        result=module.analyze(finish(trace),world)
        self.assertTrue(result['ok'],result['errors'])
        self.assertEqual([m['source_unit_root_count'] for m in result['mill_inventory']],[1,3])
        self.assertEqual([m['source_legacy_weighted_root_count'] for m in result['mill_inventory']],[0,0])
        self.assertTrue(all(not m['observed_calls'] for i in result['mill_inventory'] for m in i['active_adjacency_roots']))

    def test_unobserved_hidden_definitions_and_artifacts(self):
        trace,world=fixture();result=module.analyze(finish(trace),world)
        self.assertTrue(result['ok'])
        self.assertEqual(sum(c['must_purchase'] for c in result['coverage']),12)
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            module.write_outputs(result,Path(directory))
            self.assertTrue((Path(directory)/'analysis.json').exists())
            self.assertTrue((Path(directory)/'modifier-calls.csv').exists())

    def test_dependent_vector_propagates_in_definition_order(self):
        trace,world=fixture()
        world['metadata']['prerequisites']=[dict(ordinal=1,building=NAMES[4],prerequisite=NAMES[2],index=2),
                                            dict(ordinal=2,building=NAMES[5],prerequisite=NAMES[4],index=4)]
        before=cache({NAMES[2]:100,NAMES[4]:200,NAMES[5]:300},[{1:0,2:0},{1:0,2:0}]);after=copy.deepcopy(before)
        after['mutableBuildingQ8'][2]['value']=300
        after['mutableBuildingQ8'][4]['value']=500
        trace['records']=[record('CalculateDistrictValues',1,1,2,entry=dict(cache=before),leave=dict(identity=OWNER,cache=after))]
        result=module.analyze(finish(trace),world)
        self.assertTrue(result['ok'],result['errors'])
        self.assertTrue(result['district_aggregations'][0]['dependent_vector']['selected_family_matches'])

    def test_zero_sentinel_and_analyzer_false_preserved(self):
        trace,world=nested_fixture()
        trace['records'][0]['leave']['valueQ8']=-2559744
        trace['records'][1]['leave']['valueQ8']=0
        trace['records'][2]['leave']['accepted']=0
        result=module.analyze(trace,world)
        self.assertTrue(result['ok'],result['errors'])
        self.assertTrue(result['building_components'][0]['is_native_invalid_sentinel'])
        self.assertIsNone(result['building_components'][0]['unattributed_native_remainder_q8'])
        self.assertEqual(result['modifier_calls'][0]['outcome'],'analyzer_returned_false')
        self.assertEqual(result['modifier_values'][0]['derived_q8'],0)

    def test_cache_corruption_and_identity_change_rejected(self):
        for case in ('family','rows','alias','identity','signed'):
            with self.subTest(case=case):
                trace,world=fixture();before=cache({},[{1:0,2:0},{1:0,2:0}]);after=copy.deepcopy(before)
                r=record('CalculateDistrictValues',1,1,2,entry=dict(cache=before),leave=dict(identity=copy.deepcopy(OWNER),cache=after))
                if case=='family':before['rawBuildingQ8'][0]['type']='OTHER'
                if case=='rows':before['rows']=38
                if case=='alias':before['districtRows'][0]['rawAliasesMutable']=True
                if case=='identity':r['leave']['identity']['city']=777
                if case=='signed':after['mutableBuildingQ8'][0]['value']=2**31
                trace['records']=[r];self.assertFalse(module.analyze(finish(trace),world)['ok'])

    def test_full_compact_world_source_topology(self):
        if DEPENDENCIES is None or DATABASE is None:
            self.skipTest('optional full world fixture needs --dependencies and --database')
        sys.path.insert(0,str(DEPENDENCIES))
        worldspec=importlib.util.spec_from_file_location('world_fixture',Path(__file__).with_name('test_world.py'))
        worldmodule=importlib.util.module_from_spec(worldspec);worldspec.loader.exec_module(worldmodule)
        worldmodule.DATABASE=DATABASE
        _,world,_,_=worldmodule.fixture(full_database=True,with_core=True,large_world=True)
        trace,_=fixture();trace['config']=copy.deepcopy(world['observerConfig'])
        result=module.analyze(finish(trace),world)
        self.assertTrue(result['ok'],result['errors'])
        self.assertEqual([x['source_unit_root_count'] for x in result['mill_inventory']],[1,3])
        self.assertEqual(sum(x['active_root_count'] for x in result['coverage']),88)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--dependencies',type=Path)
    parser.add_argument('--database',type=Path)
    options,remaining=parser.parse_known_args()
    DEPENDENCIES,DATABASE=options.dependencies,options.database
    unittest.main(argv=[sys.argv[0],*remaining])
