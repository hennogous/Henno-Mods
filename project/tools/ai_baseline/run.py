"""Five natural CSC/vanilla-AI games, read-only observations, reproducible seeds.

Requires the main menu. Preserves mod preferences and auto-start; never edits
gameplay source, creates map fixtures, grants resources, or changes AI priorities.
Generated evidence goes to the explicitly required output directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/adjacencies'))
import tuner

CSC='c5e66bd1-d804-443b-ac3d-1917a20dba3c'
HOME=Path.home()
SAVES=HOME/"Documents/My Games/Sid Meier's Civilization VI/Saves/Single"
LOGS=HOME/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Logs"

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

class Runner:
    def __init__(self,out):
        self.out=out;out.mkdir(parents=True,exist_ok=True);self.seq=max([int(p.name.split('-')[0]) for p in (out/'commands').glob('*.lua')]+[0]);self.state={}
        self.log=(out/'progress.log').open('a',encoding='utf-8')
    def say(self,s):
        s=time.strftime('%H:%M:%S ')+s;print(s,flush=True);self.log.write(s+'\n');self.log.flush()
    def states(self):
        for port in (4318,4320,4321,4322,4319):
            tuner.PORT=port
            try:
                states=tuner.states()
                if states:self.state=states;return states
            except (OSError,EOFError,ValueError):pass
        raise RuntimeError('No responsive tuner states')
    def wait(self,name,seconds=240):
        deadline=time.monotonic()+seconds
        while time.monotonic()<deadline:
            try:
                if name in self.states():return
            except (OSError,RuntimeError,EOFError):pass
            time.sleep(3)
        raise TimeoutError('Waiting for '+name)
    def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
        self.seq+=1;token='CSCBASE_OK_'+str(self.seq)
        wrapped='local ok,e=pcall(function()\n'+code+'\nend);print("'+token+'",ok,tostring(e));'
        self.states();messages=tuner.command(wrapped,self.state[state],wait)
        text='\n'.join(messages)
        evidence=self.out/'commands'/f'{self.seq:04d}-{label}'
        evidence.parent.mkdir(parents=True,exist_ok=True)
        evidence.with_suffix('.lua').write_text(code,encoding='utf-8')
        evidence.with_suffix('.txt').write_text(text,encoding='utf-8')
        if check and not re.search(re.escape(token)+r'\s+true',text):raise RuntimeError(label+' failed: '+text[-3000:])
        return text
    def config(self):
        self.wait('MainMenu')
        original=self.out/'original-preferences.json'
        if not original.exists():
            text=self.cmd('''local e={};for _,m in ipairs(Modding.GetInstalledMods()) do if m.Source=='Mod' and not m.Official then e[#e+1]='"'..m.Id..'":'..tostring(m.Enabled) end end;print('CSCBASE_PREFS={'..table.concat(e,',')..'}');print('CSCBASE_AUTO',Automation.IsAutoStartEnabled());''','MainMenu','preferences')
            write(original,{'mods':json.loads(re.search(r'CSCBASE_PREFS=(\{[^\r\n]*\})',text).group(1)),'auto_start':re.search(r'CSCBASE_AUTO\s+(true|false)',text).group(1)=='true'})
        text=self.cmd(f'''local disable={{}};local csc=nil;for _,m in ipairs(Modding.GetInstalledMods()) do if m.Source=='Mod' and not m.Official then if m.Id=='{CSC}' then csc=m.Handle elseif m.Enabled then disable[#disable+1]=m.Handle end end end;if #disable>0 then Modding.DisableMod(disable) end;assert(csc,'CSC not installed');Modding.EnableMod(csc,true);for _,m in ipairs(Modding.GetInstalledMods()) do if m.Enabled then print('CSCBASE_ENABLED',m.Id,m.Name,m.Official) end end;Automation.SetAutoStartEnabled(true);''','MainMenu','enable-csc')
        (self.out/'enabled-mods.txt').write_text(text,encoding='utf-8')
        installed=HOME/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
        hashes={str(p.relative_to(installed)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in installed.rglob('*') if p.is_file() and p.suffix in ('.sql','.lua','.xml','.modinfo')}
        write(self.out/'installed-gameplay-hashes.json',hashes)
        for p in SAVES.glob('CSC before AI baseline 20261015.Civ6Save'):shutil.copy2(p,self.out/p.name)
    def start(self,i):
        self.wait('MainMenu');ms=830001+i*101;gs=940001+i*103
        write(self.out/f'game-{i:02d}'/'settings.json',{'map_seed':ms,'game_seed':gs,'map':'Continents.lua','map_size':'MAPSIZE_SMALL','players':6,'city_states':9,'speed':'GAMESPEED_STANDARD','difficulty':'DIFFICULTY_PRINCE','target_turn':200,'ai':'standard','mods':[CSC],'modes':False})
        code=f'''GameConfiguration.SetToDefaults();GameConfiguration.SetRuleSet('RULESET_EXPANSION_2');BuildHeadlessGameSetup();RebuildPlayerParameters(true);GameSetup_RefreshParameters();MapConfiguration.SetScript('Continents.lua');MapConfiguration.SetMapSize('MAPSIZE_SMALL');GameConfiguration.SetParticipatingPlayerCount(6);GameConfiguration.SetValue('CITY_STATE_COUNT',9);GameConfiguration.SetGameSpeedType('GAMESPEED_STANDARD');GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE');GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',{gs});MapConfiguration.SetValue('RANDOM_SEED',{ms});GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false);for _,pid in ipairs(GameConfiguration.GetParticipatingPlayerIDs()) do PlayerConfigurations[pid]:SetLeaderTypeName(nil);end;ReleasePlayerParameters();HideGameSetup();Automation.SetAutoStartEnabled(true);print('CSCBASE_SETUP',GameConfiguration.GetGameSpeedType(),MapConfiguration.GetMapSize(),GameConfiguration.GetParticipatingPlayerCount());Network.HostGame(ServerType.SERVER_TYPE_NONE);'''
        self.say(f'Game {i}: starting seeds map={ms} game={gs}')
        self.cmd(code,'MainMenu',f'start-{i}',wait=3,check=False)
        self.wait('CSC_AdjacencyGameplay',300)
        # Gameplay contexts can appear before native auto-start dismisses loading.
        for attempt in range(50):
            text=self.cmd('print("CSCBASE_TURN",Game.GetCurrentGameTurn());','GameCore_Tuner','ready')
            found=re.search(r'CSCBASE_TURN\s+(\d+)',text)
            if found and int(found.group(1))>=1:break
            time.sleep(3)
        else:raise RuntimeError('Game did not reach turn 1')
        self.cmd((Path(__file__).with_name('observer.lua')).read_text(encoding='utf-8'),'CSC_AdjacencyGameplay',f'observer-{i}',wait=4)
        self.snapshot(i,1)
        data=json.loads((self.out/f'game-{i:02d}'/'turn-001.json').read_text())
        assert (data['width'],data['height'])==(74,46),'Expected native Small map, got '+str((data['width'],data['height']))
        assert len(data['players'])==6,'Expected six major civilizations'
    def snapshot(self,i,target):
        text=self.cmd('CSCBASE.snapshot();','CSC_AdjacencyGameplay',f'snapshot-{i}-{target}',wait=5)
        match=re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)',text)
        if not match:raise RuntimeError('Missing snapshot')
        data=json.loads(match.group(1));assert data['turn']==target,(data['turn'],target)
        write(self.out/f'game-{i:02d}'/f'turn-{target:03d}.json',data)
        if data['errors']:raise RuntimeError('Observer errors: '+str(data['errors'])[:2000])
        self.say(f'Game {i}: snapshot turn {target}, {len(data["cities"])} major cities, {len(data["events"])} observed events')
    def autoplay(self,i,target):
        code=f'''Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetTurns({target}-Game.GetCurrentGameTurn());AutoplayManager.SetReturnAsPlayer(PlayerManager.GetAliveMajors()[1]:GetID());AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);print('CSCBASE_AUTOPLAY',Game.GetCurrentGameTurn(),AutoplayManager.GetTurns(),AutoplayManager.IsActive());'''
        self.cmd(code,'GameCore_Tuner',f'autoplay-{i}-{target}',check=False)
        deadline=time.monotonic()+3600;last_turn=-1;last_progress=time.monotonic();last_report=0;inactive_checks=0
        while time.monotonic()<deadline:
            time.sleep(8)
            try:text=self.cmd('print("CSCBASE_PROGRESS",Game.GetCurrentGameTurn(),AutoplayManager.IsActive(),AutoplayManager.GetTurns());','GameCore_Tuner',f'poll-{i}',wait=1)
            except (OSError,EOFError,RuntimeError) as exc:self.say('Transient tuner: '+str(exc)[:150]);continue
            m=re.search(r'CSCBASE_PROGRESS\s+(\d+)\s+(true|false)\s+(-?\d+)',text)
            if not m:continue
            turn=int(m.group(1));active=m.group(2)=='true'
            if turn!=last_turn:last_progress=time.monotonic();last_turn=turn
            if time.monotonic()-last_report>45:self.say(f'Game {i}: turn {turn}, target {target}, autoplay={active}');last_report=time.monotonic()
            if not active:
                if turn<target:
                    # IsActive can clear before the pending round-boundary tick.
                    inactive_checks+=1
                    if inactive_checks<=3:
                        self.say(f'Game {i}: waiting for final turn tick ({turn} -> {target})');continue
                    raise RuntimeError(f'Autoplay stopped at {turn}, wanted {target}')
                if turn!=target:raise RuntimeError(f'Autoplay stopped at {turn}, wanted {target}')
                self.snapshot(i,target);return
            if turn>target:raise RuntimeError('Autoplay overrun')
            if time.monotonic()-last_progress>180:raise RuntimeError(f'Autoplay stalled at {turn}')
        raise TimeoutError('Autoplay took over one hour for a checkpoint')
    def save(self,i):
        name=f'CSC AI baseline game {i} turn 200 20261015';start=time.time_ns()
        self.cmd('local s={Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);','PlotInfo',f'save-{i}',wait=4)
        path=SAVES/(name+'.Civ6Save')
        for _ in range(40):
            if path.exists() and path.stat().st_mtime_ns>=start and path.stat().st_size>0:
                a=(path.stat().st_size,path.stat().st_mtime_ns);time.sleep(1)
                if a==(path.stat().st_size,path.stat().st_mtime_ns):break
            time.sleep(1)
        else:raise RuntimeError('Completed save not found')
        shutil.copy2(path,self.out/f'game-{i:02d}'/path.name)
        write(self.out/f'game-{i:02d}'/'save.json',{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        folder=self.out/f'game-{i:02d}'/'logs';folder.mkdir(exist_ok=True)
        for p in LOGS.iterdir():
            if p.is_file() and (p.suffix in ('.log','.csv')):shutil.copy2(p,folder/p.name)
        self.say(f'Game {i}: completed save and logs archived')
    def menu(self):
        self.cmd('Events.ExitToMainMenu();','PlotInfo','return-menu',wait=2,check=False);self.wait('MainMenu',180)
    def restore(self):
        original=json.loads((self.out/'original-preferences.json').read_text())
        entries=','.join('['+json.dumps(k)+']='+str(v).lower() for k,v in original['mods'].items())
        code='local wanted={'+entries+'''};local disable={};for _,m in ipairs(Modding.GetInstalledMods()) do if wanted[m.Id]==false and m.Enabled then disable[#disable+1]=m.Handle end end;if #disable>0 then Modding.DisableMod(disable) end;for _,m in ipairs(Modding.GetInstalledMods()) do if wanted[m.Id]==true then Modding.EnableMod(m.Handle,true) end end;for _,m in ipairs(Modding.GetInstalledMods()) do if wanted[m.Id]~=nil then assert(m.Enabled==wanted[m.Id],m.Id) end end;Automation.SetAutoStartEnabled('''+str(original['auto_start']).lower()+''');assert(Automation.IsAutoStartEnabled()=='''+str(original['auto_start']).lower()+''');print('CSCBASE_RESTORED');'''
        self.cmd(code,'MainMenu','restore',wait=3);self.say('Original mod preferences and auto-start restored')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--first',type=int,default=1);p.add_argument('--last',type=int,default=5);p.add_argument('--restore-only',action='store_true');p.add_argument('--resume-current',action='store_true',help='Resume the first numbered game from its live checkpoint; observer must still be loaded');a=p.parse_args()
    r=Runner(a.output)
    if a.restore_only:r.wait('MainMenu');r.restore();return
    try:
        if not a.resume_current:r.config()
        write(a.output/'batch.json',{'status':'running','first':a.first,'last':a.last})
        for i in range(a.first,a.last+1):
            if a.resume_current and i==a.first:
                text=r.cmd('assert(CSCBASE);assert(not AutoplayManager.IsActive());print("CSCBASE_TURN",Game.GetCurrentGameTurn());','CSC_AdjacencyGameplay','resume')
                current=int(re.search(r'CSCBASE_TURN\s+(\d+)',text).group(1))
                if current in (1,25,50,75,100,125,150,175,200):r.snapshot(i,current)
            else:r.start(i);current=1
            for target in (25,50,75,100,125,150,175,200):
                if target>current:r.autoplay(i,target)
            r.save(i);write(a.output/f'game-{i:02d}'/'complete.json',{'turn':200,'status':'complete'});r.menu()
        r.restore();write(a.output/'batch.json',{'status':'complete','games':[int(p.parent.name.split('-')[1]) for p in sorted(a.output.glob('game-*/complete.json'))]})
    except BaseException as exc:
        write(a.output/'batch.json',{'status':'interrupted','error':str(exc),'traceback':traceback.format_exc()});r.say('STOPPED: '+str(exc));raise

if __name__=='__main__':main()
