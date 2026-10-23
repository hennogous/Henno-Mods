-- Disposable Medieval research-choice fixture. Never retained in natural play.
local target=GameInfo.Civics.CIVIC_NAVAL_TRADITION.Index
local chosen={}
for pid=1,5 do
 local player=Players[pid]
 assert(not player:IsHuman() and not player:GetCulture():HasCivic(target),'Target must remain unresearched')
 assert(player:GetCulture():HasCivic(GameInfo.Civics.CIVIC_DEFENSIVE_TACTICS.Index),'Target prerequisite missing')
 local center,qp,hp,mp
 for i=0,Map.GetPlotCount()-1 do
  local c=Map.GetPlotByIndex(i)
  if c:GetOwner()==-1 and not c:IsWater() and not c:IsImpassable() and c:GetY()>3 and c:GetY()<42 then
   local separated=true
   for _,old in ipairs(chosen) do if Map.GetPlotDistance(c:GetX(),c:GetY(),old:GetX(),old:GetY())<8 then separated=false end end
   if separated then
    for _,q in ipairs(Map.GetAdjacentPlots(c:GetX(),c:GetY())) do
     if q:GetOwner()==-1 and not q:IsWater() and not q:IsImpassable() then
      for _,h in ipairs(Map.GetAdjacentPlots(c:GetX(),c:GetY())) do
       if h:IsWater() and not h:IsLake() and h:GetOwner()==-1 and Map.GetPlotDistance(q:GetX(),q:GetY(),h:GetX(),h:GetY())==1 then
        for _,m in ipairs(Map.GetAdjacentPlots(c:GetX(),c:GetY())) do
         if m:GetIndex()~=q:GetIndex() and m:GetOwner()==-1 and not m:IsWater() and not m:IsImpassable() and Map.GetPlotDistance(q:GetX(),q:GetY(),m:GetX(),m:GetY())==1 then center,qp,hp,mp=c,q,h,m;break end
        end
       end
       if center then break end
      end
     end
     if center then break end
    end
   end
  end
  if center then break end
 end
 assert(center,'No spaced coastal fixture site for '..pid)
 chosen[#chosen+1]=center
 for _,p in ipairs({center,qp,mp,hp}) do TerrainBuilder.SetFeatureType(p,-1);ResourceBuilder.SetResourceType(p,-1) end
 local city=assert(player:GetCities():Create(center:GetX(),center:GetY()))
 city:ChangePopulation(6-city:GetPopulation())
 assert(qp:GetOwner()==pid and mp:GetOwner()==pid and hp:GetOwner()==pid,'Original city ring ownership')
 TerrainBuilder.SetTerrainType(mp,GameInfo.Terrains.TERRAIN_PLAINS.Index)
 ResourceBuilder.SetResourceType(mp,GameInfo.Resources.RESOURCE_CSC_FLAX.Index,1)
 ImprovementBuilder.SetImprovementType(mp,GameInfo.Improvements.IMPROVEMENT_FARM.Index,pid)
 city:GetBuildQueue():CreateIncompleteDistrict(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index,qp:GetIndex(),100)
 city:GetBuildQueue():CreateIncompleteDistrict(GameInfo.Districts.DISTRICT_HARBOR.Index,hp:GetIndex(),100)
 city:GetBuildQueue():CreateBuilding(GameInfo.Buildings.BUILDING_LIGHTHOUSE.Index,hp:GetIndex())
 city:GetBuildQueue():CreateBuilding(GameInfo.Buildings.BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP.Index,qp:GetIndex())
 assert(city:GetBuildings():HasBuilding(GameInfo.Buildings.BUILDING_LIGHTHOUSE.Index))
 assert(city:GetBuildings():HasBuilding(GameInfo.Buildings.BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP.Index))
 assert(city:GetBuildings():GetBuildingLocation(GameInfo.Buildings.BUILDING_LIGHTHOUSE.Index)==hp:GetIndex())
 assert(city:GetBuildings():GetBuildingLocation(GameInfo.Buildings.BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP.Index)==qp:GetIndex())
 -- Leave native current research untouched; observe later natural completions.
 print('CSC_RESEARCH_FIXTURE',pid,city:GetID(),qp:GetIndex(),mp:GetIndex(),hp:GetIndex(),player:GetCulture():GetProgressingCivic())
end
Game:SetProperty('CSC_RESEARCH_CHOICE_FIXTURE',true)
