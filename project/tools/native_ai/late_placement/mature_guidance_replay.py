"""Replay a short timing window from the Large/Standard guidance benchmark.

Both arms use the same native save, installed CSC package and controller.
Only named AI modules can vary. Restore the user's pre-session Lua on exit.
"""
import argparse
from collections import Counter
import hashlib
from pathlib import Path
import re
import shutil
from statistics import mean
import subprocess
from types import SimpleNamespace

from ce_replay import DLL, verify_modules
from driver import (HeldProcess, NativeSession, ROOT, launch, load, make_probe_controller,
                    native_inventory, require, restore_preferences, sha, write_json)
from economy_factorial import select_stack, verify_pins
from economy_guidance_timing import install_clocks, observed_turns, verify_guidance


def replace(path, data):
    temp = path.with_suffix('.lua.csc-timing')
    with temp.open('xb') as f:
        f.write(data)
    temp.replace(path)


def benchmark_module(name,expected_hash):
    # The installed ModBuddy files had mixed LF and CRLF line endings. Take
    # the exact match to the original package manifest from the benchmark commit.
    raw=subprocess.check_output(['git','show','2573f6c9:Civ Supply Chains/Lua_UI/AI/'+name],cwd=ROOT)
    lf=raw.replace(b'\r\n',b'\n')
    for data in (raw,lf,lf.replace(b'\n',b'\r\n')):
        if hashlib.sha256(data).hexdigest()==expected_hash:
            return data
    raise ValueError('Benchmark commit differs from original package: '+name)


def run(source, out, candidate, turns):
    record = load(source/'on/checkpoint.json')
    pins = load(source/'planned-inputs.json')['pins']
    start = record['turn']
    require(turns >= 5 and turns % 5 == 0 and start % 5 == 0, 'Use whole five-turn controller windows')
    require(not native_inventory(), 'Another Civ or FireTuner session is active')
    require(sha(Path(record['archive'])) == record['sha256'], 'Archived checkpoint changed')
    out.mkdir(parents=True)
    ai = Path(pins['packages']['csc']['path'])/'Lua_UI/AI'
    source_ai = ROOT/'Civ Supply Chains/Lua_UI/AI'
    originals, arm = {}, {}
    for name in ('CSC_AI_EconomyAdapters.lua', 'CSC_AI_EconomyFacts.lua', 'CSC_AI_EconomyModel.lua',
                 'CSC_AI_BakersGameplay.lua'):
        originals[name] = (ai/name).read_bytes()
        stamp = pins['packages']['csc']['files'][str(Path('Lua_UI/AI')/name)]['sha256']
        arm[name] = (source_ai/name).read_bytes() if candidate else benchmark_module(name,stamp)
    write_json(out/'arm.json', dict(candidate=candidate, save=record['sha256'], start=start, turns=turns,
               files={name:hashlib.sha256(content).hexdigest() for name, content in arm.items()}))
    backup = out/'original-lua'
    backup.mkdir()
    for name,data in originals.items():
        (backup/name).write_bytes(data)
    user = Path(pins['userdata'])
    c = make_probe_controller(out,user_root=user)
    c.study_endpoint = start+turns
    c.observer_warning_senders = range(1,10)
    c.autoplay_interval_seconds = 2700
    c.allow_observer_warning_dismissal = c.allow_observer_first_meet_dismissal = True
    c.allow_observer_congress_review = c.allow_one_more_turn = True
    session = NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    changed = []
    try:
        for name,data in arm.items():
            if data != originals[name]:
                replace(ai/name,data)
                changed.append(name)
            pins['packages']['csc']['files'][str(Path('Lua_UI/AI')/name)] = dict(
                sha256=hashlib.sha256(data).hexdigest(),size=len(data))
        verify_pins(pins)
        session.start(lambda: launch(SimpleNamespace(binary=Path(pins['binary'])),out))
        session.wait_context('MainMenu')
        select_stack(session,out,load(source/'on/protocol.json')['packages'])
        def eligible():
            verify_guidance(c,user,out,True,'opening')
            return True
        session.load_once(record['native_save'],sha256=record['sha256'],native_directory=pins['saves'],
                          turn=start,contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),
                          eligibility=eligible,timeout=600)
        fork = Path(pins['packages']['ce']['path'])/'Binaries/Win64'/DLL
        verify_modules(session,fork,out,pins['core_sha256'])
        install_clocks(c)
        for end in range(start+5,c.study_endpoint+1,5):
            c.play(end)
        verify_guidance(c,user,out,True,'endpoint')
    finally:
        try:
            if session.owner is not None and session.owner.poll() is None:
                session.close(restore_preferences=lambda: restore_preferences(c,out)
                              if (out/'original-preferences.json').exists() else None,menu_timeout=600)
        finally:
            if not native_inventory():
                for name in changed:
                    require((ai/name).read_bytes()==arm[name], 'Installed Lua edited during replay: '+name)
                    replace(ai/name,originals[name])
    require(session.closed,'Replay did not close')
    shutil.copyfile(user/'Logs/Lua.log',out/'Lua.log')
    valid,excluded,guidance = observed_turns(out,start+turns,start+1)
    require(guidance['published_packets']==turns and guidance['failed_attempts']==0,'Incomplete policy publication')
    write_json(out/'measurements.json',dict(clean=valid,excluded={k:sorted(v) for k,v in excluded.items()},
                                          guidance=guidance))


def compare(control,candidate):
    arms = [load(path/'arm.json') for path in (control,candidate)]
    require(not arms[0]['candidate'] and arms[1]['candidate'] and
            all(arms[0][k]==arms[1][k] for k in ('save','start','turns')),'Mismatched replay inputs')
    measurements = [load(path/'measurements.json') for path in (control,candidate)]
    common = sorted(set(measurements[0]['clean']) & set(measurements[1]['clean']),key=int)
    require(common,'No shared clean intervals')
    report = dict(save=arms[0]['save'], clean_turns=list(map(int,common)))
    signatures = []
    tags=('QUARTER_WORLD','SPATIAL_BID','CUSTOMER_FUTURE_BID','CUSTOMER_PROSPECTIVE_BID',
          'CUSTOMER_ECONOMIC_BID','CONNECTION_COST','CONNECTION_PLAN','CONNECTION_COMPLETION')
    event=re.compile(r'\bCSC_AI_('+'|'.join(tags)+r') turn=(\d+) (.*)')
    for path, data, name in zip((control,candidate),measurements,('control','candidate')):
        seconds = [data['clean'][t] for t in common]
        direct = data['guidance']['publisher_wall']
        report[name]=dict(turn_mean_s=mean(seconds),turn_max_s=max(seconds),
                          publisher_mean_s=direct['average_ms']/1000,publisher_max_s=direct['max_ms']/1000,
                          publications=data['guidance']['published_packets'])
        # The ordinary log carries each site's economic forecast, projected
        # customer, placement bid and protection values. Compare multisets
        # so equal values on different sites or turns cannot match.
        rows = Counter()
        with (path/'Lua.log').open(encoding='utf-8-sig',errors='replace') as stream:
            for line in stream:
                record = event.search(line)
                if record and arms[0]['start']<int(record[2])<=arms[0]['start']+arms[0]['turns']:
                    rows[record.group().rstrip()]+=1
        signatures.append(rows)
    common_rows=signatures[0] & signatures[1]
    report['logged_policy']={}
    for tag in tags:
        report['logged_policy'][tag] = {
            name:sum(count for row,count in counts.items() if row.startswith('CSC_AI_'+tag+' '))
            for name,counts in zip(('control','candidate','identical'),(*signatures,common_rows))}
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--source',type=Path,help='Original turn-350 guidance benchmark directory')
    action.add_argument('--compare',nargs=2,type=Path,metavar=('CONTROL','CANDIDATE'))
    parser.add_argument('--out',type=Path,required=True,help='New arm directory, or comparison JSON file')
    parser.add_argument('--candidate',action='store_true')
    parser.add_argument('--turns',type=int,default=10)
    args=parser.parse_args()
    if args.compare:
        write_json(args.out,compare(*args.compare))
    else:
        run(args.source,args.out,args.candidate,args.turns)
