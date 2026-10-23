"""Stage editable masters with the same UV1 translations as native exports."""
import bpy,json,sys,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/art'))
from windmill_tower_migrate import region_at
OUT=Path(sys.argv[sys.argv.index('--')+1])
ART=Path.home()/'Desktop/Working Files/3D Art'
regions=json.loads((OUT/'atlas-migration.json').read_text())['regions']
report=[]
items=json.loads((OUT/'source-uv.json').read_text())+[
    {'path':str(ART/'Storage/Storage_L/CSC_Storage_L_Crane.blend')},
    {'path':str(ART/'Storage/Storage_L/Delivery/CSC_TAILORS_Storage_Delivery.blend')}]
for item in items:
    path=Path(item['path'])
    if path in (ART/'Props/CSC_Storage_LeanTo_CON+PIL.blend',ART/'Storage/Storage_S/CSC_Storage_S_CON.blend'):continue # Retired standalone or archive-bound layouts.
    relative=path.relative_to(ART);backup=OUT/'before-sources'/relative;backup.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(path,backup)
    bpy.ops.wm.open_mainfile(filepath=str(path))
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    count=0
    for mesh in bpy.data.meshes:
        if not mesh.uv_layers:continue
        uv=mesh.uv_layers[0]
        for f in mesh.polygons:
            mat=mesh.materials[f.material_index] if f.material_index<len(mesh.materials) else None
            if not mat or not mat.name.startswith('CSC_'):continue
            # Only the shared quarter atlas; prop atlas UVs are a separate layout.
            if mat.use_nodes and not any(n.type=='TEX_IMAGE' and n.image and 'CSC_Atlas_B_' in n.image.name for n in mat.node_tree.nodes):continue
            for li in f.loop_indices:
                u,v=uv.data[li].uv;r=region_at(regions,u*1024,(1-v)*1024)
                if r:
                    uv.data[li].uv=(u+r['delta'][0]/1024,v-r['delta'][1]/1024);count+=1
    if not count:
        print('SOURCE_UNAFFECTED',path,flush=True);continue
    # Resolve relative images before staging elsewhere. Load the new paint but keep
    # canonical source paths for the final installed masters.
    for im in bpy.data.images:
        if im.source!='FILE':continue
        absolute=Path(bpy.path.abspath(im.filepath))
        candidate=OUT/'staged-textures'/(absolute.stem+'.png')
        if candidate.exists():
            if im.packed_file:im.unpack(method='REMOVE')
            im.filepath=str(candidate);im.reload();im.filepath=str(ART/'Textures'/absolute.name)
        else:im.filepath=str(absolute)
    bpy.context.scene['storage_atlas_layout']='storage-tower-v3'
    target=OUT/'staged-sources'/relative;target.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=False)
    report.append({'source':str(path),'staged':str(target),'before_sha256':hashlib.sha256(backup.read_bytes()).hexdigest(),'uv1_loops_moved':count})
    print('SOURCE_MIGRATED',path.name,count,flush=True)
(OUT/'source-migration.json').write_text(json.dumps(report,indent=2))
