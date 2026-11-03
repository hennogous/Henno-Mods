"""Clean sham/stock/custom native strategy tests; installed-only reversible overlays.

Three short nonresearch calibration worlds, then three 80-round research worlds.
No civic setters, progress grants, crash reruns or model polling loops.
"""
import argparse,csv,hashlib,json,os,re,shutil,sqlite3,sys,time,traceback,uuid,zlib
from pathlib import Path
from fixed_research_trial import FixedRunner,inventory
from improvement_research_trial import ResearchRunner
from paired_standard import HERE,read,sha
from run import ROOT,LOGS,SAVES,Runner,write
from tuner_read_retry import retry_read,IncompleteTunerRead

VERSION='clean-strategies-natural80-v2-save-tolerant'
INSTALLED=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
SQL=Path('Data/CSC_AI.sql')
LUA=Path('Lua_UI/AI/CSC_AI_Research.lua')
LIST='CSC_TEST_RESEARCH_LIST'
CUSTOM='STRATEGY_CSC_TEST_RESEARCH'
STRATEGIES={'stock':'STRATEGY_NAVAL','custom':CUSTOM}
ARMS=('sham','stock','custom')

def overlay(phase,arm):
    text=(HERE/'strategy_research_control.sql').read_text(encoding='utf-8')
    if arm!='sham':
        system,item,value=('Yields','YIELD_CULTURE',1000) if phase=='calibration' else ('Civics','CIVIC_NAVAL_TRADITION',0)
        text+=f"\nINSERT INTO AiListTypes (ListType) VALUES ('{LIST}');\nINSERT INTO AiLists (ListType,System) VALUES ('{LIST}','{system}');\nINSERT INTO AiFavoredItems (ListType,Item,Favored,Value) VALUES ('{LIST}','{item}',1,{value});\nINSERT INTO Strategy_Priorities (StrategyType,ListType) VALUES ('{STRATEGIES[arm]}','{LIST}');\n"
    return text

def native_check(db,phase,arm,patch,source):
    for table in ('AiListTypes','AiLists','AiFavoredItems','Strategy_Priorities'):
        assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%'").fetchone()[0]==0,(table,'residual CSC research rows')
    system,item,value=('Yields','YIELD_CULTURE',1000) if phase=='calibration' else ('Civics','CIVIC_NAVAL_TRADITION',0)
    expected=[] if arm=='sham' else [(item,1,value)]
    assert db.execute('SELECT Item,Favored,Value FROM AiFavoredItems WHERE ListType=?',(LIST,)).fetchall()==expected
    assert db.execute('SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType=?',(LIST,)).fetchall()==([] if arm=='sham' else [(None,None,system)])
    assert db.execute('SELECT StrategyType FROM Strategy_Priorities WHERE ListType=?',(LIST,)).fetchall()==([] if arm=='sham' else [(STRATEGIES[arm],)])
    # No other surviving native list may already favor this civic in the control.
    target=db.execute("SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item='CIVIC_NAVAL_TRADITION'").fetchall()
    assert target==([(LIST,1,0)] if phase=='research' and arm!='sham' else []),target
    conditions=db.execute("SELECT StrategyType,ConditionFunction,StringValue,ThresholdValue FROM StrategyConditions WHERE StrategyType IN ('STRATEGY_NAVAL',?) ORDER BY StrategyType",(CUSTOM,)).fetchall()
    assert conditions==[(CUSTOM,'Call Lua Function','CSC_TestResearchAlways',2),('STRATEGY_NAVAL','Call Lua Function','CSC_TestResearchAlways',1)],conditions
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0]==90
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall()==[(50,)]
    before=inventory(db);db.create_function('Make_Hash',1,lambda s:zlib.crc32(s.encode()))
    db.executescript(source+'\n'+patch)
    assert inventory(db)==before,'Native source+overlay replay differs'
    return {'passed':True,'phase':phase,'arm':arm,'fixed_rows':expected,'residual_csc_research_lists':0,'only_naval_items':target,'strategy_conditions':conditions,'replay_identical':True,'inventory':before}

def framed_export(text,request):
    block=re.search(r'CSC_TEST_EXPORT_BEGIN\s+'+request+r'\s+(\d+)\s+(\d+)(.*?)CSC_TEST_EXPORT_END\s+'+request+r'\s+(\d+)\s+(\d+)',text,re.S)
    if not block:raise IncompleteTunerRead('Incomplete observer export framing')
    match=re.search(r'CSC_TEST_EXPORT=([^\r\n]+)',block[3])
    if not match:raise IncompleteTunerRead('Missing observer JSON')
    try:data=json.loads(match[1])
    except json.JSONDecodeError as exc:raise IncompleteTunerRead('Truncated observer JSON') from exc
    if int(block[1])!=int(block[4]) or len(data['history'])!=int(block[1]) or int(block[2])!=int(block[5]) or len(data['completions'])!=int(block[2]):raise IncompleteTunerRead('Observer row count mismatch')
    return data

class StrategyRunner(FixedRunner):
    def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
        # Retain proven start-era setup. Only explicit read calls may be retried.
        if label.startswith('start-'):
            self.offsets={p.name:{'bytes':p.stat().st_size,'hash':sha(p)} for p in LOGS.iterdir() if p.is_file()}
            code=code.replace('ReleasePlayerParameters();',"GameConfiguration.SetValue('CSC_RESOURCE_MAP_ASSISTANCE',1);GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);GameConfiguration.SetStartEra(DB.MakeHash('ERA_MEDIEVAL'));ReleasePlayerParameters();")
        if getattr(self,'start_turn',None) and state!='MainMenu':code=code.replace('Game.GetCurrentGameTurn()==1','Game.GetCurrentGameTurn()=='+str(self.start_turn))
        readonly=label.startswith(('research-','snapshot-','builders-','actual-','dump-')) or label in ('verify-start-era','verify-restored-preferences','probe-loaded','probe-fixture-census')
        def send(attempt):
            text=Runner.cmd(self,code,state,label if attempt==1 else label+'-retry'+str(attempt),max(wait,4 if readonly else 5),check)
            if label=='research-probe-export':framed_export(text,self.request)
            if label=='research-probe-poll' and not re.search(r'CSC_TEST_PROGRESS\s+\d+\s+(true|false)',text):raise IncompleteTunerRead('Missing progress record')
            return text
        def notice(attempt,error,delay):
            entries=getattr(self,'read_retries',[]);entries.append({'label':label,'attempt':attempt,'error':str(error)[-500:],'unix':time.time()});self.read_retries=entries;write(self.out/'read-retries.json',entries)
        return retry_read(send,notice) if readonly else send(1)

    def pin_sources(self):
        super().pin_sources();path=self.out/'tuning-source-hashes.json';pins=read(path)
        for name in ('strategy_research_trial.py','strategy_research_control.sql','strategy_research_callbacks.lua','strategy_research_observer.lua','strategy_research_fixture.lua'):
            f=HERE/name;pins[str(f)]=sha(f)
        write(path,pins)

    def archive_version(self):
        ResearchRunner.archive_version(self)
        path=self.out/'source-version/version.json';v=read(path)
        v.update(code_version=VERSION,phase=self.phase,arm=self.arm,research={'target':'CIVIC_NAVAL_TRADITION','favored':1,'value':0,'old_lists_removed':True,'attachment':STRATEGIES.get(self.arm),'no_current_civic_reset':True},rounds=self.rounds,positive_control='Separate disposable System=Yields Culture1000 calibration; absent from research games')
        write(path,v);(path.parent/'applied-overlay.sql').write_text(self.overlay,encoding='utf-8')

    def save_checkpoint(self,i,turn):
        try:
            return self.confirm_save_checkpoint(i,turn)
        except Exception as exc:
            if turn==1:raise
            # Optional archival IO must not discard valid native observations.
            warning={'requested_turn':turn,'error':str(exc)[-2000:],'initial_save_required':False,'unix':time.time()}
            write(self.out/f'save-warning-{turn}.json',warning)
            self.say(f'Optional save at about{turn} not confirmed; native observations retained.')
            auto=SAVES/'auto';dst=self.out/'checkpoint-autosaves';dst.mkdir(exist_ok=True)
            records=[]
            for f in sorted(auto.glob('*.Civ6Save'),key=lambda p:p.stat().st_mtime,reverse=True)[:3]:
                target=dst/f.name;shutil.copy2(f,target);records.append({'path':str(target),'sha256':sha(target),'file_mtime':f.stat().st_mtime})
            write(self.out/f'autosave-fallback-{turn}.json',{'requested_turn':turn,'native_autosaves':records,'named_save_not_confirmed':True})
            if turn>=71+self.rounds:
                write(self.out/'game-01/endpoint-save.json',{'named_save_not_confirmed':True,'observed_endpoint_turn':turn,'native_autosaves':records,'kind':'preserved native autosave fallback; filename turns require metadata interpretation'})
            return False

    def confirm_save_checkpoint(self,i,turn):
        text=self.cmd("print('CSC_TEST_SAVE_TURN',Game.GetCurrentGameTurn());",'GameCore_Tuner','actual-save-turn')
        actual=int(re.search(r'CSC_TEST_SAVE_TURN\s+(\d+)',text)[1])
        name=f'CSC_STRATEGY_20261020_{self.phase}_{self.arm}_{actual:03d}';path=SAVES/(name+'.Civ6Save');stamp=time.time()
        self.cmd('local s={Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);','PlotInfo','probe-save-'+str(actual),wait=5)
        for _ in range(20):
            if path.exists() and path.stat().st_mtime>=stamp-2 and path.stat().st_size:
                size=path.stat().st_size;time.sleep(1)
                if path.stat().st_size==size:
                    dst=self.out/'game-01'/path.name;shutil.copy2(path,dst)
                    label='initial-save.json' if turn==1 else ('endpoint-save.json' if actual>=71+self.rounds else f'checkpoint-save-{actual}.json')
                    write(self.out/'game-01'/label,{'path':str(path),'sha256':sha(dst),'turn_observed_before_request':actual,'actual_turn':actual if turn==1 or actual>=71+self.rounds else None,'kind':'confirmed named native save'});return True
            time.sleep(1)
        raise RuntimeError('Native save was not confirmed')

    def finish_preflight(self,i):
        self.reset_logs=set()
        for name,old in self.offsets.items():
            p=LOGS/name
            if p.exists():
                data=p.read_bytes()
                if len(data)<old['bytes'] or hashlib.sha256(data[:old['bytes']]).hexdigest()!=old['hash']:self.reset_logs.add(name)
        write(self.out/'native-log-offsets.json',{'before_host':self.offsets,'reset_detected_during_load':sorted(self.reset_logs)})
        self.cmd("assert(CSC_RESEARCH_PROBE_NATIVE and CSC_RESEARCH_PROBE_NATIVE.version=='clean-strategy-natural-decisions-v1');",'CSC_AI_Research','probe-loaded')
        cache=Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite"
        src=sqlite3.connect(cache.as_uri()+'?mode=ro',uri=True);db=sqlite3.connect(':memory:');src.backup(db);src.close()
        dst=sqlite3.connect(self.out/'native-gameplay.sqlite');db.backup(dst);dst.close()
        validation=native_check(db,self.phase,self.arm,self.overlay,(ROOT/'Civ Supply Chains'/SQL).read_text(encoding='utf-8'));write(self.out/'native-database-validation.json',validation)
        settings=read(self.out/'game-01/settings.json');settings.update(code_version=VERSION,phase=self.phase,arm=self.arm,target_turn=71+self.rounds+1,analyzed_turns=[71,70+self.rounds],observed_rounds=self.rounds,ai='Baseline40/80/improvement90/Builder50/native12/4/10; old research lists removed; clean test strategy route');write(self.out/'game-01/settings.json',settings)
        write(self.out/'checkpoint-layout.json',{'initial_actual_turn':71,'initial_alias':'turn-001.json is a legacy alias for actual71, not an Ancient start','observed_player_turns':[71,70+self.rounds],'primary_censuses':['initial71','fixture71','actual_endpoint'],'native_save_interval_approx':25,'no_natural250_run':True})

    def export_probe(self):
        self.request=uuid.uuid4().hex
        text=self.cmd('CSC_RESEARCH_PROBE.Export('+json.dumps(self.request)+');','CSC_AI_Research','research-probe-export',wait=5)
        data=framed_export(text,self.request)
        previous=self.out/'observations-latest.json'
        if previous.exists():
            old=read(previous);assert len(data['history'])>=len(old['history']) and data['history'][:len(old['history'])]==old['history'],'Observation prefix changed'
        write(previous,data);return data

    def observe(self):
        self.cmd((HERE/'strategy_research_fixture.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','probe-opportunity-fixture',wait=5)
        # Freeze a full starting fixture census for parity, not a planner reset.
        text=self.cmd('local old=CSCBASE.checkpoints[71];CSCBASE.checkpoints[71]=nil;CSCBASE.snapshot(71);CSCBASE.checkpoints[71]=old;','CSC_AdjacencyGameplay','probe-fixture-census',wait=3)
        payload=json.loads(re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)',text)[1]);assert payload['turn']==71 and not payload['errors']
        write(self.out/'fixture-census.json',payload)
        if getattr(self,'fixture_reference',None):assert payload==read(self.fixture_reference),'Opportunity fixture censuses differ'
        self.cmd((HERE/'strategy_research_observer.lua').read_text(encoding='utf-8'),'CSC_AI_Research','probe-observer-install',wait=4);self.observer_active=True
        self.export_probe()
        self.cmd('Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetTurns('+str(self.rounds+1)+');AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);','GameCore_Tuner','probe-autoplay',wait=4)
        self.say(f'{self.phase}/{self.arm}: native autoplay started, analyzing {self.rounds} completed rounds71–{70+self.rounds}.')
        deadline=time.monotonic()+5400;last_turn=71;last_change=time.monotonic();last_checkpoint=71
        while time.monotonic()<deadline:
            time.sleep(20)
            text=self.cmd("print('CSC_TEST_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());",'GameCore_Tuner','research-probe-poll')
            turn,active=re.findall(r'CSC_TEST_PROGRESS\s+(\d+)\s+(true|false)',text)[-1];turn=int(turn)
            if turn!=last_turn:last_turn=turn;last_change=time.monotonic()
            data=self.export_probe();assert not data['errors'] and not data['native']['errors'],data['errors']
            write(self.out/'live-status.json',{'status':'running','phase':self.phase,'arm':self.arm,'turn':turn,'target_approx':71+self.rounds,'observations_saved':len(data['history']),'updated_unix':time.time()})
            if turn-last_checkpoint>=25:
                self.save_checkpoint(1,turn);last_checkpoint=turn
            if active=='false':break
            if time.monotonic()-last_change>600:raise RuntimeError('Native autoplay stalled for ten minutes')
        else:raise RuntimeError('Native arm exceeded bounded runtime')
        data=self.export_probe();write(self.out/'observations-raw.json',data)
        selected=[r for r in data['history'] if 71<=r['turn']<71+self.rounds]
        keys={(r['turn'],r['player']) for r in selected};assert len(selected)==len(keys),'Duplicate player-turn rows'
        expected={(t,p) for t in range(71,71+self.rounds) for p in range(1,6)}
        missing=expected-keys;defeats={r['player']:r['turn'] for r in data['defeats']}
        assert all(p in defeats and t>=defeats[p] for t,p in missing),('Unexplained missing observations',sorted(missing))
        assert turn>=71+self.rounds,'Early native endpoint'
        write(self.out/'observations.json',{'history':selected,'completions':[r for r in data['completions'] if 71<=r['turn']<71+self.rounds],'initial':data['initial'],'native':data['native'],'defeats':data['defeats']})
        write(self.out/'observation-validation.json',{'passed':True,'actual_endpoint':turn,'analyzed_turns':[71,70+self.rounds],'observations':len(selected),'expected_uncensored':5*self.rounds,'censored_pairs':sorted(missing),'no_research_setters':True})
        self.snapshot(1,turn)
        self.save_checkpoint(1,turn)
        self.archive_native_logs()
        victory=(self.out/'native-logs/AI_Victories.csv').read_text(errors='replace')
        following={}
        for pid in range(1,6):
            for name in STRATEGIES.values():
                matches=re.findall(r'^\s*(\d+),\s*'+str(pid)+r',\s*'+name+r',\s*Following\s*$',victory,re.M)
                assert matches,('No native Following evidence',pid,name)
                following[f'{pid}:{name}']=min(map(int,matches))
        write(self.out/'strategy-activation-validation.json',{'passed':True,'first_following':following,'first_callback_true':data['native']['first_true']})
        self.check_installed()
        for name in ('tuning-source-hashes.json','controller-source-hashes.json'):
            for file,digest in read(self.out/name).items():assert sha(Path(file))==digest,file
        self.actual_endpoint=turn
        return read(self.out/'observations.json')

    def archive_native_logs(self):
        target=self.out/'native-logs';target.mkdir(exist_ok=True)
        for p in LOGS.iterdir():
            if p.is_file():
                data=p.read_bytes();old=getattr(self,'offsets',{}).get(p.name)
                if old and p.name not in getattr(self,'reset_logs',set()) and len(data)>=old['bytes'] and hashlib.sha256(data[:old['bytes']]).hexdigest()==old['hash']:data=data[old['bytes']:]
                (target/p.name).write_bytes(data)

def decision_summary(data):
    out={}
    for pid in range(1,6):
        rows=[r for r in data['history'] if r['player']==pid]
        completions=[r for r in data['completions'] if r['player']==pid]
        boundaries=[]
        for event in completions:
            after=next((r for r in rows if r['turn']>=event['turn'] and r['civic'] not in ('NONE',event['civic'])),None)
            if after:
                boundaries.append({'completed':event['civic'],'completion_turn':event['turn'],'next_observed':after['civic'],'selection_observed_turn':after['turn'],'stock_active_before':after.get('stock_first_true',99999)<after['turn'],'custom_active_before':after.get('custom_first_true',99999)<after['turn']})
        selected=next((r['turn'] for r in rows if r['civic']=='CIVIC_NAVAL_TRADITION'),None)
        completed=next((r['turn'] for r in rows if r['naval_completed']),None)
        calibrated=[b for b in boundaries if b['stock_active_before'] and b['custom_active_before']]
        out[str(pid)]={'naval_first_observed':selected,'naval_completed':completed,'natural_completion_events':len(completions),'verified_next_selections':boundaries,'decision_opportunities_after_both_active':len(calibrated),'initial_civic':next(r['civic'] for r in data['initial'] if r['player']==pid)}
    return {'naval_selected':sum(r['naval_first_observed'] is not None for r in out.values()),'naval_completed':sum(r['naval_completed'] is not None for r in out.values()),'players':out}

def calibration_summary(root):
    samples={}
    for arm in ARMS:
        rows={}
        for line in (root/'calibration'/arm/'native-logs/AI_CityBuild.csv').read_text(errors='replace').splitlines():
            m=re.search(r'^\s*(\d+),\s*(\d+),\s*([^,]+),.*YIELD_CULTURE:\s*([-\d.]+)',line)
            if m and int(m[2]) in range(1,6) and int(m[1])==72:rows[(int(m[1]),int(m[2]),m[3].strip())]=float(m[4])
        samples[arm]=rows
    result={}
    for arm in ('stock','custom'):
        keys=samples['sham'].keys()&samples[arm].keys()
        deltas=[{'turn':k[0],'player':k[1],'city':k[2],'sham_culture_weight':samples['sham'][k],'treatment_culture_weight':samples[arm][k],'delta':round(samples[arm][k]-samples['sham'][k],5)} for k in sorted(keys)]
        result[arm]={'matched_weight_rows':len(deltas),'planned_measurement_available':bool(deltas),'players_with_increased_weight':sorted({r['player'] for r in deltas if r['delta']>0.01}),'measurable_response':any(r['delta']>0.01 for r in deltas) if deltas else None,'rows':deltas}
    result['interpretation']='Separate nonresearch Yields consumer control, not proof of research-list consumption; no diagnostic weights occur in research worlds.'
    return result

def preflight(output):
    old=Path.home()/'Desktop/Codex/csc-ai-fixed-extreme-20261019/retry-02/off/native-gameplay.sqlite'
    outcomes={};inventories={}
    source=(ROOT/'Civ Supply Chains'/SQL).read_text(encoding='utf-8')
    for phase in ('calibration','research'):
        for arm in ARMS:
            original=sqlite3.connect(old.as_uri()+'?mode=ro',uri=True);db=sqlite3.connect(':memory:');original.backup(db);original.close()
            db.create_function('Make_Hash',1,lambda s:zlib.crc32(s.encode()))
            patch=overlay(phase,arm);db.executescript(patch);validation=native_check(db,phase,arm,patch,source)
            outcomes[f'{phase}/{arm}']={k:v for k,v in validation.items() if k!='inventory'};inventories[(phase,arm)]=validation['inventory']
    for phase in ('calibration','research'):
        a,b=inventories[(phase,'stock')],inventories[(phase,'custom')]
        assert [k for k in a if a[k]!=b[k]]==['Strategy_Priorities']
    write(output,{'passed':True,'cases':outcomes,'stock_vs_custom_only_strategy_link_changes':True})

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--preflight-only',action='store_true');p.add_argument('--continue-study',action='store_true');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=a.continue_study);preflight(a.output/('offline-native-preflight-v2.json' if a.continue_study else 'offline-native-preflight.json'))
    if a.preflight_only:return
    originals={rel:(INSTALLED/rel).read_bytes() for rel in (SQL,LUA)}
    for rel,data in originals.items():
        assert data==(ROOT/'Civ Supply Chains'/rel).read_bytes(),('Installed/source differ',str(rel))
        backup=a.output/'original-installed'/rel;backup.parent.mkdir(parents=True,exist_ok=True)
        if backup.exists():assert backup.read_bytes()==data,('Original backup differs',str(rel))
        else:backup.write_bytes(data)
    runner=None;results={};reference={};native_reference={}
    write(a.output/'job-status.json',{'status':'starting','pid':os.getpid(),'code_version':VERSION})
    try:
        for phase in ('calibration','research'):
            for arm in ARMS:
                for rel,data in originals.items():assert (ROOT/'Civ Supply Chains'/rel).read_bytes()==data,('Pinned source changed',str(rel))
                completed=a.output/phase/arm
                if a.continue_study and (completed/'complete.json').exists():
                    for gate in ('complete.json','native-database-validation.json','paired-preflight.json','observation-validation.json','strategy-activation-validation.json'):
                        assert read(completed/gate)['passed'],('Invalid reuse gate',phase,arm,gate)
                    assert read(completed/'preferences-restored.json')['verified']
                    values={'world':read(completed/'game-01/initial-map.json'),'census':read(completed/'game-01/turn-071.json'),'preferences':read(completed/'original-preferences.json')}
                    if not reference:reference=values
                    else:assert values==reference,('Reused initial worlds differ',phase,arm)
                    if arm=='sham':native_reference[phase]=read(completed/'native-database-validation.json')['inventory']
                    results[f'{phase}/{arm}']=decision_summary(read(completed/'observations.json'))
                    continue
                patch=overlay(phase,arm)
                (INSTALLED/SQL).write_bytes(originals[SQL]+b'\n'+patch.encode())
                (INSTALLED/LUA).write_bytes(originals[LUA]+b'\n'+(HERE/'strategy_research_callbacks.lua').read_bytes())
                runner=StrategyRunner(a.output/phase/arm);runner.phase=phase;runner.arm=arm;runner.rounds=2 if phase=='calibration' else 80;runner.overlay=patch;runner.keep_game=False
                if phase!='calibration' or arm!='sham':runner.fixture_reference=a.output/'calibration/sham/fixture-census.json'
                runner.captures=Path.home()/'Desktop/Codex/csc-implemented-native-20261016';runner.baseline=Path.home()/'Desktop/Codex/csc-ai-paired-standard-20261016';runner.previous=Path.home()/'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
                runner.pin_sources();runner.archive_version();write(a.output/'active-stage.json',{'phase':phase,'arm':arm,'output':str(runner.out),'pid':os.getpid()});write(a.output/'job-status.json',{'status':'running','phase':phase,'arm':arm,'pid':os.getpid()})
                runner.wait('MainMenu',180);runner.config();runner.start_pair(1)
                native=read(runner.out/'native-database-validation.json')['inventory']
                if not reference:
                    reference={'world':read(runner.out/'game-01/initial-map.json'),'census':read(runner.out/'game-01/turn-071.json'),'preferences':read(runner.out/'original-preferences.json')}
                else:
                    assert read(runner.out/'game-01/initial-map.json')==reference['world'],'Fresh maps differ'
                    assert read(runner.out/'game-01/turn-071.json')==reference['census'],'Fresh initial censuses differ'
                    assert read(runner.out/'original-preferences.json')==reference['preferences'],'Original preferences differ'
                if arm=='sham':native_reference[phase]=native
                else:
                    changed={k for k in native if native[k]!=native_reference[phase][k]}
                    assert changed<={'AiLists','AiListTypes','AiFavoredItems','Strategy_Priorities'},changed
                    if arm=='custom':
                        old=read(a.output/phase/'stock/native-database-validation.json')['inventory'];assert {k for k in native if native[k]!=old[k]}=={'Strategy_Priorities'}
                write(runner.out/'paired-preflight.json',{'passed':True,'initial_world_identical':True,'initial_census_identical':True,'preferences_identical':True,'arm':arm,'phase':phase})
                observations=runner.observe();results[f'{phase}/{arm}']=decision_summary(observations)
                runner.menu();runner.restore_verified();write(runner.out/'complete.json',{'passed':True,'phase':phase,'arm':arm,'actual_endpoint':runner.actual_endpoint,'rounds_analyzed':runner.rounds})
            if phase=='calibration':write(a.output/'calibration-result.json',calibration_summary(a.output))
        result={'code_version':VERSION,'native_run_versions':{f'{phase}/{arm}':read(a.output/phase/arm/'source-version/version.json')['code_version'] for phase in ('calibration','research') for arm in ARMS},'research':{arm:results['research/'+arm] for arm in ARMS},'calibration':read(a.output/'calibration-result.json'),'limits':['One matched seed; five AI players per world are not independent maps.','Synthetic material/Service opportunity fixtures, not natural placement performance.','Native Following and nonresearch control do not by themselves establish civic preference consumption.','Current civic never reset or selected by experiment; only later naturally completed decisions are decision-boundary evidence.','Completed v1 sham research recovered offline after optional save confirmation failure; exact400 observations/end152/autosave/native DB/source pins validated; no native replay. V2 changes controller save tolerance only.']}
        write(a.output/'comparison.json',result)
        lines=['# Clean strategy research test','','80 analyzed Online rounds71–150 per research arm; actual native endpoint152. Both strategies active, old CSC research lists/items absent, target Favored1/Value0.','','| Arm | Naval selected | Naval completed |','|---|---:|---:|']
        for arm in ARMS:lines.append(f"| {arm} | {result['research'][arm]['naval_selected']}/5 | {result['research'][arm]['naval_completed']}/5 |")
        lines+=['','See comparison.json for per-player completion timing and naturally completed decision boundaries. Separate diagnostic calibration: '+json.dumps({arm:result['calibration'][arm]['measurable_response'] for arm in ('stock','custom')}),'',*result['limits']]
        (a.output/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        write(a.output/'job-status.json',{'status':'complete','code_version':VERSION,'updated_unix':time.time()})
    except BaseException as exc:
        write(a.output/'failure.json',{'error':str(exc),'traceback':traceback.format_exc()})
        if runner:
            if getattr(runner,'observer_active',False):
                try:runner.export_probe()
                except Exception:pass
            try:runner.archive_failure()
            except Exception:pass
            try:
                runner.states()
                if 'PlotInfo' in runner.state:runner.menu()
                if (runner.out/'original-preferences.json').exists():runner.restore_verified()
            except Exception as error:write(a.output/'cleanup-required.json',{'error':str(error)})
        write(a.output/'job-status.json',{'status':'failed','error':str(exc),'updated_unix':time.time()});raise
    finally:
        for rel,data in originals.items():(INSTALLED/rel).write_bytes(data)
        write(a.output/'installed-restored.json',{'verified':all((INSTALLED/rel).read_bytes()==data for rel,data in originals.items()),'source_unchanged':all((ROOT/'Civ Supply Chains'/rel).read_bytes()==data for rel,data in originals.items()),'hashes':{str(rel):sha(INSTALLED/rel) for rel in originals}})

if __name__=='__main__':main()
