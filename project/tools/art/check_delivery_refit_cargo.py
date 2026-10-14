"""Check candidate cargo sizes over the entire visible lift, swivel and slide."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');OUT=BASE/'delivery-refit-20261009'
bpy.ops.wm.open_mainfile(filepath=str(BASE/'delivery-01/CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
building=bpy.data.objects['CSC_Storage_L_Bldg']
bale=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH' and 'Textile_Bale' in o.name)
controller=bale.parent;original=controller.matrix_basis.copy()
def surface(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 pts=[e.matrix_world@v.co for v in m.vertices];faces=[list(p.vertices) for p in m.polygons]
 e.to_mesh_clear();return pts,BVHTree.FromPolygons(pts,faces)
s.frame_set(1261);_,wall=surface(building)
inv=Matrix(json.loads((OUT/'source-refit-check.json').read_text())['new_building_transform']).inverted()
rows=[]
for scale in (1.,.95,.9,.85,.8,.75,.7,.675):
 controller.matrix_basis=original@Matrix.Scale(scale,4);hits=[];crossings=[]
 for f in range(841,1322):
  s.frame_set(f);pts,tree=surface(bale)
  overlap=wall.overlap(tree)
  if overlap:hits.append({'frame':f,'triangle_intersections':len(overlap)})
  local=[inv@p for p in pts]
  if min(p.x for p in local)<-35.5837364<max(p.x for p in local):
   crossings.append({'frame':f,'side_clearance':min(min(p.y for p in local)+14.900691,20.683046-max(p.y for p in local))*.81,
                     'top_clearance':(77.691162-max(p.z for p in local))*.81})
 s.frame_set(1261);pts,_=surface(bale)
 minimum_side=min((r['side_clearance'] for r in crossings),default=999)
 rows.append({'scale':scale,'collisions':hits,'opening_crossings':crossings,'minimum_side_clearance':minimum_side,
              'landing_world_bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]})
 if not hits and minimum_side>=.5:break
controller.matrix_basis=original
result={'selected_scale':next((r['scale'] for r in rows if not r['collisions'] and r['minimum_side_clearance']>=.5),None),'candidates':rows,
 'scope':'Every frame (481 poses) from lift start to visible slide end; full storage shell, with at least 0.5 model-unit side clearance.'}
assert result['selected_scale'] is not None,'No tested cargo scale clears the shell'
(OUT/'cargo-fit-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
