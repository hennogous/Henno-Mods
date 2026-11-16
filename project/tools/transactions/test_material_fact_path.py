"""Exercise late host reconciliation -> loaded facts -> Site -> economic ledger.

Only physical city/plot APIs are fixtures. Transactions, native arguments,
registered hosts and model eligibility come from the actual production SQL/Lua.
"""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from population_catalogue_fixture import compile_catalogue,MOD
from test_population_catalogue import lua


def world(*,quarter='BAKERS',host='IMP_CL_TRADING_POST',gold=True,mc=False,customer=False):
    db=compile_catalogue(gold=gold,mc=mc)
    db.executescript('''
CREATE TABLE Improvements(ImprovementType TEXT PRIMARY KEY);
CREATE TABLE Improvement_ValidResources(ImprovementType TEXT,ResourceType TEXT);
CREATE TABLE TypeTags(Type TEXT,Tag TEXT);
INSERT INTO Improvements VALUES('IMP_CL_TRADING_POST'),('IMPROVEMENT_RES2_SAWMILL'),('IMPROVEMENT_UNREGISTERED'),('IMPROVEMENT_INDUSTRY');
INSERT INTO Improvement_ValidResources VALUES('IMP_CL_TRADING_POST','RESOURCE_WHEAT'),('IMPROVEMENT_RES2_SAWMILL','RESOURCE_BAMBOO');
INSERT INTO TypeTags VALUES('RESOURCE_WHEAT','CLASS_CSC_BAKERS_BASE'),('RESOURCE_BAMBOO','CLASS_CSC_TAILORS_BASE');
''')
    db.executescript((MOD/'Data/CSC_MaterialTransactions.sql').read_text())
    tables={}
    for name, in db.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        tables[name]=[dict(r)for r in db.execute('SELECT * FROM '+name)]
    db.close()
    producer='BUILDING_CSC_'+quarter+('_WIND_MILL'if quarter=='BAKERS'else'_TEXTILE_WORKSHOP')
    resource='RESOURCE_WHEAT'if quarter=='BAKERS'else'RESOURCE_BAMBOO'
    vm=LuaRuntime();vm.execute('TABLES='+lua(tables)+'\nPRODUCER='+lua(producer)+'\nHOST='+lua(host)+'\nRESOURCE='+lua(resource)+'\nQUARTER='+lua(quarter)+'\nCUSTOMER='+lua(customer)+'''
local function info(rows,key)
 local t={};for i,r in ipairs(rows)do r.Index=i-1;t[r[key]or i]=r;t[r.Index]=r end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
GameInfo={}
for name,rows in pairs(TABLES)do GameInfo[name]=info(rows,
 name=='Buildings'and'BuildingType'or name=='Modifiers'and'ModifierId'or'__none')end
local empty=info({},'__none')
for _,name in ipairs({'BuildingPrereqs','MutuallyExclusiveBuildings','TechnologyPrereqs','CivicPrereqs'})do GameInfo[name]=empty end
GameInfo.Resources=info({{ResourceType=RESOURCE}},'ResourceType')
GameInfo.Improvements=info(TABLES.Improvements,'ImprovementType')
GameInfo.Yields=info({{YieldType='YIELD_PRODUCTION'},{YieldType='YIELD_FOOD'},{YieldType='YIELD_GOLD'},{YieldType='YIELD_CULTURE'}},'YieldType')
GameInfo.Districts=info({{DistrictType='DISTRICT_CSC_'..QUARTER..'_QUARTER',RequiresPopulation=1},
 {DistrictType='DISTRICT_COMMERCIAL_HUB',RequiresPopulation=1},
 {DistrictType='DISTRICT_HARBOR',RequiresPopulation=1}},'DistrictType')
for b in GameInfo.Buildings()do if b.BuildingType~=PRODUCER then b.MustPurchase=1 end end
local q={GetIndex=function()return 1 end,GetX=function()return 0 end,GetY=function()return 0 end,
 GetWorkerCount=function()return QUARTER_WORKERS or 0 end,IsRiver=function()return false end}
local p={GetIndex=function()return 2 end,GetX=function()return 1 end,GetY=function()return 0 end,
 GetOwner=function()return 1 end,GetResourceType=function()return GameInfo.Resources[RESOURCE].Index end,
 GetDistrictType=function()return -1 end,GetImprovementType=function()return GameInfo.Improvements[HOST].Index end,
 IsImprovementPillaged=function()return false end,GetWorkerCount=function()return WORKERS end}
p.CanHaveDistrict=function()return true end
q.GetOwner=function()return 1 end;q.GetTerrainType=function()return 0 end
q.GetFeatureType=function()return -1 end;q.GetResourceType=function()return -1 end
q.GetImprovementType=function()return -1 end
local d={GetX=q.GetX,GetY=q.GetY,IsComplete=function()return true end,IsPillaged=function()return HOST_DAMAGED end,
 GetType=function()return GameInfo.Districts['DISTRICT_CSC_'..QUARTER..'_QUARTER'].Index end}
local customerPlot={GetIndex=function()return 3 end,GetX=function()return 0 end,GetY=function()return 1 end,
 GetOwner=function()return 1 end,GetResourceType=function()return -1 end,GetImprovementType=function()return -1 end,
 GetDistrictType=function()return GameInfo.Districts.DISTRICT_HARBOR.Index end}
local hd={GetX=customerPlot.GetX,GetY=customerPlot.GetY,IsComplete=function()return true end,
 IsPillaged=function()return CUSTOMER_DAMAGED end,GetType=customerPlot.GetDistrictType}
local ds={GetNumDistricts=function()return CUSTOMER and 2 or 1 end,GetDistrictByIndex=function(_,i)return i==0 and d or hd end}
local buildings={HasBuilding=function(_,id)return id==GameInfo.Buildings[PRODUCER].Index
 or EXTRA_BUILDINGS and EXTRA_BUILDINGS[id]
 or CUSTOMER and id==GameInfo.Buildings.BUILDING_LIGHTHOUSE.Index end,
 IsPillaged=function()return false end,GetBuildingLocation=function(_,id)return id==GameInfo.Buildings.BUILDING_LIGHTHOUSE.Index and 3 or 1 end}
local function makeCity(id)
 return{GetID=function()return id end,GetOwner=function()return 1 end,GetPopulation=function()return 10 end,
 GetX=q.GetX,GetY=q.GetY,GetBuildings=function()return buildings end,GetBuildQueue=function()return{}end,
 GetDistricts=function()return id==1 and ds or{GetNumDistricts=function()return 0 end}end}
end
city=makeCity(1);workerCity=makeCity(2)
local tech={HasTech=function()return true end};local culture={HasCivic=function()return true end}
player={GetID=function()return 1 end,GetTechs=function()return tech end,GetCulture=function()return culture end,
 GetCities=function()return{Members=function()local i=0;local cities={city,workerCity};return function()i=i+1;return i,cities[i]end end}end}
-- The iterator must terminate with nil as its first result, like the live API.
player.GetCities=function()return{Members=function()local i=0;local cities={city,workerCity};return function()i=i+1;if cities[i]then return i,cities[i]end end end}end
Map={GetPlot=function(x,y)return y==1 and customerPlot or x==1 and p or q end,
 GetPlotByIndex=function(i)return i==1 and q or i==3 and customerPlot or p end,
 GetAdjacentPlots=function()return CUSTOMER and{p,customerPlot}or{p}end}
PlayersVisibility={[1]={IsRevealed=function()return true end}}
PlayerConfigurations={};Cities={GetPlotPurchaseCity=function()return city end}
Game={GetCurrentGameTurn=function()return 20 end}
CSC_Adjacency={HasTag=function(tag,r)return tag=='CLASS_CSC_'..QUARTER..'_BASE'and r==RESOURCE end,
 ResourceVisible=function()return true end,ByDistrict={}}
placement={ReadChains=function()return{}end,ReadSuppliers=function()return{base={},specialty={}}end}
profile={key=QUARTER,district=GameInfo.Districts['DISTRICT_CSC_'..QUARTER..'_QUARTER'],
 base='CLASS_CSC_'..QUARTER..'_BASE',specialty='CLASS_CSC_'..QUARTER..'_SPEC'}
WORKERS=1;UI_LAG=0;HOST_DAMAGED=false;CUSTOMER_DAMAGED=false
ui={GetEconomyCityNumber=function()return 10 end,GetEconomyPlotFacts=function(index)return{
 turn=20-UI_LAG,plotOwner=1,workingPlayer=1,workingCity=index==1 and 1 or 2,
 workers=index==2 and WORKERS or QUARTER_WORKERS or 0,yields={}}end}
quarterPlot=q
''')
    for name in('Facts','Model'):vm.execute((MOD/f'Lua_UI/AI/CSC_AI_Economy{name}.lua').read_text())
    vm.execute('''
function evaluate()
 local snapshot=CSC_AI_EconomyFacts.New(player,placement,ui,{horizon=30})
 snapshot.Geometry=function()return{base=0,direct={},mills={}}end
 local site=assert(snapshot.Site(city,quarterPlot,profile))
 return CSC_AI_EconomyModel.Forecast(site,function(s,h)return s.amount*(h-s.ready)*256 end),site,snapshot
end
''')
    return vm


class MaterialFactPath(unittest.TestCase):
    def test_late_cl_and_r2_hosts_flow_through_site_with_actual_working_city(self):
        for q,h in [('BAKERS','IMP_CL_TRADING_POST'),('TAILORS','IMPROVEMENT_RES2_SAWMILL')]:
            vm=world(quarter=q,host=h)
            vm.execute("local r,s=evaluate();assert(#s.suppliers==1 and s.suppliers[1].ready==0);assert(r.valueQ8==3*30*256);for _,stream in ipairs(r.streams)do if stream.yield=='YIELD_PRODUCTION'or stream.yield=='YIELD_GOLD'then assert(stream.city==2)else assert(stream.city==1)end end")

    def test_unregistered_host_and_unknown_or_unworked_city_do_not_invent_input(self):
        vm=world(host='IMPROVEMENT_UNREGISTERED')
        vm.execute('assert(evaluate().valueQ8==2*30*256);WORKERS=0;assert(evaluate().valueQ8==0)')
        vm.execute('WORKERS=1;UI_LAG=1;assert(evaluate().valueQ8==2*30*256);UI_LAG=2;assert(evaluate().valueQ8==0)')
        vm.execute('''
-- A current city lookup must not make a stale worker count usable.
Cities.GetPlotWorkingCity=function()return workerCity end
Map.GetPlotByIndex(2).GetWorkerCount=nil
assert(evaluate().valueQ8==0)
UI_LAG=0;assert(evaluate().valueQ8==2*30*256)
''')

    def test_gold_off_and_exact_mc_hosts_flow_through_production_path(self):
        vm=world(host='IMPROVEMENT_INDUSTRY',mc=True,gold=False)
        vm.execute('assert(evaluate().valueQ8==4*30*256)')

    def test_protection_consumes_actual_relationship_missing_from_builder_lists(self):
        vm=world(host='IMPROVEMENT_UNREGISTERED')
        for name in('Adapters','QuarterPlacement'):
            vm.execute((MOD/f'Lua_UI/AI/CSC_AI_{"EconomyAdapters"if name=="Adapters"else name}.lua').read_text())
        vm.execute('''
local _,site,snapshot=evaluate()
snapshot.Price=function(s,h)return s.amount*(h-s.ready)*256 end
snapshot.SupplyAdjacencyLoss=function()return{}end
local chain={city=city,plot=quarterPlot,profile=profile,economy=site,
 supply={base={},specialty={}},complete=false,active=false}
snapshot.chains={chain}
local rows,_,_,_,_,exclusions=CSC_AI_QuarterPlacement.MaterialDeductions(player,false,0,0,nil,false,snapshot)
assert(#rows==2)
for _,row in ipairs(rows)do assert(row.plot==2 and row.city==1 and row.delta==-2*30*256)end
assert(#exclusions==1 and exclusions[1].plot==2)
''')

    def test_district_damage_preserves_intact_producer_plot_returns(self):
        vm=world()
        vm.execute('''
HOST_DAMAGED=true
local r,s=evaluate();assert(s.existing and s.seconds[1].intactOwner and not s.seconds[1].working)
assert(#r.investments==0)
local n=0
for _,stream in ipairs(r.streams)do if stream.id:find('material:',1,true)==1 then
 n=n+1
 if stream.yield=='YIELD_FOOD'then assert(stream.ready>0)else assert(stream.ready==0)end
end end
assert(n==3)
local zero=CSC_AI_EconomyModel.Forecast(s,function()return 0 end)
assert(zero.alternative==PRODUCER)
HOST_DAMAGED=false;assert(evaluate().valueQ8==3*30*256)
''')

    def test_damaged_customer_host_preserves_owner_only_fixed_direction(self):
        vm=world(quarter='TAILORS',host='IMPROVEMENT_UNREGISTERED',customer=True)
        vm.execute('''
WORKERS=0;CUSTOMER_DAMAGED=true
local r,s=evaluate();assert(#s.customers==1)
assert(s.customers[1].intactOwner and not s.customers[1].working)
assert(#r.streams==2)
for _,stream in ipairs(r.streams)do assert(stream.recipientBuilding==PRODUCER)end
local zero=CSC_AI_EconomyModel.Forecast(s,function()return 0 end);assert(#zero.streams==2)
CUSTOMER_DAMAGED=false;assert(#evaluate().streams==3)
''')


if __name__=='__main__':unittest.main()
