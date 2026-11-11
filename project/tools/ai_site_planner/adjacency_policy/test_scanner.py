"""Exercise scanner with the real shared core and mocked native map counts."""
import argparse,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[3]
SCANNER=ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_AdjacencyScan.lua'
HARNESS=r"""
function info(rows,key)local t={};for _,r in ipairs(rows)do t[r[key]]=r;t[r.Index]=r end;return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})end
local b='DISTRICT_CSC_BAKERS_QUARTER';local t='DISTRICT_CSC_TAILORS_QUARTER'
GameInfo={Districts=info({{Index=0,DistrictType='DISTRICT_CITY_CENTER'},{Index=1,DistrictType=b},{Index=2,DistrictType=t},{Index=4,Hash=1004,DistrictType='DISTRICT_HARBOR',RequiresPopulation=true},{Index=5,Hash=1005,DistrictType='DISTRICT_COMMERCIAL_HUB'},{Index=6,DistrictType='DISTRICT_RURALCOMMUNITYA'}},'DistrictType'),Buildings=info({{Index=1,BuildingType='BUILDING_CSC_BAKERS_WATER_MILL'},{Index=2,BuildingType='BUILDING_CSC_BAKERS_WIND_MILL'}},'BuildingType'),Policies=info({{Index=1,PolicyType='POLICY_TEST'}},'PolicyType')}
POLICY=false;MILLS=false
city={GetBuildings=function()return {HasBuilding=function()return MILLS end}end}
player={IsHuman=function()return false end,GetCities=function()return {Members=function()local once=false;return function()if not once then once=true;return 1,city end end end}end,GetCulture=function()return {IsPolicyActive=function()return POLICY end}end}
Players={[1]=player}
PlayerConfigurations={[1]={GetCivilizationTypeName=function()return 'CIV_TEST' end,GetLeaderTypeName=function()return 'LEADER_TEST' end}}
for _,name in ipairs({'Leaders','CivilizationTraits','LeaderTraits','DistrictReplaces','ExcludedDistricts'})do GameInfo[name]=info({},'Type')end
plot={river=0,hills=0,IsRiver=function(s)return s.river>0 end,GetRiverCrossingCount=function(s)return s.river end}
function rule(id,y,amount,owner,key)return {ID=id,YieldType=y,YieldChange=amount,ModifierOwner=owner or'DistrictModifiers',WhoIsTheOwner=key,ProvideType='SelfBonus',AdjacencyType='FROM_RIVER_CROSSING'}end
local base=rule('materials','YIELD_PRODUCTION',1);local sales=rule('customers','YIELD_GOLD',1)
local river=rule('river','YIELD_PRODUCTION',0.5)
local water=rule('water','YIELD_PRODUCTION',0.5,'BuildingModifiers','BUILDING_CSC_BAKERS_WATER_MILL')
local wind=rule('wind','YIELD_PRODUCTION',1,'BuildingModifiers','BUILDING_CSC_BAKERS_WIND_MILL')
local policy=rule('policy','YIELD_GOLD',1,'PolicyModifiers','POLICY_TEST')
CSC_Adjacency.ByDistrict={[b]={base,sales,water,wind,policy},[t]={base,sales,river,policy}}
local nativeCount=CSC_Adjacency.Count
function CSC_Adjacency.Count(r,p,c,pid)if r.ID=='materials'then return 2 elseif r.ID=='customers'or r.ID=='policy'then return 1 elseif r.ID=='wind'then return p.hills end;return nativeCount(r,p,c,pid)end
"""

BAKERS_SITES = r"""
local existing, placed, unlocked = false, false, true
local targetsRead, checked, gameplayChecked = 0, {}, {}
local cityDistricts = {HasDistrict=function(_, id) return existing and id==1 end}
local queue = {
    HasBeenPlaced=function(_, hash) assert(hash==1001); return placed end,
    CanProduce=function(_, hash, _, test) assert(hash==1001 and test); return unlocked end,
}
GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Hash = 1001
GameInfo.Resources = info({{Index=88,ResourceType='RESOURCE_CATTLE'}},'ResourceType')
CSC_Adjacency.HasTag = function(tag, kind) return tag=='CLASS_CSC_BAKERS_BASE' and kind=='RESOURCE_CATTLE' end
local cattleVisible = true
CSC_Adjacency.ResourceVisible = function() return cattleVisible end
city.GetID = function() return 15 end
city.GetX = function() return 2 end
city.GetY = function() return 3 end
city.GetOwner = function() return 1 end
city.GetDistricts = function() return cityDistricts end
city.GetBuildQueue = function() return queue end
player.GetID = function() return 1 end
local plots = {}
local function makeSite(id, river, host, base, spec, resource)
    local site = {
        id=id, river=river, hills=0, host=host, base=base, spec=spec,
        IsRiver=plot.IsRiver, GetRiverCrossingCount=plot.GetRiverCrossingCount,
        GetX=function() return id end, GetY=function() return 3 end,
        GetIndex=function() return id end,
        GetOwner=function(s) return s.owner or 1 end, GetDistrictType=function() return -1 end,
        GetResourceType=function() return resource or -1 end,
        CanHaveDistrict=function(_, district, owner, cityID)
            assert(district==1 and owner==1 and cityID==15); gameplayChecked[id]=true; return id~=22
        end,
    }
    plots[id] = site
end
makeSite(11, 4, true, 1, 0)
makeSite(12, 2, true, 1, 1)
makeSite(13, 6, false, 1, 1)
makeSite(14, 6, true, 0, 1)
makeSite(15, 6, true, 1, 1)
makeSite(16, 6, true, 1, 1, 88)
makeSite(17, 6, true, 1, 1)
makeSite(18, 0, true, 1, 0)
makeSite(19, 6, true, 1, 1)
makeSite(20, 6, true, 1, 1)
makeSite(21, 4, true, 1, 1)
makeSite(22, 6, true, 1, 1)
local frontierPlots = {}
for id=31,36 do makeSite(id,0,false,0,0); frontierPlots[#frontierPlots+1]=plots[id] end
-- Ring geometry stays fixed while visibility and ownership change below.
CSC_Adjacency.PlotsInBand=function(center, first, last)
    if first==1 and last==3 then return frontierPlots end
    assert(first==1 and last==1)
    return Map.GetAdjacentPlots(center:GetX(),center:GetY())
end
PlayersVisibility = {[1]={IsRevealed=function(_, x) return x~=17 end}}
Cities = {GetPlotPurchaseCity=function(p) if p.id~=19 then return city end end}
local center = {GetOwner=function() return 1 end, GetDistrictType=function() return 0 end,
    GetResourceType=function() return -1 end,
    GetIndex=function() return 2 end, GetX=city.GetX, GetY=city.GetY}
Map = {
    GetPlot=function() return center end,
    GetPlotByIndex=function(id) return plots[id] end,
    GetPlotDistance=function(_, _, x) return x==20 and 4 or 2 end,
    GetAdjacentPlots=function(x)
        return plots[x].neighbors or (plots[x].host and {center} or {})
    end,
}
CityOperationTypes = {BUILD=1, PARAM_DISTRICT_TYPE=2, PARAM_X=3, PARAM_Y=4}
CityOperationResults = {PLOTS=5}
local targets = {11,12,13,14,15,16,17,18,19,20,21,22}
CityManager = {
    GetDistrictAt=function(x, y)
        assert(x==2 and y==3)
        return {IsComplete=function() return true end, IsPillaged=function() return false end}
    end,
    GetCity=function(pid, cityID) assert(pid==1 and cityID==15); return city end,
    GetOperationTargets=function(_, op, params)
        assert(op==1 and params[2]==1001 and not params[3]); targetsRead=targetsRead+1; return {[5]=targets}
    end,
    CanStartOperation=function(_, op, params, check)
        assert(op==1 and params[2]==1001 and params[4]==3 and check)
        checked[params[3]]=true
        return params[3]~=15
    end,
}
local function supplies(_, site)
    return {base=site.base>0 and {{ready=not site.baseLocked, working=site.baseWorking}} or {},
        specialty=site.spec>0 and {{}} or {}}
end
local ui = ExposedMembers.CSC_Adjacency
local readLegalTargets = ui.GetLegalDistrictTargets
local bakers = {key='BAKERS', district=GameInfo.Districts[1], customers={[0]={}},
    base='CLASS_CSC_BAKERS_BASE', specialty='CLASS_CSC_BAKERS_SPEC'}
local function bids(profile, protected, legal, chains)
    ui.GetLegalDistrictTargets = legal
    local indexed = {}
    local offers, counts = CSC_AI_QuarterSiteForecasts(player, profile, chains or {},
        supplies, protected, ui)
    for _, site in ipairs(offers) do indexed[site.plot] = site end
    return indexed, counts
end
local sites = bids(bakers, {}, readLegalTargets)
assert(sites[21].adjacency==5 and sites[21].delta==12288)
assert(sites[13].delta==-32768 and sites[14].delta==-65536 and sites[16].delta==-65536)
assert(checked[15] and not sites[15] and not sites[17] and not sites[19] and not sites[20] and not sites[22])
sites = bids(bakers, {[21]=true}, readLegalTargets)
assert(not sites[21] and sites[11].delta==12288)
cattleVisible = false
sites = bids(bakers, {}, readLegalTargets)
assert(sites[16].delta==12288)
cattleVisible = true
targets = {18}
sites = bids(bakers, {}, readLegalTargets)
assert(sites[18].adjacency==3 and sites[18].delta==6144)
targets = {11,21}
plots[21].baseLocked = true
sites = bids(bakers, {}, readLegalTargets)
assert(sites[11].delta==12288 and not sites[21])
plots[21].river = 6
targets = {21}
assert(bids(bakers, {}, readLegalTargets)[21].delta==12288)
targets = {11,21}
sites = bids(bakers, {}, readLegalTargets)
assert(sites[21].adjacency==6 and not sites[11])
plots[21].river = 4
plots[21].baseLocked = false
existing = true
assert(next((bids(bakers, {}, readLegalTargets)))==nil)
existing, placed = false, true
assert(next((bids(bakers, {}, readLegalTargets)))==nil)
placed, unlocked = false, false
assert(next((bids(bakers, {}, readLegalTargets)))==nil and targetsRead==7)

-- Frontier coverage uses geometry even when the BUILD-operation target list
-- is empty. A possible purchasable supplier or unseen neighbor stays neutral.
existing, placed, unlocked = false, false, false
local ownedNeighbor={GetOwner=function() return 1 end, GetX=function() return 98 end,
    GetY=function() return 3 end, GetResourceType=function() return -1 end}
plots[31].owner=-1
plots[31].neighbors={ownedNeighbor}
local frontier, frontierCounts=bids(bakers, {}, readLegalTargets)
assert(frontier[31].delta==-65536 and frontierCounts.frontierBids==1 and frontierCounts.legal==0)
local pendingBase={GetOwner=function() return -1 end, GetX=function() return 99 end,
    GetY=function() return 3 end, GetResourceType=function() return 88 end}
plots[31].neighbors={ownedNeighbor,pendingBase}
assert(not bids(bakers, {}, readLegalTargets)[31])
pendingBase.GetOwner=function() return 1 end
assert(not bids(bakers, {}, readLegalTargets)[31])
pendingBase.GetOwner=function() return 2 end
assert(bids(bakers, {}, readLegalTargets)[31].delta==-65536)
pendingBase.GetOwner=function() return -1 end
pendingBase.GetResourceType=function() return -1 end
PlayersVisibility[1].IsRevealed=function(_, x) return x~=99 end
assert(not bids(bakers, {}, readLegalTargets)[31])
PlayersVisibility[1].IsRevealed=function(_, x) return x~=17 end
plots[31].neighbors={ownedNeighbor}
cattleVisible=false
assert(not bids(bakers, {}, readLegalTargets)[31])
cattleVisible=true
plots[31].owner=2
assert(not bids(bakers, {}, readLegalTargets)[31])
plots[31].owner=-1
plots[31].neighbors={pendingBase}
assert(not bids(bakers, {}, readLegalTargets)[31])
plots[31].neighbors={ownedNeighbor}
PlayersVisibility[1].IsRevealed=function(_, x) return x~=31 end
assert(not bids(bakers, {}, readLegalTargets)[31])
PlayersVisibility[1].IsRevealed=function(_, x) return x~=17 end
local canHaveFrontier=plots[31].CanHaveDistrict
plots[31].CanHaveDistrict=function() return false end
assert(not bids(bakers, {}, readLegalTargets)[31])
plots[31].CanHaveDistrict=canHaveFrontier
plots[31].neighbors={ownedNeighbor,pendingBase}
PlayersVisibility[1].IsRevealed=function(_, x) return x~=99 end
plots[31].GetResourceType=function() return 88 end
assert(bids(bakers, {}, readLegalTargets)[31].delta==-65536)
plots[31].owner=1
PlayersVisibility[1].IsRevealed=function(_, x) return x~=17 end

-- A bounded frontier preference shares the owned-site model and Q8 bands.
-- Exercise the actual UI quote bridge too. No bank read is permitted here:
-- savings and command affordability remain the native buyer's responsibility.
local quotes={[31]=85,[32]=70}
city.GetGold=function()return {GetPlotPurchaseCost=function(_,index)return quotes[index]end}end
player.GetTreasury=function()error('Live siting must not gate on current cash')end
pendingBase.GetResourceType=function()return 88 end
for _,id in ipairs({31,32})do
    plots[id].owner=-1;plots[id].base=1;plots[id].river=0
    plots[id].neighbors={center,pendingBase}
    plots[id].GetResourceType=function()return -1 end
end
frontier,frontierCounts=bids(bakers,{},readLegalTargets)
assert(not frontier[31] and frontier[32].delta==6144 and frontier[32].frontier
    and frontier[32].purchaseGold==70 and frontierCounts.frontierOffers==1)
local savedTargets=targets
unlocked=true;targets={13}
frontier,frontierCounts=bids(bakers,{},readLegalTargets)
assert(frontier[13].weak and frontier[32].frontier and frontierCounts.deferCities==0)
targets=savedTargets;unlocked=false
quotes[31]=70
assert(bids(bakers,{},readLegalTargets)[31].delta==6144) -- Stable lower-plot tie.
quotes[31]=85;plots[31].river=4
assert(bids(bakers,{},readLegalTargets)[31].delta==12288) -- Better adjacency first.
assert(bids(bakers,{[31]=true},readLegalTargets)[32].delta==6144)
quotes[31]=nil;quotes[32]=-1
frontier,frontierCounts=bids(bakers,{},readLegalTargets)
assert(not frontier[31] and not frontier[32] and frontierCounts.frontierQuoteUnknown==2)
quotes[31]=85;plots[31].base=0
assert(not bids(bakers,{},readLegalTargets)[31])
plots[31].base=1;plots[31].owner=1
assert(not bids(bakers,{},readLegalTargets)[31])
plots[31].owner=-1;plots[31].GetResourceType=function()return 88 end
assert(bids(bakers,{},readLegalTargets)[31].delta==-65536)
plots[31].owner=1;plots[32].owner=1
city.GetGold=nil

-- The same gate accepts a future Harbor before it can be built, then
-- nominates the actual legal host of an existing Tailors chain.
local tailors = {key='TAILORS', district=GameInfo.Districts[2], customers={[4]={}},
    base='CLASS_CSC_TAILORS_BASE', specialty='CLASS_CSC_TAILORS_SPEC'}
tailors.district.Hash=1002
local slots = 1
cityDistricts.HasDistrict=function(_, id) return existing and id==2 end
local function tailorPlot(id)
    makeSite(id, 4, false, 1, 0)
    plots[id].GetIndex=function() return id end
    plots[id].CanHaveDistrict=function(_, district) return district==2 or (district==4 and id==24) end
end
tailorPlot(23)
tailorPlot(24)
Map.GetAdjacentPlots=function(x) return x==23 and {plots[24]} or {} end
local rules=CSC_Adjacency.ByDistrict[tailors.district.DistrictType]
rules[#rules+1]={ID='futureHarbor', YieldType='YIELD_GOLD', YieldChange=1,
    ModifierOwner='DistrictModifiers', ProvideType='SelfBonus', AdjacencyType='FROM_RINGS_TYPETAG_DISTRICT',
    CustomAdjacentObject='TAILORS_FIXTURE_HOST', Rings=1}
local count=CSC_Adjacency.Count
CSC_Adjacency.Count=function(rule, center, city, pid)
    if rule.ID=='futureHarbor' then return plots[24]:GetDistrictType()==4 and 1 or 0 end
    return count(rule,center,city,pid)
end
local hasTag=CSC_Adjacency.HasTag
CSC_Adjacency.HasTag=function(tag, kind)
    return tag=='TAILORS_FIXTURE_HOST' and (kind=='DISTRICT_HARBOR' or kind=='DISTRICT_COMMERCIAL_HUB')
        or tag=='CLASS_CSC_TAILORS_SALES' and kind=='DISTRICT_COMMERCIAL_HUB'
        or tag=='CLASS_CSC_TAILORS_GOODS_PROVIDER' and kind=='DISTRICT_RURALCOMMUNITYA' or hasTag(tag,kind)
end
local harborUnlocked=false
local function legal(_, _, hash)
    if hash==1002 then return {23} end
    return harborUnlocked and slots>0 and {24} or {}
end
assert(bids(tailors, {}, legal)[23].adjacency==6)
slots=0
plots[23].baseLocked=true
local future, counts=bids(tailors, {}, legal)
assert(future[23].adjacency==6 and future[23].delta==12288 and counts.bothPending==1 and counts.deferCities==0)
harborUnlocked=true
assert(bids(tailors, {}, legal)[23].delta==12288)
slots=1
plots[23].baseLocked=false
assert(bids(tailors, {}, legal)[23].delta==12288)
assert(bids(tailors, {}, legal)[24].delta==4096)
tailors.district.RequiresPopulation=true
assert(not bids(tailors, {}, legal)[24])
tailors.district.RequiresPopulation=false
harborUnlocked=false
assert(bids(tailors, {[24]=true}, legal)[23].delta==-32768)
-- A later-stage Commercial Hub gives a concrete forecast even when a
-- Harbor is impossible. It does not manufacture a Stage 2 customer bid.
local canHaveDistrict=plots[24].CanHaveDistrict
plots[24].CanHaveDistrict=function(_, district) return district==5 end
assert(bids(tailors, {}, legal)[23].adjacency==6 and not bids(tailors, {}, legal)[24])
rules[#rules+1]={ID='futureProvider', YieldType='YIELD_PRODUCTION', YieldChange=1,
    ModifierOwner='DistrictModifiers', ProvideType='SelfBonus', AdjacencyType='FROM_RINGS_TYPETAG_DISTRICT',
    CustomAdjacentObject='CLASS_CSC_TAILORS_GOODS_PROVIDER', Rings=1}
plots[24].CanHaveDistrict=function(_, district) return district==6 end
assert(bids(tailors, {}, legal)[23].adjacency==6 and not bids(tailors, {}, legal)[24])
plots[24].CanHaveDistrict=canHaveDistrict
-- Missing actor metadata does not mean an otherwise promising city has
-- no future customer. Suppress forecast-only credit without a false penalty
-- or a city-deferral count; current native customer targets still work.
local savedConfig=PlayerConfigurations[1]
PlayerConfigurations[1]=nil
local unknown, unknownCounts=bids(tailors, {}, legal)
assert(not unknown[23] and unknownCounts.futureUnknown==1 and unknownCounts.noHost==0
    and unknownCounts.deferCities==0)
PlayerConfigurations[1]=savedConfig
local savedTraits=GameInfo.CivilizationTraits
GameInfo.CivilizationTraits=nil
unknown,unknownCounts=bids(tailors, {}, legal)
assert(not unknown[23] and unknownCounts.futureUnknown==1 and unknownCounts.noHost==0
    and unknownCounts.deferCities==0)
GameInfo.CivilizationTraits=savedTraits
-- Existing and pillaged Harbors keep their long-term adjacency. A built
-- Harbor's observed rule amount replaces the future projection.
local pillaged=false
CityManager.GetDistrictAt=function(x, y)
    assert(x==24 and y==3)
    return {IsComplete=function() return true end, IsPillaged=function() return pillaged end}
end
plots[24].GetDistrictType=function() return 4 end
assert(bids(tailors, {}, legal)[23].adjacency==6)
pillaged=true
assert(bids(tailors, {}, legal)[23].adjacency==6)
plots[24].GetDistrictType=function() return -1 end
existing=true
local chain={profile=tailors, ready=true, plot=plots[23], supply={base={true}}}
assert(next((bids(tailors, {}, legal, {chain})))==nil)
harborUnlocked=true
assert(bids(tailors, {}, legal, {chain,chain})[24].delta==10240)
assert(next((bids(tailors, {[24]=true}, legal, {chain})))==nil)
"""

def main():
 a=argparse.ArgumentParser();a.add_argument('--dependencies',type=pathlib.Path,required=True);a.add_argument('--output',type=pathlib.Path,required=True);args=a.parse_args();sys.path.insert(0,str(args.dependencies));from lupa.lua51 import LuaRuntime
 lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('DefenseTypes={DISTRICT_GARRISON=0,DISTRICT_OUTER=1}');lua.execute((ROOT/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua').read_text(encoding='utf-8-sig'));lua.execute(HARNESS)
 score=lua.execute(SCANNER.read_text(encoding='utf-8')+'\nassert(CSC_AI_QuarterAdjacencyValue==score);return score');g=lua.globals();checks=[]
 def check(name,quarter,river,hills,expected,current=None):
  g.plot.river=river;g.plot.hills=hills;r=score('DISTRICT_CSC_'+quarter+'_QUARTER',g.plot,g.city,1)
  actual=(r['production'],r['gold']);assert actual==expected,(name,actual,expected)
  if current is not None:assert r['current']['production']==current,(name,r['current']['production'])
  checks.append(dict(name=name,total=r['total'],requiresBuilding=r['requiresBuilding']))
 check('Tailors one edge rounds down','TAILORS',1,0,(2,1));check('Tailors paired edges','TAILORS',2,0,(3,1));check('Tailors five edges','TAILORS',5,0,(4,1))
 check('Bakers planned Water Mill','BAKERS',4,1,(4,1),2);check('River site never adds Wind Mill hill bonus','BAKERS',1,1,(2,1),2)
 check('Bakers planned Wind Mill hill','BAKERS',0,1,(3,1),2);check('Flat wind site no bonus','BAKERS',0,0,(2,1),2)
 g.POLICY=True;check('Active policy included','TAILORS',2,0,(3,2));g.POLICY=False
 g.MILLS=True;check('Existing remote Mills do not double planned branches','BAKERS',4,1,(4,1))
 lua.execute('ExposedMembers={}')
 lua.execute((SCANNER.parent.parent/'Adjacencies/CSC_AdjacencyUI.lua').read_text(encoding='utf-8-sig'))
 lua.execute(BAKERS_SITES)
 checks.append(dict(name='Immediate Bakers site respects native readiness and Stage 2 geometry'))
 assert 'A.PlotsInBand(center,1,3)'in SCANNER.read_text(encoding='utf-8') and 'if not existing[name]then'in SCANNER.read_text(encoding='utf-8')
 args.output.write_text(json.dumps(dict(passed=True,lua='Lua5.1',checks=checks,core='actual shared A.Eligible/A.Amount and native river counter; synthetic material/customer counts'),indent=2)+'\n');print('Scanner checks passed:',len(checks))
if __name__=='__main__':main()
