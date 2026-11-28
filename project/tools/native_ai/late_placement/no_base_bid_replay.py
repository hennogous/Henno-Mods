"""Replay a recorded stock production bid twice, changing only one city's Quarter gate."""
import argparse
import csv
from pathlib import Path
import shutil
import time
from types import SimpleNamespace

from lightweight_guidance import (HERE, HeldProcess, NativeSession, launch, load, lua, make_probe_controller,
    native_inventory, replace, require, restore_preferences, select_stack, sha, verify_modules, write_json)


def run(study_root, evidence, arm, receipt, start, end, value):
    pins=load(study_root/'study.json')['pins']
    user=Path(pins['userdata'])
    saves=Path(pins['saves'])
    source=Path(receipt['archive'])
    require(sha(source)==receipt['sha256'],'Historical autosave changed')
    local=saves/f"CSC_GATE_{start}_{receipt['sha256'][:12]}.Civ6Save"
    require(not native_inventory() and not arm.exists(),'Game in use or replay already exists')
    if not local.exists():
        shutil.copy2(source,local)
    require(sha(local)==receipt['sha256'],'Load-menu checkpoint differs')
    arm.mkdir()
    pkg=pins['packages']['csc']
    connector=Path(pkg['path'])/'Data/CSC_Q_ALL_AI_Connectors.sql'
    original=connector.read_bytes()
    require(original==(HERE.parents[3]/'Civ Supply Chains/Data/CSC_Q_ALL_AI_Connectors.sql').read_bytes(),
            'Installed connector differs from release')
    trial=original+b'\n'+(HERE/'no_base_city_rules.sql').read_bytes()
    c=make_probe_controller(arm,user_root=user)
    c.study_endpoint=end
    c.observer_warning_senders=range(1,6)
    c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=True
    c.allow_observer_congress_review=c.allow_one_more_turn=True
    session=NativeSession(arm,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    target=f"local city=assert(CityManager.GetCity({int(evidence['player'])},{int(evidence['city'])}))\n"
    target+=f"assert(city:GetName()=={lua(evidence['name'])});local key={lua('CSC_AI_NO_BASE_'+evidence['district'])}\n"
    target+="local center=Map.GetPlot(city:GetX(),city:GetY())\n"
    entry=Path(pkg['path'])/'Lua_UI/AI/CSC_AI_BakersGameplay.lua'
    original_entry=entry.read_bytes()
    require(original_entry==(HERE.parents[3]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_BakersGameplay.lua').read_bytes(),
            'Installed gameplay entry differs from release')
    # This autosave resumes with every seat under AI control. Install during
    # gameplay initialization in both arms, before the observer can attach.
    # Let the resumed game progress naturally. Transferring a seat changes
    # the game clock and can alter the very AI choice under investigation.
    setup=("do\n"+target+f"""
assert(city:GetProperty(key..'_REASON')=='absent' and (center:GetProperty(key) or 0)==0)
assert(city:GetProperty(key..'_BOUND')~=1)
for terrain in GameInfo.Terrains() do city:AttachModifierByID(key..'__'..terrain.TerrainType) end
center:SetProperty(key,{value})
print('CSC_GATE_FIXED',Game.GetCurrentGameTurn(),city:GetName(),center:GetProperty(key))
end
""").encode()+original_entry.decode('utf-8-sig').encode()
    try:
        replace(connector,trial)
        replace(entry,setup)
        session.start(lambda:launch(SimpleNamespace(binary=Path(pins['binary'])),arm))
        session.wait_context('MainMenu')
        select_stack(session,arm,[pkg['id']])
        session.issue_load_once(local,sha256=receipt['sha256'],native_directory=saves,turn=start)
        session.wait_context('GameCore_Tuner')
        verify_modules(session,None,arm,pins['core_sha256'])
        deadline=time.monotonic()+180
        while time.monotonic()<deadline:
            row=c.state_read('observe-resumed-clock')
            if row['turn']>=end:
                break
            if row['player0_human'] and not row['active'] and row['local_player']==0:
                c.ready(row['turn'],'named-handoff')
                c.play(min(end,row['turn']+3))
            else:
                time.sleep(3)
        else:
            raise TimeoutError('Resumed game did not reach the decision window')
        lines=(user/'Logs/Lua.log').read_text(errors='replace').splitlines()
        marks=[s.split('CSC_GATE_FIXED\t',1)[1].split('\t') for s in lines if 'CSC_GATE_FIXED\t' in s]
        require(len(marks)==1 and marks[0][1:]==[evidence['name'],str(value)]
                and int(marks[0][0])<evidence['turn'],'Missing pre-decision city gate: '+repr(marks))
        boundary=dict(source=receipt['sha256'],turn=int(marks[0][0]))
        if value:
            require(boundary==load(arm.parent/'replay-control'/'boundary.json'),'Replay handoffs differ')
        write_json(arm/'boundary.json',boundary)
    finally:
        try:
            if session.owner is not None and session.owner.poll() is None:
                session.close(restore_preferences=lambda:restore_preferences(c,arm)
                              if (arm/'original-preferences.json').exists() else None)
        finally:
            if not native_inventory():
                require(connector.read_bytes() in (original,trial),'Installed connector changed during replay')
                require(entry.read_bytes() in (original_entry,setup),'Concurrent gameplay edit')
                replace(entry,original_entry)
                replace(connector,original)
            if session.closed:
                for name in ('AI_CityBuild.csv','City_BuildQueue.csv'):
                    log=user/'Logs'/name
                    if log.is_file():
                        shutil.copy2(log,arm/name)
    with (arm/'AI_CityBuild.csv').open(encoding='utf-8-sig',errors='replace') as stream:
        rows=[r for r in csv.reader(stream,skipinitialspace=True) if len(r)>=7 and r[0].isdigit()
              and start<=int(r[0])<=end and r[1]==str(evidence['player']) and r[2]==evidence['name']]
    write_json(arm/'decision.json',dict(source=receipt['sha256'],start=start,end=end,gate=value,rows=rows))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',type=Path)
    parser.add_argument('case',type=Path)
    args=parser.parse_args()
    require(args.case.resolve().is_relative_to(args.study.resolve()),'Case must belong to the selected study')
    case=load(args.case)
    # Start before the submission, after the opportunity was classified.
    options=[r for r in case['autosaves'] if r['status']=='archived' and case['review'][0]<r['turn']<case['turn']]
    require(bool(options),'No checkpoint predates the bid and contains its previous city review')
    receipt=min(options,key=lambda r:r['turn'])
    for name,value in [('control',0),('penalty',1)]:
        arm=args.case.parent/('replay-'+name)
        if arm.exists() and not (arm/'decision.json').is_file():
            # Retain failed attempts, including launch and restoration receipts.
            arm.rename(arm.with_name(arm.name+'-attempt-'+str(len(list(arm.parent.glob(arm.name+'-attempt-*')))+1)))
        if not arm.exists():
            run(args.study,case,arm,receipt,receipt['turn'],case['turn']+4,value)
        result=load(arm/'decision.json')
        require(result['source']==receipt['sha256'] and result['gate']==value,
                'Completed branch belongs to a different comparison')


if __name__=='__main__':
    main()
