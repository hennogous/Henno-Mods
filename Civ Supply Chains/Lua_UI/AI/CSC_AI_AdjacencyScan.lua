-- Read-only Quarter site planning, shared with the placement experiments.
-- After CSC_AdjacencyCore loads the rules, the main publisher calls
-- QuarterSiteForecasts for live bids. The older AdjacencyScan entry point
-- returns a diagnostic census and caches only city-to-plot geometry.
assert(CSC_Adjacency and CSC_Adjacency.ByDistrict,'Loaded bundled adjacency engine required')
local function object(t)return setmetatable(t or {},{__json_object=true})end
local function json(v)
 local t=type(v)
 if t=='nil'then return 'null'end
 if t=='boolean'or t=='number'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 assert(t=='table','Non-scalar observation: '..t)
 local n,array=0,not(getmetatable(v)and getmetatable(v).__json_object)
 for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 local a={}
 if array then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 local keys={};for k in pairs(v)do keys[#keys+1]=k end
 table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
 for _,k in ipairs(keys)do a[#a+1]=json(tostring(k))..':'..json(v[k])end
 return '{'..table.concat(a,',')..'}'
end
local function call(o,k,...)
 if not o or type(o[k])~='function'then return {unavailable=k}end
 local ok,v=pcall(o[k],o,...);if ok then return v end
 return {error=tostring(v)}
end
local function scalar(v)
 if type(v)~='table'then return v end
 local r=object();for k,x in pairs(v)do if type(x)=='string'or type(x)=='number'or type(x)=='boolean'then r[tostring(k)]=x end end;return r
end

local A=CSC_Adjacency
local geometry={}
-- City-to-plot geometry is immutable within a game. Ownership, visibility,
-- materials and native eligibility are read afresh on each publication.
local frontierGeometry = {}
local quarters={'DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER'}
local function totals()return {production=0,gold=0}end
local function yieldKey(y)if y=='YIELD_PRODUCTION'then return 'production'elseif y=='YIELD_GOLD'then return 'gold'end end
-- Count Production and Gold with the same rule engine as gameplay. Keep the
-- active and planned totals separate because a new Bakers site can later gain
-- one Mill's adjacency. River sites plan for Water and inland sites for Wind.
local function score(district,plot,city,pid,omitDetails,futureDistrict)
 local now,planned,percent,nowPercent=totals(),totals(),totals(),totals();local details={};local mill=nil
 if district=='DISTRICT_CSC_BAKERS_QUARTER'then
  mill=plot:IsRiver()and'BUILDING_CSC_BAKERS_WATER_MILL'or'BUILDING_CSC_BAKERS_WIND_MILL'
 end
 for _,r in ipairs(A.ByDistrict[district]or{})do
  local key=yieldKey(r.YieldType)
  if key and(r.ProvideType=='SelfBonus'or r.ProvideType=='SelfMultiplier')then
   local active=A.Eligible(r,city,pid)
   local millRule=r.ModifierOwner=='BuildingModifiers'and(r.WhoIsTheOwner=='BUILDING_CSC_BAKERS_WATER_MILL'or r.WhoIsTheOwner=='BUILDING_CSC_BAKERS_WIND_MILL')
   local projected=millRule and r.WhoIsTheOwner==mill or not millRule and active
   if active or projected then
    local count=A.Count(r,plot,city,pid);local amount=A.Amount(r,count)
    local plannedAmount = amount
    -- Credit one evidenced future host through the loaded adjacency rule.
    -- Its tile is currently empty and contributes only to projected yield.
    if futureDistrict and projected and
     ((r.AdjacencyType=='FROM_RINGS_TYPETAG_DISTRICT' and A.HasTag(r.CustomAdjacentObject,futureDistrict))
     or (r.AdjacencyType=='FROM_RINGS_CAO_DISTRICT' and r.CustomAdjacentObject==futureDistrict)) then
     local first,last=A.Bounds(r)
     if first<=1 and last>=1 then plannedAmount=A.Amount(r,count+1) end
    end
    if r.ProvideType=='SelfBonus'then
     if active then now[key]=now[key]+amount end
     if projected then planned[key]=planned[key]+plannedAmount end
    else if projected then percent[key]=percent[key]+plannedAmount end;if active then nowPercent[key]=nowPercent[key]+amount end end
    if amount~=0 and not omitDetails then details[#details+1]={rule=r.ID,yield=r.YieldType,provider=r.ProvideType,count=count,amount=amount,activeNow=not not active,inPlan=not not projected,requiresBuilding=millRule and r.WhoIsTheOwner or nil}end
   end
  end
 end
 -- SelfMultiplier rules contribute percentage points on top of the summed
 -- adjacency. Keep a separate multiplier for each yield and time horizon.
 for key,value in pairs(planned)do planned[key]=value*(1+percent[key]/100);now[key]=now[key]*(1+nowPercent[key]/100)end
 return {production=planned.production,gold=planned.gold,total=planned.production+planned.gold,current=now,details=details,requiresBuilding=mill}
end


local preferredAdjacency = 4
-- The threshold above counts yield per turn. The bands below are policy
-- deltas in Q8 (256 per native utility point) at the early district score.
-- They leave Civ's later forecast contributions and final comparison in play.
local preferredSiteBidQ8 = 48 * 256
local viableSiteBidQ8 = 24 * 256
local noBasePenaltyQ8 = 256 * 256
local noCustomerPenaltyQ8 = 128 * 256
local customerSiteBidQ8 = 40 * 256
-- An unbuilt Quarter may never be chosen. Give its concrete customer site
-- a smaller starting preference than a host that can serve a working Quarter.
local futureCustomerSiteBidQ8 = 16 * 256
local sitingDistricts = {}

local function getSitingDistricts(profile)
    if sitingDistricts[profile] then return sitingDistricts[profile] end
    local byIndex, buildable = {}, {}
    local sales = 'CLASS_CSC_' .. profile.key .. '_SALES'
    local providers = 'CLASS_CSC_' .. profile.key .. '_GOODS_PROVIDER'
    -- Use loaded tags so compatibility districts and later-stage sales
    -- enter Quarter siting without changing the Stage 2 Service contract.
    for definition in GameInfo.Districts() do
        local kind = definition.DistrictType
        if profile.customers[definition.Index] or A.HasTag(sales, kind) or A.HasTag(providers, kind) then
            byIndex[definition.Index] = true
            if kind ~= 'DISTRICT_CITY_CENTER' then buildable[#buildable + 1] = definition end
        end
    end
    table.sort(buildable, function(a, b) return a.Index < b.Index end)
    local result = {byIndex=byIndex, buildable=buildable}
    sitingDistricts[profile] = result
    return result
end

local function betterQuarterSite(candidate, best)
    if not best then return true end
    if candidate.adjacency ~= best.adjacency then return candidate.adjacency > best.adjacency end
    if candidate.pending ~= best.pending then return candidate.pending < best.pending end
    if candidate.workingBase ~= best.workingBase then return candidate.workingBase end
    if candidate.base ~= best.base then return candidate.base > best.base end
    if candidate.specialty ~= best.specialty then return candidate.specialty > best.specialty end
    return candidate.plot < best.plot
end

-- Quarter siting values loaded sales and goods-provider links across stages.
-- The separate Stage 2 customer bid still needs a current native target.
function CSC_AI_QuarterSiteForecasts(player, profile, chains, readSuppliers, protectedPlots, ui)
    local bids, potential, legalCustomers, placedHosts = {}, {}, {}, {}
    local nominated = {}
    local counts = {legal=0, noBase=0, coversMaterial=0, noHost=0, bothPending=0, deferCities=0,
        offered=0, strong=0, frontierObserved=0, frontierBids=0, frontierUncertain=0}
    local district = profile.district
    local readLegalTargets = ui and ui.GetLegalDistrictTargets
    if not A.ByDistrict[district.DistrictType] or type(readLegalTargets) ~= 'function' then return bids, counts end
    local siting = getSitingDistricts(profile)
    if next(siting.byIndex) == nil then return bids, counts end
    local pid = player:GetID()
    local visibility = PlayersVisibility[pid]
    local allBaseTypesVisible
    local hosts = {}
    -- Use the UI's current native targets for customer bids. Future host
    -- geometry below is a planning hint and can never create a customer bid.
    for host in pairs(profile.customers) do
        local definition = GameInfo.Districts[host]
        if definition and definition.DistrictType ~= 'DISTRICT_CITY_CENTER' then
            hosts[#hosts + 1] = definition
        end
    end
    table.sort(hosts, function(a, b) return a.Index < b.Index end)
    for _, definition in ipairs(hosts) do
        local host = definition.Index
        for _, city in player:GetCities():Members() do
            if not city:GetDistricts():HasDistrict(host) then
                local cityID = city:GetID()
                for _, index in ipairs(readLegalTargets(pid, cityID, definition.Hash)) do
                    local plot = Map.GetPlotByIndex(index)
                    local owner = plot and Cities.GetPlotPurchaseCity(plot)
                    if owner and owner:GetID() == cityID and plot:GetOwner() == pid
                        and not protectedPlots[index] and plot:GetResourceType() == -1 then
                        local choices = legalCustomers[index] or {}
                        choices[#choices + 1] = {player=pid, city=cityID, district=host, plot=index}
                        legalCustomers[index] = choices
                    end
                end
            end
        end
    end

    local function futureHost(plot)
        -- One result per neighbor for this player/profile call. Ownership,
        -- legal targets and protections are read again next publication.
        local index = plot:GetIndex()
        if potential[index] ~= nil then return potential[index] end
        local choices = legalCustomers[index]
        local found = choices and {rank=1, district=GameInfo.Districts[choices[1].district].DistrictType} or false
        if not found and plot:GetDistrictType() == -1
            and not protectedPlots[index] and plot:GetResourceType() == -1 then
            local owner = Cities.GetPlotPurchaseCity(plot)
            if owner and owner:GetOwner() == pid then
                for _, host in ipairs(siting.buildable) do
                    -- Growth and research can make this footprint buildable
                    -- later. Immediate Harbor bids still use native targets.
                    if not owner:GetDistricts():HasDistrict(host.Index)
                        and plot:CanHaveDistrict(host.Index, pid, owner:GetID()) then
                        found = {rank=0, district=host.DistrictType}
                        break
                    end
                end
            end
        end
        potential[index] = found
        return found
    end

    -- 2 is a working district, 1 is already placed or buildable now, and
    -- 0 is feasible geometry without a native build target yet. Nil is no
    -- evidenced path. Keep placed hosts distinct for actual customer bids.
    local function hostReadiness(neighbors, includeFuture, hostTypes)
        local best, projected, projectedPlot
        for _, neighbor in ipairs(neighbors) do
            if neighbor:GetOwner() == pid then
                local rank
                if hostTypes[neighbor:GetDistrictType()] then
                    local index = neighbor:GetIndex()
                    if not placedHosts[index] then
                        placedHosts[index] = ui.HasWorkingDistrictAt
                            and ui.HasWorkingDistrictAt(neighbor:GetX(), neighbor:GetY()) and 2 or 1
                    end
                    rank = placedHosts[index]
                elseif includeFuture and visibility:IsRevealed(neighbor:GetX(), neighbor:GetY()) then
                    local future = futureHost(neighbor)
                    if future then
                        rank = future.rank
                        if not projected or rank > projected.rank then
                            projected, projectedPlot = future, neighbor:GetIndex()
                        end
                    end
                end
                if rank and (not best or rank > best) then best = rank end
            end
        end
        -- Existing hosts contribute through the real adjacency rules. One
        -- additional empty footprint can enter the forecast once. This avoids
        -- assuming several future districts can all compete for the same land.
        return best, projected and projected.district, projectedPlot
    end

    local function nominateCustomer(candidate, delta)
        local key = candidate.city .. ':' .. candidate.district .. ':' .. candidate.plot
        local bid = nominated[key]
        if bid then
            -- An existing Quarter can strengthen an earlier prospective
            -- offer. The CE packet still carries only one entry for the pair.
            bid.delta = math.max(bid.delta, delta)
            return
        end
        bid = {player=pid, city=candidate.city, district=candidate.district,
            plot=candidate.plot, delta=delta, customer=true}
        nominated[key] = bid
        bids[#bids + 1] = bid
    end

    local function frontierDeductions(city)
        local center = Map.GetPlot(city:GetX(), city:GetY())
        local key = pid .. ':' .. city:GetID() .. ':' .. center:GetIndex()
        local indices = frontierGeometry[key]
        if not indices then
            indices = {}
            for _, plot in ipairs(A.PlotsInBand(center, 1, 3)) do indices[#indices + 1] = plot:GetIndex() end
            frontierGeometry[key] = indices
        end
        for _, index in ipairs(indices) do
            local plot = Map.GetPlotByIndex(index)
            if plot:GetOwner() == -1 and plot:GetDistrictType() == -1
                and visibility:IsRevealed(plot:GetX(), plot:GetY())
                and plot:CanHaveDistrict(district.Index, pid, city:GetID()) then
                local frontier, uncertain, possibleBase = false, false, false
                for _, neighbor in ipairs(Map.GetAdjacentPlots(plot:GetX(), plot:GetY())) do
                    local owner = neighbor:GetOwner()
                    frontier = frontier or owner == pid
                    if not visibility:IsRevealed(neighbor:GetX(), neighbor:GetY()) then
                        uncertain = true
                    elseif owner == pid or owner == -1 then
                        local resource = GameInfo.Resources[neighbor:GetResourceType()]
                        if resource and A.ResourceVisible(pid, resource.Index)
                            and A.HasTag(profile.base, resource.ResourceType) then possibleBase = true end
                    end
                end
                if frontier then
                    counts.frontierObserved = counts.frontierObserved + 1
                    local resource = GameInfo.Resources[plot:GetResourceType()]
                    local coversMaterial = resource and A.ResourceVisible(pid, resource.Index)
                        and (A.HasTag(profile.base, resource.ResourceType) or A.HasTag(profile.specialty, resource.ResourceType))
                    -- A hidden mapped Base type prevents a negative conclusion
                    -- from the visible map. Check unlock visibility globally,
                    -- rather than allowing policy to infer hidden deposits.
                    if allBaseTypesVisible == nil then
                        allBaseTypesVisible = true
                        for definition in GameInfo.Resources() do
                            if A.HasTag(profile.base, definition.ResourceType) and not A.ResourceVisible(pid, definition.Index) then
                                allBaseTypesVisible = false
                                break
                            end
                        end
                    end
                    if coversMaterial or not uncertain and allBaseTypesVisible and not possibleBase then
                        -- BUILD-operation targets omit unowned plots. Publish
                        -- a conservative radius-three frontier candidate here.
                        -- CE still requires the exact proposing city and a live
                        -- native eligible row before applying this Q8 deduction.
                        bids[#bids + 1] = {player=pid, city=city:GetID(), district=district.Index,
                            plot=index, delta=-noBasePenaltyQ8, weak=true}
                        counts.frontierBids = counts.frontierBids + 1
                    elseif uncertain or not allBaseTypesVisible then
                        counts.frontierUncertain = counts.frontierUncertain + 1
                    end
                end
            end
        end
    end

    for _, city in player:GetCities():Members() do
        -- Price every eligible weak site. Permanent site potential comes
        -- first. Readiness distinguishes sites with equal projected yield.
        if not city:GetDistricts():HasDistrict(district.Index) then
            local cityID = city:GetID()
            local best
            local legal = 0
            for _, index in ipairs(readLegalTargets(pid, cityID, district.Hash)) do
                local plot = Map.GetPlotByIndex(index)
                local ownerCity = plot and Cities.GetPlotPurchaseCity(plot)
                if plot and plot:GetOwner() == pid and ownerCity and ownerCity:GetID() == cityID
                    and plot:GetDistrictType() == -1 and not protectedPlots[index]
                    and visibility:IsRevealed(plot:GetX(), plot:GetY())
                    and Map.GetPlotDistance(city:GetX(), city:GetY(), plot:GetX(), plot:GetY()) <= 3
                    and plot:CanHaveDistrict(district.Index, pid, cityID) then
                    legal = legal + 1
                    local supply = readSuppliers(player, plot, profile)
                    local resource = GameInfo.Resources[plot:GetResourceType()]
                    local coversMaterial = resource and A.ResourceVisible(pid, resource.Index)
                        and (A.HasTag(profile.base, resource.ResourceType) or A.HasTag(profile.specialty, resource.ResourceType))
                    local candidate = {player=pid, city=cityID, district=district.Index, plot=index}
                    if coversMaterial then
                        counts.coversMaterial = counts.coversMaterial + 1
                        candidate.delta, candidate.weak = -noBasePenaltyQ8, true
                    elseif #supply.base == 0 then
                        counts.noBase = counts.noBase + 1
                        candidate.delta, candidate.weak = -noBasePenaltyQ8, true
                    else
                        local host, futureDistrict, futurePlot =
                            hostReadiness(Map.GetAdjacentPlots(plot:GetX(), plot:GetY()), true, siting.byIndex)
                        if not host then
                            counts.noHost = counts.noHost + 1
                            candidate.delta, candidate.weak = -noCustomerPenaltyQ8, true
                        else
                            local ready, working = false, false
                            for _, material in ipairs(supply.base) do
                                ready = ready or material.ready
                                working = working or material.working
                            end
                            -- Record the unfinished links even when both can
                            -- be prepared later. They do not erase the site.
                            candidate.pending = (ready and 0 or 1) + (host == 2 and 0 or 1)
                            if candidate.pending == 2 then counts.bothPending = counts.bothPending + 1 end
                            candidate.workingBase = working == true
                            candidate.base, candidate.specialty = #supply.base, #supply.specialty
                            candidate.adjacency = score(district.DistrictType, plot, city, pid, true, futureDistrict).total
                            -- Only a ready Base and a current native host
                            -- target can justify acting ahead of the Quarter.
                            if ready and futurePlot then candidate.futureHost = legalCustomers[futurePlot] end
                            if betterQuarterSite(candidate, best) then best = candidate end
                        end
                    end
                    if candidate.weak then bids[#bids + 1] = candidate end
                end
            end
            counts.legal = counts.legal + legal
            if best then
                local strong = best.adjacency >= preferredAdjacency
                best.delta = strong and preferredSiteBidQ8 or viableSiteBidQ8
                bids[#bids + 1] = best
                counts.offered = counts.offered + 1
                if strong then
                    counts.strong = counts.strong + 1
                    if best.futureHost then
                        local host = best.futureHost[1]
                        local hostDistrict = GameInfo.Districts[host.district]
                        -- Both sites passed the current queue checks. When
                        -- they share a city, avoid bidding away the Quarter's
                        -- last slot if a later profile requires population.
                        if host.city ~= cityID or not district.RequiresPopulation or not hostDistrict.RequiresPopulation then
                            nominateCustomer(host, futureCustomerSiteBidQ8)
                        end
                    end
                end
            elseif legal > 0 then
                counts.deferCities = counts.deferCities + 1
            end
            -- A potential supplier on purchasable land keeps this first
            -- frontier policy neutral. Its acquisition belongs to problem 1.5.
            -- Positive Quarter and customer offers retain their owned targets.
            frontierDeductions(city)
        end
    end

    -- Several Quarters can share one customer district. Credit each legal
    -- district-site pair once and leave the final Harbor choice to Civ.
    for _, chain in ipairs(chains) do
        if chain.profile == profile and chain.ready and #chain.supply.base > 0 then
            local neighbors = Map.GetAdjacentPlots(chain.plot:GetX(), chain.plot:GetY())
            if not hostReadiness(neighbors, false, profile.customers) then
                for _, neighbor in ipairs(neighbors) do
                    for _, candidate in ipairs(legalCustomers[neighbor:GetIndex()] or {}) do
                        nominateCustomer(candidate, customerSiteBidQ8)
                    end
                end
            end
        end
    end
    return bids, counts
end


-- Diagnostic census for historical parity and tooling. It reports observations
-- to Lua and the log. Live CSC placement starts from the UI's native targets
-- above instead of consuming this radius-three census.
function CSC_AI_AdjacencyScan(originalAI)
 local t0=os.clock();local out={turn=Game.GetCurrentGameTurn(),speed=assert(GameInfo.GameSpeeds[GameConfiguration.GetGameSpeedType()]).GameSpeedType,width=0,height=0,cities={},candidates={},quarters={},players={},currentHumans={},originalAI=originalAI,geometryBuilt=0,sitesEvaluated=0,rules={}}
 out.width,out.height=Map.GetGridSize()
 local maxIndex,count=-1,0;for d in GameInfo.Districts()do maxIndex=math.max(maxIndex,d.Index);count=count+1 end
 assert(maxIndex+1==count,'Sparse native district catalog');out.districtCount=count
 for _,name in ipairs(quarters)do local d=assert(GameInfo.Districts[name]);assert(A.ByDistrict[name]and#A.ByDistrict[name]>0,'Missing Quarter adjacency rules');out.quarters[#out.quarters+1]={type=name,index=d.Index};for _,r in ipairs(A.ByDistrict[name])do out.rules[#out.rules+1]=r end end
 -- Quarter-native rows need an explicit adapter rather than silent omission.
 if GameInfo.District_Adjacencies then for row in GameInfo.District_Adjacencies()do for _,name in ipairs(quarters)do assert(row.DistrictType~=name,'Unexpected native Quarter adjacency row: needs parity adapter')end end end
 for pid=0,63 do local p=Players[pid];if p then out.players[#out.players+1]={player=pid,human=p:IsHuman(),alive=p:IsAlive(),major=p:IsMajor()};if p:IsHuman()then out.currentHumans[#out.currentHumans+1]=pid end end end
 for _,pid in ipairs(originalAI)do
  local player=assert(Players[pid]);assert(not player:IsHuman(),'Original AI currently human: refuse policy')
  if player:IsAlive()and player:IsMajor()then
   for _,city in player:GetCities():Members()do
    local center=Map.GetPlot(city:GetX(),city:GetY());local key=pid..':'..city:GetID()..':'..center:GetIndex()
    if not geometry[key]then geometry[key]={};for _,plot in ipairs(A.PlotsInBand(center,1,3))do geometry[key][#geometry[key]+1]=plot:GetIndex()end;out.geometryBuilt=out.geometryBuilt+1 end
    local c={player=pid,city=city:GetID(),name=city:GetName(),x=city:GetX(),y=city:GetY(),districts={},queue=call(city:GetBuildQueue(),'CurrentlyBuilding')}
    local existing={};local ds=city:GetDistricts()
    for i=0,ds:GetNumDistricts()-1 do local d=ds:GetDistrictByIndex(i);if d then local row=assert(GameInfo.Districts[d:GetType()]);existing[row.DistrictType]=true;c.districts[#c.districts+1]={type=row.DistrictType,plot=d:GetY()*out.width+d:GetX(),complete=d:IsComplete(),pillaged=d:IsPillaged()}end end
    out.cities[#out.cities+1]=c
    for _,index in ipairs(geometry[key])do
     local plot=Map.GetPlotByIndex(index);local ownerCity=Cities.GetPlotPurchaseCity(plot)
     local visible=PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY())
     if plot:GetOwner()==pid and visible and ownerCity and ownerCity:GetOwner()==pid and ownerCity:GetID()==city:GetID()
       and plot:GetDistrictType()==-1 and not plot:IsWater()and not plot:IsImpassable()then
      for _,name in ipairs(quarters)do if not existing[name]then
       local d=GameInfo.Districts[name];local legal=plot:CanHaveDistrict(d.Index,pid,city:GetID())
       if legal then
        local value=score(name,plot,city,pid);out.sitesEvaluated=out.sitesEvaluated+1
        local resource=plot:GetResourceType();local resourceDef=resource>=0 and GameInfo.Resources[resource]or nil
        -- Do not promote a site whose construction would harvest a mapped supply
        -- resource. Strategic/luxury legality remains the engine's responsibility.
        local materialOnSite=false
        if resourceDef then for _,tag in ipairs({'CLASS_CSC_BAKERS_BASE','CLASS_CSC_BAKERS_SPEC','CLASS_CSC_TAILORS_BASE','CLASS_CSC_TAILORS_SPEC'})do if A.HasTag(tag,resourceDef.ResourceType)then materialOnSite=true end end end
        out.candidates[#out.candidates+1]={player=pid,city=city:GetID(),quarter=name,district=d.Index,plot=index,x=plot:GetX(),y=plot:GetY(),production=value.production,gold=value.gold,total=value.total,details=value.details,current=value.current,requiresBuilding=value.requiresBuilding,legal=true,materialOnSite=materialOnSite,resource=resource,improvement=plot:GetImprovementType(),feature=plot:GetFeatureType(),riverEdges=plot:GetRiverCrossingCount()}
       end
      end end
     end
    end
   end
  end
 end
 out.elapsedSeconds=os.clock()-t0
 print('CSC_AI_ADJACENCY_SCAN='..json(out))
 return out -- Packaged CE consumer shares this exact scanner; console callers may ignore the return.
end
print('CSC_AI_ADJACENCY_SCANNER_READY')
