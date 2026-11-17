"""Closed-game ordinary-economy results, with no game connection or policy.

Reuse the established placement and census definitions. Join customer economic
proposals to versioned native receipts; merged spatial/economic entries remain
one packet, so a receipt measures their combined delivery. Construction remains
a separate observed outcome. Native utility is Q8; physical adjacency is not.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from full_game_results import census, economy, summarize
from planning_campaign_results import report
from planning_results import distribution


def numeric_fields(text):
    return {key:float(value)if'.'in value else int(value)
            for key,value in re.findall(r'(\w+)=(-?\d+(?:\.\d+)?)(?=\s|$)',text)}


def customer_delivery(log,constructions):
    publications={int(turn):int(version)for turn,version in re.findall(
        r'CSC_AI_BAKERS_DISTRICTS turn=(\d+) version=(\d+)',log)}
    proposals=[];by_version={};by_site=defaultdict(list)
    for payload in re.findall(r'CSC_AI_CUSTOMER_ECONOMIC_BID ([^\r\n]+)',log):
        row=numeric_fields(payload);proposals.append(row)
        key=tuple(row[name]for name in ('player','city','district','plot'))
        by_site[key].append(row)
        if row['turn']in publications:
            # A retry can emit another proposal before one successful commit.
            # Keep its latest component for that packet's readback identity.
            by_version[(publications[row['turn']],*key)]=row
    receipts={};readback_errors=0
    for payload in re.findall(r'CSC_AI_CUSTOMER_RECEIPT ([^\r\n]+)',log):
        header,raw=payload.split(' result=',1);row=numeric_fields(header)
        key=tuple(row[name]for name in ('version','player','city','district','plot'))
        if key not in by_version:continue
        result=json.loads(raw)
        if result.get('readbackError'):
            readback_errors+=1;continue
        previous=receipts.setdefault(key,{})
        # Receipt counters accumulate within a packet. Repeated readbacks are
        # coverage of the same window, not additional score writes.
        for field in ('staged','scoreAttempts','writes','cacheReads','siteWins'):
            previous[field]=max(previous.get(field,0),result.get(field,0))
    foundations=[]
    for row in constructions:
        key=tuple(row[name]for name in ('player','city','district','plot'))
        prior=[p for p in by_site.get(key,[])if p['turn']<=row['turn']]
        if prior:
            latest=max(prior,key=lambda p:p['turn'])
            foundations.append({name:row[name]for name in ('turn','player','city','district','plot')}|
                {'latest_proposal_turn':latest['turn'],'latest_component_Q8':latest['deltaQ8']})
    return dict(proposals=len(proposals),distinct_targets=len(by_site),
        positive=sum(p['deltaQ8']>0 for p in proposals),negative=sum(p['deltaQ8']<0 for p in proposals),
        component_utility=distribution([p['deltaQ8']/256 for p in proposals]),
        receipt_windows=len(receipts),staged_windows=sum(r.get('staged',0)>0 for r in receipts.values()),
        attempted_windows=sum(r.get('scoreAttempts',0)>0 for r in receipts.values()),
        written_windows=sum(r.get('writes',0)>0 for r in receipts.values()),
        site_win_windows=sum(r.get('siteWins',0)>0 for r in receipts.values()),
        score_attempts=sum(r.get('scoreAttempts',0)for r in receipts.values()),
        score_writes=sum(r.get('writes',0)for r in receipts.values()),readback_errors=readback_errors,
        foundations_on_previously_proposed_targets=foundations,
        scope='Receipts cover combined staged entries; foundations are a separate same-target observation.')


def analyse(root):
    root=Path(root)
    load=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
    result=load('result.json');closed=load('session-closed.json')
    if not(result['closed']and result['reached']==250 and closed['verified']
           and closed['native_exit_code']==0 and load('full-game-observation-complete.json')['verified']):
        raise ValueError('Require a completed, cleanly closed250-turn game')
    planning=report(root)
    detailed=load('planning-results.json')
    log=(root/'Lua.log').read_text(encoding='utf-8-sig')
    original=load('source.json');seats=len(original['original_ai'])
    trend=[]
    for turn in range(25,251,25):
        path=root/f'full-census-{turn}.json';census(path,turn)
        total,players=economy(path)
        trend.append(dict(turn=turn,quarters=summarize(path),economy=total,players=players,
            average_per_original_ai={name:total[name]/seats for name in
                ('cities','population','production','gross_gold','net_gold','food')}))
    work=[numeric_fields(payload)for payload in re.findall(r'CSC_AI_JOINT_WORK ([^\r\n]+)',log)]
    work_totals=Counter()
    for row in work:
        work_totals.update({key:row.get(key,0)for key in
            ('worlds','evaluations','budgetFailures','unknown','cacheHits','routeHits','routeMisses','routeOverflow')})
    return dict(schema='csc-ordinary-economy-results-v1',root=str(root),
        original_ai=original['original_ai'],closed=closed,setup=load('protocol.json'),
        planning=planning,trend=trend,
        customer_economic_delivery=customer_delivery(log,detailed['constructions']),
        joint_work=dict(total=work_totals,player_publications=len(work),
                        max_evaluations_per_player=max((r['evaluations']for r in work),default=0)),
        storekeeper=result.get('storekeeper'),processing_time=load('ai-processing-time.json'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();data=analyse(args.run)
    args.output.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(quarters=data['planning']['summary']['quarter_quality_at_foundation'],
                         customer=data['customer_economic_delivery'],
                         processing=data['processing_time']['publisher_wall']),indent=2))
