"""Compare the full-run census with the historical endpoint baseline.

The aggregation functions preserve the existing baseline definition of improved
materials (compatible, unpillaged; not necessarily worked by a citizen),
producer/customer buildings and native Service properties. A ready physical
chain, active property and independently observed Service effect stay distinct.
Same seeds with changed gameplay/CE packages are descriptive, not causal.
"""
from collections import Counter
import json
from pathlib import Path
import argparse
import re

PROFILES = ("BAKERS", "TAILORS")
DETAILS = {"MATERIAL": "materials", "PRODUCER": "producers",
           "SALES": "sales", "CUSTOMER": "customers"}


def census(path,expected_turn=None):
    source=json.loads(path.read_text(encoding='utf-8'))
    rows=source['rows'];assert rows and rows[-1][0]=='END','Incomplete census'
    turn,count=map(int,rows[-1][1].split('\t'))
    assert count==len(rows)-1,'Census row count differs'
    actual=source['phase']['turn']if isinstance(source.get('phase'),dict)else source['turn']
    assert turn==actual,'Census clock differs'
    assert expected_turn is None or turn==expected_turn,'Wrong comparison-window clock'
    return source

def summarize(path):
    source = census(path)
    quarters, services = {}, {profile: Counter() for profile in PROFILES}
    for kind, value in source["rows"][:-1]:
        row = value.split("\t")
        if kind == "QUARTER":
            profile, pid, city, plot, complete, pillaged, river, *effect = row
            assert plot not in quarters
            quarters[plot] = dict(profile=profile, complete=complete == "true",
                                  ready=complete == "true" and pillaged == "false",
                                  effects=[float(x) for x in effect], river=river == "true",
                                  materials=[], producers=[], sales=[], customers=[])
        elif kind in DETAILS:
            plot, *details = row
            quarters[plot][DETAILS[kind]].append(details)
        elif kind == "SERVICE_BUILDING":
            pid, city, building, pillaged = row
            parts = building.split("_")
            services[parts[2]][parts[4]] += 1
    totals = {}
    for profile in PROFILES:
        stats = Counter()
        by_customer = {}
        for quarter in quarters.values():
            if quarter["profile"] != profile:
                continue
            stats["placed"] += 1
            if not quarter["complete"]:
                continue
            stats["complete"] += 1
            stats["river"] += quarter["river"]
            found = {class_ for _, class_, _, _ in quarter["materials"]}
            developed = {class_ for _, class_, _, works in quarter["materials"] if works == "true"}
            stats["base"] += "BASE" in found
            stats["spec"] += "SPEC" in found
            stats["both"] += len(found) == 2
            stats["base_improved"] += "BASE" in developed
            stats["spec_improved"] += "SPEC" in developed
            stats["both_improved"] += len(developed) == 2
            stats["sales"] += bool(quarter["sales"])
            stats["sales_outside_center"] += any(
                host != "DISTRICT_CITY_CENTER" for _, host in quarter["sales"])
            for stage in (2, 3, 4):
                stage_producers = [int(status) for s, _, status in quarter["producers"] if int(s) == stage]
                stage_hosts = [(plot, complete == "true", int(status))
                               for plot, s, _, complete, status in quarter["customers"] if int(s) == stage]
                working = any(complete and status == 2 for _, complete, status in stage_hosts)
                stats[f"producer{stage}"] += bool(stage_producers)
                stats[f"producer{stage}_working"] += 2 in stage_producers
                stats[f"customer{stage}"] += bool(stage_hosts)
                stats[f"customer{stage}_without_building"] += bool(stage_hosts) and not any(
                    status > 0 for _, _, status in stage_hosts)
                stats[f"customer{stage}_with_building"] += any(status > 0 for _, _, status in stage_hosts)
                stats[f"customer{stage}_working"] += working
                stats[f"service{stage}_property"] += quarter["ready"] and quarter["effects"][stage - 2] > 0
                for plot, complete, status in stage_hosts:
                    key = (stage, plot)
                    prev = by_customer.get(key, (False, 0))
                    by_customer[key] = (prev[0] or complete, max(prev[1], status))
                if stage == 2:
                    stats["stage2_physical"] += (
                        quarter["ready"] and "BASE" in developed and 2 in stage_producers and working)
        for (stage, _), (complete, status) in by_customer.items():
            stats[f"unique_customer{stage}"] += 1
            stats[f"unique_customer{stage}_with_building"] += status > 0
            stats[f"unique_customer{stage}_working"] += complete and status == 2
        for stage in (2, 3, 4):
            stats[f"service{stage}_buildings"] = services[profile][str(stage)]
        totals[profile] = stats
    return totals


def economy(path):
    source = census(path)
    players = {}
    for kind, value in source["rows"][:-1]:
        fields = value.split("\t")
        pid = fields[0]
        if kind == "PLAYER" and fields[1] == "true":
            players[pid] = Counter()
        elif kind == "TREASURY":
            assert all(field != "unavailable" for field in fields[1:]), fields
            reserve, gross, maintenance = map(float, fields[1:])
            players[pid].update(dict(reserve=reserve, gross_gold=gross, maintenance=maintenance,
                                     net_gold=gross - maintenance))
        elif kind == "CITY":
            assert all(field != "unavailable" for field in fields[2:]), fields
            population, production, food = map(float, fields[2:])
            players[pid].update(dict(cities=1, population=population, production=production, food=food))
    # A surviving original seat can be cityless; an eliminated seat has no
    # treasury row. Neither case warrants inventing output or dropping that
    # seat from compare()'s fixed original-seat denominator.
    assert all("reserve" in p for p in players.values())
    summary = Counter({k:0 for k in ('reserve','production','gross_gold','maintenance',
        'population','net_gold','food','cities','players')})
    for p in players.values():
        summary.update(p)
    summary["players"] = len(players)
    return summary, players


def compare(run,baseline,baseline_run):
    """Require a terminal run and compare the same200 clock before follow-through.

    This is a historical same-seed comparison. Matching initial physical map,
    leaders and units does not remove the changed-content/CE confound. Average
    empire output uses the original AI-seat count, including zero for any later
    eliminated AI; per-city output is separately available to show expansion.
    """
    load=lambda p:json.loads(p.read_text(encoding='utf-8'))
    assert load(run/'result.json')['closed']and load(run/'result.json')['reached']==250
    assert load(run/'session-closed.json')['verified']
    assert load(run/'full-game-observation-complete.json')['verified']
    original=load(run/'source.json');old=load(baseline_run/'source.json')
    assert original['original_ai']==old['original_ai'],'Different original AI cohorts'
    parity={key:original[key]==old[key]for key in('original_ai','map_signature','starts','units')}
    setup=load(run/'protocol.json');old_setup=load(baseline_run/'protocol.json')
    setup_parity={key:setup[key]==old_setup[key]for key in('map','map_size','map_seed','game_seed')}
    seats=len(original['original_ai']);assert seats>0
    label=('historical; same-seed changed-content/CE, not AI-only causal'
        if all(parity.values())and all(setup_parity.values())
        else 'historical; initial-state/setup mismatch, not AI-only causal')
    result=dict(comparison=label,initial_parity=parity,setup_parity=setup_parity,
        original_ai_seats=seats,windows={})
    for key,path,expected in(('baseline200',baseline,200),('harmonised200',run/'full-census-200.json',200),
            ('harmonised250',run/'full-census-250.json',250)):
        source=census(path,expected)
        roster={int(value.split('\t')[0])for kind,value in source['rows']if kind=='PLAYER'}
        assert roster==set(original['original_ai']),'Census AI cohort differs from source'
        total,players=economy(path)
        result['windows'][key]=dict(quarters=summarize(path),economy=dict(total),
            average_per_original_ai={k:total[k]/seats for k in('cities','population','production','gross_gold','net_gold','food')},
            average_per_city={k:total[k]/total['cities']if total['cities']else None
                for k in('population','production','food')},players=players)
    log=(run/'Lua.log').read_text(encoding='utf-8-sig')
    publications=[dict(zip(('turn','version','players','entries','omitted','matched','changed'),map(int,m)))
        for m in re.findall(r'CSC_AI_BAKERS_DISTRICTS turn=(\d+) version=(\d+) players=(\d+) entries=(\d+) omitted=(\d+) previousMatched=(\d+) previousChanged=(\d+)',log)]
    result['publications']=dict(count=len(publications),first=publications[0],last=publications[-1],
        omitted_total=sum(r['omitted']for r in publications),max_entries=max(r['entries']for r in publications))
    result['storekeeper']=load(run/'result.json')['storekeeper']
    trend=[]
    for turn in range(25,251,25):
        path=run/('full-census-'+str(turn)+'.json');total,_=economy(path)
        census(path,turn)
        trend.append(dict(turn=turn,economy=total,quarters=summarize(path)))
    result['trend']=trend
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in('run','baseline','baseline-run','output'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args()
    args.output.write_text(json.dumps(compare(args.run,args.baseline,args.baseline_run),indent=2)+'\n',encoding='utf-8')

