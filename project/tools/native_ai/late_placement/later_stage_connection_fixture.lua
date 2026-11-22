-- DIAGNOSTIC ONLY. Use the archived Continents layout and open one slot in
-- each copy so the existing Commercial Hub can anchor a legal Tailors bid.
-- The scout verifies the gap without creating any district or issuing a bid.
local pid,cityID,quarterPlot,customerPlot=4,196610,2581,2506
local player=assert(Players[pid])
local city=assert(player:GetCities():FindID(cityID))
local plot=assert(Map.GetPlotByIndex(quarterPlot))
local hub=assert(Map.GetPlotByIndex(customerPlot))
local quarter=assert(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER)
if mode=='setup'then
    assert(Game.GetCurrentGameTurn()==150 and city:GetPopulation()==11)
    assert(plot:GetOwner()==pid and Cities.GetPlotPurchaseCity(plot):GetID()==cityID and plot:GetDistrictType()==-1)
    assert(hub:GetOwner()==pid and hub:GetDistrictType()==GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index)
    assert(Map.GetPlotDistance(plot:GetX(),plot:GetY(),hub:GetX(),hub:GetY())==1)
    city:ChangePopulation(2)
    assert(city:GetPopulation()==13)
    print('CSC_MILESTONE_CONNECTION_SETUP',pid,cityID,quarterPlot,customerPlot,13)
elseif mode=='legal'then
    local district=assert(CityManager.GetDistrictAt(hub:GetX(),hub:GetY()))
    assert(district:IsComplete() and not district:IsPillaged())
    local legal=assert(ExposedMembers.CSC_Adjacency.GetLegalDistrictTargets(pid,cityID,quarter.Hash))
    for _,index in ipairs(legal)do
        if index==quarterPlot then
            print('CSC_MILESTONE_CONNECTION_LEGAL',pid,cityID,quarterPlot,#legal)
            return
        end
    end
    error('Linked Tailors plot unavailable after adding one capacity slot')
elseif mode=='outcome'then
    print('CSC_MILESTONE_CONNECTION_OUTCOME',Game.GetCurrentGameTurn(),plot:GetDistrictType(),hub:GetDistrictType())
else error('Unknown connection fixture mode')end
