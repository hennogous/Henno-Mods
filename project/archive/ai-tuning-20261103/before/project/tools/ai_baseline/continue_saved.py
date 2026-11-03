"""Continue the five archived turn-200 worlds without modifying gameplay."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import time
import traceback

from run import Runner, SAVES, LOGS, HOME, write

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

class Continuation(Runner):
    def __init__(self, out, source):
        super().__init__(out); self.source=source; self.prefix=[]

    def prepare(self):
        hashes=read(self.source/'installed-gameplay-hashes.json')
        installed=HOME/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
        assert all((installed/p).exists() and sha(installed/p)==v for p,v in hashes.items()), 'Installed build differs from baseline'
        for name in ('installed-gameplay-hashes.json','mechanics-reference.json','checkpoint-exceptions.json'):
            shutil.copy2(self.source/name,self.out/name)
        for i in range(1,6):
            src=self.source/f'game-{i:02d}';dst=self.out/src.name;dst.mkdir(exist_ok=True)
            for path in [src/'settings.json',*src.glob('turn-*.json')]:
                if not (dst/path.name).exists():shutil.copy2(path,dst/path.name)
        write(self.out/'continuation.json',{'source':str(self.source),'start_turn':200,'target_turn':400,'checkpoints':list(range(225,401,25)),'events':'original turn-200 prefix plus fresh read-only observer history'})

    def load(self,i):
        self.wait('MainMenu');src=self.source/f'game-{i:02d}';meta=read(src/'save.json');saved=src/Path(meta['path']).name
        assert sha(saved)==meta['sha256'],'Source save checksum differs'
        self.prefix=read(src/'turn-200.json')['events']
        self.say(f'Game {i}: loading archived turn-200 save')
        self.cmd(f'Automation.SetAutoStartEnabled(true);print("CSCBASE_LOAD",Network.LoadGame({json.dumps(str(saved))},ServerType.SERVER_TYPE_NONE));','MainMenu',f'load-{i}',wait=3,check=False)
        self.wait('CSC_AdjacencyGameplay',300)
        self.cmd('assert(Game.GetCurrentGameTurn()==200);assert(not AutoplayManager.IsActive());Automation.SetActive(false);print("CSCBASE_LOADED",Game.GetCurrentGameTurn(),Game.GetLocalPlayer());','GameCore_Tuner',f'loaded-{i}',wait=3)
        self.cmd(Path(__file__).with_name('observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay',f'observer-{i}',wait=4)
        data=self.capture(i,200,False)
        before=read(src/'turn-200.json')
        def city_identity(s):return sorted((c['player'],c['id'],c['population'],tuple(sorted((d['type'],d['plot'],d['complete']) for d in c['districts'])),tuple(sorted((b['type'],b['plot'],b['pillaged']) for b in c['buildings']))) for c in s['cities'])
        assert city_identity(before)==city_identity(data),'Reload city state differs'
        assert before['plots']==data['plots'],'Reload plot state differs'
        write(self.out/f'game-{i:02d}'/'reload-validation.json',{'status':'passed','turn':200,'source_save_sha256':sha(saved),'city_and_plot_state_identical':True})

    def capture(self,i,target,merge=True):
        text=self.cmd('CSCBASE.snapshot();','CSC_AdjacencyGameplay',f'snapshot-{i}-{target}',wait=5)
        match=re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)',text);assert match,'Missing snapshot'
        data=json.loads(match.group(1));assert data['turn']==target,(data['turn'],target)
        assert not data['errors'],data['errors']
        if merge:data['events']=self.prefix+data['events']
        path=self.out/f'game-{i:02d}'/(f'turn-{target:03d}.json' if merge else 'reload-turn-200.json')
        write(path,data);self.say(f'Game {i}: snapshot turn {target}, {len(data["cities"])} cities, {len(data["events"])} events')
        return data

    def snapshot(self,i,target):return self.capture(i,target)

    def save(self,i):
        name=f'CSC AI baseline game {i} turn 400 20261016';start=time.time_ns()
        self.cmd('local s={Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);','PlotInfo',f'save-{i}',wait=4)
        path=SAVES/(name+'.Civ6Save')
        for _ in range(60):
            if path.exists() and path.stat().st_mtime_ns>=start and path.stat().st_size>0:
                stamp=(path.stat().st_size,path.stat().st_mtime_ns);time.sleep(1)
                if stamp==(path.stat().st_size,path.stat().st_mtime_ns):break
            time.sleep(1)
        else:raise RuntimeError('Completed save not found')
        folder=self.out/f'game-{i:02d}';shutil.copy2(path,folder/path.name)
        write(folder/'save.json',{'path':str(path),'sha256':sha(path)})
        logs=folder/'logs';logs.mkdir(exist_ok=True)
        for path in LOGS.iterdir():
            if path.is_file() and path.suffix in ('.log','.csv'):shutil.copy2(path,logs/path.name)
        self.say(f'Game {i}: turn-400 save and logs archived')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--first',type=int,default=1);p.add_argument('--last',type=int,default=5);p.add_argument('--resume-current',action='store_true',help='Resume first game with the original live observer intact');a=p.parse_args()
    r=Continuation(a.output,a.source);r.prepare()
    try:
        if not a.resume_current:r.config()
        write(a.output/'batch.json',{'status':'running','target':400})
        for i in range(a.first,a.last+1):
            if (a.output/f'game-{i:02d}'/'complete.json').exists():continue
            if a.resume_current and i==a.first:
                r.prefix=read(a.source/f'game-{i:02d}'/'turn-200.json')['events']
                text=r.cmd('assert(CSCBASE);assert(not AutoplayManager.IsActive());assert(Game.GetLocalPlayer()>=0);print("CSCBASE_TURN",Game.GetCurrentGameTurn());','CSC_AdjacencyGameplay',f'resume-{i}')
                current=int(re.search(r'CSCBASE_TURN\s+(\d+)',text).group(1))
            else:r.load(i);current=200
            for target in range(225,401,25):
                if target>current:r.autoplay(i,target)
            r.save(i);write(a.output/f'game-{i:02d}'/'complete.json',{'turn':400,'status':'complete'});r.menu()
        r.restore();write(a.output/'batch.json',{'status':'complete','target':400,'games':[int(p.parent.name.split('-')[1]) for p in a.output.glob('game-*/complete.json')]})
    except BaseException as exc:
        write(a.output/'batch.json',{'status':'interrupted','error':str(exc),'traceback':traceback.format_exc()});r.say('STOPPED: '+str(exc));raise

if __name__=='__main__':main()
