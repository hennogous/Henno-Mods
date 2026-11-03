"""Run only the two predeclared remaining references, with audited hand-offs.

No native transport is implemented here. Each game is owned exclusively by the
maintained profile worker and full_game_controller, and is bounded at150.
"""
import argparse,json,os,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');tmp.replace(p)
def run_checked(args,log):
 value=subprocess.run(args,capture_output=True,text=True);log.write_text(value.stdout+value.stderr,encoding='utf-8');assert value.returncode==0,value.stdout+value.stderr;return value
def series(a):
 P=a.campaign;reference=a.reference;py=sys.executable
 assert read(reference/'independent-audit.json')['verified_observed_contracts']
 status=dict(pid=os.getpid(),scope='fixed references B and C only; no retries/rerolls',arms=[],status='starting',native_transport='none; maintained worker only')
 if a.start_at=='C':
  prior=read(a.accepted_B/'independent-audit.json');assert prior['verified_observed_contracts']and prior['native_endpoint']==150
  assert read(a.accepted_B/'job-status.json')['status']=='complete'and read(a.accepted_B/'supervisor.json')['exit_code']==0
  status['arms'].append(dict(name='B',root=str(a.accepted_B),native150=True,audited=True,same_process_recovery=True))
 write(P/'reference-series-status.json',status)
 installed=Path(read(reference/'deployment/deployment.json')['installed'])
 try:
  arms=[('B',830102,940104),('C',830203,940207)]
  if a.start_at=='C':arms=arms[1:]
  for name,map_seed,game_seed in arms:
   R=P/('basic-'+name)/'run-01';assert not R.exists(),'Never overwrite or reroll an earlier arm';R.mkdir(parents=True)
   run_checked([py,'-B','-X','utf8',str(ROOT/'project/tools/ai_tuning/deploy_frozen_reference.py'),'--reference',str(reference),'--output',str(R/'deployment'),'--installed',str(installed)],R/'prepare.log')
   context=f'''Frozen CSC-only BASIC reference{name}, seed{map_seed}/{game_seed}, endpoint150.
Exact tested AI runtime of Basic-A staged from its archived3AI deltas, guarded
by complete current/pretest manifest equality. No obsolete510/517 archives/art
rollback. RH must be disabled, both expansions/resourcepass/assistance/subsidiesOn.
Same roster/settings, no tuning changes. New read-only completion observer and
full initial census improve coverage without production/economic commands.
Reference-series process {os.getpid()} owns audited B->C dispatch; do NOT launch
another game while it is live. Native worker exclusivelyTuner; all executed
sources/runtime/RH files frozen. No competingclient/UI/sourceedits/ComputerUse/
subagents.15min actual updates. A completed; C follows ONLY after B complete150,
independent audit, current pretestpackage/prefs restoration/allCivabsent.
Any failure halts series with artifacts preserved, no auto worldretry. Recovery
authorized preserve/reconcile/neverresendambiguousfinance. Goal remainsACTIVE
after references for CSC-only RH improvements and complete parity gates.
Source/runtime authority: reference-runtime.json + initial proof + source pins.
Actual Service payments UNOBSERVED; flags/links nottransactions. No forced
production/research/building/improvement/unit grants. Installed host solemutator,
quoted paidassignment notnativeAI PURCHASE. Light outcomes25+150; completion
observations record nativeIsComplete with city/site identity, not exact eventtime.
'''
   (R/'monitor-context.md').write_text(context,encoding='utf-8');write(R/'monitor.json',dict(automation_id='csc-rh5-profile-to-turn-150',status='ACTIVE'))
   write(R/'reference-runtime.json',dict(verified=True,reference=str(reference),runtime_exact=True,only_measurement_driver_changed=True,profile='BASIC',map_seed=map_seed,game_seed=game_seed))
   args=[py,'-B','-X','utf8',str(ROOT/'project/tools/ai_tuning/native_profile_test.py'),'supervise','--output',str(R),'--controller-adapter',str(a.controller_adapter),'--rh-package',str(a.rh_package),'--endpoint','150','--profile','BASIC','--map-seed',str(map_seed),'--game-seed',str(game_seed)]
   with(R/'job.stdout.log').open('w')as stdout,(R/'job.stderr.log').open('w')as stderr:
    proc=subprocess.Popen(args,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
   write(P/'active-run.json',dict(root=str(R),status='starting',profile='BASIC',phase='frozen-reference-'+name,supervisor_pid=proc.pid,series_pid=os.getpid(),endpoint=150,automation_id='csc-rh5-profile-to-turn-150',plan=str(P/'plan.md'),parity_verified=False,time=time.time()))
   status.update(status='waiting-for-specific-supervisor',current=name,root=str(R),supervisor_pid=proc.pid);write(P/'reference-series-status.json',status)
   code=proc.wait() # Background process handle wait, no model polling loop.
   sup=read(R/'supervisor.json');job=read(R/'job-status.json');assert code==0 and sup['status']=='complete'and sup['exit_code']==0 and job['status']=='complete'and job['native_endpoint']==150,'Preserve failed arm; no next world'
   run_checked([py,'-B','-X','utf8',str(ROOT/'project/tools/ai_tuning/audit_profile_test.py'),str(R),'--output',str(R/'independent-audit.json')],R/'audit.log')
   run_checked([py,'-B','-X','utf8',str(a.offline_tools/'profile-scorecard.py'),str(R),'--turn','150','--output',str(R/'scorecard150.json')],R/'scorecard.log')
   final=read(R/'game-01/turn-150.json');meta=final.get('completion_observer');assert meta and meta['major_calls']>0 and meta['observations']>0,'Missing native completion observer evidence'
   status['arms'].append(dict(name=name,root=str(R),native150=True,audited=True,completion_observer=meta))
   status.update(status='arm-complete',current=name);write(P/'reference-series-status.json',status)
  status.update(status='complete',finished=time.time());write(P/'reference-series-status.json',status)
  active=read(P/'active-run.json');active.update(status='complete',phase='references-complete-review-candidates',parity_verified=False);write(P/'active-run.json',active)
 except BaseException as e:
  status.update(status='attention',error=str(e),traceback=traceback.format_exc(),no_native_or_economic_retry=True,time=time.time());write(P/'reference-series-status.json',status);raise
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['launch','run']);p.add_argument('--campaign',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--controller-adapter',type=Path,required=True);p.add_argument('--rh-package',type=Path,required=True);p.add_argument('--offline-tools',type=Path,required=True);p.add_argument('--start-at',choices=['B','C'],default='B');p.add_argument('--accepted-B',dest='accepted_B',type=Path);a=p.parse_args()
 if a.mode=='run':series(a);return
 if a.start_at=='C':
  assert a.accepted_B and read(a.accepted_B/'independent-audit.json')['verified_observed_contracts']
  assert not(a.campaign/'basic-C/run-01').exists(),'Never reroll C'
  previous=a.campaign/'reference-series-status.json';archive=a.campaign/'reference-series-before-B-recovery.json';assert not archive.exists();previous.rename(archive)
 else:assert not(a.campaign/'reference-series-status.json').exists()
 args=[sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'run','--campaign',str(a.campaign),'--reference',str(a.reference),'--controller-adapter',str(a.controller_adapter),'--rh-package',str(a.rh_package),'--offline-tools',str(a.offline_tools),'--start-at',a.start_at]+(['--accepted-B',str(a.accepted_B)]if a.accepted_B else[])
 with(a.campaign/'reference-series.stdout.log').open('w')as stdout,(a.campaign/'reference-series.stderr.log').open('w')as stderr:proc=subprocess.Popen(args,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
 print(json.dumps(dict(series_pid=proc.pid,scope='fixed reference B/C; native progress pending')))
if __name__=='__main__':main()
