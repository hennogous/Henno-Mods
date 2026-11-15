-- Decision adapters for the central Quarter ledger. Site facts, transaction
-- amounts and prerequisite relationships belong to EconomyFacts/EconomyModel.
-- This module converts a ledger into a native bid, applies bounded placement
-- policy, and exposes the same marginal valuation to building/job consumers.
-- Native SQL customer adjacency, supplier protection and purchase/commitment
-- machinery remain separate consumers, not duplicate sources of income.
CSC_AI_EconomyAdapters={}
local E=CSC_AI_EconomyAdapters
local M=CSC_AI_EconomyModel
local F=CSC_AI_EconomyFacts
local C=CSC_AI_PlanContinuity
local planStates={}
local propertyPrefix='CSC_AI_QuarterIntentV1_'
local function planState(pid)
    if not C then return nil end
    local turn=Game.GetCurrentGameTurn()
    if not planStates[pid]or planStates[pid].turn~=turn then
        local encoded
        if type(Game.GetProperty)=='function'then
            local ok,value=pcall(Game.GetProperty,Game,propertyPrefix..pid)
            if not ok then return nil end
            encoded=value
        end
        planStates[pid]=C.New(pid,turn,encoded)
        planStates[pid].savedEncoded=encoded
    end
    return planStates[pid]
end

function E.ObserveNativeChoices(status,entries)
    if not C or type(CE_AIDistrictScoresTraceRead)~='function'then return end
    local function number(record,name)return tonumber(record:match('"'..name..'":(-?%d+)'))end
    local count,generation=number(status,'trace_count'),number(status,'generation')
    local version=number(status,'version')
    if not count or not generation or count<0 or count>16384 then return end
    local offered={}
    for _,entry in ipairs(entries)do if entry.economy and not entry.carried then
        offered[table.concat({entry.player,entry.city,entry.district,entry.plot},':')]=entry
    end end
    local choices={}
    -- One complete read per publication, max256 pages at the CE16384-record
    -- contract. Do not derive policy from the diagnostic top16/top32 receipts.
    -- Collect first: a stale page cannot partially confirm intent.
    for offset=0,count-1,64 do
        local page=CE_AIDistrictScoresTraceRead(offset,64,generation)
        if type(page)~='string'or page:find('"stale":true',1,true)then return end
        for record in page:gmatch('{[^{}]+}')do
            if record:match('"k":"([^"]+)"')=='best'
                and number(record,'version')==version and number(record,'existingDistrict')==0 then
                local pid,city,district,plot=number(record,'player'),number(record,'city'),number(record,'district'),number(record,'plot')
                if pid and city and district and plot then
                    local entry=offered[table.concat({pid,city,district,plot},':')]
                    if entry and entry.finalQ8>0 and number(record,'result')==entry.finalQ8 then choices[#choices+1]=entry end
                end
            end
        end
    end
    for _,entry in ipairs(choices)do
        local state=planState(entry.player)
        if state then C.Selected(state,entry)end
    end
    print(string.format('CSC_AI_PLAN_JOURNAL turn=%d records=%d pages=%d confirmed=%d saturated=%s',
        Game.GetCurrentGameTurn(),count,math.ceil(count/64),#choices,tostring(count==16384)))
end

function E.Committed(entries)
    if not C then return end
    local turn=Game.GetCurrentGameTurn()
    for pid,state in pairs(planStates)do if state.turn==turn then
        C.Committed(state,entries)
        local encoded=C.Encode(state)
        if type(Game.SetProperty)=='function'and encoded~=state.savedEncoded then
            Game:SetProperty(propertyPrefix..pid,encoded);state.savedEncoded=encoded
        end
        for _,event in ipairs(state.events)do
            print(string.format('CSC_AI_PLAN_EVENT turn=%d player=%d city=%d district=%d plot=%d kind=%s reason=%s valueQ8=%d forecastTurn=%d',
                turn,pid,event.city,event.district,event.plot,event.kind,event.reason,event.valueQ8 or 0,event.forecastTurn or -1))
        end
        if state.eventsDropped>0 then print('CSC_AI_PLAN_EVENTS_OMITTED',turn,pid,state.eventsDropped)end
        state.events={};state.eventsDropped=0
    end end
end

function E.Available()
    if type(CE_AIEconomyStatus)~='function'or type(CE_AIDistrictScoresFinalEntry)~='function'
        or type(CE_AIDistrictScoresManagedType)~='function'or type(CE_AIDistrictScoresManagedReceipt)~='function'
        or type(CE_AIYieldStreamValue)~='function'or type(CE_AIAmenityStreamValue)~='function'
        or type(CE_AIYieldFixedValue)~='function'then
        return false,'CE economic pricing/final-score API unavailable'
    end
    local ok,status=pcall(CE_AIEconomyStatus)
    if not ok or type(status)~='string'or not status:match('"pricingReady":1')
        or not status:match('"finalReady":1')then return false,'CE economic API is not qualified'end
    return true
end

function E.Snapshot(player,placement,ui)
    local available,reason=E.Available();if not available then return nil,reason end
    local snapshot=F.New(player,placement,ui)
    local quotes={};local count=0
    snapshot.Price=function(stream,horizon)
        local amount=stream.amount
        local units=amount>=0 and math.floor(amount*256+.5)or-math.floor(-amount*256+.5)
        local key=table.concat({stream.city,stream.yield,units,stream.ready,horizon,tostring(stream.fixed==true)},':')
        if quotes[key]~=nil then return quotes[key]end
        local value
        if stream.yield=='AMENITY'then
            value=CE_AIAmenityStreamValue(snapshot.id,stream.city,amount,stream.ready,horizon,4*256)
        else
            local definition=GameInfo.Yields[stream.yield]
            if not definition then return nil end
            if stream.fixed then
                value=CE_AIYieldFixedValue(snapshot.id,stream.city,definition.Index,units,stream.ready,4*256)
            else
                value=CE_AIYieldStreamValue(snapshot.id,stream.city,definition.Index,units,stream.ready,horizon,4*256)
            end
        end
        -- Unknown is not cached as zero and cannot produce a final replacement.
        -- Price/discount policy is explicit: a50-turn window and4.0 discount,
        -- matching the qualified native fixture. These are initial calibration
        -- assumptions, not a claim to reproduce every city's native horizon.
        if type(value)=='number'or type(value)=='integer'then quotes[key]=value;count=count+1 end
        return value
    end
    snapshot.QuoteCount=function()return count end
    snapshot.planState=planState(snapshot.id)
    -- Cache native UI admission/quotes within this publication. All adapters
    -- observe the same legal targets without repeating context crossings.
    snapshot.ui=setmetatable({}, {__index=ui})
    local targets={}
    snapshot.ui.GetLegalDistrictTargets=function(pid,city,hash)
        local key=pid..':'..city..':'..hash
        if not targets[key]then targets[key]=ui.GetLegalDistrictTargets(pid,city,hash)end
        return targets[key]
    end
    for _,name in ipairs({'GetRawPlotPurchaseQuote','GetPlotPurchaseQuote'})do
        local method=name
        local values={}
        snapshot.ui[method]=function(pid,city,plot)
            local key=pid..':'..city..':'..plot
            if values[key]~=nil then return values[key]or nil end
            if type(ui[method])~='function'then return nil end
            local value=ui[method](pid,city,plot)
            values[key]=value or false;return value
        end
    end
    return snapshot
end

-- Spatial quality is a native-utility preference beside the monetary ledger,
-- not additional gameplay adjacency. Henno's15 November map-planning revision
-- keeps +2 at48 and increases +3/+4/+5/+6+ to144/288/432/576. Both material
-- classes add64; extra Base/Spec deposits add24/16 each, capped at two extras.
-- These are initial bounded estimates: strengthen durable map quality without
-- allowing a cluster or several speculative customers to grow without limit.
-- Prospective customer terrain adds at most96 in total; actual transactions
-- still require completed customer districts in the economic ledger.
-- They do not make an otherwise losing investment profitable or guarantee it
-- beats another district/unit. Below+2 and no-Base sites defer this publication.
-- Managed CE types withhold nonpositive options from fresh proposals because
-- vanilla GetBestDistrict can otherwise select the least-negative candidate.
E.DeferredQuarterQ8=-1024*256
-- Both the inexpensive geometry screen and the final economic alternative
-- use this floor. A stale pre-screen must not silently discard eligible +2
-- sites before their complete-value quote reaches the publication packet.
E.MinimumAdjacency=2
E.MinimumSitingBonusQ8=48*256

function E.SpatialPlan(options)
    -- At most six adjacent plots per customer type. Keep only the two best
    -- footprints of each family, then compare singles/pairs exactly. This
    -- bounds pair work and cannot count the same tile or customer family twice.
    -- Ordinary native adjacency informs QUALITY only. One point earns8 utility
    -- up to four points;16 recognises feasible space. Inferior alternatives or
    -- consuming a better customer tile reduce that preference by up to32 each.
    local families={}
    local function better(a,b)
        if a.preference~=b.preference then return a.preference>b.preference end
        if a.adjacency~=b.adjacency then return a.adjacency>b.adjacency end
        if a.city~=b.city then return a.city<b.city end
        if a.district~=b.district then return a.district<b.district end
        return a.plot<b.plot
    end
    for _,source in ipairs(options or{})do
        local option={};for k,v in pairs(source)do option[k]=v end
        option.preference=math.max(0,16+8*math.min(4,option.adjacency)
            -8*math.min(4,math.max(0,option.bestAdjacency-option.adjacency))
            -8*math.min(4,math.max(0,option.displacedAdjacency-option.adjacency)))
        local group=families[option.family]or{};families[option.family]=group
        group[#group+1]=option;table.sort(group,better)
        if #group>2 then group[3]=nil end
    end
    local choices={}
    for _,group in pairs(families)do for _,option in ipairs(group)do choices[#choices+1]=option end end
    table.sort(choices,better)
    local best={preference=0,links={}}
    for i,a in ipairs(choices)do
        if a.preference>best.preference then best={preference=a.preference,links={a}}end
        for j=i+1,#choices do local b=choices[j]
            if a.family~=b.family and a.plot~=b.plot and a.preference>0 and b.preference>0
                and a.preference+b.preference>best.preference then
                best={preference=a.preference+b.preference,links={a,b}}
            end
        end
    end
    return best
end

function E.PlacementValue(quote,site,protectionQ8,coversOwnMaterial)
    if quote.adjacency+1e-6<E.MinimumAdjacency or (site.baseCount or 0)<1 then return E.DeferredQuarterQ8,'quality'end
    -- Only named supply loss enters the complete ledger. Old no-host/readiness
    -- heuristics were ownership-dependent and duplicated its own valuation.
    -- Missing customer space loses its current layout preference/income; it
    -- does not acquire a hidden128-utility penalty when land becomes owned.
    local penalty=math.max(0,protectionQ8 or 0)
    if coversOwnMaterial then penalty=math.max(penalty,256*256)end
    local value=quote.valueQ8-penalty
    if value<=0 then return value,'economics'end
    local premium
    if quote.adjacency<3 then
        -- Fractional adjacency can arise through yield multipliers. Interpolate
        -- 48->144 between +2/+3 rather than introducing a jump at the boundary.
        premium=E.MinimumSitingBonusQ8+(quote.adjacency-2)*(144*256-E.MinimumSitingBonusQ8)
    else
        premium=math.min(4,quote.adjacency-2)*144*256
    end
    local materials=math.min(2,math.max(0,(site.baseCount or 0)-1))*24
    if (site.specialtyCount or 0)>0 then
        materials=materials+64+math.min(2,site.specialtyCount-1)*16
    end
    local layout=site.spatialPlan and site.spatialPlan.preference or 0
    local bid=math.floor(math.max(-4096*256,math.min(4096*256,value+premium+(materials+layout)*256))+.5)
    return bid,'positive',{adjacencyQ8=math.floor(premium+.5),materialsQ8=materials*256,
        layoutQ8=layout*256,penaltyQ8=penalty}
end

local function siteKey(city,district,plot)return city..':'..district..':'..plot end

local function activePlan(snapshot,city,district,plot)
    local state=snapshot.planState
    local plan=state and state.plans[siteKey(city,district,plot)]
    return plan and plan.plot==plot and plan or nil
end

local function reconcilePlans(snapshot)
    local state=snapshot.planState
    if not C or not state then return end
    snapshot.intentKeys={}
    local plans={};for _,plan in pairs(state.plans)do
        plans[#plans+1]=plan;snapshot.intentKeys[siteKey(plan.city,plan.district,plan.plot)]=true
    end
    for _,plan in ipairs(plans)do
        local city=snapshot.cities[plan.city]and snapshot.cities[plan.city].object
        local plot=Map.GetPlotByIndex(plan.plot)
        if not plot then C.Withdraw(state,plan.city,plan.district,plan.plot,'plot_missing')
        else
            local assigned=plot:GetOwner()==snapshot.id and Cities.GetPlotPurchaseCity(plot)
            C.Reconcile(state,plan,{cityExists=city~=nil,owner=plot:GetOwner(),
                assigned=assigned and assigned:GetID(),district=plot:GetDistrictType(),
                quarterExists=city and city:GetDistricts():HasDistrict(plan.district),
                signature=snapshot.FootprintSignature and snapshot.FootprintSignature(plot)or'_'})
        end
    end
    snapshot.intentFootprints={}
    for _,plan in pairs(state.plans)do snapshot.intentFootprints[plan.plot]=true end
end

function E.ReportWithdrawals(snapshot,entries,evaluations,scopes,previous)
    local published,candidates={},{}
    for _,entry in ipairs(entries)do if entry.economy then
        published[siteKey(entry.city,entry.district,entry.plot)]=true
    end end
    for _,entry in ipairs(previous)do if entry.player==snapshot.id and entry.economy then
        local id=siteKey(entry.city,entry.district,entry.plot)
        if not published[id]then candidates[id]=entry end
    end end
    if snapshot.planState then for _,plan in pairs(snapshot.planState.plans)do
        local id=siteKey(plan.city,plan.district,plan.plot)
        if not published[id]then
            candidates[id]=candidates[id]or{city=plan.city,district=plan.district,plot=plan.plot,finalQ8=plan.lastQ8}
        end
    end end
    local ordered={}
    for id,entry in pairs(candidates)do
        ordered[#ordered+1]={id=id,entry=entry,native=snapshot.intentKeys and snapshot.intentKeys[id]==true}
    end
    table.sort(ordered,function(a,b)
        if a.native~=b.native then return a.native==true end
        return a.id<b.id
    end)
    local ordinary,omitted=0,0
    for _,item in ipairs(ordered)do
        local e=item.entry
        local details=evaluations[item.id]
        if not details then
            local city=snapshot.cities[e.city]and snapshot.cities[e.city].object
            local plot=Map.GetPlotByIndex(e.plot)
            local assigned=plot and plot:GetOwner()==snapshot.id and Cities.GetPlotPurchaseCity(plot)
            local reason='scope_not_evaluated'
            if not city then reason='city_missing'
            elseif scopes[e.city..':'..e.district]=='quarter_exists'then reason='quarter_exists'
            elseif not plot then reason='plot_missing'
            elseif plot:GetDistrictType()>=0 then reason='footprint_occupied'
            elseif plot:GetOwner()~=snapshot.id then reason='ownership_changed'
            elseif not assigned then reason='city_assignment_unknown'
            elseif assigned:GetID()~=e.city then reason='city_assignment_changed'end
            details={reason=reason,owner=plot and plot:GetOwner()}
        end
        if activePlan(snapshot,e.city,e.district,e.plot)then
            C.Withdraw(snapshot.planState,e.city,e.district,e.plot,details.reason)
        end
        if details.reason=='quarter_exists'or details.reason=='founded'then
            if item.native then print('CSC_AI_QUARTER_PLAN_FINISHED',Game.GetCurrentGameTurn(),snapshot.id,e.city,e.district,e.plot,details.reason)end
        elseif item.native or ordinary<16 then
            if not item.native then ordinary=ordinary+1 end
            print(string.format('CSC_AI_QUARTER_WITHDRAWAL_PROPOSED turn=%d player=%d city=%d district=%d plot=%d nativeIntent=%s reason=%s previousQ8=%d managedQ8=%d owner=%s adjacency=%s economicQ8=%s protectionQ8=%s ignoredLegacyQ8=%s displacementQ8=%s purchaseQ8=%s footprintWorkers=%s footprintMode=%s detail=%s',
                Game.GetCurrentGameTurn(),snapshot.id,e.city,e.district,e.plot,tostring(item.native),details.reason,
                e.finalQ8 or 0,E.DeferredQuarterQ8,tostring(details.owner),tostring(details.adjacency),
                tostring(details.economicQ8),tostring(details.protectionQ8),tostring(details.legacyIgnoredQ8),
                tostring(details.displacementQ8),tostring(details.purchaseQ8),tostring(details.footprintWorkers),
                tostring(details.footprintMode),tostring(details.detail):gsub('[%s%c]','_'):sub(1,160)))
        else omitted=omitted+1 end
    end
    if omitted>0 then print('CSC_AI_QUARTER_WITHDRAWALS_OMITTED',Game.GetCurrentGameTurn(),snapshot.id,omitted)end
end

function E.QuotePlacement(snapshot,city,plot,profile,geometry,frontier,invoice,protectionQ8,ignoredLegacy,covers,protected)
    local plan=activePlan(snapshot,city:GetID(),profile.district.Index,plot:GetIndex())
    local state=snapshot.planState
    local facts,reason=snapshot.Site(city,plot,profile)
    local details={reason='unknown',legacyIgnoredQ8=ignoredLegacy or 0,protectionQ8=protectionQ8 or 0,
        owner=plot:GetOwner(),adjacency=geometry.upper,invoice=invoice}
    local site,quote,parts,bid
    if facts then
        site=C and C.PrepareSite(plan,facts)or{}
        if not C then for k,v in pairs(facts)do site[k]=v end;site.footprintCostMode='current'end
        site.purchaseGold=invoice
        site.spatialPlan=E.SpatialPlan(snapshot.CustomerOptions
            and snapshot.CustomerOptions(city,plot,profile,protected)or{})
        local ok,value,message=pcall(M.Forecast,site,snapshot.Price,function(alternative)
            return E.PlacementValue(alternative,site,protectionQ8,covers)
        end)
        if ok then quote,reason=value,message else reason=tostring(value)end
        if quote then
            bid,details.reason,parts=E.PlacementValue(quote,site,protectionQ8,covers)
            details.economicQ8=quote.valueQ8;details.afterProtectionQ8=quote.valueQ8-(parts and parts.penaltyQ8 or math.max(protectionQ8 or 0,covers and 256*256 or 0))
            details.adjacency=quote.adjacency;details.base=site.baseCount
            details.footprintWorkers=site.footprintWorkers
            details.footprintMode=site.footprintCostMode;details.displacementQ8=0;details.purchaseQ8=0
            for _,flow in ipairs(quote.streams)do
                if flow.id:find('site:displaced:',1,true)then details.displacementQ8=details.displacementQ8+(flow.valueQ8 or 0)end
                if flow.id=='footprint-purchase'then details.purchaseQ8=flow.valueQ8 end
            end
            details.currentDisplacementQ8=details.displacementQ8
            if site.footprintCostMode~='current'then
                -- Diagnostic only: expose the cost excluded by the chosen
                -- baseline. Price at most six ordinary yields; never re-run
                -- the full alternative search or add this back into the bid.
                details.currentDisplacementQ8=0
                for _,flow in ipairs(facts.direct or{})do if flow.id:find('displaced:',1,true)then
                    local ok,cost=pcall(snapshot.Price,{city=flow.city or facts.city,
                        yield=flow.yield,amount=flow.amount,ready=facts.quarterReady},facts.horizon)
                    if not ok or type(cost)~='number'and type(cost)~='integer'then details.currentDisplacementQ8=nil;break end
                    details.currentDisplacementQ8=details.currentDisplacementQ8+cost
                end end
            end
            if details.reason=='positive'then
                if plan then
                    print(string.format('CSC_AI_PLAN_QUOTE_PROPOSED turn=%d player=%d city=%d district=%d plot=%d economicQ8=%d protectionQ8=%d ignoredLegacyQ8=%d displacementQ8=%d currentDisplacementQ8=%s purchaseQ8=%s footprintWorkers=%s footprintMode=%s finalQ8=%d',
                        Game.GetCurrentGameTurn(),snapshot.id,city:GetID(),profile.district.Index,plot:GetIndex(),
                        quote.valueQ8,protectionQ8 or 0,ignoredLegacy or 0,details.displacementQ8,
                        tostring(details.currentDisplacementQ8),tostring(details.purchaseQ8),tostring(site.footprintWorkers),site.footprintCostMode,bid))
                end
                return {bid=bid,quote=quote,site=site,parts=parts,details=details}
            end
        else
            details.reason=ok and tostring(reason):find('Native price unavailable',1,true)and'pricing_unavailable'
                or not ok and'forecast_error'or'readiness_unavailable'
        end
    else details.reason=reason=='Footprint staffing unavailable'and'footprint_staffing_unavailable'or'facts_unavailable'end
    details.detail=reason
    if not quote and C and plan then
        local supply=snapshot.Supply and snapshot.Supply(plot,profile)
        local signature=snapshot.FootprintSignature and snapshot.FootprintSignature(plot)
        -- Grace protects an OWNED confirmed construction plan, never an
        -- unpriced/increasing purchase invoice. Revalidate cheap Core safety
        -- even when staffing/native economic pricing is temporarily absent.
        local safe=not frontier and supply and #supply.base>0 and geometry.upper>=E.MinimumAdjacency
            and not covers and (protectionQ8 or 0)==0 and not protected[plot:GetIndex()]
            and signature==plan.signature
        local carried=C.Grace(state,plan,details.reason,safe)
        if carried then details.reason='grace';return{bid=carried,carried=true,details=details,plan=plan}end
    end
    if C and plan then C.Withdraw(state,plan.city,plan.district,plan.plot,details.reason)end
    return {details=details,quote=quote,site=site}
end

function E.CustomerOffers(snapshot,quarterEntries,protectedPlots)
    -- Prepare only each city/type's best economic Quarter proposal. All other
    -- positive Quarter sites still compete normally. These customer deltas
    -- are16..48 utility, checked against current native legal targets; future
    -- geometry alone never publishes a construction offer. Greedy cross-plan
    -- coordination keeps conflicting types off a shared footprint and protects
    -- the proposed Quarter footprints. Nothing reserves land or grants a slot.
    local best,plans={},{}
    for _,entry in ipairs(quarterEntries)do if entry.economy then
        local key=entry.city..':'..entry.district
        if not best[key]or entry.finalQ8>best[key].finalQ8
            or entry.finalQ8==best[key].finalQ8 and entry.plot<best[key].plot then best[key]=entry end
    end end
    for _,entry in pairs(best)do plans[#plans+1]=entry end
    table.sort(plans,function(a,b)
        if a.finalQ8~=b.finalQ8 then return a.finalQ8>b.finalQ8 end
        if a.city~=b.city then return a.city<b.city end
        return a.district<b.district
    end)
    local occupied,nominated,remaining={},{},{}
    for _,entry in ipairs(plans)do occupied[entry.plot]=true end
    if snapshot.planState then for _,plan in pairs(snapshot.planState.plans)do occupied[plan.plot]=true end end
    for _,entry in ipairs(plans)do for _,link in ipairs(entry.customerLayout or{})do
        local key=link.city..':'..link.district
        local city=snapshot.cities[link.city]and snapshot.cities[link.city].object
        local definition=GameInfo.Districts[link.district]
        if city and definition and not nominated[key]and not occupied[link.plot]and not protectedPlots[link.plot]then
            local exempt=definition.RequiresPopulation==false or definition.RequiresPopulation==0
            if remaining[link.city]==nil then
                local capacity=snapshot.DistrictCapacity(city)
                remaining[link.city]=capacity and capacity.known and capacity.allowed-capacity.used or 0
            end
            local reserve=link.city==entry.city and
                (GameInfo.Districts[entry.district].RequiresPopulation~=false
                and GameInfo.Districts[entry.district].RequiresPopulation~=0)and 1 or 0
            if exempt or remaining[link.city]>reserve then
                local legal=false
                for _,index in ipairs(snapshot.ui.GetLegalDistrictTargets(snapshot.id,link.city,definition.Hash)or{})do
                    if index==link.plot then legal=true;break end
                end
                if legal then
                    nominated[key]={player=snapshot.id,city=link.city,district=link.district,plot=link.plot,
                        delta=math.floor(link.preference*256+.5),customer=true,spatial=true}
                    occupied[link.plot]=true
                    if not exempt then remaining[link.city]=remaining[link.city]-1 end
                end
            end
        end
    end end
    local offers={}
    for _,offer in pairs(nominated)do offers[#offers+1]=offer end
    table.sort(offers,function(a,b)if a.city~=b.city then return a.city<b.city end;return a.district<b.district end)
    return offers
end

function E.QuarterBids(snapshot,placement,protectedPlots,early,previous)
    local clock=os and os.clock
    local started=clock and clock()
    local result,protection,ignoredLegacy,managed,evaluations,scopes={},{},{},{},{},{}
    local profiles=placement.StageTwoProfiles()
    for _,profile in ipairs(profiles)do managed[profile.district.Index]=true end
    for _,entry in ipairs(early)do
        local id=siteKey(entry.city,entry.district,entry.plot)
        if (entry.protectionQ8 or 0)>0 then protection[id]=math.max(protection[id]or 0,entry.protectionQ8)
        else ignoredLegacy[id]=math.max(ignoredLegacy[id]or 0,-(entry.delta or 0))end
    end
    local stats={evaluated=0,final=0,unknown=0,buyerBlocked=0,streams=0,omissions=0,
        qualityDeferred=0,economicDeferred=0,invoiceDeferred=0,carried=0,managed=true,
        capacityReady=0,capacityFull=0,capacityUnknown=0}
    local player,pid=snapshot.player,snapshot.id
    snapshot.planState=planState(pid)
    local visibility=PlayersVisibility[pid]
    reconcilePlans(snapshot)
    for _,profile in ipairs(profiles)do
        for _,city in player:GetCities():Members()do
            local scope=city:GetID()..':'..profile.district.Index
            scopes[scope]=city:GetDistricts():HasDistrict(profile.district.Index)and'quarter_exists'or'active'
            if scopes[scope]=='active'then
                -- Capacity describes CURRENT admission, not the lifetime of
                -- a future district bid. Growth can happen after this global
                -- publication and before that player's native district choice
                -- (phase-observed on this binary; AI-N128).
                -- Suppressing full scopes then leaves the new slot competing
                -- against a stale negative Quarter value for the whole round.
                -- Keep worthwhile economic bids visible; native CanZone still
                -- gates actual construction (AI-N127). The economic formula and
                -- placement premiums are unchanged, and
                -- no missing/stale capacity is treated as a promised free slot.
                local exempt=profile.district.RequiresPopulation==false or profile.district.RequiresPopulation==0
                local capacity=not exempt and snapshot.DistrictCapacity and snapshot.DistrictCapacity(city)
                local ready=exempt or capacity and capacity.known and capacity.used<capacity.allowed
                if ready then stats.capacityReady=stats.capacityReady+1
                elseif capacity and capacity.known then stats.capacityFull=stats.capacityFull+1
                else stats.capacityUnknown=stats.capacityUnknown+1 end
                print(string.format('CSC_AI_QUARTER_CAPACITY turn=%d player=%d city=%d district=%d population=%d used=%d allowed=%d state=%s',
                    Game.GetCurrentGameTurn(),pid,city:GetID(),profile.district.Index,
                    capacity and capacity.population or -1,capacity and capacity.used or -1,
                    capacity and capacity.allowed or -1,exempt and'exempt'or capacity and capacity.reason or'unavailable'))
                local capacityState=exempt and'exempt'or capacity and capacity.reason or'unavailable'
                local center=Map.GetPlot(city:GetX(),city:GetY())
                for _,plot in ipairs(CSC_Adjacency.PlotsInBand(center,1,3))do
                    local owner=plot:GetOwner()
                    local assigned=owner==pid and Cities.GetPlotPurchaseCity(plot)
                    local frontier=false
                    if owner==-1 then for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
                        frontier=frontier or near:GetOwner()==pid
                    end end
                    if plot:GetDistrictType()==-1 and visibility:IsRevealed(plot:GetX(),plot:GetY())
                        and (assigned and assigned:GetID()==city:GetID()or frontier)then
                        -- Enumerate a bounded superset of native map potential,
                        -- including future unlocks. Current CanProduce/BUILD
                        -- and CanHaveDistrict filters are deliberately absent.
                        -- CE preserves native invalid scores and eligibility;
                        -- an overinclusive quote cannot legalise a placement.
                        stats.evaluated=stats.evaluated+1
                        local id=siteKey(city:GetID(),profile.district.Index,plot:GetIndex())
                        local geometry=snapshot.Geometry(city,plot,profile)
                        if geometry.upper+1e-6<E.MinimumAdjacency then
                            stats.qualityDeferred=stats.qualityDeferred+1
                            evaluations[id]={reason='below_adjacency',adjacency=geometry.upper,owner=owner}
                            if activePlan(snapshot,city:GetID(),profile.district.Index,plot:GetIndex())then
                                C.Withdraw(snapshot.planState,city:GetID(),profile.district.Index,plot:GetIndex(),'below_adjacency')
                            end
                        else
                            local invoice=0
                            if frontier then invoice=snapshot.ui.GetRawPlotPurchaseQuote(pid,city:GetID(),plot:GetIndex())end
                            if invoice==nil or invoice<0 then
                                stats.invoiceDeferred=stats.invoiceDeferred+1
                                evaluations[id]={reason='invoice_unavailable',owner=owner,adjacency=geometry.upper}
                            else
                                local resource=GameInfo.Resources[plot:GetResourceType()]
                                local covers=resource and(CSC_Adjacency.HasTag(profile.base,resource.ResourceType)
                                    or CSC_Adjacency.HasTag(profile.specialty,resource.ResourceType))
                                local evaluation=E.QuotePlacement(snapshot,city,plot,profile,geometry,frontier,invoice,
                                    protection[id],ignoredLegacy[id],covers,protectedPlots)
                                evaluations[id]=evaluation.details
                                local quote,site,parts=evaluation.quote,evaluation.site,evaluation.parts
                                if evaluation.carried then stats.carried=stats.carried+1 end
                                if not quote and not evaluation.carried then
                                    stats.unknown=stats.unknown+1
                                    if stats.unknown<=3 then print(string.format('CSC_AI_ECONOMY_QUOTE_UNAVAILABLE turn=%d player=%d city=%d plot=%d reason=%s',
                                        Game.GetCurrentGameTurn(),pid,city:GetID(),plot:GetIndex(),tostring(evaluation.details.detail)))end
                                else
                                    local bid,why=evaluation.bid,evaluation.details.reason
                                    if quote then stats.streams=stats.streams+#quote.streams;stats.omissions=stats.omissions+#quote.omissions end
                                    if why=='quality'then stats.qualityDeferred=stats.qualityDeferred+1
                                    elseif why=='economics'then stats.economicDeferred=stats.economicDeferred+1
                                    else
                                        -- A correct invoice alone does not prove
                                        -- this city will be the native buyer.
                                        if frontier and snapshot.ui.GetPlotPurchaseQuote(pid,city:GetID(),plot:GetIndex())==nil then
                                            stats.buyerBlocked=stats.buyerBlocked+1
                                            evaluation.details.reason='buyer_ambiguous'
                                            if activePlan(snapshot,city:GetID(),profile.district.Index,plot:GetIndex())then
                                                C.Withdraw(snapshot.planState,city:GetID(),profile.district.Index,plot:GetIndex(),'buyer_ambiguous')
                                            end
                                        else
                                            result[#result+1]={player=pid,city=city:GetID(),district=profile.district.Index,
                                                plot=plot:GetIndex(),delta=0,finalQ8=bid,economy=true,
                                                carried=evaluation.carried,publishedTurn=Game.GetCurrentGameTurn(),
                                                adjacency=quote and quote.adjacency or geometry.upper,
                                                economicQ8=quote and quote.valueQ8,preferenceQ8=quote and bid-quote.valueQ8,
                                                adjacencyPreferenceQ8=parts and parts.adjacencyQ8,materialPreferenceQ8=parts and parts.materialsQ8,
                                                layoutPreferenceQ8=parts and parts.layoutQ8,protectionPenaltyQ8=parts and parts.penaltyQ8,
                                                customerLayout=site and site.spatialPlan.links or{},
                                                startingAdjacency=site and site.startingAdjacency,startingGold=site and site.startingGold,
                                                quarterReadyEstimate=site and site.quarterReady,
                                                footprintWorkers=site and site.footprintWorkers,
                                                footprintSignature=site and site.footprintSignature,
                                                footprintCostMode=site and site.footprintCostMode,
                                                currentDisplacementQ8=evaluation.details.currentDisplacementQ8,
                                                -- Gross adjacency-Gold payback AFTER Quarter
                                                -- completion; not net profit or native saving ETA.
                                                startingGoldPaybackTurns=frontier and site and (site.startingGold or 0)>0
                                                    and invoice/site.startingGold or nil,
                                                baseCount=site and site.baseCount,specialtyCount=site and site.specialtyCount,
                                                capacityUsed=capacity and capacity.used,
                                                capacityAllowed=capacity and capacity.allowed,
                                                capacityPopulation=capacity and capacity.population,
                                                capacityState=capacityState,
                                                frontier=frontier,purchaseGold=frontier and invoice or nil}
                                            stats.final=stats.final+1
                                            stats.min=math.min(stats.min or bid,bid);stats.max=math.max(stats.max or bid,bid)
                                        end
                                    end
                                end
                            end
                        end
                    end
                end
            end
        end
    end
    -- Sparse positive bids plus a declared negative default own the WHOLE
    -- managed type. Weak, unknown, unavailable and newly founded-city options
    -- defer rather than inherit an untouched native building premium. This
    -- keeps packets small for future Quarters. Other district/material bids
    -- stay intact; no old additive Quarter score is mixed with whole values.
    for _,entry in ipairs(early)do if not managed[entry.district]then result[#result+1]=entry end end
    if snapshot.CustomerOptions then
        for _,offer in ipairs(E.CustomerOffers(snapshot,result,protectedPlots))do result[#result+1]=offer end
    end
    E.ReportWithdrawals(snapshot,result,evaluations,scopes,previous or{})
    -- Retain bounded candidate-surface evidence in ordinary main-mod logs:
    -- two leading sites per city/type, with economic and spatial components.
    -- Older winner-only captures cannot reconstruct the losing site margins.
    -- These are published proposals, never a receipt of native acceptance.
    local groups={}
    for _,entry in ipairs(result)do if entry.economy and not entry.carried then
        local key=entry.city..':'..entry.district
        local group=groups[key]or{};groups[key]=group
        group[#group+1]=entry
        table.sort(group,function(a,b)if a.finalQ8~=b.finalQ8 then return a.finalQ8>b.finalQ8 end;return a.plot<b.plot end)
        if #group>2 then group[3]=nil end
    end end
    local keys={};for key in pairs(groups)do keys[#keys+1]=key end;table.sort(keys)
    for _,key in ipairs(keys)do for rank,entry in ipairs(groups[key])do
        local first,second=entry.customerLayout[1],entry.customerLayout[2]
        print(string.format('CSC_AI_SPATIAL_BID turn=%d player=%d city=%d district=%d plot=%d rank=%d adjacency=%.3f economicQ8=%d adjacencyPreferenceQ8=%d materialPreferenceQ8=%d layoutPreferenceQ8=%d protectionPenaltyQ8=%d finalQ8=%d customerPlot1=%d customerType1=%d customerPlot2=%d customerType2=%d',
            Game.GetCurrentGameTurn(),pid,entry.city,entry.district,entry.plot,rank,entry.adjacency,
            entry.economicQ8,entry.adjacencyPreferenceQ8,entry.materialPreferenceQ8,
            entry.layoutPreferenceQ8,entry.protectionPenaltyQ8,entry.finalQ8,
            first and first.plot or -1,first and first.district or -1,
            second and second.plot or -1,second and second.district or -1))
    end end
    if snapshot.SpatialStats then
        local spatial=snapshot.SpatialStats()
        -- Havok's os.clock can be a constant zero. Mark it unavailable rather
        -- than claiming a measured zero-cost pass; host turn timings remain
        -- in the shared controller journal.
        local elapsed=started and clock()-started
        print(string.format('CSC_AI_SPATIAL_WORK turn=%d player=%d maps=%d adjacencyReads=%d unavailable=%d laggedReads=%d options=%d economyMs=%.3f',
            Game.GetCurrentGameTurn(),pid,spatial.maps,spatial.adjacencyReads,spatial.unavailable,spatial.laggedReads,spatial.options,
            elapsed and elapsed>0 and elapsed*1000 or -1))
    end
    return result,stats
end

function E.BuildingValue(snapshot,chain,building)
    local site=chain.economy or snapshot.Site(chain.city,chain.plot,chain.profile)
    return site and M.Marginal(site,building,snapshot.Price)
end

function E.SupplyValue(snapshot,chain,plot)
    local site=chain.economy or snapshot.Site(chain.city,chain.plot,chain.profile)
    if not site then return nil end
    -- Pricing is optional enrichment of the already qualified structural
    -- protection. A native quote fault must not abort the whole publication.
    local ok,full=pcall(M.Forecast,site,snapshot.Price);if not ok or not full then return nil end
    local alternative={};for k,v in pairs(site)do alternative[k]=v end
    alternative.suppliers={}
    for _,s in ipairs(site.suppliers)do if s.plot~=plot then alternative.suppliers[#alternative.suppliers+1]=s end end
    -- A new district removes the deposit as well as its transactions. Re-run
    -- the same rule counts/thresholds/multipliers for that physical loss; do
    -- not keep crediting the resource in the counterfactual's direct adjacency.
    local read,loss=pcall(snapshot.SupplyAdjacencyLoss,chain,plot)
    if not read or not loss then return nil end
    alternative.direct={}
    for _,flow in ipairs(site.direct)do
        local copy={};for k,v in pairs(flow)do copy[k]=v end
        if copy.id==copy.yield then copy.amount=copy.amount-(loss[copy.yield]or 0)end
        alternative.direct[#alternative.direct+1]=copy
    end
    local worked,without=pcall(M.Forecast,alternative,snapshot.Price)
    return worked and without and full.valueQ8-without.valueQ8
end
