"""Offline Lua51/controller fixtures: no game process, console or transport."""
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock
from lupa.lua51 import LuaRuntime
from .controller import FullGameController, CANCELLABLE_OBSERVER_PROMPTS, PASSIVE_OBSERVER_STATEMENTS

HERE=Path(__file__).resolve().parent
STATEMENT='WARNING_STOP_SPYING_ON_ME'
CSV='205,4,0,4,'+STATEMENT+',NONE,INITIAL,Processing Immediately\n'

class SpyLuaTests(unittest.TestCase):
 def guard(self,setup='',**override):
  lua=LuaRuntime();lua.execute(r'''
turn=205;localPlayer=-1;human=false;open=true;peer=4;recipient=0;id=17;finds=0;calls=0
definition=true;group='WARNING_STOP_SPYING_ON_ME_FROM_AI';subtype='NONE';initiator='AI'
choices={'CHOICE_POSITIVE','CHOICE_NEGATIVE'};deferred=false;swapped=false;markers={}
Game={GetCurrentGameTurn=function()return turn end,GetLocalPlayer=function()return localPlayer end}
Players={[0]={IsHuman=function()return human end}}
GameInfo={DiplomacyStatements=function()local used=false;return function()
 if definition and not used then used=true;return {Type='WARNING_STOP_SPYING_ON_ME',Initiator=initiator,SubType=subtype,Selections=group}end end end,
 DiplomacySelections=function()local i=0;return function()i=i+1;if choices[i]then return{Type='WARNING_STOP_SPYING_ON_ME_FROM_AI',Key=choices[i]}end end end}
DiplomacyManager={FindOpenSessionID=function(a,b)assert(a==0 and b==4);finds=finds+1;return swapped and finds>1 and 18 or id end,
 IsSessionIDOpen=function(i)assert(i==17);return open end,
 GetSessionInfo=function(i)assert(i==17);return{FromPlayer=peer,ToPlayer=recipient}end,
 CloseSession=function(i)assert(i==17);calls=calls+1;if not deferred then open=false end end,
 AddResponse=function()error('forbidden response')end,AddStatement=function()error('forbidden statement')end}
ContextPtr={IsHidden=function()return true end};Close=function()error('hidden cosmetic close')end
AutoplayManager={SetActive=function()error('forbidden activation')end,SetTurns=function()error('forbidden budget')end}
print=function(...)local a={...};for i,v in ipairs(a)do a[i]=tostring(v)end;markers[#markers+1]=table.concat(a,' ')end
''');lua.execute(setup)
  values=dict(FROM=4,CORE_TURN=205,TARGET_TURN=206,CORE_ACTIVE=True,CORE_LOCAL=-1,CORE_HUMAN=False,STATEMENT=STATEMENT);values.update(override)
  code=(HERE/'spy_warning_cancellation.lua').read_text(encoding='utf-8')
  for k,v in values.items():code=code.replace('__'+k+'__',str(v).lower()if isinstance(v,bool)else str(v))
  self.assertNotIn('__',code);lua.execute(code)
  return lua.globals().calls,list(lua.globals().markers.values())
 def test_initial_warning_cancels_exact_session_without_response(self):
  n,m=self.guard();self.assertEqual(n,1)
  self.assertTrue(any('CSC_OBSERVER_CONVERSATION_CANCELLED 205 17 4 0'in s for s in m))
  self.assertTrue(any('POSSIBLE_IMPLICIT_DIPLOMATIC_EFFECTS'in s for s in m))
 def test_reviewed_stock_ignore_variant_is_not_invoked(self):self.assertEqual(self.guard("choices[3]='CHOICE_IGNORE'")[0],1)
 def test_ui_cached_human_lag_keeps_core_authority(self):
  for clock in(205,204):
   n,m=self.guard(f'human=true;turn={clock}');self.assertEqual(n,1);self.assertTrue(any('STALE_UI_HUMAN'in s for s in m))
 def test_wrong_core_phase_never_cancels(self):
  for change in({'CORE_HUMAN':True},{'CORE_ACTIVE':False},{'CORE_LOCAL':0},{'TARGET_TURN':205},{'TARGET_TURN':211}):
   with self.subTest(change=change):self.assertEqual(self.guard(**change)[0],0)
 def test_clock_control_session_and_participant_guards(self):
  for setup in('turn=203','turn=206','localPlayer=0','open=false','peer=5','recipient=1','id=-1','swapped=true'):
   with self.subTest(setup=setup):self.assertEqual(self.guard(setup)[0],0)
 def test_loaded_statement_selection_shapes_fail_closed(self):
  for setup in('definition=false',"group='MAKE_DEAL'","initiator='HUMAN'","subtype='POSITIVE'",
   "choices={'CHOICE_EXIT'}","choices={'CHOICE_POSITIVE'}","choices[3]='UNREVIEWED_CHOICE'",'GameInfo.DiplomacyStatements=nil'):
   with self.subTest(setup=setup):self.assertEqual(self.guard(setup)[0],0)
  self.assertEqual(self.guard(STATEMENT='WARNING_STOP_CONVERTING_MY_CITIES')[0],0)
 def test_async_close_is_requested_not_falsely_confirmed(self):
  n,m=self.guard('deferred=true');self.assertEqual(n,1)
  self.assertTrue(any('CANCEL_PENDING'in s for s in m));self.assertFalse(any('CONVERSATION_CANCELLED'in s for s in m))
 def test_visible_view_cleanup_does_not_repeat_native_cancellation(self):
  n,m=self.guard("ContextPtr.IsHidden=function()return false end;Close=function()print('COSMETIC_VIEW_CLOSED')end")
  self.assertEqual(n,1);self.assertEqual(sum('COSMETIC_VIEW_CLOSED'in s for s in m),1)

class SpyControllerTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH'));self.addCleanup(self.temp.cleanup)
  root=Path(self.temp.name);(root/'Logs').mkdir();self.log=root/'Logs/DiplomacyManager.csv';self.log.write_text(CSV)
  self.writes=[];self.events=[];f=FullGameController.__new__(FullGameController);self.f=f
  f.root=root;f.game_pid=999;f.seq=12;f.allow_observer_warning_dismissal=True
  f.state={'DiplomacyActionView':9};f.states=Mock()
  f.state_read=Mock(return_value=dict(turn=205,active=True,remaining=1,local_player=-1,player0_human=False))
  f.cmd=Mock(return_value='CSC_OBSERVER_WARNING_DISMISS_BEGIN\nCSC_OBSERVER_WARNING_DISMISS_REQUESTED\nCSC_OBSERVER_CONVERSATION_CANCELLED')
  f.diagnostics=types.SimpleNamespace(USER=root,journal=lambda *a,**k:self.events.append((a,k)),write=lambda *a:self.writes.append(a))
 def test_separate_set_routing_and_one_shot_cancellation_receipt(self):
  self.assertIn(STATEMENT,CANCELLABLE_OBSERVER_PROMPTS);self.assertNotIn(STATEMENT,PASSIVE_OBSERVER_STATEMENTS)
  self.f.dismiss_observer_warning(206);self.f.dismiss_observer_warning(206);self.assertEqual(self.f.cmd.call_count,1)
  code=self.f.cmd.call_args.args[0];self.assertIn('local from=4',code);self.assertIn('FindOpenSessionID(0,from)',code)
  self.assertNotIn('AddResponse(',code);self.assertNotIn('AddStatement(',code)
  r=self.writes[-1][1];self.assertTrue(r['cancelled_observer_conversation']);self.assertTrue(r['possible_implicit_diplomatic_effects'])
  self.assertEqual(r['guard_resource'],'spy_warning_cancellation.lua');self.assertEqual(self.events[0][0][0],'observer-conversation-cancellation-begin')
 def test_recorded_turn205_csv_trace_routes_to_the_guarded_handler(self):
  # Exact ordered phases/spacing from the failed campaign. No game or native
  # session is used: this proves routing of the captured failure, not live close.
  self.log.write_text('''205, 4, 0, -1, WARNING_STOP_SPYING_ON_ME, NONE, 00000000, Requesting Session (B)
205, 4, 0, 4, WARNING_STOP_SPYING_ON_ME, NONE, INITIAL, Adding to pending
205, 4, 0, 4, WARNING_STOP_SPYING_ON_ME, NONE, INITIAL, Processing Statement
205, 4, 0, 4, WARNING_STOP_SPYING_ON_ME, NONE, INITIAL, Processing Immediately
''')
  self.f.state_read.return_value=dict(turn=205,active=True,remaining=5,local_player=-1,player0_human=False)
  self.f.dismiss_observer_warning(210)
  self.assertEqual(self.f.cmd.call_count,1)
  self.assertEqual(self.writes[-1][1]['guard_resource'],'spy_warning_cancellation.lua')
  self.assertIn('local target=210',self.f.cmd.call_args.args[0])
 def test_newer_deal_or_wrong_csv_phase_blocks_older_warning(self):
  for row in('205,4,0,4,MAKE_DEAL,NONE,INITIAL,Processing Immediately\n',
   '205,4,0,4,'+STATEMENT+',POSITIVE,INITIAL,Processing Immediately\n',
   '205,4,0,4,'+STATEMENT+',NONE,INITIAL,Adding to pending\n','205,4,0,4,'+STATEMENT+'\n'):
   with self.subTest(row=row):self.log.write_text(CSV+row);self.f.dismiss_observer_warning(206);self.f.cmd.assert_not_called()
 def test_other_participants_and_turns_cannot_cancel(self):
  for row in(CSV.replace(',4,0,4,',',4,5,4,'),CSV.replace('205,','204,')):
   self.log.write_text(row);self.f.dismiss_observer_warning(206);self.f.cmd.assert_not_called()
 def test_opt_in_and_core_proof_required(self):
  self.f.allow_observer_warning_dismissal=False;self.f.dismiss_observer_warning(206);self.f.state_read.assert_not_called()
  self.f.allow_observer_warning_dismissal=True
  for k,v in(('active',False),('remaining',6),('local_player',0),('player0_human',True)):
   p=dict(turn=205,active=True,remaining=1,local_player=-1,player0_human=False);p[k]=v
   self.f.state_read.return_value=p;self.f.dismiss_observer_warning(206)
  self.f.cmd.assert_not_called()
 def test_explicit_preaction_skips_are_bounded(self):
  self.f.cmd.return_value='CSC_OBSERVER_WARNING_DISMISS_SKIPPED session_changed'
  for _ in range(8):self.f.dismiss_observer_warning(206)
  self.assertEqual(self.f.cmd.call_count,4)
 def test_ambiguity_or_begin_never_replays(self):
  for reply in('ACK true nil','CSC_OBSERVER_WARNING_DISMISS_BEGIN\nCSC_OBSERVER_WARNING_DISMISS_SKIPPED session_closed',OSError('ambiguous send')):
   with self.subTest(reply=reply):
    self.f.warning_dismissals=set();self.f.warning_guard_checks={};self.f.cmd.reset_mock()
    self.f.cmd.side_effect=reply if isinstance(reply,Exception)else None;self.f.cmd.return_value=reply
    if isinstance(reply,Exception):
     with self.assertRaises(OSError):self.f.dismiss_observer_warning(206)
     self.f.cmd.side_effect=None
    else:self.f.dismiss_observer_warning(206)
    self.f.dismiss_observer_warning(206);self.assertEqual(self.f.cmd.call_count,1)

if __name__=='__main__':unittest.main()
