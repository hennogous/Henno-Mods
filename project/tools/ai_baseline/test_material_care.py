"""Actual Lua5.1 material-care guards; no native client or game mutations."""
import sys,unittest
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
Map={GetPlotCount=function()return 9 end,GetPlotByIndex=function(i)return plots[i]end,GetPlot=function(x,y)return plots[x]end,GetAdjacentPlot=function(x,y,dir)if dir<2 then return plots[dir+1]end end};
local q={};function q:GetType()return 10 end;function q:GetX()return 0 end;function q:GetY()return 0 end;
districts={q};units={};human=false;unlocked=true;legal=true;revealed=true;resourceVisible=true;
local city={};function city:GetDistricts()return {Members=function()return ipairs(districts)end}end;
local p={};function p:GetID()return 1 end;function p:IsAlive()return true end;function p:IsMajor()return true end;function p:IsHuman()return human end;
function p:GetCities()return {Members=function()return ipairs({city})end}end;
function p:GetUnits()return {Members=function()return ipairs(units)end}end;
function p:GetTechs()return {HasTech=function()return unlocked end}end;
function p:GetCulture()return {HasCivic=function()return unlocked end}end;
Players={[1]=p};PlayersVisibility={[1]={IsRevealed=function()return revealed end}};
PlayerManager={GetAliveMajors=function()return {p}end};CSC_Adjacency={ResourceVisible=function()return resourceVisible end};
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=10}},TypeTags=info({{Tag='CLASS_CSC_BAKERS_BASE',Type='WHEAT'},{Tag='CLASS_CSC_BAKERS_SPEC',Type='HONEY'}}),Resources={WHEAT={Index=1,ResourceType='WHEAT'},HONEY={Index=2,ResourceType='HONEY'},[1]={Index=1,ResourceType='WHEAT'},[2]={Index=2,ResourceType='HONEY'}},Improvements={FARM={Index=1,PrereqTech='TECH'}},Improvement_ValidResources=info({{ResourceType='WHEAT',ImprovementType='FARM'},{ResourceType='HONEY',ImprovementType='FARM'}}),Technologies={TECH={Index=1}},Civics={},Units={UNIT_BUILDER={Index=1}}};
ImprovementBuilder={CanHaveImprovement=function()return legal end};
function builder(charges)local u={};function u:GetType()return 1 end;function u:GetBuildCharges()return charges end;units[#units+1]=u end
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
if __name__=='__main__':unittest.main()
