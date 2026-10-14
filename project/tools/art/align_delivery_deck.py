"""Correct only the added deck; preserve donor vertices, UVs, weights and animation."""
import bpy,json,sys,shutil,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_sled_geometry import align_loading_deck
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');DEL=BASE/'delivery-01';OUT=BASE/'delivery-deck-20261010'
OUT.mkdir(exist_ok=True);backup=OUT/'before-deck-alignment';backup.mkdir(exist_ok=True)
names=['CSC_TAILORS_Storage_Delivery.blend','CSC_TAILORS_Delivery_Native_Export.blend','CSC_TEST_TAILORS_Delivery_Master_Model.fgx','CSC_TEST_TAILORS_Delivery_Master_Model.geo','CSC_TEST_TAILORS_Delivery_Master.fgx','CSC_TEST_TAILORS_Delivery_Master.anm','native-check.json']
for name in names:
 if not (backup/name).exists():shutil.copy2(DEL/name,backup/name)
bpy.ops.wm.open_mainfile(filepath=str(backup/'CSC_TAILORS_Storage_Delivery.blend'))
dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh'];ids=list(range(len(dm.data.vertices)-8,len(dm.data.vertices)))
assert all(abs(dm.data.vertices[i].co.z-7)<.0001 or abs(dm.data.vertices[i].co.z-9)<.0001 for i in ids)
before=[tuple(v.co) for v in dm.data.vertices]
report=align_loading_deck(dm,ids)
assert all(tuple(v.co)==before[v.index] for v in dm.data.vertices if v.index not in ids)
report.update(unchanged_original_vertices=len(before)-len(ids),clip_sha256=hashlib.sha256((DEL/'CSC_TEST_TAILORS_Delivery_Master.fgx').read_bytes()).hexdigest(),source_vertex_count=len(before))
bpy.ops.wm.save_as_mainfile(filepath=str(DEL/'CSC_TAILORS_Storage_Delivery.blend'))
(OUT/'deck-repair-check.json').write_text(json.dumps(report,indent=2));print('DECK_ALIGNED',json.dumps(report))
