"""Diagnostic1.7 remaining-leg fixture for the already competitive23 window.

Temporarily absent existing Cattle796 lets MAIN CSC publish a genuine no-Base
scope at22. The exclusive controller restores the exact resource before any
turn advances. Ordinary23 publication must withdraw that scope, and actual
native choice/request must follow. No bid, eligibility rule, plan or queue is
overridden. This complements C165; it is not a continuous city-level cycle.
"""

PREPARE=r'''
-- Diagnostic map fixture only, after includes but before initial publication.
-- Check every original and uncertainty gate before the sole removal. A failed
-- guard must not produce a partly changed world or a guessed no-Base claim.
do
 assert(CSC_WASH_OPPORTUNITY_STATE==nil and Game.GetCurrentGameTurn()==22)
 local player=assert(Players[3]);local city=assert(CityManager.GetCity(3,65536))
 assert(not player:IsHuman() and city:GetName()=='LOC_CITY_NAME_WASHINGTON')
 local district=assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER)
 assert(district.Index==36 and not city:GetDistricts():HasDistrict(district.Index))
 local site=assert(Map.GetPlotByIndex(870));local plot=assert(Map.GetPlotByIndex(796))
 assert(site:GetOwner()==3 and Cities.GetPlotPurchaseCity(site):GetID()==65536 and site:GetDistrictType()==-1)
 assert(plot:GetOwner()==3 and Cities.GetPlotPurchaseCity(plot):GetID()==131073)
 assert(plot:GetResourceType()==GameInfo.Resources.RESOURCE_CATTLE.Index)
 assert(plot:GetResourceCount()==1 and plot:GetImprovementType()==-1 and plot:GetDistrictType()==-1)
 assert(Map.GetPlotDistance(site:GetX(),site:GetY(),plot:GetX(),plot:GetY())==1)
 local A=assert(CSC_Adjacency)
 -- Includes create an empty rule/tag cache. Initialize only database definitions
 -- here; the normal main refresh has not run yet. This does not write map state
 -- or publish policy, and main still performs its ordinary initialization.
 A.Initialize()
 local visibility=assert(PlayersVisibility[3]);local definitions=0
 for resource in GameInfo.Resources()do
  if A.HasTag('CLASS_CSC_BAKERS_BASE',resource.ResourceType)then
   definitions=definitions+1
   assert(A.ResourceVisible(3,resource.Index),'Hidden Base type; do not prepare fixture')
   print('CSC_WASH_BASE_DEFINITION',resource.ResourceType,resource.Index,true)
  end
 end
 assert(definitions>0 and A.HasTag('CLASS_CSC_BAKERS_BASE','RESOURCE_CATTLE'))
 for _,neighbor in ipairs(Map.GetAdjacentPlots(site:GetX(),site:GetY()))do
  assert(visibility:IsRevealed(neighbor:GetX(),neighbor:GetY()),'Unknown neighbor; do not prepare fixture')
  local resource=GameInfo.Resources[neighbor:GetResourceType()]
  local base=resource and A.HasTag('CLASS_CSC_BAKERS_BASE',resource.ResourceType)or false
  assert(not base or neighbor:GetIndex()==796 or neighbor:GetOwner()~=3 and neighbor:GetOwner()~=-1,
   'Another credible Base; this is not the selected missing-Base window')
  print('CSC_WASH_SOURCE_NEIGHBOR',neighbor:GetIndex(),neighbor:GetOwner(),
   neighbor:GetResourceType(),neighbor:GetImprovementType(),tostring(base))
 end
 CSC_WASH_OPPORTUNITY_STATE={resource=plot:GetResourceType(),count=plot:GetResourceCount(),
  terrain=plot:GetTerrainType(),feature=plot:GetFeatureType(),river=plot:GetRiverCrossingCount(),
  gold=player:GetTreasury():GetGoldBalance(),population=city:GetPopulation(),
  queued=city:GetBuildQueue():CurrentlyBuilding(),writes=0}
 local original=CSC_WASH_OPPORTUNITY_STATE
 print('CSC_WASH_SOURCE',22,796,3,131073,original.resource,original.count,
  original.terrain,original.feature,original.river,original.gold,original.population,original.queued)
 -- One declared temporary resource absence, not a harvest or native AI action.
 ResourceBuilder.SetResourceType(plot,-1);original.writes=1
 assert(plot:GetResourceType()==-1 and plot:GetImprovementType()==-1)
 print('CSC_WASH_BASE_ABSENT',22,796,original.writes)
end

function CSC_WASH_OPPORTUNITY_Snapshot()
 local state=assert(CSC_WASH_OPPORTUNITY_STATE)
 local plot=assert(Map.GetPlotByIndex(796));local city=assert(CityManager.GetCity(3,65536))
 local profile
 for _,p in ipairs(CSC_AI_QuarterPlacement.StageTwoProfiles())do if p.key=='BAKERS'then profile=p end end
 local supply=CSC_AI_QuarterPlacement.ReadSuppliers(Players[3],Map.GetPlotByIndex(870),assert(profile))
 local status=assert(CE_AIDistrictScoresStatus());local version=assert(tonumber(status:match('"version":(%d+)')))
 print('CSC_WASH_STATE',Game.GetCurrentGameTurn(),version,state.writes,plot:GetResourceType(),
  plot:GetResourceCount(),#supply.base,city:GetPopulation(),city:GetBuildQueue():CurrentlyBuilding())
 for _,base in ipairs(supply.base)do
  print('CSC_WASH_SUPPLIER',Game.GetCurrentGameTurn(),version,base.plot,base.resource,
   tostring(base.ready),tostring(base.working))
 end
 print('CSC_WASH_DECLINE',Game.GetCurrentGameTurn(),version,
  CE_AIDistrictDeclineReceipt(version,3,65536,36,870))
end
'''

RESTORE=r'''
assert(Game.GetCurrentGameTurn()==22 and not AutoplayManager.IsActive()
 and Game.GetLocalPlayer()==0 and Players[0]:IsHuman())
local state=assert(CSC_WASH_OPPORTUNITY_STATE);assert(state.writes==1)
local player=assert(Players[3]);local city=assert(CityManager.GetCity(3,65536))
local plot=assert(Map.GetPlotByIndex(796))
assert(plot:GetOwner()==3 and Cities.GetPlotPurchaseCity(plot):GetID()==131073)
assert(plot:GetResourceType()==-1 and plot:GetImprovementType()==-1 and plot:GetDistrictType()==-1)
assert(plot:GetTerrainType()==state.terrain and plot:GetFeatureType()==state.feature
 and plot:GetRiverCrossingCount()==state.river)
assert(player:GetTreasury():GetGoldBalance()==state.gold and city:GetPopulation()==state.population
 and city:GetBuildQueue():CurrentlyBuilding()==state.queued)
local status=assert(CE_AIDistrictScoresStatus());local version=assert(tonumber(status:match('"version":(%d+)')))
local prior=assert(CE_AIDistrictDeclineReceipt(version,3,65536,36,870))
assert(prior:match('"staged":1'),'No genuine prior main no-Base scope; do not restore as a test')
print('CSC_WASH_PRIOR_SCOPE',22,version,prior)
-- Exactly restore the existing source resource. No native acquisition or
-- improvement claim, no plan cancellation and no forced packet publication.
ResourceBuilder.SetResourceType(plot,state.resource,state.count);state.writes=2
assert(plot:GetResourceType()==state.resource and plot:GetResourceCount()==state.count)
assert(plot:GetImprovementType()==-1 and plot:GetOwner()==3 and Cities.GetPlotPurchaseCity(plot):GetID()==131073)
assert(plot:GetTerrainType()==state.terrain and plot:GetFeatureType()==state.feature
 and plot:GetRiverCrossingCount()==state.river)
assert(player:GetTreasury():GetGoldBalance()==state.gold and city:GetPopulation()==state.population
 and city:GetBuildQueue():CurrentlyBuilding()==state.queued)
assert(tonumber(CE_AIDistrictScoresStatus():match('"version":(%d+)'))==version,'Fixture forced a publication')
print('CSC_WASH_BASE_RESTORED',22,796,state.resource,state.count,state.writes)
CSC_WASH_OPPORTUNITY_Snapshot()
'''

RECEIPT=b'''    -- Read-only lineage before the normal replacement commit.
    CSC_WASH_OPPORTUNITY_Snapshot()
'''


def stage(publisher):
    initialization=b'local identityPrefix = '
    publication=b'    local accepted, message = bridge.Publish('
    assert publisher.count(initialization)==publisher.count(publication)==1
    publisher=publisher.replace(initialization,PREPARE.encode('utf-8')+b'\n'+initialization)
    return publisher.replace(publication,RECEIPT+publication)
