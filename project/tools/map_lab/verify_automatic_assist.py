"""Verify automatic startup evidence, native maps and unchanged installation."""
import argparse
from collections import Counter
import json
from pathlib import Path
from automatic_assist import read,sha,write
from continent_analysis import continent_census


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--bundle',type=Path,required=True);a=p.parse_args()
    bundle=read(a.bundle);results=[]
    for i in range(1,6):
        folder=a.output/'csc-helper-lua'/f'map-{i:02d}'
        assert read(folder/'complete.json')['automatic_lua_verified']
        entry=read(folder/'viewer-map.json');audit=read(folder/'automatic-audit.json');before=read(folder/'before.json');after=read(folder/'map.json');debug=read(folder/'automatic-debug.json')
        assert audit['status']=='complete' and entry['native_comparison']['lua_parity']
        assert after['turn']==1 and len(after['plots'])==3404
        control=next(m for m in bundle['maps'] if m['id']==f'luxuries-4-{i}')
        assert before['plots']==control['data']['plots']
        additions=audit['additions'];assert len(additions)<=10
        counts=Counter(x['continent'] for x in additions);assert max(counts.values(),default=0)<=4
        changed={x['plot']:x for x in additions};assert len(changed)==len(additions)
        for old,new in zip(before['plots'],after['plots']):
            if old['index'] in changed:
                new_resource=changed[old['index']]['resource']
                assert not old.get('resource') and new['resource']==new_resource
                assert old['index'] in debug['eligible'][new_resource]
                assert {k:v for k,v in old.items() if k!='resource'}=={k:v for k,v in new.items() if k!='resource'}
            else:assert old==new
        assert entry['continents']==continent_census(after,entry['definitions'])
        for q in audit['coverage']:
            assert not q['base_before'] or q['base_after'];assert not q['both_before'] or q['both_after']
        log=(folder/'logs/Lua.log').read_text(encoding='utf-8',errors='replace')
        start=log.rfind('Generating Continents Map');log=log[start:] if start>=0 else log
        assert log.count('CSC_MATERIAL_MAP_RESULT')==1,'Automatic pass must complete once'
        assert 'CSC_MATERIAL_MAP_ERROR' not in log and 'Runtime Error' not in log
        assert log.count('CSC_MATERIAL_MAP_ADDED')==len(additions)
        if 'Loading InGame UI' in log:assert log.index('CSC_MATERIAL_MAP_RESULT')<log.index('Loading InGame UI')
        assert '[Gameplay] ERROR' not in (folder/'logs/Database.log').read_text(encoding='utf-8',errors='replace')
        results.append({'map':i,'additions':len(additions),'initialization_turn':audit['initialization_turn'],'eligibility_checks':audit['eligibility_checks'],'exact_lua_replay':True,'one_automatic_completion':True})
    for path in (a.output/'commands').glob('*.lua'):
        code=path.read_text(encoding='utf-8')
        for forbidden in ('ResourceBuilder.SetResourceType','CSC_MaterialMapCore.Plan(', 'CSC_InitializeMaterialMap('):assert forbidden not in code,'Observer invoked helper: '+str(path)
    installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    installed_hashes=read(a.output/'installed-gameplay-hashes.json');assert all(sha(installed/k)==v for k,v in installed_hashes.items())
    deployment=read(a.output/'deployment.json');assert deployment['sdk_manifest_generated'] and deployment['unrelated_actions_preserved']
    assert read(a.output/'preferences-restored.json')['verified']
    result={'passed':True,'maps':5,'tiles':17020,'turns_advanced':0,'additions':sum(x['additions'] for x in results),'native_eligibility_checks':sum(x['eligibility_checks'] for x in results),'automatic_execution':True,'controller_resource_writes':0,'exact_lua_replay':True,'installed_files_verified':len(installed_hashes),'results':results}
    write(a.output/'validation.json',result);print(json.dumps(result))


if __name__=='__main__':main()
