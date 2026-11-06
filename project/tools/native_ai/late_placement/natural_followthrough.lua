-- Exact candidate after the single diagnostic score window is frozen.
local target = assert(CSC_BAKERS_TARGET)
local player = assert(Players[target.player])
local city = player:GetCities():FindID(target.city)
local plot = assert(Map.GetPlotByIndex(target.plot))
local civic = assert(GameInfo.Civics.CIVIC_CRAFTSMANSHIP).Index
local founded, complete, otherSite = false, false, -1
local production, population = -1, -1
local buildings, sources = {}, {}
if city then
    population = city:GetPopulation()
    local districts = city:GetDistricts()
    for i = 0, districts:GetNumDistricts() - 1 do
        local district = districts:GetDistrictByIndex(i)
        if district and district:GetType() == target.district then
            if district:GetX() == plot:GetX() and district:GetY() == plot:GetY() then
                founded, complete = true, district:IsComplete()
            else
                otherSite = Map.GetPlot(district:GetX(), district:GetY()):GetIndex()
            end
        end
    end
    local queue = city:GetBuildQueue()
    if type(queue.GetCurrentProductionTypeHash) == 'function' then production = queue:GetCurrentProductionTypeHash() end
    local inventory = city:GetBuildings()
    for _, key in ipairs({'BUILDING_CSC_BAKERS_WATER_MILL', 'BUILDING_CSC_BAKERS_WIND_MILL', 'BUILDING_GRANARY'}) do
        local building = assert(GameInfo.Buildings[key]).Index
        local present = inventory:HasBuilding(building)
        local location = present and inventory:GetBuildingLocation(building) or -1
        if type(location) ~= 'number' then location = -1 end
        buildings[#buildings + 1] = string.format('"%s":{"present":%s,"pillaged":%s,"plot":%d}', key,
            tostring(present), tostring(present and inventory:IsPillaged(building)), location)
    end
end
for _, index in ipairs(target.base) do
    local source = assert(Map.GetPlotByIndex(index))
    sources[#sources + 1] = string.format('{"plot":%d,"owner":%d,"resource":%d,"district":%d,"improvement":%d,"pillaged":%s}',
        index, source:GetOwner(), source:GetResourceType(), source:GetDistrictType(), source:GetImprovementType(),
        tostring(source:IsImprovementPillaged()))
end
print(string.format('CSC_NATURAL_FOLLOWTHROUGH={"turn":%d,"owner":%d,"cityOwner":%d,'
    .. '"district":%d,"founded":%s,"complete":%s,"otherSite":%d,"craftsmanship":%s,"productionHash":%d,'
    .. '"population":%d,"buildings":{%s},"base":[%s]}',
    Game.GetCurrentGameTurn(), plot:GetOwner(), city and city:GetOwner() or -1, plot:GetDistrictType(),
    tostring(founded), tostring(complete), otherSite, tostring(player:GetCulture():HasCivic(civic)), production or -1,
    population, table.concat(buildings, ','), table.concat(sources, ',')))
