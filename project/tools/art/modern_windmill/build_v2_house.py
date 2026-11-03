"""Silhouette-led modern house revision. Original frame/proportions, reworked construction.

Review milestone only: silo composition is intentionally a subsequent pass.
Small surface detail is painted; geometry contains only structural forms/openings.
"""
import bpy,sys,json,math,ast,shutil,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
ROOT=Path(__file__).resolve().parents[4];V1=Path.home()/'Desktop/Codex/modern-windmill-v1-20261026'
SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/CSC_BAKERS_Wind_Mill.blend'
OUT.mkdir(parents=True,exist_ok=True);(OUT/'textures').mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(V1/(ASSET+'.blend')))
scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene
for ob in list(bpy.data.objects):
    if ob.type=='MESH':bpy.data.objects.remove(ob,do_unlink=True)
rig=bpy.data.objects[ASSET];mat=bpy.data.materials[ASSET];meshes=[];uv_guide=[]
tree=ast.parse((Path(__file__).parent/'build_model.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('tileuv','mesh','box','beam')],type_ignores=[]),'<geometry helpers>','exec'))
# Measurements from historical mesh, projected into its own horizontal axes.
# Main ridge spans ~94.65; house body ~85 x 49; ridge height 82.76.
# Shelter projects to local Y=-70 and retains the second gable in the silhouette.
angle=math.radians(42.3);origin=Vector((-101,-126,0));rotation=Matrix.Rotation(angle,4,'Z')
frame=rotation@Matrix.Translation(origin)

# Regular lower masonry walls, with an actual broad arch in the left gable.
box('House_Foundation',(0,0,-12),(84,48,24),1)
for name,c,s in [('Front_Lower',(0,-22.5,16),(84,3,32)),('Rear_Lower',(0,22.5,16),(84,3,32)),('End_Lower',(40.5,0,16),(3,42,32))]:box(name,c,s,1)
for y in (-18,18):box('Arch_Wall_'+str(y),(-40.5,y,16),(3,12,32),1)
# Seven large voussoir segments shape the opening; individual stone joints are painted.
steps=8;inner=[];outer=[]
for i in range(steps+1):
    a=math.pi-i*math.pi/steps
    inner.append((10*math.cos(a),19+10*math.sin(a)))
    outer.append((14*math.cos(a),19+14*math.sin(a)))
verts=[]
for x in (-44,-38):
    verts += [(x,y,z) for y,z in inner]+[(x,y,z) for y,z in outer]
faces=[]
for i in range(steps):
    a=i;b=i+1;c=steps+1+i;d=c+1;off=2*(steps+1)
    faces += [(a,b,d,c),(a+off,c+off,d+off,b+off),(a,a+off,b+off,b),(c,d,d+off,c+off)]
mesh('Concrete_Arch',verts,faces,[11]*len(faces))
spandrel_v=[];spandrel_f=[]
for x in (-42,-39):
    for i in range(steps):
        y0,z0=outer[i];y1,z1=outer[i+1];k=len(spandrel_v)
        spandrel_v += [(x,y0,z0),(x,y1,z1),(x,y1,34),(x,y0,34)]
        spandrel_f.append((k,k+1,k+2,k+3) if x==-42 else (k+3,k+2,k+1,k))
mesh('Arch_Spandrel',spandrel_v,spandrel_f,[11]*len(spandrel_f))
for y in (-12,12):box('Arch_Jamb_'+str(y),(-41,y,9.5),(6,4,19),11)
box('Arch_Header',(-40.5,0,34),(3,48,3),11)
box('Door_Recess_Floor',(-31,0,.4),(21,24,.8),13)
box('Recess_Back',(-27,0,16),(1,23,32),13)
box('Recess_Loading_Door',(-27.6,0,13),(1,17,26),8)
# Clear two-storey proportions, restrained modern floor band and brick upper storey.
box('Floor_Band',(0,0,34),(85,49,3),11)
box('Upper_Brick',(0,0,47.5),(84,48,24),0)
mesh('Gable_Brick',[(-42,-24,59.5),(-42,24,59.5),(-42,0,81),(42,-24,59.5),(42,24,59.5),(42,0,81)],[(0,2,1),(3,4,5)],[0,0])
# Roof is a broad slab, without modeled tiles, seams, rivets or fine edge bevels.
vs=[(-47,-28,59),(47,-28,59),(-47,0,82),(47,0,82),(-47,28,59),(47,28,59),(-47,-28,56),(47,-28,56),(-47,0,79),(47,0,79),(-47,28,56),(47,28,56)]
fs=[(0,1,3,2),(2,3,5,4),(0,6,7,1),(4,5,11,10),(0,2,8,6),(2,4,10,8),(1,7,9,3),(3,9,11,5)]
roof=mesh('Main_Roof',vs,fs,[2,2,4,4,4,4,4,4])
# Roof ribs in the painting run down each slope, not along the ridge.
for p in roof.data.polygons[:2]:
    for li in p.loop_indices:
        v=roof.data.vertices[roof.data.loops[li].vertex_index].co
        roof.data.uv_layers[0].data[li].uv=tileuv(2,(v.x+47)/94,abs(v.y)/28)
box('Main_Ridge',(0,0,82),(96,4,3),5)
# Flat glazing panels; painted atlas supplies all frames and mullions.
def window(name,vs):return mesh(name,vs,[(0,1,2,3)],[7],[[(0,0),(1,0),(1,1),(0,1)]])
for x,z in [(-21,48),(-21,17),(22,48)]:window('Front_Window_'+str(x)+'_'+str(z),[(x-5,-24.08,z-7),(x+5,-24.08,z-7),(x+5,-24.08,z+7),(x-5,-24.08,z+7)])
for x in (-22,22):window('Rear_Window_'+str(x),[(x+5,24.08,41),(x-5,24.08,41),(x-5,24.08,55),(x+5,24.08,55)])
window('Gable_Window',[(-42.08,5,42),(-42.08,-5,42),(-42.08,-5,56),(-42.08,5,56)])
window('End_Window',[(42.08,-5,42),(42.08,5,42),(42.08,5,56),(42.08,-5,56)])
# Restore the full central projecting shelter, not the v1 small single-pitch canopy.
cx=22;xl=-2;xr=46;yb=-23;yf=-70
vs=[(xl,yb,40),(cx,yb,55),(xr,yb,40),(xl,yf,40),(cx,yf,55),(xr,yf,40),(xl,yb,37),(cx,yb,52),(xr,yb,37),(xl,yf,37),(cx,yf,52),(xr,yf,37)]
canopy=mesh('Shelter_Roof',vs,[(0,1,4,3),(1,2,5,4),(0,3,9,6),(2,8,11,5),(3,4,10,9),(4,5,11,10)],[2,2,4,4,4,4])
for p in canopy.data.polygons[:2]:
    for li in p.loop_indices:
        v=canopy.data.vertices[canopy.data.loops[li].vertex_index].co
        canopy.data.uv_layers[0].data[li].uv=tileuv(2,(v.y-yf)/(yb-yf),abs(v.x-cx)/24)
box('Shelter_Ridge',(cx,(yb+yf)/2,55),(4,50,3),5)
mesh('Shelter_Gable',[(1,yf+.7,39),(43,yf+.7,39),(22,yf+.7,52)],[(0,1,2)],[5])
box('Shelter_Header',(22,-67,38),(44,6,5),4)
for x in (3,41):
    for y in (-65,-27):
        box('Support_Foot_'+str(x)+'_'+str(y),(x,y,-10),(8,8,28),11)
        box('Shelter_Support_'+str(x)+'_'+str(y),(x,y,20),(5,5,34),4)
    beam('Shelter_Brace_'+str(x),(x,-65,27),(x,-54,38),3.5,4)

# All vertices are authored in the original ground frame; no visual rescaling.
bpy.ops.object.select_all(action='DESELECT');review=bpy.data.scenes['Review']
for ob in meshes:
    ob.data.transform(frame);ob.parent=rig;ob['reference_source']=str(SOURCE);review.collection.objects.link(ob)
    group=ob.vertex_groups.new(name='Bone');group.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    mod=ob.modifiers.new('Static Bone','ARMATURE');mod.object=rig
    ob.data.uv_layers.new(name='UV2');ob.data.uv_layers.active_index=1;ob.select_set(True)
bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.012,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
for ob in meshes:
    uv=ob.data.uv_layers.new(name='UV3')
    for d in uv.data:d.uv=(.02,.02)
    ob.data.uv_layers.active_index=1
# Reuse the approved concept's ImageGen material library, with new geometry AO.
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
for ch in ('B','N','G','M','E'):
    p=V1/'textures'/f'{ASSET}_{ch}.png';dest=OUT/'textures'/p.name
    shutil.copy2(OUT/'painted_materials_v2.png' if ch=='B' and (OUT/'painted_materials_v2.png').exists() else p,dest)
    nodes[ch].image=bpy.data.images.load(str(dest),check_existing=False);nodes[ch].image.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color'
for link in list(bs.inputs['Normal'].links):links.remove(link)
links.new(nodes['B'].outputs['Color'],bs.inputs['Base Color'])
ao=bpy.data.images.new(ASSET+'_AO_v2',width=1024,height=1024,alpha=False);ao.colorspace_settings.name='Non-Color';nodes['AO'].image=ao;nodes.active=nodes['AO'];scene.cycles.samples=24;scene.render.bake.margin=6
bpy.ops.object.bake(type='AO');ao.filepath_raw=str(OUT/'textures'/f'{ASSET}_AO.png');ao.file_format='PNG';ao.save()
mix=next(n for n in nodes if n.type=='MIX_RGB');links.new(mix.outputs[0],bs.inputs['Base Color']);normal=next(n for n in nodes if n.type=='NORMAL_MAP');links.new(normal.outputs[0],bs.inputs['Normal'])
for ob in meshes:ob.data.uv_layers.active_index=0;ob.select_set(False)
# Remove unused previous-source images; keep portable external source textures.
for im in list(bpy.data.images):
    if im.users==0:bpy.data.images.remove(im)
    elif im.filepath:im.filepath=bpy.path.relpath(bpy.path.abspath(im.filepath),start=str(OUT))
bpy.context.window.scene=review
bpy.ops.mesh.primitive_plane_add(size=1000,location=(20,-175,-.05));ground=bpy.context.object;ground.name='REVIEW_Ground';ground['review_only']=True
groundmat=bpy.data.materials.new('REVIEW_Ground_v2');groundmat.diffuse_color=(.4,.36,.25,1);ground.data.materials.append(groundmat)
target=Vector((35,-176,39));cam=review.camera;cam.data.type='ORTHO';cam.data.ortho_scale=195;cam.location=target+Vector((190,-310,240));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
review.render.resolution_x=review.render.resolution_y=1024;review.cycles.samples=32;review.render.film_transparent=False
review['revision_scope']='Main building silhouette and modernization review; silo placement/proportions intentionally deferred.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
for name,offset in [('house',Vector((190,-310,240))),('doorway',Vector((-300,-180,210))),('rear',Vector((-180,320,240))),('top',Vector((1,-1,500)))]:
    cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(OUT/f'modern_v2_{name}.png');bpy.ops.render.render(write_still=True)
cam.location=target+Vector((190,-310,240));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
sys.path.insert(0,str(ROOT/'project/tools/blender/scene_export'));import decode_blend as decoder
bpy.context.window.scene=scene;decoded=[decoder.decode_mesh(o,o.matrix_world) for o in meshes]
joined=decoder.merge_meshes(ASSET+'_House',decoded)
report={'original_source':str(SOURCE),'original_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'revision':'v2 main-house review','export_vertices':len(joined['vertices']),'triangles':len(joined['triangles']),'main_ridge_height':83.5,'reference_main_ridge_height':82.76144,'shelter_ridge_height':56.5,'modernized_geometry':['regular lower wall shell','broad concrete arch','sheet roof slabs','full gabled projecting shelter','painted structural supports'],'texture_only_details':['masonry joints','roof seams','window frames and mullions','rivets','surface wear'],'runtime_installed':False}
(OUT/'house-review-report.json').write_text(json.dumps(report,indent=2));(OUT/'model.json').write_text(json.dumps({'asset_id':ASSET,'kind':'building','meshes':[joined]}));print(json.dumps(report,indent=2))
