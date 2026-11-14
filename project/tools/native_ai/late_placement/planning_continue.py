"""Continue an unchanged, preselected planning game from a verified checkpoint.

This is shared-controller lifecycle glue, not AI policy. It restores exact
package bytes, loads once through NativeSession, compares structural game facts
before playing, and installs passive observers. A continuation is never counted
as another fresh seed. Importing this module launches/connects to nothing.
"""
import argparse
from collections import Counter
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
from ce_bakers_fresh import (LOGS, capture_census, check_native_status,
                            package_identity, summarize_run)
from ce_replay import DLL, HOTFIX_EXE_SHA, verify_modules
from full_game_controller.checkpoint import save_inactive_boundary
from full_game_controller.environment import archive_sources


STRUCTURAL_FIELDS = {'PLAYER': None, 'CITY': 3, 'QUARTER': 7,
                     'PRODUCER': None, 'SERVICE_BUILDING': None, 'MATERIAL': None,
                     'CUSTOMER_HOST': None, 'CUSTOMER': None, 'SALES': None}
IGNORED_CENSUS_FIELDS = {'TREASURY', 'ADJACENCY', 'END'}


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


@dataclass
class ContinuationPlan:
    source: Path
    output: Path
    at: int
    through: int
    dependencies: Path
    protocol: dict
    identity: dict
    checkpoint: dict
    expected_census: dict
    packages: list
    extras: dict
    binary: Path
    user_root: Path
    saves: Path


def prepare(source, output, at, through, dependencies):
    """Read and qualify all provenance before any install, launch or console.

    The failed run may have failure.json: supported closure/restoration, rather
    than completion, is required. Its original normal setup and unchanged
    package/checkpoint identities remain mandatory.
    """
    source, output = Path(source).resolve(strict=True), Path(output).resolve()
    dependencies = Path(dependencies).resolve(strict=True)
    require(not output.exists() and source.is_dir(), 'New continuation output required')
    require(type(at) is int and type(through) is int and at % 25 == 0 and
            0 < at < through <= 250 and through in (50, 200, 250), 'Unsupported continuation window')
    require(load(source/'session-closed.json')['verified'] and
            load(source/'preferences-restored.json')['verified'], 'Source did not close/restore cleanly')
    protocol, identity = load(source/'protocol.json'), load(source/'source.json')
    require(all(protocol.get(k) is True for k in ('fresh_game', 'ordinary_setup',
            'harmonised_observation', 'planning_observation', 'passive_savings_observation')) and
            all(protocol.get(k) is False for k in ('untuned', 'external_policy', 'gameplay_interventions')) and
            not any(k.startswith('diagnostic_') and v for k, v in protocol.items()),
            'Require an ordinary original game with integrated main CSC policy only')
    require(protocol['map'] in ('Continents', 'Pangaea', 'Fractal') and
            all(type(protocol[k]) is int for k in ('map_seed', 'game_seed')),
            'Missing original preselected map identity')
    players = identity['original_ai']
    require(players == [1, 2, 3, 4, 5] and len(identity['map_signature']) == 3 and
            {r['player'] for r in identity['starts']} == set(players) | {0},
            'Missing original roster/map provenance')
    checkpoint = load(source/('checkpoint-'+str(at)+'.json'))
    require(checkpoint['verified'] and checkpoint['turn'] == at and
            sha(Path(checkpoint['native_save'])) == checkpoint['sha256'] == sha(Path(checkpoint['archive'])),
            'Checkpoint native/archive hash mismatch')
    expected = load(source/('full-census-'+str(at)+'.json'))
    require(expected['turn'] == at and structural_rows(expected), 'Missing structural checkpoint census')
    saves = Path(checkpoint['native_save']).resolve(strict=True).parent
    require(Path(checkpoint['archive']).resolve().parent == source and
            Path(checkpoint['native_save']).suffix == '.Civ6Save', 'Unexpected checkpoint locations')
    packages = []
    for path, item in load(source/'packages.json').items():
        package, install = Path(path).resolve(strict=True), Path(item['install']).resolve()
        require(manifest(package) == item['files'] and not install.exists(), 'Frozen package/install differs: '+path)
        identity_id, root = package_identity(package)
        role = 'ce' if (package/'Binaries/Win64'/DLL).is_file() else 'csc'
        require(identity_id == protocol[role], 'Package role/identity differs')
        packages.append(dict(source=package, install=install, files=item['files'], id=identity_id, role=role))
    require(len(packages) == 2 and {p['role'] for p in packages} == {'ce', 'csc'} and
            len({p['install'].parent for p in packages}) == 1, 'Expected separate CE/CSC development packages')
    by_role = {p['role']: p for p in packages}
    require([digest(by_role[k]['files']) for k in ('ce', 'csc')] == protocol['input_digests'],
            'Original package digests differ')
    _, csc_manifest = package_identity(by_role['csc']['source'])
    require(csc_manifest.find("Dependencies/Mod[@id='"+protocol['ce']+"']") is not None,
            'CSC no longer depends on the recorded CE package')
    extras = load(source/'extra-mods.json')
    require(len(extras) == 3 and set(extras) == set(protocol['extra_mods']), 'Expected exact original three optional packages')
    for mod_id, item in extras.items():
        package = Path(item['path']).resolve(strict=True)
        require(package_identity(package)[0] == mod_id and manifest(package) == item['files'] and
                digest(item['files']) == protocol['extra_mods'][mod_id]['digest'] and
                package == Path(protocol['extra_mods'][mod_id]['path']).resolve(), 'Optional package changed: '+mod_id)
    binary = Path(load(source/'launch-bootstrap.json')['binary']).resolve(strict=True)
    require(sha(binary) == HOTFIX_EXE_SHA, 'Changed DX11 executable')
    loaded = load(source/'loaded-modules.json')
    require(loaded['GameCore_XP2_FinalRelease.dll']['sha256'] == HOTFIX_SHA and
            sha(Path(loaded['GameCore_XP2_FinalRelease.dll']['path'])) == HOTFIX_SHA and
            loaded[DLL]['sha256'] == sha(by_role['ce']['source']/'Binaries/Win64'/DLL),
            'Original XP2/CE binary identities differ')
    database = Path(load(source/'resource-stack-preflight.json')['database'])
    require(database.name == 'DebugGameplay.sqlite' and database.parent.name == 'Cache', 'Unknown user-root evidence')
    user_root = database.parent.parent.resolve(strict=True)
    mods = packages[0]['install'].parent
    require(not any(p.is_relative_to(mods) for p in (output, source, *(p['source'] for p in packages))),
            'Continuation staging/output must stay outside installed Mods')
    require((dependencies/'frida/__init__.py').is_file(), 'Existing Frida dependencies missing')
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


def run(args):
    plan = prepare(args.source, args.output, args.at, args.through, args.dependencies)
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
        new_seed=False, fixture=False, gameplay_interventions=False,
        limits=['Reload resets transient native caches and observer identity bindings.',
                'Only the continuation segment is measured here; parent evidence must be joined explicitly.',
                'No assumption of uninterrupted RNG/decision identity with the stalled segment.']))
    sources = [Path(__file__), HERE/'ce_bakers_fresh.py', HERE/'full_game_observation.py',
               HERE/'full_game_census.lua', HERE/'full_game_preflight.lua', HERE/'planning_observer.lua',
               HERE/'quarter_placement_watch.lua', HERE/'district_adjacency_watch.lua',
               HERE/'storekeeper_runtime.py', HERE/'storekeeper_runtime.lua',
               HERE/'economy_savings_watch.py', HERE/'economy_savings_watch.js',
               *sorted((HERE.parents[1]/'ai_baseline/full_game_controller').glob('*.py')),
               *sorted((HERE.parents[1]/'ai_baseline/full_game_controller').glob('*.lua'))]
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
    copied, watch, checkpoint = [], None, None

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
                {plan.protocol['ce'], plan.protocol['csc'], *plan.extras}, 'Expected exact original five packages')
        session.load_once(plan.checkpoint['native_save'], sha256=plan.checkpoint['sha256'],
                          native_directory=plan.saves, turn=plan.at,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AI_BakersGameplay', 'CSC_AdjacencyGameplay'),
                          eligibility=source_gate)
        verify_modules(session, by_role['ce']['install']/'Binaries/Win64'/DLL, out, HOTFIX_SHA)
        raw = controller.cmd('CSC_BAKERS_STOREKEEPER_WATCH=true\n'+read(HERE/'storekeeper_runtime.lua'),
                             'PlotInfo', 'install-continuation-storekeeper-watch')
        require('CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED' in raw, 'Storekeeper watch not installed')
        from full_game_observation import install, play, finish
        install(controller, out, plan.identity['original_ai'], plan.user_root, plan.through,
                planning=True, extra_mods=plan.extras, csc_path=by_role['csc']['install'],start=plan.at)
        from economy_savings_watch import EconomySavingsWatch
        for name in ('economy_savings_watch.py', 'economy_savings_watch.js'):
            shutil.copyfile(HERE/name, out/name)
        indices = [int(v) for v in re.findall(r'CSC_DISTRICT_CATALOGUE\t(\d+)\t', read(out/'loaded-district-catalogue.txt'))]
        require(indices, 'Missing loaded district catalogue')
        modules = load(out/'loaded-modules.json')
        width, height = plan.identity['map_signature'][:2]
        watch = EconomySavingsWatch(directory=plan.dependencies, binary=modules['GameCore_XP2_FinalRelease.dll']['path'],
                                    output=out, start=plan.at, through=plan.through, write=write_json,
                                    players=plan.identity['original_ai'], width=width, height=height, districts=max(indices)+1)
        watch.attach(session.owner, modules)
        play(controller, out, plan.user_root, start=plan.at, endpoint=plan.through, saves=plan.saves, savings=watch)
        from economy_preflight import inspect
        inspect(controller, out)
        final = parse(controller.cmd('print("CSC_CONTINUATION_END="..CE_AIDistrictScoresStatus())',
                                     'GameCore_Tuner', 'continuation-end-status'), 'CSC_CONTINUATION_END')
        write_json(out/'native-endpoint.json', final)
        check_native_status(final, False)
        capture_census(controller, set(plan.identity['original_ai']), plan.through, out/'chain-census.txt')
        checkpoint = save_inactive_boundary(controller, turn=plan.through, name='CSC_AI_CONTINUATION_'+str(plan.through),
                                            native_directory=plan.saves, archive=out/'endpoint.Civ6Save')
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
    watch.qualify()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'output', 'dependencies'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--at', type=int, required=True)
    parser.add_argument('--through', type=int, required=True)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
