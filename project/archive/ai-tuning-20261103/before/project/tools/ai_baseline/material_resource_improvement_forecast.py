"""Native contracts for the explicit resource-bound improvement forecast diagnostic.

These checks prove loaded rows, source equality and endpoint observations, never
that the AI has consumed a signal or that an economic outcome is causal.
"""
TYPES=('IMPROVEMENT_PASTURE','IMPROVEMENT_CAMP','IMPROVEMENT_PLANTATION')
PRIVATE='YIELD_CSC_AI_PLACEMENT'
AMOUNT=80

def verify_loaded(db,raw_db):
    query='SELECT ImprovementType,YieldType,YieldChange FROM Improvement_YieldChanges'
    before=[tuple(r)for r in raw_db.execute(query)]
    after=[tuple(r)for r in db.execute(query)]
    extra=[(typ,PRIVATE,AMOUNT)for typ in TYPES]
    assert not any((r[0],r[1])in{(t,PRIVATE)for t in TYPES}for r in before),'Control already treated'
    assert sorted(after)==sorted(before+extra),'Unexpected improvement yield row/value'
    validity={}
    for typ in TYPES:
        resources=[r[0]for r in db.execute('SELECT ResourceType FROM Improvement_ValidResources WHERE ImprovementType=?',(typ,))]
        assert resources,'Improvement must have valid resources'
        for table in('Improvement_ValidTerrains','Improvement_ValidFeatures'):
            assert not list(db.execute('SELECT * FROM '+table+' WHERE ImprovementType=?',(typ,))),'Unexpected standalone terrain/feature validity'
        validity[typ]=dict(valid_resource_rows=len(resources),no_standalone_valid_terrain_or_feature_rows=True)
    return dict(verified_loaded_native_forecast=True,improvements=list(TYPES),yield_type=PRIVATE,amount=AMOUNT,exact_three_direct_rows_added=True,real_improvement_yields_equal=True,raw_resource_signal_unchanged=True,native_validity=validity,scope='All matching improvements, including humans; diagnostic only.',native_forecast_choice_response_proven=False)

def verify_source(initial):
    assert initial['world']['turn']==16,'Expected original16'
    assert not[p for p in initial['world']['plots']if p.get('improvement')in TYPES],'Existing observed treatment improvement needs distinct parity contract'
    return dict(source16=True,matching_improvements_observed=0,improvements=list(TYPES),observation_scope='Archived world census; unseen plots not asserted absent.',strict_world_economy_units_queues_private_and_citizen_gates_still_required=True)

def verify_final_snapshot(snapshot,primary,boundary):
    assert primary['turn']==75 and snapshot['turn']in(74,75),'Wrong native/UI boundary'
    assert all(x['turn']==75 and not x['active']and x['remaining']==0 for x in(boundary['before'],boundary['after'])),'Not separated inactive75'
    native={}
    for city in snapshot['cities']:
        for plot in city['plots']:
            assert plot['plot']not in native,'Duplicate yield plot'
            native[plot['plot']]=plot
    rows=[]
    for plot in primary['plots']:
        if plot.get('improvement')not in TYPES or plot.get('owner')not in range(6):continue
        value=native.get(plot['index']);assert value is not None,'Missing observed owned treatment improvement'
        assert value['owner']==plot['owner']and value.get('resource')==plot.get('resource'),'Endpoint owner/resource changed'
        assert isinstance(value['private'],(int,float))and isinstance(value['economic'],dict),'Missing native yield'
        rows.append(dict(plot=plot['index'],owner=plot['owner'],resource=plot.get('resource'),improvement=plot['improvement'],pillaged=plot.get('pillaged'),native_private_yield=value['private'],economic=value['economic']))
    return dict(verified_native_private_snapshot=True,turn=75,raw_UI_turn=snapshot['turn'],owned_treatment_improvements_observed=len(rows),improvements=rows,forecast_private_effect_isolated=False,native_choice_response_proven=False)
