-- Read-only bonus/river native adjacency diagnostics. Never mutate the map.
local y=assert(GameInfo.Yields['YIELD_CSC_AI_PLACEMENT']).Index
local result={turn=Game.GetCurrentGameTurn(),rows={},human={},isolated_checks=0,isolated_matches=0,errors={}}
local function tagged(resource,tag)
 for r in GameInfo.TypeTags() do if r.Type==resource and r.Tag==tag then return true end end
 return false
end
for _,player in ipairs(PlayerManager.GetAliveMajors()) do
 local pid=player:GetID();result.human[#result.human+1]={player=pid,human=player:IsHuman()}
 for _,city in player:GetCities():Members() do
  for _,index in ipairs(Map.GetCityPlots():GetPurchasedPlots(city)) do
   local p=Map.GetPlotByIndex(index)
   if p:GetOwner()==pid and not p:IsWater() and not p:IsImpassable() and p:GetDistrictType()==-1
      and Map.GetPlotDistance(city:GetX(),city:GetY(),p:GetX(),p:GetY())<=3 then
    for q,dt in pairs({BAKERS='DISTRICT_CSC_BAKERS_QUARTER',TAILORS='DISTRICT_CSC_TAILORS_QUARTER'}) do
     local row={player=pid,city=city:GetID(),quarter=q,plot=index,bonus=0,bonus_owned=0,bonus_mapped=0,
       base=0,spec=0,river=p:IsRiver(),adjacent_districts=0}
     for direction=0,5 do
      local n=Map.GetAdjacentPlot(p:GetX(),p:GetY(),direction)
      if n then
       local resource=GameInfo.Resources[n:GetResourceType()]
       if resource then
        local base=tagged(resource.ResourceType,'CLASS_CSC_'..q..'_BASE')
        if resource.ResourceClassType=='RESOURCECLASS_BONUS' then
         row.bonus=row.bonus+1
         if n:GetOwner()==pid then row.bonus_owned=row.bonus_owned+1 end
         if base then row.bonus_mapped=row.bonus_mapped+1 end
        end
        if n:GetOwner()==pid and base then row.base=row.base+1 end
        if n:GetOwner()==pid and tagged(resource.ResourceType,'CLASS_CSC_'..q..'_SPEC') then row.spec=row.spec+1 end
       end
       if n:GetDistrictType()~=-1 then row.adjacent_districts=row.adjacent_districts+1 end
      end
     end
     local district=GameInfo.Districts[dt].Index
     row.legal=p:CanHaveDistrict(district,pid,city:GetID())
     local ok,value=pcall(function() return p:GetAdjacencyYield(pid,city:GetID(),district,y) end)
     if ok then row.native_value=value else result.errors[#result.errors+1]=tostring(value) end
     row.bonus_river_expected=12*row.bonus+(row.river and 4 or 0)
     if ok and row.legal and row.adjacent_districts==0 then
      result.isolated_checks=result.isolated_checks+1
      if math.abs(value-row.bonus_river_expected)<0.001 then result.isolated_matches=result.isolated_matches+1 end
     end
     result.rows[#result.rows+1]=row
    end
   end
  end
 end
end
result.status=#result.rows==0 and 'deferred-no-cities-or-candidates' or 'observed'
include('CSC_MaterialMapCore')
print('CSC_AI_NATIVE_GUIDANCE='..CSC_MaterialMapCore.Json(result))
