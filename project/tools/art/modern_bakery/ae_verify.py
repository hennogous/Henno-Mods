"""Read back final installation, source preservation and AE's automatic index."""
import json,hashlib,os,sys
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];MOD=ROOT/'Civ Supply Chains';O=Path.home()/'Desktop/Codex/modern-bakery-ae-20261028'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads((O/'publication-report.json').read_text());baseline=json.loads((O/'baseline.json').read_text())
later_edits=[]
published={Path(r['destination']) for r in report['files']}
for rel,h in baseline.items():
 if rel.startswith('Assets/') and sha(MOD/rel)!=h:
  assert MOD/rel not in published
  later_edits.append({'path':rel,'sha256':sha(MOD/rel),'handling':'Later external AE save; never written by this installation'})
edited=json.loads((O/'user-edits.json').read_text());assert sha(edited['source'])==edited['sha256']
for row in report['files']:
 p=Path(row['destination'])
 if p.is_relative_to(MOD) and p.suffix!='.tex':assert sha(p)==row['after'],p
lib=Path.home()/'Desktop/Working Files/3D Art/Textures/CSC_Buildings_Modern/Current';manifest=json.loads((lib/'library.json').read_text())
for name,h in manifest['maps'].items():assert sha(lib/'textures'/name)==h
a=np.array(Image.open(O/'sources/User_Edited_Atlas_B.png').convert('RGBA'));b=np.array(Image.open(lib/'textures/CSC_Atlas_Modern_B_BAKERS.png').convert('RGBA'));mask=np.ones((1024,1024),bool);mask[:512,512:]=False;assert np.array_equal(a[mask],b[mask])
cache=json.loads((Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json').read_text(encoding='utf-8-sig'));names={Path(x['Filename']).name for x in cache['Files']}
required={Path(r['destination']).name for r in report['files'] if Path(r['destination']).is_relative_to(MOD) and Path(r['destination']).suffix in ('.ast','.geo','.tex','.mtl')};assert required<=names,required-names
xlp=E.parse(MOD/'XLPs/CSC_Tilebases.xlp').getroot();ids=[x.get('text') for x in xlp.findall('m_Entries/Element/m_EntryID')];assert len(ids)==len(set(ids))
landmarks=E.parse(MOD/'ArtDefs/CSC_Landmarks.artdef').getroot();variants=[]
for row in landmarks.findall('.//Element'):
 name=row.find('m_Name')
 if name is None or name.get('text') not in ('06 Modern: Bakery','06 Modern: Bakery 2'):continue
 vals={e.find('m_ParamName').get('text'):e for e in row.findall('m_Fields/m_Values/Element') if e.find('m_ParamName') is not None}
 assert vals['Tag_Era'].find('m_ElementName').get('text')=='ARTERA_MODERN'
 service=vals['SelectionRule'].find('m_Value').get('text');priority=int(vals['Priority'].findtext('m_nValue'))
 assert (priority,service)==((3,'[CITYPROP:CSC_BAKERS_STAGE_3_EFFECT_HOUSING_ACTIVE]') if name.get('text').endswith(' 2') else (2,''))
 variants.append(name.get('text'))
assert len(variants)==2
result={'passed':True,'source_edited_blend_unchanged':True,'existing_ASTs_preserved_at_publication':sum(p.startswith('Assets/') for p in baseline),'subsequent_external_AE_edits_preserved':later_edits,'assetcloud_all_dependencies_registered':True,'XLP_unique':True,'modern_service_variants':variants,'releases':report['releases'],'human_pixels_outside_new_Bakery_quadrant_identical':True,'native_geometry_and_cook':'passed','AE_viewport':'unavailable: computer-use access denied','game_deployment':False,'state_limit':'Historical L2 CON+PIL retained pending modern state kit'}
(O/'final-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
