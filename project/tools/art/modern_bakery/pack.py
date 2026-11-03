from pathlib import Path
from PIL import Image
import json
O=Path.home()/'Desktop/Codex/modern-bakery-v1-20261028'
ao=Image.open(O/'textures/CSC_Props_Modern_01_AO.png').convert('RGB')
for group,(x0,y0,x1,y1) in json.loads((O/'brief.json').read_text())['AO_candidates'].items():
 p=Image.open(O/'bakes'/f'{group}.png').convert('RGB').resize((x1-x0-8,y1-y0-8),Image.Resampling.LANCZOS);ao.paste(p,(x0+4,y0+4))
 for box,xy,size in [((0,0,1,p.height),(x0,y0+4),(4,p.height)),((p.width-1,0,p.width,p.height),(x1-4,y0+4),(4,p.height)),((0,0,p.width,1),(x0+4,y0),(p.width,4)),((0,p.height-1,p.width,p.height),(x0+4,y1-4),(p.width,4))]:ao.paste(p.crop(box).resize(size),xy)
ao.save(O/'textures/CSC_Props_Modern_01_AO.png')
print('AO_PACKED')
