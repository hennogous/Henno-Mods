"""One Online250 game: resource pass4, native placement, Builder90/900.

Original AI seed/roster, intentional resource differences, read-only observers.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import traceback
from builder_tuning_trial import TrialRunner
from density_game_methods import DensityMethods
from paired_standard import CHECKPOINTS,FIELDS,HERE,read,sha
from run import ROOT,Runner,write


class DensityRunner(DensityMethods,TrialRunner):
    def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
        if label.startswith('start-'):
            code=code.replace('ReleasePlayerParameters();',"GameConfiguration.SetValue('CSC_MATERIAL_MAP_ASSISTANCE',1);GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);ReleasePlayerParameters();")
        for attempt in range(4):
            try:return Runner.cmd(self,code,state,label,wait,check)
            except (OSError,EOFError,RuntimeError,KeyError) as exc:
                before=isinstance(exc,KeyError) or str(exc)=='No responsive tuner states'
                readonly=label=='ready' or label.startswith(('dump-','actual-','snapshot-','builders-','poll'))
                if attempt==3 or not (before or readonly):raise
                time.sleep(3)

    def pin_sources(self):
        super().pin_sources()
        path=self.out/'tuning-source-hashes.json';pins=read(path)
        paths=[Path(__file__),HERE/'density_game_methods.py',HERE/'run_density_job.py',HERE/'analyze_density_game.py',HERE/'analyze_checkpoint_tuning.py',
               *list((ROOT/'Civ Supply Chains/Lua_UI/MapGeneration').glob('*.lua'))]
        pins.update({str(p):sha(p) for p in paths});write(path,pins)

    def start_pair(self,i,resume_map=False):
        assert i==1 and not resume_map
        folder=self.out/'game-01';folder.mkdir(exist_ok=True)
        original=self.captures/'implemented-vanilla-standard/map-01'
        roster=read(original/'settings.json')['leaders']
        self.check_installed();self.select_mods(False)
        self.keep_game=True;self.save_maps=False
        self.start_map('density-ai-standard',False,2,1,roster)
        self.keep_game=False
        capture=self.out/'density-ai-standard/map-01'
        data=read(capture/'map.json');shutil.copy2(capture/'map.json',folder/'initial-map.json')
        prior=read(original/'map.json')
        differences={k:sum(p.get(k)!=q.get(k) for p,q in zip(data['plots'],prior['plots'])) for k in FIELDS}
        assert not any(v for k,v in differences.items() if k not in ('resource','resource_count')),differences
        write(folder/'map-comparison.json',{'reference':str(original),'exact_original_world_required':False,'intentional_resource_pass_change':'v3 to v4 density','differences':differences})
        settings=read(capture/'settings.json');settings.update(target_turn=250,ai='native placement12/4/10; improvement90; Builder900',assistance_version=4,checkpoints=CHECKPOINTS,game_number=1,paired_map=1)
        write(folder/'settings.json',settings);shutil.copy2(capture/'enabled-mods.txt',folder/'enabled-mods.txt')
        text=self.cmd("local a=Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT');assert(a and a.status=='complete' and a.version==4 and a.initialization_turn==1);assert(a.abundance.setting==2 and a.abundance.standard_density==30);assert(a.site_density.met.base_only and a.site_density.met.both);print('CSCDENS_AI_AUDIT='..CSC_MaterialMapCore.Json(a));",'CSC_MaterialMap','assistance-audit',wait=3)
        write(folder/'assistance-audit.json',json.loads(re.search(r'CSCDENS_AI_AUDIT=([^\r\n]+)',text).group(1)))
        subprocess.run([sys.executable,'-X','utf8',str(HERE/'capture_reference.py'),'--output',str(folder/'mechanics-reference.json')],check=True)
        shutil.copy2(folder/'mechanics-reference.json',self.out/'mechanics-reference.json')
        self.cmd((HERE/'paired_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','observer-1',wait=4)
        self.snapshot(1,1);self.save_checkpoint(1,1)
        self.cmd((HERE/'builder_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-unit-observer',wait=3)
        self.finish_preflight(1)
        control=read(self.previous/'game-01/turn-001.json')['players'];current=read(folder/'turn-001.json')['players']
        keys=('id','leader','civ','techs','civics')
        assert [{k:p[k] for k in keys} for p in current]==[{k:p[k] for k in keys} for p in control]
        settings=read(folder/'settings.json');settings['comparison']=str(self.previous/'game-01');write(folder/'settings.json',settings)
        self.say('Preflight passed: original terrain/roster/research, resource pass4, AI90/900.')


def verify_run(out):
    folder=out/'game-01';previous=[]
    for turn in CHECKPOINTS:
        data=read(folder/f'turn-{turn:03d}.json')
        assert data['turn']==turn and not data['errors'] and data['events'][:len(previous)]==previous
        previous=data['events']
    for turn in (1,50,100,150,200,250):assert not read(out/f'builders-{turn:03d}.json')['errors']
    for name in ('initial-save.json','save.json'):
        save=read(folder/name);assert sha(folder/Path(save['path']).name)==save['sha256']
    for filename in ('tuning-source-hashes.json','controller-source-hashes.json'):
        for path,digest in read(out/filename).items():assert sha(Path(path))==digest,path
    assert read(out/'preferences-restored.json')['verified']
    assert not [r for r in (folder/'logs/Database.log').read_text(errors='replace').splitlines() if '[Gameplay]' in r and 'ERROR' in r]
    assert sorted((out/'commands').glob('*-observer-1.lua'))[-1].read_text(encoding='utf-8')==(HERE/'paired_observer.lua').read_text(encoding='utf-8')
    write(out/'validation.json',{'passed':True,'turn':250,'snapshots':len(CHECKPOINTS),'observer_errors':0,'source_pins':True,'save_checksums':True,'map_resource_differences_intentional':True})


def main():
    sys.stdout.reconfigure(encoding='utf-8',errors='replace');sys.stderr.reconfigure(encoding='utf-8',errors='replace')
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('output','captures','baseline','previous'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=DensityRunner(a.output);r.captures=a.captures;r.baseline=a.baseline;r.previous=a.previous;r.keep_game=False
    r.pin_sources()
    try:
        r.wait('MainMenu',240);r.config()
        write(a.output/'batch.json',{'status':'running','target_turn':250,'resource_pass_version':4})
        r.start_pair(1)
        write(a.output/'job-status.json',{'status':'running','target_turn':250,'updated_unix':time.time()})
        r.autoplay(1,250);r.builder_snapshot(250);r.save_checkpoint(1,250);r.check_installed()
        write(a.output/'game-01/complete.json',{'status':'complete','turn':250})
        r.menu();r.restore_verified();verify_run(a.output)
        write(a.output/'batch.json',{'status':'complete','turn':250,'resource_pass_version':4})
    except BaseException as exc:
        write(a.output/'batch.json',{'status':'interrupted','error':str(exc),'traceback':traceback.format_exc()})
        r.archive_failure()
        try:
            r.states()
            if 'PlotInfo' in r.state:r.menu()
            r.wait('MainMenu',20);r.restore_verified()
        except Exception as cleanup:write(a.output/'cleanup-required.json',{'error':str(cleanup)})
        raise

if __name__=='__main__':main()
