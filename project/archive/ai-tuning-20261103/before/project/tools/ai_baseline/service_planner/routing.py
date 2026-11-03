"""Read-only projected routes; current native reach is the only first-step authority.

At most three required sites and two additional connectors within current city
purchase range. Future adjacency is a projection, never native authorization.
Unknown quote is a ranking penalty, never a fabricated actual gold amount.
"""
import heapq,itertools

def acquisition_route(tiles,player,required,materials,connector_limit=2):
    required=frozenset(required);materials=frozenset(materials)
    if not required:return ()
    if len(required)>3 or connector_limit<0 or connector_limit>2:return None
    nodes={i:p for i,p in tiles.items()if p.get('owner')in(-1,player)and p.get('revealed')
           and not p.get('frontier_danger',True)
           and(p.get('owner')==player or p.get('within_city_reach',False))}
    if not required<=nodes.keys():return None
    frontier={i for i,p in nodes.items()if p.get('owner')==-1 and p.get('native_purchasable')}
    if not frontier:return None
    owned={i for i,p in nodes.items()if p.get('owner')==player}
    def path(target,added):
        if target in added|owned:return ()
        # Virtual acquired tiles only open adjacent routes after that earlier
        # step. Current native frontier roots need no inferred ownership.
        roots=set(frontier)
        for i in added:
            roots.update(j for j in nodes[i].get('neighbors',())if j in nodes)
        heap=[]
        for i in roots:
            if i not in nodes:continue
            cost=0 if i in added|owned else(tiles[i].get('price',0)if tiles[i].get('price',0)>0 else 10000)
            route=()if i in added|owned else(i,)
            heapq.heappush(heap,(len(set(route)-required),cost,len(route),route,i))
        seen={}
        while heap:
            connectors,cost,length,route,i=heapq.heappop(heap)
            if len((set(route)|added)-required)>connector_limit:continue
            # The bounded node/path state preserves different usable connector
            # choices rather than pruning solely by distance to a hex.
            state=(i,frozenset(route));score=(connectors,cost,length,route)
            if state in seen and seen[state]<=score:continue
            seen[state]=score
            if i==target:return route
            if len(route)>=len(required)+connector_limit:continue
            for j in nodes[i].get('neighbors',()):
                if j not in nodes or j in route:continue
                extra=()if j in added|owned else(j,)
                new=route+extra
                if len((set(new)|added)-required)>connector_limit:continue
                extra_cost=0 if not extra else(tiles[j].get('price',0)if tiles[j].get('price',0)>0 else 10000)
                heapq.heappush(heap,(len(set(new)-required),cost+extra_cost,len(new),new,j))
        return None
    options=[]
    for order in itertools.permutations(sorted(required)):
        added=set();sequence=[]
        for target in order:
            route=path(target,added)
            if route is None:break
            for i in route:
                if i not in added:sequence.append(i);added.add(i)
        else:
            if len(added-required)>connector_limit:continue
            cost=sum(tiles[i].get('price',0)if tiles[i].get('price',0)>0 else 10000 for i in added)
            first=next((i for i in sequence if i in frontier),None)
            if first is not None:options.append(((len(added-required),cost,first not in materials,len(added),tuple(sequence)),tuple(sequence)))
    return min(options)[1]if options else None
