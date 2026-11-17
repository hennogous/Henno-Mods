"""Shared definitions drive gameplay eligibility and both route UI consumers."""
import sys
import unittest
from pathlib import Path
from test_multiplayer_hardening import world,load

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'project/tools/transactions'))
from route_fixture import bind
from population_catalogue_fixture import compile_catalogue,MOD


class SharedRoutePreviews(unittest.TestCase):
    def setup(self,*,gold=True,database=None):
        vm=world();bind(vm,gold=gold,database=database)
        vm.execute('''
FOOD_INDEX=0;PRODUCTION_INDEX=1;GOLD_INDEX=2;SCIENCE_INDEX=3;CULTURE_INDEX=4;FAITH_INDEX=5
for _,name in ipairs({'BUILDING_CSC_BAKERS_BAKERY','BUILDING_CSC_BAKERS_CAFE',
 'BUILDING_CSC_TAILORS_TAILOR','BUILDING_CSC_TAILORS_FASHION_HOUSE'})do addBuilding(seller,name)end
for _,channel in ipairs(CSC_ROUTE_TEST_ROWS.CSC_TradeRouteChannelFacts)do seller.properties[channel.SupplyProperty]=1 end
route={OriginCityPlayer=0,OriginCityID=2,DestinationCityPlayer=0,DestinationCityID=9}
''')
        load(vm,'TradeRoutes/CSC_BTS_TradeRoutePreviewSupport.lua')
        text=(MOD/'Lua_UI/TradeRoutes/UnitPanel.lua').read_text(encoding='utf-8-sig')
        import re
        vm.execute(re.sub(r'\s*:\s*(?:number|table|string|boolean)\b','',text[:text.index('local ANIMATION_SPEED')]))
        return vm

    def test_gold_off_and_intact_source_gates_match_both_previews(self):
        vm=self.setup(gold=False)
        vm.execute('''
local d={};CSC_BTS_ApplyBakersTradeRoutePreview(route,d,{},false,'Destination')
assert(d[PRODUCTION_INDEX]==4 and(d[GOLD_INDEX]or 0)==0)
seller.pillagedBuildings[GameInfo.Buildings.BUILDING_CSC_TAILORS_TAILOR.Index]=true
local a,b=CSC_BTS_GetTailorsTradeRouteState(route);assert(not a and b)
assert(CSC_UnitPanel_GetTailorsTradeRouteCount(customer,seller)==1)
local actual=CSC_UnitPanel_GetQuarterTradeRouteAmounts(customer,seller)
local p={};CSC_BTS_ApplyBakersTradeRoutePreview(route,p,{},false,'Origin')
assert(p[CULTURE_INDEX]==1 and actual.YIELD_CULTURE==1)
assert(p[FOOD_INDEX]==2 and actual.YIELD_FOOD==2 and actual.AMENITY==3)
''')

    def test_native_amount_change_reaches_bts_unit_panel_and_suia(self):
        db=compile_catalogue()
        db.execute("UPDATE ModifierArguments SET Value=3 WHERE ModifierId='MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD' AND Name='Amount'")
        db.executescript((MOD/'Data/CSC_Q_ALL_TradeRouteReader.sql').read_text())
        vm=self.setup(database=db)
        vm.execute('''
local p={};CSC_BTS_ApplyBakersTradeRoutePreview(route,p,{},false,'Origin')
assert(p[FOOD_INDEX]==4)
assert(CSC_UnitPanel_GetQuarterTradeRouteAmounts(customer,seller).YIELD_FOOD==4)
''')
        db.executescript((MOD/'ModSupport/ModSupport_SUIA.sql').read_text())
        self.assertEqual(db.execute("SELECT Amount FROM CSC_TradeRouteYieldPresentation WHERE ModifierId='MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD'").fetchone()[0],3)


if __name__=='__main__':unittest.main()
