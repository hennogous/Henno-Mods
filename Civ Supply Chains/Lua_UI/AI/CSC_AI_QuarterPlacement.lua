-- Read live Bakers supply for district protection and evaluate corrections
-- for a completed native district forecast when measured Q8 inputs are available.
CSC_AI_QuarterPlacement = {}

local BAKERS = 'DISTRICT_CSC_BAKERS_QUARTER'
local BASE = 'CLASS_CSC_BAKERS_BASE'
local SPECIALTY = 'CLASS_CSC_BAKERS_SPEC'
local STOREKEEPER_GROWTH = 'CSC_BAKERS_STAGE_2_EFFECT_GROWTH'

-- Initial finite Q8 penalties for the early CE score input. Boston's measured
-- late deduction was 8,784 Q8. This band needs live calibration at the early
-- boundary, since later forecast contributions can change the final ranking.
local MATERIAL_COST_Q8 = 2048
local LAST_DEPOSIT_COST_Q8 = 12288
local LAST_SUPPLIER_COST_Q8 = 16384
local ACTIVE_SERVICE_COST_Q8 = 24576

local improvementsByResource

local function materialOptions()
    if improvementsByResource then return improvementsByResource end
    local options = {}
    for row in GameInfo.Improvement_ValidResources() do
        if CSC_Adjacency.HasTag(BASE, row.ResourceType) or CSC_Adjacency.HasTag(SPECIALTY, row.ResourceType) then
            local resource = GameInfo.Resources[row.ResourceType]
            local improvement = GameInfo.Improvements[row.ImprovementType]
            if resource and improvement then
                options[resource.Index] = options[resource.Index] or {}
                options[resource.Index][#options[resource.Index] + 1] = improvement.Index
            end
        end
    end
    improvementsByResource = options
    return options
end

-- A working improvement and a deposit that could supply the chain later are
-- distinct facts. A compatible pillaged improvement remains a repair option.
-- Scope supply to the player because adjacent tiles can belong to other cities.
function CSC_AI_QuarterPlacement.ReadBakersSuppliers(player, quarter)
    local options = materialOptions()
    local playerID = player:GetID()
    local supplies = {base = {}, specialty = {}}
    for _, plot in ipairs(Map.GetAdjacentPlots(quarter:GetX(), quarter:GetY())) do
        local resourceID = plot:GetResourceType()
        if options[resourceID] and plot:GetOwner() == playerID and plot:GetDistrictType() == -1
            and PlayersVisibility[playerID]:IsRevealed(plot:GetX(), plot:GetY())
            and CSC_Adjacency.ResourceVisible(playerID, resourceID) then
            local current = plot:GetImprovementType()
            local viable, working = false, false
            for _, improvement in ipairs(options[resourceID]) do
                if improvement == current then
                    viable = true
                    working = not plot:IsImprovementPillaged()
                    break
                end
                if ImprovementBuilder.CanHaveImprovement(plot, improvement, player:GetTeam()) then
                    viable = true
                end
            end
            if viable then
                local resource = GameInfo.Resources[resourceID].ResourceType
                local material = {plot = plot:GetIndex(), resource = resource, working = working}
                if CSC_Adjacency.HasTag(BASE, resource) then supplies.base[#supplies.base + 1] = material end
                if CSC_Adjacency.HasTag(SPECIALTY, resource) then supplies.specialty[#supplies.specialty + 1] = material end
            end
        end
    end
    return supplies
end

local function priceSupply(risks, supply, activeService)
    local working = 0
    for _, material in ipairs(supply) do
        if material.working then working = working + 1 end
    end
    for _, material in ipairs(supply) do
        local cost = #supply == 1 and LAST_DEPOSIT_COST_Q8 or MATERIAL_COST_Q8
        if material.working and working == 1 then
            cost = activeService and ACTIVE_SERVICE_COST_Q8 or LAST_SUPPLIER_COST_Q8
        end
        -- One district can cover only one plot. Use the strongest relationship
        -- at that plot until the marginal values of shared chains are measured.
        risks[material.plot] = math.max(risks[material.plot] or 0, cost)
    end
end

function CSC_AI_QuarterPlacement.BakersMaterialRisk(player)
    local risks = {}
    local quarterType = GameInfo.Districts[BAKERS]
    if not quarterType then return risks end
    for _, city in player:GetCities():Members() do
        local districts = city:GetDistricts()
        for index = 0, districts:GetNumDistricts() - 1 do
            local quarter = districts:GetDistrictByIndex(index)
            if quarter and quarter:GetType() == quarterType.Index then
                local plot = Map.GetPlot(quarter:GetX(), quarter:GetY())
                local supply = CSC_AI_QuarterPlacement.ReadBakersSuppliers(player, plot)
                local activeService = quarter:IsComplete() and not quarter:IsPillaged()
                    and (city:GetProperty(STOREKEEPER_GROWTH) or 0) > 0
                priceSupply(risks, supply.base, activeService)
                priceSupply(risks, supply.specialty, false)
            end
        end
    end
    return risks
end

-- A supplier can be in a different city from the Quarter. Key the deduction
-- to the city that could actually place a district there, as CE expects.
function CSC_AI_QuarterPlacement.BakersMaterialDeductions(player)
    local playerID = player:GetID()
    local entries = {}
    for index, cost in pairs(CSC_AI_QuarterPlacement.BakersMaterialRisk(player)) do
        local plot = Map.GetPlotByIndex(index)
        local city = Cities.GetPlotPurchaseCity(plot)
        if city and city:GetOwner() == playerID then
            local cityID = city:GetID()
            for district in GameInfo.Districts() do
                if district.Index > 0 and plot:CanHaveDistrict(district.Index, playerID, cityID) then
                    entries[#entries + 1] = {
                        player = playerID, city = cityID, district = district.Index, plot = index, delta = -cost,
                    }
                end
            end
        end
    end
    return entries
end

local WATER_RECIPIENT = {
    'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',
    'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
}
local INLAND_CORRECTIONS = {
    { building = 'BUILDING_CSC_BAKERS_WIND_MILL', roots = {
        'ATTACH_MOD_CSC_ADJ_CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS_STEP_1',
    } },
    { building = 'BUILDING_CSC_BAKERS_BAKERY', roots = WATER_RECIPIENT },
    { building = 'BUILDING_CSC_BAKERS_CAFE', roots = WATER_RECIPIENT },
}

local function isPositiveQ8(value)
    return type(value) == 'number' and value > 0 and value <= 2147483647 and value == math.floor(value)
end

-- The observed Bakers aggregate admits Wind, Bakery and Café. On a flat inland
-- site Wind has no hills benefit, and Water cannot receive Bakery/Café yields.
-- `buildings` contains the admitted native raw value and the consumed root
-- credits for each building, before any prerequisite-chain propagation.
function CSC_AI_QuarterPlacement.BakersAdjustment(site, forecast)
    if site.districtType ~= BAKERS or site.legal ~= true or site.hills ~= false or site.riverEdges ~= 0 then
        return nil
    end
    if not isPositiveQ8(forecast.beforeQ8) or not isPositiveQ8(forecast.nativeQ8)
        or type(forecast.buildings) ~= 'table' then return nil end

    local originalUplift, correctedUplift = 0, 0
    for _, correction in ipairs(INLAND_CORRECTIONS) do
        local building = forecast.buildings[correction.building]
        if not building or not isPositiveQ8(building.rawQ8)
            or type(building.rootCreditsQ8) ~= 'table' then return nil end
        local removed = 0
        for _, root in ipairs(correction.roots) do
            local credit = building.rootCreditsQ8[root]
            if not isPositiveQ8(credit) then return nil end
            removed = removed + credit
        end
        originalUplift = originalUplift + building.rawQ8
        -- Civ only adds positive raw building forecasts to a district. Keep
        -- that gate when the removal exceeds the building's whole raw score.
        correctedUplift = correctedUplift + math.max(0, building.rawQ8 - removed)
    end
    if forecast.beforeQ8 + originalUplift ~= forecast.nativeQ8 then return nil end
    return correctedUplift - originalUplift
end
