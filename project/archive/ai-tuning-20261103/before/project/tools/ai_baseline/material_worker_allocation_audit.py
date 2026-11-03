"""Offline comparison of zero-turn worked-plot and derived-city-output probes."""
import argparse,json,time
from pathlib import Path
from material_care_audit import read,require
from material_forecast_contract import private_yield_parity,economic_cities,production_signature
from full_game_controller.continuation import world_signature

from worker_allocation_contract import allocation_difference,allocations_stable,channels_correspond

def audit(reference,raw):
    reference=Path(reference);raw=Path(raw);S=reference.parent;C=S/'source016-control';PREP=S/'offline-preparation/source016-forecast-pair'
    checks=[read(p/'control-verification.json')for p in(reference,raw)]
    require(all(x['verified']and x['turn']==16 and x['AI_turns_requested']==x['AI_turns_advanced']==0 and x['new_worlds']==0 and x['worked_plot_census']for x in checks),'Zero-turn probes incomplete')
    require(checks[0]['source_sha256']==checks[1]['source_sha256']==read(C/'control-verification.json')['source_sha256'],'Different sources')
    for root in(reference,raw):
        cleanup=read(root/'final-restoration.json');require(cleanup['verified']and cleanup['pretest510_equal']and cleanup['all_Civ_absent']and cleanup['prefs144']and cleanup['autostart']is False,'Cleanup missing')
        require(allocations_stable(read(root/'initial-worker-allocation.json'),read(root/'final-worker-allocation.json'))and economic_cities(read(root/'world.json'))==economic_cities(read(root/'world-final.json')),'Allocation/output not settled within arm')
    worlds=[read(p/'world-final.json')for p in(reference,raw)]
    require(world_signature(worlds[0])==world_signature(worlds[1]),'Source world differs')
    require(read(reference/'units.json')==read(raw/'units.json')==read(C/'units.json'),'Units differ')
    require(read(reference/'all-major-treasuries.json')==read(raw/'all-major-treasuries.json')==read(C/'all-major-treasuries.json'),'Treasuries differ')
    require(production_signature(read(reference/'production-and-quotes.json'))==production_signature(read(raw/'production-and-quotes.json')),'Native production differs')
    plotproof=private_yield_parity(read(reference/'private-plot-yields.json'),read(raw/'private-plot-yields.json'),read(PREP/'preparation.json')['raw_resource_yields'])
    changes=allocation_difference(read(reference/'final-worker-allocation.json'),read(raw/'final-worker-allocation.json'))
    bycity=[{(c['player'],c['id']):c for c in w['cities']}for w in worlds];outputs=[]
    for c in changes:
        key=c['player'],c['city'];b,a=(x[key]['yields']for x in bycity);names={n for n in b.keys()|a.keys()if not n.startswith('YIELD_CSC_AI_')};delta={n:a.get(n,0)-b.get(n,0)for n in names}
        nonzero={n:v for n,v in delta.items()if v};c['derived_city_economic_delta']=delta;c['changed_channels_and_direction_correspond']=channels_correspond(c['worked_plot_economic_delta'],delta)
        if nonzero:outputs.append(dict(player=key[0],city=key[1],reference={n:b[n]for n in names},raw={n:a[n]for n in names},delta=nonzero))
    supported=bool(outputs)and all(c['changed_channels_and_direction_correspond']for c in changes)
    return dict(verified_zero_turn_pair=True,within_arm_allocations_stable=True,original_packet_equality_flags=[read(p/'allocation-stability.json')['worker_allocation_stable']for p in(reference,raw)],packet_flag_limit='Original helper compared the entire packet, including private signal values refreshed by care. This audit independently compares actual workers and real plot inputs; originals retained.',source_sha256=checks[0]['source_sha256'],native_turn=16,AI_turns_advanced=0,purchases=0,foundations=0,private_plot_parity=plotproof,allocation_changes=changes,derived_city_output_changes=outputs,direct_worked_plot_evidence_supports_reassignment=supported,output_change_scope=[x['player']for x in outputs],economic_plot_yield_inputs_unchanged=True,city_output_inertness_proven=False,observer_treatment_spillover=any(x['player']==0 for x in outputs),AI_only_release_ready=False,limits=['Worked-plot changes are native observations; no citizen focus or assignment command was issued.','Channel/direction agreement does not measure every amenity or city rate multiplier.','Private raw resource valuation is global and can affect human automatic citizen allocation and unowned-plot planning.','This is mechanism investigation, not proof of an AI-only production implementation or material preservation.'],time=time.time())

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('reference',type=Path);p.add_argument('raw',type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();v=audit(a.reference,a.raw);a.output.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))
