"""Compile and isolate the real quote modules under Civ's missing-setfenv case."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from lupa.lua51 import LuaRuntime
from customer_transaction_replay import query, policy_packages


class CustomerTransactionReplay(unittest.TestCase):
    def test_scheduling_arm_changes_only_adapter_without_mutating_source_manifest(self):
        with TemporaryDirectory()as temporary:
            adapter='Lua_UI/AI/CSC_AI_EconomyAdapters.lua'
            original={adapter:'old','Data/game.sql':'same'}
            plan=SimpleNamespace(packages=[dict(role='csc',id='csc-id',files=original)])
            with patch('customer_transaction_replay.package_identity',return_value=('csc-id',None)), \
                 patch('customer_transaction_replay.manifest',return_value=dict(original,**{adapter:'new'})):
                rows,changes=policy_packages(plan,Path(temporary))
            self.assertEqual(changes,[adapter]);self.assertEqual(original[adapter],'old')
            self.assertEqual(rows[0]['files'][adapter],'new')
            with patch('customer_transaction_replay.package_identity',return_value=('csc-id',None)), \
                 patch('customer_transaction_replay.manifest',return_value={adapter:'new','Data/game.sql':'changed'}):
                with self.assertRaises(Exception):policy_packages(plan,Path(temporary))

    def test_lexical_modules_leave_active_policy_intact_without_setfenv(self):
        vm=LuaRuntime()
        vm.execute('setfenv=nil;_G=nil;CSC_AI_EconomyFacts={live=true};CSC_AI_EconomyModel={live=true};CSC_AI_EconomyAdapters={live=true}')
        code=query([[5,262147,936,788,'BAKERS',789]])
        vm.eval('function(s)assert(loadstring(s))end')(code)
        prefix=code.split('\nlocal CSC_TRANSACTION_CASES=',1)[0]
        vm.execute(prefix+'''
assert(type(CSC_TRANSACTION_MODULES.CSC_AI_EconomyFacts.ProjectedCustomers)== 'nil')
assert(type(CSC_TRANSACTION_MODULES.CSC_AI_EconomyFacts.New)=='function')
assert(type(CSC_TRANSACTION_MODULES.CSC_AI_EconomyModel.CustomerBuildingForecast)=='function')
assert(CSC_TRANSACTION_MODULES.CSC_AI_EconomyFacts~=activeModules[1])
''')
        self.assertTrue(vm.eval('CSC_AI_EconomyFacts.live and CSC_AI_EconomyModel.live and CSC_AI_EconomyAdapters.live'))


if __name__=='__main__':unittest.main()
