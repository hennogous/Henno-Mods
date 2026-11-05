"""Controlled Mill yields plus ordinary CSC building forecasts in one fresh world.

Only this host owns Tuner and native execution. Test fixtures deliberately grant
objects/unlocks in a disposable turn-1 world; the observer never changes scores.
After normal exit, a second process loads the exact save for read-only persistence
checks. This avoids carrying newly instrumented code across a live module reload.
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
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'project/tools/ai_baseline'), str(HERE.parent)]
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory
from full_game_controller.environment import (launch, configure, flags, manifest,
    restore_preferences, write_json, archive_sources)
from full_game_controller.checkpoint import save_inactive_boundary
from full_game_controller.log_capture import capture_log_baseline, read_log_delta
from full_game_controller.log_capture import LogGenerationChanged
from full_game_controller.transport import NativeLuaFailure
from observer_host import prove_loaded_module

GAME_SHA = '324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
GP = 'CSC_AdjacencyGameplay'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse(raw, marker):
    rows = re.findall(re.escape(marker) + r'=([^\r\n]+)', raw or '')
    chunks = [json.loads(v) for v in re.findall(re.escape(marker + '_CHUNK') + r'=([^\r\n]+)', raw or '')]
    if chunks:
        first = chunks[0]
        keys = ('schema', 'parts', 'bytes', 'sum32', 'encoding')
        if (rows or first['schema'] != 1 or first['encoding'] != 'hex'
                or type(first['parts']) is not int or not 1 <= first['parts'] <= 2048
                or type(first['bytes']) is not int or not 0 <= first['bytes'] <= 1024 * 1024
                or len(chunks) != first['parts']):
            raise ValueError('Invalid chunked receipt framing')
        for index, chunk in enumerate(chunks, 1):
            if chunk['part'] != index or any(chunk[k] != first[k] for k in keys):
                raise ValueError('Conflicting or out-of-order receipt chunk')
        payload = b''.join(bytes.fromhex(v['data']) for v in chunks)
        if len(payload) != first['bytes'] or sum(payload) % 2**32 != first['sum32']:
            raise ValueError('Chunked receipt length/checksum mismatch')
        return json.loads(payload.decode('utf-8'))
    if len(rows) != 1:
        raise ValueError('Missing or ambiguous receipt: ' + marker)
    return json.loads(rows[0])


def lua(value):
    """Encode only finite fixture facts; JSON Unicode escapes are not Lua 5.1."""
    if value is None:
        return 'nil'
    if type(value) is bool:
        return str(value).lower()
    if type(value) in (int, float):
        return json.dumps(value, allow_nan=False)
    if isinstance(value, str):
        if not value.isascii() or any(ord(c) < 32 or ord(c) == 127 for c in value):
            raise ValueError('Fixture bindings must be printable ASCII')
        return json.dumps(value)
    if isinstance(value, list):
        return '{' + ','.join(lua(v) for v in value) + '}'
    if isinstance(value, dict):
        return '{' + ','.join('[' + lua(k) + ']=' + lua(v) for k, v in value.items()) + '}'
    raise TypeError('Unsupported fixture binding')


def stable_sample(query, *, clock=time.monotonic, timeout=30, pause=time.sleep):
    """Accept two equal samples, then let the independent oracle judge them.

    We do not poll until a desired yield appears: an incorrect stable state must
    fail the contract. Every query/reply is archived by the shared controller.
    """
    end, previous = clock() + timeout, None
    while clock() < end:
        value = query()
        if clock() >= end:
            raise TimeoutError('Native sampling exceeded its settling deadline')
        current = json.dumps(value['facts'], sort_keys=True, allow_nan=False)
        if current == previous:
            return value
        previous = current
        pause(.25)  # Separate the read-only samples across normal game frames.
    raise TimeoutError('Native fixture facts did not stabilize')


def setup_game():
    return (HERE / 'game_setup.lua').read_text(encoding='utf-8-sig')


def finish_contract(case, finish, record):
    """Keep one known extra repair diagnostic from discarding the other probe.

    The expected +1 is never relaxed. A confirmed Quarter-repair yield failure
    is retained as a failed contract and a separately labeled record-only row.
    Transport ambiguity, other assertions and all other cases still stop.
    """
    try:
        return finish()
    except NativeLuaFailure as error:
        if case != 'repair-quarter' or 'repair-quarter native Production delta' not in str(error):
            raise
        value = record()
        value['contract_passed'] = False
        value['contract_failure'] = str(error)
        return value


def run(a):
    a.csc_id = str(uuid.UUID(a.csc_id))
    out = a.output.resolve()
    if out.exists() or native_inventory():
        raise RuntimeError('Fresh output and no existing game/Tuner owner required')
    if sha(a.dll) != GAME_SHA:
        raise ValueError('Wrong original XP2 binary')
    manifests = list(a.installed.glob('*.modinfo'))
    if len(manifests) != 1 or ET.parse(manifests[0]).getroot().get('id') != a.csc_id:
        raise ValueError('Selected CSC identity does not match its isolated package')
    spec = json.loads(a.spec.read_text(encoding='utf-8-sig'))
    if spec['sha256'] != GAME_SHA or Path(spec['path']).resolve() != a.dll.resolve():
        raise ValueError('Observer specification does not match the original binary')
    # The shared OS module verifier compares native Windows path strings. Keep
    # the guard exact while normalizing the caller's equivalent slash spelling.
    spec['path'] = str(a.dll.resolve())
    out.mkdir(parents=True)
    write_json(out / 'normalized-observer-spec.json', spec)
    roots = [a.installed, a.reference_csc, a.stock_ce]
    before = {str(p.resolve()): manifest(p) for p in roots}
    # Pin executed files, not the concurrently developed offline analyzer or its
    # tests. Their edits cannot alter the running native observation.
    sources = [HERE / name for name in ('driver.py', 'game_setup.lua', 'setup.lua',
        'fixture.lua', 'world.lua', 'observer.js')]
    sources += list((ROOT / 'project/tools/ai_baseline/full_game_controller').glob('*'))
    sources += [HERE.parent / 'observer_host.py', a.spec]
    pins = {str(p.resolve()): sha(p) for p in sources if p.is_file() and '__pycache__' not in p.parts}
    write_json(out / 'source-pins.json', pins)
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    write_json(out / 'content-before.json', before)
    write_json(out / 'protocol.json', dict(schema=1, fresh_worlds=1, processes=2,
        speed='GAMESPEED_ONLINE', endpoint=2, maximum=100, exact_save_loads=1,
        score_policy=False, CE=False, fixture_grants=True,
        observer='six read-only boundaries', economic_or_matched_history_claim=False))

    def verify():
        if any(sha(p) != digest for p, digest in pins.items()):
            raise RuntimeError('Pinned research source changed')
        if any(manifest(p) != before[str(p.resolve())] for p in roots):
            raise RuntimeError('Installed content changed')

    checkpoint = descriptor = bindings = None
    fixture_all_passed = True
    results = []
    for mode in ('probe', 'reload'):
        phase_out = out / mode
        phase_out.mkdir()
        c = make_probe_controller(phase_out, user_root=a.user_root)
        c.study_endpoint = 2
        c.allow_observer_warning_dismissal = c.allow_observer_first_meet_dismissal = True
        c.allow_observer_congress_review = True
        s = NativeSession(phase_out, c, inventory=native_inventory, hold=HeldProcess, write=write_json)
        observer_session = script = None
        init_attempted = frozen = False
        error, turn = None, None
        log_baselines = {}

        def logs(label):
            for name, baseline in log_baselines.items():
                path = a.user_root / 'Logs' / name
                if path.exists():
                    generation_changed = False
                    try:
                        current, delta = read_log_delta(path, baseline)
                    except LogGenerationChanged:
                        # Preserve a new generation without representing it as
                        # an extension of a prior file. This evidence issue must
                        # not overwrite the actual fixture/observer failure.
                        current, delta = capture_log_baseline(path), None
                        generation_changed = True
                    target = phase_out / 'logs' / label / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(current.data)
                    write_json(target.with_suffix(target.suffix + '.boundary.json'),
                        dict(initial=baseline.evidence(), current=current.evidence(),
                            generation_changed=generation_changed,
                            delta_bytes=len(delta) if delta is not None else None))

        def receipt(code, label, *, mutate=False, context=GP):
            raw = s.issue_once(label, code, context) if mutate else c.cmd(code, context, label, wait=20)
            return parse(raw, 'CSC_MILL_FIXTURE')

        def world(label):
            code = 'CSC_MILL_STUDY_CONFIG=' + lua(dict(targets=bindings['targets'])) + ';\n'
            raw = c.cmd(code + (HERE / 'world.lua').read_text(encoding='utf-8-sig'),
                        'GameCore_Tuner', label, wait=20)
            value = parse(raw, 'CSC_MILL_BUILDING_WORLD')
            write_json(phase_out / (label + '.json'), value)
            return value

        def eligibility():
            c.cmd('assert(Game.GetCurrentGameTurn()==' + str(turn) +
                ");assert(Players[0]:IsHuman());assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT==nil and GameInfo.CSC_AI_Profile==nil,'Legacy tuning loaded');assert(type(CE_AIDistrictScoresBegin)=='nil','No CE research carrier');assert(GameConfiguration.GetGameSpeedType()=='GAMESPEED_ONLINE' or GameInfo.GameSpeeds[GameConfiguration.GetGameSpeedType()].GameSpeedType=='GAMESPEED_ONLINE');",
                'GameCore_Tuner', mode + '-source-identity')
            return True

        def freeze():
            nonlocal frozen
            if frozen or script is None:
                return
            if not init_attempted:
                frozen = True
                return
            status = script.exports_sync.status()
            if status['hooks'] == 0:
                write_json(phase_out / 'trace-not-installed.json', status)
            else:
                value = script.exports_sync.freeze()
                write_json(phase_out / 'trace-frozen.json', value)
            frozen = True
            logs('frozen')

        try:
            verify()
            s.start(lambda: launch(a, phase_out))
            s.wait_context('MainMenu')
            configure(c, phase_out, 'BASIC', csc_id=a.csc_id)
            if {k for k, v in flags(c, mode + '-exclusive-content')['mods'].items() if v} != {a.csc_id}:
                raise RuntimeError('CSC-only selection not verified')
            # Launch can truncate the preceding process's logs. The meaningful
            # observation baseline belongs to this configured native session.
            log_baselines = {name: capture_log_baseline(a.user_root / 'Logs' / name)
                for name in ('Lua.log', 'Database.log', 'Modding.log', 'AI_CityBuild.csv', 'City_BuildQueue.csv')}
            turn = 1 if mode == 'probe' else 2
            contexts = ('GameCore_Tuner', 'PlotInfo', GP)
            if mode == 'probe':
                s.issue_once('host-study', setup_game(), 'MainMenu')
                s.ready_after_issue(turn, contexts, eligibility=eligibility)
                prove_loaded_module(s.owner, spec, phase_out / 'loaded-module-before-fixture.json')
                setup = 'CSC_MILL_STUDY_TOKEN=' + lua(uuid.uuid4().hex) + ';\n'
                raw = s.issue_once('fixture-setup', setup + (HERE / 'setup.lua').read_text(), GP)
                bindings = parse(raw, 'CSC_MILL_STUDY_SETUP')
                write_json(phase_out / 'fixture-bindings.json', bindings)
                if s.issue_once('define-fixture', (HERE / 'fixture.lua').read_text(), GP) is None:
                    raise RuntimeError('Unconfirmed fixture definition; no replay')
                receipt('CSC_MillFixture.Print(CSC_MillFixture.Prepare(' + lua(bindings['fixture']) + '))',
                        'prepare-fixture', mutate=True)
                cases = receipt('CSC_MillFixture.Print(CSC_MillFixture.Describe())', 'describe-fixture')['cases']
                accepted = []
                for case in cases:
                    verify()
                    ident = case['id']
                    arg = lua(ident)
                    receipt('CSC_MillFixture.Print(CSC_MillFixture.PrepareCase(' + arg + '))',
                            'prepare-' + ident, mutate=True)
                    stable_sample(lambda: receipt('CSC_MillFixture.Print(CSC_MillFixture.CaptureBaseline(' + arg + '))', 'baseline-' + ident))
                    receipt('CSC_MillFixture.Print(CSC_MillFixture.ApplyCase(' + arg + '))', 'apply-' + ident, mutate=True)
                    stable_sample(lambda: receipt('CSC_MillFixture.Print(CSC_MillFixture.Capture(' + arg + '))', 'observe-' + ident))
                    result = finish_contract(ident,
                        lambda: receipt('CSC_MillFixture.Print(CSC_MillFixture.FinishCase(' + arg + ",'assert-local-contract'))", 'finish-' + ident, mutate=True),
                        lambda: receipt('CSC_MillFixture.Print(CSC_MillFixture.FinishCase(' + arg + ",'record-only'))", 'record-failure-' + ident, mutate=True))
                    if result.get('contract_passed') is False:
                        fixture_all_passed = False
                    accepted.append(result)
                    write_json(phase_out / 'fixture-cases.json', accepted)
                    write_json(out / 'progress.json', dict(phase='fixture', completed_cases=len(accepted), turn=1))
                source = world('source-world')
                if not source['sourceValidation']['valid']:
                    raise RuntimeError('Controlled AI forecast source invalid')
                # Preserve the fully prepared source before attaching new
                # diagnostic hooks. A later probe correction can load this
                # exact world instead of repeating cities and all yield cases.
                descriptor = receipt('CSC_MillFixture.Print(CSC_MillFixture.Export())', 'export-source-fixture')
                write_json(out / 'source-fixture-descriptor.json', descriptor)
                source_checkpoint = save_inactive_boundary(c, turn=1, name='CSC_MILL_STUDY_SOURCE',
                    native_directory=a.save_directory, archive=out / 'checkpoints/source-1.Civ6Save')
                write_json(out / 'source-checkpoint.json', source_checkpoint)
                prove_loaded_module(s.owner, spec, phase_out / 'loaded-module.json')
                sys.path.insert(0, str(a.dependencies.resolve()))
                import frida
                if frida.__version__ != '17.24.3' or not Path(frida.__file__).resolve().is_relative_to(a.dependencies.resolve()):
                    raise RuntimeError('Require explicit Frida17.24.3 dependency')
                write_json(phase_out / 'dependency-pins.json', manifest(a.dependencies))
                observer_session = frida.attach(s.owner.pid)
                def on_detached(*details, owner_session=s, destination=phase_out):
                    # Bind this process, rather than the next loop's session.
                    alive = False if owner_session.closed else owner_session.owner.poll() is None
                    write_json(destination / 'frida-detached.json',
                        dict(details=str(details), native_alive=alive, unix=time.time()))
                observer_session.on('detached', on_detached)
                script = observer_session.create_script((HERE / 'observer.js').read_text())
                def on_message(value, data, destination=phase_out):
                    with (destination / 'frida-messages.ndjson').open('a', encoding='utf-8') as stream:
                        stream.write(json.dumps(value) + '\n')
                script.on('message', on_message)
                script.load()
                init_attempted = True
                write_json(phase_out / 'trace-init.json', script.exports_sync.init(spec, source['observerConfig']))
                status = script.exports_sync.status()
                if not status['installed'] or status['hooks'] != 6 or status['stats']['errors']:
                    raise RuntimeError('Observer installation unhealthy')
                write_json(phase_out / 'trace-ready.json', status)
                script.exports_sync.start()
                c.play(2)
                turn = 2
                freeze()
                trace = json.loads((phase_out / 'trace-frozen.json').read_text())
                if trace['stats']['errors'] or trace['pendingFrames'] or trace['pendingPairs'] or trace['stopReason'] or not trace['records']:
                    raise RuntimeError('Incomplete or faulted native observation')
                world('endpoint-world')
                descriptor = receipt('CSC_MillFixture.Print(CSC_MillFixture.Export())', 'export-fixture')
                write_json(out / 'fixture-save-descriptor.json', descriptor)
                checkpoint = save_inactive_boundary(c, turn=2, name='CSC_MILL_STUDY_2',
                    native_directory=a.save_directory, archive=out / 'checkpoints/turn-2.Civ6Save')
                write_json(out / 'checkpoint.json', checkpoint)
            else:
                source_save = Path(checkpoint['native_save'])
                s.load_once(source_save, sha256=checkpoint['sha256'], native_directory=source_save.parent,
                            turn=2, contexts=contexts, eligibility=eligibility)
                if s.issue_once('define-reload-reader', (HERE / 'fixture.lua').read_text(), GP) is None:
                    raise RuntimeError('Unconfirmed reload reader definition')
                value = receipt('CSC_MillFixture.Print(CSC_MillFixture.VerifyReload(' + lua(descriptor) + '))', 'verify-fixture-reload')
                write_json(phase_out / 'fixture-reload.json', value)
                prove_loaded_module(s.owner, spec, phase_out / 'loaded-module.json')
                world('reloaded-world')
            verify()
        except BaseException as failure:
            error = failure
            write_json(phase_out / 'failure.json', dict(error=str(failure), traceback=traceback.format_exc(),
                turn=turn, no_automatic_replay=True))
        finally:
            if s.owner is not None and s.owner.poll() is None:
                try:
                    s.close(restore_preferences=lambda: restore_preferences(c, phase_out)
                        if (phase_out / 'original-preferences.json').exists() else None,
                        restore_package=verify, before_menu=freeze)
                except BaseException as failure:
                    error = error or failure
                    write_json(phase_out / 'cleanup-failure.json', dict(error=str(failure), traceback=traceback.format_exc()))
            # Never release live patched-code owners after an incomplete close.
            if observer_session is not None and s.owner is not None and not s.closed:
                write_json(phase_out / 'retained-observer.json', dict(pid=s.owner.pid, reason='Preserve hooks until exact native exit'))
                while s.owner.poll() is None:
                    time.sleep(1)
            logs('closed')
            write_json(phase_out / 'final-inventory.json', native_inventory())
        result = dict(mode=mode, closed=s.closed, endpoint=turn, error=str(error) if error else None,
            mill_contracts_passed=fixture_all_passed,
            installed_unchanged=all(manifest(p) == before[str(p.resolve())] for p in roots))
        write_json(phase_out / 'result.json', result)
        results.append(result)
        write_json(out / 'result.json', dict(results=results,
            complete=len(results)==2 and not error and fixture_all_passed,
            observation_complete=len(results)==2 and not error,
            mill_contracts_passed=fixture_all_passed,
            fresh_worlds=1, exact_loads=1 if mode=='reload' else 0, score_writes=False, fixture_grants=True))
        if error:
            raise error
    print(json.dumps(dict(complete=fixture_all_passed, observation_complete=True, results=results)), flush=True)
    if not fixture_all_passed:
        raise RuntimeError('Quarter repair contract failed; independent observations and reload evidence retained')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'binary', 'dll', 'user-root', 'installed', 'reference-csc', 'stock-ce', 'save-directory', 'dependencies', 'spec'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--csc-id', required=True)
    run(p.parse_args())
