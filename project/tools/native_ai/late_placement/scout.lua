-- Read-only search for a naturally approaching Craftsmanship unlock and an
-- owned Bakers site. The host qualifies the research timing separately.
local quarter = assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER)
local craftsmanship = assert(GameInfo.Civics.CIVIC_CRAFTSMANSHIP).Index
local codeOfLaws = assert(GameInfo.Civics.CIVIC_CODE_OF_LAWS).Index
local cityCenter = assert(GameInfo.Districts.DISTRICT_CITY_CENTER).Index
local tags = {}
for row in GameInfo.TypeTags() do
    if row.Tag == 'CLASS_CSC_BAKERS_BASE' then
        local resource = GameInfo.Resources[row.Type]
        if resource then tags[resource.Index] = true end
    end
end
local function list(rows)
    return '[' .. table.concat(rows, ',') .. ']'
end

local width, height = Map.GetGridSize()
local districtCount = 0
for _ in GameInfo.Districts() do districtCount = districtCount + 1 end
local civics, candidates = {}, {}
for pid = 1, 63 do
    local player = Players[pid]
    if player and player:IsMajor() and player:IsAlive() and not player:IsHuman() then
        local culture = player:GetCulture()
        local current = culture:GetProgressingCivic()
        local known = culture:HasCivic(craftsmanship)
        local code = culture:HasCivic(codeOfLaws)
        local liveEta = -1
        if current == craftsmanship and type(culture.GetTurnsLeftOnCurrentCivic) == 'function' then
            liveEta = culture:GetTurnsLeftOnCurrentCivic()
        end
        civics[#civics + 1] = string.format(
            '{"player":%d,"current":%d,"known":%s,"codeOfLaws":%s,"liveEta":%d}',
            pid, current, tostring(known), tostring(code), liveEta)
        if code and (current == craftsmanship or (CSC_BAKERS_ALLOW_UNLOCKED and known)) then
            for _, city in player:GetCities():Members() do
                local districts = city:GetDistricts()
                local population = city:GetPopulation()
                local slots, exists = 0, false
                for i = 0, districts:GetNumDistricts() - 1 do
                    local district = districts:GetDistrictByIndex(i)
                    if district then
                        local definition = assert(GameInfo.Districts[district:GetType()])
                        if definition.RequiresPopulation then slots = slots + 1 end
                        if district:GetType() == quarter.Index then exists = true end
                    end
                end
                -- Only ordinary population capacity is credited in this scout.
                if not exists and slots < 1 + math.floor((population - 1) / 3) then
                    local adjacent = Map.GetAdjacentPlots(city:GetX(), city:GetY())
                    for _, plot in ipairs(adjacent) do
                        local owner = Cities.GetPlotPurchaseCity(plot)
                        local x, y = plot:GetX(), plot:GetY()
                        if owner and owner:GetOwner() == pid and owner:GetID() == city:GetID()
                            and plot:GetOwner() == pid and plot:GetDistrictType() == -1
                            and plot:GetImprovementType() == -1 and plot:GetResourceType() == -1
                            and PlayersVisibility[pid]:IsRevealed(x, y)
                            and plot:CanHaveDistrict(quarter.Index, pid, city:GetID()) then
                            local base, centers = {}, 0
                            for _, neighbor in ipairs(Map.GetAdjacentPlots(x, y)) do
                                if neighbor:GetOwner() == pid then
                                    if neighbor:GetDistrictType() == cityCenter then centers = centers + 1 end
                                    if tags[neighbor:GetResourceType()] and neighbor:GetDistrictType() == -1
                                        and PlayersVisibility[pid]:IsRevealed(neighbor:GetX(), neighbor:GetY()) then
                                        base[#base + 1] = tostring(neighbor:GetIndex())
                                    end
                                end
                            end
                            if #base > 0 and centers > 0 then
                                candidates[#candidates + 1] = string.format(
                                    '{"player":%d,"city":%d,"plot":%d,"district":%d,"base":%s,"feature":%d,"population":%d,"slots":%d}',
                                    pid, city:GetID(), plot:GetIndex(), quarter.Index, list(base),
                                    plot:GetFeatureType(), population, slots)
                            end
                        end
                    end
                end
            end
        end
    end
end
local speed = GameConfiguration.GetGameSpeedType()
if type(speed) == 'number' then speed = assert(GameInfo.GameSpeeds[speed]).GameSpeedType end
local payload = string.format('{"turn":%d,"speed":"%s","width":%d,"height":%d,'
    .. '"districtCount":%d,"craftsmanship":%d,"civics":%s,"candidates":%s}',
    Game.GetCurrentGameTurn(), speed, width, height, districtCount, craftsmanship, list(civics), list(candidates))
-- Match the existing native receipt framing when the scan exceeds one line.
local chunkSize, sum = 450, 0
local parts = math.ceil(#payload / chunkSize)
for i = 1, #payload do sum = (sum + payload:byte(i)) % 4294967296 end
for part = 1, parts do
    local raw = payload:sub((part - 1) * chunkSize + 1, part * chunkSize)
    local hex = raw:gsub('.', function(c) return string.format('%02x', c:byte()) end)
    print(string.format('CSC_BAKERS_SCOUT_CHUNK={"schema":1,"part":%d,"parts":%d,"bytes":%d,"sum32":%.0f,"encoding":"hex","data":"%s"}',
        part, parts, #payload, sum, hex))
end
