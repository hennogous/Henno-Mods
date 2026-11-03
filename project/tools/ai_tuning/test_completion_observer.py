import unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime
H=Path(__file__).parent
class Completion(unittest.TestCase):
 def setup_lua(self,prefix=False):
  lua=LuaRuntime();lua.execute('''
   turn=10;tailorComplete=false;writes=0;
   Game={GetCurrentGameTurn=function()return turn end,SetProperty=function()writes=writes+1 end};
   GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=0,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'},DISTRICT_CSC_TAILORS_QUARTER={Index=1,DistrictType='DISTRICT_CSC_TAILORS_QUARTER'}}};
   baker={GetType=function()return 0 end,IsComplete=function()return true end,IsPillaged=function()return false end,GetX=function()return 10 end,GetY=function()return 0 end};
   tailor={GetType=function()return 1 end,IsComplete=function()return tailorComplete end,IsPillaged=function()return false end,GetX=function()return 11 end,GetY=function()return 0 end};
   campus={GetType=function()return 2 end};
   ds={GetNumDistricts=function()return 3 end,GetDistrictByIndex=function(self,i)return ({[0]=baker,[1]=tailor,[2]=campus})[i]end};
   city={GetID=function()return 65536 end,GetDistricts=function()return ds end};
   player={IsAlive=function()return true end,IsMajor=function()return true end,GetCities=function()return {Members=function()return ipairs({city})end}end};
   Players={[1]=player};Map={GetPlot=function(x,y)return {GetIndex=function()return x+74*y end}end};
   CSCBASE={events={},errors={}};CSCBASE.capture=function()return {events=CSCBASE.events}end;
   Events={PlayerTurnDeactivated={Add=function(f)handler=f end}};print=function()end;
  ''')
  if prefix:lua.execute("CSCBASE.events={{event='quarter_completion_observed',player=1,city=65536,plot=10,quarter_type='BAKERS'}}")
  lua.execute((H/'profile_completion_observer.lua').read_text());return lua
 def test_native_style_collection_complete_only(self):
  lua=self.setup_lua();lua.execute('handler(1)');b=lua.globals().CSCBASE
  self.assertEqual(len(b.events),1);self.assertEqual(b.events[1].quarter_type,'BAKERS');self.assertIsNone(b.events[1].quarter);self.assertEqual(len(b.errors),0)
 def test_repeated_turn_no_duplicate_then_new_completion(self):
  lua=self.setup_lua();lua.execute('handler(1);turn=11;handler(1);tailorComplete=true;handler(1)')
  self.assertEqual(len(lua.globals().CSCBASE.events),2);self.assertEqual(lua.globals().CSC_COMPLETION_OBSERVER.observations,2)
 def test_inherited_prefix_not_recounted(self):
  lua=self.setup_lua(True);lua.execute('handler(1)');self.assertEqual(len(lua.globals().CSCBASE.events),1);self.assertEqual(lua.globals().CSC_COMPLETION_OBSERVER.observations,0)
 def test_readonly_and_metadata(self):
  lua=self.setup_lua();lua.execute('handler(1);snapshot=CSCBASE.capture()');self.assertEqual(lua.globals().writes,0);self.assertEqual(lua.globals().snapshot.completion_observer.major_calls,1)
unittest.main()
