"""Compact, offline Medieval-start research experiment report; no Tuner calls."""
import argparse,csv,json,sqlite3
from collections import Counter
from pathlib import Path
from run import write
from paired_standard import read
from analyze_density_game import metrics
from quarter_resource_analyze import builders
from quarter_resource_detail import analyze_detail,replacement_audit
from sales_prevalence import analyze as sales,aggregate

def main():
 p=argparse.ArgumentParser();p.add_argument('--trial',type=Path,required=True);p.add_argument('--previous',type=Path,required=True);a=p.parse_args()
 assert read(a.trial/'validation.json')['passed']
 db=sqlite3.connect((a.trial/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
 defs={r['ResourceType']:dict(r) for r in db.execute('SELECT ResourceType,ResourceClassType,PrereqTech,PrereqCivic FROM Resources')};df={};bf={}
 for table,base,variant,target in [('DistrictReplaces','ReplacesDistrictType','CivUniqueDistrictType',df),('BuildingReplaces','ReplacesBuildingType','CivUniqueBuildingType',bf)]:
  for r in db.execute(f'SELECT {base},{variant} FROM {table}'):target.setdefault(r[0],{r[0]}).add(r[1])
 era={r['EraType']:r['ChronologyIndex'] for r in db.execute('SELECT EraType,ChronologyIndex FROM Eras')}
 tech={r['TechnologyType']:r['EraType'] for r in db.execute('SELECT TechnologyType,EraType FROM Technologies')};civic={r['CivicType']:r['EraType'] for r in db.execute('SELECT CivicType,EraType FROM Civics')};db.close()
 result={'setup':read(a.trial/'game-01/settings.json'),'comparisons':{},'research':{},'limits':['Medieval start versus previous Ancient start: endpoint comparisons are descriptive, not a matched treatment estimate.','One seed; war, survival and expansion may diverge.','Native on/off fixture can demonstrate a research-choice response; it does not prove optimal play or Builder forecasting.','Sales counts are functioning producer/customer relationships, not cumulative payment events.','Resource removal uses last-observed state; intervening harvests can be missed.']}
 for t in (100,150,200,225,250):
  result['comparisons'][str(t)]={}
  for label,root in [('previous_ancient',a.previous),('new_medieval',a.trial)]:
   result['comparisons'][str(t)][label]={'metrics':metrics(root/'game-01',t),'sales':aggregate([sales(root/'game-01',t,df,bf)])}
   if (root/f'builders-{t:03d}.json').exists():result['comparisons'][str(t)][label]['builders']=builders(root,t)
  r=read(a.trial/f'research-{t:03d}.json');result['research'][str(t)]={'native_callback_calls':sum(r['calls'].values()) if isinstance(r['calls'],dict) else sum(r['calls']),'players':[{k:x[k] for k in ('player','active_plans','completed')} for x in r['players']]}
 detail=analyze_detail(a.trial/'game-01',250,defs);removal=replacement_audit(a.trial/'game-01',250,defs);write(a.trial/'quarter-details.json',detail);write(a.trial/'resource-replacement-audit.json',removal)
 result['endpoint_detail']={k:v for k,v in detail.items() if k!='quarter_rows'};result['resource_removal_summary']=removal['summary']
 s=read(a.trial/'game-01/turn-250.json');bc=read(a.trial/'builders-250.json');bmap={x['player']:x for x in bc['players']};initial=read(a.trial/'game-01/turn-001.json');per=[]
 for pl in initial['players']:
  pid=pl['id'];state=next((x for x in s['players'] if x['id']==pid),None);cities=[c for c in s['cities'] if c['player']==pid];b=bmap.get(pid,{'count':0,'charges':0});row={'player':pid,'leader':pl['leader'],'cities':len(cities),'population':sum(c['population'] for c in cities),'builders':b['count'],'builder_charges':b['charges'],'builders_per_city':b['count']/len(cities) if cities else None}
  for key,catalog in [('techs',tech),('civics',civic)]:
   known=(state or {}).get(key,[]);row[key+'_count']=len(known);row[key+'_furthest_era']=max((catalog[x] for x in known if x in catalog),key=lambda x:era[x],default=None)
  row['naval_tradition']=bool(state and 'CIVIC_NAVAL_TRADITION' in state['civics']);row['opera_ballet']=bool(state and 'CIVIC_OPERA_BALLET' in state['civics']);row['quarters']=next((x['completed'] for x in detail['players'] if x['player']==pid),{});per.append(row)
 result['players250']=per
 native=[];log=a.trial/'game-01/logs/AI_Victories.csv'
 if log.exists():
  for row in csv.reader(log.read_text(errors='replace').splitlines()):
   vals=[x.strip() for x in row]
   if len(vals)>=4 and vals[2].startswith('STRATEGY_CSC_AI_SERVICE_'):native.append({'turn':int(vals[0]),'player':int(vals[1]),'strategy':vals[2],'state':vals[3]})
 result['native_strategy_changes']=native
 write(a.trial/'comparison.json',result)
 lines=['# Medieval-start CSC research priorities experiment','','Online / Prince / Small Continents / vanilla Standard; seed830102/940104. Primary Service civic180, producer prerequisites120; material-aware RH-pattern native strategies. Quarter40/improvement80, improvement90 and Builder50 retained.','','Previous game started in Ancient; this game starts Medieval. Comparisons show outcomes under different starts.','','| Metric at250 | Previous Ancient | New Medieval |','|---|---:|---:|']
 groups=[result['comparisons']['250'][k] for k in ('previous_ancient','new_medieval')]
 for label,fn in [('Cities',lambda g:g['metrics']['totals']['cities']),('Population',lambda g:g['metrics']['population']),('Improved plots',lambda g:g['metrics']['owned_improved_plots']),('Improved plots/city',lambda g:round(g['metrics']['improved_plots_per_city'],2)),('Builders remaining',lambda g:g['builders']['alive']),('Builder charges',lambda g:g['builders']['charges']),('Quarters with sales',lambda g:str(g['sales']['completed_quarters_with_sales'])+'/'+str(g['sales']['completed_quarters'])),('Sales links',lambda g:g['sales']['links'])]:lines.append('| '+label+' | '+' | '.join(str(fn(g)) for g in groups)+' |')
 for q in ('BAKERS','TAILORS'):
  for label,key in [('completed','completed'),('Base access','base'),('both access','both'),('adjacent Base copies','base_plots'),('Base copies improved','base_plots_improved')]:lines.append('| '+q+' '+label+' | '+' | '.join(str(g['metrics']['quarters'][q].get(key,0)) for g in groups)+' |')
 lines+=['','Services at250: '+json.dumps(groups[1]['metrics']['service_source_cities']),'','| Player | Cities | Bakers | Tailors | Builders/city | Naval Tradition | Opera/Ballet |','|---|---:|---:|---:|---:|---|---|']
 for r in per:lines.append('| '+str(r['leader'])+' | '+str(r['cities'])+' | '+str(r['quarters'].get('BAKERS',0))+' | '+str(r['quarters'].get('TAILORS',0))+' | '+str(round(r['builders_per_city'],2) if r['builders_per_city'] is not None else '—')+' | '+str(r['naval_tradition'])+' | '+str(r['opera_ballet'])+' |')
 lines+=['','Resource replacement last-observed summary: '+json.dumps(result['resource_removal_summary']),'','## Limits','',*['- '+x for x in result['limits']]]
 (a.trial/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print('Medieval research report saved.')
if __name__=='__main__':main()
