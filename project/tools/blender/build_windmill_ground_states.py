"""Rebase the current windmill to grade, extend foundations and author its ruin shell."""
import bpy,sys,math,json,copy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=Path(sys.argv[sys.argv.index('--')+1])
NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL';SHIFT=27.2;DEPTH=30
SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/tower'
CENTER=Vector((36.99117,-24.16936192431123,0))
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(NAME+'.blend')),load_ui=False,use_scripts=False)
scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;scene.frame_set(1)
rig=bpy.data.objects[NAME];tower=bpy.data.objects[NAME+'_Tower'];sails=bpy.data.objects[NAME+'_Sails']
assert not scene.get('ground_rebased');assert len(tower.data.vertices)==264

def mesh_data(ob):
    m=ob.data
    return dict(v=[v.co.copy() for v in m.vertices],f=[list(f.vertices) for f in m.polygons],
        uv=[[tuple(m.uv_layers[0].data[i].uv) for i in f.loop_indices] for f in m.polygons],
        mat=[f.material_index for f in m.polygons],smooth=[f.use_smooth for f in m.polygons])

def mesh_from(data,name,materials):
    m=bpy.data.meshes.new(name);m.from_pydata(data['v'],[],data['f']);m.update()
    for mat in materials:m.materials.append(mat)
    uv=m.uv_layers.new(name='UV1')
    for f,coords,mi,smooth in zip(m.polygons,data['uv'],data['mat'],data['smooth']):
        f.material_index=mi;f.use_smooth=smooth
        for i,xy in zip(f.loop_indices,coords):uv.data[i].uv=xy
    m.uv_layers.new(name='UV2');m.uv_layers.new(name='UV3')
    for item in m.uv_layers['UV3'].data:item.uv=(.999,.999)
    return m

def add_face(data,face,uv,material=0,smooth=False):
    data['f'].append(face);data['uv'].append(uv);data['mat'].append(material);data['smooth'].append(smooth)

def weight_all(ob,bone):
    ob.vertex_groups.clear();group=ob.vertex_groups.new(name=bone);group.add(list(range(len(ob.data.vertices))),1,'REPLACE')

original_sails=[v.co.copy() for v in sails.data.vertices]
data=mesh_data(tower)
for v in data['v']:v.z-=SHIFT
for v in sails.data.vertices:v.co.z-=SHIFT
assert max(abs(v.z) for v in data['v'][:12])<1e-5
for p in data['v'][:12]:p.z=0
# Three stone courses continue the original footing without stretching its paint.
last=list(range(12));stone_uv=data['uv'][12:24]
for z in (-10,-20,-DEPTH):
    current=[]
    for v in data['v'][:12]:
        p=v.copy();p.z=z;current.append(len(data['v']));data['v'].append(p)
    for i in range(12):
        j=(i+1)%12;add_face(data,[current[i],current[j],last[j],last[i]],stone_uv[i])
    last=current
rect=stone_uv[0];u0=min(x[0] for x in rect);u1=max(x[0] for x in rect);v0=min(x[1] for x in rect);v1=max(x[1] for x in rect)
def disk_uv(points):return [(u0+(p.x-CENTER.x+20)/40*(u1-u0),v0+(p.y-CENTER.y+20)/40*(v1-v0)) for p in points]
add_face(data,list(reversed(last)),disk_uv([data['v'][i] for i in reversed(last)]))
tower.data=mesh_from(data,tower.data.name+'_Grade',list(tower.data.materials));weight_all(tower,'Root')
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
bone=rig.data.edit_bones['Sails'];bone.head.z-=SHIFT;bone.tail.z-=SHIFT
bpy.ops.object.mode_set(mode='OBJECT');scene.frame_set(1)
scene['ground_rebased']=True;scene['ground_level_z']=0;scene['foundation_bottom_z']=-DEPTH
sails['ground_rebased']=True
assert max((v.co+Vector((0,0,SHIFT))-old).length for v,old in zip(sails.data.vertices,original_sails))<1e-5

def bake_and_save(asset,objects,armature):
    # Fresh unique AO layout for the new geometry; stationary and moving surfaces
    # bake separately so the rotor cannot leave a permanent shadow on the tower.
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:ob.select_set(True);ob.data.uv_layers.active_index=1
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.012,area_weight=.5);bpy.ops.object.mode_set(mode='OBJECT')
    ao=bpy.data.images.new(asset+'_AO_Grade',width=512,height=512,alpha=False);ao.generated_color=(1,1,1,1);ao.colorspace_settings.name='Non-Color'
    mats={m for ob in objects for m in ob.data.materials}
    for mat in mats:
        node=mat.node_tree.nodes.get('AO bake target');node.image=ao;mat.node_tree.nodes.active=node
    scene.render.engine='CYCLES';scene.cycles.samples=64;scene.render.bake.margin=4;scene.render.bake.use_clear=False;scene.world.light_settings.distance=9
    for ob in objects:
        bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
        for other in objects:other.hide_render=other!=ob
        bpy.ops.object.bake(type='AO')
    for ob in objects:ob.hide_render=False;ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True
    ao_path=OUT/'staged-textures'/(asset+'_AO.png');ao_path.parent.mkdir(exist_ok=True);ao.filepath_raw=str(ao_path);ao.file_format='PNG';ao.save()
    ao.filepath_raw=str(SOURCE/ao_path.name)
    for image in bpy.data.images:
        if image.source=='FILE':image.filepath=str(Path(bpy.path.abspath(image.filepath)).resolve())
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [armature,*objects]:ob.select_set(True)
    bpy.context.view_layer.objects.active=armature
    target=OUT/'masters'/(asset+'.blend');target.parent.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=False)
    path=OUT/'staged/Geometries'/(asset+'.cn6');path.parent.mkdir(parents=True,exist_ok=True)
    io_export_cn6_b4.do_export(str(path),True,True)

bake_and_save(NAME,[tower,sails],rig)
sys.path.insert(0,str(Path.home()/'.codex/skills/civ6-art/scripts'));from civ6_animation import core
clip=OUT/'staged/Animations'/(NAME+'_Turn.fgx');clip.parent.mkdir(exist_ok=True)
animation=core.export_animation(str(clip),rig,r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6',1,301,overwrite=True)
(OUT/'animation-export.json').write_text(json.dumps(animation,indent=2));scene.frame_set(1)

# Reuse the foundation, lower shell and window. Replace the cap and sails with a
# substantial broken masonry rim and an inner wall/floor for the CON+PIL shell.
keep=set(range(96))|set(range(216,256))|set(range(264,len(data['v'])))
ruin={k:[] for k in data};mapping={}
for i in sorted(keep):mapping[i]=len(ruin['v']);ruin['v'].append(data['v'][i].copy())
for face,uv,mat,smooth in zip(data['f'],data['uv'],data['mat'],data['smooth']):
    if set(face)<=keep:add_face(ruin,[mapping[i] for i in face],uv,mat,smooth)
heights=[43,47,44,51,48,46,42,45,49,46,44,48]
outer=[];inner=[];floor=[]
for i,h in enumerate(heights):
    idx=mapping[84+i];radial=ruin['v'][idx]-CENTER;radial.z=0;radial.normalize()
    radius=17.7+(13-17.7)*(h-14.4)/(57.3-14.4)
    ruin['v'][idx]=CENTER+radial*radius+Vector((0,0,h));outer.append(idx)
    inner.append(len(ruin['v']));ruin['v'].append(CENTER+radial*(radius-2.2)+Vector((0,0,h-.35)))
    floor.append(len(ruin['v']));ruin['v'].append(CENTER+radial*15.5+Vector((0,0,14.4)))
for i in range(12):
    j=(i+1)%12
    add_face(ruin,[outer[i],outer[j],inner[j],inner[i]],stone_uv[i])
    add_face(ruin,[floor[i],inner[i],inner[j],floor[j]],data['uv'][36+i],0,True)
add_face(ruin,floor,disk_uv([ruin['v'][i] for i in floor]))
# Keep the existing painted timber window material separate from plaster.
ruin_mats=[]
for old in tower.data.materials:
    new=old.copy();new.name=old.name+'_Ruin';ruin_mats.append(new)
for ob in [tower,sails]:bpy.data.objects.remove(ob,do_unlink=True)
rig.animation_data_clear();rig.name=RUIN;rig.data=rig.data.copy();rig.data.name=RUIN+'_Skeleton'
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT');rig.data.edit_bones.remove(rig.data.edit_bones['Sails']);bpy.ops.object.mode_set(mode='OBJECT')
ob=bpy.data.objects.new(RUIN+'_Shell',mesh_from(ruin,RUIN+'_Shell',ruin_mats));scene.collection.objects.link(ob);bpy.data.scenes['Review'].collection.objects.link(ob)
ob.parent=rig;mod=ob.modifiers.new('Tower skeleton','ARMATURE');mod.object=rig;weight_all(ob,'Root')
ob['role']='building_geometry';ob['export_role']='building_geometry';ob['source_asset_id']=RUIN;ob['atlas_layout']='storage-tower-v3'
scene['asset_id']=RUIN;scene['animation_notes']='Static CON+PIL shell; native PROP_Scaffold_A is attached only in Construction in the AST.'
scene.frame_end=1
bake_and_save(RUIN,[ob],rig)
(OUT/'authoring-report.json').write_text(json.dumps(dict(ground_shift=SHIFT,foundation_bottom=-DEPTH,
    intact_above_ground_unchanged=True,ruin_height_range=[min(heights),max(heights)],
    sail_tip_width=11.61,animation_seconds=10,ruin_raw_vertices=len(ruin['v']),
    scaffold_asset='PROP_Scaffold_A',scaffold_uniform_scale=1.45),indent=2))
print('GROUNDED_AND_STATES_AUTHORED',flush=True)
