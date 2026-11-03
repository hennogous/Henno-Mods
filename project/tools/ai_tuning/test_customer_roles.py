"""Actual Lua51 event/property behavior, not native modifier-consumption proof."""
import sys,unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime
H=Path(__file__).resolve().parents[3]/'Civ Supply Chains/ModSupport'
FIXTURE='''
mode='RH';uiReady=true;runtimeHuman=false;owner=1;major=true;hasQuarter=true;districtType=8;writes=0;props={};savedHumans=nil;uiHumans={['0']=true}
function collection(rows)return{Members=function()local i=0;return function()i=i+1;if rows[i]then return i,rows[i]end end end}end
Game={};function Game:GetProperty(key)assert(key=='CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS');return savedHumans end
GameInfo={Districts={[8]={DistrictType='DISTRICT_CSC_BAKERS_QUARTER'},[9]={DistrictType='DISTRICT_CITY_CENTER'}}}
GameInfo.CSC_AI_Profile=function()local done=false;return function()if not done then done=true;return{Id='ACTIVE',Mode=mode}end end end
plot={GetOwner=function()return owner end,GetProperty=function(self,k)return props[k]end,SetProperty=function(self,k,v)props[k]=v;writes=writes+1 end}
Map={GetPlot=function(x,y)assert(x==3 and y==4);return plot end}
district={GetType=function()return districtType end,GetX=function()return 3 end,GetY=function()return 4 end}
districts={GetNumDistricts=function()return hasQuarter and 1 or 0 end,GetDistrictByIndex=function(self,i)assert(i==0);return district end}
city={GetDistricts=function()return districts end}
player={GetID=function()return owner end,IsMajor=function()return major end,IsHuman=function()return runtimeHuman end,GetCities=function()return collection({city})end}
Players={[0]=player,[1]=player};PlayerManager={GetAliveMajors=function()return{player}end}
local function event()local callbacks={};return{Add=function(fn)callbacks[#callbacks+1]=fn end,Fire=function(...)for _,fn in ipairs(callbacks)do fn(...)end end}end
Events={PlayerTurnActivated=event(),DistrictAddedToMap=event(),CityTransfered=event()}
ExposedMembers={};function setupUI()ExposedMembers.CSC_AI_AssistanceUI=uiReady and{InitialHumanPlayers=function()return uiHumans end}or nil end
'''
class Roles(unittest.TestCase):
 def make(self,setup=''):
  e=LuaRuntime();e.execute(FIXTURE);e.execute(setup+'\nsetupUI()');e.execute((H/'ModSupport_RH_AI_Roles.lua').read_text());return e
 def marker(self,e):return e.globals().props['CSC_RH_CUSTOMER_CONFIGURED_AI']
 def test_AI_is_stamped_once_without_orders(self):
  e=self.make();self.assertEqual(self.marker(e),1);e.execute('Events.PlayerTurnActivated.Fire(1)');self.assertEqual(e.globals().writes,1)
 def test_configured_human_excluded_during_autoplay_and_after_return(self):
  e=self.make('owner=0;runtimeHuman=false');self.assertEqual(self.marker(e),0)
  e.execute('runtimeHuman=true;Events.PlayerTurnActivated.Fire(0)');self.assertEqual(self.marker(e),0)
 def test_saved_original_identity_wins_over_new_UI_snapshot(self):
  e=self.make("owner=0;savedHumans={['0']=true};uiHumans={}");self.assertEqual(self.marker(e),0)
 def test_missing_bridge_is_failclosed_then_reconciles(self):
  e=self.make('uiReady=false');self.assertIsNone(self.marker(e));self.assertFalse(e.globals().ExposedMembers.CSC_RH_CustomerRoles.ready)
  e.execute('uiReady=true;setupUI();Events.PlayerTurnActivated.Fire(1)');self.assertEqual(self.marker(e),1)
 def test_new_quarter_placement_stamps_before_Mill(self):
  e=self.make('hasQuarter=false');self.assertIsNone(self.marker(e))
  e.execute('Events.DistrictAddedToMap.Fire(1,45,77,3,4,8)');self.assertEqual(self.marker(e),1)
 def test_capture_reclassifies_source_for_new_human_owner(self):
  e=self.make();e.execute('owner=0;Events.CityTransfered.Fire(0,77,1)');self.assertEqual(self.marker(e),0)
  e.execute('owner=1;Events.CityTransfered.Fire(1,77,0)');self.assertEqual(self.marker(e),1)
 def test_Basic_Off_and_unrelated_district_are_untouched(self):
  for setup in ("mode='BASIC'","mode='OFF'",'districtType=9'):
   e=self.make(setup);self.assertIsNone(self.marker(e));self.assertEqual(e.globals().writes,0)
 def test_minor_source_is_excluded(self):self.assertEqual(self.marker(self.make('major=false')),0)
 def test_no_economic_or_AI_order_surface(self):
  s=(H/'ModSupport_RH_AI_Roles.lua').read_text()
  for name in ('ChangeGoldBalance','SetPlotOwner','CreateDistrict','CreateBuilding','RequestOperation','SetTurns','SetActive','SetHuman'):
   self.assertNotRegex(s,r'\b'+name+r'\s*\(')
 def test_errors_are_retained_and_no_property_written(self):
  e=self.make("uiReady=false");e.execute("uiReady=true;setupUI();districts.GetNumDistricts=function()error('fixture broken binding')end;Events.PlayerTurnActivated.Fire(1)")
  self.assertEqual(len(e.globals().ExposedMembers.CSC_RH_CustomerRoles.errors),1);self.assertIsNone(self.marker(e))

SUPPLY="\ndistrictType=10;GameInfo.Districts[10]={DistrictType='DISTRICT_CSC_TAILORS_QUARTER'}\nbasePresent=true;specPresent=true;baseOwner=1;specOwner=1;baseCovered=false;specCovered=false;techKnown=true;civicKnown=true;legal=true;neighborScans=0\nplot.GetX=function()return 3 end;plot.GetY=function()return 4 end\nGameInfo.Resources={[2]={ResourceType='RESOURCE_MOD_FIBRE',PrereqTech='TECH_TEST'},[3]={ResourceType='RESOURCE_MOD_DYE',PrereqCivic='CIVIC_TEST'}}\nGameInfo.Resources.RESOURCE_MOD_FIBRE=GameInfo.Resources[2];GameInfo.Resources.RESOURCE_MOD_DYE=GameInfo.Resources[3]\nGameInfo.Technologies={TECH_TEST={Index=20}};GameInfo.Civics={CIVIC_TEST={Index=21}}\nplayer.GetTechs=function()return{HasTech=function(self,i)assert(i==20);return techKnown end}end\nplayer.GetCulture=function()return{HasCivic=function(self,i)assert(i==21);return civicKnown end}end\nlocal function rows(values)return function()local i=0;return function()i=i+1;return values[i]end end end\nGameInfo.TypeTags=rows({{Type='RESOURCE_MOD_FIBRE',Tag='CLASS_CSC_TAILORS_BASE'},{Type='RESOURCE_MOD_DYE',Tag='CLASS_CSC_TAILORS_SPEC'}})\nGameInfo.Improvement_ValidResources=function()return rows(legal and{{ResourceType='RESOURCE_MOD_FIBRE'},{ResourceType='RESOURCE_MOD_DYE'}}or{})()end\nMap.GetAdjacentPlots=function(x,y)\n assert(x==3 and y==4);neighborScans=neighborScans+1;local out={}\n if basePresent then out[#out+1]={GetOwner=function()return baseOwner end,GetDistrictType=function()return baseCovered and 9 or -1 end,GetResourceType=function()return 2 end}end\n if specPresent then out[#out+1]={GetOwner=function()return specOwner end,GetDistrictType=function()return specCovered and 9 or -1 end,GetResourceType=function()return 3 end}end\n return out\nend\nlocal function ev()local handlers={};return{Add=function(fn)handlers[#handlers+1]=fn end,Fire=function(...)for _,fn in ipairs(handlers)do fn(...)end end}end\nEvents.ResourceAddedToMap=ev();Events.ResourceRemovedFromMap=ev();Events.PlotOwnershipChanged=ev();Events.DistrictBuildProgressChanged=ev();Events.DistrictRemovedFromMap=ev();Events.PlayerTurnDeactivated=ev();Events.TechCompleted=ev();Events.CivicCompleted=ev()\n"
class SupplyFacts(unittest.TestCase):
 make=Roles.make
 marker=Roles.marker
 def facts(self,e):
  p=e.globals().props;return p['CSC_RH_WORKSHOP_BASE_PRESENT'],p['CSC_RH_WORKSHOP_SPEC_PRESENT']
 def supply(self,setup=''):return self.make(SUPPLY+setup)
 def test_native_style_newsource_has_original_AI_and_Both_facts(self):
  e=self.supply();self.assertEqual(self.marker(e),1);self.assertEqual(self.facts(e),(1,1));self.assertEqual(e.globals().ExposedMembers.CSC_RH_CustomerRoles.version,2)
 def test_Base_Spec_and_empty_sources_separate(self):
  for setup,want in(('specPresent=false',(1,0)),('basePresent=false',(0,1)),('basePresent=false;specPresent=false',(0,0))):self.assertEqual(self.facts(self.supply(setup)),want)
 def test_human_during_autoplay_and_minor_have_no_supply_reward(self):
  for setup in('owner=0;runtimeHuman=false','major=false'):
   e=self.supply(setup);self.assertEqual(self.marker(e),0);self.assertEqual(self.facts(e),(0,0))
 def test_foreign_hidden_and_covered_not_usable(self):
  for setup in('baseOwner=2','baseCovered=true','techKnown=false'):
   self.assertEqual(self.facts(self.supply(setup)),(0,1))
  self.assertEqual(self.facts(self.supply('civicKnown=false')),(1,0))
 def test_without_native_valid_improvement_no_material_reward(self):self.assertEqual(self.facts(self.supply('legal=false')),(0,0))
 def test_ownership_and_resource_events_reconcile_in_same_turn(self):
  e=self.supply();e.execute('baseOwner=2;Events.PlotOwnershipChanged.Fire()');self.assertEqual(self.facts(e),(0,1))
  e.execute('baseOwner=1;Events.PlotOwnershipChanged.Fire()');self.assertEqual(self.facts(e),(1,1))
  e.execute('basePresent=false;Events.ResourceRemovedFromMap.Fire()');self.assertEqual(self.facts(e),(0,1))
  e.execute('basePresent=true;Events.ResourceAddedToMap.Fire()');self.assertEqual(self.facts(e),(1,1))
 def test_completion_and_visibility_changes_reconcile(self):
  e=self.supply('techKnown=false');self.assertEqual(self.facts(e),(0,1))
  e.execute('techKnown=true;Events.TechCompleted.Fire()');self.assertEqual(self.facts(e),(1,1))
  e.execute('baseCovered=true;Events.DistrictBuildProgressChanged.Fire()');self.assertEqual(self.facts(e),(0,1))
  e.execute('baseCovered=false;Events.DistrictRemovedFromMap.Fire()');self.assertEqual(self.facts(e),(1,1))
 def test_new_foundation_is_stamped_without_queued_production(self):
  e=self.supply('hasQuarter=false');self.assertIsNone(self.marker(e));e.execute('Events.DistrictAddedToMap.Fire(1,45,77,3,4,10)');self.assertEqual(self.facts(e),(1,1))
 def test_capture_moves_role_and_facts_together(self):
  e=self.supply();e.execute('owner=0;Events.CityTransfered.Fire(0,77,1)');self.assertEqual(self.facts(e),(0,0))
  e.execute('owner=1;Events.CityTransfered.Fire(1,77,0)');self.assertEqual(self.facts(e),(1,1))
 def test_no_rewrite_for_unchanged_facts_and_bounded_neighbors(self):
  e=self.supply();first=e.globals().writes;e.execute('Events.PlayerTurnActivated.Fire(1)');self.assertEqual(e.globals().writes,first);self.assertEqual(e.globals().neighborScans,2)
  source=(H/'ModSupport_RH_AI_Roles.lua').read_text();self.assertNotIn('Map.GetPlotCount',source);self.assertNotIn('Map.GetGridSize',source)
 def test_failed_scan_clears_previous_positive_facts_and_keeps_error(self):
  e=self.supply();e.execute("Map.GetAdjacentPlots=function()error('fixture broken neighbors')end;Events.PlayerTurnActivated.Fire(1)")
  self.assertEqual(self.facts(e),(0,0));self.assertEqual(len(e.globals().ExposedMembers.CSC_RH_CustomerRoles.errors),1)

if __name__=='__main__':unittest.main()
