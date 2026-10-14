"""Install CSC's built test package with a full recoverable backup first."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    installed=args.installed.resolve()
    package=args.output.resolve()/'package'/'Civ Supply Chains'
    backup=args.output.resolve()/'installed-mab-backed-backup'
    assert installed.name=='Civ Supply Chains' and installed.parent.name=='Mods'
    assert package.is_dir() and (package/'Civ Supply Chains.modinfo').is_file()
    assert not installed.is_relative_to(args.output.resolve())
    if not backup.exists(): shutil.copytree(installed,backup)
    for source in package.rglob('*'):
        target=installed/source.relative_to(package)
        if source.is_dir(): target.mkdir(parents=True,exist_ok=True); continue
        # Windows can memory-map Lua files held by another app. Identical files
        # need no replacement; skip them and verify every installed file below.
        if target.exists() and source.read_bytes()==target.read_bytes(): continue
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
    for source in package.rglob('*'):
        if source.is_file():
            target=installed/source.relative_to(package)
            assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(target.read_bytes()).digest(),target
    (args.output/'installation.json').write_text(json.dumps({'installed':str(installed),'backup':str(backup)},indent=2)+'\n',encoding='utf-8')
    print(f'Installed CSC test package; original preserved at {backup}')


if __name__=='__main__': main()
