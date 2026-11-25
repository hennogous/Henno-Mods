-- DIAGNOSTIC ONLY. Present one previously surveyed, district-free tile
-- as unowned on a copy of an ordinary save. The AI still controls its
-- treasury, savings, queue, native bids and build actions.
local scope=assert(fixtureParameters)
local playerID=scope.player
local player=assert(Players[playerID])
assert(not player:IsHuman())
local buyer=assert(CityManager.GetCity(playerID,scope.customerCity))
local receiver=assert(CityManager.GetCity(playerID,scope.quarterCity))
local site=assert(Map.GetPlotByIndex(scope.customerPlot))
local anchor=assert(Map.GetPlotByIndex(scope.quarterPlot))
local target=assert(GameInfo.Districts[scope.customer])
local reader=assert(ExposedMembers.CSC_Adjacency)

local function supplySignature(profile)
    local signature,workingBase={},0
    for material,rows in pairs(CSC_AI_QuarterPlacement.ReadSuppliers(player,anchor,profile))do
        for _,row in ipairs(rows)do
            signature[#signature+1]=table.concat({material,row.plot,row.resource,tostring(row.working)},':')
            if material=='base' and row.working then workingBase=workingBase+1 end
        end
    end
    table.sort(signature)
    return table.concat(signature,','),workingBase
end

if mode=='setup'then
    assert(Game.GetCurrentGameTurn()==fixtureTurn and Players[0]:IsHuman() and not AutoplayManager.IsActive())
    local owner=assert(Cities.GetPlotPurchaseCity(site))
    assert(site:GetOwner()==playerID and owner:GetID()==scope.customerCity and site:GetDistrictType()==-1,
        'The surveyed footprint is not an empty city-owned tile')
    assert(site:GetResourceType()==-1,'The test cannot release a resource tile')
    -- Preserve an ordinary improvement on the footprint. The native quote
    -- must continue to account for the real loss if a district replaces it.
    local improvement=site:GetImprovementType()
    local improvementPillaged=improvement>=0 and site:IsImprovementPillaged()
    assert(Map.GetPlotDistance(anchor:GetX(),anchor:GetY(),site:GetX(),site:GetY())==1)
    assert(Map.GetPlotDistance(buyer:GetX(),buyer:GetY(),site:GetX(),site:GetY())<=3)
    assert(not buyer:GetDistricts():HasDistrict(target.Index),'The buyer has already built this district type')
    local profile
    for _,row in ipairs(CSC_AI_QuarterPlacement.StageTwoProfiles())do
        if row.key==scope.quarter then profile=row;break end
    end
    assert(profile and anchor:GetOwner()==playerID and anchor:GetDistrictType()==profile.district.Index)
    local district=assert(receiver:GetDistricts():GetDistrict(profile.district.Index))
    assert(district:IsComplete() and not district:IsPillaged()
        and district:GetX()==anchor:GetX() and district:GetY()==anchor:GetY())
    local signature,workingBase=supplySignature(profile)
    assert(workingBase>0,'The saved Quarter has no working Base supplier yet')
    local treasury=assert(player:GetTreasury())
    local gold=treasury:GetGoldBalance()
    local terrain,feature,rivers=site:GetTerrainType(),site:GetFeatureType(),site:GetRiverCrossingCount()
    local preparedType,preparedPlot=-1,-1
    local parkProgress=scope.waterParkProgress or (scope.earlyWaterPark and 100)
    if parkProgress then
        -- Native Meroë chose this exact Water Park before the Hub. A nearly
        -- finished park gives both copies one ordinary production phase
        -- before the next choice, while the released Hub land is for sale.
        assert(fixtureTurn==150 and playerID==1 and scope.customerCity==65536
            and scope.quarterPlot==2735 and scope.customerPlot==2660
            and (parkProgress==95 or parkProgress==100),
            'Early Water Park is scoped to the recorded Meroë case')
        local park=assert(GameInfo.Districts.DISTRICT_WATER_ENTERTAINMENT_COMPLEX)
        local parkPlot=assert(Map.GetPlotByIndex(2737))
        local parkCity=assert(Cities.GetPlotPurchaseCity(parkPlot))
        assert(parkPlot:GetOwner()==playerID and parkCity:GetID()==scope.customerCity
            and parkPlot:GetDistrictType()==-1 and not buyer:GetDistricts():HasDistrict(park.Index),
            'The original Water Park site or city has changed')
        WorldBuilder.CityManager():CreateDistrict(buyer,park.DistrictType,parkProgress,parkPlot:GetIndex())
        local district=assert(buyer:GetDistricts():GetDistrict(park.Index),'Water Park preparation did not create the district')
        assert(district:IsComplete()==(parkProgress==100)
            and district:GetX()==parkPlot:GetX() and district:GetY()==parkPlot:GetY(),
            'The Water Park preparation did not reach the requested construction state')
        preparedType,preparedPlot=park.Index,parkPlot:GetIndex()
    end
    WorldBuilder.CityManager():SetPlotOwner(site:GetX(),site:GetY(),false)
    assert(site:GetOwner()==-1 and not Cities.GetPlotPurchaseCity(site),'Target remained owned')
    assert(site:GetDistrictType()==-1 and site:GetResourceType()==-1)
    assert(site:GetImprovementType()==improvement
        and (improvement<0 or site:IsImprovementPillaged()==improvementPillaged),
        'Releasing the district footprint changed its improvement')
    assert(site:GetTerrainType()==terrain and site:GetFeatureType()==feature and site:GetRiverCrossingCount()==rivers)
    assert(treasury:GetGoldBalance()==gold and supplySignature(profile)==signature)

    -- Both cities may have territory beside the same tile. Releasing it in
    -- a fixture must still satisfy the production buyer's uniqueness check.
    local price=reader.GetPlotPurchaseQuote(playerID,scope.customerCity,scope.customerPlot)
    if not price then
        for _,city in player:GetCities():Members()do
            local quote=reader.GetRawPlotPurchaseQuote(playerID,city:GetID(),scope.customerPlot)
            if quote or city:GetID()==scope.customerCity then
                print('CSC_MILESTONE_CUSTOMER_FRONTIER_QUOTE',city:GetID(),city:GetName(),
                    tostring(quote),Map.GetPlotDistance(city:GetX(),city:GetY(),site:GetX(),site:GetY()))
            end
        end
    end
    assert(price and price>0,'The surveyed customer city is not the unique eligible buyer')
    assert(site:CanHaveDistrict(target.Index,playerID,scope.customerCity),'Released site cannot host the customer')
    local capacity=assert(reader.GetDistrictCapacity(playerID,scope.customerCity))
    print('CSC_MILESTONE_CUSTOMER_FRONTIER_SETUP',playerID,scope.customerCity,
        scope.quarterPlot,scope.customerPlot,price,gold,workingBase,capacity.used,capacity.allowed,signature,
        preparedType,preparedPlot,parkProgress or -1,improvement,tostring(improvementPillaged))
elseif mode=='outcome'then
    local owner=Cities.GetPlotPurchaseCity(site)
    print('CSC_MILESTONE_CUSTOMER_FRONTIER_OUTCOME',Game.GetCurrentGameTurn(),
        site:GetOwner(),owner and owner:GetID() or -1,site:GetDistrictType())
else
    error('Unknown customer frontier fixture phase')
end
