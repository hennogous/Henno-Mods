"""Build site/Service candidates from one normalized native city observation.

The native reader supplies actual neighbors and legality, avoiding guessed hex
geometry or a Python emulation of CanStartOperation. Beyond-border plots are
allowed in the observation; ownership is a dependency, not an eligibility grant.
"""
from .policy import Candidate, PROFILES


def build_candidates(observation,*,material_first=False,stepwise=False,connector_limit=0):
    if material_first:return build_material_candidates(observation,stepwise=stepwise,connector_limit=connector_limit)
    pid=observation['player'];city=observation['city'];turn=observation['turn']
    tiles={p['index']:p for p in observation['tiles']}
    same=set(observation.get('same_quarter_types',()))
    out=[]
    for plot in tiles.values():
        if plot.get('owner')not in(-1,pid) or not plot.get('revealed',False):continue
        if not plot.get('within_city_reach',False):continue
        if any(plot.get(key)not in(None,-1,'')for key in('resource','improvement','district','feature')):continue
        adjacent=[tiles[i]for i in plot.get('neighbors',())if i in tiles]
        for quarter in('BAKERS','TAILORS'):
            if quarter in same:continue
            if not plot.get('potential_legal',{}).get(quarter,False):continue
            materials=[p for p in adjacent if p.get('material_visible',False)and p.get('revealed',False)
                       and p.get('owner')in(-1,pid)and
                       (quarter in p.get('base_for',())or quarter in p.get('spec_for',()))]
            owned=[p for p in materials if p['owner']==pid]
            foreign_source=plot['owner']==-1
            variants=[(plot['index'],)if foreign_source else ()]
            # V1 considers a material purchase when the Quarter tile is already
            # owned. It never buys a chain of intermediate tiles speculatively.
            if not foreign_source:
                variants.extend((p['index'],)for p in materials if p['owner']==-1 and p.get('native_purchasable',False))
            for missing in variants:
                supplies=[p for p in materials if p['owner']==pid or p['index']in missing]
                base=sum(quarter in p.get('base_for',())for p in supplies)
                spec=sum(quarter in p.get('spec_for',())for p in supplies)
                if base<1:continue
                price=tiles[missing[0]].get('price',0)if missing else 0
                purchasable=tiles[missing[0]].get('native_purchasable',False)if missing else False
                common=dict(player=pid,city=city,plot=plot['index'],quarter=quarter,base=base,specialty=spec,
                            missing_tiles=missing,purchase_plot=missing[0]if missing else None,price=price,
                            revealed=True,material_visible=True,potential_legal=True,
                            current_legal=not missing and plot.get('current_legal',{}).get(quarter,False),
                            native_purchasable=purchasable,eligible_ai=observation.get('eligible_ai',False),
                            human=observation.get('human',False),dependencies_owned_or_in_purchase=True,
                            frontier_danger=plot.get('frontier_danger',True),
                            displacement_cost=plot.get('displacement_cost',0),
                            natural_border_in_turns=tiles[missing[0]].get('natural_border_in_turns')if missing else None,
                            era=observation.get('era',999),material_plots=tuple(p['index']for p in supplies),
                            observed_turn=turn,native_projection_verified=plot.get('native_projection_verified',False))
                owned_base=sum(quarter in p.get('base_for',())for p in owned)
                owned_spec=sum(quarter in p.get('spec_for',())for p in owned)
                # Do not spend on a redundant extra supply when an owned chain
                # already meets this route's material gate.
                if not missing or foreign_source or owned_base==0:
                    out.append(Candidate(**common))
                for name,service in PROFILES.items():
                    if service.quarter!=quarter or(service.requires_specialty and spec==0):continue
                    if missing and not foreign_source and owned_base>0 and(not service.requires_specialty or owned_spec>0):continue
                    venues=[v for v in observation.get('venues',())if v['plot']in plot.get('neighbors',())
                            and v['owner']==pid and v['type']in service.venues and v.get('functioning',False)]
                    for venue in venues:
                        readiness=observation.get('readiness',{}).get(name,{})
                        out.append(Candidate(**common,service=name,venue_ready=True,customer_plot=venue['plot'],
                                             research_ready=readiness.get('research_ready',False),
                                             producer_ready=readiness.get('producer_ready',False),
                                             ready_in_turns=readiness.get('ready_in_turns',999),
                                             confidence=readiness.get('confidence',.5)))
    return out


def build_material_candidates(observation,*,stepwise=False,connector_limit=0):
    """Revealed source sites plus minimal Base/Spec acquisition plans.

    Sources stay within three tiles of an existing city; resource neighbors can
    be in the fourth ring. No venue, Service civic, production or need signal is
    consulted. A plan can require source + Base + Specialty (at most three buys).
    Each native step is chosen from current legal purchase targets. Unknown cost
    or reach retains a watch plan and never grants speculative ownership.
    """
    from itertools import product
    pid=observation['player'];cid=observation['city'];turn=observation['turn']
    tiles={p['index']:p for p in observation['tiles']};out={}
    same=set(observation.get('same_quarter_types',()))
    for source in tiles.values():
        if source.get('owner')not in(-1,pid)or not source.get('revealed')or not source.get('within_city_reach'):continue
        established=source.get('established_quarter')if stepwise else None
        if not established and any(source.get(k)not in(None,-1,'')for k in('resource','improvement','district','feature')):continue
        adjacent=[tiles[i]for i in source.get('neighbors',())if i in tiles]
        for quarter in('BAKERS','TAILORS'):
            support=bool(established==quarter and source['owner']==pid)
            if established and not support:continue
            if not support and(quarter in same or not source.get('potential_legal',{}).get(quarter)):continue
            material=[p for p in adjacent if p.get('owner')in(-1,pid)and p.get('revealed')
                      and p.get('material_visible')and(quarter in p.get('base_for',())or quarter in p.get('spec_for',()))]
            bases=[p for p in material if quarter in p.get('base_for',())]
            specs=[p for p in material if quarter in p.get('spec_for',())]
            owned={p['index']for p in material if p['owner']==pid}
            if any(p['owner']==pid for p in bases):bases=[next(p for p in bases if p['owner']==pid)]
            if any(p['owner']==pid for p in specs):specs=[next(p for p in specs if p['owner']==pid)]
            # A Base-only fallback is free-placement/watch only. Both variants
            # use a minimal extra supply set and count every already-owned Base.
            pairs=list(product(bases,specs))if specs else [(b,None)for b in bases]
            for base,spec in pairs:
                supply=owned|{base['index']}|({spec['index']}if spec else set())
                missing=tuple(sorted(({source['index']}|supply)-{i for i in ({source['index']}|supply)if tiles[i]['owner']==pid}))
                if len(missing)>3:continue
                connectors=();route_blocked=False
                if stepwise and connector_limit and missing and spec is not None:
                    from .routing import acquisition_route
                    route=acquisition_route(tiles,pid,missing,supply,connector_limit)
                    if route is None:route_blocked=True # Keep the opportunity marked for natural ownership changes.
                    else:
                        missing=tuple(sorted(set(missing)|set(route)));connectors=tuple(sorted(set(route)-({source['index']}|supply)))
                # Buy the source first if it is missing; later steps may acquire
                # its adjacent materials as ordinary native border purchases.
                next_tiles=list(missing)if stepwise else([source['index']]if source['owner']==-1 else list(missing))
                next_tiles=[i for i in next_tiles if tiles[i].get('native_purchasable')]
                if stepwise:
                    # Avoid the imminent free border step if another useful
                    # material can be acquired; spend on resources before land.
                    next_tiles=[i for i in next_tiles if tiles[i].get('natural_border_in_turns')is None or tiles[i]['natural_border_in_turns']>2]
                next_tiles.sort(key=lambda i:(i not in supply if stepwise else False,tiles[i].get('price',0),i))
                purchase=next_tiles[0]if next_tiles and not route_blocked else None
                costs=[tiles[i].get('price',0)for i in missing]
                remaining=sum(costs)if all(x>0 for x in costs)else 0
                after_step=owned|({purchase}if purchase in supply else set())
                count=lambda indices,tag:sum(quarter in tiles[i].get(tag,())for i in indices)
                c=Candidate(player=pid,city=cid,plot=source['index'],quarter=quarter,
                    base=count(supply,'base_for'),specialty=count(supply,'spec_for'),
                    dependencies_owned_or_in_purchase=True,missing_tiles=missing,purchase_plot=purchase,
                    price=tiles[purchase].get('price',0)if purchase is not None else 0,
                    remaining_price=remaining,plan_materials=tuple(sorted(supply)),
                    purchase_base=count(after_step,'base_for'),purchase_specialty=count(after_step,'spec_for'),
                    revealed=True,material_visible=True,potential_legal=True,
                    current_legal=(source['owner']==pid and count(owned,'base_for')>0 if stepwise else not missing)and source.get('current_legal',{}).get(quarter,False),
                    native_purchasable=purchase is not None,eligible_ai=observation.get('eligible_ai',False),
                    human=observation.get('human',False),frontier_danger=any(tiles[i].get('frontier_danger',True)for i in ({source['index']}|supply)),
                    displacement_cost=source.get('displacement_cost',0),
                    natural_border_in_turns=tiles[purchase].get('natural_border_in_turns')if purchase is not None else None,
                    material_plots=tuple(sorted(supply)),observed_turn=turn,
                    native_projection_verified=support or source.get('native_projection_verified',False),
                    established=support,source_owned=source['owner']==pid,owned_base=count(owned,'base_for'),owned_specialty=count(owned,'spec_for'),stepwise=stepwise,plan_connectors=connectors)
                out[c.key]=c
    return list(out.values())
