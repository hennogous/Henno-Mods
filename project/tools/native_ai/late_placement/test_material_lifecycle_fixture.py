"""Compile every diagnostic command before a real saved-world probe uses it."""
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
from lupa.lua51 import LuaRuntime
from material_lifecycle_fixture import run


class LifecycleCommands(unittest.TestCase):
    def test_generated_lua_compiles_and_uses_controller_for_all_access(self):
        vm=LuaRuntime();compile_lua=vm.eval('function(code)assert(loadstring(code))end')
        vm.execute('''
local function info(rows)return setmetatable({},{__call=function()local i=0;return function()i=i+1;return rows[i]end end})end
Game={GetCurrentGameTurn=function()return 250 end};AutoplayManager={IsActive=function()return false end}
Players={[0]={GetCities=function()return{FindID=function()return{}end}end}}
GameInfo={BuildingModifiers=info({}),ImprovementModifiers=info({{ModifierID='INPUT_ROOT'}}),
 ModifierArguments=info({{ModifierId='LEAF',Name='BuildingType',Value='BUILDING_CSC_BAKERS_WIND_MILL'},
 {ModifierId='INPUT_ROOT',Name='ModifierId',Value='LEAF'}})}
GameEffects={GetModifiers=function()return{}end}
print=function()end
''')
        class Controller:
            def cmd(self,code,context,label):
                compile_lua(code)
                if label.startswith('lifecycle-effects-'):
                    vm.execute(code)
                    return 'CSC_LIFECYCLE_EFFECTS=[]'
                if label.startswith('lifecycle-world-'):return 'CSC_LIFECYCLE_WORLD={}\nCSC_LIFECYCLE_LIVE_CITY={}'
                if label.startswith('lifecycle-yields-'):return 'CSC_LIFECYCLE_YIELDS={}'
                return 'CSC_LIFECYCLE_MUTATION_OK'
        config=dict(diagnosticOnly=True,player=0,turn=250,city=1,
                    quarters=dict(BAKERS=2,TAILORS=3),materials=dict(farm=4,maple=5,bamboo=6))
        with tempfile.TemporaryDirectory()as tmp,patch('material_lifecycle_fixture.time.sleep'):
            result=run(Controller(),Path(tmp)/'probe',config)
        self.assertTrue(result['verified'])
        self.assertEqual(len(result['measurements']),30)


if __name__=='__main__':unittest.main()
