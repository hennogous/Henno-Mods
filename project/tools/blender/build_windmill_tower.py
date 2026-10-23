"""Author the approved plaster/ladder windmill in the existing AE attachment frame.

Paint comes from the registered ImageGen plaster and existing shared atlas swatches.
This script creates geometry, UVs, a local geometry AO bake and a native animation.
"""
import bpy,math,json,sys,importlib.util
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(sys.argv[sys.argv.index('--')+1]);ART=Path.home()/'Desktop/Working Files/3D Art'
NAME='CSC_BAKERS_Wind_Mill_Tower'
MATS=['CSC_BAKERS_Wind_Mill_Plaster','CSC_BAKERS_Wind_Mill_Sails']
layout=json.loads((OUT/'atlas-migration.json').read_text());regions={r['id']:r for r in layout['regions']}
prop=json.loads((ART/'Textures/CSC_Props/Current/atlas/manifest.json').read_text())
swatches={r['name']:r['bounds'] for r in prop['regions']}
RIGHT=Vector((math.sqrt(3)/2,-.5,0));BACK=Vector((.5,math.sqrt(3)/2,0));UP=Vector((0,0,1))
HUB=Vector((26.99117,-41.48987,90.94731));CENTER=HUB+BACK*20;CENTER.z=0
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.name='Export';scene.render.fps=30;scene.frame_start=1;scene.frame_end=301
scene['asset_id']=NAME;scene['source_concept']=str(OUT.parent/'windmill-concepts-20261021/03-tower.png')
scene['atlas_layout']='storage-tower-v3';scene['animation_notes']='Stationary tower; four rigid ladder sails, 360 degrees in ten seconds. No pose-dependent shadow baked from rotor onto tower.'
parts={k:{'v':[],'f':[],'uv':[],'mat':[],'smooth':[]} for k in ['Tower','Sails']}

def atlas_rect(key):
    if key=='plaster':return layout['tower_plaster']['inner']
    r=regions[key];b=r['uv_bounds'];dx,dy=r['delta'];rect=[b[0]+dx+1,b[1]+dy+1,b[2]+dx-1,b[3]+dy-1]
    if key=='storage_22':rect[2]=rect[0]+84;rect[3]=rect[1]+31
    if key=='storage_00':rect[3]=rect[1]+43
    return rect

def add(label,verts,faces,key,mat=0,uvs=None,smooth=False):
    p=parts[label];offset=len(p['v']);p['v'].extend([tuple(v) for v in verts])
    rect=swatches[key] if mat==1 else atlas_rect(key)
    for j,f in enumerate(faces):
        p['f'].append([offset+i for i in f]);p['mat'].append(mat);p['smooth'].append(smooth)
        coords=uvs[j] if uvs else ([(0,0),(1,0),(1,1),(0,1)] if len(f)==4 else [(0,0),(1,0),(.5,1)])
        p['uv'].append([( (rect[0]+u*(rect[2]-rect[0]))/1024, 1-(rect[3]-v*(rect[3]-rect[1]))/1024) for u,v in coords])

def box(label,center,axes,dims,key,mat=1):
    c=Vector(center);a,b,d=[Vector(v)*s/2 for v,s in zip(axes,dims)]
    verts=[c+i*a+j*b+k*d for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    add(label,verts,faces,key,mat)

def ring(z0,z1,r0,r1,key,segments=12,smooth=False):
    verts=[CENTER+RIGHT*(math.cos(a)*r)+BACK*(math.sin(a)*r)+UP*z for z,r in [(z0,r0),(z1,r1)] for a in [(i+.5)*2*math.pi/segments for i in range(segments)]]
    faces=[];uvs=[]
    for i in range(segments):
        faces.append((i,(i+1)%segments,(i+1)%segments+segments,i+segments))
        # Broad plaster panels; stone and shingle tiles span a pair of facets.
        repeat=6 if key in ['storage_22','storage_00'] else 3
        u0=(i%repeat)/repeat;u1=u0+1/repeat;uvs.append([(u0,0),(u1,0),(u1,1),(u0,1)])
    add('Tower',verts,faces,key,0,uvs,smooth)

# Visible base lands at grade with the existing -3.128043 AE Z and 1.1 scale.
ring(27.2,29.8,19.5,20.0,'storage_22')
ring(29.8,40.5,20.0,18.4,'storage_22')
ring(40.5,42.0,18.4,17.7,'storage_23')
ring(41.6,84.5,17.7,13.0,'plaster',smooth=True)
ring(84.0,88.0,13.5,14.0,'storage_11')
ring(88.0,91.7,14.0,14.0,'storage_11')
ring(91.7,93.1,16.5,16.5,'storage_11')
ring(93.1,102.0,16.5,9.0,'storage_00')
ring(102.0,106.0,9.0,.1,'storage_00')
# Small framed slit on the visible front. The dark recess is painted timber.
front=CENTER-BACK*16.2+UP*60
box('Tower',front,(RIGHT,BACK,UP),(3.8,.6,11.0),'dark_timber')
for side in [-1,1]:box('Tower',front+RIGHT*(side*2.45)-BACK*.45,(RIGHT,BACK,UP),(1.2,1.3,11.0),'storage_23',0)
for z in [-6,6]:box('Tower',front+UP*z-BACK*.55,(RIGHT,BACK,UP),(6.8,1.7,2.2),'storage_23',0)
# Fixed axle passes through the cap; the moving iron hub is in front of it.
box('Tower',HUB+BACK*5,(RIGHT,BACK,UP),(4.8,13,4.8),'dark_timber')

def cylinder(label,center,radius,depth,key,mat=1,sides=12):
    verts=[Vector(center)+BACK*d+radius*(RIGHT*math.cos(i*2*math.pi/sides)+UP*math.sin(i*2*math.pi/sides)) for d in [-depth/2,depth/2] for i in range(sides)]
    verts += [Vector(center)-BACK*depth/2,Vector(center)+BACK*depth/2]
    faces=[];uvs=[]
    for i in range(sides):
        n=(i+1)%sides;faces += [(i,n,n+sides,i+sides),(2*sides,n,i),(2*sides+1,i+sides,n+sides)]
        uvs += [[(0,0),(1,0),(1,1),(0,1)],[(.5,.5),(.5+.45*math.cos(n*2*math.pi/sides),.5+.45*math.sin(n*2*math.pi/sides)),(.5+.45*math.cos(i*2*math.pi/sides),.5+.45*math.sin(i*2*math.pi/sides))],[(.5,.5),(0,0),(1,0)]]
    add(label,verts,faces,key,mat,uvs)

SAIL_WIDTH_FACTOR=1.35
for blade in range(4):
    angle=math.radians(22.5+blade*90);along=RIGHT*math.sin(angle)+UP*math.cos(angle);across=RIGHT*math.cos(angle)-UP*math.sin(angle)
    # Broad, visibly separate ladder rails with six stout cross-rungs.
    for side in [-1,1]:
        box('Sails',HUB+along*27+across*(side*4.5*SAIL_WIDTH_FACTOR),(across,along,BACK),(1.65,43,1.65),'timber')
    for radius in [8,15.8,23.6,31.4,39.2,47]:
        box('Sails',HUB+along*radius,(across,along,BACK),(10.5*SAIL_WIDTH_FACTOR,1.55,1.8),'timber')
    # Cream cloth wraps the outer frame; shallow billow is geometry, not paint.
    verts=[]
    for rad in [29.8,38.4,47.8]:
        for across_value in [-4.3,0,4.3]:
            bow=1.2 if across_value==0 and rad==38.4 else .25
            verts.append(HUB+along*rad+across*(across_value*SAIL_WIDTH_FACTOR)-BACK*(1.25+bow))
    faces=[(0,1,4,3),(1,2,5,4),(3,4,7,6),(4,5,8,7)]
    uvs=[[(0,0),(.5,0),(.5,.5),(0,.5)],[(.5,0),(1,0),(1,.5),(.5,.5)],[(0,.5),(.5,.5),(.5,1),(0,1)],[(.5,.5),(1,.5),(1,1),(.5,1)]]
    # Closed thin cloth avoids coincident front/back faces self-occluding in AO.
    verts += [v+BACK*.3 for v in verts]
    back=[tuple(i+9 for i in reversed(f)) for f in faces]
    border=[0,1,2,5,8,7,6,3];edges=[(border[i],border[(i+1)%8],border[(i+1)%8]+9,border[i]+9) for i in range(8)]
    add('Sails',verts,faces+back+edges,'ivory',1,uvs+[list(reversed(u)) for u in uvs]+[[(0,0),(1,0),(1,.02),(0,.02)]]*8)
    for rad in [30.3,47.2]:
        for side in [-1,1]:box('Sails',HUB+along*rad+across*(side*4.5*SAIL_WIDTH_FACTOR)-BACK*.3,(across,along,BACK),(2.05,.8,2.65),'rope')
cylinder('Sails',HUB-BACK*2.6,5.5,2.6,'iron')
cylinder('Sails',HUB-BACK*4.2,3.5,1.4,'timber',sides=8)
cylinder('Sails',HUB-BACK*5.0,1.25,.6,'dark_timber',sides=8)
sys.path.insert(0,str(Path(__file__).parent))
from windmill_sail_shape import taper_sails, INNER_WIDTH
parts['Sails']['v']=taper_sails(parts['Sails']['v'],SAIL_WIDTH_FACTOR)

def material(name,prop_material):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links
    bs=n.get('Principled BSDF');bs.inputs['Roughness'].default_value=.8
    uv=n.new('ShaderNodeUVMap');uv.uv_map='UV1';tex={}
    for channel in ['B','N','G','M']:
        path=(ART/'Textures/CSC_Props/Current/textures'/f'CSC_Props_Shared_01_{channel}.png') if prop_material else OUT/'staged-textures'/('CSC_Atlas_B_BAKERS.png' if channel=='B' else f'CSC_Atlas_{channel}.png')
        node=n.new('ShaderNodeTexImage');node.name=channel;node.image=bpy.data.images.load(str(path),check_existing=True)
        if channel!='B':node.image.colorspace_settings.name='Non-Color'
        l.new(uv.outputs[0],node.inputs[0]);tex[channel]=node
    l.new(tex['B'].outputs['Color'],bs.inputs['Base Color'])
    normal=n.new('ShaderNodeNormalMap');normal.uv_map='UV1';l.new(tex['N'].outputs['Color'],normal.inputs['Color']);l.new(normal.outputs[0],bs.inputs['Normal'])
    inv=n.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;l.new(tex['G'].outputs[0],inv.inputs[1]);l.new(inv.outputs[0],bs.inputs['Roughness']);l.new(tex['M'].outputs[0],bs.inputs['Metallic'])
    return mat
mats=[material(MATS[0],False),material(MATS[1],True)]
arm=bpy.data.armatures.new(NAME+'_Skeleton');rig=bpy.data.objects.new(NAME,arm);scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
root=arm.edit_bones.new('Root');root.head=(0,0,0);root.tail=(0,3,0)
rotor=arm.edit_bones.new('Sails');rotor.head=HUB;rotor.tail=HUB-BACK*5;rotor.parent=root
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
objects=[]
for label,p in parts.items():
    mesh=bpy.data.meshes.new(NAME+'_'+label);mesh.from_pydata(p['v'],[],p['f']);mesh.update()
    ob=bpy.data.objects.new(mesh.name,mesh);scene.collection.objects.link(ob)
    if label=='Sails':ob['sail_width_factor']=SAIL_WIDTH_FACTOR
    if label=='Sails':ob['sail_inner_width_fraction']=INNER_WIDTH
    ob['role']='building_geometry';ob['export_role']='building_geometry';ob['source_asset_id']=NAME;ob['atlas_layout']='storage-tower-v3'
    for mat in mats:mesh.materials.append(mat)
    uv=mesh.uv_layers.new(name='UV1')
    for f,coords,mat_index,smooth in zip(mesh.polygons,p['uv'],p['mat'],p['smooth']):
        f.material_index=mat_index;f.use_smooth=smooth
        for li,xy in zip(f.loop_indices,coords):uv.data[li].uv=xy
    # Native topology groups and GEO groups must have the same material indices.
    if label=='Sails':mesh.materials.pop(index=0)
    mesh.uv_layers.new(name='UV2');uv3=mesh.uv_layers.new(name='UV3')
    for loop in uv3.data:loop.uv=(.999,.999)
    vg=ob.vertex_groups.new(name='Sails' if label=='Sails' else 'Root');vg.add(list(range(len(mesh.vertices))),1,'REPLACE')
    modifier=ob.modifiers.new('Windmill skeleton','ARMATURE');modifier.object=rig;ob.parent=rig
    objects.append(ob)
# One unique AO layout for the new geometry. Shared quarter AO is already full.
bpy.ops.object.select_all(action='DESELECT')
for ob in objects:ob.select_set(True);ob.data.uv_layers.active_index=1
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.012,area_weight=.5);bpy.ops.object.mode_set(mode='OBJECT')
ao=bpy.data.images.new(NAME+'_AO',width=512,height=512,alpha=False);ao.generated_color=(1,1,1,1);ao.colorspace_settings.name='Non-Color'
scene.render.engine='CYCLES';scene.cycles.samples=64;scene.render.bake.margin=4;scene.render.bake.use_clear=False;scene.world=bpy.data.worlds.new('World');scene.world.light_settings.distance=9
for mat in mats:
    node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=ao;node.name='AO bake target';mat.node_tree.nodes.active=node
for ob in objects:
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    for other in objects:other.hide_render=other!=ob
    bpy.ops.object.bake(type='AO')
for ob in objects:ob.hide_render=False;ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True
ao_path=OUT/'staged-textures'/(NAME+'_AO.png');ao.filepath_raw=str(ao_path);ao.file_format='PNG';ao.save()
for mat in mats:
    n=mat.node_tree.nodes;l=mat.node_tree.links;uv=n.new('ShaderNodeUVMap');uv.uv_map='UV2';node=n.get('AO bake target');l.new(uv.outputs[0],node.inputs[0])
    mult=n.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=.6;l.new(n.get('B').outputs[0],mult.inputs[1]);l.new(node.outputs[0],mult.inputs[2]);l.new(mult.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
bone=rig.pose.bones['Sails'];bone.rotation_mode='XYZ'
for frame,angle in [(1,0),(301,2*math.pi)]:bone.rotation_euler[1]=angle;bone.keyframe_insert(data_path='rotation_euler',frame=frame)
action=rig.animation_data.action;action.name=NAME+'_Turn'
for layer in action.layers:
    for strip in layer.strips:
        for bag in strip.channelbags:
            for fc in bag.fcurves:
                for k in fc.keyframe_points:k.interpolation='LINEAR'
scene.frame_set(1)
review=bpy.data.scenes.new('Review');review.collection.children.link(scene.collection.children[0]) if scene.collection.children else None
for ob in [rig,*objects]:
    if ob.name not in review.objects:review.collection.objects.link(ob)
scene['vertex_budget_advisory']=2000
for sc in [scene,review]:
    sc.world=bpy.data.worlds.new(sc.name+' World');sc.world.use_nodes=True
    bg=sc.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.7,.8,1,1);bg.inputs['Strength'].default_value=.65
    sc.render.engine='CYCLES';sc.view_settings.view_transform='AgX' if sc==scene else 'Standard';sc.view_settings.exposure=.35 if sc==scene else -.1;sc.view_settings.gamma=1
light=bpy.data.lights.new('Review_Key','SUN');light.energy=3.2;light.color=(1,.92,.8);light.angle=math.radians(6);light.use_shadow=True
lamp=bpy.data.objects.new('Review_Key',light);review.collection.objects.link(lamp);lamp.rotation_euler=(math.radians(35),math.radians(-20),math.radians(-30))
target=OUT/'new-tower'/f'{NAME}.blend';target.parent.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
for ob in objects:ob.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.wm.save_as_mainfile(filepath=str(target))
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
geo=OUT/'staged/Geometries'/f'{NAME}.cn6';io_export_cn6_b4.do_export(str(geo),True,True)
sys.path.insert(0,str(Path.home()/'.codex/skills/civ6-art/scripts'))
from civ6_animation import core
anim=OUT/'staged/Animations'/f'{NAME}_Turn.fgx';anim.parent.mkdir(parents=True,exist_ok=True)
report=core.export_animation(str(anim),rig,r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6',1,301,overwrite=True)
(OUT/'tower-animation-export.json').write_text(json.dumps(report,indent=2))
print('TOWER_AUTHORED',sum(len(o.data.vertices) for o in objects),'vertices; animation',report,flush=True)
