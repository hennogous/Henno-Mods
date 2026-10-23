-- Fresh Core proof is substituted by the sole controller after its native poll.
-- UI can still report the previous human-player phase while its event lock
-- prevents an already-requested autoplay operation from taking over.
local coreTurn = __CORE_TURN__;
local targetTurn = __TARGET_TURN__;
local coreAutoplayActive = __CORE_ACTIVE__;
local uiTurn = Game.GetCurrentGameTurn();
local localPlayer = Game.GetLocalPlayer();
local hidden = ContextPtr:IsHidden();
print('CSC_DISASTER_PHASE_GUARD', coreTurn, targetTurn, coreAutoplayActive, uiTurn, localPlayer, hidden);
local samePhase = (uiTurn == coreTurn or uiTurn == coreTurn - 1);
local playbackIdentity = localPlayer == -1 or (localPlayer == 0 and uiTurn == coreTurn - 1);
if coreAutoplayActive and targetTurn > coreTurn and targetTurn - coreTurn <= 5 and samePhase and playbackIdentity and not hidden then
  assert(type(OnLocalPlayerTurnEnd) == 'function', 'Missing shipped disaster close handler');
  OnLocalPlayerTurnEnd();
  print('CSC_DISASTER_RELEASE_REQUESTED', coreTurn, uiTurn, localPlayer, ContextPtr:IsHidden());
end;
