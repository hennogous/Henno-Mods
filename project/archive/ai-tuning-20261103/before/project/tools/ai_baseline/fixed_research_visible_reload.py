"""One bounded reload of the same stalled viewing save, never a new world."""
import argparse,os,re,shutil,time,traceback
from pathlib import Path
from fixed_research_visible import VisibleRunner
from fixed_research_trial import INSTALLED,SOURCE,read,write,sha,summary,observation_window
from run import SAVES

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=VisibleRunner(a.output);r.keep_game=False;r.start_turn=71
 archive=a.output/'same-save-reload';archive.mkdir(exist_ok=False);shutil.copy2(__file__,archive/Path(__file__).name)
 save=SAVES/'CSC visible ON recovery turn71 20261019.Civ6Save';assert save.exists();shutil.copy2(save,archive/save.name)
 original=(a.output/'original-installed-CSC_AI.sql').read_bytes();installed=INSTALLED/'Data/CSC_AI.sql'
 write(archive/'version.json',{'version':'same-save-visible-recovery-v5','pid':os.getpid(),'controller_sha256':sha(Path(__file__)),'save_sha256':sha(save),'same_world':True,'no_new_game':True,'reason':'Autoplay active with zero completed AI turns after stop/start; user reports map without popup. Single bounded reload.'})
 try:
  r.status('reloading',same_save=True)
  r.menu();r.cmd('Automation.SetAutoStartEnabled(true);Network.LoadGame('+__import__('json').dumps(str(save))+',ServerType.SERVER_TYPE_NONE);','MainMenu','visible-load-same-save',wait=3,check=False);r.wait('CSC_AI_Research',300)
  r.cmd("assert(Game.GetCurrentGameTurn()==71);assert(Game:GetProperty('CSC_RESEARCH_CHOICE_FIXTURE'));local found=false;for x in GameInfo.AiFavoredItems() do if x.ListType=='CSC_AI_FIXED_SERVICE_CIVICS' and x.Item=='CIVIC_NAVAL_TRADITION' then assert(x.Favored and x.Value==0);found=true;end;end;assert(found);",'CSC_AI_Research','actual-reloaded-world',wait=3)
  observer=(a.output/'commands/0017-visible-observer-reveal.lua').read_text(encoding='utf-8');r.cmd(observer,'CSC_AI_Research','restore-visible-observers-only',wait=3)
  r.cmd('Automation.Pause(false);Automation.SetActive(false);AutoplayManager.SetTurns(13);AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);','GameCore_Tuner','same-save-autoplay')
  deadline=time.monotonic()+360;last_count=-1;last_progress=time.monotonic()
  while time.monotonic()<deadline:
   time.sleep(5);text=r.cmd("print('CSC_FIXED_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());",label='visible-poll');turn,active=re.findall(r'CSC_FIXED_PROGRESS\s+(\d+)\s+(true|false)',text)[-1]
   rows=r.export_choices();census,moves=r.export_movement();r.status('watching',same_save=True,turn=int(turn),observations=len(rows),movement_events=len(moves),no_viewing_pauses=True)
   if len(rows)!=last_count:last_count=len(rows);last_progress=time.monotonic();r.say(f'Same-save ON: turn{turn}; {len(rows)} completed AI turns; {len(moves)} movement events.')
   if active=='false':break
   if time.monotonic()-last_progress>90:raise RuntimeError('Same-save reload did not release simulation; no further recovery attempts')
  else:raise TimeoutError('Bounded same-save demonstration timed out')
  chosen=observation_window(rows);write(a.output/'choices.json',chosen);write(a.output/'choices-raw.json',rows)
  initial_end=next((i for i,x in enumerate(census) if i and x['player']<census[i-1]['player']),len(census));initial=census[:initial_end]
  old={(x['player'],x['id']) for x in initial if x['kind']=='CITY'};new={(x['player'],x['id']) for x in census if x['kind']=='CITY'};positions={}
  for x in census:
   if x['kind']=='UNIT':positions.setdefault((x['player'],x['id'],x['type']),set()).add((x['x'],x['y']))
  changed=[dict(player=p,id=i,type=t,distinct_positions=len(v)) for (p,i,t),v in positions.items() if len(v)>1]
  write(a.output/'result.json',dict(version='same-save-visible-recovery-v5',research=summary(chosen),actual_endpoint=int(turn),units_with_changed_positions=changed,new_city_ids=sorted(new-old),move_event_count=len(moves),initial_census_rows=initial_end,left_game_open=True,not_paired_statistical_data=True))
  r.status('complete',turn=int(turn),same_save=True,left_game_open=True)
 except BaseException as e:
  write(archive/'failure.json',{'error':str(e),'traceback':traceback.format_exc()});r.status('failed',error=str(e),no_further_recovery=True)
  try:r.cmd('AutoplayManager.SetActive(false);','GameCore_Tuner','final-stop')
  except Exception:pass
  raise
 finally:
  try:r.restore_live_preferences()
  except Exception as e:write(a.output/'cleanup-required.json',{'error':str(e)})
  installed.write_bytes(original);write(a.output/'installed-restored.json',{'verified':installed.read_bytes()==original,'sha256':sha(installed),'source_unchanged':SOURCE.read_bytes()==original})

if __name__=='__main__':main()
