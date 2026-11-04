import ast,json,re,sys,tempfile,textwrap,types,unittest,os
from pathlib import Path
from lupa.lua51 import LuaRuntime
H=Path(__file__).resolve().parent
class WarGuards(unittest.TestCase):
 def lua(self,setup=''):
  l=LuaRuntime();l.execute('''
calls=0;war=true;key='CHOICE_EXIT';definition=true;open=true;human=false;localplayer=-1;peer=5;turn=80
Game={GetCurrentGameTurn=function()return turn end,GetLocalPlayer=function()return localplayer end}
Players={[0]={IsHuman=function()return human end,GetDiplomacy=function()return{IsAtWarWith=function(self,from)assert(from==5);return war end}end}}
GameInfo={DiplomacySelections=function()local used=false;return function()if definition and not used then used=true;return{Type='DECLARE_WAR_FROM_AI',Key=key}end end end}
DiplomacyManager={FindOpenSessionID=function()return 17 end,IsSessionIDOpen=function(id)assert(id==17);return open end,GetSessionInfo=function()return{FromPlayer=peer,ToPlayer=0}end,CloseSession=function(id)assert(id==17);calls=calls+1 end,AddResponse=function()error('forbidden response')end,AddStatement=function()error('forbidden statement')end}
ContextPtr={IsHidden=function()return true end};Close=function()error('hidden view close')end;print=function()end
''');l.execute(setup)
  code=(H/'war_session_dismissal.lua').read_text()
  for k,v in dict(FROM=5,CORE_TURN=80,TARGET_TURN=85,CORE_ACTIVE=True,CORE_LOCAL=-1,CORE_HUMAN=False).items():code=code.replace('__'+k+'__',str(v).lower())
  l.execute(code);return l.globals().calls
 def test_declared_war_with_native_exit_only_definition_closes_once(self):self.assertEqual(self.lua(),1)
 def test_no_peace_war_creation_or_unreviewed_choice(self):
  for setup in ("key='CHOICE_POSITIVE'",'definition=false','war=false','open=false','localplayer=0','peer=3','turn=82'):
   self.assertEqual(self.lua(setup),0,setup)
 def method(self,lines,replies):
  draft=(H/'controller.py').read_text();tree=ast.parse(draft);cls=next(x for x in tree.body if isinstance(x,ast.ClassDef)and x.name=='FullGameController');node=next(x for x in cls.body if isinstance(x,ast.FunctionDef)and x.name=='dismiss_observer_warning')
  ns=dict(re=re,json=json,RESOURCE_ROOT=H,PASSIVE_OBSERVER_STATEMENTS=frozenset({'DIPLOMATIC_KUDO'}),FIRST_MEET_OBSERVER_STATEMENTS=frozenset(),EXIT_ONLY_OBSERVER_WARS=frozenset({'DECLARE_SURPRISE_WAR','DECLARE_FORMAL_WAR'}));exec(textwrap.dedent(ast.get_source_segment(draft,node)),ns)
  temp=tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH'));self.addCleanup(temp.cleanup);root=Path(temp.name);(root/'Logs').mkdir();(root/'Logs/DiplomacyManager.csv').write_text(lines)
  calls=[];answers=iter(replies)
  f=types.SimpleNamespace(allow_observer_warning_dismissal=True,game_pid=17712,seq=0,root=root,state={'DiplomacyActionView':9},states=lambda:None,state_read=lambda label:dict(turn=80,active=True,remaining=5,local_player=-1,player0_human=False),diagnostics=types.SimpleNamespace(USER=root,journal=lambda *a,**k:None,write=lambda *a:None))
  def cmd(code,*a,**k):calls.append(code);return next(answers)
  f.cmd=cmd;f.dismiss=types.MethodType(ns['dismiss_observer_warning'],f);return f,calls
 def test_two_open_sessions_are_not_hidden_by_first_reserved_key(self):
  f,calls=self.method('80,3,0,3,DECLARE_SURPRISE_WAR\n80,5,0,5,DECLARE_FORMAL_WAR\n',['CSC_OBSERVER_WARNING_DISMISS_REQUESTED']*2)
  f.dismiss(85);self.assertEqual(len(calls),1);f.dismiss(85);self.assertEqual(len(calls),2);f.dismiss(85);self.assertEqual(len(calls),2)
  self.assertIn('local from=5',calls[0]);self.assertIn('local from=3',calls[1])
 def test_closed_newest_session_does_not_hide_other_open_session(self):
  f,calls=self.method('80,3,0,3,DECLARE_SURPRISE_WAR\n80,5,0,5,DECLARE_FORMAL_WAR\n',['CSC_OBSERVER_WARNING_DISMISS_SKIPPED no_session','CSC_OBSERVER_WARNING_DISMISS_REQUESTED']);f.dismiss(85);self.assertEqual(len(calls),2)
 def test_newer_deal_for_same_participant_prevents_old_war_fallback(self):
  f,calls=self.method('80,5,0,5,DECLARE_FORMAL_WAR\n80,5,0,5,MAKE_DEAL\n',[]);f.dismiss(85);self.assertEqual(calls,[])
 def test_ambiguous_transmission_never_resends(self):
  f,calls=self.method('80,5,0,5,DECLARE_FORMAL_WAR\n',['ACK true nil']);f.dismiss(85);f.dismiss(85);self.assertEqual(len(calls),1)
if __name__=='__main__':unittest.main()
