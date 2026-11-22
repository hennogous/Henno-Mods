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

if CSC_WONDER_FIXTURE_MODE=='hagmatana'then
 -- This is the observed stock footprint before Broadway contract 2944.
 -- The reload can change an earlier Theater order or the Mass Media clock.
 -- Record a legal owned Theater footprint if the district is still missing.
 -- Both copies get the same prerequisites; the AI owns the Wonder order.
 local pid,id,siteIndex,quarterIndex=3,262147,1354,1428
 local city=assert(CityManager.GetCity(pid,id))
 local site=assert(Map.GetPlotByIndex(siteIndex))
 local q=assert(Map.GetPlotByIndex(quarterIndex))
 local broadway=assert(GameInfo.Buildings.BUILDING_BROADWAY)
 assert(owns(site,pid,id) and empty(site) and workingQuarter(city,q))
 assert(Map.GetPlotDistance(site:GetX(),site:GetY(),q:GetX(),q:GetY())==1)
 local theater=assert(GameInfo.Districts[broadway.AdjacentDistrict])
 local theaterPlot=-1
 local candidate
 local district=city:GetDistricts():GetDistrict(theater.Index)
 for _,tile in ipairs(neighbours(site))do
  if owns(tile,pid,id)then
   if district and tile:GetX()==district:GetX() and tile:GetY()==district:GetY()
    and district:IsComplete() and not district:IsPillaged()then
    theaterPlot=tile:GetIndex();break
   end
   if not district and tile:GetIndex()~=quarterIndex and empty(tile) and tile:CanHaveDistrict(theater.Index,pid,id)then
    -- Keep the Quarter's own material ring free whenever possible.
    local shared=Map.GetPlotDistance(tile:GetX(),tile:GetY(),q:GetX(),q:GetY())==1
    local rank=(shared and 10000 or 0)+tile:GetIndex()
    if not candidate or rank<candidate.rank then candidate={plot=tile:GetIndex(),rank=rank}end
   end
  end
 end
 local unlocked=isUnlocked(assert(Players[pid]),broadway)
 local legal=site:CanHaveWonder(broadway.Index,pid,id)
 emit('HAGMATANA_SCOUT',Game.GetCurrentGameTurn(),siteIndex,site:GetTerrainType(),theaterPlot,
  candidate and candidate.plot or -1,unlocked,legal)
 assert(theaterPlot>=0 or candidate,'Hagmatana has no legal adjacent Theater footprint')
 emit('HAGMATANA',Game.GetCurrentGameTurn(),pid,id,siteIndex,quarterIndex,broadway.Index,
  theaterPlot>=0 and theaterPlot or candidate.plot)
 return
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
local supplier=f.supplier and Map.GetPlotByIndex(f.supplier)
local special=f.specialty and Map.GetPlotByIndex(f.specialty)
local function adjacent(a,b)
 return Map.GetPlotDistance(a:GetX(),a:GetY(),b:GetX(),b:GetY())==1
end
local function workingBuilding(definition,where)
 local buildings=sourceCity:GetBuildings()
 return buildings:HasBuilding(definition.Index) and not buildings:IsPillaged(definition.Index)
  and buildings:GetBuildingLocation(definition.Index)==where
end
if CSC_WONDER_FIXTURE_MODE=='outcome' or CSC_WONDER_FIXTURE_MODE=='watch'then
 local transaction
 for row in GameInfo.CSC_BuildingTransactions()do
  if row.SourceBuildingType==producer.BuildingType and row.PartnerBuildingType==wonder.BuildingType then transaction=row end
 end
 assert(transaction,'Missing loaded Fashion House/Wonder exchange')
 local legs={}
 for leg in GameInfo.CSC_BuildingTransactionYields()do
  if leg.TransactionId==transaction.TransactionId and leg.AmountProperty then legs[leg.Recipient]=leg end
 end
 local sourceLeg,partnerLeg=assert(legs.SOURCE),assert(legs.PARTNER)
 local function outcome()
  local buildings=city:GetBuildings()
  local completed=buildings:HasBuilding(wonder.Index)
  local location=completed and buildings:GetBuildingLocation(wonder.Index)or -1
  local functioning=workingBuilding(producer,f.quarter) and workingQuarter(sourceCity,q)
  local linked=completed and functioning and adjacent(q,assert(Map.GetPlotByIndex(location)))
  local pop=city:GetPopulation()
  local quantity=linked and math.floor(pop/transaction.PopulationStep)*transaction.QuantityAmount or 0
  -- The producer total can include other customers. The partner property
  -- belongs to this Wonder type. Compare with the exact link's entitlement.
  return completed,location,functioning,sourceCity:GetProperty(sourceLeg.AmountProperty)or 0,
   city:GetProperty(partnerLeg.AmountProperty)or 0,pop,quantity*sourceLeg.AmountPerUnit,quantity*partnerLeg.AmountPerUnit
 end
 if CSC_WONDER_FIXTURE_MODE=='watch'then
  -- Diagnostic-only and exact-site. The native district placeholder can
  -- exist before the Wonder building. Keep foundation and payment separate.
  assert(not CSC_WonderFixtureWatchInstalled,'Wonder watcher already installed')
  CSC_WonderFixtureWatchInstalled=true
  local placeholder=assert(GameInfo.Districts.DISTRICT_WONDER).Index
  GameEvents.OnGameTurnStarted.Add(function()
   emit('WATCH',Game.GetCurrentGameTurn(),site:GetDistrictType()==placeholder,outcome())
  end)
  emit('WATCH_INSTALLED',Game.GetCurrentGameTurn())
 else
  emit('OUTCOME',Game.GetCurrentGameTurn(),outcome())
 end
 return
end
if CSC_WONDER_FIXTURE_MODE=='verify'then
 assert(owns(site,f.player,f.city)and empty(site),'Wonder tile lost its owner or became occupied')
 assert(site:CanHaveWonder(wonder.Index,f.player,f.city),'Wonder tile fails stock placement API')
 assert(workingQuarter(sourceCity,q)and adjacent(site,q)and adjacent(q,supplier),'Wonder supply geometry changed')
 assert(compatible(supplier,supplier:GetImprovementType())and not supplier:IsImprovementPillaged(),
  'Base supplier failed the placement readback')
 assert(adjacent(q,special) and specialty[special:GetResourceType()]
  and compatible(special,special:GetImprovementType()) and not special:IsImprovementPillaged(),
  'Specialty supplier failed the placement readback')
 -- PlotInfo owns native site legality. Gameplay already read back both
 -- the unlock and the working Fashion House in its synchronous setup.
 emit('VERIFIED',Game.GetCurrentGameTurn(),f.player,f.city,f.site,wonder.Index,f.quarter,f.supplier,f.specialty)
 return
end
assert(CSC_WONDER_FIXTURE_MODE=='setup'and Game.GetCurrentGameTurn()==CSC_WONDER_FIXTURE_TURN)
assert(not player:IsHuman()and owns(site,f.player,f.city)and empty(site))
if CSC_WONDER_STOCK_HAGMATANA then
 local theater=assert(GameInfo.Districts[wonder.AdjacentDistrict])
 local theaterTile=assert(Map.GetPlotByIndex(f.theater))
 assert(owns(theaterTile,f.player,f.city) and adjacent(site,theaterTile))
 local district=city:GetDistricts():GetDistrict(theater.Index)
 if not district then
  assert(empty(theaterTile),'Theater fixture footprint was occupied')
  city:GetBuildQueue():CreateIncompleteDistrict(theater.Index,f.theater,100)
  district=city:GetDistricts():GetDistrict(theater.Index)
  emit('THEATER_ADDED',f.theater)
 end
 assert(district and district:IsComplete() and not district:IsPillaged()
  and district:GetX()==theaterTile:GetX() and district:GetY()==theaterTile:GetY(),
  'Matched Theater preparation failed')
 -- The stock city had neither supplier class. Prefer untouched vacant land.
 -- When that cannot host two suppliers, prepare two matched land plots in
 -- this disposable fixture. The Wonder and Theater tiles stay untouched.
 local function legalResource(plot,class)
  for row in GameInfo.Resources()do
   if class[row.Index] and ResourceBuilder.CanHaveResource(plot,row.Index)then
    ResourceBuilder.SetResourceType(plot,row.Index,1)
    local legal=false
    for _,index in ipairs(improvements[row.Index]or{})do
     legal=legal or ImprovementBuilder.CanHaveImprovement(plot,index,f.player)
    end
    ResourceBuilder.SetResourceType(plot,-1)
    if legal then return row.Index end
   end
  end
 end
 local baseTiles,specTiles,eligible={},{},{}
 for _,tile in ipairs(neighbours(q))do
  local feature=GameInfo.Features[tile:GetFeatureType()]
  local landmark=feature and (feature.NaturalWonder==true or feature.NaturalWonder==1)
  if tile:GetIndex()~=f.site and tile:GetOwner()==f.player and tile:GetDistrictType()==-1
   and not tile:IsWater() and not tile:IsMountain() and not landmark then
   local res,imp=tile:GetResourceType(),tile:GetImprovementType()
   eligible[#eligible+1]={plot=tile,rank=(res>=0 and 20000 or 0)+(imp>=0 and 10000 or 0)+tile:GetIndex()}
   emit('SUPPLIER_TERRAIN',tile:GetIndex(),tile:GetTerrainType(),tile:GetFeatureType(),res,imp)
   if res==-1 and imp==-1 then
    local b=legalResource(tile,base)
    local s=legalResource(tile,specialty)
    if b then baseTiles[#baseTiles+1]={tile,b}end
    if s then specTiles[#specTiles+1]={tile,s}end
   end
  end
 end
 local b,s
 for _,first in ipairs(baseTiles)do
  for _,second in ipairs(specTiles)do
   if first[1]:GetIndex()~=second[1]:GetIndex() then b,s=first,second;break end
  end
  if b then break end
 end
 if not b then
  table.sort(eligible,function(a,c)return a.rank<c.rank end)
  assert(#eligible>=2,'Hagmatana needs two distinct owned land plots for the fixture')
  local function prepareSupplier(tile,terrain,resource,class)
   local res=assert(GameInfo.Resources[resource]).Index
   assert(class[res],'Fixture resource is absent from the loaded supplier class')
   if tile:GetImprovementType()>=0 then ImprovementBuilder.SetImprovementType(tile,-1,f.player)end
   if tile:GetResourceType()>=0 then ResourceBuilder.SetResourceType(tile,-1)end
   if tile:GetFeatureType()>=0 then TerrainBuilder.SetFeatureType(tile,-1)end
   TerrainBuilder.SetTerrainType(tile,assert(GameInfo.Terrains[terrain]).Index)
   assert(ResourceBuilder.CanHaveResource(tile,res),'Engine rejected the prepared supplier terrain')
   emit('SUPPLIER_PREPARED',tile:GetIndex(),terrain,resource)
   return {tile,res}
  end
  b=prepareSupplier(eligible[1].plot,'TERRAIN_PLAINS','RESOURCE_CSC_FLAX',base)
  s=prepareSupplier(eligible[2].plot,'TERRAIN_DESERT_HILLS','RESOURCE_SILVER',specialty)
 end
 supplier,special=b[1],s[1]
 ResourceBuilder.SetResourceType(supplier,b[2],1)
 ResourceBuilder.SetResourceType(special,s[2],1)
 f.supplier,f.specialty=supplier:GetIndex(),special:GetIndex()
 emit('SEEDED',f.supplier,f.specialty,b[2],s[2])
end
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
if CSC_WONDER_STOCK_HAGMATANA then
 -- The stock pre-roll leaves this Gameplay context's publisher dormant.
 -- Its first real publication initializes the loaded tag definitions.
 -- Do the same read-only initialization for the pre-publication check.
 CSC_Adjacency.Initialize()
 for _,tile in ipairs({supplier,special})do
  local res=tile:GetResourceType()
  emit('SUPPLIER_READY',tile:GetIndex(),res,tile:GetImprovementType(),
   PlayersVisibility[f.player]:IsRevealed(tile:GetX(),tile:GetY()),CSC_Adjacency.ResourceVisible(f.player,res))
 end
end
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
if CSC_WONDER_STOCK_HAGMATANA then assert(CSC_WonderFixtureActivatePublisher)(assert(CSC_WONDER_ORIGINAL_AI)) end
emit('SETUP_END',Game.GetCurrentGameTurn())
