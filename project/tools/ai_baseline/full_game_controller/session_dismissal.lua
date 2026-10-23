-- Standard conversation dismissal for a log-verified observer warning.
-- CloseSession ends the conversation as shipped ExitConversationMode does.
-- It is recorded as an intervention, never labelled merely cosmetic.
-- No AddResponse/AddStatement, treaty choice, turn forcing or budget change.
local function skip(reason) print('CSC_OBSERVER_WARNING_DISMISS_SKIPPED',reason) end
local from=__FROM__
local id=DiplomacyManager.FindOpenSessionID(0,from)
if type(id)~='number'or id<0 then skip('no_session');return end
local turn=__CORE_TURN__;local target=__TARGET_TURN__
if not(__CORE_ACTIVE__ and __CORE_LOCAL__==-1 and not __CORE_HUMAN__ and target-turn>0 and target-turn<=5)then skip('core_phase');return end
local ui=Game.GetCurrentGameTurn();if ui~=turn and ui~=turn-1 then skip('ui_clock');return end
if Game.GetLocalPlayer()~=-1 or Players[0]:IsHuman()then skip('ui_control');return end
if not DiplomacyManager.IsSessionIDOpen(id)then skip('session_closed');return end
if DiplomacyManager.FindOpenSessionID(0,from)~=id then skip('session_changed');return end
local info=DiplomacyManager.GetSessionInfo(id)
if not info or info.FromPlayer~=from or info.ToPlayer~=0 then skip('participants');return end
print('CSC_OBSERVER_WARNING_DISMISS_BEGIN',turn,id,from,0)
DiplomacyManager.CloseSession(id)
if not ContextPtr:IsHidden()and type(Close)=='function'then Close()end
print('CSC_OBSERVER_WARNING_DISMISS_REQUESTED',turn,id,from,0)
