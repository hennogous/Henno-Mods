"""Audit 1.4 strong-site versus viable-only guidance after both sessions close.

This reads evidence only. Complete native packet coverage and precise control
bytes establish what changed; cache/winner/request receipts establish the
decision. Independent Astra review, not this artifact checker, closes the item.
"""
import argparse
import json
from pathlib import Path
import re
from audit_river_choice import collect
from driver import read,load,sha,write_json
from liverpool_adjacency_policy import without_strong_promotions


def requests(folder,winner):
    text=read(folder/'AI_CityBuild.csv')
    lines=[line for line in text.splitlines()if line.startswith('25, 4, LOC_CITY_NAME_LIVERPOOL,')
        and 'SUBMITTED' in line and 'DISTRICT_CSC_BAKERS_QUARTER' in line]
    assert len(lines)==1
    assert int(float(re.search(r'VALUE ([0-9.]+)',lines[0])[1]))==winner['result']//256
    width=load(folder/'cases/boston-selection/survey.json')['width']
    x,y=winner['plot']%width,winner['plot']//width
    reservations=[line for line in read(folder/'AI_Behavior_Trees.csv').splitlines()
        if line.startswith('25, 4, City LOC_CITY_NAME_LIVERPOOL, Build City District, SUCCESS, Reserve Plot,')
        and line.rstrip().endswith(f'Reserving plot {x} {y}')]
    assert len(reservations)==1
    return dict(request=lines[0],reservation=reservations[0])


def audit(full,viable):
    a,b=collect(full),collect(viable)
    assert a['inputs']['saves']==b['inputs']['saves']
    assert a['inputs']['packages'].keys()==b['inputs']['packages'].keys()
    differences=[]
    for package,files in a['inputs']['packages'].items():
        other=b['inputs']['packages'][package];assert files.keys()==other.keys()
        differences.extend((package,path)for path,value in files.items()if value!=other[path])
    assert len(differences)==1 and differences[0][1].replace('\\','/')=='Lua_UI/AI/CSC_AI_AdjacencyScan.lua'
    assert without_strong_promotions((full/'CSC_AI_AdjacencyScan.lua').read_bytes())==(viable/'CSC_AI_AdjacencyScan.lua').read_bytes()
    assert a['inspection']==b['inspection'],'Physical source or conditional forecast differs'
    assert a['inspection']['forecast']['total']==4 and a['inspection']['alternateForecast']['total']==3
    assert a['inspection']['baseRule']['count']==1
    common=a['nets'].keys()&b['nets'].keys()
    assert all(a['nets'][key]==b['nets'][key]for key in common),'Shared native records differ'
    assert all(a['caches'][key]==b['caches'][key]for key in common),'Shared final cache records differ'
    changes=[]
    for key in sorted(a['nets'].keys()|b['nets'].keys()):
        left,right=a['nets'].get(key),b['nets'].get(key)
        da=left['result']-left['base']if left else 0
        db=right['result']-right['base']if right else 0
        if da!=db:changes.append(dict(key=key,full_delta=da,viable_delta=db,
            full_native_record=left,viable_native_record=right))
    assert [(r['key'],r['full_delta'],r['viable_delta'])for r in changes]==[
        ((4,131073,36,2423),12288,0),((4,131073,36,2497),12288,0),
        ((4,131073,36,2571),0,6144)],'Unexpected policy difference'
    assert len(a['winners'])==len(b['winners'])==1
    for arm,plot,delta in ((a,2497,12288),(b,2571,6144)):
        winner=arm['winners'][0];assert (winner['district'],winner['plot'])==(36,plot)
        key=(4,131073,36,plot)
        assert winner['result']==arm['nets'][key]['result']==arm['caches'][key]['result']
        assert arm['nets'][key]['result']-arm['nets'][key]['base']==delta
    return dict(artifact_audit_verified=True,closure_claim=False,
        scope='1.4 ordinary strong-site guidance versus viable-only guidance; not +48/+24 premium necessity or construction',
        source=a['inputs']['saves'],manifest_differences=differences,
        complete_packet_counts=dict(full=len(a['nets']),viable=len(b['nets'])),
        common_native_pair_count=len(common),common_net_and_cache_identical=True,
        packet_differences=changes,physical_inspections_identical=True,
        source_model_adjacency=dict(strong2497=4,weaker2571=3),
        retained_city_offers=dict(full=a['retained_city_offers'],viable=b['retained_city_offers']),
        other_arrays_identical_zero=a['other_arrays']==b['other_arrays'],
        winners=dict(full=a['winners'][0],viable=b['winners'][0]),
        requests=dict(full=requests(full,a['winners'][0]),viable=requests(viable,b['winners'][0])),
        unpaired_native_limit='Absent CSC entries have zero adjustment; raw/native-cache counterparts remain unobserved',
        pins={name:{file:sha(folder/file)for file in ('inputs.json','Lua.log','AI_CityBuild.csv',
            'AI_Behavior_Trees.csv','City_BuildQueue.csv','complete.json','session-closed.json')}
            for name,folder in (('full',full),('viable',viable))})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--full',type=Path,required=True);p.add_argument('--viable',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    assert not args.output.exists(),'Never replace a sealed audit'
    result=audit(args.full,args.viable);write_json(args.output,result);print(json.dumps(result,ensure_ascii=True))
