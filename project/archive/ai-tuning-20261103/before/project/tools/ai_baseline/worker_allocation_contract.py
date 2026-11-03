"""Pure read-only worked-plot parity and output-direction contracts."""
def allocation_difference(reference,actual):
    b={(c['player'],c['city']):c for c in reference['cities']};a={(c['player'],c['city']):c for c in actual['cities']}
    assert b.keys()==a.keys(),'Citizen city scope changed';out=[]
    for key,old in sorted(b.items()):
        new=a[key];assert old['population']==new['population'],'Population drift'
        before={p['plot']:p for p in old['plots']};after={p['plot']:p for p in new['plots']};assert before.keys()==after.keys(),'Owned city plot scope changed'
        assert sum(p['workers']for p in before.values())==sum(p['workers']for p in after.values()),'Citizen count changed'
        changes=[];delta={}
        for plot,p in before.items():
            q=after[plot];assert(p['owner'],p.get('resource'),p['economic'])==(q['owner'],q.get('resource'),q['economic']),('Plot physical/economic input changed',plot)
            n=q['workers']-p['workers']
            if n:changes.append(dict(plot=plot,workers_before=p['workers'],workers_after=q['workers'],resource=p.get('resource'),economic=p['economic'],private_before=p['private'],private_after=q['private']))
            for name,value in p['economic'].items():delta[name]=delta.get(name,0)+n*value
        out.append(dict(player=key[0],city=key[1],changed_worked_plots=changes,worked_plot_economic_delta=delta,population=old['population']))
    return out

def allocations_stable(before,after):
    return all(not row['changed_worked_plots']for row in allocation_difference(before,after))

def channels_correspond(worked,city,tolerance=1/256):
    for name in worked.keys()|city.keys():
        w,c=worked.get(name,0),city.get(name,0)
        if abs(w)<=tolerance:
            if abs(c)>tolerance:return False
        elif abs(c)<=tolerance or(w>0)!=(c>0):return False
    return True

def observer_output_evidence(reference_world,actual_world,reference_allocation,actual_allocation):
    differences=allocation_difference(reference_allocation,actual_allocation)
    before={(c['player'],c['id']):c for c in reference_world['cities']}
    after={(c['player'],c['id']):c for c in actual_world['cities']}
    assert before.keys()==after.keys(),'City scope changed'
    assert {(r['player'],r['city'])for r in differences}==before.keys(),'Incomplete citizen-allocation scope'
    out=[]
    for row in differences:
        key=row['player'],row['city'];assert row['population']==before[key]['population']==after[key]['population'],'Citizen/world population mismatch';b,a=before[key]['yields'],after[key]['yields']
        names={k for k in b.keys()|a.keys()if not k.startswith('YIELD_CSC_AI_')}
        delta={k:a.get(k,0)-b.get(k,0)for k in names}
        if not any(delta.values()):continue
        assert row['player']==0,'Non-observer economic output changed'
        assert row['changed_worked_plots'],'Observer output changed without observed worker reassignment'
        assert channels_correspond(row['worked_plot_economic_delta'],delta),'Observer output change does not match worked-plot channels/directions'
        out.append(dict(player=row['player'],city=row['city'],changed_worked_plots=row['changed_worked_plots'],worked_plot_economic_delta=row['worked_plot_economic_delta'],derived_city_economic_delta=delta))
    assert out,'No observer economic difference explained'
    return out
