-- Shared Bakers and Tailors supplier and Stage 2 chain policy. Read loaded
-- material classes, buyer stages and live footprints, then translate missing
-- or threatened links into candidate bids, repair offers and protection for
-- the CE publisher. Material development reads the exact working or actively
-- producing buyer for each stage. Deposit protection and acquisition also
-- value immediate Quarter adjacency.
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
local MATERIAL_WORKER_RADIUS = 6
local MATERIAL_QUEUE_HORIZON = 5
-- Trebizond's measured stream gives about 18–19 points for Food and
-- 17.5 each for Production and Gold. Round each term down. The bid
-- covers the immediate exchange with a working Mill.
local CUSTOMER_BID_Q8 = (18 + 17 + 17) * 256

local improvementsByResource
local materialWorkerTypes
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
        -- Keep the loaded improvement vocabulary generic. ReadSuppliers filters
        -- it by the caller's Base/Spec tags; customer-first planning can thus
        -- discover a later Quarter without adding it to the Stage 2 policy list.
        local resource = GameInfo.Resources[row.ResourceType]
        local improvement = GameInfo.Improvements[row.ImprovementType]
        if resource and improvement then
            options[resource.Index] = options[resource.Index] or {}
            options[resource.Index][#options[resource.Index] + 1] = improvement.Index
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
        local definition = resourceID >= 0 and GameInfo.Resources[resourceID]
        local base = definition and CSC_Adjacency.HasTag(profile.base, definition.ResourceType)
        local specialty = definition and CSC_Adjacency.HasTag(profile.specialty, definition.ResourceType)
        -- The generic definition cache must not cause native geometry calls
        -- for unrelated nearby resources on every Quarter/site publication.
        if (base or specialty) and options[resourceID] and plot:GetOwner() == playerID and plot:GetDistrictType() == -1
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
                local material = {plot = plot:GetIndex(), resource = definition.ResourceType, working = working, ready = ready}
                if base then supplies.base[#supplies.base + 1] = material end
                if specialty then supplies.specialty[#supplies.specialty + 1] = material end
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

-- Prefer an unlocked job for the first missing supply link. For a locked
-- option, quote its actual transaction at the estimated research finish plus
-- normal work delay. Follow only one concrete prerequisite path at a time.
-- If both systems are required, bid for the longer outstanding path first.
local function materialUnlock(player, economy, definition)
    local best, delay
    local function check(kind, key, definitions, accessor, has, active)
        if not key or key=='' then return true end
        local row=definitions[key]
        if not row then return false end
        local object=player[accessor](player)
        if object[has](object,row.Index) then return true end
        local turns=economy.Research(kind,key)
        if type(turns)~='number' or turns<1 or turns>=math.huge then return false end
        delay=math.max(delay or 0,turns)
        if (not object[active] or object[active](object)~=row.Index)
            and (not best or turns>best.turns) then
            best={kind=kind,index=row.Index,turns=turns}
        end
        return true
    end
    if check('tech',definition.PrereqTech,GameInfo.Technologies,'GetTechs','HasTech','GetResearchingTech')
        and check('civic',definition.PrereqCivic,GameInfo.Civics,'GetCulture','HasCivic','GetProgressingCivic') then
        return best,delay
    end
end

-- Pick the best exact buildable operation per supplier. Rank by the gain for
-- a working buyer. At equal value prefer repair, then stable plot and
-- improvement indices. Only the best operation in a missing class gets the
-- fallback band. Other positive operations still reach stock selection.
local function offerMaterialJob(player, chain, kind, recover, bid, economy, research, pendingBuyer, committedBuyer, operatingBuyer)
    local supply = chain.supply[kind] or {}
    if bid <= 0 then return end
    -- The calibrated floor is for opening a missing material link. Further
    -- suppliers can still pay their own transactions to the same working
    -- buyer. They compete using their actual marginal utility alone.
    -- A distant producer can still justify parallel work at its discounted
    -- value. The first-link floor is for a buyer ready within the existing
    -- five-turn Builder planning allowance.
    local supplied = hasWorkingMaterial(supply)
    local floor = (supplied or committedBuyer and committedBuyer.turns>MATERIAL_QUEUE_HORIZON)
        and 0 or bid
    local playerID = player:GetID()
    local best, bestLocked
    local localJobs = {}
    local quote=economy and CSC_AI_EconomyAdapters and CSC_AI_EconomyAdapters.MaterialJobValue
    for _, material in ipairs(supply) do
        if not material.working then
            local plot = Map.GetPlotByIndex(material.plot)
            local current = plot:GetImprovementType()
            local readyHere, lockedHere, buildHere
            for _, index in ipairs(materialOptions()[plot:GetResourceType()]) do
                local repair = current == index and plot:IsImprovementPillaged()
                local buildable = repair or improvementUnlocked(player, index)
                    and ImprovementBuilder.CanHaveImprovement(plot, index, playerID)
                if buildable then
                    local value,ordinary
                    if quote then
                        local ok, direct, service=pcall(quote,economy,chain,kind,plot,index,nil,committedBuyer)
                        if ok and type(direct)=='number'then value,ordinary=direct+(service or 0),direct end
                    end
                    value=value or 0
                    readyHere=math.max(readyHere or 0,value)
                    if (floor>0 or value>0) and (not buildHere or value>buildHere.value or value==buildHere.value
                        and (repair and not buildHere.repair or repair==buildHere.repair and index<buildHere.improvement)) then
                        -- A new improvement can finish in one action on a bare
                        -- plot. Keep clearing and replacement in normal order.
                        local finish=repair or current==-1 and plot.GetFeatureType and plot:GetFeatureType()==-1
                        buildHere={plot=material.plot,improvement=index,repair=repair,finish=finish,
                            value=value,ordinary=ordinary or 0}
                    end
                elseif research and quote and economy.Research and not improvementUnlocked(player,index)
                    and ImprovementBuilder.CanHaveImprovement(plot,index,playerID) then
                    local topic,delay=materialUnlock(player,economy,GameInfo.Improvements[index])
                    if topic and delay+5<(chain.economy and chain.economy.horizon or 0) then
                        local ok,direct,service=pcall(quote,economy,chain,kind,plot,index,delay+5,committedBuyer or pendingBuyer)
                        local value=ok and type(direct)=='number'and direct+(service or 0)
                        if ok and type(value)=='number' and value>0 and (not lockedHere or value>lockedHere.value) then
                            lockedHere={topic=topic,value=value,plot=material.plot,improvement=index}
                        end
                    end
                end
            end
            if buildHere then
                localJobs[#localJobs+1]=buildHere
                if not best or buildHere.value>best.value or buildHere.value==best.value
                    and (buildHere.repair and not best.repair or buildHere.repair==best.repair and buildHere.plot<best.plot) then
                    best=buildHere
                end
            end
            -- A ready improvement on this tile already pays its best known
            -- leg. Research gets only a positive gain over that option.
            if lockedHere then
                lockedHere.value=lockedHere.value-(readyHere or 0)
                if lockedHere.value>0 and(not bestLocked or lockedHere.value>bestLocked.value
                    or lockedHere.value==bestLocked.value and lockedHere.plot<bestLocked.plot) then
                    bestLocked=lockedHere
                end
            end
        end
    end
    -- An existing buyer earns the measured gain from another supplier even
    -- when it can already improve a different deposit. The same-plot overlap
    -- was deducted above. A producer still in the plan only justifies research
    -- for its first supplier when nothing can already fill the opening.
    if bestLocked and (not pendingBuyer or not best) then
        local topic=bestLocked.topic
        local key=topic.kind..':'..topic.index
        local offer=research[key] or {player=playerID,kind=topic.kind,index=topic.index,value=0,jobs={}}
        research[key]=offer
        -- Multiple buyers can genuinely benefit from one technology. The
        -- native queue sees one bid for the topic and no speculative fallback.
        offer.value=offer.value+bestLocked.value
        offer.jobs[bestLocked.plot]=true
    end
    for _,candidate in ipairs(localJobs)do
        if candidate==best or candidate.value>0 then
            local jobs=recover[candidate.plot]or{}
            recover[candidate.plot]=jobs
            local job=jobs[candidate.improvement]or{floor=0,value=0,ordinary=0}
            jobs[candidate.improvement]=job
            -- Add distinct buyer gains once per physical supplier operation.
            -- The fallback applies to the best missing link only, and is not
            -- stacked across buyers. A shared tile still needs one charge.
            if candidate==best then job.floor=math.max(job.floor,floor) end
            job.value=job.value+candidate.value
            job.ordinary=job.ordinary+candidate.ordinary
            job.repair=candidate.repair
            -- Give an operating buyer's sole mapped supplier a chance to
            -- finish in the worker's current turn. The native pass still
            -- needs the exact Builder on site under this job's control.
            job.finishSupply=job.finishSupply or (operatingBuyer and #supply==1 and candidate.finish)
            -- One working input restores this material channel to a present buyer.
            -- An eligible replacement deposit can restore it while the old one waits.
            job.restoreSupply=job.restoreSupply or (operatingBuyer and not supplied)
            if committedBuyer and (not job.commitment or committedBuyer.turns<job.commitment.turns) then
                -- Diagnostic source for the earliest queued buyer on a shared
                -- job. Its contribution is already accounted for in job.value.
                job.commitment={type=committedBuyer.type,turns=committedBuyer.turns,
                    city=chain.city:GetID(),quarter=chain.plot:GetIndex(),kind=kind}
            end
        end
    end
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


local function connectStageTwo(player, chain, nominations, recover, repairs, limits, canProduce, seen, repairCities, economy, research)
    local profile, city, plot = chain.profile, chain.city, chain.plot:GetIndex()
    local pid, cityID = player:GetID(), city:GetID()
    local buildings = city:GetBuildings()
    local producerWorks, producerExists, localProducer, customerWorks = false, false, false, false
    for _, producer in ipairs(profile.producers) do
        local present = buildings:HasBuilding(producer.Index)
        local onQuarter = present and buildings:GetBuildingLocation(producer.Index) == plot
        producerExists = producerExists or present
        localProducer = localProducer or onQuarter
        producerWorks = producerWorks or onQuarter and not buildings:IsPillaged(producer.Index)
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
        local committedBuyer = not producerExists and chain.economy and economy and economy.MaterialBuyerCommitment
            and economy.MaterialBuyerCommitment(city,profile.producers,chain.economy.horizon)
        if customerWorks or producerWorks or committedBuyer then
            local value = producerWorks and customerWorks and limits.builder
                or math.min(limits.builder, EARLY_SUPPLIER_BID_Q8)
            local pendingBuyer
            -- A customer and a queue-legal producer can already justify the
            -- missing unlock. Waiting for a working producer here can stall a
            -- chain whose producer nomination also needs an improved material.
            -- Scope the forecast to the earliest legal Stage 2 option and
            -- keep this future income out of immediate job and capacity bids.
            if not committedBuyer and research and customerWorks and not producerExists and not chain.workingBase and canProduce then
                for _,option in ipairs(chain.economy and chain.economy.seconds or{})do
                    local producer=GameInfo.Buildings[option.type]
                    if producer and option.unlock==0 and not option.excluded and option.turns<chain.economy.horizon
                        and (not pendingBuyer or option.turns<pendingBuyer.turns)
                        and canProduce(pid,cityID,producer.Hash) then pendingBuyer=option end
                end
            end
            offerMaterialJob(player, chain, 'base', recover, value, economy,research,pendingBuyer,committedBuyer,producerWorks)
        end
    elseif limits.repair and unlocked and chain.complete and localProducer and customerWorks and not repairCities[cityID] then
        -- Losing the Quarter and every Farm in the same event can leave each
        -- job waiting on the other. A compatible repair or legal, unlocked
        -- Base improvement gives the existing producer a credible path back.
        -- Offer only the missing district prerequisite at native value. CE
        -- admits one candidate per city and still checks the native queue.
        for _, material in ipairs(chain.supply.base) do
            if material.ready then
                repairs[#repairs + 1] = {player=pid, city=cityID, district=profile.district.Index, plot=plot}
                repairCities[cityID] = true
                break
            end
        end
    end
end

local function materialRisk(player, builderBidLimit, nominationLimit, canProduceBuilding, admitRepairs,economy,research)
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
            local economicPlots={}
            for _,kind in ipairs({'base','specialty'})do for _,material in ipairs(chain.supply[kind])do
                economicPlots[material.plot]=true
            end end
            -- Actual native material legs can exist on a nonstandard current
            -- improvement even when no legal future Builder mapping selects it.
            -- Protect those economic relationships too. The central fact reader
            -- owns eligibility; the structural lists retain last-deposit policy.
            -- Quote a shared Base/Spec plot once: its ledger counterfactual already
            -- removes every affected leg and adjacency on that physical tile.
            for _,material in ipairs(chain.economy and chain.economy.suppliers or{})do
                economicPlots[material.plot]=true
            end
            for plot in pairs(economicPlots)do
                local value=CSC_AI_EconomyAdapters.SupplyValue(economy,chain,plot)
                if value then risks[plot]=math.max(risks[plot]or 0,
                    math.min(256*256,math.max(0,value)))end
            end
        end
        if chain.complete and (limits.builder > 0 or limits.nomination > 0 or limits.repair) then
            connectStageTwo(player, chain, nominations, recover, repairs, limits, canProduceBuilding, seen, repairCities, economy,research)
            -- Specialty jobs can run while the exact Stage 4 buyer is under
            -- construction. Earlier stages, a spare unlock and remote buyers
            -- do not qualify. Use the same modest first-supplier band as Base.
            if chain.ready and limits.builder > 0 then
                local buyers=chain.profile.specialtyBuyers or {}
                local workingSpecialtyBuyer=false
                for _, buyer in ipairs(buyers) do
                    if workingBuildingAt(chain.city:GetBuildings(), buyer, chain.plot:GetIndex()) then
                        workingSpecialtyBuyer=true
                        break
                    end
                end
                local committedBuyer=not workingSpecialtyBuyer and chain.economy and economy and economy.MaterialBuyerCommitment
                    and economy.MaterialBuyerCommitment(chain.city,buyers,chain.economy.horizon)
                if workingSpecialtyBuyer or committedBuyer then
                    offerMaterialJob(player, chain, 'specialty', recover,
                        math.min(limits.builder, EARLY_SUPPLIER_BID_Q8), economy,research,nil,committedBuyer,workingSpecialtyBuyer)
                end
            end
        end
    end
    return risks, recover, nominations, repairs, chains
end



-- A supplier can be in a different city from the Quarter. Key the deduction
-- to the city that could actually place a district there, as CE expects.
function P.MaterialDeductions(player, includeBuilders, builderBidLimit, nominationLimit,
    canProduceBuilding, admitRepairs,economy,research)
    local playerID = player:GetID()
    local entries, builderSites, exclusions = {}, {}, {}
    local risks, recover, nominations, repairs, chains = materialRisk(player, builderBidLimit,
        nominationLimit, canProduceBuilding, admitRepairs,economy,research)
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
                local options = materialOptions()[plot:GetResourceType()] or {}
                -- Keep a working supplier in place. For a deposit that is not
                -- working yet, keep all mapped improvements available to Civ.
                local working = not plot:IsImprovementPillaged()
                for _, improvement in ipairs(options) do
                    if improvement == current and working then
                        options = {current}
                        break
                    end
                end
                -- CE keeps alternatives legal but applies the score bonus
                -- only to the exact improvement chosen for a chain. Both
                -- kinds of entry share the same plot guard for harvests.
                local allowed, jobs={},recover[index]or{}
                for _,improvement in ipairs(options)do
                    local job=jobs[improvement]
                    if job then
                        builderSites[#builderSites+1]={player=playerID,city=cityID,plot=index,
                            improvements={improvement},deltaQ8=math.min(builderBidLimit,math.max(job.floor,job.value)),
                            jobValueQ8=job.value,ordinaryQ8=job.ordinary,repair=job.repair,
                            finishSupply=job.finishSupply,restoreSupply=job.restoreSupply,commitment=job.commitment}
                    else
                        allowed[#allowed+1]=improvement
                    end
                end
                if #allowed>0 then
                    builderSites[#builderSites+1]={player=playerID,city=cityID,plot=index,improvements=allowed}
                end
            end
            for district in GameInfo.Districts() do
                if district.Index > 0 and plot:CanHaveDistrict(district.Index, playerID, cityID) then
                    entries[#entries + 1] = {
                        player = playerID, city = cityID, district = district.Index, plot = index, delta = -cost,
                        -- Complete Quarter valuation consumes only this named
                        -- supply loss, never another planner's site heuristic.
                        protectionQ8 = cost,
                    }
                end
            end
        end
    end
    return entries, builderSites, nominations, repairs, chains, exclusions
end

local function materialWorkers()
    if materialWorkerTypes or not GameInfo.Improvement_ValidBuildUnits then return materialWorkerTypes end
    -- Loaded permissions include compatible modded workers. For example, the
    -- City Lights Farmer can build a Pasture but cannot build an R2 Sawmill.
    -- Keep repair-only permissions separate so they cannot cover a new job.
    materialWorkerTypes={}
    for row in GameInfo.Improvement_ValidBuildUnits()do
        local unit=GameInfo.Units[row.UnitType]
        local improvement=GameInfo.Improvements[row.ImprovementType]
        if unit and improvement then
            local works=materialWorkerTypes[unit.Index] or {}
            materialWorkerTypes[unit.Index]=works
            works[improvement.Index]={repairOnly=row.ValidRepairOnly==true or row.ValidRepairOnly==1}
        end
    end
    return materialWorkerTypes
end

local function materialArea(plot)
    local area=plot and plot.GetArea and plot:GetArea()
    local id=area and area:GetID()
    return id and id>=0 and id or nil
end

-- Translate the exact jobs into a short list of native Builder-production
-- sponsorships. Reserve a charge once across all cities. Screen the near-term
-- inventory cheaply, then ask Civ for a route where the gameplay path query
-- is exposed. A nearby worker is only an estimate: Civ can spend its turn
-- on another job before this tree recruits. Leave a residual-only offer for
-- that exact fallback, which CE can use only when the native tree actually
-- requests a Builder. A finish offer names the on-site Builder for a
-- sole-supplier repair or bare-plot improvement. CE verifies that the exact
-- native job still holds that Builder before promoting it within the same
-- priority pass. A separate loan offer can restore any missing material at
-- an operating buyer. It names a routed worker and expires with this packet.
local loanArtifactIndex
local function loanArtifact()
    if loanArtifactIndex~=nil then return loanArtifactIndex end
    local artifact = GameInfo.Resources.RESOURCE_ANTIQUITY_SITE
    loanArtifactIndex = -1
    if artifact and GameInfo.Resource_Harvests then
        local harvestable=false
        for row in GameInfo.Resource_Harvests() do
            if row.ResourceType==artifact.ResourceType then harvestable=true;break end
        end
        if artifact.ResourceClassType=='RESOURCECLASS_ARTIFACT' and not harvestable then
            loanArtifactIndex=artifact.Index
        end
    end
    return loanArtifactIndex
end

function P.MaterialBuilderOffers(player, sites, ui, limit, dispatchLimit, loanEnabled)
    dispatchLimit=dispatchLimit or 0
    local builder=GameInfo.Units and GameInfo.Units.UNIT_BUILDER
    if (limit<=0 and dispatchLimit<=0 and not loanEnabled) or not builder or not player.GetUnits or not ui
        or type(ui.GetEconomyCityNumber)~='function' then return {},{} end
    -- One estimate of each plot's best job, one shareable roster, and one
    -- list of compatible units in production for the entire AI player.
    local jobs, byPlot, workforce, training = {}, {}, {}, {}
    local workers=materialWorkers()
    local function canWork(unitType,site)
        if not workers then return unitType==builder.Index end
        local permissions=workers[unitType]
        local permission=permissions and permissions[site.improvements[1]]
        return permission and (not permission.repairOnly or site.repair)
    end
    for _,site in ipairs(sites)do
        if site.deltaQ8 and (site.jobValueQ8 or 0)>0 and canWork(builder.Index,site) then
            local old=byPlot[site.plot]
            if not old or site.jobValueQ8>old.jobValueQ8 then byPlot[site.plot]=site end
        end
    end
    if not next(byPlot) then return {},{} end
    for _,site in pairs(byPlot)do jobs[#jobs+1]=site end
    table.sort(jobs,function(a,b)
        if a.jobValueQ8~=b.jobValueQ8 then return a.jobValueQ8>b.jobValueQ8 end
        return a.plot<b.plot
    end)
    for _,unit in player:GetUnits():Members() do
        local kind=unit:GetType()
        if kind==builder.Index or workers and workers[kind] then
            local charges=unit:GetBuildCharges()
            if charges>0 then
                workforce[#workforce+1]={object=unit,kind=kind,x=unit:GetX(),y=unit:GetY(),charges=charges}
            end
        end
    end
    for _,city in player:GetCities():Members()do
        local cityID=city:GetID()
        local ok,queued=pcall(ui.GetEconomyCityNumber,player:GetID(),cityID,'currentUnit',0)
        if not ok then return {},{} end
        if queued==builder.Index or workers and workers[queued] then
            local _,turns=pcall(ui.GetEconomyCityNumber,player:GetID(),cityID,'unitTurns',queued)
            -- The income quote allows five turns for work. A compatible unit
            -- training nearby may fill one opening in that window. Keep
            -- nearby queue credit when the remaining turn count is missing.
            if type(turns)~='number' or turns<0 or turns<=MATERIAL_QUEUE_HORIZON then
                local x,y=city:GetX(),city:GetY()
                training[#training+1]={city=cityID,kind=queued,x=x,y=y,area=materialArea(Map.GetPlot(x,y))}
            end
        end
    end
    local uncovered,contingent,dispatch,dispatchUnits,pathChecks={},{},{},{},0
    local loan
    local getPath=UnitManager and UnitManager.GetMoveToPath
    for _,site in ipairs(jobs)do
        local plot=Map.GetPlotByIndex(site.plot)
        local worker,nearby=nil,{}
        for order,unit in ipairs(workforce)do
            if unit.charges>0 and canWork(unit.kind,site) then
                local distance=Map.GetPlotDistance(plot:GetX(),plot:GetY(),unit.x,unit.y)
                if distance<=MATERIAL_WORKER_RADIUS then nearby[#nearby+1]={unit=unit,distance=distance,order=order} end
            end
        end
        table.sort(nearby,function(a,b)
            if a.distance~=b.distance then return a.distance<b.distance end
            return a.order<b.order
        end)
        for _,candidate in ipairs(nearby)do
            local reachable=true
            local routeVerified=candidate.distance==0
            -- Bound expensive route reads. If the API or budget is absent,
            -- count the near charge conservatively and let native recruiting
            -- own the actual assignment instead of assuming a new unit is due.
            if candidate.distance>0 and getPath and pathChecks<12 then
                pathChecks=pathChecks+1
                local ok,path=pcall(getPath,candidate.unit.object,site.plot)
                if ok then
                    reachable=type(path)=='table' and (path[1]==site.plot or path[#path]==site.plot)
                    routeVerified=reachable
                end
            end
            if reachable then
                worker=candidate.unit
                -- Publish one proven route for an operating buyer with a missing
                -- material. CE checks the worker's position, whether the holder
                -- has idle work and whether this exact job needs recruitment.
                if loanEnabled and not loan and site.restoreSupply and routeVerified
                    and worker.kind==builder.Index and site.deltaQ8>0 then
                    loan={player=site.player,city=site.city,plot=site.plot,
                        improvement=site.improvements[1],unit=worker.object:GetID(),
                        unitType=worker.kind,x=worker.x,y=worker.y,artifact=loanArtifact()}
                end
                -- A candidate here is only provisional. The native worker
                -- pass checks custody and position again before changing order.
                if #dispatch<dispatchLimit and candidate.distance==0 and site.finishSupply
                    and worker.kind==builder.Index and site.deltaQ8>0 then
                    local id=worker.object:GetID()
                    if not dispatchUnits[id] then
                        dispatch[#dispatch+1]={player=site.player,city=site.city,plot=site.plot,
                            improvement=site.improvements[1],unit=id,unitType=worker.kind,x=worker.x,y=worker.y}
                        dispatchUnits[id]=true
                    end
                end
                break
            end
        end
        if worker then
            -- Native improvement repair finishes movement but preserves the
            -- charge. Credit one such repair per Builder in this five-turn
            -- estimate. Count further jobs against its capacity so a string
            -- of repairs cannot make one unit cover an entire area.
            if site.repair and not worker.repairCredited then
                worker.repairCredited=true
            else
                worker.charges=worker.charges-1
            end
            if #contingent<4 and site.jobValueQ8-site.deltaQ8>=256 then
                contingent[#contingent+1]=site
            end
        else
            -- A Builder in another city covers nearby jobs on the same land
            -- area. Reserve just one likely job per queued unit. A distant
            -- or overseas queue must leave independent work eligible.
            local area,x,y=#training>0 and materialArea(plot),plot:GetX(),plot:GetY()
            local closest,distance
            for _,crew in ipairs(training)do
                local knownAreas=area~=nil and crew.area~=nil
                local localJob=knownAreas and area==crew.area or not knownAreas and crew.city==site.city
                if not crew.claimed and localJob and canWork(crew.kind,site) then
                    local d=Map.GetPlotDistance(x,y,crew.x,crew.y)
                    if d<=MATERIAL_WORKER_RADIUS and (not distance or d<distance) then closest,distance=crew,d end
                end
            end
            if closest then closest.claimed=true
            elseif #uncovered<4 then uncovered[#uncovered+1]={site=site,x=x,y=y} end
        end
    end
    local result={}
    local function sponsor(site, extra, backup)
        local delta=math.min(limit,math.floor(extra))
        if delta>=256 then result[#result+1]={player=site.player,city=site.city,plot=site.plot,
            improvement=site.improvements[1],unit=builder.Index,deltaQ8=delta,
            contingency=backup==true} end
    end
    for _,job in ipairs(uncovered)do
        local site=job.site
        -- Decode Trigger passes the adjusted improvement value through Present
        -- Value to Build Unit. Supplement only the transaction value clipped
        -- out of that row. The native contract converts back to Q8 after its
        -- initializer takes the extra in whole utility units.
        local extra=math.max(0,site.jobValueQ8-site.deltaQ8)
        -- A newly trained Builder can spend another charge on nearby, unstaffed
        -- work. Count at most one other job in the same city's lands and halve
        -- its ordinary gain. Alternative jobs may restore the same Service.
        -- These are alternative requests. CE sponsors only one per publication.
        for _,other in ipairs(uncovered)do
            if other~=job and other.site.ordinaryQ8>0 and other.site.city==site.city
                and Map.GetPlotDistance(job.x,job.y,other.x,other.y)<=3 then
                extra=extra+other.site.ordinaryQ8/2
                break
            end
        end
        sponsor(site,extra)
    end
    -- Prefer capacity gaps with no known crew. Give a contingent job only
    -- its own unpaid value, without pricing extra jobs that already appear
    -- staffed. The shared packet retains one native sponsorship per player.
    for _,site in ipairs(contingent)do
        if #result>=4 then break end
        sponsor(site,site.jobValueQ8-site.deltaQ8,true)
    end
    return result,dispatch,loan
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
