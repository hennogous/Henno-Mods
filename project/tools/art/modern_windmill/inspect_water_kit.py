import bpy,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector
root=Path.home()/'Desktop/Working Files/3D Art'
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
files={'base':root/'Level 1/modern/revision-02-blank-brick/CSC_Level_1_S_Modern.blend','silo':root/'BAKERS/Wind Mill/modern/revision-09-modular/CSC_BAKERS_Mill_Silo_Modern.blend','water':root/'BAKERS/Water Mill/CSC_BAKERS_Water_Mill.blend'}
for tag,path in files.items():
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    scene=bpy.data.scenes.get('Export') or bpy.context.scene;bpy.context.window.scene=scene
    data=[]
    for o in scene.objects:
        if o.type!='MESH':continue
        inv=frame.inverted() if tag!='water' else Matrix.Identity(4)
        vs=[inv@o.matrix_world@v.co for v in o.data.vertices]
        data.append({'name':o.name,'matrix':[list(r) for r in o.matrix_world],'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'vertices':len(vs),'faces':len(o.data.polygons),'materials':[m.name for m in o.data.materials],'points':[list(v) for v in vs] if tag=='water' or 'Shelter' in o.name else None})
    (out/(tag+'.json')).write_text(json.dumps(data,indent=2))
    print(tag,json.dumps([{k:r[k] for k in ('name','bounds','vertices','faces')} for r in data if tag=='water' and not 'Flour' in r['name'] or tag=='base' and ('Shelter' in r['name'] or 'Foot' in r['name']) or tag=='silo' and 'Intake' in r['name']]))
