"""Read-only source comparison, identical L1 art camera, lighting and world scale."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[4];OUT=Path(sys.argv[sys.argv.index('--')+1]);OUT.mkdir(parents=True,exist_ok=True)
BASE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill'
sources={'historical':BASE/'CSC_BAKERS_Wind_Mill.blend','modern':BASE/'modern/revision-08-concept-roof/CSC_BAKERS_Wind_Mill_Modern.blend'}
before={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in sources.items()}
preset=json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L1']['icon']
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
with suspend_csc_repairs():
    bpy.ops.wm.open_mainfile(filepath=str(sources['modern']),load_ui=False,use_scripts=False)
    sc=bpy.data.scenes['Review'];key=bpy.data.objects['Review_Key'];lighting=(tuple(key.rotation_euler),key.data.energy,tuple(key.data.color),key.data.angle)
    bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');world=(tuple(bg.inputs['Color'].default_value),bg.inputs['Strength'].default_value)
    for label,path in sources.items():
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);sc=bpy.data.scenes['Review'];bpy.context.window.scene=sc
        sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=sc.render.resolution_y=1200;sc.render.resolution_percentage=100
        sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.view_settings.view_transform='Standard';sc.view_settings.exposure=-.1;sc.view_settings.gamma=1
        cam=sc.camera;cam.data.type=preset['projection'];cam.data.lens=preset['lens']*.8;cam.data.sensor_width=preset['sensor_width'];cam.data.shift_x=preset['shift_x'];cam.data.shift_y=preset['shift_y']*.8;cam.matrix_world=Matrix(preset['matrix_world'])
        cam.data.clip_end=20000
        for o in list(sc.objects):
            if o.type=='LIGHT' or o.name.startswith('REVIEW_Ground'):bpy.data.objects.remove(o,do_unlink=True)
        light=bpy.data.lights.new('Comparison_Key','SUN');o=bpy.data.objects.new('Comparison_Key',light);sc.collection.objects.link(o);o.rotation_euler=lighting[0];light.energy=lighting[1];light.color=lighting[2];light.angle=lighting[3]
        sc.world.use_nodes=True;bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=world[0];bg.inputs['Strength'].default_value=world[1]
        bpy.ops.mesh.primitive_plane_add(size=5000,location=(20,-175,-.05));floor=bpy.context.object;floor.name='Comparison_Ground';floor.is_shadow_catcher=True
        mat=bpy.data.materials.new('Comparison_Ground');mat.use_nodes=True;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.72,.74,.76,1);bs.inputs['Roughness'].default_value=1;floor.data.materials.append(mat)
        sc.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
    for k,p in sources.items():assert hashlib.sha256(p.read_bytes()).hexdigest()==before[k]
    (OUT/'comparison.json').write_text(json.dumps({'sources':{k:str(p) for k,p in sources.items()},'unchanged_source_hashes':before,'camera':'L1 icon camera; identical 0.8 lens/shift overscan to retain historical sail tips','same_camera_scale_lighting':True,'source_comparison_only':True},indent=2))
print('COMPARISON_COMPLETE',flush=True)
