-- Opt-in endpoint study: use only the shipped One More Turn button, after an
-- actual winner and visible/enabled UI. Never dismiss defeat without extension.
local function skip(reason)print('CSC_ENDGAME_SKIP',reason)end
if __CORE_ACTIVE__ or __CORE_TURN__>=__TARGET__ or __TARGET__>__ENDPOINT__ or __TARGET__-__CORE_TURN__~=__REMAINING__ or __REMAINING__<1 or __REMAINING__>5 then skip('budget');return end
if __CORE_LOCAL__~=0 or not __CORE_HUMAN__ then skip('control');return end
if ContextPtr:IsHidden()then skip('hidden');return end
local team,kind=Game.GetWinningTeam()
if team==nil or team<0 or kind==nil or kind<0 then skip('no_winner');return end
local turn=Game.GetCurrentGameTurn()
if turn~=__CORE_TURN__ and turn~=__CORE_TURN__-1 then skip('clock');return end
if Game.GetLocalPlayer()~=0 or not Players[0]:IsHuman()then skip('local_control');return end
if Controls.BackButton:IsHidden()or Controls.BackButton:IsDisabled()then skip('not_extendable');return end
assert(type(OnBack)=='function','Shipped One More Turn handler absent')
print('CSC_ENDGAME_CONTINUE_BEGIN',team,kind,turn)
OnBack()
print('CSC_ENDGAME_CONTINUE_REQUESTED',ContextPtr:IsHidden())
