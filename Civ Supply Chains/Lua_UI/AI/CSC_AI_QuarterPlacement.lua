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
-- Alexandria's ready chain needed 56 utility units across repeat allocations.
-- The cap from CE preserves the original lower amount on older local builds.
local READY_SUPPLIER_BID_Q8 = 56 * 256
-- Initial calibration from the matched Melbourne nomination. Only publish
-- this preference when the Mill alone can complete a working Stage 2 chain.
local READY_MILL_BID_Q8 = 448 * 256
-- Trebizond's measured stream gives about 18–19 points for Food and
-- 17.5 each for Production and Gold. Round each term down. The bid
-- covers the immediate exchange with a working Mill.
local WORKING_MILL_GRANARY_BID_Q8 = (18 + 17 + 17) * 256
local WIND_MILL = 'BUILDING_CSC_BAKERS_WIND_MILL'
local WATER_MILL = 'BUILDING_CSC_BAKERS_WATER_MILL'

local improvementsByResource
local granaryTypes

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

local function workingBuildingAt(buildings, kind, plot)
    return kind and buildings:HasBuilding(kind.Index) and not buildings:IsPillaged(kind.Index)
        and buildings:GetBuildingLocation(kind.Index) == plot
end

local function visitBakersCustomers(player, quarter, visit)
    if not granaryTypes then
        granaryTypes = { GameInfo.Buildings.BUILDING_GRANARY }
        for row in GameInfo.BuildingReplaces() do
            local kind = GameInfo.Buildings[row.CivUniqueBuildingType]
            if row.ReplacesBuildingType == 'BUILDING_GRANARY' and kind
                and kind.PrereqDistrict == 'DISTRICT_CITY_CENTER' then
                granaryTypes[#granaryTypes + 1] = kind
            end
        end
    end
    local cityCenter = GameInfo.Districts.DISTRICT_CITY_CENTER.Index
    for _, plot in ipairs(Map.GetAdjacentPlots(quarter:GetX(), quarter:GetY())) do
        if plot:GetOwner() == player and plot:GetDistrictType() == cityCenter then
            local buyer = Cities.GetPlotPurchaseCity(plot)
            if buyer and buyer:GetOwner() == player and visit(buyer, plot:GetIndex()) then return true end
        end
    end
    return false
end

local function hasBakersCustomer(player, quarter)
    return visitBakersCustomers(player, quarter, function(buyer, plot)
        local buildings = buyer:GetBuildings()
        for _, kind in ipairs(granaryTypes) do
            if workingBuildingAt(buildings, kind, plot) then return true end
        end
    end)
end

local function workingBakersMill(city, plot)
    local buildings = city:GetBuildings()
    return workingBuildingAt(buildings, GameInfo.Buildings[WATER_MILL], plot)
        or workingBuildingAt(buildings, GameInfo.Buildings[WIND_MILL], plot)
end

local function nominateBakersGranaries(entries, visitedCustomers, player, quarter, bid, canProduceBuilding)
    visitBakersCustomers(player, quarter, function(buyer)
        local city = buyer:GetID()
        -- Several Mills can share a City Center, but the city makes one
        -- Granary investment. Credit the calibrated single exchange once.
        if visitedCustomers[city] then return end
        visitedCustomers[city] = true
        local buildings = buyer:GetBuildings()
        for _, kind in ipairs(granaryTypes) do
            -- A pillaged Granary calls for repair and remains the existing customer.
            if buildings:HasBuilding(kind.Index) then return end
        end
        for _, kind in ipairs(granaryTypes) do
            if canProduceBuilding(player, city, kind.Hash) then
                entries[#entries + 1] = { player = player, city = city, building = kind.Index, delta = bid }
            end
        end
    end)
end

local function nominateBakersMills(entries, player, city, quarter, base, bid)
    local supplied = false
    for _, material in ipairs(base) do
        if material.working then
            supplied = true
            break
        end
    end
    if not supplied then return end
    local buildings = city:GetBuildings()
    local wind = GameInfo.Buildings[WIND_MILL]
    local water = GameInfo.Buildings[WATER_MILL]
    -- Existing producers belong to the repair policy, including pillaged ones.
    if (wind and buildings:HasBuilding(wind.Index)) or (water and buildings:HasBuilding(water.Index)) then return end
    local playerID = player:GetID()
    if not hasBakersCustomer(playerID, quarter) then return end
    local function add(kind)
        if not kind then return end
        local tech = kind.PrereqTech and GameInfo.Technologies[kind.PrereqTech]
        if kind.PrereqTech and (not tech or not player:GetTechs():HasTech(tech.Index)) then return end
        entries[#entries + 1] = { player = playerID, city = city:GetID(), building = kind.Index, delta = bid }
    end
    -- Both variants can be legal on rivers. Let Civ compare their native
    -- values and enforce the river flag, mutual exclusion and queue checks.
    add(wind)
    if quarter:IsRiver() then add(water) end
end

function CSC_AI_QuarterPlacement.BakersMaterialRisk(player, builderBidLimit, nominationLimit, canProduceBuilding)
    local risks, recover, nominations = {}, {}, {}
    local visitedCustomers = {}
    local quarterType = GameInfo.Districts[BAKERS]
    if not quarterType then return risks, recover, nominations end
    local recoveryBid = math.min(builderBidLimit or 0, READY_SUPPLIER_BID_Q8)
    local millBid = math.min(nominationLimit or 0, READY_MILL_BID_Q8)
    local customerBid = type(canProduceBuilding) == 'function'
        and math.min(nominationLimit or 0, WORKING_MILL_GRANARY_BID_Q8) or 0
    local feudalism = (recoveryBid > 0 or millBid > 0) and GameInfo.Civics.CIVIC_FEUDALISM
    local serviceUnlocked = feudalism and player:GetCulture():HasCivic(feudalism.Index)
    for _, city in player:GetCities():Members() do
        local districts = city:GetDistricts()
        for index = 0, districts:GetNumDistricts() - 1 do
            local quarter = districts:GetDistrictByIndex(index)
            if quarter and quarter:GetType() == quarterType.Index then
                local plot = Map.GetPlot(quarter:GetX(), quarter:GetY())
                local supply = CSC_AI_QuarterPlacement.ReadBakersSuppliers(player, plot)
                local ready = quarter:IsComplete() and not quarter:IsPillaged()
                local activeService = ready and (city:GetProperty(STOREKEEPER_GROWTH) or 0) > 0
                priceSupply(risks, supply.base, activeService)
                priceSupply(risks, supply.specialty, false)
                local missingSupply = recoveryBid > 0 and #supply.base == 1 and not supply.base[1].working
                local millWorks = ready and (customerBid > 0 or (serviceUnlocked and not activeService and missingSupply))
                    and workingBakersMill(city, plot:GetIndex())
                -- The exchange can operate before the Farm or Feudalism.
                if millWorks and customerBid > 0 then
                    nominateBakersGranaries(nominations, visitedCustomers, player:GetID(), plot, customerBid,
                        canProduceBuilding)
                end
                if serviceUnlocked and ready and not activeService then
                    local base = supply.base
                    if missingSupply then
                        if millWorks and hasBakersCustomer(player:GetID(), plot) then
                            recover[base[1].plot] = recoveryBid
                        end
                    elseif millBid > 0 then
                        nominateBakersMills(nominations, player, city, plot, base, millBid)
                    end
                end
            end
        end
    end
    return risks, recover, nominations
end

-- A supplier can be in a different city from the Quarter. Key the deduction
-- to the city that could actually place a district there, as CE expects.
function CSC_AI_QuarterPlacement.BakersMaterialDeductions(player, includeBuilders, builderBidLimit, nominationLimit,
    canProduceBuilding)
    local playerID = player:GetID()
    local entries, builderSites = {}, {}
    local risks, recover, nominations = CSC_AI_QuarterPlacement.BakersMaterialRisk(player, builderBidLimit,
        nominationLimit, canProduceBuilding)
    for index, cost in pairs(risks) do
        local plot = Map.GetPlotByIndex(index)
        local city = Cities.GetPlotPurchaseCity(plot)
        if city and city:GetOwner() == playerID then
            local cityID = city:GetID()
            if includeBuilders and cost >= LAST_DEPOSIT_COST_Q8 then
                local current = plot:GetImprovementType()
                local options = materialOptions()[plot:GetResourceType()]
                -- Keep a working supplier in place. For a deposit that is not
                -- working yet, keep all mapped improvements available to Civ.
                local working = not plot:IsImprovementPillaged()
                for _, improvement in ipairs(options) do
                    if improvement == current and working then
                        options = {current}
                        break
                    end
                end
                builderSites[#builderSites + 1] = {
                    player = playerID, city = cityID, plot = index, improvements = options, deltaQ8 = recover[index],
                }
            end
            for district in GameInfo.Districts() do
                if district.Index > 0 and plot:CanHaveDistrict(district.Index, playerID, cityID) then
                    entries[#entries + 1] = {
                        player = playerID, city = cityID, district = district.Index, plot = index, delta = -cost,
                    }
                end
            end
        end
    end
    return entries, builderSites, nominations
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
