-- CSC publishes district policy through CE's guarded gameplay bindings.
-- Released CE1.3 lacks this API: availability must be checked before use.
CSC_AI_DistrictBridge={}
local B=CSC_AI_DistrictBridge
local names={'Begin','Allow','Entry','Commit','Disable','Status'}
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
function B.BuilderBidAvailable()
    return type(CE_AIBuilderProtectionBid)=='function'
end
function B.WonderStatus()
    if type(CE_AISupplierWonderProtectionStage)=='function'
        and type(CE_AISupplierWonderProtectionStatus)=='function' then
        return CE_AISupplierWonderProtectionStatus()
    end
end
function B.Publish(version,width,height,districtCount,originalAI,entries,builderSites,protectWonders)
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
        if site.deltaQ8~=nil and (not B.BuilderBidAvailable() or not integer(site.deltaQ8,1,8192)) then
            return reject('Invalid Builder supplier bid')
        end
    end
    if allowanceCount>4096 then return reject('Builder supplier batch too large') end
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
        if protectWonders and allowanceCount>0 then
            assert(CE_AISupplierWonderProtectionStage()==1,'Native Wonder protection rejected')
        end
        assert(CE_AIDistrictScoresCommit()==1,'Native commit rejected')
    end)
    if not ok then return reject(tostring(message)) end
    return true
end
