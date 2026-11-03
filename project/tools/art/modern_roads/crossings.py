"""Replace code-authored lane markings with five pedestrian crossings only."""
import ast,json,math,hashlib,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout';D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
manifest=json.loads((D/'atlas-layout.json').read_text());cells=manifest['cells'];angles=manifest['roundabout']['angles_degrees'];tex=D/'textures'
archive=O/'history/before-crossings';archive.mkdir(parents=True,exist_ok=False);shutil.copytree(tex,archive/'textures')
for name in ['02_First_building.png','04_All_tarmac.png','Roundabout_Progression.png','delivery-validation.json']:shutil.copy2(O/name,archive/name)
# Reconstruct the original code-owned markings to check for concurrent edits.
# Do not execute the initializer, which intentionally refuses to overwrite paint.
tree=ast.parse((Path(__file__).parent/'prepare.py').read_text());env={'np':np,'math':math,'Image':Image,'ImageDraw':ImageDraw,'ANGLES':angles}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'<road-mask-functions>','exec'),env)
native=O.parent/'draft-02-industrial/textures';rgb=np.asarray(Image.open(native/'Decals_Parts_Modern_01_B.dds').convert('RGBA').crop((310,268,498,452)))[:,:,:3];h=np.asarray(Image.open(native/'Decals_Parts_Modern_01_H.dds').convert('RGBA').crop((310,268,498,452)))[:,:,3]
current=np.asarray(Image.open(tex/'CSC_Roads_Modern_01_B.png').convert('RGBA')).copy();expected=np.zeros_like(current)
for key,cell in cells.items():
 x0,y0,x1,y1=cell['rect'];b,_=env['shade_cell']('Modern',key,cell,rgb,h);expected[y0:y1,x0:x1]=b
assert np.array_equal(current,expected),'Modern B was edited outside the initializer; preserve and inspect differences before repainting.'
result=current.copy()
for key,cell in cells.items():
 x0,y0,x1,y1=cell['rect'];w=x1-x0;hh=y1-y0;sx,sy=cell['size'];x,y=np.meshgrid((np.arange(w)+.5)/w*sx-sx/2,sy/2-(np.arange(hh)+.5)/hh*sy)
 base=env['sample'](rgb,x+97,y+113).astype(float);height=env['sample'](h,x+97,y+113)
 paint=Image.new('L',(w*4,hh*4));draw=ImageDraw.Draw(paint)
 def pt(a,b):return ((a/sx+.5)*w*4,(.5-b/sy)*hh*4)
 if key=='roundabout':
  for angle in angles:
   t=math.radians(angle)
   def q(u,v):return (u*math.cos(t)-v*math.sin(t),u*math.sin(t)+v*math.cos(t))
   for v in [-9,-4.5,0,4.5,9]:
    draw.polygon([pt(*q(u,z)) for u,z in [(87,v-1.25),(96,v-1.25),(96,v+1.25),(87,v+1.25)]],fill=255)
 marks=np.asarray(paint.resize((w,hh),Image.Resampling.LANCZOS))/255;marks*=np.clip(.80+(height.astype(float)-128)/900,.65,.94)
 base=base*(1-marks[...,None])+np.array([221,217,196])*marks[...,None];result[y0:y1,x0:x1,:3]=base.clip(0,255).astype('uint8')
 # Preserve the exact native surface everywhere outside the crossing paint.
 if key!='roundabout':assert np.array_equal(result[y0:y1,x0:x1,:3],env['sample'](rgb,x+97,y+113))
assert np.array_equal(result[:,:,3],current[:,:,3])
for suffix in ['B','FOW']:Image.fromarray(result).save(tex/f'CSC_Roads_Modern_01_{suffix}.png')
manifest['markings']={'style':'Pedestrian crossings only','crossings':5,'stripes_per_crossing':5,'crossing_length_world':9,'crossing_width_world':20.5,'center_lines':False,'give_way_symbols':False,'inner_ring_line':False,'reason':'Compact district road scale relative to the flatbed truck; avoid implying two vehicle lanes'}
for path in [D/'atlas-layout.json',O/'atlas-layout.json']:path.write_text(json.dumps(manifest,indent=2))
board=Image.new('RGB',(1024,1090),(31,35,39));a=Image.fromarray(result).resize((1024,1024));board.paste(a,(0,48),a);dr=ImageDraw.Draw(board);dr.text((16,12),'MODERN | pedestrian crossings only | 512 px',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23),fill='white')
for name,c in cells.items():
 a,b,cc,dd=c['rect'];dr.rectangle((a*2,b*2+48,cc*2,dd*2+48),outline=(90,105,116));dr.text((a*2+4,b*2+49),name,fill=(247,194,93))
board.save(O/'Atlas_Modern.png');(O/'crossing-change.json').write_text(json.dumps({'atlas_alpha_unchanged':True,'crossings':5,'all_other_markings_removed':True,'backup':str(archive),'method':'Edit existing code-authored technical atlas markings; retain native asphalt sampling and original alpha'},indent=2));print('CROSSINGS_READY')
