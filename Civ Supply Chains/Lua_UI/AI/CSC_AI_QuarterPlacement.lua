-- Site corrections for a completed native district forecast. A caller supplies
-- measured Q8 inputs from the same city calculation and publishes the result
-- through its native bridge. This module only evaluates the placement policy.
CSC_AI_QuarterPlacement = {}

local BAKERS = 'DISTRICT_CSC_BAKERS_QUARTER'
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
