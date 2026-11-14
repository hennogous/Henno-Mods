-- DIAGNOSTIC ONLY: physical district facts -> passive baseline journal.
-- No CSC policy, pseudo-yields, scores, properties, production orders or RNG
-- writes. Foundation and completion stay separate; captures retain physical
-- history. The native companion reads cached totals before the placement
-- factory, while UI adjacency is sampled independently in PlotInfo.
assert(not CSC_VANILLA_DISTRICTS,'Duplicate baseline observer')
local scope=assert(CSC_VANILLA_SCOPE)
local unpack=unpack or table.unpack
local W={seen={},pending={},faults=0,records=0,last=-1}
CSC_VANILLA_DISTRICTS=W
local function emit(kind,row)
 W.records=W.records+1
 assert(W.records<=200000,'Baseline district journal bound exceeded')
 row.turn=row.turn or Game.GetCurrentGameTurn()
 local f={};for k,v in pairs(row)do f[#f+1]=k..'='..tostring(v)end
 table.sort(f);print('CSC_PLANNING_'..kind..'\t'..table.concat(f,'\t'))
end
function W.Health()
 assert(not GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER,'CSC content loaded in no-CSC control')
 assert(not GameInfo.Yields.YIELD_CSC_AI_PLACEMENT,'CSC connector loaded in no-CSC control')
 assert(not CSC_AI_BAKERS_RUNTIME and not CSC_AI_QuarterPlacement,'CSC policy loaded in control')
 local status=assert(CE_AIDistrictScoresStatus)()
 for _,key in ipairs({'enabled','version','entries','matched','changed','faults','managedTypes'})do
  assert(status:match('"'..key..'":0[,}]'),'Unexpected native policy state: '..key)
 end
 assert(status:match('"ready":1'),'Native capability unavailable')
end
local function safe(fn,...)
 local ok,err=pcall(fn,...)
 if not ok then W.faults=W.faults+1;print('CSC_VANILLA_DISTRICT_FAULT',Game.GetCurrentGameTurn(),tostring(err))end
end
local function observe(pid,cid,d,source,eventTurn)
 local plot=assert(Map.GetPlot(d:GetX(),d:GetY()));local index=plot:GetIndex()
 local old=W.seen[index]
 local same=old and old.district==d:GetType()and
  (old.districtID==d:GetID()or old.player~=pid or old.city~=cid or old.complete and d:IsComplete())
 local q={player=pid,city=cid,district=d:GetType(),districtID=d:GetID(),plot=index,
  complete=d:IsComplete(),pillaged=d:IsPillaged()}
 if same then q.foundationTurn=old.foundationTurn;q.completionTurn=old.completionTurn end
 local event
 if not same then
  event=source=='added'and'FOUNDATION'or'FIRST_OBSERVED'
  if source=='added'then q.foundationTurn=eventTurn or Game.GetCurrentGameTurn()end
  if q.complete then q.completionTurn=Game.GetCurrentGameTurn()end
 elseif old.player~=pid or old.city~=cid then event='OWNERSHIP'
 elseif old.complete~=q.complete then
  event=q.complete and'COMPLETION'or'COMPLETION_REVERSED'
  if q.complete then q.completionTurn=Game.GetCurrentGameTurn()end
 elseif old.pillaged~=q.pillaged then event=q.pillaged and'PILLAGED'or'REPAIRED'end
 W.seen[index]=q
 if event then
  local row={};for k,v in pairs(q)do row[k]=v end
  row.districtType=assert(GameInfo.Districts[q.district]).DistrictType
  row.source=source;row.previousPlayer=old and old.player;row.previousCity=old and old.city
  row.eventMissing=event=='FIRST_OBSERVED'and source=='poll'
  row.nativeCallTurnKnown=false
  emit(event,row)
 end
end
local function inspect(source,pid,did,cid,x,y,kind,eventTurn)
 local player=Players[pid];local d=player and player:GetDistricts():FindID(did)
 if not d or d:GetX()~=x or d:GetY()~=y or d:GetType()~=kind then
  if source=='added'then W.pending[pid..':'..did]={pid,did,cid,x,y,kind,eventTurn or Game.GetCurrentGameTurn()}end
  return
 end
 W.pending[pid..':'..did]=nil;observe(pid,cid,d,source,eventTurn)
end
local function scan(source)
 local present={}
 for key,v in pairs(W.pending)do inspect('added',unpack(v))end
 for _,player in ipairs(PlayerManager.GetAlive())do
  local cities=player:GetCities()
  if cities then for _,city in cities:Members()do
   local ds=city:GetDistricts()
   for i=0,ds:GetNumDistricts()-1 do
    local d=ds:GetDistrictByIndex(i);if d then
     present[assert(Map.GetPlot(d:GetX(),d:GetY())):GetIndex()]=true
     observe(player:GetID(),city:GetID(),d,source)
    end
   end
  end end
 end
 for index,old in pairs(W.seen)do
  if not present[index]then
   local plot=Map.GetPlotByIndex(index)
   -- A temporarily missing city collection is not proof of demolition. Only
   -- retire physical history when the plot's actual district type changed.
   if not plot or plot:GetDistrictType()~=old.district then
    emit('REMOVED',{player=old.player,city=old.city,district=old.district,plot=index,source=source})
    W.seen[index]=nil
   end
  end
 end
end
local function census()
 local count=0
 local function row(kind,...)
  local a={...};for i,v in ipairs(a)do a[i]=tostring(v)end
  print('CSC_ENDPOINT_'..kind..'\t'..table.concat(a,'\t'));count=count+1
 end
 print('CSC_FULL_RUN_CENSUS_BEGIN',Game.GetCurrentGameTurn())
 for _,pid in ipairs(scope.players)do
  local player=assert(Players[pid]);row('PLAYER',pid,player:IsAlive())
  if player:IsAlive()then
   for _,city in player:GetCities():Members()do row('CITY',pid,city:GetID(),city:GetPopulation())end
  end
 end
 print('CSC_ENDPOINT_END\t'..Game.GetCurrentGameTurn()..'\t'..count)
end
function W.Finish()
 W.Health();scan('poll')
 assert(W.faults==0,'Baseline district observer faulted')
 -- Events can outlive the original player/district lookup after capture,
 -- replacement or removal. Retain every unresolved event for the coverage
 -- audit instead of aborting a completed game and the next campaign arm.
 -- These rows describe observation gaps, not additional built districts.
 -- Health/observer faults above still stop an unsafe or broken measurement.
 local pending=0
 for _,v in pairs(W.pending)do
  pending=pending+1
  emit('PENDING_EVENT',{player=v[1],districtID=v[2],city=v[3],x=v[4],y=v[5],
   district=v[6],eventTurn=v[7],source='unresolved-added-event'})
 end
 print('CSC_VANILLA_DISTRICT_FINISHED',Game.GetCurrentGameTurn(),W.records,W.faults,pending)
end
W.Health();scan('seed')
-- Only the first six event arguments identify the district. Extra native
-- payload fields are not timestamps. Capture our callback clock explicitly,
-- retaining it in pending rows if the public lookup becomes available later.
Events.DistrictAddedToMap.Add(function(pid,did,cid,x,y,kind)
 safe(inspect,'added',pid,did,cid,x,y,kind,Game.GetCurrentGameTurn())
end)
Events.DistrictBuildProgressChanged.Add(function(pid,did,cid,x,y,kind)
 safe(inspect,'progress',pid,did,cid,x,y,kind,Game.GetCurrentGameTurn())
end)
GameEvents.OnGameTurnStarted.Add(function()
 safe(function()
  local t=Game.GetCurrentGameTurn();if W.last==t then return end;W.last=t
  scan('poll')
  if t%25==0 and t<=scope.through then W.Health();census()end
 end)
end)
print('CSC_VANILLA_DISTRICT_INSTALLED',Game.GetCurrentGameTurn())
