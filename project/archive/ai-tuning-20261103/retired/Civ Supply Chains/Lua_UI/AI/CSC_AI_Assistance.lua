-- Installed CSC assistance. No FireTuner, autoplay, research orders, Builder
-- orders or free construction. Economic changes use the explicitly assisted
-- quoted-assignment backend verified in the test controller, not AI PURCHASE.
include('CSC_AdjacencyCore')
include('CSC_AI_OpportunityPolicy')
local P=CSC_AI_OpportunityPolicy
local A=CSC_Adjacency
CSC_AI_Assistance={version=4,cache={},geography={},busy=false,queued={}}
local M=CSC_AI_Assistance
ExposedMembers.CSC_AI_Assistance=M
local PREFIX='CSC_AI_ASSISTANCE_V1_'
local function get(k,default)local v=Game:GetProperty(PREFIX..k);if v==nil then return default end;return v end
local function put(k,v)Game:SetProperty(PREFIX..k,v)end
local function indexReceipt(kind,key)
 local entries=get(kind..'_INDEX',{})
 entries[#entries+1]=key;put(kind..'_INDEX',entries)
end
local function count(kind,amount)
 local totals=get('TOTALS',{tiles=0,cost=0,own=0,subsidy=0,foundations=0})
 totals[kind]=totals[kind]+amount;put('TOTALS',totals)
end
local function mode()
 for row in GameInfo.CSC_AI_Profile()do if row.Id=='ACTIVE'then return row.Mode end end
 return 'OFF'
end
local function eligible(pid)
 local p=Players[pid];local ui=ExposedMembers.CSC_AI_AssistanceUI
 if mode()=='OFF'or not p or not p:IsAlive()or not p:IsMajor()or not ui or type(ui.IsAIPlayer)~='function'then return false end
 local humans=get('INITIAL_HUMANS')
 if not humans then
  if type(ui.InitialHumanPlayers)~='function'then return false end
  humans=ui.InitialHumanPlayers();if type(humans)~='table'then return false end
  put('INITIAL_HUMANS',humans)
 end
 return not humans[tostring(pid)]and ui.IsAIPlayer(pid)==true
end

local function supported()
 local ui=ExposedMembers.CSC_AI_AssistanceUI
 return ui and type(ui.SupportsEconomics)=='function'and ui.SupportsEconomics()==true
end

local function equal(a,b)
 if type(a)~=type(b)then return false end
 if type(a)~='table'then return a==b end
 for k,v in pairs(a)do if not equal(v,b[k])then return false end end
 for k in pairs(b)do if a[k]==nil then return false end end
 return true
end
-- Preserve old diagnostic failures when upgrading the host. No economic,
-- foundation, cooldown or TURN ledger is reset or retried.
if get('HOST_REVISION',0)<3 then
 local previous={}
 for pid=0,63 do local e=get('ERROR_'..pid);if e then previous[tostring(pid)]=e;put('ERROR_'..pid,nil)end end
 put('DIAGNOSTIC_ERRORS_BEFORE_REVISION3',previous);put('HOST_REVISION',3)
end
local function warn(pid,error)
 local t=Game.GetCurrentGameTurn();put('ERROR_'..pid,{turn=t,error=tostring(error)})
 print('CSC AI assistance paused for player',pid,t,tostring(error))
end
local function guarded(pid,fn)
 local ok,error=pcall(fn)
 if not ok then warn(pid,error)end
 return ok
end
local materials={}
for _,key in ipairs({'BAKERS','TAILORS'})do
 local def=GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER']
 if def then
  local item={def=def,base={},spec={}};materials[key]=item
  for tag in GameInfo.TypeTags()do local r=GameInfo.Resources[tag.Type]
   if r then
    if tag.Tag=='CLASS_CSC_'..key..'_BASE'then item.base[r.Index]=true end
    if tag.Tag=='CLASS_CSC_'..key..'_SPEC'then item.spec[r.Index]=true end
   end
  end
 end
end
local function bridge()return ExposedMembers.CSC_AI_AssistanceUI end
local function unlocked(p,d)
 return (not d.PrereqTech or p:GetTechs():HasTech(GameInfo.Technologies[d.PrereqTech].Index))
  and(not d.PrereqCivic or p:GetCulture():HasCivic(GameInfo.Civics[d.PrereqCivic].Index))
end
local function geometry(city)
 local key=city:GetOwner()..':'..city:GetID()..':'..city:GetX()..':'..city:GetY()
 if not M.geography[key]then
  local rows={}
  for idx=0,Map.GetPlotCount()-1 do local p=Map.GetPlotByIndex(idx)
   if Map.GetPlotDistance(city:GetX(),city:GetY(),p:GetX(),p:GetY())<=4 then rows[#rows+1]=idx end
  end
  M.geography[key]=rows
 end
 return key,M.geography[key]
end
local function pillage(p)
 if type(p.IsImprovementPillaged)=='function'then return p:IsImprovementPillaged()end
 return nil -- Unknown is not a functioning material.
end
local function facts(city)
 local pid=city:GetOwner();local key,indices=geometry(city)
 local tiles,stamp={}, {tostring(city:GetPopulation())}
 local player=Players[pid]
 for _,q in ipairs({'BAKERS','TAILORS'})do local d=materials[q]and materials[q].def
  if d then stamp[#stamp+1]=q..':'..tostring(unlocked(player,d))..':'..tostring(city:GetDistricts():HasDistrict(d.Index))end
 end
 for _,idx in ipairs(indices)do local p=Map.GetPlotByIndex(idx)
  local reveal=PlayersVisibility[pid]:IsRevealed(p:GetX(),p:GetY())
  local owner=p:GetOwner();local resource=p:GetResourceType()
  local visible=resource<0 or A.ResourceVisible(pid,resource)
  stamp[#stamp+1]=table.concat({idx,owner,resource,p:GetDistrictType(),p:GetImprovementType(),p:GetFeatureType(),tostring(pillage(p)),tostring(reveal),tostring(visible)},':')
  if reveal and visible and(owner==pid or owner==-1)and(owner==pid or Map.GetPlotDistance(city:GetX(),city:GetY(),p:GetX(),p:GetY())<=3)then
   local t={index=idx,owner=owner,resource=resource,plot=p,neighbors={}}
   for direction=0,5 do local n=Map.GetAdjacentPlot(p:GetX(),p:GetY(),direction);if n then t.neighbors[#t.neighbors+1]=n:GetIndex()end end
   tiles[idx]=t
  end
 end
 return key,table.concat(stamp,'|'),tiles
end
local function clear(p)
 return p:GetDistrictType()<0 and p:GetResourceType()<0 and p:GetFeatureType()<0 and p:GetImprovementType()<0
end
local function keyOf(c)return c.player..':'..c.city..':'..c.quarter..':'..c.source end
local plannerV2,plannerCandidate,plannerValidate,plannerNote
local function catalog(city,key,stamp,tiles)
 local pid=city:GetOwner();local turn=Game.GetCurrentGameTurn();local cached=M.cache[key]
 if not plannerV2()and cached and cached.stamp==stamp and turn-cached.turn<25 then return cached.plans end
 local plans={};local player=Players[pid]
 for _,quarter in ipairs({'BAKERS','TAILORS'})do local q=materials[quarter]
  if q and unlocked(player,q.def)and not city:GetDistricts():HasDistrict(q.def.Index)then
   for _,index in ipairs(M.geography[key])do local source=tiles[index]
    if source and Map.GetPlotDistance(city:GetX(),city:GetY(),source.plot:GetX(),source.plot:GetY())<=3 and clear(source.plot)then
     local f=bridge().Read(pid,city:GetID(),quarter,index,index,false)
     if f and f.can_produce and f.potential and not f.same_type then
      local base,spec={},{}
      for _,near in ipairs(source.neighbors)do local t=tiles[near]
       if t and t.plot:GetDistrictType()<0 then
        if q.base[t.resource]then base[#base+1]=near end
        if q.spec[t.resource]then spec[#spec+1]=near end
       end
      end
      table.sort(base);table.sort(spec)
      if plannerV2()then
       -- V2 discovers Both and explicit Base-only intents. It refreshes customer,
       -- unlock and attachment facts every callback, independently of map cache.
       for _,b in ipairs(base)do
        local choices={};for _,s in ipairs(spec)do choices[#choices+1]=s end;choices[#choices+1]=false
        for _,s in ipairs(choices)do
         local c={player=pid,city=city:GetID(),quarter=quarter,source=index,materials=s and{b,s}or{b},base=#base,spec=s and #spec or 0,missing=0,intent_version=2}
         local used={};for _,i in ipairs({index,b,s or nil})do if not used[i]and tiles[i].owner<0 then c.missing=c.missing+1 end;used[i]=true end
         local evidence,reason,packet=plannerCandidate(c,false)
         plannerNote(c,evidence,reason,packet)
         if evidence then c.v2_intent=CSC_AI_CustomerPlannerV2.Intent(evidence,c.materials);c.v2_evidence=evidence;plans[#plans+1]=c end
        end
       end
      else
      for _,b in ipairs(base)do for _,s in ipairs(spec)do
       local c={player=pid,city=city:GetID(),quarter=quarter,source=index,materials={b,s},base=#base,spec=#spec,missing=0}
       local used={};for _,i in ipairs({index,b,s})do if not used[i]and tiles[i].owner<0 then c.missing=c.missing+1 end;used[i]=true end
       plans[#plans+1]=c
      end end
      end
     end
    end
   end
  end
 end
 table.sort(plans,plannerV2()and P.PlannerBetter or P.Better);M.cache[key]={stamp=stamp,turn=turn,plans=plans}
 return plans
end
local function current(c,plannerFresh)
 assert(eligible(c.player),'AI owner changed')
 local city=assert(CityManager.GetCity(c.player,c.city));assert(city:GetOwner()==c.player)
 local source=assert(Map.GetPlotByIndex(c.source));assert(clear(source),'Source occupied')
 local map=materials[c.quarter];assert(map and unlocked(Players[c.player],map.def))
 assert(not city:GetDistricts():HasDistrict(map.def.Index),'Same Quarter already present')
 local base,spec=false,false
 for _,idx in ipairs(c.materials)do local p=assert(Map.GetPlotByIndex(idx))
  assert(p:GetDistrictType()<0 and Map.GetPlotDistance(source:GetX(),source:GetY(),p:GetX(),p:GetY())==1)
  assert(PlayersVisibility[c.player]:IsRevealed(p:GetX(),p:GetY())and A.ResourceVisible(c.player,p:GetResourceType()))
  base=base or map.base[p:GetResourceType()];spec=spec or map.spec[p:GetResourceType()]
 end
 if c.intent_version==2 then
  assert(plannerV2()and base and c.v2_intent,'Typed v2 Base intent required')
  assert((c.v2_intent.kind=='both'and spec and #c.materials==2)or(c.v2_intent.kind=='base_only_real4'and #c.materials==1),'Typed material contract changed')
  assert(plannerValidate(c,plannerFresh~=false),'V2 customer/material/quality intent changed')
 else assert(base and spec,'Both materials lost')end
 return city,source,map.def
end
local PILOT='CSC_AI_INVESTMENT_PILOT_V1'
local PILOT_STATE='CSC_AI_INVESTMENT_PILOT_STATE_V1'
-- Resource/improvement membership is native table data, not a guessed Farm or
-- Mine rule. Rebuilt per inspection/check so a missing mapping fails closed.
local function materialFact(pid,quarter,index,role)
 local plot=Map.GetPlotByIndex(index);if not plot then return {plot=index,known=false,working=false}end
 local resource=GameInfo.Resources[plot:GetResourceType()]
 local improvement=GameInfo.Improvements and GameInfo.Improvements[plot:GetImprovementType()]
 local valid=false;local known=GameInfo.Improvement_ValidResources~=nil
 if resource and improvement and known then
  for row in GameInfo.Improvement_ValidResources()do
   if row.ResourceType==resource.ResourceType and row.ImprovementType==improvement.ImprovementType then valid=true;break end
  end
 end
 local q=materials[quarter];local mapped=q and q[role]and q[role][plot:GetResourceType()]==true or false
 local revealed=PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY())
 local visible=A.ResourceVisible(pid,plot:GetResourceType())
 local row={plot=index,known=true,owner=plot:GetOwner(),resource=plot:GetResourceType(),resource_type=resource and resource.ResourceType,
  improvement=plot:GetImprovementType(),improvement_type=improvement and improvement.ImprovementType,
  improvement_pillaged=pillage(plot),district=plot:GetDistrictType(),mapped=mapped,revealed=revealed,resource_visible=visible,
  native_valid_improvement=valid,native_mapping_known=known}
 row.working=mapped and row.owner==pid and row.district<0 and revealed and visible and valid and row.improvement_pillaged==false
 return row
end
local function copy(value)
 if type(value)~='table'then return value end
 local out={};for k,v in pairs(value)do out[k]=copy(v)end;return out
end
local function pilotStatus(state,status,reason)
 state.status=status;state.reason=reason;state.turn=Game.GetCurrentGameTurn()
 Game:SetProperty(PILOT_STATE,state)
end
-- This gate only restricts the installed economic owner. Reconciliation of an
-- assignment already issued deliberately bypasses it and never resends a grant.
local function pilotAllowed(c)
 local config=Game:GetProperty(PILOT)
 local state=Game:GetProperty(PILOT_STATE)
 if config==nil then
  if state~=nil then
   if type(state)=='table'then pilotStatus(state,'closed','config_missing')end
   return false
  end
  return true
 end
 if state~=nil and type(state)~='table'then return false end
 local turn=Game.GetCurrentGameTurn();local target,reason=P.PilotPlan(config,turn)
 if state and not equal(state.config,config)then
  pilotStatus(state,'closed','config_changed');return false
 end
 if not target then
  if state and reason=='deadline'then pilotStatus(state,'closed',reason)end
  return false
 end
 if not P.PilotMatches(config,c)then return false end
 if not state then state={config=copy(config),status='armed',turn=turn};Game:SetProperty(PILOT_STATE,state)end
 if state.status~='armed'then return false end
 if get('FOUNDATION_'..keyOf(c))then pilotStatus(state,'observing','foundation_already_requested');return false end
 local ok,error=pcall(function()
  assert(eligible(c.player),'role_lost')
  local city=assert(CityManager.GetCity(c.player,c.city),'city_missing')
  assert(city:GetOwner()==c.player and city:GetX()==config.city_x and city:GetY()==config.city_y,'city_identity_changed')
  local source=assert(Map.GetPlotByIndex(c.source),'source_missing')
  assert(clear(source)and(source:GetOwner()==c.player or source:GetOwner()==-1),'source_changed')
  assert(PlayersVisibility[c.player]:IsRevealed(source:GetX(),source:GetY()),'source_hidden')
  assert(Map.GetPlotDistance(city:GetX(),city:GetY(),source:GetX(),source:GetY())<=3,'source_range_changed')
  local map=assert(materials[c.quarter],'quarter_missing')
  assert(unlocked(Players[c.player],map.def)and not city:GetDistricts():HasDistrict(map.def.Index),'quarter_changed')
  for i,role in ipairs({'base','spec'})do
   local fact=materialFact(c.player,c.quarter,c.materials[i],role)
   assert(fact.known and fact.resource==config.material_resources[i]and fact.mapped,'material_identity_changed')
   assert(fact.district<0 and fact.revealed and fact.resource_visible and(fact.owner==c.player or fact.owner==-1),'material_lost')
   local p=Map.GetPlotByIndex(c.materials[i])
   assert(Map.GetPlotDistance(source:GetX(),source:GetY(),p:GetX(),p:GetY())==1,'material_adjacency_changed')
   if i==1 or config.spec_policy~='conditional'then assert(fact.working,'working_'..role..'_lost')end
  end
 end)
 if not ok then pilotStatus(state,'closed',tostring(error));return false end
 return true
end

-- Observation only: no eligible() call (which can persist initial humans), no
-- Game:SetProperty, no economic or queue orders. Local geometry/cache is allowed.
-- Every candidate carries its own current exact UI queue/preflight snapshot;
-- missing APIs remain explicit errors rather than fabricated readiness.
function M.Inspect(pid)
 local out={version=1,turn=Game.GetCurrentGameTurn(),player=pid,cities={},pilot=copy(Game:GetProperty(PILOT)),pilot_state=copy(Game:GetProperty(PILOT_STATE)),action_authorization=false}
 local player=Players[pid];local U=bridge()
 if not player or not U or type(U.IsAIPlayer)~='function'then out.error='player_or_UI_unavailable';return out end
 local humans=get('INITIAL_HUMANS');if humans==nil and type(U.InitialHumanPlayers)=='function'then humans=U.InitialHumanPlayers()end
 out.profile=mode();out.original_humans=copy(humans)
 out.eligible=mode()~='OFF'and player:IsAlive()and player:IsMajor()and type(humans)=='table'and not humans[tostring(pid)]and U.IsAIPlayer(pid)==true
 out.supported=supported()==true
 if not out.eligible then out.error='ineligible_player';return out end
 local treasury=player:GetTreasury();out.economics={gold=treasury:GetGoldBalance(),gross=treasury:GetGoldYield(),upkeep=treasury:GetTotalMaintenance()}
 local cities={};for _,city in player:GetCities():Members()do cities[#cities+1]=city end
 table.sort(cities,function(a,b)return a:GetID()<b:GetID()end)
 for _,city in ipairs(cities)do
  local row={city=city:GetID(),owner=city:GetOwner(),x=city:GetX(),y=city:GetY(),population=city:GetPopulation(),districts={},buildings={},tiles={},candidates={}}
  out.cities[#out.cities+1]=row
  local ok,error=pcall(function()
   local ds=city:GetDistricts()
   for i=0,ds:GetNumDistricts()-1 do local d=ds:GetDistrictByIndex(i);local def=GameInfo.Districts[d:GetType()]
    local district={index=d:GetType(),type=def and def.DistrictType,x=d:GetX(),y=d:GetY(),complete=d:IsComplete()}
    if type(d.IsPillaged)=='function'then district.pillaged=d:IsPillaged()end
    for _,quarter in ipairs({'BAKERS','TAILORS'})do local map=materials[quarter]
     if map and district.index==map.def.Index then
      district.quarter=quarter;district.materials={base={},spec={}}
      for direction=0,5 do local near=Map.GetAdjacentPlot(district.x,district.y,direction)
       if near then for _,role in ipairs({'base','spec'})do if map[role][near:GetResourceType()]then
        district.materials[role][#district.materials[role]+1]=materialFact(pid,quarter,near:GetIndex(),role)
       end end end
      end
     end
    end
    row.districts[#row.districts+1]=district
   end
   if GameInfo.Buildings~=nil then
    local buildings=city:GetBuildings()
    for b in GameInfo.Buildings()do if buildings:HasBuilding(b.Index)then
     row.buildings[#row.buildings+1]={index=b.Index,type=b.BuildingType,pillaged=buildings:IsPillaged(b.Index)}
    end end
   else row.buildings_error='building_inventory_unavailable' end
   local key,stamp,tiles=facts(city);row.stamp=stamp
   for _,idx in ipairs(M.geography[key])do local t=tiles[idx]
    if t then row.tiles[#row.tiles+1]={plot=idx,owner=t.owner,resource=t.resource,district=t.plot:GetDistrictType(),improvement=t.plot:GetImprovementType(),improvement_pillaged=pillage(t.plot),neighbors=copy(t.neighbors)}end
   end
   for _,c in ipairs(catalog(city,key,stamp,tiles))do
    local candidate=copy(c);candidate.material_facts={materialFact(pid,c.quarter,c.materials[1],'base')};if c.materials[2]then candidate.material_facts[2]=materialFact(pid,c.quarter,c.materials[2],'spec')end
    candidate.working_base=candidate.material_facts[1].working;candidate.working_spec=candidate.material_facts[2]and candidate.material_facts[2].working
    local readOK,f=pcall(U.Read,pid,c.city,c.quarter,c.source,c.source,true)
    if readOK and f then candidate.native=copy(f);if row.queue==nil then row.queue=copy(f.queue)end else candidate.native_error=tostring(f)end
    if c.materials[2]then candidate.pilot_input={version=1,player=pid,city=c.city,city_x=row.x,city_y=row.y,quarter=c.quarter,source=c.source,materials=copy(c.materials),
     material_resources={candidate.material_facts[1].resource,candidate.material_facts[2].resource},start_turn=out.turn,deadline_turn=out.turn+25,spec_policy='ready'}end
    row.candidates[#row.candidates+1]=candidate
   end
   -- Queue enumeration is not uniformly exposed in Gameplay. Its absence is
   -- optional observation loss; preserve the physical/candidate facts above and
   -- leave the queue unset for a separate UI read rather than inventing one.
   if row.queue==nil then
    local queueOK,snapshot,queueError=pcall(function()
     local q=city:GetBuildQueue()
     for _,method in ipairs({'GetSize','GetCurrentProductionTypeHash','GetAt'})do
      if not q or type(q[method])~='function'then return nil,'queue_unavailable:'..method end
     end
     local result={size=q:GetSize(),hash=q:GetCurrentProductionTypeHash(),items={}}
     for i=0,result.size-1 do local item=q:GetAt(i);local scalar={}
      if type(item)=='table'then for k,v in pairs(item)do if type(v)~='table'and type(v)~='userdata'and type(v)~='function'then scalar[k]=v end end end
      result.items[#result.items+1]=scalar
     end
     return result
    end)
    if queueOK and snapshot then row.queue=snapshot
    else row.queue_error=queueOK and queueError or tostring(snapshot)end
   end
  end)
  if not ok then row.error=tostring(error)end
 end
 return out
end
local screenAllowed,screenCommit,screenProcess,screenMode,screenRefuse
do
 local CONFIG='CSC_AI_SELECTIVE_SCREEN_V1'
 local STATE='CSC_AI_SELECTIVE_SCREEN_STATE_V1'
 local definitions=nil
 screenMode=function()return P.ScreenMode(Game:GetProperty(CONFIG),Game:GetProperty(STATE))end
 plannerV2=function()local config=Game:GetProperty(CONFIG);return type(config)=='table'and config.version==2 and screenMode()=='active'end
 local function originalAI(pid)
  local roles=get('INITIAL_HUMANS')
  if type(roles)~='table'or roles[tostring(pid)]==true or roles[pid]==true then return false end
  for _,human in pairs(roles)do if human==true then return true end end
  return false -- An empty/unknown original-role mask proves no AI role.
 end
 plannerCandidate=function(c,fresh)
  local V=CSC_AI_CustomerPlannerV2;local U=bridge()
  if not plannerV2()or not V or not U or type(U.ReadPlannerV2)~='function'then return nil,'v2_adapter_unavailable'end
  local packet,error=U.ReadPlannerV2(c.player,c.city,c.quarter,c.source,c.materials[1],c.materials[2],originalAI(c.player),fresh)
  if not packet then return nil,error end
  local result=V.Evaluate({version=2},packet)
  if c.v2_intent then
   local bound,reason=V.Revalidate(c.v2_intent,packet);return bound,reason,packet
  end
  local state=Game:GetProperty(STATE);local record=type(state)=='table'and type(state.records)=='table'and state.records[keyOf(c)]or nil
  if type(record)=='table'and record.intent_version==2 then
   local bound,reason=V.Revalidate(record.v2_intent,packet)
   if bound then c.v2_intent=copy(record.v2_intent)end
   return bound,reason,packet
  end
  if result.status~='candidate'then return nil,result.status,packet end
  return result,nil,packet
 end
 plannerValidate=function(c,fresh)
  if not c.v2_intent then return nil,'typed_intent_required'end
  local result,error,packet=plannerCandidate(c,fresh)
  if not result then return nil,error end
  return CSC_AI_CustomerPlannerV2.Revalidate(c.v2_intent,packet)
 end
 plannerNote=function(c,evidence,reason,packet)
  local discovery=M.v2Discovery and M.v2Discovery[tostring(c.player)]
  if not discovery or discovery.active~=true or discovery.turn~=Game.GetCurrentGameTurn()then return end
  local function summary()
   local result=evidence or(packet and CSC_AI_CustomerPlannerV2.Evaluate({version=2},packet))
   if not result then return nil end
   local customer=copy(result.customer);if customer then customer.quality=nil end
   return{captured_turn=discovery.turn,identity=copy(packet.identity),status=result.status,kind=result.kind,
    reasons=copy(result.reasons),customer=customer,real=copy(result.real),conditional=result.conditional,
    current_real_combined=result.current_real_combined,projected_real_combined=result.projected_real_combined,
    value_scope=packet.value_scope,native_context_validation=packet.native_context_validation,
    unknown_secondary_costs=copy(result.unknown_secondary_costs),action_authorization=false}
  end
  if packet and not discovery.first_packet then discovery.first_packet=summary()end
  if evidence then discovery.candidates=discovery.candidates+1
   if not discovery.first_candidate then discovery.first_candidate=summary()end
  else
   local why=tostring(reason or'planner_evidence_unknown'):sub(1,300)
   local bucket=why
   if discovery.rejected[bucket]==nil then
    if discovery.reason_kinds>=16 then bucket='other_reasons_capped'else discovery.reason_kinds=discovery.reason_kinds+1 end
   end
   discovery.rejected[bucket]=(discovery.rejected[bucket]or 0)+1
   discovery.last_missing_fact={site=keyOf(c),reason=why}
   local essential=packet==nil or why=='deferred_real_quality_unknown'
   if essential then local error={turn=discovery.turn,site=keyOf(c),reason=why}
    discovery.evidence_error_count=discovery.evidence_error_count+1
    discovery.first_error=discovery.first_error or error;discovery.last_error=error
   end
  end
 end
 local function variants(name)
  local out={};local row=GameInfo.Buildings and GameInfo.Buildings[name]
  if row then out[#out+1]=row end
  if GameInfo.BuildingReplaces then for replace in GameInfo.BuildingReplaces()do
   if replace.ReplacesBuildingType==name then local child=GameInfo.Buildings[replace.CivUniqueBuildingType]
    if child then out[#out+1]=child end
   end
  end end
  return out
 end
 local function defs()
  if definitions then return definitions end
  local out={}
  for _,q in ipairs({'BAKERS','TAILORS'})do if materials[q]then out[q]={producer={},customer={},paths3={}}end end
  if GameInfo.CSC_QuarterFlowBuildings then for row in GameInfo.CSC_QuarterFlowBuildings()do
   local definition=out[row.QuarterKey]
   if definition and row.Stage==2 then
    for _,building in ipairs(variants(row.BuildingType))do definition.producer[#definition.producer+1]=building end
   end
  end end
  if GameInfo.CSC_QuarterCustomerBuildings then for row in GameInfo.CSC_QuarterCustomerBuildings()do
   local definition=out[row.QuarterKey]
   if definition and row.ProducerStage==2 then
    for _,building in ipairs(variants(row.BuildingType))do
     local item={Index=building.Index,BuildingType=building.BuildingType,customer_districts={}}
     local parent=GameInfo.Districts[row.DistrictType]
     if parent then item.customer_districts[parent.Index]=true end
     if GameInfo.DistrictReplaces then for replace in GameInfo.DistrictReplaces()do
      if replace.ReplacesDistrictType==row.DistrictType then local district=GameInfo.Districts[replace.CivUniqueDistrictType]
       if district then item.customer_districts[district.Index]=true end
      end
     end end
     definition.customer[#definition.customer+1]=item
    end
   end
  end end
  -- Stage3 transactions keep their exact seller/customer pairing. These
  -- transactions are not generally Base-gated; Base below defines this screen's
  -- full-supply milestone, not the transaction engine or Service requirements.
  if GameInfo.CSC_Stage3CustomerTransactions then for row in GameInfo.CSC_Stage3CustomerTransactions()do
   local q=row.SellerDistrictType and row.SellerDistrictType:match('DISTRICT_CSC_(.+)_QUARTER');local definition=out[q]
   if definition and type(row.TransactionId)=='string'then
    local path={id=row.TransactionId,producer=variants(row.SellerBuildingType),customer={}}
    local districts={};local parent=GameInfo.Districts[row.CustomerDistrictType]
    if parent then districts[parent.Index]=true end
    if GameInfo.DistrictReplaces then for replace in GameInfo.DistrictReplaces()do
     if replace.ReplacesDistrictType==row.CustomerDistrictType then local district=GameInfo.Districts[replace.CivUniqueDistrictType]
      if district then districts[district.Index]=true end
     end
    end end
    for _,building in ipairs(variants(row.CustomerBuildingType))do path.customer[#path.customer+1]={Index=building.Index,BuildingType=building.BuildingType,customer_districts=districts}end
    definition.paths3[#definition.paths3+1]=path
   end
  end end
  for _,definition in pairs(out)do table.sort(definition.paths3,function(a,b)return a.id<b.id end)end
  definitions=out;return out
 end
 local function functioning(buildings,rows)
  for _,row in ipairs(rows)do if buildings:HasBuilding(row.Index)and buildings:IsPillaged(row.Index)==false then return row.BuildingType end end
 end
 local EFFECTS={BAKERS={[2]='CSC_BAKERS_STAGE_2_EFFECT_GROWTH',[3]='CSC_BAKERS_STAGE_3_EFFECT_HOUSING'},TAILORS={[2]='CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION',[3]='CSC_TAILORS_STAGE_3_EFFECT_FAITH'}}
 local function effect(city,key)
  if type(city.GetProperty)~='function'then return{key=key,observed=false,unavailable='GetProperty'}end
  local ok,value=pcall(city.GetProperty,city,key)
  if not ok then return{key=key,observed=false,error=tostring(value)}end
  return{key=key,observed=true,present=value~=nil,value=value}
 end
 -- One bounded owned-city/district inventory in the existing AI callback. No
 -- world scan, UI roundtrip, queue getter, Builder assignment or new event.
 local function inventory(pid)
  local out={cities={},districts={},dependencies={}}
  for _,city in Players[pid]:GetCities():Members()do
   local buildings=city:GetBuildings();local entry={id=city:GetID(),x=city:GetX(),y=city:GetY(),owner=city:GetOwner(),producer={},producer3={},effects={}}
   out.cities[tostring(entry.id)]=entry
   for q,definition in pairs(defs())do
    entry.producer[q]=functioning(buildings,definition.producer);entry.producer3[q]={};entry.effects[q]={[2]=effect(city,EFFECTS[q][2]),[3]=effect(city,EFFECTS[q][3])}
    for _,path in ipairs(definition.paths3)do entry.producer3[q][path.id]=functioning(buildings,path.producer)end
   end
   local ds=city:GetDistricts()
   for i=0,ds:GetNumDistricts()-1 do local district=ds:GetDistrictByIndex(i)
    local plot=Map.GetPlot(district:GetX(),district:GetY());assert(plot,'District plot unavailable')
    local row={plot=plot:GetIndex(),city=entry.id,owner=plot:GetOwner(),type=district:GetType(),complete=district:IsComplete(),customer={},customer3={}}
    local info=GameInfo.Districts[row.type]
    row.functioning=info and(info.DistrictType=='DISTRICT_CITY_CENTER'or district:IsPillaged()==false)or false
    for q,definition in pairs(defs())do
     for _,building in ipairs(definition.customer)do
      if building.customer_districts[row.type]and buildings:HasBuilding(building.Index)and buildings:IsPillaged(building.Index)==false then row.customer[q]=building.BuildingType;break end
     end
     row.customer3[q]={}
     for _,path in ipairs(definition.paths3)do for _,building in ipairs(path.customer)do
      if building.customer_districts[row.type]and buildings:HasBuilding(building.Index)and buildings:IsPillaged(building.Index)==false then row.customer3[q][path.id]=building.BuildingType;break end
     end end
     if materials[q].def.Index==row.type and row.owner==pid then
      local dependency={source=row.plot,materials={}}
      for direction=0,5 do local near=Map.GetAdjacentPlot(plot:GetX(),plot:GetY(),direction)
       if near and near:GetDistrictType()<0 and(materials[q].base[near:GetResourceType()]or materials[q].spec[near:GetResourceType()])then dependency.materials[#dependency.materials+1]=near:GetIndex()end
      end
      out.dependencies[#out.dependencies+1]=dependency
     end
    end
    out.districts[row.plot]=row
   end
  end
  return out
 end
 local function customers(pid,q,source,inv)
  local found={}
  for direction=0,5 do local near=Map.GetAdjacentPlot(source:GetX(),source:GetY(),direction);local d=near and inv.districts[near:GetIndex()]
   if d and d.owner==pid and d.complete and d.functioning and d.customer[q]then found[#found+1]={plot=d.plot,city=d.city,building=d.customer[q]}end
  end
  return found
 end
 local function stage3Paths(pid,q,source,inv,city)
  local found={}
  for _,path in ipairs(defs()[q].paths3)do local producer=city.producer3[q][path.id]
   if producer then for direction=0,5 do local near=Map.GetAdjacentPlot(source:GetX(),source:GetY(),direction);local d=near and inv.districts[near:GetIndex()]
    local building=d and d.customer3[q]and d.customer3[q][path.id]
    if d and d.owner==pid and d.complete and d.functioning and building then
     found[#found+1]={stage=3,transaction=path.id,producer=producer,prerequisite_producer=city.producer[q],customer={plot=d.plot,city=d.city,building=building},transaction_base_gate='not asserted; full-supply screen separately requires working Base'}
    end
   end end
  end
  return found
 end
 local function futureOption(pid,resource)
  if not resource or not GameInfo.Improvement_ValidResources or not GameInfo.Improvements then return nil end
  for row in GameInfo.Improvement_ValidResources()do if row.ResourceType==resource.ResourceType then local improvement=GameInfo.Improvements[row.ImprovementType]
   -- A unique-trait option is not credited without a recipient proof. Mapping
   -- and unlocks are projection only, never a CanHave/worker/path assertion.
   if improvement and not improvement.TraitType and unlocked(Players[pid],improvement)then return improvement.ImprovementType end
  end end
 end
 local function baseFacts(pid,q,source,selected)
  local out={known=true,present=false,working=false,plots={}}
  assert(materials[q]and next(materials[q].base)~=nil,'Base mapping unavailable')
  for direction=0,5 do local near=Map.GetAdjacentPlot(source:GetX(),source:GetY(),direction)
   if near then
    local revealed=PlayersVisibility[pid]:IsRevealed(near:GetX(),near:GetY())
    if not revealed then out.known=false end
    if materials[q].base[near:GetResourceType()]and near:GetDistrictType()<0 then
     out.present=true;local fact=materialFact(pid,q,near:GetIndex(),'base');out.plots[#out.plots+1]=fact
     out.working=out.working or fact.working
     if not fact.resource_visible or(fact.owner~=pid and fact.owner~=-1)then out.known=false end
    end
    if selected==near:GetIndex()and near:GetOwner()~=pid and near:GetOwner()~=-1 then out.known=false end
   end
  end
  return out
 end
 local function observe(record,inv)
  local fact={known=true,operational=false,base_known=false,base_present=false,reason='developing_chain'}
  local city=inv.cities[tostring(record.city)]
  if not city or city.owner~=record.player or city.x~=record.city_x or city.y~=record.city_y then fact.irrecoverable='city_lost_or_identity_changed';return fact end
  local source=Map.GetPlotByIndex(record.source)
  if not source then fact.known=false;fact.reason='source_unknown';return fact end
  local owner=source:GetOwner();fact.source_owned=owner==record.player
  if owner~=record.player and(owner~=-1 or record.source_owned_once)then fact.irrecoverable='source_ownership_lost';return fact end
  local q=assert(materials[record.quarter],'Quarter mapping unavailable')
  local district=source:GetDistrictType()
  if district>=0 and district~=q.def.Index then fact.irrecoverable='source_repurposed';return fact end
  local definition=defs()[record.quarter]
  if not definition or #definition.producer==0 or(#definition.customer==0 and #definition.paths3==0) then fact.known=false;fact.reason='chain_definition_unknown';return fact end
  local base=baseFacts(record.player,record.quarter,source,record.materials and record.materials[1])
  fact.base_known=base.known;fact.base_present=base.present;fact.working_base=base.working;fact.base=base.plots
  if not base.known then fact.known=false;fact.reason='base_visibility_or_ownership_unknown';return fact end
  local d=inv.districts[record.source]
  fact.quarter_complete=d and d.type==q.def.Index and d.complete or false
  fact.quarter_functioning=fact.quarter_complete and d.functioning or false
  fact.producer=city.producer[record.quarter]
  fact.customers=customers(record.player,record.quarter,source,inv)
  fact.stage3_paths=stage3Paths(record.player,record.quarter,source,inv,city);fact.qualifying_paths={}
  fact.effect_corroboration=city.effects[record.quarter] -- Diagnostic only, never release authority.
  if owner==record.player and fact.quarter_functioning and fact.producer~=nil and base.working then
   for _,customer in ipairs(fact.customers)do fact.qualifying_paths[#fact.qualifying_paths+1]={stage=2,producer=fact.producer,customer=customer}end
   for _,path in ipairs(fact.stage3_paths)do fact.qualifying_paths[#fact.qualifying_paths+1]=path end
  end
  fact.operational=#fact.qualifying_paths>0
  if fact.operational then fact.operational_stage=fact.qualifying_paths[1].stage;fact.operational_path=fact.qualifying_paths[1]end
  fact.benefit='structural_only; actual yields require outcome observation'
  if not fact.quarter_functioning then fact.reason='quarter_incomplete_or_pillaged'
  elseif not fact.producer then fact.reason='producer_missing_or_pillaged'
  elseif not base.working then fact.reason='base_development_or_repair_needed'
  elseif not fact.operational then fact.reason='customer_or_matching_stage3_path_missing_or_pillaged'end
  return fact
 end
 local function safeObserve(record,inv)
  local ok,fact=pcall(observe,record,inv)
  if ok then return fact end
  return{known=false,operational=false,reason='observation_error',error=tostring(fact)}
 end
 local function integer(value)
  return type(value)=='number'and value>=0 and value<math.huge and value==math.floor(value)
 end
 local function validRecords(records)
  local statuses={open=true,unknown=true,operational=true,maintenance=true,failed_sunk=true}
  for site,record in pairs(records)do
   if type(record)~='table'then return false end
   for _,field in ipairs({'player','city','source','city_x','city_y','first_turn'})do
    if not integer(record[field])then return false end
   end
   if(record.quarter~='BAKERS'and record.quarter~='TAILORS')or not statuses[record.status]
    or type(site)~='string'or site~=keyOf(record)or type(record.materials)~='table'then return false end
   if record.intent_version==2 then
    if type(record.v2_intent)~='table'or not P.ValidPlannerIntent(record.v2_intent,record)then return false end
   elseif #record.materials~=2 then return false end
   for i=1,#record.materials do if not integer(record.materials[i])or record.materials[i]==record.source then return false end end
  end
  return true
 end
 local function validDecisions(decisions)
  for pid,entry in pairs(decisions)do
   if type(pid)~='string'or not integer(tonumber(pid))or tostring(tonumber(pid))~=pid
    or type(entry)~='table'or not integer(entry.turn)or type(entry.reason)~='string'or entry.reason==''
    or(entry.site~=nil and type(entry.site)~='string')then return false end
   if entry.rejected~=nil then
    if type(entry.rejected)~='table'then return false end
    for reason,count in pairs(entry.rejected)do if type(reason)~='string'or not integer(count)then return false end end
   end
  end
  return true
 end
 local function refresh(pid,save)
  local state=Game:GetProperty(STATE);local mode=P.ScreenMode(Game:GetProperty(CONFIG),state)
  if mode=='legacy'then return nil,nil end
  if state~=nil and(type(state)~='table'or state.version~=1 or type(state.records)~='table'or type(state.decisions)~='table')then return nil,nil,'screen_state_invalid' end
  if state and not validRecords(state.records)then return nil,nil,'screen_record_invalid' end
  if state and not validDecisions(state.decisions)then return nil,nil,'screen_decision_invalid' end
  if state==nil and mode~='active'then return nil,nil,mode end
  if not save and state then state=copy(state)end
  if not state then state={version=1,activated_turn=Game.GetCurrentGameTurn(),records={},decisions={}}end
  local ok,inv=pcall(inventory,pid);if not ok then return state,nil,tostring(inv)end
  for _,record in pairs(state.records)do
   if record.player==pid then
   local fact=safeObserve(record,inv);local status,reason=P.ScreenStatus(record,fact)
   record.status=status;record.reason=reason;record.last_turn=Game.GetCurrentGameTurn();record.facts=fact
   if record.intent_version==2 then local planned=record.v2_intent.customer;local fulfilled=false
    for _,path in ipairs(fact.qualifying_paths or{})do local actual=path.customer
     if actual and path.stage==planned.stage and actual.plot==planned.plot and actual.building==planned.building and path.producer==planned.producer then fulfilled=true end
    end
    record.planned_customer_fulfilled=fulfilled
    record.planned_vs_actual='v2_intent is admission promise; facts.qualifying_paths are fresh physical structure; release need not match promise'
   end
   record.source_owned_once=record.source_owned_once or fact.source_owned==true
   if status=='operational'and record.first_operational_turn==nil then record.first_operational_turn=record.last_turn end
   if status=='failed_sunk'and record.failed_turn==nil then record.failed_turn=record.last_turn;record.failed_reason=reason end
   if status=='failed_sunk'and fact.operational then record.rehabilitated_turn=record.rehabilitated_turn or record.last_turn end
  end end
  if save then Game:SetProperty(STATE,state)end
  return state,inv
 end
 local function decision(state,pid,c,reason)
  state.decisions[tostring(pid)]={turn=Game.GetCurrentGameTurn(),site=c and keyOf(c),reason=reason}
  Game:SetProperty(STATE,state)
 end
 -- A rejected pre-economic snapshot is not an economic failure. Keep one
 -- compact last diagnostic per AI; never claim a site, reset ledgers or resend.
 screenRefuse=function(c,index,predicate,fact,gameplayOwner)
  if screenMode()=='active'then
   local state,inv,error=refresh(c.player,false)
   if state and inv and not error then
    local observed={}
    if fact then for _,field in ipairs({'turn','owner','revealed','in_range','reach','price'})do observed[field]=fact[field]end end
    local failure={turn=Game.GetCurrentGameTurn(),site=keyOf(c),plot=index,predicate=predicate,gameplay_owner=gameplayOwner,quote_available=fact~=nil,quote=observed}
    if type(state.route_failures)~='table'then state.route_failures={}end
    state.route_failures[tostring(c.player)]=failure
    state.decisions[tostring(c.player)]={turn=failure.turn,site=failure.site,reason='route_preflight_unavailable'}
    Game:SetProperty(STATE,state)
   end
  end
  return false
 end
 local function slot(state,c)
  local same=state.records[keyOf(c)]
  if same and same.status=='failed_sunk'then return false,'failed_site_no_replay' end
  if same and(same.status=='open'or same.status=='unknown')then return true end
  local open,maintenance=false,false
  for _,record in pairs(state.records)do if record.player==c.player then
   open=open or record.status=='open'or record.status=='unknown'
   maintenance=maintenance or record.status=='maintenance'
  end end
  if maintenance then return false,'maintenance_obligation' end
  if open then return false,'open_chain_cap' end
  if same then return false,'already_released_chain' end
  return true
 end
 local function candidateFacts(c,inv,quotes,fresh)
  if plannerV2()then
   local result,error=plannerValidate(c,fresh~=false)
   if not result then return nil,error end
   local customer=copy(result.customer);customer.quality=nil
   local evidence={working_base=result.base.working,existing_customer=result.customer.readiness=='actual',
    captured_turn=result.captured_turn,value_scope='ADMISSION-TIME estimated real components, not fresh checkpoint yield',horizon='named owned/currently selected prerequisites; no completion date or native customer choice promise',customer_readiness=result.customer.readiness,customer_rank=result.customer.readiness_rank,planner_version=2,kind=result.kind,
    base=result.base,customer=customer,real=result.real,current_real_combined=result.current_real_combined,projected_real_combined=result.projected_real_combined,
    conditional=result.conditional,unknown_secondary_costs=result.unknown_secondary_costs,alternatives_status=result.customer.alternatives_status}
   return evidence
  end
  if c.intent_version==2 then return nil,'typed_v2_config_required'end
  local definition=defs()[c.quarter]
  if not definition or #definition.producer==0 or #definition.customer==0 then return nil,'chain_definition_unknown' end
  local base=materialFact(c.player,c.quarter,c.materials[1],'base')
  if not base.known or not base.mapped or base.district>=0 or not base.revealed or not base.resource_visible then return nil,'base_not_credible' end
  local capture=base.owner==c.player
  if base.owner==-1 then local quote=quotes and quotes[c.materials[1]]
   capture=quote and quote.owner==-1 and quote.reach==true and quote.revealed==true and quote.in_range==true
    and type(quote.price)=='number'and quote.price>0 and quote.price==math.floor(quote.price)
    and type(quote.turn)=='number'and math.abs(Game.GetCurrentGameTurn()-quote.turn)<=1
  end
  if not capture then return nil,'base_capture_unknown_or_unavailable' end
  local option=base.working and base.improvement_type or futureOption(c.player,GameInfo.Resources[base.resource])
  if not option then return nil,'base_improvement_not_unlocked_or_unknown' end
  local source=assert(Map.GetPlotByIndex(c.source));local customer=customers(c.player,c.quarter,source,inv)
  return{working_base=base.working,existing_customer=#customer>0,base=base,customer=customer,
   future_customer='UNOBSERVED; no speculative CanHave API',
   development={improvement=option,status=base.working and'working'or'PROJECTION',
    legality='UNOBSERVED',Builder_commitment='UNOBSERVED',travel='UNOBSERVED',capture=base.owner==c.player and'owned'or'fresh_native_reach_and_quote'}}
 end
 screenAllowed=function(c,quotes,action)
  if screenMode()=='legacy'then return true end
  local state,inv,error=refresh(c.player,true)
  if not state or not inv or error then return false end
  local reason
  if screenMode()~='active'then reason=screenMode()
  elseif not originalAI(c.player)then reason='original_AI_unknown_or_human'
  elseif action=='foundation'and get('PENDING_'..c.player)then reason='pending_economic_reconciliation'
  else local allowed,why=slot(state,c);if not allowed then reason=why end end
  if not reason then reason=P.ScreenConflicts(c,state.records,inv.dependencies)end
  local fact
  if not reason then fact,reason=candidateFacts(c,inv,quotes)end
  if reason then decision(state,c.player,c,reason);return false end
  M.screenAdmission={site=keyOf(c),evidence=copy(fact)}
  return true
 end
 screenCommit=function(c,action,index,price)
  if screenMode()~='active'then return end
  local state=assert(Game:GetProperty(STATE));local site=keyOf(c);local record=state.records[site]
  if not record then local city=assert(CityManager.GetCity(c.player,c.city))
   record={player=c.player,city=c.city,quarter=c.quarter,source=c.source,city_x=city:GetX(),city_y=city:GetY(),
    first_turn=Game.GetCurrentGameTurn(),status='open',reason='request_issued',materials=copy(c.materials)};state.records[site]=record
  end
  if c.intent_version==2 then record.intent_version=2;record.v2_intent=copy(c.v2_intent)end
  record.materials=copy(c.materials);record.source_owned_once=record.source_owned_once or Map.GetPlotByIndex(c.source):GetOwner()==c.player
  if M.screenAdmission and M.screenAdmission.site==site then
   record.admission=copy(M.screenAdmission.evidence);record.first_admission=record.first_admission or copy(record.admission);M.screenAdmission=nil
  end
  record.last_request={turn=Game.GetCurrentGameTurn(),action=action,plot=index,quoted_price=price}
  decision(state,c.player,c,'request_issued')
 end
 function M.InspectPlannerV2(c)
  local result,error,packet=plannerCandidate(c,true)
  return{version=2,turn=Game.GetCurrentGameTurn(),result=copy(result),error=error,packet=copy(packet),action_authorization=false}
 end
 function M.InspectScreen(pid)
  local state,inv,error=refresh(pid,false);local rows={};local summary={open=0,operational=0,maintenance=0,failed_sunk=0,unknown=0,rehabilitated=0}
  if state then for site,record in pairs(state.records)do if record.player==pid then
   local row=copy(record);row.site=site;row.cost=get('SITE_COST_'..site,0);rows[#rows+1]=row
   summary[row.status]=summary[row.status]+1;if row.rehabilitated_turn then summary.rehabilitated=summary.rehabilitated+1 end
  end end end
  table.sort(rows,function(a,b)return a.site<b.site end)
  local diagnostics=state and type(state.planner_diagnostics)=='table'and copy(state.planner_diagnostics[tostring(pid)])or nil
  if plannerV2()and not diagnostics then diagnostics={evidence_error_count=0,initialization='no natural callbacks observed'}end
  return{version=1,planner_version=plannerV2()and 2 or 1,turn=Game.GetCurrentGameTurn(),player=pid,mode=screenMode(),config=copy(Game:GetProperty(CONFIG)),
   records=rows,summary=summary,error=error,last_decision=state and copy(state.decisions[tostring(pid)]),
   planner_diagnostics=diagnostics,
   last_planner_discovery=copy(M.v2Discovery and M.v2Discovery[tostring(pid)]),
   last_route_failure=state and type(state.route_failures)=='table'and copy(state.route_failures[tostring(pid)])or nil,
   operational_definition='owned functioning Quarter + working mapped Base + functioning upstream producer + owned adjacent actual Stage2 or matching registered Stage3 seller/customer path; structural not payment proof'}
 end
 screenProcess=function(pid)
  local state,inv,error=refresh(pid,true);if not state or not inv or error then return end
  if screenMode()~='active'or not originalAI(pid)then return end
  local plans={};local routeByCity={};local rejected={}
  if plannerV2()then M.v2Discovery=M.v2Discovery or{};M.v2Discovery[tostring(pid)]={turn=Game.GetCurrentGameTurn(),candidates=0,rejected=rejected,evidence_error_count=0,reason_kinds=0,active=true}end
  for _,city in Players[pid]:GetCities():Members()do
   local key,stamp,tiles=facts(city)
   for _,c in ipairs(catalog(city,key,stamp,tiles))do
    local allowed=slot(state,c)
    if allowed and not P.ScreenConflicts(c,state.records,inv.dependencies)and pcall(current,c,false)then
     local missing=false;for _,idx in ipairs((c.intent_version==2 and P.PlannerRequired(c)or{c.source,c.materials[1],c.materials[2]}))do if not tiles[idx]or tiles[idx].owner<0 then missing=true end end
     local quotes={};local route={};local price=0
     if missing then
      local cached=routeByCity[c.city]
      if not cached then cached={tiles={},quotes={}}
       for idx,t in pairs(tiles)do local item={owner=t.owner,neighbors=t.neighbors}
        if t.owner<0 then local quote=bridge().Read(pid,c.city,c.quarter,c.source,idx,false)
         cached.quotes[idx]=quote;item.price=quote and quote.price;item.reach=quote and quote.reach or false
        end
        cached.tiles[idx]=item
       end
       routeByCity[c.city]=cached
      end
      quotes=cached.quotes;route=P.Route(cached.tiles,(c.intent_version==2 and P.PlannerRequired(c)or{c.source,c.materials[1],c.materials[2]}))
      price=route and #route>0 and cached.tiles[route[1]].price or nil
     end
     if route and P.ScreenRouteQuotes(route,quotes)then local evidence,reason=candidateFacts(c,inv,quotes,false)
      if evidence then local candidate=copy(c);candidate.working_base=evidence.working_base;candidate.existing_customer=evidence.existing_customer
       candidate.fresh_price=price;candidate.route=route;candidate.screen_evidence=evidence;candidate.cache_key=key;plans[#plans+1]=candidate
      else rejected[reason]=(rejected[reason]or 0)+1 end
     else rejected.route_quote_unavailable=(rejected.route_quote_unavailable or 0)+1
     end
    end
   end
  end
  if plannerV2()then local discovery=M.v2Discovery[tostring(pid)];discovery.active=nil
   state.planner_diagnostics=state.planner_diagnostics or{};local previous=state.planner_diagnostics[tostring(pid)]or{evidence_error_count=0}
   previous.evidence_error_count=previous.evidence_error_count+discovery.evidence_error_count
   previous.first_error=previous.first_error or copy(discovery.first_error);previous.last_error=copy(discovery.last_error)or previous.last_error
   previous.first_packet=previous.first_packet or copy(discovery.first_packet);previous.first_candidate=previous.first_candidate or copy(discovery.first_candidate)
   previous.last_discovery=copy(discovery);state.planner_diagnostics[tostring(pid)]=previous
   Game:SetProperty(STATE,state)
  end
  table.sort(plans,function(a,b)
   if plannerV2()then return P.PlannerBetter(a,b)end
   if P.ScreenBetter(a,b)then return true end
   if P.ScreenBetter(b,a)then return false end
   if a.city~=b.city then return a.city<b.city end
   return a.quarter<b.quarter
  end)
  if #plans==0 then state.decisions[tostring(pid)]={turn=Game.GetCurrentGameTurn(),reason=plannerV2()and'no_admissible_customer_bound_plan'or'no_admissible_both_plan',rejected=rejected};Game:SetProperty(STATE,state)end
  for _,c in ipairs(plans)do
   if #c.route==0 then if M.Place(c)then M.cache[c.cache_key]=nil;return end
   elseif not get('PENDING_'..pid)and M.Acquire(c,c.route[1],c.route)then M.cache[c.cache_key]=nil;return end
  end
 end
end
local function ledger(pid,turn)
 local out={};for _,v in ipairs(get('BUYS_'..pid,{}))do if turn-v.turn<5 then out[#out+1]=v end end
 return out
end
local function closePurchase(pid,pending)
 assert(eligible(pid),'Economic owner became human or otherwise ineligible')
 assert(pending.status=='assignment_requested','Only reconcile an issued assignment')
 assert(Game.GetCurrentGameTurn()==pending.turn,'Do not debit a later-turn wallet')
 local owner,cityOwner,city=bridge().Owner(pending.plot)
 if Map.GetPlotByIndex(pending.plot):GetOwner()~=pid or owner~=pid or cityOwner~=pid or city~=pending.city then return false end
 local treasury=Players[pid]:GetTreasury();local f=pending.funding
 assert(treasury:GetGoldBalance()==f.gold+f.grant,'Wallet changed; no automatic economic replay')
 pending.status='debit_requested';put('PENDING_'..pid,pending)
 treasury:ChangeGoldBalance(-f.price)
 if bridge().Invalidate then bridge().Invalidate()end
 assert(treasury:GetGoldBalance()==f.gold+f.grant-f.price,'Exact debit failed')
 assert(treasury:GetGoldBalance()>=math.min(f.gold,f.reserve))
 pending.status='confirmed';pending.final_gold=treasury:GetGoldBalance()
 put('RECEIPT_'..pending.token,pending)
 indexReceipt('RECEIPT',pending.token)
 count('tiles',1);count('cost',f.price);count('own',f.own);count('subsidy',f.grant)
 put('SITE_COST_'..pending.site,get('SITE_COST_'..pending.site,0)+f.price)
 local buys=ledger(pid,pending.turn);buys[#buys+1]={turn=pending.turn,cost=f.price,own=f.own,donated=f.grant};put('BUYS_'..pid,buys)
 put('CITY_BUY_'..pid..':'..pending.city,pending.turn)
 put('PENDING_'..pid,nil)
 return true
end
function M.Reconcile()
 if M.busy or not supported()or not bridge()then return end
 M.busy=true
 for _,p in ipairs(PlayerManager.GetAliveMajors())do local pid=p:GetID();local pending=get('PENDING_'..pid)
  if eligible(pid)and pending and pending.status=='assignment_requested' and pending.turn==Game.GetCurrentGameTurn()then
   guarded(pid,function()closePurchase(pid,pending)end)
  end
 end
 M.busy=false
end
function M.Acquire(c,index,route)
 if not supported()then return false end
 if not pilotAllowed(c)then return false end
 local pid=c.player;local turn=Game.GetCurrentGameTurn()
 if get('PENDING_'..pid)or #ledger(pid,turn)>=3 or get('CITY_BUY_'..pid..':'..c.city)==turn then return false end
 local city
 if c.intent_version==2 then local ok;ok,city=pcall(current,c);if not ok then return false end else city=current(c)end
 local U=bridge();local q=U.Read(pid,c.city,c.quarter,c.source,index,false)
 if not q or not q.revealed or not q.in_range or not q.reach or q.owner~=-1 or not q.potential or not q.can_produce or q.same_type or math.abs(q.turn-turn)>1 then return false end
 local tr=Players[pid]:GetTreasury();local gold=tr:GetGoldBalance()
 if q.gold~=gold then return false end
 local gross,upkeep=tr:GetGoldYield(),tr:GetTotalMaintenance()
 local spent=get('SITE_COST_'..keyOf(c),0)
 local rolling=0;for _,buy in ipairs(ledger(pid,turn))do rolling=rolling+buy.cost end
 local f=P.Funding(q.price,gold,gross,upkeep,P.Enabled(GameConfiguration.GetValue('CSC_AI_SUBSIDIES'),true),math.max(spent,rolling))
 if not f then return false end
 if not WorldBuilder or type(WorldBuilder.CityManager)~='function'then return false end
 local manager=WorldBuilder.CityManager();if not manager or type(manager.SetPlotOwner)~='function'then return false end
 -- All route/source/material ownership is rechecked before granting anything.
 local allowed,routeFacts={},{};for _,idx in ipairs(route)do local p=Map.GetPlotByIndex(idx)
  if screenMode()~='legacy'then local owner=p and p:GetOwner()
   if owner~=-1 then return screenRefuse(c,idx,'gameplay_owner',nil,owner)end
  end
  assert(p:GetOwner()==-1)
  local fact=U.Read(pid,c.city,c.quarter,c.source,idx,false)
  if screenMode()~='legacy'then
   local predicate=not fact and'quote_unavailable'or(not fact.revealed and'ui_revealed'or(not fact.in_range and'ui_in_range'or(fact.owner~=-1 and'ui_owner')))
   if predicate then return screenRefuse(c,idx,predicate,fact,p:GetOwner())end
  end
  assert(fact.revealed and fact.in_range and fact.owner==-1,'Route ownership/reveal/range changed')
  routeFacts[idx]=fact
  allowed[idx]=true
 end
 assert(allowed[index])
 for _,idx in ipairs((c.intent_version==2 and P.PlannerRequired(c)or{c.source,c.materials[1],c.materials[2]}))do assert(Map.GetPlotByIndex(idx):GetOwner()==pid or allowed[idx])end
 local token=turn..':'..keyOf(c)..':'..index
 assert(not get('RECEIPT_'..token),'Closed economic token')
 if not screenAllowed(c,routeFacts,'acquire')then return false end
 screenCommit(c,'acquire',index,f.price)
 local pending={token=token,turn=turn,city=c.city,plot=index,site=keyOf(c),funding=f,status='grant_requested',backend='quoted_gold_assisted_assignment'}
 put('PENDING_'..pid,pending)
 if f.grant>0 then tr:ChangeGoldBalance(f.grant)end
 assert(tr:GetGoldBalance()==gold+f.grant,'Fallback grant failed')
 pending.status='assignment_requested';put('PENDING_'..pid,pending)
 local tile=Map.GetPlotByIndex(index);manager:SetPlotOwner(tile:GetX(),tile:GetY(),pid,c.city)
 if U.Invalidate then U.Invalidate()end
 closePurchase(pid,pending) -- A stale UI owner leaves an explicit pending ledger.
 return true
end
function M.Place(c)
 if not supported()then return false end
 if not pilotAllowed(c)then return false end
 local key=keyOf(c);if get('FOUNDATION_'..key)then return false end
 local city,source,def
 if c.intent_version==2 then local ok;ok,city,source,def=pcall(current,c);if not ok then return false end else city,source,def=current(c)end
 local pid=c.player
 for _,idx in ipairs((c.intent_version==2 and P.PlannerRequired(c)or{c.source,c.materials[1],c.materials[2]}))do if Map.GetPlotByIndex(idx):GetOwner()~=pid then return false end end
 local before=bridge().Read(pid,c.city,c.quarter,c.source,c.source,true)
 if not before or not before.legal or not before.can_produce or before.same_type or before.placed or before.city~=c.city or before.progress~=0 or type(before.cost)~='number' or before.cost<=0 then return false end
 if not screenAllowed(c,{},'foundation')then return false end
 screenCommit(c,'foundation',c.source,0)
 local pending={status='requested',turn=Game.GetCurrentGameTurn(),source=c.source,quarter=c.quarter,before=before}
 put('FOUNDATION_'..key,pending)
 indexReceipt('FOUNDATION',key)
 local pilot=Game:GetProperty(PILOT_STATE)
 if Game:GetProperty(PILOT)~=nil and pilot then pilotStatus(pilot,'observing','foundation_requested')end
 city:GetBuildQueue():CreateIncompleteDistrict(def.Index,c.source,0)
 if bridge().Invalidate then bridge().Invalidate()end
 local district=city:GetDistricts():GetDistrictAtLocation(source:GetX(),source:GetY())
 assert(district and district:GetType()==def.Index and not district:IsComplete(),'Native incomplete foundation missing')
 local after=bridge().Read(pid,c.city,c.quarter,c.source,c.source,true)
 assert(after,'UI foundation readback unavailable; requested ledger retained')
 assert(after.placed and after.progress==0 and after.cost==before.cost and equal(before.queue,after.queue),'Foundation production parity failed')
 pending.status='confirmed';pending.after=after;put('FOUNDATION_'..key,pending)
 count('foundations',1)
 return true
end
local function process(pid)
 local config=Game:GetProperty(PILOT)
 if config==nil and Game:GetProperty(PILOT_STATE)~=nil then pilotAllowed({});return end
 if config~=nil then
  local target=P.PilotPlan(config,Game.GetCurrentGameTurn())
  if not target then pilotAllowed({});return end
  if target.player~=pid or not pilotAllowed(target)then return end
  -- Reuse the normal route/funding/native one-shot owner with one fixed plan.
  -- Native turns may develop the Spec; there is no automatic target replacement.
  local city=CityManager.GetCity(pid,target.city);local key,_,tiles=facts(city)
  local missing=false
  for _,idx in ipairs({target.source,target.materials[1],target.materials[2]})do if not tiles[idx]or tiles[idx].owner<0 then missing=true end end
  if not missing then if M.Place(target)then M.cache[key]=nil end
  elseif not get('PENDING_'..pid)then
   local routeTiles={}
   for idx,t in pairs(tiles)do local item={owner=t.owner,neighbors=t.neighbors}
    if t.owner<0 then local f=bridge().Read(pid,target.city,target.quarter,target.source,idx,false);item.price=f and f.price;item.reach=f and f.reach or false end
    routeTiles[idx]=item
   end
   local route=P.Route(routeTiles,{target.source,target.materials[1],target.materials[2]})
   if route and #route>0 and M.Acquire(target,route[1],route)then M.cache[key]=nil end
  end
  return
 end
 if screenMode()~='legacy'then screenProcess(pid);return end
 local cities={};for _,city in Players[pid]:GetCities():Members()do cities[#cities+1]=city end
 table.sort(cities,function(a,b)return a:GetID()<b:GetID()end)
 for _,city in ipairs(cities)do
  local key,stamp,tiles=facts(city);local plans=catalog(city,key,stamp,tiles)
  for _,c in ipairs(plans)do
   local valid=pcall(current,c)
   if valid then
    local missing=false;for _,idx in ipairs((c.intent_version==2 and P.PlannerRequired(c)or{c.source,c.materials[1],c.materials[2]}))do if not tiles[idx]or tiles[idx].owner<0 then missing=true end end
    if not missing then
     if M.Place(c)then M.cache[key]=nil;break end
    elseif not get('PENDING_'..pid)then
     -- Only refresh quotes for a marked opportunity, not every map candidate.
     local routeTiles={}
     for idx,t in pairs(tiles)do
      local copy={owner=t.owner,neighbors=t.neighbors}
      if t.owner<0 then local q=bridge().Read(pid,c.city,c.quarter,c.source,idx,false);copy.price=q and q.price;copy.reach=q and q.reach or false end
      routeTiles[idx]=copy
     end
     local route=P.Route(routeTiles,(c.intent_version==2 and P.PlannerRequired(c)or{c.source,c.materials[1],c.materials[2]}))
     if route and #route>0 and M.Acquire(c,route[1],route)then M.cache[key]=nil;break end
    end
   end
  end
 end
end
local function UIReady(pid)
 local ui=bridge();if not ui or type(ui.HasCity)~='function'then return false end
 for _,city in Players[pid]:GetCities():Members()do if not ui.HasCity(pid,city:GetID())then return false end end
 return true
end
function M.TryQueued()
 if M.busy or not supported()then return end
 local ids={};for pid in pairs(M.queued)do ids[#ids+1]=pid end;table.sort(ids)
 for _,pid in ipairs(ids)do
  local turn=Game.GetCurrentGameTurn()
  if not eligible(pid)or get('TURN_'..pid)==turn then M.queued[pid]=nil
  elseif UIReady(pid)then
   -- The UI now knows the city. Re-evaluate current facts, never a historical
   -- opportunity or wallet. One attempted cycle per current native turn.
   put('TURN_'..pid,turn);M.busy=true
   if bridge().BeginScope then bridge().BeginScope()end
   local ok=guarded(pid,function()process(pid)end)
   if bridge().EndScope then bridge().EndScope()end
   M.busy=false;M.queued[pid]=nil
   if ok then put('ERROR_'..pid,nil)end
  end
 end
end
function M.OnPlayerTurn(pid)
 if not eligible(pid)or not supported()then return end
 M.queued[pid]=Game.GetCurrentGameTurn()
 M.TryQueued()
end
Events.PlayerTurnActivated.Add(M.OnPlayerTurn)
