"""Exercise reverse loaded relationships, real supply reads and hex footprints.

No authored Bakers/Tailors mapping in these fixtures: the arbitrary Quarter and
modded resources are discovered through generated native edges and class tags.
Both linear and triangular layouts must keep three distinct legal footprints.
"""
from pathlib import Path
import unittest
import test_boundaries as boundaries

AI = Path(__file__).resolve().parents[3] / 'Civ Supply Chains/Lua_UI/AI'


class CustomerFirstPlanning(unittest.TestCase):
    def facts(self):
        vm = boundaries.Boundaries().facts_vm()
        vm.execute('''
local function catalogue(rows,key)
 local t={};for _,r in ipairs(rows)do if r[key]then t[r[key]]=r end;if r.Index then t[r.Index]=r end end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
GameInfo.Districts=catalogue({
 {Index=20,DistrictType='DISTRICT_COMMERCIAL_HUB',Hash=200,RequiresPopulation=1},
 {Index=21,DistrictType='DISTRICT_MODDED_CUSTOMER',Hash=210,RequiresPopulation=0},
 {Index=36,DistrictType='DISTRICT_CSC_TEST_QUARTER',Hash=360,RequiresPopulation=1},
 {Index=37,DistrictType='DISTRICT_CSC_UNRELATED_QUARTER',Hash=370,RequiresPopulation=1}},'DistrictType')
GameInfo.Adjacency_YieldChanges=catalogue({
 {ID='native',YieldType='YIELD_CSC_AI_PLACEMENT',YieldChange=1,AdjacentDistrict='DISTRICT_CSC_TEST_QUARTER'},
 {ID='unrelated',YieldType='YIELD_GOLD',YieldChange=1,AdjacentDistrict='DISTRICT_CSC_UNRELATED_QUARTER'}},'ID')
GameInfo.District_Adjacencies=catalogue({
 {DistrictType='DISTRICT_COMMERCIAL_HUB',YieldChangeId='native'},
 {DistrictType='DISTRICT_COMMERCIAL_HUB',YieldChangeId='native'},
 {DistrictType='DISTRICT_MODDED_CUSTOMER',YieldChangeId='native'},
 {DistrictType='DISTRICT_COMMERCIAL_HUB',YieldChangeId='unrelated'}},'unused')
GameInfo.Resources=catalogue({{Index=50,ResourceType='RESOURCE_MOD_BASE'},
 {Index=51,ResourceType='RESOURCE_MOD_SPEC'},{Index=52,ResourceType='RESOURCE_WRONG'}},'ResourceType')
GameInfo.Improvements=catalogue({{Index=10,ImprovementType='IMPROVEMENT_TEST',PrereqTech='A'}},'ImprovementType')
GameInfo.Improvement_ValidResources=catalogue({
 {ResourceType='RESOURCE_MOD_BASE',ImprovementType='IMPROVEMENT_TEST'},
 {ResourceType='RESOURCE_MOD_SPEC',ImprovementType='IMPROVEMENT_TEST'},
 {ResourceType='RESOURCE_WRONG',ImprovementType='IMPROVEMENT_TEST'}},'unused')
GameInfo.Yields={YIELD_PRODUCTION={Index=1}}
local tags={CLASS_CSC_TEST_BASE={RESOURCE_MOD_BASE=true},CLASS_CSC_TEST_SPEC={RESOURCE_MOD_SPEC=true}}
CSC_Adjacency={HasTag=function(tag,kind)return tags[tag]and tags[tag][kind]or false end,
 ResourceVisible=function(_,resource)return not hiddenResource end}
local ds={GetNumDistricts=function()return 0 end,HasDistrict=function()return false end}
city={GetID=function()return 7 end,GetX=function()return -1 end,GetY=function()return -1 end,
 GetPopulation=function()return 4 end,GetBuildQueue=function()return{}end,
 GetBuildings=function()return{}end,GetDistricts=function()return ds end}
player.GetCities=function()return{Members=function()local done=false;return function()
 if not done then done=true;return 7,city end end end}end
local coords={{-1,-1},{0,0},{1,0},{0,-1},{2,0},{1,1},{2,1}}
plots={}
local function make(i,c)
 local p={index=i,x=c[1],y=c[2],owner=1,resource=i==5 and 50 or i==6 and 51 or -1,district=-1}
 p.GetIndex=function()return p.index end;p.GetX=function()return p.x end;p.GetY=function()return p.y end
 p.GetOwner=function()return p.owner end;p.GetResourceType=function()return p.resource end
 p.GetDistrictType=function()return p.district end;p.GetImprovementType=function()return -1 end
 p.CanHaveDistrict=function(_,kind)return kind~=36 or i==3 and not blockedQuarter end
 return p
end
for i,c in ipairs(coords)do plots[i]=make(i,c)end
local function distance(x,y,a,b)return math.max(math.abs(x-a),math.abs(y-b),math.abs(x+y-a-b))end
Map={GetPlotDistance=distance,GetPlotByIndex=function(i)return plots[i]end,
 GetPlot=function(x,y)for _,p in ipairs(plots)do if p.x==x and p.y==y then return p end end end,
 GetAdjacentPlots=function(x,y)local r={};for _,p in ipairs(plots)do
 if distance(x,y,p.x,p.y)==1 then r[#r+1]=p end end;return r end}
Cities={GetPlotPurchaseCity=function(p)return p.owner==1 and city or nil end}
PlayersVisibility={[1]={IsRevealed=function(_,x,y)return not hiddenPlot or not(hiddenPlot.x==x and hiddenPlot.y==y)end}}
ImprovementBuilder={CanHaveImprovement=function(p)return not blockedImprovement and p.owner==1 end}
CSC_AI_FutureDistrictTypes=function()return{[20]=true,[21]=true,[36]=not excludedQuarter}end
Game={GetCurrentGameTurn=function()return 20 end}
legal={2,4};adj={[2]=2,[4]=2};lag=0;reads=0
ui={GetLegalDistrictTargets=function(_,_,hash)return hash==200 and legal or {}end,
 GetDistrictAdjacency=function(_,_,plot)
 reads=reads+1;return{available=true,turn=20-lag,yields={YIELD_GOLD=adj[plot],YIELD_CSC_AI_PLACEMENT=999}}
end}
''')
        vm.execute((AI / 'CSC_AI_QuarterPlacement.lua').read_text(encoding='utf-8'))
        vm.execute('placement=CSC_AI_QuarterPlacement;placement.ReadChains=function()return{}end')
        return vm

    def test_generic_reverse_graph_and_modded_materials_need_no_policy_mapping(self):
        vm = self.facts()
        vm.execute('''
local F=CSC_AI_EconomyFacts;local graph=F.CustomerQuarterMap()
assert(#graph[20].quarters==1 and #graph[21].quarters==1)
assert(graph[20].quarters[1].base=='CLASS_CSC_TEST_BASE')
local snapshot=F.New(player,placement,ui)
local options=snapshot.CustomerFirstOptions({})
assert(#options==1)
local row=options[1]
assert(row.city==7 and row.plot==2 and row.quarterPlot==3 and row.quarterDistrict==36)
assert(row.baseCount==1 and row.specialtyCount==1 and row.basePlots[1]==5 and row.specialtyPlots[1]==6)
assert(row.adjacency==2 and row.bestAdjacency==2) -- private yield excluded
assert(row.quarterKey=='TEST' and row.customerFamily=='DISTRICT_COMMERCIAL_HUB')
assert(not player:GetTechs():HasTech(1)) -- locked improvement still has geometric potential
''')

    def test_triangle_and_straight_layouts_both_work_but_radius_two_alone_is_insufficient(self):
        vm = self.facts()
        vm.execute('''
local F=CSC_AI_EconomyFacts
assert(#F.New(player,placement,ui).CustomerFirstOptions({})==1) -- customer(0,0),Q(1,0),Base(2,0)
plots[5].x=0;plots[5].y=1 -- Base adjacent to BOTH customer and Quarter
assert(#F.New(player,placement,ui).CustomerFirstOptions({})==1)
plots[5].x=-1;plots[5].y=0 -- near customer but NOT adjacent to feasible Q footprint
assert(#F.New(player,placement,ui).CustomerFirstOptions({})==0)
''')

    def test_concrete_empty_footprints_and_actor_rules_are_required(self):
        for change in ("blockedQuarter=true", "excludedQuarter=true", "plots[3].district=99",
                       "plots[3].resource=52", "plots[3].owner=2", "plots[2].resource=50",
                       "plots[5].owner=2", "plots[5].resource=52", "blockedImprovement=true",
                       "hiddenResource=true", "hiddenPlot=plots[5]", "legal={}"):
            with self.subTest(change=change):
                vm=self.facts()
                vm.execute(change+";assert(#CSC_AI_EconomyFacts.New(player,placement,ui).CustomerFirstOptions({})==0)")

    def test_unrelated_resources_do_not_trigger_native_improvement_geometry(self):
        vm=self.facts()
        vm.execute('''
plots[5].resource=52;plots[6].resource=52
ImprovementBuilder.CanHaveImprovement=function()error('Unrelated resource must be filtered before native work')end
assert(#CSC_AI_EconomyFacts.New(player,placement,ui).CustomerFirstOptions({})==0)
''')

    def test_reserved_material_or_quarter_and_existing_supplier_earn_no_speculative_bonus(self):
        vm=self.facts()
        vm.execute('''
local F=CSC_AI_EconomyFacts
for _,blocked in ipairs({3,5})do
 local snapshot=F.New(player,placement,ui);snapshot.intentFootprints={[blocked]=true}
 assert(#snapshot.CustomerFirstOptions({})==0)
end
assert(#F.New(player,placement,ui).CustomerFirstOptions({[3]=true})==0)
plots[3].district=36
assert(#F.New(player,placement,ui).CustomerFirstOptions({})==0) -- native SQL handles existing Quarter
''')

    def test_current_customer_eligibility_and_cached_fresh_native_adjacency(self):
        vm=self.facts()
        vm.execute('''
local F=CSC_AI_EconomyFacts
local snapshot=F.New(player,placement,ui)
local row=snapshot.CustomerFirstOptions({})[1];assert(row)
local previous=reads;snapshot.CustomerFirstOptions({});assert(reads==previous)
assert(snapshot.customerFirstWork.supplyReads==1)
adj[4]=4;row=F.New(player,placement,ui).CustomerFirstOptions({})[1]
assert(row.adjacency==2 and row.bestAdjacency==4)
lag=2;assert(#F.New(player,placement,ui).CustomerFirstOptions({})==0)
''')

    def test_actual_adapter_reads_the_reverse_facts_and_preserves_better_customer_sites(self):
        vm=self.facts()
        vm.execute('CSC_AI_EconomyModel={}')
        vm.execute((AI / 'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local function offers()
 local snapshot=CSC_AI_EconomyFacts.New(player,placement,ui)
 snapshot.DistrictCapacity=function()return{known=true,used=0,allowed=1}end
 return CSC_AI_EconomyAdapters.CustomerOffers(snapshot,{},{})
end
local rows=offers();assert(#rows==1 and rows[1].delta==12*256)
assert(rows[1].plot==2 and rows[1].futureSuppliers[1].option.quarterPlot==3)
adj[4]=3;assert(#offers()==0) -- a better standalone Hub exists
adj[4]=2;legal={};assert(#offers()==0)
''')

    def test_existing_quarter_only_suppresses_its_own_supplier_city_type(self):
        vm=self.facts()
        vm.execute('''
local existing={x=-1,y=0,GetIndex=function()return 8 end,GetX=function()return -1 end,GetY=function()return 0 end,
 GetOwner=function()return 1 end,GetResourceType=function()return -1 end,GetDistrictType=function()return 36 end}
plots[8]=existing
local other={GetID=function()return 8 end};local sameCity=false
Cities.GetPlotPurchaseCity=function(p)if p==existing and not sameCity then return other end;return city end
local F=CSC_AI_EconomyFacts
assert(#F.New(player,placement,ui).CustomerFirstOptions({})==1)
sameCity=true
assert(#F.New(player,placement,ui).CustomerFirstOptions({})==0)
''')


if __name__ == '__main__':
    unittest.main()
