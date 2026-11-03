"""No-adjustment four-interval control for the observed treatment turn stall.

Uses the maintained fresh trial helpers and unchanged shared controller. Import
performs no game action. This is not another baseline qualification or policy
search: the native mode is observation-only through the fixed turn254 endpoint.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'project/tools/ai_baseline'), str(HERE.parent)]
from quarter_placement_trial import driver as trial
from quarter_placement_trial.daemon import NativeExtension
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory
from full_game_controller.log_capture import capture_log_baseline, read_log_delta
from full_game_controller.environment import (launch, configure, manifest,
    restore_preferences, archive_sources, prove_loaded_module, write_json)
from full_game_controller.natural_wonder_guard import install as install_natural_wonder_guard


def visibility_lua(names):
    """One read-only query; names come exclusively from discovered UI states."""
    literals = ','.join(json.dumps(name) for name in names)
    return ('local names={' + literals + '};for _,name in ipairs(names)do '
        'local ok,c=pcall(function()return ContextPtr:LookUpControl("/InGame/"..name)end);'
        'local found=ok and c~=nil;local hiddenOk,hidden=false,nil;'
        'if found then hiddenOk,hidden=pcall(function()return c:IsHidden()end)end;'
        'print("CSC_CONTROL_UI_VISIBILITY",name,tostring(ok),tostring(found),tostring(hiddenOk),tostring(hidden));'
        'end;print("CSC_CONTROL_UI_VISIBILITY_DONE",#names);')


def add_readonly_blocker_diagnostics(controller, output):
    original = controller.capture_blocker
    sequence = 0

    def capture(target):
        nonlocal sequence
        original(target)
        sequence += 1
        names = sorted(name for name in controller.state
                       if isinstance(name, str) and re.search(r'Popup|Dialog|Screen|Diplomacy', name, re.I))
        path = output/'ui-visibility'/('%03d-target-%s.json' % (sequence, target))
        try:
            if 'PlotInfo' not in controller.state:
                write_json(path, dict(target=target, names=names, read_only=True, query_issued=False,
                    reason='Discovered PlotInfo context absent; no alternate guessed context'))
                return
            raw = controller.cmd(visibility_lua(names), 'PlotInfo', 'control-ui-visibility-'+str(sequence))
            rows = []
            for name, lookup, found, hidden_ok, hidden in re.findall(
                    r'CSC_CONTROL_UI_VISIBILITY\t([^\t\r\n]+)\t(true|false)\t(true|false)\t(true|false)\t([^\r\n]+)', raw):
                rows.append(dict(name=name, lookup_ok=lookup == 'true', found=found == 'true',
                    hidden_ok=hidden_ok == 'true', hidden=(hidden == 'true') if hidden in ('true', 'false') else None))
            done = re.findall(r'CSC_CONTROL_UI_VISIBILITY_DONE\s+(\d+)', raw)
            complete = done == [str(len(names))] and [r['name'] for r in rows] == names
            write_json(path, dict(target=target, names=names, read_only=True, query_issued=True,
                complete=complete, visibility=rows, raw=raw, controls_changed=False))
        except Exception as error:
            write_json(path, dict(target=target, names=names, read_only=True, diagnostic_error=str(error),
                controls_changed=False, no_query_replayed=True))

    controller.capture_blocker = capture


def reference_inputs(reference):
    """Use the qualified closed reference and its shared provenance checks."""
    baseline = trial.load_baseline(reference)
    return {key: baseline[key] for key in ('initial', 'installed', 'dependencies', 'pins',
                                          'planner_revision', 'controller_revision')}


def run(args):
    output = args.output.resolve()
    if output.exists():
        raise ValueError('New control output required; no replay')
    native_directory = Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Saves/Single"
    if (args.native_directory.resolve() != native_directory.resolve() or args.source.resolve().parent != native_directory.resolve()
            or args.source.suffix != '.Civ6Save' or trial.sha(args.source) != trial.SAVE_SHA):
        raise ValueError('Exact original source in native My Games/Saves/Single required')
    if native_inventory():
        raise RuntimeError('Foreign native/Tuner owner; preserve it')
    reference = reference_inputs(args.reference.resolve())
    trial.validate_source(reference['initial'])
    spec = trial.read(args.spec); spec['path'] = str(args.dll.resolve()); trial.validate_spec(spec)
    if trial.sha(args.dll) != trial.DLL_SHA:
        raise ValueError('Wrong native DLL')
    installed, dependencies = manifest(args.installed), manifest(args.dependencies)
    if installed != reference['installed'] or dependencies != reference['dependencies']:
        raise ValueError('Control package/dependencies differ from reference')
    output.mkdir(parents=True)
    write_json(output/'reference-input-compatibility.json', dict(reference=str(args.reference.resolve()),
        native_carrier_pins_unchanged=True, planner_revision=reference['planner_revision'],
        controller_revision=reference['controller_revision'], qualified_reference=True))
    reader = HERE/'source_snapshot.lua'; code = reader.read_text(encoding='utf-8')
    for token, literal in [('__PLAYER__', str(trial.PLAYER)), ('__CITY__', str(trial.CITY)), ('__DISTRICT__', json.dumps(trial.DISTRICT))]:
        if code.count(token) != 1:
            raise ValueError('Reader substitution contract changed')
        code = code.replace(token, literal)
    files = [args.binary, args.dll, args.source, args.spec, args.script,
             args.reference/'source-loaded.json', args.reference/'source-pins.json', args.reference/'source-archive.json']
    files += [p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py', '.js', '.c', '.lua')]
    files += [Path(m.__file__) for m in list(sys.modules.values()) if getattr(m, '__file__', None)
              and Path(m.__file__).suffix == '.py' and Path(m.__file__).is_relative_to(ROOT/'project/tools')]
    files += list((ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'))
    pins = {str(p.resolve()): trial.sha(p) for p in files}
    if not set(reference['pins']).issubset(pins):
        raise ValueError('Control does not preserve the entire prior native/input source-pin set')
    write_json(output/'source-pins.json', pins)
    write_json(output/'source-archive.json', archive_sources(pins, output/'source-version'))
    write_json(output/'installed-before.json', installed); write_json(output/'dependency-pins.json', dependencies)
    write_json(output/'protocol.json', dict(experiment='no-adjustment stall control', native_mode='baseline',
        source_turn=250, maximum_endpoint=254, intervals=[251, 252, 253, 254], loads=1, fresh_worlds=0,
        score_writes_allowed=0, controller_stall_seconds=600, stop_on_first_best=False,
        extra_diagnostics='one read-only PlotInfo visibility query after each existing blocker capture',
        presentation_adapter='shared default playback guards; Natural Wonder install is idempotent; pre-ack popup-stack/visibility evidence is retained',
        no_plan=True, no_orders=True, no_grants=True, no_queue_clearing=True, no_assistance=True,
        observed_comparability='Same save, package, native carrier and one-turn cadence; extra visibility reads and new playback guard are declared; this is not an unguarded stall-causality contrast'))
    controller = make_probe_controller(output, user_root=args.user_root)
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = controller.allow_observer_congress_review = True
    controller.study_endpoint = 254
    add_readonly_blocker_diagnostics(controller, output)
    install_natural_wonder_guard(controller)
    session = NativeSession(output, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    extension = None; attempted = False; initial = None; config = None; failure = None; cleanup_failure = None
    logs = {}; intervals = []; attempted_intervals = []; states = []; coverage = None

    def verify():
        if manifest(args.installed) != installed or manifest(args.dependencies) != dependencies:
            raise RuntimeError('Frozen installed package/dependencies changed')
        if any(trial.sha(path) != digest for path, digest in pins.items()):
            raise RuntimeError('Frozen control source/input changed')

    def capture(label):
        value = trial.parse(controller.cmd(code, 'GameCore_Tuner', label, wait=35))
        write_json(output/(label+'.json'), value); return value

    def gate():
        nonlocal initial
        initial = capture('source-loaded'); trial.validate_source(initial); verify()
        if initial != reference['initial']:
            raise ValueError('Loaded no-adjustment control source differs from reference initial facts')
        return True

    def copy_logs(label):
        destination = output/'logs'/label; destination.mkdir(parents=True)
        for name, baseline in logs.items():
            path = args.user_root/'Logs'/name
            if name in trial.REQUIRED_LOGS and not path.exists():
                raise RuntimeError('Required native log absent: ' + name)
            if path.exists():
                current, delta = read_log_delta(path, baseline)
                (destination/name).write_bytes(current.data)
                write_json(destination/(name+'.boundary.json'), dict(initial=baseline.evidence(), current=current.evidence(), delta_bytes=len(delta)))

    def freeze():
        if extension is not None and attempted:
            extension.before_menu()

    try:
        verify(); session.start(lambda: launch(args, output)); session.wait_context('MainMenu')
        configure(controller, output, 'BASIC')
        session.load_once(args.source, sha256=trial.SAVE_SHA, native_directory=args.native_directory, turn=250,
            contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'), eligibility=gate)
        config = trial.make_config(initial, 'baseline')
        write_json(output/'native-spec.json', spec); write_json(output/'extension-config.json', config)
        proof = prove_loaded_module(session.owner, spec, output/'loaded-module.json')
        extension = NativeExtension(output/'extension', session.owner, script=args.script, spec=output/'native-spec.json',
            config=output/'extension-config.json', dependencies=args.dependencies, loaded_module=output/'loaded-module.json')
        attempted = True; extension.attach_disabled()
        if capture('source-attached-disabled') != initial:
            raise RuntimeError('Disabled control attachment changed source facts')
        for name in trial.LOGS:
            logs[name] = capture_log_baseline(args.user_root/'Logs'/name)
        write_json(output/'source-gate.json', dict(verified=True, no_adjustment=True, original_humans=initial['currentHumans']))
        verify(); extension.start()
        for turn in range(251, 255):
            attempted_intervals.append(turn)
            controller.play(turn); intervals.append(turn)
            value = capture('boundary-'+str(turn))
            if value['turn'] != turn or value['target'].get('human') is not False:
                raise RuntimeError('Wrong inactive boundary or target role')
            trial.validate_reset(value)
            payload, saturated = extension.snapshot('turn-'+str(turn))
            coverage = trial.validate_snapshot(payload, config)
            if saturated or payload['stats']['changed'] != 0:
                raise RuntimeError('Control trace saturated or a score was unexpectedly changed')
            write_json(output/('native-'+str(turn)+'.json'), payload); write_json(output/'boundary-native.json', payload)
            copy_logs('turn-'+str(turn)); verify()
            states.append(dict(turn=turn, districts=trial.foundation(value), queue=value['target']['queue'], coverage=coverage, changes=0))
            write_json(output/'follow-through.json', states)
    except BaseException as error:
        failure = error
        write_json(output/'failure.json', dict(error=str(error), traceback=traceback.format_exc(),
            attempted_intervals=attempted_intervals, completed_intervals=intervals, no_automatic_replay=True))
    finally:
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda: restore_preferences(controller, output) if (output/'original-preferences.json').exists() else None,
                    restore_package=verify, before_menu=freeze,
                    after_native_exit=extension.after_native_exit if extension and getattr(extension, 'process', None) is not None else lambda: None)
                if logs:
                    copy_logs('closed')
            except BaseException as error:
                cleanup_failure = error
                write_json(output/'cleanup-failure.json', dict(error=str(error), traceback=traceback.format_exc(), original_error=str(failure)))
        try:
            verify(); write_json(output/'final-inventory.json', native_inventory())
            if session.closed and extension is not None and extension.process is not None:
                final = trial.read(output/'extension/trace-counts.json')['snapshot']
                trial.validate_snapshot(final, config, frozen=True)
                if final['stats']['changed'] != 0 or trial.read(output/'extension/trace-daemon-exit.json').get('diagnostic_fault') is not False:
                    raise RuntimeError('Final control diagnostics are not clean and adjustment-free')
        except BaseException as error:
            cleanup_failure = cleanup_failure or error
            write_json(output/'post-close-validation-failure.json', dict(error=str(error), traceback=traceback.format_exc(), closed=session.closed))
    native_exit = trial.read(output/'session-native-exit.json') if (output/'session-native-exit.json').exists() else {}
    preferences = trial.read(output/'preferences-restored.json') if (output/'preferences-restored.json').exists() else {}
    closed = session.closed and native_exit.get('exit_code') == 0 and preferences.get('verified') is True and cleanup_failure is None
    scientific = ('cleanup_or_final_validation_failed' if not closed else
                  'stalled_before_endpoint' if failure and 'stall' in str(failure).lower() else
                  'observation_failed' if failure else 'reached_control_endpoint')
    result = dict(experiment='no-adjustment stall control', profile=trial.PROFILE, native_mode='baseline',
        scientificOutcome=scientific, closed=closed, native_exit_code=native_exit.get('exit_code'),
        preferences_restored=preferences.get('verified') is True, completed_intervals=intervals,
        attempted_intervals=attempted_intervals, target_endpoint=254, coverage=coverage,
        score_writes_allowed=0, no_adjustment=True, failure=str(failure) if failure else None,
        cleanup_failure=str(cleanup_failure) if cleanup_failure else None,
        save_unchanged=trial.sha(args.source) == trial.SAVE_SHA,
        installed_unchanged=manifest(args.installed) == installed, efficacy_claimed=False)
    write_json(output/'close-proof.json', dict(closed=closed, native_exit=native_exit, preferences=preferences,
        cleanup_failure=result['cleanup_failure'], scientificOutcome=scientific))
    write_json(output/'result.json', result); print(json.dumps(result))
    if cleanup_failure:
        raise cleanup_failure
    if failure:
        raise failure
    if not closed:
        raise RuntimeError('Control session did not close with verified restoration')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'source', 'native-directory', 'binary', 'dll', 'user-root', 'installed', 'dependencies', 'spec', 'script', 'reference'):
        parser.add_argument('--'+name, type=Path, required=True)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
