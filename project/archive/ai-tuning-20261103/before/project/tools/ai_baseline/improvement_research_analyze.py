"""Offline endpoint and common-checkpoint comparison for the combined AI trial."""
import argparse,json
from pathlib import Path
from analyze import read
from analyze_density_game import metrics
from quarter_resource_analyze import builders

def main():
    p=argparse.ArgumentParser();p.add_argument('--trial',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);a=p.parse_args()
    assert read(a.trial/'validation.json')['passed']
    result={'comparisons':{},'endpoint':metrics(a.trial/'game-01',250),'endpoint_native':read(a.trial/'endpoint.json'),'fixture':read(a.trial/'fixture-validation.json'),'research':{},'builders':{},'limits':['One matched seed, two combined changes: improvement-source ownership and conditional research guidance. No causal separation.','Previous run has an observation gap51–67 and no exported250 census; common complete comparisons200/225 only. Placement-event rates are not compared here.','Improvement-owned80 counts once per industry/resource, not per adjacent Quarter. Presence40 still stacks per source Quarter.','Native effects/callback consumption do not establish prospective Builder forecasting. Source and installed code are archived; no winner automatically selected.']}
    for t in (200,225):
        result['comparisons'][str(t)]={'previous':metrics(a.previous/'game-01',t),'new':metrics(a.trial/'game-01',t)}
    # Restrict events to the same fully observed window in both runs.
    result['builders']['200']={'previous':builders(a.previous,200,68),'new':builders(a.trial,200,68),'event_window_start':68}
    result['builders']['250']={'new':builders(a.trial,250,68)}
    for t in (1,25,50,75,100,125,150,175,200,225,250):
        s=read(a.trial/'game-01'/f'turn-{t:03d}.json');r=read(a.trial/f'research-{t:03d}.json');assert not r['errors']
        result['research'][str(t)]={'native_callback_calls':sum(r['calls'].values()) if isinstance(r['calls'],dict) else sum(r['calls']),'players':[{k:p[k] for k in ('player','active_plans','completed')} for p in r['players']],'naval_tradition_completed':sum('CIVIC_NAVAL_TRADITION' in p['civics'] for p in s['players']),'opera_ballet_completed':sum('CIVIC_OPERA_BALLET' in p['civics'] for p in s['players'])}
    lines=['# Improvement-owned resource value and conditional Service research','', 'Online/Prince/Small Continents, matched seeds830102/940104, vanilla Standard, material pass4. Builder50/improvement90 and native12/4/10 held fixed.','', '| Metric | Previous200 | New200 | Previous225 | New225 | New250 |','|---|---:|---:|---:|---:|---:|']
    groups=[result['comparisons']['200']['previous'],result['comparisons']['200']['new'],result['comparisons']['225']['previous'],result['comparisons']['225']['new'],result['endpoint']]
    for label,get in [('Cities',lambda g:g['totals']['cities']),('Population',lambda g:g['population']),('Improved plots/city',lambda g:round(g['improved_plots_per_city'],2)),('Improved plots/100population',lambda g:round(g['improved_plots_per_100_population'],2))]:lines.append('| '+label+' | '+' | '.join(str(get(g)) for g in groups)+' |')
    for q in ('BAKERS','TAILORS'):
        for label,key in [('completed','completed'),('Base access','base'),('Base resource copies','base_plots'),('Base copies improved','base_plots_improved'),('both-material access','both')]:lines.append('| '+q+' '+label+' | '+' | '.join(str(g['quarters'][q].get(key,0)) for g in groups)+' |')
    lines+=['','Service sources at250: '+json.dumps(result['endpoint']['service_source_cities']), '', 'Research at250: '+json.dumps(result['research']['250']), '', 'Builder common-window telemetry: '+json.dumps(result['builders']), '', '## Limits','',*['- '+x for x in result['limits']]]
    (a.trial/'comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');(a.trial/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('Combined AI trial report saved.')
if __name__=='__main__':main()
