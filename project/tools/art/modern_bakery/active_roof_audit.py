import bpy,json
from pathlib import Path
ART=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-bakery-active-roof-20261028';rows={}
for name in ('CSC_Level_2_Modern','CSC_Level_2_Modern_Workshop'):
 bpy.ops.wm.open_mainfile(filepath=str(ART/'Level 2/modern/revision-06-ae'/(name+'.blend')),load_ui=False,use_scripts=False);obs=[]
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type!='MESH':continue
  slots={}
  for p in ob.data.polygons:
   uv=[ob.data.uv_layers[0].data[k].uv for k in p.loop_indices];u=sum(x.x for x in uv)/len(uv);v=sum(x.y for x in uv)/len(uv);slot=int(u*8)-4+4*int((1-v)*8);slots[slot]=slots.get(slot,0)+1
  obs.append({'name':ob.name,'slots':slots})
 rows[name]=obs
(O/'surface-audit.json').write_text(json.dumps(rows,indent=2))
