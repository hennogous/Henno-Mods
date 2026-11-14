"""Observation integrity: a partial census must never become comparison data."""
from pathlib import Path
import tempfile
import unittest
from lupa.lua51 import LuaRuntime
from full_game_observation import archive_censuses,play,finish,observe_inactive_storekeeper,observe_purchase_contexts,HERE
from driver import lua


class FullGameObservation(unittest.TestCase):
    def test_inactive_read_defers_lagging_clock_and_never_relabels_it(self):
        class Controller:
            def __init__(self,replies):self.replies=iter(replies);self.codes=[]
            def cmd(self,code,*args):self.codes.append(code);return next(self.replies)
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);(root/'storekeeper_runtime.lua').write_text('snapshot()',encoding='utf-8')
            controller=Controller(['CSC_FULL_RUN_UI_CLOCK_DEFERRED\t54'])
            self.assertFalse(observe_inactive_storekeeper(controller,root,55))
            self.assertTrue((root/'deferred-ui-boundary-55.json').exists())
            self.assertEqual(len(controller.codes),1)
            self.assertIn('if Game.GetCurrentGameTurn()==55 then',controller.codes[0])
            self.assertTrue(observe_inactive_storekeeper(
                Controller(['CSC_STOREKEEPER_END\t55\t0']),root,55))
            for reply in ('CSC_FULL_RUN_UI_CLOCK_DEFERRED\t56','CSC_STOREKEEPER_END\t54\t0'):
                with self.assertRaises(RuntimeError):
                    observe_inactive_storekeeper(Controller([reply]),root,55)

    def test_200_endpoint_requires_exactly_its_eight_milestones(self):
        with tempfile.TemporaryDirectory()as d:
            root=Path(d)
            log=''.join('CSC_FULL_RUN_CENSUS_BEGIN\t'+str(t)+'\nCSC_ENDPOINT_END\t'+str(t)+'\t0\n'
                for t in range(25,201,25))
            (root/'Lua.log').write_text(log,encoding='utf-8')
            finish(root,200)
            with self.assertRaises(RuntimeError):finish(root,250)

    def test_complete_rows_preserve_baseline_format(self):
        with tempfile.TemporaryDirectory()as d:
            rows=archive_censuses('''CSC_FULL_RUN_CENSUS_BEGIN\t200
CSC_ENDPOINT_PLAYER\t1\ttrue
CSC_ENDPOINT_CITY\t1\t42\t7\t20\t3
CSC_ENDPOINT_END\t200\t2
''',Path(d))
            self.assertEqual(rows[200]['rows'],[['PLAYER','1\ttrue'],['CITY','1\t42\t7\t20\t3'],['END','200\t2']])

    def test_missing_rows_or_footer_are_rejected(self):
        for log in('CSC_FULL_RUN_CENSUS_BEGIN\t200\nCSC_ENDPOINT_END\t200\t1',
                'CSC_FULL_RUN_CENSUS_BEGIN\t200\nCSC_ENDPOINT_PLAYER\t1\ttrue'):
            with tempfile.TemporaryDirectory()as d:
                with self.assertRaises(RuntimeError):archive_censuses(log,Path(d))

    def test_duplicate_samples_are_rejected(self):
        log='CSC_FULL_RUN_CENSUS_BEGIN\t200\nCSC_ENDPOINT_END\t200\t0\n'
        with tempfile.TemporaryDirectory()as d:
            with self.assertRaises(RuntimeError):archive_censuses(log+log,Path(d))

    def test_actual_readers_compile_for_game_lua(self):
        vm=LuaRuntime();compile=vm.eval('function(s)assert(loadstring(s))end')
        compile((HERE/'full_game_census.lua').read_text(encoding='utf-8'))
        compile((HERE/'district_adjacency_watch.lua').read_text(encoding='utf-8'))
        compile((HERE/'full_game_preflight.lua').read_text(encoding='utf-8').replace('__SCOPE__',lua(dict(players=[1,2,3,4,5]))))

    def test_missing_native_reader_cannot_disappear_from_preflight(self):
        code=(HERE/'full_game_preflight.lua').read_text(encoding='utf-8').split('local y=')[0]
        code=code.replace('__SCOPE__',lua(dict(players=[1,2,3,4,5])))
        names=('CE_AIDistrictScoresStatus','CE_AIBuilderProtectionStatus',
            'CE_AIBuilderHarvestProtectionStatus','CE_AISupplierWonderProtectionStatus',
            'CE_AIBuildingNominationStatus','CE_AIDistrictRepairStatus',
            'CE_AISupplierExclusionStatus','CE_AIDistrictPurchaseCompletionStatus','CE_AIDistrictDeclineStatus',
            'CE_AIEconomyStatus','CE_AIDistrictScoresFinalEntry','CE_AIYieldStreamValue',
            'CE_AIYieldFixedValue','CE_AIAmenityStreamValue','CE_AIDistrictScoresManagedType','CE_AIDistrictScoresManagedReceipt',
            'ExposedMembers.CSC_Adjacency.GetEconomyCityNumber','ExposedMembers.CSC_Adjacency.GetEconomyResearchNumbers',
            'ExposedMembers.CSC_Adjacency.GetEconomyPlotFacts','ExposedMembers.CSC_Adjacency.GetDistrictCapacity')
        for absent in (None,)+names:
            vm=LuaRuntime();vm.execute('''print=function()end
Game={GetCurrentGameTurn=function()return 1 end}
AutoplayManager={IsActive=function()return false end}
GameInfo={};CSC_AI_QuarterPlacement={};CSC_AI_QuarterSiteForecasts=function()end;CSC_AI_DistrictBridge={}
CSC_AI_EconomyModel={};CSC_AI_EconomyFacts={};CSC_AI_EconomyAdapters={}
ExposedMembers={CSC_Adjacency={}}
''')
            for name in names:vm.execute(name+'=function()return \'{"ready":1,"faults":0}\'end')
            vm.execute('CE_AIEconomyStatus=function()return \'{"pricingReady":1,"finalReady":1}\'end')
            if absent:
                vm.execute(absent+'=nil')
                with self.assertRaisesRegex(Exception,'Missing .* consumer'):vm.execute(code)
            else:
                vm.execute('CE_AISupplierExclusionStatus=function()return \'{"ready":1,"capacity":256}\'end')
                vm.execute(code)

    def test_purchase_context_deduplicates_targets_and_labels_its_later_clock(self):
        class Controller:
            def __init__(self):self.calls=[]
            def cmd(self,code,*args):
                self.calls.append(code)
                return 'CSC_PURCHASE_CONTEXT_END\t20\t1'
        with tempfile.TemporaryDirectory()as d:
            c=Controller();out=Path(d)
            observe_purchase_contexts(c,out,dict(records=[]),20)
            self.assertEqual(c.calls,[])
            batch=dict(records=[dict(player=1,plot=44),dict(player=1,plot=44),
                dict(candidates=[dict(player=1,cached=dict(plot=44))])])
            observe_purchase_contexts(c,out,batch,20)
            self.assertEqual(len(c.calls),1)
            self.assertIn('laterBoundaryFacts',c.calls[0])
            self.assertIn('local targets={{1,44}}',c.calls[0])
            self.assertTrue((out/'purchase-context-20.txt').is_file())

    def test_finite_windows_preserve_intermediate_observation(self):
        class Controller:
            def __init__(self):self.boundaries=[];self.samples=[]
            def play(self,turn):self.boundaries.append(turn)
            def cmd(self,code,context,label):
                if label=='drain-final-placement-journal':return 'CSC_QUARTER_WATCH_DRAINED'
                turn=int(label.rsplit('-',1)[1]);self.samples.append(turn)
                return 'CSC_STOREKEEPER_END\t'+str(turn)+'\t0'
        with tempfile.TemporaryDirectory()as d:
            root=Path(d);(root/'Logs').mkdir()
            (root/'Logs/Lua.log').write_text('CSC_STOREKEEPER_END\t11\t0\n',encoding='utf-8')
            (root/'storekeeper_runtime.lua').write_bytes((HERE/'storekeeper_runtime.lua').read_bytes())
            controller=Controller();play(controller,root,root,start=1,endpoint=15)
            self.assertEqual(controller.boundaries,[6,11,15])
            self.assertEqual(controller.samples,[6])
            self.assertTrue(controller.allow_one_more_turn)


if __name__=='__main__':unittest.main()
