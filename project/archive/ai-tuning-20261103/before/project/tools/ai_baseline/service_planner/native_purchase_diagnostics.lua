-- Read-only, bounded owner-turn diagnostics. Never requests a purchase, changes
-- player control, treasury, ownership, research, production or autoplay.
CSC_PURCHASE_DIAGNOSTICS=CSC_PURCHASE_DIAGNOSTICS or {rows={},errors={}}
local D=CSC_PURCHASE_DIAGNOSTICS
local limits=assert(CSC_PURCHASE_DIAGNOSTIC_LIMITS)
D.first_turn=limits.first_turn;D.last_turn=limits.last_turn;D.max_rows=limits.max_rows or 24
assert(D.first_turn<=D.last_turn and D.last_turn-D.first_turn<=2 and D.max_rows<=36,'Bounded diagnostic scope required')
local function safe(object,name,...)
 if not object or type(object[name])~='function'then return nil end
 local ok,value=pcall(object[name],object,...);if ok then return value end;return nil
end
function D.Read(pid,phase)
 local turn=Game.GetCurrentGameTurn()
 if turn<D.first_turn or turn>D.last_turn or #D.rows>=D.max_rows then return end
 local p=Players[pid];if not p or not p:IsAlive()or not p:IsMajor()then return end
 local gold=p:GetTreasury():GetGoldBalance()
 local row={turn=turn,player=pid,phase=phase,local_player=Game.GetLocalPlayer(),human=p:IsHuman(),active=safe(p,'IsTurnActive'),gold=gold,mutation_commands=0}
 local found=false
 for _,city in p:GetCities():Members()do
  local args={};args[CityCommandTypes.PARAM_PLOT_PURCHASE]=true
  local visible,targets=CityManager.CanStartCommand(city,CityCommandTypes.PURCHASE,true,args,true)
  for _,idx in ipairs(visible and targets and targets[CityCommandResults.PLOTS]or {})do
   local plot=Map.GetPlotByIndex(idx);local price=city:GetGold():GetPlotPurchaseCost(idx)
   if plot:GetOwner()==-1 and not plot:IsWater()and not plot:IsImpassable()and price>0 and price<=gold and Map.GetPlotDistance(city:GetX(),city:GetY(),plot:GetX(),plot:GetY())<=3 then
    args[CityCommandTypes.PARAM_X]=plot:GetX();args[CityCommandTypes.PARAM_Y]=plot:GetY()
    row.city=city:GetID();row.city_owner=city:GetOwner();row.plot=idx;row.plot_owner=plot:GetOwner();row.price=price
    row.ordinary,row.ordinary_results=CityManager.CanStartCommand(city,CityCommandTypes.PURCHASE,args)
    row.strict,row.strict_results=CityManager.CanStartCommand(city,CityCommandTypes.PURCHASE,false,args,true)
    row.strict_result_type=type(row.strict_results)
    row.failure_reasons=row.strict_results and row.strict_results[CityCommandResults.FAILURE_REASONS]or nil
    found=true;break
   end
  end
  if found then break end
 end
 row.affordable_unowned_land_sample=found
 assert(p:GetTreasury():GetGoldBalance()==gold,'Read-only diagnostic treasury changed')
 D.rows[#D.rows+1]=row
 print('CSC_PURCHASE_DIAGNOSTIC_ROW='..CSC_SERVICE_NATIVE.Json(row))
end
local function guarded(pid,phase)
 local ok,error=pcall(D.Read,pid,phase)
 if not ok then D.errors[#D.errors+1]={turn=Game.GetCurrentGameTurn(),player=pid,phase=phase,error=tostring(error)}end
end
if Events.PlayerTurnActivated then
 if D.activated_handler and Events.PlayerTurnActivated.Remove then Events.PlayerTurnActivated.Remove(D.activated_handler)end
 D.activated_handler=function(pid)guarded(pid,'activated')end
 Events.PlayerTurnActivated.Add(D.activated_handler)
end
if Events.PlayerTurnDeactivated then
 if D.deactivated_handler and Events.PlayerTurnDeactivated.Remove then Events.PlayerTurnDeactivated.Remove(D.deactivated_handler)end
 D.deactivated_handler=function(pid)guarded(pid,'deactivated')end
 Events.PlayerTurnDeactivated.Add(D.deactivated_handler)
end
D.Export=function()print('CSC_PURCHASE_DIAGNOSTICS='..CSC_SERVICE_NATIVE.Json({rows=D.rows,errors=D.errors,first_turn=D.first_turn,last_turn=D.last_turn,turn=Game.GetCurrentGameTurn(),mutation_commands=0}))end
for pid=0,5 do guarded(pid,'baseline-inactive')end
D.Export()
