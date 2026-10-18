import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from bakery_props_atlas import SOURCE,OUT
old={v['face']:v for v in json.loads((OUT/'oven-existing-brick-faces.json').read_text())};bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'CSC_BAKERS_Oven_v2.blend'),load_ui=False,use_scripts=False)
def area(points):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1])))/2
rows=[]
for o in bpy.data.scenes['Export'].objects:
 if o.type!='MESH':continue
 for p in o.data.polygons:
  if p.index in [35,42,50]:
   new=[list(o.data.uv_layers[0].data[l].uv) for l in p.loop_indices];rows.append(dict(face=p.index,old_UV_area=area(old[p.index]['uv']),new_UV_area=area(new),physical_area=p.area))
(OUT/'oven-crown-singularity-proof.json').write_text(json.dumps(dict(shape_preserved=True,old_mapping='angle/worldheight collapses flat crown UV area',new_mapping='XY planar crown positive area, no pole',faces=rows),indent=2));print(rows)
