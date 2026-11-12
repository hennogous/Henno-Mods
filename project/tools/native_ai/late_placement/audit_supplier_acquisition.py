"""Audit recorded supplier delivery and acquisition; never contacts the game.

The short control proves the exact forecast delta, not purchase necessity: its
only resource candidate is already the supplier. The longer full arm must also
show native payment, intended ownership and actual improvement. Astra separately
reviews the acceptance scope and closure. Save hashes and journals are authority,
not an aggregate counter or a successful audit script by itself.
"""
import argparse
import json
from pathlib import Path
import re
from driver import load, read, sha, write_json
from supplier_purchase_policy import without_supplier_bid

TARGET=(3,458758,861)


def collect(folder,turns):
    assert load(folder/'complete.json')==dict(verified=True,turns_advanced=turns)
    closed=load(folder/'session-closed.json')
    assert closed['verified'] and closed['owners_absent'] and closed['native_exit_code']==0
    assert closed['preferences_verified'] and closed['package_callback_completed']
    records={}
    for name,kind in [('purchase','plot-purchase-receipt'),('selector','district-selector-receipt')]:
        trace=load(folder/(name+'-trace.json'))
        assert trace['fault'] is None
        assert all(value==0 for key,value in trace.items()if key=='active' or key.startswith('pending'))
        journal=folder/(name+'-live.ndjson')
        assert journal.exists() or not trace['records'],'Missing nonempty native journal'
        stream=[row['message']['payload']['receipt'] for line in (read(journal).splitlines()if journal.exists()else[])
            if (row:=json.loads(line))['message'].get('payload',{}).get('kind')==kind]
        assert stream==trace['records'],'Terminal/journal records differ'
        records[name]=stream
    inputs=load(folder/'inputs.json')
    assert inputs['mode']=='integrated' and not inputs['repairOwnedPurchase'] and not inputs['prototypeBuyer']
    log=read(folder/'Lua.log')
    for failure in ['CSC_AI_BAKERS_DISTRICTS_FAILED','CSC_AI_INDUSTRY_PLACEMENT_FAILED']:
        assert failure not in log,failure
    states=[dict(turn=int(t),plot=int(i),owner=int(p),city=int(c),resource=int(r),improvement=int(k),pillaged=b=='true')
        for t,i,p,c,r,k,b in re.findall(r'CSC_SUPPLIER_STATE\s+(\d+)\s+(\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(-?\d+)\s+(true|false)',log)]
    assert states and states[0]['turn']==inputs['source_turn'] and states[0]['improvement']==-1
    assert all(row['plot']==861 for row in states),'Unrelated physical plot in supplier timeline'
    assert states[0]['owner']==(-1 if inputs['source_turn']==216 else 3)
    return dict(inputs=inputs,records=records,states=states,log=log)


def audit(full,control,follow=None):
    a,b=collect(full,8),collect(control,3)
    assert a['inputs']['save_sha256']==b['inputs']['save_sha256']=='9eff6d6c10e7c95af1f5ac37ee64c364f3174e4beefd1116c33769a905ff1d49'
    assert not a['inputs']['supplier_no_bid'] and b['inputs']['supplier_no_bid']
    differences=[]
    for package,files in a['inputs']['packages'].items():
        other=b['inputs']['packages'][package];assert files.keys()==other.keys()
        differences.extend((package,name)for name,value in files.items()if value!=other[name])
    assert differences==[('CSC Bakers Development Mod',r'Lua_UI\AI\CSC_AI_QuarterPlacement.lua')]
    relative='CSC Bakers Development Mod/Lua_UI/AI/CSC_AI_QuarterPlacement.lua'
    assert without_supplier_bid((full/relative).read_bytes(),a['inputs']['case'])==(control/relative).read_bytes()
    first=[]
    for arm in(a,b):
        row=next(r for r in arm['records']['purchase']if r['kind']=='routine-candidate' and r['turn']==216)
        assert row['cached']==dict(x=47,y=11) and len(row['frontier'])==1
        site,=row['frontier'];assert site['plot']==861 and site['feature']==-1
        first.append(site)
    # Farm index1 is the loaded mapped improvement recorded in the committed
    # main offers. Preserve every other native improvement score unchanged.
    assert re.search(r'CSC_AI_SUPPLIER_ACQUISITION_OFFER turn=216 version=\d+ player=3 city=458758 quarter=788 plot=861 quote=40 deltaQ8=6656 improvements=1(?:\r|\n)',a['log'])
    assert len(first[0]['scoresQ8'])==len(first[1]['scoresQ8'])
    changed=[(i,x,y)for i,(x,y)in enumerate(zip(first[0]['scoresQ8'],first[1]['scoresQ8']))if x!=y]
    assert len(changed)==1 and changed[0][0]==1 and changed[0][1]-changed[0][2]==6656
    debit=[r for r in a['records']['purchase']if r['kind']=='debit-return' and
        (r['player'],r['city'],r['plot'])==TARGET]
    assert len(debit)==1 and debit[0]['deltaMatched'] and debit[0]['measuredDeltaQ8']<0
    # Source quotes can change before execution. Bind the measured debit to
    # the actual native handler quote, never assume the initial 40-Gold quote.
    quotes=[r for r in a['records']['purchase']if r['kind']=='quote' and
        (r['player'],r['city'],r['plot'],r['turn'])==(*TARGET,debit[0]['turn'])]
    assert len(quotes)==1 and quotes[0]['gold']>0
    assert debit[0]['measuredDeltaQ8']==-quotes[0]['gold']*256
    assert not any(r['kind']=='debit-return' and r.get('plot')==861 for r in b['records']['purchase'])
    physical=a['states'][:]
    folders=[('full',full),('control',control)]
    paid_checkpoint=load(full/'endpoint-checkpoint.json')
    assert paid_checkpoint['verified'] and paid_checkpoint['save_complete_event'] and paid_checkpoint['native_phase_unchanged']
    assert sha(full/'endpoint.Civ6Save')==paid_checkpoint['sha256']==sha(Path(paid_checkpoint['native_save']))
    if follow:
        c=collect(follow,6)
        assert c['inputs']['save_sha256']==paid_checkpoint['sha256']
        assert c['inputs']['packages']==a['inputs']['packages'],'Continuation policy packages changed'
        assert c['inputs']['case']['turn']==224 and c['states'][0]['city']==458758
        assert not any(r['kind']=='debit-return'and r.get('plot')==861 for r in c['records']['purchase'])
        physical.extend(c['states']);folders.append(('follow',follow))
    owned=[r for r in physical if r['owner']==3 and r['city']==458758]
    improved=[r for r in owned if r['resource']==54 and r['improvement']==1 and not r['pillaged']]
    assert improved,'Native supplier improvement outcome remains open'
    # Corroborate the physical Farm with the executed native tree node. READY
    # rows can still print a default Barbarian Camp type and are not execution.
    behavior=read((follow or full)/'AI_Behavior_Trees.csv')
    native_improvement_rows=[line for line in behavior.splitlines()if
        'City LOC_CITY_NAME_NUREMBERG, Build City Improvement, SUCCESS, Build Improvement, Building Improvement: IMPROVEMENT_FARM' in line]
    assert native_improvement_rows
    assert min(r['turn']for r in owned)>=debit[0]['turn']
    terminal=follow or full
    checkpoint=load(terminal/'endpoint-checkpoint.json')
    assert checkpoint['verified'] and checkpoint['save_complete_event'] and checkpoint['native_phase_unchanged']
    assert sha(terminal/'endpoint.Civ6Save')==checkpoint['sha256']==sha(Path(checkpoint['native_save']))
    files=['inputs.json','complete.json','session-closed.json','purchase-trace.json','purchase-live.ndjson',
        'selector-trace.json','selector-live.ndjson','Lua.log','AI_CityBuild.csv','AI_Behavior_Trees.csv',
        'endpoint-checkpoint.json','supplier-chain-qualification.txt']
    return dict(artifact_audit_verified=True,scope='Supplier route qualification; no supplier-bid purchase-necessity claim',
        source_sha256=a['inputs']['save_sha256'],ce_sha256=a['inputs']['ce_sha256'],package_differences=differences,
        mapped_forecast_delta=dict(improvement=1,control_q8=changed[0][2],full_q8=changed[0][1],delta_q8=6656),
        native_candidate_unchanged=True,measured_payment=debit[0],physical_supplier_timeline=physical,
        first_improved_turn=min(r['turn']for r in improved),endpoint_checkpoint=checkpoint,
        native_improvement_rows=native_improvement_rows,
        pins={label:{name:sha(folder/name)for name in files if(folder/name).exists()}for label,folder in folders})


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['full','control','output']:parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--follow',type=Path,help='Verified six-turn continuation of the paid224 endpoint')
    args=parser.parse_args()
    assert not args.output.exists(),'Do not replace a sealed audit'
    result=audit(args.full,args.control,args.follow);write_json(args.output,result)
    print(json.dumps(dict(verified=True,delta_q8=6656,first_improved_turn=result['first_improved_turn'])))
