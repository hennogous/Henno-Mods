"""Regression against the gameplay source already QAed before this migration.

The checked-in digest fixtures were produced by executing that source against
the same worlds. They cover complete native graphs and all city/plot properties,
including bit clearing after disruption. Update them only for a reviewed rule
change, never merely because a refactor produces a different result.
"""
import hashlib
import json
from pathlib import Path
import unittest
import sqlite3

from lupa.lua51 import LuaRuntime
from population_catalogue_fixture import ROOT, MOD, compile_catalogue, graph

HERE=Path(__file__).resolve().parent
GAMEPLAY=MOD/'Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def lua(value):
    if value is None:return 'nil'
    if isinstance(value,bool):return 'true'if value else 'false'
    if isinstance(value,(float,int)):return str(value)
    if isinstance(value,str):return json.dumps(value)
    if isinstance(value,list):return '{'+','.join(map(lua,value))+'}'
    return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in value.items())+'}'


WORLD=r'''
local function info(rows,key)
 local t={};for i,r in ipairs(rows)do r.Index=i-1;t[r[key]]=r;t[r.Index]=r end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
GameInfo={};for name,rows in pairs(TABLES)do GameInfo[name]=info(rows,KEYS[name])end
GameInfo.BuildingReplaces=info({{CivUniqueBuildingType='BUILDING_UNIQUE_MARKET',ReplacesBuildingType='BUILDING_MARKET'}},'CivUniqueBuildingType')
GameInfo.DistrictReplaces=info({{CivUniqueDistrictType='DISTRICT_UNIQUE_HUB',ReplacesDistrictType='DISTRICT_COMMERCIAL_HUB'}},'CivUniqueDistrictType')
Events={};GameEvents={};DirectionTypes={NUM_DIRECTION_TYPES=6}
local plots={};CITY_LIST={};local players={}
local function plot(id)
 if not plots[id]then
  local p={properties={},adj={}};plots[id]=p
  function p:GetX()return id end;function p:GetY()return 0 end
  function p:GetProperty(k)return self.properties[k]end
  function p:SetProperty(k,v)self.properties[k]=v end
 end;return plots[id]
end
function link(a,b)
 local aa,bb=plot(a),plot(b);aa.adj[#aa.adj+1]=bb;bb.adj[#bb.adj+1]=aa
 assert(#aa.adj<=6 and #bb.adj<=6)
end
function addCity(id,population,owner)
 local c={id=id,population=population,owner=owner or 1,properties={},districts={},buildings={}}
 CITY_LIST[id]=c;plot(1000+id)
 function c:GetID()return self.id end;function c:GetOwner()return self.owner end
 function c:GetPopulation()return self.population end
 function c:GetX()return 1000+self.id end;function c:GetY()return 0 end
 function c:GetProperty(k)return self.properties[k]end;function c:SetProperty(k,v)self.properties[k]=v end
 local ds={};function c:GetDistricts()return ds end
 function ds:HasDistrict(i)return c.districts[i]~=nil end
 function ds:IsPillaged(i)return c.districts[i]and c.districts[i].pillaged or false end
 function ds:GetDistrictLocation(i)return c.districts[i].plot,0 end
 local bs={};function c:GetBuildings()return bs end
 function bs:HasBuilding(i)return c.buildings[i]~=nil end
 function bs:IsPillaged(i)return c.buildings[i]and c.buildings[i].pillaged or false end
 function bs:GetBuildingLocation(i)return c.buildings[i].plot end
 return c
end
function district(c,name,p,pillaged)c.districts[GameInfo.Districts['DISTRICT_'..name].Index]={plot=p,pillaged=pillaged};plot(p)end
function building(c,name,p,pillaged)c.buildings[GameInfo.Buildings['BUILDING_'..name].Index]={plot=p,pillaged=pillaged};plot(p)end
local a,b,buyer,tailor=addCity(1,8),addCity(2,11),addCity(3,POP),addCity(4,12)
district(a,'CSC_BAKERS_QUARTER',10);district(b,'CSC_BAKERS_QUARTER',20)
for _,seller in ipairs({a,b})do
 local p=seller.id*10;building(seller,'CSC_BAKERS_BAKERY',p);building(seller,'CSC_BAKERS_CAFE',p)
end
district(tailor,'CSC_TAILORS_QUARTER',40);building(tailor,'CSC_TAILORS_TAILOR',40);building(tailor,'CSC_TAILORS_FASHION_HOUSE',40)
local hub=UNIQUE and 'UNIQUE_HUB'or'COMMERCIAL_HUB'
district(buyer,hub,301);building(buyer,UNIQUE and'UNIQUE_MARKET'or'MARKET',301)
district(buyer,'ENTERTAINMENT_COMPLEX',302);building(buyer,'ZOO',302)
district(buyer,'WATER_ENTERTAINMENT_COMPLEX',303);building(buyer,'FERRIS_WHEEL',303)
if LGD then district(buyer,'LEU_GARDEN',304);building(buyer,'LEU_CONSERVATORY',304)end
district(buyer,'HOLY_SITE',305);building(buyer,'TEMPLE',305)
district(buyer,'THEATER',306);building(buyer,'AMPHITHEATER',306)
-- Deliberately make the city's first Wonder location unrelated. Each real
-- Wonder must be resolved through its specific building location instead.
district(buyer,'WONDER',399)
building(buyer,'BOLSHOI_THEATRE',307);building(buyer,'BROADWAY',308);building(buyer,'SYDNEY_OPERA_HOUSE',309)
for _,p in ipairs({301,302,303})do link(10,p);link(20,p)end
if LGD then link(10,304);link(20,304)end
for _,p in ipairs({301,305,306,307,308,309})do link(40,p)end
Map={GetPlot=function(x,y)return plots[x]end,GetPlotByIndex=function(i)return plots[i]end,
 GetAdjacentPlot=function(x,y,d)return plots[x].adj[d+1]end}
PlayerManager={GetAlive=function()
 local grouped={};for _,c in ipairs(CITY_LIST)do grouped[c.owner]=grouped[c.owner]or{};table.insert(grouped[c.owner],c)end
 local all={};for id,list in pairs(grouped)do
  local p={};function p:GetID()return id end
  function p:GetCities()return{Members=function()local i=0;return function()i=i+1;if list[i]then return i,list[i]end end end}end
  all[#all+1]=p
 end;return all
end}
function properties()
 local result={};for _,c in ipairs(CITY_LIST)do
  local cc={};for k,v in pairs(c.properties)do if v~=0 then cc[k]=v end end
  local pp={};for k,v in pairs(plots[1000+c.id].properties)do if v~=0 then pp[k]=v end end
  result[#result+1]={city=cc,plot=pp}
 end;return result
end
'''


SCENARIOS={
    'all':'',
    'partner_district_pillaged':"for _,d in pairs(CITY_LIST[3].districts)do d.pillaged=true end",
    'partner_buildings_pillaged':"for _,b in pairs(CITY_LIST[3].buildings)do b.pillaged=true end",
    'source_district_pillaged':"for _,c in ipairs({CITY_LIST[1],CITY_LIST[2],CITY_LIST[4]})do for _,d in pairs(c.districts)do d.pillaged=true end end",
    'source_building_pillaged':"for _,c in ipairs({CITY_LIST[1],CITY_LIST[2],CITY_LIST[4]})do for _,b in pairs(c.buildings)do b.pillaged=true end end",
    'capture':"CITY_LIST[3].owner=2",
    'remove':"CITY_LIST[3].buildings={}",
    'one_supplier_removed':"CITY_LIST[1].buildings={}",
    'same_city_market':"district(CITY_LIST[1],'COMMERCIAL_HUB',311);building(CITY_LIST[1],'MARKET',311);link(10,311)",
}


def plain(t):
    if not hasattr(t,'items'):return t
    entries=list(t.items())
    if all(isinstance(k,int)for k,v in entries)and entries:return [plain(t[i])for i in range(1,len(entries)+1)]
    return {k:plain(v)for k,v in entries}


def run_world(db,source,population=10,scenario='all',unique=False,lgd=True):
    rows={n:[dict(r)for r in db.execute('SELECT * FROM '+n)]for n in [
        'Buildings','CSC_Stage3CustomerTransactions','CSC_BuildingTransactions','CSC_BuildingTransactionYields']
        if db.execute('SELECT 1 FROM sqlite_master WHERE name=?',(n,)).fetchone()}
    rows['Buildings'].append(dict(BuildingType='BUILDING_UNIQUE_MARKET',PrereqDistrict='DISTRICT_UNIQUE_HUB',IsWonder=0))
    districts=sorted({b['PrereqDistrict']for b in rows['Buildings']}|{'DISTRICT_UNIQUE_HUB'})
    rows['Districts']=[dict(DistrictType=d)for d in districts]
    keys={n:'TransactionId'for n in rows};keys.update(Buildings='BuildingType',Districts='DistrictType')
    vm=LuaRuntime();vm.execute('TABLES='+lua(rows)+';KEYS='+lua(keys)+f';POP={population};UNIQUE='+lua(unique)+';LGD='+lua(lgd))
    vm.execute(WORLD);vm.execute(source);vm.globals().CSC_RefreshCustomerPopulationReturns()
    initial=plain(vm.globals().properties())
    vm.execute(SCENARIOS[scenario]);vm.globals().CSC_RefreshCustomerPopulationReturns()
    changed=plain(vm.globals().properties())
    vm.globals().CSC_RefreshCustomerPopulationReturns()
    assert changed==plain(vm.globals().properties()),'Refresh must be idempotent'
    return dict(initial=initial,after=changed)


class PopulationCatalogue(unittest.TestCase):
    def test_build_wiring_runs_definitions_and_modsupport_before_their_readers(self):
        data=json.loads((ROOT/'project/modbuddy/CivSupplyChains.actions.json').read_text())
        actions={a['id']:a for a in data['blocks']['inGameActions']}
        order=lambda key:int(actions[key]['properties']['LoadOrder'])
        self.assertIn('Data/CSC_BuildingTransactionSchema.sql',actions['CSC_Q_ALL']['files'])
        for q in ['BAKERS','TAILORS']:
            self.assertIn(f'Data/CSC_Q_{q}_TRANSACTIONS.sql',actions['CSC_Q_'+q]['files'])
            self.assertIn(f'Data/CSC_Q_{q}_TRANSACTIONS_GOLD.sql',actions['CSC_Q_'+q+'_GOLD']['files'])
            self.assertLess(order('CSC_Q_ALL'),order('CSC_Q_'+q))
            self.assertLess(order('CSC_Q_'+q+'_GOLD'),order('CSC_BuildingTransactionProcessor'))
        self.assertLess(order('ModSupport_LGD'),order('CSC_BuildingTransactionProcessor'))
        self.assertLess(order('CSC_BuildingTransactionProcessor'),order('CSC_AdjacencyProcessor'))
        self.assertLess(order('CSC_AdjacencyProcessor'),order('CSC_AI_Connectors'))
        self.assertNotIn('criteria',actions['CSC_BuildingTransactionProcessor'])

    def test_contract_rejects_unimplemented_shapes_and_mismatched_native_bindings(self):
        for mutation in [
            "UPDATE CSC_QuarterFlowBuildings SET Stage=2 WHERE BuildingType='BUILDING_CSC_BAKERS_BAKERY'",
            "UPDATE CSC_BuildingTransactionBindings SET RequirementSetPrefix='WRONG_' WHERE TransactionId='CSC_BAKERS_BAKERY_MARKET' AND LegKey='SOURCE_PRODUCTION'",
            "DELETE FROM Modifiers WHERE ModifierId='MOD_CSC_BAKERS_MARKET_RETURN_PROD_AMOUNT_BIT_1'",
            "DELETE FROM CSC_BuildingTransactionBindings WHERE TransactionId='CSC_BAKERS_BAKERY_MARKET' AND LegKey='SOURCE_PRODUCTION'",
            "UPDATE RequirementArguments SET Value='WRONG_PROPERTY' WHERE RequirementId='REQ_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_1' AND Name='PropertyName'",
        ]:
            with self.subTest(mutation=mutation):
                db=compile_catalogue();db.execute(mutation)
                with self.assertRaises(sqlite3.IntegrityError):
                    db.executescript((MOD/'Data/CSC_BuildingTransactionProcessor.sql').read_text())
                db.close()
        db=compile_catalogue()
        for mutation in ["UPDATE CSC_BuildingTransactions SET QuantityKind='UNKNOWN_KIND'",
            "UPDATE CSC_BuildingTransactions SET SpatialRule='SAME_QUARTER'",
            "UPDATE CSC_BuildingTransactionYields SET AmountPerUnit=.5"]:
            with self.assertRaises(sqlite3.IntegrityError):db.execute(mutation)
        db.close()

    def test_changing_canonical_host_gate_changes_stage_three_gameplay(self):
        db=compile_catalogue()
        db.execute("UPDATE CSC_BuildingTransactions SET PartnerDistrictMustFunction=1 WHERE TransactionId='CSC_BAKERS_BAKERY_MARKET'")
        result=run_world(db,GAMEPLAY.read_text(),10,'partner_district_pillaged')
        self.assertGreater(result['initial'][2]['city']['CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT_Q8'],0)
        self.assertNotIn('CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT_Q8',result['after'][2]['city'])
        db.close()

    def test_native_graph_matches_qa_reference_with_and_without_gold_and_lgd(self):
        expected=json.loads((HERE/'population_qa_reference.json').read_text())
        for gold in [False,True]:
            for lgd in [False,True]:
                with self.subTest(gold=gold,lgd=lgd):
                    db=compile_catalogue(gold=gold,lgd=lgd)
                    actual=graph(db);key=f'{int(gold)}:{int(lgd)}'
                    self.assertEqual(digest(actual),expected['graphs'][key]['sha256'])
                    self.assertEqual(sum(map(len,actual.values())),expected['graphs'][key]['rows'])
                    db.close()

    def test_gameplay_payouts_and_clearing_match_qa_reference(self):
        expected=json.loads((HERE/'population_qa_reference.json').read_text())
        for key,sha in expected['worlds'].items():
            gold,lgd,pop,unique,scenario=key.split(':')
            with self.subTest(case=key):
                db=compile_catalogue(gold=gold=='1',lgd=lgd=='1')
                result=run_world(db,GAMEPLAY.read_text(encoding='utf-8'),int(pop),scenario,unique=='1',lgd=='1')
                self.assertEqual(digest(result),sha)
                db.close()

    def test_catalogue_has_ordinary_wonders_and_no_service_gates(self):
        db=compile_catalogue()
        self.assertEqual(db.execute("SELECT COUNT(*) FROM CSC_BuildingTransactions WHERE QuantityKind<>'FIXED'").fetchone()[0],10)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM CSC_BuildingTransactionYields Y JOIN CSC_BuildingTransactions T USING(TransactionId) WHERE T.QuantityKind<>'FIXED'").fetchone()[0],30)
        rows=db.execute("SELECT * FROM CSC_QuarterWonderSales").fetchall()
        self.assertEqual(len(rows),3)
        # The same source property for Production/Gold is counted once by the
        # scanner; a two-supplier Market receives 52/256 per citizen, not 104.
        world=run_world(db,GAMEPLAY.read_text(),10)
        self.assertEqual(world['after'][2]['city']['CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT_Q8'],52)
        self.assertEqual(world['after'][0]['city']['CSC_BAKERS_STAGE_4_CAFE_RETURN'],6)
        db.close()


if __name__=='__main__':unittest.main()
