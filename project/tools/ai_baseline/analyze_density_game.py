"""Summarize density4 at250 and compare real common200 checkpoints."""
import argparse
from collections import Counter
import json
from pathlib import Path
from analyze_checkpoint_tuning import summarize,extra
from analyze import read,fraction


def metrics(folder,turn):
    game=summarize(folder,turn)
    catalog={r['type']:r['class'] for r in read(folder/'initial-map.json')['resources']}
    extra(folder,game,catalog,turn)
    return {k:game[k] for k in ('totals','population','owned_improved_plots','improved_plots_per_city','improved_plots_per_100_population','quarters','service_source_cities')}


def builders(root,turn):
    d=read(root/f'builders-{turn:03d}.json');assert not d['errors']
    majors={p['player'] for p in d['players']}
    c=Counter(e['event'] for e in d['events'] if e['player'] in majors)
    return {'turn':turn,'alive':sum(p['count'] for p in d['players']),'charges':sum(p['charges'] for p in d['players']),'trained':c['builder_training_completed'],'purchased':c['builder_purchased'],'added_to_map':c['builder_added']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trial',type=Path,required=True);p.add_argument('--previous',type=Path,required=True)
    a=p.parse_args();assert read(a.trial/'validation.json')['passed']
    previous=metrics(a.previous/'game-01',200);current=metrics(a.trial/'game-01',200);endpoint=metrics(a.trial/'game-01',250)
    result={'turn250':endpoint,'matched_turn200':{'previous_resource3_ai90_900':previous,'current_resource4_ai90_900':current},'builder_censuses':[builders(a.trial,t) for t in (1,50,100,150,200,250)],'previous_builder_turn200':builders(a.previous,200),
        'limits':['Same starting terrain/roster/research, different initial resource distribution by design.','Only one seed; later wars/expansion/research can diverge.','Previous trial ended after200; no matched previous250 endpoint.','Builder additions may include captures; operation starts are not completed improvements.']}
    (a.trial/'comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    lines=['# Latest CSC AI setup — resource pass4 and Builder90/900','', 'One original-seed Online/Prince/Standard game completed to250. Same terrain/roster as previous AI tests, with intentional resource additions. RH/TAR disabled.','', '| Metric | Previous at200 | Latest at200 | Latest at250 |','|---|---:|---:|---:|']
    for label,get in [('Cities',lambda g:g['totals']['cities']),('Population',lambda g:g['population']),('Owned unpillaged improved plots',lambda g:g['owned_improved_plots']),('Improved plots/city',lambda g:round(g['improved_plots_per_city'],2)),('Improved plots/100 population',lambda g:round(g['improved_plots_per_100_population'],1))]:
        lines.append('| '+label+' | '+' | '.join(str(get(g)) for g in (previous,current,endpoint))+' |')
    for q in ('BAKERS','TAILORS'):
        lines+=['',f'## {q.title()}','', '| Metric | Previous200 | Latest200 | Latest250 |','|---|---:|---:|---:|']
        for label,n,d in [('Completed','completed',None),('Chose Base when available','base_chosen_when_available','base_available'),('Base access at endpoint','base','completed'),('Adjacent owned Base improved','base_plots_improved','base_plots'),('Adjacent owned Specialty improved','spec_plots_improved','spec_plots'),('Supporting plots covered by districts','supporting_plots_under_districts','supporting_plots_total')]:
            lines.append('| '+label+' | '+' | '.join(fraction(g['quarters'][q].get(n,0),g['quarters'][q].get(d,0)) if d else str(g['quarters'][q].get(n,0)) for g in (previous,current,endpoint))+' |')
    lines+=['','## Service source cities','', '| Service | Previous200 | Latest200 | Latest250 |','|---|---:|---:|---:|']
    for prop in sorted(set(previous['service_source_cities'])|set(current['service_source_cities'])|set(endpoint['service_source_cities'])):
        lines.append('| '+prop+' | '+' | '.join(str(g['service_source_cities'].get(prop,0)) for g in (previous,current,endpoint))+' |')
    lines+=['','## Builder telemetry','',json.dumps(result['builder_censuses']),'','Previous Builder census at200: '+json.dumps(result['previous_builder_turn200']),'','## Limits','',*['- '+x for x in result['limits']]]
    (a.trial/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Completed report:',a.trial/'report.md',flush=True)

if __name__=='__main__':main()
