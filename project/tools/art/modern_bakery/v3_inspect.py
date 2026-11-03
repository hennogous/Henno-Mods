"""Read user-edited source and historical dimensions, without saving either."""
import bpy,json,sys,math,hashlib,shutil
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[4];ART=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028'
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
for p in (O,O/'sources',O/'textures',O/'bakes',O/'review',O/'models'):p.mkdir(parents=True,exist_ok=True)
source=ART/'BAKERS/Bakery/modern/revision-02-concept-c/CSC_BAKERS_Bakery_Modern_2_Review.blend'
shutil.copy2(source,O/'sources/User_Edited_Bakery_2.blend')
shutil.copytree(source.parent/'textures',O/'textures',dirs_exist_ok=True)
out={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
def bounds(vs):return [[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
for label,path in [('modern',source),('historical',ART/'Level 2/CSC_Level_2.blend')]:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();out[label]=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH':continue
  vs=[ob.matrix_world@v.co for v in ob.data.vertices]
  row={'name':ob.name,'module':ob.get('module'),'bounds':bounds(vs),'location':list(ob.location),'rotation':list(ob.rotation_euler),'scale':list(ob.scale),'vertices':len(vs),'polys':len(ob.data.polygons)}
  if label=='historical':
   parent=list(range(len(vs)))
   def find(x):
    while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
    return x
   for e in ob.data.edges:
    a,b=e.vertices;parent[find(a)]=find(b)
   groups={}
   for i,v in enumerate(vs):groups.setdefault(find(i),[]).append(i)
   row['components']=[{'vertices':len(ids),'bounds':bounds([vs[i] for i in ids]),'indices':ids} for ids in groups.values()]
   row['z_levels']=sorted({round(v.z,2) for v in vs})
  out[label].append(row)
(O/'source-inspection.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='historical'}),flush=True)
