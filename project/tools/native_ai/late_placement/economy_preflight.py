"""Read-only qualification of native pricing in an owned shared-controller game.

No unlocks, score offers or world edits. The main CSC publisher is the only
policy. This checks helper availability/ABI and loaded district-slot contracts;
it does not prove that a complete economic bid won or produced a benefit.
"""
from driver import parse, require, write_json


def inspect(controller, output):
    raw = controller.cmd('''
local status=assert(CE_AIEconomyStatus)()
print('CSC_ECONOMY_STATUS='..status)
local function flag(value)return value==true or value==1 end
assert(flag(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.RequiresPopulation))
assert(flag(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.RequiresPopulation))
local count=0
for _,p in ipairs(PlayerManager.GetAliveMajors())do
 if not p:IsHuman()then for _,city in p:GetCities():Members()do
  local owner,id=p:GetID(),city:GetID()
  local stream=CE_AIYieldStreamValue(owner,id,GameInfo.Yields.YIELD_PRODUCTION.Index,256,0,50,1024)
  local fixed=CE_AIYieldFixedValue(owner,id,GameInfo.Yields.YIELD_GOLD.Index,-70*256,0,1024)
  local amenity=CE_AIAmenityStreamValue(owner,id,1,0,50,1024)
  assert(stream and stream>0,'Native production stream unavailable')
  assert(fixed and fixed<0,'Native fixed invoice unavailable')
  assert(amenity~=nil,'Native amenity stream unavailable')
  assert(CE_AIYieldStreamValue(owner,id,-1,256,0,50,1024)==nil)
  assert(CE_AIYieldStreamValue(owner,id,0,256,50,50,1024)==nil)
  assert(CE_AIYieldStreamValue(owner,2147483647,0,256,0,50,1024)==nil)
  print('CSC_ECONOMY_QUOTE='..table.concat({owner,id,stream,fixed,amenity,type(stream)},','))
  count=count+1
 end end
end
assert(count>0,'No AI city for economic qualification')
print('CSC_ECONOMY_PREFLIGHT_OK='..count)
''', 'GameCore_Tuner', 'read-only-economy-preflight')
    (output/'economy-preflight.txt').write_text(raw,encoding='utf-8')
    status=parse(raw,'CSC_ECONOMY_STATUS')
    require(status['pricingReady']==status['finalReady']==1,'Economic interface not ready')
    require('CSC_ECONOMY_PREFLIGHT_OK=' in raw,'Economic preflight did not complete')
    write_json(output/'economy-preflight.json',dict(verified=True,status=status,
        read_only=True,construction_or_service_claim=False))
    facts=controller.cmd('''
local ui=assert(ExposedMembers.CSC_Adjacency)
assert(type(ui.GetDistrictCapacity)=='function','District capacity UI reader unavailable')
local capacityKnown=0
for _,p in ipairs(PlayerManager.GetAliveMajors())do if not p:IsHuman()then
 local snapshot=CSC_AI_EconomyFacts.New(p,CSC_AI_QuarterPlacement,ui)
 for _,city in p:GetCities():Members()do
  local production=ui.GetEconomyCityNumber(p:GetID(),city:GetID(),'yield',GameInfo.Yields.YIELD_PRODUCTION.Index)
  local cost=ui.GetEconomyCityNumber(p:GetID(),city:GetID(),'district',GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index)
  local research=snapshot.Research('civic','CIVIC_CRAFTSMANSHIP')
  -- Read-only qualification of the integrated fact bridge. This snapshot is
  -- not an exact-time production admission; stale UI records remain explicit.
  local capacity=snapshot.DistrictCapacity(city)
  if capacity.known then capacityKnown=capacityKnown+1 end
  print('CSC_ECONOMY_CAPACITY='..table.concat({p:GetID(),city:GetID(),tostring(capacity.population),tostring(capacity.used),tostring(capacity.allowed),capacity.reason},','))
  print('CSC_ECONOMY_FACTS='..table.concat({p:GetID(),city:GetID(),tostring(production),tostring(cost),tostring(research)},','))
  assert(production and production>0 and cost and cost>0 and research<math.huge,'Incomplete economic readiness facts')
 end
end end
assert(capacityKnown>0,'No live district capacity facts agreed with Gameplay')
print('CSC_ECONOMY_FACTS_OK')
''','CSC_AI_BakersGameplay','read-only-economy-facts-preflight')
    (output/'economy-facts-preflight.txt').write_text(facts,encoding='utf-8')
    require('CSC_ECONOMY_FACTS_OK' in facts,'Economic fact binding incomplete')
