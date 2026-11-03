"""Actual Lua owner-phase diagnostics, no native mutation or extra turn."""
import json,sys,unittest
from pathlib import Path

FIXTURE=r'''
turn=110;active=false;gold=100;queries=0;messages={}
print=function(v)messages[#messages+1]=v end
Game={GetCurrentGameTurn=function()return turn end,GetLocalPlayer=function()return -1 end}
local p={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return false end,IsTurnActive=function()return active end,GetTreasury=function()return {GetGoldBalance=function()return gold end}end}
local c={GetID=function()return 10 end,GetOwner=function()return 1 end,GetX=function()return 0 end,GetY=function()return 0 end,GetGold=function()return {GetPlotPurchaseCost=function()return 60 end}end}
p.GetCities=function()return {Members=function()local done=false;return function()if not done then done=true;return 10,c end end end}end
Players={[1]=p}
CityCommandTypes={PARAM_PLOT_PURCHASE=1,PARAM_X=2,PARAM_Y=3,PURCHASE=4};CityCommandResults={PLOTS=5,FAILURE_REASONS=6}
CityManager={CanStartCommand=function(city,command,first,args,results)queries=queries+1;if first==true then return true,{[5]={42}}end;return active,{[6]=active and nil or {'owner inactive'}}end,RequestCommand=function()error('forbidden mutation')end}
Map={GetPlotByIndex=function(i)return {GetOwner=function()return -1 end,GetX=function()return 1 end,GetY=function()return 0 end,IsWater=function()return false end,IsImpassable=function()return false end}end,GetPlotDistance=function()return 1 end}
function event()local e={listeners={}};e.Add=function(fn)e.listeners[fn]=true end;e.Remove=function(fn)e.listeners[fn]=nil end;e.Fire=function(pid)for fn in pairs(e.listeners)do fn(pid)end end;return e end
Events={PlayerTurnActivated=event(),PlayerTurnDeactivated=event()}
CSC_SERVICE_NATIVE={Json=function(v)return 'mock-json' end}
CSC_PURCHASE_DIAGNOSTIC_LIMITS={first_turn=110,last_turn=111,max_rows=24}
'''
class DiagnosticTests(unittest.TestCase):
 def engine(self):
  from lupa.lua51 import LuaRuntime
  e=LuaRuntime(unpack_returned_tuples=True);e.execute(FIXTURE);e.execute(Path(__file__).with_name('native_purchase_diagnostics.lua').read_text());return e
 def test_current_owner_phase_is_explicit_and_distinct_from_inactive(self):
  e=self.engine();d=e.globals().CSC_PURCHASE_DIAGNOSTICS
  self.assertEqual(len(d.rows),1);self.assertFalse(d.rows[1].ordinary);self.assertFalse(d.rows[1].active)
  e.execute('active=true;Events.PlayerTurnActivated.Fire(1)')
  self.assertTrue(d.rows[2].ordinary);self.assertTrue(d.rows[2].strict);self.assertTrue(d.rows[2].active);self.assertEqual(d.rows[2].price,60)
  self.assertEqual(e.globals().gold,100);self.assertEqual(len(d.errors),0)
 def test_outside_scope_or_cap_adds_no_more_queries(self):
  e=self.engine();n=e.globals().queries
  e.execute('turn=112;Events.PlayerTurnActivated.Fire(1)');self.assertEqual(e.globals().queries,n)
  e.execute('turn=110;CSC_PURCHASE_DIAGNOSTICS.max_rows=1;Events.PlayerTurnActivated.Fire(1)');self.assertEqual(e.globals().queries,n)
 def test_reinstall_replaces_named_callback_without_duplicate_phase_records(self):
  e=self.engine();e.execute(Path(__file__).with_name('native_purchase_diagnostics.lua').read_text());n=len(e.globals().CSC_PURCHASE_DIAGNOSTICS.rows)
  e.execute('Events.PlayerTurnActivated.Fire(1)');self.assertEqual(len(e.globals().CSC_PURCHASE_DIAGNOSTICS.rows),n+1)
 def test_no_affordable_sample_is_missing_evidence_not_approval(self):
  e=self.engine();e.execute('gold=30;Events.PlayerTurnActivated.Fire(1)');row=e.globals().CSC_PURCHASE_DIAGNOSTICS.rows[2]
  self.assertFalse(row.affordable_unowned_land_sample);self.assertIsNone(row.ordinary)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--lua51-path',required=True);p.add_argument('--output',type=Path);a=p.parse_args();sys.path.insert(0,a.lua51_path)
 r=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(DiagnosticTests))
 if a.output:a.output.write_text(json.dumps({'passed':r.wasSuccessful(),'tests':r.testsRun,'native_connections':0},indent=2))
 raise SystemExit(not r.wasSuccessful())
