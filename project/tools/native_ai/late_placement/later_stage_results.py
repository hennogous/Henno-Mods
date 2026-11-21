"""Aggregate verified Service recipient-turns from the passive UI watcher."""
from collections import Counter, defaultdict
import re


SERVICE_LINK = re.compile(r'CSC_MILESTONE_SERVICE_LINK\t(\d+)\t(\d+)\t(\w+)\t([234])\t(\w+)\t(\d+)\t(\d+)')
SERVICE_END = re.compile(r'CSC_MILESTONE_SERVICE_END\t(\d+)\t(\d+)\t(\d+)')
UNLOCK = re.compile(r'CSC_MILESTONE_UNLOCK\t(\d+)\t(\d+)\t(tech|civic)\t(\w+)')


def stage_census(rows):
    """Count distinct physical hosts separately from their Quarter links."""
    quarters = {}
    producers = set()
    materials = set()
    customers = set()
    for kind, payload in rows:
        fields = payload.split('\t')
        if kind == 'QUARTER':
            quarter, player, _, plot, complete, pillaged, *_ = fields
            quarters[plot] = (quarter, player, complete == 'true', pillaged == 'true')
        elif kind == 'PRODUCER':
            plot, stage, building, status = fields
            producers.add((plot, int(stage), building, status == '2'))
        elif kind == 'MATERIAL':
            plot, material_plot, material_class, _, operating = fields
            materials.add((plot, material_plot, material_class, operating == 'true'))
        elif kind == 'CUSTOMER':
            plot, host, stage, district, complete, status = fields
            if status != '0':
                customers.add((plot, host, int(stage), district, complete == 'true' and status == '2'))
    result = {}
    for quarter in sorted({record[0] for record in quarters.values()}):
        built = {plot for plot, record in quarters.items() if record[0] == quarter and record[2]}
        working = {plot for plot in built if not quarters[plot][3]}
        result[quarter] = dict(quarters_built=len(built), quarters_working=len(working),
            supply={kind: dict(adjacent=sum(plot in built and c == kind for plot, _, c, _ in materials),
                              working=sum(plot in built and c == kind and active for plot, _, c, active in materials))
                    for kind in ('BASE', 'SPEC')},
            stages=[_count_stage(stage, built, working, producers, customers) for stage in (2, 3, 4)])
    return result


def _count_stage(stage, built, working, producers, customers):
    stage_producers = [(plot, active) for plot, found, _, active in producers if found == stage and plot in built]
    stage_customers = [(plot, host, district, active) for plot, host, found, district, active in customers
                       if found == stage and plot in built]
    active_producers = {plot for plot, active in stage_producers if active and plot in working}
    return dict(stage=stage, producers=len(stage_producers), working_producers=len(active_producers),
                customer_hosts=len({host for _, host, _, _ in stage_customers}),
                working_customer_hosts=len({host for _, host, _, active in stage_customers if active}),
                wonders=len({host for _, host, district, _ in stage_customers if district == 'DISTRICT_WONDER'}),
                physical_exchange_pairs=sum(plot in active_producers and active for plot, _, _, active in stage_customers))


def service_durations(log, start, end):
    if 'CSC_MILESTONE_SERVICE_FAULT' in log:
        raise ValueError('Native Service observer fault')
    snapshots = {}
    pending = defaultdict(set)
    unlocks = []
    for line in log.splitlines():
        unlock = UNLOCK.search(line)
        if unlock and start <= int(unlock[1]) < end:
            unlocks.append(dict(turn=int(unlock[1]), player=int(unlock[2]), kind=unlock[3], topic=unlock[4]))
        link = SERVICE_LINK.search(line)
        if link:
            turn, player, quarter, stage, service, source, customer = link.groups()
            pending[int(turn)].add((player, quarter, stage, service, source, customer))
        boundary = SERVICE_END.search(line)
        if boundary:
            turn, count, unreadable = map(int, boundary.groups())
            if not start <= turn < end:
                continue
            links = pending.pop(turn, set())
            if unreadable or len(links) != count or turn in snapshots:
                raise ValueError(f'Incomplete native Service observation at turn {turn}')
            snapshots[turn] = links
    turns_by_chain = defaultdict(list)
    for turn, links in sorted(snapshots.items()):
        for key in links:
            turns_by_chain[key].append(turn)
    totals = Counter()
    chains = []
    for (player, quarter, stage, service, source, customer), turns in sorted(turns_by_chain.items()):
        totals[quarter, stage] += len(turns)
        chains.append(dict(player=int(player), quarter=quarter, stage=int(stage), service=service,
                           source=int(source), customer=int(customer), first=turns[0], last=turns[-1],
                           active_turns=len(turns)))
    unlocks.sort(key=lambda row: (row['turn'], row['player'], row['kind'], row['topic']))
    return dict(observed_turns=sorted(snapshots), missing_turns=sorted(set(range(start, end)) - snapshots.keys()),
                totals=[dict(quarter=q, stage=int(s), active_link_turns=n) for (q, s), n in sorted(totals.items())],
                chains=chains, unlocked=unlocks)
