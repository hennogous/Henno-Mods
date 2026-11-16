"""Native route read-model -> shared kernel, using actual production SQL/Lua."""
import sqlite3
import json
import unittest
from lupa.lua51 import LuaRuntime
from population_catalogue_fixture import compile_catalogue,graph,MOD
from route_fixture import bind


class Routes(unittest.TestCase):
    def test_route_projection_and_shared_imports_load_after_gameplay_bindings(self):
        path=MOD.parent/'project/modbuddy/CivSupplyChains.actions.json'
        actions={a['id']:a for a in json.loads(path.read_text())['blocks']['inGameActions']}
        order=lambda key:int(actions[key]['properties']['LoadOrder'])
        self.assertIn('Data/CSC_TradeRouteSchema.sql',actions['CSC_Q_ALL']['files'])
        self.assertEqual(set(actions['CSC_TradeRouteShared']['files']),{
            'Lua_UI/TradeRoutes/CSC_TradeRouteCore.lua','Lua_UI/TradeRoutes/CSC_TradeRouteFacts.lua'})
        self.assertNotIn('criteria',actions['CSC_TradeRouteProcessor'])
        for key in ('CSC_Q_BAKERS','CSC_Q_BAKERS_GOLD','CSC_Q_TAILORS','CSC_Q_TAILORS_GOLD','ModSupport_LGD'):
            self.assertLess(order(key),order('CSC_TradeRouteProcessor'))
        self.assertLess(order('CSC_TradeRouteProcessor'),order('CSC_SUIA_YieldPresentationDatabase'))

    def vm(self,*,gold=True,database=None):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute('GameInfo={}')
        bind(vm,gold=gold,database=database)
        vm.execute('''
R=CSC_TradeRouteCore;D=assert(R.ReadDefinitions(GameInfo))
function city(player,id)
 local c={player=player,city=id,quarters={},properties={},buildings={}}
 for _,channel in ipairs(D.channels)do c.properties[channel.supplyProperty]=1;c.buildings[channel.producer]=true end
 return c
end
function amount(streams,id,yield)
 local total=0
 for _,s in ipairs(streams)do if s.city==id and s.yield==yield then total=total+s.amount end end
 return total
end
''')
        return vm

    def test_all_bit_rows_and_gold_companion_are_read_without_native_changes(self):
        for gold,expected in ((True,80),(False,60)):
            db=compile_catalogue(gold=gold)
            before=graph(db,'all_csc')
            db.executescript((MOD/'Data/CSC_TradeRouteProcessor.sql').read_text())
            self.assertEqual(before,graph(db,'all_csc'))
            self.assertEqual(db.execute('SELECT COUNT(*) FROM CSC_TradeRoutePayouts').fetchone()[0],expected)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM CSC_TradeRouteSupplyRequirements').fetchone()[0],6)
            vm=self.vm(database=db)
            vm.execute('''local a,b=city(1,1),city(1,2)
local income=R.Nominal(D,a,b,'DESTINATION');assert(income.YIELD_PRODUCTION==4)''')
            self.assertEqual(vm.eval("R.Nominal(D,city(1,1),city(1,2),'DESTINATION').YIELD_GOLD or 0"),4 if gold else 0)

    def test_scanner_source_asymmetry_and_origin_quarter_flags_are_preserved(self):
        self.vm().execute('''
local a,b=city(1,1),city(2,2)
b.buildings.BUILDING_CSC_BAKERS_BAKERY=false
b.buildings.BUILDING_CSC_TAILORS_TAILOR=false
assert(R.Eligible(D.byId.BAKERS_BAKERY,a,b))
assert(not R.Eligible(D.byId.TAILORS_TAILOR,a,b))
assert(R.Nominal(D,a,b,'ORIGIN').YIELD_FOOD==2)
assert(R.Nominal(D,a,b,'DESTINATION').YIELD_PRODUCTION==2)
a.quarters.DISTRICT_CSC_BAKERS_QUARTER=true
assert(not R.Eligible(D.byId.BAKERS_BAKERY,a,b))
assert(R.Eligible(D.byId.TAILORS_FASHION_HOUSE,a,b))
a.quarters.DISTRICT_CSC_BAKERS_QUARTER=false
assert(R.Eligible(D.byId.BAKERS_BAKERY,a,b))
''')

    def test_counts_wrap_and_keep_domestic_foreign_owner_identity(self):
        self.vm().execute('''
local a,b,d=city(1,1),city(2,1),city(1,2)
local cities={['1:1']=a,['2:1']=b,['1:2']=d}
local routes={{origin='1:1',destination='1:2'},{origin='1:1',destination='1:2'},{origin='2:1',destination='1:2'}}
local counts=assert(R.Accumulate(routes,cities,D))
assert(counts['1:1'].channels.BAKERS_BAKERY.ORIGIN==2)
assert(counts['2:1'].channels.BAKERS_BAKERY.ORIGIN==1)
assert(counts['1:2'].channels.BAKERS_BAKERY.DESTINATION==3)
local income=assert(R.Economy(counts,cities,D,1))
assert(amount(income,1,'YIELD_FOOD')==4 and amount(income,2,'YIELD_PRODUCTION')==12)
for _,s in ipairs(income)do assert(s.player==1)end
for _,count in ipairs({0,1,2,31,32,33})do
 local paid=R.EvaluateBits(D.byId.BAKERS_BAKERY,count,'ORIGIN',a)
 assert((paid.YIELD_FOOD or 0)==count%32 and(paid.AMENITY or 0)==count%32)
end
''')

    def test_actual_native_amount_mutation_reaches_preview_and_economy(self):
        db=compile_catalogue()
        db.execute("UPDATE ModifierArguments SET Value='3' WHERE ModifierId='MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD' AND Name='Amount'")
        db.execute("UPDATE ModifierArguments SET Value='7' WHERE ModifierId='MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD_BIT_2' AND Name='Amount'")
        db.executescript((MOD/'Data/CSC_TradeRouteProcessor.sql').read_text())
        self.vm(database=db).execute('''
local a,b=city(1,1),city(2,2)
assert(R.Nominal(D,a,b,'ORIGIN').YIELD_FOOD==4) -- Bakery3 + Cafe1.
local cities={['1:1']=a,['2:2']=b}
local counts=R.Accumulate({{origin='1:1',destination='2:2'}},cities,D)
assert(amount(R.Economy(counts,cities,D,1),1,'YIELD_FOOD')==4)
assert(R.EvaluateBits(D.byId.BAKERS_BAKERY,2,'ORIGIN',a).YIELD_FOOD==7)
''')

    def test_unknown_native_gate_or_missing_bit_is_rejected(self):
        for sql in (
            "UPDATE RequirementArguments SET Value=2 WHERE RequirementId='REQ_CSC_BAKERS_IMPORT_CONSUMER_ROUTE_BIT_1' AND Name='PropertyMinimum'",
            "DELETE FROM Modifiers WHERE ModifierId='MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD_BIT_4'",
            "UPDATE RequirementSets SET RequirementSetType='REQUIREMENTSET_TEST_ANY' WHERE RequirementSetId='REQSET_CSC_BAKERS_EXPORT_BAKERY_SUPPLY_PREREQ'",
        ):
            with self.subTest(sql=sql):
                db=compile_catalogue();db.execute(sql)
                with self.assertRaises(sqlite3.IntegrityError):db.executescript((MOD/'Data/CSC_TradeRouteProcessor.sql').read_text())

    def test_unsupported_lifecycle_or_dynamic_scope_is_rejected(self):
        for modifier in ('MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD','MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP'):
            for flag in ('RunOnce','Permanent','NewOnly','Repeatable'):
                with self.subTest(modifier=modifier,flag=flag):
                    db=compile_catalogue()
                    db.execute('UPDATE Modifiers SET '+flag+'=1 WHERE ModifierId=?',(modifier,))
                    with self.assertRaises(sqlite3.IntegrityError):db.executescript((MOD/'Data/CSC_TradeRouteProcessor.sql').read_text())
        db=compile_catalogue()
        db.execute("UPDATE DynamicModifiers SET CollectionType='COLLECTION_PLAYER_CITIES' WHERE ModifierType='MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE'")
        with self.assertRaises(sqlite3.IntegrityError):db.executescript((MOD/'Data/CSC_TradeRouteProcessor.sql').read_text())

    def test_timeline_removes_imports_at_foundation_and_never_invents_renewal(self):
        self.vm().execute('''
local a,b=city(1,1),city(2,2)
local world={cities={['1:1']=a,['2:2']=b},routes={{origin='1:1',destination='2:2',observedThrough=4}},
 changes={{ready=2,city='1:1',field='quarters',key='DISTRICT_CSC_BAKERS_QUARTER',value=true}}}
local flows=assert(R.Forecast(world,D,1,10))
local food,culture=0,0
for _,s in ipairs(flows)do
 if s.yield=='YIELD_FOOD'then food=food+s.amount;assert(s.ready==0 and s.finish==2)end
 if s.yield=='YIELD_CULTURE'then culture=culture+s.amount;assert(s.ready==0 and s.finish==4)end
end
assert(food==2 and culture==2 and a.quarters.DISTRICT_CSC_BAKERS_QUARTER==nil)
world.changes={};world.routes[1].observedThrough=nil
for _,s in ipairs(R.Forecast(world,D,1,10))do assert(s.finish==1)end
''')

    def test_wrapped_counter_recovery_requires_known_removal_not_a_coverage_cutoff(self):
        self.vm().execute('''
local routes={}
for i=1,32 do routes[i]={origin='1:1',destination='2:2',observedThrough=i==32 and 4 or 10}end
local w={cities={['1:1']=city(1,1),['2:2']=city(2,2)},routes=routes}
local flows=assert(R.Forecast(w,D,1,10))
assert(#flows==0) -- One uncertain contributor cannot be assumed to have ended.
routes[32].removedAt=4 -- Explicit controlled removal is a different scenario input.
flows=assert(R.Forecast(w,D,1,10))
for _,s in ipairs(flows)do assert(s.ready==4 and s.finish==10)end
assert(amount(flows,1,'YIELD_FOOD')==62)
''')

    def test_native_minimum_duration_rounds_components_separately(self):
        self.vm().execute('''
assert(R.MinimumEnd(10,20,50,10)==25)
assert(R.MinimumEnd(10,20,67,-3)==20) -- floor13.4 + floor-2.01.
assert(R.MinimumEnd(10,0,50,-10)==11)
assert(R.MinimumEnd(nil,20,50,0)==nil)
assert(R.MinimumEnd(10,20,50,nil)==nil)
local w={cities={['1:1']=city(1,1)},routes={},changes={
 {ready=2,city='1:1',field='properties',key='P',value=1},
 {ready=2,city='1:1',field='properties',key='P',value=0}}}
assert(R.Forecast(w,D,1,10)==nil)
''')

    def test_gameplay_start_turn_qualifies_current_policy_window_without_mutating_ui_facts(self):
        self.vm().execute('''
local info={GlobalParameters={TRADE_ROUTE_TURN_DURATION_BASE={Value=20}},
 GameSpeeds={ONLINE={CostMultiplier=50}},Eras={[1]={EraType='ERA_MEDIEVAL'}},
 Eras_XP2={ERA_MEDIEVAL={Index=88,TradeRouteMinimumEndTurnChange=10}}}
local started,operation=5,-2089494188
local unit={GetOperationType=function()return operation end,GetOperationParameter=function()return started end}
local players={[1]={GetUnits=function()return{FindID=function()return unit end}end}}
local game={GetCurrentGameTurn=function()return 10 end,GetEras=function()return{GetCurrentEra=function()return 1 end}end}
local config={GetGameSpeedType=function()return'ONLINE'end}
local enums={MAKE_TRADE_ROUTE=0x8374d954,PARAM_TURN=0xa783eab4}
local facts={version=1,turn=9,cities={},routes={{origin='1:1',destination='2:2',native={TraderUnitPlayer=1,TraderUnitID=9}}}}
local q=CSC_TradeRouteFacts.QualifyWindows(facts,info,game,config,players,enums)
assert(q.durationStats.qualified==1 and q.routes[1].nativeStartTurn==5)
assert(q.routes[1].currentPolicyEarliestEnd==20 and q.routes[1].observedThrough==10)
assert(facts.routes[1].observedThrough==nil and q.turn==9 and q.durationTurn==10)
started=0
q=CSC_TradeRouteFacts.QualifyWindows(facts,info,game,config,players,enums)
assert(q.routes[1].currentPolicyEarliestEnd==15 and q.routes[1].observedThrough==5)
started=50
q=CSC_TradeRouteFacts.QualifyWindows(facts,info,game,config,players,enums)
assert(q.durationStats.unknown==1 and q.routes[1].observedThrough==1)
started=5;operation=0
q=CSC_TradeRouteFacts.QualifyWindows(facts,info,game,config,players,enums)
assert(q.durationStats.unknown==1)
operation=-2089494188;started=10
q=CSC_TradeRouteFacts.QualifyWindows(facts,info,game,config,players,enums)
assert(q.durationStats.unknown==1 and q.routes[1].observedThrough==1) -- New operation after observed endpoints.
started=5;facts.turn=8
q=CSC_TradeRouteFacts.QualifyWindows(facts,info,game,config,players,enums)
assert(q.durationStats.unknown==1) -- Older than the UI/Gameplay phase allowance.
facts.turn=11
q=CSC_TradeRouteFacts.QualifyWindows(facts,info,game,config,players,enums)
assert(q.durationStats.unknown==1) -- Future packet.
facts.turn=9
operation=-2089494188;config.GetGameSpeedType=function()error('No context')end
q=CSC_TradeRouteFacts.QualifyWindows(facts,info,game,config,players,enums)
assert(q.durationStats.unknown==1 and q.routes[1].observedThrough==1)
''')


if __name__=='__main__':unittest.main()
