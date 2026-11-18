-- The stock Civilopedia loads CivilopediaPage_* files after its chapter helpers.
-- Keep the native district layout and supply just the two CSC chapter bodies.
local chapterTags = { CSCGOODS = "_GOODS_PROVIDER", CSCSALES = "_SALES" }
local getChapterBody = GetChapterBody

local function GetUnavailableDistricts(config)
    local civilization = config:GetCivilizationTypeName()
    local leaderType = config:GetLeaderTypeName()
    local leaderTypes = {}
    while leaderType and not leaderTypes[leaderType] do
        leaderTypes[leaderType] = true
        local leader = GameInfo.Leaders[leaderType]
        leaderType = leader and leader.InheritFrom
    end

    local traits = {}
    for row in GameInfo.CivilizationTraits() do
        if row.CivilizationType == civilization then traits[row.TraitType] = true end
    end
    for row in GameInfo.LeaderTraits() do
        if leaderTypes[row.LeaderType] then traits[row.TraitType] = true end
    end

    local unavailable = {}
    for district in GameInfo.Districts() do
        if district.TraitType and not traits[district.TraitType] then
            unavailable[district.DistrictType] = true
        end
    end
    for row in GameInfo.ExcludedDistricts() do
        if traits[row.TraitType] then unavailable[row.DistrictType] = true end
    end

    -- Check replacement eligibility before hiding bases so a civ exclusion on
    -- the unique can leave its base available. Tech and city limits are ignored.
    local replaced = {}
    for row in GameInfo.DistrictReplaces() do
        if not unavailable[row.CivUniqueDistrictType] then
            replaced[row.ReplacesDistrictType] = true
        end
    end
    for districtType in pairs(replaced) do unavailable[districtType] = true end
    return unavailable
end

function GetChapterBody(sectionId, pageId, chapterId)
    local suffix = chapterTags[chapterId]
    local quarter = suffix and sectionId == "DISTRICTS" and pageId:match("^DISTRICT_CSC_(%w+)_QUARTER$")
    if not quarter then return getChapterBody(sectionId, pageId, chapterId) end

    -- Resolve the player when drawing the page so hotseat sees the current civ.
    -- Spectators have no civilization to filter by and get the reference list.
    local playerId = Game.GetLocalPlayer()
    local config = playerId >= 0 and PlayerConfigurations[playerId]
    local unavailable = config and GetUnavailableDistricts(config) or {}
    local tag = "CLASS_CSC_" .. quarter .. suffix
    local districts = {}
    for row in GameInfo.TypeTags() do
        if row.Tag == tag and not unavailable[row.Type] then
            local district = GameInfo.Districts[row.Type]
            if district and not district.InternalOnly then
                districts[#districts + 1] = { Type = row.Type, Name = Locale.Lookup(district.Name) }
            end
        end
    end
    if #districts == 0 then return nil end

    table.sort(districts, function(a, b)
        local order = Locale.Compare(a.Name, b.Name)
        if order == 0 then return a.Type < b.Type end
        return order == -1
    end)

    local lines = {}
    for i, district in ipairs(districts) do
        lines[i] = "[ICON_BULLET][ICON_" .. district.Type .. "] " .. district.Name
    end
    return { table.concat(lines, "[NEWLINE]") }
end
