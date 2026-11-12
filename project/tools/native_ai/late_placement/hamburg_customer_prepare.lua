-- Diagnostic common world only: create one completed Tailors to test native
-- customer co-location. This is not AI-built construction, a score writer or
-- shipping policy. Both later arms must load the SAME saved prepared world.
-- Preserve Sheep1084, queue, population and funds; declare any ordinary
-- Lumber Mill/feature conversion at the chosen legal Quarter footprint.
do
 assert(Game.GetCurrentGameTurn()==208 and not AutoplayManager.IsActive()
  and Game.GetLocalPlayer()==0 and Players[0]:IsHuman())
 assert(CSC_HAMBURG_CUSTOMER_PREPARE_STATE==nil,'Never retry a partly executed fixture')
 local index=assert(CSC_HAMBURG_CUSTOMER_PREPARE_PLOT);assert(type(index)=='number')
 local player=assert(Players[3]);local city=assert(CityManager.GetCity(3,393221))
 assert(not player:IsHuman() and city:GetName()=='LOC_CITY_NAME_HAMBURG')
 local P,A=assert(CSC_AI_QuarterPlacement),assert(CSC_Adjacency);A.Initialize()
 local profile
 for _,p in ipairs(P.StageTwoProfiles())do if p.key=='TAILORS'then profile=p end end
 assert(profile)
 local harbor=assert(GameInfo.Districts.DISTRICT_HARBOR)
 assert(profile.customers[harbor.Index] and not city:GetDistricts():HasDistrict(harbor.Index))
 assert(not city:GetDistricts():HasDistrict(profile.district.Index))
 local plot=assert(Map.GetPlotByIndex(index));local sheep=assert(Map.GetPlotByIndex(1084))
 assert(plot:GetOwner()==3 and Cities.GetPlotPurchaseCity(plot):GetID()==393221
  and plot:GetDistrictType()==-1 and plot:GetResourceType()==-1)
 assert(sheep:GetOwner()==3 and sheep:GetResourceType()==GameInfo.Resources.RESOURCE_SHEEP.Index)
 assert(Map.GetPlotDistance(plot:GetX(),plot:GetY(),sheep:GetX(),sheep:GetY())==1)
 local supplied=false
 for _,base in ipairs(P.ReadSuppliers(player,plot,profile).base)do
  if base.plot==1084 and base.ready then supplied=true end
 end
 assert(supplied,'Main supplier reader must recognize the actual selected footprint')
 local deductions=P.MaterialDeductions(player,false,0,0,nil,false)
 for _,entry in ipairs(deductions)do assert(entry.plot~=index,'Protected footprint')end
 local ui=assert(ExposedMembers.CSC_Adjacency);local quarterLegal=false
 for _,target in ipairs(ui.GetLegalDistrictTargets(3,393221,profile.district.Hash))do
  if target==index then quarterLegal=true end
 end
 assert(quarterLegal)
 local function customerTargets()
  local result={}
  for _,target in ipairs(ui.GetLegalDistrictTargets(3,393221,harbor.Hash))do
   local p=Map.GetPlotByIndex(target);local owner=Cities.GetPlotPurchaseCity(p)
   if p:GetOwner()==3 and owner and owner:GetID()==393221 and p:GetResourceType()==-1
    and Map.GetPlotDistance(plot:GetX(),plot:GetY(),p:GetX(),p:GetY())==1 then
    local protected=false
    for _,entry in ipairs(deductions)do if entry.plot==target then protected=true end end
    if not protected then result[#result+1]=target end
   end
  end
  return result
 end
 assert(#customerTargets()>0)
 local improvement,feature=plot:GetImprovementType(),plot:GetFeatureType()
 if improvement~=-1 then
  assert(index==1083 and improvement==GameInfo.Improvements.IMPROVEMENT_LUMBER_MILL.Index)
  assert(ImprovementBuilder and type(ImprovementBuilder.SetImprovementType)=='function')
 end
 if feature~=-1 then
  local definition=assert(GameInfo.Features[feature])
  assert(definition.FeatureType=='FEATURE_FOREST'or definition.FeatureType=='FEATURE_JUNGLE'
   or definition.FeatureType=='FEATURE_MARSH','Undeclared feature conversion')
  assert(TerrainBuilder and type(TerrainBuilder.SetFeatureType)=='function')
 end
 local queue=city:GetBuildQueue();assert(type(queue.CreateIncompleteDistrict)=='function')
 local gold,pop,item=player:GetTreasury():GetGoldBalance(),city:GetPopulation(),queue:CurrentlyBuilding()
 -- Reference XP2 RVA fbd90 (SHA324c51e9; hotfix text-identical) may PopFront
 -- an existing District production item when completing another district at
 -- a plot where that queued district cannot be zoned. WorldBuilder uses the
 -- SAME factory. Wait for natural Encampment completion; never repair/reset
 -- that queue by script. Empty/building/unit queues bypass that static branch.
 assert(item==nil or not GameInfo.Districts[item],'District still queued; no common fixture edits')
 local original={sheep:GetOwner(),Cities.GetPlotPurchaseCity(sheep):GetID(),sheep:GetResourceType(),
  sheep:GetResourceCount(),sheep:GetImprovementType(),sheep:GetTerrainType(),sheep:GetFeatureType()}
 print('CSC_CUSTOMER_COMMON_BEFORE',208,index,improvement,feature,gold,pop,item)
 -- All checks precede writes. The sentinel deliberately remains set on error.
 CSC_HAMBURG_CUSTOMER_PREPARE_STATE={plot=index,writes=0}
 local state=CSC_HAMBURG_CUSTOMER_PREPARE_STATE
 if improvement~=-1 then ImprovementBuilder.SetImprovementType(plot,-1,3);state.writes=state.writes+1 end
 if feature~=-1 then TerrainBuilder.SetFeatureType(plot,-1);state.writes=state.writes+1 end
 queue:CreateIncompleteDistrict(profile.district.Index,index,100);state.writes=state.writes+1
 local district
 local districts=city:GetDistricts()
 for i=0,districts:GetNumDistricts()-1 do
  local current=districts:GetDistrictByIndex(i)
  if current and current:GetType()==profile.district.Index
   and current:GetX()==plot:GetX() and current:GetY()==plot:GetY()then
   assert(not district);district=current
  end
 end
 assert(district and district:GetType()==profile.district.Index and district:IsComplete() and not district:IsPillaged())
 assert(plot:GetResourceType()==-1 and plot:GetImprovementType()==-1 and plot:GetFeatureType()==-1)
 local after={sheep:GetOwner(),Cities.GetPlotPurchaseCity(sheep):GetID(),sheep:GetResourceType(),
  sheep:GetResourceCount(),sheep:GetImprovementType(),sheep:GetTerrainType(),sheep:GetFeatureType()}
 for n,value in ipairs(original)do assert(after[n]==value,'Common fixture changed the material supplier')end
 print('CSC_CUSTOMER_COMMON_AFTER_QUEUE',208,tostring(item),tostring(queue:CurrentlyBuilding()))
 print('CSC_CUSTOMER_COMMON_AFTER_POP',208,pop,city:GetPopulation())
 print('CSC_CUSTOMER_COMMON_AFTER_GOLD',208,gold,player:GetTreasury():GetGoldBalance())
 assert(queue:CurrentlyBuilding()==item and city:GetPopulation()==pop and player:GetTreasury():GetGoldBalance()==gold,
  'Common fixture changed queue/population/funds; do not save it')
 local targets=customerTargets();assert(#targets>0,'Quarter creation removed customer legality')
 print('CSC_CUSTOMER_COMMON_CREATED',208,index,profile.district.Index,district:GetID(),state.writes,
  improvement,feature,plot:GetImprovementType(),plot:GetFeatureType())
 for _,target in ipairs(targets)do print('CSC_CUSTOMER_COMMON_HARBOR',208,target,harbor.Index)end
end
