-- Controlled replay of an operating Bakers/Market exchange on an archived
-- turn-200 world. The setup removes only the mapped Market in both arms.
-- Ordinary AI remains responsible for selecting and executing its rebuild.
local pid = 5
local quarter = assert(Map.GetPlotByIndex(987))
local host = assert(Map.GetPlotByIndex(913))
local source = assert(Cities.GetPlotPurchaseCity(quarter))
local customer = assert(Cities.GetPlotPurchaseCity(host))
local bakery = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_BAKERY)
local market = assert(GameInfo.Buildings.BUILDING_MARKET)
assert(source:GetOwner() == pid and customer:GetOwner() == pid
    and source:GetID() == 262147 and not Players[pid]:IsHuman())
assert(host:GetDistrictType() == GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index
    and Map.GetPlotDistance(quarter:GetX(), quarter:GetY(), host:GetX(), host:GetY()) == 1)
assert(source:GetBuildings():HasBuilding(bakery.Index)
    and not source:GetBuildings():IsPillaged(bakery.Index)
    and source:GetBuildings():GetBuildingLocation(bakery.Index) == quarter:GetIndex())

local buildings = customer:GetBuildings()
local function active()
    return buildings:HasBuilding(market.Index) and not buildings:IsPillaged(market.Index)
        and buildings:GetBuildingLocation(market.Index) == host:GetIndex()
end

local function exchange()
    local transaction
    for row in GameInfo.CSC_BuildingTransactions() do
        if row.SourceBuildingType == bakery.BuildingType and row.PartnerBuildingType == market.BuildingType
            and row.QuantityKind == 'PARTNER_POPULATION' then
            transaction = row.TransactionId
        end
    end
    assert(transaction, 'No loaded Bakery/Market population exchange')
    local sourceAmount, customerAmount = 0, 0
    for row in GameInfo.CSC_BuildingTransactionYields() do
        if row.TransactionId == transaction then
            if row.Recipient == 'SOURCE' then sourceAmount = source:GetProperty(row.AmountProperty) or 0
            else customerAmount = customer:GetProperty(row.AmountProperty) or 0 end
        end
    end
    return sourceAmount, customerAmount
end

if mode == 'setup' then
    assert(Game.GetCurrentGameTurn() == 200 and active(), 'Source Market does not match the archived case')
    local seller, buyer = exchange()
    assert(seller > 0 and buyer > 0, 'Existing exchange not observed')
    buildings:RemoveBuilding(market.Index)
    assert(not buildings:HasBuilding(market.Index), 'The test Market was not removed')
    print('CSC_MILESTONE_MARKET_SETUP', pid, customer:GetID(), host:GetIndex(), market.Index, seller, buyer)
elseif mode == 'legal' then
    assert(not buildings:HasBuilding(market.Index)
        and ExposedMembers.CSC_Adjacency.CanProduceItem(pid, customer:GetID(), market.Hash),
        'Rebuild is not native-legal')
    print('CSC_MILESTONE_MARKET_LEGAL', Game.GetCurrentGameTurn(), pid, customer:GetID(), market.Index)
else
    assert(mode == 'outcome')
    local seller, buyer = exchange()
    print('CSC_MILESTONE_MARKET_OUTCOME', Game.GetCurrentGameTurn(), pid, customer:GetID(),
        tostring(active()), seller, buyer)
end
