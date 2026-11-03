-- Read-only CityAI recommendation capture in PlotInfo, using shipped signatures.
-- These returned lists may be cached/filtered. They are not scorer/job truth.
local function json(v,seen)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 if t~='table'then return json({lua_type=t,text=tostring(v)},seen)end
 seen=seen or{};assert(not seen[v],'Cyclic native recommendation result');seen[v]=true
 local a,n,array={},0,true;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end;if n~=#v then array=false end
 if array then for _,x in ipairs(v)do a[#a+1]=json(x,seen)end;seen[v]=nil;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k),seen)..':'..json(x,seen)end;seen[v]=nil;return '{'..table.concat(a,',')..'}'
end
local pid=3;local player=assert(Players[pid]);local turn=Game.GetCurrentGameTurn()
assert(turn>=110 and turn<=113 and player:IsAlive()and player:IsMajor()and not player:IsHuman())
assert(not PlayerConfigurations[pid]:IsHuman())
local out={schema=1,player=pid,turn=turn,scope='all AI3 cities x all real AI3 Builders',cities={},builders={},targets={},
 budget={max_cities=16,max_builders=16,max_API_calls=272,API_calls=0,returned_table_entries=0},
 cache_status='unknown; getters may return cached or filtered recommendations',assignment_truth=false,scorer_trace=false}
local units={}
for _,unit in player:GetUnits():Members()do if unit:GetType()==GameInfo.Units.UNIT_BUILDER.Index then
 local component=assert(unit:GetComponentID(),'Missing actual Builder component ID') -- Preserve the real object for direct API use.
 units[#units+1]={unit=unit,component=component}
 out.builders[#out.builders+1]={unit=unit:GetID(),owner=unit:GetOwner(),type=unit:GetType(),x=unit:GetX(),y=unit:GetY(),moves=unit:GetMovesRemaining(),charges=unit:GetBuildCharges(),component_type=type(component),component_id=component}
end end
assert(#units<=out.budget.max_builders,'Builder scope exceeds bounded capture')
local function invoke(ai,name,...)
 if not ai or type(ai[name])~='function'then return{status='unavailable',available=false,called=false}end
 assert(out.budget.API_calls<out.budget.max_API_calls,'Native recommendation call budget exceeded')
 out.budget.API_calls=out.budget.API_calls+1
 local ok,value=pcall(ai[name],ai,...)
 if not ok then return{status='error',available=true,called=true,ok=false,error=tostring(value)}end
 local result={status='ok_non_table',available=true,called=true,ok=true,native_return_type=type(value),raw_result=value}
 if type(value)=='table'then
  local n=0;for _ in pairs(value)do n=n+1 end
  result.returned_entries=n;result.status=n==0 and'ok_empty'or'ok_records';out.budget.returned_table_entries=out.budget.returned_table_entries+n
 end
 return result
end
local city_count=0
for _,city in player:GetCities():Members()do
 city_count=city_count+1;assert(city_count<=out.budget.max_cities,'City scope exceeds bounded capture');assert(city:GetOwner()==pid)
 local ai=city:GetCityAI();local row={owner=pid,city=city:GetID(),x=city:GetX(),y=city:GetY(),generic=invoke(ai,'GetImprovementRecommendations'),builder_recommendations={}}
 for _,entry in ipairs(units)do
  row.builder_recommendations[#row.builder_recommendations+1]={owner=pid,city=city:GetID(),unit=entry.unit:GetID(),component_type=type(entry.component),component_id=entry.component,
   result=invoke(ai,'GetImprovementRecommendationsForBuilder',entry.component)}
 end
 out.cities[#out.cities+1]=row
end
for _,idx in ipairs({2489,2344,2346})do local p=assert(Map.GetPlotByIndex(idx));local c=Cities.GetPlotPurchaseCity(p)
 out.targets[#out.targets+1]={plot=idx,x=p:GetX(),y=p:GetY(),owner=p:GetOwner(),purchase_city=c and c:GetID()or-1,resource=p:GetResourceType(),improvement=p:GetImprovementType(),feature=p:GetFeatureType()}
end
print('CSC_MATERIAL_RECOMMENDATIONS='..json(out))
