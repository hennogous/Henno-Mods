"""Actual Lua5.1 material-care guards; no native client or game mutations."""
import sys,unittest,sqlite3
from pathlib import Path
from lupa.lua51 import LuaRuntime
ROOT=Path(__file__).resolve().parents[3]
LUA=ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_MaterialCare.lua'
FIXTURE=r'''
function include()end
function iter(t)local i=0;return function()i=i+1;return t[i]end end
function info(t)return setmetatable(t,{__call=function()return iter(t)end})end
Events=setmetatable({},{__index=function(t,k)local e={callbacks={}};e.Add=function(f)table.insert(e.callbacks,f)end;e.Fire=function(...)for _,f in ipairs(e.callbacks)do f(...)end end;t[k]=e;return e end})
GameEvents=Events;turn=10;Game={GetCurrentGameTurn=function()return turn end};
plots={};for i=0,8 do local p={index=i,owner=1,resource=-1,district=-1,improvement=-1,pillaged=false,properties={}};plots[i]=p;
 function p:GetIndex()return self.index end;function p:GetX()return self.index end;function p:GetY()return 0 end;
 function p:GetOwner()return self.owner end;function p:GetResourceType()return self.resource end;function p:GetDistrictType()return self.district end;
 function p:GetImprovementType()return self.improvement end;function p:IsImprovementPillaged()return self.pillaged end;
 function p:GetProperty(k)return self.properties[k]end;function p:SetProperty(k,v)self.properties[k]=v end;
 function p:IsWater()return false end;function p:IsImpassable()return false end;
end
plots[1].resource=1;plots[2].resource=2;plots[0].district=10;
Map={GetPlotCount=function()return 9 end,GetPlotByIndex=function(i)return plots[i]end,GetPlot=function(x,y)return plots[x]end,GetPlotDistance=function(x,y,a,b)return math.abs(x-a)end,GetAdjacentPlot=function(x,y,dir)if dir<2 then return plots[dir+1]end end};
local q={};function q:GetType()return 10 end;function q:GetX()return 0 end;function q:GetY()return 0 end;
districts={q};units={};human=false;unlocked=true;legal=true;revealed=true;resourceVisible=true;
local city={};function city:GetID()return 101 end;function city:GetDistricts()return {GetNumDistricts=function()return #districts end,GetDistrictByIndex=function(_,i)return districts[i+1]end}end;
local p={};function p:GetID()return 1 end;function p:IsAlive()return true end;function p:IsMajor()return true end;function p:IsHuman()return human end;
function p:GetCities()return {Members=function()return ipairs({city})end}end;
function p:GetUnits()return {Members=function()return ipairs(units)end}end;
function p:GetTechs()return {HasTech=function()return unlocked end}end;
function p:GetCulture()return {HasCivic=function()return unlocked end}end;
Players={[1]=p};PlayersVisibility={[1]={IsRevealed=function()return revealed end}};
PlayerManager={GetAliveMajors=function()return {p}end};CSC_Adjacency={ResourceVisible=function()return resourceVisible end};
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=10}},TypeTags=info({{Tag='CLASS_CSC_BAKERS_BASE',Type='WHEAT'},{Tag='CLASS_CSC_BAKERS_SPEC',Type='HONEY'}}),Resources={WHEAT={Index=1,ResourceType='WHEAT'},HONEY={Index=2,ResourceType='HONEY'},[1]={Index=1,ResourceType='WHEAT'},[2]={Index=2,ResourceType='HONEY'}},Improvements={FARM={Index=1,PrereqTech='TECH'}},Improvement_ValidResources=info({{ResourceType='WHEAT',ImprovementType='FARM'},{ResourceType='HONEY',ImprovementType='FARM'}}),Technologies={TECH={Index=1}},Civics={},Units={UNIT_BUILDER={Index=1}}};
ImprovementBuilder={CanHaveImprovement=function()return legal end};
function builder(charges,x)local u={};function u:GetType()return 1 end;function u:GetBuildCharges()return charges end;function u:GetX()return x or 0 end;function u:GetY()return 0 end;units[#units+1]=u end
'''
class MaterialCareTests(unittest.TestCase):
 def setUp(self):
  self.l=LuaRuntime(unpack_returned_tuples=True);self.l.execute(FIXTURE);self.l.execute(LUA.read_text(encoding='utf-8-sig'))
 def runlua(self,code):return self.l.execute(code)
 def test_last_supplies_and_native_demand(self):self.runlua("local r=CSC_AI_MaterialCare.Refresh(1);assert(r.missing==2 and r.shortage);assert(plots[1]:GetProperty('CSC_AI_CARE_LAST_BASE')==1);assert(plots[2]:GetProperty('CSC_AI_CARE_LAST_SPEC')==1)")
 def test_existing_capacity_prevents_extra_builder_demand(self):self.runlua('builder(3);local r=CSC_AI_MaterialCare.Refresh(1);assert(r.charges==3 and not r.shortage)')
 def test_pillage_is_repair_not_working(self):self.runlua('plots[1].improvement=1;plots[1].pillaged=true;local r=CSC_AI_MaterialCare.Refresh(1);assert(r.repairs==1 and r.working==0)')
 def test_repair_with_zero_charge_builder_does_not_need_new_unit(self):self.runlua('builder(0);plots[1].improvement=1;plots[1].pillaged=true;plots[2].improvement=1;local r=CSC_AI_MaterialCare.Refresh(1);assert(r.repairs==1 and not r.shortage)')
 def test_repair_restores_working_count(self):self.runlua('plots[1].improvement=1;plots[1].pillaged=true;CSC_AI_MaterialCare.Refresh(1);plots[1].pillaged=false;local r=CSC_AI_MaterialCare.Refresh(1);assert(r.repairs==0 and r.working==1)')
 def test_replaced_resource_clears_signal(self):self.runlua("CSC_AI_MaterialCare.Refresh(1);plots[1].resource=-1;plots[1].district=5;local r=CSC_AI_MaterialCare.Refresh(1);assert(plots[1]:GetProperty('CSC_AI_CARE_LAST_BASE')==0 and #r.lost==1)")
 def test_foreign_resource_excluded(self):self.runlua('plots[1].owner=2;local r=CSC_AI_MaterialCare.Refresh(1);assert(#r.plots==1)')
 def test_human_excluded(self):self.runlua('human=true;local r=CSC_AI_MaterialCare.Refresh(1);assert(#r.plots==0 and not r.shortage)')
 def test_locked_or_illegal_is_not_actionable_demand(self):self.runlua("legal=false;local r=CSC_AI_MaterialCare.Refresh(1);assert(r.missing==0 and not r.shortage);unlocked=false;r=CSC_AI_MaterialCare.Refresh(1);assert(r.missing==0)")
 def test_hidden_resources_excluded(self):self.runlua('resourceVisible=false;local r=CSC_AI_MaterialCare.Refresh(1);assert(#r.plots==0)')
 def test_duplicate_quarters_do_not_stack_plot_signals(self):self.runlua("districts[2]=districts[1];local r=CSC_AI_MaterialCare.Refresh(1);assert(#r.plots==2 and #r.plots[1].links==2 and r.plots[1].rank==3)")
 def test_redundant_base_uses_lower_priority(self):self.runlua("plots[2].resource=1;local r=CSC_AI_MaterialCare.Refresh(1);assert(r.plots[1].rank==1 and plots[1]:GetProperty('CSC_AI_CARE_REDUNDANT')==1)")
 def test_unknown_legality_does_not_trigger_demand(self):self.runlua("ImprovementBuilder=nil;local r=CSC_AI_MaterialCare.Refresh(1);assert(r.missing==0 and not r.shortage and r.plots[1].state=='legality_unknown')")
 def test_observed_work_transitions_retained(self):self.runlua("CSC_AI_MaterialCare.Refresh(1);plots[1].improvement=1;CSC_AI_MaterialCare.Refresh(1);local e=CSC_AI_MaterialCare.events;assert(#e==3 and e[3].previous=='develop' and e[3].state=='working')")
 def test_no_active_mutation_backend(self):
  text=LUA.read_text();self.assertNotIn('RequestOperation(',text);self.assertNotIn('SetResourceType(',text);self.assertNotIn('ChangeGoldBalance(',text)
 def test_sustained_work_can_activate_despite_large_empire_capacity(self):
  self.runlua('builder(100,8);CSC_AI_MaterialCare.Refresh(1);turn=13;local r=CSC_AI_MaterialCare.Refresh(1);assert(not r.shortage and r.work_urgent and r.urgent_jobs==1)')
 def test_repeated_same_turn_callbacks_do_not_age_job(self):
  self.runlua('for i=1,20 do local r=CSC_AI_MaterialCare.Refresh(1);assert(not r.work_urgent and r.plots[1].ready_age==0)end')
 def test_last_base_repair_escalates_before_noncritical_work(self):
  self.runlua('plots[1].improvement=1;plots[1].pillaged=true;CSC_AI_MaterialCare.Refresh(1);turn=11;local r=CSC_AI_MaterialCare.Refresh(1);assert(r.plots[1].urgent and not r.plots[2].urgent)')
 def test_worked_tile_clears_urgency(self):
  self.runlua('CSC_AI_MaterialCare.Refresh(1);turn=18;local r=CSC_AI_MaterialCare.Refresh(1);assert(r.work_urgent);plots[1].improvement=1;plots[2].improvement=1;r=CSC_AI_MaterialCare.Refresh(1);assert(not r.work_urgent)')
 def test_unsafe_interval_does_not_count_as_safe_wait(self):
  self.runlua("CSC_AI_MaterialCare.Refresh(1);local prior=CSC_AI_MaterialCare.players[1];prior.plots[1].state='unsafe';turn=20;local r=CSC_AI_MaterialCare.Refresh(1);assert(r.plots[1].ready_age==0 and not r.plots[1].urgent)")
 def test_remote_builders_are_not_nearby_capacity(self):
  self.runlua('builder(100,8);local r=CSC_AI_MaterialCare.Refresh(1);assert(r.charges==100 and r.plots[1].nearby_builders==0 and r.plots[2].nearby_builders==1)')
 def test_nonactionable_work_never_escalates(self):
  self.runlua('legal=false;CSC_AI_MaterialCare.Refresh(1);turn=100;local r=CSC_AI_MaterialCare.Refresh(1);assert(not r.work_urgent)')
 def test_strategy_records_actual_true_and_false_evaluations(self):
  self.runlua('Events.CSC_AI_MaterialWorkReady.Fire(1);turn=13;Events.CSC_AI_MaterialWorkReady.Fire(1);assert(CSC_AI_MaterialCare.calls==2 and CSC_AI_MaterialCare.strategy.active_calls==1 and CSC_AI_MaterialCare.strategy.inactive_calls==1 and #CSC_AI_MaterialCare.strategy.transitions==2)')
class MaterialCareSQLTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  schemas={
   'Requirements':'RequirementId TEXT PRIMARY KEY,RequirementType TEXT,Inverse INT DEFAULT 0',
   'RequirementArguments':'RequirementId TEXT,Name TEXT,Value,PRIMARY KEY(RequirementId,Name)',
   'RequirementSets':'RequirementSetId TEXT PRIMARY KEY,RequirementSetType TEXT',
   'RequirementSetRequirements':'RequirementSetId TEXT,RequirementId TEXT,PRIMARY KEY(RequirementSetId,RequirementId)',
   'Modifiers':'ModifierId TEXT PRIMARY KEY,ModifierType TEXT,OwnerRequirementSetId TEXT,SubjectRequirementSetId TEXT',
   'ModifierArguments':'ModifierId TEXT,Name TEXT,Value,PRIMARY KEY(ModifierId,Name)',
   'TraitModifiers':'TraitType TEXT,ModifierId TEXT,PRIMARY KEY(TraitType,ModifierId)',
   'Types':'Type TEXT PRIMARY KEY,Kind TEXT',
   'Strategies':'StrategyType TEXT PRIMARY KEY,VictoryType TEXT,NumConditionsNeeded INT',
   'StrategyConditions':'StrategyType TEXT,ConditionFunction TEXT,StringValue TEXT,ThresholdValue INT,Disqualifier INT',
   'AiListTypes':'ListType TEXT PRIMARY KEY',
   'AiLists':'ListType TEXT,System TEXT',
   'AiFavoredItems':'ListType TEXT,Item TEXT,Favored INT,Value INT',
   'Strategy_Priorities':'StrategyType TEXT,ListType TEXT',
   'TreeData':'DefnId INT,NodeId INT,TreeName TEXT,DefaultData TEXT',
   'Resources':'ResourceType TEXT PRIMARY KEY',
   'TypeTags':'Type TEXT,Tag TEXT'}
  for table,cols in schemas.items():self.db.execute('CREATE TABLE '+table+'('+cols+')')
  self.db.executemany('INSERT INTO Resources VALUES(?)',[('WHEAT',),('HONEY',),('IRON',)])
  self.db.executemany('INSERT INTO TypeTags VALUES(?,?)',[('WHEAT','CLASS_CSC_BAKERS_BASE'),('HONEY','CLASS_CSC_BAKERS_SPEC'),('WHEAT','CLASS_CSC_TAILORS_BASE'),('IRON','CLASS_OTHER')])
  self.sql=(ROOT/'Civ Supply Chains/Data/CSC_AI_MaterialCare.sql').read_text()
 def test_native_guard_sets_map_only_materials_and_replay_once(self):
  for _ in range(2):self.db.executescript(self.sql)
  rows=self.db.execute("SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId='REQSET_CSC_AI_CARE_RESOURCE' ORDER BY 1").fetchall()
  self.assertEqual(rows,[('REQ_CSC_AI_CARE_RESOURCE_HONEY',),('REQ_CSC_AI_CARE_RESOURCE_WHEAT',)])
  for name in ('LAST_BASE','LAST_SPEC','REDUNDANT'):
   rows=self.db.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?',('REQSET_CSC_AI_CARE_'+name,)).fetchall()
   self.assertEqual({x[0] for x in rows},{'REQ_CSC_AI_CARE_'+name,'REQ_CSC_AI_CARE_NO_DISTRICT','REQ_CSC_AI_CARE_RESOURCE_PRESENT'})
  self.assertEqual(self.db.execute("SELECT RequirementType,Inverse FROM Requirements WHERE RequirementId='REQ_CSC_AI_CARE_NO_DISTRICT'").fetchone(),('REQUIREMENT_PLOT_HAS_ANY_DISTRICT',1))
 def test_replay_retires_capacity_gate_and_extra_builder_production(self):
  self.db.execute("INSERT INTO StrategyConditions VALUES('STRATEGY_CSC_AI_MATERIAL_BACKLOG','Call Lua Function','CSC_AI_MaterialCareShortage',1,NULL)")
  self.db.execute("INSERT INTO Strategy_Priorities VALUES('STRATEGY_CSC_AI_MATERIAL_BACKLOG','CSC_AI_MATERIAL_BACKLOG_UNITS')")
  self.db.execute("INSERT INTO AiFavoredItems VALUES('CSC_AI_MATERIAL_BACKLOG_UNITS','UNIT_BUILDER',1,100)")
  for _ in range(2):self.db.executescript(self.sql)
  self.assertEqual(self.db.execute("SELECT StringValue FROM StrategyConditions WHERE ConditionFunction='Call Lua Function'").fetchall(),[('CSC_AI_MaterialWorkReady',)])
  self.assertEqual(self.db.execute("SELECT ListType FROM Strategy_Priorities").fetchall(),[('CSC_AI_MATERIAL_BACKLOG_PSEUDOS',)])
  self.assertEqual(self.db.execute("SELECT Item,Value FROM AiFavoredItems").fetchall(),[('PSEUDOYIELD_IMPROVEMENT',100)])

if __name__=='__main__':unittest.main()
