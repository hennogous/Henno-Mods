assert(not CSC_MARKER_BUILDS_SENT,'Do not replay Builder operations');
local f=assert(Game:GetProperty('CSC_AI_MARKER_HUMAN_FIXTURE'));
for _,c in ipairs(f) do
 local unit=assert(Players[c.player]:GetUnits():FindID(c.builder));local p=Map.GetPlotByIndex(c.plot);
 local args={};args[UnitOperationTypes.PARAM_X]=p:GetX();args[UnitOperationTypes.PARAM_Y]=p:GetY();
 args[UnitOperationTypes.PARAM_IMPROVEMENT_TYPE]=GameInfo.Improvements[c.improvement].Index;
 assert(UnitManager.CanStartOperation(unit,UnitOperationTypes.BUILD_IMPROVEMENT,nil,args),'Builder action unavailable');
end
CSC_MARKER_BUILDS_SENT=true;
for _,c in ipairs(f) do
 local unit=Players[c.player]:GetUnits():FindID(c.builder);local p=Map.GetPlotByIndex(c.plot);
 local args={};args[UnitOperationTypes.PARAM_X]=p:GetX();args[UnitOperationTypes.PARAM_Y]=p:GetY();
 args[UnitOperationTypes.PARAM_IMPROVEMENT_TYPE]=GameInfo.Improvements[c.improvement].Index;
 UnitManager.RequestOperation(unit,UnitOperationTypes.BUILD_IMPROVEMENT,args);
end
print('CSC_MARKER_BUILD_REQUESTS_SENT',#f);
