-- Isolate Divine Right on the archived Qaraqorum Quarter. Both copies need
-- the same working Tailor and Temple. The UI scout uses stock plot legality,
-- and the fixture leaves Divine Right and all civic choices to the AI.
local pid, cityId, quarterPlot = 4, 65536, 2265
local player = assert(Players[pid])
local city = assert(CityManager.GetCity(pid, cityId))
local quarter = assert(Map.GetPlotByIndex(quarterPlot))
local holy = assert(GameInfo.Districts.DISTRICT_HOLY_SITE)
local civic = assert(GameInfo.Civics.CIVIC_DIVINE_RIGHT)
local owned = player:GetCulture():HasCivic(civic.Index)
if mode == 'scout' then
    assert(Game.GetCurrentGameTurn() == 100 and not owned and not player:IsHuman())
    assert(not city:GetDistricts():HasDistrict(holy.Index), 'City already has a Holy Site')
    local best
    for _, plot in ipairs(Map.GetAdjacentPlots(quarter:GetX(), quarter:GetY())) do
        local buyer = Cities.GetPlotPurchaseCity(plot)
        local index = plot:GetIndex()
        if plot:GetOwner() == pid and buyer and buyer:GetID() == cityId
            and plot:GetDistrictType() == -1 and plot:GetResourceType() == -1 and plot:GetImprovementType() == -1
            and plot:CanHaveDistrict(holy.Index, pid, cityId) and (not best or index < best) then
            best = index
        end
    end
    print('CSC_MILESTONE_SACRISTAN_SCOUT', assert(best, 'No eligible adjacent Holy Site footprint'))
    return
end

local function active(definition, location)
    local buildings = city:GetBuildings()
    return buildings:HasBuilding(definition.Index) and not buildings:IsPillaged(definition.Index)
        and buildings:GetBuildingLocation(definition.Index) == location
end
local template = assert(GameInfo.Buildings.BUILDING_TEMPLE)
local tailor = assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_TAILOR)
if mode == 'setup' then
    assert(Game.GetCurrentGameTurn() == 100 and not owned and not player:IsHuman())
    local target = assert(Map.GetPlotByIndex(assert(expectedBuyer)))
    assert(target:GetOwner() == pid and target:GetDistrictType() == -1
        and Map.GetPlotDistance(quarter:GetX(), quarter:GetY(), target:GetX(), target:GetY()) == 1)
    local queue = city:GetBuildQueue()
    queue:CreateIncompleteDistrict(holy.Index, target:GetIndex(), 100)
    local district = assert(city:GetDistricts():GetDistrict(holy.Index))
    assert(district:IsComplete() and not district:IsPillaged())
    for _, key in ipairs({'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP', 'BUILDING_CSC_TAILORS_TAILOR',
                         'BUILDING_SHRINE', 'BUILDING_TEMPLE'}) do
        local definition = assert(GameInfo.Buildings[key])
        local location = definition.PrereqDistrict == holy.DistrictType and target:GetIndex() or quarterPlot
        if not active(definition, location) then
            assert(not city:GetBuildings():HasBuilding(definition.Index), 'Existing fixture building is obstructed')
            queue:CreateBuilding(definition.Index, location)
        end
        assert(active(definition, location), 'Could not prepare the matched Service chain')
    end
    print('CSC_MILESTONE_SACRISTAN_SETUP', pid, cityId, quarterPlot, target:GetIndex(), civic.Index)
else
    assert(mode == 'outcome')
    local district = assert(city:GetDistricts():GetDistrict(holy.Index))
    local plot = assert(Map.GetPlot(district:GetX(), district:GetY()))
    print('CSC_MILESTONE_SACRISTAN_OUTCOME', Game.GetCurrentGameTurn(), pid, cityId, tostring(owned),
        tostring(active(tailor, quarterPlot)), tostring(active(template, plot:GetIndex())),
        city:GetProperty('CSC_TAILORS_STAGE_3_EFFECT_FAITH') or 0)
end
