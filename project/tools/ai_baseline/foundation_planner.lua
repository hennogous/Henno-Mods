-- Maintained offline foundation planner, policy v2 (22 October 2026).
-- Derived from the executed diagnostic planner; study archives stay unchanged.
-- The driver still supplies native-legal candidates and verifies UI zero progress,
-- positive unchanged cost, native legality and the result of each commitment.
-- This file is not installed gameplay and does not schedule native commands.
assert(not CSC_FOUNDATION_PROBE,'Refuse to install twice')
include('CSC_AdjacencyCore')
local A=assert(CSC_Adjacency)
CSC_FOUNDATION_PROBE={version='foundation-policy-v2-same-type-base-priority',targets={},history={},errors={},events={},skips={}}
local P=CSC_FOUNDATION_PROBE
local function safely(label,fn,...)
 local ok,value=pcall(fn,...)
 if ok then return value end
 P.errors[#P.errors+1]={turn=Game.GetCurrentGameTurn(),label=label,error=tostring(value)}
 return nil
end
local function query(object,name,...)
 local fn=object and object[name]
 if type(fn)~='function' then return nil end
 local ok,value=pcall(fn,object,...)
 if ok then return value end
 return nil
end
function P.Observe(target,reason)
 local player=Players[target.player]
 local city=player and player:GetCities():FindID(target.city)
 local row={turn=Game.GetCurrentGameTurn(),player=target.player,city=target.city,quarter=target.quarter,plot=target.plot,reason=reason}
 if not city then row.city_missing=true;return row end
 local plot=Map.GetPlotByIndex(target.plot)
 local district=city:GetDistricts():GetDistrictAtLocation(plot:GetX(),plot:GetY())
 local queue=city:GetBuildQueue()
 row.owner=plot:GetOwner();row.population=city:GetPopulation()
 row.district_present=district~=nil
 row.complete=district and district:IsComplete() or false
 row.district_type=district and district:GetType() or -1
 if row.complete and row.district_type==target.districtIndex then target.observed_complete=true end
 row.progress=query(queue,'GetDistrictProgress',target.districtIndex)
 row.cost=query(queue,'GetDistrictCost',target.districtIndex)
 row.current=query(queue,'CurrentlyBuilding')
 row.current_hash=query(queue,'GetCurrentProductionTypeHash')
 row.has_been_placed=query(queue,'HasBeenPlaced',target.districtHash)
 row.queue_size=query(queue,'GetSize')
 row.queue={}
 if row.queue_size then
  for i=0,row.queue_size-1 do
   local item=query(queue,'GetAt',i)
   if type(item)=='table' then
    local shallow={index=i}
    for k,v in pairs(item) do if type(v)=='string' or type(v)=='number' or type(v)=='boolean' then shallow[tostring(k)]=v end end
    row.queue[#row.queue+1]=shallow
   end
  end
 end
 return row
end
local maps={}
for _,key in ipairs({'BAKERS','TAILORS'}) do
 maps[key]={base={},spec={}}
 for row in GameInfo.TypeTags() do
  local r=GameInfo.Resources[row.Type]
  if r then
   if row.Tag=='CLASS_CSC_'..key..'_BASE' then maps[key].base[r.Index]=true end
   if row.Tag=='CLASS_CSC_'..key..'_SPEC' then maps[key].spec[r.Index]=true end
  end
 end
end
-- Repeated planning is read-only. The controller supplies fresh native-legal UI targets.
-- An existing Quarter blocks only another copy of the SAME Quarter type.
-- An unfinished different Quarter remains legal when the native driver allows it.
P.scans={}
local function describe(candidate)
 local pid=candidate.player
 assert(pid>=1 and pid<=5,'No player0/NPC placement')
 local player=Players[pid]
 if not player or not player:IsAlive() or not player:IsMajor() or player:IsHuman() then return nil end
 local city=player:GetCities():FindID(candidate.city)
 if not city then return nil end
 local def=assert(GameInfo.Districts['DISTRICT_CSC_'..candidate.quarter..'_QUARTER'])
 if city:GetDistricts():HasDistrict(def.Index) then return nil end
 local plot=assert(Map.GetPlotByIndex(candidate.plot))
 if plot:GetOwner()~=pid or plot:GetDistrictType()>=0 or plot:GetResourceType()>=0 or plot:GetImprovementType()>=0 or plot:GetFeatureType()>=0 then return nil end
 local base,spec,materials=0,0,{}
 for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY())) do
  local resource=near:GetResourceType()
  if near:GetOwner()==pid and resource>=0 and A.ResourceVisible(pid,resource) then
   local b=maps[candidate.quarter].base[resource] or false
   local s=maps[candidate.quarter].spec[resource] or false
   if b or s then
    if b then base=base+1 end;if s then spec=spec+1 end
    materials[#materials+1]={plot=near:GetIndex(),resource=GameInfo.Resources[resource].ResourceType,base=b,spec=s,owner=near:GetOwner(),improvement=near:GetImprovementType(),pillaged=near:IsImprovementPillaged()}
   end
  end
 end
 if base==0 then return nil end
 local t={}
 for k,v in pairs(candidate)do t[k]=v end
 t.base=base;t.spec=spec;t.both=spec>0;t.materials=materials;t.districtIndex=def.Index
 assert(type(t.districtHash)=='number','Explicit UI district hash required')
 return t
end
local function better(a,b)
 -- Retain the existing Both-class preference. Within that tier, dependable
 -- Base count precedes total material count (hence Specialty count on ties).
 if a.both~=b.both then return a.both end
 if a.base~=b.base then return a.base>b.base end
 if a.base+a.spec~=b.base+b.spec then return a.base+a.spec>b.base+b.spec end
 if a.plot~=b.plot then return a.plot<b.plot end
 return a.quarter<b.quarter
end
function P.Plan(candidates)
 local bycity={};local eligible=0
 for _,c in ipairs(candidates)do
  local t=describe(c)
  if t then
   eligible=eligible+1
   local key=t.player..'/'..t.city
   if not bycity[key] or better(t,bycity[key])then bycity[key]=t end
  end
 end
 local plan={};for _,t in pairs(bycity)do plan[#plan+1]=t end
 table.sort(plan,function(a,b)if a.player~=b.player then return a.player<b.player end;if a.city~=b.city then return a.city<b.city end;return better(a,b)end)
 local used,unique={},{}
 for _,t in ipairs(plan)do if not used[t.plot]then used[t.plot]=true;unique[#unique+1]=t end end
 P.plan=unique
 P.scans[#P.scans+1]={turn=Game.GetCurrentGameTurn(),native_candidates=#candidates,material_eligible=eligible,selected=#unique}
end
function P.Commit()
 local used={}
 for _,target in ipairs(P.plan)do
  assert(not used[target.plot]);used[target.plot]=true
  local fresh=assert(describe(target),'Candidate changed since UI preflight')
  assert(fresh.base==target.base and fresh.spec==target.spec,'Material state changed')
  for _,old in ipairs(P.targets)do assert(old.plot~=target.plot,'Never replace or recreate a previous assisted site')end
  local city=assert(Players[target.player]:GetCities():FindID(target.city))
  target.before=P.Observe(target,'before-placement')
  target.placed_turn=Game.GetCurrentGameTurn();target.requested_percentage=0
  print('CSC_DIAG_FOUNDATION_BEGIN',Game.GetCurrentGameTurn(),target.player,target.city,target.plot,target.districtIndex)
  city:GetBuildQueue():CreateIncompleteDistrict(target.districtIndex,target.plot,0)
  print('CSC_DIAG_FOUNDATION_RETURN',Game.GetCurrentGameTurn(),target.player,target.city,target.plot)
  -- Store before asserting, so even a partial failure preserves the mutation record.
  P.targets[#P.targets+1]=target
  target.after=P.Observe(target,'immediately-after-placement')
  assert(target.after.district_present and not target.after.complete,'Expected an incomplete foundation')
  P.history[#P.history+1]=target.after
 end
 P.plan={}
end
function P.Capture(reason)
 for _,target in ipairs(P.targets) do P.history[#P.history+1]=P.Observe(target,reason) end
end
Events.PlayerTurnActivated.Add(function(pid)
 if pid>=0 and pid<=5 then print('CSC_DIAG_PLAYER_TURN',Game.GetCurrentGameTurn(),pid,#P.targets,#P.errors)end
 for _,target in ipairs(P.targets) do if target.player==pid and not target.observed_complete then
  safely('player-turn-observation',function()P.history[#P.history+1]=P.Observe(target,'player-turn-start')end)
 end end
end)
Events.CityProductionCompleted.Add(function(pid,cid,order,item,cancelled)
 if pid>=1 and pid<=5 then P.events[#P.events+1]={turn=Game.GetCurrentGameTurn(),player=pid,city=cid,order=order,item=item,cancelled=cancelled} end
end)
function P.Export()
 local function json(value)
  local t=type(value)
  if t=='nil' then return 'null' end
  if t=='number' or t=='boolean' then return tostring(value) end
  if t=='string' then return string.format('%q',value) end
  if t~='table' then return 'null' end
  local array,n=true,0
  for k in pairs(value) do n=n+1;if type(k)~='number' then array=false end end
  if n~=#value then array=false end
  local out={}
  if array then for i=1,#value do out[#out+1]=json(value[i]) end;return '['..table.concat(out,',')..']' end
  local keys={};for k in pairs(value) do keys[#keys+1]=k end;table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
  for _,k in ipairs(keys) do out[#out+1]=json(tostring(k))..':'..json(value[k]) end
  return '{'..table.concat(out,',')..'}'
 end
 print('CSC_FOUNDATION_EXPORT='..json(P))
end
