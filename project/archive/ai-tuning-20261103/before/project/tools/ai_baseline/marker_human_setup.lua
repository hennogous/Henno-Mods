-- Positive Builder-operation controls: player 0 is active during turn 1.
-- AI-owned inactive-turn units cannot supply a positive CanStartOperation test.
include('CSC_MaterialMapCore');
local player=Players[0];local M=CSC_AI_MaterialMarkers;assert(M);
assert(not Game:GetProperty('CSC_AI_MARKER_HUMAN_FIXTURE'));
for t in GameInfo.Technologies() do player:GetTechs():SetTech(t.Index,true);end
for c in GameInfo.Civics() do player:GetCulture():SetCivic(c.Index,true);end
local cases={};
for _,improvement in ipairs({'IMPROVEMENT_FARM','IMPROVEMENT_PLANTATION','IMPROVEMENT_MINE'}) do
 local selected;
 for i=0,Map.GetPlotCount()-1 do
  local source=Map.GetPlotByIndex(i);local res=GameInfo.Resources[source:GetResourceType()];local valid=false;
  if res and M.IsMarker(source:GetFeatureType()) then
   for row in GameInfo.Improvement_ValidResources() do if row.ResourceType==res.ResourceType and row.ImprovementType==improvement then valid=true;break;end;end
  end
  if valid then
   for d=0,5 do
    local center=Map.GetAdjacentPlot(source:GetX(),source:GetY(),d);
    local ok=center and center:GetDistrictType()==-1 and center:GetFeatureType()==-1 and center:GetResourceType()==-1 and not center:IsWater() and not center:IsImpassable() and not center:IsMountain();
    if ok then
     for _,major in ipairs(PlayerManager.GetAliveMajors()) do for _,city in major:GetCities():Members() do
      if Map.GetPlotDistance(center:GetX(),center:GetY(),city:GetX(),city:GetY())<4 then ok=false;end
     end;end
    end
    if ok then selected={source=source,center=center};break;end
   end
  end
  if selected then break;end
 end
 assert(selected,'No positive Builder control '..improvement);
 local p=selected.source;local center=selected.center;
 local city=assert(player:GetCities():Create(center:GetX(),center:GetY()));
 WorldBuilder.CityManager():SetPlotOwner(p:GetX(),p:GetY(),0,city:GetID());
 local unit=assert(player:GetUnits():Create(GameInfo.Units.UNIT_BUILDER.Index,p:GetX(),p:GetY()));
 cases[#cases+1]={plot=p:GetIndex(),player=0,city=city:GetID(),builder=unit:GetID(),improvement=improvement};
end
Game:SetProperty('CSC_AI_MARKER_HUMAN_FIXTURE',cases);
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='human_setup',cases=cases}));
