"""Author the first modern mill master. New asset only; never edits AE assemblies."""
import bpy, math, json, sys, bmesh
from pathlib import Path
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(sys.argv[sys.argv.index('--')+1])
ASSET='CSC_BAKERS_Wind_Mill_Modern'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'textures').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.name='Export';scene['asset_id']=ASSET
mat=bpy.data.materials.new(ASSET);mat.use_nodes=True
mat.diffuse_color=(.65,.57,.38,1)
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.72
meshes=[];uv_guide=[]
COLORS=[(.70,.46,.22),(.41,.43,.44),(.21,.31,.12),(.78,.72,.55),(.25,.35,.16),(.73,.70,.57),(.16,.18,.17),(.23,.29,.28),(.20,.28,.18),(.79,.69,.48),(.42,.26,.12),(.49,.49,.43),(.76,.72,.60),(.12,.13,.11),(.74,.70,.57),(.65,.55,.38)]

def tileuv(tile,u,v):
    col=tile%4;row=tile//4
    return ((col+.025+.95*u)/4,1-(row+.025+.95*(1-v))/4)

def mesh(name,verts,faces,tiles,uvs=None,prop=False):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new('CSC_Fixed_'+name,me);scene.collection.objects.link(ob)
    ob['export_role']='fixed_geometry' if prop else 'building_geometry';ob['source_asset_id']=ASSET
    ob['surface_tiles']=json.dumps(tiles);ob.data.materials.append(mat)
    uv=me.uv_layers.new(name='UV1')
    for p,t in zip(me.polygons,tiles):
        coords=uvs[p.index] if uvs else None
        if coords is None:
            # Orthographic projection onto each face's dominant plane; upright walls.
            n=p.normal;axis=max(range(3),key=lambda i:abs(n[i]));axes=([1,2] if axis==0 else [0,2] if axis==1 else [0,1])
            raw=[(me.vertices[i].co[axes[0]],me.vertices[i].co[axes[1]]) for i in p.vertices]
            lo=[min(x[i] for x in raw) for i in (0,1)];hi=[max(x[i] for x in raw) for i in (0,1)]
            coords=[((x[0]-lo[0])/max(.01,hi[0]-lo[0]),(x[1]-lo[1])/max(.01,hi[1]-lo[1])) for x in raw]
            if axis==0 and n.x>0 or axis==1 and n.y>0: coords=[(1-u,v) for u,v in coords]
        for li,(u,v) in zip(p.loop_indices,coords): uv.data[li].uv=tileuv(t,u,v)
        uv_guide.append({'object':name,'tile':t,'polygon':[list(uv.data[li].uv) for li in p.loop_indices]})
    meshes.append(ob);return ob

def box(name,c,s,t,prop=False):
    x,y,z=c;a,b,h=[q/2 for q in s]
    vs=[(x+i*a,y+j*b,z+k*h) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],[t]*6,prop=prop)

def cylinder(name,x,y,rings,n,t,cap=5,prop=False,start=math.pi/2):
    vs=[(x+r*math.cos(start+2*math.pi*i/n),y+r*math.sin(start+2*math.pi*i/n),z) for z,r in rings for i in range(n)]
    fs=[];ts=[];uvs=[]
    zlo,zhi=rings[0][0],rings[-1][0]
    for j in range(len(rings)-1):
        for i in range(n):
            fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i));ts.append(t)
            u0,u1=i/n,(i+1)/n
            if name=='Silo_Body':
                # The emblem occupies a front quarter, not the entire circumference.
                u0,u1=((i-6)/4,(i-5)/4) if 6<=i<10 else (.02,.21)
            if name=='Silo_Foundation':u0,u1=(i%4)/4,(i%4+1)/4
            uvs.append([(u0,(rings[j][0]-zlo)/(zhi-zlo)),(u1,(rings[j][0]-zlo)/(zhi-zlo)),(u1,(rings[j+1][0]-zlo)/(zhi-zlo)),(u0,(rings[j+1][0]-zlo)/(zhi-zlo))])
    for j,rev in [(0,True),(len(rings)-1,False)]:
        ids=list(range(j*n,(j+1)*n));ids=ids[::-1] if rev else ids
        fs.append(ids);ts.append(cap);uvs.append([(.5+.48*math.cos(start+2*math.pi*(i%n)/n),.5+.48*math.sin(start+2*math.pi*(i%n)/n)) for i in ids])
    ob=mesh(name,vs,fs,ts,uvs,prop)
    for p in ob.data.polygons:p.use_smooth=p.index<(len(rings)-1)*n
    return ob

def beam(name,a,b,width,t,prop=False):
    a,b=Vector(a),Vector(b);ob=box(name,(0,0,0),(width,width,(b-a).length),t,prop)
    m=(b-a).to_track_quat('Z','Y').to_matrix().to_4x4();m.translation=(a+b)/2
    ob.data.transform(m);return ob

# The house and silo use one root; buried geometry reaches z=-24 throughout.
# Working frame rotated -25 degrees at the historic mill's anchor (30,-172).
box('House_Foundation',(-19,10,-8),(70,66,32),1)
box('House_Lower',(-19,10,24),(70,66,32),1)
box('House_Belt',(-19,10,41),(73,69,4),5)
box('House_Upper',(-19,10,64),(70,66,42),0)
# Coherent gabled volume: ridge along Y, with slight eave sweep.
x0,x1,xc=-56,18,-19;y0,y1=-26,46
mesh('Gables',[(x0+2,-23,84),(x1-2,-23,84),(xc,-23,106),(x0+2,43,84),(x1-2,43,84),(xc,43,106)],[(0,1,2),(5,4,3)],[0,0])
mesh('Roof',[(x0,y0,83),(xc,y0,108),(x1,y0,83),(x0,y1,83),(xc,y1,108),(x1,y1,83),(x0,y0,80),(x1,y0,80),(x0,y1,80),(x1,y1,80),(xc,y0,105),(xc,y1,105)],[(0,1,4,3),(1,2,5,4),(0,6,10,1),(1,10,7,2),(3,4,11,8),(4,5,9,11),(0,3,8,6),(2,7,9,5)],[2,2,4,4,4,4,4,4])
box('Ridge',(-19,10,108),(5,77,4),5)
for y in (y0,y1):
    beam('Barge_L_'+str(y),(x0-1,y,83),(xc,y,109),3,4)
    beam('Barge_R_'+str(y),(xc,y,109),(x1+1,y,83),3,4)
# Window frames are single shallow solid blocks; painted glazing and mullions.
for x,z in [(-37,64),(-6,64),(-5,22)]:box('Front_Window_'+str(x)+'_'+str(z),(x,-23.7,z),(13,2.2,20 if z>40 else 17),7)
for x in (-54.7,16.7):
    for y in (-4,27):box('Side_Window_'+str(x)+'_'+str(y),(x,y,65),(2.2,13,19),7)
for x in (-37,-6):box('Rear_Window_'+str(x),(x,43.7,65),(13,2.2,19),7)
# Loading door, raised sill and strong masonry surround; no faux giant opening.
box('Loading_Door',(-36,-24.2,18),(21,2,32),8)
box('Door_Header',(-36,-25,35),(25,4,5),5)
for x in (-48,-24):box('Door_Jamb_'+str(x),(x,-25,18),(4,4,32),5)
box('Door_Sill',(-36,-27,2),(26,9,4),11)
# One squat cylindrical silo, a broad conical cap and tall elevator behind it.
cylinder('Silo_Foundation',39,-28,[(-24,21),(13,21),(16,20)],16,1,11)
cylinder('Silo_Body',39,-28,[(16,19.5),(84,19.5)],16,3,5)
cylinder('Silo_Foot_Rim',39,-28,[(15,20.5),(18,20.5)],16,5)
cylinder('Silo_Cap',39,-28,[(84,22),(86,22),(101,4.5)],16,4,4)
cylinder('Silo_Neck',39,-28,[(100,4),(104,4)],12,6)
box('Elevator_Foundation',(44,2,-8),(18,17,32),11)
box('Elevator',(44,2,63),(14,13,110),14)
box('Elevator_Cap',(44,2,119),(18,17,5),4)
for z in (17,53,88,111):box('Elevator_Band_'+str(z),(44,2,z),(15,14,2),4)
beam('Transfer_Spout',(44,-5,111),(39,-28,103),6,5)
# A single attached loading canopy between house and silo.
mesh('Loading_Canopy',[(10,-20,53),(32,-20,53),(10,-46,44),(32,-46,44),(10,-20,50),(32,-20,50),(10,-46,41),(32,-46,41)],[(0,2,3,1),(4,5,7,6),(0,4,6,2),(1,3,7,5),(2,6,7,3),(0,1,5,4)],[2,10,4,4,4,4])
for x in (11,30):
    box('Bay_Post_'+str(x),(x,-44,12),(3.5,3.5,64),10)
    beam('Bay_Brace_'+str(x),(x,-44,30),(x,-35,45),3,10)
box('Bay_Plinth',(21,-33,-10),(27,29,26),11)
# Small enclosed intake pocket at rear of silo. Clear loading function, no exposed oven.
box('Intake_Base',(63,-2,-9),(18,21,28),11)
for x in (56,70):box('Intake_Post_'+str(x),(x,-2,18),(3,17,30),4)
box('Intake_Hopper',(63,-2,23),(12,14,12),5)
mesh('Intake_Taper',[(57,-9,17),(69,-9,17),(69,5,17),(57,5,17),(61,-4,8),(65,-4,8),(65,0,8),(61,0,8)],[(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],[5]*4)
mesh('Intake_Roof',[(53,-14,32),(73,-14,32),(53,10,40),(73,10,40),(53,-14,29),(73,-14,29),(53,10,37),(73,10,37)],[(0,1,3,2),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3),(4,6,7,5)],[2,4,4,4,4,4])
# Authored stock, entirely part of this building: two upright sacks and a pallet stack.
def sack(name,c,size):
    x,y,z=c;sx,sy,sz=size
    # Squashed, swollen eight-sided bag with pinched upper seam.
    ob=cylinder(name,x,y,[(z,0.78),(z+sz*.15,1),(z+sz*.73,1.03),(z+sz*.93,.80),(z+sz,.68)],8,9,15,True)
    for v in ob.data.vertices:v.co.x=x+(v.co.x-x)*sx/2;v.co.y=y+(v.co.y-y)*sy/2
    return ob
for i,(x,y) in enumerate([(16,-26),(25,-27)]):sack('Sack_Upright_'+str(i),(x,y,3),(8,8,17))
box('Pallet',(13,-48,-.5),(22,15,7),10,True)
for i in range(3):sack('Sack_Stack_'+str(i),(13+(.7 if i==1 else 0),-48,3+i*4.7),(19,12,5))

# Transform raw vertices into the original asset frame, leaving object/root transforms identity.
frame=Matrix.Translation((30,-172,0))@Matrix.Rotation(math.radians(-25),4,'Z')
for ob in meshes:ob.data.transform(frame)
arm=bpy.data.armatures.new(ASSET);rig=bpy.data.objects.new(ASSET,arm);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
bone=arm.edit_bones.new('Bone');bone.head=(0,0,0);bone.tail=(0,0,10);bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
for ob in meshes:
    ob.parent=rig;group=ob.vertex_groups.new(name='Bone');group.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    mod=ob.modifiers.new('Static Bone','ARMATURE');mod.object=rig
    ob.data.uv_layers.new(name='UV2');ob.data.uv_layers.active_index=1
    ob.select_set(True)
bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.012,area_weight=.8,correct_aspect=True,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT')
for ob in meshes:
    layer=ob.data.uv_layers.new(name='UV3')
    for d in layer.data:d.uv=(.02,.02)
    ob.data.uv_layers.active_index=0;ob.select_set(False)

# Low-resolution flat palette is ONLY the geometry review/painting guide, never shipped colour.
im=bpy.data.images.new('Guide_Palette',width=16,height=16)
pixels=[]
for y in range(16):
    for x in range(16):pixels.extend((*COLORS[(3-y//4)*4+x//4],1))
im.pixels[:]=pixels;im.filepath_raw=str(OUT/'textures'/'GUIDE_ONLY.png');im.file_format='PNG';im.save()
tex=nodes.new('ShaderNodeTexImage');tex.name=tex.label='B';tex.image=im;tex.interpolation='Closest';links.new(tex.outputs['Color'],bs.inputs['Base Color'])
uvnode=nodes.new('ShaderNodeUVMap');uvnode.uv_map='UV1';links.new(uvnode.outputs['UV'],tex.inputs['Vector'])

def configure(sc,review=False):
    sc.render.engine='CYCLES';sc.cycles.samples=24
    sc.world=bpy.data.worlds.new(sc.name+'_World');sc.world.use_nodes=True
    bg=sc.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.7,.8,1,1);bg.inputs['Strength'].default_value=.65
    sc.view_settings.view_transform='Standard' if review else 'AgX';sc.view_settings.exposure=-.1 if review else .35;sc.view_settings.gamma=1
    sc.render.resolution_x=sc.render.resolution_y=1024;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True
configure(scene)
review=bpy.data.scenes.new('Review');configure(review,True)
review.collection.objects.link(rig)
for ob in meshes:review.collection.objects.link(ob)
light=bpy.data.lights.new('Review_Key','SUN');light.energy=3.2;light.color=(1,.92,.8);light.angle=math.radians(6)
sun=bpy.data.objects.new('Review_Key',light);review.collection.objects.link(sun);sun.rotation_euler=(math.radians(25),math.radians(-30),math.radians(-35))
camera=bpy.data.objects.new('Review_Camera',bpy.data.cameras.new('Review_Camera'));review.collection.objects.link(camera)
target=Vector((33,-177,48));camera.location=target+Vector((220,-330,255));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=200;review.camera=camera
bpy.context.window.scene=review
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')))
review.render.filepath=str(OUT/'01_geometry_review.png');bpy.ops.render.render(write_still=True)
(OUT/'uv_contract.json').write_text(json.dumps({'asset':ASSET,'atlas':{'rows':4,'cols':4,'padding_fraction':.025},'surfaces':uv_guide,'palette':COLORS},indent=2))
print('MODERN_MILL_BUILT',len(meshes),'objects',sum(len(o.data.vertices) for o in meshes),'authored vertices')
