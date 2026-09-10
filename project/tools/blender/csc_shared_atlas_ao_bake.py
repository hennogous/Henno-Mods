"""
csc_shared_atlas_ao_bake.py
===========================

Bake geometry-correct ambient occlusion into a SHARED texture atlas for a set of
Civ VI building models, replacing script-derived (base-colour-cavity) AO with real
Cycles AO baked from the mesh -- WITHOUT giving up the UV1 texture reuse that the
atlas depends on.

Run headless, one atlas at a time:

    blender --background --python csc_shared_atlas_ao_bake.py

or paste/exec the functions via the Blender MCP bridge (how it was originally
developed). Configure the ATLAS job in the CONFIG block near the bottom.

--------------------------------------------------------------------------------
WHY THIS EXISTS
--------------------------------------------------------------------------------
CSC building families share one 1K atlas, split into 512-px quadrants; within a
quadrant the base-colour / normal / gloss / metal / AO content is shared across
several models. UV1 overlaps aggressively (identical wall segments stacked on one
patch) which is fine for MATERIAL properties -- oak is oak wherever it sits.

AO is different: it is a POSITIONAL property (where a face sits relative to
everything around it). With overlapping UV1 you cannot bake real AO -- many faces
fight for the same texels. The engine samples AO through UV2 (TEXCOORD_1), so the
fix is: give UV2 a non-overlapping layout, bake geometric AO into it, and let
model variants SHARE the parent's baked texels wherever they reuse the parent's
UV1 content. See project/docs/shared-atlas-ao.md for the full write-up.

--------------------------------------------------------------------------------
CORE CONCEPTS
--------------------------------------------------------------------------------
family      : a parent building + variants that are DUPLICATES of it (a CON+PIL
              damage state, a smaller version, etc). Variants inherit UV1 by
              duplication, so "same UV1" == "same kit piece".
quadrant    : the (u0,u1,v0,v1) sub-rect of the atlas this family owns.
union mesh  : temporary mesh = parent's full face set + only the genuinely-unique
              faces of the variants. Packed ONCE so all islands negotiate space
              together (no reservation step). Its packed layout defines UV2.
records     : dict  normalized-UV1-key -> [(uv2 loops, 3D centre), ...]  for
              EXACT reuse (a variant face with bit-identical UV1 to a union face).
reg / T     : per parent PACK-ISLAND, its UV1 polygons + 3D centres + a UV1->UV2
              similarity transform, for COVERAGE reuse (a variant face whose UV1
              footprint lies inside a parent island -- e.g. a broken half-wall).

--------------------------------------------------------------------------------
TWO BUGS THIS VERSION FIXES (both were real, both are subtle)
--------------------------------------------------------------------------------
1. FIRST-HIT BIAS. When several parent islands can host a coverage face, pick the
   one nearest in 3D, not the first found -- so a ground-level fragment samples the
   parent piece at ground level, not a look-alike up under the eaves.

2. UV2-CONNECTIVITY ISLANDS (the important one). Island transforms MUST be derived
   from UV2 connectivity (the actual pack units), NOT UV1 connectivity. The twin
   tie-break can cross-assign UV2 slots between twin faces, so a single UV1-
   connected cluster ends up pointing into TWO different packed islands. No single
   similarity fits that, and coverage faces assigned to such a Frankenstein cluster
   get a garbage transform and fly outside the quadrant (scaled/rotated wrong).
   Clustering by UV2 gives clean single-pack-unit islands (residual ~0.001 px).

The transform itself is a least-squares complex similarity (robust to sliver
islands) rather than the original two-farthest-points solve.

--------------------------------------------------------------------------------
WHAT IT DOES NOT TOUCH
--------------------------------------------------------------------------------
- UV1, materials, geometry: untouched (only UV2 is written).
- Bake writes with Clear Image OFF, so other families' quadrants survive.
- Re-resolving variants after a fix is UV2-write-only: no repack, no re-bake,
  parent files + baked atlas stay valid.

--------------------------------------------------------------------------------
KNOWN GOTCHAS (all handled here, all seen in real CSC files)
--------------------------------------------------------------------------------
- Bake targets the ACTIVE image node of the material and the ACTIVE uv layer of
  the mesh. Wrong active node -> you overwrite base colour. Wrong active uv ->
  scrambled bake.
- AO rays see the whole scene: isolate each model (hide others from RENDER) before
  baking or neighbours cast phantom shadows.
- New Blender images default to sRGB; every data map (AO/N/G/M) must be Non-Color.
- Files saved in Edit Mode expose empty mesh data to scripts -> force Object Mode.
- Auto-pack ("Automatically Pack Resources") silently embeds external textures on
  save -> disabled before every save.
- AO ray distance is scale-relative: rescale it if mesh scale changes, then re-bake.
- Degenerate zero-area-UV faces (dummies) are left untouched throughout.
"""

import bpy, bmesh, math, json
from collections import defaultdict
from mathutils import Vector

# ------------------------------------------------------------------ UV helpers

UV_MATCH = 5e-4          # loop-UV equality tolerance for island edge-walking
KEY_ROUND = 4            # decimals for the UV1 identity key (~1/6500 uv, sub-texel)
COVER_TOL = 3.0 / 1024   # dilation (px @1K) for the coverage point-in-island test
COVER_SHRINK = 0.02      # shrink face corners toward centroid before coverage test


def norm_seq(seq):
    """Rotate a loop sequence so its lexicographically smallest entry is first.
    Makes face keys rotation-invariant; returns (tuple, rotation_offset_k)."""
    k = min(range(len(seq)), key=lambda i: seq[i])
    return tuple(seq[k:] + seq[:k]), k


def face_uv_normalized(uv_layer, poly):
    """Loop UVs of a face, UDIM-normalized (floor of the min corner removed) so a
    face that wrapped past an integer boundary compares against the base tile."""
    l0, n = poly.loop_start, poly.loop_total
    pts = [Vector(uv_layer.data[l0 + i].uv) for i in range(n)]
    du = math.floor(min(a.x for a in pts))
    dv = math.floor(min(a.y for a in pts))
    if du or dv:
        pts = [Vector((a.x - du, a.y - dv)) for a in pts]
    return pts


def is_degenerate(pts):
    """True for a zero-area-UV dummy face (all loops at one point)."""
    return max(abs(a.x - pts[0].x) + abs(a.y - pts[0].y) for a in pts) < 1e-4


def islands_by(me, layer_name):
    """Cluster faces into UV islands by walking mesh edges whose loop UVs match on
    both sides. Pass 'UV2' to get the true pack units (REQUIRED for transforms);
    'UV1' for authoring islands (used only when building the union)."""
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    luv = bm.loops.layers.uv[layer_name]
    parent = list(range(len(bm.faces)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a

    for e in bm.edges:
        lf = e.link_faces
        if len(lf) != 2:
            continue
        f1, f2 = lf
        d1 = {l.vert.index: Vector(l[luv].uv) for l in f1.loops if l.vert in e.verts}
        d2 = {l.vert.index: Vector(l[luv].uv) for l in f2.loops if l.vert in e.verts}
        if all((d1[k] - d2[k]).length < UV_MATCH for k in d1):
            ra, rb = find(f1.index), find(f2.index)
            if ra != rb:
                parent[ra] = rb
    result = {f.index: find(f.index) for f in bm.faces}
    bm.free()
    return result


def point_in_poly(pt, poly):
    n = len(poly); sign = 0
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        cr = (b.x - a.x) * (pt.y - a.y) - (b.y - a.y) * (pt.x - a.x)
        if abs(cr) < 1e-9:
            continue
        s = 1 if cr > 0 else -1
        if sign == 0:
            sign = s
        elif s != sign:
            return False
    return True


def _dist_pt_seg(p, a, b):
    ab = b - a
    t = max(0, min(1, (p - a).dot(ab) / max(ab.length_squared, 1e-12)))
    return (p - (a + ab * t)).length


def near_poly(pt, poly, tol):
    if point_in_poly(pt, poly):
        return True
    return min(_dist_pt_seg(pt, poly[i], poly[(i + 1) % len(poly)])
               for i in range(len(poly))) <= tol


def lsq_similarity(pairs):
    """Least-squares complex similarity  q = w*p + t  (rotation + uniform scale +
    translation, NO reflection) over (uv1, uv2) point pairs. Robust to sliver
    islands where the two-farthest-points solve is numerically unstable.
    Returns (tx, ty, cr, ci) where w = cr + i*ci, or None if degenerate."""
    n = len(pairs)
    ax = sum(a.x for a, _ in pairs) / n; ay = sum(a.y for a, _ in pairs) / n
    bx = sum(b.x for _, b in pairs) / n; by = sum(b.y for _, b in pairs) / n
    nr = ni = den = 0.0
    for a, b in pairs:
        pax, pay = a.x - ax, a.y - ay
        qbx, qby = b.x - bx, b.y - by
        nr += qbx * pax + qby * pay
        ni += qby * pax - qbx * pay
        den += pax * pax + pay * pay
    if den < 1e-15:
        return None
    cr, ci = nr / den, ni / den
    tx = bx - (cr * ax - ci * ay)
    ty = by - (ci * ax + cr * ay)
    return (tx, ty, cr, ci)


def apply_T(T, x, y):
    tx, ty, cr, ci = T
    return (tx + cr * x - ci * y, ty + ci * x + cr * y)


# ------------------------------------------------------------- scene management

def append_mesh(path, obj_name, alias):
    """Append one mesh object from a .blend, rename it FAM_<alias>, link to scene."""
    before = {o.name for o in bpy.data.objects}
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [obj_name]
    new = [o for o in bpy.data.objects
           if o.name not in before and o.type == 'MESH']
    assert len(new) == 1, f"{alias}: expected 1 mesh, got {[o.name for o in new]}"
    o = new[0]; o.name = f'FAM_{alias}'
    bpy.context.scene.collection.objects.link(o)
    return o


def ensure_object_mode(obj):
    """Force an object to Object Mode even if its .blend was saved in Edit Mode."""
    if obj.mode == 'OBJECT':
        return
    bpy.context.view_layer.objects.active = obj
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                region = [r for r in area.regions if r.type == 'WINDOW'][0]
                with bpy.context.temp_override(
                        window=window, area=area, region=region,
                        active_object=obj, object=obj, edit_object=obj,
                        selected_objects=[obj]):
                    bpy.ops.object.mode_set(mode='OBJECT')
                return


# --------------------------------------------------------------- classification

def classify_family(members):
    """Decide, per member, which faces it CONTRIBUTES (owns unique texels) vs
    SHARES with an earlier member (exact key match or UV1-footprint coverage).

    members : ordered list of FAM_<alias>. First is the parent (contributes all).
              For INDEPENDENT buildings that must NOT share, call once per building
              with its own [parent, cp] and keep the seen-set separate (see
              run_atlas: pass scope_shared=False to reset between buildings).

    Returns contribute{alias:[face_idx]}, cover_assign{f'{alias}:{fidx}':island_root}.
    Coverage uses UV1-connectivity islands here only to define candidate footprints;
    the actual transforms are rebuilt from UV2 connectivity later.
    """
    seen = set()
    registry = {}   # (alias, uv1_island_root) -> {'polys':[...], 'c3d':[...]}
    contribute = {}
    cover_assign = {}
    for mi, alias in enumerate(members):
        me = bpy.data.objects[f'FAM_{alias}'].data
        uv1 = me.uv_layers['UV1']
        isl = islands_by(me, 'UV1')
        keep = []
        for p in me.polygons:
            pts = face_uv_normalized(uv1, p)
            if is_degenerate(pts):
                continue
            u1r = [tuple(round(c, KEY_ROUND) for c in a) for a in pts]
            key, _ = norm_seq(u1r)
            keyr, _ = norm_seq(list(reversed(u1r)))
            if mi > 0 and (key in seen or keyr in seen):
                continue                                   # exact reuse
            if mi > 0:                                     # try coverage reuse
                c = sum(pts, Vector((0, 0))) / len(pts)
                test = [a.lerp(c, COVER_SHRINK) for a in pts]
                c3 = Vector(p.center)
                hits = []
                for rk, reg in registry.items():
                    ok = True
                    for tp in test:
                        if not any(near_poly(tp, poly, COVER_TOL) for poly in reg['polys']
                                   if min(v.x for v in poly) - COVER_TOL - 0.002 <= tp.x <= max(v.x for v in poly) + COVER_TOL + 0.002
                                   and min(v.y for v in poly) - COVER_TOL - 0.002 <= tp.y <= max(v.y for v in poly) + COVER_TOL + 0.002):
                            ok = False
                            break
                    if ok:
                        hits.append((min((c3 - cc).length for cc in reg['c3d']), rk))
                if hits:
                    cover_assign[f'{alias}:{p.index}'] = min(hits)[1]   # nearest-3D
                    continue
            seen.add(key)
            keep.append(p.index)
            reg = registry.setdefault((alias, isl[p.index]), {'polys': [], 'c3d': []})
            reg['polys'].append(pts)
            reg['c3d'].append(Vector(p.center))
        contribute[alias] = keep
    return contribute, cover_assign


# ------------------------------------------------------------------ union + pack

def build_and_pack_union(all_members, contribute, quad, pack_margin=0.006):
    """Duplicate each member's contributed faces into one union mesh, pack it in
    0-1, then affine-remap into the family quadrant. Returns (union_obj,
    provenance list [(alias, orig_face_idx)] aligned to union.polygons order)."""
    for o in list(bpy.data.objects):
        if o.name.startswith('UNION'):
            bpy.data.objects.remove(o, do_unlink=True)
    dups = []
    provenance = []
    for alias in all_members:
        keep = sorted(contribute.get(alias, []))
        if not keep:
            continue
        src = bpy.data.objects[f'FAM_{alias}']
        d_me = src.data.copy()
        d = bpy.data.objects.new(f'UNION_{alias}', d_me)
        bpy.context.scene.collection.objects.link(d)
        ks = set(keep)
        bm = bmesh.new(); bm.from_mesh(d_me); bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in ks],
                         context='FACES')
        bm.to_mesh(d_me); bm.free()
        provenance += [(alias, fi) for fi in keep]   # survivors keep ascending order
        dups.append(d)

    bpy.context.view_layer.objects.active = dups[0]
    for o in bpy.context.view_layer.objects:
        o.select_set(o.name.startswith('UNION_'))
    if len(dups) > 1:
        bpy.ops.object.join()
    union = bpy.context.view_layer.objects.active
    union.name = 'UNION'
    me = union.data
    uv1, uv2 = me.uv_layers['UV1'], me.uv_layers['UV2']
    for p in me.polygons:
        pts = face_uv_normalized(uv1, p)
        for i in range(p.loop_total):
            uv2.data[p.loop_start + i].uv = pts[i]
    me.uv_layers.active = uv2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True, margin_method='ADD', margin=pack_margin)
    bpy.ops.object.mode_set(mode='OBJECT')
    q0u, q1u, q0v, q1v = quad
    su, sv = q1u - q0u, q1v - q0v
    for i in range(len(uv2.data)):
        x, y = uv2.data[i].uv
        uv2.data[i].uv = (q0u + x * su, q0v + y * sv)
    return union, provenance


# ---------------------------------------------------------------- parent lookup

def build_parent_lookup(parent_alias):
    """From a resolved parent mesh (UV1 authored + UV2 packed & baked), build:
      records : exact-reuse map  key -> [(uv2 loops, 3D centre)]
      reg     : per UV2-PACK-ISLAND {'polys','c3d','T'} for coverage reuse.

    *** THE FIX ***: islands are clustered by UV2 connectivity so each is a single
    rigid pack unit and its least-squares similarity is exact (residual ~0). UV1
    clustering here would merge twin-cross-assigned faces and yield garbage T."""
    me = bpy.data.objects[f'FAM_{parent_alias}'].data
    uv1, uv2 = me.uv_layers['UV1'], me.uv_layers['UV2']
    isl = islands_by(me, 'UV2')
    groups = defaultdict(list)
    for f, r in isl.items():
        groups[r].append(f)
    records = {}
    reg = {}
    for root, faces in groups.items():
        pairs, polys, c3d = [], [], []
        for f in faces:
            p = me.polygons[f]
            pts1 = face_uv_normalized(uv1, p)
            if is_degenerate(pts1):
                continue
            l0, n = p.loop_start, p.loop_total
            pts2 = [Vector(uv2.data[l0 + i].uv) for i in range(n)]
            u1r = [tuple(round(c, KEY_ROUND) for c in a) for a in pts1]
            key, k = norm_seq(u1r)
            records.setdefault(key, []).append(
                ([tuple(pts2[(k + i) % n]) for i in range(n)], Vector(p.center)))
            pairs += [(pts1[i], pts2[i]) for i in range(n)]
            polys.append(pts1)
            c3d.append(Vector(p.center))
        if len(pairs) >= 2:
            T = lsq_similarity(pairs)
            if T:
                reg[root] = {'polys': polys, 'c3d': c3d, 'T': T}
    return records, reg


def resolve_member(alias, records, reg, quad=None):
    """Write UV2 on a member: exact-key reuse first (nearest-3D among twins), then
    UV1-footprint coverage (nearest-3D among covering UV2 pack-islands, clean T).
    Faces that match nothing keep their existing (own-baked) UV2. Returns stats;
    if quad given, also counts faces that ended up outside the quadrant (should 0)."""
    me = bpy.data.objects[f'FAM_{alias}'].data
    u1l, u2l = me.uv_layers['UV1'], me.uv_layers['UV2']
    exact = covered = kept = outside = 0
    for p in me.polygons:
        pts = face_uv_normalized(u1l, p)
        l0, n = p.loop_start, p.loop_total
        if is_degenerate(pts):
            kept += 1
        else:
            u1r = [tuple(round(c, KEY_ROUND) for c in a) for a in pts]
            ctr = Vector(p.center)
            key, k = norm_seq(u1r)
            cands = records.get(key)
            if cands:
                u2v = min(cands, key=lambda c: (c[1] - ctr).length)[0]
                for i in range(n):
                    u2l.data[l0 + (k + i) % n].uv = u2v[i]
                exact += 1
            else:
                keyr, kr = norm_seq(list(reversed(u1r)))
                cands = records.get(keyr)
                if cands:
                    u2v = min(cands, key=lambda c: (c[1] - ctr).length)[0]
                    for i in range(n):
                        u2l.data[l0 + (n - 1 - ((kr + i) % n))].uv = u2v[i]
                    exact += 1
                else:
                    c = sum(pts, Vector((0, 0))) / len(pts)
                    test = [a.lerp(c, COVER_SHRINK) for a in pts]
                    hits = []
                    for rid, r in reg.items():
                        ok = True
                        for tp in test:
                            if not any(near_poly(tp, poly, COVER_TOL) for poly in r['polys']
                                       if min(v.x for v in poly) - COVER_TOL - 0.002 <= tp.x <= max(v.x for v in poly) + COVER_TOL + 0.002
                                       and min(v.y for v in poly) - COVER_TOL - 0.002 <= tp.y <= max(v.y for v in poly) + COVER_TOL + 0.002):
                                ok = False
                                break
                        if ok:
                            hits.append((min((ctr - cc).length for cc in r['c3d']), rid))
                    if hits:
                        T = reg[min(hits)[1]]['T']
                        for i in range(n):
                            u2l.data[l0 + i].uv = apply_T(T, pts[i].x, pts[i].y)
                        covered += 1
                    else:
                        kept += 1
        if quad is not None:
            q0u, q1u, q0v, q1v = quad
            fp = [Vector(u2l.data[l0 + i].uv) for i in range(n)]
            if any(pt.x < q0u - 0.02 or pt.x > q1u + 0.02
                   or pt.y < q0v - 0.02 or pt.y > q1v + 0.02 for pt in fp):
                outside += 1
    me.update()
    return {'exact': exact, 'covered': covered, 'kept': kept,
            'faces_outside_quadrant': outside}


# ------------------------------------------------------------------------ bake

def bake_ao(atlas_png, alias_order, ao_distance=30.0, samples=128,
            clear_quadrant=None):
    """Bake AO into the shared atlas, one model at a time, Clear Image OFF.
    alias_order: bake damage/variant models FIRST, parents LAST, so parents
    overwrite shared texels with canonical intact-geometry AO. clear_quadrant
    (u0,u1,v0,v1) optional: white-fill that rect first for a fresh quadrant."""
    img = bpy.data.images.get('CSC_Atlas_AO2')
    if img:
        bpy.data.images.remove(img)
    img = bpy.data.images.load(atlas_png)
    img.name = 'CSC_Atlas_AO2'
    img.colorspace_settings.name = 'Non-Color'
    if clear_quadrant:
        import numpy as np
        W, H = img.size
        buf = np.empty(W * H * 4, dtype=np.float32)
        img.pixels.foreach_get(buf)
        px = buf.reshape(H, W, 4)
        u0, u1, v0, v1 = clear_quadrant
        px[int(v0 * H):int(v1 * H), int(u0 * W):int(u1 * W), 0:3] = 1.0
        img.pixels.foreach_set(px.ravel())

    for alias in alias_order:
        for slot in bpy.data.objects[f'FAM_{alias}'].material_slots:
            m = slot.material
            if not m:
                continue
            m.use_nodes = True
            node = next((n for n in m.node_tree.nodes if n.name == 'TMP_BAKE'), None) \
                or m.node_tree.nodes.new('ShaderNodeTexImage')
            node.name = 'TMP_BAKE'; node.image = img
            for n in m.node_tree.nodes:
                n.select = False
            node.select = True
            m.node_tree.nodes.active = node

    sc = bpy.context.scene
    if sc.world is None:
        sc.world = bpy.data.worlds.new('World')
    sc.world.light_settings.distance = ao_distance
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = samples
    sc.cycles.device = 'CPU'
    sc.render.bake.margin = 4
    sc.render.bake.use_clear = False

    fam = {a: bpy.data.objects[f'FAM_{a}'] for a in alias_order}
    for alias in alias_order:
        cur = fam[alias]
        for a, o in fam.items():
            o.hide_render = (o != cur)
            o.hide_set(o != cur)
        cur.data.uv_layers.active = cur.data.uv_layers['UV2']
        bpy.context.view_layer.objects.active = cur
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        cur.select_set(True)
        bpy.ops.object.bake(type='AO')

    img.filepath_raw = atlas_png
    img.file_format = 'PNG'
    img.save()


# ----------------------------------------------------------------- write-back

def write_uv2(blend_path, jobs):
    """Open a source .blend, copy computed UV2 arrays onto its objects by index,
    disable auto-pack, save. jobs: [(alias, obj_name, uv2_flat_array)]."""
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    for alias, obj_name, arr in jobs:
        obj = bpy.data.objects[obj_name]
        obj.hide_viewport = False
        try:
            obj.hide_set(False)
        except Exception:
            pass
        ensure_object_mode(obj)
        uv2 = obj.data.uv_layers['UV2']
        assert len(uv2.data) * 2 == len(arr), f'{alias}: loop count mismatch'
        uv2.data.foreach_set('uv', arr)
        obj.data.update()
    bpy.data.use_autopack = False
    bpy.ops.wm.save_mainfile()


def dump_uv2(alias):
    uv2 = bpy.data.objects[f'FAM_{alias}'].data.uv_layers['UV2']
    return [round(float(c), 6) for i in range(len(uv2.data)) for c in uv2.data[i].uv]


# =============================================================================
# CONFIG  --  describe ONE atlas job, then call run_atlas().
# =============================================================================
# Each FAMILY is a group that SHARES texels internally: parent first, then its
# variants. INDEPENDENT buildings that must NOT share (e.g. Storage S/M/L) are
# separate families with independent=True -- they still co-pack the same quadrant
# (no overlap, packer allocates area by size) but never share texels cross-family.
#
# A member is (alias, blend_path, object_name).  quadrant is (u0,u1,v0,v1).
# bake_order lists aliases variants-first, parents-last.
#
# Example (the Storage quadrant, three independent buildings each with a CON+PIL):
#
#   ATLAS_PNG = ".../Textures/CSC_Atlas_AO2.png"
#   QUADRANT  = (0.505, 0.995, 0.005, 0.495)          # bottom-right
#   FAMILIES  = [
#     {"independent": True, "members": [
#         ("SS",   ".../CSC_Storage_S.blend",         "CSC_Storage_S_Bdg"),
#         ("SSCP", ".../CSC_Storage_S_CON+PIL.blend", "CSC_Storage_S_CON+PIL_Bdg")]},
#     {"independent": True, "members": [
#         ("SM",   ".../CSC_Storage_M.blend",         "CSC_Storage_M_Bldg"),
#         ("SMCP", ".../CSC_Storage_M_CON+PIL.blend", "CSC_Storage_M_CON+PIL_Bldg")]},
#     {"independent": True, "members": [
#         ("SL",   ".../CSC_Storage_L.blend",         "CSC_Storage_L_Bldg"),
#         ("SLCP", ".../CSC_Storage_L_CON+PIL.blend", "CSC_Storage_L_CON+PIL_Bldg")]},
#   ]
#   BAKE_ORDER = ["SMCP","SLCP","SS","SM","SL"]        # variants first, parents last
#   CLEAR_QUADRANT = QUADRANT                          # fresh canvas for this quadrant
# =============================================================================


def run_atlas(atlas_png, quadrant, families, bake_order,
              clear_quadrant=None, ao_distance=30.0):
    """Full pipeline for one atlas job. Families sharing texels list parent-first;
    families with independent=True never share cross-family but co-pack the quadrant.

    IMPORTANT: this computes and BAKES using appended copies in a scratch scene,
    then writes UV2 back to the source .blends grouped by file. Re-running only the
    resolve+write (no union/pack/bake) is enough after a resolver fix, because the
    parent UV2 and baked atlas are already valid."""
    bpy.ops.wm.read_homefile(use_empty=True)

    all_members = []
    for fam in families:
        for alias, path, obj in fam["members"]:
            append_mesh(path, obj, alias)
            all_members.append(alias)

    # classify per family (independent families reset the shared seen-set)
    contribute = {}
    cover = {}
    for fam in families:
        aliases = [m[0] for m in fam["members"]]
        c, cv = classify_family(aliases)
        contribute.update(c)
        cover.update(cv)

    _, provenance = build_and_pack_union(all_members, contribute, quadrant)
    # (provenance/union kept transient; parent lookups are rebuilt from resolved UV2)

    # bake into the shared atlas
    bake_ao(atlas_png, bake_order, ao_distance=ao_distance,
            clear_quadrant=clear_quadrant)

    # resolve every member's UV2 against its own family's parent lookup
    per_file = defaultdict(list)
    for fam in families:
        parent_alias = fam["members"][0][0]
        records, reg = build_parent_lookup(parent_alias)
        for alias, path, obj in fam["members"]:
            stats = resolve_member(alias, records, reg, quad=quadrant)
            print(alias, stats)
            per_file[path].append((alias, obj, dump_uv2(alias)))

    # write back grouped by source file
    for path, jobs in per_file.items():
        write_uv2(path, jobs)
        print("saved", path)


if __name__ == "__main__":
    # Fill in a CONFIG (see the block above) and call run_atlas(...).
    # Left intentionally inert so importing/execing the module has no side effects.
    print("csc_shared_atlas_ao_bake: configure run_atlas(...) before running.")
