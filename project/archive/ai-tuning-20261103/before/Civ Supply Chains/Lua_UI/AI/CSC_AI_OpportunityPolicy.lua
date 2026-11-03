-- Deterministic shared policy for CSC's installed assistance host and Lua tests.
-- Prices on later route steps are ranking hints only. Each purchased step needs
-- a fresh native quote; unknown future prices never count as free land.
CSC_AI_OpportunityPolicy={version=1}
local P=CSC_AI_OpportunityPolicy
function P.Enabled(value,default)
 if value==nil then return default end
 return value==true or value==1 or value=='1'
end
function P.Funding(price,gold,gross,upkeep,subsidies,spent)
 if type(price)~='number' or price<=0 or price~=math.floor(price)
  or type(gold)~='number' or type(gross)~='number' or type(upkeep)~='number' then return nil end
 if price+spent>300 then return nil end
 local reserve=math.max(25,math.ceil(2*upkeep),math.ceil(10*math.max(0,upkeep-gross)))
 local own=math.min(price,math.floor(.8*math.max(0,gold-reserve)))
 if not subsidies and own<price then return nil end
 return {price=price,own=own,grant=price-own,reserve=reserve,gold=gold}
end
local function sortedKeys(t)local a={};for k in pairs(t)do a[#a+1]=k end;table.sort(a);return a end
local function less(a,b)
 if a.unknown~=b.unknown then return a.unknown<b.unknown end
 if a.cost~=b.cost then return a.cost<b.cost end
 if #a.steps~=#b.steps then return #a.steps<#b.steps end
 for i=1,#a.steps do if a.steps[i]~=b.steps[i]then return a.steps[i]<b.steps[i]end end
 return a.plot<b.plot
end
local function path(tiles,target,added)
 if tiles[target].owner>=0 or added[target]then return {}end
 local open,seen={},{}
 for _,idx in ipairs(sortedKeys(tiles))do
  if tiles[idx].owner>=0 or added[idx]then open[#open+1]={plot=idx,unknown=0,cost=0,steps={}}end
 end
 while #open>0 do
  table.sort(open,less);local v=table.remove(open,1)
  if not seen[v.plot]then
   seen[v.plot]=true;if v.plot==target then return v.steps end
   for _,idx in ipairs(tiles[v.plot].neighbors)do local t=tiles[idx]
    if t and not seen[idx]then
     local missing=t.owner<0 and not added[idx]
     if not missing or #v.steps>0 or next(added)~=nil or t.reach then
      local a={};for i,x in ipairs(v.steps)do a[i]=x end
      if missing then a[#a+1]=idx end
      open[#open+1]={plot=idx,steps=a,unknown=v.unknown+(missing and (not t.price or t.price<=0)and 1 or 0),cost=v.cost+(missing and math.max(0,t.price or 0)or 0)}
     end
    end
   end
  end
 end
end
function P.Route(tiles,required)
 local missing={};local requiredSet={}
 for _,idx in ipairs(required)do
  if not tiles[idx]then return nil end
  requiredSet[idx]=true
  if tiles[idx].owner<0 then missing[#missing+1]=idx end
 end
 if #missing==0 then return {}end
 if #missing>3 then return nil end
 table.sort(missing)
 local best
 local function permutation(prefix,left)
  if #left>0 then
   for i,idx in ipairs(left)do local rest={}
    for j,x in ipairs(left)do if i~=j then rest[#rest+1]=x end end
    local p={};for j,x in ipairs(prefix)do p[j]=x end;p[#p+1]=idx;permutation(p,rest)
   end
   return
  end
  local added,steps={},{}
  for _,idx in ipairs(prefix)do local route=path(tiles,idx,added);if not route then return end
   for _,x in ipairs(route)do if not added[x]then added[x]=true;steps[#steps+1]=x end end
  end
  local connectors=0;for idx in pairs(added)do if not requiredSet[idx]then connectors=connectors+1 end end
  if connectors>2 or #steps>5 or not tiles[steps[1]].reach or not tiles[steps[1]].price or tiles[steps[1]].price<=0 then return end
  local score={plot=steps[#steps],steps=steps,unknown=0,cost=0}
  for _,idx in ipairs(steps)do local t=tiles[idx];if not t.price or t.price<=0 then score.unknown=score.unknown+1 else score.cost=score.cost+t.price end end
  if not best or less(score,best)then best=score end
 end
 permutation({},missing);return best and best.steps or nil
end
function P.Better(a,b)
 if a.base~=b.base then return a.base>b.base end
 if a.spec~=b.spec then return a.spec>b.spec end
 if a.missing~=b.missing then return a.missing<b.missing end
 if a.source~=b.source then return a.source<b.source end
 if a.materials[1]~=b.materials[1]then return a.materials[1]<b.materials[1]end
 return a.materials[2]<b.materials[2]
end

-- A single reviewed Both-material experiment, never an autonomous selector.
-- Presence of any pilot property suppresses the normal host path. A review or
-- malformed value cannot arm a target; validation itself has no side effects.
function P.PilotPlan(config,turn)
 if type(config)~='table' or config.version~=1 then return nil,'invalid_config' end
 if config.status=='review' or config.review==true then return nil,'review' end
 local function integer(v,min)return type(v)=='number' and v<math.huge and v==math.floor(v) and v>=min end
 for _,key in ipairs({'player','city','source','city_x','city_y','start_turn','deadline_turn'})do
  if not integer(config[key],0)then return nil,'invalid_'..key end
 end
 if config.quarter~='BAKERS' and config.quarter~='TAILORS'then return nil,'unsupported_quarter' end
 if config.deadline_turn<config.start_turn or config.deadline_turn-config.start_turn>25 then return nil,'invalid_deadline' end
 if type(config.materials)~='table' or #config.materials~=2
  or type(config.material_resources)~='table' or #config.material_resources~=2 then return nil,'invalid_materials' end
 for i=1,2 do
  if not integer(config.materials[i],0)or not integer(config.material_resources[i],0)
   or config.materials[i]==config.source then return nil,'invalid_material_identity' end
 end
 if config.spec_policy~=nil and config.spec_policy~='ready' and config.spec_policy~='conditional'then return nil,'invalid_spec_policy' end
 if turn<config.start_turn then return nil,'not_started' end
 if turn>config.deadline_turn then return nil,'deadline' end
 return {player=config.player,city=config.city,quarter=config.quarter,source=config.source,
  materials={config.materials[1],config.materials[2]},base=1,spec=1},'armed'
end
function P.PilotMatches(config,c)
 return type(config)=='table' and type(c)=='table' and type(c.materials)=='table' and #c.materials==2
  and config.player==c.player and config.city==c.city and config.quarter==c.quarter
  and config.source==c.source and type(config.materials)=='table'
  and config.materials[1]==c.materials[1] and config.materials[2]==c.materials[2]
end

-- Experimental admission screen. Existing policy/backend functions above are
-- unchanged. A disappeared opt-in after activation must not erase commitments.
function P.ScreenMode(config,state)
 if config==nil then return state==nil and 'legacy' or 'missing_config' end
 if type(config)~='table'or(config.version~=1 and config.version~=2)then return 'invalid_config' end
 for key in pairs(config)do if key~='version'then return 'invalid_config' end end
 return 'active'
end
function P.ScreenStatus(record,facts)
 if record.status=='failed_sunk'then return 'failed_sunk',record.failed_reason or record.reason end
 if facts.irrecoverable then return 'failed_sunk',facts.irrecoverable end
 if not facts.known then return 'unknown',facts.reason or 'facts_unknown' end
 if facts.base_known and not facts.base_present then return 'failed_sunk','base_resource_gone_or_covered' end
 if facts.operational then return 'operational',facts.operational_stage==3 and 'structural_stage3_chain'or'structural_stage2_chain' end
 if record.first_operational_turn~=nil then return 'maintenance',facts.reason or 'structural_chain_degraded' end
 return 'open',facts.reason or 'developing_chain'
end
function P.ScreenConflicts(candidate,records,dependencies)
 if candidate.intent_version==2 then local reason=P.PlannerFootprintConflict(candidate,records,dependencies);if reason then return reason end end
 local site=candidate.player..':'..candidate.city..':'..candidate.quarter..':'..candidate.source
 for key,record in pairs(records)do
  if record.player==candidate.player then
   if record.source==candidate.source and record.status=='failed_sunk'then return 'failed_site_no_replay' end
   if key~=site and record.status~='failed_sunk'then
    for _,index in ipairs(record.materials or{})do if candidate.source==index then return 'source_over_committed_material' end end
    for _,index in ipairs(candidate.materials)do if index==record.source then return 'material_over_committed_source' end end
   end
  end
 end
 for _,dependency in ipairs(dependencies or{})do
  if dependency.source~=candidate.source then
   for _,index in ipairs(dependency.materials or{})do if candidate.source==index then return 'source_over_existing_chain_material' end end
   for _,index in ipairs(candidate.materials)do if index==dependency.source then return 'material_over_existing_chain_source' end end
  end
 end
 -- Material/material sharing can be compatible; it is not two independent
 -- economic benefits, and this screen assigns no benefit score to that reuse.
end
function P.ScreenBetter(a,b)
 if a.working_base~=b.working_base then return a.working_base end
 if a.existing_customer~=b.existing_customer then return a.existing_customer end
 if a.base~=b.base then return a.base>b.base end
 if a.spec~=b.spec then return a.spec>b.spec end
 local ac,bc=type(a.fresh_price)=='number',type(b.fresh_price)=='number'
 if ac~=bc then return ac end
 if ac and a.fresh_price~=b.fresh_price then return a.fresh_price<b.fresh_price end
 return P.Better(a,b)
end

-- Screen planning may leave future reach/prices unknown. Every proposed future
-- purchase must still have the existing owner/reveal/hard city-range facts.
function P.ScreenRouteQuotes(route,quotes)
 for _,index in ipairs(route)do local quote=quotes[index]
  if not(quote and quote.revealed and quote.in_range and quote.owner==-1)then return false end
 end
 return true
end

function P.PlannerRequired(c)
 local required={c.source};for _,index in ipairs(c.materials)do required[#required+1]=index end;return required
end
-- Typed v2 wrappers do not change the legacy comparator or Both contract.
function P.PlannerBetter(a,b)
 local ae,be=a.v2_evidence or{},b.v2_evidence or{}
 local ar,br=ae.customer and ae.customer.readiness_rank or 0,be.customer and be.customer.readiness_rank or 0
 if a.working_base~=nil then ae={base={working=a.working_base}}end
 if b.working_base~=nil then be={base={working=b.working_base}}end
 local aw,bw=ae.base and ae.base.working==true or false,be.base and be.base.working==true or false
 if aw~=bw then return aw end
 if ar~=br then return ar>br end
 for _,field in ipairs({'base','spec'})do if a[field]~=b[field]then return a[field]>b[field]end end
 local ac,bc=type(a.fresh_price)=='number',type(b.fresh_price)=='number'
 if ac~=bc then return ac end
 if ac and a.fresh_price~=b.fresh_price then return a.fresh_price<b.fresh_price end
 for _,field in ipairs({'city','source','quarter'})do if a[field]~=b[field]then return a[field]<b[field]end end
 for i=1,math.max(#a.materials,#b.materials)do local av,bv=a.materials[i]or -1,b.materials[i]or -1;if av~=bv then return av<bv end end
 return false
end
function P.ValidPlannerIntent(intent,record)
 if type(intent)~='table'or intent.version~=2 or type(intent.identity)~='table'or type(intent.materials)~='table'or type(intent.customer)~='table'then return false end
 local count=intent.kind=='both'and 2 or(intent.kind=='base_only_real4'and 1 or 0)
 if count==0 or #record.materials~=count or #intent.materials~=count then return false end
 for _,field in ipairs({'player','city','source','quarter'})do if intent.identity[field]~=record[field]then return false end end
 for i,index in ipairs(record.materials)do if intent.materials[i]~=index then return false end end
 if intent.base_plot~=record.materials[1]or type(intent.base_resource)~='number'then return false end
 if count==2 and(intent.spec_plot~=record.materials[2]or type(intent.spec_resource)~='number')then return false end
 local customer=intent.customer
 if(customer.stage~=2 and customer.stage~=3)or type(customer.plot)~='number'or customer.plot<0 or customer.plot~=math.floor(customer.plot)then return false end
 for _,key in ipairs({'producer','district','building'})do if type(customer[key])~='string'or customer[key]==''then return false end end
 return customer.stage~=3 or type(customer.transaction)=='string'
end
function P.PlannerFootprintConflict(candidate,records,dependencies)
 local customer=candidate.v2_intent and candidate.v2_intent.customer
 if not customer then return 'typed_customer_missing'end
 local plot=customer.plot
 if plot==candidate.source then return 'customer_over_Quarter_source'end
 for _,index in ipairs(candidate.materials)do if plot==index then return 'customer_over_selected_material'end end
 for _,dependency in ipairs(dependencies or{})do
  for _,index in ipairs(dependency.materials or{})do if plot==index then return 'customer_over_existing_supply'end end
  if dependency.source==plot then return 'customer_over_existing_Quarter'end
 end
 local site=candidate.player..':'..candidate.city..':'..candidate.quarter..':'..candidate.source
 for key,record in pairs(records)do if record.player==candidate.player and key~=site and record.status~='failed_sunk'then
  local reserved=record.v2_intent and record.v2_intent.customer
  if record.source==plot then return 'customer_over_committed_source'end
  for _,index in ipairs(record.materials or{})do if index==plot then return 'customer_over_committed_supply'end end
  if reserved and reserved.readiness=='future_plot'and(record.status=='open'or record.status=='unknown'or record.status=='maintenance')then
   if reserved.plot==candidate.source then return 'source_over_reserved_customer'end
   for _,index in ipairs(candidate.materials)do if index==reserved.plot then return 'material_over_reserved_customer'end end
   if reserved.plot==plot then return 'conflicting_future_customer_reservation'end
  end
 end end
end

-- Pure customer-aware v2 policy and attachment-instance real-component model.
-- No native calls or mutation. Host/UI adapter supplies fresh sourced evidence.
CSC_AI_CustomerPlannerV2={version=2}
local V=CSC_AI_CustomerPlannerV2
local Y={'YIELD_PRODUCTION','YIELD_GOLD'}
local function number(x)return type(x)=='number'and x==x and x>-math.huge and x<math.huge end
local function copy(x)if type(x)~='table'then return x end;local out={};for k,v in pairs(x)do out[k]=copy(v)end;return out end
function V.Mode(config)
 if config==nil then return 'legacy'end
 if type(config)~='table'or config.version~=2 then return 'paused'end
 for key in pairs(config)do if key~='version'then return 'paused'end end
 return 'v2'
end
-- Port of durable shadow_projection.project/source_instances. Counts actual
-- unpillaged source-building ATTACHMENTS, not boolean empire source presence.
-- Rule amounts must already be encoded once per source by CSC_Adjacency.Amount.
function V.Project(preview,city,cities,inventories)
 local totals={YIELD_PRODUCTION=0,YIELD_GOLD=0};local details,gaps={},{}
 for _,r in ipairs(preview.rules or{})do if r.ProvideType=='SelfBonus'and(r.YieldType==Y[1]or r.YieldType==Y[2])then
  local missing={};local count
  if(r.ModifierOwner or'DistrictModifiers')~='BuildingModifiers'then
   if type(r.eligible)=='boolean'then count=r.eligible and 1 or 0 else missing[#missing+1]='eligibility unavailable'end
  else
   local selected={}
   if r.CollectionType=='COLLECTION_CITY_DISTRICTS'then selected={city}
   elseif r.CollectionType=='COLLECTION_PLAYER_DISTRICTS'then for id in pairs(cities)do selected[#selected+1]=id end;table.sort(selected)
   else missing[#missing+1]='unsupported building collection '..tostring(r.CollectionType)end
   count=0
   for _,id in ipairs(selected)do local inventory=inventories[id]
    if inventory==nil then missing[#missing+1]='missing named building census city '..id
    elseif inventory[r.WhoIsTheOwner]~=nil then local pillaged=inventory[r.WhoIsTheOwner]
     if pillaged==false then count=count+1 elseif pillaged~=true then missing[#missing+1]='unknown source pillage state city '..id end
    end
   end
   if r.CollectionType=='COLLECTION_CITY_DISTRICTS'or r.CollectionType=='COLLECTION_PLAYER_DISTRICTS'then
    if r.eligible==false then count=0;missing={}elseif r.eligible~=true then missing[#missing+1]='eligibility unavailable'end
   end
  end
  if not number(r.computed_amount)then missing[#missing+1]='unknown encoded amount'end
  local contribution=#missing==0 and count~=nil and r.computed_amount*count or nil
  details[#details+1]={rule=r.ID,yield_type=r.YieldType,encoded_per_source=r.computed_amount,active_source_instances=#missing==0 and count or nil,contribution=contribution,gaps=missing}
  if contribution==nil then totals[r.YieldType]=nil;for _,issue in ipairs(missing)do gaps[#gaps+1]=tostring(r.ID)..': '..issue end
  elseif totals[r.YieldType]~=nil then totals[r.YieldType]=totals[r.YieldType]+contribution end
 end end
 return{real=totals,rules=details,gaps=gaps,scope='estimated CSC SelfBonus components only; not a validated total unbuilt native getter'}
end
local function credibleBase(base,pid)
 if type(base)~='table'or base.mapped~=true or base.revealed~=true or base.resource_visible~=true or not number(base.district)or base.district>=0 then return false,'no_credible_mapped_Base'end
 if base.owner~=pid and(base.owner~=-1 or base.capture~='fresh_native_reach_and_quote')then return false,'Base_capture_unverified'end
 if base.working~=true and(not base.improvement_option or base.native_valid_option~=true or base.improvement_unlocked~=true)then return false,'Base_development_unverified'end
 return true
end
local function customer(path)
 if not path.source or(path.stage~=2 and path.stage~=3)or not path.producer or not path.district or not path.building or not number(path.plot)then return nil,'customer_identity_or_mapping_unknown'end
 if path.mapping_valid~=true then
  -- UI may know the registry identity but have rejected its producer plan.
  -- Preserve the same rejection while exposing only captured branch subcauses.
  local failure=path.producer_failure
  if path.mapping_valid==false and path.quality_error=='producer_prerequisites_unverified'and type(failure)=='table'then
   local reasons={}
   for i,attempt in ipairs(type(failure.attempts)=='table'and failure.attempts or{})do if i>4 then break end
    reasons[#reasons+1]=tostring(attempt.upstream or'unknown')..'/'..tostring(attempt.cause or'unknown')
   end
   if #reasons==0 then reasons[1]=tostring(failure.reason or'unknown')end
   if type(failure.omitted)=='number'and failure.omitted>0 then reasons[#reasons+1]=tostring(failure.omitted)..'_other_failed_branches_omitted'end
   return nil,'producer_prerequisites_unverified:'..table.concat(reasons,';')
  end
  return nil,'customer_identity_or_mapping_unknown'
 end
 if path.owned~=true or path.adjacent~=true or path.footprint_conflict==true then return nil,'customer_ownership_adjacency_or_footprint'end
 if path.readiness=='actual'then
  if path.district_complete==true and path.district_functioning==true and path.building_functioning==true then return 3 end
  return nil,'actual_customer_not_functioning'
 end
 if path.readiness=='existing_district'then
  if path.district_complete==true and path.district_functioning==true and path.building_present==false and path.unlock_plausible==true then return 2 end
  return nil,'existing_customer_building_prerequisites_unknown'
 end
 if path.readiness=='future_plot'then
  if path.native_commitment==true then return nil,'contradicting_native_commitment'end
  if path.known_better_alternative==true then return nil,'known_better_customer_alternative'end
  if number(path.native_score)and number(path.alternative_score)and path.alternative_score>path.native_score then return nil,'known_better_customer_alternative'end
  if path.legal_plot~=true or path.unlock_plausible~=true or path.capacity_plausible~=true then return nil,'future_customer_essential_legality_unknown'end
  return 1
 end
 return nil,'customer_readiness_unknown'
end
V.Customer=customer
function V.Evaluate(config,packet)
 local out={version=2,mode=V.Mode(config),identity=copy(packet.identity),status='deferred',reasons={},customer_paths={},unknown_secondary_costs=copy(packet.unknown_secondary_costs or{}),real=copy(packet.quality),private=copy(packet.private),action_authorization=false}
 if out.mode~='v2'then out.status=out.mode;return out end
 if packet.original_AI~=true or packet.source_legal~=true or packet.source_can_produce~=true or packet.source_conflict~=false then out.reasons={'essential_source_or_role_evidence_unknown'};return out end
 local good,why=credibleBase(packet.base,packet.identity.player)
 if not good then out.status='declined';out.reasons={why};return out end
 for _,path in ipairs(packet.customer_paths or{})do local rank,reason=customer(path)
  if rank then local item=copy(path);item.readiness_rank=rank;item.alternatives_status=(number(path.native_score)and number(path.alternative_score))and'captured_comparison'or'unverified; unknown scores are not zero';out.customer_paths[#out.customer_paths+1]=item
  else out.reasons[#out.reasons+1]=reason end
 end
 table.sort(out.customer_paths,function(a,b)if a.readiness_rank~=b.readiness_rank then return a.readiness_rank>b.readiness_rank end;if a.stage~=b.stage then return a.stage<b.stage end;return a.plot<b.plot end)
 if #out.customer_paths==0 then out.status='declined_no_customer_path';return out end
 local anyKnown=false
 for _,path in ipairs(out.customer_paths)do
  local quality=path.quality or packet.quality;local current=quality and quality.current and quality.current.real or{}
  local projected=quality and quality.projected and quality.projected.real or{}
  local cp=number(current[Y[1]])and number(current[Y[2]])and current[Y[1]]+current[Y[2]]or nil
  local pp=number(projected[Y[1]])and number(projected[Y[2]])and projected[Y[1]]+projected[Y[2]]or nil
  anyKnown=anyKnown or cp~=nil or pp~=nil
  if packet.both_credible==true or(cp and cp>=4)or(pp and pp>=4)then
   out.customer=path;out.real=copy(quality);out.current_real_combined=cp;out.projected_real_combined=pp
   out.kind=packet.both_credible==true and'both'or'base_only_real4';break
  end
 end
 if not out.customer then out.status=anyKnown and'declined_below_real4'or'deferred_real_quality_unknown';return out end
 out.status='candidate';out.captured_turn=packet.turn or(packet.identity and packet.identity.turn);out.base=copy(packet.base);out.spec=copy(packet.spec);out.conditional=packet.base.working~=true or out.customer.readiness~='actual'or(out.real and out.real.projected~=nil)
 out.execution_readiness='fresh host/backend revalidation required';return out
end
function V.Intent(result,materials)
 if result.status~='candidate'then return nil end
 local selected={};for _,field in ipairs({'stage','transaction','producer','plot','district','building','readiness','customer_city'})do selected[field]=result.customer[field]end
 return{version=2,captured_turn=result.captured_turn,kind=result.kind,identity=copy(result.identity),base_plot=result.base.plot,base_resource=result.base.resource,spec_plot=result.spec and result.spec.plot,spec_resource=result.spec and result.spec.resource,materials=copy(materials),customer=selected}
end
function V.Revalidate(intent,packet)
 if type(intent)~='table'or intent.version~=2 or type(intent.identity)~='table'or type(intent.materials)~='table'or type(intent.customer)~='table'or type(packet)~='table'or type(packet.identity)~='table'or type(packet.base)~='table'then return nil,'typed_intent_required'end
 for _,field in ipairs({'player','city','source','quarter'})do if intent.identity[field]~=packet.identity[field]then return nil,'intent_identity_changed'end end
 if intent.base_plot~=packet.base.plot or intent.base_resource~=packet.base.resource then return nil,'intent_Base_identity_changed'end
 if intent.kind=='both'and(not packet.spec or intent.spec_plot~=packet.spec.plot or intent.spec_resource~=packet.spec.resource)then return nil,'intent_Spec_identity_changed'end
 local materials=packet.materials or{packet.base.plot,packet.spec and packet.spec.plot}
 if #materials~=#intent.materials then return nil,'intent_materials_changed'end
 for i,index in ipairs(intent.materials)do if materials[i]~=index then return nil,'intent_materials_changed'end end
 local bound
 for _,path in ipairs(packet.customer_paths or{})do local same=true
  for _,field in ipairs({'stage','transaction','producer','plot','district','building'})do if path[field]~=intent.customer[field]then same=false end end
  if same then bound=path;break end
 end
 if not bound then return nil,'intent_customer_identity_changed'end
 local scoped=copy(packet);scoped.customer_paths={bound}
 local fresh=V.Evaluate({version=2},scoped)
 if fresh.status~='candidate'or fresh.kind~=intent.kind then return nil,'intent_no_longer_qualifies'end
 return fresh
end
