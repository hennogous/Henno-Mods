-- Diagnostic only: shared-controller saved-world query, never live AI policy.
-- Live map facts -> the existing CSC supply/adjacency readers -> tabular output.
-- Native current target lists stay separate from future actor/type geometry;
-- neither changes a district score or consumes a planning packet. The companion
-- Python driver verifies the unchanged world and zero elapsed turns.
-- BASE paths are broad geometric candidates, not promises of legal construction:
-- a land tile can contain a resource/district or lie outside a city's radius.
-- PAIR adds ownership, native eligibility, supply, local Mill rating and Harbor
-- state. MAP identifies sea versus lake and occupied footprints for analysis.
-- No bids, RNG, orders or property writes.
local A=assert(CSC_Adjacency)
local P=assert(CSC_AI_QuarterPlacement)
local ui=assert(ExposedMembers.CSC_Adjacency)
local profile
for _,p in ipairs(P.StageTwoProfiles())do if p.key=='TAILORS'then profile=p end end
assert(profile)
local qdef=profile.district
local function emit(kind,...)
 local fields={...};for i,v in ipairs(fields)do fields[i]=tostring(v):gsub('[\r\n\t]',' ')end
 print('CSC_COAST_'..kind..'\t'..table.concat(fields,'\t'))
end
local function list(materials)local t={};for _,m in ipairs(materials)do t[#t+1]=m.plot end;table.sort(t);return table.concat(t,',')end
local function workingCount(materials)local n=0;for _,m in ipairs(materials)do if m.working then n=n+1 end end;return n end
local function name(city)return Locale and Locale.Lookup and Locale.Lookup(city:GetName())or city:GetName()end
local quarterType=qdef.Index
local width,height=Map.GetGridSize()
emit('META',Game.GetCurrentGameTurn(),quarterType,width,height)
-- The empty inventory proxy isolates permanent actor/type restrictions from
-- already-built districts. It is only a future-type filter; it does not make
-- the live CanHaveDistrict/current target checks counterfactual. Keep those
-- fields separate when interpreting a candidate with an existing Quarter.
local emptyCity={GetDistricts=function()return{GetNumDistricts=function()return 0 end,GetDistrictByIndex=function()end}end}
local harborFamily={DISTRICT_HARBOR=true}
for r in GameInfo.DistrictReplaces()do if r.ReplacesDistrictType=='DISTRICT_HARBOR'then harborFamily[r.CivUniqueDistrictType]=true end end
local lights={GameInfo.Buildings.BUILDING_LIGHTHOUSE}
for r in GameInfo.BuildingReplaces()do if r.ReplacesBuildingType=='BUILDING_LIGHTHOUSE'then lights[#lights+1]=GameInfo.Buildings[r.CivUniqueBuildingType]end end
local rawBases,nearWater=0,0
for index=0,Map.GetPlotCount()-1 do
 local material=Map.GetPlotByIndex(index);local resource=GameInfo.Resources[material:GetResourceType()]
 if resource and A.HasTag(profile.base,resource.ResourceType)then
  rawBases=rawBases+1;local paths={}
  for _,q in ipairs(Map.GetAdjacentPlots(material:GetX(),material:GetY()))do
   if not q:IsWater()and not q:IsImpassable()then
    for _,water in ipairs(Map.GetAdjacentPlots(q:GetX(),q:GetY()))do if water:IsWater()then
     paths[#paths+1]=q:GetIndex()..':'..water:GetIndex()
    end end
   end
  end
  if #paths>0 then nearWater=nearWater+1 end
  emit('BASE',index,resource.ResourceType,material:GetOwner(),material:GetX(),material:GetY(),#paths,table.concat(paths,','))
 end
end
emit('BASE_TOTAL',rawBases,nearWater)
-- Default study population: the five original AI seats, excluding observer0.
-- For another player layout, supply an explicitly scoped --query to the driver.
for pid=1,5 do
 local player=Players[pid]
 if player and player:IsAlive()then
  local naval=GameInfo.Civics.CIVIC_NAVAL_TRADITION
  local config=PlayerConfigurations[pid]
  emit('PLAYER',pid,config:GetCivilizationTypeName(),config:GetLeaderTypeName(),naval and player:GetCulture():HasCivic(naval.Index)or false)
  local permanent=assert(CSC_AI_FutureDistrictTypes(pid,emptyCity))
  local harbors={}
  for d in GameInfo.Districts()do if harborFamily[d.DistrictType]then harbors[#harbors+1]=d end end
  table.sort(harbors,function(a,b)return a.Index<b.Index end)
  local cities={}
  for _,city in player:GetCities():Members()do cities[#cities+1]=city end
  -- Diagnostic-only quote cache for one unchanged saved world. Native ordinary
  -- Harbor Gold is kept separate from the private placement yield and from a
  -- hypothetical future Quarter. No native score or gameplay state is written.
  local gold,legalCache,bestGold={},{},{}
  local function harborGold(city,definition,index)
   local key=city:GetID()..':'..definition.Index..':'..index
   if gold[key]~=nil then return gold[key]or nil end
   local record=ui.GetDistrictAdjacency(pid,city:GetID(),index,definition.Index)
   local amount=record and record.available and record.yields and record.yields.YIELD_GOLD
   if type(amount)~='number'then amount=nil end
   gold[key]=amount~=nil and amount or false;return amount
  end
  local function harborTargets(city,definition)
   local key=city:GetID()..':'..definition.Index
   if not legalCache[key]then
    local set={};legalCache[key]=set
    for _,index in ipairs(ui.GetLegalDistrictTargets(pid,city:GetID(),definition.Hash)or{})do
     set[index]=true
     local amount=harborGold(city,definition,index)
     if amount~=nil then bestGold[key]=math.max(bestGold[key]or-math.huge,amount)end
    end
   end
   return legalCache[key],bestGold[key]
  end
  for _,city in ipairs(cities)do
   local id=city:GetID();local ds=city:GetDistricts();local hasQ=ds:HasDistrict(quarterType)
   local quarterLegal={};for _,plot in ipairs(ui.GetLegalDistrictTargets(pid,id,qdef.Hash)or{})do quarterLegal[plot]=true end
   local cap=ui.GetDistrictCapacity and ui.GetDistrictCapacity(pid,id)or{}
   emit('CITY',pid,id,name(city),city:GetX(),city:GetY(),city:GetPopulation(),hasQ,cap.used or -1,cap.allowed or -1,player:GetTreasury():GetGoldBalance())
   local currentHarborLegal={}
   for _,harbor in ipairs(harbors)do
    currentHarborLegal[harbor.Index]=harborTargets(city,harbor)
   end
   local center=Map.GetPlot(city:GetX(),city:GetY())
   for _,q in ipairs(A.PlotsInBand(center,1,3))do
    local owner=q:GetOwner();local assigned=owner==pid and Cities.GetPlotPurchaseCity(q)
    local owned=assigned and assigned:GetID()==id
    local placed=owned and q:GetDistrictType()==quarterType
    local vacant=q:GetDistrictType()==-1 and q:GetResourceType()==-1
    if permanent[quarterType]and(owned or owner==-1)and(placed or vacant)
      and PlayersVisibility[pid]:IsRevealed(q:GetX(),q:GetY())then
     local qgeometry=placed or q:CanHaveDistrict(quarterType,pid,id)
     local supply=P.ReadSuppliers(player,q,profile)
     if #supply.base>0 then
      local adjacency=CSC_AI_QuarterAdjacencyValue(qdef.DistrictType,q,city,pid,true)
      local qcount=0
      for _,water in ipairs(Map.GetAdjacentPlots(q:GetX(),q:GetY()))do if water:IsWater()then
       local wowner=water:GetOwner();local buyer=wowner==pid and Cities.GetPlotPurchaseCity(water)
       for _,h in ipairs(harbors)do
        local existing=wowner==pid and water:GetDistrictType()==h.Index
        local available=water:GetDistrictType()==-1 and(wowner==-1 or buyer~=nil)
        if existing or available and permanent[h.Index]then
         local candidates=buyer and{buyer}or cities
         for _,harborCity in ipairs(candidates)do
          local hid=harborCity:GetID()
          if Map.GetPlotDistance(harborCity:GetX(),harborCity:GetY(),water:GetX(),water:GetY())<=3 then
           local hgeometry=existing or water:CanHaveDistrict(h.Index,pid,hid)
           if hgeometry then
            local legal=false
            local legalSet,ordinaryBest=harborTargets(harborCity,h)
            legal=legalSet[water:GetIndex()]or false
            local workingLight=false
            if existing then for _,lighthouse in ipairs(lights)do
             if harborCity:GetBuildings():HasBuilding(lighthouse.Index)
               and not harborCity:GetBuildings():IsPillaged(lighthouse.Index)
               and harborCity:GetBuildings():GetBuildingLocation(lighthouse.Index)==water:GetIndex()then workingLight=true end
            end end
            qcount=qcount+1
            emit('PAIR',pid,id,q:GetIndex(),owned,placed,qgeometry,quarterLegal[q:GetIndex()]or false,
             #supply.base,#supply.specialty,list(supply.base),list(supply.specialty),q:IsRiver(),
             adjacency.current.production+adjacency.current.gold,adjacency.production+adjacency.gold,
             hid,h.Index,water:GetIndex(),wowner,existing,legal,workingLight,
             harborGold(harborCity,h,water:GetIndex())or'UNKNOWN',ordinaryBest or'UNKNOWN',water:IsLake(),
             workingCount(supply.base))
           end
          end
         end
        end
       end
      end end
      if placed then emit('PLACED',pid,id,q:GetIndex(),q:IsCoastalLand(),qcount,#supply.base,#supply.specialty,list(supply.base),list(supply.specialty))end
     end
    end
   end
  end
 end
end
-- Read-only physical map facts for offline obstruction/ownership analysis.
for index=0,Map.GetPlotCount()-1 do
 local p=Map.GetPlotByIndex(index);local city=Cities.GetPlotPurchaseCity(p)
 local terrain=GameInfo.Terrains[p:GetTerrainType()]
 local feature=GameInfo.Features[p:GetFeatureType()]
 local district=GameInfo.Districts[p:GetDistrictType()]
 local resource=GameInfo.Resources[p:GetResourceType()]
 emit('MAP',index,p:GetX(),p:GetY(),terrain and terrain.TerrainType or 'NONE',
  feature and feature.FeatureType or 'NONE',p:IsWater(),p:IsLake(),p:IsImpassable(),
  p:GetOwner(),city and city:GetID()or -1,district and district.DistrictType or 'NONE',
  resource and resource.ResourceType or 'NONE',p:GetImprovementType())
end
emit('END',Game.GetCurrentGameTurn())
