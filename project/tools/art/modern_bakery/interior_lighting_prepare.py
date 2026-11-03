"""Freeze current user-edited sources and extract registered interior paint guides."""
from pathlib import Path
from PIL import Image
import json,hashlib,shutil,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[4];MOD=ROOT/'Civ Supply Chains';ART=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-interior-lighting-20261028'
O.mkdir(exist_ok=True);(O/'sources').mkdir(exist_ok=True);(O/'textures').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (O/'baseline.json').exists(),'Do not overwrite frozen inputs'
baseline={p.relative_to(MOD).as_posix():sha(p) for folder in ('Assets','Geometries','Materials','Textures','ArtDefs','XLPs') for p in (MOD/folder).glob('*') if p.is_file()}
(O/'baseline.json').write_text(json.dumps(baseline,indent=2))
sources={};bindings={}
for p in (MOD/'Materials').glob('CSC_BAKERS*.mtl'):
 r=E.parse(p).getroot();bindings[p.stem]={row.find('m_ParamName').get('text'):row.find('m_ObjectName').get('text') for row in r.findall('m_CookParams/m_Values/Element') if row.find('m_ObjectName') is not None}
for name in ('CSC_Atlas_Modern_B_BAKERS','CSC_Atlas_Modern_B_BAKERS_2','CSC_Atlas_Modern_E','CSC_Atlas_E'):
 p=MOD/'Textures'/(name+'.tex')
 if not p.exists():continue
 r=E.parse(p).getroot();src=Path(r.find('m_SourceFilePath').get('text'));dds=MOD/'Textures'/(name+'.dds')
 if not src.is_file():src=dds
 dst=O/'sources'/(name+src.suffix);shutil.copy2(src,dst)
 Image.open(src).convert('RGB').save(O/'textures'/(name+'.png'))
 sources[name]={'path':str(src),'sha256':sha(src),'snapshot':str(dst),'native_dds_sha256':sha(dds),'size':Image.open(src).size}
im=Image.open(O/'textures/CSC_Atlas_Modern_B_BAKERS.png').convert('RGB');guide=Image.new('RGB',(768,256))
for i,slot in enumerate((11,12,15)):
 x=512+slot%4*128;y=slot//4*128;guide.paste(im.crop((x,y,x+128,y+128)).resize((256,256),Image.Resampling.NEAREST),(i*256,0))
guide.save(O/'sources/Interior_Paint_Target.png')
(O/'inputs.json').write_text(json.dumps({'sources':sources,'bindings':bindings,'interior_slots':[11,12,15]},indent=2));print(json.dumps({'sources':sources,'material_emissives':{k:v.get('Emissive') for k,v in bindings.items()}},indent=2))
