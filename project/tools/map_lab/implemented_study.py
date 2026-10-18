"""Fifteen native maps: implemented Quarters only, three vanilla resource levels.

FireTuner configures games and reads the automatically executed CSC pass. No
controller-side planner or resource writes. Includes actual native quantities.
"""
import argparse
import copy
from collections import Counter
import json
from pathlib import Path
import re
import traceback
from automatic_assist import AutomaticSurvey, list_fields, ROOT
from assist import read
from native_assist import write,sha
from offline import lua_runtime
from continent_analysis import continent_census
from analyze import write_csv
from build import render

GROUPS=[('implemented-vanilla-sparse','Vanilla Sparse',1),('implemented-vanilla-standard','Vanilla Standard',2),('implemented-vanilla-abundant','Vanilla Abundant',3)]
SCOPE={'BAKERS','TAILORS'}


class ImplementedSurvey(AutomaticSurvey):
    def assist_current(self,folder):
        after=read(folder/'map.json');settings=read(folder/'settings.json')
        if self.verify_only:
            audit=list_fields(read(folder/'automatic-audit.json'));debug=read(folder/'automatic-debug.json')
        else:
            code="""local a=Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT');assert(a and a.status=='complete');assert(Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_DONE'));assert(CSC_MaterialMapDebug);print('CSCIMPL_AUDIT='..CSC_MaterialMapCore.Json(a));print('CSCIMPL_DEBUG='..CSC_MaterialMapCore.Json(CSC_MaterialMapDebug));"""
            text=self.cmd(code,'CSC_MaterialMap','implemented-audit-'+settings['group']+'-'+str(self.number),wait=5)
            audit=list_fields(json.loads(re.search(r'CSCIMPL_AUDIT=([^\r\n]+)',text).group(1)))
            debug=json.loads(re.search(r'CSCIMPL_DEBUG=([^\r\n]+)',text).group(1))
            write(folder/'automatic-audit.json',audit);write(folder/'automatic-debug.json',debug)
        assert audit['version']==3 and audit['initialization_turn']==1
        assert set(debug['definitions'])==SCOPE and set(audit['abundance']['targets'])==SCOPE
        assert all(a['quarter']=='TAILORS' and a['quantity']==1 for a in audit['additions'])
        assert all(row['quarter'] in SCOPE for row in audit['coverage'])
        assert all(a['quarter']=='TAILORS' for a in audit['attempts'])
        assert audit['abundance']['setting']==settings['resource_setting'] and audit['abundance']['standard_density']==30
        before=copy.deepcopy(after);before['plots']=debug['before']['plots'];write(folder/'before.json',before)
        lua=lua_runtime(self.lua_deps);lua.execute((ROOT/'Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMapCore.lua').read_text())
        eligible={r:{i:True for i in values} for r,values in debug['eligible'].items()}
        replay=lua.globals().CSC_MaterialMapCore.Plan(lua.table_from(debug['before'],recursive=True),lua.table_from(debug['definitions'],recursive=True),lua.table_from(eligible,recursive=True),settings['map_seed'],lua.table_from(audit['abundance'],recursive=True))
        repeated=list_fields(json.loads(lua.globals().CSC_MaterialMapCore.Json(replay)))
        for k in ('additions','coverage','palettes','abundance'):assert repeated[k]==audit[k],k
        additions={a['plot']:a for a in audit['additions']}
        for p,q in zip(before['plots'],after['plots']):
            if p['index'] in additions:
                a=additions[p['index']];assert not p.get('resource') and p['resource_count']==0
                assert q['resource']==a['resource'] and q['resource_count']==a['quantity']==1
                assert {k:v for k,v in p.items() if k not in ('resource','resource_count')}=={k:v for k,v in q.items() if k not in ('resource','resource_count')}
            else:assert p==q
        copies=sum(p['resource_count'] for p in after['plots'])-sum(p['resource_count'] for p in before['plots'])
        assert copies==sum(a['quantity'] for a in audit['additions'])==len(additions)
        assert len(additions)<=audit['max_per_map']
        for cid in {a['continent'] for a in additions.values()}:assert sum(a['continent']==cid for a in additions.values())<=audit['max_per_continent']
        # Only the two implemented definitions enter gameplay. The six design
        # references are merged here solely for the research viewer/census.
        definitions=copy.deepcopy(next(m for m in self.bundle['maps'] if m['id']==f"luxuries-4-{self.number}")['definitions'])
        definitions.update(debug['definitions'])
        census=continent_census(after,definitions);prior=continent_census(before,definitions)
        for row in audit['coverage']:
            b=next(q for c in prior if c['id']==row['continent'] for q in c['quarters'] if q['quarter']==row['quarter'])
            a=next(q for c in census if c['id']==row['continent'] for q in c['quarters'] if q['quarter']==row['quarter'])
            assert (row['base_before'],row['both_before'],row['base_after'],row['both_after'])==(b['common_clearable_base'],b['common_clearable_both'],a['common_clearable_base'],a['common_clearable_both'])
            assert not row['base_before'] or row['base_after'];assert not row['both_before'] or row['both_after']
        logs=(folder/'logs/Lua.log').read_text(encoding='utf-8',errors='replace');start=logs.rfind('Generating Continents Map');assert start>=0;logs=logs[start:]
        assert logs.count('CSC_MATERIAL_MAP_RESULT')==1 and logs.count('CSC_MATERIAL_MAP_ADDED')==len(additions)
        assert logs.index('CSC_MATERIAL_MAP_RESULT')<logs.index('Loading InGame UI')
        assert 'Runtime Error' not in logs and 'CSC_MATERIAL_MAP_ERROR' not in logs
        assert '[Gameplay] ERROR' not in (folder/'logs/Database.log').read_text(encoding='utf-8',errors='replace')
        label=next(label for group,label,_ in GROUPS if group==settings['group'])
        entry={'id':settings['group']+'-'+str(self.number),'group':settings['group'],'groupLabel':'Implemented Quarters · '+label+' · native','number':self.number,'settings':settings,'data':after,'definitions':definitions,'continents':census,'reference':census[0]['quarters'],
            'study':{'kind':'implemented-native','native':True,'setup':settings['group'],'version':3,'runtime_scope':['BAKERS','TAILORS'],'initialization_turn':audit['initialization_turn'],'eligibility_checks':audit['eligibility_checks']},
            'assistance':{'seed':audit['seed'],'additions':audit['additions'],'attempts':audit['attempts'],'palettes':audit['palettes'],'before_continents':prior,'abundance':audit['abundance']},
            'provenance':{'native':True,'kind':'implemented-native','warning':'Real Civ map generation; automatic CSC v3 pass targets implemented Quarters only. Bakers already exceed the calibration aim; direct assistance targets Tailors. Other six Quarters appear as design references in the viewer, with no runtime assistance. Quantities read from native plots; exact offline planner replay passed.'}}
        write(folder/'viewer-map.json',entry)
        write(folder/'verified.json',{'passed':True,'version':3,'map':self.number,'group':settings['group'],'resource_tiles_added':len(additions),'resource_copies_added':copies,'runtime_scope':['BAKERS','TAILORS'],'exact_lua_parity':True,'before_ui':True})
        self.say(f"{label} map{self.number}: verified {len(additions)} added tiles / {copies} individual resource copies")


def combine(bundle_path,out):
    entries=[read(p.parent/'viewer-map.json') for group,_,_ in GROUPS for p in sorted((out/group).glob('map-*/verified.json'))]
    map_rows=[];coverage=[];added=[]
    for m in entries:
        a=m['assistance'];counts=Counter(x['resource'] for x in a['additions'])
        before_copies=sum(p['resource_count'] for p in m['data']['plots'])-sum(x['quantity'] for x in a['additions'])
        map_rows.append({'group':m['group'],'map':m['number'],'map_seed':m['settings']['map_seed'],'game_seed':m['settings']['game_seed'],'continents':len(m['continents'])-1,'resource_tiles_before':sum(bool(p.get('resource')) for p in m['data']['plots'])-len(a['additions']),'resource_copies_before':before_copies,'added_tiles':len(a['additions']),'added_copies':sum(x['quantity'] for x in a['additions']),'copies_by_resource':json.dumps(counts,sort_keys=True)})
        for x in a['additions']:added.append({'group':m['group'],'map':m['number'],**{k:v for k,v in x.items() if k!='coverage_gains'}})
    for group,label,_ in GROUPS:
        maps=[m for m in entries if m['group']==group]
        if not maps:continue
        for q in entries[0]['definitions']:
            b=[r for m in maps for c in m['assistance']['before_continents'] if c['id']!=-1 for r in c['quarters'] if r['quarter']==q]
            a=[r for m in maps for c in m['continents'] if c['id']!=-1 for r in c['quarters'] if r['quarter']==q]
            row={'group':group,'label':label,'quarter':q,'runtime_scope':q in SCOPE,'maps':len(maps),'continents':len(a)}
            for mode in ('base','both'):
                for when,rs in [('before',b),('after',a)]:
                    row[mode+'_'+when+'_covered']=sum(r['common_clearable_'+mode]>0 for r in rs)
                    row[mode+'_'+when+'_sites']=sum(r['common_clearable_'+mode] for r in rs)
            for when,rs in [('before',b),('after',a)]:row['clusters_'+when]=sum(r['common_clearable_both_clusters'] for r in rs)
            coverage.append(row)
    write_csv(out/'map-stats.csv',map_rows);write_csv(out/'coverage.csv',coverage);write_csv(out/'added-resource-copies.csv',added)
    write(out/'analysis.json',{'maps':len(entries),'native':True,'runtime_version':3,'coverage':coverage,'map_stats':map_rows,'total_added_tiles':sum(x['added_tiles'] for x in map_rows),'total_added_copies':sum(x['added_copies'] for x in map_rows)})
    study={'version':3,'title':'CSC implemented Quarters · native vanilla study','maps':entries,'default_group':'implemented-vanilla-standard' if any(m['group']=='implemented-vanilla-standard' for m in entries) else entries[0]['group']}
    (out/'maps.json').write_text(json.dumps(study,separators=(',',':')),encoding='utf-8');render(study,out/'viewer.html')
    bundle=read(bundle_path);groups={g for g,_,_ in GROUPS};prior=[m for m in bundle['maps'] if m['group'] not in groups]
    bundle['maps']=prior+entries;bundle['default_group']=study['default_group'];bundle_path.write_text(json.dumps(bundle,separators=(',',':')),encoding='utf-8');render(bundle,bundle_path.with_name('index.html'))
    return len(entries)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('output','bundle','lua-dependencies'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--verify-only',action='store_true');p.add_argument('--first-only',action='store_true');p.add_argument('--combine-only',action='store_true')
    a=p.parse_args()
    if a.combine_only:print('Combined',combine(a.bundle,a.output));return
    r=ImplementedSurvey(a.output);r.bundle=read(a.bundle);r.pending_folder=None;r.save_maps=False;r.lua_deps=a.lua_dependencies;r.verify_only=a.verify_only
    if a.verify_only:
        for group,_,_ in GROUPS:
            for folder in sorted((a.output/group).glob('map-*/verified.json')):r.number=int(folder.parent.name[-2:]);r.assist_current(folder.parent)
    else:
        try:
            r.wait('MainMenu');r.config();r.select_mods(False)
            write(a.output/'batch.json',{'status':'running','expected_maps':15,'resource_settings':[1,2,3],'version':3})
            for group,_,setting in GROUPS:
                for i in range(1,6):
                    if (a.output/group/f'map-{i:02d}'/'verified.json').exists():continue
                    r.number=i;r.pending_folder=a.output/group/f'map-{i:02d}'
                    roster=next(m for m in r.bundle['maps'] if m['id']==f'luxuries-4-{i}')['settings']['leaders']
                    r.start_map(group,False,setting,i,roster)
                    if a.first_only:break
                if a.first_only:break
        except BaseException as exc:
            write(a.output/'batch-error.json',{'error':str(exc),'traceback':traceback.format_exc()});raise
        finally:
            r.pending_folder=None
            if 'MainMenu' not in r.states():r.menu()
            r.cmd("GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);",'MainMenu','clear-diagnostics')
            if (a.output/'original-preferences.json').exists():r.restore()
    installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    baseline=read(a.output/'installed-gameplay-hashes.json');assert all(sha(installed/name)==digest for name,digest in baseline.items())
    for path in (a.output/'commands').glob('*.lua'):
        assert not any(s in path.read_text() for s in ('ResourceBuilder.SetResourceType','CSC_MaterialMapCore.Plan(', 'CSC_InitializeMaterialMap('))
    count=combine(a.bundle,a.output);write(a.output/'batch.json',{'status':'complete' if count==15 else 'partial','maps':count,'expected_maps':15,'native':True,'version':3,'installed_files_unchanged':len(baseline),'observer_read_only':True})


if __name__=='__main__':main()
