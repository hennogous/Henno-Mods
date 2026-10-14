"""Apply and verify the colour-only UV edit in both editable sources."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\Fashion-dress-mustard-20261013')
NAMES=['CSC_TAILORS_Fashion_House_Fitting','CSC_TAILORS_Fashion_House']
def target(o):return o.type=='MESH' and any(s in o.name for s in ['Front_Ivory_Gown_Bell','Ivory_Rounded_Sleeve'])
def snapshot():
    result={}
    for o in bpy.data.objects:
        d=dict(matrix=[list(r) for r in o.matrix_world],type=o.type)
        if o.type=='MESH':
            d.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],materials=[m.name if m else None for m in o.data.materials],uv={u.name:[list(v.uv) for v in u.data] for u in o.data.uv_layers})
        result[o.name]=d
    return result
report={}
for name in NAMES:
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'before-source'/(name+'.blend')),load_ui=False,use_scripts=False)
    before=snapshot();changed=[];seen=set()
    for o in bpy.data.objects:
        if not target(o) or o.data.as_pointer() in seen:continue
        seen.add(o.data.as_pointer());gown='Gown_Bell' in o.name
        for p in o.data.uv_layers[0].data:
            p.uv.x+=-.375 if gown else .75;p.uv.y+=-.125 if gown else .125
        changed.append(o.name)
    assert len(changed)==3,changed
    for im in bpy.data.images:
        local=OUT/'textures'/Path(bpy.path.abspath(im.filepath)).name
        if local.is_file():
            im.filepath=str(local);im.reload()
            if im.packed_file:im.pack()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')),relative_remap=True)
    for im in bpy.data.images:
        if (OUT/'textures'/Path(bpy.path.abspath(im.filepath)).name).is_file():im.filepath='//textures/'+Path(bpy.path.abspath(im.filepath)).name
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    bpy.ops.wm.open_mainfile(filepath=str(OUT/(name+'.blend')),load_ui=False,use_scripts=False)
    after=snapshot();assert before.keys()==after.keys()
    for n,a in after.items():
        b=before[n]
        if target(bpy.data.objects[n]):
            key=next(iter(a['uv']));gown='Gown_Bell' in n
            for old,new in zip(b['uv'][key],a['uv'][key]):
                assert abs(new[0]-old[0]-(-.375 if gown else .75))<1e-6
                assert abs(new[1]-old[1]-(-.125 if gown else .125))<1e-6
            a['uv'][key]=b['uv'][key]
        assert a==b,n
    report[name]=dict(changed=changed,all_geometry_transforms_other_UVs_and_materials_preserved=True,sha256=hashlib.sha256((OUT/(name+'.blend')).read_bytes()).hexdigest())
    print('SCENES',[(s.name,len(s.objects),s.camera.name if s.camera else None) for s in bpy.data.scenes])
    if name==NAMES[1]:
        scene=bpy.data.scenes.get('Review') or bpy.context.scene;bpy.context.window.scene=scene
        print('CAMERA',list(scene.camera.location),list(scene.camera.rotation_euler),scene.camera.data.ortho_scale)
        subjects=[o for o in scene.objects if o.type=='MESH' and (target(o) or 'Screen' in o.name or 'Privacy' in o.name)]
        print('SUBJECTS',[(o.name,list(o.matrix_world.translation)) for o in subjects])
        points=[o.matrix_world@Vector(c) for o in subjects for c in o.bound_box]
        if points:
            center=sum(points,Vector())/len(points);center.z=(min(p.z for p in points)+max(p.z for p in points))/2
            camera=scene.camera
            direction=camera.rotation_euler.to_quaternion()@Vector((0,0,1));camera.location=center+direction*150
            camera.data.type='ORTHO';camera.data.ortho_scale=max(max(p.x for p in points)-min(p.x for p in points),max(p.y for p in points)-min(p.y for p in points),max(p.z for p in points)-min(p.z for p in points))*1.55
            scene.render.resolution_x=1100;scene.render.resolution_y=900;scene.render.resolution_percentage=100
            scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'mustard-dress-preview.png')
            scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.device='CPU'
            bpy.ops.render.render(write_still=True)
(OUT/'source-validation.json').write_text(json.dumps(report,indent=2));print('SAVED SOURCE PARITY PASSED')
