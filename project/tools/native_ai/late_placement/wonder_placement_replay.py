"""Matched Wonder test using copies of the same qualified checkpoint.

Both arms construct the same small Tailors fixture if needed. The shared
controller owns loading, play and cleanup. Only the production adapter's
single exact Wonder offer is enabled in the treatment. Retain receipts and
native behavior logs independently of the construction outcome.
"""
import argparse
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

from ce_bakers_fresh import LOGS
from ce_replay import DLL, native_profile, verify_modules
from driver import (HeldProcess, NativeSession, configure, flags, launch, load, lua, make_probe_controller,
                    manifest, native_inventory, parse, read, require, restore_preferences, sha, write_json)
from later_stage_replay import candidate_package
from planning_continue import compare_structure, enable, parse_census, prepare

HERE = Path(__file__).resolve().parent
FIXTURE = HERE/'wonder_placement_fixture.lua'
PUBLISHER = Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua')
STOCK_PUBLISHER_ENTRY = b'''
-- Diagnostic only. Keep the original stock publisher dormant during the
-- pre-roll, then use the existing boundary callback on both matched copies.
function CSC_WonderFixtureActivatePublisher()
    assert(bridge.Available(), 'Wonder fixture lost the CE publishing path')
    CSC_WonderFixtureActivatePublisher = nil
    GameEvents.OnGameTurnStarted.Add(onBoundary)
    onBoundary()
end
'''


def stage_stock_fixture(item):
    """Keep the stock SQL and all original publisher code in the disposable copy."""
    dst = item['install']
    publisher = dst/PUBLISHER
    contents = publisher.read_bytes()
    require(b'Benchmark control retains observation helpers without publishing.' in contents,
            'Expected the proven dormant stock publisher')
    publisher.write_bytes(contents + STOCK_PUBLISHER_ENTRY)
    installed = manifest(dst)
    require(installed.keys() == item['files'].keys(), 'Stock fixture package inventory changed')
    changed = {path for path in installed if installed[path] != item['files'][path]}
    require(changed == {str(PUBLISHER)}, 'Unexpected stock fixture package change')
    return dict(item, files=installed)


def run_arm(source, out, dependencies, enabled, at, through, candidate, target=None, *, survey_only=False,
            prepare_at=None, expected_preparation=None, stock_hagmatana=False):
    plan = prepare(source, out, at, at, dependencies, read_only=True, stock_derived=stock_hagmatana)
    require(not native_inventory(), 'Foreign Civ or FireTuner session must be preserved')
    prepare_at = at if prepare_at is None else prepare_at
    require(at <= prepare_at <= (250 if survey_only else through - 1), 'Invalid fixture boundary')
    if stock_hagmatana:
        require(candidate is None and at == 100 and 138 <= prepare_at < 144
                and (plan.protocol['map_seed'],plan.protocol['game_seed']) == (27061117,37061117),
                'Hagmatana fixture requires the witnessed Pangaea source and a pre-reservation clock')
    out.mkdir(parents=True)
    shutil.copyfile(FIXTURE, out/FIXTURE.name)
    shutil.copyfile(Path(__file__), out/Path(__file__).name)
    write_json(out/'protocol.json',dict(diagnostic_only=True, source=str(source),
        checkpoint=plan.checkpoint, enabled=enabled, fixture_edits=not survey_only, stock_derived=stock_hagmatana,
        first=at, prepare_at=prepare_at, last=prepare_at if survey_only else through))
    controller=make_probe_controller(out,user_root=plan.user_root)
    controller.study_endpoint=prepare_at if survey_only else through
    controller.autoplay_interval_seconds=900
    controller.allow_one_more_turn=True
    controller.allow_observer_warning_dismissal=True
    controller.allow_observer_first_meet_dismissal=True
    controller.allow_observer_congress_review=True
    session=NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    copied=[]
    source_code=read(FIXTURE)

    def verify_packages():
        for item in copied:
            require(manifest(item['install'])==item['files'],'Test package drift')
        for item in plan.extras.values():
            require(manifest(Path(item['path']))==item['files'],'Optional package drift')

    def census(turn,label):
        code=f"CSC_ENDPOINT_PLAYERS={lua(plan.identity['original_ai'])}\nCSC_ENDPOINT_EXPECTED_TURN={turn}\n"
        raw=controller.cmd(code+read(HERE/'full_game_census.lua'),'CSC_AI_BakersGameplay','wonder-'+label)
        (out/(label+'.txt')).write_text(raw,encoding='utf-8')
        return parse_census(raw,turn)

    def gate():
        proof=compare_structure(plan.expected_census,census(at,'source-census'))
        write_json(out/'source-structure-comparison.json',proof)
        require(proof['verified'],'Loaded world differs from checkpoint')
        return True

    def fixture(mode,context,label=None):
        label=label or mode
        code=f'local CSC_WONDER_FIXTURE_MODE={lua(mode)}\n'
        code+=f'local CSC_WONDER_FIXTURE_TURN={prepare_at}\n'
        code+=f'local CSC_WONDER_FIXTURE_TARGET={lua(target)}\n' if target else ''
        code+=f'local CSC_WONDER_FIXTURE_ENABLED={lua(enabled)}\n'
        code+=f'local CSC_WONDER_STOCK_HAGMATANA={lua(stock_hagmatana)}\n'
        raw=controller.cmd(code+source_code,context,'wonder-'+label,wait=45)
        (out/(label+'.txt')).write_text(raw,encoding='utf-8')
        require('LUA_ERROR' not in raw,'Wonder fixture Lua error')
        return raw

    try:
        for item in plan.packages:
            if candidate and item['role']=='csc':
                item=dict(item,files=candidate_package(item['source'],candidate,item['install']))
            else:
                shutil.copytree(item['source'],item['install'])
            copied.append(item)
            if stock_hagmatana and not survey_only and item['role']=='csc':
                copied[-1]=stage_stock_fixture(item)
        write_json(out/'packages.json',{str(p['source']):dict(install=str(p['install']),files=p['files'])
                                       for p in copied})
        session.start(lambda:launch(SimpleNamespace(binary=plan.binary),out))
        session.wait_context('MainMenu')
        configure(controller,out,csc_id=plan.protocol['ce'])
        enable(session,plan.protocol['csc'])
        for identity in plan.extras:enable(session,identity)
        require({k for k,v in flags(controller,'wonder-test-mods')['mods'].items()if v}==
                {plan.protocol['ce'],plan.protocol['csc'],*plan.extras},'Unexpected active packages')
        session.load_once(plan.checkpoint['native_save'],sha256=plan.checkpoint['sha256'],
            native_directory=plan.saves,turn=at,contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),
            eligibility=gate)
        ce=next(item for item in copied if item['role']=='ce')
        _, core_sha = native_profile(plan.binary)
        verify_modules(session,ce['install']/'Binaries/Win64'/DLL,out,core_sha)
        if prepare_at > at:
            # Reproduce the unedited world before introducing the fixture.
            # Advance in guarded windows, then match both arms at the exact
            # preparation clock so an earlier native reservation stays visible.
            for boundary in range(at+5,prepare_at,5):
                controller.play(boundary)
            controller.play(prepare_at)
            preparation=census(prepare_at,'preparation-census')
            write_json(out/'preparation-census.json',preparation)
            if expected_preparation is not None:
                proof=compare_structure(expected_preparation,preparation)
                write_json(out/'preparation-comparison.json',proof)
                require(proof['verified'],'The pre-roll changed the matched fixture state')
        if target is None and stock_hagmatana:
            raw=fixture('hagmatana','PlotInfo')
            site=re.search(rf'CSC_WONDER_FIXTURE_HAGMATANA\t{prepare_at}\t((?:\d+\t){{4}}\d+)',raw)
            require(site is not None,'Archived Hagmatana Wonder footprint did not reappear')
            target=dict(zip(('player','city','site','quarter','wonder'),map(int,site[1].split('\t'))), existing=1)
            write_json(out/'candidates.json',[target])
        elif target is None:
            raw=fixture('scout','PlotInfo')
            require(f'CSC_WONDER_FIXTURE_SCOUT_END\t{prepare_at}\t' in raw,'Native Wonder survey incomplete')
            rows=[]
            for match in re.finditer(r'CSC_WONDER_FIXTURE_POTENTIAL\t((?:\d+\t){10})([^\r\n]+)',raw):
                names=('player','city','site','quarter','supplier','specialty','existing','working','unlocked','wonder')
                row=dict(zip(names,map(int,match[1].strip().split('\t'))))
                row['name']=match[2].strip();rows.append(row)
            write_json(out/'candidates.json', rows)
            # Prefer an existing Quarter, an already unlocked Wonder and a
            # working supplier, in that order. The tie order is stable.
            target=min(rows,default=None,key=lambda r:(-r['existing'],-r['unlocked'],-r['working'],
                                          r['player'],r['city'],r['site'],r['wonder'],r['quarter'],r['supplier'],r['specialty']))
        if not survey_only:
            require(target is not None,'No legal owned Wonder tile with Tailors, Base and Specialty supply')
            write_json(out/'target.json',target)
            setup=fixture('setup','CSC_AI_BakersGameplay')
            require(f'CSC_WONDER_FIXTURE_SETUP_END\t{prepare_at}' in setup,'Wonder world setup failed')
            offer=re.search(rf'CSC_WONDER_FIXTURE_OFFER\t{prepare_at}\t(\d+)\t(\d+)\t(\d+)\t(\d+)\t(\d+)',setup)
            require(offer is not None,'Live production offer absent')
            if stock_hagmatana:
                supply=re.search(r'CSC_WONDER_FIXTURE_SEEDED\t((?:\d+\t){3}\d+)',setup)
                require(supply is not None,'Failed to prepare two legal Hagmatana suppliers')
                chosen=dict(zip(('supplier','specialty','baseResource','specResource'),map(int,supply[1].split('\t'))))
                require(all(key not in target or target[key]==value for key,value in chosen.items()),
                        'The matched arms prepared different Hagmatana resources')
                target.update(chosen)
                write_json(out/'target.json',target)
            raw=fixture('verify','PlotInfo')
            require(f'CSC_WONDER_FIXTURE_VERIFIED\t{prepare_at}\t' in raw,'Legal fixture validation failed')
            raw=fixture('outcome','CSC_AI_BakersGameplay',label='initial-outcome')
            require(f'CSC_WONDER_FIXTURE_OUTCOME\t{prepare_at}\tfalse\t' in raw,'Wonder already completed at the replay start')
            controller.play(through)
            state=controller.state_read('wonder-final-clock')
            require(state['turn']==through and not state['active'],'Wrong diagnostic endpoint')
            raw=controller.cmd("print('CSC_WONDER_FINAL='..CE_AISupplierWonderProtectionStatus())",
                               'CSC_AI_BakersGameplay','wonder-final')
            (out/'native-endpoint.txt').write_text(raw,encoding='utf-8')
            status=parse(raw,'CSC_WONDER_FINAL')
            write_json(out/'native-endpoint.json',status)
            raw=fixture('outcome','CSC_AI_BakersGameplay')
            require(f'CSC_WONDER_FIXTURE_OUTCOME\t{through}\t' in raw,'Missing physical Wonder outcome')
            key=list(map(int,offer.groups()[:4]))
            write_json(out/'observation.json',dict(target=target,offer_key=key,offer_q8=int(offer[5]),end=state))
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda:restore_preferences(controller,out),
                          restore_package=verify_packages)
        if session.closed or session.owner is None and not native_inventory():
            for item in copied:item['install'].rename(out/item['install'].name)
        if session.closed:
            for name in LOGS:
                path=plan.user_root/'Logs'/name
                if path.is_file():shutil.copyfile(path,out/name)
    require(session.closed and sha(Path(plan.checkpoint['native_save']))==plan.checkpoint['sha256'],
            'Source save drift or unverified closure')
    return target


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--dependencies',type=Path)
    parser.add_argument('--candidate-source',type=Path)
    parser.add_argument('--at',type=int,default=200)
    parser.add_argument('--through',type=int,default=205)
    parser.add_argument('--prepare-at',type=int,help='Follow ordinary turns to this exact boundary before setup')
    parser.add_argument('--stock-hagmatana',action='store_true',help='Use the recorded stock Broadway case in matched copies')
    parser.add_argument('--survey-only',action='store_true',help='Record legal layouts and close without fixture edits')
    args=parser.parse_args()
    common=(args.at,args.through,args.candidate_source)
    prepare_at=args.at if args.prepare_at is None else args.prepare_at
    if args.survey_only:
        run_arm(args.source,args.output,args.dependencies,False,*common,survey_only=True,
                prepare_at=prepare_at,stock_hagmatana=args.stock_hagmatana)
    else:
        require(0 < args.through-prepare_at <= 35,'Wonder replay needs 1 to 35 turns after setup')
        target=run_arm(args.source,args.output/'off',args.dependencies,False,*common,
                       prepare_at=prepare_at,stock_hagmatana=args.stock_hagmatana)
        expected=None
        if prepare_at>args.at:
            expected=load(args.output/'off'/'preparation-census.json')
        run_arm(args.source,args.output/'on',args.dependencies,True,*common,target=target,prepare_at=prepare_at,
                expected_preparation=expected,stock_hagmatana=args.stock_hagmatana)
