-- Shipped Congress RESULTS acknowledgement, never voting or proposals.
-- ClosePopup may submit WORLD_CONGRESS_LOOKED_AT_AVAILABLE; record this as
-- an observer acknowledgement, not a purely cosmetic dismissal.
local turn,target=__CORE_TURN__,__TARGET_TURN__
local function skip(reason) print('CSC_CONGRESS_REVIEW_SKIP',reason)end
if not(__CORE_ACTIVE__ and __CORE_LOCAL__==-1 and not __CORE_HUMAN__ and target-turn==__REMAINING__ and __REMAINING__>0 and __REMAINING__<=5)then skip('core_phase');return end
local ui=Game.GetCurrentGameTurn()
if ui~=turn and ui~=turn-1 then skip('ui_clock');return end
local localPlayer=Game.GetLocalPlayer()
if localPlayer~=0 and localPlayer~=-1 then skip('ui_player');return end
if ContextPtr:IsHidden()then skip('hidden');return end
-- Shipped UpdateNavButtons exposes Return only for stage4 non-proposal review.
if not Controls.ReturnButton:IsVisible()or Controls.ReturnButton:IsDisabled()
 or Controls.ReviewContainer:IsHidden()or not Controls.ResolutionContainer:IsHidden()
 or Controls.AcceptButton:IsVisible()or Controls.NextButton:IsVisible()
 or Controls.PassButton:IsVisible()or Controls.AvailableProposalsSelected:IsVisible()
 or not Controls.LastResultsSelected:IsVisible()then skip('not_results');return end
assert(type(ClosePopup)=='function','Missing shipped Congress ClosePopup')
print('CSC_CONGRESS_REVIEW_BEGIN',turn,ui,target)
ClosePopup()
print('CSC_CONGRESS_REVIEW_REQUESTED',turn,ui,ContextPtr:IsHidden())
