"""Stage a first Bakery proposal without publishing the shared atlas or AE assembly."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, shutil, hashlib
ROOT=Path(__file__).resolve().parents[4]
ART=Path.home()/'Desktop/Working Files/3D Art'
O=Path.home()/'Desktop/Codex/modern-bakery-v1-20261028'
D=ART/'BAKERS/Bakery/modern/revision-01-sheltered-bakery'
L2=ART/'Level 2/modern/revision-03-window-boxes-sign'
P=ART/'Props/Modern/revision-01-architectural-details'
for p in (O,D,O/'textures',O/'sources',O/'bakes',O/'review',O/'models'):p.mkdir(parents=True,exist_ok=True)
for family,prefix,candidate,rects in [('CSC_Buildings_Modern','CSC_Atlas_Modern',L2,{'AO':[(1024,0,1536,512),(1536,0,1792,256)],'default':[(512,0,1024,512)]}),('CSC_Props_Modern','CSC_Props_Modern_01',P,{'AO':[(512,0,768,256),(768,0,1024,256)],'default':[(0,384,256,512)]})]:
 current=ART/'Textures'/family/'Current'
 for ch in ('B','N','G','M','AO','E'):
  name=prefix+('_B_BAKERS' if prefix=='CSC_Atlas_Modern' and ch=='B' else '_'+ch)+'.png'
  paths=list(current.rglob(name));assert paths,(current,name)
  base=Image.open(paths[0]).convert('RGB');src=Image.open(candidate/'textures'/name).convert('RGB')
  for rect in rects.get(ch,rects['default']):
   if ch=='E':
    if family=='CSC_Props_Modern':continue
    rect=tuple(int(x*base.width/1024) for x in rect)
   base.paste(src.crop(rect),rect)
  base.save(O/'textures'/name)
guide=Image.new('RGB',(1536,1024));g=ImageDraw.Draw(guide)
colors=['#444c49','#735235','#7d9965','#e8d4a0','#737d80','#c89348']
for i,c in enumerate(colors):
 x=i%3*512;y=i//3*512;g.rectangle((x,y,x+511,y+511),fill=c)
# Explicit front-facing projected cells: no perspective baked into surfaces.
for yy in (62,259):
 g.rounded_rectangle((45,yy,433,yy+157),radius=7,fill='#282e2d',outline='#acb1a5',width=9)
 g.rectangle((76,yy+33,402,yy+111),fill='#593a1e')
 for xx in (135,239,343):g.ellipse((xx-40,yy+44,xx+40,yy+99),fill='#d6a455')
 g.rectangle((85,yy+124,363,yy+137),fill='#aeb5ae')
g.rectangle((446,70,474,415),fill='#545b54')
for y in (103,176,280,352):g.ellipse((452,y,468,y+16),fill='#c4bda2')
g.rectangle((60,446,431,470),fill='#242a28')
g.rectangle((535,23,1001,489),outline='#acb4b5',width=16)
for yy in (105,256,407):
 for xx in (635,815,945):g.ellipse((xx-47,yy-49,xx+47,yy+49),fill='#dda553')
for x in range(1024,1536,128):g.rectangle((x,0,x+63,511),fill='#e7dfbc')
g.polygon([(256,543),(454,655),(454,881),(256,993),(58,881),(58,655)],fill='#e6ce97',outline='#526b42',width=15)
g.ellipse((125,695,387,838),fill='#955c28')
for x in (182,245,308):g.line((x,727,x+28,785),fill='#e5bd76',width=18)
g.rectangle((541,541,995,995),fill='#727e80',outline='#c2c6b9',width=16)
g.rectangle((565,565,971,971),outline='#414b4c',width=14)
g.ellipse((1090,585,1470,949),fill='#c99345')
for y in (680,765,850):g.line((1160,y,1370,y-22),fill='#efd097',width=15)
guide.save(O/'sources/Projection_Guide.png')
manifest={'purpose':'First authoring proposal; no AE, ArtDefs or shared Current publication','building_source':str(L2),'surface_slots':dict(zip(range(26,32),['deck_oven_front','bread_tray_top','striped_canopy','bakery_hex_sign','empty_tray','loaf_crust'])),'AO_candidates':{'Oven':[512,256,768,512],'Display':[512,512,768,768],'Rack':[768,256,1024,512],'Trays':[768,512,896,640]},'concept':str(Path.home()/'Desktop/Codex/bakery-modern-concept-20261026/Bakery_Modern_Sheltered_Dispatch_Concept.png')}
(O/'brief.json').write_text(json.dumps(manifest,indent=2))
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [L2/'CSC_Level_2_Modern.blend',L2/'CSC_Level_2_Modern_Workshop.blend',L2/'CSC_Level_2_Modern_Review.blend']}
(O/'input-hashes.json').write_text(json.dumps(hashes,indent=2))
print(O)
