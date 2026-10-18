include('CSC_MaterialMapCore');
local rows={};
for _,c in ipairs(assert(Game:GetProperty('CSC_AI_MARKER_HUMAN_FIXTURE'))) do
 local unit=assert(Players[c.player]:GetUnits():FindID(c.builder));local p=Map.GetPlotByIndex(c.plot);
 local args={};args[UnitOperationTypes.PARAM_X]=p:GetX();args[UnitOperationTypes.PARAM_Y]=p:GetY();
 args[UnitOperationTypes.PARAM_IMPROVEMENT_TYPE]=GameInfo.Improvements[c.improvement].Index;
 local can,details=UnitManager.CanStartOperation(unit,UnitOperationTypes.BUILD_IMPROVEMENT,nil,args,true);
 rows[#rows+1]={plot=c.plot,improvement=c.improvement,builder=c.builder,feature=p:GetFeatureType(),
  moves=unit:GetMovesRemaining(),charges=unit:GetBuildCharges(),can_build=can,details=details,
  removable=GameInfo.Features[p:GetFeatureType()] and GameInfo.Features[p:GetFeatureType()].Removable,
  can_clear=UnitManager.CanStartOperation(unit,UnitOperationTypes.REMOVE_FEATURE,nil)};
 rows[#rows].can_harvest=UnitManager.CanStartOperation(unit,UnitOperationTypes.HARVEST_RESOURCE,nil);
 rows[#rows].can_plant=UnitManager.CanStartOperation(unit,UnitOperationTypes.PLANT_FOREST,nil);
end
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='human_ui',local_player=Game.GetLocalPlayer(),rows=rows}));
