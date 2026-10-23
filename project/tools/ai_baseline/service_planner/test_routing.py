"""Bounded city-range connector routes with real-first-step authority."""
import json,sys,unittest,re
from pathlib import Path
from .routing import acquisition_route
from .observations import build_candidates
from .policy import Policy,Planner,Budget
from .test_material import observation
from .test_policy import LUA_FIXTURE
from .execution import lua

def network():
 edges={0:[1],1:[0,2],2:[1,4,5],4:[2,5,6],5:[2,4],6:[4]}
 return {i:{'index':i,'neighbors':v,'owner':1 if i in(0,6)else -1,'revealed':True,
            'within_city_reach':True,'native_purchasable':i==1,'price':20,'frontier_danger':False}for i,v in edges.items()}

class RoutingTests(unittest.TestCase):
 def test_two_connectors_reach_both_required_terminals(self):
  tiles=network();route=acquisition_route(tiles,1,(4,5),(5,6),2)
  self.assertEqual(set(route),{1,2,4,5});self.assertEqual(route[0],1)
 def test_connector_limit_prevents_long_route(self):
  self.assertIsNone(acquisition_route(network(),1,(4,5),(5,6),1))
 def test_foreign_hidden_unsafe_or_outside_ring_blocks_connector(self):
  for field,value in [('owner',2),('revealed',False),('frontier_danger',True),('within_city_reach',False)]:
   tiles=network();tiles[2][field]=value
   self.assertIsNone(acquisition_route(tiles,1,(4,5),(5,6),2),(field,value))
 def test_no_invented_first_step_when_native_frontier_empty(self):
  tiles=network();tiles[1]['native_purchasable']=False
  self.assertIsNone(acquisition_route(tiles,1,(4,5),(5,6),2))
 def test_new_ownership_uses_new_native_frontier(self):
  tiles=network();tiles[1]['owner']=1;tiles[1]['native_purchasable']=False;tiles[2]['native_purchasable']=True
  route=acquisition_route(tiles,1,(4,5),(5,6),2);self.assertEqual(route[0],2);self.assertNotIn(1,route)
 def test_unreachable_mark_is_retained_for_natural_growth(self):
  o=observation()
  for p in o['tiles']:p['native_purchasable']=False
  c=build_candidates(o,material_first=True,stepwise=True,connector_limit=2)[0]
  self.assertEqual(c.base,1);self.assertEqual(c.specialty,1);self.assertIsNone(c.purchase_plot)
  self.assertEqual(Planner(Policy.material_first_v2(max_connectors=2)).evaluate(c,{},Budget(1000),60).action,'watch')
 def test_candidate_contains_connectors_and_actual_known_costs(self):
  tiles=network();tiles[4].update(potential_legal={'TAILORS':True},current_legal={'TAILORS':False},native_projection_verified=True)
  tiles[6].update(base_for=['TAILORS'],material_visible=True)
  tiles[5].update(spec_for=['TAILORS'],material_visible=True)
  o={'player':1,'city':10,'turn':60,'eligible_ai':True,'human':False,'tiles':list(tiles.values())}
  c=next(c for c in build_candidates(o,material_first=True,stepwise=True,connector_limit=2)if c.plot==4)
  self.assertEqual(c.plan_connectors,(1,2));self.assertEqual(c.purchase_plot,1);self.assertEqual(c.remaining_price,80)
  self.assertEqual(Planner(Policy.material_first_v2(max_connectors=2)).evaluate(c,{},Budget(200,5),60).action,'purchase')
  tiles[2]['price']=-1;o['tiles']=list(tiles.values())
  c=next(c for c in build_candidates(o,material_first=True,stepwise=True,connector_limit=2)if c.plot==4)
  self.assertEqual(c.remaining_price,0) # A ranking penalty never becomes a fabricated quote.
  self.assertEqual(Planner(Policy.material_first_v2(max_connectors=2)).evaluate(c,{},Budget(200,5),60).action,'purchase')
  # The next connector is not prepaid. After acquiring the frontier tile,
  # collect again and require a new native quote before advancing the route.
  tiles[1].update(owner=1,native_purchasable=False);tiles[2]['native_purchasable']=True
  o['tiles']=list(tiles.values())
  next_c=next(c for c in build_candidates(o,material_first=True,stepwise=True,connector_limit=2)if c.plot==4)
  self.assertEqual(next_c.purchase_plot,2)
  self.assertLessEqual(next_c.price,0) # No positive current quote for tile2.
  self.assertEqual(Planner(Policy.material_first_v2(max_connectors=2)).evaluate(next_c,{},Budget(180,5),60).action,'watch')
 def test_actual_lua_declared_connector_once_and_undeclared_rejected(self):
  from lupa.lua51 import LuaRuntime
  for declared,expected in [(True,1),(False,0)]:
   e=LuaRuntime(unpack_returned_tuples=True);e.execute(LUA_FIXTURE)
   e.execute("GameInfo.TypeTags[2]={Type='WOOL',Tag='CLASS_CSC_TAILORS_SPEC'};local s=Map.GetPlotByIndex(100);s.GetOwner=function()return -1 end;Map.GetAdjacentPlots=function()return {Map.GetPlotByIndex(81),Map.GetPlotByIndex(82)}end")
   r={'player':1,'city':10,'purchase_plot':42,'source_plot':100,'quarter':'TAILORS','turn':60,'base':2,'specialty':2,
      'material_first':True,'stepwise':True,'established':False,'service':None,'plan_materials':{'81':True,'82':True},
      'remaining_tiles':{'42':True,'100':True},'plan_connectors':{'42':True}if declared else{},
      'gold':600,'price':80,'max_price':100,'reserve':150,'plot_purchase_parameter':True}
   e.globals().CSC_SERVICE_PURCHASE_REQUEST=e.eval(lua(r))
   if declared:e.execute(Path(__file__).with_name('native_purchase.lua').read_text())
   else:
    with self.assertRaisesRegex(Exception,'neither source, material nor declared connector'):e.execute(Path(__file__).with_name('native_purchase.lua').read_text())
   self.assertEqual(e.globals().requests,expected)
 def test_actual_collector_records_native_reason_tables_and_terrain(self):
  from lupa.lua51 import LuaRuntime
  fixture=re.search(r"engine.execute\(r'''(.*?)'''\)",Path(__file__).with_name('test_material.py').read_text(),re.S)[1]
  e=LuaRuntime(unpack_returned_tuples=True);e.execute(fixture)
  e.execute("local old=Map.GetPlotByIndex;Map.GetPlotByIndex=function(i)local p=old(i);p.GetTerrainType=function()return 5 end;p.IsWater=function()return false end;return p end;city=nil")
  e.execute("for _,c in Players[1]:GetCities():Members()do local old=c.GetBuildQueue;c.GetBuildQueue=function(self)local q=old(self);q.CanProduce=function()return false,{'Native capacity unavailable'}end;return q end end")
  e.execute(Path(__file__).with_name('native_observer.lua').read_text());e.execute('CSC_SERVICE_NATIVE.Read()')
  out=json.loads(e.globals().captured.split('=',1)[1]);c=out['cities'][0]
  self.assertFalse(c['district_state']['TAILORS']['can_produce']);self.assertEqual(c['district_state']['TAILORS']['secondary_result'],['Native capacity unavailable'])
  self.assertEqual(c['tiles'][0]['terrain'],5);self.assertFalse(c['tiles'][0]['water'])
  e.execute("Map.GetPlotCount=function()error('Map-wide iteration forbidden after geography cached')end;CSC_SERVICE_NATIVE.city_watch={['1:10']={[0]=true,[1]=true}};CSC_SERVICE_NATIVE.Read()")
  c=json.loads(e.globals().captured.split('=',1)[1])['cities'][0];self.assertEqual(c['checked_plot_indices'],2);self.assertFalse(c['broad_scan'])
  e.execute('CSC_SERVICE_NATIVE.city_watch=nil;CSC_SERVICE_NATIVE.Read()')
  c=json.loads(e.globals().captured.split('=',1)[1])['cities'][0];self.assertTrue(c['geography_cache_hit']);self.assertTrue(c['broad_scan'])

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--lua51-path',required=True);p.add_argument('--output',type=Path);a=p.parse_args();sys.path.insert(0,a.lua51_path)
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RoutingTests))
 if a.output:a.output.write_text(json.dumps({'passed':r.wasSuccessful(),'tests':r.testsRun,'native_connections':0},indent=2))
 raise SystemExit(not r.wasSuccessful())
