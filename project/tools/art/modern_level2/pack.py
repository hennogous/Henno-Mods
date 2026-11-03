from pathlib import Path
import json,os
from PIL import Image,ImageDraw,ImageFilter
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
O=Path(os.environ.get('CSC_LEVEL2_OUTPUT',str(O)))
ao=Image.open(O/'textures/CSC_Atlas_Modern_AO.png').convert('RGB')
alloc={'Building':(1024,0,1536,512),'Workshop':(1536,0,1792,256)}
for group,(x0,y0,x1,y1) in alloc.items():
 p=Image.open(O/'bakes'/(group+'.png')).convert('RGB').resize((x1-x0-8,y1-y0-8),Image.Resampling.LANCZOS);ao.paste(p,(x0+4,y0+4))
 for box,xy,size in [((0,0,1,p.height),(x0,y0+4),(4,p.height)),((p.width-1,0,p.width,p.height),(x1-4,y0+4),(4,p.height)),((0,0,p.width,1),(x0+4,y0),(p.width,4)),((0,p.height-1,p.width,p.height),(x0+4,y1-4),(p.width,4))]:ao.paste(p.crop(box).resize(size),xy)
ao.save(O/'textures/CSC_Atlas_Modern_AO.png')
e=Image.open(O/'textures/CSC_Atlas_Modern_E.png').convert('RGB');patch=Image.new('RGB',(128,128));d=ImageDraw.Draw(patch)
for x0,x1 in [(21,59),(69,108)]:
 for y0,y1 in [(16,53),(64,100)]:d.rectangle((x0,y0,x1,y1),fill=(205,140,60))
patch=patch.resize((32,32),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.35));e.paste(patch,(160,32));e.save(O/'textures/CSC_Atlas_Modern_E.png')
(O/'atlas-allocation.json').write_text(json.dumps({'surface_stage3':[512,0,1024,512],'AO':alloc,'emissive':'256 square; Stage3 cream windows all four panes; ground floor dark','existing_quadrants':'preserved'},indent=2))
