"""Ensure the control removes only the declared positive placement channel."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from early_host_policy import stage
from liverpool_adjacency_policy import PREPARE,FILTER,without_promotions


class AdjacencyPolicy(unittest.TestCase):
    def test_control_preserves_other_channels_and_deductions(self):
        vm=LuaRuntime();vm.execute('''print=function()end;turn=25;version=0
entries={{player=4,city=131073,district=36,plot=2497,delta=12288},
 {player=4,city=131073,district=36,plot=2423,delta=12288,frontier=true},
 {player=4,city=131073,district=36,plot=2498,delta=-65536},
 {player=4,city=131073,district=37,plot=2571,delta=6144},
 {player=4,city=65536,district=36,plot=2495,delta=12288},
 {player=3,city=131073,district=36,plot=721,delta=6144},
 {player=4,city=131073,district=36,plot=2571,delta=6144,customer=true}}
builderSites={};nominations={};repairs={};exclusions={}
''')
        vm.execute(FILTER.decode())
        self.assertEqual([(r.player,r.city,r.district,r.plot,r.delta)for r in vm.globals().entries.values()],
            [(4,131073,36,2498,-65536),(4,131073,37,2571,6144),
             (4,65536,36,2495,12288),(3,131073,36,721,6144),(4,131073,36,2571,6144)])
        for name in ('builderSites','nominations','repairs','exclusions'):
            self.assertEqual(len(vm.globals()[name]),0)

    def test_staging_compiles_and_has_one_removable_filter(self):
        root=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI'
        scanner=(root/'CSC_AI_AdjacencyScan.lua').read_bytes()
        source=(root/'CSC_AI_BakersGameplay.lua').read_bytes()
        _,publisher=stage(scanner,source,migrate_roles=False)
        control=without_promotions(publisher)
        self.assertEqual(control.replace(FILTER,b''),publisher)
        self.assertLess(control.index(b'for i = #entries, capacity + 1, -1'),control.index(FILTER))
        self.assertLess(control.index(FILTER),control.index(b'local accepted, message = bridge.Publish('))
        for code in (control,PREPARE.encode(),Path(__file__).with_name('liverpool_inspection.lua').read_bytes()):
            LuaRuntime().eval('function(code)return assert(loadstring(code))end')(code.decode('utf-8-sig'))


if __name__=='__main__':unittest.main()
