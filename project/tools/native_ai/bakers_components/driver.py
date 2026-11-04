"""One archived weak-Bakers save, one ordinary turn, read-only native components.

No native work on import. Shared controller owns all game actions. This is not
a policy trial: no CE, score writer, order, grant, queue edit or new world.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'project/tools/ai_baseline'), str(HERE.parent)]
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory
from full_game_controller.environment import (launch, configure, flags, manifest,
    restore_preferences, write_json, archive_sources)
from observer_host import prove_loaded_module

SAVE_SHA = '6569b8b97489c558212e361772f126ae8c04c054983e83ce88409d8716a65a7c'
GAME_SHA = '324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
CSC = 'c5e66bd1-d804-443b-ac3d-1917a20dba3c'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_world(raw):
    rows = re.findall(r'CSC_BAKERS_COMPONENT_WORLD=([^\r\n]+)', raw)
    if len(rows) != 1:
        raise ValueError('Missing/ambiguous component world receipt')
    return json.loads(rows[0])


def validate_world(value, turn):
    if value['turn'] != turn:
        raise ValueError('Wrong observed turn')
    mapping = value['mapping']
    if not mapping['buildingsDense'] or not mapping['districtsDense']:
        raise ValueError('Sparse definition indices need a reviewed binding')
    targets = value['targets']
    if {(row['player'], row['city']) for row in targets} != {(5, 65536), (3, 65536)}:
        raise ValueError('Wrong historical city scope')
    for row in targets:
        if not row.get('exists'):
            raise ValueError('Historical city missing')
    if turn == 80 and not value['sourceValidation']['valid']:
        raise ValueError('Historical AI/city/site identity gate failed; no fixture repair')
    return True


def run(a):
    out = a.output.resolve()
    if out.exists() or native_inventory():
        raise RuntimeError('Fresh output and no existing native/Tuner owner required')
    if sha(a.save) != SAVE_SHA or sha(a.dll) != GAME_SHA:
        raise ValueError('Wrong archived source or native build')
    out.mkdir(parents=True)
    roots = [a.installed, a.stock_ce]
    before = {str(p.resolve()): manifest(p) for p in roots}
    sources = [HERE / 'driver.py', HERE / 'observer.js', HERE / 'world.lua']
    sources += list((ROOT / 'project/tools/ai_baseline/full_game_controller').glob('*.py'))
    sources += list((ROOT / 'project/tools/ai_baseline/full_game_controller').glob('*.lua'))
    sources += [HERE.parent / 'observer_host.py']
    pins = {str(p.resolve()): sha(p) for p in sources}
    write_json(out / 'source-pins.json', pins)
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    write_json(out / 'installed-before.json', before)
    write_json(out / 'protocol.json', dict(start=80, endpoint=81, maximum=81,
        source_sha256=SAVE_SHA, speed='GAMESPEED_ONLINE', fresh_worlds=0, loads=1,
        policy='none', CE=False, frida='read-only component observer',
        native_calls=False, native_orders_or_grants=False, matched_historical_totals=False,
        goal='attribute future building inputs and generated adjacency modifier forecasts'))
    controller = make_probe_controller(out, user_root=a.user_root)
    controller.study_endpoint = 81
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    trace_session = script = None
    failure = None
    turn = None
    frozen = False
    script_loaded = False
    init_attempted = False
    observations = []

    def verify():
        if any(sha(p) != value for p, value in pins.items()):
            raise RuntimeError('Executed source changed')
        if any(manifest(p) != before[str(p.resolve())] for p in roots):
            raise RuntimeError('Installed source changed')

    def world(label):
        raw = controller.cmd((HERE / 'world.lua').read_text(encoding='utf-8-sig'),
            'GameCore_Tuner', label, wait=20)
        value = parse_world(raw)
        write_json(out / (label + '.json'), value)
        observations.append(value)
        return value

    def validate_source():
        nonlocal turn
        turn = 80
        controller.cmd("assert(Game.GetCurrentGameTurn()==80);assert(Players[0]:IsHuman());assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT==nil and GameInfo.CSC_AI_Profile==nil,'Legacy tuning loaded');assert(GameConfiguration.GetGameSpeedType()=='GAMESPEED_ONLINE' or GameInfo.GameSpeeds[GameConfiguration.GetGameSpeedType()].GameSpeedType=='GAMESPEED_ONLINE');", 'GameCore_Tuner', 'source-gates')
        value = world('source-world')
        validate_world(value, 80)
        return True

    def capture_logs(label):
        for name in ('Lua.log', 'Database.log', 'Modding.log', 'AI_CityBuild.csv', 'AI_Behavior_Trees.csv', 'City_BuildQueue.csv'):
            path = a.user_root / 'Logs' / name
            if path.is_file():
                target = out / 'logs' / label / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(path.read_bytes())

    def freeze():
        nonlocal frozen
        if script is None or frozen:
            return
        if not script_loaded or not init_attempted:
            # Script top level exports only; hooks install exclusively in init.
            write_json(out / 'trace-not-installed.json', dict(script_loaded=script_loaded,
                init_attempted=init_attempted, hook_initialization_never_called=True))
            frozen = True
            return
        status = script.exports_sync.status()
        if status['hooks'] == 0 and not status.get('started'):
            write_json(out / 'trace-not-installed.json', dict(status=status,
                zero_installed_hooks=True))
            frozen = True
            return
        value = script.exports_sync.freeze()
        write_json(out / 'trace-frozen.json', value)
        frozen = True
        capture_logs('frozen')
        # Retain all instrumentation/session references until exact native exit.

    try:
        verify()
        session.start(lambda: launch(a, out))
        session.wait_context('MainMenu')
        configure(controller, out, 'BASIC')
        selected = flags(controller, 'verify-CSC-only')
        if {key for key, value in selected['mods'].items() if value} != {CSC}:
            raise RuntimeError('Unexpected enabled mod set')
        session.load_once(a.save, sha256=SAVE_SHA, native_directory=a.save.parent,
            turn=80, contexts=('GameCore_Tuner', 'PlotInfo'), eligibility=validate_source)
        spec = json.loads(a.spec.read_text(encoding='utf-8-sig'))
        if spec['sha256'] != GAME_SHA or Path(spec['path']).resolve() != a.dll.resolve():
            raise ValueError('Observer spec target mismatch')
        prove_loaded_module(session.owner, spec, out / 'loaded-module.json')
        # Imported only after held process/module identity and source gates pass.
        sys.path.insert(0, str(a.dependencies.resolve()))
        import frida
        if frida.__version__ != '17.24.3' or not Path(frida.__file__).resolve().is_relative_to(a.dependencies.resolve()):
            raise RuntimeError('Require explicitly pinned Frida17.24.3')
        write_json(out / 'dependency-pins.json', manifest(a.dependencies))
        config = observations[0]['observerConfig']
        write_json(out / 'observer-config.json', config)
        source = (HERE / 'observer.js').read_text(encoding='utf-8-sig')
        trace_session = frida.attach(session.owner.pid)
        def detached(*details):
            write_json(out / 'frida-detached.json', dict(details=str(details),
                native_alive=session.owner.poll() is None, unix=time.time()))
        trace_session.on('detached', detached)
        script = trace_session.create_script(source)
        def message(value, data):
            with (out / 'frida-messages.ndjson').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(value) + '\n')
        script.on('message', message)
        script.load()
        script_loaded = True
        init_attempted = True
        write_json(out / 'trace-init.json', script.exports_sync.init(spec, config))
        status = script.exports_sync.status()
        write_json(out / 'trace-ready.json', status)
        script.exports_sync.start()
        controller.play(81)
        turn = 81
        validate_world(world('endpoint-world'), 81)
        write_json(out / 'trace-snapshot.json', script.exports_sync.snapshot())
        freeze()
        final = json.loads((out / 'trace-frozen.json').read_text(encoding='utf-8'))
        if final['stats']['errors'] or final['pendingFrames'] or final['pendingPairs']:
            raise RuntimeError('Component observation fault or incomplete pairs')
        if not final['records'] or final['stopReason']:
            raise RuntimeError('Component observation empty or budget-limited')
    except BaseException as error:
        failure = error
        write_json(out / 'failure.json', dict(error=str(error), traceback=traceback.format_exc(),
            turn=turn, no_automatic_replay=True))
    finally:
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda: restore_preferences(controller, out)
                    if (out / 'original-preferences.json').is_file() else None,
                    restore_package=verify, before_menu=freeze)
            except BaseException as error:
                failure = failure or error
                write_json(out / 'cleanup-failure.json', dict(error=str(error), traceback=traceback.format_exc()))
        # Never unwind Frida references while an owned process remains alive.
        if trace_session is not None and session.owner is not None and not session.closed:
            write_json(out / 'retained-observer-wait.json', dict(native_pid=session.owner.pid,
                reason='Cleanup incomplete; keep read-only hooks retained until native exit'))
            while session.owner.poll() is None:
                time.sleep(1)
        capture_logs('closed')
        write_json(out / 'final-inventory.json', native_inventory())
    result = dict(closed=session.closed, source_turn=80, endpoint=turn,
        requested_endpoint=81, error=str(failure) if failure else None,
        installed_unchanged=all(manifest(p) == before[str(p.resolve())] for p in roots),
        fresh_worlds=0, loads=1, policy='none', native_orders_or_grants=False,
        score_writes=False, explicit_frida_detach=False)
    write_json(out / 'result.json', result)
    print(json.dumps(result), flush=True)
    if failure:
        raise failure


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'binary', 'dll', 'user-root', 'installed', 'stock-ce', 'save', 'dependencies', 'spec'):
        parser.add_argument('--' + name, type=Path, required=True)
    run(parser.parse_args())
