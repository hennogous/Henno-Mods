"""Exaggerate silhouette-defining forms on the accepted v2 architecture; no tiny mesh detail."""
import bpy,sys,math,json,shutil,hashlib,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
ROOT=Path(__file__).resolve().parents[4];V2=Path.home()/'Desktop/Codex/modern-windmill-v2-20261026'
OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(V2/'textures',OUT/'textures',dirs_exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(V2/(ASSET+'.blend')))
scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)));inv=frame.inverted()
meshes=[o for o in scene.objects if o.type=='MESH']
def local_edit(ob,fn):
    for v in ob.data.vertices:v.co=frame@Vector(fn(inv@v.co))
def scale_about(ob,center,scale):local_edit(ob,lambda v:Vector(center)+(v-Vector(center))*Vector(scale))
for ob in meshes:
    n=ob.name.removeprefix('CSC_Fixed_')
    if n=='Main_Roof':
        # Thicker eave slab and broader overhang; one center cut gives a subtle sweep.
        local_edit(ob,lambda v:(v.x*49/47,v.y*30/28,v.z-2 if v.z in (56,79) else v.z))
        bm=bmesh.new();bm.from_mesh(ob.data)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=frame@Vector((0,0,0)),plane_no=frame.to_3x3()@Vector((1,0,0)),clear_inner=False,clear_outer=False)
        bm.to_mesh(ob.data);bm.free()
        local_edit(ob,lambda v:(v.x,v.y,v.z+(abs(v.x)/49)**2*1.8))
    elif n=='Main_Ridge':
        scale_about(ob,(0,0,82),(1.04,1.8,1.9))
        bm=bmesh.new();bm.from_mesh(ob.data)
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=frame@Vector((0,0,0)),plane_no=frame.to_3x3()@Vector((1,0,0)),clear_inner=False,clear_outer=False)
        bm.to_mesh(ob.data);bm.free()
        local_edit(ob,lambda v:(v.x,v.y,v.z+(abs(v.x)/50)**2*1.8+.4))
    elif n=='Shelter_Roof':
        local_edit(ob,lambda v:(22+(v.x-22)*1.07,-46.5+(v.y+46.5)*1.045,v.z-1.6 if v.z in (37,52) else v.z))
    elif n=='Shelter_Ridge':scale_about(ob,(22,-46.5,55),(1.8,1.05,1.9))
    elif n=='Shelter_Header':scale_about(ob,(22,-67,38),(1.06,1.4,1.6))
    elif n.startswith('Shelter_Support_'):
        pts=[inv@v.co for v in ob.data.vertices];c=sum(pts,Vector())/len(pts);scale_about(ob,c,(1.65,1.65,1.03))
    elif n.startswith('Support_Foot_'):
        pts=[inv@v.co for v in ob.data.vertices];c=sum(pts,Vector())/len(pts);scale_about(ob,c,(1.4,1.4,1))
    elif n.startswith('Shelter_Brace_'):
        # Structural brace thickness is silhouette, unlike painted bolts and seams.
        pts=[inv@v.co for v in ob.data.vertices];cx=sum(v.x for v in pts)/len(pts);local_edit(ob,lambda v:(cx+(v.x-cx)*1.5,v.y,v.z))
    elif n=='Floor_Band':scale_about(ob,(0,0,34),(1.025,1.04,1.5))
    elif 'Window' in n:
        pts=[inv@v.co for v in ob.data.vertices];c=sum(pts,Vector())/len(pts)
        scale_about(ob,c,(1.5,1,1.3) if n.startswith(('Front','Rear')) else (1,1.5,1.3))
    elif n in ('Concrete_Arch','Arch_Spandrel','Arch_Jamb_-12','Arch_Jamb_12','Arch_Header','Arch_Wall_-18','Arch_Wall_18','Recess_Loading_Door','Door_Recess_Floor','Recess_Back'):
        # Broader, slightly squatter entry: enlarge the void as well as its surround.
        if n.startswith('Arch_Wall'):
            local_edit(ob,lambda v:(v.x,math.copysign(24-(24-abs(v.y))*.82,v.y),v.z))
        elif n=='Arch_Header':pass
        else:local_edit(ob,lambda v:(v.x,v.y*1.16,v.z))
    # Coarser, calmer brickwork is a UV sampling change, not modeled bricks.
    if n in ('Upper_Brick','Gable_Brick'):
        for d in ob.data.uv_layers['UV1'].data:
            d.uv.x=.00625+(d.uv.x-.00625)*.76
            d.uv.y=.99375+(d.uv.y-.99375)*.76

# Refresh AO packing after the few new roof/sweep vertices; preserve UV1/UV3.
bpy.ops.object.select_all(action='DESELECT')
for ob in meshes:ob.select_set(True);ob.data.uv_layers.active_index=1
bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.012,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
mat=bpy.data.materials[ASSET];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
for ch in ('B','N','G','M','E'):
    im=bpy.data.images.load(str(OUT/'textures'/f'{ASSET}_{ch}.png'),check_existing=False);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';nodes[ch].image=im
for l in list(bs.inputs['Normal'].links):links.remove(l)
links.new(nodes['B'].outputs['Color'],bs.inputs['Base Color'])
ao=bpy.data.images.new(ASSET+'_AO_v3',width=1024,height=1024,alpha=False);ao.colorspace_settings.name='Non-Color';nodes['AO'].image=ao;nodes.active=nodes['AO'];scene.cycles.samples=24;scene.render.bake.margin=6;bpy.ops.object.bake(type='AO')
ao.filepath_raw=str(OUT/'textures'/f'{ASSET}_AO.png');ao.file_format='PNG';ao.save()
mix=next(n for n in nodes if n.type=='MIX_RGB');normal=next(n for n in nodes if n.type=='NORMAL_MAP');links.new(mix.outputs[0],bs.inputs['Base Color']);links.new(normal.outputs[0],bs.inputs['Normal'])
for ob in meshes:ob.data.uv_layers.active_index=0;ob.select_set(False)
for im in list(bpy.data.images):
    if im.users==0:bpy.data.images.remove(im)
for ch in ('B','N','G','M','E','AO'):nodes[ch].image.filepath='//textures/'+f'{ASSET}_{ch}.png'
review=bpy.data.scenes['Review'];bpy.context.window.scene=review;review['revision_scope']='v3: exaggerated Civ proportions on v2 silhouette; silo remains deferred.'
cam=review.camera;target=Vector((35,-176,39))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
for name,offset in [('house',Vector((190,-310,240))),('doorway',Vector((-300,-180,210))),('rear',Vector((-180,320,240))),('top',Vector((1,-1,500)))]:
    cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(OUT/f'modern_v3_{name}.png');bpy.ops.render.render(write_still=True)
cam.location=target+Vector((190,-310,240));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
sys.path.insert(0,str(ROOT/'project/tools/blender/scene_export'));import decode_blend as decoder
bpy.context.window.scene=scene;decoded=[decoder.decode_mesh(o,o.matrix_world) for o in meshes];joined=decoder.merge_meshes(ASSET+'_House',decoded)
report={'revision':'v3 Civ proportion pass','source_v2_sha256':hashlib.sha256((V2/(ASSET+'.blend')).read_bytes()).hexdigest(),'export_vertices':len(joined['vertices']),'triangles':len(joined['triangles']),'changes':['larger painted windows','thicker ridge caps and eaves','subtle 1.8-unit roofline sweep','chunkier shelter supports, header and footings','wider arched entrance','coarser painted brick courses'],'small_detail_geometry_added':False,'runtime_installed':False}
(OUT/'house-review-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
