"""Measured zero-turn legality response; never enables placement or alters queues."""
import copy
from native_harvest_rule import verify_live

ACCEPTED='1933683541'
REJECTED='-1234301467'
NO_LOCATION='-2028665063'
LOCATION_MESSAGE=['No suitable location to zone this district.']

def normalized_reasons(value):
    if value in (None,[]):return {}
    assert isinstance(value,dict),'Unexpected native reason representation'
    out={}
    for key,rows in value.items():
        assert isinstance(rows,list),'Unknown native reason bucket'
        if all(type(x)is int for x in rows):
            assert len(set(rows))==len(rows),'Duplicate native plot index'
            out[str(key)]=sorted(rows)
        else:
            assert all(isinstance(x,str)for x in rows),'Mixed native reason values'
            out[str(key)]=rows
    return out

def extract_changes(before,after):
    assert before['turn']==after['turn']==16,'Measured source16 only'
    root=lambda x:{k:v for k,v in x.items()if k not in('cities','delta_checks')}
    assert root(before)==root(after),'Production observation metadata changed unexpectedly'
    key=lambda c:(c['player'],c['city'])
    b={key(c):c for c in before['cities']};a={key(c):c for c in after['cities']}
    assert len(b)==len(before['cities'])and len(a)==len(after['cities'])and b.keys()==a.keys(),'City scope changed'
    tile_changes=[];district_changes=[]
    for identity in sorted(b):
        old,new=b[identity],a[identity];pid,city=identity
        assert pid in range(1,6),'Unexpected rule owner city'
        clean=lambda c:{k:v for k,v in c.items()if k not in('district_state','tiles','geography_cache_hit','delta_full_read_turn')}
        assert clean(old)==clean(new),'Queue/cost/population/production/other city fact changed'
        bt={t['index']:t for t in old['tiles']};at={t['index']:t for t in new['tiles']}
        assert len(bt)==len(old['tiles'])and len(at)==len(new['tiles'])and bt.keys()==at.keys(),'Tile observation scope changed'
        current_losses={q:set()for q in old['district_state']}
        for index in sorted(bt):
            x,y=bt[index],at[index]
            fixed=lambda t:{k:v for k,v in t.items()if k not in('potential_legal','current_legal','native_projection_verified')}
            assert fixed(x)==fixed(y),'Resource/owner/price/material/physical tile changed'
            assert x['potential_legal'].keys()==y['potential_legal'].keys()and x['current_legal'].keys()==y['current_legal'].keys(),'Quarter projection scope changed'
            assert x['native_projection_verified']==any(x['potential_legal'].values())and y['native_projection_verified']==any(y['potential_legal'].values()),'Projection derived flag inconsistent'
            for field in('potential_legal','current_legal'):
                for quarter,was in x[field].items():
                    now=y[field][quarter];assert type(was)is bool and type(now)is bool
                    if was==now:continue
                    assert was and not now and x['resource']>=0,'Rule may only remove legal resource plots'
                    if field=='current_legal':
                        assert x['owner']==pid,'Current legal loss must be owned'
                        current_losses[quarter].add(index)
            if any(x[k]!=y[k]for k in('potential_legal','current_legal','native_projection_verified')):
                tile_changes.append(dict(player=pid,city=city,plot=index,resource=x['resource'],owner=x['owner'],before_potential=x['potential_legal'],after_potential=y['potential_legal'],before_current=x['current_legal'],after_current=y['current_legal']))
        assert old['district_state'].keys()==new['district_state'].keys(),'District state scope changed'
        for quarter in sorted(old['district_state']):
            was=old['district_state'][quarter]
            now=new['district_state'][quarter]
            if was==now:
                assert not current_losses[quarter],'Native state omitted lost current plots'
                continue
            fixed=lambda d:{k:v for k,v in d.items()if k not in('secondary_result','can_produce')}
            assert fixed(was)==fixed(now),'Existing/placed/other district state changed'
            assert was['can_produce']is True and type(now['can_produce'])is bool,'Cannot unlock a Quarter or change failed prerequisites'
            wr=normalized_reasons(was.get('secondary_result'));nr=normalized_reasons(now.get('secondary_result'))
            accepted=set(wr.get(ACCEPTED,[]));remaining=set(nr.get(ACCEPTED,[]));removed=accepted-remaining
            assert remaining<=accepted and removed and removed==current_losses[quarter],'Unexpected accepted plot transition'
            assert set(nr.get(REJECTED,[]))==set(wr.get(REJECTED,[]))|removed,'Rejected plot transition differs'
            rest=lambda r:{k:v for k,v in r.items()if k not in(ACCEPTED,REJECTED,NO_LOCATION)}
            assert rest(wr)==rest(nr),'Other native prerequisite/failure reason changed'
            if not now['can_produce']:
                assert not remaining and nr.get(NO_LOCATION)==LOCATION_MESSAGE and not wr.get(NO_LOCATION),'Eligibility may close only after last legal resource location is lost'
            else:assert remaining and nr.get(NO_LOCATION)==wr.get(NO_LOCATION),'Unexpected location failure reason'
            district_changes.append(dict(player=pid,city=city,quarter=quarter,removed_plots=sorted(removed),can_produce_before=True,can_produce_after=now['can_produce'],before_reasons=wr,after_reasons=nr))
    return copy.deepcopy(dict(tile_changes=tile_changes,district_changes=district_changes))

def canonical_changes(changes):
    """Native Lua map enumeration has no semantic ordering; identities remain exact."""
    keys={'tile_changes':('player','city','plot'),'district_changes':('player','city','quarter')}
    assert isinstance(changes,dict)and changes.keys()==keys.keys(),'Unknown measured change scope'
    out={}
    for name,fields in keys.items():
        rows=changes[name];assert isinstance(rows,list),'Unknown measured change representation'
        identities=[tuple(row[field]for field in fields)for row in rows]
        assert len(identities)==len(set(identities)),'Duplicate measured transition identity'
        out[name]=copy.deepcopy(sorted(rows,key=lambda row:tuple(row[field]for field in fields)))
    return out

def verify_measured_change(before,after,proof,runtime):
    assert proof and proof['verified_zero_turn_rule_change']and proof['native_rule_definition']=='TRAIT_MAORI_PREVENT_HARVEST'and proof['turn']==16,'Missing exact measured rule proof'
    verify_live(runtime,16,confirmed=True)
    changes=extract_changes(before,after)
    assert canonical_changes(changes)==canonical_changes(proof['measured_legality_changes']),'Rule differs from measured zero-turn case'
    return changes
