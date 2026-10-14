"""Check the loaded donkey's storage approach against the building's surfaces."""
import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
building=bpy.data.objects['CSC_Storage_L_Bldg']
body=bpy.data.objects['CSC_Delivery_Donkey_Mesh']
bale=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH' and 'Textile_Bale' in o.name)
def surface(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 verts=[e.matrix_world@v.co for v in m.vertices]
 tree=BVHTree.FromPolygons(verts,[list(p.vertices) for p in m.polygons])
 e.to_mesh_clear();return verts,tree
s.frame_set(1);_,wall=surface(building)
collisions=[];points=[];frames=[]
route=json.loads((OUT/'authoring-check.json').read_text())['route_record']
for f in range(1,722,3):
 if route[str(f)][1]<=70:continue
 s.frame_set(f);frames.append(f)
 for o in (body,bale):
  verts,tree=surface(o);points.extend(verts)
  overlaps=wall.overlap(tree)
  if overlaps:collisions.append({'frame':f,'mesh':o.name,'surface_intersections':len(overlaps)})
result={'sampled_frames':frames,'building_surface_intersections':collisions,
 'loaded_swept_bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]],
 'scope':'Loaded outbound approach where route origin Y > 70; body, sled and bale against storage building surfaces.'}
(OUT/'storage-clearance-check.json').write_text(json.dumps(result,indent=2))
assert frames and not collisions,result
print('STORAGE_CLEARANCE_PASS',json.dumps(result))
