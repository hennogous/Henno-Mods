"""Guard the common diagnostic map and exact one-rule counterfactual."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from early_host_policy import stage
from liverpool_river_policy import PREPARE, without_river, OMISSION


class RiverPolicy(unittest.TestCase):
    def test_omission_changes_only_exact_rule_and_site(self):
        for pid,city,plot,rule,omitted in (
            (4,131073,2497,'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER',True),
            (3,131073,2497,'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER',False),
            (4,65536,2497,'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER',False),
            (4,131073,2495,'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER',False),
            (4,131073,2497,'CSC_BAKERS_PRODUCTION_FROM_BASE',False)):
            vm=LuaRuntime();vm.execute(f'pid={pid};city={{GetID=function()return {city} end}};'
                f'plot={{GetIndex=function()return {plot} end}};r={{ID="{rule}"}};count=2')
            vm.execute(OMISSION.decode())
            self.assertEqual(vm.globals().count,0 if omitted else 2)

    def test_saved_role_telemetry_has_no_turn22_migration(self):
        root=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI'
        original=(root/'CSC_AI_AdjacencyScan.lua').read_bytes()
        publisher=(root/'CSC_AI_BakersGameplay.lua').read_bytes()
        scanner,publisher=stage(original,publisher,migrate_roles=False)
        prefix=publisher.split(b'--',1)[0]
        self.assertTrue(publisher.startswith(b'function CSC_EARLY_DIAG_Retained'))
        self.assertNotIn(b'Early saved role differs',publisher)
        modified=without_river(scanner)
        replacement=b'    local count=A.Count(r,plot,city,pid)\n'+OMISSION+b'    local amount=A.Amount(r,count)'
        self.assertEqual(modified.replace(replacement,b'    local count=A.Count(r,plot,city,pid);local amount=A.Amount(r,count)'),scanner)
        for source in (publisher,modified,PREPARE.encode()):
            LuaRuntime().eval('function(code)return assert(loadstring(code))end')(source.decode('utf-8-sig'))

    def test_preparation_checks_all_resources_before_writes(self):
        fixture='''
print=function()end;writes=0
Game={GetCurrentGameTurn=function()return 25 end};AutoplayManager={IsActive=function()return false end}
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=36}},Resources={RESOURCE_CSC_FLAX={Index=1},RESOURCE_WHEAT={Index=2}}}
city={GetName=function()return 'LOC_CITY_NAME_LIVERPOOL'end,GetID=function()return 131073 end,
 GetDistricts=function()return {HasDistrict=function()return false end}end}
CityManager={GetCity=function()return city end};Cities={GetPlotPurchaseCity=function()return city end}
plots={};for _,r in ipairs({{2572,1,0},{2498,2,-1},{2497,-1,-1}})do
 local p={resource=r[2]};p.GetOwner=function()return 4 end;p.GetResourceType=function()return p.resource end
 p.GetDistrictType=function()return r[3]end;p.GetImprovementType=function()return -1 end
 p.GetRiverCrossingCount=function()return 2 end;plots[r[1]]=p
end
Map={GetPlotByIndex=function(index)return plots[index]end}
ResourceBuilder={SetResourceType=function(p,value)writes=writes+1;p.resource=value end}
CSC_AI_QuarterAdjacencyValue=function()return {total=4,production=2,gold=2}end
'''
        for change,allowed in (('',True),('plots[2498].resource=999',False),('plots[2572].resource=999',False)):
            vm=LuaRuntime();vm.execute(fixture+change)
            if allowed:vm.execute(PREPARE)
            else:
                with self.assertRaises(Exception):vm.execute(PREPARE)
            self.assertEqual(vm.globals().writes,2 if allowed else 0)


if __name__=='__main__':unittest.main()
