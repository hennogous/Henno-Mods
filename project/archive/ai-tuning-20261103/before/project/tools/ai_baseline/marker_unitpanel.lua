include('CSC_MaterialMapCore');
local rows={};
local function clearShown(u)
 local actions=assert(GetUnitActionsTable(u));local found=false;
 for _,list in pairs(actions) do for _,row in ipairs(list) do if row.userTag==UnitOperationTypes.REMOVE_FEATURE then found=true;end;end;end
 return found;
end
for _,c in ipairs(assert(Game:GetProperty('CSC_AI_MARKER_HUMAN_FIXTURE'))) do
 local u=assert(Players[0]:GetUnits():FindID(c.builder));local shown=clearShown(u);
 assert(not shown,'Marker clear action leaked into Unit Panel');
 rows[#rows+1]={plot=c.plot,clear_shown=shown};
end
local forest=assert(Game:GetProperty('CSC_AI_MARKER_FOREST_CONTROL'));
local u=assert(Players[0]:GetUnits():FindID(forest.builder));
assert(UnitManager.CanStartOperation(u,UnitOperationTypes.REMOVE_FEATURE,nil),'Normal Woods clearing should be possible');
local shown=clearShown(u);assert(shown,'Normal Woods clear action lost');
print('CSC_MARKER_RESULT='..CSC_MaterialMapCore.Json({stage='unitpanel',marker_rows=rows,normal_woods_clear_shown=shown}));
