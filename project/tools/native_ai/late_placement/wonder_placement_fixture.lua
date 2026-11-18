-- Disposable matched test. The scout reads the stock placement API in
-- PlotInfo. Setup runs separately in Gameplay on the validated save copy.
local quarter=assert(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER)
local wonder=assert(GameInfo.Buildings.BUILDING_BOLSHOI_THEATRE)
local civic=assert(GameInfo.Civics[wonder.PrereqCivic])
local base,improvements={},{}
for row in GameInfo.TypeTags()do
 if row.Tag=='CLASS_CSC_TAILORS_BASE'then
  local r=GameInfo.Resources[row.Type]
  if r then base[r.Index]=true end
 end
end
for row in GameInfo.Improvement_ValidResources()do
 local r,i=GameInfo.Resources[row.ResourceType],GameInfo.Improvements[row.ImprovementType]
 if r and i and base[r.Index]then
  local list=improvements[r.Index]or{}
  list[#list+1]=i.Index;improvements[r.Index]=list
 end
end
local function compatible(plot,wanted)
 local list=improvements[plot:GetResourceType()]or{}
 for _,index in ipairs(list)do if index==wanted then return index end end
end
local function neighbours(plot)return Map.GetAdjacentPlots(plot:GetX(),plot:GetY())end
local function owns(plot,pid,id)
 local owner=plot:GetOwner()==pid and Cities.GetPlotPurchaseCity(plot)
 return owner and owner:GetID()==id
end
local function empty(plot)
 return plot:GetDistrictType()==-1 and plot:GetResourceType()==-1 and plot:GetImprovementType()==-1
end
local function workingQuarter(city,plot)
 local d=city:GetDistricts():GetDistrict(quarter.Index)
 return d and d:IsComplete() and not d:IsPillaged() and d:GetX()==plot:GetX() and d:GetY()==plot:GetY()
end
local function emit(name,...)
 local values={...};for i=1,#values do values[i]=tostring(values[i])end
 print('CSC_WONDER_FIXTURE_'..name..'\t'..table.concat(values,'\t'))
end

if CSC_WONDER_FIXTURE_MODE=='scout'then
 -- Every proposed venue must already be legal for the real Wonder. Prefer
 -- natural suppliers and an existing Tailors before considering fixture edits.
 local width,height=Map.GetGridSize()
 local byPlayer={}
 for _,pid in ipairs({1,2,3,4,5})do byPlayer[pid]=Players[pid]:GetCulture():HasCivic(civic.Index)end
 for i=0,width*height-1 do
  local plot=Map.GetPlotByIndex(i);local pid=plot:GetOwner()
  if byPlayer[pid]~=nil and empty(plot) then
   local city=Cities.GetPlotPurchaseCity(plot)
   local id=city and city:GetID()
   if id and plot:CanHaveWonder(wonder.Index,pid,id) then
    -- The stock UI build queue exposes the current item by hash. The
    -- gameplay queue's CurrentlyBuilding method is used only for edits.
    local item=city:GetBuildQueue():GetCurrentProductionTypeHash()
    for _,q in ipairs(neighbours(plot))do
     local existing=q:GetDistrictType()==quarter.Index
     local usable=existing and workingQuarter(city,q)
     if not city:GetDistricts():HasDistrict(quarter.Index) and empty(q) and owns(q,pid,id)
      and not GameInfo.Districts[item or -1] then
      usable=q:CanHaveDistrict(quarter.Index,pid,id)
     end
     if usable then
      for _,sup in ipairs(neighbours(q))do
       if sup:GetIndex()~=i and sup:GetOwner()==pid and base[sup:GetResourceType()]
        and sup:GetDistrictType()==-1 and (sup:GetImprovementType()==-1
          or compatible(sup,sup:GetImprovementType()) and not sup:IsImprovementPillaged())then
        local isWorking=compatible(sup,sup:GetImprovementType())
        emit('POTENTIAL',pid,id,i,q:GetIndex(),sup:GetIndex(),existing and 1 or 0,
          isWorking and 1 or 0,byPlayer[pid]and 1 or 0,city:GetName())
       end
      end
     end
    end
   end
  end
 end
 emit('SCOUT_END',Game.GetCurrentGameTurn(),wonder.Index)
 return
end

local f=assert(CSC_WONDER_FIXTURE_TARGET)
local player=assert(Players[f.player])
local city=assert(CityManager.GetCity(f.player,f.city))
local site=assert(Map.GetPlotByIndex(f.site))
local q=assert(Map.GetPlotByIndex(f.quarter))
local supplier=assert(Map.GetPlotByIndex(f.supplier))
local function adjacent(a,b)
 return Map.GetPlotDistance(a:GetX(),a:GetY(),b:GetX(),b:GetY())==1
end
if CSC_WONDER_FIXTURE_MODE=='verify'then
 assert(owns(site,f.player,f.city)and empty(site))
 assert(site:CanHaveWonder(wonder.Index,f.player,f.city),'Wonder tile fails stock placement API')
 assert(workingQuarter(city,q)and adjacent(site,q)and adjacent(q,supplier))
 assert(compatible(supplier,supplier:GetImprovementType())and not supplier:IsImprovementPillaged())
 assert(player:GetCulture():HasCivic(civic.Index))
 emit('VERIFIED',Game.GetCurrentGameTurn(),f.player,f.city,f.site,wonder.Index,f.quarter,f.supplier)
 return
end
assert(CSC_WONDER_FIXTURE_MODE=='setup'and Game.GetCurrentGameTurn()==200)
assert(not player:IsHuman()and owns(site,f.player,f.city)and empty(site))
assert(adjacent(site,q)and adjacent(q,supplier)and supplier:GetOwner()==f.player
 and base[supplier:GetResourceType()]and supplier:GetDistrictType()==-1)
local improvement=supplier:GetImprovementType()
if improvement==-1 then
 for _,index in ipairs(improvements[supplier:GetResourceType()]or{})do
  if ImprovementBuilder.CanHaveImprovement(supplier,index,f.player)
    and (improvement==-1 or index<improvement)then improvement=index end
 end
end
assert(compatible(supplier,improvement),'No legal mapped supplier improvement')
if f.existing==0 then
 local queue=city:GetBuildQueue()
 assert(empty(q)and owns(q,f.player,f.city)and not city:GetDistricts():HasDistrict(quarter.Index))
 assert(not GameInfo.Districts[queue:CurrentlyBuilding()or -1],'A district is already queued')
 queue:CreateIncompleteDistrict(quarter.Index,f.quarter,100)
end
assert(workingQuarter(city,q))
if supplier:GetImprovementType()==-1 then
 ImprovementBuilder.SetImprovementType(supplier,improvement,f.player)
end
assert(supplier:GetImprovementType()==improvement and not supplier:IsImprovementPillaged())
if not player:GetCulture():HasCivic(civic.Index)then player:GetCulture():SetCivic(civic.Index,true)end
assert(player:GetCulture():HasCivic(civic.Index))

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
  emit('CHAIN',f.quarter,chain.ready,#chain.supply.base,chain.workingBase,improvement)
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
