"""Paired offline abundance study: actual stock/TAR Lua, then CSC's Lua helper.

Ten instances per setup = two resource seeds on each of five captured landscapes.
No Civ control, new native terrain, native RNG or starting-position adjustment.
"""
import argparse
import copy
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import statistics
import sys
import time
from offline import OfflineWorld, read, write
from automatic_assist import list_fields
from continent_analysis import continent_census
from build import render
from analyze import write_csv

ROOT=Path(__file__).resolve().parents[3]
SCRIPTS=ROOT/'Civ Supply Chains/Lua_UI/MapGeneration'
CONFIGS=[('vanilla-sparse','Vanilla · Sparse','stock',1,30),('vanilla-standard','Vanilla · Standard','stock',2,30),('vanilla-abundant','Vanilla · Abundant','stock',3,30),('tar-sparse','TAR · Sparse','tar',1,29),('tar-standard','TAR · Standard','tar',2,29),('tar-abundant','TAR · Abundant','tar',3,29),('tar-plentiful','TAR · Plentiful','tar',25,29),('tar-truly-abundant','TAR · Truly Abundant','tar',45,29)]
RULE_TABLES=('Resources','TypeTags','Features','Resource_ValidTerrains','Resource_ValidFeatures','Resource_Harvests','Resource_Distribution','Resource_SeaLuxuries','Resource_SeaStrategics')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def freeze_profile(source,target,tar):
    target.parent.mkdir(parents=True,exist_ok=True)
    s=sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True)
    # These profile signatures distinguish the actual native rule captures.
    assert bool(s.execute("SELECT 1 FROM Resource_ValidTerrains WHERE ResourceType='RESOURCE_FURS' AND TerrainType='TERRAIN_GRASS'").fetchone())==tar
    assert s.execute("SELECT COUNT(*) FROM TypeTags WHERE Tag LIKE 'CLASS_CSC_%'").fetchone()[0]==59
    if tar:assert s.execute("SELECT Value FROM GlobalParameters WHERE Name='CSC_MATERIAL_MAP_STANDARD_DENSITY'").fetchone()[0]=='29'
    t=sqlite3.connect(target);s.backup(t);t.close();s.close()
    return {'source':str(source),'source_sha256':sha(source),'frozen':str(target),'frozen_sha256':sha(target),'tar':tar}


def plan_world(w,before,seed,setting,standard):
    l=w.lua
    for name in ('CSC_MaterialMapCore','CSC_MaterialMapDefinitions'):
        l.execute((SCRIPTS/(name+'.lua')).read_text(encoding='utf-8'))
    definitions=json.loads(l.globals().CSC_MaterialMapCore.Json(l.globals().CSC_MaterialMapDefinitions.Resolve()))
    # Eligibility uses the same emulator as resource generation. Preserve the
    # captured starts at helper time; no claim these are regenerated native starts.
    starts=set(before.get('starting_plots',[]));eligible={};checks=0
    rows={r['ResourceType']:r for r in w.tables['Resources']}
    mapped=sorted({r for q in definitions.values() for kind in ('base','spec') for r in q[kind]['resources'] if r in rows and rows[r]['Frequency']>0})
    for r in mapped:
        allowed={};index=rows[r]['Index']
        for p in before['plots']:
            if p['water'] or p['impassable'] or p.get('resource') or p.get('district') or p['index'] in starts:continue
            checks+=1
            if l.globals().ResourceBuilder.CanHaveResource(l.globals().Map.GetPlotByIndex(p['index']),index):allowed[p['index']]=True
        eligible[r]=allowed
    profile=l.globals().CSC_MaterialMapCore.ResourceProfile(setting,standard)
    raw=l.globals().CSC_MaterialMapCore.Plan(l.table_from(before,recursive=True),l.table_from(definitions,recursive=True),l.table_from(eligible,recursive=True),seed,profile)
    plan=list_fields(json.loads(l.globals().CSC_MaterialMapCore.Json(raw)))
    after=copy.deepcopy(before)
    for a in plan['additions']:
        p=after['plots'][a['plot']];assert not p.get('resource') and eligible[a['resource']].get(a['plot'])
        p['resource']=a['resource']
    assert all(not p.get('resource') or after['plots'][i].get('resource')==p['resource'] for i,p in enumerate(before['plots']))
    assert len(plan['additions'])<=plan['max_per_map']
    for cid in {a['continent'] for a in plan['additions']}:assert sum(a['continent']==cid for a in plan['additions'])<=plan['max_per_continent']
    prior=continent_census(before,definitions);census=continent_census(after,definitions)
    for row in plan['coverage']:
        b=next(q for c in prior if c['id']==row['continent'] for q in c['quarters'] if q['quarter']==row['quarter'])
        a=next(q for c in census if c['id']==row['continent'] for q in c['quarters'] if q['quarter']==row['quarter'])
        assert (row['base_before'],row['both_before'],row['base_after'],row['both_after'])==(b['common_clearable_base'],b['common_clearable_both'],a['common_clearable_base'],a['common_clearable_both'])
        assert not row['base_before'] or row['base_after'];assert not row['both_before'] or row['both_after']
    return plan,after,definitions,prior,census,checks


def summarize(entries,out):
    quarters=entries[0]['definitions'];rows=[];maps=[];continents=[]
    for m in entries:
        before=m['assistance']['before_continents'];after=m['continents'];classes={r['type']:r['class'] for r in m['data']['resources']}
        additions=m['assistance']['additions'];added={a['plot'] for a in additions}
        counts=Counter(classes[p['resource']] for p in m['data']['plots'] if p.get('resource'))
        old_counts=Counter(classes[p['resource']] for p in m['data']['plots'] if p.get('resource') and p['index'] not in added)
        maps.append({'setup':m['study']['setup'],'instance':m['number'],'landscape':m['study']['landscape'],'replicate':m['study']['replicate'],'additions':len(additions),'resource_tiles_before':sum(old_counts.values()),'resource_tiles_after':sum(counts.values()),'luxury_tiles_before':old_counts['RESOURCECLASS_LUXURY'],'strategic_tiles_before':old_counts['RESOURCECLASS_STRATEGIC'],'bonus_tiles_before':old_counts['RESOURCECLASS_BONUS'],'land_luxury_types_before':before[0]['land_luxury_types'],'land_luxury_types_after':after[0]['land_luxury_types'],'attempts_added':sum(a['outcome']=='added' for a in m['assistance']['attempts']),'attempts_infeasible':sum(a['outcome']=='no safe feasible repair within budget' for a in m['assistance']['attempts'])})
        for c in after:
            if c['id']==-1:continue
            b=next(x for x in before if x['id']==c['id'])
            for q in c['quarters']:
                old=next(x for x in b['quarters'] if x['quarter']==q['quarter'])
                continents.append({'setup':m['study']['setup'],'instance':m['number'],'landscape':m['study']['landscape'],'replicate':m['study']['replicate'],'continent':c['id'],'quarter':q['quarter'],'base_before':old['common_clearable_base'],'base_after':q['common_clearable_base'],'both_before':old['common_clearable_both'],'both_after':q['common_clearable_both'],'clusters_before':old['common_clearable_both_clusters'],'clusters_after':q['common_clearable_both_clusters'],'luxury_types_before':b['land_luxury_types'],'luxury_types_after':c['land_luxury_types']})
    for setup,label,*_ in CONFIGS:
        selected=[m for m in entries if m['study']['setup']==setup]
        for q in quarters:
            subset=[r for r in continents if r['setup']==setup and r['quarter']==q]
            row={'setup':setup,'label':label,'quarter':q,'instances':len(selected),'continents':len(subset)}
            for mode in ('base','both'):
                for when in ('before','after'):
                    row[f'{mode}_{when}_covered']=sum(r[f'{mode}_{when}']>0 for r in subset)
                    row[f'{mode}_{when}_sites']=sum(r[f'{mode}_{when}'] for r in subset)
            for when in ('before','after'):row[f'clusters_{when}']=sum(r[f'clusters_{when}'] for r in subset)
            if selected:row['target_covered']=len(subset)*selected[0]['assistance']['abundance']['targets'][q]
            rows.append(row)
    write_csv(out/'coverage.csv',rows);write_csv(out/'map-stats.csv',maps);write_csv(out/'continent-stats.csv',continents)
    write(out/'analysis.json',{'instances':len(entries),'independent_landscapes':5,'resource_replicates_per_landscape':2,'coverage':rows,'maps':maps,'native':False})
    return rows


def run(a):
    a.output.mkdir(parents=True,exist_ok=True)
    profile_meta=[]
    for name,src,tar in [('stock',a.stock_database,False),('tar',a.tar_database,True)]:
        target=a.output/'profiles'/(name+'.sqlite')
        if not target.exists():meta=freeze_profile(src,target,tar);write(target.with_suffix('.json'),meta)
        else:meta=read(target.with_suffix('.json'));assert sha(target)==meta['frozen_sha256']
        profile_meta.append(meta)
    # Resource class mappings must describe the same CSC setup in both captures.
    conns=[sqlite3.connect(a.output/'profiles'/(name+'.sqlite')) for name in ('stock','tar')]
    tags=[c.execute("SELECT Type,Tag FROM TypeTags WHERE Tag LIKE 'CLASS_CSC_%' ORDER BY Type,Tag").fetchall() for c in conns]
    assert tags[0]==tags[1]
    for c in conns:c.close()
    source_bundle=read(a.bundle);landscapes=[next(m for m in source_bundle['maps'] if m['id']==f'luxuries-4-{i}') for i in range(1,6)]
    for source in landscapes:
        debug=read(a.native_fixtures/'csc-helper-lua'/f"map-{source['number']:02d}"/'automatic-debug.json')
        assert all(p['terrain']==q['terrain'] and p.get('feature')==q.get('feature') and p['neighbors']==q['neighbors'] for p,q in zip(source['data']['plots'],debug['before']['plots']))
        source['data']['starting_plots']=debug['starting_plots'];assert len(debug['starting_plots'])==15
    locked={str(p):sha(p) for p in SCRIPTS.glob('*.lua')}
    for p in [a.game_root/'DLC/Expansion2/Maps/Utility/ResourceGenerator.lua',a.workshop_root/'901009089/Utility/ResourceGenerator.lua',Path(__file__),Path(__file__).with_name('offline.py'),Path(__file__).with_name('world.lua')]:locked[str(p)]=sha(p)
    if (a.output/'sources.json').exists():assert read(a.output/'sources.json')==locked,'Study source changed; use a new output directory'
    else:write(a.output/'sources.json',locked)
    entries=[];started=time.monotonic()
    for setup,label,generator,setting,standard in CONFIGS:
        for number in range(1,11):
            folder=a.output/setup/f'instance-{number:02d}';path=folder/'viewer-map.json'
            if (folder/'complete.json').exists():entries.append(read(path));continue
            source=landscapes[(number-1)%5];replicate=(number-1)//5+1;seed=source['settings']['map_seed']+(replicate-1)*1000003
            t=time.monotonic();w=OfflineWorld(source['data'],a.output/'profiles'/(generator+'.sqlite'),a.game_root,a.workshop_root,seed,setting,a.lua_dependencies)
            before=w.run(generator,4,False,True)
            plan,after,definitions,prior,census,checks=plan_world(w,before,seed,setting,standard)
            group='abundance-offline-'+setup
            entry={'id':f'{group}-{number}','group':group,'groupLabel':'Offline abundance · '+label,'number':number,'settings':{'map_seed':source['settings']['map_seed'],'resource_seed':seed,'helper_seed':seed,'resource_setting':setting,'speed':'OFFLINE','tar':generator=='tar','csc':True},'data':after,'definitions':definitions,'continents':census,'reference':census[0]['quarters'],
                'study':{'kind':'abundance','native':False,'setup':setup,'landscape':source['number'],'replicate':replicate,'source_id':source['id']},
                'assistance':{'seed':seed,'additions':plan['additions'],'attempts':plan['attempts'],'palettes':plan['palettes'],'before_continents':prior,'abundance':plan['abundance']},
                'provenance':{'native':False,'kind':'offline-abundance','seed':seed,'warning':'OFFLINE APPROXIMATION: actual resource Lua and CSC planner on captured native terrain. Python MT19937 resource RNG; emulated eligibility/sorting; no native starting-position adjustment. Two resource seeds per landscape, not ten independent terrains. Captured starts protected during helper placement.','database_sha256':sha(a.output/'profiles'/(generator+'.sqlite')),'source_map_sha256':source.get('source_sha256'),'eligibility_checks':checks,'seconds':round(time.monotonic()-t,3)}}
            write(folder/'before.json',before);write(folder/'map.json',after);write(folder/'audit.json',plan);write(path,entry)
            (folder/'lua.log').write_text('\n'.join(w.logs)+'\n',encoding='utf-8')
            write(folder/'complete.json',{'passed':True,'native':False,'seconds':entry['provenance']['seconds'],'deposits':len(plan['additions'])})
            entries.append(entry);print(f'{len(entries)}/80 {label} instance {number}: {len(plan["additions"])} additions, {time.monotonic()-t:.1f}s',flush=True)
            if a.first_only:break
        if a.first_only:break
    assert all(sha(Path(p))==h for p,h in locked.items())
    rows=summarize(entries,a.output)
    bundle={'version':2,'title':'CSC offline abundance study','maps':entries,'default_group':entries[0]['group'],'study_summary':rows}
    (a.output/'maps.json').write_text(json.dumps(bundle,separators=(',',':')),encoding='utf-8');render(bundle,a.output/'viewer.html')
    write(a.output/'validation.json',{'passed':True,'instances':len(entries),'expected_instances':80,'all_sources_unchanged':True,'rule_profiles':profile_meta,'seconds':round(time.monotonic()-started,3),'native':False})
    print(json.dumps({'instances':len(entries),'viewer':str(a.output/'viewer.html'),'seconds':round(time.monotonic()-started,2)}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('output','bundle','stock-database','tar-database','game-root','workshop-root','lua-dependencies','native-fixtures'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--first-only',action='store_true')
    run(p.parse_args())
