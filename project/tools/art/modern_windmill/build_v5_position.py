"""Place the silo on the measured historical tower axis; compare fixed L1 art views."""
import bpy,sys,math,json,shutil
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4];OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
PREV=Path.home()/'Desktop/Codex/modern-windmill-v4-20261026'
SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/CSC_BAKERS_Wind_Mill.blend'
OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(PREV/'textures',OUT/'textures',dirs_exist_ok=True)
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));tower=bpy.data.objects['CSC_BAKERS_Wind_Mill_Tower_Tower']
pts=[tower.matrix_world@v.co for v in tower.data.vertices if abs((tower.matrix_world@v.co).z+36.10283)<.02]
center=Vector(tuple((min(p[i] for p in pts)+max(p[i] for p in pts))/2 for i in (0,1))+(0,))
local_center=frame.inverted()@center
bpy.ops.wm.open_mainfile(filepath=str(PREV/(ASSET+'.blend')))
scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene
def shift(ob,delta):ob.data.transform(Matrix.Translation(frame.to_3x3()@Vector(delta)))
for ob in list(scene.objects):
    name=ob.name.removeprefix('CSC_Fixed_')
    if name.startswith('Silo_'):shift(ob,(local_center.x-51,local_center.y+93,0))
    elif name.startswith('Elevator'):shift(ob,(55-72,-62+63,0))
    elif name=='Transfer_Spout':
        # Rebuild the connector to the relocated silo and adjacent elevator.
        a=frame@Vector((55,-67,106));b=center+Vector((0,0,98))
        m=(b-a).to_track_quat('Z','Y').to_matrix().to_4x4();m.translation=(a+b)/2
        signs=[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
        for v,(x,y,z) in zip(ob.data.vertices,signs):v.co=m@Vector((x*3,y*3,z*(b-a).length/2))
    elif name in ('Shelter_Support_3_-65','Support_Foot_3_-65','Shelter_Brace_3'):
        # This post is fully enclosed by the tower at the original building junction.
        bpy.data.objects.remove(ob,do_unlink=True)
    elif name=='Sack_Upright_0':shift(ob,(-7,-6,0))
    elif name=='Sack_Upright_1':shift(ob,(-11,-1,0))
    elif name=='Stock_Pallet' or name.startswith('Sack_Stack_'):shift(ob,(10,18,0))
meshes=[o for o in scene.objects if o.type=='MESH'];mat=bpy.data.materials[ASSET];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
for ch in ('B','N','G','M','E'):
    im=bpy.data.images.load(str(OUT/'textures'/f'{ASSET}_{ch}.png'),check_existing=False);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';nodes[ch].image=im
bpy.ops.object.select_all(action='DESELECT')
for ob in meshes:ob.select_set(True);ob.data.uv_layers.active_index=1
bpy.context.view_layer.objects.active=meshes[0]
for l in list(bs.inputs['Normal'].links):links.remove(l)
links.new(nodes['B'].outputs['Color'],bs.inputs['Base Color'])
ao=bpy.data.images.new(ASSET+'_AO_v5',width=2048,height=2048,alpha=False);ao.colorspace_settings.name='Non-Color';nodes['AO'].image=ao;nodes.active=nodes['AO'];scene.cycles.samples=24;scene.render.bake.margin=8;bpy.ops.object.bake(type='AO',uv_layer='UV2')
ao.filepath_raw=str(OUT/'textures'/f'{ASSET}_AO.png');ao.file_format='PNG';ao.save()
mix=next(n for n in nodes if n.type=='MIX_RGB');normal=next(n for n in nodes if n.type=='NORMAL_MAP');links.new(mix.outputs[0],bs.inputs['Base Color']);links.new(normal.outputs[0],bs.inputs['Normal'])
for ob in meshes:ob.data.uv_layers.active_index=0;ob.select_set(False)
for im in list(bpy.data.images):
    if im.users==0:bpy.data.images.remove(im)
for ch in ('B','N','G','M','E','AO'):nodes[ch].image.filepath='//textures/'+f'{ASSET}_{ch}.png'
presets=json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L1']
light=bpy.data.objects['Review_Key'];light_settings=(tuple(light.rotation_euler),light.data.energy,tuple(light.data.color),light.data.angle)
world_settings=(tuple(review.world.node_tree.nodes['Background'].inputs['Color'].default_value),review.world.node_tree.nodes['Background'].inputs['Strength'].default_value)
def configure(sc):
    bpy.context.window.scene=sc;sc.render.engine='CYCLES';sc.cycles.samples=32
    sc.render.resolution_x=sc.render.resolution_y=1024;sc.render.resolution_percentage=100;sc.render.film_transparent=False
    sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard';sc.view_settings.exposure=-.1;sc.view_settings.gamma=1
    p=presets['icon'];cam=sc.camera;cam.data.type=p['projection'];cam.data.lens=p['lens'];cam.data.sensor_width=p['sensor_width'];cam.data.shift_x=p['shift_x'];cam.data.shift_y=p['shift_y'];cam.matrix_world=Matrix(p['matrix_world'])
    for o in list(sc.objects):
        if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
    data=bpy.data.lights.new('Review_Key','SUN');o=bpy.data.objects.new('Review_Key',data);sc.collection.objects.link(o)
    o.rotation_euler=light_settings[0];data.energy=light_settings[1];data.color=light_settings[2];data.angle=light_settings[3]
    sc.world.use_nodes=True;bg=sc.world.node_tree.nodes['Background'];bg.inputs['Color'].default_value=world_settings[0];bg.inputs['Strength'].default_value=world_settings[1]
    if not any(o.name.startswith('REVIEW_Ground') for o in sc.objects):
        bpy.ops.mesh.primitive_plane_add(size=1000,location=(20,-175,-.05));g=bpy.context.object;g.name='REVIEW_Ground';g['review_only']=True
        m=bpy.data.materials.new('Comparison_Ground');m.diffuse_color=(.4,.36,.25,1);g.data.materials.append(m)
configure(review);review['revision_scope']='Silo matches historical tower axis; fixed L1 icon camera comparison.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
for ch in ('B','N','G','M','E','AO'):nodes[ch].image.reload()
review.render.filepath=str(OUT/'modern_v5_icon_angle.png');bpy.ops.render.render(write_still=True)
camera_matrix=review.camera.matrix_world.copy();camera_type=review.camera.data.type
review.camera.data.type='ORTHO';review.camera.data.ortho_scale=225;target=frame@Vector((15,-29,44));review.camera.location=target+Vector((1,-1,500));review.camera.rotation_euler=(target-review.camera.location).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(OUT/'modern_v5_top.png');bpy.ops.render.render(write_still=True)
review.camera.data.type=camera_type;review.camera.matrix_world=camera_matrix
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
sys.path.insert(0,str(ROOT/'project/tools/blender/scene_export'));import decode_blend as decoder
bpy.context.window.scene=scene;joined=decoder.merge_meshes(ASSET,[decoder.decode_mesh(o,o.matrix_world) for o in meshes])
silo=bpy.data.objects['CSC_Fixed_Silo_Body'];actual=sum((v.co for v in silo.data.vertices),Vector())/len(silo.data.vertices)
assert (Vector((actual.x,actual.y,0))-center).length<.001
report={'revision':'v5 exact historical tower position','historical_center_world':list(center),'silo_center_world':[actual.x,actual.y,0],'center_error':(Vector((actual.x,actual.y,0))-center).length,'silo_center_local':list(local_center),'export_vertices':len(joined['vertices']),'triangles':len(joined['triangles']),'camera':'frozen L1 icon preset, identical camera/lighting for both source-model comparison renders','runtime_installed':False}
(OUT/'assembly-review-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));historical=bpy.data.scenes['Review'];configure(historical)
historical.render.filepath=str(OUT/'historical_icon_angle.png');bpy.ops.render.render(write_still=True)
