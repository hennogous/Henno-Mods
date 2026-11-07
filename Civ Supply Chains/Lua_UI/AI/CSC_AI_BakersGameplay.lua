-- Publish CSC's Bakers district preferences from one gameplay context.
-- Native scoring still checks eligibility and compares the resulting bids.
include('CSC_AdjacencyCore')
include('CSC_AI_QuarterPlacement')
include('CSC_AI_DistrictBridge')

local bridge = CSC_AI_DistrictBridge
local placement = CSC_AI_QuarterPlacement
local identityPrefix = 'CSC_AI_OriginalHuman_'
local capacity = 4096 -- CE batch contract, across all original AI players.
local lastTurn
local districtCount

local function eligiblePlayers(turn)
    local allowed = {}
    for _, player in ipairs(PlayerManager.GetAliveMajors()) do
        local id = player:GetID()
        local key = identityPrefix .. id
        local originalHuman = Game:GetProperty(key)
        if originalHuman == nil and turn <= 1 then
            originalHuman = player:IsHuman() and 1 or 0
            Game:SetProperty(key, originalHuman)
        end
        if originalHuman == 0 and not player:IsHuman() then allowed[#allowed + 1] = id end
    end
    table.sort(allowed)
    return allowed
end

local function priority(a, b)
    if a.delta ~= b.delta then return a.delta < b.delta end
    if a.player ~= b.player then return a.player < b.player end
    if a.city ~= b.city then return a.city < b.city end
    if a.plot ~= b.plot then return a.plot < b.plot end
    return a.district < b.district
end

local function refresh(turn)
    -- Gameplay does not expose all of the game-mode checks. Wait for the
    -- UI's read-only result before capturing the original player roles.
    local ui = ExposedMembers and ExposedMembers.CSC_Adjacency
    if not ui or type(ui.IsSinglePlayer) ~= 'function' or ui.IsSinglePlayer() ~= true then
        bridge.Disable()
        return false
    end
    local status = assert(bridge.Status())
    assert(tonumber(status:match('"ready":(%d+)')) == 1, 'CE district scoring is unavailable')
    assert(tonumber(status:match('"faults":(%d+)')) == 0, 'CE district scoring has faulted')
    local version = assert(tonumber(status:match('"version":(%d+)')))
    -- The next commit resets CE's per-publication counters.
    local matched = tonumber(status:match('"matched":(%d+)')) or 0
    local changed = tonumber(status:match('"changed":(%d+)')) or 0
    local players = eligiblePlayers(turn)
    if #players == 0 then
        bridge.Disable()
        return false
    end
    if not districtCount then
        CSC_Adjacency.Initialize()
        districtCount = 0
        for district in GameInfo.Districts() do
            districtCount = math.max(districtCount, district.Index + 1)
        end
    end

    local started = os.clock()
    local entries, builderSites = {}, {}
    local builderStatus = bridge.BuilderStatus()
    local protectBuilders = builderStatus and builderStatus:match('"ready":1') and builderStatus:match('"faults":0')
    local wonderStatus = bridge.WonderStatus()
    local protectWonders = wonderStatus and wonderStatus:match('"ready":1') and wonderStatus:match('"faults":0')
    local allowances = 0
    for _, id in ipairs(players) do
        local deductions, sites = placement.BakersMaterialDeductions(Players[id], protectBuilders)
        for _, entry in ipairs(deductions) do
            entries[#entries + 1] = entry
        end
        for _, site in ipairs(sites) do
            builderSites[#builderSites + 1] = site
            allowances = allowances + #site.improvements
        end
    end
    -- Prioritise the supplier relationships most at risk if the map exceeds
    -- the shared table limit. Stable tie-breaks make the packet reproducible.
    table.sort(entries, priority)
    local omitted = math.max(0, #entries - capacity)
    for i = #entries, capacity + 1, -1 do entries[i] = nil end
    local width, height = Map.GetGridSize()
    -- Dropping part of a site's compatibility list can forbid a valid job.
    -- Retire Builder protection for the turn if the full packet cannot fit.
    local accepted, message = bridge.Publish(version + 1, width, height, districtCount, players, entries,
        allowances <= capacity and builderSites or nil, protectWonders)
    assert(accepted, message)
    if builderStatus then
        print(string.format('CSC_AI_BAKERS_BUILDERS turn=%d allowances=%d previous=%s',
            turn, allowances <= capacity and allowances or 0, builderStatus))
    end
    if wonderStatus then
        print(string.format('CSC_AI_BAKERS_WONDERS turn=%d previous=%s', turn, wonderStatus))
    end
    print(string.format('CSC_AI_BAKERS_DISTRICTS turn=%d version=%d players=%d entries=%d omitted=%d previousMatched=%d previousChanged=%d seconds=%.4f',
        turn, version + 1, #players, #entries, omitted, matched, changed, os.clock() - started))
    return true
end

local function onBoundary()
    local turn = Game.GetCurrentGameTurn()
    if lastTurn == turn then return end
    local ok, published = pcall(refresh, turn)
    if ok and published then
        lastTurn = turn
    elseif not ok then
        bridge.Disable()
        print('CSC_AI_BAKERS_DISTRICTS_FAILED ' .. tostring(published))
    end
end

if bridge.Available() then
    GameEvents.OnGameTurnStarted.Add(onBoundary)
    if Events.LoadScreenClose then Events.LoadScreenClose.Add(onBoundary) end
    onBoundary()
end
