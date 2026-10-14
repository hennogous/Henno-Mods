"""Build an editable, atlas-mapped Fashion House coach and native export package."""
import bpy, bmesh, math, json, sys, shutil, importlib.util, subprocess, copy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\Fashion-coach-20261013')
STAGE=OUT/'atlas-release'
ID='CSC_TAILORS_Fashion_Coach'
PARTS=[]
REGIONS={r['name']:r['bounds'] for r in json.loads((STAGE/'atlas/manifest.json').read_text())['regions']}

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def mesh(name,vs,fs,patch,uvs=None,smooth=False):
    data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update()
    ob=bpy.data.objects.new(name,data); export.collection.objects.link(ob); review.collection.objects.link(ob)
    data.materials.append(mat); ob['export_role']='fixed_geometry';ob['source_asset_id']=ID
    for n in ['UV1','UV2','UV3']:data.uv_layers.new(name=n)
    x,y,x1,y1=REGIONS[patch]
    for poly in data.polygons:
        poly.use_smooth=smooth
        for j,li in enumerate(poly.loop_indices):
            if uvs is not None:u,v=uvs[data.loops[li].vertex_index]
            else:u,v=[(.015,.015),(.985,.015),(.985,.985),(.015,.985)][j%4]
            data.uv_layers[0].data[li].uv=((x+(x1-x)*u)/1024,1-(y+(y1-y)*(1-v))/1024)
            data.uv_layers[1].data[li].uv=(u,v)
            data.uv_layers[2].data[li].uv=(.01,.01)
    PARTS.append(ob);return ob

def quad(name,vs,patch):return mesh(name,vs,[(0,1,2,3)],patch)

def roofline(x):
    knots=[(-9,15.4),(-7.5,15.95),(-1,16.6),(5,16.05),(6.5,15.4)]
    for (a,h),(b,j) in zip(knots,knots[1:]):
        if a<=x<=b:return h+(j-h)*(x-a)/(b-a)
    raise ValueError(x)

def side_window(name,a,b,y):
    xs=[a]+[x for x in [-7.5,-1,5] if a<x<b]+[b]
    vs=[(a,y*4.25,10),(b,y*4.25,10)]+[(x,y*4.15,roofline(x)) for x in reversed(xs)]
    uv=[(0,0),(1,0)]+[((x-a)/(b-a),1) for x in reversed(xs)]
    ob=mesh(name,vs,[tuple(range(len(vs)))],'coach_curtained_window',uv)
    if y>0:ob.data.flip_normals()
    return ob

def box(name,c,size,patch,cap=True):
    x,y,z=c;a,b,d=[s/2 for s in size]
    v=[(x+sx*a,y+sy*b,z+sz*d) for sz in [-1,1] for sy in [-1,1] for sx in [-1,1]]
    f=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    return mesh(name,v,f if cap else f[1:],patch)

def rod(name,a,b,r,patch,sides=3):
    a,b=Vector(a),Vector(b);z=(b-a).normalized();v=z.cross(Vector((0,0,1)))
    if v.length<.01:v=z.cross(Vector((0,1,0)))
    v.normalize();w=z.cross(v)
    verts=[tuple(p+r*(math.cos(i*2*math.pi/sides)*v+math.sin(i*2*math.pi/sides)*w)) for p in [a,b] for i in range(sides+1)]
    faces=[(i,i+1,i+1+sides+1,i+sides+1) for i in range(sides)]
    ob=mesh(name,verts,faces,patch,[(i/sides,k) for k in [0,1] for i in range(sides+1)])
    ob['keep_strip_ao']=True
    return ob

def wheel(name,x,y,r,n):
    z=r; vs=[];uv=[];fs=[]
    # Closed rounded rectangular rim, continuous strip UVs; a single seam.
    profile=[(r,-.22),(r,.22),(r-.45,.22),(r-.45,-.22),(r,-.22)]
    for k,(rad,dy) in enumerate(profile):
        for i in range(n+1):
            t=2*math.pi*i/n;vs.append((x+rad*math.cos(t),y+dy,z+rad*math.sin(t)));uv.append((i/n,k/4))
    for k in range(4):
        for i in range(n):a=k*(n+1)+i;fs.append((a,a+1,a+n+2,a+n+1))
    ob=mesh(name+'_Rim',vs,[tuple(reversed(f)) for f in fs],'coach_black_leather',uv,True)
    ob['keep_strip_ao']=True
    # Thin spoke blades: separate front and back winding, real visible gaps.
    for j in range(6):
        t=j*math.pi/3;dr=Vector((math.cos(t),0,math.sin(t)));per=Vector((-math.sin(t),0,math.cos(t)))
        for side in [-1,1]:
            center=Vector((x,y+side*.10,z))
            a=center+dr*.30;b=center+dr*(r-.36)
            v=[tuple(a-per*.12),tuple(b-per*.12),tuple(b+per*.12),tuple(a+per*.12)]
            if side>0:v.reverse()
            quad(name+f'_Spoke{j}_{side}',v,'coach_claret_panel')
    # Compact hexagonal brass hub.
    vs=[];uv=[]
    for dy,rr in [(-.30,.43),(.30,.43)]:
        for i in range(6):
            t=2*math.pi*i/6;vs.append((x+rr*math.cos(t),y+dy,z+rr*math.sin(t)));uv.append((.5+.4*math.cos(t),.5+.4*math.sin(t)))
    fs=[tuple(range(5,-1,-1)),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
    mesh(name+'_Hub',vs,[tuple(reversed(f)) for f in fs],'antique_brass',uv)

def main():
    global export,review,mat
    bpy.ops.wm.read_factory_settings(use_empty=True)
    export=bpy.context.scene;export.name='Export';review=bpy.data.scenes.new('Review')
    tex=OUT/'textures';tex.mkdir(exist_ok=True)
    for p in (STAGE/'textures').glob('*.png'):shutil.copy2(p,tex/p.name)
    mat=bpy.data.materials.new('CSC_ALL_Props_01');mat.use_nodes=True
    nt=mat.node_tree;nt.nodes.clear();bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.65
    output=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(bs.outputs['BSDF'],output.inputs['Surface'])
    for i,k in enumerate(['B','N','G','M','AO']):
        im=bpy.data.images.load(str(tex/f'CSC_Props_Shared_01_{k}.png'),check_existing=True)
        im.colorspace_settings.name='sRGB' if k=='B' else 'Non-Color'
        node=nt.nodes.new('ShaderNodeTexImage');node.image=im;node.label=k;node.location=(-800,i*-230)
        uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='UV2' if k=='AO' else 'UV1';nt.links.new(uv.outputs[0],node.inputs[0])
        if k=='B':base=node
        if k=='AO':ao=node
        if k=='M':nt.links.new(node.outputs['Color'],bs.inputs['Metallic'])
        if k=='N':normal=nt.nodes.new('ShaderNodeNormalMap');nt.links.new(node.outputs['Color'],normal.inputs['Color']);nt.links.new(normal.outputs[0],bs.inputs['Normal'])
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.5
    nt.links.new(base.outputs[0],mix.inputs[1]);nt.links.new(ao.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
    # Body length along X, front at +X. Ground-centred support pivot at origin.
    for x,r,n in [(-7,4.8,12),(7,3.4,10)]:
        for y in [-5.9,5.9]:wheel(('Rear' if x<0 else 'Front')+('_Near' if y<0 else '_Far'),x,y,r,n)
    for y in [-3.4,3.4]:
        rod('Chassis_Rail'+str(y),(-9,y,4.8),(9,y,4.8),.32,'coach_black_leather')
        rod('Draw_Shaft'+str(y),(8,y,3.7),(18,y,3.4),.18,'coach_black_leather')
    for x,z in [(-7,4.8),(7,3.4)]:rod('Axle'+str(x),(x,-5.9,z),(x,5.9,z),.27,'coach_black_leather')
    box('Cabin_Floor',(-1,0,5.8),(14,8.4,.6),'dark_timber')
    # Tapered lower shell, large calm ornament panels.
    for y in [-1,1]:
        for a,b in ([(-8.5,-4.1),(1.2,6)] if y<0 else [(-8.5,6)]):
            quad('Lower_Side'+str((y,a)),[(a+.3,y*3.7,6.1),(b-.3,y*3.7,6.1),(b,y*4.25,10),(a,y*4.25,10)],'coach_claret_panel')
            if y>0: PARTS[-1].data.flip_normals()
        for a,b in [(-8.5,-4.1),(1.2,6)]:
            side_window('Window'+str((y,a)),a,b,y)
        if y>0:
            mesh('Far_Door',[(-4.1,4.25,6.2),(-4.1,4.15,roofline(-4.1)),(-1,4.15,roofline(-1)),(1.2,4.15,roofline(1.2)),(1.2,4.25,6.2)],[(0,1,2,3,4)],'coach_claret_panel',[(0,0),(0,1),(.585,1),(1,1),(1,0)])
        # Fine doorway trim is already in the panel/window paint; no trim rods.
    for x in [-8.5,6]:
        mesh('End_Claret'+str(x),[(x,-4.25,6.1),(x,4.25,6.1),(x,4.15,roofline(x)),(x,0,roofline(x)+.7),(x,-4.15,roofline(x))],[(0,1,2,3,4)],'coach_claret_panel',[(0,0),(1,0),(1,.93),(.5,1),(0,.93)])
        if x<0:PARTS[-1].data.flip_normals()
    # Economical inward shell and upholstery visible through the open doorway.
    quad('Interior_Back',[(-8.4,4.05,6.15),(5.9,4.05,6.15),(5.9,4.05,15.3),(-8.4,4.05,15.3)],'claret_cloth')
    box('Passenger_Seat',(-5.7,.7,6.8),(4,5.9,1.2),'claret_cloth',False)
    for x in [-8.4,5.9]:
        quad('Interior_End'+str(x),[(x,-4.05,6.15),(x,4.05,6.15),(x,4.05,15.3),(x,-4.05,15.3)],'claret_cloth')
        if x>0:PARTS[-1].data.flip_normals()
    # Arched roof is longitudinally cambered as in the reference.
    vs=[];uv=[]
    for x,raisez in [(-9,0),(-7.5,.55),(-1,1.2),(5,.65),(6.5,0)]:
        for y,z in [(-4.65,15.45),(0,16.15),(4.65,15.45)]:vs.append((x,y,z+raisez));uv.append(((x+9)/15.5,(y+4.65)/9.3))
    fs=[(i*3+j,(i+1)*3+j,(i+1)*3+j+1,i*3+j+1) for i in range(4) for j in range(2)]
    mesh('Cambered_Leather_Roof',vs,fs,'coach_black_leather',uv,True)
    mesh('Interior_Ceiling',[(x,y,z-.08) for x,y,z in vs],[tuple(reversed(f)) for f in fs],'coach_black_leather',uv,True)
    # No geometry strips for roof edging or seat ornament at game scale.
    # Driver's box and rich padded seat.
    box('Drivers_Box',(8,0,6.25),(3.5,7.8,3),'coach_claret_panel')
    box('Drivers_Cushion',(7.8,0,8.05),(3.5,7.8,.65),'claret_cloth',False)
    box('Drivers_Backrest',(6.35,0,9.15),(.5,7.8,2.3),'claret_cloth',False)
    box('Entry_Step',(-.6,-5.8,3.8),(2.8,2.3,.28),'antique_brass')
    for x in [-1.65,.45]:
        vs=[(x,-4.1,5.75),(x,-4.1,3.65),(x,-6.6,3.65)]
        mesh('Step_Bracket'+str(x),vs+[(a+.08,b,c) for a,b,c in vs],[(0,1,2),(5,4,3)],'coach_black_leather',[(0,1),(0,0),(1,0)]*2)
    # Open coach door: hinged toward the front, with curtain and gilded panel.
    hinge=Vector((1.1,-4.35,6.2));d=Vector((.08,-.997,0))*3.4
    for name,z0,z1,patch in [('Door_Lower',0,3.9,'coach_claret_panel'),('Door_Upper',3.9,9.2,'coach_curtained_window')]:
        pts=[tuple(hinge+Vector((0,0,z0))),tuple(hinge+d+Vector((0,0,z0))),tuple(hinge+d+Vector((0,0,z1))),tuple(hinge+Vector((0,0,z1)))]
        quad(name,pts,patch);quad(name+'_Inner',list(reversed([(x+.035,y-.035,z) for x,y,z in pts])),patch)
    # Two compact brass lanterns with ivory glass, no emission.
    for y in [-4.6,4.6]:
        box('Lantern'+str(y),(6.2,y,12.0),(.75,.7,1.6),'embroidered_ivory')
        ob=mesh('Lantern_Cap'+str(y),[(5.65,y-.55,12.8),(6.75,y-.55,12.8),(6.75,y+.55,12.8),(5.65,y+.55,12.8),(6.2,y,13.55)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'antique_brass',[(0,0),(1,0),(1,1),(0,1),(.5,.5)])
        ob['keep_strip_ao']=True
    # A blue dress inside evokes the fashion delivery without adding a passenger.
    vs=[];uv=[]
    for z,rx,ry in [(6.2,1.45,1),(8.3,.85,.6),(10.5,.43,.35)]:
        for i in range(8+1):t=2*math.pi*i/8;vs.append((-2+rx*math.cos(t),-3.1+ry*math.sin(t),z));uv.append((i/8,(z-6.2)/4.3))
    mesh('Sapphire_Gown',vs,[(k*9+i,k*9+i+1,(k+1)*9+i+1,(k+1)*9+i) for k in range(2) for i in range(8)],'sapphire_cloth',uv,True)
    # Unwrap only AO. Existing material UVs remain fixed.
    bpy.context.window.scene=export
    for o in bpy.context.selected_objects:o.select_set(False)
    for o in PARTS:o.select_set(not o.get('keep_strip_ao'));o.data.uv_layers.active_index=1
    bpy.context.view_layer.objects.active=next(o for o in PARTS if not o.get('keep_strip_ao'))
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(78),island_margin=.012,area_weight=.5,correct_aspect=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    for o in PARTS:o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.pack_islands(rotate=True,margin=.008)
    bpy.ops.object.mode_set(mode='OBJECT')
    for o in PARTS:
        for loop in o.data.uv_layers[1].data:loop.uv=(.02+loop.uv.x*.96,.04+loop.uv.y*.92)
    validator=module('coach_validation',ROOT/'project/tools/blender/csc_scene_validation.py')
    counts={o.name:validator.export_vertex_count(o.data) for o in PARTS}
    (OUT/'early-counts.json').write_text(json.dumps(dict(total=sum(counts.values()),parts=counts),indent=2))
    print('COACH_COUNT',sum(counts.values()))
    # Rig shared between source scenes.
    rigdata=bpy.data.armatures.new(ID+'_Rig');rig=bpy.data.objects.new(ID+'_Rig',rigdata)
    export.collection.objects.link(rig);review.collection.objects.link(rig)
    for o in bpy.context.selected_objects:o.select_set(False)
    rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
    bone=rigdata.edit_bones.new('Bone');bone.head=(0,0,0);bone.tail=(0,0,1);bpy.ops.object.mode_set(mode='OBJECT')
    for o in PARTS:
        o.vertex_groups.new(name='Bone').add(list(range(len(o.data.vertices))),1,'REPLACE')
        o.modifiers.new('Static rig','ARMATURE').object=rig
    for s in [export,review]:
        s.render.engine='CYCLES';s.cycles.samples=48
        w=bpy.data.worlds.new(s.name+'_World');w.use_nodes=True;s.world=w
        bg=next(n for n in w.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.7,.8,1,1);bg.inputs[1].default_value=.65
        s.view_settings.view_transform='AgX' if s==export else 'Standard';s.view_settings.exposure=.35 if s==export else -.1
    light=bpy.data.lights.new('Review_Key','SUN');light.energy=3.2;light.angle=math.radians(6);light.color=(1,.92,.8)
    ob=bpy.data.objects.new('Review_Key',light);review.collection.objects.link(ob);ob.rotation_euler=Vector((300,280,-500)).to_track_quat('-Z','Y').to_euler()
    cam=bpy.data.cameras.new('Review_Camera');ob=bpy.data.objects.new('Review_Camera',cam);review.collection.objects.link(ob)
    center=Vector((2,0,8));ob.location=center+Vector((34,-50,31));ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
    cam.type='ORTHO';cam.ortho_scale=38;review.camera=ob
    review.render.resolution_x=1100;review.render.resolution_y=900;review.render.resolution_percentage=100;review.render.film_transparent=True
    review.render.image_settings.file_format='PNG';review.render.filepath=str(OUT/'coach-preview.png')
    bpy.context.window.scene=review
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ID+'.blend')));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ID+'.blend')))
    bpy.ops.render.render(write_still=True)
    print('COACH_BUILT')

if __name__=='__main__':main()
