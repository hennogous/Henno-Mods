import bpy, os, json, importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
TEX=OUT/'Textures'
NAME='CSC_BLACKSMITH_Workshop_v5'
sc=bpy.data.scenes['CSC_BLACKSMITH_Workshop_v4']
bpy.context.window.scene=sc
sc.name=NAME
obj=next(o for o in sc.objects if o.type=='MESH' and o.name.startswith('CSC_BLACKSMITH'))
arm=obj.parent
obj.name=NAME+'_Bldg';arm.name=NAME
mat=obj.data.materials[0];mat.name='CSC_BLACKSMITH_Workshop_Atlas_v5'
for n in mat.node_tree.nodes:
    if n.type=='TEX_IMAGE':
        suffix='AO' if 'AO' in n.name else n.name.rsplit('_',1)[-1]
        im=bpy.data.images.load(str(TEX/f'CSC_BLACKSMITH_Workshop_{suffix}.png'),check_existing=False)
        im.colorspace_settings.name='sRGB' if suffix in ['B','E'] else 'Non-Color'
        n.image=im
        im.filepath=f'//Textures/CSC_BLACKSMITH_Workshop_{suffix}.png'
    if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=1.0
# Keep the same studio and exposure for a fair texture comparison.
sc.cycles.samples=96
sc.render.filepath=str(OUT/'blacksmith-render-v5.png')
for other in list(bpy.data.scenes):
    if other!=sc:bpy.data.scenes.remove(other)
bpy.data.orphans_purge(do_recursive=True)
spec=importlib.util.spec_from_file_location('cn6_export',ROOT/'project/tools/scripts/io_export_cn6_b4.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True);arm.select_set(True);bpy.context.view_layer.objects.active=obj
ex.do_export(str(OUT/f'{NAME}.cn6'),True,True)
lines=(OUT/f'{NAME}.cn6').read_text().splitlines()
vertices=lines.index('triangles')-lines.index('vertices')-1
triangles=lines.index('end')-lines.index('triangles')-1
assert vertices==1491 and triangles==781
assert [u.name for u in obj.data.uv_layers]==['UV1','UV2','UV3']
assert len(obj.data.materials)==1
(OUT/'budget.json').write_text(json.dumps(dict(cn6_vertices=vertices,cn6_triangles=triangles,materials=1,atlas_size=1024,geometry='Unchanged from v4',ao='Unchanged geometry and UV2: reused v4 Cycles bake',normal='Explicit structural height; OpenGL for Blender preview; strength 1.0'),indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'{NAME}.blend'),relative_remap=False)
bpy.ops.render.render(write_still=True)
print('V5 COMPLETE',vertices,triangles,flush=True)
