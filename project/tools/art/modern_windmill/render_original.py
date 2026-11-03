import bpy,sys,json
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]);src=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/CSC_BAKERS_Wind_Mill.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));s=bpy.data.scenes['Review'];bpy.context.window.scene=s
s.render.engine='CYCLES';s.cycles.samples=24;s.render.resolution_x=s.render.resolution_y=1024;s.render.resolution_percentage=100;s.render.film_transparent=False;s.render.image_settings.file_format='PNG'
# Shared reference camera for unchanged mesh comparisons, facing the original frontage.
target=Vector((35,-176,39));s.camera.data.type='ORTHO';s.camera.data.ortho_scale=195
s.camera.location=target+Vector((190,-310,240));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=1000,location=(20,-175,-.05));floor=bpy.context.object;floor.name='REVIEW_Ground';m=bpy.data.materials.new('Review_Ground');m.diffuse_color=(.4,.36,.25,1);floor.data.materials.append(m)
for kind in ['assembly','house']:
    for o in s.objects:
        if o.type=='MESH' and 'Tower_' in o.name:o.hide_render=kind=='house'
    s.render.filepath=str(out/('original_'+kind+'.png'));bpy.ops.render.render(write_still=True)
o=bpy.data.objects['CSC_Level_1_S_Bldg'];me=o.data
face_data=[]
for p in me.polygons:
    face_data.append({'index':p.index,'verts':list(p.vertices),'center':list(o.matrix_world@p.center),'normal':list(p.normal),'uv':[list(me.uv_layers[0].data[i].uv) for i in p.loop_indices]})
(out/'original-faces.json').write_text(json.dumps({'vertices':[list(o.matrix_world@v.co) for v in me.vertices],'faces':face_data},indent=2))
