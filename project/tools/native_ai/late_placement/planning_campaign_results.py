"""Closed-record comparison for the three-map planning campaign.

This is diagnostic analysis, never live policy. Consume the selected, closed
segments produced by planning_results/segments; do not join native identities
across processes. Save alternatives, consumed bids, foundations and purchases
as separate measures. Q8 totals are native utility /256, not adjacency yields.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from planning_results import analyse, parse


def stock_district(kind):
    # Campaign packages are pinned to CSC, CL and resource packs. Both CL urban
    # CoreExpansion tiers and rural/CoreX variants are mod districts; a prefix
    # exclusion is scoped to this stack, not a generic origin detector.
    return not kind.startswith(('DISTRICT_CSC_','DISTRICT_RURAL',
                                'DISTRICT_COREX_','DISTRICT_COREEXPANSION'))


def contexts(root):
    """Later boundary facts; sharing a turn number never proves native ordering."""
    rows=[]
    for path in root.glob('purchase-context-*.txt'):
        for match in re.finditer(r'CSC_PURCHASE_CONTEXT\t([^\r\n]+)',path.read_text(encoding='utf-8-sig')):
            f=match[1].split('\t')
            if len(f)<12:
                raise ValueError('Short context row in '+str(path))
            rows.append(dict(turn=int(f[0]),player=int(f[1]),plot=int(f[2]),owner=int(f[3]),
                resource=f[5],family=f[7],base=f[8]=='true',spec=f[9]=='true',
                quarterPlots=[int(i)for i in f[10].split(',')if i]))
    return rows


def financial(rows, context_rows, quarter_indices):
    """Measure actual debits; optional unqualified native owner bytes are ignored.

    Fresh-contract lineage identifies a requested district target. Later Lua
    ownership is corroboration, not a payment-time resource/Quarter census.
    A quote or request alone is never counted as a tile purchase.
    """
    paid=[r for r in rows if r['kind']=='purchase-debit-return']
    checks=[r for r in rows if r['kind']=='targeted-savings']
    confirmed=0; quarter_paid=[]; adjacent_material=[]
    context_by_plot=defaultdict(list)
    for c in context_rows:context_by_plot[(c['player'],c['plot'])].append(c)
    for r in paid:
        later=[c for c in context_by_plot[(r['player'],r['plot'])]if c['turn']>r['turn']]
        if later and any(c['owner']==r['player']for c in later):confirmed+=1
        selection=(r.get('lineage')or{}).get('selection')or{}
        if selection.get('district')in quarter_indices:quarter_paid.append(r)
        # This is a subsequent relationship observation, not proof that the
        # Quarter existed at payment or that CSC requested the material.
        if later:
            nearest=min(c['turn']for c in later)
            if any((c['base']or c['spec'])and c['quarterPlots']for c in later if c['turn']==nearest):
                adjacent_material.append(r)
    failed=[r for r in checks if not(r['passesPlotFund']and r['passesCombinedFunds'])]
    choices=[r for r in rows if r['kind']=='district-selection']
    return dict(paid=len(paid),gold=sum(-r['measuredDeltaQ8']/256 for r in paid),
        debit_deltas_match=sum(r.get('deltaMatched')is True for r in paid),
        later_owner_confirmed=confirmed,quarter_site_payments=len(quarter_paid),
        later_adjacent_material_payments=len(adjacent_material),
        targeted_checks=len(checks),targeted_pass=sum(r['passesPlotFund']and r['passesCombinedFunds']for r in checks),
        category_fail_with_enough_treasury=sum(r['treasuryQ8']>=r['gold']*256 for r in failed),
        quarter_choices=len([r for r in choices if r['district']in quarter_indices]),
        quarter_frontier_choices=sum(r.get('frontier')is True for r in choices if r['district']in quarter_indices),
        choice_totals_read=sum(r.get('scoreStatus')=='read'for r in choices),choice_totals=len(choices),
        max_plot_fund=max((r['plotQ8']/256 for r in checks),default=None),
        weights=sorted({tuple(r['savingWeights'])for r in checks}))


def report(root):
    root=Path(root)
    # Refuse a partly written/live arm. Normalized continuations carry two
    # closure proofs; a completed seed is never inferred from its directory name.
    normalized=root/'normalized-segments.json'
    segments=[root/'segments'/s for s in ('original','continuation')]if normalized.exists()else[root]
    for segment in segments:
        for name in ('session-closed.json','preferences-restored.json'):
            if not json.loads((segment/name).read_text(encoding='utf-8')).get('verified'):
                raise ValueError('Unverified closed segment: '+str(segment/name))
    summary=analyse(root)
    result=json.loads((root/'planning-results.json').read_text(encoding='utf-8'))
    log=(root/'Lua.log').read_text(encoding='utf-8-sig')
    planning=parse(log,'CSC_PLANNING_');watch=parse(log,'CSC_QUARTER_WATCH_')
    players=set(summary['original_ai'])
    catalogue=(root/'loaded-district-catalogue.txt').read_text(encoding='utf-8-sig')
    quarter_indices={int(i)for i in re.findall(r'CSC_DISTRICT_CATALOGUE\t(\d+)\tDISTRICT_CSC_(?:BAKERS|TAILORS)_QUARTER\t',catalogue)}
    native=[json.loads(line)for line in(root/'economy-savings.ndjson').read_text(encoding='utf-8').splitlines()]
    native=[r for r in native if r.get('player')in players]
    physical={}
    for row in result['relationship_pairs']:
        key=(row['player'],row['quarterPlot'],row['neighbourPlot'])
        if key in physical and physical[key]['foundationOrder']!=row['foundationOrder']:
            raise ValueError('Conflicting physical relationship chronology: '+repr(key))
        physical[key]=row
    types=summary['district_construction']
    vanilla={k:v for k,v in types.items()if stock_district(k)}
    count_native=sum(v['foundations']for v in vanilla.values())
    quotes=sum(v['native_choice_total_Q8']['n']for k,v in vanilla.items()if k not in('DISTRICT_CITY_CENTER','DISTRICT_WONDER'))
    eligible=sum(v['foundations']for k,v in vanilla.items()if k not in('DISTRICT_CITY_CENTER','DISTRICT_WONDER'))
    funds=financial(native,contexts(root),quarter_indices)
    foundations=[r for r in watch if r['kind']=='SITE'and r.get('event')=='foundation'and r.get('player')in players]
    opportunity_packets=defaultdict(list)
    for r in planning:
        if r['kind']=='OPPORTUNITY':
            opportunity_packets[(r.get('segment'),r['player'],r['city'],r['district'],r['version'])].append(r)
    packet_comparisons=[]
    for f in result['constructions']:
        if f['district']not in quarter_indices:continue
        offered=[r for r in opportunity_packets[(f.get('segment'),f['player'],f['city'],f['district'],f.get('bidVersion'))]if r.get('offered')]
        selected=[r for r in offered if r['plot']==f['plot']]
        maximum=max((r['upper']for r in offered),default=None)
        packet_comparisons.append(dict(player=f['player'],city=f['city'],district=f['district'],plot=f['plot'],
            turn=f['turn'],segment=f.get('segment'),version=f.get('bidVersion'),positive_sites=len(offered),
            selected_was_offered=bool(selected),best_offered_geometry=maximum,
            selected_ties_best=bool(selected)and selected[-1]['upper']==maximum))
    material_origins=defaultdict(set)
    for r in planning:
        if r['kind']=='MATERIAL_STATE'and r.get('player')in players and(r.get('base')or r.get('spec')):
            for role in ('base','spec'):
                if r.get(role):material_origins[(r['quarter'],role.upper(),r.get('origin','unknown'))].add(
                    (r['player'],r['quarterPlot'],r['materialPlot']))
    return dict(root=str(root),summary=summary,financial=funds,physical_relationships=list(physical.values()),
        relationship_order=dict(Counter(r['foundationOrder']for r in physical.values())),
        providers_adjacent=len({(r['player'],r['quarterPlot'],r['neighbourPlot'])
            for r in result['relationship_pairs']if r.get('role')=='goodsProvider'}),
        vanilla_foundations=count_native,vanilla_types=len(vanilla),vanilla_quotes=quotes,vanilla_quote_eligible=eligible,
        vanilla=vanilla,quarter_foundations=foundations,
        material_role_observations={'/'.join(k):len(v)for k,v in material_origins.items()},
        packet_comparisons=packet_comparisons,
        reconsidered_scopes=len({(r['player'],r['city'],r['district'])for r in result['plan_transitions']if r.get('reconsidered')}),
        raw_segments_required_for_services=(root/'normalized-segments.json').exists())


def markdown(reports):
    lines=['# Three-map CSC planning campaign —250 turns', '',
        'Original AI seats only. Quarter quality is observed geometry with a prospective local Mill; '
        'it excludes future customers and is not active gameplay yield. Native totals are '
        'choice-time utility; adjacency is a separate UI-event yield vector. Pangaea includes a '
        'verified turn200 reload with an explicit native capture gap.', '',
        '| Map | Bakers | Tailors | +3+ | +4+ | Base | Spec / both | Vanilla footprints | Native totals joined |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,r in reports.items():
        q=r['summary']['quarter_quality_at_foundation'];b=q['BAKERS'];t=q['TAILORS']
        lines.append(f"| {name} | {b['foundations']} | {t['foundations']} | {b['at_least3']+t['at_least3']} | "
            f"{b['at_least4']+t['at_least4']} | {b['base']+t['base']} | {b['spec']+t['spec']} / {b['both']+t['both']} | "
            f"{r['vanilla_foundations']} | {r['vanilla_quotes']}/{r['vanilla_quote_eligible']} |")
    lines+=['','City Centers and Wonder footprints are included in footprint counts but excluded from '
        'the forecast-join denominator. A Wonder district completion flag does not establish completion of its building.', '',
        '| Map | Exact new-site bids consumed | Reconsiderations / scopes | Physical neighbour order | Mapped losses | Paid tiles / Gold | Quarter-site payments |',
        '|---|---:|---:|---|---:|---:|---:|']
    for name,r in reports.items():
        s=r['summary'];f=r['financial'];o=', '.join(f'{k}:{v}'for k,v in r['relationship_order'].items())or'none'
        lines.append(f"| {name} | {s['new_quarter_native_best_exact_bid_write']}/{s['new_quarter_native_best']} | "
            f"{s['reconsideration_transitions']}/{r['reconsidered_scopes']} | {o} | {s['material_loss_events']} | "
            f"{f['paid']} / {f['gold']:g} | {f['quarter_site_payments']} |")
    lines+=['','## Vanilla district calibration','',
        'These districts competed in the **tuned CSC/City Lights games**. They are not an untuned control. '
        'Different cities, turns and costs make their medians descriptive rather than interchangeable bid targets.', '',
        '| Map | District | Foundations | UI joins | Mean nonzero adjacency yields | Native quote joins | Median utility | Median quote age |',
        '|---|---|---:|---:|---|---:|---:|---:|']
    for name,r in reports.items():
        for kind,v in r['vanilla'].items():
            yields=', '.join(k.removeprefix('YIELD_').lower()+f" {d['mean']:.2f}"for k,d in v['exact_UI_event_adjacency_yields'].items()if d['mean']and k!='YIELD_CSC_AI_PLACEMENT')or'0'
            score=v['native_choice_total_Q8'];age=v['native_choice_age_turns']['median']
            median=f"{score['median']/256:.1f}"if score['n']else'—'
            lines.append(f"| {name} | {kind.removeprefix('DISTRICT_')} | {v['foundations']} | {v['UI_event_adjacency_joined']} | {yields} | {score['n']} | {median} | {age if age is not None else '—'} |")
    return '\n'.join(lines)+'\n'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='append',required=True,help='NAME=closed record directory')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    runs=dict(item.split('=',1)for item in args.run)
    reports={name:report(Path(path))for name,path in runs.items()}
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'planning-campaign-results.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf-8')
    (args.output/'planning-campaign-results.md').write_text(markdown(reports),encoding='utf-8')
    print(json.dumps({name:dict(quarters=r['summary']['quarter_quality_at_foundation'],financial=r['financial'])for name,r in reports.items()},indent=2))
