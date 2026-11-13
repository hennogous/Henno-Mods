-- Diagnostic-only, read-only lifecycle observer. Installed by the shared test
-- controller after loading the main CSC policy, never as a second AI policy.
-- Wrap Publish transparently to observe accepted packets and drain CE's bounded
-- journal before the next commit resets it. No scores, properties, queues or
-- RNG are changed. Native selection, foundation and completion remain separate.
assert(not CSC_QUARTER_PLACEMENT_WATCH, 'Duplicate placement observer')
local B=assert(CSC_AI_DistrictBridge)
local A=assert(CSC_Adjacency)
local P=assert(CSC_AI_QuarterPlacement)
local watched,offers,lastWrite,seen,managedDefaults={},{},{},{},{}
local publicationVersion
for _,profile in ipairs(P.StageTwoProfiles())do watched[profile.district.Index]=profile end
local function key(player,city,district,plot)
 return table.concat({player,city,district,plot},':')
end
local function emit(kind,row)
 local fields={}
 for name,value in pairs(row)do
  if value~=nil then fields[#fields+1]=name..'='..tostring(value):gsub('[\t\r\n]',' ')end
 end
 table.sort(fields)
 print('CSC_QUARTER_WATCH_'..kind..'\t'..table.concat(fields,'\t'))
end
local function number(record,name)return tonumber(record:match('"'..name..'":(-?%d+)'))end
local function drain()
 local status=assert(CE_AIDistrictScoresStatus())
 local generation=assert(number(status,'generation'))
 local total=assert(number(status,'trace_count'))
 local writes,best={},{}
 for offset=0,total-1,64 do
  local page=assert(CE_AIDistrictScoresTraceRead(offset,64,generation))
  assert(not page:find('"stale":true',1,true),'Publication changed during journal read')
  local ordinal=0
  for record in page:gmatch('{[^{}]+}')do
   local kind=record:match('"k":"([^"]+)"')
   if kind then ordinal=ordinal+1 end
   if kind=='final'or kind=='best'or kind=='location'or kind=='request'or kind=='pv'then
    local row={}
    for _,name in ipairs({'version','generation','player','city','district','plot','base','result','reason','eligible'})do
     row[name]=assert(number(record,name))
    end
    if watched[row.district]then
     row.nativeOrdinal=offset+ordinal
     row.reservationId=number(record,'reservationId');row.phase=number(record,'phase')
     row.existingDistrict=number(record,'existingDistrict')
     row.observedTurn=Game.GetCurrentGameTurn()
     local id=key(row.player,row.city,row.district,row.plot)
     if kind=='final'then
      -- Last native write for this identity, not an assertion that this write
      -- caused a later choice. Retained plans may outlive a packet.
      lastWrite[id]=row;writes[id]=row
     else
      local bid=offers[id];local write=lastWrite[id]
      row.bidVersion=bid and bid.version;row.bidQ8=bid and bid.finalQ8
      row.bidAdjacency=bid and bid.adjacency
      row.bidEconomicQ8=bid and bid.economicQ8;row.bidPreferenceQ8=bid and bid.preferenceQ8
      if not bid and managedDefaults[row.player..':'..row.district]then
       row.bidVersion=publicationVersion;row.bidQ8=managedDefaults[row.player..':'..row.district];row.fallback=true
      end
      row.lastWriteVersion=write and write.version;row.lastWriteQ8=write and write.result
      row.lastWriteOrdinal=write and write.nativeOrdinal
      if kind=='pv'and row.plot==-1 then row.aggregate=true end
      if kind=='best'then best[#best+1]=row
      else emit(kind=='location'and'LOCATION'or kind=='request'and'REQUEST'or'VALUE',row)end
     end
    end
   end
  end
 end
 for _,row in pairs(writes)do emit('WRITE',row)end
 for _,row in ipairs(best)do
  emit('BEST',row)
 end
 emit('DRAIN',{turn=Game.GetCurrentGameTurn(),generation=generation,total=total})
end
local function snapshot(kind,player,cityID,districtID,x,y,districtType,complete)
 local profile=watched[districtType];if not profile then return end
 local city=CityManager.GetCity(player,cityID);local plot=Map.GetPlot(x,y)
 assert(city and plot,'Missing lifecycle city/plot')
 -- Use the live planner's completed-customer filter. An empty district
 -- footprint earns no customer adjacency; Mill geometry is explicitly future.
 local completed={}
 for _,c in Players[player]:GetCities():Members()do
  local districts=c:GetDistricts()
  for i=0,districts:GetNumDistricts()-1 do
   local d=districts:GetDistrictByIndex(i)
   if d and d:IsComplete()then completed[Map.GetPlot(d:GetX(),d:GetY()):GetIndex()]=true end
  end
 end
 local value=CSC_AI_QuarterAdjacencyValue(profile.district.DistrictType,plot,city,player,false,completed)
 local supply=P.ReadSuppliers(Players[player],plot,profile)
 local baseWorking,specWorking=0,0
 for _,v in ipairs(supply.base)do if v.working then baseWorking=baseWorking+1 end end
 for _,v in ipairs(supply.specialty)do if v.working then specWorking=specWorking+1 end end
 local index=plot:GetIndex();local bid=offers[key(player,cityID,districtType,index)]
 emit('SITE',{event=kind,turn=Game.GetCurrentGameTurn(),player=player,city=cityID,
  district=districtType,districtID=districtID,plot=index,complete=complete,
  base=#supply.base,spec=#supply.specialty,baseWorking=baseWorking,specWorking=specWorking,
  river=plot:IsRiver(),hills=plot:IsHills(),
  eligibleProduction=value.current.production,eligibleGold=value.current.gold,
  millForecastProduction=value.production,millForecastGold=value.gold,millForecastTotal=value.total,
  mill=value.requiresBuilding,bidVersion=bid and bid.version,bidQ8=bid and bid.finalQ8,
  bidAdjacency=bid and bid.adjacency})
 -- Eligible rule totals are geometry, not realised output from an incomplete
 -- or pillaged Quarter. Record each nonzero source to explain +1/+2 sites.
 for _,rule in ipairs(value.details)do
  emit('RULE',{event=kind,turn=Game.GetCurrentGameTurn(),player=player,city=cityID,plot=index,
   rule=rule.rule,yield=rule.yield,count=rule.count,amount=rule.amount,
   activeNow=rule.activeNow,inPlan=rule.inPlan,requiresBuilding=rule.requiresBuilding})
 end
 for _,near in ipairs(Map.GetAdjacentPlots(x,y))do
  local resource=GameInfo.Resources[near:GetResourceType()]
  local improvement=GameInfo.Improvements[near:GetImprovementType()]
  emit('NEIGHBOR',{event=kind,turn=Game.GetCurrentGameTurn(),plot=index,neighbor=near:GetIndex(),
   owner=near:GetOwner(),resource=resource and resource.ResourceType or '-',
   improvement=improvement and improvement.ImprovementType or '-',
   pillaged=near:IsImprovementPillaged(),district=near:GetDistrictType()})
 end
end
local function inspect(kind,player,districtID,cityID,x,y,districtType)
 if not watched[districtType]then return end
 local city=CityManager.GetCity(player,cityID)
 local district=Players[player]and Players[player]:GetDistricts():FindID(districtID)
 if not city or not district then
  -- Ownership/city bookkeeping may invalidate an event's old identity before
  -- Gameplay receives it. Do not invent a foundation or abort the policy.
  -- Keep the raw clock/identity and let the next live census discover the
  -- surviving object, explicitly as first-observed/ownership-change.
  emit('DEFERRED',{event=kind,turn=Game.GetCurrentGameTurn(),player=player,city=cityID,
   district=districtType,districtID=districtID,x=x,y=y,reason=not city and'city-unavailable'or'district-unavailable'})
  return
 end
 local index=Map.GetPlot(x,y):GetIndex();local previous=seen[index]
 local complete=district:IsComplete()
 if previous and(previous.player~=player or previous.city~=cityID)then
  snapshot('ownership-change',player,cityID,districtID,x,y,districtType,complete)
 elseif not previous or previous.districtID~=districtID then
  snapshot(kind=='added'and'foundation'or'first-observed',player,cityID,districtID,x,y,districtType,complete)
  -- Purchases/instant construction can first appear already complete. Keep
  -- both lifecycle clocks; a later progress callback must not count it twice.
  if kind=='added'and complete then
   snapshot('completion',player,cityID,districtID,x,y,districtType,complete)
  end
 elseif not previous.complete and complete then
  snapshot('completion',player,cityID,districtID,x,y,districtType,complete)
 end
 seen[index]={player=player,city=cityID,districtID=districtID,complete=complete}
end
local function safe(callback,...)
 local ok,error=pcall(callback,...)
 if not ok then emit('FAULT',{turn=Game.GetCurrentGameTurn(),error=error})end
end
local function scan(kind)
 -- Seed city-states too: a later captured Quarter must not look newly founded
 -- merely because its original owner was outside the Lua/CE scoring cohort.
 for _,player in ipairs(PlayerManager.GetAlive())do
  for _,city in player:GetCities():Members()do
   local districts=city:GetDistricts()
   for i=0,districts:GetNumDistricts()-1 do
    local d=districts:GetDistrictByIndex(i)
    if d and watched[d:GetType()]then
     if kind=='seed'then
      local index=Map.GetPlot(d:GetX(),d:GetY()):GetIndex()
      seen[index]={player=player:GetID(),city=city:GetID(),districtID=d:GetID(),complete=d:IsComplete()}
      snapshot('loaded',player:GetID(),city:GetID(),d:GetID(),d:GetX(),d:GetY(),d:GetType(),d:IsComplete())
     else inspect('poll',player:GetID(),d:GetID(),city:GetID(),d:GetX(),d:GetY(),d:GetType())end
    end
   end
  end
 end
end
local publish=B.Publish
B.Publish=function(version,width,height,count,players,entries,...)
 safe(drain)
 local accepted,message=publish(version,width,height,count,players,entries,...)
 if accepted then
  offers={}
  publicationVersion=version;managedDefaults={}
  for _,scope in ipairs(select(14,...)or{})do
   managedDefaults[scope.player..':'..scope.district]=scope.fallbackQ8
  end
  for _,entry in ipairs(entries)do
   if watched[entry.district]then
    offers[key(entry.player,entry.city,entry.district,entry.plot)]={version=version,
     finalQ8=entry.finalQ8,adjacency=entry.adjacency,economicQ8=entry.economicQ8,preferenceQ8=entry.preferenceQ8}
   end
  end
 end
 return accepted,message
end
safe(scan,'seed')
Events.DistrictAddedToMap.Add(function(...)safe(inspect,'added',...)end)
Events.DistrictBuildProgressChanged.Add(function(player,district,city,x,y,kind)
 safe(inspect,'progress',player,district,city,x,y,kind)
end)
-- Poll only existing Quarters once per turn as an explicit fallback. A missed
-- event is labelled first-observed, never silently called a foundation.
GameEvents.OnGameTurnStarted.Add(function()safe(scan,'poll')end)
CSC_QUARTER_PLACEMENT_WATCH={Drain=function()safe(drain)end}
print('CSC_QUARTER_WATCH_INSTALLED',Game.GetCurrentGameTurn())
