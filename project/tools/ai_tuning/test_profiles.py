"""Source gating, native-schema SQL, and actual Lua51 economic fault fixtures.

Set CSC_TEST_NATIVE_DATABASE to a preserved native DB for the SQL suite. Supply
the existing lupa runtime through PYTHONPATH; these tests install nothing.
"""
import importlib.util,json,os,sqlite3,sys,unittest,xml.etree.ElementTree as E,zlib
from pathlib import Path
from lupa.lua51 import LuaRuntime,LuaError
sys.path.insert(0,str(Path(__file__).parent))
import configure_profiles as config
ROOT=Path(__file__).resolve().parents[3]
MOD=ROOT/'Civ Supply Chains';AI=MOD/'Lua_UI/AI'
DATA=json.loads((ROOT/'project/modbuddy/CivSupplyChains.actions.json').read_text())
REGISTRY=json.loads((ROOT/'project/config/csc-ai-profiles.json').read_text())
def active_actions(enabled,mods):
 criteria={c['attributes']['id']:c for c in DATA['blocks']['actionCriteria']}
 def match(name):
  child=criteria[name]['children'][0]
  if child['tag']=='ModInUse':
   value=child['text']in mods
   return not value if child.get('attributes',{}).get('inverse')=='1'else value
  return enabled
 return [a for a in DATA['blocks']['inGameActions']
         if a['id'].startswith('CSC_AI_Mode_')and all(match(c)for c in a.get('criteria',[]))]
class Profiles(unittest.TestCase):
 def test_settings_defaults_and_dependent_subsidies(self):
  tree=E.parse(MOD/'Settings/Settings.xml').getroot()
  rows={r.get('ConfigurationId'):r for r in tree.findall('Parameters/Row')}
  for name in ('CSC_AI_ASSISTANCE','CSC_AI_SUBSIDIES'):self.assertEqual(rows[name].get('DefaultValue'),'1')
  self.assertTrue(any(r.get('ConfigurationId')=='CSC_AI_ASSISTANCE'and r.get('ConfigurationValue')=='1'and r.get('ParameterId')=='CSC_AI_Subsidies'for r in tree.findall('ParameterDependencies/Row')))
 def test_off_is_off_with_or_without_RH(self):
  self.assertEqual(active_actions(False,set()),[])
  self.assertEqual(active_actions(False,{REGISTRY['rh'][0]['modId']}),[])
 def test_basic_and_RH_are_mutually_exclusive(self):
  basic=active_actions(True,set());rh=active_actions(True,{REGISTRY['rh'][0]['modId']})
  self.assertEqual(len(basic),5);self.assertEqual(len(rh),6)
  self.assertTrue(all('_Basic_'in a['id']for a in basic))
  self.assertTrue(all('_RH_0_'in a['id']for a in rh))
 def test_future_aliases_do_not_duplicate_handlers(self):
  registry=json.loads(json.dumps(REGISTRY));registry['rh'].append(dict(key='future-test',modId='12345678-1234-1234-1234-123456789abc',loadAfter=400000000))
  generated=config.generate(DATA,registry)
  criteria={c['attributes']['id']:c for c in generated['blocks']['actionCriteria']}
  row=next(a for a in generated['blocks']['inGameActions']if a['id']=='CSC_AI_Mode_RH_1_DB')
  self.assertIn('CSC_AI_RH_No_0',row['criteria']);self.assertEqual(criteria['CSC_AI_RH_1']['children'][0]['text'],registry['rh'][1]['modId'])
 def test_generation_idempotent_and_packaged_paths_exist(self):
  self.assertEqual(config.generate(DATA,REGISTRY),DATA)
  project=E.parse(MOD/'Civ Supply Chains.civ6proj');content={r.get('Include').replace('\\','/')for r in project.findall('.//{*}Content')}
  for path in config.CONTENT:self.assertTrue((MOD/path).is_file(),path);self.assertIn(path,content)
 def test_RH_loads_after_reviewed_override_without_replacing_RH_reports(self):
  rh=next(a for a in active_actions(True,{REGISTRY['rh'][0]['modId']})if a['type']=='UpdateDatabase')
  self.assertGreater(int(rh['properties']['LoadOrder']),REGISTRY['rh'][0]['loadAfter'])
  report=next(a for a in DATA['blocks']['inGameActions']if a['id']=='CSC_AI_ReportScreen')
  self.assertIn('CSC_AI_RH_No_0',report['criteria'])
 def test_experimental_material_care_not_promoted(self):
  actions=[a for a in DATA['blocks']['inGameActions']if a['id']in ('CSC_AI_MaterialCare','CSC_AI_MaterialCare_DB')]
  self.assertFalse(actions)
 def test_external_foundation_probe_rejects_installed_owner(self):
  lua=LuaRuntime();lua.execute('ExposedMembers={CSC_AI_Assistance={}}')
  with self.assertRaisesRegex(LuaError,'Installed CSC assistance owns mutations'):
   lua.execute((ROOT/'project/tools/ai_baseline/foundation_planner.lua').read_text())
 def test_external_funded_adapter_rejects_owner_before_installing(self):
  from types import SimpleNamespace
  sys.path.insert(0,str(ROOT/'project/tools/ai_baseline'))
  from service_planner.funded_acquisition import FundedDiagnostic
  lua=LuaRuntime();lua.execute('ExposedMembers={CSC_AI_Assistance={}}')
  obj=object.__new__(FundedDiagnostic);obj.r=SimpleNamespace(cmd=lambda code,*a:lua.execute(code))
  with self.assertRaisesRegex(LuaError,'Installed CSC assistance owns mutations'):obj.install()

class NativeSchemaSQL(unittest.TestCase):
 def setUp(self):
  path=os.environ.get('CSC_TEST_NATIVE_DATABASE')
  if not path:self.skipTest('CSC_TEST_NATIVE_DATABASE not provided')
  src=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True);self.db=sqlite3.connect(':memory:');src.backup(self.db);src.close()
  self.db.create_function('Make_Hash',1,lambda x:zlib.crc32(x.encode()))
  self.db.execute("UPDATE PseudoYields SET DefaultValue=73 WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'")
  self.db.execute("UPDATE AiFavoredItems SET Value=321 WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'")
  self.db.execute("UPDATE TreeData SET DefaultData='777' WHERE TreeName='Build City Improvement' AND DefnId=2 AND NodeId IN(13,23)")
  self.db.executescript('CREATE TABLE RHAITags(YieldName TEXT PRIMARY KEY); INSERT INTO RHAITags VALUES("LOC_YIELD_RH_AI");')
 def tearDown(self):
  if hasattr(self,'db'):self.db.close()
 def apply(self,enabled,rh):
  self.db.executescript((MOD/'Data/CSC_AI_Profile.sql').read_text())
  for a in active_actions(enabled,{REGISTRY['rh'][0]['modId']}if rh else set()):
   if a['type']=='UpdateDatabase':
    for path in a['files']:self.db.executescript((MOD/path).read_text())
 def value(self,sql):return self.db.execute(sql).fetchone()[0]
 def test_basic_weights_movement_and_native_contract_targets(self):
  self.apply(True,False)
  self.assertEqual(self.value("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'"),30)
  self.assertEqual(self.value("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'"),50)
  self.assertEqual(self.value("SELECT Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_AI_BASIC_BUILDER_MOVEMENT' AND Name='Amount'"),'1')
  self.assertEqual(self.value("SELECT Mode FROM CSC_AI_Profile"),'BASIC')
  for row in self.db.execute("SELECT DefaultData FROM TreeData WHERE TreeName='Build City Improvement' AND DefnId=2 AND NodeId IN(SELECT NodeId FROM BehaviorTreeNodes WHERE TreeName='Build City Improvement' AND NodeType='Build Unit')"):
   self.assertEqual(row[0],'-1')
 def test_RH_baseline_untouched_and_private_yield_registered(self):
  before=self.db.execute("SELECT * FROM TreeData").fetchall()
  self.apply(True,True)
  self.assertEqual(self.value("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'"),73)
  self.assertEqual(self.value("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'"),321)
  self.assertEqual(before,self.db.execute('SELECT * FROM TreeData').fetchall())
  self.assertEqual(self.value("SELECT Mode FROM CSC_AI_Profile"),'RH')
  self.assertEqual(self.value("SELECT COUNT(*) FROM RHAITags WHERE YieldName='LOC_CSC_AI_PLACEMENT_NAME'"),1)
  self.assertEqual(self.value("SELECT COUNT(*) FROM Modifiers WHERE ModifierId='MOD_CSC_AI_BASIC_BUILDER_MOVEMENT'"),0)
 def test_off_preserves_baseline(self):
  self.apply(False,True)
  self.assertEqual(self.value("SELECT Mode FROM CSC_AI_Profile"),'OFF')
  self.assertEqual(self.value("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'"),73)
 def test_RH_contract_default_only_fills_missing_parameter(self):
  self.db.execute("DELETE FROM TreeData WHERE TreeName='Build City Improvement' AND NodeId=13 AND DefnId=2")
  self.apply(True,True)
  self.assertEqual(self.value("SELECT DefaultData FROM TreeData WHERE TreeName='Build City Improvement' AND NodeId=13 AND DefnId=2"),'-1')
  self.assertEqual(self.value("SELECT DefaultData FROM TreeData WHERE TreeName='Build City Improvement' AND NodeId=23 AND DefnId=2"),'777')
 def test_movement_is_AI_builder_only(self):
  self.apply(True,False)
  owner,subject=self.db.execute("SELECT OwnerRequirementSetId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId='MOD_CSC_AI_BASIC_BUILDER_MOVEMENT'").fetchone()
  self.assertIn(('REQUIREMENT_PLAYER_IS_HUMAN',1),self.db.execute('SELECT r.RequirementType,r.Inverse FROM Requirements r JOIN RequirementSetRequirements s USING(RequirementId) WHERE s.RequirementSetId=?',(owner,)).fetchall())
  self.assertEqual(self.db.execute('SELECT a.Value FROM RequirementArguments a JOIN RequirementSetRequirements s USING(RequirementId) WHERE s.RequirementSetId=? AND a.Name="UnitType"',(subject,)).fetchone()[0],'UNIT_BUILDER')
 def test_modes_reapply_without_duplicate_private_edges(self):
  for rh in (False,True):
   self.apply(True,rh)
   counts=lambda:tuple(self.value('SELECT COUNT(*) FROM '+t)for t in ('AiFavoredItems','District_Adjacencies','ImprovementModifiers','TraitModifiers','TreeData'))
   before=counts();self.apply(True,rh);self.assertEqual(before,counts())

class Policy(unittest.TestCase):
 def setUp(self):
  self.lua=LuaRuntime(unpack_returned_tuples=True);self.lua.execute((AI/'CSC_AI_OpportunityPolicy.lua').read_text());self.p=self.lua.globals().CSC_AI_OpportunityPolicy
 def test_own_first_and_only_shortfall(self):
  f=self.p.Funding(40,50,10,0,True,0);self.assertEqual((f.own,f.grant,f.reserve),(20,20,25))
  rich=self.p.Funding(40,1000,10,0,True,0);self.assertEqual((rich.own,rich.grant),(40,0))
 def test_no_subsidy_no_unaffordable_action(self):self.assertIsNone(self.p.Funding(40,50,10,0,False,0))
 def test_upkeep_deficit_reserve_not_clipped(self):
  f=self.p.Funding(40,3,0,30,True,0);self.assertEqual((f.reserve,f.own,f.grant),(300,0,40))
 def test_caps_unknown_and_fractional_quotes(self):
  for price,spent in ((40,280),(0,0),(None,0),(1.5,0)):self.assertIsNone(self.p.Funding(price,1000,10,0,True,spent))
 def test_defaults_and_numeric_boolean(self):
  self.assertTrue(self.p.Enabled(None,True));self.assertFalse(self.p.Enabled(0,True));self.assertTrue(self.p.Enabled('1',False))
 def route(self,nodes,required):return self.p.Route(self.lua.table_from(nodes,recursive=True),self.lua.table_from(required))
 def test_stepwise_unknown_future_price_and_connector(self):
  r=self.route({0:dict(owner=7,neighbors=[1]),1:dict(owner=-1,neighbors=[0,2],reach=True,price=20),2:dict(owner=-1,neighbors=[1,3],reach=False,price=0),3:dict(owner=-1,neighbors=[2],reach=False,price=0)},[2,3])
  self.assertEqual(list(r.values()),[1,2,3])
 def test_no_first_step_quote_or_native_reach(self):
  self.assertIsNone(self.route({0:dict(owner=7,neighbors=[1]),1:dict(owner=-1,neighbors=[0],reach=False,price=20)},[1]))
 def test_connector_cap(self):
  n={0:dict(owner=7,neighbors=[1])}
  for i in range(1,5):n[i]=dict(owner=-1,neighbors=[i-1]+([i+1]if i<4 else[]),reach=i==1,price=20)
  self.assertIsNone(self.route(n,[4]))

FIXTURE=r'''
mode='BASIC';subsidy=true;wallet=50;turn=200;human=false;network=false;hotseat=false;lag=false;assignmentFails=false;badQueue=false
properties={};goldChanges={};assignments=0;creations=0;placed=false
local function iter(rows)return function()local i=0;return function()i=i+1;return rows[i]end end end
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=3,Hash=301}},Resources={[5]={Index=5},[6]={Index=6}}}
GameInfo.CSC_AI_Profile=function()return iter({{Id='ACTIVE',Mode=mode}})()end
GameInfo.TypeTags=iter({{Type=5,Tag='CLASS_CSC_BAKERS_BASE'},{Type=6,Tag='CLASS_CSC_BAKERS_SPEC'}})
Game={GetCurrentGameTurn=function()return turn end};function Game:GetProperty(k)return properties[k]end;function Game:SetProperty(k,v)properties[k]=v end
GameConfiguration={GetValue=function()return subsidy end,IsAnyMultiplayer=function()return network end,IsHotseat=function()return hotseat end}
CSC_Adjacency={ResourceVisible=function()return true end}
treasury={GetGoldBalance=function()return wallet end,GetGoldYield=function()return 10 end,GetTotalMaintenance=function()return 0 end}
function treasury:ChangeGoldBalance(v)wallet=wallet+v;goldChanges[#goldChanges+1]=v end
player={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return human end,GetTreasury=function()return treasury end,GetID=function()return 7 end}
Players={[7]=player};PlayerManager={GetAliveMajors=function()return {player}end}
plots={}
for i=0,3 do local p={idx=i,owner=i==0 or i==2 and 7 or -1,res=i==1 and 5 or i==2 and 6 or -1,x=i%2,y=math.floor(i/2)}
 if i==0 then p.owner=7 end
 function p:GetOwner()return self.owner end;function p:GetResourceType()return self.res end
 function p:GetDistrictType()return -1 end;function p:GetImprovementType()return -1 end;function p:GetFeatureType()return -1 end
 function p:GetX()return self.x end;function p:GetY()return self.y end;function p:GetIndex()return self.idx end
 plots[i]=p
end
Map={GetPlotByIndex=function(i)return plots[i]end,GetPlotDistance=function(x,y,a,b)return math.abs(x-a)+math.abs(y-b)end}
PlayersVisibility={[7]={IsRevealed=function()return true end}}
districts={HasDistrict=function()return placed end,GetDistrictAtLocation=function()if placed then return {GetType=function()return 3 end,IsComplete=function()return false end}end end}
queue={CreateIncompleteDistrict=function(self,index,source,percentage)assert(index==3 and source==3 and percentage==0);creations=creations+1;placed=true end}
city={GetOwner=function()return 7 end,GetID=function()return 11 end,GetDistricts=function()return districts end,GetBuildQueue=function()return queue end,GetPopulation=function()return 3 end,GetX=function()return 0 end,GetY=function()return 0 end}
CityManager={GetCity=function(pid,cid)assert(pid==7 and cid==11);return city end}
ExposedMembers={CSC_AI_AssistanceUI={}}
function ExposedMembers.CSC_AI_AssistanceUI.SupportsEconomics()return not(network or hotseat or multiplayer)end
function ExposedMembers.CSC_AI_AssistanceUI.InitialHumanPlayers()return {['0']=true}end
function ExposedMembers.CSC_AI_AssistanceUI.HasCity(pid,cid)return uiReady~=false end
function ExposedMembers.CSC_AI_AssistanceUI.IsAIPlayer(pid)local configured=PlayerConfigurations and PlayerConfigurations[pid];return not human and not(configured and configured.IsHuman and configured:IsHuman())end

function ExposedMembers.CSC_AI_AssistanceUI.Read(pid,cid,key,source,index,exact)
 return {turn=turn,owner=plots[index].owner,city=plots[index].owner==7 and 11 or -1,price=40,gold=wallet,reach=true,revealed=true,in_range=true,potential=true,can_produce=true,same_type=false,legal=true,placed=placed,progress=0,cost=45,queue={size=1,hash=badQueue and placed and 99 or 9,items={{Hash=9}}}}
end
function ExposedMembers.CSC_AI_AssistanceUI.Owner(index)if lag then return -1,-1,-1 end;return plots[index].owner,7,11 end
WorldBuilder={CityManager=function()return {SetPlotOwner=function(self,x,y,pid,cid)assignments=assignments+1;if assignmentFails then error('assignment rejected')end;plots[y*2+x].owner=pid end}end}
Events={PlayerTurnActivated={Add=function(fn)turnHandler=fn end}}
candidate={player=7,city=11,quarter='BAKERS',source=3,materials={1,2},base=1,spec=1,missing=2}
include=function()end;print=function()end
'''
class Transactions(unittest.TestCase):
 def fixture(self,extra=''):
  l=LuaRuntime(unpack_returned_tuples=True);l.execute(FIXTURE);l.execute(extra)
  l.execute((AI/'CSC_AI_OpportunityPolicy.lua').read_text());l.execute((AI/'CSC_AI_Assistance.lua').read_text());return l
 def acquire(self,l):return l.eval('CSC_AI_Assistance.Acquire(candidate,1,{1,3})')
 def test_AI_player_outside_test_roster_and_exact_shortfall(self):
  l=self.fixture();self.assertTrue(self.acquire(l));g=l.globals()
  self.assertEqual(g.wallet,30);self.assertEqual(g.plots[1].owner,7);self.assertEqual(list(g.goldChanges.values()),[20,-40])
 def test_rich_AI_no_grant(self):
  l=self.fixture('wallet=1000');self.acquire(l);self.assertEqual(list(l.globals().goldChanges.values()),[-40])
 def test_subsidies_off_stops_before_any_effect(self):
  l=self.fixture('subsidy=false');self.assertFalse(self.acquire(l));self.assertEqual(l.globals().wallet,50);self.assertEqual(l.globals().assignments,0)
 def test_human_guard_before_grant(self):
  l=self.fixture('human=true');ok,_=l.eval('pcall(function()CSC_AI_Assistance.Acquire(candidate,1,{1,3})end)');self.assertFalse(ok);self.assertEqual(l.globals().wallet,50)
 def test_configured_human_still_excluded_during_autoplay(self):
  l=self.fixture('PlayerConfigurations={[7]={IsHuman=function()return true end}}')
  ok,_=l.eval('pcall(function()CSC_AI_Assistance.Acquire(candidate,1,{1,3})end)');self.assertFalse(ok);self.assertEqual(l.globals().wallet,50)
 def test_off_guard_before_grant(self):
  l=self.fixture("mode='OFF'");ok,_=l.eval('pcall(function()CSC_AI_Assistance.Acquire(candidate,1,{1,3})end)');self.assertFalse(ok);self.assertEqual(l.globals().assignments,0)
 def test_assignment_failure_never_repeats_grant_or_assignment(self):
  l=self.fixture('assignmentFails=true');ok,_=l.eval('pcall(function()CSC_AI_Assistance.Acquire(candidate,1,{1,3})end)');self.assertFalse(ok)
  self.assertFalse(self.acquire(l));self.assertEqual(l.globals().wallet,70);self.assertEqual(l.globals().assignments,1)
 def test_UI_lag_reconciles_debit_only_once(self):
  l=self.fixture('lag=true');self.acquire(l);self.assertEqual(l.globals().wallet,70)
  l.execute('lag=false;CSC_AI_Assistance.Reconcile();CSC_AI_Assistance.Reconcile()')
  self.assertEqual(l.globals().wallet,30);self.assertEqual(l.globals().assignments,1)
  totals=l.globals().properties['CSC_AI_ASSISTANCE_V1_TOTALS'];self.assertEqual((totals.tiles,totals.cost,totals.own,totals.subsidy),(1,40,20,20))
 def test_same_city_same_turn_cannot_buy_twice(self):
  l=self.fixture('wallet=1000');self.acquire(l);self.assertFalse(self.acquire(l));self.assertEqual(l.globals().assignments,1)
 def test_later_turn_wallet_not_debited_by_pending_reconciliation(self):
  l=self.fixture('lag=true');self.acquire(l);l.execute('lag=false;turn=201;CSC_AI_Assistance.Reconcile()');self.assertEqual(l.globals().wallet,70)
 def test_zero_foundation_preserves_queue_cost_and_progress(self):
  l=self.fixture('plots[1].owner=7;plots[3].owner=7');self.assertTrue(l.eval('CSC_AI_Assistance.Place(candidate)'));self.assertEqual(l.globals().creations,1)
  self.assertEqual(l.globals().properties['CSC_AI_ASSISTANCE_V1_TOTALS'].foundations,1)
 def test_ambiguous_foundation_not_recreated(self):
  l=self.fixture('plots[1].owner=7;plots[3].owner=7;badQueue=true')
  ok,_=l.eval('pcall(function()CSC_AI_Assistance.Place(candidate)end)');self.assertFalse(ok)
  self.assertFalse(l.eval('CSC_AI_Assistance.Place(candidate)'));self.assertEqual(l.globals().creations,1)
 def test_network_callbacks_do_not_run_assistance(self):
  l=self.fixture('network=true');l.execute('turnHandler(7);CSC_AI_Assistance.Reconcile()');self.assertEqual(l.globals().assignments,0)
 def test_Gameplay_has_no_hotseat_getter_and_still_uses_UI_guard(self):
  l=self.fixture('GameConfiguration.IsHotseat=nil')
  self.assertTrue(self.acquire(l));self.assertEqual(l.globals().assignments,1)
 def test_direct_economic_calls_reject_multiplayer(self):
  l=self.fixture('multiplayer=true');self.assertFalse(self.acquire(l));self.assertEqual(l.globals().assignments,0)
 def test_original_human_remains_excluded_when_autoplay_flips_flags(self):
  l=self.fixture('Players[0]=player')
  l.execute('turnHandler(0)')
  self.assertIsNone(l.eval("properties['CSC_AI_ASSISTANCE_V1_TURN_0']"));self.assertEqual(l.globals().assignments,0)
 def test_UI_city_lag_defers_without_consuming_a_cycle_or_throwing(self):
  l=self.fixture("uiReady=false;player.GetCities=function()return {Members=function()return ipairs({city})end}end")
  l.execute('turnHandler(7)')
  self.assertIsNone(l.eval("properties['CSC_AI_ASSISTANCE_V1_TURN_7']"));self.assertEqual(l.eval('CSC_AI_Assistance.queued[7]'),l.eval('Game.GetCurrentGameTurn()'))
  self.assertEqual(l.globals().assignments,0)
 def test_two_normal_turn_callbacks_buy_then_place_once(self):
  l=self.fixture('''wallet=1000
   player.GetCities=function()return {Members=function()return ipairs({city})end}end
   Map.GetPlotCount=function()return 4 end
   Map.GetAdjacentPlot=function(x,y,direction)local idx=y*2+x;local adj=idx==0 and {1,2}or idx==1 and {0,3}or idx==2 and {0,3}or {1,2};return plots[adj[direction+1]]end
   queue.CreateIncompleteDistrict=function(self,index,source,percentage)assert(index==3 and percentage==0);creations=creations+1;placed=true end
  ''')
  l.execute('turnHandler(7);turnHandler(7)')
  self.assertEqual(l.globals().assignments,1);self.assertEqual(l.globals().creations,0)
  l.execute('turn=201;turnHandler(7);turnHandler(7)')
  self.assertEqual(l.globals().creations,1)

class NativeUIBindings(unittest.TestCase):
 def fixture(self):
  l=LuaRuntime(unpack_returned_tuples=True);l.execute(FIXTURE)
  l.execute('''
   CityCommandTypes={PARAM_PLOT_PURCHASE=11,PURCHASE=10};CityCommandResults={PLOTS='plots'}
   CityOperationTypes={PARAM_DISTRICT_TYPE=21,PARAM_X=22,PARAM_Y=23,BUILD=20};CityOperationResults={PLOTS='plots'}
   CityManager.CanStartCommand=function()return true,{plots={1,3}}end
   CityManager.GetOperationTargets=function(c,op,args)assert(args[21]==301 and args[22]==nil and args[23]==nil);return {plots={3}}end
   CityManager.CanStartOperation=function()return true end
   Cities={GetPlotPurchaseCity=function(p)if p.owner==7 then return city end end}
   for _,p in pairs(plots)do p.CanHaveDistrict=function()return true end end
   queue.CanProduce=function()return true,{reason='native reason table'}end
   queue.HasBeenPlaced=function()return false end;queue.GetDistrictProgress=function()return 0 end;queue.GetDistrictCost=function()return 45 end
   queue.GetSize=function()return 1 end;queue.GetAt=function()return {Hash=9}end;queue.GetCurrentProductionTypeHash=function()return 9 end
   city.GetGold=function()return {GetPlotPurchaseCost=function()return 40 end}end
  ''')
  l.execute((AI/'CSC_AI_AssistanceUI.lua').read_text())
  return l
 def test_typed_canproduce_reason_and_district_only_target_enumeration(self):
  l=self.fixture()
  q=l.eval("ExposedMembers.CSC_AI_AssistanceUI.Read(7,11,'BAKERS',3,3,true)")
  self.assertTrue(q.can_produce);self.assertTrue(q.legal);self.assertEqual(q.cost,45)
 def test_callback_cache_keeps_prices_wallet_fresh_and_invalidates(self):
  l=self.fixture();l.execute('''queries=0;local old=CityManager.CanStartCommand;CityManager.CanStartCommand=function(...)queries=queries+1;return old(...)end
   local u=ExposedMembers.CSC_AI_AssistanceUI;u.BeginScope();u.Read(7,11,'BAKERS',3,1,false)
   wallet=123;second=u.Read(7,11,'BAKERS',3,3,false);firstCount=queries
   u.Invalidate();u.Read(7,11,'BAKERS',3,3,false);afterInvalidate=queries
   u.EndScope();u.Read(7,11,'BAKERS',3,3,false)
  ''')
  self.assertEqual(l.globals().firstCount,1);self.assertEqual(l.globals().second.gold,123)
  self.assertEqual(l.globals().afterInvalidate,2);self.assertEqual(l.globals().queries,3)
 def test_exact_preflight_bypasses_cached_placement_state(self):
  l=self.fixture();l.execute('''local u=ExposedMembers.CSC_AI_AssistanceUI;u.BeginScope();u.Read(7,11,'BAKERS',3,1,false)
   queue.HasBeenPlaced=function()return true end;fresh=u.Read(7,11,'BAKERS',3,3,true)
  ''');self.assertTrue(l.globals().fresh.placed);self.assertTrue(l.globals().fresh.same_type)

if __name__=='__main__':unittest.main()

