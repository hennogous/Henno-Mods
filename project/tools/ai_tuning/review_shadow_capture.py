"""Read closed artifacts; emit a compact offline projection/planning packet.

No native imports or connection. Original capture artifacts are never rewritten.
"""
import argparse
import hashlib
import json
from pathlib import Path
from shadow_projection import review_projection


def review_capture(root):
    root=Path(root)
    names=('shadow-initial.json','shadow-final.json','initial-census.json','final-census.json')
    paths={name:root/name for name in names}
    blobs={name:path.read_bytes() for name,path in paths.items()}
    inputs={name:dict(path=str(paths[name]),sha256=hashlib.sha256(blob).hexdigest()) for name,blob in blobs.items()}
    raw={name:json.loads(blob.decode('utf-8-sig')) for name,blob in blobs.items()}
    if raw[names[0]]!=raw[names[1]] or raw[names[2]]!=raw[names[3]]:
        raise ValueError('Declared zero-turn endpoints disagree')
    shadow,core=raw[names[0]],raw[names[2]]
    source=str(paths[names[0]])+' SHA256 '+inputs[names[0]]['sha256']
    result=review_projection(shadow,core,source)
    tiles={t['plot']:t for t in shadow['tiles']}
    if len(tiles)!=len(shadow['tiles']):raise ValueError('Duplicate plot facts')
    expected={(q,t['plot'])for q,s in shadow['district_state'].items()for t in s['targets']if t['legal'] is True}
    keys=[(c['quarter'],c['plot'])for c in shadow['candidates']]
    if set(keys)!=expected or len(keys)!=len(set(keys)):
        raise ValueError('Incomplete captured native opportunity set')
    screening=[]
    for candidate,projection in zip(shadow['candidates'],result['candidates']):
        tile=tiles[candidate['plot']];materials=[]
        for p in tile['neighbors']:
            near=tiles[p];roles=near['roles'][candidate['quarter']]
            if not any(roles.values()):continue
            materials.append(dict(plot=p,resource=near['resource'],roles=roles,
                                  owner=near['owner'],visible=near['resource_visible'],
                                  functioning_improvement=near['valid_resource_improvement'] and not near['improvement_pillaged'],
                                  district=near['district']))
        base=[m for m in materials if m['roles']['base'] and m['visible']]
        screening.append(dict(quarter=candidate['quarter'],plot=candidate['plot'],materials=materials,
                              attachment_projection=projection['projection']['real'],
                              decision='no_new_start_without_mapped_base' if not base else 'needs_investment_review',
                              customer_space='uncommitted geometry only; no future yield or supply credit',
                              action_authorization=False))
    backlog={}
    for chain in shadow['chains']:
        for p in chain['dependencies']:
            t=tiles[p]
            if t['owner']!=shadow['player'] or not t['resource_visible'] or t['district']>=0:
                state='unusable_or_not_owned'
            elif not t['valid_resource_improvement']:
                state='needs_valid_improvement'
            elif t['improvement_pillaged']:
                state='needs_repair'
            else:state='functioning_improvement_geometry'
            row=backlog.setdefault(p,dict(plot=p,resource=t['resource'],state=state,dependent_chains=[]))
            row['dependent_chains'].append(dict(city=chain['city'],quarter=chain['quarter'],plot=chain['plot']))
    result.update(inputs=inputs,screening=screening,existing_material_backlog=list(backlog.values()),
                  trial_policy='credible Base required; Both or real P+G >=4, separate from investment readiness',
                  native_calls=0,ai_turns_advanced=0,
                  native_scientific_status_unchanged='partial_geometry_no_extension',
                  next_decision='Use existing-chain work and stronger site inventories; do not place any of these twelve starts')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('Preserve existing result: '+str(a.output))
    result=review_capture(a.root)
    a.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(dict(controls=result['control_count'],matched=result['controls_matched'],
                          opportunities=len(result['screening']),
                          no_base=sum(r['decision']=='no_new_start_without_mapped_base'for r in result['screening']),
                          material_states={state:sum(r['state']==state for r in result['existing_material_backlog'])
                                           for state in sorted({r['state']for r in result['existing_material_backlog']})},
                          output=str(a.output))))


if __name__=='__main__':main()
