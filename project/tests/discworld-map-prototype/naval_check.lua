-- UI reads native pathing for the temporary ship; no move order is issued here.
local a=assert(Game:GetProperty('DISC_NAVAL_FIXTURE'));
local u=assert(UnitManager.GetUnit(0,a[1]));
local good=UnitManager.GetMoveToPath(u,a[3]);local bad=UnitManager.GetMoveToPath(u,a[4]);
print('DISC_NAVAL_PATHS',a[2],a[3],a[4],good and #good or -1,bad and #bad or -1);
assert(good and #good>0,'Positive control has no path');
assert(not bad or #bad==0,'Path crosses Rim');
local q=Map.GetPlotByIndex(a[4]);local params={};
params[UnitOperationTypes.PARAM_X]=q:GetX();params[UnitOperationTypes.PARAM_Y]=q:GetY();
print('DISC_NAVAL_CAN_ORDER_VOID',UnitManager.CanStartOperation(u,UnitOperationTypes.MOVE_TO,nil,params));
