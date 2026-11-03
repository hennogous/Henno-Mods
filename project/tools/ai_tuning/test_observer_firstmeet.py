import importlib.util,sys,unittest
from pathlib import Path
from unittest.mock import patch
from lupa.lua51 import LuaRuntime
ROOT=Path(__file__).resolve().parents[3]
source=(ROOT/'project/tools/ai_baseline/full_game_controller/first_meet_session_dismissal.lua').read_text()
class Guards(unittest.TestCase):
 def run_guard(self,setup='',**replace):
  values=dict(STATEMENT='FIRST_MEET_NEAR_RECIPIENT',FROM=1,CORE_TURN=165,TARGET_TURN=170,CORE_ACTIVE='true',CORE_LOCAL=-1,CORE_HUMAN='false');values.update(replace);code=source
  for k,v in values.items():code=code.replace('__'+k+'__',str(v))
  l=LuaRuntime();l.globals().print=lambda *a:None
  l.execute("""closed=0;id=1;from=1;to=0;ui=165;localPlayer=-1;human=false;exit=true
Game={GetCurrentGameTurn=function()return ui end,GetLocalPlayer=function()return localPlayer end}
Players={[0]={IsHuman=function()return human end}}
ContextPtr={IsHidden=function()return true end}
GameInfo={DiplomacySelections=function()local i=0;local rows={{Type='FIRST_MEET_NEAR_RECIPIENT',Key='CHOICE_POSITIVE'},{Type='FIRST_MEET_NEAR_RECIPIENT',Key='CHOICE_EXIT'}};return function()i=i+1;if i==2 and not exit then return nil end;return rows[i]end end}
DiplomacyManager={FindOpenSessionID=function()return id end,IsSessionIDOpen=function()return closed==0 end,GetSessionInfo=function()return{FromPlayer=from,ToPlayer=to}end,CloseSession=function(v)assert(v==1);closed=closed+1 end}
""");l.execute(setup);l.execute(code);return l.globals().closed
 def test_declines_without_positive_or_order_api(self):self.assertEqual(self.run_guard(),1)
 def test_requires_native_exit_definition(self):self.assertEqual(self.run_guard('exit=false'),0)
 def test_unrelated_statement_rejected(self):self.assertEqual(self.run_guard(STATEMENT='DEMAND_TRIBUTE'),0)
 def test_wrong_native_participants_rejected(self):
  for setup in('from=2','to=3'):
   self.assertEqual(self.run_guard(setup),0)
 def test_human_or_ui_clock_mismatch_rejected(self):
  for setup in('human=true','localPlayer=0','ui=164-1'):
   self.assertEqual(self.run_guard(setup),0)
 def test_wrong_core_phase_rejected(self):self.assertEqual(self.run_guard(CORE_ACTIVE='false'),0)
 def test_closed_or_absent_session_rejected(self):self.assertEqual(self.run_guard('id=-1'),0)
class CLI(unittest.TestCase):
 def test_same_remaining_operation_and_endpoint_forwarded(self):
  sys.path.insert(0,str(ROOT/'project/tools/ai_tuning'));import resume_profile_live as m
  args=['resume','worker','--parent','C:/parent','--output','C:/output','--turn','165','--endpoint','200','--active-target','170','--active-source-review','C:/review.json','--controller-adapter','C:/adapter','--campaign','C:/campaign'];seen=[]
  with patch.object(sys,'argv',args),patch.object(m,'worker',lambda a:seen.append(a)):m.main()
  a=seen[0];command=m.argv(a,'worker');self.assertEqual(command[command.index('--endpoint')+1],'200');self.assertEqual(a.active_target,170)
if __name__=='__main__':unittest.main()
