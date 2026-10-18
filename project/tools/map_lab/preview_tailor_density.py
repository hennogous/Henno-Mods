"""Replay the production Tailor density pass on archived native eligibility.

No Civ connection, native writes or terrain emulation. Captured v3 outcomes are
the unchanged reference, independently counted using the continent census.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
from collections import Counter
from offline import lua_runtime,read,write
from continent_analysis import continent_census
from analyze import write_csv

ROOT=Path(__file__).resolve().parents[3]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('captures','lua-dependencies','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    core=ROOT/'Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMapCore.lua'
    lua=lua_runtime(a.lua_dependencies);lua.execute(core.read_text(encoding='utf-8'))
    C=lua.globals().CSC_MaterialMapCore;rows=[]
    def call(data,defs,eligible,seed,profile):
        result=C.Plan(lua.table_from(data,recursive=True),lua.table_from(defs,recursive=True),lua.table_from(eligible,recursive=True),seed,lua.table_from(profile,recursive=True))
        return json.loads(C.Json(result))
    for group in ('sparse','standard','abundant'):
        for number in range(1,6):
            folder=a.captures/('implemented-vanilla-'+group)/f'map-{number:02d}'
            debug=read(folder/'automatic-debug.json');settings=read(folder/'settings.json');old=read(folder/'map.json');audit=read(folder/'automatic-audit.json')
            before=copy.deepcopy(old);before['plots']=copy.deepcopy(debug['before']['plots']);before['starting_plots']=debug['starting_plots']
            eligible={r:{i:True for i in indices} for r,indices in debug['eligible'].items()}
            plan=call(before,debug['definitions'],eligible,settings['map_seed'],audit['abundance'])
            additions=plan['additions'] if isinstance(plan['additions'],list) else []
            legacy=audit['additions'] if isinstance(audit['additions'],list) else []
            assert additions[:len(legacy)]==legacy,'Original continental repair changed'
            after=copy.deepcopy(before);indices={}
            for x in additions:
                i=x['plot'];assert i not in indices and not before['plots'][i].get('resource') and i in eligible[x['resource']]
                assert x['quarter']=='TAILORS' and x['quantity']==1
                if x.get('phase')=='site_density':assert i not in before['starting_plots']
                indices[i]=x;after['plots'][i]['resource']=x['resource'];after['plots'][i]['resource_count']=1
            prior=continent_census(old,debug['definitions']);current=continent_census(after,debug['definitions'])
            totals={}
            for label,census in (('before',prior),('after',current)):
                totals[label]={q['quarter']:{'base_only':q['common_clearable_base_only'],'both':q['common_clearable_both'],'base':q['common_clearable_base'],'both_clusters':q['common_clearable_both_clusters']} for q in census[0]['quarters']}
            density=plan['site_density'];assert density['reference']=={k:totals['before']['TAILORS'][k] for k in ('base_only','both')}
            assert density['after']=={k:totals['after']['TAILORS'][k] for k in ('base_only','both')}
            for kind in ('base_only','both'):
                factor=2 if kind=='base_only' else 4
                expected=factor*totals['before']['TAILORS'][kind]
                if kind=='both':expected=max(density['minimum_both'],expected)
                assert density['targets'][kind]==expected
                assert density['met'][kind]==(density['after'][kind]>=density['targets'][kind])
            # Each existing continent retains Baker counts and last Base/both
            # coverage. No pre-existing resource, feature or quantity is changed.
            for oldc,newc in zip(prior,current):
                assert oldc['id']==newc['id']
                for oldq,newq in zip(oldc['quarters'],newc['quarters']):
                    for metric in ('common_clearable_base','common_clearable_both'):
                        assert not oldq[metric] or newq[metric]
                        if oldq['quarter']=='BAKERS':assert newq[metric]>=oldq[metric]
            assert density['additions']<=density['max_per_map']
            for cid,n in density['additions_per_continent'].items():assert n<=density['max_per_continent'][cid]
            if group=='standard' and number==1:
                assert call(before,debug['definitions'],eligible,settings['map_seed'],audit['abundance'])==plan,'Planner not deterministic'
            dest=a.output/group/f'map-{number:02d}'
            write(dest/'plan.json',plan);write(dest/'map.json',after)
            row={'group':group,'map':number,**{f'{kind}_{when}':totals[when]['TAILORS'][kind] for kind in ('base_only','both','both_clusters') for when in ('before','after')},'base_only_target':density['targets']['base_only'],'both_target':density['targets']['both'],'extra_density_copies':density['additions'],'legacy_copies':len(legacy),'total_copies':len(additions),'targets_met':all(density['met'].values()),'density_resources':dict(Counter(x['resource'] for x in additions if x.get('phase')=='site_density'))}
            rows.append(row);print(json.dumps(row),flush=True)
    write(a.output/'results.json',{'version':4,'rows':rows,'native_eligibility':True,'native_execution':False,'lua_sha256':hashlib.sha256(core.read_bytes()).hexdigest()})
    write_csv(a.output/'results.csv',rows)

if __name__=='__main__':main()
