"""Exercise the candidate's stock property lifecycle without a game or CE."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


HERE = Path(__file__).parent
POLICY = (HERE/'city_material_cue_choice.lua').read_text() + '\n' + (HERE/'local_material_guidance.lua').read_text()
SETUP = """
turn=1; connected=false; human=false; built=false; good=true; scans=0; attaches=0
function object()
    local values={}
    return {GetProperty=function(_,k)return values[k]end,SetProperty=function(_,k,v)values[k]=v end}
end
function makeCity(id)
    local c=object()
    c.GetID=function()return id end
    c.GetX=function()return id end
    c.GetY=function()return 0 end
    c.GetDistricts=function()return {HasDistrict=function()return built end}end
    c.AttachModifierByID=function(_,rule) attaches=attaches+1; lastRule=rule end
    return c
end
Game=object();Game.GetCurrentGameTurn=function()return turn end
GameConfiguration={IsAnyMultiplayer=function()return connected end,IsHotseat=function()return false end}
centers={};cities={}
for i=1,2 do
    local index=i
    centers[i]=object();centers[i].GetIndex=function()return index end
    cities[i]=makeCity(i)
end
Map={GetPlot=function(x,y)return centers[x]end}
player=object();player.GetID=function()return 2 end;player.IsHuman=function()return human end
player.GetCities=function()return {Members=function()return ipairs(cities)end}end
PlayerManager={GetAliveMajors=function()return {player}end}
GameEvents={OnGameTurnStarted={Add=function(f)tick=f end}}
terrainKeys={'PLAINS'};profiles={{district={Index=4,DistrictType='TEST'}}}
function citySites()return {} end
function ownedSites()
    scans=scans+1
    return {{count={PLAINS=3},materialTerrain=good and {PLAINS=true} or {},customerRank=1},
            {count={PLAINS=2},materialTerrain={},customerRank=0}}
end
print=function(kind,...)if kind=='CSC_LOCAL_CUE_FAULT' then fault=true end end
"""


class LocalMaterialGuidance(unittest.TestCase):
    def test_geometry_shared_across_quarters_and_hidden_rings_defer(self):
        vm = LuaRuntime()
        vm.execute("""
        function catalogue(rows,key)
            local t={}
            for _,r in ipairs(rows)do if key then t[r[key]]=r;t[r.Index]=r end end
            return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
        end
        local a='DISTRICT_CSC_A_QUARTER';local b='DISTRICT_CSC_B_QUARTER'
        GameInfo={
            Districts=catalogue({{DistrictType=a,Index=1},{DistrictType=b,Index=2},
                {DistrictType='HARBOR',Index=3,Coast=1}},'DistrictType'),
            CSC_QuarterMaterialAdjacencyConfig=catalogue({
                {QuarterKey='A',SourceTag='CLASS_CSC_A_BASE',SourceFilter='',AdjacencyType='FROM_RINGS_TYPETAG_RESOURCE'},
                {QuarterKey='B',SourceTag='CLASS_CSC_B_BASE',SourceFilter='',AdjacencyType='FROM_RINGS_TYPETAG_RESOURCE'}}),
            Resources=catalogue({{ResourceType='COTTON',Index=0},{ResourceType='MOD_DYE',Index=1}},'ResourceType'),
            TypeTags=catalogue({{Type='COTTON',Tag='CLASS_CSC_A_BASE'},{Type='COTTON',Tag='CLASS_CSC_B_BASE'},
                {Type='MOD_DYE',Tag='CLASS_CSC_B_SPEC'}}),
            Terrains=catalogue({{TerrainType='PLAINS',Index=0},{TerrainType='TERRAIN_COAST',Index=1,Water=1}},'TerrainType'),
            CSC_QuarterCustomerBuildings=catalogue({{QuarterKey='A',ProducerStage=2,DistrictType='HARBOR'}}),
            DistrictReplaces=catalogue({})}
        function plot(id,owner,terrain,resource)
           return {GetIndex=function()return id end,GetX=function()return id end,GetY=function()return 0 end,
             GetOwner=function()return owner end,GetTerrainType=function()return terrain end,GetResourceType=function()return resource end,
             GetDistrictType=function()return -1 end,GetFeatureType=function()return -1 end,CanHaveDistrict=function()return true end}
        end
        local first=plot(1,2,0,-1);local second=plot(2,2,0,-1)
        local cotton=plot(3,2,0,0);local coast=plot(4,-1,1,-1)
        local empty=plot(5,2,0,-1);local dye=plot(6,2,0,1)
        rings={{cotton,coast,empty,dye},{empty}}
        city={GetX=function()return 1 end,GetY=function()return 0 end,GetID=function()return 7 end}
        Cities={GetPlotPurchaseCity=function()return city end}; reads=0;hide=false
        Map={GetPlotXYWithRangeCheck=function(x,y,dx,dy)if dy==0 and dx==1 then return first elseif dy==0 and dx==2 then return second end end,
            GetAdjacentPlot=function(x,y,d)reads=reads+1;return rings[x][d+1]end}
        Players={[2]={}};PlayersVisibility={[2]={IsRevealed=function(_,x,y)return not (hide and x==5)end}}
        """)
        source = (HERE/'city_material_cue_choice.lua').read_text() + '\n' + (HERE/'city_material_cue_sites.lua').read_text()
        vm.execute(source + """
        local view=citySites(city,2)
        local a=ownedSites(city,2,profiles[1],view);local b=ownedSites(city,2,profiles[2],view)
        assert(reads==12 and #a==2 and #b==2)
        assert(not a[1].hasSpecialty and b[1].hasSpecialty)
        local first=selectMaterialCue(a,terrainKeys);local second=selectMaterialCue(b,terrainKeys)
        assert(first.cutoff==2 and first.hits==1 and first.customerRank==1 and second.customerRank==0)
        hide=true;assert(#ownedSites(city,2,profiles[1],citySites(city,2))==0)
        hide=false;pairPolicy={guardFrontier=true}
        local neutral=plot(7,-1,0,-1)
        neutral.IsWater=function()return false end;neutral.IsImpassable=function()return false end
        local original=Map.GetPlotXYWithRangeCheck
        Map.GetPlotXYWithRangeCheck=function(x,y,dx,dy)
            if dy==0 and dx==3 then return neutral end
            return original(x,y,dx,dy)
        end
        rings[7]={plot(8,-1,0,0),plot(9,-1,0,-1)}
        local frontier=ownedSites(city,2,profiles[1],citySites(city,2))
        assert(#frontier==2 and #frontier.frontierWeak==1)
        assert(frontier.frontierWeak[1].count.PLAINS==2)
        neutral.CanHaveDistrict=function()return false end
        assert(#ownedSites(city,2,profiles[1],citySites(city,2)).frontierWeak==0)
        """)

    def test_specialty_breaks_ties_on_the_same_base_and_customer_site(self):
        vm = LuaRuntime()
        vm.execute((HERE/'city_material_cue_choice.lua').read_text() + """
        local a={count={A=1},materialTerrain={A=true},customerRank=1}
        local b={count={B=1},materialTerrain={B=true},customerRank=1,hasSpecialty=true}
        local bad={count={},materialTerrain={},customerRank=2,hasSpecialty=true}
        local function pick()return selectMaterialCue({a,b,bad},{'A','B'}).terrain end
        assert(pick()=='B')
        a.customerRank=2;assert(pick()=='A')
        b.materialTerrain={};b.customerRank=2;assert(pick()=='A')
        """)

    def test_budget_reloads_withdrawal_and_reattachment(self):
        vm = LuaRuntime()
        vm.execute(SETUP)
        vm.execute(POLICY)
        vm.execute("assert(scans==1 and attaches==1 and centers[1]:GetProperty(lastRule)==1)")
        vm.execute(POLICY)
        vm.execute("tick(); assert(scans==1 and attaches==1)")
        vm.execute("turn=2; tick(); assert(scans==2 and attaches==2)")
        vm.execute("turn=13; good=false; tick(); assert(centers[1]:GetProperty(lastRule)==0)")
        vm.execute("turn=14; built=true; tick(); assert(scans==3 and centers[2]:GetProperty(lastRule)==0)")
        vm.execute("turn=25; good=true; built=false; tick(); assert(attaches==2 and centers[1]:GetProperty(lastRule)==1)")
        vm.execute("turn=26; human=true; tick(); assert(centers[1]:GetProperty(lastRule)==0 and not fault)")

    def test_multiplayer_and_unidentified_old_seat(self):
        vm = LuaRuntime()
        vm.execute(SETUP + '\nconnected=true')
        vm.execute(POLICY)
        vm.execute("assert(not lastRule and scans==0 and not Game:GetProperty('CSC_AI_OriginalHuman_2'))")
        vm.execute("connected=false;turn=55;tick();assert(scans==0 and not fault)")

    def test_acquisition_requests_one_bounded_review(self):
        vm=LuaRuntime()
        vm.execute(SETUP+"""
        pairPolicy={guardFrontier=true,choose=function()end,update=function()end}
        CityManager={GetCity=function(_,id)return cities[id]end}
        Events={CityTileOwnershipChanged={Add=function(f)landChange=f end}}
        """)
        vm.execute((HERE/'local_material_guidance.lua').read_text())
        vm.execute("""
        turn=2;tick();assert(scans==2)
        landChange(2,1);landChange(2,1);tick();assert(scans==2)
        turn=3;tick();assert(scans==3)
        turn=4;tick();assert(scans==3)
        """)


if __name__ == '__main__':
    unittest.main()
