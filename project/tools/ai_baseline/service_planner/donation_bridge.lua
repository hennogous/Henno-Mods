-- UI-only native quotes and exact city assignment, exposed as closures as in
-- RH's UI/GamePlay bridge. This experiment does not enable RH or copy its code.
ExposedMembers.CSC_DONATION_UI={}
local B=ExposedMembers.CSC_DONATION_UI
local function city(r)return assert(CityManager.GetCity(r.player,r.city),'City absent')end
function B.Quote(r,index)
 local c=city(r);local p=assert(Map.GetPlotByIndex(index));local player=assert(Players[r.player])
 local def=assert(GameInfo.Districts['DISTRICT_CSC_'..r.quarter..'_QUARTER']);local source=assert(Map.GetPlotByIndex(r.source))
 local canproduce=c:GetBuildQueue():CanProduce(def.Hash,false,true)
 local pars={};pars[CityCommandTypes.PARAM_PLOT_PURCHASE]=true
 local visible,targets=CityManager.CanStartCommand(c,CityCommandTypes.PURCHASE,true,pars,true)
 local reach=false;for _,i in ipairs(visible and targets and targets[CityCommandResults.PLOTS]or {})do if i==index then reach=true end end
 local ownercity=Cities.GetPlotPurchaseCity(p)
 return {turn=Game.GetCurrentGameTurn(),gold=player:GetTreasury():GetGoldBalance(),owner=p:GetOwner(),
  city_owner=c:GetOwner(),plot_city=ownercity and ownercity:GetID()or -1,
  price=c:GetGold():GetPlotPurchaseCost(index),revealed=PlayersVisibility[r.player]:IsRevealed(p:GetX(),p:GetY()),
  within_range=Map.GetPlotDistance(c:GetX(),c:GetY(),p:GetX(),p:GetY())<=3,native_reach=reach,
  source_potential=source:CanHaveDistrict(def.Index,r.player,r.city),can_produce=canproduce,
  same_quarter=c:GetDistricts():HasDistrict(def.Index)or c:GetBuildQueue():HasBeenPlaced(def.Hash)}
end
-- Ownership mutation is Gameplay-only, never invoked through this UI bridge.
function B.Owner(r,index)
 local p=assert(Map.GetPlotByIndex(index));local c=Cities.GetPlotPurchaseCity(p)
 return {owner=p:GetOwner(),plot_city=c and c:GetID()or -1,city_owner=c and c:GetOwner()or -1}
end
print('CSC_DONATION_UI_READY')
