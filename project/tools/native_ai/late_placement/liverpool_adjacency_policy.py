"""Diagnostic 1.4 common terrain derivative and positive-offer ablation.

The full arm uses unmodified main CSC policy. The original control removes
this city's positive Bakers entries after capacity trim. The viable control
instead excludes strong candidates from the shared owned/frontier comparator,
leaving ordinary viable fallback guidance. Neither writes a native replacement
value; both preserve deductions and all other decision channels.
"""

PREPARE=r'''
assert(Game.GetCurrentGameTurn()==25 and not AutoplayManager.IsActive())
local city=assert(CityManager.GetCity(4,131073))
assert(city:GetName()=='LOC_CITY_NAME_LIVERPOOL')
local plot=assert(Map.GetPlotByIndex(2571));local owner=assert(Cities.GetPlotPurchaseCity(plot))
assert(plot:GetOwner()==4 and owner:GetID()==131073 and plot:GetDistrictType()==-1)
assert(plot:GetResourceType()==-1 and plot:GetImprovementType()==-1 and plot:GetFeatureType()==-1)
assert(plot:GetTerrainType()==GameInfo.Terrains.TERRAIN_PLAINS_HILLS.Index and plot:GetRiverCrossingCount()==0)
local rule
for _,r in ipairs(CSC_Adjacency.ByDistrict.DISTRICT_CSC_BAKERS_QUARTER)do
 if r.ID=='CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS'then rule=r end
end
assert(rule and rule.AdjacencyType=='FROM_RINGS_CAO_TERRAIN_SETS' and rule.CustomAdjacentObject=='IsHills')
local first,last=CSC_Adjacency.Bounds(rule)
assert(first==0 and last==0 and rule.YieldChange==1)
assert(CSC_Adjacency.Count(rule,plot,city,4)==1)
-- Common fixture edit, never an AI action or part of shipping policy. This
-- removes the loaded self-hill Mill contribution without changing resources,
-- ownership, physical rivers, City Center or available customer footprints.
TerrainBuilder.SetTerrainType(plot,GameInfo.Terrains.TERRAIN_PLAINS.Index)
assert(CSC_Adjacency.Count(rule,plot,city,4)==0)
local strong=CSC_AI_QuarterAdjacencyValue('DISTRICT_CSC_BAKERS_QUARTER',Map.GetPlotByIndex(2497),city,4,false,'DISTRICT_COMMERCIAL_HUB')
local weak=CSC_AI_QuarterAdjacencyValue('DISTRICT_CSC_BAKERS_QUARTER',plot,city,4,false,'DISTRICT_COMMERCIAL_HUB')
assert(strong.total==4 and weak.total==3)
print('CSC_LIVERPOOL_ADJACENCY_PREPARED',2571,strong.total,weak.total)
'''

FILTER=b'''    -- Diagnostic control only. Remove positive Bakers site guidance for
    -- this one city, including its frontier alternative. Native unmodified
    -- values remain in competition; negative/material/customer entries and
    -- all Builder/building/repair arrays are preserved. No replacement bid.
    local removed=0
    for i=#entries,1,-1 do
        local entry=entries[i]
        if entry.player==4 and entry.city==131073 and entry.district==36
            and entry.delta>0 and not entry.customer then
            table.remove(entries,i);removed=removed+1
        end
    end
    print('CSC_ADJACENCY_DIAG_WITHHELD',turn,version+1,removed)
'''


def without_promotions(publisher):
    needle=b'    CSC_EARLY_DIAG_Retained(entries,turn,version+1)'
    assert publisher.count(needle)==1
    assert publisher.index(b'for i = #entries, capacity + 1, -1')<publisher.index(needle)
    return publisher.replace(needle,FILTER+needle)


STRONG_ABLATION=b'''    -- Diagnostic local strong-promotion ablation. Preserve native legality,
    -- weak-site deductions and ordinary viable fallback offers. This shared
    -- comparator serves both owned and frontier positive selection; excluding
    -- only the owned strong site would leave a strong frontier as a confound.
    if candidate.player==4 and candidate.city==131073 and candidate.district==36
        and candidate.adjacency>=preferredAdjacency then return false end
'''


def without_strong_promotions(scanner):
    # Keep original line endings so removal of the one injected block exactly
    # reproduces the archived full arm for the later artifact comparison.
    newline=b'\r\n' if b'\r\n' in scanner else b'\n'
    needle=b'local function betterQuarterSite(candidate, best)'+newline
    assert scanner.count(needle)==1
    assert scanner.count(b'if betterQuarterSite(candidate, best) then best = candidate end')==2
    return scanner.replace(needle,needle+STRONG_ABLATION)
