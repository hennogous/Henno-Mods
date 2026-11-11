"""Replay the pinned Nicopolis weak-site case through the shared controller.

This is a diagnostic fixture, outside CSC's shipped policy. It observes the
ordinary district selector and plot state. The frontier mode adds exactly one
early score entry to test CE admission before generalizing frontier coverage.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import traceback
import time
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
    if turn<200 or turn>__ENDPOINT__ then return end
    for _,index in ipairs({398,472,401}) do
        local plot=assert(Map.GetPlotByIndex(index))
        local buyer=Cities.GetPlotPurchaseCity(plot)
        local supply=placement.ReadSuppliers(player,plot,profile)
        print('CSC_NICOPOLIS_SNAPSHOT',turn,index,plot:GetOwner(),buyer and buyer:GetID() or -1,
            plot:GetDistrictType(),#supply.base,#supply.specialty,
            plot:CanHaveDistrict(profile.district.Index,1,524295))
        for _,neighbor in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY())) do
            local resource=GameInfo.Resources[neighbor:GetResourceType()]
            local revealed=PlayersVisibility[1]:IsRevealed(neighbor:GetX(),neighbor:GetY())
            local visible=resource and revealed and CSC_Adjacency.ResourceVisible(1,resource.Index)
            local district=GameInfo.Districts[neighbor:GetDistrictType()]
            print('CSC_NICOPOLIS_SITE_NEIGHBOR',turn,index,neighbor:GetIndex(),neighbor:GetOwner(),revealed,
                visible and resource.ResourceType or '-',neighbor:GetImprovementType(),
                district and district.DistrictType or '-',
                visible and CSC_Adjacency.HasTag(profile.base,resource.ResourceType) or false,
                visible and CSC_Adjacency.HasTag(profile.specialty,resource.ResourceType) or false,
                profile.customers[neighbor:GetDistrictType()]~=nil,
                district and CSC_Adjacency.HasTag('CLASS_CSC_BAKERS_SALES',district.DistrictType) or false)
        end
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
    assert 201 <= args.through <= 224, 'This fixture uses a bounded continuation of the turn-200 save'
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
    replacements = {}
    if args.mode != 'original':
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
    # Recovery must match the exact staged production files, not the older
    # frozen carrier before those substitutions. No arbitrary package reuse.
    for source, destination in packages.items():
        if recovery:
            assert destination.is_dir() and manifest(destination) == pins[source]
            assert load(recovery / 'inputs.json')['packages'][source.name] == pins[source]
        else:
            assert not destination.exists()
    sys.path.insert(0, str(args.dependencies.resolve(strict=True)))
    import frida
    assert frida.__version__ == '17.24.3'
    assert Path(frida.__file__).resolve().is_relative_to(args.dependencies.resolve())
    out.mkdir(parents=True)
    write_json(out / 'inputs.json', dict(mode=args.mode, through=args.through, save_sha256=SAVE_SHA,
        ce_sha256=CE_SHA, packages={source.name: value for source, value in pins.items()}))
    shutil.copyfile(Path(__file__), out / Path(__file__).name)
    (out / 'plot-watcher.lua').write_text(WATCHER.replace('__ENDPOINT__', str(args.through)), encoding='utf-8')
    if recovery:
        shutil.copyfile(recovery / 'original-preferences.json', out / 'original-preferences.json')
    controller = make_probe_controller(out, user_root=user_root)
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    installed = []
    observer = purchase_observer = attachment = None
    restore_allowed = False
    stream_errors = []

    def verify_packages():
        assert all(manifest(packages[source]) == pins[source] for source in installed)

    def stream_receipts(name):
        # Frida delivers bounded callback messages on its host thread. Each
        # append is flushed to disk before returning. A surviving journal is
        # explicitly partial evidence; only endpoint and closure receipts can
        # establish a completed replay. No console command is issued here.
        def receive(message, data):
            try:
                with (out / (name + '-live.ndjson')).open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(dict(partial=True, captured_unix=time.time(), message=message)) + '\n')
                    stream.flush()
                    os.fsync(stream.fileno())
            except Exception as error:
                stream_errors.append(dict(observer=name, error=str(error), captured_unix=time.time()))
                # A full disk can also prevent this error receipt. Retain the
                # in-memory error so the replay cannot report complete below.
                try:
                    write_json(out / 'receipt-stream-errors.json', stream_errors)
                except OSError:
                    pass
        return receive

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
            plots=sorted(plots), cePath=modules[DLL]['path'], streamRecords=True)
        write_json(out / 'scope.json', scope)
        sources = (STUDY / 'observer.js', HERE / 'dam_site_observer.js')
        for path in sources:
            shutil.copyfile(path, out / path.name)
        code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n"
        code += '\n'.join(read(out / path.name) for path in sources)
        attachment = frida.attach(session.owner.pid)
        observer = attachment.create_script(code)
        observer.on('message', stream_receipts('selector'))
        observer.load()
        assert observer.exports_sync.init(dict(path=modules['GameCore_XP2_FinalRelease.dll']['path'],
            image_size=XP2_IMAGE_SIZE), scope)
        observer.exports_sync.advance()
        if args.observe_purchases:
            # Separate read-only script with its own RPC state. Its hooks sit
            # in Economic::TryPurchasePlot and Purchase::Start and do not
            # alter CE's district callers or the game's purchase decisions.
            purchase_sources = (STUDY / 'observer.js', HERE / 'plot_purchase_observer.js')
            shutil.copyfile(purchase_sources[1], out / purchase_sources[1].name)
            purchase_code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n"
            purchase_code += '\n'.join(read(path) for path in purchase_sources)
            purchase_observer = attachment.create_script(purchase_code)
            purchase_observer.on('message', stream_receipts('purchase'))
            purchase_observer.load()
            # Other paid plots for this player serve as a natural positive
            # control for the command callbacks. Targeted savings observations
            # remain restricted to the two diagnostic footprints.
            purchase_scope = dict(player=1, width=74, height=46, plots=[398,401],
                allCommandPlots=True, streamRecords=True)
            write_json(out / 'purchase-scope.json', purchase_scope)
            assert purchase_observer.exports_sync.init(
                dict(path=modules['GameCore_XP2_FinalRelease.dll']['path'], image_size=XP2_IMAGE_SIZE),
                purchase_scope)
        controller.study_endpoint = args.through
        print('Nicopolis diagnostic armed', args.mode, flush=True)
        controller.play(args.through)
        trace = observer.exports_sync.freeze()
        write_json(out / 'selector-trace.json', trace)
        assert trace['fault'] is None and trace['active'] == 0
        if purchase_observer:
            purchase_trace = purchase_observer.exports_sync.freeze()
            write_json(out / 'purchase-trace.json', purchase_trace)
            assert purchase_trace['fault'] is None
            purchase_observer.unload()
            purchase_observer = None
        observer.unload()
        observer = None
        attachment.detach()
        attachment = None
        state = controller.state_read('replay-end')
        assert state['turn'] == args.through and not state['active']
        raw = controller.cmd('CSC_NICOPOLIS_Snapshot()', 'CSC_AI_BakersGameplay', 'endpoint-readback')
        (out / 'endpoint-plots.txt').write_text(raw, encoding='utf-8')
        for name in LOGS:
            shutil.copyfile(user_root / 'Logs' / name, out / name)
    except Exception as error:
        write_json(out / 'failure.json', dict(error=str(error), traceback=traceback.format_exc()))
        raise
    finally:
        # A timeout must retain whatever the native callbacks already saw.
        # Cleanup faults must also leave the shared controller an opportunity
        # to restore preferences and release its exclusively owned process.
        cleanup_errors = []
        for name, script in (('purchase', purchase_observer), ('selector', observer)):
            if script:
                try:
                    write_json(out / (name + '-partial-trace.json'), script.exports_sync.freeze())
                except Exception as error:
                    cleanup_errors.append(dict(operation=name + '-freeze', error=str(error)))
                try:
                    script.unload()
                except Exception as error:
                    cleanup_errors.append(dict(operation=name + '-unload', error=str(error)))
        if attachment:
            try:
                attachment.detach()
            except Exception as error:
                cleanup_errors.append(dict(operation='detach', error=str(error)))
        if cleanup_errors:
            write_json(out / 'observer-cleanup-errors.json', cleanup_errors)
        if session.owner is not None and session.owner.poll() is None:
            # configure saves preferences before its first mutation. Recover
            # that snapshot even when later configuration checks fail.
            restore_allowed = restore_allowed or not recovery and (out / 'original-preferences.json').exists()
            session.close(restore_preferences=lambda: restore_preferences(controller, out) if restore_allowed else None,
                restore_package=verify_packages)
        if session.closed and restore_allowed:
            for source in installed:
                packages[source].rename(out / source.name)
        if cleanup_errors and sys.exc_info()[0] is None:
            raise RuntimeError('Observer cleanup failed; see observer-cleanup-errors.json')
    assert session.closed, 'Endpoint captured without verified shared-session closure'
    assert not stream_errors, 'Native receipt stream failed; partial evidence only'
    write_json(out / 'complete.json', dict(verified=True, turns_advanced=args.through-200))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('original', 'frontier', 'integrated'), required=True)
    for name in ('output', 'reference', 'checkpoint', 'my-games', 'user-root', 'dependencies'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--recover-from', type=Path)
    parser.add_argument('--original-run', type=Path)
    parser.add_argument('--policy-root', type=Path)
    parser.add_argument('--through', type=int, default=208)
    parser.add_argument('--observe-purchases', action='store_true')
    options = parser.parse_args()
    if options.mode != 'original' and not options.original_run:
        parser.error('non-original modes require --original-run')
    if options.mode == 'integrated' and not options.policy_root:
        parser.error('integrated requires --policy-root')
    run(options)
