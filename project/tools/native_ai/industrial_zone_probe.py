"""One existing-save IZ decision observation through the shared controller.

No new world, build orders, free prerequisites, SQL treatment or weight changes.
The disposable loaded-current-CSC diagnostic suspends only CSC's named assistance
turn callback so paid placement cannot interfere. Original save bytes stay intact.
"""
import argparse
import hashlib
import json
import re
import sys
import time
import traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'project/tools/ai_baseline'),str(ROOT/'project/tools/ai_tuning'),str(Path(__file__).parent)]
from full_game_controller.probe import make_probe_controller,write_json
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess,native_inventory
from full_game_controller.log_capture import capture_log_baseline,read_log_delta
from native_session_probe import launch
from native_profile_test import configure,manifest,restore_preferences
from native_probe_artifacts import archive_sources
from observer_host import NativeObserver,prove_loaded_module,validate_contract

EXPECTED='324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
SAVE_SHA='ea818368130273e02e70e31449a6f24a54e34486b8bfa402dd34b62255443e48'
TARGETS=[{'player':4,'city':262147},{'player':2,'city':589832}]

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def parse(raw,marker):
 values=re.findall(re.escape(marker)+r'=([^\r\n]+)',raw)
 if len(values)!=1:raise ValueError('Missing/ambiguous observation: '+marker)
 return json.loads(values[0])

def validate_source(value):
 if value['turn']!=250 or value['player0']!={'human':True,'alive':True}:
  raise ValueError('Original observer phase/identity mismatch')
 m=value['mapping']
 if not(0<=m['workshopIndex']<m['buildingIndexLimit']<=4096 and 0<=m['factoryIndex']<m['buildingIndexLimit'] and m['workshopIndex']!=m['factoryIndex'] and m['buildingCount']==m['buildingIndexLimit']):
  raise ValueError('Noncontiguous or invalid native building definitions')
 by={(x['player'],x['city']):x for x in value['targets']}
 if len(value['targets'])!=2 or len(by)!=2 or set(by)!={(4,262147),(2,589832)}:raise ValueError('Wrong declared city targets')
 definitions={x['type']:x for x in value['relevantDB']['buildings']}
 for name,technology in [('BUILDING_WORKSHOP','TECH_APPRENTICESHIP'),('BUILDING_FACTORY','TECH_INDUSTRIALIZATION')]:
  row=definitions[name]
  if row['district']!='DISTRICT_INDUSTRIAL_ZONE' or row['tech']!=technology or row['placement'] not in (False,0):raise ValueError('Loaded building definition changed the vanilla premise')
 requirements=[x for x in value['relevantDB']['prerequisites'] if x['building']=='BUILDING_FACTORY']
 if requirements!=[dict(building='BUILDING_FACTORY',prerequisite='BUILDING_WORKSHOP')]:raise ValueError('Loaded Factory prerequisite changed')
 for x in by.values():
  if not(x['exists'] and x['alive'] is True and x['human'] is False and x['major'] is True and x['technologies']['TECH_INDUSTRIALIZATION'] is True):raise ValueError('Target is not an eligible actual AI city')
  if not any(d['complete'] is True and d['pillaged'] is False for d in x['districts']):raise ValueError('No functioning Industrial Zone')
  if x['factory']['present'] is not False:raise ValueError('Factory already complete')
 for pair,expected in { (4,262147):(52,40,3160), (2,589832):(46,18,1304) }.items():
  x=by[pair]
  if (x['x'],x['y'])!=expected[:2] or not any(d['plot']==expected[2] and d['complete'] is True and d['pillaged'] is False for d in x['districts']):raise ValueError('Declared city/site coordinates changed')
 if by[(4,262147)]['workshop']['present'] is not False:raise ValueError('Blocked case no longer lacks Workshop')
 if not(by[(2,589832)]['workshop']['present'] is True and by[(2,589832)]['workshop']['pillaged'] is False):raise ValueError('Positive control lacks functioning Workshop')
 return True

def economic_signature(v):
 return {k:v['assistance'].get(k) for k in ('TOTALS','PURCHASE_INDEX','FOUNDATION_INDEX','pending','turnCycles')}

SUSPEND="""
local m=assert(CSC_AI_Assistance,'Owning assistance context missing its module')
local changed=false
if m then
 assert(type(m.OnPlayerTurn)=='function' and type(Events.PlayerTurnActivated.Remove)=='function')
 assert(next(m.queued or{})==nil,'Pending assistance callback; preserve before advancing')
 Events.PlayerTurnActivated.Remove(m.OnPlayerTurn);changed=true
end
print('CSC_IZ_ASSISTANCE='..(changed and 'true'or'false'))
"""

def run(a):
 out=a.output.resolve()
 if out.exists():raise ValueError('New output directory required; no replay')
 if not 1<=a.intervals<=5:raise ValueError('At most five one-turn intervals')
 if sha(a.source)!=SAVE_SHA:raise ValueError('Wrong exact existing save')
 if a.source.resolve().parent!=a.native_directory.resolve():raise ValueError('Native save directory required')
 if native_inventory():raise RuntimeError('Foreign Civ/Tuner/research owner; preserve it')
 out.mkdir(parents=True)
 installed_before=manifest(a.installed)
 write_json(out/'installed-before.json',installed_before)
 spec=read(a.spec);spec['path']=str(a.dll.resolve())
 if sha(a.dll)!=EXPECTED or spec['sha256']!=EXPECTED:raise ValueError('Wrong native binary')
 reader=Path(__file__).with_name('industrial_zone_snapshot.lua')
 script=Path(__file__).with_name('industrial_zone_observer.js')
 pins={str(p.resolve()):sha(p) for p in [a.binary,a.dll,a.source,reader,script,a.spec,Path(__file__),Path(__file__).with_name('observer_daemon.py')]}
 for m in list(sys.modules.values()):
  p=getattr(m,'__file__',None)
  if p and Path(p).suffix=='.py' and Path(p).is_relative_to(ROOT/'project/tools'):pins[str(Path(p).resolve())]=sha(p)
 for p in (ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'):pins[str(p.resolve())]=sha(p)
 dependency_pins=manifest(a.dependencies)
 write_json(out/'dependency-pins.json',dependency_pins)
 write_json(out/'source-pins.json',pins)
 write_json(out/'source-archive.json',archive_sources(pins,out/'source-version'))
 write_json(out/'protocol.json',{'source_turn':250,'maximum_endpoint':250+a.intervals,'fresh_worlds':0,'loads':1,'targets':TARGETS,'policy':'loaded-current-CSC, no RH; observational native scoring, named CSC assistance callback suspended; no native orders or data tuning','historical_world_reproduction':False,'class_struggle_motive':'read explicitly; Toulouse may retain civic motive; no causal outcome claim'})
 r=make_probe_controller(out,user_root=a.user_root)
 r.allow_observer_warning_dismissal=True;r.allow_observer_first_meet_dismissal=True;r.allow_observer_congress_review=True;r.study_endpoint=250+a.intervals
 session=NativeSession(out,r,inventory=native_inventory,hold=HeldProcess,write=write_json)
 observer=None;initial=None;error=None;logs={};completed=[]
 def verify():
  if manifest(a.installed)!=installed_before:raise RuntimeError('Installed files changed; preserve edits')
  changed=[p for p,h in pins.items() if sha(p)!=h]
  if changed:raise RuntimeError('Frozen inputs changed: '+repr(changed))
 def capture(label):
  v=parse(r.cmd(reader.read_text(encoding='utf-8'),'GameCore_Tuner',label,wait=35),'CSC_IZ_WORLD')
  write_json(out/(label+'.json'),v);return v
 def gate():
  nonlocal initial
  initial=capture('source-loaded');validate_source(initial);verify();return True
 def log_snapshot(label):
  dest=out/'logs'/label;dest.mkdir(parents=True)
  for name,base in list(logs.items()):
   path=a.user_root/'Logs'/name
   if path.exists():
    current,delta=read_log_delta(path,base)
    (dest/name).write_bytes(current.data)
    write_json(dest/(name+'.boundary.json'),{'initial':base.evidence(),'current':current.evidence(),'delta_bytes':len(delta)})
 def freeze_observer():
  if observer is None or observer.process is None:return
  if (observer.output/'trace-ready.json').exists():observer.before_menu()
  else:
   # Attach failed before any start request; references remain retained by the
   # daemon until the normal native exit. No active collector can need freezing.
   if (observer.output/'trace-start.request').exists():raise RuntimeError('Unconfirmed started observer; preserve owner')
   write_json(out/'observer-never-started.json',{'normal_exit_required':True,'no_explicit_detach':True})
 try:
  verify();session.start(lambda:launch(a,out));session.wait_context('MainMenu')
  configure(r,out,'BASIC')
  session.load_once(a.source,sha256=SAVE_SHA,native_directory=a.native_directory,turn=250,contexts=('GameCore_Tuner','PlotInfo','CSC_AdjacencyGameplay'),eligibility=gate)
  # Explicit probe setup, confined to this unsaved loaded process. No native
  # preference/forecast/building/queue changes, and no monkeypatch of methods.
  removed=False
  owner_context=None
  if initial['assistance']['mode']!='OFF':
   r.states()
   contexts=[x for x in ('CSC_AI_Assistance','CSC_AI_Mode_Basic_Assistance') if x in r.state]
   write_json(out/'source-contexts.json',sorted(r.state))
   if len(contexts)!=1:raise RuntimeError('Missing/ambiguous owning CSC assistance context')
   owner_context=contexts[0]
   raw=r.cmd(SUSPEND,owner_context,'suspend-installed-CSC-assistance-callback')
   removed=bool(re.search(r'CSC_IZ_ASSISTANCE=true',raw))
   if not removed:raise RuntimeError('Active CSC host callback suspension was not acknowledged')
  write_json(out/'assistance-callback-control.json',{'removed':removed,'mode':initial['assistance']['mode'],'owning_context':owner_context,'only_current_process':True,'save_written':False,'all_player_cycle_and_pending_records_checked':True})
  controlled=capture('source-controlled')
  if controlled!=initial:raise RuntimeError('Callback suspension changed exported source facts')
  config=dict(profile='industrial-zone-decision-v1',targets=TARGETS,workshopIndex=initial['mapping']['workshopIndex'],factoryIndex=initial['mapping']['factoryIndex'],buildingIndexLimit=initial['mapping']['buildingIndexLimit'],workshopType='BUILDING_WORKSHOP',factoryType='BUILDING_FACTORY',mappingVerified=True,maxPairs=64,maxCallbacks=10000,maxRows=64,maxThreads=8,maxScopeDepth=16)
  validate_contract(spec,config,4)
  write_json(out/'native-spec.json',spec);write_json(out/'observer-config.json',config)
  proof=prove_loaded_module(session.owner,spec,out/'loaded-module.json')
  observer=NativeObserver(out/'observer',session.owner,script=script,spec=out/'native-spec.json',config=out/'observer-config.json',dependencies=a.dependencies,loaded_module=out/'loaded-module.json')
  observer.attach_disabled()
  after=capture('source-attached-disabled')
  if after!=initial:raise RuntimeError('Disabled attachment changed exported source facts')
  for name in ('AI_CityBuild.csv','City_BuildQueue.csv','AI_Behavior_Trees.csv','AI_Planning.csv','Lua.log','Database.log'):
   logs[name]=capture_log_baseline(a.user_root/'Logs'/name)
  write_json(out/'source-gate.json',{'verified':True,'turn':250,'target_roles':TARGETS,'loaded_module':proof,'three_source_reads_equal':True,'installed_files':len(installed_before),'pins':len(pins),'rebase_declared':True})
  observer.start();write_json(out/'status.json',{'phase':'observing','native_identity':session.owner.identity,'turn':250})
  for turn in range(251,251+a.intervals):
   verify();r.play(turn)
   v=capture('boundary-'+str(turn));completed.append(turn)
   if v['turn']!=turn or economic_signature(v)!=economic_signature(initial):raise RuntimeError('Wrong clock or CSC economic side effects')
   snapshot,saturated=observer.snapshot('turn-'+str(turn))
   log_snapshot('turn-'+str(turn))
   write_json(out/'status.json',{'phase':'observing','native_identity':session.owner.identity,'turn':turn,'stats':snapshot['stats'],'saturated':saturated})
   if snapshot['stats']['errors'] or snapshot['stats']['identityChanges'] or snapshot.get('pendingPairs')!=0:raise RuntimeError('Observer fault/unfinished pair at boundary')
   calculations=[x for x in snapshot['records'] if x['kind']=='CalculateDistrictValues']
   covered={(x['entry']['identity']['owner'],x['entry']['identity']['city']) for x in calculations}
   if saturated or (len(completed)>=3 and {(4,262147),(2,589832)}<=covered):break
  final=capture('final-boundary')
  write_json(out/'observation-result.json',{'complete_intervals':completed,'initial':initial,'final':final,'no_CSC_economic_effects':economic_signature(final)==economic_signature(initial),'weight_changes':0,'new_worlds':0,'runtime_coverage_requires_record_review':True})
 except BaseException as failure:
  error=failure;write_json(out/'failure.json',{'error':str(failure),'traceback':traceback.format_exc(),'no_automatic_replay':True})
 finally:
  if session.owner is not None and session.owner.poll() is None:
   try:
    session.close(restore_preferences=lambda:restore_preferences(r,out) if (out/'original-preferences.json').exists() else None,restore_package=verify,before_menu=freeze_observer,after_native_exit=observer.after_native_exit if observer and observer.process is not None else lambda:None)
    if logs:log_snapshot('closed')
   except BaseException as failure:
    write_json(out/'cleanup-failure.json',{'error':str(failure),'traceback':traceback.format_exc(),'original_error':str(error)})
    if error is None:error=failure
  verify()
  write_json(out/'final-inventory.json',native_inventory())
 if error is not None:raise error
 if not session.closed:raise RuntimeError('Native session remains unclosed')
 write_json(out/'result.json',{'closed':True,'native_exit_code':0,'intervals':completed,'save_unchanged':sha(a.source)==SAVE_SHA,'installed_unchanged':manifest(a.installed)==installed_before,'preferences_restored':True,'observation_is_not_efficacy_test':True})
 print(json.dumps(read(out/'result.json')))

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('output','source','native-directory','binary','dll','user-root','installed','dependencies','spec'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--intervals',type=int,default=5)
 run(p.parse_args())
if __name__=='__main__':main()
