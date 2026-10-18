"""Verify user-requested geometry boundaries directly in final saved Blender sources."""
import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import SOURCE,OUT,IDS,V
def mesh_record(path):
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 return {o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons]) for o in bpy.data.scenes['Export'].objects if o.type=='MESH'}
unchanged={}
for ident in [IDS[0],IDS[1],IDS[6]]:
 old=mesh_record(SOURCE.parent/'revision-03-prop-kit'/(ident+'.blend'));new=mesh_record(SOURCE/(ident+'.blend'));assert old==new;unchanged[ident]=True
assert not any('Peel' in name or 'Spade' in name for name in mesh_record(SOURCE/'CSC_BAKERS_Dough_Set.blend'))
old_cart=mesh_record(SOURCE.parent/'revision-03-prop-kit/CSC_BAKERS_Bread_Cart.blend');new_cart=mesh_record(SOURCE/'CSC_BAKERS_Bread_Cart.blend')
for n,m in old_cart.items():
 if 'Wicker_Basket' not in n and 'Bread_Fill' not in n:assert new_cart[n]==m
cards={}
for ident in IDS[2:6]:
 meshes=mesh_record(SOURCE/(ident+'.blend'));assert not any('Loaf' in n for n in meshes)
 fills={n:m for n,m in meshes.items() if 'Bread_Fill' in n};assert len(fills)==(2 if ident.endswith('Cart') else 1)
 for n,m in fills.items():
  assert len(m['vertices'])==48 and len(m['faces'])==37
  assert abs(max(v[2] for v in m['vertices'])-min(v[2] for v in m['vertices'])-4.55)<1e-4
 shells={n:m for n,m in meshes.items() if 'Wicker_Basket' in n}
 assert len(shells)==len(fills)
 for n,m in shells.items():
  ring=m['vertices'][39:52];xs=[v[0] for v in ring];ys=[v[1] for v in ring];corners={(round(min(xs),4),round(min(ys),4)),(round(min(xs),4),round(max(ys),4)),(round(max(xs),4),round(min(ys),4)),(round(max(xs),4),round(max(ys),4))};assert corners.issubset({(round(v[0],4),round(v[1],4)) for v in ring})
 cards[ident]=list(fills)
result=dict(square_tray_corners_verified=True,cart_non_basket_geometry_unchanged=True,unchanged_geometry=unchanged,bread_individual_loaf_meshes=0,single_generic_raised_carrier_per_basket=cards,peel_separate_source=(SOURCE/'CSC_BAKERS_Peel.blend').is_file(),no_peel_inside_dough_set=True)
(OUT/'user-revision-source-audit.json').write_text(json.dumps(result,indent=2));print('USER REVISION SOURCE AUDIT PASSED')
