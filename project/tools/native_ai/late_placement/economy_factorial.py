"""Run and report a two-seed, four-stack economy benchmark via the game controller."""

import argparse
import math
import re
import shutil
from pathlib import Path
from statistics import mean
from types import SimpleNamespace

from anchored_connection_results import loadable_layout_endpoint
from ce_bakers_fresh import host, package_identity
from ce_replay import DLL, development_package_files, native_profile, verify_modules
from driver import (HERE, HeldProcess, NativeSession, flags, launch, load, lua,
                    make_probe_controller, native_inventory, parse, read,
                    require, restore_preferences, sha, write_json)
from full_game_controller.checkpoint import SaveFileUnavailable, SavePermissionUnavailable, save_inactive_boundary
from full_game_controller.controller import ObserverEliminated
from full_game_observation import archive_censuses, archive_endpoint_autosave
from full_game_results import economy
from planning_continue import enable


TURNS = tuple(range(25, 251, 25))
ARMS = {'vanilla': (), 'csc': ('ce', 'csc'), 'city-lights': ('cl',),
        'combined': ('ce', 'csc', 'cl')}
METRICS = ('production', 'food', 'gross_gold', 'maintenance', 'net_gold', 'reserve', 'population', 'cities')
ADAPTER = Path('Lua_UI/AI/CSC_AI_EconomyAdapters.lua')


def plan(reference, seed_pool=()):
    """Freeze known cohorts without choosing seeds based on benchmark results."""
    games = {arm: reference / folder for arm, folder in (
        ('csc', 'standalone-candidate'), ('combined', 'city-lights-candidate'))}
    seeds = {}
    for arm, source in games.items():
        p = load(source / 'protocol.json')
        require(p['map'] == 'Continents' and p['map_size'] == 'small', 'Unexpected reference map')
        roster = {row['player']: row['leader'] for row in load(source/'source.json')['starts']}
        require(set(roster) == set(range(6)), 'Incomplete reference roster')
        seeds[p['map_seed']] = dict(game_seed=p['game_seed'], roster=roster, reuse_arm=arm, reference=str(source))
    if seed_pool:
        require(len(set(seed_pool))==len(seed_pool) and all(0<seed<2**31-1 for seed in seed_pool),
                'Map seeds must be unique and leave room for each paired game seed')
        rosters=[game['roster'] for game in seeds.values()]
        seeds={seed:seeds.get(seed,dict(game_seed=seed+1,roster=rosters[index%len(rosters)],reuse_arm=None))
               for index,seed in enumerate(seed_pool)}
    records = load(games['csc']/'packages.json')
    ce, = [(Path(path), item) for path, item in records.items() if str(Path('Binaries/Win64')/DLL) in item['files']]
    csc, = [(Path(path), item) for path, item in records.items() if Path(path) != ce[0]]
    cl, = load(games['combined']/'extra-mods.json').values()
    installed = {'csc': Path(csc[1]['install']), 'ce': Path(ce[1]['install']), 'cl': Path(cl['path'])}
    pins = {key: dict(path=str(path), id=package_identity(path)[0], files=development_package_files(path))
            for key, path in installed.items()}
    adapter = read(installed['csc']/ADAPTER)
    require(all(re.search(r'^E\.'+flag+r'=true\s*$', adapter, re.MULTILINE)
                for flag in ('AnchoredConnectionsEnabled', 'ProspectiveConnectionsEnabled')),
            'Installed CSC is missing its qualified default policy')
    binary = Path(load(games['csc']/'launch-bootstrap.json')['binary'])
    exe, core = native_profile(binary)
    saves = Path(load(games['csc']/'checkpoint.json')['native_save']).parent
    userdata = Path(load(games['csc']/'resource-stack-preflight.json')['database']).parent.parent
    return dict(seeds=seeds, packages=pins, binary=str(binary), executable_sha256=exe, core_sha256=core,
                saves=str(saves), userdata=str(userdata), configuration='Small Continents, Online, Prince, Gathering Storm',
                turns=TURNS, arms=ARMS)


def verify_pins(p):
    require(native_profile(Path(p['binary'])) == (p['executable_sha256'], p['core_sha256']), 'DX11 executable changed')
    for key, item in p['packages'].items():
        require(development_package_files(Path(item['path'])) == item['files'], f'Installed {key} build changed')


def select_stack(session, out, enabled):
    c = session.controller
    previous = flags(c, 'original-economy-benchmark-preferences')
    write_json(out/'original-preferences.json', previous)
    code = 'local keep='+lua({key: True for key in enabled})+'''
local disable={}
for _,mod in ipairs(Modding.GetInstalledMods()) do
    if mod.Source=='Mod' and not mod.Official and mod.Enabled and not keep[mod.Id] then
        disable[#disable+1]=mod.Handle
    end
end
if #disable>0 then Modding.DisableMod(disable) end
'''
    session.issue_once('disable-other-content', code, 'MainMenu')
    session.wait_context('MainMenu', 90)
    for identity in enabled:
        if not flags(c, 'before-enable-'+identity)['mods'].get(identity):
            enable(session, identity)
    actual = flags(c, 'verify-economy-benchmark-stack')
    require({key for key, status in actual['mods'].items() if status} == set(enabled), 'Unexpected active packages')
    write_json(out/'native-menu-configuration.json', dict(verified=True, enabled_mod_ids=enabled))


def host_roster(seed, game):
    leaders = lua({int(seat): name for seat, name in game['roster'].items()})
    fixed = f'local leaders={leaders}\nfor seat=0,{len(game["roster"])-1} do PlayerConfigurations[seat]:SetLeaderTypeName(leaders[seat]) end\n'
    return host(seed, game['game_seed'], 'Continents', game.get('size','small'),speed=game.get('speed','online')).replace(
        'ReleasePlayerParameters()', fixed+'ReleasePlayerParameters()')


def read_opening(c, out, roster, *, csc, cl, speed='online'):
    code = f'local csc={lua(csc)};local cl={lua(cl)};local expectedSpeed={lua("GAMESPEED_"+speed.upper())}\n'+'''
assert(Game.GetCurrentGameTurn()==1 and Players[0]:IsHuman())
assert((GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER~=nil)==csc)
assert((GameInfo.Districts.DISTRICT_RURALCOMMUNITYA~=nil)==cl)
assert((type(CE_AIDistrictScoresStatus)=='function')==csc)
local speed=GameConfiguration.GetGameSpeedType()
assert(speed==expectedSpeed or GameInfo.GameSpeeds[speed].GameSpeedType==expectedSpeed)
local facts={}
for i=0,Map.GetPlotCount()-1 do
    local plot=Map.GetPlotByIndex(i)
    facts[#facts+1]=table.concat({plot:GetTerrainType(),plot:GetFeatureType(),plot:GetResourceType(),
        plot:GetResourceCount(),plot:GetRiverCrossingCount(),plot:IsHills() and 1 or 0},',')
end
local width,height=Map.GetGridSize()
print('CSC_FACTOR_MAP=['..table.concat({width,height,DB.MakeHash(table.concat(facts,';'))},',')..']')
for _,player in ipairs(PlayerManager.GetAliveMajors()) do
    local seat=player:GetID();local plot=assert(player:GetStartingPlot())
    print('CSC_FACTOR_START',seat,PlayerConfigurations[seat]:GetLeaderTypeName(),plot:GetIndex(),player:IsHuman())
end
'''
    raw = c.cmd(code, 'GameCore_Tuner', 'verify-economy-opening')
    starts = [dict(player=int(i), leader=name, plot=int(plot), human=human=='true')
              for i, name, plot, human in re.findall(r'CSC_FACTOR_START\s+(\d+)\s+(\w+)\s+(\d+)\s+(\w+)', raw)]
    require({row['player']:row['leader'] for row in starts} == {int(i): name for i,name in roster.items()}
            and {row['player'] for row in starts if row['human']} == {0}, 'Opening roster differs')
    write_json(out/'source.json',dict(starts=sorted(starts,key=lambda row:row['player']),
        original_ai=list(range(1,len(roster))),map_signature=parse(raw,'CSC_FACTOR_MAP')))
    return True


def verify_endpoint(out, path, seats=range(1,6), turns=TURNS):
    require(path.is_file() and all((out/f'full-census-{t}.json').is_file() for t in turns), 'Missing save or economy checkpoint')
    for t in turns:
        summary, players = economy(out/f'full-census-{t}.json')
        require(set(players) <= set(map(str,seats)) and all(math.isfinite(summary[k]) for k in METRICS),
                f'Invalid AI economy scope at turn {t}')


def play(p, seed, game, arm, out, recovery=None, *, guidance=None, shortlist=False):
    verify_pins(p)
    out.mkdir()
    saves,user = Path(p['saves']),Path(p['userdata'])
    seats=range(1,len(game['roster']))
    endpoint=game.get('endpoint',250)
    turns=tuple(range(25,endpoint+1,25))
    enabled = [p['packages'][name]['id'] for name in ARMS[arm]]
    write_json(out/'protocol.json', dict(seed=seed, arm=arm, expected=game, packages=enabled, turns=turns,endpoint=endpoint,
        map='Continents',size=game.get('size','small'),speed=game.get('speed','online'),difficulty='prince',guidance=guidance))
    c=make_probe_controller(out,user_root=user)
    c.study_endpoint=endpoint
    c.observer_warning_senders=seats
    c.autoplay_interval_seconds=2700
    c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=True
    c.allow_observer_congress_review=c.allow_one_more_turn=True
    session=NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    checkpoint = None
    try:
        session.start(lambda: launch(SimpleNamespace(binary=Path(p['binary'])),out))
        session.wait_context('MainMenu')
        if recovery and (recovery/'original-preferences.json').is_file() and not (recovery/'preferences-restored.json').is_file():
            restore_preferences(c,recovery)
        select_stack(session,out,enabled)
        session.issue_once('host-economy-benchmark',host_roster(seed,game),'MainMenu')
        active = ARMS[arm]
        session.ready_after_issue(1, ('GameCore_Tuner','PlotInfo'), eligibility=lambda: read_opening(
            c,out,game['roster'],csc='csc' in active,cl='cl' in active,speed=game.get('speed','online')))
        fork = Path(p['packages']['ce']['path'])/'Binaries/Win64'/DLL if 'ce' in active else None
        verify_modules(session,fork,out,p['core_sha256'])
        if 'csc' in active and guidance is not False:
            raw=c.cmd('assert(CSC_AI_EconomyAdapters.AnchoredConnectionsEnabled and CSC_AI_EconomyAdapters.ProspectiveConnectionsEnabled);print("CSC_FACTOR_DEFAULT_ON")',
                      'CSC_AI_BakersGameplay','verify-normal-csc-default')
            require('CSC_FACTOR_DEFAULT_ON' in raw,'CSC default was not enabled')
        if guidance is not None:
            from economy_guidance_timing import install_clocks, verify_guidance
            verify_guidance(c,user,out,guidance,'opening')
            install_clocks(c)
        if shortlist:
            require(guidance is True,'Shortlist observation needs the normal guided planner')
            study=HERE/'shortlist_observer.lua'
            raw=c.cmd(read(study),'CSC_AI_BakersGameplay','install-read-only-shortlist-study')
            require('CSC_SHORTLIST_READY' in raw,'Shortlist observer did not load')
            write_json(out/'shortlist.json',dict(observer_sha256=sha(study),first_turn=2,
                        retained_leaders=2,rotation=1,refresh=8,live_policy='full'))
        observer=read(HERE/'economy_factorial_census.lua').replace('__SEATS__',lua(list(seats))).replace(
            'local maximum = 250',f'local maximum = {endpoint}')
        raw=c.cmd(observer,'GameCore_Tuner','install-passive-economy-snapshots')
        require('CSC_FACTOR_ECONOMY_INSTALLED' in raw,'Economic census did not install')
        # The controller's passive popup recovery is scoped to five-turn
        # windows. The Lua snapshots still share the fixed 25-turn clock.
        for turn in range(5,endpoint+1,5):
            c.play(turn)
            if shortlist and turn==5:
                raw=c.cmd("assert(CSC_AI_EconomyAdapters.ShortlistObserver.passes>0);print('CSC_SHORTLIST_ACTIVE')",
                          'CSC_AI_BakersGameplay','verify-shortlist-observation')
                require('CSC_SHORTLIST_ACTIVE' in raw,'Shortlist diagnostic did not reach the player boundaries')
        if guidance is not None:
            verify_guidance(c,user,out,guidance,'endpoint')
        name=(f'CSC_ECONOMY_{seed}_{arm.upper()}' if guidance is None else f'CSC_GUIDANCE_{seed}_{"ON" if guidance else "OFF"}')+f'_T{endpoint}'
        try:
            checkpoint=save_inactive_boundary(c,turn=endpoint,name=name,native_directory=saves,archive=out/'endpoint.Civ6Save')
        except (SavePermissionUnavailable, SaveFileUnavailable) as error:
            receipt=archive_endpoint_autosave(out,saves,endpoint,error)
            archive=Path(receipt['archive'])
            native=saves/(f'{name}_{receipt["sha256"][:12]}.Civ6Save')
            with native.open('xb') as stream, archive.open('rb') as source:
                shutil.copyfileobj(source,stream)
            checkpoint=dict(verified=True,turn=endpoint,native_save=str(native),archive=str(archive),sha256=receipt['sha256'])
        write_json(out/'checkpoint.json',checkpoint)
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(c,out) if (out/'original-preferences.json').is_file() else None,
                          restore_package=lambda: verify_pins(p),
                          # A Large game can take several minutes to unload at
                          # turn 500. Continue observing the one exit request.
                          menu_timeout=600 if endpoint==500 else 180)
        elif session.owner is not None:
            write_json(out/'unexpected-native-exit.json',dict(exit_code=session.owner.poll(),identity=session.owner.identity))
            session.owner.close()
    require(session.closed and checkpoint is not None,'Endpoint session did not complete')
    native,archive=(Path(checkpoint[key]) for key in ('native_save','archive'))
    require(sha(native)==sha(archive)==checkpoint['sha256'],'Endpoint save hash differs')
    log=read(user/'Logs/Lua.log')
    if guidance is not None:
        (out/'Lua.log').write_text(log,encoding='utf-8')
    require('CSC_FACTOR_ECONOMY_FAILED' not in log,'Economy census fault')
    require(set(archive_censuses(log,out)) == set(turns),'Missing or duplicate economy checkpoints')
    verify_endpoint(out,native,seats,turns)
    return dict(evidence=str(out),save=str(native),reused=False)


def existing(p, seed, game, arm):
    if arm != game['reuse_arm']:
        return None
    source=Path(game['reference'])
    old=load(source/'protocol.json')
    switch=load(source/'paired-layout-opening.json')
    if not (old['fresh_game'] and old['ordinary_setup'] and old['endpoint']==250
            and (old['map_seed'],old['game_seed'])==(seed,game['game_seed'])
            and switch['turn']==1 and switch['policy']=='on' and switch['anchored'] and switch['acknowledged']
            and switch['opening']['entries']==0 and switch['opening']['faults']==0
            and load(source/'session-closed.json')['verified']
            and load(source/'full-game-observation-complete.json')['verified']):
        return None
    roster={row['player']:row['leader'] for row in load(source/'source.json')['starts']}
    if roster!={int(i):name for i,name in game['roster'].items()}:
        return None
    packages=load(source/'packages.json')
    for key in ('ce','csc'):
        current=p['packages'][key]
        path,= [Path(path) for path,item in packages.items() if item['install']==current['path']]
        files=packages[str(path)]['files']
        if files!=development_package_files(path):
            return None
        if files==current['files']:
            continue
        if key!='csc' or files.keys()!=current['files'].keys() or {Path(k).as_posix() for k in files
                if files[k]!=current['files'][k]}!={ADAPTER.as_posix()}:
            return None
        # The turn-one switch exercised the current policy before any bid.
        # Accept the frozen predecessor only when the source delta is exactly
        # those two default flags and top-level explanatory comments.
        def policy(adapter):
            return [line for line in read(adapter).splitlines() if not line.startswith('--')]
        adapted=[line.replace('ConnectionsEnabled=false','ConnectionsEnabled=true')
                 if line in ('E.AnchoredConnectionsEnabled=false','E.ProspectiveConnectionsEnabled=false') else line
                 for line in policy(path/ADAPTER)]
        if adapted!=policy(Path(current['path'])/ADAPTER):
            return None
    extras=load(source/'extra-mods.json')
    cl=p['packages']['cl']
    if (arm=='combined' and extras!={cl['id']:dict(path=cl['path'],files=cl['files'])}) or (arm=='csc' and extras):
        return None
    modules=load(source/'loaded-modules.json')
    if (modules['GameCore_XP2_FinalRelease.dll']['sha256']!=p['core_sha256'] or
            modules[DLL]['sha256']!=p['packages']['ce']['files'][str(Path('Binaries/Win64')/DLL)]['sha256']):
        return None
    try:
        save=Path(loadable_layout_endpoint(source,seed,'treatment'))
        verify_endpoint(source,save)
    except (OSError, ValueError, AssertionError, RuntimeError):
        return None
    return dict(evidence=str(source),save=str(save),reused=True,
                qualification='same code, data and binaries with the shipped policy established before first bidding')


def compare(result, seeds):
    report={}
    for seed, games in result.items():
        require(set(games)==set(ARMS),'Missing matched arm')
        roster=seeds[str(seed)]['roster']
        seats=[str(i) for i in range(1,6)]
        economy_rows={}
        for arm, record in games.items():
            folder=Path(record['evidence'])
            readouts={t:economy(folder/f'full-census-{t}.json') for t in TURNS}
            economy_rows[arm]={
                'turn250': {key:readouts[250][0][key] for key in METRICS},
                'sample_average': {key:mean(row[0][key] for row in readouts.values()) for key in METRICS},
                'by_seat': {seat:{'leader':roster[seat],
                    'turn250':{key:readouts[250][1].get(seat,{}).get(key,0) for key in METRICS},
                    'sample_average':{key:mean(row[1].get(seat,{}).get(key,0) for row in readouts.values()) for key in METRICS}}
                    for seat in seats},
                'by_turn': {t:{key:row[0][key] for key in METRICS} for t,row in readouts.items()},
                **record}
        deltas={}
        for measure in ('turn250','sample_average'):
            deltas[measure]={}
            for metric in METRICS:
                values={arm:row[measure][metric] for arm,row in economy_rows.items()}
                effects={arm:values[arm]-values['vanilla'] for arm in ARMS if arm!='vanilla'}
                effects['combined_beyond_sum']=effects['combined']-effects['csc']-effects['city-lights']
                for arm,effect in effects.items():
                    by_seat={}
                    for seat in seats:
                        v={name:row['by_seat'][seat][measure][metric] for name,row in economy_rows.items()}
                        by_seat[seat]=(v['combined']-v['csc']-v['city-lights']+v['vanilla']
                                       if arm=='combined_beyond_sum' else v[arm]-v['vanilla'])
                    total=sum(abs(value) for value in by_seat.values())
                    leader=max(seats,key=lambda seat:abs(by_seat[seat]))
                    share=abs(by_seat[leader])/total if total else 0
                    entry=dict(value=effect, by_seat=by_seat)
                    if share>.5:
                        entry.update(major_driver=roster[leader], share_of_absolute_changes=share)
                    deltas[measure].setdefault(arm,{})[metric]=entry
        report[seed]=dict(economy=economy_rows,deltas=deltas)
    return report


def batch(reference, out, *, preflight=False, resume=False, seed_pool=(), matched_seeds=None, carry=None):
    proposed=plan(reference,seed_pool)
    requested=matched_seeds or len(proposed['seeds'])
    require(1<=requested<=len(proposed['seeds']),'Invalid number of matched seeds')
    if seed_pool:
        # The completion count and fallback order are fixed before any of the
        # added games run. A failed observer invalidates the seed as a group.
        proposed['matched_seeds']=requested
    if preflight:
        for seed,game in proposed['seeds'].items():
            reused=existing(proposed,seed,game,game['reuse_arm']) if game['reuse_arm'] else None
            print(seed,game['game_seed'],game['reuse_arm'], 'verified reusable' if reused else 'fresh run needed')
        return
    require(not native_inventory(),'Another native or FireTuner session owns the game')
    if not resume:
        out.mkdir(parents=True)
        write_json(out/'planned-inputs.json',proposed)
    # The on-disk plan fixes both seeds and the content digests before turn one.
    p=load(out/'planned-inputs.json')
    require(p==load_plan(proposed),'Resume inputs differ from the preselected plan')
    completed=out/'completed-runs.json'
    rejected_path=out/'ineligible-seeds.json'
    results=load(completed) if resume and completed.is_file() else {}
    rejected=load(rejected_path) if resume and rejected_path.is_file() else {}
    if carry and not resume:
        old=load(carry/'planned-inputs.json')
        require(all(old[key]==p[key] for key in ('packages','configuration','executable_sha256','core_sha256','turns','arms')),
                'Earlier games have a different benchmark input')
        results={seed:games for seed,games in load(carry/'completed-runs.json').items() if seed in p['seeds']
                 and len(games)==len(ARMS) and p['seeds'][seed]==old['seeds'][seed]}
        write_json(completed,results)
        write_json(out/'carry-receipt.json',dict(source=str(carry),verified_seeds=list(results)))
    finished={}
    for seed, game in p['seeds'].items():
        if seed in rejected:
            continue
        previous=results.setdefault(seed,{})
        for arm in ARMS:
            verify_pins(p)
            if arm in previous:
                record=previous[arm]
                source,native=Path(record['evidence']),Path(record['save'])
                saved=load(source/'checkpoint.json')
                require(sha(native)==saved['sha256']==sha(Path(saved['archive'])),'Previously accepted save changed')
                verify_endpoint(source,native)
                continue
            value=existing(p,int(seed),game,arm)
            if value is None:
                label=f'{seed}-{arm}'
                old=sorted((d for d in out.iterdir() if d.is_dir() and
                            (d.name==label or d.name.startswith(label+'-'))),key=lambda d:d.stat().st_mtime_ns)
                recovery=old[-1] if old else None
                for attempt in range(2):
                    directory=out/(label if not old else f'{label}-attempt-{len(old)+1}')
                    try:
                        value=play(p,int(seed),game,arm,directory,recovery=recovery)
                        break
                    except ObserverEliminated as error:
                        write_json(directory/'failure.json',dict(reason=str(error),type=type(error).__name__))
                        if not seed_pool:
                            raise
                        require(load(directory/'session-closed.json')['verified'] and not native_inventory(),
                                'Elimination cleanup did not complete')
                        rejected[seed]=dict(arm=arm,attempt=str(directory),reason=str(error))
                        write_json(rejected_path,rejected)
                        print(f'{seed} {arm} lost its observer; using the next preselected seed',flush=True)
                        value=None
                        break
                    except (OSError,RuntimeError,AssertionError,ValueError) as error:
                        write_json(directory/'failure.json',dict(reason=str(error),type=type(error).__name__))
                        if attempt or native_inventory():
                            raise
                        old.append(directory)
                        recovery=directory
            if value is None:
                break
            results[seed][arm]=value
            write_json(completed,results)
            print(f'{seed} {arm} verified'+(' (reused)' if value['reused'] else ''),flush=True)
        if len(previous)==len(ARMS):
            finished[seed]=previous
            if len(finished)==requested:
                break
    require(len(finished)==requested,'Preselected seed pool exhausted before the required matched endpoints')
    write_json(out/'comparison.json',compare(finished,p['seeds']))
    print(f'All {requested*len(ARMS)} matched endpoints verified',flush=True)


def load_plan(plan):
    """Use the same JSON shapes when comparing live inputs with the saved plan."""
    import json
    return json.loads(json.dumps(plan))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--preflight',action='store_true')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--seed-pool',nargs='+',type=int,default=())
    parser.add_argument('--matched-seeds',type=int)
    parser.add_argument('--carry',type=Path)
    parser.add_argument('--shortlist-seed',type=int,help='Run one guided CSC + City Lights game with passive Quarter shortlist observation')
    args=parser.parse_args()
    if args.shortlist_seed is not None:
        if args.resume or args.preflight or args.seed_pool or args.matched_seeds or args.carry:
            parser.error('The shortlist study runs one fresh game and takes its own seed')
        pins=plan(args.reference.resolve(),[args.shortlist_seed])
        require(not native_inventory(),'Another session owns the game')
        out=args.output.resolve()
        out.mkdir(parents=True)
        write_json(out/'planned-inputs.json',pins)
        play(pins,args.shortlist_seed,pins['seeds'][args.shortlist_seed],'combined',out/'full',
             guidance=True,shortlist=True)
    else:
        batch(args.reference.resolve(),args.output.resolve(),preflight=args.preflight,resume=args.resume,
              seed_pool=args.seed_pool,matched_seeds=args.matched_seeds,carry=args.carry.resolve() if args.carry else None)
