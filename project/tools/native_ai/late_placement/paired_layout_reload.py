"""Cold-load a measured endpoint and compare its centre switches and stock previews."""
import argparse
import hashlib
from pathlib import Path
from types import SimpleNamespace

from lightweight_guidance import (HERE, HeldProcess, NativeSession, launch, load, make_probe_controller,
    native_inventory, replace, require, restore_preferences, select_stack, sha, verify_modules, write_json)
from paired_material_preview import observe


def check(study, arm, out):
    pins=load(study/'study.json')['pins']
    protocol=load(arm/'protocol.json')
    checkpoint=load(arm/'checkpoint.json')
    turn=checkpoint['turn']
    filename=f'pair-preview-{turn}.json'
    before=load(arm/filename)
    pkg=pins['packages']['csc']
    install=Path(pkg['path'])
    require(protocol['paired_layout'] and sha(checkpoint['native_save'])==checkpoint['sha256'],
            'Changed endpoint or incorrect saved treatment')
    require(not native_inventory() and not out.exists(),'Game in use or output already exists')
    files={}
    for relative,receipt in [('Data/CSC_Q_ALL_AI_Connectors.sql','active_sha256'),
                             ('Lua_UI/AI/CSC_AI_BakersGameplay.lua','gameplay_sha256')]:
        path=install/relative
        original=path.read_bytes()
        require(original==(HERE.parents[3]/'Civ Supply Chains'/relative).read_bytes(),'Installed release differs')
        candidate=(original+b'\n'+(HERE/'paired_material_rules.sql').read_bytes()
                   if relative.endswith('.sql') else (arm/'local-gameplay.lua').read_bytes())
        require(hashlib.sha256(candidate).hexdigest()==protocol[receipt],'Candidate differs from saved game')
        files[path]=(original,candidate)
    out.mkdir()
    controller=make_probe_controller(out,user_root=Path(pins['userdata']))
    session=NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    try:
        for path,(_,candidate) in files.items():
            replace(path,candidate)
        session.start(lambda:launch(SimpleNamespace(binary=Path(pins['binary'])),out))
        session.wait_context('MainMenu')
        select_stack(session,out,[pkg['id']])
        session.load_once(checkpoint['native_save'],sha256=checkpoint['sha256'],native_directory=Path(pins['saves']),
                          turn=turn,contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),eligibility=lambda:True)
        verify_modules(session,None,out,pins['core_sha256'])
        observe(controller,out,turn)
        after=load(out/filename)
        fields=('city','player','district','plots','rules','on','off','restored','other_city')
        require(all(before[k]==after[k] for k in fields),'Active city rules or readbacks changed on cold load')
        write_json(out/'reload.json',dict(source=checkpoint['sha256'],turn=turn,fields=fields,equal=True))
    finally:
        try:
            if session.owner and session.owner.poll() is None:
                session.close(restore_preferences=lambda:restore_preferences(controller,out)
                              if (out/'original-preferences.json').exists() else None)
        finally:
            if not native_inventory():
                for path,(original,candidate) in files.items():
                    require(path.read_bytes() in (original,candidate),'Concurrent CSC edit')
                    replace(path,original)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for argument in ('study','arm','out'):
        parser.add_argument(argument,type=Path)
    args=parser.parse_args()
    check(args.study,args.arm,args.out)
