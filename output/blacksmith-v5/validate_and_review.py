"""Read-back checks and controlled neutral-material normal-map comparison."""
import bpy, json, hashlib
from pathlib import Path

OUT=Path(__file__).resolve().parent
sc=bpy.context.scene
obj=next(o for o in sc.objects if o.type=='MESH' and o.name.startswith('CSC_BLACKSMITH'))
mat=obj.data.materials[0];ns=mat.node_tree.nodes;ls=mat.node_tree.links
checks={}
for node in ns:
    if node.type=='TEX_IMAGE':
        image=node.image;resolved=Path(bpy.path.abspath(image.filepath))
        assert image.filepath.startswith('//Textures/') and resolved.is_file(),image.filepath
        assert not image.packed_file
        assert list(image.size)==[1024,1024]
        expected='sRGB' if resolved.stem.endswith(('_B','_E')) else 'Non-Color'
        assert image.colorspace_settings.name==expected
        checks[resolved.name]=dict(path=image.filepath,color_space=expected,size=list(image.size))
v4=OUT.parent/'blacksmith-v4/CSC_BLACKSMITH_Workshop_v4.cn6'
v5=OUT/'CSC_BLACKSMITH_Workshop_v5.cn6'
def geometry(p):
    lines=p.read_text().splitlines()
    return lines[lines.index('vertices'):lines.index('end')]
assert geometry(v4)==geometry(v5),'Geometry or UV export unexpectedly changed'
ao='CSC_BLACKSMITH_Workshop_AO.png'
assert (OUT/'Textures'/ao).read_bytes()==(OUT.parent/'blacksmith-v4/Textures'/ao).read_bytes()
(OUT/'validation.json').write_text(json.dumps(dict(images=checks,geometry_and_uvs='CN6 vertex and triangle sections identical to v4',ao='byte-identical v4 geometry bake'),indent=2))

bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED')
for name in ['Base Color','Roughness','Metallic','Emission Color']:
    for link in list(bs.inputs[name].links):ls.remove(link)
bs.inputs['Base Color'].default_value=(.42,.42,.42,1)
bs.inputs['Roughness'].default_value=.55
bs.inputs['Metallic'].default_value=0
bs.inputs['Emission Color'].default_value=(0,0,0,1)
normal=next(n for n in ns if n.type=='NORMAL_MAP')
sc.render.resolution_x=800;sc.render.resolution_y=800
sc.cycles.samples=48
for enabled in [False,True]:
    normal.inputs['Strength'].default_value=1 if enabled else 0
    sc.render.filepath=str(OUT/('relief-on.png' if enabled else 'relief-off.png'))
    bpy.ops.render.render(write_still=True)
print('VALIDATED: external maps, colorspaces, unchanged CN6/UVs and AO. Review renders saved; blend unchanged.')

# Separate clean export handoff from the useful camera/light preview scene.
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_BLACKSMITH_Workshop_v5.blend'))
sc=bpy.context.scene
for ob in list(sc.objects):
    if not ob.name.startswith('CSC_BLACKSMITH_Workshop_v5'):
        bpy.data.objects.remove(ob,do_unlink=True)
assert sorted(o.type for o in sc.objects)==['ARMATURE','MESH']
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CSC_BLACKSMITH_Workshop_v5_export.blend'),relative_remap=False)
