-- DIAGNOSTIC ONLY. Current native geometry/costs and isolated central-model
-- transaction projections -> JSON evidence. The driver supplies a private
-- module environment; the installed main policy remains unchanged. No score,
-- queue, world property or gameplay object is written. Services are excluded
-- from both sides of each prospective customer comparison.
local ui=assert(ExposedMembers.CSC_Adjacency)
local P=assert(CSC_AI_QuarterPlacement)
local E,M=assert(CSC_TRANSACTION_MODULES.CSC_AI_EconomyAdapters),assert(CSC_TRANSACTION_MODULES.CSC_AI_EconomyModel)
local hub=assert(GameInfo.Districts.DISTRICT_COMMERCIAL_HUB)
local unpack=unpack or table.unpack
local snapshots={}
local context=assert(CE_AIEvaluationContext())
local horizon=assert(tonumber(context:match('"ordinaryHorizon":(%d+)')))
local discount=assert(tonumber(context:match('"discountQ8":(%d+)')))
for _,case in ipairs(CSC_TRANSACTION_CASES)do
    local pid,id,chosen,alternative,key,quarter=unpack(case)
    local player=assert(Players[pid]);local city=assert(player:GetCities():FindID(id))
    local legal={};for _,plot in ipairs(ui.GetLegalDistrictTargets(pid,id,hub.Hash)or{})do legal[plot]=true end
    local profile;for _,p in ipairs(P.StageTwoProfiles())do if p.key==key then profile=p end end
    assert(profile,'Unknown Quarter family')
    local snapshot=snapshots[pid]
    if not snapshot then snapshot=assert(E.Snapshot(player,P,ui));snapshots[pid]=snapshot end
    local ready=ui.GetEconomyCityNumber(pid,id,'districtTurns',hub.Index)
    if not ready or ready<1 then
        local cost=ui.GetEconomyCityNumber(pid,id,'district',hub.Index)
        local production=snapshot.cities[id].production
        ready=cost and production and production>0 and math.max(1,math.ceil(cost/production))or nil
    end
    local record={turn=Game.GetCurrentGameTurn(),player=pid,city=id,name=Locale.Lookup(city:GetName()),
        district=hub.Index,districtReady=ready,horizon=horizon,discountQ8=discount,
        chosen=chosen,alternative=alternative,quarter=quarter,quarterKey=key,plots={}}
    for _,index in ipairs({chosen,alternative})do
        local plot=assert(Map.GetPlotByIndex(index));local assigned=Cities.GetPlotPurchaseCity(plot)
        local row={plot=index,owner=plot:GetOwner(),city=assigned and assigned:GetID(),district=plot:GetDistrictType(),
            resource=plot:GetResourceType(),feature=plot:GetFeatureType(),improvement=plot:GetImprovementType(),
            river=plot:IsRiver(),legal=legal[index]or false,adjacency=ui.GetDistrictAdjacency(pid,id,index,hub.Index)}
        -- Instant-ready intrinsic/net quotes isolate ordinary site accounting;
        -- selector matrices retain their actual preparation/building forecast.
        local raw=CE_AIDistrictSiteAdjustment(pid,id,hub.Index,plot:GetX(),plot:GetY(),0,horizon,discount)
        row.nativeInstantSite=raw
        record.plots[#record.plots+1]=row
    end
    local q=assert(Map.GetPlotByIndex(quarter))
    if q:GetDistrictType()==profile.district.Index and q:GetOwner()==pid then
        local seller=assert(Cities.GetPlotPurchaseCity(q))
        local site,message=snapshot.Site(seller,q,profile)
        record.site=site;record.siteError=message
        if site and ready then
            local prospect=Map.GetPlotByIndex(alternative)
            assert(Map.GetPlotDistance(q:GetX(),q:GetY(),prospect:GetX(),prospect:GetY())==1,'Nonadjacent transaction projection')
            local projected=snapshot.ProjectedCustomers(profile,id,hub.Index,alternative)
            record.projectedCustomers=projected
            local value,reason=M.CustomerBuildingForecast(site,projected,id,ready,snapshot.Price)
            record.transaction=value;record.transactionError=reason
        end
    else record.siteError='Quarter not present in this boundary'end
    print('CSC_TRANSACTION_RECORD='..encode(record))
end
print('CSC_TRANSACTION_COMPLETE',Game.GetCurrentGameTurn(),#CSC_TRANSACTION_CASES)
