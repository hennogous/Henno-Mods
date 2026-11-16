"""Fixed catalogue drives native rules and the economic model with the same terms."""
import json
from pathlib import Path
import sqlite3
import unittest
from lupa.lua51 import LuaRuntime

from population_catalogue_fixture import ROOT,MOD,compile_catalogue,graph
from test_population_catalogue import digest,lua

HERE=Path(__file__).resolve().parent
PROCESSOR=MOD/'Data/CSC_FixedBuildingTransactionProcessor.sql'


def transactions(db):
    result={}
    for r in db.execute("SELECT * FROM CSC_BuildingTransactions WHERE QuantityKind='FIXED'").fetchall():
        legs=[dict(key=l['LegKey'],recipient=l['Recipient'],yield_=l['YieldType'],amount=l['AmountPerUnit'])
            for l in db.execute('SELECT * FROM CSC_BuildingTransactionYields WHERE TransactionId=?',(r['TransactionId'],))]
        for leg in legs:leg['yield']=leg.pop('yield_')
        result[r['SourceBuildingType']+':'+r['PartnerBuildingType']]=dict(id=r['TransactionId'],kind='FIXED',amount=r['QuantityAmount'],legs=legs)
    return result


class FixedTransactions(unittest.TestCase):
    def model(self,db):
        vm=LuaRuntime();vm.execute((MOD/'Lua_UI/AI/CSC_AI_EconomyModel.lua').read_text())
        vm.execute('TX='+lua(transactions(db))+'''
M=CSC_AI_EconomyModel
local water='BUILDING_CSC_BAKERS_WATER_MILL';local wind='BUILDING_CSC_BAKERS_WIND_MILL'
local buyer='BUILDING_GRANARY'
site={city=1,population=10,horizon=30,quarterReady=0,existing=true,materialYield='YIELD_FOOD',
 seconds={{type=water,working=true},{type=wind,working=true}},direct={},suppliers={},
 customers={{type=buyer,building=buyer,city=1,plot=7,stage=2,complete=true,working=true,
   transactions={[water]=TX[water..':'..buyer],[wind]=TX[wind..':'..buyer]}}}}
price=function(s,h)return s.amount*(h-s.ready)*256 end
''')
        return vm

    def test_native_graph_matches_qa_baseline_including_owner_replacements(self):
        reference=json.loads((HERE/'fixed_qa_reference.json').read_text())
        for gold in [False,True]:
            for uniques in [False,True]:
                db=compile_catalogue(gold=gold,uniques=uniques)
                actual=graph(db,'fixed');key=f'{int(gold)}:{int(uniques)}'
                self.assertEqual(digest(actual),reference[key]['sha256'])
                self.assertEqual(sum(map(len,actual.values())),reference[key]['rows'])
                db.close()

    def test_declared_amount_reaches_native_and_model_once_with_one_mill(self):
        db=compile_catalogue()
        db.execute("UPDATE CSC_BuildingTransactionYields SET AmountPerUnit=2 WHERE LegKey='PARTNER_RETURN' AND TransactionId IN (SELECT TransactionId FROM CSC_BuildingTransactions WHERE QuantityKind='FIXED' AND PartnerBuildingType='BUILDING_GRANARY')")
        db.executescript(PROCESSOR.read_text())
        amount=db.execute("SELECT Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY' AND Name='Amount'").fetchone()[0]
        self.assertEqual(float(amount),2)
        self.model(db).execute("local r=M.Forecast(site,price);assert(r.valueQ8==4*30*256)")
        db.close()

    def test_shared_native_leaf_rejects_conflicting_terms(self):
        db=compile_catalogue()
        db.execute("UPDATE CSC_BuildingTransactionYields SET AmountPerUnit=2 WHERE LegKey='PARTNER_RETURN' AND TransactionId='CSC_BAKERS_WATER_MILL_GRANARY'")
        with self.assertRaises(sqlite3.IntegrityError):db.executescript(PROCESSOR.read_text())
        db.close()

    def test_local_recipient_and_enabling_investment_are_separate(self):
        db=compile_catalogue();vm=self.model(db)
        vm.execute('''
local bakery='BUILDING_CSC_BAKERS_BAKERY'
site.customers={};site.third={type=bakery,working=true,localTransactions={}}
for _,second in ipairs(site.seconds)do site.third.localTransactions[second.type]=TX[second.type..':'..bakery]end
local r=M.Forecast(site,price);assert(r.valueQ8==3*30*256)
local n=0
for _,s in ipairs(r.streams)do if s.id:find('local:',1,true)==1 then
 n=n+1;assert(s.investmentBuilding==bakery)
 if s.yield=='YIELD_FOOD'then assert(s.recipientBuilding==bakery)
 else assert(s.recipientBuilding==r.alternative)end
end end
assert(n==3)
''');db.close()

    def test_absent_canonical_transaction_does_not_invent_unit_income(self):
        db=compile_catalogue();vm=self.model(db)
        vm.execute('''site.customers[1].transactions={};assert(M.Forecast(site,price).valueQ8==0)''')
        db.close()


if __name__=='__main__':unittest.main()
