"""No Civ connections: fake transport/control fixtures plus optional actual Lua51."""
import argparse,json,pathlib,socket,struct,tempfile,types,unittest
from unittest.mock import patch
from . import controller as control
from . import renderer_evidence as renderer
from .transport import receive_command,MissingAcknowledgment,NativeLuaFailure

class Clock:
 def __init__(self):self.t=0
 def __call__(self):self.t+=0.1;return self.t

class FakeSocket:
 def __init__(self,chunks):self.chunks=list(chunks);self.sends=[]
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def settimeout(self,t):pass
 def sendall(self,data):self.sends.append(data)
 def recv(self,n):
  if not self.chunks:raise socket.timeout()
  item=self.chunks.pop(0)
  if isinstance(item,Exception):raise item
  return item

def frame(text):
 data=text.encode('utf-8');return struct.pack('<II',len(data),1)+data

def boundary(turn,target,n):
 if turn>target:raise RuntimeError('overrun')
 if turn==target:return'done',n
 if n<3:return'wait',n+1
 raise RuntimeError('inactive below target')

class Base:
 def __init__(self,root):self.seq=0;self.required_state=None;self.state={'GameCore_Tuner':1}
 def states(self):pass

class OfflineTests(unittest.TestCase):
 scratch=None
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir=self.scratch);self.addCleanup(self.temp.cleanup)
  self.events=[];self.writes=[]
  diag=types.SimpleNamespace(sha=lambda p:'test-digest',write=lambda *a:self.writes.append(a),journal=lambda *a,**kw:self.events.append((a,kw)),checkpoint=lambda *a:None)
  self.f=control.make_controller(Base,diagnostics=diag,boundary_decision=boundary,tuner_port=4318)(self.temp.name)
 def test_public_handoff_exception_matches_core(self):
  from . import SourceUpdateHandoff
  self.assertIs(SourceUpdateHandoff,control.SourceUpdateHandoff)
 def log_boundary(self,text=None):
  import gzip
  p=pathlib.Path(self.temp.name)/'lua-boundary';p.mkdir()
  size=len(text.encode())if text is not None else 0
  (p/'log-segments.json').write_text(json.dumps([{'file':'Lua.log','start':100,'end':100+size,'bytes':size}]))
  if text is not None:(p/'Lua.log.gz').write_bytes(gzip.compress(text.encode()))
  return p
 def test_exact_reviewed_false_ack_trace_is_diagnostic(self):
  from .log_evidence import review_lua_boundary
  r=review_lua_boundary(self.log_boundary('PlotInfo: CSC_FULL_ACK_1916_19002\tfalse\tread-only probe error\nstack traceback:\n'),['CSC_FULL_ACK_1916_19002'])
  self.assertEqual(r['blocking_errors'],0);self.assertEqual(r['known_diagnostic_errors'],1)
 def test_unknown_native_runtime_error_is_not_hidden_by_known_probe(self):
  from .log_evidence import review_lua_boundary
  r=review_lua_boundary(self.log_boundary('PlotInfo: CSC_FULL_ACK_1916_19002\tfalse\tprobe\nstack traceback:\nRuntime Error: native gameplay handler failed\nstack traceback:\n'),['CSC_FULL_ACK_1916_19002'])
  self.assertEqual(r['known_diagnostic_errors'],1);self.assertEqual(r['blocking_errors'],2)
 def test_truncated_or_wrong_ack_trace_remains_unreviewed(self):
  from .log_evidence import review_lua_boundary
  r=review_lua_boundary(self.log_boundary('stack traceback:\nPlotInfo: CSC_FULL_ACK_999_1\tfalse\terr\nstack traceback:\n'),['CSC_FULL_ACK_1916_19002'])
  self.assertEqual(r['blocking_errors'],2)
 def test_closed_empty_lua_segment_is_observed(self):
  from .log_evidence import review_lua_boundary
  r=review_lua_boundary(self.log_boundary());self.assertTrue(r['evidence_observed']);self.assertEqual(r['blocking_errors'],0)
 def test_missing_lua_boundary_is_not_zero_errors(self):
  from .log_evidence import review_lua_boundary
  r=review_lua_boundary(pathlib.Path(self.temp.name));self.assertFalse(r['evidence_observed']);self.assertIsNone(r['blocking_errors'])
 def test_source_handoff_archives_without_native_control(self):
  self.f.game_pid=99;self.f.ready=unittest.mock.Mock();self.f.capture=unittest.mock.Mock();self.f.preserve_telemetry=unittest.mock.Mock()
  self.f.state_read=lambda label:{'turn':83,'active':False,'local_player':0,'player0_human':True}
  self.f.cmd=unittest.mock.Mock(side_effect=AssertionError('No control command during handoff'))
  result=self.f.handoff_for_update(83,{'cycle_executed':False})
  self.assertTrue(result['verified']);self.assertEqual(result['native_controls_issued'],0);self.assertFalse(result['world_reloaded'])
  self.assertEqual(self.f.capture.call_count,1);self.f.cmd.assert_not_called()
 def test_source_handoff_rejects_active_or_wrong_clock_or_observer(self):
  self.f.game_pid=99;self.f.ready=unittest.mock.Mock();self.f.capture=unittest.mock.Mock();self.f.preserve_telemetry=unittest.mock.Mock()
  for proof in ({'turn':83,'active':True,'local_player':0,'player0_human':True},{'turn':84,'active':False,'local_player':0,'player0_human':True},{'turn':83,'active':False,'local_player':-1,'player0_human':False}):
   self.f.state_read=lambda label,p=proof:p
   with self.assertRaises(AssertionError):self.f.handoff_for_update(83)
  self.f.capture.assert_not_called();self.f.preserve_telemetry.assert_not_called()

 def renderer_root(self,manifest,data=None):
  import gzip
  root=pathlib.Path(self.temp.name);folder=root/'diagnostics'/'checkpoint';folder.mkdir(parents=True)
  (root/'run-start.json').write_text(json.dumps({'time':100}))
  (folder/'log-segments.json').write_text(json.dumps(manifest))
  if data is not None:(folder/'Renderer.log.gz').write_bytes(gzip.compress(data))
  return root
 def test_renderer_closed_empty_delta_is_observed_not_fault(self):
  root=self.renderer_root([{'file':'Renderer.log','start':900,'end':900,'bytes':0}])
  report=renderer.review(root)
  self.assertEqual(report['at_or_after_run_start_events'],0)
  self.assertTrue(report['segments'][0]['observed_empty_delta'])
  renderer.assert_no_errors(report)
 def test_missing_renderer_remains_unknown_without_false_fault(self):
  report=renderer.review(self.renderer_root([]))
  self.assertIsNone(report['at_or_after_run_start_events'])
  self.assertIn('UNOBSERVED',report['renderer_error_gate'])
  renderer.assert_no_errors(report)
 def test_positive_renderer_error_still_blocks(self):
  data=b'[2026-10-22 22:00:00] Unable to locate appropriate Pipeline State Object. SP: 58 SM: 2 Vertex Format: 23 Topology: 3\n'
  report=renderer.review(self.renderer_root([{'file':'Renderer.log','start':0,'end':len(data),'bytes':len(data)}],data))
  self.assertEqual(report['at_or_after_run_start_events'],1)
  with self.assertRaises(RuntimeError):renderer.assert_no_errors(report)
 def test_nonempty_missing_renderer_archive_remains_unknown(self):
  report=renderer.review(self.renderer_root([{'file':'Renderer.log','start':0,'end':900,'bytes':900}]))
  self.assertIsNone(report['at_or_after_run_start_events'])
 def test_warning_csv_initiator_is_not_used_as_session_id(self):
  self.f.game_pid=123;self.f.allow_observer_warning_dismissal=True
  self.f.diagnostics.USER=pathlib.Path(self.temp.name);logs=self.f.diagnostics.USER/'Logs';logs.mkdir()
  (logs/'DiplomacyManager.csv').write_text('Game Turn, From, To, Initiator, Type\n67, 2, 0, 2, WARNING_TOO_MANY_TROOPS_NEAR_ME\n')
  self.f.state_read=lambda label:{'turn':67,'active':True,'remaining':1,'local_player':-1,'player0_human':False}
  self.f.state['DiplomacyActionView']=9
  self.f.cmd=unittest.mock.Mock(return_value='CSC_OBSERVER_WARNING_DISMISS_REQUESTED 67 9 2 0')
  self.f.dismiss_observer_warning(68);self.f.dismiss_observer_warning(68)
  self.assertEqual(self.f.cmd.call_count,1)
  code=self.f.cmd.call_args.args[0]
  self.assertIn('FindOpenSessionID(0,from)',code)
  self.assertNotIn('local id=2',code)

 def warning_fixture(self,replies):
  self.f.game_pid=123;self.f.allow_observer_warning_dismissal=True
  self.f.diagnostics.USER=pathlib.Path(self.temp.name);logs=self.f.diagnostics.USER/'Logs';logs.mkdir()
  (logs/'DiplomacyManager.csv').write_text('92,2,0,2,WARNING_TOO_MANY_TROOPS_NEAR_ME\n')
  self.f.state_read=lambda label:{'turn':92,'active':True,'remaining':1,'local_player':-1,'player0_human':False}
  self.f.state['DiplomacyActionView']=9;self.f.cmd=unittest.mock.Mock(side_effect=replies)
 def test_warning_explicit_guard_skip_can_recheck_then_one_dismissal(self):
  self.warning_fixture(['CSC_OBSERVER_WARNING_DISMISS_SKIPPED session_closed','CSC_OBSERVER_WARNING_DISMISS_BEGIN 92 2 2 0\nCSC_OBSERVER_WARNING_DISMISS_REQUESTED 92 2 2 0'])
  for _ in range(5):self.f.dismiss_observer_warning(93)
  self.assertEqual(self.f.cmd.call_count,2)
 def test_warning_repeated_skips_bounded(self):
  self.warning_fixture(['CSC_OBSERVER_WARNING_DISMISS_SKIPPED ui_control']*4)
  for _ in range(8):self.f.dismiss_observer_warning(93)
  self.assertEqual(self.f.cmd.call_count,4)
 def test_warning_ambiguous_or_begin_reply_never_rechecks(self):
  self.warning_fixture(['ACK true nil'])
  self.f.dismiss_observer_warning(93);self.f.dismiss_observer_warning(93)
  self.assertEqual(self.f.cmd.call_count,1)
 def test_warning_begin_even_with_skip_marker_never_rechecks(self):
  self.warning_fixture(['CSC_OBSERVER_WARNING_DISMISS_SKIPPED ui_clock\nCSC_OBSERVER_WARNING_DISMISS_BEGIN'])
  self.f.dismiss_observer_warning(93);self.f.dismiss_observer_warning(93)
  self.assertEqual(self.f.cmd.call_count,1)
 def test_warning_transport_failure_never_rechecks(self):
  self.warning_fixture([OSError('send outcome ambiguous')])
  with self.assertRaises(OSError):self.f.dismiss_observer_warning(93)
  self.f.dismiss_observer_warning(93);self.assertEqual(self.f.cmd.call_count,1)

 def test_passive_kudo_uses_same_guard_and_one_shot(self):
  self.warning_fixture(['CSC_OBSERVER_WARNING_DISMISS_REQUESTED'])
  (self.f.diagnostics.USER/'Logs/DiplomacyManager.csv').write_text('101,2,0,2,DIPLOMATIC_KUDO,NONE,INITIAL,Processing Immediately\n')
  self.f.state_read=lambda label:{'turn':101,'active':True,'remaining':1,'local_player':-1,'player0_human':False}
  self.f.dismiss_observer_warning(102);self.f.dismiss_observer_warning(102)
  self.assertEqual(self.f.cmd.call_count,1)
 def test_exit_only_agenda_statements_use_guarded_one_shot(self):
  for statement in ('DIPLOMATIC_WARNING','DIPLOMATIC_HIDDEN_AGENDA_KUDO','DIPLOMATIC_HIDDEN_AGENDA_WARNING'):
   with self.subTest(statement=statement):
    self.warning_fixture(['CSC_OBSERVER_WARNING_DISMISS_REQUESTED'])
    (self.f.diagnostics.USER/'Logs/DiplomacyManager.csv').write_text('92,5,0,5,'+statement+',NONE,INITIAL,Processing Immediately\n')
    self.f.dismiss_observer_warning(93);self.f.dismiss_observer_warning(93)
    self.assertEqual(self.f.cmd.call_count,1)
    self.assertIn('local from=5',self.f.cmd.call_args.args[0])
    self.assertNotIn('AddResponse(',self.f.cmd.call_args.args[0])
    self.f.warning_dismissals.clear();self.f.warning_guard_checks.clear()
    import shutil
    shutil.rmtree(self.f.diagnostics.USER/'Logs')
 def test_agenda_warning_cannot_override_newer_choice_or_other_turn(self):
  self.warning_fixture([])
  for suffix in ('92,2,0,2,MAKE_DEAL','92,2,0,2,MAKE_DEMAND','92,2,0,2,REQUEST_PROMISE'):
   (self.f.diagnostics.USER/'Logs/DiplomacyManager.csv').write_text('92,2,0,2,DIPLOMATIC_HIDDEN_AGENDA_WARNING\n'+suffix+'\n91,5,0,5,DIPLOMATIC_HIDDEN_AGENDA_WARNING\n')
   self.f.dismiss_observer_warning(93)
  self.f.cmd.assert_not_called()
 def test_latest_deal_cannot_fall_back_to_old_same_turn_warning(self):
  self.warning_fixture([])
  (self.f.diagnostics.USER/'Logs/DiplomacyManager.csv').write_text('92,2,0,2,WARNING_TOO_MANY_TROOPS_NEAR_ME\n92,2,0,2,MAKE_DEAL\n')
  self.f.dismiss_observer_warning(93);self.f.cmd.assert_not_called()
 def test_unhandled_passive_or_choice_statement_stays_diagnostic(self):
  self.warning_fixture([])
  for statement in('MAKE_DEAL','MAKE_DEMAND','REQUEST_FRIENDSHIP','UNKNOWN_STATEMENT'):
   (self.f.diagnostics.USER/'Logs/DiplomacyManager.csv').write_text('92,2,0,2,'+statement+'\n')
   self.f.dismiss_observer_warning(93)
  self.f.cmd.assert_not_called()
 def test_active_handoff_preserves_single_existing_budget(self):
  proof={'turn':101,'active':True,'remaining':1,'local_player':-1,'player0_human':False}
  self.f.game_pid=99;self.f.state_read=lambda label:dict(proof)
  self.f.preserve_telemetry=unittest.mock.Mock();self.f.capture=unittest.mock.Mock();self.f.capture_blocker=unittest.mock.Mock()
  self.f.cmd=unittest.mock.Mock(side_effect=AssertionError('No native controls'))
  r=self.f.handoff_active_for_update(102)
  self.assertTrue(r['verified']);self.assertEqual(r['native_controls_issued'],0);self.assertFalse(r['second_activation'])
  self.f.cmd.assert_not_called()
 def test_active_handoff_rejects_moving_phase_or_wrong_budget(self):
  p={'turn':101,'active':True,'remaining':1,'local_player':-1,'player0_human':False}
  self.f.game_pid=99;self.f.preserve_telemetry=unittest.mock.Mock();self.f.capture=unittest.mock.Mock();self.f.capture_blocker=unittest.mock.Mock()
  self.f.state_read=lambda label:dict(p)
  with self.assertRaises(AssertionError):self.f.handoff_active_for_update(103)
  self.f.state_read=unittest.mock.Mock(side_effect=[dict(p),dict(p,turn=102,active=False,remaining=0)])
  receipt=self.f.handoff_active_for_update(102);self.assertFalse(receipt['verified']);self.assertTrue(receipt['continue_owner'])
  self.assertFalse(any(str(args[0]).endswith('source-update-handoff.json')for args in self.writes))

 def test_moving_active_handoff_returns_to_existing_operation_without_reactivation(self):
  request=pathlib.Path(self.temp.name)/'source-update-request.json';request.write_text(json.dumps({'allow_active_handoff':True}))
  samples=iter([{'turn':101,'active':True,'remaining':1,'local_player':-1,'player0_human':False},
                {'turn':102,'active':False,'remaining':0,'local_player':0,'player0_human':True}])
  self.f.state_read=lambda label:next(samples);self.f.ready=unittest.mock.Mock()
  self.f.handoff_active_for_update=unittest.mock.Mock(return_value={'verified':False,'continue_owner':True})
  self.f.cmd=unittest.mock.Mock(side_effect=AssertionError('No second native activation'))
  with patch.object(control.time,'sleep',lambda seconds:None):self.f._await_target(102)
  self.f.handoff_active_for_update.assert_called_once_with(102);self.f.cmd.assert_not_called()
  self.assertEqual(self.f.last_interval_turn,102)

 def test_three_boundary_replies_remain_required_without_long_idle_waits(self):
  self.f.state_read=unittest.mock.Mock(return_value={'turn':100,'active':False,'local_player':0,'player0_human':True})
  with patch.object(control.time,'sleep')as sleep:self.f.ready(100,'fixture')
  self.assertEqual(self.f.state_read.call_count,3)
  self.assertEqual([c.args[0]for c in sleep.call_args_list],[.15,.15])
 def test_fast_poll_observes_completion_without_extra_activation(self):
  self.f.state_read=unittest.mock.Mock(return_value={'turn':101,'active':False,'remaining':0,'local_player':0,'player0_human':True})
  self.f.ready=unittest.mock.Mock();self.f.cmd=unittest.mock.Mock(side_effect=AssertionError('No control resend'))
  with patch.object(control.time,'sleep')as sleep:self.f._await_target(101)
  self.assertEqual(sleep.call_args.args,(.5,));self.f.ready.assert_called_once_with(101,'after-101')
  self.f.cmd.assert_not_called()
 def test_fragmented_delayed_ack_same_socket(self):
  token='ACK_FIXTURE';packet=frame('O\0GameCore_Tuner: '+token+'\ttrue\tnil')
  fake=FakeSocket([packet[:3],socket.timeout(),packet[3:11],socket.timeout(),packet[11:]])
  text,ack=receive_command('control();',7,token,4318,timeout=15,connect=lambda *a,**kw:fake,clock=Clock())
  self.assertTrue(ack);self.assertIn(token,text);self.assertEqual(len(fake.sends),1)
 def test_missing_ack_never_resends_mutation(self):
  fake=FakeSocket([])
  with self.assertRaises(MissingAcknowledgment):receive_command('mutation();',7,'ACK_FIXTURE',4318,timeout=1,connect=lambda *a,**kw:fake,clock=Clock())
  self.assertEqual(len(fake.sends),1)
 def test_refused_connection_recovers_before_one_send(self):
  token='ACK_FIXTURE';fake=FakeSocket([frame(token+' true nil')]);attempts=[]
  def connect(*a,**kw):
   attempts.append(a)
   if len(attempts)<3:raise ConnectionRefusedError('listener briefly unavailable')
   return fake
  _,ack=receive_command('mutation();',7,token,4318,connect=connect,clock=Clock(),sleep=lambda _:None)
  self.assertTrue(ack);self.assertEqual(len(attempts),3);self.assertEqual(len(fake.sends),1)
 def test_persistent_connect_refusal_is_bounded_without_send(self):
  connect=unittest.mock.Mock(side_effect=ConnectionRefusedError('unavailable'))
  with self.assertRaises(ConnectionRefusedError):receive_command('mutation();',7,'ACK_FIXTURE',4318,connect=connect,clock=Clock(),sleep=lambda _:None)
  self.assertEqual(connect.call_count,3)
 def test_send_failure_never_reconnects(self):
  fake=FakeSocket([])
  def failed_send(data):fake.sends.append(data);raise ConnectionResetError('ambiguous send')
  fake.sendall=failed_send;connect=unittest.mock.Mock(return_value=fake)
  with self.assertRaises(ConnectionResetError):receive_command('mutation();',7,'ACK_FIXTURE',4318,connect=connect,clock=Clock())
  self.assertEqual(connect.call_count,1);self.assertEqual(len(fake.sends),1)
 def test_windows_unsafe_label_keeps_original_journal_and_one_send(self):
  label='donated-chain:24/1\\65536?*"<>|'
  with patch.object(control,'receive_command',return_value=('native receipt',True))as send:
   self.assertEqual(self.f.cmd('irreversible();',label=label),'native receipt')
  self.assertEqual(send.call_count,1);self.assertEqual(send.call_args.args[0],'irreversible();')
  sources=list((self.f.root/'pending-commands').glob('*.lua'));self.assertEqual(len(sources),1)
  self.assertFalse(any(x in sources[0].name for x in ':<>"/\\|?*'))
  self.assertEqual(self.writes[-1][1]['label'],label)
  self.assertEqual(sources[0].read_text(),'irreversible();')
 def test_long_dotted_labels_do_not_overwrite_reply_pair(self):
  with patch.object(control,'receive_command',return_value=('native receipt',True))as send:
   self.f.cmd('first();',label='site.'*100);self.f.cmd('second();',label='site.'*100)
  replies=list((self.f.root/'commands').glob('*.txt'));self.assertEqual(len(replies),2)
  self.assertEqual(send.call_count,2);self.assertTrue(all(len(x.name)<80 for x in replies))
 def test_context_discovery_selected_port_is_used(self):
  selected={'port':4318}
  self.f.tuner_port=lambda:selected['port']
  self.f.states=lambda:selected.update(port=4320)
  with patch.object(control,'receive_command',return_value=('native reply',True))as send:self.f.cmd('print("fixture");')
  self.assertEqual(send.call_args.args[3],4320)
  self.assertEqual(self.writes[-1][1]['port'],4320)
 def test_factory_accepts_unbound_port_getter(self):
  factory=control.make_controller(Base,diagnostics=self.f.diagnostics,boundary_decision=boundary,tuner_port=lambda:4320)
  f=factory(self.temp.name)
  with patch.object(control,'receive_command',return_value=('native reply',True))as send:f.cmd('print("fixture");')
  self.assertEqual(send.call_args.args[3],4320)
 def test_metadata_lock_retries_only_file_publication(self):
  count=[];original=self.f.diagnostics.write
  def write(path,value):
   count.append(path)
   if len(count)<3:raise PermissionError('Windows reader sharing lock')
   return original(path,value)
  self.f.diagnostics.write=write
  with patch.object(control.time,'sleep',lambda _:None),patch.object(control,'receive_command',return_value=('native reply',True))as send:
   self.assertEqual(self.f.cmd('mutation();'),'native reply')
  self.assertEqual(send.call_count,1);self.assertEqual(len(count),5)
 def test_persistent_optional_metadata_lock_preserves_command_evidence(self):
  self.f.diagnostics.write=unittest.mock.Mock(side_effect=PermissionError('locked status index'))
  with patch.object(control.time,'sleep',lambda _:None),patch.object(control,'receive_command',return_value=('native reply',True))as send:
   self.assertEqual(self.f.cmd('mutation();'),'native reply')
  self.assertEqual(send.call_count,1);self.assertEqual(self.f.diagnostics.write.call_count,15)
  self.assertEqual(next((self.f.root/'commands').glob('*.txt')).read_text(),'native reply')
  warnings=[x for x in self.events if x[0][0]=='active-command-metadata-warning']
  self.assertEqual(len(warnings),3)
  self.assertTrue(all(x[1]['no_native_command_replayed']for x in warnings))
 def test_metadata_lock_does_not_hide_native_lua_failure(self):
  self.f.diagnostics.write=unittest.mock.Mock(side_effect=PermissionError('locked status index'))
  with patch.object(control.time,'sleep',lambda _:None),patch.object(control,'receive_command',side_effect=NativeLuaFailure('actual native error'))as send:
   with self.assertRaises(NativeLuaFailure):self.f.cmd('mutation();')
  self.assertEqual(send.call_count,1)
 def test_native_error_preserves_reply(self):
  fake=FakeSocket([frame('ACK_FIXTURE false actual Lua error')])
  with self.assertRaises(NativeLuaFailure)as caught:receive_command('mutation();',7,'ACK_FIXTURE',4318,timeout=1,connect=lambda *a,**kw:fake,clock=Clock())
  self.assertIn('actual Lua error',caught.exception.text);self.assertEqual(len(fake.sends),1)
 def test_unconfirmed_host_is_explicit(self):
  fake=FakeSocket([]);_,ack=receive_command('Network.HostGame();',7,'ACK_FIXTURE',4318,timeout=1,check=False,connect=lambda *a,**kw:fake,clock=Clock())
  self.assertFalse(ack);self.assertEqual(len(fake.sends),1)
 def test_cmd_failure_records_evidence_once(self):
  with patch.object(control,'receive_command',side_effect=MissingAcknowledgment('token','partial native reply'))as send:
   with self.assertRaises(MissingAcknowledgment):self.f.cmd('mutation();',label='fixture')
  self.assertEqual(send.call_count,1)
  self.assertEqual(next((self.f.root/'commands').glob('*.txt')).read_text(),'partial native reply')
 def test_command_artifact_matches_watchdog_filename(self):
  def write(path,value):
   path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
  self.f.diagnostics.write=write
  with patch.object(control,'receive_command',return_value=('native reply',True))as send:
   self.f.cmd('print("fixture");',label='fixture')
  metadata=json.loads((self.f.root/'active-command.json').read_text())
  self.assertEqual(metadata['phase'],'acknowledged');self.assertEqual(metadata['label'],'fixture')
  self.assertTrue(pathlib.Path(metadata['source']).is_file());self.assertEqual(send.call_count,1)
  self.assertEqual(sorted(p.name for p in self.f.root.glob('active-*.json')),['active-command.json'])
 def test_snapshot_writes_standard_turn_filename(self):
  def write(path,value):
   path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
  self.f.diagnostics.write=write
  self.f.cmd=unittest.mock.Mock(return_value='CSCBASE_SNAPSHOT={"turn":25}')
  self.f.snapshot(1,25)
  self.assertEqual([p.name for p in (self.f.root/'game-01').iterdir()],['turn-025.json'])
  self.assertEqual(json.loads((self.f.root/'game-01/turn-025.json').read_text())['turn'],25)
 def test_readonly_query_retry_is_bounded(self):
  count=[]
  def fail(*a,**kw):count.append(a);raise MissingAcknowledgment('token','')
  self.f.cmd=fail
  with patch.object(control.time,'sleep',lambda t:None):
   with self.assertRaises(MissingAcknowledgment):self.f.state_read('fixture')
  self.assertEqual(len(count),3)
 def test_readonly_native_lua_error_is_not_retried(self):
  self.f.cmd=unittest.mock.Mock(side_effect=NativeLuaFailure('actual Lua error'))
  with self.assertRaises(NativeLuaFailure):self.f.state_read('fixture')
  self.assertEqual(self.f.cmd.call_count,1)
 def test_async_activation_starts_one_finite_operation(self):
  calls=[];self.f.ready=lambda expected,label:calls.append(('ready',expected))
  self.f.cmd=lambda code,*a,**kw:calls.append(('command',code))
  rows=iter([{'turn':1,'active':False,'remaining':4},{'turn':1,'active':True,'remaining':4},{'turn':5,'active':False,'remaining':0}])
  self.f.state_read=lambda label:next(rows)
  clock=Clock()
  with patch.object(control.time,'monotonic',clock),patch.object(control.time,'time',clock),patch.object(control.time,'sleep',lambda t:None):self.f.play(5)
  self.assertEqual(self.f.last_interval_turn,5);self.assertEqual(len([x for x in calls if x[0]=='command']),1)
  self.assertEqual(calls[0],('ready',1));self.assertEqual(calls[-1],('ready',5))
 def test_diplomacy_without_disaster_context(self):
  self.f.state={'DiplomacyActionView':7}
  self.f.state_read=lambda label:{'turn':240,'active':True,'remaining':5,'local_player':-1,'player0_human':False}
  self.f.cmd=unittest.mock.Mock(return_value='GUARD_NO_ACTION')
  self.f.release_disaster(245)
  self.assertEqual(self.f.cmd.call_count,1);self.assertEqual(self.f.cmd.call_args.args[1],'DiplomacyActionView')
 def test_human_core_never_closes_diplomacy(self):
  self.f.state={'DiplomacyActionView':7}
  self.f.state_read=lambda label:{'turn':240,'active':True,'remaining':5,'local_player':0,'player0_human':True}
  self.f.cmd=unittest.mock.Mock();self.f.release_disaster(245);self.f.cmd.assert_not_called()
 def test_wonder_without_other_playback_contexts(self):
  self.f.state={'WonderBuiltPopup':8}
  self.f.state_read=lambda label:{'turn':20,'active':True,'remaining':5,'local_player':-1,'player0_human':False}
  self.f.cmd=unittest.mock.Mock(return_value='GUARD_NO_ACTION')
  self.f.release_disaster(25)
  self.assertEqual(self.f.cmd.call_count,1);self.assertEqual(self.f.cmd.call_args.args[1],'WonderBuiltPopup')
 def test_human_core_never_closes_wonder(self):
  self.f.state={'WonderBuiltPopup':8}
  self.f.state_read=lambda label:{'turn':20,'active':True,'remaining':5,'local_player':0,'player0_human':True}
  self.f.cmd=unittest.mock.Mock();self.f.release_disaster(25);self.f.cmd.assert_not_called()
 def test_wrong_budget_never_closes(self):
  self.f.state={'NaturalDisasterPopup':1,'DiplomacyActionView':7,'WonderBuiltPopup':8}
  self.f.state_read=lambda label:{'turn':240,'active':True,'remaining':4,'local_player':-1,'player0_human':False}
  self.f.cmd=unittest.mock.Mock();self.f.release_disaster(245);self.f.cmd.assert_not_called()
 def test_independent_telemetry_preservation(self):
  self.f.state={'CSC_AdjacencyGameplay':1}
  def command(code,state,label,**kw):
   if label.endswith('research'):raise RuntimeError('research unavailable')
   return ('CSCBASE_SNAPSHOT='if label.endswith('primary-current')else'CSC_BUILDERS_SNAPSHOT=')+'{"turn":240}'
  self.f.cmd=unittest.mock.Mock(side_effect=command);self.f.preserve_telemetry()
  self.assertEqual(self.f.cmd.call_count,3)
  names=[pathlib.Path(x[0]).name for x in self.writes]
  self.assertIn('failure-preserve-research-warning.json',names);self.assertIn('failure-preserved-primary-current.json',names);self.assertIn('failure-preserved-builders-current.json',names)

def lua_fixtures(lua51_path):
 if lua51_path:
  import sys
  sys.path.insert(0,str(lua51_path))
 try:from lupa.lua51 import LuaRuntime
 except ImportError:return {'status':'UNOBSERVED','reason':'Lua51 runtime unavailable; no installation attempted'}
 count=0
 disaster=[(True,105,110,104,0,False,1),(True,105,110,105,-1,False,1),(False,105,110,104,0,False,0),(True,105,110,105,0,False,0),(True,105,110,104,0,True,0),(True,105,110,103,0,False,0),(True,105,110,104,2,False,0),(True,110,110,109,0,False,0),(True,105,250,104,0,False,0)]
 for active,core,target,ui,local,hidden,expected in disaster:
  code=control.GUARD
  for k,v in {'CORE_TURN':core,'TARGET_TURN':target,'CORE_ACTIVE':active}.items():code=code.replace('__'+k+'__',str(v).lower())
  lua=LuaRuntime();lua.execute('calls=0;Game={GetCurrentGameTurn=function()return '+str(ui)+' end,GetLocalPlayer=function()return '+str(local)+' end};ContextPtr={IsHidden=function()return '+str(hidden).lower()+' end};OnLocalPlayerTurnEnd=function()calls=calls+1 end;print=function()end')
  lua.execute(code);assert lua.globals().calls==expected;count+=1
 diplomacy=[(True,-1,False,240,-1,False,1),(True,-1,False,239,0,False,1),(False,0,True,240,0,False,0),(True,0,True,240,0,False,0),(True,-1,False,240,-1,True,0),(True,-1,False,238,0,False,0),(True,-1,False,240,1,False,0)]
 for active,corelocal,human,ui,local,hidden,expected in diplomacy:
  code=control.DIPLOMACY_GUARD
  for k,v in {'CORE_TURN':240,'TARGET_TURN':245,'CORE_ACTIVE':active,'CORE_LOCAL':corelocal,'CORE_HUMAN':human}.items():code=code.replace('__'+k+'__',str(v).lower())
  lua=LuaRuntime();lua.execute('calls=0;Game={GetCurrentGameTurn=function()return '+str(ui)+' end,GetLocalPlayer=function()return '+str(local)+' end};ContextPtr={IsHidden=function()return '+str(hidden).lower()+' end};Close=function()calls=calls+1 end;OnClose=function()error("forbidden response")end;DiplomacyManager={AddResponse=function()error("forbidden")end,CloseSession=function()error("forbidden")end};print=function()end')
  lua.execute(code);assert lua.globals().calls==expected;count+=1
 wonder=[(True,-1,False,20,25,20,0,False,1),(True,-1,False,20,25,19,0,False,1),(True,-1,False,20,25,20,-1,False,1),(False,-1,False,20,25,20,0,False,0),(True,0,True,20,25,20,0,False,0),(True,-1,False,20,20,20,0,False,0),(True,-1,False,20,26,20,0,False,0),(True,-1,False,20,25,18,0,False,0),(True,-1,False,20,25,20,1,False,0),(True,-1,False,20,25,20,0,True,0)]
 for active,corelocal,human,core,target,ui,local,hidden,expected in wonder:
  code=control.WONDER_GUARD
  for k,v in {'CORE_TURN':core,'TARGET_TURN':target,'CORE_ACTIVE':active,'CORE_LOCAL':corelocal,'CORE_HUMAN':human}.items():code=code.replace('__'+k+'__',str(v).lower())
  lua=LuaRuntime();lua.execute('calls=0;Game={GetCurrentGameTurn=function()return '+str(ui)+' end,GetLocalPlayer=function()return '+str(local)+' end};ContextPtr={IsHidden=function()return '+str(hidden).lower()+' end};Close=function()calls=calls+1 end;AutoplayManager={SetActive=function()error("forbidden")end,SetTurns=function()error("forbidden")end};print=function()end')
  lua.execute(code);assert lua.globals().calls==expected;count+=1
 warning=[(False,-1,True,True,2,1,1),(True,-1,True,True,2,1,0),(False,0,True,True,2,1,0),(False,-1,False,True,2,1,0),(False,-1,True,False,2,1,0),(False,-1,True,True,3,1,0),(False,-1,True,True,2,0,0)]
 for human,local,active,open_,peer,remaining,expected in warning:
  code=(control.RESOURCE_ROOT/'session_dismissal.lua').read_text(encoding='utf-8')
  for k,v in {'FROM':2,'CORE_TURN':67,'TARGET_TURN':67+remaining,'CORE_ACTIVE':active,'CORE_LOCAL':local,'CORE_HUMAN':human}.items():code=code.replace('__'+k+'__',str(v).lower())
  lua=LuaRuntime();lua.execute("calls=0;closed=nil;print=function()end;Game={GetCurrentGameTurn=function()return 67 end,GetLocalPlayer=function()return "+str(local)+" end};Players={[0]={IsHuman=function()return "+str(human).lower()+" end}};ContextPtr={IsHidden=function()return true end};DiplomacyManager={IsSessionIDOpen=function(id)assert(id==9);return "+str(open_).lower()+" end,FindOpenSessionID=function()return 9 end,GetSessionInfo=function(id)assert(id==9);return {FromPlayer="+str(peer)+",ToPlayer=0}end,CloseSession=function(id)closed=id;calls=calls+1 end,AddResponse=function()error('forbidden response')end,AddStatement=function()error('forbidden statement')end};AutoplayManager={SetActive=function()error('forbidden activation')end,SetTurns=function()error('forbidden budget')end}")
  lua.execute(code);assert lua.globals().calls==expected
  if expected:assert lua.globals().closed==9
  count+=1
 code=(control.RESOURCE_ROOT/'session_dismissal.lua').read_text(encoding='utf-8')
 for k,v in {'FROM':2,'CORE_TURN':92,'TARGET_TURN':93,'CORE_ACTIVE':True,'CORE_LOCAL':-1,'CORE_HUMAN':False}.items():code=code.replace('__'+k+'__',str(v).lower())
 lua=LuaRuntime();lua.execute("calls=0;open=false;markers={};print=function(...)markers[#markers+1]=table.concat({...},' ')end;Game={GetCurrentGameTurn=function()return 92 end,GetLocalPlayer=function()return -1 end};Players={[0]={IsHuman=function()return false end}};ContextPtr={IsHidden=function()return true end};DiplomacyManager={FindOpenSessionID=function()return 2 end,IsSessionIDOpen=function()return open end,GetSessionInfo=function()return {FromPlayer=2,ToPlayer=0}end,CloseSession=function()calls=calls+1 end};Close=function()error('hidden cosmetic view must not be called')end")
 lua.execute(code);assert lua.globals().calls==0 and 'SKIPPED session_closed'in lua.globals().markers[1];count+=1
 lua.execute('open=true');lua.execute(code);assert lua.globals().calls==1 and 'DISMISS_REQUESTED'in lua.globals().markers[3];count+=1
 return {'status':'PASS','fixtures':count}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--scratch',type=pathlib.Path);p.add_argument('--lua51-path',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path);args=p.parse_args()
 OfflineTests.scratch=args.scratch
 result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(OfflineTests))
 lua=lua_fixtures(args.lua51_path)
 report={'verified':result.wasSuccessful(),'python_fixtures':result.testsRun,'Lua51':lua,'native_connections':0,'native_full_game_validation':'PENDING; offline checks do not establish full-game reliability'}
 if args.output:args.output.write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(report));raise SystemExit(0 if result.wasSuccessful()else 1)
