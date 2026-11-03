"""Bounded zero-turn load/read/close exercise of the maintained shared session.

No new world, autoplay, DLL observer, treatment, installation or AI policy change.
The supplied read-only census must equal a declared complete reference. This is
a session integration test, not an AI intervention or a full-game validation.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'project/tools/ai_baseline'), str(ROOT/'project/tools/ai_tuning')]
from full_game_controller.probe import make_probe_controller, write_json
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory
from native_profile_test import configure, flags, manifest, restore_preferences
from native_probe_artifacts import archive_sources


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def launch(a, out):
    """One direct launch; allow only the reviewed exit53→fresh Steam successor."""
    directory = out/'sdk-working'
    directory.mkdir()
    (directory/'steam_appid.txt').write_text('289070\n', encoding='ascii')
    before = time.time()
    process = subprocess.Popen([str(a.binary)], cwd=directory, creationflags=subprocess.CREATE_NO_WINDOW)
    write_json(out/'launch-bootstrap.json',dict(pid=process.pid,binary=str(a.binary),time=before))
    time.sleep(2)
    if process.poll() is None:
        return HeldProcess.from_popen(process)
    write_json(out/'launch-bootstrap-exit.json',dict(pid=process.pid,exit_code=process.returncode))
    if process.returncode != 53:
        raise RuntimeError('Direct native bootstrap exited; no automatic relaunch')
    deadline = time.monotonic()+20
    while time.monotonic()<deadline:
        rows=native_inventory()
        if rows: break
        time.sleep(.5)
    if len(rows)!=1:
        raise RuntimeError('Steam successor missing or ambiguous; preserve owners')
    row=rows[0];identity=row['identity']
    if Path(identity['executable_path']).resolve()!=a.binary.resolve():
        raise RuntimeError('Unexpected Steam successor executable')
    created=identity['creation_filetime']/10_000_000-11644473600
    if not before-1<=created<=time.time():
        raise RuntimeError('Steam successor predates this launch')
    code="Get-Process -Id "+str(int(row['ParentProcessId']))+" -ErrorAction Stop | Select-Object ProcessName,Path | ConvertTo-Json -Compress"
    parent=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',code],text=True,creationflags=subprocess.CREATE_NO_WINDOW))
    if parent['ProcessName'].lower()!='steam':
        raise RuntimeError('Successor is not Steam-owned')
    held=HeldProcess(row['pid'])
    if held.identity!=identity:
        raise RuntimeError('Steam successor identity changed before hold')
    write_json(out/'launch-steam-successor.json',dict(identity=identity,parent=parent,bootstrap_exit=53))
    return held


def run(a, *, capture=None, extra_pins=()):
    out=a.output.resolve()
    if out.exists(): raise RuntimeError('Use a new output directory; never replay a partial session')
    if native_inventory(): raise RuntimeError('Native/Tuner/research owner present; preserve it')
    out.mkdir(parents=True)
    before=manifest(a.installed)
    if sha(a.source)!=a.sha256: raise RuntimeError('Source hash mismatch before launch')
    if a.source.resolve().parent!=a.native_directory.resolve(): raise RuntimeError('Unsupported save directory')
    reader=a.reader.read_text(encoding='utf-8')
    reference=json.loads(a.reference.read_text(encoding='utf-8-sig'))
    # Caller explicitly selects an entire exported Core census, not a field mask.
    if a.reference_key: reference=reference[a.reference_key]
    pins={str(p.resolve()):sha(p) for p in (a.binary,a.binary.parents[3]/'DLC/Expansion2/Binaries/Win64/GameCore_XP2_FinalRelease.dll',a.source,a.reader,a.reference,Path(__file__))}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).suffix=='.py' and Path(path).is_relative_to(ROOT/'project/tools'):
            pins[str(Path(path).resolve())]=sha(path)
    for path in (ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'):
        pins[str(path.resolve())]=sha(path)
    for path in a.rh_package.rglob('*'):
        if path.is_file(): pins[str(path.resolve())]=sha(path)
    for path in extra_pins: pins[str(Path(path).resolve())]=sha(path)
    write_json(out/'source-archive-scope.json',archive_sources(pins,out/'source-version'))
    write_json(out/'source-pins.json',pins)
    write_json(out/'installed-before.json',before)
    write_json(out/'contract.json',dict(turn=a.turn,AI_turns_authorized=0,worlds_authorized=0,
               instrumentation=False,policy_changes=False,reference=str(a.reference),
               reference_key=a.reference_key,source_sha256=a.sha256,profile=a.profile))
    r=make_probe_controller(out,user_root=getattr(a,'user_root',None))
    session=NativeSession(out,r,inventory=native_inventory,hold=HeldProcess,write=write_json)
    initial=None
    def verify_inputs():
        if manifest(a.installed)!=before: raise RuntimeError('Installed files changed; preserve edits')
        changed=[p for p,h in pins.items() if sha(p)!=h]
        if changed: raise RuntimeError('Executed/input pins changed: '+repr(changed))
    def census(label):
        raw=r.cmd(reader,'GameCore_Tuner',label,wait=25)
        value=json.loads(re.findall(re.escape(a.marker)+r'=([^\r\n]+)',raw)[-1])
        for key in ('players','cities','units'):
            value[key].sort(key=lambda v:(v.get('owner',-1),v['id']))
        write_json(out/(label+'.json'),value)
        return value
    def gate():
        nonlocal initial
        initial=census('initial-census')
        verify_inputs()
        if initial!=reference: raise RuntimeError('Complete declared source census mismatch; no rebase or AI')
        return True
    error=None
    try:
        verify_inputs()
        session.start(lambda:launch(a,out))
        session.wait_context('MainMenu')
        configure(r,out,a.profile)
        session.load_once(a.source,sha256=a.sha256,native_directory=a.native_directory,
                          turn=a.turn,contexts=('GameCore_Tuner','PlotInfo','CSC_AdjacencyGameplay'),eligibility=gate)
        if capture is not None: capture(r,out,'shadow-initial')
        r.ready(a.turn,'zero-turn-final-boundary')
        if capture is not None: capture(r,out,'shadow-final')
        final=census('final-census')
        if final!=initial: raise RuntimeError('Read-only interval changed exported state')
        write_json(out/'native-boundary-proof.json',dict(verified=True,turn=a.turn,
                   initial_and_final_census_equal=True,complete_reference_equal=True,AI_turns_advanced=0))
    except BaseException as failure:
        error=failure
        write_json(out/'failure.json',dict(error=str(failure),traceback=traceback.format_exc(),no_retry=True))
    finally:
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda:restore_preferences(r,out),restore_package=verify_inputs)
            except BaseException as failure:
                write_json(out/'cleanup-failure.json',dict(error=str(failure),traceback=traceback.format_exc(),original_error=str(error)))
                if error is None: error=failure
        verify_inputs()
        write_json(out/'final-inventory.json',native_inventory())
    if error is not None: raise error
    if not session.closed: raise RuntimeError('Shared session did not close')
    write_json(out/'result.json',dict(verified=True,AI_turns_advanced=0,new_worlds=0,
               exact_source_census=True,pins=len(pins),installed_files=len(before),
               installed_unchanged=True,preferences_restored=True,native_exit_code=0))
    print(json.dumps(json.loads((out/'result.json').read_text())))


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('output','binary','source','native-directory','installed','rh-package','reader','reference'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--sha256',required=True)
    p.add_argument('--turn',type=int,required=True)
    p.add_argument('--marker',default='NATIVE_PROBE_WORLD')
    p.add_argument('--reference-key',default='')
    p.add_argument('--profile',choices=('RH','BASIC'),default='RH')
    p.add_argument('--user-root',type=Path,help='Actual native user directory containing Logs; overrides LOCALAPPDATA')
    return p


def main():
    run(parser().parse_args())


if __name__=='__main__': main()

