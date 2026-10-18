"""Repair map1's sparse edge enumeration using the identical native map2 grid."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    folder=a.output/'vanilla-abundant'/'map-01';path=folder/'map.json';backup=folder/'map-original-neighbor-enumeration.json'
    reference=a.output/'vanilla-abundant'/'map-02'/'map.json';original=read(path);canonical=read(reference)
    if backup.exists():print('Already normalized');return
    assert (original['width'],original['height'])==(canonical['width'],canonical['height'])==(74,46)
    canonical_grid={p['index']:p for p in canonical['plots']}
    changed=[]
    for plot in original['plots']:
        new=canonical_grid[plot['index']]
        assert (plot['x'],plot['y'])==(new['x'],new['y'])
        assert set(plot['neighbors'])<=set(new['neighbors'])
        if set(plot['neighbors'])!=set(new['neighbors']):changed.append(plot['index'])
        plot['neighbors']=new['neighbors']
    shutil.copy2(path,backup)
    original['neighbor_normalization']={'reason':'Initial ipairs export truncated sparse edge arrays','reference':str(reference),'method':'Native six-direction coordinate grid from the identical map script, dimensions and wrap settings','changed_plots':changed,'original_sha256':sha(backup)}
    path.write_text(json.dumps(original,indent=2)+'\n',encoding='utf-8')
    (folder/'neighbor-normalization.json').write_text(json.dumps(original['neighbor_normalization'],indent=2)+'\n',encoding='utf-8')
    print(f'Normalized{len(changed)} edge-neighbor lists; original observations retained')

if __name__=='__main__':main()
