-- Read-only accounting for a single Quarter plot. The lens requests this on
-- hover so opening the map does not scan modifiers for every visible pin.
include("CSC_AdjacencyCore")
CSC_QuarterTooltip = {}
local T = CSC_QuarterTooltip
local A = CSC_Adjacency
if not next(A.ByDistrict) then A.Initialize() end
local nativeAdjacencyYields = {}
for row in GameInfo.District_Adjacencies() do
    local change = GameInfo.Adjacency_YieldChanges[row.YieldChangeId]
    if change then
        local yields = nativeAdjacencyYields[row.DistrictType] or {}
        nativeAdjacencyYields[row.DistrictType] = yields
        yields[change.YieldType] = true
    end
end
local effectTypes = {
    EFFECT_ADJUST_BUILDING_YIELD_CHANGE = true,
    EFFECT_ADJUST_CITY_YIELD_CHANGE = true,
    EFFECT_ADJUST_CITY_YIELD_PER_POPULATION = true,
    EFFECT_ADJUST_PLOT_YIELD = true,
    EFFECT_ADJUST_DISTRICT_EXTRA_ENTERTAINMENT = true,
}

local function Add(totals, yield, amount)
    totals[yield] = (totals[yield] or 0) + amount
end

local function Working(plot, city)
    local districts = city and city:GetDistricts()
    local kind, index = plot:GetDistrictType(), plot:GetIndex()
    return districts and districts:IsComplete(kind, index) and not districts:IsPillaged(kind, index)
end

local function BuildingPlotReader()
    local byCity = {}
    return function(city, building)
        if not city or not building then return nil end
        local key = city:GetOwner() .. ":" .. city:GetID()
        local locations = byCity[key]
        if not locations then
            locations = {}
            byCity[key] = locations
            -- GetBuildingLocation is gameplay-only. Like CitySupport, use
            -- the UI building lists on each district plot, including Wonders.
            local buildings = city:GetBuildings()
            for _, district in city:GetDistricts():Members() do
                local plot = Map.GetPlot(district:GetX(), district:GetY())
                if plot then
                    local index = plot:GetIndex()
                    for _, buildingIndex in ipairs(buildings:GetBuildingsAtLocation(index)) do
                        if buildings:HasBuilding(buildingIndex) and not buildings:IsPillaged(buildingIndex) then
                            locations[buildingIndex] = index
                        end
                    end
                end
            end
        end
        return locations[building.Index]
    end
end

local function ReadAdjacencies(plot, city, district)
    local totals = {}
    if Working(plot, city) then
        -- The built district's adjacency read can already include CSC's live
        -- SelfBonus effects. Use the stock placement query only for yields
        -- with actual native rules, then add the encoded CSC amounts once.
        for yieldType in pairs(nativeAdjacencyYields[district.DistrictType] or {}) do
            local yield = GameInfo.Yields[yieldType]
            if yield then
                Add(totals, yieldType, plot:GetAdjacencyYield(city:GetOwner(), city:GetID(), district.Index, yield.Index))
            end
        end
        for _, rule in ipairs(A.ByDistrict[district.DistrictType] or {}) do
            if rule.ProvideType == "SelfBonus" then
                local amount = plot:GetProperty("CSC_ADJ_" .. rule.ID .. "_ENCODED_AMOUNT") or 0
                Add(totals, rule.YieldType, amount)
            end
        end
    end
    for _, neighbor in ipairs(Map.GetAdjacentPlots(plot:GetX(), plot:GetY())) do
        local other = GameInfo.Districts[neighbor:GetDistrictType()]
        local buyer = Cities.GetPlotPurchaseCity(neighbor)
        if other and neighbor:GetOwner() == city:GetOwner() and Working(neighbor, buyer) then
            for _, rule in ipairs(A.ByDistrict[other.DistrictType] or {}) do
                if rule.ProvideType == "SelfBonus" and rule.AdjacencyType == "FROM_RINGS_CAO_DISTRICT"
                    and rule.CustomAdjacentObject == district.DistrictType then
                    -- The receiving district can have several equal Quarter
                    -- sources. Attribute only this plot's share of the live total.
                    local property = "CSC_ADJ_" .. rule.ID
                    local count = neighbor:GetProperty(property .. "_TOTAL") or 0
                    if count > 0 then
                        Add(totals, rule.YieldType, (neighbor:GetProperty(property .. "_ENCODED_AMOUNT") or 0) / count)
                    end
                end
            end
        end
    end
    return totals
end

local function ObjectReader()
    local objects = {}
    return function(id)
        if not id then return {} end
        if objects[id] then return objects[id] end
        local object = {}
        local kind = (GameEffects.GetObjectType(id) or ""):upper()
        for field, value in (GameEffects.GetObjectString(id) or ""):gmatch("(%w+):%s*(-?%d+)") do
            object[field] = tonumber(value)
        end
        local owner = object.Owner or GameEffects.GetObjectsPlayerId(id)
        if owner and object.City then object.city = CityManager.GetCity(owner, object.City) end
        if not object.city and owner and Players[owner] and kind:match("CITY$") then
            -- Better Report Screen also encounters city owners by name.
            -- Match only within the native object's player.
            local name = GameEffects.GetObjectName(id)
            for _, city in Players[owner]:GetCities():Members() do
                if city:GetName() == name then object.city = city; break end
            end
        end
        object.building = kind:match("BUILDING$") ~= nil
        objects[id] = object
        return object
    end
end

local function CollectActive(key)
    local prefix = "MOD_CSC_" .. key .. "_"
    local effects, parents, roots = {}, {}, {}
    for row in GameInfo.BuildingModifiers() do
        local building = GameInfo.Buildings[row.BuildingType]
        if row.ModifierId:sub(1, #prefix) == prefix and building
            and building.PrereqDistrict == "DISTRICT_CSC_" .. key .. "_QUARTER" then
            roots[row.ModifierId] = roots[row.ModifierId] or {}
            table.insert(roots[row.ModifierId], building)
        end
    end
    for _, id in pairs(GameEffects.GetModifiers() or {}) do
        local live = GameEffects.GetModifierDefinition(id)
        local def = live and GameInfo.Modifiers[live.Id]
        if def and live.Id:sub(1, 8) == "MOD_CSC_" then
            local effect = GameInfo.DynamicModifiers[def.ModifierType]
            if effect and (effectTypes[effect.EffectType] or effect.EffectType == "EFFECT_ATTACH_MODIFIER")
                and GameEffects.GetModifierActive(id) then
                local args = live.Arguments or {}
                local owner = GameEffects.GetModifierOwner(id)
                local subjects = GameEffects.GetModifierSubjects(id) or {}
                if next(subjects) then
                    local instance = {id=live.Id, type=effect.EffectType, args=args, owner=owner, subjects=subjects}
                    if args.ModifierId then
                        local byOwner = parents[args.ModifierId] or {}
                        parents[args.ModifierId] = byOwner
                        for _, subject in pairs(subjects) do
                            byOwner[subject] = byOwner[subject] or {}
                            table.insert(byOwner[subject], instance)
                        end
                    elseif effectTypes[effect.EffectType] then
                        table.insert(effects, instance)
                    end
                end
            end
        end
    end
    return effects, parents, roots
end

local function QuarterSources(instance, snapshot, visited, plots)
    if visited[instance] then return end
    visited[instance] = true
    local owner = snapshot.object(instance.owner)
    if owner.building then
        for _, building in ipairs(snapshot.roots[instance.id] or {}) do
            local index = snapshot.buildingPlot(owner.city, building)
            if index then plots[index] = true end
        end
    end
    local byOwner = snapshot.parents[instance.id]
    for _, parent in ipairs(byOwner and byOwner[instance.owner] or {}) do
        QuarterSources(parent, snapshot, visited, plots)
    end
end

local function IsBuildingType(building, expected)
    if building == expected then return true end
    if not GameInfo.BuildingReplaces then return false end
    for row in GameInfo.BuildingReplaces() do
        if row.CivUniqueBuildingType == building and row.ReplacesBuildingType == expected then return true end
    end
    return false
end

local stage3ByRequirement
local function Stage3Properties()
    if stage3ByRequirement then return stage3ByRequirement end
    local properties, requirements = {}, {}
    for row in GameInfo.CSC_Stage3CustomerTransactions() do
        properties[row.SellerReturnAmountProperty] = {seller = row.SellerBuildingType}
        if row.CustomerYieldAmountProperty then
            properties[row.CustomerYieldAmountProperty] = {venue = row.CustomerBuildingType}
        end
    end
    for argument in GameInfo.RequirementArguments() do
        if argument.Name == "PropertyName" then
            local base = argument.Value:match("^(.*)_BIT_%d+$")
            if base and properties[base] then requirements[argument.RequirementId] = properties[base] end
        end
    end
    stage3ByRequirement = {}
    for row in GameInfo.RequirementSetRequirements() do
        if requirements[row.RequirementId] then stage3ByRequirement[row.RequirementSetId] = requirements[row.RequirementId] end
    end
    return stage3ByRequirement
end

local function CustomerShares(links, city, stage, buildingType)
    local suppliers = {}
    for _, link in ipairs(links) do
        if link.kind == "SALE" and link.stages and link.stages[stage] then
            local site = Map.GetPlotByIndex(link.target)
            local buyer = Cities.GetPlotPurchaseCity(site)
            if buyer and buyer:GetID() == city:GetID() and buyer:GetOwner() == city:GetOwner() then
                local buildings = buyer:GetBuildings()
                for _, index in ipairs(buildings:GetBuildingsAtLocation(link.target)) do
                    local host = GameInfo.Buildings[index]
                    if host and IsBuildingType(host.BuildingType, buildingType)
                        and buildings:HasBuilding(index) and not buildings:IsPillaged(index) then
                        suppliers[link.source] = true
                        break
                    end
                end
            end
        end
    end
    return suppliers
end

local routeImports = {
    BAKERS = {CONSUMER="BAKERY", SPECIALTY="CAFE"},
    TAILORS = {TAILOR="TAILOR", FASHION_HOUSE="FASHION_HOUSE"},
}

local function RouteShares(origin, key, goods, buildingPlot)
    local sources = {}
    local producer = routeImports[key] and routeImports[key][goods]
    local trade = origin and origin:GetTrade()
    if not producer or not trade then return sources end
    local building = GameInfo.Buildings["BUILDING_CSC_" .. key .. "_" .. producer]
    for _, route in ipairs(trade:GetOutgoingRoutes() or {}) do
        local destination = CityManager.GetCity(route.DestinationCityPlayer, route.DestinationCityID)
        local supplied = destination and destination:GetProperty("CSC_" .. key .. "_" .. producer .. "_SUPPLIED")
        local index = supplied and supplied > 0 and buildingPlot(destination, building)
        if index then sources[index] = (sources[index] or 0) + 1 end
    end
    return sources
end

local adjacentPayments, adjacentPaymentLeaves
local function AdjacentPayments()
    if adjacentPayments then return adjacentPayments, adjacentPaymentLeaves end
    adjacentPayments, adjacentPaymentLeaves = {}, {}
    local args, requirements, modifierArgs = {}, {}, {}
    for row in GameInfo.RequirementArguments() do
        args[row.RequirementId] = args[row.RequirementId] or {}
        args[row.RequirementId][row.Name] = row.Value
    end
    for row in GameInfo.RequirementSetRequirements() do
        requirements[row.RequirementSetId] = requirements[row.RequirementSetId] or {}
        table.insert(requirements[row.RequirementSetId], row.RequirementId)
    end
    for row in GameInfo.ModifierArguments() do
        modifierArgs[row.ModifierId] = modifierArgs[row.ModifierId] or {}
        modifierArgs[row.ModifierId][row.Name] = row.Value
    end
    for row in GameInfo.BuildingModifiers() do
        local building = GameInfo.Buildings[row.BuildingType]
        local wrapper = GameInfo.Modifiers[row.ModifierId]
        local improvementPayment = wrapper and wrapper.ModifierType == "MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER"
        local customerPayment = wrapper and wrapper.ModifierType == "MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER"
        if building and building.PrereqDistrict and building.PrereqDistrict:match("^DISTRICT_CSC_.+_QUARTER$")
            and (improvementPayment or customerPayment) and not wrapper.OwnerRequirementSetId then
            local childID = (modifierArgs[row.ModifierId] or {}).ModifierId
            local child = childID and GameInfo.Modifiers[childID]
            local setID = wrapper.SubjectRequirementSetId
            local set = setID and GameInfo.RequirementSets[setID]
            local leafType = improvementPayment and "MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS" or "MODIFIER_BUILDING_YIELD_CHANGE"
            if child and child.ModifierType == leafType
                and not child.OwnerRequirementSetId and not child.SubjectRequirementSetId
                and set and set.RequirementSetType == "REQUIREMENTSET_TEST_ALL" then
                local rule = {}
                local adjacent, supported = false, true
                for _, id in ipairs(requirements[setID] or {}) do
                    local requirement = GameInfo.Requirements[id]
                    local kind = requirement and requirement.RequirementType
                    local arguments = args[id] or {}
                    if not requirement or requirement.Inverse == true or requirement.Inverse == 1 then
                        supported = false
                    elseif kind == "REQUIREMENT_PLOT_ADJACENT_TO_OWNER" and not next(arguments) then
                        adjacent = true
                    elseif improvementPayment and kind == "REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES" and arguments.Tag and not rule.tag then
                        rule.tag = arguments.Tag
                    elseif improvementPayment and kind == "REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES"
                        and arguments.ImprovementType and not rule.improvement then
                        local improvement = GameInfo.Improvements[arguments.ImprovementType]
                        if improvement then rule.improvement = improvement.Index else supported = false end
                    elseif customerPayment and kind == "REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES"
                        and arguments.DistrictType and not rule.district then
                        local district = GameInfo.Districts[arguments.DistrictType]
                        if district then rule.district = district.Index else supported = false end
                    elseif customerPayment and kind == "REQUIREMENT_CITY_HAS_BUILDING"
                        and arguments.BuildingType and not rule.requiredBuilding then
                        rule.requiredBuilding = GameInfo.Buildings[arguments.BuildingType]
                        if not rule.requiredBuilding then supported = false end
                    else
                        supported = false
                    end
                end
                local payout = modifierArgs[childID] or {}
                rule.yield, rule.amount = payout.YieldType, tonumber(payout.Amount)
                rule.customer = customerPayment and payout.BuildingType and GameInfo.Buildings[payout.BuildingType]
                if supported and adjacent and (rule.tag or (rule.district and rule.customer)) and rule.yield and rule.amount then
                    local payments = adjacentPayments[building.Index] or {}
                    adjacentPayments[building.Index] = payments
                    payments[#payments + 1] = rule
                    adjacentPaymentLeaves[childID] = true
                end
            end
        end
    end
    return adjacentPayments, adjacentPaymentLeaves
end

local function MatchesPayment(rule, plot, owner)
    if rule.tag then
        local improvement = plot:GetImprovementType()
        if improvement < 0 or plot:IsImprovementPillaged() or (rule.improvement and rule.improvement ~= improvement) then return false end
        local resource = GameInfo.Resources[plot:GetResourceType()]
        return resource and A.ResourceVisible(owner, resource.Index) and A.HasTag(rule.tag, resource.ResourceType)
    end
    if plot:GetDistrictType() ~= rule.district then return false end
    local customer = Cities.GetPlotPurchaseCity(plot)
    if not Working(plot, customer) then return false end
    local buildings = customer:GetBuildings()
    if rule.requiredBuilding and not buildings:HasBuilding(rule.requiredBuilding.Index) then return false end
    for _, index in ipairs(buildings:GetBuildingsAtLocation(plot:GetIndex())) do
        if index == rule.customer.Index then
            return buildings:HasBuilding(index) and not buildings:IsPillaged(index)
        end
    end
    return false
end

local function ReadAdjacentPayments(totals, plot, city, payments)
    if not Working(plot, city) then return end
    local buildings = city:GetBuildings()
    local neighbors = Map.GetAdjacentPlots(plot:GetX(), plot:GetY())
    local owner = city:GetOwner()
    for _, index in ipairs(buildings:GetBuildingsAtLocation(plot:GetIndex())) do
        local rules = payments[index]
        if rules and buildings:HasBuilding(index) and not buildings:IsPillaged(index) then
            for _, neighbor in ipairs(neighbors) do
                if neighbor:GetOwner() == owner then
                    for _, rule in ipairs(rules) do
                        if MatchesPayment(rule, neighbor, owner) then Add(totals, rule.yield, rule.amount) end
                    end
                end
            end
        end
    end
end

local function Transactions(snapshot, key, plot, district, city)
    local totals, amenities = {}, 0
    local payments, paidLeaves = AdjacentPayments()
    -- The UI cannot consistently join attached effects back to the paying
    -- building. Read the SQL payouts once per working building and exact
    -- recipient, including when multiple Quarters pay the same recipient.
    ReadAdjacentPayments(totals, plot, city, payments)
    if not GameEffects then return totals, amenities end
    if not snapshot.effects then
        snapshot.effects, snapshot.parents, snapshot.roots = CollectActive(key)
        snapshot.object = ObjectReader()
        snapshot.buildingPlot = BuildingPlotReader()
        snapshot.stage3Properties = Stage3Properties()
    end
    local index = plot:GetIndex()
    for _, effect in ipairs(snapshot.effects) do
        local args = effect.args
        local amount = tonumber(args.Amount)
        if not paidLeaves[effect.id] and amount
            and (args.YieldType or effect.type == "EFFECT_ADJUST_DISTRICT_EXTRA_ENTERTAINMENT") then
            local building = args.BuildingType and GameInfo.Buildings[args.BuildingType]
            local sources = {}
            QuarterSources(effect, snapshot, {}, sources)
            local counted = {}
            for _, subject in pairs(effect.subjects) do
                local city = snapshot.object(subject).city or snapshot.object(effect.owner).city
                local recipient = building and building.PrereqDistrict == district.DistrictType
                    and snapshot.buildingPlot(city, building)
                local owners = sources
                local prefix = "MOD_CSC_" .. key .. "_"
                if city and not next(owners) and effect.id:sub(1, #prefix) == prefix then
                    -- Route counts are encoded as active 1/2/4/8/16 leaves.
                    -- Their Amount already includes the bit's weight.
                    local importID = effect.id:gsub("_BIT_%d+$", "")
                    local import = importID:match("_IMPORT_(.+)_FOOD$") or importID:match("_IMPORT_(.+)_CULTURE$")
                        or importID:match("_IMPORT_(.+)_AMENITY$")
                    if import then
                        owners = RouteShares(city, key, import, snapshot.buildingPlot)
                    elseif not building then
                        local def = GameInfo.Modifiers[effect.id]
                        local transaction = snapshot.stage3Properties[def.SubjectRequirementSetId]
                        if transaction and transaction.venue then
                            owners = CustomerShares(snapshot.links, city, 3, transaction.venue)
                        elseif transaction and transaction.seller then
                            recipient = snapshot.buildingPlot(city, GameInfo.Buildings[transaction.seller])
                        end
                    elseif not recipient and effect.id:find("_STAGE_4_", 1, true) and effect.id:find("_RETURN_", 1, true) then
                        owners = CustomerShares(snapshot.links, city, 4, args.BuildingType)
                    end
                end
                -- Reused leaf modifiers can have several active parent sources
                -- at one receiver. Share the actual amount across those sources.
                local share = recipient == index and 1 or 0
                if share == 0 and owners[index] then
                    local count = 0
                    for _, weight in pairs(owners) do count = count + (weight == true and 1 or weight) end
                    share = (owners[index] == true and 1 or owners[index]) / count
                end
                local target = effect.type == "EFFECT_ADJUST_PLOT_YIELD" and subject or city or subject
                if share > 0 and not counted[target] then
                    counted[target] = true
                    local scaled = amount * share
                    if effect.type == "EFFECT_ADJUST_CITY_YIELD_PER_POPULATION" then
                        -- The gameplay scanner first sizes the exchange from
                        -- customer population, then divides by the receiving
                        -- city's population to encode the native rate. Undo
                        -- that encoding using the receiving city's population.
                        scaled = scaled * (city and city:GetPopulation() or 0)
                    end
                    if args.YieldType then Add(totals, args.YieldType, scaled)
                    else amenities = amenities + scaled end
                end
            end
        end
    end
    return totals, amenities
end

local function RegionalAmenities(snapshot, city, building)
    snapshot.regionalAmenities = snapshot.regionalAmenities or {}
    local key = city:GetOwner() .. ":" .. building.Index
    if snapshot.regionalAmenities[key] then return snapshot.regionalAmenities[key] end
    local totals, cities, suppliers = {}, {}, {}
    snapshot.regionalAmenities[key] = totals
    local buildingPlot = snapshot.buildingPlot or BuildingPlotReader()
    snapshot.buildingPlot = buildingPlot
    local powered = GameInfo.Buildings_XP2 and GameInfo.Buildings_XP2[building.BuildingType]
    for _, candidate in Players[city:GetOwner()]:GetCities():Members() do
        cities[#cities + 1] = candidate
        local index = buildingPlot(candidate, building)
        if index then
            local plot = Map.GetPlotByIndex(index)
            -- The player's district cache is available in UI contexts.
            local district = Players[city:GetOwner()]:GetDistricts():FindID(plot:GetDistrictID())
            local amount = building.Entertainment or 0
            if powered and (powered.EntertainmentBonusWithPower or 0) > 0
                and candidate:GetPower():IsFullyPowered() then
                amount = amount + powered.EntertainmentBonusWithPower
            end
            suppliers[#suppliers + 1] = {
                index = index, x = plot:GetX(), y = plot:GetY(),
                range = building.RegionalRange + (district and district:GetExtraRegionalRange() or 0),
                amount = amount + (district and district:GetExtraRegionalEntertainment() or 0),
            }
        end
    end
    -- Native Growth::GetAmenitiesFromEntertainment takes the strongest copy of
    -- each building type within range of the receiving City Center. Split ties
    -- evenly for this ledger, so overlapping Quarters never claim that city's
    -- same amenity twice. Different building types retain separate budgets.
    for _, recipient in ipairs(cities) do
        local best, winners = 0, {}
        for _, source in ipairs(suppliers) do
            if Map.GetPlotDistance(source.x, source.y, recipient:GetX(), recipient:GetY()) <= source.range then
                if source.amount > best then best, winners = source.amount, {} end
                if source.amount == best and best > 0 then winners[#winners + 1] = source.index end
            end
        end
        for _, index in ipairs(winners) do totals[index] = (totals[index] or 0) + best / #winners end
    end
    return totals
end

-- These are the producer eligibility properties written by the same SQL
-- requirements as the Service effects. Tailors use a separate producer gate
-- for Wonders, also used by CSC_WonderServicePlacement.
local serviceProperties = {
    BAKERS = {
        [2] = "CSC_BAKERS_STAGE_2_EFFECT_GROWTH",
        [3] = "CSC_BAKERS_STAGE_3_EFFECT_HOUSING",
        [4] = "CSC_BAKERS_STAGE_4_EFFECT_TOURISM",
    },
    TAILORS = {
        [2] = "CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION",
        [3] = "CSC_TAILORS_STAGE_3_EFFECT_FAITH",
        [4] = "CSC_TAILORS_STAGE_4_EFFECT_TOURISM",
        Wonder = "CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE",
    },
}

local function SupportedServices(snapshot, key, index, city)
    local names = {}
    local properties = serviceProperties[key] or {}
    for _, link in ipairs(snapshot.links) do
        if link.kind == "SALE" and link.source == index and link.stages then
            for _, marker in ipairs(snapshot.markers) do
                if marker.icon and marker.index == link.target and marker.stage and link.stages[marker.stage] then
                    -- The marker proves the exact customer has a live Service.
                    -- The stage link and source gate prove this Quarter feeds it.
                    local property = marker.isWonder and properties.Wonder or properties[marker.stage]
                    local eligibility = property and city:GetProperty(property)
                    if eligibility == nil and property and not marker.isWonder then
                        eligibility = city:GetProperty(property .. "_ART")
                    end
                    if (tonumber(eligibility) or 0) > 0 then
                        local building = GameInfo.Buildings[marker.target]
                        if building then names[Locale.Lookup(building.Name)] = true end
                    end
                end
            end
        end
    end
    local sorted = {}
    for name in pairs(names) do sorted[#sorted + 1] = name end
    table.sort(sorted)
    return sorted
end

local function Number(amount)
    -- Match the stock city yield totals. The small tolerance protects exact tenths.
    local displayed = math.floor(amount * 10 + .00000001) / 10
    return string.format("%.1f", displayed):gsub("%.0$", "")
end

local function YieldLines(lines, totals)
    local start = #lines
    for yield in GameInfo.Yields() do
        local amount = Number(totals[yield.YieldType] or 0)
        if amount ~= "0" then
            lines[#lines + 1] = amount .. " " .. yield.IconString .. " " .. Locale.Lookup(yield.Name)
        end
    end
    if #lines == start then lines[#lines + 1] = "—" end
end

function T.Format(snapshot, key, index)
    local plot = Map.GetPlotByIndex(index)
    local district = plot and GameInfo.Districts[plot:GetDistrictType()]
    if not district then return "" end
    local lines = {Locale.Lookup(district.Name)}
    local city = Cities.GetPlotPurchaseCity(plot)
    if not city or plot:GetOwner() ~= Game.GetLocalPlayer()
        or not city:GetDistricts():IsComplete(district.Index, index) then return lines[1] end
    local adjacency = ReadAdjacencies(plot, city, district)
    local transactions, amenities = Transactions(snapshot, key, plot, district, city)
    local specialists, workers = {}, plot:GetWorkerCount()
    for yield in GameInfo.Yields() do specialists[yield.YieldType] = plot:GetYield(yield.Index) * workers end
    local maintenance = district.Maintenance or 0
    amenities = amenities + (district.Entertainment or 0)
    local buildings = city:GetBuildings()
    for _, buildingIndex in ipairs(buildings:GetBuildingsAtLocation(index)) do
        local building = GameInfo.Buildings[buildingIndex]
        if building and buildings:HasBuilding(buildingIndex) then
            maintenance = maintenance + (building.Maintenance or 0)
            if not buildings:IsPillaged(buildingIndex) then
                if (building.RegionalRange or 0) > 0 then
                    amenities = amenities + (RegionalAmenities(snapshot, city, building)[index] or 0)
                else
                    amenities = amenities + (building.Entertainment or 0)
                end
            end
        end
    end
    local function Heading(tag, ...)
        lines[#lines + 1] = ""
        lines[#lines + 1] = Locale.Lookup("LOC_CSC_LENS_QUARTER_" .. tag, ...)
    end
    Heading("ADJACENCY")
    YieldLines(lines, adjacency)
    Heading("TRANSACTIONS")
    YieldLines(lines, transactions)
    Heading("SERVICES")
    local services = SupportedServices(snapshot, key, index, city)
    for _, name in ipairs(services) do lines[#lines + 1] = "[ICON_Bullet] " .. name end
    if #services == 0 then lines[#lines + 1] = "—" end
    Heading("SPECIALISTS", workers)
    YieldLines(lines, specialists)
    lines[#lines + 1] = ""
    lines[#lines + 1] = Locale.Lookup("LOC_CSC_LENS_QUARTER_AMENITIES", Number(amenities))
    Heading("MAINTENANCE")
    YieldLines(lines, {YIELD_GOLD = -maintenance})
    return table.concat(lines, "[NEWLINE]")
end
