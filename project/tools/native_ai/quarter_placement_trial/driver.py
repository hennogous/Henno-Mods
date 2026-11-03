"""Closed-baseline site intervention and bounded natural Quarter follow-through.

Only the shared controller performs game operations. Importing this module does
not launch, attach, load, send an order, or connect to a game. The plan is a
mechanism test, not a material/customer quality heuristic or an efficacy trial.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'project/tools/ai_baseline'), str(HERE.parent)]
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory
from full_game_controller.log_capture import capture_log_baseline, read_log_delta
from full_game_controller.environment import (launch, configure, manifest,
    restore_preferences, archive_sources, prove_loaded_module, write_json)

PROFILE = 'quarter-placement-choice-v2'
SAVE_SHA = 'ea818368130273e02e70e31449a6f24a54e34486b8bfa402dd34b62255443e48'
DLL_SHA = '324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
DISTRICT = 'DISTRICT_CSC_TAILORS_QUARTER'
PLAYER, CITY = 5, 131073
FUNCTIONS = {
    'DistrictNetValue': (0x52a440, '8954241055535657415441554156488d6c24f14881eca0000000448b756f33c0'),
    'CalculateDistrictValues': (0x3dfee0, '4c8bdc41554881eca000000083b9d8040000004c8be90f84ae030000488b91c8'),
    'GetBestDistrict': (0x3e4a50, '48894c24085355564154415541574883ec284c8bea488be9e873be3e00488bb5'),
    'PresentValueOf': (0x3e7f40, '4d63d84c8bd2488bc14183fbff750833c9488bc2890ac34d85c9744d8b81d804'),
}
REQUIRED_LOGS = ('AI_CityBuild.csv', 'AI_Behavior_Trees.csv', 'City_BuildQueue.csv')
LOGS = REQUIRED_LOGS + ('Lua.log', 'Database.log', 'Modding.log')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse(raw):
    values = re.findall(r'CSC_QUARTER_PLACEMENT_WORLD=([^\r\n]+)', raw)
    if len(values) != 1:
        raise ValueError('Missing or ambiguous Quarter source observation')
    return json.loads(values[0])


def integer(value, lower=-2147483648, upper=2147483647):
    return type(value) is int and lower <= value <= upper


def clean_site(row):
    return (isinstance(row, dict) and integer(row.get('index'), 0, 3403)
        and integer(row.get('x'), 0, 73) and integer(row.get('y'), 0, 45)
        and row['index'] == row['x'] + row['y'] * 74
        and row.get('owner') == PLAYER
        and all(row.get(k) == -1 for k in ('district', 'feature', 'resource', 'improvement'))
        and all(row.get(k) is False for k in ('water', 'impassable', 'pillaged'))
        and row.get('revealed') is True and row.get('legal') is True
        and row.get('purchaseCity') == dict(player=PLAYER, city=CITY))


def validate_reset(value):
    reset, assistance = value['aiReset'], value['assistance']
    if (reset.get('privateYieldPresent') is not False or reset.get('profileTablePresent') is not False
            or any(reset.get(k) != [] for k in ('profileRows', 'cscAILists', 'cscAIAdjacencies', 'cscAIModifiers'))):
        raise ValueError('Old CSC AI database inputs remain loaded')
    if (assistance.get('properties') != {} or assistance.get('pending') != {}
            or assistance.get('turnCycles') != {}
            or not isinstance(assistance.get('contextExposure'), dict)
            or any(v is not False for v in assistance['contextExposure'].values())):
        raise ValueError('Legacy assistance state or context exposure remains; no repairs permitted')


def validate_source(value):
    if (value['turn'], value['width'], value['height']) != (250, 74, 46):
        raise ValueError('Wrong source turn or map')
    target, mapping = value['target'], value['mapping']
    if (not all(target.get(k) is True for k in ('exists', 'alive', 'major'))
            or target.get('human') is not False
            or (target.get('player'), target.get('city'), target.get('x'), target.get('y')) != (PLAYER, CITY, 50, 32)
            or target.get('hasSelectedQuarter') is not False):
        raise ValueError('Declared original AI Sydney or absent Tailors fixture changed')
    if value.get('currentHumans') != [0]:
        raise ValueError('Initial original human identity differs; capture before autoplay')
    players = {r['player']: r for r in value['players']}
    if players.get(0, {}).get('human') is not True or players.get(PLAYER, {}).get('human') is not False:
        raise ValueError('Source player identities absent')
    if (mapping.get('districtType') != DISTRICT
            or not integer(mapping.get('districtCount'), 1, 4096)
            or mapping.get('districtIndexLimit') != mapping['districtCount']
            or not integer(mapping.get('districtIndex'), 0, mapping['districtCount'] - 1)):
        raise ValueError('Invalid loaded district mapping')
    catalog = value['districtCatalog']
    if (len(catalog) != mapping['districtCount']
            or {r['index'] for r in catalog} != set(range(mapping['districtCount']))
            or [r['type'] for r in catalog if r['index'] == mapping['districtIndex']] != [DISTRICT]):
        raise ValueError('Unverified contiguous loaded district catalog')
    definition = value['definition']
    if (definition.get('DistrictType') != DISTRICT or definition.get('PrereqCivic') != 'CIVIC_CRAFTSMANSHIP'
            or definition.get('RequiresPlacement') is not True or definition.get('InternalOnly') is not False
            or definition.get('OnePerCity') is not True or definition.get('RequiresPopulation') is not False
            or target['research'].get('prereqCivic') is not True):
        raise ValueError('Changed Quarter definition or missing current civic')
    if any(r.get('type') == DISTRICT for r in target['districts']):
        raise ValueError('Tailors already founded; no placement intervention allowed')
    candidates = value['candidates']
    if (not isinstance(candidates, list) or len(candidates) != 37
            or len({r['index'] for r in candidates}) != 37
            or any(not integer(r.get('distance'), 0, 3) for r in candidates)
            or len([r for r in candidates if clean_site(r)]) < 2):
        raise ValueError('Need complete radius-three facts and at least two clear owned legal sites')
    validate_reset(value)
    return True


def validate_spec(spec):
    rows = spec.get('functions', [])
    if (len(rows) != 4 or {r['name']: (r['rva'], r['bytes']) for r in rows} != FUNCTIONS
            or spec.get('sha256') != DLL_SHA or spec.get('timestamp') != 1719431003
            or spec.get('image_size') != 12976128):
        raise ValueError('Unreviewed native binary or fingerprint specification')


def validate_snapshot(payload, config, *, frozen=False):
    if payload.get('profile') != PROFILE or payload.get('read_only') is not False:
        raise ValueError('Explicit native intervention profile required')
    stats, rows = payload['stats'], payload['records']
    for key in ('callbacks', 'admitted', 'changed', 'errors', 'records', 'suppressed', 'active', 'mode'):
        if not integer(stats.get(key), 0, 4294967295):
            raise ValueError('Malformed native counter: ' + key)
    if (stats['records'] != len(rows) or len(rows) > 512 or stats['mode'] > 2
            or stats['errors'] or stats['active'] or stats['suppressed']
            or payload.get('fatal') or payload.get('saturated') or stats['records'] >= 512):
        raise RuntimeError('Native fault, unfinished frame, or saturated record budget')
    if frozen and stats['mode'] != 0:
        raise RuntimeError('Native freeze did not disable')
    if not frozen and stats['mode'] == 0:
        raise RuntimeError('Native monitoring disarmed during the declared interval')
    changes = []
    for row in rows:
        if (row.get('k') not in ('net', 'cache', 'best', 'pv') or row.get('player') != PLAYER or row.get('city') != CITY
                or any(not integer(row.get(k)) for k in ('district', 'plot', 'x', 'y', 'base', 'result', 'reason', 'eligible'))):
            raise ValueError('Malformed or out-of-city native record')
        if row['k'] in ('net', 'cache') and row['district'] != config['districtIndex']:
            raise ValueError('Native selected-type scope changed')
        if row['k'] == 'net' and row['base'] != row['result']:
            changes.append(row)
    if (stats['changed'] != len(changes) or stats['changed'] > (0 if config['mode'] == 'baseline' else 128)
            or any((r['district'], r['plot'], r['x'], r['y']) != (config['districtIndex'], config['plot'], config['plotX'], config['plotY'])
                   or r['result'] - r['base'] != config['deltaQ8'] or r['reason'] != 0 or r['eligible'] != 1
                   or r['base'] in (0, -2559744) for r in changes)):
        raise RuntimeError('Native mutation exceeds the declared single-site additive policy')
    return {kind: sum(r['k'] == kind for r in rows) for kind in ('net', 'cache', 'best', 'pv')}


def make_config(initial, mode, plan=None):
    mapping = initial['mapping']
    preferred = plan['preferred'] if plan else dict(plot=-1, x=-1, y=-1)
    return dict(profile=PROFILE, mode=mode, deltaQ8=plan['deltaQ8'] if plan else 256,
        player=PLAYER, city=CITY, districtType=DISTRICT, districtIndex=mapping['districtIndex'],
        districtCount=mapping['districtCount'], districtIndexLimit=mapping['districtIndexLimit'],
        plot=preferred['plot'], plotX=preferred['x'], plotY=preferred['y'], mapWidth=74, mapHeight=46,
        maxChanges=128, maxRecords=512, session=7, epoch=1, version=2,
        originalHuman=False, currentHuman=False, mappingVerified=True, snapshotVerified=True,
        baselineGapQ8=plan['baselineGapQ8'] if plan else 0, marginQ8=256)


def make_plan(baseline):
    """Pure qualification and deterministic runner-up selection over a bundle."""
    result = baseline['result']
    if (result.get('mode') != 'baseline' or result.get('profile') != PROFILE
            or result.get('closed') is not True or result.get('native_exit_code') != 0
            or any(result.get(k) is not True for k in ('preferences_restored', 'save_unchanged', 'installed_unchanged'))
            or baseline['preferences'].get('verified') is not True
            or baseline['closed'].get('verified') is not True
            or baseline['closed'].get('owners_absent') is not True
            or baseline['inventory'] != [] or baseline['save_sha256'] != SAVE_SHA):
        raise ValueError('A fully closed and restored unchanged baseline is required')
    decision_turn = result.get('decisionTurn')
    if (not integer(decision_turn, 251, 255)
            or result.get('intervals') != list(range(251, decision_turn + 1))):
        raise ValueError('Need a first natural decision within the bounded five-interval baseline')
    initial, payload, frozen = baseline['initial'], baseline['payload'], baseline['frozen']
    validate_source(initial)
    decision = baseline['decision']
    if (decision.get('turn') != decision_turn or decision['target'].get('player') != PLAYER
            or decision['target'].get('city') != CITY or decision['target'].get('human') is not False):
        raise ValueError('Missing or changed decision-boundary city observation')
    validate_reset(decision)
    config = make_config(initial, 'baseline')
    if baseline['config'] != config:
        raise ValueError('Baseline configuration differs from the declared clean scope')
    validate_snapshot(payload, config)
    validate_snapshot(frozen, config, frozen=True)
    if frozen['records'] != payload['records']:
        raise ValueError('Native records changed after the baseline boundary observation')
    reservations = payload.get('reservations')
    if (payload.get('reservationCaptureCount') != 1 or not isinstance(reservations, list) or len(reservations) > 37
            or any(not isinstance(r, dict) or any(not integer(r.get(k)) for k in ('plot', 'controller', 'score', 'cacheScore')) for r in reservations)
            or len({r['plot'] for r in reservations}) != len(reservations)
            or frozen.get('reservations') != reservations
            or frozen.get('reservationCaptureCount') != payload['reservationCaptureCount']):
        raise ValueError('Need one unambiguous bounded native reservation capture for the baseline choice')
    reservation_by_plot = {r['plot']: r for r in reservations}
    initial_sites = {r['index']: r for r in initial['candidates'] if clean_site(r)}
    decision_sites = {r['index']: r for r in decision['candidates'] if clean_site(r) and r['index'] in initial_sites
             and (r['x'], r['y']) == (initial_sites[r['index']]['x'], initial_sites[r['index']]['y'])}
    sites = initial_sites
    records = payload['records']
    best_positions = [i for i, row in enumerate(records) if row['k'] == 'best']
    if len(best_positions) != 1:
        raise ValueError('Need exactly one natural Best call, with no multiple-choice ambiguity')
    best_position = best_positions[0]
    if any(r['k'] in ('net', 'cache') for r in records[best_position + 1:]):
        raise ValueError('Post-Best calculation makes the flat reservation capture ambiguous')
    if best_position == 0 or records[best_position - 1]['k'] != 'cache':
        raise ValueError('Best must immediately follow its fresh contiguous cache block')
    cache_start = best_position - 1
    while cache_start > 0 and records[cache_start - 1]['k'] == 'cache':
        cache_start -= 1
    cache_rows = records[cache_start:best_position]
    if len({r['plot'] for r in cache_rows}) != len(cache_rows):
        raise ValueError('Duplicate plots within the selected cache generation')
    previous_cache_end = max((i for i in range(cache_start) if records[i]['k'] == 'cache'), default=-1)
    nets, caches = {}, {r['plot']: [r] for r in cache_rows}
    for row in records[previous_cache_end + 1:cache_start]:
        if row['k'] == 'net':
            nets.setdefault(row['plot'], []).append(row)
    winners = [r for r in records if r['k'] == 'best' and r['eligible'] == 1 and r['result'] > 0
               and integer(r['district'], 0, initial['mapping']['districtCount'] - 1)
               and integer(r['plot'], 0, 3403) and r['plot'] == r['x'] + 74 * r['y']]
    if len(winners) != 1:
        raise ValueError('Need exactly one unambiguous positive native joint winner')
    winner = winners[0]
    joined = []
    for index, site in sites.items():
        if len(nets.get(index, [])) != 1 or len(caches.get(index, [])) != 1:
            continue
        net, cache = nets[index][0], caches[index][0]
        reservation = reservation_by_plot.get(index)
        if (net['base'] > 0 and net['base'] == net['result'] and net['reason'] == 0 and net['eligible'] == 1
                and cache['base'] > 0 and cache['base'] == cache['result'] and cache['reason'] == 0 and cache['eligible'] == 1
                and reservation is not None and reservation['controller'] == -1 and reservation['cacheScore'] == cache['result']
                and (net['x'], net['y']) == (cache['x'], cache['y']) == (site['x'], site['y'])):
            joined.append(dict(district=config['districtIndex'], plot=index, x=site['x'], y=site['y'],
                               cacheQ8=cache['result'], netQ8=net['base']))
    experiment_kind = 'site switch' if winner['district'] == config['districtIndex'] else 'district-type switch'
    if len(joined) < (2 if experiment_kind == 'site switch' else 1):
        raise ValueError('Need two unambiguous fresh positive NetValue/cache pairs for a same-type site switch, or one for a district-type switch')
    joined.sort(key=lambda r: (-r['cacheQ8'], r['plot']))
    alternatives = [r for r in joined if r['plot'] in decision_sites
                    and (r['district'], r['plot']) != (winner['district'], winner['plot'])]
    if not alternatives:
        raise ValueError('No distinct eligible alternative still clear at the decision boundary')
    chosen = alternatives[0]
    gap = max(winner['result'], joined[0]['cacheQ8']) - chosen['cacheQ8']
    delta = gap + 256
    if not integer(gap, 0, 1048320) or not integer(delta, 256, 1048576):
        raise ValueError('Observed gap exceeds the declared additive intervention limit; no clamp')
    if (chosen['netQ8'] + delta > 2147483647
            or chosen['cacheQ8'] + (3 * delta + 1) // 2 + 1 > 2147483647):
        raise ValueError('Potential signed32 overflow after NetValue or positive district preference; no intervention')
    return dict(profile=PROFILE, sourceSaveSha256=SAVE_SHA, player=PLAYER, city=CITY, districtType=DISTRICT, decisionTurn=decision_turn,
        preferred=chosen, baselineWinning={k: winner[k] for k in ('district', 'plot', 'x', 'y')} | {'scoreQ8': winner['result']},
        baselineGapQ8=gap, deltaQ8=delta, marginQ8=256,
        joinedPositiveSites=joined, experimentKind=experiment_kind,
        plotChanged=chosen['plot'] != winner['plot'], districtTypeChanged=chosen['district'] != winner['district'],
        planner_revision=baseline.get('planner_revision'), controller_revision=baseline.get('controller_revision'),
        scope='mechanism only; score-ranked unreserved Quarter alternative, not a site-quality heuristic',
        observationSlice=dict(previousCacheEnd=previous_cache_end, netStart=previous_cache_end + 1,
                              cacheStart=cache_start, cacheEnd=best_position - 1, bestPosition=best_position),
        policy='add gap plus one utility unit to fresh preferred-site NetValue; no direct cache write or forced order')


def load_baseline(directory):
    import ast
    directory = Path(directory).resolve()
    pins = read(directory/'source-pins.json')
    current_driver = (HERE/'driver.py').resolve()
    current_controller = (ROOT/'project/tools/ai_baseline/full_game_controller/controller.py').resolve()
    planner_revision = None
    controller_revision = None
    for path, digest in pins.items():
        actual = sha(path)
        if actual == digest:
            continue
        if Path(path).resolve() == current_controller:
            if digest != '9a5d34e0037213a9ccbf7fcc4515b957286244900a48a918f7fe50d7001e44c2':
                raise ValueError('Unreviewed original controller pin for presentation revision')
            archives = read(directory/'source-archive.json')['archived']
            matches = [r for r in archives if Path(r['source']).resolve() == current_controller]
            if len(matches) != 1:
                raise ValueError('Exactly one archived baseline controller source is required')
            archived = Path(matches[0]['archive']).resolve()
            if (not archived.is_relative_to((directory/'source-version').resolve())
                    or not archived.is_file() or sha(archived) != digest):
                raise ValueError('Archived baseline controller source does not match its original pin')
            # Text equality permits precisely the reviewed presentation hook.
            # CRLF is the sole normalization; policy/timing/control text is exact.
            before_controller = archived.read_bytes().decode('utf-8').replace('\r\n', '\n')
            after_controller = current_controller.read_bytes().decode('utf-8').replace('\r\n', '\n')
            import_anchor = 'from .transport import receive_command,MissingAcknowledgment,NativeLuaFailure\n'
            init_anchor = "  self.session_token='CSC_FULL_ACK_'+str(os.getpid())+'_'\n"
            import_line = 'from .presentation_playback import install as install_playback_guard\n'
            init_line = '  install_playback_guard(self)\n'
            if before_controller.count(import_anchor) != 1 or before_controller.count(init_anchor) != 1:
                raise ValueError('Original controller presentation patch anchors are not unique')
            expected_controller = before_controller.replace(import_anchor, import_anchor + import_line, 1).replace(init_anchor, init_anchor + init_line, 1)
            if after_controller != expected_controller:
                raise ValueError('Controller differs from the exact reviewed two-line presentation patch')
            controller_revision = dict(before_sha=digest, after_sha=actual,
                added_lines=[import_line.rstrip('\n'), init_line.rstrip('\n')],
                normalization='CRLF to LF only', archived_source_verified=True,
                presentation_behavior_changed=True, native_policy_changed=False)
            continue
        if (Path(path).resolve() != current_driver
                or digest != '97d57a9841f43e3c9169ed87a01311aed22f829b641a901d1318e0e499875261'):
            raise ValueError('Closed baseline source/input pin changed: ' + path)
        archives = read(directory/'source-archive.json')['archived']
        matches = [r for r in archives if Path(r['source']).resolve() == current_driver]
        if len(matches) != 1:
            raise ValueError('Exactly one archived baseline driver source is required')
        archived = Path(matches[0]['archive']).resolve()
        if (not archived.is_relative_to((directory/'source-version').resolve())
                or not archived.is_file() or sha(archived) != digest):
            raise ValueError('Archived baseline driver source does not match its original pin')
        before = ast.parse(archived.read_text(encoding='utf-8-sig'))
        after = ast.parse(current_driver.read_text(encoding='utf-8-sig'))
        allowed = {'make_plan', 'load_baseline'}

        def execution_structure(tree):
            functions = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in allowed]
            if sorted(functions) != sorted(allowed):
                raise ValueError('Planner revision must retain exactly the two permitted function definitions')
            retained = [n for n in tree.body if not (isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in allowed)]
            return ast.dump(ast.Module(body=retained, type_ignores=[]), include_attributes=False)

        if execution_structure(before) != execution_structure(after):
            raise ValueError('Planner revision changed native control or another top-level AST node outside the two allowed functions')
        planner_revision = dict(before_sha=digest, after_sha=actual,
            only_functions=['make_plan', 'load_baseline'], archived_source_verified=True)
    result = read(directory/'result.json')
    intervals = result.get('intervals', [])
    if (not isinstance(intervals, list) or not intervals or len(intervals) > 5
            or any(not integer(t, 251, 255) for t in intervals)):
        raise ValueError('Malformed bounded baseline interval history')
    boundaries = {turn: read(directory/('boundary-'+str(turn)+'.json')) for turn in intervals}
    bundle = dict(result=result, preferences=read(directory/'preferences-restored.json'),
        closed=read(directory/'session-closed.json'), inventory=read(directory/'final-inventory.json'),
        initial=read(directory/'source-loaded.json'), payload=read(directory/'boundary-native.json'),
        frozen=read(directory/'extension/trace-counts.json')['snapshot'], config=read(directory/'extension-config.json'),
        installed=read(directory/'installed-before.json'), dependencies=read(directory/'dependency-pins.json'),
        pins=pins, save_sha256=read(directory/'session-load-input.json')['sha256'],
        decision=boundaries[intervals[-1]], prefix=boundaries, planner_revision=planner_revision, controller_revision=controller_revision)
    make_plan(bundle)
    return bundle


def foundation(value):
    return [r for r in value['target']['districts'] if r['type'] == DISTRICT]


def outcome(value, plan):
    districts = foundation(value)
    if len(districts) > 1:
        raise RuntimeError('Unexpected duplicate OnePerCity Quarter')
    if not districts:
        return 'unfounded'
    district = districts[0]
    if district['plot'] != plan['preferred']['plot']:
        return 'different_site'
    return 'completed_preferred' if district['complete'] is True else 'founded_preferred'


def run(args):
    output = args.output.resolve()
    if output.exists():
        raise ValueError('New output directory required; no replay')
    expected_directory = Path.home()/'Documents/My Games/Sid Meier\'s Civilization VI/Saves/Single'
    if (args.native_directory.resolve() != expected_directory.resolve()
            or args.source.resolve().parent != args.native_directory.resolve()
            or args.source.suffix != '.Civ6Save' or sha(args.source) != SAVE_SHA):
        raise ValueError('Require exact native My Games/Saves/Single source with declared hash')
    if native_inventory():
        raise RuntimeError('Foreign native/Tuner owner; preserve it')
    reference = load_baseline(args.baseline) if args.mode == 'treatment' else None
    plan = make_plan(reference) if reference else None
    if args.plan and (plan is None or read(args.plan) != plan):
        raise ValueError('Supplied plan differs from the qualified deterministic baseline plan')
    spec = read(args.spec); spec['path'] = str(args.dll.resolve()); validate_spec(spec)
    if sha(args.dll) != DLL_SHA:
        raise ValueError('Wrong native binary')
    from quarter_placement_trial.daemon import NativeExtension
    output.mkdir(parents=True)
    if plan:
        write_json(output/'plan.json', plan)
    installed = manifest(args.installed); dependencies = manifest(args.dependencies)
    if reference and (reference['installed'] != installed or reference['dependencies'] != dependencies):
        raise ValueError('Treatment package/dependencies differ from the baseline')
    reader = HERE/'source_snapshot.lua'
    code = reader.read_text(encoding='utf-8')
    for token, literal in [('__PLAYER__', str(PLAYER)), ('__CITY__', str(CITY)), ('__DISTRICT__', json.dumps(DISTRICT))]:
        if code.count(token) != 1:
            raise ValueError('Reader literal substitution contract changed')
        code = code.replace(token, literal)
    files = [args.binary, args.dll, args.source, args.script, args.spec, reader]
    if args.plan:
        files.append(args.plan)
    files += [p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py', '.js', '.c', '.lua')]
    files += [Path(m.__file__) for m in list(sys.modules.values()) if getattr(m, '__file__', None)
              and Path(m.__file__).suffix == '.py' and Path(m.__file__).is_relative_to(ROOT/'project/tools')]
    files += list((ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'))
    pins = {str(p.resolve()): sha(p) for p in files}
    write_json(output/'source-pins.json', pins)
    write_json(output/'source-archive.json', archive_sources(pins, output/'source-version'))
    write_json(output/'installed-before.json', installed); write_json(output/'dependency-pins.json', dependencies)
    write_json(output/'protocol.json', dict(mode=args.mode, source_turn=250, maximum_endpoint=255 if args.mode == 'baseline' else 260,
        loads=1, fresh_worlds=0, profile=PROFILE, maxChanges=128, maxRecords=512,
        baseline_stop='first native Best call or five normal one-turn intervals; no forced category event',
        scope='mechanism only; no economic quality or benefit claim', historical_world_reproduction=False,
        no_forced_orders=True, no_prerequisite_grants=True, no_queue_clearing=True, no_assistance=True,
        epoch_scope='one immutable single-load window, not a native generation API',
        disabling_is_rollback=False, treated_autosaves_are_clean_reference=False))
    controller = make_probe_controller(output, user_root=args.user_root)
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = controller.allow_observer_congress_review = True
    controller.study_endpoint = 255 if args.mode == 'baseline' else 260
    session = NativeSession(output, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    extension = None; attempted = False; initial = None; error = None; logs = {}; intervals = []; states = []; coverage = None
    decision_turn = None; prefix_checks = []

    def verify():
        if manifest(args.installed) != installed or manifest(args.dependencies) != dependencies:
            raise RuntimeError('Frozen installed content or dependencies changed; preserve edits')
        if any(sha(path) != digest for path, digest in pins.items()):
            raise RuntimeError('Frozen source or input changed')

    def capture(label):
        value = parse(controller.cmd(code, 'GameCore_Tuner', label, wait=35))
        write_json(output/(label+'.json'), value)
        return value

    def gate():
        nonlocal initial
        initial = capture('source-loaded'); validate_source(initial); verify()
        if reference and initial != reference['initial']:
            raise ValueError('Treatment source facts differ from the closed baseline')
        return True

    def copy_logs(label):
        destination = output/'logs'/label; destination.mkdir(parents=True)
        for name, baseline in logs.items():
            path = args.user_root/'Logs'/name
            if name in REQUIRED_LOGS and not path.exists():
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
        session.load_once(args.source, sha256=SAVE_SHA, native_directory=args.native_directory, turn=250,
            contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'), eligibility=gate)
        config = make_config(initial, args.mode, plan)
        write_json(output/'native-spec.json', spec); write_json(output/'extension-config.json', config)
        proof = prove_loaded_module(session.owner, spec, output/'loaded-module.json')
        extension = NativeExtension(output/'extension', session.owner, script=args.script, spec=output/'native-spec.json',
            config=output/'extension-config.json', dependencies=args.dependencies, loaded_module=output/'loaded-module.json')
        attempted = True; extension.attach_disabled()
        if capture('source-attached-disabled') != initial:
            raise RuntimeError('Disabled attachment changed source facts')
        for name in LOGS:
            logs[name] = capture_log_baseline(args.user_root/'Logs'/name)
        write_json(output/'source-gate.json', dict(verified=True, turn=250, current_content_rebase=True,
            clean_AI_reset=True, original_humans=initial['currentHumans'], source_identity=proof))
        verify(); extension.start()
        for turn in range(251, 256 if args.mode == 'baseline' else 261):
            controller.play(turn); intervals.append(turn)
            value = capture('boundary-'+str(turn))
            if value['turn'] != turn or value['target'].get('human') is not False:
                raise RuntimeError('Wrong inactive boundary or target role changed')
            validate_reset(value)
            if plan and turn < plan['decisionTurn']:
                expected = reference['prefix'].get(turn)
                matches = expected is not None and value == expected
                prefix_checks.append(dict(turn=turn, matched=matches,
                    differingSections=[] if matches else sorted(k for k in set(value) | set(expected or {}) if value.get(k) != (expected or {}).get(k))))
                write_json(output/'prefix-parity.json', prefix_checks)
                if not matches:
                    write_json(output/'prefix-parity-limit.json', dict(turn=turn, scientific_limit=True, no_automatic_replay=True))
                    raise RuntimeError('Pre-decision physical source prefix differs from the baseline; stop without a forced event')
            payload, saturated = extension.snapshot('turn-'+str(turn))
            coverage = validate_snapshot(payload, config)
            if saturated:
                raise RuntimeError('Native trace saturated; no complete candidate-policy claim')
            write_json(output/('native-'+str(turn)+'.json'), payload)
            write_json(output/'boundary-native.json', payload)
            copy_logs('turn-'+str(turn)); verify()
            status = outcome(value, plan) if plan else ('existing_foundation' if foundation(value) else 'unfounded')
            states.append(dict(turn=turn, status=status, districts=foundation(value), queue=value['target']['queue'], coverage=coverage, changed=payload['stats']['changed']))
            write_json(output/'follow-through.json', states)
            if args.mode == 'baseline' and coverage['best'] > 0:
                decision_turn = turn
                break
            if plan and status in ('different_site', 'completed_preferred'):
                break
        write_json(output/'observation-result.json', dict(mode=args.mode, initial=initial, final=value, coverage=coverage,
            states=states, preferred_site=plan['preferred'] if plan else None,
            preferred_foundation_observed=any(s['status'] in ('founded_preferred', 'completed_preferred') for s in states),
            preferred_completion_observed=any(s['status'] == 'completed_preferred' for s in states),
            wrong_site_observed=any(s['status'] == 'different_site' for s in states),
            queue_evidence='Exact native logs archived separately; an item-only queue getter does not prove its placement coordinates',
            changed_choice_proven=False, economic_benefit_proven=False, rollback_claimed=False))
    except BaseException as failure:
        error = failure
        write_json(output/'failure.json', dict(error=str(failure), traceback=traceback.format_exc(), no_automatic_replay=True))
    finally:
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda: restore_preferences(controller, output) if (output/'original-preferences.json').exists() else None,
                    restore_package=verify, before_menu=freeze,
                    after_native_exit=extension.after_native_exit if extension and getattr(extension, 'process', None) is not None else lambda: None)
                if logs:
                    copy_logs('closed')
            except BaseException as failure:
                write_json(output/'cleanup-failure.json', dict(error=str(failure), traceback=traceback.format_exc(), original_error=str(error)))
                if error is None:
                    error = failure
        verify(); write_json(output/'final-inventory.json', native_inventory())
    if error is not None:
        raise error
    if not session.closed:
        raise RuntimeError('Native session remains unclosed')
    # Cleanup permits diagnostic faults so that the native process can still
    # close normally. Scientific success additionally requires clean final data.
    try:
        final_counts = read(output/'extension/trace-counts.json')['snapshot']
        validate_snapshot(final_counts, config, frozen=True)
        daemon_exit = read(output/'extension/trace-daemon-exit.json')
        if daemon_exit.get('diagnostic_fault') is not False:
            raise RuntimeError('Late extension diagnostic fault; closed session is not a successful observation')
    except BaseException as failure:
        write_json(output/'post-close-validation-failure.json', dict(error=str(failure), traceback=traceback.format_exc(), closed=True))
        raise
    result = dict(profile=PROFILE, mode=args.mode, closed=True, native_exit_code=0, intervals=intervals, coverage=coverage,
        save_unchanged=sha(args.source) == SAVE_SHA, installed_unchanged=manifest(args.installed) == installed,
        preferences_restored=read(output/'preferences-restored.json').get('verified') is True,
        source_save_sha256=SAVE_SHA, mechanism_test=True, efficacy_test=False, mutation_rollback_claimed=False,
        final_status=states[-1]['status'], decisionTurn=decision_turn if args.mode == 'baseline' else plan['decisionTurn'])
    write_json(output/'result.json', result)
    print(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'source', 'native-directory', 'binary', 'dll', 'user-root', 'installed', 'dependencies', 'spec', 'script', 'baseline', 'plan'):
        parser.add_argument('--'+name, type=Path)
    parser.add_argument('--mode', choices=('baseline', 'treatment'))
    parser.add_argument('--plan-only', type=Path, help='Export a new qualified plan file without native operations')
    args = parser.parse_args()
    if args.plan_only:
        if not args.baseline or args.plan_only.exists():
            parser.error('--plan-only requires a closed --baseline and a new output file')
        plan = make_plan(load_baseline(args.baseline)); write_json(args.plan_only, plan); print(json.dumps(plan)); return
    required = ('output', 'source', 'native_directory', 'binary', 'dll', 'user_root', 'installed', 'dependencies', 'spec', 'script', 'mode')
    if any(getattr(args, key) is None for key in required) or (args.mode == 'treatment' and args.baseline is None):
        parser.error('A run requires every native path and explicit mode; treatment also requires --baseline')
    run(args)


if __name__ == '__main__':
    main()
