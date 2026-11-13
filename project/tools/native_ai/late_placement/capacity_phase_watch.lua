-- Diagnostic-only phase ordering in a short, controller-owned replay. Read city
-- population, claimed districts, UI allocation and the current published offers.
-- Never call the CSC publisher, change a packet, order production or refresh UI.
-- In particular a population event can precede the UI cache: keep both values.
assert(not CSC_CAPACITY_PHASE_WATCH, 'Duplicate capacity phase observer')
local B=assert(CSC_AI_DistrictBridge)
local ui=assert(ExposedMembers.CSC_Adjacency)
assert(type(ui.GetDistrictCapacity)=='function', 'Missing capacity read boundary')
local state={enabled=true,sequence=0,faults=0,publications=0,populationEvents=0,offersKnown=false,
    districtEvents=0,playerEvents=0,offers={}}
state.version=tonumber(assert(CE_AIDistrictScoresStatus()):match('"version":(%d+)'))
local function flag(v)return v==true or v==1 end
local function emit(kind,row)
    -- A runaway callback disables this observer through safe(), not CSC policy.
    assert(state.sequence<20000,'Capacity phase record bound')
    state.sequence=state.sequence+1
    row.sequence=state.sequence;row.event=kind;row.turn=Game.GetCurrentGameTurn()
    local fields={}
    for k,v in pairs(row)do if v~=nil then
        fields[#fields+1]=k..'='..tostring(v):gsub('[\t\r\n]',' ')
    end end
    table.sort(fields);print('CSC_CAPACITY_PHASE\t'..table.concat(fields,'\t'))
end
local function observe(kind,pid,id,extra)
    if not pid or pid<1 or pid>5 then return end
    local city=CityManager.GetCity(pid,id)
    if not city then emit(kind,{player=pid,city=id,missing=true});return end
    local used,inventory=0,{}
    local ds=city:GetDistricts()
    for i=0,ds:GetNumDistricts()-1 do
        local d=ds:GetDistrictByIndex(i)
        if d then
            local def=assert(GameInfo.Districts[d:GetType()])
            if flag(def.RequiresPopulation)and not flag(def.InternalOnly)then used=used+1 end
            inventory[#inventory+1]=d:GetType()..':'..tostring(d:IsComplete())
        end
    end
    table.sort(inventory)
    local capacity=ui.GetDistrictCapacity(pid,id)or{}
    local population=city:GetPopulation()
    local row={player=pid,city=id,name=city:GetName(),population=population,liveUsed=used,
        uiPopulation=capacity.population,uiUsed=capacity.used,uiAllowed=capacity.allowed,
        agrees=capacity.population==population and capacity.used==used,
        version=state.version,offersKnown=state.offersKnown,inventory=table.concat(inventory,',')}
    for _,district in ipairs({36,37})do
        local offer=state.offers[pid..':'..id..':'..district]
        row['offers'..district]=state.offersKnown and(offer and offer.count or 0)or nil
        row['bid'..district]=offer and offer.bid
        row['plot'..district]=offer and offer.plot
    end
    for k,v in pairs(extra or{})do row[k]=v end
    emit(kind,row)
end
local function scan(kind,onlyPlayer)
    for _,player in ipairs(PlayerManager.GetAliveMajors())do
        local pid=player:GetID()
        if pid>=1 and pid<=5 and(not onlyPlayer or onlyPlayer==pid)then
            for _,city in player:GetCities():Members()do observe(kind,pid,city:GetID())end
        end
    end
end
local function safe(fn,...)
    if not state.enabled then return end
    local ok,error=pcall(fn,...)
    if not ok then
        state.faults=state.faults+1;state.enabled=false
        print('CSC_CAPACITY_PHASE_FAULT',tostring(error))
    end
end
local publish=B.Publish
B.Publish=function(version,width,height,count,players,entries,...)
    safe(scan,'publication-enter') -- old packet remains active here
    local accepted,message=publish(version,width,height,count,players,entries,...)
    if accepted then
        state.version=version;state.offers={};state.offersKnown=true;state.publications=state.publications+1
        for _,entry in ipairs(entries)do
            if(entry.district==36 or entry.district==37)and entry.finalQ8 and entry.finalQ8>0 then
                local key=entry.player..':'..entry.city..':'..entry.district
                local old=state.offers[key]
                local best=not old or entry.finalQ8>old.bid
                state.offers[key]={count=(old and old.count or 0)+1,
                    bid=best and entry.finalQ8 or old.bid,plot=best and entry.plot or old.plot}
            end
        end
        safe(scan,'publication-accepted') -- receipt, not a native choice
    end
    return accepted,message
end
local function bind(name,fn)
    local event=Events[name]
    emit('binding',{name=name,available=event~=nil})
    if event then event.Add(fn)end
end
bind('CityPopulationChanged',function(player,city,...)
    state.populationEvents=state.populationEvents+1
    safe(observe,'population-event',player,city)
end)
bind('DistrictAddedToMap',function(player,district,city,x,y,kind)
    state.districtEvents=state.districtEvents+1
    safe(observe,'district-event',player,city,{addedDistrict=kind,addedID=district,x=x,y=y})
end)
bind('PlayerTurnActivated',function(player,first)
    state.playerEvents=state.playerEvents+1
    safe(scan,'player-activated',player)
end)
GameEvents.OnGameTurnStarted.Add(function()safe(scan,'round-after-policy')end)
safe(scan,'installed')
CSC_CAPACITY_PHASE_WATCH={Finish=function()
    emit('finish',{faults=state.faults,publications=state.publications,
        populationEvents=state.populationEvents,districtEvents=state.districtEvents,
        playerEvents=state.playerEvents})
    assert(state.faults==0,'Capacity phase observer failed')
end}
print('CSC_CAPACITY_PHASE_INSTALLED')
