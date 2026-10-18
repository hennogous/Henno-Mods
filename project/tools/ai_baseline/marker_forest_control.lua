include('CSC_MaterialMapCore');
assert(not Game:GetProperty('CSC_AI_MARKER_FOREST_CONTROL'));
local player=Players[0];local target,city;
for _,c in player:GetCities():Members() do
 for i=0,Map.GetPlotCount()-1 do local p=Map.GetPlotByIndex(i);
  if p:GetFeatureType()==GameInfo.Features.FEATURE_FOREST.Index and p:GetDistrictType()==-1
   and Map.GetPlotDistance(p:GetX(),p:GetY(),c:GetX(),c:GetY())<=3 then target=p;city=c;break;end
 end
 if target then break;end
end
assert(target,'No normal Woods control');
WorldBuilder.CityManager():SetPlotOwner(target:GetX(),target:GetY(),0,city:GetID());
local u=assert(player:GetUnits():Create(GameInfo.Units.UNIT_BUILDER.Index,target:GetX(),target:GetY()));
Game:SetProperty('CSC_AI_MARKER_FOREST_CONTROL',{builder=u:GetID(),plot=target:GetIndex()});
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='forest_control',plot=target:GetIndex(),builder=u:GetID()}));
