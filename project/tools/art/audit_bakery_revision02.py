"""Verify user-requested geometry boundaries directly in final saved Blender sources."""
import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import SOURCE,OUT,IDS,V
def mesh_record(path):
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 return {o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons]) for o in bpy.data.scenes['Export'].objects if o.type=='MESH'}
old=mesh_record(SOURCE.parent/'revision-01-prop-kit/CSC_BAKERS_Dough_Set.blend');new=mesh_record(SOURCE/'CSC_BAKERS_Dough_Set.blend')
assert not any('Peel' in name or 'Spade' in name for name in new)
for n in ['Mixing_Bowl','Flour_Dusting']:assert old[n]==new[n]
ratios={}
for name in ['Dough0','Dough1','Dough2']:
 a=old[name]['vertices'];b=new[name]['vertices'];ratios[name]=[(max(v[i] for v in b)-min(v[i] for v in b))/(max(v[i] for v in a)-min(v[i] for v in a)) for i in range(3)];assert all(abs(v-1.4)<1e-5 for v in ratios[name])
cards={}
for ident in IDS[2:6]:
 meshes=mesh_record(SOURCE/(ident+'.blend'));assert not any('Loaf' in n for n in meshes)
 fills={n:m for n,m in meshes.items() if 'Bread_Fill' in n};assert len(fills)==(2 if ident.endswith('Cart') else 1)
 for n,m in fills.items():assert len(m['faces'])==1;assert max(v[2] for v in m['vertices'])-min(v[2] for v in m['vertices'])<1e-6
 cards[ident]=list(fills)
result=dict(dough_xyz_size_ratios=ratios,bowl_unchanged=True,flour_card_unchanged=True,bread_individual_loaf_meshes=0,flat_single_face_bread_fills=cards,peel_separate_source=(SOURCE/'CSC_BAKERS_Peel.blend').is_file(),no_peel_inside_dough_set=True)
(OUT/'user-revision-source-audit.json').write_text(json.dumps(result,indent=2));print('USER REVISION SOURCE AUDIT PASSED')
