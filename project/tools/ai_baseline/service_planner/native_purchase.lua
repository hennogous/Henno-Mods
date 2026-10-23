-- Loaded only by an explicitly authorized driver using the shared controller.
-- RequestCommand is the native gold-spending path. Never grant ownership/gold.
-- UI purchase events may lag; the Python adapter reconciles on a later read.
local r = CSC_SERVICE_PURCHASE_REQUEST
assert(type(r)=='table' and type(r.player)=='number' and type(r.city)=='number')
assert(r.purchase_plot~=nil and r.turn==Game.GetCurrentGameTurn(),'Stale purchase')
local player=assert(Players[r.player])
assert(player:IsAlive() and player:IsMajor() and not player:IsHuman(),'AI owner required')
local city=assert(CityManager.GetCity(r.player,r.city))
assert(city:GetOwner()==r.player,'City ownership changed')
local target=assert(Map.GetPlotByIndex(r.purchase_plot))
assert(target:GetOwner()==-1,'Purchase only unowned land')
local source=assert(Map.GetPlotByIndex(r.source_plot))
local def=assert(GameInfo.Districts['DISTRICT_CSC_'..r.quarter..'_QUARTER'])
if r.stepwise and r.established then
 assert(source:GetOwner()==r.player and source:GetDistrictType()==def.Index,'Established Quarter ownership/type changed')
 assert(city:GetDistricts():HasDistrict(def.Index)or city:GetBuildQueue():HasBeenPlaced(def.Hash),'Established city Quarter absent')
else
assert(not city:GetDistricts():HasDistrict(def.Index),'Same Quarter already exists')
assert(not city:GetBuildQueue():HasBeenPlaced(def.Hash),'Same Quarter already placed')
assert(source:GetOwner()==r.player or source:GetIndex()==r.purchase_plot or(r.stepwise and source:GetOwner()==-1 and r.remaining_tiles[tostring(source:GetIndex())]),'Source land unavailable')
assert(source:GetDistrictType()<0 and source:GetResourceType()<0
 and source:GetImprovementType()<0 and source:GetFeatureType()<0,'Source tile changed')
assert(source:CanHaveDistrict(def.Index,r.player,r.city),'Native potential legality changed')
end -- Established support acquires materials only; never another foundation.
local visibility=assert(PlayersVisibility[r.player])
assert(visibility:IsRevealed(target:GetX(),target:GetY()),'Unrevealed purchase')
local function visible(resource)
 local d=GameInfo.Resources[resource]
 if not d then return false end
 if d.PrereqTech then
  local t=GameInfo.Technologies[d.PrereqTech]
  if not t or not player:GetTechs():HasTech(t.Index)then return false end
 end
 if d.PrereqCivic then
  local t=GameInfo.Civics[d.PrereqCivic]
  if not t or not player:GetCulture():HasCivic(t.Index)then return false end
 end
 return true
end
local base,spec={},{}
for tag in GameInfo.TypeTags()do
 local d=GameInfo.Resources[tag.Type]
 if d then
  if tag.Tag=='CLASS_CSC_'..r.quarter..'_BASE'then base[d.Index]=true end
  if tag.Tag=='CLASS_CSC_'..r.quarter..'_SPEC'then spec[d.Index]=true end
 end
end
local actualBase,actualSpec=0,0
for _,p in ipairs(Map.GetAdjacentPlots(source:GetX(),source:GetY()))do
 local res=p:GetResourceType()
 local owned=p:GetOwner()==r.player or(p:GetIndex()==r.purchase_plot and p:GetOwner()==-1)
 if owned and visible(res)then
  if base[res]then actualBase=actualBase+1 end
  if spec[res]then actualSpec=actualSpec+1 end
 end
end
assert((r.material_first or actualBase>=1)and actualBase==r.base and actualSpec==r.specialty,'Supply projection changed')
if r.material_first then
 assert(r.remaining_tiles[tostring(r.purchase_plot)],'Purchase is outside the acquisition plan')
 local connectors=0
 for _ in pairs(r.plan_connectors or {})do connectors=connectors+1 end
 assert(connectors<=2,'Connector budget exceeded')
 assert(r.purchase_plot==r.source_plot or r.plan_materials[tostring(r.purchase_plot)]or(r.stepwise and r.plan_connectors and r.plan_connectors[tostring(r.purchase_plot)]),'Purchase is neither source, material nor declared connector')
 -- Validate the full marked supply plan without pretending the later purchases
 -- are already owned. The counts above describe only this one next native buy.
 local plannedBase,plannedSpec=0,0
 for _,p in ipairs(Map.GetAdjacentPlots(source:GetX(),source:GetY()))do
  if r.plan_materials[tostring(p:GetIndex())]then
   local res=p:GetResourceType()
   assert(p:GetOwner()==r.player or(p:GetOwner()==-1 and r.remaining_tiles[tostring(p:GetIndex())]),'Planned material ownership changed')
   assert(visibility:IsRevealed(p:GetX(),p:GetY())and visible(res),'Planned material no longer visible')
   if base[res]then plannedBase=plannedBase+1 end
   if spec[res]then plannedSpec=plannedSpec+1 end
  end
 end
 assert(plannedBase>0 and plannedSpec>0,'Marked plan no longer has Base + Specialty')
 assert(not r.service,'Strategy/Service matching disabled')
end
if r.service then
 assert(r.venue_type and r.customer_plot~=nil,'Missing Service customer')
 local adjacent=false
 for _,p in ipairs(Map.GetAdjacentPlots(source:GetX(),source:GetY()))do
  if p:GetIndex()==r.customer_plot and p:GetOwner()==r.player then adjacent=true end
 end
 assert(adjacent,'Service customer not adjacent or owned')
 local venue=assert(GameInfo.Buildings[r.venue_type])
 local customer=false
 for _,other in player:GetCities():Members()do
  local b=other:GetBuildings()
  if b:HasBuilding(venue.Index)and not b:IsPillaged(venue.Index)
   then
   local location=nil
   if type(b.GetBuildingLocation)=='function'then location=b:GetBuildingLocation(venue.Index)
   else
    -- UI CityBuildings lacks GetBuildingLocation. The adapter imports an exact
    -- Gameplay building-location readback immediately before this request.
    local s=assert(CSC_SERVICE_NATIVE,'Fresh Gameplay venue bridge required')
    assert(s.venues_turn==r.turn,'Stale Gameplay venue bridge')
    for _,v in ipairs(s.external_venues)do
     if v.owner==r.player and v.city==other:GetID()and v.type==r.venue_type and v.functioning then location=v.plot end
    end
   end
   if location==r.customer_plot then customer=true end
  end
 end
 assert(customer,'Service customer no longer functioning')
 if r.requires_specialty then assert(actualSpec>0,'Stage4 lacks Specialty')end
 if r.require_research_now then
  local civic=assert(GameInfo.Civics[r.civic])
  assert(player:GetCulture():HasCivic(civic.Index),'Strong Service research no longer ready')
 end
end
local treasury=player:GetTreasury()
local gold=treasury:GetGoldBalance()
local cost=city:GetGold():GetPlotPurchaseCost(r.purchase_plot)
assert(gold==r.gold and cost==r.price and cost>0,'Native price/gold changed')
assert(cost<=r.max_price and gold-cost>=r.reserve,'Purchase budget changed')
local pars={}
pars[CityCommandTypes.PARAM_PLOT_PURCHASE]=r.plot_purchase_parameter
pars[CityCommandTypes.PARAM_X]=target:GetX()
pars[CityCommandTypes.PARAM_Y]=target:GetY()
assert(r.plot_purchase_parameter==true,'Native plot-purchase flag must be boolean true, independent of current UI mode')
local commandLegal=CityManager.CanStartCommand(city,CityCommandTypes.PURCHASE,pars)
if not commandLegal then
 assert(r.material_first and r.allow_ai_native_request_probe==true,'Native purchase command unavailable; explicit AI native-request test not enabled')
 local visible,results=CityManager.CanStartCommand(city,CityCommandTypes.PURCHASE,true,pars,true)
 local found=false
 for _,idx in ipairs(visible and results and results[CityCommandResults.PLOTS]or {})do if idx==r.purchase_plot then found=true end end
 assert(found,'Selected plot absent from native visible purchase reach')
end
print('CSC_SERVICE_PURCHASE_PREFLIGHT',r.player,r.purchase_plot,tostring(commandLegal),tostring(r.allow_ai_native_request_probe),Game.GetLocalPlayer())
-- Begin is printed before the only mutation; no handler retries this command.
print('CSC_SERVICE_PURCHASE_BEGIN',r.player,r.city,r.purchase_plot,gold,cost)
local returned=CityManager.RequestCommand(city,CityCommandTypes.PURCHASE,pars)
print('CSC_SERVICE_PURCHASE_REQUEST_RETURN',tostring(returned))
print('CSC_SERVICE_PURCHASE_REQUESTED',r.player,r.city,r.purchase_plot)
