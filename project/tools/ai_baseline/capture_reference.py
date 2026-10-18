"""Read the loaded gameplay database to pin baseline unlocks and AI entries."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    source=Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite"
    db=sqlite3.connect(source.as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    queries={
      'buildings':"SELECT BuildingType,PrereqTech,PrereqCivic,PrereqDistrict,Cost,Maintenance FROM Buildings WHERE BuildingType LIKE 'BUILDING_CSC_%'",
      'building_prereqs':"SELECT * FROM BuildingPrereqs WHERE Building LIKE 'BUILDING_CSC_%'",
      'districts':"SELECT * FROM Districts WHERE DistrictType LIKE 'DISTRICT_CSC_%'",
      'ai_items':"SELECT * FROM AiFavoredItems WHERE Item LIKE '%CSC%' OR ListType LIKE '%CSC%'",
      'native_csc_adjacencies':"SELECT * FROM District_Adjacencies WHERE DistrictType LIKE 'DISTRICT_CSC_%' OR YieldChangeId LIKE '%CSC%'",
      'resource_tags':"SELECT * FROM TypeTags WHERE Tag LIKE 'CLASS_CSC_%_BASE' OR Tag LIKE 'CLASS_CSC_%_SPEC'",
      'material_config':"SELECT * FROM CSC_QuarterMaterialAdjacencyConfig",
      'pseudo_yields':"SELECT * FROM PseudoYields",
      'default_yield_bias':"SELECT * FROM AiFavoredItems WHERE ListType='DefaultYieldBias'",
      'rh_virtual_yields':"SELECT Type FROM Types WHERE Type LIKE 'YIELD_RH_%'",
    }
    result={'database':str(source),'database_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    for name,query in queries.items():result[name]=[dict(row) for row in db.execute(query)]
    db.close();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Pinned baseline gameplay reference:',a.output)
    print('CSC AI preferences:',len(result['ai_items']),'native CSC adjacencies:',len(result['native_csc_adjacencies']))

if __name__=='__main__':main()
