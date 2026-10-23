"""Bounded Medieval native research-choice check and one natural250 game."""
import argparse,hashlib,json,re,shutil,sqlite3,subprocess,sys,time,traceback
from pathlib import Path
from improvement_research_trial import ResearchRunner
from quarter_resource_trial import QuarterResourceRunner,verify
from paired_standard import HERE,read,sha,CHECKPOINTS
from run import ROOT,SAVES,LOGS,write

VERSION='medieval-rh-research180-support120-v1c'
class MedievalRunner(ResearchRunner):
    def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
        if label.startswith('start-'):
            code=code.replace('ReleasePlayerParameters();',"GameConfiguration.SetStartEra(DB.MakeHash('ERA_MEDIEVAL'));assert(GameConfiguration.GetStartEra()==DB.MakeHash('ERA_MEDIEVAL'));ReleasePlayerParameters();")
        if getattr(self,'start_turn',None) and state!='MainMenu':
            code=code.replace('Game.GetCurrentGameTurn()==1','Game.GetCurrentGameTurn()=='+str(self.start_turn))
        if label=='reload-pristine':
            meta=read(self.out/'game-01/initial-save.json')
            code=code.replace(json.dumps(str(self.out/'game-01'/Path(meta['path']).name)),json.dumps(meta['path']))
        return super().cmd(code,state,label,wait,check)
    def snapshot(self,i,target):
        actual=self.start_turn if target==1 else target
        super().snapshot(i,actual)
        if target==1:
            for src,dst in [(self.out/f'game-01/turn-{actual:03d}.json',self.out/'game-01/turn-001.json'),(self.out/f'research-{actual:03d}.json',self.out/'research-001.json')]:
                if src!=dst:shutil.copy2(src,dst)
    def builder_snapshot(self,target):
        if target!=1 and target<self.start_turn:return
        actual=self.start_turn if target==1 else target
        super().builder_snapshot(actual)
        if target==1 and actual!=1:shutil.copy2(self.out/f'builders-{actual:03d}.json',self.out/'builders-001.json')
    def autoplay(self,i,target,resume=False):
        import improvement_research_trial as prior
        saved=prior.CHECKPOINTS;prior.CHECKPOINTS=[t for t in CHECKPOINTS if t>self.start_turn]
        try:return super().autoplay(i,target,resume)
        finally:prior.CHECKPOINTS=saved
    def pin_sources(self):
        super().pin_sources();p=self.out/'tuning-source-hashes.json';pins=read(p)
        for name in ('research_priorities_trial.py','research_choice_fixture.lua','research_priorities_analyze.py'):
            f=HERE/name
            if f.exists():pins[str(f)]=sha(f)
        write(p,pins)
    def archive_version(self):
        super().archive_version();p=self.out/'source-version/version.json';d=read(p)
        d.update(code_version=VERSION,research='RH-pattern Lua native strategy; primary civic180; producer prerequisites120',start_era='ERA_MEDIEVAL');write(p,d)
    def start_pair(self,i,resume_map=False):
        folder=self.out/'game-01';folder.mkdir(exist_ok=True)
        roster=read(self.captures/'implemented-vanilla-standard/map-01/settings.json')['leaders']
        self.check_installed()
        if not getattr(self,'resume_origin',None):
            self.select_mods(False)
            leaders='local leaders={'+','.join(json.dumps(x) for x in roster)+'};for j,pid in ipairs(GameConfiguration.GetParticipatingPlayerIDs()) do PlayerConfigurations[pid]:SetLeaderTypeName(leaders[j]);end;'
            setup="GameConfiguration.SetToDefaults();GameConfiguration.SetRuleSet('RULESET_EXPANSION_2');BuildHeadlessGameSetup();RebuildPlayerParameters(true);GameSetup_RefreshParameters();MapConfiguration.SetScript('Continents.lua');MapConfiguration.SetMapSize('MAPSIZE_SMALL');GameConfiguration.SetParticipatingPlayerCount(6);GameConfiguration.SetValue('CITY_STATE_COUNT',9);GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE');GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE');GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',940104);MapConfiguration.SetValue('RANDOM_SEED',830102);MapConfiguration.SetValue('resources',2);GameConfiguration.SetValue('CSC_INCLUDE_ANIMAL_RESOURCES',1);GameConfiguration.SetValue('CSC_REMOVE_UNUSED_MODDED_RESOURCES',1);GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false);"+leaders+"ReleasePlayerParameters();HideGameSetup();Automation.SetAutoStartEnabled(true);Network.HostGame(ServerType.SERVER_TYPE_NONE);"
            self.cmd(setup,'MainMenu','start-medieval',wait=3,check=False)
        self.wait('CSC_AdjacencyGameplay',300)
        text=self.cmd("print('CSC_START_TURN',Game.GetCurrentGameTurn());assert(GameConfiguration.GetStartEra()==DB.MakeHash('ERA_MEDIEVAL'));",'GameCore_Tuner','verify-start-era',wait=2)
        self.start_turn=int(re.search(r'CSC_START_TURN\s+(\d+)',text)[1]);assert self.start_turn==71
        text=self.cmd((HERE.parent/'map_survey/dump.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','dump-medieval',wait=4);world=json.loads(re.search(r'CSCMAP_SURVEY=([^\r\n]+)',text)[1]);assert world['turn']==self.start_turn
        write(folder/'initial-map.json',world)
        settings={'map_seed':830102,'game_seed':940104,'leaders':roster,'resource_setting':2,'speed':'Online','code_version':VERSION,'start_era':'ERA_MEDIEVAL','initial_turn':self.start_turn,'target_turn':250,'simulation_rounds':250-self.start_turn,'checkpoints':[self.start_turn,*[t for t in CHECKPOINTS if t>self.start_turn]],'ai':'Quarter40/improvement80; improvement90/Builder50; conditional civic180/support120'};write(folder/'settings.json',settings)
        (folder/'enabled-mods.txt').write_text(getattr(self,'active_mods','Recovered same native setup; original mod list in setup origin.'),encoding='utf-8')
        write(self.out/'checkpoint-layout.json',{'initial_actual_turn':self.start_turn,'initial_alias':'turn-001.json/builders-001.json/research-001.json are legacy initial-state aliases; JSON actual turn remains71. No earlier observations exist.','primary':[self.start_turn,*[t for t in CHECKPOINTS if t>self.start_turn]],'builders':[self.start_turn,100,150,200,250]})
        subprocess.run([sys.executable,'-X','utf8',str(HERE/'capture_reference.py'),'--output',str(folder/'mechanics-reference.json')],check=True);shutil.copy2(folder/'mechanics-reference.json',self.out/'mechanics-reference.json')
        self.cmd((HERE/'paired_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','observer-1',wait=3);self.snapshot(1,1);self.save_checkpoint(1,1)
        self.cmd((HERE/'builder_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-unit-observer',wait=2);self.finish_preflight(1)
    def reload(self):
        meta=read(self.out/'game-01/initial-save.json');self.menu()
        self.cmd('Automation.SetAutoStartEnabled(true);Network.LoadGame('+json.dumps(meta['path'])+',ServerType.SERVER_TYPE_NONE);','MainMenu','reload-pristine',wait=3,check=False);self.wait('CSC_AdjacencyGameplay',300)
        self.cmd("assert(Game.GetCurrentGameTurn()==1 and not AutoplayManager.IsActive() and not Game:GetProperty('CSC_RESEARCH_CHOICE_FIXTURE'));",'CSC_AdjacencyGameplay','pristine-ready',wait=3)
    def choices(self,on):
        self.cmd((HERE/'research_choice_fixture.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','choice-fixture-'+str(on),wait=3)
        self.cmd("CSC_AI_Research.Invalidate();for p=1,5 do assert(CSC_AI_Research.Evaluate(p,4));end;local R=CSC_AI_Research;local original=R.Evaluate;R.Evaluate=function(pid,plan) return "+str(on).lower()+" and plan==4 and original(pid,plan) end;R.choiceHistory={};local function capture(pid) if pid>=1 and pid<=5 then local p=Players[pid];local c=p:GetCulture():GetProgressingCivic();local d=GameInfo.Civics[c];R.choiceHistory[#R.choiceHistory+1]={Game.GetCurrentGameTurn(),pid,d and d.CivicType or 'NONE',p:GetCulture():HasCivic(GameInfo.Civics.CIVIC_NAVAL_TRADITION.Index),R.Evaluate(pid,4)};end;end;Events.PlayerTurnDeactivated.Add(capture);",'CSC_AI_Research','choice-gate-'+str(on),wait=2)
        self.cmd('AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetTurns(12);AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);','GameCore_Tuner','choice-autoplay-'+str(on),wait=1)
        deadline=time.monotonic()+600
        while time.monotonic()<deadline:
            time.sleep(8);text=self.cmd("print('CSC_CHOICE_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());",'GameCore_Tuner','choice-poll',wait=1);m=re.search(r'CSC_CHOICE_PROGRESS\s+(\d+)\s+(true|false)',text)
            if m and m[2]=='false':break
        else:raise RuntimeError('Choice fixture stalled')
        text=self.cmd("for _,r in ipairs(CSC_AI_Research.choiceHistory) do print('CSC_CHOICE',r[1],r[2],r[3],r[4],r[5]);end;local n=0;for _,v in pairs(CSC_AI_Research.calls) do n=n+v end;assert(n>0);print('CSC_NATIVE_CALLS',n);",'CSC_AI_Research','choice-results-'+str(on),wait=2)
        rows=[{'turn':int(t),'player':int(p),'civic':c,'naval_completed':done=='true','gate':gate=='true'} for t,p,c,done,gate in re.findall(r'CSC_CHOICE\s+(\d+)\s+(\d+)\s+(\S+)\s+(true|false)\s+(true|false)',text)]
        assert rows,'No actual player-choice observations';write(self.out/('choices-on.json' if on else 'choices-off.json'),rows)
        dest=self.out/('native-logs-on' if on else 'native-logs-off');dest.mkdir(exist_ok=True)
        for name in ('AI_Victories.csv','AI_Research.csv','Database.log','Lua.log'):
            if (LOGS/name).exists():shutil.copy2(LOGS/name,dest/name)
        return rows

def main():
    p=argparse.ArgumentParser()
    for n in ('output','captures','baseline','previous'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--phase',choices=('mechanism','natural'),required=True);p.add_argument('--mechanism',type=Path);p.add_argument('--resume-setup',type=Path)
    a=p.parse_args();r=MedievalRunner(a.output);r.captures=a.captures;r.baseline=a.baseline;r.previous=a.previous;r.keep_game=False;r.pin_sources();r.archive_version()
    write(a.output/'job-status.json',{'status':'starting','phase':a.phase,'version':VERSION,'pid':__import__('os').getpid()})
    try:
        if a.resume_setup:
            r.resume_origin=a.resume_setup
            for name in ('original-preferences.json','installed-gameplay-hashes.json'):shutil.copy2(a.resume_setup/name,a.output/name)
            r.states()
            if (a.resume_setup/'game-01/initial-save.json').exists():
                meta=read(a.resume_setup/'game-01/initial-save.json')
                if 'PlotInfo' in r.state:r.menu()
                r.wait('MainMenu',180)
                r.cmd('Automation.SetAutoStartEnabled(true);Network.LoadGame('+json.dumps(meta['path'])+',ServerType.SERVER_TYPE_NONE);','MainMenu','recover-initial-save',wait=3,check=False);r.wait('CSC_AdjacencyGameplay',300)
            write(a.output/'setup-recovery.json',{'origin':str(a.resume_setup),'reason':'Same Medieval71 native world; readiness/building-fixture repairs, no natural autoplay yet.'})
        else:r.wait('MainMenu',180);r.config()
        r.start_pair(1)
        if a.phase=='mechanism':
            off=r.choices(False);r.reload();on=r.choices(True)
            result={'code_version':VERSION,'attempt':1,'max_attempts':3,'start_era':'Medieval','turns_per_arm':12,'same_pristine_sha':read(a.output/'game-01/initial-save.json')['sha256'],'off':{},'on':{}}
            for key,rows in [('off',off),('on',on)]:
                result[key]={'players':sorted({x['player'] for x in rows}),'naval_selected':sorted({x['player'] for x in rows if x['civic']=='CIVIC_NAVAL_TRADITION'}),'naval_completed':sorted({x['player'] for x in rows if x['naval_completed']}),'first_choices':{str(pid):next((x['civic'] for x in rows if x['player']==pid),'NONE') for pid in range(1,6)}}
            result['choice_changed']=result['off']['first_choices']!=result['on']['first_choices'];result['target_response']=len(result['on']['naval_selected'])>len(result['off']['naval_selected']) or len(result['on']['naval_completed'])>len(result['off']['naval_completed'])
            write(a.output/'mechanism-results.json',result);r.menu();r.restore_verified();write(a.output/'job-status.json',{'status':'complete','phase':'mechanism','target_response':result['target_response']});return
        assert a.mechanism and read(a.mechanism/'mechanism-results.json')['target_response'],'Research-choice evidence required before natural play'
        QuarterResourceRunner.native_fixture(r)
        # Scope native AI logs AFTER disposable fixture and pristine reload.
        offsets={f.name:f.stat().st_size for f in LOGS.iterdir() if f.is_file()};write(a.output/'natural-log-offsets.json',offsets)
        write(a.output/'job-status.json',{'status':'running','phase':'natural','target_turn':250,'version':VERSION});r.autoplay(1,250);r.save_checkpoint(1,250);r.check_installed()
        logs=a.output/'game-01/logs';logs.mkdir(exist_ok=True)
        for f in LOGS.iterdir():
            if f.is_file():
                data=f.read_bytes();(logs/f.name).write_bytes(data[offsets.get(f.name,0):] if len(data)>=offsets.get(f.name,0) else data)
        auto=a.output/'endpoint-autosaves';auto.mkdir(exist_ok=True)
        for f in sorted((SAVES/'auto').glob('*.Civ6Save'),key=lambda f:f.stat().st_mtime,reverse=True)[:3]:shutil.copy2(f,auto/f.name)
        r.menu();r.restore_verified()
        for t in [r.start_turn,*[x for x in CHECKPOINTS if x>r.start_turn]]:
            assert read(a.output/f'game-01/turn-{t:03d}.json')['turn']==t
            assert not read(a.output/f'game-01/turn-{t:03d}.json')['errors']
            assert not read(a.output/f'research-{t:03d}.json')['errors']
        for t in (r.start_turn,100,150,200,250):assert not read(a.output/f'builders-{t:03d}.json')['errors']
        for name in ('tuning-source-hashes.json','controller-source-hashes.json'):
            for path,digest in read(a.output/name).items():assert sha(Path(path))==digest,path
        assert read(a.output/'preferences-restored.json')['verified'] and read(a.output/'fixture-validation.json')['passed']
        write(a.output/'validation.json',{'passed':True,'turn':250,'initial_actual_turn':r.start_turn,'primary_censuses':9,'builder_censuses':5,'no_observation_gap_after_start':True,'source_pins':True,'preferences_restored':True})
        write(a.output/'game-01/complete.json',{'turn':250,'status':'complete','version':VERSION})
        subprocess.run([sys.executable,'-X','utf8',str(HERE/'research_priorities_analyze.py'),'--trial',str(a.output),'--previous',str(a.previous)],check=True)
        write(a.output/'job-status.json',{'status':'complete','phase':'natural','turn':250})
    except BaseException as e:
        write(a.output/'failure.json',{'error':str(e),'traceback':traceback.format_exc()});r.archive_failure()
        try:
            r.states()
            if 'PlotInfo' in r.state:r.menu()
            r.wait('MainMenu',30);r.restore_verified()
        except Exception as cleanup:write(a.output/'cleanup-required.json',{'error':str(cleanup)})
        write(a.output/'job-status.json',{'status':'failed','phase':a.phase,'error':str(e)});raise
if __name__=='__main__':main()
