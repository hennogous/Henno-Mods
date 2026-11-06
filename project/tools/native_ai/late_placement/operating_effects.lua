-- Read the UI cache for building legality and actual yields on the target.
-- The gameplay census independently verifies supplier, owner and placement.
local target = assert(CSC_BAKERS_TARGET)
local city = assert(Players[target.player]:GetCities():FindID(target.city))
local buildings = city:GetBuildings()
local queue = city:GetBuildQueue()
local function number(value)
    return type(value) == 'number' and tostring(value) or 'null'
end
local function building(key)
    local row = assert(GameInfo.Buildings[key])
    local present = buildings:HasBuilding(row.Index)
    local food, production, gold, legal = nil, nil, nil, 'null'
    if present and type(city.GetBuildingYield) == 'function' then
        food = city:GetBuildingYield(row.Index, 'YIELD_FOOD')
        production = city:GetBuildingYield(row.Index, 'YIELD_PRODUCTION')
        gold = city:GetBuildingYield(row.Index, 'YIELD_GOLD')
    end
    if not present and type(queue.CanProduce) == 'function' then
        local ok, value = pcall(queue.CanProduce, queue, row.Hash, false, true)
        if ok and type(value) == 'boolean' then legal = tostring(value) end
    end
    return string.format('"%s":{"canProduce":%s,"food":%s,"production":%s,"gold":%s}',
        key, legal, number(food), number(production), number(gold))
end
local granaryFood = 0
for row in GameInfo.Building_YieldChanges() do
    if row.BuildingType == 'BUILDING_GRANARY' and row.YieldType == 'YIELD_FOOD' then
        granaryFood = granaryFood + row.YieldChange
    end
end
local service = type(city.GetProperty) == 'function' and city:GetProperty('CSC_BAKERS_STAGE_2_EFFECT_GROWTH') or nil
print(string.format('CSC_BAKERS_EFFECTS={"turn":%d,"granaryBaseFood":%s,"serviceGrowthProperty":%s,'
    .. '"buildings":{%s,%s,%s}}', Game.GetCurrentGameTurn(), number(granaryFood), number(service),
    building('BUILDING_GRANARY'), building('BUILDING_CSC_BAKERS_WATER_MILL'), building('BUILDING_CSC_BAKERS_WIND_MILL')))
