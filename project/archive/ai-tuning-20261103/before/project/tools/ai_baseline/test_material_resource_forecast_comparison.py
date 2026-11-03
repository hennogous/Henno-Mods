import copy,importlib.util,json,unittest
from unittest.mock import patch
from pathlib import Path
import material_resource_forecast_comparison as report
class EvidenceBoundaries(unittest.TestCase):
 def fixture(self):
  material=dict(plot=20,resource='RESOURCE_HONEY',owner=1,category='spec',improvement=None,pillaged=False)
  site=dict(player=1,plot=10,quarter='BAKERS',complete=True,pillaged=False,producer_built=True,materials=[material])
  point=dict(sites=[site]);care=dict(players={'1':dict(plots=[dict(plot=20,state='develop',ready_age=40,nearby_builders=2,nearby_charges=3)])});primary=dict(plots=[dict(index=20,owner=1,resource='RESOURCE_HONEY')]);return point,care,primary
 def test_multiple_Quarter_links_not_multiple_resource_plots(self):
  p,c,w=self.fixture();second=copy.deepcopy(p['sites'][0]);second['plot']=11;p['sites'].append(second)
  values=report.material_rows(p,c,[],w);self.assertEqual(len(values),1);self.assertEqual(len(values[0]['links']),2);self.assertEqual(values[0]['categories'],['spec'])
 def test_unobserved_care_is_not_a_lock_or_working(self):
  p,c,w=self.fixture();c['players']={};v=report.material_rows(p,c,[],w)[0];self.assertEqual(v['care_state'],'UNOBSERVED');self.assertFalse(v['working_care_observed']);self.assertIsNone(v['care'])
 def test_other_tree_plan_does_not_fabricate_city_job_or_no_all_plan(self):
  p,c,w=self.fixture();plan=dict(plot=20,player=1,turn=22,tree='Seek Tech Boost',improvement='IMPROVEMENT_CAMP');v=report.material_rows(p,c,[plan],w)[0]
  self.assertTrue(v['no_logged_reserved_city_improvement_plan']);self.assertEqual(v['all_logged_reserved_plans'],[plan]);self.assertFalse(v['no_logged_plan_is_no_hidden_job_claim'])
 def test_no_endpoint_plot_remains_unobserved(self):
  p,c,w=self.fixture();w['plots']=[];self.assertIsNone(report.material_rows(p,c,[],w)[0]['physical'])
 def test_incomplete_producer_or_pillaged_material_is_not_functioning(self):
  for mode in('unfinished','pillaged'):
   p,c,w=self.fixture();p['sites'][0]['materials'][0]['improvement']='IMPROVEMENT_CAMP'
   if mode=='unfinished':p['sites'][0]['complete']=False
   else:p['sites'][0]['materials'][0]['pillaged']=True
   with self.subTest(mode=mode):self.assertEqual(report.material_rows(p,c,[],w)[0]['functioning_producer_link_count'],0)
 def test_unknown_material_category_rejected(self):
  p,c,w=self.fixture();p['sites'][0]['materials'][0]['category']='specialty'
  with self.assertRaises(AssertionError):report.material_rows(p,c,[],w)
 def test_lost_material_still_preserves_physical_observation_and_prior_plan(self):
  primary=dict(plots=[dict(index=2533,owner=1,improvement='IMPROVEMENT_FARM')]);plan=dict(plot=2533,player=1,turn=20,tree='Build City Improvement',improvement='IMPROVEMENT_FARM')
  value=report.focus_evidence(2533,['RESOURCE_CATTLE'],primary,[],[plan]);self.assertTrue(value['physical_observed']);self.assertFalse(value['resource_presence_by_reference']['RESOURCE_CATTLE']);self.assertEqual(value['first_logged_city_improvement_plan']['improvements'],['IMPROVEMENT_FARM']);self.assertFalse(value['cause_of_absence_inferred'])
 def test_missing_endpoint_observation_not_assumed_harvested(self):
  value=report.focus_evidence(20,['RESOURCE_HONEY'],dict(plots=[]),[],[]);self.assertIsNone(value['resource_presence_by_reference']['RESOURCE_HONEY']);self.assertFalse(value['physical_observed'])
 def test_equal_physical_world_is_not_citizen_or_economic_inertness(self):
  plots=[dict(plot=1,owner=1,resource=None,workers=1,private=0,economic={'YIELD_FOOD':2,'YIELD_PRODUCTION':0}),dict(plot=2,owner=1,resource='SILK',workers=0,private=20,economic={'YIELD_FOOD':2,'YIELD_PRODUCTION':1})]
  before=dict(turn=75,cities=[dict(player=1,city=1,population=1,plots=plots)]);after=copy.deepcopy(before);after['cities'][0]['plots'][0]['workers']=0;after['cities'][0]['plots'][1].update(workers=1,private=100)
  world=dict(turn=75,width=2,height=2,players=[],plots=[],cities=[dict(player=1,id=1,name='City',x=0,y=0,population=1,buildings=[],districts=[],yields={'YIELD_FOOD':2,'YIELD_PRODUCTION':0})]);changed=copy.deepcopy(world);changed['cities'][0]['yields']['YIELD_PRODUCTION']=1
  boundary=dict(before=dict(turn=75,active=False,remaining=0),after=dict(turn=75,active=False,remaining=0))
  def read(path):
   path=Path(path);new='new'in path.parts
   if path.name=='final-native-private-snapshot.json':return after if new else before
   if path.name=='final-native-private-boundary.json':return boundary
   return changed if new else world
  with patch.object(report,'read',side_effect=read):value=report.endpoint_spillover(Path('old'),Path('new'))
  self.assertTrue(value['physical_world_signature_equal']);self.assertEqual(len(value['worker_allocation_changes']),1);self.assertTrue(value['worker_allocation_changes'][0]['worked_and_city_output_directions_correspond']);self.assertEqual(value['worker_allocation_changes'][0]['derived_city_economic_delta']['YIELD_PRODUCTION'],1)
 def test_actual_v5_locked_prerequisite_and_no_job_evidence_preserved(self):
  r=Path('C:/Users/Shadow/Desktop/Codex/csc-material-care-v2-20261023/raw-resource016-075-pasture-forecast-v5')
  if not r.exists():self.skipTest('Optional local native75 fixture is not available')
  read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));point=read(r/'metric-points/turn-075.json');care=read(r/'material-care/turn-075.json');primary=read(r/'game-01/turn-075.json');tree,_=report.reconstruct_checkpoint(r,'AI_Behavior_Trees.csv',75);plans=report.reservations(tree,75,primary['width']);rows=report.material_rows(point,care,plans,primary);cow=next(x for x in rows if(x['player'],x['plot'])==(2,1573));sugar=next(x for x in rows if(x['player'],x['plot'])==(2,1204))
  self.assertEqual(cow['care_state'],'develop');self.assertEqual(cow['care']['ready_age'],56);self.assertTrue(cow['no_logged_reserved_city_improvement_plan']);self.assertEqual(sugar['care_state'],'locked_or_illegal');self.assertFalse(sugar['working_care_observed'])
if __name__=='__main__':unittest.main()
