"""Fixed endpoint continuation uses shipped button and only remaining budget."""
import ast,tempfile,types,unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime
from . import controller

HERE=Path(__file__).parent
class EndgameTests(unittest.TestCase):
 def lua(self,**overrides):
  params=dict(CORE_ACTIVE=False,CORE_TURN=199,TARGET=200,ENDPOINT=250,REMAINING=1,CORE_LOCAL=0,CORE_HUMAN=True)
  params.update(overrides);code=(HERE/'endgame_playback.lua').read_text()
  for key,value in params.items():code=code.replace('__'+key+'__',str(value).lower())
  e=LuaRuntime(unpack_returned_tuples=True)
  e.execute('''hidden=false;disabled=false;clicks=0;winner=4;kind=1;turn=199;localplayer=0;human=true;buttonhidden=false
Game={GetWinningTeam=function()return winner,kind end,GetCurrentGameTurn=function()return turn end,GetLocalPlayer=function()return localplayer end}
Players={[0]={IsHuman=function()return human end}}
ContextPtr={IsHidden=function()return hidden end};Controls={BackButton={IsHidden=function()return buttonhidden end,IsDisabled=function()return disabled end}}
OnBack=function()clicks=clicks+1;hidden=true end
''')
  return e,code
 def test_actual_lua_shipped_one_more_turn_called_once(self):
  e,code=self.lua();e.execute(code);e.execute(code);self.assertEqual(e.globals().clicks,1)
 def test_actual_lua_guards(self):
  for settings in ({'CORE_ACTIVE':True},{'TARGET':201},{'ENDPOINT':199},{'CORE_HUMAN':False},{'CORE_LOCAL':-1}):
   e,code=self.lua(**settings);e.execute(code);self.assertEqual(e.globals().clicks,0)
  for setup in('hidden=true','winner=-1','kind=-1','turn=197','localplayer=1','human=false','disabled=true','buttonhidden=true'):
   e,code=self.lua();e.execute(setup);e.execute(code);self.assertEqual(e.globals().clicks,0,setup)
 def fake(self,after=None,raw='CSC_ENDGAME_CONTINUE_REQUESTED true',enabled=True):
  class Runner:
   allow_one_more_turn=enabled;study_endpoint=250
   def __init__(self):
    self.root=Path('.');self.state={'EndGameMenu':1};self.calls=[];self.diagnostics=types.SimpleNamespace(write=lambda *args:None)
   def states(self):pass
   def cmd(self,code,state,label):self.calls.append((code,state,label));return raw
   def state_read(self,label):return after
  return Runner()
 def invoke(self,r,proof):
  # Exercise the actual generated method on an isolated fake runner.
  tree=ast.parse((HERE/'controller.py').read_text())
  fn=next(n for n in ast.walk(tree)if isinstance(n,ast.FunctionDef)and n.name=='continue_after_victory')
  ns={'RESOURCE_ROOT':HERE};exec(compile(ast.Module(body=[fn],type_ignores=[]),'endgame-method','exec'),ns)
  return ns['continue_after_victory'](r,200,proof)
 def proof(self,**kwargs):return dict(dict(turn=199,active=False,remaining=1,local_player=0,player0_human=True),**kwargs)
 def test_python_optin_and_budget_guard(self):
  r=self.fake(enabled=False);self.assertFalse(self.invoke(r,self.proof()));self.assertFalse(r.calls)
  r=self.fake();p=self.proof();p['remaining']=2;self.assertFalse(self.invoke(r,p));self.assertFalse(r.calls)
 def test_remaining_only_resume_no_new_turn_budget(self):
  r=self.fake(after=self.proof());self.assertTrue(self.invoke(r,self.proof()))
  self.assertEqual(len(r.calls),2);self.assertNotIn('SetTurns',r.calls[1][0]);self.assertIn('GetTurns()==1',r.calls[1][0])
  self.assertFalse(self.invoke(r,self.proof()));self.assertEqual(len(r.calls),2)
 def test_native_already_advanced_never_activates_again(self):
  after=self.proof();after.update(turn=200,remaining=0)
  r=self.fake(after=after);self.assertTrue(self.invoke(r,self.proof()));self.assertEqual(len(r.calls),1)
 def test_ambiguous_button_reply_is_reserved(self):
  r=self.fake(raw='CSC_ENDGAME_CONTINUE_BEGIN 4 1 199')
  self.assertFalse(self.invoke(r,self.proof()));self.assertFalse(self.invoke(r,self.proof()));self.assertEqual(len(r.calls),1)
