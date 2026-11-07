"""Start an ordinary Bakers development game with separate local CSC and CE packages."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import traceback
import uuid
import xml.etree.ElementTree as ET

from ce_replay import DLL, HOTFIX_EXE_SHA, verify_modules
from driver import (
    HERE, HOTFIX_SHA, HeldProcess, NativeSession, configure, flags, launch, load,
    make_probe_controller, manifest, native_inventory, parse, read, require,
    restore_preferences, sha, write_json,
)
from storekeeper_runtime import audit


LOGS = ('Lua.log', 'Database.log', 'Modding.log', 'AI_CityBuild.csv',
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
        session.issue_once('host-normal-start', host(args.map_seed, args.game_seed, args.map, args.map_size), 'MainMenu')
        contexts = ('GameCore_Tuner', 'PlotInfo')
        if not args.untuned:
            contexts += ('CSC_AI_BakersGameplay',)
        session.ready_after_issue(1, contexts, eligibility=source_gate)
        verify_modules(session, local[ce] / ce_dll, out, HOTFIX_SHA)
        raw = controller.cmd('CSC_BAKERS_STOREKEEPER_WATCH=true\n' + read(HERE / 'storekeeper_runtime.lua'),
                             'PlotInfo', 'install-storekeeper-watch')
        require('CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED' in raw, 'Storekeeper watch was not installed')
        controller.play(args.through)
        final = parse(controller.cmd('print("CSC_FRESH_CE="..CE_AIDistrictScoresStatus())',
                                     'GameCore_Tuner', 'fresh-endpoint-status'), 'CSC_FRESH_CE')
        write_json(out / 'native-endpoint.json', final)
        check_native_status(final, args.untuned)
    except Exception as error:
        write_json(out / 'failure.json', dict(error=str(error), traceback=traceback.format_exc()))
        raise
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, out)
                          if (out / 'original-preferences.json').exists() else None,
                          restore_package=verify_packages)
        if session.closed or (session.owner is None and not native_inventory()):
            for source in copied:
                local[source].rename(out / local[source].name)
            for name in LOGS:
                log = args.user_root / 'Logs' / name
                if session.closed and log.is_file():
                    shutil.copyfile(log, out / name)
    log = read(out / 'Lua.log')
    published = 'CSC_AI_BAKERS_DISTRICTS turn=' in log
    require('CSC_AI_BAKERS_DISTRICTS_FAILED' not in log and published != args.untuned,
            'Unexpected CSC policy publication in the development arm')
    require('CSC_AI_BAKERS_PLACEMENT_FAILED' not in log, 'CSC placement scan faulted during the run')
    placement_bids = {int(turn): int(count) for turn, count in
                      re.findall(r'CSC_AI_BAKERS_PLACEMENT turn=(\d+) bids=(\d+)', log)}
    score_samples = [dict(turn=int(turn), previous_version=int(version), rows=json.loads(samples))
                     for turn, version, samples in re.findall(
                         r'CSC_AI_BAKERS_DISTRICT_SAMPLES turn=(\d+) previousVersion=(\d+) samples=(\[[^\r\n]+\])', log)]
    result = audit(log, players, expected_turns=range(2, args.through))
    write_json(out / 'result.json', dict(closed=session.closed, reached=args.through,
                                       placement_bids=placement_bids, district_score_samples=score_samples,
                                       storekeeper=result))


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
    parser.add_argument('--ce-sha256', required=True)
    options = parser.parse_args()
    if not (3 <= options.through <= 250 and 0 < options.map_seed < 2**31 and 0 < options.game_seed < 2**31):
        parser.error('Use positive 31-bit seeds and an endpoint between turns 3 and 250')
    if not 30 <= options.interval_minutes <= 240:
        parser.error('Use a continuous window limit between 30 and 240 minutes')
    run(options)
