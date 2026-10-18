"""Compare a completed tuning trial with its original seed; no game connection."""
import argparse
import json
from pathlib import Path
from statistics import median
from analyze import analyze, output_csv, read
from paired_analysis import base_opportunities


def fraction(n,d):
    return f'{n}/{d} ({100*n/d:.0f}%)' if d else '0/0'


def summarize(folder):
    game=analyze(folder,250)
    game['base_placement_choices']=base_opportunities(folder,game)
    s=read(folder/'turn-250.json')
    majors={p['id'] for p in read(folder/'turn-001.json')['players']}
    game['population']=sum(c['population'] for c in s['cities'])
    game['owned_improved_plots']=sum(p['owner'] in majors and bool(p.get('improvement')) and not p['pillaged'] for p in s['plots'])
    for q,v in game['quarters'].items():
        for cat in ('base','spec'):
            plots=[p for p in game['improvement_comparison'] if p['quarter']==q and p['category']==cat and p['adjacent_to_quarter']]
            v[cat+'_plots']=len(plots);v[cat+'_plots_improved']=sum(p['improved'] for p in plots)
        sales=[p for p in game['customer_choices'] if p['quarter']==q and p['comparable'] and p['adjacency_option']]
        v['later_sales_options']=len(sales);v['later_sales_chosen']=sum(p['adjacent'] for p in sales)
        seen=set();available=chosen=0
        for e in s['events']:
            if e['event']!='district':continue
            identity=(e['plot'],e.get('district'))
            if identity in seen:continue
            seen.add(identity)
            if e.get('quarter')!=q or e['player'] not in majors:continue
            cache=e.get('previous_candidates') or {};sites=cache.get('sites') or []
            if not sites or not 0<=e['turn']-cache.get('turn',-100)<=1:continue
            if any(p['sales']>0 for p in sites):
                available+=1;chosen+=e['site']['sales']>0
        v['quarter_sales_options']=available;v['quarter_sales_chosen']=chosen
        lost={p['resource_plot'] for p in game['material_retention'] if p['quarter']==q and not p['resource_retained'] and p['final_district']}
        v['supporting_plots_under_districts']=len(lost)
        waits=[p['improved_turn']-p['quarter_turn'] for p in game['improvement_timing'] if p['quarter']==q and p['category']=='base' and p['improved_turn'] is not None]
        v['base_improvement_median_wait']=median(waits) if waits else None
    return game


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trial',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--map',type=int,default=1)
    a=p.parse_args();folder=f'game-{a.map:02d}'
    assert read(a.trial/folder/'complete.json')['turn']==250
    control=summarize(a.baseline/folder);trial=summarize(a.trial/folder)
    result={'baseline':control,'trial':trial}
    if (a.trial/'placement-probe.json').exists():
        probe=read(a.trial/'placement-probe.json');rows=probe.get('rows',[])
        ai={p['player'] for p in probe.get('human',[]) if not p['human']}
        valid=[r for r in rows if r['player'] in ai and r.get('native_value') is not None]
        material=[r for r in valid if r['base']>0 or r['spec']>0]
        legal=[r for r in valid if r.get('legal')]
        legal_material=[r for r in legal if r['base']>0 or r['spec']>0]
        completed=[r for r in probe.get('completed',[]) if r['player'] in ai and r.get('complete') and not r.get('pillaged') and r.get('native_value') is not None]
        completed_material=[r for r in completed if r['base']>0 or r['spec']>0]
        result['probe_summary']={'candidate_rows':len(rows),'ai_rows':len(valid),'material_rows':len(material),
            'legal_ai_rows':len(legal),'legal_material_rows':len(legal_material),
            'legal_material_rows_with_additional_native_value':sum(abs(r['native_value']-10*r['sales'])>.001 for r in legal_material),
            'native_equals_sales_only':sum(abs(r['native_value']-10*r['sales'])<.001 for r in valid),
            'material_rows_with_additional_native_value':sum(abs(r['native_value']-10*r['sales'])>.001 for r in material),
            'completed_ai_quarters':len(completed),'completed_ai_material_quarters':len(completed_material),
            'completed_material_exact_expected_value':sum(abs(r['native_value']-(10*r['sales']+12*bool(r['base'])+4*bool(r['spec'])))<.001 for r in completed_material),
            'completed_material_adjacency_equals_sales':sum(r.get('native_adjacency') is not None and abs(r['native_adjacency']-10*r['sales'])<.001 for r in completed_material),
            'completed_material_signal_matches_native_plot_delta':sum(r.get('native_plot_adjacency') is not None and abs(r['native_value']-r['native_plot_adjacency']-12*bool(r['base'])-4*bool(r['spec']))<.001 for r in completed_material),
            'material_modifier_instances':len(probe.get('modifiers',[])),
            'material_modifier_active_instances':sum(bool(r['active']) for r in probe.get('modifiers',[])),
            'modifier_probe_error':probe.get('modifier_probe_error'),
            'ui_filter':probe.get('ui_filter')}
        result['material_choices_nonhuman']={label:{q:{key:sum(v[key] for v in g['base_placement_choices'] if v['quarter']==q and v['player'] in ai)
            for key in ('base_available','base_chosen_when_available','base_sales_available','base_sales_chosen_when_available')}
            for q in ('BAKERS','TAILORS')} for label,g in (('baseline',control),('trial',trial))}
    (a.trial/'comparison.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for name in ('details','base_placement_choices','customer_choices','improvement_comparison','improvement_timing','material_retention','service_opportunities','building_opportunities','timeline'):
        output_csv(a.trial/(name+'.csv'),[{'run':label,**r} for label,g in [('baseline',control),('trial',trial)] for r in g[name]])
    metrics=[('Completed Quarters','completed',None),('Base access at endpoint','base','completed'),
             ('Sales access at endpoint','sales','completed'),('Non-City-Center sales access','non_center_sales','completed'),
             ('Chose Base when available','base_chosen_when_available','base_available'),
             ('Chose Base + sales when available','base_sales_chosen_when_available','base_sales_available'),
             ('Quarter chose sales adjacency when available','quarter_sales_chosen','quarter_sales_options'),
             ('Later sales chose Quarter adjacency when available','later_sales_chosen','later_sales_options'),
             ('Adjacent owned Base plots improved','base_plots_improved','base_plots'),
             ('Adjacent owned Specialty plots improved','spec_plots_improved','spec_plots'),
             ('Supporting material plots later covered by districts','supporting_plots_under_districts',None)]
    lines=['# CSC AI native placement tuning — seed 1 trial','',
           'One real game to the beginning of turn 250, Online/Prince/Standard, Small map (74×46), Continents.lua, CSC and standard AI. The starting map and leaders match baseline seed pair 1. RomanHoliday is a code reference, not an enabled mod.','',
           '| Metric | Baseline | Tuning v1 |','|---|---:|---:|',
           f'| Major cities | {control["totals"]["cities"]} | {trial["totals"]["cities"]} |',
           f'| Population | {control["population"]} | {trial["population"]} |',
           f'| Owned improved plots | {control["owned_improved_plots"]} | {trial["owned_improved_plots"]} |']
    for q in ('BAKERS','TAILORS'):
        lines+=['',f'## {q.title()}','', '| Metric | Baseline | Tuning v1 |','|---|---:|---:|']
        for label,n,d in metrics:
            values=[fraction(g['quarters'][q].get(n,0),g['quarters'][q].get(d,0)) if d else str(g['quarters'][q].get(n,0)) for g in (control,trial)]
            lines.append('| '+label+' | '+' | '.join(values)+' |')
        lines.append('| Stage 2 / 3 / 4 buildings | '+' | '.join(' / '.join(str(g['quarters'][q].get('stage'+str(i),0)) for i in (2,3,4)) for g in (control,trial))+' |')
    lines+=['','## Native Service sources','', '| Source property | Baseline | Tuning v1 |','|---|---:|---:|']
    for prop in sorted(control['service_source_cities'].keys()|trial['service_source_cities'].keys()):
        lines.append(f'| {prop} | {control["service_source_cities"].get(prop,0)} | {trial["service_source_cities"].get(prop,0)} |')
    lines+=['','## Native prospective probe','',json.dumps(result.get('probe_summary',{})),
            '', '## Interpretation','',
            'Placement alternatives are owned native plot-legal scans, at most one turn old; they do not establish affordability or the best overall city plan. A Quarter can be worthwhile without materials. Base supports stages 2/3 and Specialty is needed for rarer stage 4.',
            '', 'The candidate probe reads prospective adjacency, not total district yield or a complete internal AI score. Material modifiers change base yield, so their absence from the adjacency query would not prove that the AI ignores them. Conversely, completed activation would not prove prospective recognition. One matched seed is exploratory: wars, expansion and subsequent choices diverge, and the combined treatment does not isolate each coefficient.',
            '', 'Primary behavior tables retain all six autoplay majors, matching the baseline. Player 0 retains its human flag during autoplay, so AI-only material modifiers exclude it; the native probe excludes it too. The non-human-only material-choice counts are retained separately in comparison.json.',
            '', 'Exact commands, native SQL/UI checks, unchanged observer, eleven snapshots, two saves, source/installed hashes and restored preferences are retained with this trial. Excluded turn-one smoke attempts in the parent folder are not included.']
    (a.trial/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'baseline':control['totals'],'trial':trial['totals'],'probe':result.get('probe_summary')}))


if __name__=='__main__':main()
