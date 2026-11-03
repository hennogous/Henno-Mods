"""Native-style UI Members contract; fixtures are not native game evidence."""
import json
import unittest
from unittest.mock import patch, Mock
from pathlib import Path
from lupa.lua51 import LuaRuntime
from native_shadow_probe import preserve_candidate_stage, capture_raw
from full_game_controller.transport import NativeLuaFailure
from shadow_geometry import review

FIXTURE = r'''
function rows(items)
 local t={};for _,v in ipairs(items)do if v.Index then t[v.Index]=v end
  for _,k in ipairs({'DistrictType','BuildingType','ResourceType','ImprovementType','YieldType'})do if v[k]then t[v[k]]=v end end end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return items[i]end end})
end
function collection(items)return{Members=function()local i=0;return function()i=i+1;if items[i]then return i,items[i]end end end}end
Game={GetCurrentGameTurn=function()return 110 end}
GameInfo={Districts=rows({{Index=0,DistrictType='DISTRICT_CITY_CENTER'},{Index=23,DistrictType='DISTRICT_GOVERNMENT'},
 {Index=36,Hash=36,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'},{Index=37,Hash=37,DistrictType='DISTRICT_CSC_TAILORS_QUARTER'}}),
 Buildings=rows({{Index=99,BuildingType='BUILDING_GOV_FAITH'}}),Resources=rows({{Index=1,ResourceType='RESOURCE_WHEAT'}}),
 Improvements=rows({{Index=1,ImprovementType='IMPROVEMENT_FARM'}}),Yields=rows({{Index=1,YieldType='YIELD_PRODUCTION'},{Index=2,YieldType='YIELD_GOLD'}}),
 TypeTags=rows({{Type='RESOURCE_WHEAT',Tag='CLASS_CSC_BAKERS_BASE'}}),
 Improvement_ValidResources=rows({{ResourceType='RESOURCE_WHEAT',ImprovementType='IMPROVEMENT_FARM'}}),
 Requirements=rows({}),RequirementArguments=rows({}),RequirementSets=rows({}),RequirementSetRequirements=rows({})}
local q={GetSize=function()return 1 end,GetCurrentProductionTypeHash=function()return 99 end,GetAt=function()return{type=99}end,
 CanProduce=function()return true end,HasBeenPlaced=function()return false end,GetDistrictCost=function()return 45 end,GetDistrictProgress=function()return 0 end}
local function district(kind,x,y)return{GetType=function()return kind end,GetX=function()return x end,GetY=function()return y end,
 IsComplete=function()return true end,IsPillaged=function()return false end,GetAdjacencyYield=function(self,y)return y==1 and 1 or 0 end,
 GetYield=function(self,y)return y==1 and 3 or 0 end}end
local function city(id,x,y,ds)
 ds.HasDistrict=function(self,k)for _,d in self:Members()do if d:GetType()==k then return true end end;return false end
 return{GetID=function()return id end,GetOwner=function()return 3 end,GetX=function()return x end,GetY=function()return y end,
 GetPopulation=function()return 7 end,GetDistricts=function()return ds end,GetBuildQueue=function()return q end,GetYield=function()return 10 end,
 GetBuildings=function()return{HasBuilding=function()return false end}end}
end
target=city(131073,43,30,collection({district(0,43,30),district(23,43,30)}))
local existing=city(99,10,10,collection({district(36,10,10)}))
local cities=collection({target,existing})
if enrichmentFailure then cities.Members=function()error('fixture enrichment unavailable')end end
local player={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return false end,
 GetCities=function()return cities end,GetTreasury=function()return{GetGoldBalance=function()return 50 end}end}
Players={[3]=player};PlayerConfigurations={[3]={IsHuman=function()return false end}}
PlayersVisibility={[3]={IsRevealed=function()return true end}}
CityManager={GetCity=function()return target end,GetOperationTargets=function()return{plots={1}}end,CanStartOperation=function()return true end}
CityOperationTypes={BUILD='build',PARAM_DISTRICT_TYPE='type',PARAM_X='x',PARAM_Y='y'};CityOperationResults={PLOTS='plots'}
local plots={};local xy={{43,30},{44,30},{45,30},{10,10},{11,10}}
for i,v in ipairs(xy)do local idx=i-1;plots[idx]={GetIndex=function()return idx end,GetX=function()return v[1]end,GetY=function()return v[2]end,
 GetOwner=function()return 3 end,GetResourceType=function()return(idx==2 or idx==4)and 1 or -1 end,
 GetImprovementType=function()return(idx==2 or idx==4)and 1 or -1 end,IsImprovementPillaged=function()return false end,
 GetDistrictType=function()return idx==0 and 0 or idx==3 and 36 or -1 end,GetWorkerCount=function()return 0 end,IsRiver=function()return idx==1 end,
 CanHaveDistrict=function()return true end,GetAdjacencyYield=function(self,pid,cid,d,y)assert(pid==3);return y==1 and 1 or 0 end}
end
Map={GetPlotCount=function()return 5 end,GetPlotByIndex=function(i)return plots[i]end,
 GetPlotDistance=function(x,y,xx,yy)return math.max(math.abs(x-xx),math.abs(y-yy))end,
 GetPlot=function(x,y)for _,p in pairs(plots)do if p:GetX()==x and p:GetY()==y then return p end end end,
 GetAdjacentPlots=function(x,y)if x==44 then return{plots[0],plots[2]}elseif x==10 then return{plots[4]}else return{}end end}
Cities={GetPlotPurchaseCity=function(p)return p:GetIndex()<3 and target or existing end}
CSC_Adjacency={ByDistrict={DISTRICT_CSC_BAKERS_QUARTER={{ID='real',ProvideType='SelfBonus',YieldType='YIELD_PRODUCTION',YieldChange=1,
 AdjacencyType='FROM_RINGS_TYPETAG_RESOURCE',CustomAdjacentObject='CLASS_CSC_BAKERS_BASE'}}},Eligible=function()return true end,
 Count=function()return 1 end,Amount=function(r,n)return r.YieldChange*n end}
'''


class ReaderTests(unittest.TestCase):
    def run_reader(self, fail=False):
        lua=LuaRuntime();captured=[];lua.globals().print=captured.append
        lua.globals().enrichmentFailure=fail;lua.execute(FIXTURE)
        lua.execute(Path(__file__).with_name('native_shadow_reader.lua').read_text(encoding='utf-8'))
        return {s.split('=',1)[0]:json.loads(s.split('=',1)[1])for s in captured}

    def test_ui_members_shape_and_candidate_stage(self):
        stages=self.run_reader();partial=stages['CSC_SHADOW_CANDIDATES'];full=stages['CSC_SHADOW_GEOMETRY']
        self.assertFalse(partial['enrichment_complete']);self.assertTrue(full['enrichment_complete'])
        self.assertEqual(len(full['candidates']),2);self.assertEqual(len(full['controls']),1)
        self.assertTrue(review(full,'synthetic native-style UI')['native_accessor_positive'])
        self.assertIn('city_building_inventory',full['tiles'][0]);self.assertNotIn('buildings',full['tiles'][0])

    def test_optional_enrichment_failure_retains_candidates_but_fails_complete_gate(self):
        stages=self.run_reader(True);full=stages['CSC_SHADOW_GEOMETRY']
        self.assertEqual(len(stages['CSC_SHADOW_CANDIDATES']['candidates']),2)
        self.assertFalse(full['enrichment_complete']);self.assertIn('fixture enrichment',full['enrichment_error'])
        self.assertEqual(review(full,'synthetic')['status'],'partial_geometry_no_extension')

    def test_partial_text_preserved_after_transport_failure(self):
        raw='CSC_SHADOW_CANDIDATES='+json.dumps(dict(action_authorization=False,enrichment_complete=False))+'\nACK false error'
        with patch('native_shadow_probe.write_json')as write:
            controller=Mock();controller.cmd.side_effect=NativeLuaFailure(raw)
            with self.assertRaises(NativeLuaFailure):
                capture_raw(controller,Path(__file__).with_name('native_shadow_reader.lua'),Path('synthetic-output'),'synthetic')
            path,value=write.call_args.args
            self.assertEqual(path,Path('synthetic-output/synthetic-candidate-stage.json'))
            self.assertFalse(value['action_authorization']);self.assertFalse(value['enrichment_complete'])


if __name__=='__main__':unittest.main()
