"""Check live-script wiring against a cross-city Bakers supplier fixture."""

from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


SOURCE = Path(__file__).resolve().parents[4] / 'Civ Supply Chains/Lua_UI/AI'
FIXTURE = r'''
local function iterator(rows)
    local i = 0
    return function() i = i + 1; return rows[i] end
end
local function info(rows)
    return setmetatable(rows, {__call = function() return iterator(rows) end})
end
local bakers = {Index=3}
local cattle = {Index=4,ResourceType='RESOURCE_CATTLE'}
GameInfo = {
    Districts=info({{Index=0},{Index=1},{Index=2},bakers,DISTRICT_CSC_BAKERS_QUARTER=bakers}),
    Resources={[4]=cattle,RESOURCE_CATTLE=cattle},
    Improvements={IMPROVEMENT_PASTURE={Index=5}, IMPROVEMENT_FIXTURE={Index=6}},
    Improvement_ValidResources=info({
        {ResourceType='RESOURCE_CATTLE',ImprovementType='IMPROVEMENT_PASTURE'},
        {ResourceType='RESOURCE_CATTLE',ImprovementType='IMPROVEMENT_FIXTURE'},
    }),
}
CSC_Adjacency = {
    ByDistrict={},
    Initialize=function() end,
    ResourceVisible=function() return true end,
    HasTag=function(tag, resource) return tag=='CLASS_CSC_BAKERS_BASE' and resource=='RESOURCE_CATTLE' end,
}
local quarter = {GetType=function() return 3 end, GetX=function() return 10 end, GetY=function() return 10 end,
    IsComplete=function() return true end, IsPillaged=function() return false end}
local districts = {GetNumDistricts=function() return 1 end, GetDistrictByIndex=function() return quarter end}
local city = {GetDistricts=function() return districts end, GetProperty=function() return 1 end}
local cities = {Members=function()
    local once = false
    return function() if not once then once = true; return 1,city end end
end}
local function player(id, human)
    return {GetID=function() return id end, IsHuman=function() return human end,
        GetTeam=function() return 9 end, GetCities=function() return cities end}
end
Players = {[0]=player(0,true), [3]=player(3,false)}
PlayerManager = {GetAliveMajors=function() return {Players[0],Players[3]} end}
PlayersVisibility = {[3]={IsRevealed=function() return true end}}
pasture = {GetIndex=function() return 101 end, GetX=function() return 11 end, GetY=function() return 10 end,
    GetResourceType=function() return 4 end, GetOwner=function() return 3 end, GetDistrictType=function() return -1 end,
    GetImprovementType=function() return improvement end, IsImprovementPillaged=function() return pillaged end,
    CanHaveDistrict=function(_, district, owner, cityID) return district==1 and owner==3 and cityID==42 end}
improvement, pillaged = 5, false
Map = {GetPlot=function() return quarter end, GetPlotByIndex=function() return pasture end,
    GetAdjacentPlots=function() return {pasture} end, GetGridSize=function() return 40,30 end}
Cities = {GetPlotPurchaseCity=function() return {GetOwner=function() return 3 end,GetID=function() return 42 end} end}
ImprovementBuilder = {CanHaveImprovement=function(_, _, team) assert(team==9); return true end}
local properties = {}
turn = 1
Game = {GetCurrentGameTurn=function() return turn end,GetProperty=function(_,k) return properties[k] end,
    SetProperty=function(_,k,v) properties[k]=v end}
ExposedMembers = {}
GameConfiguration = {}
GameEvents = {OnGameTurnStarted={Add=function(callback) boundary=callback end}}
Events = {}
version, packet = 0, nil
CE_AIDistrictScoresBegin = function(v) version=v; packet={}; builders={}; wonderStages=0; return 1 end
CE_AIDistrictScoresAllow = function(id) assert(id==3); return 1 end
CE_AIDistrictScoresEntry = function(...) packet[#packet+1]={...}; return 1 end
CE_AIDistrictScoresCommit = function() return 1 end
CE_AIDistrictScoresDisable = function() packet=nil; return 1 end
CE_AIDistrictScoresStatus = function() return '{"ready":1,"faults":0,"version":'..version..'}' end
'''


class BakersGameplayTest(unittest.TestCase):
    def test_real_publisher_protects_the_city_that_can_cover_the_supplier(self):
        lua = LuaRuntime()
        lua.execute(FIXTURE)

        def include(name):
            if name != 'CSC_AdjacencyCore':
                lua.execute((SOURCE / f'{name}.lua').read_text(encoding='utf-8'))

        lua.globals().include = include
        include('CSC_AI_BakersGameplay')
        self.assertIsNone(lua.eval('packet'))
        # The gameplay script can load before the separate UI context.
        lua.execute('GameConfiguration = {IsAnyMultiplayer=function() return false end, '
                    'IsHotseat=function() return true end}')
        ui = SOURCE.parent / 'Adjacencies/CSC_AdjacencyUI.lua'
        lua.execute(ui.read_text(encoding='utf-8'))
        lua.execute('boundary()')
        self.assertIsNone(lua.eval('packet'))
        lua.execute('GameConfiguration.IsHotseat=function() return false end; boundary()')
        self.assertEqual(lua.eval('table.concat(packet[1], ",")'), '3,42,1,101,-24576')
        self.assertEqual(lua.eval('#builders'), 0)
        lua.execute('boundary()')
        self.assertEqual(lua.eval('version'), 1)
        lua.execute("""
            CE_AIBuilderProtectionStatus=function() return '{"ready":1,"faults":0}' end
            CE_AIBuilderProtectionAllow=function(...) builders[#builders+1]={...}; return 1 end
            CE_AISupplierWonderProtectionStatus=function() return '{"ready":1,"faults":0}' end
            CE_AISupplierWonderProtectionStage=function()
                assert(#builders>0); wonderStages=wonderStages+1; return 1
            end
            turn=2; boundary()
        """)
        self.assertEqual(lua.eval('#builders'), 1)
        self.assertEqual(lua.eval('table.concat(builders[1], ",")'), '3,42,101,5')
        self.assertEqual(lua.eval('wonderStages'), 1)
        lua.execute('turn=3; pillaged=true; boundary()')
        self.assertEqual(lua.eval('table.concat(packet[1], ",")'), '3,42,1,101,-12288')
        self.assertEqual(lua.eval('#builders'), 2)
        self.assertEqual(lua.eval('table.concat(builders[2], ",")'), '3,42,101,6')
        lua.execute("""
            CE_AISupplierWonderProtectionStatus=function() return '{"ready":1,"faults":1}' end
            turn=4; improvement=-1; boundary()
        """)
        self.assertEqual(lua.eval('table.concat(packet[1], ",")'), '3,42,1,101,-12288')
        self.assertEqual(lua.eval('wonderStages'), 0)
        lua.execute("""
            CSC_AI_BakersSiteForecasts=function(player, readSuppliers, excluded)
                assert(player==Players[3] and readSuppliers==CSC_AI_QuarterPlacement.ReadBakersSuppliers and excluded[101])
                return {{player=3,city=42,district=3,plot=100,delta=12288}}
            end
            turn=5; boundary()
        """)
        self.assertEqual(lua.eval('table.concat(packet[1], ",")'), '3,42,1,101,-12288')
        self.assertEqual(lua.eval('table.concat(packet[2], ",")'), '3,42,3,100,12288')
        lua.execute("CSC_AI_BakersSiteForecasts=function() error('fixture') end; turn=6; boundary()")
        self.assertEqual(lua.eval('#packet'), 1)
        self.assertEqual(lua.eval('table.concat(packet[1], ",")'), '3,42,1,101,-12288')
        lua.execute('turn=7; Players[3].IsHuman=function() return true end; boundary()')
        self.assertIsNone(lua.eval('packet'))


if __name__ == '__main__':
    unittest.main()
