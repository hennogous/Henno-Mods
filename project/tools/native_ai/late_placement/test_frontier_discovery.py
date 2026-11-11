"""Boundary checks for the diagnostic; this does not establish live Lua API parity."""
import json
from pathlib import Path
import unittest
import tempfile
from lupa.lua51 import LuaRuntime
from frontier_discovery import ui_readback

FIXTURE = '''
output={};print=function(s)output[#output+1]=s end
local function rows(values)return setmetatable(values,{__call=function(self)local n=0;return function()n=n+1;return self[n]end end})end
local district={HasDistrict=function()return false end}
local treasury={GetGoldBalance=function()return 50 end,GetGoldYield=function()return 10 end,GetTotalMaintenance=function()return 2 end}
gold={GetPlotPurchaseCost=function(self,index)assert(index==31);return 145 end}
city={GetID=function()return 42 end,GetName=function()return 'Fixture' end,GetX=function()return 0 end,GetY=function()return 0 end,GetDistricts=function()return district end,GetGold=function()return gold end}
-- Native Members yields the iteration key and object separately.
local cities={Members=function()local done=false;return function()if not done then done=true;return 0,city end end end}
player={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return false end,GetTreasury=function()return treasury end,GetCities=function()return cities end}
Players={[1]=player};PlayersVisibility={[1]={IsRevealed=function()return true end}}
local function plot(index,owner,district)return {GetIndex=function()return index end,GetX=function()return index end,GetY=function()return 0 end,GetOwner=function()return owner end,GetDistrictType=function()return district end,GetResourceType=function()return -1 end,CanHaveDistrict=function()return true end,GetRiverCrossingCount=function()return 0 end}end
site=plot(31,-1,-1);host=plot(2,1,0)
Map={GetGridSize=function()return 74,46 end,GetPlot=function()return host end,GetAdjacentPlots=function()return {host}end}
GameInfo={Districts=rows({{Index=0,DistrictType='DISTRICT_CITY_CENTER'}}),Resources={}}
CSC_Adjacency={Initialize=function()end,PlotsInBand=function()return {site}end,HasTag=function()return false end,ResourceVisible=function()return true end}
profile={key='BAKERS',district={Index=36},customers={[0]={}},base='BASE',producers={}}
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return {profile}end,ReadSuppliers=function()return {base={{plot=1,working=true,ready=true}},specialty={}}end}
Game={GetCurrentGameTurn=function()return 200 end}
'''


class Discovery(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime()
        self.lua.execute(FIXTURE)
        self.script = Path(__file__).with_name('frontier_site_survey.lua').read_text()

    def sample(self, change=''):
        self.lua.execute(change)
        self.lua.execute(self.script)
        lines = self.lua.globals().output
        return json.loads(lines[len(lines)].split('=', 1)[1])

    def test_known_supply_customer_and_economy(self):
        data = self.sample()
        self.assertEqual(data['sites'][0]['quote'], 145)
        self.assertTrue(data['sites'][0]['hosts'][0]['stageTwo'])
        self.assertTrue(data['sites'][0]['quoteAvailable'])
        self.assertEqual(data['players'][0]['treasuryGold'], 50)
        self.assertEqual(data['players'][0]['goldYield'], 10)

    def test_missing_quote_is_explicit(self):
        row = self.sample('city.GetGold=nil')['sites'][0]
        self.assertFalse(row['quoteAvailable'])
        self.assertNotIn('quote', row)
        self.assertIn('missing method', row['quoteError'])

    def test_nonpositive_quote_is_retained_as_a_lead(self):
        row = self.sample('gold.GetPlotPurchaseCost=function()return -1 end')['sites'][0]
        self.assertTrue(row['quoteAvailable'])
        self.assertEqual(row['quote'], -1)

    def test_no_base_is_not_promoted_to_known_supply(self):
        data = self.sample('CSC_AI_QuarterPlacement.ReadSuppliers=function()return {base={},specialty={}}end')
        self.assertEqual(data['sites'], [])
        self.assertEqual(data['players'][0]['frontierPairs'], 1)

    def test_foreign_or_unrevealed_site_is_not_frontier(self):
        for change in ('site.GetOwner=function()return 2 end',
            'PlayersVisibility[1].IsRevealed=function()return false end'):
            self.setUp()
            data = self.sample(change)
            self.assertEqual(data['sites'], [])
            self.assertEqual(data['players'][0]['frontierPairs'], 0)

    def test_ui_pairs_are_deduplicated_and_joined(self):
        class Controller:
            def cmd(self, code, context, label):
                assert context == 'PlotInfo' and 'CanStartCommand' in code
                return ('O\0CSC_FRONTIER_UI_QUOTE\t1\t42\t31\t145\ttrue\r\n'
                    'O\0CSC_FRONTIER_UI_ECONOMY\t1\t150\t12\t2\r\n'
                    'O\0CSC_FRONTIER_UI_END\t200\t1\t1\r\n')
        state=dict(turn=200,players=[dict(player=1)],sites=[dict(player=1,city=42,plot=31)],
            supplierLeads=[dict(player=1,city=42,plot=31)])
        parent=Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=parent,prefix='.discovery-test-') as folder:
            assert Path(folder).resolve().parent==parent
            ui_readback(Controller(),Path(folder),state)
        self.assertEqual(state['sites'][0]['ui'],dict(quote=145.0,uiCanStartAtBoundary=True))
        self.assertEqual(state['supplierLeads'][0]['ui'],state['sites'][0]['ui'])
        self.assertEqual(state['uiEconomy'][0]['treasuryGold'],150)


if __name__ == '__main__':
    unittest.main()
