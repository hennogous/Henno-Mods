"""Replay the pinned Nicopolis weak-site case through the shared controller.

This is a diagnostic fixture, outside CSC's shipped policy. It observes the
ordinary district selector and plot state. The frontier mode adds exactly one
early score entry to test CE admission before generalizing frontier coverage.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import traceback
from types import SimpleNamespace

from ce_bakers_fresh import package_identity
from ce_replay import DLL, HOTFIX_EXE_SHA, verify_modules
from driver import (
    HERE, STUDY, HOTFIX_SHA, XP2_IMAGE_SIZE, HeldProcess, NativeSession, configure,
    flags, launch, load, make_probe_controller, manifest, native_inventory, parse, read,
    restore_preferences, sha, write_json,
)

CE_SHA = 'f8121151c787e4dcd4fea876eaaef5d6d1bb2b54561bc94d9d7da6385f21aa07'
SAVE_SHA = 'e333251ec7318fb6b170678a956c28e02e2f9b01c4c4753c99e84b1a112fe19a'
PACKAGES = ('CSC Bakers Development CE', 'CSC Bakers Development Mod')
SCANNER = Path('Lua_UI/AI/CSC_AI_AdjacencyScan.lua')
LOGS = ('Lua.log', 'AI_CityBuild.csv', 'AI_Behavior_Trees.csv', 'City_BuildQueue.csv')

# The source property reads are diagnostic only. Unowned neighboring deposits
# are logged separately because ReadSuppliers intentionally counts owned supply.
WATCHER = """
local placement=assert(CSC_AI_QuarterPlacement)
local profile=placement.StageTwoProfiles()[1]
local player=Players[1]
assert(profile.key=='BAKERS')
function CSC_NICOPOLIS_Snapshot()
    local turn=Game.GetCurrentGameTurn()
    if turn<200 or turn>208 then return end
    for _,index in ipairs({398,472}) do
        local plot=assert(Map.GetPlotByIndex(index))
        local buyer=Cities.GetPlotPurchaseCity(plot)
        local supply=placement.ReadSuppliers(player,plot,profile)
        print('CSC_NICOPOLIS_SNAPSHOT',turn,index,plot:GetOwner(),buyer and buyer:GetID() or -1,
            plot:GetDistrictType(),#supply.base,#supply.specialty,
            plot:CanHaveDistrict(profile.district.Index,1,524295))
    end
    local candidate=Map.GetPlotByIndex(398)
    for _,plot in ipairs(Map.GetAdjacentPlots(candidate:GetX(),candidate:GetY())) do
        local resource=GameInfo.Resources[plot:GetResourceType()]
        local revealed=PlayersVisibility[1]:IsRevealed(plot:GetX(),plot:GetY())
        local visible=resource and revealed and CSC_Adjacency.ResourceVisible(1,resource.Index)
        print('CSC_NICOPOLIS_NEIGHBOR',turn,plot:GetIndex(),plot:GetOwner(),revealed,
            visible and resource.ResourceType or '-',plot:GetDistrictType())
        if visible then
            print('CSC_NICOPOLIS_ADJACENT_RESOURCE',turn,plot:GetIndex(),plot:GetOwner(),
                resource.ResourceType,CSC_Adjacency.HasTag(profile.base,resource.ResourceType))
        end
    end
end
CSC_NICOPOLIS_Snapshot()
GameEvents.OnGameTurnStarted.Add(CSC_NICOPOLIS_Snapshot)
"""

FRONTIER_PROBE = b"""    -- Diagnostic fixture only. Plot 398 was admitted by the stock
    -- selector while unowned. Test one early entry without creating a
    -- purchase request or changing the native treasury/legality checks.
    if pid == 1 and district.Index == 36 then
        local site = Map.GetPlotByIndex(398)
        if site and site:GetOwner() == -1 and visibility:IsRevealed(site:GetX(), site:GetY())
            and #readSuppliers(player, site, profile).base == 0 then
            bids[#bids + 1] = {player=pid, city=524295, district=36, plot=398,
                delta=-noBasePenaltyQ8, weak=true}
        end
    end
"""


def entry_keys(profile):
    return {(row['id'], row['subscription'], row['file']) for row in profile['entries']}


def run(args):
    out = args.output.resolve()
    home, user_root = args.my_games.resolve(), args.user_root.resolve()
    reference = args.reference.resolve(strict=True)
    checkpoint = args.checkpoint.resolve(strict=True)
    assert not out.exists() and not native_inventory(), 'Fresh output and exclusive native session required'
    assert load(reference / 'complete.json')['verified']
    assert load(reference / 'session-closed.json')['verified']
    meta = load(checkpoint / 'checkpoint.json')
    save = Path(meta['native_save']).resolve(strict=True)
    assert meta['verified'] and meta['turn'] == 200 and meta['sha256'] == SAVE_SHA
    assert save.parent == (home / 'Saves/Single').resolve()
    assert sha(save) == sha(checkpoint / 'endpoint.Civ6Save') == SAVE_SHA
    packages = {reference / name: home / 'Mods' / name for name in PACKAGES}
    original_pins = {source: manifest(source) for source in packages}
    pins = {source: dict(value) for source, value in original_pins.items()}
    ce, csc = packages
    ce_id, _ = package_identity(ce)
    csc_id, _ = package_identity(csc)
    test_ids = {ce_id, csc_id}
    ce_relative = Path('Binaries/Win64') / DLL
    assert sha(ce / ce_relative) == CE_SHA
    binary = Path(load(reference / 'launch-bootstrap.json')['binary'])
    assert sha(binary) == HOTFIX_EXE_SHA
    recovery = args.recover_from.resolve(strict=True) if args.recover_from else None
    for source, destination in packages.items():
        if recovery:
            assert destination.is_dir() and manifest(destination) == pins[source]
        else:
            assert not destination.exists()
    replacements = {}
    if args.mode != 'original':
        assert not recovery, 'Complete preference recovery before a frontier test'
        original_run = args.original_run.resolve(strict=True)
        assert load(original_run / 'complete.json')['verified']
        trace = load(original_run / 'selector-trace.json')
        selected, = (row for row in trace['records'] if row['kind'] == 'selection' and row['turn'] == 203)
        assert selected['winner'] == dict(district=36, x=28, y=5, q8=396462)
        frontier, = (row for row in selected['sites'] if row['plot'] == 398)
        assert frontier['owned'] == 0 and frontier['frontier'] == 1 and frontier['reservation'] == -1
    if args.mode == 'frontier':
        before = (csc / SCANNER).read_bytes()
        newline = b'\r\n' if b'\r\n' in before else b'\n'
        needle = b'    return bids, counts' + newline + b'end'
        assert before.count(needle) == 1
        modified = before.replace(needle, FRONTIER_PROBE.replace(b'\n', newline) + needle)
        replacements[SCANNER] = modified
    elif args.mode == 'integrated':
        # Stage only the two production AI files being qualified. Unrelated
        # worktree gameplay, art and content cannot enter this saved fixture.
        for relative in (SCANNER, Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua')):
            replacements[relative] = (args.policy_root / relative).read_bytes()
    for relative, data in replacements.items():
        pins[csc][str(relative)] = dict(sha256=hashlib.sha256(data).hexdigest(), size=len(data))
    sys.path.insert(0, str(args.dependencies.resolve(strict=True)))
    import frida
    assert frida.__version__ == '17.24.3'
    assert Path(frida.__file__).resolve().is_relative_to(args.dependencies.resolve())
    out.mkdir(parents=True)
    write_json(out / 'inputs.json', dict(mode=args.mode, save_sha256=SAVE_SHA,
        ce_sha256=CE_SHA, packages={source.name: value for source, value in pins.items()}))
    shutil.copyfile(Path(__file__), out / Path(__file__).name)
    (out / 'plot-watcher.lua').write_text(WATCHER, encoding='utf-8')
    if recovery:
        shutil.copyfile(recovery / 'original-preferences.json', out / 'original-preferences.json')
    controller = make_probe_controller(out, user_root=user_root)
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    installed = []
    observer = attachment = None
    restore_allowed = False

    def verify_packages():
        assert all(manifest(packages[source]) == pins[source] for source in installed)

    try:
        for source, destination in packages.items():
            if not recovery:
                shutil.copytree(source, destination)
            installed.append(source)
        for relative, data in replacements.items():
            (packages[csc] / relative).write_bytes(data)
            (out / relative.name).write_bytes(data)
        verify_packages()
        session.start(lambda: launch(SimpleNamespace(binary=binary), out))
        session.wait_context('MainMenu')
        if recovery:
            original = load(out / 'original-preferences.json')
            actual = flags(controller, 'inspect-interrupted-menu')
            assert entry_keys(actual) == entry_keys(original), 'Inventory changed since interrupted run'
            assert actual == original or {key for key, value in actual['mods'].items() if value} == test_ids
            restore_allowed = True
            configure(controller, out / 'recovered-setup', csc_id=ce_id)
        else:
            configure(controller, out, csc_id=ce_id)
            restore_allowed = True
        session.issue_once('enable-csc', f"""
local chosen
for _, m in ipairs(Modding.GetInstalledMods()) do
    if m.Id=='{csc_id}' then assert(not chosen); chosen=m end
end
assert(chosen and Modding.CanEnableMod(chosen.Handle)=='OK')
Modding.EnableMod(chosen.Handle,true)
""", 'MainMenu')
        assert {key for key, value in flags(controller, 'verify-local-pair')['mods'].items() if value} == test_ids
        session.issue_load_once(save, sha256=SAVE_SHA, native_directory=home / 'Saves/Single', turn=200)

        plots = []

        def ready():
            verify_modules(session, (packages[ce] / ce_relative).resolve(), out, HOTFIX_SHA)
            controller.cmd(read(out / 'plot-watcher.lua'), 'CSC_AI_BakersGameplay', 'watch-source-plots')
            raw = controller.cmd("""
local city=assert(CityManager.GetCity(1,524295))
local center=assert(Map.GetPlot(city:GetX(),city:GetY()))
local indices={}
for _,plot in ipairs(CSC_Adjacency.PlotsInBand(center,1,3)) do
    indices[#indices+1]=plot:GetIndex()
end
print('CSC_REPLAY_PLOTS=['..table.concat(indices,',')..']')
""", 'CSC_AI_BakersGameplay', 'scope-radius-three-plots')
            plots.extend(parse(raw, 'CSC_REPLAY_PLOTS'))
            assert len(plots) == len(set(plots)) and 398 in plots and 472 in plots and len(plots) <= 36
            return True

        session.ready_after_issue(200, ('GameCore_Tuner', 'PlotInfo', 'CSC_AI_BakersGameplay'), eligibility=ready)
        modules = load(out / 'loaded-modules.json')
        scope = dict(player=1, city=524295, width=74, height=46, districtCount=38, district=36,
            plots=sorted(plots), cePath=modules[DLL]['path'])
        write_json(out / 'scope.json', scope)
        sources = (STUDY / 'observer.js', HERE / 'dam_site_observer.js')
        for path in sources:
            shutil.copyfile(path, out / path.name)
        code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n"
        code += '\n'.join(read(out / path.name) for path in sources)
        attachment = frida.attach(session.owner.pid)
        observer = attachment.create_script(code)
        observer.load()
        assert observer.exports_sync.init(dict(path=modules['GameCore_XP2_FinalRelease.dll']['path'],
            image_size=XP2_IMAGE_SIZE), scope)
        observer.exports_sync.advance()
        controller.study_endpoint = 208
        print('Nicopolis diagnostic armed', args.mode, flush=True)
        controller.play(208)
        trace = observer.exports_sync.freeze()
        write_json(out / 'selector-trace.json', trace)
        assert trace['fault'] is None and trace['active'] == 0
        observer.unload()
        observer = None
        attachment.detach()
        attachment = None
        state = controller.state_read('replay-end')
        assert state['turn'] == 208 and not state['active']
        raw = controller.cmd('CSC_NICOPOLIS_Snapshot()', 'CSC_AI_BakersGameplay', 'endpoint-readback')
        (out / 'endpoint-plots.txt').write_text(raw, encoding='utf-8')
        for name in LOGS:
            shutil.copyfile(user_root / 'Logs' / name, out / name)
    except Exception as error:
        write_json(out / 'failure.json', dict(error=str(error), traceback=traceback.format_exc()))
        raise
    finally:
        if observer:
            observer.unload()
        if attachment:
            attachment.detach()
        if session.owner is not None and session.owner.poll() is None:
            # configure saves preferences before its first mutation. Recover
            # that snapshot even when later configuration checks fail.
            restore_allowed = restore_allowed or not recovery and (out / 'original-preferences.json').exists()
            session.close(restore_preferences=lambda: restore_preferences(controller, out) if restore_allowed else None,
                restore_package=verify_packages)
        if session.closed and restore_allowed:
            for source in installed:
                packages[source].rename(out / source.name)
    write_json(out / 'complete.json', dict(verified=True, turns_advanced=8))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('original', 'frontier', 'integrated'), required=True)
    for name in ('output', 'reference', 'checkpoint', 'my-games', 'user-root', 'dependencies'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--recover-from', type=Path)
    parser.add_argument('--original-run', type=Path)
    parser.add_argument('--policy-root', type=Path)
    options = parser.parse_args()
    if options.mode != 'original' and not options.original_run:
        parser.error('non-original modes require --original-run')
    if options.mode == 'integrated' and not options.policy_root:
        parser.error('integrated requires --policy-root')
    run(options)
