from pathlib import Path
from PIL import Image
import json
O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029';plan=json.loads((O/'atlas-plan.json').read_text())
for name,groups in [('CSC_Atlas_Modern',('M','L')),('CSC_Props_Modern_01',('Hoist','Truck','PalletJack','Drum'))]:
 p=O/'textures'/f'{name}_AO.png';im=Image.open(p).convert('RGB')
 for group in groups:
  rect=plan['AO'][group];w,h=rect[2]-rect[0],rect[3]-rect[1];src=Image.open(O/'bakes'/f'{group}.png').convert('RGB');tile=src.resize((w,h));tile.paste(src.resize((w-8,h-8)),(4,4));im.paste(tile,rect)
 im.save(p)
print('AO_PACKED')
