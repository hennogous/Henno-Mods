"""One watchable fixed-ON demonstration; deliberately separate from paired data.

Prepares a fresh native game, reveals viewer0, and waits for a human-ready file.
Only native autoplay moves units. Leaves the endpoint open for inspection.
"""
import argparse,json,os,re,time,traceback
from pathlib import Path
from fixed_research_trial import FixedRunner,HERE,INSTALLED,SOURCE,sha,read,write,summary,observation_window

VERSION='fixed-on-visible-map-v1'

class VisibleRunner(FixedRunner):
 def pin_sources(self):
  super().pin_sources();p=self.out/'tuning-source-hashes.json';v=read(p);v[str(Path(__file__))]=sha(Path(__file__));write(p,v)
 def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
  # These prefixes already have bounded read retries in FixedRunner.
  if label=='visible-poll':label='fixed-poll'
  return super().cmd(code,state,label,wait,check)
 def status(self,status,**kw):
  write(self.out/'job-status.json',dict(status=status,pid=os.getpid(),version=VERSION,updated_unix=time.time(),**kw))
 def prepare_view(self):
  self.cmd((HERE/'research_choice_fixture.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','visible-choice-fixture')
  self.cmd("""CSC_AI_Research.Invalidate();for pid=1,5 do assert(CSC_AI_Research.Evaluate(pid,4));end;
local R=CSC_AI_Research;R.fixedHistory={};R.visibleCensus={};R.visibleMoves={};
local function census(pid)
 local p=Players[pid];local c=p:GetCulture():GetProgressingCivic();local d=GameInfo.Civics[c];
 R.fixedHistory[#R.fixedHistory+1]={Game.GetCurrentGameTurn(),pid,d and d.CivicType or 'NONE',p:GetCulture():HasCivic(GameInfo.Civics.CIVIC_NAVAL_TRADITION.Index)};
 for _,u in p:GetUnits():Members() do R.visibleCensus[#R.visibleCensus+1]={Game.GetCurrentGameTurn(),pid,'UNIT',u:GetID(),GameInfo.Units[u:GetType()].UnitType,u:GetX(),u:GetY()};end;
 for _,v in p:GetCities():Members() do R.visibleCensus[#R.visibleCensus+1]={Game.GetCurrentGameTurn(),pid,'CITY',v:GetID(),'CITY',v:GetX(),v:GetY()};end;
end;
-- Initial positions are retained separately from completed-player-turn records.
for pid=1,5 do census(pid);end;R.fixedHistory={};
Events.PlayerTurnDeactivated.Add(function(pid) if pid>=1 and pid<=5 then census(pid);end;end);
if Events.UnitMoved then Events.UnitMoved.Add(function(pid,id,x,y) if pid>=1 and pid<=5 then R.visibleMoves[#R.visibleMoves+1]={Game.GetCurrentGameTurn(),pid,id,x,y};end;end);end;
local u=Players[1]:GetUnits();local target=nil;for _,v in u:Members() do if GameInfo.Units[v:GetType()].UnitType=='UNIT_SETTLER' then target=v;break;end;end;
if not target then for _,v in u:Members() do target=v;break;end;end;
assert(target);Game:SetProperty('CSC_VISIBLE_CAMERA',{target:GetX(),target:GetY(),target:GetID()});
local v=PlayersVisibility[0];assert(v);v:RevealAllPlots();
local n=Map.GetPlotCount();for i=0,n-1 do if not v:IsVisible(i) then v:ChangeVisibilityCount(i,1);end;end;
local revealed,visible=0,0;for i=0,n-1 do if v:IsRevealed(i) then revealed=revealed+1;end;if v:IsVisible(i) then visible=visible+1;end;end;
assert(revealed==n and visible==n);print('CSC_VISIBLE_MAP',n,revealed,visible);
""",'CSC_AI_Research','visible-observer-reveal',wait=3)
  text=self.cmd("""local q=Game:GetProperty('CSC_VISIBLE_CAMERA');assert(q);UI.LookAtPlot(q[1],q[2]);
print('CSC_VISIBLE_CAMERA',q[1],q[2],q[3]);print('CSC_VISIBLE_OPTIONS',UserConfiguration.IsQuickMovement(),UserConfiguration.IsQuickCombat());
print('CSC_VISIBLE_MODDING',type(Modding),Modding and type(Modding.GetInstalledMods));
""",'PlotInfo','actual-visible-ui',wait=3)
  m=re.search(r'CSC_VISIBLE_OPTIONS\s+(true|false)\s+(true|false)',text)
  if m:
   self.original_animation=[x=='true' for x in m.groups()];write(self.out/'original-animation.json',self.original_animation)
   self.cmd('UserConfiguration.SetValue("QuickMovement",false);UserConfiguration.SetValue("QuickCombat",false);','PlotInfo','visible-animation')
  # Mod preferences affect future loads, not this already-loaded native database.
  # Restore them in the live UI if the same documented Modding API is available.
  if re.search(r'CSC_VISIBLE_MODDING\s+table\s+function',text):
   self.restore_live_preferences()
  else:write(self.out/'cleanup-required.json',{'reason':'Original mod preferences require frontend restoration after viewing.','original':str(self.out/'original-preferences.json')})
  write(self.out/'view-settings.json',{'version':VERSION,'viewer':0,'camera_player':1,'all_plots_revealed_and_visible':True,'paired_statistics':False,'reason':'Viewer knowledge and watchable pacing differ from controlled experiment.'})
 def restore_live_preferences(self):
  original=read(self.out/'original-preferences.json');entries=','.join('['+json.dumps(k)+']='+str(v).lower() for k,v in original['mods'].items())
  code='local wanted={'+entries+'''};local disable={};for _,m in ipairs(Modding.GetInstalledMods()) do if wanted[m.Id]==false and m.Enabled then disable[#disable+1]=m.Handle end;end;if #disable>0 then Modding.DisableMod(disable);end;for _,m in ipairs(Modding.GetInstalledMods()) do if wanted[m.Id]==true then Modding.EnableMod(m.Handle,true);end;end;for _,m in ipairs(Modding.GetInstalledMods()) do if wanted[m.Id]~=nil then assert(m.Enabled==wanted[m.Id],m.Id);end;end;Automation.SetAutoStartEnabled('''+str(original['auto_start']).lower()+');assert(Automation.IsAutoStartEnabled()=='+str(original['auto_start']).lower()+');'
  self.cmd(code,'PlotInfo','restore-live-preferences',wait=3)
  write(self.out/'preferences-restored.json',{'verified':True,'mods':len(original['mods']),'auto_start':original['auto_start'],'context':'PlotInfo while current loaded game remains open'})
 def export_movement(self):
  text=self.cmd("for _,r in ipairs(CSC_AI_Research.visibleCensus) do print('CSC_VISIBLE_CENSUS',r[1],r[2],r[3],r[4],r[5],r[6],r[7]);end;for _,r in ipairs(CSC_AI_Research.visibleMoves) do print('CSC_VISIBLE_MOVE',r[1],r[2],r[3],r[4],r[5]);end;",'CSC_AI_Research','actual-visible-movement',wait=3)
  rows=[dict(turn=int(t),player=int(p),kind=k,id=int(i),type=typ,x=int(x),y=int(y)) for t,p,k,i,typ,x,y in re.findall(r'CSC_VISIBLE_CENSUS\s+(\d+)\s+(\d+)\s+(\w+)\s+(\d+)\s+(\w+)\s+(-?\d+)\s+(-?\d+)',text)]
  assert rows,'No unit/city census';write(self.out/'movement-censuses.json',rows)
  moves=[dict(turn=int(t),player=int(p),id=int(i),x=int(x),y=int(y)) for t,p,i,x,y in re.findall(r'CSC_VISIBLE_MOVE\s+(\d+)\s+(\d+)\s+(\d+)\s+(-?\d+)\s+(-?\d+)',text)];write(self.out/'unit-move-events.json',moves)
  return rows,moves
 def show(self):
  rows=[]
  for step in range(1,16):
   # A native round, followed by a real pause for viewing. No forced unit moves.
   self.cmd('Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(0);AutoplayManager.SetTurns(1);AutoplayManager.SetActive(true);','GameCore_Tuner','visible-one-round')
   deadline=time.monotonic()+180
   while time.monotonic()<deadline:
    time.sleep(3);text=self.cmd("print('CSC_FIXED_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());",label='visible-poll')
    turn,active=re.findall(r'CSC_FIXED_PROGRESS\s+(\d+)\s+(true|false)',text)[-1]
    if active=='false':break
   else:raise RuntimeError('Visible native round stalled; no automatic restart')
   rows=self.export_choices();census,moves=self.export_movement();self.status('watching',turn=int(turn),step=step,observations=len(rows),movement_events=len(moves))
   self.say(f'Visible ON: turn{turn}; {len(rows)} completed AI turns, {len(moves)} movement events.')
   try:chosen=observation_window(rows)
   except AssertionError:chosen=None
   if chosen is not None:break
   time.sleep(12)
  else:raise RuntimeError('Exact 12-round observation window not reached')
  write(self.out/'choices.json',chosen);write(self.out/'choices-raw.json',rows)
  unique={}
  for r in census:
   if r['kind']=='UNIT':unique.setdefault((r['player'],r['id'],r['type']),set()).add((r['x'],r['y']))
  changed=[{'player':p,'id':i,'type':typ,'distinct_positions':len(pos)} for (p,i,typ),pos in unique.items() if len(pos)>1]
  initial={(r['player'],r['id']) for r in census if r['kind']=='CITY' and r['turn']==71}
  final={(r['player'],r['id']) for r in census if r['kind']=='CITY'}
  result=dict(version=VERSION,research=summary(chosen),observed_turns=[71,82],actual_endpoint=int(turn),units_with_changed_positions=changed,new_city_ids=sorted(final-initial),move_event_count=len(moves),left_game_open=True,not_paired_statistical_data=True)
  write(self.out/'result.json',result);return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 r=VisibleRunner(a.output);r.fixed_on=True;r.overlay=(HERE/'fixed_research_control.sql').read_text(encoding='utf-8');r.keep_game=False
 r.captures=Path.home()/'Desktop/Codex/csc-implemented-native-20261016';r.baseline=Path.home()/'Desktop/Codex/csc-ai-paired-standard-20261016';r.previous=Path.home()/'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
 installed=INSTALLED/'Data/CSC_AI.sql';original=installed.read_bytes();assert original==SOURCE.read_bytes();(a.output/'original-installed-CSC_AI.sql').write_bytes(original)
 try:
  r.status('preparing');r.wait('MainMenu',30);installed.write_bytes(original+b'\n'+r.overlay.encode());r.pin_sources();r.archive_version();r.config();r.start_pair(1);r.prepare_view()
  r.status('ready',turn=71,map_revealed=True,waiting_for=str(a.output/'viewer-ready.json'))
  # Human acknowledgement prevents the demonstration finishing offscreen.
  deadline=time.monotonic()+1800
  while not (a.output/'viewer-ready.json').exists():
   if time.monotonic()>deadline:raise TimeoutError('Viewing readiness not received; no autoplay started')
   time.sleep(2)
  r.show()
  if hasattr(r,'original_animation'):
   m,c=[str(x).lower() for x in r.original_animation];r.cmd(f'UserConfiguration.SetValue("QuickMovement",{m});UserConfiguration.SetValue("QuickCombat",{c});','PlotInfo','restore-animation')
  r.status('complete',left_game_open=True)
 except BaseException as e:
  write(a.output/'failure.json',{'error':str(e),'traceback':traceback.format_exc()});r.status('failed',error=str(e),no_automatic_restart=True)
  # Preserve the visible game rather than hiding it on a controller failure.
  try:r.cmd('AutoplayManager.SetActive(false);','GameCore_Tuner','stop-on-failure')
  except Exception:pass
  raise
 finally:
  installed.write_bytes(original);write(a.output/'installed-restored.json',{'verified':installed.read_bytes()==original,'sha256':sha(installed),'source_unchanged':SOURCE.read_bytes()==original})

if __name__=='__main__':main()
