"""Match the approved concept's near-isometric axes for a review-only render."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
bpy.ops.wm.open_mainfile(filepath=str(OUT/(ASSET+'.blend')))
sc=bpy.data.scenes['Review'];bpy.context.window.scene=sc;cam=sc.camera
# Concept's two horizontal facade axes have image slopes approximately +/-0.58.
# That corresponds to a classic isometric 35.264-degree elevation and local -135 azimuth.
elevation=math.atan(1/math.sqrt(2));azimuth=math.radians(42.3-135)
direction=Vector((math.cos(azimuth)*math.cos(elevation),math.sin(azimuth)*math.cos(elevation),math.sin(elevation)))
rotation=(-direction).to_track_quat('-Z','Y');basis=rotation.to_matrix();right=basis@Vector((1,0,0));up=basis@Vector((0,1,0))
points=[]
for ob in bpy.data.scenes['Export'].objects:
    if ob.type!='MESH':continue
    for v in ob.data.vertices:
        p=ob.matrix_world@v.co;p.z=max(0,p.z);points.append(p)
xs=[p.dot(right) for p in points];ys=[p.dot(up) for p in points]
mid=right*((min(xs)+max(xs))/2)+up*((min(ys)+max(ys))/2)
# Align model's visible height and centre with the concept's building (excluding scenery).
pixels_per_unit=719/(max(ys)-min(ys));target=mid-right*(12/pixels_per_unit)-up*(53.5/pixels_per_unit)
cam.location=target+direction*600;cam.rotation_euler=rotation.to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1536/pixels_per_unit;cam.data.shift_x=cam.data.shift_y=0;cam.data.clip_end=20000
sc.render.resolution_x=1536;sc.render.resolution_y=1024;sc.render.resolution_percentage=100;sc.cycles.samples=48
sc.render.filepath=str(OUT/'modern_v5_concept_angle.png');bpy.ops.render.render(write_still=True)
(OUT/'concept-camera-match.json').write_text(json.dumps({'purpose':'review only; source model unmodified','method':'orthographic fit to concept facade axes, approximate because concept is generated artwork','elevation_degrees':math.degrees(elevation),'world_azimuth_degrees':math.degrees(azimuth),'height_pixels':719,'render':sc.render.filepath},indent=2))
