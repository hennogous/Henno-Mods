"""Start an ordinary Bakers development game with separate local CSC and CE packages."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import traceback
import uuid
import xml.etree.ElementTree as ET

from ce_replay import DLL, HOTFIX_EXE_SHA, verify_modules
from driver import (
    HERE, HOTFIX_SHA, STUDY, XP2_IMAGE_SIZE, HeldProcess, NativeSession, configure, flags, launch, load, lua,
    make_probe_controller, manifest, native_inventory, parse, read, require,
    restore_preferences, sha, write_json,
)
from full_game_controller.checkpoint import save_inactive_boundary
from storekeeper_runtime import audit


LOGS = ('Lua.log', 'Database.log', 'Modding.log', 'AI_CityBuild.csv', 'AI_Research.csv',
        'AI_Behavior_Trees.csv', 'City_BuildQueue.csv', 'UnitOperations.log')
MAPS = ('Continents', 'Pangaea', 'Fractal')
MAP_SIZES = {'small': (6, 9), 'standard': (8, 12)}  # Major and city-state counts.


def host(map_seed, game_seed, map_name, map_size):
    if map_name not in MAPS:
        raise ValueError('Unknown map script')
    majors, city_states = MAP_SIZES[map_size]
    return f"""
GameConfiguration.SetToDefaults()
GameConfiguration.SetRuleSet('RULESET_EXPANSION_2')
BuildHeadlessGameSetup()
RebuildPlayerParameters(true)
GameSetup_RefreshParameters()
MapConfiguration.SetScript('{map_name}.lua')
MapConfiguration.SetMapSize('MAPSIZE_{map_size.upper()}')
GameConfiguration.SetParticipatingPlayerCount({majors})
GameConfiguration.SetValue('CITY_STATE_COUNT',{city_states})
GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE')
GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE')
MapConfiguration.SetValue('RANDOM_SEED',{map_seed})
GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',{game_seed})
GameConfiguration.SetStartEra(DB.MakeHash('ERA_ANCIENT'))
ReleasePlayerParameters()
HideGameSetup()
Automation.SetAutoStartEnabled(true)
Network.HostGame(ServerType.SERVER_TYPE_NONE)
"""


def package_identity(package):
    metadata, = package.glob('*.modinfo')
    root = ET.parse(metadata).getroot()
    return str(uuid.UUID(root.attrib['id'])), root


def untuned_manifest(root):
    """Derive the control manifest by removing only the runtime policy action."""
    actions = root.find('InGameActions')
    publisher, = (node for node in actions if node.get('id') == 'CSC_AI_BakersGameplay')
    require(publisher.tag == 'AddGameplayScripts'
            and [file.text for file in publisher.findall('File')] == ['Lua_UI/AI/CSC_AI_BakersGameplay.lua'],
            'The publisher action must have exactly one CSC policy script')
    actions.remove(publisher)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def check_native_status(status, untuned):
    require(status['ready'] == 1 and status['faults'] == 0, 'CE district scoring unavailable or faulted')
    if untuned:
        require(all(status[key] == 0 for key in ('enabled', 'version', 'entries', 'matched', 'changed')),
                'CSC AI policy unexpectedly active in the control')
    else:
        require(status['enabled'] == 1 and status['version'] > 0, 'Integrated CSC AI policy did not publish')


def capture_census(controller, players, turn, path):
    scope = "CSC_BAKERS_COHORT_MODE='census'\nCSC_BAKERS_CENSUS_PLAYERS=" + lua(sorted(players)) + '\n'
    raw = controller.cmd(scope + read(HERE / 'retention_cohort.lua'),
                         'CSC_AdjacencyGameplay', f'chain-census-{turn}')
    path.write_text(raw, encoding='utf-8')
    rows = re.findall(r'CSC_BAKERS_CENSUS_(?!END\t)([A-Z]+\t[^\r\n]+)', raw)
    footer = re.findall(r'CSC_BAKERS_CENSUS_END\t(\d+)\t(\d+)', raw)
    require(footer == [(str(turn), str(len(rows)))], 'Incomplete Bakers endpoint census')
    return sorted(rows)


def capture_builders(controller, player, turn, path):
    code = f"""
local player = assert(Players[{player}])
local builder = assert(GameInfo.Units.UNIT_BUILDER).Index
for _, unit in player:GetUnits():Members() do
    if unit:GetType() == builder then
        print(string.format('CSC_BUILDER %d %d %d %d', unit:GetID(), unit:GetX(), unit:GetY(), unit:GetBuildCharges()))
    end
end
print('CSC_BUILDER_TURN=' .. Game.GetCurrentGameTurn())
"""
    raw = controller.cmd(code, 'GameCore_Tuner', f'supplier-builder-census-{turn}')
    require(parse(raw, 'CSC_BUILDER_TURN') == turn, 'Builder census clock differs')
    rows = [dict(unit=int(unit), x=int(x), y=int(y), charges=int(charges))
            for unit, x, y, charges in re.findall(r'CSC_BUILDER (\d+) (\d+) (\d+) (\d+)', raw)]
    write_json(path, rows)


def capture_wind_mill_readiness(controller, player, city, turn, path):
    code = f"""
local city = assert(Players[{player}]:GetCities():FindID({city}))
local mill = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL)
local build = assert(city:GetBuildQueue())
local available = build:CanProduce(mill.Hash, false, true)
assert(type(available) == 'boolean')
print(string.format('CSC_WIND_MILL={{"index":%d,"turn":%d,"available":%s}}',
    mill.Index, Game.GetCurrentGameTurn(), tostring(available)))
"""
    row = parse(controller.cmd(code, 'PlotInfo', f'wind-mill-readiness-{turn}'), 'CSC_WIND_MILL')
    # The UI cache can lag the inactive GameCore boundary by one turn.
    require(row['turn'] in (turn, turn - 1), 'Wind Mill readiness clock differs')
    write_json(path, row)
    return row['index']


def watch_supplier_access(controller, player, plot):
    code = f"""
local playerID, target = {player}, assert(Map.GetPlotByIndex({plot}))
local builder = assert(GameInfo.Units.UNIT_BUILDER).Index
local function snapshot()
    local turn = Game.GetCurrentGameTurn()
    for _, unit in Players[playerID]:GetUnits():Members() do
        if unit:GetType() == builder then
            print('CSC_SUPPLIER_BUILDER', turn, unit:GetID(), unit:GetX(), unit:GetY(), unit:GetBuildCharges())
        end
    end
    for _, unit in ipairs(Units.GetUnitsInPlot(target) or {{}}) do
        print('CSC_SUPPLIER_OCCUPANT', turn, unit:GetOwner(), unit:GetID(), GameInfo.Units[unit:GetType()].UnitType)
    end
    print('CSC_SUPPLIER_ACCESS_END', turn, target:GetOwner(), target:GetImprovementType())
end
snapshot()
Events.PlayerTurnDeactivated.Add(function(id)
    if id == playerID then
        local ok, message = pcall(snapshot)
        if not ok then print('CSC_SUPPLIER_ACCESS_FAULT', message) end
    end
end)
print('CSC_SUPPLIER_ACCESS_INSTALLED')
"""
    raw = controller.cmd(code, 'CSC_AdjacencyGameplay', 'install-supplier-access-watch')
    require('CSC_SUPPLIER_ACCESS_INSTALLED' in raw, 'Supplier movement watch was not installed')


def summarize_run(out, players, start, endpoint, untuned, checkpoint):
    require(load(out / 'session-closed.json')['verified'], 'Expected a closed development run')
    log = read(out / 'Lua.log')
    published = 'CSC_AI_BAKERS_DISTRICTS turn=' in log
    require('CSC_AI_BAKERS_DISTRICTS_FAILED' not in log and published != untuned,
            'Unexpected CSC policy publication in the development arm')
    require('CSC_AI_BAKERS_PLACEMENT_FAILED' not in log, 'CSC placement scan faulted during the run')
    placement_bids = {int(turn): int(count) for turn, count in
                      re.findall(r'CSC_AI_BAKERS_PLACEMENT turn=(\d+) bids=(\d+)', log)}
    score_samples, incomplete = {}, set()
    for turn, version, payload in re.findall(
            r'CSC_AI_BAKERS_DISTRICT_SAMPLES turn=(\d+) previousVersion=(\d+) samples=([^\r\n]*)', log):
        # Civ can cut off a long optional telemetry line. Preserve the raw
        # log and mark that batch unavailable without dropping Service evidence.
        try:
            rows = json.loads(payload)
        except json.JSONDecodeError:
            incomplete.add(int(turn))
            continue
        key = int(turn), int(version)
        score_samples.setdefault(key, []).extend(rows)
    result = audit(log, players, expected_turns=range(start + 1, endpoint))
    write_json(out / 'result.json', dict(closed=True, reached=endpoint, placement_bids=placement_bids,
        district_score_samples=[dict(turn=turn, previous_version=version, rows=rows)
                                for (turn, version), rows in score_samples.items()],
        incomplete_district_sample_turns=sorted(incomplete),
        storekeeper=result, checkpoint=checkpoint))


def run(args):
    out, mods = args.output.resolve(), args.mods.resolve(strict=True)
    ce, csc = (path.resolve(strict=True) for path in (args.ce, args.csc))
    ce_id, _ = package_identity(ce)
    csc_id, csc_manifest = package_identity(csc)
    require(ce_id != csc_id and csc_manifest.find(f"Dependencies/Mod[@id='{ce_id}']") is not None,
            'The staged CSC manifest must depend on the separate local CE package')
    local = {ce: mods / 'CSC Bakers Development CE', csc: mods / 'CSC Bakers Development Mod'}
    require(not out.exists() and not native_inventory() and all(not path.exists() for path in local.values()),
            'Fresh output, unused development paths and exclusive native ownership required')
    require(not any(path.is_relative_to(mods) for path in (out, ce, csc)),
            'Staging and output must be outside the installed Mods directory')
    require(not args.saves or args.saves.is_dir(), 'The native save directory must already exist')
    require(sha(args.binary) == HOTFIX_EXE_SHA, 'The validated DX11 executable is required')
    ce_dll = Path('Binaries/Win64') / DLL
    require(sha(ce / ce_dll) == args.ce_sha256, 'The staged CE DLL hash differs from the expected build')
    pins = {source: manifest(source) for source in local}
    installed_pins = dict(pins)
    if args.untuned:
        csc_file, = (item.name for item in csc.glob('*.modinfo'))
        control_manifest = untuned_manifest(csc_manifest)
        installed_pins[csc] = dict(pins[csc])
        installed_pins[csc][csc_file] = dict(size=len(control_manifest),
                                             sha256=hashlib.sha256(control_manifest).hexdigest())
    protocol = dict(map=args.map, map_size=args.map_size, map_seed=args.map_seed, game_seed=args.game_seed,
        endpoint=args.through, interval_minutes=args.interval_minutes, csc=csc_id, ce=ce_id,
        untuned=args.untuned, development=True, ordinary_setup=True,
        fresh_game=True, qualification=False, external_policy=False, gameplay_interventions=False,
        input_digests=[hashlib.sha256(json.dumps(pins[source], sort_keys=True).encode()).hexdigest()
                       for source in (ce, csc)])
    if args.saves:
        protocol['archive_endpoint'] = True
    start = 1
    prior = args.resume_from.resolve(strict=True) if args.resume_from else None
    if prior:
        previous = load(prior / 'protocol.json')
        checkpoint_input = load(prior / 'checkpoint.json')
        start = checkpoint_input['turn']
        expected = dict(protocol, endpoint=start, interval_minutes=previous['interval_minutes'])
        if 'diagnostic_start' in previous:
            # A saved intervention stays labelled as such even when the
            # follow-through starts with the integrated policy alone.
            expected.update(fresh_game=False, ordinary_setup=False, diagnostic_start=previous['diagnostic_start'],
                            gameplay_interventions=previous['gameplay_interventions'])
            for key in ('diagnostic_extra_pasture_q8', 'diagnostic_source_sha256', 'diagnostic_movement_only',
                        'diagnostic_calibration_build'):
                if key in previous:
                    expected[key] = previous[key]
        if args.calibration_replay:
            require(checkpoint_input['sha256'] == 'b3d6cc1aa78e8a156e60c4b110b229a3631ccaed57e24d7883aaca549fbc9545'
                    and args.supplier == [2, 196610, 2311, 2312] and args.through == 122,
                    'Calibration uses the exact Alexandria movement checkpoint')
            prior_packages = {row['install']: row['files'] for row in load(prior / 'packages.json').values()}
            permitted = {
                ce: {str(ce_dll)},
                csc: {str(Path('Lua_UI/AI') / name) for name in (
                    'CSC_AI_BakersGameplay.lua', 'CSC_AI_DistrictBridge.lua', 'CSC_AI_QuarterPlacement.lua')},
            }
            for source, destination in local.items():
                old, new = prior_packages[str(destination)], pins[source]
                changed = {name for name in old.keys() | new.keys() if old.get(name) != new.get(name)}
                require(changed == permitted[source], 'Unexpected file changes in the calibration package')
            expected['input_digests'] = previous['input_digests']
            protocol['diagnostic_calibration_build'] = True
        require(previous == expected
                and load(prior / 'session-closed.json')['verified'],
                'Diagnostic continuation requires the same closed package and setup')
        require(checkpoint_input['verified'] and sha(checkpoint_input['archive']) == checkpoint_input['sha256']
                and start < args.through <= start + 15, 'Expected an exact bounded continuation')
        protocol.update(fresh_game=False, ordinary_setup=False, diagnostic_start=start,
                        diagnostic_source_sha256=checkpoint_input['sha256'],
                        gameplay_interventions=previous['gameplay_interventions'])
        if args.movement_only:
            protocol['diagnostic_movement_only'] = True
        if args.alexandria_bid:
            matched_endpoints = {
                'e47f3982a1cf4b9e69ec3950e86d009fd08f9fdd07a4ab7cc4e3ff0995f7d769': 112,
                'b3d6cc1aa78e8a156e60c4b110b229a3631ccaed57e24d7883aaca549fbc9545': 122,
            }
            require(args.supplier == [2, 196610, 2311, 2312]
                    and matched_endpoints.get(checkpoint_input['sha256']) == args.through,
                    'The measured Pasture comparison requires the matched Alexandria checkpoint')
            protocol['diagnostic_extra_pasture_q8'] = 6144
            protocol['gameplay_interventions'] = True
    other_source = None
    if args.matched_source:
        other_source = args.matched_source.resolve(strict=True)
        previous = load(other_source.parent / 'protocol.json')
        require(previous == dict(protocol, untuned=not args.untuned),
                'Matched arms require the same staged content and setup with opposite policy states')
        require(load(other_source.parent / 'session-closed.json')['verified'], 'Matched arm did not close cleanly')
    out.mkdir(parents=True)
    write_json(out / 'packages.json', {str(source): dict(install=str(local[source]), files=files)
                                       for source, files in installed_pins.items()})
    write_json(out / 'protocol.json', protocol)
    controller = make_probe_controller(out, user_root=args.user_root)
    controller.study_endpoint = args.through
    # A long qualification window stays continuous for the native Service
    # watcher. The shared controller still fails a ten-minute single-turn stall.
    controller.autoplay_interval_seconds = args.interval_minutes * 60
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    players = set()
    copied = []
    checkpoint = None
    observer = None
    trace_name = 'supplier-trace.json' if args.supplier else 'wind-mill-trace.json'

    def verify_packages():
        for source in copied:
            require(manifest(local[source]) == installed_pins[source], f'Installed development package changed: {source}')

    def source_gate():
        mode = 'local untuned = ' + str(args.untuned).lower() + '\n'
        raw = controller.cmd(mode + """
assert(Game.GetCurrentGameTurn()==1 and Players[0]:IsHuman())
assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER)
assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT==nil and GameInfo.CSC_AI_Profile==nil,'Legacy AI tuning loaded')
local speed=GameConfiguration.GetGameSpeedType()
assert(speed=='GAMESPEED_ONLINE' or GameInfo.GameSpeeds[speed].GameSpeedType=='GAMESPEED_ONLINE')
local map={}
for index=0,Map.GetPlotCount()-1 do
    local plot=Map.GetPlotByIndex(index)
    map[#map+1]=table.concat({plot:GetTerrainType(),plot:GetFeatureType(),plot:GetResourceType(),
        plot:GetResourceCount(),plot:GetRiverCrossingCount(),plot:IsHills() and 1 or 0},',')
end
local width,height=Map.GetGridSize()
print('CSC_FRESH_MAP=['..table.concat({width,height,DB.MakeHash(table.concat(map,';'))},',')..']')
local ids={}
for _,p in ipairs(PlayerManager.GetAliveMajors()) do
    local id=p:GetID()
    local original=Game:GetProperty('CSC_AI_OriginalHuman_'..id)
    if untuned then assert(original==nil) else assert(original==(p:IsHuman() and 1 or 0)) end
    local config=assert(PlayerConfigurations[id])
    local start=p.GetStartingPlot and p:GetStartingPlot()
    print('CSC_FRESH_START='..table.concat({id,assert(config:GetLeaderTypeName()),
        start and start:GetIndex() or -1},','))
    for _,unit in p:GetUnits():Members() do
        print('CSC_FRESH_UNIT='..table.concat({id,unit:GetID(),GameInfo.Units[unit:GetType()].UnitType,
            unit:GetX(),unit:GetY()},','))
    end
    if not p:IsHuman() then
        assert(not p:GetCulture():HasCivic(GameInfo.Civics.CIVIC_CRAFTSMANSHIP.Index))
        ids[#ids+1]=id
    end
end
print('CSC_FRESH_AI=['..table.concat(ids,',')..']')
print('CSC_FRESH_CE='..CE_AIDistrictScoresStatus())
""", 'GameCore_Tuner', 'fresh-start-identity')
        players.update(parse(raw, 'CSC_FRESH_AI'))
        status = parse(raw, 'CSC_FRESH_CE')
        map_signature = parse(raw, 'CSC_FRESH_MAP')
        starts = [dict(player=int(pid), leader=leader, plot=int(plot)) for pid, leader, plot in
                  re.findall(r'CSC_FRESH_START=(\d+),([A-Za-z0-9_]+),(-?\d+)', raw)]
        units = [dict(player=int(pid), unit=int(uid), type=kind, x=int(x), y=int(y)) for pid, uid, kind, x, y in
                 re.findall(r'CSC_FRESH_UNIT=(\d+),(\d+),([A-Za-z0-9_]+),(\d+),(\d+)', raw)]
        majors, _ = MAP_SIZES[args.map_size]
        require(len(players) == majors - 1 and 0 not in players, 'Original AI roster differs from the setup')
        require(len(starts) == majors and {row['player'] for row in starts} == players | {0},
                'Normal-start roster evidence is incomplete')
        require({row['player'] for row in units} == players | {0}, 'Normal-start unit census is incomplete')
        check_native_status(status, args.untuned)
        state = dict(original_ai=sorted(players), native=status, map_signature=map_signature,
            starts=sorted(starts, key=lambda row: row['player']),
            units=sorted(units, key=lambda row: (row['player'], row['unit'])))
        write_json(out / 'source.json', state)
        if other_source:
            other = load(other_source)
            for key in ('original_ai', 'map_signature', 'starts', 'units'):
                require(state[key] == other[key], f'Matched source differs in {key}')
        return True

    def continuation_gate():
        identity = load(prior / 'source.json')
        players.update(identity['original_ai'])
        archived = re.findall(r'CSC_BAKERS_CENSUS_(?!END\t)([A-Z]+\t[^\r\n]+)',
                              read(prior / 'chain-census.txt'))
        loaded = capture_census(controller, players, start, out / 'source-census.txt')
        require(sorted(archived) == loaded, 'The loaded Stage 2 census differs from the saved endpoint')
        pid, city, quarter, *_ = args.supplier or args.wind_mill
        require(pid in players and any(row.startswith(f'QUARTER\t{pid}\t{city}\t{quarter}\ttrue\tfalse\t')
                                       for row in loaded), 'The scoped Quarter is not a working AI district on this save')
        if args.supplier:
            plot = args.supplier[3]
            require(f'IMPROVEMENT\t{quarter}\t{plot}\tIMPROVEMENT_PASTURE\ttrue' in loaded
                    and any(row.startswith(f'NEIGHBOR\t{quarter}\t{plot}\t{pid}\t-1\tRESOURCE_CATTLE\t-\t')
                            for row in loaded), 'The scoped Cattle tile is not a missing supplier on this save')
        else:
            require(f'MILL\t{quarter}\tBUILDING_CSC_BAKERS_WIND_MILL\tabsent\t-1\ttrue' in loaded,
                    'The scoped Quarter does not have the expected missing unlocked Wind Mill')
        native = parse(controller.cmd('print("CSC_FRESH_CE="..CE_AIDistrictScoresStatus())',
                                      'GameCore_Tuner', 'diagnostic-start-status'), 'CSC_FRESH_CE')
        check_native_status(native, False)
        if args.calibration_replay:
            builder = parse(controller.cmd('print("CSC_FRESH_BUILDER="..CE_AIBuilderProtectionStatus())',
                                           'GameCore_Tuner', 'verify-calibrated-builder-cap'), 'CSC_FRESH_BUILDER')
            require(builder['ready'] == 1 and builder['faults'] == 0 and builder['maxBidQ8'] == 16384,
                    'The calibrated Builder cap is unavailable')
        write_json(out / 'source.json', identity)
        return True

    try:
        for source, destination in local.items():
            shutil.copytree(source, destination)
            copied.append(source)
            if args.untuned and source == csc:
                (destination / csc_file).write_bytes(control_manifest)
        verify_packages()
        session.start(lambda: launch(args, out))
        session.wait_context('MainMenu')
        # Enable the provider first. CSC has a real dependency in the local manifest.
        configure(controller, out, csc_id=ce_id)
        session.issue_once('enable-csc', f"""
local chosen
for _,m in ipairs(Modding.GetInstalledMods()) do
    if m.Id=='{csc_id}' then assert(not chosen); chosen=m end
end
assert(chosen and Modding.CanEnableMod(chosen.Handle)=='OK')
Modding.EnableMod(chosen.Handle,true)
""", 'MainMenu')
        session.wait_context('MainMenu', 90)
        require({key for key, enabled in flags(controller, 'verify-local-pair')['mods'].items() if enabled}
                == {ce_id, csc_id}, 'Expected only the two development packages')
        contexts = ('GameCore_Tuner', 'PlotInfo')
        if not args.untuned:
            contexts += ('CSC_AI_BakersGameplay',)
        if prior:
            session.load_once(checkpoint_input['native_save'], sha256=checkpoint_input['sha256'],
                              native_directory=args.saves, turn=start, contexts=(*contexts, 'CSC_AdjacencyGameplay'),
                              eligibility=continuation_gate)
        else:
            session.issue_once('host-normal-start', host(args.map_seed, args.game_seed, args.map, args.map_size), 'MainMenu')
            session.ready_after_issue(1, contexts, eligibility=source_gate)
        verify_modules(session, local[ce] / ce_dll, out, HOTFIX_SHA)
        raw = controller.cmd('CSC_BAKERS_STOREKEEPER_WATCH=true\n' + read(HERE / 'storekeeper_runtime.lua'),
                             'PlotInfo', 'install-storekeeper-watch')
        require('CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED' in raw, 'Storekeeper watch was not installed')
        if args.supplier:
            capture_builders(controller, args.supplier[0], start, out / 'source-builders.json')
            watch_supplier_access(controller, args.supplier[0], args.supplier[3])
        if args.probe_dependencies:
            dependencies = args.probe_dependencies.resolve(strict=True)
            sys.path.insert(0, str(dependencies))
            import frida
            require(frida.__version__ == '17.24.3' and Path(frida.__file__).resolve().is_relative_to(dependencies),
                    'Exact existing Frida package required')
            modules = load(out / 'loaded-modules.json')
            pid, city, *_ = args.supplier or args.wind_mill
            scope = dict(player=pid, city=city, cePath=modules[DLL]['path'])
            if args.supplier:
                plot = args.supplier[3]
                width = load(out / 'source.json')['map_signature'][0]
                pasture = parse(controller.cmd(
                    "print('CSC_PASTURE='..assert(GameInfo.Improvements.IMPROVEMENT_PASTURE).Index)",
                    'GameCore_Tuner', 'supplier-improvement-index'), 'CSC_PASTURE')
                scope.update(plot=plot, x=plot % width, y=plot // width, pasture=pasture)
                if args.alexandria_bid:
                    scope['extraPastureQ8'] = protocol['diagnostic_extra_pasture_q8']
                probe = HERE / 'pasture_recovery_observer.js'
                write_json(out / 'supplier-scope.json', scope)
            else:
                scope['mill'] = capture_wind_mill_readiness(controller, pid, city, start, out / 'source-mill.json')
                probe = HERE / 'mill_repair_observer.js'
                write_json(out / 'wind-mill-scope.json', scope)
            attachment = frida.attach(session.owner.pid)
            code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n" + '\n'.join(
                read(path) for path in (STUDY / 'observer.js', probe))
            script = attachment.create_script(code)
            script.load()
            observer = script
            spec = dict(path=modules['GameCore_XP2_FinalRelease.dll']['path'], image_size=XP2_IMAGE_SIZE)
            require(observer.exports_sync.init(spec, scope), 'Decision observer installation failed')
            observer.exports_sync.advance(start)
        controller.play(args.through)
        if observer:
            trace = observer.exports_sync.freeze()
            write_json(out / trace_name, trace)
            require(trace['fault'] is None and trace['active'] == 0, 'Native decision trace faulted')
        if args.supplier:
            capture_builders(controller, args.supplier[0], args.through, out / 'endpoint-builders.json')
        final = parse(controller.cmd('print("CSC_FRESH_CE="..CE_AIDistrictScoresStatus())',
                                     'GameCore_Tuner', 'fresh-endpoint-status'), 'CSC_FRESH_CE')
        write_json(out / 'native-endpoint.json', final)
        check_native_status(final, args.untuned)
        if args.saves:
            # Save the natural endpoint for follow-up diagnosis after the
            # continuous Service observation window has finished.
            state = controller.state_read('fresh-endpoint-save-check')
            if state['player0_alive']:
                checkpoint = save_inactive_boundary(controller, turn=args.through, name='CSC_BAKERS_FRESH',
                    native_directory=args.saves, archive=out / 'endpoint.Civ6Save')
                write_json(out / 'checkpoint.json', checkpoint)
            else:
                write_json(out / 'checkpoint-unavailable.json', state)
            capture_census(controller, players, args.through, out / 'chain-census.txt')
    except Exception as error:
        write_json(out / 'failure.json', dict(error=str(error), traceback=traceback.format_exc()))
        raise
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, out)
                          if (out / 'original-preferences.json').exists() else None,
                          restore_package=verify_packages,
                          before_menu=lambda: observer.exports_sync.freeze() if observer else None)
        if session.closed or (session.owner is None and not native_inventory()):
            for source in copied:
                local[source].rename(out / local[source].name)
            for name in LOGS:
                log = args.user_root / 'Logs' / name
                if session.closed and log.is_file():
                    shutil.copyfile(log, out / name)
    summarize_run(out, players, start, args.through, args.untuned, checkpoint)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'mods', 'user-root', 'binary', 'ce', 'csc'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('map-seed', 'game-seed', 'through'):
        parser.add_argument('--' + name, type=int, required=True)
    parser.add_argument('--map', choices=MAPS, default='Continents')
    parser.add_argument('--map-size', choices=MAP_SIZES, default='small')
    parser.add_argument('--interval-minutes', type=int, default=30,
                        help='Maximum wall time of one continuous autoplay window (30–240)')
    parser.add_argument('--untuned', action='store_true', help='Remove only the CSC runtime policy action locally')
    parser.add_argument('--matched-source', type=Path, help='Require initial state parity with the other arm')
    parser.add_argument('--saves', type=Path, help='Native Saves/Single path for an endpoint census and archived save')
    parser.add_argument('--resume-from', type=Path, help='Continue a closed tuned development run for diagnosis')
    target = parser.add_mutually_exclusive_group()
    target.add_argument('--supplier', type=int, nargs=4, metavar=('PLAYER', 'CITY', 'QUARTER', 'PLOT'))
    target.add_argument('--wind-mill', type=int, nargs=3, metavar=('PLAYER', 'CITY', 'QUARTER'))
    parser.add_argument('--probe-dependencies', type=Path, help='Existing exact Frida package directory')
    parser.add_argument('--alexandria-bid', action='store_true', help='Add a scoped +6144 Q8 in the matched replay only')
    parser.add_argument('--movement-only', action='store_true', help='Observe assigned Builder movement without native hooks')
    parser.add_argument('--calibration-replay', action='store_true', help='Verify the integrated bid on the exact Alexandria save')
    parser.add_argument('--ce-sha256', required=True)
    options = parser.parse_args()
    if options.resume_from:
        if not (options.saves and (options.supplier or options.wind_mill)
                and (options.probe_dependencies or options.movement_only)
                and not options.untuned and not options.matched_source):
            parser.error('A tuned continuation needs --saves, one target, and a diagnostic mode')
        if options.alexandria_bid and not options.supplier:
            parser.error('The Alexandria bid requires --supplier')
        if options.movement_only and (not options.supplier or options.probe_dependencies or options.alexandria_bid):
            parser.error('Movement-only diagnosis requires --supplier and uses no native probe or bid')
        if options.calibration_replay and not options.movement_only:
            parser.error('Integrated calibration requires --movement-only')
    elif (options.supplier or options.wind_mill or options.probe_dependencies or options.alexandria_bid
          or options.movement_only or options.calibration_replay):
        parser.error('Decision diagnostics require --resume-from')
    if not (3 <= options.through <= 250 and 0 < options.map_seed < 2**31 and 0 < options.game_seed < 2**31):
        parser.error('Use positive 31-bit seeds and an endpoint between turns 3 and 250')
    if not 30 <= options.interval_minutes <= 240:
        parser.error('Use a continuous window limit between 30 and 240 minutes')
    run(options)
