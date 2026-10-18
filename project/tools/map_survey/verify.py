"""Independently verify complete map-survey evidence and source consistency."""
import argparse
import hashlib
import json
from pathlib import Path
from analyze import GROUPS

def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-partial',action='store_true');a=p.parse_args()
    paths=[p.parent for p in a.output.glob('*/map-*/complete.json')]
    if not a.allow_partial:assert len(paths)==15,'Expected15 completedmaps'
    checked=[]
    for folder in sorted(paths):
        settings=read(folder/'settings.json');data=read(folder/'map.json');save=read(folder/'save.json') if (folder/'save.json').exists() else None
        assert data['turn']==1 and (data['width'],data['height'])==(74,46)
        plots={p['index']:p for p in data['plots']};assert set(plots)==set(range(3404))
        assert len(data['players'])==6
        assert [p['leader'] for p in sorted(data['players'],key=lambda p:p['id'])]==settings['leaders']
        for i,plot in plots.items():
            assert plot['x']==i%74 and plot['y']==i//74
            assert plot.get('terrain') and type(plot['water']) is bool and type(plot['hills']) is bool
            assert len(plot['neighbors'])==len(set(plot['neighbors']))
            for n in plot['neighbors']:assert n in plots and i in plots[n]['neighbors']
        assert settings['speed']=='GAMESPEED_ONLINE' and settings['csc'] and settings['animal_resources']==1
        assert settings['resource_setting']==(45 if settings['group']=='tar-truly-abundant' else 3)
        assert settings['tar']==(settings['group']!='vanilla-abundant')
        assert ('RESOURCE_IRON' in {r['resource'] for r in data['harvests']})==settings['tar'],('TAR database fingerprint differs',folder)
        actual=(folder/'actual-settings.txt').read_text(encoding='utf-8');assert 'GAMESPEED_ONLINE' in actual
        if save:
            native_save=folder/Path(save['path']).name;assert native_save.stat().st_size>0 and sha(native_save)==save['sha256']
        else:assert read(folder/'complete.json')['saved'] is False
        errors=[line for line in (folder/'logs/Database.log').read_text(encoding='utf-8',errors='replace').splitlines() if '[Gameplay]' in line and 'ERROR' in line]
        assert not errors,(folder,errors)
        checked.append({'group':settings['group'],'map':settings['map_number'],'plots':3404,'turn':1,'save_sha256':save['sha256'] if save else None,'gameplay_sql_errors':0})
    installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    hashes=read(a.output/'installed-gameplay-hashes.json')
    assert all((installed/relative).exists() and sha(installed/relative)==digest for relative,digest in hashes.items())
    locked=read(a.output/'source-hashes.json')
    revision=read(a.output/'observer-revision.json') if (a.output/'observer-revision.json').exists() else None
    controller_revision=read(a.output/'controller-revision.json') if (a.output/'controller-revision.json').exists() else None
    for path,digest in locked.items():
        assert Path(path).exists(),path
        actual=sha(Path(path))
        if revision and path==revision['path']:
            assert digest==revision['before_hash'] and actual==revision['after_hash'],path
        elif controller_revision and path==controller_revision['path']:
            assert digest==controller_revision['before_hash'] and actual==controller_revision['after_hash'],path
        else:assert actual==digest,('A recorded source changed',path)
    first=a.output/'vanilla-abundant/map-01'
    if (first/'neighbor-normalization.json').exists():
        normalization=read(first/'neighbor-normalization.json');old=read(first/'map-original-neighbor-enumeration.json');new=read(first/'map.json')
        assert sha(first/'map-original-neighbor-enumeration.json')==normalization['original_sha256']
        canonical={p['index']:p['neighbors'] for p in read(Path(normalization['reference']))['plots']}
        for before,after in zip(old['plots'],new['plots']):
            assert {k:v for k,v in before.items() if k!='neighbors'}=={k:v for k,v in after.items() if k!='neighbors'}
            assert after['neighbors']==canonical[after['index']]
    result={'status':'passed','maps':len(checked),'tiles':3404*len(checked),'turns_advanced':0,'installed_csc_files':len(hashes),'locked_sources':len(locked),'games':checked}
    if (a.output/'analysis.json').exists():
        analysis=read(a.output/'analysis.json');assert len(analysis['opportunities'])==8*len(checked)
        for row in analysis['opportunities']:
            assert 0<=row['common_clearable_both']<=row['land_both']
            assert row['common_clearable_both']<=row['harvest_aware_both']<=row['land_both']
            assert row['resource_only_both']+row['terrain_feature_gain']==row['land_both']
        result['quarter_map_rows']=len(analysis['opportunities'])
    (a.output/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f'PASS: {len(checked)}maps, {result["tiles"]}tiles, verifieddata, unchangedCSC/TAR/sourcefiles, zeroGameplaySQLerrors')

if __name__=='__main__':main()
