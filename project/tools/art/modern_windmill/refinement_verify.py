import bpy,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from modular_v9 import ROOT,ART,BASE,SILO,TROLLEY,PALLET,PMAT,dump
O=Path.home()/'Desktop/Codex/modern-kit-refinement-20261027';WATER='CSC_BAKERS_Water_Mill_Modern'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
def read(p):
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
 rows={}
 for o in bpy.context.scene.objects:
  if o.type=='MESH':rows[o.name]={'points':[list(o.matrix_world@v.co) for v in o.data.vertices],'uv':[list(d.uv) for d in o.data.uv_layers[0].data],'polygons':[list(p.vertices) for p in o.data.polygons],'material':o.data.materials[0].name}
 return rows
baseline=json.loads((O/'baseline.json').read_text());sources={Path(p).stem:Path(p) for p in baseline['sources']};results={}
with suspend_csc_repairs():
 for ident in (BASE,WATER,SILO,TROLLEY,PALLET):
  before=read(sources[ident]);after=read(O/'masters'/ident/(ident+'.blend'));report=validate_current_scene();assert report['automated_pass'];dump(O/'masters'/ident/'validation.json',report)
  if ident==BASE:
   expected=set(before)-{'CSC_Fixed_Door_Recess_Floor','CSC_Fixed_Recess_Back'};assert set(after)==expected
   for name in expected-{'CSC_Fixed_House_Foundation'}:assert before[name]['points']==after[name]['points'] and before[name]['polygons']==after[name]['polygons'],name
   base=after
  elif ident==WATER:
   F=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)));W=Matrix.Translation(Vector((-34,20.5,6.15)));err=0
   for name,r in base.items():
    if name=='CSC_Fixed_Front_Window_-21_17':assert name not in after;continue
    assert r['polygons']==after[name]['polygons']
    for a,b in zip(r['points'],after[name]['points']):err=max(err,(W@F.inverted()@Vector(a)-Vector(b)).length)
   assert err<.0001,err;results['water_kit_max_error']=err
   for name,r in before.items():
    if name not in base and name not in ('CSC_Fixed_Door_Recess_Floor','CSC_Fixed_Recess_Back'):assert r['points']==after[name]['points'],name
  else:
   assert set(before)==set(after)
   for name,r in before.items():assert r['points']==after[name]['points'] and r['polygons']==after[name]['polygons']
  results[ident]={'saved_validation':True,'meshes':len(after)}
dump(O/'source-propagation-validation.json',results);print(results)
