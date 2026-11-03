"""Resource-only Farm forecast contracts; native decision response is separate."""
import copy,json
from material_forecast_contract import source_parity
PRIVATE='YIELD_CSC_AI_PLACEMENT'
MODIFIER='MOD_CSC_AI_FARM_RESOURCE_FORECAST'
PREFIX='REQ_CSC_AI_FARM_FORECAST_'
SET='REQSET_CSC_AI_FARM_RESOURCE_FORECAST'
AMOUNT=80

def verify_loaded(db,base):
    resources={v[0]for v in db.execute("SELECT ResourceType FROM Improvement_ValidResources WHERE ImprovementType='IMPROVEMENT_FARM'")};assert resources
    assert list(db.execute('SELECT ModifierType,OwnerRequirementSetId FROM Modifiers WHERE ModifierId=?',(MODIFIER,)))==[('MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',SET)]
    assert dict(db.execute('SELECT Name,Value FROM ModifierArguments WHERE ModifierId=?',(MODIFIER,)))=={'YieldType':PRIVATE,'Amount':'80'}
    assert list(db.execute('SELECT ImprovementType FROM ImprovementModifiers WHERE ModifierId=?',(MODIFIER,)))==[('IMPROVEMENT_FARM',)]
    assert list(db.execute('SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId=?',(SET,)))==[('REQUIREMENTSET_TEST_ANY',)]
    assert {v[0]for v in db.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?',(SET,))}=={PREFIX+r for r in resources}
    for resource in resources:
        assert list(db.execute('SELECT RequirementType FROM Requirements WHERE RequirementId=?',(PREFIX+resource,)))==[('REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES',)]
        assert dict(db.execute('SELECT Name,Value FROM RequirementArguments WHERE RequirementId=?',(PREFIX+resource,)))=={'ResourceType':resource}
    # No flat Farm signal, real yield, terrain legality, technology or AI weights
    # change. The table-level exception is limited to the exact authored rows.
    allowed={'Requirements','RequirementArguments','RequirementSets','RequirementSetRequirements','Modifiers','ModifierArguments','ImprovementModifiers'}
    changed=[]
    tables=[v[0]for v in db.execute("SELECT name FROM sqlite_master WHERE type='table'AND name NOT LIKE 'sqlite_%'")]
    for table in tables:
        rows=lambda con:sorted(json.dumps(list(v),default=str)for v in con.execute('SELECT * FROM "'+table+'"'))
        before,after=rows(base),rows(db)
        if before!=after:
            assert table in allowed,('Unexpected DB change',table);assert set(before)<=set(after),'Existing rows changed';changed.append(table)
    assert set(changed)==allowed
    assert not list(db.execute("SELECT * FROM Improvement_YieldChanges WHERE ImprovementType='IMPROVEMENT_FARM'AND YieldType=?",(PRIVATE,)))
    return dict(verified=True,resources=sorted(resources),private_amount=80,terrain_only_farm_extra=0,database_changed_tables=sorted(changed),all_owner_diagnostic=True,native_projection_or_decision_proven=False)

def source_gate(reference,actual,resources):
    """Only existing eligible Farm private values may change at source16.

    Private city totals are recorded treatment outputs only for cities working
    those Farms. Ordinary city/plot inputs, all citizens, Gold, units, production
    and physical world remain strict. No unknown city-multiplier formula claimed.
    """
    resources=set(resources);normalized=copy.deepcopy(actual);physical={p['index']:p for p in reference['world']['plots']}
    eligible={i for i,p in physical.items()if p.get('improvement')=='IMPROVEMENT_FARM'and p.get('resource')in resources and not p.get('pillaged')}
    before={p['plot']:p for p in reference['private']};affected=[]
    for row in normalized['private']:
        if row['plot']in eligible:
            assert row['private']==before[row['plot']]['private']+80,('Eligible Farm native value missing',row['plot'],before[row['plot']]['private'],row['private'])
            row['private']-=80;affected.append(row['plot'])
    assert affected,'No positive native eligible Farm control observed'
    b={(c['player'],c['city']):c for c in reference['allocation']['cities']};worked=set()
    for city in normalized['allocation']['cities']:
        key=city['player'],city['city'];prior=b[key];bp={p['plot']:p for p in prior['plots']}
        for row in city['plots']:
            if row['plot']in eligible:
                assert row['private']==bp[row['plot']]['private']+80
                row['private']-=80
                if row['workers']>0:worked.add(key)
        assert city==prior,('Citizens/ordinary inputs/private scope changed',key)
    refcities={(c['player'],c['id']):c for c in reference['world']['cities']};private_cities=[]
    for city in normalized['world']['cities']:
        key=city['player'],city['id'];old=refcities[key]['yields'];new=city['yields'];delta=new.get(PRIVATE,0)-old.get(PRIVATE,0)
        if delta:
            assert key in worked and delta>0,('Undeclared private city change',key,delta)
            private_cities.append(dict(player=key[0],city=key[1],delta=delta,exact_multiplier_formula_proven=False));new[PRIVATE]=old[PRIVATE]
    parity=source_parity(reference,normalized,{})
    result=dict(parity)
    result.update(verified=True,base_parity=parity,eligible_existing_Farms=sorted(affected),only_private_farm_treatment_difference=True,private_city_output_deltas=private_cities,ordinary_inputs_and_citizens_equal=True,native_AI_decision_response_proven=False)
    result.update(city_output_inertness_claimed=False,ordinary_city_output_equal=True)
    return result

def endpoint_snapshot(snapshot,primary,boundary):
    assert primary['turn']==150 and snapshot['turn']in(149,150)
    assert all(v['turn']==150 and not v['active']and v['remaining']==0 for v in boundary.values())
    rows=[p for c in snapshot['cities']for p in c['plots']];assert len(rows)==len({p['plot']for p in rows})
    return dict(verified_read=True,turn=150,raw_UI_turn=snapshot['turn'],AI_choice_or_forecast_score_proven=False,private_values_are_UI_getter_observations=True)
