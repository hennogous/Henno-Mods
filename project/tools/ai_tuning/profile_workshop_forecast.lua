-- Read-only controls for the material-backed Workshop forecast. Expected scope
-- is reconstructed from THIS UI frame, independently of the SQL requirement
-- evaluator. Incomplete/pillaged district behavior is recorded as uncertain.
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
local out={requested_core_turn=requested,ui_turn=Game.GetCurrentGameTurn(),records={},errors={},
 controls={positive_unbuilt=0,positive_built=0,negative_human=0,negative_no_base=0,negative_no_quarter=0,uncertain=0,failed=0}}
assert(out.ui_turn==requested or out.ui_turn==requested-1,'UI controls clock outside observed lag')
local role=assert(ExposedMembers.CSC_RH_CustomerRoles,'Configured-role component missing')
assert(role.version==2 and #role.errors==0,'Configured-role component error')
local humans=assert(ExposedMembers.CSC_AI_AssistanceUI.InitialHumanPlayers())
local target=assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP)
local quarter=assert(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER)
local yield=assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT)
local legal,mapping={},{BASE={},SPEC={}}
for r in GameInfo.Improvement_ValidResources()do legal[r.ResourceType]=true end
for r in GameInfo.TypeTags()do
 local key=r.Tag=='CLASS_CSC_TAILORS_BASE'and'BASE'or(r.Tag=='CLASS_CSC_TAILORS_SPEC'and'SPEC'or nil)
 if key and legal[r.Type]and GameInfo.Resources[r.Type]then mapping[key][r.Type]=true end
end
local function visible(player,info)
 if info.PrereqTech then return player:GetTechs():HasTech(assert(GameInfo.Technologies[info.PrereqTech]).Index)end
 if info.PrereqCivic then return player:GetCulture():HasCivic(assert(GameInfo.Civics[info.PrereqCivic]).Index)end
 return true
end
-- Native CanProduce's second result may be a table. Preserve bounded printable
-- evidence; never feed that table to Lua assert's string message parameter.
local function reasonText(value,depth)
 if type(value)~='table'then return tostring(value)end
 if depth==0 then return '<table>'end
 local rows={};for k,v in pairs(value)do rows[#rows+1]=tostring(k)..'='..reasonText(v,depth-1)end
 table.sort(rows);return '{'..table.concat(rows,',')..'}'
end
for pid=0,5 do local player=Players[pid]
 if player and player:IsAlive()then
  local human=humans[tostring(pid)]==true or humans[pid]==true
  for _,city in player:GetCities():Members()do
   assert(city:GetOwner()==pid,'UI city owner mismatch')
   local ds=city:GetDistricts();local sources={};local base,spec=0,0;local uncertain=false
   for _,district in ds:Members()do
    if district:GetType()==quarter.Index then
     local p=assert(Map.GetPlot(district:GetX(),district:GetY()));local idx=p:GetIndex()
     local marker=p:GetProperty('CSC_RH_CUSTOMER_CONFIGURED_AI')
     if marker~=(human and 0 or 1)then out.controls.failed=out.controls.failed+1;out.errors[#out.errors+1]='Quarter role marker mismatch: '..idx end
     local source={plot=idx,marker=marker,complete=ds:HasDistrict(quarter.Index,true),pillaged=ds:IsPillaged(quarter.Index,idx),neighbors={}}
     for _,n in ipairs(Map.GetAdjacentPlots(p:GetX(),p:GetY())or{})do
      local info=GameInfo.Resources[n:GetResourceType()]
      if info then
       local known=visible(player,info);local owned=n:GetOwner()==pid;local uncovered=n:GetDistrictType()<0
       local isBase=mapping.BASE[info.ResourceType]==true;local isSpec=mapping.SPEC[info.ResourceType]==true
       source.neighbors[#source.neighbors+1]={plot=n:GetIndex(),owner=n:GetOwner(),resource=info.ResourceType,visible=known,owned=owned,uncovered=uncovered,base=isBase,spec=isSpec}
       if owned and known and uncovered and isBase then base=base+1 end
       if owned and known and uncovered and isSpec then spec=spec+1 end
      end
     end
     if not source.complete or source.pillaged then uncertain=true end
     sources[#sources+1]=source
    end
   end
   assert(#sources<=1,'Unexpected duplicate Tailors Quarter in city')
   if #sources==1 then
    local source=sources[1];local p=assert(Map.GetPlotByIndex(source.plot))
    source.base_fact=p:GetProperty('CSC_RH_WORKSHOP_BASE_PRESENT')
    source.spec_fact=p:GetProperty('CSC_RH_WORKSHOP_SPEC_PRESENT')
    local expectedBase=not human and base>0 and 1 or 0
    local expectedSpec=not human and spec>0 and 1 or 0
    if source.base_fact~=expectedBase or source.spec_fact~=expectedSpec then
     out.controls.failed=out.controls.failed+1
     out.errors[#out.errors+1]='Source supply facts disagree with independent UI neighbours: '..source.plot
    end
   end

   local expected=not human and base>0 and(80+(spec>0 and 40 or 0))or 0
   local value=city:GetBuildingPotentialYield(target.Hash,yield.YieldType)
   assert(type(value)=='number'and value==value,'Potential yield unavailable')
   local built=city:GetBuildings():HasBuilding(target.Index)
   local actual=built and city:GetBuildingYield(target.Index,yield.YieldType)or nil
   -- Public Culture is observational evidence for the real material-to-Workshop
   -- path. Potential input is separate from a physically built producer.
   local potentialCulture=city:GetBuildingPotentialYield(target.Hash,'YIELD_CULTURE')
   local actualCulture=built and city:GetBuildingYield(target.Index,'YIELD_CULTURE')or nil
   assert(type(potentialCulture)=='number','Public Culture getter unavailable')
   local canProduce,reasons=city:GetBuildQueue():CanProduce(target.Hash,false,true)
   assert(type(canProduce)=='boolean','CanProduce returned no boolean')
   local kind=human and'negative_human'or(uncertain and'uncertain'or(#sources==0 and'negative_no_quarter'or(base==0 and'negative_no_base'or(built and'positive_built'or'positive_unbuilt'))))
   local pass=kind~='uncertain'and math.abs(value-expected)<0.000001
   -- Realized private building input is checked separately from potential.
   if built and kind~='uncertain'and actual~=expected then pass=false end
   out.controls[kind]=out.controls[kind]+1
   if kind~='uncertain'and not pass then out.controls.failed=out.controls.failed+1 end
   out.records[#out.records+1]={player=pid,city=city:GetID(),name=city:GetName(),human=human,current_human=player:IsHuman(),
    target=target.BuildingType,built=built,actual_building_yield=actual,potential_culture=potentialCulture,actual_culture=actualCulture,actual=value,expected=expected,control=kind,pass=pass,
    base_neighbors=base,spec_neighbors=spec,sources=sources,native_can_produce=canProduce,native_reasons=reasonText(reasons,2)}
  end
 end
end
out.application_observed=out.controls.positive_unbuilt+out.controls.positive_built>0 and out.controls.failed==0
out.unbuilt_forecast_observed=out.controls.positive_unbuilt>0 and out.controls.failed==0
out.choice_effect='UNPROVEN_by_this_getter'
print('CSC_PROFILE_WORKSHOP_FORECAST='..json(out))
