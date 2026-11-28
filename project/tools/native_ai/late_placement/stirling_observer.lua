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
    -- The UI district collection exposes HasDistrict. Indexed enumeration of
    -- individual district objects belongs to the gameplay API.
    for definition in GameInfo.Districts() do
        if ds:HasDistrict(definition.Index) then inventory[#inventory+1]=definition.DistrictType end
    end
    local can, result = queue:CanProduce(d.Hash,false,true)
    local reasons = result and result[CityCommandResults.FAILURE_REASONS] or {}
    local gate = 'CSC_AI_PAIR_ACTIVE_'..d.DistrictType
    -- Plot 796 is the original Flax next to 870. A change in its ownership,
    -- resource or occupation can end the supplied layout during a long bid.
    local flax=Map.GetPlotByIndex(796)
    print('CSC_STIRLING_SUPPLIER',turn,flax:GetOwner(),flax:GetResourceType(),
          flax:GetDistrictType(),flax:GetImprovementType())
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
