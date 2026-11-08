"""Start an ordinary Bakers development or qualification game with local CSC and CE packages."""

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
QUALIFICATION_SEEDS = {
    'Continents': (17260413, 27410653),
    'Pangaea': (18431267, 28681391),
    'Fractal': (19672039, 29812257),
}
QUALIFICATION_ENDPOINT = 249
QUALIFICATION_CENSUSES = [100, 150, 200, 240]


def check_qualification(args):
    if (args.resume_from or not args.saves or args.map_size != 'standard'
            or args.through != QUALIFICATION_ENDPOINT
            or (args.map_seed, args.game_seed) != QUALIFICATION_SEEDS[args.map]):
        raise ValueError('Qualification requires a fresh preselected Standard game through turn 249 and --saves')
    if args.untuned != bool(args.matched_source) or (args.untuned and args.map != 'Continents'):
        raise ValueError('The untuned Continents qualification arm requires the matching tuned source')


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


def archive_milestone_censuses(log, turns, out):
    active = None
    rows = []
    result = {turn: 'missing' for turn in turns}
    for kind, payload in re.findall(r'CSC_BAKERS_WATCH_CENSUS_([A-Z]+)\t([^\r\n]+)', log):
        if kind == 'BEGIN':
            active = int(payload)
            rows = []
            if active in result:
                result[active] = 'incomplete'
        elif kind == 'END':
            turn, count = map(int, payload.split('\t'))
            if turn == active and turn in result and len(rows) == count:
                prefix = 'CSC_BAKERS_CENSUS_'
                (out / f'chain-census-{turn}.txt').write_text(
                    ''.join(f'{prefix}{row}\n' for row in rows) + f'{prefix}END\t{turn}\t{count}\n',
                    encoding='utf-8')
                result[turn] = 'complete'
            active = None
        elif kind == 'FAULT':
            active = None
        elif active in result:
            rows.append(f'{kind}\t{payload}')
    return result


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


def capture_dam_sites(controller, player, city, plot, turn, path):
    code = f'local CSC_DAM_SITE_SCOPE = {lua([player, city, plot])}\n' + read(HERE / 'dam_sites.lua')
    raw = controller.cmd(code, 'PlotInfo', f'dam-sites-{turn}')
    require(parse(raw, 'CSC_DAM_TURN') == turn, 'Dam site survey clock differs')
    rows = []
    for kind, site, river, owner, resource, improvement, coverage in re.findall(
            r'CSC_DAM_(PROTECTED|LEGAL)\t(\d+)\t(-?\d+)\t(-?\d+)\t(-?\d+)\t(-?\d+)\t([0-9,]+|-)', raw):
        rows.append(dict(kind=kind.lower(), plot=int(site), river=int(river), owner=int(owner),
                         resource=int(resource), improvement=int(improvement),
                         floodplain=[] if coverage == '-' else [int(index) for index in coverage.split(',')]))
    require(rows and rows[0]['kind'] == 'protected' and rows[0]['plot'] == plot
            and len(rows) == parse(raw, 'CSC_DAM_COUNT') + 1
            and all(row['kind'] == 'legal' for row in rows[1:]),
            'Expected the protected floodplain and every legal Dam footprint')
    result = dict(player=player, city=city, turn=turn, protected=rows[0], legal=rows[1:])
    for row in result['legal']:
        row['sameFloodplain'] = bool(rows[0]['floodplain'] and row['river'] == rows[0]['river']
                                     and row['floodplain'] == rows[0]['floodplain'])
    write_json(path, result)
    return result


def capture_building_readiness(controller, player, city, turn, path,
                               building_type='BUILDING_CSC_BAKERS_WIND_MILL'):
    code = f"""
local city = assert(Players[{player}]:GetCities():FindID({city}))
local building = assert(GameInfo.Buildings[{json.dumps(building_type)}])
local build = assert(city:GetBuildQueue())
local available = build:CanProduce(building.Hash, false, true)
assert(type(available) == 'boolean')
print(string.format('CSC_BUILDING_READINESS={{"index":%d,"turn":%d,"available":%s}}',
    building.Index, Game.GetCurrentGameTurn(), tostring(available)))
"""
    row = parse(controller.cmd(code, 'PlotInfo', f'building-readiness-{turn}'), 'CSC_BUILDING_READINESS')
    # The UI cache can lag the inactive GameCore boundary by one turn.
    require(row['turn'] in (turn, turn - 1), 'Building readiness clock differs')
    write_json(path, row)
    return row['index']


def capture_quarter_repair_legality(controller, player, city, plot, turn, path):
    code = f"""
local city = assert(CityManager.GetCity({player}, {city}))
local plot = assert(Map.GetPlotByIndex({plot}))
local district = assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER)
local build = CityOperationTypes.BUILD
local params = {{ [CityOperationTypes.PARAM_DISTRICT_TYPE] = district.Hash,
    [CityOperationTypes.PARAM_X] = plot:GetX(), [CityOperationTypes.PARAM_Y] = plot:GetY() }}
local legal = CityManager.CanStartOperation(city, build, params, true)
assert(type(legal) == 'boolean')
local queue = city:GetBuildQueue()
print(string.format('CSC_QUARTER_REPAIR={{"turn":%d,"legal":%s,"productionCost":%d,"productionProgress":%.8g}}',
    Game.GetCurrentGameTurn(), tostring(legal), queue:GetDistrictCost(district.Index),
    queue:GetDistrictProgress(district.Index)))
"""
    row = parse(controller.cmd(code, 'PlotInfo', f'quarter-repair-legality-{turn}'), 'CSC_QUARTER_REPAIR')
    require(row['turn'] == turn, 'Quarter repair legality clock differs')
    write_json(path, row)


def capture_granary_exchange(controller, target, turn, path):
    player, city, _ = target
    scope = dict(player=player, city=city)
    code = 'CSC_BAKERS_TARGET=' + lua(scope) + '\n' + read(HERE / 'operating_effects.lua')
    raw = controller.cmd(code, 'PlotInfo', f'granary-exchange-{turn}')
    state = parse(raw, 'CSC_BAKERS_EFFECTS')
    require(state['turn'] in (turn, turn - 1), 'Granary exchange clock differs')
    write_json(path, state)


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


def summarize_run(out, players, start, endpoint, untuned, checkpoint, census_turns, *,
                  qualification=False, observer_boundary=None):
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
    require(not qualification or observer_boundary is None, 'Qualification requires uninterrupted sampling')
    expected_turns = set(range(start + 1, endpoint))
    # The diagnostic hands player 0 back before that clock's UI sample.
    # Account for just that deliberate pause and audit every other clock.
    skipped = []
    if observer_boundary in expected_turns and f'CSC_STOREKEEPER_END\t{observer_boundary}\t' not in log:
        expected_turns.remove(observer_boundary)
        skipped.append(observer_boundary)
    result = audit(log, players, expected_turns=expected_turns)
    result['unsampled_turns'] = skipped
    # This is the retention result for one game. Recovery, the matched arm
    # and the remaining seeds still need their own evidence.
    retention = {}
    if qualification:
        chains = [row for row in result['active_turns'] if row['turns'] >= 100]
        retention = dict(qualification_retention=dict(chains=chains, meets_target=len(chains) >= 3))
    write_json(out / 'result.json', dict(closed=True, reached=endpoint, placement_bids=placement_bids,
        district_score_samples=[dict(turn=turn, previous_version=version, rows=rows)
                                for (turn, version), rows in score_samples.items()],
        incomplete_district_sample_turns=sorted(incomplete),
        storekeeper=result, checkpoint=checkpoint,
        milestone_censuses=archive_milestone_censuses(log, census_turns, out), **retention))


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
        untuned=args.untuned, development=not args.qualification, ordinary_setup=True,
        fresh_game=True, qualification=args.qualification, external_policy=False, gameplay_interventions=False,
        input_digests=[hashlib.sha256(json.dumps(pins[source], sort_keys=True).encode()).hexdigest()
                       for source in (ce, csc)])
    if args.saves:
        protocol['archive_endpoint'] = True
    start = 1
    prior = args.resume_from.resolve(strict=True) if args.resume_from else None
    if prior:
        previous = load(prior / 'protocol.json')
        checkpoint_input = load(prior / ('observer-checkpoint.json' if args.mill_opening_components else 'checkpoint.json'))
        start = checkpoint_input['turn']
        repair_followthrough = args.repair_ce_replay and previous.get('diagnostic_repair_ce_replay') is True
        expected = dict(protocol, endpoint=start, interval_minutes=previous['interval_minutes'])
        if 'diagnostic_supplier_boundary' in previous:
            # A read-only observer can start before the archived endpoint.
            # Keep that provenance when replaying the endpoint for a new link.
            expected['diagnostic_supplier_boundary'] = previous['diagnostic_supplier_boundary']
        if args.mill_opening_components:
            endpoint = 116 if args.melbourne_builder_offers else 112
            require(start == 105 and args.through == endpoint and args.wind_mill == [4, 131073, 1423]
                    and checkpoint_input['sha256'] == 'dfc29fce2c25bb717bc3a2374640a37accc4052d0fd7989b753479153f1f83cd',
                    'The opening forecast uses the verified Melbourne turn-105 source')
            expected.update(endpoint=120, diagnostic_supplier_boundary=105)
        if 'census_turns' in previous:
            expected['census_turns'] = previous['census_turns']
        if 'diagnostic_start' in previous:
            # A saved intervention stays labelled as such even when the
            # follow-through starts with the integrated policy alone.
            expected.update(fresh_game=False, ordinary_setup=False, diagnostic_start=previous['diagnostic_start'],
                            gameplay_interventions=previous['gameplay_interventions'])
            for key in ('diagnostic_extra_pasture_q8', 'diagnostic_source_sha256', 'diagnostic_movement_only',
                        'diagnostic_calibration_build', 'diagnostic_mill_nomination_q8',
                        'diagnostic_mill_ce_replay', 'diagnostic_granary_nomination_q8', 'diagnostic_granary_ce_replay',
                        'diagnostic_dam_sites', 'diagnostic_water_mill_repair', 'diagnostic_quarter_repair_selector',
                        'diagnostic_quarter_repair_offer', 'diagnostic_mill_only_repair',
                        'diagnostic_repair_ce_replay'):
                if key in previous:
                    expected[key] = previous[key]
        if args.calibration_replay or args.mill_ce_replay or args.granary_ce_replay or (
                args.repair_ce_replay and not repair_followthrough):
            if args.calibration_replay:
                require(checkpoint_input['sha256'] == 'b3d6cc1aa78e8a156e60c4b110b229a3631ccaed57e24d7883aaca549fbc9545'
                        and args.supplier == [2, 196610, 2311, 2312] and args.through == 122,
                        'Calibration uses the exact Alexandria movement checkpoint')
                protocol['diagnostic_calibration_build'] = True
            elif args.mill_ce_replay:
                require(checkpoint_input['sha256'] == 'bb5280928bc4c47b62f5aa58304bba873d08856aef692b548bbf1b83836d77de'
                        and args.wind_mill == [4, 131073, 1423] and args.through == 139,
                        'CE nomination uses the exact Melbourne checkpoint')
                protocol['diagnostic_mill_ce_replay'] = args.mill_ce_replay
            elif args.granary_ce_replay:
                require(checkpoint_input['sha256'] == '1c6a36651a77d2361d06d651856eac8c57d6de921e2aede0fa4fca2d146f8843'
                        and args.granary == [1, 327684, 914] and args.through == 164,
                        'Integrated Granary nomination uses the exact Trebizond checkpoint')
                protocol['diagnostic_granary_ce_replay'] = True
            else:
                require(start == 200 and args.through in (206, 214) and not args.mill_only_repair
                        and args.water_mill_repair == [2, 196610, 2311]
                        and checkpoint_input['sha256'] == '641421d09b33a8f467b5d8635a98af1731c236edfa14d0acdbf95695ad5820d6',
                        'Integrated repair uses the exact Alexandria turn-200 fixture')
                protocol['diagnostic_repair_ce_replay'] = True
            prior_packages = {row['install']: row['files'] for row in load(prior / 'packages.json').values()}
            permitted = {
                ce: {str(ce_dll)},
                csc: {str(Path('Lua_UI/AI') / name) for name in (
                    'CSC_AI_BakersGameplay.lua', 'CSC_AI_DistrictBridge.lua', 'CSC_AI_QuarterPlacement.lua')},
            }
            if args.mill_ce_replay == 'parity':
                permitted[csc] = set()
            if args.granary_ce_replay:
                permitted = {ce: set(), csc: {str(Path(name)) for name in (
                    'Lua_UI/AI/CSC_AI_BakersGameplay.lua', 'Lua_UI/AI/CSC_AI_QuarterPlacement.lua',
                    'Lua_UI/Adjacencies/CSC_AdjacencyUI.lua',
                )}}
            for source, destination in local.items():
                old, new = prior_packages[str(destination)], pins[source]
                changed = {name for name in old.keys() | new.keys() if old.get(name) != new.get(name)}
                require(changed == permitted[source], 'Unexpected file changes in the calibration package')
            expected['input_digests'] = previous['input_digests']
        if repair_followthrough:
            require(args.water_mill_repair == [2, 196610, 2311]
                    and (start == 206 and args.through == 214 and not args.mill_only_repair
                         or start == 214 and args.through == 229 and args.mill_only_repair),
                    'Packaged repair follow-through uses the turn-206 or turn-214 archived endpoint')
            protocol['diagnostic_repair_ce_replay'] = True
        require(previous == expected
                and load(prior / 'session-closed.json')['verified'],
                'Diagnostic continuation requires the same closed package and setup')
        require(checkpoint_input['verified'] and sha(checkpoint_input['archive']) == checkpoint_input['sha256']
                and start < args.through <= start + 15, 'Expected an exact bounded continuation')
        protocol.update(fresh_game=False, ordinary_setup=False, diagnostic_start=start,
                        diagnostic_source_sha256=checkpoint_input['sha256'],
                        gameplay_interventions=previous['gameplay_interventions'])
        if 'diagnostic_supplier_boundary' in previous:
            protocol['diagnostic_supplier_boundary'] = previous['diagnostic_supplier_boundary']
        if args.mill_opening_components:
            protocol.update(diagnostic_mill_opening_components=True, gameplay_interventions=True)
        if args.dam_sites:
            protocol['diagnostic_dam_sites'] = args.dam_sites
        if args.water_mill_repair:
            protocol['diagnostic_water_mill_repair'] = args.water_mill_repair
        if args.mill_only_repair:
            protocol['diagnostic_mill_only_repair'] = True
        if args.quarter_repair_selector:
            protocol['diagnostic_quarter_repair_selector'] = True
        if args.quarter_repair_offer:
            require(start == 200 and args.through in (203, 214) and args.water_mill_repair == [2, 196610, 2311]
                    and checkpoint_input['sha256'] == '641421d09b33a8f467b5d8635a98af1731c236edfa14d0acdbf95695ad5820d6',
                    'The separate repair offer uses the exact Alexandria turn-200 fixture')
            protocol.update(diagnostic_quarter_repair_offer=True, gameplay_interventions=True)
        if args.melbourne_builder_offers:
            protocol['diagnostic_melbourne_builder_offers'] = True
        if args.melbourne_builder_recruitment:
            protocol['diagnostic_melbourne_builder_recruitment'] = True
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
        if args.melbourne_mill_bid:
            require(checkpoint_input['sha256'] == 'bb5280928bc4c47b62f5aa58304bba873d08856aef692b548bbf1b83836d77de'
                    and args.wind_mill == [4, 131073, 1423] and args.through == 134,
                    'Wind Mill nomination uses the exact Melbourne checkpoint')
            protocol['diagnostic_mill_nomination_q8'] = 448 * 256
            protocol['gameplay_interventions'] = True
        if args.trebizond_granary_bid:
            require(checkpoint_input['sha256'] == '1c6a36651a77d2361d06d651856eac8c57d6de921e2aede0fa4fca2d146f8843'
                    and args.granary == [1, 327684, 914] and args.through == 164,
                    'Granary nomination uses the exact Trebizond checkpoint')
            protocol['diagnostic_granary_nomination_q8'] = 288 * 256
            protocol['gameplay_interventions'] = True
        if args.granary_components:
            require(checkpoint_input['sha256'] == '1c6a36651a77d2361d06d651856eac8c57d6de921e2aede0fa4fca2d146f8843'
                    and args.granary == [1, 327684, 914] and args.through <= 154,
                    'Component capture uses a short read-only Trebizond window')
    require(all(start < turn < args.through for turn in args.census_turns),
            'Milestone censuses must be interior turns')
    if args.census_turns:
        protocol['census_turns'] = args.census_turns
    if args.observe_supplier_at is not None:
        protocol['diagnostic_supplier_boundary'] = args.observe_supplier_at
    other_source = None
    if args.matched_source:
        other_source = args.matched_source.resolve(strict=True)
        previous = load(other_source.parent / 'protocol.json')
        require(previous == dict(protocol, untuned=not args.untuned),
                'Matched arms require the same staged content and setup with opposite policy states')
        require(load(other_source.parent / 'session-closed.json')['verified'], 'Matched arm did not close cleanly')
        if args.qualification:
            require(other_source.name == 'source.json'
                    and load(other_source.parent / 'result.json')['reached'] == QUALIFICATION_ENDPOINT,
                    'The matched qualification arm must have archived its full tuned run')
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
    target = args.supplier or args.wind_mill or args.granary or args.dam_sites or args.water_mill_repair
    trace_name = ('dam-site-trace.json' if args.dam_sites else 'supplier-trace.json' if args.supplier else
                  'quarter-repair-trace.json' if args.quarter_repair_selector else
                  'water-mill-repair-trace.json' if args.water_mill_repair else
                  'granary-trace.json' if args.granary else 'wind-mill-trace.json')

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
        census_name = 'observer-start-census.txt' if args.mill_opening_components else 'chain-census.txt'
        archived = re.findall(r'CSC_BAKERS_CENSUS_(?!END\t)([A-Z]+\t[^\r\n]+)', read(prior / census_name))
        loaded = capture_census(controller, players, start, out / 'source-census.txt')
        require(sorted(archived) == loaded, 'The loaded Stage 2 census differs from the saved endpoint')
        pid, city, quarter, *_ = target
        quarters = [row.split('\t') for row in loaded if row.startswith(f'QUARTER\t{pid}\t')]
        if not args.dam_sites:
            quarters = [row for row in quarters if row[2] == str(city)]
        pillaged = 'true' if args.water_mill_repair and not args.mill_only_repair else 'false'
        require(pid in players and any(row[3:6] == [str(quarter), 'true', pillaged] for row in quarters),
                'The scoped completed AI Quarter differs from the expected repair state')
        if args.water_mill_repair:
            require(f'MILL\t{quarter}\tBUILDING_CSC_BAKERS_WATER_MILL\tpillaged\t{quarter}\ttrue' in loaded
                    and any(row.startswith(f'CUSTOMER\t{quarter}\t') and '\tworking\t' in row for row in loaded)
                    and any(row.startswith(f'NEIGHBOR\t{quarter}\t') and row.endswith('\ttrue\ttrue\tfalse')
                            and row.split('\t')[3:5] == [str(pid), '-1'] for row in loaded),
                    'Expected a pillaged Water Mill with a working supplier and customer')
        elif args.dam_sites:
            plot = args.dam_sites[3]
            working = [row.split('\t')[2] for row in loaded if
                       row.startswith(f'NEIGHBOR\t{quarter}\t') and row.endswith('\ttrue\ttrue\tfalse')
                       and row.split('\t')[3:5] == [str(pid), '-1']]
            require(working == [str(plot)], 'Expected the exact sole working Base supplier')
        elif args.supplier:
            plot = args.supplier[3]
            require(f'IMPROVEMENT\t{quarter}\t{plot}\tIMPROVEMENT_PASTURE\ttrue' in loaded
                    and any(row.startswith(f'NEIGHBOR\t{quarter}\t{plot}\t{pid}\t-1\tRESOURCE_CATTLE\t-\t')
                            for row in loaded), 'The scoped Cattle tile is not a missing supplier on this save')
        elif args.granary:
            require(any(row.startswith(f'CUSTOMER\t{quarter}\t{city}\t')
                        and row.endswith('\tBUILDING_GRANARY\tabsent\t-1') for row in loaded),
                    'The scoped Quarter lacks the expected adjacent Granary host')
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
        if args.mill_opening_components:
            # A controlled opening fixture: preserve the Rice and Granary
            # while removing only the Farm. The native probe writes no scores.
            source = sorted(re.findall(r'CSC_BAKERS_CENSUS_(?!END\t)([A-Z]+\t[^\r\n]+)',
                                       read(out / 'source-census.txt')))
            healthy = 'NEIGHBOR\t1423\t1498\t4\t-1\tRESOURCE_RICE\tIMPROVEMENT_FARM\ttrue\ttrue\tfalse'
            bare = 'NEIGHBOR\t1423\t1498\t4\t-1\tRESOURCE_RICE\t-\ttrue\tfalse\tfalse'
            require(healthy in source and 'CUSTOMER\t1423\t131073\t1422\tBUILDING_GRANARY\tworking\t1422' in source,
                    'The opening fixture requires the verified Rice Farm and working Granary')
            session.issue_once('remove-melbourne-rice-farm', """
local plot = assert(Map.GetPlotByIndex(1498))
assert(plot:GetOwner()==4 and plot:GetDistrictType()==-1 and not plot:IsImprovementPillaged())
assert(plot:GetResourceType()==GameInfo.Resources.RESOURCE_RICE.Index)
assert(plot:GetImprovementType()==GameInfo.Improvements.IMPROVEMENT_FARM.Index)
ImprovementBuilder.SetImprovementType(plot, -1)
""", 'GameCore_Tuner')
            prepared = capture_census(controller, players, start, out / 'opening-start-census.txt')
            require(prepared == sorted(bare if row == healthy else row for row in source),
                    'The opening preparation changed another census fact')
            capture_builders(controller, 4, start, out / 'opening-builders.json')
            economy = parse(controller.cmd("""
local city = assert(Players[4]:GetCities():FindID(131073))
local queue = city:GetBuildQueue()
local builder = assert(GameInfo.Units.UNIT_BUILDER)
local mill = assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL)
local engineer = assert(GameInfo.PseudoYields.PSEUDOYIELD_GPP_ENGINEER)
print(string.format('CSC_OPENING_ECONOMY={"turn":%d,"foodSurplus":%.8g,"builderProduction":%d,'
    .. '"millProduction":%d,"engineerPseudoYieldIndex":%d}',
    Game.GetCurrentGameTurn(), city:GetGrowth():GetFoodSurplus(), queue:GetUnitCost(builder.Index),
    queue:GetBuildingCost(mill.Index), engineer.Index))
""", 'PlotInfo', 'opening-economy'), 'CSC_OPENING_ECONOMY')
            require(economy['turn'] == start, 'Opening economy must match the inactive boundary')
            write_json(out / 'opening-economy.json', economy)
            if args.melbourne_builder_offers:
                raw = controller.cmd("""
for _, city in Players[4]:GetCities():Members() do
    print(string.format('CSC_OFFER_CITY %d %s', city:GetID(), city:GetName()))
end
print('CSC_OFFER_TURN=' .. Game.GetCurrentGameTurn())
""", 'GameCore_Tuner', 'opening-offer-cities')
                offer_cities = {int(city): name.strip() for city, name in
                                re.findall(r'CSC_OFFER_CITY (\d+) ([^\r\n]+)', raw)}
                require(parse(raw, 'CSC_OFFER_TURN') == start and len(offer_cities) == 6
                        and 131073 in offer_cities, 'Expected the six verified Australian cities')
                write_json(out / 'opening-offer-cities.json', offer_cities)
            prepared_save = save_inactive_boundary(controller, turn=start, name='CSC_BAKERS_MILL_OPENING',
                                                   native_directory=args.saves, archive=out / 'opening-source.Civ6Save')
            write_json(out / 'opening-checkpoint.json', prepared_save)
        raw = controller.cmd('CSC_BAKERS_STOREKEEPER_WATCH=true\n' + read(HERE / 'storekeeper_runtime.lua'),
                             'PlotInfo', 'install-storekeeper-watch')
        require('CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED' in raw, 'Storekeeper watch was not installed')
        if args.census_turns:
            scope = ("CSC_BAKERS_COHORT_MODE='census-watch'\nCSC_BAKERS_CENSUS_PLAYERS="
                     + lua(sorted(players)) + '\nCSC_BAKERS_CENSUS_TURNS=' + lua(args.census_turns) + '\n')
            raw = controller.cmd(scope + read(HERE / 'retention_cohort.lua'),
                                 'CSC_AdjacencyGameplay', 'install-bakers-census-watch')
            require('CSC_BAKERS_CENSUS_WATCH_INSTALLED' in raw, 'Milestone census watch was not installed')
        probe_start = start
        if args.observe_supplier_at is not None:
            # Rotating autosaves can retain an AI-controlled return player.
            # Let the shared controller settle a supported inactive boundary
            # before inspecting the live supplier or attaching the observer.
            probe_start = args.observe_supplier_at
            controller.play(probe_start)
            census = capture_census(controller, players, probe_start, out / 'observer-start-census.txt')
            player, city, quarter, plot = args.supplier
            require(f'PLAYER\t{player}\ttrue\ttrue' in census
                    and any(row.startswith(f'QUARTER\t{player}\t{city}\t{quarter}\ttrue\tfalse\t')
                            for row in census)
                    and any(row.startswith(f'MILL\t{quarter}\t') and row.endswith(f'\tworking\t{quarter}\ttrue')
                            for row in census)
                    and any(row.startswith(f'CUSTOMER\t{quarter}\t') and '\tworking\t' in row
                            for row in census)
                    and any(row.startswith(f'NEIGHBOR\t{quarter}\t{plot}\t{player}\t-1\tRESOURCE_CATTLE\t-\t')
                            for row in census)
                    and f'IMPROVEMENT\t{quarter}\t{plot}\tIMPROVEMENT_PASTURE\ttrue' in census,
                    'The fresh diagnostic boundary does not have the expected missing Pasture')
            boundary = save_inactive_boundary(controller, turn=probe_start, name='CSC_BAKERS_SUPPLIER_OBSERVER',
                                              native_directory=args.saves, archive=out / 'observer-start.Civ6Save')
            write_json(out / 'observer-checkpoint.json', boundary)
        if args.supplier:
            capture_builders(controller, args.supplier[0], probe_start, out / 'source-builders.json')
            watch_supplier_access(controller, args.supplier[0], args.supplier[3])
        if args.dam_sites:
            pid, city, _, plot = args.dam_sites
            dam_sites = capture_dam_sites(controller, pid, city, plot, start, out / 'source-dam-sites.json')
        if args.water_mill_repair:
            capture_quarter_repair_legality(controller, *args.water_mill_repair, start,
                                            out / 'source-quarter-repair.json')
            if args.quarter_repair_offer or (args.repair_ce_replay and not args.mill_only_repair):
                require(load(out / 'source-quarter-repair.json')['legal'], 'Quarter repair is no longer legal')
            if args.repair_ce_replay:
                if args.mill_only_repair:
                    capture_building_readiness(controller, *args.water_mill_repair[:2], start,
                                               out / 'source-mill.json', 'BUILDING_CSC_BAKERS_WATER_MILL')
                    require(load(out / 'source-mill.json')['available'], 'Restored Quarter did not admit Mill repair')
                status = parse(controller.cmd("print('CSC_REPAIR='..assert(CE_AIDistrictRepairStatus)())",
                    'GameCore_Tuner', 'district-repair-capability'), 'CSC_REPAIR')
                require(status['ready'] == 1 and status['faults'] == 0, 'CE repair admission is unavailable')
                write_json(out / 'source-repair-status.json', status)
        if args.granary:
            pid, city, _ = args.granary
            granary_index = capture_building_readiness(controller, pid, city, start,
                out / 'source-granary.json', 'BUILDING_GRANARY')
            capture_granary_exchange(controller, args.granary, start, out / 'source-exchange.json')
        if args.mill_ce_replay:
            pid, city, _ = args.wind_mill
            capture_building_readiness(controller, pid, city, start, out / 'source-mill.json')
            require(load(out / 'source-mill.json')['available'], 'Wind Mill is no longer available')
            status = parse(controller.cmd(
                "print('CSC_NOMINATION='..assert(CE_AIBuildingNominationStatus)())",
                'GameCore_Tuner', 'building-nomination-capability'), 'CSC_NOMINATION')
            require(status['ready'] == 1 and status['faults'] == 0, 'CE nomination capability is unavailable')
            require(args.mill_ce_replay != 'parity' or status['entries'] == 0, 'Parity arm published a nomination')
            write_json(out / 'source-nomination.json', status)
        if args.probe_dependencies:
            dependencies = args.probe_dependencies.resolve(strict=True)
            sys.path.insert(0, str(dependencies))
            import frida
            require(frida.__version__ == '17.24.3' and Path(frida.__file__).resolve().is_relative_to(dependencies),
                    'Exact existing Frida package required')
            modules = load(out / 'loaded-modules.json')
            pid, city, *_ = target
            scope = dict(player=pid, city=city, cePath=modules[DLL]['path'])
            if args.dam_sites or args.quarter_repair_selector:
                width, height, *_ = load(out / 'source.json')['map_signature']
                district_type = 'DISTRICT_DAM' if args.dam_sites else 'DISTRICT_CSC_BAKERS_QUARTER'
                indices = parse(controller.cmd(f"""
local count = 0
for _ in GameInfo.Districts() do count = count + 1 end
print(string.format('CSC_DISTRICT_INDICES={{"district":%d,"districtCount":%d}}',
    GameInfo.Districts.{district_type}.Index, count))
""", 'GameCore_Tuner', 'selector-district-indices'), 'CSC_DISTRICT_INDICES')
                plots = ({dam_sites['protected']['plot'], *(row['plot'] for row in dam_sites['legal'])}
                         if args.dam_sites else {args.water_mill_repair[2]})
                scope.update(width=width, height=height, **indices, plots=sorted(plots))
                if args.quarter_repair_selector:
                    scope['traceTree'] = True
                if args.quarter_repair_offer:
                    scope['offerRepair'] = True
                probe = HERE / 'dam_site_observer.js'
            elif args.supplier:
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
            elif args.granary:
                scope['granary'] = granary_index
                if args.trebizond_granary_bid:
                    require(load(out / 'source-granary.json')['available'], 'Granary is no longer available')
                    scope['granaryNominationQ8'] = protocol['diagnostic_granary_nomination_q8']
                if args.granary_components:
                    scope['granaryComponents'] = True
                probe = HERE / 'mill_repair_observer.js'
            elif args.water_mill_repair:
                scope['mill'] = capture_building_readiness(controller, pid, city, start, out / 'source-mill.json',
                                                           'BUILDING_CSC_BAKERS_WATER_MILL')
                probe = HERE / 'mill_repair_observer.js'
            else:
                scope['mill'] = capture_building_readiness(controller, pid, city, start, out / 'source-mill.json')
                if args.mill_opening_components:
                    require(load(out / 'source-mill.json')['available'], 'The opening Wind Mill is unavailable')
                    scope['millOpeningComponents'] = True
                    scope['engineerPseudoYieldIndex'] = economy['engineerPseudoYieldIndex']
                    if args.melbourne_builder_offers:
                        scope['offerCities'] = sorted(offer_cities)
                    if args.melbourne_builder_recruitment:
                        scope['recruitmentBuilder'] = parse(controller.cmd(
                            "print('CSC_BUILDER_INDEX='..assert(GameInfo.Units.UNIT_BUILDER).Index)",
                            'GameCore_Tuner', 'recruitment-builder-index'), 'CSC_BUILDER_INDEX')
                if args.melbourne_mill_bid:
                    require(load(out / 'source-mill.json')['available'], 'Wind Mill is no longer available')
                    scope['nominationBidQ8'] = protocol['diagnostic_mill_nomination_q8']
                probe = HERE / 'mill_repair_observer.js'
            if args.granary_components or args.mill_opening_components:
                scope.update(parse(controller.cmd(
                    """local yields = GameInfo.Yields
print(string.format('CSC_YIELD_INDICES={"foodYieldIndex":%d,"productionYieldIndex":%d,"goldYieldIndex":%d}',
    yields.YIELD_FOOD.Index, yields.YIELD_PRODUCTION.Index, yields.YIELD_GOLD.Index))""",
                    'GameCore_Tuner', 'exchange-yield-indices'), 'CSC_YIELD_INDICES'))
            if args.dam_sites:
                write_json(out / 'dam-site-scope.json', scope)
            elif args.quarter_repair_selector:
                write_json(out / 'quarter-repair-scope.json', scope)
            elif args.water_mill_repair:
                write_json(out / 'water-mill-repair-scope.json', scope)
            elif not args.supplier:
                write_json(out / ('granary-scope.json' if args.granary else 'wind-mill-scope.json'), scope)
            attachment = frida.attach(session.owner.pid)
            probe_sources = [STUDY / 'observer.js', probe]
            if args.quarter_repair_offer:
                probe_sources.append(HERE / 'quarter_repair_offer.js')
            code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n" + '\n'.join(
                read(path) for path in probe_sources)
            script = attachment.create_script(code)
            if args.quarter_repair_offer:
                def archive_repair_receipt(message, _data):
                    payload = message.get('payload')
                    if (message['type'] == 'send' and isinstance(payload, dict)
                            and payload.get('kind') == 'quarter-repair-receipt'):
                        with (out / 'quarter-repair-receipts.ndjson').open('a', encoding='utf-8') as journal:
                            journal.write(json.dumps(payload['receipt']) + '\n')
                script.on('message', archive_repair_receipt)
            script.load()
            observer = script
            spec = dict(path=modules['GameCore_XP2_FinalRelease.dll']['path'], image_size=XP2_IMAGE_SIZE)
            require(observer.exports_sync.init(spec, scope), 'Decision observer installation failed')
            observer.exports_sync.advance(probe_start)
        controller.play(args.through)
        if observer:
            trace = observer.exports_sync.freeze()
            write_json(out / trace_name, trace)
            require(trace['fault'] is None and trace['active'] == 0, 'Native decision trace faulted')
            if args.quarter_repair_offer:
                require(sum(row['kind'] == 'repair-tree' for row in trace['records']) == 1,
                        'The exact separate Quarter repair tree did not reproduce once')
            if args.granary_components or args.mill_opening_components:
                components = trace['granaryComponents' if args.granary_components else 'millOpeningComponents']
                require(components['stopReason'] is None and not components['faults']
                        and components['counts']['BuildingValue']['accepted'] > 0,
                        'No complete fault-free exchange component capture')
            if args.trebizond_granary_bid:
                edits = [row for row in trace['records'] if row.get('deltaQ8', 0)]
                require(len(edits) == 1 and edits[0]['kind'] == 'granary-compare'
                        and edits[0]['deltaQ8'] == protocol['diagnostic_granary_nomination_q8'],
                        'The exact Granary comparison did not reproduce once')
        if args.supplier:
            capture_builders(controller, args.supplier[0], args.through, out / 'endpoint-builders.json')
        if args.melbourne_builder_recruitment:
            capture_builders(controller, 4, args.through, out / 'endpoint-builders.json')
        if args.granary:
            capture_granary_exchange(controller, args.granary, args.through, out / 'endpoint-exchange.json')
        final = parse(controller.cmd('print("CSC_FRESH_CE="..CE_AIDistrictScoresStatus())',
                                     'GameCore_Tuner', 'fresh-endpoint-status'), 'CSC_FRESH_CE')
        write_json(out / 'native-endpoint.json', final)
        check_native_status(final, args.untuned)
        if args.repair_ce_replay:
            status = parse(controller.cmd("print('CSC_REPAIR='..assert(CE_AIDistrictRepairStatus)())",
                'GameCore_Tuner', 'district-repair-endpoint-status'), 'CSC_REPAIR')
            write_json(out / 'endpoint-repair-status.json', status)
            require(status['ready'] == 1 and status['faults'] == 0, 'CE repair admission faulted')
        if args.saves:
            capture_census(controller, players, args.through, out / 'chain-census.txt')
            # Save the natural endpoint for follow-up diagnosis after the
            # census and Service observation are captured. A file timeout
            # should leave the read-only evidence available for inspection.
            state = controller.state_read('fresh-endpoint-save-check')
            if state['player0_alive']:
                checkpoint = save_inactive_boundary(controller, turn=args.through, name='CSC_BAKERS_FRESH',
                    native_directory=args.saves, archive=out / 'endpoint.Civ6Save')
                write_json(out / 'checkpoint.json', checkpoint)
            else:
                write_json(out / 'checkpoint-unavailable.json', state)
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
    summarize_run(out, players, start, args.through, args.untuned, checkpoint, args.census_turns,
                  qualification=args.qualification, observer_boundary=args.observe_supplier_at)


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
    parser.add_argument('--qualification', action='store_true',
                        help='Record a preselected fresh Standard run with strict Storekeeper turn coverage')
    parser.add_argument('--matched-source', type=Path, help='Require initial state parity with the other arm')
    parser.add_argument('--saves', type=Path, help='Native Saves/Single path for an endpoint census and archived save')
    parser.add_argument('--census-turns', type=int, nargs='+', default=[],
                        help='Read-only Bakers milestone snapshots during autoplay')
    parser.add_argument('--resume-from', type=Path, help='Continue a closed tuned development run for diagnosis')
    parser.add_argument('--observe-supplier-at', type=int,
                        help='Observe an exact Pasture target after a verified fresh-game boundary')
    target = parser.add_mutually_exclusive_group()
    target.add_argument('--supplier', type=int, nargs=4, metavar=('PLAYER', 'CITY', 'QUARTER', 'PLOT'))
    target.add_argument('--wind-mill', type=int, nargs=3, metavar=('PLAYER', 'CITY', 'QUARTER'))
    target.add_argument('--granary', type=int, nargs=3, metavar=('PLAYER', 'CITY', 'QUARTER'))
    target.add_argument('--dam-sites', type=int, nargs=4, metavar=('PLAYER', 'CITY', 'QUARTER', 'PLOT'),
                        help='Survey legal Dam sites and flood coverage around a sole working Base supplier')
    target.add_argument('--water-mill-repair', type=int, nargs=3, metavar=('PLAYER', 'CITY', 'QUARTER'),
                        help='Observe a pillaged Water Mill and Quarter with the other chain links working')
    parser.add_argument('--quarter-repair-selector', action='store_true',
                        help='Observe the existing Quarter at the district selector instead of the Mill comparison')
    parser.add_argument('--quarter-repair-offer', action='store_true',
                        help='Submit one unmodified native repair offer on the exact Alexandria replay')
    parser.add_argument('--mill-only-repair', action='store_true',
                        help='Observe a pillaged Water Mill after its host Quarter has been restored')
    parser.add_argument('--repair-ce-replay', action='store_true',
                        help='Verify packaged CE and CSC repair admission on the exact Alexandria replay')
    parser.add_argument('--probe-dependencies', type=Path, help='Existing exact Frida package directory')
    parser.add_argument('--alexandria-bid', action='store_true', help='Add a scoped +6144 Q8 in the matched replay only')
    parser.add_argument('--melbourne-mill-bid', action='store_true', help='Add 448 score units at the matched Wind Mill nomination')
    parser.add_argument('--trebizond-granary-bid', action='store_true', help='Add 288 score units once at the matched Granary nomination')
    parser.add_argument('--granary-components', action='store_true',
                        help='Read native modifier contributions in the short Trebizond baseline')
    parser.add_argument('--mill-opening-components', action='store_true',
                        help='Prepare the exact Melbourne two-link fixture and read its Wind Mill forecast')
    parser.add_argument('--melbourne-builder-offers', action='store_true',
                        help='Follow Australian city offers through turn 116 in the exact opening fixture')
    parser.add_argument('--melbourne-builder-recruitment', action='store_true',
                        help='Record existing Builder candidates for the exact Melbourne Rice job')
    parser.add_argument('--granary-ce-replay', action='store_true',
                        help='Verify the calibrated CSC Granary nomination with the exact CE package')
    parser.add_argument('--movement-only', action='store_true', help='Observe assigned Builder movement without native hooks')
    parser.add_argument('--calibration-replay', action='store_true', help='Verify the integrated bid on the exact Alexandria save')
    parser.add_argument('--mill-ce-replay', choices=('parity', 'tuned'),
                        help='Verify the CE hook with the old or integrated CSC publisher on the exact Melbourne save')
    parser.add_argument('--ce-sha256', required=True)
    options = parser.parse_args()
    options.census_turns = sorted(set(options.census_turns))
    if options.qualification:
        try:
            check_qualification(options)
        except ValueError as error:
            parser.error(str(error))
        if options.census_turns and options.census_turns != QUALIFICATION_CENSUSES:
            parser.error('Qualification uses the same four milestone censuses in every arm')
        options.census_turns = QUALIFICATION_CENSUSES
    if len(options.census_turns) > 8:
        parser.error('At most eight milestone census turns are supported')
    if options.quarter_repair_selector and not options.water_mill_repair:
        parser.error('The Quarter selector requires --water-mill-repair')
    if options.mill_only_repair and not (options.water_mill_repair and options.resume_from
                                          and not options.quarter_repair_selector):
        parser.error('The Mill-only observer requires a saved Water Mill repair continuation')
    if options.quarter_repair_offer and not (options.quarter_repair_selector and options.resume_from
                                               and options.probe_dependencies and not options.qualification):
        parser.error('The separate repair offer requires the matched selector continuation')
    if options.repair_ce_replay and not (options.water_mill_repair and options.resume_from and not (
            options.probe_dependencies or options.quarter_repair_selector
            or options.qualification)):
        parser.error('Packaged repair qualification requires the matched save and uses native CE telemetry')
    if options.melbourne_builder_offers and not options.mill_opening_components:
        parser.error('The Builder offer trace requires --mill-opening-components')
    if options.melbourne_builder_recruitment and not options.melbourne_builder_offers:
        parser.error('The recruitment trace requires --melbourne-builder-offers')
    if options.mill_opening_components and (
            not options.resume_from or not options.wind_mill or not options.probe_dependencies
            or options.observe_supplier_at is not None or options.melbourne_mill_bid or options.mill_ce_replay
            or options.calibration_replay or options.granary_ce_replay or options.movement_only
            or options.alexandria_bid or options.trebizond_granary_bid or options.granary_components):
        parser.error('Opening components require the exact Wind Mill continuation and a read-only probe')
    if options.observe_supplier_at is not None:
        if (not (options.saves and options.supplier and options.probe_dependencies)
                or options.resume_from or options.untuned or options.qualification or options.matched_source
                or options.alexandria_bid or options.melbourne_mill_bid or options.trebizond_granary_bid
                or options.granary_components or options.granary_ce_replay or options.movement_only
                or options.calibration_replay or options.mill_ce_replay
                or not 1 < options.observe_supplier_at < options.through <= options.observe_supplier_at + 15):
            parser.error('Fresh supplier observation needs an exact target, a read-only probe, --saves and a window of 1–15 turns')
    elif options.resume_from:
        if not (options.saves and (options.supplier or options.wind_mill or options.granary or options.dam_sites
                                  or options.water_mill_repair)
                and (options.probe_dependencies or options.movement_only or options.mill_ce_replay
                     or options.granary_ce_replay or options.dam_sites or options.repair_ce_replay)
                and not options.untuned and not options.matched_source):
            parser.error('A tuned continuation needs --saves, one target, and a diagnostic mode')
        if options.dam_sites and options.qualification:
            parser.error('A Dam site survey uses the shared controller and the existing CE package')
        if options.water_mill_repair and not (options.probe_dependencies or options.repair_ce_replay):
            parser.error('Water Mill repair observation requires --probe-dependencies')
        if options.alexandria_bid and not options.supplier:
            parser.error('The Alexandria bid requires --supplier')
        if options.melbourne_mill_bid and not options.wind_mill:
            parser.error('The Melbourne bid requires --wind-mill')
        if options.trebizond_granary_bid and not options.granary:
            parser.error('The Trebizond bid requires --granary')
        if options.granary_components and (not options.granary or options.trebizond_granary_bid):
            parser.error('Granary component capture requires a read-only --granary continuation')
        if options.granary_ce_replay and (not options.granary or options.trebizond_granary_bid
                                         or options.granary_components or options.probe_dependencies):
            parser.error('Integrated Granary qualification requires --granary and uses native CE telemetry')
        if options.movement_only and (not options.supplier or options.probe_dependencies or options.alexandria_bid):
            parser.error('Movement-only diagnosis requires --supplier and uses no native probe or bid')
        if options.calibration_replay and not options.movement_only:
            parser.error('Integrated calibration requires --movement-only')
        if options.mill_ce_replay and (not options.wind_mill or options.probe_dependencies or options.melbourne_mill_bid):
            parser.error('CE nomination qualification requires --wind-mill and uses no external probe or bid')
    elif (options.supplier or options.wind_mill or options.granary or options.dam_sites or options.water_mill_repair
          or options.probe_dependencies or options.alexandria_bid
          or options.melbourne_mill_bid or options.trebizond_granary_bid or options.granary_components or options.granary_ce_replay
          or options.movement_only or options.calibration_replay or options.mill_ce_replay):
        parser.error('Decision diagnostics require --resume-from')
    if not (3 <= options.through <= 250 and 0 < options.map_seed < 2**31 and 0 < options.game_seed < 2**31):
        parser.error('Use positive 31-bit seeds and an endpoint between turns 3 and 250')
    if not 30 <= options.interval_minutes <= 240:
        parser.error('Use a continuous window limit between 30 and 240 minutes')
    run(options)
