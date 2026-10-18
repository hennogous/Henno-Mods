"""Archived marker experiment: validate explicitly supplied SQL in a memory copy."""
import argparse,json,sqlite3,zlib
from pathlib import Path
from validate_tuning import inventory
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--loaded',action='store_true')
p.add_argument('--sql',type=Path,required=True,help='Archived marker SQL; current CSC source no longer implements markers')
a=p.parse_args()
path=Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite"
source=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True);db=sqlite3.connect(':memory:');source.backup(db);source.close()
db.create_function('Make_Hash',1,lambda v:zlib.crc32(v.encode()))
sql=a.sql.read_text()
if not a.loaded:db.executescript(sql)
assert not db.execute("SELECT * FROM Modifiers WHERE ModifierId LIKE 'MOD_CSC_AI_MATERIAL_%'").fetchall()
markers=db.execute('SELECT ResourceType,FeatureType FROM CSC_AI_MaterialMarkers').fetchall();assert markers
edges=db.execute("SELECT a.DistrictType,y.AdjacentFeature,y.YieldChange FROM District_Adjacencies a JOIN Adjacency_YieldChanges y ON y.ID=a.YieldChangeId WHERE y.ID LIKE 'CSC_AI_MATERIAL_%'").fetchall();assert edges
assert all(v in (4,12) for _,_,v in edges)
assert all(db.execute('SELECT 1 FROM Features WHERE FeatureType=? AND Removable=1 AND Settlement=1 AND Appeal=0 AND MovementChange=0 AND DefenseModifier=0 AND NaturalWonder=0',(f,)).fetchone() for _,f in markers)
assert not db.execute("SELECT 1 FROM Feature_YieldChanges WHERE FeatureType LIKE 'FEATURE_CSC_AI_RESOURCE_%'").fetchone()
assert not db.execute('SELECT 1 FROM CSC_AI_MaterialMarkers m JOIN Resources r ON r.ResourceType=m.ResourceType WHERE r.PrereqTech IS NOT NULL OR r.PrereqCivic IS NOT NULL').fetchone()
once=inventory(db);db.executescript(sql);assert inventory(db)==once
assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()==(3.0,)
result={'status':'passed','loaded':a.loaded,'markers':len(markers),'material_edges':len(edges),'idempotent':True,'old_material_modifiers':0}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
