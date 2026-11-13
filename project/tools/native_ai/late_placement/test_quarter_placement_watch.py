"""Verify observational attribution without making a game decision or score write."""
import json
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from driver import lua
from placement_watch_results import parse

SOURCE=Path(__file__).with_name('quarter_placement_watch.lua').read_text(encoding='utf-8')


class PlacementWatch(unittest.TestCase):
    def setUp(self):
        self.vm=LuaRuntime()
        self.vm.execute('''
rows={};print=function(...)local t={...};for i,v in ipairs(t)do t[i]=tostring(v)end;rows[#rows+1]=table.concat(t,'\t')end
turn=150;complete=false;trace='{"records":[]}'
local function event()return {Add=function(f)return f end}end
Events={DistrictAddedToMap=event(),DistrictBuildProgressChanged=event()}
Events.DistrictAddedToMap.Add=function(f)added=f end
Events.DistrictBuildProgressChanged.Add=function(f)progress=f end
GameEvents={OnGameTurnStarted={Add=function(f)poll=f end}}
Game={GetCurrentGameTurn=function()return turn end}
district={IsComplete=function()return complete end}
plot={GetIndex=function()return 1062 end,IsRiver=function()return false end,IsHills=function()return false end}
Map={GetPlot=function()return plot end,GetAdjacentPlots=function()return {}end}
local empty={Members=function()return function()end end}
city={GetDistricts=function()return {GetNumDistricts=function()return 0 end}end}
Players={[1]={GetCities=function()return empty end,GetDistricts=function()return {FindID=function()return district end}end}}
CityManager={GetCity=function()return city end}
PlayerManager={GetAlive=function()return {}end}
GameInfo={Resources={},Improvements={}}
CSC_AI_DistrictBridge={Publish=function(...)args={...};return accepted,'receipt'end}
accepted=true
CSC_Adjacency={}
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return {{district={Index=37,DistrictType='TAILORS'}}}end,
ReadSuppliers=function()return {base={{working=true}},specialty={}}end}
CSC_AI_QuarterAdjacencyValue=function()return {production=1,gold=0,total=1,current={production=1,gold=0},details={}}end
CE_AIDistrictScoresStatus=function()return '{"generation":3,"trace_count":1}'end
CE_AIDistrictScoresTraceRead=function()return trace end
''')
        self.vm.execute(SOURCE)

    def output(self):return '\n'.join(self.vm.globals().rows.values())

    def publish(self,version=4,bid=100):
        return self.vm.execute('return CSC_AI_DistrictBridge.Publish('+str(version)+',74,46,38,{1},'
            +lua([dict(player=1,city=327684,district=37,plot=1062,finalQ8=bid,adjacency=1)])+',"extra")')

    def test_publish_preserves_arguments_and_result(self):
        self.assertEqual(self.publish(),(True,'receipt'))
        self.assertEqual(self.vm.globals().args[7],'extra')
        self.vm.execute('accepted=false')
        self.assertEqual(self.publish(5,999),(False,'receipt'))
        self.vm.execute('added(1,42,327684,26,14,37)')
        self.assertIn('bidQ8=100',self.output())
        self.assertNotIn('bidQ8=999',self.output())

    def test_foundation_and_completion_are_each_recorded_once(self):
        self.publish()
        self.vm.execute('added(1,42,327684,26,14,37);added(1,42,327684,26,14,37);complete=true;progress(1,42,327684,26,14,37);progress(1,42,327684,26,14,37)')
        self.assertEqual(self.output().count('event=foundation'),1)
        self.assertEqual(self.output().count('event=completion'),1)
        self.assertIn('millForecastTotal=1',self.output())
        self.assertNotIn('FAULT',self.output())

    def test_later_write_is_not_attributed_to_an_earlier_selection(self):
        self.publish()
        def row(kind,result):
            return dict(k=kind,version=4,generation=3,player=1,city=327684,district=37,
                        plot=1062,base=999,result=result,reason=0,eligible=1)
        self.vm.globals().trace=json.dumps(dict(records=[row('best',999),row('final',100),row('best',100)]),separators=(',',':'))
        self.publish(5)
        best=[line for line in self.output().splitlines()if line.startswith('CSC_QUARTER_WATCH_BEST')]
        self.assertEqual(len(best),2)
        self.assertNotIn('lastWriteQ8',best[0])
        self.assertIn('lastWriteQ8=100',best[1])
        self.assertIn('result=999',best[0])

    def test_instant_completion_and_rebuilt_district_have_separate_lifecycles(self):
        self.vm.execute('complete=true;added(1,42,327684,26,14,37);progress(1,42,327684,26,14,37)')
        self.assertEqual(self.output().count('event=foundation'),1)
        self.assertEqual(self.output().count('event=completion'),1)
        self.vm.execute('complete=false;added(1,43,327684,26,14,37);complete=true;progress(1,43,327684,26,14,37)')
        self.assertEqual(self.output().count('event=foundation'),2)
        self.assertEqual(self.output().count('event=completion'),2)

    def test_capture_is_not_a_new_foundation_even_if_native_id_changes(self):
        self.vm.execute('complete=true;added(1,42,327684,26,14,37);Players[2]=Players[1];added(2,99,10,26,14,37)')
        self.assertEqual(self.output().count('event=foundation'),1)
        self.assertEqual(self.output().count('event=ownership-change'),1)

    def test_stale_event_is_explicitly_deferred_not_called_a_foundation(self):
        self.vm.execute('Players[1].GetDistricts=function()return {FindID=function()return nil end}end;added(1,42,327684,26,14,37)')
        self.assertIn('CSC_QUARTER_WATCH_DEFERRED',self.output())
        self.assertNotIn('event=foundation',self.output())
        self.assertNotIn('FAULT',self.output())

    def test_observer_failure_does_not_prevent_policy_publication(self):
        self.vm.execute('CE_AIDistrictScoresStatus=function()error("reader unavailable")end')
        self.assertEqual(self.publish(),(True,'receipt'))
        self.assertIn('CSC_QUARTER_WATCH_FAULT',self.output())

    def test_result_distinguishes_loaded_and_first_observed_from_foundations(self):
        self.publish()
        self.vm.execute('added(1,42,327684,26,14,37);complete=true;progress(1,42,327684,26,14,37)')
        result=parse(self.output())
        self.assertEqual(result['summary']['foundation']['below3'],1)
        self.assertEqual(result['summary']['completion']['below3'],1)
        self.assertEqual(result['summary']['loaded']['count'],0)
        with self.assertRaisesRegex(AssertionError,'fault'):parse(self.output()+'\nCSC_QUARTER_WATCH_FAULT\terror=missing')
        partial=parse(self.output()+'\nCSC_QUARTER_WATCH_FAULT\terror=missing',allow_faults=True)
        self.assertFalse(partial['measurementComplete'])
        self.assertEqual(len(partial['faults']),1)


if __name__=='__main__':unittest.main()
