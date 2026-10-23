"""Render sampled native movement in the saved assembly, and audit sail clearance."""
import bpy,json,sys,math
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
OUT=Path(sys.argv[sys.argv.index('--')+1]);NAME='CSC_BAKERS_Wind_Mill_Tower'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'review/sv/CSC_BAKERS_Wind_Mill_sv.blend'))
scene=bpy.context.scene;moving=[o for o in scene.objects if o.type=='MESH' and '/'+NAME+'_Sails/' in o.get('ae_semantic_path','')];assert len(moving)==1
ob=moving[0];base=[v.co.copy() for v in ob.data.vertices];normals=[n.vector.copy() for n in ob.data.corner_normals]
ts=np.load(OUT/'native-animation-transforms.npz')['Sails'];hub=Vector((26.99117,-41.48987,90.94731))
static={o.name:BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons]) for o in scene.objects if o.type=='MESH' and o!=ob}
blade_faces=[tuple(f.vertices) for f in ob.data.polygons if all((base[i]-hub).length>8 for i in f.vertices)]
collisions={}
for frame in range(0,301,5):
    t=Matrix(ts[frame].tolist());verts=[ob.matrix_world@(t@v) for v in base];bvh=BVHTree.FromPolygons(verts,blade_faces)
    for name,other in static.items():
        overlap=bvh.overlap(other)
        if overlap:collisions.setdefault(name,[]).append({'frame':frame+1,'pairs':len(overlap)})
(OUT/'sail-clearance.json').write_text(json.dumps(collisions,indent=2));print('CLEARANCE',collisions,flush=True)
# A tighter hero framing of the same saved assembly; placement and paint stay intact.
scene.camera.data.ortho_scale*=.69
scene.render.resolution_x=1100;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.cycles.samples=48
scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'Windmill-Tower.png');bpy.ops.render.render(write_still=True)
scene.render.resolution_x=650;scene.render.resolution_y=600;scene.cycles.samples=24
frames=OUT/'motion-frames';frames.mkdir(exist_ok=True)
for index,frame in enumerate(range(0,300,25)):
    t=Matrix(ts[frame].tolist());r=t.to_3x3()
    for v,p in zip(ob.data.vertices,base):v.co=t@p
    ob.data.normals_split_custom_set([(r@n).normalized() for n in normals]);ob.data.update()
    scene.render.filepath=str(frames/f'{index:03}.png');bpy.ops.render.render(write_still=True)
print('NATIVE_MOTION_RENDERED',flush=True)
