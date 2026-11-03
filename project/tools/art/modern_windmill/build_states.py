"""Author matching construction/pillage shell; intact stock is never shown in these states."""
import bpy,sys,json,math,ast
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(sys.argv[sys.argv.index('--')+1]);BASE='CSC_BAKERS_Wind_Mill_Modern';ASSET=BASE+'_CON+PIL'
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'project/tools/blender/scene_export'));import decode_blend as decoder
bpy.ops.wm.open_mainfile(filepath=str(OUT/(BASE+'.blend')))
scene=bpy.data.scenes['Export'];scene['asset_id']=ASSET;bpy.context.window.scene=scene
for ob in list(bpy.data.objects):
    if ob.type=='MESH' and not ob.get('review_only'):bpy.data.objects.remove(ob,do_unlink=True)
rig=bpy.data.objects[BASE];rig.name=ASSET;rig.data.name=ASSET
mat=bpy.data.materials[BASE].copy();mat.name=ASSET
meshes=[];uv_guide=[]
tree=ast.parse((Path(__file__).parent/'build_model.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('tileuv','mesh','box','cylinder','beam')],type_ignores=[]),'<authoring helpers>','exec'))
box('Ruin_Footings',(-19,10,-10),(70,66,28),1)
for i,(x,y,sx,sy,h) in enumerate([(-52,10,4,66,27),(14,10,4,66,34),(-19,41,66,4,25),(-51,-21,6,4,23),(-3,-21,36,4,19),(-44,40,18,4,35),(14,30,4,16,43)]):
    box('Ruin_Wall_'+str(i),(x,y,h/2),(sx,sy,h),1)
cylinder('Silo_Foundation',39,-28,[(-24,21),(13,21)],16,1,11)
vs=[];n=16
for rad,top in [(19.5,False),(19.5,True),(16.5,False),(16.5,True)]:
    for i in range(n):
        theta=math.pi/2+2*math.pi*i/n;z=13 if not top else [33,39,38,25,28,31,24,27,35,45,40,29,30,34,26,32][i]
        vs.append((39+rad*math.cos(theta),-28+rad*math.sin(theta),z))
faces=[];tiles=[]
for i in range(n):
    k=(i+1)%n
    faces += [(i,k,n+k,n+i),(2*n+k,2*n+i,3*n+i,3*n+k),(n+i,n+k,3*n+k,3*n+i)]
    tiles += [12,13,6]
mesh('Ruin_Silo_Wall',vs,faces,tiles)
box('Ruin_Elevator',(44,2,5),(14,13,58),14)
box('Ruin_Intake_Base',(63,-2,-9),(18,21,28),11)
# Scaffold frame is an independent state mesh, visible only during Construction.
for x in (-58,20):
    for y in (-29,49):box('Scaffold_Post_'+str(x)+'_'+str(y),(x,y,23),(3,3,94),10,True)
for z in (28,58):
    for y in (-29,49):beam('Scaffold_Rail_'+str(y)+'_'+str(z),(-58,y,z),(20,y,z),2.7,10,True)
    for x in (-58,20):beam('Scaffold_Rail_'+str(x)+'_'+str(z),(x,-29,z),(x,49,z),2.7,10,True)
frame=Matrix.Translation((30,-172,0))@Matrix.Rotation(math.radians(-25),4,'Z')
bpy.ops.object.select_all(action='DESELECT')
review=bpy.data.scenes['Review']
for ob in meshes:
    ob.data.transform(frame);ob.parent=rig;review.collection.objects.link(ob)
    group=ob.vertex_groups.new(name='Bone');group.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    mod=ob.modifiers.new('Static Bone','ARMATURE');mod.object=rig
    ob.data.uv_layers.new(name='UV2');ob.data.uv_layers.active_index=1;ob.select_set(True)
bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.014,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
for ob in meshes:
    uv=ob.data.uv_layers.new(name='UV3')
    for d in uv.data:d.uv=(.02,.02)
    ob.data.uv_layers.active_index=1
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
normal_link=list(bs.inputs['Normal'].links)
for l in normal_link:links.remove(l)
links.new(nodes['B'].outputs['Color'],bs.inputs['Base Color'])
ao=bpy.data.images.new(ASSET+'_AO',width=1024,height=1024,alpha=False);ao.colorspace_settings.name='Non-Color';nodes['AO'].image=ao;nodes.active=nodes['AO']
scene.cycles.samples=16;scene.render.bake.margin=6;bpy.ops.object.bake(type='AO')
ao.filepath_raw=str(OUT/'textures'/(ASSET+'_AO.png'));ao.file_format='PNG';ao.save()
for ob in meshes:ob.data.uv_layers.active_index=0;ob.select_set(False)
mix=next(n for n in nodes if n.type=='MIX_RGB');links.new(mix.outputs[0],bs.inputs['Base Color'])
for im in bpy.data.images:
    if im.filepath:im.filepath=bpy.path.relpath(bpy.path.abspath(im.filepath),start=str(OUT))
bpy.context.window.scene=review
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')))
for state in ['Construction','Pillaged']:
    for ob in meshes:ob.hide_render=state=='Pillaged' and ob.get('export_role')=='fixed_geometry'
    review.render.filepath=str(OUT/f'04_{state}.png');review.cycles.samples=24;bpy.ops.render.render(write_still=True)
for ob in meshes:ob.hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')))
bpy.context.window.scene=scene
decoded=[decoder.decode_mesh(o,o.matrix_world) for o in meshes]
parts=[decoder.merge_meshes(ASSET+'_'+name,[m for m in decoded if m['role']==role]) for role,name in [('building_geometry','Shell'),('fixed_geometry','Scaffold')]]
(OUT/'state_model.json').write_text(json.dumps({'asset_id':ASSET,'kind':'building','meshes':parts}))
print('STATE_EXPORT_COUNTS',[(m['name'],len(m['vertices']),len(m['triangles'])) for m in parts])
