"""Real SQL/Facts route reader and event factory; only game objects are fixtures."""
import unittest
from test_material_fact_path import world
from route_fixture import bind


def observed_world():
    vm=world(host='IMPROVEMENT_RES2_SAWMILL')
    bind(vm)
    vm.execute('''
D=assert(CSC_TradeRouteCore.ReadDefinitions(GameInfo))
CHANNEL=D.byId.BAKERS_BAKERY
EXTRA_BUILDINGS={[GameInfo.Buildings[CHANNEL.producer].Index]=true}
WORKERS=0;BRIDGE_CALLS=0;BRIDGE_TURN=20;OP_START=15
local original=player.GetCities
player.GetCities=function(...)
 local result=original(...)
 result.FindID=function(_,id)return id==1 and city or id==2 and workerCity or nil end
 return result
end
player.GetUnits=function()return{FindID=function()return{
 GetOperationType=function()return 0x8374d954 end,
 GetOperationParameter=function()return OP_START end}end}end
Players={[1]=player}
for _,c in ipairs({city,workerCity})do
 local actual=c
 local ds=c:GetDistricts()
 ds.HasDistrict=function(_,id)return actual==city and id==profile.district.Index end
 ds.IsPillaged=function()return false end
 c.GetDistricts=function()return ds end
 c.GetProperty=function(_,key)
  if key==CHANNEL.supplyProperty and actual==city then return 1 end
  return 0
 end
end
placement.StageTwoProfiles=function()return{profile}end
Game.GetEras=function()return{GetCurrentEra=function()return 1 end}end
GameConfiguration={GetGameSpeedType=function()return'ONLINE'end}
UnitOperationTypes={MAKE_TRADE_ROUTE=0x8374d954,PARAM_TURN=0xa783eab4}
GameInfo.Eras={[1]={EraType='ERA_CLASSICAL'}}
GameInfo.GameSpeeds={ONLINE={CostMultiplier=50}}
GameInfo.GlobalParameters={TRADE_ROUTE_TURN_DURATION_BASE={Value=20}}
ExposedMembers={CSC_TradeRoutes={GetFacts=function()
 BRIDGE_CALLS=BRIDGE_CALLS+1
 return{version=1,turn=BRIDGE_TURN,cities={
  ['1:1']={player=1,city=1,properties={[CHANNEL.supplyProperty]=999}},
  ['1:2']={player=1,city=2}},routes={{origin='1:2',destination='1:1',native={TraderUnitPlayer=1,TraderUnitID=5}}}}
end}}
''')
    return vm


class RouteFacts(unittest.TestCase):
    def test_ai_scope_keeps_owned_cities_and_skips_unrelated_foreign_network(self):
        observed_world().execute('''
local get=ExposedMembers.CSC_TradeRoutes.GetFacts
Players[2]={GetCities=function()error('Unrelated foreign city should not be refreshed')end}
ExposedMembers.CSC_TradeRoutes.GetFacts=function()
 local facts=get();facts.cities['2:77']={player=2,city=77};facts.cities['3:88']={player=3,city=88}
 facts.routes[#facts.routes+1]={origin='2:77',destination='3:88',native={TraderUnitPlayer=2,TraderUnitID=99}}
 return facts
end
local _,_,snapshot=evaluate();local t=assert(snapshot.TradeRoutes())
assert(t.observed.cities['1:1']and t.observed.cities['1:2'])
assert(t.observed.cities['2:77']==nil and #t.observed.routes==1)
''')

    def test_one_observation_refreshes_gameplay_endpoints_and_native_start(self):
        observed_world().execute('''
local _,site,snapshot=evaluate()
local facts=assert(snapshot.TradeRoutes())
assert(facts.observed.cities['1:1'].properties[CHANNEL.supplyProperty]==1)
assert(facts.observed.routes[1].nativeStartTurn==15 and facts.observed.routes[1].observedThrough==5)
assert(snapshot.TradeRoutes()==facts and BRIDGE_CALLS==1)
''')

    def test_route_supply_does_not_require_worker_or_registered_material_input_host(self):
        observed_world().execute('''
local _,site,snapshot=evaluate()
local t=assert(snapshot.TradeWorld({site}))
local found=false
for _,e in ipairs(t.plannedChanges)do if e.key==CHANNEL.supplyProperty then
 found=true;assert(e.ready==0 and e.value==1 and e.investmentKey==nil)
end end
assert(found and site.suppliers[1].worked==false)
local after=assert(snapshot.TradeWorld({site},{removedPlot=2,ready=0}))
local zero=false
for _,e in ipairs(after.changes)do if e.key==CHANNEL.supplyProperty then zero=e.value==0 and e.ready==0 end end
assert(zero)
for _,e in ipairs(after.plannedChanges)do assert(e.key~=CHANNEL.supplyProperty)end
assert(after.observed==t.observed) -- One acknowledged baseline across alternatives.
local future,reason=snapshot.TradeWorld({site},{removedPlot=2,ready=5})
assert(future==nil and reason=='Only immediate district footprints are supported')
''')

    def test_stale_snapshot_or_reassigned_trader_cannot_enter_joint_world(self):
        observed_world().execute('''
BRIDGE_TURN=18
local _,_,snapshot=evaluate()
assert(snapshot.TradeRoutes()==nil)
BRIDGE_TURN=19;OP_START=20
local _,_,nextSnapshot=evaluate()
local facts,reason=nextSnapshot.TradeRoutes()
assert(facts==nil and reason=='Observed route operation changed')
''')

    def test_native_supply_threshold_and_shared_material_plot_identity_drive_readiness(self):
        observed_world().execute('''
local requirements={requirements={{tag='BASE',count=2},{tag='SPEC',count=1}}}
local R=CSC_TradeRouteCore
local a={plot=1,ready=0,tags={BASE=true,SPEC=true}}
assert(R.SupplyReady(requirements,{a,a})==math.huge)
assert(R.SupplyReady(requirements,{a,{plot=2,ready=7,tags={BASE=true}}})==7)
assert(R.SupplyReady(requirements,{
 {plot=3,ready=4,tags={BASE=true}},{plot=2,ready=7,tags={BASE=true}},
 {plot=1,ready=0,tags={BASE=true,SPEC=true}}})==4)
''')


if __name__=='__main__':unittest.main()
