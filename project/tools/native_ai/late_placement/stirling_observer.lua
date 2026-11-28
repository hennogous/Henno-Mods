-- Diagnostic UI reader. At the shared save and each subsequent TurnBegin,
-- retain district eligibility and all legal private-yield previews. BuildQueue
-- and CityBuild then tell us which submissions and investments followed.
local function inspect()
    local city = assert(CityManager.GetCity(5,65536))
    assert(city:GetName() == 'LOC_CITY_NAME_STIRLING')
    local turn, d = Game.GetCurrentGameTurn(), GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER
    local center = Map.GetPlot(city:GetX(),city:GetY())
    local ds, queue = city:GetDistricts(), city:GetBuildQueue()
    local inventory={}
    for i=0,ds:GetNumDistricts()-1 do
        local district=ds:GetDistrictByIndex(i)
        if district then
            local kind=GameInfo.Districts[district:GetType()].DistrictType
            inventory[#inventory+1]=kind..'/'..tostring(district:IsComplete())..'/'..tostring(district:IsPillaged())
        end
    end
    local can, result = queue:CanProduce(d.Hash,false,true)
    local reasons = result and result[CityCommandResults.FAILURE_REASONS] or {}
    local gate = 'CSC_AI_PAIR_ACTIVE_'..d.DistrictType
    print('CSC_STIRLING_CAPACITY',turn,city:GetPopulation(),ds:GetNumZonedDistrictsRequiringPopulation(),
          ds:GetNumAllowedDistrictsRequiringPopulation(),tostring(can),table.concat(reasons,'|'),
          center:GetProperty(gate..1) or '-',center:GetProperty(gate..2) or '-',table.concat(inventory,','))
    for y=-3,3 do
        for x=-3,3 do
            local p = Map.GetPlotXYWithRangeCheck(city:GetX(),city:GetY(),x,y,3)
            if p and PlayersVisibility[5]:IsRevealed(p:GetX(),p:GetY()) then
                local purchaseCity = Cities.GetPlotPurchaseCity(p)
                local owned = p:GetOwner()==5 and purchaseCity and purchaseCity:GetID()==city:GetID()
                local legal=p:CanHaveDistrict(d.Index,5,city:GetID())
                if p:GetIndex()==870 or ((owned or p:GetOwner()<0) and legal) then
                    print('CSC_STIRLING_PREVIEW',turn,p:GetIndex(),p:GetOwner(),
                          p:GetAdjacencyYield(5,city:GetID(),d.Index,GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index),
                          tostring(legal),tostring(owned==true))
                end
            end
        end
    end
end
inspect()
Events.TurnBegin.Add(inspect)
print('CSC_STIRLING_READY')
