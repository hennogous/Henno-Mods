"""Monitor the already-running same ON game; reveal its endpoint at250."""
import argparse,json,os,re,shutil,sqlite3,time,traceback
from pathlib import Path
from fixed_research_visible import VisibleRunner
from fixed_research_trial import HERE,read,write,sha
from run import SAVES

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--origin',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False)
 r=VisibleRunner(a.output);shutil.copy2(__file__,a.output/Path(__file__).name)
 write(a.output/'version.json',{'version':'visible-same-game-to250-v1','controller_sha256':sha(Path(__file__)),'origin':str(a.origin),'fresh_game':False,'target':250,'user_request':'Let it run; reveal entire map again at250.','native_gameplay':'Same loaded fixed ON save; installed temporary overlay already restored.','observation_gap':'No completed turn71 rows after reload; first full research observations72. Synthetic opportunity fixtures retained; not a natural baseline.'})
 try:
  r.status('running',target=250)
  r.cmd("Game:SetProperty('CSC_VISIBLE_TARGET_250',false);Events.PlayerTurnActivated.Add(function(pid) if Game.GetCurrentGameTurn()>=250 and not Game:GetProperty('CSC_VISIBLE_TARGET_250') then Game:SetProperty('CSC_VISIBLE_TARGET_250',Game.GetCurrentGameTurn());AutoplayManager.SetActive(false);end;end);print('CSC_TARGET_HOOK',Game.GetCurrentGameTurn());",'GameCore_Tuner','target250-hook')
  # Archive the loaded database, rather than confusing restored disk SQL with
  # the definitions which this same running game continues to use.
  cache=Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite"
  source=sqlite3.connect(cache.as_uri()+'?mode=ro',uri=True);dest=sqlite3.connect(a.output/'loaded-native-gameplay.sqlite');source.backup(dest);source.close()
  assert dest.execute("SELECT Item,Favored,Value FROM AiFavoredItems WHERE ListType='CSC_AI_FIXED_SERVICE_CIVICS'").fetchall()==[('CIVIC_NAVAL_TRADITION',1,0)];dest.close()
  deadline=time.monotonic()+14400;last_turn=None;progress=time.monotonic();continued=False
  while time.monotonic()<deadline:
   text=r.cmd("print('CSC_FIXED_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());",label='visible-poll');turn,active=re.findall(r'CSC_FIXED_PROGRESS\s+(\d+)\s+(true|false)',text)[-1];turn=int(turn)
   r.status('running',turn=turn,target=250,autoplay=active=='true')
   if turn!=last_turn:last_turn=turn;progress=time.monotonic();r.say(f'Visible ON game at{turn}; target250.')
   if turn>=250 and active=='false':break
   if active=='false':
    if 248<=turn<250 and not continued:
     continued=True;r.cmd('AutoplayManager.SetTurns(250-Game.GetCurrentGameTurn());AutoplayManager.SetActive(true);','GameCore_Tuner','finish-final-native-round')
    else:raise RuntimeError(f'Autoplay stopped early at{turn}; do not restart automatically')
   if time.monotonic()-progress>240:raise RuntimeError(f'No native turn progress for four minutes at{turn}')
   time.sleep(15)
  else:raise TimeoutError('Native game exceeded four-hour bound')
  reveal=r.cmd("local v=PlayersVisibility[0];v:RevealAllPlots();local n=Map.GetPlotCount();for i=0,n-1 do if not v:IsVisible(i) then v:ChangeVisibilityCount(i,1);end;end;local seen,visible=0,0;for i=0,n-1 do if v:IsRevealed(i) then seen=seen+1;end;if v:IsVisible(i) then visible=visible+1;end;end;assert(seen==n and visible==n);print('CSC_ENDPOINT_REVEAL',Game.GetCurrentGameTurn(),n,seen,visible);",'GameCore_Tuner','reveal-entire-endpoint',wait=5)
  actual,total,seen,visible=map(int,re.search(r'CSC_ENDPOINT_REVEAL\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',reveal).groups());write(a.output/'map-revealed.json',{'actual_turn':actual,'total_tiles':total,'revealed':seen,'visible':visible,'player':0,'verified':True})
  r.states()
  if 'NaturalWonderPopup' in r.state:r.cmd('OnLocalPlayerTurnEnd();','NaturalWonderPopup','close-endpoint-discovery-cinematics')
  rows=r.export_choices();write(a.output/'research-choices.json',rows)
  r.cmd("local R=CSC_AI_Research;Game:SetProperty('CSC_VISIBLE_RESEARCH_HISTORY',R.fixedHistory);Game:SetProperty('CSC_VISIBLE_MOVEMENT_CENSUSES',R.visibleCensus);Game:SetProperty('CSC_VISIBLE_MOVEMENT_EVENTS',R.visibleMoves);print('CSC_FINAL_OBSERVATIONS',#R.fixedHistory,#R.visibleCensus,#R.visibleMoves);",'CSC_AI_Research','preserve-endpoint-native-observations',wait=5)
  # A complete endpoint state supports later questions; no forced fixtures,
  # research, improvements or gameplay changes are added by this observer.
  r.cmd('if not CSCBASE then\n'+(HERE/'paired_observer.lua').read_text(encoding='utf-8')+'\nend;CSCBASE.snapshot();','CSC_AdjacencyGameplay','snapshot-endpoint',wait=8)
  text=(sorted((a.output/'commands').glob('*snapshot-endpoint.txt'))[-1]).read_text(encoding='utf-8');match=re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)',text)
  if match:write(a.output/'endpoint-state.json',json.loads(match[1]))
  name=f'CSC visible fixed ON turn{actual} 20261019';r.cmd('assert(Network.SaveGame({Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false})~=false);','PlotInfo','save-revealed-endpoint',wait=5)
  save=SAVES/(name+'.Civ6Save')
  for _ in range(15):
   if save.exists() and save.stat().st_size>0:break
   time.sleep(1)
  assert save.exists();shutil.copy2(save,a.output/save.name);write(a.output/'endpoint-save.json',{'path':str(save),'sha256':sha(save),'actual_turn':actual})
  r.status('complete',turn=actual,target=250,map_revealed=True,left_game_open=True)
 except BaseException as e:
  write(a.output/'failure.json',{'error':str(e),'traceback':traceback.format_exc()});r.status('failed',error=str(e),no_automatic_new_game=True)
  raise

if __name__=='__main__':main()
