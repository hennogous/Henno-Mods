-- Diagnostic only. Read the existing Fractal supplier once after loading and
-- again after ordinary AI turns. The replay makes no fixture grants or moves.
local playerID,cityID,quarterPlot,materialPlot=5,131073,2038,2112
local repairQuarterPlot,repairPlot=2114,2188
local player=assert(Players[playerID])
local city=assert(player:GetCities():FindID(cityID))
local plot=assert(Map.GetPlotByIndex(materialPlot))
local quarter=assert(Map.GetPlotByIndex(quarterPlot))
local repair=assert(Map.GetPlotByIndex(repairPlot))
local repairQuarter=assert(Map.GetPlotByIndex(repairQuarterPlot))
local farm=assert(GameInfo.Improvements.IMPROVEMENT_FARM)
local flax=assert(GameInfo.Resources.RESOURCE_CSC_FLAX)
assert(Game.GetCurrentGameTurn()==100 and not AutoplayManager.IsActive())
assert(not player:IsHuman() and plot:GetOwner()==playerID and plot:GetResourceType()==flax.Index)
local district=assert(city:GetDistricts():GetDistrictAtLocation(quarter:GetX(),quarter:GetY()))
assert(district:IsComplete() and district:GetType()==GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index)
assert(plot:GetImprovementType()==-1 and Map.GetPlotDistance(plot:GetX(),plot:GetY(),quarter:GetX(),quarter:GetY())==1)
assert(repair:GetOwner()==playerID and repair:GetResourceType()==flax.Index
    and repair:GetImprovementType()==farm.Index and repair:IsImprovementPillaged()
    and Map.GetPlotDistance(repair:GetX(),repair:GetY(),repairQuarter:GetX(),repairQuarter:GetY())==1)

local function report(site,quarterIndex)
    local working=site:GetOwner()==playerID and site:GetResourceType()==flax.Index
        and site:GetImprovementType()==farm.Index and not site:IsImprovementPillaged()
    return string.format('{"quarter":%d,"plot":%d,"x":%d,"y":%d,"working":%s,"pillaged":%s}',
        quarterIndex,site:GetIndex(),site:GetX(),site:GetY(),tostring(working),tostring(site:IsImprovementPillaged()))
end

function CSC_MaterialFixtureRead(label)
    print(string.format('%s={"turn":%d,"player":%d,"city":%d,"improvement":%d,"plots":[%s,%s]}',
        label,Game.GetCurrentGameTurn(),playerID,cityID,farm.Index,
        report(plot,quarterPlot),report(repair,repairQuarterPlot)))
end
CSC_MaterialFixtureRead('CSC_MATERIAL_FIXTURE_START')
print('CSC_MATERIAL_FIXTURE_SCORE='..CE_AIBuilderProtectionStatus())
