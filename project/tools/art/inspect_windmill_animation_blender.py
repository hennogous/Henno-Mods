"""Read the saved windmill rig without changing its source."""
import bpy, json
from pathlib import Path
p=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/CSC_BAKERS_Wind_Mill.blend'
bpy.ops.wm.open_mainfile(filepath=str(p), load_ui=False, use_scripts=False)
if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
print('WINDMILL_INSPECTION',json.dumps(dict(
 scenes=[dict(name=s.name, frame=s.frame_current, props=dict(s.items())) for s in bpy.data.scenes],
 rigs=[dict(name=o.name, props=dict(o.items()), matrix=[list(r) for r in o.matrix_world],
 bones=[dict(name=b.name,parent=b.parent.name if b.parent else None) for b in o.data.bones],
 action=o.animation_data.action.name if o.animation_data and o.animation_data.action else None) for o in bpy.data.objects if o.type=='ARMATURE'],
 meshes=[dict(name=o.name, vertices=len(o.data.vertices), faces=len(o.data.polygons), materials=[m.name for m in o.data.materials], props=dict(o.items())) for o in bpy.data.objects if o.type=='MESH']
),default=str))
