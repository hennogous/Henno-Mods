assert(Game.GetCurrentGameTurn()==1,'Disposable turn-1 game required');
local A=CSC_Adjacency;
local fixture=CSC_AdjacencyFixture;
local player=Players[fixture.PlayerID];
local city=player:GetCities():FindID(fixture.CityID);
local quarterPlots={Map.GetPlotByIndex(fixture.Plots[1]),Map.GetPlotByIndex(fixture.Plots[2])};
fixture.MaterialPlots={};
-- Expand the city's owned land around the test Quarters, then place both kinds
-- of material. Native terrain/resource builders deliberately bypass placement.
local used={};
for index,quarter in ipairs({'BAKERS','TAILORS'}) do
    local plot=quarterPlots[index];
    for _,neighbor in ipairs(A.PlotsInBand(plot,1,1)) do
        if neighbor:GetDistrictType()==-1 then
            WorldBuilder.CityManager():SetPlotOwner(neighbor:GetX(),neighbor:GetY(),0,city:GetID());
            ResourceBuilder.SetResourceType(neighbor,-1);
            TerrainBuilder.SetTerrainType(neighbor,GameInfo.Terrains.TERRAIN_GRASS.Index);
            if neighbor:GetFeatureType()>=0 then TerrainBuilder.SetFeatureType(neighbor,-1); end
        end
    end
    for _,class in ipairs({'BASE','SPEC'}) do
        local tag='CLASS_CSC_'..quarter..'_'..class;
        local names={}; for kind in pairs(A.Tags[tag]) do names[#names+1]=kind; end; table.sort(names);
        local definition=GameInfo.Resources[names[1]];
        if definition.PrereqTech then player:GetTechs():SetTech(GameInfo.Technologies[definition.PrereqTech].Index,true); end
        if definition.PrereqCivic then player:GetCulture():SetCivic(GameInfo.Civics[definition.PrereqCivic].Index,true); end
        local chosen=nil;
        for _,neighbor in ipairs(A.PlotsInBand(plot,1,1)) do
            if neighbor:GetDistrictType()==-1 and not used[neighbor:GetIndex()] then chosen=neighbor; break; end
        end
        assert(chosen,'No space for material fixture');
        used[chosen:GetIndex()]=true;
        ResourceBuilder.SetResourceType(chosen,definition.Index,1);
        fixture.MaterialPlots[#fixture.MaterialPlots+1]=chosen:GetIndex();
    end
end
-- An overlapping band can remove an earlier material while preparing terrain.
-- Re-place the four selected resources after all terrain preparation finishes.
for index,quarter in ipairs({'BAKERS','TAILORS'}) do
    for offset,class in ipairs({'BASE','SPEC'}) do
        local names={}; for kind in pairs(A.Tags['CLASS_CSC_'..quarter..'_'..class]) do names[#names+1]=kind; end; table.sort(names);
        ResourceBuilder.SetResourceType(Map.GetPlotByIndex(fixture.MaterialPlots[(index-1)*2+offset]),GameInfo.Resources[names[1]].Index,1);
    end
end
for _,kind in ipairs({'BUILDING_CSC_BAKERS_WATER_MILL','BUILDING_CSC_BAKERS_WIND_MILL'}) do
    city:GetBuildings():RemoveBuilding(GameInfo.Buildings[kind].Index);
end
TerrainBuilder.SetTerrainType(quarterPlots[1],GameInfo.Terrains.TERRAIN_GRASS_HILLS.Index);
TerrainBuilder.SetWOfRiver(quarterPlots[1],true,FlowDirectionTypes.FLOWDIRECTION_SOUTH);
TerrainBuilder.SetNWOfRiver(quarterPlots[2],true,FlowDirectionTypes.FLOWDIRECTION_NORTHEAST);
CSC_RefreshAdjacencies();
for _,quarter in ipairs({'BAKERS','TAILORS'}) do
    local plot=quarterPlots[quarter=='BAKERS' and 1 or 2];
    for _,class in ipairs({'BASE','SPEC'}) do
        assert(plot:GetProperty('CSC_ADJ_CSC_'..quarter..'_PRODUCTION_FROM_'..class..'_TOTAL')>=1,quarter..' '..class);
    end
end
fixture.Baseline={};
function CSC_LiveDistricts()
    local result={};
    for _,c in player:GetCities():Members() do
        local districts=c:GetDistricts();
        for i=0,districts:GetNumDistricts()-1 do result[#result+1]=districts:GetDistrictByIndex(i); end
    end
    return result;
end
function CSC_LiveZeroBits()
    for _,district in ipairs(CSC_LiveDistricts()) do
        local plot=Map.GetPlot(district:GetX(),district:GetY());
        for _,rule in ipairs(A.ByDistrict[GameInfo.Districts[district:GetType()].DistrictType] or {}) do A.Write(plot,rule,0); end
    end
end
function CSC_LiveCaptureBaseline()
    fixture.Baseline={};
    for _,district in ipairs(CSC_LiveDistricts()) do
        local plot=Map.GetPlot(district:GetX(),district:GetY());
        fixture.Baseline[plot:GetIndex()]={};
        for yield in GameInfo.Yields() do fixture.Baseline[plot:GetIndex()][yield.Index]=district:GetYield(yield.Index); end
    end
end
function CSC_LiveAssertYields(label)
    for _,district in ipairs(CSC_LiveDistricts()) do
        local plot=Map.GetPlot(district:GetX(),district:GetY());
        local kind=GameInfo.Districts[district:GetType()].DistrictType;
        local expected={};
        for _,rule in ipairs(A.ByDistrict[kind] or {}) do
            assert(rule.ProvideType=='SelfBonus','Unexpected live fixture provider');
            local amount=plot:GetProperty('CSC_ADJ_'..rule.ID..'_ENCODED_AMOUNT') or 0;
            local yield=GameInfo.Yields[rule.YieldType].Index;
            expected[yield]=(expected[yield] or 0)+amount;
        end
        for yield in GameInfo.Yields() do
            local baseline=fixture.Baseline[plot:GetIndex()][yield.Index];
            local actual=district:GetYield(yield.Index);
            local delta=expected[yield.Index] or 0;
            print('CSC_LIVE_YIELD',label,kind,yield.YieldType,baseline,actual,delta);
            assert(math.abs(actual-baseline-delta)<0.001,kind..' '..yield.YieldType..' native yield mismatch');
        end
    end
end
function CSC_LiveRemoveMaterialOwner()
    local plot=Map.GetPlotByIndex(fixture.MaterialPlots[1]);
    local rule=nil; for _,r in ipairs(A.Rules) do if r.ID=='CSC_BAKERS_PRODUCTION_FROM_BASE' then rule=r; end; end
    local before=A.Count(rule,quarterPlots[1],city,0);
    WorldBuilder.CityManager():SetPlotOwner(plot:GetX(),plot:GetY(),false);
    CSC_RefreshAdjacencies();
    assert(A.Count(rule,quarterPlots[1],city,0)==before-1,'Ownership transition must remove exactly one material');
end
function CSC_LiveEnableRemoteMill()
    local remote=nil;
    for _,c in player:GetCities():Members() do if c:GetID()~=city:GetID() then remote=c; break; end; end
    if not remote then
        for _,plot in ipairs(A.PlotsInBand(Map.GetPlot(city:GetX(),city:GetY()),6,6)) do
            if plot:GetOwner()==-1 and plot:GetDistrictType()==-1 then
                ResourceBuilder.SetResourceType(plot,-1);
                TerrainBuilder.SetTerrainType(plot,GameInfo.Terrains.TERRAIN_GRASS.Index);
                if plot:GetFeatureType()>=0 then TerrainBuilder.SetFeatureType(plot,-1); end
                remote=player:GetCities():Create(plot:GetX(),plot:GetY()); break;
            end
        end
    end
    assert(remote,'Could not create a remote mill city'); fixture.RemoteCity=remote:GetID();
    local host=nil;
    local districts=remote:GetDistricts();
    for i=0,districts:GetNumDistricts()-1 do
        local district=districts:GetDistrictByIndex(i);
        if district:GetType()==GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index then host=Map.GetPlot(district:GetX(),district:GetY()); end
    end
    if not host then
        for _,plot in ipairs(Map.GetAdjacentPlots(remote:GetX(),remote:GetY())) do
            if plot:GetDistrictType()==-1 then
                WorldBuilder.CityManager():SetPlotOwner(plot:GetX(),plot:GetY(),0,remote:GetID());
                ResourceBuilder.SetResourceType(plot,-1);
                TerrainBuilder.SetTerrainType(plot,GameInfo.Terrains.TERRAIN_GRASS.Index);
                if plot:GetFeatureType()>=0 then TerrainBuilder.SetFeatureType(plot,-1); end
                remote:GetBuildQueue():CreateIncompleteDistrict(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index,plot:GetIndex(),100);
                host=plot; break;
            end
        end
    end
    assert(host,'Missing remote Quarter');
    local building=GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL.Index;
    remote:GetBuildQueue():CreateBuilding(building,host:GetIndex());
    assert(remote:GetBuildings():HasBuilding(building));
    assert(not city:GetBuildings():HasBuilding(building));
    CSC_RefreshAdjacencies();
    assert(quarterPlots[1]:GetProperty('CSC_ADJ_CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER_ENCODED_AMOUNT')==math.floor(quarterPlots[1]:GetRiverCrossingCount()*0.5));
end
function CSC_LiveRemoveRemoteMill()
    player:GetCities():FindID(fixture.RemoteCity):GetBuildings():RemoveBuilding(GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL.Index);
    CSC_RefreshAdjacencies();
    assert(quarterPlots[1]:GetProperty('CSC_ADJ_CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER_ENCODED_AMOUNT')==0);
end
function CSC_LiveAssertSources()
    local count=0;
    for name in pairs(A.Sources) do
        A.Count({AdjacencyType=name,CustomAdjacentObject='NONE',MinRings=1,MaxRings=1},quarterPlots[1],city,0);
        count=count+1;
    end
    assert(count==55);
end
