"""Compose road progression boards; preserve generated render pixels."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,subprocess,sys,struct
ROOT=Path(__file__).resolve().parents[4]
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
items=[('01_Stone','Before buildings','Complete industrial stone paving'),('02_First_building','First building','Circle + two upper exits + Stage 2 exit'),('04_All_tarmac','All required branches paved','Narrow connector remains unmarked')]
board=Image.new('RGB',(1800,720),(27,31,35));dr=ImageDraw.Draw(board)
for i,(name,title,sub) in enumerate(items):
 im=Image.open(O/(name+'.png')).convert('RGB').resize((600,600),Image.Resampling.LANCZOS);board.paste(im,(i*600,100));dr.text((i*600+18,18),title,font=font,fill='white');dr.text((i*600+18,57),sub,font=small,fill=(193,200,205))
board.save(O/'Roundabout_Progression.png')
board=Image.new('RGB',(1200,690),(27,31,35));dr=ImageDraw.Draw(board)
for i,(name,title) in enumerate([('03A_East','East destination added'),('03B_Southwest','Southwest destination added')]):
 board.paste(Image.open(O/(name+'.png')).convert('RGB').resize((600,600),Image.Resampling.LANCZOS),(i*600,80));dr.text((i*600+18,18),title,font=font,fill='white')
board.save(O/'Independent_Branches.png')
# Uncompressed mipmapped native candidate DDS. No runtime publication/cook.
dest=D/'textures/native';dest.mkdir(exist_ok=True);rows=[]
for path in (D/'textures').glob('*.png'):
 source=path
 if path.stem.endswith('_S'):
  source=O/'sources'/path.name;Image.open(path).convert('RGBA').save(source)
 args=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',str(dest)]
 if path.stem.endswith(('_B','_FOW')):args+=['-srgb']
 result=subprocess.run(args+[str(source)],capture_output=True,text=True);assert result.returncode==0,result.stdout+result.stderr
 dds=dest/(path.stem+'.dds');raw=dds.read_bytes();h,w=struct.unpack_from('<II',raw,12);mips=struct.unpack_from('<I',raw,28)[0];assert(w,h,mips)==(512,512,10)
 check=Image.open(dds);assert check.size==(512,512);rows.append({'file':str(dds),'size':[w,h],'mips':mips,'rgba_decode':True})
(O/'texture-validation.json').write_text(json.dumps(rows,indent=2));print('REVIEW_AND_DDS_PASS',len(rows))
