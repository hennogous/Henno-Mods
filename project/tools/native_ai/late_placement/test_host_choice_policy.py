"""Verify a read-only, generation-bounded CE trace prefix and scoped filtering."""
import unittest
from lupa.lua51 import LuaRuntime
from host_choice_policy import candidate_scope,stage


class HostReader(unittest.TestCase):
    def fixture(self,change=''):
        vm=LuaRuntime()
        scope=[dict(player=4,city=655369,district=37,plot=2678)]
        vm.execute('''
output={};print=function(...)local parts={...};for i,v in ipairs(parts)do parts[i]=tostring(v)end
 output[#output+1]=table.concat(parts,'\t')end
Game={GetCurrentGameTurn=function()return 207 end}
GameEvents={OnGameTurnStarted={Add=function(fn)turnCallback=fn end}}
statusCalls=0;pageCalls=0;finalGeneration=5;stale=false;nextOffset=3
function CE_AIDistrictScoresStatus()
 statusCalls=statusCalls+1
 return '{"ready":1,"enabled":1,"faults":0,"generation":'..
  (statusCalls==1 and 5 or finalGeneration)..',"version":7,"trace_count":3}'
end
function CE_AIDistrictScoresTraceRead(offset,limit,generation)
 pageCalls=pageCalls+1;assert(offset==0 and limit==3 and generation==5)
 return '{"generation":5,"version":7,"total":4,"offset":0,"next":'..nextOffset..
 ',"stale":'..tostring(stale)..',"records":['..
 '{"k":"cache","player":4,"city":655369,"district":37,"plot":2678,"result":120},'..
 '{"k":"cache","player":4,"city":655369,"district":36,"plot":2677,"result":121},'..
 '{"k":"best","player":4,"city":655369,"district":10,"plot":2677,"result":122}]}'
end
'''+change)
        vm.execute(stage(b'',scope).decode('utf-8'))
        return vm

    def test_append_safe_prefix_keeps_exact_pair_and_city_winner_only(self):
        vm=self.fixture();vm.globals().CSC_HOST_DIAG_Arm()
        lines=list(vm.globals().output.values())
        native=[line for line in lines if line.startswith('CSC_HOST_NATIVE\t')]
        self.assertEqual(len(native),2)
        self.assertIn('"district":37',native[0])
        self.assertIn('"k":"best"',native[1])
        self.assertTrue(lines[-1].startswith('CSC_HOST_PREFIX_END\t207\t5\t7\t3'))
        self.assertEqual(vm.globals().pageCalls,1)

    def test_stale_short_page_or_generation_reset_is_rejected(self):
        for change in ('stale=true','nextOffset=2','finalGeneration=6'):
            with self.subTest(change=change):
                vm=self.fixture(change)
                with self.assertRaises(Exception):vm.globals().CSC_HOST_DIAG_Arm()

    def test_multiple_pages_preserve_stable_native_indices(self):
        vm=self.fixture()
        vm.execute('''
function CE_AIDistrictScoresStatus()
 return '{"ready":1,"enabled":1,"faults":0,"generation":5,"version":7,"trace_count":65}'
end
function CE_AIDistrictScoresTraceRead(offset,limit,generation)
 assert(generation==5 and ((offset==0 and limit==64)or(offset==64 and limit==1)))
 local records={}
 for index=offset,offset+limit-1 do
  records[#records+1]='{"k":"cache","player":4,"city":655369,"district":37,"plot":2678,"result":'..index..'}'
 end
 return '{"generation":5,"version":7,"total":66,"offset":'..offset..',"next":'..
  (offset+limit)..',"stale":false,"records":['..table.concat(records,',')..']}'
end
''')
        vm.globals().CSC_HOST_DIAG_Arm()
        native=[line for line in vm.globals().output.values() if line.startswith('CSC_HOST_NATIVE\t')]
        self.assertEqual(len(native),65)
        self.assertTrue(native[-1].startswith('CSC_HOST_NATIVE\t207\t5\t64\t'))

    def test_only_positive_changed_pairs_nominate_scope(self):
        def row(plot,delta):return ['4','655369','Makwa','TAILORS','37',str(plot),str(delta)]
        old={'sites':[row(1,-32768),row(2,6144),row(3,-65536)]}
        new={'sites':[row(1,6144),row(2,6144),row(3,-32768)]}
        self.assertEqual(candidate_scope(old,new),[dict(player=4,city=655369,name='Makwa',
            profile='TAILORS',district=37,plot=1,previousDelta=-32768,expandedDelta=6144)])

    def test_unarmed_startup_is_logged_without_reading_native_state(self):
        vm=self.fixture();vm.globals().turnCallback()
        self.assertEqual(vm.globals().statusCalls,0)
        self.assertIn('CSC_HOST_DIAG_NOT_ARMED\t207',list(vm.globals().output.values()))
        vm.globals().CSC_HOST_DIAG_Arm()
        with self.assertRaisesRegex(Exception,'already armed'):vm.globals().CSC_HOST_DIAG_Arm()

    def test_early_player_scope_keeps_all_published_quarter_rows_and_winner(self):
        vm=self.fixture()
        vm.execute('''Game.GetCurrentGameTurn=function()return 23 end
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return {
 {district={Index=36}},{district={Index=37}}}end}''')
        vm.execute(stage(b'',[],start=22,end=24,players=[4]).decode('utf-8'))
        vm.globals().CSC_HOST_DIAG_Arm()
        native=[line for line in vm.globals().output.values() if line.startswith('CSC_HOST_NATIVE\t')]
        self.assertEqual(len(native),3)
        with self.assertRaises(AssertionError):stage(b'',[],start=22,end=24,players=[0])

    def test_extended_scout_does_not_relax_ordinary_window_guard(self):
        with self.assertRaises(AssertionError):stage(b'',[],start=22,end=40,players=[1])
        self.assertIn(b'if turn<22 or turn>40',stage(b'',[],start=22,end=40,players=[1],window_limit=18))
        with self.assertRaises(AssertionError):stage(b'',[],start=22,end=41,players=[1],window_limit=18)
        with self.assertRaises(AssertionError):stage(b'',[],start=200,end=218,players=[1],window_limit=18)


if __name__=='__main__':unittest.main()
