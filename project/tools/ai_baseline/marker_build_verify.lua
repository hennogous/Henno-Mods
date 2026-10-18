include('CSC_MaterialMapCore');local rows={};
for _,c in ipairs(assert(Game:GetProperty('CSC_AI_MARKER_HUMAN_FIXTURE'))) do
 local p=Map.GetPlotByIndex(c.plot);local unit=assert(Players[c.player]:GetUnits():FindID(c.builder));
 assert(p:GetImprovementType()==GameInfo.Improvements[c.improvement].Index,'Native Builder did not complete '..c.improvement);
 assert(unit:GetBuildCharges()==2,'Expected exactly one charge');
 rows[#rows+1]={plot=c.plot,improvement=c.improvement,charges=unit:GetBuildCharges(),marker=CSC_AI_MaterialMarkers.IsMarker(p:GetFeatureType()),resource=p:GetResourceType()};
end
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='build_verify',rows=rows}));
