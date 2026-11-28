"""Compare physical CSC chains, active Service links and elapsed turn time on one seed."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from statistics import mean

from full_game_results import economy, quarter_rows, summarize


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def supplier_tile_state(row):
    """Physical state after a loss; the boundary observer cannot name a Builder operation."""
    if int(row['ownerAfter']) != int(row['player']):
        return 'ownership_changed'
    if int(row['district']) >= 0:
        return 'district_on_tile'
    if row['resourceAfter'] != row['resource']:
        return 'resource_changed_or_removed'
    if row['pillaged'] == 'true':
        return 'improvement_pillaged'
    if int(row['improvementAfter']) < 0:
        return 'resource_still_there_without_improvement'
    return 'resource_and_improvement_still_there'


def read_arm(folder, through=None):
    protocol = load(folder/'protocol.json')
    turn = protocol['turn'] if through is None else through
    if not 0 < turn <= protocol['turn']:
        raise ValueError(f'Comparison turn {turn} outside the run window')
    census = folder/f'full-census-{turn}.json'
    endpoint = summarize(census)
    result = {}
    profiles = {}
    for path in sorted(folder.glob('full-census-*.json')):
        if int(path.stem.rsplit('-',1)[1]) > turn:
            continue
        for quarter in quarter_rows(path):
            profiles[quarter['plot']] = quarter['profile']
    for profile, totals in endpoint.items():
        complete = totals['complete']
        supplied = totals['base_improved_customer_any']
        result[profile] = dict(complete=complete, working_base_and_customer=supplied,
            share=supplied/complete if complete else None, no_base=complete-totals['base'],
            working_base=totals['base_improved'], both_materials=totals['both'],
            mapped_customer=totals['customer_any_completed'],
            stage2_producer=totals['producer2_working'],
            stage2_customer_district=totals['mapped_customer2_completed'],
            stage2_customer_building=totals['mapped_customer2_with_working_building'],
            supplied_stage2_customer_building=totals['base_improved_customer2_working'],
            stage2_chain_physical=totals['stage2_physical'])

    intervals = {}
    links = defaultdict(set)
    losses = defaultdict(set)
    loss_states = {'working': defaultdict(set), 'deposit': defaultdict(set)}
    district_types = {}
    covering_districts = defaultdict(set)
    harvest_turn = {}
    harvested_losses = set()
    harvest_watched = False
    poor = set()
    foundations = {}
    clear_coast = set()
    observed_terrain = set()
    active_city_rules = {}
    founder_rules = {}
    founder_terrain = defaultdict(Counter)
    city_cue_stats = Counter()
    city_cue_time = Counter()
    district_profiles = defaultdict(set)
    seats = set(load(folder/'source.json')['original_ai'])
    for line in (folder/'Lua.log').read_text(encoding='utf-8-sig',errors='replace').splitlines():
        if 'CSC_LOCAL_CUE_LUA_MICROS\t' in line:
            turn_id,micros=map(int,line.split('CSC_LOCAL_CUE_LUA_MICROS\t',1)[1].split())
            if turn_id <= turn:
                city_cue_time[turn_id] += micros
        elif 'CSC_LOCAL_CUE_REVIEW\t' in line:
            stamp,_,_,evaluated,matched = line.split('CSC_LOCAL_CUE_REVIEW\t',1)[1].split()
            if int(stamp) > turn:
                continue
            city_cue_stats['city_reviews'] += 1
            city_cue_stats['legal_sites_evaluated'] += int(evaluated)
            city_cue_stats['quarter_reviews_with_signal'] += int(matched)
        elif 'CSC_LOCAL_CUE_CHANGE\t' in line:
            stamp,pid,cid,quarter,_,rule,_,_,_ = line.split('CSC_LOCAL_CUE_CHANGE\t',1)[1].split()
            if int(stamp) > turn:
                continue
            key = (int(pid),int(cid),quarter)
            if rule == '-':
                active_city_rules.pop(key,None)
                city_cue_stats['withdrawals'] += 1
            else:
                # Modifier names end in the exact terrain and integer cutoff.
                terrain,cutoff = rule.rsplit('__',1)[1].rsplit('_',1)
                active_city_rules[key] = terrain,int(cutoff)
                city_cue_stats['activations'] += 1
        elif 'CSC_MILESTONE_SERVICE_END\t' in line:
            t, count, unknown = map(int,line.split('CSC_MILESTONE_SERVICE_END\t',1)[1].split())
            if t > turn:
                continue
            if t in intervals:
                raise ValueError(f'Duplicate Service sample on turn {t}')
            intervals[t] = (count,unknown)
        elif 'CSC_MILESTONE_SERVICE_LINK\t' in line:
            t, player, quarter, stage, service, producer, customer = line.split('CSC_MILESTONE_SERVICE_LINK\t',1)[1].split()
            if int(t) <= turn:
                links[int(t)].add((int(player),quarter,stage,service,producer,customer))
        elif 'CSC_QUARTER_WATCH_' in line:
            event, _, tail = line.split('CSC_QUARTER_WATCH_',1)[1].partition('\t')
            if event == 'DISTRICT_INDEX':
                fields = dict(v.split('=',1) for v in tail.split('\t') if '=' in v)
                district_types[int(fields['index'])] = fields['districtType']
                continue
            if event == 'HARVEST_OBSERVER':
                harvest_watched = True
                continue
            if event not in ('SITE','NEIGHBOR','SUPPLIER_LOSS','HARVEST'):
                continue
            row = dict(field.split('=',1) for field in tail.split('\t') if '=' in field)
            if int(row['turn']) > turn:
                continue
            if event == 'NEIGHBOR':
                # A featureless, resourceless coast tile beside the Quarter
                # leaves a possible Harbor footprint. Ownership and a city's
                # remaining district slots still govern actual construction.
                if row['event'] == 'foundation' and 'terrain' in row and 'feature' in row:
                    site = (int(row['plot']),int(row['turn']))
                    observed_terrain.add(site)
                    if site in founder_rules:
                        founder_terrain[site][row['terrain']] += 1
                    if (row['terrain'] == 'TERRAIN_COAST' and row['resource'] == '-'
                            and row['feature'] == '-' and int(row['district']) < 0):
                        clear_coast.add(site)
                continue
            player = int(row['player'])
            if player not in seats:
                continue
            if event == 'HARVEST':
                harvest_watched = True
                harvest_turn[player,int(row['plot'])] = int(row['turn'])
            if event == 'SITE':
                # Older receipts have the native district index only. Recover
                # its name from this game's censused plots; newer receipts
                # carry the type directly, even for a subsequently razed city.
                profile = profiles.get(int(row['plot']))
                if row.get('quarterType'):
                    profile = row['quarterType'].removeprefix('DISTRICT_CSC_').removesuffix('_QUARTER')
                if profile:
                    district_profiles[row['district']].add(profile)
                if row['event'] == 'foundation':
                    key = (player,int(row['plot']),int(row['turn']))
                    foundations[key] = row
                    rule = active_city_rules.get((player,int(row['city']),row.get('quarterType')))
                    if rule:
                        founder_rules[key[1:]] = rule
                    if int(row['base']) == 0:
                        poor.add(key)
            if event == 'SUPPLIER_LOSS':
                key = (player,int(row['quarter']),row['class'],int(row['turn']))
                if row['lastWorking'] == 'true':
                    losses['working'].add(key)
                    loss_states['working'][key].add(supplier_tile_state(row))
                    if int(row['district']) >= 0:
                        losses['working_district_covered'].add(key)
                if row['lastDeposit'] == 'true':
                    losses['deposit'].add(key)
                    state = supplier_tile_state(row)
                    loss_states['deposit'][key].add(state)
                    if int(row['district']) >= 0:
                        covering_districts[key].add(int(row['district']))
                    # Log order excludes later actions on the same turn.
                    latest = harvest_turn.get((player,int(row['supplier'])))
                    if state == 'resource_changed_or_removed' and latest in (key[-1]-1,key[-1]):
                        harvested_losses.add(key)
    for t,(count,_) in intervals.items():
        if count != len(links[t]):
            raise ValueError(f'Active link count disagrees with receipts at turn {t}')
    # An early smoke game predated the loss watcher. Zero needs a registered
    # observer, even if no Quarter was built before that game's endpoint.
    receipt = next((folder/'pending-commands').glob('*observe-foundations.lua'),None)
    observer = receipt.read_text(encoding='utf-8-sig') if receipt else ''
    watched = 'local CSC_OBSERVE_SUPPLIER_LOSS=' in observer
    if through is None:
        measured=load(folder/'measured.json')
        timing = {int(k):v for k,v in measured['clean'].items()}
        processing = measured['direct']
    else:
        # A defeated observer can end an otherwise healthy game. Use the same
        # physical census and clock window for every arm, including completed
        # games. Recalculate the publisher times inside that window too.
        from economy_guidance_timing import observed_turns
        timing,_,guidance = observed_turns(folder,turn,2)
        processing = guidance['publisher_wall']
    placement = {}
    for row in foundations.values():
        names = district_profiles[row['district']]
        profile = next(iter(names)) if len(names)==1 else 'unresolved'
        stats = placement.setdefault(profile, dict(founded=0,owned_base=0,working_base=0,
            owned_spec=0,both_materials=0,current_adjacency_3plus=0,coast_surveyed_foundations=0,clear_coast_neighbor=0,
            owned_base_and_clear_coast_neighbor=0))
        base,spec = int(row['base'])>0,int(row['spec'])>0
        stats['founded'] += 1
        stats['owned_base'] += base
        stats['working_base'] += int(row['baseWorking'])>0
        stats['owned_spec'] += spec
        stats['both_materials'] += base and spec
        site = (int(row['plot']),int(row['turn']))
        stats['coast_surveyed_foundations'] += site in observed_terrain
        coastal = site in clear_coast
        stats['clear_coast_neighbor'] += coastal
        stats['owned_base_and_clear_coast_neighbor'] += base and coastal
        if site in founder_rules:
            terrain,cutoff = founder_rules[site]
            city_cue_stats[profile+'_foundations_with_active_rule'] += 1
            if founder_terrain[site][terrain] >= cutoff:
                city_cue_stats[profile+'_foundations_on_rewarded_terrain'] += 1
                city_cue_stats[profile+'_rewarded_foundations_with_usable_base'] += base
        stats['current_adjacency_3plus'] += float(row['eligibleGold'])+float(row['eligibleProduction'])>=3
    for stats in placement.values():
        if not stats['coast_surveyed_foundations']:
            stats['clear_coast_neighbor'] = None
            stats['owned_base_and_clear_coast_neighbor'] = None
    if city_cue_time:
        city_cue_stats['lua_clock_turns'] = len(city_cue_time)
        city_cue_stats['mean_lua_clock_ms'] = mean(city_cue_time.values()) / 1000
        city_cue_stats['max_lua_clock_ms'] = max(city_cue_time.values()) / 1000
    # The last two suppliers can disappear together. Preserve both states on
    # that single Quarter loss rather than crediting it to either tile alone.
    state_counts = {}
    for kind, events in loss_states.items():
        counts = defaultdict(int)
        for states in events.values():
            counts[' + '.join(sorted(states))] += 1
        state_counts[kind] = dict(sorted(counts.items()))
    report = dict(quarters=result, economy=economy(census)[0], founded=len(foundations),
        placement_by_quarter=placement,local_material_guidance=dict(city_cue_stats) if protocol.get('local_material_cues') else None,
        no_usable_owned_base_at_foundation=len(poor), endpoint_turn=turn, start_save=protocol['shared_save'],
        last_supplier_losses={k:len(losses[k]) for k in ('working','working_district_covered','deposit')} if watched else None,
        supplier_tile_states_after_loss=state_counts if watched else None,
        district_types_covering_last_deposit=dict(Counter(
            ' + '.join(sorted(district_types[i] for i in indices)) for indices in covering_districts.values()
        )) if watched and district_types else None,
        deposit_losses_with_matching_harvest=len(harvested_losses) if watched and harvest_watched else None,
        losses_by_quarter={k:sum(profiles.get(x[1])==k for x in losses['working']) for k in result} if watched else None,
        unresolved_service_samples=sum(unknown for _,unknown in intervals.values()),
        planner_processing={k:processing[k] for k in ('turns','average_ms','max_ms')})
    return report, intervals, links, timing


def compare(folders, through=None):
    if len({folder.name for folder in folders}) != len(folders):
        raise ValueError('Use one folder per named arm on the same seed')
    opening=load(folders[0]/'source.json')
    for folder in folders[1:]:
        if opening != load(folder/'source.json'):
            raise ValueError('Opening map, roster or starting sites differ')
    arms = {folder.name:read_arm(folder, through) for folder in folders}
    if len({arm[0]['endpoint_turn'] for arm in arms.values()}) != 1:
        raise ValueError('Endpoint turns differ')
    sample = set.intersection(*(set(intervals) for _,intervals,_,_ in arms.values()))
    turns = set.intersection(*(set(timing) for _,_,_,timing in arms.values()))
    if not sample or not turns:
        raise ValueError('No comparable Service or timing observations')
    for report,_,links,timing in arms.values():
        contacts = defaultdict(set)
        active = defaultdict(int)
        for turn in sample:
            for identity in links[turn]:
                service = identity[3]
                contacts[service].add(identity)
                active[service] += 1
        report['services'] = {s:dict(chains=len(c),active_chain_turns=active[s]) for s,c in sorted(contacts.items())}
        report['active_chain_turns'] = sum(active.values())
        peak = max(sorted(turns),key=timing.get)
        report['turn_seconds'] = dict(mean=mean(timing[t] for t in turns),maximum=timing[peak],max_turn=peak)
    return dict(common_service_samples=len(sample), common_popup_free_turns=len(turns),
        arms={name:data[0] for name,data in arms.items()})


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('arms',type=Path,nargs='+')
    parser.add_argument('--through',type=int,help='Use the same recorded census turn in every arm')
    args=parser.parse_args()
    print(json.dumps(compare(args.arms,args.through),indent=2))
