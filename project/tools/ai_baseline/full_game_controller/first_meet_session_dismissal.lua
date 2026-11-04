-- Standard CHOICE_EXIT (busy/no visit) for a log-verified observer first meet.
-- First-meet also offers a positive invitation; this NEVER chooses that branch.
-- Shipped DiplomacyActionView.OnSelectConversationDiplomacyStatement maps
-- CHOICE_EXIT to ExitConversationMode/CloseSession, with no AddResponse or
-- AddStatement. Record this as a declined invitation, not cosmetic playback.
-- CloseSession ends the conversation as shipped ExitConversationMode does.
-- It is recorded as an intervention, never labelled merely cosmetic.
-- No AddResponse/AddStatement, treaty choice, turn forcing or budget change.
local function skip(reason) print('CSC_OBSERVER_WARNING_DISMISS_SKIPPED',reason) end
local statement='__STATEMENT__'
if statement~='FIRST_MEET_NEAR_RECIPIENT'then skip('statement');return end
local exit=false
for row in GameInfo.DiplomacySelections()do
 if row.Type==statement and row.Key=='CHOICE_EXIT'then exit=true end
end
if not exit then skip('missing_exit_definition');return end
local from=__FROM__
local id=DiplomacyManager.FindOpenSessionID(0,from)
if type(id)~='number'or id<0 then skip('no_session');return end
local turn=__CORE_TURN__;local target=__TARGET_TURN__
if not(__CORE_ACTIVE__ and __CORE_LOCAL__==-1 and not __CORE_HUMAN__ and target-turn>0 and target-turn<=5)then skip('core_phase');return end
local ui=Game.GetCurrentGameTurn();if ui~=turn and ui~=turn-1 then skip('ui_clock');return end
if Game.GetLocalPlayer()~=-1 then skip('ui_control');return end
-- UI player objects can retain the pre-autoplay human flag. The fresh Core
-- proof above owns control authority; retain the independent UI clock/local gate.
if Players[0]:IsHuman()then print('CSC_OBSERVER_WARNING_STALE_UI_HUMAN',turn,ui)end
if not DiplomacyManager.IsSessionIDOpen(id)then skip('session_closed');return end
if DiplomacyManager.FindOpenSessionID(0,from)~=id then skip('session_changed');return end
local info=DiplomacyManager.GetSessionInfo(id)
if not info or info.FromPlayer~=from or info.ToPlayer~=0 then skip('participants');return end
print('CSC_OBSERVER_WARNING_DISMISS_BEGIN',turn,id,from,0)
DiplomacyManager.CloseSession(id)
if not ContextPtr:IsHidden()and type(Close)=='function'then Close()end
print('CSC_OBSERVER_WARNING_DISMISS_REQUESTED',turn,id,from,0)
