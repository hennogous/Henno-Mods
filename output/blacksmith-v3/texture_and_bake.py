import bpy,bmesh,math,os,json,importlib.util
from mathutils import Vector

ROOT='/Users/henno.gous/Play/Henno-Mods'
OUT=ROOT+'/output/blacksmith-v3';TEX=OUT+'/Textures';NAME='CSC_BLACKSMITH_Workshop_v3'
source=bpy.data.scenes['CSC_BLACKSMITH_Workshop_v2']
source_collection=next(c for c in source.collection.children if c.name.startswith('BLACKSMITH |'))
sc=bpy.data.scenes.new(NAME);bpy.context.window.scene=sc
col=bpy.data.collections.new('BLACKSMITH | textured geometry');sc.collection.children.link(col)
studio=bpy.data.collections.new('PREVIEW | textured studio');sc.collection.children.link(studio)

# Rectangles are based on visual inspection of the generated atlas, in top-left
# image coordinates. Generative boundaries differ slightly from the prompt.
rects={'roof':(.012,.008,.488,.492),'stone':(.51,.012,.988,.49),
 'wood':(.012,.51,.488,.985),'plaster':(.51,.51,.988,.672),
 'iron':(.507,.691,.619,.809),'endgrain':(.631,.691,.743,.809),
 'cloth':(.756,.691,.868,.809),'coals':(.882,.691,.989,.809),
 'soot':(.508,.826,.619,.99),'water':(.631,.826,.743,.99),
 'leather':(.757,.826,.868,.99),'steel':(.882,.826,.989,.99)}
def atlas_uv(region,u,v):
    x0,y0,x1,y1=rects[region]
    return (x0+(x1-x0)*u,1-(y0+(y1-y0)*v))
parts=[];region_counts={}
roofline=[(-2.34,2.63),(-1.87,2.94),(-1.39,3.64),(-.88,4.75),(-.42,3.64),(.08,2.96),(.66,2.66)]
arc=[0]
for a,b in zip(roofline,roofline[1:]):arc.append(arc[-1]+math.hypot(b[0]-a[0],b[1]-a[1]))
def roof_distance(x):
    return sum(max(0,min(1,(x-a[0])/(b[0]-a[0])))*math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(roofline,roofline[1:]))

for source_ob in source_collection.objects:
    if source_ob.type!='MESH':continue
    ob=source_ob.copy();ob.data=source_ob.data.copy();col.objects.link(ob);parts.append(ob)
    me=ob.data;me.update()
    old=me.materials[0].name
    region=('roof' if 'clay roof' in old else 'stone' if 'masonry' in old else 'wood' if 'oak' in old else 'plaster' if 'plaster' in old else 'soot' if 'recess' in old else 'iron' if 'forged iron' in old else 'wood' if 'cut timber' in old else 'coals' if 'hot coals' in old else 'cloth' if 'leather sign' in old else 'water')
    bounds=[(min(v.co[k] for v in me.vertices),max(v.co[k] for v in me.vertices)) for k in range(3)]
    longest=max(range(3),key=lambda k:bounds[k][1]-bounds[k][0])
    for poly in me.polygons:
        n=poly.normal;drop=max(range(3),key=lambda k:abs(n[k]));axes=[k for k in range(3) if k!=drop]
        coords=[me.vertices[me.loops[li].vertex_index].co for li in poly.loop_indices]
        lo=[min(p[k] for p in coords) for k in range(3)];hi=[max(p[k] for p in coords) for k in range(3)]
        pr=region
        if region=='wood' and abs(n[longest])>.88:pr='endgrain'
        if ob.name.startswith('60'):pr='endgrain' if abs(n.z)>.88 else 'wood'
        if region=='wood':axes.sort(key=lambda k:hi[k]-lo[k])
        region_counts[pr]=region_counts.get(pr,0)+1
        for li,p in zip(poly.loop_indices,coords):
            if region=='roof' and ob.name.startswith('03'):
                u=(p.y+1.62)/3.20
                d=roof_distance(p.x)
                v=(arc[3]-d)/arc[3] if poly.center.x<-.88 else (d-arc[3])/(arc[-1]-arc[3])
            elif region=='roof':
                u=.08+(p.y-bounds[1][0])/3.2
                v=.08+(p.x-bounds[0][0])/3.0
            elif pr=='wood':
                # Both directions use physical size, with the long axis in V.
                u=.08+(p[axes[0]]-lo[axes[0]])*.22
                v=.025+(p[axes[1]]-lo[axes[1]])*.27
            elif pr=='stone':
                # Align courses by Z on vertical surfaces. The chimney needs a
                # full-height region while small components reuse smaller patches.
                horizontal=0 if abs(n.y)>=abs(n.x) else 1
                if abs(n.z)<.8:
                    u=.06+(p[horizontal]-bounds[horizontal][0])*.40
                    v=.97-(p.z-bounds[2][0])*(.175 if ob.name.startswith('40') else .36)
                else:
                    u=.10+(p.x-bounds[0][0])*.40;v=.15+(p.y-bounds[1][0])*.40
            elif pr=='plaster':
                u=.04+(p[axes[0]]-bounds[axes[0]][0])*.19
                v=.04+(p[axes[1]]-bounds[axes[1]][0])*.18
            else:
                u=.05+.90*(p[axes[0]]-lo[axes[0]])/max(hi[axes[0]]-lo[axes[0]],1e-6)
                v=.05+.90*(p[axes[1]]-lo[axes[1]])/max(hi[axes[1]]-lo[axes[1]],1e-6)
            uv=atlas_uv(pr,max(.012,min(.988,u)),max(.012,min(.988,v)))
            me.uv_layers['UV1'].data[li].uv=uv
            me.uv_layers['UV3'].data[li].uv=uv

bpy.ops.object.select_all(action='DESELECT')
for ob in parts:ob.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();obj=bpy.context.object;obj.name=NAME+'_Bldg'
bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.split_edges(bm,edges=list(bm.edges));bm.to_mesh(obj.data);bm.free()
for v in obj.data.vertices:v.co*=30
me=obj.data;me.update()

# Unwrap the actual, final-scale geometry for a unique AO layout.
me.uv_layers.active=me.uv_layers['UV2'];me.uv_layers['UV2'].active_render=True
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=1.151917,island_margin=.008,area_weight=.5,correct_aspect=True,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT')

mat=bpy.data.materials.new('CSC_BLACKSMITH_Workshop_Atlas');mat.use_nodes=True
ns=mat.node_tree.nodes;ls=mat.node_tree.links;ns.clear()
output=ns.new('ShaderNodeOutputMaterial');output.location=(850,80)
bs=ns.new('ShaderNodeBsdfPrincipled');bs.location=(600,80);ls.new(bs.outputs[0],output.inputs[0])
uv1=ns.new('ShaderNodeUVMap');uv1.uv_map='UV1';uv1.location=(-1000,350)
uv2=ns.new('ShaderNodeUVMap');uv2.uv_map='UV2';uv2.location=(-1000,-300)
uv3=ns.new('ShaderNodeUVMap');uv3.uv_map='UV3';uv3.location=(-1000,-600)
nodes={}
for index,suffix in enumerate(['B','N','G','M','E']):
    im=bpy.data.images.load(TEX+'/CSC_BLACKSMITH_Workshop_'+suffix+'.png',check_existing=False)
    im.colorspace_settings.name='sRGB' if suffix in ['B','E'] else 'Non-Color'
    tex=ns.new('ShaderNodeTexImage');tex.name='External _'+suffix;tex.label='External _'+suffix;tex.image=im;tex.extension='EXTEND';tex.location=(-720,450-index*200)
    ls.new((uv3 if suffix=='E' else uv1).outputs[0],tex.inputs[0]);nodes[suffix]=tex
ao=bpy.data.images.new('CSC_BLACKSMITH_Workshop_AO',width=1024,height=1024,alpha=False)
ao.generated_color=(1,1,1,1);ao.colorspace_settings.name='Non-Color';ao.filepath_raw=TEX+'/CSC_BLACKSMITH_Workshop_AO.png';ao.file_format='PNG'
ao_node=ns.new('ShaderNodeTexImage');ao_node.name='Geometry AO through UV2';ao_node.image=ao;ao_node.location=(-450,120);ls.new(uv2.outputs[0],ao_node.inputs[0])
# Add AO after baking so the active bake image is not a material dependency.
ls.new(nodes['B'].outputs['Color'],bs.inputs['Base Color'])
normal=ns.new('ShaderNodeNormalMap');normal.uv_map='UV1';normal.inputs['Strength'].default_value=.65;normal.location=(150,-150);ls.new(nodes['N'].outputs['Color'],normal.inputs['Color']);ls.new(normal.outputs[0],bs.inputs['Normal'])
invert=ns.new('ShaderNodeMath');invert.operation='SUBTRACT';invert.inputs[0].default_value=1;ls.new(nodes['G'].outputs['Color'],invert.inputs[1]);ls.new(invert.outputs[0],bs.inputs['Roughness'])
ls.new(nodes['M'].outputs['Color'],bs.inputs['Metallic']);ls.new(nodes['E'].outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1.7
me.materials.clear();me.materials.append(mat)
for p in me.polygons:p.material_index=0
armdata=bpy.data.armatures.new('Blacksmith armature');arm=bpy.data.objects.new(NAME,armdata);col.objects.link(arm)
obj.select_set(False);arm.select_set(True);bpy.context.view_layer.objects.active=arm
bpy.ops.object.mode_set(mode='EDIT');bone=armdata.edit_bones.new('Bone');bone.head=(0,0,0);bone.tail=(0,0,30);bpy.ops.object.mode_set(mode='OBJECT')
obj.parent=arm;mod=obj.modifiers.new('Armature','ARMATURE');mod.object=arm;vg=obj.vertex_groups.new(name='Bone');vg.add(list(range(len(me.vertices))),1,'REPLACE')

sc.render.engine='CYCLES';sc.cycles.samples=96;sc.cycles.use_denoising=True
sc.world=source.world.copy();sc.world.light_settings.distance=34
sc.render.bake.margin=5;sc.render.bake.use_clear=True;sc.render.bake.use_selected_to_active=False
ns.active=ao_node
for node in ns:node.select=False
ao_node.select=True
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
print('BAKING geometry AO, 1024px, 96 samples, 34 game-unit ray distance',flush=True)
bpy.ops.object.bake(type='AO');ao.save()
mix=ns.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.8;mix.location=(170,300)
ls.new(nodes['B'].outputs['Color'],mix.inputs[1]);ls.new(ao_node.outputs['Color'],mix.inputs[2]);ls.new(mix.outputs[0],bs.inputs['Base Color'])
me.uv_layers.active=me.uv_layers['UV1'];me.uv_layers['UV1'].active_render=True

# Recreate the studio at final game-unit scale after baking; ground and neighbours
# were absent during the AO bake and therefore cannot contaminate it.
source_studio=next(c for c in source.collection.children if c.name.startswith('PREVIEW |'))
for source_ob in source_studio.objects:
    cp=source_ob.copy();cp.data=source_ob.data.copy();studio.objects.link(cp);cp.location*=30
    if cp.type=='MESH':
        for v in cp.data.vertices:v.co*=30
    elif cp.type=='LIGHT':
        cp.data.energy*=900
        if cp.data.type=='AREA':cp.data.size*=30
        elif cp.data.type=='POINT':cp.data.shadow_soft_size*=30
    elif cp.type=='CAMERA':cp.data.ortho_scale*=30;cp.data.clip_end=30000;sc.camera=cp
sc.render.resolution_x=1200;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.filepath=OUT+'/blacksmith-render-v3.png'
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.30

spec=importlib.util.spec_from_file_location('cn6_export',ROOT+'/project/tools/scripts/io_export_cn6_b4.py');ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);arm.select_set(True);bpy.context.view_layer.objects.active=obj
ex.do_export(OUT+'/'+NAME+'.cn6',True,True)
lines=open(OUT+'/'+NAME+'.cn6').read().splitlines();export_verts=lines.index('triangles')-lines.index('vertices')-1;export_tris=lines.index('end')-lines.index('triangles')-1
assert export_verts<=1500,export_verts
assert len(me.uv_layers)==3
assert all(-.0001<=c<=1.0001 for loop in me.uv_layers['UV2'].data for c in loop.uv)
with open(OUT+'/budget.json','w') as f:json.dump({'cn6_vertices':export_verts,'cn6_triangles':export_tris,'materials':1,'atlas_size':1024,'ao_bake':'Cycles AO; UV2; 96 samples; distance 34 game units; studio excluded','mapped_faces':region_counts},f,indent=2)
for image in [n.image for n in ns if n.type=='TEX_IMAGE']:
    image.filepath=bpy.path.relpath(image.filepath,start=OUT)
sc.render.image_settings.color_mode='RGBA'
bpy.ops.file.pack_all() if False else None
bpy.context.preferences.filepaths.save_version=1
if bpy.data.use_autopack:bpy.ops.file.autopack_toggle()
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.clip_end=30000;area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.region_3d.view_camera_zoom=5;area.spaces.active.shading.type='MATERIAL';area.spaces.active.overlay.show_overlays=False;area.spaces.active.show_region_ui=False
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/'+NAME+'.blend',relative_remap=False)
bpy.ops.render.render(write_still=True)
print('DONE',export_verts,export_tris,flush=True)
