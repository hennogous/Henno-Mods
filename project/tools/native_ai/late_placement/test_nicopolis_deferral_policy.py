"""Bound diagnostic knowledge edits; a Lua fixture proves no native choice."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from nicopolis_deferral_policy import REVEAL, stage


class KnowledgeFixture(unittest.TestCase):
    def vm(self):
        vm=LuaRuntime()
        vm.execute('''changed={};revealed={};print=function()end
Game={GetCurrentGameTurn=function()return 200 end}
Players={[1]={IsAlive=function()return true end,IsHuman=function()return false end}}
CityManager={GetCity=function(pid,cid)assert(pid==1 and cid==524295);return {
 GetName=function()return 'LOC_CITY_NAME_NICOPOLIS' end,GetX=function()return 0 end,GetY=function()return 0 end}end}
Map={GetPlotCount=function()return 6 end,GetPlotByIndex=function(i)return {GetX=function()return i end,GetY=function()return 0 end}end,
 GetPlotDistance=function(x,y,a,b)return a end}
PlayersVisibility={[1]={IsRevealed=function(self,i)return i==0 or revealed[i]==true end,
 IsVisible=function(self,i)return (changed[i] or 0)>0 end,
 ChangeVisibilityCount=function(self,i,n)assert(n==1 or n==-1);changed[i]=(changed[i] or 0)+n;assert(changed[i]>=0);if n==1 then revealed[i]=true end end}}
''')
        return vm

    def test_only_unknown_radius_four_changes(self):
        vm=self.vm();vm.execute(REVEAL)
        self.assertEqual(dict(vm.globals().changed),{1:0,2:0,3:0,4:0})
        self.assertEqual(dict(vm.globals().revealed),{1:True,2:True,3:True,4:True})
        vm.execute(REVEAL) # Knowledge already present causes no extra count.
        self.assertEqual(dict(vm.globals().changed),{1:0,2:0,3:0,4:0})

    def test_wrong_source_rejected_before_knowledge_edit(self):
        vm=self.vm();vm.execute('Game.GetCurrentGameTurn=function()return 201 end')
        with self.assertRaises(Exception):vm.execute(REVEAL)
        self.assertEqual(dict(vm.globals().changed),{})

    def test_observer_preserves_actual_publish_call(self):
        source=(Path('Civ Supply Chains/Lua_UI/AI/CSC_AI_BakersGameplay.lua')).read_bytes()
        modified=stage(source)
        self.assertEqual(modified.count(b'    local accepted, message = bridge.Publish('),1)
        self.vm().execute('assert(loadstring(...))',modified.decode('utf-8'))


if __name__=='__main__':unittest.main()
