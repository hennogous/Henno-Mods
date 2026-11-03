-- Experimental v2: native feature adjacency over featureless material deposits.
-- This never replaces a real feature. Markers are global geography, including
-- unowned/foreign materials, and reward each deposit rather than class presence.
local watched={'ResourceAddedToMap','ResourceRemovedFromMap','ResourceChanged','FeatureAddedToMap',
 'ImprovementAddedToMap','ImprovementRemovedFromMap','ImprovementChanged',
 'DistrictAddedToMap','PlayerTurnActivated','UnitMoved','UnitAddedToMap','UnitRemovedFromMap'};
-- A native diagnostic can reload this exact module without duplicate listeners.
local prior=CSC_AI_MaterialMarkers;
if prior and prior.Refresh then for _,name in ipairs(watched) do
 if Events[name] then Events[name].Remove(prior.Refresh);end
end;end
CSC_AI_MaterialMarkers={Version=3,Enabled=true};
local M=CSC_AI_MaterialMarkers;
local byResource,ours={},{};
for row in GameInfo.CSC_AI_MaterialMarkers() do
 local r,f=GameInfo.Resources[row.ResourceType],GameInfo.Features[row.FeatureType];
 if r and f then byResource[r.Index]=f.Index;ours[f.Index]=true;end
end
local busy=false;
function M.IsMarker(index) return ours[index]==true;end
function M.Refresh()
 if busy then return;end
 busy=true;
 local audit={version=M.Version,added=0,removed=0,retained=0,real_feature_skips=0,builder_skips=0};
 local configured=GameConfiguration.GetValue('CSC_AI_MATERIAL_MARKERS');
 local enabled=M.Enabled and configured~=false and configured~=0;
 local ok,err=pcall(function()
  -- Never give a Builder a removable synthetic feature to clear. Withhold
  -- markers one movement step before arrival, then restore them after departure.
  local nearBuilder={};
  for pid=0,63 do local player=Players[pid];
   if player and player:IsAlive() then for _,unit in player:GetUnits():Members() do
    if unit:GetType()==GameInfo.Units.UNIT_BUILDER.Index then
     local center=Map.GetPlot(unit:GetX(),unit:GetY());
     if center then
      nearBuilder[center:GetIndex()]=true;
      for d=0,5 do local n=Map.GetAdjacentPlot(unit:GetX(),unit:GetY(),d);if n then nearBuilder[n:GetIndex()]=true;end;end
     end
    end
   end;end
  end
  for i=0,Map.GetPlotCount()-1 do
   local p=Map.GetPlotByIndex(i);local f=p:GetFeatureType();local desired;
   if enabled and not p:IsWater() and not p:IsImpassable() and p:GetDistrictType()==-1 then
    desired=byResource[p:GetResourceType()];
   end
   if desired and nearBuilder[i] then desired=nil;audit.builder_skips=audit.builder_skips+1;end
   if ours[f] then
    if desired~=f then
     TerrainBuilder.SetFeatureType(p,-1);audit.removed=audit.removed+1;
     f=-1;
    else audit.retained=audit.retained+1;end
   end
   if desired and f==-1 then
    TerrainBuilder.SetFeatureType(p,desired);
    assert(p:GetFeatureType()==desired,'CSC marker readback failed: '..i);
    audit.added=audit.added+1;
   elseif desired and not ours[f] then audit.real_feature_skips=audit.real_feature_skips+1;end
  end
 end);
 busy=false;M.LastAudit=audit;
 if not ok then M.Enabled=false;error('CSC material marker: '..tostring(err));end
 return audit;
end
-- Resource/feature/improvement changes can invalidate a marker in the same turn.
-- The busy guard prevents our own feature events from recursively reconciling.
for _,name in ipairs(watched) do
 if Events[name] then Events[name].Add(M.Refresh);end
end
local initial=M.Refresh();
print('CSC_AI_MARKERS_INITIALIZED',initial.added,initial.retained,initial.real_feature_skips);
