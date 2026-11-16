"""Directional materials preserve gameplay and drive model amounts/eligibility."""
from pathlib import Path
import json,unittest,sqlite3
from lupa.lua51 import LuaRuntime
from population_catalogue_fixture import compile_catalogue,graph,MOD,legacy_reference_graph
from test_population_catalogue import digest,lua

HERE=Path(__file__).resolve().parent
PROCESSOR=MOD/'Data/CSC_MaterialTransactionProcessor.sql'
WIND='BUILDING_CSC_BAKERS_WIND_MILL'


def loaded(db,producer=WIND):
    row=db.execute('SELECT * FROM CSC_MaterialTransactions WHERE ProducerBuildingType=?',(producer,)).fetchone()
    outputs=[]
    for leg in db.execute('''SELECT y.*,b.RootModifierId FROM CSC_MaterialTransactionYields y
        JOIN CSC_MaterialTransactionBindings b USING(TransactionId,LegKey) WHERE y.TransactionId=?''',(row['TransactionId'],)):
        hosts={r[0]:True for r in db.execute('SELECT ImprovementType FROM ImprovementModifiers WHERE ModifierId=?',(leg['RootModifierId'],))}
        outputs.append(dict(key=leg['LegKey'],recipient=leg['Recipient'],yield_=leg['YieldType'],
            amount=leg['Amount'],scope=leg['ImprovementScope'],improvement=leg['ImprovementType'],hosts=hosts))
    for leg in outputs:leg['yield']=leg.pop('yield_')
    return dict(id=row['TransactionId'],producer=producer,legs=outputs)


def model(transaction,improvement,*,worked=True,ready=0):
    vm=LuaRuntime()
    for name in('Facts','Model'):vm.execute((MOD/f'Lua_UI/AI/CSC_AI_Economy{name}.lua').read_text())
    vm.execute('TX='+lua(transaction)+'\nIMPROVEMENT='+lua(improvement)+'\nREADY='+lua(ready)+'\nWORKED='+lua(worked)+'''
local selected=CSC_AI_EconomyFacts.SelectMaterialLegs(TX,IMPROVEMENT,READY)
site={city=1,population=10,horizon=30,quarterReady=0,existing=true,
 seconds={{type=TX.producer,working=true}},direct={},customers={},
 suppliers={{kind='base',plot=9,city=2,worked=WORKED,transactions={[TX.producer]=selected}}}}
result=CSC_AI_EconomyModel.Forecast(site,function(s,h)return s.amount*(h-s.ready)*256 end)
''')
    return vm


class MaterialCatalogue(unittest.TestCase):
    def test_native_graph_matches_qa_source_with_gold_and_mc_switches(self):
        reference=json.loads((HERE/'material_qa_reference.json').read_text())
        for gold in(False,True):
            for mc in(False,True):
                db=compile_catalogue(gold=gold,mc=mc,lgd=False)
                actual=legacy_reference_graph(db,'material');expected=reference[f'{int(gold)}:{int(mc)}']
                self.assertEqual(digest(actual),expected['sha256'])
                self.assertEqual(sum(map(len,actual.values())),expected['rows']);db.close()

    def test_mc_inputs_and_incremental_returns_reach_model_once(self):
        for gold in(False,True):
            db=compile_catalogue(gold=gold,mc=True)
            for improvement,units in [('IMPROVEMENT_FARM',3 if gold else 2),('IMPROVEMENT_INDUSTRY',6 if gold else 4),('IMPROVEMENT_CORPORATION',9 if gold else 6)]:
                vm=model(loaded(db),improvement)
                self.assertEqual(vm.globals().result.valueQ8,units*30*256)
                vm.execute("for _,s in ipairs(result.streams)do if s.yield=='YIELD_FOOD'then assert(s.city==1)else assert(s.city==2)end end")
            db.close()

    def test_unregistered_host_keeps_return_without_inventing_input(self):
        db=compile_catalogue(mc=True);transaction=loaded(db)
        vm=model(transaction,'IMPROVEMENT_UNREGISTERED')
        self.assertEqual(vm.globals().result.valueQ8,2*30*256)
        self.assertEqual(model(transaction,'IMPROVEMENT_UNREGISTERED',worked=False).globals().result.valueQ8,0)
        self.assertEqual(model(transaction,None).globals().result.valueQ8,0);db.close()

    def test_working_citizen_gates_return_income_not_producer_input(self):
        db=compile_catalogue();transaction=loaded(db)
        vm=model(transaction,'IMPROVEMENT_FARM',worked=False)
        self.assertEqual(vm.globals().result.valueQ8,30*256)
        delayed=model(transaction,'IMPROVEMENT_FARM',ready=5)
        self.assertEqual(delayed.globals().result.valueQ8,3*25*256);db.close()

    def test_changed_input_amount_reaches_native_and_model(self):
        db=compile_catalogue()
        db.execute("UPDATE CSC_MaterialTransactionYields SET Amount=2 WHERE TransactionId='CSC_BAKERS_WIND_MILL_BASE' AND LegKey='INPUT_ORDINARY'")
        db.executescript(PROCESSOR.read_text())
        native=db.execute("SELECT Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WIND_MILL' AND Name='Amount'").fetchone()[0]
        self.assertEqual(float(native),2)
        self.assertEqual(model(loaded(db),'IMPROVEMENT_FARM').globals().result.valueQ8,4*30*256);db.close()

    def test_conflicting_shared_fixed_material_leaf_is_rejected(self):
        db=compile_catalogue()
        db.execute("UPDATE CSC_MaterialTransactionYields SET Amount=2 WHERE TransactionId='CSC_BAKERS_CAFE_SPEC' AND LegKey='INPUT_ORDINARY'")
        with self.assertRaises(sqlite3.IntegrityError):db.executescript(PROCESSOR.read_text())
        db.close()

    def test_empty_canonical_map_never_falls_back_to_unit_income(self):
        db=compile_catalogue();vm=model(loaded(db),'IMPROVEMENT_FARM')
        vm.execute('site.suppliers[1].transactions={};assert(CSC_AI_EconomyModel.Forecast(site,function()return 1 end).valueQ8==0)')
        db.close()

    def test_incomplete_bindings_or_extra_gate_are_rejected(self):
        mutations=[
            "DELETE FROM CSC_MaterialTransactionBindings WHERE TransactionId='CSC_BAKERS_WIND_MILL_BASE' AND LegKey='INPUT_ORDINARY'",
            "DELETE FROM CSC_MaterialTransactionGateBindings WHERE TransactionId='CSC_BAKERS_WIND_MILL_BASE' AND LegKey='INPUT_ORDINARY'",
            "UPDATE CSC_MaterialTransactionYields SET ImprovementType='IMPROVEMENT_MINE' WHERE TransactionId='CSC_BAKERS_WIND_MILL_BASE' AND LegKey='INPUT_INDUSTRY'",
            "INSERT INTO RequirementSetRequirements VALUES('REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE','REQ_CSC_TEST_EXTRA_GATE')",
        ]
        for statement in mutations:
            db=compile_catalogue(mc=True);db.execute(statement)
            with self.assertRaises(sqlite3.IntegrityError):db.executescript(PROCESSOR.read_text())
            db.close()

    def test_finite_gate_and_modifier_fields_are_stably_normalised(self):
        from test_native_foreign_keys import native_keys
        db=compile_catalogue(mc=True);native_keys(db)
        db.execute("UPDATE Requirements SET Inverse=1 WHERE RequirementId='REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'")
        db.execute("UPDATE RequirementSets SET RequirementSetType='REQUIREMENTSET_TEST_ANY' WHERE RequirementSetId='REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'")
        db.executescript(PROCESSOR.read_text())
        self.assertEqual(db.execute("SELECT Inverse FROM Requirements WHERE RequirementId='REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'").fetchone()[0],0)
        self.assertEqual(db.execute("SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId='REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'").fetchone()[0],'REQUIREMENTSET_TEST_ALL')
        db.close()

    def test_zero_price_does_not_erase_a_physically_working_producer(self):
        db=compile_catalogue();vm=model(loaded(db),'IMPROVEMENT_FARM')
        vm.execute('local r=CSC_AI_EconomyModel.Forecast(site,function()return 0 end);assert(r.alternative==TX.producer);assert(#r.streams==3)')
        db.close()

    def test_intact_stage_four_returns_survive_masks_without_rebuilding_owner(self):
        cafe='BUILDING_CSC_BAKERS_CAFE'
        db=compile_catalogue();transaction=loaded(db,cafe);vm=model(transaction,'IMPROVEMENT_MINE')
        vm.execute('''
site.suppliers[1].kind='specialty'
site.seconds={{type='BUILDING_CSC_BAKERS_WIND_MILL',working=false,intactOwner=true,hostReady=10}}
site.fourth={type=TX.producer,working=false,intactOwner=true,hostReady=10,maintenance=999,cost=999,turns=999,localTransactions={}}
for _,leg in ipairs(site.suppliers[1].transactions[TX.producer].legs)do
 if leg.recipient=='IMPROVEMENT'then leg.producerReady=0 end
end
for _,price in ipairs({function()return 0 end,function(s,h)return s.amount*(h-s.ready)*256 end})do
 local r=CSC_AI_EconomyModel.Forecast(site,price)
 local n=0
 for _,stream in ipairs(r.streams)do
  assert(not stream.id:find('upkeep:',1,true))
  if stream.id:find('material:',1,true)==1 then n=n+1 end
 end
 assert(n==3 and #r.investments==0)
end
''');db.close()


if __name__=='__main__':unittest.main()
