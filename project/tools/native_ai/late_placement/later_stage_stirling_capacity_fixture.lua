-- DIAGNOSTIC ONLY. Give both replay copies one district slot immediately
-- before the near-tie at Stirling. The game still chooses every build order.
local player, cityID, tailorsPlot = 2, 65536, 2692
local quarter = assert(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER)
local city = assert(CityManager.GetCity(player, cityID))
local plot = assert(Map.GetPlotByIndex(tailorsPlot))
local reader = assert(ExposedMembers.CSC_Adjacency)

if mode=='before' then
    assert(Game.GetCurrentGameTurn()==127)
    local capacity = assert(reader.GetDistrictCapacity(player, cityID))
    assert(capacity.used==6 and capacity.allowed==6 and
        (capacity.population==16 or capacity.population==17))
    print('CSC_MILESTONE_STIRLING_CAPACITY_BEFORE', capacity.population, capacity.used, capacity.allowed)
elseif mode=='setup' then
    assert(Game.GetCurrentGameTurn()==127)
    assert(city:GetOwner()==player and (city:GetPopulation()==16 or city:GetPopulation()==17))
    assert(plot:GetOwner()==player and Cities.GetPlotPurchaseCity(plot):GetID()==cityID)
    assert(plot:GetDistrictType()==-1 and not city:GetDistricts():HasDistrict(quarter.Index))
    for index, definition in pairs({[2618]=GameInfo.Districts.DISTRICT_HOLY_SITE,
                                    [2693]=GameInfo.Districts.DISTRICT_THEATER}) do
        local anchor = assert(Map.GetPlotByIndex(index))
        local district = assert(CityManager.GetDistrictAt(anchor:GetX(), anchor:GetY()))
        assert(anchor:GetOwner()==player and district:GetType()==definition.Index and district:IsComplete())
        assert(Map.GetPlotDistance(plot:GetX(), plot:GetY(), anchor:GetX(), anchor:GetY())==1)
    end
    city:ChangePopulation(19-city:GetPopulation())
    assert(city:GetPopulation()==19)
    print('CSC_MILESTONE_STIRLING_CAPACITY_SETUP', player, cityID, tailorsPlot, 19)
elseif mode=='legal' then
    local capacity = assert(reader.GetDistrictCapacity(player, cityID))
    assert(capacity.population==19 and capacity.used==6 and capacity.allowed==7)
    for _, index in ipairs(reader.GetLegalDistrictTargets(player, cityID, quarter.Hash)) do
        if index==tailorsPlot then
            print('CSC_MILESTONE_STIRLING_CAPACITY_LEGAL', player, cityID, tailorsPlot, capacity.allowed)
            return
        end
    end
    error('Stirling Tailors footprint unavailable after opening the slot')
elseif mode=='outcome' then
    print('CSC_MILESTONE_STIRLING_CAPACITY_OUTCOME', Game.GetCurrentGameTurn(), plot:GetDistrictType())
else
    error('Unknown Stirling capacity observation')
end
