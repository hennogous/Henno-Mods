-- Decision adapters for the central Quarter ledger. Site facts, transaction
-- amounts and prerequisite relationships belong to EconomyFacts/EconomyModel.
-- This module converts a ledger into a native bid, applies bounded placement
-- policy, and exposes the same marginal valuation to building/job consumers.
-- Native SQL customer adjacency, supplier protection and purchase/commitment
-- machinery remain separate consumers, not duplicate sources of income.
-- Quarter investments also price the shared world's marginal Services through
-- optional CE growth/pseudo-yield quotes. Customer placement remains ordinary
-- economics; its native overlap needs separate Service-aware qualification.
CSC_AI_EconomyAdapters={}
local E=CSC_AI_EconomyAdapters
local M=CSC_AI_EconomyModel
local F=CSC_AI_EconomyFacts
local C=CSC_AI_PlanContinuity
local planStates={}
local wonderCustomers
local wonderAuditMemory={}
-- Opt in on a frozen test package while we qualify the additional placement
-- cost through native comparison and check turn time on ordinary worlds.
E.AnchoredConnectionsEnabled=false
-- The matched campaign enables this on both packages. The control reads the
-- same eligible footprint facts and returns before pricing or changing bids.
E.AnchoredConnectionAuditEnabled=false
-- The matched layout experiment switches this without changing the package.
-- Once a footprint exists, the anchored calculation owns its link again.
E.ProspectiveConnectionsEnabled=false
-- Match the ceiling used for Stage 2 exchange orders in the shared building
-- packet. These are Q8 utility points in the native production comparison.
local LATER_BUILDING_CAP_Q8=64*256

function E.WonderOffers(player,chains,protectedPlots,limit,maxOfferQ8,canPlaceWonder,reservedPlots)
    -- The same generated sales catalogue feeds the Quarter forecast for
    -- completed Wonders. Here it identifies the individual Wonder building
    -- for CE's separate, native-legal plot comparison. Cache only definitions.
    if not wonderCustomers then
        wonderCustomers={}
        if GameInfo.CSC_QuarterWonderSales then
            for row in GameInfo.CSC_QuarterWonderSales()do
                local building=GameInfo.Buildings[row.BuildingType]
                if building and (building.IsWonder==true or building.IsWonder==1)then
                    local list=wonderCustomers[row.QuarterKey]or{}
                    list[#list+1]=building.Index;wonderCustomers[row.QuarterKey]=list
                end
            end
        end
    end
    local pid=player:GetID()
    local offers,seen={},{}
    local legalBySite,observed={},{}
    local prior=wonderAuditMemory[pid]or{}
    local function supplierLevel(materials)
        local level=0
        for _,material in ipairs(materials or{})do
            if material.working then return 2 end
            if material.ready then level=1 end
        end
        return level
    end
    for _,chain in ipairs(chains or{})do
        local mapped=wonderCustomers[chain.profile.key]
        local supply=chain.supply
        local base=supply and supplierLevel(supply.base)or 0
        local specialty=supply and supplierLevel(supply.specialty)or 0
        local anchor=chain.economy
        local considering=E.AnchoredConnectionsEnabled or E.AnchoredConnectionAuditEnabled
        local underway=considering and chain.complete==false and anchor
            and (anchor.quarterReady or math.huge)<anchor.horizon
        local ready=chain.ready or underway
        if mapped and ready and base>0 and specialty>0 then
            -- A Stage 4 Wonder chain needs both classes. A legal future
            -- supplier permits an offer. Each working class adds eight
            -- utility before CE's positive-row and proportional checks.
            local amount=(base+specialty-1)*8
            -- Older CE accepts at most 8 utility. Keep its packet valid.
            local deltaQ8=math.min(amount*256,maxOfferQ8)
            for _,plot in ipairs(Map.GetAdjacentPlots(chain.plot:GetX(),chain.plot:GetY()))do
                local index=plot:GetIndex()
                local city=plot:GetOwner()==pid and plot:GetDistrictType()==-1
                    and not protectedPlots[index] and Cities.GetPlotPurchaseCity(plot)
                if city and city:GetOwner()==pid then
                    for _,building in ipairs(mapped)do
                        if not city:GetBuildings():HasBuilding(building)then
                            local key=city:GetID()..':'..building..':'..index
                            local reserved=reservedPlots and reservedPlots[index]
                            if canPlaceWonder and not reserved and legalBySite[key]==nil then
                                local ok,legal=pcall(canPlaceWonder,pid,city:GetID(),building,index)
                                legalBySite[key]=ok and type(legal)=='boolean' and (legal and 'legal' or 'blocked')or 'unavailable'
                            end
                            if E.AnchoredConnectionAuditEnabled and legalBySite[key]=='legal' then
                                local definition=GameInfo.Buildings[building]
                                local id=chain.profile.key..':'..chain.plot:GetIndex()..':'..definition.BuildingType..':'..key
                                observed[id]=true
                                if not prior[id]then
                                    print(string.format('CSC_AI_WONDER_CONNECTION_OPPORTUNITY turn=%d player=%d order=quarterFirst quarter=%s anchor=%d building=%s city=%d plot=%d',
                                        Game.GetCurrentGameTurn(),pid,chain.profile.key,chain.plot:GetIndex(),definition.BuildingType,city:GetID(),index))
                                end
                            end
                            -- An unavailable UI read leaves CE's exact native
                            -- placement gate in charge. Known-impossible plots
                            -- cannot occupy the candidate's bounded offer list.
                            if (chain.ready or E.AnchoredConnectionsEnabled) and
                                (not E.AnchoredConnectionsEnabled or not reserved and legalBySite[key]~='blocked')then
                                local offer=seen[key]
                                if offer then offer.deltaQ8=math.max(offer.deltaQ8,deltaQ8)
                                else
                                    offer={player=pid,city=city:GetID(),building=building,plot=index,deltaQ8=deltaQ8}
                                    seen[key]=offer;offers[#offers+1]=offer
                                end
                            end
                        end
                    end
                end
            end
        end
    end
    if E.AnchoredConnectionAuditEnabled then wonderAuditMemory[pid]=observed end
    -- Overlapping Quarters retain one maximum offer. Trim weaker prospects
    -- first, with stable keys, so dense cities cannot fill the native packet.
    table.sort(offers,function(a,b)
        if a.deltaQ8~=b.deltaQ8 then return a.deltaQ8>b.deltaQ8 end
        if a.city~=b.city then return a.city<b.city end
        if a.building~=b.building then return a.building<b.building end
        return a.plot<b.plot
    end)
    for i=#offers,limit+1,-1 do offers[i]=nil end
    return offers
end

local propertyPrefix='CSC_AI_QuarterIntentV1_'
local layoutProperty='CSC_AI_PlannedLayoutsV1_'
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
        if E.ProspectiveConnectionsEnabled and type(Game.GetProperty)=='function' then
            planStates[pid].savedLayouts=Game:GetProperty(layoutProperty..pid)
        end
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
        if state.nextLayouts and type(Game.SetProperty)=='function' then
            -- This callback follows a successful CE publication. An aborted
            -- quote or rejected packet cannot replace last turn's shortlist.
            local layouts=C.EncodeLayouts(state.nextLayouts)
            if layouts~=state.savedLayouts then
                Game:SetProperty(layoutProperty..pid,layouts)
                state.savedLayouts=layouts
            end
            state.nextLayouts=nil
        end
        for _,event in ipairs(state.events)do
            print(string.format('CSC_AI_PLAN_EVENT turn=%d player=%d city=%d district=%d plot=%d kind=%s reason=%s valueQ8=%d forecastTurn=%d baselineWorkers=%s signature=%s',
                turn,pid,event.city,event.district,event.plot,event.kind,event.reason,event.valueQ8 or 0,event.forecastTurn or -1,
                tostring(event.baselineWorkers),tostring(event.signature)))
        end
        if state.eventsDropped>0 then print('CSC_AI_PLAN_EVENTS_OMITTED',turn,pid,state.eventsDropped)end
        state.events={};state.eventsDropped=0
    end end
end

function E.Available()
    if type(CE_AIEconomyStatus)~='function'or type(CE_AIDistrictScoresFinalEntry)~='function'
        or type(CE_AIDistrictScoresManagedType)~='function'or type(CE_AIDistrictScoresManagedReceipt)~='function'
        or type(CE_AIYieldIntervalValue)~='function'or type(CE_AIAmenityIntervalValue)~='function'
        or type(CE_AIYieldFixedValue)~='function'then
        return false,'CE economic interval-pricing/final-score API unavailable'
    end
    local ok,status=pcall(CE_AIEconomyStatus)
    if not ok or type(status)~='string'or not status:match('"pricingReady":1')
        or not status:match('"finalReady":1')then return false,'CE economic API is not qualified'end
    return true,nil,status
end

function E.Snapshot(player,placement,ui)
    local available,reason,status=E.Available();if not available then return nil,reason end
    -- Actual initialized engine parameters, including speed scaling. Older CE
    -- retains the previous explicit Online calibration; new APIs are adopted
    -- together so site costs and ready-time pricing share one context.
    local context
    if type(CE_AIEvaluationContext)=='function'and type(CE_AIDistrictSiteAdjustment)=='function'then
        local ok,raw=pcall(CE_AIEvaluationContext)
        if not ok or type(raw)~='string'then return nil,'Native evaluation context unavailable'end
        local function field(name)return tonumber(raw:match('"'..name..'":(%d+)'))end
        context={horizon=field('ordinaryHorizon'),discountQ8=field('discountQ8'),nativeSite=true}
        if not context.horizon or not context.discountQ8 then return nil,'Incomplete native evaluation context'end
    end
    if context and status and status:match('"servicePricingReady":1')
        and type(CE_AIPseudoYieldIntervalValue)=='function'and type(CE_AIGrowthIntervalValue)=='function'then
        -- Optional scalar consumers add no hooks. Older CE keeps the qualified
        -- ordinary economy, consistently excluding Services in both worlds.
        context.serviceKinds={GROWTH=true,PSEUDOYIELD=true,YIELD_PERCENT=true,NAVAL_PRODUCTION_PERCENT=true,HOUSING=true}
    end
    local snapshot=F.New(player,placement,ui,context)
    snapshot.evaluationContext=context or{horizon=50,discountQ8=4*256,nativeSite=false}
    local discount=snapshot.evaluationContext.discountQ8
    -- Interval APIs use a zero cumulative origin. Raw native Stream APIs treat
    -- turn zero as a fixed income amount, which can reject a valid 0..1 flow.
    -- Require the corrected contract above rather than silently changing the
    -- horizon or dropping short observed-route contributions. Quotes are cached
    -- only in this snapshot: native strategy and happiness can change next turn.
    local quotes={};local count=0
    local function rawPrice(stream,horizon,amount)
        local yield=stream.yield
        horizon=math.min(horizon,stream.finish or horizon)
        if stream.ready>=horizon then return 0 end
        local nativeGrowth=stream.service and yield=='GROWTH'
        if not nativeGrowth and(yield=='GROWTH'or yield=='NAVAL_PRODUCTION_PERCENT')then
            local city=snapshot.cities[stream.city]
            local base
            if city then
                if yield=='GROWTH'then base=city.foodSurplus else base=city.navalProduction end
            end
            if base==nil then return nil end
            -- A transparent utility proxy, not a gameplay Food/Production
            -- grant: +10% growth is valued as current surplus*10%, and naval
            -- Production requires observed eligible ship work. No whole-city
            -- +20% industrial output is invented for Dockmaster.
            amount=math.max(0,base)*amount/100
            yield=yield=='GROWTH'and'YIELD_FOOD'or'YIELD_PRODUCTION'
        end
        local units=amount>=0 and math.floor(amount*256+.5)or-math.floor(-amount*256+.5)
        local key=table.concat({stream.city,yield,stream.pseudoYield or'',units,stream.ready,horizon,tostring(stream.fixed==true),tostring(nativeGrowth==true)},':')
        if quotes[key]~=nil then return quotes[key]end
        local value
        if nativeGrowth then
            value=CE_AIGrowthIntervalValue(snapshot.id,stream.city,units,stream.ready,horizon,discount)
        elseif yield=='PSEUDOYIELD'then
            local definition=GameInfo.PseudoYields and GameInfo.PseudoYields[stream.pseudoYield]
            if definition and type(CE_AIPseudoYieldIntervalValue)=='function'then
                value=CE_AIPseudoYieldIntervalValue(snapshot.id,stream.city,definition.Index,units,stream.ready,horizon,discount)
            end
        elseif yield=='AMENITY'then
            value=CE_AIAmenityIntervalValue(snapshot.id,stream.city,amount,stream.ready,horizon,discount)
        else
            local definition=GameInfo.Yields[yield]
            if not definition then return nil end
            if stream.fixed then
                value=CE_AIYieldFixedValue(snapshot.id,stream.city,definition.Index,units,stream.ready,discount)
            else
                value=CE_AIYieldIntervalValue(snapshot.id,stream.city,definition.Index,units,stream.ready,horizon,discount)
            end
        end
        -- Unknown is not cached as zero and cannot produce a final replacement.
        -- Memoize only successful native Q8 quotes inside this publication.
        -- Costs/amenities use their own native routes; no yield is multiplied
        -- twice by its DefaultValue or the player's strategic preference.
        if type(value)=='number'or type(value)=='integer'then quotes[key]=value;count=count+1 end
        return value
    end
    snapshot.Price=function(stream,horizon)
        local raw=rawPrice(stream,horizon,stream.amount)
        if raw==nil then return nil end
        local depth=stream.forecastDepth or 0
        if stream.service or not context or depth<=0 or stream.amount<=0 or stream.yield=='AMENITY'or stream.fixed then return raw,raw end
        -- GameCore BuildingValue weights an early building-income subtotal by
        -- 1+2d, then deducts upkeep and discounts it. CSC maps its missing
        -- producer's ordinary exchange income to that effective-income slot.
        -- This mapping is our bidding policy: native's modifier interpreter
        -- does not apply this multiplier to every CSC modifier automatically.
        -- Actual ledger amounts/valueQ8 remain unchanged. Missing customers,
        -- unknown unlocks and out-of-window benefits still earn nothing.
        local bid=rawPrice(stream,horizon,stream.amount*(1+2*depth))
        if bid==nil then return nil end
        return raw,bid
    end
    local worldQuotes={}
    local worldStats={worlds=0,evaluations=0,budgetFailures=0,unknown=0,cacheHits=0}
    snapshot.WorldStats=function()
        local routes=snapshot.TradeCacheStats and snapshot.TradeCacheStats()or{}
        worldStats.routeHits=routes.hits or 0;worldStats.routeMisses=routes.misses or 0
        worldStats.routeEntries=routes.entries or 0;worldStats.routeOverflow=routes.overflow or 0
        return worldStats
    end
    snapshot.WorldQuote=function(world)
        -- Fact worlds and this Price function are immutable for one publication.
        -- Share the ordinary baseline and repeated references across adapters;
        -- no stale native weights, route counters or construction times survive.
        if worldQuotes[world]then worldStats.cacheHits=worldStats.cacheHits+1;return worldQuotes[world]end
        worldStats.worlds=worldStats.worlds+1
        local planWorld=world
        if world.baselineWorld then
            local baseline,problem=snapshot.WorldQuote(world.baselineWorld)
            if not baseline then return nil,problem end
            -- Freeze only unrelated discrete choices around the common plan.
            -- Every trial still schedules/prices every chain, so shared queues,
            -- rounded returns and route losses respond to the candidate.
            planWorld={};for k,v in pairs(world)do planWorld[k]=v end
            planWorld.baselinePlan=baseline.plan
        end
        local value,problem=M.JointForecast(planWorld,snapshot.Price)
        if value then
            worldQuotes[world]=value;worldStats.evaluations=worldStats.evaluations+(value.evaluations or 0)
        elseif type(problem)=='string'and problem:find('budget',1,true)then
            worldStats.budgetFailures=worldStats.budgetFailures+1
        else worldStats.unknown=worldStats.unknown+1 end
        return value,problem
    end
    local customerNative={}
    snapshot.CustomerNetValue=function(cityID,district,plotIndex,ready)
        local key=cityID..':'..district..':'..plotIndex..':'..ready
        if customerNative[key]~=nil then return customerNative[key]or nil end
        local plot=Map.GetPlotByIndex(plotIndex)
        local value
        if context and plot then
            local ok,raw=pcall(CE_AIDistrictSiteAdjustment,snapshot.id,cityID,district,
                plot:GetX(),plot:GetY(),ready,context.horizon,discount)
            value=ok and type(raw)=='string'and tonumber(raw:match('"netQ8":(-?%d+)'))or nil
        end
        customerNative[key]=value or false;return value
    end
    if context and type(snapshot.Site)=='function'then
        local readSite=snapshot.Site
        snapshot.Site=function(...)
            local site,message=readSite(...)
            if site and not site.comparisonReferenceQ8 then
                -- Scale a location preference for actual construction delay.
                -- The empirical reference includes ordinary construction; use
                -- one fifth of its horizon as that reference delay. A site
                -- ready near the horizon cannot earn a full spatial premium.
                -- Two unit-stream quotes share the existing per-city cache.
                local referenceReady=math.floor(site.horizon/5)
                local unit={city=site.city,yield='YIELD_PRODUCTION',amount=1,ready=referenceReady}
                local normal=rawPrice(unit,site.horizon,1)
                unit.ready=site.quarterReady
                local current=rawPrice(unit,site.horizon,1)
                if normal and normal>0 and current then
                    -- Publish the two cached facts atomically. A failed unit
                    -- quote must not leave a reference with a fabricated1.0
                    -- readiness on the next read of this cached site.
                    site.sitingReadiness=math.min(1.25,math.max(0,current/normal))
                    site.comparisonReferenceQ8=E.NativeInvestmentReference(Game.GetCurrentGameTurn(),site.horizon)
                else return nil,'Siting readiness quote unavailable'end
            end
            return site,message
        end
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
-- not additional gameplay adjacency. Qualified native context uses the smooth
-- control-district reference and quality caps below. Older CE retains its
-- previous48/144/288/432/576 utility bands explicitly. Both material classes
-- add64; extra Base/Spec deposits add24/16 each, capped at two extras.
-- Prospective customer terrain adds at most96 in total; actual transactions
-- still require completed customer districts in the economic ledger.
-- They do not make an otherwise losing investment profitable or guarantee it
-- beats another district/unit. Below+2 and no-Base sites defer, except Tailors
-- at+1 beside a completed Harbor. That exception opens eligibility only; it
-- does not invent a Service payout or bypass positive economics/protection.
-- Managed CE types withhold nonpositive options from fresh proposals because
-- vanilla GetBestDistrict can otherwise select the least-negative candidate.
E.DeferredQuarterQ8=-1024*256
-- Both the inexpensive geometry screen and the final economic alternative
-- use this floor. A stale pre-screen must not silently discard eligible +2
-- sites before their complete-value quote reaches the publication packet.
E.MinimumAdjacency=2
E.MinimumSitingBonusQ8=48*256
local MINIMUM_SITING_REFERENCE_FRACTION=.08

function E.PlacementMinimumAdjacency(facts)
    -- Shared by cheap geometry, full quotes and continuity grace. The live
    -- facts reader supplies an owned completed Harbor plot, not future space.
    -- Missing evidence keeps the normal floor; loss/capture is reconsidered
    -- on the next publication. Base supply remains a separate mandatory gate.
    if facts and facts.quarterKey=='TAILORS'and type(facts.completedHarborPlot)=='number'
        and facts.completedHarborPlot>=0 then return 1 end
    return E.MinimumAdjacency
end

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
    for _,source in ipairs(options or{})do if not source.purchaseGold then
        local option={};for k,v in pairs(source)do option[k]=v end
        option.preference=math.max(0,16+8*math.min(4,option.adjacency)
            -8*math.min(4,math.max(0,option.bestAdjacency-option.adjacency))
            -8*math.min(4,math.max(0,option.displacedAdjacency-option.adjacency)))
        local group=families[option.family]or{};families[option.family]=group
        group[#group+1]=option;table.sort(group,better)
        if #group>2 then group[3]=nil end
    end end
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

function E.StrongQuarterLayout(site,options,reserved,pairedPlanning,partnerRank)
    -- Recognise a supply-backed layout before either district exists. Count
    -- usable plots, not resource tags. A live reservation can consume a
    -- deposit before this Quarter uses it. Two Base plots can support earlier
    -- stages, while Stage 4 needs a distinct Specialty source.
    local base,specialty={},{}
    for _,supplier in ipairs(site.suppliers or{})do
        if supplier.ready<site.horizon and not reserved[supplier.plot]then
            if supplier.kind=='base'then base[supplier.plot]=true
            elseif supplier.kind=='specialty'then specialty[supplier.plot]=true end
        end
    end
    local firstBase=next(base)
    if not firstBase then return nil end
    local firstSpec=next(specialty)
    local extraBase=next(base,firstBase)~=nil
    local hasSpec=firstSpec~=nil and (firstSpec~=firstBase or next(specialty,firstSpec)~=nil or extraBase)
    local strongSupply=extraBase or hasSpec
    if not strongSupply and not pairedPlanning then return nil end

    local bestByState={}
    local function consider(option,stage,existing)
        -- Rank established and unbuilt customers separately. The site bid
        -- still prefers an established link. The prospective quote can then
        -- price what a second, unbuilt customer adds to that same site.
        if not stage or stage==4 and not hasSpec then return end
        local candidate={plot=option.plot,city=option.city,district=option.district,stage=stage,
            existing=existing,adjacency=option.adjacency or 0,extraBase=extraBase,hasSpec=hasSpec,
            purchaseGold=option.purchaseGold}
        if pairedPlanning and not existing and partnerRank then
            candidate.rank,candidate.gain,candidate.customerYields,candidate.customerGain=partnerRank(option,stage)
            if not candidate.rank then return end
        end
        if stage==0 then candidate.role='provider' end
        local best=bestByState[existing]
        if best then
            if candidate.rank~=best.rank then
                if candidate.rank<best.rank then return end
            elseif stage~=best.stage then
                -- Equal returns favour the first seller with a buyer. A
                -- provider supplies the Quarter and has no seller stage of
                -- its own. In a tie give the transaction partner precedence.
                if pairedPlanning then
                    if stage==0 or (best.stage~=0 and stage>best.stage) then return end
                elseif stage<best.stage then return end
            elseif candidate.adjacency~=best.adjacency then
                if candidate.adjacency<best.adjacency then return end
            elseif candidate.plot~=best.plot then
                if candidate.plot>best.plot then return end
            elseif (candidate.district or -1)>=(best.district or -1)then return end
        end
        bestByState[existing]=candidate
    end
    for _,venue in ipairs(site.customers or{})do
        if venue.transaction and venue.transaction.spatial=='ADJACENT_OWNED' and not venue.excluded then
            consider(venue,venue.stage,true)
        end
    end
    for _,option in ipairs(options)do
        -- Apply the extra preference to a customer that can already match
        -- its city's other sites on ordinary adjacency. Some spatial links
        -- are providers only and have no compatible customer stage.
        if pairedPlanning and partnerRank then
            for stage=2,4 do
                if option.stages and option.stages[stage] then consider(option,stage,false) end
            end
            if option.goodsProvider then consider(option,0,false) end
        elseif option.stages and option.adjacency>=math.max(option.bestAdjacency,option.displacedAdjacency)then
            for stage=4,2,-1 do if option.stages[stage] and(stage<4 or hasSpec)then
                consider(option,stage,false);break
            end end
        end
    end
    return strongSupply and (bestByState[true]or bestByState[false]) or nil,bestByState[false]
end

-- Both the siting preference and the economic quote use the same two-district
-- schedule. A shared city can build the Quarter while it researches its
-- customer. Separate cities can work in parallel. The second return value
-- fixes the Quarter completion date only when that city builds it first.
local function connectionSchedule(snapshot,site,layout)
    local ready,unlock,turns=snapshot.ProspectiveCustomerReady(layout.city,layout.district)
    if not ready or site.quarterReady>=site.horizon then return nil end
    local work=site.quarterWork
    if layout.city==site.city and work and unlock and turns then
        local queue=site.queueReady and site.queueReady[site.city]or 0
        local firstQuarter=math.max(queue,work.unlock)+work.turns
        local lastCustomer=math.max(firstQuarter,unlock)+turns
        ready=math.max(queue,unlock)+turns
        local lastQuarter=math.max(ready,work.unlock)+work.turns
        if lastCustomer<lastQuarter then
            return lastCustomer,firstQuarter,lastCustomer
        end
        return ready,nil,lastQuarter
    end
    return ready,nil,math.max(ready,site.quarterReady)
end

local function hasSlotsForBoth(snapshot,quarter,customer)
    if not snapshot.DistrictCapacity then return false end
    local required={}
    for _,option in ipairs({quarter,customer})do
        local definition=GameInfo.Districts[option.district]
        if not definition or definition.RequiresPopulation==nil then return false end
        if definition.RequiresPopulation==true or definition.RequiresPopulation==1 then
            required[option.city]=(required[option.city]or 0)+1
        end
    end
    for city,count in pairs(required)do
        local host=snapshot.cities[city]
        local slots=host and snapshot.DistrictCapacity(host.object)
        if not slots or not slots.known or slots.allowed-slots.used<count then return false end
    end
    return true
end

local function forecastPairedAdjacency(snapshot,site,city,plot,profile,partner)
    -- This is a siting preference for one named adjacent district. Cash flows
    -- remain in projectedLinkValue. Counting the hypothetical neighbour as
    -- current income here would charge its value again in that quote.
    if not (partner and snapshot.ProjectedConnectionYields and snapshot.ProspectiveCustomerReady) then return end
    local _,_,bothReady=connectionSchedule(snapshot,site,partner)
    if not bothReady or bothReady>=site.horizon then return end
    local quarter={city=city:GetID(),district=profile.district.Index}
    if not hasSlotsForBoth(snapshot,quarter,partner) then return end
    local gain=partner.gain
    if gain==nil then
        local yields=snapshot.ProjectedConnectionYields({city=city,plot=plot,profile=profile},partner.district,partner.plot,partner.purchaseGold)
        if not yields then return end
        gain=(yields.YIELD_GOLD or 0)+(yields.YIELD_PRODUCTION or 0)
    end
    if gain<=0 then return end
    site.pairAdjacencyGain=gain
    site.pairReady=bothReady
end

local function rankPartners(snapshot,site,city,plot,profile)
    if not (snapshot.CustomerStageSchedule and snapshot.ProjectedConnectionYields) then return nil end
    local sellerReady={}
    local function completion(building,start)
        if not building or building.excluded then return math.huge end
        if building.working then return start end
        return math.max(start,building.unlock or math.huge)+(building.turns or math.huge)
    end
    for _,producer in ipairs(site.seconds or {}) do
        sellerReady[2]=math.min(sellerReady[2] or math.huge,completion(producer,site.quarterReady))
    end
    sellerReady[3]=completion(site.third,sellerReady[2] or math.huge)
    -- Both later sellers depend on Stage 2 in the shared ledger. Either
    -- can be the next investment when the other has a distant unlock.
    sellerReady[4]=completion(site.fourth,sellerReady[2] or math.huge)
    local chain={city=city,plot=plot,profile=profile}
    local gains,customerYields={},{ }
    return function(option,stage)
        local _,_,both=connectionSchedule(snapshot,site,option)
        if not both or both>=site.horizon then return nil end
        if gains[option]==nil then
            local amounts=snapshot.ProjectedConnectionYields(chain,option.district,option.plot,option.purchaseGold)
            gains[option]=amounts and ((amounts.YIELD_PRODUCTION or 0)+(amounts.YIELD_GOLD or 0)) or false
            customerYields[option]=snapshot.CustomerAdjacencyChange and
                snapshot.CustomerAdjacencyChange(profile,option.district,option.plot,plot:GetIndex()) or {}
        end
        local gain=gains[option]
        if not gain or (stage==0 and gain<=0) then return nil end
        local elsewhere=math.max(option.bestAdjacency,option.displacedAdjacency)
        local customerGain=0
        for _,amount in pairs(customerYields[option]) do customerGain=customerGain+amount end
        local customerWithQuarter=option.adjacency+customerGain
        if customerWithQuarter+gain<elsewhere then return nil end
        -- Rank in rough yield-turns solely to choose the partner for a full
        -- quote. Credit the district's own terrain and the supported Quarter
        -- gain, less adjacency sacrificed elsewhere. A transaction gets one
        -- additional point for each turn both buildings could operate. The
        -- native bid later uses the actual economic terms and shared queue.
        local score=(site.horizon-both)*(customerWithQuarter+gain-math.max(0,elsewhere-customerWithQuarter))
        if stage>0 then
            local buyer=snapshot.CustomerStageSchedule(profile,option.city,option.district,option.plot)[stage]
            local ready=math.max(both,buyer or math.huge,sellerReady[stage] or math.huge)
            score=score+math.max(0,site.horizon-ready)
        end
        -- Approximate yield-turns are used for shortlisting only. Subtract
        -- the full customer invoice here so a comparable owned site wins.
        -- The later native Q8 comparison prices the same Gold in its units.
        score=score-(option.purchaseGold or 0)
        if score<=0 then return nil end
        return score,gain,customerYields[option],customerGain
    end
end

function E.NativeInvestmentReference(turn,horizon)
    -- Native-control medians, not a new gameplay yield or universal native
    -- formula. The three-map exact+2 Campus/Hub/Theater samples anchor ordinary
    -- investment near600/1200/2100 Q8-utility points in Online early/mid/late
    -- periods. Smooth interpolation avoids abrupt bid jumps during a retained
    -- request. Scale the clock by the actual native horizon for other speeds.
    local online=turn*50/horizon
    local value
    if online<=38 then value=600
    elseif online<=113 then value=600+(online-38)*600/75
    elseif online<200 then value=1200+(online-113)*900/87
    else value=2100 end
    -- Income utility also grows with the native time horizon. Keep the Online
    -- reference in proportion when the engine supplies Standard/longer speed.
    -- Live calibration remains Online; CE's overall score ceiling still bounds
    -- the resulting bids on every speed.
    return math.floor(value*256*horizon/50+.5)
end

function E.PlacementValue(quote,site,protectionQ8,coversOwnMaterial)
    local qualifyingAdjacency=quote.adjacency+(site.pairAdjacencyGain or 0)
    if qualifyingAdjacency+1e-6<E.PlacementMinimumAdjacency(site) or (site.baseCount or 0)<1 then return E.DeferredQuarterQ8,'quality'end
    -- Only named supply loss enters the complete ledger. Old no-host/readiness
    -- heuristics were ownership-dependent and duplicated its own valuation.
    -- Missing customer space loses its current layout preference/income; it
    -- does not acquire a hidden128-utility penalty when land becomes owned.
    -- Joint worlds already remove the displaced supplier's transactions,
    -- adjacency and route contribution. Keep the explicit material-covering
    -- policy floor, but do not debit that same economic SupplyValue again.
    local penalty=site.jointEconomy and 0 or math.max(0,protectionQ8 or 0)
    if coversOwnMaterial then penalty=math.max(penalty,256*256)end
    local economic=quote.valueQ8-penalty
    if economic<=0 then return economic,'economics'end
    local value=(quote.bidValueQ8 or quote.valueQ8)-penalty
    local premium
    local reference=site.comparisonReferenceQ8
    -- An admitted +1 Harbor/Tailors uses the minimum siting band and the same
    -- weak-site cap as +2. Keep the real +1 in the ledger/logs; extrapolating
    -- the +2..+3 formula backwards would create a negative preference. This
    -- exception adds no automatic Dockmaster income. Only separately admitted
    -- gameplay Service attachments can earn that value; total economics must
    -- still be positive. Stronger Quarters retain their usual siting bands.
    local sitingAdjacency=math.max(E.MinimumAdjacency,qualifyingAdjacency)
    if reference then
        -- Spatial policy, kept separate from actual economic income. At the
        -- early600 reference, +2/+3/+4 preferences are48/240/600. Strong +4
        -- quarters with positive economics can beat typical +2 native bids;
        -- +2 sites retain a useful offer but cannot inflate into top-tier bids
        -- merely from a later generic amenity forecast. Actual native units,
        -- timing, material losses and production competition stay in force.
        local adjacency=math.min(6,sitingAdjacency)
        local fraction=adjacency<3 and(MINIMUM_SITING_REFERENCE_FRACTION+.32*(adjacency-2))or(.4+.6*(adjacency-3))
        premium=reference*fraction*(site.sitingReadiness or 1)
    elseif sitingAdjacency<3 then
        -- Fractional adjacency can arise through yield multipliers. Interpolate
        -- 48->144 between +2/+3 rather than introducing a jump at the boundary.
        premium=E.MinimumSitingBonusQ8+(sitingAdjacency-2)*(144*256-E.MinimumSitingBonusQ8)
    else
        premium=math.min(4,sitingAdjacency-2)*144*256
    end
    local materials=math.min(2,math.max(0,(site.baseCount or 0)-1))*24
    if (site.specialtyCount or 0)>0 then
        materials=materials+64+math.min(2,site.specialtyCount-1)*16
    end
    local layout=site.spatialPlan and site.spatialPlan.preference or 0
    local service=quote.serviceValueQ8 or 0
    local spatial=premium+(materials+layout)*256
    -- The quoted bid already includes this signed land subtotal and the
    -- local protection charge. Cap the forecast before reapplying both
    -- exactly once. Otherwise two capped sites look equally good even when
    -- only one requires a purchase or removes a working improvement.
    local footprint=(quote.footprintBidQ8 or quote.siteAdjustmentQ8 or 0)-penalty
    local ordinary=value-service-footprint
    local strongLayout=site.strongLayout and qualifyingAdjacency>=E.MinimumAdjacency
    -- The adjacency-based ceiling was calibrated against ordinary future
    -- income/amenities. A strong layout has usable supply and a competitive
    -- mapped customer footprint. Keep its already-priced spatial preference
    -- outside that forecast ceiling. Less certain layouts retain the existing
    -- combined ceiling so projected income cannot make a middling site win.
    -- Service utility enters once, after either path.
    local ordinaryBid=ordinary+spatial
    local proposed=ordinaryBid
    local qualityCap
    if reference then
        local extra=math.max(0,math.min(4,sitingAdjacency-2))
        qualityCap=reference*(.5+.65*math.min(1,extra)+.6*math.max(0,extra-1))
        ordinaryBid=math.min(ordinaryBid,qualityCap)
        proposed=strongLayout and math.min(ordinary,qualityCap)+spatial or ordinaryBid
    end
    proposed=proposed+service+footprint
    -- The ordinary forecast cap still limits projected income. A concrete
    -- competitive customer layout with redundant or diverse supply receives
    -- separate spatial credit of 12% of the normal district reference at +2,
    -- rising to 20% at +3. Scale with ordinary opportunities, up to 256 native
    -- utility. The lower +1 Harbor exception keeps its usual bid.
    local limit=4096*256
    local bid=math.floor(math.max(-limit,math.min(limit,proposed))+.5)
    local layoutCredit=0
    if strongLayout and reference then
        local fraction=math.min(.20,.12+.08*(qualifyingAdjacency-E.MinimumAdjacency))
        layoutCredit=math.min(256*256,math.floor(reference*fraction+.5),limit-bid)
    end
    bid=bid+layoutCredit
    return bid,'positive',{adjacencyQ8=math.floor(premium+.5),materialsQ8=materials*256,
        layoutQ8=layout*256,strongLayoutQ8=layoutCredit,strongLayout=strongLayout and site.strongLayout,
        -- Grace retains the ordinary score. Both forms of fresh strong-layout
        -- credit require rechecking the suppliers and customer footprint.
        ordinaryBidQ8=site.pairAdjacencyGain and 0 or math.floor(math.max(-limit,math.min(limit,ordinaryBid+service+footprint))+.5),
        penaltyQ8=penalty,forecastQ8=(quote.bidValueQ8 or quote.valueQ8)-quote.valueQ8,
        qualityCapQ8=qualityCap and math.floor(qualityCap+.5),serviceQ8=service,
        capAdjustmentQ8=bid-value-math.floor(premium+.5)-(materials+layout)*256-layoutCredit}
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
    for id,plan in pairs(state.plans)do
        -- A sole exact Quarter intent may use its own planned footprint.
        -- True marks a conflict between intents and fences it for every bid.
        snapshot.intentFootprints[plan.plot]=snapshot.intentFootprints[plan.plot] and true or id
    end
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

function E.QuarterForecast(snapshot,city,plot,profile,site,protectionQ8,covers)
    if not snapshot.QuarterWorld or not snapshot.WorldQuote then
        return M.Forecast(site,snapshot.Price,function(q)return E.PlacementValue(q,site,protectionQ8,covers)end)
    end
    local before,after=snapshot.QuarterWorld(city,plot,profile,site)
    if not before then return nil,after end
    if next(snapshot.serviceKinds or{})then
        -- Ordinary customer worlds deliberately retain their old baseline.
        -- Clone WORLD identities, not records, so enabling Services for Quarter
        -- investment cannot mutate a cached ordinary customer comparison. Both
        -- Service arms share the same pricing mode and active income cancels.
        snapshot.serviceWorlds=snapshot.serviceWorlds or{}
        local source=before
        if not snapshot.serviceWorlds[source]then
            -- These two modes price exactly the same physical baseline. Reuse
            -- at most16 unpriced plan ledgers; still optimize each objective
            -- independently. Candidate worlds never inherit this baseline memo.
            if not source.evaluationMemo then
                source.ledgerMemoToken={}
                source.evaluationMemo={token=source.ledgerMemoToken,entries={},count=0,hits=0}
            end
            local value={};for k,v in pairs(source)do value[k]=v end
            value.includeServices=true;snapshot.serviceWorlds[source]=value
        end
        before=snapshot.serviceWorlds[source]
        local value={};for k,v in pairs(after)do value[k]=v end
        value.includeServices=true;value.baselineWorld=before
        value.evaluationMemo=nil;value.ledgerMemoToken=nil;after=value
    end
    local baseline,problem=snapshot.WorldQuote(before)
    if not baseline then return nil,problem end
    site.jointEconomy=true
    local function marginal(result)
        local stages=result.chainStages[site.key]
        local terrain=0
        for _,second in ipairs(site.seconds or{})do if stages and second.type==stages.second then terrain=second.terrain or 0 end end
        local streams,premium={},0
        local prefix=site.key..'/'
        for _,flow in ipairs(result.streams)do if flow.id:sub(1,#prefix)==prefix then
            local copy={};for k,v in pairs(flow)do copy[k]=v end
            copy.id=flow.id:sub(#prefix+1);streams[#streams+1]=copy
            premium=premium+(flow.bidValueQ8 or flow.valueQ8)-flow.valueQ8
        end end
        -- Only the new Quarter receives its stock-style building-depth premium.
        -- Reweighting unrelated existing plans cannot become free new-Quarter
        -- value. Shared/pooled effects still enter once at their raw marginal.
        local raw=result.valueQ8-baseline.valueQ8
        return{valueQ8=raw,bidValueQ8=raw+premium,
            adjacency=(site.adjacency or 0)+terrain,streams=streams,omissions=result.omissions,
            siteAdjustmentQ8=result.siteAdjustmentQ8-baseline.siteAdjustmentQ8,
            footprintBidQ8=(result.footprintBidQ8 or result.siteAdjustmentQ8)
                -(baseline.footprintBidQ8 or baseline.siteAdjustmentQ8),
            forecastAdjustmentQ8=premium,jointEconomy=true,
            affectedChains=result.affectedChains,jointEvaluations=result.evaluations,servicesExcluded=result.servicesExcluded,
            serviceValueQ8=(result.serviceValueQ8 or 0)-(baseline.serviceValueQ8 or 0),serviceStreams=result.serviceStreams or 0,
            second=stages and stages.second}
    end
    after.objective=function(result)return E.PlacementValue(marginal(result),site,protectionQ8,covers)end
    local result,error=snapshot.WorldQuote(after)
    if not result then return nil,error end
    local quote=marginal(result)
    -- The whole new Quarter owns its marginal bid. Existing-chain income,
    -- shared buildings/rounding and current route income cancel against the
    -- common baseline; the footprint's losses and import-blocking flag remain.
    -- Native site costs enter once through the new site's existing accounting.
    print(string.format('CSC_AI_QUARTER_WORLD turn=%d player=%d city=%d district=%d plot=%d chains=%d evaluations=%d beforeQ8=%d afterQ8=%d marginalQ8=%d bidQ8=%d serviceQ8=%d',
        Game.GetCurrentGameTurn(),snapshot.id,city:GetID(),profile.district.Index,plot:GetIndex(),
        result.affectedChains,result.evaluations,baseline.valueQ8,result.valueQ8,quote.valueQ8,quote.bidValueQ8,quote.serviceValueQ8 or 0))
    return quote
end

function E.QuotePlacement(snapshot,city,plot,profile,geometry,frontier,invoice,protectionQ8,ignoredLegacy,covers,protected,screenedOptions)
    local plan=activePlan(snapshot,city:GetID(),profile.district.Index,plot:GetIndex())
    local state=snapshot.planState
    local facts,reason=snapshot.Site(city,plot,profile)
    local details={reason='unknown',legacyIgnoredQ8=ignoredLegacy or 0,protectionQ8=protectionQ8 or 0,
        owner=plot:GetOwner(),adjacency=geometry.upper,invoice=invoice}
    local site,quote,parts,bid
    if facts then
        site=C and C.PrepareSite(plan,facts)or{}
        if not C then for k,v in pairs(facts)do site[k]=v end;site.footprintCostMode='current'end
        -- The native site residual already includes the native land invoice
        -- on a frontier footprint. Keep the UI invoice for affordability and
        -- ownership diagnostics, but do not charge a second Gold payment.
        site.purchaseGold=site.nativeSiteIncludesPurchase and 0 or invoice
        if site.nativeSiteAdjustmentQ8~=nil then site.footprintCostMode='native_site'end
        local options=screenedOptions or snapshot.CustomerOptions
            and snapshot.CustomerOptions(city,plot,profile,protected,E.AnchoredConnectionsEnabled,E.ProspectiveConnectionsEnabled)or{}
        site.spatialPlan=E.SpatialPlan(options)
        if E.AnchoredConnectionsEnabled then
            local rank=E.ProspectiveConnectionsEnabled and rankPartners(snapshot,site,city,plot,profile)
            site.strongLayout,site.prospectiveLayout=E.StrongQuarterLayout(site,options,snapshot.intentFootprints or{},E.ProspectiveConnectionsEnabled,rank)
            if E.ProspectiveConnectionsEnabled and site.prospectiveLayout then
                site.prospectiveCustomers=options
                forecastPairedAdjacency(snapshot,site,city,plot,profile,site.prospectiveLayout)
            end
        end
        -- The legacy single-chain Stage2 estimate must not stack with the new
        -- attachment-driven joint Service ledger. Copy the cached site so
        -- building/repair marginals retain their narrow existing Stage2 input;
        -- joint Quarter worlds use site.services when qualified CE is present.
        local transactionSite={};for k,v in pairs(site)do transactionSite[k]=v end
        transactionSite.service=nil
        local ok,value,message=pcall(E.QuarterForecast,snapshot,city,plot,profile,transactionSite,protectionQ8,covers)
        if ok then quote,reason=value,message else reason=tostring(value)end
        if quote then
            site.jointEconomy=quote.jointEconomy==true
            bid,details.reason,parts=E.PlacementValue(quote,site,protectionQ8,covers)
            details.economicQ8=quote.valueQ8;details.afterProtectionQ8=quote.valueQ8-(parts and parts.penaltyQ8 or math.max(protectionQ8 or 0,covers and 256*256 or 0))
            details.forecastAdjustmentQ8=quote.forecastAdjustmentQ8 or 0
            details.serviceQ8=quote.serviceValueQ8 or 0
            details.nativeSiteAdjustmentQ8=site.nativeSiteAdjustmentQ8
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
        local safe=not frontier and supply and #supply.base>0 and geometry.upper>=E.PlacementMinimumAdjacency(geometry)
            and not covers and (protectionQ8 or 0)==0 and not protected[plot:GetIndex()]
            and signature==plan.signature
        local carried=C.Grace(state,plan,details.reason,safe)
        if carried then details.reason='grace';return{bid=carried,carried=true,details=details,plan=plan}end
    end
    if C and plan then C.Withdraw(state,plan.city,plan.district,plan.plot,details.reason)end
    return {details=details,quote=quote,site=site}
end

function E.CustomerFirstPreference(option)
    -- Preparation policy, not forecast income: 8 utility for an actual Base
    -- deposit, +2 for each of at most two extra Base deposits, +4 for Spec.
    -- Harbor preparation for Tailors adds8:16..24 per supplier city/type.
    -- This bounded siting preference is deliberately separate from Service
    -- income: eligible ship output, unlock timing and era are not assumed.
    -- The facts come from reverse gameplay edges and loaded district families,
    -- so unique Harbors qualify without another authored relationship list.
    -- Require the best measured ordinary adjacency before adding any bonus;
    -- this cannot compensate for sacrificing native adjacency elsewhere.
    -- Other native site costs/forecasts still compete with this small delta.
    local base=option and tonumber(option.baseCount)
    local spec=option and tonumber(option.specialtyCount)
    local adjacency=option and tonumber(option.adjacency)
    local best=option and tonumber(option.bestAdjacency)
    if not base or not spec or not adjacency or not best
        or base<1 or spec<0 or base%1~=0 or spec%1~=0
        or adjacency~=adjacency or best~=best or math.abs(adjacency)==math.huge or math.abs(best)==math.huge
        or adjacency+1e-6<best then return 0 end
    local preference=math.min(16,8+2*math.min(2,base-1)+(spec>0 and 4 or 0))
    if option.quarterKey=='TAILORS'and option.customerFamily=='DISTRICT_HARBOR'then preference=preference+8 end
    -- Both directions now point to the exact same shortlisted layout. Use the
    -- existing capped customer-side placement preference. The positive native
    -- customer site still has to compete on its ordinary placement score.
    if option.strongLayout then preference=preference+16 end
    return preference
end

function E.CustomerFirstPlan(options,quarterClaims,customerClaims)
    -- Match supplier (city,Quarter type) groups to distinct adjacent plots.
    -- One group contributes once even if several sites fit; shared material
    -- deposits do NOT consume a slot in this matching and may feed multiple
    -- different Quarters. There are at most six adjacent Quarter footprints:
    -- a64-state mask DP finds the best compatible combination without an
    -- exponential search over Quarter types. All inputs are snapshot facts.
    local groups,plotSet={},{}
    for _,option in ipairs(options)do
        local preference=E.CustomerFirstPreference(option)
        if preference>0 and not customerClaims[option.quarterPlot]
            and(not quarterClaims[option.quarterPlot]or quarterClaims[option.quarterPlot]==option.quarterDistrict)then
            local key=option.quarterCity..':'..option.quarterDistrict
            local group=groups[key]or{};groups[key]=group
            group[#group+1]={option=option,preference=preference};plotSet[option.quarterPlot]=true
        end
    end
    local plots,keys={},{}
    for plot in pairs(plotSet)do plots[#plots+1]=plot end;table.sort(plots)
    for key in pairs(groups)do keys[#keys+1]=key end;table.sort(keys)
    if #plots>6 then return{preference=0,rawPreference=0,links={}}end -- malformed geometry: no invented match
    local bits={};for i,plot in ipairs(plots)do bits[plot]=2^(i-1)end
    local states={[0]={value=0}}
    for _,key in ipairs(keys)do
        local nextStates={};for mask,state in pairs(states)do nextStates[mask]=state end
        local group=groups[key];table.sort(group,function(a,b)return a.option.quarterPlot<b.option.quarterPlot end)
        for mask=0,2^#plots-1 do local state=states[mask]
            if state then for _,choice in ipairs(group)do
                local bit=bits[choice.option.quarterPlot]
                if math.floor(mask/bit)%2==0 then
                    local target=mask+bit;local value=state.value+choice.preference
                    if not nextStates[target]or value>nextStates[target].value then
                        nextStates[target]={value=value,previous=state,choice=choice}
                    end
                end
            end end
        end
        states=nextStates
    end
    local best={value=0}
    for mask=0,2^#plots-1 do local state=states[mask]
        if state and state.value>best.value then best=state end
    end
    local links={};local state=best
    while state.choice do
        links[#links+1]={option=state.choice.option,preference=state.choice.preference};state=state.previous
    end
    table.sort(links,function(a,b)
        local x,y=a.option,b.option
        if x.quarterCity~=y.quarterCity then return x.quarterCity<y.quarterCity end
        return x.quarterDistrict<y.quarterDistrict
    end)
    -- Speculative total cap32 utility is a conservative policy band, not
    -- calibrated income. All legitimate contributions stay in diagnostics;
    -- several future links cannot grow an unbounded production incentive.
    return{preference=math.min(32,best.value),rawPreference=best.value,links=links}
end

local CUSTOMER_FORECAST_BUDGET=16
local CUSTOMER_ALTERNATIVES=3
local CUSTOMER_RESIDUAL_LIMIT_Q8=256*256
-- Runtime-only scheduling memory. No score, game object or native reservation
-- survives a publication: only group/plot identities and a runner-up cursor.
-- Current legal candidate sets revalidate every hint. Reload simply rebuilds
-- the queue; eviction restarts a plot cursor without removing native options.
local customerSchedules={}
local CUSTOMER_SCHEDULE_LIMIT=128
function E.CustomerEconomicOffers(snapshot,protectedPlots)
    -- Native building forecasts are common to a city/type. Compare two full
    -- CSC worlds for that SAME investment, retaining signed site differences
    -- instead of adding its entire economic marginal a second time. Ordinary
    -- adjacency picks a stable reference without consulting our modified cache.
    -- The early native hook consumes these Q8 residuals on fresh evaluation;
    -- stock district preference and production competition still follow.
    local stats={groups=0,forecasts=0,unknown=0,clamped=0,offers=0,
        referenceUnavailable=0,candidateUnavailable=0,nativeUnavailable=0,nativeNonpositive=0}
    if not snapshot.CustomerCandidateSets or not snapshot.WorldQuote or not snapshot.CustomerNetValue then return {},stats end
    local source,waiting=snapshot.CustomerCandidateSets(protectedPlots);local offers={}
    local plans,anchored,anchorValues,anchorPressure={},{},{},{}
    if snapshot.captureConnections then
        snapshot.connectionGroups={}
        for _,list in ipairs({source,waiting or{}})do
            for _,group in ipairs(list)do snapshot.connectionGroups[#snapshot.connectionGroups+1]=group end
        end
        plans=E.AnchoredConnectionPlans(snapshot,protectedPlots)
        for _,plan in ipairs(plans)do if plan.order=='quarterFirst'then
            local option=plan.best.option
            local key=option.city..':'..option.district
            if not anchored[key]or plan.best.valueQ8>anchored[key].valueQ8 then anchored[key]=plan.best end
            local target=siteKey(option.city,option.district,plan.best.plot)
            anchorPressure[target]=math.max(anchorPressure[target]or 0,plan.pressureQ8 or 0)
            for _,row in ipairs(plan.choices)do
                local target=row.option.city..':'..row.option.district..':'..row.plot
                anchorValues[target]=math.max(anchorValues[target]or 0,row.valueQ8)
            end
        end end
    end
    local function referenceCredit(group,ready)
        local ref=group.reference
        local value=anchorValues[siteKey(group.city,group.district,ref.plot)]
        if not (value and value>0 and ready)then return 0 end
        local net=snapshot.CustomerNetValue(group.city,group.district,ref.plot,ready)
        if not net or net<=0 then return 0 end
        -- A linked reference currently supplies the relative forecast's zero
        -- point. Credit its priced transaction once so the district TYPE can
        -- compete for that gain, including when this is the sole legal site.
        -- Carry the same origin into each freshly priced alternative below.
        -- Native private yield remains in the base score and is absent here.
        local credit=math.min(E.ConnectionCompletionCapQ8,value)
        offers[#offers+1]={player=snapshot.id,city=group.city,district=group.district,plot=ref.plot,
            delta=credit,customer=true,customerEconomic=true,referencePlot=ref.plot}
        print(string.format('CSC_AI_CONNECTION_COMPLETION turn=%d player=%d city=%d district=%d plot=%d order=quarterFirst creditQ8=%d',
            Game.GetCurrentGameTurn(),snapshot.id,group.city,group.district,ref.plot,credit))
        return credit
    end
    local state=customerSchedules[snapshot.id]or{groups={}}
    customerSchedules[snapshot.id]=state
    local groups,active={},{}
    stats.singletons=0
    for _,group in ipairs(source)do
        local candidates,seen,linked={},{},{}
        for _,candidate in ipairs(group.candidates)do
            if candidate.plot~=group.reference.plot and not seen[candidate.plot]then
                candidates[#candidates+1]=candidate;seen[candidate.plot]=true
                if(candidate.links or 0)>0 then linked[candidate.plot]=true end
            end
        end
        if #candidates==0 then
            stats.singletons=stats.singletons+1
            if anchorValues[siteKey(group.city,group.district,group.reference.plot)] then
                referenceCredit(group,snapshot.ConnectionDistrictTurns(group.city,group.district))
            end
        else
            local key=group.city..':'..group.district
            local meta=state.groups[key]or{cursor=1}
            -- A captured/occupied/protected footprint is absent from this
            -- publication's legal set and loses its scheduling hint here.
            if(group.reference.links or 0)>0 then linked[group.reference.plot]=true end
            if meta.hint and not linked[meta.hint]then meta.hint=nil end
            local anchor=anchored[key]and anchored[key].plot
            -- A new or redirected connection gets the same immediate quote as
            -- a foundation event. A standing connection stays a hint only,
            -- leaving alternate visits available to reprice its backups.
            local foundation=snapshot.customerFoundationHints and snapshot.customerFoundationHints[key]
            if anchor and anchor~=meta.anchor then foundation=anchor end
            if foundation and not linked[foundation]then foundation=nil end
            if foundation or anchor then meta.hint=foundation or anchor end
            local work={group=group,key=key,meta=meta,candidates=candidates,used={},linked=linked,attempted=0,
                foundation=foundation,anchor=anchor}
            groups[#groups+1]=work;active[key]=meta
        end
    end
    state.groups=active
    local count=#groups
    if count==0 then
        stats.offers=#offers
        print(string.format('CSC_AI_CUSTOMER_SCHEDULE turn=%d player=%d usefulGroups=0 singletonGroups=%d visitedGroups=0 forecasts=0',
            Game.GetCurrentGameTurn(),snapshot.id,stats.singletons))
        return offers,stats,plans
    end
    table.sort(groups,function(a,b)if a.group.city~=b.group.city then return a.group.city<b.group.city end
        return a.group.district<b.group.district end)
    local offset=(Game.GetCurrentGameTurn()+snapshot.id)%count
    for i,work in ipairs(groups)do if work.key==state.nextKey then offset=i-1;break end end
    local order,scheduled={},{}
    -- At most one real-foundation hint goes first. All remaining slots follow
    -- the regular queue, so a stream of new Quarters cannot starve older cities.
    for step=1,count do
        local work=groups[(offset+step-1)%count+1]
        if work.foundation then order[#order+1]=work;scheduled[work.key]=true;break end
    end
    for step=1,count do
        local work=groups[(offset+step-1)%count+1]
        if not scheduled[work.key]then order[#order+1]=work end
    end
    local function quote(group,plot)
        stats.forecasts=stats.forecasts+1
        local before,after=snapshot.CustomerWorld(group.city,group.district,plot)
        if not before then return nil,after end
        local value,problem=snapshot.WorldQuote(after)
        if value then return value,after.customer end
        return nil,problem
    end
    local function evaluate(work,candidate,advance)
        local group,reference=work.group,work.reference
        work.used[candidate.plot]=true;work.attempted=work.attempted+1
        work.meta.last=Game.GetCurrentGameTurn()
        for i,row in ipairs(work.candidates)do if advance~=false and row.plot==candidate.plot then
            work.meta.cursor=i%#work.candidates+1;break
        end end
        local value,investment=quote(group,candidate.plot)
        local outcome,rawValue,finalDelta,netValue='candidate_unavailable',nil,nil,nil
        if value then
            local raw=value.valueQ8-reference.valueQ8
            rawValue=raw
            local referenceCreditQ8=work.referenceCreditQ8 or 0
            local pressure=anchorPressure[siteKey(group.city,group.district,candidate.plot)]or 0
            -- The linked reference correction restores the comparison's
            -- common origin. A scarce alternative can use that much or its
            -- own last-slot preference. They never stack in the same cell.
            -- Cap the relative forecast first. Clipping the common origin
            -- only on the positively saturated alternative changes its
            -- distance from the linked reference in the native comparison.
            local residual=math.max(-CUSTOMER_RESIDUAL_LIMIT_Q8,math.min(CUSTOMER_RESIDUAL_LIMIT_Q8,raw))
            local ordinaryDelta=residual+referenceCreditQ8
            local delta=residual+math.max(pressure,referenceCreditQ8)
            local net=snapshot.CustomerNetValue(group.city,group.district,candidate.plot,investment.ready)
            netValue=net
            if net and net>0 then
                -- Building aggregation only uplifts positive raw
                -- cells. Keep this negative residual above zero so
                -- it cannot accidentally erase a large common
                -- building subtotal. Unknown/nonpositive raw sites
                -- retain native treatment. This is a publication
                -- estimate; final eligibility remains native.
                delta=math.max(delta,1-net)
                local pressureApplied=math.max(0,delta-math.max(ordinaryDelta,1-net))
                finalDelta=delta;outcome=delta~=0 and'offered'or'zero_difference'
                if delta~=raw then stats.clamped=stats.clamped+1 end
                if delta~=0 then
                    offers[#offers+1]={player=snapshot.id,city=group.city,district=group.district,
                        plot=candidate.plot,delta=delta,customer=true,customerEconomic=true,
                        customerEconomicQ8=delta,referencePlot=group.reference.plot,connectionPressureQ8=pressureApplied}
                    print(string.format('CSC_AI_CUSTOMER_ECONOMIC_BID turn=%d player=%d city=%d district=%d plot=%d reference=%d rawQ8=%d deltaQ8=%d netQ8=%d afterQ8=%d referenceQ8=%d adjacency=%.3f links=%d',
                        Game.GetCurrentGameTurn(),snapshot.id,group.city,group.district,candidate.plot,
                        group.reference.plot,raw,delta,net,value.valueQ8,reference.valueQ8,candidate.adjacency,candidate.links))
                end
                if pressureApplied>0 then
                    print(string.format('CSC_AI_CONNECTION_PRESSURE turn=%d player=%d city=%d district=%d plot=%d order=quarterFirst creditQ8=%d',
                        Game.GetCurrentGameTurn(),snapshot.id,group.city,group.district,candidate.plot,pressureApplied))
                end
            else
                stats.unknown=stats.unknown+1
                outcome=net==nil and'native_unavailable'or'native_nonpositive'
                if net==nil then stats.nativeUnavailable=stats.nativeUnavailable+1
                else stats.nativeNonpositive=stats.nativeNonpositive+1 end
            end
        else stats.unknown=stats.unknown+1;stats.candidateUnavailable=stats.candidateUnavailable+1 end
        if Game.GetCurrentGameTurn()%25==0 then
            -- At most the existing15 alternative quotes/player at
            -- a census. Identify the priced shortlist even when a
            -- zero delta or native gate prevents publication.
            print(string.format('CSC_AI_CUSTOMER_ALTERNATIVE turn=%d player=%d city=%d district=%d plot=%d reference=%d outcome=%s rawQ8=%s deltaQ8=%s nativeQ8=%s adjacency=%.3f links=%d',
                Game.GetCurrentGameTurn(),snapshot.id,group.city,group.district,candidate.plot,
                group.reference.plot,outcome,tostring(rawValue),tostring(finalDelta),tostring(netValue),
                candidate.adjacency,candidate.links))
        end
        -- Collect fresh actionable evidence for the group, then choose once.
        -- A later unrelated loser must not erase a useful incumbent; a raw
        -- economic winner with no native-positive admission is not a hint.
        if value and netValue and netValue>0 and value.valueQ8>reference.valueQ8
            and(candidate.links or 0)>0 and(not work.bestValue or value.valueQ8>work.bestValue
                or value.valueQ8==work.bestValue and candidate.plot<work.bestPlot)then
            work.bestValue=value.valueQ8;work.bestPlot=candidate.plot
        end
    end
    local visited={}
    for _,work in ipairs(order)do
        if stats.forecasts+2>CUSTOMER_FORECAST_BUDGET then break end
        local group=work.group
        local reference,investment=quote(group,group.reference.plot)
        work.reference=reference
        stats.groups=stats.groups+1;visited[work.key]=true
        work.meta.visits=(work.meta.visits or 0)+1
        if not work.reference then
            stats.unknown=stats.unknown+1;stats.referenceUnavailable=stats.referenceUnavailable+1
            work.meta.hint=nil
        else
            work.referenceCreditQ8=referenceCredit(group,investment and investment.ready)
            local candidate
            -- Alternate the strongest/hinted challenger with a rotating plot.
            -- Even when eight groups consume the entire budget, lower-ranked
            -- alternatives eventually get a fresh comparison.
            if work.foundation or work.meta.visits%2==1 then
                for _,row in ipairs(work.candidates)do if row.plot==work.meta.hint then candidate=row;break end end
                if not candidate then for _,row in ipairs(work.candidates)do
                    if ((row.links or 0)>0)~=((group.reference.links or 0)>0)then candidate=row;break end
                end end
            end
            local preferred=candidate~=nil
            candidate=candidate or work.candidates[(work.meta.cursor-1)%#work.candidates+1]
            -- Repricing an incumbent must not reset the exploration cursor.
            evaluate(work,candidate,not preferred or work.meta.visits==1)
        end
    end
    -- Everyone gets a reference/challenger pair before third/fourth plots.
    -- Extra comparisons are round-robin, not all spent on the first city.
    for pass=2,CUSTOMER_ALTERNATIVES do
        for _,work in ipairs(order)do
            if stats.forecasts>=CUSTOMER_FORECAST_BUDGET then break end
            if work.reference and work.attempted<pass then
                local candidate
                for n=1,#work.candidates do
                    local row=work.candidates[(work.meta.cursor+n-2)%#work.candidates+1]
                    if not work.used[row.plot]then candidate=row;break end
                end
                if candidate then evaluate(work,candidate)end
            end
        end
    end
    for _,work in ipairs(groups)do
        local incumbent=work.meta.hint
        -- An unvisited group retains its one-time priority until it receives
        -- a quote. Clear a gone anchor immediately so a returning one is new.
        if not work.anchor or visited[work.key]then work.meta.anchor=work.anchor end
        if incumbent and incumbent~=work.group.reference.plot and not work.used[incumbent]
            and work.linked[incumbent]then
            -- Identity only: its fresh value will be checked on the next
            -- incumbent pass. No score is copied into this packet.
        else work.meta.hint=work.bestPlot end
    end
    state.nextKey=nil
    for step=1,count do
        local work=groups[(offset+step-1)%count+1]
        if not visited[work.key]then state.nextKey=work.key;break end
    end
    if not state.nextKey then state.nextKey=groups[(offset+1)%count+1].key end
    -- Bound hints independently of the number of eligible city/type groups.
    -- Group fairness uses nextKey and therefore survives hint eviction.
    if count>CUSTOMER_SCHEDULE_LIMIT then
        local oldest={};for key,meta in pairs(state.groups)do oldest[#oldest+1]={key=key,last=meta.last or-1}end
        table.sort(oldest,function(a,b)if a.last~=b.last then return a.last>b.last end;return a.key<b.key end)
        for i=CUSTOMER_SCHEDULE_LIMIT+1,#oldest do state.groups[oldest[i].key]=nil end
    end
    print(string.format('CSC_AI_CUSTOMER_SCHEDULE turn=%d player=%d usefulGroups=%d singletonGroups=%d visitedGroups=%d forecasts=%d next=%s',
        Game.GetCurrentGameTurn(),snapshot.id,count,stats.singletons,stats.groups,stats.forecasts,tostring(state.nextKey)))
    stats.offers=#offers
    print(string.format('CSC_AI_CUSTOMER_ECONOMIC_WORK turn=%d player=%d groups=%d totalGroups=%d forecasts=%d offers=%d unknown=%d clamped=%d quotes=%d',
        Game.GetCurrentGameTurn(),snapshot.id,stats.groups,count,stats.forecasts,#offers,stats.unknown,stats.clamped,snapshot.QuoteCount and snapshot.QuoteCount()or 0))
    -- Passive reason totals use the results above, not another forecast or native
    -- quote. Keep the old WORK contract for existing reports. This separates a
    -- missing model quote from the deliberate native nonpositive-cell guard.
    print(string.format('CSC_AI_CUSTOMER_ECONOMIC_GAPS turn=%d player=%d referenceUnavailable=%d candidateUnavailable=%d nativeUnavailable=%d nativeNonpositive=%d unvisitedGroups=%d',
        Game.GetCurrentGameTurn(),snapshot.id,stats.referenceUnavailable,stats.candidateUnavailable,
        stats.nativeUnavailable,stats.nativeNonpositive,count-stats.groups))
    return offers,stats,plans
end

function E.ReportQuarterFunnel(snapshot,evaluations)
    -- Diagnostic only: inspect already-calculated results every25 turns. One
    -- summary and at most eight representative rejected cells per player; no
    -- extra map scan, world evaluation, score write or change to candidate order.
    local turn=Game.GetCurrentGameTurn()
    if turn%25~=0 then return end
    local counts,best={},{}
    for id,details in pairs(evaluations)do
        local reason=details.reason or'unspecified'
        counts[reason]=(counts[reason]or 0)+1
        local previous=best[reason]
        if reason~='positive'and reason~='grace'and(not previous
            or(details.adjacency or-1)>(previous.details.adjacency or-1)
            or((details.adjacency or-1)==(previous.details.adjacency or-1)and id<previous.id))then
            best[reason]={id=id,details=details}
        end
    end
    local names={};for name in pairs(counts)do names[#names+1]=name end;table.sort(names)
    local totals={};local samples=0
    for _,name in ipairs(names)do
        totals[#totals+1]=name..':'..counts[name]
        local row=best[name]
        if row and samples<8 then
            samples=samples+1
            print(string.format('CSC_AI_QUARTER_FUNNEL_SAMPLE turn=%d player=%d key=%s reason=%s adjacency=%s economicQ8=%s purchaseQ8=%s detail=%s',
                turn,snapshot.id,row.id,name,tostring(row.details.adjacency),
                tostring(row.details.economicQ8),tostring(row.details.purchaseQ8),
                tostring(row.details.detail):gsub('[\r\n\t]',' ')))
        end
    end
    print(string.format('CSC_AI_QUARTER_FUNNEL turn=%d player=%d reasons=%s samples=%d',turn,snapshot.id,table.concat(totals,','),samples))
end

function E.MergeCustomerOffers(entries,offers)
    -- CE's packet rejects duplicate keys. Combine the existing spatial signal,
    -- structural deduction and economic residual once before native staging.
    -- Copy rows so merging never changes the original planner/protection facts.
    local result,byKey={},{}
    local function key(row)return row.player..':'..row.city..':'..row.district..':'..row.plot end
    for _,row in ipairs(entries)do
        local copy={};for k,v in pairs(row)do copy[k]=v end
        result[#result+1]=copy;byKey[key(copy)]=copy
    end
    for _,offer in ipairs(offers)do
        local previous=byKey[key(offer)]
        if previous then
            if previous.finalQ8==nil then
                previous.delta=(previous.delta or 0)+offer.delta
                previous.customer=true
                if offer.customerPurchaseGold then previous.customerPurchaseGold=offer.customerPurchaseGold end
                if offer.customerEconomic then
                    previous.customerEconomic=true;previous.customerEconomicQ8=offer.delta;previous.referencePlot=offer.referencePlot
                    previous.connectionPressureQ8=offer.connectionPressureQ8
                end
            end
        else
            local copy={};for k,v in pairs(offer)do copy[k]=v end
            result[#result+1]=copy;byKey[key(copy)]=copy
        end
    end
    for i=#result,1,-1 do if result[i].finalQ8==nil and result[i].delta==0 then table.remove(result,i)end end
    return result
end

function E.CustomerOffers(snapshot,quarterEntries,protectedPlots)
    -- Customer-first planning is independent of a winning/unlocked Quarter
    -- proposal. Aggregate once per customer footprint, with one contribution
    -- per supplier city/type and a bounded total. Native ordinary adjacency
    -- leads; the customer still competes with all normal production choices.
    -- Cross-customer coordination is greedy, while each customer's supplier
    -- matching is exact. No land/slot is reserved across publications. Current
    -- capacity only pays for the customer; future growth can admit Quarters.
    if not snapshot.CustomerFirstOptions then return {}end
    local best,quarterClaims,customerClaims,nominated={},{},{},{}
    for _,entry in ipairs(quarterEntries)do if entry.economy then
        local key=entry.city..':'..entry.district
        if not best[key]or entry.finalQ8>best[key].finalQ8
            or entry.finalQ8==best[key].finalQ8 and entry.plot<best[key].plot then best[key]=entry end
    end end
    local plans={};for _,entry in pairs(best)do plans[#plans+1]=entry end
    table.sort(plans,function(a,b)
        if a.finalQ8~=b.finalQ8 then return a.finalQ8>b.finalQ8 end
        if a.city~=b.city then return a.city<b.city end
        return a.district<b.district
    end)
    for _,entry in ipairs(plans)do quarterClaims[entry.plot]=quarterClaims[entry.plot]or entry.district end
    if snapshot.planState then for _,plan in pairs(snapshot.planState.plans)do quarterClaims[plan.plot]=plan.district end end
    local grouped={}
    for _,option in ipairs(snapshot.CustomerFirstOptions(protectedPlots))do
        local quarter=best[option.quarterCity..':'..option.quarterDistrict]
        local layout=quarter and quarter.strongLayout
        option.strongLayout=layout and not layout.existing and quarter.plot==option.quarterPlot
            and layout.city==option.city and layout.district==option.district and layout.plot==option.plot
        local key=option.city..':'..option.district..':'..option.plot
        local group=grouped[key]or{city=option.city,district=option.district,plot=option.plot,
            adjacency=option.adjacency,options={}}
        grouped[key]=group;group.options[#group.options+1]=option
    end
    local candidates={}
    for _,group in pairs(grouped)do
        group.plan=E.CustomerFirstPlan(group.options,quarterClaims,customerClaims)
        candidates[#candidates+1]=group
    end
    table.sort(candidates,function(a,b)
        if a.plan.preference~=b.plan.preference then return a.plan.preference>b.plan.preference end
        if a.adjacency~=b.adjacency then return a.adjacency>b.adjacency end
        if a.city~=b.city then return a.city<b.city end
        if a.district~=b.district then return a.district<b.district end
        return a.plot<b.plot
    end)
    local remaining,offers={},{}
    for _,candidate in ipairs(candidates)do
        local key=candidate.city..':'..candidate.district
        local city=snapshot.cities[candidate.city]and snapshot.cities[candidate.city].object
        local definition=GameInfo.Districts[candidate.district]
        if city and definition and not nominated[key]and not quarterClaims[candidate.plot]
            and not customerClaims[candidate.plot]and not protectedPlots[candidate.plot]then
            local plan=E.CustomerFirstPlan(candidate.options,quarterClaims,customerClaims)
            local exempt=definition.RequiresPopulation==false or definition.RequiresPopulation==0
            if remaining[candidate.city]==nil then
                local capacity=snapshot.DistrictCapacity(city)
                remaining[candidate.city]=capacity and capacity.known and capacity.allowed-capacity.used or 0
            end
            if plan.preference>0 and(exempt or remaining[candidate.city]>0)then
                local offer={player=snapshot.id,city=candidate.city,district=candidate.district,plot=candidate.plot,
                    delta=plan.preference*256,customer=true,spatial=true,customerFirst=true,
                    futureSuppliers=plan.links,rawPreferenceQ8=plan.rawPreference*256}
                offers[#offers+1]=offer;nominated[key]=true;customerClaims[candidate.plot]=true
                if not exempt then remaining[candidate.city]=remaining[candidate.city]-1 end
                -- Proposal identities join ordinary CE customer receipts.
                -- Component records preserve each legitimate shared-material
                -- incentive separately from the capped aggregate packet bid.
                print(string.format('CSC_AI_CUSTOMER_FUTURE_BID turn=%d player=%d city=%d district=%d plot=%d suppliers=%d rawQ8=%d deltaQ8=%d',
                    Game.GetCurrentGameTurn(),snapshot.id,offer.city,offer.district,offer.plot,#plan.links,offer.rawPreferenceQ8,offer.delta))
                for _,link in ipairs(plan.links)do local option=link.option
                    quarterClaims[option.quarterPlot]=option.quarterDistrict
                    print(string.format('CSC_AI_CUSTOMER_FUTURE_LINK turn=%d player=%d city=%d district=%d plot=%d quarterCity=%d quarterDistrict=%d quarterPlot=%d base=%d spec=%d basePlots=%s specPlots=%s ordinaryAdjacency=%.3f bestOrdinaryAdjacency=%.3f contributionQ8=%d strongLayout=%s',
                        Game.GetCurrentGameTurn(),snapshot.id,offer.city,offer.district,offer.plot,
                        option.quarterCity,option.quarterDistrict,option.quarterPlot,option.baseCount,option.specialtyCount,
                        table.concat(option.basePlots,','),table.concat(option.specialtyPlots,','),
                        option.adjacency,option.bestAdjacency,link.preference*256,tostring(option.strongLayout==true)))
                end
            end
        end
    end
    table.sort(offers,function(a,b)if a.city~=b.city then return a.city<b.city end;return a.district<b.district end)
    local work=snapshot.customerFirstWork or{}
    print(string.format('CSC_AI_CUSTOMER_FUTURE_WORK turn=%d player=%d targets=%d quarterChecks=%d supplyReads=%d options=%d unknown=%d offers=%d',
        Game.GetCurrentGameTurn(),snapshot.id,work.targets or 0,work.quarterChecks or 0,
        work.supplyReads or 0,work.options or 0,work.unknown or 0,#offers))
    return offers
end

-- The existing models already price completing the district. The connection
-- plan prices only the opportunity forgone by using its intended footprint
-- for a different district. Retain identity only, so a stale offer cannot
-- protect a tile after capture, a new reservation or a change in eligibility.
local connectionMemory={}
local connectionAuditMemory={}
local CONNECTION_GROUPS_PER_ORDER=2
local CONNECTION_COST_CAP_Q8=64*256
E.ConnectionCompletionCapQ8=CONNECTION_COST_CAP_Q8
local STRONG_SITE_LINK_RELIEF_LIMIT_Q8=128*256

function E.ConnectionLossQ8(best, backup)
    -- A cautious first calibration: half the ordinary link margin displaced,
    -- up to 64 native utility. With equally valuable distinct sites the cost
    -- is zero. Unknown backup values must be resolved before using this rule.
    return math.min(CONNECTION_COST_CAP_Q8,math.max(0,math.floor((best-backup)/2)))
end

local function projectedLinkValue(snapshot,candidate,layout)
    local site,profile=candidate.site,candidate.profile
    local ready,quarterFirstReady,bothReady=connectionSchedule(snapshot,site,layout)
    if not bothReady or bothReady>=site.horizon then return nil end
    local venues={}
    for _,venue in ipairs(snapshot.ProjectedCustomers(profile,layout.city,layout.district,layout.plot,ready))do
        if venue.stage<4 or layout.hasSpec then venues[#venues+1]=venue end
    end
    -- Quote the same Quarter with and without the linked buyer. The model
    -- schedules the shared city queue and carries the actual buyer timings.
    -- The customer's private native adjacency and Services stay outside
    -- this incremental link quote and retain their ordinary consumers.
    local value=0
    if #venues>0 then
        local forecast=M.CustomerBuildingForecast(site,venues,layout.city,ready,snapshot.Price,quarterFirstReady)
        if not forecast then return nil end
        value=forecast.valueQ8
        bothReady=math.max(ready,forecast.with.quarterReadyByChain[site.key] or bothReady)
    elseif layout.role~='provider' then
        return nil
    end
    local city=snapshot.cities[site.city]
    local quarterPlot=Map.GetPlotByIndex(site.plot)
    local yields=city and quarterPlot and snapshot.ProjectedConnectionYields(
        {city=city.object,plot=quarterPlot,profile=profile},layout.district,layout.plot,layout.purchaseGold)
    if not yields then return nil end
    -- A Rural Community can be a pure goods provider. Its adjacency begins
    -- when the linked districts exist, with no customer building to schedule.
    for yield,amount in pairs(yields)do
        if amount~=0 then
            local price=snapshot.Price({player=snapshot.id,city=site.city,yield=yield,amount=amount,ready=bothReady},site.horizon)
            if price==nil then return nil end
            value=value+price
        end
    end
    -- This is the partner's *increment* from a still-unbuilt Quarter. Its
    -- ordinary terrain income remains in its native bid. Once the Quarter
    -- exists, the native adjacency read already sees it and this path ends.
    for yield,amount in pairs(layout.customerYields or {}) do
        if amount~=0 then
            local price=snapshot.Price({player=snapshot.id,city=layout.city,yield=yield,amount=amount,
                ready=bothReady},site.horizon)
            if price==nil then return nil end
            value=value+price
        end
    end
    if layout.purchaseGold then
        local invoice=snapshot.Price({player=snapshot.id,city=layout.city,yield='YIELD_GOLD',
            amount=-layout.purchaseGold,ready=0,fixed=true},site.horizon)
        if not invoice then return nil end
        value=value+invoice
    end
    return value
end

function E.ProspectiveConnectionPlans(snapshot,protectedPlots)
    if not(E.ProspectiveConnectionsEnabled and snapshot.ProspectiveCustomerReady
        and snapshot.ProjectedCustomers and snapshot.ProjectedConnectionYields)then return {},{}end
    local groups,ranked={},{}
    local function available(plot,entry)
        local intent=snapshot.intentFootprints and snapshot.intentFootprints[plot]
        return not protectedPlots[plot]and(not intent or entry and intent==siteKey(entry.city,entry.district,entry.plot))
    end
    for _,candidate in ipairs(snapshot.connectionQuarters or{})do
        local entry=candidate.entry
        local key=entry.city..':'..entry.district
        local group=groups[key]
        if not group then group={};groups[key]=group;ranked[#ranked+1]=group end
        group[#group+1]=candidate
        if not group.best or entry.finalQ8>group.best.entry.finalQ8
            or entry.finalQ8==group.best.entry.finalQ8 and entry.plot<group.best.entry.plot then
            group.best=candidate
        end
        local prior=snapshot.savedLayouts and snapshot.savedLayouts[key]
        local partner=entry.prospectiveLayout
        if prior and prior.plot==entry.plot and partner and prior.partnerCity==partner.city
            and prior.partnerDistrict==partner.district and prior.partnerPlot==partner.plot then
            group.retained=candidate
        end
    end
    -- Keep a still-competitive complete plan within the existing 10% band
    -- used for substitutes. All bids below use today's facts and prices.
    for _,group in ipairs(ranked) do
        if group.retained and group.retained.entry.finalQ8>=group.best.entry.finalQ8*.90 then
            group.best=group.retained
        end
    end
    table.sort(ranked,function(a,b)
        local x,y=a.best.entry,b.best.entry
        if x.finalQ8~=y.finalQ8 then return x.finalQ8>y.finalQ8 end
        if x.city~=y.city then return x.city<y.city end
        return x.district<y.district
    end)
    -- Keep three leading city plans first. Rotate the fourth quote through
    -- the remaining cities so a mature empire can revisit affordable plans
    -- outside its top four without expanding the per-publication budget.
    if #ranked>4 then
        local index=4+(Game.GetCurrentGameTurn()+snapshot.id)%(#ranked-3)
        table.insert(ranked,4,table.remove(ranked,index))
    end
    local plans,credits,claimed,admitted={},{},{},{}
    local function canBid(option,isQuarter,site)
        if isQuarter and option.capacityState~='ready'and option.capacityState~='exempt'then return false end
        if not(snapshot.ui and snapshot.ui.GetLegalDistrictTargets)then return false end
        local key=option.city..':'..option.district
        local targets=admitted[key]
        if not targets then
            targets={};admitted[key]=targets
            local definition=GameInfo.Districts[option.district]
            if not definition then return false end
            local ok,indices=pcall(snapshot.ui.GetLegalDistrictTargets,snapshot.id,option.city,definition.Hash)
            if ok and type(indices)=='table'then for _,index in ipairs(indices)do targets[index]=true end end
        end
        if not targets[option.plot] and not option.purchaseGold then return false end
        if isQuarter then
            -- An owned legal target has passed the native prerequisite check.
            -- A frontier invoice establishes a buyer, so check the Quarter's
            -- research separately until native zoning admits the owned plot.
            return targets[option.plot] or site.quarterWork and site.quarterWork.unlock==0
        end
        local ready,unlock=snapshot.ProspectiveCustomerReady(option.city,option.district)
        if option.purchaseGold then
            -- Owned BUILD targets cannot list a plot that Economic must buy.
            -- The frontier reader already checked map fit and exact buyer.
            -- Keep research, population admission and positive native value.
            local definition=GameInfo.Districts[option.district]
            local host=snapshot.cities[option.city]
            local capacity=host and snapshot.DistrictCapacity and snapshot.DistrictCapacity(host.object)
            if unlock~=0 or not definition or (definition.RequiresPopulation~=0 and definition.RequiresPopulation~=false
                and not (capacity and capacity.known and capacity.allowed>capacity.used)) then return false end
        end
        local net=ready and snapshot.CustomerNetValue and snapshot.CustomerNetValue(option.city,option.district,option.plot,ready)
        return net and net>0
    end
    local priced=0
    for _,group in ipairs(ranked)do
        local best=group.best
        local quarter=best.entry
        local layout=quarter.prospectiveLayout or quarter.strongLayout
        if layout and not layout.existing and layout.plot~=quarter.plot
            and available(quarter.plot,quarter)and available(layout.plot)
            and not claimed[quarter.plot]and not claimed[layout.plot]then
            if snapshot.auditConnections and quarter.pairedAdjacency then
                -- Diagnostic only, one shortlisted offer per city and Quarter
                -- type. Adjacency figures are gameplay yield points. The bid
                -- premium is Q8 native utility and the ETA is turns from now.
                print(string.format('CSC_AI_PAIR_QUALIFICATION turn=%d player=%d city=%d district=%d plot=%d partnerCity=%d partnerDistrict=%d partnerPlot=%d role=%s stage=%d starting=%.3f withMill=%.3f withPartner=%.3f partnerOwn=%.3f partnerWithQuarter=%.3f ready=%d premiumQ8=%d',
                    Game.GetCurrentGameTurn(),snapshot.id,quarter.city,quarter.district,quarter.plot,
                    layout.city,layout.district,layout.plot,layout.role or 'customer',layout.stage,
                    quarter.startingAdjacency or 0,quarter.adjacency,quarter.pairedAdjacency,layout.adjacency,
                    layout.adjacency+(layout.customerGain or 0),quarter.pairReady,quarter.adjacencyPreferenceQ8))
            end
            local alternateQuarter,alternateCustomer
            local function considerBackup(other,partner)
                -- A comparably strong full plan can replace both empty
                -- targets. An established buyer is also a credible substitute.
                -- Treat bids within 10% as credible backups in this first
                -- trial. This tolerance only withdraws a scarcity premium.
                if other.plot~=quarter.plot and other.finalQ8>=quarter.finalQ8*.90 and partner
                    and partner.role==layout.role and (layout.rank and partner.rank and partner.rank>=layout.rank*.90
                        or not layout.rank and partner.stage>=layout.stage) and available(other.plot,other)
                    and (partner.existing or available(partner.plot))then
                    -- A replacement has to survive losing the original tile
                    -- entirely. Swapping the district roles still needs both
                    -- original tiles and cannot release either footprint.
                    if partner.plot~=quarter.plot then alternateQuarter=alternateQuarter or other.plot end
                    if other.plot~=layout.plot and partner.plot~=layout.plot then
                        alternateCustomer=alternateCustomer or partner.plot
                    end
                end
            end
            for _,alternative in ipairs(group)do
                local other=alternative.entry
                considerBackup(other,other.strongLayout)
                if other.prospectiveLayout~=other.strongLayout then considerBackup(other,other.prospectiveLayout)end
            end
            for _,other in ipairs(best.site.prospectiveCustomers or{})do
                if other.plot~=layout.plot and available(other.plot) and
                    (layout.role=='provider' and other.goodsProvider or other.stages and other.stages[layout.stage])
                    and other.adjacency>=math.max(other.bestAdjacency,other.displacedAdjacency,layout.adjacency)
                then
                    alternateCustomer=other.plot
                    break
                end
            end
            if snapshot.auditConnections and (alternateQuarter or alternateCustomer)then
                -- Diagnostic only. A substitute is a live layout that met
                -- today's supply, geometry and adjacency checks. It explains
                -- why the corresponding footprint receives no scarcity cost.
                print(string.format('CSC_AI_PROSPECTIVE_SUBSTITUTE turn=%d player=%d quarterCity=%d quarter=%d quarterPlot=%d customerCity=%d customer=%d customerPlot=%d alternateQuarterPlot=%d alternateCustomerPlot=%d',
                    Game.GetCurrentGameTurn(),snapshot.id,quarter.city,quarter.district,quarter.plot,
                    layout.city,layout.district,layout.plot,alternateQuarter or -1,alternateCustomer or -1))
            end
            local legs=(alternateQuarter and 0 or 1)+(alternateCustomer and 0 or 1)
            -- Only a live source can secure this plan. Work out which deposits
            -- survive the proposed foundations; a resource under the partner
            -- cannot supply the Quarter once that district starts.
            local supply={base={},specialty={}}
            for _,source in ipairs(best.site.suppliers or {}) do
                if source.plot and source.plot~=quarter.plot and source.plot~=layout.plot
                    and source.ready<best.site.horizon and supply[source.kind]
                    and not (snapshot.intentFootprints or {})[source.plot] then
                    table.insert(supply[source.kind],source)
                end
            end
            local materials={}
            local function protectLastSource(sources)
                local first=sources[1]
                if not first or protectedPlots[first.plot] then return end
                for _,other in ipairs(sources) do if other.plot~=first.plot then return end end
                -- If a comparable alternate Quarter has another supplier of
                -- this class, losing the deposit still leaves a working plan.
                for _,other in ipairs(group) do
                    if other.entry.plot==alternateQuarter then
                        for _,source in ipairs(other.site.suppliers or {}) do
                            if source.kind==first.kind and source.plot and source.plot~=first.plot
                                and source.plot~=other.entry.plot and source.plot~=layout.plot
                                and source.ready<other.site.horizon and available(source.plot) then return end
                        end
                    end
                end
                local tile=Map.GetPlotByIndex(first.plot)
                local owner=tile and tile:GetOwner()==snapshot.id and Cities.GetPlotPurchaseCity(tile)
                if owner and owner:GetOwner()==snapshot.id and tile:GetDistrictType()<0
                    and (not materials[1] or materials[1].plot~=first.plot) then
                    materials[#materials+1]={plot=first.plot,city=owner:GetID()}
                end
            end
            protectLastSource(supply.base)
            if layout.stage==4 then protectLastSource(supply.specialty) end
            local function remember()
                if not snapshot.nextLayouts then return end
                if #supply.base>0 then
                    local key=quarter.city..':'..quarter.district
                    snapshot.nextLayouts[key]=C.LayoutRecord(quarter,layout,supply,alternateQuarter,alternateCustomer,
                        snapshot.savedLayouts[key],Game.GetCurrentGameTurn())
                end
            end
            -- An interchangeable pair needs no scarcity premium. Its identity
            -- still helps us follow the first foundation next publication.
            if priced>=4 then
                -- Preserve an already remembered identity only when this
                -- turn independently shortlisted the same feasible pair.
                -- Its original freshness expires unless it is priced again.
                if snapshot.nextLayouts and group.retained==best then
                    local key=quarter.city..':'..quarter.district
                    snapshot.nextLayouts[key]=snapshot.savedLayouts[key]
                end
            else
                priced=priced+1
                local value=projectedLinkValue(snapshot,best,layout)
                if value and value>0 then
                    remember()
                    local quarterReady,customerReady=canBid(quarter,true,best.site),canBid(layout,false)
                    local readyPair=quarterReady and customerReady and hasSlotsForBoth(snapshot,quarter,layout)
                    -- The net link quote already discounts research, queues
                    -- and construction. Spend it once across the scarce
                    -- footprints if both projects fit now. Individual native
                    -- admission can offer both the same last slot, so check
                    -- their joint demand. Retain half the quote while waiting
                    -- for a slot or an unlock the two-project timing omits.
                    -- Each admitted leg splits its capped share between its
                    -- own bid and the residual cost on a rival at that tile.
                    local divisor=math.max(1,legs)*(readyPair and 1 or 2)
                    local perLeg=math.min(CONNECTION_COST_CAP_Q8,math.floor(value/divisor))
                    if perLeg>0 and (legs>0 or #materials>0) then
                        -- Keep the positive bids at their original size. Share
                        -- the remaining deterrent across rival district sites
                        -- that would destroy this particular plan. Each lost
                        -- link gets one budget even with two scarce deposits.
                        local materialBudget=legs==0 and perLeg or 0
                        local function retain(option,backup,isQuarter,ready)
                            local credit=ready and math.floor(perLeg/2)or 0
                            local cost=perLeg-credit
                            local share=math.floor(cost*#materials/(legs+#materials))
                            materialBudget=materialBudget+share
                            cost=cost-share
                            local row={plot=option.plot,option=option,options={option}}
                            plans[#plans+1]={order='prospective',anchor=backup,stage=layout.stage,best=row,costQ8=cost}
                            if credit>0 then
                                credits[#credits+1]={city=option.city,district=option.district,plot=option.plot,
                                    quarter=isQuarter,valueQ8=credit,purchaseGold=option.purchaseGold}
                            end
                            return cost,credit
                        end
                        local qCost,qCredit,cCost,cCredit=0,0,0,0
                        if not alternateQuarter then qCost,qCredit=retain(quarter,layout.plot,true,quarterReady)end
                        if not alternateCustomer then cCost,cCredit=retain(layout,quarter.plot,false,customerReady)end
                        for _,source in ipairs(materials) do
                            -- No district completes a supplier deposit. Limit
                            -- the comparison to the city's legal placements.
                            plans[#plans+1]={order='plannedSupply',anchor=quarter.plot,stage=layout.stage,
                                best={plot=source.plot,option=source,options={}},
                                costQ8=math.floor(materialBudget/#materials)}
                        end
                        claimed[quarter.plot]=true;claimed[layout.plot]=true
                        print(string.format('CSC_AI_PROSPECTIVE_CONNECTION turn=%d player=%d quarterCity=%d quarter=%d quarterPlot=%d customerCity=%d customer=%d customerPlot=%d valueQ8=%d quarterCostQ8=%d customerCostQ8=%d quarterCreditQ8=%d customerCreditQ8=%d readyPair=%d',
                            Game.GetCurrentGameTurn(),snapshot.id,quarter.city,quarter.district,quarter.plot,
                            layout.city,layout.district,layout.plot,value,qCost,cCost,qCredit,cCredit,readyPair and 1 or 0))
                    end
                end
            end
        end
    end
    return plans,credits
end

local function restoreLayouts(snapshot,profiles)
    if not (C and E.ProspectiveConnectionsEnabled and snapshot.planState and snapshot.districts) then return end
    local turn=Game.GetCurrentGameTurn()
    local saved=C.ReadLayouts(snapshot.planState.savedLayouts,turn)
    snapshot.savedLayouts={};snapshot.nextLayouts={}
    snapshot.handoffs={};snapshot.partnerHints={}
    local byDistrict={}
    for _,profile in ipairs(profiles) do byDistrict[profile.district.Index]=profile end
    local function footprint(index,city,district)
        if not snapshot.cities[city] then return nil end
        local plot=Map.GetPlotByIndex(index)
        if not plot then return nil end
        local owner=plot:GetOwner()
        if owner~=snapshot.id and owner~=-1 then return nil end
        if owner==snapshot.id then
            local assigned=Cities.GetPlotPurchaseCity(plot)
            if not assigned or assigned:GetID()~=city then return nil end
        end
        if plot:GetDistrictType()==-1 then return 'empty' end
        local host=snapshot.districts[index]
        if host and host.city==city and host.type==district then return 'founded' end
    end
    for key,p in pairs(saved) do
        local q=footprint(p.plot,p.city,p.district)
        local partner=footprint(p.partnerPlot,p.partnerCity,p.partnerDistrict)
        local profile=byDistrict[p.district]
        if q and partner and profile and not(q=='founded' and partner=='founded') then
            local supply=snapshot.Supply(Map.GetPlotByIndex(p.plot),profile)
            if supply and #supply.base>0 and (p.stage~=4 or #supply.specialty>0) then
                snapshot.savedLayouts[key]=p
                local order=q=='founded' and 'quarterFirst' or partner=='founded' and 'customerFirst'
                if order then
                    local anchor=q=='founded' and p.plot or p.partnerPlot
                    local missing=q=='founded' and p.partnerPlot or p.plot
                    local group=table.concat({order,anchor,p.stage,profile.key},':')
                    snapshot.handoffs[group]={record=p,plot=missing,phase=q=='founded' and 1 or 2}
                    if q=='founded' then snapshot.partnerHints[p.partnerCity..':'..p.partnerDistrict]=missing end
                    -- Keep the anchor while growth or an unlock delays the
                    -- missing district. Only a fresh useful quote renews it.
                    snapshot.nextLayouts[key]=p
                end
            end
        end
    end
end

function E.ApplyProspectiveConnectionCredit(snapshot,entries,credits)
    if #credits==0 then return entries end
    local bySite,offers={},{}
    for _,row in ipairs(entries)do
        if row.economy and not row.carried then bySite[siteKey(row.city,row.district,row.plot)]=row end
    end
    for _,credit in ipairs(credits)do
        local key=siteKey(credit.city,credit.district,credit.plot)
        if credit.quarter then
            local row=bySite[key]
            if row and row.finalQ8>0 then row.finalQ8=math.min(4096*256,row.finalQ8+credit.valueQ8)end
        else
            -- The ordinary customer delta can already contain spatial or
            -- anchored income. This empty-pair allowance uses only its
            -- shared loss budget, and falls away after a real foundation.
            offers[#offers+1]={player=snapshot.id,city=credit.city,district=credit.district,plot=credit.plot,
                customer=true,delta=credit.valueQ8,customerPurchaseGold=credit.purchaseGold}
            print(string.format('CSC_AI_CUSTOMER_PROSPECTIVE_BID turn=%d player=%d city=%d district=%d plot=%d deltaQ8=%d',
                Game.GetCurrentGameTurn(),snapshot.id,credit.city,credit.district,credit.plot,credit.valueQ8))
        end
    end
    if #offers==0 then return entries end
    return E.MergeCustomerOffers(entries,offers)
end

function E.AnchoredConnectionPlans(snapshot,protectedPlots)
    local turn,pid=Game.GetCurrentGameTurn(),snapshot.id
    local groups={quarterFirst={},customerFirst={}}
    local before=connectionMemory[pid]or{}
    local nextMemory={}
    local function add(order,anchor,stage,quarterKey,option)
        local key=table.concat({order,anchor,stage,quarterKey},':')
        local g=groups[order][key]or{key=key,anchor=anchor,stage=stage,order=order,quarter=quarterKey,plots={}}
        groups[order][key]=g
        local plot=g.plots[option.plot]or{plot=option.plot,options={}}
        g.plots[option.plot]=plot
        plot.options[#plot.options+1]=option
    end
    local function supplied(site,stage,consumedPlot)
        local base,specialty=false,false
        for _,supplier in ipairs(site.suppliers or{})do
            -- The local venue forecast keeps current supply. Reject a new
            -- customer footprint that would cover one of those suppliers.
            if consumedPlot~=nil and supplier.plot==consumedPlot then return false end
            if (supplier.ready or math.huge)<site.horizon then
                base=base or supplier.kind=='base';specialty=specialty or supplier.kind=='specialty'
            end
        end
        return base and(stage<4 or specialty)
    end
    local function free(index,ownIntent)
        local reserved=snapshot.intentFootprints and snapshot.intentFootprints[index]
        return not protectedPlots[index]and (not reserved or reserved==ownIntent)
    end
    for _,group in ipairs(snapshot.connectionGroups or{})do
        -- Reuse the owned, unprotected candidate sets. Waiting candidates
        -- retain the same map fit without immediate native build admission.
        for _,candidate in ipairs(group.candidates)do if free(candidate.plot)then
            for _,chain in ipairs(candidate.chains or{})do if chain.economy and (chain.ready or
                chain.complete==false and (chain.economy.quarterReady or math.huge)<chain.economy.horizon)then
                -- A provider has a real adjacency effect without a buyer
                -- building. Once the Quarter exists, quote the same effect
                -- with fresh geometry in the ordinary customer-site auction.
                if E.ProspectiveConnectionsEnabled and snapshot.IsGoodsProvider
                    and snapshot.IsGoodsProvider(chain.profile,group.district)
                    and supplied(chain.economy,2,candidate.plot) then
                    add('quarterFirst',chain.plot:GetIndex(),0,chain.profile.key,
                        {plot=candidate.plot,city=group.city,district=group.district,rank=candidate.adjacency,
                         site=chain.economy,chain=chain,projected=true,venue={building=''},waiting=candidate.waiting,
                         purchaseGold=candidate.purchaseGold})
                end
                for _,venue in ipairs(snapshot.ProjectedCustomers(chain.profile,group.city,group.district,candidate.plot))do
                    local transactionReady=not venue.excluded and supplied(chain.economy,venue.stage,candidate.plot)
                    local canPriceYields=snapshot.ProjectedConnectionYields and supplied(chain.economy,2,candidate.plot)
                    if venue.transaction and (transactionReady or canPriceYields)then
                        add('quarterFirst',chain.plot:GetIndex(),venue.stage,chain.profile.key,
                            {plot=candidate.plot,city=group.city,district=group.district,rank=candidate.adjacency,
                             site=chain.economy,chain=chain,venue=venue,projected=true,
                             transactionReady=transactionReady,waiting=candidate.waiting,purchaseGold=candidate.purchaseGold})
                    end
                end
            end end
        end end
    end
    local admitted={}
    for _,candidate in ipairs(snapshot.connectionQuarters or{})do
        local entry,site=candidate.entry,candidate.site
        if free(entry.plot,siteKey(entry.city,entry.district,entry.plot))then
            local venues=site.customers
            local pending=snapshot.PendingConnectionVenues and snapshot.PendingConnectionVenues(site,candidate.profile)
            local providers={}
            if E.ProspectiveConnectionsEnabled and snapshot.IsGoodsProvider then
                local center=Map.GetPlotByIndex(entry.plot)
                for _,near in ipairs(Map.GetAdjacentPlots(center:GetX(),center:GetY())) do
                    local host=snapshot.districts[near:GetIndex()]
                    if host and snapshot.IsGoodsProvider(candidate.profile,host.type) then
                        providers[#providers+1]={stage=0,provider=true,plot=near:GetIndex(),building='',
                            anchorReady=not host.complete and snapshot.ConnectionDistrictTurns(host.city,host.type)}
                    end
                end
            end
            if (pending and #pending>0) or #providers>0 then
                venues={}
                for _,venue in ipairs(site.customers)do venues[#venues+1]=venue end
                for _,venue in ipairs(pending or {})do venues[#venues+1]=venue end
                for _,venue in ipairs(providers)do venues[#venues+1]=venue end
            end
            for _,venue in ipairs(venues)do
                local host=snapshot.districts[venue.plot]
                local transactionReady=venue.transaction and not venue.excluded and supplied(site,venue.stage)
                local canPriceYields=snapshot.ExistingConnectionYields and supplied(site,2)
                local wonder=venue.districtType=='DISTRICT_WONDER'
                if host and (host.working or not host.complete and venue.anchorReady) and (venue.transaction or venue.provider)
                    and venue.districtType~='DISTRICT_CITY_CENTER'
                    and (transactionReady or not wonder and canPriceYields)then
                    local key=entry.city..':'..entry.district
                    if not admitted[key]then
                        local definition=GameInfo.Districts[entry.district]
                        local ok,targets=pcall(snapshot.ui.GetLegalDistrictTargets,pid,entry.city,definition.Hash)
                        admitted[key]={}
                        if ok and type(targets)=='table'then
                            for _,index in ipairs(targets)do admitted[key][index]=true end
                        end
                    end
                    local ready=admitted[key][entry.plot]
                    -- QuarterBids intentionally builds a fresh, owned map
                    -- forecast even at full capacity. Keep an otherwise
                    -- suitable footprint while waiting for growth because a
                    -- competing district can consume it before that update.
                    -- The native cache and request gate still decide if the
                    -- Quarter can build. Unknown capacity gives no exception.
                    local waiting=false
                    if not ready and entry.capacityState=='full'then
                        local plot=Map.GetPlotByIndex(entry.plot)
                        waiting=plot and plot:CanHaveDistrict(entry.district,pid,entry.city)
                    end
                    if ready or waiting then
                        add('customerFirst',venue.plot,venue.stage,candidate.quarter,
                            {plot=entry.plot,city=entry.city,district=entry.district,rank=entry.finalQ8,
                             site=site,venue=venue,profile=candidate.profile,transactionReady=transactionReady,
                             wonder=wonder,waiting=waiting})
                    end
                end
            end
        end
    end
    if snapshot.auditConnections then
        local previous=connectionAuditMemory[pid]or{}
        local current,changes={},{}
        for _,ordered in pairs(groups)do for _,group in pairs(ordered)do
            for _,row in pairs(group.plots)do for _,option in ipairs(row.options)do
                local key=table.concat({group.key,option.city,option.district,row.plot},':')
                local observation=option.waiting and key..':capacityWait'or key
                if not previous[observation]and not current[observation]then
                    changes[#changes+1]={key=key,group=group,option=option}
                end
                current[observation]=true
            end end
        end end
        table.sort(changes,function(a,b)return a.key<b.key end)
        for _,change in ipairs(changes)do
            -- Diagnostic only. Current owned, material-safe and native-legal
            -- option. Valuation, selection and construction have later receipts.
            local group,option=change.group,change.option
            if option.waiting then
                print(string.format('CSC_AI_CONNECTION_CAPACITY_WAIT turn=%d player=%d identity=%s',turn,pid,change.key))
            elseif option.wonder then
                print(string.format('CSC_AI_WONDER_CONNECTION_OPPORTUNITY turn=%d player=%d order=customerFirst quarter=%s anchor=%d building=%s city=%d plot=%d',
                    turn,pid,group.quarter,group.anchor,option.venue.building,option.city,option.plot))
            else
                print(string.format('CSC_AI_CONNECTION_OPPORTUNITY turn=%d player=%d identity=%s',turn,pid,change.key))
            end
        end
        connectionAuditMemory[pid]=current
    end
    if snapshot.auditConnectionsOnly then return {} end
    local plans={}
    local function byRank(a,b)
        if (a.waiting==true)~=(b.waiting==true)then return a.waiting~=true end
        if a.rank~=b.rank then return a.rank>b.rank end
        if a.district~=b.district then return a.district<b.district end
        return a.venue.building<b.venue.building
    end
    local function value(option)
        local utility,gains=0,nil
        if option.projected then
            if option.transactionReady then
                local ready=snapshot.ConnectionDistrictTurns(option.city,option.district)
                if not ready then return nil end
                local forecast=M.CustomerBuildingForecast(option.site,{option.venue},option.city,ready,snapshot.Price)
                if not forecast then return nil end
                utility=forecast.valueQ8
            end
            if snapshot.ProjectedConnectionYields then
                gains=snapshot.ProjectedConnectionYields(option.chain,option.district,option.plot,option.purchaseGold)
            end
        else
            if option.transactionReady then
                utility=M.ExistingCustomerConnectionValue(option.site,option.venue,snapshot.Price)
                if utility==nil then return nil end
            end
            if snapshot.ExistingConnectionYields then
                gains=snapshot.ExistingConnectionYields(option.site,option.profile,option.venue.plot)
            end
        end
        for yield,amount in pairs(gains or{})do if amount~=0 then
            -- The private native yield belongs to the prospective customer.
            -- Only the receiving Quarter's real gameplay yield reaches this
            -- local price. The loaded rule starts at the partner foundation
            -- once the receiving Quarter has itself completed.
            local ready=option.site.quarterReady or 0
            local price=snapshot.Price({player=pid,city=option.site.city,yield=yield,amount=amount,ready=ready},option.site.horizon)
            if price==nil then return nil end
            utility=utility+price
        end end
        if option.purchaseGold then
            local invoice=snapshot.Price({player=pid,city=option.city,yield='YIELD_GOLD',
                amount=-option.purchaseGold,ready=0,fixed=true},option.site.horizon)
            if not invoice then return nil end
            utility=utility+invoice
        end
        return utility
    end
    local function competitiveBackup(first,second)
        if not second or not second.valueQ8 or second.valueQ8<=0 then return 0 end
        local a,b=first.option,second.option
        local best,backup
        if a.city==b.city and a.district==b.district then
            if not a.projected then
                -- Whole Quarter bids already reflect the proposed link.
                -- Use the individually priced link as the overlap estimate
                -- so that losing that link enters the footprint cost once.
                -- The remainder still makes a genuinely weaker site a
                -- less useful substitute within the city's same district.
                best,backup=a.rank-first.valueQ8,b.rank-second.valueQ8
            elseif not a.waiting and not b.waiting and snapshot.CustomerNetValue then
                -- The ordinary customer's future building subtotal is common
                -- to this city and district. Compare its two positive native
                -- site values before that aggregation, in the same Q8 units.
                local ready=snapshot.ConnectionDistrictTurns(a.city,a.district)
                if ready then
                    best=snapshot.CustomerNetValue(a.city,a.district,first.plot,ready)
                    backup=snapshot.CustomerNetValue(b.city,b.district,second.plot,ready)
                    if not(best and best>0 and backup and backup>0)then best,backup=nil,nil end
                end
            end
        end
        -- Keep the undiminished fallback for other city/type comparisons or
        -- unknown native quotes. Losing a site never charges more than the
        -- bounded local connection value, even when the native gap is large.
        local disadvantage=best and math.max(0,best-backup)or 0
        return math.max(0,second.valueQ8-disadvantage)
    end
    for _,order in ipairs({'quarterFirst','customerFirst'})do
        local candidates={}
        for _,group in pairs(groups[order])do
            candidates[#candidates+1]=group
            -- Preserve a still-legal identity when another anchor receives
            -- this turn's forecast slots. It will break ties when repriced;
            -- no score from the previous packet survives this way.
            local prior=before[group.key]
            if prior and group.plots[prior]then nextMemory[group.key]=prior end
        end
        table.sort(candidates,function(a,b)return a.key<b.key end)
        -- Rotate each direction independently. This bounds the local ledger
        -- work to eight candidate prices across four groups per player even
        -- when a large empire has many mapped districts.
        local visits={}
        if snapshot.handoffs then
            -- Spend the first available quote on a newly founded partner.
            -- Rotate among simultaneous foundations and leave the other
            -- visit for the ordinary schedule, including competing plans.
            for step=0,#candidates-1 do
                local g=candidates[(turn+pid+step)%#candidates+1]
                local h=snapshot.handoffs[g.key]
                if h and h.record.phase~=h.phase and g.plots[h.plot] then visits[1]=g;break end
            end
        end
        for step=0,#candidates-1 do
            if #visits>=CONNECTION_GROUPS_PER_ORDER then break end
            local g=candidates[(turn+pid+step)%#candidates+1]
            if g~=visits[1] then visits[#visits+1]=g end
        end
        for _,group in ipairs(visits) do
            local handoff=snapshot.handoffs and snapshot.handoffs[group.key]
            local preferred=handoff and handoff.plot or before[group.key]
            local plots={}
            for _,row in pairs(group.plots)do
                table.sort(row.options,byRank)
                row.option=row.options[1]
                plots[#plots+1]=row
            end
            table.sort(plots,function(a,b)
                local aWaiting,bWaiting=a.option.waiting==true,b.option.waiting==true
                if aWaiting~=bWaiting then return not aWaiting end
                if a.option.rank~=b.option.rank then return a.option.rank>b.option.rank end
                if (a.option.purchaseGold or 0)~=(b.option.purchaseGold or 0) then
                    return (a.option.purchaseGold or 0)<(b.option.purchaseGold or 0)
                end
                if (a.plot==preferred)~=(b.plot==preferred)then return a.plot==preferred end
                return a.plot<b.plot
            end)
            local first,second=plots[1],plots[2]
            first.valueQ8=value(first.option)
            if second then second.valueQ8=value(second.option) end
            -- For two sites of the same Quarter in one city, rank already
            -- includes the link, the rest of the CSC forecast and site costs.
            -- An older preferred plot or a higher local exchange alone must
            -- not displace the stronger fresh bid. Keep that plot as a backup.
            local fullQuarterComparison=second and order=='customerFirst'
                and first.option.city==second.option.city and first.option.district==second.option.district
            if second and second.valueQ8 and (not first.valueQ8 or first.valueQ8<=0
                or not fullQuarterComparison and (first.option.waiting==true)==(second.option.waiting==true)
                    and(second.valueQ8>first.valueQ8 or second.valueQ8==first.valueQ8 and second.plot==preferred))then
                first,second=second,first
            end
            if first.valueQ8 and first.valueQ8>0 then
                if handoff then
                    local old=handoff.record
                    local qCity,qDistrict,qPlot=old.city,old.district,old.plot
                    local pCity,pDistrict,pPlot=old.partnerCity,old.partnerDistrict,old.partnerPlot
                    local option=first.option
                    if order=='quarterFirst' then
                        pCity,pDistrict,pPlot=option.city,option.district,first.plot
                    else
                        qCity,qDistrict,qPlot=option.city,option.district,first.plot
                    end
                    local profile=option.profile or option.chain.profile
                    local supply=snapshot.Supply(Map.GetPlotByIndex(qPlot),profile)
                    if supply and #supply.base>0 then
                        local q={city=qCity,district=qDistrict,plot=qPlot}
                        local p={city=pCity,district=pDistrict,plot=pPlot,stage=group.stage}
                        local backup=second and second.plot
                        local nextPlan=C.LayoutRecord(q,p,supply,order=='customerFirst' and backup,
                            order=='quarterFirst' and backup,old,turn)
                        nextPlan.phase=handoff.phase
                        snapshot.nextLayouts[old.city..':'..old.district]=nil
                        snapshot.nextLayouts[qCity..':'..qDistrict]=nextPlan
                        if old.phase~=nextPlan.phase or first.plot~=handoff.plot then
                            print(string.format('CSC_AI_LAYOUT_HANDOFF turn=%d player=%d order=%s anchor=%d planned=%d target=%d valueQ8=%d',
                                turn,pid,order,group.anchor,handoff.plot,first.plot,first.valueQ8))
                        end
                    end
                end
                -- Unpriced options can still be backups. Price two leading
                -- completions even in a rich city, and defer any scarcity
                -- penalty while a third option or unknown quote survives.
                local completeSet=#plots<=2 and (not second or second.valueQ8~=nil)
                local fallback=completeSet and competitiveBackup(first,second)or nil
                local cost=fallback and E.ConnectionLossQ8(first.valueQ8,fallback)or 0
                group.choices={first}
                if second and second.valueQ8 then group.choices[2]=second end
                local target=first.option
                local definition=GameInfo.Districts[target.district]
                local targetCity=snapshot.cities and snapshot.cities[target.city]
                if target.purchaseGold then
                    -- The target can compete in native future-site scoring.
                    -- Use the same finite scarcity budget for acquiring this
                    -- tile and deterring rivals. Native Economic checks its
                    -- own savings and gold before it issues any purchase.
                    local capacity=targetCity and snapshot.DistrictCapacity(targetCity.object)
                    local needsSlot=definition and (definition.RequiresPopulation==1 or definition.RequiresPopulation==true)
                    local ready=snapshot.ConnectionDistrictTurns(target.city,target.district)
                    local net=ready and snapshot.CustomerNetValue(target.city,target.district,first.plot,ready)
                    if net and net>0 and (not needsSlot or capacity and capacity.known and capacity.used<capacity.allowed) then
                        group.purchaseCreditQ8=math.floor(cost/2)
                        group.costQ8=cost-group.purchaseCreditQ8
                        if group.purchaseCreditQ8>0 and snapshot.nextLayouts then
                            local chain=target.chain
                            local quarter={city=chain.city:GetID(),district=chain.profile.district.Index,plot=chain.plot:GetIndex()}
                            local partner={city=target.city,district=target.district,plot=target.plot,
                                stage=group.stage,purchaseGold=target.purchaseGold}
                            local key=quarter.city..':'..quarter.district
                            local supply=snapshot.Supply(chain.plot,chain.profile)
                            local saved=C.LayoutRecord(quarter,partner,supply,nil,second and second.plot,
                                snapshot.savedLayouts[key],turn)
                            saved.phase=1
                            snapshot.nextLayouts[key]=saved
                        end
                    end
                end
                -- One remaining population slot means a different district
                -- here can defer every local backup at once. A credible backup
                -- in another city remains available. Reserve most of the
                -- bounded value at stake for the bid on the actual completion.
                -- The cap is in native Q8 (64 utility); no extra money or order.
                if not target.purchaseGold and completeSet and targetCity and snapshot.DistrictCapacity and definition
                    and(definition.RequiresPopulation==true or definition.RequiresPopulation==1)then
                    local capacity=snapshot.DistrictCapacity(targetCity.object)
                    if capacity and capacity.known and capacity.allowed-capacity.used==1 then
                        local outside=second and second.option.city~=target.city and math.max(0,second.valueQ8)or 0
                        group.pressureBudgetQ8=math.min(CONNECTION_COST_CAP_Q8,math.max(0,first.valueQ8-outside))
                        group.pressureQ8=math.floor(group.pressureBudgetQ8*.75)
                    end
                end
                nextMemory[group.key]=first.plot
                group.best=first;group.backup=second;group.competitiveBackupQ8=fallback;group.costQ8=cost
                plans[#plans+1]=group
            else nextMemory[group.key]=nil end
        end
    end
    connectionMemory[pid]=nextMemory
    return plans
end

function E.ApplyConnectionCosts(snapshot,entries,plans,managed)
    if #plans==0 then return entries end
    local nativeCostAvailable=type(CE_AIDistrictScoresEarlyCost)=='function'
    local occupiedByPlan,byKey={},{}
    for _,entry in ipairs(entries)do byKey[siteKey(entry.city,entry.district,entry.plot)]=entry end
    for _,plan in ipairs(plans)do if plan.costQ8>0 then
        local option=plan.best.option
        local footprintCost=plan.costQ8
        if plan.order~='prospective' and plan.order~='plannedSupply'then
            local completion=byKey[siteKey(option.city,option.district,option.plot)]
            local pressure=completion and completion.connectionPressureQ8 or 0
            footprintCost=math.min(footprintCost,math.max(0,(plan.pressureBudgetQ8 or footprintCost)-pressure))
        end
        -- A prospective plan arrives with its own credit already deducted.
        -- Its marginal quote excludes the income from existing neighbours.
        -- An anchored credit on the same district spends a different budget.
        -- Contending rival costs still merge by largest loss on this tile.
        local plot=plan.best.plot
        local reserve=occupiedByPlan[plot]or{plan=plan,costQ8=0,completion={}}
        occupiedByPlan[plot]=reserve
        -- Several chains can share a customer or future Quarter. Use the
        -- largest individual loss, and exempt any productive retained type.
        -- This avoids stacking whole link prices or blocking shared Hubs.
        for _,option in ipairs(plan.best.options)do reserve.completion[option.district]=true end
        if footprintCost>reserve.costQ8 then reserve.plan=plan;reserve.costQ8=footprintCost end
    end end
    -- Shared completions still contribute their exemptions above. A plot
    -- whose whole loss budget went to a positive bid needs no native quotes.
    local plots={};for plot,reserve in pairs(occupiedByPlan)do
        if reserve.costQ8>0 then plots[#plots+1]=plot end
    end;table.sort(plots)
    for _,index in ipairs(plots)do
        local reserve=occupiedByPlan[index]
        local plan=reserve.plan
        local city=plan.best.option.city
        local plot=Map.GetPlotByIndex(index)
        local targetCity=snapshot.cities and snapshot.cities[city]
        local allowed=targetCity and snapshot.FutureDistrictTypes and snapshot.FutureDistrictTypes(targetCity.object)
        for definition in GameInfo.Districts()do
            local district=definition.Index
            -- Map fit alone also admits foreign uniques and one-per-city
            -- types already built here. Neither can spend this footprint.
            -- Unavailable type facts leave the earlier native quote in charge.
            if district>0 and definition.DistrictType~='DISTRICT_WONDER'
                and definition.InternalOnly~=true and definition.InternalOnly~=1 and not reserve.completion[district]
                and (not allowed or allowed[district])
                and plot:CanHaveDistrict(district,snapshot.id,city)then
                local key=siteKey(city,district,index)
                local entry=byKey[key]
                local cost=reserve.costQ8
                if managed[district]then
                    -- Managed Quarter rows are complete scores at the late
                    -- native reader. Fresh rows are safe to edit once here.
                    cost=entry and not entry.carried and math.min(cost,entry.finalQ8-1)or 0
                    if cost>0 then
                        entry.finalQ8=entry.finalQ8-cost
                    end
                else
                    local existing=entry and entry.delta or 0
                    if not nativeCostAvailable then
                        -- Older Dev CE needs the original read-before-write
                        -- guard to leave native building aggregation in play.
                        local ready=snapshot.ConnectionDistrictTurns(city,district)
                        local net=ready and snapshot.CustomerNetValue(city,district,index,ready)
                        cost=net and math.min(cost,net+existing-1,262144+existing)or 0
                    end
                    if cost>0 then
                        if not entry then
                            entry={player=snapshot.id,city=city,district=district,plot=index,delta=0}
                            entries[#entries+1]=entry
                        end
                        -- The newer consumer uses the exact live NetValue.
                        -- The ordinary residual stays separate so this cost
                        -- cannot change its effect on an invalid/negative cell.
                        if nativeCostAvailable then entry.earlyCostQ8=cost
                        else entry.delta=existing-cost end
                    end
                end
                if cost>0 then
                    entry.connectionCostQ8=cost;entry.connectionOrder=plan.order
                    print(string.format('CSC_AI_CONNECTION_COST turn=%d player=%d city=%d district=%d plot=%d order=%s anchor=%d stage=%d backup=%d costQ8=%d',
                        Game.GetCurrentGameTurn(),snapshot.id,city,district,index,plan.order,plan.anchor,plan.stage,
                        plan.backup and plan.backup.plot or -1,cost))
                end
            end
        end
    end
    for i=#entries,1,-1 do
        local entry=entries[i]
        if entry.finalQ8==nil and entry.delta==0 and not entry.earlyCostQ8 then table.remove(entries,i)end
    end
    return entries
end

function E.ApplyQuarterConnectionCredit(snapshot,entries,plans)
    if #plans==0 then return end
    local credits,pressure={},{}
    for _,plan in ipairs(plans)do if plan.order=='customerFirst'then
        for _,row in ipairs(plan.choices)do
            local key=siteKey(row.option.city,row.option.district,row.plot)
            credits[key]=math.max(credits[key]or 0,row.valueQ8)
        end
        local target=plan.best.option
        local key=siteKey(target.city,target.district,plan.best.plot)
        pressure[key]=math.max(pressure[key]or 0,plan.pressureQ8 or 0)
    end end
    for _,entry in ipairs(entries)do if entry.economy and not entry.carried then
        local key=siteKey(entry.city,entry.district,entry.plot)
        local value=credits[key]or 0
        -- The complete Quarter forecast already includes the real customer.
        -- For a strong site, the recovery limit can scale with the smallest
        -- ordinary siting premium. This gives a larger host city room to
        -- recover actual link value clipped from its bid. Keep the 64-utility
        -- limit on weaker sites and on the separate loss and timing costs.
        local reliefLimit=E.ConnectionCompletionCapQ8
        if (entry.adjacency or 0)+1e-6>=3 and entry.comparisonReferenceQ8 then
            local calibrated=math.floor(entry.comparisonReferenceQ8*MINIMUM_SITING_REFERENCE_FRACTION)
            reliefLimit=math.max(reliefLimit,math.min(STRONG_SITE_LINK_RELIEF_LIMIT_Q8,calibrated))
        end
        local relief=entry.qualityCapQ8 and math.min(value,reliefLimit,
            math.max(0,-(entry.qualityCapAdjustmentQ8 or 0)))or 0
        -- Use the greater of recovery and last-slot pressure. They can
        -- support the same link, and native district and production choices
        -- still compare the resulting bid with their ordinary competitors.
        local credit=math.min(math.max(relief,pressure[key]or 0),4096*256-entry.finalQ8)
        if credit>0 then
            entry.finalQ8=entry.finalQ8+credit
            entry.connectionPressureQ8=math.max(0,credit-relief)
            print(string.format('CSC_AI_CONNECTION_COMPLETION turn=%d player=%d city=%d district=%d plot=%d order=customerFirst creditQ8=%d',
                Game.GetCurrentGameTurn(),snapshot.id,entry.city,entry.district,entry.plot,credit))
        end
    end end
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
        qualityDeferred=0,economicDeferred=0,invoiceDeferred=0,materialDeferred=0,carried=0,managed=true,
        capacityReady=0,capacityFull=0,capacityUnknown=0}
    local player,pid=snapshot.player,snapshot.id
    if (E.AnchoredConnectionsEnabled or E.AnchoredConnectionAuditEnabled) and snapshot.ConnectionDistrictTurns then
        snapshot.captureConnections=true;snapshot.connectionQuarters={}
        snapshot.auditConnections=E.AnchoredConnectionAuditEnabled
        snapshot.auditConnectionsOnly=not E.AnchoredConnectionsEnabled
    end
    snapshot.planState=planState(pid)
    if snapshot.planState then snapshot.planState.nextLayouts=nil end
    snapshot.planCustomerPurchases=E.ProspectiveConnectionsEnabled and E.AnchoredConnectionsEnabled
    local visibility=PlayersVisibility[pid]
    reconcilePlans(snapshot)
    restoreLayouts(snapshot,profiles)
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
                        local minimum=E.PlacementMinimumAdjacency(geometry)
                        local belowMinimum=geometry.upper+1e-6<minimum
                        -- A supply-backed site below the individual floor can
                        -- qualify with a concrete partner. Admit it to the
                        -- forecast only if the city has a mapped footprint.
                        local supply=(not belowMinimum or E.ProspectiveConnectionsEnabled) and snapshot.Supply and snapshot.Supply(plot,profile)
                        local screenedOptions=belowMinimum and E.ProspectiveConnectionsEnabled and E.AnchoredConnectionsEnabled
                            and supply and #supply.base>0 and not protectedPlots[plot:GetIndex()] and snapshot.CustomerOptions
                            and snapshot.CustomerOptions(city,plot,profile,protectedPlots,true,true)
                        if belowMinimum and not (screenedOptions and #screenedOptions>0) then
                            stats.qualityDeferred=stats.qualityDeferred+1
                            evaluations[id]={reason='below_adjacency',adjacency=geometry.upper,owner=owner}
                            if activePlan(snapshot,city:GetID(),profile.district.Index,plot:GetIndex())then
                                C.Withdraw(snapshot.planState,city:GetID(),profile.district.Index,plot:GetIndex(),'below_adjacency')
                            end
                        elseif supply and #supply.base==0 then
                            -- This same Base gate is enforced after valuation.
                            -- Apply it cheaply first to avoid evaluating native
                            -- site costs for a geometry made only of Spec.
                            stats.qualityDeferred=stats.qualityDeferred+1
                            evaluations[id]={reason='no_base',adjacency=geometry.upper,owner=owner}
                            local plan=activePlan(snapshot,city:GetID(),profile.district.Index,plot:GetIndex())
                            if C and plan then C.Withdraw(snapshot.planState,plan.city,plan.district,plan.plot,'no_base')end
                        elseif protectedPlots[plot:GetIndex()]then
                            -- An empirical spatial preference must never buy
                            -- its way through the existing protected-material
                            -- map. Customer planning already honours it; new
                            -- Quarter planning uses that same cross-quarter
                            -- guard before any expensive valuation or invoice.
                            stats.materialDeferred=stats.materialDeferred+1
                            evaluations[id]={reason='protected_material',adjacency=geometry.upper,owner=owner}
                            local plan=activePlan(snapshot,city:GetID(),profile.district.Index,plot:GetIndex())
                            if C and plan then C.Withdraw(snapshot.planState,plan.city,plan.district,plan.plot,'protected_material')end
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
                                    protection[id],ignoredLegacy[id],covers,protectedPlots,screenedOptions)
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
                                                dockmasterHarborPlot=site and site.completedHarborPlot,
                                                economicQ8=quote and quote.valueQ8,preferenceQ8=quote and bid-quote.valueQ8,
                                                forecastAdjustmentQ8=quote and quote.forecastAdjustmentQ8,
                                                nativeSiteAdjustmentQ8=quote and quote.siteAdjustmentQ8,
                                                evaluationHorizon=site and site.horizon,
                                                evaluationDiscountQ8=snapshot.evaluationContext and snapshot.evaluationContext.discountQ8,
                                                comparisonReferenceQ8=site and site.comparisonReferenceQ8,
                                                qualityCapQ8=parts and parts.qualityCapQ8,
                                                qualityCapAdjustmentQ8=parts and parts.capAdjustmentQ8,
                                                adjacencyPreferenceQ8=parts and parts.adjacencyQ8,materialPreferenceQ8=parts and parts.materialsQ8,
                                                layoutPreferenceQ8=parts and parts.layoutQ8,protectionPenaltyQ8=parts and parts.penaltyQ8,
                                                customerLayout=site and site.spatialPlan.links or{},
                                                -- A bid at the native ceiling can retain this
                                                -- customer footprint for the other decision.
                                                strongLayout=parts and parts.strongLayout or nil,
                                                prospectiveLayout=parts and site and site.prospectiveLayout or nil,
                                                pairedAdjacency=site and site.pairAdjacencyGain and quote and quote.adjacency+site.pairAdjacencyGain,
                                                pairReady=site and site.pairReady,
                                                ordinaryBidQ8=parts and parts.ordinaryBidQ8,
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
                                            local entry=result[#result]
                                            local primary,prospect=entry.strongLayout,entry.prospectiveLayout
                                            -- A second qualified footprint shares this site's bid.
                                            -- Only the primary layout earned the quoted site premium.
                                            -- A one-Base forecast can have just the prospective
                                            -- layout. An array starting with nil skips that case.
                                            local function reportLayout(layout)
                                                print(string.format('CSC_AI_STRONG_QUARTER_LAYOUT turn=%d player=%d city=%d district=%d plot=%d customerCity=%d customerDistrict=%d customerPlot=%d stage=%d existing=%s extraBase=%s specialty=%s capacity=%s frontier=%s creditQ8=%d',
                                                    Game.GetCurrentGameTurn(),pid,city:GetID(),profile.district.Index,
                                                    plot:GetIndex(),layout.city,layout.district or -1,layout.plot,layout.stage,
                                                    tostring(layout.existing),tostring(layout.extraBase),tostring(layout.hasSpec),
                                                    capacityState,tostring(frontier),layout==primary and parts.strongLayoutQ8 or 0))
                                            end
                                            if primary then reportLayout(primary) end
                                            if prospect and prospect~=primary then reportLayout(prospect) end
                                            if snapshot.captureConnections and (not frontier or E.ProspectiveConnectionsEnabled) and site
                                                and not evaluation.carried and bid>0 then
                                                snapshot.connectionQuarters[#snapshot.connectionQuarters+1]=
                                                    {entry=result[#result],site=site,quarter=profile.key,profile=profile}
                                            end
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
    if snapshot.CustomerFirstOptions then
        result=E.MergeCustomerOffers(result,E.CustomerOffers(snapshot,result,protectedPlots))
    end
    -- A founded Quarter can continue the geometric customer hint identified
    -- by its prior offer. Current candidate legality rechecks the target below;
    -- no Quarter score, spent-cost bonus or native reservation is transferred.
    snapshot.customerFoundationHints={}
    for _,entry in ipairs(previous or{})do
        local host=snapshot.districts and snapshot.districts[entry.plot]
        if entry.player==snapshot.id and entry.economy and host and host.type==entry.district and host.city==entry.city then
            for _,link in ipairs(entry.customerLayout or{})do
                snapshot.customerFoundationHints[link.city..':'..link.district]=link.plot
            end
            local layout=E.ProspectiveConnectionsEnabled and entry.prospectiveLayout or entry.strongLayout
            if layout and not layout.existing then
                snapshot.customerFoundationHints[layout.city..':'..layout.district]=layout.plot
            end
        end
    end
    for key,index in pairs(snapshot.partnerHints or {}) do snapshot.customerFoundationHints[key]=index end
    local plans={}
    if snapshot.CustomerCandidateSets then
        local offers,_,priced=E.CustomerEconomicOffers(snapshot,protectedPlots)
        result=E.MergeCustomerOffers(result,offers)
        plans=priced or plans
    end
    if snapshot.captureConnections then
        E.ApplyQuarterConnectionCredit(snapshot,result,plans)
        -- Combine before forming packet entries. The footprint allocator
        -- takes the largest loss per tile, even if an established chain and
        -- a new layout both have a claim on the same resource-free land.
        local costs,credits=E.ProspectiveConnectionPlans(snapshot,protectedPlots)
        -- Several sellers may support the same paid footprint. Publish one
        -- acquisition offer using the strongest freshly priced marginal.
        local paid={}
        for _,plan in ipairs(plans) do
            if (plan.purchaseCreditQ8 or 0)>0 then
                local option=plan.best.option
                local key=siteKey(option.city,option.district,option.plot)
                if not paid[key] or plan.purchaseCreditQ8>paid[key].valueQ8 then
                    paid[key]={city=option.city,district=option.district,plot=option.plot,
                        purchaseGold=option.purchaseGold,valueQ8=plan.purchaseCreditQ8}
                end
            end
        end
        for _,offer in pairs(paid) do credits[#credits+1]=offer end
        result=E.ApplyProspectiveConnectionCredit(snapshot,result,credits)
        for _,plan in ipairs(plans)do costs[#costs+1]=plan end
        result=E.ApplyConnectionCosts(snapshot,result,costs,managed)
        -- Proposed opportunities and costs. Actual consumption is visible in
        -- CE's early net or late managed journal on the matching packet.
        for _,plan in ipairs(plans)do
            print(string.format('CSC_AI_CONNECTION_PLAN turn=%d player=%d order=%s anchor=%d stage=%d city=%d district=%d plot=%d valueQ8=%d backup=%d backupQ8=%d costQ8=%d pressureQ8=%d capacityWait=%s competitiveBackupQ8=%s',
                Game.GetCurrentGameTurn(),pid,plan.order,plan.anchor,plan.stage,plan.best.option.city,
                plan.best.option.district,plan.best.plot,plan.best.valueQ8,plan.backup and plan.backup.plot or -1,
                plan.backup and plan.backup.valueQ8 or 0,plan.costQ8,plan.pressureQ8 or 0,tostring(plan.best.option.waiting==true),
                tostring(plan.competitiveBackupQ8)))
        end
    end
    if snapshot.WorldStats then
        local work=snapshot.WorldStats()
        print(string.format('CSC_AI_JOINT_WORK turn=%d player=%d worlds=%d evaluations=%d budgetFailures=%d unknown=%d cacheHits=%d routeHits=%d routeMisses=%d routeOverflow=%d',
            Game.GetCurrentGameTurn(),snapshot.id,work.worlds,work.evaluations,work.budgetFailures,work.unknown,work.cacheHits,
            work.routeHits,work.routeMisses,work.routeOverflow))
    end
    E.ReportQuarterFunnel(snapshot,evaluations)
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
        print(string.format('CSC_AI_SPATIAL_BID turn=%d player=%d city=%d district=%d plot=%d rank=%d adjacency=%.3f economicQ8=%d forecastAdjustmentQ8=%d nativeSiteAdjustmentQ8=%d horizon=%d discountQ8=%d referenceQ8=%d qualityCapQ8=%d capAdjustmentQ8=%d adjacencyPreferenceQ8=%d materialPreferenceQ8=%d layoutPreferenceQ8=%d protectionPenaltyQ8=%d finalQ8=%d customerPlot1=%d customerType1=%d customerPlot2=%d customerType2=%d dockmasterHarborPlot=%d',
            Game.GetCurrentGameTurn(),pid,entry.city,entry.district,entry.plot,rank,entry.adjacency,
            entry.economicQ8,entry.forecastAdjustmentQ8 or 0,entry.nativeSiteAdjustmentQ8 or 0,
            entry.evaluationHorizon or 50,entry.evaluationDiscountQ8 or 1024,
            entry.comparisonReferenceQ8 or 0,entry.qualityCapQ8 or 0,entry.qualityCapAdjustmentQ8 or 0,
            entry.adjacencyPreferenceQ8,entry.materialPreferenceQ8,
            entry.layoutPreferenceQ8,entry.protectionPenaltyQ8,entry.finalQ8,
            first and first.plot or -1,first and first.district or -1,
            second and second.plot or -1,second and second.district or -1,entry.dockmasterHarborPlot or -1))
    end end
    if snapshot.SpatialStats then
        local spatial=snapshot.SpatialStats()
        -- Havok's os.clock can be a constant zero. Mark it unavailable rather
        -- than claiming a measured zero-cost pass; host turn timings remain
        -- in the shared controller journal.
        local elapsed=started and clock()-started
        local costs=snapshot.nativeSiteStats or{}
        print(string.format('CSC_AI_SPATIAL_WORK turn=%d player=%d maps=%d adjacencyReads=%d unavailable=%d laggedReads=%d options=%d nativeSiteQuotes=%d emptySiteQuotes=%d unavailableSiteQuotes=%d economyMs=%.3f',
            Game.GetCurrentGameTurn(),pid,spatial.maps,spatial.adjacencyReads,spatial.unavailable,spatial.laggedReads,spatial.options,
            costs.native or 0,costs.empty or 0,costs.unavailable or 0,
            elapsed and elapsed>0 and elapsed*1000 or -1))
    end
    if snapshot.nextLayouts then snapshot.planState.nextLayouts=snapshot.nextLayouts end
    return result,stats
end

function E.BuildingValue(snapshot,chain,building)
    local site=chain.economy or snapshot.Site(chain.city,chain.plot,chain.profile)
    return site and M.Marginal(site,building,snapshot.Price)
end

function E.ProducerInvestment(snapshot,chain,options)
    local site=chain.economy
    if site then return M.ProducerInvestment(site,options,snapshot.Price)end
end

function E.StageTwoCustomerValue(snapshot,chain,buyer,footprint,building)
    -- The existing-site facts already resolve the active civ's building
    -- variant and its inherited transaction. Match the real legal receiver.
    local site=chain.economy
    for _,customer in ipairs(site and site.customers or{})do
        if customer.city==buyer:GetID() and customer.plot==footprint
            and customer.building==building.BuildingType and customer.stage==2 then
            return M.StageTwoCustomerValue(site,customer,snapshot.Price)
        end
    end
end

local function stageFourSuppliers(snapshot,chain)
    -- Consider the actual working suppliers and at most one feasible job
    -- for a missing class. The ledger retains each job's material ETA and
    -- charges one share of a Builder for each distinct new improvement.
    local site,selected,jobs=chain.economy,{},{}
    for _,kind in ipairs({'base','specialty'})do
        local legal={}
        for _,material in ipairs(chain.supply[kind]or{})do
            if material.ready then legal[material.plot]=material end
        end
        local working,pending=false,nil
        for _,supplier in ipairs(site.suppliers)do
            local fact=legal[supplier.plot]
            if supplier.kind==kind and fact then
                if supplier.ready==0 and fact.working then
                    selected[#selected+1]=supplier;working=true
                elseif supplier.ready>0 and supplier.ready<site.horizon
                    and (not pending or supplier.ready<pending.ready
                        or supplier.ready==pending.ready and supplier.plot<pending.plot)then
                    pending=supplier
                end
            end
        end
        if not working then
            if not pending then return nil end
            selected[#selected+1]=pending
            -- Repair consumes movement and its ready-time allowance, but
            -- native execution preserves the Builder charge.
            if not legal[pending.plot].repairable then jobs[pending.plot]=true end
        end
    end
    if not next(jobs)then return selected,0 end
    local cost=snapshot.SupplierChargeCost(site.city)
    if not cost then return nil end
    local count=0
    for _ in pairs(jobs)do count=count+1 end
    return selected,cost*count
end

function E.LaterStageInvestments(snapshot,research,nominations,nominationLimit)
    -- Reuse the established city/building comparison and final research-goal
    -- packet. No new queue order is created here. Physical customer groups
    -- combine every connected working source before pricing one building.
    if #snapshot.chains>64 then return end
    local byBuilding,customerGroups={},{}
    for _,bid in ipairs(nominations)do byBuilding[bid.city..':'..bid.building]=bid end
    local function allowed(city,definition)
        return nominationLimit>0 and type(snapshot.ui.CanProduceItem)=='function'
            and snapshot.ui.CanProduceItem(snapshot.id,city,definition.Hash)==true
    end
    local function nominate(city,definition,value,reason)
        local raw=math.floor(value or 0)
        local delta=math.min(nominationLimit,LATER_BUILDING_CAP_Q8,raw)
        if delta<=0 then return end
        local key=city..':'..definition.Index
        local previous=byBuilding[key]
        if previous then
            if delta>previous.delta then previous.stageReason=reason;previous.stageRawQ8=raw end
            previous.delta=math.max(previous.delta,delta)
            previous.queueDelta=math.max(previous.queueDelta or 0,delta)
        else
            local offer={player=snapshot.id,city=city,building=definition.Index,delta=delta,queueDelta=delta,
                stageReason=reason,stageRawQ8=raw}
            nominations[#nominations+1]=offer;byBuilding[key]=offer
        end
    end
    local function considerProducer(chain,site,field)
        local building=site[field]
        if not building or building.present or building.working or building.excluded or building.prerequisites
            or not building.unlock or not building.turns
            or building.unlock+building.turns>=site.horizon then return end
        local definition=GameInfo.Buildings[building.type]
        if not definition or not snapshot.MaterialBuyerPrerequisitesMet(chain,definition)
            or snapshot.MaterialBuyerCommitment(chain.city,{definition},site.horizon)then return end
        local tech=snapshot.UnownedResearch('tech',definition.PrereqTech)
        local civic=snapshot.UnownedResearch('civic',definition.PrereqCivic)
        local researching=tech~=nil or civic~=nil
        -- Submit a locked producer through its one missing research target.
        -- A building nomination here could let native preparation bypass
        -- the separate population-10 construction policy.
        if researching then
            if not research or tech and civic or site.population<7 then return end
        elseif site.population<10 or not allowed(site.city,definition)then return end
        local suppliers,cost
        if field=='fourth'then
            suppliers,cost=stageFourSuppliers(snapshot,chain)
            if not suppliers then return end
        end
        local value=M.StageBuildingInvestment({{site=site,producer=field,building=building,
            suppliers=suppliers,developmentCost=cost and cost>0 and cost or nil}},snapshot.Price)
        if not value or value<=0 then return end
        if researching then
            local kind,index=tech and 'tech'or'civic',tech or civic
            local key=kind..':'..index
            local offer=research[key]or{player=snapshot.id,kind=kind,index=index,value=0,jobs={}}
            offer.producerCities=offer.producerCities or{}
            local previous=offer.producerCities[site.city]or 0
            local gain=math.max(0,value-previous)
            -- Distinct cities may invest after the same unlock. One city
            -- earns only its strongest project while it has one queue.
            offer.producerCities[site.city]=math.max(value,previous)
            offer.producerQ8=(offer.producerQ8 or 0)+gain
            offer.value=offer.value+gain;research[key]=offer
        else nominate(site.city,definition,value,field)end
    end
    if nominationLimit<=0 and not research then return end
    for _,chain in ipairs(snapshot.chains)do
        local site=chain.economy
        if chain.ready and site then
            if site.population>=7 then
                considerProducer(chain,site,'third')
                considerProducer(chain,site,'fourth')
            end
            if nominationLimit>0 then for _,customer in ipairs(site.customers)do
                local producer=customer.stage==3 and site.third or customer.stage==4 and site.fourth
                if producer and producer.working and customer.complete and not customer.present and not customer.working
                    and not customer.excluded and not customer.prerequisites and customer.unlock==0
                    and customer.turns<site.horizon then
                    local definition=GameInfo.Buildings[customer.type]
                    if definition then
                        local key=customer.city..':'..definition.Index
                        local group=customerGroups[key]
                        if not group then
                            group={city=customer.city,plot=customer.plot,definition=definition,links={},sites={},
                                allowed=allowed(customer.city,definition)}
                            customerGroups[key]=group
                        end
                        if group.allowed and group.plot==customer.plot then
                            local link=group.sites[site.key]
                            if not link then
                                link={site=site,customers={}};group.sites[site.key]=link
                                group.links[#group.links+1]=link
                            end
                            link.customers[#link.customers+1]=customer
                        end
                    end
                end
            end end
        end
    end
    -- Stable order keeps equally priced physical orders reproducible.
    local keys={};for key in pairs(customerGroups)do keys[#keys+1]=key end;table.sort(keys)
    for _,key in ipairs(keys)do
        local group=customerGroups[key]
        if #group.links>0 then
            nominate(group.city,group.definition,M.StageBuildingInvestment(group.links,snapshot.Price),'customer')
        end
    end
end

function E.ServiceResearch(snapshot,research)
    -- Use only this empire's existing Quarter snapshot. Material repair
    -- supplies the same actual Housing baseline; topic pooling applies all
    -- new effects together before the bridge compares research goals.
    local sites,housing={},nil
    for _,chain in ipairs(snapshot.chains)do
        local site=chain.economy
        if chain.ready and site and site.services and #site.services>0 then
            sites[#sites+1]=site
            for _,service in ipairs(site.services)do
                if service.kind=='HOUSING'and service.known and service.researchTopic then
                    local facts=snapshot.MaterialHousing(site)
                    if facts then
                        -- Keep memoized site facts immutable while
                        -- collecting receiving cities across chains.
                        housing=housing or{cities={},activeCities={},stop=facts.stop,quarter=facts.quarter,half=facts.half}
                        for id,city in pairs(facts.cities)do housing.cities[id]=city end
                    end
                    break
                end
            end
        end
    end
    for key,quote in pairs(M.ServiceResearchOffers(sites,housing,snapshot.evaluationContext.horizon,snapshot.Price))do
        local offer=research[key]or{player=snapshot.id,kind=quote.kind,index=quote.index,value=0,jobs={}}
        offer.value=offer.value+quote.value
        offer.serviceQ8=quote.value
        offer.serviceChains=0
        for _ in pairs(quote.chains)do offer.serviceChains=offer.serviceChains+1 end
        research[key]=offer
    end
end

-- Quote the ordinary transactions and the contingent Service separately in
-- signed Q8. The Builder policy can credit the Service once across competing
-- jobs. Missing ordinary pricing leaves the resulting offer unavailable.
function E.MaterialJobValue(snapshot,chain,kind,plot,improvement,workTurn,pendingBuyer)
    local streams=snapshot.MaterialJobStreams and snapshot.MaterialJobStreams(chain,kind,plot,improvement,workTurn,pendingBuyer)
    if not streams then return nil end
    local q8,serviceQ8=0,0
    local site=chain.economy
    for _,stream in ipairs(streams) do
        local value=snapshot.Price(stream,site.horizon)
        if type(value)~='number' then return nil end
        q8=q8+value
    end
    if not pendingBuyer and site.services and #site.services>0 then
        local housing=snapshot.MaterialHousing and snapshot.MaterialHousing(site)
        for _,stream in ipairs(M.MaterialServiceStreams(site,kind,workTurn or 5,housing))do
            local value=snapshot.Price(stream,site.horizon)
            if type(value)=='number'then serviceQ8=serviceQ8+value end
        end
    end
    -- Bids can compare which single job restores these benefits. The separate
    -- Service subtotal keeps two alternative jobs from each claiming the same
    -- activation when pricing additional Builder charges.
    return q8,serviceQ8
end

function E.SupplyValue(snapshot,chain,plot)
    local site=chain.economy or snapshot.Site(chain.city,chain.plot,chain.profile)
    if not site then return nil end
    -- This delta enters other-district placement protection (Problem2.2), so
    -- keep prospective Services deferred here too. Structural critical-supplier
    -- protection still observes the real chain. Actual building/repair consumers
    -- retain the cached Service-aware site; never mutate that shared record.
    local ordinary={};for k,v in pairs(site)do ordinary[k]=v end
    ordinary.service=nil;site=ordinary
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
