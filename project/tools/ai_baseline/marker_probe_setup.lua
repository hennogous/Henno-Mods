-- Controlled disposable fixture: native resources/terrain retained; AI cities,
-- ownership and research created solely to compare marker on/off feasibility.
assert(Game.GetCurrentGameTurn()==1,'Fresh disposable game required');
local M=CSC_AI_MaterialMarkers;assert(M and M.Version==2);
assert(not Game:GetProperty('CSC_AI_MARKER_FIXTURE'),'Fixture already exists');
include('CSC_MaterialMapCore');
local player=Players[1];local pid=1;
for tech in GameInfo.Technologies() do player:GetTechs():SetTech(tech.Index,true);end
for civic in GameInfo.Civics() do player:GetCulture():SetCivic(civic.Index,true);end
local function tagged(rt,tag)
 for row in GameInfo.TypeTags() do if row.Type==rt and row.Tag==tag then return true;end;end
 return false;
end
local cases={};local occupied={};local signature={};
for i=0,Map.GetPlotCount()-1 do
 local p=Map.GetPlotByIndex(i);local f=p:GetFeatureType();
 if f~=-1 and not M.IsMarker(f) then signature[#signature+1]={plot=i,feature=f};end
end
for _,kind in ipairs({'BAKERS_BASE','BAKERS_SPEC','TAILORS_BASE','TAILORS_SPEC'}) do
 local selected;
 for i=0,Map.GetPlotCount()-1 do
  local resource=Map.GetPlotByIndex(i);local row=GameInfo.Resources[resource:GetResourceType()];
  if row and M.IsMarker(resource:GetFeatureType()) and tagged(row.ResourceType,'CLASS_CSC_'..kind) then
   for direction=0,5 do
    local q=Map.GetAdjacentPlot(resource:GetX(),resource:GetY(),direction);
    if q and not q:IsWater() and not q:IsImpassable() and q:GetFeatureType()==-1 and q:GetResourceType()==-1 and q:GetDistrictType()==-1 then
     for d=0,5 do
      local center=Map.GetAdjacentPlot(q:GetX(),q:GetY(),d);local viable=center and center:GetIndex()~=i and not center:IsWater() and not center:IsImpassable() and not center:IsMountain() and center:GetFeatureType()==-1 and center:GetResourceType()==-1 and center:GetDistrictType()==-1;
      if viable then
       for _,c in ipairs(occupied) do if Map.GetPlotDistance(c.x,c.y,center:GetX(),center:GetY())<6 then viable=false;break;end;end
       for _,major in ipairs(PlayerManager.GetAliveMajors()) do for _,c in major:GetCities():Members() do
        if Map.GetPlotDistance(c:GetX(),c:GetY(),center:GetX(),center:GetY())<6 then viable=false;end
       end;end
      end
      if viable then selected={resource=resource,quarter=q,center=center};break;end
     end
    end
    if selected then break;end
   end
  end
  if selected then break;end
 end
 assert(selected,'No native fixture for '..kind);
 local center=selected.center;local city=player:GetCities():Create(center:GetX(),center:GetY());assert(city);
 occupied[#occupied+1]={x=center:GetX(),y=center:GetY()};
 for _,p in ipairs({selected.resource,selected.quarter}) do
  WorldBuilder.CityManager():SetPlotOwner(p:GetX(),p:GetY(),pid,city:GetID());
  assert(p:GetOwner()==pid);
 end
 local unit=player:GetUnits():Create(GameInfo.Units.UNIT_BUILDER.Index,selected.resource:GetX(),selected.resource:GetY());assert(unit);
 local q=kind:match('^(.-)_');
 cases[#cases+1]={kind=kind,resource=selected.resource:GetIndex(),quarter=selected.quarter:GetIndex(),
  district='DISTRICT_CSC_'..q..'_QUARTER',city=city:GetID(),player=pid,builder=unit:GetID()};
end
Game:SetProperty('CSC_AI_MARKER_FIXTURE',{cases=cases,real_features=signature});
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='setup',cases=cases,real_features=#signature}));
