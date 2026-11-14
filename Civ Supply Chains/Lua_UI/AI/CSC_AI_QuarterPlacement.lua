-- Shared Bakers and Tailors supplier and Stage 2 chain policy. Read loaded
-- material classes, buyer stages and live footprints, then translate missing
-- or threatened links into candidate bids, repair offers and protection for
-- the CE publisher. Specialty development waits for its Stage 4 buyer; deposit
-- protection and acquisition also value its immediate Quarter adjacency.
-- The bounded Bakers forecast diagnostic at the end has its own caller.
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
-- The ready-chain band comes from the matched Melbourne Mill nomination.
-- The smaller band prices ordinary exchange when there is no Service premium.
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
    -- Cache the loaded definitions once. A city lookup uses the host district
    -- index, then checks the actual building variant and footprint at runtime.
    if profiles then return profiles end
    profiles = {}
    local byKey = {}
    for key, service in pairs(serviceRules) do
        local district = GameInfo.Districts['DISTRICT_CSC_' .. key .. '_QUARTER']
        if district then
            local profile = {key = key, district = district, base = 'CLASS_CSC_' .. key .. '_BASE',
                specialty = 'CLASS_CSC_' .. key .. '_SPEC', service = service, producers = {}, specialtyBuyers = {}, customers = {}}
            byKey[key] = profile
            profiles[#profiles + 1] = profile
        end
    end
    if GameInfo.CSC_QuarterFlowBuildings and GameInfo.CSC_QuarterCustomerBuildings then
        for row in GameInfo.CSC_QuarterFlowBuildings() do
            local p = byKey[row.QuarterKey]
            local building = GameInfo.Buildings[row.BuildingType]
            if p and building and building.PrereqDistrict == p.district.DistrictType then
                if row.Stage == 2 then p.producers[#p.producers + 1] = building end
                if row.Stage == 4 then p.specialtyBuyers[#p.specialtyBuyers + 1] = building end
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
        -- Stage 4 is a development gate, not a request to construct that buyer
        -- or an assumed active Service. Respect loaded unique replacements.
        for _, p in ipairs(profiles) do
            local buyers = {}
            for _, building in ipairs(p.specialtyBuyers) do
                buyers[#buyers + 1] = building
                for _, variant in ipairs(variants[building.BuildingType] or {}) do
                    buyers[#buyers + 1] = variant
                end
            end
            p.specialtyBuyers = buyers
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
    -- Cache resource-to-improvement definitions. The map and player can change
    -- whether an improvement is legal, present, pillaged or currently useful.
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

-- Map suitability can exist before the improvement is unlocked. Share the
-- unlock check between the siting forecast and the actual Builder offer.
local function improvementUnlocked(player, index)
    local definition = GameInfo.Improvements[index]
    if not definition then return false end
    local tech = definition.PrereqTech and GameInfo.Technologies[definition.PrereqTech]
    local civic = definition.PrereqCivic and GameInfo.Civics[definition.PrereqCivic]
    return (not definition.PrereqTech or tech and player:GetTechs():HasTech(tech.Index))
        and (not definition.PrereqCivic or civic and player:GetCulture():HasCivic(civic.Index))
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
            local viable, working, ready = false, false, false
            for _, improvement in ipairs(options[resourceID]) do
                if improvement == current then
                    viable = true
                    working = not plot:IsImprovementPillaged()
                    ready = true -- An existing compatible improvement can be used or repaired.
                    break
                end
                -- Native Lua wrapper 1a2a0 consumes a PLAYER ID, not a team.
                -- Its ownership-sensitive query is appropriate for this owned reader.
                if ImprovementBuilder.CanHaveImprovement(plot, improvement, playerID) then
                    viable = true
                    ready = ready or improvementUnlocked(player, improvement)
                end
            end
            if viable then
                local resource = GameInfo.Resources[resourceID].ResourceType
                local material = {plot = plot:GetIndex(), resource = resource, working = working, ready = ready}
                if CSC_Adjacency.HasTag(profile.base, resource) then supplies.base[#supplies.base + 1] = material end
                if CSC_Adjacency.HasTag(profile.specialty, resource) then supplies.specialty[#supplies.specialty + 1] = material end
            end
        end
    end
    return supplies
end

local function priceSupply(risks, supply, activeService)
    -- Losing the last possible deposit and losing the last working supplier
    -- are different risks. Charge the highest band when the loss would break
    -- an already active Stage 2 Base supply link.
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

local function hasWorkingMaterial(supply)
    for _, material in ipairs(supply) do
        if material.working then return true end
    end
    return false
end

-- One unfinished job per material class per chain. Prefer repairing a
-- compatible improvement, then the lowest plot index among buildable deposits.
-- Base and Spec share this plumbing; their buyer-stage gates are separate.
-- Shared plots retain the strongest bid, never a sum. CE and the game still
-- own assignment and execution; these Q8 values are proposals, not commands.
local function offerMaterialJob(player, chain, kind, recover, bid)
    local supply = chain.supply[kind] or {}
    if bid <= 0 or hasWorkingMaterial(supply) then return end
    local playerID = player:GetID()
    local best, bestRepair
    for _, material in ipairs(supply) do
        local plot = Map.GetPlotByIndex(material.plot)
        local current = plot:GetImprovementType()
        for _, index in ipairs(materialOptions()[plot:GetResourceType()]) do
            local repair = current == index and plot:IsImprovementPillaged()
            local buildable = repair or improvementUnlocked(player, index)
                and ImprovementBuilder.CanHaveImprovement(plot, index, playerID)
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
                    complete = complete, ready = ready, supply = supply, workingBase = hasWorkingMaterial(supply.base),
                    -- The Service source property is a policy signal. Auditing
                    -- the customer payout requires separate evidence.
                    active = ready and (city:GetProperty(profile.service.property) or 0) > 0 }
            end
        end
    end
    return chains
end

local function visitCustomerPlots(player, chain, visit)
    -- Customer adjacency is between district plots. The recipient city can be
    -- the Quarter's own city or another city of the same player.
    for _, plot in ipairs(Map.GetAdjacentPlots(chain.plot:GetX(), chain.plot:GetY())) do
        local variants = chain.profile.customers[plot:GetDistrictType()]
        if variants and plot:GetOwner() == player then
            local buyer = Cities.GetPlotPurchaseCity(plot)
            if buyer and buyer:GetOwner() == player then visit(buyer, plot:GetIndex(), variants) end
        end
    end
end

local function canTrainDockmasterShip(playerID, cityID, canProduce, lastEra, trainable)
    -- Cache the ship definitions for the session and the queue answer only for
    -- this player's current snapshot. A trainable ship establishes a possible
    -- use for the bonus. It does not forecast demand for that ship.
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
    local producerWorks, producerExists, customerWorks = false, false, false
    for _, producer in ipairs(profile.producers) do
        producerExists = producerExists or buildings:HasBuilding(producer.Index)
        producerWorks = producerWorks or workingBuildingAt(buildings, producer, plot)
    end

    local function bid(buyer, building, value)
        -- The UI reads immediate queue legality. CE may encounter the bid
        -- later when the ordinary building comparison runs. An occupied
        -- native planning slot can delay that comparison while forecasts
        -- continue. Keep the strongest offer when several chains suggest it.
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
        -- A working Stage 2 buyer already pays for improved Base materials;
        -- an absent customer must not suppress that ordinary supply benefit.
        -- Reserve the larger band for a producer/customer pair that works now.
        if customerWorks or producerWorks then
            local value = producerWorks and customerWorks and limits.builder
                or math.min(limits.builder, EARLY_SUPPLIER_BID_Q8)
            offerMaterialJob(player, chain, 'base', recover, value)
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

local function materialRisk(player, builderBidLimit, nominationLimit, canProduceBuilding, admitRepairs,economy)
    -- Share deduplication and city queue reads across all chains for this player.
    local risks, recover, nominations, repairs = {}, {}, {}, {}
    local seen, repairCities = {}, {}
    local limits = {builder=math.min(builderBidLimit or 0, READY_SUPPLIER_BID_Q8),
        nomination=nominationLimit or 0, repair=admitRepairs, trainableShips={}}
    local chains = economy and economy.chains or P.ReadChains(player)
    for _, chain in ipairs(chains) do
        priceSupply(risks, chain.supply.base, chain.active)
        priceSupply(risks, chain.supply.specialty, false)
        if economy and CSC_AI_EconomyAdapters then
            -- The central ledger supplies marginal ordinary economic loss;
            -- structural last-deposit/active-Service floors remain deliberate
            -- protection policy, not substitute forecasts of yield income.
            for _,kind in ipairs({'base','specialty'})do for _,material in ipairs(chain.supply[kind])do
                local value=CSC_AI_EconomyAdapters.SupplyValue(economy,chain,material.plot)
                if value then risks[material.plot]=math.max(risks[material.plot]or 0,
                    math.min(256*256,math.max(0,value)))end
            end end
        end
        if chain.complete and (limits.builder > 0 or limits.nomination > 0 or limits.repair) then
            connectStageTwo(player, chain, nominations, recover, repairs, limits, canProduceBuilding, seen, repairCities)
            -- Spec improvement exchange starts at Stage 4. Mere technology,
            -- Stage 2 progress or a remote/pillaged buyer cannot activate it.
            -- Reuse the modest 26-unit band: no unmeasured Stage 4 Service uplift.
            if chain.ready and limits.builder > 0 then
                for _, buyer in ipairs(chain.profile.specialtyBuyers or {}) do
                    if workingBuildingAt(chain.city:GetBuildings(), buyer, chain.plot:GetIndex()) then
                        offerMaterialJob(player, chain, 'specialty', recover,
                            math.min(limits.builder, EARLY_SUPPLIER_BID_Q8))
                        break
                    end
                end
            end
        end
    end
    return risks, recover, nominations, repairs, chains
end



-- A supplier can be in a different city from the Quarter. Key the deduction
-- to the city that could actually place a district there, as CE expects.
function P.MaterialDeductions(player, includeBuilders, builderBidLimit, nominationLimit,
    canProduceBuilding, admitRepairs,economy)
    local playerID = player:GetID()
    local entries, builderSites, exclusions = {}, {}, {}
    local risks, recover, nominations, repairs, chains = materialRisk(player, builderBidLimit,
        nominationLimit, canProduceBuilding, admitRepairs,economy)
    for index, cost in pairs(risks) do
        local plot = Map.GetPlotByIndex(index)
        local city = Cities.GetPlotPurchaseCity(plot)
        if city and city:GetOwner() == playerID then
            local cityID = city:GetID()
            -- A finite score deduction covers each legal district pair. Scarce
            -- supply also gets a plot exclusion for the native selector.
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

-- An unowned supplier needs its own investment, separate from buying a Quarter
-- footprint. The existing CE improvement bid feeds the native plot forecast:
-- AnalyzeCityPlots ranks resource frontier rows, then Economic quotes its cached
-- winner and applies its ordinary savings, legality and Treasury checks. This
-- publishes neither a purchase command nor a Builder assignment.
function P.SupplierAcquisitionOffers(player, chains, ui, builderBidLimit)
    local result, seen = {}, {}
    local delta = math.min(builderBidLimit or 0, EARLY_SUPPLIER_BID_Q8)
    if delta <= 0 or not ui or type(ui.GetPlotPurchaseQuote) ~= 'function' then return result end
    local pid, options = player:GetID(), materialOptions()
    for _, chain in ipairs(chains) do
        -- Both resource classes give immediate Quarter adjacency, even before
        -- their buyers exist. Secure only the first missing viable deposit in
        -- each class. Improvement development remains Stage 2/4 buyer-gated
        -- above; this offer neither assumes nor grants a future Service.
        for _, kind in ipairs({'base', 'specialty'}) do
            if chain.ready and #(chain.supply[kind] or {}) == 0 then
                local best
                for _, plot in ipairs(Map.GetAdjacentPlots(chain.plot:GetX(), chain.plot:GetY())) do
                    local resource = GameInfo.Resources[plot:GetResourceType()]
                    if plot:GetOwner() == -1 and plot:GetDistrictType() == -1 and plot:GetImprovementType() == -1
                        and resource and options[resource.Index]
                        and PlayersVisibility[pid]:IsRevealed(plot:GetX(), plot:GetY())
                        and CSC_Adjacency.ResourceVisible(pid, resource.Index)
                        and CSC_Adjacency.HasTag(chain.profile[kind], resource.ResourceType) then
                        local improvements = {}
                        for _, index in ipairs(options[resource.Index]) do
                            if improvementUnlocked(player, index) then improvements[#improvements + 1] = index end
                        end
                        -- Lua CanHaveImprovement forces the native ownership check
                        -- and rejects ordinary unowned tiles. Do not call it here
                        -- or invent a fourth ignore-ownership argument. These are
                        -- mapped, unlocked proposals: native row admission validates
                        -- actor/geometry and preserves zero/negative scores before CE
                        -- can add the finite 26-unit Q8 early-supplier band.
                        local ok, quote = false, nil
                        if #improvements > 0 then
                            ok, quote = pcall(ui.GetPlotPurchaseQuote, pid, chain.city:GetID(), plot:GetIndex())
                        end
                        if ok and type(quote) == 'number' and quote > 0
                            and (not best or quote < best.purchaseGold
                                or quote == best.purchaseGold and plot:GetIndex() < best.plot) then
                            best = {player=pid, city=chain.city:GetID(), plot=plot:GetIndex(), improvements=improvements,
                                deltaQ8=delta, acquisition=true, purchaseGold=quote, quarter=chain.plot:GetIndex(), materialClass=kind}
                        end
                    end
                end
                if best then
                    -- One deterministic option per class, no stacking when several
                    -- Quarters or classes share a purchased plot. Rebuild from live
                    -- ownership/quotes each publication; acquisition retires
                    -- this offer on the next turn.
                    local key = best.city .. ':' .. best.plot
                    if not seen[key] then result[#result + 1], seen[key] = best, true end
                end
            end
        end
    end
    return result
end

-- Diagnostic only. The late-placement research driver supplies exact native
-- forecast components. The ordinary publisher uses the early-score bids above.
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
    -- The measured components must reconcile with the native aggregate before
    -- returning a correction. A missing contributor would make it ambiguous.
    if forecast.beforeQ8 + originalUplift ~= forecast.nativeQ8 then return nil end
    return correctedUplift - originalUplift
end
