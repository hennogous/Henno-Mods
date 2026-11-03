"""Continue the same revealed ON demonstration without viewing pauses."""
import argparse,json,os,re,shutil,time,traceback
from pathlib import Path
from fixed_research_visible import VisibleRunner
from fixed_research_trial import INSTALLED,SOURCE,sha,read,write,summary,observation_window

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--segment',default='continuous-controller');a=p.parse_args();r=VisibleRunner(a.output);r.start_turn=71
 original=(a.output/'original-installed-CSC_AI.sql').read_bytes();installed=INSTALLED/'Data/CSC_AI.sql'
 archive=a.output/a.segment;archive.mkdir(exist_ok=False);shutil.copy2(__file__,archive/Path(__file__).name)
 write(archive/'version.json',{'version':'fixed-on-visible-user-restart-v4','sha256':sha(Path(__file__)),'same_game':True,'reason':'User requested stop/start after possibly cancelling autoplay while dismissing discovery popups. Use proven fixed-test ObserveAsPlayer(-1), original animation options, no artificial pauses.','pid':os.getpid()})
 try:
  r.status('continuing',same_game=True,no_viewing_pauses=True)
  r.cmd('AutoplayManager.SetActive(false);','GameCore_Tuner','visible-transfer-stop')
  r.states()
  # Revealing every tile raised discovery cinematics. Clear their queue through
  # the shipped popup handler, which also releases its native processing lock.
  if 'NaturalWonderPopup' in r.state:r.cmd('OnLocalPlayerTurnEnd();','NaturalWonderPopup','close-reveal-cinematics')
  r.cmd("assert(CSC_AI_Research.fixedHistory);print('CSC_VISIBLE_CONTINUE',Game.GetCurrentGameTurn());local ok,e=pcall(function() print('CSC_VISIBLE_PAUSE',GameConfiguration.IsPaused(),GameConfiguration.GetPausePlayer(),Automation.IsPaused(),Game.GetLocalPlayer(),Game.GetLocalObserver(),PlayerTypes.OBSERVER);end);print('CSC_VISIBLE_PAUSE_QUERY',ok,tostring(e));",'CSC_AI_Research','actual-visible-continuation')
  r.cmd("local q=Game:GetProperty('CSC_VISIBLE_CAMERA');if q then UI.LookAtPlot(q[1],q[2]);end;",'PlotInfo','visible-camera-reset')
  if (a.output/'original-animation.json').exists():
   m,c=[str(x).lower() for x in read(a.output/'original-animation.json')];r.cmd(f'UserConfiguration.SetValue("QuickMovement",{m});UserConfiguration.SetValue("QuickCombat",{c});','PlotInfo','restore-animation-before-restart')
  r.cmd('Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetTurns(math.max(1,84-Game.GetCurrentGameTurn()));AutoplayManager.SetActive(true);','GameCore_Tuner','visible-continuous-autoplay')
  deadline=time.monotonic()+600;last_count=-1;last_progress=time.monotonic()
  while time.monotonic()<deadline:
   time.sleep(5)
   text=r.cmd("print('CSC_FIXED_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());",label='visible-poll');turn,active=re.findall(r'CSC_FIXED_PROGRESS\s+(\d+)\s+(true|false)',text)[-1]
   rows=r.export_choices();census,moves=r.export_movement();r.status('watching',same_game=True,turn=int(turn),observations=len(rows),movement_events=len(moves),no_viewing_pauses=True)
   if len(rows)!=last_count:last_count=len(rows);last_progress=time.monotonic();r.say(f'Continuous ON: turn{turn}; {len(rows)} completed AI turns; {len(moves)} movement events.')
   if active=='false':break
   if time.monotonic()-last_progress>120:raise RuntimeError('Continuous autoplay stalled; preserve same game and stop, no new world')
  else:raise TimeoutError('Continuous viewing run exceeded bounded deadline')
  chosen=observation_window(rows);write(a.output/'choices.json',chosen);write(a.output/'choices-raw.json',rows)
  # Initial census is the first full five-player block, before natural turns.
  initial_end=next((i for i,x in enumerate(census) if i and x['player']<census[i-1]['player']),len(census))
  initial=census[:initial_end];initial_cities={(x['player'],x['id']) for x in initial if x['kind']=='CITY'}
  all_cities={(x['player'],x['id']) for x in census if x['kind']=='CITY'}
  positions={}
  for x in census:
   if x['kind']=='UNIT':positions.setdefault((x['player'],x['id'],x['type']),set()).add((x['x'],x['y']))
  changed=[dict(player=p,id=i,type=t,distinct_positions=len(v)) for (p,i,t),v in positions.items() if len(v)>1]
  result=dict(version='fixed-on-visible-user-restart-v4',research=summary(chosen),observed_turns=[71,82],actual_endpoint=int(turn),units_with_changed_positions=changed,new_city_ids=sorted(all_cities-initial_cities),move_event_count=len(moves),initial_census_rows=initial_end,left_game_open=True,not_paired_statistical_data=True,no_viewing_pauses=True)
  write(a.output/'result.json',result)
  r.cmd("local s={Name='CSC visible fixed ON endpoint 20261019',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);",'PlotInfo','visible-endpoint-save')
  r.status('complete',turn=int(turn),left_game_open=True,no_viewing_pauses=True)
 except BaseException as e:
  write(a.output/'continuous-failure.json',{'error':str(e),'traceback':traceback.format_exc()});r.status('failed',error=str(e),same_game=True,no_automatic_restart=True)
  try:r.cmd('AutoplayManager.SetActive(false);','GameCore_Tuner','stop-on-continuation-failure')
  except Exception:pass
  raise
 finally:
  try:
   if (a.output/'original-animation.json').exists():
    m,c=[str(x).lower() for x in read(a.output/'original-animation.json')];r.cmd(f'UserConfiguration.SetValue("QuickMovement",{m});UserConfiguration.SetValue("QuickCombat",{c});','PlotInfo','restore-animation')
  finally:
   installed.write_bytes(original);write(a.output/'installed-restored.json',{'verified':installed.read_bytes()==original,'sha256':sha(installed),'source_unchanged':SOURCE.read_bytes()==original})

if __name__=='__main__':main()
