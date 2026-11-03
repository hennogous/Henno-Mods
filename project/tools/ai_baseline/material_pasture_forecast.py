"""Exact native-table contract for the broad Pasture forecasting diagnostic."""
PASTURE='IMPROVEMENT_PASTURE'
PRIVATE='YIELD_CSC_AI_PLACEMENT'
AMOUNT=80

def verify_loaded(db,raw_db):
    query='SELECT ImprovementType,YieldType,YieldChange FROM Improvement_YieldChanges'
    before=[tuple(r)for r in raw_db.execute(query)];after=[tuple(r)for r in db.execute(query)]
    assert not any(r[:2]==(PASTURE,PRIVATE)for r in before),'Control already has the diagnostic signal'
    assert sorted(after)==sorted(before+[(PASTURE,PRIVATE,AMOUNT)]),'Unexpected improvement-yield row/value change'
    assert [r for r in after if r[1].startswith('YIELD_CSC_AI_')and r not in before]==[(PASTURE,PRIVATE,AMOUNT)],'Other private forecast changes'
    return dict(verified_loaded_native_forecast=True,improvement=PASTURE,yield_type=PRIVATE,amount=AMOUNT,only_one_direct_row_added=True,real_improvement_yields_equal=True,raw_resource_signal_unchanged=True,scope='All Pastures, including humans; diagnostic only.',native_forecast_choice_response_proven=False)

def verify_source(initial):
    assert initial['world']['turn']==16,'Expected original source16'
    assert not[p for p in initial['world']['plots']if p.get('improvement')==PASTURE],'Existing observed Pasture requires a different source contract'
    return dict(source16=True,existing_observed_Pastures=0,observation_scope='Archived world census; unseen map plots are not asserted absent.',strict_world_economy_units_queues_private_and_citizen_gates_still_required=True)


def verify_final_snapshot(snapshot,primary,boundary):
    assert primary['turn']==75 and snapshot['turn']in(74,75),'Wrong final native/UI phase'
    assert all(row['turn']==75 and not row['active']and row['remaining']==0 for row in(boundary['before'],boundary['after'])),'Private snapshot crossed an active/wrong native boundary' 
    plots={}
    for city in snapshot['cities']:
        for plot in city['plots']:
            assert plot['plot'] not in plots,'Duplicate private-yield plot'
            plots[plot['plot']]=plot
    pastures=[]
    for plot in primary['plots']:
        if plot.get('improvement')!=PASTURE or plot.get('owner') not in range(0,6):continue
        native=plots.get(plot['index']);assert native is not None,'Owned Pasture missing from final native yield snapshot'
        assert native['owner']==plot['owner']and native.get('resource')==plot.get('resource'),'Pasture ownership/resource differs across endpoint reads'
        assert isinstance(native['private'],(int,float))and isinstance(native['economic'],dict),'Missing native yield fields'
        pastures.append(dict(plot=plot['index'],owner=plot['owner'],resource=plot.get('resource'),pillaged=plot.get('pillaged'),native_private_yield=native['private'],economic=native['economic']))
    return dict(verified_native_private_snapshot=True,turn=75,raw_UI_turn=snapshot['turn'],native_turn_before=boundary['before']['turn'],native_turn_after=boundary['after']['turn'],owned_Pastures_observed=len(pastures),Pastures=pastures,scope='Endpoint native plot yields, not a zero-turn on/off isolation of the direct contribution.',forecast_private_effect_isolated=False,native_choice_response_proven=False)
