"""Stage a non-destructive shared-atlas candidate and measured surface guides."""
from pathlib import Path
from PIL import Image,ImageDraw
import shutil,json,hashlib
A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029'
for d in ('textures','sources','bakes','review','models','native'): (O/d).mkdir(parents=True,exist_ok=True)
baseline={}
for family in ('CSC_Buildings_Modern','CSC_Props_Modern','CSC_Buildings_Emissive'):
 for p in (A/'Textures'/family/'Current/textures').glob('*.png'):
  shutil.copy2(p,O/'textures'/p.name);baseline[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
# Keep the Café's unpublished occupied regions in this combined candidate.
C=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029/textures'
for ch in ('B_BAKERS','N','G','M','O'):
 p=O/'textures'/f'CSC_Atlas_Modern_{ch}.png';im=Image.open(p);src=Image.open(C/p.name);im.paste(src.crop((0,512,512,1024)),(0,512));im.save(p)
for ch in ('B','N','G','M'):
 p=O/'textures'/f'CSC_Props_Modern_01_{ch}.png';im=Image.open(p);src=Image.open(C/p.name)
 for cell in (40,41,43,44,45):x=cell%8*128;y=cell//8*128;im.paste(src.crop((x,y,x+128,y+128)),(x,y))
 im.save(p)
for p in C.glob('CSC_Interiors*'):shutil.copy2(p,O/'textures'/p.name)
for family,rects in [('CSC_Atlas_Modern',[(0,1024,512,1536)]),('CSC_Props_Modern_01',[(0,768,512,1024),(896,512,1024,768)])]:
 p=O/'textures'/f'{family}_AO.png';im=Image.open(p);src=Image.open(C/p.name)
 for rect in rects:im.paste(src.crop(rect),rect)
 im.save(p)
Image.open(A.parent/'Pantry Exports/DIS_COM_Base_B.dds').convert('RGB').save(O/'sources/Firaxis_Market_B.png')
im=Image.open(O/'textures/CSC_Atlas_Modern_B_BAKERS.png');im.save(O/'sources/Existing_Modern_B.png')
# Flat measured faces: door leaves 11x23 each; four-pane window 24x20;
# truck bed side 24x6; electric hoist casing 5x4. Texturing scales recorded below.
g=Image.new('RGB',(1024,1024),'#48583c');d=ImageDraw.Draw(g)
d.rectangle((8,8,503,503),fill='#455b3d',outline='#a0a77c',width=8)
for x in (35,256,477):d.line((x,24,x,488),fill='#233a2c',width=12)
for y in (65,450):d.line((25,y,486,y),fill='#a2ac7a',width=12)
d.rectangle((520,8,1015,503),fill='#ded2ab');d.rectangle((548,36,986,475),fill='#405547')
for x0,x1 in ((567,752),(781,968)):
 for y0,y1 in ((55,239),(270,456)):d.rectangle((x0,y0,x1,y1),fill='#38403c')
d.rectangle((8,520,503,1015),fill='#4c6045')
for y in (550,690,830,975):d.rectangle((25,y,486,y+15),fill='#829267')
d.rectangle((520,520,1015,1015),fill='#65704c');d.rectangle((585,585,950,900),fill='#cbb747');d.rectangle((630,665,915,810),fill='#445147');d.ellipse((680,705,715,740),fill='#d3bc55')
g.save(O/'sources/Storage_Surface_Projection_Guide.png')
plan={'status':'candidate; no Current/runtime publication','source_hashes':baseline,'building_quadrant':[512,512,1024,1024],'storage_cells':{'0':'brick (registered accepted L2 material)','1':'grey block','2':'standing seam roof','3':'sage trim','4':'cream stone trim','5':'new four-pane stock window','6':'new loading-door leaves','7':'concrete','8':'timber grain','9':'dark interior','10':'green steel','11':'steel grey'},'props_new_cells':{'46':'green truck bed panelling','47':'electric hoist casing'},'preserved_cafe_cells':[40,41,43,44,45],'AO':{'M':[1024,1024,1536,1536],'L':[1536,1024,2048,1536],'Hoist':[1024,0,1280,256],'Truck':[1280,0,1792,512],'PalletJack':[1024,256,1280,512],'Drum':[1792,0,2048,256]},'AO_props_note':'Bakers TL quarter full including pending Cafe. Additional modern storage reuse block in TR is candidate-only; no overwrite of reserved future quarters in Current. Needs committed library allocation when installed.'}
(O/'atlas-plan.json').write_text(json.dumps(plan,indent=2));print('PREPARED')
