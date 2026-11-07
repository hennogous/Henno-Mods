-- Find working Bakers chains by their exact physical participants.
-- Gameplay records each player phase. The UI independently checks realized yields.
local mode = assert(CSC_BAKERS_COHORT_MODE)
local quarter = assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER).Index
local cityCenter = assert(GameInfo.Districts.DISTRICT_CITY_CENTER).Index
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

local granaryTypes = {BUILDING_GRANARY = granary}
local granaries = {granary}
for row in GameInfo.BuildingReplaces() do
    local building = GameInfo.Buildings[row.CivUniqueBuildingType]
    if row.ReplacesBuildingType == 'BUILDING_GRANARY' and building and building.PrereqDistrict == 'DISTRICT_CITY_CENTER' then
        granaryTypes[row.CivUniqueBuildingType] = building.Index
        granaries[#granaries + 1] = building.Index
    end
end
table.sort(granaries)
local granaryFood = {}
for row in GameInfo.Building_YieldChanges() do
    local index = granaryTypes[row.BuildingType]
    if index and row.YieldType == 'YIELD_FOOD' then
        granaryFood[index] = (granaryFood[index] or 0) + row.YieldChange
    end
end

local function working(buildings, kind)
    return buildings:HasBuilding(kind) and not buildings:IsPillaged(kind)
end

local function census(players, prefix)
    -- Include unfinished and broken Quarters. The retention collector below
    -- deliberately skips them, which hides the links a development run needs.
    local count = 0
    local function emit(kind, ...)
        local fields = {...}
        for i, value in ipairs(fields) do fields[i] = tostring(value) end
        print(prefix .. kind .. '\t' .. table.concat(fields, '\t'))
        count = count + 1
    end
    local function unlocked(player, row)
        local tech = GameInfo.Technologies[row.PrereqTech]
        local civic = GameInfo.Civics[row.PrereqCivic]
        return (not tech or player:GetTechs():HasTech(tech.Index))
            and (not civic or player:GetCulture():HasCivic(civic.Index))
    end
    local function buildingState(buildings, kind)
        if not buildings:HasBuilding(kind) then return 'absent', -1 end
        return working(buildings, kind) and 'working' or 'pillaged', buildings:GetBuildingLocation(kind)
    end
    for _, playerID in ipairs(players) do
        local player = assert(Players[playerID])
        local alive = player:IsAlive()
        emit('PLAYER', playerID, alive, alive and player:GetCulture():HasCivic(feudalism))
        if alive then
            for _, city in player:GetCities():Members() do
                local districts = city:GetDistricts()
                for index = 0, districts:GetNumDistricts() - 1 do
                    local district = districts:GetDistrictByIndex(index)
                    if district and district:GetType() == quarter then
                        local x, y = district:GetX(), district:GetY()
                        local quarterPlot = Map.GetPlotIndex(x, y)
                        emit('QUARTER', playerID, city:GetID(), quarterPlot, district:IsComplete(),
                            district:IsPillaged(), Map.GetPlotByIndex(quarterPlot):IsRiver())
                        for _, kind in ipairs({water, wind}) do
                            local row = GameInfo.Buildings[kind]
                            local status, location = buildingState(city:GetBuildings(), kind)
                            emit('MILL', quarterPlot, row.BuildingType, status, location, unlocked(player, row))
                        end
                        for _, plot in ipairs(Map.GetAdjacentPlots(x, y)) do
                            local resource = GameInfo.Resources[plot:GetResourceType()]
                            local improvement = GameInfo.Improvements[plot:GetImprovementType()]
                            local mapped = resource and base[resource.ResourceType]
                            emit('NEIGHBOR', quarterPlot, plot:GetIndex(), plot:GetOwner(), plot:GetDistrictType(),
                                resource and resource.ResourceType or '-', improvement and improvement.ImprovementType or '-',
                                mapped ~= nil, mapped and improvement and mapped[improvement.Index] == true or false,
                                plot:IsImprovementPillaged())
                            for kind in pairs(mapped or {}) do
                                local row = GameInfo.Improvements[kind]
                                emit('IMPROVEMENT', quarterPlot, plot:GetIndex(), row.ImprovementType, unlocked(player, row))
                            end
                            if plot:GetOwner() == playerID and plot:GetDistrictType() == cityCenter then
                                local buyer = Cities.GetPlotPurchaseCity(plot)
                                if buyer and buyer:GetOwner() == playerID
                                    and buyer:GetX() == plot:GetX() and buyer:GetY() == plot:GetY() then
                                    for _, kind in ipairs(granaries) do
                                        local status, location = buildingState(buyer:GetBuildings(), kind)
                                        if kind == granary or status ~= 'absent' then
                                            emit('CUSTOMER', quarterPlot, buyer:GetID(), plot:GetIndex(),
                                                GameInfo.Buildings[kind].BuildingType, status, location)
                                        end
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
    end
    print(string.format('%sEND\t%d\t%d', prefix, Game.GetCurrentGameTurn(), count))
end

if mode == 'census' then
    census(assert(CSC_BAKERS_CENSUS_PLAYERS), 'CSC_BAKERS_CENSUS_')
    return
end

if mode == 'census-watch' then
    -- Sample selected gameplay boundaries while autoplay continues. Keep
    -- this framing separate from the controller's inactive endpoint census.
    assert(not CSC_BAKERS_CENSUS_WATCH_INSTALLED, 'Bakers census watcher already installed')
    local players = assert(CSC_BAKERS_CENSUS_PLAYERS)
    local pending = {}
    for _, turn in ipairs(assert(CSC_BAKERS_CENSUS_TURNS)) do pending[turn] = true end
    GameEvents.OnGameTurnStarted.Add(function()
        local turn = Game.GetCurrentGameTurn()
        if not pending[turn] then return end
        pending[turn] = nil
        print(string.format('CSC_BAKERS_WATCH_CENSUS_BEGIN\t%d', turn))
        local ok, message = pcall(census, players, 'CSC_BAKERS_WATCH_CENSUS_')
        if not ok then
            print(string.format('CSC_BAKERS_WATCH_CENSUS_FAULT\t%d\t%s', turn, tostring(message)))
        end
    end)
    CSC_BAKERS_CENSUS_WATCH_INSTALLED = true
    print('CSC_BAKERS_CENSUS_WATCH_INSTALLED')
    return
end

if mode == 'ui' then
    -- PlotInfo has building yields but lacks the gameplay building-location API.
    -- The gameplay snapshot supplies the exact IDs to query here.
    local count = 0
    for _, key in ipairs(assert(CSC_BAKERS_COHORT_KEYS)) do
        local player, cityID, mill = key:match('^(%d+)/(%d+)/%d+/(%d+)/')
        local buyerID, granaryID = key:match('^%d+/%d+/%d+/%d+/%d+/%d+/%d+/%d+/(%d+)/(%d+)$')
        -- Archived eight-field receipts kept the Granary in the producer city.
        buyerID, granaryID = buyerID or cityID, tonumber(granaryID) or granary
        local cities = Players[tonumber(player)]:GetCities()
        local city = assert(cities:FindID(tonumber(cityID)))
        local buyer = assert(cities:FindID(tonumber(buyerID)))
        local food = assert(buyer:GetBuildingYield(granaryID, 'YIELD_FOOD'))
        local millFood = assert(city:GetBuildingYield(tonumber(mill), 'YIELD_FOOD'))
        if food >= (granaryFood[granaryID] or 0) + 1 and millFood >= 1 then
            print(string.format('CSC_COHORT_YIELD %s %.4g %.4g', key, food, millFood))
            count = count + 1
        end
    end
    print(string.format('CSC_COHORT_UI %d %d', Game.GetCurrentGameTurn(), count))
    return
end

local function buyers(playerID, neighbors)
    local result = {}
    for _, plot in ipairs(neighbors) do
        if plot:GetOwner() == playerID and plot:GetDistrictType() == cityCenter then
            local city = Cities.GetPlotPurchaseCity(plot)
            if city and city:GetOwner() == playerID and city:GetX() == plot:GetX() and city:GetY() == plot:GetY() then
                local buildings = city:GetBuildings()
                if buildings:HasBuilding(service) then
                    for _, kind in ipairs(granaries) do
                        if working(buildings, kind) and buildings:GetBuildingLocation(kind) == plot:GetIndex() then
                            result[#result + 1] = {city = city:GetID(), building = kind, plot = plot:GetIndex()}
                        end
                    end
                end
            end
        end
    end
    return result
end

local function scanCity(playerID, city, rows)
    if (city:GetProperty('CSC_BAKERS_STAGE_2_EFFECT_GROWTH') or 0) <= 0 then return end
    local buildings = city:GetBuildings()
    local mill = working(buildings, water) and water or (working(buildings, wind) and wind or nil)
    if not mill then return end
    local millPlot = buildings:GetBuildingLocation(mill)
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
    local customers = buyers(playerID, neighbors)
    if #customers == 0 then return end

    for _, plot in ipairs(neighbors) do
        local resource = GameInfo.Resources[plot:GetResourceType()]
        local improvements = resource and base[resource.ResourceType]
        local improvement = plot:GetImprovementType()
        if improvements and improvements[improvement] and plot:GetOwner() == playerID
            and plot:GetDistrictType() == -1 and not plot:IsImprovementPillaged() then
            for _, customer in ipairs(customers) do
                rows[#rows + 1] = table.concat({playerID, city:GetID(), millPlot, mill, customer.plot,
                    plot:GetIndex(), resource.Index, improvement, customer.city, customer.building}, '/')
            end
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
