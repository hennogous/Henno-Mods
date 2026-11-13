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

function E.QuarterBids(snapshot,placement,protectedPlots,early)
    local result,replace={},{}
    local prior={}
    for _,entry in ipairs(early)do
        prior[entry.city..':'..entry.district..':'..entry.plot]=entry
    end
    local stats={evaluated=0,final=0,unknown=0,buyerBlocked=0,streams=0,omissions=0,min=nil,max=nil}
    local player,pid=snapshot.player,snapshot.id
    local visibility=PlayersVisibility[pid]
    local function quoteCandidate(city,plot,profile,old)
        local index=plot:GetIndex()
        stats.evaluated=stats.evaluated+1
        local site,reason=snapshot.Site(city,plot,profile)
        local quote
        if site then
            if old and old.frontier then site.purchaseGold=old.purchaseGold end
            quote,reason=M.Forecast(site,snapshot.Price)
        end
        if quote then
            local key=city:GetID()..':'..profile.district.Index..':'..index
            -- A complete Quarter valuation replaces the early
            -- +24/+48 heuristic and Civ's building premium.
            -- Preserve finite material/no-host policy where it
            -- exceeds the ordinary below+3 quality deduction.
            local penalty=quote.adjacency<3 and math.floor((3-quote.adjacency)*64*256+.5)or 0
            if old and old.delta<0 then penalty=math.max(penalty,-old.delta)end
            local resource=GameInfo.Resources[plot:GetResourceType()]
            if site.baseCount==0 or resource and(CSC_Adjacency.HasTag(profile.base,resource.ResourceType)
                or CSC_Adjacency.HasTag(profile.specialty,resource.ResourceType))then penalty=math.max(penalty,256*256)end
            local bid=math.max(-4096*256,math.min(4096*256,quote.valueQ8-penalty))
            -- A known invoice is enough to compare sites coherently, but not
            -- enough to promote a purchase for this particular city. Economic
            -- may pick another buyer; CE acknowledges intended ownership only
            -- after it exists. Preserve the old unambiguous-buyer safeguard.
            if old and old.frontier and bid>0 then
                local eligible,exclusive=pcall(snapshot.ui.GetPlotPurchaseQuote,pid,city:GetID(),index)
                if not eligible or exclusive==nil then bid=0;stats.buyerBlocked=stats.buyerBlocked+1 end
            end
            local entry={player=pid,city=city:GetID(),district=profile.district.Index,plot=index,
                delta=0,finalQ8=bid,economy=true,adjacency=quote.adjacency,
                declineNoBase=old and old.declineNoBase,weak=bid<=0,
                frontier=old and old.frontier,purchaseGold=old and old.purchaseGold}
            result[#result+1]=entry;replace[key]=true
            stats.final=stats.final+1;stats.streams=stats.streams+#quote.streams
            stats.omissions=stats.omissions+#quote.omissions
            stats.min=math.min(stats.min or bid,bid);stats.max=math.max(stats.max or bid,bid)
        else
            stats.unknown=stats.unknown+1
            if stats.unknown<=3 then
                print(string.format('CSC_AI_ECONOMY_QUOTE_UNAVAILABLE turn=%d player=%d city=%d plot=%d reason=%s',Game.GetCurrentGameTurn(),pid,city:GetID(),index,tostring(reason)))
            end
        end
    end

    for _,profile in ipairs(placement.StageTwoProfiles())do
        for _,city in player:GetCities():Members()do
            if not city:GetDistricts():HasDistrict(profile.district.Index)then
                for _,index in ipairs(snapshot.ui.GetLegalDistrictTargets(pid,city:GetID(),profile.district.Hash))do
                    local plot=Map.GetPlotByIndex(index)
                    local owner=plot and Cities.GetPlotPurchaseCity(plot)
                    if owner and owner:GetID()==city:GetID()and plot:GetOwner()==pid
                        and plot:GetDistrictType()==-1
                        and visibility:IsRevealed(plot:GetX(),plot:GetY())
                        and Map.GetPlotDistance(city:GetX(),city:GetY(),plot:GetX(),plot:GetY())<=3
                        and plot:CanHaveDistrict(profile.district.Index,pid,city:GetID())then
                        local key=city:GetID()..':'..profile.district.Index..':'..index
                        quoteCandidate(city,plot,profile,prior[key])
                    end
                end
            end
        end
    end
    -- Native plot-analysis rows also admit unowned frontier sites; the BUILD
    -- target list omits them. Cover every revealed radius-three frontier pair,
    -- not only the old planner's favourite, or an untouched building premium
    -- could beat all fully priced owned sites. Payment remains entirely native.
    for _,profile in ipairs(placement.StageTwoProfiles())do
        for _,city in player:GetCities():Members()do
            if not city:GetDistricts():HasDistrict(profile.district.Index)then
                local center=Map.GetPlot(city:GetX(),city:GetY())
                for _,plot in ipairs(CSC_Adjacency.PlotsInBand(center,1,3))do
                    if plot:GetOwner()==-1 and plot:GetDistrictType()==-1
                        and visibility:IsRevealed(plot:GetX(),plot:GetY())
                        and plot:CanHaveDistrict(profile.district.Index,pid,city:GetID())then
                        local frontier=false
                        for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
                            frontier=frontier or near:GetOwner()==pid
                        end
                        if frontier then
                            local ok,invoice=pcall(snapshot.ui.GetRawPlotPurchaseQuote,pid,city:GetID(),plot:GetIndex())
                            if ok and (type(invoice)=='number'or type(invoice)=='integer')and invoice>0 then
                                local key=city:GetID()..':'..profile.district.Index..':'..plot:GetIndex()
                                local original=prior[key];local entry={}
                                for k,v in pairs(original or{})do entry[k]=v end
                                entry.delta=entry.delta or 0;entry.frontier=true;entry.purchaseGold=invoice
                                quoteCandidate(city,plot,profile,entry)
                            else stats.unknown=stats.unknown+1 end
                        end
                    end
                end
            end
        end
    end
    -- Whole-value replacement must cover the comparison coherently. If any
    -- owned legal quote is unavailable, retain this player's old compact
    -- policy rather than leave an unpriced native-premium candidate among
    -- fully replaced peers. Diagnostics never describe that as integration.
    if stats.unknown>0 then stats.fallback=true;stats.final=0;return early,stats end
    -- One score entry per pair. Do not sum a whole economic bid with the old
    -- adjacency preference or native future-building forecast. Unquoted frontier
    -- deductions remain finite guidance; quoted investment options use the
    -- same final bid and native acquisition machinery as owned candidates.
    for _,entry in ipairs(early)do
        if not replace[entry.city..':'..entry.district..':'..entry.plot]then result[#result+1]=entry end
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
