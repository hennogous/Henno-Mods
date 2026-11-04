-- Developer parity package. CE owns native code; this context evaluates the
-- unchanged CSC v2 policy. It never creates districts or changes yields/orders.
include('CSC_AdjacencyCore')
include('CSC_AI_AdjacencyScan')
include('CSC_AI_DistrictBridge')
include('CSC_AI_AdjacencyPolicy')

CSC_AI_CEPolicy = {}
local C = CSC_AI_CEPolicy
local B,P = CSC_AI_DistrictBridge,CSC_AI_AdjacencyPolicy
local ready,stopped,lastTurn,version = false,false,nil,0
local failed,stopReason = false,nil
local originalAI = {}
local latestSnapshot,latestPlan = nil,nil
local identityPrefix = 'CSC_CE_POLICY_ORIGINAL_HUMAN_'

-- Receipts are deterministic JSON. Arrays stay arrays even when empty. Full
-- scans are emitted by the shared scanner; these receipts preserve decisions
-- and native counters before the next publication resets a native window.
local function json(v)
    local t = type(v)
    if t == 'nil' then return 'null' end
    if t == 'boolean' or t == 'number' or t == 'integer' then return tostring(v) end
    if t == 'string' then
        return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'
    end
    assert(t == 'table','Unsupported receipt value: '..t)
    local count,array = 0,not(getmetatable(v) and getmetatable(v).__json_object)
    for k in pairs(v) do count=count+1; if type(k)~='number' and type(k)~='integer' then array=false end end
    if count ~= #v then array=false end
    local out = {}
    if array then
        for _,x in ipairs(v) do out[#out+1]=json(x) end
        return '['..table.concat(out,',')..']'
    end
    local keys={};for k in pairs(v) do keys[#keys+1]=k end;table.sort(keys)
    for _,k in ipairs(keys) do out[#out+1]=json(k)..':'..json(v[k]) end
    return '{'..table.concat(out,',')..'}'
end
local receiptEpoch,receiptSequence=nil,0
local function checksum(s)
    local sum=0
    for i=1,#s do sum=(sum+string.byte(s,i))%4294967296 end
    return sum
end
local function emit(kind,payload)
    -- Civ's disk Lua.log truncates individual print lines at2047 bytes even
    -- when the Tuner socket retains the complete reply. Hex encodes raw byte
    -- chunks so UTF-8 boundaries/escaping never inflate a line unpredictably.
    assert(type(kind)=='string' and kind:match('^[A-Z_]+$') and #kind<=32)
    assert(type(payload)=='string')
    receiptSequence=receiptSequence+1
    local marker='CSC_CE_POLICY_'..kind..'='
    if #payload+#marker<=1400 then print(marker..payload);return end
    local parts=math.ceil(#payload/512)
    local sum=checksum(payload)
    for part=1,parts do
        local raw=payload:sub((part-1)*512+1,part*512)
        local data=(raw:gsub('.',function(c) return string.format('%02x',string.byte(c)) end))
        local line='CSC_CE_POLICY_CHUNK={"schema":1,"epoch":'..json(receiptEpoch or 'uninitialized')
            ..',"seq":'..receiptSequence..',"kind":'..json(kind)..',"part":'..part..',"parts":'..parts
            ..',"bytes":'..#payload..',"sum32":'..sum..',"encoding":"hex","data":'..json(data)..'}'
        assert(#line<=1600,'Receipt framing exceeds safe disk line size')
        print(line)
    end
end
local function receipt(kind,value) emit(kind,json(value)) end
local function nativeStatus(reason)
    local raw,message = B.Status()
    if not raw then error(message,0) end
    assert(type(raw)=='string' and raw:sub(1,1)=='{','Malformed CE status')
    if not receiptEpoch then
        local initialGeneration=assert(tonumber(raw:match('"generation":(%d+)')),'Missing native generation')
        receiptEpoch='g'..tostring(initialGeneration)..'-t'..tostring(Game.GetCurrentGameTurn())
    end
    emit('NATIVE','{"reason":'..json(reason)..',"turn":'..tostring(Game.GetCurrentGameTurn())
        ..',"version":'..tostring(version)..',"status":'..raw..'}')
    assert(tonumber(raw:match('"ready":(%d+)'))==1,'CE scoring capability not ready')
    assert(tonumber(raw:match('"faults":(%d+)'))==0,'CE scoring capability faulted')
    return raw
end
local function flushTrace(reason)
    local raw=nativeStatus(reason)
    assert(tonumber(raw:match('"enabled":(%d+)'))==0,'Freeze native policy before flushing traces')
    assert(type(CE_AIDistrictScoresTraceRead)=='function','CE trace paging capability unavailable')
    local generation=assert(tonumber(raw:match('"generation":(%d+)')),'Missing trace generation')
    local count=assert(tonumber(raw:match('"trace_count":(%d+)')),'Missing trace count')
    assert(count>=0 and count<=16384,'Invalid trace count')
    local offset=0
    while offset<count do
        local limit=math.min(64,count-offset)
        local page=CE_AIDistrictScoresTraceRead(offset,limit,generation)
        assert(type(page)=='string' and page:sub(1,1)=='{','Malformed CE trace page')
        assert(not page:match('"stale":true'),'Native trace generation changed while frozen')
        assert(tonumber(page:match('"next":(%d+)'))==offset+limit,'Native trace page did not advance')
        emit('TRACE','{"reason":'..json(reason)..',"turn":'..tostring(Game.GetCurrentGameTurn())
            ..',"generation":'..tostring(generation)..',"page":'..page..'}')
        offset=offset+limit
    end
end
local function stop(reason,isFailure)
    local disabled=B.Disable();stopped=true
    if not failed then stopReason=reason end
    failed=failed or not not isFailure
    if ready then
        local ok,message=pcall(flushTrace,'stop: '..reason)
        if not ok then failed=true;receipt('TRACE_FAILURE',{turn=Game.GetCurrentGameTurn(),reason=tostring(message)}) end
    end
    receipt('STOP',{turn=Game.GetCurrentGameTurn(),version=version,reason=reason,failed=failed,originalFailure=failed and stopReason or nil})
    return disabled
end
local function initialize()
    if ready then return end
    assert(B.Available(),'CE district-score capability unavailable')
    local turn = Game.GetCurrentGameTurn()
    local identities = {}
    -- The gameplay context is loaded before the controller can change roles.
    -- A later load must carry saved identities; inferring them after autoplay
    -- would include the original human in the intervention scope.
    for pid=0,63 do
        local player = Players[pid]
        if player and player:IsAlive() and player:IsMajor() then
            local key = identityPrefix..pid
            local human = Game:GetProperty(key)
            if human == nil then
                assert(turn <= 1,'Missing original identities in a loaded game')
                human=player:IsHuman() and 1 or 0
                Game:SetProperty(key,human)
            end
            assert(human==0 or human==1,'Invalid saved original identity')
            identities[#identities+1]={player=pid,originalHuman=human==1}
            if human==0 then originalAI[#originalAI+1]=pid end
        end
    end
    assert(#identities>0,'Players not initialized')
    CSC_Adjacency.Initialize() -- Read-only database cache, not gameplay writer.
    local raw = nativeStatus('initialize')
    version=assert(tonumber(raw:match('"version":(%d+)')),'Missing native version')
    ready=true
    receipt('IDENTITIES',{turn=turn,originalAI=originalAI,identities=identities,profile=P.Profile})
end
function C.Refresh(eventName)
    if stopped then return false end
    eventName=type(eventName)=='string' and eventName or 'manual'
    local ok,message = pcall(function()
        initialize()
        local turn=Game.GetCurrentGameTurn()
        if turn==lastTurn then return end
        -- Freeze before reading the old window. Already-admitted invocations
        -- recheck the enabled/generation contract and cannot append later writes.
        -- This retires old callbacks; it does not wait for a whole analysis pass.
        assert(B.Disable(),'Native freeze failed')
        flushTrace('before-publication')
        local mode=GameConfiguration.GetValue('CSC_CE_POLICY_MODE')
        assert(mode==nil or mode=='v2' or mode=='off','Invalid CE parity policy mode')
        if mode=='off' then stop('configured off');lastTurn=turn;return end
        if turn>100 then stop('authorized endpoint');lastTurn=turn;return end
        local snapshot=CSC_AI_AdjacencyScan(originalAI)
        assert(snapshot.turn==turn and snapshot.speed=='GAMESPEED_ONLINE','Parity package requires Online speed')
        receipt('SCAN',snapshot) -- Complete autonomous snapshot; historical scanner print may truncate.
        local plan=P.Shortlist(snapshot)
        latestSnapshot,latestPlan=snapshot,plan
        if turn==100 then
            lastTurn=turn
            receipt('PLAN',{event=eventName,turn=turn,version=version,profile=P.Profile,qualified=#plan.qualified,
                selected=plan.selected,penalized=#plan.penalized,entries=plan.entries,published=false,
                cities=#snapshot.cities,sitesEvaluated=snapshot.sitesEvaluated,geometryBuilt=snapshot.geometryBuilt,
                elapsedSeconds=snapshot.elapsedSeconds})
            stop('authorized endpoint');return
        end
        version=version+1
        local accepted,message=B.Publish(version,snapshot.width,snapshot.height,snapshot.districtCount,originalAI,plan.entries)
        assert(accepted,message)
        lastTurn=turn
        receipt('PLAN',{event=eventName,turn=turn,version=version,profile=P.Profile,published=true,qualified=#plan.qualified,selected=plan.selected,
            penalized=#plan.penalized,entries=plan.entries,cities=#snapshot.cities,sitesEvaluated=snapshot.sitesEvaluated,
            geometryBuilt=snapshot.geometryBuilt,elapsedSeconds=snapshot.elapsedSeconds})
        nativeStatus('published')
    end)
    if not ok then stop(tostring(message),true);return false end
    return true
end
function C.Status(reason)
    if stopped or not ready then return end
    local ok,message=pcall(nativeStatus,reason or 'manual')
    if not ok then stop(tostring(message),true) end
end
function C.Disable(reason) return stop(reason or 'explicit disable') end
function C.State() return {ready=ready,stopped=stopped,lastTurn=lastTurn,version=version,originalAI=originalAI,failed=failed,reason=stopReason} end
function C.Snapshot() return latestSnapshot end
function C.Plan() return latestPlan end
function C.Query(label)
    local raw,message=B.Status()
    print('CSC_CE_POLICY_REPORT={"label":'..json(label or 'query')..',"state":'..json(C.State())
        ..',"snapshot":'..json(latestSnapshot)..',"plan":'..json(latestPlan)
        ..',"native":'..(raw or 'null')..',"message":'..json(message)..'}')
end
-- Stable controller surface; Python reads/audits these values but makes no
-- placement decisions. Explicit disable persists until the context reloads.
function CSC_CE_PolicyStatus()
    local raw=B.Status()
    return {turn=Game.GetCurrentGameTurn(),version=version,originalAI=originalAI,
        failed=failed,disabled=stopped,reason=stopReason,snapshot=latestSnapshot,
        plan=latestPlan,native=raw}
end
function CSC_CE_PolicyDisable() return C.Disable('controller disable') end
function CSC_CE_PolicyReport()
    -- Explicit controller queries retain their full socket reply. Disk logs
    -- already carry the complete chunked SCAN/PLAN/NATIVE receipts separately.
    print('CSC_CE_POLICY_STATE='..json(CSC_CE_PolicyStatus()))
end

if GameEvents and GameEvents.OnGameTurnStarted then
    GameEvents.OnGameTurnStarted.Add(function() C.Refresh('OnGameTurnStarted') end)
end
if Events and Events.PlayerTurnActivated then
    Events.PlayerTurnActivated.Add(function() C.Status('PlayerTurnActivated') end)
end
if Events and Events.LoadScreenClose then Events.LoadScreenClose.Add(function() C.Refresh('LoadScreenClose') end) end
C.Refresh('script startup')
