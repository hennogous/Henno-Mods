-- Controller-only observer recovery, not AI policy or cosmetic playback.
-- Evidence: stock DiplomacyActionView.lua CloseFocusedState/KeyHandler(Escape)
-- reaches ExitConversationMode -> DiplomacyManager.CloseSession (lines311,
-- 2685,2722 in the October2026 installation). Spy warnings have positive and
-- negative responses, so they must NOT enter the passive-message whitelist.
-- This closes the exact AI->observer0 session once, selecting no response,
-- promise, refusal, deal or war. The engine may attach implicit diplomatic
-- consequences to cancellation; the controller records that limitation.
-- Python supplies a fresh finite Core proof and newest same-participant CSV
-- NONE/INITIAL/Processing Immediately warning. GetSessionInfo exposes only
-- participants, not the live statement: do not claim more runtime knowledge.
local function skip(reason)print('CSC_OBSERVER_WARNING_DISMISS_SKIPPED',reason)end
local statement='__STATEMENT__'
if statement~='WARNING_STOP_SPYING_ON_ME'then skip('statement');return end
local turn=__CORE_TURN__;local target=__TARGET_TURN__
if not(__CORE_ACTIVE__ and __CORE_LOCAL__==-1 and not __CORE_HUMAN__ and target-turn>0 and target-turn<=5)then skip('core_phase');return end
local ui=Game.GetCurrentGameTurn()
if ui~=turn and ui~=turn-1 then skip('ui_clock');return end
if Game.GetLocalPlayer()~=-1 then skip('ui_control');return end
-- UI's cached human flag may lag Core during autoplay. Core proof owns control;
-- the independent UI turn and local-player checks still apply.
if Players[0]:IsHuman()then print('CSC_OBSERVER_WARNING_STALE_UI_HUMAN',turn,ui)end
if not GameInfo.DiplomacyStatements or not GameInfo.DiplomacySelections then skip('definitions_unavailable');return end
local group='WARNING_STOP_SPYING_ON_ME_FROM_AI'
local definitions=0
for row in GameInfo.DiplomacyStatements()do
 if row.Type==statement and row.Initiator=='AI'and row.SubType=='NONE'then
  definitions=definitions+1
  if row.Selections~=group then skip('statement_group_changed');return end
 end
end
if definitions==0 then skip('missing_statement_definition');return end
local choices={}
for row in GameInfo.DiplomacySelections()do
 if row.Type==group then
  -- Base stock includes IGNORE; the loaded XP2/modded DB may omit it. Require
  -- positive+negative and accept only the three source-reviewed keys. None of
  -- these handlers is invoked, including IGNORE (which can itself be a response).
  if row.Key~='CHOICE_POSITIVE'and row.Key~='CHOICE_NEGATIVE'and row.Key~='CHOICE_IGNORE'then skip('selection_group_changed');return end
  choices[row.Key]=true
 end
end
if not choices.CHOICE_POSITIVE or not choices.CHOICE_NEGATIVE then skip('missing_selection_definition');return end
local from=__FROM__
local id=DiplomacyManager.FindOpenSessionID(0,from)
if type(id)~='number'or id<0 then skip('no_session');return end
if not DiplomacyManager.IsSessionIDOpen(id)then skip('session_closed');return end
local info=DiplomacyManager.GetSessionInfo(id)
if not info or info.FromPlayer~=from or info.ToPlayer~=0 then skip('participants');return end
-- Resolve once, recheck immediately before the single close, and never derive
-- session identity from the CSV's initiator/player number.
if DiplomacyManager.FindOpenSessionID(0,from)~=id then skip('session_changed');return end
print('CSC_OBSERVER_WARNING_DISMISS_BEGIN',turn,id,from,0)
print('CSC_OBSERVER_CONVERSATION_CANCEL_BEGIN',turn,id,from,0,'ESC_EQUIVALENT_POSSIBLE_IMPLICIT_DIPLOMATIC_EFFECTS')
DiplomacyManager.CloseSession(id)
print('CSC_OBSERVER_WARNING_DISMISS_REQUESTED',turn,id,from,0)
if not DiplomacyManager.IsSessionIDOpen(id)then
 print('CSC_OBSERVER_CONVERSATION_CANCELLED',turn,id,from,0,'NO_EXPLICIT_RESPONSE_SELECTED')
else
 -- An asynchronous/unconfirmed close remains reserved by the controller. It
 -- cannot be replayed merely because this immediate read still says open.
 print('CSC_OBSERVER_CONVERSATION_CANCEL_PENDING',turn,id,from,0)
end
if not ContextPtr:IsHidden()and type(Close)=='function'then Close()end
