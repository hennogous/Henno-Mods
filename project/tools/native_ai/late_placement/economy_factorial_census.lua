-- Passive stock GameCore observer for the mod comparison. These rows use the
-- same readers and turn-start clock as the existing CSC full-game census.
local seats = __SEATS__
local last = -1
local maximum = 250
local production = assert(GameInfo.Yields.YIELD_PRODUCTION).Index

GameEvents.OnGameTurnStarted.Add(function()
    local turn = Game.GetCurrentGameTurn()
    if turn > maximum or turn % 25 ~= 0 or turn == last then return end
    last = turn
    local ok, reason = pcall(function()
        local count = 0
        local function emit(kind, ...)
            local fields = {...}
            for i, value in ipairs(fields) do fields[i] = tostring(value) end
            print('CSC_ENDPOINT_' .. kind .. '\t' .. table.concat(fields, '\t'))
            count = count + 1
        end
        print('CSC_FULL_RUN_CENSUS_BEGIN', turn)
        for _, id in ipairs(seats) do
            local player = assert(Players[id])
            emit('PLAYER', id, player:IsAlive())
            if player:IsAlive() then
                local treasury = player:GetTreasury()
                emit('TREASURY', id, treasury:GetGoldBalance(), treasury:GetGoldYield(), treasury:GetTotalMaintenance())
                for _, city in player:GetCities():Members() do
                    emit('CITY', id, city:GetID(), city:GetPopulation(), city:GetYield(production),
                        city:GetGrowth():GetFoodSurplus())
                end
            end
        end
        print('CSC_ENDPOINT_END', turn, count)
    end)
    if not ok then print('CSC_FACTOR_ECONOMY_FAILED', turn, tostring(reason)) end
end)
print('CSC_FACTOR_ECONOMY_INSTALLED')
