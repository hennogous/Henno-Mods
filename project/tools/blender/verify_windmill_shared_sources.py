"""Verify installed masters against Henno's saved UV edits and scaffold source."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3];ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill/tower'
NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL'
sys.path.insert(0,str(ROOT/'project/tools/blender'));import csc_scene_validation as validator
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    result={}
    for ob in bpy.data.scenes['Export'].objects if 'Export' in bpy.data.scenes else bpy.context.scene.objects:
        if ob.type!='MESH':continue
        m=ob.data;result[ob.name]=dict(vertices=[tuple(v.co) for v in m.vertices],faces=[sorted(f.vertices) for f in m.polygons],matrix=[tuple(r) for r in ob.matrix_world],uv={l.name:[sorted((m.loops[i].vertex_index,*l.data[i].uv) for i in f.loop_indices) for f in m.polygons] for l in m.uv_layers},weights=[[(g.group,g.weight) for g in v.groups] for v in m.vertices])
    return result
results=[]
for name in (NAME,RUIN):
    old=snapshot(OUT/'before'/(name+'.blend'));new=snapshot(SOURCE/(name+'.blend'))
    for key,a in old.items():
        b=new[key]
        for field in ('vertices','faces','matrix','weights'):assert a[field]==b[field],(key,field)
        for uv in ('UV1','UV3'):assert a['uv'][uv]==b['uv'][uv],(key,uv)
    report=validator.validate_current_scene();assert report['error_count']==0 and report['warning_count']==0,report
    report['source_sha256']=hashlib.sha256((SOURCE/(name+'.blend')).read_bytes()).hexdigest()
    (OUT/(name+'-installed-validation.json')).write_text(json.dumps(report,indent=2));results.append(dict(asset=name,surface_uvs_geometry_weights_preserved=True,errors=0,warnings=0))
native=snapshot(ART/'Level 1/CSC_Level_1_S_CON+PIL.blend')['Scaffolding'];current=snapshot(SOURCE/(RUIN+'.blend'))[RUIN+'_Scaffolding']
assert native['uv']==current['uv'] and native['faces']==current['faces']
center=Vector(((2.6851577758789062+102.86904907226562)/2,(-227.5590057373047-150.65550231933594)/2,0));destination=Vector((36.99117,-24.16936192431123,0))
error=max(((Vector(a)-center)*.7+destination-Vector(b)).length for a,b in zip(native['vertices'],current['vertices']));assert error<1e-5,error
results.append(dict(scaffold_source_exact_uvs_and_topology=True,uniform_transform_max_error=error))
(OUT/'installed-source-parity.json').write_text(json.dumps(results,indent=2));print('FINAL_SOURCE_PARITY',results,flush=True)
