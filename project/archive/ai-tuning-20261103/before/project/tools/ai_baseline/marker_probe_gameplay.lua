include('CSC_MaterialMapCore');
local M=CSC_AI_MaterialMarkers;assert(M);
local f=assert(Game:GetProperty('CSC_AI_MARKER_FIXTURE'));
local rows={};
for _,c in ipairs(f.cases) do
 local p=Map.GetPlotByIndex(c.resource);local player=Players[c.player];local imps={};local yields={};
 for y in GameInfo.Yields() do if y.YieldType~='YIELD_CSC_AI_PLACEMENT' then yields[y.YieldType]=p:GetYield(y.Index);end;end
 for i in GameInfo.Improvements() do
  imps[i.ImprovementType]=ImprovementBuilder.CanHaveImprovement(p,i.Index,player:GetTeam());
 end
 rows[#rows+1]={kind=c.kind,plot=c.resource,feature=p:GetFeatureType(),resource=p:GetResourceType(),quantity=p:GetResourceCount(),
  yields=yields,appeal=p:GetAppeal(),improvements=imps};
end
local kept=0;
for _,v in ipairs(f.real_features) do if Map.GetPlotByIndex(v.plot):GetFeatureType()==v.feature then kept=kept+1;end;end
assert(kept==#f.real_features,'Real feature changed');
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='gameplay',enabled=M.Enabled,rows=rows,real_features_kept=kept,audit=M.LastAudit}));
