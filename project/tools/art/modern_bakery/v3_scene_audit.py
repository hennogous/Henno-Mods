import bpy,json
from pathlib import Path
p=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Bakery/modern/revision-02-concept-c/CSC_BAKERS_Bakery_Modern_2_Review.blend'
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
export=set(bpy.data.scenes['Export'].objects);out=[]
for o in bpy.data.scenes['Review'].objects:
 if o.type=='MESH' and o not in export:out.append({'name':o.name,'module':o.get('module'),'vertices':len(o.data.vertices),'render_hidden':o.hide_render,'viewport_hidden':o.hide_get(),'collections':[c.name for c in o.users_collection]})
print('REVIEW_ONLY',json.dumps(out),flush=True)
