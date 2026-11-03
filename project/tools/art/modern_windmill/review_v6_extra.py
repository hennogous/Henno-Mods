import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
bpy.ops.wm.open_mainfile(filepath=str(OUT/(ASSET+'.blend')))
sc=bpy.data.scenes['Review'];bpy.context.window.scene=sc;cam=sc.camera
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)));inv=frame.inverted()
target=frame@Vector((12,-35,43));sc.render.resolution_x=sc.render.resolution_y=1024;sc.cycles.samples=24
cam.data.type='ORTHO';cam.data.ortho_scale=235;cam.data.shift_x=cam.data.shift_y=0;cam.data.clip_end=20000
for name,offset in [('rear',Vector((-180,320,240))),('top',Vector((1,-1,500)))]:
    cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(OUT/f'modern_v6_{name}.png');bpy.ops.render.render(write_still=True)
checks={}
for ob in bpy.data.scenes['Export'].objects:
    if ob.type!='MESH':continue
    if 'Foundation' in ob.name or 'Support_Foot' in ob.name:checks[ob.name]=min(v.co.z for v in ob.data.vertices)
assert all(z<=-29.99 for z in checks.values()),checks
ob=bpy.data.objects['CSC_Fixed_Silo_Body'];c=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
expected=Vector((70.21623229980469,-204.37718200683594,0));err=(Vector((c.x,c.y,0))-expected).length
assert err<.001
roof=bpy.data.objects['CSC_Fixed_Main_Roof'];local=[inv@v.co for v in roof.data.vertices];ridge=[v.z for v in local if abs(v.y)<.001]
report={'foundation_depths':checks,'historical_tower_axis_error':err,'main_roof_ridge_levels':sorted(set(round(z,3) for z in ridge)),'roof_sweep':False}
(OUT/'placement-foundation-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
