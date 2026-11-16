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
    local snapshot=F.New(player,placement,ui,context)
    snapshot.evaluationContext=context or{horizon=50,discountQ8=4*256,nativeSite=false}
    local discount=snapshot.evaluationContext.discountQ8
    local quotes={};local count=0
    local function rawPrice(stream,horizon,amount)
        local yield=stream.yield
        horizon=math.min(horizon,stream.finish or horizon)
        if stream.ready>=horizon then return 0 end
        if yield=='GROWTH'or yield=='NAVAL_PRODUCTION_PERCENT'then
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
        local key=table.concat({stream.city,yield,units,stream.ready,horizon,tostring(stream.fixed==true)},':')
        if quotes[key]~=nil then return quotes[key]end
        local value
        if yield=='AMENITY'then
            value=CE_AIAmenityStreamValue(snapshot.id,stream.city,amount,stream.ready,horizon,discount)
        else
            local definition=GameInfo.Yields[yield]
            if not definition then return nil end
            if stream.fixed then
                value=CE_AIYieldFixedValue(snapshot.id,stream.city,definition.Index,units,stream.ready,discount)
            else
                value=CE_AIYieldStreamValue(snapshot.id,stream.city,definition.Index,units,stream.ready,horizon,discount)
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
        if not context or depth<=0 or stream.amount<=0 or stream.yield=='AMENITY'or stream.fixed then return raw,raw end
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
    if quote.adjacency+1e-6<E.PlacementMinimumAdjacency(site) or (site.baseCount or 0)<1 then return E.DeferredQuarterQ8,'quality'end
    -- Only named supply loss enters the complete ledger. Old no-host/readiness
    -- heuristics were ownership-dependent and duplicated its own valuation.
    -- Missing customer space loses its current layout preference/income; it
    -- does not acquire a hidden128-utility penalty when land becomes owned.
    local penalty=math.max(0,protectionQ8 or 0)
    if coversOwnMaterial then penalty=math.max(penalty,256*256)end
    local economic=quote.valueQ8-penalty
    if economic<=0 then return economic,'economics'end
    local value=(quote.bidValueQ8 or quote.valueQ8)-penalty
    local premium
    local reference=site.comparisonReferenceQ8
    -- An admitted +1 Harbor/Tailors uses the minimum siting band and the same
    -- weak-site cap as +2. Keep the real +1 in the ledger/logs; extrapolating
    -- the +2..+3 formula backwards would create a negative preference. This
    -- small exception earns no Dockmaster income and cannot lift a losing
    -- economic ledger into a bid. Stronger Quarters retain their usual bands.
    local sitingAdjacency=math.max(E.MinimumAdjacency,quote.adjacency)
    if reference then
        -- Spatial policy, kept separate from actual economic income. At the
        -- early600 reference, +2/+3/+4 preferences are48/240/600. Strong +4
        -- quarters with positive economics can beat typical +2 native bids;
        -- +2 sites retain a useful offer but cannot inflate into top-tier bids
        -- merely from a later generic amenity forecast. Actual native units,
        -- timing, material losses and production competition stay in force.
        local adjacency=math.min(6,sitingAdjacency)
        local fraction=adjacency<3 and(.08+.32*(adjacency-2))or(.4+.6*(adjacency-3))
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
    local proposed=value+premium+(materials+layout)*256
    local qualityCap
    if reference then
        local extra=math.max(0,math.min(4,sitingAdjacency-2))
        qualityCap=reference*(.5+.65*math.min(1,extra)+.6*math.max(0,extra-1))
        proposed=math.min(proposed,qualityCap)
    end
    local bid=math.floor(math.max(-4096*256,math.min(4096*256,proposed))+.5)
    return bid,'positive',{adjacencyQ8=math.floor(premium+.5),materialsQ8=materials*256,
        layoutQ8=layout*256,penaltyQ8=penalty,forecastQ8=(quote.bidValueQ8 or quote.valueQ8)-quote.valueQ8,
        qualityCapQ8=qualityCap and math.floor(qualityCap+.5),
        capAdjustmentQ8=bid-value-math.floor(premium+.5)-(materials+layout)*256}
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
        -- The native site residual already includes the native land invoice
        -- on a frontier footprint. Keep the UI invoice for affordability and
        -- ownership diagnostics, but do not charge a second Gold payment.
        site.purchaseGold=site.nativeSiteIncludesPurchase and 0 or invoice
        if site.nativeSiteAdjustmentQ8~=nil then site.footprintCostMode='native_site'end
        site.spatialPlan=E.SpatialPlan(snapshot.CustomerOptions
            and snapshot.CustomerOptions(city,plot,profile,protected)or{})
        -- District siting currently prices ordinary CSC transactions only.
        -- Service opportunity/demand valuation is deferred for BOTH Quarters
        -- and customer districts. Copy the cached site so actual building/
        -- repair marginals retain their existing narrow Stage2 Service input.
        local transactionSite={};for k,v in pairs(site)do transactionSite[k]=v end
        transactionSite.service=nil
        local ok,value,message=pcall(M.Forecast,transactionSite,snapshot.Price,function(alternative)
            return E.PlacementValue(alternative,site,protectionQ8,covers)
        end)
        if ok then quote,reason=value,message else reason=tostring(value)end
        if quote then
            bid,details.reason,parts=E.PlacementValue(quote,site,protectionQ8,covers)
            details.economicQ8=quote.valueQ8;details.afterProtectionQ8=quote.valueQ8-(parts and parts.penaltyQ8 or math.max(protectionQ8 or 0,covers and 256*256 or 0))
            details.forecastAdjustmentQ8=quote.forecastAdjustmentQ8 or 0
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
                    print(string.format('CSC_AI_CUSTOMER_FUTURE_LINK turn=%d player=%d city=%d district=%d plot=%d quarterCity=%d quarterDistrict=%d quarterPlot=%d base=%d spec=%d basePlots=%s specPlots=%s ordinaryAdjacency=%.3f bestOrdinaryAdjacency=%.3f contributionQ8=%d',
                        Game.GetCurrentGameTurn(),snapshot.id,offer.city,offer.district,offer.plot,
                        option.quarterCity,option.quarterDistrict,option.quarterPlot,option.baseCount,option.specialtyCount,
                        table.concat(option.basePlots,','),table.concat(option.specialtyPlots,','),
                        option.adjacency,option.bestAdjacency,link.preference*256))
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
                        local minimum=E.PlacementMinimumAdjacency(geometry)
                        local supply=geometry.upper+1e-6>=minimum and snapshot.Supply and snapshot.Supply(plot,profile)
                        if geometry.upper+1e-6<minimum then
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
    if snapshot.CustomerFirstOptions then
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
    return result,stats
end

function E.BuildingValue(snapshot,chain,building)
    local site=chain.economy or snapshot.Site(chain.city,chain.plot,chain.profile)
    return site and M.Marginal(site,building,snapshot.Price)
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
