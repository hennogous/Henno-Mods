"""Production SQL/Core/Facts/Model, with a small physical two-city hex map.

Only native definitions and game-object APIs are fixtures. Quarter partner,
material, route, adjacency and payout rules come from current gameplay source.
"""
from functools import lru_cache
import re
from lupa.lua51 import LuaRuntime
from population_catalogue_fixture import compile_catalogue,MOD,statements
from driver import lua


@lru_cache(maxsize=2)
def definitions(city_lights):
    db=compile_catalogue()
    db.executescript('CREATE TABLE Tags(Tag TEXT PRIMARY KEY,Vocabulary TEXT);CREATE TABLE TypeTags(Type TEXT,Tag TEXT,PRIMARY KEY(Type,Tag));CREATE TABLE Districts(DistrictType TEXT PRIMARY KEY);')
    db.executescript('''
CREATE TABLE IF NOT EXISTS DistrictReplaces(CivUniqueDistrictType TEXT,ReplacesDistrictType TEXT);
CREATE TABLE Improvements(ImprovementType TEXT PRIMARY KEY);
CREATE TABLE Improvement_ValidResources(ImprovementType TEXT,ResourceType TEXT);
INSERT INTO Improvements SELECT DISTINCT ImprovementType FROM ImprovementModifiers;
INSERT OR IGNORE INTO Improvements VALUES('IMPROVEMENT_FARM');
INSERT INTO Improvement_ValidResources VALUES('IMPROVEMENT_FARM','RESOURCE_WHEAT');
''')
    db.executescript((MOD/'Data/CSC_Q_ALL_MaterialHosts.sql').read_text())
    # compile_catalogue loads the shared schema, including adjacency config.
    for name in ('CSC_AdjacencySchema.sql','CSC_AdjacencySources.sql'):
        db.executescript((MOD/'Lua_UI/Adjacencies'/name).read_text())
    sources=[MOD/f'Data/CSC_Q_{q}.sql'for q in ('BAKERS','TAILORS')]
    if city_lights:sources.append(MOD/'ModSupport/ModSupport_CL.sql')
    for source in sources:
        for s in statements(source.read_text(encoding='utf-8-sig')):
            if re.match(r'INSERT(?: OR IGNORE)? INTO (?:Tags|TypeTags|CSC_QuarterMaterialAdjacencyConfig)\b',s):db.executescript(s)
    kinds={'DISTRICT_CITY_CENTER','DISTRICT_COMMERCIAL_HUB','DISTRICT_HARBOR','DISTRICT_HOLY_SITE',
           'DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER'}
    kinds|={r[0]for r in db.execute("SELECT DISTINCT Type FROM TypeTags WHERE Type LIKE 'DISTRICT_%'")}
    kinds|={r[0]for r in db.execute('SELECT DISTINCT PrereqDistrict FROM Buildings')}
    db.executemany('INSERT INTO Districts VALUES(?)',[(v,)for v in sorted(kinds)])
    db.executescript((MOD/'Lua_UI/Adjacencies/CSC_AdjacencyProcessor.sql').read_text())
    tables={name:[dict(r)for r in db.execute('SELECT * FROM '+name)]for name, in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    db.close()
    return tables


def world(*,city_lights=False):
    vm=LuaRuntime(unpack_returned_tuples=True)
    vm.execute('TABLES='+lua(definitions(city_lights))+'''
function info(rows,key)
 local result={}
 for i,r in ipairs(rows)do r.Index=i-1;result[r.Index]=r;if key then result[r[key]]=r end end
 return setmetatable(result,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
GameInfo={}
for name,rows in pairs(TABLES)do GameInfo[name]=info(rows,
 name=='Buildings'and'BuildingType'or name=='Districts'and'DistrictType'or name=='Tags'and'Tag'or nil)end
for _,name in ipairs({'BuildingPrereqs','MutuallyExclusiveBuildings','TechnologyPrereqs','CivicPrereqs',
 'CivilizationTraits','LeaderTraits','Technologies','Civics','BuildingReplaces'})do GameInfo[name]=info({})end
local resources={};local seen={}
for row in GameInfo.TypeTags()do if row.Type:find('RESOURCE_',1,true)==1 and not seen[row.Type]then
 resources[#resources+1]={ResourceType=row.Type};seen[row.Type]=true
end end
table.sort(resources,function(a,b)return a.ResourceType<b.ResourceType end)
GameInfo.Resources=info(resources,'ResourceType')
GameInfo.Improvements=info(TABLES.Improvements,'ImprovementType')
GameInfo.Yields=info({{YieldType='YIELD_FOOD'},{YieldType='YIELD_PRODUCTION'},
 {YieldType='YIELD_GOLD'},{YieldType='YIELD_CULTURE'}},'YieldType')
GameInfo.Eras={[1]={EraType='ERA_CLASSICAL'}}
GameInfo.GameSpeeds={ONLINE={CostMultiplier=50}}
GameInfo.GlobalParameters={TRADE_ROUTE_TURN_DURATION_BASE={Value=20}}
for row in GameInfo.Districts()do row.OnePerCity=1;row.RequiresPopulation=1 end
for row in GameInfo.Buildings()do row.MustPurchase=1 end
for _,kind in ipairs({'BUILDING_CSC_BAKERS_WIND_MILL','BUILDING_CSC_BAKERS_BAKERY','BUILDING_MARKET'})do
 GameInfo.Buildings[kind].MustPurchase=0
end
GameInfo.Buildings.BUILDING_MARKET.Maintenance=1
PLOTS={};CITIES={};UNITS={};PLACED={};BUILDINGS={};PACKET_TURN=20
function plot(id,x,y,city,resource,improvement,district)
 local p={id=id,x=x,y=y,city=city,resource=resource,improvement=improvement,district=district,workers=0}
 p.GetIndex=function(s)return s.id end;p.GetX=function(s)return s.x end;p.GetY=function(s)return s.y end
 p.GetOwner=function()return 1 end;p.GetWorkerCount=function(s)return s.workers end
 p.GetResourceType=function(s)return s.resource and GameInfo.Resources[s.resource].Index or -1 end
 p.GetImprovementType=function(s)return s.improvement and GameInfo.Improvements[s.improvement].Index or -1 end
 p.GetDistrictType=function(s)return s.district and GameInfo.Districts[s.district].Index or -1 end
 p.GetTerrainType=function()return 0 end;p.GetFeatureType=function()return -1 end
 p.IsImprovementPillaged=function()return false end;p.IsRiver=function()return false end
 p.GetRiverCrossingCount=function()return 0 end;p.IsHills=function()return false end
 PLOTS[id]=p;return p
end
plot(1,0,0,1,nil,nil,'DISTRICT_CSC_BAKERS_QUARTER')
plot(2,2,0,2,nil,nil,'DISTRICT_CSC_BAKERS_QUARTER')
plot(3,1,0,3)
plot(4,0,1,1,'RESOURCE_WHEAT','IMPROVEMENT_FARM').workers=1
plot(5,2,1,2,'RESOURCE_WHEAT','IMPROVEMENT_FARM').workers=1
plot(6,-1,0,1,nil,nil,'DISTRICT_CITY_CENTER')
plot(7,3,0,2,nil,nil,'DISTRICT_CITY_CENTER')
plot(8,1,-1,3,nil,nil,'DISTRICT_CITY_CENTER')
Map={GetPlotByIndex=function(id)return PLOTS[id]end,GetPlot=function(x,y)
 for _,p in pairs(PLOTS)do if p.x==x and p.y==y then return p end end
end,GetPlotDistance=function(x,y,a,b)return math.max(math.abs(x-a),math.abs(y-b),math.abs(x-a+y-b))end}
Map.GetAdjacentPlots=function(x,y)
 local result={};for _,p in pairs(PLOTS)do if Map.GetPlotDistance(x,y,p.x,p.y)==1 then result[#result+1]=p end end
 table.sort(result,function(a,b)return a.id<b.id end);return result
end
function grant(city,kind,location)BUILDINGS[city][kind]={location=location}end
function city(id,center)
 BUILDINGS[id]={}
 local buildings={HasBuilding=function(_,index)local b=GameInfo.Buildings[index];return b and BUILDINGS[id][b.BuildingType]~=nil end,
 IsPillaged=function()return false end,GetBuildingLocation=function(_,index)
  local b=GameInfo.Buildings[index];local actual=b and BUILDINGS[id][b.BuildingType];return actual and actual.location or -1
 end}
 local ds={}
 ds.GetNumDistricts=function()local n=0;for _,p in pairs(PLOTS)do if p.city==id and p.district then n=n+1 end end;return n end
 ds.GetDistrictByIndex=function(_,index)
  local items={};for _,p in pairs(PLOTS)do if p.city==id and p.district then items[#items+1]=p end end
  table.sort(items,function(a,b)return a.id<b.id end);local p=items[index+1];if not p then return end
  return{GetType=p.GetDistrictType,GetX=function()return p.x end,GetY=function()return p.y end,
   IsComplete=function()return not p.incomplete end,IsPillaged=function()return p.pillaged or false end}
 end
 -- GetType requires the plot receiver rather than the district object's table.
 local indexed=ds.GetDistrictByIndex
 ds.GetDistrictByIndex=function(_,index)local d=indexed(ds,index);if d then
  local p=Map.GetPlot(d:GetX(),d:GetY());d.GetType=function()return p:GetDistrictType()end
 end;return d end
 ds.HasDistrict=function(_,index)for _,p in pairs(PLOTS)do if p.city==id and p:GetDistrictType()==index then return true end end;return false end
 ds.IsPillaged=function(_,index)
  for _,p in pairs(PLOTS)do if p.city==id and p:GetDistrictType()==index then return p.pillaged or false end end
  return false
 end
 local c={GetID=function()return id end,GetOwner=function()return 1 end,GetPopulation=function()return 9 end,
  GetX=function()return PLOTS[center].x end,GetY=function()return PLOTS[center].y end,
  GetBuildings=function()return buildings end,GetDistricts=function()return ds end,
  GetBuildQueue=function()return{}end,GetProperty=function()return 0 end,
  GetTrade=function()return{GetOutgoingRoutes=function()return{}end}end}
 CITIES[id]=c;return c
end
city(1,6);city(2,7);city(3,8)
for id=1,2 do grant(id,'BUILDING_CSC_BAKERS_WIND_MILL',id);grant(id,'BUILDING_CSC_BAKERS_BAKERY',id)end
player={GetID=function()return 1 end,IsHuman=function()return false end,GetCulture=function()return{HasCivic=function()return true end,IsPolicyActive=function()return false end}end,
 GetTechs=function()return{HasTech=function()return true end}end,GetCities=function()return{
  FindID=function(_,id)return CITIES[id]end,Members=function()local i=0;return function()i=i+1;if CITIES[i]then return i,CITIES[i]end end end}end}
Players={[1]=player};PlayersVisibility={[1]={IsRevealed=function()return true end}}
PlayerConfigurations={};Cities={GetPlotPurchaseCity=function(p)return CITIES[p.city]end,
 GetPlotWorkingCity=function(id)return CITIES[PLOTS[id].city]end}
Game={GetCurrentGameTurn=function()return 20 end,GetEras=function()return{GetCurrentEra=function()return 1 end}end}
GameConfiguration={GetGameSpeedType=function()return'ONLINE'end};UnitOperationTypes={}
ui={GetEconomyCityNumber=function(_,_,kind)return kind=='districtTurns'and 4 or kind=='buildingTurns'and 2 or 10 end,
 GetEconomyPlotFacts=function(id)local p=PLOTS[id];return{turn=20,plotOwner=1,workers=p.workers,workingPlayer=1,workingCity=p.city,yields={}}end}
profile={key='BAKERS',district=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER,
 base='CLASS_CSC_BAKERS_BASE',specialty='CLASS_CSC_BAKERS_SPEC'}
tailorProfile={key='TAILORS',district=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER,
 base='CLASS_CSC_TAILORS_BASE',specialty='CLASS_CSC_TAILORS_SPEC'}
placement={StageTwoProfiles=function()return{profile,tailorProfile}end,ReadSuppliers=function()return{base={},specialty={}}end}
placement.ReadChains=function()
 local result={};for id=1,2 do for _,p in ipairs(placement.StageTwoProfiles())do
  if PLOTS[id].district==p.district.DistrictType then
   result[#result+1]={profile=p,city=CITIES[PLOTS[id].city],plot=PLOTS[id],complete=not PLOTS[id].incomplete}
  end
 end end;return result
end
include=function()end
DefenseTypes={DISTRICT_GARRISON=0,DISTRICT_OUTER=1}
''')
    for name in ('Adjacencies/CSC_AdjacencyCore.lua','TradeRoutes/CSC_TradeRouteCore.lua','TradeRoutes/CSC_TradeRouteFacts.lua',
                 'AI/CSC_AI_EconomyFacts.lua','AI/CSC_AI_EconomyModel.lua'):
        vm.execute((MOD/'Lua_UI'/name).read_text())
    vm.execute('''
CSC_Adjacency.Initialize()
local reader=CSC_TradeRouteFacts.New(GameInfo,assert(CSC_TradeRouteCore.ReadDefinitions(GameInfo)))
ExposedMembers={CSC_TradeRoutes={GetFacts=function()
 local facts=assert(reader.Snapshot({player},PACKET_TURN));facts.version=1;return facts
end}}
function snapshot()return CSC_AI_EconomyFacts.New(player,placement,ui,{horizon=30})end
function price(s,h)return math.floor(s.amount*(math.min(h,s.finish or h)-s.ready)*256+.000001)end
''')
    return vm
