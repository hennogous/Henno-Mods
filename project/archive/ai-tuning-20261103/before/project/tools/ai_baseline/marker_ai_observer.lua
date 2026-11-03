include('CSC_MaterialMapCore');
assert(not CSC_MARKER_AI_OBSERVER);
CSC_MARKER_AI_OBSERVER={removed={},clear_operations={},started=Game.GetCurrentGameTurn()};
local cache={};
for i=0,Map.GetPlotCount()-1 do cache[i]=Map.GetPlotByIndex(i):GetFeatureType();end
Events.FeatureAddedToMap.Add(function(x,y)
 local p=Map.GetPlot(x,y);cache[p:GetIndex()]=p:GetFeatureType();
end);
Events.FeatureRemovedFromMap.Add(function(x,y)
 local p=Map.GetPlot(x,y);local i=p:GetIndex();
 if CSC_AI_MaterialMarkers.IsMarker(cache[i]) then
  local rows=CSC_MARKER_AI_OBSERVER.removed;
  rows[#rows+1]={turn=Game.GetCurrentGameTurn(),plot=i,resource=p:GetResourceType(),improvement=p:GetImprovementType(),district=p:GetDistrictType()};
 end
 cache[i]=p:GetFeatureType();
end);
Events.UnitOperationStarted.Add(function(pid,uid,operation)
 if operation~=UnitOperationTypes.REMOVE_FEATURE then return;end
 local u=Players[pid]:GetUnits():FindID(uid);if not u then return;end
 local p=Map.GetPlot(u:GetX(),u:GetY());
 if CSC_AI_MaterialMarkers.IsMarker(cache[p:GetIndex()]) or CSC_AI_MaterialMarkers.IsMarker(p:GetFeatureType()) then
  local rows=CSC_MARKER_AI_OBSERVER.clear_operations;
  rows[#rows+1]={player=pid,unit=uid,plot=p:GetIndex(),turn=Game.GetCurrentGameTurn()};
 end
end);
print('CSC_MARKER_AI_OBSERVER_READY');
