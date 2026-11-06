-- The stock CivicsTree and LaunchBar read these values in a UI context.
-- Query the original AI players directly without changing the local player.
local civic = assert(GameInfo.Civics.CIVIC_CRAFTSMANSHIP).Index
local function number(culture, method)
    if type(culture[method]) ~= 'function' then return -1 end
    local ok, value = pcall(culture[method], culture, civic)
    return ok and type(value) == 'number' and value or -1
end
local rows = {}
for pid = 1, 63 do
    local player = Players[pid]
    if player and player:IsMajor() and player:IsAlive() and not player:IsHuman() then
        local culture = player:GetCulture()
        rows[#rows + 1] = string.format('"%d":{"progress":%.6f,"eta":%d}', pid,
            number(culture, 'GetCulturalProgress'), number(culture, 'GetTurnsToProgressCivic'))
    end
end
print(string.format('CSC_CIVIC_PROGRESS={"turn":%d,"players":{%s}}', Game.GetCurrentGameTurn(), table.concat(rows, ',')))
