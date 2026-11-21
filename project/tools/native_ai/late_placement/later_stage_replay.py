"""Compare the current CSC AI Lua with its frozen predecessor on one save.

The checkpoint, CE DLL, gameplay database and optional mods stay identical.
This first replay uses an ordinary world to check later-stage offer delivery.
Separate matched fixtures can qualify decisions too rare in that window.
"""
import argparse
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

from ce_bakers_fresh import LOGS
from ce_replay import DLL, STEAM_26595377_CORE_SHA, verify_modules
from driver import (HeldProcess, NativeSession, configure, flags, launch, lua,
                    make_probe_controller, manifest, native_inventory, parse, read,
                    require, restore_preferences, sha, write_json)
from planning_continue import HERE, compare_structure, enable, parse_census, prepare
from later_stage_results import service_durations


POLICY_FILES = (
    'Lua_UI/AI/CSC_AI_BakersGameplay.lua',
    'Lua_UI/AI/CSC_AI_EconomyAdapters.lua',
    'Lua_UI/AI/CSC_AI_EconomyFacts.lua',
    'Lua_UI/AI/CSC_AI_EconomyModel.lua',
    'Lua_UI/Adjacencies/CSC_AdjacencyUI.lua',
)


def candidate_package(original, csc_source, candidate):
    """Overlay only registered Lua scripts on an already built CSC package."""
    shutil.copytree(original, candidate)
    for name in POLICY_FILES:
        require((candidate / name).is_file(), 'Missing packaged script ' + name)
        shutil.copy2(csc_source / name, candidate / name)
    before, after = manifest(original), manifest(candidate)
    changed = {Path(name).as_posix() for name in before if before[name] != after[name]}
    require(set(after) == set(before) and changed == set(POLICY_FILES),
            'Frozen candidate must differ only in the five registered policy scripts')
    return after


def run_arm(source, output, start, end, candidate_source, fixture=None):
    plan = prepare(source, output, start, start, None, read_only=True)
    require(not native_inventory(), 'Another session owns Civ or FireTuner')
    require(plan.protocol['native_profile']['gamecore_sha256'] == STEAM_26595377_CORE_SHA,
            'Checkpoint runtime differs from the supported CE build')
    output.mkdir(parents=True)
    controller = make_probe_controller(output, user_root=plan.user_root)
    controller.study_endpoint = end
    controller.autoplay_interval_seconds = 15 * 60
    controller.allow_observer_warning_dismissal = True
    controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    controller.allow_one_more_turn = True
    session = NativeSession(output, controller, inventory=native_inventory,
                            hold=HeldProcess, write=write_json)
    installed = []

    def verify_packages():
        for item in installed:
            require(manifest(item['install']) == item['files'], 'Installed package drift')
        for extra in plan.extras.values():
            require(manifest(Path(extra['path'])) == extra['files'], 'Optional package drift')

    def census(turn, label):
        scope = f'CSC_ENDPOINT_PLAYERS={lua(plan.identity["original_ai"])}\nCSC_ENDPOINT_EXPECTED_TURN={turn}\n'
        scope += 'local CSC_MILESTONE_EXCHANGE_CENSUS=true\n'
        raw = controller.cmd(scope + read(HERE / 'full_game_census.lua'),
                             'CSC_AI_BakersGameplay', label)
        (output / (label + '.txt')).write_text(raw, encoding='utf-8')
        result = parse_census(raw, turn)
        write_json(output / (label + '.json'), result)
        return result

    def source_gate():
        proof = compare_structure(plan.expected_census, census(start, 'source-census'))
        write_json(output / 'source-structure-comparison.json', proof)
        return proof['verified']

    def native_status(label):
        readers = dict(research='CE_AIMaterialDevelopmentStatus',
                       building='CE_AIBuildingNominationStatus', wonder='CE_AISupplierWonderProtectionStatus')
        code = '\n'.join(f'print("CSC_STAGE_STATUS_{key}="..{reader}())' for key, reader in readers.items())
        raw = controller.cmd(code, 'CSC_AI_BakersGameplay', label)
        status = {key: parse(raw, 'CSC_STAGE_STATUS_' + key) for key in readers}
        write_json(output / (label + '.json'), status)

    def service_observation(label, every_turn=False):
        source = read(HERE / 'later_stage_service_watch.lua')
        filter_seats = lua({pid: True for pid in plan.identity['original_ai']})
        code = f'CSC_MILESTONE_SERVICE_PLAYERS={filter_seats}\n'
        if every_turn:
            code += 'CSC_MILESTONE_SERVICE_EVERY_TURN=true\n'
        code += source
        raw = controller.cmd(code, 'PlotInfo', label)
        (output / (label + '.txt')).write_text(raw, encoding='utf-8')
        marker = 'CSC_MILESTONE_SERVICE_INSTALLED' if every_turn else 'CSC_MILESTONE_SERVICE_END'
        require(marker in raw, 'Missing Service observation acknowledgement')

    def fixture_receipt(mode, context, expected=None):
        script = read(HERE / f'later_stage_{fixture}_fixture.lua')
        label = f'{fixture}-{mode}'
        raw = controller.cmd(f'local mode={lua(mode)}\nlocal expectedBuyer={lua(expected)}\n' + script, context, label)
        (output / (label + '.txt')).write_text(raw, encoding='utf-8')
        require(f'CSC_MILESTONE_{fixture.upper()}_{mode.upper()}' in raw, 'Fixture evidence missing')
        return raw

    try:
        for item in plan.packages:
            require(not item['install'].exists(), 'Test mod destination already exists')
            if item['role'] == 'csc' and candidate_source:
                item = dict(item, files=candidate_package(item['source'], candidate_source, item['install']))
            else:
                shutil.copytree(item['source'], item['install'])
            installed.append(item)
        verify_packages()
        write_json(output / 'inputs.json', dict(source=str(source), start=start, end=end,
                   checkpoint=plan.checkpoint['sha256'], fixture=fixture,
                   packages={i['role']: i['files'] for i in installed}))
        session.start(lambda: launch(SimpleNamespace(binary=plan.binary), output))
        session.wait_context('MainMenu')
        configure(controller, output, csc_id=plan.protocol['ce'])
        addons = {plan.protocol['ce'], plan.protocol['csc'], *plan.extras}
        for addon in [plan.protocol['csc'], *plan.extras]:
            enable(session, addon)
        require({key for key, active in flags(controller, 'verify-mods')['mods'].items() if active} == addons,
                'Unexpected active mod stack')
        session.load_once(plan.checkpoint['native_save'], sha256=plan.checkpoint['sha256'],
                          native_directory=plan.saves, turn=start,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AI_BakersGameplay'), eligibility=source_gate)
        ce = next(item for item in installed if item['role'] == 'ce')
        verify_modules(session, (ce['install'] / 'Binaries/Win64' / DLL).resolve(), output, STEAM_26595377_CORE_SHA)
        if fixture:
            setup = fixture_receipt('setup', 'CSC_AI_BakersGameplay')
            if fixture == 'market':
                fixture_receipt('legal', 'PlotInfo')
            elif fixture == 'entertainment':
                buyer = re.search(r'CSC_MILESTONE_ENTERTAINMENT_SETUP\s+3\s+(\d+)\b', setup)
                require(buyer is not None, 'Entertainment Complex buyer missing from setup')
                fixture_receipt('legal', 'PlotInfo', int(buyer[1]))
        service_observation('service-before')
        service_observation('service-observer', every_turn=True)
        native_status('native-before')
        controller.play(end)
        state = controller.state_read('later-stage-final-clock')
        require(state['turn'] == end and not state['active'], 'Wrong replay boundary')
        census(end, 'endpoint-census')
        native_status('native-after')
        if fixture:
            fixture_receipt('outcome', 'CSC_AI_BakersGameplay')
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, output)
                          if (output / 'original-preferences.json').exists() else None,
                          restore_package=verify_packages)
        if session.closed or session.owner is None and not native_inventory():
            for item in installed:
                item['install'].rename(output / item['install'].name)
        if session.closed:
            for name in LOGS:
                log = plan.user_root / 'Logs' / name
                if log.is_file():
                    shutil.copy2(log, output / name)
    require(session.closed and sha(Path(plan.checkpoint['native_save'])) == plan.checkpoint['sha256'],
            'Source save changed or replay closure unverified')
    log = read(output / 'Lua.log')
    for marker in ('CSC_AI_BAKERS_DISTRICTS_FAILED', 'CSC_MILESTONE_SERVICE_FAULT'):
        require(marker not in log, 'Replay log contains ' + marker)
    write_json(output / 'observed-services.json', service_durations(log, start + 1, end))
    write_json(output / 'complete.json', dict(verified=True, turn=end))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'output', 'candidate-source'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('start', 'end'):
        parser.add_argument('--' + name, type=int, required=True)
    parser.add_argument('--arm', choices=('control', 'treatment'), action='append')
    fixtures = parser.add_mutually_exclusive_group()
    fixtures.add_argument('--market-rebuild', action='store_true',
                          help='Controlled player-5 Market rebuild on the qualified turn-200 checkpoint')
    fixtures.add_argument('--storekeeper-preparation', action='store_true',
                          help='Add the same missing Mill on both turn-50 copies to isolate Feudalism')
    fixtures.add_argument('--entertainment-preparation', action='store_true',
                          help='Prepare the adjacent Arena on both turn-200 copies to isolate Zoo production')
    fixtures.add_argument('--sacristan-preparation', action='store_true',
                          help='Prepare the missing Tailor beside an existing Temple to isolate Divine Right')
    args = parser.parse_args()
    require(0 < args.end - args.start <= 25, 'Replay window must be 1 to 25 turns')
    require(not args.market_rebuild or args.start == 200, 'Market fixture requires the turn-200 source')
    require(not args.storekeeper_preparation or args.start == 50, 'Storekeeper fixture requires the turn-50 source')
    require(not args.entertainment_preparation or args.start == 200, 'Entertainment fixture requires the turn-200 source')
    require(not args.sacristan_preparation or args.start == 100, 'Sacristan fixture requires the turn-100 source')
    fixture = next((name for enabled, name in ((args.market_rebuild, 'market'),
                    (args.storekeeper_preparation, 'storekeeper'), (args.entertainment_preparation, 'entertainment'),
                    (args.sacristan_preparation, 'sacristan'))
                    if enabled), None)
    for arm in args.arm or ('control', 'treatment'):
        run_arm(args.source, args.output / arm, args.start, args.end,
                args.candidate_source if arm == 'treatment' else None, fixture)
