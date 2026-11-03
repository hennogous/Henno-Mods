"""Reuse the existing bolted cream/green casing patch on the turbine side faces."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from water_modern import ROOT,WATER,BMAT,dump
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
out=Path(sys.argv[sys.argv.index('--')+1]);folder=out/'masters'/WATER
with suspend_csc_repairs():
    bpy.ops.wm.open_mainfile(filepath=str(folder/(WATER+'.blend')),load_ui=False,use_scripts=False)
    sc=bpy.data.scenes['Export'];bpy.context.window.scene=sc;o=bpy.data.objects['CSC_Fixed_Turbine_Bearing_Housing']
    for p in o.data.polygons:
        if abs(p.normal.z)>.5:continue
        axes=[1,2] if abs(p.normal.x)>.5 else [0,2]
        pts=[o.data.vertices[i].co for i in p.vertices];lo=[min(v[a] for v in pts) for a in axes];hi=[max(v[a] for v in pts) for a in axes]
        for li in p.loop_indices:
            q=o.data.vertices[o.data.loops[li].vertex_index].co;u,v=[(q[a]-lo[j])/(hi[j]-lo[j]) for j,a in enumerate(axes)]
            o.data.uv_layers[0].data[li].uv=((7+.025+.95*u)/8,1-(.025+.95*(1-v))/8)
    review=bpy.data.scenes['Review'];cam=review.camera;target=Vector((-22,0,13));cam.data.type='ORTHO';cam.data.ortho_scale=200;cam.data.shift_x=cam.data.shift_y=0
    cam.location=target+Vector((175,-255,170));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.window.scene=review;bpy.ops.wm.save_as_mainfile(filepath=str(folder/(WATER+'.blend')))
    bpy.ops.wm.open_mainfile(filepath=str(folder/(WATER+'.blend')),load_ui=False,use_scripts=False)
    report=validate_current_scene();dump(folder/'validation.json',report);assert report['automated_pass']
    bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();groups={}
    for o in bpy.context.scene.objects:
        if o.type=='MESH':groups.setdefault('Building' if o.data.materials[0].name==BMAT else 'Machinery',[]).append(dec.decode_mesh(o,o.matrix_world))
    dump(out/'models'/(WATER+'.json'),{'asset_id':WATER,'kind':'building','meshes':[dec.merge_meshes(WATER+'_'+k,v) for k,v in groups.items()]})
print('HOUSING_SURFACES_FINISHED')
