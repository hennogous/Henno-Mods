include('CSC_MaterialMapCore');
local f=assert(Game:GetProperty('CSC_AI_MARKER_RESOURCE_REMOVED'));local p=Map.GetPlotByIndex(f.plot);
assert(p:GetResourceType()==-1,'Resource removal failed');
assert(not CSC_AI_MaterialMarkers.IsMarker(p:GetFeatureType()),'Stale material marker remained');
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='resource_removed',plot=f.plot,feature=p:GetFeatureType(),resource=p:GetResourceType()}));
