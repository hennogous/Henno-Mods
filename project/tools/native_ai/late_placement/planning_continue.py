"""Continue an unchanged, preselected planning game from a verified checkpoint.

This is shared-controller lifecycle glue, not AI policy. It restores exact
package bytes, loads once through NativeSession, compares structural game facts
before playing, and installs passive observers. A continuation is never counted
as another fresh seed. Importing this module launches/connects to nothing.
"""
import argparse
from collections import Counter
from contextlib import nullcontext
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace
import traceback

from driver import (HERE, HOTFIX_SHA, HeldProcess, NativeSession, configure, flags,
                    launch, load, lua, make_probe_controller, manifest, native_inventory,
                    parse, read, require, restore_preferences, sha, write_json)
from ce_bakers_fresh import (LOGS, MAPS, capture_census, check_native_status,
                            package_identity, passive_publisher, summarize_run, untuned_manifest)
from ce_replay import DLL, STEAM_26595377_CORE_SHA, native_profile, verify_modules
from full_game_controller.checkpoint import SaveFileUnavailable, SavePermissionUnavailable, save_inactive_boundary
from full_game_controller.environment import archive_sources


STRUCTURAL_FIELDS = {'PLAYER': None, 'CITY': 3, 'QUARTER': 7,
                     'PRODUCER': None, 'SERVICE_BUILDING': None, 'MATERIAL': None,
                     'CUSTOMER_HOST': None, 'CUSTOMER': None, 'SALES': None}
IGNORED_CENSUS_FIELDS = {'TREASURY', 'ADJACENCY', 'POPULATION_EXCHANGE', 'END'}


def structural_rows(census):
    """Canonical multiset; exclude only documented yield/transient columns.

    CITY retains population, QUARTER retains completion/pillage/river. Quarter
    effect properties and city output are recalculated by Lua/UI and are not
    load-equivalence proofs. Unknown row types are an error, never silently
    discarded. Duplicate rows count, so Counter comparison cannot hide losses.
    """
    rows = []
    for kind, payload in census['rows']:
        if kind in IGNORED_CENSUS_FIELDS:
            continue
        require(kind in STRUCTURAL_FIELDS, 'Unknown structural census kind: ' + kind)
        fields = payload.split('\t')
        limit = STRUCTURAL_FIELDS[kind]
        require(limit is None or len(fields) >= limit, 'Short structural census row: ' + kind)
        rows.append((kind, *fields[:limit]))
    return Counter(rows)


def parse_census(raw, turn):
    rows = re.findall(r'CSC_ENDPOINT_([A-Z_]+)\t([^\r\n]+)', raw)
    footer = [payload.split('\t') for kind, payload in rows if kind == 'END']
    data = [(kind, payload) for kind, payload in rows if kind != 'END']
    require(footer == [[str(turn), str(len(data))]], 'Incomplete continuation source census')
    return dict(turn=turn, phase='loaded-inactive-boundary', rows=data)


def compare_structure(expected, actual):
    require(expected['turn'] == actual['turn'], 'Structural census clocks differ')
    before, after = structural_rows(expected), structural_rows(actual)
    return dict(verified=before == after, expected_rows=sum(before.values()),
                actual_rows=sum(after.values()),
                missing=[dict(row=list(row), count=count) for row, count in (before-after).items()],
                unexpected=[dict(row=list(row), count=count) for row, count in (after-before).items()],
                ignored_kinds=sorted(IGNORED_CENSUS_FIELDS),
                retained_partial_columns={'CITY': 3, 'QUARTER': 7})


def digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def stock_archive_manifest(pristine, root, original):
    """Derive the exact passive benchmark package from its pinned original."""
    metadata, = pristine.glob('*.modinfo')
    publisher = Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua')
    replacements = {
        metadata.name: untuned_manifest(root, keep_observer_context=True),
        str(publisher): passive_publisher((pristine/publisher).read_bytes()),
    }
    return original | {name: dict(sha256=hashlib.sha256(data).hexdigest(), size=len(data))
                       for name, data in replacements.items()}


def source_lifecycle_verified(source):
    """Accept a supported close or separately verified interruption cleanup.

    An abruptly lost process has no known exit code. Never fabricate its
    session-closed receipt to satisfy continuation. A new menu-only session
    can restore the exact preferences and archive unchanged installed packages;
    its own clean-close receipt and original-source identity qualify recovery.
    World eligibility still comes from the saved checkpoint/structural gate.
    """
    source = Path(source).resolve()
    closed = source/'session-closed.json'
    try:
        if load(closed).get('verified'):
            return True
    except FileNotFoundError:
        pass
    path = source/'interruption-reconciled.json'
    if not path.is_file():
        return False
    record = load(path)
    cleanup = source/'interruption-cleanup/session-closed.json'
    return (record.get('verified') is True and record.get('original_exit_unknown') is True
            and record.get('owners_absent') is True and record.get('preferences_verified') is True
            and record.get('source') == str(source)
            and record.get('source_sha256') == sha(source/'source.json')
            and cleanup.is_file() and load(cleanup).get('verified') is True)


@dataclass
class ContinuationPlan:
    source: Path
    output: Path
    at: int
    through: int
    dependencies: Path | None
    protocol: dict
    identity: dict
    checkpoint: dict
    expected_census: dict
    packages: list
    extras: dict
    binary: Path
    user_root: Path
    saves: Path


def prepare(source, output, at, through, dependencies, *, read_only=False, material_only=False,
            finish_port_replay=False, observe_material=False, stock_derived=False):
    """Read and qualify all provenance before any install, launch or console.

    The failed run may have failure.json or an abrupt exit: supported closure
    or separate verified interruption cleanup is required. Original normal setup and unchanged
    package/checkpoint identities remain mandatory.
    """
    source, output = Path(source).resolve(strict=True), Path(output).resolve()
    dependencies = Path(dependencies).resolve(strict=True) if dependencies is not None else None
    require(not output.exists() and source.is_dir(), 'New continuation output required')
    # Read-only diagnostics may reuse the exact checkpoint without advancing
    # its clock. The ordinary continuation route keeps its original strict
    # forward window. Neither mode relaxes source/save/package qualification.
    typed=type(at)is int and type(through)is int
    window=typed and(0<at==through<=250 if read_only else 0<at<through<=250)
    # A read-only source inspection may use any regular archived checkpoint,
    # including100/150. Playing continuations retain their qualified endpoints.
    endpoint_ok = at in (50, 100, 150, 200, 250) if read_only else through in (50, 200, 250)
    if observe_material:
        require(material_only and (at, through) in ((100, 175), (150, 155)),
                'Axum trace needs a qualified Continents checkpoint and replay window')
        endpoint_ok = True
    require(typed and at % 25 == 0 and window and endpoint_ok, 'Unsupported continuation window')
    require(not stock_derived or (read_only and dependencies is None),
            'Stock-derived fixtures require an explicit controller-only source inspection')
    require(source_lifecycle_verified(source) and
            load(source/'preferences-restored.json')['verified'], 'Source did not close/restore cleanly')
    protocol, identity = load(source/'protocol.json'), load(source/'source.json')
    # A same-turn inspection or a material-only recovery uses the gameplay
    # census independently of treasury instrumentation. A savings continuation
    # still requires matching original savings capture.
    no_savings = read_only or material_only
    require(all(protocol.get(k) is True for k in ('fresh_game', 'ordinary_setup',
            'harmonised_observation', 'planning_observation')) and
            (no_savings or protocol.get('passive_savings_observation') is True) and
            (not material_only or protocol.get('passive_savings_observation') is False) and
            protocol.get('untuned') is stock_derived and
            all(protocol.get(k) is False for k in ('external_policy', 'gameplay_interventions')) and
            not any(k.startswith('diagnostic_') and v for k, v in protocol.items()),
            'Require an ordinary stock benchmark' if stock_derived else
            'Require an ordinary original game with integrated main CSC policy only')
    if stock_derived:
        from later_stage_results import verify_policy
        verify_policy(load(source/'native-endpoint.json'), load(source/'loaded-native-customer-database.json'),
                      load(source/'ai-processing-time.json'), untuned=True)
    require(protocol['map'] in MAPS and
            all(type(protocol[k]) is int for k in ('map_seed', 'game_seed')),
            'Missing original preselected map identity')
    players = identity['original_ai']
    require(players == [1, 2, 3, 4, 5] and len(identity['map_signature']) == 3 and
            {r['player'] for r in identity['starts']} == set(players) | {0},
            'Missing original roster/map provenance')
    checkpoint_path = source/('checkpoint-'+str(at)+'.json')
    # Fresh-game drivers name the final receipt checkpoint.json; intermediate
    # boundaries use checkpoint-N.json. Both still require exact turn/save hashes.
    if at == 250 and not checkpoint_path.is_file():
        checkpoint_path = source/'checkpoint.json'
    checkpoint = load(checkpoint_path)
    require(checkpoint['verified'] and checkpoint['turn'] == at and
            sha(Path(checkpoint['native_save'])) == checkpoint['sha256'] == sha(Path(checkpoint['archive'])),
            'Checkpoint native/archive hash mismatch')
    expected = load(source/('full-census-'+str(at)+'.json'))
    require(expected['turn'] == at and structural_rows(expected), 'Missing structural checkpoint census')
    saves = Path(checkpoint['native_save']).resolve(strict=True).parent
    require(Path(checkpoint['archive']).resolve().parent == source and
            Path(checkpoint['native_save']).suffix == '.Civ6Save', 'Unexpected checkpoint locations')
    packages, originals = [], {}
    for path, item in load(source/'packages.json').items():
        package, install = Path(path).resolve(strict=True), Path(item['install']).resolve()
        require(not install.exists(), 'Frozen package/install differs: '+path)
        identity_id, root = package_identity(package)
        role = 'ce' if (package/'Binaries/Win64'/DLL).is_file() else 'csc'
        require(identity_id == protocol[role], 'Package role/identity differs')
        originals[role] = manifest(package)
        if stock_derived and role == 'csc':
            # Preserve both the original input digest and the exact dormant
            # publisher/SQL withholding bytes loaded in the stock world.
            expected = stock_archive_manifest(package, root, originals[role])
            package = (source/install.name).resolve(strict=True)
            require(package.parent == source and expected == item['files'] == manifest(package),
                    'Archived stock CSC package differs from the measured control')
        else:
            require(originals[role] == item['files'], 'Frozen package/install differs: '+path)
        packages.append(dict(source=package, install=install, files=item['files'], id=identity_id, role=role))
    require(len(packages) == 2 and {p['role'] for p in packages} == {'ce', 'csc'} and
            len({p['install'].parent for p in packages}) == 1, 'Expected separate CE/CSC development packages')
    by_role = {p['role']: p for p in packages}
    require([digest(originals[k]) for k in ('ce', 'csc')] == protocol['input_digests'],
            'Original package digests differ')
    _, csc_manifest = package_identity(by_role['csc']['source'])
    optional=csc_manifest.find("ActionCriteria/Criteria[@id='CSC_CE_SupplierExclusion']/ModInUse")
    # Main CSC keeps CE optional. Qualify that specific gate for the original
    # material setup, then still require live capability and package parity.
    optional_ce=no_savings and optional is not None and optional.text==protocol['ce']
    require(csc_manifest.find("Dependencies/Mod[@id='"+protocol['ce']+"']") is not None or optional_ce,
            'CSC no longer depends on the recorded CE package')
    extras = load(source/'extra-mods.json')
    # The Government-screen regression adds the pinned BRS/EPC UI pair. A
    # zero-turn survey must reload that original stack, never silently drop it.
    # Playing continuations retain their qualified three-gameplay-mod contract.
    ui_pair = {'6f2888d4-79dc-415f-a8ff-f9d81d7afb53', '382a187f-c8ba-4094-a6a7-0d5315661f33'}
    extra_count_ok = len(extras) == 3 or (no_savings and len(extras) == 5 and ui_pair <= set(extras))
    require(extra_count_ok and set(extras) == set(protocol['extra_mods']), 'Expected exact original optional packages')
    for mod_id, item in extras.items():
        package = Path(item['path']).resolve(strict=True)
        require(package_identity(package)[0] == mod_id and manifest(package) == item['files'] and
                digest(item['files']) == protocol['extra_mods'][mod_id]['digest'] and
                package == Path(protocol['extra_mods'][mod_id]['path']).resolve(), 'Optional package changed: '+mod_id)
    binary = Path(load(source/'launch-bootstrap.json')['binary']).resolve(strict=True)
    executable_sha, core_sha = native_profile(binary)
    loaded = load(source/'loaded-modules.json')
    original_core_sha = protocol.get('native_profile', {}).get('gamecore_sha256', HOTFIX_SHA)
    if finish_port_replay:
        # The old save is an input fixture for an explicit port test. Recheck
        # its structure after loading, and qualify the new live DLL separately.
        require(read_only and at == through and dependencies is None
                and original_core_sha == HOTFIX_SHA and core_sha == STEAM_26595377_CORE_SHA,
                'The finishing port replay requires the exact older fixture and updated Steam pair')
    else:
        require(core_sha == original_core_sha, 'Original DX11/XP2 build differs')
        if 'native_profile' in protocol:
            require(protocol['native_profile']['executable_sha256'] == executable_sha, 'Original DX11 build differs')
    require(dependencies is None or core_sha == HOTFIX_SHA, 'Native diagnostics need their own relocation audit')
    require(loaded['GameCore_XP2_FinalRelease.dll']['sha256'] == original_core_sha and
            sha(Path(loaded['GameCore_XP2_FinalRelease.dll']['path'])) == core_sha and
            loaded[DLL]['sha256'] == sha(by_role['ce']['source']/'Binaries/Win64'/DLL),
            'Original XP2/CE binary identities differ')
    database = Path(load(source/'resource-stack-preflight.json')['database'])
    require(database.name == 'DebugGameplay.sqlite' and database.parent.name == 'Cache', 'Unknown user-root evidence')
    user_root = database.parent.parent.resolve(strict=True)
    mods = packages[0]['install'].parent
    require(not any(p.is_relative_to(mods) for p in (output, source, *(p['source'] for p in packages))),
            'Continuation staging/output must stay outside installed Mods')
    # A read-only source preparation may feed a controller-only diagnostic.
    # Playing continuations and callers supplying a dependency directory keep
    # the existing Frida check for their native instrumentation.
    require(not material_only or dependencies is None, 'Material-only recovery does not attach a savings observer')
    require((no_savings and dependencies is None) or
            (dependencies is not None and (dependencies/'frida/__init__.py').is_file()),
            'Existing Frida dependencies missing')
    return ContinuationPlan(source, output, at, through, dependencies, protocol, identity,
                            checkpoint, expected, packages, extras, binary, user_root, saves)


def enable(session, identity):
    session.issue_once('enable-'+identity, """
local chosen
for _,m in ipairs(Modding.GetInstalledMods())do
 if m.Id=='__ID__'then assert(not chosen);chosen=m end
end
assert(chosen and Modding.CanEnableMod(chosen.Handle)=='OK')
Modding.EnableMod(chosen.Handle,true)
""".replace('__ID__', identity), 'MainMenu')
    session.wait_context('MainMenu', 90)


def run(args, *, material_observer=None, material_observer_start=None):
    material_only = getattr(args, 'material_only', False)
    plan = prepare(args.source, args.output, args.at, args.through, args.dependencies,
                   material_only=material_only, observe_material=material_observer is not None)
    require(material_observer_start is None or
            (material_observer is not None and plan.at < material_observer_start < plan.through),
            'Deferred material observer must start inside its replay window')
    from economy_component_probe import targets,capture
    component_targets=targets(getattr(args,'component_target',None)or[])
    require(not material_only or not component_targets, 'Material recovery keeps ordinary integrated observations')
    require(not native_inventory(), 'Foreign native/Tuner owner; preserve it')
    out = plan.output
    out.mkdir(parents=True)
    by_role = {p['role']: p for p in plan.packages}
    protocol = dict(plan.protocol, fresh_game=False, ordinary_setup=False,
                    natural_continuation=True, continuation_start=plan.at, endpoint=plan.through,
                    original_source=str(plan.source), source_checkpoint_sha256=plan.checkpoint['sha256'])
    for name, data in [('protocol.json', protocol), ('source.json', plan.identity),
                       ('extra-mods.json', plan.extras), ('packages.json', {
                           str(p['source']): dict(install=str(p['install']), files=p['files']) for p in plan.packages})]:
        write_json(out/name, data)
    write_json(out/'continuation.json', dict(source=str(plan.source), at=plan.at, through=plan.through,
        source_checkpoint=plan.checkpoint, original_map=plan.protocol['map'],
        map_seed=plan.protocol['map_seed'], game_seed=plan.protocol['game_seed'],
        new_seed=False, fixture=False, gameplay_interventions=False, material_only=material_only,
        limits=['Reload resets transient native caches and observer identity bindings.',
                'Only the continuation segment is measured here; parent evidence must be joined explicitly.',
                'No assumption of uninterrupted RNG/decision identity with the stalled segment.']))
    sources = [Path(__file__), HERE/'ce_bakers_fresh.py', HERE/'full_game_observation.py',
               HERE/'full_game_census.lua', HERE/'full_game_preflight.lua', HERE/'planning_observer.lua',
               HERE/'quarter_placement_watch.lua', HERE/'district_adjacency_watch.lua', HERE/'customer_placement_watch.lua',
               HERE/'storekeeper_runtime.py', HERE/'storekeeper_runtime.lua',
               HERE/'economy_savings_watch.py', HERE/'economy_savings_watch.js',
               *sorted((HERE.parents[1]/'ai_baseline/full_game_controller').glob('*.py')),
               *sorted((HERE.parents[1]/'ai_baseline/full_game_controller').glob('*.lua'))]
    if component_targets:
        sources.extend([HERE/'economy_component_probe.lua',HERE/'economy_component_probe.py'])
    pins = {str(p.resolve()): sha(p) for p in sources}
    write_json(out/'implementation-pins.json', pins)
    write_json(out/'implementation-archive.json', archive_sources(pins, out/'implementation-version'))
    shutil.copyfile(Path(__file__), out/Path(__file__).name)
    controller = make_probe_controller(out, user_root=plan.user_root)
    controller.study_endpoint = plan.through
    controller.autoplay_interval_seconds = plan.protocol['interval_minutes']*60
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    copied, watch, checkpoint, autosave_receipt = [], None, None, None

    def verify_packages():
        for p in plan.packages:
            require(manifest(p['source']) == p['files'], 'Frozen package changed during continuation')
        for p in copied:
            require(manifest(p['install']) == p['files'], 'Installed package changed during continuation')
        for item in plan.extras.values():
            require(manifest(Path(item['path'])) == item['files'], 'Optional package changed during continuation')
        require(all(sha(Path(path)) == value for path, value in pins.items()), 'Executed observer/controller source changed')

    def source_gate():
        roster = {r['player']: r['leader'] for r in plan.identity['starts']}
        code = 'local leaders='+lua(roster)+'\n'+f"""
assert(Game.GetCurrentGameTurn()=={plan.at} and Players[0]:IsHuman())
assert(GameInfo.CSC_AI_Profile==nil,'Legacy policy loaded')
assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT,'Missing integrated native connector')
for pid,leader in pairs(leaders)do
 assert(PlayerConfigurations[pid]:GetLeaderTypeName()==leader,'Changed original leader')
 if pid~=0 then assert(not Players[pid]:IsHuman())end
end
local speed=GameConfiguration.GetGameSpeedType()
assert(speed=='GAMESPEED_ONLINE' or GameInfo.GameSpeeds[speed].GameSpeedType=='GAMESPEED_ONLINE')
local width,height=Map.GetGridSize()
print('CSC_CONTINUATION_GRID=['..width..','..height..']')
print('CSC_CONTINUATION_NATIVE='..CE_AIDistrictScoresStatus())
"""
        raw = controller.cmd(code, 'CSC_AI_BakersGameplay', 'continuation-source-identity')
        require(parse(raw, 'CSC_CONTINUATION_GRID') == plan.identity['map_signature'][:2], 'Changed loaded map dimensions')
        native = parse(raw, 'CSC_CONTINUATION_NATIVE')
        check_native_status(native, False)
        scope = 'CSC_ENDPOINT_PLAYERS='+lua(plan.identity['original_ai'])+'\nCSC_ENDPOINT_EXPECTED_TURN='+str(plan.at)+'\n'
        raw = controller.cmd(scope+read(HERE/'full_game_census.lua'), 'CSC_AI_BakersGameplay', 'continuation-source-census')
        (out/'source-census.txt').write_text(raw, encoding='utf-8')
        actual = parse_census(raw, plan.at)
        write_json(out/'source-full-census.json', actual)
        proof = compare_structure(plan.expected_census, actual)
        write_json(out/'source-structure-comparison.json', proof)
        require(proof['verified'], 'Loaded continuation structure differs; inspect comparison before retry')
        return True

    try:
        for p in plan.packages:
            shutil.copytree(p['source'], p['install'])
            copied.append(p)
        verify_packages()
        session.start(lambda: launch(SimpleNamespace(binary=plan.binary), out))
        session.wait_context('MainMenu')
        configure(controller, out, csc_id=plan.protocol['ce'])
        enable(session, plan.protocol['csc'])
        for mod_id in plan.extras:
            enable(session, mod_id)
        require({k for k, v in flags(controller, 'verify-continuation-packages')['mods'].items() if v} ==
                {plan.protocol['ce'], plan.protocol['csc'], *plan.extras}, 'Expected exact original packages')
        session.load_once(plan.checkpoint['native_save'], sha256=plan.checkpoint['sha256'],
                          native_directory=plan.saves, turn=plan.at,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AI_BakersGameplay', 'CSC_AdjacencyGameplay'),
                          eligibility=source_gate)
        core_sha = plan.protocol.get('native_profile', {}).get('gamecore_sha256', HOTFIX_SHA)
        verify_modules(session, by_role['ce']['install']/'Binaries/Win64'/DLL, out, core_sha)
        raw = controller.cmd('CSC_BAKERS_STOREKEEPER_WATCH=true\n'+read(HERE/'storekeeper_runtime.lua'),
                             'PlotInfo', 'install-continuation-storekeeper-watch')
        require('CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED' in raw, 'Storekeeper watch not installed')
        from full_game_observation import archive_endpoint_autosave, install, play, finish
        install(controller, out, plan.identity['original_ai'], plan.user_root, plan.through,
                planning=True, extra_mods=plan.extras, csc_path=by_role['csc']['install'],start=plan.at,
                service_watch=plan.protocol.get('service_observation',False))
        if not material_only:
            from economy_savings_watch import EconomySavingsWatch
            for name in ('economy_savings_watch.py', 'economy_savings_watch.js'):
                shutil.copyfile(HERE/name, out/name)
            indices = [int(v) for v in re.findall(r'CSC_DISTRICT_CATALOGUE\t(\d+)\t', read(out/'loaded-district-catalogue.txt'))]
            require(indices, 'Missing loaded district catalogue')
            modules = load(out/'loaded-modules.json')
            width, height = plan.identity['map_signature'][:2]
            watch = EconomySavingsWatch(directory=plan.dependencies, binary=modules['GameCore_XP2_FinalRelease.dll']['path'],
                                        output=out, start=plan.at, through=plan.through, write=write_json,
                                        players=plan.identity['original_ai'], width=width, height=height, districts=max(indices)+1,
                                        capture_placement=True)
            watch.attach(session.owner, modules)
        if component_targets:
            capture(controller,out,component_targets,plan.at)
        start = plan.at
        if material_observer_start is not None:
            # Qualify initial playback while no Frida callbacks are present.
            # Keep the ordinary passive observation installed across both phases.
            from full_game_observation import observe_inactive_storekeeper
            start = material_observer_start
            controller.play(start)
            write_json(out/'material-observer-baseline.json', dict(turn=start, replay_start=plan.at))
            if not re.search(r'CSC_STOREKEEPER_END\t'+str(start)+r'\t', read(plan.user_root/'Logs/Lua.log')):
                observe_inactive_storekeeper(controller, out, start)
        native_observation = material_observer(session,controller,out) if material_observer else nullcontext()
        with native_observation as worker_boundary:
            if worker_boundary:
                worker_boundary(start)
            boundary_reader = (lambda turn: capture(controller,out,component_targets,turn)) if component_targets else worker_boundary
            play(controller, out, plan.user_root, start=start, endpoint=plan.through, saves=plan.saves, savings=watch,
                 observe_boundary=boundary_reader, step=1 if worker_boundary else 5)
        from economy_preflight import inspect
        inspect(controller, out)
        final = parse(controller.cmd('print("CSC_CONTINUATION_END="..CE_AIDistrictScoresStatus())',
                                     'GameCore_Tuner', 'continuation-end-status'), 'CSC_CONTINUATION_END')
        write_json(out/'native-endpoint.json', final)
        check_native_status(final, False)
        capture_census(controller, set(plan.identity['original_ai']), plan.through, out/'chain-census.txt')
        try:
            checkpoint = save_inactive_boundary(controller, turn=plan.through,
                                                 name='CSC_AI_CONTINUATION_'+str(plan.through),
                                                 native_directory=plan.saves, archive=out/'endpoint.Civ6Save')
        except (SavePermissionUnavailable, SaveFileUnavailable) as error:
            if not material_only:
                raise
            autosave_receipt = archive_endpoint_autosave(out,plan.saves,plan.through,error)
        else:
            write_json(out/'checkpoint.json', checkpoint)
    except Exception as error:
        write_json(out/'failure.json', dict(error=str(error), traceback=traceback.format_exc()))
        raise
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, out)
                          if (out/'original-preferences.json').exists() else None,
                          restore_package=verify_packages,
                          before_menu=lambda: watch.freeze() if watch else None,
                          after_native_exit=lambda: watch.after_exit() if watch else None)
        if watch and not session.closed and (session.owner is None or session.owner.poll() is not None):
            watch.after_exit()
        if session.closed or session.owner is None and not native_inventory():
            for p in copied:
                p['install'].rename(out/p['install'].name)
            if session.closed:
                for name in LOGS:
                    path = plan.user_root/'Logs'/name
                    if path.is_file():
                        shutil.copyfile(path, out/name)
    summarize_run(out, set(plan.identity['original_ai']), plan.at, plan.through, False, checkpoint, [], qualification=False)
    finish(out, plan.through, start=plan.at)
    if autosave_receipt:
        write_json(out/'completed-via-autosave.json', dict(autosave_receipt, native_closed_verified=True))
    if watch:
        watch.qualify()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--dependencies', type=Path)
    parser.add_argument('--material-only', action='store_true',
                        help='Resume the ordinary material test with its original passive observers')
    parser.add_argument('--at', type=int, required=True)
    parser.add_argument('--through', type=int, required=True)
    parser.add_argument('--component-target',nargs=4,action='append',metavar=('PLAYER','CITY','PLOT','QUARTER'),
                        help='Read-only economic component audit; may be repeated up to eight times')
    run(parser.parse_args())


if __name__ == '__main__':
    main()
