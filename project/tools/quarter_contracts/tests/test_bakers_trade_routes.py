"""Execute route lifecycle, SQL payouts and SUIA classification offline."""
from pathlib import Path
import re
import sqlite3
import unittest

from test_multiplayer_hardening import world, load

ROOT = Path(__file__).resolve().parents[4]


class QuarterRouteTests(unittest.TestCase):
    def routes(self):
        lua = world()
        load(lua, 'TradeRoutes/CSC_TradeRouteInteractions_Gameplay.lua')
        load(lua, 'TradeRoutes/CSC_TradeRouteInteractions.lua')
        return lua

    def test_distinct_destinations_stack_and_supply_loss_removes_one_route(self):
        lua = self.routes()
        lua.execute('''
            other=addCity(12,10);
            seller.properties.CSC_BAKERS_BAKERY_SUPPLIED=1;
            seller.properties.CSC_BAKERS_CAFE_SUPPLIED=1;
            other.properties.CSC_BAKERS_BAKERY_SUPPLIED=1;
            customer.routes={
                {DestinationCityPlayer=0,DestinationCityID=9},
                {DestinationCityPlayer=0,DestinationCityID=12}};
            Events.TradeRouteActivityChanged.Fire();routeUpdate(0);deliver();
        ''')
        for scope in ('customer', 'Map.GetPlot(customer:GetX(),customer:GetY())'):
            self.assertEqual(lua.eval(f"{scope}:GetProperty('CSC_BAKERS_IMPORT_CONSUMER_ROUTE')"), 2)
            self.assertEqual(lua.eval(f"{scope}:GetProperty('CSC_BAKERS_IMPORT_CONSUMER_ROUTE_BIT_1')"), None)
            self.assertEqual(lua.eval(f"{scope}:GetProperty('CSC_BAKERS_IMPORT_CONSUMER_ROUTE_BIT_2')"), 1)
            self.assertEqual(lua.eval(f"{scope}:GetProperty('CSC_BAKERS_IMPORT_SPECIALTY_ROUTE_BIT_1')"), 1)
        lua.execute('other.properties.CSC_BAKERS_BAKERY_SUPPLIED=0;Events.CityPropertyChanged.Fire();routeUpdate(0);deliver()')
        self.assertEqual(lua.eval("customer:GetProperty('CSC_BAKERS_IMPORT_CONSUMER_ROUTE')"), 1)
        self.assertEqual(lua.eval("customer:GetProperty('CSC_BAKERS_IMPORT_CONSUMER_ROUTE_BIT_1')"), 1)
        self.assertEqual(lua.eval("customer:GetProperty('CSC_BAKERS_IMPORT_CONSUMER_ROUTE_BIT_2')"), 0)
        lua.execute('customer.routes={};Events.TradeRouteActivityChanged.Fire();routeUpdate(0);deliver()')
        self.assertEqual(lua.eval("customer:GetProperty('CSC_BAKERS_IMPORT_CONSUMER_ROUTE')"), 0)
        self.assertEqual(lua.eval("customer:GetProperty('CSC_BAKERS_IMPORT_SPECIALTY_ROUTE_BIT_1')"), 0)

    def test_load_screen_close_wakes_deferred_refresh_without_direct_load_writes(self):
        lua = self.routes()
        self.assertFalse(lua.eval('ContextPtr.hidden'))
        self.assertEqual(lua.eval('#queue'), 0)
        lua.execute('Events.LoadScreenClose.Fire()')
        self.assertEqual(lua.eval('#queue'), 0)
        lua.execute('routeUpdate(0)')
        self.assertEqual(lua.eval('#queue'), 2)

    def test_distinct_tailors_destinations_stack_both_channels_and_respect_gates(self):
        lua = self.routes()
        lua.execute('''
            other=addCity(12,10);
            addBuilding(other,'BUILDING_CSC_TAILORS_TAILOR');
            addBuilding(other,'BUILDING_CSC_TAILORS_FASHION_HOUSE');
            other.properties.CSC_TAILORS_TAILOR_SUPPLIED=1;
            other.properties.CSC_TAILORS_FASHION_HOUSE_SUPPLIED=1;
            customer.routes={
                {DestinationCityPlayer=0,DestinationCityID=9},
                {DestinationCityPlayer=0,DestinationCityID=12}};
            Events.TradeRouteActivityChanged.Fire();routeUpdate(0);deliver();
        ''')
        for channel in ('TAILOR', 'FASHION_HOUSE'):
            self.assertEqual(lua.eval(f"customer:GetProperty('CSC_TAILORS_IMPORT_{channel}_ROUTE')"), 2)
            self.assertEqual(lua.eval(f"customer:GetProperty('CSC_TAILORS_IMPORT_{channel}_ROUTE_BIT_2')"), 1)
        lua.execute('other.properties.CSC_TAILORS_FASHION_HOUSE_SUPPLIED=0;Events.CityPropertyChanged.Fire();routeUpdate(0);deliver()')
        self.assertEqual(lua.eval("customer:GetProperty('CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE')"), 1)
        self.assertEqual(lua.eval("customer:GetProperty('CSC_TAILORS_IMPORT_TAILOR_ROUTE')"), 2)
        lua.execute("other.pillagedBuildings[GameInfo.Buildings.BUILDING_CSC_TAILORS_TAILOR.Index]=true;Events.BuildingChanged.Fire();routeUpdate(0);deliver()")
        self.assertEqual(lua.eval("customer:GetProperty('CSC_TAILORS_IMPORT_TAILOR_ROUTE')"), 1)
        lua.execute("addDistrict(customer,'DISTRICT_CSC_TAILORS_QUARTER',1,0);Events.DistrictAddedToMap.Fire();routeUpdate(0);deliver()")
        for channel in ('TAILOR', 'FASHION_HOUSE'):
            self.assertEqual(lua.eval(f"customer:GetProperty('CSC_TAILORS_IMPORT_{channel}_ROUTE')"), 0)
            self.assertEqual(lua.eval(f"customer:GetProperty('CSC_TAILORS_IMPORT_{channel}_ROUTE_BIT_1')"), 0)

    def test_legacy_save_with_counts_but_no_import_bits_is_reconciled(self):
        lua = self.routes()
        lua.execute('''
            seller.properties.CSC_BAKERS_BAKERY_SUPPLIED=1;
            CSC_RefreshBakersTradeRouteProperties();deliver();
            for _,key in ipairs({'CSC_BAKERS_IMPORT_CONSUMER_ROUTE_BIT_1',
                'CSC_TAILORS_IMPORT_TAILOR_ROUTE_BIT_1','CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE_BIT_1'}) do
                customer.properties[key]=nil;
                Map.GetPlot(customer:GetX(),customer:GetY()):SetProperty(key,nil);
            end;
            CSC_RefreshBakersTradeRouteProperties();deliver();
        ''')
        for prop in ('CSC_BAKERS_IMPORT_CONSUMER', 'CSC_TAILORS_IMPORT_TAILOR', 'CSC_TAILORS_IMPORT_FASHION_HOUSE'):
            self.assertEqual(lua.eval(f"customer:GetProperty('{prop}_ROUTE_BIT_1')"), 1)

    def test_sql_food_amenity_and_tooltip_registry_pay_each_encoded_route(self):
        self.check_sql_payouts('BAKERS', 'Bakers', ('CONSUMER', 'SPECIALTY'), 'FOOD')

    def test_sql_culture_amenity_and_tooltip_registry_pay_each_encoded_route(self):
        self.check_sql_payouts('TAILORS', 'Tailors', ('TAILOR', 'FASHION_HOUSE'), 'CULTURE')

    def check_sql_payouts(self, quarter, title, channels, yield_name):
        c = sqlite3.connect(':memory:')
        c.executescript('''
            CREATE TABLE Modifiers(ModifierId TEXT PRIMARY KEY,ModifierType TEXT,OwnerRequirementSetId TEXT,SubjectRequirementSetId TEXT);
            CREATE TABLE DistrictModifiers(DistrictType TEXT,ModifierId TEXT,PRIMARY KEY(DistrictType,ModifierId));
            CREATE TABLE ModifierArguments(ModifierId TEXT,Name TEXT,Value,PRIMARY KEY(ModifierId,Name));
            CREATE TABLE Requirements(RequirementId TEXT PRIMARY KEY,RequirementType TEXT,Inverse INTEGER DEFAULT 0);
            CREATE TABLE RequirementSets(RequirementSetId TEXT PRIMARY KEY,RequirementSetType TEXT);
            CREATE TABLE RequirementSetRequirements(RequirementSetId TEXT,RequirementId TEXT,PRIMARY KEY(RequirementSetId,RequirementId));
            CREATE TABLE RequirementArguments(RequirementId TEXT,Name TEXT,Value,PRIMARY KEY(RequirementId,Name));
            CREATE TABLE CSC_RouteStackBits(Bit INTEGER PRIMARY KEY);
            INSERT INTO CSC_RouteStackBits VALUES(2),(4),(8),(16);
        ''')
        source = (ROOT / f'Civ Supply Chains/Data/CSC_Q_{quarter}.sql').read_text(encoding='utf-8-sig')
        marker = f'CREATE TEMP TABLE CSC_{title}ImportChannels'
        before, block = source.split(marker, 1)
        # Read real base rows, then execute the complete production import generator.
        before = re.sub(r'--[^\n]*|/\*.*?\*/', '', before, flags=re.S)
        for match in re.finditer(r'INSERT(?: OR IGNORE)? INTO (Modifiers|DistrictModifiers|ModifierArguments|Requirements|RequirementSets|RequirementSetRequirements|RequirementArguments)\b.*?;', before, re.S):
            statement = match.group()
            if re.match(r'INSERT(?: OR IGNORE)? INTO \w+\s*\([^)]*\)\s*VALUES', statement):
                c.executescript(statement)
        c.executescript(marker + block)
        c.executescript((ROOT / 'Civ Supply Chains/ModSupport/ModSupport_SUIA.sql').read_text())
        for tier, channel in zip(('CONSUMER', 'SPECIALTY'), channels):
            for count in range(32):
                expected_properties = {f'CSC_{quarter}_IMPORT_{channel}_ROUTE_BIT_{bit}': count // bit % 2 for bit in (1,2,4,8,16)}
                for effect in (yield_name, 'AMENITY'):
                    paid = 0
                    for mod, reqset in c.execute('SELECT ModifierId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId LIKE ?', (f'MOD_CSC_{quarter}_IMPORT_{channel}_{effect}%',)):
                        req, = c.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?', (reqset,)).fetchone()
                        args = dict(c.execute('SELECT Name,Value FROM RequirementArguments WHERE RequirementId=?', (req,)))
                        if expected_properties.get(args['PropertyName'], 0) >= int(args['PropertyMinimum']):
                            paid += int(c.execute("SELECT Value FROM ModifierArguments WHERE ModifierId=? AND Name='Amount'", (mod,)).fetchone()[0])
                    self.assertEqual(paid, count, (channel, effect, count))
                displayed = sum(amount for prop,amount in c.execute("SELECT PropertyName,Amount FROM CSC_TradeRouteYieldPresentation WHERE EntryId LIKE ?", (f'CSC_{quarter}_IMPORT_{tier}_{yield_name}%',)) if expected_properties.get(prop,0)>0)
                self.assertEqual(displayed, count)


if __name__ == '__main__':
    unittest.main()
