"""Count distinct both-material sites separately from repeated decisions."""
import argparse
import json
from pathlib import Path
from analyze import read, distance, rows, output_csv

def count(folder):
    snapshots=[read(path) for path in sorted(folder.glob('turn-*.json'))]
    first=snapshots[0];final=snapshots[-1];w=first['width'];h=first['height']
    known={};confirmed={q:set() for q in first['quarters']};placement_options={q:set() for q in first['quarters']}
    census=folder.parent/'map-census'/folder.name/'map.json'
    if census.exists():known={p['index']:p for p in read(census)['plots']}
    observations={q:[] for q in first['quarters']}
    for s in snapshots:
        for p in s['plots']:known.setdefault(p['index'],p)
        for o in s['options']:
            for site in rows(o['sites']):
                if site['base'] and site['spec']:confirmed[o['quarter']].add(site['plot']);observations[o['quarter']].append((s['turn'],o['player'],o['city'],site['plot']))
    seen=set();majors={p['id'] for p in first['players']}
    for e in final['events']:
        if not e.get('quarter'):continue
        identity=(e['plot'],e['district'])
        if identity in seen:continue
        seen.add(identity)
        if e['player'] not in majors:continue
        q=e['quarter'];cache=e.get('previous_candidates') or {}
        if e['turn']-cache.get('turn',-100)>1:continue
        for site in rows(cache.get('sites')):
            if site['base'] and site['spec']:confirmed[q].add(site['plot']);placement_options[q].add(site['plot']);observations[q].append((e['turn'],e['player'],e['city'],site['plot']))
    result=[];details=[]
    for q,classes in first['quarters'].items():
        base=[p for p in first['plots'] if p.get('resource') in classes['base']]
        spec=[p for p in first['plots'] if p.get('resource') in classes['spec']]
        sites=[]
        for index in range(w*h):
            p={'index':index,'x':index%w,'y':index//w}
            bs=[r for r in base if distance(p,r,w)==1]
            if not bs:continue
            sp=[r for r in spec if distance(p,r,w)==1]
            if not sp:continue
            k=known.get(index,{})
            terrain=k.get('terrain');feature=k.get('feature')
            category='unknown' if not terrain else 'water' if terrain in ('TERRAIN_COAST','TERRAIN_OCEAN') else 'mountain' if 'MOUNTAIN' in terrain else 'land'
            d={'game':folder.name,'quarter':q,'plot':index,'x':p['x'],'y':p['y'],'terrain_category':category,'terrain':terrain,'feature':feature,'resource':k.get('resource'),'initial_district':next((r.get('district') for r in first['plots'] if r['index']==index),None),'base_plots':';'.join(str(r['index']) for r in bs),'spec_plots':';'.join(str(r['index']) for r in sp),'ever_confirmed_owned_native_legal':index in confirmed[q],'confirmed_at_placement_decision':index in placement_options[q]}
            details.append(d);sites.append(d)
        result.append({'game':folder.name,'quarter':q,'initial_resource_geometry_sites':len(sites),'known_land_sites':sum(d['terrain_category']=='land' for d in sites),'known_water_sites':sum(d['terrain_category']=='water' for d in sites),'known_mountain_sites':sum(d['terrain_category']=='mountain' for d in sites),'unknown_terrain_sites':sum(d['terrain_category']=='unknown' for d in sites),'distinct_confirmed_owned_native_legal_sites':len(confirmed[q]),'distinct_sites_at_placement_decisions':len(placement_options[q]),'distinct_city_owner_combinations_observed':len({(pid,cid) for _,pid,cid,_ in observations[q]}),'confirmed_plots':sorted(confirmed[q]),'placement_option_plots':sorted(placement_options[q])})
    return result,details

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--games',type=int,nargs='+',default=[1,2]);a=p.parse_args()
    results=[];details=[]
    for i in a.games:
        r,d=count(a.output/f'game-{i:02d}');results+=r;details+=d
    (a.output/'map-opportunities.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    output_csv(a.output/'map-opportunity-sites.csv',details)
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
