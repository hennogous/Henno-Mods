"""Actual Lua51 S2-or-S3 release tests; captured150 physical projections, no game."""
import copy,json,os,sys,unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime
ROOT=Path(os.environ.get('CSC_SCREEN_REPO_ROOT',Path(__file__).resolve().parents[3]))
sys.path.insert(0,str(ROOT/'project/tools/ai_tuning'))
AI=Path(os.environ.get('CSC_SCREEN_STAGE23_SOURCE_DIR',ROOT/'Civ Supply Chains/Lua_UI/AI'))
HOST=(AI/'CSC_AI_Assistance.lua').read_text();POLICY=(AI/'CSC_AI_OpportunityPolicy.lua').read_text()
# Exact native150 projection; only relevant Quarter/city facts embedded, no DB/save copy.
# Source SHA256 eabe002785f878d0862a5c6f78780914851bae8472be92704954b5a41eb5e066
REAL_CASES=[{'city': {'buildings': [{'index': 147,
                          'pillaged': False,
                          'plot': 2165,
                          'stage': 2,
                          'type': 'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'},
                         {'index': 148,
                          'pillaged': False,
                          'plot': 2165,
                          'stage': 3,
                          'type': 'BUILDING_CSC_TAILORS_TAILOR'},
                         {'index': 11, 'pillaged': False, 'plot': 2164, 'type': 'BUILDING_TEMPLE'}],
           'city': 458758,
           'name': 'LOC_CITY_NAME_BUHEN',
           'player': 1,
           'properties': {'CSC_BAKERS_STAGE_2_EFFECT_GROWTH': {'observed': True, 'present': False},
                          'CSC_BAKERS_STAGE_3_EFFECT_HOUSING': {'observed': True, 'present': False},
                          'CSC_BAKERS_STAGE_4_EFFECT_TOURISM': {'observed': True, 'present': False},
                          'CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION': {'observed': True, 'present': False},
                          'CSC_TAILORS_STAGE_3_EFFECT_FAITH': {'observed': True, 'present': True, 'value': 1},
                          'CSC_TAILORS_STAGE_4_EFFECT_TOURISM': {'observed': True, 'present': False}},
           'x': 20,
           'y': 30},
  'quarter': {'city': 458758,
              'complete': True,
              'customers': [{'building': {'index': 11,
                                          'pillaged': False,
                                          'plot': 2164,
                                          'type': 'BUILDING_TEMPLE'},
                             'city': 458758,
                             'district': 'DISTRICT_HOLY_SITE',
                             'district_complete': True,
                             'district_functioning': True,
                             'district_owner': 1,
                             'district_pillaged': False,
                             'owned': True,
                             'player': 1,
                             'plot': 2164,
                             'stage': 3}],
              'materials': [{'base_mapped': False,
                             'district': 0,
                             'native_valid': False,
                             'owner': 1,
                             'pillaged': False,
                             'plot': 2240,
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': False,
                             'working_base': False,
                             'working_spec': False},
                            {'base_mapped': True,
                             'district': -1,
                             'improvement': 'IMPROVEMENT_FARM',
                             'native_valid': True,
                             'owner': 1,
                             'pillaged': False,
                             'plot': 2166,
                             'resource': 'RESOURCE_CSC_FLAX',
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': True,
                             'working_base': True,
                             'working_spec': False},
                            {'base_mapped': False,
                             'district': -1,
                             'improvement': 'IMPROVEMENT_FARM',
                             'native_valid': False,
                             'owner': 1,
                             'pillaged': False,
                             'plot': 2092,
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': False,
                             'working_base': False,
                             'working_spec': False},
                            {'base_mapped': False,
                             'district': -1,
                             'improvement': 'IMPROVEMENT_PLANTATION',
                             'native_valid': True,
                             'owner': 1,
                             'pillaged': False,
                             'plot': 2091,
                             'resource': 'RESOURCE_SILK',
                             'revealed': True,
                             'spec_mapped': True,
                             'visible': True,
                             'working_base': False,
                             'working_spec': True},
                            {'base_mapped': False,
                             'district': 1,
                             'native_valid': False,
                             'owner': 1,
                             'pillaged': False,
                             'plot': 2164,
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': False,
                             'working_base': False,
                             'working_spec': False},
                            {'base_mapped': False,
                             'district': -1,
                             'improvement': 'IMPROVEMENT_FARM',
                             'native_valid': False,
                             'owner': 1,
                             'pillaged': False,
                             'plot': 2239,
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': False,
                             'working_base': False,
                             'working_spec': False}],
              'owner': 1,
              'pillaged': False,
              'player': 1,
              'producers': [{'index': 147,
                             'pillaged': False,
                             'plot': 2165,
                             'stage': 2,
                             'type': 'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'},
                            {'index': 148,
                             'pillaged': False,
                             'plot': 2165,
                             'stage': 3,
                             'type': 'BUILDING_CSC_TAILORS_TAILOR'}],
              'quarter': 'TAILORS',
              'source': 2165}},
 {'city': {'buildings': [{'index': 147,
                          'pillaged': False,
                          'plot': 2562,
                          'stage': 2,
                          'type': 'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'},
                         {'index': 148,
                          'pillaged': False,
                          'plot': 2562,
                          'stage': 3,
                          'type': 'BUILDING_CSC_TAILORS_TAILOR'},
                         {'index': 11, 'pillaged': False, 'plot': 2561, 'type': 'BUILDING_TEMPLE'}],
           'city': 65536,
           'name': 'LOC_CITY_NAME_QARAQORUM',
           'player': 3,
           'properties': {'CSC_BAKERS_STAGE_2_EFFECT_GROWTH': {'observed': True, 'present': False},
                          'CSC_BAKERS_STAGE_3_EFFECT_HOUSING': {'observed': True, 'present': False},
                          'CSC_BAKERS_STAGE_4_EFFECT_TOURISM': {'observed': True, 'present': False},
                          'CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION': {'observed': True, 'present': False},
                          'CSC_TAILORS_STAGE_3_EFFECT_FAITH': {'observed': True, 'present': True, 'value': 1},
                          'CSC_TAILORS_STAGE_4_EFFECT_TOURISM': {'observed': True, 'present': False}},
           'x': 46,
           'y': 32},
  'quarter': {'city': 65536,
              'complete': True,
              'customers': [{'building': {'index': 11,
                                          'pillaged': False,
                                          'plot': 2561,
                                          'type': 'BUILDING_TEMPLE'},
                             'city': 65536,
                             'district': 'DISTRICT_HOLY_SITE',
                             'district_complete': True,
                             'district_functioning': True,
                             'district_owner': 3,
                             'district_pillaged': False,
                             'owned': True,
                             'player': 3,
                             'plot': 2561,
                             'stage': 3}],
              'materials': [{'base_mapped': True,
                             'district': -1,
                             'improvement': 'IMPROVEMENT_FARM',
                             'native_valid': True,
                             'owner': 3,
                             'pillaged': False,
                             'plot': 2636,
                             'resource': 'RESOURCE_CSC_FLAX',
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': True,
                             'working_base': True,
                             'working_spec': False},
                            {'base_mapped': False,
                             'district': -1,
                             'improvement': 'IMPROVEMENT_FARM',
                             'native_valid': True,
                             'owner': 3,
                             'pillaged': False,
                             'plot': 2563,
                             'resource': 'RESOURCE_MAIZE',
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': True,
                             'working_base': False,
                             'working_spec': False},
                            {'base_mapped': False,
                             'district': 27,
                             'native_valid': False,
                             'owner': 3,
                             'pillaged': False,
                             'plot': 2488,
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': False,
                             'working_base': False,
                             'working_spec': False},
                            {'base_mapped': False,
                             'district': -1,
                             'improvement': 'IMPROVEMENT_FARM',
                             'native_valid': False,
                             'owner': 3,
                             'pillaged': False,
                             'plot': 2487,
                             'resource': 'RESOURCE_HORSES',
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': True,
                             'working_base': False,
                             'working_spec': False},
                            {'base_mapped': False,
                             'district': 1,
                             'native_valid': False,
                             'owner': 3,
                             'pillaged': False,
                             'plot': 2561,
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': False,
                             'working_base': False,
                             'working_spec': False},
                            {'base_mapped': False,
                             'district': -1,
                             'improvement': 'IMPROVEMENT_FARM',
                             'native_valid': True,
                             'owner': 3,
                             'pillaged': False,
                             'plot': 2635,
                             'resource': 'RESOURCE_MAIZE',
                             'revealed': True,
                             'spec_mapped': False,
                             'visible': True,
                             'working_base': False,
                             'working_spec': False}],
              'owner': 3,
              'pillaged': False,
              'player': 3,
              'producers': [{'index': 147,
                             'pillaged': False,
                             'plot': 2562,
                             'stage': 2,
                             'type': 'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'},
                            {'index': 148,
                             'pillaged': False,
                             'plot': 2562,
                             'stage': 3,
                             'type': 'BUILDING_CSC_TAILORS_TAILOR'}],
              'quarter': 'TAILORS',
              'source': 2562}}]

def lua_value(value):
 if value is None:return 'nil'
 if isinstance(value,bool):return str(value).lower()
 if isinstance(value,(int,float)):return str(value)
 if isinstance(value,str):return json.dumps(value)
 if isinstance(value,list):return '{'+','.join(lua_value(x)for x in value)+'}'
 return '{'+','.join('['+lua_value(k)+']='+lua_value(v)for k,v in value.items())+'}'
ADAPT=r"""
local function rows(a)return function()local i=0;return function()i=i+1;return a[i]end end end
local q,c=case.quarter,case.city;local pid=q.player
GameInfo={Districts={},Buildings={},Resources={},Improvements={},Technologies={}}
local function district(name,index)GameInfo.Districts[name]={Index=index,DistrictType=name};GameInfo.Districts[index]=GameInfo.Districts[name]end
district('DISTRICT_CSC_TAILORS_QUARTER',3);district('DISTRICT_HOLY_SITE',1);district('DISTRICT_CITY_CENTER',0);district('DISTRICT_HARBOR',4);district('DISTRICT_COMMERCIAL_HUB',5)
for _,b in ipairs(c.buildings)do GameInfo.Buildings[b.type]={Index=b.index,BuildingType=b.type}end
GameInfo.Buildings.BUILDING_LIGHTHOUSE={Index=99,BuildingType='BUILDING_LIGHTHOUSE'}
GameInfo.Buildings.BUILDING_MARKET={Index=12,BuildingType='BUILDING_MARKET'}
GameInfo.TypeTags=rows({{Type=5,Tag='CLASS_CSC_TAILORS_BASE'},{Type=6,Tag='CLASS_CSC_TAILORS_SPEC'}})
GameInfo.Resources[5]={Index=5,ResourceType='RESOURCE_CSC_FLAX'};GameInfo.Resources[6]={Index=6,ResourceType='RESOURCE_SILK'}
GameInfo.Improvements[10]={ImprovementType='IMPROVEMENT_FARM'};GameInfo.Improvements[11]={ImprovementType='IMPROVEMENT_PLANTATION'}
GameInfo.Improvement_ValidResources=rows({{ResourceType='RESOURCE_CSC_FLAX',ImprovementType='IMPROVEMENT_FARM'},{ResourceType='RESOURCE_SILK',ImprovementType='IMPROVEMENT_PLANTATION'}})
GameInfo.CSC_AI_Profile=rows({{Id='ACTIVE',Mode='RH'}})
GameInfo.CSC_QuarterFlowBuildings=rows({{QuarterKey='TAILORS',Stage=2,BuildingType='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'},{QuarterKey='TAILORS',Stage=3,BuildingType='BUILDING_CSC_TAILORS_TAILOR'}})
GameInfo.CSC_QuarterCustomerBuildings=rows({{QuarterKey='TAILORS',ProducerStage=2,DistrictType='DISTRICT_HARBOR',BuildingType='BUILDING_LIGHTHOUSE'}})
transactions={{TransactionId='CSC_TAILORS_TAILOR_TEMPLE',SellerDistrictType='DISTRICT_CSC_TAILORS_QUARTER',SellerBuildingType='BUILDING_CSC_TAILORS_TAILOR',CustomerDistrictType='DISTRICT_HOLY_SITE',CustomerBuildingType='BUILDING_TEMPLE'},{TransactionId='CSC_TAILORS_TAILOR_MARKET',SellerDistrictType='DISTRICT_CSC_TAILORS_QUARTER',SellerBuildingType='BUILDING_CSC_TAILORS_TAILOR',CustomerDistrictType='DISTRICT_COMMERCIAL_HUB',CustomerBuildingType='BUILDING_MARKET'}}
GameInfo.CSC_Stage3CustomerTransactions=rows(transactions)
properties={CSC_AI_SELECTIVE_SCREEN_V1={version=1},CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS={['0']=true},CSC_AI_ASSISTANCE_V1_HOST_REVISION=3};writes=0
Game={GetCurrentGameTurn=function()return 150 end,GetProperty=function(self,k)return properties[k]end,SetProperty=function(self,k,v)writes=writes+1;properties[k]=v end}
plots={};local neighbors={};local function plot(index,owner,district,resource,improvement,pillaged,reveal,visible)
 local p={index=index,owner=owner,district=district,res=resource,imp=improvement,pillaged=pillaged,revealed=reveal,visible=visible}
 function p:GetIndex()return self.index end;function p:GetX()return self.index end;function p:GetY()return 0 end;function p:GetOwner()return self.owner end;function p:GetDistrictType()return self.district end;function p:GetResourceType()return self.res end;function p:GetImprovementType()return self.imp end;function p:IsImprovementPillaged()return self.pillaged end
 plots[index]=p;return p
end
plot(q.source,q.owner,3,-1,-1,false,true,true)
local base,spec
for _,m in ipairs(q.materials)do
 local resource=m.base_mapped and 5 or m.spec_mapped and 6 or -1;local improvement=m.improvement=='IMPROVEMENT_FARM'and 10 or m.improvement=='IMPROVEMENT_PLANTATION'and 11 or -1
 plot(m.plot,m.owner,m.district,resource,improvement,m.pillaged,m.revealed,m.visible);neighbors[#neighbors+1]=m.plot
 if m.base_mapped then base=m.plot end;if m.spec_mapped then spec=m.plot end
end
local ds={{GetType=function()return 3 end,GetX=function()return q.source end,GetY=function()return 0 end,IsComplete=function()return q.complete end,IsPillaged=function()return q.pillaged end}}
for _,customer in ipairs(q.customers)do local kind=GameInfo.Districts[customer.district].Index
 ds[#ds+1]={GetType=function()return kind end,GetX=function()return customer.plot end,GetY=function()return 0 end,IsComplete=function()return customer.district_complete end,IsPillaged=function()return customer.district_pillaged end}
end
city={GetID=function()return c.city end,GetX=function()return c.x end,GetY=function()return c.y end,GetOwner=function()return pid end,GetProperty=function(self,key)local p=c.properties[key];return p and p.value end,GetBuildings=function()return{HasBuilding=function(self,index)for _,b in ipairs(c.buildings)do if b.index==index then return true end end;return false end,IsPillaged=function(self,index)for _,b in ipairs(c.buildings)do if b.index==index then return b.pillaged end end;return false end}end,GetDistricts=function()return{GetNumDistricts=function()return #ds end,GetDistrictByIndex=function(self,i)return ds[i+1]end}end}
Players={[pid]={GetCities=function()return{Members=function()return ipairs({city})end}end}}
Map={GetPlotByIndex=function(index)return plots[index]end,GetPlot=function(x,y)return plots[x]end,GetAdjacentPlot=function(x,y,d)return x==q.source and plots[neighbors[d+1]]or nil end}
PlayersVisibility={[pid]={IsRevealed=function(self,x,y)return plots[x].revealed end}};CSC_Adjacency={ResourceVisible=function(player,index)return true end}
ExposedMembers={CSC_AI_AssistanceUI={}};Events={PlayerTurnActivated={Add=function()end}};include=function()end;print=function()end
-- This hypothetical tracked record tests release on the exact existing native
-- physical chain. It does not assert the native chain was assisted.
site=pid..':'..c.city..':TAILORS:'..q.source
properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1={version=1,records={[site]={player=pid,city=c.city,quarter='TAILORS',source=q.source,city_x=c.x,city_y=c.y,first_turn=20,status='open',materials={base,spec or q.materials[2].plot}}},decisions={}}
"""
class Stage23(unittest.TestCase):
 def physical(self,data,setup=''):
  lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('case='+lua_value(data));lua.execute(ADAPT);lua.execute(setup);lua.execute(POLICY);lua.execute(HOST);return lua,lua.eval('CSC_AI_Assistance.InspectScreen(case.quarter.player).records[1]')
 def test_two_exact_native150_inland_Tailors_release_via_registered_Temple(self):
  for case in REAL_CASES:
   lua,row=self.physical(copy.deepcopy(case));self.assertEqual(row.status,'operational');self.assertEqual(row.facts.operational_stage,3);self.assertEqual(row.facts.operational_path.transaction,'CSC_TAILORS_TAILOR_TEMPLE');self.assertEqual(row.facts.operational_path.customer.building,'BUILDING_TEMPLE');self.assertEqual(row.facts.effect_corroboration[3].value,1);self.assertEqual(lua.globals().writes,0)
 def test_Qaraqorum_no_Spec_no_Harbor_is_not_Both_gated_at_release(self):
  case=copy.deepcopy(REAL_CASES[1]);self.assertFalse(any(m['working_spec']for m in case['quarter']['materials']));lua,row=self.physical(case);self.assertEqual(row.status,'operational');self.assertEqual(len(row.facts.customers),0)
 def test_missing_or_pillaged_actual_path_producer_prerequisite_or_customer_blocks(self):
  for name in('BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP','BUILDING_CSC_TAILORS_TAILOR','BUILDING_TEMPLE'):
   for missing in(True,False):
    case=copy.deepcopy(REAL_CASES[0])
    if missing:case['city']['buildings']=[b for b in case['city']['buildings']if b['type']!=name]
    else:next(b for b in case['city']['buildings']if b['type']==name)['pillaged']=True
    lua,row=self.physical(case);self.assertNotEqual(row.status,'operational')
 def test_customer_foreign_incomplete_pillaged_or_wrong_registered_pair_blocks(self):
  for field,value in(('district_owner',9),('district_complete',False),('district_pillaged',True)):
   case=copy.deepcopy(REAL_CASES[0]);case['quarter']['customers'][0][field]=value
   if field=='district_owner':next(m for m in case['quarter']['materials']if m['plot']==case['quarter']['customers'][0]['plot'])['owner']=value
   lua,row=self.physical(case);self.assertNotEqual(row.status,'operational')
  lua,row=self.physical(copy.deepcopy(REAL_CASES[0]),"transactions[1].CustomerBuildingType='BUILDING_MARKET'");self.assertNotEqual(row.status,'operational')
 def test_flag_alone_never_releases_and_absent_flag_does_not_override_structure(self):
  case=copy.deepcopy(REAL_CASES[0]);case['city']['buildings']=[b for b in case['city']['buildings']if b['type']!='BUILDING_TEMPLE'];lua,row=self.physical(case);self.assertNotEqual(row.status,'operational');self.assertEqual(row.facts.effect_corroboration[3].value,1)
  case=copy.deepcopy(REAL_CASES[0]);case['city']['properties']['CSC_TAILORS_STAGE_3_EFFECT_FAITH']={};lua,row=self.physical(case);self.assertEqual(row.status,'operational');self.assertFalse(row.facts.effect_corroboration[3].present)
 def test_full_supply_Base_gate_not_claimed_as_universal_Stage3_transaction_gate(self):
  case=copy.deepcopy(REAL_CASES[0]);next(m for m in case['quarter']['materials']if m['base_mapped'])['pillaged']=True;lua,row=self.physical(case);self.assertNotEqual(row.status,'operational');self.assertEqual(len(row.facts.stage3_paths),1);self.assertIn('not asserted',row.facts.stage3_paths[1].transaction_base_gate)
 def test_direct_unique_seller_customer_and_district_variants_qualify(self):
  case=copy.deepcopy(REAL_CASES[0]);names={'BUILDING_CSC_TAILORS_TAILOR':('BUILDING_UNIQUE_TAILOR',248),'BUILDING_TEMPLE':('BUILDING_UNIQUE_TEMPLE',211)}
  for b in case['city']['buildings']:
   if b['type']in names:b['type'],b['index']=names[b['type']]
  setup="""GameInfo.BuildingReplaces=function()local a={{ReplacesBuildingType='BUILDING_CSC_TAILORS_TAILOR',CivUniqueBuildingType='BUILDING_UNIQUE_TAILOR'},{ReplacesBuildingType='BUILDING_TEMPLE',CivUniqueBuildingType='BUILDING_UNIQUE_TEMPLE'}};local i=0;return function()i=i+1;return a[i]end end
   GameInfo.Districts.DISTRICT_HOLY_SITE.Index=9;GameInfo.Districts.DISTRICT_UNIQUE_HOLY_SITE={Index=1,DistrictType='DISTRICT_UNIQUE_HOLY_SITE'};GameInfo.Districts[1]=GameInfo.Districts.DISTRICT_UNIQUE_HOLY_SITE
   GameInfo.DistrictReplaces=function()local done=false;return function()if not done then done=true;return{ReplacesDistrictType='DISTRICT_HOLY_SITE',CivUniqueDistrictType='DISTRICT_UNIQUE_HOLY_SITE'}end end end
  """
  lua,row=self.physical(case,setup);self.assertEqual(row.status,'operational');self.assertEqual(row.facts.operational_path.producer,'BUILDING_UNIQUE_TAILOR');self.assertEqual(row.facts.operational_path.customer.building,'BUILDING_UNIQUE_TEMPLE')
 def test_released_stage3_path_loss_becomes_maintenance(self):
  lua,row=self.physical(copy.deepcopy(REAL_CASES[0]));lua.execute("properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1.records[site].first_operational_turn=150;case.city.buildings[2].pillaged=true")
  row=lua.eval('CSC_AI_Assistance.InspectScreen(case.quarter.player).records[1]');self.assertEqual(row.status,'maintenance')
if __name__=='__main__':unittest.main()
