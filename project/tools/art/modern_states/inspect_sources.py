import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix,Vector
A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-l1-states-20261028';O.mkdir(exist_ok=True)
paths={'base':A/'Level 1/modern/revision-04-painted-kit/CSC_Level_1_S_Modern.blend','silo':A/'BAKERS/Wind Mill/modern/revision-10-painted-kit/CSC_BAKERS_Mill_Silo_Modern.blend','water':A/'BAKERS/Water Mill/modern/revision-02-painted-kit/CSC_BAKERS_Water_Mill_Modern.blend','old_base':A/'Level 1/CSC_Level_1_S_CON+PIL.blend'}
F=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
for tag,path in paths.items():
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);s=bpy.data.scenes.get('Export') or bpy.context.scene;bpy.context.window.scene=s;bpy.context.view_layer.update();rows=[]
 for o in s.objects:
  if o.type=='ARMATURE':print('RIG',tag,o.name,[b.name for b in o.data.bones])
  if o.type!='MESH':continue
  vs=[o.matrix_world@v.co for v in o.data.vertices];ps=[F.inverted()@v for v in vs]
  row={'name':o.name,'vertices':len(vs),'faces':len(o.data.polygons),'local':[[round(f(v[i] for v in ps),3) for i in range(3)] for f in (min,max)],'world':[[round(f(v[i] for v in vs),3) for i in range(3)] for f in (min,max)],'materials':[m.name for m in o.data.materials],'props':dict(o.items()),'matrix':[list(r) for r in o.matrix_world]}
  rows.append(row)
  print(tag,o.name,'V',len(vs),'local',row['local'],'materials',row['materials'], 'groups',[(g.name) for g in o.vertex_groups])
 (O/(tag+'-inspection.json')).write_text(json.dumps(rows,indent=2,default=str))
 print('SCENES',tag,[s.name for s in bpy.data.scenes])
