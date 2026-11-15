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

function E.PlacementValue(quote,site,legacyDelta,coversOwnMaterial)
    if quote.adjacency+1e-6<E.MinimumAdjacency or (site.baseCount or 0)<1 then return E.DeferredQuarterQ8,'quality'end
    local penalty=math.max(0,-(legacyDelta or 0))
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
                        delta=link.preference*256,customer=true,spatial=true}
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

function E.QuarterBids(snapshot,placement,protectedPlots,early)
    local clock=os and os.clock
    local started=clock and clock()
    local result,prior,managed={},{},{}
    local profiles=placement.StageTwoProfiles()
    for _,profile in ipairs(profiles)do managed[profile.district.Index]=true end
    for _,entry in ipairs(early)do prior[entry.city..':'..entry.district..':'..entry.plot]=entry end
    local stats={evaluated=0,final=0,unknown=0,buyerBlocked=0,streams=0,omissions=0,
        qualityDeferred=0,economicDeferred=0,invoiceDeferred=0,managed=true,
        capacityReady=0,capacityFull=0,capacityUnknown=0}
    local player,pid=snapshot.player,snapshot.id
    local visibility=PlayersVisibility[pid]
    for _,profile in ipairs(profiles)do
        for _,city in player:GetCities():Members()do
            if not city:GetDistricts():HasDistrict(profile.district.Index)then
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
                        local geometry=snapshot.Geometry(city,plot,profile)
                        if geometry.upper+1e-6<E.MinimumAdjacency then stats.qualityDeferred=stats.qualityDeferred+1
                        else
                            local invoice=0
                            if frontier then invoice=snapshot.ui.GetRawPlotPurchaseQuote(pid,city:GetID(),plot:GetIndex())end
                            if invoice==nil or invoice<0 then stats.invoiceDeferred=stats.invoiceDeferred+1
                            else
                                local old=prior[city:GetID()..':'..profile.district.Index..':'..plot:GetIndex()]
                                local resource=GameInfo.Resources[plot:GetResourceType()]
                                local covers=resource and(CSC_Adjacency.HasTag(profile.base,resource.ResourceType)
                                    or CSC_Adjacency.HasTag(profile.specialty,resource.ResourceType))
                                local site,reason=snapshot.Site(city,plot,profile)
                                local quote
                                if site then
                                    site.purchaseGold=invoice
                                    site.spatialPlan=E.SpatialPlan(snapshot.CustomerOptions
                                        and snapshot.CustomerOptions(city,plot,profile,protectedPlots)or{})
                                    quote,reason=M.Forecast(site,snapshot.Price,function(alternative)
                                        return E.PlacementValue(alternative,site,old and old.delta,covers)
                                    end)
                                end
                                if not quote then
                                    stats.unknown=stats.unknown+1
                                    if stats.unknown<=3 then print(string.format('CSC_AI_ECONOMY_QUOTE_UNAVAILABLE turn=%d player=%d city=%d plot=%d reason=%s',
                                        Game.GetCurrentGameTurn(),pid,city:GetID(),plot:GetIndex(),tostring(reason)))end
                                else
                                    local bid,why,parts=E.PlacementValue(quote,site,old and old.delta,covers)
                                    stats.streams=stats.streams+#quote.streams;stats.omissions=stats.omissions+#quote.omissions
                                    if why=='quality'then stats.qualityDeferred=stats.qualityDeferred+1
                                    elseif why=='economics'then stats.economicDeferred=stats.economicDeferred+1
                                    else
                                        -- A correct invoice alone does not prove
                                        -- this city will be the native buyer.
                                        if frontier and snapshot.ui.GetPlotPurchaseQuote(pid,city:GetID(),plot:GetIndex())==nil then
                                            stats.buyerBlocked=stats.buyerBlocked+1
                                        else
                                            result[#result+1]={player=pid,city=city:GetID(),district=profile.district.Index,
                                                plot=plot:GetIndex(),delta=0,finalQ8=bid,economy=true,adjacency=quote.adjacency,
                                                economicQ8=quote.valueQ8,preferenceQ8=bid-quote.valueQ8,
                                                adjacencyPreferenceQ8=parts.adjacencyQ8,materialPreferenceQ8=parts.materialsQ8,
                                                layoutPreferenceQ8=parts.layoutQ8,protectionPenaltyQ8=parts.penaltyQ8,
                                                customerLayout=site.spatialPlan.links,
                                                startingAdjacency=site.startingAdjacency,startingGold=site.startingGold,
                                                quarterReadyEstimate=site.quarterReady,
                                                -- Gross adjacency-Gold payback AFTER Quarter
                                                -- completion; not net profit or native saving ETA.
                                                startingGoldPaybackTurns=frontier and (site.startingGold or 0)>0
                                                    and invoice/site.startingGold or nil,
                                                baseCount=site.baseCount,specialtyCount=site.specialtyCount,
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
    -- Retain bounded candidate-surface evidence in ordinary main-mod logs:
    -- two leading sites per city/type, with economic and spatial components.
    -- Older winner-only captures cannot reconstruct the losing site margins.
    -- These are published proposals, never a receipt of native acceptance.
    local groups={}
    for _,entry in ipairs(result)do if entry.economy then
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
        print(string.format('CSC_AI_SPATIAL_WORK turn=%d player=%d maps=%d adjacencyReads=%d unavailable=%d options=%d economyMs=%.3f',
            Game.GetCurrentGameTurn(),pid,spatial.maps,spatial.adjacencyReads,spatial.unavailable,spatial.options,
            started and (clock()-started)*1000 or -1))
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
