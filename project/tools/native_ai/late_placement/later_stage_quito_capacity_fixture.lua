-- DIAGNOSTIC ONLY. Open the same city district slot in each copy of the
-- natural turn-200 Quito save. The game chooses both districts and any
-- competing production. The new population can change native scores, so
-- only the post-preparation control establishes this replay's margin.
local player,cityID,quarterPlot,customerPlot=1,196610,2603,2529
local city=assert(CityManager.GetCity(player,cityID))
local reader=assert(ExposedMembers.CSC_Adjacency)
local quarter=assert(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER)
local customer=assert(GameInfo.Districts.DISTRICT_COMMERCIAL_HUB)
local rival=assert(GameInfo.Districts.DISTRICT_RURALCOMMUNITYA)

local function targets(definition,index)
    for _,target in ipairs(assert(reader.GetLegalDistrictTargets(player,cityID,definition.Hash)))do
        if target==index then return true end
    end
    return false
end

local function empty(index)
    local plot=assert(Map.GetPlotByIndex(index))
    local owner=Cities.GetPlotPurchaseCity(plot)
    assert(plot:GetOwner()==player and owner and owner:GetID()==cityID and plot:GetDistrictType()==-1)
    return plot
end

if mode=='before' then
    assert(Game.GetCurrentGameTurn()==224)
    local capacity=assert(reader.GetDistrictCapacity(player,cityID))
    assert(capacity.used==capacity.allowed)
    print('CSC_MILESTONE_QUITO_CAPACITY_BEFORE',capacity.population,capacity.used,capacity.allowed)
elseif mode=='setup' then
    assert(Game.GetCurrentGameTurn()==224 and city:GetOwner()==player)
    local q,c=empty(quarterPlot),empty(customerPlot)
    assert(Map.GetPlotDistance(q:GetX(),q:GetY(),c:GetX(),c:GetY())==1)
    assert(not city:GetDistricts():HasDistrict(quarter.Index) and not city:GetDistricts():HasDistrict(customer.Index))
    local population=city:GetPopulation()
    -- The next standard slot arrives at populations 1, 4, 7 and so on.
    -- The UI readback below verifies the real capacity after the change.
    local added=3-(population-1)%3
    city:ChangePopulation(added)
    assert(city:GetPopulation()==population+added)
    print('CSC_MILESTONE_QUITO_CAPACITY_SETUP',player,cityID,population,population+added)
elseif mode=='legal' then
    local capacity=assert(reader.GetDistrictCapacity(player,cityID))
    assert(capacity.allowed-capacity.used==1 and targets(quarter,quarterPlot)
        and targets(customer,customerPlot) and targets(rival,quarterPlot))
    print('CSC_MILESTONE_QUITO_CAPACITY_LEGAL',player,cityID,quarterPlot,customerPlot,capacity.allowed)
elseif mode=='outcome' then
    print('CSC_MILESTONE_QUITO_CAPACITY_OUTCOME',Game.GetCurrentGameTurn(),
        Map.GetPlotByIndex(quarterPlot):GetDistrictType(),Map.GetPlotByIndex(customerPlot):GetDistrictType())
else
    error('Unknown Quito capacity observation')
end
