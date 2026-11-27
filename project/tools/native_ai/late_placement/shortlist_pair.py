"""Create one turn-one save and replay it with full and selective Quarter forecasting."""
import argparse
from collections import Counter
from pathlib import Path
import shutil
from statistics import mean, median
from types import SimpleNamespace

from driver import (HERE, HeldProcess, NativeSession, launch, load, lua, make_probe_controller,
                    native_inventory, read, require, restore_preferences, sha, write_json)
from economy_factorial import ARMS, host_roster, plan, play, read_opening, select_stack, verify_pins
from full_game_controller.checkpoint import save_inactive_boundary
from full_game_results import quarter_rows, summarize
from shortlist_results import fields


def install_pricing(controller, folder, pricing):
    context='CSC_AI_BakersGameplay'
    raw=controller.cmd("""assert(CSC_AI_EconomyAdapters.SupportsSelectiveQuarterForecasts)
CSC_AI_EconomyAdapters.MeasureQuarterPricing=true
print('CSC_QUOTE_COUNTER_READY')""",context,'count-executed-forecasts')
    require('CSC_QUOTE_COUNTER_READY' in raw,'Missing actual forecast counter')
    if pricing=='selective':
        policy=read(HERE/'shortlist_observer.lua')
        raw=controller.cmd('local CSC_LIVE_SHORTLIST=true\n'+policy,context,'enable-selective-forecasting')
        require('CSC_SHORTLIST_LIVE_READY' in raw,'Selective planner failed to activate')
        write_json(folder/'policy.json',dict(pricing=pricing,sha256=sha(HERE/'shortlist_observer.lua')))
    else:
        require(pricing=='full','Unknown Quarter pricing mode')
        raw=controller.cmd("assert(not CSC_AI_EconomyAdapters.ShortlistObserver);print('CSC_FULL_PRICING')",
                           context,'verify-full-forecasting')
        require('CSC_FULL_PRICING' in raw,'Control must run the ordinary full planner')


def install_observers(controller, folder, seats, pricing):
    install_pricing(controller,folder,pricing)
    context='CSC_AI_BakersGameplay'
    raw=controller.cmd('local CSC_LIFECYCLE_ONLY=true\n'+read(HERE/'quarter_placement_watch.lua'),
                       context,'observe-actual-quarter-foundations')
    require('CSC_QUARTER_WATCH_INSTALLED' in raw,'Missing Quarter lifecycle observer')
    census=read(HERE/'full_game_census.lua')
    raw=controller.cmd('local CSC_ENDPOINT_PLAYERS='+lua(list(seats))+'''
GameEvents.OnGameTurnStarted.Add(function()
    local CSC_ENDPOINT_EXPECTED_TURN=Game.GetCurrentGameTurn()
    if CSC_ENDPOINT_EXPECTED_TURN%25~=0 then return end
    print('CSC_FULL_RUN_CENSUS_BEGIN',CSC_ENDPOINT_EXPECTED_TURN)
'''+census+"\nend)\nprint('CSC_PLACEMENT_CENSUS_READY')",context,'observe-materials-and-customers')
    require('CSC_PLACEMENT_CENSUS_READY' in raw,'Missing supply-chain census')


def prepare(pins, seed, game, folder):
    require(not native_inventory(), 'Another session owns the game')
    folder.mkdir(parents=True)
    controller = make_probe_controller(folder,user_root=Path(pins['userdata']))
    session = NativeSession(folder,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    try:
        session.start(lambda: launch(SimpleNamespace(binary=Path(pins['binary'])),folder))
        session.wait_context('MainMenu')
        select_stack(session,folder,[pins['packages'][name]['id'] for name in ARMS['combined']])
        session.issue_once('host-shared-opening',host_roster(seed,game),'MainMenu')
        session.ready_after_issue(1,('GameCore_Tuner','PlotInfo'),timeout=600,
            eligibility=lambda: read_opening(controller,folder,game['roster'],csc=True,cl=True))
        record=save_inactive_boundary(controller,turn=1,name=f'CSC_SHORTLIST_{seed}_START',
            native_directory=Path(pins['saves']),archive=folder/'opening.Civ6Save')
        write_json(folder/'checkpoint.json',record)
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller,folder)
                          if (folder/'original-preferences.json').is_file() else None,menu_timeout=600)
    require(session.closed,'Opening session did not close')


def mature(pins, source, root, mode):
    """Time both policies on the same established Large empire using current CSC."""
    from ce_replay import DLL, verify_modules
    from economy_guidance_timing import install_clocks, observed_turns, verify_guidance
    record=load(source/'on/checkpoint.json')
    start=record['turn']
    require(start==350 and sha(Path(record['native_save']))==record['sha256'] and not native_inventory(),
            'Mature replay needs the verified free turn-350 save')
    folder=root/('mature-'+mode)
    folder.mkdir()
    user=Path(pins['userdata'])
    controller=make_probe_controller(folder,user_root=user)
    controller.study_endpoint=start+10
    controller.observer_warning_senders=range(1,10)
    controller.allow_observer_warning_dismissal=controller.allow_observer_first_meet_dismissal=True
    controller.allow_observer_congress_review=controller.allow_one_more_turn=True
    controller.autoplay_interval_seconds=2700
    session=NativeSession(folder,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    try:
        session.start(lambda:launch(SimpleNamespace(binary=Path(pins['binary'])),folder))
        session.wait_context('MainMenu')
        select_stack(session,folder,[pins['packages'][n]['id'] for n in ARMS['combined']])
        def eligible():
            verify_guidance(controller,user,folder,True,'opening')
            return True
        session.load_once(record['native_save'],sha256=record['sha256'],native_directory=pins['saves'],
            turn=start,contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),eligibility=eligible,timeout=600)
        verify_modules(session,Path(pins['packages']['ce']['path'])/'Binaries/Win64'/DLL,folder,pins['core_sha256'])
        install_pricing(controller,folder,mode)
        install_clocks(controller)
        controller.play(start+5)
        controller.play(start+10)
        verify_guidance(controller,user,folder,True,'endpoint')
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda:restore_preferences(controller,folder)
                          if (folder/'original-preferences.json').exists() else None,menu_timeout=600)
    require(session.closed,'Mature session did not close')
    shutil.copyfile(user/'Logs/Lua.log',folder/'Lua.log')
    valid,_,g=observed_turns(folder,start+10,start+1)
    log=read(folder/'Lua.log')
    quoted=[fields(l) for l in log.splitlines() if 'CSC_QUARTER_PRICING turn=' in l]
    require(g['published_packets']==10 and not g['failed_attempts'] and 'CSC_SHORTLIST_ERROR' not in log
            and (any(r['skipped'] for r in quoted)==(mode=='selective')),'Incomplete mature timing evidence')
    write_json(folder/'measurements.json',dict(clean=valid,guidance=g['publisher_wall'],save=record['sha256'],
        calls=sum(r['calls'] for r in quoted),skipped=sum(r['skipped'] for r in quoted)))


def compare(root,through=250):
    from economy_guidance_timing import observed_turns
    start=load(root/'opening/checkpoint.json')
    opening=load(root/'opening/source.json')
    clean=[]
    sites=[]
    result={}
    for name in ('full','selective'):
        folder=root/name
        require(load(folder/'session-load-input.json')['sha256']==start['sha256']
                and load(folder/'source.json')==opening,'Different opening map or seat')
        require(load(folder/'session-closed.json')['verified'],'Session did not close')
        if through==250:
            endpoint=load(folder/'checkpoint.json')
            require(endpoint['turn']==250 and sha(Path(endpoint['native_save']))==endpoint['sha256'],
                    'Missing verified endpoint')
        valid,_,processing=observed_turns(folder,through,2)
        require(processing['published_packets']==through-1 and not processing['failed_attempts'],
                'Incomplete guidance publication')
        clean.append(valid)
        calls,skipped,events=Counter(),Counter(),{}
        passes=set()
        with (folder/'Lua.log').open(encoding='utf-8-sig',errors='replace') as stream:
            for line in stream:
                require(not any(x in line for x in ('CSC_SHORTLIST_ERROR','CSC_AI_ECONOMY_FAILED',
                              'CSC_QUARTER_WATCH_FAULT','CSC_FACTOR_ECONOMY_FAILED')),'Live policy or observation fault')
                if 'CSC_QUARTER_PRICING turn=' in line:
                    r=fields(line)
                    if not 2<=r['turn']<=through:continue
                    stamp=r['turn'],r['player']
                    require(stamp not in passes,'Duplicate planner pass')
                    passes.add(stamp)
                    calls[r['turn']]+=r['calls'];skipped[r['turn']]+=r['skipped']
                elif 'CSC_QUARTER_WATCH_SITE\t' in line:
                    r=fields(line)
                    if r['turn']<=through and r['event'] in ('foundation','first-observed') and r['player'] in opening['original_ai']:
                        identity=r['district'],r['plot']
                        events.setdefault(identity,r)
        require((sum(skipped.values())>0)==(name=='selective') and set(calls)==set(range(2,through+1)),
                'Missing selective or full pricing evidence')
        final=folder/f'full-census-{through}.json'
        held=quarter_rows(final)
        sites.append({(q['profile'],q['plot']) for q in held})
        direct=processing['publisher_wall']
        require(direct['turns']==through-1,'Incomplete publisher clock')
        result[name]=dict(passes=len(passes),calls=sum(calls.values()),skipped=sum(skipped.values()),
            publisher_mean=direct['average_ms']/1000,publisher_max=direct['max_ms']/1000,
            at_foundation=dict(sites=len(events),confirmed_events=sum(r['event']=='foundation' for r in events.values()),
                base=sum(r['base']>0 for r in events.values()),both=sum(r['base']>0 and r['spec']>0 for r in events.values()),
                river=sum(r['river']=='true' for r in events.values()),
                current_at_least_two=sum(float(r['eligibleProduction'])+float(r['eligibleGold'])>=2 for r in events.values()),
                mill_potential_at_least_four=sum(float(r['millForecastTotal'])>=4 for r in events.values())),
            final=summarize(final),tailors_stage2_host=sum(q['profile']=='TAILORS' and any(
                stage=='2' and complete=='true' for _,stage,host,complete,status in q['customers']) for q in held))
    common=sorted(set(clean[0])&set(clean[1]))
    require(common,'Missing matched turn timings')
    for i,name in enumerate(('full','selective')):
        values=[clean[i][t] for t in common]
        late=[clean[i][t] for t in common if t>200]
        result[name].update(clean_turns=len(values),whole_mean=mean(values),whole_median=median(values),whole_max=max(values),
            late_mean=mean(late) if late else None)
    result['shared_endpoint_sites']=len(sites[0]&sites[1])
    result['full_only_sites']=sorted(sites[0]-sites[1])
    result['selective_only_sites']=sorted(sites[1]-sites[0])
    result['through']=through
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('phase',choices=['prepare','full','selective','compare','mature-full','mature-selective'])
    parser.add_argument('--seed',type=int,default=27112601)
    parser.add_argument('--through',type=int,default=250,help='Last shared census turn for compare')
    parser.add_argument('--mature-source',type=Path,help='Large Standard benchmark with on/checkpoint.json')
    args=parser.parse_args()
    folder=args.output.resolve()
    if args.phase=='compare':
        write_json(folder/f'comparison-{args.through}.json',compare(folder,args.through))
        raise SystemExit(0)
    pins=plan(args.reference.resolve())
    if args.seed not in pins['seeds']:
        pins=plan(args.reference.resolve(),[args.seed])
    game=pins['seeds'][args.seed]
    if args.phase=='prepare':
        prepare(pins,args.seed,game,folder/'opening')
    elif args.phase.startswith('mature-'):
        if not args.mature_source:parser.error('A mature replay requires --mature-source')
        require(load(folder/'packages.json')==pins['packages'],'Mature replay packages differ from the campaign')
        mature(pins,args.mature_source,folder,args.phase.removeprefix('mature-'))
    else:
        pinned=folder/'packages.json'
        if pinned.exists():
            require(load(pinned)==pins['packages'],'Packages changed between replay arms')
        else:
            write_json(pinned,pins['packages'])
        require(not native_inventory(),'Another session owns the game')
        record=load(folder/'opening/checkpoint.json')
        require(record['verified'] and record['turn']==1 and sha(Path(record['archive']))==record['sha256'],
                'Shared opening changed')
        play(pins,args.seed,game,'combined',folder/args.phase,guidance=True,
             opening=record,pricing=args.phase)
