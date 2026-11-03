"""Offline deposit viability at the exact pre-commit native observation.

District-free resource adjacency is a necessary structural condition for CSC
improvement supply. It is not proof of technology, path, safety or future work.
Historical receipts remain unchanged; this reports a different, explicit gate.
"""
import argparse,hashlib,json,re
from pathlib import Path

def empty_district(value):return value in(None,-1,'')

def selected_materials(candidate,city):
    tiles={t['index']:t for t in city['tiles']};quarter=candidate['quarter'];owner=candidate['player']
    selected=candidate.get('plan_materials')or candidate.get('material_plots',[])
    rows=[]
    for index in selected:
        tile=tiles.get(index)
        if tile is None:rows.append(dict(plot=index,observed=False,structurally_available=None));continue
        available=empty_district(tile.get('district'))
        rows.append(dict(plot=index,observed=True,owner=tile.get('owner'),resource=tile.get('resource'),district=tile.get('district'),revealed=tile.get('revealed'),material_visible=tile.get('material_visible'),structurally_available=available,owned_by_AI=tile.get('owner')==owner,base=quarter in tile.get('base_for',[]),spec=quarter in tile.get('spec_for',[])))
    missing=[r['plot']for r in rows if not r['observed']]
    good=[r for r in rows if r['observed']and r['structurally_available']and r['owned_by_AI']and r['revealed']and r['material_visible']]
    base=sum(r['base']for r in good);spec=sum(r['spec']for r in good)
    return dict(selected=rows,missing_observations=missing,covered_materials=[r['plot']for r in rows if r['observed']and not r['structurally_available']],district_free_owned_base=base,district_free_owned_spec=spec,Both_structural_gate=(base>0 and spec>0)if not missing else None,complete_native_improvement_legality_claimed=False)

def precommit(root,candidate):
    root=Path(root);turn=candidate['observed_turn'];tag=f"{turn}-{candidate['player']}-{candidate['city']}-{candidate['quarter']}"
    commands=list((root/'pending-commands').glob('*-zero-commit-'+tag+'.lua'))
    if len(commands)!=1:return dict(observed=False,reason='No unique native commit marker',matches=len(commands))
    sequence=int(commands[0].name.split('-',1)[0]);matches=[]
    for path in(root/'commands').glob('*-service-read-'+str(turn)+'.txt'):
        seq=int(path.name.split('-',1)[0])
        if seq>=sequence:continue
        packets=re.findall(r'CSC_SERVICE_NATIVE=([^\r\n]+)',path.read_text(encoding='utf-8-sig'))
        if not packets:continue
        packet=json.loads(packets[-1]);assert abs(packet['turn']-turn)<=1,'Unexpected UI phase'
        city=next((x for x in packet['cities']if(x['player'],x['city'])==(candidate['player'],candidate['city'])),None)
        if city is None:continue
        result=selected_materials(candidate,city)
        if result['missing_observations']:continue
        matches.append((seq,path,packet['turn'],result))
    if not matches:return dict(observed=False,reason='No complete same-turn raw native material observation before commit')
    seq,path,ui,result=max(matches,key=lambda x:x[0])
    return dict(observed=True,read=str(path),read_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),read_sequence=seq,commit_sequence=sequence,raw_UI_turn=ui,Core_turn=turn,**result)

def report(root):
    root=Path(root);rows=[]
    for path in sorted((root/'placements').glob('*/validation.json')):
        data=json.loads(path.read_text(encoding='utf-8-sig'));c=data['candidate'];proof=precommit(root,c)
        rows.append(dict(player=c['player'],city=c['city'],plot=c['plot'],quarter=c['quarter'],turn=c['observed_turn'],original_claim=dict(base=c['base'],spec=c['specialty']),validation=str(path),precommit=proof))
    return dict(root=str(root),retrospective_report=True,original_receipts_unchanged=True,placements=len(rows),precommit_observed=sum(x['precommit']['observed']for x in rows),failed_Both_structural_gate=sum(x['precommit'].get('Both_structural_gate')is False for x in rows),unknown_Both_gate=sum(x['precommit'].get('Both_structural_gate')is None for x in rows),cases=rows,limits=['Only necessary district-free/owned/revealed material gates, not complete native improvement legality.','Missing technology can be a future opportunity; this report does not exclude it.','A district retaining a resource is not an improvement supplying CSC Stage1.','Historical assisted placements remain actual outcomes; a retrospective failure is not a native crash or a fabricated undo.'])

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();v=report(a.root);a.output.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v[k]for k in('placements','precommit_observed','failed_Both_structural_gate','unknown_Both_gate')}))
