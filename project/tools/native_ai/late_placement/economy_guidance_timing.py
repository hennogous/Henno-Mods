"""Queue the matched Large/Standard CSC + City Lights guidance timing pair."""

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import shutil
from statistics import mean
import subprocess
import xml.etree.ElementTree as ET

from ce_bakers_fresh import check_native_status, package_identity, untuned_manifest
from customer_adjacency_policy import database_snapshot, qualify_database
from driver import HeldProcess, load, native_inventory, parse, read, require, sha, write_json
from economy_factorial import plan, play, verify_pins
from processing_time_summary import summarise


def verify_guidance(c, user, out, enabled, phase):
    if phase=='opening':
        database=database_snapshot(user/'Cache/DebugGameplay.sqlite')
        if enabled:
            qualify_database(database,'on')
        else:
            require(not any(database[key] for key in ('links','rules','yields','biases')),
                    'Control has active CSC native SQL guidance')
        write_json(out/'guidance-sql.json',database)
    raw=c.cmd("print('CSC_GUIDANCE_STATUS='..CE_AIDistrictScoresStatus())",'GameCore_Tuner',f'verify-guidance-{phase}')
    status=parse(raw,'CSC_GUIDANCE_STATUS')
    check_native_status(status,not enabled)
    write_json(out/f'guidance-{phase}.json',status)


def install_clocks(c):
    # Read the same native monotonic clock in both arms, at the Core turn
    # boundary. UI callbacks only record presentation so the report can screen
    # affected turns without losing ordinary engine or guidance work.
    raw=c.cmd('''
local now=assert(CE_AIMonotonicSeconds)
assert(type(now())=='number')
local last=-1
GameEvents.OnGameTurnStarted.Add(function()
    local turn=Game.GetCurrentGameTurn()
    if turn==last then return end
    last=turn
    print(string.format('CSC_GUIDANCE_CLOCK %d %.6f',turn,now()))
end)
print('CSC_GUIDANCE_CORE_CLOCK_READY')
''','GameCore_Tuner','install-guidance-core-clock')
    require('CSC_GUIDANCE_CORE_CLOCK_READY' in raw,'Core clock registration failed')
    raw=c.cmd('''
local names={'NaturalDisasterPopup_Shown','NaturalDisasterPopup_Closed',
    'NaturalWonderPopup_Shown','NaturalWonderPopup_Closed','WonderBuiltPopup_Shown','WonderBuiltPopup_Closed',
    'ProjectBuiltPopup_Shown','ProjectBuiltPopup_Closed','DiplomacyActionView_HideIngameUI',
    'DiplomacyActionView_ShowIngameUI','DiplomacyActionView_ShowCongressResults',
    'WorldCongressPopup_ShowWorldCongressBetweenTurns','EraReviewPopup_Show','EndGameMenu_Shown',
    'EndGameMenu_Closed','RockBandMoviePopup_Shown','RockBandMoviePopup_Closed'}
for _,name in ipairs(names) do
    local signal=name
    LuaEvents[signal].Add(function()
        print('CSC_GUIDANCE_POPUP',Game.GetCurrentGameTurn(),signal)
    end)
end
print('CSC_GUIDANCE_POPUP_CLOCK_READY')
''','PlotInfo','install-passive-guidance-popup-receipts')
    require('CSC_GUIDANCE_POPUP_CLOCK_READY' in raw,'Popup logging registration failed')


def observed_turns(out,endpoint):
    log=read(out/'Lua.log')
    marks={}
    for row in re.finditer(r'CSC_GUIDANCE_CLOCK\s+(\d+)\s+([\d.]+)',log):
        turn, now=int(row[1]),float(row[2])
        require(turn not in marks and math.isfinite(now),'Ambiguous Core turn clock')
        marks[turn]=now
    require(set(range(2,endpoint+1)) <= marks.keys(),'Missing Core turn clock')
    excluded={}
    def exclude(turn, reason):
        excluded.setdefault(turn,set()).add(reason)

    for row in re.finditer(r'CSC_GUIDANCE_POPUP\s+(\d+)\s+(\w+)',log):
        # The UI can observe the old turn while Core has moved one clock.
        # Exclude both possible intervals rather than estimate delay length.
        for turn in (int(row[1]),int(row[1])+1):
            exclude(turn,row[2])
    for folder in ('blocker-diagnostics','session-dismissals','congress-reviews',
                   'endgame-continuations','natural-wonder-recoveries','project-built-recoveries'):
        for file in (out/folder).glob('*.json'):
            evidence=load(file)
            core=evidence.get('core') or evidence.get('core_proof') or {}
            visible=evidence.get('native',{}).get('hidden') is False
            if 'turn' in core and (visible or evidence.get('requested') or evidence.get('cancelled_observer_conversation')):
                exclude(core['turn'],folder)
    releases=out/'playback-recoveries.ndjson'
    if releases.is_file():
        for line in read(releases).splitlines():
            row=json.loads(line)
            if row['requested']:
                exclude(row['core_proof']['turn'],row['context'])
    # Every multiple of five hands control back to the controller. Its gap
    # includes polling and reactivation, so use intervals inside each window.
    valid={t:marks[t+1]-marks[t] for t in range(2,endpoint) if t%5!=0 and t not in excluded}
    require(valid and all(v>0 for v in valid.values()),'Missing or invalid clean turn intervals')
    return valid,excluded,summarise(log,last=endpoint)


def compare_timings(out, games,endpoint):
    controls={name:observed_turns(Path(row['evidence']),endpoint) for name,row in games.items()}
    common=sorted(set.intersection(*(set(x[0]) for x in controls.values())))
    require(common,'No shared popup-free turn sample')
    report={}
    for name,(turns,excluded,guidance) in controls.items():
        measured={turn:turns[turn] for turn in common}
        peak=max(measured,key=measured.get)
        report[name]=dict(mean_seconds=mean(measured.values()),max_seconds=measured[peak],max_turn=peak,
            clean_seconds_by_turn=measured,excluded_popup_turns={key:sorted(v) for key,v in sorted(excluded.items())},
            direct_guidance=guidance['publisher_wall'],**games[name])
    write_json(out/'comparison.json',dict(endpoint=endpoint,shared_clean_turns=common,arms=report,
        method='Core turn-start intervals, excluding handoffs and observed popup turns in either game'))


def wait_for_worker(pid, predecessor):
    command=(f"Get-CimInstance Win32_Process -Filter 'ProcessId={int(pid)}' | "
             "Select-Object Name,CommandLine | ConvertTo-Json -Compress")
    raw=subprocess.check_output(['powershell','-NoProfile','-Command',command],text=True,
                                creationflags=subprocess.CREATE_NO_WINDOW).strip()
    if not raw:
        return
    row=json.loads(raw)
    require(row['Name'].lower()=='python.exe' and 'economy_factorial.py' in row['CommandLine']
            and str(predecessor).casefold() in row['CommandLine'].casefold(),'Unexpected predecessor process')
    owner=HeldProcess(pid)
    try:
        require(owner.kernel.WaitForSingleObject(owner.handle,0xFFFFFFFF)==0,'Could not wait for the benchmark worker')
    finally:
        owner.close()


def run(reference,out,predecessor,pid,seed,*,endpoint=500,preflight=False,resume_queue=False,resume_game=False):
    interrupted=load(out/'planned-inputs.json') if resume_game else None
    pins=interrupted['pins'] if interrupted else plan(reference)
    leaders=list(dict.fromkeys(leader for game in pins['seeds'].values() for leader in game['roster'].values()))[:10]
    require(len(leaders)==10,'The Large roster needs ten distinct leaders')
    require(endpoint in (250,500),'Unsupported performance endpoint')
    game=dict(game_seed=seed+1,roster=dict(enumerate(leaders)),size='large',speed='standard',endpoint=endpoint)
    installed=Path(pins['packages']['csc']['path'])
    metadata,=installed.glob('*.modinfo')
    original=(out/'csc-original.modinfo').read_bytes() if interrupted else metadata.read_bytes()
    disabled=untuned_manifest(ET.fromstring(original) if interrupted else package_identity(installed)[1])
    require(original!=disabled,'No control mask generated')
    if preflight:
        print(seed,game,'Control masks exactly the CSC publisher and native SQL action')
        return
    receipt=dict(seed=seed,game=game,pins=pins,predecessor=str(predecessor),pid=pid,
        control_manifest_sha256=sha256(disabled).hexdigest())
    if resume_game:
        require(interrupted==json.loads(json.dumps(receipt)),'Interrupted run differs from the queued setup')
    elif resume_queue:
        require(not (out/'off').exists() and not (out/'on').exists()
                and load(out/'planned-inputs.json')==json.loads(json.dumps(receipt))
                and (out/'csc-original.modinfo').read_bytes()==original,'Existing queue no longer matches the unstarted plan')
    else:
        out.mkdir(parents=True)
        write_json(out/'planned-inputs.json',receipt)
        (out/'csc-original.modinfo').write_bytes(original)
    wait_for_worker(pid,predecessor)
    require(not native_inventory(),'Another Civ or FireTuner session is present')
    relative=str(metadata.relative_to(installed))
    ci=pins['packages']['csc']
    control_pin=dict(pins,packages=dict(pins['packages'],csc=dict(ci,files={**ci['files'],
        relative:dict(sha256=sha256(disabled).hexdigest(),size=len(disabled))})))

    def stage(payload):
        temp=metadata.with_name(metadata.name+'.csc-timing-arm')
        with temp.open('xb') as file:
            file.write(payload)
        temp.replace(metadata)

    current=metadata.read_bytes()
    require(current in (original,disabled),'Unexpected installed CSC manifest')
    verify_pins(control_pin if current==disabled else pins)
    completed=out/'completed-runs.json'
    games=load(completed) if interrupted and completed.is_file() else {}

    def play_arm(arm, arm_pins):
        previous=sorted((entry for entry in out.iterdir() if entry.is_dir() and
                         (entry.name==arm or entry.name.startswith(arm+'-retry-'))),key=lambda d:d.stat().st_mtime_ns)
        recovery=previous[-1] if previous else None
        if recovery:
            pending=not (recovery/'session-closed.json').exists()
            source=Path(pins['userdata'])/'Logs/Lua.log'
            preserved=recovery/'Lua.interrupted.log'
            if pending and source.is_file() and not preserved.exists():
                shutil.copyfile(source,preserved)
        destination=out/(f'{arm}-retry-{len(previous)}' if previous else arm)
        result=play(arm_pins,seed,game,'combined',destination,recovery=recovery,guidance=arm=='on')
        games[arm]=result
        write_json(completed,games)

    if 'off' not in games:
        if current==original:
            stage(disabled)
        try:
            play_arm('off',control_pin)
        finally:
            require(not native_inventory() and sha(metadata)==sha256(disabled).hexdigest(),
                    'Keep the control manifest until the game and package can be reconciled')
            stage(original)
            verify_pins(pins)
    elif current==disabled:
        stage(original)
        verify_pins(pins)
    if 'on' not in games:
        play_arm('on',pins)
    require(load(Path(games['off']['evidence'])/'source.json')==load(Path(games['on']['evidence'])/'source.json'),
            'Matched openings differ')
    compare_timings(out,games,endpoint)
    print('Both Large Standard guidance endpoints verified',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('reference','output','predecessor'):
        parser.add_argument(name,type=Path)
    parser.add_argument('pid',type=int)
    parser.add_argument('seed',type=int)
    parser.add_argument('--through',type=int,default=500)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--resume-queue',action='store_true')
    parser.add_argument('--resume-game',action='store_true')
    a=parser.parse_args()
    run(a.reference.resolve(),a.output.resolve(),a.predecessor.resolve(),a.pid,a.seed,
        endpoint=a.through,preflight=a.preflight,resume_queue=a.resume_queue,resume_game=a.resume_game)
