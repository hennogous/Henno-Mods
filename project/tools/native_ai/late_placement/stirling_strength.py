"""Replay one city's existing desert signal from an identical saved position at three strengths."""
import argparse
import csv
import hashlib
from pathlib import Path
import shutil
from types import SimpleNamespace

from lightweight_guidance import (HERE, HeldProcess, NativeSession, launch, load, make_probe_controller,
    native_inventory, read, relief_sql, replace, require, restore_preferences, select_stack, sha,
    verify_modules, write_json)


GATE = 'CSC_AI_PAIR_DISTRICT_CSC_TAILORS_QUARTER__R_TERRAIN_DESERT'
EXTRA = 'CSC_STIRLING_DIAGNOSTIC_DESERT'


def city_rows(path, column):
    with path.open(encoding='utf-8-sig', errors='replace') as stream:
        return [r for r in csv.reader(stream, skipinitialspace=True)
                if len(r)>column and r[column]=='LOC_CITY_NAME_STIRLING']


def replay(study, saved, out, weight, end):
    pins = load(study/'study.json')['pins']
    checkpoint, protocol = load(saved/'checkpoint.json'), load(saved/'protocol.json')
    source = Path(checkpoint['native_save'])
    require(sha(source)==checkpoint['sha256'] and checkpoint['turn']==80,'Wrong Stirling checkpoint')
    require(not native_inventory() and not out.exists(),'Game in use or duplicate replay')
    pkg = pins['packages']['csc']
    install = Path(pkg['path'])
    connector = install/'Data/CSC_Q_ALL_AI_Connectors.sql'
    entry = install/'Lua_UI/AI/CSC_AI_BakersGameplay.lua'
    source_mod = HERE.parents[3]/'Civ Supply Chains'
    old_sql, old_entry = connector.read_bytes(), entry.read_bytes()
    for path in (connector,entry):
        require(path.read_bytes()==(source_mod/path.relative_to(install)).read_bytes(),'Release drift: '+str(path))
    sql = old_sql+b'\n'+(HERE/'no_base_city_rules.sql').read_bytes()+relief_sql(6)
    script = (saved/'local-gameplay.lua').read_bytes()
    require(hashlib.sha256(sql).hexdigest()==protocol['active_sha256'] and
            hashlib.sha256(script).hexdigest()==protocol['gameplay_sha256'],'Checkpoint treatment differs')
    # All arms define the same private modifier and attach it to Stirling only.
    # Its subject is the original desert property's requirement set, so the
    # extra weight disappears automatically as soon as the original cue ends.
    sql += f"""
INSERT INTO Modifiers(ModifierId,ModifierType,SubjectRequirementSetId)
SELECT '{EXTRA}',ModifierType,SubjectRequirementSetId FROM Modifiers WHERE ModifierId='{GATE}';
INSERT INTO ModifierArguments(ModifierId,Name,Value)
SELECT '{EXTRA}',Name,CASE WHEN Name='Amount' THEN {weight-6} ELSE Value END
FROM ModifierArguments WHERE ModifierId='{GATE}';
""".encode()
    out.mkdir()
    user = Path(pins['userdata'])
    c = make_probe_controller(out,user_root=user)
    c.study_endpoint=end
    c.observer_warning_senders=range(1,6)
    c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=True
    c.allow_observer_congress_review=c.allow_one_more_turn=True
    session=NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    try:
        replace(connector,sql)
        replace(entry,script)
        session.start(lambda:launch(SimpleNamespace(binary=Path(pins['binary'])),out))
        session.wait_context('MainMenu')
        select_stack(session,out,[pkg['id']])
        session.load_once(source,sha256=checkpoint['sha256'],native_directory=Path(pins['saves']),turn=80,
                          contexts=('PlotInfo','GameCore_Tuner','CSC_AI_BakersGameplay'),eligibility=lambda:True)
        verify_modules(session,None,out,pins['core_sha256'])
        raw=c.cmd(f"""local city=assert(CityManager.GetCity(5,65536))
assert(city:GetName()=='LOC_CITY_NAME_STIRLING')
city:AttachModifierByID('{EXTRA}')
print('CSC_STIRLING_ATTACHED',Game.GetCurrentGameTurn())""",'CSC_AI_BakersGameplay','apply-city-weight')
        require('CSC_STIRLING_ATTACHED\t80' in raw,'Treatment missed the shared boundary: '+raw[-300:])
        raw=c.cmd(read(HERE/'stirling_observer.lua'),'PlotInfo','observe-previews-and-eligibility')
        require('CSC_STIRLING_READY' in raw,'Preview reader failed: '+raw[-500:])
        for turn in range(85,end+1,5):
            c.play(turn)
    finally:
        try:
            if session.owner is not None and session.owner.poll() is None:
                session.close(restore_preferences=lambda:restore_preferences(c,out)
                              if (out/'original-preferences.json').exists() else None)
        finally:
            if not native_inventory():
                for path,original,trial in ((entry,old_entry,script),(connector,old_sql,sql)):
                    require(path.read_bytes() in (original,trial),'Concurrent edit: '+str(path))
                    replace(path,original)
            for name in ('AI_CityBuild.csv','City_BuildQueue.csv','Lua.log'):
                if (user/'Logs'/name).is_file():
                    shutil.copy2(user/'Logs'/name,out/name)
    with (out/'Lua.log').open(encoding='utf-8-sig',errors='replace') as stream:
        facts=[r.strip().split('CSC_STIRLING_',1)[1].split('\t') for r in stream if 'CSC_STIRLING_' in r]
    require(any(r[:2]==['PREVIEW','80'] and r[2]=='870' for r in facts),'Target missing at start')
    write_json(out/'decision.json',dict(source=checkpoint['sha256'],weight=weight,end=end,facts=facts,
        submissions=city_rows(out/'AI_CityBuild.csv',2),production=city_rows(out/'City_BuildQueue.csv',1)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',type=Path)
    parser.add_argument('saved',type=Path)
    parser.add_argument('--end',type=int,default=115)
    args=parser.parse_args()
    for strength in (6,9,12):
        out=args.saved.parent/f'stirling-weight-{strength}'
        if not (out/'decision.json').is_file():
            if out.exists():
                require((out/'session-closed.json').is_file() and not native_inventory(),
                        'Previous attempt still owns the game or lacks its closure receipt')
                # Preserve diagnostic failures separately. Never send another
                # launch while the previous session is alive.
                keep=next(i for i in range(1,100) if not out.with_name(f'{out.name}-attempt-{i}').exists())
                out.rename(out.with_name(f'{out.name}-attempt-{keep}'))
            replay(args.study,args.saved,out,strength,args.end)
