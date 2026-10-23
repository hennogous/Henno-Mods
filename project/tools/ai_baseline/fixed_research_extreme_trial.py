"""Fresh Medieval OFF/ON games testing an extreme fixed trait-owned civic preference.

Never reloads historical starts, restarts failed games or edits Workshop/source SQL.
The disposable installed overlay and original mod preferences are restored.
"""
import argparse,csv,hashlib,json,os,re,shutil,sqlite3,subprocess,sys,time,traceback,uuid,zlib
from pathlib import Path
from research_priorities_trial import MedievalRunner
from paired_standard import HERE,read,sha
from run import ROOT,LOGS,write,Runner
from tuner_read_retry import retry_read,IncompleteTunerRead

VERSION='fixed-naval-favored1-value10000-v1-matched-short'
INSTALLED=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
SOURCE=ROOT/'Civ Supply Chains/Data/CSC_AI.sql'
LIST='CSC_AI_FIXED_SERVICE_CIVICS'

def inventory(db):
 return {t:hashlib.sha256(repr(sorted(db.execute('SELECT * FROM "'+t+'"').fetchall(),key=repr)).encode()).hexdigest() for t, in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()}

def observation_window(rows,start=71,rounds=12):
 expected={(turn,pid) for turn in range(start,start+rounds) for pid in range(1,6)}
 selected=[r for r in rows if (r['turn'],r['player']) in expected]
 assert len(selected)==len(expected) and {(r['turn'],r['player']) for r in selected}==expected,'Incomplete or duplicated player-turn observation window'
 return selected

def parse_history(text,request):
 blocks=re.findall(r'CSC_FIXED_HISTORY_BEGIN\s+'+request+r'\s+(\d+)(.*?)CSC_FIXED_HISTORY_END\s+'+request+r'\s+(\d+)',text,re.S)
 if not blocks:raise IncompleteTunerRead('Missing complete choice-history response')
 before,body,after=blocks[-1]
 rows=[{'turn':int(t),'player':int(pid),'civic':c,'naval_completed':done=='true'} for t,pid,c,done in re.findall(r'CSC_FIXED_CHOICE\s+(\d+)\s+(\d+)\s+(\S+)\s+(true|false)',body)]
 if int(before)!=int(after) or len(rows)!=int(after):raise IncompleteTunerRead('Truncated choice-history response')
 return rows

class FixedRunner(MedievalRunner):
 def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
  # Keep inherited era/fixture adaptation, but avoid nested retry loops. Only
  # whitelisted queries are resent; fixture creation/autoplay/hosting send once.
  if label.startswith('start-'):
   code=code.replace('ReleasePlayerParameters();',"GameConfiguration.SetValue('CSC_RESOURCE_MAP_ASSISTANCE',1);GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);GameConfiguration.SetStartEra(DB.MakeHash('ERA_MEDIEVAL'));assert(GameConfiguration.GetStartEra()==DB.MakeHash('ERA_MEDIEVAL'));ReleasePlayerParameters();")
  if getattr(self,'start_turn',None) and state!='MainMenu':code=code.replace('Game.GetCurrentGameTurn()==1','Game.GetCurrentGameTurn()=='+str(self.start_turn))
  readonly=label in {'fixed-poll','fixed-choice-history','fixed-choice-observer-check','fixed-loaded-basics','initial-civic-choices','verify-start-era','dump-medieval','fixture-endpoint','verify-restored-preferences'} or label.startswith(('snapshot-','research-','builders-','actual-','dump-'))
  def send(attempt):
   text=Runner.cmd(self,code,state,label if attempt==1 else label+'-retry'+str(attempt),max(wait,3 if readonly else 5),check)
   if label=='fixed-poll' and not re.search(r'CSC_FIXED_PROGRESS\s+\d+\s+(true|false)',text):raise IncompleteTunerRead('Missing progress payload')
   if label=='fixed-choice-history':parse_history(text,self.history_request)
   return text
  if not readonly:return send(1)
  def notice(attempt,error,delay):
   record={'label':label,'attempt':attempt,'delay_seconds':delay,'error':str(error)[-500:],'unix':time.time()}
   self.read_retries=getattr(self,'read_retries',[])+[record];write(self.out/'read-retries.json',self.read_retries)
   self.say('Temporary Tuner read failure ('+label+'); retrying in '+str(delay)+'s. Last saved observations retained.')
  return retry_read(send,notice)
 def pin_sources(self):
  super().pin_sources();p=self.out/'tuning-source-hashes.json';pins=read(p)
  for f in (Path(__file__),HERE/'fixed_research_control.sql',HERE/'tuner_read_retry.py'):pins[str(f)]=sha(f)
  write(p,pins)
 def archive_version(self):
  super().archive_version();p=self.out/'source-version/version.json';v=read(p)
  v.update(code_version=VERSION,arm='on' if self.fixed_on else 'off',research={'fixed_trait':'TRAIT_LEADER_MAJOR_CIV','system':'Civics','item':'CIVIC_NAVAL_TRADITION','favored':1,'value':10000,'enabled':self.fixed_on,'dynamic_preference_links':0},fresh_native_start=True)
  write(p,v);(self.out/'source-version/applied-overlay.sql').write_text(self.overlay,encoding='utf-8')
 def finish_preflight(self,i):
  self.cmd((HERE/'builder_export.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-export',wait=1);self.builder_snapshot(1)
  self.cmd("assert(GameInfo.PseudoYields.PSEUDOYIELD_IMPROVEMENT.DefaultValue==90);local n=0;for r in GameInfo.AiFavoredItems() do if r.ListType=='UnitPriorityBoosts' and r.Item=='UNIT_BUILDER' then assert(r.Value==50);n=n+1;end;end;assert(n==1);assert(CSC_AI_Research);",'CSC_AI_Research','fixed-loaded-basics',wait=1)
  cache=Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite"
  src=sqlite3.connect(cache.as_uri()+'?mode=ro',uri=True);db=sqlite3.connect(':memory:');src.backup(db);src.close()
  assert db.execute('SELECT LeaderType,System FROM AiLists WHERE ListType=?',(LIST,)).fetchall()==[('TRAIT_LEADER_MAJOR_CIV','Civics')]
  expected=[('CIVIC_NAVAL_TRADITION',1,10000)] if self.fixed_on else []
  assert db.execute('SELECT Item,Favored,Value FROM AiFavoredItems WHERE ListType=?',(LIST,)).fetchall()==expected
  assert db.execute("SELECT COUNT(*) FROM Strategy_Priorities WHERE StrategyType LIKE 'STRATEGY_CSC_AI_SERVICE_%'").fetchone()[0]==0
  assert db.execute('SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType=?',('PSEUDOYIELD_IMPROVEMENT',)).fetchone()[0]==90
  assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall()==[(50,)]
  dst=sqlite3.connect(self.out/'native-gameplay.sqlite');db.backup(dst);dst.close()
  once=inventory(db);db.create_function('Make_Hash',1,lambda s:zlib.crc32(s.encode()))
  db.executescript(SOURCE.read_text(encoding='utf-8')+'\n'+self.overlay)
  assert inventory(db)==once,'Native source+overlay replay changed database'
  write(self.out/'native-database-validation.json',{'passed':True,'fixed_on':self.fixed_on,'fixed_rows':expected,'dynamic_priority_links':0,'replay_identical':True,'inventory':once})
  settings=read(self.out/'game-01/settings.json');settings.update(code_version=VERSION,arm='on' if self.fixed_on else 'off',ai='Fixed Naval favored1/value10000; dynamic priorities disconnected; other treatment unchanged',observed_turns=[71,82],observed_rounds=12,native_autoplay_turns=13);write(self.out/'game-01/settings.json',settings)
 def export_choices(self):
  self.history_request=uuid.uuid4().hex
  request=json.dumps(self.history_request)
  text=self.cmd("local history=CSC_AI_Research.fixedHistory or {};print('CSC_FIXED_HISTORY_BEGIN',"+request+",#history);for _,r in ipairs(history) do print('CSC_FIXED_CHOICE',r[1],r[2],r[3],r[4]);end;print('CSC_FIXED_HISTORY_END',"+request+",#history);",'CSC_AI_Research','fixed-choice-history',wait=3)
  rows=parse_history(text,self.history_request)
  prior=self.out/'choices-latest.json'
  if prior.exists():
   previous=read(prior);assert len(rows)>=len(previous) and rows[:len(previous)]==previous,'Choice history changed or regressed; preserving previous file'
  write(self.out/'choices-latest.json',rows)
  return rows
 def choices(self):
  offsets={f.name:{'bytes':f.stat().st_size,'hash':sha(f)} for f in LOGS.iterdir() if f.is_file()}
  self.cmd("for pid=1,5 do local p=Players[pid];local c=p:GetCulture():GetProgressingCivic();local d=GameInfo.Civics[c];print('CSC_FIXED_BEFORE_FIXTURE',pid,d and d.CivicType or 'NONE');end;",'CSC_AI_Research','initial-civic-choices',wait=1)
  self.cmd((HERE/'research_choice_fixture.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','fixed-choice-fixture',wait=2)
  self.cmd("CSC_AI_Research.Invalidate();for pid=1,5 do assert(CSC_AI_Research.Evaluate(pid,4));end;local R=CSC_AI_Research;R.fixedHistory={};Events.PlayerTurnDeactivated.Add(function(pid) if pid>=1 and pid<=5 then local p=Players[pid];local c=p:GetCulture():GetProgressingCivic();local d=GameInfo.Civics[c];R.fixedHistory[#R.fixedHistory+1]={Game.GetCurrentGameTurn(),pid,d and d.CivicType or 'NONE',p:GetCulture():HasCivic(GameInfo.Civics.CIVIC_NAVAL_TRADITION.Index)};Game:SetProperty('CSC_FIXED_RESEARCH_HISTORY',R.fixedHistory);end;end);",'CSC_AI_Research','fixed-choice-observer',wait=1)
  # Readiness is audited, but no dynamic strategy has any attached preference list.
  # One extra native round accommodates IsActive/round-boundary timing. Analyze
  # exactly the first12 completed player turns, irrespective of displayed endpoint.
  self.cmd('Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetTurns(13);AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);','GameCore_Tuner','fixed-choice-autoplay',wait=1)
  self.say('Fixed '+('ON' if self.fixed_on else 'OFF')+': native autoplay started; recording player turns71–82.')
  deadline=time.monotonic()+600
  while time.monotonic()<deadline:
   time.sleep(10)
   text=self.cmd("print('CSC_FIXED_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());",'GameCore_Tuner','fixed-poll',wait=1)
   rows=self.export_choices() # Preserve evidence before any endpoint/assertion.
   matches=re.findall(r'CSC_FIXED_PROGRESS\s+(\d+)\s+(true|false)',text);assert matches,'Missing progress';m=(None,*matches[-1])
   write(self.out/'live-status.json',{'status':'running','turn':int(m[1]),'observations_saved':len(rows),'observation_target':60,'updated_unix':time.time()})
   if m[2]=='false':break
  else:raise RuntimeError('Fixed research arm stalled; no restart')
  rows=self.export_choices();write(self.out/'choices-raw.json',rows)
  self.actual_endpoint=int(m[1]);rows=observation_window(rows)
  write(self.out/'choices.json',rows)
  write(self.out/'observation-validation.json',{'passed':True,'actual_simulation_turn':self.actual_endpoint,'analyzed_turns':[71,82],'observations':len(rows),'all_five_players_each_turn':True,'raw_exported_before_validation':True})
  self.cmd('assert(#CSC_AI_Research.errors==0);','CSC_AI_Research','fixed-choice-observer-check',wait=1)
  self.cmd('CSCBASE.snapshot();','CSC_AdjacencyGameplay','fixture-endpoint',wait=2)
  logs=self.out/'native-logs';logs.mkdir()
  for f in LOGS.iterdir():
   if f.is_file():
    data=f.read_bytes();old=offsets.get(f.name)
    if old and len(data)>=old['bytes'] and hashlib.sha256(data[:old['bytes']]).hexdigest()==old['hash']:data=data[old['bytes']:]
    (logs/f.name).write_bytes(data)
  self.check_installed()
  for name in ('tuning-source-hashes.json','controller-source-hashes.json'):
   for p,digest in read(self.out/name).items():assert sha(Path(p))==digest,p
  return rows

def summary(rows):
 return {'players':len({r['player'] for r in rows}),'naval_selected':sorted({r['player'] for r in rows if r['civic']=='CIVIC_NAVAL_TRADITION'}),'naval_completed':sorted({r['player'] for r in rows if r['naval_completed']}),'first_choices':{str(pid):next(x['civic'] for x in rows if x['player']==pid) for pid in range(1,6)},'first_completion_turn':{str(pid):next((x['turn'] for x in rows if x['player']==pid and x['naval_completed']),None) for pid in range(1,6)}}

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--prior-attempt',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 if a.prior_attempt:write(a.output/'controller-repair.json',{'prior_attempt':str(a.prior_attempt),'reason':'Bounded retries for explicitly read-only empty/incomplete Tuner replies, longer response collection, request-specific history framing, durable history in autosaves. ON runs first. Gameplay treatment unchanged.'})
 installed_sql=INSTALLED/'Data/CSC_AI.sql';original=installed_sql.read_bytes();source_digest=sha(SOURCE);assert original==SOURCE.read_bytes(),'Installed/source SQL differ before test'
 (a.output/'original-installed-CSC_AI.sql').write_bytes(original)
 write(a.output/'job-status.json',{'status':'starting','pid':os.getpid(),'version':VERSION})
 cases={};runner=None;overlay=(HERE/'fixed_research_control.sql').read_text(encoding='utf-8').replace("'CIVIC_NAVAL_TRADITION',1,0)","'CIVIC_NAVAL_TRADITION',1,10000)")
 try:
  for on,arm in ((True,'on'),(False,'off')):
   assert sha(SOURCE)==source_digest,'Source SQL changed during test'
   patch=overlay if on else overlay.split('-- ON_ARM_ONLY')[0]
   installed_sql.write_bytes(original+b'\n'+patch.encode('utf-8'))
   runner=FixedRunner(a.output/arm);runner.fixed_on=on;runner.overlay=patch;runner.keep_game=False
   runner.captures=Path.home()/'Desktop/Codex/csc-implemented-native-20261016';runner.baseline=Path.home()/'Desktop/Codex/csc-ai-paired-standard-20261016';runner.previous=Path.home()/'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
   runner.pin_sources();runner.archive_version()
   write(a.output/'active-stage.json',{'stage':arm,'output':str(runner.out),'pid':os.getpid(),'fresh_native_start':True});write(a.output/'job-status.json',{'status':'running','arm':arm,'pid':os.getpid()})
   runner.wait('MainMenu',180);runner.config();runner.start_pair(1)
   if not on:
    assert read(a.output/'on/game-01/initial-map.json')==read(runner.out/'game-01/initial-map.json'),'Fresh native worlds differ'
    assert read(a.output/'on/game-01/turn-071.json')==read(runner.out/'game-01/turn-071.json'),'Fresh initial states differ'
    old=read(a.output/'on/native-database-validation.json')['inventory'];new=read(runner.out/'native-database-validation.json')['inventory'];changed=[k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)];assert changed==['AiFavoredItems'],changed
    write(a.output/'paired-preflight.json',{'initial_worlds_identical':True,'initial_censuses_identical':True,'native_changed_tables':changed,'only_treatment':'One fixed NavalTradition Favored1/Value10000 row from startup; both arms dynamic priorities disconnected'})
   cases[arm]=runner.choices();runner.menu();runner.restore_verified();write(runner.out/'complete.json',{'actual_simulation_turn':runner.actual_endpoint,'analyzed_turns':[71,82],'observations':60,'fixed_on':on,'native_preflight_passed':True})
  result={'code_version':VERSION,'off':summary(cases['off']),'on':summary(cases['on']),'same_choice_completion_history':cases['off']==cases['on'],'paired_preflight':read(a.output/'paired-preflight.json'),'limits':['One seed; fiveAI players share each game and are not independent maps.','Twelve-round synthetic opportunity fixture, not natural placement or250turn performance.','Both arms start fresh; no historical saved native definitions reused.']}
  result['target_response']=len(result['on']['naval_selected'])>len(result['off']['naval_selected']) or len(result['on']['naval_completed'])>len(result['off']['naval_completed'])
  write(a.output/'comparison.json',result)
  lines=['# Fixed Naval Tradition preference — controlled result','','Medieval observed player turns71–82, Online/Prince/Small Continents, Standard resources, CSC only. OFF/ON fresh native worlds and initial censuses identical. Dynamic preference links disconnected in both; ON adds one trait-owned Naval Tradition Favored1/Value10000 row. Actual simulation endpoint retained separately.','','| Metric | OFF | ON |','|---|---:|---:|',f"| Players selecting Naval Tradition | {len(result['off']['naval_selected'])}/5 | {len(result['on']['naval_selected'])}/5 |",f"| Players completing Naval Tradition | {len(result['off']['naval_completed'])}/5 | {len(result['on']['naval_completed'])}/5 |",'','| Player | OFF first civic | ON first civic | OFF Naval complete | ON Naval complete |','|---|---|---|---:|---:|']
  for pid in range(1,6):
   k=str(pid);lines.append('| '+k+' | '+result['off']['first_choices'][k]+' | '+result['on']['first_choices'][k]+' | '+str(result['off']['first_completion_turn'][k])+' | '+str(result['on']['first_completion_turn'][k])+' |')
  lines+=['','Identical complete choice history: '+str(result['same_choice_completion_history']), '',*result['limits']];(a.output/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
  write(a.output/'job-status.json',{'status':'complete','target_response':result['target_response'],'updated_unix':time.time()})
 except BaseException as exc:
  write(a.output/'failure.json',{'error':str(exc),'traceback':traceback.format_exc()})
  if runner:
   try:runner.export_choices()
   except Exception:pass
   runner.archive_failure()
   try:
    runner.states()
    if 'PlotInfo' in runner.state:runner.menu()
    if (runner.out/'original-preferences.json').exists():runner.restore_verified()
   except Exception as cleanup:write(a.output/'cleanup-required.json',{'error':str(cleanup)})
  write(a.output/'job-status.json',{'status':'failed','error':str(exc),'updated_unix':time.time()});raise
 finally:
  installed_sql.write_bytes(original)
  write(a.output/'installed-restored.json',{'verified':installed_sql.read_bytes()==original,'sha256':sha(installed_sql),'source_unchanged':sha(SOURCE)==source_digest})
if __name__=='__main__':main()
