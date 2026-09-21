"""Read SDK package manifests and rank material/stock/workshop prop candidates."""
import json,re,sys
from pathlib import Path
import xml.etree.ElementTree as ET
SDK=Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets")
ROOT=Path(__file__).resolve().parents[3]
OUTPUT=Path(sys.argv[1]).resolve()
LIB=Path('C:/Users/Shadow/Desktop/Working Files/3D Art/Props/CSC_Prop_Library')
TERMS={
 'Timber and wood':r'wood|lumber|timber|plank|logs?(?:_|$)|logpile|board|firewood|sawmill',
 'Stone and mineral stock':r'stone|marble|brick|block|rock|ore(?:_|$)|coal|ingot|quarry|metal|iron|copper|goldpile',
 'Bulk goods and textiles':r'pile|stack|heap|bundle|bale|sack|bag(?:_|$)|grain|hay(?:_|$)|wheat|cotton|cloth|fabric|leather|hide(?:_|$)|spice|dye|silk|rope|roll(?:_|$)|wool',
 'Containers and storage':r'crate|barrel|basket|bucket|pot(?:_|$)|jar(?:_|$)|vase|amphora|tub(?:_|$)|bin(?:_|$)|box(?:_|$)|chest|cask|keg|bottle',
 'Handling and work props':r'cart|wheelbarrow|wagon|rack|shelf|shelves|bench|table|anvil|forge|kiln|furnace|hoist|crane|saw(?:_|$)|tools?|grind|press(?:_|$)|cauldron|trough',
}
def text(e,path):
 n=e.find(path);return n.get('text',n.text or '') if n is not None else ''
def parse(p):return ET.fromstring(re.sub(r'(<\/?)([\w.]+):+',r'\1\2.',p.read_text(encoding='utf-8-sig')))
def main():
 OUTPUT.mkdir(parents=True,exist_ok=True)
 owned={r['asset_id'].lower() for r in json.loads((LIB/'catalogue.json').read_text(encoding='utf-8'))['assets']}
 files={};manifests={}
 for key,pack in [('civ6','Base game'),('expansion1','Rise and Fall'),('expansion2','Gathering Storm')]:
  manifest=key+'-asset-deps.json';d=json.loads((SDK/manifest).read_text())
  for f in d['Files']:
   rel=f['Filename'];p=SDK/rel
   if p.suffix.lower()=='.ast':files.setdefault(rel,(pack,manifest,d['Dependencies'].get(rel,[])))
 rows=[];errors=[]
 for rel,(pack,manifest,deps) in files.items():
  p=SDK/rel
  if not p.exists():continue
  aid=p.stem
  evidence=aid+' '+' '.join(Path(dep).stem for dep in deps if Path(dep).suffix.lower()=='.geo')
  if not any(re.search(pattern,evidence,re.I) for pattern in TERMS.values()):continue
  if re.search(r'^(LEAD|UNIT|UI|VFX|FX|TERR|FEATURE)_',aid,re.I):continue
  try:
   ast=parse(p); models=[text(m,'m_GeoName') for m in ast.findall('m_GeometrySet/m_ModelInstances/Element')]
   cls=text(ast,'m_ClassName')
   namehits={k:re.findall(v,aid,re.I) for k,v in TERMS.items()};namehits={k:v for k,v in namehits.items() if v}
   # Geometry labels expose small reusable components with less descriptive AST names.
   geohits={k:re.findall(v,' '.join(models),re.I) for k,v in TERMS.items()};geohits={k:v for k,v in geohits.items() if v}
   if not namehits and not geohits: continue
   score=10*len(namehits)+3*len(geohits)
   if re.search(r'pile|stack|plank|barrel|crate|wood|timber|sack|bale|basket|brick|bucket|block|ingot|rope|cart',aid,re.I): score+=20
   excluded=[]
   if aid.lower() in owned:excluded.append('already in library')
   if re.search(r'(^|_)(PIL|CON|Pillaged|Construction|FX|VFX|Decal|FOW|SV)(_|$)',aid,re.I):excluded.append('state/effect variant')
   if cls not in ['TileBase','Clutter']:excluded.append('non-prop class '+cls)
   if re.search(r'^(LEAD|UNIT|UI|VFX|FX|TERR|FEATURE)_',aid,re.I):excluded.append('character/terrain/UI family')
   if re.search(r'Stonehenge|RockBand|Rock_Band|Rockefeller|RockHewn|Boarding|Broadway',aid,re.I):excluded.append('semantic false positive')
   rows.append(dict(asset_id=aid,source_pack=pack,source_ast=str(p),provenance=dict(manifest=manifest,path=rel),asset_class=cls,geometry_ids=models,name_hits=namehits,geometry_hits=geohits,score=score,excluded=excluded))
  except Exception as exc:errors.append(dict(path=rel,error=str(exc)))
 rows.sort(key=lambda r:(bool(r['excluded']),-r['score'],r['asset_id']))
 report=dict(package_ast_count=len(files),unique_package_ast_paths=len({str(SDK/rel).lower() for rel in files}),unique_package_asset_ids=len({Path(rel).stem.lower() for rel in files}),matched_count=len(rows),unique_matched_ids=len({r['asset_id'].lower() for r in rows}),parse_errors=errors,candidates=rows)
 (OUTPUT/'discovery.json').write_text(json.dumps(report,indent=2))
 print('PACKAGE ASTs',len(files),'MATCHED',len(rows),'UNEXCLUDED',sum(not r['excluded'] for r in rows),'ERRORS',len(errors),flush=True)
 for r in rows:
  if not r['excluded']:print(f"{r['score']:2} {r['asset_id']} | {r['source_pack']} | {r['asset_class']}")
if __name__=='__main__':main()
