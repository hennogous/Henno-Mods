"""Concept refinement: straight lighter roof, broad silo, exposed work scene, consistent material scale."""
import bpy,sys,math,json,ast,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4];OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
PREV=Path.home()/'Desktop/Codex/modern-windmill-v5-20261026'
bpy.ops.wm.open_mainfile(filepath=str(PREV/(ASSET+'.blend')))
scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene
rig=bpy.data.objects[ASSET];mat=bpy.data.materials[ASSET]
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)));inv=frame.inverted()
sx,sy=15.385688781738281,-72.42012023925781
meshes=[];uv_guide=[]
tree=ast.parse((Path(__file__).parent/'build_model.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('tileuv','mesh','box','beam','cylinder')],type_ignores=[]),'<geometry helpers>','exec'))
# Work in the house's source frame, preserving the exact historical tower axis.
for ob in list(scene.objects):
    if ob.type!='MESH':continue
    n=ob.name.removeprefix('CSC_Fixed_')
    if n.startswith(('Silo_','Elevator','Transfer_','Sack_','Stock_','Support_Foot_')):
        bpy.data.objects.remove(ob,do_unlink=True);continue
    ob.data.transform(inv)
    if n=='Main_Roof':
        for v in ob.data.vertices:
            sweep=(abs(v.co.x)/49)**2*1.8;z=v.co.z-sweep
            v.co.x*=47.5/49;v.co.y*=26/30
            v.co.z={82:80,79:77.6,77:77.6,59:61.5,56:59.1,54:59.1}.get(round(z),z)
    elif n=='Main_Ridge':
        for v in ob.data.vertices:
            oldz=v.co.z-(abs(v.co.x)/50)**2*1.8-.4
            v.co.x*=96/99.84;v.co.y*=4.8/7.2;v.co.z=80.5+(oldz-82)*3.4/5.7
    elif n=='Upper_Brick':
        for v in ob.data.vertices:v.co.z=35.5+(v.co.z-35.5)*27/24
    elif n=='Gable_Brick':
        for v in ob.data.vertices:v.co.z=62.5+(v.co.z-59.5)*(78.5-62.5)/(81-59.5)
    elif n=='Shelter_Roof':
        for v in ob.data.vertices:
            v.co.x=22+(v.co.x-22)/1.07;v.co.y=-46.5+(v.co.y+46.5)/1.045
            v.co.z={55:52.5,50:50.2,40:40,35:37.7}.get(round(v.co.z),v.co.z)
    elif n=='Shelter_Ridge':
        for v in ob.data.vertices:v.co.x=22+(v.co.x-22)*4.5/7.2;v.co.z=53+(v.co.z-55)*3.3/5.7
    elif n=='Shelter_Gable':
        for v in ob.data.vertices:v.co.z=39+(v.co.z-39)*(50-39)/(52-39)
    elif n.startswith('Shelter_Support_'):
        c=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
        for v in ob.data.vertices:v.co.x=c.x+(v.co.x-c.x)*.67;v.co.y=c.y+(v.co.y-c.y)*.67
    elif n=='Shelter_Header':
        c=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
        for v in ob.data.vertices:v.co.y=c.y+(v.co.y-c.y)*.72;v.co.z=c.z+(v.co.z-c.z)*.70
    elif n=='House_Foundation':
        for v in ob.data.vertices:v.co.x*=88/84;v.co.y*=52/48;v.co.z=-30 if v.co.z<0 else 0
    elif n in ('Front_Lower','Rear_Lower','End_Lower') or n.startswith('Entrance_Masonry'):
        for v in ob.data.vertices:
            taper=max(0,1-v.co.z/34);v.co.x*=1+2/42*taper;v.co.y*=1+2/24*taper
    elif 'Window' in n:
        c=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
        for v in ob.data.vertices:
            if n.startswith(('Front','Rear')):v.co.x=c.x+(v.co.x-c.x)*.9
            else:v.co.y=c.y+(v.co.y-c.y)*.9
            if n=='Front_Window_-21_17':v.co.y=-24.10-2*(1-v.co.z/34)
    ob['revision']='v6 straight roof / consistent surface scale'

def battered_box(name,c,width,depth,topwidth,topdepth,topz,tile):
    x,y=c;vs=[]
    for z,w,d in [(-30,width,depth),(0,width,depth),(topz,topwidth,topdepth)]:
        vs.extend([(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z)])
    fs=[(0,3,2,1),(8,9,10,11)]
    for j in (0,4):
        for i in range(4):fs.append((j+i,j+(i+1)%4,j+4+(i+1)%4,j+4+i))
    return mesh(name,vs,fs,[tile]*len(fs))
for x,y in [(3,-27),(41,-27),(41,-65)]:battered_box('Support_Foot_'+str(x)+'_'+str(y),(x,y),9,9,6.5,6.5,4,1)
# Broader body, flatter cap, and a visibly battered two-course stone plinth.
foundation=cylinder('Silo_Foundation',sx,sy,[(-30,28),(0,28),(16,25)],16,1,11)
silo=cylinder('Silo_Body',sx,sy,[(16,24),(75,24)],16,12,5,start=math.pi/2)
cylinder('Silo_Foot_Rim',sx,sy,[(14,25),(17,25)],16,5)
cap=cylinder('Silo_Cap',sx,sy,[(75,27),(77,27),(88,4)],16,4,4)
cylinder('Silo_Neck',sx,sy,[(87,3.5),(90,3.5)],12,6)
# The wheat panel faces local southwest, towards the concept camera, not around the side.
for p in silo.data.polygons:
    if p.index>=16:continue
    i=p.index
    if 4<=i<8:
        coords=[((i-4)/4,0),((i-3)/4,0),((i-3)/4,1),((i-4)/4,1)];t=3
    else:
        coords=[(.18,0),(.25,0),(.25,1),(.18,1)];t=3
    for li,(u,v) in zip(p.loop_indices,coords):silo.data.uv_layers['UV1'].data[li].uv=tileuv(t,u,v)
for p in cap.data.polygons:
    if p.index>=32:continue
    side=p.index%16
    for li in p.loop_indices:
        vi=cap.data.loops[li].vertex_index;v=cap.data.vertices[vi].co
        cap.data.uv_layers['UV1'].data[li].uv=tileuv(2,0 if vi%16==side else 1/12,(v.z-75)/13)
# Elevator casing detail and reinforcement bands are entirely painted/normal mapped.
battered_box('Elevator_Foundation',(55,-62),19,18,15,14,6,1)
box('Elevator',(55,-62,55),(13,12,98),14);box('Elevator_Cap',(55,-62,105),(16,15,4),4)
path=[Vector(p) for p in [(55,-68,99),(51,-69,98.8),(23,-71.7,91.5),(18,-72.3,91),(sx,sy,89),(sx,sy,87.5)]]
vs=[];fs=[];uvs=[];n=8
for j,c in enumerate(path):
    tangent=(path[min(j+1,len(path)-1)]-path[max(0,j-1)]).normalized();q=tangent.to_track_quat('Z','Y')
    for i in range(n):vs.append(c+q@Vector((3.2*math.cos(i*2*math.pi/n),3.2*math.sin(i*2*math.pi/n),0)))
for j in range(len(path)-1):
    for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
fs.extend([tuple(reversed(range(n))),tuple(range((len(path)-1)*n,len(path)*n))])
pipe=mesh('Rounded_Transfer_Pipe',vs,fs,[5]*len(fs))
for p in pipe.data.polygons:p.use_smooth=True
# Compact enclosed intake pocket, as in the approved concept.
battered_box('Intake_Foundation',(68,-58),15,17,12,14,4,1)
box('Intake_Frame',(68,-58,14),(11,12,20),4);box('Intake_Hopper',(68,-58,23),(10,11,8),12)
mesh('Intake_Roof',[(60,-67,28),(76,-67,28),(60,-49,32),(76,-49,32),(60,-67,26),(76,-67,26),(60,-49,30),(76,-49,30)],[(0,1,3,2),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3),(4,6,7,5)],[2,4,4,4,4,4])

# Rounded rectangular bags: fewer, broad folds rather than pancake-like cylinders.
def bag(name,c,size,standing=True):
    x,y,z=c;w,d,h=size;outline=[(-.35,-.5),(.35,-.5),(.5,-.30),(.5,.30),(.35,.5),(-.35,.5),(-.5,.30),(-.5,-.30)]
    vs=[]
    for zz,s in [(0,.78),(.2,1),(.78,1),(.97,.78),(1,.65)]:vs.extend([(x+u*w*s,y+v*d*s,z+zz*h) for u,v in outline])
    fs=[];ts=[];uv=[]
    for j in range(4):
        for i in range(8):
            fs.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i));ts.append(9 if i in (0,7) and standing else 15)
            uv.append([(i/8,j/4),((i+1)/8,j/4),((i+1)/8,(j+1)/4),(i/8,(j+1)/4)])
    fs.extend([tuple(reversed(range(8))),tuple(range(32,40))]);ts.extend([15,15 if standing else 9])
    uv.extend([[((u+.5),(v+.5)) for u,v in reversed(outline)],[((u+.5),(v+.5)) for u,v in outline]])
    ob=mesh(name,vs,fs,ts,uv,True)
    # Full printed face on the broad visible side; side folds use the plain sack patch.
    for p in ob.data.polygons:
        if p.index<32:
            i=p.index%8;j=p.index//8
            for li in p.loop_indices:
                v=ob.data.vertices[ob.data.loops[li].vertex_index].co
                ob.data.uv_layers['UV1'].data[li].uv=tileuv(9 if i==0 and standing else 15,(v.x-x)/w+.5,(v.z-z)/h)
        p.use_smooth=p.index<32
    return ob
bag('Sack_Upright_A',(-7,-43,-1),(11,9,19));bag('Sack_Upright_B',(4,-40,-1),(11,9,20))
box('Visible_Pallet',(-18,-55,-2),(24,17,8),10,True)
for i in range(3):bag('Visible_Stack_'+str(i),(-18+(.6 if i==1 else 0),-55,2+i*5.2),(22,15,5.7),False)
# Hand truck silhouette: two rails, a toe plate, axle and wheels; no bolts or tread mesh.
tx,ty=-12,-86
for x in (tx-5,tx+5):beam('Truck_Rail_'+str(x),(x,ty+2,2),(x,ty+8,27),1.8,6,True)
beam('Truck_Handle',(tx-5,ty+8,27),(tx+5,ty+8,27),1.8,6,True)
box('Truck_Toe',(tx,ty-2,2),(12,10,2),6,True);beam('Truck_Axle',(tx-7,ty+2,4),(tx+7,ty+2,4),2,6,True)
for side in (-1,1):
    wheel=cylinder('Truck_Wheel_'+str(side),0,0,[(-1.2,4),(1.2,4)],10,6,6,True,start=0)
    m=Matrix.Translation(Vector((tx+side*6.5,ty+2,4)))@Matrix.Rotation(math.pi/2,4,'Y');wheel.data.transform(m)
bag('Truck_Flour_Sack',(tx,ty,3),(10,8,17))

# Continuous repeating UVs with world-sized periods. Split only at texture-cell boundaries.
# This topology supports UV registration; there is no modeled mortar/seam relief.
def clip(poly,axis,bound,keep_greater):
    result=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        da=a[axis]-bound;db=b[axis]-bound;ina=da>=-1e-7 if keep_greater else da<=1e-7;inb=db>=-1e-7 if keep_greater else db<=1e-7
        if ina:result.append(a)
        if ina!=inb:result.append(a+(b-a)*(da/(da-db)))
    return result
def map_periodic(ob,tile,period,roof=False):
    old=ob.data;verts=[];faces=[];uvs=[]
    for p in old.polygons:
        original=[old.vertices[i].co.copy() for i in p.vertices]
        axis=max(range(3),key=lambda a:abs(p.normal[a]));axes=([1,2] if axis==0 else [0,2] if axis==1 else [0,1])
        if roof and abs(p.normal.z)>.5:
            axes=[0,1] if 'Main_Roof' in ob.name else [1,0]
        a,b=axes;pw,ph=period
        for iu in range(math.floor(min(v[a] for v in original)/pw),math.floor((max(v[a] for v in original)-1e-6)/pw)+1):
            for iv in range(math.floor(min(v[b] for v in original)/ph),math.floor((max(v[b] for v in original)-1e-6)/ph)+1):
                poly=original
                for ax,edge,greater in [(a,iu*pw,True),(a,(iu+1)*pw,False),(b,iv*ph,True),(b,(iv+1)*ph,False)]:poly=clip(poly,ax,edge,greater) if poly else []
                if len(poly)<3:continue
                # Reject degenerate clipped slivers on boundaries.
                if sum(((poly[j]-poly[0]).cross(poly[j+1]-poly[0]).length for j in range(1,len(poly)-1)))<1e-6:continue
                k=len(verts);verts.extend(poly);faces.append(tuple(range(k,k+len(poly))));uvs.append([tileuv(tile,v[a]/pw-iu,v[b]/ph-iv) for v in poly])
    me=bpy.data.meshes.new(old.name+'_world_sampled');me.from_pydata(verts,[],faces);me.materials.append(mat);me.update();uv=me.uv_layers.new(name='UV1')
    for p,coords in zip(me.polygons,uvs):
        for li,co in zip(p.loop_indices,coords):uv.data[li].uv=co
    ob.data=me
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001);bm.to_mesh(me);bm.free()

allmeshes=[o for o in scene.objects if o.type=='MESH']
for ob in allmeshes:
    n=ob.name.removeprefix('CSC_Fixed_')
    if n in ('Upper_Brick','Gable_Brick'):map_periodic(ob,0,(64,32))
    elif n in ('Front_Lower','Rear_Lower','End_Lower','House_Foundation') or n.startswith('Entrance_Masonry'):map_periodic(ob,1,(84,32))
    elif n in ('Main_Roof','Shelter_Roof','Intake_Roof'):
        # Roof sampling follows the broad sheets; eave thickness shares the plain green tile.
        map_periodic(ob,2,(96,32),True)
    elif n=='Silo_Foundation':
        # Sixteen sides each represent a real arc length, with two visible 8-unit courses.
        for p in ob.data.polygons:
            if p.index>=32:continue
            i=p.index%16;row=p.index//16
            for li in p.loop_indices:
                vi=ob.data.loops[li].vertex_index;v=ob.data.vertices[vi].co
                u=((i%8)+(1 if vi%16==(i+1)%16 else 0))/8
                ob.data.uv_layers['UV1'].data[li].uv=tileuv(1,u,max(0,min(1,v.z/32)))
    ob.data.transform(frame);ob.parent=rig
    if ob.name not in review.objects:review.collection.objects.link(ob)
    ob.vertex_groups.clear();group=ob.vertex_groups.new(name='Bone');group.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    if not any(m.type=='ARMATURE' for m in ob.modifiers):mod=ob.modifiers.new('Static Bone','ARMATURE');mod.object=rig
    while len(ob.data.uv_layers)>1:ob.data.uv_layers.remove(ob.data.uv_layers[-1])
    ob.data.uv_layers.new(name='UV2');ob.data.uv_layers.new(name='UV3')
    for d in ob.data.uv_layers['UV3'].data:d.uv=(.02,.02)

bpy.ops.object.select_all(action='DESELECT')
for ob in allmeshes:ob.select_set(True);ob.data.uv_layers.active_index=1
bpy.context.view_layer.objects.active=allmeshes[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.008,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
for ch in ('B','N','G','M','E'):
    im=bpy.data.images.load(str(OUT/'textures'/f'{ASSET}_{ch}.png'),check_existing=False);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';nodes[ch].image=im
for l in list(bs.inputs['Normal'].links):links.remove(l)
links.new(nodes['B'].outputs['Color'],bs.inputs['Base Color'])
ao=bpy.data.images.new(ASSET+'_AO_v6',width=2048,height=2048,alpha=False);ao.colorspace_settings.name='Non-Color';nodes['AO'].image=ao;nodes.active=nodes['AO'];scene.cycles.samples=24;scene.render.bake.margin=6;bpy.ops.object.bake(type='AO',uv_layer='UV2');ao.filepath_raw=str(OUT/'textures'/f'{ASSET}_AO.png');ao.file_format='PNG';ao.save()
mix=next(n for n in nodes if n.type=='MIX_RGB');mix.inputs[0].default_value=.35;normal=next(n for n in nodes if n.type=='NORMAL_MAP');normal.inputs['Strength'].default_value=1.15;links.new(mix.outputs[0],bs.inputs['Base Color']);links.new(normal.outputs[0],bs.inputs['Normal'])
for ob in allmeshes:ob.data.uv_layers.active_index=0;ob.select_set(False)
for im in list(bpy.data.images):
    if im.users==0:bpy.data.images.remove(im)
for ch in ('B','N','G','M','E','AO'):nodes[ch].image.filepath='//textures/'+f'{ASSET}_{ch}.png'
bpy.context.window.scene=review;review['revision_scope']='v6 concept refinement; straight roofs, battered buried bases, world-scale ImageGen materials, visible stock and hand truck.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
for ch in ('B','N','G','M','E','AO'):nodes[ch].image.reload()
sys.path.insert(0,str(ROOT/'project/tools/blender/scene_export'));import decode_blend as decoder
bpy.context.window.scene=scene;joined=decoder.merge_meshes(ASSET,[decoder.decode_mesh(o,o.matrix_world) for o in allmeshes])
report={'revision':'v6 concept refinement','export_vertices':len(joined['vertices']),'triangles':len(joined['triangles']),'silo_center_local':[sx,sy],'silo_radius':24,'foundation_depth':30,'roof_sweep':False,'texture_sampling':'brick 8x4; stone 14x8; roof seam pitch8 model units','runtime_installed':False}
(OUT/'assembly-review-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
# Review matched to the concept, using the same public rendering helper.
sys.argv=[str(ROOT/'project/tools/art/modern_windmill/render_concept_angle.py'),'--',str(OUT)]
exec(compile((ROOT/'project/tools/art/modern_windmill/render_concept_angle.py').read_text(),'<concept camera>','exec'))
