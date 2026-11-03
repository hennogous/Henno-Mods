"""Independent offline audit of one completed installed-profile test."""
import argparse,hashlib,json,sqlite3,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ai_baseline'))
from service_planner.metrics import summarize
from service_planner.benchmark_report import report_points
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(root):
 job=read(root/'job-status.json');sup=read(root/'supervisor.json')
 endpoint=job['native_endpoint'];assert endpoint in(150,200)
 checkpoints=[1]+list(range(25,endpoint+1,25))
 assert job['status']=='complete'and job['native_endpoint']==endpoint
 assert sup['status']=='complete'and sup['exit_code']==0
 init=read(root/'initialization.json');assert init['verified']and init['observer_only_external_driver']
 mode=init.get('profile','RH'if init['RH_mode']else'BASIC');assert mode in('BASIC','RH')
 assert set(init['expansions'])=={'Rise and Fall','Gathering Storm'}
 pins=read(root/'executed-source-pins.json')
 for i,(name,digest)in enumerate(pins.items()):assert sha(root/'source-version'/f'{i:04d}-{Path(name).name}')==digest,name
 with sqlite3.connect((root/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)as db:
  assert db.execute("SELECT Mode FROM CSC_AI_Profile WHERE Id='ACTIVE'").fetchone()==(mode,)
  movement=db.execute("SELECT COUNT(*) FROM Modifiers WHERE ModifierId='MOD_CSC_AI_BASIC_BUILDER_MOVEMENT'").fetchone()[0]
  if mode=='RH':
   assert movement==0
   assert db.execute("SELECT COUNT(*) FROM RHAITags WHERE YieldName='LOC_CSC_AI_PLACEMENT_NAME'").fetchone()[0]==1
  else:
   assert movement==1
   assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()==(30,)
   assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts'AND Item='UNIT_BUILDER'").fetchone()==(50,)
   menu=read(root/'native-menu-configuration.json');assert menu['enabled_mod_ids']==['c5e66bd1-d804-443b-ac3d-1917a20dba3c']
  assert db.execute("SELECT COUNT(*) FROM Districts WHERE DistrictType='DISTRICT_DAM'").fetchone()[0]==1
  assert db.execute("SELECT COUNT(*) FROM Governors").fetchone()[0]>0
 explicit_gaps=read(root/'checkpoint-save-gaps.json')if(root/'checkpoint-save-gaps.json').exists()else[]
 if explicit_gaps:
  assert len(explicit_gaps)==1 and explicit_gaps[0]['turn']==150
  gap=explicit_gaps[0];endpoint_proof=read(root/'endpoint150-verification.json')
  assert endpoint==150 and endpoint_proof['verified']and endpoint_proof['native_endpoint']==150 and endpoint_proof['three_inactive_samples']and endpoint_proof['world_known_fact_equal']and endpoint_proof['economic_ledger_equal']and endpoint_proof['research_rows']==745
  assert gap['save_requests']==1 and gap['resends']==0 and gap['save_complete_event']is False and gap['native_file_observed']is False
  import re
  assert re.search(r'CSC_PENDING_SAVE\s+'+re.escape(gap['unique_name'])+r'\s+false',gap['raw_status'])
 for turn in checkpoints:
  save_path=root/'exact-checkpoints'/f'turn-{turn:03d}.json'
  if turn==150 and not save_path.exists()and explicit_gaps:
   assert not(root/'exact-checkpoints/turn-150.Civ6Save').exists()
  elif turn==125 and not save_path.exists() and (root/'checkpoint125-save-gap.json').exists():
   gap=read(root/'checkpoint125-save-gap.json');assert gap.get('verified') is False or gap.get('save_verified') is False or gap.get('save_complete_event') is False or 'unconfirmed' in json.dumps(gap).lower()
  else:
   save=read(save_path);assert save['verified']and save['turn']==turn
   assert sha(root/'exact-checkpoints'/f'turn-{turn:03d}.Civ6Save')==save['sha256']
  for folder in('game-01','chain-metrics','research','builders','quarter-sites'):
   v=read(root/folder/f'turn-{turn:03d}.json');assert v['turn']==turn,(folder,turn)
 final=read(root/'receipts'/f'turn-{endpoint:03d}.json');assert final['turn']==endpoint and not final['errors']and not final['pending']
 tokens=set();cost=own=donations=0
 for r in final['receipts']:
  assert r['status']=='confirmed'and r['token']not in tokens;tokens.add(r['token']);f=r['funding']
  assert f['price']==f['own']+f['grant']and r['final_gold']==f['gold']+f['grant']-f['price']
  assert f['own']>=0 and f['grant']>=0 and r['final_gold']>=min(f['gold'],f['reserve'])
  cost+=f['price'];own+=f['own'];donations+=f['grant']
 keys=set()
 for entry in final['foundations']:
  assert entry['key']not in keys;keys.add(entry['key']);f=entry['value'];assert f['status']=='confirmed'
  assert f['before']['progress']==f['after']['progress']==0 and f['before']['cost']==f['after']['cost']>0
  assert f['before']['queue']==f['after']['queue']and f['after']['placed']
 assert final['totals']==dict(tiles=len(tokens),cost=cost,own=own,subsidy=donations,foundations=len(keys))
 research=read(root/'research'/f'turn-{endpoint:03d}.json');assert not research['errors']
 seen={(r['turn'],r['player'])for r in research['history']};assert len(seen)==len(research['history'])
 defeats={v['player']:v['turn']for v in research['defeats']}
 expected={(t,p)for t in range(1,endpoint)for p in range(1,6)if p not in defeats or t<defeats[p]}
 missing=sorted(expected-seen);unexpected=sorted(seen-expected)
 restored=read(root/'package-restored.json');prefs=read(root/'preferences-restored.json')
 assert restored['verified']and restored['pretest_package_equal']and restored['all_Civ_absent']and prefs['verified']and prefs['auto_start']is False
 installation=Path(read(root/'deployment/deployment.json')['installed']);original=read(root/'deployment/original-installed-manifest.json')
 current={str(p.relative_to(installation)):{'sha256':sha(p),'size':p.stat().st_size}for p in installation.rglob('*')if p.is_file()}
 assert current==original,'Current pretest runtime differs'
 physical=read(root/'game-01'/f'turn-{endpoint:03d}.json');cities=[c for c in physical['cities']if 1<=c['player']<=5]
 quarters=[d for city in cities for d in city['districts']if d.get('quarter')]
 points=[summarize(read(root/'chain-metrics'/f'turn-{t:03d}.json'))for t in checkpoints]
 targets=[dict(plot=int(e['key'].split(':')[3]),quarter=e['key'].split(':')[2])for e in final['foundations']]
 retention=report_points([p for p in points if p['turn']>=75],targets)
 return dict(verified_observed_contracts=True,profile=mode,native_endpoint=endpoint,AI_counts=points[-1]['counts'],**{'retention75_'+str(endpoint):{k:retention[k]for k in('observed_material_link_retention','material_links_available_at_every_observed_checkpoint','coverage')}},pins=len(pins),economics=final['totals'],new_installed_acquisition_observed=bool(tokens),new_foundation_observed=bool(keys),AI_cities=len(cities),AI_population=sum(c['population']for c in cities),Quarters=len(quarters),complete_Quarters=sum(bool(d['complete'])for d in quarters),research_rows=len(seen),missing_research=missing,unexpected_research=unexpected,full_dense_observation_pass=not missing and not unexpected,exact_save_coverage_complete=not explicit_gaps and not(root/'checkpoint125-save-gap.json').exists(),exact_save_gaps=([125]if(root/'checkpoint125-save-gap.json').exists()else[])+[g['turn']for g in explicit_gaps],customer_links_are_not_payments=True,actual_service_payments='UNOBSERVED',causal_effect='Not estimated: one combined-treatment pilot')
def main():
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 value=audit(a.root);a.output.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');print(json.dumps(value))
if __name__=='__main__':main()
