-- Read exact Storekeeper modifier instances from a UI context. The producer
-- property alone cannot identify the native growth recipient or prove that
-- the growth effect itself is active. Keep both the attach and effect rows
-- so the source and the recipient can be reconciled on a real save.
local tracked = {
    MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER = true,
    MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND = true,
    MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER = true,
    MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND = true,
}
local effects = assert(GameEffects, "Storekeeper runtime probe needs the UI effect API")

local function object(id)
    if id == nil then return "-" end
    return string.format("%s %s %s", tostring(id), effects.GetObjectType(id) or "-",
        (effects.GetObjectString(id) or "-"):gsub("%s+", " "))
end

local function snapshot(turn)
    local found = 0
    for _, id in pairs(assert(effects.GetModifiers())) do
        local definition = effects.GetModifierDefinition(id)
        if definition and tracked[definition.Id] then
            found = found + 1
            local owner = effects.GetModifierOwner(id)
            local subjects = effects.GetModifierSubjects(id) or {}
            print(string.format("CSC_STOREKEEPER_INSTANCE\t%d\t%d\t%s\t%s\t%d\t%s",
                turn, id, definition.Id, tostring(effects.GetModifierActive(id)),
                effects.GetModifierSubjectCount(id), object(owner)))
            for _, subject in pairs(subjects) do
                print(string.format("CSC_STOREKEEPER_SUBJECT\t%d\t%d\t%s", turn, id, object(subject)))
            end
        end
    end
    print(string.format("CSC_STOREKEEPER_END\t%d\t%d", turn, found))
end

if CSC_BAKERS_STOREKEEPER_WATCH then
    assert(not CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED, "Storekeeper observer already installed")
    local lastTurn, fault
    Events.TurnBegin.Add(function()
        if fault or not AutoplayManager.IsActive() then return end
        local turn = Game.GetCurrentGameTurn()
        if turn == lastTurn then return end
        lastTurn = turn
        local ok, message = pcall(snapshot, turn)
        if not ok then
            fault = true
            print(string.format("CSC_STOREKEEPER_FAULT\t%d\t%s", turn, tostring(message)))
        end
    end)
    CSC_BAKERS_STOREKEEPER_WATCH = nil
    CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED = true
    print("CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED")
else
    snapshot(Game.GetCurrentGameTurn())
end
