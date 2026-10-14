"""Prepare current three-UV storage shell with the existing animated crane as a child asset.

Run in Blender with -- --output <review folder>. Leaves source and crane files unchanged.
"""
import argparse, copy, hashlib, json, sys
from pathlib import Path
import xml.etree.ElementTree as ET
import bpy, bmesh
from mathutils import Matrix
import io_export_cn6 as cn6

parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
out=Path(parser.parse_args(sys.argv[sys.argv.index('--')+1:]).output).resolve()
out.mkdir(parents=True,exist_ok=True)
repo=Path(__file__).resolve().parents[3];mod=repo/'Civ Supply Chains'
source=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L\CSC_Storage_L.blend')
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(source))
bpy.context.window.scene=bpy.data.scenes['Export'];scene=bpy.context.scene
mesh=bpy.data.objects['CSC_Storage_L_Mesh'];rig=mesh.parent
rig.data.pose_position='REST'
names=json.loads(mesh['source_components'])
remove_ids={i for i,n in enumerate(names) if n.startswith('CSC_Fixed_Crane_')}
assert len(remove_ids)==8
attribute=mesh.data.attributes['csc_source_component']
def corner_snapshot(data,exclude):
 rows=[]
 for p in data.polygons:
  if attribute.data[p.vertices[0]].value in exclude:continue
  rows.append(tuple((tuple(data.vertices[data.loops[i].vertex_index].co),
                     tuple(tuple(uv.data[i].uv) for uv in data.uv_layers)) for i in p.loop_indices))
 return sorted(rows)
expected=corner_snapshot(mesh.data,remove_ids)
bm=bmesh.new();bm.from_mesh(mesh.data);layer=bm.verts.layers.int['csc_source_component']
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v[layer] in remove_ids],context='VERTS')
bm.to_mesh(mesh.data);bm.free();mesh.data.update()
attribute=mesh.data.attributes['csc_source_component']
assert corner_snapshot(mesh.data,set())==expected
assert len(mesh.data.vertices)==1632
mesh.name='CSC_TEST_Storage_Shell_Mesh';mesh.data.name=mesh.name
mesh.vertex_groups.clear();mesh.vertex_groups.new(name='Bone').add(list(range(len(mesh.data.vertices))),1,'REPLACE')
rig.animation_data_clear();rig.name='CSC_TEST_Storage_Shell';rig.data.name='CSC_TEST_Storage_Shell_Rig'
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for b in list(rig.data.edit_bones):rig.data.edit_bones.remove(b)
b=rig.data.edit_bones.new('Bone');b.head=(0,0,0);b.tail=(0,1,0)
bpy.ops.object.mode_set(mode='OBJECT');rig.data.pose_position='REST'
for im in bpy.data.images:
 if im.source=='FILE':im.filepath=bpy.path.abspath(im.filepath)
for sc in bpy.data.scenes:sc.frame_set(1)
mesh.select_set(True)
cn6.csc_export_fgx_geo('CSC_TEST_Storage_Shell',str(out),'LandmarkModel',3,True,rig)
geo_path=out/'CSC_TEST_Storage_Shell.geo'
geo_path.write_text(geo_path.read_text().replace('AssetObjects:','AssetObjects..'))
geo=ET.parse(geo_path).getroot()
for value in geo.findall('.//m_nBoundBoneCount'):value.text='0'
ET.indent(geo,space='  ');ET.ElementTree(geo).write(geo_path,encoding='utf-8',xml_declaration=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'CSC_Storage_L_Shell.blend'))

# Keep the working crane's behavior/material encapsulated in its child AST.
# The parent has only a static model and a fixed root attachment.
asset=ET.parse(mod/'Assets/CSC_TEST_Storage_L_Animated.ast').getroot()
for path in ('m_animationBindings/m_Bindings','m_timelineBindings/m_Bindings','m_timelines/m_Timelines'):
 asset.find('m_BehaviorData/m_behaviorDataSets/'+path).clear()
points=asset.find('.//m_Points');point=copy.deepcopy(points.find('Element'));points.clear()
def text(root,path,value):root.find(path).set('text',value)
def param(root,name):return next(e for e in root.findall('m_CookParams/m_Values/Element') if e.find('m_ParamName').get('text')==name)
text(point,'m_Name','Storage_Crane');text(point,'m_BoneName','CSC_TEST_Storage_Shell')
text(point,'m_ModelInstanceName','CSC_TEST_Storage_Shell');point.find('m_scale').text='1.0'
for axis in 'xyz':point.find('m_position/'+axis).text='0';point.find('m_orientation/'+axis).text='0'
text(param(point,'Asset'),'m_EntryName','CSC_TEST_Storage_Crane')
param(point,'RandomizeAnims').find('m_bValue').text='false';points.append(point)
models=asset.find('m_GeometrySet/m_ModelInstances')
old_shell=next(m for m in models if m.find('m_GeoName').get('text')=='CSC_TEST_Storage_Shell')
states={e.find('m_StateName').get('text'):copy.deepcopy(e) for e in old_shell.findall('m_GroupStates/Element')}
models.clear();model=ET.SubElement(models,'Element')
ET.SubElement(model,'m_Name',text='CSC_TEST_Storage_Shell');ET.SubElement(model,'m_GeoName',text='CSC_TEST_Storage_Shell')
groups=ET.SubElement(model,'m_GroupStates')
for m in geo.findall('m_Meshes/Element'):
 for g in m.findall('m_Groups/Element'):
  for row in states.values():
   row=copy.deepcopy(row);text(row,'m_MeshName',m.find('m_Name').get('text'));text(row,'m_GroupName',g.find('m_Name').get('text'));groups.append(row)
text(asset,'m_Description','Latest UV-edited static storage shell, with the independently animated crane asset attached at the origin.')
assert not asset.findall('.//m_AnimationName')
assert len(models)==1 and len(points)==1
ET.indent(asset,space='  ');ET.ElementTree(asset).write(out/'CSC_TEST_Storage_L_Animated.ast',encoding='utf-8',xml_declaration=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
report={'source':str(source),'source_sha256':source_hash,'shell_vertices':len(mesh.data.vertices),
        'removed_components':[names[i] for i in sorted(remove_ids)],'uv_geometry_parity':True,
        'child_asset':'CSC_TEST_Storage_Crane','attachment_position':[0,0,0],'attachment_rotation':[0,0,0],
        'attachment_scale':1,'crane_files_modified':False,'source_modified':False,'ae_verified':False}
(out/'attached-crane-check.json').write_text(json.dumps(report,indent=2))
print('STORAGE_SHELL_ATTACHMENT_PREPARED')
