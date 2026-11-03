from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,shutil
O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028'
src=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2/exec-458639bf-25bc-4adc-98ab-d7ac58113532.png'
shutil.copy2(src,O/'sources/Bread_Interior_Generated.png');sheet=Image.open(src).convert('RGB')
old=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Bakery/modern/revision-02-concept-c/textures'
maps={fam:{c:Image.open(old/f'{fam}_{c}.png').convert('RGB') for c in ('N','G','M')} for fam in ('CSC_Props_Modern_01','CSC_Atlas_Modern')}
maps['CSC_Props_Modern_01']['B']=Image.open(old/'CSC_Props_Modern_01_B.png').convert('RGB')
maps['CSC_Atlas_Modern']['B']=Image.open(old/'CSC_Atlas_Modern_B_BAKERS.png').convert('RGB')
def norm(h,coverage):
 dy,dx=np.gradient(h,coverage[1]/h.shape[0],coverage[0]/h.shape[1]);n=np.stack((-dx,dy,np.ones_like(h)),2);n/=np.linalg.norm(n,axis=2,keepdims=True);return Image.fromarray(np.uint8(np.clip((n+1)*127.5,0,255)))
def padded(a):return Image.fromarray(np.pad(np.array(a.resize((122,122),Image.Resampling.LANCZOS)),((3,3),(3,3),(0,0)),mode='edge'))
yy,xx=np.mgrid[:512,:512];profiles=[]
for i,ellipses in enumerate([
 [(144,166,96,96,0),(358,180,103,110,-10),(223,369,98,99,0)],
 [(94,259,59,221,0),(254,260,59,222,0),(419,260,59,221,0)],
 [(120,155,69,87,-8),(282,148,69,83,0),(437,155,62,83,10),(110,361,60,85,-10),(281,374,74,105,-24),(418,367,61,113,20)]
]):
 h=np.zeros((512,512));occ=np.ones_like(h)
 for x,y,rx,ry,angle in ellipses:
  a=np.deg2rad(angle);u=(xx-x)*np.cos(a)+(yy-y)*np.sin(a);v=-(xx-x)*np.sin(a)+(yy-y)*np.cos(a);r=(u/rx)**2+(v/ry)**2
  h=np.maximum(h,1.7*np.maximum(0,1-r)**.65);occ=np.minimum(occ,1-.25*np.exp(-((np.sqrt(r)-1)/.09)**2))
 # Tray rim is a shallow raised border; flour, seeds and toasted stains are colour only.
 rim=((xx<17)|(xx>495)|(yy<17)|(yy>495));h=np.maximum(h,rim*.45)
 # Explicit score cuts aligned to the painted central loaf cuts, not brightness noise.
 cuts=Image.new('L',(512,512));d=ImageDraw.Draw(cuts)
 if i==0:
  d.line([(88,105),(190,214)],fill=255,width=9);d.line([(87,209),(201,107)],fill=255,width=9)
  d.line([(303,104),(351,169),(409,235)],fill=255,width=10)
  d.line([(170,364),(225,310),(277,368),(223,419),(170,364)],fill=255,width=9)
 elif i==1:
  for x in (94,254,419):
   for y in (120,205,290,375):d.line([(x-22,y+27),(x+20,y-25)],fill=255,width=10)
 h-=np.array(cuts.filter(ImageFilter.GaussianBlur(2)),dtype=float)/255*.2*(h>.4)
 h=np.pad(np.array(Image.fromarray(h.astype('float32'),'F').resize((122,122),Image.Resampling.BILINEAR)),3,mode='edge');profiles.append(h)
 family='CSC_Props_Modern_01';slot=36+i;x=slot%8*128;y=slot//8*128
 patch=padded(sheet.crop((i*512,0,(i+1)*512,512)))
 maps[family]['B'].paste(patch,(x,y));maps[family]['N'].paste(norm(h,(14*128/122,12*128/122)),(x,y));maps[family]['G'].paste((62,62,62),(x,y,x+128,y+128));maps[family]['M'].paste((0,0,0),(x,y,x+128,y+128))
 np.save(O/'sources'/f'tray_{slot}_height.npy',h)
 micro=Image.fromarray(np.pad(np.array(Image.fromarray(np.uint8(occ*255)).resize((122,122),Image.Resampling.LANCZOS)),3,mode='edge'));micro.save(O/'sources'/f'tray_{slot}_microAO.png')
 # Registration sheet keeps actual B and structural height side by side.
 proof=Image.new('RGB',(512,256));proof.paste(patch.resize((256,256)),(0,0));proof.paste(Image.fromarray(np.uint8(np.clip(h/1.7*255,0,255))).convert('RGB').resize((256,256)),(256,0));proof.save(O/'sources'/f'tray_{slot}_registration.png')
for i,slot in enumerate((11,12,15)):
 family='CSC_Atlas_Modern';x=512+slot%4*128;y=slot//4*128
 maps[family]['B'].paste(padded(sheet.crop((i*512,512,(i+1)*512,1024))),(x,y));maps[family]['N'].paste((128,128,255),(x,y,x+128,y+128));maps[family]['G'].paste((40,40,40),(x,y,x+128,y+128));maps[family]['M'].paste((0,0,0),(x,y,x+128,y+128))
# Preserve the existing frame art/relief, replacing painted warm panes with the
# accepted blue-grey glass from cell5; warmth now comes from the inset box.
b=maps['CSC_Atlas_Modern']['B'];blue=b.crop((640,128,768,256));b.paste(blue,(768,384))
o=Image.new('RGB',(1024,1024),'white');od=ImageDraw.Draw(o);g=maps['CSC_Atlas_Modern']['G']
for slot,rects in [(14,[(20,17,59,54),(69,17,108,54),(20,64,59,100),(69,64,108,100)]),(6,[(24,18,59,40),(69,18,102,40),(24,48,59,69),(69,48,102,69),(24,78,59,100),(69,78,102,100)])]:
 x=512+slot%4*128;y=slot//4*128
 for j,(a,c,A,C) in enumerate(rects):
  rect=(x+a,y+c,x+A,y+C);od.rectangle(rect,fill=(40,40,40));g.paste((220,220,220),rect)
  if slot==6:b.paste(blue.crop((20,17,59,54)).resize((A-a,C-c)),rect)
  od.line([(x+a,y+C-3),(x+A-3,y+c)],fill=(70,70,70),width=2)
o.save(O/'textures/CSC_Atlas_Modern_O.png')
for family,channels in maps.items():
 for c,im in channels.items():im.save(O/'textures'/(family+('_B_BAKERS' if family=='CSC_Atlas_Modern' and c=='B' else '_'+c)+'.png'))
(O/'atlas-plan-v3.json').write_text(json.dumps({'candidate_only':True,'source':str(src),'generator':'Built-in ImageGen','props_cells':{'36':'round sourdough tray','37':'baguettes tray','38':'rolls and croissants tray'},'building_stage3_cells':{'11':'interior back shelves','12':'interior side wall','15':'interior floor','14':'ground window frame with opacity/gloss','6':'door with opacity/gloss'},'opacity':'white default, glass40/255 with70/255 highlight; Generic_OPAC native coverage not physical refraction','microAO':'explicit contact profiles at painted loaf perimeter, composited onto tray faces in UV2 after geometry bake','height':'explicit loaf volumes and traced scoring; no luminance-to-height'},indent=2))
print('V3_MATERIALS_READY')
