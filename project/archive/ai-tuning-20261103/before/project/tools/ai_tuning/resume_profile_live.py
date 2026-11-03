"""Continue a preserved inactive profile boundary in the SAME native process.

Also supports a preserved existing finite operation, with an independent
active-source review. That path resumes its remaining budget without a second
activation, load, observer reset or replay. Uses the maintained controller and
installed mutation owner. No loading, hosting,
observer resets, economic requests, or replay of the already accepted source
cycle. Requires an exact source checkpoint plus full known-world/Gold/prefix
parity before the first new finite operation. Scope remains bounded at the explicitly selected original endpoint (150/200).
"""
import argparse,json,os,shutil,subprocess,sys,time,traceback
from pathlib import Path
import native_profile_test as p
ROOT=Path(__file__).resolve().parents[3]

def prepare(a):
 assert not a.output.exists();a.output.mkdir(parents=True)
 assert p.read(a.parent/'supervisor.json')['exit_code']==1
 for name in ('deployment','game-01','chain-metrics','research','builders','quarter-sites','exact-checkpoints','receipts','diagnostics','customer-forecast-controls','workshop-forecast-controls'):
  if(a.parent/name).exists():shutil.copytree(a.parent/name,a.output/name)
 for name in ('initialization.json','native-gameplay.sqlite','native-menu-configuration.json','initial-census.json','initial-receipts.json','original-preferences.json','host-issued.json','log-offsets.json','monitor-context.md','monitor.json','foundation-priority-controls.json','foundation-registration-controls.json','strategy-building-controls.json'):
  if(a.parent/name).exists():shutil.copy2(a.parent/name,a.output/name)
 init=p.read(a.output/'initialization.json');assert init['endpoint']==a.endpoint;init.update(live_resume_turn=a.turn,source_parent=str(a.parent),source_census='preserved partial active turn; not a completed outcome'if getattr(a,'active_target',0)else'original accepted same-process boundary; fresh parity readback');p.write(a.output/'initialization.json',init)
 p.write(a.output/'accepted-parent.json',dict(parent=str(a.parent),source_turn=a.turn,same_process=True,no_load=True,AI_replay=0,observer_prefixes_inherited_once=True,original_failure_preserved=True,existing_active_target=getattr(a,'active_target',0)or None))
 with(a.output/'monitor-context.md').open('a',encoding='utf-8')as f:f.write('\nCURRENT same-process source'+str(a.turn)+' continuation: read live-resume-validation and new exact owners. Read live-resume-validation for the reviewed diagnostic/controller source delta; gameplay/installed/RH unchanged; original failed artifacts preserved. No load/AIreplay/reconstruction/economicresend. An active source resumes its EXISTING remaining operation without a second activation; an inactive source starts the next finite operation. Controls source point is fresh corrected native readback, not original failed export. AllcurrentpinsFROZEN/exclusiveworkerTuner.\n')

 if getattr(a,'active_target',0):
  context=a.output/'monitor-context.md'
  context.write_text('CURRENT active-operation recovery at native'+str(a.turn)+'->'+str(a.active_target)+': prior owners exited1, same live Civ. Independent source review must match full known world/Gold/research/Builder snapshot before any standard exit-only conversation release. No load/rehost/AI replay/observer reset/financial resend/second activation. Installed gameplay and RH unchanged; only reviewed reusable controller recovery code differs. Earlier startup labels below are HISTORY. Read live-resume-validation and existing-operation-advance; dispatch is not native progress.\n\n'+context.read_text(encoding='utf-8'),encoding='utf-8')

def worker(a):
 c=p.adapter(a.controller_adapter);d=c.d;d.ROOT=a.output
 from full_game_controller.discovery import discover_contexts
 from full_game_controller.continuation import world_signature
 from full_game_controller.checkpoint import save_inactive_boundary
 from service_planner.boundary_bundle import capture
 oldsup=p.read(a.parent/'supervisor.json');oldjob=p.read(a.parent/'job-status.json')
 assert oldsup['exit_code']==1
 owners=(oldsup['supervisor_pid'],oldjob['worker_pid'])
 raw=d.ps('Get-CimInstance Win32_Process | Where-Object {$_.ProcessId -in @('+','.join(map(str,owners))+')} | Select-Object ProcessId | ConvertTo-Json -Compress');assert not raw.strip(),'Old owners still alive'
 identity=p.read(a.parent/'game-process.json');assert any(v['pid']==identity['pid']and v['created']==identity['created']for v in d.processes()),'Exact original native process required'
 expected=p.read(a.output/'deployment/expected-installed-manifest.json');assert p.manifest(d.INSTALLED)==expected
 active=getattr(a,'active_target',0)
 if active:
  review=p.read(a.active_source_review);war_peers=[int(row['from'])for row in review.get('native',{}).get('rows',[])if row.get('at_war')];assert all(0<x<64 for x in war_peers);assert review['verified']and review['original_owners_absent']and review['native_controls_issued']==0
  assert review['exact_native_identity']==identity
  assert review['source']['turn']==a.turn and review['source']['active']and active-a.turn==review['source']['remaining']and 0<active-a.turn<=5
  source=None
 else:
  source=p.read(a.parent/'exact-checkpoints'/f'turn-{a.turn:03d}.json');assert source['verified']and source['turn']==a.turn and p.sha(a.parent/'exact-checkpoints'/f'turn-{a.turn:03d}.Civ6Save')==source['sha256']
 oldpins=p.read(a.parent/'executed-source-pins.json');changes=[n for n,h in oldpins.items()if p.sha(Path(n))!=h]
 allowed=str(Path(__file__).with_name('profile_customer_forecast.lua').resolve())
 if active:
  assert set(changes)=={str(ROOT/'project/tools/ai_baseline/full_game_controller/controller.py')},('Only reviewed controller recovery source may change',changes)
 else:assert changes==[allowed],('Only the corrected read-only reader may change',changes)
 Controller=c.maintained.make_controller(c.full.Fresh,diagnostics=d,boundary_decision=c.b.boundary_decision,tuner_port=lambda:c.b.tuner.PORT,prepare_output=c.prepare_output,state_discovery=discover_contexts)
 r=Controller(a.output);r.seq=80000000;r.game_pid=identity['pid'];r.study_endpoint=a.endpoint;r.allow_one_more_turn=True;r.allow_observer_warning_dismissal=True;r.allow_observer_congress_review=True
 p.write(a.output/'game-process.json',identity);p.write(a.output/'worker-started.json',dict(pid=os.getpid(),same_native_process=True,no_load=True,time=time.time()))
 try:
  if active:
   phase=r.state_read('existing-source-before-reconciliation')
   assert all(phase[k]==review['source'][k]for k in ('turn','active','remaining','local_player','player0_human'))
  else:r.ready(a.turn,'live-source-before-reconciliation')
  receipts=p.parse(r.cmd(p.RECEIPTS,'CSC_AdjacencyGameplay','live-source-exact-receipts'),'CSC_PROFILE_RECEIPTS')
  reference_receipts=p.read(Path(review['review_root'])/'receipts.json')if active and review.get('review_root')else p.read(a.parent/'receipts'/f'turn-{a.turn:03d}.json')
  assert receipts==reference_receipts and not receipts['errors']and not receipts['pending']
  bundle=capture(r,a.output,p.write,a.turn)
  primary=a.parent/'failure-preserved-primary-current.json'if active else a.parent/'game-01'/f'turn-{a.turn:03d}.json'
  research=a.parent/'failure-preserved-research.json'if active else a.parent/'research'/f'turn-{a.turn:03d}.json'
  builders=a.parent/'failure-preserved-builders-current.json'if active else a.parent/'builders'/f'turn-{a.turn:03d}.json'
  assert world_signature(bundle['primary'])==world_signature(p.read(primary))
  assert bundle['research']==p.read(research)
  assert bundle['builders']['events']==p.read(builders)['events']
  if active:
   assert bundle['builders']==p.read(builders)
   for key,value in bundle.items():p.write(a.output/'active-source'/f'{key}.json',value)
  pins={n:p.sha(Path(n))for n in oldpins};pins[str(Path(__file__).resolve())]=p.sha(Path(__file__))
  if active:
   for resource in(ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'):pins[str(resource)]=p.sha(resource)
  for i,n in enumerate(pins):dest=a.output/'source-version'/f'{i:04d}-{Path(n).name}';dest.parent.mkdir(exist_ok=True);shutil.copy2(n,dest)
  p.write(a.output/'executed-source-pins.json',pins)
  proof=dict(verified=True,source_turn=a.turn,same_native_process=True,native_pid=r.game_pid,no_load=True,no_new_world=True,AI_replay=0,world_known_fact_parity=True,Gold_and_closed_receipts_equal=True,research_prefix_rows=len(bundle['research']['history']),Builder_event_prefix_equal=True,observers_reset=False,installed_gameplay_and_RH_unchanged=True,changed_diagnostic_source=changes,exact_source_save_sha256=source['sha256']if source else None,existing_active_target=active or None,no_second_activation=True,source_census='preserved partial active turn; not a completed outcome'if active else'inactive accepted boundary',nonBuilder_full_unit_reference='UNOBSERVED; no full exact unit-parity claim')
  p.write(a.output/'live-resume-validation.json',proof)
  init=p.read(a.output/'initialization.json')
  if init.get('customer_forecast_controls')and not active:p.capture_customer_forecast(r,a.output,a.turn)
  if init.get('workshop_forecast_controls')and not active:p.capture_workshop_forecast(r,a.output,a.turn)
  inherited=p.read(a.parent/'independent-startup-confirmation.json');inherited.update(inherited_initial_startup=str(a.parent/'independent-startup-confirmation.json'),source_startup_native_turn=inherited['actual_native_turn'],actual_native_turn=a.turn,pins=len(pins),source_resume_proof=str(a.output/'live-resume-validation.json'));p.write(a.output/'independent-startup-confirmation.json',inherited)
  p.write(a.output/'job-status.json',dict(status='running',worker_pid=os.getpid(),native_pid=r.game_pid,endpoint=a.endpoint))
  r.last_interval_turn=a.turn
  for turn in range(a.turn+5,a.endpoint+1,5):
   if active and turn==active:r.resume_active(turn)
   else:r.play(turn)
   extra=''
   if active and turn==active and war_peers:
    extra="\nlocal wars={};for _,pid in ipairs({"+','.join(map(str,war_peers))+"})do wars[#wars+1]={player=pid,at_war=Players[0]:GetDiplomacy():IsAtWarWith(pid)}end;print('CSC_PROFILE_WAR_AFTER='..json({turn=Game.GetCurrentGameTurn(),wars=wars}))"
   raw=r.cmd(p.RECEIPTS+extra,'CSC_AdjacencyGameplay','receipts-'+str(turn))
   value=p.parse(raw,'CSC_PROFILE_RECEIPTS');assert value['turn']==turn and not value['errors']and not value['pending']
   if active and turn==active:
    after=p.parse(raw,'CSC_PROFILE_WAR_AFTER')if war_peers else None;assert after is None or(after['turn']==turn and all(row['at_war']for row in after['wars']))
    p.write(a.output/'existing-operation-advance.json',dict(verified=True,source_turn=a.turn,actual_native_turn=turn,war_states_after=after,no_load=True,second_activation=False,AI_replay=0,unchanged_installed_gameplay=True))
   p.write(a.output/'receipts'/f'turn-{turn:03d}.json',value)
   assert all(v.get('last_cycle')!=turn-1 for v in value['players']if v['player']==0),'Observer economic cycle detected'
   if turn%25==0 or turn==a.endpoint:
    bundle=capture(r,a.output,p.write,turn)
    for key,folder in (('primary','game-01'),('chain','chain-metrics'),('research','research'),('builders','builders'),('quarters','quarter-sites')):p.write(a.output/folder/f'turn-{turn:03d}.json',bundle[key])
    d.checkpoint('outcome-'+str(turn))
    saved=save_inactive_boundary(r,turn=turn,name='CSC_RH5_T'+str(turn),native_directory=d.SAVES,archive=a.output/'exact-checkpoints'/f'turn-{turn:03d}.Civ6Save');p.write(a.output/'exact-checkpoints'/f'turn-{turn:03d}.json',saved)
    if init.get('customer_forecast_controls'):p.capture_customer_forecast(r,a.output,turn)
    if init.get('workshop_forecast_controls'):p.capture_workshop_forecast(r,a.output,turn)
    if init.get('workshop_forecast_controls'):p.capture_workshop_forecast(r,a.output,turn)
    assert p.manifest(d.INSTALLED)==expected and all(p.sha(Path(n))==h for n,h in pins.items())
   p.write(a.output/'live-status.json',dict(turn=turn,endpoint=a.endpoint,worker_pid=os.getpid(),native_pid=r.game_pid,totals=value['totals'],pending=value['pending'],errors=value['errors'],time=time.time()))
  r.cmd('Events.ExitToMainMenu();','PlotInfo','normal-menu-after150',check=False);r.wait('MainMenu',120);p.restore_preferences(r,a.output)
  p.write(a.output/'exit-issued.json',dict(once=True,pid=r.game_pid,time=time.time()))
  try:r.cmd('assert(type(ExitOK)=="function");ExitOK();','FrontEndPopup','supported-exit-after150',check=False)
  except Exception as e:p.write(a.output/'exit-ack-warning.json',dict(error=str(e),no_resend=True))
  for _ in range(45):
   if not[x for x in d.processes()if x['name'].startswith('CivilizationVI')]:break
   time.sleep(1)
  else:raise RuntimeError('Native did not exit; preserve runtime')
  p.restore_package(c,a.output);p.write(a.output/'job-status.json',dict(status='complete',native_endpoint=a.endpoint,exit_code=0,time=time.time()))
 except BaseException as e:
  p.write(a.output/'failure.json',dict(error=str(e),traceback=traceback.format_exc(),no_native_or_economic_resend=True))
  try:r.preserve_telemetry();d.checkpoint('failure-preserved')
  except Exception as x:p.write(a.output/'preservation-warning.json',dict(error=str(x)))
  if isinstance(e,c.core.ObserverEliminated):
   try:p.close_eliminated_observer(c,r,a.output)
   except BaseException as cleanup_error:p.write(a.output/'observer-cleanup-warning.json',dict(error=str(cleanup_error),original_error=str(e)))
  p.write(a.output/'job-status.json',dict(status='attention',worker_pid=os.getpid(),native_pid=r.game_pid,endpoint=a.endpoint,error=str(e)));raise

def argv(a,mode):return[sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),mode,'--parent',str(a.parent),'--output',str(a.output),'--turn',str(a.turn),'--endpoint',str(a.endpoint),'--controller-adapter',str(a.controller_adapter),'--campaign',str(a.campaign),'--active-target',str(getattr(a,'active_target',0)),'--active-source-review',str(getattr(a,'active_source_review',''))]
def supervise(a):
 with(a.output/'worker.stdout.log').open('w')as stdout,(a.output/'worker.stderr.log').open('w')as stderr:child=subprocess.Popen(argv(a,'worker'),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
 p.write(a.output/'supervisor.json',dict(supervisor_pid=os.getpid(),worker_pid=child.pid,status='running',endpoint=a.endpoint));code=child.wait();p.write(a.output/'supervisor.json',dict(supervisor_pid=os.getpid(),worker_pid=child.pid,status='complete'if code==0 else'attention',exit_code=code,endpoint=a.endpoint))
def main():
 q=argparse.ArgumentParser();q.add_argument('mode',choices=['launch','supervise','worker']);q.add_argument('--parent',type=Path,required=True);q.add_argument('--output',type=Path,required=True);q.add_argument('--turn',type=int,required=True);q.add_argument('--controller-adapter',type=Path,required=True);q.add_argument('--campaign',type=Path,required=True);q.add_argument('--endpoint',type=int,default=150);q.add_argument('--active-target',type=int,default=0);q.add_argument('--active-source-review',type=Path,default=None);a=q.parse_args();assert a.endpoint in(150,200);assert (a.turn in range(5,a.endpoint,5)and a.active_target==a.turn+5 and a.active_source_review)if a.active_target else a.turn in (25,50,75,100,125)
 if a.mode=='worker':worker(a);return
 if a.mode=='supervise':supervise(a);return
 prepare(a)
 with(a.output/'job.stdout.log').open('w')as stdout,(a.output/'job.stderr.log').open('w')as stderr:child=subprocess.Popen(argv(a,'supervise'),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
 old=p.read(a.campaign/'active-run.json');old.update(root=str(a.output),status='reconciling-live-source',supervisor_pid=child.pid,phase='same-world-existing-finite-operation-recovery'if a.active_target else'customer-forecast-v2-reader-corrected-same-world',parity_verified=False);p.write(a.campaign/'active-run.json',old)
 print(json.dumps(dict(supervisor_pid=child.pid,root=str(a.output),native_advance='PENDING')))
if __name__=='__main__':main()
