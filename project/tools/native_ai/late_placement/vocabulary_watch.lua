-- Read-only stock UI observer. Join a gameplay review to the actual private
-- preview and the city's production eligibility on the next UI turn boundary.
-- The rival is the strongest modeled change, which may differ from the
-- strongest ordinary preview. CityBuild and BuildQueue record later decisions.
local quarters,seen={},{}
for row in GameInfo.CSC_QuarterMaterialAdjacencyConfig() do
    local district=GameInfo.Districts['DISTRICT_CSC_'..row.QuarterKey..'_QUARTER']
    if district then quarters[district.Index]=district end
end
local yield=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index
Events.TurnBegin.Add(function()
    local t=Game.GetCurrentGameTurn()
    for pid=1,5 do
        for _,city in Players[pid]:GetCities():Members() do
            local p=Map.GetPlot(city:GetX(),city:GetY())
            for ix,d in pairs(quarters) do
                local prefix='CSC_AI_VOC_'..d.DistrictType
                local stamp=p:GetProperty(prefix..'_REVIEW')
                local key=pid..'/'..city:GetID()..'/'..ix
                if stamp and seen[key]~=stamp then
                    seen[key]=stamp
                    local target=p:GetProperty(prefix..'_TARGET')
                    local rival=p:GetProperty(prefix..'_RIVAL')
                    local function preview(i)
                        if not i or i<0 then return '-' end
                        return Map.GetPlotByIndex(i):GetAdjacencyYield(pid,city:GetID(),ix,yield)
                    end
                    local ds=city:GetDistricts()
                    local can=city:GetBuildQueue():CanProduce(d.Hash,false,true)
                    print('CSC_VOCAB_NATIVE',t,stamp,pid,city:GetID(),city:GetName(),d.DistrictType,
                          target,preview(target),rival,preview(rival),tostring(can),
                          ds:GetNumZonedDistrictsRequiringPopulation(),ds:GetNumAllowedDistrictsRequiringPopulation())
                end
            end
        end
    end
end)
print('CSC_VOCAB_WATCH_READY')
