-- Main CSC tuning entry point for Bakers and Tailors. Read live supply chains,
-- plan site and investment bids, then publish one versioned packet to CE.
-- Each native decision consumes the relevant part of that packet when it runs.
-- Civ still owns candidate legality, selection, queueing and execution.
-- Complete economy mode declares managed Quarter types with a negative default:
-- only profitable +2-or-better sites with Base get positive offers, preferring
-- +3 and better sites, material clusters and compatible terrain-aware customer
-- layouts through bounded spatial preferences. Future layouts earn no current
-- adjacency or transaction income. CE refreshes the
-- shared cache at its consumers and reprices retained new-Quarter requests;
-- nonpositive proposals defer, while existing foundations/repairs stay native.
-- Optional ownership scopes let CE acknowledge an already-fulfilled purchase
-- prerequisite for a native Quarter plan. They never buy land or force a bid.
-- Optional typed declines withhold no-Base Quarter sites and, in the paired
-- planner, already-fulfilled provider types when a ready alternate has a live
-- bid. Each publication replaces the scopes. CE restores the cache after the
-- native site comparison and preserves standing districts and repairs.
-- Game setup owns the advanced planner switch. A save made before the
-- option existed retains its previous default. With the switch off or CE
-- absent, native database rules run independently and no planner subscribes
-- to turns or reads cities. The publisher still checks single-player state.
local advanced=GameConfiguration and GameConfiguration.GetValue('CSC_ADVANCED_AI_PLANNING')
if advanced==false or advanced==0 or advanced=='0' or advanced=='false' then
    print('CSC_AI_MODE native reason=setup')
    return
end
if type(CE_AIDistrictScoresStatus)~='function' then
    print('CSC_AI_MODE native reason=capability')
    return
end
include('CSC_AdjacencyCore')
include('CSC_TradeRouteCore')
include('CSC_TradeRouteFacts')
include('CSC_AI_EconomyModel')
include('CSC_AI_PlanContinuity')
include('CSC_AI_EconomyFacts')
include('CSC_AI_EconomyAdapters')
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
local previousLaterBuildingBids = {}
local reportedOwnershipUnavailable = false

local function wallClock()
    -- Optional read-only CE clock. A missing timer never disables policy or
    -- masquerades as zero overhead; logs mark that measurement unavailable.
    if type(CE_AIMonotonicSeconds)~='function'then return nil end
    local ok,value=pcall(CE_AIMonotonicSeconds)
    if ok and(type(value)=='number'or type(value)=='integer')and value>=0 and value<math.huge then return value end
end
local function elapsedMicros(started,finished)
    if started==nil or finished==nil or finished<started then return -1 end
    return math.floor((finished-started)*1000000+.5)
end

function CSC_AI_ReportNativeProcessing()
    -- Read the current packet before replacement, and once at the final inactive
    -- test boundary. CE accumulates managed refresh microseconds per version;
    -- the offline report keeps the largest observation of each packet. Reading
    -- it never publishes policy, clears counters or changes a native decision.
    if not previousOffers then return end
    local ok,status=pcall(bridge.Status)
    if not ok or type(status)~='string'then return end
    local version=tonumber(status:match('"version":(%d+)'))
    -- A failure between native Commit and Lua tracking must not assign the new
    -- packet's work to the previous turn. Preserve that gap as missing evidence.
    if version~=previousOffers.version then return end
    print(string.format('CSC_AI_NATIVE_PROCESSING turn=%d version=%d managedMicros=%d',
        previousOffers.turn or -1,version,
        tonumber(status:match('"managedMicroseconds":(%d+)'))or -1))
end

local function readReceipt(getter, ...)
    -- Observability is optional on older CE builds. A readback fault must
    -- not prevent the next valid policy packet from being published.
    local ok, result = pcall(getter, ...)
    if ok and type(result) == 'string' then return result,true end
    return '{"readbackError":true}',false
end

-- When the economic planner owns both Quarters it consumes supplier protection
-- directly and supplies its own customer bids. Its managed defaults cover even
-- unpriced plots. The legacy scan then has no live recipient. Run it on failure
-- (or for an older snapshot that still relies on its early customer nominations).
local function addFallbackPlacements(player, chains, protectedPlots, playerUI, economy, playerEntries, turn, id)
    for _, profile in ipairs(placement.StageTwoProfiles()) do
        local ok, industryBids, counts = pcall(CSC_AI_QuarterSiteForecasts, player, profile, chains,
            economy and function(_,plot,p)return economy.Supply(plot,p)end or placement.ReadSuppliers, protectedPlots, playerUI, economy)
        if ok then
            for _, bid in ipairs(industryBids) do playerEntries[#playerEntries + 1] = bid end
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
end

local function reportReceipts(turn, version, status)
    -- Read the last packet before the next commit resets its counters. The log
    -- turn is when Lua reads the receipt. The version identifies the offer
    -- window, and forecast, comparison and score-write counts are distinct.
    local previous = previousOffers
    if not previous or previous.version ~= version then return end
    -- Policy sees the whole bounded native journal, independently of the
    -- top-N diagnostic receipts below. A published score is not intent.
    if CSC_AI_EconomyAdapters and CSC_AI_EconomyAdapters.ObserveNativeChoices then
        local ok,reason=pcall(CSC_AI_EconomyAdapters.ObserveNativeChoices,status,previous.economy or{})
        if not ok then print('CSC_AI_PLAN_INPUT_UNAVAILABLE',turn,tostring(reason))end
    end
    -- The published lists below point to the same entry when one site is
    -- both a frontier Quarter and a planned connection. Each successful
    -- receipt scans the native journal; share that read within this boundary
    -- while keeping each role's diagnostic line and retrying readback faults.
    local districtReceipts={}
    local function districtReceipt(site)
        if districtReceipts[site] then return districtReceipts[site] end
        local value,ok=readReceipt(CE_AIDistrictScoresReceipt,version,site.player,site.city,site.district,site.plot)
        if ok then districtReceipts[site]=value end
        return value
    end
    for _,scope in ipairs(previous.managed or{})do
        local result=readReceipt(CE_AIDistrictScoresManagedReceipt,version,scope.player,scope.district)
        print(string.format('CSC_AI_QUARTER_COVERAGE turn=%d version=%d player=%d district=%d result=%s',
            turn,version,scope.player,scope.district,result))
    end
    for i=1,math.min(#(previous.economy or {}),customerReceiptLimit)do
        local site=previous.economy[i]
        local result=districtReceipt(site)
        print(string.format('CSC_AI_ECONOMY_RECEIPT turn=%d version=%d player=%d city=%d district=%d plot=%d bidQ8=%d result=%s',
            turn,version,site.player,site.city,site.district,site.plot,site.finalQ8,result))
    end
    if #(previous.economy or {})>customerReceiptLimit then
        print(string.format('CSC_AI_ECONOMY_RECEIPTS_OMITTED turn=%d version=%d count=%d',turn,version,#previous.economy-customerReceiptLimit))
    end
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
        local result = districtReceipt(site)
        print(string.format('CSC_AI_FRONTIER_RECEIPT turn=%d version=%d player=%d city=%d district=%d plot=%d result=%s',
            turn, version, site.player, site.city, site.district, site.plot, result))
    end
    if #previous.frontier > frontierReceiptLimit then
        print(string.format('CSC_AI_FRONTIER_RECEIPTS_OMITTED turn=%d version=%d count=%d',
            turn, version, #previous.frontier-frontierReceiptLimit))
    end
    -- Check scarce paid sites first within the existing receipt budget.
    -- Ordinary customer entries can otherwise fill the limit before the
    -- exact plot whose early score has to reach the purchase decision.
    local land = previous.customerLand or {}
    local customerCount = #land + #previous.customers
    for i = 1, math.min(customerCount, customerReceiptLimit) do
        local site = land[i] or previous.customers[i - #land]
        local result = districtReceipt(site)
        print(string.format('CSC_AI_CUSTOMER_RECEIPT turn=%d version=%d player=%d city=%d district=%d plot=%d result=%s',
            turn, version, site.player, site.city, site.district, site.plot, result))
    end
    -- Diagnostic only. Retain a few exact entries in each placement order
    -- after packet trimming. A receipt can say staged without a native read.
    for _,site in ipairs(previous.connections or {})do
        local result=districtReceipt(site)
        print(string.format('CSC_AI_CONNECTION_RECEIPT turn=%d version=%d player=%d city=%d district=%d plot=%d order=%s costQ8=%d result=%s',
            turn,version,site.player,site.city,site.district,site.plot,site.connectionOrder,site.connectionCostQ8,result))
    end
    for i = 1, math.min(#previous.buildings, buildingReceiptLimit) do
        local bid = previous.buildings[i]
        local result = readReceipt(CE_AIBuildingNominationReceipt, version, bid.player, bid.city, bid.building)
        print(string.format('CSC_AI_BUILDING_RECEIPT turn=%d version=%d player=%d city=%d building=%d result=%s',
            turn, version, bid.player, bid.city, bid.building, result))
    end
    if customerCount > customerReceiptLimit or #previous.buildings > buildingReceiptLimit then
        print(string.format('CSC_AI_RECEIPTS_OMITTED turn=%d version=%d customer=%d buildings=%d', turn, version,
            math.max(0, customerCount - customerReceiptLimit),
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

local function publishBefore(a, b)
    -- Wide weak-site coverage must never crowd out supplier protection or
    -- a positive bid for a viable Quarter or its customer.
    if (a.weak == true) ~= (b.weak == true) then return not a.weak end
    local changeA,changeB=a.delta-(a.earlyCostQ8 or 0),b.delta-(b.earlyCostQ8 or 0)
    if changeA~=changeB then return changeA<changeB end
    -- Complete scores always have zero delta. A two-stage offer can also
    -- net to zero while influencing two separate native decisions. At equal
    -- net change put that offer first, then order complete scores by value.
    -- Comparing a mixed tie by city before this step could form a cycle:
    -- changing input order would then change the packet at the capacity cut.
    if (a.finalQ8~=nil)~=(b.finalQ8~=nil) then return a.finalQ8==nil end
    if a.finalQ8~=b.finalQ8 then return a.finalQ8>b.finalQ8 end
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
    -- Read receipts for the previous version before committing replaces its
    -- counters. Both warm starts and reloads begin from CE's live version.
    local status = assert(bridge.Status())
    assert(tonumber(status:match('"ready":(%d+)')) == 1, 'CE district scoring is unavailable')
    assert(tonumber(status:match('"faults":(%d+)')) == 0, 'CE district scoring has faulted')
    local version = assert(tonumber(status:match('"version":(%d+)')))
    CSC_AI_ReportNativeProcessing()
    reportReceipts(turn, version, status)
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
    local managedTypes={}
    -- A CE build may expose district scoring without every optional consumer.
    -- Give the planner zero capacity for unsupported bids and enable only the
    -- protection hooks that report readiness. Harvest shares the Builder sites.
    local builderStatus = bridge.BuilderStatus()
    local protectBuilders = builderStatus and builderStatus:match('"ready":1') and builderStatus:match('"faults":0')
    local builderBidLimit = protectBuilders and bridge.BuilderBidLimit(builderStatus) or 0
    local materialStatus=bridge.MaterialDevelopmentStatus()
    -- Finish eligible sole-supplier jobs by default. The bridge grants
    -- capacity only when CE exposes the finishing-only worker consumer.
    -- Matched controls can set the test override to false for this packet.
    local finishEnabled = CSC_AI_TEST_LAST_SUPPLIER_FINISH ~= false
    local materialTechLimit, materialCivicLimit, materialRequestLimit, materialFinishLimit, materialLoanReady =
        bridge.MaterialDevelopmentLimits(materialStatus, finishEnabled)
    -- The isolated ablation can keep the same packages and retire loan offers.
    local materialLoanEnabled = materialLoanReady and CSC_AI_TEST_WORKER_LOAN ~= false
    local materialResearch,materialRequests,materialServices,materialCommitments,materialWorkers={},{},{},{},{}
    local materialLoans={}
    if materialStatus then
        -- These are earlier-packet native receipts. A compared topic can
        -- lose, and an initialized request still has to win and train.
        print(string.format('CSC_AI_MATERIAL_DEVELOPMENT_RECEIPT turn=%d version=%d %s',turn,version,materialStatus))
    end
    local wonderStatus = bridge.WonderStatus()
    local protectWonders = wonderStatus and wonderStatus:match('"ready":1') and wonderStatus:match('"faults":0')
    local wonderLimit, maxWonderOfferQ8 = bridge.WonderOfferLimit(wonderStatus)
    local wonderOffers = {}
    local harvestStatus = bridge.BuilderHarvestStatus()
    local protectHarvests = protectBuilders and harvestStatus
        and harvestStatus:match('"ready":1') and harvestStatus:match('"faults":0')
    local nominationStatus = bridge.NominationStatus()
    local nominationLimit = bridge.NominationLimit(nominationStatus)
    local queueNomination = bridge.NominationQueueAvailable(nominationStatus)
    -- CE retains exact building receipts for one packet. Read the previous
    -- later-stage offers before publishing replacements. A queue write means
    -- native production compared the option and applied the bid, even when
    -- another item won. Construction remains a separate observation.
    if nominationStatus and type(CE_AIBuildingNominationReceipt)=='function' then
        for _,bid in ipairs(previousLaterBuildingBids) do
            local receipt=readReceipt(CE_AIBuildingNominationReceipt,version,bid.player,bid.city,bid.building)
            if (tonumber(receipt:match('"comparisons":(%d+)')) or 0)>0
                or (tonumber(receipt:match('"queueComparisons":(%d+)')) or 0)>0 then
                print(string.format('CSC_AI_LATER_BUILDING_RECEIPT turn=%d version=%d player=%d city=%d building=%d %s',
                    turn,version,bid.player,bid.city,bid.building,receipt))
            end
        end
    end
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
        local playerWall,playerLuaClock=wallClock(),os.clock()
        local player = Players[id]
        local playerEntries={}
        local economy,playerUI=nil,ui
        if CSC_AI_EconomyAdapters then
            local ok,value,reason=pcall(CSC_AI_EconomyAdapters.Snapshot,player,placement,ui)
            if ok and value then economy=value;playerUI=economy.ui
            else
                -- A missing/failed economic quote must preserve the proven
                -- native/protection paths. It is explicit fallback, not a
                -- successful transaction forecast or a zero-value economy.
                print(string.format('CSC_AI_ECONOMY_UNAVAILABLE turn=%d player=%d reason=%s',turn,id,tostring(ok and reason or value)))
            end
        end
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
        local research=(materialTechLimit>0 or materialCivicLimit>0) and {} or nil
        local deductions, sites, bids, candidates, chains, threatened = placement.MaterialDeductions(player, protectBuilders,
            builderBidLimit, nominationLimit, playerUI.CanProduceItem, repairLimit > 0,economy,research)
        if economy then
            CSC_AI_EconomyAdapters.LaterStageInvestments(economy,research,bids,nominationLimit)
        end
        if economy and research then
            -- Ready Services, producer unlocks and material jobs share the
            -- native final-goal comparator. Merge by topic before applying
            -- CE's four-topic limit and let it choose the prerequisite step.
            CSC_AI_EconomyAdapters.ServiceResearch(economy,research)
        end
        local topics={}
        for _,offer in pairs(research or{})do
            local limit=offer.kind=='tech' and materialTechLimit or materialCivicLimit
            offer.kind=offer.kind=='tech' and 0 or 1
            offer.deltaQ8=math.min(limit,math.floor(offer.value))
            if offer.deltaQ8>0 then topics[#topics+1]=offer end
        end
        table.sort(topics,function(a,b)
            if a.value~=b.value then return a.value>b.value end
            if a.kind~=b.kind then return a.kind<b.kind end
            return a.index<b.index
        end)
        -- Four pending unlocks per empire are ample for the current buyers.
        -- Stable ordering keeps a busy empire from publishing marginal noise.
        for i=1,math.min(4,#topics)do materialResearch[#materialResearch+1]=topics[i] end
        local requests, workers, loan = placement.MaterialBuilderOffers(
            player, sites, playerUI, materialRequestLimit, materialFinishLimit, materialLoanEnabled)
        if loan then materialLoans[#materialLoans+1]=loan end
        for _,offer in ipairs(requests)do materialRequests[#materialRequests+1]=offer end
        for _,offer in ipairs(workers)do materialWorkers[#materialWorkers+1]=offer end
        for _, bid in ipairs(bids) do
            -- Older CE builds still deliver the ordinary building preference.
            -- Only a qualified queue caller can consume the separate value.
            if not queueNomination then bid.queueDelta=nil end
            nominations[#nominations + 1] = bid
        end
        for _, candidate in ipairs(candidates) do repairs[#repairs + 1] = candidate end
        for _, site in ipairs(threatened or {}) do exclusions[#exclusions + 1] = site end
        local protectedPlots = {}
        for _, entry in ipairs(deductions) do
            playerEntries[#playerEntries + 1] = entry
            protectedPlots[entry.plot] = true
        end
        local serviceSample,serviceValue,commitmentSample
        for _, site in ipairs(sites) do
            builderSites[#builderSites + 1] = site
            allowances = allowances + #site.improvements
            -- One representative value per player keeps the Service quote
            -- visible without recording every material job each turn.
            local value=site.ordinaryQ8 and site.jobValueQ8-site.ordinaryQ8
            if value and value>0 and (not serviceValue or value>serviceValue)then
                serviceSample,serviceValue=site,value
            end
            if site.commitment and site.deltaQ8>0 and (not commitmentSample or site.deltaQ8>commitmentSample.deltaQ8
                or site.deltaQ8==commitmentSample.deltaQ8 and site.plot<commitmentSample.plot) then
                commitmentSample=site
            end
        end
        if serviceSample then materialServices[#materialServices+1]=serviceSample end
        if commitmentSample then materialCommitments[#materialCommitments+1]=commitmentSample end
        if protectBuilders then
            for _, site in ipairs(placement.SupplierAcquisitionOffers(player, chains, playerUI, builderBidLimit)) do
                builderSites[#builderSites + 1] = site
                allowances = allowances + #site.improvements
            end
        end
        local deferFallback=economy and type(economy.CustomerOptions)=='function'
        if not deferFallback then
            addFallbackPlacements(player,chains,protectedPlots,playerUI,economy,playerEntries,turn,id)
        end
        if economy then
            -- Budget two full city rings' worth of cells, using the same optional
            -- admission capability as Quarter deferral. The budget per seat
            -- bounds the extra matrix and diagnostic work in a mature empire.
            if declineLimit>0 and CSC_AI_EconomyAdapters.ProspectiveConnectionsEnabled
                and CSC_AI_EconomyAdapters.FulfilledProviderDeclinesEnabled then
                economy.providerDeclineLimit=math.min(72,declineLimit)
            end
            local ok,replacement,counts=pcall(CSC_AI_EconomyAdapters.QuarterBids,economy,placement,protectedPlots,playerEntries,
                previousOffers and previousOffers.economy or{})
            if ok then
                playerEntries=replacement
                if ownershipLimit>0 and economy.planCustomerPurchases then
                    -- A purchased plot can become owned between publications.
                    -- Keep its city's district tree eligible to acknowledge
                    -- ownership until construction, replan or expiry. CE
                    -- verifies the actual retained target and purchasing city.
                    local scopes={}
                    local function include(city,district)
                        local key=city..':'..district
                        if not scopes[key] then
                            scopes[key]=true
                            ownershipScopes[#ownershipScopes+1]={player=id,city=city,district=district}
                        end
                    end
                    for _,bid in ipairs(replacement) do
                        if bid.customerPurchaseGold then
                            include(bid.city,bid.district)
                        end
                    end
                    for _,layout in pairs(economy.nextLayouts or {}) do
                        if layout.invoice>0 then include(layout.partnerCity,layout.partnerDistrict) end
                    end
                end
                if counts.managed then for _,profile in ipairs(placement.StageTwoProfiles())do
                    managedTypes[#managedTypes+1]={player=id,district=profile.district.Index,
                        fallbackQ8=CSC_AI_EconomyAdapters.DeferredQuarterQ8}
                end end
                print(string.format('CSC_AI_ECONOMY_PLAN turn=%d player=%d evaluated=%d final=%d unknown=%d streams=%d omissions=%d quotes=%d minQ8=%d maxQ8=%d buyerBlocked=%d carried=%d',
                    turn,id,counts.evaluated,counts.final,counts.unknown,counts.streams,counts.omissions,
                    economy.QuoteCount(),counts.min or 0,counts.max or 0,counts.buyerBlocked or 0,counts.carried or 0))
                -- Capacity counters are city/Quarter scopes, not tile counts;
                -- ready means a population slot, not full native admission.
                -- Full/unknown are observations, not reasons to suppress a
                -- valuable future bid before in-turn growth/native planning.
                print(string.format('CSC_AI_QUARTER_DEFERRALS turn=%d player=%d quality=%d economics=%d invoice=%d unknown=%d capacityReady=%d capacityFull=%d capacityUnknown=%d',
                    turn,id,counts.qualityDeferred or 0,counts.economicDeferred or 0,counts.invoiceDeferred or 0,counts.unknown or 0,
                    counts.capacityReady or 0,counts.capacityFull or 0,counts.capacityUnknown or 0))
            else
                print(string.format('CSC_AI_ECONOMY_FAILED turn=%d player=%d reason=%s',turn,id,tostring(replacement)))
                if deferFallback then
                    addFallbackPlacements(player,chains,protectedPlots,playerUI,economy,playerEntries,turn,id)
                end
            end
        end
        if wonderLimit>0 and maxWonderOfferQ8>0 and CSC_AI_EconomyAdapters then
            -- QuarterBids has reconciled the confirmed Quarter footprints for
            -- this packet. Keep them and the threatened suppliers available
            -- while weighing the Wonder's separate native placement offer.
            local wonderProtected={}
            for index in pairs(protectedPlots)do wonderProtected[index]=true end
            for _,site in ipairs(sites)do wonderProtected[site.plot]=true end
            for _,site in ipairs(threatened or{})do wonderProtected[site.plot]=true end
            local limit=math.min(128,wonderLimit-#wonderOffers)
            if limit>0 then
                local adapter=CSC_AI_EconomyAdapters
                local consider=adapter.AnchoredConnectionsEnabled or adapter.AnchoredConnectionAuditEnabled
                local query=consider and playerUI and playerUI.CanPlaceWonder
                local anchors=consider and economy and economy.chains or chains
                local intent=consider and economy and economy.intentFootprints
                for _,offer in ipairs(adapter.WonderOffers(player,anchors,wonderProtected,limit,maxWonderOfferQ8,query,intent))do
                    wonderOffers[#wonderOffers+1]=offer
                end
            end
        end
        for _,entry in ipairs(playerEntries)do entries[#entries+1]=entry end
        for _, chain in ipairs(chains or {}) do
            local key = chain.profile.key
            local totals = stageTwo[key] or {placed=0, complete=0, supplied=0, active=0}
            stageTwo[key] = totals
            totals.placed = totals.placed + 1
            if chain.complete then totals.complete = totals.complete + 1 end
            if chain.workingBase then totals.supplied = totals.supplied + 1 end
            if chain.active then totals.active = totals.active + 1 end
        end
        print(string.format('CSC_AI_PLAYER_PROCESSING turn=%d player=%d wallMicros=%d luaClockMicros=%d entries=%d',
            turn,id,elapsedMicros(playerWall,wallClock()),elapsedMicros(playerLuaClock,os.clock()),#playerEntries))
    end
    -- Retain structural protection first and the strongest positive Quarter
    -- investments next. Managed defaults cover omitted pairs: table pressure
    -- defers those investments rather than reviving an untouched native building
    -- premium. Other bounded lists keep their own all-or-nothing contracts.
    if #entries>capacity then
        print(string.format('CSC_AI_ECONOMY_CAPACITY_TRIM turn=%d entries=%d limit=%d managedTypes=%d',turn,#entries,capacity,#managedTypes))
    end
    table.sort(entries, publishBefore)
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
    -- Use only alternate provider bids that survived trimming. Quarter
    -- deferrals keep their existing priority. Each exhausted city/type fits
    -- as a whole or waits for the next publication.
    for _,entry in ipairs(entries) do
        for _,scope in ipairs(entry.providerDeclines or {}) do
            if #scope<=declineLimit-#declines then
                for _,target in ipairs(scope) do declines[#declines+1]=target end
                print(string.format('CSC_AI_PROVIDER_DECLINE_PROPOSED turn=%d version=%d player=%d city=%d district=%d alternative=%d alternativePlot=%d sites=%d',
                    turn,version+1,entry.player,entry.city,scope[1].district,entry.district,entry.plot,#scope))
            else omittedDeclines=omittedDeclines+#scope end
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
        declines,declineLimit,managedTypes,wonderOffers,materialResearch,
        allowances<=capacity and materialRequests or nil, allowances<=capacity and materialWorkers or nil,
        allowances<=capacity and materialLoans or nil)
    assert(accepted, message)
    if allowances<=capacity then
        for _,offer in ipairs(materialLoans)do
            print(string.format('CSC_AI_WORKER_LOAN_OFFER turn=%d version=%d player=%d city=%d plot=%d unit=%d',
                turn,version+1,offer.player,offer.city,offer.plot,offer.unit))
        end
    end
    previousLaterBuildingBids={}
    if #nominations<=capacity then
        for _,bid in ipairs(nominations)do
            if bid.stageReason then
                previousLaterBuildingBids[#previousLaterBuildingBids+1]=bid
                print(string.format('CSC_AI_LATER_BUILDING_OFFER turn=%d version=%d player=%d city=%d building=%d role=%s rawQ8=%d deltaQ8=%d',
                    turn,version+1,bid.player,bid.city,bid.building,bid.stageReason,bid.stageRawQ8,bid.delta))
            end
        end
    end
    for _,offer in ipairs(materialResearch)do
        local plots={};for plot in pairs(offer.jobs)do plots[#plots+1]=plot end;table.sort(plots)
        if #plots>0 then
            print(string.format('CSC_AI_MATERIAL_RESEARCH_OFFER turn=%d version=%d player=%d kind=%d index=%d deltaQ8=%d plots=%s',
                turn,version+1,offer.player,offer.kind,offer.index,offer.deltaQ8,table.concat(plots,',')))
        end
        if offer.serviceQ8 then
            print(string.format('CSC_AI_SERVICE_UNLOCK_OFFER turn=%d version=%d player=%d kind=%d index=%d serviceQ8=%d chains=%d deltaQ8=%d',
                turn,version+1,offer.player,offer.kind,offer.index,offer.serviceQ8,offer.serviceChains,offer.deltaQ8))
        end
        if offer.producerQ8 then
            print(string.format('CSC_AI_LATER_PRODUCER_RESEARCH_OFFER turn=%d version=%d player=%d kind=%d index=%d producerQ8=%d deltaQ8=%d',
                turn,version+1,offer.player,offer.kind,offer.index,offer.producerQ8,offer.deltaQ8))
        end
    end
    if allowances<=capacity then
        -- Only published preparation bids appear here. Join this exact
        -- city/plot/improvement to the native choice and physical work.
        for _,site in ipairs(builderSites)do
            local buyer=site.preparation
            if buyer then
                print(string.format('CSC_AI_MATERIAL_PREPARATION turn=%d version=%d player=%d builderCity=%d buyerCity=%d quarter=%d plot=%d improvement=%d class=%s buyer=%s eta=%d deltaQ8=%d',
                    turn,version+1,site.player,site.city,buyer.city,buyer.quarter,site.plot,site.improvements[1],buyer.kind,buyer.type,buyer.turns,site.deltaQ8))
            end
        end
        for _,site in ipairs(materialCommitments)do
            -- One published example per player and turn. Subsequent native
            -- reservations and work establish whether parallel bidding helped.
            local buyer=site.commitment
            print(string.format('CSC_AI_MATERIAL_COMMITTED_BUYER turn=%d version=%d player=%d builderCity=%d buyerCity=%d quarter=%d plot=%d improvement=%d class=%s buyer=%s eta=%d deltaQ8=%d',
                turn,version+1,site.player,site.city,buyer.city,buyer.quarter,site.plot,site.improvements[1],buyer.kind,buyer.type,buyer.turns,site.deltaQ8))
        end
        for _,site in ipairs(materialServices)do
            print(string.format('CSC_AI_MATERIAL_SERVICE_QUOTE turn=%d player=%d city=%d plot=%d ordinaryQ8=%d serviceQ8=%d improvementDeltaQ8=%d',
                turn,site.player,site.city,site.plot,site.ordinaryQ8,site.jobValueQ8-site.ordinaryQ8,site.deltaQ8))
        end
        for _,offer in ipairs(materialRequests)do
            -- The contingency flag describes the planner's workforce estimate.
            -- The native receipt still establishes whether the request used it.
            print(string.format('CSC_AI_MATERIAL_REQUEST_OFFER turn=%d version=%d player=%d city=%d plot=%d improvement=%d unit=%d deltaQ8=%d contingency=%d',
                turn,version+1,offer.player,offer.city,offer.plot,offer.improvement,offer.unit,offer.deltaQ8,offer.contingency and 1 or 0))
        end
        for _,offer in ipairs(materialWorkers)do
            -- A route was accepted into the packet. CE reports updated tree
            -- order separately, and the game log records the action taken.
            print(string.format('CSC_AI_MATERIAL_WORKER_OFFER turn=%d version=%d player=%d city=%d plot=%d improvement=%d unit=%d',
                turn,version+1,offer.player,offer.city,offer.plot,offer.improvement,offer.unit))
        end
    end
    if CSC_AI_EconomyAdapters and CSC_AI_EconomyAdapters.Committed then
        -- Only retained entries in this accepted packet renew known values.
        -- A failed publish or a one-turn carried quote cannot renew a plan.
        local ok,reason=pcall(CSC_AI_EconomyAdapters.Committed,entries)
        if not ok then print('CSC_AI_PLAN_MEMORY_UNAVAILABLE',turn,tostring(reason))end
    end
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
    local tracked = {turn=turn,version=version + 1, customers={}, customerLand={}, buildings={}, frontier={},declines=declines,economy={},managed=managedTypes,
        connections={}}
    -- Each kind of connection cost gets four readbacks. The adapter also
    -- emits plannedSupply when a deposit needs protection. Start each kind
    -- at zero on first sight so a new policy can share this receipt path.
    local connectionReads={}
    for _, entry in ipairs(entries) do
        local connectionOrder=entry.connectionOrder
        local reads=connectionReads[connectionOrder] or 0
        if connectionOrder and reads<4 and type(CE_AIDistrictScoresReceipt)=='function'then
            tracked.connections[#tracked.connections+1]=entry
            connectionReads[connectionOrder]=reads+1
        end
        if entry.finalQ8~=nil then tracked.economy[#tracked.economy+1]=entry end
        if entry.weak then
            weakSites = weakSites + 1
        elseif entry.customer then
            customerSites = customerSites + 1
            -- Report only paid-site offers retained in the committed packet.
            -- A staged offer still needs a native write and a later purchase.
            if entry.customerPurchaseGold then
                print(string.format('CSC_AI_CUSTOMER_LAND_OFFER turn=%d player=%d city=%d district=%d plot=%d invoice=%d bidQ8=%d version=%d',
                    turn,entry.player,entry.city,entry.district,entry.plot,entry.customerPurchaseGold,entry.delta,version+1))
            end
            if type(CE_AIDistrictScoresReceipt) == 'function' then
                local receiptGroup = entry.customerPurchaseGold and tracked.customerLand or tracked.customers
                receiptGroup[#receiptGroup + 1] = entry
            end
        -- Complete Quarter values deliberately carry delta=0: CE replaces
        -- the native operand with finalQ8. Count/track that published value,
        -- otherwise the legacy additive-only diagnostic reports zero offers
        -- and drops frontier-specific receipts despite successful delivery.
        -- This bookkeeping changes no packet, score, request or game order.
        elseif (entry.finalQ8 or entry.delta) > 0 then
            siteBids = siteBids + 1
            if entry.frontier then
                -- Log only entries retained in the committed packet, not
                -- proposals omitted by its capacity. Publication still is
                -- distinct from CE consumption, native choice and purchase.
                print(string.format('CSC_AI_FRONTIER_OFFER turn=%d version=%d player=%d city=%d district=%d plot=%d adjacency=%.3f quote=%.3f deltaQ8=%d finalQ8=%s startingAdjacency=%.3f startingGold=%.3f grossGoldPaybackTurns=%.3f quarterReadyEstimate=%.3f',
                    turn,version+1,entry.player,entry.city,entry.district,entry.plot,
                    entry.adjacency,entry.purchaseGold,entry.delta,tostring(entry.finalQ8),
                    entry.startingAdjacency or 0,entry.startingGold or 0,
                    entry.startingGoldPaybackTurns or -1,entry.quarterReadyEstimate or -1))
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
        print(string.format('CSC_AI_BAKERS_WONDERS turn=%d version=%d offers=%d previous=%s',
            turn,version+1,#wonderOffers,wonderStatus))
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
    local wallStarted,luaClockStarted=wallClock(),os.clock()
    local ok, published = pcall(refresh, turn)
    if ok and published then
        lastTurn = turn
    elseif not ok then
        bridge.Disable()
        print('CSC_AI_BAKERS_DISTRICTS_FAILED ' .. tostring(published))
    end
    -- Whole policy envelope: facts, model, receipts, all AI players, staging and
    -- continuity writes. Record failed/retried startup attempts too, so analysis
    -- can sum ACTUAL work per turn rather than average only successful packets.
    print(string.format('CSC_AI_PROCESSING turn=%d published=%d ok=%d wallMicros=%d luaClockMicros=%d',
        turn,published==true and 1 or 0,ok and 1 or 0,elapsedMicros(wallStarted,wallClock()),elapsedMicros(luaClockStarted,os.clock())))
end

if bridge.Available() then
    GameEvents.OnGameTurnStarted.Add(onBoundary)
    if Events.LoadScreenClose then Events.LoadScreenClose.Add(onBoundary) end
    onBoundary()
end
