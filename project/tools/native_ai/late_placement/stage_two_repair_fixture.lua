-- Shared-controller checkpoint diagnostic for Problem 13.1. Validate all
-- working chains first, then pillage exactly one building per case. Production
-- and repair decisions remain with the AI. This file is not part of the mod.
local fixture = assert(CSC_STAGE_TWO_REPAIR_FIXTURE)
assert(Game.GetCurrentGameTurn() == fixture.turn and #fixture.cases > 0)

local function cityFor(player, city)
    return player and player:GetCities():FindID(city)
end

local function buildingStatus(city, definition, plot)
    if not city then return 'missing' end
    local buildings = city:GetBuildings()
    if not buildings:HasBuilding(definition.Index) or buildings:GetBuildingLocation(definition.Index) ~= plot then
        return 'missing'
    end
    return buildings:IsPillaged(definition.Index) and 'pillaged' or 'working'
end

local function acquire(test)
    local player = assert(Players[test.player])
    assert(not player:IsHuman())
    local quarter, customer = assert(Map.GetPlotByIndex(test.quarter)), assert(Map.GetPlotByIndex(test.customer))
    assert(quarter:GetOwner() == test.player and customer:GetOwner() == test.player)
    assert(Map.GetPlotDistance(quarter:GetX(), quarter:GetY(), customer:GetX(), customer:GetY()) == 1)
    local source = assert(cityFor(player, test.city))
    local recipient = assert(Cities.GetPlotPurchaseCity(customer))
    assert(recipient:GetOwner() == test.player)
    local activeChain
    for _, chain in ipairs(CSC_AI_QuarterPlacement.ReadChains(player)) do
        if chain.city:GetID() == test.city and chain.plot:GetIndex() == test.quarter then
            activeChain = chain
            break
        end
    end
    assert(activeChain and activeChain.active and activeChain.workingBase)

    local producer = assert(GameInfo.Buildings[test.producer])
    local mappedProducer = false
    for _, candidate in ipairs(activeChain.profile.producers) do
        if candidate.Index == producer.Index then mappedProducer = true break end
    end
    local mappedCustomers = assert(activeChain.profile.customers[customer:GetDistrictType()])
    local buyer = assert(GameInfo.Buildings[test.buyer])
    assert(mappedProducer and mappedCustomers[buyer.Index])
    assert(buildingStatus(source, producer, test.quarter) == 'working')
    assert(buildingStatus(recipient, buyer, test.customer) == 'working')
    assert(test.damage == 'producer' or test.damage == 'customer')
    return {case=test, profile=activeChain.profile, recipient=recipient:GetID(), producer=producer, buyer=buyer}
end

local function sample(row, phase)
    local test = row.case
    local player = Players[test.player]
    local source = cityFor(player, test.city)
    local recipient = cityFor(player, row.recipient)
    local producerDamage = test.damage == 'producer'
    local city = cityFor(player, producerDamage and test.city or row.recipient)
    local building = producerDamage and row.producer or row.buyer
    local queue = city and city:GetBuildQueue()
    local production = queue and queue.GetCurrentProductionTypeHash and queue:GetCurrentProductionTypeHash()
    local service = source and source:GetProperty(row.profile.service.property) or 0
    local ui = ExposedMembers and ExposedMembers.CSC_Adjacency
    local canProduce = ui and ui.CanProduceItem
    local eligible = canProduce and city and tostring(canProduce(test.player, city:GetID(), building.Hash)) or 'unknown'
    print(string.format('CSC_STAGE_TWO_BUILDING_REPAIR phase=%s turn=%d player=%d quarter=%d customer=%d recipient=%d role=%s building=%s era=%d producer=%s buyer=%s service=%s canProduce=%s queue=%s',
        phase, Game.GetCurrentGameTurn(), test.player, test.quarter, test.customer, row.recipient, test.damage,
        building.BuildingType, player and player:GetEra() or -1, buildingStatus(source, row.producer, test.quarter),
        buildingStatus(recipient, row.buyer, test.customer), tostring(service), eligible, tostring(production)))
end

local qualified, used = {}, {}
for _, test in ipairs(fixture.cases) do
    local row = acquire(test)
    -- Give each damaged building its own empire so the repair cases do not
    -- compete for the same production or trade with one shared supplier.
    assert(not used[test.player], 'Repair cases must use distinct players')
    used[test.player] = true
    qualified[#qualified+1] = row
end
for _, row in ipairs(qualified) do sample(row, 'before') end
for _, row in ipairs(qualified) do
    local test, producer = row.case, row.case.damage == 'producer'
    local city = assert(cityFor(Players[test.player], producer and test.city or row.recipient))
    local building = producer and row.producer or row.buyer
    local buildings = city:GetBuildings()
    buildings:SetPillaged(building.Index, true)
    assert(buildings:IsPillaged(building.Index))
    sample(row, 'damaged')
end
GameEvents.OnGameTurnStarted.Add(function()
    for _, row in ipairs(qualified) do sample(row, 'poll') end
end)
print('CSC_STAGE_TWO_BUILDING_FIXTURE_READY ' .. #qualified)
