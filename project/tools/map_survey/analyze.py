"""Count all eight Quarters' material geometry from complete native tile dumps."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
from statistics import mean

GROUPS=['vanilla-abundant','tar-abundant','tar-truly-abundant']
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def truth(value):return value is True or value==1
def write_csv(path,values):
    if not values:return
    fields=list(dict.fromkeys(k for row in values for k in row))
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(values)

def analyze_map(folder,definitions):
    data=read(folder/'map.json');settings=read(folder/'settings.json');plots={p['index']:p for p in data['plots']}
    resources={r['type']:r for r in data['resources']};features={f['type']:f for f in data['features']}
    harvests={r['resource'] for r in data['harvests']};resolved=json.loads(json.dumps(definitions))
    for q in ('BAKERS','TAILORS'):
        for kind in ('base','spec'):
            actual=sorted(t['type'] for t in data['material_tags'] if t['tag']==f'CLASS_CSC_{q}_{kind.upper()}' and t['type'] in resources)
            assert actual,(folder,q,kind)
            resolved[q][kind]['resources']=actual
    def matches(p,rule,resource_only=False):
        return bool(p.get('resource') in rule.get('resources',[]) or (not resource_only and ((rule.get('hills') and p['hills']) or p.get('feature') in rule.get('features',[]))))
    def ordinary_land(p):return not p['water'] and not p['impassable']
    def feature_clearable(p):
        f=p.get('feature')
        return not f or truth(features[f].get('removable')) or f in ('FEATURE_FLOODPLAINS','FEATURE_FLOODPLAINS_PLAINS','FEATURE_FLOODPLAINS_GRASSLAND')
    def clearable(p,mod_harvest=False):
        if p.get('district') or not feature_clearable(p):return False
        r=p.get('resource')
        return not r or resources[r]['class']=='RESOURCECLASS_BONUS' or (mod_harvest and r in harvests)
    rows=[];sites=[];union=set();common_union=set()
    for q,rules in resolved.items():
        v=Counter();candidate_ids=set();support_pairs=set()
        base_sources={i for i,p in plots.items() if matches(p,rules['base'])};spec_sources={i for i,p in plots.items() if matches(p,rules['spec'])}
        resource_base={i for i,p in plots.items() if matches(p,rules['base'],True)};resource_spec={i for i,p in plots.items() if matches(p,rules['spec'],True)}
        for i,p in plots.items():
            if not ordinary_land(p):continue
            ns=set(p['neighbors']);base=ns&base_sources;spec=ns&spec_sources
            v['base_only_or_both']+=bool(base);v['spec_only_or_both']+=bool(spec)
            if not base or not spec:continue
            v['land_both']+=1;union.add(i);candidate_ids.add(i)
            common=clearable(p);native_harvest=clearable(p,True)
            v['common_clearable_both']+=common;v['harvest_aware_both']+=native_harvest
            if common:common_union.add(i)
            distinct=any(a!=b for a in base for b in spec);v['distinct_source_tiles']+=distinct
            resource_both=bool(ns&resource_base) and bool(ns&resource_spec);v['resource_only_both']+=resource_both
            for a in base:
                for b in spec:support_pairs.add((a,b))
            sites.append({'group':settings['group'],'map':settings['map_number'],'quarter':q,'plot':i,'x':p['x'],'y':p['y'],'base_plots':';'.join(map(str,sorted(base))),'spec_plots':';'.join(map(str,sorted(spec))),'common_clearable':common,'harvest_aware_clearable':native_harvest,'distinct_sources':distinct,'resource_only':resource_both,'candidate_resource':p.get('resource'),'candidate_feature':p.get('feature')})
        remaining=set(candidate_ids);clusters=0
        while remaining:
            clusters+=1;todo=[remaining.pop()]
            while todo:
                near=set(plots[todo.pop()]['neighbors'])&remaining;remaining-=near;todo.extend(near)
        rows.append({'group':settings['group'],'map':settings['map_number'],'quarter':q,'base_source_tiles':len(base_sources),'spec_source_tiles':len(spec_sources),'land_both':v['land_both'],'common_clearable_both':v['common_clearable_both'],'harvest_aware_both':v['harvest_aware_both'],'resource_only_both':v['resource_only_both'],'terrain_feature_gain':v['land_both']-v['resource_only_both'],'distinct_source_tiles':v['distinct_source_tiles'],'connected_clusters':clusters,'supporting_pairs':len(support_pairs)})
    summary={'group':settings['group'],'map':settings['map_number'],'land_tiles':sum(not p['water'] for p in plots.values()),'passable_land_tiles':sum(ordinary_land(p) for p in plots.values()),'resource_tiles':sum(bool(p.get('resource')) for p in plots.values()),'land_resource_tiles':sum(bool(p.get('resource')) and not p['water'] for p in plots.values()),'any_quarter_both':len(union),'any_quarter_common_clearable':len(common_union),'resource_counts':dict(Counter(p['resource'] for p in plots.values() if p.get('resource'))),'resolved_definitions':resolved}
    gold_base={i for i,p in plots.items() if matches(p,resolved['GOLDSMITHS']['base'])}
    gold_spec={i for i,p in plots.items() if matches(p,resolved['GOLDSMITHS']['spec']) or p.get('resource')=='RESOURCE_PEARLS'}
    sensitivity=[p for p in plots.values() if ordinary_land(p) and set(p['neighbors'])&gold_base and set(p['neighbors'])&gold_spec]
    summary['goldsmiths_with_pearls_land_both']=len(sensitivity)
    summary['goldsmiths_with_pearls_common_clearable']=sum(clearable(p) for p in sensitivity)
    return rows,sites,summary

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);a=parser.parse_args()
    defs=read(a.output/'materials.json');rows=[];sites=[];maps=[]
    for group in GROUPS:
        for folder in sorted((a.output/group).glob('map-*')):
            if not (folder/'complete.json').exists():continue
            r,s,m=analyze_map(folder,defs);rows+=r;sites+=s;maps.append(m)
    write_csv(a.output/'quarter-opportunities.csv',rows);write_csv(a.output/'opportunity-sites.csv',sites)
    write_csv(a.output/'map-summary.csv',[{k:v for k,v in m.items() if k not in ('resource_counts','resolved_definitions')} for m in maps])
    averages=[]
    for q in defs:
        for group in GROUPS:
            rs=[r for r in rows if r['quarter']==q and r['group']==group]
            if rs:averages.append({'quarter':q,'group':group,'maps':len(rs),**{key:mean(r[key] for r in rs) for key in ('land_both','common_clearable_both','harvest_aware_both','resource_only_both','terrain_feature_gain')}})
    write_csv(a.output/'group-means.csv',averages)
    comparisons=[]
    for i in range(1,6):
        first=a.output/GROUPS[0]/f'map-{i:02d}'/'map.json'
        if not first.exists():continue
        base=read(first)['plots']
        for group in GROUPS[1:]:
            other=a.output/group/f'map-{i:02d}'/'map.json'
            if not other.exists():continue
            paired=read(other)['plots'];comparisons.append({'map':i,'group':group,'same_land_water':sum(p['water']==q['water'] for p,q in zip(base,paired)),'same_terrain':sum(p['terrain']==q['terrain'] for p,q in zip(base,paired)),'same_features':sum(p.get('feature')==q.get('feature') for p,q in zip(base,paired)),'same_resources':sum(p.get('resource')==q.get('resource') for p,q in zip(base,paired)),'plots':len(base)})
    write_csv(a.output/'paired-map-comparison.csv',comparisons)
    result={'maps':maps,'opportunities':rows,'group_means':averages,'paired_terrain_comparisons':comparisons}
    (a.output/'analysis.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    text=['# CSC map material opportunities','',f'{len(maps)} generated maps. Small Continents, six civilizations, nine city states, Online speed. Five fixed seed pairs and leader rosters are reused across resource setups. CSC is enabled throughout.','',
    'The main counts are distinct passable land tiles adjacent to at least one base-material source and at least one specialty-material source. They include all generated resources, including unrevealed strategics, and apply no ownership or city-reach filter. Terrain and feature materials count where the individual Quarter design specifies them. No improvements or future research are granted.','',
    'A single neighboring tile can satisfy both classes when its terrain and resource match different classes. The CSV separately counts sites with two distinct supporting tiles. Neighboring candidate sites may share the same material sources; these are tile opportunities, not independent settlements.','']
    labels={'vanilla-abundant':'Vanilla Abundant with CSC','tar-abundant':'TAR enabled with Abundant','tar-truly-abundant':'TAR enabled with Truly Abundant'}
    for group in GROUPS:
        text+=['## '+labels[group],'','| Quarter | Map 1 | Map 2 | Map 3 | Map 4 | Map 5 | Mean |','|---|---:|---:|---:|---:|---:|---:|']
        for q in defs:
            rs={r['map']:r for r in rows if r['quarter']==q and r['group']==group};vals=[str(rs[i]['land_both']) if i in rs else 'pending' for i in range(1,6)]
            text.append('| '+q.title()+' | '+' | '.join(vals)+' | '+(f'{mean(r["land_both"] for r in rs.values()):.1f}' if rs else 'pending')+' |')
        text+=['']
    text+=['## Sites with ordinary placement blockers removed','','The common clearable-site comparison excludes existing districts, nonremovable features other than Gathering Storm floodplains, and tiles carrying luxury or strategic resources. It allows bonus-resource removal and normal feature clearing after research. This common filter is the same for every group. The harvest-aware CSV additionally permits resources that the loaded rules make harvestable; TAR adds luxury and strategic harvesting. Neither filter is a complete native city-specific district eligibility test.','',
    '| Quarter | Vanilla Abundant mean | TAR Abundant mean | TAR Truly Abundant mean |','|---|---:|---:|---:|']
    for q in defs:
        vals=[next((f'{r["common_clearable_both"]:.1f}' for r in averages if r['quarter']==q and r['group']==g),'pending') for g in GROUPS]
        text.append('| '+q.title()+' | '+' | '.join(vals)+' |')
    text+=['','## Material definitions','','Bakers and Tailors use their actual loaded CSC resource tags. The six other Quarters use their individual design pages rather than incomplete SQL stubs. Carpenters use Woods/Rainforest, Copper and Iron as base materials and Aluminium, Amber, Dyes, Silk and Silver as specialty materials. Stonemasons and Blacksmiths include Hills as base material. Goldsmiths use Diamonds and Jade from their individual page; the overview additionally lists Pearls, so a Pearls-inclusive sensitivity count is retained separately.','',
    'The material JSON and resolved definitions in analysis.json list every resource identifier. Source hashes, full native tile dumps, save files, settings and command transcripts remain with the raw evidence. No AI tuning was applied.']
    (a.output/'report.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(f'Analyzed {len(maps)} maps and {len(rows)} Quarter-map combinations')

if __name__=='__main__':main()
