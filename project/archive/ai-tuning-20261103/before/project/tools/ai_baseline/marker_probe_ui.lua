include('CSC_MaterialMapCore');
local f=assert(Game:GetProperty('CSC_AI_MARKER_FIXTURE'));local rows={};
local y=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index;
for _,c in ipairs(f.cases) do
 local p=Map.GetPlotByIndex(c.quarter);local resource=Map.GetPlotByIndex(c.resource);
 local unit=Players[c.player]:GetUnits():FindID(c.builder);assert(unit);
 local operations={};
 for i in GameInfo.Improvements() do
  local args={};args[UnitOperationTypes.PARAM_IMPROVEMENT_TYPE]=i.Index;
  args[UnitOperationTypes.PARAM_X]=resource:GetX();args[UnitOperationTypes.PARAM_Y]=resource:GetY();
  operations[i.ImprovementType]=UnitManager.CanStartOperation(unit,UnitOperationTypes.BUILD_IMPROVEMENT,nil,args);
 end
 local canRemove=UnitManager.CanStartOperation(unit,UnitOperationTypes.REMOVE_FEATURE,nil);
 local expected=0;local q=c.district:match('DISTRICT_CSC_(.-)_QUARTER');
 for d=0,5 do
  local n=Map.GetAdjacentPlot(p:GetX(),p:GetY(),d);local f=n and GameInfo.Features[n:GetFeatureType()];
  if f and f.FeatureType:match('^FEATURE_CSC_AI_RESOURCE_') then
   local r=GameInfo.Resources[n:GetResourceType()];
   for tag in GameInfo.TypeTags() do if tag.Type==r.ResourceType then
    if tag.Tag=='CLASS_CSC_'..q..'_BASE' then expected=expected+12;end
    if tag.Tag=='CLASS_CSC_'..q..'_SPEC' then expected=expected+4;end
   end;end
  end
 end
 rows[#rows+1]={kind=c.kind,value=p:GetAdjacencyYield(c.player,c.city,GameInfo.Districts[c.district].Index,y),
  quarter_legal=p:CanHaveDistrict(GameInfo.Districts[c.district].Index,c.player,c.city),
  resource_district_legal=resource:CanHaveDistrict(GameInfo.Districts[c.district].Index,c.player,c.city),
  build_operations=operations,remove_feature=canRemove,marker_expected=expected};
end
local shown=0;for row in GameInfo.Features() do if row.FeatureType:match('^FEATURE_CSC_AI_RESOURCE_') then shown=shown+1;end;end
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='ui',rows=rows,marker_rows_shown=shown,filter=CSC_AI_UIFilterInstalled}));
