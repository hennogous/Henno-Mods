import importlib.util,json,unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime
H=Path(__file__).parent
P=Path(__file__).with_name('native_profile_test.py')
spec=importlib.util.spec_from_file_location('driver',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Census(unittest.TestCase):
 def fixture(self):
  lua=LuaRuntime();rows=[];lua.globals().print=lambda *x:rows.append('\t'.join(str(v)for v in x))
  lua.execute('''
   currentTurn=1;writes=0;
   Game={GetCurrentGameTurn=function()return currentTurn end,GetProperty=function()return nil end,SetProperty=function()writes=writes+1 end};
   plot={GetIndex=function()return 0 end,GetX=function()return 0 end,GetY=function()return 0 end,GetTerrainType=function()return 0 end,
    GetFeatureType=function()return -1 end,GetResourceType=function()return 0 end,GetResourceCount=function()return 1 end,
    GetContinentType=function()return 1 end,GetOwner=function()return -1 end,IsHills=function()return false end,
    IsWater=function()return false end,IsRiver=function()return true end,IsLake=function()return false end,
    IsImpassable=function()return false end,IsStartingPlot=function()return true end};
   Map={GetGridSize=function()return 1,1 end,GetPlotCount=function()return 1 end,GetPlotByIndex=function(i)assert(i==0);return plot end};
   GameInfo={Terrains={[0]={TerrainType='TERRAIN_PLAINS'}},Features={},Resources={[0]={ResourceType='RESOURCE_WHEAT'}},Units={[0]={UnitType='UNIT_SETTLER'}}};
   unit={GetID=function()return 101 end,GetType=function()return 0 end,GetX=function()return 0 end,GetY=function()return 0 end,GetDamage=function()return 0 end};
   p={GetID=function()return 1 end,GetStartingPlot=function()return plot end,
    GetTreasury=function()return {GetGoldBalance=function()return 100 end}end,
    GetUnits=function()return {Members=function()return ipairs({unit})end}end,
    GetCities=function()return {Members=function()return ipairs({})end}end};
   PlayerManager={GetAliveMajors=function()return {p}end};
   PlayerConfigurations={[1]={GetLeaderTypeName=function()return 'LEADER_TEST' end}};
   ExposedMembers={CSC_AI_AssistanceUI={IsAIPlayer=function()return true end}};
  ''');return lua,rows
 def test_complete_grid_and_setup_units_no_writes(self):
  lua,rows=self.fixture();lua.execute(m.RECEIPTS+'\n'+(H/'profile_initial_census.lua').read_text())
  v=json.loads(next(v.split('=',1)[1]for v in rows if v.startswith('CSC_PROFILE_INITIAL=')))
  self.assertEqual(len(v['plots']),1);self.assertEqual(v['units'][0]['type'],'UNIT_SETTLER');self.assertEqual(v['players'][0]['starting_plot'],0);self.assertEqual(lua.globals().writes,0)
 def test_missing_start_getter_is_unobserved(self):
  lua,rows=self.fixture();lua.execute('p.GetStartingPlot=nil');lua.execute(m.RECEIPTS+'\n'+(H/'profile_initial_census.lua').read_text())
  v=json.loads(next(v.split('=',1)[1]for v in rows if v.startswith('CSC_PROFILE_INITIAL=')))
  self.assertFalse(v['players'][0]['starting_plot_getter_observed']);self.assertNotIn('starting_plot',v['players'][0])
 def test_later_turn_cannot_be_relabelled_initial(self):
  lua,rows=self.fixture();lua.execute('currentTurn=2')
  with self.assertRaises(Exception):lua.execute(m.RECEIPTS+'\n'+(H/'profile_initial_census.lua').read_text())
  self.assertFalse(any(v.startswith('CSC_PROFILE_INITIAL=')for v in rows));self.assertEqual(lua.globals().writes,0)
unittest.main()
