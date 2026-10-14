-- Only gameplay writes properties; UI previews evaluate without mutations.
include('CSC_AdjacencyCore');
local A = CSC_Adjacency;
local ready = false;
local refreshing = false;
local previousPlots = {};

local function refresh()
    local currentPlots = {};
    for _,player in ipairs(PlayerManager.GetAliveMajors()) do
        for _,city in player:GetCities():Members() do
            local districts = city:GetDistricts();
            for index=0,districts:GetNumDistricts()-1 do
                local district = districts:GetDistrictByIndex(index);
                local definition = GameInfo.Districts[district:GetType()];
                local rules = definition and A.ByDistrict[definition.DistrictType];
                if rules then
                    local plot = Map.GetPlot(district:GetX(),district:GetY());
                    if plot then
                        currentPlots[plot:GetIndex()] = rules;
                        for _,rule in ipairs(rules) do
                            local count = 0;
                            if district:IsComplete() and A.Eligible(rule,city,player:GetID()) then
                                count = A.Count(rule,plot,city,player:GetID());
                            end
                            A.Write(plot,rule,count);
                        end
                    end
                end
            end
        end
    end
    -- Remove stale properties after demolition, capture or district replacement.
    for index,rules in pairs(previousPlots) do
        local plot = Map.GetPlotByIndex(index);
        if plot then
            local live = {};
            for _,rule in ipairs(currentPlots[index] or {}) do live[rule.ID]=true; end
            for _,rule in ipairs(rules) do if not live[rule.ID] then A.Write(plot,rule,0); end end
        end
    end
    previousPlots = currentPlots;
end

function CSC_RefreshAdjacencies()
    if not ready or refreshing then return; end
    refreshing = true;
    local ok,message = pcall(refresh);
    refreshing = false;
    if not ok then error(message,0); end
end

local function initialize()
    A.Initialize();
    ready = true;
    CSC_RefreshAdjacencies();
    print('CSC adjacencies: ' .. #A.Rules .. ' bundled rules initialized');
end

-- Full refresh scans relevant districts, never the whole map. Neighbor ownership
-- and wider bands can affect several players, so event callbacks recompute all.
for _,name in ipairs({
    'PlayerTurnActivated','DistrictBuildProgressChanged','DistrictAddedToMap',
    'DistrictRemovedFromMap','BuildingAddedToMap','BuildingRemovedFromMap','BuildingChanged',
    'CityProductionCompleted','CityAddedToMap','CityRemovedFromMap','CityTransfered',
    'ImprovementAddedToMap','ImprovementRemovedFromMap','ImprovementChanged',
    'ResourceAddedToMap','ResourceRemovedFromMap','ResourceChanged','PlotOwnershipChanged',
    'ImprovementPillaged','DistrictPillaged','TerrainChanged','FeatureAddedToMap','FeatureRemovedFromMap',
    'RouteAddedToMap','RouteRemovedFromMap',
    'ResearchCompleted','CivicCompleted','PolicyChanged','GovernmentChanged'
}) do
    if Events[name] then Events[name].Add(CSC_RefreshAdjacencies); end
end
local function refreshForUnits()
    for _,rule in ipairs(A.Rules) do
        if rule.AdjacencyType:find('UNIT',1,true) or rule.AdjacencyType:find('AIR',1,true) then
            CSC_RefreshAdjacencies(); return;
        end
    end
end
for _,name in ipairs({'UnitMoved','UnitAddedToMap','UnitRemovedFromMap','UnitPromoted','UnitUpgraded'}) do
    if Events[name] then Events[name].Add(refreshForUnits); end
end
if GameEvents and GameEvents.BuildingConstructed then GameEvents.BuildingConstructed.Add(CSC_RefreshAdjacencies); end
if Events.LoadGameViewStateDone then Events.LoadGameViewStateDone.Add(initialize); end
initialize();
