"""One fresh Online-speed CSC-only game, bounded to turn100.

All game control uses the maintained shared controller/session. The scanner
reads loaded rules; the native table adds score priority, never creates content.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'project/tools/ai_baseline'),str(HERE)]
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess,native_inventory
from full_game_controller.environment import launch,configure,manifest,restore_preferences,archive_sources,prove_loaded_module,write_json
from full_game_controller.log_capture import capture_log_baseline,read_log_delta
from daemon import NativeExtension,SHA,validate_contract,validate_snapshot
from policy import shortlist,PROFILE,PENALTY_PER_POINT_Q8,MAX_PENALTY_Q8

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def parse(raw,marker):
 values=re.findall(re.escape(marker)+r'=([^\r\n]+)',raw)
 if len(values)!=1:raise ValueError('Missing or ambiguous '+marker)
 return json.loads(values[0])

def recovery_projection(value):
 """Exact captured site/city/rule facts, ignoring collection order and clocks.

 This is a scanner-fact comparison, never full-world, RNG or native-cache parity.
 Timing/geometry-cache statistics intentionally differ after a new process.
 """
 def canonical(v):
  if isinstance(v,dict):return {k:canonical(x)for k,x in sorted(v.items())}
  if isinstance(v,list):return sorted((canonical(x)for x in v),key=lambda x:json.dumps(x,sort_keys=True))
  return v
 keys=('turn','speed','width','height','districtCount','originalAI','currentHumans','players','cities','candidates','quarters','rules')
 return {k:canonical(value[k])for k in keys}

def setup():
 return """GameConfiguration.SetToDefaults();GameConfiguration.SetRuleSet('RULESET_EXPANSION_2');BuildHeadlessGameSetup();RebuildPlayerParameters(true);GameSetup_RefreshParameters();MapConfiguration.SetScript('Continents.lua');MapConfiguration.SetMapSize('MAPSIZE_SMALL');GameConfiguration.SetParticipatingPlayerCount(6);GameConfiguration.SetValue('CITY_STATE_COUNT',9);GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE');GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE');GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',26131103);MapConfiguration.SetValue('RANDOM_SEED',16131103);MapConfiguration.SetValue('resources',2);GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false);GameConfiguration.SetStartEra(DB.MakeHash('ERA_ANCIENT'));for _,pid in ipairs(GameConfiguration.GetParticipatingPlayerIDs())do PlayerConfigurations[pid]:SetLeaderTypeName(nil)end;ReleasePlayerParameters();HideGameSetup();Automation.SetAutoStartEnabled(true);Network.HostGame(ServerType.SERVER_TYPE_NONE);"""

def run(args):
 out=args.output.resolve()
 if out.exists()or native_inventory():raise RuntimeError('Fresh output and no existing native owner required')
 first=args.resume_turn if args.resume_save else 1
 if not 1<=first<100:raise ValueError('Invalid recovery boundary')
 if args.resume_save and(not args.original_run or not args.resume_save.is_file()):raise ValueError('Recovery provenance required')
 original_preferences=read(args.original_run/'original-preferences.json')if args.resume_save else None
 spec=read(args.spec);spec['path']=str(args.dll.resolve())
 if sha(args.dll)!=SHA:raise ValueError('Pinned XP2 binary required')
 out.mkdir(parents=True);installed=manifest(args.installed);deps=manifest(args.dependencies)
 files=list(HERE.glob('*'));files=[p for p in files if p.is_file()]
 files += [Path(m.__file__) for m in list(sys.modules.values()) if getattr(m,'__file__',None)and Path(m.__file__).is_relative_to(ROOT/'project/tools')]
 files += list((ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'))
 files += [args.binary,args.dll,args.spec]
 reference_scan=None
 if args.resume_save:
  files += [args.resume_save,args.original_run/'original-preferences.json',args.original_run/'scans/source-1.json']
  for path in (args.original_run/'scans'/('turn-'+str(first)+'.json'),args.original_run/'scans'/('source-'+str(first)+'.json')):
   if path.is_file():reference_scan=path;files.append(path);break
 pins={str(p.resolve()):sha(p) for p in files}
 write_json(out/'source-pins.json',pins);write_json(out/'source-archive.json',archive_sources(pins,out/'source-version'))
 write_json(out/'installed-before.json',installed);write_json(out/'dependency-pins.json',deps)
 write_json(out/'protocol.json',dict(profile=PROFILE,speed='GAMESPEED_ONLINE',start_turn=first,maximum_endpoint=100,fresh_worlds=0 if args.resume_save else 1,loads=1 if args.resume_save else 0,recovery_from=str(args.original_run)if args.resume_save else None,threshold=4,deltaQ8=1048576,penalty_per_missing_point_Q8=PENALTY_PER_POINT_Q8,maximum_penalty_Q8=MAX_PENALTY_Q8,penalty_floor_Q8=-1048576,weak_sites_remain_selectable=True,delta_is_priority_not_economic_value=True,map_seed=16131103,game_seed=26131103,legacy_tuning=False,forced_orders=False,grants=False,native_callbacks='score/cache/best/PV; no game API calls',refresh='once each inactive turn; cached city geometry',planned_bakers_mill=True,stale_request_rollback_claimed=False))
 controller=make_probe_controller(out,user_root=args.user_root)
 controller.allow_observer_warning_dismissal=controller.allow_observer_first_meet_dismissal=controller.allow_observer_congress_review=True
 controller.study_endpoint=100
 session=NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
 extension=None;error=None;initial=None;original_ai=[];history=[];windows=[];logs={};config=None;last_turn=None
 def verify(content=False):
  if any(sha(path)!=digest for path,digest in pins.items()):raise RuntimeError('Frozen test source changed')
  if content and(manifest(args.installed)!=installed or manifest(args.dependencies)!=deps):raise RuntimeError('Installed package/dependencies changed; preserve edits')
 def scan(label):
  t0=time.perf_counter();raw=controller.cmd('CSC_AI_AdjacencyScan({'+','.join(map(str,original_ai))+'});','CSC_AdjacencyGameplay',label,wait=15)
  value=parse(raw,'CSC_AI_ADJACENCY_SCAN');value['transportWallSeconds']=time.perf_counter()-t0
  write_json(out/'scans'/(label+'.json'),value);return value
 def gate():
  nonlocal original_ai,initial,last_turn
  raw=controller.cmd("assert(Game.GetCurrentGameTurn()=="+str(first)+");assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT==nil and GameInfo.CSC_AI_Profile==nil,'Legacy tuning loaded');local a={};for pid=0,63 do local p=Players[pid];if p and p:IsAlive()and p:IsMajor()and not p:IsHuman()then a[#a+1]=tostring(pid)end end;print('CSC_ORIGINAL_AI=['..table.concat(a,',')..']');",'GameCore_Tuner','original-player-identities')
  original_ai=read(args.original_run/'scans/source-1.json')['originalAI']if args.resume_save else parse(raw,'CSC_ORIGINAL_AI');assert len(original_ai)==5 and 0 not in original_ai
  controller.cmd((HERE/'scan.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','install-readonly-scanner',wait=5)
  initial=scan('source-'+str(first));assert initial['turn']==first and initial['speed']=='GAMESPEED_ONLINE'and not(set(initial['currentHumans'])&set(original_ai))
  if not args.resume_save:assert initial['currentHumans']==[0]
  if reference_scan:
   expected,actual=recovery_projection(read(reference_scan)),recovery_projection(initial)
   different=[k for k in expected if expected[k]!=actual[k]]
   write_json(out/'recovery-scanner-parity.json',dict(reference=str(reference_scan),reference_sha256=sha(reference_scan),different_fields=different,verified=not different,scope='Captured city/district/queue/candidate/rule/player facts; not full world, RNG, cache or fractional-turn parity'))
   if different:raise RuntimeError('Recovery scanner facts differ: '+','.join(different))
  last_turn=first;verify(content=True);return True
 def freeze():
  if extension is not None:extension.before_menu()
 def save_logs():
  destination=out/'logs-closed';destination.mkdir(exist_ok=True)
  for name,baseline in logs.items():
   path=args.user_root/'Logs'/name
   if path.exists():
    current,delta=read_log_delta(path,baseline);(destination/name).write_bytes(current.data);write_json(destination/(name+'.boundary.json'),dict(initial=baseline.evidence(),current=current.evidence(),delta_bytes=len(delta)))
 try:
  verify(content=True);session.start(lambda:launch(args,out));session.wait_context('MainMenu');configure(controller,out,'BASIC')
  if args.resume_save:
   write_json(out/'configuration-before-original-preference-recovery.json',read(out/'original-preferences.json'))
   write_json(out/'original-preferences.json',original_preferences)
   session.load_once(args.resume_save,sha256=sha(args.resume_save),native_directory=args.resume_save.resolve().parent,turn=first,contexts=('GameCore_Tuner','PlotInfo','CSC_AdjacencyGameplay'),eligibility=gate)
  else:
   session.issue_once('host-online-game',setup(),'MainMenu')
   session.ready_after_issue(first,('GameCore_Tuner','PlotInfo','CSC_AdjacencyGameplay'),eligibility=gate,timeout=300)
  config=dict(profile=PROFILE,width=initial['width'],height=initial['height'],districtCount=initial['districtCount'],districtIndices=[q['index']for q in initial['quarters']],originalAI=original_ai)
  validate_contract(spec,config);write_json(out/'native-spec.json',spec);write_json(out/'extension-config.json',config)
  prove_loaded_module(session.owner,spec,out/'loaded-module.json')
  extension=NativeExtension(out/'extension',session.owner,script=HERE/'live.js',spec=out/'native-spec.json',config=out/'extension-config.json',dependencies=args.dependencies,loaded_module=out/'loaded-module.json')
  extension.attach_disabled();extension.start()
  for name in('AI_CityBuild.csv','AI_Behavior_Trees.csv','City_BuildQueue.csv','Lua.log','Database.log','Modding.log'):logs[name]=capture_log_baseline(args.user_root/'Logs'/name)
  value=initial
  for turn in range(first,101):
   if value['turn']!=turn or value['speed']!='GAMESPEED_ONLINE':raise RuntimeError('Unexpected turn/speed')
   plan=shortlist(value);write_json(out/'plans'/('turn-'+str(turn)+'.json'),plan)
   history.append(dict(turn=turn,cities=len(value['cities']),evaluated=value['sitesEvaluated'],geometryBuilt=value['geometryBuilt'],elapsedSeconds=value['elapsedSeconds'],qualified=len(plan['qualified']),selected=plan['selected'],penalized=len(plan['penalized']),quarters=[dict(player=c['player'],city=c['city'],**d)for c in value['cities']for d in c['districts']if d['type'].startswith('DISTRICT_CSC_')]))
   write_json(out/'progress.json',dict(turn=turn,maximum_endpoint=100,qualified=len(plan['qualified']),selected=len(plan['selected']),penalized=len(plan['penalized']),updated_unix=time.time(),quarters=len(history[-1]['quarters'])))
   if turn==100:break
   publication=extension.publish(plan['entries'],turn+1);windows.append(publication['previous'])
   verify();controller.play(turn+1)
   payload,saturated=extension.snapshot('turn-'+str(turn+1));validate_snapshot(payload,config)
   if saturated:raise RuntimeError('Native window exhausted')
   write_json(out/'native'/('turn-'+str(turn+1)+'.json'),payload)
   value=scan('turn-'+str(turn+1));last_turn=turn+1
  write_json(out/'history.json',history)
 except BaseException as failure:
  error=failure;write_json(out/'failure.json',dict(error=str(failure),traceback=traceback.format_exc(),last_turn=last_turn,no_automatic_replay=True));write_json(out/'history.json',history)
 finally:
  if session.owner is not None and session.owner.poll()is None:
   try:session.close(restore_preferences=lambda:restore_preferences(controller,out)if(out/'original-preferences.json').exists()else None,restore_package=lambda:verify(content=True),before_menu=freeze,after_native_exit=extension.after_native_exit if extension and extension.process else lambda:None);save_logs()
   except BaseException as failure:write_json(out/'cleanup-failure.json',dict(error=str(failure),traceback=traceback.format_exc()));error=error or failure
  write_json(out/'final-inventory.json',native_inventory())
 if extension and(out/'extension/trace-counts.json').exists():
  final=read(out/'extension/trace-counts.json');
  if 'snapshot'in final:windows.append(final['snapshot'])
 write_json(out/'native-windows.json',windows)
 result=dict(profile=PROFILE,closed=session.closed,endpoint=last_turn,maximum_endpoint=100,originalAI=original_ai,windows=len(windows),mutations=sum(w['stats']['changed']for w in windows),penalty_mutations=sum(r['k']=='net'and r['result']<r['base'] for w in windows for r in w['records']),bonus_mutations=sum(r['k']=='net'and r['result']>r['base'] for w in windows for r in w['records']),native_errors=sum(w['stats']['errors']for w in windows),best_calls=sum(sum(r['k']=='best'for r in w['records'])for w in windows),qualified_city_turns=sum(bool(h['selected'])for h in history),observed_Quarters=history[-1]['quarters']if history else [],installed_unchanged=manifest(args.installed)==installed,economic_benefit_proven=False,changed_choice_proven=False,error=str(error)if error else None)
 write_json(out/'result.json',result);print(json.dumps(result),flush=True)
 if error:raise error

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in('output','binary','dll','user-root','installed','dependencies','spec'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--resume-save',type=Path);p.add_argument('--resume-turn',type=int);p.add_argument('--original-run',type=Path)
 run(p.parse_args())
if __name__=='__main__':main()
