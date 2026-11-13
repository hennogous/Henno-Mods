"""Census totals count Quarters, not deposits, and preserve missing evidence."""
from pathlib import Path
import json
import tempfile
import unittest
from full_game_results import summarize,economy,census,compare,quarter_rows


class Results(unittest.TestCase):
    def rows(self,folder,rows):
        path=Path(folder)/'joint-census.json'
        path.write_text(json.dumps(dict(turn=200,rows=rows+[['END','200\t'+str(len(rows))]])),encoding='utf-8')
        return path

    def sample(self,folder):
        rows=[['PLAYER','1\ttrue'],['TREASURY','1\t100\t30\t3'],
            ['CITY','1\t42\t10\t15\t5'],
            ['QUARTER','BAKERS\t1\t42\t100\ttrue\tfalse\ttrue\t1\t0\t0'],
            ['MATERIAL','100\t101\tBASE\tRESOURCE_TEST\ttrue'],
            ['MATERIAL','100\t102\tBASE\tRESOURCE_TEST\ttrue'],
            ['MATERIAL','100\t103\tSPEC\tRESOURCE_SPEC\tfalse'],
            ['PRODUCER','100\t2\tBUILDING_TEST\t2'],
            ['CUSTOMER','100\t99\t2\tDISTRICT_CITY_CENTER\ttrue\t2'],
            ['END','200\t9']]
        path=Path(folder)/'census.json'
        path.write_text(json.dumps(dict(turn=200,phase='turn-start',rows=rows)),encoding='utf-8')
        return path

    def test_materials_count_quarters_and_physical_chain_is_distinct(self):
        with tempfile.TemporaryDirectory()as folder:
            result=summarize(self.sample(folder))['BAKERS']
            self.assertEqual([result[k]for k in('complete','base','base_improved','both','stage2_physical','service2_property')],[1,1,1,1,1,1])
            self.assertEqual(result['both_improved'],0)

    def test_economy_reports_gross_and_net_separately(self):
        with tempfile.TemporaryDirectory()as folder:
            total,players=economy(self.sample(folder))
            self.assertEqual((total['players'],total['production'],total['net_gold'],total['food']),(1,15,27,5))

    def test_partial_footer_cannot_be_used_as_comparison_data(self):
        with tempfile.TemporaryDirectory()as folder:
            path=self.sample(folder);data=json.loads(path.read_text());data['rows'].pop()
            path.write_text(json.dumps(data))
            with self.assertRaises(AssertionError):census(path)

    def comparison(self,folder,*,eliminated=False):
        root=Path(folder);run=root/'run';old=root/'old';run.mkdir();old.mkdir()
        template=json.loads(self.sample(folder).read_text())
        def write(path,value):path.write_text(json.dumps(value),encoding='utf-8')
        def sample(path,turn,dead=False):
            rows=([['PLAYER','1\tfalse']]if dead else template['rows'][:-1])+[['PLAYER','2\tfalse']]
            write(path,dict(turn=turn,phase='turn-start',rows=rows+[['END',str(turn)+'\t'+str(len(rows))]]))
        source=dict(original_ai=[1,2],map_signature=[74,46,1],starts=[],units=[])
        protocol=dict(map='Continents',map_size='small',map_seed=1,game_seed=2)
        for path in(run,old):write(path/'source.json',source);write(path/'protocol.json',protocol)
        write(run/'result.json',dict(closed=True,reached=250,storekeeper={}))
        write(run/'session-closed.json',dict(verified=True))
        write(run/'full-game-observation-complete.json',dict(verified=True))
        (run/'Lua.log').write_text('CSC_AI_BAKERS_DISTRICTS turn=1 version=1 players=2 entries=0 omitted=0 previousMatched=0 previousChanged=0\n')
        baseline=root/'baseline.json';sample(baseline,200)
        for turn in range(25,251,25):sample(run/('full-census-'+str(turn)+'.json'),turn,eliminated)
        return run,baseline,old

    def test_comparison_uses_original_seats_and_handles_elimination(self):
        with tempfile.TemporaryDirectory()as folder:
            run,baseline,old=self.comparison(folder,eliminated=True)
            result=compare(run,baseline,old)
            self.assertEqual(result['windows']['baseline200']['average_per_original_ai']['production'],7.5)
            current=result['windows']['harmonised200']
            self.assertEqual(current['average_per_original_ai']['production'],0)
            self.assertIsNone(current['average_per_city']['production'])
            self.assertEqual(current['economy']['players'],0)

    def test_comparison_rejects_wrong_window_even_with_valid_footer(self):
        with tempfile.TemporaryDirectory()as folder:
            run,baseline,old=self.comparison(folder)
            path=run/'full-census-200.json';value=json.loads(path.read_text())
            value['turn']=199;value['rows'][-1][1]='199\t10';path.write_text(json.dumps(value))
            with self.assertRaisesRegex(AssertionError,'comparison-window'):compare(run,baseline,old)

    def test_mismatched_initial_state_is_not_labelled_same_seed(self):
        with tempfile.TemporaryDirectory()as folder:
            run,baseline,old=self.comparison(folder)
            path=old/'source.json';value=json.loads(path.read_text());value['map_signature']=[74,46,2]
            path.write_text(json.dumps(value))
            self.assertNotIn('same-seed',compare(run,baseline,old)['comparison'])
            value['original_ai']=[1];path.write_text(json.dumps(value))
            with self.assertRaisesRegex(AssertionError,'cohorts'):compare(run,baseline,old)

    def test_cityless_survivor_has_zero_city_output(self):
        with tempfile.TemporaryDirectory()as folder:
            path=Path(folder)/'cityless.json'
            path.write_text(json.dumps(dict(turn=200,rows=[['PLAYER','1\ttrue'],
                ['TREASURY','1\t0\t0\t0'],['END','200\t2']])))
            total,players=economy(path)
            self.assertEqual((total['players'],total['cities'],total['production']),(1,0,0))

    def test_joint_counts_deduplicate_edges_and_preserve_resource_and_holder_identity(self):
        with tempfile.TemporaryDirectory()as folder:
            p=self.sample(folder);data=json.loads(p.read_text());rows=data['rows'][:-1]
            rows += [['SALES','100\t99\tDISTRICT_CITY_CENTER'],
                     ['CUSTOMER','100\t99\t2\tDISTRICT_CITY_CENTER\ttrue\t2'],
                     ['CUSTOMER','100\t98\t3\tDISTRICT_CAMPUS\ttrue\t0']]
            p=self.rows(folder,rows);r=summarize(p)['BAKERS']
            for key in('customer_any_completed','customer_any_footprint','base_customer_any',
                       'both_customer_any','base_improved_customer_any','base_customer2',
                       'base_improved_customer2_working'):
                self.assertEqual(r[key],1,key)
            self.assertEqual((r['mapped_customer2_with_working_building'],
                              r['mapped_customer2_without_working_building']), (1,0))
            self.assertEqual((r['mapped_customer3_completed'],
                              r['mapped_customer3_without_working_building']), (1,1))
            row,=quarter_rows(p)
            self.assertEqual((row['player'],row['city'],row['plot']),(1,42,100))
            self.assertEqual(row['materials'][0],['101','BASE','RESOURCE_TEST','true'])

    def test_an_arbitrary_wonder_is_raw_geometry_not_a_confirmed_customer(self):
        with tempfile.TemporaryDirectory()as folder:
            rows=[['QUARTER','TAILORS\t1\t42\t100\ttrue\tfalse\tfalse\t0\t0\t0'],
                  ['MATERIAL','100\t101\tBASE\tRESOURCE_TEST\ttrue'],
                  ['CUSTOMER','100\t99\t4\tDISTRICT_WONDER\ttrue\t0'],
                  ['CUSTOMER_HOST','100\t99\tDISTRICT_WONDER\ttrue\tfalse']]
            r=summarize(self.rows(folder,rows))['TAILORS']
            self.assertEqual((r['raw_customer_geometry_any'],r['customer4']),(1,1))
            self.assertEqual((r['customer_any_footprint'],r['base_customer_any'],
                              r['mapped_customer4_without_working_building']),(0,0,0))
            rows[2][1]='100\t99\t4\tDISTRICT_WONDER\ttrue\t1'
            r=summarize(self.rows(folder,rows))['TAILORS']
            self.assertEqual((r['base_customer_any'],r['mapped_customer4_completed'],
                              r['mapped_customer4_without_working_building']),(1,1,1))

    def test_new_host_state_distinguishes_unfinished_and_completed_pillaged_customers(self):
        with tempfile.TemporaryDirectory()as folder:
            rows=[['QUARTER','BAKERS\t1\t42\t100\ttrue\tfalse\tfalse\t0\t0\t0'],
                  ['MATERIAL','100\t101\tBASE\tRESOURCE_TEST\ttrue'],
                  ['CUSTOMER','100\t99\t2\tDISTRICT_CITY_CENTER\tfalse\t2'],
                  ['CUSTOMER_HOST','100\t99\tDISTRICT_CITY_CENTER\tfalse\tfalse']]
            r=summarize(self.rows(folder,rows))['BAKERS']
            self.assertEqual((r['customer_any_footprint'],r['customer_any_completed'],
                              r['customer_completion_unknown'],r['base_customer2']),(1,0,0,0))
            rows[3][1]='100\t99\tDISTRICT_CITY_CENTER\ttrue\ttrue'
            r=summarize(self.rows(folder,rows))['BAKERS']
            self.assertEqual((r['base_customer_any'],r['base_customer2'],
                              r['base_improved_customer2_working']),(1,1,0))
            self.assertEqual(r['mapped_customer2_completed_without_working_building'],1)

    def test_legacy_false_readiness_and_sales_only_completion_remain_unknown(self):
        with tempfile.TemporaryDirectory()as folder:
            rows=[['QUARTER','BAKERS\t1\t42\t100\ttrue\tfalse\tfalse\t0\t0\t0'],
                  ['MATERIAL','100\t101\tBASE\tRESOURCE_TEST\ttrue'],
                  ['SALES','100\t99\tDISTRICT_CITY_CENTER'],
                  ['CUSTOMER','100\t98\t3\tDISTRICT_CAMPUS\tfalse\t0']]
            r=summarize(self.rows(folder,rows))['BAKERS']
            self.assertEqual((r['base_customer_any'],r['base_customer_any_footprint'],
                              r['customer_completion_unknown']),(0,1,1))
            rows.append(['CUSTOMER_HOST','100\t99\tDISTRICT_CITY_CENTER\ttrue\tfalse'])
            r=summarize(self.rows(folder,rows))['BAKERS']
            self.assertEqual((r['base_customer_any'],r['customer_completion_unknown']),(1,1))

    def test_cohort_filter_uses_player_city_and_plot_not_city_id_alone(self):
        with tempfile.TemporaryDirectory()as folder:
            rows=[]
            for pid,plot in[(1,100),(2,200)]:
                rows += [['QUARTER',f'BAKERS\t{pid}\t42\t{plot}\ttrue\tfalse\tfalse\t0\t0\t0'],
                         ['MATERIAL',f'{plot}\t{plot+1}\tBASE\tRESOURCE_TEST\ttrue'],
                         ['SERVICE_BUILDING',f'{pid}\t42\tBUILDING_CSC_BAKERS_STAGE_2_SERVICE\tfalse']]
            p=self.rows(folder,rows)
            self.assertEqual(summarize(p)['BAKERS']['service2_buildings'],2)
            r=summarize(p,quarter_filter=lambda q:(q['player'],q['city'],q['plot'])==(2,42,200))['BAKERS']
            self.assertEqual((r['complete'],r['base_improved'],r['service2_buildings']),(1,1,1))

    def test_census_emits_actual_host_completion_separately_from_legacy_readiness(self):
        try:
            from lupa.lua51 import LuaRuntime
        except ImportError:
            self.skipTest('Lupa required for the diagnostic census writer fixture')
        vm=LuaRuntime()
        vm.execute('''
output={};print=function(...)local r={...};for i,v in ipairs(r)do r[i]=tostring(v)end;output[#output+1]=table.concat(r,'\t')end
local function info(rows)local t={};for _,r in ipairs(rows)do if r.Index then t[r.Index]=r end;if r.DistrictType then t[r.DistrictType]=r end;if r.BuildingType then t[r.BuildingType]=r end end;return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})end
Game={GetCurrentGameTurn=function()return 200 end};CSC_ENDPOINT_EXPECTED_TURN=200;CSC_ENDPOINT_PLAYERS={1}
GameInfo={Districts=info({{Index=0,DistrictType='DISTRICT_CITY_CENTER'},{Index=36,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'},{Index=37,DistrictType='DISTRICT_CSC_TAILORS_QUARTER'}}),Buildings=info({{Index=3,BuildingType='BUILDING_GRANARY'}}),Yields={YIELD_PRODUCTION={Index=0}},Resources={}}
for _,name in ipairs({'DistrictReplaces','BuildingReplaces','CSC_QuarterFlowBuildings','CSC_Stage3CustomerTransactions','CSC_QuarterWonderSales','Improvement_ValidResources'})do GameInfo[name]=info({})end
GameInfo.CSC_QuarterCustomerBuildings=info({{QuarterKey='BAKERS',ProducerStage=2,DistrictType='DISTRICT_CITY_CENTER',BuildingType='BUILDING_GRANARY'}})
CSC_Adjacency={HasTag=function(tag,kind)return tag=='CLASS_CSC_BAKERS_SALES'and kind=='DISTRICT_CITY_CENTER'end}
local near={GetOwner=function()return 1 end,GetIndex=function()return 99 end,GetResourceType=function()return -1 end,GetDistrictType=function()return 0 end,GetX=function()return 0 end,GetY=function()return 1 end}
local plot={GetIndex=function()return 100 end,GetX=function()return 1 end,GetY=function()return 1 end,IsRiver=function()return false end}
local quarter={GetType=function()return 36 end,GetX=function()return 1 end,GetY=function()return 1 end,IsComplete=function()return true end,IsPillaged=function()return false end}
local host={GetType=function()return 0 end,GetX=function()return 0 end,GetY=function()return 1 end,IsComplete=function()return true end,IsPillaged=function()return true end}
local districts={GetNumDistricts=function()return 2 end,GetDistrictByIndex=function(_,i)return i==0 and quarter or host end}
local buildings={HasBuilding=function()return false end}
local city={GetID=function()return 42 end,GetOwner=function()return 1 end,GetPopulation=function()return 10 end,GetYield=function()return 15 end,GetGrowth=function()return{GetFoodSurplus=function()return 3 end}end,GetProperty=function()return 0 end,GetBuildings=function()return buildings end,GetDistricts=function()return districts end}
local cities={Members=function()local i=0;return function()i=i+1;if i==1 then return i,city end end end}
Players={[1]={IsAlive=function()return true end,GetTreasury=function()return{GetGoldBalance=function()return 0 end,GetGoldYield=function()return 1 end,GetTotalMaintenance=function()return 0 end}end,GetCities=function()return cities end}}
Map={GetPlot=function()return plot end,GetAdjacentPlots=function()return{near}end};Cities={GetPlotPurchaseCity=function()return city end}
''')
        vm.execute(Path(__file__).with_name('full_game_census.lua').read_text(encoding='utf-8'))
        text=vm.eval("table.concat(output,'\\n')")
        self.assertIn('CSC_ENDPOINT_CUSTOMER_HOST\t100\t99\tDISTRICT_CITY_CENTER\ttrue\ttrue',text)
        self.assertIn('CSC_ENDPOINT_CUSTOMER\t100\t99\t2\tDISTRICT_CITY_CENTER\tfalse\t0',text)


if __name__=='__main__':unittest.main()
