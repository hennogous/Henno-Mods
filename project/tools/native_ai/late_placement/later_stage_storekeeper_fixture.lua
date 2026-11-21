-- Controlled research replay. The turn-50 world already has a working
-- Bakers, two improved Base resources and an adjacent Granary. Add only
-- the missing Mill on both copies and let the AI research normally.
local pid, cityId, site, customerPlot = 3, 65536, 2497, 2496
local player = assert(Players[pid])
local city = assert(CityManager.GetCity(pid, cityId))
local plot = assert(Map.GetPlotByIndex(site))
local granary = assert(GameInfo.Buildings.BUILDING_GRANARY)
local feudalism = assert(GameInfo.Civics.CIVIC_FEUDALISM)
local guilds = assert(GameInfo.Civics.CIVIC_GUILDS)
local bakers = assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER)
local mill = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL)
local wind = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL)

local function working(building, location)
    local buildings = city:GetBuildings()
    return buildings:HasBuilding(building.Index) and not buildings:IsPillaged(building.Index)
        and buildings:GetBuildingLocation(building.Index) == location
end

if mode == 'setup' then
    assert(Game.GetCurrentGameTurn() == 50 and not player:IsHuman())
    local district = assert(city:GetDistricts():GetDistrict(bakers.Index))
    assert(district:IsComplete() and not district:IsPillaged()
        and district:GetX() == plot:GetX() and district:GetY() == plot:GetY() and plot:IsRiver())
    local culture = player:GetCulture()
    local feudalismOwned, guildsOwned = culture:HasCivic(feudalism.Index), culture:HasCivic(guilds.Index)
    assert(working(granary, customerPlot) and (not feudalismOwned or not guildsOwned),
        'The replay needs a working Granary and at least one unowned research goal')
    local placement = assert(CSC_AI_QuarterPlacement)
    local profile
    for _, definition in ipairs(placement.StageTwoProfiles()) do
        if definition.key == 'BAKERS' then profile = definition; break end
    end
    local count = 0
    for _, rule in ipairs(placement.ReadSuppliers(player, plot, assert(profile)).base) do
        if rule.working then count = count + 1 end
    end
    assert(count >= 1 and city:GetPopulation() >= 7, 'Source does not have ready supply and Stage 3 population')
    local buildings = city:GetBuildings()
    assert(not buildings:HasBuilding(mill.Index) and not buildings:HasBuilding(wind.Index))
    city:GetBuildQueue():CreateBuilding(mill.Index, site)
    assert(working(mill, site), 'Matched Mill setup failed')
    print('CSC_MILESTONE_STOREKEEPER_SETUP', pid, cityId, site, count, feudalism.Index, guilds.Index,
        tostring(feudalismOwned), tostring(guildsOwned))
else
    assert(mode == 'outcome')
    print('CSC_MILESTONE_STOREKEEPER_OUTCOME', Game.GetCurrentGameTurn(), pid, cityId,
        tostring(player:GetCulture():HasCivic(feudalism.Index)), tostring(working(mill, site)),
        tostring(working(granary, customerPlot)), city:GetProperty('CSC_BAKERS_STAGE_2_EFFECT_GROWTH') or 0)
end
