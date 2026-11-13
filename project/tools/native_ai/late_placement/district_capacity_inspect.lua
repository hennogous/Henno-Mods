-- Diagnostic-only UI reader: saved city facts -> shipped production legality.
-- This does not publish a bid or create a contract. It advances no game turns.
-- Capacity is a city-wide prerequisite, distinct from a site's economic value.
-- The ordinary ProductionPanel uses CanProduce(hash,false,true); its returned
-- reasons are native UI evidence, not an observed rejection of an AI request.
local targets={
 {1,196610,'BAKERS'},{4,65536,'BAKERS'},{4,65536,'TAILORS'},
 {4,131073,'BAKERS'},{4,262147,'BAKERS'},{5,131073,'BAKERS'},
}
local turn=Game.GetCurrentGameTurn()
for _,target in ipairs(targets)do
 local player,cityID,quarter=target[1],target[2],target[3]
 local city=assert(CityManager.GetCity(player,cityID),'Missing saved city')
 local definition=assert(GameInfo.Districts['DISTRICT_CSC_'..quarter..'_QUARTER'])
 assert(definition.RequiresPopulation==true or definition.RequiresPopulation==1,
  'Quarter no longer uses population capacity')
 local districts=city:GetDistricts()
 local used=districts:GetNumZonedDistrictsRequiringPopulation()
 local allowed=districts:GetNumAllowedDistrictsRequiringPopulation()
 local canProduce,results=city:GetBuildQueue():CanProduce(definition.Hash,false,true)
 print('CSC_CAPACITY_CITY',turn,player,cityID,quarter,city:GetName(),
  city:GetPopulation(),used,allowed,tostring(canProduce),
  tostring(districts:HasDistrict(definition.Index)))
 local reasons=results and results[CityCommandResults.FAILURE_REASONS]
 for _,reason in ipairs(reasons or{})do
  print('CSC_CAPACITY_REASON',turn,player,cityID,quarter,reason)
 end
end
assert(Game.GetCurrentGameTurn()==turn,'Clock changed during saved-state inspection')
print('CSC_CAPACITY_FACTS_COMPLETE',turn,#targets)
