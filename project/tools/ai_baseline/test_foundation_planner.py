"""Run the real planner in an existing Lua 5.1 runtime; never connect to Civ."""
import argparse
import json
from pathlib import Path
import sys
import unittest


BOOTSTRAP = r'''
function include() end
CSC_Adjacency={ResourceVisible=function(pid,res)return visible end}
Game={GetCurrentGameTurn=function()return 60 end}
visible=true; owner=1; feature=-1; existing={}; placements={}; mutations=0
function rows(values) return setmetatable(values,{__call=function(t)
 local i=0; return function()i=i+1;return t[i]end end}) end
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=36,Hash=360},
 DISTRICT_CSC_TAILORS_QUARTER={Index=37,Hash=370}},Resources={
 [10]={Index=10,ResourceType='WHEAT'},WHEAT={Index=10,ResourceType='WHEAT'},
 [11]={Index=11,ResourceType='SPICES'},SPICES={Index=11,ResourceType='SPICES'}},
 TypeTags=rows({{Tag='CLASS_CSC_BAKERS_BASE',Type='WHEAT'},
 {Tag='CLASS_CSC_BAKERS_SPEC',Type='SPICES'}})}
GameInfo.Districts[36]={DistrictType='DISTRICT_CSC_BAKERS_QUARTER'}
GameInfo.Districts[37]={DistrictType='DISTRICT_CSC_TAILORS_QUARTER'}
function district(kind,complete)return {GetType=function()return kind end,
 IsComplete=function()return complete end}end
queue={CreateIncompleteDistrict=function(self,kind,plot,percentage)
 assert(percentage==0);mutations=mutations+1;placements[plot]=kind end,
 GetDistrictProgress=function()return 0 end,GetDistrictCost=function()return 45 end,
 CurrentlyBuilding=function()return 'UNIT_TRADER'end,GetCurrentProductionTypeHash=function()return 123 end,
 HasBeenPlaced=function()return mutations>0 end,GetSize=function()return 0 end}
districts={HasDistrict=function(self,kind)
 for _,d in ipairs(existing)do if d:GetType()==kind then return true end end
 for _,v in pairs(placements)do if v==kind then return true end end
 return false end,GetNumDistricts=function()return #existing end,
 GetDistrictByIndex=function(self,i)return existing[i+1]end,
 GetDistrictAtLocation=function(self,x,y)
 if placements[x]then return district(placements[x],false)end end}
city={GetDistricts=function()return districts end,GetBuildQueue=function()return queue end,
 GetPopulation=function()return 5 end}
Players={[1]={IsAlive=function()return true end,IsMajor=function()return true end,
 IsHuman=function()return false end,GetCities=function()return {FindID=function()return city end}end}}
plots={};Map={GetPlotByIndex=function(i)return plots[i]end,
 GetAdjacentPlots=function(x,y)return plots[x].neighbors end}
Events={PlayerTurnActivated={Add=function()end},CityProductionCompleted={Add=function()end}}
function candidate(index,base,spec)
 local p={neighbors={},GetIndex=function()return index end,GetX=function()return index end,
 GetY=function()return 0 end,GetOwner=function()return owner end,
 GetDistrictType=function()return placements[index]or -1 end,
 GetResourceType=function()return -1 end,GetImprovementType=function()return -1 end,
 GetFeatureType=function()return feature end}
 for n=1,base+spec do local resource=n<=base and 10 or 11
  p.neighbors[#p.neighbors+1]={GetResourceType=function()return resource end,
   GetOwner=function()return owner end,GetIndex=function()return index*100+n end,
   GetImprovementType=function()return -1 end,IsImprovementPillaged=function()return false end}
 end
 plots[index]=p
 return {player=1,city=1,quarter='BAKERS',plot=index,districtHash=360}
end
'''


class PlannerTests(unittest.TestCase):
    def setUp(self):
        from lupa.lua51 import LuaRuntime
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(BOOTSTRAP)
        self.lua.execute(Path(__file__).with_name('foundation_planner.lua').read_text(encoding='utf-8'))

    def run_lua(self, code):
        self.lua.execute(code)

    def test_unfinished_other_quarter_is_legal(self):
        self.run_lua("existing={district(37,false)};CSC_FOUNDATION_PROBE.Plan({candidate(1,1,0)});assert(#CSC_FOUNDATION_PROBE.plan==1)")

    def test_unfinished_same_quarter_is_rejected(self):
        self.run_lua("existing={district(36,false)};CSC_FOUNDATION_PROBE.Plan({candidate(1,1,0)});assert(#CSC_FOUNDATION_PROBE.plan==0)")

    def test_completed_same_quarter_is_rejected(self):
        self.run_lua("existing={district(36,true)};CSC_FOUNDATION_PROBE.Plan({candidate(1,1,0)});assert(#CSC_FOUNDATION_PROBE.plan==0)")

    def test_base_count_beats_total_material_count(self):
        self.run_lua("CSC_FOUNDATION_PROBE.Plan({candidate(1,1,4),candidate(2,2,1)});assert(CSC_FOUNDATION_PROBE.plan[1].plot==2)")

    def test_both_class_preference_is_retained(self):
        self.run_lua("CSC_FOUNDATION_PROBE.Plan({candidate(1,4,0),candidate(2,1,1)});assert(CSC_FOUNDATION_PROBE.plan[1].plot==2)")

    def test_specialty_breaks_equal_base_tie(self):
        self.run_lua("CSC_FOUNDATION_PROBE.Plan({candidate(1,2,1),candidate(2,2,2)});assert(CSC_FOUNDATION_PROBE.plan[1].plot==2)")

    def test_specialty_without_base_is_rejected(self):
        self.run_lua("CSC_FOUNDATION_PROBE.Plan({candidate(1,0,3)});assert(#CSC_FOUNDATION_PROBE.plan==0)")

    def test_resource_must_be_visible(self):
        self.run_lua("visible=false;CSC_FOUNDATION_PROBE.Plan({candidate(1,1,1)});assert(#CSC_FOUNDATION_PROBE.plan==0)")

    def test_target_must_be_owned(self):
        self.run_lua("owner=2;CSC_FOUNDATION_PROBE.Plan({candidate(1,1,1)});assert(#CSC_FOUNDATION_PROBE.plan==0)")

    def test_existing_feature_still_blocks_target(self):
        self.run_lua("feature=1;CSC_FOUNDATION_PROBE.Plan({candidate(1,1,1)});assert(#CSC_FOUNDATION_PROBE.plan==0)")

    def test_commit_uses_zero_and_never_recreates(self):
        self.run_lua("CSC_FOUNDATION_PROBE.Plan({candidate(1,1,1)});CSC_FOUNDATION_PROBE.Commit();assert(mutations==1);CSC_FOUNDATION_PROBE.Plan({candidate(1,1,1)});assert(#CSC_FOUNDATION_PROBE.plan==0);assert(queue:CurrentlyBuilding()=='UNIT_TRADER')")

    def test_fresh_same_type_check_prevents_stale_commit(self):
        self.run_lua("CSC_FOUNDATION_PROBE.Plan({candidate(1,1,1)});existing={district(36,false)};local ok=pcall(CSC_FOUNDATION_PROBE.Commit);assert(not ok);assert(mutations==0)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lua51-path', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    sys.path.insert(0, str(args.lua51_path))
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PlannerTests))
    if args.output:
        args.output.write_text(json.dumps({'passed':result.wasSuccessful(),'actual_lua51_fixtures':result.testsRun,'native_connections':0,'installed_changes':False},indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
