"""Cross-owner CSC payouts and UI parity; no native game connection."""
from pathlib import Path
import re
import sqlite3
import unittest

from test_multiplayer_hardening import world, load

ROOT = Path(__file__).resolve().parents[4]


def source_lua(text):
    return re.sub(r'\s*:\s*(?:number|table|string|boolean)\b', '', text)


class InternationalTradeTests(unittest.TestCase):
    def setUp(self):
        self.lua = world()
        self.lua.execute('''
            seller.owner=1;
            localSeller=addCity(12,10);foreignOrigin=addCity(13,10);foreignOrigin.owner=1;
            function supply(c)
                addBuilding(c,'BUILDING_CSC_TAILORS_TAILOR');
                addBuilding(c,'BUILDING_CSC_TAILORS_FASHION_HOUSE');
                for _,key in ipairs({'CSC_BAKERS_BAKERY_SUPPLIED','CSC_BAKERS_CAFE_SUPPLIED',
                    'CSC_TAILORS_TAILOR_SUPPLIED','CSC_TAILORS_FASHION_HOUSE_SUPPLIED'}) do
                    c.properties[key]=1;
                end;
            end;
            supply(seller);supply(localSeller);
            function player(id)
                return {GetID=function()return id;end,
                    GetTrade=function()return {GetInternationalYieldModifier=function()return 2;end};end,
                    GetCities=function()
                        return {FindID=function(_,cityID)
                            for _,c in ipairs(fashionCities)do if c.owner==id and c.id==cityID then return c;end;end;
                        end,Members=function()
                            local i=0;return function()
                                repeat i=i+1 until not fashionCities[i]or fashionCities[i].owner==id;
                                if fashionCities[i]then return i,fashionCities[i];end;
                            end;
                        end};
                    end};
            end;
            Players[0]=player(0);Players[1]=player(1);
            PlayerManager.GetAlive=function()return {Players[0],Players[1]};end;
            domestic={OriginCityPlayer=0,OriginCityID=2,DestinationCityPlayer=0,DestinationCityID=12};
            international={OriginCityPlayer=0,OriginCityID=2,DestinationCityPlayer=1,DestinationCityID=9};
            customer.routes={domestic,international};
            foreignOrigin.routes={{DestinationCityPlayer=0,DestinationCityID=12}};
            include=function()end;
        ''')
        load(self.lua, 'TradeRoutes/CSC_TradeRouteInteractions_Gameplay.lua')
        load(self.lua, 'TradeRoutes/CSC_TradeRouteInteractions.lua')

    def test_cross_owner_routes_pay_both_players_and_stack_with_domestic_routes(self):
        lua = self.lua
        lua.execute('Events.TradeRouteActivityChanged.Fire();routeUpdate(0)')
        self.assertTrue(lua.eval('(function()for _,q in ipairs(queue)do if q.sender~=0 then return false;end;end;return true;end)()'))
        self.assertTrue(lua.eval('(function()for _,q in ipairs(queue)do if q.params.CityPlayerID==1 then return true;end;end;return false;end)()'))
        lua.execute('deliver()')
        for channel in ('CSC_BAKERS_IMPORT_CONSUMER', 'CSC_BAKERS_IMPORT_SPECIALTY',
                        'CSC_TAILORS_IMPORT_TAILOR', 'CSC_TAILORS_IMPORT_FASHION_HOUSE'):
            self.assertEqual(lua.eval(f"customer:GetProperty('{channel}_ROUTE')"), 2)
            self.assertEqual(lua.eval(f"customer:GetProperty('{channel}_ROUTE_BIT_2')"), 1)
            self.assertEqual(lua.eval(f"foreignOrigin:GetProperty('{channel}_ROUTE')"), 1)
        for channel in ('CSC_BAKERS_EXPORT_BAKERY', 'CSC_BAKERS_EXPORT_CAFE',
                        'CSC_TAILORS_EXPORT_TAILOR', 'CSC_TAILORS_EXPORT_FASHION_HOUSE'):
            self.assertEqual(lua.eval(f"seller:GetProperty('{channel}_ROUTE_BIT_1')"), 1)
            self.assertEqual(lua.eval(f"localSeller:GetProperty('{channel}_ROUTE_BIT_2')"), 1)
        lua.execute('customer.routes={domestic};Events.TradeRouteActivityChanged.Fire();routeUpdate(0);deliver()')
        self.assertEqual(lua.eval("seller:GetProperty('CSC_BAKERS_EXPORT_BAKERY_ROUTE')"), 0)
        self.assertEqual(lua.eval("customer:GetProperty('CSC_BAKERS_IMPORT_CONSUMER_ROUTE')"), 1)

    def test_bts_native_getters_keep_csc_amounts_equal_despite_international_multiplier(self):
        lua = self.lua
        load(lua, 'TradeRoutes/CSC_BTS_TradeRoutePreviewSupport.lua')
        lua.execute('''
            GameInfo.Yields={};
            for i,name in ipairs({'FOOD','PRODUCTION','GOLD','SCIENCE','CULTURE','FAITH'})do
                GameInfo.Yields[i-1]={Name=name,IconString='[ICON_'..name..']'};
            end;
            Game.GetTradeManager=function()return setmetatable({}, {__index=function()
                return function()return {1,1,1,1,1,1};end;
            end});end;
            GetDestinationCityName=function()return 'Destination';end;
            CSC_BTS_FormatSignedTooltipAmount=tostring;
        ''')
        text = (ROOT / 'Civ Supply Chains/Lua_UI/TradeRoutes/TradeSupport.lua').read_text(encoding='utf-8-sig')
        getters = text[text.index('function GetYieldsForOriginCity('):text.index('function GetYieldForOriginCity(')]
        lua.execute(source_lua(getters))
        for route, native in (('domestic', 3), ('international', 6)):
            lua.execute(f"oy,ot=GetYieldsForOriginCity({route},true,false);dy,dt=GetYieldsForDestinationCity({route},true,false)")
            self.assertEqual(lua.eval('oy[FOOD_INDEX]') - native, 2)
            self.assertEqual(lua.eval('oy[CULTURE_INDEX]') - native, 2)
            self.assertEqual(lua.eval('dy[PRODUCTION_INDEX]') - native, 4)
            self.assertEqual(lua.eval('dy[GOLD_INDEX]') - native, 4)
            self.assertEqual(lua.eval(f'CSC_BTS_GetQuarterImportAmenityAmount({route})'), 4)
            self.assertIn('+2 [ICON_Food]', lua.eval('ot[FOOD_INDEX]'))
            self.assertIn('+2 [ICON_Culture]', lua.eval('ot[CULTURE_INDEX]'))
            self.assertIn('+4 [ICON_Gold]', lua.eval('dt[GOLD_INDEX]'))
            self.assertIn('4 [ICON_Amenities]', lua.eval('ot[FAITH_INDEX]'))

    def test_unit_panel_and_preview_keep_origin_exclusions_for_foreign_routes(self):
        lua = self.lua
        load(lua, 'TradeRoutes/CSC_BTS_TradeRoutePreviewSupport.lua')
        text = (ROOT / 'Civ Supply Chains/Lua_UI/TradeRoutes/UnitPanel.lua').read_text(encoding='utf-8-sig')
        lua.execute(source_lua(text[:text.index('local ANIMATION_SPEED')]))
        for target in ('seller', 'localSeller'):
            self.assertEqual(lua.eval(f'CSC_UnitPanel_GetBakersTradeRouteCount(customer,{target})'), 2)
            self.assertEqual(lua.eval(f'CSC_UnitPanel_GetTailorsTradeRouteCount(customer,{target})'), 2)
        lua.execute("addDistrict(customer,'DISTRICT_CSC_BAKERS_QUARTER',1,0)")
        self.assertEqual(lua.eval('CSC_UnitPanel_GetBakersTradeRouteCount(customer,seller)'), 0)
        self.assertEqual(lua.eval('CSC_BTS_GetBakersTradeRouteState(international)'), (False, False))
        self.assertEqual(lua.eval('CSC_GetBakersTradeRouteState(customer,seller)'), (False, False))
        self.assertEqual(lua.eval('CSC_UnitPanel_GetTailorsTradeRouteCount(customer,seller)'), 2)
        lua.execute('seller.properties.CSC_TAILORS_TAILOR_SUPPLIED=0;seller.properties.CSC_TAILORS_FASHION_HOUSE_SUPPLIED=0')
        self.assertEqual(lua.eval('CSC_UnitPanel_GetTailorsTradeRouteCount(customer,seller)'), 0)
        self.assertEqual(lua.eval('CSC_BTS_GetTailorsTradeRouteState(international)'), (False, False))
        self.assertEqual(lua.eval('CSC_GetTailorsTradeRouteState(customer,seller)'), (False, False))

    def test_suia_reclassifies_domestic_and_foreign_imports_together_without_changing_total(self):
        lua = self.lua
        lua.execute('CSC_RefreshBakersTradeRouteProperties();deliver()')
        c = sqlite3.connect(':memory:')
        c.executescript('CREATE TABLE CSC_RouteStackBits(Bit INTEGER);INSERT INTO CSC_RouteStackBits VALUES(2),(4),(8),(16);')
        c.executescript((ROOT / 'Civ Supply Chains/ModSupport/ModSupport_SUIA.sql').read_text())
        columns = [column[1] for column in c.execute('PRAGMA table_info(CSC_TradeRouteYieldPresentation)')]
        rows = [dict(zip(columns, row)) for row in c.execute('SELECT * FROM CSC_TradeRouteYieldPresentation')]
        lua.globals().presentationRows = lua.table_from([lua.table_from(row) for row in rows])
        lua.execute('''
            GameInfo.CSC_TradeRouteYieldPresentation=function()
                local i=0;return function()i=i+1;return presentationRows[i];end;
            end;
            UI.GetHeadSelectedCity=function()return customer;end;
            TTManager={GetTypeControlTable=function()end};
            InstanceManager={new=function()return {};end};
            Locale.Lookup=function(key,arg)
                local label=key=='LOC_CITY_YIELD_FROM_GAMEEFFECTS_TOOLTIP'and 'from Modifiers'or 'from Outgoing Trade Routes';
                return tostring(arg.Value)..' '..label;
            end;
            Locale.ToNumber=function(value)return tostring(value);end;
        ''')
        text = (ROOT / 'Civ Supply Chains/UI/Common/Additions/Suk_YieldTT.lua').read_text(encoding='utf-8-sig')
        helpers = text[:text.index('local sTooltip_Base_Cache')]
        api = lua.execute(helpers + '\nreturn {amount=CSC_GetOutgoingRouteYieldAmount,reclassify=CSC_ReclassifyOutgoingRouteYield}')
        for name in ('Food', 'Culture'):
            amount = api.amount(name)
            self.assertEqual(amount, 4)  # Two channels on each of two distinct routes.
            entries = lua.table_from([lua.table_from(['7', '', 'from Modifiers']), lua.table_from(['3', '', 'from Outgoing Trade Routes'])])
            api.reclassify(entries, amount)
            self.assertEqual(float(entries[1][1]), 3)
            self.assertEqual(float(entries[2][1]), 7)


if __name__ == '__main__':
    unittest.main()
