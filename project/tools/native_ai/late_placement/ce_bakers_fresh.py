"""Start an ordinary Bakers development game with separate local CSC and CE packages."""

import argparse
from pathlib import Path
import shutil
import traceback
import uuid
import xml.etree.ElementTree as ET

from ce_replay import DLL, HOTFIX_EXE_SHA, verify_modules
from driver import (
    HERE, HOTFIX_SHA, HeldProcess, NativeSession, configure, flags, launch,
    make_probe_controller, manifest, native_inventory, parse, read, require,
    restore_preferences, sha, write_json,
)
from storekeeper_runtime import audit


LOGS = ('Lua.log', 'Database.log', 'Modding.log', 'AI_CityBuild.csv',
        'AI_Behavior_Trees.csv', 'City_BuildQueue.csv', 'UnitOperations.log')


def host(map_seed, game_seed):
    return f"""
GameConfiguration.SetToDefaults()
GameConfiguration.SetRuleSet('RULESET_EXPANSION_2')
BuildHeadlessGameSetup()
RebuildPlayerParameters(true)
GameSetup_RefreshParameters()
MapConfiguration.SetScript('Continents.lua')
MapConfiguration.SetMapSize('MAPSIZE_SMALL')
GameConfiguration.SetParticipatingPlayerCount(6)
GameConfiguration.SetValue('CITY_STATE_COUNT',9)
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
    out.mkdir(parents=True)
    write_json(out / 'packages.json', {str(source): dict(install=str(local[source]), files=files)
                                       for source, files in pins.items()})
    write_json(out / 'protocol.json', dict(map='Continents', map_seed=args.map_seed, game_seed=args.game_seed,
        endpoint=args.through, csc=csc_id, ce=ce_id, development=True, ordinary_setup=True,
        fresh_game=True, qualification=False, external_policy=False, gameplay_interventions=False))
    controller = make_probe_controller(out, user_root=args.user_root)
    controller.study_endpoint = args.through
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    players = set()
    copied = []

    def verify_packages():
        for source in copied:
            require(manifest(local[source]) == pins[source], f'Installed development package changed: {source}')

    def source_gate():
        raw = controller.cmd("""
assert(Game.GetCurrentGameTurn()==1 and Players[0]:IsHuman())
assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER)
local ids={}
for _,p in ipairs(PlayerManager.GetAliveMajors()) do
    local id=p:GetID()
    assert(Game:GetProperty('CSC_AI_OriginalHuman_'..id)==(p:IsHuman() and 1 or 0))
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
        require(len(players) == 5 and 0 not in players and status['ready'] == 1 and not status['faults'],
                'Original AI roster or integrated CE capability did not initialize')
        write_json(out / 'source.json', dict(original_ai=sorted(players), native=status))
        return True

    try:
        for source, destination in local.items():
            shutil.copytree(source, destination)
            copied.append(source)
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
        session.issue_once('host-normal-start', host(args.map_seed, args.game_seed), 'MainMenu')
        session.ready_after_issue(1, ('GameCore_Tuner', 'PlotInfo', 'CSC_AI_BakersGameplay'), eligibility=source_gate)
        verify_modules(session, local[ce] / ce_dll, out, HOTFIX_SHA)
        raw = controller.cmd('CSC_BAKERS_STOREKEEPER_WATCH=true\n' + read(HERE / 'storekeeper_runtime.lua'),
                             'PlotInfo', 'install-storekeeper-watch')
        require('CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED' in raw, 'Storekeeper watch was not installed')
        controller.play(args.through)
        final = parse(controller.cmd('print("CSC_FRESH_CE="..CE_AIDistrictScoresStatus())',
                                     'GameCore_Tuner', 'fresh-endpoint-status'), 'CSC_FRESH_CE')
        write_json(out / 'native-endpoint.json', final)
        require(final['ready'] == 1 and final['faults'] == 0, 'CE district scoring failed during autoplay')
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
    require('CSC_AI_BAKERS_DISTRICTS_FAILED' not in log and 'CSC_AI_BAKERS_DISTRICTS turn=' in log,
            'Integrated CSC publication missing or faulted')
    result = audit(log, players, expected_turns=range(2, args.through))
    write_json(out / 'result.json', dict(closed=session.closed, reached=args.through, storekeeper=result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'mods', 'user-root', 'binary', 'ce', 'csc'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('map-seed', 'game-seed', 'through'):
        parser.add_argument('--' + name, type=int, required=True)
    parser.add_argument('--ce-sha256', required=True)
    options = parser.parse_args()
    if not (3 <= options.through <= 250 and 0 < options.map_seed < 2**31 and 0 < options.game_seed < 2**31):
        parser.error('Use positive 31-bit seeds and an endpoint between turns 3 and 250')
    run(options)
