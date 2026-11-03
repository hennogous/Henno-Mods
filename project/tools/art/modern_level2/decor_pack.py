from pathlib import Path
from PIL import Image
O=Path.home()/'Desktop/Codex/modern-level2-v3-details-20261028'
for filename,alloc in [('CSC_Atlas_Modern_AO.png',{'Building':(1024,0,1536,512)}),('CSC_Props_Modern_01_AO.png',{'FlowerBox':(512,0,768,256),'Sign':(768,0,1024,256)})]:
 ao=Image.open(O/'textures'/filename).convert('RGB')
 for group,(x0,y0,x1,y1) in alloc.items():
  p=Image.open(O/'bakes'/(group+'.png')).convert('RGB').resize((x1-x0-8,y1-y0-8),Image.Resampling.LANCZOS);ao.paste(p,(x0+4,y0+4))
  for box,xy,size in [((0,0,1,p.height),(x0,y0+4),(4,p.height)),((p.width-1,0,p.width,p.height),(x1-4,y0+4),(4,p.height)),((0,0,p.width,1),(x0+4,y0),(p.width,4)),((0,p.height-1,p.width,p.height),(x0+4,y1-4),(p.width,4))]:ao.paste(p.crop(box).resize(size),xy)
 ao.save(O/'textures'/filename)
print('DECOR_AO_PACKED')
