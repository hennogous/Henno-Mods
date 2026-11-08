-- Read live Bakers supply for district protection and evaluate corrections
-- for a completed native district forecast when measured Q8 inputs are available.
CSC_AI_QuarterPlacement = {}

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
local READY_PRODUCER_BID_Q8 = 448 * 256
local EXCHANGE_PRODUCER_BID_Q8 = 18 * 256
local EARLY_SUPPLIER_BID_Q8 = 26 * 256
-- Trebizond's measured stream gives about 18–19 points for Food and
-- 17.5 each for Production and Gold. Round each term down. The bid
-- covers the immediate exchange with a working Mill.
local CUSTOMER_BID_Q8 = (18 + 17 + 17) * 256

local improvementsByResource
local profiles
local dockmasterShipHashes
local P = CSC_AI_QuarterPlacement

-- Match the naval families in the Dockmaster production modifiers. Use the
-- loaded unlock eras so unique and modded ships can qualify through the queue.
local dockmasterNavalClasses = {
    PROMOTION_CLASS_NAVAL_MELEE = true,
    PROMOTION_CLASS_NAVAL_RANGED = true,
    PROMOTION_CLASS_NAVAL_RAIDER = true,
}

-- The database supplies relationships and replacements. These profiles supply
-- each Service gate. The shared initial bands come from the Bakers replays.
-- A Quarter with incomplete metadata stays outside the production adapters.
local serviceRules = {
    BAKERS = { civic = 'CIVIC_FEUDALISM', property = STOREKEEPER_GROWTH },
    TAILORS = { civic = 'CIVIC_NAVAL_TRADITION', property = 'CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION' },
}

function P.StageTwoProfiles()
    if profiles then return profiles end
    profiles = {}
    local byKey = {}
    for key, service in pairs(serviceRules) do
        local district = GameInfo.Districts['DISTRICT_CSC_' .. key .. '_QUARTER']
        if district then
            local profile = {key = key, district = district, base = 'CLASS_CSC_' .. key .. '_BASE',
                specialty = 'CLASS_CSC_' .. key .. '_SPEC', service = service, producers = {}, customers = {}}
            byKey[key] = profile
            profiles[#profiles + 1] = profile
        end
    end
    if GameInfo.CSC_QuarterFlowBuildings and GameInfo.CSC_QuarterCustomerBuildings then
        for row in GameInfo.CSC_QuarterFlowBuildings() do
            local p = byKey[row.QuarterKey]
            local building = GameInfo.Buildings[row.BuildingType]
            if p and row.Stage == 2 and building and building.PrereqDistrict == p.district.DistrictType then
                p.producers[#p.producers + 1] = building
            end
        end
        local variants = {}
        for row in GameInfo.BuildingReplaces() do
            local building = GameInfo.Buildings[row.CivUniqueBuildingType]
            if building then
                local list = variants[row.ReplacesBuildingType] or {}
                list[#list + 1] = building
                variants[row.ReplacesBuildingType] = list
            end
        end
        local districtVariants = {}
        for row in GameInfo.DistrictReplaces() do
            local district = GameInfo.Districts[row.CivUniqueDistrictType]
            if district then
                local list = districtVariants[row.ReplacesDistrictType] or {}
                list[#list + 1] = district
                districtVariants[row.ReplacesDistrictType] = list
            end
        end
        local function addToHost(profile, building, district)
            local list = profile.customers[district.Index] or {}
            list[building.Index] = building
            profile.customers[district.Index] = list
        end
        local function addCustomer(profile, building)
            local district = GameInfo.Districts[building.PrereqDistrict]
            if not district then return end
            addToHost(profile, building, district)
            for _, replacement in ipairs(districtVariants[building.PrereqDistrict] or {}) do
                addToHost(profile, building, replacement)
            end
        end
        for row in GameInfo.CSC_QuarterCustomerBuildings() do
            local p = byKey[row.QuarterKey]
            local building = GameInfo.Buildings[row.BuildingType]
            if p and row.ProducerStage == 2 and building then
                addCustomer(p, building)
                for _, variant in ipairs(variants[row.BuildingType] or {}) do addCustomer(p, variant) end
            end
        end
    end
    table.sort(profiles, function(a, b) return a.district.Index < b.district.Index end)
    return profiles
end

local function materialOptions()
    if improvementsByResource then return improvementsByResource end
    local options = {}
    for row in GameInfo.Improvement_ValidResources() do
        for _, profile in ipairs(P.StageTwoProfiles()) do
            if CSC_Adjacency.HasTag(profile.base, row.ResourceType)
                or CSC_Adjacency.HasTag(profile.specialty, row.ResourceType) then
                local resource = GameInfo.Resources[row.ResourceType]
                local improvement = GameInfo.Improvements[row.ImprovementType]
                if resource and improvement then
                    options[resource.Index] = options[resource.Index] or {}
                    options[resource.Index][#options[resource.Index] + 1] = improvement.Index
                end
                break
            end
        end
    end
    improvementsByResource = options
    return options
end

-- A working improvement and a deposit that could supply the chain later are
-- distinct facts. A compatible pillaged improvement remains a repair option.
-- Scope supply to the player because adjacent tiles can belong to other cities.
function P.ReadSuppliers(player, quarter, profile)
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
                if CSC_Adjacency.HasTag(profile.base, resource) then supplies.base[#supplies.base + 1] = material end
                if CSC_Adjacency.HasTag(profile.specialty, resource) then supplies.specialty[#supplies.specialty + 1] = material end
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

local function hasWorkingBase(base)
    for _, material in ipairs(base) do
        if material.working then return true end
    end
    return false
end

-- One unfinished job per chain. Prefer repairing a compatible improvement.
-- Otherwise choose a currently buildable supplier, even when several viable
-- deposits exist. CE and the game still own assignment and execution.
local function offerBaseJob(player, chain, recover, bid)
    if bid <= 0 or chain.workingBase then return end
    local team = player:GetTeam()
    local best, bestRepair
    for _, material in ipairs(chain.supply.base) do
        local plot = Map.GetPlotByIndex(material.plot)
        local current = plot:GetImprovementType()
        for _, index in ipairs(materialOptions()[plot:GetResourceType()]) do
            local repair = current == index and plot:IsImprovementPillaged()
            local definition = GameInfo.Improvements[index]
            local tech = definition and definition.PrereqTech and GameInfo.Technologies[definition.PrereqTech]
            local civic = definition and definition.PrereqCivic and GameInfo.Civics[definition.PrereqCivic]
            local buildable = repair or definition
                and (not definition.PrereqTech or tech and player:GetTechs():HasTech(tech.Index))
                and (not definition.PrereqCivic or civic and player:GetCulture():HasCivic(civic.Index))
                and ImprovementBuilder.CanHaveImprovement(plot, index, team)
            if buildable and (not best or repair and not bestRepair
                or repair == bestRepair and material.plot < best) then
                best, bestRepair = material.plot, repair
            end
        end
    end
    if best then recover[best] = math.max(recover[best] or 0, bid) end
end

-- One snapshot per existing Quarter, shared by the placement, material
-- protection and building adapters. All tile and building facts are read
-- again next turn. Only loaded relationship definitions are cached.
function P.ReadChains(player)
    local byDistrict, chains = {}, {}
    for _, profile in ipairs(P.StageTwoProfiles()) do byDistrict[profile.district.Index] = profile end
    for _, city in player:GetCities():Members() do
        local districts = city:GetDistricts()
        for index = 0, districts:GetNumDistricts() - 1 do
            local quarter = districts:GetDistrictByIndex(index)
            local profile = quarter and byDistrict[quarter:GetType()]
            if profile then
                local plot = Map.GetPlot(quarter:GetX(), quarter:GetY())
                local complete = quarter:IsComplete()
                local ready = complete and not quarter:IsPillaged()
                local supply = P.ReadSuppliers(player, plot, profile)
                chains[#chains + 1] = { profile = profile, city = city, plot = plot,
                    complete = complete, ready = ready, supply = supply, workingBase = hasWorkingBase(supply.base),
                    active = ready and (city:GetProperty(profile.service.property) or 0) > 0 }
            end
        end
    end
    return chains
end

local function visitCustomerPlots(player, chain, visit)
    for _, plot in ipairs(Map.GetAdjacentPlots(chain.plot:GetX(), chain.plot:GetY())) do
        local variants = chain.profile.customers[plot:GetDistrictType()]
        if variants and plot:GetOwner() == player then
            local buyer = Cities.GetPlotPurchaseCity(plot)
            if buyer and buyer:GetOwner() == player then visit(buyer, plot:GetIndex(), variants) end
        end
    end
end

local function canTrainDockmasterShip(playerID, cityID, canProduce, lastEra, trainable)
    if trainable[cityID] ~= nil then return trainable[cityID] end
    if not dockmasterShipHashes then
        dockmasterShipHashes = {}
        for unit in GameInfo.Units() do
            if unit.Domain == 'DOMAIN_SEA' and not unit.MustPurchase and dockmasterNavalClasses[unit.PromotionClass] then
                local tech = unit.PrereqTech and GameInfo.Technologies[unit.PrereqTech]
                local civic = unit.PrereqCivic and GameInfo.Civics[unit.PrereqCivic]
                local techEra = tech and tech.EraType and GameInfo.Eras[tech.EraType]
                local civicEra = civic and civic.EraType and GameInfo.Eras[civic.EraType]
                if (techEra or civicEra)
                    and (not unit.PrereqTech or techEra and techEra.Index <= lastEra)
                    and (not unit.PrereqCivic or civicEra and civicEra.Index <= lastEra) then
                    dockmasterShipHashes[#dockmasterShipHashes + 1] = unit.Hash
                end
            end
        end
    end
    for _, hash in ipairs(dockmasterShipHashes) do
        if canProduce(playerID, cityID, hash, true) then
            trainable[cityID] = true
            return true
        end
    end
    trainable[cityID] = false
    return false
end


local function connectStageTwo(player, chain, nominations, recover, repairs, limits, canProduce, seen, repairCities)
    local profile, city, plot = chain.profile, chain.city, chain.plot:GetIndex()
    local pid, cityID = player:GetID(), city:GetID()
    local buildings = city:GetBuildings()
    local producerWorks, producerExists, customerWorks, customerHost = false, false, false, false
    for _, producer in ipairs(profile.producers) do
        producerExists = producerExists or buildings:HasBuilding(producer.Index)
        producerWorks = producerWorks or workingBuildingAt(buildings, producer, plot)
    end

    local function bid(buyer, building, value)
        local delta = math.min(limits.nomination, value)
        if delta <= 0 or not canProduce or not canProduce(pid, buyer:GetID(), building.Hash) then return end
        local key = buyer:GetID() .. ':' .. building.Index
        local existing = seen[key]
        if existing then
            existing.delta = math.max(existing.delta, delta)
        else
            local entry = {player=pid, city=buyer:GetID(), building=building.Index, delta=delta}
            nominations[#nominations + 1], seen[key] = entry, entry
        end
    end

    local civic = GameInfo.Civics and GameInfo.Civics[profile.service.civic]
    local unlocked = civic and player:GetCulture():HasCivic(civic.Index)
    local lastNavalEra = profile.key == 'TAILORS' and GameInfo.Eras and GameInfo.Eras.ERA_RENAISSANCE
    local checkShips = lastNavalEra and chain.ready and chain.workingBase and not producerExists
        and unlocked and canProduce and player:GetEra() <= lastNavalEra.Index
    local navalProductionAvailable = false
    local hasBase = #chain.supply.base > 0
    visitCustomerPlots(pid, chain, function(buyer, footprint, variants)
        customerHost = true
        local buyerBuildings = buyer:GetBuildings()
        local exists = false
        for _, building in pairs(variants) do
            exists = exists or buyerBuildings:HasBuilding(building.Index)
            if workingBuildingAt(buyerBuildings, building, footprint) then
                customerWorks = true
                if checkShips and not navalProductionAvailable then
                    navalProductionAvailable = canTrainDockmasterShip(
                        pid, buyer:GetID(), canProduce, lastNavalEra.Index, limits.trainableShips)
                end
            end
        end
        -- The producer/customer exchange can pay before the Service unlock.
        if chain.ready and producerWorks and hasBase and not exists then
            for _, building in pairs(variants) do bid(buyer, building, CUSTOMER_BID_Q8) end
        end
    end)

    if chain.ready then
        if chain.workingBase and customerWorks and not producerExists then
            -- Keep the modest exchange bid whenever the supplier and customer
            -- are working. The larger Tailors bid prices Dockmaster production
            -- only while the AI is in the sail era and its customer can use it.
            local servicePremium = unlocked and (profile.key ~= 'TAILORS' or navalProductionAvailable)
            local value = servicePremium and READY_PRODUCER_BID_Q8 or EXCHANGE_PRODUCER_BID_Q8
            for _, producer in ipairs(profile.producers) do bid(city, producer, value) end
        end
        if customerWorks or (producerWorks and customerHost) then
            local value = producerWorks and customerWorks and limits.builder
                or math.min(limits.builder, EARLY_SUPPLIER_BID_Q8)
            offerBaseJob(player, chain, recover, value)
        end
    elseif limits.repair and unlocked and chain.complete and chain.workingBase
        and producerExists and not producerWorks and customerWorks and not repairCities[cityID] then
        -- A damaged Quarter can block repair of its producer. Offer the
        -- missing prerequisite at native value. CE admits at most one
        -- candidate per city and rechecks the actual district and queue.
        repairs[#repairs + 1] = {player=pid, city=cityID, district=profile.district.Index, plot=plot}
        repairCities[cityID] = true
    end
end

local function materialRisk(player, builderBidLimit, nominationLimit, canProduceBuilding, admitRepairs)
    local risks, recover, nominations, repairs = {}, {}, {}, {}
    local seen, repairCities = {}, {}
    local limits = {builder=math.min(builderBidLimit or 0, READY_SUPPLIER_BID_Q8),
        nomination=nominationLimit or 0, repair=admitRepairs, trainableShips={}}
    local chains = P.ReadChains(player)
    for _, chain in ipairs(chains) do
        priceSupply(risks, chain.supply.base, chain.active)
        priceSupply(risks, chain.supply.specialty, false)
        if chain.complete and (limits.builder > 0 or limits.nomination > 0 or limits.repair) then
            connectStageTwo(player, chain, nominations, recover, repairs, limits, canProduceBuilding, seen, repairCities)
        end
    end
    return risks, recover, nominations, repairs, chains
end



-- A supplier can be in a different city from the Quarter. Key the deduction
-- to the city that could actually place a district there, as CE expects.
function P.MaterialDeductions(player, includeBuilders, builderBidLimit, nominationLimit,
    canProduceBuilding, admitRepairs)
    local playerID = player:GetID()
    local entries, builderSites, exclusions = {}, {}, {}
    local risks, recover, nominations, repairs, chains = materialRisk(player, builderBidLimit,
        nominationLimit, canProduceBuilding, admitRepairs)
    for index, cost in pairs(risks) do
        local plot = Map.GetPlotByIndex(index)
        local city = Cities.GetPlotPurchaseCity(plot)
        if city and city:GetOwner() == playerID then
            local cityID = city:GetID()
            if cost >= LAST_DEPOSIT_COST_Q8 then
                exclusions[#exclusions + 1] = {player = playerID, city = cityID, plot = index, cost = cost}
            end
            if includeBuilders and (cost >= LAST_DEPOSIT_COST_Q8 or recover[index]) then
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
    return entries, builderSites, nominations, repairs, chains, exclusions
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
