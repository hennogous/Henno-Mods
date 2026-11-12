-- Translate the Lua planner's packet into CE's guarded gameplay calls. This
-- module validates identities, sizes and units. It leaves valuation to the
-- planner and leaves native decision timing and application to CE.
-- A build without the required district-score API cannot publish a packet.
CSC_AI_DistrictBridge={}
local B=CSC_AI_DistrictBridge
local names={'Begin','Allow','Entry','Commit','Disable','Status'}
-- Q8 represents one native utility point as 256 integers. Lua clamps the
-- optional budgets to both CE's reported capacity and the limits below.
local MAX_BUILDER_BID_Q8=64*256
local MAX_NOMINATION_BID_Q8=512*256
local MAX_REPAIR_CANDIDATES=256
local MAX_OWNERSHIP_SCOPES=4096
local function integer(x,low,high)
    local kind=type(x)
    return (kind=='number' or kind=='integer') and x==math.floor(x) and x>=low and x<=high
end
function B.Available()
    -- Civ's gameplay environment need not expose the standard Lua _G alias.
    local api={Begin=CE_AIDistrictScoresBegin,Allow=CE_AIDistrictScoresAllow,
        Entry=CE_AIDistrictScoresEntry,Commit=CE_AIDistrictScoresCommit,
        Disable=CE_AIDistrictScoresDisable,Status=CE_AIDistrictScoresStatus}
    for _,name in ipairs(names) do
        if type(api[name])~='function' then return false end
    end
    return true
end
function B.Disable()
    if type(CE_AIDistrictScoresDisable)=='function' then return CE_AIDistrictScoresDisable()==1 end
    return false
end
function B.Status()
    if not B.Available() then return nil,'CE district-score capability unavailable' end
    return CE_AIDistrictScoresStatus()
end
function B.BuilderStatus()
    if type(CE_AIBuilderProtectionAllow)=='function' and type(CE_AIBuilderProtectionStatus)=='function' then
        return CE_AIBuilderProtectionStatus()
    end
end
function B.BuilderBidLimit(status)
    if type(CE_AIBuilderProtectionBid)~='function' or type(status)~='string' then return 0 end
    local limit=tonumber(status:match('"maxBidQ8":(%d+)')) or 0
    return math.min(limit,MAX_BUILDER_BID_Q8)
end
function B.BuilderHarvestStatus()
    if type(CE_AIBuilderHarvestProtectionStage)=='function'
        and type(CE_AIBuilderHarvestProtectionStatus)=='function' then
        return CE_AIBuilderHarvestProtectionStatus()
    end
end
function B.WonderStatus()
    if type(CE_AISupplierWonderProtectionStage)=='function'
        and type(CE_AISupplierWonderProtectionStatus)=='function' then
        return CE_AISupplierWonderProtectionStatus()
    end
end
function B.NominationStatus()
    if type(CE_AIBuildingNominationBid)=='function' and type(CE_AIBuildingNominationStatus)=='function' then
        return CE_AIBuildingNominationStatus()
    end
end
function B.NominationLimit(status)
    if type(status)~='string' or not status:match('"ready":1') or not status:match('"faults":0') then return 0 end
    return math.min(tonumber(status:match('"maxBidQ8":(%d+)')) or 0,MAX_NOMINATION_BID_Q8)
end
function B.RepairStatus()
    if type(CE_AIDistrictRepairStage)=='function' and type(CE_AIDistrictRepairStatus)=='function' then
        return CE_AIDistrictRepairStatus()
    end
end
function B.RepairLimit(status)
    if type(status)~='string' or not status:match('"ready":1') or not status:match('"faults":0') then return 0 end
    return math.min(tonumber(status:match('"maxCandidates":(%d+)')) or 0,MAX_REPAIR_CANDIDATES)
end
function B.ExclusionStatus()
    if type(CE_AISupplierExclusionStage)=='function' and type(CE_AISupplierExclusionStatus)=='function' then
        return CE_AISupplierExclusionStatus()
    end
end
function B.OwnershipStatus()
    if type(CE_AIDistrictPurchaseCompletionStage)=='function'
        and type(CE_AIDistrictPurchaseCompletionStatus)=='function'
        and type(CE_AIDistrictPurchaseCompletionReceipt)=='function' then
        return CE_AIDistrictPurchaseCompletionStatus()
    end
end
function B.OwnershipLimit(status)
    if type(status)~='string' or not status:match('"ready":1') or not status:match('"faults":0') then return 0 end
    return math.min(tonumber(status:match('"capacity":(%d+)')) or 0,MAX_OWNERSHIP_SCOPES)
end

function B.DeclineStatus()
    if type(CE_AIDistrictDeclineStage)=='function' and type(CE_AIDistrictDeclineStatus)=='function'
        and type(CE_AIDistrictDeclineReceipt)=='function' then return CE_AIDistrictDeclineStatus() end
end
function B.DeclineLimit(status)
    if type(status)~='string' or tonumber(status:match('"abi":(%d+)'))~=1
        or tonumber(status:match('"ready":(%d+)'))~=1 or tonumber(status:match('"faults":(%d+)'))~=0 then return 0 end
    return math.min(tonumber(status:match('"capacity":(%d+)')) or 0,4096)
end

-- District scores address a player, city, district index and plot index.
-- Building bids address a player, city and building index. The Builder
-- allowlist and bids address a supplier plot and an improvement index.
-- A supplier exclusion is a separate selector input keyed to the whole plot
-- in its owning city. A repair identifies an existing district footprint.
function B.Publish(version,width,height,districtCount,originalAI,entries,builderSites,protectWonders,protectHarvests,
    builderBidLimit,nominations,nominationLimit,repairs,repairLimit,exclusions,ownershipScopes,ownershipLimit,
    declines,declineLimit)
    if not B.Available() then return false,'CE district-score capability unavailable' end
    local function reject(message) B.Disable();return false,message end
    if not(integer(version,1,2147483647) and integer(width,1,256) and integer(height,1,256)
        and integer(districtCount,1,4096) and type(originalAI)=='table' and type(entries)=='table'
        and #originalAI<=64 and #entries<=4096) then return reject('Invalid publication header') end
    local allowed,keys={},{}
    for _,pid in ipairs(originalAI) do
        if not integer(pid,0,63) or allowed[pid] then return reject('Invalid original AI identities') end
        allowed[pid]=true
    end
    -- Validate the entire packet before entering native staging. Original-human
    -- identity capture is caller-owned; current autoplay IsHuman is insufficient.
    for _,e in ipairs(entries) do
        if type(e)~='table' or not(integer(e.player,0,63) and allowed[e.player]
            and integer(e.city,0,2147483647) and integer(e.district,1,districtCount-1)
            and integer(e.plot,0,width*height-1) and integer(e.delta,-262144,1048576)
            and e.delta~=0) then return reject('Invalid district-site entry') end
        local key=e.player..':'..e.city..':'..e.district..':'..e.plot
        if keys[key] then return reject('Duplicate district-site entry') end
        keys[key]=true
    end
    local allowanceCount=0
    for _,site in ipairs(builderSites or {}) do
        if not (integer(site.player,0,63) and allowed[site.player]
            and integer(site.city,0,2147483647) and integer(site.plot,0,width*height-1)
            and type(site.improvements)=='table' and #site.improvements>0) then
            return reject('Invalid Builder supplier site')
        end
        for _,kind in ipairs(site.improvements) do
            if not integer(kind,0,2147483647) then return reject('Invalid supplier improvement') end
            allowanceCount=allowanceCount+1
        end
        if site.deltaQ8~=nil and (not integer(builderBidLimit,1,MAX_BUILDER_BID_Q8)
            or not integer(site.deltaQ8,1,builderBidLimit)) then
            return reject('Invalid Builder supplier bid')
        end
    end
    if allowanceCount>4096 then return reject('Builder supplier batch too large') end
    if nominations and #nominations>4096 then return reject('Building nomination batch too large') end
    for _,e in ipairs(nominations or {}) do
        if not (integer(nominationLimit,1,MAX_NOMINATION_BID_Q8) and integer(e.player,0,63)
            and allowed[e.player] and integer(e.city,0,2147483647) and integer(e.building,0,2147483647)
            and integer(e.delta,1,nominationLimit)) then return reject('Invalid building nomination entry') end
    end
    if repairs and (not integer(repairLimit,1,MAX_REPAIR_CANDIDATES) or #repairs>repairLimit) then
        return reject('Invalid district repair batch')
    end
    local repairCities={}
    for _,e in ipairs(repairs or {}) do
        if not (integer(e.player,0,63) and allowed[e.player] and integer(e.city,0,2147483647)
            and integer(e.district,1,districtCount-1) and integer(e.plot,0,width*height-1)) then
            return reject('Invalid district repair candidate')
        end
        local key=e.player..':'..e.city
        if repairCities[key] then return reject('Duplicate district repair city') end
        repairCities[key]=true
    end
    if exclusions and #exclusions>256 then return reject('Supplier exclusion batch too large') end
    -- These are ownership-prerequisite scopes, not bids or purchase orders.
    -- The native executing tree supplies the actual contract/plot. Missing
    -- optional capability leaves ordinary district guidance available.
    if ownershipScopes and type(ownershipScopes)~='table' then return reject('Invalid ownership scopes') end
    if ownershipScopes and (#ownershipScopes>(ownershipLimit or 0) or #ownershipScopes>MAX_OWNERSHIP_SCOPES
        or (#ownershipScopes>0 and type(CE_AIDistrictPurchaseCompletionStage)~='function')) then
        return reject('Invalid ownership scope capacity')
    end
    local ownershipKeys={}
    for _,e in ipairs(ownershipScopes or {}) do
        if not(integer(e.player,0,63) and allowed[e.player] and integer(e.city,0,2147483647)
            and integer(e.district,1,districtCount-1)) then return reject('Invalid ownership scope') end
        local key=e.player..':'..e.city..':'..e.district
        if ownershipKeys[key] then return reject('Duplicate ownership scope') end
        ownershipKeys[key]=true
    end
    for _,e in ipairs(exclusions or {}) do
        if not (integer(e.player,0,63) and allowed[e.player] and integer(e.city,0,2147483647)
            and integer(e.plot,0,width*height-1)) then return reject('Invalid supplier exclusion') end
    end
    -- A typed decline is selection admission, not a score or an instruction
    -- to cancel a plan. Its lifetime is exactly this complete publication.
    -- Missing optional support is handled by the caller's zero-capacity list;
    -- supplied but malformed/unsupported scopes must reject the whole packet.
    if declines and (type(declines)~='table' or #declines>(declineLimit or 0) or #declines>4096
        or (#declines>0 and type(CE_AIDistrictDeclineStage)~='function')) then
        return reject('Invalid district decline batch')
    end
    local declineKeys={}
    for _,e in ipairs(declines or {}) do
        if not(integer(e.player,0,63) and allowed[e.player] and integer(e.city,0,2147483647)
            and integer(e.district,1,districtCount-1) and integer(e.plot,0,width*height-1)) then
            return reject('Invalid district decline scope')
        end
        local key=e.player..':'..e.city..':'..e.district..':'..e.plot
        if declineKeys[key] then return reject('Duplicate district decline scope') end
        declineKeys[key]=true
    end
    -- Begin opens staging. Nothing here queues an action. Commit publishes
    -- the packet for later native calls. If validation or a native call fails,
    -- Disable clears the policy so an older or incomplete offer cannot linger.
    local ok,message=pcall(function()
        assert(CE_AIDistrictScoresBegin(version,width,height,districtCount)==1,'Native begin rejected')
        for _,pid in ipairs(originalAI) do assert(CE_AIDistrictScoresAllow(pid)==1,'Native identity rejected') end
        for _,e in ipairs(entries) do
            assert(CE_AIDistrictScoresEntry(e.player,e.city,e.district,e.plot,e.delta)==1,'Native entry rejected')
        end
        for _,site in ipairs(builderSites or {}) do
            for _,kind in ipairs(site.improvements) do
                if site.deltaQ8 then
                    assert(CE_AIBuilderProtectionBid(site.player,site.city,site.plot,kind,site.deltaQ8)==1,
                        'Native supplier bid rejected')
                else
                    assert(CE_AIBuilderProtectionAllow(site.player,site.city,site.plot,kind)==1,'Native supplier rejected')
                end
            end
        end
        -- Wonder and harvest protection consume the staged supplier sites.
        -- They have no separate plot list to publish.
        if protectWonders and allowanceCount>0 then
            assert(CE_AISupplierWonderProtectionStage()==1,'Native Wonder protection rejected')
        end
        if protectHarvests and allowanceCount>0 then
            assert(CE_AIBuilderHarvestProtectionStage()==1,'Native harvest protection rejected')
        end
        for _,e in ipairs(nominations or {}) do
            assert(CE_AIBuildingNominationBid(e.player,e.city,e.building,e.delta)==1,'Native building nomination rejected')
        end
        for _,e in ipairs(repairs or {}) do
            assert(CE_AIDistrictRepairStage(e.player,e.city,e.district,e.plot)==1,'Native district repair rejected')
        end
        for _,e in ipairs(exclusions or {}) do
            assert(CE_AISupplierExclusionStage(e.player,e.city,e.plot)==1,'Native supplier exclusion rejected')
        end
        for _,e in ipairs(ownershipScopes or {}) do
            assert(CE_AIDistrictPurchaseCompletionStage(e.player,e.city,e.district)==1,'Native ownership scope rejected')
        end
        for _,e in ipairs(declines or {}) do
            assert(CE_AIDistrictDeclineStage(e.player,e.city,e.district,e.plot)==1,'Native district decline rejected')
        end
        assert(CE_AIDistrictScoresCommit()==1,'Native commit rejected')
    end)
    if not ok then return reject(tostring(message)) end
    return true
end
