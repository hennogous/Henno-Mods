-- Loaded in DMT's calculator context when the Workshop mod is active. Its
-- imported script owns the pin cache, vanilla forecasts, refresh and broadcast.
include('dmt_yieldcalculator');
local getDmtYields = GetBonusYields;
local convertDmtYields = ConvertToYieldString;
if not getDmtYields or not convertDmtYields or not GetRealizedPlotFeatures or not GetMapPinSubject then return; end

include('CSC_AdjacencyPresentation');
local A = CSC_Adjacency;

-- DMT only shows its yield tooltip when the badge string is nonempty. Its
-- update loop formats the same yield table returned by GetBonusYields, so
-- attach forecast-only display text by table identity without adding a yield.
local forecastBadges = setmetatable({}, {__mode = 'k'});

function ConvertToYieldString(yields)
    return forecastBadges[yields] or convertDmtYields(yields);
end

local resourceSources = {FROM_RINGS_TYPETAG_RESOURCE=true, FROM_RINGS_CAO_RESOURCE=true,
    FROM_RINGS_CAO_RESOURCE_CLASS=true};
local districtSources = {FROM_RINGS_TYPETAG_DISTRICT=true, FROM_RINGS_CAO_DISTRICT=true};

local function ProjectedTiles(playerID)
    local cache = {};
    return function(plot, rule)
        if not IsPlotRevealedToPlayer(plot, playerID) then return nil; end
        local resourceSource = resourceSources[rule.AdjacencyType];
        if not resourceSource and not districtSources[rule.AdjacencyType] then return plot; end

        local index = plot:GetIndex();
        local tile = cache[index];
        if not tile then
            local owner = plot:GetOwner();
            local tack = GetMapPinSubject(playerID, plot:GetX(), plot:GetY());
            -- DMT uses these projected features for its own yields. Placement
            -- warnings are a separate pass and must not affect this read.
            local features = GetRealizedPlotFeatures(playerID, plot, tack);
            local districtType = features[AdjacencyBonusTypes.ADJACENCY_DISTRICT];
            local resourceType = features[AdjacencyBonusTypes.ADJACENCY_RESOURCE];
            local district = districtType and GameInfo.Districts[districtType];
            local resource = resourceType and GameInfo.Resources[resourceType];
            -- For CSC's ownership gate, a neutral tile can be claimed in the plan.
            if owner == -1 then owner = playerID; end
            tile = {Owner=owner, District=district and district.Index or -1,
                Resource=resource and resource.Index or -1};
            cache[index] = tile;
        end
        return {
            GetOwner=function() return tile.Owner; end,
            GetDistrictType=function() return tile.District; end,
            GetResourceType=function() return tile.Resource; end
        };
    end;
end

local function LiveCity(plot, district, playerID)
    if plot:GetOwner() == playerID and plot:GetDistrictType() == district.Index then
        return Cities.GetPlotPurchaseCity(plot:GetX(), plot:GetY());
    end
end

local function HasMill(city, rules)
    if not city then return false; end
    for _,rule in ipairs(rules) do
        if A.UnitSteps[rule.ID] and city:GetBuildings():HasBuilding(GameInfo.Buildings[rule.WhoIsTheOwner].Index) then
            return true;
        end
    end
    return false;
end

function GetBonusYields(playerID, pin)
    local yields, tooltip = getDmtYields(playerID, pin);
    local rules = pin.Type == 'DISTRICT' and A.ByDistrict[pin.Key];
    if not rules then return yields, tooltip; end
    local plot = Map.GetPlot(pin.X, pin.Y);
    if not plot or not IsPlotRevealedToPlayer(plot, playerID) then return yields, tooltip; end

    local city = LiveCity(plot, GameInfo.Districts[pin.Key], playerID);
    local project = ProjectedTiles(playerID);
    local lines = {};
    if tooltip and tooltip ~= '' then lines[1] = tooltip; end
    for _,rule in ipairs(rules) do
        -- SelfBonus changes the district's base yields in the native game.
        -- Add it after DMT's adjacency multipliers and mirrored yields.
        if rule.ProvideType == 'SelfBonus' and A.Eligible(rule, city, playerID) then
            local count = A.Count(rule, plot, city, playerID, project);
            local amount = A.Amount(rule, count);
            if amount ~= 0 then
                yields[rule.YieldType] = (yields[rule.YieldType] or 0) + amount;
                lines[#lines+1] = A.PreviewLine(rule, amount, count);
            end
        end
    end
    if pin.Key == 'DISTRICT_CSC_BAKERS_QUARTER' and not HasMill(city, rules) then
        local millBadge, millOptions = A.MillPlacementText(plot, city, playerID);
        if millOptions ~= '' then
            table.insert(lines, 1, millOptions);
            if next(yields) == nil then forecastBadges[yields] = millBadge; end
        end
    end
    return yields, table.concat(lines, '[NEWLINE]');
end

print('CSC Detailed Map Tacks forecast loaded');
