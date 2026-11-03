from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,shutil,json
O=Path.home()/'Desktop/Codex/modern-bakery-v2-20261028'
source=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2/exec-e92b1877-cabb-4596-a83f-262e2e915e24.png'
shutil.copy2(source,O/'sources/Truck_Windows_Generated.png');sheet=Image.open(source).convert('RGB')
def normal(h,w):
 dy,dx=np.gradient(h,w[1]/h.shape[0],w[0]/h.shape[1]);a=np.stack((-dx,dy,np.ones_like(h)),axis=-1);a/=np.linalg.norm(a,axis=2,keepdims=True);return Image.fromarray(np.uint8(np.clip((a+1)*127.5,0,255)))
maps={c:Image.open(O/'textures'/f'CSC_Props_Modern_01_{c}.png').convert('RGB') for c in ('B','N','G','M')}
for i,slot in enumerate(range(32,36)):
 patch=sheet.crop((i%3*512,i//3*512,i%3*512+512,i//3*512+512)).resize((122,122),Image.Resampling.LANCZOS)
 tile=np.pad(np.array(patch),((3,3),(3,3),(0,0)),mode='edge');h=Image.new('L',(512,512),128);d=ImageDraw.Draw(h)
 if i==0:
  d.rounded_rectangle((42,40,470,220),radius=12,fill=65);d.rectangle((139,307,377,418),fill=80);d.rectangle((31,447,482,479),fill=200)
  for x in (96,416):d.ellipse((x-32,300,x+32,366),fill=175)
 elif i==1:
  d.polygon([(48,220),(112,44),(465,44),(465,235)],fill=65);d.rectangle((88,264,458,456),outline=95,width=6);d.rectangle((354,282,430,301),fill=190)
 elif i==2:d.rectangle((16,16,496,496),outline=140,width=5)
 else:
  d.ellipse((34,34,478,478),fill=140);d.ellipse((127,127,385,385),fill=175);d.ellipse((206,206,306,306),fill=198)
 height=(np.array(h.filter(ImageFilter.GaussianBlur(4)).resize((128,128)),dtype=float)-128)/127*.18
 x=slot%8*128;y=slot//8*128;maps['B'].paste(Image.fromarray(tile),(x,y));maps['N'].paste(normal(height,[(16,20),(15,19),(24,20),(7,7)][i]),(x,y));maps['G'].paste((75,75,75) if i<3 else (30,30,30),(x,y,x+128,y+128));maps['M'].paste((50,50,50) if i<3 else (20,20,20),(x,y,x+128,y+128));np.save(O/'sources'/f'{slot}_height.npy',height)
for c,im in maps.items():im.save(O/'textures'/f'CSC_Props_Modern_01_{c}.png')
# Keep the exact existing frames and normal registration. Only generated panes
# enter the inherited B; the warm four-pane window gets its own unused cell14.
base=Image.open(O/'textures/CSC_Atlas_Modern_B_BAKERS.png').convert('RGB')
for idx,srcslot,dstslot,panes in [(4,5,14,[(20,17,59,54),(69,17,108,54),(20,64,59,100),(69,64,108,100)]),(5,6,6,[(24,18,59,40),(69,18,102,40),(24,48,59,69),(69,48,102,69),(24,78,59,100),(69,78,102,100)])]:
 sx=512+srcslot%4*128;sy=srcslot//4*128;patch=base.crop((sx,sy,sx+128,sy+128));generated=sheet.crop((idx%3*512,idx//3*512,idx%3*512+512,idx//3*512+512)).resize((128,128),Image.Resampling.LANCZOS)
 for rect in panes:patch.paste(generated.crop(rect),rect)
 dx=512+dstslot%4*128;dy=dstslot//4*128;base.paste(patch,(dx,dy))
 if dstslot!=srcslot:
  for c in ('N','G','M'):
   name=f'CSC_Atlas_Modern_{c}.png';im=Image.open(O/'textures'/name).convert('RGB');im.paste(im.crop((sx,sy,sx+128,sy+128)),(dx,dy));im.save(O/'textures'/name)
base.save(O/'textures/CSC_Atlas_Modern_B_BAKERS.png')
(O/'atlas-plan-v2.json').write_text(json.dumps({'candidate_only':True,'props_surface':{'32':'truck front','33':'truck cab side','34':'cream cargo with bread emblem','35':'tyre and hub'},'building_stage3':{'6':'existing green door with warm painted glass','14':'warm four-pane ground window; registered N/G/M copied from5','5':'upstairs blue-grey four-pane window unchanged'},'AO':{'Building':[1024,0,1536,512],'Workshop':[1536,0,1792,256],'Truck':[512,768,1024,1024]},'emissive':'upper windows UV3 sample existing window cell5; all ground glazing black'},indent=2))
print('V2_MATERIALS_READY')
