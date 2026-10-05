-- Disposable NEW GAME only. Creates a compact owned district/resource fixture.
-- Execute in the CSC_AdjacencyGameplay tuner state, not in a saved campaign.
assert(Game.GetCurrentGameTurn()==1,'Fixture must run in a fresh turn-1 test game');
local player=Players[0];
local city=nil;
for _,existing in player:GetCities():Members() do city=existing; break; end
if not city then
    for _,unit in player:GetUnits():Members() do
        if unit:GetType()==GameInfo.Units.UNIT_SETTLER.Index then
            city=player:GetCities():Create(unit:GetX(),unit:GetY());
            break;
        end
    end
end
assert(city,'Could not found a fixture city');
CSC_AdjacencyFixture={CityID=city:GetID(),PlayerID=0,Plots={},Districts={}};
city:ChangePopulation(30-city:GetPopulation());
local center=Map.GetPlot(city:GetX(),city:GetY());
local ring=Map.GetAdjacentPlots(center:GetX(),center:GetY());
local quarterTypes={'DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER',
    'DISTRICT_COMMERCIAL_HUB','DISTRICT_HOLY_SITE','DISTRICT_THEATER'};
for index,districtType in ipairs(quarterTypes) do
    local plot=ring[index];
    assert(plot and plot:GetOwner()==0,'Fixture district plot is not owned');
    if plot:GetDistrictType()==-1 then
        ResourceBuilder.SetResourceType(plot,-1);
        TerrainBuilder.SetTerrainType(plot,GameInfo.Terrains.TERRAIN_GRASS.Index);
        if plot:GetFeatureType()>=0 then TerrainBuilder.SetFeatureType(plot,-1); end
        city:GetBuildQueue():CreateIncompleteDistrict(GameInfo.Districts[districtType].Index,plot:GetIndex(),100);
    end
    CSC_AdjacencyFixture.Plots[#CSC_AdjacencyFixture.Plots+1]=plot:GetIndex();
    CSC_AdjacencyFixture.Districts[#CSC_AdjacencyFixture.Districts+1]=districtType;
end
local placed={};
for i,quarter in ipairs({'BAKERS','TAILORS'}) do
    local plot=Map.GetPlotByIndex(CSC_AdjacencyFixture.Plots[i]);
    for _,class in ipairs({'BASE','SPEC'}) do
        local tag='CLASS_CSC_'..quarter..'_'..class;
        local resources={};
        for kind in pairs(CSC_Adjacency.Tags[tag] or {}) do
            if GameInfo.Resources[kind] then resources[#resources+1]=kind; end
        end
        table.sort(resources);
        local resource=GameInfo.Resources[resources[1]];
        assert(resource,'Missing material fixture resource for '..tag);
        if resource.PrereqTech then player:GetTechs():SetTech(GameInfo.Technologies[resource.PrereqTech].Index,true); end
        if resource.PrereqCivic then player:GetCulture():SetCivic(GameInfo.Civics[resource.PrereqCivic].Index,true); end
        for _,neighbor in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY())) do
            if neighbor:GetOwner()==0 and neighbor:GetDistrictType()==-1 and not placed[neighbor:GetIndex()] then
                ResourceBuilder.SetResourceType(neighbor,resource.Index,1);
                placed[neighbor:GetIndex()]=true;
                print('CSC_FIXTURE_RESOURCE',quarter,class,resource.ResourceType,neighbor:GetIndex());
                break;
            end
        end
    end
end
CSC_RefreshAdjacencies();
print('CSC_FIXTURE_READY',city:GetID(),center:GetIndex(),#CSC_AdjacencyFixture.Plots);
