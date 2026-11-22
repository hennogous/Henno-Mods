-- Disposable matched test. The scout reads the stock placement API in
-- PlotInfo. Setup runs separately in Gameplay on the validated save copy.
local quarter=assert(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER)
local producer=assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_FASHION_HOUSE)
local workshop=assert(GameInfo.Buildings.BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP)
local base,specialty,improvements={},{},{}
for row in GameInfo.TypeTags()do
 if row.Tag=='CLASS_CSC_TAILORS_BASE' or row.Tag=='CLASS_CSC_TAILORS_SPEC'then
  local r=GameInfo.Resources[row.Type]
  if r then
   local class=row.Tag=='CLASS_CSC_TAILORS_BASE'and base or specialty
   class[r.Index]=true
  end
 end
end
for row in GameInfo.Improvement_ValidResources()do
 local r,i=GameInfo.Resources[row.ResourceType],GameInfo.Improvements[row.ImprovementType]
 if r and i and (base[r.Index] or specialty[r.Index])then
  local list=improvements[r.Index]or{}
  list[#list+1]=i.Index;improvements[r.Index]=list
 end
end
local function compatible(plot,wanted)
 local list=improvements[plot:GetResourceType()]or{}
 for _,index in ipairs(list)do if index==wanted then return index end end
end
local function neighbours(plot)return Map.GetAdjacentPlots(plot:GetX(),plot:GetY())end
local function supplierCandidate(plot,pid,class)
 if plot:GetOwner()~=pid or not class[plot:GetResourceType()] or plot:GetDistrictType()~=-1 then return false end
 local current=plot:GetImprovementType()
 if current>=0 then return compatible(plot,current) and not plot:IsImprovementPillaged() end
 for _,index in ipairs(improvements[plot:GetResourceType()]or{}) do
  if ImprovementBuilder.CanHaveImprovement(plot,index,pid)then return true end
 end
 return false
end
local function owns(plot,pid,id)
 local owner=plot:GetOwner()==pid and Cities.GetPlotPurchaseCity(plot)
 return owner and owner:GetID()==id
end
local function empty(plot)
 -- The stock Wonder query decides whether an ordinary improvement can be
 -- covered. Supplier plots are out of scope and keep their actual deposits.
 return plot:GetDistrictType()==-1 and plot:GetResourceType()==-1
end
local function workingQuarter(city,plot)
 local d=city:GetDistricts():GetDistrict(quarter.Index)
 return d and d:IsComplete() and not d:IsPillaged() and d:GetX()==plot:GetX() and d:GetY()==plot:GetY()
end
local function quarterHost(plot,pid)
 local city=plot:GetOwner()==pid and Cities.GetPlotPurchaseCity(plot)
 if city and city:GetOwner()==pid then return city end
end
local function emit(name,...)
 local values={...};for i=1,#values do values[i]=tostring(values[i])end
 print('CSC_WONDER_FIXTURE_'..name..'\t'..table.concat(values,'\t'))
end

local function unlocks(wonder)
 local civic=wonder.PrereqCivic and GameInfo.Civics[wonder.PrereqCivic]
 local tech=wonder.PrereqTech and GameInfo.Technologies[wonder.PrereqTech]
 return civic,tech
end
local function isUnlocked(player,wonder)
 local civic,tech=unlocks(wonder)
 return (not civic or player:GetCulture():HasCivic(civic.Index))
  and (not tech or player:GetTechs():HasTech(tech.Index))
end

if CSC_WONDER_FIXTURE_MODE=='scout'then
 -- Every proposed venue must already be legal for the real Wonder. Prefer
 -- natural suppliers and an existing Tailors before considering fixture edits.
 local wonders={}
 for row in GameInfo.CSC_QuarterWonderSales()do
  local definition=GameInfo.Buildings[row.BuildingType]
  if row.QuarterKey=='TAILORS' and row.ProducerStage==4 and definition then
   wonders[#wonders+1]=definition
  end
 end
 local available={}
 for _,wonder in ipairs(wonders)do
  local built=false
  for _,pid in ipairs(PlayerManager.GetAliveMajorIDs())do
   for _,city in Players[pid]:GetCities():Members()do
    if city:GetBuildings():HasBuilding(wonder.Index)then built=true;break end
   end
   if built then break end
  end
  if not built then available[#available+1]=wonder end
 end
 local width,height=Map.GetGridSize()
 for i=0,width*height-1 do
  local plot=Map.GetPlotByIndex(i);local pid=plot:GetOwner()
  if pid>=1 and pid<=5 and empty(plot) then
   local city=Cities.GetPlotPurchaseCity(plot)
   local id=city and city:GetID()
   local legal={}
   if id then for _,wonder in ipairs(available)do
    if plot:CanHaveWonder(wonder.Index,pid,id)then legal[#legal+1]=wonder end
   end end
   if #legal>0 then
    for _,q in ipairs(neighbours(plot))do
     -- A Tailors in a neighboring city of the same player can trade with
     -- this Wonder. Check capacity and production in the Quarter's city.
     local host=quarterHost(q,pid)
     local existing=q:GetDistrictType()==quarter.Index
     local usable=host and existing and workingQuarter(host,q)
     if host and not host:GetDistricts():HasDistrict(quarter.Index) and empty(q) then
      -- This is the UI queue. CurrentlyBuilding is available in Gameplay.
      local item=host:GetBuildQueue():GetCurrentProductionTypeHash()
      usable=not GameInfo.Districts[item or -1] and q:CanHaveDistrict(quarter.Index,pid,host:GetID())
     end
     if usable then
      for _,sup in ipairs(neighbours(q))do
       if sup:GetIndex()~=i and supplierCandidate(sup,pid,base)then
        for _,spec in ipairs(neighbours(q))do
         if spec:GetIndex()~=i and spec:GetIndex()~=sup:GetIndex() and supplierCandidate(spec,pid,specialty)then
          local working=(sup:GetImprovementType()>=0 and 1 or 0)+(spec:GetImprovementType()>=0 and 1 or 0)
          for _,wonder in ipairs(legal)do
           emit('POTENTIAL',pid,id,i,q:GetIndex(),sup:GetIndex(),spec:GetIndex(),existing and 1 or 0,
             working,isUnlocked(Players[pid],wonder) and 1 or 0,wonder.Index,city:GetName())
          end
         end
        end
       end
      end
     end
    end
   end
  end
 end
 emit('SCOUT_END',Game.GetCurrentGameTurn(),#available)
 return
end

local f=assert(CSC_WONDER_FIXTURE_TARGET)
local wonder=assert(GameInfo.Buildings[f.wonder])
local player=assert(Players[f.player])
local city=assert(CityManager.GetCity(f.player,f.city))
local site=assert(Map.GetPlotByIndex(f.site))
local q=assert(Map.GetPlotByIndex(f.quarter))
local sourceCity=assert(quarterHost(q,f.player))
local supplier=assert(Map.GetPlotByIndex(f.supplier))
local special=assert(Map.GetPlotByIndex(f.specialty))
local function adjacent(a,b)
 return Map.GetPlotDistance(a:GetX(),a:GetY(),b:GetX(),b:GetY())==1
end
local function workingBuilding(definition,where)
 local buildings=sourceCity:GetBuildings()
 return buildings:HasBuilding(definition.Index) and not buildings:IsPillaged(definition.Index)
  and buildings:GetBuildingLocation(definition.Index)==where
end
if CSC_WONDER_FIXTURE_MODE=='outcome'then
 local buildings=city:GetBuildings()
 local completed=buildings:HasBuilding(wonder.Index)
 local location=completed and buildings:GetBuildingLocation(wonder.Index)or -1
 local transaction
 for row in GameInfo.CSC_BuildingTransactions()do
  if row.SourceBuildingType==producer.BuildingType and row.PartnerBuildingType==wonder.BuildingType then transaction=row end
 end
 assert(transaction,'Missing loaded Fashion House/Wonder exchange')
 -- The producer property can include other adjacent customers. The Wonder's
 -- property is unique to its building type. Record both totals alongside
 -- the quantity implied by this exact physical link and the authored rule.
 local sourceReturn,partnerReturn,linkSource,linkPartner=0,0,0,0
 local functioning=workingBuilding(producer,f.quarter) and workingQuarter(sourceCity,q)
 local linked=completed and functioning and adjacent(q,assert(Map.GetPlotByIndex(location)))
 local quantity=linked and math.floor(city:GetPopulation()/transaction.PopulationStep)*transaction.QuantityAmount or 0
 for leg in GameInfo.CSC_BuildingTransactionYields()do
  if leg.TransactionId==transaction.TransactionId then
   local prop=leg.AmountProperty
   if prop and leg.Recipient=='SOURCE'then
    sourceReturn=sourceCity:GetProperty(prop)or 0
    linkSource=quantity*leg.AmountPerUnit
   elseif prop and leg.Recipient=='PARTNER'then
    partnerReturn=city:GetProperty(prop)or 0
    linkPartner=quantity*leg.AmountPerUnit
   end
  end
 end
 emit('OUTCOME',Game.GetCurrentGameTurn(),completed,location,functioning,sourceReturn,partnerReturn,
   city:GetPopulation(),linkSource,linkPartner)
 return
end
if CSC_WONDER_FIXTURE_MODE=='verify'then
 assert(owns(site,f.player,f.city)and empty(site))
 assert(site:CanHaveWonder(wonder.Index,f.player,f.city),'Wonder tile fails stock placement API')
 assert(workingQuarter(sourceCity,q)and adjacent(site,q)and adjacent(q,supplier))
 assert(compatible(supplier,supplier:GetImprovementType())and not supplier:IsImprovementPillaged())
 assert(adjacent(q,special) and specialty[special:GetResourceType()]
  and compatible(special,special:GetImprovementType()) and not special:IsImprovementPillaged())
 assert(isUnlocked(player,wonder))
 assert(workingBuilding(producer,f.quarter))
 emit('VERIFIED',Game.GetCurrentGameTurn(),f.player,f.city,f.site,wonder.Index,f.quarter,f.supplier,f.specialty)
 return
end
assert(CSC_WONDER_FIXTURE_MODE=='setup'and Game.GetCurrentGameTurn()==CSC_WONDER_FIXTURE_TURN)
assert(not player:IsHuman()and owns(site,f.player,f.city)and empty(site))
assert(adjacent(site,q)and adjacent(q,supplier)and supplier:GetOwner()==f.player
 and base[supplier:GetResourceType()]and supplier:GetDistrictType()==-1)
assert(adjacent(q,special) and supplierCandidate(special,f.player,specialty))
local function improve(plot)
 local improvement=plot:GetImprovementType()
 if improvement==-1 then
  for _,index in ipairs(improvements[plot:GetResourceType()]or{})do
   if ImprovementBuilder.CanHaveImprovement(plot,index,f.player)
     and (improvement==-1 or index<improvement)then improvement=index end
  end
  assert(compatible(plot,improvement),'No legal mapped supplier improvement')
  ImprovementBuilder.SetImprovementType(plot,improvement,f.player)
 end
 assert(plot:GetImprovementType()==improvement and not plot:IsImprovementPillaged())
 return improvement
end
if f.existing==0 then
 local queue=sourceCity:GetBuildQueue()
 assert(empty(q)and not sourceCity:GetDistricts():HasDistrict(quarter.Index))
 assert(not GameInfo.Districts[queue:CurrentlyBuilding()or -1],'A district is already queued')
 queue:CreateIncompleteDistrict(quarter.Index,f.quarter,100)
end
assert(workingQuarter(sourceCity,q))
local improvement=improve(supplier)
improve(special)
-- Both arms start with the same functioning producer. Its future exchange
-- depends on where the AI chooses to build the Wonder and whether it finishes.
for _,building in ipairs({workshop,producer})do
 if not workingBuilding(building,f.quarter)then
  assert(not sourceCity:GetBuildings():HasBuilding(building.Index),'Fixture only adds missing producers')
  sourceCity:GetBuildQueue():CreateBuilding(building.Index,f.quarter)
 end
 assert(workingBuilding(building,f.quarter),'Fixture producer unavailable')
end
local civic,tech=unlocks(wonder)
if civic and not player:GetCulture():HasCivic(civic.Index)then player:GetCulture():SetCivic(civic.Index,true)end
if tech and not player:GetTechs():HasTech(tech.Index)then player:GetTechs():SetTech(tech.Index,true)end
assert(isUnlocked(player,wonder))

-- Both arms run the production adapter, then the diagnostic wrapper limits
-- delivery to one exact live offer in ON. Neither arm orders the Wonder.
local E=assert(CSC_AI_EconomyAdapters)
local collect=E.WonderOffers
local function targeted(offers)
 for _,offer in ipairs(offers)do
  if offer.player==f.player and offer.city==f.city and offer.building==wonder.Index and offer.plot==f.site then
   return offer
  end
 end
end
local p=assert(CSC_AI_QuarterPlacement)
local chains=p.ReadChains(player)
for _,chain in ipairs(chains)do
 if chain.plot:GetIndex()==f.quarter then
  emit('CHAIN',f.quarter,chain.ready,#chain.supply.base,#chain.supply.specialty,chain.workingBase,improvement)
 end
end
local offer=assert(targeted(collect(player,chains,{},128,6144)),'No production Wonder offer for fixture')
emit('OFFER',Game.GetCurrentGameTurn(),offer.player,offer.city,offer.plot,offer.building,offer.deltaQ8)
local on=CSC_WONDER_FIXTURE_ENABLED
E.WonderOffers=function(active,...)
 if active:GetID()~=f.player then return {}end
 local selected=targeted(collect(active,...))
 if not selected then return {}end
 emit('PUBLICATION',Game.GetCurrentGameTurn(),selected.player,selected.city,selected.plot,selected.building,selected.deltaQ8,on and 1 or 0)
 return on and {selected}or{}
end
emit('SETUP_END',Game.GetCurrentGameTurn())
