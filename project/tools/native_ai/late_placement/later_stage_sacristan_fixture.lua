-- Isolate Divine Right in the turn-100 world with an operating Base
-- supplier and Temple beside Tailors. Reset Divine Right before creating
-- the missing Tailor on both disposable copies. This isolates one civic on
-- an already developed map. Native AI owns the new selection and completion.
local pid, cityId, quarterPlot, templePlot = 5, 131073, 2038, 1965
local player = assert(Players[pid])
local city = assert(CityManager.GetCity(pid, cityId))
local quarter, venue = assert(Map.GetPlotByIndex(quarterPlot)), assert(Map.GetPlotByIndex(templePlot))
local customer = assert(Cities.GetPlotPurchaseCity(venue))
local civic = assert(GameInfo.Civics.CIVIC_DIVINE_RIGHT)
local culture = player:GetCulture()
local owned = culture:HasCivic(civic.Index)
local temple = assert(GameInfo.Buildings.BUILDING_TEMPLE)
local tailor = assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_TAILOR)
local workshop = assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP)
if mode == 'before' or mode == 'progress' then
    -- Progress is exposed by the UI reader. Gameplay owns the civic mutation
    -- below and has no progress getter in this binary.
    local progress = culture:GetCulturalProgress(civic.Index)
    if mode == 'progress' then assert(progress == 0, 'Civic progress reset was not observed') end
    local marker = mode == 'before' and 'BEFORE' or 'PROGRESS'
    print('CSC_MILESTONE_SACRISTAN_' .. marker, Game.GetCurrentGameTurn(), pid, civic.Index, tostring(owned), progress)
    return
end
local function active(owner, definition, location)
    local buildings = owner:GetBuildings()
    return buildings:HasBuilding(definition.Index) and not buildings:IsPillaged(definition.Index)
        and buildings:GetBuildingLocation(definition.Index) == location
end
local function customerWorks()
    if active(customer, temple, templePlot) then return true end
    for row in GameInfo.BuildingReplaces() do
        if row.ReplacesBuildingType == temple.BuildingType
            and active(customer, assert(GameInfo.Buildings[row.CivUniqueBuildingType]), templePlot) then return true end
    end
    return false
end
if mode == 'setup' then
    assert(Game.GetCurrentGameTurn() == 100 and not player:IsHuman())
    assert(customer:GetOwner() == pid and customerWorks()
        and Map.GetPlotDistance(quarter:GetX(), quarter:GetY(), venue:GetX(), venue:GetY()) == 1)
    local profile
    for _, candidate in ipairs(CSC_AI_QuarterPlacement.StageTwoProfiles()) do
        if candidate.key == 'TAILORS' then profile = candidate; break end
    end
    local supplied = false
    for _, item in ipairs(CSC_AI_QuarterPlacement.ReadSuppliers(player, quarter, assert(profile)).base) do
        supplied = supplied or item.working
    end
    assert(supplied, 'No working Base supplier in the archived Tailors chain')
    -- Clearing ownership does not broadcast the completion event. Require
    -- this exact world to have no Tailor before resetting the civic, so the
    -- Service attachment is created against the reset facts on both copies.
    assert(not city:GetBuildings():HasBuilding(tailor.Index), 'The fixture needs the archived missing Tailor')
    assert(type(culture.SetCivic) == 'function' and type(culture.SetCulturalProgress) == 'function',
        'Gameplay civic setters are unavailable')
    culture:SetCivic(civic.Index, false)
    culture:SetCulturalProgress(civic.Index, 0)
    assert(not culture:HasCivic(civic.Index), 'The controlled civic ownership reset was not observed')
    for _, building in ipairs({workshop, tailor}) do
        if not active(city, building, quarterPlot) then
            assert(not city:GetBuildings():HasBuilding(building.Index), 'Producer already exists but is damaged')
            city:GetBuildQueue():CreateBuilding(building.Index, quarterPlot)
        end
        assert(active(city, building, quarterPlot), 'Producer preparation failed')
    end
    print('CSC_MILESTONE_SACRISTAN_SETUP', pid, cityId, quarterPlot, templePlot, civic.Index, tostring(owned))
else
    assert(mode == 'outcome')
    print('CSC_MILESTONE_SACRISTAN_OUTCOME', Game.GetCurrentGameTurn(), pid, cityId, tostring(owned),
        tostring(active(city, tailor, quarterPlot)), tostring(customerWorks()),
        customer:GetProperty('CSC_TAILORS_STAGE_3_EFFECT_FAITH') or 0)
end
