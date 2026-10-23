"""Translate only the sail cloth UV1 islands into their dedicated weathered swatch."""
import bpy,bmesh,json,sys
from pathlib import Path
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill/tower';NAME='CSC_BAKERS_Wind_Mill_Tower'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(NAME+'.blend')),load_ui=False,use_scripts=False)
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.window.scene=bpy.data.scenes['Export'];scene=bpy.context.scene;scene.frame_set(1)
objects=[o for o in scene.objects if o.type=='MESH'];rig=bpy.data.objects[NAME];sails=bpy.data.objects[NAME+'_Sails'];me=sails.data
assert len(me.vertices)==390 and len(me.polygons)==324
def signature(o):return dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(f.vertices) for f in o.data.polygons],uvs={u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers},weights=[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices])
before={o.name:signature(o) for o in objects};loops=[];faces=[]
for f in me.polygons:
    if all(v<328 and 64<=v%82<82 for v in f.vertices):
        faces.append(f.index)
        for i in f.loop_indices:
            uv=me.uv_layers['UV1'].data[i].uv
            assert 4/1024-1e-6<=uv.x<=124/1024+1e-6 and 1-508/1024-1e-6<=uv.y<=1-388/1024+1e-6
            uv.x+=.875;uv.y-=.125;loops.append(i)
assert len(faces)==96,(len(faces),faces)
after={o.name:signature(o) for o in objects}
for name,a in before.items():
    b=after[name]
    for k in ['vertices','faces','weights']:assert a[k]==b[k]
    for k in a['uvs']:
        if name!=sails.name or k!='UV1':assert a['uvs'][k]==b['uvs'][k]
        else:
            for i,(u,v) in enumerate(zip(a['uvs'][k],b['uvs'][k])):
                if i not in loops:assert u==v
for im in bpy.data.images:
    filename=Path(bpy.path.abspath(im.filepath)).name
    if filename in ['CSC_Props_Shared_01_'+k+'.png' for k in 'BNGM']:
        packed=bool(im.packed_file);im.filepath=str(OUT/'atlas-release/textures'/filename);im.reload()
        if packed:im.pack()
        im.filepath=str(ART/'Textures/CSC_Props/Current/textures'/filename)
for s in bpy.data.scenes:s['atlas_release']='2026-10-22_Shared_01_r042'
bpy.ops.object.select_all(action='DESELECT')
for o in [rig,*objects]:o.select_set(True)
bpy.context.view_layer.objects.active=rig;bpy.context.preferences.filepaths.save_version=0
dest=OUT/'masters'/(NAME+'.blend');dest.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=False)
tower=next(o for o in objects if o.name.endswith('_Tower'));tower.data=tower.data.copy();bm=bmesh.new();bm.from_mesh(tower.data);bmesh.ops.split_edges(bm,edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle()>.01]);bm.to_mesh(tower.data);bm.free()
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
cn6=OUT/'staged/Geometries'/(NAME+'.cn6');io_export_cn6_b4.do_export(str(cn6),True,True)
(OUT/'authoring-report.json').write_text(json.dumps(dict(cloth_faces=len(faces),cloth_uv1_corners=len(loops),geometry_weights_uv2_uv3_preserved=True,frame_start=scene.frame_start,frame_end=scene.frame_end,fps=scene.render.fps),indent=2))
assert scene.frame_start==1 and scene.frame_end==241 and scene.render.fps==30
print('WEATHERED_CLOTH_UV1_SAVED',len(faces),len(loops),flush=True)
