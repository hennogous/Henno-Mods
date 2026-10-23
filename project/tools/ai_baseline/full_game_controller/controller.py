"""Bounded five-turn autoplay/telemetry mixin, independent of any trial folder.

The caller supplies its existing native interfaces, diagnostics and boundary
decision. This module does not launch Civ, host worlds, choose seeds, install
assets, place foundations or implement restart policy.
"""
import json,os,re,time
from pathlib import Path
from .transport import receive_command,MissingAcknowledgment,NativeLuaFailure
RESOURCE_ROOT=Path(__file__).resolve().parent
HANDOFF='print("CSC_SHARED_STATE",Game.GetCurrentGameTurn(),AutoplayManager.IsActive(),AutoplayManager.GetTurns(),Game.GetLocalPlayer(),Players[0]:IsHuman());'
GUARD=(RESOURCE_ROOT/'disaster_playback.lua').read_text(encoding='utf-8')
DIPLOMACY_GUARD=(RESOURCE_ROOT/'diplomacy_playback.lua').read_text(encoding='utf-8')
WONDER_GUARD=(RESOURCE_ROOT/'wonder_playback.lua').read_text(encoding='utf-8')

def make_controller(base_class,*,diagnostics,boundary_decision,tuner_port,prepare_output=None,state_discovery=None):
 """Compose with validated capture/config/planner interfaces; no native work here.

 base_class must provide __init__(output), states(), state/required_state/seq,
 and its experiment-specific config/capture/scan/Menu/restore methods. Diagnostics
 supplies write(path,value), sha(path), journal(event,**fields), checkpoint(label).
 boundary_decision(turn,target,inactive_count) returns ("wait"|"done",new_count).
 prepare_output(output) optionally binds legacy diagnostic roots before init.
 """
 return type('Controller',(FullGameController,base_class),{
  'diagnostics':diagnostics,'boundary_decision':staticmethod(boundary_decision),
  'tuner_port':staticmethod(tuner_port)if callable(tuner_port)else tuner_port,'prepare_output':staticmethod(prepare_output or(lambda out:None)),
  'state_discovery':staticmethod(state_discovery)if state_discovery else None})

PASSIVE_OBSERVER_STATEMENTS=frozenset(('WARNING_TOO_MANY_TROOPS_NEAR_ME','DIPLOMATIC_KUDO','DIPLOMATIC_WARNING','DIPLOMATIC_HIDDEN_AGENDA_KUDO','DIPLOMATIC_HIDDEN_AGENDA_WARNING'))

class SourceUpdateHandoff(Exception):
 """Validated read-only ownership handoff, not native failure."""

class FullGameController:
 def __init__(self,out):
  out=Path(out).resolve();self.prepare_output(out)
  super().__init__(out);self.root=out;self.last_interval_turn=1
  self.session_token='CSC_FULL_ACK_'+str(os.getpid())+'_'
 def states(self):
  if self.state_discovery is None:return super().states()
  # Fresh discovery for EVERY command; only its fixed receive delay is removed.
  # Keep the existing bounded read-only discovery retry when simulation is busy.
  # No Lua command has been transmitted at this point.
  for attempt in range(3):
   try:
    self.discovery_port,self.state=self.state_discovery(self.required_state)
    return self.state
   except RuntimeError as error:
    if str(error)!='No responsive tuner states'or attempt==2:raise
    self.diagnostics.journal('readonly-state-discovery-retry',attempt=attempt+1,no_command_sent=True)
    time.sleep(2)
 def publish_active(self,value):
  # Windows readers can briefly deny atomic replacement. This status index is
  # optional: the fsynced command journal and unique command/reply files remain
  # authoritative. Retry only metadata I/O; never repeat a native command.
  for attempt in range(5):
   try:
    self.diagnostics.write(self.root/'active-command.json',value)
    return True
   except PermissionError as error:
    if attempt<4:time.sleep(.1)
    else:self.diagnostics.journal('active-command-metadata-warning',number=value.get('number'),phase=value.get('phase'),error=str(error),no_native_command_replayed=True)
  return False
 def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
  # Exactly one send. A missing ACK is ambiguous for controls and mutations;
  # caller must inspect postconditions or fail, never blindly replay them.
  self.seq+=1;n=self.seq;token=self.session_token+str(n)
  artifact_label=re.sub(r'[^A-Za-z0-9_-]','_',str(label))[:64]or'command'
  path=self.root/'pending-commands'/('%04d-%s.lua'%(n,artifact_label));path.parent.mkdir(exist_ok=True);path.write_text(code,encoding='utf-8')
  record={'number':n,'label':label,'artifact_label':artifact_label,'state':state,'lua_sha256':self.diagnostics.sha(path),'source':str(path),'started_unix':time.time(),'sent_at_most_once':True,'ack_token':token}
  self.publish_active(dict(record,phase='discovering'))
  previous=self.required_state;self.required_state=state
  text=''
  try:
   self.states();assert state in self.state,'Required native context unavailable: '+state
   record['discovery_seconds']=time.time()-record['started_unix']
   port=self.discovery_port if self.state_discovery else(self.tuner_port()if callable(self.tuner_port)else self.tuner_port)
   record['port']=port
   self.diagnostics.journal('command-begin',**record) # fsync BEFORE transmission.
   self.publish_active(dict(record,phase='issuing',port=port))
   try:text,ack=receive_command(code,self.state[state],token,port,timeout=max(15,float(wait)),check=check)
   except(MissingAcknowledgment,NativeLuaFailure)as error:text=error.text;raise
   evidence=self.root/'commands'/('%04d-%s'%(n,artifact_label));evidence.parent.mkdir(exist_ok=True)
   evidence.with_suffix('.lua').write_text(code,encoding='utf-8');evidence.with_suffix('.txt').write_text(text,encoding='utf-8')
   phase='acknowledged'if ack else'sent-unconfirmed-requires-postcondition'
   self.publish_active(dict(record,phase=phase,completed_unix=time.time(),port=port))
   self.diagnostics.journal('command-end',number=n,label=label,acknowledged=ack,reply_bytes=len(text));return text
  except BaseException as error:
   evidence=self.root/'commands'/('%04d-%s'%(n,artifact_label));evidence.parent.mkdir(exist_ok=True)
   evidence.with_suffix('.lua').write_text(code,encoding='utf-8');evidence.with_suffix('.txt').write_text(text,encoding='utf-8')
   self.publish_active(dict(record,phase='exception',error=str(error),completed_unix=time.time()))
   self.diagnostics.journal('command-error',number=n,label=label,error=str(error));raise
  finally:self.required_state=previous
 def handoff_for_update(self,turn,details=None):
  """Archive an inactive boundary for a new source owner; no Menu or controls.

  Caller must exit after this receipt and independently verify owner absence
  before changing source. capture() must be its validated read-only observer.
  """
  path=self.root/'source-update-handoff.json'
  assert not path.exists(),'Never replace an archived source handoff'
  self.ready(turn,'source-update-handoff')
  proof=self.state_read('source-update-proof')
  assert proof['turn']==turn and not proof['active']and proof['local_player']==0 and proof['player0_human'],proof
  self.preserve_telemetry();self.capture('source-update-handoff')
  self.diagnostics.checkpoint('source-update-handoff-'+str(turn))
  receipt={'verified':True,'native_turn':turn,'native_pid':self.game_pid,
           'worker_pid':os.getpid(),'proof':proof,'details':details or {},
           'native_controls_issued':0,'world_reloaded':False,'owner_exit_required':True}
  self.diagnostics.journal('source-update-handoff',turn=turn,native_pid=self.game_pid,no_native_control=True)
  self.diagnostics.write(path,receipt)
  return receipt
 def handoff_active_for_update(self,target):
  """Archive the existing finite operation and yield ownership without controls."""
  path=self.root/'source-update-handoff.json'
  assert not path.exists(),'Never replace an ownership receipt'
  proof=self.state_read('active-source-update-proof')
  assert proof['active']and proof['local_player']==-1 and not proof['player0_human']and target-proof['turn']==proof['remaining']and 0<proof['remaining']<=5,proof
  self.preserve_telemetry();self.capture('active-source-update-handoff');self.capture_blocker(target)
  final=self.state_read('active-source-update-final')
  if not all(proof[k]==final[k]for k in('turn','active','remaining','local_player','player0_human')):
   self.diagnostics.journal('active-source-update-deferred',proof=proof,final=final,no_control=True)
   return {'verified':False,'continue_owner':True,'reason':'Native phase moved; finish current operation and hand off inactive'}
  self.diagnostics.checkpoint('active-source-update-handoff-'+str(proof['turn']))
  receipt={'verified':True,'kind':'active-finite-operation','native_turn':proof['turn'],'target':target,
           'native_pid':self.game_pid,'worker_pid':os.getpid(),'proof':final,
           'native_controls_issued':0,'world_reloaded':False,'second_activation':False,'owner_exit_required':True}
  self.diagnostics.journal('active-source-update-handoff',**receipt)
  self.diagnostics.write(path,receipt)
  return receipt
 def state_read(self,label):
  for attempt in range(3):
   try:
    raw=self.cmd(HANDOFF,'GameCore_Tuner',label+'-'+str(attempt),wait=1)
    t,a,n,p,h=re.findall(r'CSC_SHARED_STATE\s+(\d+)\s+(true|false)\s+(-?\d+)\s+(-?\d+)\s+(true|false)',raw)[-1]
    return {'turn':int(t),'active':a=='true','remaining':int(n),'local_player':int(p),'player0_human':h=='true','time':time.time()}
   except(MissingAcknowledgment,OSError,EOFError,IndexError):
    if attempt==2:raise
    self.diagnostics.journal('readonly-state-query-retry',label=label,attempt=attempt+1,no_control_replayed=True);time.sleep(2)
 def ready(self,expected,label):
  rows=[];good=0
  for _ in range(12):
   row=self.state_read(label);rows.append(row)
   self.diagnostics.write(self.root/'handoff-readbacks'/(label+'.json'),{'expected_turn':expected,'samples':rows,'read_only':True})
   assert row['turn']==expected,('Unexpected native handoff clock',expected,row)
   good=good+1 if not row['active']and row['local_player']==0 and row['player0_human']else 0
   if good==3:return
   time.sleep(.15) # Three separate native replies, without two-second idle gaps.
  raise RuntimeError('Native handoff did not settle within bounded read-only checks')
 def release_disaster(self,target):
  # Known presentation contexts are independent; absence of one cannot skip another.
  self.states()
  for context,template,marker in [('NaturalDisasterPopup',GUARD,'CSC_DISASTER_RELEASE_REQUESTED'),('DiplomacyActionView',DIPLOMACY_GUARD,'CSC_DIPLOMACY_PLAYBACK_RELEASE_REQUESTED'),('WonderBuiltPopup',WONDER_GUARD,'CSC_WONDER_PLAYBACK_RELEASE_REQUESTED')]:
   if context not in self.state:continue
   proof=self.state_read('playback-core-proof-'+context)
   if not proof['active']or not(0<proof['remaining']<=5)or target-proof['turn']!=proof['remaining']:continue
   if context in ('DiplomacyActionView','WonderBuiltPopup')and(proof['local_player']!=-1 or proof['player0_human']):continue
   code=template
   for name,value in {'CORE_TURN':proof['turn'],'TARGET_TURN':target,'CORE_ACTIVE':proof['active'],'CORE_LOCAL':proof['local_player'],'CORE_HUMAN':proof['player0_human']}.items():code=code.replace('__'+name+'__',str(value).lower())
   raw=self.cmd(code,context,'guarded-playback-'+context+'-'+str(proof['turn']),wait=1)
   row={'context':context,'core_proof':proof,'target':target,'raw':raw,'requested':marker in raw,'gameplay_response_submitted':False,'time':time.time()}
   with(self.root/'playback-recoveries.ndjson').open('a',encoding='utf-8')as f:f.write(json.dumps(row)+'\n')
   if row['requested']:self.diagnostics.checkpoint('playback-release-'+context+'-'+str(self.seq))
 def capture_blocker(self,target):
  # Capture native session/context state BEFORE any cosmetic view teardown.
  # Diagnostic failures do not trigger controls or hide the original stall.
  try:
   self.states();proof=self.state_read('blocker-core-proof')
   for context in ('DiplomacyActionView','WonderBuiltPopup','NaturalDisasterPopup'):
    if context not in self.state:continue
    raw=self.cmd((RESOURCE_ROOT/'blocker_diagnostics.lua').read_text(encoding='utf-8'),context,'blocker-'+context)
    match=re.search(r'CSC_BLOCKER_DIAGNOSTICS=([^\r\n]+)',raw)
    value=json.loads(match[1])if match else {'raw':raw}
    self.diagnostics.write(self.root/'blocker-diagnostics'/(str(self.seq)+'-'+context+'.json'),{'core':proof,'target':target,'context':context,'native':value,'read_only':True})
  except Exception as error:self.diagnostics.write(self.root/'blocker-diagnostic-warning.json',{'error':str(error),'no_control_replayed':True})
 def dismiss_observer_warning(self,target):
  if not getattr(self,'allow_observer_warning_dismissal',False):return
  proof=self.state_read('warning-dismiss-core-proof')
  if not proof['active']or proof['local_player']!=-1 or proof['player0_human']or target-proof['turn']!=proof['remaining']or not(0<proof['remaining']<=5):return
  # Native diplomacy CSV identifies the actual statement/session, not a guess
  # based on a visible leader. Only the reviewed troop warning and exit-only agenda kudos/warnings
  # are supported. Shipped KUDO_EXIT/WARNING_EXIT expose CHOICE_EXIT only.
  # No response, promise or deal is selected.
  import csv
  log=self.diagnostics.USER/'Logs/DiplomacyManager.csv'
  if not log.exists():return
  warning=None;seen_from=set()
  for row in reversed(list(csv.reader(log.read_text(encoding='utf-8-sig',errors='replace').splitlines()))):
   row=[v.strip()for v in row]
   if len(row)<5 or row[0]!=str(proof['turn'])or row[1]not in('1','2','3','4','5')or row[2]!='0':continue
   if row[1]in seen_from:continue
   seen_from.add(row[1]) # Latest message from this participant wins; never fall back past a deal/demand.
   if row[4]in PASSIVE_OBSERVER_STATEMENTS:
    warning={'turn':int(row[0]),'from':int(row[1]),'to':0,'initiator_raw':row[3],'statement':row[4]};break
  if warning is None:return
  # CSV column4 is Initiator, not a session ID. Lua resolves the native open
  # session for the log-verified participants and checks its identity.
  key=(self.game_pid,proof['turn'],warning['from'],warning['statement'])
  if not hasattr(self,'warning_dismissals'):self.warning_dismissals=set()
  if key in self.warning_dismissals:return
  if not hasattr(self,'warning_guard_checks'):self.warning_guard_checks={}
  checks=self.warning_guard_checks.get(key,0)
  if checks>=4:return # At most four fresh checks; normal stall cadence separates them.
  self.states()
  if 'DiplomacyActionView'not in self.state:return
  code=(RESOURCE_ROOT/'session_dismissal.lua').read_text(encoding='utf-8')
  for name,value in {'FROM':warning['from'],'CORE_TURN':proof['turn'],'TARGET_TURN':target,'CORE_ACTIVE':proof['active'],'CORE_LOCAL':proof['local_player'],'CORE_HUMAN':proof['player0_human']}.items():code=code.replace('__'+name+'__',str(value).lower())
  self.diagnostics.journal('observer-warning-dismissal-begin',warning=warning,core=proof,native_pid=self.game_pid,no_response_selected=True)
  # Reserve before transmission: any transport/Lua ambiguity remains one-shot.
  self.warning_dismissals.add(key);self.warning_guard_checks[key]=checks+1
  raw=self.cmd(code,'DiplomacyActionView','dismiss-observer-warning-from-'+str(warning['from']))
  skipped=bool(re.search(r'CSC_OBSERVER_WARNING_DISMISS_SKIPPED\s+(no_session|core_phase|ui_clock|ui_control|session_closed|session_changed|participants)',raw))
  if skipped and 'CSC_OBSERVER_WARNING_DISMISS_BEGIN'not in raw and 'CSC_OBSERVER_WARNING_DISMISS_REQUESTED'not in raw:
   self.warning_dismissals.remove(key) # ACK proves the Lua guard returned before CloseSession.
  self.diagnostics.journal('observer-warning-guard-result',key=key,check=checks+1,explicit_skip=skipped,may_recheck=key not in self.warning_dismissals)
  self.diagnostics.write(self.root/'session-dismissals'/(str(self.seq)+'.json'),{'warning':warning,'core':proof,'raw':raw,'requested':'CSC_OBSERVER_WARNING_DISMISS_REQUESTED'in raw,'intervention':'standard conversation dismissal; no AddResponse/statement/turn change'})
 def continue_after_victory(self,target,proof):
  """Opt-in fixed endpoint: shipped One More Turn, then remaining budget only.

  A victory can end a finite operation early. This is a separately journaled
  continuation, not a resend: require visible/enabled native UI and a winner,
  then reuse its exact positive remaining budget without SetTurns or replay.
  """
  if not getattr(self,'allow_one_more_turn',False):return False
  endpoint=getattr(self,'study_endpoint',0)
  if proof['active']or not(0<target-proof['turn']==proof['remaining']<=5)or target>endpoint:return False
  if proof['local_player']!=0 or not proof['player0_human']:return False
  if not hasattr(self,'endgame_continuations'):self.endgame_continuations=set()
  key=(proof['turn'],target)
  if key in self.endgame_continuations:return False
  self.states()
  if 'EndGameMenu'not in self.state:return False
  code=(RESOURCE_ROOT/'endgame_playback.lua').read_text(encoding='utf-8')
  for name,value in {'CORE_ACTIVE':proof['active'],'CORE_TURN':proof['turn'],'TARGET':target,'ENDPOINT':endpoint,'REMAINING':proof['remaining'],'CORE_LOCAL':proof['local_player'],'CORE_HUMAN':proof['player0_human']}.items():code=code.replace('__'+name+'__',str(value).lower())
  # Reserve before transmission. Only an explicit guard skip proves that no
  # click occurred and allows a later fresh presentation check.
  self.endgame_continuations.add(key)
  raw=self.cmd(code,'EndGameMenu','one-more-turn-'+str(target))
  requested='CSC_ENDGAME_CONTINUE_REQUESTED'in raw
  self.diagnostics.write(self.root/'endgame-continuations'/f'{target}.json',dict(core=proof,target=target,raw=raw,requested=requested,shipped_one_more_turn=True))
  if not requested:
   if 'CSC_ENDGAME_SKIP'in raw and 'CSC_ENDGAME_CONTINUE_BEGIN'not in raw:self.endgame_continuations.remove(key)
   return False
  after=self.state_read('after-one-more-turn')
  assert proof['turn']<=after['turn']<=target,('One More Turn clock changed unexpectedly',after)
  if after['turn']==target or after['active']:return True
  assert not after['active']and after['local_player']==0 and after['player0_human']and after['remaining']==target-after['turn']and after['remaining']>0,('Remaining operation no longer proven',after)
  self.cmd('assert(not AutoplayManager.IsActive()and Game.GetCurrentGameTurn()=='+str(after['turn'])+' and AutoplayManager.GetTurns()=='+str(after['remaining'])+');AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);print("CSC_ENDGAME_RESUMED_REMAINING",AutoplayManager.GetTurns());','GameCore_Tuner','resume-remaining-after-victory-'+str(target))
  return True
 def resume_active(self,target):
  proof=self.state_read('existing-finite-operation')
  assert proof['active']and target-proof['turn']==proof['remaining']and 0<proof['remaining']<=5,proof
  self.diagnostics.write(self.root/'existing-operation.json',dict(proof,target=target,no_second_activation=True))
  self.capture_blocker(target);self.dismiss_observer_warning(target)
  return self._await_target(target)
 def play(self,target):
  self.ready(self.last_interval_turn,'before-'+str(target))
  self.cmd('Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetTurns('+str(target)+'-Game.GetCurrentGameTurn());AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);print("CSC_DIAG_AUTOPLAY",Game.GetCurrentGameTurn(),AutoplayManager.GetTurns(),AutoplayManager.IsActive());','GameCore_Tuner','autoplay-'+str(target),wait=2)
  return self._await_target(target)
 def _await_target(self,target):
  deadline=time.monotonic()+1800;last=None;changed=time.monotonic();release=0;inactive=0
  while time.monotonic()<deadline:
   time.sleep(.5 if last is None else 1) # Poll state only; never resend activation.
   if(self.root/'native-fault-signal.json').exists():raise RuntimeError('Watchdog observed native fault')
   row=self.state_read('progress');turn=row['turn']
   if turn!=last:last=turn;changed=time.monotonic()
   self.diagnostics.write(self.root/'live-status.json',dict(row,target=target,endpoint=250,worker_pid=os.getpid()))
   request=self.root/'source-update-request.json'
   if request.exists()and row['active']and 0<row['remaining']<=5 and target-turn==row['remaining']and row['local_player']==-1 and not row['player0_human']and json.loads(request.read_text(encoding='utf-8-sig')).get('allow_active_handoff'):
    if getattr(self,'active_handoff_deferred_target',None)!=target:
     receipt=self.handoff_active_for_update(target)
     if receipt['verified']:raise SourceUpdateHandoff('Validated live-operation handoff; exit current owner')
     self.active_handoff_deferred_target=target # Native progress is normal; let the caller hand off inactive.
   if not row['active']:
    if self.continue_after_victory(target,row):inactive=0;changed=time.monotonic();continue
    action,inactive=self.boundary_decision(turn,target,inactive)
    if action=='done':break
   if turn>target:raise RuntimeError('Native autoplay overrun')
   if time.monotonic()-changed>35 and time.monotonic()-release>35:self.capture_blocker(target);self.dismiss_observer_warning(target);self.release_disaster(target);release=time.monotonic()
   if time.monotonic()-changed>600:raise RuntimeError('Native ten-minute turn stall')
  else:raise TimeoutError('Thirty-minute native interval bound')
  self.ready(target,'after-'+str(target));self.last_interval_turn=target
 def snapshot(self,i,target):
  raw=self.cmd('CSCBASE.snapshot('+str(target)+');','CSC_AdjacencyGameplay','primary-'+str(target),wait=4)
  value=json.loads(re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)',raw)[1]);assert value['turn']==target
  self.diagnostics.write(self.root/'game-01'/('turn-%03d.json'%target),value);return value
 def supplemental(self,label):
  raw=self.cmd('CSC_SERIES_RESEARCH.Export();','CSC_AdjacencyGameplay','research-'+label,wait=3)
  value=json.loads(re.search(r'CSC_SERIES_RESEARCH=([^\r\n]+)',raw)[1]);assert not value['errors']
  self.diagnostics.write(self.root/'research-latest.json',value);return value
 def preserve_telemetry(self):
  # Best effort BEFORE Menu destroys Lua observer state. Independent failures
  # are recorded so one unavailable export does not suppress all other evidence.
  self.states()
  if'CSC_AdjacencyGameplay'not in self.state:return
  for name,code,pattern in[
   ('research','if CSC_SERIES_RESEARCH then CSC_SERIES_RESEARCH.Export()end;',r'CSC_SERIES_RESEARCH=([^\r\n]+)'),
   ('primary-current','if CSCBASE then CSCBASE.snapshot(Game.GetCurrentGameTurn())end;',r'CSCBASE_SNAPSHOT=([^\r\n]+)'),
   ('builders-current','if CSC_BUILDERS then CSC_BUILDERS.Export(Game.GetCurrentGameTurn())end;',r'CSC_BUILDERS_SNAPSHOT=([^\r\n]+)')]:
   try:
    raw=self.cmd(code,'CSC_AdjacencyGameplay','failure-preserve-'+name,wait=3);match=re.search(pattern,raw)
    if match:self.diagnostics.write(self.root/('failure-preserved-'+name+'.json'),json.loads(match[1]))
   except Exception as error:self.diagnostics.write(self.root/('failure-preserve-'+name+'-warning.json'),{'error':str(error)})
