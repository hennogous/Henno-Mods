from pathlib import Path
import sys,shutil,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
from correct_modern_normals import normals
O=Path.home()/'Desktop/Codex/modern-level2-v3-details-20261028'
cache=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2'
fol=cache/'exec-a6e72073-ab1a-4091-9c40-8b5d87c35024.png';sign=cache/'exec-98a9679c-dc72-43eb-95c5-73014753453a.png'
shutil.copy2(fol,O/'sources/Foliage_Generated.png');shutil.copy2(sign,O/'sources/Hex_Sign_Generated.png')
patches={}
for slot,path,right in [(24,fol,False),(25,sign,True)]:
 im=Image.open(path).convert('RGB');w,h=im.size;patch=im.crop((w//2 if right else 0,0,w if right else w//2,h)).resize((128,128),Image.Resampling.LANCZOS);patches[slot]=patch
b=Image.open(O/'textures/CSC_Props_Modern_01_B.png').convert('RGB');n=Image.open(O/'textures/CSC_Props_Modern_01_N.png').convert('RGB');g=Image.open(O/'textures/CSC_Props_Modern_01_G.png').convert('RGB');m=Image.open(O/'textures/CSC_Props_Modern_01_M.png').convert('RGB')
Y,X=np.mgrid[:128,:128];h=np.zeros((128,128),dtype=float)
# Selected large leaf/flower forms, traced from generated paint. No luminance/noise bump.
for x,y,rx,ry in [(9,10,8,4),(23,28,8,6),(49,16,8,10),(70,10,5,9),(91,13,7,9),(119,31,7,8),(24,55,8,6),(57,66,8,10),(19,80,7,6),(86,74,8,10),(115,111,7,9),(74,113,8,11)]:
 h+=.018*np.maximum(0,1-((X-x)/rx)**2-((Y-y)/ry)**2)**2
for x,y in [(27,14),(109,20),(67,33),(19,51),(94,56),(46,67),(114,79),(67,89),(15,96),(47,107),(106,104)]:h+=.025*np.exp(-((X-x)**2+(Y-y)**2)/9)
mask=Image.new('L',(128,128));d=ImageDraw.Draw(mask);d.polygon([(5,64),(35,13),(93,13),(120,64),(93,114),(35,114)],fill=255);mask=mask.filter(ImageFilter.GaussianBlur(.65));hs=.12*(1-np.asarray(mask,dtype=float)/255)
for slot,height,coverage in [(24,h,(8,5)),(25,hs,(14,12))]:
 x=slot%8*128;y=slot//8*128;b.paste(patches[slot],(x,y));n.paste(normals(height,coverage),(x,y));g.paste((18,18,18),(x,y,x+128,y+128));m.paste((0,0,0),(x,y,x+128,y+128));np.save(O/'sources'/f'height_{slot}.npy',height)
 patches[slot].save(O/'sources'/f'{slot}_B.png')
for ch,im in [('B',b),('N',n),('G',g),('M',m)]:im.save(O/'textures'/f'CSC_Props_Modern_01_{ch}.png')
print('DECOR_MATERIALS_READY')
