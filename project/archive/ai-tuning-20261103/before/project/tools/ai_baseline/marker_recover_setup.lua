-- Recover the three already-created disposable cases; do not replay creation.
include('CSC_MaterialMapCore');
assert(not Game:GetProperty('CSC_AI_MARKER_FIXTURE'));
local M=CSC_AI_MaterialMarkers;local player=Players[1];local cases={};
local function tagged(rt,tag)
 for r in GameInfo.TypeTags() do if r.Type==rt and r.Tag==tag then return true;end;end
 return false;
end
local builders={};for _,u in player:GetUnits():Members() do
 if u:GetType()==GameInfo.Units.UNIT_BUILDER.Index then builders[#builders+1]=u;end
end
table.sort(builders,function(a,b)return a:GetID()<b:GetID();end);
assert(#builders==3,'Expected exactly three partial fixture Builders');
local kinds={'BAKERS_BASE','BAKERS_SPEC','TAILORS_BASE'};
local function chooseQuarter(resource,city)
 for d=0,5 do
  local p=Map.GetAdjacentPlot(resource:GetX(),resource:GetY(),d);
  if p and p:GetOwner()==1 and not p:IsWater() and not p:IsImpassable() and p:GetResourceType()==-1 and p:GetFeatureType()==-1 and p:GetDistrictType()==-1
   and Map.GetPlotDistance(p:GetX(),p:GetY(),city:GetX(),city:GetY())<=3 then return p;end
 end
end
for i,u in ipairs(builders) do
 local p=Map.GetPlot(u:GetX(),u:GetY());local row=GameInfo.Resources[p:GetResourceType()];
 assert(row and tagged(row.ResourceType,'CLASS_CSC_'..kinds[i]));
 local city;
 for _,c in player:GetCities():Members() do if Map.GetPlotDistance(c:GetX(),c:GetY(),p:GetX(),p:GetY())<=2 then city=c;break;end;end
 assert(city);local q=assert(chooseQuarter(p,city));
 cases[#cases+1]={kind=kinds[i],player=1,city=city:GetID(),builder=u:GetID(),resource=p:GetIndex(),quarter=q:GetIndex(),
  district='DISTRICT_CSC_'..kinds[i]:match('^(.-)_')..'_QUARTER'};
end
-- Add one legal featureless specialty deposit within an existing fixture city.
local target,resource,city,quarter;
for _,c in player:GetCities():Members() do
 for i=0,Map.GetPlotCount()-1 do
  local p=Map.GetPlotByIndex(i);
  if p:GetDistrictType()==-1 and p:GetResourceType()==-1 and p:GetFeatureType()==-1 and not p:IsWater() and not p:IsImpassable()
   and Map.GetPlotDistance(c:GetX(),c:GetY(),p:GetX(),p:GetY())<=2 then
   local q=chooseQuarter(p,c);
   if q then
    for r in GameInfo.Resources() do
     if tagged(r.ResourceType,'CLASS_CSC_TAILORS_SPEC') and ResourceBuilder.CanHaveResource(p,r.Index) then
      target=p;resource=r;city=c;quarter=q;break;
     end
    end
   end
  end
  if target then break;end
 end
 if target then break;end
end
assert(target,'No legal featureless Tailors specialty fixture');
WorldBuilder.CityManager():SetPlotOwner(target:GetX(),target:GetY(),1,city:GetID());
ResourceBuilder.SetResourceType(target,resource.Index,1);
local u=assert(player:GetUnits():Create(GameInfo.Units.UNIT_BUILDER.Index,target:GetX(),target:GetY()));
cases[#cases+1]={kind='TAILORS_SPEC',player=1,city=city:GetID(),builder=u:GetID(),resource=target:GetIndex(),quarter=quarter:GetIndex(),
 district='DISTRICT_CSC_TAILORS_QUARTER'};
local signature={};for i=0,Map.GetPlotCount()-1 do
 local p=Map.GetPlotByIndex(i);local f=p:GetFeatureType();
 if f~=-1 and not M.IsMarker(f) then signature[#signature+1]={plot=i,feature=f};end
end
Game:SetProperty('CSC_AI_MARKER_FIXTURE',{cases=cases,real_features=signature});
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='recovered_setup',cases=cases,real_features=#signature}));
