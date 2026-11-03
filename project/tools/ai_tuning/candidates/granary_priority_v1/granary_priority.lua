-- Experimental append-only payload. No orders, yields or economic changes.
-- The native Buildings preference is player-wide while one exact local gap
-- qualifies. This private flag is nil/inactive by default; no UI roundtrip or
-- current autoplay IsHuman flag is used by the predicate.
do
 local FLAG='CSC_AI_GRANARY_PRIORITY_V1'
 local CALLBACK='CSC_AI_GranaryPriority_V1'
 local G={version=1,flag_property=FLAG,callback_name=CALLBACK,
  strategy_type='STRATEGY_CSC_AI_GRANARY_PRIORITY_V1',list_type=CALLBACK,
  registered=0,calls=0,true_calls=0,false_calls=0,error_count=0,
  states={},transitions={},errors={},callback_forms={},
  stopped_notifications='UNOBSERVED: no validated stop-notification interface',
  native_adoption='UNOBSERVED_BY_CALLBACK'}
 ExposedMembers.CSC_AI_GranaryPriority=G
 local function copy(v)
  if type(v)~='table'then return v end
  local out={};for k,x in pairs(v)do out[k]=copy(x)end;return out
 end
 local function mode()
  for row in GameInfo.CSC_AI_Profile()do if row.Id=='ACTIVE'then return row.Mode end end
  return 'OFF'
 end
 local mapping=nil
 local function materials()
  if mapping then return mapping end
  local tags,valid={},{}
  for row in GameInfo.TypeTags()do if row.Tag=='CLASS_CSC_BAKERS_BASE'then tags[row.Type]=true end end
  for row in GameInfo.Improvement_ValidResources()do
   valid[row.ResourceType]=valid[row.ResourceType]or{};valid[row.ResourceType][row.ImprovementType]=true
  end
  mapping={tags=tags,valid=valid};return mapping
 end
 local function visible(player,res)
  if res.PrereqTech then local row=GameInfo.Technologies[res.PrereqTech]
   if not row or not player:GetTechs():HasTech(row.Index)then return false end
  end
  if res.PrereqCivic then local row=GameInfo.Civics[res.PrereqCivic]
   if not row or not player:GetCulture():HasCivic(row.Index)then return false end
  end
  return true
 end
 -- Pure facts: no callback counters/transitions, Game/plot writes or UI bridge.
 local function predicate(pid)
  local fact={active=false,turn=Game.GetCurrentGameTurn(),player=pid,city=196610,source=2711,working_base_plots={},functioning_mills={}}
  local function off(reason)fact.reason=reason;return fact end
  local cfg=Game:GetProperty(FLAG)
  if cfg==nil then return off('flag_inactive')end
  if type(cfg)~='table'or cfg.version~=1 or cfg.player~=3 or cfg.city~=196610 or cfg.source~=2711
   or cfg.start_turn~=110 or cfg.deadline_turn~=131 then return off('flag_invalid')end
  if pid~=3 then return off('other_player')end
  if fact.turn<110 or fact.turn>131 then return off('outside_window')end
  if mode()~='RH'then return off('profile_not_RH')end
  local roles=Game:GetProperty('CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS')
  if type(roles)~='table'or not(roles['0']==true or roles[0]==true)then return off('original_roles_unknown')end
  if roles['3']==true or roles[3]==true then return off('configured_human')end
  fact.original_configured_AI=true
  local player=Players[pid]
  if not player or not player:IsAlive()or not player:IsMajor()then return off('ineligible_player')end
  local city=CityManager.GetCity(pid,196610)
  if not city or city:GetOwner()~=pid then return off('city_missing_or_captured')end
  local source=Map.GetPlotByIndex(2711)
  if not source or source:GetOwner()~=pid then return off('source_missing_or_captured')end
  local quarter=GameInfo.Districts['DISTRICT_CSC_BAKERS_QUARTER']
  if not quarter or source:GetDistrictType()~=quarter.Index then return off('source_type_changed')end
  local district=city:GetDistricts():GetDistrictAtLocation(source:GetX(),source:GetY())
  if not district or district:GetType()~=quarter.Index or district:IsComplete()~=true or district:IsPillaged()~=false then return off('source_not_functioning')end
  fact.source_complete=true;fact.source_unpillaged=true
  local buildings=city:GetBuildings()
  for _,name in ipairs({'BUILDING_CSC_BAKERS_WIND_MILL','BUILDING_CSC_BAKERS_WATER_MILL'})do local b=GameInfo.Buildings[name]
   if b and b.PrereqDistrict=='DISTRICT_CSC_BAKERS_QUARTER'and buildings:HasBuilding(b.Index)and buildings:IsPillaged(b.Index)==false then
    fact.functioning_mills[#fact.functioning_mills+1]=name
   end
  end
  if #fact.functioning_mills==0 then return off('no_functioning_mill')end
  local center=Map.GetPlot(city:GetX(),city:GetY());local centerDef=GameInfo.Districts['DISTRICT_CITY_CENTER']
  if not center or not centerDef or center:GetOwner()~=pid or center:GetDistrictType()~=centerDef.Index
   or Map.GetPlotDistance(source:GetX(),source:GetY(),center:GetX(),center:GetY())~=1 then return off('customer_not_adjacent_owned_center')end
  local cc=city:GetDistricts():GetDistrictAtLocation(center:GetX(),center:GetY())
  if not cc or cc:GetType()~=centerDef.Index or cc:IsComplete()~=true then return off('customer_incomplete')end
  fact.customer_plot=center:GetIndex()
  -- City Center defense pillage is not used as a building-function gate.
  local granary=GameInfo.Buildings['BUILDING_GRANARY']
  if not granary or granary.Index~=3 then return off('granary_mapping_unknown')end
  if buildings:HasBuilding(granary.Index)then return off('granary_present')end
  fact.granary_missing=true
  local pottery=GameInfo.Technologies['TECH_POTTERY']
  if not pottery or not player:GetTechs():HasTech(pottery.Index)then return off('pottery_locked')end
  fact.pottery=true
  local map=materials()
  for direction=0,5 do local near=Map.GetAdjacentPlot(source:GetX(),source:GetY(),direction)
   if near then
   local resource=GameInfo.Resources[near:GetResourceType()];local improvement=GameInfo.Improvements[near:GetImprovementType()]
   if near:GetOwner()==pid and near:GetDistrictType()<0 and resource and improvement
    and map.tags[resource.ResourceType]and map.valid[resource.ResourceType]and map.valid[resource.ResourceType][improvement.ImprovementType]
    and PlayersVisibility[pid]:IsRevealed(near:GetX(),near:GetY())and visible(player,resource)
    and near:IsImprovementPillaged()==false then fact.working_base_plots[#fact.working_base_plots+1]=near:GetIndex()end
   end
  end
  if #fact.working_base_plots==0 then return off('no_working_base')end
  table.sort(fact.working_base_plots);fact.active=true;fact.reason='qualifying_target_gap';return fact
 end
 local function checked(pid)
  local ok,value=pcall(predicate,pid)
  if ok then return value end
  return{active=false,reason='predicate_error',error=tostring(value),turn=Game.GetCurrentGameTurn(),player=pid,city=196610,source=2711}
 end
 local function status()
  local out={};for _,key in ipairs({'version','flag_property','callback_name','strategy_type','list_type','registered','calls','true_calls','false_calls',
   'error_count','states','transitions','errors','callback_forms','last_callback','stopped_notifications','native_adoption'})do out[key]=copy(G[key])end
  return out
 end
 function G.Inspect(pid)return{flag=copy(Game:GetProperty(FLAG)),predicate=checked(pid),status=status()}end
 local function evaluate(...)
  G.calls=G.calls+1;local pid=select(1,...);local count=select('#',...)
  G.callback_forms[tostring(count)]=(G.callback_forms[tostring(count)]or 0)+1
  local raw={argument_count=count,arguments={}}
  for i=1,math.min(count,4)do local value=select(i,...);local kind=type(value)
   raw.arguments[i]={type=kind};if kind=='number'or kind=='boolean'or kind=='string'then raw.arguments[i].value=value end
  end
  G.last_callback=raw
  local fact=checked(pid)
  if fact.error then G.error_count=G.error_count+1;if #G.errors<20 then G.errors[#G.errors+1]={turn=fact.turn,error=fact.error}end end
  if fact.active then G.true_calls=G.true_calls+1 else G.false_calls=G.false_calls+1 end
  local key=tostring(pid);local previous=G.states[key]
  if not previous or previous.active~=fact.active or previous.reason~=fact.reason then
   local row={turn=fact.turn,player=pid,active=fact.active,reason=fact.reason}
   G.states[key]=row;if #G.transitions<256 then G.transitions[#G.transitions+1]=copy(row)end
  end
  return fact.active
 end
 if GameEvents and GameEvents[CALLBACK]then
  local ok,error=pcall(function()GameEvents[CALLBACK].Add(evaluate)end)
  if ok then G.registered=1 else G.error_count=G.error_count+1;G.errors[1]={error=tostring(error),stage='registration'}end
 else G.error_count=G.error_count+1;G.errors[1]={error='missing_native_GameEvent',stage='registration'}end
end
