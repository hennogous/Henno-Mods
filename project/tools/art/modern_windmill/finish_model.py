"""Apply generated painting, bake geometry AO, render, and decode static export groups."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'project/tools/blender/scene_export'))
import decode_blend as decoder
bpy.ops.wm.open_mainfile(filepath=str(OUT/(ASSET+'.blend')))
scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene
mat=bpy.data.materials[ASSET];nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
base=nodes.get('B');base.image=bpy.data.images.load(str(OUT/'textures'/f'{ASSET}_B.png'));base.interpolation='Linear'
uv1=next(n for n in nodes if n.type=='UVMAP');uv1.uv_map='UV1'
uv2=nodes.new('ShaderNodeUVMap');uv2.uv_map='UV2'
for ch in ('N','G','M','E'):
    n=nodes.new('ShaderNodeTexImage');n.name=n.label=ch;n.image=bpy.data.images.load(str(OUT/'textures'/f'{ASSET}_{ch}.png'))
    n.image.colorspace_settings.name='sRGB' if ch=='E' else 'Non-Color';links.new(uv1.outputs['UV'],n.inputs['Vector'])
# Bake without normals/old AO affecting it.
ao=bpy.data.images.new(ASSET+'_AO',width=1024,height=1024,alpha=False);ao.colorspace_settings.name='Non-Color'
aon=nodes.new('ShaderNodeTexImage');aon.name=aon.label='AO';aon.image=ao;nodes.active=aon
links.new(uv2.outputs['UV'],aon.inputs['Vector'])
bpy.ops.object.select_all(action='DESELECT');meshes=[o for o in scene.objects if o.type=='MESH']
for ob in meshes:ob.select_set(True);ob.data.uv_layers.active_index=1
bpy.context.view_layer.objects.active=meshes[0];scene.cycles.samples=32;scene.render.bake.margin=6
bpy.ops.object.bake(type='AO')
ao.filepath_raw=str(OUT/'textures'/f'{ASSET}_AO.png');ao.file_format='PNG';ao.save()
for ob in meshes:ob.data.uv_layers.active_index=0;ob.select_set(False)
mix=nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.45
links.new(base.outputs['Color'],mix.inputs[1]);links.new(aon.outputs['Color'],mix.inputs[2]);links.new(mix.outputs[0],bs.inputs['Base Color'])
normal=nodes.new('ShaderNodeNormalMap');normal.uv_map='UV1';normal.inputs['Strength'].default_value=.6
links.new(nodes['N'].outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bs.inputs['Normal'])
inv=nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1
links.new(nodes['G'].outputs['Color'],inv.inputs[1]);links.new(inv.outputs[0],bs.inputs['Roughness']);links.new(nodes['M'].outputs['Color'],bs.inputs['Metallic'])
for im in bpy.data.images:
    if im.filepath:im.filepath=bpy.path.relpath(im.filepath,start=str(OUT))
review=bpy.data.scenes['Review'];bpy.context.window.scene=review
floor_mesh=bpy.data.meshes.new('Review_Ground');floor_mesh.from_pydata([(-500,-600,-.1),(500,-600,-.1),(500,400,-.1),(-500,400,-.1)],[],[(0,1,2,3)])
floor=bpy.data.objects.new('REVIEW_Ground',floor_mesh);review.collection.objects.link(floor);floor['review_only']=True
fm=bpy.data.materials.new('REVIEW_Ground');fm.diffuse_color=(.40,.36,.25,1);floor.data.materials.append(fm)
cam=review.camera;target=Vector((30,-176,53));rot=Matrix.Rotation(math.radians(-25),4,'Z')
cam.location=target+rot.to_3x3()@Vector((200,-330,260));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=180
review.render.film_transparent=False;review.cycles.samples=48
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')))
for suffix,offset in [('front',Vector((200,-330,260))),('rear',Vector((-240,300,220))),('top',Vector((1,-1,500)))]:
    cam.location=target+rot.to_3x3()@offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    review.render.filepath=str(OUT/f'03_textured_{suffix}.png');bpy.ops.render.render(write_still=True)
cam.location=target+rot.to_3x3()@Vector((200,-330,260));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')))
bpy.context.window.scene=scene
decoded=[decoder.decode_mesh(o,o.matrix_world) for o in meshes]
parts=[]
for role,name in [('building_geometry','Building'),('fixed_geometry','Stock')]:
    parts.append(decoder.merge_meshes(ASSET+'_'+name,[m for m in decoded if m['role']==role]))
model={'asset_id':ASSET,'kind':'building','meshes':parts}
(OUT/'model.json').write_text(json.dumps(model))
print('EXPORT_COUNTS',[(m['name'],len(m['vertices']),len(m['triangles'])) for m in parts])
prov=json.loads((OUT/'texture_provenance.json').read_text());prov['AO']='Blender Cycles geometry bake, unique non-overlapping UV2, no shader normal connected during bake';(OUT/'texture_provenance.json').write_text(json.dumps(prov,indent=2))
