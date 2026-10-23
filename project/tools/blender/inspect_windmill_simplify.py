"""Snapshot edited masters and render untextured sail construction for diagnosis."""
import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);OUT.mkdir(parents=True,exist_ok=True)
SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/tower';NAME='CSC_BAKERS_Wind_Mill_Tower';rows=[]
for name in [NAME,NAME+'_CON+PIL']:
 p=SOURCE/(name+'.blend');bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 row=dict(path=str(p),sha=hashlib.sha256(p.read_bytes()).hexdigest(),scenes=[s.name for s in bpy.data.scenes],objects=[])
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type!='MESH':continue
  row['objects'].append(dict(name=ob.name,vertices=[list(v.co) for v in ob.data.vertices],faces=[list(f.vertices) for f in ob.data.polygons],uvs={u.name:[list(v.uv) for v in u.data] for u in ob.data.uv_layers},materials=[m.name for m in ob.data.materials],material_faces=[sum(f.material_index==i for f in ob.data.polygons) for i in range(len(ob.data.materials))],groups=[g.name for g in ob.vertex_groups],unweighted=sum(not v.groups for v in ob.data.vertices),modifiers=[(m.name,m.type) for m in ob.modifiers]))
 rows.append(row)
(OUT/'edited-sources.json').write_text(json.dumps(rows));print([(r['path'],[(o['name'],len(o['vertices']),len(o['faces']),o['materials'],o['unweighted']) for o in r['objects']]) for r in rows])
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(NAME+'.blend')),load_ui=False,use_scripts=False)
scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;scene.frame_set(1)
sails=bpy.data.objects[NAME+'_Sails']
for ob in scene.objects:ob.hide_render=ob!=sails
mat=bpy.data.materials.new('Inspection');mat.diffuse_color=(.65,.65,.65,1);sails.data.materials.clear();sails.data.materials.append(mat)
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
cam=bpy.data.objects.new('Inspect camera',bpy.data.cameras.new('Inspect camera'));scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=110
center=Vector((26.99117,-41.48987,63.74731));back=Vector((.5,math.sqrt(3)/2,0));right=Vector((math.sqrt(3)/2,-.5,0))
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for label,direction in [('front',-back+right*.2+Vector((0,0,.12))),('back',back+right*.3+Vector((0,0,.15)))]:
 cam.location=center+direction*150;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/('sails-'+label+'.png'));bpy.ops.render.render(write_still=True)
