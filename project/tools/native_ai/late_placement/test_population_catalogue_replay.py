"""Compact console proof still compares every population bit and both mirrors."""
import unittest
from lupa.lua51 import LuaRuntime
from population_catalogue_replay import survey


class PopulationReplayProof(unittest.TestCase):
    def run_proof(self,mutation):
        vm=LuaRuntime(unpack_returned_tuples=True)
        output=[]
        vm.globals().print=lambda line:output.append(str(line))
        vm.execute('''
VALUE=0
local function get(_,key)
 if key=='AMOUNT'then return 2 end
 if key=='AMOUNT_BIT_65536'then return VALUE end
 return 0
end
local city={GetID=function()return 7 end,GetX=function()return 0 end,GetY=function()return 0 end,GetProperty=get}
local player={GetID=function()return 3 end,GetCities=function()return{Members=function()
 local i=0;return function()i=i+1;if i==1 then return 1,city end end end}end}
PlayerManager={GetAlive=function()return{player}end}
Game={GetCurrentGameTurn=function()return 250 end}
Map={GetPlot=function()return{GetProperty=get}end}
GameInfo={CSC_BuildingTransactionYields=function()
 local i=0;return function()i=i+1;if i==1 then return{AmountProperty='AMOUNT'}end end
end,CSC_Stage3CustomerTransactions=function()return function()end end}
''')
        vm.execute('function CSC_RefreshCustomerPopulationReturns()VALUE='+str(mutation)+' end')
        reference='function CSC_RefreshCustomerPopulationReturns()VALUE=0 end\nif GameEvents and GameEvents.PlayerTurnStarted then end'
        code=survey(reference)
        return vm.eval('function(code)local ok,e=pcall(assert(loadstring(code)));return ok,tostring(e)end')(code),output

    def test_success_retains_exact_reading_count_with_small_console_proof(self):
        (ok,_),output=self.run_proof(0)
        self.assertTrue(ok)
        self.assertTrue(any('"readings":42'in line and '"verified":true'in line for line in output))
        self.assertTrue(any('"AMOUNT":[2,2]'in line for line in output))
        self.assertLess(sum(map(len,output)),500)

    def test_unprinted_zero_bit_change_still_fails_full_parity(self):
        (ok,error),output=self.run_proof(1)
        self.assertFalse(ok)
        self.assertIn('Population migration changes gameplay properties',error)
        self.assertTrue(any('"verified":false'in line for line in output))
        self.assertTrue(any('CSC_POPULATION_DIFFERENCE='in line and 'AMOUNT_BIT_65536'in line for line in output))


if __name__=='__main__':unittest.main()
