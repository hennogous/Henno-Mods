import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix,Vector
A=Path.home()/'Desktop/Working Files/3D Art'
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
paths={'base':A/'Level 1/modern/revision-03-finished-shelter/CSC_Level_1_S_Modern.blend','historical':A/'Level 1/CSC_Level_1_S.blend','water':A/'BAKERS/Water Mill/modern/revision-01/CSC_BAKERS_Water_Mill_Modern.blend'}
F=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
for tag,path in paths.items():
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 s=bpy.data.scenes.get('Export') or bpy.context.scene;bpy.context.window.scene=s;bpy.context.view_layer.update();rows=[]
 for o in s.objects:
  if o.type!='MESH':continue
  vs=[o.matrix_world@v.co for v in o.data.vertices];local=[F.inverted()@v for v in vs]
  rows.append({'name':o.name,'vertices':len(vs),'faces':len(o.data.polygons),'world':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'local':[[min(v[i] for v in local) for i in range(3)],[max(v[i] for v in local) for i in range(3)]],'materials':[m.name for m in o.data.materials],'props':dict(o.items()),'matrix':[list(r) for r in o.matrix_world]})
  if tag=='historical' or 'Foundation' in o.name:
   rows[-1]['points_local']=[list(v) for v in local]
   rows[-1]['polygons']=[list(p.vertices) for p in o.data.polygons]
 (out/(tag+'.json')).write_text(json.dumps(rows,indent=2,default=str));print(tag,len(rows))
