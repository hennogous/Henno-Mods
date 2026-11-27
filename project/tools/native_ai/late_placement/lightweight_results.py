"""Compare physical CSC chains, active Service links and elapsed turn time on one seed."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import mean

from full_game_results import economy, quarter_rows, summarize


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def read_arm(folder):
    protocol = load(folder/'protocol.json')
    turn = protocol['turn']
    census = folder/f'full-census-{turn}.json'
    endpoint = summarize(census)
    result = {}
    profiles = {}
    for path in sorted(folder.glob('full-census-*.json')):
        for quarter in quarter_rows(path):
            profiles[quarter['plot']] = quarter['profile']
    for profile, totals in endpoint.items():
        complete = totals['complete']
        supplied = totals['base_improved_customer_any']
        result[profile] = dict(complete=complete, working_base_and_customer=supplied,
            share=supplied/complete if complete else None, no_base=complete-totals['base'],
            working_base=totals['base_improved'], both_materials=totals['both'],
            mapped_customer=totals['customer_any_completed'])

    intervals = {}
    links = defaultdict(set)
    losses = defaultdict(set)
    poor = set()
    foundations = set()
    seats = set(load(folder/'source.json')['original_ai'])
    for line in (folder/'Lua.log').read_text(encoding='utf-8-sig',errors='replace').splitlines():
        if 'CSC_MILESTONE_SERVICE_END\t' in line:
            t, count, unknown = map(int,line.split('CSC_MILESTONE_SERVICE_END\t',1)[1].split())
            if t in intervals:
                raise ValueError(f'Duplicate Service sample on turn {t}')
            intervals[t] = (count,unknown)
        elif 'CSC_MILESTONE_SERVICE_LINK\t' in line:
            t, player, quarter, stage, service, producer, customer = line.split('CSC_MILESTONE_SERVICE_LINK\t',1)[1].split()
            links[int(t)].add((int(player),quarter,stage,service,producer,customer))
        elif 'CSC_QUARTER_WATCH_' in line:
            event, _, tail = line.split('CSC_QUARTER_WATCH_',1)[1].partition('\t')
            if event not in ('SITE','SUPPLIER_LOSS'):
                continue
            row = dict(field.split('=',1) for field in tail.split('\t') if '=' in field)
            player = int(row['player'])
            if player not in seats:
                continue
            if event == 'SITE' and row['event'] == 'foundation':
                key = (player,int(row['plot']),int(row['turn']))
                foundations.add(key)
                if int(row['base']) == 0:
                    poor.add(key)
            if event == 'SUPPLIER_LOSS':
                key = (player,int(row['quarter']),row['class'],int(row['turn']))
                if row['lastWorking'] == 'true':
                    losses['working'].add(key)
                    if int(row['district']) >= 0:
                        losses['working_district_covered'].add(key)
                if row['lastDeposit'] == 'true':
                    losses['deposit'].add(key)
    for t,(count,_) in intervals.items():
        if count != len(links[t]):
            raise ValueError(f'Active link count disagrees with receipts at turn {t}')
    # An early smoke game predated the loss watcher. Zero needs a registered
    # observer, even if no Quarter was built before that game's endpoint.
    receipt = next((folder/'pending-commands').glob('*observe-foundations.lua'),None)
    watched = receipt is not None and 'local CSC_OBSERVE_SUPPLIER_LOSS=' in receipt.read_text(encoding='utf-8-sig')
    timing = {int(k):v for k,v in load(folder/'measured.json')['clean'].items()}
    report = dict(quarters=result, economy=economy(census)[0], founded=len(foundations),
        no_usable_owned_base_at_foundation=len(poor), endpoint_turn=turn, start_save=protocol['shared_save'],
        last_supplier_losses={k:len(losses[k]) for k in ('working','working_district_covered','deposit')} if watched else None,
        losses_by_quarter={k:sum(profiles.get(x[1])==k for x in losses['working']) for k in result} if watched else None,
        unresolved_service_samples=sum(unknown for _,unknown in intervals.values()))
    return report, intervals, links, timing


def compare(folders):
    if len({folder.name for folder in folders}) != len(folders):
        raise ValueError('Use one folder per named arm on the same seed')
    opening=load(folders[0]/'source.json')
    for folder in folders[1:]:
        if opening != load(folder/'source.json'):
            raise ValueError('Opening map, roster or starting sites differ')
    arms = {folder.name:read_arm(folder) for folder in folders}
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
    args=parser.parse_args()
    print(json.dumps(compare(args.arms),indent=2))
