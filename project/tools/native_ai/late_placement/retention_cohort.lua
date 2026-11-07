-- Find working Bakers chains by their exact physical participants.
-- Gameplay records each player phase. The UI independently checks realized yields.
local mode = assert(CSC_BAKERS_COHORT_MODE)
local quarter = assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER).Index
local granary = assert(GameInfo.Buildings.BUILDING_GRANARY).Index
local water = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL).Index
local wind = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL).Index
local service = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_STAGE_2_SERVICE).Index
local feudalism = assert(GameInfo.Civics.CIVIC_FEUDALISM).Index

local base = {}
for row in GameInfo.TypeTags() do
    if row.Tag == 'CLASS_CSC_BAKERS_BASE' then
        base[row.Type] = {}
    end
end
for row in GameInfo.Improvement_ValidResources() do
    if base[row.ResourceType] then
        base[row.ResourceType][GameInfo.Improvements[row.ImprovementType].Index] = true
    end
end

local granaryFood = 0
for row in GameInfo.Building_YieldChanges() do
    if row.BuildingType == 'BUILDING_GRANARY' and row.YieldType == 'YIELD_FOOD' then
        granaryFood = granaryFood + row.YieldChange
    end
end

local function working(buildings, kind)
    return buildings:HasBuilding(kind) and not buildings:IsPillaged(kind)
end

if mode == 'ui' then
    -- PlotInfo has building yields but lacks the gameplay building-location API.
    -- The gameplay snapshot supplies the exact IDs to query here.
    local count = 0
    for _, key in ipairs(assert(CSC_BAKERS_COHORT_KEYS)) do
        local player, cityID, mill = key:match('^(%d+)/(%d+)/%d+/(%d+)/')
        local city = assert(Players[tonumber(player)]:GetCities():FindID(tonumber(cityID)))
        local food = assert(city:GetBuildingYield(granary, 'YIELD_FOOD'))
        local millFood = assert(city:GetBuildingYield(tonumber(mill), 'YIELD_FOOD'))
        if food >= granaryFood + 1 and millFood >= 1 then
            print(string.format('CSC_COHORT_YIELD %s %.4g %.4g', key, food, millFood))
            count = count + 1
        end
    end
    print(string.format('CSC_COHORT_UI %d %d', Game.GetCurrentGameTurn(), count))
    return
end

local function scanCity(playerID, city, rows)
    if (city:GetProperty('CSC_BAKERS_STAGE_2_EFFECT_GROWTH') or 0) <= 0 then return end
    local buildings = city:GetBuildings()
    if not working(buildings, granary) or not buildings:HasBuilding(service) then return end
    local mill = working(buildings, water) and water or (working(buildings, wind) and wind or nil)
    if not mill then return end
    local millPlot = buildings:GetBuildingLocation(mill)
    local granaryPlot = buildings:GetBuildingLocation(granary)
    local districts = city:GetDistricts()
    local district = nil
    for index = 0, districts:GetNumDistricts() - 1 do
        local candidate = districts:GetDistrictByIndex(index)
        if candidate and candidate:GetType() == quarter then
            district = candidate
            break
        end
    end
    if not district or not district:IsComplete() or district:IsPillaged() then return end
    if millPlot ~= Map.GetPlotIndex(district:GetX(), district:GetY()) then return end
    local neighbors = Map.GetAdjacentPlots(district:GetX(), district:GetY())
    local customer = false
    for _, plot in ipairs(neighbors) do
        if plot:GetIndex() == granaryPlot and plot:GetOwner() == playerID then customer = true end
    end
    if not customer then return end

    for _, plot in ipairs(neighbors) do
        local resource = GameInfo.Resources[plot:GetResourceType()]
        local improvements = resource and base[resource.ResourceType]
        local improvement = plot:GetImprovementType()
        if improvements and improvements[improvement] and plot:GetOwner() == playerID
            and plot:GetDistrictType() == -1 and not plot:IsImprovementPillaged() then
            local key = table.concat({playerID, city:GetID(), millPlot, mill, granaryPlot,
                plot:GetIndex(), resource.Index, improvement}, '/')
            rows[#rows + 1] = key
        end
    end
end

local function collect()
    local rows = {}
    for _, player in ipairs(PlayerManager.GetAliveMajors()) do
        local playerID = player:GetID()
        -- Player 0 is the controller's return slot. Qualify only a separate AI.
        if playerID ~= 0 and player:GetCulture():HasCivic(feudalism) then
            for _, city in player:GetCities():Members() do
                scanCity(playerID, city, rows)
            end
        end
    end
    table.sort(rows)
    return rows
end

assert(mode == 'gameplay' and CSC_BAKERS_COHORT == nil)
local phases = {}
local fault = nil
CSC_BAKERS_COHORT = {}

function CSC_BAKERS_COHORT.snapshot()
    local rows = collect()
    for _, row in ipairs(rows) do print('CSC_COHORT_KEY ' .. row) end
    print(string.format('CSC_COHORT_CORE %d %d', Game.GetCurrentGameTurn(), #rows))
end

local function capture(player)
    if fault then return end
    local ok, rows = pcall(collect)
    if not ok then
        fault = tostring(rows)
        return
    end
    phases[#phases + 1] = string.format('CSC_COHORT_PHASE %d %d %s',
        Game.GetCurrentGameTurn(), player, #rows > 0 and table.concat(rows, ',') or '-')
end

function CSC_BAKERS_COHORT.export()
    for _, phase in ipairs(phases) do print(phase) end
    if fault then print('CSC_COHORT_FAULT ' .. fault) end
    print('CSC_COHORT_COUNT ' .. tostring(#phases))
    phases = {}
end

Events.PlayerTurnDeactivated.Add(capture)
print('CSC_COHORT_INSTALLED')
