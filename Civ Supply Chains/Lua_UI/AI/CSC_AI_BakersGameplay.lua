-- Main CSC tuning entry point for Bakers and Tailors. Read live supply chains,
-- plan site and investment bids, then publish one versioned packet to CE.
-- Each native decision consumes the relevant part of that packet when it runs.
-- Civ still owns candidate legality, selection, queueing and execution.
-- Optional ownership scopes let CE acknowledge an already-fulfilled purchase
-- prerequisite for a native Quarter plan. They never buy land or force a bid.
-- Optional typed declines withhold proven no-Base district-site pairs from a
-- fresh native comparison. Each turn's live potential replaces the scopes;
-- CE restores score bytes after selection and never cancels retained plans.
include('CSC_AdjacencyCore')
include('CSC_AI_AdjacencyScan')
include('CSC_AI_QuarterPlacement')
include('CSC_AI_DistrictBridge')

local bridge = CSC_AI_DistrictBridge
local placement = CSC_AI_QuarterPlacement
local identityPrefix = 'CSC_AI_OriginalHuman_'
local capacity = 4096 -- CE batch contract, across all original AI players.
local customerReceiptLimit = 16 -- Each customer read scans the native district journal.
local frontierReceiptLimit = 32 -- Bounded exact-pair readback of new purchase-site offers.
local buildingReceiptLimit = 96
local declineReceiptLimit = 64 -- Bounded readback; every native key remains queryable.
local lastTurn
local districtCount
local previousOffers
local previousOwnershipScopes = {}
local reportedOwnershipUnavailable = false

local function readReceipt(getter, ...)
    -- Observability is optional on older CE builds. A readback fault must
    -- not prevent the next valid policy packet from being published.
    local ok, result = pcall(getter, ...)
    if ok and type(result) == 'string' then return result end
    return '{"readbackError":true}'
end

local function reportReceipts(turn, version)
    -- Read the last packet before the next commit resets its counters. The log
    -- turn is when Lua reads the receipt. The version identifies the offer
    -- window, and forecast, comparison and score-write counts are distinct.
    local previous = previousOffers
    if not previous or previous.version ~= version then return end
    for i = 1, math.min(#(previous.declines or {}), declineReceiptLimit) do
        local site = previous.declines[i]
        local result = readReceipt(CE_AIDistrictDeclineReceipt, version, site.player, site.city, site.district, site.plot)
        print(string.format('CSC_AI_DECLINE_RECEIPT turn=%d version=%d player=%d city=%d district=%d plot=%d result=%s',
            turn,version,site.player,site.city,site.district,site.plot,result))
    end
    if #(previous.declines or {}) > declineReceiptLimit then
        print(string.format('CSC_AI_DECLINE_RECEIPTS_OMITTED turn=%d version=%d count=%d',
            turn,version,#previous.declines-declineReceiptLimit))
    end
    for i = 1, math.min(#previous.frontier, frontierReceiptLimit) do
        local site = previous.frontier[i]
        local result = readReceipt(CE_AIDistrictScoresReceipt, version, site.player, site.city, site.district, site.plot)
        print(string.format('CSC_AI_FRONTIER_RECEIPT turn=%d version=%d player=%d city=%d district=%d plot=%d result=%s',
            turn, version, site.player, site.city, site.district, site.plot, result))
    end
    if #previous.frontier > frontierReceiptLimit then
        print(string.format('CSC_AI_FRONTIER_RECEIPTS_OMITTED turn=%d version=%d count=%d',
            turn, version, #previous.frontier-frontierReceiptLimit))
    end
    for i = 1, math.min(#previous.customers, customerReceiptLimit) do
        local site = previous.customers[i]
        local result = readReceipt(CE_AIDistrictScoresReceipt, version, site.player, site.city, site.district, site.plot)
        print(string.format('CSC_AI_CUSTOMER_RECEIPT turn=%d version=%d player=%d city=%d district=%d plot=%d result=%s',
            turn, version, site.player, site.city, site.district, site.plot, result))
    end
    for i = 1, math.min(#previous.buildings, buildingReceiptLimit) do
        local bid = previous.buildings[i]
        local result = readReceipt(CE_AIBuildingNominationReceipt, version, bid.player, bid.city, bid.building)
        print(string.format('CSC_AI_BUILDING_RECEIPT turn=%d version=%d player=%d city=%d building=%d result=%s',
            turn, version, bid.player, bid.city, bid.building, result))
    end
    if #previous.customers > customerReceiptLimit or #previous.buildings > buildingReceiptLimit then
        print(string.format('CSC_AI_RECEIPTS_OMITTED turn=%d version=%d customer=%d buildings=%d', turn, version,
            math.max(0, #previous.customers - customerReceiptLimit),
            math.max(0, #previous.buildings - buildingReceiptLimit)))
    end
end

local function eligiblePlayers(turn)
    -- Persist the original seats before autoplay can temporarily make a human
    -- look like an AI. A later save without a stored identity has no safe basis
    -- for publishing to that seat. Also exclude seats currently controlled by a human.
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
    -- Wide weak-site coverage must never crowd out supplier protection or
    -- a positive bid for a viable Quarter or its customer.
    if (a.weak == true) ~= (b.weak == true) then return not a.weak end
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
    reportReceipts(turn, version)
    -- The next commit resets CE's per-publication counters.
    local matched = tonumber(status:match('"matched":(%d+)')) or 0
    local changed = tonumber(status:match('"changed":(%d+)')) or 0
    local samples = changed > 0 and status:match('"samples":(%b[])')
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
    local entries, builderSites, nominations, repairs, exclusions = {}, {}, {}, {}, {}
    -- A CE build may expose district scoring without every optional consumer.
    -- Give the planner zero capacity for unsupported bids and enable only the
    -- protection hooks that report readiness. Harvest shares the Builder sites.
    local builderStatus = bridge.BuilderStatus()
    local protectBuilders = builderStatus and builderStatus:match('"ready":1') and builderStatus:match('"faults":0')
    local builderBidLimit = protectBuilders and bridge.BuilderBidLimit(builderStatus) or 0
    local wonderStatus = bridge.WonderStatus()
    local protectWonders = wonderStatus and wonderStatus:match('"ready":1') and wonderStatus:match('"faults":0')
    local harvestStatus = bridge.BuilderHarvestStatus()
    local protectHarvests = protectBuilders and harvestStatus
        and harvestStatus:match('"ready":1') and harvestStatus:match('"faults":0')
    local nominationStatus = bridge.NominationStatus()
    local nominationLimit = bridge.NominationLimit(nominationStatus)
    local repairStatus = bridge.RepairStatus()
    local repairLimit = bridge.RepairLimit(repairStatus)
    local exclusionStatus = bridge.ExclusionStatus()
    local exclusionLimit = exclusionStatus and exclusionStatus:match('"ready":1')
        and math.min(256, tonumber(exclusionStatus:match('"capacity":(%d+)')) or 0) or 0
    local ownershipStatus = bridge.OwnershipStatus()
    local ownershipLimit = bridge.OwnershipLimit(ownershipStatus)
    local declineStatus = bridge.DeclineStatus()
    local declineLimit = bridge.DeclineLimit(declineStatus)
    local ownershipScopes = {}
    -- Read exact scopes only after a reported acknowledgement. This avoids
    -- scanning every native scope merely to report zero each turn. The last
    -- publication is retained locally until its receipts have been consumed.
    if ownershipStatus and (tonumber(ownershipStatus:match('"acknowledged":(%d+)')) or 0)>0 then
        for _,scope in ipairs(previousOwnershipScopes) do
            local receipt=readReceipt(CE_AIDistrictPurchaseCompletionReceipt,version,scope.player,scope.city,scope.district)
            if (tonumber(receipt:match('"acknowledged":(%d+)')) or 0)>0 then
                print(string.format('CSC_AI_OWNERSHIP_RECEIPT turn=%d version=%d player=%d city=%d district=%d %s',
                    turn,version,scope.player,scope.city,scope.district,receipt))
            end
        end
    end
    local allowances, stageTwo = 0, {}
    for _, id in ipairs(players) do
        local player = Players[id]
        if ownershipLimit>0 then
            -- O(cities * supported Quarters), no tile scan and no cached game
            -- pointers. The native executing tree supplies the chosen site.
            -- A founded Quarter no longer needs a purchase prerequisite scope.
            for _,city in player:GetCities():Members() do
                for _,profile in ipairs(placement.StageTwoProfiles()) do
                    if not city:GetDistricts():HasDistrict(profile.district.Index) then
                        ownershipScopes[#ownershipScopes+1]={player=id,city=city:GetID(),district=profile.district.Index}
                    end
                end
            end
        end
        -- Take one chain snapshot per player. Supply protection marks plots
        -- before placement plans run, so a customer bid cannot promote a site
        -- already flagged by this player's material deductions.
        local deductions, sites, bids, candidates, chains, threatened = placement.MaterialDeductions(player, protectBuilders,
            builderBidLimit, nominationLimit, ui.CanProduceItem, repairLimit > 0)
        for _, bid in ipairs(bids) do nominations[#nominations + 1] = bid end
        for _, candidate in ipairs(candidates) do repairs[#repairs + 1] = candidate end
        for _, site in ipairs(threatened or {}) do exclusions[#exclusions + 1] = site end
        local protectedPlots = {}
        for _, entry in ipairs(deductions) do
            entries[#entries + 1] = entry
            protectedPlots[entry.plot] = true
        end
        for _, site in ipairs(sites) do
            builderSites[#builderSites + 1] = site
            allowances = allowances + #site.improvements
        end
        if protectBuilders then
            for _, site in ipairs(placement.SupplierAcquisitionOffers(player, chains, ui, builderBidLimit)) do
                builderSites[#builderSites + 1] = site
                allowances = allowances + #site.improvements
            end
        end
        -- An unsupported placement read must leave the working supplier
        -- protection active. A fresh native site score is still required.
        for _, profile in ipairs(placement.StageTwoProfiles()) do
            local ok, industryBids, counts = pcall(CSC_AI_QuarterSiteForecasts, player, profile, chains,
                placement.ReadSuppliers, protectedPlots, ui)
            if ok then
                for _, bid in ipairs(industryBids) do entries[#entries + 1] = bid end
                -- This is CSC's assessment of the current legal targets.
                -- The engine may still pick a penalized or unassisted site.
                if counts and counts.legal > 0 then
                    print(string.format('CSC_AI_QUARTER_PLAN turn=%d player=%d key=%s legal=%d noBase=%d coversMaterial=%d noHost=%d bothPending=%d deferCities=%d offers=%d strong=%d lowAdjacency=%d',
                        turn, id, profile.key, counts.legal, counts.noBase, counts.coversMaterial,
                        counts.noHost, counts.bothPending, counts.deferCities, counts.offered, counts.strong, counts.lowAdjacency or 0))
                end
                if counts and (counts.frontierObserved or 0) > 0 then
                    -- These are proposed deductions on map candidates. The
                    -- CE consumer still validates the native frontier row.
                    print(string.format('CSC_AI_FRONTIER_QUARTER_PLAN turn=%d player=%d key=%s observed=%d bids=%d uncertain=%d',
                        turn, id, profile.key, counts.frontierObserved, counts.frontierBids, counts.frontierUncertain))
                end
            else
                print(string.format('CSC_AI_INDUSTRY_PLACEMENT_FAILED turn=%d player=%d key=%s %s',
                    turn, id, profile.key, tostring(industryBids)))
            end
        end
        for _, chain in ipairs(chains or {}) do
            local key = chain.profile.key
            local totals = stageTwo[key] or {placed=0, complete=0, supplied=0, active=0}
            stageTwo[key] = totals
            totals.placed = totals.placed + 1
            if chain.complete then totals.complete = totals.complete + 1 end
            if chain.workingBase then totals.supplied = totals.supplied + 1 end
            if chain.active then totals.active = totals.active + 1 end
        end
    end
    -- Prioritise the supplier relationships most at risk if the map exceeds
    -- the shared table limit. Stable tie-breaks make the packet reproducible.
    table.sort(entries, priority)
    local omitted = math.max(0, #entries - capacity)
    for i = #entries, capacity + 1, -1 do entries[i] = nil end
    -- Only retained, validated planner entries may request admission control.
    -- No-Base evidence is per-site; a neutral/potential site stays eligible.
    -- Stable packet ordering bounds scopes without a second map scan. Missing
    -- capability or overflow leaves the ordinary finite deductions in force.
    local declines, omittedDeclines = {}, 0
    for _,entry in ipairs(entries) do
        if entry.declineNoBase then
            if #declines < declineLimit then declines[#declines+1]=entry
            else omittedDeclines=omittedDeclines+1 end
        end
    end
    local width, height = Map.GetGridSize()
    -- Dropping part of a site's improvement allowlist can forbid a valid job.
    -- Send Builder, building and repair lists only when each fits as a whole.
    -- Plot exclusions can be trimmed independently, so keep the greatest risks.
    local publishRepairs = #repairs > 0 and #repairs <= repairLimit
    table.sort(exclusions, function(a, b)
        if a.cost ~= b.cost then return a.cost > b.cost end
        if a.player ~= b.player then return a.player < b.player end
        return a.plot < b.plot
    end)
    local omittedExclusions = math.max(0, #exclusions - exclusionLimit)
    for i = #exclusions, exclusionLimit + 1, -1 do exclusions[i] = nil end
    local accepted, message = bridge.Publish(version + 1, width, height, districtCount, players, entries,
        allowances <= capacity and builderSites or nil, protectWonders, protectHarvests, builderBidLimit,
        #nominations <= capacity and nominations or nil, nominationLimit, publishRepairs and repairs or nil, repairLimit,
        exclusions, ownershipLimit>0 and #ownershipScopes<=ownershipLimit and ownershipScopes or nil, ownershipLimit,
        declines,declineLimit)
    assert(accepted, message)
    print(string.format('CSC_AI_DECLINES turn=%d version=%d scopes=%d omitted=%d previous=%s',
        turn,version+1,#declines,omittedDeclines,declineStatus or 'unavailable; finite guidance retained'))
    -- These are committed improvement proposals, not buying or assignment
    -- receipts. Native candidate, payment and actual improvement are separate.
    if allowances <= capacity then
        for _, site in ipairs(builderSites) do
            if site.acquisition then
                print(string.format('CSC_AI_SUPPLIER_ACQUISITION_OFFER turn=%d version=%d player=%d city=%d quarter=%d plot=%d quote=%s deltaQ8=%d improvements=%s',
                    turn,version+1,site.player,site.city,site.quarter,site.plot,tostring(site.purchaseGold),
                    site.deltaQ8 or 0,table.concat(site.improvements,',')))
            end
        end
    end
    previousOwnershipScopes = #ownershipScopes<=ownershipLimit and ownershipScopes or {}
    if ownershipStatus then
        print(string.format('CSC_AI_OWNERSHIP_COMPLETION turn=%d scopes=%d omitted=%d previous=%s',turn,
            #previousOwnershipScopes,#ownershipScopes-#previousOwnershipScopes,ownershipStatus))
    elseif not reportedOwnershipUnavailable then
        print('CSC_AI_OWNERSHIP_COMPLETION capability unavailable; ordinary score guidance remains available')
        reportedOwnershipUnavailable=true
    end
    -- Chain totals describe the snapshot used to plan. The active column is
    -- a source-property read, while the native receipts describe score delivery.
    for key, totals in pairs(stageTwo) do
        print(string.format('CSC_AI_STAGE_TWO turn=%d key=%s placed=%d complete=%d supplied=%d active=%d',
            turn, key, totals.placed, totals.complete, totals.supplied, totals.active))
    end
    if samples and samples ~= '[]' then
        -- Civ clips long Lua log lines. CE sends a flat array of small
        -- numeric rows, so split it only at complete row boundaries.
        local chunk = {}
        local prefix = string.format('CSC_AI_BAKERS_DISTRICT_SAMPLES turn=%d previousVersion=%d samples=',
            turn, version)
        for row in samples:sub(2, -2):gmatch('%b[]') do
            chunk[#chunk + 1] = row
            if #chunk == 16 then
                print(prefix .. '[' .. table.concat(chunk, ',') .. ']')
                chunk = {}
            end
        end
        if #chunk > 0 then print(prefix .. '[' .. table.concat(chunk, ',') .. ']') end
    end
    local siteBids, weakSites, customerSites = 0, 0, 0
    -- Save the exact published identities for readback on the next boundary.
    -- Receipt caps limit logging work. They do not limit what CE receives.
    local tracked = {version=version + 1, customers={}, buildings={}, frontier={},declines=declines}
    for _, entry in ipairs(entries) do
        if entry.weak then
            weakSites = weakSites + 1
        elseif entry.customer then
            customerSites = customerSites + 1
            if type(CE_AIDistrictScoresReceipt) == 'function' then
                tracked.customers[#tracked.customers + 1] = entry
            end
        elseif entry.delta > 0 then
            siteBids = siteBids + 1
            if entry.frontier then
                -- Log only entries retained in the committed packet, not
                -- proposals omitted by its capacity. Publication still is
                -- distinct from CE consumption, native choice and purchase.
                print(string.format('CSC_AI_FRONTIER_OFFER turn=%d version=%d player=%d city=%d district=%d plot=%d adjacency=%.3f quote=%.3f deltaQ8=%d',
                    turn,version+1,entry.player,entry.city,entry.district,entry.plot,
                    entry.adjacency,entry.purchaseGold,entry.delta))
                if type(CE_AIDistrictScoresReceipt) == 'function' then
                    tracked.frontier[#tracked.frontier + 1] = entry
                end
            end
        end
    end
    if type(CE_AIBuildingNominationReceipt) == 'function' and #nominations <= capacity then
        tracked.buildings = nominations
    end
    previousOffers = tracked
    print(string.format('CSC_AI_BAKERS_PLACEMENT turn=%d bids=%d weak=%d customer=%d',
        turn, siteBids, weakSites, customerSites))
    if builderStatus then
        print(string.format('CSC_AI_BAKERS_BUILDERS turn=%d allowances=%d previous=%s',
            turn, allowances <= capacity and allowances or 0, builderStatus))
    end
    if wonderStatus then
        print(string.format('CSC_AI_BAKERS_WONDERS turn=%d previous=%s', turn, wonderStatus))
    end
    if harvestStatus then
        print(string.format('CSC_AI_BAKERS_HARVEST turn=%d previous=%s', turn, harvestStatus))
    end
    if nominationStatus then
        local publishedCount = #nominations <= capacity and #nominations or 0
        local preview = {}
        for i = 1, math.min(publishedCount, 8) do
            local bid = nominations[i]
            preview[i] = string.format('[%d,%d,%d,%d]', bid.player, bid.city, bid.building, bid.delta)
        end
        print(string.format('CSC_AI_BAKERS_NOMINATIONS turn=%d bids=%d preview=[%s] previous=%s',
            turn, publishedCount, table.concat(preview, ','), nominationStatus))
    end
    if repairStatus then
        print(string.format('CSC_AI_BAKERS_REPAIRS turn=%d candidates=%d previous=%s',
            turn, publishRepairs and #repairs or 0, repairStatus))
    end
    if exclusionStatus then
        print(string.format('CSC_AI_SUPPLIER_EXCLUSIONS turn=%d sites=%d omitted=%d previous=%s',
            turn, #exclusions, omittedExclusions, exclusionStatus))
    end
    print(string.format('CSC_AI_BAKERS_DISTRICTS turn=%d version=%d players=%d entries=%d omitted=%d previousMatched=%d previousChanged=%d seconds=%.4f',
        turn, version + 1, #players, #entries, omitted, matched, changed, os.clock() - started))
    return true
end

local function onBoundary()
    -- Startup and the load-screen event can fire on the same turn. Record the
    -- turn after a successful publication so a later event can retry when the
    -- UI read bridge was unavailable during startup.
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
