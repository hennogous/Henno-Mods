"""Read-only review renders for the two independent prop masters."""
import sys,math,json
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from modular_v9 import ROOT,TROLLEY,PALLET
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
out=Path(sys.argv[sys.argv.index('--')+1]);(out/'images').mkdir(exist_ok=True)
preset=json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L1']['icon']
with suspend_csc_repairs():
    for ident in (TROLLEY,PALLET):
        bpy.ops.wm.open_mainfile(filepath=str(out/'masters'/ident/(ident+'.blend')),load_ui=False,use_scripts=False)
        s=bpy.data.scenes['Review'];bpy.context.window.scene=s
        meshes=[o for o in s.objects if o.type=='MESH' and o.get('source_asset_id')==ident]
        for o in list(s.objects):
            if o.type=='MESH' and o not in meshes:bpy.data.objects.remove(o,do_unlink=True)
        pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
        lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);center=(lo+hi)/2
        cam=s.camera;cam.matrix_world=Matrix(preset['matrix_world']);cam.data.type='ORTHO';cam.data.ortho_scale=max(hi-lo)*1.65
        cam.location=center+(cam.matrix_world.to_quaternion()@Vector((0,0,1)))*200
        for o in s.objects:
            if o.type=='LIGHT':o.data.energy=3;o.data.color=(1,1,1)
        bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(1,1,.9,1);bg.inputs['Strength'].default_value=.8
        bpy.ops.mesh.primitive_plane_add(size=500,location=(0,0,-.05));floor=bpy.context.object;floor.is_shadow_catcher=True
        floor.name='REVIEW_Ground';floor['review_only']=True;floor['csc_export_exclude']=True
        s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=s.render.resolution_y=640;s.render.resolution_percentage=100
        s.render.film_transparent=True;s.view_settings.view_transform='Standard';s.view_settings.exposure=0
        s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.filepath=str(out/'images'/(ident+'.png'))
        bpy.ops.render.render(write_still=True)
        # Deliver an immediately usable standalone view, with only review changes.
        # Icon lighting is only a render preset; saved authoring scenes retain
        # the project's validator-required review lighting.
        bg.inputs['Color'].default_value=(.7,.8,1,1);bg.inputs['Strength'].default_value=.65
        s.view_settings.exposure=-.1;s.view_settings.gamma=1
        key=bpy.data.objects['Review_Key'];key.data.energy=3.2;key.data.color=(1,.92,.8);key.data.angle=math.radians(6);key.data.use_shadow=True
        source=out/'masters'/ident/(ident+'.blend')
        bpy.ops.wm.save_as_mainfile(filepath=str(source))
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
        report=validate_current_scene();(source.parent/'validation.json').write_text(json.dumps(report,indent=2))
        assert report['error_count']==0,report['findings']
print('PROP_REVIEWS_COMPLETE')
