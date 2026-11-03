from pathlib import Path
import json,shutil,hashlib,subprocess
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-level2-v3-details-20261028';ART=Path.home()/'Desktop/Working Files/3D Art'
D=ART/'Level 2/modern/revision-03-window-boxes-sign';P=ART/'Props/Modern/revision-01-architectural-details'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for kind,source,dest,prefix in [('building',ART/'Level 2/modern/revision-01-concept-base/atlas-candidate',D/'building-atlas-candidate','CSC_Atlas_Modern'),('props',ART/'Textures/CSC_Props_Modern/Current',P/'props-atlas-candidate','CSC_Props_Modern_01')]:
 shutil.copytree(source,dest,dirs_exist_ok=True)
 for path in (O/'textures').glob(prefix+'*.png'):
  shutil.copy2(path,dest/'textures'/path.name)
  ch=path.stem.removeprefix(prefix+'_');ch='B' if ch=='B_BAKERS' else ch
  if ch in ('B','N','G','M','E'):shutil.copy2(path,dest/'sources'/('registered_'+ch+'.png'))
 plan=json.loads((dest/'atlas-plan.json').read_text());info=json.loads((dest/'library.json').read_text())
 if kind=='building':
  shutil.copy2(O/'bakes/Building.png',dest/'bakes/CSC_Level_2_Modern.png')
  shutil.copy2(Path.home()/'Desktop/Codex/modern-level2-v2-footprint-20261028/bakes/Workshop.png',dest/'bakes/CSC_Level_2_Modern_Workshop.png')
  plan['building']['stage3_used_tiles']['6']='green glazed entrance door; layout follows historical wall openings'
 else:
  plan['props']['decorative_cells']={'24':'windowbox foliage with ivory/yellow flowers','25':'blank framed hexagonal sign, point-up on mesh'}
  for group,ident,rect in [('FlowerBox','CSC_ALL_Window_Box_Modern',[512,0,768,256]),('Sign','CSC_ALL_Hanging_Sign_Modern',[768,0,1024,256])]:
   plan['AO_allocations'][ident]=['props',rect];shutil.copy2(O/'bakes'/(group+'.png'),dest/'bakes'/(ident+'.png'))
  shutil.copytree(O/'sources',dest/'sources/decor',dirs_exist_ok=True)
  shutil.copy2(Path(__file__).with_name('decor_materials.py'),dest/'sources/decor/decor_materials.py')
 plan['status']='Authoring candidate; shared Current/runtime unchanged'
 (dest/'atlas-plan.json').write_text(json.dumps(plan,indent=2))
 info.update(release='2026-10-28_Level2_Details_candidate03',status='Authoring candidate, not published Current or AE',maps={p.name:sha(p) for p in (dest/'textures').glob('*.png')});(dest/'library.json').write_text(json.dumps(info,indent=2))
# Prove existing modern prop consumers and Level1 surfaces are untouched.
base=ART/'Textures/CSC_Props_Modern/Current/textures';checks={}
for ch in ('B','N','G','M'):
 a=Image.open(base/f'CSC_Props_Modern_01_{ch}.png').convert('RGB');b=Image.open(O/'textures'/f'CSC_Props_Modern_01_{ch}.png').convert('RGB')
 for rect in [(0,0,1024,384),(256,384,1024,512),(0,512,1024,1024)]:assert a.crop(rect).tobytes()==b.crop(rect).tobytes()
checks['existing_prop_cells_preserved']=True
for path in (ART/'Textures/CSC_Buildings_Modern/Current/textures').glob('*.png'):
 a=Image.open(path).convert('RGB');b=Image.open(O/'textures'/path.name).convert('RGB');w,h=a.size
 for rect in [(0,0,w//2,h//2),(0,h//2,w,h)]:assert a.crop(rect).tobytes()==b.crop(rect).tobytes(),path.name
checks['existing_building_regions_preserved']=True
# Native surface round-trip for the newly introduced prop artwork.
(O/'native/textures').mkdir(exist_ok=True,parents=True)
for ch in ('B','N','G','M'):
 p=O/'textures'/f'CSC_Props_Modern_01_{ch}.png'
 r=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',str(O/'native/textures'),str(p)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 assert Image.open(O/'native/textures'/(p.stem+'.dds')).convert('RGB').tobytes()==Image.open(p).convert('RGB').tobytes()
checks['native_prop_surface_pixels_verified']=True
bg=(26,30,33,255);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',26);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
sheet=Image.new('RGBA',(1600,880),bg);draw=ImageDraw.Draw(sheet)
for i,(path,title) in enumerate([(O/'review/combined.png','Modern Level 2 · historical wall openings'),(O/'review/rear.png','Rear view · reusable details')]):
 im=Image.open(path).convert('RGBA').resize((800,800),Image.Resampling.LANCZOS);sheet.alpha_composite(im,(800*i,50));draw.text((800*i+18,12),title,font=font,fill=(235,235,225))
draw.text((18,850),'Hexagonal sign: points up/down · emission off',font=small,fill=(190,200,190));sheet.convert('RGB').save(O/'Level2_Details_Review.png')
sheet=Image.new('RGBA',(1400,1020),bg);draw=ImageDraw.Draw(sheet)
for i,mode in enumerate(('B-only','combined','normal-off-A','normal-on-A','normal-off-B','normal-on-B')):
 im=Image.open(O/'review'/('props-'+mode+'.png')).convert('RGBA').resize((700,300),Image.Resampling.LANCZOS);x=i%2*700;y=i//2*340;sheet.alpha_composite(im,(x,y+35));draw.text((x+18,y+5),mode,font=small,fill='white')
sheet.convert('RGB').save(O/'Prop_Material_Review.png')
(O/'package-verification.json').write_text(json.dumps(checks,indent=2));print(checks)
