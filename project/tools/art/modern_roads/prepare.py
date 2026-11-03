"""Author reusable decal masks/markings around unchanged Firaxis surface artwork.

Run in the workspace Python runtime. No runtime asset registrations are changed.
"""
from pathlib import Path
import json, hashlib, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
P=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-02-industrial/textures'
if (D/'atlas-layout.json').exists() and json.loads((D/'atlas-layout.json').read_text()).get('shoulders'):
 raise SystemExit('Painted shoulder revision exists. Edit the saved atlas; do not overwrite it with the initial atlas generator.')
for p in (O,D,D/'textures',O/'sources'):p.mkdir(parents=True,exist_ok=True)
CELLS={
 'roundabout':{'rect':[8,8,264,264],'size':[208,208]},
 'straight':{'rect':[280,8,504,56],'size':[168,36]},
 'connector':{'rect':[280,72,504,112],'size':[168,30]},
 'transition':{'rect':[280,128,392,176],'size':[84,36]},
 'plain':{'rect':[400,128,504,176],'size':[78,36]},
 'end':{'rect':[280,184,392,232],'size':[84,36]},
 'junction':{'rect':[280,256,504,424],'size':[168,126]},
 'bend':{'rect':[8,280,232,504],'size':[168,168]},
 'patch':{'rect':[248,448,504,504],'size':[192,42]},
}
ANGLES=[145,55,-8,-75,-140]
def sample(a,x,y):
 # Mirrored sampling avoids jumps at repeated patch borders; same operation on B/H.
 def wrap(v,n):
  z=np.mod(v,2*n);return np.clip(np.where(z<n,z,2*n-1-z).astype(int),0,n-1)
 return a[wrap(y,a.shape[0]),wrap(x,a.shape[1])]
def shade_cell(era,key,cell,rgb,h):
 x0,y0,x1,y1=cell['rect'];w=x1-x0;hh=y1-y0;sx,sy=cell['size']
 x,y=np.meshgrid((np.arange(w)+.5)/w*sx-sx/2,sy/2-(np.arange(hh)+.5)/hh*sy)
 radius=np.hypot(x,y)
 if key=='roundabout':
  signed=np.minimum(radius-55,81-radius)
  for angle in ANGLES:
   t=math.radians(angle);u=x*math.cos(t)+y*math.sin(t);v=-x*math.sin(t)+y*math.cos(t)
   # Widen each mouth as it meets the circulating lane.
   half=13+np.maximum(0,91-u)*.32
   stub=np.minimum.reduce([u-65,103-u,half-np.abs(v)])
   signed=np.maximum(signed,stub)
 elif key=='bend':signed=13-np.abs(np.hypot(x+63,y+63)-105);signed=np.minimum(signed,np.minimum(x+63,y+63))
 elif key=='junction':signed=np.maximum(13-np.abs(y+25),np.minimum.reduce([13+np.maximum(0,10-y)*.35-np.abs(x),y+25,60-y]))
 else:signed=(9 if key=='connector' else 13)-np.abs(y)
 alpha=np.clip((signed+.4)/1.5,0,1)
 if key=='transition':alpha*=np.clip((x+sx/2)/23,0,1)
 if key=='end':alpha*=np.clip((sx/2-x)/22,0,1)
 if key=='patch':alpha*=np.clip((sx/2-np.abs(x))/8,0,1)
 base=sample(rgb,x+97,y+113).astype(float);height=sample(h,x+97,y+113)
 # Original paint is preserved; only new technical road markings are drawn here.
 paint=Image.new('L',(w*4,hh*4));draw=ImageDraw.Draw(paint)
 def pt(a,b):return ((a/sx+.5)*w*4,(.5-b/sy)*hh*4)
 def line(points,width=1):draw.line([pt(a,b) for a,b in points],fill=255,width=max(1,round(width*w/sx*4)),joint='curve')
 if era=='Modern':
  if key=='roundabout':
   for angle in ANGLES:
    t=math.radians(angle)
    def q(u,v):return (u*math.cos(t)-v*math.sin(t),u*math.sin(t)+v*math.cos(t))
    for v in [-9,-4.5,0,4.5,9]:
     draw.polygon([pt(*q(u,z)) for u,z in [(87,v-1.25),(96,v-1.25),(96,v+1.25),(87,v+1.25)]],fill=255)
 marks=np.asarray(paint.resize((w,hh),Image.Resampling.LANCZOS))/255
 # Paint wear follows the actual native surface values, rather than random noise.
 marks*=np.clip(.80+(height.astype(float)-128)/900,.65,.94)
 base=base*(1-marks[...,None])+np.array([221,217,196])*marks[...,None]
 return np.dstack([base.clip(0,255).astype('uint8'),(alpha*255).astype('uint8')]),height

sources=[]
for era in ['Industrial','Modern']:
 src={k:Image.open(P/f'Decals_Parts_{era}_01_{k}.dds').convert('RGBA') for k in ['B','H']}
 for k in src:
  path=P/f'Decals_Parts_{era}_01_{k}.dds';sources.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'crop':[310,268,498,452]})
 rgb=np.asarray(src['B'].crop((310,268,498,452)))[:,:,:3];height=np.asarray(src['H'].crop((310,268,498,452)))[:,:,0]
 neutral=int(np.median(height));atlas=Image.new('RGBA',(512,512));hm=Image.new('RGBA',(512,512),(neutral,neutral,neutral,0))
 for key,cell in CELLS.items():
  b,h=shade_cell(era,key,cell,rgb,height);pos=cell['rect'][:2];atlas.paste(Image.fromarray(b),pos)
  pad=np.pad(h,((4,4),(4,4)),mode='edge');v=np.dstack([pad,pad,pad,np.zeros_like(pad)]);hm.paste(Image.fromarray(v),(pos[0]-4,pos[1]-4))
 # Decal H is grayscale RGB relief plus coverage alpha, not height in alpha.
 hm.putalpha(atlas.getchannel('A'))
 for suffix,img in [('B',atlas),('H',hm),('FOW',atlas),('S',Image.new('L',(512,512),18 if era=='Industrial' else 30))]:img.save(D/'textures'/f'CSC_Roads_{era}_01_{suffix}.png')
 # Technical atlas sheet on a neutral ground, annotated outside allocated cells.
 board=Image.new('RGB',(1024,1090),(31,35,39));board.paste(atlas.resize((1024,1024)),(0,48),atlas.resize((1024,1024)))
 dr=ImageDraw.Draw(board);dr.text((16,12),f'{era.upper()} | 512 px | identical UV layout',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23),fill='white')
 for name,c in CELLS.items():
  a,b,cc,dd=c['rect'];dr.rectangle((a*2,b*2+48,cc*2,dd*2+48),outline=(90,105,116));dr.text((a*2+4,b*2+49),name,fill=(247,194,93))
 board.save(O/f'Atlas_{era}.png')
manifest={'version':1,'atlas_size':512,'cells':CELLS,'roundabout':{'center':[-35,30],'inner_radius':55,'outer_radius':81,'angles_degrees':ANGLES},'sources':sources,'sampling':'One native texel per world unit; mirrored crop repeated; paired B/H transforms','progression':{'initial':'Full Industrial stone network','first_building':['roundabout','NW','NE','SE'],'independent_optional':['E','SW'],'connector':'Pave when both lower exit destinations need the connector; preview uses SW+SE'},'status':'Authoring candidate, not installed; branch destination mapping beyond Stage2 SE remains a proposal'}
manifest['roundabout']['center']=json.loads((D/'atlas-layout.json').read_text())['roundabout']['center'] if (D/'atlas-layout.json').exists() else [5,10]
(D/'atlas-layout.json').write_text(json.dumps(manifest,indent=2));(O/'atlas-layout.json').write_text(json.dumps(manifest,indent=2))
print('ATLAS_READY',D)
