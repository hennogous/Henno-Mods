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

-- Initial siting preferences are native Q8 utility, not additional gameplay
-- yields. +3/+4/+5/+6+ profitable sites receive +96/+192/+288/+384 utility;
-- both material classes add16 for later-stage flexibility. These bounded bands
-- are estimates against observed native improvement bids around163 utility.
-- They do not make an otherwise losing investment profitable or guarantee it
-- beats another district/unit. Below+3 and no-Base sites defer this publication.
-- Managed CE types withhold nonpositive options from fresh proposals because
-- vanilla GetBestDistrict can otherwise select the least-negative candidate.
E.DeferredQuarterQ8=-1024*256
function E.PlacementValue(quote,site,legacyDelta,coversOwnMaterial)
    if quote.adjacency+1e-6<3 or (site.baseCount or 0)<1 then return E.DeferredQuarterQ8,'quality'end
    local penalty=math.max(0,-(legacyDelta or 0))
    if coversOwnMaterial then penalty=math.max(penalty,256*256)end
    local value=quote.valueQ8-penalty
    if value<=0 then return value,'economics'end
    local premium=math.min(4,math.max(0,quote.adjacency-2))*96*256
    if (site.specialtyCount or 0)>0 then premium=premium+16*256 end
    return math.floor(math.max(-4096*256,math.min(4096*256,value+premium))+.5),'positive'
end

function E.QuarterBids(snapshot,placement,protectedPlots,early)
    local result,prior,managed={},{},{}
    local profiles=placement.StageTwoProfiles()
    for _,profile in ipairs(profiles)do managed[profile.district.Index]=true end
    for _,entry in ipairs(early)do prior[entry.city..':'..entry.district..':'..entry.plot]=entry end
    local stats={evaluated=0,final=0,unknown=0,buyerBlocked=0,streams=0,omissions=0,
        qualityDeferred=0,economicDeferred=0,invoiceDeferred=0,managed=true}
    local player,pid=snapshot.player,snapshot.id
    local visibility=PlayersVisibility[pid]
    for _,profile in ipairs(profiles)do
        for _,city in player:GetCities():Members()do
            if not city:GetDistricts():HasDistrict(profile.district.Index)then
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
                        if geometry.upper+1e-6<3 then stats.qualityDeferred=stats.qualityDeferred+1
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
                                    quote,reason=M.Forecast(site,snapshot.Price,function(alternative)
                                        return E.PlacementValue(alternative,site,old and old.delta,covers)
                                    end)
                                end
                                if not quote then
                                    stats.unknown=stats.unknown+1
                                    if stats.unknown<=3 then print(string.format('CSC_AI_ECONOMY_QUOTE_UNAVAILABLE turn=%d player=%d city=%d plot=%d reason=%s',
                                        Game.GetCurrentGameTurn(),pid,city:GetID(),plot:GetIndex(),tostring(reason)))end
                                else
                                    local bid,why=E.PlacementValue(quote,site,old and old.delta,covers)
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
                                                baseCount=site.baseCount,specialtyCount=site.specialtyCount,
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
