-- Diagnostic only: qualify the2.1 Hamburg geometry before any common fixture.
-- Reads main CSC's relationships/protections and native UI targets. It never
-- publishes a bid, places a district, edits a queue or advances the clock.
-- The controller combines this with UI capacity readback and refuses edits
-- unless the loaded required population slots remain for Quarter and Harbor.
do
 local function object(v)return setmetatable(v or {},{__json_object=true})end
 local function json(v)
  if type(v)=='nil'then return 'null'end
  if type(v)=='number'or type(v)=='boolean'then return tostring(v)end
  if type(v)=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
  assert(type(v)=='table');local rows={}
  if getmetatable(v)and getmetatable(v).__json_object then
   local keys={};for key in pairs(v)do keys[#keys+1]=key end;table.sort(keys)
   for _,key in ipairs(keys)do rows[#rows+1]=json(key)..':'..json(v[key])end
   return '{'..table.concat(rows,',')..'}'
  end
  for _,item in ipairs(v)do rows[#rows+1]=json(item)end
  return '['..table.concat(rows,',')..']'
 end
 local turn=Game.GetCurrentGameTurn()
 assert((turn==202 or turn==208)and not AutoplayManager.IsActive())
 local player=assert(Players[3]);local city=assert(CityManager.GetCity(3,393221))
 assert(not player:IsHuman() and city:GetName()=='LOC_CITY_NAME_HAMBURG')
 local P,A=assert(CSC_AI_QuarterPlacement),assert(CSC_Adjacency);A.Initialize()
 local ui=assert(ExposedMembers.CSC_Adjacency)
 assert(type(ui.GetLegalDistrictTargets)=='function')
 local profile
 for _,p in ipairs(P.StageTwoProfiles())do if p.key=='TAILORS'then profile=p end end
 assert(profile)
 local harbor=assert(GameInfo.Districts.DISTRICT_HARBOR)
 assert(profile.customers[harbor.Index],'Loaded Stage2 mapping is not Harbor')
 local deductions,_,_,_,chains=P.MaterialDeductions(player,false,0,0,nil,false)
 local protected={}
 for _,entry in ipairs(deductions)do protected[entry.plot]=true end
 local function targets(definition)
  local rows=assert(ui.GetLegalDistrictTargets(3,393221,definition.Hash));table.sort(rows)
  local known={};for _,index in ipairs(rows)do assert(not known[index]);known[index]=true end
  return rows,known
 end
 local harborTargets,harborSet=targets(harbor)
 local quarterTargets,quarterSet=targets(profile.district)
 local function plotFacts(index)
  local plot=assert(Map.GetPlotByIndex(index));local owner=Cities.GetPlotPurchaseCity(plot)
  local resource=GameInfo.Resources[plot:GetResourceType()]
  local district=GameInfo.Districts[plot:GetDistrictType()]
  local improvement=GameInfo.Improvements[plot:GetImprovementType()]
  return object{plot=index,owner=plot:GetOwner(),city=owner and owner:GetID()or -1,
   district=plot:GetDistrictType(),districtType=district and district.DistrictType or '-',
   resource=plot:GetResourceType(),resourceType=resource and resource.ResourceType or '-',
   improvement=plot:GetImprovementType(),improvementType=improvement and improvement.ImprovementType or '-',
   terrain=plot:GetTerrainType(),feature=plot:GetFeatureType(),protected=protected[index]==true,
   quarterTarget=quarterSet[index]==true,harborTarget=harborSet[index]==true}
 end
 local site=assert(Map.GetPlotByIndex(1083));local supply=P.ReadSuppliers(player,site,profile)
 local suppliers={}
 for _,base in ipairs(supply.base)do
  local facts=plotFacts(base.plot);facts.ready=base.ready;facts.working=base.working
  suppliers[#suppliers+1]=facts
 end
 local candidates={}
 for _,index in ipairs(harborTargets)do
  local facts=plotFacts(index);local plot=Map.GetPlotByIndex(index)
  facts.quarterDistance=Map.GetPlotDistance(site:GetX(),site:GetY(),plot:GetX(),plot:GetY())
  candidates[#candidates+1]=facts
 end
 -- Only six supplier-neighbor alternatives: this is fixture selection, not
 -- shipping policy or a world search. Prefer an unimproved valid footprint.
 local alternatives={};local sheep=assert(Map.GetPlotByIndex(1084))
 for _,plot in ipairs(Map.GetAdjacentPlots(sheep:GetX(),sheep:GetY()))do
  local facts=plotFacts(plot:GetIndex());facts.supplierDistance=1;facts.customerPlots={}
  for _,index in ipairs(harborTargets)do
   local target=Map.GetPlotByIndex(index)
   if Map.GetPlotDistance(plot:GetX(),plot:GetY(),target:GetX(),target:GetY())==1 then
    facts.customerPlots[#facts.customerPlots+1]=index
   end
  end
  alternatives[#alternatives+1]=facts
 end
 local nativeSignal=object{yieldDefinition=object{},bias={},adjacencies={}}
 local yield=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT
 if yield then
  nativeSignal.yieldDefinition=object{type=yield.YieldType,index=yield.Index,defaultValue=yield.DefaultValue}
  for row in GameInfo.AiFavoredItems()do
   if row.ListType=='DefaultYieldBias'and row.Item==yield.YieldType then
    nativeSignal.bias[#nativeSignal.bias+1]=object{list=row.ListType,item=row.Item,value=row.Value,favored=row.Favored}
   end
  end
  for row in GameInfo.District_Adjacencies()do
   if row.DistrictType==harbor.DistrictType then
    local rule=GameInfo.Adjacency_YieldChanges[row.YieldChangeId]
    if rule and rule.YieldType==yield.YieldType then
     nativeSignal.adjacencies[#nativeSignal.adjacencies+1]=object{id=row.YieldChangeId,
      customer=row.DistrictType,quarter=rule.AdjacentDistrict,yield=rule.YieldType,amount=rule.YieldChange,
      tilesRequired=rule.TilesRequired}
    end
   end
  end
 end
 local catalog={}
 for definition in GameInfo.Districts()do
  catalog[#catalog+1]=object{type=definition.DistrictType,index=definition.Index}
  print('CSC_CUSTOMER_INSPECT_DISTRICT',definition.DistrictType,definition.Index)
 end
 local result=object{turn=turn,mutationCommands=0,
  city=object{player=3,id=393221,name=city:GetName(),population=city:GetPopulation(),
   queued=city:GetBuildQueue():CurrentlyBuilding(),
   queueIsDistrict=city:GetBuildQueue():CurrentlyBuilding()~=nil
    and GameInfo.Districts[city:GetBuildQueue():CurrentlyBuilding()]~=nil,
   hasQuarter=city:GetDistricts():HasDistrict(profile.district.Index),
   hasHarbor=city:GetDistricts():HasDistrict(harbor.Index)},
  quarter=object{type=profile.district.DistrictType,index=profile.district.Index,
   hash=profile.district.Hash,requiresPopulation=profile.district.RequiresPopulation},
  harbor=object{type=harbor.DistrictType,index=harbor.Index,hash=harbor.Hash,requiresPopulation=harbor.RequiresPopulation},
  site=plotFacts(1083),suppliers=suppliers,candidates=candidates,quarterAlternatives=alternatives,nativeSignal=nativeSignal,
  harborTargets=harborTargets,quarterTargets=quarterTargets,catalog=catalog}
 -- The console preserves the full response; parse failure is fatal. The raw
 -- response and parsed JSON are both archived even if Lua.log clips its line.
 print('CSC_HAMBURG_CUSTOMER_INSPECT='..json(result))
end
