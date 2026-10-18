"""Generate paired CSC maps for three resource setups; never advance a turn."""
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
sys.path.insert(0,str(ROOT/'project/tools/ai_baseline'))
from run import Runner,write,SAVES,LOGS,CSC

TAR='960c7ce4-c961-43c8-90bf-282eb7b260ea'
GROUPS=[('vanilla-abundant',False,3),('tar-abundant',True,3),('tar-truly-abundant',True,45)]
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class Survey(Runner):
    def select_mods(self,tar):
        code=f'''local handle=nil;for _,m in ipairs(Modding.GetInstalledMods()) do if string.lower(m.Id)=='{TAR}' then handle=m.Handle end end;assert(handle,'TAR not installed');'''
        code+= 'Modding.EnableMod(handle,true);' if tar else 'Modding.DisableMod({handle});'
        code+=f'''for _,m in ipairs(Modding.GetInstalledMods()) do if m.Enabled then if not m.Official then assert(string.lower(m.Id)=='{CSC}' or ({str(tar).lower()} and string.lower(m.Id)=='{TAR}'),'Unexpected community mod '..m.Id);end;print("CSCMAP_MOD",m.Id,m.Name,m.Official) end end;'''
        self.active_mods=self.cmd(code,'MainMenu','select-mods-'+str(tar),wait=3)

    def start_map(self,group,tar,resource,i,roster,resume=False):
        folder=self.out/group/f'map-{i:02d}';folder.mkdir(parents=True,exist_ok=True)
        ms=830001+i*101;gs=940001+i*103
        settings={'group':group,'map_number':i,'map_seed':ms,'game_seed':gs,'map':'Continents.lua','map_size':'MAPSIZE_SMALL','players':6,'city_states':9,'speed':'GAMESPEED_ONLINE','difficulty':'DIFFICULTY_PRINCE','resource_setting':resource,'csc':True,'tar':tar,'leaders':roster,'animal_resources':1,'turns_to_advance':0}
        write(folder/'settings.json',settings)
        (folder/'enabled-mods.txt').write_text(self.active_mods,encoding='utf-8')
        leaders='local leaders={'+','.join(json.dumps(x) for x in roster)+'};for j,pid in ipairs(GameConfiguration.GetParticipatingPlayerIDs()) do PlayerConfigurations[pid]:SetLeaderTypeName(leaders[j]);end;'
        code=f'''GameConfiguration.SetToDefaults();GameConfiguration.SetRuleSet('RULESET_EXPANSION_2');BuildHeadlessGameSetup();RebuildPlayerParameters(true);GameSetup_RefreshParameters();MapConfiguration.SetScript('Continents.lua');MapConfiguration.SetMapSize('MAPSIZE_SMALL');GameConfiguration.SetParticipatingPlayerCount(6);GameConfiguration.SetValue('CITY_STATE_COUNT',9);GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE');GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE');GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',{gs});MapConfiguration.SetValue('RANDOM_SEED',{ms});MapConfiguration.SetValue('resources',{resource});GameConfiguration.SetValue('CSC_INCLUDE_ANIMAL_RESOURCES',1);GameConfiguration.SetValue('CSC_REMOVE_UNUSED_MODDED_RESOURCES',1);GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false);'''+leaders+f'''assert(MapConfiguration.GetValue('resources')=={resource});ReleasePlayerParameters();HideGameSetup();Automation.SetAutoStartEnabled(true);print('CSCMAP_SETUP',GameConfiguration.GetGameSpeedType(),MapConfiguration.GetMapSize(),MapConfiguration.GetValue('resources'));Network.HostGame(ServerType.SERVER_TYPE_NONE);'''
        self.say(f'{group} map{i}: '+('resuming loaded map' if resume else f'generating seed{ms}, resources{resource}, Online'))
        if not resume:self.cmd(code,'MainMenu',f'start-{group}-{i}',wait=3,check=False)
        self.wait('CSC_AdjacencyGameplay',300)
        for _ in range(50):
            text=self.cmd('print("CSCMAP_READY",Game.GetCurrentGameTurn());','GameCore_Tuner','ready',wait=2)
            found=re.search(r'CSCMAP_READY\s+(\d+)',text)
            if found and int(found.group(1))==1:break
            time.sleep(2)
        else:raise RuntimeError('Map did not reach turn1')
        text=self.cmd(Path(__file__).with_name('dump.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay',f'dump-{group}-{i}',wait=5)
        found=re.search(r'CSCMAP_SURVEY=([^\r\n]+)',text);assert found,'No map dump'
        data=json.loads(found.group(1));assert data['turn']==1
        assert (data['width'],data['height'],len(data['plots']))==(74,46,3404)
        assert [p['leader'] for p in sorted(data['players'],key=lambda p:p['id'])]==roster
        write(folder/'map.json',data)
        actual=self.cmd('local speed=GameInfo.GameSpeeds[GameConfiguration.GetGameSpeedType()];print("CSCMAP_ACTUAL",speed and speed.GameSpeedType,MapConfiguration.GetValue("resources"),GameConfiguration.GetValue("CSC_INCLUDE_ANIMAL_RESOURCES"));','PlotInfo',f'actual-{group}-{i}',wait=2)
        (folder/'actual-settings.txt').write_text(actual,encoding='utf-8')
        assert re.search(r'CSCMAP_ACTUAL\s+GAMESPEED_ONLINE\s+'+str(resource)+r'\s+1',actual),actual
        save_hash=None
        if self.save_maps:
            name=f'CSC materials {group} map {i} 20261016';started=time.time_ns()
            self.cmd('local s={Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);','PlotInfo',f'save-{group}-{i}',wait=4)
            path=SAVES/(name+'.Civ6Save')
            for _ in range(60):
                if path.exists() and path.stat().st_mtime_ns>=started and path.stat().st_size>0:
                    stamp=(path.stat().st_size,path.stat().st_mtime_ns);time.sleep(1)
                    if stamp==(path.stat().st_size,path.stat().st_mtime_ns):break
                time.sleep(1)
            else:raise RuntimeError('Map save not confirmed')
            shutil.copy2(path,folder/path.name);save_hash=sha(path);write(folder/'save.json',{'path':str(path),'sha256':save_hash})
        logs=folder/'logs';logs.mkdir(exist_ok=True)
        for name in ('Database.log','Modding.log','Lua.log'):
            if (LOGS/name).exists():shutil.copy2(LOGS/name,logs/name)
        write(folder/'complete.json',{'status':'complete','turn':1,'plots':3404,'saved':self.save_maps,'save_sha256':save_hash})
        self.say(f'{group} map{i}: complete3404tiles, turn1'+(', save verified' if self.save_maps else ', numbers only'))
        self.menu()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--rosters',type=Path,required=True);p.add_argument('--save-maps',action='store_true');p.add_argument('--resume-current',action='store_true');p.add_argument('--resume-group',default='vanilla-abundant',choices=[g[0] for g in GROUPS]);p.add_argument('--resume-map',type=int,default=1);a=p.parse_args()
    r=Survey(a.output);r.save_maps=a.save_maps
    try:
        if not a.resume_current:r.config()
        shutil.copy2(Path(__file__).with_name('materials.json'),a.output/'materials.json')
        locked={}
        for path in [*Path(__file__).parent.glob('*.py'),Path(__file__).with_name('dump.lua'),Path(__file__).with_name('materials.json'),* (ROOT/'docs/content/quarters').glob('*.md')]:locked[str(path)]=sha(path)
        tarroot=Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/289070/901009089')
        for path in tarroot.rglob('*'):
            if path.is_file():locked[str(path)]=sha(path)
        write(a.output/('source-hashes-current.json' if (a.output/'source-hashes.json').exists() else 'source-hashes.json'),locked)
        write(a.output/'batch.json',{'status':'running','target_maps':15,'groups':[g[0] for g in GROUPS]})
        for group,tar,resource in GROUPS:
            if a.resume_current and group==a.resume_group:r.active_mods=(a.output/group/f'map-{a.resume_map:02d}'/'enabled-mods.txt').read_text(encoding='utf-8')
            else:r.select_mods(tar)
            for i in range(1,6):
                if (a.output/group/f'map-{i:02d}'/'complete.json').exists():continue
                roster=[p['leader'] for p in sorted(read(a.rosters/f'game-{i:02d}'/'turn-001.json')['players'],key=lambda p:p['id'])]
                r.start_map(group,tar,resource,i,roster,a.resume_current and group==a.resume_group and i==a.resume_map)
        r.restore();write(a.output/'batch.json',{'status':'complete','maps':15,'turns_advanced':0})
    except BaseException as exc:
        write(a.output/'batch.json',{'status':'interrupted','error':str(exc),'traceback':traceback.format_exc()});r.say('STOPPED: '+str(exc));raise

if __name__=='__main__':main()
