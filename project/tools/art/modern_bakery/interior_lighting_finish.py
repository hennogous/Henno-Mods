"""Verify installed bytes, atlas safety, automatic indexing and review sheets."""
import sys,json,hashlib,os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-interior-lighting-20261028';MOD=ROOT/'Civ Supply Chains'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify():
 report=json.loads((O/'publication-report.json').read_text());mismatches=[r['destination'] for r in report['files'] if sha(r['destination'])!=r['after']]
 assert not mismatches,mismatches
 base=json.loads((O/'baseline.json').read_text());preserved={f:all(sha(MOD/p)==h for p,h in base.items() if p.startswith(f+'/')) for f in ('Assets','ArtDefs','XLPs')};assert all(preserved.values()),preserved
 checks=json.loads((O/'staging-validation.json').read_text());assert checks['historical_DDS_exact']
 assert sha(MOD/'Textures/CSC_Atlas_E_BAKERS.dds')==sha(MOD/'Textures/CSC_Atlas_E.dds')
 e=np.array(Image.open(O/'textures/CSC_Atlas_Modern_E_BAKERS.png').convert('RGB'));old=np.array(Image.open(O/'sources/CSC_Atlas_Modern_E.png').convert('RGB').resize((512,512),Image.Resampling.NEAREST));mask=np.zeros((512,512),bool);mask[128:192,256:448]=True
 assert np.array_equal(e[~mask],old[~mask]);assert not e[448:512,0:64].any()
 cache=json.loads((Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json').read_text())['Dependencies']
 indexed={name:any(k.endswith('/'+name+'.tex') for k in cache) for name in ('CSC_Atlas_E_BAKERS','CSC_Atlas_Modern_E_BAKERS')}
 bindings={}
 for name in ('CSC_BAKERS_E','CSC_BAKERS_E_2','CSC_BAKERS_Modern','CSC_BAKERS_Modern_2'):
  deps=cache.get('Civ Supply Chains/Materials/'+name+'.mtl',[]);target='CSC_Atlas_Modern_E_BAKERS' if 'Modern' in name else 'CSC_Atlas_E_BAKERS';bindings[name]=any(p.endswith('/'+target+'.tex') for p in deps)
 assert all(indexed.values()) and all(bindings.values()),(indexed,bindings)
 final={'passed':True,'published_bytes_exact':True,'preserved':preserved,'historical_E_DDS_byte_identical':True,'modern_existing_window_pixels_unchanged':True,'black_sentinel_preserved':True,'AE_texture_indexed':indexed,'AE_material_dependencies_updated':bindings,'day_review':'E disabled; lighter B alone','night_review':'Soft interior emission at strength1 in Blender; native engine brightness requires human review','game_deployment':False}
 (O/'final-verification.json').write_text(json.dumps(final,indent=2));print(json.dumps(final,indent=2))
def sheet():
 font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
 page=Image.new('RGB',(1400,1080),(25,29,35));draw=ImageDraw.Draw(page)
 for i,(label,title) in enumerate([('after-day','Day — lighter interior, E disabled'),('after-night','Night — soft room emission')]):
  im=Image.open(O/'review'/label/'render.png').convert('RGBA').resize((700,700),Image.Resampling.LANCZOS);page.paste(im,(i*700,35),im);draw.text((i*700+25,12),title,font=font,fill=(235,236,238))
 for i,(label,title) in enumerate([('before-day','Previous daytime'),('after-day','Brighter daytime'),('after-night','Night detail')]):
  im=Image.open(O/'review'/label/'render.png').convert('RGBA').crop((650,565,805,770)).resize((217,287),Image.Resampling.LANCZOS);x=125+i*460;page.paste(im,(x,770),im);draw.text((x,740),title,font=small,fill=(235,236,238))
 draw.text((25,1055),'Saved AE assembly • Blender lighting preview; native night intensity still needs review.',font=small,fill=(172,182,197));page.save(O/'review/Day-Night-Comparison.png')
 # Labeled allocation guide is separate from the paintable runtime PNG.
 atlas=Image.open(O/'textures/CSC_Atlas_Modern_E_BAKERS.png').convert('RGB').resize((1024,1024),Image.Resampling.NEAREST);guide=Image.new('RGB',(1380,1100),(25,29,35));guide.paste(atlas,(20,50));d=ImageDraw.Draw(guide)
 d.text((20,12),'Modern E / Bakers — fixed UV3 layout (512 px)',font=font,fill='white')
 roles={8:'Room back',9:'Room sides',10:'Room floor',11:'Reserved',12:'BLACK',13:'Room B back',14:'Room B side',15:'Room B floor'}
 for q,(ox,oy) in enumerate([(20,50),(532,50),(20,562),(532,562)]):
  for slot in range(16):
   x=ox+slot%4*128;y=oy+slot//4*128;d.rectangle((x,y,x+127,y+127),outline=(100,120,135),width=1);d.text((x+6,y+5),str(slot),font=small,fill=(180,200,210))
  d.rectangle((ox,oy,ox+511,oy+511),outline=(225,225,225),width=2)
 d.multiline_text((1060,60),'Quadrants\nTL: Stage 2\nTR: Stage 3\nBL: Stage 4\nBR: Storage\n\nSlots 0–7\nFaçade/windows\n\n'+ '\n'.join(f'{k}: {v}' for k,v in roles.items())+'\n\n64 px cells\n2 px UV inset\n\nPaint the PNG,\nnot this guide.',font=small,fill=(230,232,235),spacing=8)
 guide.save(O/'review/Modern-E-Layout-Guide.png')
if __name__=='__main__':verify();sheet()
