-- Only gameplay writes properties; UI previews evaluate without mutations.
include('CSC_AdjacencyCore');
local A = CSC_Adjacency;
local ready = false;
local refreshing = false;
local previousPlots = {};

local function refresh()
    local currentPlots = {};
    local sites = {};
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
                        sites[#sites+1] = {Plot=plot, Rules=rules, District=district, City=city, PlayerID=player:GetID()};
                    end
                end
            end
        end
    end
    -- Native collection order is not a mutation-order contract.
    table.sort(sites,function(a,b) return a.Plot:GetIndex()<b.Plot:GetIndex(); end);
    for _,site in ipairs(sites) do
        currentPlots[site.Plot:GetIndex()] = site.Rules;
        for _,rule in ipairs(site.Rules) do
            local count = 0;
            if site.District:IsComplete() and A.Eligible(rule,site.City,site.PlayerID) then
                count = A.Count(rule,site.Plot,site.City,site.PlayerID);
            end
            A.Write(site.Plot,rule,count);
        end
    end
    -- Remove stale properties after demolition, capture or district replacement.
    local staleIndexes = {};
    for index in pairs(previousPlots) do staleIndexes[#staleIndexes+1]=index; end
    table.sort(staleIndexes);
    for _,index in ipairs(staleIndexes) do
        local rules = previousPlots[index];
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
    -- Property writes can cause nested refresh events. Always release the guard,
    -- including on errors, so one failed pass cannot disable later reconciliation.
    if not ready or refreshing then return; end
    refreshing = true;
    local ok,message = pcall(refresh);
    refreshing = false;
    if not ok then error(message,0); end
end

local function initialize()
    A.Initialize();
    ready = true;
    print('CSC adjacencies: ' .. #A.Rules .. ' bundled rules initialized');
end

-- Full refresh scans relevant districts, never the whole map. Neighbor ownership
-- and wider bands can affect several players, so event callbacks recompute all.
for _,name in ipairs({
    'DistrictBuildProgressChanged','DistrictAddedToMap',
    'DistrictRemovedFromMap','BuildingAddedToMap','BuildingRemovedFromMap','BuildingChanged',
    'CityProductionCompleted','CityAddedToMap','CityRemovedFromMap','CityTransfered',
    'ImprovementAddedToMap','ImprovementRemovedFromMap','ImprovementChanged',
    'ResourceAddedToMap','ResourceRemovedFromMap','ResourceChanged','CityTileOwnershipChanged',
    'ImprovementPillaged','DistrictPillaged','TerrainChanged','FeatureAddedToMap','FeatureRemovedFromMap',
    'RouteAddedToMap','RouteRemovedFromMap',
    'ResearchCompleted','CivicCompleted','GovernmentPolicyChanged',
    'GovernmentPolicyObsoleted','GovernmentChanged'
}) do
    if Events[name] then Events[name].Add(CSC_RefreshAdjacencies); end
end
local function refreshForUnits()
    -- Ordinary Quarter rules do not depend on units. Avoid a district scan on
    -- every unit move unless a loaded rule actually uses unit/aircraft state.
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
-- Loading a view/rejoining is local to one client. Initialize read-only caches
-- here; reconcile saved properties only from synchronized gameplay events.
if GameEvents and GameEvents.PlayerTurnStarted then GameEvents.PlayerTurnStarted.Add(CSC_RefreshAdjacencies); end
if GameEvents and GameEvents.OnGameTurnStarted then GameEvents.OnGameTurnStarted.Add(CSC_RefreshAdjacencies); end
initialize();
