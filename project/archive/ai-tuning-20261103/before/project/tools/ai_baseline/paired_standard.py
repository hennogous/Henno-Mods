"""Ten paired Online AI baselines: CSC vanilla Standard and TAR Standard.

Regenerate and verify the five captured Standard worlds, then play each to
250. Configuration and autoplay are the only gameplay interventions; observers
do not place districts, improve tiles, grant research, or change AI preferences.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE))
from run import Runner,write,SAVES,LOGS

spec=importlib.util.spec_from_file_location('paired_map_survey',HERE.parent/'map_survey/run.py')
survey=importlib.util.module_from_spec(spec);spec.loader.exec_module(survey)
GROUPS=[('vanilla-standard',False),('tar-standard',True)]
CHECKPOINTS=[1,*range(25,251,25)]
FIELDS=('terrain','feature','resource','resource_count','continent','river','lake','district','owner','neighbors','water','hills','impassable')

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class PairedRunner(survey.Survey):
    def states(self):
        for attempt in range(8):
            try:return super().states()
            except (RuntimeError,OSError,EOFError):
                if attempt==7:raise
                time.sleep(2)

    def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
        if label.startswith('start-'):
            code=code.replace('ReleasePlayerParameters();',"GameConfiguration.SetValue('CSC_RESOURCE_MAP_ASSISTANCE',1);GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);ReleasePlayerParameters();")
        for attempt in range(8):
            try:return super().cmd(code,state,label,wait,check)
            except (RuntimeError,KeyError,OSError,EOFError) as exc:
                before_send=isinstance(exc,KeyError) or str(exc)=='No responsive tuner states'
                read_only=label=='ready' or label.startswith(('poll-','snapshot-','dump-','actual-'))
                if attempt==7 or not (before_send or read_only):raise
                time.sleep(2)

    def menu(self):
        if not self.keep_game:super().menu()

    def pin_sources(self):
        path=self.out/'controller-source-hashes.json'
        paths=[Path(__file__),HERE/'run.py',HERE/'paired_observer.lua',HERE/'analyze.py',HERE/'capture_reference.py',HERE.parent/'map_survey/run.py',HERE.parent/'map_survey/dump.lua']
        paths+=list(Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/289070/901009089').rglob('*'))
        current={str(p):sha(p) for p in paths if p.is_file()}
        if path.exists():assert current==read(path),'Pinned controller or TAR sources changed'
        else:write(path,current)

    def check_installed(self):
        installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
        for name,digest in read(self.out/'installed-gameplay-hashes.json').items():
            assert sha(installed/name)==digest,('Installed gameplay changed',name)

    def start_pair(self,i,resume_map=False):
        group,tar=GROUPS[(i-1)//5];number=(i-1)%5+1
        folder=self.out/f'game-{i:02d}';folder.mkdir(exist_ok=True)
        original=self.captures/'implemented-vanilla-standard'/f'map-{number:02d}'
        roster=read(original/'settings.json')['leaders']
        self.check_installed()
        if resume_map:self.active_mods=(self.out/group/f'map-{number:02d}'/'enabled-mods.txt').read_text(encoding='utf-8')
        else:self.select_mods(tar)
        self.keep_game=True;self.save_maps=False
        self.start_map(group,tar,2,number,roster,resume=resume_map)
        self.keep_game=False
        capture=self.out/group/f'map-{number:02d}'
        data=read(capture/'map.json');shutil.copy2(capture/'map.json',folder/'initial-map.json')
        prior=read(original/'map.json');comparison={k:sum(p.get(k)!=q.get(k) for p,q in zip(data['plots'],prior['plots'])) for k in FIELDS}
        if not tar:assert not any(comparison.values()),('Captured Standard map did not reproduce',number,comparison)
        write(folder/'map-comparison.json',{'reference':str(original),'exact_original_world_required':not tar,'differences':comparison})
        settings=read(capture/'settings.json');settings.update({'target_turn':250,'ai':'standard','assistance_version':3,'checkpoints':CHECKPOINTS,'game_number':i,'paired_map':number})
        write(folder/'settings.json',settings);shutil.copy2(capture/'enabled-mods.txt',folder/'enabled-mods.txt')
        code="""local a=Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT');assert(a and a.status=='complete' and a.version==3 and a.initialization_turn==1);assert(a.abundance.setting==2);assert(a.abundance.standard_density==DENSITY);print('CSCPAIR_AUDIT='..CSC_MaterialMapCore.Json(a));""".replace('DENSITY','29' if tar else '30')
        text=self.cmd(code,'CSC_MaterialMap',f'assistance-audit-{i}',wait=3)
        write(folder/'assistance-audit.json',json.loads(re.search(r'CSCPAIR_AUDIT=([^\r\n]+)',text).group(1)))
        subprocess.run([sys.executable,str(HERE/'capture_reference.py'),'--output',str(folder/'mechanics-reference.json')],check=True)
        if i==1:shutil.copy2(folder/'mechanics-reference.json',self.out/'mechanics-reference.json')
        self.cmd((HERE/'paired_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay',f'observer-{i}',wait=4)
        self.snapshot(i,1);self.save_checkpoint(i,1)
        self.say(f'Game {i}/10: {group}, paired map {number}, starting world verified')

    def save_checkpoint(self,i,turn):
        folder=self.out/f'game-{i:02d}';name=f'CSC paired AI game {i:02d} turn {turn:03d} 20261016';started=time.time_ns()
        if turn==250:
            closed=[];self.states()
            for state,action in [('NaturalDisasterPopup','OnClose()'),('DiplomacyActionView','Close()')]:
                if state not in self.state:continue
                text=self.cmd("if not ContextPtr:IsHidden() then "+action+";print('CSCPAIR_ENDPOINT_PLAYBACK_CLOSED') end;",state,f'endpoint-playback-{i}-{state}',wait=2)
                if 'CSCPAIR_ENDPOINT_PLAYBACK_CLOSED' in text:closed.append(state)
            # Keep the standardized first-activation census intact. Playback
            # completion may finish automatic city growth within this same
            # turn, so retain a second census describing the saved state.
            text=self.cmd('assert(Game.GetCurrentGameTurn()==250 and not AutoplayManager.IsActive());local old=CSCBASE.checkpoints[250];local ok,e=pcall(function() CSCBASE.checkpoints[250]=nil;CSCBASE.snapshot(250) end);CSCBASE.checkpoints[250]=old;assert(ok,e);','CSC_AdjacencyGameplay',f'snapshot-settled-{i}',wait=5)
            settled=json.loads(re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)',text).group(1));assert settled['turn']==250 and not settled['errors']
            write(folder/'save-state-turn-250.json',settled)
            prior=read(folder/'turn-250.json')
            write(folder/'save-state-comparison.json',{'turn':250,'closed_playback_contexts':closed,'first_activation_census_identical':prior==settled,'changed_sections':[k for k in prior.keys()|settled.keys() if prior.get(k)!=settled.get(k)],'game_turn_advanced':False})
        self.cmd('local s={Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);','PlotInfo',f'save-{i}-{turn}',wait=4)
        path=SAVES/(name+'.Civ6Save')
        for _ in range(45):
            if path.exists() and path.stat().st_mtime_ns>=started and path.stat().st_size>0:
                stamp=(path.stat().st_size,path.stat().st_mtime_ns);time.sleep(1)
                if stamp==(path.stat().st_size,path.stat().st_mtime_ns):break
            time.sleep(1)
        else:raise RuntimeError('Save not confirmed')
        shutil.copy2(path,folder/path.name)
        write(folder/('save.json' if turn==250 else 'initial-save.json'),{'path':str(path),'sha256':sha(path),'turn':turn})
        if turn==250:
            logs=folder/'logs';logs.mkdir(exist_ok=True)
            for p in LOGS.iterdir():
                if p.is_file() and p.suffix in ('.log','.csv'):shutil.copy2(p,logs/p.name)

    def snapshot(self,i,target):
        text=self.cmd(f'CSCBASE.snapshot({target});','CSC_AdjacencyGameplay',f'snapshot-{i}-{target}',wait=5)
        data=json.loads(re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)',text).group(1))
        assert data['turn']==target and not data['errors'],(target,data.get('errors'))
        write(self.out/f'game-{i:02d}'/f'turn-{target:03d}.json',data)
        self.say(f'Game {i}: snapshot turn {target}, {len(data["cities"])} major cities, {len(data["events"])} observed events')

    def autoplay(self,i,target,resume=False):
        code=f'''Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);if not CSCPAIR_RETURN_GUARD then CSCPAIR_RETURN_GUARD=function() if AutoplayManager.IsActive() then local alive=PlayerManager.GetAliveMajors();if alive[1] then AutoplayManager.SetReturnAsPlayer(alive[1]:GetID());print('CSCPAIR_ALIVE_RETURN',alive[1]:GetID()) end end end;Events.PlayerDefeat.Add(CSCPAIR_RETURN_GUARD) end;AutoplayManager.SetTurns({target}-Game.GetCurrentGameTurn());AutoplayManager.SetReturnAsPlayer(PlayerManager.GetAliveMajors()[1]:GetID());AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);'''
        if not resume:self.cmd(code,'GameCore_Tuner',f'autoplay-{i}-{target}',check=False)
        deadline=time.monotonic()+3600;last_turn=-1;last_progress=time.monotonic();last_report=0;inactive_checks=0;last_release=0
        while time.monotonic()<deadline:
            time.sleep(8)
            text=self.cmd('if AutoplayManager.IsActive() then local alive=PlayerManager.GetAliveMajors();if alive[1] then AutoplayManager.SetReturnAsPlayer(alive[1]:GetID()) end end;print("CSCPAIR_PROGRESS",Game.GetCurrentGameTurn(),AutoplayManager.IsActive(),AutoplayManager.GetTurns());','GameCore_Tuner',f'poll-{i}',wait=1)
            m=re.search(r'CSCPAIR_PROGRESS\s+(\d+)\s+(true|false)\s+(-?\d+)',text)
            if not m:continue
            turn=int(m.group(1));active=m.group(2)=='true'
            if turn!=last_turn:last_progress=time.monotonic();last_turn=turn
            if time.monotonic()-last_report>45:self.say(f'Game {i}: turn {turn}, target {target}, autoplay={active}');last_report=time.monotonic()
            if not active:
                if turn<target:
                    inactive_checks+=1
                    if inactive_checks<=3:continue
                assert turn==target,('Autoplay endpoint',turn,target)
                self.snapshot(i,target);return
            assert turn<=target,'Autoplay overrun'
            if time.monotonic()-last_progress>35 and time.monotonic()-last_release>35:
                for state,action in [('NaturalDisasterPopup','OnLocalPlayerTurnEnd()'),('DiplomacyActionView','Close()')]:
                    if state not in self.state:continue
                    # Pure UI cleanup: DiplomacyActionView.Close releases its
                    # event lock without AddResponse or CloseSession. Only act
                    # in observer mode, never make a player's diplomatic choice.
                    text=self.cmd("if Game.GetLocalPlayer()==-1 and not ContextPtr:IsHidden() then "+action+";print('CSCPAIR_PLAYBACK_RELEASED') end;",state,f'playback-{i}-{turn}-{state}',wait=1)
                    if 'CSCPAIR_PLAYBACK_RELEASED' in text:
                        self.say(f'Game {i}: released {state} playback at turn {turn}')
                        path=self.out/'playback-recoveries.json';records=read(path) if path.exists() else []
                        records.append({'game':i,'turn':turn,'target':target,'context':state,'gameplay_response_submitted':False});write(path,records)
                last_release=time.monotonic()
            if time.monotonic()-last_progress>240:raise RuntimeError(f'Autoplay stalled at {turn}')
        raise TimeoutError('Autoplay checkpoint took more than one hour')

def verify(out,partial=False):
    folders=[p.parent for p in sorted(out.glob('game-*/complete.json'))]
    if not partial:assert len(folders)==10
    hashes=read(out/'controller-source-hashes.json');assert all(sha(Path(p))==h for p,h in hashes.items())
    installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    ih=read(out/'installed-gameplay-hashes.json');assert all(sha(installed/p)==h for p,h in ih.items())
    result={'status':'passed','games':[],'snapshots':0,'installed_files':len(ih),'observer_errors':0}
    for folder in folders:
        i=int(folder.name[-2:]);paths=sorted(folder.glob('turn-*.json'));assert [int(p.stem[-3:]) for p in paths]==CHECKPOINTS,folder
        previous=[]
        for p,t in zip(paths,CHECKPOINTS):
            s=read(p);assert s['turn']==t and (s['width'],s['height'])==(74,46) and not s['errors'],p
            assert s['events'][:len(previous)]==previous,('Missing event history',p)
            previous=s['events'];result['snapshots']+=1
            for c in s['cities']:
                for d in c['districts']:
                    if not d.get('quarter'):continue
                    for cat in ('base','spec'):
                        material=[m for m in d['site']['materials'] if m['category']==cat and m['owner']==c['player']]
                        assert len(material)==d['site'][cat]
                        assert sum(bool(m.get('improvement')) and not m['pillaged'] for m in material)==d['site'][cat+'_improved']
        for name in ('initial-save.json','save.json'):
            save=read(folder/name);assert sha(folder/Path(save['path']).name)==save['sha256']
        assert not [x for x in (folder/'logs/Database.log').read_text(errors='replace').splitlines() if '[Gameplay]' in x and 'ERROR' in x]
        injected=sorted((out/'commands').glob(f'*-observer-{i}.lua'));assert injected[-1].read_text()==(HERE/'paired_observer.lua').read_text()
        if i<=5:assert not any(read(folder/'map-comparison.json')['differences'].values())
        assert read(folder/'complete.json')['turn']==250
        result['games'].append({'game':i,'group':read(folder/'settings.json')['group'],'turn':250,'snapshots':11,'events':len(previous)})
    write(out/'validation.json',result);print('Verified',len(folders),'completed games /',result['snapshots'],'snapshots',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--captures',type=Path,required=True);p.add_argument('--first',type=int,default=1);p.add_argument('--last',type=int,default=10);p.add_argument('--resume-current',action='store_true');p.add_argument('--resume-map',action='store_true');p.add_argument('--resume-blocked',action='store_true');p.add_argument('--resume-running',action='store_true');p.add_argument('--verify-only',action='store_true');a=p.parse_args()
    if a.verify_only:verify(a.output,a.last<10);return
    r=PairedRunner(a.output);r.captures=a.captures;r.keep_game=False;r.pin_sources()
    if not a.resume_current and not a.resume_map:r.wait('MainMenu');r.config()
    try:
        write(a.output/'batch.json',{'status':'running','target_games':10,'target_turn':250,'groups':[g[0] for g in GROUPS]})
        for i in range(a.first,a.last+1):
            if (a.output/f'game-{i:02d}'/'complete.json').exists():continue
            if a.resume_current and i==a.first:
                text=r.cmd('assert(CSCBASE and CSCBASE.version==3);'+('' if a.resume_blocked or a.resume_running else 'assert(not AutoplayManager.IsActive());')+'print("CSCPAIR_CURRENT",Game.GetCurrentGameTurn(),AutoplayManager.IsActive());','CSC_AdjacencyGameplay','resume',wait=4)
                match=re.search(r'CSCPAIR_CURRENT\s+(\d+)\s+(true|false)',text);current=int(match.group(1));active=match.group(2)=='true';assert 1<=current<=250
                if current in CHECKPOINTS:r.snapshot(i,current)
            else:r.start_pair(i,resume_map=a.resume_map and i==a.first);current=1;active=False
            if current<250:r.autoplay(i,250,resume=active)
            else:r.snapshot(i,250)
            for target in CHECKPOINTS[1:-1]:r.snapshot(i,target)
            r.save_checkpoint(i,250);r.check_installed()
            write(a.output/f'game-{i:02d}'/'complete.json',{'status':'complete','turn':250})
            r.menu();verify(a.output,True)
        r.restore()
        write(a.output/'preferences-restored.json',{'verified':True,'auto_start':read(a.output/'original-preferences.json')['auto_start']})
        verify(a.output,a.last<10)
        write(a.output/'batch.json',{'status':'complete' if a.last==10 else 'partial','target_turn':250,'games':[int(p.parent.name[-2:]) for p in sorted(a.output.glob('game-*/complete.json'))]})
    except BaseException as exc:
        write(a.output/'batch.json',{'status':'interrupted','error':str(exc),'traceback':traceback.format_exc()});r.say('STOPPED: '+str(exc));raise

if __name__=='__main__':main()
