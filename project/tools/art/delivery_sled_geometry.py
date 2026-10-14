"""Remove the Mine payload without deleting runner vertices sharing its bone."""
import bmesh

def align_loading_deck(mesh, deck_ids):
    """Align the added platform to the two intact inner runner edges in plan."""
    import math
    from mathutils import Matrix, Vector
    # Measured original Mine edge endpoints. Match by position, not topology IDs.
    pairs = [((8.6384773,-11.3072796,9.8199825),(39.6330719,-13.3300200,4.2172370)),
             ((9.4621506,.7725677,9.7981892),(40.4145508,-1.2952501,4.1955452))]
    edges = []
    for pair in pairs:
        edge=[]
        for value in pair:
            p=Vector(value)
            v=min((v for v in mesh.data.vertices if v.index not in deck_ids),key=lambda v:(v.co-p).length_squared)
            assert (v.co-p).length<.0002, 'Unexpected Mine source; remeasure runner reference edges'
            edge.append(v.co.copy())
        edges.append(edge)
    axis=sum((Vector((b.x-a.x,b.y-a.y,0)).normalized() for a,b in edges),Vector()).normalized()
    angle=math.atan2(axis.y,axis.x)
    center=sum((mesh.data.vertices[i].co for i in deck_ids),Vector())/len(deck_ids)
    target=center.copy()
    target.y=sum(a.y+(center.x-a.x)*(b.y-a.y)/(b.x-a.x) for a,b in edges)/2
    rotation=Matrix.Rotation(angle,3,'Z')
    for i in deck_ids:mesh.data.vertices[i].co=target+rotation@(mesh.data.vertices[i].co-center)
    # The original Cart bone was for the payload, and yaws independently during
    # the gait. Primarily follow Sledge_R, retaining the small Cart contribution
    # of the opposite runner. All eight corners share one blend (planar deck).
    # 85/15 was checked against both runner axes across the authored gait.
    for group in mesh.vertex_groups:group.remove(deck_ids)
    mesh.vertex_groups['Sledge_R'].add(deck_ids,.85,'REPLACE')
    mesh.vertex_groups['Cart'].add(deck_ids,.15,'REPLACE')
    return {'yaw_degrees':math.degrees(angle),'old_center':list(center),'new_center':list(target),'deck_vertices':list(deck_ids),'deck_weights':{'Sledge_R':.85,'Cart':.15}}

def remove_native_payload(mesh):
    cart = mesh.vertex_groups['Cart'].index
    cart_vertices = {v.index for v in mesh.data.vertices
                     if any(g.group == cart and g.weight > .5 for g in v.groups)}
    adjacent = {v.index: set() for v in mesh.data.vertices}
    # The imported mesh splits vertices at UV/normal seams. Connect those seams
    # for selection only; do not weld or change the original export topology.
    seams = {}
    for v in mesh.data.vertices:
        seams.setdefault(tuple(round(x, 4) for x in v.co), []).append(v.index)
    for ids in seams.values():
        for i in ids:
            adjacent[i].update(ids)
    for e in mesh.data.edges:
        a, b = e.vertices
        adjacent[a].add(b)
        adjacent[b].add(a)
    unseen = set(adjacent)
    remove = set()
    while unseen:
        stack = [unseen.pop()]
        component = set(stack)
        while stack:
            for i in adjacent[stack.pop()] - component:
                component.add(i)
                unseen.discard(i)
                stack.append(i)
        # Crate and ore are entire Cart-only components. The right runner also
        # includes Sledge_F/Sledge_R, so its Cart-weighted vertices must survive.
        if component <= cart_vertices:
            remove.update(component)
    faces = sum(bool(set(p.vertices) & remove) for p in mesh.data.polygons)
    # Explicit contract for this measured donor; fail on unexpected source edits.
    assert len(remove) == 273 and faces == 236, (len(remove), faces)
    assert len(cart_vertices - remove) == 12
    bm = bmesh.new()
    bm.from_mesh(mesh.data)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in remove], context='VERTS')
    bm.to_mesh(mesh.data)
    bm.free()
    return {'removed_payload_vertices': len(remove), 'removed_payload_faces': faces,
            'retained_runner_cart_vertices': len(cart_vertices - remove)}
