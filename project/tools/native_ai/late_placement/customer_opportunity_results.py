"""Join positively observed legal customer alternatives to actual foundations.

Closed records only. GROUP is the existing policy's publication-time legal set;
REMOVED is absence from that result, including failed reads. A same-turn CLOCK
is required. Outcomes without it remain unknown. This measures physical sites,
deduplicating capture, and leaves exact native admission/calibration to matrices
and the native journal. No game connection or new economic calculation.
"""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import re

from planning_results import parse


def fields(line):
    return dict(re.findall(r'(\w+)=([^\s]*)',line))


def candidate_state(log):
    histories=defaultdict(list);clocks=Counter()
    for kind,payload in re.findall(r'CSC_CUSTOMER_WATCH_(GROUP|REMOVED|CLOCK) ([^\r\n]+)',log):
        row=fields(payload);turn=int(row['turn'])
        if kind=='CLOCK':
            clocks[(int(row['player']),turn)]+=1
        elif kind=='REMOVED':
            histories[tuple(map(int,row['scope'].split(':')))].append((turn,None))
        else:
            def plots(value):
                return {int(p):dict(adjacency=float(a),links=int(n))
                        for p,a,n in (r.split(':')for r in value.split(',')if r)}
            key=tuple(int(row[k])for k in('player','city','district'))
            histories[key].append((turn,dict(reference=int(row['reference']),
                linked=plots(row.get('linked','')),ordinary=plots(row.get('ordinary','')))))
    return histories,clocks


def classify(choice,histories,clocks):
    if choice is None:return dict(status='native_choice_unobserved')
    pid,city,district,turn=(choice[k]for k in('player','city','district','turn'))
    if clocks[(pid,turn)]!=1:return dict(status='publication_clock_unknown_or_ambiguous')
    past=[r for r in histories.get((pid,city,district),[])if r[0]<=turn]
    current=past[-1][1]if past else None
    if not current:return dict(status='no_positive_group_observation')
    linked,ordinary=current['linked'],current['ordinary'];plot=choice['plot']
    if plot not in linked and plot not in ordinary:return dict(status='selected_plot_outside_observed_set')
    return dict(status='comparable'if linked and ordinary else'linked_only',
        selected_linked=plot in linked,group_observed_turn=past[-1][0],
        linked_plots=sorted(linked),ordinary_plots=sorted(ordinary),
        selected_ordinary_adjacency=(linked.get(plot)or ordinary[plot])['adjacency'],
        best_linked_adjacency=max((r['adjacency']for r in linked.values()),default=None),
        best_ordinary_adjacency=max((r['adjacency']for r in ordinary.values()),default=None))


def analyse(root):
    root=Path(root);closed=json.loads((root/'session-closed.json').read_text())
    if not(closed['verified']and closed['native_exit_code']==0):raise ValueError('Require cleanly closed game')
    log=(root/'Lua.log').read_text(encoding='utf-8-sig')
    if not re.search(r'CSC_CUSTOMER_WATCH_FINISH records=\d+ faults=0 dropped=0\b',log):
        raise ValueError('Require complete customer opportunity observer')
    detailed=json.loads((root/'planning-results.json').read_text())
    histories,clocks=candidate_state(log)
    # Native catalogue/connector output retains zero-link mapped district types.
    database=json.loads((root/'loaded-native-customer-database.json').read_text())
    mapped={row['DistrictType']for row in database['links']}
    foundations={}
    for row in detailed['constructions']:
        if row['districtType']not in mapped:continue
        key=row['districtType'],row['plot']
        if key not in foundations or row['turn']<foundations[key]['turn']:foundations[key]=row
    relation_rows=[r for r in parse(log,'CSC_PLANNING_')if r['kind']=='RELATION']
    results=[]
    for row in sorted(foundations.values(),key=lambda r:(r['turn'],r['plot'])):
        choice=row.get('nativeChoice');verdict=classify(choice,histories,clocks)
        related=[r for r in relation_rows if r['player']==row['player']and r['neighbourPlot']==row['plot']
            and r.get('neighbourDistrict')==row['district']and r.get('neighbourFoundationTurn')==row['turn']]
        earlier=[r for r in related if r.get('foundationOrder')=='quarterFirst'
            or r.get('foundationOrder')=='quarterPreexistingDateUnknown'
            and r.get('quarterFirstSeen',row['turn'])<row['turn']]
        # Only physical observations with the Quarter already founded establish
        # connection at the customer foundation. Later Quarter-first claims are
        # not inferred from end-game adjacency alone.
        linked_at_foundation=bool(earlier)
        results.append(dict(player=row['player'],city=row['city'],district=row['districtType'],plot=row['plot'],
            foundation_turn=row['turn'],choice_turn=choice and choice['turn'],
            adjacent_quarter_at_foundation=linked_at_foundation,
            supplier_quarters=sorted({r['quarter']for r in earlier}),
            later_customer_first_quarters=sorted({r['quarter']for r in related if r.get('foundationOrder')=='neighbourFirst'}),
            opportunity=verdict))
    by_type={}
    for kind in sorted({r['district']for r in results}):
        rows=[r for r in results if r['district']==kind];opps=[r for r in rows if r['opportunity']['status']=='comparable']
        by_type[kind]=dict(physical_customer_sites=len(rows),
            adjacent_at_foundation=sum(r['adjacent_quarter_at_foundation']for r in rows),
            founded_with_observed_competing_sites=len(opps),
            selected_linked_when_comparable=sum(r['opportunity']['selected_linked']for r in opps),
            physically_connected_when_comparable=sum(r['adjacent_quarter_at_foundation']for r in opps),
            coverage=dict(Counter(r['opportunity']['status']for r in rows)))
    return dict(schema='csc-customer-opportunities-v1',source=str(root),by_type=by_type,foundations=results,
        scope='Positive publication-time legal sets joined to native choices and physical sites; later native admission is separate.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=analyse(args.root)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['by_type'],indent=2))
