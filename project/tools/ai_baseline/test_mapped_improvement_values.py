import json,sys,unittest
from pathlib import Path
sys.path.insert(0,'C:/Users/Shadow/Desktop/Codex/csc-adjacencies/test-deps')
from lupa.lua51 import LuaRuntime
class NativeValues(unittest.TestCase):
 def fixture(self,extra=''):
  l=LuaRuntime(unpack_returned_tuples=True);l.execute('''rows={};for i=0,3 do local p={res=-1,value=0,props={},pillaged=false};rows[i]=p;
   function p:GetOwner()return 1 end;function p:GetResourceType()return self.res end;function p:GetImprovementType()return 1 end;function p:GetDistrictType()return -1 end;
   function p:IsImprovementPillaged()return self.pillaged end;function p:GetYield()return self.value end;function p:GetProperty(k)return self.props[k]end;function p:GetX()return 0 end;function p:GetY()return 0 end;end;
   rows[1].res=1;rows[1].value=100;rows[2].res=2;rows[3].res=3;rows[3].value=120;
   local function iter(t)return function()local i=0;return function()i=i+1;return t[i]end end end;
   Game={GetCurrentGameTurn=function()return 25 end};Map={GetPlotCount=function()return 4 end,GetPlotByIndex=function(i)return rows[i]end,GetAdjacentPlot=function()return nil end};
   GameInfo={Yields={YIELD_CSC_AI_PLACEMENT={Index=7}},Districts={},Resources={[1]={ResourceType='RESOURCE_SALT'},[2]={ResourceType='RESOURCE_IRON'},[3]={ResourceType='RESOURCE_MOD_ORE'}},Improvements={[1]={ImprovementType='IMPROVEMENT_MINE'}}};
   GameInfo.RequirementArguments=iter({{RequirementId='salt',Name='ResourceType',Value='RESOURCE_SALT'},{RequirementId='mod',Name='ResourceType',Value='RESOURCE_MOD_ORE'}});
   GameInfo.RequirementSetRequirements=iter({{RequirementSetId='mapped',RequirementId='salt'},{RequirementSetId='mapped',RequirementId='mod'}});
   GameInfo.Modifiers=iter({{ModifierId='MOD_CSC_AI_MAPPED_IMPROVEMENT_IMPROVEMENT_MINE',OwnerRequirementSetId='mapped'}});
   GameInfo.ImprovementModifiers=iter({{ImprovementType='IMPROVEMENT_MINE',ModifierID='MOD_CSC_AI_MAPPED_IMPROVEMENT_IMPROVEMENT_MINE'}});
   GameInfo.Resource_YieldChanges=iter({{ResourceType='RESOURCE_SALT',YieldType='YIELD_CSC_AI_PLACEMENT',YieldChange=20},{ResourceType='RESOURCE_MOD_ORE',YieldType='YIELD_CSC_AI_PLACEMENT',YieldChange=40}});print=function(v)result=v end;''')
  l.execute(extra);l.execute(Path(__file__).with_name('mapped_improvement_values.lua').read_text());return json.loads(l.globals().result.split('=',1)[1])
 def test_resource_and_modded_positive_with_terrain_and_Iron_zero(self):
  v=self.fixture();self.assertEqual((v['eligible_isolated_controls'],v['excluded_isolated_controls'],v['failed_eligible'],v['failed_excluded']),(2,2,0,0))
 def test_missing_resource_incentive_detected(self):self.assertEqual(self.fixture('rows[1].value=20')['failed_eligible'],1)
 def test_terrain_Mine_bonus_detected(self):self.assertEqual(self.fixture('rows[0].value=80')['failed_excluded'],1)
 def test_unrelated_resource_Mine_bonus_detected(self):self.assertEqual(self.fixture('rows[2].value=80')['failed_excluded'],1)
 def test_care_and_pillage_do_not_false_validate(self):
  for extra in('rows[1].props.CSC_AI_CARE_LAST_BASE=1','rows[1].pillaged=true'):
   self.assertEqual(self.fixture(extra)['eligible_isolated_controls'],1)
 def test_modded_resource_not_hardcoded(self):self.assertTrue(self.fixture()['rows'][3]['eligible'])
if __name__=='__main__':unittest.main()
