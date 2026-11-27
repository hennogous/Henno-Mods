"""Create one turn-one save and replay it with full and selective Quarter forecasting."""
import argparse
from collections import Counter
from pathlib import Path
from statistics import mean, median
from types import SimpleNamespace

from driver import (HERE, HeldProcess, NativeSession, launch, load, lua, make_probe_controller,
                    native_inventory, read, require, restore_preferences, sha, write_json)
from economy_factorial import ARMS, host_roster, plan, play, read_opening, select_stack, verify_pins
from full_game_controller.checkpoint import save_inactive_boundary
from full_game_results import quarter_rows, summarize
from shortlist_results import fields


def install_observers(controller, folder, seats, pricing):
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


def compare(root):
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
        endpoint=load(folder/'checkpoint.json')
        require(endpoint['turn']==250 and sha(Path(endpoint['native_save']))==endpoint['sha256']
                and load(folder/'session-closed.json')['verified'],'Missing verified endpoint')
        valid,_,processing=observed_turns(folder,250,2)
        require(processing['published_packets']==249 and not processing['failed_attempts'],
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
                    stamp=r['turn'],r['player']
                    require(stamp not in passes,'Duplicate planner pass')
                    passes.add(stamp)
                    calls[r['turn']]+=r['calls'];skipped[r['turn']]+=r['skipped']
                elif 'CSC_QUARTER_WATCH_SITE\t' in line:
                    r=fields(line)
                    if r['event'] in ('foundation','first-observed') and r['player'] in opening['original_ai']:
                        identity=r['district'],r['plot']
                        events.setdefault(identity,r)
        require((sum(skipped.values())>0)==(name=='selective') and set(calls)==set(range(2,251)),
                'Missing selective or full pricing evidence')
        final=folder/'full-census-250.json'
        held=quarter_rows(final)
        sites.append({(q['profile'],q['plot']) for q in held})
        direct=processing['publisher_wall']
        require(direct['turns']==249,'Incomplete publisher clock')
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
        result[name].update(clean_turns=len(values),whole_mean=mean(values),whole_median=median(values),whole_max=max(values),
            late_mean=mean(clean[i][t] for t in common if t>200))
    result['shared_endpoint_sites']=len(sites[0]&sites[1])
    result['full_only_sites']=sorted(sites[0]-sites[1])
    result['selective_only_sites']=sorted(sites[1]-sites[0])
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('phase',choices=['prepare','full','selective','compare'])
    parser.add_argument('--seed',type=int,default=27112601)
    args=parser.parse_args()
    folder=args.output.resolve()
    if args.phase=='compare':
        write_json(folder/'comparison.json',compare(folder))
        raise SystemExit(0)
    pins=plan(args.reference.resolve(),[args.seed])
    game=pins['seeds'][args.seed]
    if args.phase=='prepare':
        prepare(pins,args.seed,game,folder/'opening')
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
