import bpy,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs
D=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Bakery/modern/revision-03-height-interiors'
O=Path.home()/'Desktop/Codex/modern-bakery-ae-20261028';O.mkdir(exist_ok=True)
def snapshot(p):
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 out={}
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type!='MESH':continue
  data={'vertices':[list(v.co) for v in ob.data.vertices],'faces':[list(f.vertices) for f in ob.data.polygons],'uv':[[list(d.uv) for d in uv.data] for uv in ob.data.uv_layers]}
  out[ob.name]={'module':ob.get('module'),'source_asset_id':ob.get('source_asset_id'),'transform':[list(r) for r in ob.matrix_world],'geometry_hash':hashlib.sha256(json.dumps(data).encode()).hexdigest(),'vertices':len(ob.data.vertices),'materials':[m.name for m in ob.data.materials]}
 return out
p=D/'CSC_BAKERS_Bakery_Modern_2_Review.blend'
a=snapshot(p.with_suffix('.blend1'));b=snapshot(p)
report={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changed':{k:{'old':a.get(k),'new':b.get(k)} for k in a.keys()|b.keys() if a.get(k)!=b.get(k)},'objects':b}
(O/'user-edits.json').write_text(json.dumps(report,indent=2))
print('USER_EDIT_DIFF',json.dumps(report['changed']),flush=True)
