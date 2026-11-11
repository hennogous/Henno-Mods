"""Diagnostic fixture/control for 1.3; none of this is installed CSC policy.

Both arms load one common map derivative. Main CSC still supplies the live
model, ordinary Q8 bands, eligibility and CE publication. The control withholds
only one projected Mill rule at one site; it never writes a native score itself.
"""

PREPARE=r'''
assert(Game.GetCurrentGameTurn()==25 and not AutoplayManager.IsActive())
local city=assert(CityManager.GetCity(4,131073))
assert(city:GetName()=='LOC_CITY_NAME_LIVERPOOL')
assert(not city:GetDistricts():HasDistrict(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index))
local removed={{2572,'RESOURCE_CSC_FLAX',0},{2498,'RESOURCE_WHEAT',-1}}
-- Common controlled map preparation, not an AI action or a shipping map pass.
-- Validate ALL originals before touching either resource. Preserve the Maize,
-- actual river edges, City Center and future Commercial Hub footprint.
for _,r in ipairs(removed)do
 local p=assert(Map.GetPlotByIndex(r[1]));local buyer=assert(Cities.GetPlotPurchaseCity(p))
 assert(p:GetOwner()==4 and buyer:GetID()==131073)
 assert(p:GetResourceType()==GameInfo.Resources[r[2]].Index and p:GetDistrictType()==r[3])
 assert(p:GetImprovementType()==-1)
end
for _,r in ipairs(removed)do ResourceBuilder.SetResourceType(Map.GetPlotByIndex(r[1]),-1)end
for _,r in ipairs(removed)do assert(Map.GetPlotByIndex(r[1]):GetResourceType()==-1)end
local site=assert(Map.GetPlotByIndex(2497));assert(site:GetRiverCrossingCount()==2 and site:GetDistrictType()==-1)
local forecast=CSC_AI_QuarterAdjacencyValue('DISTRICT_CSC_BAKERS_QUARTER',site,city,4,false,'DISTRICT_COMMERCIAL_HUB')
assert(forecast.total==4 and forecast.production==2 and forecast.gold==2)
print('CSC_LIVERPOOL_RIVER_PREPARED',2572,2498,2496,forecast.total)
'''

OMISSION=b'''    -- Diagnostic counterfactual: preserve real map/native forecasts and
    -- omit only this site's prospective Water Mill river input to CSC's model.
    -- Main policy must recompute ranking and its ordinary +48/+24 Q8 offer.
    if pid==4 and city:GetID()==131073 and plot:GetIndex()==2497
     and r.ID=='CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER' then count=0 end
'''


def without_river(scanner):
    needle=b'    local count=A.Count(r,plot,city,pid);local amount=A.Amount(r,count)'
    assert scanner.count(needle)==1
    return scanner.replace(needle,b'    local count=A.Count(r,plot,city,pid)\n'+OMISSION+
        b'    local amount=A.Amount(r,count)')
