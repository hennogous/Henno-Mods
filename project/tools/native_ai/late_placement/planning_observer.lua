-- DIAGNOSTIC ONLY. Live facts -> observational history, never a second policy.
-- Install after CSC's policy and quarter_placement_watch. We observe the exact
-- Geometry calls made by QuarterBids (no second forecast/site enumeration), then
-- distinguish proposed opportunities from accepted Publish packets, CE native
-- best comparisons, physical foundations, completion and realised neighbours.
-- No orders, scores, properties, RNG or CE journal reads are issued here.
assert(not CSC_AI_PLANNING_WATCH, 'Duplicate planning observer')
local A=assert(CSC_Adjacency)
local P=assert(CSC_AI_QuarterPlacement)
local E=assert(CSC_AI_EconomyAdapters)
local B=assert(CSC_AI_DistrictBridge)
local W={};CSC_AI_PLANNING_WATCH=W
local unpack=unpack or table.unpack
local function pack(...)return {n=select('#',...),...}end
local profiles,byType={},{}
for _,p in ipairs(P.StageTwoProfiles())do profiles[p.key]=p;byType[p.district.Index]=p end
local districts,materials,relations,offers,native,opportunities,pending={},{},{},{},{},{},{}
local adjacencyPending={}
local sequence,records,faults,lastPoll=0,0,0,nil
-- A cap is a diagnostic failure, never silent successful coverage. It bounds
-- pathological log volume without changing policy or game progress. Default
-- 1m rows covers 250 turns of mature empires; Finish reports any lost records.
local limit=CSC_PLANNING_MAX_RECORDS or 1000000
local dropped=0
local function turn()return Game.GetCurrentGameTurn()end
local function emit(kind,row)
 if records>=limit then
  dropped=dropped+1
  if dropped==1 then print('CSC_PLANNING_LIMIT\tturn='..turn()..'\tlimit='..limit..'\tincomplete=true')end
  return
 end
 records=records+1;sequence=sequence+1
 row.turn=row.turn or turn();row.sequence=sequence
 local fields={}
 for k,v in pairs(row)do if v~=nil then fields[#fields+1]=k..'='..tostring(v):gsub('[\t\r\n]',' ')end end
 table.sort(fields);print('CSC_PLANNING_'..kind..'\t'..table.concat(fields,'\t'))
end
local function safe(fn,...)
 local ok,err=pcall(fn,...)
 if not ok then faults=faults+1;emit('FAULT',{message=err,incomplete=true})end
end
local function identity(p,c,d,plot)return table.concat({p,c,d,plot},':')end
local function typeName(index)local r=GameInfo.Districts[index];return r and r.DistrictType or tostring(index)end
local function rows(name,fn)
 local source=GameInfo[name]
 if source then for r in source()do fn(r)end end
end
local replacements={}
rows('DistrictReplaces',function(r)
 replacements[r.ReplacesDistrictType]=replacements[r.ReplacesDistrictType]or{}
 table.insert(replacements[r.ReplacesDistrictType],r.CivUniqueDistrictType)
end)
local mapped={}
for k in pairs(profiles)do mapped[k]={}end
local function map(k,host,stage,building,role)
 if not mapped[k]or not GameInfo.Districts[host]then return end
 local function add(name)
  local index=GameInfo.Districts[name].Index
  mapped[k][index]=mapped[k][index]or{}
  mapped[k][index][table.concat({role or'customer',stage or 0,building or''},':')]=
   {role=role or'customer',stage=stage or 0,building=building}
 end
 add(host);for _,name in ipairs(replacements[host]or{})do add(name)end
end
rows('CSC_QuarterCustomerBuildings',function(r)map(r.QuarterKey,r.DistrictType,r.ProducerStage,r.BuildingType)end)
rows('CSC_Stage3CustomerTransactions',function(r)
 local d=GameInfo.Districts[r.SellerDistrictType];local p=d and byType[d.Index]
 if p then map(p.key,r.CustomerDistrictType,3,r.CustomerBuildingType)end
end)
rows('CSC_QuarterWonderSales',function(r)map(r.QuarterKey,'DISTRICT_WONDER',r.ProducerStage,r.BuildingType,'wonderCustomer')end)
-- Unique buildings can change the host district as well as the building type.
rows('BuildingReplaces',function(r)
 local unique=GameInfo.Buildings[r.CivUniqueBuildingType]
 if unique then
  local additions={}
  for k,hosts in pairs(mapped)do for _,rules in pairs(hosts)do for _,rule in pairs(rules)do
   if rule.building==r.ReplacesBuildingType then additions[#additions+1]={k,rule.stage,rule.role}end
   end end end
  for _,a in ipairs(additions)do map(a[1],unique.PrereqDistrict,a[2],unique.BuildingType,a[3])end
 end
end)
rows('Districts',function(r)
 for k in pairs(profiles)do
  if A.HasTag('CLASS_CSC_'..k..'_SALES',r.DistrictType)then map(k,r.DistrictType,0,nil,'sales')end
  if A.HasTag('CLASS_CSC_'..k..'_GOODS_PROVIDER',r.DistrictType)then map(k,r.DistrictType,0,nil,'goodsProvider')end
 end
end)
local compatible={}
rows('Improvement_ValidResources',function(r)
 local i=GameInfo.Improvements[r.ImprovementType]
 if i then compatible[r.ResourceType]=compatible[r.ResourceType]or{};compatible[r.ResourceType][i.Index]=true end
end)
for k,hosts in pairs(mapped)do for d,rules in pairs(hosts)do for _,rule in pairs(rules)do
 emit('MAPPING',{quarter=k,district=d,districtType=typeName(d),role=rule.role,stage=rule.stage,building=rule.building,source='loadedRegistryAndTags'})
end end end
local function buildingAt(d,kind)
 if not kind then return 0 end
 local def=GameInfo.Buildings[kind];local city=CityManager.GetCity(d.player,d.city)
 if not def or not city then return 0 end
 local bs=city:GetBuildings()
 if not bs:HasBuilding(def.Index)or bs:GetBuildingLocation(def.Index)~=d.plot then return 0 end
 return bs:IsPillaged(def.Index)and 1 or 2
end
local function order(q,c,field)
 local a,b=q[field],c[field]
 if a and b then if a==b then return 'sameTurn' elseif a<b then return 'quarterFirst'else return 'neighbourFirst'end end
 if not a and b then return 'quarterPreexistingDateUnknown'end
 if a and not b then return 'neighbourPreexistingDateUnknown'end
 return 'bothDatesUnknown'
end
local function scanRelations()
 local now={}
 for plot,q in pairs(districts)do local p=byType[q.district]
  if p then for _,near in ipairs(Map.GetAdjacentPlots(q.x,q.y))do
   local c=districts[near:GetIndex()]
   if c and c.player==q.player then for ruleID,rule in pairs(mapped[p.key][c.district]or{})do
    local status=buildingAt(c,rule.building)
    -- A generic Wonder footprint is insufficient: a named mapped Wonder must
    -- physically exist there. Ordinary customer footprints remain observable
    -- before their mapped building, with buildingStatus=0 explicitly.
    if rule.role~='wonderCustomer'or status>0 then
     local id=plot..':'..c.plot..':'..ruleID;now[id]=true
     local fingerprint=table.concat({q.player,c.player,tostring(q.complete),tostring(c.complete),tostring(q.pillaged),tostring(c.pillaged),status},':')
     if relations[id]~=fingerprint then
      emit('RELATION',{quarter=p.key,player=q.player,city=q.city,quarterPlot=plot,neighbourPlot=c.plot,neighbourCity=c.city,
       neighbourDistrict=c.district,role=rule.role,stage=rule.stage,building=rule.building,buildingStatus=status,
       quarterComplete=q.complete,neighbourComplete=c.complete,quarterPillaged=q.pillaged,neighbourPillaged=c.pillaged,
       foundationOrder=order(q,c,'foundationTurn'),completionOrder=order(q,c,'completionTurn'),
       quarterFoundationTurn=q.foundationTurn,neighbourFoundationTurn=c.foundationTurn,
       quarterFirstSeen=q.firstSeen,neighbourFirstSeen=c.firstSeen,present=true})
      relations[id]=fingerprint
     end
    end
   end end
  end end
 end
 for id in pairs(relations)do if not now[id]then emit('RELATION_REMOVED',{relation=id});relations[id]=nil end end
end
local function adjacency(d,source)
 local reader=CSC_AI_PLANNING_READ_ADJACENCY or(ExposedMembers and ExposedMembers.CSC_Adjacency and ExposedMembers.CSC_Adjacency.GetDistrictAdjacency)
 if type(reader)~='function'then emit('ADJACENCY',{player=d.player,city=d.city,district=d.district,plot=d.plot,source=source,available=false,reason='qualifiedUIReaderUnavailable'});return end
 local v=reader(d.player,d.city,d.plot,d.district)
 if not v then emit('ADJACENCY',{player=d.player,city=d.city,district=d.district,plot=d.plot,source=source,available=false,reason='UIReaderReturnedNil'});return end
 local row={player=d.player,city=d.city,district=d.district,plot=d.plot,source=source,available=v.available,
  sampledTurn=v.turn,plotDistrict=v.plotDistrict,footprintMatches=v.plotDistrict==d.district,
  exactFoundationTime=false,reason=v.reason}
 for name,value in pairs(v.yields or{})do row[name]=value end
 emit('ADJACENCY',row)
 if v.available and v.plotDistrict==d.district then adjacencyPending[d.plot]=nil
 else adjacencyPending[d.plot]=d end
end
local function observe(player,city,d,source)
 local plot=Map.GetPlot(d:GetX(),d:GetY());local index=plot:GetIndex();local old=districts[index]
 local q={player=player,city=city,district=d:GetType(),districtID=d:GetID(),plot=index,x=d:GetX(),y=d:GetY(),
  complete=d:IsComplete(),pillaged=d:IsPillaged(),firstSeen=turn()}
 local same=old and old.district==q.district and(old.districtID==q.districtID or old.player~=q.player or old.city~=q.city)
 -- Native IDs are seat-local. Capture preserves physical history even when the
 -- receiver gets another ID; an incomplete same-owner replacement is a rebuild.
 if old and old.district==q.district and old.complete and q.complete then same=true end
 if same then
  q.firstSeen=old.firstSeen;q.foundationTurn=old.foundationTurn;q.completionTurn=old.completionTurn
 end
 local event
 if not same then
  event=source=='added'and'FOUNDATION'or'FIRST_OBSERVED'
  if source=='added'then q.foundationTurn=turn()end
  if q.complete and source~='seed'then q.completionTurn=turn()end
 elseif old.player~=q.player or old.city~=q.city then event='OWNERSHIP'
 elseif old.complete~=q.complete then event=q.complete and'COMPLETION'or'COMPLETION_REVERSED';if q.complete then q.completionTurn=turn()end
 elseif old.pillaged~=q.pillaged then event=q.pillaged and'PILLAGED'or'REPAIRED'
 end
 districts[index]=q
 if event then
  local id=identity(player,city,q.district,index);local bid=offers[id];local last=native[id];local op=opportunities[player..':'..city..':'..q.district]
  emit(event,{player=player,city=city,district=q.district,districtType=typeName(q.district),districtID=q.districtID,plot=index,
   previousPlayer=old and old.player,previousCity=old and old.city,source=source,complete=q.complete,pillaged=q.pillaged,
   foundationTurn=q.foundationTurn,completionTurn=q.completionTurn,firstSeen=q.firstSeen,
   foundationDateKnown=q.foundationTurn~=nil,eventMissing=event=='FIRST_OBSERVED'and source=='poll',
   completionTimeExact=event=='COMPLETION'and source=='progress',
   bidVersion=bid and bid.version,bidQ8=bid and bid.finalQ8,bidAdjacency=bid and bid.adjacency,
   opportunityTurn=op and op.turn,opportunityBest=op and op.best,opportunityQualified=op and op.qualified,
   nativeQ8=last and last.result,nativeDrainTurn=last and last.observedTurn,nativeOrdinal=last and last.nativeOrdinal,
   nativeCallTurnKnown=false})
  safe(adjacency,q,event)
 end
 return q
end
local function materialFact(q,p,near)
 local resource=GameInfo.Resources[near:GetResourceType()];local improvement=GameInfo.Improvements[near:GetImprovementType()]
 local name=resource and resource.ResourceType or'NONE'
 local base=resource and A.HasTag(p.base,name)or false;local spec=resource and A.HasTag(p.specialty,name)or false
 local vis=PlayersVisibility[q.player]
 local visible=resource and(not A.ResourceVisible or A.ResourceVisible(q.player,resource.Index))or false
 local revealed=vis and vis:IsRevealed(near:GetX(),near:GetY())or false
 local matches=resource and compatible[name]and compatible[name][near:GetImprovementType()]or false
 -- Compatibility alone is not a Quarter supply role: an unrelated Potato Farm
 -- can be valid and working without supplying Tailors. Role-gate this flag so
 -- its later removal is not misreported as lost CSC supply. Keep compatible
 -- separately for raw geometry/debugging; it carries no supplier claim.
 local working=(base or spec)and matches and not near:IsImprovementPillaged()and near:GetOwner()==q.player and near:GetDistrictType()==-1 and visible and revealed
 return {resource=name,resourceIndex=near:GetResourceType(),improvement=improvement and improvement.ImprovementType or'NONE',
  improvementIndex=near:GetImprovementType(),pillaged=near:IsImprovementPillaged(),owner=near:GetOwner(),district=near:GetDistrictType(),
  base=base,spec=spec,visible=visible,revealed=revealed,compatible=matches,working=working,
  origin=CSC_PLANNING_RESOURCE_ORIGINS and CSC_PLANNING_RESOURCE_ORIGINS[name]or'unclassified'}
end
local function fingerprint(row)
 local result={};for k,v in pairs(row)do result[#result+1]=k..'='..tostring(v)end;table.sort(result);return table.concat(result,';')
end
local function scanMaterials(source,changedPlot)
 local alive={}
 for plot,q in pairs(districts)do local p=byType[q.district]
  if p then
   local facts,counts={}, {base=0,spec=0,baseWorking=0,specWorking=0}
   local relevant=changedPlot==nil
   for _,near in ipairs(Map.GetAdjacentPlots(q.x,q.y))do
    if near:GetIndex()==changedPlot then relevant=true end
    local f=materialFact(q,p,near);facts[#facts+1]={plot=near:GetIndex(),fact=f}
    local eligible=f.owner==q.player and f.district==-1 and f.visible and f.revealed
    if f.base and eligible then counts.base=counts.base+1;if f.working then counts.baseWorking=counts.baseWorking+1 end end
    if f.spec and eligible then counts.spec=counts.spec+1;if f.working then counts.specWorking=counts.specWorking+1 end end
   end
   for _,entry in ipairs(facts)do
    local id=plot..':'..entry.plot;alive[id]=true
    if relevant then
     local f=entry.fact;local old=materials[id];local signature=fingerprint(f)
     if not old or old.signature~=signature then
      local row={player=q.player,city=q.city,quarter=p.key,quarterPlot=plot,materialPlot=entry.plot,source=source,
       previousResource=old and old.fact.resource,previousImprovement=old and old.fact.improvement,
       previousOwner=old and old.fact.owner,previousWorking=old and old.fact.working,
       lostBase=old and old.fact.base and not f.base or false,lostSpec=old and old.fact.spec and not f.spec or false,
       lostWorking=old and old.fact.working and not f.working or false,
       lastBase=counts.base==0,lastSpec=counts.spec==0,lastWorkingBase=counts.baseWorking==0,lastWorkingSpec=counts.specWorking==0}
      for k,v in pairs(f)do row[k]=v end
      -- Raw resource disappearance, loss of ownership, pillage and visibility
      -- are independent fields; fog is never asserted to be a physical harvest.
      emit('MATERIAL_STATE',row);materials[id]={signature=signature,fact=f}
     end
    end
   end
   if relevant then emit('MATERIAL_TOTAL',{player=q.player,city=q.city,quarter=p.key,quarterPlot=plot,source=source,
    base=counts.base,spec=counts.spec,baseWorking=counts.baseWorking,specWorking=counts.specWorking})end
  end
 end
 if not changedPlot then for id in pairs(materials)do if not alive[id]then emit('MATERIAL_WATCH_ENDED',{identity=id,reason='quarterNoLongerPresent'});materials[id]=nil end end end
end
local function scan(source)
 local present={}
 -- Players also contains uninitialised/dead seats whose GetCities method can
 -- return nil. Alive is the same engine roster used by the existing watcher;
 -- keep city-states for capture chronology, without probing every vacant slot.
 for _,player in ipairs(PlayerManager.GetAlive())do
  local pid=player:GetID();local cities=player:GetCities()
  if cities then for _,city in cities:Members()do
   local ds=city:GetDistricts()
   for i=0,ds:GetNumDistricts()-1 do local d=ds:GetDistrictByIndex(i)
    if d then local q=observe(pid,city:GetID(),d,source);present[q.plot]=true end
   end
  end end
 end
 for plot,d in pairs(districts)do if not present[plot]then emit('REMOVED',{player=d.player,city=d.city,district=d.district,plot=plot,source=source});districts[plot]=nil end end
 for plot in pairs(adjacencyPending)do
  if districts[plot]then safe(adjacency,districts[plot],'FIRST_LATER_OBSERVATION')else adjacencyPending[plot]=nil end
 end
 scanRelations();scanMaterials(source)
 emit('POLL',{source=source,records=records,faults=faults,dropped=dropped})
end
local function event(source,pid,districtID,cityID,x,y,kind)
 local player=Players[pid];local ds=player and player:GetDistricts();local d=ds and ds:FindID(districtID)
 if not d or d:GetX()~=x or d:GetY()~=y or d:GetType()~=kind then
  emit('EVENT_DEFERRED',{source=source,player=pid,city=cityID,districtID=districtID,x=x,y=y,district=kind,reason='liveIdentityNotReady'});return
 end
 observe(pid,cityID,d,source);scanRelations()
 -- Capture suppliers immediately when a Quarter first appears. Other district
 -- events resample only neighbours of that footprint, catching overwrites in
 -- the same turn rather than waiting for the next global poll.
 if byType[kind]then scanMaterials(source)
 else scanMaterials(source,Map.GetPlot(x,y):GetIndex())end
end
-- Native records arrive through the parent's existing single journal reader.
-- Drain time is observable; CE's current trace does not timestamp the native
-- call. Retaining a best record is evidence of a comparison, not construction.
function W.Native(row)
 safe(function()
  local r={};for k,v in pairs(row)do if type(v)~='table'then r[k]=v end end
  r.observedTurn=r.observedTurn or turn();r.nativeCallTurnKnown=false
  if r.nativeKind=='decline'then
   emit('NATIVE_DECLINE',r);return
  end
  native[identity(r.player,r.city,r.district,r.plot)]=r;emit('NATIVE_BEST',r)
 end)
end
local quarterBids=E.QuarterBids
E.QuarterBids=function(snapshot,placement,protected,early,...)
 local captured,scopes={},{};local geometry=snapshot.Geometry
 -- Keep scopes with zero eligible geometric calls: otherwise a completely
 -- unavailable city/type would vanish rather than show a deferred packet.
 safe(function()for _,p in ipairs(placement.StageTwoProfiles())do
  for _,city in snapshot.player:GetCities():Members()do
   if not city:GetDistricts():HasDistrict(p.district.Index)then
    scopes[snapshot.id..':'..city:GetID()..':'..p.district.Index]={player=snapshot.id,city=city:GetID(),district=p.district.Index,
     seen=0,qualified=0,offered=0,best=-1,turn=turn()}
   end
  end
 end end)
 snapshot.Geometry=function(city,plot,profile,...)
  local result=pack(geometry(city,plot,profile,...))
  safe(function()
   local g=result[1];local id=identity(snapshot.id,city:GetID(),profile.district.Index,plot:GetIndex())
   captured[id]={player=snapshot.id,city=city:GetID(),district=profile.district.Index,plot=plot:GetIndex(),
    direct=g.base,upper=g.upper,qualified=g.upper+1e-6>=3,owner=plot:GetOwner(),frontier=plot:GetOwner()==-1,
    protected=protected and protected[plot:GetIndex()]~=nil,turn=turn()}
  end)
  return unpack(result,1,result.n)
 end
 local result=pack(pcall(quarterBids,snapshot,placement,protected,early,...))
 snapshot.Geometry=geometry
 if not result[1]then error(result[2])end
 safe(function()pending[snapshot.id]={captured=captured,scopes=scopes,turn=turn()}end)
 return unpack(result,2,result.n)
end
local publish=B.Publish
B.Publish=function(version,width,height,count,players,entries,...)
 local extras=pack(...)
 local result=pack(publish(version,width,height,count,players,entries,...))
 safe(function()
  emit('PUBLICATION',{version=version,accepted=result[1],pendingTurn=turn()})
  if result[1]then
   -- Observe the exact accepted typed scopes and acquisition proposals. This
   -- records attempted policy, independently of native masking or payment.
   for _,r in ipairs(extras[1]or{})do if r.acquisition then
    local copy={version=version};for k,v in pairs(r)do if type(v)~='table'then copy[k]=v end end
    emit('ACQUISITION_OFFER',copy)
   end end
   for _,r in ipairs(extras[12]or{})do
    emit('DECLINE_OFFER',{version=version,player=r.player,city=r.city,district=r.district,plot=r.plot})
   end
   local accepted={}
   for _,r in ipairs(entries or{})do if byType[r.district]and r.finalQ8 and r.finalQ8>0 then
    local copy={version=version};for k,v in pairs(r)do if type(v)~='table'then copy[k]=v end end
    accepted[identity(r.player,r.city,r.district,r.plot)]=copy
   end end
   local summaries={}
   for _,batch in pairs(pending)do for scope,row in pairs(batch.scopes)do summaries[scope]=row end end
   for _,batch in pairs(pending)do for id,r in pairs(batch.captured)do
    local scope=r.player..':'..r.city..':'..r.district
    local s=summaries[scope]or{player=r.player,city=r.city,district=r.district,seen=0,qualified=0,offered=0,best=-1,turn=batch.turn}
    summaries[scope]=s;s.seen=s.seen+1;s.best=math.max(s.best,r.upper)
    if r.qualified then s.qualified=s.qualified+1 end
    if accepted[id]then s.offered=s.offered+1 end
    local row={};for k,v in pairs(r)do row[k]=v end
    row.version=version;row.offered=accepted[id]~=nil;row.bidQ8=accepted[id]and accepted[id].finalQ8
    row.geometryOnly=true;row.nativeEligibility='notMeasured';row.futureCustomersCounted=false
    emit('OPPORTUNITY',row)
   end end
   for scope,s in pairs(summaries)do
    local old=opportunities[scope];s.version=version
    -- Deferred means this accepted packet contains no positive offer for this
    -- scope. It does NOT claim an engine rejection or diagnose a missing unlock.
    s.state=s.offered>0 and'offered'or'deferred'
    emit('OPPORTUNITY_SUMMARY',s)
    if not old or old.state~=s.state then emit('PLAN_TRANSITION',{player=s.player,city=s.city,district=s.district,
     previous=old and old.state or'unobserved',state=s.state,version=version,
     reconsidered=old and old.state=='deferred'and s.state=='offered'or false})end
    opportunities[scope]=s
   end
   offers=accepted
  end
  -- Never associate a rejected/old diagnostic capture with a later packet.
  pending={}
 end)
 return unpack(result,1,result.n)
end
Events.DistrictAddedToMap.Add(function(...)safe(event,'added',...)end)
Events.DistrictBuildProgressChanged.Add(function(...)safe(event,'progress',...)end)
for _,name in ipairs({'ResourceAddedToMap','ResourceRemovedFromMap','ImprovementAddedToMap','ImprovementRemovedFromMap','ImprovementChanged'})do
 local source=name;local hook=Events[source]
 if hook and hook.Add then
  hook.Add(function(x,y)safe(function()local plot=Map.GetPlot(x,y);if plot then scanMaterials(source,plot:GetIndex())end end)end)
  emit('CAPABILITY',{name=source,available=true})
 else emit('CAPABILITY',{name=source,available=false,fallback='perTurnMaterialPoll'})end
end
GameEvents.OnGameTurnStarted.Add(function()
 local t=turn();if lastPoll==t then return end;lastPoll=t;safe(scan,'poll')
end)
function W.Finish()safe(scan,'finish');emit('FINISH',{records=records,faults=faults,dropped=dropped,incomplete=faults>0 or dropped>0})end
safe(scan,'seed')
emit('INSTALLED',{geometry='observedExistingPolicyCalls',materialCadence='everyGlobalTurnAndAvailableEvents',
 resourceOriginAvailable=CSC_PLANNING_RESOURCE_ORIGINS~=nil,
 adjacencyReaderAvailable=type(CSC_AI_PLANNING_READ_ADJACENCY)=='function'or(ExposedMembers and ExposedMembers.CSC_Adjacency and type(ExposedMembers.CSC_Adjacency.GetDistrictAdjacency)=='function')or false,
 exactNativeCallTurnAvailable=false,recordsLimit=limit})
