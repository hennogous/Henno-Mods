-- UI provides native legality, prices and production readbacks. It never issues
-- a purchase command, switches player roles, grants Gold or edits ownership.
-- Resolve reusable modules while this UI chunk owns include's context. A later
-- ExposedMembers call must use these UI-owned captures, not lazy module imports
-- or a caller context's global table. Rule initialization remains deferred.
local plannerAdjacency,plannerPolicy
local plannerImportErrors={}
do
 local ok,error=pcall(include,'CSC_AdjacencyCore')
 if not ok then plannerImportErrors.adjacency=tostring(error):sub(1,300)end
 plannerAdjacency=CSC_Adjacency
 ok,error=pcall(include,'CSC_AI_OpportunityPolicy')
 if not ok then plannerImportErrors.policy=tostring(error):sub(1,300)end
 plannerPolicy=CSC_AI_CustomerPlannerV2
end
ExposedMembers.CSC_AI_AssistanceUI={version=1}
local U=ExposedMembers.CSC_AI_AssistanceUI
-- Presence/capability evidence only; no rule initialization, natural candidate,
-- ownership/order/property write or automatic re-import is performed here.
function U.PlannerBootstrap()
 return{version=2,phase='UI_chunk',adjacency_type=type(plannerAdjacency),policy_type=type(plannerPolicy),policy_version=type(plannerPolicy)=='table'and plannerPolicy.version or nil,adjacency_loaded=type(plannerAdjacency)=='table',policy_loaded=type(plannerPolicy)=='table',
  adjacency_initialize=type(plannerAdjacency)=='table'and type(plannerAdjacency.Initialize)=='function',
  adjacency_resource_visible=type(plannerAdjacency)=='table'and type(plannerAdjacency.ResourceVisible)=='function',
  adjacency_count=type(plannerAdjacency)=='table'and type(plannerAdjacency.Count)=='function',
  adjacency_eligible=type(plannerAdjacency)=='table'and type(plannerAdjacency.Eligible)=='function',
  adjacency_amount=type(plannerAdjacency)=='table'and type(plannerAdjacency.Amount)=='function',
  adjacency_bounds=type(plannerAdjacency)=='table'and type(plannerAdjacency.Bounds)=='function',
  policy_project=type(plannerPolicy)=='table'and type(plannerPolicy.Project)=='function',
  policy_revalidate=type(plannerPolicy)=='table'and type(plannerPolicy.Revalidate)=='function',
  policy_evaluate=type(plannerPolicy)=='table'and type(plannerPolicy.Evaluate)=='function',
  rules_initialized=U.plannerCoreReady==true,adjacency_import_error=plannerImportErrors.adjacency,policy_import_error=plannerImportErrors.policy}
end
-- Capture configured human identities before autoplay can temporarily flip
-- those flags. Gameplay persists this read-only snapshot for later reloads.
local initialHumans={}
for pid=0,63 do local configured=PlayerConfigurations and PlayerConfigurations[pid]
 if configured and type(configured.IsHuman)=='function'and configured:IsHuman()then initialHumans[tostring(pid)]=true end
end
function U.InitialHumanPlayers()local copy={};for id,v in pairs(initialHumans)do copy[id]=v end;return copy end
function U.HasCity(pid,cid)local c=CityManager.GetCity(pid,cid);return c~=nil end
-- These getters are available in UI, not uniformly in Gameplay. The gameplay
-- owner calls this read-only bridge before any economic or foundation action.
function U.SupportsEconomics()
 return type(GameConfiguration.IsAnyMultiplayer)=='function'and not GameConfiguration.IsAnyMultiplayer()
  and type(GameConfiguration.IsHotseat)=='function'and not GameConfiguration.IsHotseat()
end
function U.IsAIPlayer(pid)
 local p=Players[pid];local configured=PlayerConfigurations and PlayerConfigurations[pid]
 return not initialHumans[tostring(pid)]and p and p:IsAlive()and p:IsMajor()and not p:IsHuman()
  and configured and type(configured.IsHuman)=='function'and not configured:IsHuman()
end
function U.BeginScope()U.scope={reach={},source={}}end
function U.EndScope()U.scope=nil end
function U.Invalidate()if U.scope then U.BeginScope()end end
local function queue(q)
 local out={size=q:GetSize(),hash=q:GetCurrentProductionTypeHash(),items={}}
 for i=0,out.size-1 do local row=q:GetAt(i);local copy={}
  if type(row)=='table'then for k,v in pairs(row)do
   if type(v)=='string'or type(v)=='number'or type(v)=='boolean'then copy[k]=v end
  end end
  out.items[#out.items+1]=copy
 end
 return out
end
function U.Read(pid,cid,key,source,index,exact)
 local c=CityManager.GetCity(pid,cid);if not c then return nil,'UI city not published' end;local p=assert(Players[pid])
 assert(c:GetOwner()==pid and p:IsAlive()and p:IsMajor()and not p:IsHuman())
 local configured=PlayerConfigurations and PlayerConfigurations[pid]
 assert(not(configured and configured.IsHuman and configured:IsHuman()),'Configured human is not an AI assistance target')
 local d=assert(GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER'])
 local s=assert(Map.GetPlotByIndex(source));local t=assert(Map.GetPlotByIndex(index));local q=c:GetBuildQueue()
 -- Cache native target enumeration only within one synchronous AI callback.
 -- Every Gold/price/owner read stays fresh. CSC mutations invalidate the cache;
 -- exact before/after foundation checks always bypass cached source facts.
 local cityKey=pid..':'..cid;local sourceKey=cityKey..':'..key..':'..source
 local ready=not exact and U.scope and U.scope.source[sourceKey]or nil
 if not ready then
  local producible=q:CanProduce(d.Hash,false,true) -- Secondary native result can be a table.
  ready={can_produce=producible,potential=s:CanHaveDistrict(d.Index,pid,cid),same_type=c:GetDistricts():HasDistrict(d.Index)or q:HasBeenPlaced(d.Hash)}
  if not exact and U.scope then U.scope.source[sourceKey]=ready end
 end
 local reachable=U.scope and U.scope.reach[cityKey]or nil
 if not reachable then
  local args={};args[CityCommandTypes.PARAM_PLOT_PURCHASE]=true
  local visible,targets=CityManager.CanStartCommand(c,CityCommandTypes.PURCHASE,true,args,true)
  reachable={};for _,idx in ipairs(visible and targets and targets[CityCommandResults.PLOTS]or {})do reachable[idx]=true end
  if U.scope then U.scope.reach[cityKey]=reachable end
 end
 local pc=Cities.GetPlotPurchaseCity(t)
 local result={turn=Game.GetCurrentGameTurn(),owner=t:GetOwner(),city=pc and pc:GetID()or -1,
  price=c:GetGold():GetPlotPurchaseCost(index),gold=p:GetTreasury():GetGoldBalance(),reach=reachable[index]or false,
  revealed=PlayersVisibility[pid]:IsRevealed(t:GetX(),t:GetY()),
  in_range=Map.GetPlotDistance(c:GetX(),c:GetY(),t:GetX(),t:GetY())<=3,
  potential=ready.potential,can_produce=ready.can_produce,same_type=ready.same_type}
 if exact then
  local args={};args[CityOperationTypes.PARAM_DISTRICT_TYPE]=d.Hash
  local ops=CityManager.GetOperationTargets(c,CityOperationTypes.BUILD,args);local found=false
  for _,idx in ipairs(ops and ops[CityOperationResults.PLOTS]or {})do if idx==source then found=true end end
  args[CityOperationTypes.PARAM_X]=s:GetX();args[CityOperationTypes.PARAM_Y]=s:GetY()
  result.legal=found and CityManager.CanStartOperation(c,CityOperationTypes.BUILD,args,true)or false
  result.progress=q:GetDistrictProgress(d.Index);result.cost=q:GetDistrictCost(d.Index)
  result.queue=queue(q);result.placed=q:HasBeenPlaced(d.Hash)
 end
 return result
end
function U.Owner(index)
 local p=assert(Map.GetPlotByIndex(index));local c=Cities.GetPlotPurchaseCity(p)
 return p:GetOwner(),c and c:GetOwner()or -1,c and c:GetID()or -1
end
-- Only reconcile an already issued transaction here; normal opportunity planning
-- belongs to the AI-turn callback. A pending economic effect is never resent.
if Events.GameCoreEventPublishComplete then Events.GameCoreEventPublishComplete.Add(function()
 local host=ExposedMembers.CSC_AI_Assistance
 if host and host.Reconcile then host.Reconcile()end
 if host and host.TryQueued then host.TryQueued()end
end)end

-- V2 evidence bridge. All calls are reads; customer reservations live in the
-- Gameplay planner only. Unsupported evidence defers this candidate rather
-- than granting permission or silently replacing a native result with zero.
do
 local function clone(value)
  if type(value)~='table'then return value end
  local result={};for key,item in pairs(value)do result[key]=clone(item)end;return result
 end
 local function unlock(player,row)
  if not row or row.TraitType then return false end
  if row.PrereqTech then local t=GameInfo.Technologies[row.PrereqTech];if not t or not player:GetTechs():HasTech(t.Index)then return false end end
  if row.PrereqCivic then local c=GameInfo.Civics[row.PrereqCivic];if not c or not player:GetCulture():HasCivic(c.Index)then return false end end
  return true
 end
 local function variants(tableName,replacesName,name,key,replaced,unique)
  local out={};local rows=GameInfo[tableName];local row=rows and rows[name]
  if row then out[#out+1]=row end
  if GameInfo[replacesName]then for item in GameInfo[replacesName]()do
   if item[replaced]==name and rows[item[unique]]then out[#out+1]=rows[item[unique]]end
  end end
  table.sort(out,function(a,b)return a[key]<b[key]end);return out
 end
 local function buildings(name)return variants('Buildings','BuildingReplaces',name,'BuildingType','ReplacesBuildingType','CivUniqueBuildingType')end
 local function districts(name)return variants('Districts','DistrictReplaces',name,'DistrictType','ReplacesDistrictType','CivUniqueDistrictType')end
 local function rowsFor(key)
  if not GameInfo.CSC_QuarterFlowBuildings or not GameInfo.CSC_QuarterCustomerBuildings or not GameInfo.CSC_Stage3CustomerTransactions then return nil,'registry_unavailable'end
  local producers,paths={},{}
  for row in GameInfo.CSC_QuarterFlowBuildings()do if row.QuarterKey==key and row.Stage==2 then
   for _,b in ipairs(buildings(row.BuildingType))do producers[#producers+1]=b end
  end end
  table.sort(producers,function(a,b)return a.BuildingType<b.BuildingType end)
  for row in GameInfo.CSC_QuarterCustomerBuildings()do if row.QuarterKey==key and row.ProducerStage==2 then
   for _,producer in ipairs(producers)do paths[#paths+1]={stage=2,producer=producer,customer=row.BuildingType,district=row.DistrictType}end
  end end
  for row in GameInfo.CSC_Stage3CustomerTransactions()do if row.SellerDistrictType=='DISTRICT_CSC_'..key..'_QUARTER'then
   for _,producer in ipairs(buildings(row.SellerBuildingType))do paths[#paths+1]={stage=3,transaction=row.TransactionId,producer=producer,customer=row.CustomerBuildingType,district=row.CustomerDistrictType}end
  end end
  if #producers==0 or #paths==0 then return nil,'registry_definitions_missing'end
  return{producers=producers,paths=paths}
 end
 local function mapped(resource,key,role)
  for row in GameInfo.TypeTags()do if row.Type==resource and row.Tag=='CLASS_CSC_'..key..'_'..role then return true end end
  return false
 end
 local function material(A,pid,cid,key,source,index,role)
  local plot=Map.GetPlotByIndex(index);if not plot then return{plot=index,known=false}end
  local player=Players[pid];local r=GameInfo.Resources[plot:GetResourceType()]
  local imp=GameInfo.Improvements[plot:GetImprovementType()];local valid=false;local option
  if r and GameInfo.Improvement_ValidResources then for row in GameInfo.Improvement_ValidResources()do if row.ResourceType==r.ResourceType then
   local candidate=GameInfo.Improvements[row.ImprovementType]
   if imp and row.ImprovementType==imp.ImprovementType then valid=true end
   if candidate and unlock(player,candidate)and(not option or candidate.ImprovementType<option)then option=candidate.ImprovementType end
  end end end
  local out={plot=index,known=true,resource=plot:GetResourceType(),resource_type=r and r.ResourceType,
   owner=plot:GetOwner(),district=plot:GetDistrictType(),mapped=r and mapped(r.ResourceType,key,role)or false,
   revealed=PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY()),resource_visible=r and A.ResourceVisible(pid,plot:GetResourceType())or false,
   improvement=plot:GetImprovementType(),improvement_pillaged=plot:IsImprovementPillaged(),native_valid_improvement=valid,
   improvement_option=option,native_valid_option=option~=nil,improvement_unlocked=option~=nil}
  out.working=out.owner==pid and out.district<0 and out.mapped and out.revealed and out.resource_visible and valid and out.improvement_pillaged==false
  if out.owner==-1 then local quote=U.Read(pid,cid,key,source,index,false)
   out.capture_quote=quote and{turn=quote.turn,owner=quote.owner,reach=quote.reach,price=quote.price,revealed=quote.revealed,in_range=quote.in_range}
   if quote and quote.owner==-1 and quote.reach==true and quote.revealed and quote.in_range and type(quote.price)=='number'and quote.price>0 and quote.price==math.floor(quote.price)
    and math.abs(Game.GetCurrentGameTurn()-quote.turn)<=1 then out.capture='fresh_native_reach_and_quote'end
  end
  return out
 end
 -- Named source census is complete for this player's cities, including empty
 -- inventories. This is attachment multiplicity, not a boolean mill-presence cue.
 local function census(A,pid,districtType)
  local wanted={};for _,rule in ipairs(A.ByDistrict[districtType]or{})do
   if rule.ModifierOwner=='BuildingModifiers'and rule.WhoIsTheOwner then wanted[rule.WhoIsTheOwner]=true end
  end
  local cities,inventories={},{}
  for _,city in Players[pid]:GetCities():Members()do local id=city:GetID();cities[id]=true;inventories[id]={};local b=city:GetBuildings()
   for name in pairs(wanted)do local definition=GameInfo.Buildings[name]
    if not definition then error('source_building_definition_unavailable:'..name)end
    if b:HasBuilding(definition.Index)then inventories[id][name]=b:IsPillaged(definition.Index)end
   end
  end
  return cities,inventories
 end
 local function preview(A,plot,city,pid,districtType)
  local out={rules={}}
  for _,rule in ipairs(A.ByDistrict[districtType]or{})do if rule.ProvideType=='SelfBonus'and(rule.YieldType=='YIELD_PRODUCTION'or rule.YieldType=='YIELD_GOLD')then
   local row={};for k,v in pairs(rule)do if type(v)~='table'and type(v)~='userdata'and type(v)~='function'then row[k]=v end end
   row.eligible=A.Eligible(rule,city,pid);row.count=A.Count(rule,plot,city,pid);row.computed_amount=A.Amount(rule,row.count);out.rules[#out.rules+1]=row
  end end
  return out
 end
 -- Exact currently selected unlocks may support a named future construction
 -- branch. No unselected tech/civic tree or estimated completion date is credited.
 -- Failure text describes facts already read by this predicate. It must not
 -- add calls, change eligibility, or turn unknown active research into absence.
 local function plannedUnlock(player,row)
  if not row then return false,nil,'definition_unavailable'end
  if row.TraitType then return false,nil,'trait_recipient_unverified:'..row.TraitType end
  local pending={}
  if row.PrereqTech then local tech=GameInfo.Technologies[row.PrereqTech]
   if not tech then return false,nil,'technology_definition_unavailable:'..row.PrereqTech end
   local owner=player:GetTechs()
   if not owner:HasTech(tech.Index)then
    if type(owner.GetResearchingTech)~='function'then return false,nil,'active_technology_unavailable:'..row.PrereqTech end
    local active=owner:GetResearchingTech()
    if active~=tech.Index then local known=type(active)=='number'and active==active and active>=-1 and active<math.huge and active==math.floor(active);return false,nil,(known and'technology_not_owned_or_selected:'or'active_technology_unknown:')..row.PrereqTech end
    pending[#pending+1]={kind='technology',type=row.PrereqTech,status='currently_researching; no completion date assumed'}
   end
  end
  if row.PrereqCivic then local civic=GameInfo.Civics[row.PrereqCivic]
   if not civic then return false,nil,'civic_definition_unavailable:'..row.PrereqCivic end
   local owner=player:GetCulture()
   if not owner:HasCivic(civic.Index)then
    if type(owner.GetProgressingCivic)~='function'then return false,nil,'active_civic_unavailable:'..row.PrereqCivic end
    local active=owner:GetProgressingCivic()
    if active~=civic.Index then local known=type(active)=='number'and active==active and active>=-1 and active<math.huge and active==math.floor(active);return false,nil,(known and'civic_not_owned_or_selected:'or'active_civic_unknown:')..row.PrereqCivic end
    pending[#pending+1]={kind='civic',type=row.PrereqCivic,status='currently_progressing; no completion date assumed'}
   end
  end
  return true,pending
 end
 local function planBuilding(city,pid,row,planned,steps,visiting,depth)
  if not row then return nil,nil,'building_definition_unavailable'end
  if depth>8 then return nil,nil,'prerequisite_depth_limit:'..row.BuildingType end
  if visiting[row.BuildingType]then return nil,nil,'prerequisite_cycle:'..row.BuildingType end
  local name=row.BuildingType;local owned=city:GetBuildings()
  if planned[name]or(owned:HasBuilding(row.Index)and owned:IsPillaged(row.Index)==false)then return planned,steps end
  local unlocked,pending,failure=plannedUnlock(Players[pid],row);if not unlocked then return nil,nil,name..'/'..failure end
  if not GameInfo.BuildingPrereqs or not GameInfo.MutuallyExclusiveBuildings then return nil,nil,'building_prerequisite_registry_unavailable:'..name end
  for pair in GameInfo.MutuallyExclusiveBuildings()do if pair.Building==name then local other=GameInfo.Buildings[pair.MutuallyExclusiveBuilding]
   if planned[pair.MutuallyExclusiveBuilding]or(other and owned:HasBuilding(other.Index))then return nil,nil,'mutually_exclusive_building:'..name..'/'..pair.MutuallyExclusiveBuilding end
  end end
  visiting=clone(visiting);visiting[name]=true
  local prerequisites={}
  for pair in GameInfo.BuildingPrereqs()do if pair.Building==name then prerequisites[#prerequisites+1]=pair.PrereqBuilding end end
  table.sort(prerequisites)
  if #prerequisites>0 then local accepted,firstFailure
   for _,prerequisite in ipairs(prerequisites)do
    local nextPlan,nextSteps,failed=planBuilding(city,pid,GameInfo.Buildings[prerequisite],clone(planned),clone(steps),visiting,depth+1)
    if nextPlan then planned,steps=nextPlan,nextSteps;accepted=true;break end
    firstFailure=firstFailure or('required_building:'..prerequisite..'/'..tostring(failed or'unknown'))
   end
   if not accepted then return nil,nil,firstFailure end
  end
  local repair=owned:HasBuilding(row.Index)and owned:IsPillaged(row.Index)==true
  planned[name]=true;steps[#steps+1]={kind=repair and'repair'or'building',type=name,city=city:GetID(),cost=not repair and row.Cost or nil,nominal_new_build_cost=row.Cost,repair_cost_unobserved=repair or nil,maintenance=row.Maintenance,unlock_conditions=pending,
   status='CONDITIONAL construction; production allocation/native future queue legality unobserved'}
  return planned,steps
 end
 local function futureProducer(city,pid,definition,path,source)
  local flags={};local flagSteps={}
  if path.producer.PrereqDistrict=='DISTRICT_CSC_BAKERS_QUARTER'then
   -- Exact CSC_Q_BAKERS DistrictModifier/requirement contract, not vanilla
   -- RequiresRiver columns: one site-derived flag will be granted by the game.
   local river='BUILDING_CSC_BAKERS_RIVER_ACCESS';local dry='BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'
   if not GameInfo.Buildings[river]or not GameInfo.Buildings[dry]or type(source.IsRiver)~='function'then return nil,nil,nil,{reason='site_flag_evidence_unavailable',attempts={}}end
   local name=source:IsRiver()and river or dry;flags[name]=true
   flagSteps[1]={kind='site_flag',type=name,source=source:GetIndex(),condition='CSC REQUIREMENT_PLOT_ADJACENT_TO_RIVER / inverse',status='CONDITIONAL engine grant after Quarter; no Lua grant'}
  end
  local failed={reason='producer_branches_unverified',scope='already attempted upstream branches; capped summaries, not an exhaustive future plan',attempts={},omitted=0}
  for _,row in ipairs(definition.producers)do
   local plan,steps,failure=planBuilding(city,pid,row,clone(flags),clone(flagSteps),{},0)
   if plan then
    plan,steps,failure=planBuilding(city,pid,path.producer,plan,steps,{},0)
    if plan then return row.BuildingType,plan,steps end
   end
   -- At most four already-attempted branch summaries; no prerequisite tree dump.
   if #failed.attempts<4 then failed.attempts[#failed.attempts+1]={upstream=row.BuildingType,producer=path.producer.BuildingType,cause=tostring(failure or'unknown'):sub(1,240)}else failed.omitted=failed.omitted+1 end
  end
  return nil,nil,nil,failed
 end
 local function quality(A,V,pid,city,source,definition,path,cities,inventories,currentPreview,selectedMaterials)
  local projected=clone(currentPreview);local projectedInventory=clone(inventories)
  local producer=path.producer;local upstream,planned,producerSteps,producerFailure=futureProducer(city,pid,definition,path,source)
  if not upstream then return nil,'producer_prerequisites_unverified',producerFailure end
  -- Future attachments are explicitly conditional. Only simple source ownership
  -- gates are lifted; trait/Only-restricted rules keep their captured eligibility.
  for name in pairs(planned)do projectedInventory[city:GetID()][name]=false end
  for _,rule in ipairs(projected.rules)do
   if rule.ModifierOwner=='BuildingModifiers'and planned[rule.WhoIsTheOwner]and not rule.TraitType and(rule.Only==nil or rule.Only=='Human&AI')
    and(rule.CollectionType=='COLLECTION_PLAYER_DISTRICTS'or rule.CollectionType=='COLLECTION_CITY_DISTRICTS')then rule.eligible=true end
   if rule.AdjacencyType=='FROM_RINGS_TYPETAG_RESOURCE'and(rule.MustOwn==1 or rule.MustOwn==true)then
    for _,material in ipairs(selectedMaterials)do if material.owner==-1 and material.capture=='fresh_native_reach_and_quote'and material.resource_type then
     local first,last=A.Bounds(rule)
     if first<=1 and last>=1 then for tag in GameInfo.TypeTags()do if tag.Type==material.resource_type and tag.Tag==rule.CustomAdjacentObject then
      rule.count=rule.count+1;rule.computed_amount=A.Amount(rule,rule.count);break
     end end end
    end end
   end
   if path.readiness=='future_plot'and(rule.AdjacencyType=='FROM_RINGS_TYPETAG_DISTRICT'or rule.AdjacencyType=='FROM_RINGS_CAO_DISTRICT')then
    local match=rule.CustomAdjacentObject==path.district
    if not match then for tag in GameInfo.TypeTags()do if tag.Type==path.district and tag.Tag==rule.CustomAdjacentObject then match=true;break end end end
    local first,last=A.Bounds(rule)
    if match and first<=1 and last>=1 then rule.count=rule.count+1;rule.computed_amount=A.Amount(rule,rule.count)end
   end
  end
  return{current=V.Project(currentPreview,city:GetID(),cities,inventories),projected=V.Project(projected,city:GetID(),cities,projectedInventory),
   assumptions={upstream_producer=upstream,path_producer=producer.BuildingType,customer_district=path.readiness=='future_plot'and path.district or nil,
    producer_steps=producerSteps,horizon='named prerequisites owned or currently selected research/civic; no dates or unselected tree credit',status='CONDITIONAL; no order, worker commitment, native future building queue legality or total native preview claimed'}}
 end
 local function exactFuture(city,pid,plot,district,quarter,sourceCityID)
  local q=city:GetBuildQueue();local ds=city:GetDistricts()
  local result={legal_plot=plot:CanHaveDistrict(district.Index,pid,city:GetID()),unlock_plausible=plannedUnlock(Players[pid],district),capacity_plausible=false,
   native_commitment=ds:HasDistrict(district.Index)or q:HasBeenPlaced(district.Hash),alternative_scores='UNAVAILABLE'}
  -- A plot-potential result does not imply current build permission. Counts include
  -- pending zoned districts in the shipped CitySupport contract.
  if district.RequiresPopulation==false or district.RequiresPopulation==0 then result.capacity_plausible=true;result.planned_Quarter_capacity=0
  elseif type(ds.GetNumZonedDistrictsRequiringPopulation)=='function'and type(ds.GetNumAllowedDistrictsRequiringPopulation)=='function'then
   result.capacity_used=ds:GetNumZonedDistrictsRequiringPopulation();result.capacity_allowed=ds:GetNumAllowedDistrictsRequiringPopulation()
   result.planned_Quarter_capacity=(city:GetID()==sourceCityID and(quarter.RequiresPopulation==true or quarter.RequiresPopulation==1))and 1 or 0
   result.capacity_plausible=result.capacity_used+result.planned_Quarter_capacity<result.capacity_allowed
  else result.capacity_unavailable=true end
  result.unlock_owned=unlock(Players[pid],district)
  result.can_produce=q:CanProduce(district.Hash,false,true)
  if result.legal_plot and result.can_produce and result.unlock_plausible and result.capacity_plausible and not result.native_commitment then
   local args={};args[CityOperationTypes.PARAM_DISTRICT_TYPE]=district.Hash
   local targets=CityManager.GetOperationTargets(city,CityOperationTypes.BUILD,args);local found=false
   for _,index in ipairs(targets and targets[CityOperationResults.PLOTS]or{})do if index==plot:GetIndex()then found=true end end
   args[CityOperationTypes.PARAM_X]=plot:GetX();args[CityOperationTypes.PARAM_Y]=plot:GetY()
   result.exact_target=found;result.exact_operation=found and CityManager.CanStartOperation(city,CityOperationTypes.BUILD,args,true)or false
  end
  result.potential=result.legal_plot;result.legal_plot=result.potential==true and result.can_produce==true and result.exact_target==true and result.exact_operation==true
  result.future_permission_conditional=false -- first pilot requires current exact district permission
  result.scope='potential + separate current unlock/capacity/CanProduce/exact native operation; false/unknown is deferred, not forever illegal'
  return result
 end
 -- Memoization exists only inside the already bounded UI callback scope.
 -- Fresh action admission bypasses it; CSC mutation calls U.Invalidate().
 local function scoped(name,key,fresh,fn)
  if fresh or not U.scope then return fn()end
  U.scope.plannerShared=U.scope.plannerShared or{};local memo=U.scope.plannerShared
  memo[name]=memo[name]or{};if memo[name][key]==nil then memo[name][key]=fn()end
  return memo[name][key]
 end
 local function read(pid,cid,key,sourceIndex,baseIndex,specIndex,originalAI,fresh)
  local A,V=plannerAdjacency,plannerPolicy
  if type(A)~='table'then return nil,'planner_UI_adjacency_module_unavailable'end
  if type(V)~='table'then return nil,'planner_UI_policy_module_unavailable'end
  for _,name in ipairs({'Initialize','ResourceVisible','Count','Eligible','Amount','Bounds'})do
   if type(A[name])~='function'then return nil,'planner_UI_adjacency_capability_unavailable:'..name end
  end
  for _,name in ipairs({'Project','Evaluate','Revalidate'})do
   if type(V[name])~='function'then return nil,'planner_UI_policy_capability_unavailable:'..name end
  end
  if not U.plannerCoreReady then A.Initialize();U.plannerCoreReady=true end
  local rules=A.ByDistrict['DISTRICT_CSC_'..key..'_QUARTER']
  if type(rules)~='table'or #rules==0 then return nil,'Quarter_adjacency_rules_unavailable'end
  local city=assert(CityManager.GetCity(pid,cid));local source=assert(Map.GetPlotByIndex(sourceIndex));local qdef=assert(GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER'])
  local definition=scoped('registry',key,fresh,function()return rowsFor(key)end);if not definition then return nil,'registry_unavailable_or_incomplete'end
  local initial=U.Read(pid,cid,key,sourceIndex,sourceIndex,false)
  local base=material(A,pid,cid,key,sourceIndex,baseIndex,'BASE')
  local spec=specIndex and material(A,pid,cid,key,sourceIndex,specIndex,'SPEC')or nil
  local packet={version=2,turn=Game.GetCurrentGameTurn(),value_scope='read-only estimated CSC real SelfBonus components at this capture; projected values conditional, not observed native total yield',identity={player=pid,city=cid,quarter=key,source=sourceIndex},original_AI=originalAI==true,
   source_legal=initial and initial.potential==true,source_can_produce=initial and initial.can_produce==true,source_conflict=not initial or initial.same_type~=false,
   base=base,spec=spec,materials={baseIndex,specIndex},customer_paths={},unknown_secondary_costs={'Builder availability and travel','customer construction opportunity cost','future prices and maintenance'},
   native_alternative_scores='UNAVAILABLE; no preferred native district plot claim',native_context_validation='PENDING bounded native preflight'}
  packet.both_credible=spec~=nil and spec.mapped and spec.revealed and spec.resource_visible and spec.district<0 and(spec.owner==pid or(spec.owner==-1 and spec.capture=='fresh_native_reach_and_quote'))or false
  local named=scoped('census',pid..':'..key,fresh,function()local cities,inventories=census(A,pid,qdef.DistrictType);return{cities,inventories}end)
  local cities,inventories=named[1],named[2]
  local currentPreview=scoped('preview',pid..':'..cid..':'..key..':'..sourceIndex,fresh,function()return preview(A,source,city,pid,qdef.DistrictType)end)
  packet.quality={current=V.Project(currentPreview,cid,cities,inventories)}
  -- UI collections use Members (shipped/accepted shadow capture). Gameplay's
  -- GetDistrictAtLocation is deliberately not called across this bridge.
  local byPlot=scoped('districts',pid,fresh,function()local byPlot={}
  for _,ownedCity in Players[pid]:GetCities():Members()do for _,d in ownedCity:GetDistricts():Members()do
   local plot=Map.GetPlot(d:GetX(),d:GetY());if plot then byPlot[plot:GetIndex()]={district=d,city=ownedCity}end
  end end;return byPlot end)
  local neighboring={};for direction=0,5 do local plot=Map.GetAdjacentPlot(source:GetX(),source:GetY(),direction);if plot then neighboring[#neighboring+1]=plot end end
  for _,path in ipairs(definition.paths)do for _,district in ipairs(districts(path.district))do for _,building in ipairs(buildings(path.customer))do
   for _,plot in ipairs(neighboring)do if plot:GetOwner()==pid then
    local existing=byPlot[plot:GetIndex()];local ownerCity=existing and existing.city or Cities.GetPlotPurchaseCity(plot);local actual=existing and existing.district
    local item={source='CSC runtime registries + read-only UI native facts',mapping_valid=true,stage=path.stage,transaction=path.transaction,
     producer=path.producer.BuildingType,district=district.DistrictType,building=building.BuildingType,plot=plot:GetIndex(),customer_city=ownerCity and ownerCity:GetID(),owned=true,adjacent=true,
     footprint_conflict=plot:GetIndex()==baseIndex or plot:GetIndex()==specIndex,producer_prereq_tech=path.producer.PrereqTech,producer_prereq_civic=path.producer.PrereqCivic,
     building_prereq_tech=building.PrereqTech,building_prereq_civic=building.PrereqCivic}
    if actual and actual:GetType()==district.Index then local b=ownerCity:GetBuildings()
     item.district_complete=actual:IsComplete();item.raw_district_pillaged=actual:IsPillaged()
     item.district_functioning=district.DistrictType=='DISTRICT_CITY_CENTER'or item.raw_district_pillaged==false
     item.building_present=b:HasBuilding(building.Index);item.building_functioning=item.building_present and b:IsPillaged(building.Index)==false
     item.readiness=item.building_present and'actual'or'existing_district'
     local plan,steps=planBuilding(ownerCity,pid,building,{}, {},{},0);item.unlock_plausible=plan~=nil;item.customer_construction_steps=steps
    elseif plot:GetDistrictType()<0 and plot:GetResourceType()<0 and plot:GetImprovementType()<0 and plot:GetFeatureType()<0 and ownerCity and ownerCity:GetOwner()==pid then
     item.readiness='future_plot';local native=scoped('future',pid..':'..ownerCity:GetID()..':'..plot:GetIndex()..':'..district.Index..':'..cid..':'..qdef.Index,fresh,function()return exactFuture(ownerCity,pid,plot,district,qdef,cid)end);for k,v in pairs(native)do item[k]=v end
     local plan,steps=planBuilding(ownerCity,pid,building,{}, {},{},0);item.unlock_plausible=item.unlock_plausible and plan~=nil;item.customer_construction_steps=steps
    end
    if item.readiness then
     item.quality,item.quality_error,item.producer_failure=quality(A,V,pid,city,source,definition,{producer=path.producer,readiness=item.readiness,district=item.district},cities,inventories,currentPreview,{base,spec})
     -- Missing producer prerequisites are essential even for Both: a concrete
     -- customer path is not credible when its named seller cannot be developed.
     if not item.quality then item.mapping_valid=false end
     packet.customer_paths[#packet.customer_paths+1]=item
    end
   end end
  end end end
  return packet
 end
 function U.ReadPlannerV2(pid,cid,key,source,base,spec,originalAI,fresh)
  local cacheKey=table.concat({pid,cid,key,source,base,spec or'-'},':')
  if not fresh and U.scope and U.scope.plannerV2 and U.scope.plannerV2[cacheKey]then return clone(U.scope.plannerV2[cacheKey])end
  local ok,packet,error=pcall(read,pid,cid,key,source,base,spec,originalAI,fresh)
  if not ok then return nil,'planner_evidence_unavailable:'..tostring(packet)end
  if not packet then return nil,error end
  if not fresh and U.scope then U.scope.plannerV2=U.scope.plannerV2 or{};U.scope.plannerV2[cacheKey]=clone(packet)end
  return packet
 end
end
