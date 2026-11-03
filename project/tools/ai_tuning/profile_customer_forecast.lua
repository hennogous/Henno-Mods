-- Read-only UI controls for the RH Granary forecast candidate.
-- Expected inputs and the potential-yield getter come from THIS UI frame.
-- UI may lag Core by one turn: never label these facts as a Core-frame census.
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 assert(t=='table','Unexpected diagnostic type')
 local out,n,array={},0,true;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 if array then for _,x in ipairs(v)do out[#out+1]=json(x)end;return '['..table.concat(out,',')..']'end
 for k,x in pairs(v)do out[#out+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(out,',')..'}'
end
local requested=__TARGET_TURN__
local out={requested_core_turn=requested,ui_turn=Game.GetCurrentGameTurn(),records={},sources={},errors={},
 controls={positive_unbuilt=0,positive_built=0,negative_no_source=0,negative_human=0,uncertain=0,failed=0}}
assert(out.ui_turn==requested or out.ui_turn==requested-1,'UI controls clock outside observed lag')
local role=assert(ExposedMembers.CSC_RH_CustomerRoles,'RH configured-role component missing')
assert(role.version==2 and #role.errors==0,'RH configured-role component error')
local ui=assert(ExposedMembers.CSC_AI_AssistanceUI)
local originalHumans=assert(ui.InitialHumanPlayers())
assert(type(originalHumans)=='table','Original human identities unavailable')
out.configured_role_component={version=role.version,ready=role.ready,writes=role.writes,refreshes=role.refreshes}
out.foundation_priority=role.foundation_priority
local yield=assert(GameInfo.Yields['YIELD_CSC_AI_PLACEMENT'])
local targets={BUILDING_GRANARY=true}
for r in GameInfo.BuildingReplaces()do if r.ReplacesBuildingType=='BUILDING_GRANARY'then targets[r.CivUniqueBuildingType]=true end end
local mills={BUILDING_CSC_BAKERS_WIND_MILL=true,BUILDING_CSC_BAKERS_WATER_MILL=true}
local cities={}
for pid=0,5 do local player=Players[pid]
 if player and player:IsAlive()then
  for _,city in player:GetCities():Members()do
   assert(city:GetOwner()==pid,'UI city ownership mismatch')
   cities[#cities+1]={player=pid,city=city,human=originalHumans[tostring(pid)]==true or originalHumans[pid]==true,current_human=player:IsHuman()}
   local bs=city:GetBuildings();local ds=city:GetDistricts()
   -- These are the UI CitySupport.lua interfaces. Gameplay's building-location
   -- and district-by-index getters are not interchangeable with UI bindings.
   for _,district in ds:Members()do
    local plot=assert(Map.GetPlot(district:GetX(),district:GetY()),'UI district plot unavailable')
    local index=plot:GetIndex();local di=assert(GameInfo.Districts[district:GetType()])
    for _,buildingIndex in ipairs(bs:GetBuildingsAtLocation(index)or{})do
     local info=assert(GameInfo.Buildings[buildingIndex])
     if mills[info.BuildingType]then
      local marker=plot:GetProperty('CSC_RH_CUSTOMER_CONFIGURED_AI')
      local expectedRole=(originalHumans[tostring(pid)]or originalHumans[pid])and 0 or 1
      if marker~=expectedRole then out.controls.failed=out.controls.failed+1;out.errors[#out.errors+1]='Source plot configured-role marker mismatch: '..index end
      out.sources[#out.sources+1]={player=pid,city=city:GetID(),building=info.BuildingType,plot=index,x=plot:GetX(),y=plot:GetY(),
       configured_ai_marker=plot:GetProperty('CSC_RH_CUSTOMER_CONFIGURED_AI'),building_pillaged=bs:IsPillaged(info.Index),district_pillaged=ds:IsPillaged(district:GetType(),index),complete=ds:HasDistrict(di.Index,true)}
     end
    end
   end
  end
 end
end
for _,entry in ipairs(cities)do
 local city=entry.city;local matches,foreign,uncertain={},{},false
 for _,s in ipairs(out.sources)do
  if Map.GetPlotDistance(city:GetX(),city:GetY(),s.x,s.y)==1 then
   if s.player~=entry.player then foreign[#foreign+1]=s
   elseif s.complete and not s.building_pillaged and not s.district_pillaged then matches[#matches+1]=s
   elseif not s.building_pillaged then uncertain=true end
  end
 end
 for name in pairs(targets)do local b=assert(GameInfo.Buildings[name])
  -- Shipped ToolTipHelper.AddBuildingYieldTooltip uses Hash and YieldType.
  local value=city:GetBuildingPotentialYield(b.Hash,yield.YieldType)
  assert(type(value)=='number'and value==value,'Potential yield unavailable')
  local built=city:GetBuildings():HasBuilding(b.Index)
  local actualBuildingYield=built and city:GetBuildingYield(b.Index,yield.YieldType)or nil
  if entry.human and built and actualBuildingYield~=0 then
   out.controls.failed=out.controls.failed+1;out.errors[#out.errors+1]='Human actual Granary private yield is not zero'
  end
  local expected=entry.human and 0 or 40*#matches
  local kind=entry.human and'negative_human'or(uncertain and'uncertain'or(#matches==0 and'negative_no_source'or(built and'positive_built'or'positive_unbuilt')))
  local pass=kind~='uncertain'and math.abs(value-expected)<0.000001
  out.controls[kind]=out.controls[kind]+1
  if kind~='uncertain'and not pass then out.controls.failed=out.controls.failed+1 end
  out.records[#out.records+1]={player=entry.player,city=city:GetID(),name=city:GetName(),target=name,human=entry.human,
   built=built,actual=value,actual_building_yield=actualBuildingYield,current_human=entry.current_human,expected=expected,control=kind,pass=pass,matching_sources=matches,
   adjacent_foreign_sources=foreign,source_district_state_uncertain=uncertain}
 end
end
out.application_observed=out.controls.positive_unbuilt+out.controls.positive_built>0 and out.controls.failed==0
out.unbuilt_forecast_observed=out.controls.positive_unbuilt>0 and out.controls.failed==0
out.choice_effect='UNPROVEN_by_this_getter'
print('CSC_PROFILE_CUSTOMER_FORECAST='..json(out))
