"""Offline execution only: mutation traces, local lifecycle and queued operations.

Run with the existing isolated lupa dependency on PYTHONPATH. No game connections.
"""
from pathlib import Path
import re
import unittest
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
LUA = ROOT / 'Civ Supply Chains/Lua_UI'
FIXTURES = Path(__file__).with_name('fixtures')


def load(lua, name):
    lua.execute(re.sub(r'\s*:\s*(?:number|table|string|boolean)\b', '',
                       (LUA / name).read_text(encoding='utf-8-sig')))


def world(reverse=False):
    lua = LuaRuntime(unpack_returned_tuples=True)
    for name in ('cafe_stage4_world.lua', 'fashion_house_world.lua'):
        lua.execute((FIXTURES / name).read_text(encoding='utf-8-sig'))
    lua.execute('''
        function events()
            return setmetatable({}, {__index=function(t,k)
                local callbacks={}; local e={};
                e.Add=function(f) callbacks[#callbacks+1]=f; end;
                e.Fire=function(...) for _,f in ipairs(callbacks) do f(...); end; end;
                rawset(t,k,e); return e;
            end});
        end
        Events=events(); GameEvents=events(); trace={}; queue={}; turn=10;
        localID=0;hostID=0;network=true;
        Game.GetLocalPlayer=function()return localID;end;
        Game.GetCurrentGameTurn=function()return turn;end;
        GameConfiguration.IsNetworkMultiplayer=function()return network;end;
        Network={GetGameHostPlayerID=function()return hostID;end};
        Players[2]=Players[0]; -- second client/host can submit for target owner 0
        local nativePlot=Map.GetPlot;
        Map.GetPlot=function(x,y)
            local p=nativePlot(x,y);
            if not p.logged then
                p.logged=true;local setter=p.SetProperty;
                p.SetProperty=function(self,k,v)
                    trace[#trace+1]='plot:'..self:GetIndex()..':'..k..'='..tostring(v);
                    setter(self,k,v);
                end;
            end;
            return p;
        end;
        local nativeCity=addCity;
        addCity=function(id,pop)
            local c=nativeCity(id,pop);local setter=c.SetProperty;
            c.SetProperty=function(self,k,v)
                trace[#trace+1]='city:'..self.id..':'..k..'='..tostring(v);
                setter(self,k,v);
            end;
            return c;
        end;
        UI.RequestPlayerOperation=function(sender,op,params)
            assert(op==PlayerOperations.EXECUTE_SCRIPT);
            queue[#queue+1]={sender=sender,params=params};
        end;
        function deliver()
            local pending=queue;queue={};
            for _,request in ipairs(pending) do
                GameEvents.CSC_SetBakersTradeRouteProperties.Fire(request.sender,request.params);
            end;
        end;
        function writes()return table.concat(trace,'\\n');end;
        seller=addCity(9,15);customer=addCity(2,10);
        addDistrict(seller,'DISTRICT_CSC_TAILORS_QUARTER',0,0);
        addBuilding(seller,'BUILDING_CSC_TAILORS_FASHION_HOUSE');
        addBuilding(seller,'BUILDING_CSC_TAILORS_TAILOR');
        seller.properties.CSC_TAILORS_TAILOR_SUPPLIED=1;
        seller.properties.CSC_TAILORS_FASHION_HOUSE_SUPPLIED=1;
        seller.properties.CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION=1;
        addDistrict(customer,'DISTRICT_THEATER',1,0);
        addBuilding(customer,'BUILDING_AMPHITHEATER');
        addWonder(customer,'BUILDING_BROADWAY',0,1);
        hasOpera=true;
        customer.routes={{DestinationCityPlayer=0,DestinationCityID=9}};
        trace={};
    ''')
    if reverse:
        lua.execute('''
            local nativePairs=pairs;
            pairs=function(t)
                local keys={};for k in nativePairs(t) do keys[#keys+1]=k;end;
                table.sort(keys,function(a,b)return tostring(a)>tostring(b);end);
                local i=0;return function()i=i+1;local k=keys[i];if k~=nil then return k,t[k];end;end;
            end;
            Players[0].GetCities=(function(base)return function()
                local m=base();local members=m.Members;
                m.Members=function()
                    local all={};for _,c in members()do table.insert(all,1,c);end;
                    local i=0;return function()i=i+1;if all[i]then return i,all[i];end;end;
                end;
                return m;
            end;end)(Players[0].GetCities);
        ''')
    return lua


class MultiplayerHardeningTests(unittest.TestCase):
    def routes(self, reverse=False):
        lua = world(reverse)
        load(lua, 'TradeRoutes/CSC_TradeRouteInteractions_Gameplay.lua')
        load(lua, 'TradeRoutes/CSC_TradeRouteInteractions.lua')
        return lua

    def test_loading_is_read_only_until_synchronized_event(self):
        for name in ('CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua',
                     'ArtProperties/CSC_ArtProperties.lua',
                     'WonderServices/CSC_WonderServicePlacement.lua'):
            with self.subTest(script=name):
                lua = world()
                load(lua, name)
                lua.execute('Events.LoadGameViewStateDone.Fire();Events.LoadScreenClose.Fire();Events.PlayerTurnActivated.Fire(0)')
                self.assertEqual(lua.eval('writes()'), '')
                self.assertEqual(lua.eval('#placementCalls'), 0)
                lua.execute('GameEvents.PlayerTurnStarted.Fire(0)')
                self.assertNotEqual(lua.eval('writes()'), '')
                before = lua.eval('writes()')
                lua.execute('GameEvents.OnGameTurnStarted.Fire(10)')
                self.assertEqual(lua.eval('writes()'), before, 'repeat refresh must be idempotent')

    def test_population_art_and_wonder_write_traces_ignore_iteration_order(self):
        for name in ('CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua',
                     'ArtProperties/CSC_ArtProperties.lua',
                     'WonderServices/CSC_WonderServicePlacement.lua'):
            traces = []
            for reverse in (False, True):
                lua = world(reverse)
                # Two independent Stage 3 rows exercise registry/property ordering.
                lua.execute('''
                    local rows={};
                    for _,id in ipairs({'Z','A'})do rows[#rows+1]={TransactionId=id,
                        SellerDistrictType='DISTRICT_CSC_TAILORS_QUARTER',SellerBuildingType='BUILDING_CSC_TAILORS_TAILOR',
                        CustomerDistrictType='DISTRICT_THEATER',CustomerBuildingType='BUILDING_AMPHITHEATER',
                        SellerPopulationProperty='TEST_POP_'..id,SellerReturnAmountProperty='TEST_RETURN_'..id,
                        CustomerYieldAmountProperty='TEST_CUSTOMER_'..id,EngineAmountPerPopulation=.125};end;
                    GameInfo.CSC_Stage3CustomerTransactions=function()local i=0;return function()i=i+1;return rows[i];end;end;
                ''')
                load(lua, name)
                lua.execute('GameEvents.PlayerTurnStarted.Fire(0)')
                # Exercise cleanup as well as normal writes.
                lua.execute('customer.buildings={};GameEvents.PlayerTurnStarted.Fire(0)')
                traces.append(lua.eval('writes()'))
            self.assertTrue(traces[0], name)
            self.assertEqual(*traces, name)

    def test_only_host_submits_local_player_operations_in_city_order(self):
        lua = self.routes(True)
        self.assertEqual(lua.eval('#queue'), 0, 'script loading must not submit snapshots')
        lua.execute('localID=2;Events.LoadGameViewStateDone.Fire();routeUpdate(0)')
        self.assertEqual(lua.eval('#queue'), 0, 'joining nonhost must not submit')
        lua.execute('localID=0;Events.LoadGameViewStateDone.Fire();routeUpdate(0)')
        self.assertEqual(lua.eval('#queue'), 2)
        self.assertEqual(lua.eval('queue[1].params.CityID'), 2)
        self.assertEqual(lua.eval('queue[2].params.CityID'), 9)
        self.assertTrue(lua.eval('queue[1].sender==0 and queue[2].sender==0'))
        self.assertEqual(lua.eval('writes()'), '', 'UI cannot mutate properties directly')
        lua.execute('deliver()')
        self.assertEqual(lua.eval("seller:GetProperty('CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1')"), 1)
        self.assertEqual(lua.eval("customer:GetProperty('CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE')"), 1)

    def test_duplicate_and_stale_revision_requests_are_noops(self):
        lua = self.routes()
        lua.execute('CSC_RefreshBakersTradeRouteProperties();saved=queue[1];deliver();trace={}')
        lua.execute('GameEvents.CSC_SetBakersTradeRouteProperties.Fire(saved.sender,saved.params)')
        self.assertEqual(lua.eval('writes()'), '')
        lua.execute('saved.params.Revision=999;GameEvents.CSC_SetBakersTradeRouteProperties.Fire(saved.sender,saved.params)')
        self.assertEqual(lua.eval('writes()'), '')

    def test_inflight_route_change_is_reconciled_after_acknowledgement(self):
        lua = self.routes()
        lua.execute('CSC_RefreshBakersTradeRouteProperties();customer.routes={};deliver();routeUpdate(1);deliver()')
        self.assertEqual(lua.eval("seller:GetProperty('CSC_TAILORS_EXPORT_TAILOR_ROUTE')"), 0)
        self.assertEqual(lua.eval("customer:GetProperty('CSC_TAILORS_IMPORT_TAILOR_ROUTE')"), 0)
        lua.execute('trace={};routeUpdate(1);deliver()')
        self.assertEqual(lua.eval('writes()'), '')

    def test_wrong_turn_city_owner_id_or_malformed_payload_is_rejected_atomically(self):
        for change in ('p.Turn=p.Turn-1', 'p.CityID=999', 'p.CityPlayerID=2',
                       'p.ExportTailorRoute=-1', 'p.ExportTailorRoute=.5',
                       'p.ExportTailorRoute=0/0', 'p.ExportTailorRoute=math.huge',
                       'p.HasBakersQuarter=2', 'p.ImportConsumerRoute=nil'):
            with self.subTest(change=change):
                lua = self.routes()
                lua.execute('CSC_RefreshBakersTradeRouteProperties();p=queue[1].params;' + change)
                lua.execute('queue={};GameEvents.CSC_SetBakersTradeRouteProperties.Fire(0,p)')
                self.assertEqual(lua.eval('writes()'), '')

    def test_host_migration_and_hotseat_use_the_current_local_sender(self):
        lua = self.routes()
        lua.execute('hostID=2;Events.MultiplayerHostMigrated.Fire(2);routeUpdate(0)')
        self.assertEqual(lua.eval('#queue'), 0)
        lua.execute('localID=2;Events.MultiplayerHostMigrated.Fire(2);routeUpdate(0)')
        self.assertEqual(lua.eval('#queue'), 2)
        self.assertTrue(lua.eval('queue[1].sender==2 and queue[1].params.CityPlayerID==0'))
        lua.execute('deliver();customer.routes={};network=false;localID=0;CSC_RefreshBakersTradeRouteProperties();deliver()')
        self.assertEqual(lua.eval("customer:GetProperty('CSC_TAILORS_IMPORT_TAILOR_ROUTE')"), 0)

    def test_route_operations_deliver_identical_traces_on_two_peers(self):
        peers = [self.routes(reverse) for reverse in (False, True)]
        peers[0].execute('CSC_RefreshBakersTradeRouteProperties()')
        for request in peers[0].globals().queue.values():
            payload = dict(request.params.items())
            for lua in peers:
                lua.globals().GameEvents.CSC_SetBakersTradeRouteProperties.Fire(
                    request.sender, lua.table_from(payload))
        self.assertEqual(peers[0].eval('writes()'), peers[1].eval('writes()'))

    def test_ui_property_bursts_are_coalesced_and_bit_inputs_are_not_trusted(self):
        lua = self.routes()
        lua.execute('for i=1,20 do Events.CityPropertyChanged.Fire(0,9) end')
        self.assertEqual(lua.eval('#queue'), 0)
        lua.execute('routeUpdate(0)')
        self.assertEqual(lua.eval('#queue'), 2)
        lua.execute('queue[2].params.ExportTailorRoute=2;queue[2].params.ExportTailorRouteBit16=1;deliver()')
        self.assertEqual(lua.eval("seller:GetProperty('CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_2')"), 1)
        self.assertEqual(lua.eval("seller:GetProperty('CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_16') or 0"), 0)

    def test_sparse_player_ids_are_not_treated_as_a_count_range(self):
        for script, refresh in (
            ('CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua', 'CSC_RefreshCustomerPopulationReturns'),
            ('ArtProperties/CSC_ArtProperties.lua', 'CSC_RefreshAllArtProperties'),
            ('TradeRoutes/CSC_TradeRouteInteractions.lua', 'CSC_RefreshBakersTradeRouteProperties'),
        ):
            with self.subTest(script=script):
                lua = world()
                lua.execute('''
                    Players[5]={GetID=function()return 5;end,GetCities=Players[0].GetCities,
                        GetCulture=Players[0].GetCulture};
                    PlayerManager.GetAlive=function()return {Players[5]};end;
                    seller.owner=5;customer.owner=5;customer.routes[1].DestinationCityPlayer=5;
                ''')
                if 'TradeRoutes' in script:
                    load(lua, 'TradeRoutes/CSC_TradeRouteInteractions_Gameplay.lua')
                load(lua, script)
                lua.globals()[refresh]()
                lua.execute('deliver()')
                self.assertNotEqual(lua.eval('writes()'), '')

    def test_adjacency_startup_and_cleanup_ignore_native_collection_order(self):
        traces = []
        for reverse in (False, True):
            lua = world(reverse)
            lua.execute('''
                local sites={};local plots={};
                for _,index in ipairs({50,10,30}) do
                    local p={index=index,props={}};
                    function p:GetIndex()return self.index;end;
                    sites[#sites+1]=p;plots[index]=p;
                end;
                if REVERSE then sites[1],sites[3]=sites[3],sites[1];end;
                local districts={};
                for _,p in ipairs(sites)do
                    districts[#districts+1]={GetType=function()return 0;end,
                        GetX=function()return p.index;end,GetY=function()return 0;end,
                        IsComplete=function()return true;end};
                end;
                local city={GetDistricts=function()return {
                    GetNumDistricts=function()return #districts;end,
                    GetDistrictByIndex=function(_,i)return districts[i+1];end};end};
                PlayerManager.GetAliveMajors=function()return {{GetID=function()return 0;end,
                    GetCities=function()return {Members=function()local i=0;return function()
                        i=i+1;if i==1 then return i,city;end;end;end};end}};end;
                GameInfo.Districts={[0]={DistrictType='TEST'}};
                Map.GetPlot=function(x,y)return plots[x];end;
                Map.GetPlotByIndex=function(index)return plots[index];end;
                CSC_Adjacency={Rules={{ID='A',AdjacencyType='FIXED'},{ID='Z',AdjacencyType='FIXED'}}};
                local A=CSC_Adjacency;A.ByDistrict={TEST=A.Rules};
                A.Initialize=function()end;A.Eligible=function()return true;end;A.Count=function()return 1;end;
                A.Write=function(p,r,value)if p.props[r.ID]~=value then
                    trace[#trace+1]=p.index..':'..r.ID..'='..value;p.props[r.ID]=value;
                end;end;
                include=function()end;removeDistricts=function()districts={};end;
                trace={};
            '''.replace('REVERSE', 'true' if reverse else 'false'))
            load(lua, 'Adjacencies/CSC_AdjacencyGameplay.lua')
            lua.execute('Events.LoadGameViewStateDone.Fire();Events.LoadScreenClose.Fire()')
            self.assertEqual(lua.eval('writes()'), '')
            lua.execute('GameEvents.PlayerTurnStarted.Fire(0);removeDistricts();GameEvents.OnGameTurnStarted.Fire(10)')
            traces.append(lua.eval('writes()'))
        self.assertEqual(*traces)
        self.assertEqual(traces[0], '\n'.join(f'{i}:{r}={v}' for v in (1,0) for i in (10,30,50) for r in ('A','Z')))


if __name__ == '__main__':
    unittest.main()
