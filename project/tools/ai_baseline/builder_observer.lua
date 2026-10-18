-- Supplemental read-only unit observations; primary baseline observer unchanged.
assert(not CSC_BUILDERS)
CSC_BUILDERS={version=1,events={},checkpoints={},errors={}}
local B=CSC_BUILDERS
local unitType=assert(GameInfo.Units.UNIT_BUILDER).Index
local unitPurchaseType=EventSubTypes and EventSubTypes.UNIT
local function safe(name,fn)
 return function(...) local ok,e=pcall(fn,...);if not ok then B.errors[#B.errors+1]={turn=Game.GetCurrentGameTurn(),name=name,error=tostring(e)} end end
end
local function add(kind,row)
 row.event=kind;row.turn=Game.GetCurrentGameTurn();B.events[#B.events+1]=row
end
function B.Capture()
 local result={turn=Game.GetCurrentGameTurn(),players={},events={},errors={},unit_purchase_subtype=unitPurchaseType}
 for _,player in ipairs(PlayerManager.GetAliveMajors()) do
  local row={player=player:GetID(),builders={},count=0,charges=0}
  for _,unit in player:GetUnits():Members() do
   if unit:GetType()==unitType then
    local charges=unit:GetBuildCharges()
    row.count=row.count+1;row.charges=row.charges+charges
    row.builders[#row.builders+1]={unit=unit:GetID(),x=unit:GetX(),y=unit:GetY(),charges=charges}
   end
  end
  result.players[#result.players+1]=row
 end
 for i,e in ipairs(B.events) do result.events[i]=e end
 for i,e in ipairs(B.errors) do result.errors[i]=e end
 return result
end
Events.UnitAddedToMap.Add(safe('unit added',function(pid,uid)
 local player=Players[pid];local unit=player and player:GetUnits():FindID(uid)
 if unit and unit:GetType()==unitType then add('builder_added',{player=pid,unit=uid,charges=unit:GetBuildCharges()}) end
end))
Events.CityProductionCompleted.Add(safe('training',function(pid,cid,order,item,cancelled)
 -- Stock TutorialUIRoot uses 0 for ORDER_TRAIN in this event.
 if not cancelled and order==0 and item==unitType then add('builder_training_completed',{player=pid,city=cid}) end
end))
Events.CityMadePurchase.Add(safe('purchase',function(pid,cid,x,y,purchaseType,item)
 if unitPurchaseType~=nil and purchaseType==unitPurchaseType and item==unitType then add('builder_purchased',{player=pid,city=cid})
 elseif unitPurchaseType==nil then add('unclassified_city_purchase',{player=pid,city=cid,purchase_type=purchaseType,item=item}) end
end))
Events.UnitOperationStarted.Add(safe('operation',function(pid,uid,operation)
 local player=Players[pid];local unit=player and player:GetUnits():FindID(uid)
 if unit and unit:GetType()==unitType then add('builder_operation_started',{player=pid,unit=uid,operation=operation,charges=unit:GetBuildCharges(),x=unit:GetX(),y=unit:GetY()}) end
end))
Events.PlayerTurnActivated.Add(safe('census',function(pid)
 local player=Players[pid];if not player or not player:IsMajor() then return end
 local turn=Game.GetCurrentGameTurn()
 if turn%50==0 and not B.checkpoints[turn] then B.checkpoints[turn]=B.Capture() end
end))
B.checkpoints[Game.GetCurrentGameTurn()]=B.Capture()
print('CSC_BUILDERS_READY')
