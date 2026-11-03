"""Artifact-only exact-checkpoint native-rule progress report; not a final audit."""
import argparse,hashlib,json,sys,time
from pathlib import Path
from material_checkpoint_logs import reconstruct_checkpoint
from material_loss_intelligence import attribute,clear_targets,unit_operations,native_hash
from log_intelligence import repair_episodes

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def checkpoint(root,turn):
 root=Path(root);care=read(root/'material-care'/f'turn-{turn:03d}.json');primary=read(root/'game-01'/f'turn-{turn:03d}.json');builders=read(root/'builders'/f'turn-{turn:03d}.json');points=read(root/'metric-points'/f'turn-{turn:03d}.json')
 assert all(x['turn']==turn for x in(care,primary,builders,points))and not care['errors']and not builders['errors']
 op,cov=reconstruct_checkpoint(root,'UnitOperations.log',turn);tree,tcov=reconstruct_checkpoint(root,'AI_Behavior_Trees.csv',turn)
 ops=unit_operations(op,16,turn,set(range(1,6)));targets=clear_targets(tree,16,turn,set(range(1,6)),primary['width'])
 lost=[attribute(e,builders['events'],ops,targets,primary['width'])for e in care['events']if e['event']=='supply_lost'and e['turn']<=turn and e['player']in range(1,6)]
 grouped={}
 for e in lost:grouped[e['classification']]=grouped.get(e['classification'],0)+1
 starts=[e for e in builders['events']if e.get('event')=='builder_operation_started'and e.get('operation')==native_hash('UNITOPERATION_HARVEST_RESOURCE')and e['player']in range(1,6)and 16<=e['turn']<=turn]
 sentinels=[]
 for index in(1573,2533,2269,1647,2563,1619,2489):
  plot=next((p for p in primary['plots']if p['index']==index),None)
  links=[dict(Quarter=s['plot'],quarter=s['quarter'],player=s['player'],complete=s['complete'],producer_built=s['producer_built'],material=m)for s in points['sites']for m in s['materials']if m['plot']==index]
  sentinels.append(dict(plot=index,plot_observed=plot is not None,physical=plot,material_links=links))
 return dict(turn=turn,counts=points['counts'],care_callbacks=care['calls'],strategy=care['strategy'],loss_classifications=grouped,loss_cases=lost,harvest_operation_starts=starts,repair_episodes=repair_episodes(care['events'],builders['events'],primary['width']),sentinels=sentinels,closed_log_boundaries={'UnitOperations.log':cov,'AI_Behavior_Trees.csv':tcov},sparse_between_checkpoints=True)

def compare(control,rule,turn):
 control,rule=Path(control),Path(rule);audit=read(control/'independent-diagnostic-audit.json');startup=read(rule/'independent-native-rule-startup-confirmation.json');assert audit['verified']and audit['endpoint']==75 and startup['verified'];assert audit['source_sha256']==read(rule/'source-validation.json')['source_sha256'];assert read(control/'native-database-inventory.json')==read(rule/'native-database-inventory.json')
 pins=read(rule/'executed-source-pins.json');assert all(sha(Path(p))==digest for p,digest in pins.items())
 return dict(midrun_checkpoint_report=True,final_rule_audit_pending=True,one_saved_world=True,new_worlds=0,turn=turn,source_sha256=audit['source_sha256'],pins_verified=len(pins),control=checkpoint(control,turn),native_rule=checkpoint(rule,turn),actual_Service_payments='UNOBSERVED',no_uninterrupted_retention_inferred=True,time=time.time())

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('control',type=Path);p.add_argument('rule',type=Path);p.add_argument('--turn',type=int,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();v=compare(a.control,a.rule,a.turn);a.output.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(turn=a.turn,final_rule_audit_pending=True,counts={k:v[k]['counts']for k in('control','native_rule')},losses={k:v[k]['loss_classifications']for k in('control','native_rule')})))
