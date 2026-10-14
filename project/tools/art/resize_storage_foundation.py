"""Extend both arch surrounds to foundation depth, then resize the static shell."""
import bpy,bmesh,json,hashlib,sys
from pathlib import Path
from mathutils import Matrix,Vector
SOURCE=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L\CSC_Storage_L.blend')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\foundation-scale-20261009')
OLD=OUT.parent/'interior-20261008'
SCALE=.9
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
inventory=json.loads((OUT/'source.json').read_text())
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==inventory['source_sha256'],'Source changed during inspection'
M=Matrix(json.loads((OLD/'source-transform.json').read_text())['matrix'])
historical=json.loads((OLD/'CSC_Storage_L_before_rig_20261008-114851.blend.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));o=bpy.data.objects['CSC_Storage_L_Bldg'];m=o.data
assert o.matrix_world==Matrix.Identity(4)
assert len([x for x in bpy.data.objects if x.type=='MESH'])==1
assert all(g.name=='Root' for g in o.vertex_groups if any(any(w.group==g.index and w.weight>.001 for w in v.groups) for v in m.vertices))
def sig(points):return tuple(sorted(tuple(round(x,3) for x in p) for p in points))
lookup={sig([m.vertices[i].co for i in p.vertices]):p.index for p in m.polygons}
arch_faces=[]
for name in ('CSC_Fixed_Front_Arch','CSC_Fixed_Left_Wing_Arch'):
 ref=next(x for x in historical['objects'] if x['name']==name)
 for face in ref['faces']:
  pts=[Vector(ref['vertices'][i]) for i in face];key=sig([M@p for p in pts])
  assert key in lookup,('Arch geometry changed',name)
  if min(v.z for v in pts)<.001:arch_faces.append(lookup[key])
assert len(arch_faces)==16
original_vertices=[v.co.copy() for v in m.vertices]
original_faces=[tuple(p.vertices) for p in m.polygons]
original_uvs={u.name:[tuple(l.uv) for l in u.data] for u in m.uv_layers}
normals=[tuple(n.vector) for n in m.corner_normals]
old_face_count=len(m.polygons);old_vert_count=len(m.vertices)
depth=min(v.co.z for v in m.vertices)
assert abs(depth+19.44)<.001,('Unexpected foundation depth',depth)
bm=bmesh.new();bm.from_mesh(m);bm.faces.ensure_lookup_table()
layers=[bm.loops.layers.uv.get(n) for n in original_uvs]
deform=bm.verts.layers.deform.verify();root=o.vertex_groups['Root'].index
for i in arch_faces:
 bm.faces.ensure_lookup_table()
 face=bm.faces[i]
 points=[]
 for loop in face.loops:
  p=loop.vert.co.copy();p.z=depth if abs(p.z)<.001 else 0
  v=bm.verts.new(p);v[deform][root]=1.;points.append(v)
 extension=bm.faces.new(points);extension.material_index=face.material_index;extension.smooth=face.smooth
 for a,b in zip(extension.loops,face.loops):
  for layer in layers:a[layer].uv=b[layer].uv
bm.to_mesh(m);bm.free();m.update()
assert len(m.vertices)==old_vert_count+64 and len(m.polygons)==old_face_count+16
assert [tuple(p.vertices) for p in m.polygons[:old_face_count]]==original_faces
assert all((m.vertices[i].co-p).length==0 for i,p in enumerate(original_vertices))
for name,uvs in original_uvs.items():assert [tuple(x.uv) for x in m.uv_layers[name].data[:len(uvs)]]==uvs
for p in m.polygons[old_face_count:]:normals.extend([tuple(p.normal)]*len(p.vertices))
m.normals_split_custom_set(normals)
marker=m.attributes.new('storage_arch_foundation','BOOLEAN','FACE')
for p in m.polygons:marker.data[p.index].value=p.index>=old_face_count
pivot=Vector((0,0,0)) if '--district-origin' in sys.argv else Vector((M.translation.x,M.translation.y,0))
for v in m.vertices:v.co=pivot+(v.co-pivot)*SCALE
m.update()
for i,p in enumerate(original_vertices):assert (m.vertices[i].co-(pivot+(p-pivot)*SCALE)).length<.00003
assert all(any(w.group==root and abs(w.weight-1)<1e-7 for w in v.groups) for v in m.vertices)
o['storage_resize_factor']=SCALE;o['storage_resize_pivot']=list(pivot)
o['storage_arch_foundation']='Both entrance surrounds continue from grade to the existing buried foundation depth.'
for image in bpy.data.images:
 if image.source=='FILE':image.filepath=bpy.path.abspath(image.filepath)
report={'source_sha256':inventory['source_sha256'],'scale_factor_relative_to_current_source':SCALE,'pivot':list(pivot),
 'original_vertices':old_vert_count,'vertices':len(m.vertices),'original_faces':old_face_count,'faces':len(m.polygons),
 'extension_faces':list(range(old_face_count,len(m.polygons))),'source_arch_faces':arch_faces,
 'foundation_bottom_before':depth,'foundation_bottom_after':depth*SCALE,
 'retained_uvs_unchanged':True,'static_root_weights_verified':True,
 'original_upper_floor_z':(M@Vector((0,0,46.55539321899414))).z,
 'resized_upper_floor_z':(M@Vector((0,0,46.55539321899414))).z*SCALE,
 'placement_matrix_before':[list(r) for r in M]}
(OUT/'edit-check.json').write_text(json.dumps(report,indent=2))
bpy.context.window.scene=bpy.data.scenes['Review'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CSC_Storage_L.blend'))
print('FOUNDATION_SCALE_STAGED',json.dumps(report))
