-- The game controller loads this study only for an explicit trial. In shadow
-- mode it compares a shortlist with the full planner. Live mode can return
-- false immediately before QuarterForecast, removing that site from the bid.
-- Cold starts and gaps in a city's history always get a complete evaluation.
local E=assert(CSC_AI_EconomyAdapters)
assert(not E.ShortlistObserver)
local O={passes=0,live=CSC_LIVE_SHORTLIST==true}
if O.live then assert(E.SupportsSelectiveQuarterForecasts) end
local histories={}
local watches={}
local function yes(value)return value and 1 or 0 end
local function scope(city,district)return city..':'..district end
local function earlier(a,b)
    return a.finalQ8>b.finalQ8 or a.finalQ8==b.finalQ8 and a.plot<b.plot
end

local function unlocked(s,id)
    if s.unlocks[id]==nil then
        local d=GameInfo.Districts[id]
        local tech=d.PrereqTech and GameInfo.Technologies[d.PrereqTech]
        local civic=d.PrereqCivic and GameInfo.Civics[d.PrereqCivic]
        s.unlocks[id]=yes((not tech or s.player:GetTechs():HasTech(tech.Index))
            and (not civic or s.player:GetCulture():HasCivic(civic.Index)))
    end
    return s.unlocks[id]
end

function O.site(snapshot,city,plot,profile,site,options,invoice,plan)
    local s=snapshot.shortlistSample
    if not s then
        s={groups={},unlocks={},gold=snapshot.player:GetTreasury():GetGoldBalance(),player=snapshot.player}
        snapshot.shortlistSample=s
    end
    local cityID,district,index=city:GetID(),profile.district.Index,plot:GetIndex()
    local key=scope(cityID,district)
    local g=s.groups[key] or {city=cityID,district=district,quarter=profile.key,rows={}}
    s.groups[key]=g
    assert(not g.rows[index],'duplicate forecast candidate')
    local capacity=snapshot.DistrictCapacity(city)
    local sig={tostring(plot:GetOwner()),tostring(site.startingAdjacency),tostring(capacity.reason),
        tostring(unlocked(s,district)),tostring(invoice<=s.gold)}
    local links={}
    for _,v in ipairs(site.suppliers or {})do
        links[#links+1]=table.concat({'m',v.kind,v.plot,yes(v.ready==0),yes(v.ready and v.ready<site.horizon)},':')
    end
    for _,v in ipairs(site.customers or {})do
        links[#links+1]=table.concat({'c',v.plot or -1,v.type or '',yes(v.complete),yes(v.working),yes(v.unlock==0)},':')
    end
    local harbor=site.completedHarborPlot~=nil
    for _,v in ipairs(options)do
        links[#links+1]=table.concat({'o',v.city,v.district,v.plot,unlocked(s,v.district),yes((v.purchaseGold or 0)<=s.gold)},':')
        harbor=harbor or v.family=='DISTRICT_HARBOR'
    end
    -- A visible hostile unit arriving or leaving can change which district
    -- can use the plot. Avoid consulting hidden unit positions.
    if PlayersVisibility[snapshot.id]:IsVisible(plot:GetX(),plot:GetY()) and plot:GetUnitCount()>0 then
        for _,u in ipairs(Units.GetUnitsInPlot(plot) or {})do
            if s.player:GetDiplomacy():IsAtWarWith(u:GetOwner()) then links[#links+1]='hostile';break end
        end
    end
    table.sort(links)
    sig[#sig+1]=table.concat(links,',')
    local saved=snapshot.savedLayouts and snapshot.savedLayouts[key]
    g.rows[index]={signature=table.concat(sig,'|'),must=plan or (saved and saved.plot==index)
        or (snapshot.intentFootprints and snapshot.intentFootprints[index]),
        base=site.baseCount,spec=site.specialtyCount,harbor=harbor,
        partner=(site.strongLayout or site.prospectiveLayout or {}).plot or -1}
    if O.live then
        local turn=Game.GetCurrentGameTurn()
        local history=histories[snapshot.id]
        local prior=history and history.turn==turn-1 and history.groups[key]
        local row=g.rows[index]
        -- An empty shortlist can conceal an entire new investment when the
        -- city's economy changes. Give every eligible site a fresh chance.
        if not prior or not prior.best or (turn+cityID+district)%8==0 then return true end
        -- A customer footprint can itself become the best Quarter location
        -- next turn. Price it even if today's geometry still looks identical.
        return row.must or prior.leaders[index] or prior.partners[index] or index==prior.spare
            or prior.signatures[index]~=row.signature
    end
end

local function finishLive(snapshot,entries)
    local turn,pid=Game.GetCurrentGameTurn(),snapshot.id
    local groups=snapshot.shortlistSample and snapshot.shortlistSample.groups or {}
    local history=histories[pid]
    local state={turn=turn,groups={}}
    for _,entry in ipairs(entries)do
        if entry.economy and not entry.carried and entry.finalQ8>0 then
            local g=assert(groups[scope(entry.city,entry.district)])
            if not g.best or earlier(entry,g.best)then g.second=g.best;g.best=entry
            elseif not g.second or earlier(entry,g.second)then g.second=entry end
        end
    end
    for key,g in pairs(groups)do
        local prior=history and history.turn==turn-1 and history.groups[key]
        local cursor=prior and prior.spare or -1
        local nextGroup={best=g.best~=nil,leaders={},partners={},signatures={}}
        if g.best then
            nextGroup.leaders[g.best.plot]=true
            if g.second then nextGroup.leaders[g.second.plot]=true end
            for _,option in ipairs(g.best.customerLayout or {})do nextGroup.partners[option.plot]=true end
            if g.best.strongLayout then nextGroup.partners[g.best.strongLayout.plot]=true end
            if g.best.prospectiveLayout then nextGroup.partners[g.best.prospectiveLayout.plot]=true end
        end
        -- Pick the next spare by plot ID from the last known candidate set.
        -- This permits a one-pass cutoff. A disappearing spare costs one
        -- rotation; new, changed and protected plots always qualify directly.
        local first,nextPlot
        for plot,row in pairs(g.rows)do
            nextGroup.signatures[plot]=row.signature
            if not row.must and not nextGroup.leaders[plot] and not nextGroup.partners[plot] then
                if not first or plot<first then first=plot end
                if plot>cursor and (not nextPlot or plot<nextPlot)then nextPlot=plot end
            end
        end
        nextGroup.spare=nextPlot or first
        state.groups[key]=nextGroup
    end
    histories[pid]=state
    O.passes=O.passes+1
end

local function selectPlots(g,prior,turn)
    local keep,others={},{}
    local refresh=not prior or (turn+g.city+g.district)%8==0
    for plot,row in pairs(g.rows)do
        if refresh or row.must or prior.leaders[plot] or prior.signatures[plot]~=row.signature then
            keep[plot]=true
        else others[#others+1]=plot end
    end
    local cursor=prior and prior.cursor or -1
    if #others>0 then
        table.sort(others)
        local rotated=others[1]
        for _,plot in ipairs(others)do if plot>cursor then rotated=plot;break end end
        keep[rotated]=true;cursor=rotated
    end
    return keep,cursor
end

function O.finish(snapshot,entries)
    if O.live then return finishLive(snapshot,entries) end
    local turn,pid=Game.GetCurrentGameTurn(),snapshot.id
    local previous=histories[pid]
    local pending=watches[pid] or {};watches[pid]=pending
    local state={turn=turn,groups={}}
    local groups=snapshot.shortlistSample and snapshot.shortlistSample.groups or {}
    local keys={};for k in pairs(groups)do keys[#keys+1]=k end;table.sort(keys)
    -- Decide every retained set before looking at today's complete scores.
    for _,key in ipairs(keys)do
        local g=groups[key]
        local prior=previous and previous.turn==turn-1 and previous.groups[key]
        g.keep,g.cursor=selectPlots(g,prior,turn)
        g.cold=not prior
        g.bids={}
    end
    for _,e in ipairs(entries)do if e.economy and not e.carried then
        local g=assert(groups[scope(e.city,e.district)],'bid without a sampled scope')
        assert(g.rows[e.plot],'bid without a sampled forecast')
        g.bids[#g.bids+1]=e
    end end
    for _,key in ipairs(keys)do
        local g=groups[key]
        table.sort(g.bids,earlier)
        local nextState={leaders={},signatures={},cursor=g.cursor}
        state.groups[key]=nextState
        local priced,kept=0,0
        for plot,row in pairs(g.rows)do
            nextState.signatures[plot]=row.signature
            priced=priced+1;kept=kept+yes(g.keep[plot])
        end
        local best,runner=g.bids[1],nil
        local n=0
        for _,bid in ipairs(g.bids)do if g.keep[bid.plot]then
            runner=runner or bid
            nextState.leaders[bid.plot]=true;n=n+1
            if n==2 then break end
        end end
        local facts=best and g.rows[best.plot] or {}
        if best and not g.keep[best.plot] then
            local id=key..':'..best.plot
            if not pending[id] then pending[id]={start=turn,city=g.city,scope=key,plot=best.plot,partner=facts.partner} end
        end
        print(string.format('CSC_SHORTLIST_SCOPE turn=%d player=%d city=%d district=%d quarter=%s calls=%d kept=%d cold=%d winner=%d bid=%d alternate=%d alternateBid=%d base=%d spec=%d harbor=%d partner=%d',
            turn,pid,g.city,g.district,g.quarter,priced,kept,yes(g.cold),best and best.plot or -1,best and best.finalQ8 or 0,
            runner and runner.plot or -1,runner and runner.finalQ8 or 0,facts.base or 0,facts.spec or 0,yes(facts.harbor),facts.partner or -1))
    end
    -- Observe up to ten turns after a missed leader. The full planner still
    -- acts, so later occupation is evidence of competition in this game.
    local function occupant(index)
        if index<0 then return -1 end
        local plot=Map.GetPlotByIndex(index)
        if not PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY()) then return -1 end
        local d=GameInfo.Districts[plot:GetDistrictType()]
        return d and d.DistrictType or -1
    end
    for id,w in pairs(pending)do if turn>w.start then
        local g=groups[w.scope]
        local q,p=occupant(w.plot),occupant(w.partner)
        local repriced=g and g.keep[w.plot]
        if q~=-1 or repriced or turn-w.start>=10 then
            print(string.format('CSC_SHORTLIST_WATCH turn=%d player=%d start=%d site=%s repriced=%d occupant=%s partnerOccupant=%s',
                turn,pid,w.start,id,yes(repriced),tostring(q),tostring(p)))
            pending[id]=nil
        end
    end end
    histories[pid]=state
    O.passes=O.passes+1
    print('CSC_SHORTLIST_PASS',turn,pid,#keys)
end
E.ShortlistObserver=O
print(O.live and 'CSC_SHORTLIST_LIVE_READY' or 'CSC_SHORTLIST_READY')
