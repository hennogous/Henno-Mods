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
local bakers = {Index=3,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'}
local center = {Index=0,DistrictType='DISTRICT_CITY_CENTER'}
local cattle = {Index=4,ResourceType='RESOURCE_CATTLE'}
local pastureKind = {Index=5}
local alternateKind = {Index=6}
GameInfo = {
    Districts=info({center,{Index=1},{Index=2},bakers,DISTRICT_CSC_BAKERS_QUARTER=bakers,
        DISTRICT_CITY_CENTER=center}),
    Resources={[4]=cattle,RESOURCE_CATTLE=cattle},
    Improvements={[5]=pastureKind, [6]=alternateKind,
        IMPROVEMENT_PASTURE=pastureKind, IMPROVEMENT_FIXTURE=alternateKind},
    Buildings={
        BUILDING_GRANARY={Index=8,Hash=108,PrereqDistrict='DISTRICT_CITY_CENTER'},
        BUILDING_CSC_BAKERS_WATER_MILL={Index=9,Hash=109,PrereqDistrict=bakers.DistrictType},
        BUILDING_CSC_BAKERS_WIND_MILL={Index=10,Hash=110,PrereqDistrict=bakers.DistrictType},
        BUILDING_FIXTURE_GRANARY={Index=11,Hash=111,PrereqDistrict='DISTRICT_CITY_CENTER'},
    },
    BuildingReplaces=info({
        {ReplacesBuildingType='BUILDING_GRANARY',CivUniqueBuildingType='BUILDING_FIXTURE_GRANARY'},
    }),
    DistrictReplaces=info({}),
    CSC_QuarterFlowBuildings=info({
        {QuarterKey='BAKERS',Stage=2,BuildingType='BUILDING_CSC_BAKERS_WIND_MILL'},
        {QuarterKey='BAKERS',Stage=2,BuildingType='BUILDING_CSC_BAKERS_WATER_MILL'},
    }),
    CSC_QuarterCustomerBuildings=info({
        {QuarterKey='BAKERS',ProducerStage=2,BuildingType='BUILDING_GRANARY'},
    }),
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
    GetIndex=function() return 100 end, IsComplete=function() return true end, IsPillaged=function() return false end}
local districts = {GetNumDistricts=function() return 1 end, GetDistrictByIndex=function() return quarter end}
city = {GetDistricts=function() return districts end, GetProperty=function() return 1 end,
    GetID=function() return 42 end}
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
    def test_tailors_uses_same_builder_and_repair_rules_with_multiple_deposits(self):
        lua = LuaRuntime()
        lua.execute(FIXTURE)
        lua.execute("""
            local tailor = GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER
            GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER = nil
            tailor.DistrictType = 'DISTRICT_CSC_TAILORS_QUARTER'
            GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER = tailor
            GameInfo.Districts.DISTRICT_HARBOR = {Index=2, DistrictType='DISTRICT_HARBOR'}
            GameInfo.Buildings.WORKSHOP = {Index=9, Hash=109, PrereqDistrict=tailor.DistrictType}
            GameInfo.Buildings.LIGHTHOUSE = {Index=8, Hash=108, PrereqDistrict='DISTRICT_HARBOR'}
            local function row(value)
                return function()
                    local used = false
                    return function() if not used then used = true; return value end end
                end
            end
            GameInfo.CSC_QuarterFlowBuildings = row({QuarterKey='TAILORS', Stage=2, BuildingType='WORKSHOP'})
            GameInfo.CSC_QuarterCustomerBuildings = row({QuarterKey='TAILORS', ProducerStage=2, BuildingType='LIGHTHOUSE'})
            GameInfo.Civics = {CIVIC_NAVAL_TRADITION={Index=7}}
            Players[3].GetCulture = function() return {HasCivic=function(_, id) return id==7 end} end
            CSC_Adjacency.HasTag = function(tag) return tag=='CLASS_CSC_TAILORS_BASE' end
            city.GetProperty = function() return 0 end
            city.GetBuildings = function()
                return {HasBuilding=function(_, id) return id==9 and workshop end,
                    IsPillaged=function() return damaged end, GetBuildingLocation=function() return 100 end}
            end
            local harbor = {GetIndex=function() return 99 end, GetOwner=function() return 3 end,
                GetDistrictType=function() return 2 end, GetResourceType=function() return -1 end}
            local alternative = setmetatable({GetIndex=function() return 98 end,
                GetImprovementType=function() return -1 end, IsImprovementPillaged=function() return false end},
                {__index=pasture})
            local getPlot = Map.GetPlotByIndex
            Map.GetPlotByIndex = function(id) return id==98 and alternative or getPlot(id) end
            Map.GetAdjacentPlots = function() return {alternative,pasture,harbor} end
            local getBuyer = Cities.GetPlotPurchaseCity
            Cities.GetPlotPurchaseCity = function(plot)
                if plot~=harbor then return getBuyer(plot) end
                return {GetOwner=function() return 3 end, GetID=function() return 77 end,
                    GetBuildings=function()
                        return {HasBuilding=function(_, id) return id==8 and lighthouse end,
                            IsPillaged=function() return false end, GetBuildingLocation=function() return 99 end}
                    end}
            end
            Map.GetPlot().IsPillaged = function() return damaged end
            workshop, lighthouse, damaged, pillaged = true, true, false, true
        """)
        lua.execute((SOURCE / 'CSC_AI_QuarterPlacement.lua').read_text(encoding='utf-8'))
        lua.execute("""
            function plan()
                local _, jobs, buildings, repairs = CSC_AI_QuarterPlacement.MaterialDeductions(
                    Players[3], true, 16384, 131072, function() return true end, true)
                local values = {}
                for _, job in ipairs(jobs) do values[job.plot] = job.deltaQ8 end
                return values, buildings, repairs
            end
            jobs, buildings, repairs = plan()
        """)
        self.assertEqual(lua.eval('jobs[101]'), 14336)
        self.assertIsNone(lua.eval('jobs[98]'))
        lua.execute('pillaged=false; lighthouse=false; jobs, buildings, repairs=plan()')
        self.assertEqual(lua.eval('buildings[1].city'), 77)
        self.assertEqual(lua.eval('buildings[1].delta'), 13312)
        lua.execute('lighthouse=true; workshop=false; jobs, buildings, repairs=plan()')
        self.assertEqual(lua.eval('buildings[1].city'), 42)
        self.assertEqual(lua.eval('buildings[1].delta'), 114688)
        lua.execute('workshop=true; damaged=true; jobs, buildings, repairs=plan()')
        self.assertEqual(lua.eval('repairs[1].district'), 3)
        self.assertEqual(lua.eval('#buildings'), 0)

    def test_shared_model_resolves_unique_host_and_building(self):
        lua = LuaRuntime()
        lua.execute(FIXTURE)
        lua.execute("""
            local function rows(values)
                return function()
                    local index = 0
                    return function() index = index + 1; return values[index] end
                end
            end
            GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER = {Index=9,DistrictType='DISTRICT_CSC_TAILORS_QUARTER'}
            GameInfo.Districts.DISTRICT_HARBOR = {Index=4,DistrictType='DISTRICT_HARBOR'}
            GameInfo.Districts.DISTRICT_DOCKYARD = {Index=5,DistrictType='DISTRICT_DOCKYARD'}
            GameInfo.Buildings = {
                BUILDING_WORKSHOP={Index=19,PrereqDistrict='DISTRICT_CSC_TAILORS_QUARTER'},
                BUILDING_LIGHTHOUSE={Index=20,PrereqDistrict='DISTRICT_HARBOR'},
                BUILDING_UNIQUE_LIGHTHOUSE={Index=21,PrereqDistrict='DISTRICT_DOCKYARD'},
            }
            GameInfo.BuildingReplaces=rows({
                {ReplacesBuildingType='BUILDING_LIGHTHOUSE',CivUniqueBuildingType='BUILDING_UNIQUE_LIGHTHOUSE'},
            })
            GameInfo.DistrictReplaces=rows({
                {ReplacesDistrictType='DISTRICT_HARBOR',CivUniqueDistrictType='DISTRICT_DOCKYARD'},
            })
            GameInfo.CSC_QuarterFlowBuildings=rows({
                {QuarterKey='TAILORS',Stage=2,BuildingType='BUILDING_WORKSHOP'},
            })
            GameInfo.CSC_QuarterCustomerBuildings=rows({
                {QuarterKey='TAILORS',ProducerStage=2,BuildingType='BUILDING_LIGHTHOUSE'},
            })
        """)
        lua.execute((SOURCE / 'CSC_AI_QuarterPlacement.lua').read_text(encoding='utf-8'))
        profile = lua.eval('CSC_AI_QuarterPlacement.StageTwoProfiles()[2]')
        self.assertEqual(profile.producers[1].Index, 19)
        self.assertEqual(profile.customers[4][20].Index, 20)
        self.assertEqual(profile.customers[5][20].Index, 20)
        self.assertEqual(profile.customers[5][21].Index, 21)

    def test_real_publisher_protects_the_city_that_can_cover_the_supplier(self):
        lua = LuaRuntime()
        lua.execute(FIXTURE)
        messages = []
        lua.globals().print = messages.append

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
            CSC_AI_QuarterSiteForecasts=function(player, profile, chains, readSuppliers, excluded, readLegalTargets)
                assert(player==Players[3] and profile.key=='BAKERS' and #chains==1)
                assert(readSuppliers==CSC_AI_QuarterPlacement.ReadSuppliers and excluded[101])
                assert(readLegalTargets==ExposedMembers.CSC_Adjacency.GetLegalDistrictTargets)
                return {{player=3,city=42,district=3,plot=100,delta=12288},
                    {player=3,city=42,district=3,plot=102,delta=-65536,weak=true}}
            end
            CE_AIDistrictScoresStatus=function()
                return '{"ready":1,"faults":0,"version":'..version..
                    ',"changed":1,"samples":[[3,42,1,101,12288,0]]}'
            end
            turn=5; boundary()
        """)
        self.assertEqual(lua.eval('table.concat(packet[1], ",")'), '3,42,1,101,-12288')
        self.assertEqual(lua.eval('table.concat(packet[2], ",")'), '3,42,3,100,12288')
        self.assertEqual(lua.eval('table.concat(packet[3], ",")'), '3,42,3,102,-65536')
        self.assertIn('CSC_AI_BAKERS_DISTRICT_SAMPLES turn=5 previousVersion=4 samples=[[3,42,1,101,12288,0]]',
                      messages)
        lua.execute("""
            CE_AIDistrictScoresStatus=function()
                local rows = {}
                for i = 1, 33 do rows[i] = '[3,42,1,'..(100+i)..',12288,0]' end
                return '{"ready":1,"faults":0,"version":'..version..
                    ',"changed":33,"samples":['..table.concat(rows, ',')..']}'
            end
            turn=6; boundary()
        """)
        chunks = [line for line in messages if 'CSC_AI_BAKERS_DISTRICT_SAMPLES turn=6 ' in line]
        self.assertEqual([line.count('[3,42,1,') for line in chunks], [16, 16, 1])
        self.assertTrue(all(len(line) < 1500 and line.endswith(']]') for line in chunks))
        lua.execute("CSC_AI_QuarterSiteForecasts=function() error('fixture') end; turn=7; boundary()")
        self.assertEqual(lua.eval('#packet'), 1)
        self.assertEqual(lua.eval('table.concat(packet[1], ",")'), '3,42,1,101,-12288')
        lua.execute("""
            GameInfo.Civics={CIVIC_FEUDALISM={Index=7}}
            Players[3].GetCulture=function() return {HasCivic=function(_, i) return i==7 end} end
            city.GetProperty=function() return 0 end
            city.GetBuildings=function()
                return {HasBuilding=function(_, i) return i==9 end, IsPillaged=function() return false end,
                    GetBuildingLocation=function() return 100 end}
            end
            local customer={GetIndex=function() return 99 end, GetOwner=function() return 3 end,
                GetX=function() return 9 end, GetY=function() return 10 end,
                GetDistrictType=function() return 0 end, GetResourceType=function() return -1 end}
            Map.GetAdjacentPlots=function() return {pasture,customer} end
            local getCity=Cities.GetPlotPurchaseCity
            hasGranary = true
            Cities.GetPlotPurchaseCity=function(plot)
                if plot~=customer then return getCity(plot) end
                return {GetOwner=function() return 3 end, GetID=function() return 77 end, GetBuildings=function()
                    return {HasBuilding=function(_, i) return i==8 and hasGranary end,
                        IsPillaged=function() return granaryPillaged == true end,
                        GetBuildingLocation=function() return 99 end}
                end}
            end
            CE_AIBuilderProtectionBid=function(...) builders[#builders+1]={...}; return 1 end
            CE_AIBuilderProtectionStatus=function()
                return '{"ready":1,"faults":0,"maxBidQ8":'..bidLimit..'}'
            end
            bidLimit=8192; turn=8; boundary()
        """)
        self.assertEqual(lua.eval('table.concat(builders[1], ",")'), '3,42,101,5,8192')
        lua.execute('bidLimit=16384; turn=9; boundary()')
        self.assertEqual(lua.eval('table.concat(builders[1], ",")'), '3,42,101,5,14336')
        lua.execute('improvement=5; pillaged=false; turn=10; boundary()')
        self.assertEqual(lua.eval('table.concat(builders[1], ",")'), '3,42,101,5')
        lua.execute("""
            local begin = CE_AIDistrictScoresBegin
            CE_AIDistrictScoresBegin = function(...)
                nominations = {}
                return begin(...)
            end
            CE_AIBuildingNominationBid = function(...)
                nominations[#nominations+1] = {...}
                return 1
            end
            CE_AIBuildingNominationStatus = function()
                return '{"ready":1,"faults":0,"maxBidQ8":'..nominationLimit..'}'
            end
            nominationLimit = 32768
            city.GetID = function() return 42 end
            city.GetBuildings = function()
                return {HasBuilding=function(_, i) return i==9 and hasMill end,
                    IsPillaged=function() return millPillaged == true end,
                    GetBuildingLocation=function() return 100 end}
            end
            Map.GetPlot().IsRiver = function() return river end
            CityManager = {GetCity=function(player, id)
                assert(player==3 and id==42)
                return {GetBuildQueue=function()
                    return {CanProduce=function(_, hash, visible, immediate)
                        assert(visible==false and immediate==true)
                        return (hash==109 and river) or (hash==110 and machinery)
                    end}
                end}
            end}
            machinery, river, hasMill = true, false, false
            turn=11; boundary()
        """)
        self.assertEqual(lua.eval('#nominations'), 1)
        self.assertEqual(lua.eval('table.concat(nominations[1], ",")'), '3,42,10,32768')
        lua.execute('nominationLimit=131072; river=true; turn=12; boundary()')
        self.assertEqual(lua.eval('#nominations'), 2)
        self.assertEqual(lua.eval('table.concat(nominations[2], ",")'), '3,42,9,114688')
        lua.execute('machinery=false; turn=13; boundary()')
        self.assertEqual(lua.eval('#nominations'), 1)
        self.assertEqual(lua.eval('table.concat(nominations[1], ",")'), '3,42,9,114688')
        lua.execute('hasMill=true; turn=14; boundary()')
        self.assertEqual(lua.eval('#nominations'), 0)
        lua.execute('hasMill=false; pillaged=true; turn=15; boundary()')
        self.assertEqual(lua.eval('#nominations'), 0)
        lua.execute("""
            Players[3].GetCulture = function() return {HasCivic=function() return false end} end
            hasMill, hasGranary = true, false
            CityManager = {GetCity=function(player, id)
                assert(player==3 and id==77)
                return {GetBuildQueue=function()
                    return {CanProduce=function(_, hash, visible, immediate)
                        assert(visible==false and immediate==true)
                        return hash==111
                    end}
                end}
            end}
            turn=16; boundary()
        """)
        self.assertEqual(lua.eval('#nominations'), 1)
        self.assertEqual(lua.eval('table.concat(nominations[1], ",")'), '3,77,11,13312')
        lua.execute("""
            local getCities = Players[3].GetCities
            local getPlot = Map.GetPlot
            local secondQuarter = setmetatable({
                GetX=function() return 11 end,
                GetIndex=function() return 102 end,
            }, {__index=getPlot()})
            local secondCity = setmetatable({
                GetID=function() return 43 end,
                GetDistricts=function()
                    return {GetNumDistricts=function() return 1 end,
                            GetDistrictByIndex=function() return secondQuarter end}
                end,
                GetBuildings=function()
                    local buildings = city:GetBuildings()
                    buildings.GetBuildingLocation=function() return 102 end
                    return buildings
                end,
            }, {__index=city})
            Map.GetPlot=function(x, y)
                if x==11 then return secondQuarter end
                return getPlot(x,y)
            end
            Players[3].GetCities=function()
                return {Members=function() return ipairs({city,secondCity}) end}
            end
            turn=17; boundary()
            Map.GetPlot = getPlot
            Players[3].GetCities = getCities
        """)
        self.assertEqual(lua.eval('#nominations'), 1)
        self.assertEqual(lua.eval('table.concat(nominations[1], ",")'), '3,77,11,13312')
        lua.execute('hasGranary=true; granaryPillaged=true; turn=18; boundary()')
        self.assertEqual(lua.eval('#nominations'), 0)
        lua.execute('hasGranary=false; millPillaged=true; turn=19; boundary()')
        self.assertEqual(lua.eval('#nominations'), 0)
        lua.execute('turn=20; Players[3].IsHuman=function() return true end; boundary()')
        self.assertIsNone(lua.eval('packet'))


if __name__ == '__main__':
    unittest.main()
