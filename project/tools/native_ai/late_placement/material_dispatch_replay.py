"""Compare worker dispatch on the two retained Fractal checkpoints.

The shared controller owns the process, save and active packages. Diagnostic
arms can adjust native decisions at a verified supplier. The packaged comparison
uses the same current CSC Lua in both arms and changes only the CE DLL.
"""
import argparse
import csv
import json
from pathlib import Path
import re
import shutil
import sys
from types import SimpleNamespace

from audit_xp2_hotfix import XP2_IMAGE_SIZE
from ce_bakers_fresh import LOGS
from ce_replay import DLL, native_profile, verify_modules
from driver import (ROOT, HeldProcess, NativeSession, configure, flags, launch, load, lua, make_probe_controller,
                    manifest, native_inventory, parse, read, require, restore_preferences, sha, write_json)
from material_development_replay import observe_workers, worker_handoffs
from material_development_summary import COMMITTED_BUYER, OFFER, RECEIPT, trace_work_trees
from material_scheduler_campaign import FINISH_OFF, FINISH_ON, qualify_packages
from planning_continue import HERE, compare_structure, digest as package_digest, enable, parse_census, prepare
from full_game_controller.checkpoint import save_inactive_boundary


FIXTURES = {
    'kish': dict(start=150, end=175, city=131073, quarter=2114,
                 resource='RESOURCE_CSC_FLAX', plots=[2188], pillaged=True, buyer_working=True),
    'umma': dict(start=200, end=215, city=393221, quarter=1974,
                 resource='RESOURCE_WHEAT', plots=[1975, 2047], pillaged=False, buyer_working=False),
    'quebec': dict(start=150, end=166, player=3, city=131073, quarter=696,
                   resource='RESOURCE_BERRIES', plots=[622], specialty='BUILDING_CSC_BAKERS_CAFE'),
}

# The actual turn-241 autosave retained AI ownership of the observer seat.
# Reproduce the observed damage on the same map's verified manual checkpoint.
# Both arms receive the same damage once. Every subsequent decision is native.
UMMA_DAMAGE = '''
assert(Game.GetCurrentGameTurn()==200 and not AutoplayManager.IsActive() and Players[0]:IsHuman())
local player=assert(Players[5])
local city=assert(player:GetCities():FindID(393221))
local site=assert(Map.GetPlotByIndex(1974))
local district=assert(city:GetDistricts():GetDistrictAtLocation(site:GetX(),site:GetY()))
assert(district:IsComplete() and not district:IsPillaged()
    and district:GetType()==GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index)
local buildings=city:GetBuildings()
local mill=GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL.Index
assert(buildings:HasBuilding(mill) and buildings:GetBuildingLocation(mill)==1974 and not buildings:IsPillaged(mill))
local wheat=GameInfo.Resources.RESOURCE_WHEAT.Index
local farm=GameInfo.Improvements.IMPROVEMENT_FARM.Index
local first,second=assert(Map.GetPlotByIndex(1975)),assert(Map.GetPlotByIndex(2047))
for _,plot in ipairs({first,second})do
    assert(plot:GetOwner()==5 and plot:GetResourceType()==wheat and plot:GetDistrictType()==-1)
end
assert(first:GetImprovementType()==farm and not first:IsImprovementPillaged() and second:GetImprovementType()==-1)
ImprovementBuilder.SetImprovementType(first,-1,5)
district:SetPillaged(true)
if not buildings:IsPillaged(mill) then buildings:SetPillaged(mill,true) end
'''


def snapshot(controller, fixture, label):
    code = f'local case={lua(fixture)}\n' + '''
local player=assert(Players[5])
assert(not player:IsHuman())
local city=assert(player:GetCities():FindID(case.city))
local quarter=assert(Map.GetPlotByIndex(case.quarter))
local district=assert(city:GetDistricts():GetDistrictAtLocation(quarter:GetX(),quarter:GetY()))
assert(district:IsComplete() and district:GetType()==GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index)
local buildings=city:GetBuildings()
local mill, millPillaged=false,false
for _,name in ipairs({'BUILDING_CSC_BAKERS_WATER_MILL','BUILDING_CSC_BAKERS_WIND_MILL'})do
    local i=GameInfo.Buildings[name].Index
    if buildings:HasBuilding(i) and buildings:GetBuildingLocation(i)==case.quarter then
        mill, millPillaged=true,buildings:IsPillaged(i)
    end
end
local farm=GameInfo.Improvements.IMPROVEMENT_FARM.Index
local builder=GameInfo.Units.UNIT_BUILDER.Index
local resource=GameInfo.Resources[case.resource].Index
local sites={}
for _,index in ipairs(case.plots)do
    local plot=assert(Map.GetPlotByIndex(index))
    local x,y=plot:GetX(),plot:GetY()
    assert(Map.GetPlotDistance(x,y,quarter:GetX(),quarter:GetY())==1)
    local valid=plot:GetOwner()==5 and plot:GetResourceType()==resource and plot:GetDistrictType()==-1
    local pillaged=plot:IsImprovementPillaged()
    local improvement=plot:GetImprovementType()
    local working=valid and improvement==farm and not pillaged
    sites[#sites+1]=string.format('{"plot":%d,"x":%d,"y":%d,"valid":%s,"working":%s,"pillaged":%s,"improvement":%d}',
        index,x,y,tostring(valid),tostring(working),tostring(pillaged),improvement)
end
local quarterPillaged=district:IsPillaged()
local works=mill and not millPillaged and not quarterPillaged
print(string.format('CSC_DISPATCH={"turn":%d,"farm":%d,"builder":%d,"buyerWorking":%s,"quarterPillaged":%s,"millPillaged":%s,"plots":[%s]}',
    Game.GetCurrentGameTurn(),farm,builder,tostring(works),tostring(quarterPillaged),tostring(millPillaged),table.concat(sites,',')))
print('CSC_DISPATCH_REPAIR='..CE_AIDistrictRepairStatus())
'''
    raw = controller.cmd(code, 'CSC_AI_BakersGameplay', label)
    return {**parse(raw, 'CSC_DISPATCH'), 'nativeRepair': parse(raw, 'CSC_DISPATCH_REPAIR')}


def case_jobs(out, fixture):
    requests = {(fixture.get('player', 5), plot): fixture['start'] for plot in fixture['plots']}
    with (out/'AI_Behavior_Trees.csv').open(encoding='utf-8-sig', errors='replace', newline='') as log:
        return trace_work_trees(log, requests, 74, fixture['end'])


SPECIALTY_READ = '''
local player=assert(Players[case.player])
assert(not player:IsHuman())
local city=assert(player:GetCities():FindID(case.city))
local quarter=assert(Map.GetPlotByIndex(case.quarter))
local district=assert(city:GetDistricts():GetDistrictAtLocation(quarter:GetX(),quarter:GetY()))
assert(district:IsComplete() and not district:IsPillaged()
    and district:GetType()==GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index)
local buyer=assert(GameInfo.Buildings[case.specialty])
local buildings=city:GetBuildings()
local supplier=assert(Map.GetPlotByIndex(case.plots[1]))
assert(supplier:GetOwner()==case.player and supplier:GetDistrictType()==-1
    and supplier:GetResourceType()==GameInfo.Resources[case.resource].Index
    and Map.GetPlotDistance(supplier:GetX(),supplier:GetY(),quarter:GetX(),quarter:GetY())==1)
local plantation=GameInfo.Improvements.IMPROVEMENT_PLANTATION.Index
local ui=assert(ExposedMembers.CSC_Adjacency)
local building=assert(ui.GetEconomyCityNumber)(case.player,case.city,'currentBuilding',0)==buyer.Index
local operating=buildings:HasBuilding(buyer.Index) and buildings:GetBuildingLocation(buyer.Index)==case.quarter
    and not buildings:IsPillaged(buyer.Index)
local planted=supplier:GetImprovementType()==plantation
local pillaged=planted and supplier:IsImprovementPillaged()
local controlActive=CSC_SPECIALTY_CONTROL_ACTIVE==true
'''


def specialty_replay(session, controller, fixture, apply, output):
    """Test the actual Stage 4 queue with one matched, legal supplier loss."""
    scope = 'local case=' + lua(fixture) + '\n'

    def sample(label):
        report = '''
print(string.format('CSC_SPECIALTY={"turn":%d,"building":%s,"operating":%s,"planted":%s,"pillaged":%s,"control":%s}',
    Game.GetCurrentGameTurn(),tostring(building),tostring(operating),tostring(planted),tostring(pillaged),tostring(controlActive)))
'''
        return parse(controller.cmd(scope + SPECIALTY_READ + report, 'CSC_AI_BakersGameplay', label), 'CSC_SPECIALTY')

    if not apply:
        # Match ordinary policy except for the exact unfinished Café quote.
        # F.New creates a fresh facts snapshot for each player publication.
        # Once the Café operates, both arms use the normal buyer evaluation.
        control = '''
local facts=assert(CSC_AI_EconomyFacts)
local create=assert(facts.New)
facts.New=function(player,...)
    local state=create(player,...)
    if player:GetID()==case.player then
        local commitment=assert(state.MaterialBuyerCommitment)
        state.MaterialBuyerCommitment=function(city,buyers,horizon)
            local quote=commitment(city,buyers,horizon)
            if city:GetID()==case.city and quote and quote.type==case.specialty then
                print('CSC_DURING_CONSTRUCTION_CONTROL turn='..Game.GetCurrentGameTurn())
                return nil
            end
            return quote
        end
    end
    return state
end
CSC_SPECIALTY_CONTROL_ACTIVE=true
'''
        session.issue_once('omit-quebec-unfinished-quote', scope + control, 'CSC_AI_BakersGameplay')

    samples = [sample('specialty-opening')]
    opening = samples[0]
    require(opening['control'] == (not apply), 'Specialty fixture ablation is not in the requested state')
    require(opening['planted'] and not opening['pillaged'] and not opening['operating'], 'Quebec source supplier differs')
    damaged = None
    while samples[-1]['turn'] < fixture['end']:
        # Advance normally to shortly before the archived Café start on 159.
        # Poll each subsequent turn to distinguish active construction from
        # the completed building, including if a replay chooses another item.
        turn = samples[-1]['turn']
        next_turn = min(turn + 5, 157) if turn < 157 else turn + 1
        controller.play(next_turn)
        current = sample('specialty-turn-' + str(next_turn))
        require(current['turn'] == next_turn, 'Unexpected Specialty replay boundary')
        if damaged is None and current['building'] and not current['operating'] and current['planted'] and not current['pillaged']:
            damage = '''
assert(building and not operating and planted and not pillaged)
ImprovementBuilder.SetImprovementPillaged(supplier,true)
'''
            session.issue_once('quebec-supplier-damage', scope + SPECIALTY_READ + damage, 'CSC_AI_BakersGameplay')
            post = sample('specialty-verified-loss')
            require(post == dict(current, pillaged=True), 'Specialty fixture changed the buyer or failed to pillage the supply')
            write_json(output/'specialty-before-loss.json', current)
            damaged = next_turn
            current = post
        samples.append(current)
        write_json(output/'supplier-snapshots.json', samples)
    return samples, dict(loss_turn=damaged)


def specialty_quotes(output, fixture):
    suppressed, published = [], []
    with (output/'Lua.log').open(encoding='utf-8-sig', errors='replace') as lines:
        for line in lines:
            if control := re.search(r'CSC_DURING_CONSTRUCTION_CONTROL turn=(\d+)', line):
                suppressed.append(int(control[1]))
            if match := COMMITTED_BUYER.search(line):
                quote = dict(component.split('=', 1) for component in match[1].split())
                if (int(quote['player']), int(quote['quarter']), int(quote['plot']), quote['buyer']) == (
                        fixture['player'], fixture['quarter'], fixture['plots'][0], fixture['specialty']):
                    published.append(quote)
    return dict(suppressed_turns=suppressed, published=published)


def freeze_dispatch_packages(output, packages, candidate, matched_csc, finish_enabled=False):
    """Stage only the runtime files that implement ordinary Builder dispatch."""
    csc = next(item for item in packages if item['role'] == 'csc')
    ce = next(item for item in packages if item['role'] == 'ce')
    # Both arms use the same Lua, including the current prerequisite quote
    # rules. Older CE exposes zero dispatch capacity, so Lua sends no worker bids.
    paths = tuple(Path('Lua_UI/AI')/(name+'.lua') for name in (
        'CSC_AI_BakersGameplay', 'CSC_AI_DistrictBridge', 'CSC_AI_QuarterPlacement',
    ))
    frozen = output/'frozen-dispatch-csc' if finish_enabled or matched_csc is None else matched_csc
    if matched_csc is None:
        shutil.copytree(csc['source'], frozen)
        for path in paths:
            require((frozen/path).is_file(), 'CSC dispatch script absent from archived package: '+str(path))
            shutil.copyfile(ROOT/'Civ Supply Chains'/path, frozen/path)
    elif finish_enabled:
        shutil.copytree(matched_csc, frozen)
    if matched_csc is None or finish_enabled:
        # Freeze the decision explicitly so these comparisons still isolate
        # the scheduling treatment after the gameplay default changes.
        publisher = frozen / paths[0]
        code = publisher.read_bytes().removeprefix(FINISH_OFF)
        publisher.write_bytes((FINISH_ON if finish_enabled else FINISH_OFF) + code)
    files = manifest(frozen)
    allowed = set(map(str, paths))
    require(files.keys() == csc['files'].keys()
            and {name for name in files if files[name] != csc['files'][name]} <= allowed,
            'Unexpected CSC dispatch package change')
    csc.update(source=frozen, files=files)
    if candidate:
        relative = Path('Binaries/Win64') / DLL
        frozen = output/'frozen-dispatch-ce'
        shutil.copytree(ce['source'], frozen)
        shutil.copyfile(candidate, frozen/relative)
        files = manifest(frozen)
        require(files.keys() == ce['files'].keys()
                and {name for name in files if files[name] != ce['files'][name]} == {str(relative)},
                'Builder dispatch treatment must change just the CE DLL')
        ce.update(source=frozen, files=files)
    result = {item['role']: package_digest(item['files']) for item in packages}
    write_json(output/'dispatch-packages.json', result)
    return result


def packaged_evidence(output, fixture, ready):
    """Attribute receipts to the runtime and keep exact job identities for comparison."""
    receipts, offers = [], []
    with (output/'Lua.log').open(encoding='utf-8-sig', errors='replace') as lines:
        for line in lines:
            if match := RECEIPT.search(line):
                status = json.loads(match[3])
                if fixture['start'] <= int(match[1]) <= fixture['end']:
                    require(status.get('workerFaults', 0) == 0, 'Worker pass reported an incomplete swap')
                    for label in ('workerStart', 'workerFinish'):
                        if status.get(label, 0):
                            receipts.append(dict(turn=int(match[1]), event=label, count=status[label],
                                                 first=status[label+'First']))
            if (match := OFFER.search(line)) and match[1] == 'WORKER':
                row = {name: int(value) for name, value in (part.split('=') for part in match[2].split())}
                if (row['player'], row['city'], row['plot']) == (5, fixture['city'], fixture['plots'][0]):
                    offers.append(row)
    return dict(ready=ready, receipts=receipts, offers=offers)


def run_arm(source, output, fixture, apply, frida, *, workforce=False, early_dispatch=False,
            packaged=False, candidate=None, matched_csc=None, finish_seed=False, finish_source=None,
            finish_port_replay=False):
    start, endpoint = fixture['start'], fixture['end']
    root_turn = FIXTURES['kish']['start'] if finish_source else start
    require(not finish_port_replay or (packaged and candidate and finish_source and not frida),
            'The port check needs the retained finishing fixture and the staged CE binary')
    plan = prepare(source, output, root_turn, root_turn, None, read_only=True,
                   finish_port_replay=finish_port_replay)
    require(plan.identity['map_signature'][0] == 74 and not native_inventory(),
            'Require the recorded Fractal with no existing Civ or FireTuner session')
    native = Path(plan.checkpoint['native_save'])
    digest = plan.checkpoint['sha256']
    expected_census = plan.expected_census
    if finish_source:
        saved = load(finish_source/'finish-checkpoint.json')
        preparation = load(finish_source/'protocol.json')
        expected_census = load(finish_source/'finish-census.json')
        require(load(finish_source/'session-closed.json')['verified'] and preparation['finish_seed']
                and preparation['save_sha256'] == digest and saved['turn'] == start == expected_census['turn'],
                'Finishing comparison needs the verified shared preparation')
        native, digest = Path(saved['native_save']), saved['sha256']
        require(saved['verified'] and native.resolve().parent == plan.saves
                and Path(saved['archive']).resolve().parent == finish_source.resolve()
                and sha(native) == sha(Path(saved['archive'])) == digest,
                'Finishing checkpoint digest or location differs')
    controlled_damage = fixture['city'] == 393221
    specialty = fixture.get('specialty')
    repair_policy = controlled_damage and apply
    output.mkdir()
    runtime = freeze_dispatch_packages(output, plan.packages, candidate, matched_csc,
                                       finish_enabled=bool(finish_source and apply)) if packaged else None
    if repair_policy:
        item = next(item for item in plan.packages if item['role'] == 'csc')
        frozen = output/'frozen-quarter-recovery'
        relative = Path('Lua_UI/AI/CSC_AI_QuarterPlacement.lua')
        shutil.copytree(item['source'], frozen)
        shutil.copyfile(ROOT/'Civ Supply Chains'/relative, frozen/relative)
        files = manifest(frozen)
        require(files.keys() == item['files'].keys()
                and {name for name in files if files[name] != item['files'][name]} == {str(relative)},
                'Umma treatment must change only the Quarter prerequisite rule')
        item.update(source=frozen, files=files)
    write_json(output/'protocol.json', dict(start=start, endpoint=endpoint, fixture=fixture, apply=apply,
                                          save_sha256=digest, packages=plan.protocol['input_digests'],
                                          new_quarter_recovery=repair_policy, controlled_damage=controlled_damage or bool(specialty),
                                          observe_workforce=workforce, early_dispatch=early_dispatch, runtime=runtime,
                                          finish_seed=finish_seed, finish_source=str(finish_source) if finish_source else None))
    controller = make_probe_controller(output, user_root=plan.user_root)
    controller.study_endpoint = endpoint
    controller.autoplay_interval_seconds = plan.protocol['interval_minutes'] * 60
    controller.allow_one_more_turn = controller.allow_observer_congress_review = True
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    session = NativeSession(output, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    copied, samples, opening_census = [], [], None
    attachment = script = None

    def verify_packages():
        for item in copied:
            require(manifest(item['install']) == manifest(item['source']) == item['files'], 'Replay package drift')
        for item in plan.extras.values():
            require(manifest(Path(item['path'])) == item['files'], 'Optional replay package drift')

    def census_at(turn, label):
        scope = 'CSC_ENDPOINT_PLAYERS=' + lua(plan.identity['original_ai']) + '\nCSC_ENDPOINT_EXPECTED_TURN=' + str(turn) + '\n'
        raw = controller.cmd(scope+read(HERE/'full_game_census.lua'), 'CSC_AI_BakersGameplay', label)
        return parse_census(raw, turn)

    def source_gate():
        opening_census = census_at(start, 'dispatch-source-census')
        write_json(output/'source-census.json', opening_census)
        proof = compare_structure(expected_census, opening_census)
        require(proof['verified'], 'Loaded supplier world differs from checkpoint')
        write_json(output/'source-structure-comparison.json', proof)
        return True

    def play(opening, dispatch=None, through=endpoint):
        current = opening
        armed_windows = 0
        while current['turn'] < through:
            if dispatch:
                # Stop adjusting the decision once a first supplier works.
                missing = [p['plot'] for p in current['plots'] if p['valid'] and not p['working']]
                resolved = any(p['working'] for p in current['plots'])
                armed_plots = missing if current['buyerWorking'] and not resolved else []
                dispatch.exports_sync.arm(armed_plots)
                armed_windows += bool(armed_plots)
            next_turn = min(current['turn'] + (1 if finish_source else 5), through)
            controller.play(next_turn)
            state = controller.state_read('dispatch-clock')
            require(state['turn'] == next_turn and not state['active'], 'Unexpected dispatch replay boundary')
            current = snapshot(controller, fixture, 'dispatch-turn-'+str(next_turn))
            require(current['turn'] == next_turn, 'Unexpected supplier snapshot turn')
            samples.append(current)
            write_json(output/'supplier-snapshots.json', samples)
        return armed_windows

    def verify_onsite():
        # Read the exact Builder from the repeated Kish result. Native custody
        # is checked again by the finishing consumer at its normal update.
        code = '''
local p=assert(Players[5])
for _,unit in p:GetUnits():Members()do
    if unit:GetID()==4390912 then
        assert(unit:GetX()==42 and unit:GetY()==29 and unit:GetBuildCharges()>0)
        print('CSC_FINISH_ONSITE')
        return
    end
end
'''
        require('CSC_FINISH_ONSITE' in controller.cmd(code, 'CSC_AI_BakersGameplay', 'finish-onsite'),
                'Kish lacks the on-site charged Builder at the shared boundary')

    try:
        for item in plan.packages:
            shutil.copytree(item['source'], item['install'])
            copied.append(item)
        session.start(lambda: launch(SimpleNamespace(binary=plan.binary), output))
        session.wait_context('MainMenu')
        configure(controller, output, csc_id=plan.protocol['ce'])
        enable(session, plan.protocol['csc'])
        for identity in plan.extras:
            enable(session, identity)
        require({k for k, v in flags(controller, 'dispatch-packages')['mods'].items() if v} ==
                {plan.protocol['ce'], plan.protocol['csc'], *plan.extras}, 'Unexpected active dispatch packages')
        session.load_once(native, sha256=digest, native_directory=plan.saves, turn=start,
                          contexts=('GameCore_Tuner', 'CSC_AI_BakersGameplay'), eligibility=source_gate)
        ce = next(item for item in copied if item['role'] == 'ce')
        verify_modules(session, ce['install']/'Binaries/Win64'/DLL, output, native_profile(plan.binary)[1])
        if controlled_damage:
            write_json(output/'before-damage.json', snapshot(controller, fixture, 'dispatch-before-damage'))
            session.issue_once('umma-damage-fixture', UMMA_DAMAGE, 'CSC_AI_BakersGameplay')
        if specialty:
            samples, evidence = specialty_replay(session, controller, fixture, apply, output)
        else:
            opening = snapshot(controller, fixture, 'dispatch-opening')
            require(opening['turn'] == start and opening['buyerWorking'] == fixture['buyer_working'] and all(
                plot['valid'] and not plot['working'] and plot['pillaged'] == fixture['pillaged']
                and plot['improvement'] == (opening['farm'] if fixture['pillaged'] else -1)
                for plot in opening['plots']), 'Checkpoint lacks the verified supplier loss')
            samples.append(opening)
            write_json(output/'opening.json', opening)
        if packaged:
            raw = controller.cmd("print('CSC_DISPATCH_CAPABILITY='..CE_AIMaterialDevelopmentStatus())\n"
                                 "print('CSC_DISPATCH_PATH='..tostring(UnitManager and type(UnitManager.GetMoveToPath)))",
                                 'CSC_AI_BakersGameplay', 'worker-dispatch-capability')
            status = parse(raw, 'CSC_DISPATCH_CAPABILITY')
            require(bool(status.get('workerReady')) == bool(candidate), 'Unexpected native worker capability')
            if finish_source:
                require(status.get('workerFinishOnly') == 1, 'The comparison requires the finish-only consumer')
                require(apply or not status['workerOffers'], 'Default CSC published an experimental finish offer')
                verify_onsite()
            path = re.search(r'CSC_DISPATCH_PATH=(\w+)', raw)
            require(path is not None, 'Missing worker path API readback')
            status['route_api'] = path[1]
            write_json(output/'dispatch-capability.json', status)
            play(opening)
            if finish_seed:
                require(samples[-1]['buyerWorking'] and samples[-1]['plots'][0]['pillaged'],
                        'The preparation must stop before the supplier is repaired')
                verify_onsite()
                write_json(output/'finish-census.json', census_at(endpoint, 'finish-census'))
                checkpoint = save_inactive_boundary(controller, turn=endpoint, name='CSC_KISH_FINISH',
                                                    native_directory=plan.saves, archive=output/'turn-166.Civ6Save')
                write_json(output/'finish-checkpoint.json', checkpoint)
        elif workforce:
            # Reuse the exact Kish recruitment and custody observer from the
            # earlier handoff study. The admission/hold modifier stays off.
            # The treatment changes scheduling only, in the same native
            # priority pass and with a free, charged, local Builder present.
            scope = dict(player=5, city=fixture['city'], improvement=opening['farm'],
                         plots=[dict(plot=2112,x=40,y=28), *opening['plots']], earlyDispatch=early_dispatch)
            if early_dispatch:
                # Match the control's saved opening and five-turn boundaries.
                # The first-in-pass variant needs only the turn-172 handoff.
                play(opening, through=170 if early_dispatch in ('first', 'finish') else 160)
            with observe_workers(frida, session, controller, scope, output):
                play(samples[-1])
            evidence = load(output/'worker-native-evidence.json')
            evidence['handoffs'] = worker_handoffs(evidence['events'])
        elif not specialty:
            probe = HERE/'material_dispatch_probe.js'
            shutil.copyfile(probe, output/probe.name)
            modules = load(output/'loaded-modules.json')
            scope = dict(player=5, city=fixture['city'], farm=opening['farm'], builder=opening['builder'],
                         plots=opening['plots'], cePath=modules[DLL]['path'], apply=apply)
            spec = dict(path=modules['GameCore_XP2_FinalRelease.dll']['path'], image_size=XP2_IMAGE_SIZE)
            attachment = frida.attach(session.owner.pid)
            script = attachment.create_script(read(probe))
            script.load()
            require(script.exports_sync.init(spec, scope), 'Native dispatch trace did not attach')
            armed_windows = play(opening, script)
            evidence = script.exports_sync.freeze()
            evidence['armed_windows'] = armed_windows
            write_json(output/'dispatch-native-evidence.json', evidence)
            require(evidence['active'] == 0 and evidence['fault'] is None and (evidence['samples'] or not armed_windows),
                    'Native dispatch capture incomplete')
    finally:
        if script:
            script.exports_sync.freeze()
        if attachment:
            attachment.detach()
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, output)
                          if (output/'original-preferences.json').exists() else None, restore_package=verify_packages)
        if session.closed or session.owner is None and not native_inventory():
            for item in copied:
                item['install'].rename(output/item['install'].name)
            if session.closed:
                for name in LOGS:
                    log = plan.user_root/'Logs'/name
                    if log.is_file():
                        shutil.copyfile(log, output/name)
    require(session.closed and sha(native) == digest, 'Dispatch replay did not close or preserve the original save')
    if packaged:
        evidence = packaged_evidence(output, fixture, bool(candidate))
    result = dict(opening=samples[0], endpoint=samples[-1], jobs=case_jobs(output, fixture), native=evidence)
    if specialty:
        result['quotes'] = specialty_quotes(output, fixture)
        result['restored'] = next((item for item in samples if evidence['loss_turn'] is not None
                                   and item['turn'] > evidence['loss_turn'] and item['planted'] and not item['pillaged']), None)
    write_json(output/'result.json', result)
    return result


def run_finish_pair(source, output, preparation, candidate, *, finish_port_replay=False):
    saved = load(preparation/'finish-checkpoint.json')
    require(saved['turn'] == 166, 'Expected the retained Kish custody boundary')
    fixture = dict(FIXTURES['kish'], start=166, end=170)
    output.mkdir()
    control, treatment = output/'control', output/'treatment'
    before = run_arm(source, control, fixture, False, None,
                     packaged=True, candidate=candidate, finish_source=preparation,
                     finish_port_replay=finish_port_replay)
    after = run_arm(source, treatment, fixture, True, None, packaged=True, candidate=candidate,
                    matched_csc=control/'frozen-dispatch-csc', finish_source=preparation,
                    finish_port_replay=finish_port_replay)
    before_packages = load(control/'dispatch-packages.json')
    after_packages = load(treatment/'dispatch-packages.json')
    require(before_packages['ce'] == after_packages['ce'], 'Finishing arms used different CE builds')
    base_csc = control/'frozen-dispatch-csc'
    trial_csc = treatment/'frozen-dispatch-csc'
    qualify_packages(base_csc, trial_csc)
    for event in (*before['native']['receipts'], *after['native']['receipts']):
        require(event['event'] == 'workerFinish', 'The finishing consumer reordered recruitment')
    require(not before['native']['offers'] and not before['native']['receipts'],
            'The scheduler-off arm intervened in worker scheduling')
    proof = compare_structure(load(control/'source-census.json'), load(treatment/'source-census.json'))
    require(proof['verified'] and before['opening'] == after['opening'], 'Finishing arms differ at load')
    write_json(output/'source-structure-comparison.json', proof)
    write_json(output/'comparison.json', dict(control=before, treatment=after, checkpoint_sha256=saved['sha256']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--probe-dependencies', type=Path)
    parser.add_argument('--case', choices=FIXTURES, required=True)
    parser.add_argument('--reference-control', type=Path, help='Reuse a verified passive arm after correcting the probe')
    workforce = parser.add_mutually_exclusive_group()
    workforce.add_argument('--observe-workforce', action='store_true', help='Trace Kish worker pools and assignment with stock decisions')
    workforce.add_argument('--early-workforce', action='store_true', help='Run the scoped early-recruitment treatment against the verified passive arm')
    workforce.add_argument('--first-recruitment', action='store_true', help='Test Kish at the start of its usual native priority pass on turn 172')
    workforce.add_argument('--finish-recruitment', action='store_true', help='Also give Kish one finishing turn if its assigned Builder is already on the Flax')
    workforce.add_argument('--packaged-dispatch', type=Path, metavar='CE_DLL',
                           help='Compare current integrated CSC with and without the new CE worker consumer')
    workforce.add_argument('--finish-only', nargs=2, type=Path, metavar=('PREPARED', 'CE_DLL'),
                           help='Compare opt-in finishing against default behaviour from the same saved Kish assignment')
    args = parser.parse_args()
    if args.finish_only:
        if args.case != 'kish' or args.reference_control:
            parser.error('Finishing compares two new arms of the same Kish checkpoint')
        preparation, candidate = (path.resolve(strict=True) for path in args.finish_only)
        if not preparation.is_dir() or candidate.suffix.lower() != '.dll':
            parser.error('Finishing requires a preparation directory and a built CE DLL')
        run_finish_pair(args.source, args.output, preparation, candidate)
        return
    if args.reference_control and args.case != 'kish':
        parser.error('The saved passive arm is supported for Kish')
    if args.observe_workforce and (args.case != 'kish' or args.reference_control):
        parser.error('Use the workforce trace as a single unmodified Kish replay')
    candidate = args.packaged_dispatch
    if candidate:
        if args.case != 'kish' or args.reference_control:
            parser.error('Packaged dispatch requires a new matched Kish pair')
        candidate = candidate.resolve(strict=True)
        if candidate.suffix.lower() != '.dll':
            parser.error('The packaged dispatch treatment requires a built CE DLL')
    early_dispatch = 'finish' if args.finish_recruitment else 'first' if args.first_recruitment else args.early_workforce
    if early_dispatch and (args.case != 'kish' or not args.reference_control):
        parser.error('Early recruitment needs the matching verified passive Kish arm')
    frida = None
    if args.case != 'quebec' and not candidate:
        if args.probe_dependencies is None:
            parser.error('Native dispatch replays require --probe-dependencies')
        dependencies = args.probe_dependencies.resolve(strict=True)
        sys.path.insert(0, str(dependencies))
        import frida
        require(frida.__version__ == '17.24.3' and Path(frida.__file__).resolve().is_relative_to(dependencies),
                'Existing pinned Frida package required')
    if args.observe_workforce:
        run_arm(args.source, args.output, FIXTURES['kish'], False, frida, workforce=True)
        return
    args.output.mkdir()
    fixture = FIXTURES[args.case]
    control = (args.reference_control or args.output/'control').resolve()
    treatment = args.output/'treatment'
    if args.reference_control:
        baseline = load(control/'protocol.json')
        require(not baseline['apply'] and load(control/'session-closed.json')['verified']
                and all(baseline['fixture'][k] == fixture[k] for k in ('start', 'end', 'city', 'quarter', 'plots')),
                'Reference must be the completed passive arm for this supplier')
        saved = load(args.source/f"checkpoint-{fixture['start']}.json")
        require(baseline['save_sha256'] == saved['sha256']
                and baseline['packages'] == load(args.source/'protocol.json')['input_digests'],
                'Reference save or packages differ')
        if early_dispatch:
            require(baseline['observe_workforce'] and not baseline.get('early_dispatch'),
                    'Early recruitment control must observe the same worker pools')
        before = load(control/'result.json')
    else:
        before = run_arm(args.source, control, fixture, False, frida, packaged=bool(candidate))
    after = run_arm(args.source, treatment, fixture, not early_dispatch, frida,
                    workforce=bool(early_dispatch), early_dispatch=early_dispatch,
                    packaged=bool(candidate), candidate=candidate,
                    matched_csc=control/'frozen-dispatch-csc' if candidate else None)
    if candidate:
        before_packages = load(control/'dispatch-packages.json')
        after_packages = load(treatment/'dispatch-packages.json')
        require(before_packages['csc'] == after_packages['csc'] and before_packages['ce'] != after_packages['ce'],
                'Expected a matched CSC runtime with the CE dispatch consumer isolated')
    opening_keys = ('turn', 'building', 'operating', 'planted', 'pillaged') if fixture.get('specialty') else (
        'turn', 'farm', 'builder', 'buyerWorking', 'plots')
    require(all(before['opening'][k] == after['opening'][k] for k in opening_keys), 'Different supplier opening')
    if fixture.get('specialty'):
        require(before['native']['loss_turn'] == after['native']['loss_turn'], 'Specialty arms differ at the buyer opening')
    proof = compare_structure(load(control/'source-census.json'), load(treatment/'source-census.json'))
    require(proof['verified'], 'Matched dispatch opening census differs')
    write_json(args.output/'source-structure-comparison.json', proof)
    write_json(args.output/'comparison.json', dict(control=before, treatment=after, control_evidence=str(control)))


if __name__ == '__main__':
    main()
