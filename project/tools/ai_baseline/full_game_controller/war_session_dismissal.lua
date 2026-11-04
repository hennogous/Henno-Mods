-- The declaration has ALREADY made both participants at war. The native
-- DECLARE_WAR_FROM_AI selection group must contain CHOICE_EXIT only. End that
-- log-verified conversation without selecting any war, peace, deal or response.
local function skip(why)print('CSC_OBSERVER_WARNING_DISMISS_SKIPPED',why)end
local from=__FROM__
if not(__CORE_ACTIVE__ and __CORE_LOCAL__==-1 and not __CORE_HUMAN__ and __TARGET_TURN__-__CORE_TURN__>0 and __TARGET_TURN__-__CORE_TURN__<=5)then skip('core_phase');return end
local ui=Game.GetCurrentGameTurn()
if ui~=__CORE_TURN__ and ui~=__CORE_TURN__-1 then skip('ui_clock');return end
if Game.GetLocalPlayer()~=-1 then skip('ui_control');return end
-- UI player objects can retain the pre-autoplay human flag. The fresh Core
-- proof above owns control authority; retain the independent UI clock/local gate.
if Players[0]:IsHuman()then print('CSC_OBSERVER_WARNING_STALE_UI_HUMAN',__CORE_TURN__,ui)end
local selections=0
for row in GameInfo.DiplomacySelections()do
 if row.Type=='DECLARE_WAR_FROM_AI'then
  selections=selections+1;if row.Key~='CHOICE_EXIT'then skip('non_exit_choice');return end
 end
end
if selections==0 then skip('missing_exit_definition');return end
if not Players[0]:GetDiplomacy():IsAtWarWith(from)then skip('war_not_already_declared');return end
local id=DiplomacyManager.FindOpenSessionID(0,from)
if type(id)~='number'or id<0 then skip('no_session');return end
if not DiplomacyManager.IsSessionIDOpen(id)then skip('session_closed');return end
if DiplomacyManager.FindOpenSessionID(0,from)~=id then skip('session_changed');return end
local info=DiplomacyManager.GetSessionInfo(id)
if not info or info.FromPlayer~=from or info.ToPlayer~=0 then skip('participants');return end
print('CSC_OBSERVER_WARNING_DISMISS_BEGIN',__CORE_TURN__,id,from,0)
DiplomacyManager.CloseSession(id)
if not ContextPtr:IsHidden()and type(Close)=='function'then Close()end
print('CSC_OBSERVER_WARNING_DISMISS_REQUESTED',__CORE_TURN__,id,from,0)
assert(Players[0]:GetDiplomacy():IsAtWarWith(from),'War state changed after conversation exit')
