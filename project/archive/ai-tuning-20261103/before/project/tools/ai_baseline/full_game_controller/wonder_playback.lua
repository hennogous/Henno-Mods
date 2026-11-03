-- Cosmetic wonder playback only. Shipped Close() restores the lens and unlocks
-- PopupManager when its presentation queue is empty. It submits no game choice.
local coreTurn = __CORE_TURN__;
local targetTurn = __TARGET_TURN__;
local coreActive = __CORE_ACTIVE__;
local coreLocal = __CORE_LOCAL__;
local coreHuman = __CORE_HUMAN__;
local uiTurn = Game.GetCurrentGameTurn();
local uiLocal = Game.GetLocalPlayer();
local hidden = ContextPtr:IsHidden();
print('CSC_WONDER_PLAYBACK_GUARD',coreTurn,targetTurn,coreActive,coreLocal,coreHuman,uiTurn,uiLocal,hidden);
if coreActive and coreLocal == -1 and not coreHuman and targetTurn > coreTurn and targetTurn-coreTurn <= 5 and (uiTurn == coreTurn or uiTurn == coreTurn-1) and (uiLocal == -1 or uiLocal == 0) and not hidden then
  assert(type(Close)=='function','Missing shipped wonder playback Close handler');
  Close();
  print('CSC_WONDER_PLAYBACK_RELEASE_REQUESTED',coreTurn,uiTurn,uiLocal,ContextPtr:IsHidden());
end;
