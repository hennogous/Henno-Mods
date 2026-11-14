"""Read-only observer contract tests; no game process, CE DLL or console.

Run with the existing CSC Lua51/Lupa test environment. Fixtures deliberately
expose native-publication returns, district event timing and material loss;
these are observer truthfulness contracts, not copies of CSC placement policy.
"""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


SOURCE = Path(__file__).with_name("planning_observer.lua")
FIXTURE = r'''
logs={};function print(...)local a={...};for i,v in ipairs(a)do a[i]=tostring(v)end;logs[#logs+1]=table.concat(a,'\t')end
function info(rows,field)
 local t={};for _,r in ipairs(rows)do if r.Index then t[r.Index]=r end;if field then t[r[field]]=r end end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
GameInfo={
 Districts=info({{Index=1,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'},{Index=2,DistrictType='DISTRICT_CITY_CENTER'},
  {Index=3,DistrictType='DISTRICT_TEST_PROVIDER'},{Index=4,DistrictType='DISTRICT_CAMPUS'}},'DistrictType'),
 Buildings=info({{Index=1,BuildingType='BUILDING_GRANARY',PrereqDistrict='DISTRICT_CITY_CENTER'}},'BuildingType'),
 Resources=info({{Index=1,ResourceType='RESOURCE_TEST_BASE'},{Index=2,ResourceType='RESOURCE_TEST_SPEC'}},'ResourceType'),
 Improvements=info({{Index=1,ImprovementType='IMPROVEMENT_FARM'}},'ImprovementType'),
 Improvement_ValidResources=info({{ImprovementType='IMPROVEMENT_FARM',ResourceType='RESOURCE_TEST_BASE'},
  {ImprovementType='IMPROVEMENT_FARM',ResourceType='RESOURCE_TEST_SPEC'}}),
 CSC_QuarterCustomerBuildings=info({{QuarterKey='BAKERS',ProducerStage=2,DistrictType='DISTRICT_CITY_CENTER',BuildingType='BUILDING_GRANARY'}}),
 DistrictReplaces=info({}),BuildingReplaces=info({})}
Game={t=1,GetCurrentGameTurn=function()return Game.t end}
Events={};GameEvents={}
function hook()return {Add=function(fn)return fn end}end
for _,n in ipairs({'DistrictAddedToMap','DistrictBuildProgressChanged','ResourceAddedToMap','ResourceRemovedFromMap',
 'ImprovementAddedToMap','ImprovementRemovedFromMap','ImprovementChanged'})do
 local h={callbacks={}};h.Add=function(f)h.callbacks[#h.callbacks+1]=f end;Events[n]=h
end
GameEvents.OnGameTurnStarted={callbacks={}};GameEvents.OnGameTurnStarted.Add=function(f)table.insert(GameEvents.OnGameTurnStarted.callbacks,f)end
function fire(name,...)for _,f in ipairs(Events[name].callbacks)do f(...)end end
function poll()for _,f in ipairs(GameEvents.OnGameTurnStarted.callbacks)do f()end end
plots={};function plot(id,resource,improvement)
 local p={id=id,resource=resource or -1,improvement=improvement or -1,owner=0,district=-1,pillaged=false}
 function p:GetIndex()return self.id end;function p:GetX()return self.id end;function p:GetY()return 0 end
 function p:GetResourceType()return self.resource end;function p:GetImprovementType()return self.improvement end
 function p:GetOwner()return self.owner end;function p:GetDistrictType()return self.district end
 function p:IsImprovementPillaged()return self.pillaged end
 plots[id]=p;return p
end
for i=1,6 do plot(i)end;plots[4].resource=1;plots[4].improvement=1
Map={GetPlot=function(x,y)return plots[x]end,GetPlotByIndex=function(i)return plots[i]end,
 GetAdjacentPlots=function(x,y)local r={};for i=1,6 do if i~=x then r[#r+1]=plots[i]end end;return r end}
ds={};function district(id,kind,where,complete)
 local d={id=id,kind=kind,where=where,complete=complete,pillaged=false}
 function d:GetID()return self.id end;function d:GetType()return self.kind end
 function d:GetX()return self.where end;function d:GetY()return 0 end
 function d:IsComplete()return self.complete end;function d:IsPillaged()return self.pillaged end
 ds[#ds+1]=d;plots[where].district=kind;return d
end
district(1,2,1,true)
districtsAPI={GetNumDistricts=function()return #ds end,GetDistrictByIndex=function(self,i)return ds[i+1]end,
 FindID=function(self,id)for _,d in ipairs(ds)do if d.id==id then return d end end end,
 HasDistrict=function(self,kind)for _,d in ipairs(ds)do if d.kind==kind then return true end end;return false end}
city={GetID=function()return 10 end,GetDistricts=function()return districtsAPI end,
 GetBuildings=function()return {HasBuilding=function()return false end}end}
cities={Members=function()local used=false;return function()if not used then used=true;return 10,city end end end}
Players={[0]={GetCities=function()return cities end,GetDistricts=function()return districtsAPI end}}
PlayerManager={GetAlive=function()
 local alive={};for id,p in pairs(Players)do
  local pid=id;p.GetID=function()return pid end
  if p:GetCities()then alive[#alive+1]=p end
 end;return alive
end}
PlayersVisibility={[0]={IsRevealed=function()return true end}}
CityManager={GetCity=function()return city end}
CSC_Adjacency={HasTag=function(tag,name)
 return tag=='CLASS_CSC_BAKERS_BASE'and name=='RESOURCE_TEST_BASE'
  or tag=='CLASS_CSC_BAKERS_SPEC'and name=='RESOURCE_TEST_SPEC'
  or tag=='CLASS_CSC_BAKERS_GOODS_PROVIDER'and name=='DISTRICT_TEST_PROVIDER'
 end,ResourceVisible=function()return true end}
profile={key='BAKERS',base='CLASS_CSC_BAKERS_BASE',specialty='CLASS_CSC_BAKERS_SPEC',district=GameInfo.Districts[1]}
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return {profile}end}
geometryCalls=0;siteCalls=0;offerEnabled=false;geometryUpper=4
snapshot={id=0,player=Players[0],Geometry=function(c,p,profile)geometryCalls=geometryCalls+1;return {base=2,upper=geometryUpper}end,
 Site=function()siteCalls=siteCalls+1;error('observer must not call Site')end}
CSC_AI_EconomyAdapters={QuarterBids=function(s,p,protected,early)
 s.Geometry(city,plots[2],profile)
 local result={};if offerEnabled then result[1]={player=0,city=10,district=1,plot=2,finalQ8=12345,adjacency=4}end
 return result,{evaluated=1},'thirdReturn'
end}
publishAccepted=true;publishCalls=0
CSC_AI_DistrictBridge={Publish=function(...)publishCalls=publishCalls+1;return publishAccepted,'message',nil,'fourth' end}
CSC_PLANNING_RESOURCE_ORIGINS={RESOURCE_TEST_BASE='modded',RESOURCE_TEST_SPEC='modded'}
function publish()
 local entries,stats,third=CSC_AI_EconomyAdapters.QuarterBids(snapshot,CSC_AI_QuarterPlacement,{},{});
 return CSC_AI_DistrictBridge.Publish(Game.t,10,10,1,{0},entries),third
end
'''


class PlanningObserverTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(FIXTURE)
        self.lua.execute(SOURCE.read_text(encoding="utf-8"))

    def rows(self, kind):
        prefix = "CSC_PLANNING_" + kind + "\t"
        return [dict(field.split("=", 1) for field in value[len(prefix):].split("\t"))
                for value in self.lua.globals().logs.values() if value.startswith(prefix)]

    def test_wrappers_preserve_returns_and_never_repeat_geometry_or_forecast(self):
        self.lua.execute("originalGeometry=snapshot.Geometry; entries,stats,third=CSC_AI_EconomyAdapters.QuarterBids(snapshot,CSC_AI_QuarterPlacement,{},{}); a,b,c,d=CSC_AI_DistrictBridge.Publish(1,10,10,1,{0},entries)")
        self.assertEqual(self.lua.eval("geometryCalls"), 1)
        self.assertEqual(self.lua.eval("siteCalls"), 0)
        self.assertTrue(self.lua.eval("snapshot.Geometry==originalGeometry"))
        self.assertEqual(self.lua.eval("third"), "thirdReturn")
        self.assertEqual(self.lua.eval("a,b,c,d"), (True, "message", None, "fourth"))
        self.assertEqual(self.rows("OPPORTUNITY")[0]["qualified"], "true")

    def test_defer_reconsider_requires_accepted_publication(self):
        self.lua.execute("publish(); Game.t=2;offerEnabled=true;publishAccepted=false;publish();Game.t=3;publishAccepted=true;publish()")
        transitions = self.rows("PLAN_TRANSITION")
        self.assertEqual([r["state"] for r in transitions], ["deferred", "offered"])
        self.assertEqual(transitions[-1]["reconsidered"], "true")
        self.assertEqual(transitions[-1]["turn"], "3")

    def test_foundation_completion_stale_event_and_provider_order(self):
        self.lua.execute("fire('DistrictAddedToMap',0,99,10,2,0,1);Game.t=2;q=district(2,1,2,false);fire('DistrictAddedToMap',0,2,10,2,0,1);fire('DistrictAddedToMap',0,2,10,2,0,1);Game.t=3;q.complete=true;fire('DistrictBuildProgressChanged',0,2,10,2,0,1);Game.t=4;d=district(3,3,3,false);fire('DistrictAddedToMap',0,3,10,3,0,3);poll()")
        self.assertEqual(len(self.rows("EVENT_DEFERRED")), 1)
        self.assertEqual(len(self.rows("FOUNDATION")), 2)
        self.assertEqual(len(self.rows("COMPLETION")), 1)
        customer = [r for r in self.rows("RELATION") if r["role"] == "customer"][0]
        self.assertEqual(customer["foundationOrder"], "neighbourPreexistingDateUnknown")
        provider = [r for r in self.rows("RELATION") if r["role"] == "goodsProvider"][0]
        self.assertEqual(provider["foundationOrder"], "quarterFirst")
        self.assertEqual(self.rows("FAULT"), [])

    def test_material_loss_reconstructs_resource_and_last_working_class(self):
        self.lua.execute("q=district(2,1,2,true);fire('DistrictAddedToMap',0,2,10,2,0,1);Game.t=2;poll();Game.t=3;plots[4].pillaged=true;fire('ImprovementChanged',4,0);Game.t=4;plots[4].resource=-1;fire('ResourceRemovedFromMap',4,0)")
        changes = [r for r in self.rows("MATERIAL_STATE") if r["materialPlot"] == "4"]
        self.assertEqual(changes[0]["origin"], "modded")
        self.assertEqual(changes[1]["lostWorking"], "true")
        self.assertEqual(changes[1]["lastWorkingBase"], "true")
        self.assertEqual(changes[2]["lostBase"], "true")
        self.assertEqual(changes[2]["previousResource"], "RESOURCE_TEST_BASE")
        self.assertEqual(self.rows("FAULT"), [])

    def test_poll_missing_event_and_capture_do_not_invent_foundation(self):
        self.lua.execute("Game.t=2;q=district(2,1,2,false);poll();Game.t=3;q.id=42;q.complete=true;poll()")
        self.assertEqual(len(self.rows("FOUNDATION")), 0)
        first = [r for r in self.rows("FIRST_OBSERVED") if r["plot"] == "2"][0]
        self.assertEqual(first["eventMissing"], "true")
        self.assertEqual(first["foundationDateKnown"], "false")

    def test_capture_keeps_foundation_history_and_rebuild_gets_new_history(self):
        self.lua.execute("Game.t=2;q=district(2,1,2,true);fire('DistrictAddedToMap',0,2,10,2,0,1);Game.t=3;Players[1]=Players[0];q.id=42;fire('DistrictBuildProgressChanged',1,42,10,2,0,1)")
        self.assertEqual(len(self.rows("FOUNDATION")), 1)
        capture = self.rows("OWNERSHIP")[0]
        self.assertEqual(capture["foundationTurn"], "2")
        self.assertEqual(capture["previousPlayer"], "0")
        self.lua.execute("Game.t=4;q.id=43;q.complete=false;fire('DistrictAddedToMap',1,43,10,2,0,1)")
        self.assertEqual(len(self.rows("FOUNDATION")), 2)
        self.assertEqual(self.rows("FOUNDATION")[-1]["foundationTurn"], "4")

    def test_spec_resource_uses_loaded_mapping_and_visibility_is_not_harvest(self):
        self.lua.execute("plots[5].resource=2;plots[5].improvement=1;q=district(2,1,2,false);fire('DistrictAddedToMap',0,2,10,2,0,1);Game.t=2;PlayersVisibility[0].IsRevealed=function()return false end;poll()")
        spec = [r for r in self.rows("MATERIAL_STATE") if r["materialPlot"] == "5"]
        self.assertEqual(spec[0]["spec"], "true")
        self.assertEqual(spec[0]["working"], "true")
        self.assertEqual(spec[-1]["resource"], "RESOURCE_TEST_SPEC")
        self.assertEqual(spec[-1]["lostSpec"], "false")
        self.assertEqual(spec[-1]["lostWorking"], "true")
        self.assertEqual(spec[-1]["revealed"], "false")

    def test_unrelated_compatible_improvement_is_not_quarter_supply(self):
        # Reproduce the campaign's unrelated Potato Farm false loss: its
        # improvement is valid, but neither material class maps the resource.
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(FIXTURE+"""
GameInfo.Resources=info({{Index=1,ResourceType='RESOURCE_TEST_BASE'},
 {Index=2,ResourceType='RESOURCE_TEST_SPEC'},
 {Index=3,ResourceType='RESOURCE_TEST_UNRELATED'}},'ResourceType')
GameInfo.Improvement_ValidResources=info({
 {ImprovementType='IMPROVEMENT_FARM',ResourceType='RESOURCE_TEST_BASE'},
 {ImprovementType='IMPROVEMENT_FARM',ResourceType='RESOURCE_TEST_UNRELATED'}})
plots[5].resource=3;plots[5].improvement=1
""")
        self.lua.execute(SOURCE.read_text(encoding='utf-8'))
        self.lua.execute("q=district(2,1,2,false);fire('DistrictAddedToMap',0,2,10,2,0,1);Game.t=2;plots[5].improvement=-1;poll()")
        unrelated=[r for r in self.rows('MATERIAL_STATE')if r['materialPlot']=='5']
        self.assertEqual(unrelated[0]['compatible'],'true')
        self.assertEqual(unrelated[0]['working'],'false')
        self.assertEqual(unrelated[-1]['lostWorking'],'false')
        self.assertEqual(self.rows('FAULT'),[])

    def test_diagnostic_geometry_failure_cannot_change_original_returns(self):
        self.lua.execute("snapshot.Geometry=function()return nil end;entries,stats,third=CSC_AI_EconomyAdapters.QuarterBids(snapshot,CSC_AI_QuarterPlacement,{},{});a=CSC_AI_DistrictBridge.Publish(1,10,10,1,{0},entries)")
        self.assertEqual(self.lua.eval("third"), "thirdReturn")
        self.assertTrue(self.lua.eval("a"))
        self.assertEqual(len(self.rows("FAULT")), 1)

    def test_native_comparison_drain_time_and_ui_snapshot_are_qualified(self):
        self.lua.execute("CSC_AI_PLANNING_READ_ADJACENCY=function(p,c,plot,d)return {available=true,turn=Game.t,plotDistrict=d,yields={YIELD_PRODUCTION=3}}end;CSC_AI_PLANNING_WATCH.Native({player=0,city=10,district=1,plot=2,result=444,observedTurn=1,nativeOrdinal=7});Game.t=2;q=district(2,1,2,false);fire('DistrictAddedToMap',0,2,10,2,0,1)")
        row = self.rows("FOUNDATION")[0]
        self.assertEqual(row["nativeQ8"], "444")
        self.assertEqual(row["nativeDrainTurn"], "1")
        self.assertEqual(row["nativeCallTurnKnown"], "false")
        self.assertEqual(self.rows("ADJACENCY")[-1]["exactFoundationTime"], "false")

    def test_native_decline_is_not_a_selected_forecast(self):
        self.lua.execute("CSC_AI_PLANNING_WATCH.Native({nativeKind='decline',player=0,city=10,district=1,plot=2,result=-999,observedTurn=1});Game.t=2;q=district(2,1,2,false);fire('DistrictAddedToMap',0,2,10,2,0,1)")
        self.assertEqual(len(self.rows('NATIVE_DECLINE')),1)
        self.assertEqual(len(self.rows('NATIVE_BEST')),0)
        self.assertNotIn('nativeQ8',self.rows('FOUNDATION')[0])

    def test_diagnostic_failure_and_cap_do_not_disable_policy(self):
        self.lua.execute("snapshot.Geometry=function()error('native geometry failure')end;ok=pcall(CSC_AI_EconomyAdapters.QuarterBids,snapshot,CSC_AI_QuarterPlacement,{},{});a,b,c,d=CSC_AI_DistrictBridge.Publish(1,10,10,1,{0},{})")
        self.assertFalse(self.lua.eval("ok"))
        self.assertTrue(self.lua.eval("a"))
        # A separate observer instance with a tiny diagnostic cap still publishes.
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE + "\nCSC_PLANNING_MAX_RECORDS=1")
        lua.execute(SOURCE.read_text(encoding="utf-8"))
        lua.execute("publish();CSC_AI_PLANNING_WATCH.Finish()")
        self.assertEqual(lua.eval("publishCalls"), 1)
        self.assertTrue(any("CSC_PLANNING_LIMIT" in r for r in lua.globals().logs.values()))


if __name__ == "__main__":
    unittest.main()
