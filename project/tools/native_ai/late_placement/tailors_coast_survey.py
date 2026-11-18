"""Inspect coastal Tailors opportunities in an unchanged saved world.

Diagnostic only: the query reads live materials, Quarter/Harbor geometry and
current native eligibility. It never publishes policy, advances turns or gives
orders. The shared controller owns loading, package/module qualification,
structural equivalence and shutdown; a foreign session is preserved. A custom
--query must retain the CSC_COAST_END marker and the same read-only contract.
Large results and cloned packages belong in an explicit Desktop output folder.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse,json,shutil
from planning_continue import prepare,enable,parse_census,compare_structure
from driver import NativeSession,HeldProcess,make_probe_controller,native_inventory,launch,configure,flags,read,write_json,manifest,sha,restore_preferences,lua,require,archive_sources
from ce_replay import verify_modules,DLL,HOTFIX_SHA
from ce_bakers_fresh import LOGS

def run(args):
 # Custom read-only economic benchmarks can exceed the usual short query.
 # This bounds acknowledgement waiting only: it never retries a transmission,
 # changes the saved world, or permits a second console owner.
 query_timeout=getattr(args,'query_timeout_seconds',15)
 require(type(query_timeout)is int and 1<=query_timeout<=60,'Read-only query timeout must be1..60 seconds')
 plan=prepare(args.source,args.output,args.at,args.at,args.dependencies,read_only=True)
 require(not native_inventory(),'Foreign session must be preserved')
 out=plan.output;out.mkdir(parents=True)
 controller=make_probe_controller(out,user_root=plan.user_root)
 controller.study_endpoint=args.at;controller.autoplay_interval_seconds=900
 session=NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
 copied=[]
 query=args.query or Path(__file__).with_name('tailors_coast_survey.lua')
 pins={str(p.resolve()):sha(p)for p in (Path(__file__),query)}
 write_json(out/'implementation-archive.json',archive_sources(pins,out/'implementation-version'))
 write_json(out/'protocol.json',dict(diagnostic=True,read_only=True,source=str(plan.source),turn=args.at,checkpoint=plan.checkpoint,world_edits=False,turns_advanced=0,query_timeout_seconds=query_timeout))
 def verify():
  for item in copied:
   require(manifest(item['install'])==item['files'],'Installed package changed')
   require(manifest(item['source'])==item['files'],'Frozen package changed')
  for item in plan.extras.values():require(manifest(Path(item['path']))==item['files'],'Optional package changed')
  require(all(sha(Path(p))==h for p,h in pins.items()),'Survey implementation changed')
 def gate():
  from planning_continue import HERE
  code='CSC_ENDPOINT_PLAYERS='+lua(plan.identity['original_ai'])+'\nCSC_ENDPOINT_EXPECTED_TURN='+str(args.at)+'\n'+read(HERE/'full_game_census.lua')
  raw=controller.cmd(code,'CSC_AI_BakersGameplay','coast-source-census')
  (out/'source-census.txt').write_text(raw,encoding='utf-8')
  proof=compare_structure(plan.expected_census,parse_census(raw,args.at))
  write_json(out/'source-structure-comparison.json',proof)
  require(proof['verified'],'Survey world differs from source')
  return True
 try:
  for item in plan.packages:shutil.copytree(item['source'],item['install']);copied.append(item)
  write_json(out/'installed-manifests.json',{i['role']:i['files']for i in copied})
  # Match the full-game archive contract so closed diagnostic package copies
  # can be retired against these immutable keepers, rather than accumulating
  # another complete art/CE bundle for every read-only question.
  write_json(out/'packages.json',{str(i['source']):dict(install=str(i['install']),files=i['files'])for i in copied})
  session.start(lambda:launch(SimpleNamespace(binary=plan.binary),out));session.wait_context('MainMenu')
  configure(controller,out,csc_id=plan.protocol['ce']);enable(session,plan.protocol['csc'])
  for identity in plan.extras:enable(session,identity)
  require({k for k,v in flags(controller,'coast-survey-mods')['mods'].items()if v}=={plan.protocol['ce'],plan.protocol['csc'],*plan.extras},'Unexpected active packages')
  session.load_once(plan.checkpoint['native_save'],sha256=plan.checkpoint['sha256'],native_directory=plan.saves,turn=args.at,
   contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay','CSC_AdjacencyGameplay'),eligibility=gate)
  ce=next(i for i in copied if i['role']=='ce')
  verify_modules(session,ce['install']/'Binaries/Win64'/DLL,out,HOTFIX_SHA)
  raw=controller.cmd(read(query),'CSC_AI_BakersGameplay','tailors-coast-survey',wait=query_timeout)
  (out/'tailors-coast-survey.txt').write_text(raw,encoding='utf-8')
  require('CSC_COAST_END\t'+str(args.at)in raw,'Coast survey incomplete')
  state=controller.state_read('coast-survey-final-clock')
  require(state['turn']==args.at and not state['active'],'Read-only survey clock changed')
  write_json(out/'complete.json',dict(verified=True,turn=args.at,turns_advanced=0))
 finally:
  if session.owner is not None and session.owner.poll()is None:
   session.close(restore_preferences=lambda:restore_preferences(controller,out),restore_package=verify)
  if session.closed:
   for item in copied:item['install'].rename(out/item['install'].name)
   for name in LOGS:
    p=plan.user_root/'Logs'/name
    if p.is_file():shutil.copyfile(p,out/name)

if __name__=='__main__':
 p=argparse.ArgumentParser()
 for k in('source','output','dependencies'):p.add_argument('--'+k,type=Path,required=True)
 p.add_argument('--at',type=int,default=250)
 p.add_argument('--query',type=Path)
 p.add_argument('--query-timeout-seconds',type=int,default=15)
 run(p.parse_args())
