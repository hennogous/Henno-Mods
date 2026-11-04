-- Package-owned delivery smoke test. No external code injection or console
-- installation is needed. Default mode observes only; the controller may set
-- CSC_BRIDGE_SMOKE_DELTA=256 BEFORE hosting to request a tiny diagnostic input.
-- This does not install the +4 policy or rank CSC sites.
local version=0
local originalAI={}
local ready=false
local function status(label)
    if type(CSCBridgeStatus)=='function' then
        print('CSC_WORKSHOP_BRIDGE '..label..' '..CSCBridgeStatus())
    else print('CSC_WORKSHOP_BRIDGE '..label..' NATIVE_API_MISSING') end
end
local function initialize()
    if ready then return end
    assert(type(CSCBridgeBegin)=='function','Native Workshop bridge was not loaded')
    -- Persist the human exclusion before autoplay changes runtime roles.
    for pid=0,63 do
        local p=Players[pid]
        if p and p:IsAlive() and p:IsMajor() then
            local key='CSC_BRIDGE_ORIGINAL_HUMAN_'..pid
            local human=Game:GetProperty(key)
            if human==nil then human=p:IsHuman() and 1 or 0;Game:SetProperty(key,human) end
            if human==0 then originalAI[#originalAI+1]=pid end
        end
    end
    ready=true
    status('startup')
end
local function publish()
    initialize()
    local delta=GameConfiguration.GetValue('CSC_BRIDGE_SMOKE_DELTA') or 0
    assert(delta==0 or delta==256,'Delivery prototype allows only observation or +1 utility')
    if delta==0 then CSCBridgeDisable();status('observe');return end
    local d=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER
    if not d then CSCBridgeDisable();status('no-CSC');return end
    local w,h=Map.GetGridSize()
    local max=-1;for row in GameInfo.Districts() do max=math.max(max,row.Index) end
    version=version+1
    assert(CSCBridgeBegin(version,w,h,max+1)==1)
    local count=0
    for _,pid in ipairs(originalAI) do
        assert(CSCBridgeAllow(pid)==1)
        local p=Players[pid]
        if p and p:IsAlive() then
            for _,city in p:GetCities():Members() do
                if not city:GetDistricts():HasDistrict(d.Index) then
                    for dx=-3,3 do for dy=-3,3 do
                        local plot=Map.GetPlotXYWithRangeCheck(city:GetX(),city:GetY(),dx,dy,3)
                        local ownerCity=plot and Cities.GetPlotPurchaseCity(plot)
                        if plot and plot:GetOwner()==pid and ownerCity and ownerCity:GetID()==city:GetID() then
                            assert(CSCBridgeEntry(pid,city:GetID(),d.Index,plot:GetIndex(),delta)==1)
                            count=count+1
                        end
                    end end
                end
            end
        end
    end
    assert(CSCBridgeCommit()==1)
    print('CSC_WORKSHOP_PUBLICATION '..Game.GetCurrentGameTurn()..' '..version..' '..count)
end
local function guarded_publish()
    local ok,message=pcall(publish)
    if not ok then
        if type(CSCBridgeDisable)=='function' then CSCBridgeDisable() end
        print('CSC_WORKSHOP_BRIDGE FAILURE '..tostring(message))
    end
end
-- Synchronized gameplay events supply policy; scoring jobs only read native data.
if GameEvents and GameEvents.OnGameTurnStarted then GameEvents.OnGameTurnStarted.Add(guarded_publish) end
Events.PlayerTurnActivated.Add(function() if ready then status('turn') end end)
guarded_publish()
