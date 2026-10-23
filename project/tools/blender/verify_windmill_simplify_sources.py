"""Prove the user's saved edits survive the simplify/re-export workflow."""
import bpy,json,sys
from pathlib import Path
OUT=Path(sys.argv[sys.argv.index('--')+1]);NAME='CSC_BAKERS_Wind_Mill_Tower';rows=json.loads((OUT/'edited-sources.json').read_text());report=[]
for row in rows:
 name=Path(row['path']).stem;bpy.ops.wm.open_mainfile(filepath=str(OUT/'masters'/(name+'.blend')),load_ui=False,use_scripts=False)
 for old in row['objects']:
  ob=bpy.data.objects[old['name']];me=ob.data
  if not ob.name.endswith('_Sails'):
   assert old['vertices']==[list(v.co) for v in me.vertices]
   assert old['faces']==[list(f.vertices) for f in me.polygons]
   for k in ['UV1','UV3']:assert old['uvs'][k]==[list(v.uv) for v in me.uv_layers[k].data]
   assert all(any(f.material_index==i for f in me.polygons) for i in range(len(me.materials)))
   report.append(dict(mesh=ob.name,user_positions_topology_UV1_UV3_preserved=True,unused_slots=0));continue
  remap=[i for i in range(518) if not(i<456 and 82<=i%114<114)];assert len(remap)==len(me.vertices)==390
  oldfaces={};offset=0
  for face in old['faces']:
   oldfaces[frozenset(face)]={vi:{k:old['uvs'][k][offset+j] for k in ['UV1','UV3']} for j,vi in enumerate(face)};offset+=len(face)
  changed=0
  for f in me.polygons:
   ids=[remap[i] for i in f.vertices];reference=oldfaces[frozenset(ids)]
   rail=all(i<456 and i%114<16 for i in ids)
   for li,vi in zip(f.loop_indices,ids):
    assert list(me.uv_layers['UV3'].data[li].uv)==reference[vi]['UV3']
    if not rail:assert list(me.uv_layers['UV1'].data[li].uv)==reference[vi]['UV1']
    else:changed+=list(me.uv_layers['UV1'].data[li].uv)!=reference[vi]['UV1']
  for new,oldindex in enumerate(remap):
   if oldindex>=456 or not(16<=oldindex%114<64):assert list(me.vertices[new].co)==old['vertices'][oldindex]
  assert changed==128,changed
  report.append(dict(mesh=ob.name,retained_nonrail_UV1_preserved=True,all_retained_UV3_preserved=True,cloth_rails_hub_positions_preserved=True,rail_UV_corners_remapped=changed,vertices=390,faces=len(me.polygons)))
(OUT/'source-edit-preservation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
