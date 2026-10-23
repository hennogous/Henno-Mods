"""Widen the installed plaster windmill's four sail frames without changing UVs/rig."""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[sys.argv.index('--') + 1])
NAME = 'CSC_BAKERS_Wind_Mill_Tower'
SOURCE = Path.home() / 'Desktop/Working Files/3D Art/BAKERS/Wind Mill/tower'
FACTOR = 1.35
TAPER = '--taper' in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(SOURCE / (NAME + '.blend')), load_ui=False, use_scripts=False)
scene = bpy.data.scenes['Export']; bpy.context.window.scene = scene; scene.frame_set(1)
rig = bpy.data.objects[NAME]
rotor = bpy.data.objects[NAME + '_Sails']; tower = bpy.data.objects[NAME + '_Tower']
assert len(rotor.data.vertices) == 518
if TAPER:
    assert abs(rotor.get('sail_width_factor',0)-FACTOR)<1e-6
    assert not rotor.get('sail_inner_width_fraction'), 'Already tapered.'
else:
    assert not rotor.get('sail_width_factor'), 'Already widened; refusing to apply twice.'
before_tower = [tuple(v.co) for v in tower.data.vertices]
before_uvs = [[tuple(v.uv) for v in layer.data] for layer in rotor.data.uv_layers]
before_hub = [tuple(v.co) for v in rotor.data.vertices[456:]]
right = Vector((math.sqrt(3)/2, -.5, 0)); up = Vector((0, 0, 1))
hub = Vector((26.99117, -41.48987, 90.94731))
for blade in range(0 if TAPER else 4):
    angle = math.radians(22.5 + blade*90)
    across = right*math.cos(angle) - up*math.sin(angle)
    start = blade*114
    for local in range(114):
        vertex = rotor.data.vertices[start + local]
        if local < 16:
            side = -1 if local < 8 else 1
            vertex.co += across*(side*4.5*(FACTOR-1))
        elif local < 82:
            vertex.co += across*((vertex.co-hub).dot(across)*(FACTOR-1))
        else:
            side = -1 if ((local-82)//8)%2 == 0 else 1
            vertex.co += across*(side*4.5*(FACTOR-1))
if TAPER:
    sys.path.insert(0,str(Path(__file__).parent))
    from windmill_sail_shape import taper_sails, INNER_WIDTH
    positions=taper_sails([v.co.copy() for v in rotor.data.vertices],FACTOR)
    for vertex,position in zip(rotor.data.vertices,positions):vertex.co=position
    rotor['sail_inner_width_fraction']=INNER_WIDTH
rotor.data.update(); rotor['sail_width_factor'] = FACTOR
assert before_tower == [tuple(v.co) for v in tower.data.vertices]
assert before_uvs == [[tuple(v.uv) for v in layer.data] for layer in rotor.data.uv_layers]
assert before_hub == [tuple(v.co) for v in rotor.data.vertices[456:]]

# Keep the established UV2 packing and tower AO. Bake only the changed rotor.
ao = rotor.data.materials[-1].node_tree.nodes['AO bake target'].image
original_path = str((SOURCE / (NAME + '_AO.png')).resolve())
ao.filepath = original_path; ao.reload()
before_pixels = list(ao.pixels)
scene.render.engine = 'CYCLES'; scene.cycles.samples = 64
scene.render.bake.margin = 4; scene.render.bake.use_clear = False
scene.world.light_settings.distance = 9
for mat in rotor.data.materials:
    mat.node_tree.nodes.active = mat.node_tree.nodes['AO bake target']
bpy.ops.object.select_all(action='DESELECT'); rotor.select_set(True)
bpy.context.view_layer.objects.active = rotor; rotor.data.uv_layers.active_index = 1
tower.hide_render = True
bpy.ops.object.bake(type='AO')
tower.hide_render = False
rotor.data.uv_layers.active_index = 0; rotor.data.uv_layers[0].active_render = True
# Protect every texel covered by the stationary tower, with its bake padding.
import numpy as np
mask = np.zeros((512, 512), dtype=bool)
uv = tower.data.uv_layers['UV2']
for face in tower.data.polygons:
    points = np.array([tuple(uv.data[i].uv) for i in face.loop_indices])*512
    for j in range(1, len(points)-1):
        tri = points[[0, j, j+1]]
        lo = np.maximum(np.floor(tri.min(axis=0)).astype(int), 0)
        hi = np.minimum(np.ceil(tri.max(axis=0)).astype(int)+1, 512)
        yy, xx = np.mgrid[lo[1]:hi[1], lo[0]:hi[0]]
        signs = []
        for a, b in zip(tri, np.roll(tri, -1, axis=0)):
            signs.append((xx+.5-a[0])*(b[1]-a[1])-(yy+.5-a[1])*(b[0]-a[0]))
        inside = np.all(np.array(signs)>=0, axis=0) | np.all(np.array(signs)<=0, axis=0)
        mask[lo[1]:hi[1], lo[0]:hi[0]] |= inside
padded = np.pad(mask, 4)
mask = np.logical_or.reduce([padded[y:y+512, x:x+512] for y in range(9) for x in range(9)])
pixels = list(ao.pixels)
protected = 0
for i, value in enumerate(mask.ravel()):
    if value:
        pixels[i*4:i*4+4] = before_pixels[i*4:i*4+4]; protected += 1
ao.pixels[:] = pixels
target_ao = OUT / 'staged-textures' / (NAME + '_AO.png')
target_ao.parent.mkdir(parents=True, exist_ok=True)
ao.filepath_raw = str(target_ao); ao.file_format = 'PNG'; ao.save()
ao.filepath_raw = original_path
for image in bpy.data.images:
    if image.source == 'FILE': image.filepath = str(Path(bpy.path.abspath(image.filepath)).resolve())
bpy.ops.object.select_all(action='DESELECT')
for ob in (rig, rotor, tower): ob.select_set(True)
bpy.context.view_layer.objects.active = rig
target = OUT / 'new-tower' / (NAME + '.blend'); target.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(target), relative_remap=False)
sys.path.insert(0, str(ROOT / 'project/tools/scripts'))
import io_export_cn6_b4
geo = OUT / 'staged/Geometries' / (NAME + '.cn6'); geo.parent.mkdir(parents=True, exist_ok=True)
io_export_cn6_b4.do_export(str(geo), True, True)
(OUT / 'width-revision.json').write_text(json.dumps(dict(width_factor=FACTOR,
    tapered=TAPER,inner_width_fraction=INNER_WIDTH if TAPER else 1,
    rung_span_before=10.5, rung_span_after=10.5*FACTOR,
    cloth_span_before=8.6, cloth_span_after=8.6*FACTOR,
    tower_geometry_unchanged=True, rotor_uvs_unchanged=True, hub_unchanged=True,
    protected_tower_ao_pixels=protected), indent=2))
print('TAPERED_SAILS' if TAPER else 'WIDENED_SAILS', FACTOR, flush=True)
