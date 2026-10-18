"""Offline summaries of the Quarter-owned supply trial, no native connection."""
import argparse,json
from collections import Counter
from pathlib import Path
from analyze_density_game import metrics
from analyze import read,fraction

def builders(root,turn,start_turn=1):
    d=read(root/f'builders-{turn:03d}.json');assert not d['errors']
    cohort={p['player'] for p in read(root/'builders-001.json')['players']}
    ev=Counter(e['event'] for e in d['events'] if e['player'] in cohort and e['turn']>=start_turn)
    return {'trained':ev['builder_training_completed'],'purchased':ev['builder_purchased'],'added_to_map':ev['builder_added'],'alive':sum(p['count'] for p in d['players'] if p['player'] in cohort),'charges':sum(p['charges'] for p in d['players'] if p['player'] in cohort)}

def main():
    p=argparse.ArgumentParser()
    for n in ('trial','previous'):p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert read(a.trial/'validation.json')['passed']
    gap=read(a.trial/'observation-gap.json') if (a.trial/'observation-gap.json').exists() else None
    start_turn=(gap['resume_turn']+1) if gap else 1
    result={'setup':{'improvement_base':90,'builder_priority':50,'quarter_owned_present':40,'improved_extra':80,'turn':250},'comparisons':{},'builders':{},'native_fixture':read(a.trial/'fixture-validation.json'),'limits':['One seed and combined Builder-priority/modifier treatment; cannot isolate causation.','Native effect application does not establish prospective AI valuation.','The Quarter owns the resource signal; marginal80 uses the Workshop improvement-attachment chain. Five additional experiments were deferred by user.','Historical initial resource4 world matched; later events may diverge. Current test uses DX12 versus prior DX11.','Builder event totals retain original major cohort after defeat; additions may include captures/grants.']}
    lines=['# Quarter-owned resource incentive trial','', 'Online / Prince / vanilla Standard, CSC only; same seed, roster and resource4 start as the previous run. Improvement90; Builder50; native bonus12/river4/sales10 retained; matching resources+40 and improved resources+80 extra.','', 'Native fixture verified actual private yields and pristine reload before natural autoplay. All checkpoint observers are read-only.','']
    for t in (200,250):
        old=metrics(a.previous/'game-01',t);new=metrics(a.trial/'game-01',t);result['comparisons'][str(t)]={'previous':old,'new':new};result['builders'][str(t)]={'previous':builders(a.previous,t,start_turn),'new':builders(a.trial,t,start_turn),'event_count_window_start':start_turn}
        lines += [f'## Turn {t}','', '| Metric | Previous | New |','|---|---:|---:|']
        for label,key in [('Cities',None),('Population','population'),('Owned unpillaged improved plots','owned_improved_plots'),('Improved plots/city','improved_plots_per_city'),('Improved plots/100population','improved_plots_per_100_population')]:
            vals=[g['totals']['cities'] if key is None else g[key] for g in (old,new)];lines.append('| '+label+' | '+' | '.join(str(round(v,2)) for v in vals)+' |')
        for q in ('BAKERS','TAILORS'):
            lines += ['',f'### {q.title()}','', '| Metric | Previous | New |','|---|---:|---:|']
            for label,n,d in [('Completed','completed',None),('Base placement choice when available','base_chosen_when_available','base_available'),('Final Base access','base','completed'),('Final both access','both','completed'),('Owned adjacent Base improved','base_plots_improved','base_plots'),('Owned adjacent Specialty improved','spec_plots_improved','spec_plots'),('Later sales chose adjacency','later_sales_chosen','later_sales_options'),('Supporting plots covered','supporting_plots_under_districts','supporting_plots_total')]:
                vals=[fraction(g['quarters'][q].get(n,0),g['quarters'][q].get(d,0)) if d else str(g['quarters'][q].get(n,0)) for g in (old,new)];lines.append('| '+label+' | '+' | '.join(vals)+' |')
        lines+=['','Services previous: '+json.dumps(old['service_source_cities']),'','Services new: '+json.dumps(new['service_source_cities']),'','Builder telemetry: '+json.dumps(result['builders'][str(t)]),'']
    result['observation_gap']=gap
    if gap:
        note='Observer gap: turns51 through '+str(gap['resume_turn'])+'. Final state counts are valid; placement decisions cover observed events only. Builder event comparisons use matched turns'+str(start_turn)+' onward; alive/charges are full endpoint censuses. Turn50 Builder census and private-yield sample were not exported.'
        result['limits'].append(note);lines += ['',note,'']
    result['native_signals']={}
    for t in (50,100,150,200,250):
        path=a.trial/f'supply-signal-{t:03d}.json'
        if not path.exists():
            result['native_signals'][str(t)]={'available':False,'reason':'Observer interruption before export'};continue
        d=read(path);result['native_signals'][str(t)]={'sampled':len(d['plots']),'improved':sum(x['improved'] for x in d['plots']),'errors':d['errors']}
    lines+=['## Limits','',*['- '+x for x in result['limits']],'','Final named save confirmed: '+str(read(a.trial/'validation.json')['named_save_confirmed'])+'. Endpoint autosaves preserved separately.']
    (a.trial/'comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');(a.trial/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Comparison/report complete at250.',flush=True)

if __name__=='__main__':main()
