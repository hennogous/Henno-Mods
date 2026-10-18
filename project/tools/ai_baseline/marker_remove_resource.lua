local cases=assert(Game:GetProperty('CSC_AI_MARKER_HUMAN_FIXTURE'));
assert(not Game:GetProperty('CSC_AI_MARKER_RESOURCE_REMOVED'),'Do not replay resource mutation');
local p=Map.GetPlotByIndex(cases[1].plot);
assert(CSC_AI_MaterialMarkers.IsMarker(p:GetFeatureType()));
Game:SetProperty('CSC_AI_MARKER_RESOURCE_REMOVED',{plot=p:GetIndex(),resource=p:GetResourceType()});
ResourceBuilder.SetResourceType(p,-1);
print('CSC_MARKER_RESOURCE_REMOVAL_DISPATCHED',p:GetIndex());
