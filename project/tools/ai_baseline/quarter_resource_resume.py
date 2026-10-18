"""Resume the SAME natural game after a read-only observer failure; no new map."""
import argparse,hashlib,json,re,shutil,subprocess,sys,time,traceback
from pathlib import Path
from quarter_resource_trial import QuarterResourceRunner,verify
from paired_standard import HERE,read,sha
from run import LOGS,SAVES,write

class ResumeRunner(QuarterResourceRunner):
    def snapshot(self,i,target):
        super().snapshot(i,target)
        if target>=self.resume_turn:
            path=self.out/f'game-{i:02d}'/f'turn-{target:03d}.json';data=read(path)
            data['events']=self.event_prefix+data['events'];write(path,data)
    def builder_snapshot(self,turn):
        if turn==50 and not (self.out/'builders-050.json').exists():
            self.say('Turn50 Builder census unavailable after observer interruption; not reconstructed.');return
        super().builder_snapshot(turn)

def main():
    sys.stdout.reconfigure(encoding='utf-8',errors='replace');sys.stderr.reconfigure(encoding='utf-8',errors='replace')
    p=argparse.ArgumentParser()
    for name in ('output','captures','baseline','previous','resume-from'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=ResumeRunner(a.output);r.captures=a.captures;r.baseline=a.baseline;r.previous=a.previous;r.keep_game=False
    origin=a.resume_from;assert read(origin/'fixture-validation.json')['passed'];assert read(origin/'preferences-restored.json')['verified']
    r.event_prefix=read(origin/'game-01/turn-050.json')['events'];r.resume_turn=63;r.pin_sources()
    try:
        r.wait('MainMenu',300);r.config();r.select_mods(False)
        offsets={f.name:{'size':f.stat().st_size,'prefix':hashlib.sha256(f.read_bytes()[:128]).hexdigest()} for f in LOGS.iterdir() if f.is_file()};write(a.output/'log-offsets.json',offsets)
        archived=origin/'failure-autosaves/AutoSave_0063.Civ6Save';assert archived.exists();saved=SAVES/'CSC_QR_Resume_0063_20261019.Civ6Save';shutil.copy2(archived,saved);assert sha(saved)==sha(archived);write(a.output/'resume-save.json',{'source':str(archived),'load_path':str(saved),'sha256':sha(saved),'origin':str(origin),'same_natural_game':True,'gameplay_unchanged':True,'bounded_last_resume_attempt':True})
        text=r.cmd('Automation.SetAutoStartEnabled(true);Network.LeaveGame();local result=Network.LoadGame('+json.dumps(str(saved))+',ServerType.SERVER_TYPE_NONE);print("CSC_LOAD_RESULT",result);','MainMenu','load-same-game-63-local',wait=3,check=False)
        if re.search(r'CSC_LOAD_RESULT\s+false',text):raise RuntimeError('Native load rejected the normal-directory resume save')
        r.wait('CSC_AdjacencyGameplay',300)
        text=r.cmd("Automation.SetActive(false);AutoplayManager.SetActive(false);assert(not Game:GetProperty('CSC_QR_FIXTURE'));print('CSC_RESUME_TURN',Game.GetCurrentGameTurn());",'GameCore_Tuner','freeze-resume',wait=2)
        r.resume_turn=int(re.search(r'CSC_RESUME_TURN\s+(\d+)',text).group(1));assert 63<=r.resume_turn<=70,r.resume_turn
        r.cmd((HERE/'paired_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','observer-resume',wait=3)
        r.cmd((HERE/'builder_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-observer-resume',wait=2)
        r.cmd((HERE/'builder_export.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-export-resume',wait=2)
        text=r.cmd("local t=Game.GetCurrentGameTurn();CSCBASE.checkpoints[t]=CSCBASE.capture();CSC_BUILDERS.checkpoints[t]=CSC_BUILDERS.Capture();print('CSC_RESUME_FROZEN',t);",'CSC_AdjacencyGameplay','freeze-real-resume-census',wait=3)
        r.resume_turn=int(re.search(r'CSC_RESUME_FROZEN\s+(\d+)',text).group(1));assert 63<=r.resume_turn<=80,r.resume_turn
        write(a.output/'observation-gap.json',{'reason':'UI-only probe called unavailable gameplay district API; same game resumed from archived autosave, no gameplay changes','first_segment_last_checkpoint':50,'resume_turn':r.resume_turn,'placement_event_gap_inclusive':[51,r.resume_turn],'builder_event_comparison_start':r.resume_turn+1,'missing_builder_census':[50],'missing_supply_samples':[50],'source_segment_before_resume':str(origin/'source-version'),'renderer':'DX12'})
        r.snapshot(1,r.resume_turn);r.builder_snapshot(r.resume_turn)
        subprocess.run([sys.executable,'-X','utf8',str(HERE/'validate_tuning.py'),'--loaded','--output',str(a.output/'native-database-validation.json')],check=True)
        # Test UI probe once before continuation; optional failures never stop natural play.
        try:
            text=r.cmd((HERE/'quarter_resource_probe.lua').read_text(encoding='utf-8'),'PlotInfo','supply-probe-resume',wait=3);value=json.loads(re.search(r'CSC_QR_SIGNAL=([^\r\n]+)',text).group(1));write(a.output/f'supply-signal-{r.resume_turn:03d}.json',value)
        except Exception as exc:write(a.output/'resume-probe-warning.json',{'error':str(exc)[-1500:]})
        write(a.output/'job-status.json',{'status':'running','resumed_from':r.resume_turn,'target':250,'updated_unix':time.time()});r.say('Continuing SAME natural game from turn'+str(r.resume_turn)+' to250; observer gap documented.')
        r.autoplay(1,250);r.builder_snapshot(250);r.save_checkpoint(1,250);r.check_installed()
        logs=a.output/'game-01/logs';logs.mkdir(exist_ok=True);full=a.output/'full-session-logs';full.mkdir(exist_ok=True)
        for f in LOGS.iterdir():
            if f.is_file():
                shutil.copy2(f,full/f.name);data=f.read_bytes();off=offsets.get(f.name,{})
                if len(data)>=off.get('size',0) and hashlib.sha256(data[:128]).hexdigest()==off.get('prefix'):data=data[off['size']:]
                (logs/f.name).write_bytes(data)
        auto=SAVES/'auto';dst=a.output/'endpoint-autosaves';dst.mkdir(exist_ok=True)
        for f in sorted(auto.glob('*.Civ6Save'),key=lambda x:x.stat().st_mtime,reverse=True)[:3]:shutil.copy2(f,dst/f.name)
        r.menu();r.restore_verified();verify(a.output);write(a.output/'game-01/complete.json',{'turn':250,'status':'complete','resumed_same_game':True,'observation_gap':read(a.output/'observation-gap.json')})
    except BaseException as exc:
        write(a.output/'failure.json',{'error':str(exc),'traceback':traceback.format_exc()});r.archive_failure()
        try:
            r.states()
            if 'PlotInfo' in r.state:r.menu()
            r.wait('MainMenu',30);r.restore_verified()
        except Exception as cleanup:write(a.output/'cleanup-required.json',{'error':str(cleanup)})
        raise

if __name__=='__main__':main()
