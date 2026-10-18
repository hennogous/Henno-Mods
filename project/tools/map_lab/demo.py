"""Build native viewer plus a separate, labelled offline experiment viewer."""
import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from build import build, read, render, HERE


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--survey',type=Path,required=True)
    p.add_argument('--database',type=Path,required=True)
    p.add_argument('--game-root',type=Path,required=True)
    p.add_argument('--workshop-root',type=Path,required=True)
    p.add_argument('--lua-dependencies',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); viewer=build(a.survey,a.output)
    profile=a.output/'rules-profile.sqlite'
    src=sqlite3.connect(a.database.resolve().as_uri()+'?mode=ro',uri=True)
    dest=sqlite3.connect(profile);src.backup(dest);src.close();dest.close()
    maps=read(a.output/'maps.json');experiments=[]
    for luxury,oceans in [(4,False),(5,False),(6,False),(6,True)]:
        out=a.output/f'offline-tar-{luxury}{"-oceans" if oceans else ""}'
        cmd=[sys.executable,str(HERE/'offline.py'),'--map',str(a.survey/'vanilla-abundant/map-02/map.json'),
             '--database',str(profile),'--game-root',str(a.game_root),'--workshop-root',str(a.workshop_root),
             '--lua-dependencies',str(a.lua_dependencies),'--luxury-types',str(luxury),'--approximate','--output',str(out)]
        if oceans:cmd.append('--oceans')
        subprocess.run(cmd,check=True)
        experiments.append(read(out/'viewer-map.json'))
    (a.output/'experiments.json').write_text(json.dumps({'version':1,'maps':experiments},separators=(',',':')),encoding='utf-8')
    maps['maps'].extend(experiments)
    render(maps,a.output/'experiments.html')
    print(json.dumps({'native_viewer':str(viewer),'experiment_viewer':str(a.output/'experiments.html'),'native_maps':15,'offline_experiments':4}))


if __name__=='__main__':main()
