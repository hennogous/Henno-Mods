"""Integration checks for actual installed Lua, with explicit emulation limits."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time
from offline import OfflineWorld, read, write


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--map',type=Path,required=True)
    p.add_argument('--database',type=Path,required=True)
    p.add_argument('--game-root',type=Path,required=True)
    p.add_argument('--workshop-root',type=Path,required=True)
    p.add_argument('--lua-dependencies',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); native=read(a.map); before=hashlib.sha256(a.map.read_bytes()).hexdigest()
    checks=[]; summaries=[]
    def new(approximate=True):return OfflineWorld(native,a.database,a.game_root,a.workshop_root,12345,3,a.lua_dependencies,approximate)
    try:new(False)
    except RuntimeError as e:assert 'Native export lacks' in str(e);checks.append('incomplete native exports require explicit approximate flag')
    else:raise AssertionError('Expected rejection of incomplete export')
    for oceans in (False,True):
        worlds=[]
        for _ in range(2):
            started=time.monotonic();w=new();d=w.run('tar',6,oceans);worlds.append((w,d))
            summaries.append({'oceans':oceans,'seconds':round(time.monotonic()-started,3),'resources':dict(Counter(p.get('resource') for p in d['plots'] if p.get('resource'))),'kelp':sum(p.get('feature')=='FEATURE_SUK_KELP' for p in d['plots'])})
            assert all(p['terrain']==q['terrain'] and p['x']==q['x'] and p['y']==q['y'] and p['neighbors']==q['neighbors'] for p,q in zip(d['plots'],native['plots']))
            if not oceans:assert all(p.get('feature')==q.get('feature') for p,q in zip(d['plots'],native['plots']))
            for file,sha in w.sources.items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==sha
            assert len(d['plots'])==3404
            assert sum(bool(p.get('resource')) for p in d['plots'])>0
        assert worlds[0][1]==worlds[1][1],f'Non-repeatable emulation: Oceans={oceans}'
        checks.append(f'actual TAR Lua with Oceans={oceans}: deterministic, geometry preserved, sources unchanged')
        if oceans:
            assert summaries[-1]['kelp']>0
            assert any(k.startswith('RESOURCE_SUK_') for k in summaries[-1]['resources'])
            checks.append('actual Oceans SQL and Lua produce kelp and custom resources')
        else:
            other=new();d4=other.run('tar',4)
            assert d4['plots']!=worlds[0][1]['plots']
            checks.append('changing the luxury-type argument changes resource output')
    assert hashlib.sha256(a.map.read_bytes()).hexdigest()==before
    w=new();w.bootstrap()
    try:w.lua.execute('Fractal.Create()')
    except Exception as e:assert 'Native-only API unsupported offline' in str(e);checks.append('unsupported engine facility fails explicitly')
    else:raise AssertionError('Unsupported Fractal call succeeded')
    write(a.output,{'passed':True,'checks':checks,'runs':summaries,'native_parity_tested':False})
    print(json.dumps({'passed':True,'checks':len(checks),'runs':len(summaries)}))


if __name__=='__main__':main()
