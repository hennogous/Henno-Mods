"""Native schema gates and independent actual Lua51 UI controls, not choice proof."""
import json,os,sqlite3,sys,unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime,LuaError
import native_profile_test as driver
ROOT=Path(__file__).resolve().parents[3]
SQL=(ROOT/'Civ Supply Chains/ModSupport/ModSupport_RH_AI.sql').read_text().split('-- BEGIN CSC RH MATERIAL-BACKED WORKSHOP FORECAST V6',1)[1].split('-- END CSC RH MATERIAL-BACKED WORKSHOP FORECAST V6',1)[0]
LUA=(ROOT/'project/tools/ai_tuning/profile_workshop_forecast.lua').read_text()
validate=driver.validate_workshop_database
def db(basic=False):
 p=Path(os.environ['CSC_TEST_BASIC_DATABASE'if basic else'CSC_TEST_NATIVE_DATABASE']);c=sqlite3.connect(':memory:');source=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True);source.backup(c);source.close();return c
def dump(c,exclude=False):
 return {t:sorted(repr(r)for r in c.execute('SELECT * FROM "'+t+'"')if not exclude or not any(isinstance(v,str)and'CSC_RH_WORKSHOP_'in v for v in r))for t, in c.execute("SELECT name FROM sqlite_master WHERE type='table'AND name NOT LIKE 'sqlite_%'")}
class FactSQL(unittest.TestCase):
 def test_Basic_has_zero_changes(self):
  c=db(True);before=dump(c);c.executescript(SQL);self.assertEqual(before,dump(c))
 def test_prior_RH_rows_unchanged_and_FKs_valid(self):
  c=db();before=dump(c,True);c.executescript(SQL);self.assertEqual(before,dump(c,True));self.assertFalse(list(c.execute('PRAGMA foreign_key_check')))
 def test_reapply_idempotent(self):
  c=db();c.executescript(SQL);before=dump(c);c.executescript(SQL);self.assertEqual(before,dump(c))
 def test_active_native_properties_not_empire_collections(self):
  c=db();c.executescript(SQL);validate(c)
  self.assertFalse(list(c.execute("SELECT * FROM RequirementArguments WHERE RequirementId LIKE 'REQ_CSC_RH_WORKSHOP_%'AND Name='CollectionType'")))
 def test_Both_needs_Base_and_original_AI_in_both_gates(self):
  c=db();c.executescript(SQL)
  for key in('BASE','BOTH_EXTRA'):
   rows={r[0]for r in c.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?',('REQSET_CSC_RH_WORKSHOP_OWNER_'+key,))}
   self.assertIn('REQ_CSC_RH_CUSTOMER_FORECAST_CONFIGURED_AI',rows);self.assertIn('REQ_CSC_RH_WORKSHOP_FACT_BASE',rows)
   self.assertEqual('REQ_CSC_RH_WORKSHOP_FACT_SPEC'in rows,key=='BOTH_EXTRA')
 def test_only_Tailors_Workshop_private_value_without_building_presence(self):
  c=db();c.executescript(SQL)
  self.assertEqual(set(c.execute("SELECT DistrictType,ModifierId FROM DistrictModifiers WHERE ModifierId LIKE 'MOD_CSC_RH_WORKSHOP_%'")),{('DISTRICT_CSC_TAILORS_QUARTER','MOD_CSC_RH_WORKSHOP_FORECAST_'+k)for k in('BASE','BOTH_EXTRA')})
  for key,amount in(('BASE','80'),('BOTH_EXTRA','40')):
   self.assertEqual(set(c.execute('SELECT Name,Value FROM ModifierArguments WHERE ModifierId=?',('MOD_CSC_RH_WORKSHOP_FORECAST_'+key,))),{('Amount',amount),('BuildingType','BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'),('YieldType','YIELD_CSC_AI_PLACEMENT')})
  self.assertFalse(list(c.execute("SELECT * FROM RequirementArguments WHERE RequirementId LIKE 'REQ_CSC_RH_WORKSHOP_%'AND Value='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'")))
 def test_preflight_rejects_wrong_property_and_missing_active_gate(self):
  c=db();c.executescript(SQL)
  c.execute("UPDATE RequirementArguments SET Value='TYPO'WHERE RequirementId='REQ_CSC_RH_WORKSHOP_FACT_BASE'AND Name='PropertyName'")
  with self.assertRaises(AssertionError):validate(c)
  c.execute("UPDATE RequirementArguments SET Value='CSC_RH_WORKSHOP_BASE_PRESENT'WHERE RequirementId='REQ_CSC_RH_WORKSHOP_FACT_BASE'AND Name='PropertyName'")
  c.execute("DELETE FROM RequirementSetRequirements WHERE RequirementSetId='REQSET_CSC_RH_WORKSHOP_OWNER_BASE'AND RequirementId='REQ_CSC_RH_WORKSHOP_FACT_BASE'")
  with self.assertRaises(AssertionError):validate(c)

class ReaderControls(unittest.TestCase):
 def run_reader(self,setup='',target=25):
  e=LuaRuntime();captured=[];e.globals().print=lambda x:captured.append(x)
  e.execute('''
ui_turn=25;human=false;currentHuman=false;hasQuarter=true;complete=true;pillaged=false;built=false;actual=80;actualBuilt=80;base=true;spec=false;foreign=false;covered=false;known=true;marker=1;canProduce=true;noCities=false;secondCity=false
function rows(values)return function()local i=0;return function()i=i+1;return values[i]end end end
function collection(values)return{Members=function()local i=0;return function()i=i+1;if values[i]then return i,values[i]end end end}end
Game={GetCurrentGameTurn=function()return ui_turn end}
local workshop={Index=101,Hash=5001,BuildingType='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'}
GameInfo={Buildings={BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP=workshop},Districts={DISTRICT_CSC_TAILORS_QUARTER={Index=20}},Yields={YIELD_CSC_AI_PLACEMENT={YieldType='YIELD_CSC_AI_PLACEMENT'}},Resources={[1]={ResourceType='RESOURCE_TEST_FIBRE',PrereqTech='TECH_TEST'},[2]={ResourceType='RESOURCE_TEST_DYE'}},Technologies={TECH_TEST={Index=9}},Civics={}}
GameInfo.Resources.RESOURCE_TEST_FIBRE=GameInfo.Resources[1];GameInfo.Resources.RESOURCE_TEST_DYE=GameInfo.Resources[2]
GameInfo.Improvement_ValidResources=rows({{ResourceType='RESOURCE_TEST_FIBRE'},{ResourceType='RESOURCE_TEST_DYE'}})
GameInfo.TypeTags=rows({{Type='RESOURCE_TEST_FIBRE',Tag='CLASS_CSC_TAILORS_BASE'},{Type='RESOURCE_TEST_DYE',Tag='CLASS_CSC_TAILORS_SPEC'}})
ExposedMembers={CSC_RH_CustomerRoles={version=2,errors={}},CSC_AI_AssistanceUI={InitialHumanPlayers=function()return{['1']=human}end}}
local quarter={GetIndex=function()return 100 end,GetProperty=function(self,key)if key=='CSC_RH_CUSTOMER_CONFIGURED_AI'then return marker end;local ok=not human and not foreign and not covered;if key=='CSC_RH_WORKSHOP_BASE_PRESENT'then if factOverride~=nil then return factOverride end;return ok and base and known and 1 or 0 end;if key=='CSC_RH_WORKSHOP_SPEC_PRESENT'then return ok and spec and 1 or 0 end;error('unexpected property')end,GetX=function()return 0 end,GetY=function()return 0 end}
local function neighbor(resource,index)return{GetIndex=function()return index end,GetResourceType=function()return resource end,GetOwner=function()return foreign and 2 or 1 end,GetDistrictType=function()return covered and 5 or -1 end}end
Map={GetPlotByIndex=function(index)assert(index==100);return quarter end,GetPlot=function()return quarter end,GetAdjacentPlots=function()local out={};if base then out[#out+1]=neighbor(1,101)end;if spec then out[#out+1]=neighbor(2,102)end;return out end}
function makecity(id,withQuarter,value)
 local district={GetType=function()return 20 end,GetX=function()return 0 end,GetY=function()return 0 end}
 local ds=collection(withQuarter and{district}or{});ds.HasDistrict=function(self,index,mustComplete)assert(index==20 and mustComplete);return complete end;ds.IsPillaged=function()return pillaged end
 return{GetOwner=function()return 1 end,GetID=function()return id end,GetName=function()return 'City'..id end,GetDistricts=function()return ds end,GetBuildings=function()return{HasBuilding=function()return built end}end,
 GetBuildingPotentialYield=function(self,hash,yield)assert(hash==5001);if yield=='YIELD_CULTURE'then return culturePotential or 0 end;assert(yield=='YIELD_CSC_AI_PLACEMENT');return value end,GetBuildingYield=function(self,index,yield)if yield=='YIELD_CULTURE'then return cultureActual or 0 end;return actualBuilt end,
 GetBuildQueue=function()return{CanProduce=function(self,hash,first,second)assert(hash==5001 and first==false and second==true);return canProduce,{'LOCK_REASON',{detail='native-table'}}end}end}
end
function prepare()
 local cities={};if not noCities then cities[1]=makecity(11,hasQuarter,actual);if secondCity then cities[2]=makecity(12,false,0)end end
 Players={[1]={IsAlive=function()return true end,IsHuman=function()return currentHuman end,GetCities=function()return collection(cities)end,GetTechs=function()return{HasTech=function()return known end}end}}
end
''');e.execute(setup);e.execute('prepare()');e.execute(LUA.replace('__TARGET_TURN__',str(target)))
  return json.loads(next(x.split('=',1)[1]for x in captured if x.startswith('CSC_PROFILE_WORKSHOP_FORECAST=')))
 def test_Base_and_Both_expected_and_native_table_reasons(self):
  x=self.run_reader();self.assertEqual(x['records'][0]['expected'],80);self.assertTrue(x['unbuilt_forecast_observed']);self.assertIn('native-table',x['records'][0]['native_reasons'])
  x=self.run_reader('spec=true;actual=120');self.assertEqual(x['records'][0]['expected'],120);self.assertEqual(x['controls']['failed'],0)
 def test_spec_only_foreign_covered_hidden_noBase_zero(self):
  for setup in('base=false;spec=true','foreign=true','covered=true','known=false'):
   x=self.run_reader(setup+';actual=0');self.assertEqual(x['controls']['failed'],0);self.assertEqual(x['records'][0]['expected'],0);self.assertFalse(x['application_observed'])
 def test_original_human_zero_even_when_current_AI(self):
  x=self.run_reader('human=true;marker=0;currentHuman=false;actual=0');self.assertEqual(x['controls']['failed'],0);self.assertEqual(x['controls']['negative_human'],1)
 def test_actual_human_building_checked(self):
  x=self.run_reader('human=true;marker=0;actual=0;built=true;actualBuilt=80');self.assertEqual(x['controls']['failed'],1)
 def test_no_quarter_and_cross_city_no_bleed(self):
  x=self.run_reader('hasQuarter=false;actual=0');self.assertEqual(x['controls']['negative_no_quarter'],1)
  x=self.run_reader('secondCity=true');self.assertEqual(x['records'][1]['expected'],0);self.assertEqual(x['controls']['failed'],0)
 def test_incomplete_pillaged_observed_uncertain(self):
  for setup in('complete=false','pillaged=true'):
   x=self.run_reader(setup);self.assertEqual(x['controls']['uncertain'],1);self.assertFalse(x['application_observed'])
 def test_bad_marker_and_bad_value_fail(self):
  for setup in('marker=nil','actual=0'):
   self.assertGreater(self.run_reader(setup)['controls']['failed'],0)
 def test_built_and_unbuilt_application_separate(self):
  x=self.run_reader('built=true');self.assertTrue(x['application_observed']);self.assertFalse(x['unbuilt_forecast_observed'])
 def test_native_legality_does_not_change_value_expected(self):
  x=self.run_reader('canProduce=false');self.assertFalse(x['records'][0]['native_can_produce']);self.assertEqual(x['controls']['failed'],0)
 def test_UI_lag_and_initial_absence(self):
  self.assertEqual(self.run_reader('ui_turn=24')['ui_turn'],24)
  with self.assertRaises(LuaError):self.run_reader('ui_turn=23')
  self.assertFalse(self.run_reader('noCities=true')['application_observed'])
 def test_reader_has_no_mutations_or_Gameplay_only_city_APIs(self):
  for token in('SetProperty','SetActive','SetTurns','CreateBuilding','ChangeGoldBalance','RequestOperation','GetBuildingLocation','GetDistrictByIndex','GetNumDistricts'):
   self.assertNotRegex(LUA,r'\b'+token+r'\s*\(')

 def test_inconsistent_mirrored_fact_is_failure_even_when_value_matches(self):
  self.assertGreater(self.run_reader('factOverride=0')['controls']['failed'],0)
 def test_AI_built_actual_yield_checked_separately_from_potential(self):
  self.assertGreater(self.run_reader('built=true;actualBuilt=0')['controls']['failed'],0)


 def test_public_Culture_is_recorded_separately_not_assumed_from_private_value(self):
  x=self.run_reader('built=true;culturePotential=7;cultureActual=3');self.assertEqual(x['records'][0]['potential_culture'],7);self.assertEqual(x['records'][0]['actual_culture'],3);self.assertEqual(x['controls']['failed'],0)
if __name__=='__main__':unittest.main()
