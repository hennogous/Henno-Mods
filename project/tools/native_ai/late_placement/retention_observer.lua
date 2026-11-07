-- Read the same physical chain and native Service after every player's turn.
-- The controller checks yields separately at each inactive batch boundary.
assert(CSC_BAKERS_RETENTION == nil, 'Retention observer already installed')
local target = assert(CSC_BAKERS_TARGET)
local granary = assert(GameInfo.Buildings.BUILDING_GRANARY).Index
local mill = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL).Index
local marker = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_STAGE_2_SERVICE).Index
local cattle = assert(GameInfo.Resources.RESOURCE_CATTLE).Index
local pasture = assert(GameInfo.Improvements.IMPROVEMENT_PASTURE).Index
local rows = {}
local changes = {}
local observer = {fault = nil}
CSC_BAKERS_RETENTION = observer

local function reason()
    local city = Players[target.player]:GetCities():FindID(target.city)
    if not city or city:GetOwner() ~= target.player then return 'city' end
    local source = Map.GetPlotByIndex(target.base[1])
    if source:GetOwner() ~= target.player or source:GetResourceType() ~= cattle or source:GetDistrictType() ~= -1 then
        return 'deposit'
    end
    if source:GetImprovementType() ~= pasture or source:IsImprovementPillaged() then return 'pasture' end
    local plot = Map.GetPlotByIndex(target.plot)
    local districts = city:GetDistricts()
    local quarter = nil
    for index = 0, districts:GetNumDistricts() - 1 do
        local district = districts:GetDistrictByIndex(index)
        if district and district:GetX() == plot:GetX() and district:GetY() == plot:GetY() then
            quarter = district
            break
        end
    end
    if not quarter or quarter:GetType() ~= target.district or not quarter:IsComplete() or quarter:IsPillaged() then
        return 'quarter'
    end
    local buildings = city:GetBuildings()
    if not buildings:HasBuilding(mill) or buildings:IsPillaged(mill) or buildings:GetBuildingLocation(mill) ~= target.plot then
        return 'mill'
    end
    if not buildings:HasBuilding(granary) or buildings:IsPillaged(granary) or buildings:GetBuildingLocation(granary) ~= 795 then
        return 'granary'
    end
    if not buildings:HasBuilding(marker) or (city:GetProperty('CSC_BAKERS_STAGE_2_EFFECT_GROWTH') or 0) <= 0 then
        return 'service'
    end
    return 'working'
end

function observer.capture(player)
    if observer.fault then return end
    local ok, state = pcall(reason)
    if not ok then observer.fault = tostring(state); return end
    rows[#rows + 1] = string.format('CSC_RETENTION %d %d %s', Game.GetCurrentGameTurn(), player, state)
end

function observer.export()
    for _, row in ipairs(rows) do print(row) end
    for _, change in ipairs(changes) do print(change) end
    if observer.fault then print('CSC_RETENTION_FAULT ' .. observer.fault) end
    print('CSC_RETENTION_COUNT ' .. tostring(#rows))
    rows = {}
    changes = {}
end

-- A weather event or unit action may remove the improvement between player phases.
local function recordSupplierRemoval(x, y, owner)
    local plot = Map.GetPlot(x, y)
    if plot and plot:GetIndex() == target.base[1] then
        changes[#changes + 1] = string.format('CSC_RETENTION_CHANGE %d %s supplier-removed',
            Game.GetCurrentGameTurn(), tostring(owner))
    end
end

Events.ImprovementRemovedFromMap.Add(recordSupplierRemoval)
Events.PlayerTurnDeactivated.Add(observer.capture)
print('CSC_RETENTION_INSTALLED')
