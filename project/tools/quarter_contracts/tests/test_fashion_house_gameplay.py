"""Execute the Fashion House production Lua against controlled game API state."""
from pathlib import Path
import re
import unittest
from lupa import LuaRuntime

ROOT=Path(__file__).resolve().parents[4]
FIXTURES=Path(__file__).with_name('fixtures')
LUA=ROOT/'Civ Supply Chains/Lua_UI'

class FashionWorld(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        for filename in ('cafe_stage4_world.lua','fashion_house_world.lua'):
            self.lua.execute((FIXTURES/filename).read_text())
        self.lua.execute("""
            seller=addCity(1,15);customer=addCity(2,5);
            addDistrict(seller,'DISTRICT_CSC_TAILORS_QUARTER',0,0);
            addBuilding(seller,'BUILDING_CSC_TAILORS_FASHION_HOUSE');
            addDistrict(customer,'DISTRICT_THEATER',1,0);
            addBuilding(customer,'BUILDING_AMPHITHEATER');
        """)

    def load(self, path): self.lua.execute((LUA/path).read_text(encoding='utf-8-sig'))
    def eval(self, expression): return self.lua.eval(expression)
    def execute(self, text): self.lua.execute(text)
    def stacks(self, city, branch='FASHION_HOUSE_RETURN'):
        prop='CSC_TAILORS_STAGE_4_'+branch
        amount=self.eval(f"{city}:GetProperty('{prop}') or 0")
        for scope in (city,city+'.center'):
            self.assertEqual(self.eval(f"{scope}:GetProperty('{prop}') or 0"),amount)
            self.assertEqual(sum(bit*self.eval(f"{scope}:GetProperty('{prop}_BIT_{bit}') or 0") for bit in (1<<i for i in range(20))),amount)
        return amount

class FashionPopulationTests(FashionWorld):
    def setUp(self):
        super().setUp();self.load('CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua')
    def refresh(self):self.lua.globals().CSC_RefreshCustomerPopulationReturns()

    def test_customer_threshold_controls_both_sides(self):
        for pop,expected in ((4,0),(5,1),(9,1),(10,2),(55,11),(1280,256)):
            with self.subTest(population=pop):
                self.execute(f'customer.population={pop};seller.population=40');self.refresh()
                self.assertEqual(self.stacks('seller'),expected)
                self.assertEqual(self.stacks('customer','AMPHITHEATER_CULTURE_RETURN'),expected)
        self.execute('customer.population=15;seller.population=5');self.refresh()
        self.assertEqual(self.stacks('seller'),3)

    def test_each_wonder_site_and_amphitheater_stack_independently(self):
        self.execute("""
            addWonder(customer,'BUILDING_BOLSHOI_THEATRE',0,1);
            addWonder(customer,'BUILDING_BROADWAY',-1,1);
            addWonder(customer,'BUILDING_SYDNEY_OPERA_HOUSE',-1,0);
            customer.population=10;
        """);self.refresh()
        self.assertEqual(self.stacks('seller'),8)
        for branch in ('AMPHITHEATER','BOLSHOI','BROADWAY','SYDNEY'):
            self.assertEqual(self.stacks('customer',branch+'_CULTURE_RETURN'),2)
        self.execute("customer.pillagedBuildings[GameInfo.Buildings.BUILDING_BROADWAY.Index]=true");self.refresh()
        self.assertEqual(self.stacks('seller'),6)
        self.assertEqual(self.stacks('customer','BROADWAY_CULTURE_RETURN'),0)

    def test_rounds_two_cities_before_summing(self):
        self.execute("""
            customer.population=9;second=addCity(3,9);
            addWonder(second,'BUILDING_BROADWAY',0,1);
        """);self.refresh()
        self.assertEqual(self.stacks('seller'),2)
        self.assertEqual(self.stacks('second','BROADWAY_CULTURE_RETURN'),1)

    def test_multiple_sellers_and_same_city_replacement(self):
        self.execute("""
            other=addCity(3,2);addDistrict(other,'DISTRICT_CSC_TAILORS_QUARTER',2,0);
            addBuilding(other,'BUILDING_CSC_TAILORS_FASHION_HOUSE');
            addDistrict(seller,'DISTRICT_THEATER',0,1);addBuilding(seller,'BUILDING_MARAE');
        """);self.refresh()
        self.assertEqual(self.stacks('seller'),4)
        self.assertEqual(self.stacks('other'),1)
        self.assertEqual(self.stacks('customer','AMPHITHEATER_CULTURE_RETURN'),2)
        self.assertEqual(self.stacks('seller','AMPHITHEATER_CULTURE_RETURN'),3)

    def test_loss_clears_raw_and_bits(self):
        for change in ("customer.owner=1","customer.buildings={}","seller.buildings={}","customer.pillagedDistricts[6]=true","seller.pillagedDistricts[5]=true"):
            with self.subTest(change=change):
                self.setUp();self.assertEqual(self.stacks('seller'),1)
                self.execute(change);self.refresh()
                self.assertEqual(self.stacks('seller'),0)
                self.assertEqual(self.stacks('customer','AMPHITHEATER_CULTURE_RETURN'),0)

class WonderPlacementTests(FashionWorld):
    def setUp(self):
        super().setUp()
        self.execute("""
            addWonder(customer,'BUILDING_BROADWAY',0,1);
            addWonder(customer,'BUILDING_BOLSHOI_THEATRE',-1,1);
            addWonder(customer,'BUILDING_SYDNEY_OPERA_HOUSE',-1,0);
        """);self.load('WonderServices/CSC_WonderServicePlacement.lua')
    def refresh(self):self.lua.globals().CSC_RefreshWonderServices()
    def active(self):
        self.execute("hasOpera=true;seller:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',1)");self.refresh()
    def present(self,suffix):return self.eval(f"customer:GetBuildings():HasBuilding(GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_{suffix}.Index)")
    def test_native_unset_properties_can_return_no_values(self):
        self.execute("""
            for _,city in ipairs(fashionCities) do
                city.properties={};
                city.GetProperty=function(self,key)
                    if self.properties[key]~=nil then return self.properties[key];end;
                end;
            end;
            for _,xy in ipairs({{0,1},{-1,1},{-1,0}}) do
                local plot=Map.GetPlot(xy[1],xy[2]);plot.properties={};
                plot.GetProperty=function(self,key)
                    if self.properties[key]~=nil then return self.properties[key];end;
                end;
            end;
            capturedPrints={};
        """)
        self.refresh();self.assertFalse(self.present('BROADWAY'))
        self.active();self.assertTrue(self.present('BROADWAY'))
        self.assertEqual(self.eval('#capturedPrints'),0)

    def test_city_collections_not_available_during_startup(self):
        self.execute("savedGetCities=Players[0].GetCities;Players[0].GetCities=function()end;capturedPrints={}")
        self.load('WonderServices/CSC_WonderServicePlacement.lua')
        self.assertEqual(self.eval('#capturedPrints'),0)
        self.execute('Players[0].GetCities=savedGetCities')
        self.active();self.assertTrue(self.present('BROADWAY'))

    def test_player_without_city_collection_does_not_block_other_players(self):
        self.execute("""
            Players[1]={GetID=function()return 1;end,GetCities=function()end};
            PlayerManager.GetWasEverAliveCount=function()return 2;end;
            PlayerManager.GetAlive=function()return {Players[1],Players[0]};end;
        """)
        self.active()
        for venue in ('BOLSHOI','BROADWAY','SYDNEY'):
            self.assertTrue(self.present(venue))
        self.assertEqual(self.eval('#capturedPrints'),0)

    def test_player_count_is_not_an_id_range(self):
        self.execute("""
            Players[5]=Players[0];Players[0]=nil;
            Players[5].GetID=function()return 5;end;
            for _,city in ipairs(fashionCities)do city.owner=5;end;
            PlayerManager.GetWasEverAliveCount=function()return 1;end;
            PlayerManager.GetAlive=function()return {Players[5]};end;
        """)
        self.active()
        for venue in ('BOLSHOI','BROADWAY','SYDNEY'):
            self.assertTrue(self.present(venue))
        self.assertEqual(self.eval('#capturedPrints'),0)

    def test_native_gameplay_district_pillage_api(self):
        self.execute("""
            local base=seller.GetDistricts;
            seller.GetDistricts=function(self)
                local districts=base(self);districts.IsPillaged=nil;return districts;
            end;
        """)
        self.active();self.assertTrue(self.present('BOLSHOI'))
        self.execute("seller.pillagedDistricts[GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index]=true")
        self.refresh()
        self.assertEqual(self.eval("customer:GetProperty('CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_READY')"),0)
        self.assertTrue(self.present('BOLSHOI'))
        self.assertEqual(self.eval('#capturedPrints'),0)

    def test_supply_and_civic_gates_then_correct_multiple_wonder_placement(self):
        self.assertFalse(self.present('BROADWAY'))
        self.execute("hasOpera=true");self.refresh();self.assertFalse(self.present('BROADWAY'))
        self.active()
        for suffix,host in (('BROADWAY','BUILDING_BROADWAY'),('BOLSHOI','BUILDING_BOLSHOI_THEATRE'),('SYDNEY','BUILDING_SYDNEY_OPERA_HOUSE')):
            self.assertTrue(self.present(suffix))
            self.assertEqual(self.eval(f"customer:GetBuildings():GetBuildingLocation(GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_{suffix}.Index)"),self.eval(f"customer:GetBuildings():GetBuildingLocation(GameInfo.Buildings.{host}.Index)"))
        self.assertEqual(self.eval('#placementCalls'),3)
        self.refresh();self.assertEqual(self.eval('#placementCalls'),3)
        self.assertEqual(self.eval('#capturedPrints'),0)

    def test_persistent_service_repair_reload_and_orphan_removal(self):
        self.active()
        self.execute("seller:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',0)");self.refresh()
        self.assertTrue(self.present('BROADWAY'))
        self.assertEqual(self.eval("customer:GetProperty('CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_READY')"),0)
        self.execute("customer.locations[GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY.Index]=customer.center:GetIndex()")
        self.refresh()
        self.assertEqual(self.eval('customer.locations[GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY.Index]'),self.eval('customer.locations[GameInfo.Buildings.BUILDING_BROADWAY.Index]'))
        self.execute("customer:GetBuildings():RemoveBuilding(GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY.Index)")
        self.load('WonderServices/CSC_WonderServicePlacement.lua');self.assertTrue(self.present('BROADWAY'))
        self.execute("customer:GetBuildings():RemoveBuilding(GameInfo.Buildings.BUILDING_BROADWAY.Index)");self.refresh()
        self.assertFalse(self.present('BROADWAY'))
        self.assertEqual(self.eval("Map.GetPlot(0,1):GetProperty('CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_READY')"),0)

    def test_wrong_owner_or_pillaged_seller_cannot_establish(self):
        self.execute("hasOpera=true;seller:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',1);customer.owner=1")
        self.refresh();self.assertFalse(self.present('BROADWAY'))
        self.execute("customer.owner=0;seller.pillagedBuildings[GameInfo.Buildings.BUILDING_CSC_TAILORS_FASHION_HOUSE.Index]=true")
        self.refresh();self.assertFalse(self.present('BROADWAY'))

class WonderPresentationTests(FashionWorld):
    def setUp(self):
        super().setUp()
        self.execute("""
            addWonder(customer,'BUILDING_BROADWAY',0,1);
            addWonder(customer,'BUILDING_BOLSHOI_THEATRE',-1,1);
            addWonder(customer,'BUILDING_SYDNEY_OPERA_HOUSE',-1,0);
        """)
        self.load('WonderServices/CSC_WonderServicePlacement.lua')
        self.lua.execute((FIXTURES/'wonder_service_presentation.lua').read_text())
        for filename in ('Suk_MCUIS_CSC.lua','CSC_UI_Notifications.lua'):
            source=(LUA/'Notifications_Suk_MCUIS'/filename).read_text(encoding='utf-8-sig')
            # Civ's Lua accepts typed local declarations; stock Lua does not.
            self.lua.execute(re.sub(r'\s*:\s*(?:number|string|boolean|table)\b','',source))
        self.execute('OnSuk_MCUIS_RequestRegistration(registration)')

    def query(self,venue=''):
        suffix='_'+venue if venue else ''
        self.execute(f"OnSuk_MCUIS_QueryIcon('City','CSC_ActiveModifiers_MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM{suffix}',icon)")

    def test_venue_icons_and_notification_streams_remain_separate(self):
        self.assertEqual(self.eval('#registeredIcons'),4)
        self.query();self.assertFalse(self.eval('icon.make'))
        self.execute("hasOpera=true;seller:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',1);CSC_RefreshWonderServices();OnRefreshCityQuarters()")
        for venue in ('','BOLSHOI','BROADWAY','SYDNEY'):
            suffix='_'+venue if venue else ''
            self.query(venue);self.assertTrue(self.eval('icon.make'))
            self.assertEqual(self.eval('icon.image'),'ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE'+suffix)
            self.assertEqual(self.eval('icon.description'),'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION'+suffix+'|+2|+1|1')
        self.assertEqual(self.eval('#notifications'),4)
        self.execute('CSC_RefreshWonderServices();OnRefreshCityQuarters()')
        self.assertEqual(self.eval('#notifications'),4)
        self.execute("customer.pillagedBuildings[GameInfo.Buildings.BUILDING_BROADWAY.Index]=true;CSC_RefreshWonderServices();OnRefreshCityQuarters()")
        self.assertEqual(self.eval('#notifications'),5)
        self.assertEqual(self.eval('notifications[5].kind'),'NOTIFICATION_CSC_TAILORS_EFFECT_REMOVED')
        self.query('BROADWAY');self.assertFalse(self.eval('icon.make'))
        self.query('BOLSHOI');self.assertTrue(self.eval('icon.make'))
        self.execute("seller:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',0);CSC_RefreshWonderServices();OnRefreshCityQuarters()")
        self.assertEqual(self.eval('#notifications'),8)
        self.query();self.assertFalse(self.eval('icon.make'))
        self.assertTrue(self.eval('customer:GetBuildings():HasBuilding(GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY.Index)'))
        self.execute("customer.pillagedBuildings={};seller:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',1);CSC_RefreshWonderServices();OnRefreshCityQuarters()")
        self.assertEqual(self.eval('#notifications'),12)

    def test_two_seller_cities_stack_within_one_venue(self):
        self.execute("""
            hasOpera=true;seller:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',1);
            other=addCity(3,10);addDistrict(other,'DISTRICT_CSC_TAILORS_QUARTER',0,2);
            addBuilding(other,'BUILDING_CSC_TAILORS_FASHION_HOUSE');
            presentationSellers[2]={City=other,Venues={BROADWAY=true}};
            CSC_RefreshWonderServices();OnRefreshCityQuarters();
            other:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',1);
            CSC_RefreshWonderServices();OnRefreshCityQuarters();
        """)
        self.query('BROADWAY');self.assertIn('|+4|+2|2',self.eval('icon.description'))
        self.assertEqual(self.eval('#notifications'),5)
        self.assertEqual(self.eval('notifications[5].kind'),'NOTIFICATION_CSC_TAILORS_EFFECT_INCREASED')
        self.execute("seller:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',0);CSC_RefreshWonderServices();OnRefreshCityQuarters()")
        self.query('BROADWAY');self.assertIn('|+2|+1|1',self.eval('icon.description'))
        self.assertTrue(self.eval("customer:GetProperty('CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_READY')==1"))
        self.assertEqual(self.eval('#notifications'),9)
        self.assertEqual(self.eval("(function()for i=6,9 do if notifications[i].kind=='NOTIFICATION_CSC_TAILORS_EFFECT_DECREASED' then return notifications[i].data.summary;end;end;end)()"),'LOC_NOTIFICATION_HENNO_DECREASED_CITY_QUARTER_ABILITY_SUMMARY|City2|LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BROADWAY_DECREASED|-2|-1|1')
        self.execute('CSC_RefreshWonderServices();OnRefreshCityQuarters()')
        self.assertEqual(self.eval('#notifications'),9)


class FashionTradeTests(FashionWorld):
    def setUp(self):
        super().setUp()
        self.execute("""
            addBuilding(seller,'BUILDING_CSC_TAILORS_TAILOR');
            seller:SetProperty('CSC_TAILORS_TAILOR_SUPPLIED',1);
            seller:SetProperty('CSC_TAILORS_FASHION_HOUSE_SUPPLIED',1);
            customer.routes={{DestinationCityPlayer=0,DestinationCityID=1}};
        """)
        self.load('TradeRoutes/CSC_TradeRouteInteractions_Gameplay.lua')
        self.load('TradeRoutes/CSC_TradeRouteInteractions.lua')
    def refresh(self):self.lua.globals().CSC_RefreshBakersTradeRouteProperties()
    def test_tailor_and_fashion_route_channels_stack_and_clear(self):
        self.assertEqual(self.eval("customer:GetProperty('CSC_TAILORS_IMPORT_TAILOR_ROUTE')"),1)
        self.assertEqual(self.eval("customer:GetProperty('CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE')"),1)
        self.assertEqual(self.eval("seller.center:GetProperty('CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1')"),1)
        self.execute("seller.pillagedBuildings[GameInfo.Buildings.BUILDING_CSC_TAILORS_FASHION_HOUSE.Index]=true");self.refresh()
        self.assertEqual(self.eval("customer.center:GetProperty('CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE')"),0)
        self.assertEqual(self.eval("customer.center:GetProperty('CSC_TAILORS_IMPORT_TAILOR_ROUTE')"),1)
        self.execute('customer.routes={}');self.refresh()
        self.assertEqual(self.eval("seller.center:GetProperty('CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1')"),0)

    def test_multiple_routes_and_origin_quarter_exclusion(self):
        self.execute('customer.routes[2]=customer.routes[1]');self.refresh()
        self.assertEqual(self.eval("seller:GetProperty('CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE')"),2)
        self.assertEqual(self.eval("seller:GetProperty('CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_2')"),1)
        self.execute("addDistrict(customer,'DISTRICT_CSC_TAILORS_QUARTER',3,0)");self.refresh()
        self.assertEqual(self.eval("seller:GetProperty('CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE')"),0)
        self.assertEqual(self.eval("customer:GetProperty('CSC_TAILORS_IMPORT_TAILOR_ROUTE')"),0)

    def test_bts_preview_counts_two_yields_and_two_amenities(self):
        self.load('TradeRoutes/CSC_BTS_TradeRoutePreviewSupport.lua')
        self.execute("""
            route={OriginCityPlayer=0,OriginCityID=2,DestinationCityPlayer=0,DestinationCityID=1};
            yields={};tooltips={};CSC_BTS_ApplyBakersTradeRoutePreview(route,yields,tooltips,true,'Origin');
        """)
        self.assertEqual(self.eval('yields[CULTURE_INDEX]'),2)
        self.assertEqual(self.eval('CSC_BTS_GetQuarterImportAmenityAmount(route)'),2)
        self.execute("yields={};CSC_BTS_ApplyBakersTradeRoutePreview(route,yields,{},false,'Destination')")
        self.assertEqual(self.eval('yields[PRODUCTION_INDEX]'),2)
        self.assertEqual(self.eval('yields[GOLD_INDEX]'),2)

if __name__=='__main__':unittest.main()
