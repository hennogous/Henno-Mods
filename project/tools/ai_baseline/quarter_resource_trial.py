"""Single matched250-turn Quarter-owned resource valuation trial."""
import argparse,hashlib,json,re,shutil,subprocess,sys,time,traceback
from pathlib import Path
from density_game_trial import DensityRunner
from density_game_methods import DensityMethods
from paired_standard import HERE,read,sha
from run import ROOT,SAVES,LOGS,write

class QuarterResourceRunner(DensityRunner):
    def say(self,message):
        super().say(message.replace("AI90/900.","AI90/50; Workshop improvement attachment."))

    def pin_sources(self):
        super().pin_sources()
        p=self.out/'tuning-source-hashes.json';pins=read(p)
        for name in ('quarter_resource_trial.py','quarter_resource_fixture.lua','quarter_resource_probe.lua','quarter_resource_analyze.py','quarter_resource_job.py','quarter_resource_resume.py'):
            f=HERE/name;pins[str(f)]=sha(f)
        write(p,pins)

    def save_checkpoint(self,i,turn):
        # Short unique filename; a final save failure must not discard valid data.
        name=f'CSC_QR_V2_20261018_{turn:03d}';path=SAVES/(name+'.Civ6Save');started=time.time()
        self.cmd('local s={Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);','PlotInfo','save-'+str(turn),wait=4)
        confirmed=False
        for _ in range(20):
            if path.exists() and path.stat().st_mtime>=started-2 and path.stat().st_size:
                size=path.stat().st_size;time.sleep(1)
                if path.stat().st_size==size:confirmed=True;break
            time.sleep(1)
        if not confirmed:
            write(self.out/f'save-warning-{turn}.json',{'turn':turn,'error':'Named save not confirmed'})
            if turn==1:raise RuntimeError('Pristine initial save required for fixture reload')
            return
        dst=self.out/'game-01'/path.name;shutil.copy2(path,dst)
        write(self.out/'game-01'/('initial-save.json' if turn==1 else 'save.json'),{'path':str(path),'sha256':sha(dst),'turn':turn})

    def native_fixture(self):
        pristine=read(self.out/'game-01/turn-001.json')
        self.cmd((HERE/'quarter_resource_fixture.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','supply-fixture-setup',wait=5)
        for stage,expected in [('present',40),('improved',120),('pillaged',40)]:
            if stage!='present':
                code="local t=Game:GetProperty('CSC_QR_FIXTURE');for _,c in ipairs(t.cases) do local p=Map.GetPlotByIndex(c.material);"
                code+=("ImprovementBuilder.SetImprovementType(p,GameInfo.Improvements.IMPROVEMENT_FARM.Index,c.player);" if stage=='improved' else "ImprovementBuilder.SetImprovementPillaged(p,true);")
                self.cmd(code+'end','CSC_AdjacencyGameplay','fixture-'+stage,wait=3)
            code="local y=GameInfo.Yields['YIELD_CSC_AI_PLACEMENT'].Index;local t=Game:GetProperty('CSC_QR_FIXTURE');assert(t and #t.cases==2);for _,c in ipairs(t.cases) do local p=Map.GetPlotByIndex(c.material);local w=Map.GetPlotByIndex(c.wrong);local far=Map.GetPlotByIndex(c.far);print('CSC_QR_VALUE',c.player,p:GetYield(y),w:GetYield(y));assert(p:GetYield(y)=="+str(expected)+",p:GetYield(y));assert(w:GetYield(y)==0,w:GetYield(y));assert(far:GetYield(y)==0,'Distant Flax must not be boosted');end;print('CSC_QR_FIXTURE_"+stage.upper()+"_PASSED');"
            self.cmd(code,'PlotInfo','fixture-read-'+stage,wait=3)
        # Remove fixture by restoring original native save, never manually undo it.
        meta=read(self.out/'game-01/initial-save.json');saved=self.out/'game-01'/Path(meta['path']).name
        self.menu();self.cmd('Automation.SetAutoStartEnabled(true);Network.LoadGame('+json.dumps(str(saved))+',ServerType.SERVER_TYPE_NONE);','MainMenu','reload-pristine',wait=3,check=False)
        self.wait('CSC_AdjacencyGameplay',300)
        for _ in range(40):
            try:
                self.cmd("assert(Game.GetCurrentGameTurn()==1 and not Game:GetProperty('CSC_QR_FIXTURE'));assert(not AutoplayManager.IsActive());",'CSC_AdjacencyGameplay','pristine-ready',wait=2);break
            except (RuntimeError,KeyError):time.sleep(3)
        else:raise RuntimeError('Pristine reload did not settle')
        self.cmd((HERE/'paired_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','observer-pristine',wait=3)
        self.snapshot(1,1);assert read(self.out/'game-01/turn-001.json')==pristine,'Fixture reload differs from pristine census'
        self.cmd((HERE/'builder_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-pristine',wait=2)
        self.cmd((HERE/'builder_export.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-export-pristine',wait=2)
        self.builder_snapshot(1)
        write(self.out/'fixture-validation.json',{'passed':True,'present':40,'improved':120,'pillaged':40,'unmapped':0,'distant_material':0,'readback_context':'PlotInfo UI (gameplay GetYield omits modifier additions)','originally_owned_fixture_plots':True,'pristine_reload_identical':True})
        self.say('Native supply fixture passed; pristine start restored.')

    def snapshot(self,i,target):
        super().snapshot(i,target)
        if target>=50 and target%50==0:
            try:
                text=self.cmd((HERE/'quarter_resource_probe.lua').read_text(encoding='utf-8'),'PlotInfo','supply-signal-'+str(target),wait=3)
                data=json.loads(re.search(r'CSC_QR_SIGNAL=([^\r\n]+)',text).group(1))
            except Exception as exc:
                data={'turn':target,'plots':[],'errors':[{'probe_error':str(exc)[-1500:]}]}
            write(self.out/f'supply-signal-{target:03d}.json',data)
            if data['errors']:self.say('Supply sample has '+str(len(data['errors']))+' audit entries; natural observations continue.')

    def finish_preflight(self,i):
        self.cmd(Path(__file__).with_name('builder_export.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-unit-export',wait=2)
        self.builder_snapshot(1)
        folder = self.out/f'game-{i:02d}'
        settings = read(folder/'settings.json')
        settings['ai'] = 'standard + CSC native placement signals + Quarter-owned supply40/+80; Builder50; improvement90'
        settings['comparison'] = str(self.baseline/f'game-{i:02d}')
        write(folder/'settings.json', settings)
        self.cmd("assert(GameInfo.PseudoYields['PSEUDOYIELD_IMPROVEMENT'].DefaultValue==90);local n=0;for r in GameInfo.AiFavoredItems() do assert(r.ListType~='CSC_AI_ImprovementPriorities');if r.ListType=='UnitPriorityBoosts' and r.Item=='UNIT_BUILDER' then assert(r.Value==50);n=n+1 end end;assert(n==1);print('CSC_AI_BUILDER_V4_LOADED');",'CSC_AdjacencyGameplay','tuning-loaded',wait=3)
        self.cmd("assert(GameInfo.Adjacency_YieldChanges['CSC_AI_BONUS_RESOURCE'].AdjacentResourceClass=='RESOURCECLASS_BONUS');assert(GameInfo.Adjacency_YieldChanges['CSC_AI_BONUS_RESOURCE'].YieldChange==12);assert(GameInfo.Adjacency_YieldChanges['CSC_AI_RIVER'].AdjacentRiver and GameInfo.Adjacency_YieldChanges['CSC_AI_RIVER'].YieldChange==4);for row in GameInfo.Features() do assert(not row.FeatureType:match('^FEATURE_CSC_AI_RESOURCE_')) end;for row in GameInfo.Modifiers() do assert(not row.ModifierId:match('^MOD_CSC_AI_MATERIAL_')) end;print('CSC_AI_BUILDER_V4_RULES_PASSED');", 'CSC_AdjacencyGameplay', 'native-rule-smoke', wait=3)
        import subprocess
        subprocess.run([sys.executable,str(Path(__file__).with_name('validate_tuning.py')),'--loaded','--output',str(self.out/'native-database-validation.json')],check=True)
        self.cmd("assert(GameInfo.Technologies['TECH_CSC_AI_PLACEMENT']==nil);local n=0;for r in GameInfo.Yields() do if r.YieldType=='YIELD_CSC_AI_PLACEMENT' then n=n+1 end end;assert(n==1);print('CSC_AI_GAMEPLAY_SIGNAL_VISIBLE');", 'CSC_AdjacencyGameplay', 'native-signal-database', wait=3)
        code="assert(CSC_AI_UIFilterInstalled);local n=0;for r in GameInfo.Yields() do assert(r.YieldType~='YIELD_CSC_AI_PLACEMENT');n=n+1 end;assert(n==6,n);local r=assert(GameInfo.Yields['YIELD_CSC_AI_PLACEMENT']);assert(GameInfo.Yields[r.Index].YieldType==r.YieldType);for a in GameInfo.District_Adjacencies() do assert(GameInfo.Adjacency_YieldChanges[a.YieldChangeId].YieldType~='YIELD_CSC_AI_PLACEMENT') end;print('CSC_AI_UI_FILTER_PASSED',n);"
        for state in ('PlotInfo','PlotToolTip','ReportScreen','CivilopediaScreen'):
            self.cmd(code,state,'ui-filter-'+state,wait=2)
        text=self.cmd(Path(__file__).with_name('native_guidance_probe.lua').read_text(encoding='utf-8'),'PlotInfo','native-guidance-initial',wait=8)
        match=re.search(r'CSC_AI_NATIVE_GUIDANCE=([^\r\n]+)',text);assert match
        write(self.out/'native-guidance-initial.json',json.loads(match.group(1)))

def verify(out):
    folder=out/'game-01';events=[]
    for t in [1,*range(25,251,25)]:
        d=read(folder/f'turn-{t:03d}.json');assert d['turn']==t and not d['errors'] and d['events'][:len(events)]==events;events=d['events']
    gap=read(out/'observation-gap.json') if (out/'observation-gap.json').exists() else None
    for t in (1,50,100,150,200,250):
        if t==50 and gap and not (out/f'builders-{t:03d}.json').exists():continue
        assert not read(out/f'builders-{t:03d}.json')['errors']
    for name in ('tuning-source-hashes.json','controller-source-hashes.json'):
        for p,digest in read(out/name).items():assert sha(Path(p))==digest,p
    assert read(out/'preferences-restored.json')['verified'];assert read(out/'fixture-validation.json')['passed']
    assert read(out/'native-database-validation.json')['status']=='passed'
    assert not [s for s in (folder/'logs/Database.log').read_text(errors='replace').splitlines() if '[Gameplay]' in s and 'ERROR' in s]
    write(out/'validation.json',{'passed':True,'turn':250,'snapshots':11,'observer_errors':0,'source_pins':True,'native_fixture':True,'named_save_confirmed':(folder/'save.json').exists(),'observation_gap':gap})

def main():
    p=argparse.ArgumentParser()
    for name in ('output','captures','baseline','previous'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=QuarterResourceRunner(a.output);r.captures=a.captures;r.baseline=a.baseline;r.previous=a.previous;r.keep_game=False;r.pin_sources()
    try:
        r.wait('MainMenu',300);r.config()
        offsets={f.name:{'size':f.stat().st_size,'prefix':hashlib.sha256(f.read_bytes()[:128]).hexdigest()} for f in LOGS.iterdir() if f.is_file()}
        write(a.output/'log-offsets.json',offsets);r.start_pair(1)
        settings=read(a.output/'game-01/settings.json');settings.update(target_turn=250,ai='Quarter resource40/+80; Builder50; improvement90',checkpoints=[1,*range(25,251,25)])
        write(a.output/'game-01/settings.json',settings)
        control=read(a.previous/'game-01/initial-map.json');world=read(a.output/'game-01/initial-map.json');assert world['plots']==control['plots'],'Latest resource4 world differs'
        r.native_fixture();write(a.output/'job-status.json',{'status':'running','target_turn':250,'updated_unix':time.time(),'code_version':'quarter-owned-workshop80-builder50-v2b'})
        r.autoplay(1,250);r.builder_snapshot(250);r.save_checkpoint(1,250);r.check_installed()
        logs=a.output/'game-01/logs';logs.mkdir(exist_ok=True)
        for f in LOGS.iterdir():
            if f.is_file():
                full=a.output/'full-session-logs';full.mkdir(exist_ok=True);shutil.copy2(f,full/f.name)
                data=f.read_bytes();offset=offsets.get(f.name,{})
                if len(data)>=offset.get('size',0) and hashlib.sha256(data[:128]).hexdigest()==offset.get('prefix'):data=data[offset['size']:]
                (logs/f.name).write_bytes(data)
        auto=SAVES/'auto';dst=a.output/'endpoint-autosaves';dst.mkdir(exist_ok=True)
        for f in sorted(auto.glob('*.Civ6Save'),key=lambda x:x.stat().st_mtime,reverse=True)[:3]:shutil.copy2(f,dst/f.name)
        r.menu();r.restore_verified();verify(a.output);write(a.output/'game-01/complete.json',{'turn':250,'status':'complete'})
    except BaseException as exc:
        write(a.output/'failure.json',{'error':str(exc),'traceback':traceback.format_exc()});r.archive_failure()
        try:
            r.states()
            if 'PlotInfo' in r.state:r.menu()
            r.wait('MainMenu',30);r.restore_verified()
        except Exception as cleanup:write(a.output/'cleanup-required.json',{'error':str(cleanup)})
        raise

if __name__=='__main__':main()
