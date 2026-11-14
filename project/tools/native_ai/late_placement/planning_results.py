"""Summarise passive planning evidence without upgrading proposals to outcomes.

Keep raw event rows in the output for case review. Forecast units are Q8 native
utility; UI adjacency is a separate yield vector. A missing join stays missing.
This analysis never contacts the game or changes a policy package.
"""
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
import re
import statistics


def value(text):
    if text in ('true','false'):return text=='true'
    try:return int(text)
    except ValueError:
        try:return float(text)
        except ValueError:return text


def parse(text,prefix):
    rows=[]
    for line in text.splitlines():
        match=re.search(re.escape(prefix)+r'([A-Z_]+)\t(.*)',line)
        if not match:continue
        row={'kind':match[1]}
        for field in match[2].split('\t'):
            if '='in field:
                key,item=field.split('=',1);row[key]=value(item)
        rows.append(row)
    return rows


def distribution(values):
    return dict(n=len(values),minimum=min(values)if values else None,
                median=statistics.median(values)if values else None,
                mean=statistics.mean(values)if values else None,
                maximum=max(values)if values else None)


def analyse(root):
    root=Path(root);source=json.loads((root/'source.json').read_text(encoding='utf-8'))
    players=set(source['original_ai'])
    log=(root/'Lua.log').read_text(encoding='utf-8-sig')
    planning=parse(log,'CSC_PLANNING_')
    quarter=parse(log,'CSC_QUARTER_WATCH_')
    ui=parse(log,'CSC_DISTRICT_UI_')
    savings_path=root/'economy-savings.ndjson'
    savings=[json.loads(line)for line in savings_path.read_text(encoding='utf-8').splitlines()]if savings_path.exists()else[]
    choices=defaultdict(list)
    for row in savings:
        if row['kind']=='district-selection':
            choices[tuple(row[k]for k in ('player','city','district','plot'))].append(row)
    ai=lambda r:r.get('player')in players
    foundations=[r for r in planning if r['kind']=='FOUNDATION'and ai(r)]
    completions=[r for r in planning if r['kind']=='COMPLETION'and ai(r)]
    types={r['district']:r['districtType']for r in foundations}
    for line in (root/'loaded-district-catalogue.txt').read_text(encoding='utf-8').splitlines():
        m=re.search(r'CSC_DISTRICT_CATALOGUE\t(\d+)\t([^\t]+)',line)
        if m:types[int(m[1])]=m[2]
    ui_by_plot=defaultdict(list)
    for row in ui:
        if ai(row):ui_by_plot[(row['player'],row['city'],row['district'],row['plot'])].append(row)
    construction=[]
    for row in foundations:
        key=tuple(row[k]for k in ('player','city','district','plot'))
        observed=[r for r in ui_by_plot[key]if r.get('footprintMatches')and r.get('source')=='added'
                  and r.get('districtID')==row.get('districtID')and abs(r['turn']-row['turn'])<=1]
        prior_choices=[c for c in choices[key]if c['turn']<=row['turn']and c.get('totalQ8')is not None]
        chosen=max(prior_choices,key=lambda c:(c['turn'],c['sequence']))if prior_choices else None
        copy=dict(row,uiAdjacency=observed[0]if observed else None,
            uiClockDelta=observed[0]['turn']-row['turn']if observed else None,
            nativeChoice=chosen,nativeChoiceAgeTurns=row['turn']-chosen['turn']if chosen else None,
            sameTurnNativeOrderKnown=False)
        # This is the last known matched cache comparison at foundation, not a
        # recomputation of the native forecast or a proof of causal selection.
        copy['nativeScoreKnown']=row.get('nativeQ8')is not None
        construction.append(copy)
    relations={}
    for row in planning:
        if row['kind']=='RELATION'and ai(row):
            key=(row['player'],row['quarterPlot'],row['neighbourPlot'],row['role'])
            relations[key]=row
    orders=defaultdict(Counter)
    for row in relations.values():orders[row['role']][row['foundationOrder']]+=1
    by_type={}
    for district,kind in sorted(types.items(),key=lambda v:v[1]):
        built=[r for r in construction if r['district']==district]
        if not built:continue
        scores=[r['nativeQ8']for r in built if r['nativeScoreKnown']]
        adjacency=defaultdict(list)
        for r in built:
            for name,amount in (r['uiAdjacency']or{}).items():
                if name.startswith('YIELD_'):adjacency[name].append(amount)
        by_type[kind]=dict(foundations=len(built),
            completions=sum(r['district']==district for r in completions)+sum(bool(r.get('complete'))for r in built),
            matched_prior_native_Q8=distribution(scores),
            native_choice_total_Q8=distribution([r['nativeChoice']['totalQ8']for r in built if r['nativeChoice']]),
            native_choice_age_turns=distribution([r['nativeChoiceAgeTurns']for r in built if r['nativeChoice']]),
            exact_UI_event_adjacency_yields={name:distribution(v)for name,v in adjacency.items()},
            UI_event_adjacency_joined=sum(r['uiAdjacency']is not None for r in built))
    quality={}
    for family in ('BAKERS','TAILORS'):
        kind='DISTRICT_CSC_'+family+'_QUARTER'
        indices={index for index,name in types.items()if name==kind}
        rows=[r for r in quarter if r['kind']=='SITE'and r.get('event')=='foundation'
              and ai(r)and r.get('district')in indices]
        opportunities=[r for r in planning if r['kind']=='OPPORTUNITY'and ai(r)and r.get('district')in indices]
        quality[family]=dict(foundations=len(rows),at_least3=sum(r['millForecastTotal']>=3 for r in rows),
            at_least4=sum(r['millForecastTotal']>=4 for r in rows),
            base=sum(r['base']>0 for r in rows),spec=sum(r['spec']>0 for r in rows),
            both=sum(r['base']>0 and r['spec']>0 for r in rows),
            distinct_geometry_qualified_candidates=len({tuple(r[k]for k in ('player','city','district','plot'))
                for r in opportunities if r.get('qualified')}),
            distinct_positive_offers=len({tuple(r[k]for k in ('player','city','district','plot'))
                for r in opportunities if r.get('offered')}))
    losses=[r for r in planning if r['kind']=='MATERIAL_STATE'and ai(r)
            and(r.get('lostBase')or r.get('lostSpec')or r.get('lostWorking'))]
    previous_totals={};exhaustions=[]
    for row in planning:
        if row['kind']!='MATERIAL_TOTAL'or not ai(row):continue
        key=(row['player'],row['quarterPlot']);old=previous_totals.get(key)
        if old:
            for role in ('base','spec','baseWorking','specWorking'):
                if old[role]>0 and row[role]==0:
                    exhaustions.append(dict(player=row['player'],quarterPlot=row['quarterPlot'],
                        turn=row['turn'],role=role,previous=old[role],current=0,source=row['source']))
        previous_totals[key]=row
    transitions=[r for r in planning if r['kind']=='PLAN_TRANSITION'and ai(r)]
    summary=dict(original_ai=sorted(players),district_construction=by_type,quarter_quality_at_foundation=quality,
        distinct_relationship_orders={role:dict(count)for role,count in orders.items()},
        material_loss_events=len(losses),raw_resource_loss_events=sum(bool(r.get('lostBase')or r.get('lostSpec'))for r in losses),
        working_supplier_loss_events=sum(bool(r.get('lostWorking'))for r in losses),
        usable_material_exhaustions_by_role=dict(Counter(r['role']for r in exhaustions)),
        reconsideration_transitions=sum(bool(r.get('reconsidered'))for r in transitions),
        actual_native_declines=sum(r['kind']=='NATIVE_DECLINE'and ai(r)for r in planning),
        acquisition_offers_by_class=dict(Counter(r.get('materialClass','unknown')for r in planning
            if r['kind']=='ACQUISITION_OFFER'and ai(r))),
        native_savings_events=dict(Counter(r['kind']for r in savings)),
        native_choice_score_status=dict(Counter(r.get('scoreStatus','unknown')for r in savings if r['kind']=='district-selection')),
        faults=[r for r in planning if r['kind']in ('FAULT','LIMIT')],
        limits=['UI event adjacency is not the exact Core native call time.',
                'A prior cached native score can precede foundation; missing joins stay missing.',
                'Geometric candidates do not guarantee native legality, admission or investment.',
                'Category savings balances are not per-tile promises.'])
    output=dict(summary=summary,constructions=construction,material_losses=losses,
                usable_material_exhaustions=exhaustions,
                relationship_pairs=list(relations.values()),plan_transitions=transitions)
    (root/'planning-results.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path)
    print(json.dumps(analyse(parser.parse_args().run),indent=2))
