-- Prepare an Arena beside the archived Café so the Zoo is a legal option.
-- The same completed dependency is used on both copies. The native AI still
-- owns comparison, construction, and the eventual Café/Zoo exchange.
local pid, site, host = 3, 1503, 1576
local zoo = assert(GameInfo.Buildings.BUILDING_ZOO)
if mode == 'legal' then
    assert(ExposedMembers.CSC_Adjacency.CanProduceItem(pid, assert(expectedBuyer), zoo.Hash),
        'The Zoo fails immediate native eligibility')
    print('CSC_MILESTONE_ENTERTAINMENT_LEGAL', pid, expectedBuyer, zoo.Index)
    return
end

local quarter, venue = assert(Map.GetPlotByIndex(site)), assert(Map.GetPlotByIndex(host))
local source, customer = assert(Cities.GetPlotPurchaseCity(quarter)), assert(Cities.GetPlotPurchaseCity(venue))
local cafe = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_CAFE)
local arena = assert(GameInfo.Buildings.BUILDING_ARENA)
local function working(city, building, at)
    local buildings = city:GetBuildings()
    return buildings:HasBuilding(building.Index) and not buildings:IsPillaged(building.Index)
        and buildings:GetBuildingLocation(building.Index) == at
end
assert(source:GetOwner() == pid and customer:GetOwner() == pid and source:GetID() == 393221)
assert(working(source, cafe, site) and venue:GetDistrictType() == GameInfo.Districts.DISTRICT_ENTERTAINMENT_COMPLEX.Index)
assert(Map.GetPlotDistance(quarter:GetX(), quarter:GetY(), venue:GetX(), venue:GetY()) == 1)

if mode == 'setup' then
    assert(Game.GetCurrentGameTurn() == 200 and not Players[pid]:IsHuman() and customer:GetPopulation() >= 5)
    assert(not customer:GetBuildings():HasBuilding(zoo.Index), 'Zoo is already present')
    if not working(customer, arena, host) then
        assert(not customer:GetBuildings():HasBuilding(arena.Index), 'Arena is already present but blocked')
        customer:GetBuildQueue():CreateBuilding(arena.Index, host)
    end
    assert(working(customer, arena, host), 'Arena preparation failed')
    print('CSC_MILESTONE_ENTERTAINMENT_SETUP', pid, customer:GetID(), host, zoo.Index)
else
    assert(mode == 'outcome')
    local transaction = assert(GameInfo.CSC_BuildingTransactions.CSC_BAKERS_CAFE_ZOO)
    local seller, buyer = 0, 0
    for leg in GameInfo.CSC_BuildingTransactionYields() do
        if leg.TransactionId == transaction.TransactionId then
            if leg.Recipient == 'SOURCE' then seller = source:GetProperty(leg.AmountProperty) or 0
            else buyer = customer:GetProperty(leg.AmountProperty) or 0 end
        end
    end
    print('CSC_MILESTONE_ENTERTAINMENT_OUTCOME', Game.GetCurrentGameTurn(), pid, customer:GetID(),
        tostring(working(customer, zoo, host)), seller, buyer)
end
