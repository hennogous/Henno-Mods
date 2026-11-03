"""Evidence and comparison package for the extension-only revision."""
from pathlib import Path
import json,shutil,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path.home()/'Desktop/Codex/modern-level2-v2-footprint-20261028'
OLD=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
D=Path.home()/'Desktop/Working Files/3D Art/Level 2/modern/revision-02-tailor-footprint'
ident='CSC_Level_2_Modern'
a=json.loads((OLD/'models'/f'{ident}.json').read_text());b=json.loads((O/'models'/f'{ident}.json').read_text())
for ma,mb in zip(a['meshes'],b['meshes']):
 assert {k:v for k,v in ma.items() if k!='materials'}=={k:v for k,v in mb.items() if k!='materials'},'Main geometry/UV/bindings changed'
for ch in ('B_BAKERS','N','G','M','E'):
 name=f'CSC_Atlas_Modern_{ch}.png';assert (OLD/'textures'/name).read_bytes()==(O/'textures'/name).read_bytes(),name
im0=Image.open(OLD/'textures/CSC_Atlas_Modern_AO.png').convert('RGB');im1=Image.open(O/'textures/CSC_Atlas_Modern_AO.png').convert('RGB')
assert im0.crop((1024,0,1536,512)).tobytes()==im1.crop((1024,0,1536,512)).tobytes(),'Main AO changed'
shutil.copy2(O/'CSC_Level_2_Modern_Assembly.blend',D/'CSC_Level_2_Modern_Review.blend')
(D/'bakes').mkdir(exist_ok=True);shutil.copy2(O/'bakes/Workshop.png',D/'bakes/Workshop.png')
bg=(26,30,33,255);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',28);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
def sheet(name,panels,size=850):
 out=Image.new('RGBA',(size*len(panels),size+90),bg);d=ImageDraw.Draw(out)
 for i,(path,title) in enumerate(panels):
  im=Image.open(path).convert('RGBA');im=ImageOps.contain(im,(size,size),Image.Resampling.LANCZOS)
  out.alpha_composite(im,(i*size+(size-im.width)//2,50));d.text((i*size+22,12),title,font=font,fill=(230,230,220))
 d.text((22,size+58),'Extension-only revision | main building unchanged | emission off',font=small,fill=(185,195,190))
 out.convert('RGB').save(O/name)
sheet('Extension_Before_After.png',[(OLD/'review/combined.png','First version'),(O/'review/combined.png','Forward work bay + narrow rear return')])
sheet('Extension_Rear_And_Plan.png',[(O/'review/rear.png','Rear return'),(O/'review/top.png','Top view')],750)
report={'main_geometry_UVs_bindings_exactly_unchanged':True,'main_AO_exactly_unchanged':True,'surface_maps_exactly_unchanged':True,'main_vertices':896,'workshop_vertices':780,'reviewed_views':['front','rear','top'],'scope':'Extension only. Tailor forward lean-to relationship; narrow side continuation12 and rear return8. Separate variant; no AE update.'}
(O/'variant-verification.json').write_text(json.dumps(report,indent=2));shutil.copy2(O/'variant-verification.json',D/'variant-verification.json')
(D/'Texture-authoring.txt').write_text('Surface B/N/G/M/E artwork is unchanged from revision-01-concept-base/atlas-candidate. This variant retains portable texture snapshots; only workshop UV2 and its AO allocation are new. Main geometry, UV1/2/3, bindings and AO are unchanged. Rebuild the workshop with project/tools/art/modern_level2/footprint_v2.py only if this variant has not subsequently been hand edited. Shared Current and AE remain unchanged.\n')
print(json.dumps(report))
