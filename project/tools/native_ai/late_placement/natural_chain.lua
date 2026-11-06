-- Additional Stage 2 facts for the exact Quarter in natural_followthrough.lua.
local target = assert(CSC_BAKERS_TARGET)
local player = assert(Players[target.player])
local city = player:GetCities():FindID(target.city)
local plot = assert(Map.GetPlotByIndex(target.plot))
local techs = player:GetTechs()
local currentTech = type(techs.GetResearchingTech) == 'function' and techs:GetResearchingTech() or -1

local function building(key)
    local row = assert(GameInfo.Buildings[key])
    local tech = row.PrereqTech and GameInfo.Technologies[row.PrereqTech]
    local hasTech = not tech or techs:HasTech(tech.Index)
    local current = tech and currentTech == tech.Index or false
    local nativeLegal = 'null'
    if city then
        local queue = city:GetBuildQueue()
        if type(queue.CanProduce) == 'function' then
            local ok, can = pcall(queue.CanProduce, queue, row.Hash, false, true)
            if ok and type(can) == 'boolean' then nativeLegal = tostring(can) end
        end
    end
    return string.format('"%s":{"tech":"%s","unlocked":%s,"researching":%s,"canProduce":%s}',
        key, row.PrereqTech or '', tostring(hasTech), tostring(current), nativeLegal)
end

local function has(key)
    return city and city:GetBuildings():HasBuilding(assert(GameInfo.Buildings[key]).Index) or false
end

local research = GameInfo.Technologies[currentTech]
local feudalism = player:GetCulture():HasCivic(assert(GameInfo.Civics.CIVIC_FEUDALISM).Index)
print(string.format('CSC_NATURAL_CHAIN={"river":%s,"riverEdges":%d,"hills":%s,"currentTech":"%s",'
    .. '"riverFlag":%s,"inlandFlag":%s,"feudalism":%s,"serviceMarker":%s,"options":{%s,%s,%s}}',
    tostring(plot:IsRiver()), plot:GetRiverCrossingCount(), tostring(plot:IsHills()), research and research.TechnologyType or '',
    tostring(has('BUILDING_CSC_BAKERS_RIVER_ACCESS')), tostring(has('BUILDING_CSC_BAKERS_NO_RIVER_ACCESS')),
    tostring(feudalism), tostring(has('BUILDING_CSC_BAKERS_STAGE_2_SERVICE')),
    building('BUILDING_CSC_BAKERS_WATER_MILL'), building('BUILDING_CSC_BAKERS_WIND_MILL'), building('BUILDING_GRANARY')))
