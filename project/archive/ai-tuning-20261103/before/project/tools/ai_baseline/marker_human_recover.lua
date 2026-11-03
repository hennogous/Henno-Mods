include('CSC_MaterialMapCore');
assert(not Game:GetProperty('CSC_AI_MARKER_HUMAN_FIXTURE'));
local player=Players[0];local cases={};local city;
for _,c in player:GetCities():Members() do city=c;break;end;assert(city);
for _,u in player:GetUnits():Members() do
 if u:GetType()==GameInfo.Units.UNIT_BUILDER.Index then
  local p=Map.GetPlot(u:GetX(),u:GetY());local r=GameInfo.Resources[p:GetResourceType()];local improvement;
  for row in GameInfo.Improvement_ValidResources() do if row.ResourceType==r.ResourceType and
   (row.ImprovementType=='IMPROVEMENT_FARM' or row.ImprovementType=='IMPROVEMENT_PLANTATION') then improvement=row.ImprovementType;break;end;end
  assert(improvement);
  cases[#cases+1]={plot=p:GetIndex(),player=0,city=city:GetID(),builder=u:GetID(),improvement=improvement};
 end
end
assert(#cases==2,'Expected two partial active-player fixtures');
-- Reuse the earlier legal Silver fixture, transferring just this disposable
-- tile rather than founding another neighboring city.
local ai=assert(Game:GetProperty('CSC_AI_MARKER_FIXTURE'));local target;
for _,c in ipairs(ai.cases) do if c.kind=='TAILORS_SPEC' then target=Map.GetPlotByIndex(c.resource);end;end
assert(target);local res=GameInfo.Resources[target:GetResourceType()];local mine=false;
for row in GameInfo.Improvement_ValidResources() do if row.ResourceType==res.ResourceType and row.ImprovementType=='IMPROVEMENT_MINE' then mine=true;end;end
assert(mine,'Tailors specialty is not a native Mine resource');
WorldBuilder.CityManager():SetPlotOwner(target:GetX(),target:GetY(),0,city:GetID());assert(target:GetOwner()==0);
local u=assert(player:GetUnits():Create(GameInfo.Units.UNIT_BUILDER.Index,target:GetX(),target:GetY()));
cases[#cases+1]={plot=target:GetIndex(),player=0,city=city:GetID(),builder=u:GetID(),improvement='IMPROVEMENT_MINE'};
Game:SetProperty('CSC_AI_MARKER_HUMAN_FIXTURE',cases);
CSC_AI_MaterialMarkers.Refresh();
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='human_recovered',cases=cases}));
