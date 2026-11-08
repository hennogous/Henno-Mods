"""Exercise scanner with the real shared core and mocked native map counts."""
import argparse,json,pathlib,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[3]
SCANNER=ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_AdjacencyScan.lua'
HARNESS=r"""
function info(rows,key)local t={};for _,r in ipairs(rows)do t[r[key]]=r;t[r.Index]=r end;return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})end
local b='DISTRICT_CSC_BAKERS_QUARTER';local t='DISTRICT_CSC_TAILORS_QUARTER'
GameInfo={Districts=info({{Index=0,DistrictType='DISTRICT_CITY_CENTER'},{Index=1,DistrictType=b},{Index=2,DistrictType=t}},'DistrictType'),Buildings=info({{Index=1,BuildingType='BUILDING_CSC_BAKERS_WATER_MILL'},{Index=2,BuildingType='BUILDING_CSC_BAKERS_WIND_MILL'}},'BuildingType'),Policies=info({{Index=1,PolicyType='POLICY_TEST'}},'PolicyType')}
POLICY=false;MILLS=false
city={GetBuildings=function()return {HasBuilding=function()return MILLS end}end}
player={IsHuman=function()return false end,GetCities=function()return {Members=function()local once=false;return function()if not once then once=true;return 1,city end end end}end,GetCulture=function()return {IsPolicyActive=function()return POLICY end}end}
Players={[1]=player}
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
local cityDistricts = {HasDistrict=function(_, id) assert(id==1); return existing end}
local queue = {
    HasBeenPlaced=function(_, hash) assert(hash==1001); return placed end,
    CanProduce=function(_, hash, _, test) assert(hash==1001 and test); return unlocked end,
}
GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Hash = 1001
GameInfo.Resources = {[88]={ResourceType='RESOURCE_CATTLE'}}
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
        GetOwner=function() return 1 end, GetDistrictType=function() return -1 end,
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
PlayersVisibility = {[1]={IsRevealed=function(_, x) return x~=17 end}}
Cities = {GetPlotPurchaseCity=function(p) if p.id~=19 then return city end end}
local center = {GetOwner=function() return 1 end, GetDistrictType=function() return 0 end}
Map = {
    GetPlotByIndex=function(id) return plots[id] end,
    GetPlotDistance=function(_, _, x) return x==20 and 4 or 2 end,
    GetAdjacentPlots=function(x) return plots[x].host and {center} or {} end,
}
CityOperationTypes = {BUILD=1, PARAM_DISTRICT_TYPE=2, PARAM_X=3, PARAM_Y=4}
CityOperationResults = {PLOTS=5}
local targets = {11,12,13,14,15,16,17,18,19,20,21,22}
CityManager = {
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
    return {base=site.base>0 and {true} or {}, specialty=site.spec>0 and {true} or {}}
end
local readLegalTargets = ExposedMembers.CSC_Adjacency.GetLegalDistrictTargets
local bakers = {district=GameInfo.Districts[1], customers={[0]={}},
    base='CLASS_CSC_BAKERS_BASE', specialty='CLASS_CSC_BAKERS_SPEC'}
local function bids(profile, protected, legal, chains)
    local indexed = {}
    for _, site in ipairs(CSC_AI_QuarterSiteForecasts(player, profile, chains or {},
        supplies, protected, legal)) do indexed[site.plot] = site end
    return indexed
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
existing = true
assert(next(bids(bakers, {}, readLegalTargets))==nil)
existing, placed = false, true
assert(next(bids(bakers, {}, readLegalTargets))==nil)
placed, unlocked = false, false
assert(next(bids(bakers, {}, readLegalTargets))==nil and targetsRead==4)

-- The same gate accepts a future Harbor before it can be built, then
-- nominates the actual legal host of an existing Tailors chain.
local tailors = {district=GameInfo.Districts[2], customers={[4]={}},
    base='CLASS_CSC_TAILORS_BASE', specialty='CLASS_CSC_TAILORS_SPEC'}
tailors.district.Hash=1002
GameInfo.Districts[4]={Index=4, Hash=1004, DistrictType='DISTRICT_HARBOR'}
cityDistricts.HasDistrict=function(_, id) return existing and id==2 end
local function tailorPlot(id)
    makeSite(id, 4, false, 1, 0)
    plots[id].GetIndex=function() return id end
    plots[id].CanHaveDistrict=function(_, district) return district==2 or (district==4 and id==24) end
end
tailorPlot(23)
tailorPlot(24)
Map.GetAdjacentPlots=function(x) return x==23 and {plots[24]} or {} end
local harborUnlocked=false
local function legal(_, _, hash)
    if hash==1002 then return {23} end
    return harborUnlocked and {24} or {}
end
assert(bids(tailors, {}, legal)[23].delta==12288)
assert(bids(tailors, {[24]=true}, legal)[23].delta==-32768)
existing=true
local chain={profile=tailors, ready=true, plot=plots[23], supply={base={true}}}
assert(next(bids(tailors, {}, legal, {chain}))==nil)
harborUnlocked=true
assert(bids(tailors, {}, legal, {chain,chain})[24].delta==10240)
assert(next(bids(tailors, {[24]=true}, legal, {chain}))==nil)
"""

def main():
 a=argparse.ArgumentParser();a.add_argument('--dependencies',type=pathlib.Path,required=True);a.add_argument('--output',type=pathlib.Path,required=True);args=a.parse_args();sys.path.insert(0,str(args.dependencies));from lupa.lua51 import LuaRuntime
 lua=LuaRuntime(unpack_returned_tuples=True);lua.execute('DefenseTypes={DISTRICT_GARRISON=0,DISTRICT_OUTER=1}');lua.execute((ROOT/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua').read_text(encoding='utf-8-sig'));lua.execute(HARNESS)
 score=lua.execute(SCANNER.read_text(encoding='utf-8')+'\nreturn score');g=lua.globals();checks=[]
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
