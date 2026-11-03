"""Save and export the previously authored basket with portable shared materials."""
import sys,json,math
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/art'));sys.path.insert(0,str(ROOT/'project/tools/blender'))
OUT=Path('C:/Users/Shadow/Desktop/Codex/Tailors-newer-basket-20261026')
ART=Path('C:/Users/Shadow/Desktop/Working Files/3D Art')
NAME='CSC_TAILORS_Basket'
SOURCE=ART/'TAILORS/Textile Workshop/revision-11-pantry-interiors-shared-ao'/f'{NAME}.blend'
DEST=ART/'Props/Tailors'/f'{NAME}.blend'
RELEASE='2026-10-26_Shared_01_r046'
def write(path,data):path.write_text(json.dumps(data,indent=2),encoding='utf-8')
from csc_scene_validation import validate_current_scene
from ae_asset_render_blender import Builder
from migrate_legacy_prop_atlas_blender import frame

def build():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    export=next(s for s in bpy.data.scenes if any(o.type=='MESH' for o in s.objects))
    bpy.context.window.scene=export
    for s in list(bpy.data.scenes):
        if s!=export:bpy.data.scenes.remove(s)
    objects=[o for o in export.objects if o.type in ['MESH','ARMATURE']]
    assert len(objects)==2
    for o in list(bpy.data.objects):
        if o not in objects:bpy.data.objects.remove(o,do_unlink=True)
    materials=json.loads((OUT/'materials.json').read_text());builder=Builder(dict(output=str(OUT/'masters'),materials=materials,warnings=[]),'sv')
    export.name='Export'
    if 'placement_authority' in export:del export['placement_authority']
    export['asset_id']=NAME;export['atlas_release']=RELEASE;export['authoring_source']=str(SOURCE)
    ob=next(o for o in objects if o.type=='MESH');rig=next(o for o in objects if o.type=='ARMATURE')
    assert len(ob.data.vertices)==169
    mat=builder.material(next(iter(materials)),3);mat.name='CSC_ALL_Props_01';mat['ae_group']='CSC_ALL_Props_01';mat['ae_material']='CSC_ALL_Props_01'
    ob.data.materials.clear();ob.data.materials.append(mat);ob['export_role']='building_geometry';ob['source_asset_id']=NAME
    for poly in ob.data.polygons:poly.material_index=0
    for image in builder.images.values():
        if image.packed_file:image.unpack(method='REMOVE')
        image.filepath='//textures/'+Path(image.filepath).name
    for m in list(bpy.data.materials):
        if m!=mat:bpy.data.materials.remove(m)
    for im in list(bpy.data.images):
        if not im.users:bpy.data.images.remove(im)
    review=bpy.data.scenes.new('Review')
    for o in objects:review.collection.objects.link(o)
    world=bpy.data.worlds.new('Review World');world.use_nodes=True
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.7,.8,1,1);bg.inputs['Strength'].default_value=.65
    for sc,view,exp in [(export,'AgX',.35),(review,'Standard',-.1)]:
        sc.world=world;sc.render.engine='CYCLES';sc.view_settings.view_transform=view;sc.view_settings.exposure=exp;sc.view_settings.gamma=1
    light=bpy.data.objects.new('Review_Key',bpy.data.lights.new('Review_Key','SUN'));review.collection.objects.link(light)
    light.data.energy=3.2;light.data.color=(1,.92,.8);light.data.angle=math.radians(6);light.data.use_shadow=True;light.rotation_euler=tuple(map(math.radians,(25,-30,-25)))
    cam=bpy.data.objects.new('Review_Camera',bpy.data.cameras.new('Review_Camera'));review.collection.objects.link(cam);cam.data.type='ORTHO';review.camera=cam;frame(review)
    bpy.context.window.scene=export;bpy.context.preferences.filepaths.save_version=0
    path=OUT/'masters'/f'{NAME}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
    validate_export(path)
    bpy.context.window.scene=bpy.data.scenes['Review'];bpy.context.scene.render.filepath=str(OUT/'newer-basket.png');bpy.ops.render.render(write_still=True)

def validate_export(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export']
    report=validate_current_scene();write(OUT/('installed-source-validation.json' if path==DEST else 'source-validation.json'),report)
    assert report['error_count']==0,[f for f in report['findings'] if f['severity']=='error']
    sys.path.insert(0,str(Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons'));import io_export_cn6 as cn6
    target=OUT/('installed-export' if path==DEST else 'source-export')/f'{NAME}.cn6';target.parent.mkdir(exist_ok=True)
    cn6.csc_do_export_selected(str(target),[o for o in bpy.context.scene.objects if o.type in ['MESH','ARMATURE']]);assert target.exists()

def verify():validate_export(DEST)
if __name__=='__main__':globals()[sys.argv[sys.argv.index('--')+1]]()
