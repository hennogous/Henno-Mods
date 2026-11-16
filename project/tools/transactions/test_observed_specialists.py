"""Actual citizen-yield SQL -> production Facts/Model; only staffing is a fixture."""
import unittest
from test_material_fact_path import world


class ObservedSpecialists(unittest.TestCase):
    def test_bakery_uses_observed_workers_and_excludes_service_building_rates(self):
        vm=world()
        vm.execute('''
local bakery=GameInfo.Buildings.BUILDING_CSC_BAKERS_BAKERY
-- The reduced schema fixture omits non-economic building definitions; its
-- Service citizen-yield rows were still loaded from the real gameplay SQL.
local service={Index=999,BuildingType='BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER'}
GameInfo.Buildings[service.BuildingType]=service;GameInfo.Buildings[service.Index]=service
EXTRA_BUILDINGS={[bakery.Index]=true,[service.Index]=true}
for workers=0,2 do
 QUARTER_WORKERS=workers
 local r,s=evaluate()
 assert(s.specialists.workers==workers and s.specialists.base.YIELD_FOOD==2)
 assert(s.specialists.base.YIELD_CULTURE==nil and s.specialists.base.YIELD_GOLD==nil)
 local actual=0
 for _,flow in ipairs(r.streams)do if flow.id=='specialist-base:YIELD_FOOD'then
  actual=actual+flow.amount;assert(flow.city==1 and flow.ready==0)
 end end
 assert(actual==2*workers)
end
''')

    def test_intrinsic_tailor_specialist_gold_survives_transaction_gold_off(self):
        vm=world(quarter='TAILORS',host='IMPROVEMENT_RES2_SAWMILL',gold=False)
        vm.execute('''
local tailor=GameInfo.Buildings.BUILDING_CSC_TAILORS_TAILOR
EXTRA_BUILDINGS={[tailor.Index]=true};QUARTER_WORKERS=2
local r,s=evaluate()
assert(s.specialists.base.YIELD_CULTURE==2 and s.specialists.base.YIELD_GOLD==1)
local culture,gold=0,0
for _,flow in ipairs(r.streams)do
 if flow.id=='specialist-base:YIELD_CULTURE'then culture=flow.amount end
 if flow.id=='specialist-base:YIELD_GOLD'then gold=flow.amount end
end
assert(culture==4 and gold==2)
''')

    def test_missing_building_changes_existing_workers_but_does_not_create_staffing(self):
        vm=world()
        vm.execute('''
local bakery=GameInfo.Buildings.BUILDING_CSC_BAKERS_BAKERY
local cafe=GameInfo.Buildings.BUILDING_CSC_BAKERS_CAFE
bakery.MustPurchase=0;cafe.MustPurchase=0
EXTRA_BUILDINGS={[bakery.Index]=true}
for workers=0,2 do
 QUARTER_WORKERS=workers
 local r,s=evaluate();local culture=0
 for _,flow in ipairs(r.streams)do
  if flow.id=='specialist-building:BUILDING_CSC_BAKERS_CAFE:YIELD_CULTURE'then
   culture=culture+flow.amount;assert(flow.ready>0 and flow.city==1)
  end
 end
 assert(culture==workers)
end
''')

    def test_missing_receiving_city_earns_no_assumed_specialist_income(self):
        vm=world()
        vm.execute('''
local bakery=GameInfo.Buildings.BUILDING_CSC_BAKERS_BAKERY
EXTRA_BUILDINGS={[bakery.Index]=true};QUARTER_WORKERS=1;UI_LAG=2
local r,s=evaluate()
assert(s.specialists==nil)
for _,flow in ipairs(r.streams)do assert(not flow.id:find('specialist-',1,true))end
''')

    def test_present_pillaged_building_rate_is_not_added_again_as_future_income(self):
        vm=world()
        vm.execute('''
local bakery=GameInfo.Buildings.BUILDING_CSC_BAKERS_BAKERY
local cafe=GameInfo.Buildings.BUILDING_CSC_BAKERS_CAFE
bakery.MustPurchase=0;cafe.MustPurchase=0
EXTRA_BUILDINGS={[bakery.Index]=true,[cafe.Index]=true};QUARTER_WORKERS=1
city:GetBuildings().IsPillaged=function(_,id)return id==bakery.Index end
local r,s=evaluate()
assert(s.specialists.presentBuildings[bakery.BuildingType])
assert(s.specialists.base.YIELD_FOOD==3 and s.specialists.base.YIELD_CULTURE==1)
for _,flow in ipairs(r.streams)do assert(not flow.id:find('specialist-building:',1,true))end
''')


if __name__=='__main__':unittest.main()
