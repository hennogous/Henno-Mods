"""Compile and isolate the real quote modules under Civ's missing-setfenv case."""
import unittest
from lupa.lua51 import LuaRuntime
from customer_transaction_replay import query


class CustomerTransactionReplay(unittest.TestCase):
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
