"""Common supplier-acquisition fixture; never imported by the live CSC mod.

Release one already-owned, unimproved mapped deposit beside the completed
Quarter. Both later arms must load this same inactive save. The edit is not
a purchase: native payment, correct-city ownership and improvement still need
independent observations. Do not add funds, technologies, units or buildings.
"""

def without_supplier_bid(source, case):
    """Matched diagnostic ablation: retain allowances/protection, remove only bid."""
    assert source.count(b'function P.SupplierAcquisitionOffers(')==1
    addition=('''
-- DIAGNOSTIC ONLY: exact supplier-offer ablation; allowances remain identical.
local supplierOffers=CSC_AI_QuarterPlacement.SupplierAcquisitionOffers
CSC_AI_QuarterPlacement.SupplierAcquisitionOffers=function(...)
 local rows=supplierOffers(...)
 for _,r in ipairs(rows)do
  if r.player==%d and r.city==%d and r.plot==%d then r.deltaQ8=nil end
 end
 return rows
end
'''%(case['player'],case['city'],case['purchasePlots'][0])).encode()
    return source+addition


INSPECT=r'''
for _,chain in ipairs(CSC_AI_QuarterPlacement.ReadChains(Players[3]))do
 if chain.city:GetID()==458758 and chain.plot:GetIndex()==788 then
  print('CSC_SUPPLIER_CHAIN',chain.ready,#chain.supply.base,chain.workingBase)
  local b=chain.city:GetBuildings()
  for _,p in ipairs(chain.profile.producers)do
   print('CSC_SUPPLIER_PRODUCER',p.Index,b:HasBuilding(p.Index),b:IsPillaged(p.Index))
  end
  for _,plot in ipairs(Map.GetAdjacentPlots(chain.plot:GetX(),chain.plot:GetY()))do
   local types=chain.profile.customers[plot:GetDistrictType()]
   local c=Cities.GetPlotPurchaseCity(plot)
   if types and c then
    local buildings=c:GetBuildings()
    for _,definition in pairs(types)do
     print('CSC_SUPPLIER_CUSTOMER',c:GetID(),plot:GetIndex(),definition.Index,
      buildings:HasBuilding(definition.Index),buildings:IsPillaged(definition.Index))
    end
   end
  end
 end
end
'''


PREPARE = r'''
assert(Game.GetCurrentGameTurn()==216 and Players[0]:IsHuman() and not AutoplayManager.IsActive())
local player=assert(Players[3]);assert(not player:IsHuman())
local city=assert(CityManager.GetCity(3,458758));assert(city:GetName()=='LOC_CITY_NAME_NUREMBERG')
local quarter=assert(Map.GetPlotByIndex(788))
local supplier=assert(Map.GetPlotByIndex(861))
assert(quarter:GetDistrictType()==GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index)
local complete=false
for i=0,city:GetDistricts():GetNumDistricts()-1 do
 local d=city:GetDistricts():GetDistrictByIndex(i)
 if d:GetType()==quarter:GetDistrictType() and d:GetX()==quarter:GetX() and d:GetY()==quarter:GetY() then
  complete=d:IsComplete() and not d:IsPillaged()
 end
end
assert(complete,'Supplier fixture needs the physically completed Quarter')
local owner=assert(Cities.GetPlotPurchaseCity(supplier))
assert(supplier:GetOwner()==3 and owner:GetID()==458758)
assert(supplier:GetResourceType()==GameInfo.Resources.RESOURCE_CSC_FLAX.Index)
assert(supplier:GetDistrictType()==-1 and supplier:GetImprovementType()==-1)
local farm=assert(GameInfo.Improvements.IMPROVEMENT_FARM)
local before=ImprovementBuilder.CanHaveImprovement(supplier,farm.Index,player:GetID())
local gold=player:GetTreasury():GetGoldBalance()
local terrain,feature,rivers=supplier:GetTerrainType(),supplier:GetFeatureType(),supplier:GetRiverCrossingCount()
-- Explicit common fixture edit: no AI command, payment or policy success.
WorldBuilder.CityManager():SetPlotOwner(supplier:GetX(),supplier:GetY(),false)
assert(supplier:GetOwner()==-1 and not Cities.GetPlotPurchaseCity(supplier))
assert(supplier:GetDistrictType()==-1 and supplier:GetImprovementType()==-1)
assert(supplier:GetResourceType()==GameInfo.Resources.RESOURCE_CSC_FLAX.Index)
assert(supplier:GetTerrainType()==terrain and supplier:GetFeatureType()==feature and supplier:GetRiverCrossingCount()==rivers)
assert(player:GetTreasury():GetGoldBalance()==gold)
print('CSC_SUPPLIER_RELEASED',Game.GetCurrentGameTurn(),861,gold,before,
 ImprovementBuilder.CanHaveImprovement(supplier,farm.Index,player:GetID()))
for _,unit in player:GetUnits():Members()do
 local definition=GameInfo.Units[unit:GetType()]
 if definition and definition.UnitType=='UNIT_BUILDER' then
  print('CSC_SUPPLIER_BUILDER',unit:GetID(),unit:GetX(),unit:GetY(),unit:GetBuildCharges())
 end
end
print('CSC_SUPPLIER_TECH',farm.PrereqTech,
 not farm.PrereqTech or player:GetTechs():HasTech(GameInfo.Technologies[farm.PrereqTech].Index))
'''
