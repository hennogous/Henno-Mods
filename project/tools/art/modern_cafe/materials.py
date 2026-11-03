"""Pack painted sources and explicitly registered structural relief; no albedo bump."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,shutil
A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029';T=O/'textures'
G=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2'
for src,dst in [('exec-8ff65788-c7f7-4b24-a565-ed5e69dc271e.png','L3_Modern_Painted.png'),('exec-e2fe69ab-fd99-4108-994c-045906c10256.png','Cafe_Interiors_Props_Painted.png')]:shutil.copy2(G/src,O/'sources'/dst)
paint=Image.open(O/'sources/L3_Modern_Painted.png').convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS)
sheet=Image.open(O/'sources/Cafe_Interiors_Props_Painted.png').convert('RGB').resize((1536,1024),Image.Resampling.LANCZOS)
def normal(h,world=30,relief=.8):
 a=np.array(h.filter(ImageFilter.GaussianBlur(1.15)),dtype=float)/255*relief;dy,dx=np.gradient(a,world/h.height,world/h.width);n=np.stack((-dx,dy,np.ones_like(dx)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True);return Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255),'RGB')
def pad(p,size,padding):
 r=p.resize((size-2*padding,size-2*padding),Image.Resampling.LANCZOS);out=r.resize((size,size));out.paste(r,(padding,padding));return out
def tile(im,i,n=4):s=im.width//n;return (i%n*s,i//n*s,(i%n+1)*s,(i//n+1)*s)
base=Image.open(T/'CSC_Atlas_Modern_B_BAKERS.png').convert('RGB');base.paste(paint.resize((512,512),Image.Resampling.LANCZOS),(0,512));base.save(T/'CSC_Atlas_Modern_B_BAKERS.png')
# Preserve historical relief on unchanged quoins/arches; replace tile-roof relief.
oldN=Image.open(A/'Textures/CSC_Atlas_N.dds').convert('RGB').crop((0,512,512,1024)).resize((1024,1024))
height=Image.new('L',(1024,1024),0);hd=ImageDraw.Draw(height);mask=Image.new('L',(1024,1024));md=ImageDraw.Draw(mask)
regions=[[(414,45),(866,45),(866,409),(414,409)],[(80,157),(176,114),(273,158),(273,296),(80,296)],[(840,502),(1006,502),(1006,895),(840,895)]]
for poly in regions:
 md.polygon(poly,fill=255)
 for x in range(min(p[0] for p in poly)+18,max(p[0] for p in poly),54):hd.line((x,min(p[1] for p in poly),x,max(p[1] for p in poly)),fill=210,width=4)
oldN.paste(normal(height,world=100,relief=1.2),mask=mask)
# Bold green frames follow the painted glazing, not the glass reflections.
for rect,xs,ys in [((464,719,577,941),(500,540),(782,855,934)),((638,724,755,833),(695,),(782,830)),((59,441,144,554),(101,),(468,507,549)),((219,441,305,554),(262,),(468,507,549)),((310,60,391,127),(350,),(91,124))]:
 h=Image.new('L',(1024,1024));d=ImageDraw.Draw(h);d.rectangle(rect,outline=220,width=6)
 for x in xs:d.line((x,rect[1],x,rect[3]),fill=220,width=5)
 for y in ys:d.line((rect[0],y,rect[2],y),fill=220,width=5)
 oldN.paste(normal(h,100,1.1).crop(rect),rect)
nn=Image.open(T/'CSC_Atlas_Modern_N.png').convert('RGB');nn.paste(oldN.resize((512,512),Image.Resampling.LANCZOS),(0,512));nn.save(T/'CSC_Atlas_Modern_N.png')
for ch,val in [('G',52),('M',0),('O',255)]:
 im=Image.open(T/f'CSC_Atlas_Modern_{ch}.png').convert('RGB');patch=Image.new('RGB',(1024,1024),(val,)*3);d=ImageDraw.Draw(patch)
 if ch in ('G','M'):
  for poly in regions:d.polygon(poly,fill=(115,)*3 if ch=='G' else (40,)*3)
 # Glass masks deliberately leave frame strips opaque.
 for xa,xb in ((468,498),(505,538),(544,574)):
  for ya,yb in ((744,779),(786,852),(859,930)):
   if ch=='O':d.rectangle((xa,ya,xb,yb),fill=(42,)*3)
   elif ch=='G':d.rectangle((xa,ya,xb,yb),fill=(205,)*3)
 if ch=='O':
  for xa,xb in ((647,691),(700,744)):d.rectangle((xa,754,xb,779),fill=(42,)*3);d.rectangle((xa,787,xb,826),fill=(42,)*3)
 im.paste(patch.resize((512,512)),(0,512));im.save(T/f'CSC_Atlas_Modern_{ch}.png')
# Dedicated interiors. A quarter owns its B/E art; UV layout and normal structure stay fixed.
ib=Image.new('RGB',(1024,1024),(223,211,184));inn=Image.new('RGB',(1024,1024),(128,128,255));ie=Image.new('RGB',(512,512))
buildB=Image.open(T/'CSC_Atlas_Modern_B_BAKERS.png');buildN=Image.open(T/'CSC_Atlas_Modern_N.png')
for target,src in enumerate((11,12,15)):
 rect=(514+src%4*128,src//4*128+2,638+src%4*128,126+src//4*128);p=buildB.crop(rect);ib.paste(pad(p,256,6),tile(ib,target));inn.paste(pad(buildN.crop(rect),256,6),tile(inn,target))
for i in range(3):
 p=sheet.crop((i*512,0,(i+1)*512,512));ib.paste(pad(p,256,6),tile(ib,4+i))
 h=Image.new('L',(512,512),0);d=ImageDraw.Draw(h)
 if i==0:
  for y in (124,237):d.rounded_rectangle((18,y-5,500,y+9),radius=3,fill=230)
  d.rounded_rectangle((130,256,383,398),radius=7,fill=185);d.rectangle((8,399,503,420),fill=245)
  for x,y,X,Y in [(137,57,170,117),(176,66,211,119),(215,76,252,120),(339,39,389,118),(400,39,451,118),(60,189,97,230),(104,188,140,231),(204,168,241,230),(248,168,283,230),(290,168,326,230)]:d.rounded_rectangle((x,y,X,Y),radius=5,fill=150)
  for x in (20,152,283,412):d.rectangle((x,440,x+80,503),outline=130,width=5)
 elif i==1:
  for y in (125,242):d.rectangle((20,y-6,496,y+9),fill=230)
  for x in (139,166,191,222):d.rounded_rectangle((x,47,x+20,116),radius=2,fill=155)
  d.ellipse((161,336,353,376),fill=220);d.ellipse((292,404,425,445),fill=150);d.arc((317,313,460,435),180,360,fill=210,width=10);d.rectangle((5,455,506,471),fill=100)
 else:
  d.rectangle((0,0,511,511),fill=130)
  for x in (8,137,264,392,506):d.line((x,0,x,511),fill=0,width=4)
  for y in (9,121,239,358,480):d.line((0,y,511,y),fill=0,width=4)
 h.save(O/'sources'/f'Cafe_Interior_{i}_Relief.png');inn.paste(pad(normal(h,30,.8 if i<2 else .25),256,6),tile(inn,4+i))
for slot in (0,1,2,4,5,6):
 rgb=np.asarray(ib.crop(tile(ib,slot)),float)/255;lin=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4);lin*=.16 if slot not in (2,6) else .07;lin*=np.array([1,.88,.65]);e=np.where(lin<=.0031308,lin*12.92,1.055*lin**(1/2.4)-.055);ie.paste(Image.fromarray(np.uint8(np.clip(e,0,1)*255)).resize((128,128),Image.Resampling.LANCZOS),tile(ie,slot))
ib.save(T/'CSC_Interiors_Modern_B_BAKERS.png');inn.save(T/'CSC_Interiors_Modern_N.png');ie.save(T/'CSC_Interiors_Modern_E_BAKERS.png')
# Counter and truck reuse coherent contiguous new row; no occupied surfaces touched.
pb=Image.open(T/'CSC_Props_Modern_01_B.png').convert('RGB');pn=Image.open(T/'CSC_Props_Modern_01_N.png').convert('RGB')
for i,slot in enumerate((40,41,43)):
 p=sheet.crop((i*512,512,(i+1)*512,1024));pb.paste(pad(p,128,3),tile(pb,slot,8));h=Image.new('L',(512,512));d=ImageDraw.Draw(h)
 if i==0:
  d.rounded_rectangle((48,45,460,151),radius=12,fill=190);d.rectangle((35,340,480,392),fill=240)
  for x in (162,352):d.rounded_rectangle((x-40,158,x+40,190),radius=8,fill=200);d.ellipse((x-42,273,x+42,345),fill=175)
 elif i==1:
  d.rectangle((13,20,500,492),outline=255,width=16)
  for y in (162,281,410):d.rectangle((25,y-5,490,y+6),fill=230)
  for x in (85,200,320,432):
   for y in (130,246,375):d.ellipse((x-34,y-27,x+34,y+22),fill=150)
 else:d.rounded_rectangle((125,142,356,345),radius=35,fill=45)
 pn.paste(pad(normal(h,20,.6),128,3),tile(pn,slot,8))
pb.save(T/'CSC_Props_Modern_01_B.png');pn.save(T/'CSC_Props_Modern_01_N.png')
plan=json.loads((O/'atlas-plan.json').read_text());plan['AO_candidate'].update(counter=[0,768,256,1024],van=[256,768,512,1024],parasol=[896,512,1024,640]);(O/'atlas-plan.json').write_text(json.dumps(plan,indent=2))
print('PAINT_AND_REGISTERED_RELIEF_PACKED')
