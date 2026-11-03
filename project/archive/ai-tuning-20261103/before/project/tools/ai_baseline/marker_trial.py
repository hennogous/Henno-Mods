"""Disposable native marker smoke; explicitly separate from natural AI baselines."""
import argparse,json,re,shutil,time
from pathlib import Path
from run import Runner,write,LOGS
from tuning_trial import TrialRunner

class MarkerRunner(Runner):
 def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
  if label.startswith('start-'):code=code.replace('GAMESPEED_STANDARD','GAMESPEED_ONLINE')
  return super().cmd(code,state,label,wait,check)

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('stage',choices=['start','load','quit','probe','command','compare','humancompare','finalsmoke','ai','guardai','cleanup'])
p.add_argument('--output',type=Path,required=True)
p.add_argument('--file',type=Path)
p.add_argument('--state',default='CSC_AI_MaterialMarkers')
p.add_argument('--label')
p.add_argument('--target-turn',type=int,default=20)
a=p.parse_args();r=MarkerRunner(a.output)
if a.stage=='start':
 r.config();r.start(1)
 write(a.output/'status.json',{'status':'ready','disposable':True,'natural_benchmark':False})
elif a.stage=='quit':
 r.states()
 if 'PlotInfo' in r.state:r.menu()
 r.wait('MainMenu')
 try:r.cmd('Events.UserConfirmedClose();','MainMenu','quit-for-marker-definition',wait=1,check=False)
 except (ConnectionResetError,EOFError):pass
elif a.stage=='load':
 r.wait('MainMenu')
 save=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Saves/Single/CSC marker disposable fixture 20261017.Civ6Save"
 assert save.exists()
 shutil.copy2(save,a.output/save.name)
 r.cmd('Automation.SetAutoStartEnabled(true);Network.LoadGame('+json.dumps(str(save))+',ServerType.SERVER_TYPE_NONE);','MainMenu','reload-fixture',wait=2,check=False)
 r.wait('CSC_AI_MaterialMarkers',300)
 r.cmd("assert(CSC_AI_MaterialMarkers);print('CSC_MARKER_RELOADED',Game.GetCurrentGameTurn());",'CSC_AI_MaterialMarkers','reloaded',wait=3)
elif a.stage in ('probe','command'):
 assert a.file
 label=a.label or a.file.stem
 t=r.cmd(a.file.read_text(),a.state,label,wait=8,check=True)
 match=re.search(r'CSC_MARKER_RESULT=([^\r\n]+)',t)
 if match:write(a.output/(label+'.json'),json.loads(match.group(1)))
elif a.stage in ('ai','guardai'):
 if a.stage=='ai':
  r.cmd(Path(__file__).with_name('paired_observer.lua').read_text(),'CSC_AdjacencyGameplay','controlled-ai-observer',wait=3)
  r.cmd(Path(__file__).with_name('marker_ai_observer.lua').read_text(),'CSC_AI_MaterialMarkers','marker-ai-observer',wait=3)
 else:
  r.cmd('assert(CSCBASE and CSCBASE.version==3);CSCBASE.checkpoints[Game.GetCurrentGameTurn()]=nil;','CSC_AdjacencyGameplay','continue-observer')
  r.cmd(Path(__file__).with_name('marker_guard_observer.lua').read_text(),'CSC_AI_MaterialMarkers','marker-guard-observer',wait=3)
 text=r.cmd("print('CSC_MARKER_START_TURN',Game.GetCurrentGameTurn());",'CSC_AI_MaterialMarkers','ai-start-turn')
 start=int(re.search(r'CSC_MARKER_START_TURN\s+(\d+)',text).group(1))
 r.snapshot(1,start)
 r.autoplay(1,a.target_turn)
 value='CSC_MARKER_AI_OBSERVER' if a.stage=='ai' else 'CSC_MARKER_GUARD_OBSERVER'
 text=r.cmd("print('CSC_MARKER_AI_RESULT='..CSC_MaterialMapCore.Json("+value+"));",'CSC_AI_MaterialMarkers','marker-ai-results',wait=4)
 write(a.output/'marker-events.json',json.loads(re.search(r'CSC_MARKER_AI_RESULT=([^\r\n]+)',text).group(1)))
 write(a.output/'controlled-ai.json',{'status':'complete','start':start,'turn':a.target_turn,'disposable_fixture':True,'natural_benchmark':False})
elif a.stage in ('compare','humancompare','finalsmoke'):
 def record(name,code,state):
  t=r.cmd(code,state,name,wait=4)
  match=re.search(r'CSC_MARKER_RESULT=([^\r\n]+)',t);assert match,name
  value=json.loads(match.group(1));write(a.output/(name+'.json'),value);return value
 if a.stage=='finalsmoke':
  def probe(name,filename,state):return record(name,Path(__file__).with_name(filename).read_text(),state)
  probe('final-marked-gameplay','marker_probe_gameplay.lua','CSC_AI_MaterialMarkers')
  probe('final-marked-ui','marker_probe_ui.lua','PlotInfo')
  r.cmd('CSC_AI_MaterialMarkers.Enabled=false;CSC_AI_MaterialMarkers.Refresh();','CSC_AI_MaterialMarkers','final-off')
  probe('final-unmarked-gameplay','marker_probe_gameplay.lua','CSC_AI_MaterialMarkers')
  probe('final-unmarked-ui','marker_probe_ui.lua','PlotInfo')
  probe('final-unmarked-human','marker_human_ui.lua','PlotInfo')
  r.cmd('CSC_AI_MaterialMarkers.Enabled=true;CSC_AI_MaterialMarkers.Refresh();','CSC_AI_MaterialMarkers','final-on')
  probe('final-marked-human','marker_human_ui.lua','PlotInfo')
  probe('final-forest-control','marker_forest_control.lua','CSC_AI_MaterialMarkers')
  probe('final-unitpanel','marker_unitpanel.lua','UnitPanel')
  r.cmd(Path(__file__).with_name('marker_build_ui.lua').read_text(),'PlotInfo','final-build',wait=4)
  probe('final-build-verify','marker_build_verify.lua','CSC_AI_MaterialMarkers')
  r.cmd(Path(__file__).with_name('marker_remove_resource.lua').read_text(),'CSC_AI_MaterialMarkers','final-remove-resource',wait=4)
  probe('final-resource-removed','marker_verify_removal.lua','CSC_AI_MaterialMarkers')
  write(a.output/'final-smoke.json',{'status':'passed'})
  raise SystemExit(0)
 prefix=(a.label+'-') if a.label else ''
 r.cmd('CSC_AI_MaterialMarkers.Enabled=false;CSC_AI_MaterialMarkers.Refresh();','CSC_AI_MaterialMarkers',prefix+'markers-off')
 if a.stage=='compare':
  record(prefix+'unmarked-gameplay',Path(__file__).with_name('marker_probe_gameplay.lua').read_text(),'CSC_AI_MaterialMarkers')
  record(prefix+'unmarked-ui',Path(__file__).with_name('marker_probe_ui.lua').read_text(),'PlotInfo')
 else:record(prefix+'unmarked-human',Path(__file__).with_name('marker_human_ui.lua').read_text(),'PlotInfo')
 r.cmd('CSC_AI_MaterialMarkers.Enabled=true;CSC_AI_MaterialMarkers.Refresh();','CSC_AI_MaterialMarkers',prefix+'markers-on')
 if a.stage=='compare':
  record(prefix+'restored-gameplay',Path(__file__).with_name('marker_probe_gameplay.lua').read_text(),'CSC_AI_MaterialMarkers')
  record(prefix+'restored-ui',Path(__file__).with_name('marker_probe_ui.lua').read_text(),'PlotInfo')
 else:record(prefix+'restored-human',Path(__file__).with_name('marker_human_ui.lua').read_text(),'PlotInfo')
elif a.stage=='cleanup':
 r.states()
 if 'PlotInfo' in r.state:r.menu()
 # The v1 restore checker handles duplicate installed mod IDs robustly.
 other=TrialRunner(a.output);other.restore();other.verify_preferences()
 logs=a.output/'logs';logs.mkdir(exist_ok=True)
 for path in LOGS.iterdir():
  if path.is_file() and path.suffix in ('.log','.csv'):shutil.copy2(path,logs/path.name)
 write(a.output/'status.json',{'status':'archived','disposable':True,'preferences_restored':True})
