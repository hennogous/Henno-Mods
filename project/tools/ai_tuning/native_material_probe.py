"""One source110 load and at most five native turns of material observation.

Composes the maintained session and finite core. No orders, new actors, package
changes, saves, new worlds, or automatic extensions/retries. Optional reviewed
read-only consumer hooks are explicit and default off.
"""
import hashlib
import json
import re
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'project/tools/ai_baseline'), str(ROOT/'project/tools/ai_tuning')]
from native_session_probe import launch, parser
from native_profile_test import configure, manifest, restore_preferences
from full_game_controller.probe import make_probe_controller, write_json
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory
from full_game_controller.log_capture import capture_log_baseline, read_log_delta
from native_probe_artifacts import archive_sources


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse(raw, marker):
    values = re.findall(re.escape(marker)+r'=([^\r\n]+)', raw)
    if len(values) != 1:
        raise ValueError('Missing/ambiguous native observation marker: '+marker)
    return json.loads(values[0])


def physical_changes(initial, current):
    """Compare physical targets, not recommendations or repeated log rows."""
    before = {r['plot']: r for r in initial['targets']}
    after = {r['plot']: r for r in current['targets']}
    if before.keys() != after.keys():
        raise ValueError('Target scope changed')
    fields = ('owner', 'resource', 'count', 'feature', 'improvement',
              'improvement_pillaged', 'district')
    return [{'plot': idx, 'fields': {k: [before[idx][k], after[idx][k]]
            for k in fields if before[idx][k] != after[idx][k]}}
            for idx in before if any(before[idx][k] != after[idx][k] for k in fields)]


def validate_endpoint(endpoint, recommendations=False):
    if not 110 <= endpoint <= 115:
        raise ValueError('Material endpoint must stay within110..115')
    if recommendations and endpoint > 113:
        raise ValueError('Recommendation diagnostic allows at most3AIturns')


def validate_recommendation_coverage(value):
    cities = value['cities']; builders = value['builders']
    if not cities or not builders:
        raise ValueError('Source recommendation scope lacks real cities/Builders')
    city_ids = {c['city'] for c in cities}; unit_ids = {b['unit'] for b in builders}
    if any(b['owner'] != 3 for b in builders):
        raise ValueError('Foreign Builder identity in recommendation scope')
    if len(city_ids) != len(cities) or len(unit_ids) != len(builders):
        raise ValueError('Duplicate city/Builder identity')
    for city in cities:
        results = [city['generic']] + [b['result'] for b in city['builder_recommendations']]
        if any(b['owner'] != 3 or b['city'] != city['city'] for b in city['builder_recommendations']):
            raise ValueError('Foreign/mismatched city-Builder pair')
        if city['owner'] != 3 or {b['unit'] for b in city['builder_recommendations']} != unit_ids or len(results) != 1+len(builders):
            raise ValueError('Incomplete city/Builder recommendation joins')
        if any(r.get('status') not in ('ok_empty','ok_records') or not r.get('called') or not r.get('ok') or r.get('native_return_type') != 'table' for r in results):
            raise ValueError('Native recommendation API unavailable/error/unparsed; no absence claim or further AI')
    if value['budget']['API_calls'] != len(cities)*(1+len(builders)):
        raise ValueError('Incomplete recommendation API call coverage')
    return True


def main():
    p = parser()
    p.add_argument('--material-reader', type=Path, required=True)
    p.add_argument('--installed-reference', type=Path, required=True)
    p.add_argument('--logs', type=Path, required=True)
    p.add_argument('--recommendation-reader', type=Path)
    p.add_argument('--endpoint', type=int, default=115)
    p.add_argument('--observer-contract', type=Path)
    a = p.parse_args()
    validate_endpoint(a.endpoint, a.recommendation_reader is not None or a.observer_contract is not None)
    if a.observer_contract and a.recommendation_reader:
        raise ValueError('Native work observer excludes advisory recommendation calls')
    observer_module = None; observer_contract = None
    if a.observer_contract:
        sys.path.insert(0,str(ROOT/'project/tools/native_ai'))
        import observer_host as observer_module
        observer_contract = json.loads(a.observer_contract.read_text(encoding='utf-8-sig'))
        observer_module.validate_contract(json.loads(Path(observer_contract['spec']).read_text()), json.loads(Path(observer_contract['config']).read_text()), 2)
    if a.turn != 110 or a.reference_key:
        raise ValueError('This protocol requires the complete source110 census')
    out = a.output.resolve()
    if out.exists():
        raise RuntimeError('Output exists; no automatic replay')
    if native_inventory():
        raise RuntimeError('Native/Tuner owner present')
    before = manifest(a.installed)
    expected = json.loads(a.installed_reference.read_text(encoding='utf-8-sig'))
    if before != expected:
        raise RuntimeError('Current package differs from declared611 capture; no launch or overwrite')
    if len(before) != 611:
        raise RuntimeError('Expected captured611 package')
    if sha(a.source) != a.sha256:
        raise RuntimeError('Source save changed')
    out.mkdir(parents=True)
    write_json(out/'worker-owner.json', dict(pid=__import__('os').getpid(), started=time.time()))
    write_json(out/'installed-before.json', before)
    reference = json.loads(a.reference.read_text(encoding='utf-8-sig'))
    paths = [a.binary, a.binary.parents[3]/'DLC/Expansion2/Binaries/Win64/GameCore_XP2_FinalRelease.dll',
             a.source, a.reader, a.reference, a.material_reader, a.installed_reference, Path(__file__), Path(__file__).with_name('test_native_material.py')]
    paths += [Path(m.__file__) for m in list(sys.modules.values()) if getattr(m, '__file__', None)
              and Path(m.__file__).suffix == '.py' and Path(m.__file__).is_relative_to(ROOT/'project/tools')]
    paths += list((ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'))
    paths += [q for q in a.rh_package.rglob('*') if q.is_file()]
    if a.recommendation_reader:
        paths += [a.recommendation_reader, Path(__file__).with_name('test_native_material_recommendations.py')]
    if observer_contract:
        paths += [a.observer_contract, *(Path(observer_contract[k])for k in ('script','spec','config')), ROOT/'project/tools/native_ai/observer_daemon.py', ROOT/'project/tools/native_ai/test_work_admission_observer.js', ROOT/'project/tools/native_ai/test_observer_host.py']
        paths += [q for q in Path(observer_contract['dependencies']).rglob('*')if q.is_file()]
    pins = {str(q.resolve()): sha(q) for q in paths}
    write_json(out/'source-archive-scope.json', archive_sources(pins, out/'source-version'))
    write_json(out/'source-pins.json', pins)
    write_json(out/'contract.json', dict(source_turn=110, endpoint_max=a.endpoint, AI_turns_max=a.endpoint-110,
        diagnostic_repeat_of_prior_interval=a.recommendation_reader is not None or observer_contract is not None,
        observer_boundaries=2 if observer_contract else 0, observer_max_pairs=64 if observer_contract else 0,
        source_sha256=a.sha256, worlds=0, source_loads_max=1, no_forced_orders=True,
        no_property_treatment=True, first_target_physical_change_stops=True,
        assistance_pause='session callback/queue only; persistent ledgers retained'))
    r = make_probe_controller(out)
    r.study_endpoint = a.endpoint
    r.allow_observer_warning_dismissal = True
    r.allow_observer_congress_review = True
    session = NativeSession(out, r, inventory=native_inventory, hold=HeldProcess, write=write_json)
    core = a.reader.read_text(encoding='utf-8-sig')
    reader = a.material_reader.read_text(encoding='utf-8-sig')
    recommendation_reader = a.recommendation_reader.read_text(encoding='utf-8-sig') if a.recommendation_reader else None
    error = None
    endpoint = None
    reason = None
    log_boundaries = {}
    observer = None; runtime_observer_pins = {}; previous_observer_records = []

    def verify_inputs():
        if manifest(a.installed) != before:
            raise RuntimeError('Installed package changed; preserve it')
        changed = [path for path, digest in {**pins,**runtime_observer_pins}.items() if sha(path) != digest]
        if changed:
            raise RuntimeError('Frozen inputs changed: '+repr(changed))

    def census(label):
        value = parse(r.cmd(core, 'GameCore_Tuner', label, wait=25), a.marker)
        for key in ('players', 'cities', 'units'):
            value[key].sort(key=lambda v: (v.get('owner', -1), v['id']))
        write_json(out/(label+'.json'), value)
        return value

    def capture(label):
        value = parse(r.cmd(reader.replace('__CORE_LEGALITY_ONLY__', 'false'), 'PlotInfo', label, wait=25), 'CSC_MATERIAL_FOLLOWTHROUGH')
        legal = parse(r.cmd(reader.replace('__CORE_LEGALITY_ONLY__', 'true'), 'GameCore_Tuner', label+'-core-legality', wait=25), 'CSC_MATERIAL_LEGALITY')
        write_json(out/(label+'-core-legality.json'), legal)
        value['core_legality'] = legal
        write_json(out/(label+'.json'), value)
        return value

    def recommendations(label, validate=True):
        if recommendation_reader is None: return None
        value = parse(r.cmd(recommendation_reader, 'PlotInfo', label+'-recommendations', wait=25), 'CSC_MATERIAL_RECOMMENDATIONS')
        write_json(out/(label+'-recommendations.json'), value)
        if validate: validate_recommendation_coverage(value)
        return value

    def gate():
        initial = census('initial-census')
        verify_inputs()
        if initial != reference:
            raise RuntimeError('Complete source110 census mismatch; no rebase/reload')
        return True

    def logs(label):
        evidence = {}
        for name, boundary in list(log_boundaries.items()):
            path = a.logs/name
            if not path.exists() and not boundary.existed:
                evidence[name] = dict(observed=False, reason='not created', baseline=boundary.evidence())
                continue
            next_boundary, delta = read_log_delta(path, boundary)
            target = out/'logs'/label/name; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(delta)
            evidence[name] = dict(observed=True, before=boundary.evidence(), after=next_boundary.evidence(),
                                  segment_sha256=sha(target), segment_bytes=len(delta))
            log_boundaries[name] = next_boundary
        write_json(out/'logs'/label/'boundaries.json', evidence)
        lua = (out/'logs'/label/'Lua.log')
        if lua.exists() and re.search(rb'(Runtime Error|Stack traceback|Lua Error)', lua.read_bytes(), re.I):
            raise RuntimeError('New native Lua error in closed observed log segment')

    try:
        verify_inputs()
        session.start(lambda: launch(a, out))
        session.wait_context('MainMenu')
        configure(r, out, a.profile)
        session.load_once(a.source, sha256=a.sha256, native_directory=a.native_directory, turn=110,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AI_Assistance', 'CSC_AdjacencyGameplay'), eligibility=gate)
        initial = capture('material-before-pause-110')
        if recommendation_reader is not None:
            initial_recommendations = recommendations('material-before-pause-110', validate=False)
            if census('initial-recommendation-read-census') != reference:
                raise RuntimeError('Initial recommendation read changed complete Core state')
            write_json(out/'initial-recommendation-read-proof.json', dict(verified=True, complete_Core_before_after_equal=True, cache_freshness='unknown'))
            validate_recommendation_coverage(initial_recommendations)
        if len(initial['quarters']) != 3 or any(x['owner'] != 3 for x in initial['targets']):
            raise RuntimeError('Target identity/ownership/Quarter invariant failed')
        for target in initial['targets']:
            if target['improvement'] != -1 or target['district'] != -1:
                raise RuntimeError('Declared targets no longer unimproved/uncovered')
        session.issue_once('pause-new-assistance', "assert(Game.GetCurrentGameTurn()==110 and not AutoplayManager.IsActive());local m=assert(CSC_AI_Assistance);Events.PlayerTurnActivated.Remove(m.OnPlayerTurn);m.queued={};m.TryQueued=function()end;print('CSC_ASSISTANCE_SUSPENDED');", 'CSC_AI_Assistance')
        paused = capture('material-110')
        after_pause = census('pause-census')
        if paused != initial or after_pause != reference:
            raise RuntimeError('Session-only pause changed persisted economics or physical census')
        recommendations('material-110')
        write_json(out/'pause-proof.json', dict(verified=True, exact_complete_core_equal=True, exact_scoped_and_ledger_equal=True))
        if observer_contract:
            runtime_dir=out/'observer-inputs';runtime_dir.mkdir()
            config=json.loads(Path(observer_contract['config']).read_text());catalog=initial['metadata']['improvement_catalog']
            if not 0<catalog['count']<=256 or not 0<catalog['index_limit']<=256:
                raise RuntimeError('Actual native improvement catalog exceeds declared bound')
            for name in ('IMPROVEMENT_FARM','IMPROVEMENT_CAMP','IMPROVEMENT_MINE'):
                if name not in catalog['selected']:raise RuntimeError('Required native improvement identity missing')
            config.update(improvementCatalog=catalog['rows'],improvementIndexLimit=catalog['index_limit'],mapWidth=reference['width'],mapHeight=reference['height'])
            runtime_config=runtime_dir/'observer-config.json';write_json(runtime_config,config)
            spec=json.loads(Path(observer_contract['spec']).read_text());proof=runtime_dir/'loaded-module.json'
            observer_module.prove_loaded_module(session.owner,spec,proof)
            observer=observer_module.NativeObserver(out/'observer',session.owner,script=Path(observer_contract['script']),spec=Path(observer_contract['spec']),config=runtime_config,dependencies=Path(observer_contract['dependencies']),loaded_module=proof)
            observer.attach_disabled()
            if census('observer-attached-census')!=reference or capture('observer-attached-material-110')!=initial:
                raise RuntimeError('Disabled observer attachment changed complete source/scoped state')
            write_json(out/'observer-attachment-proof.json',dict(verified=True,complete_Core_equal=True,scoped_and_ledger_equal=True,improvement_catalog=catalog))
            for path in [runtime_config,proof,*[out/'observer'/n for n in ('trace.js','native-spec.json','observer-config.json','loaded-module.json','native-owner.json')]]:
                runtime_observer_pins[str(path.resolve())]=sha(path)
            write_json(out/'observer-runtime-pins.json',runtime_observer_pins)
            observer.start()
        names = {'AI_Behavior_Trees.csv', 'AI_Planning.csv', 'UnitOperations.log', 'Lua.log', 'Database.log'}
        names.update(q.name for q in a.logs.iterdir() if q.is_file() and (q.name.startswith('AI_') or q.name.startswith('Unit')))
        log_boundaries = {name: capture_log_baseline(a.logs/name) for name in sorted(names)}
        write_json(out/'logs'/'initial-boundaries.json', {n: b.evidence() for n, b in log_boundaries.items()})
        for turn in range(111, a.endpoint+1):
            verify_inputs()
            r.play(turn)
            endpoint = turn
            current = capture('material-'+str(turn))
            if current['turn'] != turn:
                raise RuntimeError('Scoped capture clock mismatch')
            recommendations('material-'+str(turn))
            logs('turn-'+str(turn))
            if current['ledger'] != initial['ledger']:
                raise RuntimeError('Assistance persistent ledger changed while paused')
            observer_saturated=False
            if observer is not None:
                trace,observer_saturated=observer.snapshot('boundary-'+str(turn))
                if trace['records'][:len(previous_observer_records)]!=previous_observer_records:
                    raise RuntimeError('Observer record prefix changed')
                write_json(out/('observer-boundary-'+str(turn)+'.json'),dict(turn=turn,native_AI_turn=turn-1,completed_pairs=trace['stats']['completedPairs'],new_pairs=len(trace['records'])-len(previous_observer_records),saturated=observer_saturated))
                previous_observer_records=trace['records']
            changes = physical_changes(initial, current)
            write_json(out/'latest-boundary.json', dict(turn=turn, physical_changes=changes,
                       target_states=current['targets'], builder_count=len(current['builders'])))
            if changes:
                reason = 'target_physical_change'; break
            if observer_saturated:
                reason = 'observer_saturated_at_inactive_boundary'; break
        else:
            reason = 'bounded_non_response_through'+str(a.endpoint)
        if endpoint is None: endpoint = 110
        r.ready(endpoint, 'final-boundary')
        census('final-census')
        verify_inputs()
    except BaseException as failure:
        error = failure
        write_json(out/'failure.json', dict(error=str(failure), traceback=traceback.format_exc(), no_retry=True, endpoint=endpoint))
    finally:
        if log_boundaries:
            try: logs('before-menu-tail')
            except BaseException as tail_error:
                write_json(out/'log-tail-failure.json', dict(error=str(tail_error)))
                if error is None: error = tail_error
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda: restore_preferences(r, out), restore_package=verify_inputs, before_menu=observer.before_menu if observer else (lambda:None), after_native_exit=observer.after_native_exit if observer else (lambda:None))
            except BaseException as failure:
                write_json(out/'cleanup-failure.json', dict(error=str(failure), traceback=traceback.format_exc(), original_error=str(error)))
                if error is None: error = failure
        if session.closed and log_boundaries:
            try: logs('closed-tail')
            except BaseException as tail_error:
                write_json(out/'closed-log-tail-failure.json', dict(error=str(tail_error)))
                if error is None: error = tail_error
        verify_inputs()
        write_json(out/'final-inventory.json', native_inventory())
    if error is not None:
        raise error
    if not session.closed:
        raise RuntimeError('Session not normally closed')
    result = dict(verified=True, actual_endpoint=endpoint, turns_advanced=endpoint-110,
                  stop_reason=reason, source_save_unchanged=True, installed_files=len(before),
                  installed_unchanged=True, preferences_restored=True, owners_absent=True,
                  native_exit_code=0, causal_benefit_claim=False)
    write_json(out/'result.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
