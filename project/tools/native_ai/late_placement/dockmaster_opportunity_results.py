"""Summarize read-only coast captures without multiplying overlapping layouts.

BASE paths are broad map geometry; PAIR rows add actual player/city/native
constraints. Extended captures include ordinary Harbor Gold and its best current
legal alternative. Unknown quality in older captures remains unknown.
"""
import argparse
import json
from pathlib import Path
import re


def analyse(path):
    rows={}
    for kind,payload in re.findall(r'CSC_COAST_([A-Z_]+)\t([^\r\n]*)',Path(path).read_text(encoding='utf-8-sig',errors='replace').replace('\0','')):
        rows.setdefault(kind,[]).append(payload.split('\t'))
    plots={int(r[0]):dict(x=int(r[1]),y=int(r[2]),water=r[5]=='true',lake=r[6]=='true',
        impassable=r[7]=='true',owner=int(r[8]),city=int(r[9]),district=r[10],resource=r[11])for r in rows.get('MAP',[])}
    if not plots or not rows.get('END')or not rows.get('META'):
        raise ValueError('Require a complete coast capture with physical map rows and clock markers')
    width=max(p['x']for p in plots.values())+1;height=max(p['y']for p in plots.values())+1
    if len(plots)!=width*height or rows['META'][0][0]!=rows['END'][-1][0]:
        raise ValueError('Incomplete map or inconsistent survey clocks')
    harbors={'DISTRICT_HARBOR'}
    for row in rows.get('PAIR',[]):
        if row[18]=='true'and int(row[16])in plots:harbors.add(plots[int(row[16])]['district'])
    layouts={};usable_resources=set()
    for row in rows.get('BASE',[]):
        material=int(row[0]);m=plots.get(material)
        if not m or m['district']!='NONE':continue
        for value in row[6].split(','):
            if not value:continue
            q,h=map(int,value.split(':'));quarter,harbor=plots.get(q),plots.get(h)
            if not quarter or not harbor:continue
            if (quarter['water']or quarter['impassable']or quarter['resource']!='NONE'
                or quarter['district']not in('NONE','DISTRICT_CSC_TAILORS_QUARTER')):continue
            if (not harbor['water']or harbor['lake']or harbor['impassable']
                or harbor['resource']!='NONE'or harbor['district']not in harbors|{'NONE'}):continue
            layouts.setdefault((q,h),set()).add(material);usable_resources.add(material)
    # Group resources sharing a usable Quarter footprint. A coast deposit may
    # support several Quarter/Harbor pairs; do not call each a separate cluster.
    parents={i:i for i in usable_resources}
    def find(i):
        while parents[i]!=i:parents[i]=parents[parents[i]];i=parents[i]
        return i
    by_quarter={}
    for(q,h),materials in layouts.items():by_quarter.setdefault(q,set()).update(materials)
    for materials in by_quarter.values():
        ordered=sorted(materials)
        for i in ordered[1:]:parents[find(i)]=find(ordered[0])
    pairs={}
    for row in rows.get('PAIR',[]):
        hplot=int(row[16]);h=plots.get(hplot)
        if h and h['lake']:continue
        record=dict(player=int(row[0]),city=int(row[1]),quarterPlot=int(row[2]),
            quarterOwned=row[3]=='true',quarterExists=row[4]=='true',quarterGeometry=row[5]=='true',
            quarterLegal=row[6]=='true',base=int(row[7]),spec=int(row[8]),basePlots=row[9],
            quarterForecastAdjacency=float(row[13]),harborCity=int(row[14]),harborPlot=hplot,
            harborOwner=int(row[17]),harborExists=row[18]=='true',harborLegal=row[19]=='true',
            lighthouseWorks=row[20]=='true')
        for index,key in ((21,'harborGold'),(22,'bestLegalHarborGold')):
            try:record[key]=float(row[index])
            except(IndexError,ValueError):record[key]=None
        pairs[(record['player'],record['quarterPlot'],hplot)]=record
    practical=[r for r in pairs.values()if r['quarterGeometry']and r['quarterOwned']and r['harborOwner']==r['player']]
    ready=[r for r in practical if(r['quarterExists']or r['quarterLegal'])and(r['harborExists']or r['harborLegal'])]
    comparable=[r for r in practical if r['harborGold']is not None and r['bestLegalHarborGold']is not None]
    summary=dict(raw_base_deposits=len(rows.get('BASE',[])),
        resource_free_sea_layouts=len(layouts),quarter_footprints=len(by_quarter),
        usable_coastal_base_deposits=len(usable_resources),coastal_material_clusters=len({find(i)for i in parents}),
        player_city_native_pairs=len(pairs),owned_geometry_pairs=len(practical),currently_admitted_pairs=len(ready),
        owned_harbor_quality_known=sum(r['harborGold']is not None for r in practical),
        owned_harbor_gold_at_least2=(sum(r['harborGold']is not None and r['harborGold']>=2 for r in practical)
            if any(r['harborGold']is not None for r in practical)else None),
        owned_pairs_matching_best_harbor=(sum(r['harborGold']>=r['bestLegalHarborGold']for r in comparable)if comparable else None),
        existing_quarter_harbor_pairs=sum(r['quarterExists']and r['harborExists']for r in practical))
    return dict(schema='csc-dockmaster-opportunities-v1',source=str(path),summary=summary,
        layouts=[dict(quarter=q,harbor=h,basePlots=sorted(materials))for(q,h),materials in sorted(layouts.items())],
        native_pairs=list(pairs.values()),scope='Late-world free geometry and current native opportunities; not original map or promised future builds.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--survey',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=analyse(args.survey)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result['summary'],indent=2))
