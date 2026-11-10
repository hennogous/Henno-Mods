-- Read-only FireTuner diagnostic in CSC_AI_BakersGameplay. Reuse the live
-- planner and the UI build targets without submitting or resetting a CE packet.
-- The outputs identify replay candidates. They do not show a native comparison.
local placement = assert(CSC_AI_QuarterPlacement)
local ui = assert(ExposedMembers.CSC_Adjacency)
assert(type(CSC_AI_QuarterSiteForecasts) == 'function')
assert(type(ui.GetLegalDistrictTargets) == 'function')
CSC_Adjacency.Initialize()

local rowCount = 0
local function emit(kind, ...)
    local fields = {...}
    for i, value in ipairs(fields) do fields[i] = tostring(value) end
    print('CSC_QUARTER_SURVEY_' .. kind .. '\t' .. table.concat(fields, '\t'))
    rowCount = rowCount + 1
end

for _, id in ipairs(CSC_QUARTER_SURVEY_PLAYERS) do
    local player = assert(Players[id])
    if player:IsAlive() and not player:IsHuman() then
        local deductions, _, _, _, chains = placement.MaterialDeductions(player, false, 0, 0, nil, false)
        local protectedPlots = {}
        for _, entry in ipairs(deductions) do protectedPlots[entry.plot] = true end
        for _, profile in ipairs(placement.StageTwoProfiles()) do
            local bids = CSC_AI_QuarterSiteForecasts(player, profile, chains,
                placement.ReadSuppliers, protectedPlots, ui)
            local byCity = {}
            for _, bid in ipairs(bids) do
                if bid.district == profile.district.Index then
                    byCity[bid.city] = byCity[bid.city] or {}
                    byCity[bid.city][bid.plot] = bid
                end
            end
            for _, city in player:GetCities():Members() do
                local cityID = city:GetID()
                local targets = ui.GetLegalDistrictTargets(id, cityID, profile.district.Hash)
                table.sort(targets)
                for _, index in ipairs(targets) do
                    local plot = assert(Map.GetPlotByIndex(index))
                    local ownerCity = Cities.GetPlotPurchaseCity(plot)
                    if plot:GetOwner() == id and ownerCity and ownerCity:GetID() == cityID
                        and plot:GetDistrictType() == -1 and not protectedPlots[index]
                        and PlayersVisibility[id]:IsRevealed(plot:GetX(), plot:GetY())
                        and Map.GetPlotDistance(city:GetX(), city:GetY(), plot:GetX(), plot:GetY()) <= 3
                        and plot:CanHaveDistrict(profile.district.Index, id, cityID) then
                        local bid = (byCity[cityID] or {})[index]
                        local supply = placement.ReadSuppliers(player, plot, profile)
                        emit('SITE', id, cityID, city:GetName(), profile.key, profile.district.Index, index,
                            bid and bid.delta or 0, bid and bid.adjacency or '-', bid and bid.pending or '-',
                            #supply.base, #supply.specialty, plot:GetRiverCrossingCount())
                    end
                end
            end
        end
    end
end
emit('END', Game.GetCurrentGameTurn(), rowCount)
