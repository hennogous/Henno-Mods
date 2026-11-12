-- Diagnostic only: inspect the retained Nicopolis plan and one potential Base
-- opportunity. Calls the actual main planner, without publishing a CE packet,
-- changing a score, queue, ownership or game clock. The shared controller alone
-- may call the separate explicit territorial fixture after these facts qualify.
do
 local function object(t)return setmetatable(t or {},{__json_object=true})end
 local function json(v)
  local kind=type(v)
  if kind=='nil'then return 'null'end
  if kind=='boolean'or kind=='number'then return tostring(v)end
  if kind=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r')..'"'end
  assert(kind=='table','Unexpected diagnostic value')
  local rows={}
  if getmetatable(v)and getmetatable(v).__json_object then
   local keys={};for k in pairs(v)do keys[#keys+1]=k end;table.sort(keys)
   for _,k in ipairs(keys)do rows[#rows+1]=json(k)..':'..json(v[k])end
   return '{'..table.concat(rows,',')..'}'
  end
  for _,value in ipairs(v)do rows[#rows+1]=json(value)end
  return '['..table.concat(rows,',')..']'
 end
 local function optional(value,name,...)
  if not value or type(value[name])~='function'then return 'unavailable'end
  local ok,result=pcall(value[name],value,...)
  if ok and result~=nil then return result end
  return 'unavailable'
 end
 function CSC_DEFERRAL_OPPORTUNITY_Inspect()
  local player=assert(Players[1]);local city=assert(CityManager.GetCity(1,524295))
  assert(city:GetName()=='LOC_CITY_NAME_NICOPOLIS')
  local placement=assert(CSC_AI_QuarterPlacement)
  local profile
  for _,p in ipairs(placement.StageTwoProfiles())do if p.key=='BAKERS'then profile=p end end
  assert(profile and profile.district.Index==36)
  local ui=assert(ExposedMembers.CSC_Adjacency)
  local deductions,_,_,_,chains=placement.MaterialDeductions(player,false,0,0,nil,false)
  local protected={};for _,e in ipairs(deductions)do protected[e.plot]=true end
  local offers=CSC_AI_QuarterSiteForecasts(player,profile,chains,placement.ReadSuppliers,protected,ui)
  local byPlot={}
  for _,offer in ipairs(offers)do
   if offer.city==524295 and offer.district==36 then byPlot[offer.plot]=offer end
  end
  local supplier=assert(Map.GetPlotByIndex(471))
  local ownerCity=Cities.GetPlotPurchaseCity(supplier)
  local resource=GameInfo.Resources[supplier:GetResourceType()]
  local improvement=GameInfo.Improvements[supplier:GetImprovementType()]
  local status=assert(CE_AIDistrictScoresStatus())
  local version=assert(tonumber(status:match('"version":(%d+)')))
  local result=object{turn=Game.GetCurrentGameTurn(),ceVersion=version,ceStatus=status,
   mutationCommands=0,hasQuarter=city:GetDistricts():HasDistrict(36),
   city=object{owner=1,id=524295,name=city:GetName(),population=city:GetPopulation(),
    x=city:GetX(),y=city:GetY(),currentItem=city:GetBuildQueue():CurrentlyBuilding(),
    allowed=optional(city:GetDistricts(),'GetNumAllowedDistrictsRequiringPopulation'),
    zoned=optional(city:GetDistricts(),'GetNumZonedDistrictsRequiringPopulation')},
   supplier=object{plot=471,owner=supplier:GetOwner(),city=ownerCity and ownerCity:GetID() or -1,
    resource=supplier:GetResourceType(),resourceType=resource and resource.ResourceType or '-',
    improvement=supplier:GetImprovementType(),improvementType=improvement and improvement.ImprovementType or '-',
    pillaged=supplier:IsImprovementPillaged(),terrain=supplier:GetTerrainType(),feature=supplier:GetFeatureType(),
    resourceCount=optional(supplier,'GetResourceCount'),riverEdges=supplier:GetRiverCrossingCount(),
    revealed=PlayersVisibility[1]:IsRevealed(supplier:GetX(),supplier:GetY()),
    resourceVisible=resource and CSC_Adjacency.ResourceVisible(1,resource.Index)or false,
    mappedBase=resource and CSC_Adjacency.HasTag(profile.base,resource.ResourceType)or false},sites={}}
  for _,index in ipairs({397,398,472})do
   local plot=assert(Map.GetPlotByIndex(index));local purchaseCity=Cities.GetPlotPurchaseCity(plot)
   local supply=placement.ReadSuppliers(player,plot,profile);local sources={}
   for _,s in ipairs(supply.base)do sources[#sources+1]=object{plot=s.plot,ready=s.ready,working=s.working}end
   local neighbors={}
   for _,neighbor in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
    local district=GameInfo.Districts[neighbor:GetDistrictType()]
    neighbors[#neighbors+1]=object{plot=neighbor:GetIndex(),owner=neighbor:GetOwner(),district=neighbor:GetDistrictType(),
     districtType=district and district.DistrictType or '-',
     sales=district and CSC_Adjacency.HasTag('CLASS_CSC_BAKERS_SALES',district.DistrictType)or false,
     goodsProvider=district and CSC_Adjacency.HasTag('CLASS_CSC_BAKERS_GOODS_PROVIDER',district.DistrictType)or false}
   end
   local offer=byPlot[index];local hostTargets={}
   for _,host in ipairs(offer and offer.futureHost or {})do
    hostTargets[#hostTargets+1]=object{district=host.district,plot=host.plot,city=host.city}
   end
   result.sites[#result.sites+1]=object{plot=index,owner=plot:GetOwner(),city=purchaseCity and purchaseCity:GetID()or -1,
    district=plot:GetDistrictType(),legal=plot:CanHaveDistrict(36,1,524295),
    supplierDistance=Map.GetPlotDistance(plot:GetX(),plot:GetY(),supplier:GetX(),supplier:GetY()),
    base=sources,quote=ui.GetPlotPurchaseQuote(1,524295,index),neighbors=neighbors,
    model=offer and object{delta=offer.delta,weak=offer.weak,declineNoBase=offer.declineNoBase,
     adjacency=offer.adjacency,pending=offer.pending,currentLegalHostTargets=hostTargets}or object{},
    declineReceipt=CE_AIDistrictDeclineReceipt(version,1,524295,36,index)}
  end
  -- Civ clips long single log lines. Exact bounded framing preserves the full
  -- model/physical snapshot; the controller rejects gaps or duplicate chunks.
  local payload=json(result);local parts=math.ceil(#payload/1000)
  for part=1,parts do
   print('CSC_DEFERRAL_OPPORTUNITY_CHUNK',result.turn,part,parts,payload:sub((part-1)*1000+1,part*1000))
  end
  print('CSC_DEFERRAL_OPPORTUNITY_END',result.turn,parts,#payload)
 end
end
CSC_DEFERRAL_OPPORTUNITY_Inspect()
