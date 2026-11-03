"""Assert and summarize paired native marker smoke evidence, not AI efficacy."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
def read(name):return json.loads((a.output/(name+'.json')).read_text())
assert read('final-smoke')['status']=='passed'
off,on=read('final-unmarked-gameplay'),read('final-marked-gameplay')
for x,y in zip(off['rows'],on['rows']):
 assert {k:v for k,v in x.items() if k!='feature'}=={k:v for k,v in y.items() if k!='feature'}
assert off['real_features_kept']==on['real_features_kept']
u,v=read('final-unmarked-ui'),read('final-marked-ui');signals=[]
for x,y in zip(u['rows'],v['rows']):
 assert y['value']-x['value']==y['marker_expected'] and y['marker_expected']>0
 for key in ('quarter_legal','resource_district_legal','build_operations'):assert x[key]==y[key],(x['kind'],key)
 signals.append({'kind':x['kind'],'off':x['value'],'on':y['value'],'delta':y['marker_expected']})
assert v['marker_rows_shown']==0 and v['filter']
u,v=read('final-unmarked-human'),read('final-marked-human')
for x,y in zip(u['rows'],v['rows']):
 assert x['can_build'] and y['can_build']
 for k in ('can_harvest','can_plant','charges','moves'):assert x[k]==y[k]
assert read('final-unitpanel')['normal_woods_clear_shown']
assert not any(x['clear_shown'] for x in read('final-unitpanel')['marker_rows'])
assert all(x['charges']==2 and x['marker'] for x in read('final-build-verify')['rows'])
assert read('final-resource-removed')['feature']==-1
result={'status':'passed','signals':signals,'real_features_preserved':on['real_features_kept'],
 'native_clear_operation_still_exists':True,'clear_hidden_in_unitpanel':True,
 'native_builder_builds':3,'resource_removal_cleanup':True,'ai_efficacy_proven':False}
trial=a.output/'controlled-ai'
if (trial/'controlled-ai.json').exists():
 s=json.loads((trial/'game-01/turn-020.json').read_text());events=[e for e in s['events'] if e.get('quarter')]
 result['controlled_ai']={'turn':20,'quarter_placements':len(events),'placements':[{'player':e['player'],'quarter':e['quarter'],'plot':e['plot'],'base':e['site']['base'],'spec':e['site']['spec'],'sales':e['site']['sales']} for e in events],
 'marker_removals':json.loads((trial/'marker-events.json').read_text())['removed'],
 'observer_errors':s['errors'],'natural_baseline_comparison':False}
 assert not s['errors']
deployment=json.loads((a.output.parent/'deploy-final/deployment.json').read_text())
result['tested_deployment_hashes']=deployment['files']
result['decision']='Rejected: real feature objects affect Builder planning and district legality.'
result['revision_note']='20-turn AI run used deployed revision 2. Revision 3 Builder guard was hot-loaded after turn 20, then disabled without further AI turns.'
(a.output/'marker-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
