from pathlib import Path
from PIL import Image
import json
O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029'
alloc=json.loads((O/'AO_allocations.json').read_text())
for ch,groups in [('CSC_Atlas_Modern_AO',('Building',)),('CSC_Props_Modern_01_AO',('Counter','Van','Parasol','Valance'))]:
 p=O/'textures'/(ch+'.png');im=Image.open(p).convert('RGB')
 for g in groups:
  rect=alloc[g];w,h=rect[2]-rect[0],rect[3]-rect[1];src=Image.open(O/'bakes'/(g+'.png')).convert('RGB');tile=src.resize((w,h));tile.paste(src.resize((w-8,h-8)),(4,4));im.paste(tile,rect)
 im.save(p)
print('AO_PACKED')
