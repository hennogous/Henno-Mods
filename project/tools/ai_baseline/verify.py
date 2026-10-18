"""Verify completed baseline evidence without connecting to the game."""
import argparse
import hashlib
import json
from pathlib import Path

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-partial',action='store_true');p.add_argument('--turn',type=int,default=200);a=p.parse_args()
    folders=[p.parent for p in sorted(a.output.glob('game-*/complete.json'))]
    if not a.allow_partial:assert [p.name for p in folders]==[f'game-{i:02d}' for i in range(1,6)],'Five completed games required'
    result={'status':'passed','games':[],'snapshot_count':0,'observer_errors':0}
    expected_default=[1,*range(25,a.turn+1,25)]
    exceptions=read(a.output/'checkpoint-exceptions.json') if (a.output/'checkpoint-exceptions.json').exists() else {}
    observer=Path(__file__).with_name('observer.lua').read_text(encoding='utf-8')
    for folder in folders:
        expected=[exceptions.get(folder.name,{}).get(str(turn),turn) for turn in expected_default]
        paths=sorted(folder.glob('turn-*.json'));assert [int(p.stem.split('-')[1]) for p in paths]==expected,folder
        previous=0
        for path,turn in zip(paths,expected):
            data=read(path);assert data['turn']==turn,path
            assert (data['width'],data['height'])==(74,46),path
            assert not data['errors'],(path,data['errors'])
            assert len(data['events'])>=previous,path;previous=len(data['events'])
            if turn==1:assert len(data['players'])==6,path
            for city in data['cities']:
                for d in city['districts']:
                    if not d.get('quarter'):continue
                    site=d['site']
                    for cat in ('base','spec'):
                        owned=[m for m in site['materials'] if m['owner']==city['player'] and m['category']==cat]
                        assert len(owned)==site[cat],(path,d,cat)
                        assert sum(bool(m.get('improvement')) and not m['pillaged'] for m in owned)==site[cat+'_improved'],(path,d,cat)
            result['snapshot_count']+=1
        save=read(folder/'save.json');copied=folder/Path(save['path']).name
        assert copied.stat().st_size>0 and sha(copied)==save['sha256'],folder
        game=int(folder.name.split('-')[1]);scripts=sorted((a.output/'commands').glob(f'*-observer-{game}.lua'))
        assert scripts and scripts[-1].read_text(encoding='utf-8')==observer,('Observer differs',folder)
        if a.turn>200:
            continuation=read(a.output/'continuation.json');source=Path(continuation['source'])/folder.name
            assert read(folder/'reload-validation.json')['city_and_plot_state_identical'],folder
            prefix=read(source/'turn-200.json')['events']
            before=read(source/'turn-200.json');reloaded=read(folder/'reload-turn-200.json')
            assert before['players']==reloaded['players'],('Research or roster changed on load',folder)
            def properties(s):return sorted((c['player'],c['id'],sorted(c['properties'].items())) for c in s['cities'])
            assert properties(before)==properties(reloaded),('Service properties changed on load',folder)
            for path in paths:
                turn=int(path.stem.split('-')[1])
                if turn<=200:assert sha(path)==sha(source/path.name),('Original snapshot altered',path)
                else:assert read(path)['events'][:len(prefix)]==prefix,('Event prefix altered',path)
        sql_errors=[line for line in (folder/'logs/Database.log').read_text(encoding='utf-8',errors='replace').splitlines() if '[Gameplay]' in line and 'ERROR' in line]
        assert not sql_errors,(folder,sql_errors)
        assert read(folder/'complete.json')['turn']==a.turn,folder
        result['games'].append({'game':game,'turn':a.turn,'snapshots':len(paths),'checkpoint_turns':expected,'save_sha256':save['sha256'],'observer_sha256':sha(scripts[-1]),'gameplay_sql_errors':0})
    installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    hashes=read(a.output/'installed-gameplay-hashes.json')
    changes=[relative for relative,digest in hashes.items() if not (installed/relative).exists() or sha(installed/relative)!=digest]
    assert not changes,('Installed gameplay changed',changes)
    result['installed_files_verified']=len(hashes)
    (a.output/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(folders)} completed games, {result["snapshot_count"]} snapshots, verified saves, unchanged {len(hashes)} installed files, zero recorder/gameplay SQL errors')

if __name__=='__main__':main()
