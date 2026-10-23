"""Read-only reconstruction of external CSC sales links at archived checkpoints.

Counts matching functioning producer/customer building pairs, not payment events.
No resource or Service-civic requirement is imposed on ordinary goods sales.
"""
import argparse,json,sqlite3
from collections import Counter
from pathlib import Path

ROUTES=[
 ('Wind Mill → Granary','BAKERS','BUILDING_CSC_BAKERS_WIND_MILL','DISTRICT_CITY_CENTER','BUILDING_GRANARY',2),
 ('Water Mill → Granary','BAKERS','BUILDING_CSC_BAKERS_WATER_MILL','DISTRICT_CITY_CENTER','BUILDING_GRANARY',2),
 ('Bakery → Market','BAKERS','BUILDING_CSC_BAKERS_BAKERY','DISTRICT_COMMERCIAL_HUB','BUILDING_MARKET',3),
 ('Café → Zoo','BAKERS','BUILDING_CSC_BAKERS_CAFE','DISTRICT_ENTERTAINMENT_COMPLEX','BUILDING_ZOO',4),
 ('Café → Ferris Wheel','BAKERS','BUILDING_CSC_BAKERS_CAFE','DISTRICT_WATER_ENTERTAINMENT_COMPLEX','BUILDING_FERRIS_WHEEL',4),
 ('Textile Workshop → Lighthouse','TAILORS','BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP','DISTRICT_HARBOR','BUILDING_LIGHTHOUSE',2),
 ('Tailor → Market','TAILORS','BUILDING_CSC_TAILORS_TAILOR','DISTRICT_COMMERCIAL_HUB','BUILDING_MARKET',3),
 ('Tailor → Temple','TAILORS','BUILDING_CSC_TAILORS_TAILOR','DISTRICT_HOLY_SITE','BUILDING_TEMPLE',3),
 ('Fashion House → Amphitheater','TAILORS','BUILDING_CSC_TAILORS_FASHION_HOUSE','DISTRICT_THEATER','BUILDING_AMPHITHEATER',4),
 ('Fashion House → Bolshoi','TAILORS','BUILDING_CSC_TAILORS_FASHION_HOUSE','DISTRICT_WONDER','BUILDING_BOLSHOI_THEATRE',4),
 ('Fashion House → Broadway','TAILORS','BUILDING_CSC_TAILORS_FASHION_HOUSE','DISTRICT_WONDER','BUILDING_BROADWAY',4),
 ('Fashion House → Sydney Opera House','TAILORS','BUILDING_CSC_TAILORS_FASHION_HOUSE','DISTRICT_WONDER','BUILDING_SYDNEY_OPERA_HOUSE',4),
]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def analyze(folder,turn,df,bf):
 s=read(folder/f'turn-{turn:03d}.json');world=read(folder/'initial-map.json');neighbors={x['index']:set(x['neighbors']) for x in world['plots']}
 cities=s['cities'];districts={d['plot']:(c,d) for c in cities for d in c['districts']};rows=[];quarters={}
 for c in cities:
  for d in c['districts']:
   if d.get('quarter') and d['complete']:quarters[(c['player'],d['plot'])]={'player':c['player'],'city':c['name'],'quarter':d['quarter'],'plot':d['plot'],'base':d['site']['base']>0,'links':0,'routes':set()}
 for name,q,source,customer_district,customer_building,stage in ROUTES:
  sellers=[];customer_sites=[];district_sites=[]
  for c in cities:
   for d in c['districts']:
    # A City Center pillage flag can refer to defenses; use Granary building state.
    if not d['complete'] or (d['pillaged'] and d['type']!='DISTRICT_CITY_CENTER'):continue
    if d.get('quarter')==q and any(b['type'] in bf.get(source,{source}) and not b['pillaged'] and b['plot']==d['plot'] for b in c['buildings']):sellers.append((c,d))
    if d['type'] in df.get(customer_district,{customer_district}) and (stage<4 or c['population']>=5):
     district_sites.append((c,d))
     for b in c['buildings']:
      if b['type'] in bf.get(customer_building,{customer_building}) and not b['pillaged'] and b['plot']==d['plot']:customer_sites.append((c,d));break
  adjacent_district=sum(any(cc['player']==c['player'] and dd['plot'] in neighbors[d['plot']] for cc,dd in district_sites) for c,d in sellers)
  links=[];selling=set();without_base=set();with_base=set();cross_city=0
  for c,d in sellers:
   for cc,dd in customer_sites:
    if c['player']==cc['player'] and dd['plot'] in neighbors[d['plot']]:
     ident=(c['player'],d['plot']);selling.add(ident)
     (with_base if d['site']['base'] else without_base).add(ident)
     cross_city+=c['id']!=cc['id']
     links.append({'player':c['player'],'seller_city':c['name'],'seller_plot':d['plot'],'customer_city':cc['name'],'customer_plot':dd['plot'],'customer_population':cc['population']})
     quarters[ident]['links']+=1;quarters[ident]['routes'].add(name)
  rows.append({'route':name,'quarter':q,'stage':stage,'producers':len(sellers),'producers_selling':len(selling),'links':len(links),'customer_sites':len(customer_sites),'producers_adjacent_customer_district':adjacent_district,'without_base_selling':len(without_base),'with_base_selling':len(with_base),'cross_city_links':cross_city,'detail':links})
 for x in quarters.values():x['routes']=sorted(x['routes'])
 return {'folder':str(folder),'turn':turn,'cities':len(cities),'routes':rows,'quarters':list(quarters.values()),'services':dict(Counter(k for c in cities for k,v in c['properties'].items() if v>0))}
def aggregate(games):
 result={}
 for name,*_ in ROUTES:
  rows=[r for g in games for r in g['routes'] if r['route']==name]
  result[name]={k:sum(r[k] for r in rows) for k in ('producers','producers_selling','links','customer_sites','producers_adjacent_customer_district','without_base_selling','with_base_selling','cross_city_links')}
 qrows=[x for g in games for x in g['quarters']];q={}
 for quarter in ('BAKERS','TAILORS'):
  rows=[r for r in qrows if r['quarter']==quarter];q[quarter]={'completed':len(rows),'with_sales':sum(r['links']>0 for r in rows),'without_base':sum(not r['base'] for r in rows),'without_base_with_sales':sum(not r['base'] and r['links']>0 for r in rows),'with_base':sum(r['base'] for r in rows),'with_base_with_sales':sum(r['base'] and r['links']>0 for r in rows)}
 return {'games':len(games),'cities':sum(g['cities'] for g in games),'routes':result,'quarters':q,'links':sum(x['links'] for x in result.values()),'completed_quarters_with_sales':sum(x['links']>0 for x in qrows),'completed_quarters':len(qrows)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--desktop',type=Path,required=True);p.add_argument('--database',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 db=sqlite3.connect(a.database.as_uri()+'?mode=ro',uri=True);df={};bf={}
 for table,orig,variant,target in [('DistrictReplaces','ReplacesDistrictType','CivUniqueDistrictType',df),('BuildingReplaces','ReplacesBuildingType','CivUniqueBuildingType',bf)]:
  for base,new in db.execute(f'SELECT {orig},{variant} FROM {table}'):target.setdefault(base,{base}).add(new)
 db.close();base=a.desktop/'csc-ai-paired-standard-20261016'
 groups={'Vanilla baseline':[(base/f'game-{i:02d}',250) for i in range(1,6)],'TAR baseline':[(base/f'game-{i:02d}',250) for i in range(6,11)],'Placement v1':[(a.desktop/'csc-ai-placement-v1-20261017/trial/game-01',250)],'Native bonus/river v3':[(a.desktop/'csc-ai-native-bonus-river-20261017/retry-01/game-01',250)],'Density v4 / Builder900':[(a.desktop/'csc-ai-density-v4-20261017/trial/game-01',250)]}
 data={name:[analyze(f,t,df,bf) for f,t in paths] for name,paths in groups.items()};summary={name:aggregate(g) for name,g in data.items()};summary['All10 baseline']=aggregate(data['Vanilla baseline']+data['TAR baseline'])
 result={'basis':'Functioning same-owner adjacent building-pair relationships at250, reconstructed from checkpoints; not individually logged payments or cumulative transaction counts. No material or Service-civic gate for ordinary sales. Stage4 requires customer population>=5. CityCenter defense pillage flag ignored for Granary; building pillage respected. One-level native district/building replacements included.','summary':summary,'games':data}
 a.output.mkdir(parents=True,exist_ok=True);(a.output/'sales.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 cols=['All10 baseline','Placement v1','Native bonus/river v3','Density v4 / Builder900'];lines=['# CSC historical sales relationships','',result['basis'],'', 'Ten baseline games (five vanillaStandard, fiveTARStandard), plus three completed250-turn tuning games. AllOnline. Earlier400-turn maps and incomplete runs excluded from this comparison.','', 'Entries are producers selling / functioning producers, followed by number of distinct producer-customer links in parentheses.','', '| Route | 10 baseline games | Placement v1 | Native v3 | Density v4 |','|---|---:|---:|---:|---:|']
 for route,*_ in ROUTES:lines.append('| '+route+' | '+' | '.join(f"{summary[col]['routes'][route]['producers_selling']}/{summary[col]['routes'][route]['producers']} ({summary[col]['routes'][route]['links']})" for col in cols)+' |')
 lines+=['', '## Quarter coverage','', '| Group | Completed Quarters selling | Links |','|---|---:|---:|']
 for name in ['Vanilla baseline','TAR baseline',*cols[1:]]:
  x=summary[name];lines.append(f"| {name} | {x['completed_quarters_with_sales']}/{x['completed_quarters']} | {x['links']} |")
 lines+=['', 'Resource support is not required for these sales; material access instead enables additional extraction interactions and Services. Counts establish structural eligibility; actual applied economic-yield/payment amounts were not recorded in these censuses. Detailed per-game and per-link results in sales.json.']
 (a.output/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 print(json.dumps({'summary':summary}))
if __name__=='__main__':main()
