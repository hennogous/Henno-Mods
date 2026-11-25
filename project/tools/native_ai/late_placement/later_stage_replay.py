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
from ce_replay import (DLL, STEAM_26595377_CORE_SHA, archive_development_package,
                       development_package_files, verify_modules)
from driver import (HeldProcess, NativeSession, configure, flags, launch, load, lua,
                    make_probe_controller, manifest, native_inventory, parse, read,
                    require, restore_preferences, sha, write_json)
from planning_continue import HERE, compare_structure, enable, parse_census, prepare
from later_stage_results import service_durations
from ce_bakers_fresh import package_identity
from full_game_controller.checkpoint import save_inactive_boundary


POLICY_FILES = (
    'Lua_UI/AI/CSC_AI_BakersGameplay.lua',
    'Lua_UI/AI/CSC_AI_EconomyAdapters.lua',
    'Lua_UI/AI/CSC_AI_EconomyFacts.lua',
    'Lua_UI/AI/CSC_AI_EconomyModel.lua',
    'Lua_UI/Adjacencies/CSC_AdjacencyUI.lua',
)
CONNECTION_FILES = (
    # Freeze the complete registered AI package. The entry point calls the
    # bridge and the scanners from the same revision even when links are off.
    'Lua_UI/AI/CSC_AI_AdjacencyScan.lua',
    'Lua_UI/AI/CSC_AI_BakersGameplay.lua',
    'Lua_UI/AI/CSC_AI_DistrictBridge.lua',
    'Lua_UI/AI/CSC_AI_EconomyAdapters.lua',
    'Lua_UI/AI/CSC_AI_EconomyFacts.lua',
    'Lua_UI/AI/CSC_AI_EconomyModel.lua',
    'Lua_UI/AI/CSC_AI_PlanContinuity.lua',
    'Lua_UI/AI/CSC_AI_QuarterPlacement.lua',
)
CONNECTION_WONDER_UI = 'Lua_UI/Adjacencies/CSC_AdjacencyUI.lua'
CONNECTION_ADAPTER = 'Lua_UI/AI/CSC_AI_EconomyAdapters.lua'


def with_connection_switch(source, enabled):
    setting = b'true' if enabled else b'false'
    updated, count = re.subn(rb'(?m)^E\.AnchoredConnectionsEnabled=(true|false)(?=\r?$)',
                             b'E.AnchoredConnectionsEnabled=' + setting, source)
    require(count == 1, 'Expected exactly one connection policy switch')
    return updated


def candidate_package(original, csc_source, candidate, policy_files=POLICY_FILES, *,
                      connection_enabled=None, allow_identical_scripts=False):
    """Overlay only registered Lua scripts on an already built CSC package."""
    shutil.copytree(original, candidate)
    for name in policy_files:
        require((candidate / name).is_file(), 'Missing packaged script ' + name)
        shutil.copy2(csc_source / name, candidate / name)
    if connection_enabled is not None:
        # Matched connection replays use the same policy source in both arms.
        # The single switch is the experimental change. This preserves the
        # native private yield and all other guidance in an older save.
        require(CONNECTION_ADAPTER in policy_files, 'Missing the connection policy adapter')
        adapter = candidate / CONNECTION_ADAPTER
        adapter.write_bytes(with_connection_switch(adapter.read_bytes(), connection_enabled))
    before, after = manifest(original), manifest(candidate)
    changed = {Path(name).as_posix() for name in before if before[name] != after[name]}
    expected = set(policy_files)
    allowed = changed <= expected if allow_identical_scripts or connection_enabled is not None else changed == expected
    require(set(after) == set(before) and allowed,
            'Frozen candidate must differ only in the declared registered policy scripts')
    return after


def require_clean_replay_log(log):
    for marker in ('CSC_AI_BAKERS_DISTRICTS_FAILED', 'CSC_MILESTONE_SERVICE_FAULT',
                   'CSC_AI_ECONOMY_FAILED', 'CSC_AI_PLAN_MEMORY_UNAVAILABLE', 'CSC_CUSTOMER_LAND_TARGET_FAULT'):
        require(marker not in log, 'Replay log contains ' + marker)


def run_arm(source, output, start, end, candidate_source, fixture=None, *,
            natural_sacristan=None, expected_preparation=None, replay_ce=None, connection_prototype=False,
            connection_scout=(), connection_enabled=None, connection_switch_turn=None,
            connection_timing_player=None, paired_layout_csc=None, paired_layout_switch_turn=None,
            recover_preferences_from=None, land_targets=(), timing_query=None,
            provider_decline_switch=False, fixture_parameters=None, timing_query_at_switch=False,
            archive_prepared_frontier=False, prepared_frontier=None):
    if fixture == 'customer_frontier':
        require(paired_layout_csc and paired_layout_switch_turn == start
                and isinstance(fixture_parameters, dict),
                'Customer frontier replay needs the exact shared save, policy switch and target coordinates')
    if provider_decline_switch:
        require(paired_layout_csc and paired_layout_switch_turn == start and fixture is None
                and 0 < end-start <= 30 and connection_scout,
                'The provider experiment switches both copies at the loaded boundary')
    if replay_ce is not None:
        replay_ce=replay_ce.resolve(strict=True)
        require((replay_ce/'DevCE.modinfo').is_file() and
                (replay_ce/'Binaries/Win64'/DLL).is_file(), 'Expected a staged Dev CE build')
    plan = prepare(source, output, start, start, None, read_only=True, replay_ce=replay_ce,
                   paired_layout_csc=paired_layout_csc)
    original_checkpoint = plan.checkpoint['sha256']
    original_save = Path(plan.checkpoint['native_save'])
    prepared_board = None
    if archive_prepared_frontier or prepared_frontier is not None:
        require(fixture == 'customer_frontier' and not (archive_prepared_frontier and prepared_frontier),
                'Prepared checkpoints are only for separate, scoped customer-frontier replays')
    if prepared_frontier is not None:
        receipt = Path(prepared_frontier).resolve(strict=True)
        prepared_board = load(receipt)
        closed = load(receipt.parent / 'session-closed.json')
        require(closed['verified'] and closed['owners_absent'] and closed['preferences_verified']
                and closed['package_callback_completed'] and prepared_board['source'] == str(plan.source)
                and prepared_board['source_sha256'] == original_checkpoint
                and prepared_board['parameters'] == fixture_parameters,
                'A prepared checkpoint must come from the same verified layout fixture')
        prepared_save = prepared_board['checkpoint']
        native, archive = (Path(prepared_save[key]).resolve(strict=True) for key in ('native_save', 'archive'))
        require(prepared_save['verified'] and prepared_save['turn'] == start
                and prepared_board['census']['turn'] == start
                and native.parent == plan.saves and archive.parent == receipt.parent
                and sha(native) == prepared_save['sha256'] == sha(archive),
                'Prepared checkpoint clock, location or hash differs')
        plan.checkpoint = prepared_save
        plan.expected_census = prepared_board['census']
    switch_turn = paired_layout_switch_turn or connection_switch_turn
    if timing_query_at_switch:
        require(timing_query is not None and switch_turn is not None and start < switch_turn < end
                and fixture is None and natural_sacristan is None,
                'A switch-boundary timing query needs an unmodified pre-roll')
    deferred_capacity = fixture in ('stirling_capacity', 'quito_capacity')
    if replay_ce is not None:
        require(package_identity(replay_ce)[0]==plan.protocol['ce'], 'Dev CE replay mod identity differs')
    if fixture=='connection':
        require(plan.checkpoint['sha256']=='2c3ac19cd18cfc50b368fb1dddfa40a3507cc8dfd4c3ac28ff503d504e590873',
                'Connection capacity fixture expects the exact archived Continents layout')
    if fixture=='stirling_capacity':
        require(plan.checkpoint['sha256']=='3abc302fdc23f3941450158354e7348b9571bdffa3f13d5a0d01acb102c10df7',
                'Stirling capacity fixture expects the qualified turn-100 save')
    require(len(connection_scout)<=4 and all(pid in plan.identity['original_ai'] and 0<city<2**31
            for pid,city in connection_scout), 'Connection scout requires up to four original AI city scopes')
    scout_cities = {tuple(scope) for scope in connection_scout}
    require(len(land_targets)<=4 and all((pid,city) in scout_cities and district>=0 and plot>=0
            for pid,city,district,plot in land_targets), 'Land targets require a named connection scout city')
    require(connection_timing_player is None or connection_timing_player in plan.identity['original_ai'],
            'Connection timing requires an original AI player')
    require(not native_inventory(), 'Another session owns Civ or FireTuner')
    require(plan.protocol['native_profile']['gamecore_sha256'] == STEAM_26595377_CORE_SHA,
            'Checkpoint runtime differs from the supported CE build')
    output.mkdir(parents=True)
    controller = make_probe_controller(output, user_root=plan.user_root)
    controller.study_endpoint = end
    controller.autoplay_interval_seconds = (20 if paired_layout_csc else 15) * 60
    controller.allow_observer_warning_dismissal = True
    controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    controller.allow_one_more_turn = True
    session = NativeSession(output, controller, inventory=native_inventory,
                            hold=HeldProcess, write=write_json)
    installed = []
    preparation_turn = 55 if natural_sacristan is not None else start
    log_cursor = 0

    def check_live_log():
        nonlocal log_cursor
        path = plan.user_root / 'Logs' / 'Lua.log'
        with path.open(encoding='utf-8-sig', errors='replace') as live:
            live.seek(log_cursor)
            require_clean_replay_log(live.read())
            log_cursor = live.tell()

    def play_between(first, last):
        # Keep shared observer recovery eligible in every finite window.
        # Stop a broken frozen package at startup or the first short boundary.
        check_live_log()
        for boundary in (*range(first + 5, last, 5), last):
            controller.play(boundary)
            check_live_log()

    def verify_packages():
        for item in installed:
            require(development_package_files(item['install']) == item['files'], 'Installed package drift')
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
        return raw

    def fixture_receipt(mode, context, expected=None):
        script = read(HERE / f'later_stage_{fixture}_fixture.lua')
        label = f'{fixture}-{mode}'
        options = (f'local mode={lua(mode)}\nlocal expectedBuyer={lua(expected)}\n'
                   f'local naturalSacristan={lua(natural_sacristan)}\nlocal fixtureTurn={preparation_turn}\n'
                   f'local fixtureParameters={lua(fixture_parameters)}\n')
        raw = controller.cmd(options + script, context, label)
        (output / (label + '.txt')).write_text(raw, encoding='utf-8')
        require(f'CSC_MILESTONE_{fixture.upper()}_{mode.upper()}' in raw, 'Fixture evidence missing')
        return raw

    def capture_policy_timing(turn):
        # Private copies of the model read one paused world. They neither
        # publish scores nor advance turns, so this can inspect common setup.
        raw = controller.cmd(read(timing_query), 'CSC_AI_BakersGameplay', 'same-state-timing', wait=60)
        (output / 'same-state-timing.txt').write_text(raw, encoding='utf-8')
        require('CSC_CUSTOMER_TIMING_COMPLETE=' in raw and re.search(rf'CSC_COAST_END\t{turn}\b', raw),
                'Same-state timing checks did not complete')

    def sacristan_civic_state(mode):
        raw = fixture_receipt(mode, 'PlotInfo')
        row = re.search(rf'CSC_MILESTONE_SACRISTAN_{mode.upper()}\t([^\r\n]+)', raw)
        require(row is not None, 'Sacristan civic readback missing')
        return row[1].split('\t')

    try:
        for item in plan.packages:
            if item['role']=='ce' and replay_ce is not None:
                item=dict(item,source=replay_ce,files=development_package_files(replay_ce),reused=item['install'].is_dir())
                if not item['reused']:shutil.copytree(item['source'],item['install'])
            elif item['role']=='csc' and paired_layout_csc is not None:
                item=dict(item,source=paired_layout_csc,files=development_package_files(paired_layout_csc))
            elif item['reused']:
                require(item['role']!='csc' or candidate_source is None,
                        'Use an isolated package for a CSC overlay replay')
            else:
                require(not item['install'].exists(), 'Test mod destination already exists')
                if item['role'] == 'csc' and candidate_source:
                    policy_files=CONNECTION_FILES if connection_prototype else POLICY_FILES
                    if connection_prototype and (candidate_source / CONNECTION_WONDER_UI).is_file():
                        policy_files += (CONNECTION_WONDER_UI,)
                    initial_connection = False if connection_switch_turn is not None else connection_enabled
                    item=dict(item,files=candidate_package(item['source'],candidate_source,item['install'],policy_files,
                                                          connection_enabled=initial_connection,
                                                          allow_identical_scripts=connection_prototype))
                else:
                    shutil.copytree(item['source'], item['install'])
            installed.append(item)
        verify_packages()
        write_json(output / 'inputs.json', dict(source=str(source), start=start, end=end,
                   checkpoint=plan.checkpoint['sha256'], original_checkpoint=original_checkpoint,
                   fixture=fixture,
                   fixture_parameters=fixture_parameters,
                   natural_sacristan=natural_sacristan, preparation_turn=preparation_turn,
                   connection_scout=connection_scout, connection_enabled=connection_enabled,
                   land_targets=land_targets,
                   connection_switch_turn=connection_switch_turn,
                   paired_layout_switch_turn=paired_layout_switch_turn,
                   provider_decline_switch=provider_decline_switch,
                   paired_layout_csc=str(paired_layout_csc) if paired_layout_csc else None,
                   connection_timing_player=connection_timing_player,
                   timing_query_sha256=sha(timing_query) if timing_query is not None else None,
                   timing_query_turn=(switch_turn if timing_query_at_switch else start)
                   if timing_query is not None else None,
                   packages={i['role']: i['files'] for i in installed}))
        session.start(lambda: launch(SimpleNamespace(binary=plan.binary), output))
        session.wait_context('MainMenu')
        # A native exception can strand the previous game's mod choices.
        # Restore the player's captured menu settings before configure() saves
        # this arm's starting state. This operates before loading any world.
        if recover_preferences_from is not None:
            recovery = output / 'previous-session-menu'
            recovery.mkdir()
            shutil.copyfile(recover_preferences_from / 'original-preferences.json', recovery / 'original-preferences.json')
            restore_preferences(controller, recovery)
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
        if paired_layout_csc:
            # Short replays isolate the prospective extension on top of the
            # anchored planner in both arms. Set that common starting state
            # at the loaded boundary so they can use the exact full-game pin.
            # The qualification control reads the packaged defaults separately.
            code = (f'assert(Game.GetCurrentGameTurn()=={start});local A=assert(CSC_AI_EconomyAdapters);'
                    'assert(A.ProspectiveConnectionsEnabled==false);'
                    'A.AnchoredConnectionsEnabled=true;A.AnchoredConnectionAuditEnabled=true;'
                    'print("CSC_REPLAY_ANCHORED",tostring(A.AnchoredConnectionsEnabled),'
                    'tostring(A.AnchoredConnectionAuditEnabled))')
            raw = controller.cmd(code, 'CSC_AI_BakersGameplay', 'paired-layout-common-opening')
            require(re.search(r'CSC_REPLAY_ANCHORED\s+true\s+true',raw), 'Missing common replay policy')
        if timing_query is not None and not timing_query_at_switch and fixture != 'customer_frontier':
            capture_policy_timing(start)
        if natural_sacristan is not None:
            # Both arms use the same integrated package throughout pre-roll.
            # Only the target civic's Service credit is toggled after setup.
            play_between(start, preparation_turn)
            prepared = census(preparation_turn, 'preparation-census')
            if expected_preparation is not None:
                proof = compare_structure(expected_preparation['census'], prepared)
                write_json(output / 'preparation-comparison.json', proof)
                require(proof['verified'], 'The natural Sacristan preparation worlds diverged')
        if fixture and not deferred_capacity:
            if fixture == 'sacristan':
                civic_start = sacristan_civic_state('before')
                require(civic_start[0] == str(preparation_turn), 'Civic UI did not reach the preparation turn')
                if expected_preparation is not None:
                    require(civic_start == expected_preparation['civic_start'], 'Starting civic state differs between arms')
            setup = fixture_receipt('setup', 'CSC_AI_BakersGameplay') if prepared_board is None else None
            if fixture == 'customer_frontier':
                if prepared_board is None:
                    receipt = re.search(r'CSC_MILESTONE_CUSTOMER_FRONTIER_SETUP\t([^\r\n]+)', setup)
                    require(receipt is not None, 'Customer frontier setup receipt is missing its facts')
                    frontier_start = receipt[1].split('\t')
                else:
                    frontier_start = prepared_board['fixture_start']
                if expected_preparation is not None:
                    require(frontier_start == expected_preparation['frontier_start'],
                            'Released footprint, price, capacity or supply differs between arms')
                if archive_prepared_frontier:
                    # File-backed restart lets the engine rebuild its city
                    # cache after WorldBuilder changes the district count.
                    # Neither replay needs to apply the setup a second time.
                    before_save = census(start, 'prepared-frontier-census')
                    checkpoint = save_inactive_boundary(controller, turn=start,
                        name=f'CSC_PREPARED_FRONTIER_{start}_{original_checkpoint[:10]}',
                        native_directory=plan.saves, archive=output/'prepared-frontier.Civ6Save')
                    write_json(output/'prepared-frontier.json', dict(source=str(plan.source),
                        source_sha256=original_checkpoint, parameters=fixture_parameters,
                        fixture_start=frontier_start, checkpoint=checkpoint, census=before_save))
                if timing_query is not None:
                    capture_policy_timing(start)
            if fixture == 'market':
                fixture_receipt('legal', 'PlotInfo')
            elif fixture == 'entertainment':
                buyer = re.search(r'CSC_MILESTONE_ENTERTAINMENT_SETUP\s+3\s+(\d+)\b', setup)
                require(buyer is not None, 'Entertainment Complex buyer missing from setup')
                fixture_receipt('legal', 'PlotInfo', int(buyer[1]))
            elif fixture == 'connection':
                fixture_receipt('legal', 'PlotInfo')
            elif fixture == 'sacristan':
                civic_prepared = sacristan_civic_state('progress')
                if natural_sacristan is not None:
                    require(civic_start == civic_prepared, 'Building setup changed natural civic state')
        service_start = service_observation('service-before')
        if natural_sacristan is not None:
            require(not re.search(r'CSC_MILESTONE_SERVICE_LINK\t\d+\t5\tTAILORS\t3\t\w+\t2038\t1965\b',
                                  service_start), 'The prepared Sacristan was already operational')
        service_observation('service-observer', every_turn=True)
        native_status('native-before')
        if connection_scout:
            targets='local landTargets='+lua([list(row) for row in land_targets])+'\n'
            raw=controller.cmd(targets+read(HERE/'customer_land_watch.lua'), 'PlotInfo', 'customer-land-history')
            require('CSC_CUSTOMER_LAND_WATCH_INSTALLED' in raw, 'Land purchase observer did not install')
            # Read the existing CE journal before each publication replaces it.
            # This attaches neither a second native observer nor policy writer.
            raw=controller.cmd(read(HERE/'planning_observer.lua'), 'CSC_AI_BakersGameplay', 'connection-history')
            require('CSC_PLANNING_INSTALLED' in raw, 'Physical connection history did not install')
            code='CSC_CUSTOMER_WATCH_TARGETS='+lua([list(row) for row in connection_scout])+'\n'
            code+=read(HERE/'customer_placement_watch.lua')
            raw=controller.cmd(code, 'CSC_AI_BakersGameplay', 'connection-scout')
            require('CSC_CUSTOMER_WATCH_INSTALLED' in raw, 'Native connection scout did not install')
        if connection_timing_player is not None:
            code = f'CSC_CONNECTION_TIMING_PLAYER={connection_timing_player}\n' + read(HERE/'connection_timing_watch.lua')
            raw = controller.cmd(code, 'CSC_AI_BakersGameplay', 'connection-timing')
            require(f'CSC_CONNECTION_TIMING_READY={connection_timing_player}' in raw, 'Connection timer did not install')
        if switch_turn is None:
            if paired_layout_csc:
                code = ('local A=assert(CSC_AI_EconomyAdapters);'
                        'assert(A.AnchoredConnectionsEnabled==true and A.ProspectiveConnectionsEnabled==false);'
                        'print("CSC_CONNECTION_SCOUT_BASELINE")')
                raw = controller.cmd(code, 'CSC_AI_BakersGameplay', 'connection-scout-baseline')
                require('CSC_CONNECTION_SCOUT_BASELINE' in raw, 'Scout did not load the revised baseline')
            play_between(preparation_turn, end)
        else:
            # Switch at the loaded inactive checkpoint when an independent
            # pre-roll would risk changing the world's condition before the test.
            # An interior switch still compares both worlds after the pre-roll.
            if start < switch_turn:
                play_between(start, switch_turn)
            prepared = census(switch_turn, 'connection-switch-census')
            if timing_query_at_switch:
                capture_policy_timing(switch_turn)
            if expected_preparation is not None:
                prior = expected_preparation['census']
                proof = compare_structure(prior, prepared)
                if paired_layout_csc:
                    # Equal geography and population alone do not establish
                    # equal buying power for a prospective district footprint.
                    prior_treasury, treasury = (
                        sorted(row for kind, row in snapshot['rows'] if kind == 'TREASURY')
                        for snapshot in (prior, prepared)
                    )
                    proof['treasury_matches'] = prior_treasury == treasury
                    if not proof['treasury_matches']:
                        proof.update(verified=False, expected_treasury=prior_treasury,
                                     actual_treasury=treasury)
                write_json(output / 'connection-switch-comparison.json', proof)
                require(proof['verified'], 'Connection switch starting states differ')
            if deferred_capacity:
                fixture_receipt('before', 'PlotInfo')
                fixture_receipt('setup', 'CSC_AI_BakersGameplay')
                fixture_receipt('legal', 'PlotInfo')
                capacity_census = census(switch_turn, 'connection-capacity-census')
                if expected_preparation is not None:
                    proof = compare_structure(expected_preparation['capacity_census'], capacity_census)
                    write_json(output / 'connection-capacity-comparison.json', proof)
                    require(proof['verified'], 'Controlled capacity preparation diverged')
            setting = 'true' if connection_enabled else 'false'
            switch = 'ProspectiveConnectionsEnabled' if paired_layout_switch_turn else 'AnchoredConnectionsEnabled'
            baseline = 'assert(A.AnchoredConnectionsEnabled==true);' if paired_layout_switch_turn else ''
            if provider_decline_switch:
                # This pair controls only empty-site admission for fulfilled
                # providers. Both arms run the same prospective economics.
                switch = 'FulfilledProviderDeclinesEnabled'
                baseline += ('assert(A.ProspectiveConnectionsEnabled==false and A.FulfilledProviderDeclinesEnabled==true);'
                             'A.ProspectiveConnectionsEnabled=true;A.FulfilledProviderDeclinesEnabled=false;')
            code = (f'local A=assert(CSC_AI_EconomyAdapters);{baseline}assert(A.{switch}==false);'
                    f'A.{switch}={setting};print("CSC_CONNECTION_SWITCH="..tostring(A.{switch}))')
            raw = controller.cmd(code, 'CSC_AI_BakersGameplay', 'connection-switch')
            require(f'CSC_CONNECTION_SWITCH={setting}' in raw, 'Connection switch did not read back')
            if (fixture == 'customer_frontier' and fixture_parameters.get('refreshPublisher')
                    and not archive_prepared_frontier):
                # Change the paused world's initial conditions before resuming.
                # This dedicated diagnostic package lets the real publisher
                # see them before any AI tree reads the prepared turn's scores.
                raw = controller.cmd('assert(CSC_TEST_FRONTIER_REFRESH)()',
                                     'CSC_AI_BakersGameplay', 'prepared-turn-publication')
                require(f'CSC_TEST_FRONTIER_REFRESHED\t{switch_turn}' in raw,
                        'Prepared-turn policy publication was not confirmed')
            play_between(switch_turn, end)
        state = controller.state_read('later-stage-final-clock')
        require(state['turn'] == end and not state['active'], 'Wrong replay boundary')
        census(end, 'endpoint-census')
        if connection_scout:
            raw=controller.cmd('CSC_CUSTOMER_PLACEMENT_WATCH.Finish()',
                               'CSC_AI_BakersGameplay', 'connection-scout-end')
            require(re.search(r'CSC_CUSTOMER_WATCH_FINISH records=\d+ faults=0 dropped=0\b',raw),
                    'Connection scout journal is incomplete')
            raw=controller.cmd('CSC_AI_PLANNING_WATCH.Finish()', 'CSC_AI_BakersGameplay', 'connection-history-end')
            require(re.search(r'CSC_PLANNING_FINISH\s+[^\r\n]*\bdropped=0\b[^\r\n]*\bfaults=0\b',raw),
                    'Physical connection history is incomplete')
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
                if item['role']!='csc' or not item['reused']:
                    archive_development_package(item['install'],output/item['install'].name,item['reused'])
        if session.closed:
            for name in LOGS:
                log = plan.user_root / 'Logs' / name
                if log.is_file():
                    shutil.copy2(log, output / name)
    require(session.closed and sha(Path(plan.checkpoint['native_save'])) == plan.checkpoint['sha256']
            and sha(original_save) == original_checkpoint,
            'Source save changed or replay closure unverified')
    log = read(output / 'Lua.log')
    require_clean_replay_log(log)
    write_json(output / 'observed-services.json', service_durations(log, preparation_turn + 1, end))
    write_json(output / 'complete.json', dict(verified=True, turn=end))
    if natural_sacristan is not None:
        return dict(census=prepared, civic_start=civic_start)
    if switch_turn is not None:
        result = dict(census=prepared)
        if deferred_capacity:
            result['capacity_census'] = capacity_census
        if fixture == 'customer_frontier':
            result['frontier_start'] = frontier_start
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'output', 'candidate-source'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--recover-preferences-from', type=Path,
                        help="Restore an interrupted session's original mod and auto-start settings before the first arm")
    for name in ('start', 'end'):
        parser.add_argument('--' + name, type=int, required=True)
    parser.add_argument('--arm', choices=('control', 'treatment'), action='append')
    parser.add_argument('--replay-ce',type=Path,help='Use this pinned Dev CE package in both replay arms')
    parser.add_argument('--connection-prototype',action='store_true',help='Stage the anchored connection Lua scripts over the saved package')
    parser.add_argument('--matched-connection-switch',action='store_true',
                        help='Use the same staged policy in both arms, with only anchored connections switched')
    parser.add_argument('--connection-switch-turn',type=int,
                        help='Use the identical inactive pre-roll in both arms before switching the experiment on')
    parser.add_argument('--paired-layout-csc', type=Path,
                        help='Shared installed CSC snapshot for a matched switch or a control-only connection scout')
    parser.add_argument('--paired-layout-switch-turn', type=int,
                        help='Switch prospective placement at the loaded turn or after a matched inactive pre-roll')
    parser.add_argument('--provider-decline-switch', action='store_true',
                        help='Keep prospective placement in both arms and switch only fulfilled provider admission')
    parser.add_argument('--connection-scout', nargs=2, action='append', type=int, default=[], metavar=('PLAYER','CITY'),
                        help='Read the existing native score and choice journal for this AI city')
    parser.add_argument('--land-target', nargs=4, action='append', type=int, default=[],
                        metavar=('PLAYER','CITY','DISTRICT','PLOT'),
                        help='Observe price, buyer and terrain legality for a customer site in a scout city')
    parser.add_argument('--connection-timing-player', type=int,
                        help='Time the existing connection planner and site quotes for one AI seat')
    fixtures = parser.add_mutually_exclusive_group()
    fixtures.add_argument('--market-rebuild', action='store_true',
                          help='Controlled player-5 Market rebuild on the qualified turn-200 checkpoint')
    fixtures.add_argument('--storekeeper-preparation', action='store_true',
                          help='Add the same missing Mill on both turn-50 copies to isolate Feudalism')
    fixtures.add_argument('--entertainment-preparation', action='store_true',
                          help='Prepare the adjacent Arena on both turn-200 copies to isolate Zoo production')
    fixtures.add_argument('--sacristan-preparation', action='store_true',
                          help='Reset Divine Right and add the missing Tailor beside an existing Temple on both copies')
    fixtures.add_argument('--sacristan-natural', action='store_true',
                          help='Prepare the Tailor and Temple at turn 55 before Divine Right starts')
    fixtures.add_argument('--connection-capacity', action='store_true',
                          help='Open one district slot in both copies of the scoped Continents turn-150 save')
    fixtures.add_argument('--stirling-capacity', action='store_true',
                          help='Open the same district slot in Stirling at the matched turn-127 boundary')
    fixtures.add_argument('--quito-capacity', action='store_true',
                          help='Open the same district slot in Quito at the matched turn-224 boundary')
    args = parser.parse_args()
    # The connection replay may need to cross a reservation change and still
    # leave time to complete the selected district. Native scouting is scoped
    # to a few named cities throughout that window.
    max_turns = 65 if args.connection_scout else 50 if args.sacristan_natural else 30 if args.storekeeper_preparation else 25
    if args.paired_layout_csc and args.connection_scout:
        # An archived checkpoint can predate the matched switch substantially.
        # Keep the ordinary qualification endpoint and native record bounds,
        # and leave enough later turns to observe both districts completing.
        max_turns = 250-args.start
    require(0 < args.end - args.start <= max_turns, f'Replay window must be 1 to {max_turns} turns')
    require(not args.market_rebuild or args.start == 200, 'Market fixture requires the turn-200 source')
    require(not args.storekeeper_preparation or args.start == 50, 'Storekeeper fixture requires the turn-50 source')
    require(not args.entertainment_preparation or args.start == 200, 'Entertainment fixture requires the turn-200 source')
    require(not args.sacristan_preparation or args.start == 100, 'Sacristan fixture requires the turn-100 source')
    require(not args.sacristan_natural or (args.start == 50 and args.end > 55),
            'Natural Sacristan fixture needs the turn-50 source and an endpoint after preparation at turn 55')
    require(not args.connection_capacity or (args.connection_prototype and args.start==150),
            'Connection capacity fixture requires the anchored prototype comparison at turn 150')
    require(not args.matched_connection_switch or (args.connection_prototype and not args.sacristan_natural),
            'A matched connection switch requires the anchored policy and one unchanged setup')
    require(args.connection_timing_player is None or (args.connection_prototype and args.end - args.start <= 5),
            'Connection timing is for short diagnostic replays of the anchored planner')
    require(not args.stirling_capacity or (args.start==100 and args.connection_switch_turn==127),
            'Stirling capacity fixture starts on turn 100 and prepares on 127')
    fixture = next((name for enabled, name in ((args.market_rebuild, 'market'),
                    (args.storekeeper_preparation, 'storekeeper'), (args.entertainment_preparation, 'entertainment'),
                    (args.sacristan_preparation or args.sacristan_natural, 'sacristan'),
                    (args.connection_capacity, 'connection'), (args.stirling_capacity, 'stirling_capacity'),
                    (args.quito_capacity, 'quito_capacity'))
                    if enabled), None)
    arms=args.arm or ('control', 'treatment')
    paired_layout = args.paired_layout_csc.resolve(strict=True) if args.paired_layout_csc else None
    if paired_layout or args.paired_layout_switch_turn:
        require(paired_layout
                and not (args.connection_prototype or args.matched_connection_switch
                         or args.connection_switch_turn or args.replay_ce),
                'The paired-layout study uses one installed CSC pin and its archived CE build')
        if args.paired_layout_switch_turn is not None:
            require(fixture in (None, 'quito_capacity') and arms == ('control', 'treatment')
                    and args.start <= args.paired_layout_switch_turn < args.end,
                    'The paired-layout experiment needs both arms and a switch from start through end minus one')
        else:
            require(fixture is None and list(arms) == ['control'] and args.connection_scout,
                    'A no-switch paired-layout run is a control-only connection scout')
    require(not args.quito_capacity or (paired_layout and args.start == 200 and args.paired_layout_switch_turn == 224),
            'The Quito slot fixture needs the natural turn-200 replay and turn-224 preparation')
    require(not args.provider_decline_switch or (paired_layout and args.paired_layout_switch_turn == args.start
            and fixture is None and args.connection_scout and args.end-args.start <= 30),
            'The provider experiment needs a scoped matched replay at the loaded boundary')
    require(args.connection_switch_turn is None or (args.matched_connection_switch and fixture in (None, 'stirling_capacity')
            and len(arms)==2 and set(arms)=={'control','treatment'} and args.start < args.connection_switch_turn < args.end),
            'An inactive connection switch requires both matched arms and an interior turn without a setup fixture')
    preparation = None
    for arm in arms:
        candidate = args.candidate_source if arm == 'treatment' or args.sacristan_natural or args.matched_connection_switch else None
        natural = arm == 'treatment' if args.sacristan_natural else None
        connection = arm == 'treatment' if args.matched_connection_switch or paired_layout else None
        result = run_arm(args.source, args.output / arm, args.start, args.end, candidate, fixture,
                         natural_sacristan=natural, expected_preparation=preparation,
                         replay_ce=args.replay_ce,connection_prototype=args.connection_prototype,
                         connection_scout=args.connection_scout,connection_enabled=connection,
                         connection_switch_turn=args.connection_switch_turn,
                         connection_timing_player=args.connection_timing_player, paired_layout_csc=paired_layout,
                         paired_layout_switch_turn=args.paired_layout_switch_turn,
                         provider_decline_switch=args.provider_decline_switch,
                         recover_preferences_from=args.recover_preferences_from if arm == arms[0] else None,
                         land_targets=args.land_target)
        if result is not None:
            preparation = result
    if (args.matched_connection_switch or paired_layout) and set(arms)=={'control','treatment'}:
        a,b=(load(args.output / arm / 'inputs.json') for arm in ('control','treatment'))
        left,right=a['packages']['csc'],b['packages']['csc']
        differences={Path(name).as_posix() for name in left.keys() | right.keys() if left.get(name)!=right.get(name)}
        expected=set() if args.connection_switch_turn is not None or paired_layout else {CONNECTION_ADAPTER}
        require(differences==expected and a['checkpoint']==b['checkpoint']
                and a['connection_enabled'] is False and b['connection_enabled'] is True
                and a['packages']['ce']==b['packages']['ce'], 'Matched connection replay package or checkpoint drift')
        policy = 'providerDecline' if args.provider_decline_switch else ('prospective' if paired_layout else 'anchored')
        write_json(args.output / 'matched-switch.json',dict(verified=True,checkpoint=a['checkpoint'],
                   switch_turn=args.paired_layout_switch_turn or args.connection_switch_turn,
                   policy=policy,changed=sorted(differences)))
