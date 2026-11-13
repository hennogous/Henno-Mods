-- Diagnostic read-only deployment check, never live AI policy.
-- Require the consumers used by the ten integrated placement capabilities.
-- A score-only fallback is useful to players but cannot qualify this full run
-- as exercising acquisition acknowledgement, admission and material protection.
local scope=__SCOPE__
assert(Game.GetCurrentGameTurn()==1 and not AutoplayManager.IsActive())
assert(CSC_AI_QuarterPlacement and CSC_AI_QuarterSiteForecasts and CSC_AI_DistrictBridge)
assert(CSC_AI_EconomyModel and CSC_AI_EconomyFacts and CSC_AI_EconomyAdapters,
 'Central economic policy modules missing')
assert(GameInfo.CSC_AI_Profile==nil,'Legacy policy loaded')
-- Validate before constructing the table: a nil value otherwise vanishes
-- from pairs(), which could silently skip a required missing consumer.
local function required(name,getter)
 assert(type(getter)=='function','Missing '..name..' consumer')
 return getter
end
-- These UI wrappers are required dependencies of the economic facts, even
-- though the policy itself runs in Gameplay. A DLL/API-only check can pass
-- while obsolete packaged UI bindings silently make every build time unknown.
local ui=assert(ExposedMembers and ExposedMembers.CSC_Adjacency,'Missing economic UI boundary')
required('city number',ui.GetEconomyCityNumber)
required('research number',ui.GetEconomyResearchNumbers)
required('plot facts',ui.GetEconomyPlotFacts)
required('district capacity',ui.GetDistrictCapacity)
local readers={
 district=required('district',CE_AIDistrictScoresStatus),
 builder=required('builder',CE_AIBuilderProtectionStatus),
 harvest=required('harvest',CE_AIBuilderHarvestProtectionStatus),
 wonder=required('wonder',CE_AISupplierWonderProtectionStatus),
 nomination=required('nomination',CE_AIBuildingNominationStatus),
 repair=required('repair',CE_AIDistrictRepairStatus),
 exclusion=required('exclusion',CE_AISupplierExclusionStatus),
 ownership=required('ownership',CE_AIDistrictPurchaseCompletionStatus),
 decline=required('decline',CE_AIDistrictDeclineStatus),
}
-- This trial qualifies the new main-mod economy, not successful legacy
-- fallback. Require its transports now and check readiness at every census.
local economyStatus=required('economy',CE_AIEconomyStatus)
required('final value',CE_AIDistrictScoresFinalEntry)
required('managed type',CE_AIDistrictScoresManagedType)
required('managed readback',CE_AIDistrictScoresManagedReceipt)
required('yield price',CE_AIYieldStreamValue)
required('fixed price',CE_AIYieldFixedValue)
required('amenity price',CE_AIAmenityStreamValue)
function CSC_FULL_RUN_Health()
 for name,getter in pairs(readers)do
  assert(type(getter)=='function','Missing '..name..' consumer')
  local status=getter()
  -- The exclusion API reports readiness/capacity but has no faults field.
  -- Do not invent a mandatory counter absent from that published schema.
  assert(type(status)=='string'and status:match('"ready":1')
   and(name=='exclusion'or status:match('"faults":0')),
   'Unavailable/faulted '..name..' consumer: '..tostring(status))
  print('CSC_FULL_RUN_HEALTH',Game.GetCurrentGameTurn(),name,status)
 end
 local status=economyStatus()
 assert(type(status)=='string'and status:match('"pricingReady":1')and status:match('"finalReady":1'),
  'Economic pricing/final transport unavailable: '..tostring(status))
 print('CSC_FULL_RUN_ECONOMY_HEALTH',Game.GetCurrentGameTurn(),status)
end
CSC_FULL_RUN_Health()
local y=assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT)
for _,key in ipairs({'BAKERS','TAILORS'})do
 local value=assert(GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER']).RequiresPopulation
 assert(value==true or value==1,'Quarter must consume a population-limited district slot')
end
assert(y.DefaultValue==1)
local biases=0
for r in GameInfo.AiFavoredItems()do
 if r.ListType=='DefaultYieldBias'and r.Item==y.YieldType then
  assert(r.Value==25);biases=biases+1
 end
end
assert(biases==1)
local links=0
for edge in GameInfo.District_Adjacencies()do
 local r=GameInfo.Adjacency_YieldChanges[edge.YieldChangeId]
 if r and r.YieldType==y.YieldType then
  assert(r.YieldChange==1 and r.TilesRequired==1)
  links=links+1
  print('CSC_FULL_RUN_NATIVE_LINK',edge.DistrictType,edge.YieldChangeId,r.AdjacentDistrict)
 end
end
assert(links>0)
for _,id in ipairs(scope.players)do
 assert(Game:GetProperty('CSC_AI_OriginalHuman_'..id)==0,'Original AI seat missing')
end
assert(Game:GetProperty('CSC_AI_OriginalHuman_0')==1,'Original human seat missing')
print('CSC_FULL_RUN_PREFLIGHT_OK',Game.GetCurrentGameTurn(),links,y.Index)
