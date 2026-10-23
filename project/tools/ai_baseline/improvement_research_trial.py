"""One matched CSC250 trial: improvement-owned80 plus material-aware research."""
import argparse,hashlib,json,re,shutil,sqlite3,subprocess,sys,time,traceback
from pathlib import Path
from quarter_resource_trial import QuarterResourceRunner,verify
from paired_standard import HERE,read,sha,CHECKPOINTS
from run import ROOT,SAVES,LOGS,write

VERSION='improvement-owned80-dynamic-service-research-v1b'
class ResearchRunner(QuarterResourceRunner):
    def select_mods(self,tar):
        if getattr(self,'resume_setup',False):
            self.active_mods=(self.resume_origin/'commands/0003-select-mods-False.txt').read_text(encoding='utf-8');return
        return super().select_mods(tar)
    def start_map(self,group,tar,resource,i,roster,resume=False):
        return super().start_map(group,tar,resource,i,roster,resume or getattr(self,'resume_setup',False))
    def pin_sources(self):
        super().pin_sources();p=self.out/'tuning-source-hashes.json';pins=read(p)
        for f in [Path(__file__),HERE/'improvement_research_analyze.py',HERE/'quarter_resource_job.py',ROOT/'project/modbuddy/CivSupplyChains.actions.json',ROOT/'Civ Supply Chains/Civ Supply Chains.civ6proj']:
            pins[str(f)]=sha(f)
        write(p,pins)
    def archive_version(self):
        dst=self.out/'source-version';assert not dst.exists();dst.mkdir()
        files={}
        for name in ('tuning-source-hashes.json','controller-source-hashes.json'):
            for path,digest in read(self.out/name).items():
                f=Path(path)
                if f.is_relative_to(ROOT):
                    rel=f.relative_to(ROOT);target=dst/'repository'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target);assert sha(target)==digest;files[str(rel)]=digest
        installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains";native={}
        for f in installed.rglob('*'):
            if f.is_file() and f.suffix in ('.sql','.lua','.xml','.modinfo'):
                rel=f.relative_to(installed);target=dst/'installed'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target);native[str(rel)]=sha(target)
        write(dst/'version.json',{'code_version':VERSION,'archived_unix':time.time(),'source_files':files,'installed_files':native,'improvement':90,'builder':50,'presence':40,'improved_extra':80,'research':'native Favored1/Value0 lists; Lua material gate','map_seed':830102,'game_seed':940104,'speed':'Online','resource_setting':'vanilla Standard','resource_pass':4})
    def save_checkpoint(self,i,turn):
        text=self.cmd('print("CSC_IR_SAVE_TURN",Game.GetCurrentGameTurn());','GameCore_Tuner','actual-save-turn',wait=1)
        actual=int(re.search(r'CSC_IR_SAVE_TURN\s+(\d+)',text).group(1));name=f'CSC_IR_20261019_{actual:03d}';path=SAVES/(name+'.Civ6Save');stamp=time.time()
        self.cmd('local s={Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);','PlotInfo','save-'+str(turn),wait=4)
        for _ in range(20):
            if path.exists() and path.stat().st_mtime>=stamp-2 and path.stat().st_size:
                size=path.stat().st_size;time.sleep(1)
                if path.stat().st_size==size:
                    dst=self.out/'game-01'/path.name;shutil.copy2(path,dst);write(self.out/'game-01'/('initial-save.json' if turn==1 else 'save.json'),{'path':str(path),'sha256':sha(dst),'turn':actual,'requested_checkpoint':turn});return
            time.sleep(1)
        write(self.out/f'save-warning-{turn}.json',{'actual_turn':actual,'requested':turn})
        if turn==1:raise RuntimeError('Pristine save required')
    def research_snapshot(self,target):
        text=self.cmd(f'CSC_AI_Research.Export({target});','CSC_AI_Research','research-'+str(target),wait=2)
        data=json.loads(re.search(r'CSC_AI_RESEARCH_AUDIT=([^\r\n]+)',text).group(1));assert data['turn']==target and not data['errors'];write(self.out/f'research-{target:03d}.json',data)
    def snapshot(self,i,target):
        super().snapshot(i,target)
        self.research_snapshot(target)
    def finish_preflight(self,i):
        super().finish_preflight(i)
        self.cmd("assert(CSC_AI_Research and CSC_AI_Research.version==1);local found=false;for p in GameInfo.CSC_AI_ServiceResearch() do if p.Id==4 then assert(p.CivicType=='CIVIC_NAVAL_TRADITION');found=true;end;end;assert(found);",'CSC_AI_Research','research-loaded',wait=2)
        src=sqlite3.connect((Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite").as_uri()+'?mode=ro',uri=True);dst=sqlite3.connect(self.out/'native-gameplay.sqlite');src.backup(dst);dst.close();src.close()
    def native_fixture(self):
        pristine=read(self.out/'game-01/turn-001.json')
        self.cmd((HERE/'quarter_resource_fixture.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','fixture-create',wait=4)
        # Direct evaluation tests are separate from native callback-consumption counters.
        self.cmd("CSC_AI_Research.Invalidate();assert(CSC_AI_Research.Evaluate(1,1));assert(CSC_AI_Research.Evaluate(2,4));assert(not CSC_AI_Research.Evaluate(1,3));assert(not CSC_AI_Research.Evaluate(2,6));",'CSC_AI_Research','research-base-only',wait=2)
        for stage,value in [('present',40),('improved',120),('pillaged',40)]:
            if stage!='present':
                action='ImprovementBuilder.SetImprovementType(p,GameInfo.Improvements.IMPROVEMENT_FARM.Index,c.player)' if stage=='improved' else 'ImprovementBuilder.SetImprovementPillaged(p,true)'
                self.cmd("for _,c in ipairs(Game:GetProperty('CSC_QR_FIXTURE').cases) do local p=Map.GetPlotByIndex(c.material);"+action+";end",'CSC_AdjacencyGameplay','fixture-'+stage,wait=2)
                if stage=='improved':
                    self.cmd("for _,c in ipairs(Game:GetProperty('CSC_QR_FIXTURE').cases) do ImprovementBuilder.SetImprovementType(Map.GetPlotByIndex(c.far),GameInfo.Improvements.IMPROVEMENT_FARM.Index,c.player);ImprovementBuilder.SetImprovementType(Map.GetPlotByIndex(c.wrong),GameInfo.Improvements.IMPROVEMENT_QUARRY.Index,c.player);end",'CSC_AdjacencyGameplay','fixture-improved-negative-controls',wait=2)
            self.cmd("local y=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index;for _,c in ipairs(Game:GetProperty('CSC_QR_FIXTURE').cases) do local actual=Map.GetPlotByIndex(c.material):GetYield(y);print('CSC_IR_VALUE',c.player,actual);assert(actual=="+str(value)+",actual);assert(Map.GetPlotByIndex(c.wrong):GetYield(y)==0);assert(Map.GetPlotByIndex(c.far):GetYield(y)==0);end",'PlotInfo','fixture-read-'+stage,wait=2)
        self.cmd("for i,c in ipairs(Game:GetProperty('CSC_QR_FIXTURE').cases) do ResourceBuilder.SetResourceType(Map.GetPlotByIndex(c.wrong),GameInfo.Resources[i==1 and 'RESOURCE_SUGAR' or 'RESOURCE_SILK'].Index,1);end",'CSC_AdjacencyGameplay','fixture-add-spec',wait=2)
        self.cmd("CSC_AI_Research.Invalidate();assert(CSC_AI_Research.Evaluate(1,3));assert(CSC_AI_Research.Evaluate(2,6));",'CSC_AI_Research','research-both-classes',wait=2)
        self.cmd("for _,c in ipairs(Game:GetProperty('CSC_QR_FIXTURE').cases) do ResourceBuilder.SetResourceType(Map.GetPlotByIndex(c.material),-1);end",'CSC_AdjacencyGameplay','fixture-remove-base',wait=2)
        self.cmd("CSC_AI_Research.Invalidate();assert(not CSC_AI_Research.Evaluate(1,1));assert(not CSC_AI_Research.Evaluate(1,3));assert(not CSC_AI_Research.Evaluate(2,4));assert(not CSC_AI_Research.Evaluate(2,6));",'CSC_AI_Research','research-resource-loss',wait=2)
        self.cmd("for _,c in ipairs(Game:GetProperty('CSC_QR_FIXTURE').cases) do ResourceBuilder.SetResourceType(Map.GetPlotByIndex(c.material),GameInfo.Resources.RESOURCE_CSC_FLAX.Index,1);end;for _,v in ipairs({{1,'CIVIC_FEUDALISM'},{2,'CIVIC_NAVAL_TRADITION'}}) do Players[v[1]]:GetCulture():SetCivic(GameInfo.Civics[v[2]].Index,true);end",'CSC_AdjacencyGameplay','fixture-researched',wait=2)
        self.cmd("CSC_AI_Research.Invalidate();assert(not CSC_AI_Research.Evaluate(1,1));assert(not CSC_AI_Research.Evaluate(2,4));assert(CSC_AI_Research.Evaluate(1,2));assert(CSC_AI_Research.Evaluate(2,5));",'CSC_AI_Research','research-stop-on-completion',wait=2)
        self.cmd('AutoplayManager.SetTurns(1);AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);','GameCore_Tuner','fixture-one-turn',wait=2)
        for _ in range(45):
            text=self.cmd('print("CSC_IR_FIXTURE_TURN",Game.GetCurrentGameTurn(),AutoplayManager.IsActive());','GameCore_Tuner','fixture-progress',wait=1)
            if re.search(r'CSC_IR_FIXTURE_TURN\s+[2-9]\d*\s+false',text):break
            time.sleep(2)
        else:raise RuntimeError('Disposable fixture turn did not finish')
        self.cmd("local n=0;for _,v in pairs(CSC_AI_Research.calls) do n=n+v;end;assert(n>0,'Native AI never invoked research callback');assert(#CSC_AI_Research.errors==0);print('CSC_IR_NATIVE_CALLBACKS',n);",'CSC_AI_Research','research-native-consumption',wait=2)
        meta=read(self.out/'game-01/initial-save.json');self.menu()
        self.cmd('Automation.SetAutoStartEnabled(true);Network.LoadGame('+json.dumps(meta['path'])+',ServerType.SERVER_TYPE_NONE);','MainMenu','reload-pristine',wait=3,check=False);self.wait('CSC_AdjacencyGameplay',300)
        self.cmd("assert(Game.GetCurrentGameTurn()==1 and not Game:GetProperty('CSC_QR_FIXTURE'));assert(not AutoplayManager.IsActive());",'CSC_AdjacencyGameplay','pristine-check',wait=3)
        self.cmd((HERE/'paired_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','observer-pristine',wait=2);self.snapshot(1,1);assert read(self.out/'game-01/turn-001.json')==pristine
        self.cmd((HERE/'builder_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-pristine',wait=2);self.cmd((HERE/'builder_export.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-export-pristine',wait=2);self.builder_snapshot(1)
        write(self.out/'fixture-validation.json',{'passed':True,'present':40,'improved':120,'pillaged':40,'unmapped':0,'far':0,'base_only_research':True,'same_quarter_both_materials':True,'resource_loss_deactivates':True,'research_completion_deactivates':True,'native_callback_consumed':True,'pristine_reload_identical':True})
        self.say('Native improvement/research fixtures passed; pristine start restored.')
    def autoplay(self,i,target,resume=False):
        self.cmd("if not CSCPAIR_RETURN_GUARD then CSCPAIR_RETURN_GUARD=function() if AutoplayManager.IsActive() then local a=PlayerManager.GetAliveMajors();if a[1] then AutoplayManager.SetReturnAsPlayer(a[1]:GetID());end;end;end;Events.PlayerDefeat.Add(CSCPAIR_RETURN_GUARD);end;",'GameCore_Tuner','autoplay-defeat-guard',wait=1)
        self.cmd(f'Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetTurns({target}-Game.GetCurrentGameTurn());AutoplayManager.SetReturnAsPlayer(PlayerManager.GetAliveMajors()[1]:GetID());AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);','GameCore_Tuner','autoplay-start',wait=2,check=False)
        archived={1};builders={1};start=last_progress=time.monotonic();last=-1;failures=0
        while time.monotonic()-start<10800:
            time.sleep(20)
            try:
                text=self.cmd('print("CSC_IR_PROGRESS",Game.GetCurrentGameTurn(),AutoplayManager.IsActive());','GameCore_Tuner','poll',wait=1);m=re.search(r'CSC_IR_PROGRESS\s+(\d+)\s+(true|false)',text);assert m;current=int(m[1]);active=m[2]=='true';failures=0
            except (RuntimeError,OSError,KeyError,AssertionError):
                failures+=1
                if failures>=3:raise RuntimeError('Three failed tuner polls; preserve partial game')
                continue
            if current!=last:last_progress=time.monotonic();last=current
            write(self.out/'live-status.json',{'status':'running','turn':current,'target':target,'updated_unix':time.time()})
            # Export frozen target data BEFORE considering the actual stopping turn.
            for t in CHECKPOINTS:
                if t<=min(current,target) and t not in archived:self.snapshot(i,t);archived.add(t)
            for t in (50,100,150,200,250):
                if t<=min(current,target) and t not in builders:self.builder_snapshot(t);builders.add(t);self.say(f'Checkpoint {t} archived.')
            if current>=target:
                if active:self.cmd('AutoplayManager.SetActive(false);','GameCore_Tuner','autoplay-stop',wait=1)
                write(self.out/'endpoint.json',{'target_census':target,'actual_simulation_turn':current,'overshoot':current-target,'frozen_target_archived':True});return
            if not active:raise RuntimeError('Autoplay stopped before target at '+str(current))
            if time.monotonic()-last_progress>600:raise RuntimeError('Autoplay stalled at '+str(current))
        raise RuntimeError('Autoplay exceeded three hours')

def main():
    p=argparse.ArgumentParser()
    for name in ('output','captures','baseline','previous'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--resume-setup',type=Path)
    a=p.parse_args();r=ResearchRunner(a.output);r.captures=a.captures;r.baseline=a.baseline;r.previous=a.previous;r.keep_game=False;r.pin_sources();r.archive_version()
    try:
        if a.resume_setup:
            r.resume_setup=True;r.resume_origin=a.resume_setup;r.wait('CSC_AdjacencyGameplay',300)
            r.cmd('assert(Game.GetCurrentGameTurn()==1 and not AutoplayManager.IsActive());','GameCore_Tuner','resume-initial-setup',wait=2)
            for name in ('original-preferences.json','installed-gameplay-hashes.json'):shutil.copy2(a.resume_setup/name,a.output/name)
            write(a.output/'setup-recovery.json',{'origin':str(a.resume_setup),'same_native_world':True,'turn':1,'reason':'Startup child was interrupted after relaunch PID misread; native map finished loading, no autoplay or observers yet.'})
        else:r.wait('MainMenu',300);r.config()
        offsets={f.name:{'size':f.stat().st_size,'prefix':hashlib.sha256(f.read_bytes()[:128]).hexdigest()} for f in LOGS.iterdir() if f.is_file()};write(a.output/'log-offsets.json',offsets)
        r.start_pair(1);assert read(a.output/'game-01/initial-map.json')['plots']==read(a.previous/'game-01/initial-map.json')['plots']
        settings=read(a.output/'game-01/settings.json');settings.update(code_version=VERSION,target_turn=250,ai='improvement-owned80 + Quarter presence40 + dynamic material-aware Service research; Builder50/improvement90');write(a.output/'game-01/settings.json',settings)
        r.native_fixture();write(a.output/'job-status.json',{'status':'running','target_turn':250,'updated_unix':time.time(),'code_version':VERSION});r.autoplay(1,250);r.save_checkpoint(1,250);r.check_installed()
        logs=a.output/'game-01/logs';logs.mkdir(exist_ok=True)
        for f in LOGS.iterdir():
            if not f.is_file():continue
            full=a.output/'full-session-logs';full.mkdir(exist_ok=True);shutil.copy2(f,full/f.name);data=f.read_bytes();off=offsets.get(f.name,{})
            if len(data)>=off.get('size',0) and hashlib.sha256(data[:128]).hexdigest()==off.get('prefix'):data=data[off['size']:]
            (logs/f.name).write_bytes(data)
        dst=a.output/'endpoint-autosaves';dst.mkdir(exist_ok=True)
        for f in sorted((SAVES/'auto').glob('*.Civ6Save'),key=lambda x:x.stat().st_mtime,reverse=True)[:3]:shutil.copy2(f,dst/f.name)
        r.menu();r.restore_verified();verify(a.output)
        for t in CHECKPOINTS:assert not read(a.output/f'research-{t:03d}.json')['errors']
        write(a.output/'game-01/complete.json',{'turn':250,'status':'complete','version':VERSION})
    except BaseException as e:
        write(a.output/'failure.json',{'error':str(e),'traceback':traceback.format_exc()});r.archive_failure()
        try:
            r.states()
            if 'PlotInfo' in r.state:r.menu()
            r.wait('MainMenu',30);r.restore_verified()
        except Exception as cleanup:write(a.output/'cleanup-required.json',{'error':str(cleanup)})
        raise
if __name__=='__main__':main()
