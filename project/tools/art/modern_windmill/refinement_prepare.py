import sys,json,shutil
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from modular_v9 import ART,sha,dump
O=Path.home()/'Desktop/Codex/modern-kit-refinement-20261027';O.mkdir(exist_ok=True)
SLOTS=[51,53,54,55,52,7,48,35,19,27,2,32]
remap={old:(i//4)*8+i%4 for i,old in enumerate(SLOTS)}
dump(O/'props-remap.json',remap)
for kind,lib in [('building','CSC_Buildings_Modern'),('props','CSC_Props_Modern')]:
 src=ART/'Textures'/lib/'Current';dst=O/'libraries'/kind
 if not dst.exists():shutil.copytree(src,dst)
 stem='CSC_Atlas_Modern_B_BAKERS' if kind=='building' else 'CSC_Props_Modern_01_B'
 im=Image.open(src/'textures'/(stem+'.png')).convert('RGB')
 if kind=='building':guide=im.crop((0,0,512,512)).resize((1024,1024))
 else:
  guide=Image.new('RGB',(512,384))
  for i,s in enumerate(SLOTS):guide.paste(im.crop((s%8*128,s//8*128,s%8*128+128,s//8*128+128)),(i%4*128,i//4*128))
  guide=guide.resize((1024,768))
 guide.save(O/(kind+'-paint-target.png'))
Image.open(Path.home()/'Desktop/Working Files/Pantry Exports/DIS_COM_Base_B.dds').convert('RGB').save(O/'Firaxis-style-reference.png')
for tag in ('base','historical','water'):
 rows=json.loads((O/'inspection'/(tag+'.json')).read_text())
 print(tag,[(r['name'],r['vertices'],r['faces'],r['local'] if tag=='base' else r['world']) for r in rows if tag!='water' or any(s in r['name'] for s in ('Floor','Foundation','Recess'))])
